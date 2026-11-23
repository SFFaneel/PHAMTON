import streamlit as st
from pathlib import Path
import sqlite3 as sl
import pandas as pd
import datetime
from datetime import date

from UTILS import (
                    desenhar_grafo_hierarquico, 
                    consultar_empresa,
                    bsc_dados_reg,
                    sorteio,
                    existe_tabela,
                    carga_sqlite_cache,
                    max_arq,
                    executar_vis
                    )
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

@st.fragment()
def _vis_001(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if existe_tabela('TST_CMP2_INCR', bd):
            st.html(f"""<h2>VOC do arquivo Incremental com os valores ajustados pela Fiscalização</h2>
                        <div style="text-align: justify; text-indent: 40px; padding-top: 20px"><p>Nessa etapa, 
                        apenas se verifica se os dados do VOC do arquivo incremental estão de acordo com 
                        os resultados do trabalho de fiscalização do AIS. Esse teste é chamado de 
                        Saida_INCR_F0_xxx. São feitos testes de conciliação tanto em valor quanto em 
                        quantidade. Resumidamente:</p>
    
                        <div style="text-align: justify;text-indent: 40px;">
                        <ul style="padding-left: 80px;">
                        <li>Valor proposto pela avaliadora vs valor definido pela fiscalização
                            (ou resultado SAS ou resultado ROS_VAL);</li>
                        <li>Teste de quantidade do incremental com o ROA por código de item;</li>
                        <li>Teste de quantidade do incremental com o ROA por TUC+A1;</li>
                        <li>Teste de quantidade do incremental com o ROA e com o AIS, por TUC+A1.</li>
                        </ul></div>
                            
                        <div style="text-align: justify;text-indent: 40px; padding-top: 20px"><p>O gráfico 
                        de fluxo sintetiza o processo:</p>
                        """)
            imag0 =st.columns([1, 3, 1])
            with imag0[1]:
                st.image("Imagens/INC_F0.png", caption="Representação da análise entre VOC validado e VOC Incremental.", width='stretch')
            
            st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                    a conciliação, abaixo, em valor, do VOC fiscalizado e do arquivo Incremental. 
                    Há diferenças significativas? Verifique e justifique. 
                    Abaixo é apresentado apenas os resultados.</p>
                    """)
            
            sSQL = """SELECT * FROM TST_CMP2_INCR"""
            ANL_LST_TUC = carga_sqlite_cache(sSQL, bd)
    
            for n in ANL_LST_TUC.columns.to_list():
                if n[:2].upper() in ['VL', 'QT']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(
                                            lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if pd.notnull(x) else ""
                                        )
    
            tab0 =st.columns([1, 5, 1])
            with tab0[1]:
                st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True)
        if existe_tabela('TST_CMP3_INCR', bd):
            st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                    a conciliação, abaixo, em quantidade, do ROA e do arquivo Incremental. 
                    Há diferenças significativas? Verifique e justifique. 
                    Abaixo é apresentado apenas os resultados.</p>
                    """)
            
            sSQL = """SELECT * FROM TST_CMP3_INCR"""
            ANL_LST_TUC1 = carga_sqlite_cache(sSQL, bd)
            for n in ANL_LST_TUC1.columns.to_list():
                if n[:2].upper() in ['VL', 'QT']:
                    ANL_LST_TUC1[n] = ANL_LST_TUC1[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC']:
                    ANL_LST_TUC1[n] = ANL_LST_TUC1[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab1 =st.columns([1, 5, 1])
            with tab1[1]:
                st.dataframe(ANL_LST_TUC1, width='stretch', hide_index=True)
        
        if existe_tabela('TST_CMP4_INCR', bd):
            st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                    a conciliação, usando UC e A1, abaixo, em quantidade, do ROA, do AIS e do arquivo Incremental. 
                    Há diferenças significativas? Verifique e justifique. 
                    Abaixo é apresentado apenas os resultados.</p>
                    """)
            
            sSQL = """SELECT * FROM TST_CMP4_INCR"""            
            ANL_LST_TUC2 = carga_sqlite_cache(sSQL, bd)
            for n in ANL_LST_TUC2.columns.to_list():
                if n[:2].upper() in ['VL', 'QT']:
                    ANL_LST_TUC2[n] = ANL_LST_TUC2[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC']:
                    ANL_LST_TUC2[n] = ANL_LST_TUC2[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab2 =st.columns([1, 5, 1])
            with tab2[1]:
                st.dataframe(ANL_LST_TUC2, width='stretch', hide_index=True)
        
        if existe_tabela('TST_CMP5_INCR', bd):
            st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                    a conciliação, usando Cd_SubODI, abaixo, em quantidade, do ROA, do AIS e do arquivo Incremental. 
                    Há diferenças significativas? Verifique e justifique. 
                    Abaixo é apresentado apenas os resultados.</p>
                    """)
            
            sSQL = """SELECT * FROM TST_CMP5_INCR"""
            ANL_LST_TUC3 = carga_sqlite_cache(sSQL, bd)
            for n in ANL_LST_TUC3.columns.to_list():
                if n[:2].upper() in ['VL', 'QT']:
                    ANL_LST_TUC3[n] = ANL_LST_TUC3[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC']:
                    ANL_LST_TUC3[n] = ANL_LST_TUC3[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab3 =st.columns([1, 5, 1])
            with tab3[1]:
                st.dataframe(ANL_LST_TUC3, width='stretch', hide_index=True)

@st.fragment()
def _vis_002(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if existe_tabela('TX_JOA_APL', bd):
            st.html(f"""<h2>JOA regulatório por Tipologia</h2>
                    <p  style="text-align: justify;text-indent: 40px">Apresentamos os dados
                    do JOA regulatório por tipologia para avaliar os cálculos do Laudo.</p>
                    """)
            
            sSQL = """SELECT * FROM TX_JOA_APL"""
            ANL_LST_TUC4 = carga_sqlite_cache(sSQL, bd)
            for n in ANL_LST_TUC4.columns.to_list():
                if n[:2].upper() in ['VL', 'QT']:
                    ANL_LST_TUC4[n] = ANL_LST_TUC4[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC','TX']:
                    ANL_LST_TUC4[n] = ANL_LST_TUC4[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab0 =st.columns([1, 5, 1])
            with tab0[1]:
                st.dataframe(ANL_LST_TUC4, width='stretch', hide_index=True)

@st.fragment()
def _vis_003(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if existe_tabela('TST_CD_SISBASE', bd):
            st.html(f"""<h2>Teste do Código SISBASE</h2>
                        <p  style="text-align: justify;text-indent: 40px">Apresentamos o resultado
                    da validação do código SISBASE. 
                    Abaixo é apresentado apenas os resultados.</p>
                    """)
            
            sSQL = """
                    SELECT * FROM TST_CD_SISBASE
    
                    """
            ANL_LST_TUC5 = carga_sqlite_cache(sSQL, bd)
            tab0 =st.columns([1, 5, 1])
            with tab0[1]:
                st.dataframe(ANL_LST_TUC5, width='stretch', hide_index=True)

@st.fragment()
def _vis_004(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if existe_tabela('TST_VAO_MIN_INCR', bd):
            st.html(f"""<h2>Teste do Vão Mínimo para Redes e Ramais</h2>
                        <p  style="text-align: justify;text-indent: 40px">Apresentamos o resultado
                    de análise dos vãos para redes aéreas e ramais, urbanos e rurais. 
                    Abaixo é apresentado apenas os resultados.</p>
                    """)
            
            sSQL = """SELECT * FROM TST_VAO_MIN_INCR"""
            ANL_LST_TUC6 = carga_sqlite_cache(sSQL, bd)
            for n in ANL_LST_TUC6.columns.to_list():
                if n[:2].upper() in ['QT']:
                    ANL_LST_TUC6[n] = ANL_LST_TUC6[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            tab0 =st.columns([1, 5, 1])
            with tab0[1]:
                st.dataframe(ANL_LST_TUC6, width='stretch', hide_index=True)
        
        if existe_tabela('TST_MED_INCR', bd):
            st.html(f"""<h2>Teste de tipologias de medição</h2>
                        <p  style="text-align: justify;text-indent: 40px">Apresentamos o resultado
                    de análise das tipologias de medição, urbanos e rurais. 
                    Abaixo é apresentado os resultados.</p>
                    """)
            
            sSQL = """SELECT * FROM TST_MED_INCR"""
            ANL_LST_TUC7 = carga_sqlite_cache(sSQL, bd)
            for n in ANL_LST_TUC7.columns.to_list():
                if n[:2].upper() in ['QT']:
                    ANL_LST_TUC7[n] = ANL_LST_TUC7[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            tab1 =st.columns([1, 5, 1])
            with tab1[1]:
                st.dataframe(ANL_LST_TUC7, width='stretch', hide_index=True)
    
        if existe_tabela('ANL_LIMITES_VOC', bd):
            st.html(f"""<h2>Teste de limitação 90 e 110</h2>
                        <p  style="text-align: justify;text-indent: 40px">Apresentamos o resultado
                    de análise do limitador de 90 e 110, nas obras valoradas por BPR, por
                    tipologia. 
                    Abaixo é apresentado apenas os resultados.</p>
                    """)
            
            sSQL = """SELECT * FROM ANL_LIMITES_VOC"""
            ANL_LST_TUC8 = carga_sqlite_cache(sSQL, bd)
            for n in ANL_LST_TUC8.columns.to_list():
                if n[:2].upper() in ['VL']:
                    ANL_LST_TUC8[n] = ANL_LST_TUC8[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PE']:
                    ANL_LST_TUC8[n] = ANL_LST_TUC8[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab2 =st.columns([1, 5, 1])
            with tab2[1]:
                st.dataframe(ANL_LST_TUC8, width='stretch', hide_index=True)

@st.fragment()
def _vis_005(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if existe_tabela('ANL_ALMOX', bd):
            st.html(f"""<h2>Teste dos itens de Almoxarifado</h2>
                    <p  style="text-align: justify;text-indent: 40px">Apresentamos o resultado
                    de análise do almoxarifado, por item, para a empresa. 
                    Abaixo é apresentado apenas os resultados.</p>
                    """)
            
            sSQL = """SELECT * FROM ANL_ALMOX"""
            ANL_LST_TUC9 = carga_sqlite_cache(sSQL, bd)
            for n in ANL_LST_TUC9.columns.to_list():
                if n[:2].upper() in ['VL']:
                    ANL_LST_TUC9[n] = ANL_LST_TUC9[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PE']:
                    ANL_LST_TUC9[n] = ANL_LST_TUC9[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab0 =st.columns([1, 5, 1])
            with tab0[1]:
                st.dataframe(ANL_LST_TUC9, width='stretch', hide_index=True)
    
        if existe_tabela('ANL_VL_MENSAL', bd):
            st.html(f"""<h2>Teste do saldo mensal de Almoxarifado</h2>
                        <p  style="text-align: justify;text-indent: 40px">Apresentamos o resultado
                    de análise do saldo médio mensal, para a empresa. 
                    Abaixo é apresentado apenas os resultados.</p>
                    """)
            
            sSQL = """SELECT * FROM ANL_VL_MENSAL"""
            ANL_LST_TUC10 = carga_sqlite_cache(sSQL, bd)
            for n in ANL_LST_TUC10.columns.to_list():
                if n[:2].upper() in ['VL']:
                    ANL_LST_TUC10[n] = ANL_LST_TUC10[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PE']:
                    ANL_LST_TUC10[n] = ANL_LST_TUC10[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab1 =st.columns([1, 5, 1])
            with tab1[1]:
                st.dataframe(ANL_LST_TUC10, width='stretch', hide_index=True)

@st.fragment()
def _vis_006(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if existe_tabela('ANL_INCREMENTAL', bd):
            st.html(f"""<h2>Teste analítico do arquivo INCREMENTAL</h2>
                        <p  style="text-align: justify;text-indent: 40px">Apresentamos o resultado
                    de análise do arquivo incremental, visão analítica, para a empresa. 
                    Abaixo é apresentado apenas os resultados.</p>
                    """)
            
            sSQL = """SELECT * FROM ANL_INCREMENTAL"""
            ANL_LST_TUC11 = carga_sqlite_cache(sSQL, bd)
            for n in ANL_LST_TUC11.columns.to_list():
                ANL_LST_TUC11[n] = ANL_LST_TUC11[n].fillna(0)
                if ANL_LST_TUC11[n].dtype != 'object':
                    if n[:2].upper() in ['VL','FA','QT']:
                        ANL_LST_TUC11[n] = ANL_LST_TUC11[n].fillna(0)
                        ANL_LST_TUC11[n] = ANL_LST_TUC11[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    elif n[:3].upper() in ['TX_', 'DEP']:
                        ANL_LST_TUC11[n] = ANL_LST_TUC11[n].fillna(0)
                        ANL_LST_TUC11[n] = ANL_LST_TUC11[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                else:
                    if n[:2].upper() in ['VL','FA','QT']:
                        ANL_LST_TUC11[n] = ANL_LST_TUC11[n].fillna(0)
                        ANL_LST_TUC11[n] = ANL_LST_TUC11[n].apply(lambda x: f"{float(str(x).replace(',', '.')):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    elif n[:3].upper() in ['TX_', 'DEP']:
                        ANL_LST_TUC11[n] = ANL_LST_TUC11[n].fillna(0)
                        ANL_LST_TUC11[n] = ANL_LST_TUC11[n].apply(lambda x: f"{float(str(x).replace(',', '.')):,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                
            tab0 =st.columns([1, 5, 1])
            with tab0[1]:
                st.dataframe(ANL_LST_TUC11, width='stretch', hide_index=True)
        if existe_tabela('RES_INCR_QDTAR', bd):
            st.html(f"""<h2>RESUMO DO ARQUIVO INCREMENTAL: LAUDO vs SIMULADO</h2>
                    <p  style="text-align: justify;text-indent: 40px">A seguir tem-se o
                    o resultado consolidado do arquivo incremental, visão quadro para o
                    cálculo econômico, para a empresa. 
                    Abaixo é apresentado apenas os resultados.</p>
                    """)
                                    
            sSQL = """
                    SELECT 
                            t1."index",
                            COALESCE(t2.Valor, 0) AS VL_AVAL, 
                            COALESCE(t1.Valor, 0) AS VL_SIM,
                            CASE 
                                WHEN COALESCE(t1.Valor, 0) = 0 THEN 0
                                ELSE (COALESCE(t2.Valor, 0) / COALESCE(t1.Valor, 1) - 1)
                            END AS PCT_VAR
                    FROM RES_INCR_QDTAR_SFF t1 JOIN
                    RES_INCR_QDTAR t2 ON t1."index"=t2."index"
                    """
            ANL_LST_TUC12 = pd.read_sql(sSQL, bd)
            ordem = ['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)', '(2) Índice de Aproveitamento Integral', 
                        '(3) Obrigações Especiais Bruta', '(4) Bens Totalmente Depreciados', '(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)', 
                        '(6) Depreciação Acumulada', '(7) AIS Líquido (Valor de Mercado em Uso)', 
                        '(8) Índice de Aproveitamento Depreciado', '(9) Valor da Base de Remuneração (VBR)', 
                        '(10) Almoxarifado em Operação', '(11) Ativo Diferido', '(12) Obrigações Especiais Liquida', 
                        '(13) Terrenos e Servidões', '(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)']
            ANL_LST_TUC12 = ANL_LST_TUC12.set_index('index').loc[ordem].reset_index()
            for n in ANL_LST_TUC12.columns.to_list():
                    if ANL_LST_TUC12[n].dtype != 'object':
                        if n[:2].upper() in ['VL','FA','QT']:
                            ANL_LST_TUC12[n] = ANL_LST_TUC12[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                        elif n[:3].upper() in ['TX_', 'DEP', 'PCT']:
                            ANL_LST_TUC12[n] = ANL_LST_TUC12[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                    else:
                        if n[:2].upper() in ['VL','FA','QT']:
                            ANL_LST_TUC12[n] = ANL_LST_TUC12[n].apply(lambda x: f"{float(x.replace(',', '.')):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                        elif n[:3].upper() in ['TX_', 'DEP', 'PCT']:
                            ANL_LST_TUC12[n] = ANL_LST_TUC12[n].apply(lambda x: f"{float(x.replace(',', '.')):,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
            config = {
                    "index": st.column_config.TextColumn("Item"),
                    "VL_AVAL": st.column_config.TextColumn("Avaliadora (R$)"),
                    "VL_SIM": st.column_config.TextColumn("Simulado (R$)"),
                    "PCT_VAR": st.column_config.TextColumn("Variação (%)"),
                }       
            tab1 =st.columns([1, 5, 1])
            with tab1[1]:
                st.dataframe(ANL_LST_TUC12[ANL_LST_TUC12['index'].notnull()], width='stretch',
                            height=550, hide_index=True, column_config=config)
    
def visualizador_INCR(st = None):
    if not'tra_dir' in st.session_state:
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

    st.html("""
                <h2>Análise do Incremental</h2>
                <hr></hr>

                <h3>Observações iniciais</h3>
                <div style="text-align: justify; text-indent: 40px;">
                    Esse é um documento base para se executar análise da base incremental. 
                Pode-se alterar o arquivo, porém somente será aplicado a versão original 
                para análise do valor empregado no laudo. Sugere-se usar este arquivo como 
                base para modificações e inclusões de análises, para discussões com a 
                fiscalização.
                </div>

                <h3>Licença Pública Geral GNU (GPL)</h3>
                <div style="text-align: justify; padding-top: 10px;">
                    Versão 3, 29 de junho de 2007
                </div>
                <div style="text-align: justify; padding-top: 5px;">
                    Copyright (C) 2025, SFF/ANEEL.
                </div>
                <div style="text-align: justify; text-indent: 40px; padding-top: 10px;">
                    Este é um documento de uso livre: você pode redistribuí-lo ou modificá-lo sob os termos da Licença Pública Geral GNU, conforme publicada pela Free Software Foundation, tanto na versão 3 da Licença, ou qualquer versão posterior. Ele é distribuído na expectativa de que seja útil, mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM PROPÓSITO ESPECÍFICO. Consulte a Licença Pública Geral GNU para obter mais detalhes no sítio 
                    <a href="http://www.gnu.org/licenses/" target="_blank">http://www.gnu.org/licenses/</a>.
                </div>

                <hr></hr>

                <h3>Normas</h3>
                <div style="text-align: justify; text-indent: 40px;">
                    Conforme PRORET 2.3, item 3.5, emprega o método do Valor Novo de 
                    Reposição, VNR, que se dá pela utilização do Banco de Preços 
                    Referenciais, do Banco de Preços da Concessionária ou de Orçamento 
                    Referencial (§18-19). No entanto, há um conjunto de ativos, definidos 
                    no módulo, que a valoração se dará pela atualização de valores contábeis 
                    pelo índice IPCA, sendo definido como Valor Original Contábil (VOC)
                    Atualizado.
                </div>
                <div style="text-align: justify;text-indent: 40px; padding-top: 10px;">
                Considerando o primeiro caso, conforme PRORET 2.3, item 4.1.1, §39:<br></div>
                <p style='text-align: justify;padding-left: 60px; padding-top: 10px;'><i>39. A avaliação patrimonial não 
                representa o valor de mercado, mas sim, um valor referencial, oriundo 
                da aplicação do aproveitamento e da depreciação sobre os custos de 
                reposição para equipamentos, benfeitorias e obras civis em operação 
                (contemplados os gastos com instalações e outros custos adicionais, 
                e expurgados os gastos com impostos recuperáveis – ICMS; já os impostos 
                não-recuperáveis são considerados na formação de custos).</i></p>

                <div style="text-align: justify;text-indent: 40px">Assim, de acordo com 
                o PRORET 2.3, versão 2C, item 40, o valor novo de reposição, VNR, é 
                calculado pela equação abaixo:</div>

                """)
    st.markdown(r"""
                $$
                \large
                \begin{aligned}
                VNR = VF + COM + CA + JOA
                \end{aligned}
                $$
                <div style="text-align: justify;text-indent: 40px">Em que:</div>
                """, unsafe_allow_html=True
                )
    st.markdown(r"""
                    $$
                    \large
                    \begin{aligned}
                        VF & = \text{Valor de fábrica do equipamento principal;} \\
                        COM & = \text{Valor dos componentes acessórios vinculados a um equipamento principal;} \\
                        CA & = \text{Custos de projeto, gerenciamento, montagem e frete, de acordo com o MCSE;} \\
                        JOA & = \text{representa a remuneração da obra em curso e é aplicado para subestações, linhas e redes de distribuição.} \\
                    \end{aligned}
                    $$
                    """, unsafe_allow_html=True)
    st.html("""
                <div style="text-align: justify;text-indent: 40px; padding-top: 10px;">Nada obstante, 
                observe-se que o valor de fábrica foi tratado nos documentos de análise do 
                financeiro do ICMS e do banco de compras. No entanto, é importante 
                ressaltar o seguinte ponto sobre VF:</div>
                <p style='text-align: justify;padding-left: 60px; padding-top: 10px;'>
                <i>46. Para os bens que não se encontrarem no banco de preços da 
                concessionária deverão ser considerados bens de características similares 
                para o propósito de avaliação. Se ainda assim, não for encontrado bem 
                similar, este deve ser avaliado por meio da atualização dos valores 
                históricos contábeis pela aplicação da fórmula paramétrica correspondente 
                ao equipamento, conforme o Anexo III deste Submódulo. </i></p>
                <div style="text-align: justify;text-indent: 40px">Sobre componentes menores, item 4.1.1.2, §47:<p></p></div>

                <p style='text-align: justify;;padding-left: 60px; padding-top: 10px;'><i>47. O custo do COM será definido a partir 
                do Banco de Preços Referenciais, atribuído a cada equipamento principal, 
                conforme critérios estabelecidos neste Submódulo. </i></p>

                <div style="text-align: justify;text-indent: 40px">Algo similar se aplica 
                ao CA, item 4.1.1.3, §49:<p></p></div>

                <p style='text-align: justify;;padding-left: 60px; padding-top: 10px;'><i>49. O Custo Adicional será definido 
                a partir do Banco de Preços Referenciais, atribuído a cada equipamento 
                principal, conforme critérios estabelecidos neste Submódulo. </i></p>

                <div style="text-align: justify;text-indent: 40px">O banco de preços 
                referencial é tratado no item 4.1.2. Ele é estruturado na forma modular, no qual se associa um módulo a cada equipamento principal, codificdo de acordo com o MCPSE. Na tabela 4 do PRORETE 2.3, executa-se uma classificação dos bens:<p></p></div>

                <table align="center" style="font-family: Arial, Helvetica, sans-serif;
                                                border-collapse: collapse;; font-size: 75%;
                                                width: 100%; padding-top: 10px;">
                    <thead>
                        <tr bgcolor="lightgray">
                            <th style = "text-align: center;">Bens essenciais</th>
                            <th style = "text-align: center;">Bens Acessórios</th>
                            <th style = "text-align: center;">Bens de Infraestrutura</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="text-align:center;">Estrutura (255)</td>
                            <td style="text-align:center;">Equipamentos de rede</td>
                            <td style="text-align:center;">Sistemas diversos</td>
                        </tr>
                        <tr>
                            <td style="text-align:center;">Condutor (190)</td>
                            <td style="text-align:center;">Equipamentos de linha</td>
                            <td style="text-align:center;">Imóveis operacionais</td>
                        </tr>
                        <tr>
                            <td style="text-align:center;">Transformador de distribuição (565)</td>
                            <td style="text-align:center;">Equipamentos de subestações</td>
                            <td style="text-align:center;">Equipamentos não modularizáveis</td>
                        </tr>
                        <tr>
                            <td style="text-align:center;">Transformador de força (570)</td>
                            <td style="text-align:center;">Equipamentos de sistemas de medição</td>
                            <td style="text-align:center;"></td>
                        </tr>
                        <tr>
                            <td style="text-align:center;">Medidores (295)</td>
                            <td style="text-align:center;"></td>
                            <td style="text-align:center;"></td>
                        </tr>
                    </tbody>
                </table>

                <div style="text-align: justify;text-indent: 40px; padding-top: 10px;">A 
                estrutura modular está no Anexo IV do PRORET 2.3, conquanto a relação de 
                módulos está no Anexo V. A atualização dos valores de COM e CA é feita por 
                meio do IPCA, da data base do banco para a do laudo. As empresas são 
                classificadas em grupos (tabela 5 do PRORET) e, também, os valores de COM e 
                CA são de acordo com o grupo a que pertencem. Para os bens que possuem 
                correspondência modular, mas não tiverem valor definido para o módulo no 
                banco de preços referenciais, no período de aplicação do banco, bem como 
                para os bens que não possuem correspondência modular, a valoração do COM 
                e CA desses TUCs para a base de remuneração será feita a partir da 
                apuração do AIS, ou seja, pelo Valor Original Contábil (VOC) atualizado. 
                Para os medidores em Subestações, bem como para os de fronteira, a 
                classificação do Medidor deve ser efetivada no TUC 305 (Painel, Mesa de 
                Comando e Cubículo), o qual será considerado como um Tipo de Bem de 
                Infraestrutura, sendo valorado pelo VOC atualizado. Para os bens de 
                Infraestrutura, a valoração será feita pelo VOC atualizado. A tabela a 
                seguir relaciona os TUCs de Infraestrutura:<br><br></div>
                    <table align="center" style="font-family: Arial, Helvetica, sans-serif;
                                                border-collapse: collapse; font-size: 75%;
                                                width: 100%; padding-top: 10px;">
                        <thead bgcolor="lightgray">
                            <tr>
                                <th style="text-align:center;">Código</th>
                                <th style="text-align:center;">Tipo de Unidade de Cadastro</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td style="text-align:center;">100</td><td>ARMAZENAGEM, MANIPULAÇÃO E TRANSPORTE DE COMBUSTÍVEL LÍQUIDO OU GASOSO</td></tr>
                            <tr><td style="text-align:center;">112</td><td>ARMAZENAGEM, MANIPULAÇÃO E TRANSPORTE DE RESÍDUO</td></tr>
                            <tr><td style="text-align:center;">120</td><td>BALANÇA PARA VEÍCULOS DE CARGA</td></tr>
                            <tr><td style="text-align:center;">135.03</td><td>CONJUNTO DE ISOLADORES DE PEDESTAL</td></tr>
                            <tr><td style="text-align:center;">145</td><td>CÂMARA E GALERIA</td></tr>
                            <tr><td style="text-align:center;">180</td><td>CONDUTO E CANALETA</td></tr>
                            <tr><td style="text-align:center;">190.03</td><td>CONJUNTO DE CADEIA DE ISOLADORES</td></tr>
                            <tr><td style="text-align:center;">205.05</td><td>SERVIDÕES</td></tr>
                            <tr><td style="text-align:center;">215</td><td>EDIFICAÇÃO</td></tr>
                            <tr><td style="text-align:center;">220</td><td>ELEVADOR E TELEFÉRICO</td></tr>
                            <tr><td style="text-align:center;">250</td><td>ESTRADA DE ACESSO</td></tr>
                            <tr><td style="text-align:center;">265</td><td>ESTRUTURA SUPORTE DE EQUIPAMENTO E DE BARRAMENTO</td></tr>
                            <tr><td style="text-align:center;">270</td><td>FIBRA ÓTICA</td></tr>
                            <tr><td style="text-align:center;">285</td><td>INSTALAÇÕES DE RECREAÇÃO E LAZER</td></tr>
                            <tr><td style="text-align:center;">305</td><td>PAINEL, MESA DE COMANDO E CUBÍCULO</td></tr>
                            <tr><td style="text-align:center;">315</td><td>PONTE ROLANTE, GUINDASTE OU PÓRTICO</td></tr>
                            <tr><td style="text-align:center;">355</td><td>SISTEMA ANTI-RUÍDO</td></tr>
                            <tr><td style="text-align:center;">360</td><td>SISTEMA DE ABASTECIMENTO DE ÁGUA</td></tr>
                            <tr><td style="text-align:center;">365</td><td>SISTEMA DE ÁGUA DE ALIMENTAÇÃO</td></tr>
                            <tr><td style="text-align:center;">375</td><td>SISTEMA DE ALIMENTAÇÃO DE ENERGIA</td></tr>
                            <tr><td style="text-align:center;">385</td><td>SISTEMA DE AR COMPRIMIDO</td></tr>
                            <tr><td style="text-align:center;">395</td><td>SISTEMA DE ATERRAMENTO</td></tr>
                            <tr><td style="text-align:center;">400</td><td>SISTEMA DE COLETA DE ÓLEO ISOLANTE</td></tr>
                            <tr><td style="text-align:center;">405</td><td>SISTEMA DE COLETA E TRATAMENTO DE LIXO</td></tr>
                            <tr><td style="text-align:center;">410</td><td>SISTEMA DE COMUNICAÇÃO E PROTEÇÃO CARRIER</td></tr>
                            <tr><td style="text-align:center;">415</td><td>SISTEMA DE COMUNICAÇÃO LOCAL</td></tr>
                            <tr><td style="text-align:center;">430</td><td>SISTEMA DE DADOS METEOROLÓGICOS, HIDROLÓGICOS E SISMOLÓGICOS</td></tr>
                            <tr><td style="text-align:center;">445</td><td>SISTEMA DE DRENAGEM, ENCHIMENTO E ESGOTAMENTO</td></tr>
                            <tr><td style="text-align:center;">450</td><td>SISTEMA DE ESGOTO SANITÁRIO</td></tr>
                            <tr><td style="text-align:center;">455</td><td>SISTEMA DE EXAUSTÃO, VENTILAÇÃO E AR CONDICIONADO</td></tr>
                            <tr><td style="text-align:center;">460</td><td>SISTEMA DE ILUMINAÇÃO E FORÇA</td></tr>
                            <tr><td style="text-align:center;">465</td><td>SISTEMA DE LUBRIFICAÇÃO, DE ÓLEO DE REGULAÇÃO E DE ÓLEO ISOLANTE OU PARA ISOLAMENTO</td></tr>
                            <tr><td style="text-align:center;">480</td><td>SISTEMA DE PROTEÇÃO CONTRA INCÊNDIO</td></tr>
                            <tr><td style="text-align:center;">485</td><td>SISTEMA DE PROTEÇÃO, MEDIÇÃO E AUTOMAÇÃO</td></tr>
                            <tr><td style="text-align:center;">495</td><td>SISTEMA DE RADIOCOMUNICAÇÃO</td></tr>
                            <tr><td style="text-align:center;">515</td><td>SISTEMA DE RESFRIAMENTO DE EQUIPAMENTOS</td></tr>
                            <tr><td style="text-align:center;">520</td><td>SISTEMA DE VIGILÂNCIA ELETRÔNICA</td></tr>
                            <tr><td style="text-align:center;">540</td><td>SUBESTAÇÃO SF 6</td></tr>
                            <tr><td style="text-align:center;">545</td><td>SUBESTAÇÃO UNITÁRIA</td></tr>
                            <tr><td style="text-align:center;">555</td><td>TERRENO</td></tr>
                            <tr><td style="text-align:center;">610</td><td>URBANIZAÇÃO E BENFEITORIAS</td></tr>
                            <tr><td style="text-align:center;">615.03</td><td>VEÍCULO OPERACIONAL ESPECIAL (Derrick Digger)</td></tr>
                        </tbody>
                    </table>
                    <div style="text-align: justify;text-indent: 40px; padding-top: 20px">A 
                    tabela 7, sumariza o processo de valoração:<p></p></div>

                    <table align="center" style="font-family: Arial, Helvetica, sans-serif;
                                                border-collapse: collapse; font-size: 75%;
                                                width: 100%; padding-top: 10px;">
                        <thead bgcolor="lightgray">
                            <tr>
                                <th rowspan = "2" style = "text-align: center">Bens</th>
                                <th rowspan = "2" style = "text-align: center">Valor de fábrica (Equipamento Principal)</th>
                                <th colspan = "3" style = "border-bottom: 1pt solid black; border-collapse: collapse; text-align: center">COM e CA</th>
                            </tr>
                            <tr bgcolor="lightgray">
                                <th colspan = "2" bgcolor="lightgray" style = "text-align: center">Características</th>
                                <th bgcolor="lightgray" style = "text-align: center">Valoração</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                            <td rowspan = "3" style = "border-bottom: 1pt solid black; border-collapse: collapse;text-align: center">Essenciais e Acessórios</td>
                            <td rowspan = "3" style = "border-bottom: 1pt solid black; border-collapse: collapse;text-align: center">Banco de preços da concessionária, atualizado pelas fórmulas paramétricas</td>
                            <td rowspan = "2" style = "border-bottom: 1pt solid black; border-collapse: collapse;text-align: center">Modularizado</td>
                            <td style = "border-bottom: 1pt solid black; border-collapse: collapse;text-align: center">Com valor no BPR</td>
                            <td style = "border-bottom: 1pt solid black; border-collapse: collapse;text-align: center">Módulo BPR</td>
                            </tr>
                            <tr>
                            <td style = "border-bottom: 1pt solid black; border-collapse: collapse;text-align: center">Sem valor no BPR</td>
                            <td style = "border-bottom: 1pt solid black; border-collapse: collapse;text-align: center">VOC Atualizado</td>
                            </tr>
                            <tr>
                            <td colspan = "2" style = "border-bottom: 1pt solid black; border-collapse: collapse;text-align: center">Não Modularizado</td>
                            <td style = "border-bottom: 1pt solid black; border-collapse: collapse;text-align: center">VOC Atualizado</td>
                            </tr>
                            <tr>
                            <td style = "border-bottom: 1pt solid black; border-collapse: collapse;text-align: center">Infraestrutura</td>
                            <td colspan = "4" style = "border-bottom: 1pt solid black; border-collapse: collapse;text-align: center">VOC Atualizado</td>
                            </tr>
                        
                    </tbody>
                    </table>
                    <div style="text-align: justify;text-indent: 40px; padding-top: 30px">
                    Além dos TUCs de infraestrutura e não modularizados, alguns tipos de obras 
                    serão tratados como casos atípicos, sendo que todas as obras enquadradas 
                    nessa situação deverão ser valoradas pelo VOC atualizado e estarão sujeitas 
                    à validação e ajustes pela fiscalização da ANEEL. As principais obras que 
                    se enquadram nessa situação são:</div>

                    <div style="text-align: justify;text-indent: 40px; padding-top: 10px">
                    <ul>
                        <li>Expansão em Linha Viva;</li>
                        <li>Recondutoramento de circuitos;</li>
                        <li>Recapacitação de linhas;</li>
                        <li>Instalação ou substituição de UAR que não seja a própria UC;</li>
                        <li>Redes e Linhas de Distribuição Subterrâneas ou Submersas (todas as TUCs associadas);</li>
                        <li>Estruturas tipo Torre (TUC 255.02);</li>
                        <li>Estruturas tipo Poste em Linhas de Distribuição (TUC 255.01);</li>
                        <li>Sistemas especiais de medição; e</li>
                        <li>Novas tecnologias, ainda não modularizadas.</li>
                        </ul>
                    </div>

                    <div style="text-align: justify;text-indent: 40px; padding-top: 10px">As 
                    obras que se enquadrarem como casos atípicos devem estar claramente 
                    identificadas no laudo de avaliação, especificando o “Tipo de Projeto” 
                    como Atípico e a descrição da obra. Demais situações de obras não 
                    passíveis de modularização deverão ser informadas previamente à área de 
                    fiscalização, que caso sejam aceitas como atípicas, seguirão o mesmo 
                    tratamento dessas.</div>

                    <div style="text-align: justify;text-indent: 40px; padding-top: 10px">O 
                    Banco de Preços Referenciais, revisão 2.0 do Submódulo 2.3, será 
                    aplicado aos investimentos realizados e unitizados contabilmente entre a 
                    data 1º de junho de 2016 a 31 de julho de 2021. O Banco de Preços 
                    Referenciais, revisão 2.0c deste Submódulo, será aplicado aos 
                    investimentos realizados e unitizados contabilmente a partir de 1º de 
                    agosto de 2021. O prazo de transição de 180 (cento e oitenta) dias se 
                    aplica nos casos de revisão metodológica do banco.</div>
                    <div style="text-align: justify;text-indent: 40px; padding-top: 10px">
                    Para a aprovação da base de remuneração, nos investimentos realizados no 
                    período de aplicação do Banco de Preços Referenciais, será considerado 
                    como limite inferior o valor de 90% (noventa por cento) do VOC 
                    atualizado e como limite superior o valor de 110% (cento e dez por cento) 
                    do VOC atualizado. Essa faixa de aceitação se aplica no valor global dos 
                    investimentos por Tipo de Instalação (Redes de Distribuição, Linhas de 
                    Distribuição, Subestações e Medição), valorados exclusivamente pelo 
                    Banco de Preços Referenciais e excluindo-se o JOA.</div>

                    <div style="text-align: justify;text-indent: 40px; padding-top: 10px">Para 
                    o JOA, item 4.1.1.4, §51:</div>

                    <p style='text-align: justify;; padding-left: 60px; padding-top: 10px;'><i>51. O JOA é definido regulatoriamente e 
                    calculado considerando-se o WACC real após impostos, aplicando-se a 
                    fórmula a seguir, de acordo com as considerações abaixo:</i></p>

                """)
    st.markdown(r"""
                    $$
                    \large
                    \begin{aligned}
                        JOA = \sum_{i=1}^{N}\left ( \left ( 1+r \right )^{\frac{N+1-i}{12}} -1\right )\cdot C_{i}
                    \end{aligned}
                    $$
                """)
    st.html("""
                    <div style="text-align: justify;text-indent: 40px;">Em que:</div>
                    <div style="text-align: justify;text-indent: 100px;; padding-top: 10px">
                        <p><i>JOA</i> = Juros sobre obras em andamento;</p>
                        <p><i>N</i> = número de meses de acordo com o tipo de obra;</b>;</p>
                        <p><i>r</i> = custo médio ponderado de capital anual (WACC);</p>
                        <p><i>C<sub>i</sub></i> = desembolso mensal em percentual (%), distribuido em 
                        acordo com o fluxo financeiro.</p>
                    </div>                       
                    <div style="text-align: justify;text-indent: 40px; padding-top: 10px">Abaixo a tabela 2,
                        do PRORET 2.3, que trata do prazo médio de construção para as 
                    tipologias.<br><br></div>
                    <div>
                    <table align="center" style="font-family: Arial, Helvetica, sans-serif;
                                                border-collapse: collapse; font-size: 75%;
                                                width: 90%; padding-top: 10px;">
                        <thead bgcolor="lightgray">
                            <tr>
                                <th style="text-align: center;">Tipologia</th>
                                <th style="text-align: center;">Grupos* 1, 2 e 3</th>
                                <th style="text-align: center;">Grupos* 4 e 5</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="text-align: center;">Redes de Distribuição Aéreas (RDA)</td>
                                <td style="text-align: center;">5</td>
                                <td style="text-align: center;">3</td>
                            </tr>
                            <tr>
                                <td style="text-align: center;">Redes de Distribuição Subterrâneas (RDS)</td>
                                <td style="text-align: center;">6</td>
                                <td style="text-align: center;">4</td>
                            </tr>
                            <tr>
                                <td style="text-align: center;">Linhas de Distribuição Aéreas e Subterrâneas (LDA/LDS)</td>
                                <td style="text-align: center;">12</td>
                                <td style="text-align: center;">14</td>
                            </tr>
                            <tr>
                                <td style="text-align: center;">Subestações (SE)</td>
                                <td style="text-align: center;">9</td>
                                <td style="text-align: center;">8</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div style="text-align: justify;text-indent: 40px; padding-top: 10px; 
                padding-bottom: 10px">Deve-se considerar 40% de desembolso distribuído ao 
                longo da primeira metade do prazo de construção e 60% distribuídos ao longo 
                da segunda e última metade do prazo de construção considerado, conforme 
                tabela abaixo.<br><br></div>

                <table align="center" style="font-family: Arial, Helvetica, sans-serif;
                                                border-collapse: collapse; font-size: 75%;
                                                width: 90%; padding-top: 10px;">
                    <thead bgcolor="lightgray">
                        <tr>
                            <th rowspan = "2" style = "text-align: center">Desembolso</th>
                            <th colspan = "4" style = "border-bottom: 1pt solid black; border-collapse: collapse; text-align: center">Grupos 1, 2 e 3</th>
                            <th colspan = "4" style = "border-bottom: 1pt solid black; border-collapse: collapse; text-align: center">Grupos 4 e 5</th>
                        </tr>
                        <tr>
                            <th bgcolor="lightgray" style = "text-align: center">RDA</th>
                            <th bgcolor="lightgray" style = "text-align: center">RDS</th>
                            <th bgcolor="lightgray" style = "text-align: center">LDA/LDS</th>
                            <th bgcolor="lightgray" style = "text-align: center">SE</th>
                            <th bgcolor="lightgray" style = "text-align: center">RDA</th>
                            <th bgcolor="lightgray" style = "text-align: center">RDS</th>
                            <th bgcolor="lightgray" style = "text-align: center">LDA/LDS</th>
                            <th bgcolor="lightgray" style = "text-align: center">SE</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                        <td style = "text-align: center">d<sub>1</sub></td>
                        <td style = "text-align: center">15,00%</td>
                        <td style = "text-align: center">13,00%</td>
                        <td style = "text-align: center">6,66%</td>
                        <td style = "text-align: center">8,00%</td>
                        <td style = "text-align: center">25,00%</td>
                        <td style = "text-align: center">20,00%</td>
                        <td style = "text-align: center">5,71%</td>
                        <td style = "text-align: center">10,00%</td>
                        </tr>
                        <tr>
                        <td style = "text-align: center">d<sub>2</sub></td>
                        <td style = "text-align: center">15,00%</td>
                        <td style = "text-align: center">13,00%</td>
                        <td style = "text-align: center">6,66%</td>
                        <td style = "text-align: center">8,00%</td>
                        <td style = "text-align: center">35,00%</td>
                        <td style = "text-align: center">20,00%</td>
                        <td style = "text-align: center">5,71%</td>
                        <td style = "text-align: center">10,00%</td>
                        </tr>
                        <tr>
                        <td style = "text-align: center">d<sub>3</sub></td>
                        <td style = "text-align: center">20,00%</td>
                        <td style = "text-align: center">14,00%</td>
                        <td style = "text-align: center">6,66%</td>
                        <td style = "text-align: center">8,00%</td>
                        <td style = "text-align: center">40,00%</td>
                        <td style = "text-align: center">30,00%</td>
                        <td style = "text-align: center">5,71%</td>
                        <td style = "text-align: center">10,00%</td>
                        </tr>
                        <tr>
                        <td style = "text-align: center">d<sub>4</sub></td>
                        <td style = "text-align: center">25,00%</td>
                        <td style = "text-align: center">20,00%</td>
                        <td style = "text-align: center">6,66%</td>
                        <td style = "text-align: center">8,00%</td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">30,00%</td>
                        <td style = "text-align: center">5,71%</td>
                        <td style = "text-align: center">10,00%</td>
                        </tr>
                        <tr>
                        <td style = "text-align: center">d<sub>5</sub></td>
                        <td style = "text-align: center">25,00%</td>
                        <td style = "text-align: center">20,00%</td>
                        <td style = "text-align: center">6,66%</td>
                        <td style = "text-align: center">8,00%</td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">30,00%</td>
                        <td style = "text-align: center">5,71%</td>
                        <td style = "text-align: center">15,00%</td>
                        </tr>
                        <tr>
                        <td style = "text-align: center">d<sub>6</sub></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">20,00%</td>
                        <td style = "text-align: center">6,70%</td>
                        <td style = "text-align: center">15,00%</td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">5,71%</td>
                        <td style = "text-align: center">15,00%</td>
                        </tr>
                        <tr>
                        <td style = "text-align: center">d<sub>7</sub></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">10,00%</td>
                        <td style = "text-align: center">15,00%</td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">5,74%</td>
                        <td style = "text-align: center">15,00%</td>
                        </tr>
                        <tr>
                        <td style = "text-align: center">d<sub>8</sub></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">10,00%</td>
                        <td style = "text-align: center">15,00%</td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">8,57%</td>
                        <td style = "text-align: center">15,00%</td>
                        </tr>
                        <tr>
                        <td style = "text-align: center">d<sub>9</sub></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">10,00%</td>
                        <td style = "text-align: center">15,00%</td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">8,57%</td>
                        <td style = "text-align: center"></td>
                        </tr>
                        <tr>
                        <td style = "text-align: center">d<sub>10</sub></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">10,00%</td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">8,57%</td>
                        <td style = "text-align: center"></td>
                        </tr>
                        <tr>
                        <td style = "text-align: center">d<sub>11</sub></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">10,00%</td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">8,57%</td>
                        <td style = "text-align: center"></td>
                        </tr>
                        <tr>
                        <td style = "text-align: center">d<sub>12</sub></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">10,00%</td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">8,57%</td>
                        <td style = "text-align: center"></td>
                        </tr>
                        <tr>
                        <td style = "text-align: center">d<sub>13</sub></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">10,00%</td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">8,57%</td>
                        <td style = "text-align: center"></td>
                        </tr>
                        <tr>
                        <td style = "text-align: center">d<sub>14</sub></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center"></td>
                        <td style = "text-align: center">8,58%</td>
                        <td style = "text-align: center"></td>
                        </tr>
                </tbody>
                </table>

                <div style="text-align: justify;text-indent: 40px; padding-top: 10px">Lembremos que não se aplica JOA em medidores (§52) e que o custo de capital deve conserar a média ponderada dos valores regulatórios vigentes (§53).<p></p></div>

                <a href="https://www.gov.br/aneel/pt-br/centrais-de-conteudos/procedimentos-regulatorios/proret">Visite o sitio da Aneel para mais detalhes!</a>
                </div>>
                <br><br><br>
                <hr></hr>
                <h2>Resultados</h2>
                <hr></hr>
                """)

    executar_vis(_vis_001, bd_path, st, empresa, bd_EFD_path)
    executar_vis(_vis_002, bd_path, st, empresa, bd_EFD_path)
    executar_vis(_vis_003, bd_path, st, empresa, bd_EFD_path)    
    executar_vis(_vis_004, bd_path, st, empresa, bd_EFD_path)
    executar_vis(_vis_005, bd_path, st, empresa, bd_EFD_path)
    executar_vis(_vis_006, bd_path, st, empresa, bd_EFD_path)
    