import pandas as pd
import streamlit as st
import sqlite3 as sl
from pathlib import Path
from typing import Callable
from UTILS import (
                    ler_metadados,
                    existe_tabela,
                    bsc_dados_reg
                  )
from RELATORIOS import imp_ck_list
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

dados = [
            ["Seção", "Item", "Verificado"],

            ["1. Identificação e Objetivo", "O sumário apresenta o objetivo da avaliação da BRR?", ""],
            ["1. Identificação e Objetivo", "Informa que se refere à RTP ou outro processo regulatório?", ""],
            ["1. Identificação e Objetivo", "Cita o Submódulo 2.3 – versão 2.0C da ANEEL?", ""],

            ["2. Composição da BRR", "Explicita sobre critérios empregados nas análises do AIS, Intangível, Almoxarifado de Operação e Obrigação Especiais?", ""],
            ["2. Composição da BRR", "Explica critérios de inclusão e exclusão de ativos (eligibilidade, conciliação, fatores de aproveitamento)?", ""],
            ["2. Composição da BRR", "Explica como foi feita a amostragem? Houve reprovações? Foram encontradas sobras físicas?", ""],

            ["3. Critério de Avaliação", "Indica claramente os critérios para determinação de VNR? Fez alguma ressalva?", ""],
            ["3. Critério de Avaliação", "Apresenta discussão sobre obras atípicas? Se sim, quais os motivos determinantes para aceitar?", ""],
            ["3. Critério de Avaliação", "Menciona sobras físicas? Como fez a valoração se existirem?", ""],

            ["4. Aspectos Contábeis", "Os ativos foram conciliados com os dados contábeis? Houve sobras contábeis? Está propondo ajustes de eligibilidade ou de conciliação? Explicou os motivos determinantes?", ""],
            ["4. Aspectos Contábeis", "Há análise de baixas contábeis e justificativas?", ""],
            ["4. Aspectos Contábeis", "Considera vida útil regulatória e depreciação acumulada?", ""],

            ["5. Obrigações Especiais", "Avaliadas separadamente da BRR bruta?", ""],
            ["5. Obrigações Especiais", "Metodologia de apuração descrita?", ""],

            ["6. JOA", "JOA calculado com base na metodologia do PRORET?", ""],
            ["6. JOA", "Critério de apuração temporal está descrito?", ""],

            ["7. Atualização Monetária", "Usado o IPCA como índice oficial?", ""],
            ["7. Atualização Monetária", "Correção está em conformidade com o período-base?", ""],

            ["8. Conformidade e Transparência", "Aderência à regulação da ANEEL está clara?", ""],
            ["8. Conformidade e Transparência", "Transparência nas premissas e parâmetros?", ""],
            ["8. Conformidade e Transparência", "Responsável técnico identificado?", ""],

            ["9. Destaques e Mudanças", "Mudanças em relação ao ciclo anterior estão descritas?", ""],
            ["9. Destaques e Mudanças", "Adaptações exigidas pela versão 2.0C estão citadas?", ""],

            ["10. Anexos e Referências", "Há anexos com tabelas de ativos, VNR, etc.?", ""],
            ["10. Anexos e Referências", "Fontes como laudos e inventário são citadas?", ""],
        ]


@rastrear_funcao
def rastrear_metados(
                    arquivo: Path,
                    bd: sl.Connection,
                    st = None,
                    *,
                    ler_metadados: Callable,
                    database,
                    execucao_id,
                ) -> tuple[int, int]:
    y_meta, y_ind = ler_metadados(arquivo, bd, st)
    registrar_metrica(
                            database,
                            execucao_id,
                            "arquivos_encontrados",
                            y_meta,
                        )
    registrar_metrica(
                                database,
                                execucao_id,
                                "arquivos_encontrados_com_indícios",
                                y_ind,
                            )
    return y_meta, y_ind

