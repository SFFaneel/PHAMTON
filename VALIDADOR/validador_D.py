from __future__ import annotations

import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path

import chardet
import pandas as pd
import sqlite3 as sl
import streamlit as st

from .imprimir_erros_MANUAL import (
                                        grafico_resultado, 
                                        imprime
                                    )

from .validador_funcoes import (
                                ler_dados_csv, 
                                validar_tabela_em_lotes, 
                                gerar_relatorio_erros, 
                                limpar_texto_latin1,
                                validar_duplicidades_global,
                                validar_incr_bloco,
                                gravar_agregado_incr,
                                validar_vnr_voc_ipca,
                                consolidar_agregados_incr,
                                analisar_agregados_incr,
                                gerar_alertas_incr_agregados,
                                analisar_vf_agregado_incr,
                                gerar_alertas_incr_vf_agregados
                               )
from UTILS import (
                       existe_tabela,
                       bsc_cd_aneel,
                       busca_ipca,
                       bsc_dados_reg
                    )

from MANIFESTO import (
                            execucao_trilha,
                            rastrear_funcao,
                            registrar_evento,
                            registrar_metrica,
                            registrar_artefato,
                            inicializa_database,
                            inicializa_detalhes,
                            inicializar_rastreamento,
                       )

def _registrar_saida_se_existir(database: str, execucao_id: str, caminho: Path) -> None:
    if caminho.is_file():
        registrar_artefato(database, execucao_id, str(caminho), "SAIDA")

