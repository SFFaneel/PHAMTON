from __future__ import annotations
import os, pandas as pd, numpy as np, math, copy
import matplotlib.pyplot as plt
import seaborn as sns, sqlite3 as sl 
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import duckdb

from SRC.ais_funcoes import abertura_voc as fc_abt_voc
from SRC.calculos import tst_cod_sisbase, calc_tx_md
from UTILS import (
                    desenhar_grafo_hierarquico,
                    monitor_completo,
                    exportar_texto,
                    _std_seguro,
                    _lognormal_mu_media,
                    _garante_dir_saida,
                    df_dict_to_json,
                    existe_tabela,
                    max_arq,
                    carga_sqlite_cache,
                    bsc_cd_aneel,
                    imp_tbl_forma_001,
                    busca_ipca,
                    salvar_df,
                    carregar_df
                  )  

import plotly.io as pio
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import silhouette_score
from sklearn.ensemble import IsolationForest
from datetime import timedelta, datetime
import streamlit as st
import dataframe_image as dfi
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Union, Dict
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import itertools
from datetime import date

@dataclass
class BlocoResultado:
    bloco: int
    t_revisao: int
    anos_no_bloco: int
    base_residual: float
    receita_anual: float
    vp_bloco: float

@dataclass
class ModeloConfig:
    n_sim: int = 10000
    min_historia_mes: int = 6
    usar_bootstrap: bool = True
    aplicar_sazonalidade: bool = True
    permitir_mes_negativo: bool = True

    habilitar_cisnes: bool = True
    quartil_extraordinario: float = 0.95
    min_uc_extra_eventos: int = 3
    min_ti_extra_eventos: int = 8
    fallback_lambda_evento_por_mes: float = 0.05
    fallback_valor_evento_medio: float = 5000000.0
    fallbackk_valor_evento_sigma: float = 1.0
    evento_escala: float = 1

    sigma_choque_comum: float = 0.1
    escala_residual_dp: float = 1.0
    seed: int = 42


@monitor_completo(st.session_state.LOGGER)
def outliers_iqr(df, grupo, col = 'VL_TOTAL'):
    q1 = df.groupby(grupo)[col].transform(lambda x: x.quantile(0.25))
    q3 = df.groupby(grupo)[col].transform(lambda x: x.quantile(0.75))
    iqr = q3 - q1
    return (df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)

@monitor_completo(st.session_state.LOGGER)
def score_risco(df, col_COD ='COD_ITEM', col_VL = 'VL_TOTAL'):
    base = (
                df.groupby(col_COD)
                .agg(
                    freq_sd =('OUTLIER','mean'),
                    cmu=(col_VL,'mean'),
                    cmax=(col_VL,'max'),
                    dp=(col_VL,'std')
                )
                .reset_index()
            )

    base['flag_cmu_zero'] = (base['cmu'] == 0).astype(int)
    base['flag_cmu_estp'] = (base['cmu'] < 0).astype(int)
    base['dp'] = base['dp'].fillna(0)
    cmu_est = base['cmu'].clip(lower=1)
    base['VL_REF'] = np.log1p(np.maximum((base['cmax']/cmu_est) - 1, 0))
    base['dp_est'] = np.log1p(base['dp'])

    base['VL_RISCO_BRT'] = (
                             0.6 * base['freq_sd'] +
                             0.3 * base['VL_REF'] +
                             0.1 * (base['dp_est'] / cmu_est) +
                             0.1 * base['flag_cmu_zero'] * base['flag_cmu_estp']
                           )
    p95 = base['VL_RISCO_BRT'].quantile(0.95)
    base['VL_RISCO'] = (
                            100 * base['VL_RISCO_BRT'] / p95
                        ).clip(upper=100).round(1)
    
    return base

@monitor_completo(st.session_state.LOGGER)
def analise_causa(df, meses, col_COD ='COD_ITEM', col_VL = 'VL_TOTAL', col_DT = 'mes', janela=2):
    eventos = []
    for _, r in df[df['OUTLIER']].iterrows():
        contexto = df[
                        (df[col_COD]==r[col_COD]) &
                        (df[col_DT].between(r[col_DT]-janela, r[col_DT]+janela))
                     ]
        ref = contexto[contexto[col_DT]!=r[col_DT]][col_VL].mean()
        eventos.append({
                            f'{col_COD}': r[col_COD],
                            'MES': meses[r[col_DT]],
                            'CUSTO_OUTLIER': round(r[col_VL],2),
                            'MEDIA_CONTEXTO': round(ref,2),
                            'DELTA_%': round(100*(r[col_VL]-ref)/ref,1)
                        })
    return pd.DataFrame(eventos)

@monitor_completo(st.session_state.LOGGER)
def clusterizar_itens(df_risco, n_clusters=3):
    for nm in ['freq_sd','VL_REF','dp','VL_RISCO']:
        if nm not in df_risco.columns:
            raise "Problemas com dataframe de risco."
    X = df_risco[['freq_sd','VL_REF','dp','VL_RISCO']]
    X = X.fillna(0)

    X_scaled = StandardScaler().fit_transform(X)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_risco['CLUSTER'] = kmeans.fit_predict(X_scaled)

    mapa = {
                0: '➖ Estável',
                1: '↕️ Volátil',
                2: '⬇️ Crítico'
            }

    df_risco['PERFIL_RISCO'] = df_risco['CLUSTER'].map(mapa)
    return df_risco

