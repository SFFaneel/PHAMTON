import streamlit as st
import sqlite3 as sl
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import date

from SRC.ais_funcoes import (ROS_VAL, anl_LADO_A_vs_B, anl_OBRAS_EMERG, ANL_ODD, anl_AIS_BAIXAS, anl_AIS_COM_MED,
anl_AIS_ROA, anl_LST_TUC, ger_LSTS, anl_FLXTMP, anl_RACcom, estornos, bsc_proj, bsc_proj_dd, calcular_kpis, bsc_ddsTI,
ais_roa_conc_cmp, ros_rod_baixas_cmp, analise_mop, rac_st, abertura_voc)
from UTILS import (TCCU, TCKdE, TCKdEa1a6, TCKdeIndicadores, resumo_por_projeto, sel_projetos, resumo_roa, resumo_st,
                   resumo_por_tipo_mao_de_obra, resumo_consolidado, resumo_por_fase, ajs_txt, exportar_texto,
                   monitor_completo, existe_tabela, bsc_dados_reg)
from BDGD import (RCP_base_V11 as RCPat,  RCP_base_M10 as RCPant, RCP_TOT,
                         anl_incr_rcp, eqp_rsv)
from SRC.calculos import (pre_dados, conv_num, calc_fin_icms, calc_incr, calc_oe_nv, calc_bb)
from MANIFESTO import (
                        visual_manifesto, 
                        criar_manifesto,
                        execucao_trilha,
                        rastrear_funcao,
                        registrar_evento,
                        registrar_metrica,
                        registrar_artefato,
                        inicializa_database,
                        inicializa_detalhes,
                        inicializar_rastreamento,
                      )
import os, duckdb, math, time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib import gridspec
from scipy.signal import find_peaks
from scipy.stats import chisquare, entropy
import plotly.express as px      
import ast
import inspect
import linecache
import types


def abt_VOC(st=None):
    if st.session_state.dt_fim > date.today():
        abertura_voc(st, True, html_config = False)
    else:
        abertura_voc(st, html_config = False)

def banco_compras(local, bd, bd_EFD, empresa, ano, st):
    if not isinstance(bd, str):
        return None

    caminho = str(Path(local))
    progresso = st.progress(0, text="Avaliando ICMS globalmente")

    try:
        with sl.connect(bd) as conn:

            if not existe_tabela("BL_C", bd_EFD):
                (
                    df,
                    BL_G110,
                    BL_G125,
                    BL_G126,
                    BL_G125cmp1,
                    BL_UN
                ) = calc_fin_icms(
                    bd_EFD,
                    st.session_state.dt_ini,
                    st.session_state.dt_fim,
                    progresso,
                    st
                )

            x1 = pre_dados(
                caminho,
                st.session_state.dt_ini,
                st.session_state.dt_fim,
                st.session_state.FLG_ARQ,
                st.session_state.credito_icms,
                st.session_state.val_odc,
                bd,
                bd_EFD,
                empresa,
                ano,
                st,
                st.session_state.conc_SPED_ERP,
                st.session_state.FLG_DIFAL
            )

        return x1

    except Exception as e:
        st.error(f"Erro ao processar banco de compras: {e}")
        raise

    finally:
        progresso.empty()

def ler_rcp_ant(local, bd_ANT, empresa, ano, st):
    try:
        return RCPant(f"{local}", bd_ANT, empresa, ano, st)
    except Exception:
        st.warning(
                        "Falhou leitura pela estrutura antiga, "
                        "tentando nova estrutura da BDGD."
                    )
        return RCPat(bd_ANT, f"{local}",empresa, ano, st, "ANT")

def descrever_lambda(acao):
    texto = str(inspect.getsource(acao))
    if not 'lambda' in texto:
        raise TypeError("Ação deve ser uma função lambda")
    nm_funcao = texto[texto.find(":")+2:texto.find("(")]
    arg_funcao = texto[texto.find("(")+1:texto.find(")")].split(",")

    return {
                "funcao": nm_funcao,
                "parametros": arg_funcao
            }

