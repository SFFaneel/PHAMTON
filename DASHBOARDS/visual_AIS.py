from __future__ import annotations
import streamlit as st
import sqlite3 as sl
import numpy as np
import pandas as pd
import plotly.graph_objects as go 
from scipy.stats import t
from datetime import date, timedelta
from SRC.ais_funcoes import (bsc_proj, bsc_proj_dd, calcular_kpis, bsc_ddsTI)
from SRC.calculos import fnc_ajs_df
from pathlib import Path
import os, duckdb, math, html, re
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import matplotlib.patches as patches
from matplotlib.colors import LogNorm
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib import gridspec
from scipy.signal import find_peaks
from scipy.stats import chisquare, entropy, chi2, norm, binom, binomtest
from matplotlib.ticker import FuncFormatter
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from html import escape

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
 
from UTILS import (
                    resumo_por_tipo_mao_de_obra, 
                    resumo_consolidado, 
                    resumo_por_fase, 
                    ajs_txt,
                    monitor_completo,
                    TCCU, 
                    TCKdE, 
                    TCKdEa1a6, 
                    TCKdeIndicadores, 
                    resumo_por_projeto, 
                    sel_projetos,
                    resumo_roa, 
                    resumo_st,
                    exportar_texto,
                    existe_tabela,
                    max_arq,
                    bsc_dados_reg,
                    executar_vis
                 )  
import plotly.express as px      

@st.fragment
def vis_AX001(bd_path, caminho, empresa, st):
    with sl.connect(bd_path) as bd:
        for tbl in ['ROA','ROD']:
            if existe_tabela(tbl, bd):
                xi = resumo_roa(bd, caminho, empresa, st, tbl)

def moeda(valor):
    return (
                f"R$ {valor:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

def percentual(valor):
    return f"{valor:.1f}%".replace(".", ",")

@st.fragment
def vis_AX002ax(bd = None, caminho = None, empresa = None, st = None, local = None, df = None):
    st.html("""<h4>Recorrência de valores por trimestre</h4>
            <p style="text-align:justify;text-indent:40px;line-height:1.7">
            A análise da recorrência de valores globais e unitários,
            segmentada por item, natureza de gasto e classe de custo,
            permite identificar padrões de repetição monetária e sua
            persistência ao longo dos trimestres examinados. A avaliação
            dos valores unitários, quando disponíveis os respectivos
            quantitativos, possibilita distinguir a padronização de
            preços dos efeitos decorrentes das quantidades apropriadas,
            enquanto a consideração dos montantes globais preserva
            a dimensão financeira dos registros. A integração dessas
            perspectivas contribui para a identificação de concentrações
            relevantes em materiais, serviços, mão de obra e demais
            componentes de custos, subsidiando a seleção de ocorrências
            para verificação da consistência dos critérios de valoração,
            da rastreabilidade documental e da conformidade das
            apropriações realizadas.
            </p>
            """)
    dimensoes = {
                    "Item": "DESCR_LCMTO",
                    "Natureza de gasto": "DESCR_NG",
                    "Classe de custo": "DESCR_CCUSTO",
                }

    df_filtro = df.copy()
    cols = st.columns([1,6,1], gap='small')
    with cols[1]:
        with st.container(border=True):
            colunas = st.columns(3)
    for i, (nome, coluna) in enumerate(dimensoes.items()):
        if coluna not in df_filtro.columns:
            st.warning(f"Coluna não encontrada: {coluna}")
            continue
        df_filtro[coluna] = df_filtro[coluna].astype("string").str.strip()
        opcoes =  df_filtro[coluna].dropna().unique().tolist()
        opcoes = ["Todos"] + sorted([v for v in opcoes if v != "Todos"])

        with colunas[i]:
            selecionado = st.selectbox(
                                        nome,
                                        options=opcoes,
                                        key=f"filtro_{coluna}"
                                    )
        if selecionado != "Todos":
            df_filtro = df_filtro[df_filtro[coluna] == selecionado].copy()

    tipo_analise = st.radio(
                                "Base de comparação",
                                ["Valor global", "Valor unitário"],
                                horizontal=True
                            )
    COL_VL = "VL_tot"
    COL_QTD = "Qtd"
    COL_DT = "Dt_Lcmto"
    dados = df_filtro.copy()
    dados[COL_DT] = pd.to_datetime(dados[COL_DT], errors="coerce", dayfirst=True)

    if tipo_analise == "Valor unitário":
        validos = dados[COL_QTD].notna() & np.isfinite(dados[COL_QTD])(dados[COL_QTD] != 0)
        dados = dados.loc[validos].copy()
        dados["VALOR_ANALISE"] = dados[COL_VL] / dados[COL_QTD]
        casas = 2
    else:
        dados["VALOR_ANALISE"] = dados[COL_VL]
        casas = 2

    dados = dados.dropna(subset=["TRI", "VALOR_ANALISE"]).copy()
    if dados.empty:
        st.info("Não há registros para os filtros selecionados.")
        return
    dados["VALOR_CHAVE"] =dados["VALOR_ANALISE"].round(casas)
    
    dados["FREQ_TRI"] = dados.groupby(["TRI", "VALOR_CHAVE"])["VALOR_CHAVE"].transform("size")
    repetidos = dados[dados["FREQ_TRI"] > 1].copy()

    freq = (
                repetidos.groupby(
                    ["TRI", "VALOR_CHAVE"],
                    as_index=False
                )
                .agg(
                    FREQUENCIA=("VALOR_ANALISE", "size"),
                    MONTANTE=(COL_VL, lambda x: x.abs().sum()),
                    QTD_DISTINTAS=(COL_QTD, "nunique")
                )
            )

    total = len(dados)
    total_rep = len(repetidos)
    montante_total = dados[COL_VL].abs().sum()
    montante_rep = repetidos[COL_VL].abs().sum()
    pct_rep = 100 * total_rep / total

    pct_fin = (
                    100 * montante_rep / montante_total
                    if montante_total > 0 else 0
                )

    c1, c2, c3, c4 = st.columns([2,1,3,1])

    c1.metric("Lançamentos", f"{total:,}".replace(",","."))
    c2.metric("Recorrência", f"{pct_rep:.1f}%".replace(".",","))
    c3.metric("Montante recorrente", moeda(montante_rep))
    c4.metric("Participação financeira", f"{pct_fin:.1f}%".replace(".",","))
    
    if freq.empty:
        st.info("Não foram encontrados valores recorrentes.")

    else:
        metrica = st.radio("Intensidade do mapa", ["Frequência", "Montante financeiro"], horizontal=True)
        plot = freq.copy()
        plot["VALOR_ABS"] = plot["VALOR_CHAVE"].abs()
        plot = plot[plot["VALOR_ABS"] > 0].copy()
        if plot.empty:
            st.info("As recorrências encontradas possuem valor zero.")
        else:
            expoente = np.floor(np.log10(plot["VALOR_ABS"])).astype(int)

            plot["ORDEM"] = expoente
            plot["FAIXA"] = expoente.map(lambda x: f"10^{x} a 10^{x+1}")

            coluna = "FREQUENCIA" if metrica == "Frequência" else "MONTANTE"
            matriz = plot.pivot_table(
                                        index=["ORDEM", "FAIXA"],
                                        columns="TRI",
                                        values=coluna,
                                        aggfunc="sum",
                                        fill_value=0
                                    ).sort_index()

            matriz = matriz.reindex(columns=sorted(dados["TRI"].unique()), fill_value=0)
            valores = matriz.to_numpy(dtype=float)

            fig, ax = plt.subplots(figsize=(13, max(4, len(matriz) * 0.65)))
            positivos = valores[valores > 0]

            if len(positivos):
                imagem = ax.imshow(
                                        np.ma.masked_less_equal(valores, 0),
                                        cmap="Blues",
                                        aspect="auto",
                                        norm=LogNorm(
                                            vmin=positivos.min(),
                                            vmax=max(
                                                positivos.max(),
                                                positivos.min() * 1.01
                                            )
                                        )
                                    )

                fig.colorbar(imagem, ax=ax, label=metrica)

            ax.set_xticks(range(len(matriz.columns)))
            ax.set_xticklabels(
                                    matriz.columns.astype(str),
                                    rotation=45,
                                    ha="right"
                                )

            ax.set_yticks(range(len(matriz)))
            ax.set_yticklabels(
                                    matriz.index.get_level_values("FAIXA")
                                )

            ax.set_xlabel("Trimestre")
            ax.set_ylabel(
                            "Faixa de valor unitário (R$)"
                            if tipo_analise == "Valor unitário"
                            else "Faixa de valor global (R$)"
                        )

            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

@st.fragment
def vis_AX002(bd_path, caminho, empresa, st, local):
    with sl.connect(bd_path) as bd:
        if existe_tabela('DIST_REPT_NG', bd):
            caminho = f"{local}"
            arquivo_roa = [
                                os.path.join(f"{caminho}\DADOS_BRUTOS_MANUAL", f)
                                for f in os.listdir(f"{caminho}/DADOS_BRUTOS_MANUAL")
                                if f.lower().endswith('.csv') and (f.lower()[:4]=="roa_")
                            ]

            erro = {}
            if (len(arquivo_roa) !=0):
                for enc in ['CP1252', 'latin-1', 'utf-8']:
                    try:
                        sSQL = f"""
                                    WITH ROA_BASE AS (
                                        SELECT
                                            Ide_RO_Analitico,
                                            Cd_SubODI,
                                            Nr_TI,
                                            Cd_Cls_Custo,
                                            COD_ITEM,
                                            Cd_NG,
                                            try_strptime(Dt_Lcmto, '%Y/%m/%d')::DATE AS Dt_Lcmto,
                                            TRY_CAST(replace(VL_tot, ',', '.') AS DOUBLE) AS VL_tot,
                                            TRY_CAST(replace(Qtd, ',', '.') AS DOUBLE) AS Qtd
                                        FROM read_csv(
                                            '{arquivo_roa[0]}',
                                            delim='|',
                                            header=true,
                                            encoding='{enc}',
                                            auto_detect=true,
                                            all_varchar=true
                                        )
                                    )
                                    SELECT
                                        *
                                    FROM ROA_BASE t1"""
                        con = duckdb.connect()
                        df = con.execute(sSQL).fetchdf()
                        break
                    except Exception as e:
                        erro[enc] = e
                        df= pd.DataFrame()
                
                if len(df)==0:
                    st.text(erro)
                    raise UserWarning("Você tem problema de codificação do arquivo.")
                LST_MAT = pd.DataFrame(columns=['COD_ITEM','DESCR_ITEM'])
                dt_ARQ = max_arq("LST_MAT", bd, empresa)
                if dt_ARQ:
                    SQLq = f"""
                        SELECT  DISTINCT CAST(COD_ITEM AS TEXT) AS COD_ITEM, DESCR_ITEM
                        FROM LST_MAT t1 WHERE t1.dt_ARQ = {dt_ARQ} 
                        """
                    LST_MAT = pd.read_sql(SQLq, bd)

                LST_ST = pd.DataFrame(columns=['COD_ITEM','DESCR_ITEM'])
                dt_ARQ = max_arq("LST_SERV", bd, empresa)
                if dt_ARQ:
                    SQLq = f"""
                        SELECT DISTINCT CAST(COD_ITEM AS TEXT) AS COD_ITEM, DESCR_ITEM
                        FROM LST_SERV t1 WHERE t1.dt_ARQ = {dt_ARQ} 
                        """
                    LST_ST = pd.read_sql(SQLq, bd)

                LST_CL = pd.DataFrame(columns=['Cd_Cls_Custo', 'Txt_Cls_Custo'])
                dt_ARQ = max_arq("DSC_CLS_CUSTO", bd, empresa)
                if dt_ARQ:
                    SQLq = f"""
                        SELECT DISTINCT Cd_Cls_Custo, Txt_Cls_Custo
                        FROM DSC_CLS_CUSTO t1 WHERE t1.dt_ARQ = {dt_ARQ} 
                        """
                    LST_CL = pd.read_sql(SQLq, bd)

                fontes = [
                            (LST_MAT, 'COD_ITEM', 'DESCR_ITEM', 'DESCR_LCMTO'),
                            (LST_ST, 'COD_ITEM', 'DESCR_ITEM', 'DESCR_LCMTO'),
                            (LST_CL, 'Cd_Cls_Custo', 'Txt_Cls_Custo', 'DESCR_CCUSTO')
                         ]

                df['DESCR_NG'] = pd.NA
                df['DESCR_LCMTO'] = pd.NA
                df['DESCR_CCUSTO'] = pd.NA
                
                for dados, chave, coluna_descr, coluna in fontes:
                    if dados.empty:
                        continue
                    mapa = (dados.set_index(chave)[coluna_descr])
                    descricao = df[chave].map(mapa)
                    df[coluna] = (df[coluna].fillna(descricao))
                dic_NG = {
                            '1' : 'UC/UAR',
                            '2' : 'COM',
                            '3' : 'MOP',
                            '4' : 'ST',
                            '5' : 'JOA',
                            '6' : 'OUTROS',
                        }
                descricao = df['Cd_NG'].map(dic_NG)
                df['DESCR_NG'] = (df['DESCR_NG'].fillna(descricao))
                df.to_sql('DIST_REPT_NG', bd, if_exists='replace', index=False)
                df.to_csv(f'{local}/AIS_ANLS/ROA_VALORES_REPETIDOS_{empresa}.csv', index=False, 
                            sep="|", decimal=',', encoding="Latin-1", header = True)
        else:
            sSQL = "SELECT * FROM DIST_REPT_NG"
            df = pd.read_sql(sSQL, bd)

        df = df.copy()
        COL_DT = "Dt_Lcmto"
        COL_VL = "VL_tot"
        df[COL_DT] = pd.to_datetime(df[COL_DT], errors='coerce', dayfirst=True)
        df['VL_CTVOS'] = ((df[COL_VL] * 100).round().astype('Int64'))
        df['TRI'] = (df[COL_DT].dt.to_period('Q'))
        df['FREQ_GLOBAL'] = df.groupby('VL_CTVOS', dropna=False)['VL_CTVOS'].transform('size').astype('Int64')
        df['FREQ_TRI'] = df.groupby(['TRI', 'VL_CTVOS'], dropna=False)['VL_CTVOS'].transform('size').astype('Int64')

        base = df.dropna(subset=['TRI', 'VL_CTVOS']).copy()
        if base.empty:
            st.warning("Não há lançamentos válidos para análise.")
            return
        
        st.divider()
        st.html(f"""
                    <h3 style="text-align:center;font-size:30px;">
                    Recorrência de valores monetários — {html.escape(str(empresa))}
                    </h3>
                    <p style="text-align: justify;text-indent: 40px">
                    Abaixo, podemos selecionar os trimestres para análise, caso haja efeitos temporais significativos.</p>
                """)

        trimestres = sorted(base["TRI"].unique())
        selecionados = st.multiselect(
                                            "Período de análise",
                                            options=trimestres,
                                            default=trimestres,
                                            format_func=lambda x: str(x)
                                        )
        if not selecionados:
            st.info("Selecione pelo menos um trimestre.")
            return
        base = base[base["TRI"].isin(selecionados)].copy()
        repetidos = base[base["FREQ_TRI"] > 1]
        
        total_lanc = len(base)
        total_rep = len(repetidos)
        montante_total = base[COL_VL].abs().sum()
        montante_rep = repetidos[COL_VL].abs().sum()
        montante_pos = base[base[COL_VL]>0][COL_VL].abs().sum()
        montante_neg = base[base[COL_VL]<0][COL_VL].abs().sum()

        pct_lanc = (100 * total_rep / total_lanc if total_lanc else 0)
        pct_valor = (100 * montante_rep / montante_total if montante_total else 0)

        st.html(
                    f"""<p style="text-align: justify;text-indent: 40px">
                    A análise dos indicadores financeiros do ROA permite avaliar a materialidade, a recorrência e a composição dos 
                    lançamentos, constituindo instrumento para a fiscalização da consistência e da rastreabilidade dos registros 
                    apresentados pela concessionária. O montante analisado expressa a dimensão financeira do universo examinado, 
                    enquanto o percentual de lançamentos recorrentes e o respectivo montante evidenciam a frequência e a 
                    representatividade econômica de valores monetários idênticos, permitindo identificar concentrações que 
                    demandem melhor entendimento durante o processo fiscalizatório. A participação financeira dos valores 
                    recorrentes complementa essa avaliação ao dimensionar sua relevância relativa no conjunto das operações. 
                    Por sua vez, a segregação entre montantes positivos e negativos, associada à participação dos valores negativos 
                    e à apuração do montante líquido, possibilita examinar a magnitude dos ajustes, estornos e demais registros 
                    redutores, bem como seus efeitos sobre o resultado consolidado.</p>
                    """
                )
        c1, c2, c3, c4 = st.columns([3,1,3,1], gap='small')
        c5, _, c7, c8 = st.columns([3,1,3,1], gap='small')
        c9, _, _, _ = st.columns([3,1,3,1], gap='small')
        rel = montante_neg / montante_pos * 100

        c1.metric("Montante analisado", moeda(montante_total))
        c2.metric("Lançamentos recorrentes", percentual(pct_lanc))
        c3.metric("Montante recorrente",moeda(montante_rep))
        c4.metric("Participação financeira",percentual(pct_valor))
        c5.metric("Montante positivo",moeda(montante_pos))
        c7.metric("Montante negativo",moeda(montante_neg))
        c8.metric("Participação valores negativos",percentual(rel))
        c9.metric("Montante líquido",moeda(montante_pos - montante_neg))

        st.caption(
                        f"{total_lanc:,} lançamentos analisados | ".replace(",",".") +
                        f"{total_rep:,} associados a valores repetidos | ".replace(",",".") +
                        f"{len(selecionados)} trimestres"
                    )

        st.divider()
        resumo = (
                    base.groupby("TRI")
                    .agg(
                        LANCAMENTOS=(COL_VL, "size"),
                        VALORES_DISTINTOS=("VL_CTVOS", "nunique"),
                        MONTANTE_ABS=(COL_VL, lambda x: x.abs().sum())
                    )
                )

        resumo_rep = (
                        repetidos.groupby("TRI")
                        .agg(
                            LANC_REPETIDOS=(COL_VL, "size"),
                            MONTANTE_REPETIDO=(
                                COL_VL, lambda x: x.abs().sum()
                            )
                        )
                    )

        resumo = resumo.join(resumo_rep).fillna(0)
        resumo["PCT_LANC_REPETIDOS"] = (
                                            100 * resumo["LANC_REPETIDOS"]
                                            / resumo["LANCAMENTOS"]
                                        )

        resumo["PCT_VALOR_REPETIDO"] = (
                                            100 * resumo["MONTANTE_REPETIDO"]
                                            / resumo["MONTANTE_ABS"].replace(0, np.nan)
                                        )
        total_recorrente = resumo['MONTANTE_REPETIDO'].sum()
        resumo['PCT_CONCENTRACAO'] = (
                                        100 * resumo['MONTANTE_REPETIDO']
                                        / total_recorrente
                                        if total_recorrente > 0
                                        else 0.0
                                    )
        total_periodo = resumo['MONTANTE_ABS'].sum()
        resumo['PCT_EXPOSICAO_GLOBAL'] = (
                                            100 * resumo['MONTANTE_REPETIDO']
                                            / total_periodo
                                            if total_periodo > 0
                                            else 0.0
                                        )
        resumo = resumo.sort_index()

        fig, ax = plt.subplots(figsize=(12, 5))
        x = np.arange(len(resumo))
        ax2 = ax.twinx()
        barras = ax2.bar(
                            x,
                            resumo['MONTANTE_REPETIDO'] / 1_000_000,
                            width=0.55,
                            color='lightsteelblue',
                            alpha=0.45,
                            label='Montante recorrente (R$ milhões)',
                            zorder=1
                        )

        linha1, = ax.plot(
                                x,
                                resumo['PCT_LANC_REPETIDOS'],
                                marker='o',
                                linewidth=2,
                                color='steelblue',
                                label='Lançamentos recorrentes',
                                zorder=3
                            )

        linha2, = ax.plot(
                            x,
                            resumo['PCT_VALOR_REPETIDO'],
                            marker='s',
                            linewidth=2,
                            color='darkorange',
                            label='Participação financeira recorrente',
                            zorder=3
                        )

        ax.set_zorder(ax2.get_zorder() + 1)
        ax.patch.set_visible(False)
        ax.set_xticks(x)
        ax.set_xticklabels(resumo.index.astype(str),rotation=45)
        ax.set_ylabel('Participação (%)')
        ax2.set_ylabel('Montante recorrente (R$ milhões)')
        ax.set_ylim(0, 105)
        ax2.set_ylim(bottom=0)
        ax.grid(axis='y', linestyle='--', alpha=0.35)
        ax.set_axisbelow(True)

        for eixo in (ax, ax2):
            for lado in ('top',):
                eixo.spines[lado].set_visible(False)

        ax.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)

        ax.legend(
                    [linha1, linha2, barras],
                    [
                        'Lançamentos recorrentes',
                        'Participação financeira recorrente',
                        'Montante recorrente (R$ milhões)'
                    ],
                    loc='upper left',
                    frameon=False
                )

        ax.legend(frameon=False)

        fig.tight_layout()
        st.html(
                    f"""<p style="text-align: justify;text-indent: 40px">
                    A evolução trimestral dos indicadores de recorrência monetária
                    apresenta a tendência da proporção de lançamentos
                    com valores globais repetidos, acompanhada de sua 
                    representatividade financeira. A ideia é avaliar sobre o ciclo
                    os comportamentos e as tendências.</p>
                    """
                )
        st.pyplot(fig)
        plt.close(fig)

        tri_maior_freq = resumo["PCT_LANC_REPETIDOS"].idxmax()
        tri_menor_freq = resumo["PCT_LANC_REPETIDOS"].idxmin()
        tri_maior_valor = resumo['MONTANTE_REPETIDO'].idxmax()
        maior_freq = resumo.loc[tri_maior_freq, "PCT_LANC_REPETIDOS"]
        menor_freq = resumo.loc[tri_menor_freq, "PCT_LANC_REPETIDOS"]
        maior_valor = resumo.loc[tri_maior_valor, 'MONTANTE_REPETIDO']
        concentracao = resumo.loc[tri_maior_valor, 'PCT_CONCENTRACAO']

        st.html(
                f"""<p style="text-align:justify;text-indent:40px;line-height:1.7">
                A análise da evolução trimestral evidencia a distribuição
                temporal da recorrência monetária sob duas perspectivas
                complementares: a frequência relativa dos lançamentos e
                sua materialidade financeira. No período examinado,
                {percentual(pct_lanc)} dos lançamentos apresentaram
                valores globais repetidos em seus respectivos trimestres,
                correspondendo a {percentual(pct_valor)} do montante
                absoluto analisado. A maior recorrência quantitativa
                foi registrada em {tri_maior_freq}, com
                {percentual(maior_freq)}, enquanto a menor ocorreu em
                {tri_menor_freq}, com {percentual(menor_freq)}.
                Sob a perspectiva financeira, destaca-se {tri_maior_valor},
                com montante recorrente de {moeda(maior_valor)},
                equivalente a {percentual(concentracao)} da exposição
                recorrente total do período. </p>
                """
                )

        st.info(
                    "A recorrência monetária é um indicador exploratório. "
                    "Valores repetidos podem decorrer de preços padronizados, "
                    "contratos recorrentes ou características operacionais. "
                )

        st.divider()

        dados = base.copy()
        dados['VALOR_ABS'] = dados[COL_VL].abs()
        dados = dados[np.isfinite(dados['VALOR_ABS']) & (dados['VALOR_ABS'] > 0)]
        dados = dados[dados['VALOR_ABS'] > 0]

        trimestres = sorted(dados['TRI'].unique())
        if dados.empty:
            st.warning("Sem valores positivos em módulo para o gráfico.")
            return
        else:
            st.html(
                            "<p style='text-align:justify;text-indent:40px;'>Abaixo, temos os histogramas com escalas " \
                            "logarítmicas nos dois eixos, por trimestre. "
                            "As faixas monetárias são comuns a todos os trimestres.</p>"
                        )
            minimo = dados['VALOR_ABS'].min()
            maximo = dados['VALOR_ABS'].max()

            if minimo == maximo:
                minimo /= 1.1
                maximo *= 1.1

            bins = np.logspace(np.log10(minimo), np.log10(maximo), 45)

            ncols = 2
            nrows = math.ceil(len(trimestres) / ncols)

            fig, axes = plt.subplots(nrows, ncols, figsize=(14, 4 * nrows), squeeze=False)

            for ax, trimestre in zip(axes.flat, trimestres):
                valores = dados.loc[dados['TRI'] == trimestre, 'VALOR_ABS']
                ax.hist(
                            valores,
                            bins=bins,
                            edgecolor='white',
                            color="steelblue", 
                            alpha=0.8
                        )

                ax.set_xscale('log')
                ax.set_yscale('log')
                ax.set_title(str(trimestre))
                ax.set_xlabel('Valor global absoluto (R$)')
                ax.set_ylabel('Frequência')
                ax.grid(axis="x", linestyle="--", alpha=0.35)
                ax.set_axisbelow(True)
                for lado in ("top", "right"):
                    ax.spines[lado].set_visible(False)

            for ax in axes.flat[len(trimestres):]:
                ax.set_visible(False)

            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        st.divider()
        freq = (
                    base.groupby(["TRI", "VL_CTVOS"])
                    .agg(
                        FREQUENCIA=(COL_VL, "size"),
                        VALOR_GLOBAL=(COL_VL, "first"),
                        MONTANTE=(COL_VL, "sum")
                    )
                    .reset_index()
                )

        freq["MONTANTE_ABS"] = (freq["VALOR_GLOBAL"].abs() * freq["FREQUENCIA"])
        freq["EXCESSO_REPETICOES"] = (freq["FREQUENCIA"] - 1)
        freq_rep = freq[freq["FREQUENCIA"] > 1].copy()
        if freq_rep.empty:
            st.info(
                        "Não foram identificados valores repetidos "
                        "nos trimestres selecionados."
                    )
        else:
            criterio = st.radio("Ordenar valores por",
                                    [
                                        "Montante financeiro",
                                        "Número de ocorrências"
                                    ],
                                    horizontal=True
                                )

            coluna_ordem = ("MONTANTE_ABS" if criterio == "Montante financeiro" else "FREQUENCIA")
            top = (
                        freq_rep.sort_values(
                            coluna_ordem,
                            ascending=False
                        )
                        .head(20)
                        .copy()
                    )

            top["TRI"] = top["TRI"].astype(str)
            st.dataframe(
                top[
                    [
                        "TRI",
                        "VALOR_GLOBAL",
                        "FREQUENCIA",
                        "MONTANTE_ABS",
                        "EXCESSO_REPETICOES"
                    ]
                ],
                column_config={
                    "TRI": "Trimestre",
                    "VALOR_GLOBAL": st.column_config.NumberColumn(
                        "Valor global",
                        format="R$ %.2f"
                    ),
                    "FREQUENCIA": "Ocorrências",
                    "MONTANTE_ABS": st.column_config.NumberColumn(
                        "Montante absoluto",
                        format="R$ %.2f"
                    ),
                    "EXCESSO_REPETICOES": "Repetições adicionais"
                },
                hide_index=True,
            )

        vis_AX002ax(bd, caminho, empresa, st, local, df)