def _processar_validacao(database, execucao_id, local, empresa, ano,
                         csv_dir, sai_dir, temp, LMP_arq, lst_arq, lst_arq_opc):

    _ler_csv_rastreado = rastrear_funcao(ler_dados_csv)
    _validar_lotes_rastreado = rastrear_funcao(validar_tabela_em_lotes)
    _relatorio_erros_rastreado = rastrear_funcao(gerar_relatorio_erros)
    ipca = busca_ipca(st)[["Dt_REF", "VAR_MENSAL", "Nr_IPCA"]]
    Path("tabelas").mkdir(parents=True, exist_ok=True)
    ipca.to_csv(Path("tabelas") / "IPCA.csv", index=False, sep="|")
    registrar_metrica(database, execucao_id, "linhas_ipca", len(ipca), "linhas")
    os.makedirs(f"{csv_dir}/CHECKPOINTS", exist_ok=True)

    registrar_evento(database, execucao_id, "PREPARACAO", "Preparando checkpoints")
    if LMP_arq:
        for arquivo in os.listdir(f"{csv_dir}/CHECKPOINTS"):
            caminho_arquivo = os.path.join(f"{csv_dir}/CHECKPOINTS", arquivo)
            if os.path.isfile(caminho_arquivo):
                os.remove(caminho_arquivo)

    if os.path.isdir(csv_dir) and os.path.isdir(sai_dir):
        st.success("Validação iniciada com sucesso!")
        nm_TBL = ""
        cd_EMP = ""
        dt_DAT = ""
        tbl_avl = []
        tamanho = 0

        os.makedirs(csv_dir + "/DEMAIS", exist_ok=True) 

        list_arq = [
                        arq for arq in os.listdir(csv_dir) 
                        if os.path.isfile(os.path.join(csv_dir, arq)) 
                        and not arq.startswith('.') 
                        and not arq.startswith('IPCA')
                    ]

        registrar_metrica(database, execucao_id, "arquivos_encontrados", len(list_arq), "arquivos")
        nr_arq = len(list_arq) + 1

        if not list_arq:
            raise FileNotFoundError(f"Nenhum CSV encontrado em {csv_dir}")
        progresso = st.progress(0, text=f"Analisando arquivo {list_arq[0]}")

        Nr_LINHAS = 0
        arquivo = os.path.join(local, "BD_LOCAL", "linhas_analisadas.json")

        if os.path.exists(arquivo):
            with open(arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                Nr_LINHAS = dados.get("Nr_LINHAS", 0)

        p = f"{csv_dir}/CHECKPOINTS/dados_arq.json"

        if os.path.exists(p):
            with open(p) as f:
                dc_arq = json.load(f)
        else:
            dc_arq = {}

        dic_erros_arquivos = {}
        padrao = r"^(.+)_(\d{5})_(\d{8})\.csv$"

        for i, arq in enumerate(list_arq):
            vistos_duplicidade = {}
            registrar_evento(database, execucao_id, "INICIO_ARQUIVO", f"Arquivo: {arq}")
            registrar_artefato(database, execucao_id, str(Path(csv_dir) / arq), "ENTRADA")
            if arq[:arq.rfind("_")-6] in lst_arq:
                dc_arq[arq] = "NO"
            else:
                dc_arq[arq] = f"Arquivo inesperado, manual de dados ({arq[:arq.rfind('_')-6]})"

            match = re.fullmatch(padrao, arq, flags=re.IGNORECASE)
            if match is None:
                registrar_evento(
                                    database,
                                    execucao_id,
                                    nome_evento="ARQUIVO_NOME_INVALIDO",
                                    mensagem=f"Nome fora do padrão: {arq}",
                                    nivel="ALERTA",
                                    detalhes={
                                        "arquivo": arq,
                                        "padrao_esperado": "NOME_12345_YYYYMMDD.csv",
                                    },
                                )

                dic_erros_arquivos[arq] = {
                                        "mensagem": "ARQUIVO_NOME_INVALIDO",
                                        "detalhe": f"Nome fora do padrão: {arq}",
                                        "acao": "Ajuste nome do arquivo. Exemplo: MOP_00000_20250131."
                                    }
                continue
            nxt_ARQ = False

            if not match:
                dic_erros_arquivos['arq'] = {
                                                "mensagem": "Nome do arquivo inválido.",
                                                "detalhe": "O nome do arquivo deve seguir o padrão xxxx_yyyy_YYYYMMDD.csv.",
                                                "acao": "Renomeie o arquivo conforme o padrão esperado. Exemplo: AIS_01234_20250131.csv."
                                            }
                nxt_ARQ = True

            try:
                nome_tabela, tmp, data_arquivo = match.groups()
            except Exception as e:
                st.error(f"Problema no {arq}, verifique!")
                st.write(e)
                raise UserWarning(f"Avalie: {e}")

            if cd_EMP == "":
                cd_EMP = tmp
            else:
                if tmp != cd_EMP:
                    os.replace(os.path.join(csv_dir, arq), os.path.join(f"{csv_dir}/DEMAIS",arq))
                    dic_erros_arquivos[arq] = {
                                                'mensagem': 'Código da empresa no nome está incorreto.',
                                                'detalhe': f'Arquivo apresentou código {tmp} ao invés de {cd_EMP}.',
                                                'acao': 'Reveja o código da empresa no nome do arquivo.'
                                            }
                    nxt_ARQ = True
            
            try:
                datetime.strptime(data_arquivo, "%Y%m%d")
            except ValueError:
                dic_erros_arquivos[arq] = {
                                                "mensagem": "Data inválida no nome do arquivo.",
                                                "detalhe": f"Data encontrada: {data_arquivo}. A data deve estar no formato YYYYMMDD e ser válida.",
                                                "acao": "Ajuste a data no nome do arquivo. Exemplo: 20250131."
                                            }

            with open(os.path.join(csv_dir, arq), 'rb') as f:
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                if (result.get('encoding') or 'desconhecido').lower() not in ['latin-1', 'iso-8859-1', 'utf-8', 'ascii', 'macroman', 'windows-1252']:
                    dic_erros_arquivos[arq] = {
                                                'mensagem': 'Encoding inválido.',
                                                'detalhe': f"Encoding detectado: {result['encoding']}. O sistema aceita apenas latin1 ou UTF-8.",
                                                'acao': 'Converta o arquivo CSV para latin1 ou UTF-8.'
                                            }

                    nxt_ARQ = True

                if b'\r\n' in raw_data:
                    fim_linha = 'CRLF (Windows)'
                elif b'\n' in raw_data:
                    fim_linha = 'LF (Unix/Linux)'
                elif b'\r' in raw_data:
                    fim_linha = 'CR (Mac antigo)'

                if fim_linha != 'CRLF (Windows)':
                    dic_erros_arquivos[arq] = {
                                                'mensagem': 'Tipo de fim de linha incorreto.',
                                                'detalhe': f'Tipo de fim de linha detectado: {fim_linha}. O sistema aceita CRLF (Windows).',
                                                'acao': 'Converta o arquivo CSV para tipo de fim de linha CRLF (Windows).'
                                            }

            nm_TBL = arq[:arq.rfind("_")-6]

            if nxt_ARQ:
                st.warning(f"Pulou tabela: {nm_TBL}, encoding {(result.get('encoding') or 'desconhecido').lower()}. Verifique se é erro!")
                continue

            p = f"{csv_dir}/CHECKPOINTS/{arq}.chk"

            if os.path.exists(p):
                with open(p) as f:
                    arq_c = json.load(f)
                    etapa = arq_c["etapa"]
                    if etapa == "concluido":
                        tbl_avl.append(arq)
                        continue
                    Nr_LOTE = arq_c["fase"]
            else:
                etapa = None
                Nr_LOTE = 1

            TAM_LOTE = 50000
            TAM_ARQ = TAM_LOTE

            if etapa is None or etapa == "iniciado": 
                while (TAM_ARQ >= TAM_LOTE):
                    progresso.progress(i  * 100 // nr_arq, text= f"Analisando arquivo {arq}. Etapa: {Nr_LOTE}, analisando erros.") 
                    erros = []
                    dados, TAM_ARQ = _ler_csv_rastreado(os.path.join(csv_dir, arq), TAM_LOTE, Nr_LOTE)
                    if TAM_ARQ > 0:
                        lt_ini = 300
                        deslocamento=(Nr_LOTE - 1) * TAM_LOTE
                        erros = _validar_lotes_rastreado(dados[0], tamanho_lote_inicial=lt_ini, 
                                                         tipo=nm_TBL, deslocamento=deslocamento)
                        if nm_TBL == "INCR":
                            df_bloco = pd.DataFrame.from_records(dados[0])
                            erros1, ipca = (
                                            validar_incr_bloco(
                                                df_bloco,
                                                deslocamento=deslocamento,
                                                pasta="tabelas",
                                                dt_fim=st.session_state.dt_fim
                                            )
                                        )

                            erros.extend(erros1)
                            base_agregada = validar_vnr_voc_ipca(
                                                df_bloco,
                                                ipca,
                                                deslocamento=deslocamento,
                                                
                                            )
                            gravar_agregado_incr(
                                                    base_agregada=base_agregada,
                                                    nr_lote=Nr_LOTE,
                                                    pasta=str(
                                                                    Path(csv_dir) / "CHECKPOINTS" / "agregados_incr"
                                                                )
                                                )
                            
                        if nm_TBL in ["ROS_VAL", "ROS"]:
                            erros.extend(
                                            validar_duplicidades_global(
                                                                            dados=dados[0],
                                                                            vistos=vistos_duplicidade,
                                                                            deslocamento=deslocamento,
                                                                            campo="Cd_SubODI"
                                                                        )
                                        )
                        elif nm_TBL in ['ROServ', 'RServ']:
                            erros.extend(
                                            validar_duplicidades_global(
                                                                            dados=dados[0],
                                                                            vistos=vistos_duplicidade,
                                                                            deslocamento=deslocamento,
                                                                            campo="Cd_SubODS"
                                                                        )
                                        )
                        elif nm_TBL in ['DSC_CLS_CUSTO']:
                            erros.extend(
                                            validar_duplicidades_global(
                                                                            dados=dados[0],
                                                                            vistos=vistos_duplicidade,
                                                                            deslocamento=deslocamento,
                                                                            campo="Cd_Cls_Custo"
                                                                        )
                                        )
                        elif nm_TBL in ['LST_MAT', 'LST_SERV', 'LST_FCUM']:
                            erros.extend(
                                            validar_duplicidades_global(
                                                                            dados=dados[0],
                                                                            vistos=vistos_duplicidade,
                                                                            deslocamento=deslocamento,
                                                                            campo="COD_ITEM"
                                                                        )
                                        )
                        elif nm_TBL in ['DESC_ODI']:
                            erros.extend(
                                            validar_duplicidades_global(
                                                                            dados=dados[0],
                                                                            vistos=vistos_duplicidade,
                                                                            deslocamento=deslocamento,
                                                                            campo="Cd_ODI"
                                                                        )
                                        )
                        if erros:
                            progresso.progress(i  * 100 // nr_arq, text= f"Analisando arquivo {arq}. Etapa: {Nr_LOTE}, gerando relatório de erros.")
                            df_erro = _relatorio_erros_rastreado(erros, nm_TBL, tam_lote=lt_ini)
                            existe_temp = os.path.exists(temp)
                            df_erro.to_csv(
                                            temp,
                                            mode="a" if existe_temp else "w",
                                            header=not existe_temp,
                                            index=False
                                        )

                        Nr_LOTE += 1
                        with open(p, "w") as f:
                            json.dump({"etapa": "iniciado",
                                    "fase": Nr_LOTE}, f)

                        Nr_LINHAS += len(dados[0]) * len(dados[0][0])
                        x = {"Nr_LINHAS": Nr_LINHAS}

                        with open(str(Path(local) / "BD_LOCAL" / "linhas_analisadas.json"), "w", encoding="utf-8") as f:
                            json.dump(x, f, ensure_ascii=False, indent=2)

                with open(p, "w") as f:
                    json.dump({"etapa": "concluido"}, f)

                if nm_TBL == "INCR":
                    progresso.progress(
                                            i * 100 // nr_arq,
                                            text=f"Consolidando os agregados da tabela {nm_TBL}."
                                        )
                    pasta_agregados = str(
                                                Path(csv_dir) / "CHECKPOINTS" / "agregados_incr"
                                            )
                    consolidado = consolidar_agregados_incr(pasta=pasta_agregados)
                    divergencias = analisar_agregados_incr(consolidado)
                    alertas_agregados = gerar_alertas_incr_agregados(divergencias)

                    divergencias_vf = analisar_vf_agregado_incr(consolidado)
                    alertas_vf = gerar_alertas_incr_vf_agregados(divergencias_vf)
                    alertas_agregados.extend(alertas_vf)

                    temp_alertas = str(
                                        Path(temp).with_name(
                                            Path(temp).stem + "_alertas_agregados.csv"
                                        )
                                    )
                    if alertas_agregados:
                        df_alertas = _relatorio_erros_rastreado(
                                                                    alertas_agregados,
                                                                    nm_TBL,
                                                                    tam_lote=1
                                                                )
                    else:
                        df_alertas = pd.DataFrame(
                                                    columns=[
                                                        "Campo",
                                                        "Severidade",
                                                        "Descrição do Erro",
                                                        "Qtd",
                                                        "Exemplos (Amostra, linha do arquivo)",
                                                        "Nm_TAB"
                                                    ]
                                                )
                    df_alertas.to_csv(temp_alertas, index=False)

                with open(p, "w") as f:
                    json.dump(
                                {"etapa": "concluido"},
                                f
                            )
            tbl_avl.append(arq)

        registrar_metrica(database, execucao_id, "arquivos_avaliados", len(tbl_avl), "arquivos")
        lst_arq_lidos = [arq[:arq.rfind("_")-6] for arq in dc_arq.keys() if dc_arq[arq] == 'NO']
        faltando = list(set(lst_arq) - set(lst_arq_lidos))
        for nm in faltando:
            if nm in lst_arq_opc:
                dc_arq[f'{nm}_xxxxx_YYYYMMDD.csv'] = f'Não foi entregue o arquivo ({nm}), mas é opcional.'
            else:
                dc_arq[f'{nm}_xxxxx_YYYYMMDD.csv'] = f'Não foi entregue o arquivo ({nm}).'

        if len(dc_arq) > 0:
            with open(rf"{csv_dir}/CHECKPOINTS/dados_arq.json", "w", encoding="utf-8") as f:
                json.dump(dc_arq, f, ensure_ascii=False, indent=2)

        df_formatos = pd.DataFrame.from_dict(dic_erros_arquivos, orient='index').reset_index()
        df_formatos = df_formatos.rename(columns={'index': 'arquivo'})

        df_controle = pd.DataFrame.from_dict(dc_arq, orient='index').reset_index()
        df_controle = df_controle.rename(columns={'index': 'arquivo', 0 : 'OBS_SFF'})

        temp_alertas = str(
                            Path(temp).with_name(
                                                    Path(temp).stem + "_alertas_agregados.csv"
                                                )
                        )
        colunas = [
                        "Campo",
                        "Severidade",
                        "Descrição do Erro",
                        "Qtd",
                        "Exemplos (Amostra, linha do arquivo)",
                        "Nm_TAB"
                    ]

        partes = []

        for caminho in [temp, temp_alertas]:
            if Path(caminho).is_file():
                parcial = pd.read_csv(caminho)

                if not parcial.empty:
                    partes.append(parcial)
        
        df_IMPR = (
                        pd.concat(partes, ignore_index=True)
                        if partes
                        else pd.DataFrame(columns=colunas)
                    )
        df1 = df_IMPR.groupby(by=['Campo',"Severidade",'Descrição do Erro','Nm_TAB'], dropna=False)['Qtd'].sum().reset_index()

        if 'Exemplos (Amostra, linha do arquivo)' in df_IMPR.columns:
            df2 = df_IMPR.groupby(by=['Campo',"Severidade",'Descrição do Erro','Nm_TAB'], dropna=False)['Exemplos (Amostra, linha do arquivo)'].first().reset_index()
            df_IMPR = df1.merge(df2, how = 'left', on = ['Campo',"Severidade",'Descrição do Erro','Nm_TAB'])

        local = st.session_state.tra_dir
        empresa = st.session_state.nm_empr
        ano = st.session_state.dt_fim.year

        bd = sl.connect(str(Path(local) / "BD_LOCAL" / f"{empresa}_{ano}.db"))

        if len(df_IMPR)>0:
            df_IMPR.to_sql('ERROS_SDI', bd, if_exists='replace', index=False)
            df_formatos.to_sql('ERROS_FORMATOS_SDI', bd, if_exists='replace', index=False)
            df = pd.DataFrame(tbl_avl, columns=["valor"])
            df.to_sql('ERROS_tbl_avl', bd, if_exists='replace', index=False)
            df_IMPR = df_IMPR.map(limpar_texto_latin1)
            df_IMPR.to_csv(str(Path(local) / "RELATORIOS" / f"{empresa}_{ano}.csv"), 
                        index=False, 
                        sep="|", 
                        decimal=",", 
                        encoding="Latin-1",
                        quoting=csv.QUOTE_MINIMAL,
                        doublequote=True)

            df_formatos.to_csv(str(Path(local) / "RELATORIOS" / f"{empresa}_formatos_{ano}.csv"), 
                        index=False, 
                        sep="|", 
                        decimal=",", 
                        encoding="Latin-1",
                        quoting=csv.QUOTE_MINIMAL,
                        doublequote=True)

            df_controle.to_csv(str(Path(local) / "RELATORIOS" / f"{empresa}_controle_arquivos_{ano}.csv"), 
                        index=False, 
                        sep="|", 
                        decimal=",", 
                        encoding="Latin-1",
                        quoting=csv.QUOTE_MINIMAL,
                        doublequote=True)
        else:
            st.info(f"Finalizado, sem erros!")

        progresso.empty()
        st.success("Finalizado a validação!") 

        if 'df_IMPR' in locals():
            del df_IMPR

        if 'df_erro' in locals():
            del df_erro    

        df_IMPR = ""
        if bd:
            bd.close()
    else:
        raise FileNotFoundError("Certifique-se de que ambos os diretórios estão corretos.")
    for saida in (
                        Path(local) / "RELATORIOS" / f"{empresa}_{ano}.csv",
                        Path(local) / "RELATORIOS" / f"{empresa}_formatos_{ano}.csv",
                        Path(local) / "RELATORIOS" / f"{empresa}_controle_arquivos_{ano}.csv",
                    ):
        _registrar_saida_se_existir(database, execucao_id, saida)

def executar_validacao(
                            database: str, local: str, empresa: str, ano: int,
                            csv_dir: str, sai_dir: str, temp: str,
                            LMP_arq: bool, lst_arq: list[str], lst_arq_opc: list[str],
                        ) -> str:
    with execucao_trilha(
                            db_path=database,
                            script_nome="Validacao Distribuidora",
                            script_versao="1.0.0",
                            parametros={"empresa": str(empresa), "ano": ano, "refazer_todos": LMP_arq},
                        ) as execucao_id:
        registrar_evento(database, execucao_id, "INICIO_VALIDACAO", "Validação iniciada")
        _processar_validacao(database, execucao_id, local, empresa, ano,
                            csv_dir, sai_dir, temp, LMP_arq, lst_arq, lst_arq_opc)
        registrar_evento(database, execucao_id, "FIM_VALIDACAO", "Validação finalizada")
        return execucao_id

def _processar_pdf(database, execucao_id, local, empresa, ano, IA_anl):
    _grafico_rastreado = rastrear_funcao(grafico_resultado)
    _imprime_rastreado = rastrear_funcao(imprime)
    bd = sl.connect(str(Path(local) / "BD_LOCAL" / f"{empresa}_{ano}.db"))

    with st.spinner("Fazendo o relatório de erros em pdf..."):
        if existe_tabela("ERROS_SDI", bd):
            df_IMPR = pd.read_sql("SELECT * FROM ERROS_SDI", bd)

            if existe_tabela("ERROS_tbl_avl", bd):
                df = pd.read_sql("SELECT * FROM ERROS_tbl_avl", bd)
                tbl_avl = df['valor'].drop_duplicates().to_list()
            else:
                tbl_avl = []
            tipo_erro = []

            with open(str(Path(local) / "BD_LOCAL" / "linhas_analisadas.json"), "r", encoding="utf-8") as f:
                Nr_LINHAS = json.load(f) 
            FATOR = _grafico_rastreado(df_IMPR, Nr_LINHAS['Nr_LINHAS'], str(Path(local) / "IMAGENS")) 
            empresa = st.session_state.nm_empr
            cd_EMP = bsc_cd_aneel(empresa)
            x = _imprime_rastreado(FATOR, df_IMPR, cd_EMP, tbl_avl, f'{local}', tipo_erro, st, IA=IA_anl)
            if 'df_IMPR' in locals():
                del df_IMPR

def executar_geracao_pdf(database: str, local: str, empresa: str, ano: int, IA_anl: bool) -> str:
    with execucao_trilha(
                            db_path=database,
                            script_nome="Gerar PDF validação de Distribuidoras",
                            script_versao="1.0.0",
                            parametros={"empresa": str(empresa), "ano": ano, "analise_ia": IA_anl},
                        ) as execucao_id:
        registrar_evento(database, execucao_id, "INICIO_PDF", "Geração de PDF iniciada")
        _processar_pdf(database, execucao_id, local, empresa, ano, IA_anl)
        registrar_evento(database, execucao_id, "FIM_PDF", "Processamento do PDF concluído")
        return execucao_id

def VALIDADOR_D():

    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
    st.html(f"<style>{css}</style>")

    if "tra_dir" not in st.session_state:
        st.html('''<div class="fade-message pulse">Você deve configurar o diretório de trabalho na aba <i>Criar Pasta de Trabalho</i>, barra lateral.</div>''')
        return
    
    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    pasta_manifesto = Path(local) / "MANIFESTO" / "TRILHA_EXEC"
    pasta_manifesto.mkdir(parents=True, exist_ok=True)
    database = str(pasta_manifesto / "execucoes.db")

    inicializa_database(database)
    inicializa_detalhes(database)
    inicializar_rastreamento(database)

    col1 = st.columns([1,5,1], gap='small')
    with col1[1]:
        st.html("""<h1 style="text-align: center;">Validação de Arquivos CSV</h1><br><br>
            <p style="text-align: justify;text-indent: 40px">
                    Faz a validação e permite criar relatório de erros de estrutura, 
                    elaborado com base em testes e esquema pré-configurados, visando garantir 
                    a integridade e a qualidade dos dados a serem processados. 
                    A validação é realizada por meio de um validador Pydantic, que
                    identifica inconsistências nos campos conforme as regras estabelecidas. O
                    resultado do processo fornece informações sobre falhas estruturais,
                    permitindo a correção antecipada de erros e a otimização da coleta de dados. 
                    Como o processo é demorado, tem-se um botão Validar que aciona o
                    processo de validação e produz um relatório no formato CSV. A opção 'Refazer análise de todos os arquivos'
                    muda o comportamento do botão "Validar". Caso esteja ativo, ele refaz todos os arquivos, caso inativo 
                    ele apenas continua do último arquivo avaliado. O botão Gerar
                    monta um relatório no formato PDF. Se a opção "Ativar análise por IA" estiver ativa, o relatório terá 
                    uma análise de cada tabela processada por de IA, caso não, será relatório estático.
                    
            </p>
            """)

        csv_dir = rf"{st.session_state.tra_dir}\DADOS_BRUTOS_MANUAL"
        sai_dir = rf"{st.session_state.tra_dir}\RELATORIOS"

        st.markdown("### Ações")
        col_btn1, col_btn2 = st.columns(2, gap="medium")

        with col_btn1:
            teste = st.button("Validar", use_container_width=True)

        with col_btn2:
            gerar_pdf = st.button("Gerar PDF", use_container_width=True)

        st.markdown("### Opções")
        col_opt1, col_opt2 = st.columns(2, gap="medium")

        lst_arq = ['AIS','AISat','AISant','ROS','ROSaicANT','ROSaicAT','RServ','ROS_VAL','ROS_ABT_AJST',
                'CD_SUBODI_AIS_ROS','ROS_ABT_CP','ROA','ROAaicANT','ROAaicAT','RAserv','ROD','DSC_CLS_CUSTO',
                'LST_MAT','LST_SERV','LST_FCUM','LST_OBRAS_EMERG','LST_MAT_OBRAS_EMERG','DT_ENERG','COMERCIAL_MEDIDORES',
                'NT_COM','NT_CMU','OE_AGR','OE_AJS','BP_EC','BPFP_UAR','BP_UAR','REFORMADOS_INCREMENTAL',
                'ORIGEM_ATIVOS_INCREMENTAL','BS','BS_ABT','MOP','MOP_RUBRICAS','MOP_SERVICOS','MUDANCA_PATRIMONIO','BAIXAS',
                'DESC_ODI','PPBB','PCBB','INCR','AO','LD_SALDO','LD_LCMTO','LD_PTD','ECDdepara','TDOMUC']
        lst_arq_opc = ['CD_SUBODI_AIS_ROS','DSC_CLS_CUSTO','LST_FCUM','DT_ENERG','TDOMUC']
        
        with col_opt1:
            IA_anl = st.checkbox(
                                    "Ativar análise por IA",
                                    value=False,
                                    disabled=True
                                )

        with col_opt2:
            LMP_arq = st.checkbox(
                                    "Refazer análise de todos os arquivos",
                                    value=False
                                )

        temp = str(Path(csv_dir) / "CHECKPOINTS" / "erros_parciais.csv")
        if teste:
            #try:
            with st.spinner("Validando arquivos..."):
                execucao_id = executar_validacao(
                                                    database, local, empresa, ano, csv_dir, sai_dir, temp,
                                                    LMP_arq, lst_arq, lst_arq_opc,
                                                )
            st.success(f"Execução registrada: {execucao_id}")
            #except Exception as exc:
            #    raise UserWarning(f"Falha na validação: {exc}")

        if gerar_pdf:
            try:
                execucao_id = executar_geracao_pdf(database, local, empresa, ano, IA_anl)
                st.success(f"Execução registrada: {execucao_id}")
            except Exception as exc:
                raise UserWarning(f"Falha na geração do PDF: {exc}")