def dados_fotos_inv():
    if not 'tra_dir' in st.session_state:
        st.html("""
                    <p>Você deve configurar o diretório de trabalho na aba 
                    <i>Criar Pasta de Trabalho</i>, barra lateral.</p>
                """)
        return
    
    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
    st.html(f"<style>{css}</style>")

    caminho_manifesto = Path(local) / "MANIFESTO" / "TRILHA_EXEC" / "execucoes.db"
    caminho_manifesto.parent.mkdir(parents=True, exist_ok=True)
    inicializa_database(str(caminho_manifesto))
    inicializa_detalhes(str(caminho_manifesto))
    inicializar_rastreamento(str(caminho_manifesto))
    database = str(caminho_manifesto)
    pasta_fotos = Path(local) / "IMAGENS_SUMARIO"

    bd = sl.connect(f'{local}\BD_LOCAL\{empresa}_{ano}.db')

    col1a = st.columns([1,5,1], gap='small')
    with col1a[1]:
        st.html(f"""<h1>Painel para Análises de Metadados das Fotos de Inventário</h1><br><br>
                    <p  style="text-align: justify;text-indent: 40px">Desenvolvido para 
                    apoiar a análise de laudos técnicos por meio da leitura automatizada de metadados de 
                    imagens, especialmente data, hora e coordenadas de geolocalização. A partir das 
                    informações EXIF incorporadas nos arquivos fotográficos, é possível verificar se as 
                    fotos foram capturadas no local e período compatíveis com o objeto analisado, garantindo 
                    maior confiabilidade, rastreabilidade e adequação das evidências visuais utilizadas. 
                    Ao identificar automaticamente possíveis inconsistências temporais ou espaciais, o 
                    sistema contribui para a validação e integridade dos registros apresentados no laudo.
                    Para reprocessar use o botão a seguir.""")
        st.divider()
        cols = st.columns([1,2,1,2,1], gap='small')
        with cols[1]:
            x = st.button("(Re)Fazer", key="ANL_FOTOS_INV")
        with cols[3]:
            x1 = st.button("Check List", key="CHECKLIST_LAUDO")
        st.divider()
        if x1:
            with execucao_trilha(
                                    db_path=database, script_nome="APOIO_ANL_LAUDO",
                                    parametros={"empresa": empresa, "ano": ano},
                                ) as execucao_id:
        
                registrar_evento(database, execucao_id, "GERACAO_ARQ_APOIO_LAUDO_INICIADO",
                                    mensagem=f"Iniciando geração de arquivo de apoio para análise do Sumário Executivo")
                saida = imp_ck_list(f'{local}//RELATORIOS//checklist_sumario.xlsx', dados)
                registrar_artefato(database, execucao_id, f'{local}//RELATORIOS//checklist_sumario.xlsx', "SAIDA")
                registrar_evento(database, execucao_id, "GERACAO_ARQ_APOIO_LAUDO_FINALIZADO",
                                mensagem=f"Finalizado geração de arquivo de apoio para análise do Sumário Executivo")
            if saida == "Falhou":
                st.warning("Geração do checklist falhou!")

            else:
                st.info(f"Executado com sucesso, arquivo na pasta {local}/RELATORIOS/checklist_sumario.xlsx.")

        if x:
            
            if not pasta_fotos.is_dir():
                st.warning(
                    f"Diretório de imagens não encontrado: {pasta_fotos}"
                )
            with st.spinner("Lendo metadados das fotos"):
                with execucao_trilha(
                                        db_path=database, script_nome="Leitura_METADADOS_FOTOS",
                                        parametros={"empresa": empresa, "ano": ano},
                                    ) as execucao_id:
            
                    registrar_evento(database, execucao_id, "IMPORTACAO_LEITURA_METADADOS_FOTOS_INICIADO",
                                        mensagem=f"Iniciando leitura de de metadados das fotos de inventário")
                    try:
                        y1, y2 = rastrear_metados(
                                                        pasta_fotos,
                                                        bd,
                                                        st,
                                                        ler_metadados=ler_metadados,
                                                        database=database,
                                                        execucao_id=execucao_id,
                                                    )
                        registrar_evento(database, execucao_id, "IMPORTACAO_LEITURA_METADADOS_FOTOS_FINALIZADO",
                                            mensagem=f"Finalizado leitura de metadados das fotos de inventário")
                    except Exception as e:
                        registrar_evento(database, execucao_id, "ARQUIVO_REPROVADO",
                                            mensagem=f"GERACAO ARQAPOIO METDADOS FALHOU", nivel="ERRO",
                                            detalhes={"erro": f"{e}"})

        if (existe_tabela('tbl_FOTOS', bd)):
            cont1, _, cont2 = st.columns([15,1,15], gap = 'small')
            with cont1:
                with st.container(border=True):
                    st.html(f"""<h3 style="text-align: center;">Resumo Fotos Analisadas</h3><br>
                                <p  style="text-align: justify;text-indent: 40px">Resumo das fotos 
                                disponiveis na pasta {pasta_fotos} e que foram avaliadas.""")
                    sSQL = "SELECT * FROM tbl_FOTOS"
                    df = pd.read_sql(sSQL, bd)
                    config = {
                                "arquivo": st.column_config.TextColumn("Foto"),
                                "latitude": st.column_config.TextColumn("Latitude"),
                                "longitude": st.column_config.TextColumn("Longitude"),
                                "lat_dms": st.column_config.TextColumn("Latitude DMS"),
                                "lon_dms": st.column_config.TextColumn("Longitude DMS"),
                                "data_original": st.column_config.TextColumn("Data Original"),
                                "data_digitizacao": st.column_config.TextColumn("Data Digitalização"),
                                "data_modificacao": st.column_config.TextColumn("Data Modificação"),
                                "software": st.column_config.TextColumn("Software")
                            }
                    st.dataframe(df, width='stretch', hide_index=True,  column_config=config)
                    st.download_button(
                                        "Exportar em CSV",
                                        data=df.to_csv(index=False, sep="|").encode("latin-1"),
                                        file_name=f"fotos_metadados.csv",
                                        mime="text/csv",
                                        key=f"fotos_exportar_dados",
                                        disabled=df.empty,
                                      )
            
            if (existe_tabela('tbl_FOTOS_indicios', bd)):
                with cont2:
                    with st.container(border=True):
                        st.html(f"""<h3 style="text-align: center;">Resumo de Indícios</h3><br>
                                    <p  style="text-align: justify;text-indent: 40px">Resumo das fotos 
                                    disponiveis na pasta {pasta_fotos} e indícios.""")
                        sSQL = "SELECT * FROM tbl_FOTOS_indicios"
                        df1 = pd.read_sql(sSQL, bd)
                        df1 = df1.replace(r'^\s*$', "ND", regex=True).fillna("ND")
                        config = {
                                    "arquivo": st.column_config.TextColumn("Foto"),
                                    "indicio_1": st.column_config.TextColumn("Indicio de datas"),
                                    "indicio_2": st.column_config.TextColumn("Indicio de Software"),
                                    "indicio_3": st.column_config.TextColumn("Indicio de Marca/Modelo")
                                }
                        st.dataframe(df1, width='stretch', hide_index=True,  column_config=config)
                        st.download_button(
                                            "Exportar em CSV",
                                            data=df1.to_csv(index=False, sep="|").encode("latin-1"),
                                            file_name=f"fotos_metadados_indicios.csv",
                                            mime="text/csv",
                                            key=f"fotos_exportar_dados1",
                                            disabled=df.empty,
                                            )
        else:
            st.warning("Sem fotos para analisar!")
            