@st.fragment
def vis_AX003(bd_path, caminho, empresa, st): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('ROS_VAL', bd):
            return 

        st.divider()
        st.html(f"""
                    <h3 style="text-align: center;font-size: 30px;">
                    <u>Resultado do ROS VALIDADO simulado</u></h3>
                    """)
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                    consistência entre o ROS Validado simulado e o entregue pela empresa.
                    Você deve justificar quando os valores forem divergentes. 
                    Abaixo é apresentado apenas os resultados, leie o relatório para análise completa.</p><br>
                    """)
        sSQL = """
                SELECT * FROM ROS_VAL

            """
        ANL_LST_TUC = pd.read_sql(sSQL, bd)
        for n in ANL_LST_TUC.columns.to_list():
            if (n[:2].upper() == 'VL') & pd.api.types.is_numeric_dtype(ANL_LST_TUC[n]):
                ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True)

@st.fragment
def vis_AX004(bd_path, caminho, empresa, st): 
    return None

@st.fragment
def vis_AX005(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('tst_pct_est', bd):
            return

        sSQL = """
                SELECT projeto, total, estornos, pct_estornos
                FROM tst_pct_est

            """
        txtMOVOBRAS = pd.read_sql(sSQL, bd)
        config = {
                    "projeto": st.column_config.TextColumn("Projeto Avaliado"),
                    "total": st.column_config.TextColumn("Número de lançamentos do projeto"),
                    "estornos": st.column_config.TextColumn("Número de estornos do projeto"),
                    "pct_estornos": st.column_config.TextColumn("Percentual de estornos do projeto"),
                }

        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Resumo do percentual de lançamentos negativos da {empresa} durante o projeto</h3>
                    """)
        
        qtd_pct = f"{len(txtMOVOBRAS[txtMOVOBRAS['pct_estornos']>10])/len(txtMOVOBRAS):.2%}".replace(".",",")
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Apresentamos as estatísticas de estornos 
                    contábeis por projeto a partir de um arquivo CSV, considerando o valor negativo na coluna 
                    'VL_tot' como indicador de estorno. Encontramos {len(txtMOVOBRAS)}
                    projetos com estas características. Destes, {qtd_pct} apresentam uma quantidade de estornos
                    significativa (>10% da quantidade de lançamentos). Verificar os motivos determinantes.</p><br>
                    """)
        st.dataframe(txtMOVOBRAS.head(100), width='stretch', hide_index=True,  column_config=config)

        if not existe_tabela('tst_pct_est_dt', bd):
            return

        sSQL = """
                SELECT data, estornos, total
                FROM tst_pct_est_dt

            """
        txtMOVOBRAS = pd.read_sql(sSQL, bd)

        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Resumo do percentual de estornos da {empresa} por data</h3>
                    """)
        
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Os gráficos a seguir, apresentam
                    a distribuição no tempo dos estornos e dos lançamentos.</p><br>
                    """)

        total = txtMOVOBRAS['total'].sum()
        txtMOVOBRAS['percentual_total'] = txtMOVOBRAS['total'] / total * 100
        txtMOVOBRAS['data'] = pd.to_datetime(txtMOVOBRAS['data'])
        total = txtMOVOBRAS['estornos'].sum()
        txtMOVOBRAS['percentual_estornos_total'] = txtMOVOBRAS['estornos'] / total * 100

        limiar_suspeito = 0.5  # % do total
        df_suspeitos = txtMOVOBRAS[txtMOVOBRAS['percentual_total'] > limiar_suspeito]
        df_suspeitos_est = txtMOVOBRAS[txtMOVOBRAS['percentual_estornos_total'] > limiar_suspeito]

        df_suspeitos['tipo'] = 'lançamento'
        df_suspeitos_est['tipo'] = 'estorno'

        df_suspeitos_total = pd.concat([df_suspeitos, df_suspeitos_est], ignore_index=True)

        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=(12, 6))
        largura = 0.4
        
        x = txtMOVOBRAS['data']
        ax.fill_between(x, txtMOVOBRAS.get('total', 0), step='mid', alpha=0.4, label='Lançamentos', color='tab:blue')
        ax.fill_between(x, txtMOVOBRAS.get('estornos', 0), step='mid', alpha=0.8, label='Estornos', color='tab:red')
        ax.set_title("Concentração de Estornos e Lançamentos", fontsize=16, loc='left')
        ax.set_xlabel("Data")
        ax.set_ylabel("Quantidade")
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
        ax.tick_params(axis='x', rotation=45)

        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend()
        col1g, col2g, col3g = st.columns([1,3,1], gap='small')
        with col2g:
            st.pyplot(fig)
        plt.close()

        fig1, ax1 = plt.subplots(figsize=(12, 6))
        ax1.fill_between(txtMOVOBRAS['data'], txtMOVOBRAS.get('percentual_estornos_total', 0), alpha=0.5, color='tab:blue', label='% dos lançamentos')
        ax1.plot(txtMOVOBRAS['data'], txtMOVOBRAS.get('percentual_estornos_total', 0), color='tab:blue', linewidth=2)

        for _, row in df_suspeitos_est.iterrows():
            ax1.annotate(
                f"{row['percentual_estornos_total']:.1f}%",
                (row['data'], row['percentual_estornos_total']),
                textcoords="offset points",
                xytext=(0, 5),
                ha='center',
                fontsize=9,
                color='crimson'
            )
            ax1.plot(row['data'], row['percentual_estornos_total'], 'o', color='crimson')

        ax1.set_title("Distribuição Percentual dos Estornos ao Longo do Tempo", fontsize=14, loc='left')
        ax1.set_ylabel("Percentual (%)")
        ax1.set_xlabel("Data")
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}%'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=5))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.legend()

        col1h, col2h, col3h = st.columns([1,3,1], gap='small')
        with col2h:
            st.pyplot(fig1)
        plt.close()

        fig2, ax2 = plt.subplots(figsize=(12, 6))
        ax2.fill_between(x, txtMOVOBRAS.get('percentual_total', 0), alpha=0.5, color='tab:blue', label='% dos lançamentos')
        ax2.plot(x, txtMOVOBRAS.get('percentual_total', 0), color='tab:blue', linewidth=2)

        for _, row in df_suspeitos.iterrows():
            ax2.annotate(
                f"{row['percentual_total']:.1f}%",
                (row['data'], row['percentual_total']),
                textcoords="offset points",
                xytext=(0, 5),
                ha='center',
                fontsize=9,
                color='crimson'
            )
            ax2.plot(row['data'], row['percentual_total'], 'o', color='crimson')

        ax2.set_title("Distribuição Percentual dos Lançamentos ao Longo do Tempo", fontsize=14, loc='left')
        ax2.set_ylabel("Percentual (%)")
        ax2.set_xlabel("Data")
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}%'))
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.legend()

        col1i, col2i, col3i = st.columns([1,3,1], gap='small')
        with col2i:
            st.pyplot(fig2)
        plt.close()

        df_suspeitos_total = df_suspeitos_total.sort_values(by = ['data'])
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">A identificação de dias com 
                    percentuais expressivos de lançamentos e estornos indica possíveis concentrações atípicas. 
                    Esses picos podem estar relacionados a lançamentos em  lote, ajustes retroativos, reprocessamentos 
                    sistêmicos ou correções manuais, sendo que se deve verificar a origem dos dados, os responsáveis 
                    pelos registros e a documentação de suporte.</p><br>
                    """)
        st.dataframe(df_suspeitos_total, width='stretch', hide_index=True)
    
        if not existe_tabela('tst_pct_ajst', bd):
            return
        sSQL = """
                SELECT projeto,total_valor,soma_estornos,pct_estorno_valor,
                soma_ajustes_finais,pct_ajuste_finais_valor
                FROM tst_pct_ajst

            """
        txtMOVOBRAS = pd.read_sql(sSQL, bd)
        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Resumo do percentual de ajustes e de estornos da {empresa} por projeto</h3>
                    """)

        vb = len(txtMOVOBRAS[(txtMOVOBRAS['pct_estorno_valor'] >= 10) | (txtMOVOBRAS['pct_ajuste_finais_valor'] >= 10) | (txtMOVOBRAS['pct_ajuste_finais_valor'] <= -10)]) / len(txtMOVOBRAS)
        qtd_pct = f"""{vb:.2%}""".replace(".", ",")
        amst, df_amst = sel_projetos(txtMOVOBRAS)
        dados = ", ".join(amst)
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Apresentamos asestatísticas financeiras 
                    de estornos e ajustes finais por projeto, considerando lançamentos dos últimos 15 dias 
                    de cada obra como ajustes finais. Destes, {qtd_pct} apresentam uma quantidade de estornos ou 
                    de ajustes significativa (>10% do valor total de lançamentos). 
                    Verificar os motivos determinantes para a amostra: <b>{dados}</b>.</p><br>
                    """)

        for n in ['total_valor', 'soma_estornos', 'soma_ajustes_finais']:
            txtMOVOBRAS[n] = txtMOVOBRAS[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        config = {
                "projeto": st.column_config.TextColumn("Projeto Avaliado"),
                "total_valor": st.column_config.TextColumn("Valor total do projeto"),
                "soma_estornos": st.column_config.TextColumn("Valor total de estornos do projeto"),
                "pct_estorno_valor": st.column_config.TextColumn("Percentual de estornos do projeto"),
                "soma_ajustes_finais": st.column_config.TextColumn("Valor total de ajustes do projeto"),
                "pct_ajuste_finais_valor": st.column_config.TextColumn("Percentual de ajustes do projeto"),
            }
        st.dataframe(df_amst[df_amst['FLG_AMST']==1].head(100), width='stretch', hide_index=True,  column_config=config)
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Abaixo a amostra selecionada, 
                    representação gráfica.</p><br>
                    """)

        x = np.arange(len(df_amst))
        y = df_amst["VL_ACUM"]

        limA = df_amst[df_amst["CLS_ABC"] == "A"].index.max()
        limB = df_amst[df_amst["CLS_ABC"] == "B"].index.max()

        fig17b = plt.figure(figsize=(14, 6))
        cmap_line = plt.cm.plasma(0.75)
        cmap_points = plt.cm.plasma(0.25)
        plt.axvspan(0, limA, alpha=0.18, color="#f70a0a")
        plt.axvspan(limA, limB, alpha=0.15, color="#0404f3")
        plt.axvspan(limB, len(df_amst), alpha=0.12, color="#09f567")
        plt.plot(x, y, linewidth=2, color=cmap_line)

        for idx, row in df_amst.iterrows():
            if row["FLG_AMST"] == 1:
                plt.scatter(idx, row["VL_ACUM"], 
                            s=80, 
                            edgecolor="black", 
                            linewidth=1.2, 
                            facecolor=cmap_points)
        plt.title("Curva Acumulada de Projetos com Destaque ABC e Amostragem (AUM)", fontsize=16)
        plt.ylabel("Valor Acumulado", fontsize=12)

        passo = max(1, int(round(len(df_amst) / 10, 0)))
        plt.xticks(
                        x[::passo], 
                        df_amst["projeto"][::passo], 
                        rotation=45, 
                        ha="right",
                        fontsize=12
                    )

        plt.grid(alpha=0.2)
        plt.tight_layout()
        col1ka, col2ka, col3ka = st.columns([1,2,1], gap='small')
        with col2ka:
            st.pyplot(fig17b)
        plt.close()

        plt.savefig(f"{local}//RELATORIOS//figuras//amostra_estornos.png", dpi=300, bbox_inches='tight')
        df_amst.to_csv(f"{local}/AIS_ANLS/AMST_ESTORNOS.csv", index=False, sep="|", decimal=",", encoding="Latin-1")

@st.fragment
def vis_AX006(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('LCMTO_FLX_TEMP', bd):
            return
        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Análise de Fluxo Temporal</h3>
                    """)
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie o tempo
                    empregado para execução das obras, estimado com base nos períodos de 
                    cálculo do JOA, estabelecidos no PRORET. Abaixo é apresentado apenas os 100 primeiros
                    resultados.</p><br>
                    """)
        sSQL = """
                SELECT * FROM LCMTO_FLX_TEMP LIMIT 100

            """
        ANL_LST_TUC = pd.read_sql(sSQL, bd)

        ANL_LST_TUC['VL_tot'] = ANL_LST_TUC['VL_tot'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        config = {}
        for n in ANL_LST_TUC.columns.to_list():
            if n=="Dt_Lcmto":
                nm = "Data do Lançamento"
            elif n[:7] == 'DT_MAXr':
                nm = "Data Máxima para o período " + n[7:]
            elif n[:7] == 'DT_MINr':
                nm = "Data Mínima para o período " + n[7:]
            if n[:2].upper() =='DT':
                config[n] = st.column_config.DateColumn(nm, format="DD/MM/YYYY")

        st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True,  column_config=config)

@st.fragment
def vis_AX007(bd_path, caminho, empresa, st, local, df_CARACT): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('ROS', bd):
            return

        dt_ARQ = max_arq("ROS", bd, empresa)
        if dt_ARQ:
            st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                        Distribuição dos investimentos da {empresa} por projeto</h3>
                        <p style="text-align: justify;text-indent: 40px;">
                        A análise da evolução econômica das obras imobilizadas
                        é realizada a partir dos lançamentos registrados nas respectivas
                        ordens em curso associados
                        à formação dos custos de imobilização. O procedimento examina
                        a distribuição temporal dos registros, a evolução dos valores
                        acumulados, a composição das naturezas de gasto e a continuidade
                        das apropriações econômicas, com o objetivo de identificar
                        padrões para a avaliação da consistência e da rastreabilidade dos investimentos.
                        </p>

                        <p style="text-align: justify;text-indent: 40px;">
                        Os indicadores de <b>centralidade temporal acumulada (CTA)</b>,
                        <b>irregularidade da derivada (ID)</b> e
                        <b>incursões fora da faixa de variação (IRange)</b>
                        caracterizam o comportamento da curva econômica, permitindo
                        examinar a concentração temporal dos valores acumulados,
                        a variabilidade do ritmo de apropriação, as reversões de
                        sentido e a ocorrência de variações de maior intensidade.
                        Complementarmente, o <b>KPI_CRESC</b> quantifica a frequência
                        relativa de reduções no saldo acumulado, enquanto o
                        <b>KPI_PER</b> relaciona a duração observada ao período
                        de referência da obra.
                        </p>

                        <p style="text-align: justify;text-indent: 40px;">
                        Os indicadores de continuidade temporal compreendem o
                        <b>IED</b>, associado à maior duração de estabilidade da
                        curva acumulada, o <b>IEg</b>, referente ao maior intervalo
                        entre lançamentos de qualquer natureza, e o <b>IEuc</b>,
                        relativo aos intervalos entre registros de UC/UAR.
                        O <b>KPI_GAP</b> complementa essa avaliação ao mensurar
                        o período transcorrido desde o último lançamento positivo
                        de UC até o encerramento da janela examinada.
                        Essas medidas auxiliam na identificação de interrupções,
                        descontinuidades e possíveis defasagens no processo
                        de apropriação.
                        </p>

                        <p style="text-align: justify;text-indent: 40px;">
                        A análise da sequência das naturezas de gasto é complementada
                        pelos sinalizadores <b>FLG_MOP</b>, <b>FLG_ST</b> e
                        <b>FLG_JOA</b>, que identificam ocorrências dessas
                        naturezas sem registros de materiais nos dois meses
                        calendários anteriores. A composição é
                        avaliada pelos indicadores <b>CA_TOT</b>, que expressa
                        a participação conjunta de MOP e ST, e <b>UC_TOT</b>,
                        que representa a participação dos lançamentos de UC.
                        Por sua vez, o <b>CMD</b> apresenta o custo médio diário
                        calculado sobre o intervalo temporal observado.
                        </p>

                        <p style="text-align: justify;text-indent: 40px;">
                        Em conjunto, os indicadores constituem instrumentos
                        exploratórios, destinados a evidenciar
                        concentrações financeiras, oscilações, períodos de
                        inatividade e características da composição dos custos
                        de imobilização. Seus resultados devem ser interpretados
                        considerando a natureza da obra, o estágio de execução,
                        a abrangência temporal dos dados e as particularidades
                        dos procedimentos contábeis aplicáveis, não constituindo,
                        isoladamente, comprovação de desconformidade regulatória.
                        </p>
                        """)
            sSQL = f"""
                    SELECT Cd_SubODI
                    FROM ROS WHERE dt_ARQ = {dt_ARQ}

                """
            ROS = pd.read_sql(sSQL, bd)
            cols_AX = st.columns(3, gap="small")
            with cols_AX[0]:
                x1 = st.selectbox(  'Selecione o projeto',
                                    tuple(ROS['Cd_SubODI'].drop_duplicates().to_list()),
                                    index=1,
                                    placeholder="Projeto...",
                                )
                
            if x1:
                df_PR = bsc_proj(f"{local}", x1)
                df_dd = bsc_proj_dd(f"{local}", x1)
                
                if len(df_PR)>0:
                    perc = 0.1
                    df_PR = df_PR.sort_values(by=['data','Cd_NG'])
                    df_PR['cumulativo'] = df_PR['valor'].cumsum()
                    indicadores = calcular_kpis(df_PR, x1, f"{local}", perc, 1, st)
                    interpretacoes = {}

                    # --- CTA ---
                    cta = indicadores['CTA']
                    if abs(cta) < 0.1:
                        interpretacoes['CTA'] = "isso indica que há distribuição temporal bem balanceada de lançamentos"
                    elif cta < -0.5:
                        interpretacoes['CTA'] = "isso indica que há alta concentração de lançamentos no início da série"
                    elif cta > 0.5:
                        interpretacoes['CTA'] = "isso indica que há alta concentração de lançamentos no final da série"
                    else:
                        interpretacoes['CTA'] = "indicando distribuição temporal levemente enviesada de lançamentos"

                    # --- ID ---
                    data_ranges = [
                                    # CV <= 20%, Inversões <= 10%
                                    {
                                        "Faixa CV da derivada": "≤ 20%",
                                        "Faixa % Inversões": "≤ 10%",
                                        "Classificação": "Baixo / Baixo",
                                        "Interpretação": "a obra apresenta taxa de crescimento contínuo, com baixa quantidade de ajustes."
                                    },
                                    # CV <= 20%, Inversões > 10%
                                    {
                                        "Faixa CV da derivada": "≤ 20%",
                                        "Faixa % Inversões": "> 10%",
                                        "Classificação": "Baixo / Alto",
                                        "Interpretação": "a obra apresenta taxa de crescimento contínuo, mas alterna constantemente com ajustes ocorrendo em frequência considerável."
                                    },
                                    # CV > 20%, Inversões ≤ 10%
                                    {
                                        "Faixa CV da derivada": "> 20%",
                                        "Faixa % Inversões": "≤ 10%",
                                        "Classificação": "Alto / Baixo",
                                        "Interpretação": "a obra apresenta variações significativas na taxa de crescimento, indicando boa possibilidade de períodos parados ou lançamentos concentrados ou poucos registros na obra. No entanto, a frequência de ajustes parece baixa."
                                    },
                                    # CV > 20%, Inversões > 10%
                                    {
                                        "Faixa CV da derivada": "> 20%",
                                        "Faixa % Inversões": "> 10%",
                                        "Classificação": "Alto / Alto",
                                        "Interpretação": "a obra apresenta variações significativas na taxa de crescimento, indicando boa possibilidade de períodos parados ou lançamentos concentrados ou poucos registros na obra. Ademais, a frequência de ajustes é alta."
                                    },
                                ]

                    if (indicadores['ID_desv_pad'] <= 0.2) and (indicadores['ID_rev'] <= 0.1):
                        interpretacoes['ID'] = data_ranges[0]['Interpretação']
                    elif (indicadores['ID_desv_pad'] <= 0.2) and (indicadores['ID_rev'] > 0.1):
                        interpretacoes['ID'] = data_ranges[1]['Interpretação']
                    elif (indicadores['ID_desv_pad'] > 0.2) and (indicadores['ID_rev'] <= 0.1):
                        interpretacoes['ID'] = data_ranges[2]['Interpretação']
                    else:
                        interpretacoes['ID'] = data_ranges[3]['Interpretação']

                    # --- IRange ---
                    irange = indicadores['IRange']
                    if irange == 0:
                        interpretacoes['IRange'] = f"não houve lançamentos em que a derivada superou {perc:.2%} do valor da obra"
                    else:
                        interpretacoes['IRange'] = f"{irange} excursão(ões) em que a derivada superou {perc:.2%} do valor da obra"

                    # --- IED ---
                    ied = indicadores['IED_dias']
                    if ied == 0:
                        interpretacoes['IED_dias'] = "quantidade de dias parado não supera limiar regulatório da tipologia"
                    else:
                        interpretacoes['IED_dias'] = "estagnação prolongada detectada, quantidade de dias parado supera limiar regulatório da tipologia"

                    # --- KPI_CRESC ---
                    kpi_cresc = indicadores['KPI_CRESC (%)']
                    if kpi_cresc == 0:
                        interpretacoes['KPI_CRESC (%)'] = "indicando crescimento sempre positivo"
                    elif kpi_cresc < 0.1:
                        interpretacoes['KPI_CRESC (%)'] = "indicando existência de pequenas quedas pontuais, isto é, menos de 10% dos lançamentos conduzem a reduções do acumulado"
                    else:
                        interpretacoes['KPI_CRESC (%)'] = "indicando variações negativas frequentes no acumulado, isto é, 10% ou mais dos lançamento conduzem a reduções do acumulado"

                    # --- KPI_GAP ---
                    kpi_gap = indicadores['KPI_GAP (dias)']
                    if kpi_gap < 30:
                        interpretacoes['KPI_GAP (dias)'] = "indicando que inexiste longos períodos de inatividade recente, antes da unitização"
                    elif kpi_gap < 90:
                        interpretacoes['KPI_GAP (dias)'] = "indicando que há um período relevante de inatividade, antes da unitização, mas dentro dos 90 dias"
                    else:
                        interpretacoes['KPI_GAP (dias)'] = "indicando inatividade prolongada ao final da série, antes da unitização, superior aos 90 dias"

                    # --- KPI_PER ---
                    kpi_gap = indicadores['KPI_PER']
                    if kpi_gap <= 1.0:
                        interpretacoes['KPI_PER'] = "o período da obra encontra-se conforme o perfil regulatório"
                    elif kpi_gap <= 1.5:
                        interpretacoes['KPI_PER'] = "o período da obra encontra-se acima do perfil regulatório"
                    else:
                        interpretacoes['KPI_PER'] = "o período da obra encontra-se muito acima do perfil regulatório"


                    df_cd1_pos = df_PR[(df_PR['Cd_NG'] == 1) & (df_PR['valor'] > 0)]
                    dic_dd = {1: 'UC', 2: 'COM', 3: 'MOP', 4: 'ST', 5: 'JOA', 6: 'OUTROS'}
                    categorias_principais = [1, 2, 3, 4]
                    categoria_outras = [k for k in dic_dd if k not in categorias_principais]

                    # Ordena o df_PR e calcula o acumulado total (uma vez só)
                    df_PR = df_PR.sort_values("data")
                    df_PR["cumulativo"] = df_PR["valor"].cumsum()

                    # Gráficos KPI
                    figEST = plt.figure(figsize=(14, 24))
                    gs = gridspec.GridSpec(7, 1, height_ratios=[1.2]*5 + [1.5, 3], hspace=0.7)

                    cores = plt.cm.get_cmap('rainbow', len(dic_dd))
                    mapa_cores = {cat: cores(i) for i, cat in enumerate(dic_dd)}

                    # Gráficos por categoria
                    data_min = df_PR['data'].min()
                    data_max = df_PR['data'].max() + pd.Timedelta(days=2)
                    for i, cat in enumerate(categorias_principais + ['OUTROS']):
                        if cat == 'OUTROS':
                            df_cat = df_PR[df_PR['Cd_NG'].isin(categoria_outras)]
                            titulo = "Demais Categorias"
                        else:
                            df_cat = df_PR[df_PR['Cd_NG'] == cat]
                            titulo = f"Movimentações – {dic_dd[cat]}"

                        ax = figEST.add_subplot(gs[i])
                        for _, row in df_cat.iterrows():
                            ax.vlines(x=row['data'], ymin=0, ymax=row['valor'], color=mapa_cores.get(row['Cd_NG'], 'black'), linewidth=6)

                        ax.set_title(titulo, fontsize=12, fontweight='bold')
                        ax.set_ylabel("Valor")
                        ax.grid(True)
                        ax.set_xlim(data_min, data_max)
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))

                        if cat == 1 and not df_cd1_pos.empty:
                            ultimo_pos = df_cd1_pos.iloc[-1]
                            data_ultimo_positivo = ultimo_pos['data']
                            valor_ultimo_positivo = ultimo_pos['valor']
                            data_ultimo = df_PR['data'].max()
                            dias_dist = (data_ultimo - data_ultimo_positivo).days

                            ax.plot(data_ultimo_positivo, valor_ultimo_positivo, marker='o', color='red', markersize=10)
                            ax.annotate(f"{dias_dist} dias sem movimentação Cd_NG=1",
                                        xy=(data_ultimo_positivo, valor_ultimo_positivo),
                                        xytext=(10, 40), textcoords='offset points',
                                        arrowprops=dict(arrowstyle="->", color='gray'),
                                        fontsize=9, color='black', backgroundcolor='white')

                    # Gráfico único do acumulado total
                    ax_acum = figEST.add_subplot(gs[5])
                    ax_acum.plot(df_PR['data'], df_PR['cumulativo'], color='blue', linewidth=2, marker='o')
                    ax_acum.set_title("Evolução do Valor Acumulado (Total)", fontsize=14, fontweight='bold')
                    ax_acum.set_ylabel("Valor Acumulado")
                    ax_acum.grid(True)
                    ax_acum.set_xlim(data_min, data_max)
                    ax_acum.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))

                    # Painel de Indicadores
                    gs_inner = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=gs[6], wspace=0.4, hspace=0.8)
                    indicadores_list = list(indicadores.items())

                    for i, (k, v) in enumerate(indicadores_list[:-9]):
                        ax = figEST.add_subplot(gs_inner[i // 4, i % 4])
                        ax.barh([k], [v], color='skyblue')
                        ax.set_xlim(0, max(1, v * 1.2) if v < 100 else 100)
                        ax.set_title(k, fontsize=10)
                        ax.grid(True, axis='x', linestyle='--', alpha=0.7)
                        ax.set_xlabel('Valor')

                    # Remove eixos extras se tiver menos de 8 indicadores
                    indicador_axes = figEST.axes[6:]
                    for ax in indicador_axes[len(indicadores_list):]:
                        figEST.delaxes(ax)

                    # Título geral
                    figEST.suptitle(f'Projeto {x1} – Análise por Categoria, Acumulado Total e Indicadores', fontsize=16, fontweight='bold')

                    # Exibir no Streamlit
                    colsC = st.columns([1,6,1], gap='small')
                    with colsC[1]:
                        st.pyplot(figEST)
                    plt.savefig(f"{local}//RELATORIOS//figuras//tempo_indicadores.png", dpi=300, bbox_inches='tight')
                    plt.close()

                    # --- CMD ---
                    CMD = f"{indicadores['CMD']:,.2f}".replace(".","x").replace(",",".").replace("x",",")
                    if indicadores['CMD'] == 0:
                        interpretacoes['CMD'] = "O valor está zerado."
                    else:
                        interpretacoes['CMD'] = f"O valor médio por dia de projeto é de R$ {CMD}."
                    if indicadores['Nr_TI'] != "ND":
                        if len(df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']])==1:
                            MED = f"{df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']]['media'].iloc[0]:,.2f}".replace(".","x").replace(",",".").replace("x",",")
                            DES_PAD = f"{df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']]['desvio_padrao'].iloc[0]:,.2f}".replace(".","x").replace(",",".").replace("x",",")
                            Q1 = f"{df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']]['q1'].iloc[0]:,.2f}".replace(".","x").replace(",",".").replace("x",",")
                            Q2 = f"{df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']]['q3'].iloc[0]:,.2f}".replace(".","x").replace(",",".").replace("x",",")

                            interpretacoes['CMD'] += f""" Para esta tipologia, {indicadores['Nr_TI']}, temos média de R$ {MED},
                            com desvio padrão de R$ {DES_PAD}. O primeiro quartil é R$ {Q1} e o terceiro quartil é R$ {Q2}."""

                    # --- UC_TOT ---
                    UC_TOT = indicadores['UC_TOT']
                    if UC_TOT == 0:
                        interpretacoes['UC_TOT'] = "entendemos não ser investimento, trata-se de despesa por não ter material capitalizável"
                    elif UC_TOT <= 0.1:
                        interpretacoes['UC_TOT'] = f"chamou atenção a baixa participação de itens capitalizáveis, {UC_TOT:.2%}"
                    else:
                        interpretacoes['UC_TOT'] = f"a participação de itens capitalizáveis é de {UC_TOT:.2%}"

                    try:
                        aa = df_dd['Txt_Desc_PRJ'].iloc[0]
                    except:
                        aa = "sem descrição de ODI"

                    try:
                        bb = df_dd['Dt_Inic_Proj'].iloc[0]
                    except:
                        bb = "sem data de início de projeto"

                    try:
                        vv = df_dd['Dt_Energ'].iloc[0]
                    except:
                        vv = "sem data de energização"

                    try:
                        zz = df_dd['Dt_Uniti'].iloc[0]
                    except:
                        zz = "sem data de unitização"

                    if (indicadores['KPI_PER']>1):
                        texto = f"""
                            <p  style="text-align: justify;text-indent: 40px">Foi analisado os lançamentos do razão de uma obra, {aa}. A obra
                            iniciou em {bb} e foi energizada em {vv}.
                            A transferência para o ativo imobilizado ocorreu em {zz}. Obtemos o valor
                            de {indicadores['KPI_CRESC (%)']:.2%} para a proporção de vezes em que o valor acumulado (coluna 'cumulativo')
                            possui 'quebras' no crescimento (delta de cumulativo < 0); {interpretacoes['KPI_CRESC (%)']}. Obtemos o valor
                            de {indicadores['KPI_GAP (dias)']:.2f} dias sem movimentações positivas de UC/UAR
                            (valor > 0) no final da obra, em relação à data de unitização do projeto; {interpretacoes['KPI_GAP (dias)']}.
                            Obtemos o valor de {indicadores['CTA']:.2f} para a distribuição temporal de lançamentos do projeto; {interpretacoes['CTA']}.
                            Obtemos o valor de {indicadores['ID_desv_pad']:.2%} para irregularidade da derivada e {indicadores['ID_rev']:.2%} para reversões de sentido, dos lançamentos do projeto; {interpretacoes['ID']}
                            Obtemos o valor de {indicadores['IRange']:.2f} para o número de vezes que ocorre uma derivada relevante nos lançamentos do projeto; isto é, {interpretacoes['IRange']}.
                            Obtemos o valor de {int(indicadores['IED_dias'])} para o maior período consecutivo com derivada próxima de zero (em dias) nos lançamentos do projeto; isto é, {interpretacoes['IED_dias']}.
                            Obtemos o valor de {indicadores['KPI_PER']:.2f} para a relação período da obra sobre o regulatório para a TI do projeto; assim, {interpretacoes['KPI_PER']}.
                            No geral, tivemos {indicadores['IEg_dias']} dias como máxima distância entre lançamentos de qualquer natureza de gasto.
                            Por sua vez, tivemos {indicadores['IEuc_dias']} dias como máxima distância entre lançamentos de natureza de gasto de UC/UAR,
                            considerando o último lançamento como proxy de UC/UAR também. Nada obstante, nessa obra temos que cerca de
                            {indicadores['CA_TOT']:.2%} representam os custos de mão de obra no projeto, considerando o valor total da obra.
                            Nesta obra, {interpretacoes['UC_TOT']}. {interpretacoes['CMD']}</p><br>
                            """
                    else:
                        texto = f"""
                            <p  style="text-align: justify;text-indent: 40px">Foi analisado os lançamentos do razão de uma obra, {aa}. A obra
                            iniciou em {bb} e foi energizada em {vv}.
                            A transferência para o ativo imobilizado ocorreu em {zz}.
                            No geral, tivemos {indicadores['IEg_dias']} dias como máxima distância entre lançamentos de qualquer natureza de gasto.
                            Por sua vez, tivemos {indicadores['IEuc_dias']} dias como máxima distância entre lançamentos de natureza de gasto de UC/UAR,
                            considerando o último lançamento como proxy de UC/UAR também.  Nada obstante, nessa obra temos que cerca de
                            {indicadores['CA_TOT']:.2%} representam os custos de mão de obra no projeto, considerando o valor total da obra.
                            Obtemos o valor de {indicadores['KPI_PER']:.2f} para a relação período da obra sobre o regulatório para a TI do projeto; assim, {interpretacoes['KPI_PER']}.
                            Nesta obra, {interpretacoes['UC_TOT']}. {interpretacoes['CMD']}</p><br>
                            """
                    if indicadores['FLG_MOP']:
                        texto += """<p  style="text-align: justify;text-indent: 40px">Há lançamentos de MOP, sem lançamentos de material no mês.</p>"""
                    if indicadores['FLG_ST']:
                        texto += """<p  style="text-align: justify;text-indent: 40px">Há lançamentos de ST, sem lançamentos de material no mês.</p>"""
                    if indicadores['FLG_JOA']:
                        texto += """<p  style="text-align: justify;text-indent: 40px">Há lançamentos de JOA, sem lançamentos de material no mês.</p>"""

                    st.html(texto)

                    exportar_texto( f"{local}//RELATORIOS//textos", 
                                    "IND_DESC.txt", 
                                    texto.replace('  style="text-align: justify;text-indent: 40px"','').replace('<br>',''),
                                    True)
                    
                    if existe_tabela("ANL_OUTLIERS_INDICADORES", bd):
                        df = pd.read_sql("SELECT * FROM ANL_OUTLIERS_INDICADORES", bd)

                        if len(df[df['FLG_OUT']==1])>0:
                            res, amostra_final, IA, R, dd_res_amst = resumo_por_projeto(df = df[df['FLG_OUT']==1].copy(), tipo ="INDICADORES", st = st)

                            st.html("""<p  style='text-align: justify;text-indent: 40px'>Procedeu-se à integração entre a classificação 
                                        ABC e a técnica de Amostragem por Unidade Monetária (AUM/MUS) para seleção dos projetos a 
                                        serem examinados. A classificação ABC permitiu identificar os projetos mais relevantes, enquanto a 
                                        AUM assegurou uma seleção probabilística proporcional ao valor incorrido, conferindo maior 
                                        probabilidade de inclusão aos itens mais representativos da população. Essa abordagem combinada 
                                        fortalece a efetividade dos procedimentos de fiscalização, garantindo que a amostra seja 
                                        estatisticamente robusta, orientada por risco e direcionada para a detecção de potenciais 
                                        distorções materiais. A coluna FLG_AMST identifica os projetos selecionados para verificação 
                                        detalhada. Segue os resultados:</p>""")
                            
                            RESUMOa = res.copy().fillna(0)
                            container8b = st.container(border=True)
                            for n in ['VL_tot','VL_ACUM','Pct_PRJ','Pct_ACM']:
                                if n[:3] == 'Pct':
                                    try:
                                        RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                                    except:
                                        RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{float(x):,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                                else:
                                    try:
                                        RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
                                    except:
                                        RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{float(x):,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
                            
                            container8b.dataframe(RESUMOa, width='stretch', hide_index=True)  

                            st.html(dd_res_amst)

                            R = f"{R:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                            IA = f"{IA:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

                            st.html(f"""<p  style='text-align: justify;text-indent: 40px'> 
                                        Considerando o exposto, o ponto inicial da amostragem foi de R$ {R}, e o total de projetos amostrados foi {len(amostra_final)}, 
                                        sendo que o intervalor amostral foi de R$ {IA}. Interesante mencionarmos que podem exister itens de 
                                        valor muito alto (que acabam ocupando vários intervalos. IA), o número de amostras pode ser grande em 
                                        relação ao tamanho da população ou até o intervalo IA fica muito pequeno em relação aos degraus dos 
                                        projetos. Isso provoca, como consequência, que um dado projeto é selecionado várias vezes, porque ele 
                                        ocupa vários “pontos” do acumulado. Para evitar isso, quando um projeto é sorteado, ele não é reposto
                                        para o sorteio seguinte, isto é, partir do segundo ponto de amostragem, se o projeto correspondente 
                                        já tiver sido selecionado, o algoritmo avança para o próximo projeto elegível na lista ordenada, 
                                        garantindo MUS sem reposição. Isso preserva a proporcionalidade ao valor e elimina duplicidades, 
                                        tornando o sorteio mais eficiente e consistente para finalidade de fiscalização.</p>
                                        <p  style='text-align: justify;text-indent: 40px'> Ademais, para cada projeto pode ocorrer uma quantidade 
                                        significativa de lançamentos, mas lembramos que aqui a unidade de amostragem está sendo o projeto, 
                                        não o lançamento. No caso de haver muitos lançamentos, dentro de cada projeto selecionado, faça uma
                                        amostragem simplificada de lançamentos para validação. O arquivo com as amostras é AMST_INDICADORES.csv, 
                                        disponível no diretório {local}\AIS_ANLS. A seguir temos representação visual do processo.
                                        </p>""")

                            
                            x = np.arange(len(res))
                            y = res["VL_ACUM"]

                            limA = res[res["CLS_ABC"] == "A"].index.max()
                            limB = res[res["CLS_ABC"] == "B"].index.max()

                            fig14b = plt.figure(figsize=(14, 6))
                            cmap_line = plt.cm.plasma(0.75)
                            cmap_points = plt.cm.plasma(0.25)
                            plt.axvspan(0, limA, alpha=0.18, color="#f70a0a")
                            plt.axvspan(limA, limB, alpha=0.15, color="#0404f3")
                            plt.axvspan(limB, len(res), alpha=0.12, color="#09f567")
                            plt.plot(x, y, linewidth=2, color=cmap_line)

                            for idx, row in res.iterrows():
                                if row["FLG_AMST"] == 1:
                                    plt.scatter(idx, row["VL_ACUM"], 
                                                s=80, 
                                                edgecolor="black", 
                                                linewidth=1.2, 
                                                facecolor=cmap_points)
                            plt.title("Curva Acumulada de Projetos com Destaque ABC e Amostragem (AUM)", fontsize=16)
                            plt.ylabel("Valor Acumulado", fontsize=12)

                            passo = max(1, int(round(len(res) / 10, 0)))
                            plt.xticks(
                                            x[::passo], 
                                            res["Cd_SubODI"][::passo], 
                                            rotation=45, 
                                            ha="right",
                                            fontsize=12
                                        )

                            plt.grid(alpha=0.2)
                            plt.tight_layout()
                            col1k, col2k, col3k = st.columns([1,2,1], gap='small')
                            with col2k:
                                st.pyplot(fig14b)
                            plt.close()

                            plt.savefig(f"{local}//RELATORIOS//figuras//amostra_indicadores.png", dpi=300, bbox_inches='tight')
                            res.to_csv(f"{local}/AIS_ANLS/AMST_INDICADORES.csv", index=False, sep="|", decimal=",", encoding="Latin-1")
                            txtAMST = ", ".join(res['Cd_SubODI'].to_list())
                            texto = f"""
                                        <p> 
                                        Considerando o exposto, o ponto inicial da amostragem foi de R$ {R}, e o total de projetos amostrados foi {len(amostra_final)}, 
                                        sendo que o intervalor amostral foi de R$ {IA}. Interesante mencionarmos que podem exister itens de 
                                        valor muito alto (que acabam ocupando vários intervalos. IA), o número de amostras pode ser grande em 
                                        relação ao tamanho da população ou até o intervalo IA fica muito pequeno em relação aos degraus dos 
                                        projetos. Isso provoca, como consequência, que um dado projeto é selecionado várias vezes, porque ele 
                                        ocupa vários “pontos” do acumulado. Para evitar isso, quando um projeto é sorteado, ele não é reposto
                                        para o sorteio seguinte, isto é, partir do segundo ponto de amostragem, se o projeto correspondente 
                                        já tiver sido selecionado, o algoritmo avança para o próximo projeto elegível na lista ordenada, 
                                        garantindo MUS sem reposição. Isso preserva a proporcionalidade ao valor e elimina duplicidades, 
                                        tornando o sorteio mais eficiente e consistente para finalidade de fiscalização.</p>
                                        <p> Foram selecionados os projetos: {txtAMST}. Ademais, para cada projeto pode ocorrer uma quantidade 
                                        significativa de lançamentos, mas lembramos que aqui a unidade de amostragem está sendo o projeto, 
                                        não o lançamento. No caso de haver muitos lançamentos, dentro de cada projeto selecionado, faça uma
                                        amostragem simplificada de lançamentos para validação. A seguir temos representação visual do processo.
                                        </p>
                                    """
                            exportar_texto( f"{local}//RELATORIOS//textos", 
                                        "IND_AMST_DESC.txt", 
                                        texto,
                                        True)
            st.divider()

@st.fragment
def vis_AX008(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('TOT_MED_AIS', bd):
            return

        sSQL = """
                SELECT * FROM TOT_MED_AIS LIMIT 100

            """
        txtMED = pd.read_sql(sSQL, bd)

        for n in ['Qtd_AIS', 'Qtd_COM', 'Qtd_LAUDO', 'DELTA_AIS_COM',
                'DELTA_LAUDO_COM']:
            if n in ['DELTA_AIS_COM','DELTA_LAUDO_COM']:
                txtMED[n] = txtMED[n].apply(lambda x: f"{x}".replace(",", "X").replace(".", ",").replace("X", "."))
            else:
                txtMED[n] = txtMED[n].apply(lambda x: f"{float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        config = {
                "TIPO": st.column_config.TextColumn("Tipo Medidor"),
                "Nr_FASES": st.column_config.TextColumn("Número de fases"),
                "Qtd_AIS": st.column_config.TextColumn("Quantidade total AIS"),
                "Qtd_COM": st.column_config.TextColumn("Quantidade total Comercial"),
                "Qtd_LAUDO": st.column_config.TextColumn("Quantidade total Laudo"),
                "DELTA_AIS_COM": st.column_config.TextColumn("Variação AIS vs Comercial"),
                "DELTA_LAUDO_COM": st.column_config.TextColumn("Variação Laudo vs Comercial"),
                "OBS_SFF_AIS_COM": st.column_config.TextColumn("Observação da variação entre AIS e Comercial"),
                "OBS_SFF_LAUDO_COM": st.column_config.TextColumn("Observação da variação entre Laudo e Comercial"),
            }

        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Resumo dos medidores da {empresa}</h3>
                    """)
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie as diferenças e
                    justifique conforme as observações.</p><br>
                    """)
        st.dataframe(txtMED, width='stretch', hide_index=True,  column_config=config)

@st.fragment
def vis_AX009(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('ANL_ROA_ROS_AIS_OEMG_CMP', bd):
            return
        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Avaliação do ROS vs ROA vs ROD</h3>
                    """)
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie as diferenças e
                    justifique conforme as observações. Abaixo é apresentado apenas os 100 primeiros
                    resultados.</p><br>
                    """)
        sSQL = """
                SELECT * FROM ANL_ROA_ROS_AIS_OEMG_CMP LIMIT 100

            """
        txtMED = pd.read_sql(sSQL, bd)

        for n in ['VL_UC_ROA', 'VL_COM_ROA', 'VL_MOP_ROA', 'VL_ST_ROA', 'VL_JOA_ROA', 
                'VL_OUT_ROA', 'VL_TOT_ROA', 'VL_CA_ST_ODD', 'VL_CA_MOP_ODD', 
                'VL_OE', 'VL_VOC', 'Pct_OE', 'DELTA']:
            txtMED[n] = txtMED[n].fillna(0)
            if n in ['Pct_OE', 'DELTA']:
                txtMED[n] = txtMED[n].apply(lambda x: f"{x:.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
            else:
                txtMED[n] = txtMED[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        config = {
                "Dt_Inic_Proj": st.column_config.DateColumn("Data de Início do Projeto", format="DD/MM/YYYY"),
                "Dt_Energ": st.column_config.DateColumn("Data de Energização", format="DD/MM/YYYY"),
                "Dt_Uniti": st.column_config.DateColumn("Data de Unitização", format="DD/MM/YYYY"),
                "Dt_Lcmto_Min": st.column_config.DateColumn("Data de Lançamento no ROA mínima", format="DD/MM/YYYY"),
                "Dt_Lcmto_Max": st.column_config.DateColumn("Data de Lançamento no ROA máxima", format="DD/MM/YYYY"),
            }
        
        st.dataframe(txtMED, width='stretch', hide_index=True,  column_config=config)

@st.fragment
def vis_AX010(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('ANL_LST_TUC', bd):
            return

        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Lista dos Grupos de UC por TI</h3>
                    """)
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie a pertinencia dos
                    grupos de UC formados por TI. Por exemplo, justificar quando ocorrer um
                    transformador de força em Redes Aéreas. Abaixo é apresentado apenas os 100 primeiros
                    resultados.</p><br>
                    """)
        sSQL = """
                SELECT * FROM ANL_LST_TUC LIMIT 100

            """
        ANL_LST_TUC = pd.read_sql(sSQL, bd)

        for n in ['Qtd', 'VL_tot']:
            if ANL_LST_TUC[n].dtype !=object:
                ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True)

@st.fragment
def vis_AX011(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('ANL_PLATOS_MED', bd):
            return

        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Análise de Platôs em SM</h3>
                    """)
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie se as obras de medição sofreram
                    paralizações superiores a 90 dias, o que chamamos de "platôs", períodos longos de baixa 
                    variação em valor. Caso sim, verifique no gráfico se há
                    melhoras com o tempo (redução de platôs). Para a análise fizemos a apresentação
                    dos platôs por SubODI e data. Adicionalmente, há a distribuição de frequência por
                    datas. O que se espera é uma melhora ao passo que o tempo evolui.</p><br>
                    """)
        sSQL = """
                SELECT * FROM ANL_PLATOS_MED

            """
        df = pd.read_sql(sSQL, bd)

        # Ordenar datas e Cd_SubODI
        df['Dt_Lcmto'] = pd.to_datetime(df['Dt_Lcmto'], errors='coerce')
        df_plato = df[df['FLG_OBR_INT']==1].copy()
        datas = sorted(df['Dt_Lcmto'].unique())
        subodis = sorted(df['Cd_SubODI'].unique())
        # Mapa de cores por projeto
        projetos = df['Nr_TI'].unique()
        cores = sns.color_palette("hls", n_colors=len(projetos))
        mapa_cores = dict(zip(projetos, cores))

        # Criar figura matplotlib
        fig, ax = plt.subplots(figsize=(15,10))
        gs = gridspec.GridSpec(2, 1, height_ratios=[4, 1])
        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1], sharex=ax1)
        ax3 = ax2.twinx()  
        ax3.set_ylim(0, 1)

        # Plotar cada retângulo onde is_plato == True
        for _, row in df.iterrows():
            if row['FLG_OBR_INT']:
                x = datas.index(row['Dt_Lcmto'])
                y = subodis.index(row['Cd_SubODI'])
                cor = mapa_cores[row['Nr_TI']]
                ax1.add_patch(patches.Rectangle((x, y), 20, 5, color=cor))

        
    
        legenda = [
            patches.Patch(color=mapa_cores[ti], label=f'{ti}')
            for ti in projetos
        ]
        ax1.legend(handles=legenda, title="TI", bbox_to_anchor=(1.05, 1), loc='upper left')

        # Eixos e labels
        ax1.set_xlim(0, len(datas))
        ax1.set_ylim(0, len(subodis))
        xticks_pos = np.linspace(0, len(datas) - 1, min(len(datas), 10), dtype=int)
        xticks_labels = [datas[i].strftime('%Y-%m-%d') for i in xticks_pos]
        ax1.set_xticks(xticks_pos)
        ax1.set_xticklabels(xticks_labels, rotation=45)
        yticks_pos = np.linspace(0, len(subodis) - 1, min(len(subodis), 10), dtype=int)
        yticks_labels = [subodis[i] for i in yticks_pos]
        ax1.set_yticks(yticks_pos)
        ax1.set_yticklabels(yticks_labels)
        ax1.set_ylabel("Cd_SubODI") 
        ax1.set_title("Análise Temporal de Platôs")
        ax1.grid(False)

        contagem_por_data = df_plato.groupby('Dt_Lcmto').size().reindex(datas, fill_value=0)
        x_vals = list(range(len(datas)))
        y_vals = contagem_por_data.values

        ax2.plot(x_vals, y_vals, color='lightblue', marker='o', linewidth=1.5)
        ax3.plot(x_vals, y_vals/ y_vals.max(), color='black', linewidth=1.5)

        df_plato['mes'] = df_plato['Dt_Lcmto'].dt.to_period('D')
        serie_mensal = df_plato.groupby('mes').size().sort_index()
        serie_mensal.index = serie_mensal.index.to_timestamp()
        serie_mensal = serie_mensal.reindex(pd.date_range(start=min(datas), end=max(datas), freq='D'), fill_value=0)
        media_movel = serie_mensal.rolling(window=7, center=True, min_periods=1).mean()
        media_movel_plot = media_movel.reindex(datas, fill_value=0)
        x_vals = np.arange(len(datas))
        ax2.plot(x_vals, media_movel_plot.values, color='red', linewidth=2, label='Média móvel semanal')
        ax2.legend()

        ax3.set_ylabel("Valor normalizado de platôs")
        ax2.set_ylabel("Quantidade de platôs")
        ax2.set_xlabel("Data")
        ax2.set_ylim(0, max(y_vals) + 1)

        # Eixo X (datas)
        xticks_pos = np.linspace(0, len(datas) - 1, min(len(datas), 10), dtype=int)
        xticks_labels = [datas[i].strftime('%Y-%m-%d') for i in xticks_pos]
        ax2.set_xticks(xticks_pos)
        ax2.set_xticklabels(xticks_labels, rotation=45)
        ax2.set_title("Distribuição de platôs por data")

        # Tira rótulos do eixo X no gráfico de cima
        ax2.grid(True)
        plt.setp(ax1.get_xticklabels(), visible=False)
        fig.tight_layout(rect=[0, 0, 0.95, 1])
        for ax in fig.axes:
            if ax not in [ax1, ax2, ax3]:
                ax.set_visible(False)
        col1l, col2l, col3l = st.columns([1,3,1], gap='small')
        with col2l:
            st.pyplot(fig)
        plt.close()

@st.fragment
def vis_AX012(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('RESUMO_AJS_RAC_COM', bd):
            return

        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Análise de Racionalização de COM</h3>
                    """)
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                    racionalização de COM, para as obras de redes aéreas rurais e urbanas. Você
                    deve justificar quando os valores forem superiores. Abaixo é apresentado 
                    apenas os 100 primeiros resultados, leia o relatório para 
                    análise completa.</p><br>
                    """)
        sSQL = """
                SELECT * FROM RESUMO_AJS_RAC_COM LIMIT 100

            """
        ANL_LST_TUC = pd.read_sql(sSQL, bd)
        for n in ANL_LST_TUC.columns.to_list():
            if n[:2].upper() == 'VL':
                ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True)

@st.fragment
def vis_AX013(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('ANL_ROS_ODD_CA', bd):
            return

        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Análise de ODD</h3>
                    """)
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                    consistência de ODD com ROS, para as diferentes tipologias. Você
                    deve justificar quando os valores forem divergentes. Abaixo é apresentado 
                    apenas os 100 primeiros resultados, leia o relatório para 
                    análise completa.</p><br>
                    """)
        sSQL = """
                SELECT * FROM ANL_ROS_ODD_CA WHERE Cd_ODD IS NOT NULL LIMIT 100

            """
        ANL_LST_TUC = pd.read_sql(sSQL, bd)
        for n in ANL_LST_TUC.columns.to_list():
            if n[:2].upper() == 'VL':
                ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True)

@st.fragment
def vis_AX014(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('Tst_QTD_MAT_ROA_OBR_EM', bd):
            return

        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Análise de Obras Emergenciais</h3>
                    """)
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                    consistência de Obras Emergenciais com demais arquivos, como quantitativo de
                    material entre ROA e Obras Emergenciais. Você
                    deve justificar quando os valores forem divergentes. Abaixo é apresentado 
                    apenas os 100 primeiros resultados, leie o relatório para 
                    análise completa.</p><br>
                    """)
        sSQL = """
                SELECT * FROM Tst_QTD_MAT_ROA_OBR_EM LIMIT 100

            """
        ANL_LST_TUC = pd.read_sql(sSQL, bd)
        for n in ANL_LST_TUC.columns.to_list():
            if n[:2].upper() == 'VL':
                ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True)

@st.fragment
def vis_AX015(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('Tst_LDAvB', bd):
            return

        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Análise Lado A vs Lado B</h3>
                    """)
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                    consistência das origens dos materiais imobilizados e apresentados no arquivo
                    INCREMENTAL. Você deve justificar quando os valores forem divergentes. 
                    Abaixo é apresentado apenas os 100 primeiros resultados, leie o relatório para análise completa.</p><br>
                    """)
        sSQL = """
                SELECT * FROM Tst_LDAvB LIMIT 100

            """
        ANL_LST_TUC = pd.read_sql(sSQL, bd)
        for n in ANL_LST_TUC.columns.to_list():
            if n[:2].upper() == 'VL':
                ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True)

@st.fragment
def vis_AX016(bd_path, caminho, empresa, st, local): 
    if os.path.isfile(f'{local}/AIS_ANLS/ROA_AJS_SERV_{empresa}.csv'):
        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Análise de Racionalização de Serviços</h3>
                    """)
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Abaixo tem-se o resultado de racionalização
                    de serviços.</p><br>
                    """)
        df_rac_serv = pd.read_csv(f'{local}/AIS_ANLS/ROA_AJS_SERV_{empresa}.csv',sep="|")
        for n in df_rac_serv.columns.to_list():
            if (n[:2].upper() in ['VL','QT'])  and (df_rac_serv[n].dtype !=object):
                df_rac_serv[n] = df_rac_serv[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        container1 = st.container(border=True)
        container1.dataframe(df_rac_serv, width='stretch', hide_index=True)

@st.fragment
def vis_AX017(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('txtALERTAS', bd):
            return

        sSQL = """
                SELECT * FROM txtALERTAS LIMIT 100

            """
        txtALERTAS = pd.read_sql(sSQL, bd)

        config = {
                        "Id_SEQ": st.column_config.TextColumn("Código Linha Arquivo de Origem"),
                        "Nm_Arq": st.column_config.TextColumn("Arquivo de Origem"),
                        "OBS_FISC": st.column_config.TextColumn("Observação a ser tratada"),
                    }
        
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">A seguir iremos apresentar
                    alguns alertas sobre os arquivos associados ao AIS. Por favor, acesse o relatório
                    completo e justifique cada observação.</p><br>
                    """)
        nr_ALERTAS = 100
        container = st.container(border=True)
        for i in range(0, len(txtALERTAS), nr_ALERTAS):
            container.html(f"""<h2 style="text-align: center;">Alertas (de {i*100} a {(i+1)*100} linhas)</h2>
                    """)
            container.dataframe(txtALERTAS[i:i+nr_ALERTAS], width='stretch', hide_index=True,  column_config=config)

@st.fragment
def vis_AX018(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('INCR', bd):
            return

        st.html(f"""<h2 style="text-align: center;font-size: 30px;">
                    <u>Testes Estatísticos</u></h2>
                    """)
        if not existe_tabela('tbl_anomalias_cmu', bd):
            with st.spinner("Fazendo a análise Isolation Forest..."):
                x = TCCU(st)
        sSQL = """
                SELECT * FROM tbl_anomalias_cmu

            """
        tbl_anomalias_cmu = pd.read_sql(sSQL, bd)
        FT = f"{len(tbl_anomalias_cmu[tbl_anomalias_cmu['ANOMALIA'] != 'NO']) / len(tbl_anomalias_cmu):,.2%}".replace(".","x").replace(",",".").replace("x",",")
        REG = f"{len(tbl_anomalias_cmu):,.0f}".replace(".","x").replace(",",".").replace("x",",")
        VL_VOCpr = f"{tbl_anomalias_cmu[tbl_anomalias_cmu['ANOMALIA'] != 'NO']['VL_VOC'].sum():,.2f}".replace(".","x").replace(",",".").replace("x",",")
        VL_VOC = f"{tbl_anomalias_cmu['VL_VOC'].sum():,.2f}".replace(".","x").replace(",",".").replace("x",",")
        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Detecção de outliers multivariados (Isolation Forest)</h3>
                    """)
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Algoritmo de detecção de anomalias 
                    baseado na busca de valores diferentes do padrão da população. Nesse caso, o Isolation Forest cria 
                    diversas árvores de decisão aleatórias que dividem iterativamente o conjunto de dados, 
                    e considera como anômalos os pontos que são isolados com poucas divisões, pois estão 
                    mais distantes do padrão geral. O que fizemos foi separar o arquivo do razão após ajustes da
                    avaliadora em seus custos unitários, por natureza de gasto sendo que Mão de Obra foi classificada
                    como CA. Depois, consideramos os atributos TI e tucagem (TUC + A1-6) para extratificar a população
                    em subgrupos que fariam sentido do ponto de vista técnico. Para evitarmos conjuntos com poucos elementos,
                    isolamos as TI de maior ocorrência (40, 41, 93, 96), retiramos combinações que pouco aparecem e
                    aplicamos o algoritmo. A ideia é que o modelo aprenda o padrão multivariado típico desses custos 
                    (como eles se relacionam entre si). Quando um registro tem combinações de custos que fogem do 
                    comportamento esperado, dado pela prórpia população, ele é marcado e deve ser avaliado. Aqui, {FT}, ou
                    R$ {VL_VOCpr}, são tratados como anômalos, de {REG} registros analisados, R$ {VL_VOC}.</p><br>
                    """)
        container2 = st.container(border=True)
        container2.dataframe(tbl_anomalias_cmu.head(10000), width='stretch', hide_index=True)

@st.fragment
def vis_AX019(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('ROA', bd):
            return
 
        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Teste de Densidade de Atributos Técnicos</h3>
                    """)   
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Aplica o método de estimativa de densidade por 
                    kernel (KDE – Kernel Density Estimation) para identificar valores atípicos em atributos técnicos 
                    contínuos, como tensões, potências ou alturas, dentro de grupos de ativos homogêneos. A técnica 
                    calcula a probabilidade de ocorrência de cada valor em relação à distribuição geral e classifica 
                    como anômalos aqueles pertencentes às regiões de menor densidade (tipicamente os 5% menos frequentes). 
                    </p><br>
                    """)     
        if not existe_tabela('tbl_atributos_anomalos', bd):
            with st.spinner("Fazendo a análise de densidade..."):
                x = TCKdE(st)
        if not existe_tabela('tbl_atributos_anomalos_A1A6', bd):
            with st.spinner("Fazendo a análise de densidade..."):        
                x = TCKdEa1a6(st)

        sSQL = """
                SELECT * FROM tbl_atributos_anomalos

            """
        tbl_atributos_anomalos = pd.read_sql(sSQL, bd)
        REG = f"{len(tbl_atributos_anomalos):,.0f}".replace(".","x").replace(",",".").replace("x",",")
        
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px"> 
                    Essa abordagem permite detectar automaticamente possíveis erros de cadastro, unidade ou parametrização 
                    técnica, oferecendo um indicativo estatístico para priorizar revisões de campo ou correções nos 
                    registros de engenharia. Aqui, foram encontrados {REG} registros que requerem avaliação.</p><br>
                    """)
        container3 = st.container(border=True)
        container3.dataframe(tbl_atributos_anomalos, width='stretch', hide_index=True)

        sSQL = """
                SELECT * FROM tbl_atributos_anomalos_A1A6

            """
        tbl_atributos_anomalos_A1A6 = pd.read_sql(sSQL, bd)
        REG1 = f"{len(tbl_atributos_anomalos_A1A6):,.0f}".replace(".","x").replace(",",".").replace("x",",")
        
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px"> 
                    Essa abordagem permite detectar automaticamente possíveis erros de cadastro, unidade ou parametrização 
                    técnica, oferecendo um indicativo estatístico para priorizar revisões de campo ou correções nos 
                    registros de engenharia. Aqui, foram encontrados {REG1} registros que requerem avaliação, considerando
                    a classificação A1-6 fornecida.</p><br>
                    """)
        container4 = st.container(border=True)
        container4.dataframe(tbl_atributos_anomalos_A1A6.head(1000), width='stretch', hide_index=True)

@st.fragment
def vis_AX020(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        Dt_ARQ = max_arq('ROA', bd, empresa)
        if not Dt_ARQ:
            return
        
        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    <u>Resultado da distribuição de Benford para o ROA</u></h3>
                    """)
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px"> Apresenta-se, a seguir, o resumo da análise de 
                    conformidade dos dois primeiros dígitos significativos dos lançamentos com a distribuição teórica 
                    da Lei de Benford, considerando os registros com valor absoluto igual ou superior a R$ 100,00. 
                    A metodologia utiliza o teste global de aderência qui-quadrado de Pearson (χ²), com nível de 
                    significância de 5% e, quando necessário, simulações de Monte Carlo para avaliação da hipótese 
                    nula (H₀), complementado pelo Desvio Médio Absoluto (MAD), que mensura a magnitude das divergências 
                    observadas. Para identificar desvios individuais, são aplicados testes binomiais bilaterais 
                    com correção de Bonferroni às 90 combinações possíveis de dígitos (10 a 99), controlando o risco 
                    global de erro do Tipo I em 5%, com significância individual de aproximadamente 0,0556%. Os 
                    resultados permitem avaliar a aderência global à Lei de Benford, dimensionar a relevância prática
                    dos desvios e identificar grupos de lançamentos que demandam investigação complementar, 
                    subsidiando a priorização dos procedimentos de fiscalização. Ressalta-se que 
                    divergências estatísticas constituem indicadores de risco e não representam, isoladamente, 
                    evidência conclusiva de erro.</p>
                    <h4>Resultado da Análise de Benford</h4>
                    """)
        
        sSQL = f"""
                SELECT
                    Cd_ODI, Cd_Cls_Custo, COD_ITEM, Cd_NG, Cd_CA, 
                    CAST(REPLACE(VL_tot, ',', '.') AS REAL) AS VL_tot,
                    CAST(REPLACE(Qtd,",",".") AS REAL) AS Qtd
                FROM ROA t1 WHERE t1.Dt_ARQ= {Dt_ARQ}

            """
        df = pd.read_sql(sSQL, bd)
        valor_minimo = 100.0
        alpha = 0.05
        mad_proximo, mad_aceitavel, mad_marginal = 0.0012, 0.0018, 0.0022
        n_simulacoes = 10000  # Monte Carlo quando há frequências esperadas < 5

        serie = pd.to_numeric(df['VL_tot'], errors='coerce')
        valores = serie.dropna().abs().to_numpy(dtype=float)
        valores = valores[np.isfinite(valores) & (valores >= valor_minimo)]
        N = len(valores)
        if N == 0:
            st.info('Nenhum lançamento válido >= R$ 100 encontrado.')
            st.stop()

        centavos = np.rint(valores * 100).astype(np.int64)
        if np.any(centavos < 10000):
            raise ValueError('Valores monetários inconsistentes após conversão em centavos.')

        dois_digitos = np.fromiter((int(str(int(v))[:2]) for v in centavos), dtype=np.int64, count=N)
        digitos_possiveis = np.arange(10, 100)
        k_categorias = len(digitos_possiveis)
        observado = np.bincount(dois_digitos, minlength=100)[10:100]
        prop_observada = observado / N
        prop_esperada = np.log10(1.0 + 1.0 / digitos_possiveis)
        esperado = N * prop_esperada
        desvios = np.abs(prop_observada - prop_esperada)
        mad = float(np.mean(desvios))

        if mad <= mad_proximo:
            classificacao_mad = 'CONFORMIDADE_PROXIMA'
        elif mad <= mad_aceitavel:
            classificacao_mad = 'CONFORMIDADE_ACEITAVEL'
        elif mad <= mad_marginal:
            classificacao_mad = 'CONFORMIDADE_MARGINAL'
        else:
            classificacao_mad = 'NAO_CONFORMIDADE'
        conforme_mad = bool(mad <= mad_aceitavel)

        gl = k_categorias - 1
        chi2_global = float(np.sum((observado - esperado) ** 2 / esperado))
        aproximacao_chi2_valida = bool(np.all(esperado >= 5))
        if aproximacao_chi2_valida:
            metodo_teste_global = 'QUI_QUADRADO_ASSINTOTICO'
            p_value_global = float(chi2.sf(chi2_global, df=gl))
        else:
            metodo_teste_global = 'QUI_QUADRADO_MONTE_CARLO_H0'
            rng = np.random.default_rng(42)
            n_extremos = 0
            simulados = 0
            while simulados < n_simulacoes:
                lote = min(500, n_simulacoes - simulados)
                contagens = rng.multinomial(N, prop_esperada, size=lote)
                estatisticas = np.sum((contagens - esperado) ** 2 / esperado, axis=1)
                n_extremos += int(np.count_nonzero(estatisticas >= chi2_global))
                simulados += lote
            p_value_global = (n_extremos + 1) / (n_simulacoes + 1)
        rejeita_h0 = bool(p_value_global < alpha)

        alpha_bonferroni = alpha / k_categorias
        p_values_exatos = np.array([binomtest(int(o), N, float(p), alternative='two-sided').pvalue for o, p in zip(observado, prop_esperada)])
        p_values_bonf = np.minimum(1.0, p_values_exatos * k_categorias)
        fora_banda_bonf = p_values_exatos < alpha_bonferroni
        qtd_rejeitadas_bonf = int(fora_banda_bonf.sum())

        def limites_teste_binomial(n, p, nivel):
            moda = int(np.floor((n + 1) * p))
            def aceita(k):
                return binomtest(int(k), n, float(p), alternative='two-sided').pvalue >= nivel
            lo, hi = 0, moda
            while lo < hi:
                mid = (lo + hi) // 2
                if aceita(mid):
                    hi = mid
                else:
                    lo = mid + 1
            inferior = lo

            lo, hi = moda, n
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if aceita(mid):
                    lo = mid
                else:
                    hi = mid - 1
            superior = lo
            return inferior, superior

        limites_bonf_contagens = np.array([
            limites_teste_binomial(N, float(p), alpha_bonferroni)
            for p in prop_esperada
        ], dtype=np.int64)
        limite_inferior_bonf = limites_bonf_contagens[:, 0] / N * 100
        limite_superior_bonf = limites_bonf_contagens[:, 1] / N * 100

        limites_95_contagens = np.array([limites_teste_binomial(N, float(p), alpha)  for p in prop_esperada], dtype=np.int64)
        limite_inferior_95 = limites_95_contagens[:, 0] / N * 100
        limite_superior_95 = limites_95_contagens[:, 1] / N * 100

        fora_limites = ((observado < limites_bonf_contagens[:, 0]) | (observado > limites_bonf_contagens[:, 1]))
        if not np.array_equal(fora_banda_bonf, fora_limites):
            raise RuntimeError('Inconsistência entre testes exatos e bandas de Bonferroni.')

        decisao_h0 = 'REJEITA_H0' if rejeita_h0 else 'NAO_REJEITA_H0'
        resultado = f'{decisao_h0} | {classificacao_mad}'
        nao_rejeita_h0 = not rejeita_h0
        metodo = metodo_teste_global

        df_detalhado = pd.DataFrame({
                                    'Digitos': digitos_possiveis,
                                    'Qtd_Observada': observado,
                                    'Qtd_Esperada': np.round(esperado, 2),
                                    'Prop_Obs (%)': np.round(prop_observada * 100, 4),
                                    'Prop_Benford (%)': np.round(prop_esperada * 100, 4),
                                    'Desvio_Abs (%)': np.round(desvios * 100, 4),
                                    'p_value_Bonf': p_values_bonf,
                                    'Rejeita_Bonf': fora_banda_bonf,
                                    'Banda_Bonf_Inferior (%)': limite_inferior_bonf,
                                    'Banda_Bonf_Superior (%)': limite_superior_bonf,
                                })
        df_resumo = pd.DataFrame([{
                                    'N': N, 'Metodo': metodo, 'Alpha': alpha, 'MAD': mad,
                                    'Classificacao_MAD': classificacao_mad,
                                    'Limite_MAD': mad_aceitavel, 'Conforme_MAD': conforme_mad,
                                    'Chi2_Global': chi2_global, 'p_value_Global': p_value_global,
                                    'Aproximacao_Chi2_Valida': aproximacao_chi2_valida,
                                    'Alpha_Individual_Bonf': alpha_bonferroni,
                                    'N_Simulacoes_MC': n_simulacoes if not aproximacao_chi2_valida else 0,
                                    'Semente_MC': 42 if not aproximacao_chi2_valida else None,
                                    'Decisao_H0': decisao_h0,
                                    'Qtd_Rejeitadas_Bonf': qtd_rejeitadas_bonf,
                                    'Nao_Rejeita_H0': nao_rejeita_h0, 'Resultado': resultado,
                                }])
        df_detalhado.to_sql('RESUMO_BENFORD', bd, if_exists='replace', index=False)
        df_resumo.to_sql('RESULTADO_BENFORD', bd, if_exists='replace', index=False)

        if N < 1147:
            criterio_principal = 'TESTES_EXATOS (Monte Carlo + Binomial/Bonferroni)'
            justificativa_criterio = (
                'Amostra pequena (N < 1.147, com frequências esperadas < 5): '
                'priorize o teste exato global (Monte Carlo) e as bandas de Bonferroni; '
                'o MAD tem alta variância amostral nesta faixa.'
            )
            conclusao_pratica = (
                'DIVERGÊNCIA ESTATÍSTICA DETECTADA' if rejeita_h0
                else 'SEM EVIDÊNCIA DE DIVERGÊNCIA'
            )
        elif N <= 10000:
            criterio_principal = 'CONJUNTO (Qui-Quadrado/Bonferroni + MAD)'
            justificativa_criterio = (
                'Amostra intermediária (1.147 ≤ N ≤ 10.000): '
                'avalie em conjunto a significância estatística (p-valor / Bonferroni) '
                'e a magnitude prática (MAD).'
            )
            if rejeita_h0 and not conforme_mad:
                conclusao_pratica = 'NÃO CONFORME (significância estatística e magnitude relevante)'
            elif rejeita_h0 and conforme_mad:
                conclusao_pratica = 'ATENÇÃO LEVE (divergência estatística, mas magnitude dentro do aceitável)'
            else:
                conclusao_pratica = 'CONFORME'
        elif N <= 100000:
            criterio_principal = 'MAD (com triagem por Bonferroni)'
            justificativa_criterio = (
                'Amostra grande (10.000 < N ≤ 100.000): '
                'o Qui-Quadrado já apresenta sensibilidade elevada a pequenos desvios. '
                'Priorize o MAD para conformidade global e use Bonferroni para localizar dígitos.'
            )
            conclusao_pratica = (
                f'{classificacao_mad} (prioridade para magnitude MAD)'
            )
        else:
            criterio_principal = 'MAD + RANKING DE DESVIO ABSOLUTO'
            justificativa_criterio = (
                'Amostra muito grande (N > 100.000 — excesso de poder estatístico): '
                'o Qui-Quadrado e Bonferroni tendem a rejeitar H0 por desvios operacionais mínimos. '
                'Baseie a decisão no MAD e priorize dígitos pelos maiores desvios absolutos (p.p.).'
            )
            conclusao_pratica = (
                f'{classificacao_mad} (decisão baseada no MAD; p-valor apenas informativo)'
            )
        _, cola, _ = st.columns([1,5,1], gap="small")
        with cola:
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)
                col1.metric('Lançamentos', f'{N:,}'.replace(',', '.'))
                col2.metric('MAD', f'{mad:.6f}')
                col3.metric('Dígitos significativos (Bonferroni)', qtd_rejeitadas_bonf)
                st.write('Teste global:', metodo)
                st.write('p-valor global:', f'{p_value_global:.6g}')
                st.write('Classificação MAD:', classificacao_mad)
                st.write('Decisão estatística:', decisao_h0)
                st.write('Avaliação de magnitude:', classificacao_mad)
                if rejeita_h0:
                    st.warning('H0 rejeitada: há evidência de divergência global de Benford.')
                else:
                    st.info('H0 não rejeitada: evidência insuficiente de divergência global.')
                if classificacao_mad == 'NAO_CONFORMIDADE':
                    st.warning('MAD: não conformidade pela referência de magnitude adotada.')
                elif classificacao_mad == 'CONFORMIDADE_MARGINAL':
                    st.info('MAD: conformidade marginal; recomenda-se investigação complementar.')
                else:
                    st.success('MAD: magnitude dentro da faixa próxima ou aceitável.')
                st.info(f"**Critério indicado para N = {N:,}:** {criterio_principal}\n\n{justificativa_criterio}".replace(',', '.'))
        digitos = digitos_possiveis
        prop_obs_pct = prop_observada * 100
        prop_benford_pct = prop_esperada * 100
        cores_barras = ['#d9534f' if fora else '#3b7ddd' for fora in fora_banda_bonf]
        fig, (ax1, ax2) = plt.subplots(
                                            nrows=2, ncols=1, figsize=(16, 9), sharex=True,
                                            gridspec_kw={'height_ratios': [3, 1.2], 'hspace': 0.20}
                                        )
        ax1.bar(digitos, prop_obs_pct, width=0.72, color=cores_barras,
                alpha=0.88, edgecolor='#1b3b6f', linewidth=0.5,
                label='Proporção observada (VL_tot)')
        ax1.plot(digitos, prop_benford_pct, color='#111111', linewidth=2.0,
                label='Distribuição teórica de Benford')
        ax1.plot(digitos, limite_superior_95, color='#777777', linestyle=':', linewidth=1.1,
                label='Banda individual 95% (sem ajuste)')
        ax1.plot(digitos, limite_inferior_95, color='#777777', linestyle=':', linewidth=1.1)
        ax1.plot(digitos, limite_superior_bonf, color='#d9534f', linestyle='--', linewidth=1.5,
                label='Região de aceitação binomial exata com Bonferroni (FWER ≤ 5%)')
        ax1.plot(digitos, limite_inferior_bonf, color='#d9534f', linestyle='--', linewidth=1.5)
        ax1.fill_between(digitos, limite_inferior_bonf, limite_superior_bonf,
                        color='#28a745', alpha=0.13)

        status = ('H0 REJEITADA' if rejeita_h0 else 'H0 NÃO REJEITADA')
        cor_titulo = '#d9534f' if rejeita_h0 else '#1e7e34'
        ax1.set_title(
            'Lei de Benford — dois primeiros dígitos (|VL_tot| ≥ R$ 100)\n'
            f'{status} | N={N:,} | p global={p_value_global:.4g} | MAD={mad:.5f} | {classificacao_mad}',
            fontsize=11, fontweight='bold', color=cor_titulo, pad=14
        )
        ax1.set_ylabel('Frequência relativa (%)', fontsize=11, fontweight='bold')
        ax1.grid(axis='y', linestyle=':', alpha=0.6)
        ax1.legend(loc='upper right', frameon=True, fontsize=8)

        ax2.bar(digitos, desvios * 100, width=0.72, color='#6c757d', alpha=0.75,
                label='Desvio absoluto por dígito (p.p.)')
        ax2.axhline(mad * 100, color='#0056b3', linewidth=2,
                    label=f'MAD observado ({mad*100:.3f} p.p.)')
        ax2.axhline(mad_aceitavel * 100, color='#d9534f', linestyle='--', linewidth=1.5,
                    label=f'Limite MAD aceitável ({mad_aceitavel*100:.3f} p.p.)')
        ax2.set_xlabel('Dois primeiros dígitos significativos (10 a 99)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Desvio absoluto (p.p.)', fontsize=10, fontweight='bold')
        ax2.set_xticks(np.arange(10, 100, 2))
        ax2.set_xlim(9, 100)
        ax2.grid(axis='y', linestyle=':', alpha=0.6)
        ax2.legend(loc='upper right', frameon=True, fontsize=9)

        pasta_saida = Path(local) / 'AIS_ANLS'
        pasta_saida.mkdir(parents=True, exist_ok=True)
        df_detalhado.to_csv(pasta_saida / 'AMST_REPETIDOS.csv', index=False,
                            sep='|', decimal=',', encoding='latin-1')
        fig.savefig(pasta_saida / 'ANL_BENFORD.png', dpi=300, bbox_inches='tight')
        st.pyplot(fig)
        plt.close(fig)

        dados = df.copy()
        vis_AX020a(dados, st)

@st.fragment
def vis_AX020a(df_dados = None, st = None): 
    colunas_filtro = ["Cd_ODI","Cd_NG","Cd_CA","Cd_Cls_Custo"]
    _, cola, _ = st.columns([1,5,1], gap='small')
    dados = df_dados.copy()
    st.html("""<p  style="text-align: justify;text-indent: 40px"> 
                Abaixo há gráficos com intuito de se fazer análise exploratória da distribuição dos lançamentos 
                e de seus valores, utilizando escalas logarítmicas, segregação por sinal, concentração financeira 
                acumulada e estratificação por percentis, com o objetivo de caracterizar o comportamento dos dados, 
                identificar padrões, assimetrias e concentrações atípicas, subsidiando análises posteriores, sem 
                caráter conclusivo quanto à existência de irregularidades.</p>
                """)
    with cola:
        with st.container(border=True):
            cols = st.columns(4)
            for i, coluna in enumerate(colunas_filtro):
                opcoes = sorted(df_dados[coluna].dropna().astype(str).unique())
                opcoes = ["Todos"] + opcoes
                with cols[i]:
                    selecao = st.selectbox(coluna, options=opcoes,key=f"filtro_{coluna}")

                if selecao != "Todos":
                    dados = dados[dados[coluna].astype(str) == selecao]

    dados['VL_tot'] = pd.to_numeric(dados['VL_tot'], errors='coerce')
    dados['Qtd'] = pd.to_numeric(dados['Qtd'], errors='coerce')
    dados = dados.loc[dados['VL_tot'].notna() & (dados['VL_tot'] != 0)].copy()
    dados['qtd_invalida'] = dados['Qtd'].isna() | (dados['Qtd'] == 0)
    dados['Qtd_ajustada'] = dados['Qtd'].mask(dados['qtd_invalida'], 1)
    dados['valor_abs'] = dados['VL_tot'].abs()
    dados['valor_unit_abs'] = (dados['VL_tot'] / dados['Qtd_ajustada']).abs()
    dados['sinal'] = np.where(dados['VL_tot'] > 0, 'Positivo', 'Negativo')
    dados = dados.loc[np.isfinite(dados['valor_unit_abs']) & (dados['valor_unit_abs'] > 0)].copy()

    fig5a, ax5a = plt.subplots(3, 2, figsize=(15, 6))


    ax5a[0, 0].hist(np.log10(dados["valor_unit_abs"]),bins=80, color="steelblue", alpha=0.8)
    ax5a[0, 0].set_title("Distribuição Logarítmica dos Valores Unitários")
    ax5a[0, 0].set_xlabel("log10(|VL_tot / Qtd|)")
    ax5a[0, 0].set_ylabel("Quantidade de lançamentos")
    
    for sinal, cor in [("Positivo", "steelblue"),("Negativo", "darkorange")]:
        valores = dados.loc[dados["sinal"] == sinal, "valor_abs"]
        if len(valores):
            ax5a[0, 1].hist(np.log10(valores),bins=80,alpha=0.5,color=cor,label=sinal)

    ax5a[0, 1].set_title("Distribuição dos Valores por Sinal")
    ax5a[0, 1].set_xlabel("log10(|VL_tot|)")
    ax5a[0, 1].set_ylabel("Quantidade de lançamentos")
    ax5a[0, 1].legend()

    valores_ord = np.sort(dados.loc[dados["VL_tot"].abs() > 0, "VL_tot"].abs().to_numpy())
    pct_valor_acum = ( np.cumsum(valores_ord) / valores_ord.sum() * 100)

    ax5a[1, 1].plot(np.log10(valores_ord), pct_valor_acum, color="darkorange", linewidth=2)
    ax5a[1, 1].set_title("Distribuição Cumulativa em Valor")
    ax5a[1, 1].set_xlabel("log10(|VL_tot|)")
    ax5a[1, 1].set_ylabel("% Acumulado do Valor Absoluto")
    ax5a[1, 1].set_ylim(0, 100)

    resumo = dados.groupby("sinal").agg(quantidade=("VL_tot", "size"), valor_absoluto=("valor_abs", "sum"))

    ax5a[1, 0].bar(resumo.index, resumo["quantidade"], color=["darkorange" if x == "Negativo" else "steelblue" for x in resumo.index])
    ax5a[1, 0].set_title("Quantidade de Lançamentos por Sinal")
    ax5a[1, 0].set_ylabel("Quantidade")

    idx_p20 = np.searchsorted(pct_valor_acum, 20.0)
    valor_corte_p20 = valores_ord[idx_p20]
    valores_sup_p20 = valores_ord[idx_p20:]
    valores_inf_p20 = valores_ord[:idx_p20]
    
    ax5a[2, 0].hist(np.log10(valores_sup_p20),bins=80, color="steelblue", alpha=0.8)
    ax5a[2, 1].hist(np.log10(valores_inf_p20),bins=80, color="steelblue", alpha=0.8)
    ax5a[2, 0].set_title("Distribuição Logarítmica dos Valores com P20, acima em valor")
    ax5a[2, 0].set_xlabel("log10(|VL_tot|)")
    ax5a[2, 0].set_ylabel("Quantidade de lançamentos")
    ax5a[2, 1].set_title("Distribuição Logarítmica dos Valores com P20, abaixo em valor")
    ax5a[2, 1].set_xlabel("log10(|VL_tot|)")
    ax5a[2, 1].set_ylabel("Quantidade de lançamentos")

    for ax in ax5a.flat:
        ax.grid(axis="y", linestyle=":", alpha=0.3)
        ax.tick_params(axis="both", labelsize=8)

    plt.tight_layout()
    st.pyplot(fig5a)

@st.fragment
def vis_AX021(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('RESUMO_QTD_AIS_ROA_CHV_CMP', bd):
            return
 
        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Teste de Consistência de Quantidade entre ROA e AIS</h3>
                    """)   
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">É um processo similar ao feito entre BDGD e AIS. 
                    A alteração aqui é que se usa o ROA e faz-se o teste em quantidade. Esse teste não é feito em valor, por 
                    conta do processo alocativo dos custos de COM, CA e JOA para as TUC. Como o processo já foi descrito, 
                    apenas explicita-se aqui, em cada etapa, o conjunto específico de chaves: 
                    </p><br>
                    """)
        st.html(f"""<p style = "background-color: #e6f7ff;text-indent: 45px; padding: 15px; border-left: 5px solid #1f77b4;">
                        • Cd_ODI, Cd_SubODI, Nr_TI, Nr_TUC, Nr_A1-Nr_A6, UND (granularidade máxima)</p>
                        <p style = "background-color: #e6f7ff;text-indent: 45px; padding: 15px; border-left: 5px solid #1f77b4;">
                        • Cd_ODI, Cd_SubODI, Nr_TI, Nr_TUC, Nr_A1-Nr_A6</p>
                        <p style = "background-color: #e6f7ff;text-indent: 45px; padding: 15px; border-left: 5px solid #1f77b4;">
                        • Cd_ODI, Cd_SubODI, Nr_TI, Nr_TUC</p>
                        <p style = "background-color: #e6f7ff;text-indent: 45px; padding: 15px; border-left: 5px solid #1f77b4;">
                        • Cd_ODI, Cd_SubODI, Nr_TUC</p>
                        <p style = "background-color: #e6f7ff;text-indent: 45px; padding: 15px; border-left: 5px solid #1f77b4;">
                        • Cd_ODI, Nr_TUC</p>
                        <p style = "background-color: #e6f7ff;text-indent: 45px; padding: 15px; border-left: 5px solid #1f77b4;">
                        • Nr_TUC (nível mínimo)</p>
                    </p><br>
                    """)     

        sSQL = """
                SELECT * FROM RESUMO_QTD_AIS_ROA_CHV_CMP

            """
        RESUMO_QTD_AIS_ROA_CHV_CMP = pd.read_sql(sSQL, bd)
        
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px"> 
                    Ainda, existem ocorrências que correspondem a sistemas cujas unidades de medida são 
                    distintas (por exemplo, itens contabilizados em unidades, conjunto funcional, massa ou outras 
                    métricas específicas) e que, por natureza, não são comparáveis diretamente aos valores do ROA. 
                    Por esse motivo, não incluimos essas TUC nos testes de consistência quantitativa, uma vez que 
                    sua comparação direta produz distorções e resultados espúrios. Eis a lista: 100, 105, 110, 112, 115, 
                    140, 145, 150, 155, 170, 175, 185, 205, 215, 220, 225, 240, 245, 260, 275, 280, 285, 300, 320, 335, 350, 355, 360, 365, 
                    370, 375, 380, 385, 390, 395, 400, 405, 410, 415, 420, 425, 430, 435, 440, 445, 450, 455, 460, 465, 470, 475, 480, 485, 
                    490, 500, 505, 510, 515, 520, 525, 530, 550, 555, 585, 590, 595, 600, 610. 
                    Qtd_CONC_OK é quando os valores de quantidade são iguais nos dois lados.
                    Qtd_CONC_DIV é quando as quantidades diferem.
                    Qtd_AUS_ROA e Qtd_AUS_AIS são registros não encontrados no parceiro.
                    Pct_CONC é o percentual de registros conciliados, TOT_CONC, sobre o total de registros da etapa, TOT_REG.
                    A seguir o resultado:</p><br>
                    """)
        container3 = st.container(border=True)
        for n in ['Qtd_CONC', 'Qtd_CONC_OK', 'Qtd_CONC_DIV', 'Qtd_AUS_AIS', 'Qtd_AUS_ROA', 'TOT_CONC','TOT_REG',
                'Pct_CONC']:
            if n in ['Pct_CONC']:
                RESUMO_QTD_AIS_ROA_CHV_CMP[n] = RESUMO_QTD_AIS_ROA_CHV_CMP[n].apply(lambda x: f"{float(x):,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
            else:
                RESUMO_QTD_AIS_ROA_CHV_CMP[n] = RESUMO_QTD_AIS_ROA_CHV_CMP[n].apply(lambda x: f"{float(x):,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        container3.dataframe(RESUMO_QTD_AIS_ROA_CHV_CMP, width='stretch', hide_index=True)

        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Também aplicamos o teste considerando apenas a TUC. Quando 
                    se emprega apenas a TUC, tem-se por finalidade avaliar a coerência entre os registros das duas bases 
                    analisadas, ROA e AIS, período incremental, no nível básico de identificação de ativos, isto é, pelo 
                    equipamento principal. Ao restringir a análise à UC, elimina-se a influência das demais dimensões de 
                    categorização — como ODI, TUC ou atributos que caracterizam o equipamento — permitindo verificar se, 
                    na granularidade mínima do dado, existe aderência entre os dados, do ROA e do AIS. Essa etapa funciona 
                    como uma verificação básica de consistência estrutural, tratando-se, portanto, de um diagnóstico 
                    preliminar para compreender a distribuição dos não conciliados e a robustez da base analisada. Novamente, 
                    esse teste não é feito em valor, por conta do processo alocativo dos custos de COM, CA e JOA para as TUC. 
                    Abaixo, tem-se o resultado por UC: 
                    </p><br>
                    """)
        
        sSQL = """
                    SELECT * FROM RESUMO_QTD_AIS_ROA_CHV_SMP
                """
        RESUMO_QTD_AIS_ROA_CHV_CMP = pd.read_sql(sSQL, bd)

        container4 = st.container(border=True)
        for n in ['Qtd_ROA','Qtd_AIS','DELTA']:
            if n in ['DELTA']:
                RESUMO_QTD_AIS_ROA_CHV_CMP[n] = RESUMO_QTD_AIS_ROA_CHV_CMP[n].apply(lambda x: f"{float(x):,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
            else:
                RESUMO_QTD_AIS_ROA_CHV_CMP[n] = RESUMO_QTD_AIS_ROA_CHV_CMP[n].apply(lambda x: f"{float(x):,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        container4.dataframe(RESUMO_QTD_AIS_ROA_CHV_CMP, width='stretch', hide_index=True)

        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Por fim, fazemos uma análise de valor por TI entre as bases.
                    Dada a quantidade projetos no período incremental, não se 
                    apresenta o resultado do teste nessa granularidade, apenas por TI. No entanto, foi avaliado por projeto e 
                    aqueles com desvios mais significativos foram abordados. O teste é empregado com o intuito de garantir a 
                    integridade dos registros contábeis de Ativo Imobilizado em Serviço (AIS). Este teste visa validar se o 
                    valor total registrado dos ativos em serviço, agrupados pela TI, está consistente com o valor total
                        correspondente no ROA. O AIS representa o custo final do ativo após sua conclusão e entrada em uso, 
                    enquanto o ROA é um registro detalhado, frequentemente utilizado para rastrear os custos incorridos 
                    durante a fase de construção ou instalação de um ativo antes de sua capitalização e transferência para 
                    o AIS. As divergências entre ambos pode indicar erros de classificação, falhas na transferência de valores 
                    de obras em andamento para o ativo final, ou problemas de segregação contábil por tipo de instalação 
                    (como ocasionados em obras mistas). Abaixo, tem-se o resultado por TI: 
                    </p><br>
                    """)
        
        sSQL = """
                    SELECT * FROM RESUMO_VL_AIS_ROA_CHV_SMP
                """
        RESUMO_QTD_AIS_ROA_CHV_CMP = pd.read_sql(sSQL, bd)

        container5 = st.container(border=True)
        for n in ['VL_ROA','VL_AIS','DELTA']:
            if n in ['DELTA']:
                RESUMO_QTD_AIS_ROA_CHV_CMP[n] = RESUMO_QTD_AIS_ROA_CHV_CMP[n].apply(lambda x: f"{float(x):,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
            else:
                RESUMO_QTD_AIS_ROA_CHV_CMP[n] = RESUMO_QTD_AIS_ROA_CHV_CMP[n].apply(lambda x: f"{float(x):,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        container5.dataframe(RESUMO_QTD_AIS_ROA_CHV_CMP, width='stretch', hide_index=True)

@st.fragment
def vis_AX022(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('tbl_comparativa_mop_fopag_roa', bd):
            return
 
        st.html("""
                    <h2>Conciliação FOPAG x Razões Analíticos</h2>
                    """)
        sSQL = """
                SELECT * FROM tbl_comparativa_mop_fopag_roa WHERE VL_FOPAG_CAPEX>0

            """
        df = pd.read_sql(sSQL, bd)
        df['DT_REF'] = pd.to_datetime(df['DT_REF'], errors='coerce')
        df['DIF_FOPAG_RO'] = (
                                df['VL_FOPAG_CAPEX'] - df['VL_TOT_RO']
                            ).round(2)

        df['DIF_FOPAG_LIMITE'] = (
                                    df['VL_FOPAG_CAPEX'] - df['VL_ODI_REF_SFF']
                                ).round(2)

        df['DIF_RO_LIMITE'] = (
                                    df['VL_TOT_RO'] - df['VL_ODI_REF_SFF']
                                ).round(2)

        tol = 1.00

        df['SIT_CAPEX'] = np.select(
                                        [
                                            df['VL_FOPAG_CAPEX'] > df['VL_ODI_REF_SFF'] + tol,
                                            df['VL_FOPAG_CAPEX'] > df['VL_TOT_RO'] + tol,
                                            df['VL_FOPAG_CAPEX'].sub(df['VL_TOT_RO']).abs() <= tol,
                                        ],
                                        [
                                            'FOPAG acima do limite SFF',
                                            'FOPAG acima do AIC + AIS',
                                            'Conciliado com AIC + AIS',
                                        ],
                                        default='Verificar'
                                    )
        def br_money(v):
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        vl_ais = df['VL_TOTAL_MOP_ROA'].sum()
        vl_aic = df['VL_TOTAL_MOP_ROAaicAT'].sum()
        vl_ro = df['VL_TOT_RO'].sum()
        vl_limite = df['VL_ODI_REF_SFF'].sum()
        vl_fopag = df['VL_FOPAG_CAPEX'].sum()

        dif_fopag_ro = vl_fopag - vl_ro
        dif_fopag_limite = vl_fopag - vl_limite

        kpis = [
                    ('AIS', vl_ais, 'VL_TOTAL_MOP_ROA'),
                    ('AIC', vl_aic, 'VL_TOTAL_MOP_ROAaicAT'),
                    ('AIC + AIS', vl_ro, 'VL_TOT_RO'),
                    ('Limite SFF', vl_limite, 'VL_ODI_REF_SFF'),
                    ('FOPAG CAPEX', vl_fopag, 'VL_FOPAG_CAPEX'),
                ]
        
        cols_MOP = st.columns([1,10,1], gap='small')
        with cols_MOP[1]:
            st.html("""
                        <p  style="text-align: justify;text-indent: 40px">
                                Os indicadores abaixo apresentam uma visão consolidada dos valores analisados durante
                                o período selecionado. São demonstrados os montantes identificados nos razões
                                analíticos do <b>Ativo Imobilizado em Serviço (AIS)</b>, do
                                <b>Ativo Imobilizado em Curso (AIC)</b>, o total das apropriações contábeis
                                (<b>AIC + AIS</b>), o <b>limite de investimento calculado pelo SFF</b> e o
                                valor da <b>FOPAG apropriada como CAPEX</b> informado pela concessionária.
                                Esses indicadores permitem avaliar, de forma imediata, se a folha de pagamento
                                destinada a investimento apresenta compatibilidade com os registros contábeis e
                                com o limite técnico calculado, direcionando a análise para eventuais excessos
                                de apropriação, insuficiências ou divergências de maior materialidade.
                            </p>
                        """)
            st.html("""
                        <style>
                        .kpi-card {
                            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
                            border: 1px solid #e5e7eb;
                            border-radius: 18px;
                            padding: 22px;
                            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
                        }

                        .kpi-label {
                            font-size: 13px;
                            color: #6b7280;
                            font-weight: 700;
                            text-transform: uppercase;
                            letter-spacing: .04em;
                        }

                        .kpi-value {
                            font-size: 27px;
                            font-weight: 850;
                            color: #111827;
                            margin-top: 8px;
                        }

                        .kpi-note {
                            font-size: 13px;
                            color: #9ca3af;
                            margin-top: 6px;
                        }
                        </style>
                        """)

            st.html(f"""
                            <div style="
                                display: grid;
                                grid-template-columns: repeat(3, minmax(0, 1fr));
                                gap: 16px;
                                margin: 10px 0 28px 0;
                            ">

                                <div class="kpi-card">
                                    <div class="kpi-label">AIS</div>
                                    <div class="kpi-value">{br_money(vl_ais)}</div>
                                    <div class="kpi-note">Razão analítico AIS</div>
                                </div>

                                <div class="kpi-card">
                                    <div class="kpi-label">AIC</div>
                                    <div class="kpi-value">{br_money(vl_aic)}</div>
                                    <div class="kpi-note">Razão analítico AIC</div>
                                </div>

                                <div class="kpi-card">
                                    <div class="kpi-label">AIC + AIS</div>
                                    <div class="kpi-value">{br_money(vl_ro)}</div>
                                    <div class="kpi-note">Total contábil identificado</div>
                                </div>

                                <div class="kpi-card">
                                    <div class="kpi-label">Limite SFF</div>
                                    <div class="kpi-value">{br_money(vl_limite)}</div>
                                    <div class="kpi-note">Valor limite calculado</div>
                                </div>

                                <div class="kpi-card">
                                    <div class="kpi-label">FOPAG CAPEX</div>
                                    <div class="kpi-value">{br_money(vl_fopag)}</div>
                                    <div class="kpi-note">Valor informado pela concessionária</div>
                                </div>

                                <div class="kpi-card">
                                    <div class="kpi-label">Diferença</div>
                                    <div class="kpi-value">{br_money(dif_fopag_limite)}</div>
                                    <div class="kpi-note">FOPAG CAPEX - Limite SFF</div>
                                </div>

                            </div>
                            """)
            df_melt = df.melt(
                                    id_vars='DT_REF',
                                    value_vars=[
                                        'VL_TOTAL_MOP_ROA',
                                        'VL_TOTAL_MOP_ROAaicAT',
                                        'VL_TOT_RO',
                                        'VL_ODI_REF_SFF',
                                        'VL_FOPAG_CAPEX'
                                    ],
                                    var_name='Fonte',
                                    value_name='Valor'
                                )

            map_fonte = {
                            'VL_TOTAL_MOP_ROA': 'AIS',
                            'VL_TOTAL_MOP_ROAaicAT': 'AIC',
                            'VL_TOT_RO': 'AIC + AIS',
                            'VL_ODI_REF_SFF': 'Limite SFF',
                            'VL_FOPAG_CAPEX': 'FOPAG CAPEX'
                        }

            df_melt['Fonte'] = df_melt['Fonte'].map(map_fonte)

            fig = px.line(
                            df_melt,
                            x='DT_REF',
                            y='Valor',
                            color='Fonte',
                            markers=True,
                            title='Evolução mensal: FOPAG CAPEX x AIC + AIS x Limite SFF'
                        )
            st.html("""
                        <h3>Evolução mensal da FOPAG CAPEX, razões analíticos e limite SFF</h3>
                            <p  style="text-align: justify;text-indent: 40px">
                                O gráfico apresenta, mês a mês, a comparação entre o valor de mão de obra informado
                                na folha de pagamento como <b>CAPEX</b>, os valores identificados nos razões analíticos
                                de <b>AIS</b> e <b>AIC</b>, o respectivo total <b>AIC + AIS</b>, e o
                                <b>valor limite de investimento calculado pelo SFF</b>.
                                A análise permite verificar se a parcela de folha apropriada como investimento
                                encontra respaldo nos registros contábeis analíticos e se permanece dentro do limite
                                calculado para reconhecimento em CAPEX. Diferenças persistentes, picos isolados ou
                                valores de FOPAG CAPEX superiores ao limite SFF devem ser tratados como pontos de
                                atenção para revisão documental ou eventual glosa.
                            </p>
                        """)
            st.plotly_chart(fig, use_container_width=True)

            fig = px.bar(
                            df,
                            x='DT_REF',
                            y='DIF_FOPAG_LIMITE',
                            title='Diferença entre FOPAG CAPEX e Limite SFF',
                            text='DIF_FOPAG_LIMITE'
                        )
            st.html("""
                        <h3>Diferença entre a FOPAG CAPEX informada e o limite SFF</h3>
                            <p  style="text-align: justify;text-indent: 40px">
                                Este gráfico evidencia, por mês de referência, a diferença entre o valor informado
                                na folha de pagamento como <b>CAPEX</b> e o <b>valor limite de investimento calculado pelo SFF</b>.
                                Valores positivos indicam que a FOPAG CAPEX informada supera o limite calculado,
                                configurando potencial excesso de apropriação em investimento e possível necessidade
                                de glosa ou justificativa complementar. Valores negativos indicam que não foram informados
                                dados relevantes para se fazer análise.
                            </p>
                        """)
            st.plotly_chart(fig, use_container_width=True)

            cols_revisao = [
                                'DT_REF',
                                'VL_TOTAL_MOP_ROA',
                                'VL_TOTAL_MOP_ROAaicAT',
                                'VL_TOT_RO',
                                'VL_ODI_REF_SFF',
                                'VL_FOPAG_CAPEX',
                                'DIF_FOPAG_RO',
                                'DIF_FOPAG_LIMITE',
                                'DIF_RO_LIMITE',
                                'SIT_CAPEX'
                            ]
            st.html("""
                        <h3>Detalhamento mensal dos valores analisados</h3>
                            <p  style="text-align: justify;text-indent: 40px">
                                A tabela abaixo apresenta os valores utilizados na conciliação para cada mês de
                                referência. São demonstrados os montantes apurados nos razões analíticos do
                                <b>AIS</b> e do <b>AIC</b>, o respectivo total (<b>AIC + AIS</b>), o
                                <b>valor limite de investimento calculado pelo SFF</b>, o valor de
                                <b>FOPAG CAPEX informado pela concessionária</b> e as diferenças apuradas.
                                A análise permite identificar os períodos em que houve convergência entre
                                os registros ou em que foram observadas divergências relevantes. Meses com diferenças
                                positivas indicam que o valor informado como investimento supera o limite calculado,
                                enquanto diferenças negativas evidenciam que faltam dados para se validar os dados.
                            </p>
                        """)
            st.dataframe(
                            df[cols_revisao].sort_values('DT_REF'),
                            width='content'
                        )

@st.fragment
def vis_AX023(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('Conciliados_VL_ST_MOP', bd):
            return

        sSQL = """SELECT * FROM Conciliados_VL_ST_MOP"""
        RESUMO = pd.read_sql(sSQL, bd)

        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Teste de Consistência de Valor de MOP e ST entre ROD e ROS</h3>
                    """)   
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">A realização deste teste consiste em confrontar os 
                    valores apresentados no ROS com os registros correspondentes no Razão Analítico de Obras com Desativação, 
                    de forma a validar a consistência e a completude das informações consolidadas. O procedimento envolve 
                    verificar se os custos classificados como desativação — segmentados entre mão de obra própria e serviços 
                    de terceiros — estão devidamente suportados por lançamentos analíticos individualizados, observando 
                    critérios de competência, natureza da despesa e correção da conta contábil utilizada. Busca-se identificar 
                    eventuais divergências, omissões ou reclassificações indevidas, avaliando se o relatório sintético reflete 
                    de maneira fidedigna a movimentação registrada no razão analítico e garantindo a confiabilidade das 
                    demonstrações gerenciais de custos de obras. A seguir temos os resultados, na forma tabular, 
                    dos testes dos itens que foram conciliados.
                    </p>
                    """)
            
        RESUMO = RESUMO.fillna(0)
        RESUMOa = RESUMO.copy()
        container6 = st.container(border=True)
        for n in ['VL_ROD_UC','VL_ROD_COM','VL_ROD_MOP','VL_ROD_ST','VL_ROD_JOA','VL_ROD_Outros','VL_ROS_MOP','VL_ROS_ST','DELTA']:
            if n in ['DELTA']:
                RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{float(x):,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
            else:
                RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{float(x):,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        container6.dataframe(RESUMOa, width='stretch', hide_index=True)

        criterio_CN = RESUMO['DELTA'] == 0
        criterio_NCN = RESUMO['DELTA'] != 0

        VL_CN_ROD = RESUMO[criterio_CN]['VL_ROD_MOP'].abs().sum() + RESUMO[criterio_CN]['VL_ROD_ST'].abs().sum()
        VL_NCN_ROD = RESUMO[criterio_NCN]['VL_ROD_MOP'].abs().sum() + RESUMO[criterio_NCN]['VL_ROD_ST'].abs().sum()

        QTD_OCOR_CN = criterio_CN.sum()
        QTD_OCOR_NCN = criterio_CN.sum()
        QTD_OCOR = QTD_OCOR_NCN + QTD_OCOR_CN

        Pct_ANL = f"{VL_CN_ROD/(VL_NCN_ROD+VL_CN_ROD):,.2%}".replace(",", "X").replace(".", ",").replace("X", ".")

        VL_CN_ROD = f"{VL_CN_ROD:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        VL_NCN_ROD = f"{VL_NCN_ROD:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        QTD_OCOR_CN = f"{QTD_OCOR_CN:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        QTD_OCOR_NCN = f"{QTD_OCOR_NCN:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

        if Pct_ANL != "100,00%":
            TRC_DIV = f"""Por sua vez, foram identificadas divergências em {QTD_OCOR_NCN} projetos, somando diferenças 
            de R$ {VL_NCN_ROD}, demandando investigação das causas e verificação dos impactos potenciais."""
        else:
            TRC_DIV = f"""Não foram identificadas divergências entre os valores analisados, indicando total aderência 
            entre o ROS e o ROD."""

        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">A síntese da conciliação entre o ROS e o ROD indica que, 
                    do total de projetos avaliados, os projetos que apresentaram plena correspondência totalizaram 
                    {QTD_OCOR_CN} projetos, com valor agregado de R$ {VL_CN_ROD}. {TRC_DIV} Essa consolidação permite 
                    avaliar de forma objetiva o nível de conformidade entre os registros conciliados, que foi de {Pct_ANL} 
                    nesta empresa.</p>
                    """)

        texto_ST_MOP = f"""
                    <p1">A síntese da conciliação entre o ROS e o ROD indica que, 
                    do total de projetos avaliados, os projetos que apresentaram plena correspondência totalizaram 
                    {QTD_OCOR_CN} projetos, com valor agregado de R$ {VL_CN_ROD}. {TRC_DIV} Essa consolidação permite 
                    avaliar de forma objetiva o nível de conformidade entre os registros conciliados, que foi de {Pct_ANL} 
                    nesta empresa. </p1>
                    """

        dic = {}
        if existe_tabela('Nao_Conciliados_ROS_VL_ST_MOP', bd):
            dic['RESUMO_NC_ROS'] = pd.read_sql("SELECT * FROM Nao_Conciliados_ROS_VL_ST_MOP", bd)
        else:
            dic['RESUMO_NC_ROS'] = pd.DataFrame()
        if existe_tabela('Nao_Conciliados_ROD_VL_ST_MOP', bd):
            dic['RESUMO_NC_ROD'] = pd.read_sql("SELECT * FROM Nao_Conciliados_ROD_VL_ST_MOP", bd)
        else:
            dic['RESUMO_NC_ROD'] = pd.DataFrame()

        for nm in ['ROS','ROD']:
            ax = [x for x in ['ROS', 'ROD'] if x != nm]
            if len(dic[f'RESUMO_NC_{nm}']) == 0:
                dic[f'Qtd_{nm}'] = 0
                st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Na tabela {nm}, apresentada,
                    não foi encontrado registros não declarados na tabela {ax[0]}.</p>
                    """)  
                texto_ST_MOP += f"""
                    <p1">Na tabela {nm}, apresentada,
                    não foi encontrado registros não declarados na tabela {ax[0]}. </p1>
                    """      
            else:
                dic[f'Qtd_{nm}'] = len(dic[f'RESUMO_NC_{nm}'])
                st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Na tabela {nm}, apresentada,
                    foi encontrado {dic[f'Qtd_{nm}']} registros não declarados na tabela {ax[0]}. A seguir, em dados 
                    tabulares, os projetos não encontrados:</p>
                    """)
                texto_ST_MOP += f"""
                    <p1">Na tabela {nm}, apresentada,
                    foi encontrado {dic[f'Qtd_{nm}']} registros não declarados na tabela {ax[0]}. </p1>
                    """
                RESUMOa = dic[f'RESUMO_NC_{nm}'].copy().fillna(0)
                container7 = st.container(border=True)
                for n in ['VL_ROD_UC','VL_ROD_COM','VL_ROD_MOP','VL_ROD_ST','VL_ROD_JOA',
                            'VL_ROD_Outros','VL_ROS_MOP','VL_ROS_ST']:
                    try:
                        RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    except:
                        RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{float(x):,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
                container7.dataframe(RESUMOa, width='stretch', hide_index=True)  


        VL_CN = VL_CN_ROD if QTD_OCOR != "0" else "0,00"

        QTD_ROS = dic[f'Qtd_ROS']
        VL_ROS = ((dic['RESUMO_NC_ROS']['VL_ROS_MOP'].abs().sum() + dic['RESUMO_NC_ROS']['VL_ROS_ST'].abs().sum()) 
                    if QTD_ROS > 0 
                    else 0)

        dic['RESUMO_NC_ROD'] = dic['RESUMO_NC_ROD'].fillna(0)
        QTD_ROD = dic[f'Qtd_ROD']
        VL_ROD = ((dic['RESUMO_NC_ROD']['VL_ROD_MOP'].abs().sum() + dic['RESUMO_NC_ROD']['VL_ROD_ST'].abs().sum()) 
                    if QTD_ROD > 0 
                    else 0)

        c = QTD_OCOR > 0
        r = QTD_ROS > 0
        d = QTD_ROD > 0

        QTD_OCOR = f"{QTD_OCOR:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        QTD_ROS = f"{QTD_ROS:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        QTD_ROD = f"{QTD_ROD:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        VL_ROS = f"{VL_ROS:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        VL_ROD = f"{VL_ROD:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        texto = """<p  style="text-align: justify;text-indent: 40px">A conciliação entre o razão sintético e o 
                    razão analítico de obras de desativação apresentou o seguinte resultado: """

        # 1) Somente conciliados
        if c and not r and not d:
            texto += (
                f"todos os itens foram conciliados, totalizando {QTD_OCOR} registros "
                f"com valor consolidado de R$ {VL_CN}, não havendo divergências "
                "nem no ROS nem no razão analítico de obras de desativação.</p>"
            )

        # 2) Conciliados + divergências no ROS
        elif c and r and not d:
            texto += (
                f"{QTD_OCOR} registros foram conciliados, somando R$ {VL_CN}. "
                f"Foram identificadas divergências no ROS, abrangendo {QTD_ROS} registros "
                f"com diferenças de R$ {VL_ROS}, enquanto não foram apontadas "
                "inconsistências no razão analítico de obras de desativação.</p>"
            )

        # 3) Conciliados + divergências no razão de desativação
        elif c and not r and d:
            texto += (
                f"{QTD_OCOR} itens foram conciliados corretamente, totalizando R$ {VL_CN}. "
                f"Foram identificadas divergências no razão analítico de obras de desativação, "
                f"abrangendo {QTD_ROD} registros com valor de R$ {VL_ROD}, "
                "enquanto o ROS não apresentou inconsistências.</p>"
            )

        # 4) Conciliados + divergências nos dois lados
        elif c and r and d:
            texto += (
                f"foram conciliados {QTD_OCOR} registros (R$ {VL_CN}). "
                f"No entanto, foram encontradas divergências tanto no ROS, com {QTD_ROS} itens "
                f"somando R$ {VL_ROS}, quanto no razão analítico de obras de desativação, "
                f"com {QTD_ROD} registros totalizando R$ {VL_ROD:}.</p>"
            )

        # 5) Nenhum conciliado + divergências apenas no ROS
        elif not c and r and not d:
            texto += (
                f"não houve itens conciliados. As inconsistências concentram-se no ROS, "
                f"totalizando {QTD_ROS} registros com diferença de R$ {VL_ROS}, "
                "não havendo divergências identificadas no razão de desativação.</p>"
            )

        # 6) Nenhum conciliado + divergências apenas no razão de desativação
        elif not c and not r and d:
            texto += (
                f"não foram identificados itens conciliados. As divergências estão restritas ao "
                f"razão analítico de obras de desativação, com {QTD_ROD} registros "
                f"no valor total de R$ {VL_ROD}, sem inconsistências no ROS.</p>"
            )

        # 7) Nenhum conciliado + divergências nos dois lados
        elif not c and r and d:
            texto += (
                "não foram encontrados itens conciliados. "
                f"Foram identificadas divergências no ROS ({QTD_ROS} registros, R$ {VL_ROS}) "
                f"e no razão analítico de desativação ({QTD_ROD} registros, R$ {VL_ROD}).</p>"
            )

        # 8) Nenhum registro em nenhum dataframe (caso extremo)
        else:
            texto += (
                "não foram encontrados registros para conciliação, indicando ausência "
                "de dados tanto conciliados quanto divergentes.</p>"
            ) 

        st.html(texto)

        texto_ST_MOP += ajs_txt(texto)
        
        if existe_tabela('ROD_CA_TP', bd):
            ROD_CA_TP = pd.read_sql("SELECT * FROM ROD_CA_TP", bd)
            res = resumo_consolidado(ROD_CA_TP)

            VL_CA_TOT = f"{res['VL_CA_TOT']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            VL_CA_MOP = f"{res['VL_CA_MOP']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            VL_CA_ST = f"{res['VL_CA_ST']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            Pct_MOP = (res["VL_CA_MOP"] / res["VL_CA_TOT"]) if res["VL_CA_TOT"] else 0
            Pct_ST = (res["VL_CA_ST"] / res["VL_CA_TOT"]) if res["VL_CA_TOT"] else 0
            if abs(Pct_MOP - Pct_ST) < 0.1:
                classificacao = "participações equilibradas entre mão de obra própria e de terceiros"
            elif Pct_MOP > Pct_ST:
                classificacao = "predominância de mão de obra própria"
            else:
                classificacao = "predominância de serviços de terceiros"

            Pct_MOP = f"{Pct_MOP:,.2%}".replace(",", "X").replace(".", ",").replace("X", ".")
            Pct_ST = f"{Pct_ST:,.2%}".replace(",", "X").replace(".", ",").replace("X", ".")

            texto = (
                f"<p  style='text-align: justify;text-indent: 40px'>Com base nos valores consolidados de CA, <b>do ROD</b>, "
                f"o total apurado foi de R$ {VL_CA_TOT}. "
                f"Desse montante, a mão de obra própria correspondeu a R$ {VL_CA_MOP}, "
                f"representando aproximadamente {Pct_MOP}. "
                f"Já a mão de obra de terceiros totalizou R$ {VL_CA_ST}, "
                f"equivalendo a cerca de {Pct_ST} do valor analisado. "
                f"Observa-se, portanto, {classificacao} no conjunto das atividades analisadas. </p>"
            )

            texto_ST_MOP += ajs_txt(texto)
            st.html(texto)
            st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Dito isso, passamos a analisar os dados de CA do ROD.
                    A primeira análise é avaliar a distribuição entre as diferentes fases do projeto: projeto, transporte,
                    gerenciamento, montagem, fiscalização e custos de suporte. O gráfico abaixo apresenta a distribuição de
                    todas as obras do ROD:</p>
                    """)
            res = resumo_por_fase(ROD_CA_TP)

            texto_ST_MOP += """
                                <p1">Dito isso, passamos a analisar os dados de CA do ROD.
                    A primeira análise é avaliar a distribuição entre as diferentes fases do projeto: projeto, transporte,
                    gerenciamento, montagem, fiscalização e custos de suporte. O gráfico abaixo apresenta a distribuição de
                    todas as obras do ROD: </p1>
                    <INSERIR>CA_FASE_ROD.png</INSERIR>
                            """

            fases = list(res.keys())
            valores = np.array(list(res.values()))

            pct = valores / valores.sum()
            fig12, ax12 = plt.subplots(figsize=(10, 2))
            heatmap = ax12.imshow(pct.reshape(1, -1), cmap="viridis")

            ax12.set_xticks(np.arange(len(fases)))
            ax12.set_xticklabels(fases, rotation=45, ha="right", fontsize=8)
            ax12.set_yticks([])

            for i, v in enumerate(pct):
                txt_ax = f"{v:.2%}".replace(",", "X").replace(".", ",").replace("X", ".")
                ax12.text(i, 0, txt_ax, ha='center', va='center', color="white" if v < 0.4 else "black")

            plt.title("Participação por Fase do CA", fontsize=12)

            plt.tight_layout()
            col1n, col2n, col3n = st.columns([1,2,1], gap='small')
            with col2n:
                st.pyplot(fig12)
            fig12.savefig(f"{local}/RELATORIOS/figuras/CA_FASE_ROD.png", dpi=300, bbox_inches='tight')
            plt.close()

            fase_max = fases[np.argmax(valores)]
            pct_max = f"{pct.max():.2%}".replace(",", "X").replace(".", ",").replace("X", ".")

            texto = (
                f"<p  style='text-align: justify;text-indent: 40px'>A análise visual evidencia que a fase '{fase_max}' concentra a maior parcela "
                f"dos custos de CA, representando aproximadamente {pct_max} do total. "
                "Essa concentração indica onde os recursos estão mais intensamente alocados, "
                "direcionando a atenção para potenciais oportunidades de otimização ou para a "
                "necessidade de maior controle e acompanhamento nesta etapa específica. </p>"
            )
            st.html(texto)
            texto_ST_MOP += ajs_txt(texto)
            texto_ST_MOP += """
                                <p1>Agora, segregamos, ainda, por tipo de CA, MOP ou ST: </p1>
                                <INSERIR>CA_MOP_ST_FASE_ROD.png</INSERIR>
                            """
            res = resumo_por_tipo_mao_de_obra(ROD_CA_TP)

            fases = ['VL_FRT_TRN', 'VL_PRJ', 'VL_GER', 'VL_FISC', 'VL_MONT', 'VL_SUP']
            mop_vals = np.array([res["MOP"]["VL_Fase"].get(f, 0) for f in fases])
            st_vals  = np.array([res["ST"]["VL_Fase"].get(f, 0) for f in fases])
            mop_pct = mop_vals / mop_vals.sum()
            st_pct  = st_vals  / st_vals.sum()
            matriz = np.vstack([mop_pct, st_pct])

            st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Agora, segregamos, ainda, por tipo de CA, MOP ou ST:</p>
                    """)

            fig13, ax13 = plt.subplots(figsize=(12, 4))
            heatmap = ax13.imshow(matriz, cmap="viridis")


            ax13.set_xticks(np.arange(len(fases)))
            ax13.set_xticklabels(fases, rotation=45, ha="right", fontsize=8)
            ax13.set_yticks([0, 1])
            ax13.set_yticklabels(["MOP", "ST"], fontsize=8)
            plt.title("Participação por Fase do CA (MOP × ST)", fontsize=12)

            for i in range(2):
                for j in range(len(fases)):
                    txt_ax = f"{matriz[i, j]:.2%}".replace(",", "X").replace(".", ",").replace("X", ".")
                    ax13.text(j, i, txt_ax, ha="center", va="center", color="white" if matriz[i, j] < 0.4 else "black")

            plt.tight_layout()
            col1o, col2o, col3o = st.columns([1,2,1], gap='small')
            with col2o:
                st.pyplot(fig13)
            fig13.savefig(f"{local}/RELATORIOS/figuras/CA_MOP_ST_FASE_ROD.png", dpi=300, bbox_inches='tight')
            plt.close()

            fase_mop_max = fases[np.argmax(mop_vals)]
            fase_st_max  = fases[np.argmax(st_vals)]

            texto = (
                        f"<p  style='text-align: justify;text-indent: 40px'>O heatmap evidencia diferenças na distribuição dos custos entre mão de obra própria "
                        f"(MOP) e serviços de terceiros (ST). Para a MOP, a fase de maior participação é '{fase_mop_max}', "
                        f"enquanto para ST predomina a fase '{fase_st_max}', indicando que cada tipo de recurso apresenta "
                        f"padrões distintos de alocação. Essa visualização facilita a identificação de onde se concentram "
                        f"os esforços internos versus terceirizados. </p>"
                    )
            st.html(texto)

            if len(ROD_CA_TP)>0:
                texto_ST_MOP += ajs_txt(texto)
                texto_ST_MOP += """
                                    <p1>Foi elaborado uma amostra para análise dos dados acima. Assim, procedeu-se à integração entre a classificação 
                                    ABC e a técnica de Amostragem por Unidade Monetária (AUM/MUS) para seleção dos projetos do ROD a 
                                    serem examinados. A classificação ABC permitiu identificar os projetos mais relevantes, enquanto a 
                                    AUM assegurou uma seleção probabilística proporcional ao valor incorrido, conferindo maior 
                                    probabilidade de inclusão aos itens mais representativos da população. Essa abordagem combinada 
                                    fortalece a efetividade dos procedimentos de fiscalização, garantindo que a amostra seja 
                                    estatisticamente robusta, orientada por risco e direcionada para a detecção de potenciais 
                                    distorções materiais. </p1>
                                """
                res, amostra_final, IA, R, dd_res_amst = resumo_por_projeto(ROD_CA_TP, st=st)

                st.html("""<p  style='text-align: justify;text-indent: 40px'>Procedeu-se à integração entre a classificação 
                            ABC e a técnica de Amostragem por Unidade Monetária (AUM/MUS) para seleção dos projetos do ROD a 
                            serem examinados. A classificação ABC permitiu identificar os projetos mais relevantes, enquanto a 
                            AUM assegurou uma seleção probabilística proporcional ao valor incorrido, conferindo maior 
                            probabilidade de inclusão aos itens mais representativos da população. Essa abordagem combinada 
                            fortalece a efetividade dos procedimentos de fiscalização, garantindo que a amostra seja 
                            estatisticamente robusta, orientada por risco e direcionada para a detecção de potenciais 
                            distorções materiais. A coluna FLG_AMST identifica os projetos selecionados para verificação 
                            detalhada. Segue os resultados:</p>""")
                
                RESUMOa = res.copy().fillna(0)
                container8 = st.container(border=True)
                for n in ['VL_FRT_TRN', 'VL_PRJ', 'VL_GER', 'VL_FISC', 'VL_MONT', 'VL_SUP',
                        'VL_TOT_PRJ','VL_ACUM','Pct_PRJ','Pct_ACM']:
                    if n[:3] == 'Pct':
                        try:
                            RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                        except:
                            RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{float(x):,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                    else:
                        try:
                            RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
                        except:
                            RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{float(x):,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
                
                container8.dataframe(RESUMOa, width='stretch', hide_index=True)  

                st.html(dd_res_amst)
                texto_ST_MOP += ajs_txt(dd_res_amst)
                RESUMOa['Cd_ODD'] = RESUMOa['Cd_ODD'].astype(str)
                lst_prj = RESUMOa.loc[RESUMOa['FLG_AMST']==1, 'Cd_ODD'].drop_duplicates().to_list()
                lst_prj = (", ").join(lst_prj)

                R = f"{R:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                IA = f"{IA:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

                st.html(f"""<p  style='text-align: justify;text-indent: 40px'> 
                            Considerenado o exposto, o ponto inicial da amostragem foi de R$ {R}, e o total de projetos amostrados foi {len(amostra_final)}, 
                            sendo que o intervalor amostral foi de R$ {IA}. Interesante mencionarmos que podem exister itens de 
                            valor muito alto (que acabam ocupando vários intervalos. IA), o número de amostras pode ser grande em 
                            relação ao tamanho da população ou até o intervalo IA fica muito pequeno em relação aos degraus dos 
                            projetos. Isso provoca, como consequência, que um dado projeto é selecionado várias vezes, porque ele 
                            ocupa vários “pontos” do acumulado. Para evitar isso, quando um projeto é sorteado, ele não é reposto
                            para o sorteio seguinte, isto é, partir do segundo ponto de amostragem, se o projeto correspondente 
                            já tiver sido selecionado, o algoritmo avança para o próximo projeto elegível na lista ordenada, 
                            garantindo MUS sem reposição. Isso preserva a proporcionalidade ao valor e elimina duplicidades, 
                            tornando o sorteio mais eficiente e consistente para finalidade de fiscalização.</p>
                            <p  style='text-align: justify;text-indent: 40px'> Ademais, para cada projeto pode ocorrer uma quantidade 
                            significativa de lançamentos, mas lembramos que aqui a unidade de amostragem está sendo o projeto, 
                            não o lançamento. No caso de haver muitos lançamentos, dentro de cada projeto selecionado, faça uma
                            amostragem simplificada de lançamentos para validação. O arquivo com as amostras é AMST_ROD.csv, 
                            disponível no diretório {local}\AIS_ANLS. A seguir temos representação visual do processo.
                            </p>""")
                
                texto_ST_MOP += f"""
                                    <p1>Considerenado o exposto, o ponto inicial da amostragem foi de R$ {R}, e o total de projetos amostrados foi {len(amostra_final)}, 
                            sendo que o intervalor amostral foi de R$ {IA}. Interesante mencionarmos que podem exister itens de 
                            valor muito alto (que acabam ocupando vários intervalos. IA), o número de amostras pode ser grande em 
                            relação ao tamanho da população ou até o intervalo IA fica muito pequeno em relação aos degraus dos 
                            projetos. Isso provoca, como consequência, que um dado projeto é selecionado várias vezes, porque ele 
                            ocupa vários “pontos” do acumulado. Para evitar isso, quando um projeto é sorteado, ele não é reposto
                            para o sorteio seguinte, isto é, partir do segundo ponto de amostragem, se o projeto correspondente 
                            já tiver sido selecionado, o algoritmo avança para o próximo projeto elegível na lista ordenada, 
                            garantindo MUS sem reposição. Isso preserva a proporcionalidade ao valor e elimina duplicidades, 
                            tornando o sorteio mais eficiente e consistente para finalidade de fiscalização. </p>
                            <p1> Ademais, para cada projeto pode ocorrer uma quantidade 
                            significativa de lançamentos, mas lembramos que aqui a unidade de amostragem está sendo o projeto, 
                            não o lançamento. No caso de haver muitos lançamentos, dentro de cada projeto selecionado, faça uma
                            amostragem simplificada de lançamentos para validação. O arquivo com as amostras é AMST_ROD.csv, 
                            disponível no diretório {local}\AIS_ANLS. A seguir temos representação visual do processo. </p1>
                            <p1>A realização deste teste consiste em confrontar os 
                        valores apresentados no arquivo de Baixas com os registros correspondentes no Razão Analítico de Obras 
                        com Desativação, de forma a validar a consistência e a completude das informações consolidadas. 
                        O procedimento envolve verificar se as quantidades dos componentes principais no arquivo de baixas
                        estão devidamente suportados por lançamentos analíticos individualizados, observando 
                        critérios de competência, natureza e correção da conta contábil utilizada. Busca-se identificar 
                        eventuais divergências, omissões ou reclassificações indevidas, avaliando se o arquivo de Baixas reflete 
                        de maneira fidedigna a movimentação registrada no razão analítico e garantindo a confiabilidade das 
                        demonstrações gerenciais. </p1>
                            <INSERIR>CA_AMST_ROD.png</INSERIR>
                            <p1>As amostras selecionadas são: {lst_prj}.</p1>
                            """

                x = np.arange(len(res))
                y = res["VL_ACUM"]

                limA = res[res["CLS_ABC"] == "A"].index.max()
                limB = res[res["CLS_ABC"] == "B"].index.max()

                fig14 = plt.figure(figsize=(14, 6))
                cmap_line = plt.cm.plasma(0.75)
                cmap_points = plt.cm.plasma(0.25)
                plt.axvspan(0, limA, alpha=0.18, color="#f70a0a")
                plt.axvspan(limA, limB, alpha=0.15, color="#0404f3")
                plt.axvspan(limB, len(res), alpha=0.12, color="#09f567")
                plt.plot(x, y, linewidth=2, color=cmap_line)

                for idx, row in res.iterrows():
                    if row["FLG_AMST"] == 1:
                        plt.scatter(idx, row["VL_ACUM"], 
                                    s=80, 
                                    edgecolor="black", 
                                    linewidth=1.2, 
                                    facecolor=cmap_points)
                plt.title("Curva Acumulada de Projetos com Destaque ABC e Amostragem (AUM)", fontsize=16)
                plt.ylabel("Valor Acumulado", fontsize=12)

                passo = max(1, int(round(len(res) / 10, 0)))
                plt.xticks(
                                x[::passo], 
                                res["Cd_ODD"][::passo], 
                                rotation=45, 
                                ha="right",
                                fontsize=12
                            )

                plt.grid(alpha=0.2)
                plt.tight_layout()
                col1p, col2p, col3p = st.columns([1,2,1], gap='small')
                with col2p:
                    st.pyplot(fig14)
                fig14.savefig(f"{local}/RELATORIOS/figuras/CA_AMST_ROD.png", dpi=300, bbox_inches='tight')
                plt.close()
                
                res.to_csv(f"{local}/AIS_ANLS/AMST_ROD.csv", index=False, sep="|", decimal=",", encoding="Latin-1")
        
        xEsc = exportar_texto(f"{local}/RELATORIOS/textos", f"ST_MOP_ODD_ROS_DESC.txt", texto_ST_MOP, True)

@st.fragment
def vis_AX024(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if (not existe_tabela('Conciliados_Qtd', bd) or not existe_tabela('Nao_Conciliados_ROD_Qtd', bd) or
            not existe_tabela('Nao_Conciliados_BAIXAS_Qtd', bd)):
            return

        st.html(f"""<h3 style="text-align: center;font-size: 30px;">
                    Teste de Consistência de Quantidades entre ROD e BAIXAS</h3>
                    """)   
        
        if existe_tabela('Conciliados_Qtd', bd):
            CONC_QTD = pd.read_sql("SELECT * FROM Conciliados_Qtd", bd)
        else:
            CONC_QTD = pd.DataFrame()
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">A realização deste teste consiste em confrontar os 
                    valores apresentados no arquivo de Baixas com os registros correspondentes no Razão Analítico de Obras 
                    com Desativação, de forma a validar a consistência e a completude das informações consolidadas. 
                    O procedimento envolve verificar se as quantidades dos componentes principais no arquivo de baixas
                    estão devidamente suportados por lançamentos analíticos individualizados, observando 
                    critérios de competência, natureza e correção da conta contábil utilizada. Busca-se identificar 
                    eventuais divergências, omissões ou reclassificações indevidas, avaliando se o arquivo de Baixas reflete 
                    de maneira fidedigna a movimentação registrada no razão analítico e garantindo a confiabilidade das 
                    demonstrações gerenciais.
                    </p>
                    """)
            
        texto_ST_MOP = """
                            <p1>Também foi efetuada avaliação cruzada entre os 
                            valores apresentados no arquivo de Baixas com os registros correspondentes no Razão Analítico de Obras 
                            com Desativação, de forma a validar a consistência e a completude das informações consolidadas. 
                            O procedimento envolve verificar se as quantidades dos componentes principais no arquivo de baixas
                            estão devidamente suportados por lançamentos analíticos individualizados, observando 
                            critérios de competência, natureza e correção da conta contábil utilizada. Busca-se identificar 
                            eventuais divergências, omissões ou reclassificações indevidas, avaliando se o arquivo de Baixas reflete 
                            de maneira fidedigna a movimentação registrada no razão analítico. 
                            </p1> 
                        """

        CONC_QTD = CONC_QTD.fillna(0)
        RESUMOa = CONC_QTD.copy()
        
        if len(CONC_QTD) > 0:
            st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">A seguir temos os resultados, na forma tabular, 
                    dos testes dos itens que foram conciliados.
                    </p>
                    """)
            container10 = st.container(border=True)

            criterio_CN = RESUMOa['DELTA'] == 0
            criterio_NCN = RESUMOa['DELTA'] != 0
            Qtd_CN_ROD = RESUMOa[criterio_CN]['Qtd_ROD'].abs().sum()
            Qtd_NCN_ROD = RESUMOa[criterio_NCN]['Qtd_ROD'].abs().sum()
            Qtd_OCOR_CN = criterio_CN.sum()
            Qtd_OCOR_NCN = criterio_NCN.sum()
            Qtd_OCOR = Qtd_OCOR_NCN + Qtd_OCOR_CN

            for n in ['Qtd_BAIXAS','Qtd_ROD','DELTA']:
                if n in ['DELTA']:
                    RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{float(x):,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                else:
                    RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{float(x):,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
            container10.dataframe(RESUMOa, width='stretch', hide_index=True)

        else:
            Qtd_CN_ROD = 0
            Qtd_NCN_ROD = 0
            Qtd_OCOR = 0
            Qtd_OCOR_CN = 0
            Qtd_OCOR_NCN = 0

        Pct_ANL = f"{Qtd_CN_ROD/(Qtd_NCN_ROD+Qtd_CN_ROD) if Qtd_NCN_ROD+Qtd_CN_ROD else 0:,.2%}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        Qtd_CN_ROD = f"{Qtd_CN_ROD:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        Qtd_NCN_ROD = f"{Qtd_NCN_ROD:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        Qtd_OCOR_CN = f"{Qtd_OCOR_CN:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        Qtd_OCOR_NCN = f"{Qtd_OCOR_NCN:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

        if Pct_ANL != "100,00%":
            TRC_DIV = f"""Por sua vez, foram identificadas divergências em {Qtd_OCOR_NCN} projetos, somando diferenças 
            de {Qtd_NCN_ROD}, demandando investigação das causas e verificação dos impactos potenciais."""
        else:
            TRC_DIV = f"""Não foram identificadas divergências entre as quantidades analisadas, indicando total aderência 
            entre o arquivo de Baixas e o ROD."""
        if len(CONC_QTD) > 0:
            st.html(f"""
                        <p  style="text-align: justify;text-indent: 40px">A síntese da conciliação entre o arquivo de Baixas 
                        e o ROD indica que, do total de projetos avaliados, os projetos que apresentaram plena correspondência 
                        totalizaram {Qtd_OCOR_CN} projetos, com quantidade agregada de {Qtd_CN_ROD}. {TRC_DIV} Essa consolidação 
                        permite avaliar de forma objetiva o nível de conformidade entre os registros conciliados, que foi de 
                        {Pct_ANL} nesta empresa.</p>
                        """)
            texto_ST_MOP += f"""
                        <p1>A síntese da conciliação entre o arquivo de Baixas 
                        e o ROD indica que, do total de projetos avaliados, os projetos que apresentaram plena correspondência 
                        totalizaram {Qtd_OCOR_CN} projetos, com quantidade agregada de {Qtd_CN_ROD}. {TRC_DIV} Essa consolidação 
                        permite avaliar de forma objetiva o nível de conformidade entre os registros conciliados, que foi de 
                        {Pct_ANL} nesta empresa. 
                        </p1> 
                        """
        else:
            st.html(f"""
                        <p  style="text-align: justify;text-indent: 40px">Nesta empresa não houve conciliação de dados. Isto
                        provavelmente decorre de um erro na chave declarada, ou no arquivo de Baixas ou no arquivo ROD. Revise os
                        dados e refaça as análises.</p>
                        """)
            texto_ST_MOP += f"""
                        <p1>Nesta empresa não houve conciliação de dados. Isto
                        provavelmente decorre de um erro na chave declarada, ou no arquivo de Baixas ou no arquivo ROD. Revise os
                        dados e refaça as análises. 
                        </p1> 
                        """
        

        dic = {}
        if existe_tabela('Nao_Conciliados_BAIXAS_Qtd', bd):
            dic['RESUMO_NC_BAIXAS'] = pd.read_sql("SELECT * FROM Nao_Conciliados_BAIXAS_Qtd", bd)
        else:
            dic['RESUMO_NC_BAIXAS'] = pd.DataFrame()
        if existe_tabela('Nao_Conciliados_ROD_Qtd', bd):
            dic['RESUMO_NC_ROD'] = pd.read_sql("SELECT * FROM Nao_Conciliados_ROD_Qtd", bd)
        else:
            dic['RESUMO_NC_ROD'] = pd.DataFrame()

        for nm in ['BAIXAS','ROD']:
            ax = [x for x in ['BAIXAS', 'ROD'] if x != nm]
            if len(dic[f'RESUMO_NC_{nm}']) == 0:
                dic[f'Qtd_{nm}'] = 0
                st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Na tabela {nm}, apresentada,
                    não foi encontrado registros não declarados na tabela {ax[0]}. </p>
                    """) 
                texto_ST_MOP += f"""Na tabela {nm}, apresentada,
                    não foi encontrado registros não declarados na tabela {ax[0]}. """       
            else:
                dic[f'Qtd_{nm}'] = len(dic[f'RESUMO_NC_{nm}'])
                st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Na tabela {nm}, apresentada,
                    foi encontrado {dic[f'Qtd_{nm}']} registros não declarados na tabela {ax[0]}. A seguir, em dados 
                    tabulares, os projetos não encontrados:</p>
                    """)
                texto_ST_MOP += f"""Na tabela {nm}, apresentada,
                    foi encontrado {dic[f'Qtd_{nm}']} registros não declarados na tabela {ax[0]}. """
                RESUMOa = dic[f'RESUMO_NC_{nm}'].copy().fillna(0)
                container11 = st.container(border=True)
                for n in ['Qtd_BAIXAS','Qtd_ROD']:
                    try:
                        RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    except:
                        RESUMOa[n] = RESUMOa[n].apply(lambda x: f"{float(x):,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
                container11.dataframe(RESUMOa, width='stretch', hide_index=True)  

        
        Qtd_CN = Qtd_CN_ROD if Qtd_OCOR != "0" else "0,00"
        QTD_BAIXAS = dic[f'Qtd_BAIXAS']
        Qtd_UC_BAIXAS = ((dic['RESUMO_NC_BAIXAS']['Qtd_BAIXAS'].fillna(0).abs().sum()) 
                    if QTD_BAIXAS > 0 
                    else 0)

        QTD_ROD = dic[f'Qtd_ROD']
        Qtd_UC_ROD = ((dic['RESUMO_NC_ROD']['Qtd_ROD'].fillna(0).abs().sum()) 
                    if QTD_ROD > 0 
                    else 0)
        try:
            c = Qtd_OCOR > 0
        except:
            Qtd_OCOR = int(Qtd_OCOR.replace(".",""))
            c = Qtd_OCOR > 0
        r = QTD_BAIXAS > 0
        d = QTD_ROD > 0

        QTD_OCOR = f"{Qtd_OCOR:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        QTD_BAIXAS = f"{QTD_BAIXAS:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        QTD_ROD = f"{QTD_ROD:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        Qtd_UC_BAIXAS = f"{Qtd_UC_BAIXAS:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        Qtd_UC_ROD = f"{Qtd_UC_ROD:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        texto = """<p  style="text-align: justify;text-indent: 40px">A conciliação entre o arquivo de baixas e o 
                    razão analítico de obras de desativação apresentou o seguinte resultado: """

        # 1) Somente conciliados
        if c and not r and not d:
            texto += (
                f"todos os itens foram conciliados, totalizando {QTD_OCOR} registros "
                f"com quantidade consolidada de {Qtd_CN}, não havendo divergências "
                "nem no arquivo de baixas nem no razão analítico de obras de desativação.</p>"
            )

        # 2) Conciliados + divergências no arquivo de baixas
        elif c and r and not d:
            texto += (
                f"{QTD_OCOR} registros foram conciliados, no total, em quantidade, de {Qtd_CN}. "
                f"Foram identificadas divergências no arquivo de baixas, abrangendo {QTD_BAIXAS} registros "
                f"com diferenças de {Qtd_UC_BAIXAS}, em quantidade, enquanto não foram apontadas "
                "inconsistências no razão analítico de obras de desativação.</p>"
            )

        # 3) Conciliados + divergências no razão de desativação
        elif c and not r and d:
            texto += (
                f"{QTD_OCOR} itens foram conciliados corretamente, totalizando {Qtd_CN}, em quantidade. "
                f"Foram identificadas divergências no razão analítico de obras de desativação, "
                f"abrangendo {QTD_ROD} registros no total de {Qtd_UC_ROD}, em quantidade, "
                "enquanto o arquivo de baixas não apresentou inconsistências.</p>"
            )

        # 4) Conciliados + divergências nos dois lados
        elif c and r and d:
            texto += (
                f"foram conciliados {QTD_OCOR} registros ({Qtd_CN}, em quantidade). "
                f"No entanto, foram encontradas divergências tanto no arquivo de baixas, com {QTD_BAIXAS} itens "
                f"totalizando {Qtd_UC_BAIXAS}, quanto no razão analítico de obras de desativação, "
                f"com {QTD_ROD} registros totalizando {Qtd_UC_ROD}, ambos em quantidade.</p>"
            )

        # 5) Nenhum conciliado + divergências apenas no arquivo de baixas
        elif not c and r and not d:
            texto += (
                f"não houve itens conciliados. As inconsistências concentram-se no arquivo de baixas, "
                f"totalizando {QTD_BAIXAS} registros com diferença de {Qtd_UC_BAIXAS}, em quantidade, "
                "não havendo divergências identificadas no razão de desativação.</p>"
            )

        # 6) Nenhum conciliado + divergências apenas no razão de desativação
        elif not c and not r and d:
            texto += (
                f"não foram identificados itens conciliados. As divergências estão restritas ao "
                f"razão analítico de obras de desativação, com {QTD_ROD} registros "
                f"no total de {Qtd_UC_ROD}, em quantidade, sem inconsistências no arquivo de baixas.</p>"
            )

        # 7) Nenhum conciliado + divergências nos dois lados
        elif not c and r and d:
            texto += (
                "não foram encontrados itens conciliados. "
                f"Foram identificadas divergências no arquivo de baixas ({QTD_BAIXAS} registros, {Qtd_UC_BAIXAS}) "
                f"e no razão analítico de desativação ({QTD_ROD} registros, {Qtd_UC_ROD}).</p>"
            )

        # 8) Nenhum registro em nenhum dataframe (caso extremo)
        else:
            texto += (
                "não foram encontrados registros para conciliação, indicando ausência "
                "de dados tanto conciliados quanto divergentes.</p>"
            ) 

        st.html(texto)

        texto_ST_MOP += ajs_txt(texto)
        xEsc = exportar_texto(f"{local}/RELATORIOS/textos", f"MAT_ODD_ROS_DESC.txt", texto_ST_MOP, True)


@st.fragment
def vis_AX025(bd_path, caminho, empresa, st, local): 
    with sl.connect(bd_path) as bd:
        if not existe_tabela('ANL_INCREMENTAL', bd):
            return
        sSQL = ""
        try:
            tbls = ['OE_MOV', 'OE_CCCMOV', 'OE_IRMOV', 'OE_PLPTMOV']
            for i,tbl in enumerate(tbls):
                if existe_tabela(tbl, bd):
                    if (sSQL == ""):
                        sSQL = f"SELECT t{i}.* FROM {tbl} t{i}"
                    else:
                        sSQL += f" UNION ALL SELECT t{i}.* FROM {tbl} t{i}"

            INCRoe = pd.read_sql(sSQL, bd)
        except:
            INCRoe = pd.read_sql("SELECT t1.* FROM OE_AGR t1", bd)
        lst_col = []
        for col in INCRoe.columns.to_list():
            if (col.upper()[:4] == 'VL_M'):
                lst_col += [col]
                INCRoe[col] = pd.to_numeric(INCRoe[col], errors='coerce')
        INCRoe = INCRoe[lst_col].sum(numeric_only=True)
        INCRoe.name = 'VL_OE'
        INCRoe = INCRoe.to_frame().reset_index(drop=True)
        INCRoe['Dt_REF'] =  pd.date_range(start=st.session_state.dt_ini, periods=len(INCRoe), freq='M') 

        Dt_ARQ = max_arq("ROA", bd, empresa)
        if Dt_ARQ:
            sSQL = f"""
                    SELECT 
                            t1.Qtd,
                            t1.VL_tot,
                            t1.Dt_Lcmto,
                            t1.Nr_TUC,
                            t1.Cd_NG,
                            t1.Nr_TI
                    FROM ROA t1 WHERE t1.Dt_ARQ={Dt_ARQ};
                    """
            
            ROA = pd.read_sql(sSQL, bd)
            for n in ['Qtd', 'VL_tot']:
                if ROA[n].dtype == 'object':
                    ROA[n] = pd.to_numeric(ROA[n].str.replace(",","."), errors='coerce')
            if ROA['Dt_Lcmto'].dtype == 'object':
                ROA['Dt_Lcmto'] = pd.to_datetime(ROA['Dt_Lcmto'], errors='coerce')
        else:
            return

        sSQL = """
                SELECT 
                        t1.Dt_Imob,
                        t1.Dt_CNTB_AJST,
                        t1.Nr_TUC,
                        t1.Nr_TI,
                        t1.Cd_TP_AVAL,
                        t1.MTD_AVAL,
                        t1.VL_VOC,
                        t1.VL_VNR_SFF,
                        t1.VL_VNR_UC,
                        t1.VL_DAC_UC,
                        t1.VL_VBR_UC,
                        t1.VL_VOCsjoa_IMB_AT
                FROM ANL_INCREMENTAL t1 WHERE t1.Cd_CONC=1 AND t1.FLG_ELIG=1;
            """
        
        INCRini = pd.read_sql(sSQL, bd)
        FA_OE = INCRini['VL_VNR_UC'].sum()/INCRini['VL_VOC'].sum()
        INCRini['ANO'] = pd.to_datetime(INCRini['Dt_Imob'], errors='coerce').dt.year

        st.html(f"""<h2 style="text-align: center;font-size: 30px;">
                                    Investimento cumulativo</h2>
                    <p  style="text-align: justify;text-indent: 40px">Abaixo, observamos
                    o investimento cumulativo ao longo do período 
                    incremental. Também apresentamos por data de imobilização e data 
                    ajustada, e do razão de obras do período incremental. Considerando 
                    o alto grau de discretização dos investimentos de alta tensão, 
                    dependendo do porte da empresa, espera-se descontinuidades no
                        gráfico.
                    </p><br>
                    """)

        ROA_RES = pd.pivot_table(ROA, values = ['VL_tot'], index = ['Dt_Lcmto'], columns = ['Cd_NG'], 
                    aggfunc = "sum", fill_value = 0).reset_index()
        ROA_RES.columns = ROA_RES.columns.droplevel()
        for i in range(1,7):
            if str(i) not in ROA_RES.columns.to_list():
                ROA_RES[str(i)]=0
        ROA_RES = ROA_RES[['', '1', '2', '3', '4', '5', '6']]
        ROA_RES.columns = ['Dt_Lcmto','UC','COM','MOP','ST','JOA','OUTROS']
        ROA_RES = ROA_RES.sort_values(by='Dt_Lcmto')
        ROA_RES['ACUM_MAT'] = ROA_RES['UC'].cumsum() + ROA_RES['COM'].cumsum()
        ROA_RES['ACUM_MOP'] = ROA_RES['MOP'].cumsum() 
        ROA_RES['ACUM_ST'] = ROA_RES['ST'].cumsum()

        ROAa = ROA.groupby(['Dt_Lcmto'], dropna=False)[['VL_tot']].sum().reset_index()
        INCRini['Dt_Imob'] = pd.to_datetime(INCRini['Dt_Imob'], errors='coerce')
        INCRini['Dt_CNTB_AJST'] = pd.to_datetime(INCRini['Dt_CNTB_AJST'], errors='coerce')

        TESTE_02 = INCRini.groupby(['Dt_Imob'])[['VL_VNR_UC']].sum().reset_index()
        TESTE_02 = TESTE_02.sort_values(by='Dt_Imob')
        TESTE_02['ACUM'] = (TESTE_02['VL_VNR_UC'].cumsum() / TESTE_02['VL_VNR_UC'].sum() 
                            * 100)
        
        ROAa = ROAa.sort_values(by='Dt_Lcmto')
        ROAa['ACUM'] = ROAa['VL_tot'].cumsum() / ROAa['VL_tot'].sum() * 100

        fig2 = make_subplots(rows=1, cols=2, subplot_titles=[
                                'Cumulativo, NG', 
                                'Cumulativo, por data'
                            ])

        fig2.add_trace(go.Scatter(x=ROA_RES['Dt_Lcmto'], y=ROA_RES['ACUM_MAT'],  
                                line=dict(color='rgba(0,0,128,0.5)'), stackgroup='one', 
                                name='MATERIAL ROA'), row=1, col=1)
        fig2.add_trace(go.Scatter(x=ROA_RES['Dt_Lcmto'], y=ROA_RES['ACUM_MOP'], 
                                line=dict(color='rgba(65,105,225,0.5)'), stackgroup='one',
                                name='MOP ROA'), row=1, col=1)
        fig2.add_trace(go.Scatter(x=ROA_RES['Dt_Lcmto'], y=ROA_RES['ACUM_ST'],  
                                line=dict(color='rgba(30,144,255,0.5)'), stackgroup='one', 
                                name='ST ROA'), row=1, col=1)
        
        D1 = st.session_state.dt_ini
        D2 = st.session_state.dt_fim
        D1a = INCRini['Dt_CNTB_AJST'].min() if (-D1.year + D2.year) > 6 else D1
        datas = [D1a + timedelta(days=i) for i in range((D2 - D1a).days + 1)]
        valores_y = [i/len(datas)*100 for i in range(len(datas))]
        
        if st.session_state.dt_fim < date.today():
            TESTE_02b = INCRini.groupby(['Dt_CNTB_AJST'])[['VL_VNR_UC']].sum().reset_index()
            TESTE_02b = TESTE_02b.sort_values(by='Dt_CNTB_AJST')
            TESTE_02b['ACUM'] = TESTE_02b['VL_VNR_UC'].cumsum() / TESTE_02b['VL_VNR_UC'].sum() * 100
            fig2.add_trace(go.Scatter(x=ROAa['Dt_Lcmto'], y=ROAa['ACUM'], fill='tozeroy', 
                                    line=dict(color='chartreuse'), 
                                    name='ROA'), row=1, col=2)
            fig2.add_trace(go.Scatter(x=TESTE_02['Dt_Imob'], y=TESTE_02['ACUM'], fill='tozeroy', 
                                    line=dict(color='#2ca02c'), 
                                    name='INCR Data Imobilização'), row=1, col=2)
            fig2.add_trace(go.Scatter(x=TESTE_02b['Dt_CNTB_AJST'], y=TESTE_02b['ACUM'], fill='tozeroy', 
                                    line=dict(color='#17becf'), 
                                    name='INCR Data Corrigida'), row=1, col=2)
            fig2.add_trace(go.Scatter(x=datas, y=valores_y, fill='tozeroy', 
                                line=dict(color='#D3D3D3'), 
                                name='Referência'), row=1, col=2)
        else:
            TESTE_02 = TESTE_02.set_index('Dt_Imob').sort_index()
            TESTE_02['VL_CUMSUM'] = TESTE_02['VL_VNR_UC'].cumsum()
            data_final_observada = TESTE_02.index.max()
            novo_indice = pd.date_range(start=TESTE_02.index.min(), end=st.session_state.dt_fim, freq='MS')
            df_estendido = TESTE_02.reindex(novo_indice)
            x_existente = TESTE_02.index.map(pd.Timestamp.toordinal).to_numpy(dtype=float)
            y_existente = TESTE_02['VL_CUMSUM'].to_numpy(dtype=float)
            m, c = np.polyfit(x_existente, y_existente, deg=1)
            x_todos = df_estendido.index.map(pd.Timestamp.toordinal)
            valores_extrapolados = m * x_todos + c
            n = len(x_existente)

            if n > 2:
                valores_ajustados = m * x_existente + c
                residuos = y_existente - valores_ajustados
                graus_liberdade = n - 2
                erro_padrao_residual = np.sqrt(
                                                    np.sum(residuos**2) / graus_liberdade
                                                )
                media_x = x_existente.mean()
                soma_quadrados_x = np.sum(
                                            (x_existente - media_x) ** 2
                                        )
                nivel_confianca = 0.95
                alfa = 1 - nivel_confianca
                t_critico = t.ppf(
                                    1 - alfa / 2,
                                    df=graus_liberdade,
                                )
                erro_previsao = erro_padrao_residual * np.sqrt(
                                                                    1
                                                                    + (1 / n)
                                                                    + ((x_todos - media_x) ** 2 / soma_quadrados_x)
                                                                )
                margem = t_critico * erro_previsao
                limite_inferior = valores_extrapolados - margem
                limite_superior = valores_extrapolados + margem
            else:
                limite_inferior = valores_extrapolados
                limite_superior = valores_extrapolados

            limite_inferior = np.maximum(
                                            limite_inferior,
                                            0,
                                        )
            serie_prevista = pd.Series(
                                        valores_extrapolados,
                                        index=df_estendido.index,
                                    )

            df_estendido['VL_CUMSUM'] = df_estendido['VL_CUMSUM'].fillna(serie_prevista)
            df_estendido["VL_LIM_INF"] = limite_inferior
            df_estendido["VL_LIM_SUP"] = limite_superior
            mascara_observado = df_estendido.index <= data_final_observada
            df_estendido.loc[
                                mascara_observado,
                                "VL_LIM_INF",
                            ] = df_estendido.loc[
                                                    mascara_observado,
                                                    "VL_CUMSUM",
                                                ]

            df_estendido.loc[
                                mascara_observado,
                                "VL_LIM_SUP",
                            ] = df_estendido.loc[
                                                    mascara_observado,
                                                    "VL_CUMSUM",
                                                ]

            TESTE_02 = df_estendido.reset_index().rename(columns={'index': 'Dt_Imob'})
            TESTE_02['ACUM'] = TESTE_02['VL_CUMSUM'] / TESTE_02['VL_CUMSUM'].iloc[-1] * 100
            TESTE_02['ACUM2'] = TESTE_02['VL_VNR_UC'].cumsum() / TESTE_02['VL_CUMSUM'].iloc[-1] * 100
            TESTE_02["ACUM_INF"] = (
                                        TESTE_02["VL_LIM_INF"]
                                        / TESTE_02['VL_CUMSUM'].iloc[-1]
                                        * 100
                                    )

            TESTE_02["ACUM_SUP"] = (
                                        TESTE_02["VL_LIM_SUP"]
                                        / TESTE_02['VL_CUMSUM'].iloc[-1]
                                        * 100
                                    )
            
            fig2.add_trace(
                            go.Scatter(
                                x=TESTE_02["Dt_Imob"],
                                y=TESTE_02["ACUM_SUP"],
                                mode="lines",
                                line=dict(
                                    width=0,
                                ),
                                showlegend=False,
                                hoverinfo="skip",
                            ),
                            row=1,
                            col=2,
                        )

            fig2.add_trace(
                            go.Scatter(
                                x=TESTE_02["Dt_Imob"],
                                y=TESTE_02["ACUM_INF"],
                                mode="lines",
                                line=dict(
                                    width=0,
                                ),
                                fill="tonexty",
                                fillcolor="rgba(128, 128, 128, 0.20)",
                                name="Intervalo de previsão — 95%",
                                hovertemplate=(
                                    "Data: %{x|%m/%Y}<br>"
                                    "Limite inferior: %{y:.2f}%"
                                    "<extra></extra>"
                                ),
                            ),
                            row=1,
                            col=2,
                        )

            fig2.add_trace(
                            go.Scatter(
                                x=TESTE_02["Dt_Imob"],
                                y=TESTE_02["ACUM"],
                                mode="lines",
                                line=dict(
                                    color="#808080",
                                    dash="dash",
                                    width=2,
                                ),
                                name="INCR previsto",
                                hovertemplate=(
                                    "Data: %{x|%m/%Y}<br>"
                                    "Previsto: %{y:.2f}%"
                                    "<extra></extra>"
                                ),
                            ),
                            row=1,
                            col=2,
                        )

            fig2.add_trace(
                                go.Scatter(
                                    x=TESTE_02["Dt_Imob"],
                                    y=TESTE_02["ACUM2"],
                                    mode="lines",
                                    fill="tozeroy",
                                    line=dict(
                                        color="#2ca02c",
                                        width=2,
                                    ),
                                    name="INCR imobilizado",
                                    hovertemplate=(
                                        "Data: %{x|%m/%Y}<br>"
                                        "Imobilizado: %{y:.2f}%"
                                        "<extra></extra>"
                                    ),
                                ),
                                row=1,
                                col=2,
                            )
            valor_final = f"{TESTE_02['VL_CUMSUM'].iloc[-1]:,.2f}".replace(",","x").replace(".",",").replace("x",".")
            fig2.add_annotation(
                                    x=TESTE_02["Dt_Imob"].iloc[-1],
                                    y=TESTE_02["ACUM"].iloc[-1],
                                    text=f"Previsto<br>{valor_final}",
                                    showarrow=True,
                                    arrowhead=2,
                                    arrowsize=1.2,
                                    arrowwidth=1.5,
                                    ax=-70,
                                    ay=-40,
                                    bgcolor="rgba(255,255,255,0.85)",
                                    bordercolor="gray",
                                    borderwidth=1,
                                    font=dict(size=11),
                                    row=1,
                                    col=2
                                )

        fig2.update_layout(title = "Investimento",
                                xaxis_title='Ano', 
                                yaxis_title='Valor (R$)'
                            )

        st.plotly_chart(fig2)
        fig2.update_layout(
                                width=1000, 
                                height=800,
                                autosize=False,
                                margin=dict(l=60, r=20, t=100, b=100),
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.15,
                                    xanchor="center",
                                    x=0.5
                                ),
                                template="plotly_white"
                            )
        fig2.update_annotations(font_size=14)
        fig2.write_image(rf"{local}/RELATORIOS/figuras/dispendios.png", width=1000, height=800, scale=3)
        ROA_RES.to_sql("TBL_ROA_RES", bd, if_exists='replace', index=False)

        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Espera-se que as 
                    obras de média e baixa tensão tenham uma distribuição mais 
                    uniforme ao longo do tempo, pois são realizadas continuamente 
                    pela empresa (recomenda-se a leitura do Livro Verde). No entanto, as redes de 34,5 kV, 
                    embora pertencentes ao segmento de média tensão, podem ser classificadas como 
                    subtransmissão dependendo da visão funcional da distribuidora. 
                    Essa categorização pode resultar em uma execução menos regular, 
                    seja por uma maior discretização no planejamento ou por uma 
                    flexibilidade ampliada nos prazos de implementação. A seguir, 
                    analisaremos essas obras.
                    </p><br>
                    """)
        
        dic_TI = {(1,1) : ['40', '41', '93', '96'],
                    (1,2) : ['93', '96'],
                    (2,1) : ['40', '41'],}
        
        fig3 = make_subplots(rows=2, cols=2, subplot_titles=[
                                'Cumulativo, Obras de MT/BT',
                                'Cumulativo, Obras de Medição',
                                'Cumulativo, Obras de Rede',
                            ])

        D3 = pd.to_datetime(INCRini['Dt_Imob'], format='%Y-%m-%d %H:%M:%S', errors='coerce').max()

        D1a = pd.to_datetime(D1a)
        D2  = pd.to_datetime(D2)
        posicao = 100 * (D3 - D1a).days / (D2 - D1a).days
        posicao = max(0, min(100, posicao))

        for chave, valor in dic_TI.items():
            LST_TI = valor

            ROAa = ROA[ROA['Nr_TI'].isin(LST_TI)].groupby(['Dt_Lcmto'], 
                                        dropna=False)[['VL_tot']].sum().reset_index()

            TESTE_02 = INCRini[INCRini['Nr_TI'].isin(LST_TI)].groupby(['Dt_Imob'], 
                                        dropna=False)[['VL_VNR_UC']].sum().reset_index()
            TESTE_02 = TESTE_02.sort_values(by='Dt_Imob')
            TESTE_02['ACUM'] = TESTE_02['VL_VNR_UC'].cumsum() / TESTE_02['VL_VNR_UC'].sum() * posicao

            TESTE_02b = INCRini[INCRini['Nr_TI'].isin(LST_TI)].groupby(['Dt_CNTB_AJST'],
                                        dropna = False)[['VL_VNR_UC']].sum().reset_index()
            TESTE_02b = TESTE_02b.sort_values(by='Dt_CNTB_AJST')
            TESTE_02b['ACUM'] = TESTE_02b['VL_VNR_UC'].cumsum() / TESTE_02b['VL_VNR_UC'].sum() * posicao

            ROAa = ROAa.sort_values(by='Dt_Lcmto')
            ROAa['ACUM'] = ROAa['VL_tot'].cumsum() / ROAa['VL_tot'].sum() * posicao

            fig3.add_trace(go.Scatter(x=TESTE_02['Dt_Imob'], y=TESTE_02['ACUM'], fill='tozeroy', 
                                    line=dict(color='#2ca02c'), 
                                    name='INCR Data Imobilização'), row=chave[0], col=chave[1])
            fig3.add_trace(go.Scatter(x=TESTE_02b['Dt_CNTB_AJST'], y=TESTE_02b['ACUM'], fill='tozeroy', 
                                    line=dict(color='#17becf'), 
                                    name='INCR Data Corrigida'), row=chave[0], col=chave[1])
            fig3.add_trace(go.Scatter(x=ROAa['Dt_Lcmto'], y=ROAa['ACUM'], fill='tozeroy', 
                                    line=dict(color='chartreuse'), 
                                    name='ROA'), row=chave[0], col=chave[1])
            fig3.add_trace(go.Scatter(x=datas, y=valores_y, fill='tozeroy', 
                                    line=dict(color='#D3D3D3'), 
                                    name='Referência'), row=chave[0], col=chave[1])

        fig3.update_layout(title = "Investimento",
                                xaxis_title='Ano', 
                                yaxis_title='Valor (%)'
                            )

        vlr = f"{TESTE_02['VL_VNR_UC'].sum():,.2f}".replace(".","x").replace(",",".").replace("x",",")

        fig3.add_annotation(
                                x=1,
                                y=-0.1,
                                xref="paper",
                                yref="paper",
                                text=f"Base de análise: {vlr}",
                                showarrow=False
                            )
        
        st.plotly_chart(fig3)

        fig3.update_layout(
                                width=1000, 
                                height=800,
                                autosize=False,
                                margin=dict(l=60, r=20, t=100, b=100),
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.15,
                                    xanchor="center",
                                    x=0.5
                                ),
                                template="plotly_white"
                            )
        fig3.update_annotations(font_size=14)
        fig3.write_image(rf"{local}/RELATORIOS/figuras/dispendios_tipologia.png", width=1000, height=800, scale=3)

        TESTE_02 = INCRini.copy()
        TESTE_02['ANO'] = TESTE_02['Dt_Imob'].dt.year
        TESTE_02['ANO1'] = TESTE_02['Dt_CNTB_AJST'].dt.year
        TESTE_02['MES'] = TESTE_02['Dt_Imob'].dt.strftime('%B')
        TESTE_02_P1 = TESTE_02[TESTE_02['ANO'] < TESTE_02['ANO'].max()].copy()
        TESTE_02_P1['MES'] = 'TOTAL'
        TESTE_02_P2 = TESTE_02[TESTE_02['ANO'] == TESTE_02['ANO'].max()].copy()
        TESTE_02_T = pd.concat([TESTE_02_P1,TESTE_02_P2])
        TESTE_02_T = TESTE_02_T.groupby(['Nr_TI','ANO','ANO1','MES'],
                                dropna=False)[['VL_VNR_UC','VL_DAC_UC',
                                'VL_VBR_UC','VL_VOCsjoa_IMB_AT']].sum().reset_index()

        meses = ['TOTAL', 'January', 'February', 'March', 'April', 'May', 
                    'June', 'July', 'August', 'September', 'October', 'November', 
                    'December']
        TESTE_02_T['MES'] = pd.Categorical(TESTE_02_T['MES'], categories=meses, 
                                            ordered=True)
        TESTE_02_T = TESTE_02_T.sort_values(['Nr_TI','ANO','ANO1','MES'])

        meses_traducao = {
                            "January": "Janeiro",
                            "February": "Fevereiro",
                            "March": "Março",
                            "April": "Abril",
                            "May": "Maio",
                            "June": "Junho",
                            "July": "Julho",
                            "August": "Agosto",
                            "September": "Setembro",
                            "October": "Outubro",
                            "November": "Novembro",
                            "December": "Dezembro"
                        }
        
        TESTE_02_T['MES'] = TESTE_02_T['MES'].replace(meses_traducao)

        TESTE_02_T =  fnc_ajs_df(TESTE_02_T, ['VL'])

        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">A tabela abaixo
                    sumariza os investimentos no período incremental, por TI e para os anos
                    de imobilização e após ajustes de data. Para o ano final,
                    deixamos por meses.
                    </p><br>
                    """) 
        config = {
                    "ANO": st.column_config.TextColumn("ANO Dt_Imob"),
                    "ANO1": st.column_config.TextColumn("Ano Dt_CNTB_AJS"),
                }
        cols = st.columns([1,5,1])    
        with cols[1]:
            st.dataframe(TESTE_02_T, width='content', 
                        hide_index=True, column_config=config)
        
        TESTE_02['ANO'] = TESTE_02['Dt_Imob'].dt.year
        TESTE_02['MES'] = TESTE_02['Dt_Imob'].dt.strftime('%B')
        TESTE_02_P1 = TESTE_02[TESTE_02['ANO'] < TESTE_02['ANO'].max()].copy()
        TESTE_02_P1['MES'] = 'TOTAL'
        TESTE_02_P2 = TESTE_02[TESTE_02['ANO'] == TESTE_02['ANO'].max()].copy()
        TESTE_02_T = pd.concat([TESTE_02_P1, TESTE_02_P2])
        TESTE_02_T = TESTE_02_T.groupby(['ANO', 'MES'])['VL_VNR_UC'].sum().reset_index()

        INCRoe['VL_OE'] = INCRoe['VL_OE'].abs() * FA_OE
        INCRoe['ANO'] = INCRoe['Dt_REF'].dt.year
        INCRoe['MES'] = INCRoe['Dt_REF'].dt.strftime('%B')
        INCRoe_P1 = INCRoe[INCRoe['ANO'] < INCRoe['ANO'].max()].copy()
        INCRoe_P1['MES'] = 'TOTAL'
        INCRoe_P2 = INCRoe[INCRoe['ANO'] == INCRoe['ANO'].max()].copy()
        INCRoe_T = pd.concat([INCRoe_P1, INCRoe_P2])
        INCRoe_T = INCRoe_T.groupby(['ANO', 'MES'])['VL_OE'].sum().reset_index()

        INCRoe_T['MES'] = pd.Categorical(INCRoe_T['MES'], categories=meses, 
                                            ordered=True)
        INCRoe_T = INCRoe_T.sort_values(['ANO', 'MES'])
        INCRoe_T['MES'] = INCRoe_T['MES'].replace(meses_traducao)

        INCRoe_Ta = INCRoe.groupby(['ANO'])['VL_OE'].sum().reset_index()
        INCRoe_Ta['VL_OE'] = INCRoe_Ta['VL_OE'] / 1000000

        TESTE_02_T['MES'] = pd.Categorical(TESTE_02_T['MES'], categories=meses, 
                                            ordered=True)
        TESTE_02_T = TESTE_02_T.sort_values(['ANO', 'MES'])
        TESTE_02_T['MES'] = TESTE_02_T['MES'].replace(meses_traducao)

        TESTE_02_Ta = TESTE_02.groupby(['ANO'])['VL_VNR_UC'].sum().reset_index()
        TESTE_02_Ta['VL_VNR_UC'] = TESTE_02_Ta['VL_VNR_UC'] / 1000000

        TESTE_02_Ta['PROP'] = TESTE_02_Ta['VL_VNR_UC'] / TESTE_02_Ta['VL_VNR_UC'].sum()
        TESTE_02_Ta['PESO'] = ((TESTE_02_Ta['ANO'] - TESTE_02_Ta['ANO'].min()) / 
                                (TESTE_02_Ta['ANO'].max() - TESTE_02_Ta['ANO'].min()))
        FA = np.sum((TESTE_02_Ta['PROP'] - 1 / len(TESTE_02_Ta)) * TESTE_02_Ta['PESO'])

        TESTE_02_Ta = TESTE_02_Ta.merge(INCRoe_Ta, how='left', on =['ANO'])

        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Com base
                    nesses dados podemos montar um gráfico. Também empregaremos
                    um indicador, FA, para observarmos a assimetria dos investimentos.
                    Essa assimetria pode ser decorrente de um investimento concentrado,
                    por exemplo uma SE, mas deve ser avaliado sua pertinência pelo
                    fiscal. 

                    </p><br>
                    """)

        df_long = TESTE_02_Ta.melt(
                                        id_vars='ANO',
                                        value_vars=['VL_VNR_UC', 'VL_OE'],
                                        var_name='Tipo',
                                        value_name='Valor'
                                    )

        fig4 = px.bar(
                        df_long,
                        x='Valor',
                        y='ANO',
                        orientation='h',
                        color='Tipo',
                        text=df_long['Valor'].map(lambda x: f"{x:.2f}"),  # 🔹 duas casas decimais
                        labels={'Valor': 'Valor (Milhões de R$)', 'ANO': 'Ano'},
                        title='Evolução de Investimentos no Ciclo',
                        color_discrete_sequence=px.colors.sequential.Magma
                    )
        fig4.update_traces(
                                texttemplate='%{text}M',
                                textposition='inside',
                                opacity=0.65 
                            )

        fig4.update_layout(
                                xaxis=dict(title='Valor (Milhões de R$)', tickformat=',.2fM'),
                                yaxis=dict(title='Ano'),
                                barmode='overlay',  # 🔸 barras sobrepostas
                                showlegend=True,
                                legend_title_text='Indicador'
                            )

        if FA > 0:
            concentracao = "Concentração no final"
        elif FA < 0:
            concentracao = "Concentração no início"
        else:
            concentracao = "Distribuição uniforme"
        a = f"{FA:.4f}".replace(".",",")
        fig4.add_annotation(
                                x=1,
                                y=-0.3,
                                xref="paper",
                                yref="paper",
                                text=f"FA = {a} ({concentracao})",
                                showarrow=False
                            )

        st.plotly_chart(fig4)
        fig4.update_layout(
                                width=1000, 
                                height=800,
                                autosize=False,
                                margin=dict(l=60, r=20, t=100, b=100),
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.15,
                                    xanchor="center",
                                    x=0.5
                                ),
                                template="plotly_white"
                            )
        fig4.update_annotations(font_size=14)
        fig4.write_image(rf"{local}/RELATORIOS/figuras/distribuicao_investimentos.png", width=1000, height=800, scale=3)
        st.html(r"""
                    <div style="text-align: justify;text-indent: 40px">
                            <p>A fórmula para calcular o indicador é:</p>
                    </div>
                    """)
        st.markdown(r"""
                    $$
                    \scriptsize
                    \begin{aligned}
                        FA = \sum_{i=1}^n \left( P_i - \frac{1}{n} \right) W_i
                    \end{aligned}
                    $$
                    """, unsafe_allow_html = True)
        st.html("""
                    <div style="text-align: justify; text-indent: 40px">
                        <p>Em que:</p>
                        <ul style="padding-left:120;">
                            <li><i>P<sub>i</sub></i> : Proporção do valor no ano <i>i</i>;</li>
                            <li><i>n</i> : número de anos;</li>
                            <li><i>W<sub>i</sub></i> : Peso normalizado do ano <i>i</i>, dado por:</li>
                        </ul>
                        
                    </div>
                    """)
        st.markdown(r"""
                    $$
                    \scriptsize
                    \begin{aligned}
                        W_i = \frac{\text{ANO}_i - \text{ANO}_{\min}}{\text{ANO}_{\max} - \text{ANO}_{\min}}
                    \end{aligned}
                    $$
                    """, unsafe_allow_html = True)
        st.html("""<div style="text-align: justify; text-indent: 40px">
                    <p>Interpretação:</p>
                        <ul style="padding-left:120;">
                            <li><i>FA > 0 </i>: Concentração no final do período.</li>
                            <li><i>FA < 0 </i>: Concentração no início do período.</li>
                            <li>Quanto mais próximo de zero, mais uniforme é a distribuição.</li>
                        </ul>
                    </div>
                    """)