@monitor_completo(st.session_state.LOGGER)
def resumo_roa(bd, dir_trab, empresa, st = None, tbl = 'ROA'):
    if st == None:
        return

    nm_tbl = tbl.lower()
    pio.templates.default = "plotly"
    a = st.progress(0, "Iniciando descrição do ROA...")
    dir_trabm = dir_trab.replace("AIS_ANLS","")
    arquivo_csv = [
                        os.path.join(f"{dir_trabm}DADOS_BRUTOS_MANUAL", f)
                        for f in os.listdir(f"{dir_trabm}/DADOS_BRUTOS_MANUAL")
                        if f.lower().endswith('.csv') and (f.lower()[:4]== f"{nm_tbl}_")
                    ]
    arq = arquivo_csv[0].replace("\\","/")

    a.progress(5, f"Importando o {tbl}...")
    #-------------------------------------------------------------------------------
    # Dados da distribuição temporal
    #-------------------------------------------------------------------------------
    erro = {}
    for enc in ['CP1252', 'latin-1', 'utf-8']:
        try:
            SQLq = f"""SELECT 
                                TRY_CAST(Dt_Lcmto AS DATE) AS Dt_Lcmto,
                                SUM(
                                    CASE
                                        WHEN TRIM(VL_tot) IN ('', '-') OR VL_tot IS NULL THEN 0
                                        ELSE TRY_CAST(
                                            REPLACE(
                                                REPLACE(TRIM(VL_tot), '.', ''),
                                                ',', '.'
                                            ) AS DECIMAL(18,2)
                                        )
                                    END
                                ) AS VL_TOTAL
                                FROM read_csv('{arq}', 
                                delim='|',
                                null_padding=true, 
                                encoding='{enc}',
                                parallel=true,
                                all_varchar=true)
                                GROUP BY Dt_Lcmto
                                ORDER BY Dt_Lcmto;
                        """

            df_ROA = duckdb.query(SQLq).to_df()
            break
        except Exception as e:
            erro[enc] = e

    if len(erro)>0:
        st.text(erro)
        raise UserWarning("Você tem problema de codificação do arquivo.")

    a.progress(15, "Análise da distribuição temporal...")
    df_ROA["Dt_Lcmto"] = df_ROA["Dt_Lcmto"].ffill()
    df_ROA["mes"] = df_ROA["Dt_Lcmto"].dt.to_period("M").astype(str)
    df_ROA["VL_mm"] = df_ROA.set_index("Dt_Lcmto")["VL_TOTAL"].rolling("30D", min_periods=1).mean().values
    df_ROA["VL_loess_like"] = df_ROA["VL_TOTAL"].ewm(span=30, adjust=False).mean()

    st.html(f"""<h2 style="text-align: center;font-size: 30px;">
                        Descrições do {tbl}</h2>
                        """)  
    st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                        Análise de distribuição temporal dos lançamentos</h3>
                        """)  
    st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">O primeiro gráfico (Total por Data) mostra a distribuição 
                dos valores ao longo do tempo, permitindo identificar concentrações, rupturas e pontos isolados que podem 
                indicar lançamentos atípicos. O segundo gráfico (suavizada) revela a tendência real da série, 
                filtrando ruídos e destacando movimentos estruturais, como períodos de crescimento, estabilização ou 
                queda do valor das obras. Já o terceiro gráfico (Boxplot + Scatter por mês) permite comparar a 
                variabilidade mensal, identificando meses com maior dispersão, presença de outliers e padrões de comportamento 
                recorrentes. Por fim, o gráfico de tendência com média móvel suaviza flutuações diárias e evidencia ciclos 
                ou tendências de longo prazo, facilitando a leitura da evolução gradual dos valores. Em conjunto, os quatro 
                gráficos oferecem uma visão complementar: distribuição pontual, tendência suave, variação mensal e comportamento 
                de longo prazo. 
                </p><br>
                <p  style="text-align: justify;text-indent: 40px>
                No conjunto dos quatro gráficos, espera-se observar, de maneira geral, um comportamento em que, nos primeiros 
                anos da série, anterior ao início do período incremental, os valores se distribuam de forma mais residual e 
                dispersa. A partir do segundo ano do período incremental, a tendência incremental destacada pela suavização 
                (média móvel) deve se tornar mais perceptível, refletindo uma fase de intensificação dos lançamentos. 
                Já na análise mensal (boxplot + scatter), é comum que a distribuição se torne mais concentrada e próxima de um 
                padrão aproximadamente normal nos períodos finais. Assim, os gráficos em conjunto ajudam a visualizar a 
                transição de um estágio inicial mais irregular para uma fase de maturidade, na qual os valores se tornam mais 
                consistentes e concentrados ao longo do tempo.
                </p><br>
                """) 
    if tbl == 'ROA':
        ax = 'Cd_SubODI'
        ni = "dos Investimentos"
        c1 = "2.3.24"
        c2 = "2.3.25"
    elif tbl == 'ROD':
        ax = 'Cd_ODD'
        ni = "das Desativações"
        c1 = "2.4.4"
        c2 = "2.4.5"
    else:
        return "Falhou"
    texto = f"""<h6>{c1} Análise de distribuição temporal dos lançamentos do {tbl}.</h6>
                <p>O primeiro gráfico (Total por Data) mostra a distribuição 
                dos valores ao longo do tempo, permitindo identificar concentrações, rupturas e pontos isolados que podem 
                indicar lançamentos atípicos. O segundo gráfico (suavizada) revela a tendência real da série, 
                filtrando ruídos e destacando movimentos estruturais, como períodos de crescimento, estabilização ou 
                queda do valor das obras. Já o terceiro gráfico (Boxplot + Scatter por mês) permite comparar a 
                variabilidade mensal, identificando meses com maior dispersão, presença de outliers e padrões de comportamento 
                recorrentes. Por fim, o gráfico de tendência com média móvel suaviza flutuações diárias e evidencia ciclos 
                ou tendências de longo prazo, facilitando a leitura da evolução gradual dos valores. Em conjunto, os quatro 
                gráficos oferecem uma visão complementar: distribuição pontual, tendência suave, variação mensal e comportamento 
                de longo prazo.</p>
                <p>No conjunto dos quatro gráficos, espera-se observar, de maneira geral, um comportamento em que, nos primeiros 
                anos da série, anterior ao início do período incremental, os valores se distribuam de forma mais residual e 
                dispersa. A partir do segundo ano do período incremental, a tendência incremental destacada pela suavização 
                (média móvel) deve se tornar mais perceptível, refletindo uma fase de intensificação dos lançamentos. 
                Já na análise mensal (boxplot + scatter), é comum que a distribuição se torne mais concentrada e próxima de um 
                padrão aproximadamente normal nos períodos finais. Assim, os gráficos em conjunto ajudam a visualizar a 
                transição de um estágio inicial mais irregular para uma fase de maturidade, na qual os valores se tornam mais 
                consistentes e concentrados ao longo do tempo.</p>
                <INSERIR>DIST_TEMP_{tbl}.png</INSERIR>\n
                <p1>Para melhor visualização, alteramos o box-plot, por conta da densidade de datas:</p1>
                <INSERIR>DIST_TEMP_{tbl}_2.png</INSERIR>\n
                <p2>Em sua análise verifique se existem concentrações atípicas de densidade de lançamentos em determinados períodos;
                se há períodos em que a densidade de lançamentos é muito baixa ou praticamente inexistente;
                o comportamento da distribuição temporal mudou em algum ponto (mudança de regime estatístico);
                ela tende a ter valores residuais ou significativos em período anterior ao ciclo; etc..
                </p2>
                """
    dir_esc = f"{dir_trabm}RELATORIOS/textos".replace("\\","/").replace("/","/")
    xEsc = exportar_texto(dir_esc, f"{tbl}_DESC.txt", texto, True)
    st.html(f'<div class="img-box-1">')
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    plt.subplots_adjust(hspace=0.3, wspace=0.25)

    ax1 = axes[0, 0]
    sns.scatterplot(
                        data=df_ROA,
                        x="Dt_Lcmto",
                        y="VL_TOTAL",
                        hue="VL_TOTAL",
                        palette="viridis",
                        size="VL_TOTAL",
                        sizes=(40, 200),
                        alpha=0.7,
                        ax=ax1,
                        s=50
                    )

    ax1.set_title("Distribuição de Valor Total x Tempo", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Data")
    ax1.set_ylabel("VL_TOTAL (R$)")
    ax1.legend_.remove()

    ax2 = axes[0, 1]
    sns.scatterplot(
                    data=df_ROA,
                    x="Dt_Lcmto",
                    y="VL_TOTAL",
                    color="gray",
                    s=40,
                    alpha=0.5,
                    ax=ax2
                )
    ax2.plot(df_ROA["Dt_Lcmto"], df_ROA["VL_loess_like"], color="crimson", linewidth=3, label="Suavização (EWMA)")

    ax2.set_title("Suavizada", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Data")
    ax2.set_ylabel("VL_TOTAL")
    ax2.legend()

    ax3 = axes[1, 0]

    sns.boxplot(
                    data=df_ROA,
                    x="mes",
                    y="VL_TOTAL",
                    fliersize=0,
                    color="lightgray",
                    ax=ax3
                )

    sns.stripplot(
                    data=df_ROA,
                    x="mes",
                    y="VL_TOTAL",
                    hue="VL_TOTAL",
                    palette="viridis",
                    alpha=0.7,
                    size=6,
                    ax=ax3,
                    dodge=False
                )
    
    for idx, label in enumerate(ax3.get_xticklabels()):
        if idx % 3 != 0:
            label.set_visible(False)

    ax3.set_title("Distribuição Mensal (Boxplot + Scatter)", fontsize=14, fontweight="bold")
    ax3.set_xlabel("Mês")
    ax3.set_ylabel("VL_TOTAL")
    ax3.tick_params(axis="x", rotation=45)
    ax3.legend_.remove()

    ax4 = axes[1, 1]

    ax4.plot(df_ROA["Dt_Lcmto"], df_ROA["VL_TOTAL"], alpha=0.25, color="gray", label="VL_TOTAL (bruto)")
    ax4.plot(df_ROA["Dt_Lcmto"], df_ROA["VL_mm"], color="blue", linewidth=3, label="Média Móvel (30 dias)")

    ax4.set_title("Trend Line — Média Móvel (30 dias)", fontsize=14, fontweight="bold")
    ax4.set_xlabel("Data")
    ax4.set_ylabel("VL_TOTAL")
    ax4.legend()
    plt.tight_layout()
    col1, col2, col3 = st.columns([1,3,1], gap = 'small')
    with col2:
        st.pyplot(fig)
    dir_FIG = f"{dir_trabm}RELATORIOS/figuras".replace("\\","/").replace("/","/")
    if not os.path.exists(dir_FIG):
        os.makedirs(dir_FIG, exist_ok=True)

    fig.savefig(f"{dir_FIG}/DIST_TEMP_{tbl}.png", dpi=300, bbox_inches='tight')
    st.html('</div>')

    st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">
                Para melhor visualiação, abaixo o gráfico de Box-plot. Nele, foi definida a
                região de outliers (vermelho) e apontado o limite superior do box-plot.
                </p><br>
                """) 
    st.html(f'<div class="img-box-1">')
    sns.set_theme(style="whitegrid", rc={
                    "axes.facecolor": "#FAFAFA",
                    "grid.color": "#E8E8E8",
                    "axes.edgecolor": "#CCCCCC",
                    "axes.titleweight": "bold",
                    "figure.facecolor": "#FFFFFF"
                    })
    fig, axo = plt.subplots(figsize=(8, 12))

    sns.boxplot(
                    data=df_ROA,
                    y="mes",
                    x="VL_TOTAL",
                    width=0.75,
                    linewidth=0.4,
                    boxprops={"facecolor": "white", "edgecolor": "#333"},
                    showcaps=True,
                    fliersize=0,
                    whiskerprops={"color": "#333"},
                    orient="h",
                    ax=axo
                )
    
    Q1 = df_ROA["VL_TOTAL"].quantile(0.25)
    Q3 = df_ROA["VL_TOTAL"].quantile(0.75)
    IQR = Q3 - Q1

    lim_inf = Q1 - 1.5 * IQR
    lim_sup = Q3 + 1.5 * IQR

    limite_max = df_ROA["VL_TOTAL"].quantile(0.99)
    limite_min = df_ROA["VL_TOTAL"].quantile(0.01)

    axo.axvspan(limite_min,lim_inf,color="red",alpha=0.10)
    axo.axvspan(lim_sup,limite_max,color="red",alpha=0.10)

    for idx, label in enumerate(axo.get_yticklabels()):
        if idx % 3 != 0:
            label.set_visible(False)

    for i, line in enumerate(axo.lines):
        if i % 6 == 3:
            xdata = line.get_xdata()
            xmax = xdata.max()
            y = line.get_ydata().mean()
            if xmax>lim_sup:
                axo.text(
                            xmax,
                            y,
                            f"{xmax:,.0f}".replace(",","."),
                            va="center",
                            ha="left",
                            fontsize=9,
                            color="black",
                            fontweight="bold"
                        )
    
    axo.set_xlim(limite_min, limite_max)

    axo.set_title("Distribuição Mensal (Boxplot)", fontsize=14, fontweight="bold")
    axo.set_ylabel("Mês")
    axo.set_xlabel("Valor (R$)")

    sns.despine(left=True, bottom=False)
    plt.tight_layout()
    col1b, col2b, col3b = st.columns([1,2,1], gap = 'small')
    with col2b:
        st.pyplot(fig)
    fig.savefig(f"{dir_FIG}/DIST_TEMP_{tbl}_2.png", dpi=300, bbox_inches='tight')
    st.html(f'</div>')
    a.progress(25, f"Importando o {tbl}, por estrutura...")
    arquivo_csv = [
                        os.path.join(f"{dir_trabm}/DADOS_BRUTOS_MANUAL", f)
                        for f in os.listdir(f"{dir_trabm}/DADOS_BRUTOS_MANUAL")
                        if f.lower().endswith('.csv') and ((f.lower()[:4]=="ros_") & (f.lower()[:5]!="ros_v") & (f.lower()[:5]!="ros_a"))
                    ]
    arq1 = arquivo_csv[0].replace("\\","/")

    erro = {}
    for enc in ['CP1252', 'latin-1', 'utf-8']:
        try:        
            SQLq = f"""
                WITH T1 AS (
                            SELECT 
                                CAST({ax} AS STRING) AS {ax},
                                CAST(Nr_TI AS STRING) AS Nr_TI,
                                CAST(Cd_NG AS STRING) AS Cd_NG,
                                CAST(Cd_CA AS STRING) AS Cd_CA,
                                (SUM(
                                    CASE
                                        WHEN TRIM(VL_tot) IN ('', '-') OR VL_tot IS NULL THEN 0
                                        ELSE TRY_CAST(
                                            REPLACE(
                                                REPLACE(TRIM(VL_tot), '.', ''),
                                                ',', '.'
                                            ) AS DECIMAL(18,2)
                                        )
                                    END
                                )) AS VL_TOTAL
                            FROM read_csv('{arq}',
                                delim='|',
                                null_padding=true, 
                                encoding='{enc}',
                                parallel=true,
                                all_varchar=true
                            )
                            GROUP BY {ax}, Nr_TI, Cd_NG, Cd_CA
                        ),

                        T2 AS (
                            SELECT
                                CAST({ax} AS STRING) AS {ax},
                                CAST(Cd_Tipo_Obra AS STRING) AS Cd_Tipo_Obra
                            FROM read_csv('{arq1}',
                                delim='|',
                                null_padding=true, 
                                encoding='{enc}',
                                parallel=true,
                                all_varchar=true
                            )
                        ),

                        ti AS (
                                SELECT
                                    CAST(Id_TI AS STRING)        AS Id_TI,
                                    CAST(Txt_Class AS STRING)    AS Txt_Class
                                FROM read_csv_auto('tabelas/TBL_TI.csv',
                                    delim='|',
                                    null_padding=true,
                                    ignore_errors=true
                                )
                            )

                        SELECT
                            ti.Txt_Class AS Txt_TI,
                            COALESCE(T2.Cd_Tipo_Obra, '0') AS Cd_Tipo_Obra,
                            T1.Cd_NG,
                            T1.Cd_CA,
                            SUM(T1.VL_TOTAL) AS VL_TOTAL
                        FROM T1
                        LEFT JOIN T2
                            ON T1.{ax} = T2.{ax}
                            LEFT JOIN ti ON T1.Nr_TI = ti.Id_TI
                        GROUP BY 
                            T2.Cd_Tipo_Obra,
                            ti.Txt_Class,
                            T1.Cd_NG,
                            T1.Cd_CA
                        ORDER BY
                            T2.Cd_Tipo_Obra,
                            ti.Txt_Class,
                            T1.Cd_NG,
                            T1.Cd_CA;
            """

            df_ROA = duckdb.query(SQLq).to_df()
            break
        except Exception as e:
            erro[enc] = e

    if len(erro)>0:
        st.text(erro)
        raise UserWarning("Você tem problema de codificação do arquivo.")


    a.progress(45, "Análise da estrutura de custos...")
    st.html(f"""<h2 style="text-align: center;font-size: 30px;">
                        Análise de distribuição estrutural dos lançamentos</h2>
                        """)  
    
    texto = f"""
            <h6>{c2} Análise de distribuição estrutural dos lançamentos do {tbl}</h6>
            <p>O gráfico mostra a distribuição estrutural, permitindo identificar como a empresa distribui seus {ni[4:].lower()}. As naturezas de agregação são
            tipologia; tipologia e tipo de investimento (investimento ou manutenção); tipologia, tipo de investimento 
            (investimento ou manutenção) e tipo de obra; tipologia, tipo de investimento (investimento ou manutenção), 
            tipo de obra e natureza de gasto; e tipologia, tipo de investimento (investimento ou manutenção), 
            tipo de obra, natureza de gasto e tipo de CA.</p> 
            <INSERIR>DIST_ESTRUTURA_COL_{tbl}.png</INSERIR>\n
            <p1>Verificar se a distribuição dos lançamentos por tipologia (ou níveis mais detalhados) apresenta 
            concentrações no padrão de {ni[4:].lower()}, considerando os perfis do ROS; se a segmentação entre investimento 
            e manutenção apresenta padrões temporais distintos ou anômalos ao longo das tipologias e tipos de obra;
            se distribuição estrutural evidencia aumento súbito em determinadas combinações (ex.: tipologia + tipo de obra + tipo de CA);
            etc..</p1>
            """
    
    xEsc = exportar_texto(dir_esc, f"{tbl}_DESC.txt", texto, False)

    df_ROA = df_ROA.fillna('0')
    df_ROA['Cd_TIPO'] = df_ROA['Cd_Tipo_Obra']
    dic_NG = {"1" : "UC",
              "2" : "COM",
              "3" : "MOP",
              "4" : "ST",
              "5" : "JOA",
              "6" : "OUTROS"}
    
    dic_CA = {"0" : "NA",
              "1" : "VL_FRT_TRN",
              "2" : "VL_PRJ",
              "3" : "VL_GER",
              "4" : "VL_FISC",
              "5" : "VL_MONT",
              "6" : "VL_SUP"}
    
    dic_TP1 = { "0" : "NA",
                '1' : 'Ampliação/Expansão',
                '2' : 'Construção',
                '3' : 'Manutenção',
                '4' : 'Melhoria/Reforma',
                '5' : 'Administrativo',
                '6' : 'Administrativo',
                '7' : 'Incorporação',
                '8' : 'PEE',
                '9' : 'PED',
                '10' : 'Manutenção',
                '11' : 'Medição',
                '12' : 'Medição'
                }
    dic_TP2 = { "0" : "NA",
                '1' : 'Investimento',
                '2' : 'Investimento',
                '3' : 'Manutenção',
                '4' : 'Investimento',
                '5' : 'Investimento',
                '6' : 'Manutenção',
                '7' : 'Investimento',
                '8' : 'Investimento',
                '9' : 'Investimento',
                '10' : 'Investimento',
                '11' : 'Investimento',
                '12' : 'Manutenção'
                }
    
    a.progress(55, "Análise da estrutura de custos, gráfico de colunas...")
    df_ROA[["Txt_TI", "Cd_TIPO", "Cd_Tipo_Obra", 
            "Cd_NG", "Cd_CA"]] =df_ROA[["Txt_TI", "Cd_TIPO", "Cd_Tipo_Obra", 
                                        "Cd_NG", "Cd_CA"]].replace('', None)
    
    df_ROA["Cd_NG"] = df_ROA["Cd_NG"].map(dic_NG)
    df_ROA["Cd_CA"] = df_ROA["Cd_CA"].map(dic_CA)
    df_ROA["Cd_TIPO"] = df_ROA["Cd_TIPO"].map(dic_TP2)
    df_ROA["Cd_Tipo_Obra"] = df_ROA["Cd_Tipo_Obra"].map(dic_TP1)
    df_ROA = df_ROA.fillna("ND")
    
    a.progress(65, "Análise da estrutura de custos, gráfico sunburst...")
    st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">O gráfico abaixo representa a estrutura hierárquica  
                {ni.lower()}, de forma mais prática, permitindo compreender como o valor total se distribui e se ramifica 
                a partir de diferentes níveis de agregação. No centro do gráfico está o 
                nível mais alto (Txt_TI), que corresponde aos grandes agrupamentos de tipologias. Cada anel subsequente 
                expande a hierarquia para níveis mais detalhados — primeiro Cd_TIPOLOGIA, depois Cd_Tipo_Obra, seguido por Cd_NG 
                e finalmente Cd_CA — mostrando como cada categoria contribui proporcionalmente ao volume total de {ni[4:].lower()}. 
                A área de cada fatia reflete o valor investido naquele grupo, e a cor permite identificar rapidamente a qual 
                TI cada segmento pertence, mesmo nos níveis mais profundos. Ao navegar pelo gráfico, é possível observar tanto 
                a participação relativa de cada elemento, quanto identificar concentrações, desequilíbrios e caminhos 
                dominantes na distribuição estrutural {ni.lower()}.
                </p><br>
                """) 

    texto = f"""
                <p>O gráfico abaixo representa a estrutura hierárquica 
                {ni.lower()}, de forma mais prática, permitindo compreender como o valor total se distribui e se ramifica 
                a partir de diferentes níveis de agregação, explicados no parágrafo anterior. No centro do gráfico está o 
                nível mais alto (Txt_TI), que corresponde aos grandes agrupamentos de tipologias. Cada anel subsequente 
                expande a hierarquia para níveis mais detalhados — primeiro Cd_TIPO, depois Cd_Tipo_Obra, seguido por Cd_NG 
                e finalmente Cd_CA — mostrando como cada categoria contribui proporcionalmente ao volume total de {ni[4:].lower()}. 
                A área de cada fatia reflete o valor investido naquele grupo, e a cor permite identificar rapidamente a qual 
                TI cada segmento pertence, mesmo nos níveis mais profundos. Ao navegar pelo gráfico, é possível observar tanto 
                a participação relativa de cada elementUo, quanto identificar concentrações, desequilíbrios e caminhos 
                dominantes na distribuição estrutural {ni.lower()}.</p>
                <INSERIR>DIST_ESTRUTURA_SUNBURST_{tbl}.png</INSERIR>\n
            """
    xEsc = exportar_texto(dir_esc, f"{tbl}_DESC.txt", texto, False)
    df_ROA['VL_TOTAL'] = df_ROA['VL_TOTAL'].clip(0, df_ROA['VL_TOTAL'])

    fig2 = px.sunburst(
                        df_ROA,
                        path=["Txt_TI", "Cd_TIPO", "Cd_Tipo_Obra", "Cd_NG", "Cd_CA"],
                        values="VL_TOTAL",
                        color="Txt_TI",
                        title=f"Distribuição Hierárquica {ni}"
                    )
    fig2.update_traces(marker=dict(line=dict(color="white", width=1)))
    fig2.update_layout(title_x=0.5, margin=dict(t=50, l=0, r=0, b=0))
    st.plotly_chart(fig2, use_container_width=True)
    fig2.write_image(f"{dir_FIG}/DIST_ESTRUTURA_SUNBURST_{tbl}.png", scale=2)
    a.progress(100, "Finalizado.")
    a.empty()
    return None


def resumo_st(bd, dir_trab, empresa, st = None, tbl = 'ROA'):
    if st == None:
        return
    if tbl == 'ROA':
        nm_PRJ = 'Cd_SubODI'
        ni = "dos Investimentos"
    else:
        nm_PRJ = 'Cd_ODD'
        ni = "das Desativações"
    nm_tbl = tbl.lower()
    pio.templates.default = "plotly"
    a = st.progress(0, "Iniciando descrição de ST...")
    dir_trabm = dir_trab.replace("AIS_ANLS","")
    arquivo_csv = [
                        os.path.join(f"{dir_trabm}DADOS_BRUTOS_MANUAL", f)
                        for f in os.listdir(f"{dir_trabm}/DADOS_BRUTOS_MANUAL")
                        if f.lower().endswith('.csv') and (f.lower()[:4]== f"{nm_tbl}_")
                    ]
    arq = arquivo_csv[0].replace("\\","/")

    arquivo_csv = [
                        os.path.join(f"{dir_trabm}DADOS_BRUTOS_MANUAL", f)
                        for f in os.listdir(f"{dir_trabm}/DADOS_BRUTOS_MANUAL")
                        if f.lower().endswith('.csv') and ((f.lower()[:4]=="ros_") & (f.lower()[:5]!="ros_v"))
                    ]
    arq1 = arquivo_csv[0].replace("\\","/")

    a.progress(5, f"Importando o {tbl}...")
    #-------------------------------------------------------------------------------
    # Dados de serviços
    #-------------------------------------------------------------------------------
    SQLq = f"""
                WITH T1 AS (
                            SELECT 
                                CAST({nm_PRJ} AS STRING) AS {nm_PRJ},
                                CAST(Nr_TI AS STRING) AS Nr_TI,
                                CAST(Cd_CA AS STRING) AS Cd_CA,
                                CAST(COD_ITEM AS STRING) AS COD_ITEM,
                                CAST(Dt_Lcmto AS DATE) AS Dt_Lcmto,
                                (SUM(
                                    CAST(
                                        REPLACE(
                                            REPLACE(Qtd, '.', ''), 
                                            ',', '.'
                                        ) AS DOUBLE
                                    )
                                )) AS Qtd_TOTAL,
                                (SUM(
                                    CAST(
                                        REPLACE(
                                            REPLACE(VL_tot, '.', ''), 
                                            ',', '.'
                                        ) AS DOUBLE
                                    )
                                )) AS VL_TOTAL
                            FROM read_csv('{arq}',
                                delim='|',
                                header=true, 
                                sample_size=-1
                            )
                            WHERE Cd_NG = 4
                            GROUP BY CAST(Dt_Lcmto AS DATE), Nr_TI, {nm_PRJ}, Cd_CA, COD_ITEM
                        ),

                        T2 AS (
                            SELECT
                                CAST({nm_PRJ} AS STRING) AS {nm_PRJ},
                                CAST(Cd_Tipo_Obra AS STRING) AS Cd_Tipo_Obra
                            FROM read_csv('{arq1}',
                                delim='|',
                                header=true, 
                                sample_size=-1
                            )
                        ),

                        ti AS (
                                SELECT
                                    CAST(Id_TI AS STRING)        AS Id_TI,
                                    CAST(Txt_Class AS STRING)    AS Txt_Class
                                FROM read_csv('tabelas/TBL_TI.csv',
                                    delim='|',
                                    header=true, 
                                    sample_size=-1
                                )
                            ),

                        tiS AS (SELECT
                            ti.Txt_Class AS Txt_TI,
                            T1.{nm_PRJ},
                            COALESCE(T2.Cd_Tipo_Obra, '0') AS Cd_Tipo_Obra,
                            T1.Cd_CA,
                            T1.COD_ITEM,
                            T1.Dt_Lcmto,
                            CASE
                                WHEN SUM(T1.Qtd_TOTAL) <> 0 THEN SUM(T1.Qtd_TOTAL)
                                ELSE 1 
                            END
                            AS Qtd_TOTAL,
                            SUM(T1.VL_TOTAL) AS VL_TOTAL
                        FROM T1
                        LEFT JOIN T2
                            ON T1.{nm_PRJ} = T2.{nm_PRJ}
                            LEFT JOIN ti ON T1.Nr_TI = ti.Id_TI
                        GROUP BY
                            Txt_TI,
                            T1.{nm_PRJ}, 
                            T2.Cd_Tipo_Obra,
                            ti.Txt_Class,
                            T1.Cd_CA,
                            T1.COD_ITEM,
                            T1.Dt_Lcmto
                        ORDER BY
                            T1.Dt_Lcmto,
                            Txt_TI,
                            T1.{nm_PRJ},
                            T2.Cd_Tipo_Obra,
                            ti.Txt_Class,
                            T1.Cd_CA,
                            T1.COD_ITEM)
                        SELECT * FROM tiS WHERE VL_TOTAL !=0;
            """
    df_ST = duckdb.query(SQLq).to_df()

    a.progress(15, "Análise da distribuição temporal...")
    df_ST["mes"] = df_ST["Dt_Lcmto"].dt.to_period("M").astype(str)
    df_ST = df_ST.fillna('0')
    df_ST['Cd_TIPO'] = df_ST['Cd_Tipo_Obra']

    dic_CA = {"0" : "NA",
              "1" : "VL_FRT_TRN",
              "2" : "VL_PRJ",
              "3" : "VL_GER",
              "4" : "VL_FISC",
              "5" : "VL_MONT",
              "6" : "VL_SUP"}
    
    dic_TP1 = { "0" : "NA",
                '1' : 'Ampliação/Expansão',
                '2' : 'Construção',
                '3' : 'Manutenção',
                '4' : 'Melhoria/Reforma',
                '5' : 'Administrativo',
                '6' : 'Administrativo',
                '7' : 'Incorporação',
                '8' : 'PEE',
                '9' : 'PED',
                '10' : 'Manutenção',
                '11' : 'Medição',
                '12' : 'Medição'
                }
    dic_TP2 = { "0" : "NA",
                '1' : 'Investimento',
                '2' : 'Investimento',
                '3' : 'Manutenção',
                '4' : 'Investimento',
                '5' : 'Investimento',
                '6' : 'Manutenção',
                '7' : 'Investimento',
                '8' : 'Investimento',
                '9' : 'Investimento',
                '10' : 'Investimento',
                '11' : 'Investimento',
                '12' : 'Manutenção'
                }
    
    a.progress(20, "Análise da estrutura de custos, gráfico sunburst...")

    st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">O gráfico abaixo representa a estrutura hierárquica de ST  
                {ni.lower()}, de forma mais prática, permitindo compreender como o valor total se distribui e se ramifica 
                a partir de diferentes níveis de agregação, explicados no parágrafo anterior. No centro do gráfico está o 
                nível mais alto (Txt_TI), que corresponde aos grandes agrupamentos de tipologias. Cada anel subsequente 
                expande a hierarquia para níveis mais detalhados — primeiro Cd_TIPO, depois Cd_Tipo_Obra  
                e finalmente Cd_CA — mostrando como cada categoria contribui proporcionalmente ao volume total de ST {ni[4:].lower()}. 
                A área de cada fatia reflete o valor investido naquele grupo, e a cor permite identificar rapidamente a qual 
                TI cada segmento pertence, mesmo nos níveis mais profundos. Ao navegar pelo gráfico, é possível observar tanto 
                a participação relativa de cada elemento, quanto identificar concentrações, desequilíbrios e caminhos 
                dominantes na distribuição estrutural de ST {ni.lower()}. Um detalhe, a visualização permite explorar: 
                clicar, abrir, ver distribuição interna.
                </p><br>
                """) 
    
    df_ST["Cd_CA"] = df_ST["Cd_CA"].map(dic_CA)
    df_ST["Cd_TIPO"] = df_ST["Cd_TIPO"].map(dic_TP2)
    df_ST["Cd_Tipo_Obra"] = df_ST["Cd_Tipo_Obra"].map(dic_TP1)
    df_ST = df_ST.fillna("ND")

    fig2 = px.sunburst(
                            df_ST,
                            path=["mes", "Txt_TI", "Cd_TIPO", "Cd_Tipo_Obra", "Cd_CA"],
                            values="VL_TOTAL",
                            color="Txt_TI",
                            title=f"Distribuição Hierárquica ST"
                        )
    fig2.update_traces(marker=dict(line=dict(color="white", width=1)))
    fig2.update_layout(
                            title_x=0.5,
                            margin=dict(t=50, l=0, r=0, b=0)
                        )
    st.plotly_chart(fig2, use_container_width=True)

    df_RES_ST = df_ST.groupby(by=['COD_ITEM', 'Cd_CA', 'mes'], dropna=False)[['Qtd_TOTAL','VL_TOTAL']].sum().reset_index()
    df_RES_ST['CMU'] = df_RES_ST['VL_TOTAL'] / df_RES_ST['Qtd_TOTAL']
    a.progress(40, "Análise do risco pela estrutura de lançamentos...")
    df_f = df_RES_ST.copy()  
    df_f['OUT_IQR_CA'] = outliers_iqr(df_f, 'Cd_CA', col = 'CMU')
    df_f['OUT_IQR_ITEM'] = outliers_iqr(df_f, 'COD_ITEM', col = 'CMU')
    df_f['OUTLIER'] = df_f['OUT_IQR_ITEM']
    df_risco = score_risco(df_f, col_COD = 'COD_ITEM', col_VL = 'CMU')
    df_risco = clusterizar_itens(df_risco)
    df_f = df_f.merge(df_risco[['COD_ITEM','VL_RISCO','PERFIL_RISCO']], on='COD_ITEM')
    df_f['mes'] = pd.to_datetime(df_f['mes'], format="%Y-%m")
    min_mes = df_f['mes'].min().to_pydatetime()
    max_mes = df_f['mes'].max().to_pydatetime()
    a.progress(50, "Indicadores principais...")
    with st.container():
        st.subheader(f"Indicadores principais {tbl}")
        st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">Na sequência, são apresentados filtros interativos que 
                permitem direcionar a análise para períodos e grupos específicos, bem como indicadores-chave que oferecem 
                uma visão sintética dos principais sinais de risco identificados.
                </p><br>
                """)
        colunas = st.columns([0.2, 0.01, 0.4, 0.01, 0.38], gap='small')
        with colunas[0]:
            cls_sel = st.multiselect(
                                        "TIPO CA",
                                        options=df_RES_ST['Cd_CA'].unique(),
                                        default=df_RES_ST['Cd_CA'].unique()
                                  )
        with colunas[2]:
            mes_range = st.slider(
                                    "Período (meses)",
                                    min_value=min_mes,
                                    max_value=max_mes,
                                    value=(min_mes, max_mes),
                                    format="MMM YYYY",
                                    step=timedelta(days=30)
                                )
        with colunas[4]:
            risco_min = st.slider(
                                    "Risco mínimo",
                                    0.0, 100.0, 70.0
                                 )

        df_filt = df_f[
                            (df_f['Cd_CA'].isin(cls_sel)) &
                            (df_f['mes'].between(*mes_range))
                        ]

        col1, col2, col3 = st.columns(3)

        col1.metric("Itens analisados", df_filt['COD_ITEM'].nunique(), border=True)
        col2.metric("Itens com outlier", df_filt[df_filt['OUTLIER']]['COD_ITEM'].nunique(), border=True)
        col3.metric(
                        "% Outliers",
                        f"{100 * df_filt['OUTLIER'].mean():.2f}%".replace(".",","), 
                        border=True
                    )
        a.progress(70, "Priorizando itens para análise...")
        st.subheader("Itens Prioritários para Análise")
        st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">Se apresenta os itens classificados como 
                    prioritários para análise, com base em critérios objetivos de risco extraídos do comportamento 
                    histórico dos valores, da recorrência de ocorrências atípicas e da variabilidade observada ao longo 
                    do período analisado. Os itens são organizados por nível de risco, permitindo ao analista direcionar 
                    a investigação para aqueles com maior potencial de inconsistência, selecionar os casos mais relevantes 
                    para aprofundamento e reduzir o escopo da análise a um conjunto gerenciável, priorizando esforços 
                    com base em evidências quantitativas.
                </p><br>
                """)
        df_score = (
                        df_filt
                        .groupby(['COD_ITEM', 'Cd_CA'], as_index=False)
                        .agg(
                            risco=('VL_RISCO', 'max'),
                            freq_outlier=('OUTLIER', 'mean'),
                            cmu_medio=('CMU', 'mean'),
                            cmu_max=('CMU', 'max')
                        )
                    )

        df_score = df_score[df_score['risco'] >= risco_min]
        df_score = df_score.sort_values('risco', ascending=False)

        st.dataframe(
                        df_score,
                        use_container_width=True
                    )
        
        a.progress(85, "Construindo representação temporal...")
        st.subheader("Evolução Temporal do Item")
        st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">Apresenta o detalhamento dos lançamentos associados ao item 
                selecionado, permitindo a análise individualizada dos registros que compõem o seu comportamento ao longo 
                do período. O objetivo é possibilitar a verificação da consistência dos valores, a identificação de eventuais 
                erros de lançamento, estornos ou reclassificações, e a compreensão das causas que justificam os sinais de 
                risco observados nas etapas anteriores, servindo como base para a validação das conclusões e para o registro 
                de evidências de fiscalização.
                </p><br>
                """)
        
        item_sel = st.selectbox(
                                    "Selecione o item para análise",
                                    df_score['COD_ITEM'].unique()
                                )

        df_item = df_filt[df_filt['COD_ITEM'] == item_sel]
        df_item = df_item.sort_values(by='mes')
        fig_item = px.line(
                                df_item,
                                x='mes',
                                y='CMU',
                                color='OUTLIER',
                                markers=True,
                                title=f"Evolução do CMU – Item {item_sel}"
                            )

        fig_item.update_xaxes(tickformat="%b/%y")
        st.plotly_chart(fig_item, use_container_width=True)
        a.progress(90, "Detalhando lançamentos...")
        st.subheader("Lançamentos do Item")
        st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">Se apresenta o detalhamento dos lançamentos associados ao 
                item selecionado, permitindo a análise individualizada dos registros que compõem o seu comportamento ao 
                longo do período. O objetivo é possibilitar a verificação da consistência dos valores, a identificação 
                de eventuais erros de lançamento, estornos ou reclassificações, e a compreensão das causas que 
                justificam os sinais de risco observados nas etapas anteriores, servindo como base para a validação 
                das conclusões e para o registro de evidências de fiscalização.
                </p><br>
                """)
        st.dataframe(
                        df_item,
                        use_container_width=True
                    )
        a.progress(91, "Box-plot dos itens com maior risco...")
        st.subheader("Box-Plot dos itens com maior risco")
        st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">A análise a seguir tem como objetivo identificar e 
                    contextualizar comportamentos atípicos nos registros, apoiando a seleção de itens que demandam 
                    verificação detalhada com base em evidências quantitativas.
                </p><br>
                """)
        top_itens = (
                        df_f
                        .sort_values('VL_RISCO', ascending=False)
                        .head(100)['COD_ITEM']
                    )
        
        df_box = df_filt[df_filt['COD_ITEM'].isin(top_itens)]
        
        fig_box = px.box(
                            df_box,
                            x='CMU',
                            y='COD_ITEM',
                            orientation='h',
                            points='outliers',   # mostra só outliers
                            title="Distribuição de CMU por Item (Box-plot)"
                        )

        fig_box.update_layout(
                                height=600,
                                yaxis_title="Item",
                                xaxis_title="CMU (R$)"
                            )
        
        df_out = df_box[df_box['OUTLIER']]

        fig_box.add_scatter(
                                x=df_out['CMU'],
                                y=df_out['COD_ITEM'],
                                mode='markers',
                                marker=dict(
                                    color='red',
                                    size=6,
                                    symbol='x'
                                ),
                                name='Outlier (modelo)'
                            )

        st.plotly_chart(fig_box, use_container_width=True)

    a.progress(92, "Alterando tipo de CA para tipo de TI...")
    df_RES_ST = df_ST.groupby(by=['COD_ITEM', 'Txt_TI', 'mes'], dropna=False)[['Qtd_TOTAL','VL_TOTAL']].sum().reset_index()
    df_RES_ST['CMU'] = df_RES_ST['VL_TOTAL'] / df_RES_ST['Qtd_TOTAL']
    a.progress(93, "Análise do risco pela estrutura de lançamentos...")
    df_f = df_RES_ST.copy()  
    df_f['OUT_IQR_CA'] = outliers_iqr(df_f, 'Txt_TI', col = 'CMU')
    df_f['OUT_IQR_ITEM'] = outliers_iqr(df_f, 'COD_ITEM', col = 'CMU')
    df_f['OUTLIER'] = df_f['OUT_IQR_ITEM']
    df_risco = score_risco(df_f, col_COD = 'COD_ITEM', col_VL = 'CMU')
    df_risco = clusterizar_itens(df_risco)
    df_f = df_f.merge(df_risco[['COD_ITEM','VL_RISCO','PERFIL_RISCO']], on='COD_ITEM')
    df_f['mes'] = pd.to_datetime(df_f['mes'], format="%Y-%m")
    min_mes = df_f['mes'].min().to_pydatetime()
    max_mes = df_f['mes'].max().to_pydatetime()
    a.progress(94, "Indicadores principais...")
    with st.container():
        st.subheader(f"Indicadores principais {tbl}, considerando TI ao invés de tipo de CA")
        st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">Na sequência, são apresentados filtros interativos que 
                permitem direcionar a análise para períodos e grupos específicos, bem como indicadores-chave que oferecem 
                uma visão sintética dos principais sinais de risco identificados.
                </p><br>
                """)
        colunasTI = st.columns([0.2, 0.01, 0.4, 0.01, 0.38], gap='small')
        with colunasTI[0]:
            cls_selTI = st.multiselect(
                                        "Txt_TI",
                                        options=df_RES_ST['Txt_TI'].unique(),
                                        default=df_RES_ST['Txt_TI'].unique(),
                                        
                                  )
        with colunasTI[2]:
            mes_rangeTI = st.slider(
                                    "Período (meses)",
                                    min_value=min_mes,
                                    max_value=max_mes,
                                    value=(min_mes, max_mes),
                                    format="MMM YYYY",
                                    step=timedelta(days=30),
                                    key="slider_3"
                                )
        with colunasTI[4]:
            risco_minTI = st.slider(
                                    "Risco mínimo",
                                    0.0, 100.0, 70.0,
                                    key="slider_4"
                                 )

        df_filt = df_f[
                            (df_f['Txt_TI'].isin(cls_selTI)) &
                            (df_f['mes'].between(*mes_rangeTI))
                        ]

        col1TI, col2TI, col3TI = st.columns(3)

        col1TI.metric("Itens analisados", df_filt['COD_ITEM'].nunique(), border=True)
        col2TI.metric("Itens com outlier", df_filt[df_filt['OUTLIER']]['COD_ITEM'].nunique(), border=True)
        col3TI.metric(
                        "% Outliers",
                        f"{100 * df_filt['OUTLIER'].mean():.2f}%".replace(".",","), 
                        border=True
                    )
        a.progress(95, "Priorizando itens para análise...")
        st.subheader("Itens Prioritários para Análise, considerando TI ao invés de tipo de CA")
        st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">Se apresenta os itens classificados como 
                    prioritários para análise, com base em critérios objetivos de risco extraídos do comportamento 
                    histórico dos valores, da recorrência de ocorrências atípicas e da variabilidade observada ao longo 
                    do período analisado. Os itens são organizados por nível de risco, permitindo ao analista direcionar 
                    a investigação para aqueles com maior potencial de inconsistência, selecionar os casos mais relevantes 
                    para aprofundamento e reduzir o escopo da análise a um conjunto gerenciável, priorizando esforços 
                    com base em evidências quantitativas.
                </p><br>
                """)
        df_score = (
                        df_filt
                        .groupby(['COD_ITEM', 'Txt_TI'], as_index=False)
                        .agg(
                            risco=('VL_RISCO', 'max'),
                            freq_outlier=('OUTLIER', 'mean'),
                            cmu_medio=('CMU', 'mean'),
                            cmu_max=('CMU', 'max')
                        )
                    )

        df_score = df_score[df_score['risco'] >= risco_min]
        df_score = df_score.sort_values('risco', ascending=False)

        st.dataframe(
                        df_score,
                        use_container_width=True
                    )
        
        a.progress(97, "Construindo representação temporal...")
        st.subheader("Evolução Temporal do Item")
        st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">Apresenta o detalhamento dos lançamentos associados ao item 
                selecionado, permitindo a análise individualizada dos registros que compõem o seu comportamento ao longo 
                do período. O objetivo é possibilitar a verificação da consistência dos valores, a identificação de eventuais 
                erros de lançamento, estornos ou reclassificações, e a compreensão das causas que justificam os sinais de 
                risco observados nas etapas anteriores, servindo como base para a validação das conclusões e para o registro 
                de evidências de fiscalização.
                </p><br>
                """)
        
        item_sel = st.selectbox(
                                    "Selecione o item para análise",
                                    df_score['COD_ITEM'].unique()
                                )

        df_item = df_filt[df_filt['COD_ITEM'] == item_sel]
        df_item = df_item.sort_values(by='mes')
        fig_itemTI = px.line(
                                df_item,
                                x='mes',
                                y='CMU',
                                color='OUTLIER',
                                markers=True,
                                title=f"Evolução do CMU – Item {item_sel}"
                            )

        fig_itemTI.update_xaxes(tickformat="%b/%y")
        st.plotly_chart(fig_itemTI, use_container_width=True)
        a.progress(98, "Detalhando lançamentos...")
        st.subheader("Lançamentos do Item")
        st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">Se apresenta o detalhamento dos lançamentos associados ao 
                item selecionado, permitindo a análise individualizada dos registros que compõem o seu comportamento ao 
                longo do período. O objetivo é possibilitar a verificação da consistência dos valores, a identificação 
                de eventuais erros de lançamento, estornos ou reclassificações, e a compreensão das causas que 
                justificam os sinais de risco observados nas etapas anteriores, servindo como base para a validação 
                das conclusões e para o registro de evidências de fiscalização.
                </p><br>
                """)
        st.dataframe(
                        df_item,
                        use_container_width=True
                    )
        a.progress(99, "Box-plot dos itens com maior risco...")
        st.subheader("Box-Plot dos itens com maior risco")
        st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">A análise a seguir tem como objetivo identificar e 
                    contextualizar comportamentos atípicos nos registros, apoiando a seleção de itens que demandam 
                    verificação detalhada com base em evidências quantitativas.
                </p><br>
                """)
        top_itens = (
                        df_f
                        .sort_values('VL_RISCO', ascending=False)
                        .head(100)['COD_ITEM']
                    )
        
        df_box = df_filt[df_filt['COD_ITEM'].isin(top_itens)]
        
        fig_boxTI = px.box(
                            df_box,
                            x='CMU',
                            y='COD_ITEM',
                            orientation='h',
                            points='outliers',
                            title="Distribuição de CMU por Item (Box-plot)"
                        )

        fig_boxTI.update_layout(
                                height=600,
                                yaxis_title="Item",
                                xaxis_title="CMU (R$)"
                            )
        
        df_out = df_box[df_box['OUTLIER']]

        fig_boxTI.add_scatter(
                                x=df_out['CMU'],
                                y=df_out['COD_ITEM'],
                                mode='markers',
                                marker=dict(
                                    color='red',
                                    size=6,
                                    symbol='x'
                                ),
                                name='Outlier (modelo)'
                            )

        st.plotly_chart(fig_boxTI, use_container_width=True)
        a.empty()

@monitor_completo(st.session_state.LOGGER)
def anl_investimentos(st=None, depr = True):
    with open("tabelas/estilo_001.css") as f:
        css = f.read()
    st.html(f"""
                    <style>
                    {css}    
                    </style>
                """)
    if st==None:
        return
    if 'tra_dir' in st.session_state:
        local = st.session_state.tra_dir
        empresa = st.session_state.nm_empr
        ano = st.session_state.dt_fim.year

        bd = sl.connect(f'{local}\BD_LOCAL\{empresa}_{ano}.db')
        if (existe_tabela('AIS', bd)):
            cols = st.columns([1,5,1], gap='small')
            with cols[1]: 
                dt_ARQ = max_arq('AIS', bd, empresa)
                SQLq = f"""
                            SELECT 
                                *
                            FROM 
                                AIS t1 
                            WHERE 
                                t1.dt_ARQ = ?
                        """
                AIS = carga_sqlite_cache(SQLq, bd, (dt_ARQ,))
                tbl_CNTB = pd.read_csv("tabelas/tbl_CNTB.csv",sep="|",decimal=',',on_bad_lines='skip',
                            encoding="Latin-1",dtype=str);
                
                AIS = AIS.merge(tbl_CNTB, how='left', on='Cd_CC')
                dic_Q1A = {
                            '1.1' : (AIS['Cd_CC'].astype(str).isin(['123310101','123310401','123320101',
                                                                        '123320401','123330101','123330401',
                                                                        '123340101','123350101']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Servidões permanentes')),
                            '1.2' : (AIS['Cd_CC'].astype(str).isin(['123310103','123310403','123320103',
                                                                        '123320403','123330103','123330403',
                                                                        '123340103','123350103']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Softwares')),
                            '1.3' : (AIS['Cd_CC'].astype(str).isin(['123310199','123310499','123320199',
                                                                        '123320499','123330199','123330499',
                                                                        '123340199','123350199']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Outros')),
                            '2.1' : (AIS['Cd_CC'].astype(str).isin(['123210101','123210402']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Terrenos')),                                             
                            '2.2' : (AIS['Cd_CC'].astype(str).isin(['123220101','123220402','123230101','123230402']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Terrenos')),
                            '2.3' : (AIS['Cd_CC'].astype(str).isin(['123240101']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Terrenos')),
                            '2.4' : (AIS['Cd_CC'].astype(str).isin(['123250101']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Terrenos')),
                            '3' : (AIS['Cd_CC'].astype(str).isin(['123210102','123210402']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Reservatórios, barragens e adutoras')),
                            '4.1' : (AIS['Cd_CC'].astype(str).isin(['123210103','123210403']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Edificações, obras civis e benfeitorias')),
                            '4.2' : (AIS['Cd_CC'].astype(str).isin(['123220103','123220403','123230103','123230403']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Edificações, obras civis e benfeitorias')),
                            '4.3' : (AIS['Cd_CC'].astype(str).isin(['123240103']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Edificações, obras civis e benfeitorias')),
                            '4.4' : (AIS['Cd_CC'].astype(str).isin(['123250103']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Edificações, obras civis e benfeitorias')),
                            '5.1' : (AIS['Cd_CC'].astype(str).isin(['123210104','123210404']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Máquinas e equipamentos')),
                            '5.2' : (AIS['Cd_CC'].astype(str).isin(['123220104','123220404','123230104','123230404']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Máquinas e equipamentos')),
                            '5.3' : (AIS['Cd_CC'].astype(str).isin(['123240104']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Máquinas e equipamentos')),
                            '5.4' : (AIS['Cd_CC'].astype(str).isin(['123250104']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Máquinas e equipamentos')),
                            '6.1' : (AIS['Cd_CC'].astype(str).isin(['123210105','123210405']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Veículos')),
                            '6.2' : (AIS['Cd_CC'].astype(str).isin(['123220105','123220405','123230105','123230405']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Veículos')),
                            '6.3' : (AIS['Cd_CC'].astype(str).isin(['123240105']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Veículos')),
                            '6.4' : (AIS['Cd_CC'].astype(str).isin(['123250105']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Veículos')),
                            '7.1' : (AIS['Cd_CC'].astype(str).isin(['123210106','123210406']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Móveis e utensílios')),
                            '7.2' : (AIS['Cd_CC'].astype(str).isin(['123220106','123220406','123230106','123230406']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Móveis e utensílios')),
                            '7.3' : (AIS['Cd_CC'].astype(str).isin(['123240106']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Móveis e utensílios')),
                            '7.4' : (AIS['Cd_CC'].astype(str).isin(['123250106']) &
                                                                        (AIS['Nm_RZ_ANAL'].astype(str) == 'Móveis e utensílios'))}
                
                for Cd_1A, crit in dic_Q1A.items():
                    AIS.loc[crit, 'Cd_Q1A'] = Cd_1A 

                AIS['VL_VOC'] = pd.to_numeric(AIS['VL_VOC'], errors='coerce').fillna(0)
                AIS['VL_DEP_ACUM'] = pd.to_numeric(AIS['VL_DEP_ACUM'], errors='coerce').fillna(0)
                AIS['Qtd_AIS'] = pd.to_numeric(AIS['Qtd_AIS'], errors='coerce').fillna(0)
                AIS['Dt_Imob'] = pd.to_datetime(AIS['Dt_Imob'], format='ISO8601', errors='coerce')
                AIS['ANO'] = AIS['Dt_Imob'].dt.year
                AIS['Nm_RZ_SINT'] = AIS['Nm_RZ_SINT'].str.replace('''Linhas, Redes e Subestações''', 'LD/RD/SE')
                AIS['Nm_RZ_SINT'] = AIS['Nm_RZ_SINT'].str.replace('''Sistema de transmissão associado''', 'STA')
                AIS['Nm_RZ_ANAL'] = AIS['Nm_RZ_ANAL'].str.replace('''Edificações, obras civis e benfeitorias''', 'EDIF/OC/BENF')
                AIS['Nm_RZ_ANAL'] = AIS['Nm_RZ_ANAL'].str.replace('''Máquinas e equipamentos''', 'MAQ/EQUIP')
                AIS['Nm_RZ_ANAL'] = AIS['Nm_RZ_ANAL'].str.replace('''Servidões permanentes''', 'SERVIDAO')
                AIS['Nm_RZ_ANAL'] = AIS['Nm_RZ_ANAL'].str.replace('''Móveis e utensílios''', 'MOV/UTEN')

                tabela = AIS[AIS['FLG_PER'].astype(str)=='1'].pivot_table(index='Nr_TI', 
                            columns=['Nm_ATVD', 'Nm_RZ_SINT', 'Nm_RZ_ANAL','Nm_CLASS'], 
                            values='VL_VOC', aggfunc='sum').fillna(0)
                tabela.to_sql("TBL_AIS_RELATORIO", bd, if_exists='replace')
                def formatar_br(valor):
                    if pd.isna(valor):
                        return ""
                    elif isinstance(valor, str):
                        return valor
                    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                tabela1 = tabela.applymap(formatar_br).style.set_properties(**{'text-align': 'right'})
                st.html(f"""<h1>Painel para Análises</h1>
                            <h2>AIS</h2>
                            <p  style="text-align: justify;text-indent: 40px">A partir do AIS, referência {AIS['Dt_Imob'].max().strftime('%d/%m/%Y')}, 
                            fizemos a filtragem do investimento incremental e segregamos por tipologia, TI, e por grupo de atividade,
                            segmento e tipo de investimento:</p>
                            """)
                st.write(tabela1.to_html(escape=False), unsafe_allow_html=True)

                def dataframe_to_image(df, output_path, nome = None):
                    if nome == 'GR_ANO':
                        df_aux = df.reset_index()
                        segunda_col = df_aux.columns[1]
                        df_aux[segunda_col] = df_aux[segunda_col].apply(lambda x: str(x).ljust(110, ' '))
                        df = df_aux.set_index(list(df.index.names))
                        df = df.applymap(formatar_br).style.set_table_styles([
                                            {   
                                                'selector': 'td',
                                                'props': [
                                                            ('text-align', 'right')
                                                        ]
                                            }
                                        ])

                    try:
                        dfi.export(df, output_path, table_conversion='matplotlib')
                        return True
                    except Exception as e:
                        print(f"Erro ao exportar imagem: {e}")
                        return False
                dir_FIG = rf"{local}/RELATORIOS/figuras"
                dataframe_to_image(tabela1, rf"{dir_FIG}/tabela_ais_incremental_grupo_contas.png", 'GR_CNT')

                TI = pd.read_csv("tabelas/TBL_TI.csv",sep="|",decimal=',',on_bad_lines='skip',encoding="Latin-1",dtype=str)
                

                AIS = AIS.merge(TI.rename(columns={'Id_TI' : 'Nr_TI'}), how='left', on='Nr_TI')
                AIS['Txt_Desc'] = AIS['Txt_Desc'].str.replace('''Sistemas de telecomunicação, telecontrole, teleprocessamento, proteção, controle e supervisão - Automação; Cada sistema de comunicação (exceto o sistema de ondas portadoras Carrier que integra as ODI de Subestações e os sistemas de comunicação que integram as ODI Adm. Central e Adm. Específica)''', 'Sistemas de Automação, de Telecomunicação')
                AIS['Txt_Desc'] = AIS['Txt_Desc'].str.replace('''Reserva imobilizada (exceto equipamentos reservas exclusivos de usinas e subestações que integram ODI específicas)''', 'Reserva Imobilizada')
                
                tabela = AIS[AIS['FLG_PER'].astype(str)=='1'].pivot_table(index=['Nr_TI','Txt_Desc'], 
                            columns=['ANO'], 
                            values='VL_VOC', aggfunc='sum').fillna(0)
                
                tabela1 = tabela.applymap(formatar_br).style.set_properties(**{'text-align': 'right'})
                st.html(f"""
                            <p  style="text-align: justify;text-indent: 40px">Também segregamos por tipologia, TI, e por ano:</p>
                            """)
                st.write(tabela1.to_html(escape=False), unsafe_allow_html=True)
                dataframe_to_image(tabela, rf"{dir_FIG}/tabela_ais_incremental_ano.png", 'GR_ANO')


                tabela = AIS[AIS['FLG_PER'].astype(str)=='1'].pivot_table(index=['Nr_TUC'], 
                            columns=['ANO'], 
                            values='VL_VOC', aggfunc='sum').fillna(0)
                soma_total = tabela.sum(axis=1)
                tabela['TOTAL'] = soma_total
                tabela = tabela.sort_values(by='TOTAL', ascending=False)

                tabela1 = tabela.applymap(formatar_br).style.set_properties(**{'text-align': 'right'})
                st.html(f"""
                            <p  style="text-align: justify;text-indent: 40px">Também segregamos por unidade de cadastro, UC, 
                        reordenando das de maior para menor investimento:</p>
                            """)
                st.write(tabela1.to_html(escape=False), unsafe_allow_html=True)
                dataframe_to_image(tabela1, rf"{dir_FIG}/tabela_ais_incremental_UC.png")

                if existe_tabela("BASE_INCR_COMP_A1", bd) and (st.session_state.dt_fim < date.today()):
                    INCR = carga_sqlite_cache("SELECT * FROM BASE_INCR_COMP_A1", bd)
                    INCR['Dt_Imob'] = pd.to_datetime(INCR['Dt_Imob'], errors='coerce')
                    INCR['Dt_REF_DADOS'] = pd.to_datetime(INCR['Dt_REF_DADOS'], errors='coerce')
                    INCR['ANO'] = INCR['Dt_Imob'].dt.year
                    INCR['VL_VOCa'] = INCR['VL_VOC'] * INCR['FA_IPCA']
                    d1 = pd.to_datetime(INCR['Dt_REF_DADOS'].max()).replace(day=1)     
                else:
                    if (not existe_tabela('TBL_AIS_INCR_SIM', bd)):
                        DD_GRP = pd.read_csv("tabelas/TBL_GRUPOS.csv",sep="|",decimal=',',on_bad_lines='skip',
                                    encoding="Latin-1");

                        DD_GRP = DD_GRP[DD_GRP['Cd_ANEEL'] == bsc_cd_aneel(empresa)]
                        SQLq = f"""
                                    SELECT 
                                        t1.COD_ITEM, t1.DESCR_ITEM AS txt_Desc_Bem
                                    FROM 
                                        LST_MAT t1 
                                    WHERE 
                                        dt_ARQ = ?;
                                """
                        LST_MAT_SDI = imp_tbl_forma_001('LST_MAT', SQLq = SQLq, con = bd, st=st, Empresa=empresa)

                        AIS = AIS.merge(LST_MAT_SDI, how='left', on = 'txt_Desc_Bem')

                        AIS = AIS.rename(columns = {'Txt_Class' : 'Cd_TI'})
                        for i in range(len(DD_GRP)):
                            AIS.loc[AIS['Dt_Imob'] >= DD_GRP.iloc[i,2],'Nr_GRUPO']=DD_GRP.iloc[i,1]

                        LST_TUC = AIS[['Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                        'Nr_A3','Nr_A4','Nr_A5','Nr_A6']].drop_duplicates()
                        LST_TUC['Cd_SISBASE'] = ''
                        LST_TUC = tst_cod_sisbase(LST_TUC, st.session_state.dt_fim)
                        LST_TUC = LST_TUC.drop(columns=['Cd_SISBASE','TESTE_Cd'])
                        LST_TUC.loc[LST_TUC['Cd_SISBASE_SFF']=='ND', 'Cd_FOR_COGE_SFF'] = 'FCM0403'
                        LST_TUC.loc[LST_TUC['Cd_SISBASE_SFF']=='ND', 'Nr_FAM_SFF'] = 'ND'

                        AIS = AIS.merge(LST_TUC[['Nr_TI','Nr_TUC','Nr_A1','Nr_A2','Nr_A3',
                                                    'Nr_A4','Nr_A5','Nr_A6','Cd_SISBASE_SFF',
                                                    'Cd_FOR_COGE_SFF','Nr_FAM_SFF']], 
                                            how='left', 
                                            on=['Nr_TI','Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6'])

                        dt_ref_base = pd.to_datetime(AIS['Dt_Ref_AIS']).max().to_period('M').to_timestamp()
                        AIS = AIS.assign(
                                                DT_REF_BASE=dt_ref_base,
                                                Dt_Imob = pd.to_datetime(AIS['Dt_Imob']).values.astype('datetime64[M]'),
                                                DT_IMB_BASE = pd.to_datetime(AIS['Dt_Imob']).values.astype('datetime64[M]')  
                                            )
                        ipca = busca_ipca()[['Dt_REF', 'Nr_IPCA']].rename(columns={'Dt_REF': 'DT_CMPT'})
                        ipca.columns=['DT_IMB_BASE','Nr_IPCA_REF_IMB']
                        ipca['DT_IMB_BASE'] = ipca['DT_IMB_BASE'].to_numpy().astype('datetime64[M]')
                        AIS['Nr_IPCA_REF_BASE'] = ipca.loc[ipca['DT_IMB_BASE'] == dt_ref_base, 'Nr_IPCA_REF_IMB'].iloc[-1]
                        AIS = AIS.merge(ipca, how='left', on='DT_IMB_BASE')

                        #Em função de bases desblindadas é necessário fixar o IPCA na data de fim de correção de balanços.
                        AIS.loc[(AIS['DT_IMB_BASE'] < pd.to_datetime('01/01/1996')) 
                                    & (AIS['Nr_IPCA_REF_IMB'].isnull()),'Nr_IPCA_REF_IMB'] = 1260.9
                        AIS['FA_IPCA'] = AIS['Nr_IPCA_REF_BASE']/AIS['Nr_IPCA_REF_IMB']
                        AIS.to_sql("TBL_AIS_CMP_SIM", bd, if_exists='replace', index=False)
                    
                        INCR = AIS[AIS['FLG_PER'].astype(str)=='1'].copy()

                        LST_SISTEMAS = ['100', '105', '110', '112', '115', '140', '145', '150', '155', '170', '175', '185', '205', '215', '220', '225', '240', '245', '260', 
                                '275', '280', '285', '300', '320', '335', '350', '355', '360', '365', '370', '375', '380', '385', '390', '395', '400', '405', '410', 
                                '415', '420', '425', '430', '435', '440', '445', '450', '455', '460', '465', '470', '475', '480', '485', '490', '500', '505', '510', 
                                '515', '520', '525', '530', '550', '555', '585', '590', '595', '600', '610']
                        INCR['FLG_EXC'] = np.where(INCR['Nr_TUC'].isin(LST_SISTEMAS),
                                                True,
                                                False)

                        SQLq = f"""
                                    SELECT 
                                        t1.Cd_SubODI, 
                                        t1.COD_ITEM,
                                        t1.Nr_TI,
                                        t1.Nr_TUC,
                                        t1.Nr_A1,
                                        t1.Nr_A2,
                                        t1.Nr_A3,
                                        t1.Nr_A4,
                                        t1.Nr_A5,
                                        t1.Nr_A6,
                                        t1.Unidade AS Cd_UND_AIS,
                                        SUM(
                                            CASE 
                                                WHEN Qtd LIKE '%,%' THEN CAST(REPLACE(Qtd, ',', '.') AS REAL)
                                                ELSE CAST(Qtd AS REAL)
                                            END
                                        ) AS Qtd, 
                                        SUM(
                                            CASE 
                                                WHEN VL_tot LIKE '%,%' THEN CAST(REPLACE(VL_tot, ',', '.') AS REAL)
                                                ELSE CAST(VL_tot AS REAL)
                                            END
                                        ) AS VL_tot 
                                    FROM 
                                        ROA t1 
                                    WHERE 
                                        dt_ARQ = ? AND t1.Cd_NG = '1'
                                    GROUP BY 
                                        t1.Cd_SubODI, 
                                        t1.COD_ITEM,
                                        t1.Nr_TI,
                                        t1.Nr_TUC,
                                        t1.Nr_A1,
                                        t1.Nr_A2,
                                        t1.Nr_A3,
                                        t1.Nr_A4,
                                        t1.Nr_A5,
                                        t1.Nr_A6,
                                        t1.Unidade;
                                """
                        df_VL_VF_ROA = imp_tbl_forma_001('ROA', SQLq = SQLq, con = bd, st=st, Empresa=empresa)
                        SQLq = f"""
                                    SELECT 
                                        t1.COD_ITEM, t1.DESCR_ITEM
                                    FROM 
                                        LST_MAT t1 
                                    WHERE 
                                        dt_ARQ = ?;
                                """
                        LST_MAT_SDI = imp_tbl_forma_001('LST_MAT', SQLq = SQLq, con = bd, st=st, Empresa=empresa)
                        df_VL_VF_ROA = df_VL_VF_ROA.fillna('0').merge(LST_MAT_SDI, how='left', on = 'COD_ITEM')
                        
                        VL_VF_ROA = (df_VL_VF_ROA
                                    .groupby(by=['Cd_SubODI','Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                                'Nr_A3','Nr_A4','Nr_A5','Nr_A6'])[['Qtd', 'VL_tot']]
                                    .sum()
                                    .reset_index())
                        
                        INCR = INCR.merge(VL_VF_ROA, how='left', on = ['Cd_SubODI','Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                                'Nr_A3','Nr_A4','Nr_A5','Nr_A6'], suffixes=("_UNT1", "_UNT2"))
                        
                        VL_VF_ROA = (df_VL_VF_ROA
                                    .groupby(by=['Nr_TUC','Nr_A1','Nr_A2',
                                                'Nr_A3','Nr_A4','Nr_A5','Nr_A6'])[['Qtd', 'VL_tot']]
                                    .sum()
                                    .reset_index())
                        
                        INCR = INCR.merge(VL_VF_ROA, how='left', on = ['Nr_TUC','Nr_A1','Nr_A2',
                                                'Nr_A3','Nr_A4','Nr_A5','Nr_A6'], suffixes=("_UNT1", "_UNT2"))

                        INCR['Qtd_ROA'] = np.where(INCR['VL_tot_UNT1'].notnull(),
                                                            INCR['Qtd_UNT1'],
                                                            INCR['Qtd_UNT2'])
                        
                        condicoes = [
                                        INCR['VL_tot_UNT1'].notnull() & (INCR['Qtd_ROA'] > 0),
                                        INCR['VL_tot_UNT2'].notnull() & (INCR['Qtd_ROA'] > 0),
                                    ]

                        escolhas = [
                                        INCR['VL_tot_UNT1'] / INCR['Qtd_UNT1'],
                                        INCR['VL_tot_UNT2'] / INCR['Qtd_UNT2'],

                                    ]
                        escolhas1 = [
                                        'MTD1',
                                        'MTD2',
                                    ]
                        INCR['MTD_VF'] = np.select(condicoes, escolhas1, default='')
                        INCR['VL_VOC_VF_UNT'] = np.select(condicoes, escolhas, default=0)
                        
                        SQLq = f"""
                                    SELECT 
                                        t1.Cd_SubODI, t1.Cd_NG, 
                                        SUM(
                                            CASE 
                                                WHEN VL_tot LIKE '%,%' THEN CAST(REPLACE(VL_tot, ',', '.') AS REAL)
                                                ELSE CAST(VL_tot AS REAL)
                                            END
                                        ) AS VL_TOT
                                    FROM 
                                        ROA t1 
                                    WHERE 
                                        t1.dt_ARQ = ?
                                    GROUP BY
                                        t1.Cd_SubODI, t1.Cd_NG
                                """
                        ROA_JOA = imp_tbl_forma_001('ROA', SQLq = SQLq, con = bd, st=st, Empresa=empresa)
                        for nm in ROA_JOA.columns.to_list():
                            if ROA_JOA[nm].dtype == 'object' and nm[:2].upper() in ["VL"]:
                                ROA_JOA[nm] = pd.to_numeric(ROA_JOA[nm].astype(str).str.replace(',','.'), 
                                                                            errors='coerce',
                                                                            downcast='float')
                        ROA_JOA = (ROA_JOA
                                .pivot_table(values="VL_TOT", index=["Cd_SubODI"], 
                                            columns="Cd_NG", aggfunc="sum", dropna=False, fill_value=0)
                                .rename_axis(columns=None)
                                .reset_index())
                        for n in range(1, 7):
                            if f"{n}" not in ROA_JOA.columns:
                                ROA_JOA[f"{n}"] = 0
                        ROA_JOA = ROA_JOA.rename(columns = {'1' : 'VL_UC_TOT', '2' : 'VL_COM_TOT', '3' : 'VL_MOP_TOT',
                                                    '4' : 'VL_ST_TOT', '5' : 'VL_JOA_TOT', '6' : 'VL_OUT_TOT'})
                        ROA_JOA['VL_TOT'] = ROA_JOA[['VL_UC_TOT','VL_COM_TOT','VL_MOP_TOT','VL_ST_TOT','VL_JOA_TOT','VL_OUT_TOT']].sum(axis=1)
                        ROA_JOA['Pct_JOA_ROA'] = (ROA_JOA['VL_JOA_TOT'] / (ROA_JOA['VL_TOT'])).fillna(0)
                        ROA_JOA['Pct_COM_ROA'] = (ROA_JOA['VL_COM_TOT'] / (ROA_JOA['VL_TOT'])).fillna(0)
                        INCR = INCR.merge(ROA_JOA[['Cd_SubODI','Pct_COM_ROA','Pct_JOA_ROA']], how='left', on = ['Cd_SubODI'])
                        
                        INCR['VL_VOC_VF_UNT'] = np.maximum(INCR['VL_VOC_VF_UNT'].fillna(0), 0)
                        INCR['VL_VOC_VF'] = np.maximum(INCR['VL_VOC_VF_UNT'] * INCR['Qtd_AIS'], 0)
                        INCR['VL_VOC_COM'] = np.maximum(INCR['VL_VOC'] * ROA_JOA['Pct_COM_ROA'], 0)
                        INCR['VL_VOC_CA'] = np.maximum(INCR['VL_VOC'] * (1 - ROA_JOA['Pct_JOA_ROA']) - INCR['VL_VOC_VF'] - INCR['VL_VOC_COM'], 0)
                        INCR['VL_VOC_JOA'] = np.maximum(INCR['VL_VOC'] * ROA_JOA['Pct_JOA_ROA'], 0)
                        INCR['VL_VOC_COM_CA_IMB'] = INCR[['VL_VOC_COM', 'VL_VOC_CA']].sum(axis=1)
                        
                        INCR['VL_JOA_IMB_AT'] = INCR['VL_VOC_JOA'] * INCR['FA_IPCA']
                        INCR.loc[INCR['Nr_TI'].isin(['93', '96']), 'VL_JOA_IMB_AT'] = 0
                        INCR['VL_VOC_COM_CA_IMB_AT'] = INCR['VL_VOC_COM_CA_IMB'] * INCR['FA_IPCA']
                        INCR['VL_VOC_VF_IMB_AT'] = INCR['VL_VOC_VF'] * INCR['FA_IPCA']

                        INCR['VL_VOCsjoa_IMB_AT'] = (
                                                    INCR['VL_VOC_COM_CA_IMB_AT'] + INCR['VL_VOC_VF_IMB_AT'] + INCR['VL_JOA_IMB_AT']
                                                )
                        
                        INCR = INCR.rename(columns={'COD_ITEM_x' : 'COD_ITEM'})
                        tbl_AX = INCR[INCR['COD_ITEM'].notnull() & (INCR['Cd_UC'] != 'UAR')][['COD_ITEM','VL_VOC_VF_UNT','FA_IPCA','Qtd_AIS']].copy()
                        tbl_AX['VL_VF'] = tbl_AX['VL_VOC_VF_UNT'] * tbl_AX['FA_IPCA']
                        def limite_tukey_inferior(coluna):
                            q1 = coluna.quantile(0.25)
                            q3 = coluna.quantile(0.75)
                            iqr = q3 - q1
                            return q1 - 1.5 * iqr
                        def limite_tukey_superior(coluna):
                            q1 = coluna.quantile(0.25)
                            q3 = coluna.quantile(0.75)
                            iqr = q3 - q1
                            return q3 + 1.5 * iqr
                        
                        tbl_AX['limite_inf_grupo'] = tbl_AX.groupby('COD_ITEM')['VL_VF'].transform(limite_tukey_inferior)
                        tbl_AX['limite_sup_grupo'] = tbl_AX.groupby('COD_ITEM')['VL_VF'].transform(limite_tukey_superior)
                        tbl_AX['Outlier_Inferior'] = (tbl_AX['VL_VF'] > tbl_AX['limite_sup_grupo']) | (tbl_AX['VL_VF'] < tbl_AX['limite_inf_grupo'])
                        df_limpo = tbl_AX[~tbl_AX['Outlier_Inferior']].copy()
                        df_limpo['produto_ponderado'] = df_limpo['VL_VF'] * df_limpo['Qtd_AIS']
                        resultado = df_limpo.groupby('COD_ITEM').apply(
                                        lambda x: x['produto_ponderado'].sum() / x['Qtd_AIS'].sum()
                                    ).reset_index(name='VL_VF_POND')

                        INCR = INCR.merge(resultado, how='left', on = 'COD_ITEM')

                        crit = (INCR['Cd_SISBASE_SFF'] != 'ND') & (INCR['VL_VF_POND']==0)
                        INCR.loc[crit, 'VL_VOCsjoa_IMB_AT'] = (
                                                    INCR['VL_VOC'] * (1 - INCR['Pct_JOA_ROA']) * INCR['FA_IPCA']
                                                )

                        BPR=pd.read_csv('tabelas/tbl_BPR_DADOS.csv',sep="|",decimal=',',encoding="Latin-1",dtype=str);
                        BPR['DT_REF']=pd.to_datetime(BPR['DT_REF'])
                        BPR['DT_APL']=pd.to_datetime(BPR['DT_APL'])
                        for c in ['Nr_GRUPO','VL_COM','VL_CA']:
                            BPR[c]=pd.to_numeric(BPR[c].str.replace(',','.'), errors='coerce')
                            BPR[c] = BPR[c].fillna(0)
                        BPR = BPR.rename(columns={'Cd_SISBASE' : 'Cd_SISBASE_SFF'})

                        BPR_AX = BPR[['DT_REF', 'DT_APL']].drop_duplicates()
                        teste = INCR[['DT_IMB_BASE']].reset_index()
                        dt_ref_list = BPR['DT_REF'].drop_duplicates().sort_values().tolist()
                        for i in dt_ref_list:
                            ia = BPR_AX.loc[BPR_AX['DT_REF'] == i, 'DT_APL'].values  
                            if ia.size > 0:  
                                teste.loc[((teste['DT_IMB_BASE'] - ia[0]) / np.timedelta64(1, 'D') >= 0), 'DT_REF'] = i

                        DT_BPR = teste[['DT_IMB_BASE','DT_REF']].drop_duplicates()
                        INCR = INCR.merge(DT_BPR, how='left', on='DT_IMB_BASE')
                        INCR = INCR.merge(BPR, how='left', on=['Cd_SISBASE_SFF','Nr_GRUPO','DT_REF'])

                        ipca.columns=['DT_REF','Nr_IPCA_REF_COM_CA']
                        INCR=INCR.merge(ipca, how='left', on='DT_REF')
                        INCR['VL_COM_AT']=INCR['VL_COM']/INCR['Nr_IPCA_REF_COM_CA']*INCR['Nr_IPCA_REF_BASE']
                        INCR['VL_CA_AT']=INCR['VL_CA']/INCR['Nr_IPCA_REF_COM_CA']*INCR['Nr_IPCA_REF_BASE']

                        INFRA = pd.read_csv("tabelas/TBL_TUC_INFRA.csv",sep="|",decimal=',',on_bad_lines='skip',
                                    encoding="Latin-1",dtype=str);
                
                        INCR['FLG_INFRA'] = 0
                        lst_INFRA = INFRA.loc[INFRA['Nr_A1'] == '0', 'Nr_TUC'].drop_duplicates()
                        INCR.loc[INCR['Nr_TUC'].isin(lst_INFRA), 'FLG_INFRA'] = 1

                        lst_INFRA = INFRA.loc[INFRA['Nr_A1'] != '0', 'Nr_TUC'].drop_duplicates()
                        axA1 = INFRA.groupby('Nr_TUC')['Nr_A1'].last()
                        INCR.loc[(INCR['Nr_TUC'].isin(lst_INFRA)) & 
                                    (INCR['Nr_A1'] == INCR['Nr_TUC'].map(axA1)), 'FLG_INFRA'] = 1

                        ORCAM = pd.read_csv("tabelas/TBL_TUC_ORC.csv",sep="|",decimal=',',on_bad_lines='skip',
                                            encoding="Latin-1",dtype=str);
                        tbl_CNTB = pd.read_csv("tabelas/tbl_CNTB.csv",sep="|",decimal=',',on_bad_lines='skip',
                                            encoding="Latin-1",dtype=str);
                        
                        lst_OE = ORCAM[ORCAM['Nr_A1'] == '0']['Nr_TUC'].drop_duplicates().tolist()
                        lst_CNT_OE = tbl_CNTB[tbl_CNTB['Nm_RZ_ANAL'] == 
                                    'Edificações, obras civis e benfeitorias']['Cd_CC'].drop_duplicates().tolist()

                        INCR['FLG_ORC'] = 0
                        INCR.loc[INCR['Nr_TUC'].isin(lst_OE) & 
                                INCR['Cd_CC'].isin(lst_CNT_OE), 'FLG_ORC'] = 1

                        SQLq = f"""
                                    SELECT 
                                        t1.Cd_SubODI, t1.Cd_Tipo_OE
                                    FROM 
                                        ROS t1 
                                    WHERE 
                                        t1.dt_ARQ = ?
                                    GROUP BY
                                        t1.Cd_SubODI
                                """
                        ROS = imp_tbl_forma_001('ROS', SQLq = SQLq, con = bd, st=st, Empresa=empresa)
                        INCR = INCR.merge(ROS, how='left', on = 'Cd_SubODI')
                        if 'Cd_Tipo_OE' in INCR.columns:
                            INCR['Cd_Tipo_OE'] = INCR['Cd_Tipo_OE'].fillna('0')
                        else:
                            INCR['Cd_Tipo_OE'] = '0'
                        INCR['MTD_AVAL']='A'
                        invalido_sff = ['', '0', 'ND']
                        invalido_vals = [0, 'ND']

                        mask = (
                                    ~INCR['Cd_SISBASE_SFF'].isin(invalido_sff) &
                                    INCR['VL_VF_POND'].notna() &
                                    INCR['VL_COM'].notna() &
                                    ~INCR['VL_COM'].isin(invalido_vals) &
                                    ~INCR['VL_VF_POND'].isin(invalido_vals)
                                )


                        INCR.loc[mask, 'MTD_AVAL'] = 'BPR'
                        INCR.loc[(INCR['FLG_INFRA'] == 1), 'MTD_AVAL'] = 'A'
                        INCR.loc[(INCR['Cd_Tipo_OE'].astype(str).isin(['4','7'])), 'MTD_AVAL'] = 'A'
                        INCR.loc[(INCR['Cd_UAR'] == 'UAR'), 'MTD_AVAL']='A'
                        INCR.loc[(INCR['Nr_TI']=='98'), 'MTD_AVAL']='A'
                        INCR.loc[(INCR['FLG_ORC']==1),'MTD_AVAL'] = 'ORC'
                        INCR['VL_VF_TOT'] = 0
                        INCR['VL_COM_TOT'] = 0
                        INCR['VL_CA_TOT'] = 0
                        INCR['VL_JOA_TOT'] = 0

                        familias = INCR[INCR['MTD_AVAL']=='BPR'].groupby('Cd_Patrim')['Cd_UAR'].nunique()
                        cd_familias = familias[familias > 1].index    
                        INCR.loc[INCR['Cd_Patrim'].isin(cd_familias),'MTD_AVAL'] = 'BPR_F'
                        INCR.loc[INCR['Cd_Patrim'].isin(cd_familias),'TST_VF_ROA_AVL'] = 'Família e BPR, fazer testes'
            
                        bprf = INCR['MTD_AVAL']=='BPR_F'
                        bpr = INCR['MTD_AVAL']=='BPR'

                        INCR.loc[bpr,'VL_VF_TOT'] = INCR['VL_VF_POND'] * INCR['Qtd_AIS']
                        INCR.loc[bpr,'VL_COM_TOT'] = INCR['VL_COM_AT']*INCR['Qtd_AIS']
                        INCR.loc[bpr,'VL_CA_TOT'] = INCR['VL_CA_AT']*INCR['Qtd_AIS']
                        somaVOC_Cd_PATR = INCR[bprf].groupby('Cd_Patrim')['VL_VOC'].transform('sum')
                        INCR.loc[bprf,'VL_VF_TOT'] = INCR['VL_VF_POND'] * INCR['Qtd_AIS'] * INCR['VL_VOC']/somaVOC_Cd_PATR
                        INCR.loc[bprf,'VL_COM_TOT'] = INCR['VL_COM_AT']*INCR['Qtd_AIS']*INCR['VL_VOC']/somaVOC_Cd_PATR
                        INCR.loc[bprf,'VL_CA_TOT'] = INCR['VL_CA_AT']*INCR['Qtd_AIS']*INCR['VL_VOC']/somaVOC_Cd_PATR
                        INCR.loc[bpr | bprf,'VL_JOA_TOT'] = ((INCR['VL_VF_TOT'] + INCR['VL_COM_TOT'] +
                                                        INCR['VL_CA_TOT'])*INCR['Pct_JOA_ROA'])
                        INCR.loc[bpr | bprf,'VL_BPRC_TOT'] = INCR.loc[bpr | bprf,['VL_VF_TOT', 'VL_COM_TOT', 
                                                                        'VL_CA_TOT', 'VL_JOA_TOT']].sum(axis=1)
                        INCR.loc[INCR['Cd_Patrim'].isin(cd_familias), 'MTD_AVAL'] = 'BPR'

                        BASE_BPR=INCR[bpr | bprf].groupby('Cd_TI', dropna=False)[['VL_VOCsjoa_IMB_AT','VL_BPRC_TOT','VL_JOA_TOT']].sum().reset_index()
                        BASE_BPR['PER_VAR']=(BASE_BPR['VL_BPRC_TOT'] - BASE_BPR['VL_JOA_TOT'])/BASE_BPR['VL_VOCsjoa_IMB_AT']
                        BASE_BPR['Cd_ANL']='OK'
                        BASE_BPR['FT_AJS']=1
                        AJ90 = BASE_BPR['PER_VAR']<0.9
                        AJ110 = BASE_BPR['PER_VAR']>1.1
                        BASE_BPR.loc[AJ90,'Cd_ANL'] = 'LIM 90%'
                        BASE_BPR.loc[AJ110,'Cd_ANL'] ='LIM 110%'
                        BASE_BPR.loc[AJ90,'FT_AJS'] = 0.9/BASE_BPR['PER_VAR']
                        BASE_BPR.loc[AJ110,'FT_AJS'] = 1.1/BASE_BPR['PER_VAR']
                        BASE_BPR_AX = BASE_BPR[['Cd_TI','Cd_ANL','FT_AJS']]

                        INCR = INCR.merge(BASE_BPR_AX, how='left', on='Cd_TI')

                        INCR.loc[bpr | bprf,'VL_BPR_TOT_AJS'] = ((INCR['VL_CA_TOT'] + 
                                                    INCR['VL_COM_TOT'])*INCR['FT_AJS'] + 
                                                    INCR['VL_VF_TOT'] + INCR['VL_JOA_TOT'])
                        
                        INCR['VL_VNR_SFF'] = INCR['VL_VOC'] * INCR['FA_IPCA']
                        INCR.loc[bpr | bprf,'VL_VNR_SFF'] = INCR['VL_BPR_TOT_AJS']
                        INCR.loc[~(bpr | bprf),'FT_AJS'] = 1
                        INCR.loc[~(bpr | bprf),'Cd_ANL'] = 'NA'

                        INCR['Dt_CNTB_AJST'] = INCR['Dt_Imob']
                        INCR['VL_VNR_UC'] = INCR['VL_VNR_SFF']
                        INCR['VL_DAC_UC'] = INCR['VL_VNR_SFF'] * INCR['VL_DEP_ACUM'].abs() / INCR['VL_VNR_SFF']
                        INCR['VL_VOCa'] = INCR['VL_VOC'] * INCR['FA_IPCA']
                        INCR['Dt_REF_DADOS'] = INCR['DT_REF_BASE']
                        INCR['Cd_CONC'] = '1'

                        INCR['Pct_Delta_VNR'] = (INCR['VL_VNR_SFF'] - INCR['VL_VOCa']) / INCR['VL_VNR_SFF'].replace(0, np.inf)
                        tol = 0.30

                        condicao_2 = INCR['Pct_Delta_VNR'] > tol
                        condicao_3 = INCR['Pct_Delta_VNR'] < -tol

                        INCR['TST_VNR'] = np.where(
                            
                                condicao_2,
                                "Avaliar, " + INCR['MTD_AVAL'] + ", há uma diferença a maior.",
                                np.where(condicao_3,
                                "Avaliar, " + INCR['MTD_AVAL'] + ", há uma diferença a menor.",
                                "VNR simulado consistente.")
                            )


                        df_TESTE = (INCR.groupby(['MTD_AVAL','TST_VNR'])
                                    .agg(
                                            VL_PCT_MEDIA = ('Pct_Delta_VNR', 'mean'),
                                            VL_PCT_MIN = ('Pct_Delta_VNR', 'min'),
                                            VL_PCT_MAX = ('Pct_Delta_VNR', 'max'),
                                            VL_PCT_STD = ('Pct_Delta_VNR', 'std'),
                                            QTD_OCOR = ('Pct_Delta_VNR', 'count'),
                                            VL_VOCa = ('VL_VOCa', 'sum'),
                                            VL_VNR_SFF = ('VL_VNR_SFF', 'sum')
                                        )
                                    .reset_index()
                                    .assign(
                                            PCT_AVAL_TOT = lambda x: x['VL_VOCa'] / INCR['VL_VNR_UC'].sum()
                                    )
                                    )

                        AIS_TX = INCR[['Ide_AIS','Cd_CC','Nr_TUC','Nr_A1','Nr_A2','Dt_CNTB_AJST','Dt_Imob',
                            'DT_IMB_BASE','VL_VOC','VL_DEP_ACUM','VL_VNR_UC','VL_DAC_UC','Dt_REF_DADOS',
                            'Cd_CONC']].copy()

                        AIS_TX = calc_tx_md(AIS_TX, depr)
                        INCR = INCR.merge(AIS_TX, how='left', on='Ide_AIS')

                        SQLq = f"""
                                    SELECT 
                                        t1.Cd_SubODI, 
                                        t1.Dt_Energ,
                                        DATETIME(t1.Dt_Energ, '+90 days') AS DT_LIM_UNIT
                                    FROM 
                                        ROS t1 
                                    WHERE 
                                        dt_ARQ = ?
                                    GROUP BY 
                                        Cd_SubODI;
                                """
                        ROS = imp_tbl_forma_001('ROS', SQLq = SQLq, con = bd, st=st, Empresa=empresa)
                        SQLq = f"""
                                    SELECT 
                                        t1.Cd_Patrim, 
                                        t1.Cd_DIG_INC,
                                        t1.Dt_Energ,
                                        DATETIME(t1.Dt_Energ, '+90 days') AS DT_LIM_UNIT
                                    FROM 
                                        DT_ENERG t1 
                                    WHERE 
                                        dt_ARQ = ?
                                    GROUP BY 
                                        Cd_Patrim, Cd_DIG_INC;
                                """
                        DT_ENERG = imp_tbl_forma_001('DT_ENERG', SQLq = SQLq, con = bd, st=st, Empresa=empresa)
                        if len(DT_ENERG)>0:
                            INCR = INCR.merge(DT_ENERG, how='left', on=['Cd_Patrim', 'Cd_DIG_INC'])
                        else:
                            INCR = INCR.merge(ROS, how='left', on=['Cd_SubODI'])

                        INCR['TST_DT_IMOB'] = 'OK'
                        INCR.loc[INCR['Dt_Energ'] > INCR['Dt_CNTB_AJST'],
                                'TST_DT_IMOB'] = 'DATA DE ENERGIZAÇÃO MAIOR QUE A DATA CONTÁBIL AJUSTADA INFORMADA'
                        INCR.loc[INCR['Dt_CNTB_AJST'] > INCR['DT_LIM_UNIT'],
                                'TST_DT_IMOB'] = """ATRASO NA UNITIZAÇÃO, APÓS CORREÇÃO DA AVALIADORA, (>90 DIAS 
                                                    DA ENERGIZAÇÃO)"""
                        INCR.loc[INCR['Dt_Energ'].isnull(),
                                    'TST_DT_IMOB'] = 'DATA DE ENERGIZAÇÃO NÃO INFORMADA'
                        INCR.loc[(INCR['Cd_Tipo_OE'].astype(str) == '4') & (INCR['TST_DT_IMOB'] != 'OK'),
                                    'TST_DT_IMOB'] = 'DOAÇÃO, TESTE NÃO SE APLICA'
                        INCR.loc[(INCR['Cd_Tipo_OE'].astype(str) == '7') & (INCR['TST_DT_IMOB'] != 'OK'),
                                    'TST_DT_IMOB'] = 'INCORPORAÇÃO, TESTE NÃO SE APLICA'
                        
                        INCR.to_sql("TBL_AIS_INCR_SIM", bd, if_exists='replace', index=False)
                        AIS1 = AIS.copy()
                    else:
                        INCR = carga_sqlite_cache("SELECT * FROM TBL_AIS_INCR_SIM", bd)
                    
                df_AX = INCR.groupby(['Nr_TUC','VL_VU','ANO'], dropna=False)['VL_VOC'].sum().reset_index()
                df_AX['VL_VU'] = df_AX['VL_VU'].fillna("0").astype(int).astype(str)
                tabela = df_AX.pivot_table(index=['Nr_TUC','VL_VU'], 
                            columns=['ANO'], 
                            values='VL_VOC', aggfunc='sum').fillna(0).rename(columns={'VL_VU':'Vida_Util_Economica'})
                soma_total = tabela.sum(axis=1)
                tabela['TOTAL'] = soma_total
                tabela = tabela.sort_values(by='TOTAL', ascending=False)
                tabela['CLS_ABC'] = tabela['TOTAL'].cumsum() / tabela['TOTAL'].sum()
                condicoes = [
                                (tabela['CLS_ABC'] <= 0.85),
                                (tabela['CLS_ABC'] <= 0.95)
                             ]
                escolhas = ['A', 'B']
                tabela['CLS_ABC'] = np.select(condicoes, escolhas, default='C')

                tabela1 = tabela.applymap(formatar_br).style.set_properties(**{'text-align': 'right'})
                st.html(f"""
                            <p  style="text-align: justify;text-indent: 40px">Também segregamos por unidade de cadastro, UC e vida útil, 
                        reordenando das de maior para menor investimento:</p>
                            """)
                st.write(tabela1.to_html(escape=False), unsafe_allow_html=True)
                dataframe_to_image(tabela1, rf"{dir_FIG}/tabela_ais_incremental_UC_VU_VOCa.png")



                tabela = INCR.groupby(['MTD_AVAL'], dropna=False)[['VL_VOCa','VL_VNR_SFF']].sum()
                tabela['Pct_INV'] = tabela['VL_VOCa'] / tabela['VL_VOCa'].sum() * 100
                tabela1 = tabela.applymap(formatar_br).style.set_properties(**{'text-align': 'right'})
                st.html(f"""
                            <p  style="text-align: justify;text-indent: 40px">A seguir, o VNR estimado:</p>
                            """)
                st.write(tabela1.to_html(escape=False), unsafe_allow_html=True)
                dataframe_to_image(tabela1, rf"{dir_FIG}/tabela_ais_incremental_participacao_metodo.png")
                          
        st.html(f"""
                    <div style="font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #222; 
                    max-width: 1000px; margin: 0 auto;">

                    <h2 style="margin-bottom: 0.4rem;">Modelo para análise do valor presente relativo com 
                    remuneração em degraus</h2>
                    <p style="margin-top: 0;">
                        Avaliar o comportamento do valor presente líquido relativo de ativos com vidas úteis entre 
                        5 e 40 anos, considerando atualização da receita a cada 5 anos, ambiente não inflacionário, 
                        taxa de remuneração de capital fixa e taxa de manutenção de 10%.
                    </p>
                    <hr style="margin: 1.5rem 0;">
                    <h3>1. Base do modelo</h3>
                    <p>
                        Adota-se valor inicial normalizado do ativo igual a:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px;">
                        <code>I₀ = 1</code>
                    </div>
                    <p>
                        A vida útil econômica do ativo é representada por <code>N</code>, com:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px;">
                        <code>N ∈ {5, ..., 40}</code>
                    </div>
                    <p>
                        A depreciação econômica é linear. Logo, a depreciação anual é dada por:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px;">
                        <code>Dep(N) = 1 / N</code>
                    </div>
                    <p>
                        A base residual do ativo na idade <code>t</code> é:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px;">
                        <code>B(t) = 1 - t / N</code>
                    </div>
                    <p>
                        Quando ocorre uma revisão tarifária na idade <code>t</code>, a receita anual regulatória 
                        do bloco seguinte é:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px;">
                        <code>R(t) = w · B(t) + 1 / N + m</code>
                    </div>
                    <p>
                        em que:
                    </p>
                    <ul>
                        <li><code>w = T<sub>WACC</sub></code> é a taxa de capital fixa;</li>
                        <li><code>m = 10%</code> é a taxa de manutenção anual.</li>
                    </ul>
                    <p>
                        Substituindo a base residual, obtém-se:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px;">
                        <code>R(t) = w · (1 - t / N) + 1 / N + 0,10</code>
                    </div>
                    <p>
                        Essa receita permanece constante ao longo de cada bloco de 5 anos, o que gera uma remuneração 
                        em degraus.
                    </p>

                    <hr style="margin: 1.5rem 0;">
                    <h3>2. Posição da ativação dentro do ciclo de 5 anos</h3>
                    <p>
                        Para capturar o efeito da atualização tarifária por blocos, define-se a posição da ativação no 
                        ciclo regulatório:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px;">
                        <code>r ∈ {0, 1, 2, 3, 4}</code>
                    </div>
                    <p>
                        com a seguinte interpretação:
                    </p>
                    <ul>
                        <li><code>r = 0</code>: ativação coincidente com a revisão da receita;</li>
                        <li><code>r = 1</code>: ativação 1 ano após a revisão;</li>
                        <li><code>r = 2</code>: ativação 2 anos após a revisão;</li>
                        <li><code>r = 3</code>: ativação 3 anos após a revisão;</li>
                        <li><code>r = 4</code>: ativação 4 anos após a revisão, isto é, 1 ano antes da próxima 
                        atualização.</li>
                    </ul>
                    <p>
                        O tempo de espera até a primeira revisão é dado por:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px;">
                        <code>
                        δ<sub>r</sub> =
                        0, se r = 0 <br>
                        δ<sub>r</sub> = 5 - r, se r ∈ {1, 2, 3, 4}
                        </code>
                    </div>
                    <p>
                        Assim:
                    </p>
                    <ul>
                        <li><code>r = 0 → δ = 0</code></li>
                        <li><code>r = 1 → δ = 4</code></li>
                        <li><code>r = 2 → δ = 3</code></li>
                        <li><code>r = 3 → δ = 2</code></li>
                        <li><code>r = 4 → δ = 1</code></li>
                    </ul>
                    <hr style="margin: 1.5rem 0;">
                    <h3>3. Receita em cada bloco</h3>
                    <p>
                        As revisões tarifárias ocorrem nas idades:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px;">
                        <code>t<sub>j</sub> = δ<sub>r</sub> + 5j</code>
                    </div>
                    <p>
                        para <code>j = 0, 1, 2, ...</code>, enquanto <code>t<sub>j</sub> &lt; N</code>.
                    </p>
                    <p>
                        Em cada revisão <code>j</code>, a receita anual do bloco é:
                    </p>

                    <div style="background:#f7f7f7; padding:12px; border-radius:8px;">
                        <code>R<sub>j</sub> = w · (1 - t<sub>j</sub> / N) + 1 / N + 0,10</code>
                    </div>
                    <p>
                        Essa receita vale por:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px;">
                        <code>n<sub>j</sub> = min(5, N - t<sub>j</sub>)</code>
                    </div>
                    <p>
                        anos, de forma que o último bloco pode ter menos de 5 anos caso a vida útil termine antes.
                    </p>

                    <hr style="margin: 1.5rem 0;">

                    <h3>4. Valor presente relativo</h3>
                    <p>
                        O valor presente relativo da sequência de receitas, descontado à própria taxa de capital 
                        <code>w</code>, é:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px; overflow-x:auto;">
                        <code>
                        VPR(N, r) = Σ<sub>j</sub> Σ<sub>u=1</sub><sup>n<sub>j</sub></sup> R<sub>j</sub> / (1 + w)<sup>t<sub>j</sub> + u</sup>
                        </code>
                    </div>
                    <p>
                        Se quisermos o valor presente líquido relativo, subtraindo o investimento inicial normalizado, 
                        temos:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px;">
                        <code>VPL<sub>rel</sub>(N, r) = VPR(N, r) - 1</code>
                    </div>
                    <p>
                        Esse é o indicador mais adequado para analisar o efeito da ativação em diferentes pontos do ciclo 
                        tarifário.
                    </p>
                    <hr style="margin: 1.5rem 0;">
                    <h3>5. Interpretação econômica</h3>
                    <p>
                        O modelo produz naturalmente um comportamento em degraus, porque a receita só é atualizada a cada 
                        5 anos. Isso implica diferenças relevantes no valor presente a depender do momento em que o ativo 
                        entra em operação.
                    </p>
                    <ul>
                        <li><strong>r = 0</strong>: melhor situação, pois o ativo entra já no início de um bloco 
                        remunerado;</li>
                        <li><strong>r = 1</strong>: pior situação, pois o ativo espera 4 anos até ser incluído na 
                        atualização seguinte;</li>
                        <li><strong>r = 2, 3 e 4</strong>: situações intermediárias, com melhora progressiva à medida 
                        que a espera até a próxima revisão diminui;</li>
                        <li><strong>vidas úteis maiores</strong>: reduzem o peso relativo da espera inicial, suavizando 
                        a diferença entre posições de ativação.</li>
                    </ul>
                    <p>
                        Portanto, o modelo permite evidenciar a assimetria econômica gerada pela defasagem entre a 
                        ativação do ativo e a atualização tarifária.
                    </p>
                    <hr style="margin: 1.5rem 0;">
                    <h3>6. Exemplo numérico ilustrativo</h3>
                    <p>
                        A título ilustrativo, considerando <code>T<sub>WACC</sub> = 8%</code>, obtém-se a seguinte tabela 
                        de <code>VPL<sub>rel</sub></code>:
                    </p>
                    <div style="overflow-x:auto;">
                        <table style="border-collapse: collapse; width: 100%; font-size: 0.96rem;">
                        <thead>
                            <tr style="background:#f0f0f0;">
                            <th style="border:1px solid #ccc; padding:8px; text-align:left;">Vida útil (N)</th>
                            <th style="border:1px solid #ccc; padding:8px;">r = 0</th>
                            <th style="border:1px solid #ccc; padding:8px;">r = 1</th>
                            <th style="border:1px solid #ccc; padding:8px;">r = 2</th>
                            <th style="border:1px solid #ccc; padding:8px;">r = 3</th>
                            <th style="border:1px solid #ccc; padding:8px;">r = 4</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                            <td style="border:1px solid #ccc; padding:8px;">5</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">0,517</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">-0,785</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">-0,530</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">-0,231</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">0,116</td>
                            </tr>
                            <tr>
                            <td style="border:1px solid #ccc; padding:8px;">10</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">0,770</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">-0,176</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">0,020</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">0,241</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">0,490</td>
                            </tr>
                            <tr>
                            <td style="border:1px solid #ccc; padding:8px;">20</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">1,054</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">0,285</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">0,450</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">0,632</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">0,833</td>
                            </tr>
                            <tr>
                            <td style="border:1px solid #ccc; padding:8px;">40</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">1,236</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">0,554</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">0,703</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">0,866</td>
                            <td style="border:1px solid #ccc; padding:8px; text-align:center;">1,043</td>
                            </tr>
                        </tbody>
                        </table>
                    </div>
                    <p>
                        O padrão observado é claro: <code>r = 0</code> é o melhor caso, <code>r = 1</code> é o pior,
                        e os demais casos mostram melhora monotônica conforme a ativação se aproxima da próxima revisão.
                    </p>
                    <hr style="margin: 1.5rem 0;">
                    <h3>7. Fórmula compacta para implementação</h3>
                    <p>
                        A expressão consolidada do modelo é:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px; overflow-x:auto;">
                        <code>
                        VPL<sub>rel</sub>(N, r) =
                        Σ<sub>j: t<sub>j</sub> &lt; N</sub>
                        [
                        ( w · (1 - t<sub>j</sub> / N) + 1 / N + 0,10 )
                        ·
                        Σ<sub>u=1</sub><sup>n<sub>j</sub></sup>
                        1 / (1 + w)<sup>t<sub>j</sub> + u</sup>
                        ]
                        - 1
                        </code>
                    </div>
                    <p>
                        com:
                    </p>
                    <div style="background:#f7f7f7; padding:12px; border-radius:8px;">
                        <code>
                        t<sub>j</sub> = δ<sub>r</sub> + 5j <br>
                        n<sub>j</sub> = min(5, N - t<sub>j</sub>)
                        </code>
                    </div>
                    <p>
                        Essa formulação permite calcular, para cada vida útil e para cada posição de ativação dentro do 
                        ciclo regulatório, o valor presente líquido relativo do ativo e, assim, analisar de forma direta 
                        o comportamento do VPL sob remuneração em degraus. Vamos trabalhar melhor a seguir.
                    </p>
                    </div>
                """)
        st.info(
                        "Ativos com vida útil entre 5 e 40 anos, receita atualizada a cada 5 anos, "
                        "ambiente não inflacionário, manutenção de 10% e taxa de capital fixa."
                    )

        def taxa_depreciacao_linear(n: int) -> float:
            if n <= 0:
                raise ValueError("A vida útil N deve ser positiva.")
            return 1.0 / n
        
        def base_residual(t: int, n: int) -> float:
            return max(0.0, 1.0 - t / n)
        
        def tempo_ate_revisao(r: int) -> int:
            """
            Tempo até a primeira revisão tarifária.
            r = 0 -> ativação coincide com revisão
            r = 1..4 -> anos restantes até a próxima revisão
            """
            if r not in {0, 1, 2, 3, 4}:
                raise ValueError("r deve estar entre 0 e 4.")
            return 0 if r == 0 else 5 - r
        
        def receita_anual_na_revisao(t: int, n: int, wacc: float, manut: float = 0.10) -> float:
            """
            Receita anual regulatória definida na revisão ocorrida em t.
            R(t) = w * B(t) + 1/N + manut
            """
            dep = taxa_depreciacao_linear(n)
            base = base_residual(t, n)
            return wacc * base + dep + manut
        
        def valor_presente(
                                    t_revisao: int,
                                    anos: int,
                                    receita_anual: float,
                                    wacc: float,
                                ) -> float:
            vp = 0.0
            for u in range(1, anos + 1):
                vp += receita_anual / ((1.0 + wacc) ** (t_revisao + u))
            return vp
        
        def calcular_vpr_detalhado(
                                        n: int,
                                        r: int,
                                        wacc: float,
                                        manut: float = 0.10,
                                    ) -> tuple[float, float, pd.DataFrame]:
            """
                Calcula:
                    - VPR(N, r)
                    - VPL_rel(N, r) = VPR - 1
                    - tabela de detalhe dos blocos
            """
            delta = tempo_ate_revisao(r)
            indice = 0
            t_revisao = delta
            total_vpr = 0.0
            linha: list[BlocoResultado] = []

            while t_revisao < n:
                anos_bloco = min(5, n - t_revisao)
                base = base_residual(t_revisao, n)
                rec_anual = receita_anual_na_revisao(t_revisao, n, wacc, manut)
                vp_bloco = valor_presente(t_revisao, anos_bloco, rec_anual, wacc)

                linha.append(
                                BlocoResultado(
                                    bloco=indice,
                                    t_revisao=t_revisao,
                                    anos_no_bloco=anos_bloco,
                                    base_residual=base,
                                    receita_anual=rec_anual,
                                    vp_bloco=vp_bloco,
                                )
                            )

                total_vpr += vp_bloco
                indice += 1
                t_revisao = delta + 5 * indice

            df_detalhado = pd.DataFrame([r.__dict__ for r in linha])
            vpl_rel = total_vpr - 1.0
            return total_vpr, vpl_rel, df_detalhado
        
        def matriz_bloco(
                            wacc: float,
                            manut: float = 0.10,
                            n_min: int = 5,
                            n_max: int = 40,
                        ) -> pd.DataFrame:
            """
                Monta a matriz principal:
                    linhas = vida útil N
                    colunas = r=0..4
                    valores = VPL_rel(N, r)
            """
            linhas = []

            for n in range(n_min, n_max + 1):
                linha = {"Vida útil (anos)": n}
                for r in range(5):
                    _, vpl_rel, _ = calcular_vpr_detalhado(
                                                            n=n,
                                                            r=r,
                                                            wacc=wacc,
                                                            manut=manut,
                                                            )
                    linha[f"r = {r}"] = vpl_rel
                linhas.append(linha)

            return pd.DataFrame(linhas)
        
        def matriz_final(df_matriz: pd.DataFrame) -> pd.DataFrame:
            return df_matriz.melt(
                                    id_vars=["Vida útil (anos)"],
                                    var_name="Posição no ciclo",
                                    value_name="VPL_rel",
                                    )
        
        colsF = st.columns([1,2,1,2,1], gap='small')
        with colsF[1]:
            wacc_pct = st.number_input(
                                        "T_WACC (%)",
                                        min_value=0.0,
                                        max_value=15.0,
                                        value=8.0,
                                        step=0.05,
                                        help="Taxa de capital fixa usada tanto na remuneração quanto no desconto.",
                                        )
            manut_pct = st.number_input(
                                            "Taxa de manutenção (%)",
                                            min_value=0.0,
                                            max_value=100.0,
                                            value=10.0,
                                            step=0.5,
                                        )
            n_min, n_max = st.slider(
                                        "Faixa de vida útil (anos)",
                                        min_value=5,
                                        max_value=40,
                                        value=(5, 40),
                                    )
        with colsF[3]:
            detalhe_n = st.selectbox(
                                                "Vida útil para tabela de detalhe",
                                                options=list(range(n_min, n_max + 1)),
                                                index=min(15, n_max - n_min),
                                            )
            detalhe_r = st.selectbox(
                                        "Posição no ciclo para detalhe",
                                        options=[0, 1, 2, 3, 4],
                                        index=0,
                                    )

            show_vpr = st.checkbox(
                                        "Mostrar VPR em vez de VPL relativo",
                                        value=False,
                                        help="VPR = soma descontada das receitas. VPL relativo = VPR - 1.",
                                    )
        colsG = st.columns([5,1,5], gap='small')
        with colsG[0]:
            wacc = wacc_pct / 100.0
            manut = manut_pct / 100.0
            matriz_df = matriz_bloco(
                                        wacc=wacc,
                                        manut=manut,
                                        n_min=n_min,
                                        n_max=n_max,
                                    )
            display_df = matriz_df.copy()

            if show_vpr:
                for col in [c for c in display_df.columns if c.startswith("r = ")]:
                    display_df[col] = display_df[col] + 1.0

            formatada_df = display_df.copy()
            cols_valor = [c for c in formatada_df.columns if c.startswith("r = ")]
            matriz_estilizada = (
                                    formatada_df.style
                                    .format({col: "{:.3f}" for col in cols_valor})
                                    .background_gradient(
                                                            cmap="RdYlGn",
                                                            subset=cols_valor,
                                                            axis=None,
                                                        )
                                    .set_properties(
                                                        subset=cols_valor,
                                                        **{
                                                            "text-align": "center",
                                                            "font-weight": "600",
                                                        }
                                                    )
                                    .set_properties(
                                                        subset=["Vida útil (anos)"],
                                                        **{
                                                            "text-align": "center",
                                                            "font-weight": "700",
                                                        }
                                                    )
                                )
            nome_metrica = "VPR" if show_vpr else "VPL relativo"
            st.html(f"""<h3>Tabela principal — {nome_metrica}</h3>
                        <p style="text-align: justify; text-indent: 40px;">
                            Cada linha representa uma <b>vida útil do ativo</b> e cada coluna representa 
                            a <b>posição da ativação no ciclo tarifário</b>.
                        </p>
                        <ul>
                            <li><b>r = 0</b>: ativação coincide com a revisão;</li>
                            <li><b>r = 1</b>: ativação 1 ano após a revisão;</li>
                            <li><b>r = 4</b>: ativação 4 anos após a revisão, isto é, 1 ano antes da próxima revisão.</li>
                        </ul>
                        <p style="text-align: justify; text-indent: 40px;">
                            A escala de cor ajuda a perceber rapidamente onde o valor presente é menor ou maior.
                        </p>"""
                        )
            st.dataframe(
                            matriz_estilizada,
                            width='stretch', hide_index=True,
                            height=760,
                        )
            dataframe_to_image(matriz_estilizada, rf"{dir_FIG}/tabela_vpr_faixa_ampla.png")
            st.html(f"""<h3>Resumo</h3>""")
            melhor_idx = None
            pior_idx = None
            melhor_value = -float("inf")
            pior_value = float("inf")

            for _, row in display_df.iterrows():
                n = int(row["Vida útil (anos)"])
                for r in range(5):
                    val = float(row[f"r = {r}"])
                    if val > melhor_value:
                        melhor_value = val
                        melhor_idx = (n, r)
                    if val < pior_value:
                        pior_value = val
                        pior_idx = (n, r)

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric(
                            "Maior valor da matriz",
                            f"{melhor_value:.3f}".replace(".",","),
                            help=f"Ocorrência em N={melhor_idx[0]} anos, r={melhor_idx[1]}",
                        )
                st.caption(f"N = {melhor_idx[0]} anos | r = {melhor_idx[1]}")

            with c2:
                st.metric(
                            "Menor valor da matriz",
                            f"{pior_value:.3f}".replace(".",","),
                            help=f"Ocorrência em N={pior_idx[0]} anos, r={pior_idx[1]}",
                            )
                st.caption(f"N = {pior_idx[0]} anos | r = {pior_idx[1]}")

            with c3:
                spread = melhor_value - pior_value
                st.metric(
                            "Amplitude",
                            f"{spread:.3f}".replace(".",","),
                            help="Diferença entre o maior e o menor valor observados na matriz.",
                        )
        with colsG[2]:
            st.html(f"""<h3>Tabela de detalhe por caso</h3>"""
                        )
            vpr_detalhado, vpl_rel_detalhado, df_detalhado = calcular_vpr_detalhado(
                                                                                n=detalhe_n,
                                                                                r=detalhe_r,
                                                                                wacc=wacc,
                                                                                manut=manut,
                                                                            )

            detalhado_display = df_detalhado.copy()
            detalhado_display["base_residual"] = detalhado_display["base_residual"].map(lambda x: f"{x:.4f}".replace(".",","))
            detalhado_display["receita_anual"] = detalhado_display["receita_anual"].map(lambda x: f"{x:.4f}".replace(".",","))
            detalhado_display["vp_bloco"] = detalhado_display["vp_bloco"].map(lambda x: f"{x:.4f}".replace(".",","))

            c4, c5 = st.columns([1, 2])

            with c4:
                st.markdown("**Caso selecionado**")
                st.write(f"Vida útil \(N\): **{detalhe_n} anos**")
                st.write(f"Posição no ciclo \(r\): **{detalhe_r}**")
                st.write(f"VPR: **{vpr_detalhado:.4f}**".replace(".",","))
                st.write(f"VPL relativo: **{vpl_rel_detalhado:.4f}**".replace(".",","))

                st.markdown("**Leitura econômica**")
                if detalhe_r == 0:
                    st.info("O ativo entra exatamente no momento da revisão tarifária.")
                elif detalhe_r == 1:
                    st.warning("Este é o caso mais penalizado: o ativo espera 4 anos até a próxima revisão.")
                else:
                    st.info(
                        f"O ativo espera {teste(detalhe_r)} ano(s) até a primeira revisão, "
                        "o que reduz parcialmente a defasagem regulatória."
                    )
            with c5:
                st.dataframe(
                                detalhado_display,
                                width='stretch', hide_index=True,
                            )
                dataframe_to_image(detalhado_display, rf"{dir_FIG}/tabela_vpr_exemplo.png")

                st.html(
                        f"""
                        <div style="font-family: Arial, Helvetica, sans-serif; color: #222; line-height: 1.65; 
                        padding: 16px 18px; background: #fafafa; border: 1px solid #e8e8e8; border-radius: 12px;">
                            <div style="font-size: 1.02rem; font-weight: 700; margin-bottom: 10px;">
                                Premissas do modelo
                            </div>

                            <ul style="margin: 0; padding-left: 20px;">
                                <li style="margin-bottom: 6px;">Valor inicial do ativo normalizado em <strong>1</strong>;
                                </li>
                                <li style="margin-bottom: 6px;">Vida útil econômica entre <strong>{n_min}</strong> e 
                                <strong>{n_max}</strong> anos;</li>
                                <li style="margin-bottom: 6px;">Depreciação linear: <strong>1 / N</strong>;</li>
                                <li style="margin-bottom: 6px;">
                                    Receita regulatória por bloco:
                                    <strong>R(t) = WACC × base residual + depreciação + manutenção</strong>;
                                </li>
                                <li style="margin-bottom: 6px;">
                                    Base residual na idade t:
                                    <strong>B(t) = 1 - t / N</strong>;
                                </li>
                                <li style="margin-bottom: 6px;">Atualização da receita a cada <strong>5 
                                anos</strong>;</li>
                                <li style="margin-bottom: 6px;">Ambiente <strong>não inflacionário</strong>;</li>
                                <li style="margin-bottom: 6px;">Desconto à própria taxa <strong>WACC</strong>;</li>
                                <li>Métrica principal: <strong>VPL relativo = valor presente das receitas - 1</strong>.
                                </li>
                            </ul>
                        </div>
                        """
                    )
        
        