@st.fragment()
def coluna_01(st=None, opcoes = None, tbl_codigos = None, trilha = None):
    escolhas = []
    for opcao in opcoes:
        df_HELP = tbl_codigos[tbl_codigos['Nm_MENU']==opcao].copy()
        if df_HELP.empty:
            txt_HELP = ""
        else:
            txt_HELP = df_HELP['Cd_TESTE'].iloc[0].replace("'","")
        if opcao in ['RAC ST', 'ROS VAL']:
            continue
        if st.checkbox(opcao, value=False, help=txt_HELP, key=opcao, disabled = trilha[opcao][1]):
            escolhas.append(opcao)

    if st.checkbox("RAC ST", value=False, help="['VAL-010']", key="RAC_ST", disabled = not st.session_state.calc_rac_st):
        escolhas.append("RAC ST")
    if st.checkbox("ROS VAL", value=False, key="ROS_VAL", disabled = not st.session_state.calc_ros_val):
        escolhas.append("ROS VAL")

    return escolhas

def trilha_fisc():
    if not 'tra_dir' in st.session_state:
        st.html("""
                <p style="text-align: justify;text-indent: 40px">
                Você deve configurar o diretório de trabalho, empresa e período
                 na aba <i>Criar Pasta de Trabalho</i>, barra lateral.</p>
            """)
        return

    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
    dds = bsc_dados_reg('TBL_EMPRESAS')
    lst_emp = dds['Nm_EMPRESA'].drop_duplicates().to_list()
    st.html(f"<style>{css}</style>")
    raiz = Path(local)
    caminho_manifesto = raiz / "MANIFESTO" / "TRILHA_EXEC" / "execucoes.db"
    caminho_manifesto.parent.mkdir(parents=True, exist_ok=True)
    inicializa_database(str(caminho_manifesto))
    inicializa_detalhes(str(caminho_manifesto))
    inicializar_rastreamento(str(caminho_manifesto))
    database = str(caminho_manifesto)
    bd_path = f'{local}/BD_LOCAL/{empresa}_{ano}.db'
    bd_BDGDAT_path = f'{local}/BD_LOCAL/BDGD_AT_{empresa}_{ano}.db'
    bd_BDGDANT_path = f'{local}/BD_LOCAL/BDGD_ANT_{empresa}_{ano}.db'
    bd_EFD_path = f'{local}\BD_LOCAL\EFD_ICMS_{empresa}_{ano}.db'
    if 'calc_rac_st' not in st.session_state:
        st.session_state.calc_rac_st = False
    if 'calc_ros_val' not in st.session_state:
        st.session_state.calc_ros_val = False

    st.html(f"""
                <h1>Execução do planejamento, testes automatizados</h1>
                <br></br>            
                <h2>Observações iniciais</h2>
                <div style="text-align: justify;text-indent: 40px; padding-top: 10px">Base para se executar análises do 
                do trabalho de fiscalização. Pode-se alterar, porém somente será aplicado a versão original 
                para análise na fiscalização. Sugere-se usar este como base para modificações e 
                inclusões de análises, para discussões com a fiscalização.<p></p></div>
                <h3> Licença Pública Geral GNU (GPL)</h3>
                <div style="text-align: justify; padding-top: 10px">Versão 3, 29 de junho de 2007<p></p></div>
                <div style="text-align: justify">Copyright (C) 2025, SFF/ANEEL.<p></p></div>
                <div style="text-align: justify;text-indent: 40px; padding-top: 10px">Este é um documento de uso livre: você pode redistribuí-lo ou modificá-lo sob os termos da Licença Pública Geral GNU, conforme publicada pela Free Software Foundation, tanto na versão 3 da Licença, ou qualquer versão posterior. Ele é distribuído na expectativa de que seja útil, mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM PROPÓSITO ESPECÍFICO. Consulte a Licença Pública Geral GNU para obter mais detalhes, no sitio <a>http://www.gnu.org/licenses/</a>.<p></p></div>
                <hr></hr>              
                <h2> Normas</h2>
                <a href="https://www.gov.br/aneel/pt-br/centrais-de-conteudos/procedimentos-regulatorios/proret">Visite o sitio da Aneel para mais detalhes!</a>        
                <hr></hr>              
                """)

    processo = "Não selecionado"
    with sl.connect(bd_path) as bd:
        if (existe_tabela('tbl_PLANEJAMENTO', bd)):
            tbl_PLAN = pd.read_sql('SELECT * FROM tbl_PLANEJAMENTO WHERE TP_FISC IS NOT NULL ORDER BY TP_FISC ASC', bd)
            if not tbl_PLAN.empty:
                processo = tbl_PLAN['TP_FISC'].values[0]
            else:
                st.error("Tem de ser feito o planejamento")
                return
        else:
            st.error("Tem de ser feito o planejamento")
            return

    tbl_codigos = bsc_dados_reg("tab_rel_testes_scripts")
    df_CARACT = bsc_ddsTI(f"{local}", st)    
    trilha = {
               'AIS vs ROA': [True, True, ('bd_path', "Verificando AIS ROA conciliado...", 
                lambda: ais_roa_conc_cmp(bd, f"{local}/AIS_ANLS", empresa, st))],

                'ESTORNO': [True, True, ('bd_path', "Analisando estornos do ROA...", 
                lambda: estornos(f"{local}", bd, empresa, st))],

                'BAIXAS': [True, True, ('bd_path', "Verificando UC para arquivo de baixas e de AIS...", 
                lambda: ros_rod_baixas_cmp(bd, f"{local}/AIS_ANLS", empresa, st))],

                'MOP': [True, True, ('bd_path', "Verificando Dados de MOP...", 
                lambda:  analise_mop(st, bd, empresa, f"{local}/AIS_ANLS"))],

                'MEDIDORES COMERCIAL' : [True, True, ('bd_path', "Verificando medidores...", 
                lambda: anl_AIS_COM_MED(bd, f"{local}/AIS_ANLS", empresa, st))],

                'ANÁLISES DATAS' : [False, True, ('bd_path', "Verificando datas do ROA contra ROS...", 
                lambda: anl_AIS_ROA(bd, f"{local}/AIS_ANLS", empresa, st))],

                'UC por TI' : [True, True, ('bd_path', "Verificando grupos de TUC por TI...", 
                lambda: anl_LST_TUC(bd, f"{local}/AIS_ANLS", empresa, st))],

                'LISTAS' : [True, True, ('bd_path', "Gerando listas de Materiais e Serviços...", 
                lambda: ger_LSTS(bd, f"{local}/AIS_ANLS", empresa, st),
                lambda: not (
                    os.path.exists(f"{local}/AIS_ANLS/LST_MAT_AJ_{empresa}.csv") and
                    os.path.exists(f"{local}/AIS_ANLS/LST_SER_AJ_{empresa}.csv")
                ))],

                'FLUXO TEMPORAL' : [True, True, ('bd_path', "Analisando fluxo temporal...", 
                lambda: anl_FLXTMP(bd, f"{local}/AIS_ANLS", empresa, st, df_CARACT))],

                'OUTLIERS INDICADORES' : [True, True, ('bd_path', "Avaliando outliers pelos indicadores...", 
                lambda: TCKdeIndicadores(st))],

                'RACIONALIZAÇÃO COM' : [True, True, ('bd_path', "Analisando racionalização de COM...", 
                lambda: anl_RACcom(bd, f"{local}/AIS_ANLS", empresa, st))],

                'ODD vs ROS' : [True, True, ('bd_path', "Analisando ODD vs ROS...", 
                lambda: ANL_ODD(bd, f"{local}/AIS_ANLS", empresa, st))],

                'OBRAS EMERGENCIAIS' : [True, True, ('bd_path', "Analisando Obras Emergenciais...", 
                                        lambda: anl_OBRAS_EMERG(bd, f"{local}/AIS_ANLS", empresa, st))],
                
                'Anomalia Tucagem' : [True, True, ('bd_path', "Analisando anomalias considerando Tucagem...", 
                                        lambda: TCKdE(st))],

                'Anomalia Atributos' : [True, True, ('bd_path', "Analisando anomalias considerando atributos...", 
                                        lambda: TCKdEa1a6(st))],

                'RAC ST' : [True, True, ('bd_path', "Analisando racionalização de Serviços...",
                                         lambda: rac_st(st.session_state.get("calc_rac_st", False), "CRIAR", st, bd))],

                'ROS VAL' : [True, True, ('bd_path', "Criando ROS Validado...",
                                          lambda: ROS_VAL(bd, f"{local}/AIS_ANLS", f"{local}/AIS_ANLS", empresa, st))],

                'ABERTURA VOC' : [True, True, ('bd_path', "Analisando Abertura do VOC...", 
                                        lambda: abt_VOC(st))],

                'RCP BDGD AT' : [True, True, ('bd_BDGDAT_path', "Criando RCP BDGD AT...",
                                          lambda: RCPat(bd, f'{local}/BDGD_ANLS', empresa, ano, st))],

                'RCP BDGD ANT' : [True, True, ('bd_BDGDANT_path', "Criando RCP BDGD ANT...",
                                            lambda: ler_rcp_ant(f'{local}/BDGD_ANLS', bd, empresa, ano, st))],

                'RCP TOT' : [True, True, ('bd_path', "Criando RCP Total...",
                                            lambda: RCP_TOT(f'{local}', bd, empresa, st))],

                'CONCILIAÇÃO INCREMENTAL BDGD' : [True, True, ('bd_path', "Conciliando base incremental com BDGD...",
                                            lambda: anl_incr_rcp(f'{local}', bd, empresa, 
                                           st.session_state.dt_ini, st.session_state.dt_fim, st))],

                'CONCILIAÇÃO TOTAL BDGD' : [True, True, ('bd_path', "Conciliando base completa com BDGD...",
                                                            lambda: anl_incr_rcp(f'{local}', bd, empresa, 
                                                           st.session_state.dt_ini, st.session_state.dt_fim, st, False))],

                'EQUIPAMENTO RESERVA BDGD' : [True, True, ('bd_path', "Conciliando equipamento de reservas com BDGD...",
                                            lambda: eqp_rsv(f'{local}\BDGD_ANLS', 'AT', bd, bd_path, st))],

                'BANCO DE COMPRAS' : [True, True, ('bd_EFD_path', "Emulando banco de compras...",
                                        lambda: banco_compras(f'{local}\BP_ANLS', bd_path, bd, empresa, ano, st))],

                'INCREMENTAL' : [True, True, ('bd_path', "Emulando base incremental...",
                                        lambda: calc_incr(f'{local}\INC_ANLS', st.session_state.dt_ini, 
                                            st.session_state.dt_fim, st.session_state.ROA_RD, st.session_state.genre, 
                                            bd, empresa, ano, st))],

                'LADO A vs B' : [True, True, ('bd_path', "Analisando LADO A vs B...", 
                                lambda: anl_LADO_A_vs_B(
                                bd, f"{local}/AIS_ANLS", empresa, 
                                st.session_state.dt_ini, st.session_state.dt_fim, st))],

                'OE' : [True, True, ('bd_path', "Emulando movimentação de OE...",
                                    lambda: calc_oe_nv(f'{local}\OE_ANLS', 
                                    st.session_state.dt_ini, 
                                    st.session_state.dt_fim, 
                                    st.session_state.TX_AMT_OE, 
                                    bd, empresa, ano, st))],

                'BB' : [True, True, ('bd_path', "Emulando movimentação de BB...",
                                    lambda: calc_bb(f'{local}\BB_ANLS', st.session_state.dt_ini, 
                                    st.session_state.dt_fim, bd, empresa, ano, st, st.session_state.opcao, 
                                    st.session_state.nm_empr_fus, st.session_state.data_ref))],
                                                }
    
    tbl_codigos["existe"] = tbl_codigos["Nm_MENU"].isin(trilha)
    lst_ATV = [nm for nm in tbl_codigos[tbl_codigos["existe"]]["Nm_MENU"].drop_duplicates().to_list()]
    for nm_menu in lst_ATV:
        resultado = tbl_codigos.loc[tbl_codigos["Nm_MENU"].isin([nm_menu]), "Cd_TESTE"]
        saida = resultado.iloc[0] if not resultado.empty else None
        lst_TSTS = [nm.replace("'","") for nm in saida[1:-2].split(",")]
        lst_PLAN = tbl_PLAN['Cd_TESTE'].drop_duplicates().to_list()
        intersecao = list(set(lst_TSTS) & set(lst_PLAN))
        if len(intersecao)>0:
            trilha[nm_menu][1] = False

    st.html(f"""<h2 style="text-align: center;">{processo}</h2>""")
    opcoes = [nm for nm in trilha.keys()]
    col1, _, col2 = st.columns([2,.1,8], gap='small')
    with col1:
        with st.container(border=True, height=1500, key='escolhas'):
            st.html(f"""<h2 style="text-align: left;">Etapas:</h2>""")
            escolhas = coluna_01(st, opcoes, tbl_codigos, trilha)
            
    with col2:
        with st.container(border=True, height=1500, key='execucoes'):
            st.html(f"""<h2 style="text-align: left;">Painel de Execução:</h2>""")
            st.html(f"""
                        <p  style="text-align: justify;text-indent: 40px">O painel de execução controla o comportamento
                        de alguns dos testes. Somente execute os testes após configurar adequadamente cada elemento a 
                        seguir. Após, inicio-os por meio de <b>Calcular</b>.</p>  
                        <hr></hr>
                                
                    """)
            with st.container(border=True):
                st.html("""<h3 style="text-align: center;">Opções de Execução:</h3>""")
                st.divider()
                colunas = st.columns([1,7,1,7,1], gap='small', vertical_alignment="center")
                with colunas[1]:
                    st.html("""<p><b>Do AIS e ROA</b></p>""")
                    est_ANT1 = st.session_state.get("calc_rac_st", False)
                    est_ANT2 = st.session_state.get("calc_ros_val", False)
                    est_ANT3 = st.session_state.get("credito_icms", True)
                    est_ANT4 = st.session_state.get("conc_SPED_ERP", False)
                    est_ANT5 = st.session_state.get("bsc_cnpj_bc", False)
                    est_ANT6 = st.session_state.get("val_odc", 0)
                    est_ANT7 = st.session_state.get("FLG_ARQ", True)
                    est_ANT8 = st.session_state.get("FLG_DIFAL", True)
                    st.session_state.calc_rac_st = st.checkbox("Criar RAC ST", value=est_ANT1, 
                                              help="Só ative após primeira rodada", 
                                              key="rac_st_check")
                    st.session_state.calc_ros_val = st.checkbox("Criar ROS_VAL", value=est_ANT2, 
                                              help="Só ative após primeira rodada", 
                                              key="ros_val_check")
                    st.divider()
                    st.html("""<p><b>Do Banco de compras</b></p>""")
                    st.session_state.credito_icms = st.checkbox("Aproveita crédito de ICMS na UF?", value=est_ANT3, 
                                                                  help="Reaproveita o crédito de ICMS do imobilizado", 
                                                                  key="credito_icms_chv")
                    st.session_state.conc_SPED_ERP = st.checkbox("(Re)Conciliar SPED e ERP?", value=est_ANT4, 
                                                help="(Re)Concilia SPED ICMS e AIS", 
                                                key="conc_SPED_ERP_chv")
                    st.session_state.bsc_cnpj_bc = st.checkbox("Buscar dados de CNPJ das empresas não conciliadas, lado EFD?", value=est_ANT5, 
                                                            help="Apenas se realmente for necessário", 
                                                            key="bsc_cnpj_bc_chv")
                    st.session_state.val_odc = st.number_input("Valor de ODC apurado, para itens do imobilizado, (R$):", 
                                                                                                   min_value=0., max_value=100e7, value=0.,width='stretch', key="vl_odc_chv")
                    st.session_state.FLG_ARQ = st.checkbox("Fluxo de pagamento: arquivo (ativo), se projeção (inativo)", value=est_ANT7, 
                                                                    help="Empregar o fluxo de pagamento informado", 
                                                                    key="FLG_ARQ_chv")
                    st.session_state.FLG_DIFAL = st.checkbox("Limitar DIFAL: sim (ativo), não (inativo)", value=est_ANT8, 
                                                help="Limita o percentual de DIFAL informado ao valor esperado", 
                                                key="FLG_DIFAL_chv")
                    st.divider()

                    if ((est_ANT1 != st.session_state.calc_rac_st) or
                       (est_ANT2 != st.session_state.calc_ros_val) or
                       (est_ANT3 != st.session_state.credito_icms) or
                       (est_ANT4 != st.session_state.conc_SPED_ERP) or
                       (est_ANT5 != st.session_state.bsc_cnpj_bc) or
                       (est_ANT6 != st.session_state.val_odc) or
                        (est_ANT7 != st.session_state.FLG_ARQ) or
                        (est_ANT8 != st.session_state.FLG_DIFAL)):
                       st.rerun()
                with colunas[3]:
                    est_ANT9 = st.session_state.get("ROA_RD", False)
                    est_ANT10 = st.session_state.get("genre", "***Mês seguinte***")
                    est_ANT11 = st.session_state.get("TX_AMT_OE", False)
                    est_ANT12 = st.session_state.get("opcao", False)
                    est_ANT13 = st.session_state.get("nm_empr_fus", "")
                    est_ANT14 = st.session_state.get("data_ref", st.session_state.dt_ini)
                    data_default = date.today()
                    dt_min=date(2019, 1, 1)

                    st.html("""<p><b>Do Incremental</b></p>""")
                    st.session_state.ROA_RD = st.checkbox("""Há necessidade de arquivo de-para para projetos 
                                                            entre ROA e AIS?""", value=est_ANT9, 
                                                            key="ROA_RD_chv")
                    st.session_state.genre = st.radio(
                                        "Sobre o método de depreciação:",
                                        ["***Mês seguinte***", "***Próprio mês***"],
                                        captions=[
                                            "Considerar o dia para depreciar (exemplo: imobilizado dia 1º toma carga no mesmo mês. Imobilizado no dia 30 toma carga somente no mês seguinte)?",
                                            "Considerar o próprio mês para depreciar?",
                                        ],
                                    )
                    st.divider()
                    st.html("""<p><b>De OE</b></p>""")
                    st.session_state.TX_AMT_OE = st.toggle("""Considerar o valor da taxa média do laudo, base blindada e base incremental, 
                                            (ativo) ou valor da contabilidade (inativo -> DEFAULT)""", 
                                            value=est_ANT11)
                    st.divider()
                    st.html("""<p><b>De base blindada</b></p>""")

                    st.session_state.opcao = st.checkbox("Resultante de fusão? Se sim, indicar qual a empresa abaixo.", 
                                                        value=est_ANT12, help="Sim, ativar a  opção!")
                    st.session_state.nm_empr_fus = st.selectbox("Empresa:", lst_emp, 
                                                            help="Selecione a empresa que foi fusionada")
                    st.session_state.data_ref = st.date_input(
                                    "Data de referência da blindada da distribuidora incorporada:",
                                    value = est_ANT14,
                                    min_value=dt_min,
                                    max_value=date(data_default.year + 5, 12, 31) 
                                    )


                    if (
                        (est_ANT9 != st.session_state.ROA_RD) or
                        (est_ANT10 != st.session_state.genre) or
                        (est_ANT11 != st.session_state.TX_AMT_OE) or
                        (est_ANT12 != st.session_state.opcao) or
                        (est_ANT13 != st.session_state.nm_empr_fus) or
                        (est_ANT14 != st.session_state.data_ref)):
                        st.rerun()
                st.divider()
                colunasB = st.columns(7, gap='small')
                with colunasB[3]:
                    recalcular = st.button("Calcular", width='stretch')

    
    if recalcular:
        with st.container(border=True):
            st.html(f"""<h2 style="text-align: left;">Resultados de Execução:</h2>""")
            st.html(f"""
                        <p  style="text-align: justify;text-indent: 40px">Para maior detalhes avaliar os relatórios 
                        de saída dos testes. Abaixo temos um resumo com informações, quando disponíveis, dos testes
                        executados.</p>  
                        <hr></hr>
                                
                    """)
            progresso = st.status(label="0. Iniciando análises...")
            etapas = [trilha[nm][2] for nm in trilha.keys() if nm in escolhas]
            with execucao_trilha(
                                db_path=database, script_nome="Execucao_Trilha_Fiscalizacao",
                                parametros={"empresa": empresa, "ano": ano, "solicitacoes" : len(etapas)},
                                ) as execucao_id:
                
                st.session_state.database_MAN = database
                st.session_state.execucao_id = execucao_id
                total = len(etapas)

                resultados = {}
                tempos = {}

                for i, etapa in enumerate(etapas, start=1):

                    dic_evento = descrever_lambda(etapa[2])
                    detalhes = {}
                    for nxx in dic_evento['parametros']:
                        if nxx.strip()=="bd":
                            detalhes['BANCO'] = bd_path
                        elif 'f"' in nxx:
                            detalhes['SAIDA'] = eval(nxx)
                        elif 'empresa' in nxx:
                            detalhes['empresa'] = eval(nxx)
                        elif 'ano' in nxx:
                            detalhes['ano'] = eval(nxx)
                        elif 'dt_ini' in nxx:
                            detalhes['Dt_INI'] = f"{st.session_state.dt_ini:%d/%m/%Y}"
                        elif 'dt_fim' in nxx:
                            detalhes['Dt_FIM'] = f"{st.session_state.dt_fim::%d/%m/%Y}"

                    registrar_evento(database, execucao_id, nome_evento = dic_evento["funcao"],
                                    mensagem = etapa[0], nivel = 'INFO',
                                    detalhes = detalhes)
                    msg = etapa[1]
                    func = etapa[2]
                    cond = etapa[3] if len(etapa) > 3 else lambda: True

                    if not cond():
                        continue

                    estado = progresso.status(f"{int(i)}. {msg}", state="running")

                    inicio = time.perf_counter()
                    bd_REF = eval(etapa[0])
                    try:
                        with sl.connect(bd_REF) as bd:
                            resultados[msg] = func()
                        estado.update(label=f"{int(i)}. {msg}", state="complete")
                        registrar_evento(database, execucao_id, nome_evento = dic_evento["funcao"],
                                        mensagem = "Finalizado", nivel = 'INFO',
                                        detalhes = detalhes)
                    except Exception as e:
                        estado.update(label=f"{int(i)}. {msg}", state = 'error')
                        progresso.update(label="Finalizado", state = 'error')
                        st.exception(e)
                        registrar_evento(database, execucao_id, nome_evento = dic_evento["funcao"],
                                        mensagem = f"Erro: {e}", nivel = 'ERRO',
                                        detalhes = detalhes)
                        raise
                    finally:
                        a_seg = time.perf_counter() - inicio
                        tempos[msg] = a_seg
                        registrar_metrica(database, execucao_id, nome = f"Tempo_{dic_evento['funcao']}",
                                            valor = a_seg, unidade = "s")


                progresso.update(label="Finalizado", state = 'complete')

                tempo_total = f"{sum(tempos.values()):,.2f}".replace(",","x").replace(".",",").replace("x",".")
                itens_html = "".join(
                                        f"""
                                        <div style="
                                            display: flex;
                                            justify-content: space-between;
                                            align-items: center;
                                            padding: 10px 0;
                                            border-bottom: 1px solid rgba(128, 128, 128, 0.20);
                                        ">
                                            <span style="
                                                font-size: 0.95rem;
                                            ">
                                                {mensagem}
                                            </span>

                                            <span style="
                                                font-size: 0.90rem;
                                                font-weight: 600;
                                                font-family: monospace;
                                                white-space: nowrap;
                                            ">
                                                {tempo:.2f} s
                                            </span>
                                        </div>
                                        """
                                        for mensagem, tempo in tempos.items()
                                    )
                cols = st.columns([1,3,1], gap='small')
                with cols[1]:
                    st.html(
                            f"""
                            <div style="
                                padding: 18px 22px;
                                border: 1px solid rgba(128, 128, 128, 0.25);
                                border-radius: 12px;
                                margin: 12px 0;
                            ">
                                <div style="
                                    font-size: 1.05rem;
                                    font-weight: 600;
                                    margin-bottom: 4px;
                                ">
                                    Tempo de execução dos processos
                                </div>

                                <div style="
                                    font-size: 0.85rem;
                                    opacity: 0.70;
                                    margin-bottom: 14px;
                                ">
                                    Detalhamento do tempo consumido em cada etapa do processamento.
                                </div>

                                {itens_html}

                                <div style="
                                    display: flex;
                                    justify-content: space-between;
                                    align-items: center;
                                    padding-top: 14px;
                                    font-weight: 700;
                                ">
                                    <span>Tempo total de processamento</span>
                                    <span style="
                                        font-family: monospace;
                                        white-space: nowrap;
                                    ">
                                        {tempo_total} s
                                    </span>
                                </div>
                            </div>
                            """
                        )
                st.session_state.database_MAN = ""
                st.session_state.execucao_id = ""
        st.divider()
    return


    