def visualizador_AIS(st = None):
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
    df_CARACT = bsc_ddsTI(f"{local}", st)
    
    st.html(f"""           
                <h3>Observações iniciais</h3>
                <div style="text-align: justify;text-indent: 40px; padding-top: 10px">Base para se 
                executar análise do AIS. Pode-se alterar o arquivo, porém somente será aplicado a 
                versão original para análise do valor empregado no laudo. Sugere-se usar este arquivo 
                como base para modificações e inclusões de análises, para discussões com a fiscalização.<p></p></div>
                <h4> Licença Pública Geral GNU (GPL)</h4>
                <div style="text-align: justify; padding-top: 10px">Versão 3, 29 de junho de 2007<p></p></div>
                <div style="text-align: justify">Copyright (C) 2025, SFF/ANEEL.<p></p></div>
                <div style="text-align: justify;text-indent: 40px; padding-top: 10px">Este é um documento 
                de uso livre: você pode redistribuí-lo ou modificá-lo sob os termos da Licença Pública Geral GNU, 
                conforme publicada pela Free Software Foundation, tanto na versão 3 da Licença, ou qualquer 
                versão posterior. Ele é distribuído na expectativa de que seja útil, mas SEM QUALQUER GARANTIA; 
                sem mesmo a garantia implícita de COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM PROPÓSITO ESPECÍFICO. 
                Consulte a Licença Pública Geral GNU para obter mais detalhes, no sitio 
                <a>http://www.gnu.org/licenses/</a>.<p></p></div>
                <hr></hr>              
                <h3> Normas</h3>
                <a href="https://www.gov.br/aneel/pt-br/centrais-de-conteudos/procedimentos-regulatorios/proret">Visite o sitio da Aneel para mais detalhes!</a>
                <h3> Orientações gerais</h3>
                <br>
                <p style="text-align: justify;text-indent: 40px">
                A análise deve ser conduzida em conformidade com o <b>framework metodológico definido no ROCT</b>, 
                observando seus critérios, procedimentos de validação, regras de consistência e diretrizes para 
                identificação e tratamento de discrepâncias. Algumas visualizações devem ser feitas em conjunto 
                com os artefatos gerados pelos testes. A medida que discutimos, apontaremos quais artefatos.
                <hr></hr>
                <h2 style="text-align: center">Resultados</h2>           
                <hr></hr>              
                """)

    executar_vis(vis_AX001, bd_path, f"{local}/AIS_ANLS", empresa, st)
    executar_vis(vis_AX025, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX002, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX003, bd_path, f"{local}/AIS_ANLS", empresa, st)
    executar_vis(vis_AX004, bd_path, f"{local}/AIS_ANLS", empresa, st)
    executar_vis(vis_AX005, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX006, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX007, bd_path, f"{local}/AIS_ANLS", empresa, st, local, df_CARACT)
    executar_vis(vis_AX008, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX009, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX010, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX011, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX012, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX013, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX014, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX015, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX016, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX017, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX021, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX022, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX023, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX024, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX018, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX019, bd_path, f"{local}/AIS_ANLS", empresa, st, local)
    executar_vis(vis_AX020, bd_path, f"{local}/AIS_ANLS", empresa, st, local)



    
    
    