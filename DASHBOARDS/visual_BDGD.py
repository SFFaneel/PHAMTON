import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3 as sl
import pandas as pd, numpy as np
from dateutil import relativedelta
from datetime import datetime
from datetime import date
import os
from pathlib import Path
import geopandas as gpd
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.patches as mpatches
from shapely.geometry import Point
from scipy.spatial import cKDTree
import base64

from BDGD import (
                 plt_grafico, 
                 vao_medio, 
                 csv_to_local,
                 combina_arq_shp, 
                 bsc_dd_SEC, 
                 bsc_dd_REG, 
                 bsc_dd_CR, 
                 segcon_AT
                 )
from UTILS import (
                    existe_tabela,
                    bsc_dados_reg,
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
def _vis_001(bd_path, sufixo="AT", local =""):
    with sl.connect(bd_path) as bd_AT:
        if not existe_tabela(f'RCP_BDGD_{sufixo}', bd_AT):
            return
        texto_AX = "atuais" if sufixo == "AT" else "anteriores"
        st.html(f"""<h2>Análise dos ativos dos dados georeferenciados {texto_AX}</h2>
                    <p  style="text-align: justify;text-indent: 40px">Resumo dos principais
                    ativos da base georeferenciada, uma base sintética com o controle
                    patrimonial georeferenciado. Serão empregados para análise comparativa,
                    com a base contábil, em etapa posterior. Observe se há anomalias.
                    Leie o relatório do AIS para análise completa.</p>
                    """)
        sSQL = f"""SELECT * FROM RCP_BDGD_{sufixo}"""
        RCP = pd.read_sql(sSQL, bd_AT)
        for n in RCP.columns.to_list():
            if n[:2].upper() == 'QT':
                RCP[n] = RCP[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        colsd = st.columns([1,3,1], gap='small')
        with colsd[1]:
            st.dataframe(RCP, width='stretch', hide_index=True)
        RCP.to_csv(f'{local}\BDGD_ANLS\RCP_BDGD_{sufixo}.csv', sep="|", index=False)

@st.fragment()
def _vis_002(bd_path, sufixo="AT", local =""):
    with sl.connect(bd_path) as bd_AT:
        if not existe_tabela(f'RCP_TOT', bd_AT):
            return
        st.html(f"""<h2>
                    Relatório de controle patrimonial consolidado</h2>
                    <p  style="text-align: justify;text-indent: 40px">Resumo dos principais
                    ativos da base georeferenciada, anterior e atual, e também os dados contábeis
                    de baixas, incremental, blindada. Observe se há anomalias.
                    Leie o relatório do 
                    AIS para análise completa.</p>
                    """)
        if st.session_state.dt_fim >= date.today():
            sSQL = """
                    SELECT 
                        TUC, 
                        Qtd_BDGD_AT, 
                        Qtd_AIS, 
                        Qtd_BDGD_ANT, 
                        DT_BDGD_AT_AIS 
                    FROM 
                        RCP_TOT 
                    WHERE 
                        TUC > 0 AND TUC <> '' 
                    """
        else:
            sSQL = """
                    SELECT 
                        * 
                    FROM 
                        RCP_TOT 
                    WHERE 
                        TUC > 0 AND TUC <> '' 

                    """
        RCP = pd.read_sql(sSQL, bd_AT)
        for n in RCP.columns.to_list():
            if n[:2].upper() in ['QT', 'BD']:
                RCP[n] = RCP[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            elif n[:2] == 'DT':
                RCP[n] = RCP[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))

        colsb = st.columns([1,3,1], gap='small')
        with colsb[1]:
            st.dataframe(RCP, width='stretch', hide_index=True)

        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">A seguir temos a tabela 
                    resumida num gráfico para as principais UC.</p>
                    """)

        x = plt_grafico(f'{local}', bd_AT, st)
        if not x:
            st.error("Falha na geração do gráfico.")

@st.fragment()
def _vis_003(bd_path, sufixo="AT", local =""):
    with sl.connect(bd_path) as bd:
        if not existe_tabela(f'REL_RCP_MTnv_INCR', bd):
            return

        st.html(f"""<h2>Relatório de controle patrimonial consolidado, chave completa</h2>
                    <p  style="text-align: justify;text-indent: 40px">Resumo dos principais
                    ativos da base georeferenciada, atual, comparada com a base
                    incremental. Observe se há anomalias.
                    Abaixo é apresentado os resultados, leie o relatório REL_CONCILIACAO_INCR.xlsx para análise completa.</p>
                    """)
        sSQL = """SELECT * FROM REL_RCP_MTnv_INCR"""
        RCP = pd.read_sql(sSQL, bd)

        for n in RCP.columns.to_list():
            if n[:2].upper() in ['QT','TO']:
                RCP[n] = RCP[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            elif n[:2].upper() == 'PC':
                RCP[n] = RCP[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
        colsa = st.columns([1,3,1], gap='small')
        with colsa[1]:
            st.dataframe(RCP, width='stretch', hide_index=True)
        
        if existe_tabela('REL_RCP_BDGDnc_MTnv_INCR', bd):
            sSQL = """SELECT * FROM REL_RCP_BDGDnc_MTnv_INCR"""
            RCP = pd.read_sql(sSQL, bd)
            if len(RCP)>0:
                st.html("""
                            <p  style="text-align: justify;text-indent: 40px">Resumo dos principais
                            ativos da base georeferenciada, atual, que não foram conciliados. 
                            Leie o relatório REL_CONCILIACAO_INCR.xlsx para análise completa.</p>
                            """)

                for n in RCP.columns.to_list():
                    if n[:2].upper() in ['QT']:
                        if RCP[n].dtype == 'object':
                            RCP[n] = pd.to_numeric(
                                                        RCP[n].astype(str).str.replace(',', '.', regex=False), 
                                                        errors='ignore'
                                                    )
                        RCP[n] = RCP[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    elif n[:2] == 'PC':
                        RCP[n] = RCP[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))

                colse = st.columns([4,2,4], gap='small')
                with colse[1]:
                    st.dataframe(RCP, width='stretch', hide_index=True)

        if existe_tabela('REL_RCP_AISnc_MTnv_INCR', bd):
            sSQL = """
                    SELECT * FROM 
                    REL_RCP_AISnc_MTnv_INCR

                    """
            RCP = pd.read_sql(sSQL, bd)
            
            if len(RCP)>0:
                st.html("""
                            <p  style="text-align: justify;text-indent: 40px">Resumo dos principais
                            ativos do AIS incremental não conciliados. Observe se há anomalias.
                            Leie o relatório REL_CONCILIACAO_INCR.xlsx para análise completa.</p>""")

                for n in RCP.columns.to_list():
                    if n[:2].upper() in ['VL','QT']:
                        RCP[n] = RCP[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    elif n[:2] == 'PC':
                        RCP[n] = RCP[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))

                colsf = st.columns([4,2,4], gap='small')
                with colsf[1]:
                    st.dataframe(RCP, width='stretch', hide_index=True)

        if existe_tabela('REL_RCP_BDGD_AIS_UC_INCR', bd):
            st.html("""
                        <p  style="text-align: justify;text-indent: 40px">Resumo dos principais
                        ativos da base georeferenciada, atual, comparada com a base
                        incremental, considerando apenas a UC. Observe se há anomalias.
                        Leie o relatório REL_CONCILIACAO_INCR.xlsx para análise completa.</p>
                        """)
            sSQL = """
                    SELECT * FROM 
                    REL_RCP_BDGD_AIS_UC_INCR t1

                    """
            RCP = pd.read_sql(sSQL, bd)

            for n in RCP.columns.to_list():
                if n[:2].upper() in ['QT', 'DI']:
                    RCP[n] = RCP[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2] == 'PC':
                    RCP[n] = RCP[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))

            colsh = st.columns([1,3,1], gap='small')
            with colsh[1]:
                st.dataframe(RCP, width='stretch', hide_index=True)
            RCP.to_csv(f'{local}\BDGD_ANLS\RCP_BDGD_UC.csv', sep="|", index=False)
        
        if existe_tabela("TBL_RESERVAS_CONCILIACAO", bd):
            sSQL = """
                    SELECT * FROM TBL_RESERVAS_CONCILIACAO

                    """
            RCP = pd.read_sql(sSQL, bd)
            if len(RCP)>0:
                st.html("""
                        <div>

                            <h2>
                                Análise dos Equipamentos de Reserva da BDGD
                            </h2>

                            <p  style="text-align: justify;text-indent: 40px">
                                Foi realizada a conciliação entre os itens registrados na <strong>BDGD</strong> 
                                e no <strong>AIS</strong>, considerando especificamente os equipamentos 
                                classificados como reserva. Nesse sentido, devem ser avaliadas as diferenças identificadas entre as bases, 
                                de forma a verificar a necessidade de ajustes, justificativas ou complementação 
                                das informações apresentadas.
                            </p>

                        </div>
                    """)
                for n in RCP.columns.to_list():
                    if n[:2].upper() in ['QT', 'DI']:
                        RCP[n] = RCP[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    elif n[:2] == 'PC':
                        RCP[n] = RCP[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))

                colsi = st.columns([1,3,1], gap='small')
                with colsi[1]:
                    st.dataframe(RCP, width='stretch', hide_index=True)

@st.fragment()
def _plotar_redes(bd_path, pct_anl=1, local="", empresa="", st=None):
    with sl.connect(bd_path) as bd_AT:
        if existe_tabela('SSDMT_AT', bd_AT):
            try:
                sSQL = """
                        SELECT ARE_LOC, COMP
                        FROM SSDMT_AT t1
                        WHERE t1.SITCONT = 'AT1' AND t1.POS = 'PD' AND t1.TI in (40,41)

                    """
                df_SMT = pd.read_sql(sSQL, bd_AT)
            except:
                sSQL = """
                    SELECT ARE_LOC, COMP
                    FROM SSDMT_AT t1
                    WHERE t1.SITCONTFAS = 'AT1' AND t1.POS = 'PD' AND t1.TI in (40,41)

                """
                df_SMT = pd.read_sql(sSQL, bd_AT)

            if len(df_SMT)>0:
                st.html(f"""<h2>
                            Análise do Vão Mínimo</h2>
                            <p  style="text-align: justify;text-indent: 40px">Aqui se faz a
                            análise do vão mínimo. Você deve selecionar se deseja região urbana
                            ou rural e depois variar o slider para encontrar o melhor valor.
                            Observe se há anomalias. Abaixo é apresentado os resultados, 
                            leie o relatório do AIS para análise completa.</p><br>
                            """)

                st.divider()
                colis1, colis2, colis3 = st.columns([0.2, 0.1, 0.7], gap='small')
                with colis1:
                    xAREA = st.toggle("Escolha entre rede urbana (UB, desligado) e rural (NU, ligado)")
                with colis3:
                    xMin = st.slider("Valor mínimo para rede (outlier)", min_value=0.0, max_value=10.0, value=.5)
                
                st.divider()
                x = vao_medio(f"{local}", empresa, xAREA, xMin, df_SMT, st, pct=pct_anl)


@st.fragment()
def _plotar_redes_sub(bd_path, pct_anl=1, local="", empresa="", st=None):
    with sl.connect(bd_path) as bd_AT:
        if existe_tabela('SSDMT_AT', bd_AT):
            try:
                sSQL = """
                        SELECT ARE_LOC, COMP
                        FROM SSDMT_AT t1
                        WHERE t1.SITCONT = 'AT1' AND t1.POS = 'PD' AND t1.TI in (42,43)

                    """
                df_SMT = pd.read_sql(sSQL, bd_AT)
            except:
                sSQL = """
                    SELECT ARE_LOC, COMP
                    FROM SSDMT_AT t1
                    WHERE t1.SITCONTFAS = 'AT1' AND t1.POS = 'PD' AND t1.TI in (42,43)

                """
                df_SMT = pd.read_sql(sSQL, bd_AT)

            if len(df_SMT)>0:
                st.html(f"""<h2>
                            Análise do Vão Mínimo</h2>
                            <p  style="text-align: justify;text-indent: 40px">Aqui se faz a
                            análise do vão mínimo para redes subterrâneas. Você deve selecionar se deseja região urbana
                            ou rural e depois variar o slider para encontrar o melhor valor.
                            Observe se há anomalias. Abaixo é apresentado os resultados, 
                            leie o relatório do AIS para análise completa.</p><br>
                            """)

                st.divider()
                colis1, colis2, colis3 = st.columns([0.2, 0.1, 0.7], gap='small')
                with colis1:
                    xAREA = st.toggle("Escolha entre rede urbana subterrânea (UB, desligado) e rural (NU, ligado)", key='sub000')
                with colis3:
                    xMin = st.slider("Valor mínimo para rede subterrânea (outlier)", min_value=0.0, max_value=10.0, value=.5, key='sub001')
                
                st.divider()
                x = vao_medio(f"{local}", empresa, xAREA, xMin, df_SMT, st, pct=pct_anl, nome="SUBTERRÂNEO")

@st.fragment()
def _plotar_ramais(bd_path, pct_anl=1, local="", empresa="", st=None):
    with sl.connect(bd_path) as bd_AT:
        if existe_tabela('RAMLIG_AT', bd_AT):
                try:
                    sSQL = """
                            SELECT ARE_LOC, COMP
                            FROM RAMLIG_AT t1
                            WHERE t1.SITCONT = 'AT1' AND t1.POS = 'PD'

                        """
                    df_RM = pd.read_sql(sSQL, bd_AT)
                except:
                    sSQL = """
                        SELECT ARE_LOC, COMP
                        FROM RAMLIG_AT t1
                        WHERE t1.SITCONTFAS = 'AT1' AND t1.POS = 'PD'

                    """
                    df_RM = pd.read_sql(sSQL, bd_AT)

                if len(df_RM)>0:
                    st.html(f"""<h2>
                                Análise do Vão Mínimo de Ramais</h2>
                                <p  style="text-align: justify;text-indent: 40px">Aqui se faz a
                                análise do vão mínimo de ramas. Você deve selecionar se deseja região urbana
                                ou rural e depois variar o slider para encontrar o melhor valor.
                                Observe se há anomalias. Abaixo é apresentado os resultados, 
                                leie o relatório do AIS para análise completa.</p><br>
                                """)

                    st.divider()
                    colis1a, colis2a, colis3a = st.columns([0.2, 0.1, 0.7], gap='small')
                    with colis1a:
                        xAREAa = st.toggle("Escolha entre ramal urbano (UB, desligado) e rural (NU, ligado)")
                    with colis3a:
                        xMina = st.slider("Valor mínimo para ramal (outlier)", min_value=0.0, max_value=10.0, value=.5)
                    
                    st.divider()
                    x1 = vao_medio(f"{local}", empresa, xAREAa, xMina, df_RM, st, nome="RAMAL", pct=pct_anl)

@st.fragment()
def _vis_005(dir = "", direto = "", bd_path ="", gdf = None, nm_emp = "", gdf_CONJ = None):
    if dir == "":
        return
    
    LST = ['AT','MT','BT']
    with sl.connect(bd_path) as bd:
        if not existe_tabela('tbl_resumo_ener_conj', bd):
            df_RES = pd.DataFrame()
            for tp in LST:
                if os.path.exists(f"{dir}/CONSOL/UC{tp}.shp"):
                    df_PR_ALTA = gpd.read_file(f"{dir}/CONSOL/UC{tp}.shp", engine='pyogrio', use_arrow  =True)
                    if not df_PR_ALTA.crs:
                        df_PR_ALTA = df_PR_ALTA.set_crs("EPSG:4674")
                    lst_var = [n for n in df_PR_ALTA.columns if n.upper().startswith(('ENE_'))]
                    df_PR = df_PR_ALTA.groupby(['CONJ'], dropna=False)[lst_var].sum().reset_index()
                    nmes = 1
                    if tp == 'AT':
                        colunas_a = [col for col in df_PR.columns if col.startswith("ENE_P")]
                        colunas_b = [col for col in df_PR.columns if col.startswith("ENE_F")]
                        colunas_a.sort()
                        colunas_b.sort()
                        
                        for a, b in zip(colunas_a, colunas_b):
                            df_PR[f"EN_{nmes}"] = df_PR[a] + df_PR[b]
                            nmes += 1
                        df_PR = df_PR.drop(columns=colunas_a + colunas_b)
                    else:
                        colunas_a = [col for col in df_PR.columns if col.startswith("ENE_")]
                        colunas_a.sort()
                        for a in colunas_a:
                            df_PR[f"EN_{nmes}"] = df_PR[a]
                            nmes += 1
                        df_PR = df_PR.drop(columns=colunas_a)
                    df_PR['TP'] = tp
                    if df_RES.empty:
                        df_RES = df_PR.copy()
                    else:
                        df_RES = pd.concat([df_RES,df_PR], ignore_index=True)
            df_RES = df_RES.fillna(0)
            df_RES.to_sql('tbl_resumo_ener_conj', bd, if_exists='replace', index=False)
        else:
            sSQL = """SELECT * FROM tbl_resumo_ener_conj"""
            df_RES = pd.read_sql(sSQL, bd)

    gdf_CONJplt = gdf_CONJ.merge(df_RES, how='left', left_on='COD_ID', right_on = 'CONJ')

    meses = {
                        "EN_1": "JAN",
                        "EN_2": "FEV",
                        "EN_3": "MAR",
                        "EN_4": "ABR",
                        "EN_5": "MAI",
                        "EN_6": "JUN",
                        "EN_7": "JUL",
                        "EN_8": "AGO",
                        "EN_9": "SET",
                        "EN_10": "OUT",
                        "EN_11": "NOV",
                        "EN_12": "DEZ",
                    }
    df_LONG = gdf_CONJplt[['TP', 'geometry','CONJ','EN_1','EN_2','EN_3','EN_4','EN_5',
                                        'EN_6','EN_8','EN_9','EN_10','EN_11','EN_12']].melt(
                    id_vars=["CONJ", "TP", 'geometry'],
                    var_name="mes",
                    value_name="valor"
                )
    df_LONG["mes"] = df_LONG["mes"].replace(meses)
    dfP = df_LONG.groupby(['geometry','CONJ','mes'], dropna=False)[['valor']].sum().reset_index()
    dfP['TP'] = 'TOTAL'
    df_LONG = pd.concat([df_LONG, dfP], ignore_index=True)
    a = f"{df_LONG['valor'].sum():,.2f}".replace(".","x").replace(",",".").replace("x",",")
    st.html(f"""
            <p  style="text-align: justify;text-indent: 40px">Por sua vez,
            a empresa informou as energias ativa medidas nos postos tarifários, por mês,
            para cada UC, no total de {a}kWh, para o ano. A seguir consolidamos por conjunto, podendo ser definido o nível e o 
            mês para visualização.</p><br>
            """)
    
    colAs = st.columns([0.45,0.1,0.45], gap='small')
    with colAs[0]:
        energia = st.selectbox(
                                    "Selecione a distribuição que desejas",
                                    LST + ['TOTAL'],
                                    index=1
                                )
    with colAs[2]:
        mes = st.selectbox(
                                "Selecione o mês",
                                ['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ'],
                                index=0
                            )
    
    if energia or mes:
        figENE, axENE = plt.subplots(figsize=(10, 8))
        divider = make_axes_locatable(axENE)
        cax = divider.append_axes("bottom", size="5%", pad=0.1)
        df_LONG[((df_LONG['mes'] == mes) if mes else True) & 
                ((df_LONG['TP'] == energia) if energia else True)].plot(
                    ax=axENE,
                    cax = cax,
                    column="valor",
                    cmap="BuGn",
                    edgecolor="black",
                    linewidth=0.5,
                    legend=True,
                    legend_kwds={"orientation": "horizontal"}
                )
        gdf_CONJ.plot(
                            ax=axENE,
                            color="none",    
                            edgecolor="lightgray", 
                            linewidth=0.5     
                        )

        axENE.set_title(f"Distribuição de energia de {energia}, em kWh, {mes}, referência laudo atual.", fontsize=12, fontweight="bold")
        axENE.set_axis_off()
        col1b, col2b, col3b = st.columns([1,2,1], gap="large")
        with col2b:
            st.pyplot(figENE)

@st.fragment()
def _vis_006(dir = "", direto = "", arq = "", gdf_CONJ = None):
    if dir == "":
        return    
    
    st.html(f"""
            <p  style="text-align: justify;text-indent: 40px">Há outros dados de entidades
            geográficas, que podemos observar a seguir.</p><br>
            """)
    
    cols = st.columns([0.1,0.8,0.1], gap='small')
    lst_var = [n for n in arq if not n.upper().startswith(('SS', 'UN'))]
    apagar = list(set(lst_var) & set(arq))
    for apg in apagar:
        arq.remove(apg)
    with cols[1]:
        acao = st.selectbox(
                                "Selecione a entidade geográfica para graficar",
                                arq,
                                index=0
                            )
    if acao:
        gdfa1 = gpd.read_file(f"{dir}/CONSOL/{acao}.shp", engine='pyogrio', use_arrow  =True)
        if not gdfa1.crs:
            gdfa1 = gdfa1.set_crs("EPSG:4674")
        fig3, ax3 = plt.subplots(figsize=(15, 6))
        
        gdf_CONJ.plot(
                        ax=ax3,
                        color="#8ecae6",
                        edgecolor="white",
                        linewidth=0.2
                    )
        if acao in ['SSDMT','SSDBT','UNSEMT', 'UNTRMT']:
            gdfa1 = gdfa1.to_crs('EPSG:3857')
            gdfa1["geometry"] = gdfa1["geometry"].simplify(tolerance=1000) 
            gdfa1 = gdfa1.to_crs(gdf_CONJ.crs)
        if acao[:2]=="SS":
            gdfa1.plot(ax=ax3,
                    color="black",
                    edgecolor="white",
                    linewidth=0.2)
        else:
            gdfa1.plot(ax=ax3,
                    color="#011216",
                    edgecolor="#2F7CA3",
                    markersize=1,
                    linewidth=0.02,
                    alpha=0.95)

        ax3.set_axis_off()
        col1d, col2d, col3d = st.columns([1,2,1], gap="large")
        with col2d:
            st.pyplot(fig3)
        imagem_path = f"{direto}\REPR_ATIVO_{acao}.png"
        fig3.savefig(imagem_path, dpi=300, bbox_inches='tight', transparent=True)

        st.divider()

def _vis_004(bd_path="", bd_BDGDAT_path="", bd_BDGDANT_path="", local="", st=None, empresa=""):
    st.session_state.page = "Análise Espacial de Ativos"
    if (bd_path=="") or (local==""):
        return
    
    with sl.connect(bd_BDGDAT_path) as bdAT:
        with sl.connect(bd_BDGDANT_path) as bdANT:
            if not existe_tabela('TARE_M10',bdAT):
                x = csv_to_local('tabelas/M10', bdAT, 'M10', st)
                if existe_tabela('EQTRS_ANT', bdANT):
                    x = csv_to_local('tabelas/DDA', bdANT, 'ANT', st)
                else:
                    x = csv_to_local('tabelas/M10', bdANT, 'ANT', st)
            st.write("Aqui")
            st.html(""" <h2>Avaliações geoespaciais complementares dos dados</h1>
                        <p  style="text-align: justify;text-indent: 40px">A análise geoespacial 
                        no controle contábil de ativos permite vincular informações financeiras 
                        à localização física, garantindo maior consistência no registro e na 
                        depreciação de bens. Essa abordagem auxilia na verificação de ativos 
                        empregados no laudo de avaliação, reduzindo discrepâncias e 
                        direcionando os trabalhos. Antes de iniciar, verificaremos alguns
                        arquivos.</p><br>
                        """)
            
            avl = st.info("Vamos avaliar os arquivos da BDGD.")
            for nm_dir in ['BDGD_ANT','BDGD_AT']:
                dir = f'{local}/{nm_dir}'
                files = os.listdir(dir)
                arq_dbf = [f for f in files if os.path.isfile(f'{dir}/{f}') and f[-3:] == 'dbf']
                arq_shp = [f[:-4] for f in files if os.path.isfile(f'{dir}/{f}') and f[-3:] == 'shp']
                arq = []
                for n in arq_dbf:
                    a = n.rfind("_") if n.rfind("_") > 0 else n.rfind(".")
                    if (n[:n.rfind(".")] in arq_shp) and (n[:a] not in arq):
                        arq += [n[:a]]
                for n in arq:
                    gdf = combina_arq_shp(dir, n, 'CONSOL')
                    avl.info(f"Feito arquivo {n}.")

            avl.info(f"Finalizada as análises.")
            st.divider()
            
            gdf = gpd.read_file(f"{dir}/CONSOL/ARAT.shp", engine='pyogrio', use_arrow  =True)
            if not gdf.crs:
                gdf = gdf.set_crs("EPSG:4674")
            gdf = gdf.to_crs("EPSG:4326")
            gdf_CONJ = gpd.read_file(f"{dir}/CONSOL/CONJ.shp", engine='pyogrio', use_arrow  =True)
            if not gdf_CONJ.crs:
                gdf_CONJ = gdf_CONJ.set_crs("EPSG:4674")
            gdf_CONJ = gdf_CONJ.to_crs(gdf.crs)

            gdf_CONJ_km2 = gdf_CONJ.to_crs("EPSG:31983")
            gdf_CONJ_km2["area_km2"] = gdf_CONJ_km2.area / 1e6
            
            a = f"{gdf_CONJ_km2['area_km2'].sum():,.2f}".replace(".","x").replace(",",".").replace("x",",")

            nm_emp = gdf.iloc[0,4] if gdf.iloc[0,4] != None else st.session_state.nm_empr
            st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                            Características Geográficas da {nm_emp}</h3>
                            """)
            st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">A {nm_emp}, com {a}km<sup>2</sup> de área total,
                    apresentou os seguintes conjuntos:</p><br>
                    """)
            
            fig, (ax_map, ax_legend) = plt.subplots(1, 2, figsize=(18, 10), gridspec_kw={'width_ratios': [3, 1]})

            gdf_CONJ.plot(
                            ax=ax_map,
                            column="NOME",
                            cmap="plasma",
                            edgecolor="white",
                            linewidth=0.5
                        )

            ax_map.set_title(f"Conjuntos da {nm_emp}", fontsize=14, fontweight="bold")
            ax_map.set_axis_off()

            ax_legend.set_title("Legenda", fontsize=12, fontweight="bold")

            unique_names = gdf_CONJ["NOME"].unique()
            num_colors = len(unique_names)

            cmap = plt.cm.get_cmap("plasma", num_colors)
            handles = [mpatches.Patch(color=cmap(i / num_colors), label=name) for i, name in enumerate(unique_names)]

            ax_legend.legend(handles=handles, loc="upper left", fontsize=10, ncol=3, frameon=False)
            ax_legend.set_xticks([])
            ax_legend.set_yticks([])
            ax_legend.set_frame_on(False)  

            plt.tight_layout()
            col1, col2, col3 = st.columns([1,2,1], gap="large")
            with col2:
                st.pyplot(fig)
            direto = f"{local}\IMAGENS"
            imagem_path = f"{direto}\REPR_CONJ.png"
            fig.savefig(imagem_path, dpi=300, bbox_inches='tight', transparent=True)
            
            if os.path.isfile(rf"{dir}/CONSOL/SUB.shp"):
                gdfa = gpd.read_file(rf"{dir}/CONSOL/SUB.shp", engine='pyogrio', use_arrow  =True)

                if not gdfa.empty and len(gdfa[gdfa['POS']=='PD'])>0:

                    st.html(f"""
                                <p  style="text-align: justify;text-indent: 40px">Por sua vez,
                                as SE de propriedade da distribuidora estão distribuidas conforme
                                apresentado a seguir.</p><br>
                            """)
                    fig2, ax2 = plt.subplots(figsize=(10, 8))
                    
                    if not gdfa.crs:
                        gdfa = gdfa.set_crs("EPSG:4674")
                    gdfa = gdfa.to_crs(gdf.crs)
                    gdfa['centroid'] = gdfa.geometry.centroid

                    main_bounds = gdf.total_bounds  
                    center_x, center_y = (main_bounds[0] + main_bounds[2]) / 2, (main_bounds[1] + main_bounds[3]) / 2
                    map_width = main_bounds[2] - main_bounds[0]  

                    gdfa['distance'] = gdfa['centroid'].distance(Point(center_x, center_y))
                    gdfa.sort_values(by='distance', ascending=False, inplace=True)
                    Prmun = gdfa.iloc[0]
                    if len(gdfa)>1:  
                        Scmun = gdfa.iloc[1] 
                    else:
                        Scmun = Prmun

                    gap = (Prmun['distance'] / Scmun['distance']) > 1.05

                    gdf.plot(
                                ax=ax2,
                                color="#8ecae6",
                                edgecolor="#023047",
                                linewidth=0.1
                            )
                    for idx, row in gdfa[gdfa['POS']=='PD'].iterrows():
                        ax2.text(
                            row['centroid'].x,
                            row['centroid'].y+0.05,
                            row['DESCR'],
                            fontsize=8,
                            ha='center',
                            va='center',
                            color="black",
                            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none")
                        )
                    gdfa[gdfa['POS']=='PD']['centroid'].plot(
                                    ax=ax2,
                                    color="red",
                                    markersize=40,
                                    label="SE"
                                )

                    ax2.set_title(f"Subestações da {nm_emp}", fontsize=12, fontweight="bold")
                    ax2.set_axis_off()

                    col1a, col2a, col3a = st.columns([1,2,1], gap="large")
                    with col2a:
                        st.pyplot(fig2)
                    imagem_path = f"{direto}\REPR_ATIVO_SE.png"
                    fig2.savefig(imagem_path, dpi=300, bbox_inches='tight', transparent=True)

            _vis_005(dir, direto, bd_path, gdf, nm_emp, gdf_CONJ)
            _vis_006(dir, direto, arq, gdf_CONJ)
            
            FLG_AT = False
            for nm_arq in os.listdir(rf"{dir}/"):
                if nm_arq.lower().endswith('.dbf'):
                    if nm_arq.split(".")[0] in ['SSDAT','UCAT','UGAT','UNTRAT','UNSEAT','UNREAT'] or nm_arq.split(".")[0][-2:] == 'AT':
                        FLG_AT = True
                        break

            if FLG_AT:
                st.html("""
                            <h2 style="text-align: center;font-size: 30px;">
                            Síntese de alterações de bases geográficas</h2>
                            <p style="text-align: justify; text-indent: 40px">
                                Neste momento, iremos nos concentrar no levantamento das mudanças 
                                relacionadas ao <strong>grupo de alta tensão</strong>, a fim de aprimorar 
                                as análises iniciais. O objetivo é identificar alterações 
                                entre dois arquivos databasefile que representam o mesmo conjunto de dados 
                                em períodos distintos (revisão atual versus a anterior), por meio da 
                                análise de dados. Para o caso de linhas empregaremos a geometria.
                            </p>
                            <p style="text-align: justify; text-indent: 40px">
                                Inicialmente, nas linhas, investigaremos as <strong>geometrias 
                                adicionadas</strong>. Em seguida, passaremos à análise das <strong>
                                geometrias removidas</strong>, das <strong>geometrias 
                                modificadas</strong>, incluindo o databasefile na análise,
                                e, por fim, identificaremos as <strong>geometrias 
                                coincidentes</strong>, incluindo databasefile. Este processo focará especificamente nas 
                                geometrias associadas a ativos, ou seja, tabelas que representam 
                                ativos modelados contabilmente. 
                            </p>
                            """)
                st.divider()
                st.html("""
                            <h3 style="text-align: left;font-size: 20px;">
                            a) Mutações no período para transformadores de força, TUC 570</h3>
                        """)
                
                lst_SE_NV = []
                lst_SE_VL = []
                gdf_at = pd.DataFrame()
                if os.path.exists(f"{local}/BDGD_AT/CONSOL/UNTRAT.shp"):
                    gdf_at = gpd.read_file(f"{local}/BDGD_AT/CONSOL/UNTRAT.shp", 
                                        engine='pyogrio', 
                                        use_arrow  = True,
                                        sql="""SELECT COD_ID, SUB,  TIP_UNID,
                                                ARE_LOC, POT_NOM, 'AT' AS GRU_TEN FROM "UNTRAT" 
                                                WHERE TIP_UNID IN ('41') AND  POS = 'PD'
                                                AND  SIT_ATIV = 'AT'""")
                    if not gdf_at.crs:
                        gdf_at = gdf_at.set_crs("EPSG:4674")
                    gdf_at.to_crs(gdf.crs)
                if os.path.exists(f"{local}/BDGD_AT/CONSOL/UNTRMT.shp"):
                    gdf_mt = gpd.read_file(
                                            rf"{local}/BDGD_AT/CONSOL/UNTRMT.shp",
                                            engine="pyogrio",
                                            use_arrow=True,
                                            sql="""
                                                SELECT COD_ID, SUB, TIP_UNID, ARE_LOC, POT_NOM, 'MT' AS GRU_TEN
                                                FROM UNTRMT
                                                WHERE TIP_UNID IN ('41','54')
                                                AND POS = 'PD'
                                                AND SIT_ATIV = 'AT'
                                            """
                                        )
                    
                    if not gdf_mt.crs:
                        gdf_mt = gdf_mt.set_crs("EPSG:4674")
                    gdf_mt.to_crs(gdf.crs)

                    if gdf_at.empty:
                        gdf_at = gdf_mt.copy()
                    else:
                        gdf_at = pd.concat([gdf_at, gdf_mt], ignore_index=True)

                    gdf_at = gdf_at.merge(gdfa[['NOME','DESCR','COD_ID']], how = 'left', left_on='SUB', right_on='COD_ID',
                                        suffixes=("","_SUB"))
                    
                    sSQL = ""
                    if existe_tabela('EQTRAT_AT', bdAT) and existe_tabela('EQTRMT_AT', bdAT):
                        sSQL = """
                                    WITH TRAFO_ALTA AS (
                                        SELECT 
                                            t1.COD_ID AS COD_ID_EQTRA,
                                            TIP_INST,
                                            UNI_TR_AT AS COD_ID,
                                            t2.DESCR AS CLAS_TEN,
                                            t3.DESCR AS POT_NOM,
                                            t4.DESCR AS LIG,
                                            t5.DESCR AS TEN_PRI,
                                            t6.DESCR AS TEN_SEC,
                                            t7.DESCR AS TEN_TER,
                                            ODI, 'AT' AS GRU_TEN
                                        FROM EQTRAT_AT t1
                                        LEFT JOIN TPOTAPRT_M10 t3 ON t1.POT_NOM = t3.COD_ID
                                        LEFT JOIN TCLATEN_M10 t2 ON t1.CLAS_TEN = t2.COD_ID
                                        LEFT JOIN TLIG_M10 t4 ON t1.LIG = t4.COD_ID
                                        LEFT JOIN TTEN_M10 t5 ON t5.COD_ID = t1.TEN_PRI
                                        LEFT JOIN TTEN_M10 t6 ON t6.COD_ID = t1.TEN_SEC
                                        LEFT JOIN TTEN_M10 t7 ON t7.COD_ID = t1.TEN_TER
                                        WHERE TIP_INST IN ('SE_AT', 'SE_MT') AND t1.TUC = 570 AND t1.SITCONT IN ('AT1', 'RT')
                                    ),

                                    TRAFO_MEDIA AS (
                                        SELECT 
                                            t1.COD_ID AS COD_ID_EQTRA,
                                            TIP_INST,
                                            UNI_TR_MT AS COD_ID,
                                            t2.DESCR AS CLAS_TEN,
                                            t3.DESCR AS POT_NOM,
                                            t4.DESCR AS LIG,
                                            t5.DESCR AS TEN_PRI,
                                            t6.DESCR AS TEN_SEC,
                                            t7.DESCR AS TEN_TER,
                                            ODI, 'MT' AS GRU_TEN
                                        FROM EQTRMT_AT t1
                                        LEFT JOIN TPOTAPRT_M10 t3 ON t1.POT_NOM = t3.COD_ID
                                        LEFT JOIN TCLATEN_M10 t2 ON t1.CLAS_TEN = t2.COD_ID
                                        LEFT JOIN TLIG_M10 t4 ON t1.LIG = t4.COD_ID
                                        LEFT JOIN TTEN_M10 t5 ON t5.COD_ID = t1.TEN_PRI
                                        LEFT JOIN TTEN_M10 t6 ON t6.COD_ID = t1.TEN_SEC
                                        LEFT JOIN TTEN_M10 t7 ON t7.COD_ID = t1.TEN_TER
                                        WHERE TIP_INST IN ('SE_AT', 'SE_MT') AND t1.TUC = 570 AND t1.SITCONT IN ('AT1', 'RT')
                                    )

                                    SELECT * FROM TRAFO_ALTA
                                    UNION ALL
                                    SELECT * FROM TRAFO_MEDIA;
                            """
                    elif existe_tabela('EQTRAT_AT', bdAT):
                        sSQL = """
                                    WITH TRAFO_ALTA AS (
                                        SELECT 
                                            t1.COD_ID AS COD_ID_EQTRA,
                                            TIP_INST,
                                            UNI_TR_AT AS COD_ID,
                                            t2.DESCR AS CLAS_TEN,
                                            t3.DESCR AS POT_NOM,
                                            t4.DESCR AS LIG,
                                            t5.DESCR AS TEN_PRI,
                                            t6.DESCR AS TEN_SEC,
                                            t7.DESCR AS TEN_TER,
                                            ODI, 'AT' AS GRU_TEN
                                        FROM EQTRAT_AT t1
                                        LEFT JOIN TPOTAPRT_M10 t3 ON t1.POT_NOM = t3.COD_ID
                                        LEFT JOIN TCLATEN_M10 t2 ON t1.CLAS_TEN = t2.COD_ID
                                        LEFT JOIN TLIG_M10 t4 ON t1.LIG = t4.COD_ID
                                        LEFT JOIN TTEN_M10 t5 ON t5.COD_ID = t1.TEN_PRI
                                        LEFT JOIN TTEN_M10 t6 ON t6.COD_ID = t1.TEN_SEC
                                        LEFT JOIN TTEN_M10 t7 ON t7.COD_ID = t1.TEN_TER
                                        WHERE TIP_INST IN ('SE_AT', 'SE_MT') AND t1.TUC = 570 AND t1.SITCONT IN ('AT1', 'RT')
                                    )

                                    SELECT * FROM TRAFO_ALTA;
                            """

                    elif existe_tabela('EQTRAT_MT', bdAT):
                        sSQL = """
                                    WITH TRAFO_MEDIA AS (
                                        SELECT 
                                            t1.COD_ID AS COD_ID_EQTRA,
                                            TIP_INST,
                                            UNI_TR_MT AS COD_ID,
                                            t2.DESCR AS CLAS_TEN,
                                            t3.DESCR AS POT_NOM,
                                            t4.DESCR AS LIG,
                                            t5.DESCR AS TEN_PRI,
                                            t6.DESCR AS TEN_SEC,
                                            t7.DESCR AS TEN_TER,
                                            ODI, 'MT' AS GRU_TEN
                                        FROM EQTRMT_AT t1
                                        LEFT JOIN TPOTAPRT_M10 t3 ON t1.POT_NOM = t3.COD_ID
                                        LEFT JOIN TCLATEN_M10 t2 ON t1.CLAS_TEN = t2.COD_ID
                                        LEFT JOIN TLIG_M10 t4 ON t1.LIG = t4.COD_ID
                                        LEFT JOIN TTEN_M10 t5 ON t5.COD_ID = t1.TEN_PRI
                                        LEFT JOIN TTEN_M10 t6 ON t6.COD_ID = t1.TEN_SEC
                                        LEFT JOIN TTEN_M10 t7 ON t7.COD_ID = t1.TEN_TER
                                        WHERE TIP_INST IN ('SE_AT', 'SE_MT') AND t1.TUC = 570 AND t1.SITCONT IN ('AT1', 'RT')
                                    )

                                    SELECT * FROM TRAFO_MEDIA;
                            """

                if sSQL != "":
                    df_EQTRAT_AT = pd.read_sql(sSQL, bdAT)
                                    
                    gdf_at = gdf_at.merge(df_EQTRAT_AT, how = 'outer', on=['COD_ID','GRU_TEN'],
                                    suffixes=("","_SUB"), indicator=True)
                    map = {
                                'both' : 'Tanto no arquivo EQ quanto UNTR',
                                'left_only' : 'Somente no arquivo UNTR',
                                'right_only' : 'Somente no arquivo EQ'
                            }
                    gdf_at['IND_CONC'] = gdf_at['_merge'].replace(map)
                    gdf_at = gdf_at.drop(columns='_merge')
                    lst_SE_NV = gdf_at['SUB'].drop_duplicates().to_list()

                if os.path.exists(f"{local}/BDGD_ANT/CONSOL/UNTRS.shp"):    
                    gdf_ant = gpd.read_file(f"{local}/BDGD_ANT/CONSOL/UNTRS.shp", 
                                            engine='pyogrio', 
                                            use_arrow  =True,
                                            sql="""SELECT COD_ID, SUB,  TIP_UNID, ARE_LOC,
                                                POT_NOM FROM "UNTRS" 
                                                WHERE TIP_UNID IN ('41') AND  POS = 'PD'
                                                AND  SIT_ATIV = 'AT'""")
                    if not gdf_ant.crs:
                        gdf_ant = gdf_ant.set_crs("EPSG:4674") 
                    if existe_tabela('EQTRS_ANT', bdANT):
                        sSQL = """
                            SELECT 
                                t1.COD_ID,
                                "SE_AT" AS TIP_INST,
                                t2.DESCR AS CLAS_TEN,
                                t3.DESCR AS POT_NOM,
                                t4.DESCR AS LIG, 
                                t5.DESCR AS TEN_PRI, 
                                t6.DESCR AS TEN_SEC, 
                                t7.DESCR AS TEN_TER,
                                t1.ODI
                            FROM EQTRS_ANT t1 LEFT JOIN TCLA_TEN_ANT t2 ON t1.CLAS_TEN=t2.COD_ID
                            LEFT JOIN TPOT_TRAN_ANT t3 ON t3.COD_ID=t1.POT_NOM
                            LEFT JOIN TLIG_ANT t4 ON t4.COD_ID=t1.LIG
                            LEFT JOIN TTEN_ANT t5 ON t5.COD_ID=t1.TEN_PRI
                            LEFT JOIN TTEN_ANT t6 ON t6.COD_ID=t1.TEN_SEC
                            LEFT JOIN TTEN_ANT t7 ON t7.COD_ID=t1.TEN_TER

                            """
                        df_EQTRS_ANT = pd.read_sql(sSQL, bdANT)
                        gdf_ant = gdf_ant.merge(df_EQTRS_ANT, how = 'left', on='COD_ID',
                                        suffixes=("","_SUB"))
                        lst_SE_VL = gdf_ant['SUB'].drop_duplicates().to_list()
                elif os.path.exists(f"{local}/BDGD_ANT/CONSOL/UNTRAT.shp"):
                    gdf_ant = gpd.read_file(f"{local}/BDGD_ANT/CONSOL/UNTRAT.shp", 
                                        engine='pyogrio', 
                                        use_arrow  = True,
                                        sql="""SELECT COD_ID, SUB,  TIP_UNID,
                                                ARE_LOC, POT_NOM, 'AT' AS GRU_TEN FROM "UNTRAT" 
                                                WHERE TIP_UNID IN ('41') AND  POS = 'PD'
                                                AND  SIT_ATIV = 'AT'""")
                    if not gdf_ant.crs:
                        gdf_ant = gdf_ant.set_crs("EPSG:4674")
                    gdf_ant.to_crs(gdf.crs)

                    gdf_mt_ant = gpd.read_file(
                                            rf"{local}/BDGD_ANT/CONSOL/UNTRMT.shp",
                                            engine="pyogrio",
                                            use_arrow=True,
                                            sql="""
                                                SELECT COD_ID, SUB, TIP_UNID, ARE_LOC, POT_NOM, 'MT' AS GRU_TEN
                                                FROM UNTRMT
                                                WHERE TIP_UNID IN ('41','54')
                                                AND POS = 'PD'
                                                AND SIT_ATIV = 'AT'
                                            """
                                        )
                    
                    if not gdf_mt_ant.crs:
                        gdf_mt_ant = gdf_mt_ant.set_crs("EPSG:4674")
                    gdf_mt_ant.to_crs(gdf.crs)
                    gdf_ant = pd.concat([gdf_ant, gdf_mt_ant], ignore_index=True)

                    gdf_ant = gdf_ant.merge(gdfa[['NOME','DESCR','COD_ID']], how = 'left', left_on='SUB', right_on='COD_ID',
                                        suffixes=("","_SUB"))
                    
                    if existe_tabela('EQTRAT_ANT', bdANT):
                        sSQL = """
                                    WITH TRAFO_ALTA AS (
                                        SELECT 
                                            t1.COD_ID AS COD_ID_EQTRA,
                                            TIP_INST,
                                            UNI_TR_AT AS COD_ID,
                                            t2.DESCR AS CLAS_TEN,
                                            t3.DESCR AS POT_NOM,
                                            t4.DESCR AS LIG,
                                            t5.DESCR AS TEN_PRI,
                                            t6.DESCR AS TEN_SEC,
                                            t7.DESCR AS TEN_TER,
                                            ODI, 'AT' AS GRU_TEN
                                        FROM EQTRAT_ANT t1
                                        LEFT JOIN TPOTAPRT_ANT t3 ON t1.POT_NOM = t3.COD_ID
                                        LEFT JOIN TCLATEN_ANT t2 ON t1.CLAS_TEN = t2.COD_ID
                                        LEFT JOIN TLIG_ANT t4 ON t1.LIG = t4.COD_ID
                                        LEFT JOIN TTEN_ANT t5 ON t5.COD_ID = t1.TEN_PRI
                                        LEFT JOIN TTEN_ANT t6 ON t6.COD_ID = t1.TEN_SEC
                                        LEFT JOIN TTEN_ANT t7 ON t7.COD_ID = t1.TEN_TER
                                        WHERE TIP_INST = 'SE_AT' AND t1.TUC = 570
                                    ),

                                    TRAFO_MEDIA AS (
                                        SELECT 
                                            t1.COD_ID AS COD_ID_EQTRA,
                                            TIP_INST,
                                            UNI_TR_MT AS COD_ID,
                                            t2.DESCR AS CLAS_TEN,
                                            t3.DESCR AS POT_NOM,
                                            t4.DESCR AS LIG,
                                            t5.DESCR AS TEN_PRI,
                                            t6.DESCR AS TEN_SEC,
                                            t7.DESCR AS TEN_TER,
                                            ODI, 'MT' AS GRU_TEN
                                        FROM EQTRMT_ANT t1
                                        LEFT JOIN TPOTAPRT_ANT t3 ON t1.POT_NOM = t3.COD_ID
                                        LEFT JOIN TCLATEN_ANT t2 ON t1.CLAS_TEN = t2.COD_ID
                                        LEFT JOIN TLIG_ANT t4 ON t1.LIG = t4.COD_ID
                                        LEFT JOIN TTEN_ANT t5 ON t5.COD_ID = t1.TEN_PRI
                                        LEFT JOIN TTEN_ANT t6 ON t6.COD_ID = t1.TEN_SEC
                                        LEFT JOIN TTEN_ANT t7 ON t7.COD_ID = t1.TEN_TER
                                        WHERE TIP_INST IN ('SE_AT','SE_MT') AND t1.TUC = 570
                                    )

                                    SELECT * FROM TRAFO_ALTA
                                    UNION ALL
                                    SELECT * FROM TRAFO_MEDIA;
                            """
                        df_EQTRAT_ANT = pd.read_sql(sSQL, bdANT)
                        
                        gdf_ant = gdf_ant.merge(df_EQTRAT_ANT, how = 'outer', on=['COD_ID','GRU_TEN'],
                                        suffixes=("","_SUB"), indicator=True)
                        map = {
                            'both' : 'Tanto no arquivo EQ quanto UNTR',
                            'left_only' : 'Somente no arquivo UNTR',
                            'right_only' : 'Somente no arquivo EQ'
                        }
                        gdf_ant['IND_CONC'] = gdf_ant['_merge'].replace(map)
                        gdf_ant = gdf_ant.drop(columns='_merge')
                        lst_SE_VL = gdf_ant['SUB'].drop_duplicates().to_list()

                with sl.connect(bd_path) as bd:
                    dt_ARQ = max_arq("AIS", bd, empresa)
                    if dt_ARQ:
                        sSQL = f"""
                            SELECT 
                                t1.Cd_ODI,
                                t1.txt_Desc_Bem AS TRAFO_AIS,
                                SUM(Qtd_AIS) AS Qtd_AIS
                            FROM AIS t1 WHERE t1.dt_ARQ = {dt_ARQ} AND t1.Cd_UAR <> 'UAR'
                            AND t1.Nr_TUC IN (570, 545, 540)
                            GROUP BY t1.Cd_ODI, t1.txt_Desc_Bem
                            """
                        df_OUTb = pd.read_sql(sSQL, bd)
                        df_OUTb['TRAFO_AIS'] = df_OUTb['Qtd_AIS'].astype(str).fillna("") + " UN, " + df_OUTb['TRAFO_AIS'].fillna("")
                        df_OUTb = df_OUTb.groupby(['Cd_ODI']).agg({
                                            'TRAFO_AIS': lambda x: ',<br> '.join(x)
                                        }).reset_index()
                    else:
                        df_OUTb = pd.DataFrame()

                df_OUT = pd.DataFrame()
                df_OUTa = pd.DataFrame()

                if len(lst_SE_NV)>0:
                    df_OUT = gdf_at.groupby(['ODI', 'SUB', 'NOME', 'TEN_PRI', 'TEN_SEC',
                                    'POT_NOM_SUB'], 
                                    dropna=False).size().reset_index(name='QTD_FIS_AT')
                    df_OUT['TRAFO_ATUAIS_BDGD'] = (df_OUT['QTD_FIS_AT'].astype(str).fillna('') + 
                                                " UN, " + df_OUT['TEN_PRI'].fillna('') + "/" +  
                                                df_OUT['TEN_SEC'].fillna('') + ", " +  
                                                df_OUT['POT_NOM_SUB'].fillna('')).str.strip(", ")
                    df_OUT.drop(columns=['TEN_PRI', 'TEN_SEC', 'POT_NOM_SUB'], inplace=True)

                    df_OUT = df_OUT.groupby(['ODI', 'SUB', 'NOME']).agg({
                                            'TRAFO_ATUAIS_BDGD': lambda x: ',<br> '.join(x)
                                        }).reset_index()

                if (len(lst_SE_VL)>0):
                    df_OUTa = gdf_ant.groupby(['ODI', 'SUB', 'TEN_PRI', 'TEN_SEC',
                                'POT_NOM_SUB'], 
                                dropna=False).size().reset_index(name='QTD_FIS_ANT')
                    df_OUTa['TRAFO_ANTERIORES_BDGD'] = (df_OUTa['QTD_FIS_ANT'].astype(str).fillna('') + 
                                                        " UN, " + df_OUTa['TEN_PRI'].fillna('') + "/" +  
                                                        df_OUTa['TEN_SEC'].fillna('') + ", " +  
                                                        df_OUTa['POT_NOM_SUB'].fillna('')).str.strip(', ')
                    df_OUTa.drop(columns=['TEN_PRI', 'TEN_SEC', 'POT_NOM_SUB'], inplace=True)
                    df_OUTa = df_OUTa.groupby(['ODI', 'SUB']).agg({
                                        'TRAFO_ANTERIORES_BDGD': lambda x: ',<br> '.join(x)
                                    }).reset_index()
            
            if FLG_AT and (not df_OUT.empty or not df_OUTa.empty):
                if df_OUT.empty and (not df_OUTa.empty):
                    df_OUT = df_OUTa.copy()
                if not df_OUTa.empty:
                    df_OUT = df_OUT.merge(df_OUTa, how='outer', on =['ODI', 'SUB'], 
                                        suffixes=('_AT','_ANT'), indicator=True)
                    df_OUT['RES_CONC_BDGD_AT_vs_ANT'] = (
                                                            df_OUT['_merge']
                                                            .astype('string')
                                                            .map({
                                                                'both': 'NO',
                                                                'left_only': 'APENAS BDGD ATUAL',
                                                                'right_only': 'APENAS BDGD ANTERIOR'
                                                            })
                                                            .astype('string')
                                                        )
                    df_OUT = df_OUT.drop(columns=['_merge'])
                    df_OUT = df_OUT.fillna("ND")
                
                if not df_OUTb.empty:
                    teste = df_OUT.merge(df_OUTb, how='inner', left_on ='ODI', right_on = 'Cd_ODI')
                    if len(teste) == 0:
                        df_OUT['Cd_ODI'] = df_OUT['ODI'].str.lstrip('0')
                    else:
                        df_OUT['Cd_ODI'] = df_OUT['ODI']
                    
                    df_OUTint = df_OUT[df_OUT['TRAFO_ATUAIS_BDGD'] != 'ND'].merge(df_OUTb, how='outer', on =['Cd_ODI'], 
                                        suffixes=('_BDGD','_AIS'), indicator=True)
                    df_OUTint['RES_CONC_BDGD_AT_vs_AIS'] = (
                                                            df_OUTint['_merge']
                                                            .astype('string')
                                                            .map({
                                                                'both': 'NO',
                                                                'left_only': 'APENAS BDGD ATUAL',
                                                                'right_only': 'APENAS AIS'
                                                            })
                                                            .astype('string')
                                                        )
                    df_OUTint = df_OUTint.drop(columns=['_merge'])
                    chave = ['ODI','SUB','NOME','TRAFO_ATUAIS_BDGD','TRAFO_ANTERIORES_BDGD','RES_CONC_BDGD_AT_vs_ANT']
                    df_OUT = df_OUT.merge(df_OUTint, how='left', on=chave, 
                                          indicator=True)
                    df_OUT['RES_CONC'] = (
                                            df_OUT['_merge']
                                            .astype('string')
                                            .map({
                                                'both': 'NO',
                                                'left_only': 'POSSÍVEL MUTAÇÃO ou BAIXA',
                                                'right_only': 'APENAS AIS'
                                            })
                                            .astype('string')
                                        )  
                    df_OUT = df_OUT.drop(columns=['_merge'])
                    df_OUT = df_OUT.fillna("ND")
                    df_OUT = df_OUT.drop(columns=['Cd_ODI_x']).rename(columns={'Cd_ODI_y' : 'Cd_ODI'})
                
                    crit01 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ANTERIOR') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'ND')         
                             )
                    crit02 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ATUAL') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'NO')         
                                )
                    crit03 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ATUAL') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'ND')         
                                )
                    crit04 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'ND') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'APENAS AIS')         
                                )
                    df_OUT['OBS_SFF'] = "NO"
                    df_OUT.loc[crit01, 'OBS_SFF'] = "Item baixado no período ou feito ajustes de codificação patrimonial"
                    df_OUT.loc[crit02, 'OBS_SFF'] = "Item adicionado no período ou feito ajustes de codificação patrimonial, com candidatos no AIS"
                    df_OUT.loc[crit03, 'OBS_SFF'] = "Item adicionado no período ou falta ajustes de codificação patrimonial, sem candidatos no AIS"
                    df_OUT.loc[crit04, 'OBS_SFF'] = "Sobra(s) contábil(eis), reserva(s) técnica(s) fria(s) não modelada(s) na BDGD, TI que não são de subestação ou outros"
                    
                st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Agora, faremos uma análise
                    por SE da empresa, conforme item 6.4, subitem 4, temos uma ODI para cada SE: 
                    <i>4 – cada subestação e todas as suas ampliações</i>. A tabela a seguir sumariza
                    por SE, os transformadores de força representados nas bases atual e anterior dos
                    dados georeferenciados, incluindo atributos. Também foi buscado os dados do arquivo
                    AIS, cuidado com a classificação UC e UAR, os erros ficam claros, abaixo.
                    As divergências, entre informações do geo, podem ter origens nos domínios 
                    empregados, DDA, para fazer a representação, verifique se há algum erro nos 
                    dados apresentados e certifique o correto. Isso também deve ser feito em relação
                    aos dados do AIS.</p><br>
                    """)

                with pd.ExcelWriter(f"{local}/BDGD_ANLS/TRAFO.xlsx", engine="openpyxl") as writer:
                    if len(df_OUT) > 0: df_OUT.to_excel(writer, sheet_name="CONCILIACAO_AIS_BDGD", index=False)
                    if len(gdf_ant) > 0: gdf_ant.to_excel(writer, sheet_name="CONCILIACAO_BDGD_EQ_UCTR_ANT", index=False)
                    if len(gdf_at) > 0: gdf_at.to_excel(writer, sheet_name="CONCILIACAO_BDGD_EQ_UCTR_AT", index=False)

                st.write(f"{df_OUT.to_html(escape=False, index=False)}".replace('style="text-align: right;"','style="text-align: center;"'), 
                        unsafe_allow_html=True)
                df_ODI = df_OUT[df_OUT['ODI'].notnull()][['SUB','ODI']].drop_duplicates(subset='SUB')

                df5 = df_OUT.head(5)
                with sl.connect(bd_path) as bd:
                    df5.to_sql('tbl_resumo_trafo_SE', bd, if_exists='replace', index=False)

            if FLG_AT:
                st.divider()
                st.html("""
                            <h3 style="text-align: left;font-size: 20px;">
                            b) Mutações no período para equipamento seccionadores</h3>
                        """)
                
                df_EQSE_AT = bsc_dd_SEC('EQSE_AT', bdAT, 'BDGD_AT', local)

                df_OUT = df_EQSE_AT[df_EQSE_AT['TIP_INST'].str.startswith("SE")].copy()
                df_OUT = df_OUT.sort_values(by=['SUB','ODI'])
                df_OUT = df_OUT.groupby(['ODI', 'SUB', 'CLAS_TEN',
                                        'MEI_ISO','COR_NOM', 'TIPO_UNIDADE'], 
                                        dropna=False).size().reset_index(name='QTD_FIS_AT')
                
                df_OUT['SECC_ATUAIS_BDGD'] = (df_OUT['QTD_FIS_AT'].astype(str).fillna('') + 
                                                " UN " + df_OUT['TIPO_UNIDADE'].fillna('') + ", " + 
                                                df_OUT['CLAS_TEN'].fillna('') + ", " +  
                                                df_OUT['COR_NOM'].fillna('') + ", " +  
                                                df_OUT['MEI_ISO'].fillna('')).str.strip(', ')
                df_OUT = df_OUT.drop(columns=['CLAS_TEN','MEI_ISO','COR_NOM','TIPO_UNIDADE'])
                df_OUT['SECC_ATUAIS_BDGD'] = df_OUT['SECC_ATUAIS_BDGD'].fillna("ND")
                df_OUT = df_OUT.groupby(['ODI', 'SUB']).agg({
                                        'SECC_ATUAIS_BDGD': lambda x: ',<br> '.join(x)
                                    }).reset_index()
                
                if existe_tabela('EQTRS_ANT', bdANT):
                    if existe_tabela('TUNI_ANT', bdANT):
                        sSQL = "SELECT * FROM TUNI_ANT"
                        TUNI_ANT = pd.read_sql(sSQL,bdANT)
                        LST_TUNI = f"""{(
                                    TUNI_ANT.loc[TUNI_ANT['UNIDADE'] == 'Unidade Seccionadora', 'COD_ID']
                                    .drop_duplicates()
                                    .astype(str)
                                    .tolist()
                                    )}"""[1:-1]

                    if existe_tabela('EQSE_ANT', bdANT):
                        sSQL = """
                            SELECT 
                                t1.COD_ID AS COD_ID_EQSE,
                                '' AS TIP_INST,
                                PAC_1,
                                PAC_2,
                                t2.DESCR AS CLAS_TEN,
                                ELO_FSV,
                                MEI_ISO,
                                t5.DESCR AS COR_NOM,
                                ODI
                            FROM EQSE_ANT t1
                            LEFT JOIN TCLA_TEN_ANT t2 ON t1.CLAS_TEN=t2.COD_ID LEFT JOIN TCOR_NOM_ANT t5 
                            ON t5.COD_ID=t1.COR_NOM
                            WHERE t1.CLAS_TEN IN (SELECT t3.COD_ID FROM TCLA_TEN_ANT t3 WHERE t3.TEN>68000)

                            """
                        df_EQSE_ANT = pd.read_sql(sSQL, bdANT)
                        
                    dic_cmp_sql = {
                                        'UNSEAT' : "PAC_1, PAC_2, COD_ID, SUB,  CONJ,  TIP_UNID, TLCD",
                                        'UNSEMT' : "PAC_1, PAC_2, COD_ID, SUB,  CONJ,  TIP_UNID, TLCD, CTMT, UNI_TR_S, ARE_LOC",
                                        'UNSEBT' : "PAC_1, PAC_2, COD_ID, SUB,  CONJ,  TIP_UNID, TLCD, CTMT, UNI_TR_S, UNI_TR_D, ARE_LOC",
                                    }
                    df_UNSE_ANT = pd.DataFrame()
                    for nm_tab in ['UNSEAT','UNSEMT','UNSEBT']:
                        if os.path.exists(f"{local}/BDGD_ANT/CONSOL/{nm_tab}.shp"):    
                            df_PR = gpd.read_file(f"{local}/BDGD_ANT/CONSOL/{nm_tab}.shp", 
                                                    engine='pyogrio', 
                                                    use_arrow  =True,
                                                    sql=f"""SELECT {dic_cmp_sql[nm_tab]} FROM "{nm_tab}" 
                                                        WHERE TIP_UNID IN ({LST_TUNI}) AND  POS = 'PD'
                                                        AND  SIT_ATIV = 'AT'""")         
                            if not df_PR.crs:
                                df_PR = df_PR.set_crs("EPSG:4674")
                            if df_UNSE_ANT.empty:
                                df_UNSE_ANT = df_PR.copy()
                            else:
                                df_UNSE_ANT = pd.concat([df_UNSE_ANT,df_PR], ignore_index=True)
                    df_UNSE_ANT = df_UNSE_ANT.fillna("ND")
                    df_UNSE_ANT = df_UNSE_ANT.merge(TUNI_ANT[['COD_ID','DESCR']], how='left', 
                                                    left_on = 'TIP_UNID', right_on = 'COD_ID',
                                                    suffixes = ('_UNSE','_TUNI'))
                    df_UNSE_ANT.drop(columns=['COD_ID_TUNI', 'TIP_UNID'])

                    df_EQSE_ANT = df_EQSE_ANT.merge(df_UNSE_ANT, how = 'left', on=['PAC_1', 'PAC_2'],
                                                suffixes=("_EQ","_GEO"))
                else:
                    df_EQSE_ANT = bsc_dd_SEC('EQSE_ANT', bdANT, 'BDGD_ANT', local)
                with sl.connect(bd_path) as bd:
                    dt_ARQ = max_arq("AIS", bd, empresa)
                    dt_ARQ1 = max_arq("DESC_ODI", bd, empresa)
                    if dt_ARQ:
                        sSQL = f"""
                            SELECT 
                                t1.txt_Desc_Bem AS DESCR_AIS,
                                SUM(Qtd_AIS) AS Qtd_AIS,
                                t1.Cd_ODI,
                                t2.Txt_DESC_ODI
                            FROM AIS t1 LEFT JOIN (SELECT Cd_ODI, Txt_DESC_ODI
                            FROM DESC_ODI WHERE dt_ARQ = {dt_ARQ1}) t2 ON t1.Cd_ODI=t2.Cd_ODI
                            WHERE (t1.dt_ARQ = {dt_ARQ}) AND (t1.Cd_UAR <> 'UAR')
                            AND (CAST(t1.Nr_TUC AS INTEGER) in (160,210,345)) AND
                            (CAST(t1.Nr_TI AS INTEGER) in (20,21,22,23,30,31,32,33,34,50,51,52,53,54,98))
                            GROUP BY t1.Cd_ODI, t1.txt_Desc_Bem
                            """
                        df_OUTb = pd.read_sql(sSQL, bd)
                        df_OUTb['DESCR_AIS'] = (df_OUTb['Qtd_AIS'].astype(str).fillna('') + 
                                                " UN, " + df_OUTb['DESCR_AIS'].fillna(''))
                        df_OUTb = df_OUTb.groupby(['Cd_ODI','Txt_DESC_ODI']).agg({
                                            'DESCR_AIS': lambda x: ',<br> '.join(x)
                                        }).reset_index()
                    else:
                        df_OUTb = pd.DataFrame()
                
                df_OUTa = df_EQSE_ANT.copy()  
                if not df_OUTa.empty:
                    df_OUTa.sort_values(by=['SUB','ODI'], inplace=True)
                    mapeamento = df_ODI.set_index('SUB')['ODI'].to_dict()
                    df_OUTa['ODI'] = df_OUTa['SUB'].map(mapeamento)
                    try:
                        df_OUTa = df_OUTa.groupby(['ODI', 'SUB', 'CLAS_TEN',
                                                'MEI_ISO','COR_NOM', 'DESCR'], 
                                                dropna=False).size().reset_index(name='QTD_FIS_ANT')
                    except:
                        df_OUTa = df_OUTa.groupby(['ODI', 'SUB', 'CLAS_TEN',
                                                'MEI_ISO','COR_NOM', 'TIPO_UNIDADE'], 
                                                dropna=False).size().reset_index(name='QTD_FIS_ANT')
                        df_OUTa.columns = ['ODI', 'SUB', 'CLAS_TEN',
                                                'MEI_ISO','COR_NOM', 'DESCR', 'QTD_FIS_ANT']

                    df_OUTa['SECC_ANTERIORES_BDGD'] = (df_OUTa['QTD_FIS_ANT'].astype(str).fillna('') + 
                                                    " UN " + df_OUTa['DESCR'].fillna('') + ", " + 
                                                    df_OUTa['CLAS_TEN'].fillna('') + ", " +  
                                                    df_OUTa['COR_NOM'].fillna('') + ", " +  
                                                    df_OUTa['MEI_ISO'].fillna('')).str.strip(', ')
                    df_OUTa.drop(columns=['CLAS_TEN','MEI_ISO','COR_NOM','DESCR'], inplace=True)
                    df_OUTa['SECC_ANTERIORES_BDGD'] = df_OUTa['SECC_ANTERIORES_BDGD'].fillna("ND")
                    df_OUTa = df_OUTa.groupby(['ODI', 'SUB']).agg({
                                            'SECC_ANTERIORES_BDGD': lambda x: ',<br> '.join(x)
                                        }).reset_index()

                    df_OUT = df_OUT.merge(df_OUTa, how='outer', on =['ODI', 'SUB'], 
                                            suffixes=('_ANT','_AT'), indicator=True)
                    df_OUT['RES_CONC_BDGD_AT_vs_ANT'] = (
                                                            df_OUT['_merge']
                                                            .astype('string')
                                                            .map({
                                                                'both': 'NO',
                                                                'left_only': 'APENAS BDGD ATUAL',
                                                                'right_only': 'APENAS BDGD ANTERIOR'
                                                            })
                                                            .astype('string')
                                                        )
                    df_OUT = df_OUT.drop(columns=['_merge'])
                    df_OUT = df_OUT.fillna("ND")
                else:
                    df_OUT['SECC_ANTERIORES_BDGD']=""

                if not df_OUTb.empty:
                    teste = df_OUT.merge(df_OUTb, how='inner', left_on ='ODI', right_on = 'Cd_ODI')
                    if len(teste) == 0:
                        df_OUT['Cd_ODI'] = df_OUT['ODI'].str.lstrip('0')
                    else:
                        df_OUT['Cd_ODI'] = df_OUT['ODI']

                    df_OUTint = df_OUT[df_OUT['SECC_ATUAIS_BDGD'] != 'ND'].merge(df_OUTb, how='outer', on =['Cd_ODI'], 
                                                            suffixes=('_BDGD','_AIS'), indicator=True)
                    df_OUTint['RES_CONC_BDGD_AT_vs_AIS'] = (
                                                            df_OUTint['_merge']
                                                            .astype('string')
                                                            .map({
                                                                'both': 'NO',
                                                                'left_only': 'APENAS BDGD ATUAL',
                                                                'right_only': 'APENAS AIS'
                                                            })
                                                            .astype('string')
                                                        )  
                    df_OUTint = df_OUTint.drop(columns=['_merge'])

                    chave = ['ODI','SUB','SECC_ATUAIS_BDGD','SECC_ANTERIORES_BDGD','RES_CONC_BDGD_AT_vs_ANT']
                    df_OUT = df_OUT.merge(df_OUTint, how='outer', on=chave, 
                                          indicator=True)
                    df_OUT['RES_CONC'] = (
                                            df_OUT['_merge']
                                            .astype('string')
                                            .map({
                                                'both': 'NO',
                                                'left_only': 'POSSÍVEL MUTAÇÃO ou BAIXA',
                                                'right_only': 'APENAS AIS'
                                            })
                                            .astype('string')
                                        )  
                    df_OUT = df_OUT.drop(columns=['_merge'])
                    df_OUT = df_OUT.fillna("ND")
                    df_OUT = df_OUT.drop(columns=['Cd_ODI_x']).rename(columns={'Cd_ODI_y' : 'Cd_ODI'})
                    crit01 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ANTERIOR') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'ND')         
                                )
                    crit02 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ATUAL') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'NO')         
                                )
                    crit03 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ATUAL') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'ND')         
                                )
                    crit04 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'ND') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'APENAS AIS')         
                                )
                    df_OUT['OBS_SFF'] = "NO"
                    df_OUT.loc[crit01, 'OBS_SFF'] = "Item baixado no período ou feito ajustes de codificação patrimonial"
                    df_OUT.loc[crit02, 'OBS_SFF'] = "Item adicionado no período ou feito ajustes de codificação patrimonial, com candidatos no AIS"
                    df_OUT.loc[crit03, 'OBS_SFF'] = "Item adicionado no período ou falta ajustes de codificação patrimonial, sem candidatos no AIS"
                    df_OUT.loc[crit04, 'OBS_SFF'] = "Sobra(s) contábil(eis), reserva(s) técnica(s) fria(s) não modelada(s) na BDGD, TI que não são de subestação ou outros"
                    df_OUT = df_OUT[['ODI', 'SUB', 'SECC_ATUAIS_BDGD', 'SECC_ANTERIORES_BDGD', 
                                     'RES_CONC_BDGD_AT_vs_ANT', 'DESCR_AIS', 'Cd_ODI', 
                                     'Txt_DESC_ODI', 'RES_CONC_BDGD_AT_vs_AIS', 
                                     'RES_CONC', 'OBS_SFF']]
                    contagem = df_OUT.groupby('ODI')['SUB'].transform("nunique")
                    mensagens = {
                                    2: "possível mudança de nome em relação a anterior ou avalie a SUB informada em UNSE",
                                    3: "avalie a SUB informada em UNSE"
                                }
                    cond_2 = contagem == 2
                    cond_maior_2 = contagem > 2
                    for cond, mensagem in [(cond_2, mensagens[2]),(cond_maior_2, mensagens[3])]:
                        separador = df_OUT.loc[cond, 'OBS_SFF'].apply(lambda x: " | " if x.strip() else "")
                        df_OUT.loc[cond, 'OBS_SFF'] = (df_OUT.loc[cond, 'OBS_SFF'] + separador + mensagem)

                    df_OUT = df_OUT[['ODI','SUB','SECC_ATUAIS_BDGD','SECC_ANTERIORES_BDGD',
                                    'RES_CONC_BDGD_AT_vs_ANT','DESCR_AIS',
                                    'RES_CONC_BDGD_AT_vs_AIS', 'RES_CONC', 'OBS_SFF',
                                    'Cd_ODI','Txt_DESC_ODI']]
                else:
                    df_OUT['DESCR_AIS'] = ''
                    df_OUT['Cd_ODI'] = ''
                    df_OUT['Txt_DESC_ODI'] = ''

                if not df_OUT.empty:
                    st.html(f"""
                        <p  style="text-align: justify;text-indent: 40px">Agora, faremos análise
                        dos equipamentos seccionadores nas SE. A tabela a seguir sumariza
                        por SE, os seccionadores representados nas bases atual e anterior dos
                        dados georeferenciados, incluindo atributos físicos. Também foi buscado os dados do arquivo
                        AIS, cuidado com a classificação UC e UAR, os erros ficam claros, abaixo.
                        As divergências, entre informações do geo, podem ter origens nos domínios 
                        empregados, DDA, para fazer a representação, verifique se há algum erro nos 
                        dados apresentados e certifique o correto. Isso também deve ser feito em relação
                        aos dados do AIS.</p>
                        <p  style="text-align: justify;text-indent: 40px">
                        O teste é realizado buscando os elementos da tabela EQSE, que estão em SE, feita conciliação com
                        os dados da UNSE, de AT ou MT, conforme GRU_TEN informado. Se houver conflito
                        entre SUB (sigla da SE) e ODI, haverá multiplicidade e a conciliação falha.
                        <p>
                        """)
                    df_OUT = df_OUT.sort_values(by=['ODI','SUB'])
                    df_OUT.to_excel(f"{local}/BDGD_ANLS/SECC.xlsx", index=False)
                    st.write(f"{df_OUT.to_html(escape=False, index=False)}".replace('style="text-align: right;"','style="text-align: center;"'), 
                                unsafe_allow_html=True)

                    st.divider()
                
                df_EQRE_AT = bsc_dd_REG('EQRE_AT', bdAT, 'BDGD_AT', local)
                df_OUT = df_EQRE_AT[df_EQRE_AT['TIP_INST'].str.startswith("SE")].copy()
                df_OUT.sort_values(by=['SUB','ODI'], inplace=True)
                df_OUT = df_OUT.groupby(['ODI', 'SUB', 'POT_NOM','REL_TC',
                                        'REL_TP','COR_NOM', 'TIPO_UNIDADE'], 
                                        dropna=False).size().reset_index(name='QTD_FIS_AT')
                df_OUT['REG_ATUAIS_BDGD'] = (df_OUT['QTD_FIS_AT'].astype(str).fillna('') + 
                                                " UN " + df_OUT['TIPO_UNIDADE'].fillna('') + ", " + 
                                                df_OUT['POT_NOM'].fillna('') + ", " +  
                                                df_OUT['COR_NOM'].fillna('') + ", " + 
                                                df_OUT['REL_TP'].fillna('') + ", " +  
                                                df_OUT['REL_TC'].fillna('')).str.strip(', ')
                df_OUT.drop(columns=['POT_NOM','REL_TC','REL_TP','COR_NOM','TIPO_UNIDADE'], inplace=True)
                df_OUT['REG_ATUAIS_BDGD'] = df_OUT['REG_ATUAIS_BDGD'].fillna("ND")
                df_OUT = df_OUT.groupby(['ODI', 'SUB']).agg({
                                        'REG_ATUAIS_BDGD': lambda x: ',<br> '.join(x)
                                    }).reset_index()
                
                if existe_tabela('EQTRS_ANT', bdANT):
                    if existe_tabela('TUNI_ANT', bdANT):
                        sSQL = "SELECT * FROM TUNI_ANT"
                        TUNI_ANT = pd.read_sql(sSQL,bdANT)
                        LST_TUNI = f"""{(
                                    TUNI_ANT.loc[TUNI_ANT['UNIDADE'] == 'Unidade Reguladora', 'COD_ID']
                                    .drop_duplicates()
                                    .astype(str)
                                    .tolist()
                                    )}"""[1:-1]

                    if existe_tabela('EQRE_ANT', bdANT):
                        sSQL = """
                            SELECT 
                                t1.COD_ID AS COD_ID_EQRE,
                                '' AS TIP_INST,
                                PAC_1,
                                PAC_2,
                                t2.DESCR AS POT_NOM,
                                t3.DESCR AS REL_TP,
                                t4.DESCR AS REL_TC,
                                t5.DESCR AS COR_NOM,
                                ODI
                            FROM EQRE_ANT t1
                            LEFT JOIN TPOT_TRAN_ANT t2 ON t1.POT_NOM=t2.COD_ID
                            LEFT JOIN TREL_TP_ANT t3 ON t1.REL_TP =t3.COD_ID
                            LEFT JOIN TREL_TC_ANT t4 ON t1.REL_TC =t4.COD_ID
                            LEFT JOIN TCOR_NOM_ANT t5 ON t5.COD_ID=t1.COR_NOM

                            """
                        df_EQRE_ANT = pd.read_sql(sSQL, bdANT)
                        
                    dic_cmp_sql = {
                        'UNREAT' : "PAC_1, PAC_2, COD_ID, SUB,  CONJ,  TIP_UNID, BANC",
                        'UNREMT' : "PAC_1, PAC_2, COD_ID, SUB,  CONJ,  TIP_UNID, BANC, CTMT, UNI_TR_S",
                    }
                    df_UNRE_ANT = pd.DataFrame()
                    for nm_tab in ['UNREAT','UNREMT']:
                        if os.path.exists(f"{local}/BDGD_ANT/CONSOL/{nm_tab}.shp"):    
                            df_PR = gpd.read_file(f"{local}/BDGD_ANT/CONSOL/{nm_tab}.shp", 
                                                    engine='pyogrio', 
                                                    use_arrow  =True,
                                                    sql=f"""SELECT {dic_cmp_sql[nm_tab]} FROM "{nm_tab}" 
                                                        WHERE TIP_UNID IN ({LST_TUNI}) AND  POS = 'PD'
                                                        AND  SIT_ATIV = 'AT'""")         
                            if not df_PR.crs:
                                df_PR = df_PR.set_crs("EPSG:4674")

                            if df_UNRE_ANT.empty:
                                df_UNRE_ANT = df_PR.copy()
                            else:
                                df_UNRE_ANT = pd.concat([df_UNRE_ANT,df_PR], ignore_index=True)
                    df_UNRE_ANT = df_UNRE_ANT.fillna("ND")
                    df_UNRE_ANT = df_UNRE_ANT.merge(TUNI_ANT[['COD_ID','DESCR']], how='left', 
                                                    left_on = 'TIP_UNID', right_on = 'COD_ID',
                                                    suffixes = ('_UNRE','_TUNI'))
                    df_UNRE_ANT.drop(columns=['COD_ID_TUNI', 'TIP_UNID'])

                    df_EQRE_ANT = df_EQRE_ANT.merge(df_UNRE_ANT, how = 'left', on=['PAC_1', 'PAC_2'],
                                                suffixes=("_EQ","_GEO"))
                else:
                    df_EQRE_ANT = bsc_dd_REG('EQRE_ANT', bdANT, 'BDGD_ANT', local)

                with sl.connect(bd_path) as bd:
                    dt_ARQ = max_arq("AIS", bd, empresa)
                    dt_ARQ1 = max_arq("DESC_ODI", bd, empresa)
                    if dt_ARQ:
                        
                        sSQL = f"""
                            SELECT 
                                t1.txt_Desc_Bem AS DESCR_AIS,
                                SUM(Qtd_AIS) AS Qtd_AIS,
                                t1.Cd_ODI,
                                t2.Txt_DESC_ODI
                            FROM AIS t1 LEFT JOIN (SELECT Cd_ODI, Txt_DESC_ODI
                            FROM DESC_ODI WHERE dt_ARQ = {dt_ARQ1}) t2 ON t1.Cd_ODI=t2.Cd_ODI
                            WHERE t1.dt_ARQ = {dt_ARQ} AND t1.Cd_UAR <> 'UAR'
                            AND t1.Nr_TUC in (340) AND
                            t1.Nr_TI in (20,21,22,23,30,31,32,33,34,50,51,52,53,54,98)
                            GROUP BY t1.Cd_ODI, t1.txt_Desc_Bem
                            """
                        df_OUTb = pd.read_sql(sSQL, bd)
                        
                        df_OUTb['DESCR_AIS'] = (df_OUTb['Qtd_AIS'].astype(str).fillna('') + 
                                                " UN, " + df_OUTb['DESCR_AIS'].fillna(''))
                        df_OUTb = df_OUTb.groupby(['Cd_ODI','Txt_DESC_ODI']).agg({
                                            'DESCR_AIS': lambda x: ',<br> '.join(x)
                                        }).reset_index()
                    else:
                        df_OUTb = pd.DataFrame()
                
                df_OUTa = df_EQRE_ANT[df_EQRE_ANT['CTMT']=='ND'].copy()
                df_OUTa.sort_values(by=['SUB','ODI'], inplace=True)
                mapeamento = df_ODI.set_index('SUB')['ODI'].to_dict()
                df_OUTa['ODI'] = df_OUTa['SUB'].map(mapeamento)
                try:
                    df_OUTa = df_OUTa.groupby(['ODI', 'SUB', 'POT_NOM','REL_TP','REL_TC',
                                            'COR_NOM', 'DESCR'], 
                                            dropna=False).size().reset_index(name='QTD_FIS_ANT')
                except:
                    df_OUTa = df_OUTa.groupby(['ODI', 'SUB', 'POT_NOM','REL_TP','REL_TC',
                                            'COR_NOM', 'TIPO_UNIDADE'], 
                                            dropna=False).size().reset_index(name='QTD_FIS_ANT')
                    df_OUTa.columns = ['ODI', 'SUB', 'POT_NOM','REL_TP','REL_TC',
                                            'COR_NOM', 'DESCR', 'QTD_FIS_ANT']
                df_OUTa['REG_ANTERIORES_BDGD'] = (df_OUTa['QTD_FIS_ANT'].astype(str).fillna('') + 
                                                " UN " + df_OUTa['DESCR'].fillna('') + ", " + 
                                                df_OUTa['POT_NOM'].fillna('') + ", " +  
                                                df_OUTa['COR_NOM'].fillna('') + ", " +  
                                                df_OUTa['REL_TP'].fillna('') + ", " +
                                                df_OUTa['REL_TC'].fillna('')).str.strip(', ')
                df_OUTa.drop(columns=['POT_NOM','REL_TP','REL_TC','COR_NOM','DESCR'], inplace=True)
                df_OUTa['REG_ANTERIORES_BDGD'] = df_OUTa['REG_ANTERIORES_BDGD'].fillna("ND")
                df_OUTa = df_OUTa.groupby(['ODI', 'SUB']).agg({
                                        'REG_ANTERIORES_BDGD': lambda x: ',<br> '.join(x)
                                    }).reset_index()
   
                if not df_OUTa.empty:
                    df_OUT = df_OUT.merge(df_OUTa, how='outer', on =['ODI', 'SUB'], 
                                            suffixes=('_ANT','_AT'), indicator=True)
                    df_OUT['RES_CONC_BDGD_AT_vs_ANT'] = (
                                                            df_OUT['_merge']
                                                            .astype('string')
                                                            .map({
                                                                'both': 'NO',
                                                                'left_only': 'APENAS BDGD ATUAL',
                                                                'right_only': 'APENAS BDGD ANTERIOR'
                                                            })
                                                            .astype('string')
                                                        )
                    df_OUT = df_OUT.drop(columns=['_merge'])
                    df_OUT = df_OUT.fillna("ND")
                else:
                    df_OUT['REG_ANTERIORES_BDGD'] = ''
                if not df_OUTb.empty:
                    teste = df_OUT.merge(df_OUTb, how='inner', left_on ='ODI', right_on = 'Cd_ODI')
                    if len(teste) == 0:
                        df_OUT['Cd_ODI'] = df_OUT['ODI'].str.lstrip('0')
                    else:
                        df_OUT['Cd_ODI'] = df_OUT['ODI']

                    df_OUTint = df_OUT[df_OUT['REG_ATUAIS_BDGD'] != 'ND'].merge(df_OUTb, how='outer', on =['Cd_ODI'], 
                                                                                suffixes=('_BDGD','_AIS'), indicator=True)
                    df_OUTint['RES_CONC_BDGD_AT_vs_AIS'] = (
                                                            df_OUTint['_merge']
                                                            .astype('string')
                                                            .map({
                                                                'both': 'NO',
                                                                'left_only': 'APENAS BDGD ATUAL',
                                                                'right_only': 'APENAS AIS'
                                                            })
                                                            .astype('string')
                                                        )  
                    df_OUTint = df_OUTint.drop(columns=['_merge'])

                    chave = ['ODI','SUB','REG_ATUAIS_BDGD','REG_ANTERIORES_BDGD','RES_CONC_BDGD_AT_vs_ANT']
                    df_OUT = df_OUT.merge(df_OUTint, how='outer', on=chave, 
                                            indicator=True)
                    df_OUT['RES_CONC'] = (
                                            df_OUT['_merge']
                                            .astype('string')
                                            .map({
                                                'both': 'NO',
                                                'left_only': 'POSSÍVEL MUTAÇÃO ou BAIXA',
                                                'right_only': 'APENAS AIS'
                                            })
                                            .astype('string')
                                        )  
                    df_OUT = df_OUT.drop(columns=['_merge'])
                    df_OUT = df_OUT.fillna("ND")
                    df_OUT = df_OUT.drop(columns=['Cd_ODI_x']).rename(columns={'Cd_ODI_y' : 'Cd_ODI'})
                    crit01 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ANTERIOR') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'ND')         
                                )
                    crit02 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ATUAL') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'NO')         
                                )
                    crit03 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ATUAL') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'ND')         
                                )
                    crit04 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'ND') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'APENAS AIS')         
                                )
                    df_OUT['OBS_SFF'] = "NO"
                    df_OUT.loc[crit01, 'OBS_SFF'] = "Item baixado no período ou feito ajustes de codificação patrimonial"
                    df_OUT.loc[crit02, 'OBS_SFF'] = "Item adicionado no período ou feito ajustes de codificação patrimonial, com candidatos no AIS"
                    df_OUT.loc[crit03, 'OBS_SFF'] = "Item adicionado no período ou falta ajustes de codificação patrimonial, sem candidatos no AIS"
                    df_OUT.loc[crit04, 'OBS_SFF'] = "Sobra(s) contábil(eis), reserva(s) técnica(s) fria(s) não modelada(s) na BDGD, TI que não são de subestação ou outros"
                    df_OUT = df_OUT[['ODI', 'SUB', 'REG_ATUAIS_BDGD', 'REG_ANTERIORES_BDGD', 
                                        'RES_CONC_BDGD_AT_vs_ANT', 'DESCR_AIS', 'Cd_ODI', 
                                        'Txt_DESC_ODI', 'RES_CONC_BDGD_AT_vs_AIS', 
                                        'RES_CONC', 'OBS_SFF']]
                    contagem = df_OUT.groupby('ODI')['SUB'].transform("nunique")
                    mensagens = {
                                    2: "possível mudança de nome em relação a anterior ou avalie a SUB informada em UNSE",
                                    3: "avalie a SUB informada em UNSE"
                                }
                    cond_2 = contagem == 2
                    cond_maior_2 = contagem > 2
                    for cond, mensagem in [(cond_2, mensagens[2]),(cond_maior_2, mensagens[3])]:
                        separador = df_OUT.loc[cond, 'OBS_SFF'].apply(lambda x: " | " if x.strip() else "")
                        df_OUT.loc[cond, 'OBS_SFF'] = (df_OUT.loc[cond, 'OBS_SFF'] + separador + mensagem)

                    df_OUT = df_OUT[['ODI','SUB','REG_ATUAIS_BDGD','REG_ANTERIORES_BDGD',
                                    'RES_CONC_BDGD_AT_vs_ANT','DESCR_AIS',
                                    'RES_CONC_BDGD_AT_vs_AIS', 'RES_CONC', 'OBS_SFF',
                                    'Cd_ODI','Txt_DESC_ODI']]

                else:
                    df_OUT['DESCR_AIS'] = ''
                    df_OUT['Cd_ODI'] = ''
                    df_OUT['Txt_DESC_ODI'] = ''

                if not df_OUT.empty:
                    st.html(f"""<h3 style="text-align: left;font-size: 20px;">
                            c) Mutações no período para equipamento regulador tensão</h3>
                            <p  style="text-align: justify;text-indent: 40px">Agora, faremos análise
                            dos equipamentos reguladores nas SE. A tabela a seguir sumariza
                            por SE, os reguladores representados nas bases atual e anterior dos
                            dados georeferenciados, incluindo atributos físicos. Também foi buscado os dados do arquivo
                            AIS, cuidado com a classificação UC e UAR, os erros ficam claros, abaixo.
                            As divergências, entre informações do geo, podem ter origens nos domínios 
                            empregados, DDA, para fazer a representação, verifique se há algum erro nos 
                            dados apresentados e certifique o correto. Isso também deve ser feito em relação
                            aos dados do AIS.</p><br>
                            """)
                    df_OUT.sort_values(by=['ODI','SUB'], inplace=True)
                    df_OUT.to_excel(f"{local}/BDGD_ANLS/REG.xlsx", index=False)
                    st.write(f"{df_OUT.to_html(escape=False, index=False)}".replace('style="text-align: right;"','style="text-align: center;"'), 
                                unsafe_allow_html=True)

                    st.divider()
                
                df_EQCR_AT = bsc_dd_CR('EQCR_AT', bdAT, 'BDGD_AT', local)
                df_OUT = df_EQCR_AT.copy().sort_values(by=['SUB','ODI'])
                df_OUT = df_OUT.groupby(['ODI', 'SUB', 'POT_NOM','TIPO_UNIDADE'], 
                                        dropna=False).size().reset_index(name='QTD_FIS_AT')
                df_OUT['CR_ATUAIS_BDGD'] = (df_OUT['QTD_FIS_AT'].astype(str).fillna('') + 
                                                " UN " + df_OUT['TIPO_UNIDADE'].fillna('') + ", " + 
                                                df_OUT['POT_NOM'].fillna('')).str.strip(', ')
                df_OUT.drop(columns=['POT_NOM','TIPO_UNIDADE'], inplace=True)
                df_OUT['CR_ATUAIS_BDGD'] = df_OUT['CR_ATUAIS_BDGD'].fillna("ND")
                df_OUT = df_OUT.groupby(['ODI', 'SUB']).agg({
                                        'CR_ATUAIS_BDGD': lambda x: ',<br> '.join(x)
                                    }).reset_index()

                if existe_tabela('EQTRS_ANT', bdANT):
                    if existe_tabela('TUNI_ANT', bdANT):
                        sSQL = "SELECT * FROM TUNI_ANT"
                        TUNI_ANT = pd.read_sql(sSQL,bdANT)
                        LST_TUNI = f"""{(
                                    TUNI_ANT.loc[TUNI_ANT['UNIDADE'] == 'Unidade Capacitora', 'COD_ID']
                                    .drop_duplicates()
                                    .astype(str)
                                    .tolist()
                                    )}"""[1:-1]
                    if existe_tabela('EQCR_ANT', bdANT):
                        sSQL = """
                            SELECT 
                                t1.COD_ID AS COD_ID_EQCR,
                                '' AS TIP_INST,
                                PAC_1,
                                PAC_2,
                                ODI
                            FROM EQCR_ANT t1

                            """
                        df_EQCR_ANT = pd.read_sql(sSQL, bdANT)
                        

                    dic_cmp_sql = {
                                        'UNCRAT' : "PAC_1, PAC_2, COD_ID, SUB,  CONJ, TIP_UNID, POT_NOM, BANC",
                                        'UNCRMT' : "PAC_1, PAC_2, COD_ID, SUB,  CONJ, TIP_UNID,  POT_NOM, BANC, CTMT, UNI_TR_S",
                                        'UNCRBT' : "PAC_1, PAC_2, COD_ID, SUB,  CONJ, TIP_UNID,  POT_NOM, BANC, CTMT, UNI_TR_S, UNI_TR_D",
                                    }
                    df_UNCR_ANT = pd.DataFrame()
                    for nm_tab in ['UNCRAT','UNCRMT','UNCRBT']:
                        if os.path.exists(f"{local}/BDGD_ANT/CONSOL/{nm_tab}.shp"):    
                            df_PR = gpd.read_file(f"{local}/BDGD_ANT/CONSOL/{nm_tab}.shp", 
                                                    engine='pyogrio', 
                                                    use_arrow  = True,
                                                    sql=f"""SELECT {dic_cmp_sql[nm_tab]} FROM "{nm_tab}" 
                                                        WHERE POS = 'PD'
                                                        AND  SIT_ATIV = 'AT'""")        
                            if not df_PR.crs:
                                df_PR = df_PR.set_crs("EPSG:4674")
                            if df_UNCR_ANT.empty:
                                df_UNCR_ANT = df_PR.copy()
                            else:
                                df_UNCR_ANT = pd.concat([df_UNCR_ANT, df_PR], ignore_index=True)

                    TPOTRTV_AT = pd.read_sql("SELECT * FROM TPOT_CAP_ANT", bdANT)
                    mapeamento = TPOTRTV_AT.set_index('COD_ID')['DESCR'].to_dict()
                    df_UNCR_ANT['POT_NOM'] = df_UNCR_ANT['COD_ID'].map(mapeamento)
                    df_UNCR_ANT = df_UNCR_ANT.fillna("ND")
                    df_UNCR_ANT = df_UNCR_ANT.merge(TUNI_ANT[['COD_ID','DESCR']], how='left', 
                                                    left_on = 'TIP_UNID', right_on = 'COD_ID',
                                                    suffixes = ('_UNCR','_TUNI'))
                    df_UNCR_ANT.drop(columns=['COD_ID_TUNI', 'TIP_UNID'])

                    df_EQCR_ANT = df_EQCR_ANT.merge(df_UNCR_ANT, how = 'left', on=['PAC_1', 'PAC_2'],
                                                suffixes=("_EQ","_GEO"))
                else:
                    df_EQCR_ANT = bsc_dd_CR('EQCR_ANT', bdANT, 'BDGD_ANT', local)

                with sl.connect(bd_path) as bd:
                    dt_ARQ = max_arq("AIS", bd, empresa)
                    dt_ARQ1 = max_arq("DESC_ODI", bd, empresa)
                    if dt_ARQ:
                        sSQL = f"""
                            SELECT 
                                t1.txt_Desc_Bem AS DESCR_AIS,
                                SUM(Qtd_AIS) AS Qtd_AIS,
                                t1.Cd_ODI,
                                t2.Txt_DESC_ODI
                            FROM AIS t1 LEFT JOIN (SELECT Cd_ODI, Txt_DESC_ODI
                            FROM DESC_ODI WHERE dt_ARQ = {dt_ARQ1}) t2 ON t1.Cd_ODI=t2.Cd_ODI
                            WHERE t1.dt_ARQ = {dt_ARQ} AND t1.Cd_UAR <> 'UAR'
                            AND t1.Nr_TUC in (125,130) AND
                            t1.Nr_TI in (20,21,22,23,30,31,32,33,34,50,51,52,53,54,98)
                            GROUP BY t1.Cd_ODI, t1.txt_Desc_Bem
                            """
                        df_OUTb = pd.read_sql(sSQL, bd)
                        df_OUTb['DESCR_AIS'] = (df_OUTb['Qtd_AIS'].astype(str).fillna('') + 
                                                " UN, " + df_OUTb['DESCR_AIS'].fillna(''))
                        df_OUTb = df_OUTb.groupby(['Cd_ODI','Txt_DESC_ODI']).agg({
                                            'DESCR_AIS': lambda x: ',<br> '.join(x)
                                        }).reset_index()
                    else:
                        df_OUTb = pd.DataFrame()
                
                df_OUTa = df_EQRE_ANT.copy()
                df_OUTa.sort_values(by=['SUB','ODI'], inplace=True)
                mapeamento = df_ODI.set_index('SUB')['ODI'].to_dict()
                df_OUTa['ODI'] = df_OUTa['SUB'].map(mapeamento)
                try:
                    df_OUTa = df_OUTa.groupby(['ODI', 'SUB', 'POT_NOM', 'DESCR'], 
                                            dropna=False).size().reset_index(name='QTD_FIS_ANT')
                except:
                    df_OUTa = df_OUTa.groupby(['ODI', 'SUB', 'POT_NOM', 'TIPO_UNIDADE'], 
                                            dropna=False).size().reset_index(name='QTD_FIS_ANT')
                    df_OUTa.columns = ['ODI', 'SUB', 'POT_NOM', 'DESCR', 'QTD_FIS_ANT']
                    
                df_OUTa['CR_ANTERIORES_BDGD'] = (df_OUTa['QTD_FIS_ANT'].astype(str).fillna('') + 
                                                " UN " + df_OUTa['DESCR'].fillna('') + ", " + 
                                                df_OUTa['POT_NOM'].fillna('')).str.strip(', ')
                df_OUTa.drop(columns=['POT_NOM','DESCR'], inplace=True)
                df_OUTa['CR_ANTERIORES_BDGD'] = df_OUTa['CR_ANTERIORES_BDGD'].fillna("ND")
                df_OUTa = df_OUTa.groupby(['ODI', 'SUB']).agg({
                                        'CR_ANTERIORES_BDGD': lambda x: ',<br> '.join(x)
                                    }).reset_index()

                if not df_OUTa.empty:
                    df_OUT = df_OUT.merge(df_OUTa, how='outer', on =['ODI', 'SUB'], 
                                            suffixes=('_ANT','_AT'), indicator=True)
                    df_OUT['RES_CONC_BDGD_AT_vs_ANT'] = (
                                                            df_OUT['_merge']
                                                            .astype('string')
                                                            .map({
                                                                'both': 'NO',
                                                                'left_only': 'APENAS BDGD ATUAL',
                                                                'right_only': 'APENAS BDGD ANTERIOR'
                                                            })
                                                            .astype('string')
                                                        )
                    df_OUT = df_OUT.drop(columns=['_merge'])
                    df_OUT = df_OUT.fillna("ND")
                else:
                    df_OUT['CR_ANTERIORES_BDGD'] = ''

                if not df_OUTb.empty:
                    teste = df_OUT.merge(df_OUTb, how='inner', left_on ='ODI', right_on = 'Cd_ODI')
                    if len(teste) == 0:
                        df_OUT['Cd_ODI'] = df_OUT['ODI'].astype(str).str.lstrip('0')
                    else:
                        df_OUT['Cd_ODI'] = df_OUT['ODI']

                    df_OUTint = df_OUT[df_OUT['CR_ATUAIS_BDGD'] != 'ND'].merge(df_OUTb, how='outer', on =['Cd_ODI'],                                                                                                     suffixes=('_BDGD','_AIS'), indicator=True)
                    df_OUTint['RES_CONC_BDGD_AT_vs_AIS'] = (
                                                            df_OUTint['_merge']
                                                            .astype('string')
                                                            .map({
                                                                'both': 'NO',
                                                                'left_only': 'APENAS BDGD ATUAL',
                                                                'right_only': 'APENAS AIS'
                                                            })
                                                            .astype('string')
                                                        )  
                    df_OUTint = df_OUTint.drop(columns=['_merge'])

                    chave = ['ODI','SUB','CR_ATUAIS_BDGD','CR_ANTERIORES_BDGD','RES_CONC_BDGD_AT_vs_ANT']
                    df_OUT = df_OUT.merge(df_OUTint, how='outer', on=chave, 
                                            indicator=True)
                    df_OUT['RES_CONC'] = (
                                            df_OUT['_merge']
                                            .astype('string')
                                            .map({
                                                'both': 'NO',
                                                'left_only': 'POSSÍVEL MUTAÇÃO ou BAIXA',
                                                'right_only': 'APENAS AIS'
                                            })
                                            .astype('string')
                                        )  
                    df_OUT = df_OUT.drop(columns=['_merge'])
                    df_OUT = df_OUT.fillna("ND")
                    df_OUT = df_OUT.drop(columns=['Cd_ODI_x']).rename(columns={'Cd_ODI_y' : 'Cd_ODI'})
                    crit01 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ANTERIOR') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'ND')         
                                )
                    crit02 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ATUAL') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'NO')         
                                )
                    crit03 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ATUAL') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'ND')         
                                )
                    crit04 = (
                                (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'ND') &
                                (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'APENAS AIS')         
                                )
                    df_OUT['OBS_SFF'] = "NO"
                    df_OUT.loc[crit01, 'OBS_SFF'] = "Item baixado no período ou feito ajustes de codificação patrimonial"
                    df_OUT.loc[crit02, 'OBS_SFF'] = "Item adicionado no período ou feito ajustes de codificação patrimonial, com candidatos no AIS"
                    df_OUT.loc[crit03, 'OBS_SFF'] = "Item adicionado no período ou falta ajustes de codificação patrimonial, sem candidatos no AIS"
                    df_OUT.loc[crit04, 'OBS_SFF'] = "Sobra(s) contábil(eis), reserva(s) técnica(s) fria(s) não modelada(s) na BDGD, TI que não são de subestação ou outros"
                    df_OUT = df_OUT[['ODI', 'SUB', 'CR_ATUAIS_BDGD', 'CR_ANTERIORES_BDGD', 
                                        'RES_CONC_BDGD_AT_vs_ANT', 'DESCR_AIS', 'Cd_ODI', 
                                        'Txt_DESC_ODI', 'RES_CONC_BDGD_AT_vs_AIS', 
                                        'RES_CONC', 'OBS_SFF']]
                    contagem = df_OUT.groupby('ODI')['SUB'].transform("nunique")
                    mensagens = {
                                    2: "possível mudança de nome em relação a anterior ou avalie a SUB informada em UNSE",
                                    3: "avalie a SUB informada em UNSE"
                                }
                    cond_2 = contagem == 2
                    cond_maior_2 = contagem > 2
                    for cond, mensagem in [(cond_2, mensagens[2]),(cond_maior_2, mensagens[3])]:
                        separador = df_OUT.loc[cond, 'OBS_SFF'].apply(lambda x: " | " if x.strip() else "")
                        df_OUT.loc[cond, 'OBS_SFF'] = (df_OUT.loc[cond, 'OBS_SFF'] + separador + mensagem)

                    df_OUT = df_OUT[['ODI','SUB','CR_ATUAIS_BDGD','CR_ANTERIORES_BDGD',
                                    'RES_CONC_BDGD_AT_vs_ANT','DESCR_AIS',
                                    'RES_CONC_BDGD_AT_vs_AIS', 'RES_CONC', 'OBS_SFF',
                                    'Cd_ODI','Txt_DESC_ODI']]

                else:
                    df_OUT['DESCR_AIS'] = ''
                    df_OUT['Cd_ODI'] = ''
                    df_OUT['Txt_DESC_ODI'] = ''
                if not df_OUT.empty:
                    st.html(f"""
                            <h3 style="text-align: left;font-size: 20px;">
                            d) Mutações no período para equipamento compensador de reativos de alta tensão</h3>
                            <p  style="text-align: justify;text-indent: 40px">Agora, faremos análise
                            dos equipamentos compensadores de reativos nas SE. A tabela a seguir sumariza
                            por SE, os compensadores representados nas bases atual e anterior dos
                            dados georeferenciados, incluindo atributos físicos. Também foi buscado os dados do arquivo
                            AIS, cuidado com a classificação UC e UAR, os erros ficam claros, abaixo.
                            As divergências, entre informações do geo, podem ter origens nos domínios 
                            empregados, DDA, para fazer a representação, verifique se há algum erro nos 
                            dados apresentados e certifique o correto. Isso também deve ser feito em relação
                            aos dados do AIS.</p><br>
                            """)
                    df_OUT.sort_values(by=['ODI','SUB'], inplace=True)
                    df_OUT.to_excel(f"{local}/BDGD_ANLS/REAT.xlsx", index=False)
                    st.write(f"{df_OUT.to_html(escape=False, index=False)}".replace('style="text-align: right;"','style="text-align: center;"'), 
                                unsafe_allow_html=True)
                    
                    st.divider()

                if (os.path.exists(f"{local}/BDGD_AT/CONSOL/SSDAT.shp") or
                os.path.exists(f"{local}/BDGD_ANT/CONSOL/SSDAT.shp")):
                    st.html("""
                                <h3 style="text-align: left;font-size: 20px;">
                                e) Mutações no período para linhas de distribuição de alta tensão</h3>
                            <p  style="text-align: justify;text-indent: 40px">Para essa situação é interessante
                            observarmos a mutação espacial, nos termos já abordados. O primeiro gráfico relevante
                            são das geometrias removidas (vermelho), após as adicionadas (amarelo), e por fim 
                            as inalteradas (preto). Um problema que pode ocorrer é a divergência de coordenadas
                            nas geometrias declaradas, mesmo com tolerância, que impede de fazer a análise de mutação geométrica.</p><br>
                            """)
                    
                    if os.path.exists(f"{local}/BDGD_AT/CONSOL/SSDAT.shp"):    
                        gdf_LD_AT = gpd.read_file(f"{local}/BDGD_AT/CONSOL/SSDAT.shp", 
                                                engine='pyogrio', 
                                                use_arrow  = True,
                                                sql=f"""SELECT * FROM "SSDAT" 
                                                    WHERE POS = 'PD'
                                                    AND  SITCONT IN ('AT1','SF')""")
                        if not gdf_LD_AT.crs:
                            gdf_LD_AT = gdf_LD_AT.set_crs("EPSG:4674")
                        gdf_LD_AT.to_crs(gdf.crs)

                    if (os.path.exists(f"{local}/BDGD_ANT/CONSOL/SSDAT.shp") and 
                    os.path.exists(f"{local}/BDGD_ANT/CONSOL/UNTRS.shp")):    
                        gdf_LD_ANT = gpd.read_file(f"{local}/BDGD_ANT/CONSOL/SSDAT.shp", 
                                                engine='pyogrio', 
                                                use_arrow  = True,
                                                sql=f"""SELECT * FROM "SSDAT" 
                                                    WHERE POS = 'PD'
                                                    AND  SITCONTFAS IN ('AT1','SF')""")
                        if not gdf_LD_ANT.crs:
                            gdf_LD_ANT = gdf_LD_ANT.set_crs("EPSG:4674")
                        gdf_LD_ANT.to_crs(gdf.crs)
                    elif os.path.exists(f"{local}/BDGD_ANT/CONSOL/SSDAT.shp"):    
                        gdf_LD_ANT = gpd.read_file(f"{local}/BDGD_ANT/CONSOL/SSDAT.shp", 
                                                engine='pyogrio', 
                                                use_arrow  = True,
                                                sql=f"""SELECT * FROM "SSDAT" 
                                                    WHERE POS = 'PD'
                                                    AND  SITCONT IN ('AT1','SF')""")
                        if not gdf_LD_ANT.crs:
                            gdf_LD_ANT = gdf_LD_ANT.set_crs("EPSG:4674")
                        gdf_LD_ANT.to_crs(gdf.crs)
                        
                    for gdf, prefix in [(gdf_LD_ANT, 'CTR_ANT'), (gdf_LD_AT, 'CTR_AT')]:
                        gdf[f'{prefix}_x'] = gdf['geometry'].centroid.x
                        gdf[f'{prefix}_y'] = gdf['geometry'].centroid.y


                    df_E1 = gdf_LD_ANT[['COD_ID', 'CTR_ANT_x', 'CTR_ANT_y']].rename(columns={'COD_ID': 'COD_ID_ANT'})
                    df_E2 = gdf_LD_AT[['COD_ID', 'CTR_AT_x', 'CTR_AT_y']].rename(columns={'COD_ID': 'COD_ID_AT'})

        
                    tolerancia = 0.05

                    coords1 = df_E1[['CTR_ANT_x', 'CTR_ANT_y']].values
                    coords2 = df_E2[['CTR_AT_x', 'CTR_AT_y']].values
                    tree = cKDTree(coords2)

                    distancias, indices = tree.query(coords1, k=1)

                    df_E1['correspondencia'] = [
                        df_E2.iloc[indices[i]]['COD_ID_AT'] if distancias[i] <= tolerancia else None
                        for i in range(len(distancias))
                    ]

                    df_E1 = df_E1.merge(df_E2, how='outer', left_on='correspondencia', right_on='COD_ID_AT')

                    LST_BXS = (
                        df_E1[df_E1['correspondencia'].isnull() & df_E1['CTR_AT_x'].isnull()]['COD_ID_ANT']
                        .drop_duplicates()
                        .to_list()
                    )
                    LST_INC = (
                        df_E1[df_E1['correspondencia'].isnull() & df_E1['CTR_ANT_x'].isnull()]['COD_ID_AT']
                        .drop_duplicates()
                        .to_list()
                    )

                    fig4, ax4 = plt.subplots(figsize=(15, 10))
                    gdf_CONJ.plot(
                        ax=ax4,
                        color="#8ecae6",
                        edgecolor="white",
                        linewidth=0.2
                    )
                    
                    gdf_LD_AT.plot(
                        ax=ax4,
                        color="black",
                        edgecolor="black",
                        linewidth=1
                    )
                    if len(LST_BXS)>0:
                        gdf_LD_ANT[gdf_LD_ANT['COD_ID'].isin(LST_BXS)].plot(
                            ax=ax4,
                            color="red",
                            edgecolor="red",
                            linewidth=1
                        )

                    if len(LST_INC)>0:
                        gdf_plot = gdf_LD_AT[gdf_LD_AT['COD_ID'].isin(LST_INC)]
                        if not gdf_plot.empty and gdf_plot.geometry.notnull().all():
                            gdf_plot.plot(ax=ax4, color="yellow", edgecolor="yellow", linewidth=1)
                        else:
                            st.error("GeoDataFrame vazio ou com geometrias inválidas")           
                    ax4.set_axis_off()

                    plt.title("Identificação das mutações de geometrias", 
                            fontsize=22, fontweight="bold")
                    plt.tight_layout()
                    imagem_path = f"{direto}\LD_MUTACAO.png"
                    fig4.savefig(imagem_path, dpi=300, bbox_inches='tight', transparent=True)

                    col1e, col2e, col3e = st.columns([1,5,1], gap = "large")
                    with col2e:
                        st.pyplot(fig4)

                    if existe_tabela('SEGCON_ANT', bdANT):
                        if os.path.exists(f"{local}/BDGD_ANT/CONSOL/UNTRS.shp"):
                            sSQL = """
                                SELECT 
                                    t1.COD_ID AS TIP_CND,
                                    'LD_AT' AS TIP_INST,
                                    (SELECT t2.DESCR FROM TCABO_GEOM_ANT t2 WHERE t1.GEOM_CAB=t2.COD_ID) AS GEOM_CAB,
                                    (SELECT t3.DESCR FROM TCABO_FOR_ANT t3 WHERE t1.FORM_CAB=t3.COD_ID) AS FORM_CAB,
                                    (SELECT t4.DESCR FROM TCABO_MAT_ANT t4 WHERE t1.MAT_FAS_1=t4.COD_ID) AS MAT_FAS_1,
                                    (SELECT t4.DESCR FROM TCABO_MAT_ANT t4 WHERE t1.MAT_FAS_2=t4.COD_ID) AS MAT_FAS_2,
                                    (SELECT t4.DESCR FROM TCABO_MAT_ANT t4 WHERE t1.MAT_FAS_3=t4.COD_ID) AS MAT_FAS_3,
                                    (SELECT t4.DESCR FROM TCABO_MAT_ANT t4 WHERE t1.MAT_NEU=t4.COD_ID) AS MAT_NEU,
                                    (SELECT t6.DESCR FROM TCABO_ISO_ANT t6 WHERE t1.ISO_FAS_1=t6.COD_ID) AS ISO_FAS_1,
                                    (SELECT t6.DESCR FROM TCABO_ISO_ANT t6 WHERE t1.ISO_FAS_2=t6.COD_ID) AS ISO_FAS_2,
                                    (SELECT t6.DESCR FROM TCABO_ISO_ANT t6 WHERE t1.ISO_FAS_3=t6.COD_ID) AS ISO_FAS_3,
                                    (SELECT t6.DESCR FROM TCABO_ISO_ANT t6 WHERE t1.ISO_NEU=t6.COD_ID) AS ISO_NEU,
                                    t1.CND_FAS,
                                    t1.FTRCNV,
                                    (SELECT t7.DESCR FROM TCABO_BIT_ANT t7 WHERE t1.BIT_FAS_1=t7.COD_ID) AS BIT_FAS_1,
                                    (SELECT t7.DESCR FROM TCABO_BIT_ANT t7 WHERE t1.BIT_FAS_2=t7.COD_ID) AS BIT_FAS_2,
                                    (SELECT t7.DESCR FROM TCABO_BIT_ANT t7 WHERE t1.BIT_FAS_3=t7.COD_ID) AS BIT_FAS_3,
                                    (SELECT t7.DESCR FROM TCABO_BIT_ANT t7 WHERE t1.BIT_NEU=t7.COD_ID) AS BIT_NEU
                                FROM SEGCON_ANT t1

                                """
                            df_LD_AT_ANT = pd.read_sql(sSQL, bdANT)
                            gdf_LD_ANT = gdf_LD_ANT.merge(df_LD_AT_ANT, how='left', on='TIP_CND')
                            try:
                                gdf_LD_ANT.loc[gdf_LD_ANT['FORM_CAB'] =='Singelo', "Qtd_kg"] = (
                                        gdf_LD_ANT['CND_FAS'] /  gdf_LD_ANT['FTRCNV'] * gdf_LD_ANT['COMP_GIS']
                                        * (gdf_LD_ANT['BIT_FAS_1'].apply(lambda x: 0 if pd.isna(x) else 1) +
                                        gdf_LD_ANT['BIT_FAS_2'].apply(lambda x: 0 if pd.isna(x) else 1) +
                                        gdf_LD_ANT['BIT_FAS_3'].apply(lambda x: 0 if pd.isna(x) else 1) +
                                        gdf_LD_ANT['BIT_NEU'].apply(lambda x: 0 if pd.isna(x) else 1))
                                )
                            except:
                                gdf_LD_ANT.loc[gdf_LD_ANT['FORM_CAB'] =='Singelo', "Qtd_kg"] = (
                                        gdf_LD_ANT['CND_FAS'] /  gdf_LD_ANT['FTRCNV'] * gdf_LD_ANT['COMP']
                                        * (gdf_LD_ANT['BIT_FAS_1'].apply(lambda x: 0 if pd.isna(x) else 1) +
                                        gdf_LD_ANT['BIT_FAS_2'].apply(lambda x: 0 if pd.isna(x) else 1) +
                                        gdf_LD_ANT['BIT_FAS_3'].apply(lambda x: 0 if pd.isna(x) else 1) +
                                        gdf_LD_ANT['BIT_NEU'].apply(lambda x: 0 if pd.isna(x) else 1))
                                )
                        else:
                            gdf_LD_ANT = segcon_AT('SEGCON_ANT', bdANT, gdf_LD_ANT, 'COMP', 'ANT')
                        df_OUTa = gdf_LD_ANT.copy()

                        try:
                            df_OUTa.sort_values(by=['ODI_FAS'], inplace=True)
                            df_OUTa = df_OUTa.rename(columns={'ODI_FAS': 'ODI'})
                        except:
                            df_OUTa.sort_values(by=['ODI'], inplace=True)

                        df_OUTa = df_OUTa.groupby(
                                        ['ODI', 'MAT_FAS_1', 'ISO_FAS_1', 'BIT_FAS_1'],
                                        dropna=False
                                    )['Qtd_kg'].sum().reset_index()

                        df_OUTa.rename(columns={"Qtd_kg": "QTD_FIS_ANT"}, inplace=True)
                        df_OUTa['QTD_FIS_ANT'] = df_OUTa['QTD_FIS_ANT'].apply(
                            lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                            if pd.notna(x) else ''
                        )
                        df_OUTa['CABO_ANTERIORES_BDGD'] = (df_OUTa['QTD_FIS_ANT'].astype(str).fillna('') + 
                                                        " kg, " + df_OUTa['MAT_FAS_1'].fillna('') + ", " + 
                                                        df_OUTa['BIT_FAS_1'].fillna('') + ", " + 
                                                        df_OUTa['ISO_FAS_1'].fillna('')).str.strip(', ')
                        df_OUTa.drop(columns=['MAT_FAS_1', 'ISO_FAS_1','BIT_FAS_1'], inplace=True)
                        df_OUTa['CABO_ANTERIORES_BDGD'] = df_OUTa['CABO_ANTERIORES_BDGD'].fillna("ND")
                        df_OUTa = df_OUTa.groupby(['ODI']).agg({
                                                'CABO_ANTERIORES_BDGD': lambda x: ',<br> '.join(x)
                                            }).reset_index()
                        
                    if existe_tabela('SEGCON_AT', bdAT):
                        gdf_LD_AT = segcon_AT('SEGCON_AT', bdAT, gdf_LD_AT,'COMP','M10')
                        df_OUT = gdf_LD_AT.copy()
                        df_OUT.sort_values(by=['ODI'], inplace=True)
                        df_OUT = df_OUT.groupby(
                                        ['ODI', 'MAT_FAS_1', 'ISO_FAS_1', 'BIT_FAS_1'],
                                        dropna=False
                                    )['Qtd_kg'].sum().reset_index()

                        df_OUT.rename(columns={"Qtd_kg": "QTD_FIS_AT"}, inplace=True)
                        df_OUT['QTD_FIS_AT'] = df_OUT['QTD_FIS_AT'].apply(
                            lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                            if pd.notna(x) else ''
                        )
                        df_OUT['CABO_ATUAIS_BDGD'] = (df_OUT['QTD_FIS_AT'].astype(str).fillna('') + 
                                                        " kg, " + df_OUT['MAT_FAS_1'].fillna('') + ", " + 
                                                        df_OUT['BIT_FAS_1'].fillna('') + ", " + 
                                                        df_OUT['ISO_FAS_1'].fillna('')).str.strip(', ')
                        df_OUT.drop(columns=['MAT_FAS_1', 'ISO_FAS_1','BIT_FAS_1'], inplace=True)
                        df_OUT['CABO_ATUAIS_BDGD'] = df_OUT['CABO_ATUAIS_BDGD'].fillna("ND")
                        df_OUT = df_OUT.groupby(['ODI']).agg({
                                                'CABO_ATUAIS_BDGD': lambda x: ',<br> '.join(x)
                                            }).reset_index()
                    with sl.connect(bd_path) as bd:
                        dt_ARQ = max_arq("AIS", bd, empresa)
                        dt_ARQ1 = max_arq("DESC_ODI", bd, empresa)
                        if dt_ARQ:
                            sSQL = f"""
                                SELECT 
                                    t1.txt_Desc_Bem AS DESCR_AIS,
                                    SUM(Qtd_AIS) AS Qtd_AIS,
                                    t1.Cd_ODI,
                                    t2.Txt_DESC_ODI
                                FROM AIS t1 LEFT JOIN (SELECT Cd_ODI, Txt_DESC_ODI
                                FROM DESC_ODI WHERE dt_ARQ = {dt_ARQ1}) t2 ON t1.Cd_ODI=t2.Cd_ODI
                                WHERE t1.dt_ARQ = {dt_ARQ} AND t1.Cd_UAR <> 'UAR'
                                AND t1.Nr_TUC in (190) AND t1.Nr_A1 in (1,'1','01',2,'2','02') AND
                                t1.Nr_TI in (35,36,37,38,39,55,56,57,58,59,65,66,67,68,69)
                                GROUP BY t1.Cd_ODI, t1.txt_Desc_Bem
                                """
                            
                            df_OUTb = pd.read_sql(sSQL, bd)
                            df_OUTb['Qtd_AIS'] = df_OUTb['Qtd_AIS'].apply(
                                                                            lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                                                                            if pd.notna(x) else ''
                                                                        )
                            df_OUTb['DESCR_AIS'] = (df_OUTb['Qtd_AIS'].astype(str).fillna('') + 
                                                    " kg, " + df_OUTb['DESCR_AIS'].fillna(''))
                            df_OUTb = df_OUTb.groupby(['Cd_ODI','Txt_DESC_ODI']).agg({
                                                'DESCR_AIS': lambda x: ',<br> '.join(x)
                                            }).reset_index()

                        else:
                            df_OUTb = pd.DataFrame()


                    if not df_OUTa.empty:
                        df_OUT = df_OUT.merge(df_OUTa, how='outer', on =['ODI'], 
                                                suffixes=('_ANT','_AT'), indicator=True)
                        df_OUT['RES_CONC_BDGD_AT_vs_ANT'] = (
                                                                df_OUT['_merge']
                                                                .astype('string')
                                                                .map({
                                                                    'both': 'NO',
                                                                    'left_only': 'APENAS BDGD ATUAL',
                                                                    'right_only': 'APENAS BDGD ANTERIOR'
                                                                })
                                                                .astype('string')
                                                            )
                        df_OUT = df_OUT.drop(columns=['_merge'])
                        df_OUT = df_OUT.fillna("ND")
                    else:
                        df_OUT['CABO_ANTERIORES_BDGD'] = ''
                    if not df_OUTb.empty:
                        teste = df_OUT.merge(df_OUTb, how='inner', left_on ='ODI', right_on = 'Cd_ODI')
                        if len(teste) == 0:
                            df_OUT['Cd_ODI'] = df_OUT['ODI'].str.lstrip('0')
                        else:
                            df_OUT['Cd_ODI'] = df_OUT['ODI']

                        df_OUTint = df_OUT[df_OUT['CABO_ATUAIS_BDGD'] != 'ND'].merge(df_OUTb, how='outer', on =['Cd_ODI'],                                                                                                     suffixes=('_BDGD','_AIS'), indicator=True)
                        df_OUTint['RES_CONC_BDGD_AT_vs_AIS'] = (
                                                                df_OUTint['_merge']
                                                                .astype('string')
                                                                .map({
                                                                    'both': 'NO',
                                                                    'left_only': 'APENAS BDGD ATUAL',
                                                                    'right_only': 'APENAS AIS'
                                                                })
                                                                .astype('string')
                                                            )  
                        df_OUTint = df_OUTint.drop(columns=['_merge'])
    
                        chave = ['ODI','CABO_ATUAIS_BDGD','CABO_ANTERIORES_BDGD','RES_CONC_BDGD_AT_vs_ANT']
                        df_OUT = df_OUT.merge(df_OUTint, how='outer', on=chave, 
                                                indicator=True)
                        df_OUT['RES_CONC'] = (
                                                df_OUT['_merge']
                                                .astype('string')
                                                .map({
                                                    'both': 'NO',
                                                    'left_only': 'POSSÍVEL MUTAÇÃO ou BAIXA',
                                                    'right_only': 'APENAS AIS'
                                                })
                                                .astype('string')
                                            )  
                        df_OUT = df_OUT.drop(columns=['_merge'])
                        df_OUT = df_OUT.fillna("ND")
                        df_OUT = df_OUT.drop(columns=['Cd_ODI_x']).rename(columns={'Cd_ODI_y' : 'Cd_ODI'})
                        crit01 = (
                                    (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ANTERIOR') &
                                    (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'ND')         
                                    )
                        crit02 = (
                                    (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ATUAL') &
                                    (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'NO')         
                                    )
                        crit03 = (
                                    (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'APENAS BDGD ATUAL') &
                                    (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'ND')         
                                    )
                        crit04 = (
                                    (df_OUT['RES_CONC_BDGD_AT_vs_ANT'] == 'ND') &
                                    (df_OUT['RES_CONC_BDGD_AT_vs_AIS'] == 'APENAS AIS')         
                                    )
                        df_OUT['OBS_SFF'] = "NO"
                        df_OUT.loc[crit01, 'OBS_SFF'] = "Item baixado no período ou feito ajustes de codificação patrimonial"
                        df_OUT.loc[crit02, 'OBS_SFF'] = "Item adicionado no período ou feito ajustes de codificação patrimonial, com candidatos no AIS"
                        df_OUT.loc[crit03, 'OBS_SFF'] = "Item adicionado no período ou falta ajustes de codificação patrimonial, sem candidatos no AIS"
                        df_OUT.loc[crit04, 'OBS_SFF'] = "Sobra(s) contábil(eis), reserva(s) técnica(s) fria(s) não modelada(s) na BDGD, TI que não são de subestação ou outros"
                        
                        df_OUT = df_OUT[['ODI','CABO_ATUAIS_BDGD','CABO_ANTERIORES_BDGD',
                                        'RES_CONC_BDGD_AT_vs_ANT','DESCR_AIS',
                                        'RES_CONC_BDGD_AT_vs_AIS', 'RES_CONC', 'OBS_SFF',
                                        'Cd_ODI','Txt_DESC_ODI']]

                    else:
                        df_OUT['DESCR_AIS'] = ''
                        df_OUT['Cd_ODI'] = ''
                        df_OUT['Txt_DESC_ODI'] = ''
                    df_OUT.sort_values(by=['ODI'], inplace=True)
                    if not df_OUT.empty:
                        st.html(f"""
                                <p  style="text-align: justify;text-indent: 40px">Ao avaliar a tabela
                                a seguir temos de observar se o fator de conversão declarado na BDGD
                                está correto. Divergências grandes devem ser justificadas.</p><br>
                                """)
                        df_OUT.to_excel(f"{local}/BDGD_ANLS/CONDUTORES.xlsx", index=False)
                        st.write(f"{df_OUT.to_html(escape=False, index=False)}".replace('style="text-align: right;"','style="text-align: center;"'), 
                                unsafe_allow_html=True)

                        st.divider()
                    if os.path.exists(f"{local}/BDGD_AT/CONSOL/SSDAT.shp"):
                        st.html("""
                                    <h3 style="text-align: left;font-size: 20px;">
                                    f) Área e geometria das SE</h3>
                                    <p  style="text-align: justify;text-indent: 40px">A seguir apresentamos
                                    as geometrias e áreas das SE.
                                    """)
                    with sl.connect(bd_path) as bd:
                        if not existe_tabela('tbl_resumo_area_SE', bd):
                            df_saida = gdfa[['COD_ID','NOME']]
                            df_saida['GEOMETRIA SE'] = 'Indisponível'
                            df_saida['AREA SE'] = 'Indisponível'
                            
                            gdfa_m2 = gdfa.to_crs("EPSG:31983")
                            # Configuração inicial
                            for COD_ID in df_saida['COD_ID'].drop_duplicates().to_list():
                                # Criação da figura e plotagem
                                fig5, ax5 = plt.subplots(figsize=(10, 6), dpi=300)
                                gdfa[gdfa['COD_ID'] == COD_ID].plot(
                                    ax=ax5,
                                    color="#8ecae6",
                                    edgecolor="white",
                                    linewidth=0.2
                                )

                                # Cálculo da área e centroide
                                gdfa_m2["area_m2"] = gdfa_m2.geometry.area
                                gdfa_m2["centroid"] = gdfa_m2.geometry.centroid

                                # Recupera o centroide e a área da geometria correspondente ao COD_ID
                                row = gdfa_m2[gdfa_m2['COD_ID'] == COD_ID]
                                if not row.empty:
                                    centroid = row.iloc[0].centroid
                                    area_m2 = row.iloc[0].area_m2
                                    var_area = f"{area_m2:,.2f} m²".replace('.', 'x').replace(',', '.').replace('x', ',')
                                else:
                                    centroid = None
                                    var_area = "Área desconhecida"

                                # Configuração do título
                                nome = gdfa.loc[gdfa['COD_ID'] == COD_ID, 'NOME'].iloc[0] if not gdfa[gdfa['COD_ID'] == COD_ID].empty else "NOME DESCONHECIDO"
                                descr = gdfa.loc[gdfa['COD_ID'] == COD_ID, 'DESCR'].iloc[0] if not gdfa[gdfa['COD_ID'] == COD_ID].empty else "DESCRIÇÃO DESCONHECIDA"

                                # Configurações do gráfico
                                ax5.set_axis_off()
                                #plt.title(f"SE {nome}, {descr}, {var_area}", fontsize=22, fontweight="bold")
                                plt.tight_layout()

                                # Salvamento da imagem
                                nome_limpo = f"SE_{COD_ID}_{nome}.png".replace("/","_").replace("\\","_").replace("-","_")
                                imagem_path = f"{direto}\\{nome_limpo}"
                                fig5.savefig(imagem_path, dpi=300, bbox_inches='tight', transparent=True)

                                with open(imagem_path, "rb") as img_file:
                                    base64_string = base64.b64encode(img_file.read()).decode("utf-8")

                                df_saida.loc[df_saida['COD_ID'] == COD_ID,'GEOMETRIA SE'] = f"""<img src="data:image/png;base64,{base64_string}" alt="Imagem" width = "150">"""
                                df_saida.loc[df_saida['COD_ID'] == COD_ID,'AREA SE'] = var_area


                            df_saida.sort_values(by=['COD_ID'], inplace=True)
                            df_saida.to_sql('tbl_resumo_area_SE', bd, if_exists='replace', index=False)
                        else:
                            SQLq = "SELECT * FROM tbl_resumo_area_SE"
                            df_saida = pd.read_sql(SQLq, bd)

                    st.write(f"{df_saida.to_html(escape=False, index=False)}".replace('style="text-align: right;"','style="text-align: center;"').replace('<td><img ','<td class="image-cell;"><img '), 
                            unsafe_allow_html=True)


def visualizador_BDGD(st = None):
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

    colGERAL = st.columns([1,10,1], gap='small')
    with colGERAL[1]:
        st.html("""
                    <h2>Análise dos Dados Georeferenciados</h2>

                    <hr></hr>
                                    
                    <h3>Observações iniciais</h3>
                    <div style="text-align: justify;text-indent: 40px; padding-top: 10px">Esse é um documento base 
                                    para se executar análise de dados georeferenciados. Pode-se alterar o arquivo, 
                                    porém somente será aplicado a versão original para análise do valor empregado 
                                    no laudo. Sugere-se usar este arquivo como base para modificações e inclusões 
                                    de análises, para discussões com a fiscalização.<p></p></div>


                    <h3>Licença Pública Geral GNU (GPL)</h3>
                    <div style="text-align: justify; padding-top: 10px">Versão 3, 29 de junho de 2007<p></p></div>
                    <div style="text-align: justify">Copyright (C) 2025, SFF/ANEEL.<p></p></div>
                    <div style="text-align: justify;text-indent: 40px; padding-top: 10px">Este é um documento de uso livre: você pode redistribuí-lo ou modificá-lo sob os termos da Licença Pública Geral GNU, conforme publicada pela Free Software Foundation, tanto na versão 3 da Licença, ou qualquer versão posterior. Ele é distribuído na expectativa de que seja útil, mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM PROPÓSITO ESPECÍFICO. Consulte a Licença Pública Geral GNU para obter mais detalhes, no sitio <a>http://www.gnu.org/licenses/</a>.<p></p></div>

                    <hr></hr>
                                    
                    <h3>Normas</h3>

                    <a href="https://dadosabertos.aneel.gov.br/dataset/base-de-dados-geografica-da-distribuidora-bdgd">Visite o sitio da Aneel para mais detalhes da BDGD!</a><br>
                    <a href="https://www.gov.br/aneel/pt-br/centrais-de-conteudos/procedimentos-regulatorios/proret">Visite o sitio da Aneel para mais detalhes do PRORET!</a>
                                
                    <hr></hr>
                        
                    <h2>Resultado das Análises</h2> 
                                    
                    <hr></hr>
                                    

                                <p  style="text-align: justify;text-indent: 40px">Pretendemos fornecer uma <b>visão 
                                estruturada do controle patrimonial</b> da empresa, com base na análise de um 
                                <b>cadastro de ativos georreferenciados</b>. A abordagem adotada busca verificar a 
                                <b>conformidade patrimonial</b> e identificar possíveis <b>discrepâncias contábeis 
                                e operacionais</b> a partir de uma comparação direta com a <b>base de ativos 
                                registrada na contabilidade</b>.</p>  

                                <p  style="text-align: justify;text-indent: 40px;">Serve como <b>subsídio para
                                fiscalização</b>, permitindo a avaliação da <b>fidedignidade das informações 
                                patrimoniais</b>, bem como a identificação de potenciais <b>riscos e oportunidades de 
                                aprimoramento nos controles internos da empresa</b>. Dentro do escopo, salientamos:<p>  

                                <div class="box" style= "padding: 10px; margin-bottom: 10px;">
                                    <p  style="text-align: justify;text-indent: 40px;"><b>1. Reconciliação Patrimonial</b></p>
                                        <ul style = "padding-left: 80px; text-align: justify;">  
                                            <li>Verificação da correspondência entre os ativos <b>georreferenciados</b> e os 
                                        <b>ativos contábeis registrados</b>.</li>
                                            <li>Identificação de <b>ativos físicos não contabilizados</b> e 
                                        <b>ativos contábeis sem correspondente físico</b>.</li>  
                                            <li>Avaliação da <b>correta classificação e precificação</b> dos ativos no contexto
                                        do laudo.</li>  
                                    </ul>
                                </div>
                                <div class="box" style= "padding: 10px; margin-bottom: 10px;">
                                    <p  style="text-align: justify;text-indent: 40px;"><b>2. Critérios de Conformidade</b></p>  
                                        <ul style = "padding-left: 80px; text-align: justify;">  
                                                <li>Análise com base nas <b>normas contábeis aplicáveis</b> e diretrizes 
                                                regulatórias pertinentes.</li>  
                                                <li>Avaliação do cumprimento dos <b>princípios de transparência e 
                                                rastreabilidade</b> dos ativos patrimoniais.</li>  
                                                <li>Inspeção documental para verificar a <b>coerência entre registros 
                                                e a realidade operacional</b>.</li>  
                                        </ul>
                                </div>
                                <div class="box" style= "padding: 10px; margin-bottom: 10px;">
                                    <p  style="text-align: justify;text-indent: 40px;"><b>3. Análises Complementares</b></p>  
                                        <ul style = "padding-left: 80px; text-align: justify;">  
                                                <li>Estudo de variações patrimoniais ao longo do tempo, considerando 
                                                <b>depreciação, reavaliação e baixa de ativos</b>.</li>  
                                                <li>Avaliação de políticas internas relacionadas à <b>gestão 
                                                patrimonial, inventários físicos e reconciliação contábil</b>.</li>  
                                                <li>Identificação de <b>eventuais riscos associados a ativos 
                                                imobilizados</b>, incluindo subutilização ou obsolescência.</li>  
                                        </ul>
                                </div>
                                <div class="box" style= "padding: 10px; margin-bottom: 10px;">
                                <p  style="text-align: justify;text-indent: 40px;">Utilizaremos a análise 
                                como referência para:</p>  
                                <ul style = "padding-left: 80px; text-align: justify;"> 
                                    <li><b>Identificar inconsistências nos registros patrimoniais</b> que possam impactar 
                                    a <b>elaboração do Laudo</b>.</li>  
                                    <li><b>Avaliar a robustez dos controles internos</b> sobre o gerenciamento dos ativos
                                    fixos.</li>   
                                    <li><b>Emitir recomendações para melhoria da governança patrimonial</b>, incluindo 
                                    sugestões de regularização de ativos não conciliados.</li>   
                                    <li><b>Atestar a confiabilidade dos registros patrimoniais</b> e seu alinhamento 
                                    com as melhores práticas contábeis.</li>   
                                </ul>
                                </div>
                                    

                                <p  style="text-align: justify;text-indent: 40px;">Os achados fornecerão insumos para 
                                a fiscalização do Laudo e servirão de base para eventuais <b>ajustes contábeis, 
                                medidas corretivas e aprimoramento dos processos de controle patrimonial</b>.  

                                <p  style="text-align: justify;text-indent: 40px;">Atualizaremos 
                                conforme novas informações sejam incorporadas, garantindo que a fiscalização conte 
                                com <b>dados atualizados e consistentes</b> para embasar sua avaliação.<p>  

                                <hr></hr>
                                <p style ="text-align: center; font-size: 12px; margin-top: 20px;">
                                📍 Para esclarecimentos adicionais, recomenda-se o contato com a equipe de 
                                    fiscalização responsável.</p>

                                <hr></hr>""" )
        
        executar_vis(_vis_001, bd_BDGDAT_path, local = local)
        executar_vis(_vis_001, bd_BDGDANT_path, "ANT", local = local)
        executar_vis(_vis_002, bd_path, "ANT", local = local)
        executar_vis(_vis_003, bd_path, "ANT", local = local)
        executar_vis(_vis_004, bd_path, bd_BDGDAT_path, bd_BDGDANT_path, local, st,  empresa=empresa)
        executar_vis(_plotar_redes, f'{local}\BD_LOCAL\BDGD_AT_{empresa}_{ano}.db', pct_anl=1, local=local, empresa=empresa, st=st)
        executar_vis(_plotar_redes_sub, f'{local}\BD_LOCAL\BDGD_AT_{empresa}_{ano}.db', pct_anl=1, local=local, empresa=empresa, st=st)
        executar_vis(_plotar_ramais, f'{local}\BD_LOCAL\BDGD_AT_{empresa}_{ano}.db', pct_anl=1, local=local, empresa=empresa, st=st)

            


    