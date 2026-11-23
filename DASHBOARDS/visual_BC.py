import streamlit as st, numpy as np
from pathlib import Path

from SRC.calculos import conv_num
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
import sqlite3 as sl
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
from htmldocx import HtmlToDocx

def formatar_cnpj(cnpj):
    cnpj = ''.join(filter(str.isalnum, str(cnpj))).upper()

    if len(cnpj) != 14:
        return cnpj

    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

@st.fragment()
def _vis_001(bd_path="", st=None, empresa = "", bd_path2=""):
  
    with sl.connect(bd_path) as bd_EFD:
        tabelas = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", con=bd_EFD)
        tabelas = tabelas['name'].tolist()
        cnpjs = [t.split('_')[-1] for t in tabelas if t.startswith('BLF_G110_')]
        cnpjs = sorted(set(cnpjs))

        for i, cnpj in enumerate(cnpjs):
            nome = "NI"
            if existe_tabela(f"BL_Z", bd_EFD):
                sSQL = f'SELECT "6" AS Nome FROM BL_Z WHERE "7" = "{cnpj}" LIMIT 1'
                df_NM = carga_sqlite_cache(sSQL, bd_EFD)
                nome = df_NM.iloc[0]['Nome'] if not df_NM.empty else 'NI'

            if existe_tabela(f"BLF_G126_{cnpj}", bd_EFD):
                sSQL = f"SELECT * FROM BLF_G126_{cnpj}"
                BL_G126 = carga_sqlite_cache(sSQL, bd_EFD)
            else:
                BL_G126 = pd.DataFrame()
            sSQL = f"SELECT * FROM tbl_icms_fin_{cnpj}"
            df = carga_sqlite_cache(sSQL, bd_EFD)
            sSQL = f"SELECT * FROM BLF_G110_{cnpj}"
            BL_G110 = carga_sqlite_cache(sSQL, bd_EFD)
            sSQL = f"SELECT * FROM BLF_G125_{cnpj}"
            BL_G125 = carga_sqlite_cache(sSQL, bd_EFD)
            sSQL = f"SELECT * FROM BLF_G125cmp_{cnpj}"
            BL_G125cmp1 = carga_sqlite_cache(sSQL, bd_EFD)
            sSQL = f"SELECT * FROM BLF_UN_{cnpj}"
            BL_UN = carga_sqlite_cache(sSQL, bd_EFD)

            st.html(f"""<h3>Resultado das análises do ICMS para {nome}, CNPJ {formatar_cnpj(cnpj)}</h3>
                        <hr></hr>
                        <div style="text-align: justify; text-indent: 40px;">Apresenta-se o resultado do cálculo 
                        financeiro relacionado ao ICMS, global, com base nos dados  fornecidos e na metodologia aplicada. 
                        Abaixo estão descritos os resultados obtidos e os argumentos que justificam o processo 
                        utilizado.
                        </div>""")

            WACC_POND = f"{df[df['Item']=='WACC Ponderado (%)'].iloc[-1,-1]/100:.2%}".replace(".",",")
            WACC_MES = f"{df[df['Item']=='i (%)'].iloc[-1,-1]/100:.2%}".replace(".",",")
            VL_ICMS_CRED = f"{df[df['Item']=='Cicms(R) (R$)'].iloc[-1,-1]:,.2f}".replace(".","#").replace(",",".").replace("#",",")
            VL_ICMS_NCRED = f"{df[df['Item']=='Cicms(NR) (R$)'].iloc[-1,-1]:,.2f}".replace(".","#").replace(",",".").replace("#",",")
            VL_VP = f"{df[df['Item']=='VP (R$)'].iloc[-1,-1]:,.2f}".replace(".","#").replace(",",".").replace("#",",")
            
            st.html(f"""
                        <div style="text-align: justify; padding-left: 60px;">
                            <b>WACC<sub>POND</sub> (WACC Ponderado):</b> O Weighted Average Cost of Capital (WACC) ponderado representa a taxa de desconto aplicada com base nos custos ponderados de capital. Este valor foi calculado considerando a estrutura de financiamento da empresa e as taxas aplicáveis.
                            <b>Foi obtido {WACC_POND} para a {empresa} ({formatar_cnpj(cnpj)})</b>.
                        </div>

                        <div style="text-align: justify; padding-left: 60px;">
                        <b>WACC<sub>MES</sub> (WACC por Mês):</b> O WACC mensal foi derivado da taxa anualizada, ajustada para períodos mensais, e aplicada no cálculo dos fluxos de caixa futuros associados aos créditos de ICMS.
                        <b>Foi obtido {WACC_MES} para a {empresa} ({formatar_cnpj(cnpj)})</b>.
                        </div>

                        <div style="text-align: justify; padding-left: 60px;">
                            <b>VL<sub>ICMS_CRED</sub> (Valor dos Créditos de ICMS):</b> Este valor representa o montante total de créditos de ICMS que foram reconhecidos como recuperáveis. O cálculo foi baseado no EFD ICMS, nas notas fiscais e na legislação vigente sobre a recuperação de créditos tributários.
                            <b>Foi obtido R$ {VL_ICMS_CRED} para a {empresa} ({formatar_cnpj(cnpj)})</b>.
                        </div>

                        <div style="text-align: justify; padding-left: 60px;">
                            <b>VL<sub>ICMS_NCRED</sub> (Valor do ICMS Não Creditado):</b> O ICMS não creditado inclui valores que, por restrições legais ou documentais, não puderam ser considerados no cálculo de recuperação de crédito. Este montante também foi considerado no cálculo financeiro global.
                            <b>Foi obtido R$ {VL_ICMS_NCRED} para a {empresa} ({formatar_cnpj(cnpj)})</b>.
                        </div>

                        <div style="text-align: justify; padding-left: 60px;">
                            <b>VP (Valor Presente do ICMS):</b> O valor presente inclui:
                            <ul style = "padding-left:80px;">
                                <li>Os créditos de ICMS recuperáveis (VL<sub>ICMS_CRED</sub>).</li>
                                <li>Os valores não creditados (VL<sub>ICMS_NCRED</sub>).</li>
                                <li>A remuneração aplicada devido ao período de recuperação dos créditos.</li>
                            </ul>
                            O cálculo do VP foi realizado utilizando o WACC mensal como taxa de desconto, obtendo <b>R$ {VL_VP} para a {empresa}</b>.
                        </div>
                        """)

            st.html("""<div style="text-align: justify; text-indent: 40px; padding-top: 5px; padding-botton: 20px;">
                        A seguir temos a matriz demonstrando os passos de cálculo.<br><br>
                        </div>""")

            BL_G110F = BL_G125cmp1.copy()
            
            for n in ['VL_TRIB_EXP', 'VL_TOTAL', 'VL_ICMS_COMPRA_ATIVO', 'VL_DIFAL_COMPRA_ATIVO',
                    'VL_SUBST_TRIB', 'COEF_CRED_EST', 'VL_CRED_ICMS', 'Tx_WACC', 'VL_SALDO_AMT',
                    'VL_SALDO_RED', 'VL_SALDO_ACUMULADO', 'VL_ICMS_CREDIT', 'VL_ICMS_CRED',
                    'VL_ICMS_NCRED']:
                if n == 'Tx_WACC':
                    BL_G110F[n] = BL_G110F[n].apply(lambda x: f"{x:.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                else:
                    BL_G110F[n] = BL_G110F[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
            config = {
                    "REG": st.column_config.TextColumn("Bloco do SPED ICMS"),
                    "DT_INI": st.column_config.DateColumn("Data de Início", format="DD/MM/YYYY"),
                    "DT_FIM": st.column_config.DateColumn("Data de Fim", format="DD/MM/YYYY"),
                }
            st.dataframe(BL_G110F, use_container_width=True, hide_index=True,  column_config=config)
        st.divider()


        with sl.connect(bd_path2) as bd:
            if existe_tabela("IND_PER_SAI_CIAP",bd):
                sSQL = """
                            SELECT 
                                    DT_DOC_CIAP, IND_PER_SAI_CIAP, FLG_OUTLIER
                            FROM IND_PER_SAI_CIAP
                        """
                IND_PER_SAI_CIAP = pd.read_sql(sSQL, bd, parse_dates=['DT_DOC_CIAP'])
                st.html(f"""<h3>Análise do fator de recuperação de ICMS para a concessionária {nome}</h3>
                            <hr></hr>
                            """)
                st.html(f"""
                            <p  style="text-align: justify;text-indent: 40px">Abaixo, temos o fator de recuperação por mês. Também, há 
                        indicação dos meses atípicos, para discutir com a concessionária.</p>
                            """)
                IND_PER_SAI_CIAP['FLG_OUTLIER_LABEL'] = IND_PER_SAI_CIAP['FLG_OUTLIER'].map({
                                                                    0: 'Não outlier',
                                                                    1: 'Outlier'
                                                                })
                q1 = IND_PER_SAI_CIAP['IND_PER_SAI_CIAP'].quantile(0.25)
                q3 = IND_PER_SAI_CIAP['IND_PER_SAI_CIAP'].quantile(0.75)
                iqr = q3 - q1

                lim_inf = q1 - 1.5 * iqr
                lim_sup = q3 + 1.5 * iqr

                media = IND_PER_SAI_CIAP['IND_PER_SAI_CIAP'].mean()
                desvio = IND_PER_SAI_CIAP['IND_PER_SAI_CIAP'].std()
                cv = desvio / media if pd.notna(media) and media != 0 else None

                fig = px.scatter(
                                        IND_PER_SAI_CIAP,
                                        x='DT_DOC_CIAP',
                                        y='IND_PER_SAI_CIAP',
                                        color='FLG_OUTLIER_LABEL',
                                        color_discrete_map={
                                            'Não outlier': '#A9B8C9',
                                            'Outlier': '#E76F51'
                                        },
                                        opacity=0.75,
                                        title='Outliers vs Dados Normais',
                                        hover_data=['FLG_OUTLIER']
                                    )
                fig.add_shape(
                                type="rect",
                                xref="paper",   
                                yref="y",
                                x0=0,
                                x1=1,
                                y0=lim_inf,
                                y1=lim_sup,
                                fillcolor="rgba(42, 157, 143, 0.16)", 
                                line=dict(width=0),
                                layer="below"
                            )

                fig.update_traces(
                                    selector=dict(name='True'),
                                    marker=dict(size=9, opacity=1)
                                )

                fig.update_layout(
                                    template='plotly_white',
                                    legend_title='Outlier',
                                    xaxis_title='Data',
                                    yaxis_title='Fator de recuperação',
                                    margin=dict(l=20, r=20, t=40, b=20)
                                )
                
                fig.update_yaxes(range=[min(0,lim_inf*1.1), max(1,lim_sup*1.1)], title='Fator de recuperação', gridcolor='rgba(180,180,180,0.18)')
                fig.update_xaxes(title='Data', gridcolor='rgba(180,180,180,0.10)')
                texto_cv = f'CV = {cv:.2%}'.replace(".",",") if cv is not None else 'CV = NA'
                fig.add_annotation(
                                        x=0.01,
                                        y=0.99,
                                        xref='paper',
                                        yref='paper',
                                        text=texto_cv,
                                        showarrow=False,
                                        align='left',
                                        bgcolor='rgba(255,255,255,0.85)',
                                        bordercolor='lightgray',
                                        borderwidth=1
                                    )
                colsA = st.columns([2,10,1], gap='small')
                with colsA[1]:
                    st.plotly_chart(fig, width='content')

                st.html(f"""
                            <p  style="text-align: justify;text-indent: 40px">Os dados tabulares são apresentados a seguir.</p>
                            """)
                
                for n in IND_PER_SAI_CIAP.columns.to_list():
                    if n[:2].upper() == 'VL':
                        if not (IND_PER_SAI_CIAP[n].dtype == 'object'):
                            IND_PER_SAI_CIAP[n] = IND_PER_SAI_CIAP[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    if n[:3].upper() == 'IND':
                        if not (IND_PER_SAI_CIAP[n].dtype == 'object'):
                            IND_PER_SAI_CIAP[n] = IND_PER_SAI_CIAP[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                    if n[:2].upper() == 'DT':
                        if not (IND_PER_SAI_CIAP[n].dtype == 'object'):
                            IND_PER_SAI_CIAP[n] = pd.to_datetime(IND_PER_SAI_CIAP[n]).dt.strftime('%d/%m/%Y')

                st.dataframe(IND_PER_SAI_CIAP, width='stretch', hide_index=True)
                st.download_button(label="📥 Baixar CSV",
                                   data=IND_PER_SAI_CIAP.to_csv(index=False, sep="|", decimal=",").encode("latin-1"),
                                   file_name="fator_ciap.csv",
                                    mime="text/csv",
                                    key=f"{cnpj}_chv"
                                  )

@st.fragment()
def _vis_002(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path2) as bd:
        if not existe_tabela('BP_EC_AVALc', bd):
            return
        if not existe_tabela('tbl_resumo_compras', bd):
            sSQL = """
                    SELECT 
                        COD_ITEM,
                        Dt_NF,
                        NUM_DOC,
                        SUM(COALESCE(QTD,0)) AS QTD,
                        SUM(
                                COALESCE(VL_TOT_LIQ, 0) + 
                                COALESCE(VL_TOT_ICMS, 0) + 
                                COALESCE(VL_TOT_IPI, 0) + 
                                COALESCE(VL_DIFAL, 0) + 
                                COALESCE(VL_ST, 0)
                            ) AS VL_ITEM_CONSOLIDADO
                    FROM BP_EC_AVALc
                    WHERE COD_ITEM IS NOT NULL AND Cd_NG_EC = 1
                    GROUP BY COD_ITEM, NUM_DOC, Dt_NF
                """
            BP_EC = carga_sqlite_cache(sSQL, bd)
            BP_EC.to_sql('tbl_resumo_compras', bd, if_exists='replace', index=False)
        else:
            BP_EC = carga_sqlite_cache("SELECT * FROM tbl_resumo_compras", bd)
        
        st.html(f"""<h3>Compras para {empresa}</h3>
                    <hr></hr>
                    """)

        BP_EC['Dt_NF'] = pd.to_datetime(BP_EC['Dt_NF'], errors='coerce')
        BP_EC = BP_EC.groupby(by=['NUM_DOC','Dt_NF'])["VL_ITEM_CONSOLIDADO"].sum().reset_index()
        p50 = BP_EC["VL_ITEM_CONSOLIDADO"].median()
        p90 = BP_EC["VL_ITEM_CONSOLIDADO"].quantile(0.90)
        p99 = BP_EC["VL_ITEM_CONSOLIDADO"].quantile(0.99)

        BP_EC["Risco"] = BP_EC["VL_ITEM_CONSOLIDADO"].apply(
                                                                lambda x: "Exceção (≥ P99)" if x >= p99 else "Padrão"
                                                            )

        mediana_mensal = (
                            BP_EC
                            .set_index("Dt_NF")
                            .resample("M")["VL_ITEM_CONSOLIDADO"]
                            .median()
                            .reset_index()
                        )
        
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Abaixo, temos a relação entre o tempo e o valor 
                    dos itens adquiridos, tratados como UC/UAR, com base nas datas de emissão das notas fiscais. Cada observação corresponde 
                    a um item de compra individual, permitindo avaliar a distribuição temporal dos gastos e a variabilidade 
                    dos valores praticados. A aplicação de escala logarítmica no eixo vertical reduz o efeito de assimetria 
                    da distribuição e viabiliza a análise conjunta de itens de baixo e alto valor, característica comum em 
                    dados de compras. Os histogramas marginais evidenciam a densidade de ocorrências tanto ao longo do tempo 
                    quanto por faixa de valor.</p>
                    """)
        fig = px.scatter(
                            BP_EC,
                            x="Dt_NF",
                            y="VL_ITEM_CONSOLIDADO",
                            color="Risco",
                            color_discrete_map={
                                "Padrão": "#9aa0a6",
                                "Exceção (≥ P99)": "#fef603"
                            },
                            opacity=0.15,
                            log_y=True,
                            height=450,
                            labels={
                                "Dt_NF": "Data da NFe",
                                "VL_ITEM_CONSOLIDADO": "Valor do Item (Escala Log)"
                            },
                            title=(
                                "Distribuição Temporal dos Valores de Itens Adquiridos"
                            )
                        )
        
        fig.add_scatter(
                            x=mediana_mensal["Dt_NF"],
                            y=mediana_mensal["VL_ITEM_CONSOLIDADO"],
                            mode="lines",
                            name="Mediana Mensal",
                            line=dict(color="#000000", width=4)
                        )

        fig.add_hline(y=p50, line_dash="dot", line_color="blue", annotation_text="Mediana")
        fig.add_hline(y=p90, line_dash="dash", line_color="orange", annotation_text="P90")
        fig.add_hline(y=p99, line_dash="solid", line_color="red", annotation_text="P95 (Exceção)")

        fig.update_layout(
                                legend_title="Classificação de Risco",
                                xaxis_tickformat="%m/%Y",
                                title_x=0.5
                            )

        BP_EC["AnoMes"] = BP_EC["Dt_NF"].dt.to_period("M").astype(str)

        fig_dist_tempo = px.box(
                                    BP_EC,
                                    x="AnoMes",
                                    y="VL_ITEM_CONSOLIDADO",
                                    log_y=True,
                                    points="outliers",
                                    height=300,
                                    labels={
                                        "AnoMes": "Período (Ano-Mês)",
                                        "VL_ITEM_CONSOLIDADO": "Valor NFe (escala log)"
                                    },
                                    title=(
                                        "Distribuição dos Valores por NFe ao Longo do Tempo"
                                    )
                                )

        fig_dist_tempo.update_layout(
                                        xaxis_tickangle=45,
                                        title_x=0.5
                                    )
        valor_por_mes = (
                            BP_EC
                            .groupby(BP_EC["Dt_NF"].dt.to_period("M"))["VL_ITEM_CONSOLIDADO"]
                            .sum()
                        )
        cv_valor = valor_por_mes.std() / valor_por_mes.mean()
        df_valor_mes = valor_por_mes.reset_index()
        df_valor_mes.columns = ["Periodo", "Valor"]
        df_valor_mes["Periodo"] = df_valor_mes["Periodo"].astype(str)

        figa = px.bar(
                        df_valor_mes,
                        x="Periodo",
                        y="Valor",
                        title="Valor Total de Compras por Período"
                    )
        
        _, kpi1, _, kpi2, _, kpi3, _ = st.columns([1,5,1,5,1,2,1], gap='small')
        _, kpi4, _, kpi5, _ = st.columns([1,5,1,5,4], gap='small')
        kpi1.metric(
                        "Total das Compras",
                        f"R$ {BP_EC['VL_ITEM_CONSOLIDADO'].sum():,.2f}".replace(".", "x").replace(",", ".").replace("x", ",")
                    )

        kpi2.metric(
                        "Maior Nota",
                        f"R$ {BP_EC['VL_ITEM_CONSOLIDADO'].max():,.2f}".replace(".", "x").replace(",", ".").replace("x", ",")
                    )

        kpi3.metric("CV", f"{cv_valor:,.2f}".replace(".", "x").replace(",", ".").replace("x", ","))

        kpi4.metric(
                        "Média Mensal",
                        f"R$ {valor_por_mes.mean():,.2f}".replace(".", "x").replace(",", ".").replace("x", ",")
                    )

        kpi5.metric(
                        "Desvio Padrão Mensal",
                        f"R$ {valor_por_mes.std():,.2f}".replace(".", "x").replace(",", ".").replace("x", ",")
                    )

        col_left, col_main, col_right = st.columns([1, 15, 1])
        with col_main:
            with st.container(border=True):
                st.plotly_chart(fig, width="stretch")

            with st.container(border=True):
                st.plotly_chart(fig_dist_tempo, width="stretch")

            with st.container(border=True):
                st.plotly_chart(figa, width="stretch")

            with st.container(border=True):
                st.html(f"""
                            <p  style="text-align: justify;text-indent: 40px">Segue os dados brutos do gráfico. Há 
                        {(BP_EC["VL_ITEM_CONSOLIDADO"] >= p99).sum()} NFe com valores mais elevados de um total de 
                        {len(BP_EC)} NFe.</p>
                        """)
                colu = st.columns([1,6,1], gap="large")
                with colu[1]:
                    BP_EC = BP_EC.sort_values(by='VL_ITEM_CONSOLIDADO', ascending=False)
                    for n in BP_EC.columns.to_list():
                        if n[:2].upper() == 'VL':
                            if not (BP_EC[n].dtype == 'object'):
                                BP_EC[n] = BP_EC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

                    st.dataframe(BP_EC, width='stretch', hide_index=True)
                    st.download_button(label="📥 Baixar CSV",
                                   data=BP_EC.to_csv(index=False, sep="|", decimal=",").encode("utf-8"),
                                   file_name="dados_compras.csv",
                                    mime="text/csv",
                                    key=f"compras_chv"
                                  )

@st.fragment()
def _vis_003(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path2) as bd:
        if not existe_tabela('CONSOL_TOT_QTD_FISICO', bd):
            return
        dt_ARQ = max_arq("LST_MAT", bd, empresa)
        if dt_ARQ:
            st.html(f"""<h2>Destino dos materiais</h2>
                        <p  style="text-align: justify;text-indent: 40px">A análise dos materiais distribuídos entre diferentes 
                        categorias, função de sua aplicação, apresenta visão do emprego das compras observadas. A síntese proposta 
                        busca consolidar quantitativamente os materiais alocados em quatro perspectivas: ativo imobilizado (bens já 
                        incorporados ao patrimônio e em operação), ativo imobilizado em curso (bens em processo de implantação ou 
                        construção), estoque (materiais disponíveis para uso imediato) e obras de manutenção (materiais aplicados 
                        em intervenções corretivas ou preventivas que não são unitizáveis). Esta abordagem permite avaliar o fluxo dos 
                        materiais, além da contabilização patrimonial, proporcionando uma descrição do fluxo de utilização dos recursos 
                        materiais, bem como fluxo financeiro associado, apresentando um reflexo dos gastos com a disponibilidade operacional 
                        e a aplicação de recursos na sustentação da infraestrutura existente.</p>
                        """)
            
            sSQL = """
                        SELECT 
                            t1.COD_ITEM, COALESCE(t2.DESCR_ITEM,'AUSENTE EM LST_MAT') AS DESCR_ITEM, 
                            t1.Cd_Unid, t1.QTD_ROA, t1.QTD_ROA_CURSO, 
                            t1.IND_DESTINO_ODI_CURSO_IMOB, t1.QTD_AO, t1.IND_DESTINO_ODI_ESTOQUE, 
                            t1.QTD_MAN, t1.IND_DESTINO_ODI_ODS, t1.QTD
                        FROM 
                                CONSOL_TOT_QTD_FISICO t1 LEFT JOIN (SELECT COD_ITEM, DESCR_ITEM FROM
                                LST_MAT WHERE dt_ARQ = ?) t2 
                        ON 
                                t1.COD_ITEM = t2.COD_ITEM
                        
                    """
            ANL_LST_TUC = pd.read_sql(sSQL, bd, params=(dt_ARQ,))
            ANL_LST_TUC[['QTD_ROA','QTD_ROA_CURSO','QTD_AO',
                                    'QTD_MAN','QTD']] = ANL_LST_TUC[['QTD_ROA','QTD_ROA_CURSO','QTD_AO',
                                    'QTD_MAN','QTD']].fillna(0)
            crit = ANL_LST_TUC['QTD_MAN'].abs() < 0.1
            ANL_LST_TUC.loc[crit, 'IND_USO'] = "Somente " + ANL_LST_TUC.loc[crit, 'IND_DESTINO_ODI_ESTOQUE']
            ANL_LST_TUC.loc[~crit, 'IND_USO'] = ANL_LST_TUC.loc[~crit, 'IND_DESTINO_ODI_ESTOQUE'] + " e Manutenção"
            for n in ANL_LST_TUC.columns:
                if n[:2].upper() in ['VL','QT']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].fillna(0)
                    if not (ANL_LST_TUC[n].dtype == 'object'):
                        ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            st.dataframe(ANL_LST_TUC[['DESCR_ITEM','COD_ITEM','Cd_Unid','QTD_ROA','QTD_ROA_CURSO','QTD_AO',
                                    'QTD_MAN','QTD','IND_USO']], width='stretch', hide_index=True)

@st.fragment()
def _vis_004(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path2) as bd:
        if not existe_tabela('TBL_MAT_ATIVOS_SPED', bd):
            return

        dt_ARQ = max_arq("LST_MAT", bd, empresa)
        if dt_ARQ:
            st.html(f"""<h2>Materiais com DE-PARA entre EFD e ERP</h2>
                        <p  style="text-align: justify;text-indent: 40px">A tabela a seguir apresenta o resultado da
                        conciliação entre ativos do EFD e do ERP, pelo COD_ITEM. Quando conciliado preenchemos a natureza
                        de gasto.</p>
                        """)
            sSQL = """
                        SELECT 
                            t1.COD_ITEM, COALESCE(t2.DESCR_ITEM,'AUSENTE EM LST_MAT') AS DESCR_ITEM, 
                            t1.COD_ITEM_SPD, 
                            t1.Cd_NG
                        FROM 
                                TBL_MAT_ATIVOS_SPED t1 LEFT JOIN (SELECT COD_ITEM, DESCR_ITEM FROM
                                LST_MAT WHERE dt_ARQ = ?) t2 
                        ON 
                                t1.COD_ITEM = t2.COD_ITEM
                        
                    """
            ANL_LST_TUC = pd.read_sql(sSQL, bd, params=(dt_ARQ,))
            st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True)

@st.fragment()
def _vis_005(bd_path="", st=None, empresa = "", bd_path2="", local="", apr2=False):
    with sl.connect(bd_path2) as bd:
        if not existe_tabela('LST_NFe_CONC', bd):
            return

        st.html(f"""<h2>Validação das Compras entre EFD e ERP e apropriação de Créditos Fiscais</h2>
                <p  style="text-align: justify;text-indent: 40px">O processo de conciliação entre ERP e EFD ICMS por Nota Fiscal 
                Eletrônica (NFE) consiste em uma análise comparativa que confronta os registros contábeis declarados pela Empresa,
                conforme Manual de Dados e extraídos do ERP com os dados declarados na EFD ICMS, utilizando como elemento de 
                reconciliação a chave da NFE. Esta conciliação opera em duas dimensões críticas: o valor fiscal (base de cálculo 
                do ICMS, valor da mercadoria e impostos incidentes) e a quantidade global dos itens transacionados, assegurando 
                que as informações declaradas na base contábil estejam refletindo a fiscal. A importância desta prática reside 
                na verificação automatizada da apropriação dos créditos fiscais recuperáveis, uma vez que discrepâncias podem 
                gerar diferenças no custo médio do equipamento. Adicionalmente, podemos avaliar falhas nos processos de lançamento, 
                inconsistências na integração entre sistemas e possíveis erros de digitação, funcionando como controle  
                que assegura a conformidade regulatória, com base na perspectiva fiscal. A seguir apresentamos o resultado:</p>
                """)
        sSQL = """SELECT * FROM LST_NFe_CONC"""
        LST_NFe_CONC = pd.read_sql(sSQL, bd)
        LST_NFe_CONC = LST_NFe_CONC.fillna(0)
        crit_NFe = LST_NFe_CONC['CHV_NFE']!=0
        crit_QTD = LST_NFe_CONC['TST_GLB_QTD']=="OK"
        crit_VL = LST_NFe_CONC['TST_GLB_VL']=="OK"
        crit_GL = LST_NFe_CONC['TST_GLB']=="OK"
        Nr_NFe = f"{len(LST_NFe_CONC[crit_NFe]):,.0f}".replace(",",".")
        Nr_NFe_nCONC_QTD = f"{len(LST_NFe_CONC[crit_NFe & ~crit_QTD]):,.0f}".replace(",",".")
        Nr_NFe_nCONC_VL = f"{len(LST_NFe_CONC[crit_NFe & ~crit_VL]):,.0f}".replace(",",".")
        Nr_NFe_CONC_GL = f"{len(LST_NFe_CONC[crit_NFe & crit_GL]):,.0f}".replace(",",".")

        crit_IT1 = crit_NFe & crit_QTD
        VL_NFe_CONC_QTD = (f"{max(LST_NFe_CONC[crit_IT1]['VL_ERP_TOT'].sum(),LST_NFe_CONC[crit_IT1]['VL_EFD_TOT'].sum()):,.2f}"
                           .replace(".","x")
                           .replace(",",".")
                           .replace("x",","))
        crit_IT2 = crit_NFe & crit_VL
        VL_NFe_CONC_VL = (f"{max(LST_NFe_CONC[crit_IT2]['VL_ERP_TOT'].sum(),LST_NFe_CONC[crit_IT2]['VL_EFD_TOT'].sum()):,.2f}"
                          .replace(".","x")
                          .replace(",",".")
                          .replace("x",","))
        crit_IT3 = crit_NFe & crit_GL
        VL_NFe_CONC_GL = (f"{max(LST_NFe_CONC[crit_IT3]['VL_ERP_TOT'].sum(),LST_NFe_CONC[crit_IT3]['VL_EFD_TOT'].sum()):,.2f}"
                          .replace(".","x")
                          .replace(",",".")
                          .replace("x",","))
        VL_NFe = (f"{max(LST_NFe_CONC['VL_ERP_TOT'].sum() * 0,LST_NFe_CONC['VL_EFD_TOT'].sum()):,.2f}"
                  .replace(".","x")
                  .replace(",",".")
                  .replace("x",","))
        crit_IT4 = (LST_NFe_CONC['VL_ERP_TOT'].abs() < 0.1) | LST_NFe_CONC['VL_ERP_TOT'].isnull()
        VL_NFe_nCONC_ausERP = (f"{LST_NFe_CONC[crit_IT4]['VL_EFD_TOT'].sum():,.2f}"
                          .replace(".","x")
                          .replace(",",".")
                          .replace("x",","))
        PCT = (f"{max(LST_NFe_CONC[crit_IT3]['VL_ERP_TOT'].sum(),LST_NFe_CONC[crit_IT3]['VL_EFD_TOT'].sum()) / max(LST_NFe_CONC['VL_ERP_TOT'].sum() * 0,LST_NFe_CONC['VL_EFD_TOT'].sum()):,.2%}"
                            .replace(".","x")
                            .replace(",",".")
                            .replace("x",","))
        PCT_EFD = (f"{LST_NFe_CONC[crit_IT4]['VL_EFD_TOT'].sum() / max(LST_NFe_CONC['VL_ERP_TOT'].sum(),LST_NFe_CONC['VL_EFD_TOT'].sum()):,.2%}"
                            .replace(".","x")
                            .replace(",",".")
                            .replace("x",","))
        vl_ctr = (LST_NFe_CONC[crit_IT4]['VL_EFD_TOT'].sum() / 
                  max(LST_NFe_CONC[~crit_IT3]['VL_ERP_TOT'].sum(),LST_NFe_CONC[~crit_IT3]['VL_EFD_TOT'].sum()))
        PCT_PART_ERRO = (f"""{vl_ctr:,.2%}"""
                            .replace(".","x")
                            .replace(",",".")
                            .replace("x",","))
        vl_total = max(LST_NFe_CONC['VL_ERP_TOT'].sum() * 0,LST_NFe_CONC['VL_EFD_TOT'].sum())
        vl_conc = max(LST_NFe_CONC[crit_IT3]['VL_ERP_TOT'].sum(),LST_NFe_CONC[crit_IT3]['VL_EFD_TOT'].sum())
        DELTA = (vl_total - vl_conc)
        if vl_ctr <=0.1:
            txt_ctr = " Ausências que representem até 10% do valor total conciliado representam operações de baixo valor " \
            "unitário ou eventuais atrasos no processamento."
        else:
            txt_ctr = " Ausências que representam operações " \
            "com diferenças significativas e que devem ser detalhadas."
        dic_map = {}
        lst_impr = []
        for n in LST_NFe_CONC.columns:
            if n not in ['_merge']:
                dic_map[n] = n.upper()
                lst_impr.append(dic_map[n])
            if n[:2].upper() in ['VL','QT']:
                LST_NFe_CONC[n] = LST_NFe_CONC[n].fillna(0)
                if not (LST_NFe_CONC[n].dtype == 'object'):
                    LST_NFe_CONC[n] = LST_NFe_CONC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        LST_NFe_CONC = LST_NFe_CONC.rename(columns=dic_map)
        st.dataframe(LST_NFe_CONC[lst_impr], width='stretch', hide_index=True)
        LST_NFe_CONC.to_csv(rf"{local}/BP_ANLS/saida_conciliacao_NFE.csv", index=False, encoding='latin-1', sep = "|")
        
        dt_ARQ = max_arq("BP_EC", bd, empresa)
        if dt_ARQ:
            sSQL = """SELECT Cd_NG, Cd_CFOP, Cd_NFe, VL_TOT_ICMS, VL_TOT_IPI, VL_TOT_LIQ,
                             VL_DIFAL, VL_ST FROM BP_EC"""
            BP = pd.read_sql(sSQL, bd)
            for n in BP.columns:
                if n[:2].upper() in ['VL','QT']:
                    BP[n] = BP[n].fillna('0')
                    if (BP[n].dtype == 'object'):
                        BP[n] = pd.to_numeric(BP[n].str.replace(",","."), errors='coerce')
            crit = BP['Cd_NFe'].isnull()
            BP['VL_TOT'] = (BP['VL_TOT_ICMS'].fillna(0) + 
                            BP['VL_TOT_IPI'].fillna(0) + 
                            BP['VL_TOT_LIQ'].fillna(0) +
                            BP['VL_DIFAL'].fillna(0) )
            if crit.sum() > 0:
                pct = crit.sum() / len(BP)
                if pct < 0.1:
                    txt = ""
                elif pct < 0.6:
                    txt = ", valor considerado alto, empresa deve justificar"
                else:
                    txt = ", percentual inadimissível, empresa deve justificar"
                pct_txt = f"{pct:,.2%}".replace(",",'X').replace(".",',').replace("x",',')
                st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">Foram encontrados {crit.sum()} itens sem código de nota 
                fiscal associado, no extrato de compras. Representa {pct_txt} dos lançamentos{txt}.
                </p>
                """)
            BP_ANLS = BP[crit].groupby(['Cd_CFOP'], dropna=False)[['VL_TOT']].sum().reset_index()
            df1 = BP[~crit].groupby(['Cd_CFOP'], dropna=False)[['VL_TOT']].sum().reset_index()
            df1['Cd_CFOP'] = df1['Cd_CFOP'].astype(str)
            BP_ANLS['Cd_CFOP'] = BP_ANLS['Cd_CFOP'].astype(str)

            BP_ANLS = BP_ANLS.merge(df1, how='outer', on = 'Cd_CFOP', suffixes=("_sem_CHV", "_com_CHV"), indicator=True)

            map_res = {
                    'both' : 'CFOP presente em ambos',
                    'left_only' : 'Somente em itens sem código da chave',
                    'right_only' : 'Somente em itens com código da chave',
                        }
            BP_ANLS['IND_CONC'] = BP_ANLS['_merge'].replace(map_res)
            BP_ANLS = BP_ANLS.drop(columns='_merge')
            BP_ANLS['VL_TOT_sem_CHV'] = BP_ANLS['VL_TOT_sem_CHV'].fillna(0)
            BP_ANLS['VL_TOT_com_CHV'] = BP_ANLS['VL_TOT_com_CHV'].fillna(0)
            introito = """
                            <div style="
                                margin-bottom: 18px;
                                padding: 14px;
                                background-color: #f8f9fa;
                                border-left: 5px solid #d9534f;
                                border-radius: 6px;
                                font-family: Arial;
                                font-size: 15px;
                                line-height: 1.6;
                                color: #333;
                            ">
                                <b>Análise de CFOP:</b><br><br>

                                A tabela abaixo apresenta os valores consolidados por CFOP, contemplando os
                                montantes calculados com e sem chave da NFe, bem como o indicador de
                                CFOP por chave. As linhas destacadas em vermelho representam
                                operações classificadas como <b>CFOP_INV = 1</b>, indicando CFOP considerados
                                como de investimento.
                            </div>
                            """

            st.html(introito)
            BP_ANLS['CFOP_INV'] = 0
            BP_ANLS.loc[
                            BP_ANLS['Cd_CFOP'].astype(str).str[1:].str.contains(r'406|551|553|555', na=False),
                            'CFOP_INV'
                        ] = 1

            BP_ANLS.to_csv(rf"{local}/BP_ANLS/resultado_nfe_cfop.csv", index=False, encoding='latin-1', sep = "|")
            cols = ["Cd_CFOP", "VL_TOT_sem_CHV", "VL_TOT_com_CHV", "IND_CONC", "CFOP_INV"]

            html = """
                        <table style="
                            border-collapse: collapse;
                            width: 100%;
                            font-family: Arial;
                        ">
                            <thead>
                                <tr style="background-color:#f0f0f0;">
                        """

            for col in cols:
                html += f"""
                    <th style="
                        border:1px solid #ccc;
                        padding:8px;
                        text-align:center;
                    ">
                        {col}
                    </th>
                """

            html += "</tr></thead><tbody>"

            for _, row in BP_ANLS[cols].iterrows():

                destaque = (
                                "background-color:#ffcccc; font-weight:bold;"
                                if row["CFOP_INV"] == 1
                                else ""
                            )

                html += f'<tr style="{destaque}">'

                html += f"""
                    <td style="border:1px solid #ccc;padding:6px;text-align:center;">
                        {row["Cd_CFOP"]}
                    </td>

                    <td style="border:1px solid #ccc;padding:6px;text-align:right;">
                        {row["VL_TOT_sem_CHV"]:,.2f}
                    </td>

                    <td style="border:1px solid #ccc;padding:6px;text-align:right;">
                        {row["VL_TOT_com_CHV"]:,.2f}
                    </td>

                    <td style="border:1px solid #ccc;padding:6px;text-align:center;">
                        {row["IND_CONC"]}
                    </td>

                    <td style="border:1px solid #ccc;padding:6px;text-align:center;">
                        {row["CFOP_INV"]}
                    </td>
                """

                html += "</tr>"

            html += "</tbody></table>"

            st.html(html)

        sSQL = """SELECT * FROM TBL_BP_EC_CONC"""
        TBL_BP_EC_CONC = carga_sqlite_cache(sSQL, bd)

        for n in TBL_BP_EC_CONC.columns:
            if n[:2].upper() in ['VL','QT']:
                TBL_BP_EC_CONC[n] = pd.to_numeric(TBL_BP_EC_CONC[n].astype(str).fillna("0.0"), errors='coerce')

        dds_df = TBL_BP_EC_CONC[TBL_BP_EC_CONC['Cd_CFOP_SUF'].astype(str).str.contains(r'406|551|553|555', na=False)]
        dds_df.to_excel(
                            rf"{local}/BP_ANLS/resultado_conciliacao.xlsx",
                            index=False
                        )


        crit_NFe_inv = ~dds_df['SIT_CONC'].str.startswith("SOM")
        crit_QTD_inv = dds_df['DIV_QTD'].abs() > 0.01
        crit_VL_inv = dds_df['DIV_VL'].abs() > 0.01
        crit_GL_inv = ~crit_QTD_inv & ~crit_VL_inv

        Nr_NFe_inv = f"{len(dds_df):,.0f}".replace(",",".")
        Nr_NFe_nCONC_QTD_inv = f"{len(dds_df[crit_NFe_inv & crit_QTD_inv]):,.0f}".replace(",",".")
        Nr_NFe_nCONC_VL_inv = f"{len(dds_df[crit_NFe_inv & crit_VL_inv]):,.0f}".replace(",",".")
        Nr_NFe_CONC_GL_inv = f"{len(dds_df[crit_NFe_inv & crit_GL_inv]):,.0f}".replace(",",".")

        dds_df['VL_ERP_TOT'] = dds_df['VL_TOT_ICMS'] + dds_df['VL_TOT_IPI'] + dds_df['VL_ITEM']

        crit_IT1_inv = crit_NFe_inv & ~crit_QTD_inv
        VL_NFe_CONC_QTD_inv = (f"{max(dds_df[crit_IT1_inv]['VL_ERP_TOT'].sum(),dds_df[crit_IT1_inv]['VL_ITEM_EFD'].sum()):,.2f}"
                            .replace(".","x")
                            .replace(",",".")
                            .replace("x",","))
        crit_IT2_inv = crit_NFe_inv & ~crit_VL_inv
        VL_NFe_CONC_VL_inv = (f"{max(dds_df[crit_IT2_inv]['VL_ERP_TOT'].sum(),dds_df[crit_IT2_inv]['VL_ITEM_EFD'].sum()):,.2f}"
                            .replace(".","x")
                            .replace(",",".")
                            .replace("x",","))
        crit_IT3_inv = crit_NFe_inv & crit_GL_inv
        VL_NFe_CONC_GL_inv = (f"{max(dds_df[crit_IT3_inv]['VL_ERP_TOT'].sum(),dds_df[crit_IT3_inv]['VL_ITEM_EFD'].sum()):,.2f}"
                            .replace(".","x")
                            .replace(",",".")
                            .replace("x",","))
        VL_NFe_inv = (f"{max(dds_df['VL_ERP_TOT'].sum() * 0,dds_df['VL_ITEM_EFD'].sum()):,.2f}"
                    .replace(".","x")
                    .replace(",",".")
                    .replace("x",","))
        crit_IT4_inv = (dds_df['VL_ERP_TOT'].abs() < 0.1) | dds_df['VL_ERP_TOT'].isnull()
        VL_NFe_nCONC_ausERP_inv = (f"{dds_df[crit_IT4_inv]['VL_ITEM_EFD'].sum():,.2f}"
                            .replace(".","x")
                            .replace(",",".")
                            .replace("x",","))

        PCT_inv = (f"{max(dds_df[crit_IT3_inv]['VL_ERP_TOT'].sum(),dds_df[crit_IT3_inv]['VL_ITEM'].sum()) / max(dds_df['VL_ERP_TOT'].sum() * 0,dds_df['VL_ITEM'].sum()):,.2%}"
                                    .replace(".","x")
                                    .replace(",",".")
                                    .replace("x",","))
        PCT_EFD_inv = (f"{dds_df[crit_IT4_inv]['VL_ITEM'].sum() / max(dds_df['VL_ERP_TOT'].sum(),dds_df['VL_ITEM'].sum()):,.2%}"
                            .replace(".","x")
                            .replace(",",".")
                            .replace("x",","))
        vl_ctr_inv = (dds_df[crit_IT4_inv]['VL_ITEM_EFD'].sum() / 
                    (
                        max(dds_df['VL_ERP_TOT'].sum() * 0,dds_df['VL_ITEM_EFD'].sum()) -
                        max(dds_df[crit_IT3_inv]['VL_ERP_TOT'].sum(),dds_df[crit_IT3_inv]['VL_ITEM_EFD'].sum())
                    )
                    )
        PCT_PART_ERRO_inv = (f"""{vl_ctr_inv:,.2%}"""
                            .replace(".","x")
                            .replace(",",".")
                            .replace("x",","))

        
        st.html(f"""
                <p  style="text-align: justify;text-indent: 40px">Foram encontradas {Nr_NFe}, sendo que {Nr_NFe_CONC_GL} conciliaram 
                tanto em valor quanto em quantidade. Adicionalmente, {Nr_NFe_nCONC_QTD} apresentaram divergência de quantidade e 
                {Nr_NFe_nCONC_VL} apresentaram divergência em unidades monetárias. O valor total, cruzando ERP e EFD ICMS, é de 
                R$ {VL_NFe}, EFD de referência, com R$ {VL_NFe_CONC_GL} conciliados em valor e quantidade, isto é, {PCT} de conciliação em valor. O 
                valor consolidado de NFe encontradas no EFD e não localizadas no ERP é de R$ {VL_NFe_nCONC_ausERP} ou 
                {PCT_PART_ERRO} do erro. {txt_ctr}</p> 
                <p  style="text-align: justify;text-indent: 40px">Se considerarmos CFOP de investimento, foram encontradas {Nr_NFe_inv}, sendo que {Nr_NFe_CONC_GL_inv} conciliaram 
                tanto em valor quanto em quantidade. Adicionalmente, {Nr_NFe_nCONC_QTD_inv} apresentaram divergência de quantidade e 
                {Nr_NFe_nCONC_VL_inv} apresentaram divergência em unidades monetárias. O valor total, cruzando ERP e EFD ICMS, é de 
                R$ {VL_NFe_inv}, EFD de referência, com R$ {VL_NFe_CONC_GL_inv} conciliados em valor e quantidade, isto é, {PCT_inv} de conciliação em valor. O 
                valor consolidado de NFe encontradas no EFD e não localizadas no ERP é de R$ {VL_NFe_nCONC_ausERP_inv} ou 
                {PCT_PART_ERRO_inv} do erro.
                Nota-se que o foco neste trabalho é nas operações com CFOP de investimento, cuja população constituem o segmento 
                crítico desta fiscalização, demandando atenção devido ao impacto direto na constituição do ativo imobilizado.</p>
                """)

        st.html(f"""<h3>Conciliação do ERP com o EFD ICMS, visão analítica</h3>
                    <p style="text-align: justify;text-indent: 40px; padding-top: 20px">Foi 
                    solicitado para a empresa, Manual de Dados, o extrato de compras, conforme ERP. Nesse teste, 
                    faz-se a comparação dos dados dos materiais apresentados no ERP com os declarados no sistema de 
                    escrituração fiscal, EFD ICMS. Para fazer isso, aplicou-se heurística simples, usando as seguintes
                    chaves em cada base:</p>
                        <div class="rules-list" style="margin: 20px 0; padding-left: 60px;">
                            <ol style="list-style-type: decimal; line-height: 1.6;">
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Quantidade, Unidade, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 1, VL_TOT_LIQ como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Quantidade, Unidade, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 2, VL_TOT_LIQ + VL_TOT_ICMS + VL_ST como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Quantidade, Unidade, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 3, VL_TOT_LIQ + VL_TOT_IPI + VL_TOT_ICMS + VL_ST como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Quantidade, Unidade, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 4, VL_TOT_LIQ + VL_TOT_IPI + VL_TOT_ICMS como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Quantidade, Unidade, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 5, VL_TOT_LIQ + VL_TOT_IPI como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Quantidade, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 1 SEM UNIDADE, VL_TOT_LIQ como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Quantidade, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 2 SEM UNIDADE, VL_TOT_LIQ + VL_TOT_ICMS + VL_ST como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Quantidade, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 3 SEM UNIDADE, VL_TOT_LIQ + VL_TOT_IPI + VL_TOT_ICMS + VL_ST como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Quantidade, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 4 SEM UNIDADE, VL_TOT_LIQ + VL_TOT_IPI + VL_TOT_ICMS como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Quantidade, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 5 SEM UNIDADE, VL_TOT_LIQ + VL_TOT_IPI como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Quantidade, Unidade</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA_QTD_COM_UND)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Quantidade</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA_QTD_SEM_UND)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 1 VALOR, VL_TOT_LIQ como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 2 VALOR, VL_TOT_LIQ + VL_TOT_ICMS + VL_ST como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 3 VALOR, VL_TOT_LIQ + VL_TOT_IPI + VL_TOT_ICMS + VL_ST como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 4 VALOR, VL_TOT_LIQ + VL_TOT_IPI + VL_TOT_ICMS  como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                                <li style="margin-bottom: 10px;">
                                    <strong>Código NFe, Valor</strong> 
                                    <span style="color: #666; font-style: italic;">
                                        (REGRA 5 VALOR, VL_TOT_LIQ + VL_TOT_IPI como valor no ERP e VL_ITEM no EFD)
                                    </span>
                                </li>
                            </ol>
                        </div>

                    <p style="text-align: justify;text-indent: 40px; padding-top: 20px">Segue o resultado:</p>    
                    """)
        TBL_BP_EC_CONC = carga_sqlite_cache(sSQL, bd)
        for n in TBL_BP_EC_CONC.columns.to_list():
            if n[:2].upper() in ['VL', 'QT'] and not (TBL_BP_EC_CONC[n].dtype == 'object'):
                TBL_BP_EC_CONC[n] = TBL_BP_EC_CONC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(TBL_BP_EC_CONC.head(1000), width='stretch', hide_index=True)

        CNPJ_EFD = TBL_BP_EC_CONC[TBL_BP_EC_CONC['SIT_CONC'] == 'SOMENTE EFD'][['Nm_EMP','CNPJ_EFD', 
                                                                               'CHV_NFE_EFD', 'Cd_CFOP_EFD','VL_ITEM_EFD']].copy()
        
        CNPJ_EFD['VL_ITEM_EFD'] = pd.to_numeric(CNPJ_EFD['VL_ITEM_EFD'].astype(str).str.replace(",","x").str.replace(".","").str.replace("x","."), errors='coerce')
        CNPJ_ERP = TBL_BP_EC_CONC[TBL_BP_EC_CONC['SIT_CONC'] == 'SOMENTE ERP'][['Txt_Nom_Forn','CNPJ', 
                                                                               'CHV_NFE', 'Cd_CFOP','VL_ITEM',
                                                                               'VL_TOT_IPI','VL_TOT_ICMS']].copy()
        for col in ['VL_ITEM','VL_TOT_IPI','VL_TOT_ICMS']:
            CNPJ_ERP[col] = pd.to_numeric(CNPJ_ERP[col].astype(str).str.replace(",","x").str.replace(".","").str.replace("x","."), errors='coerce').fillna(0)
        CNPJ_ERP['VL_ITEM'] += CNPJ_ERP['VL_TOT_IPI']
        CNPJ_ERP['VL_ITEM'] += CNPJ_ERP['VL_TOT_ICMS']
        if len(CNPJ_EFD)>0:
            st.html("""<p style="text-align: justify; text-indent: 40px; padding-top: 20px">
                        Com base na análise de conciliação fiscal realizada entre os sistemas ERP e EFD ICMS, foram identificados 
                            itens que não apresentaram correspondência perfeita entre as bases de dados, tabela abaixo. Do total de registros não 
                            conciliados presentes na tabela EFD, procedeu-se com um filtro adicional para selecionar 
                            especificamente aqueles operações cujo CFOP (Código Fiscal de Operações e Prestações) está associado 
                            a transações de investimento.                     
                        </p>
                        """)
            st.dataframe(CNPJ_EFD, width='stretch', hide_index=True)
            LST_CFOP_INV = ['1406', '1551', '1553', '1555', '2406', '2553', '2551', '2555']
            txt_CFOP = (", ").join(LST_CFOP_INV)
            st.html(f"""<p style="text-align: justify; text-indent: 40px; padding-top: 20px">
                        A seleção por CFOP de investimento ({txt_CFOP}) visa priorizar a análise de operações que envolvem aquisições de 
                        bens para o ativo imobilizado, capitalização ou outras movimentações dessa natureza. 
                        Esta etapa de filtragem permitiu isolar um subconjunto mais crítico dos registros 
                        não conciliados para aprofundamento analítico. Para garantir uma amostragem representativa e 
                        metodologicamente consistente, aplicou-se um processo de sorteio por unidades monetárias. Esta abordagem 
                        assegura que os casos selecionados para fiscalização reflitam adequadamente a população total de não 
                        conciliações relacionadas a investimentos, evitando vieses de seleção e permitindo inferências 
                        estatisticamente válidas sobre as causas-raiz dos discrepâncias identificadas. Os casos sorteados serão 
                        analisados, considerando: verificação do documento fiscal, conferência com ERP e EFD ICMS, avaliação da adequação da 
                        classificação fiscal ou no ERP e identificação de possíveis erros de digitação.                   
                        </p>
                        """)
            
            CNPJ_EFD = (CNPJ_EFD
                        .groupby(['Nm_EMP','CNPJ_EFD','Cd_CFOP_EFD'], dropna=False)
                        .agg(
                            VL_TOTAL= ('VL_ITEM_EFD', 'sum'),
                            QTD_NFE = ('VL_ITEM_EFD', 'count'), 
                        )
                        .reset_index()
                        .sort_values(by='VL_TOTAL', ascending=False)
                        )
            CNPJ_EFD_INV = CNPJ_EFD[CNPJ_EFD['Cd_CFOP_EFD'].isin(LST_CFOP_INV) & (CNPJ_EFD['VL_TOTAL']>0)].copy().reset_index(drop=True)
            CNPJ_EFD_CON = CNPJ_EFD[(~CNPJ_EFD['Cd_CFOP_EFD'].isin(LST_CFOP_INV)) & (CNPJ_EFD['VL_TOTAL']>0)].copy().reset_index(drop=True)
        
        def grafico_A(df, nome, nm_agrup):
            
            CNPJ_EFD_AMST = df.groupby(nm_agrup)[['VL_TOTAL']].sum().reset_index()
            CNPJ_EFD_AMST, amostra_final, IA, R, texto_anl = sorteio(CNPJ_EFD_AMST, 
                            coluna_valor = 'VL_TOTAL', 
                            coluna_identificador = nm_agrup,

                            metodo = "AUM",
                            tipo = "INDICADORES", st=st)
            
            def _ger_html(dados, valor_padrao = "ND"):
                if nome != 'EFD_INV_NC':
                    return ""
                html_content = f"""
                                    <style>
                                        body {{
                                            font-family: Arial, sans-serif;
                                            margin: 0;
                                            padding: 20px;
                                            background-color: #f9f9f9;
                                        }}
                                        .container {{
                                            max-width: 800px;
                                            margin: auto;
                                            background: white;
                                            padding: 20px;
                                            border-radius: 8px;
                                            box-shadow: 0 0 10px rgba(0,0,0,0.1);
                                        }}
                                        h1 {{
                                            color: #2c3e50;
                                            text-align: center;
                                        }}
                                        h2 {{
                                            color: #34495e;
                                            border-bottom: 1px solid #ccc;
                                            padding-bottom: 5px;
                                        }}
                                        p {{
                                            line-height: 1.6em;
                                        }}
                                        ul {{
                                            list-style-type: none;
                                            padding-left: 0;
                                        }}
                                        li {{
                                            margin-bottom: 10px;
                                        }}
                                        .section {{
                                            margin-top: 20px;
                                        }}
                                    </style>

                                    <div class="container">
                                        <h3>{dados.get('razao_social', valor_padrao)}</h3>
                                        
                                        <p><strong>Nome Fantasia:</strong> {dados.get('nome_fantasia', valor_padrao)}</p>
                                        <p><strong>CNPJ:</strong> {dados.get('cnpj', valor_padrao)}</p>
                                        <p><strong>Data Início Atividade:</strong> {dados.get('data_inicio_atividade', valor_padrao)}</p>
                                        <p><strong>Situação Cadastral:</strong> {dados.get('descricao_situacao_cadastral', valor_padrao)} ({dados.get('data_situacao_cadastral', valor_padrao)})</p>
                                        <p><strong>Natureza Jurídica:</strong> {dados.get('natureza_juridica', valor_padrao)}</p>
                                        <p><strong>Porte:</strong> {dados.get('porte', valor_padrao)}</p>
                                        <p><strong>Capital Social:</strong> R$ {dados.get('capital_social', valor_padrao):,.2f}</p>

                                        <div class="section">
                                            <h4>Endereço</h4>
                                            <p><strong>Tipo Logradouro:</strong> {dados.get('descricao_tipo_de_logradouro', valor_padrao)}</p>
                                            <p><strong>Logradouro:</strong> {dados.get('logradouro', valor_padrao)}, {dados.get('numero', valor_padrao)}</p>
                                            <p><strong>Bairro:</strong> {dados.get('bairro', valor_padrao)}</p>
                                            <p><strong>Município:</strong> {dados.get('municipio', valor_padrao)} - {dados.get('uf', valor_padrao)}</p>
                                            <p><strong>CEP:</strong> {dados.get('cep', valor_padrao)}</p>
                                            <p><strong>Complemento:</strong> {dados.get('complemento', valor_padrao)}</p>
                                        </div>

                                        <div class="section">
                                            <h4>Contato</h4>
                                            <p><strong>Telefone:</strong> {dados.get('ddd_telefone_1', valor_padrao)}</p>
                                            <p><strong>Fax:</strong> {dados.get('ddd_fax', valor_padrao)}</p>
                                        </div>

                                        <div class="section">
                                            <h4>CNAE Fiscal</h4>
                                            <p>{dados.get('cnae_fiscal_descricao', valor_padrao)}</p>
                                            
                                            <h3>CNAEs Secundários</h3>
                                            <ul>
                                                {''.join([f'<li>{item["descricao"]}</li>' for item in dados['cnaes_secundarios']])}
                                            </ul>
                                        </div>

                                        <div class="section">
                                            <h4>Regime Tributário</h4>
                                            <table style="width:100%; border-collapse: collapse;">
                                                <thead>
                                                    <tr style="background:#eee;"><th>Ano</th><th>Forma Tributação</th></tr>
                                                </thead>
                                                <tbody>
                                                    {''.join([f'<tr><td>{item["ano"]}</td><td>{item["forma_de_tributacao"]}</td></tr>' for item in dados['regime_tributario']])}
                                                </tbody>
                                            </table>
                                        </div>

                                        <div class="section">
                                            <h4>Quadro Societário</h4>
                                            <ul>
                                                {''.join([
                                                    f"<li><strong>{socio['nome_socio']}</strong><br/>Qualificação: {socio['qualificacao_socio']}<br/>Entrada: {socio['data_entrada_sociedade']}<br/>País: {socio.get('pais', 'Brasil')}</li>"
                                                    for socio in dados['qsa']
                                                ])}
                                            </ul>
                                        </div>
                                    </div>
                                    """
                return html_content
            
            amostra_final1 = ", ".join(amostra_final)
            st.html(texto_anl.replace('</p>','') + f""" A amostra considera os seguintes CNPJ: {amostra_final1}. O resultado 
                    aberto é dado a seguir:</p>""")
   
            st.dataframe(CNPJ_EFD_AMST, width='stretch', hide_index=True)


            if (nome == 'EFD_INV_NC') and (len(amostra_final)>0) and apr2:
                st.html(f"""<p style="text-align: justify; text-indent: 40px; padding-top: 20px">
                            Informações adicionais para os CNPJ selecionados:                   
                            </p>
                            """)
                PASTA_RELATORIOS = Path(rf"{local}/BP_ANLS/RELATORIOS_CNPJ")
                PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)
                for cnpj in amostra_final:
                    cnpj_limpo = "".join(filter(str.isdigit, str(cnpj)))
                    arquivo_html = PASTA_RELATORIOS / f"{cnpj_limpo}.html"
                    arquivo_docx = PASTA_RELATORIOS / f"{cnpj_limpo}"
                    if arquivo_html.exists():
                        txt_html = arquivo_html.read_text(encoding="utf-8")
                    else:
                        dic_prov = consultar_empresa(cnpj)
                        txt_html = _ger_html(dic_prov)
                        if txt_html != "":
                            arquivo_html.write_text(txt_html, encoding="utf-8")
                            new_parser = HtmlToDocx()
                            new_parser.parse_html_file(arquivo_html, arquivo_docx)
                    if txt_html != "":
                        st.html(txt_html)

            x = np.arange(len(CNPJ_EFD_AMST))
            y = CNPJ_EFD_AMST["VL_ACUM"]

            limA = CNPJ_EFD_AMST[CNPJ_EFD_AMST["CLS_ABC"] == "A"].index.max()
            limB = CNPJ_EFD_AMST[CNPJ_EFD_AMST["CLS_ABC"] == "B"].index.max()

            fig17b = plt.figure(figsize=(14, 6))
            cmap_line = plt.cm.plasma(0.75)
            cmap_points = plt.cm.plasma(0.25)
            plt.axvspan(0, limA, alpha=0.18, color="#f70a0a")
            plt.axvspan(limA, limB, alpha=0.15, color="#0404f3")
            plt.axvspan(limB, len(CNPJ_EFD_AMST), alpha=0.12, color="#09f567")
            plt.plot(x, y, linewidth=2, color=cmap_line)

            for idx, row in CNPJ_EFD_AMST.iterrows():
                if row["FLG_AMST"] == 1:
                    plt.scatter(idx, row["VL_ACUM"], 
                                s=80, 
                                edgecolor="black", 
                                linewidth=1.2, 
                                facecolor=cmap_points)
            txt = nome.replace("_"," ")
            plt.title(f"Curva Acumulada de Fornecedores não Conciliados, lado {txt}, com Destaque ABC e Amostragem (AUM)", fontsize=16)
            plt.ylabel("Valor Acumulado", fontsize=12)

            passo = max(1, int(round(len(CNPJ_EFD_AMST) / 10, 0)))
            plt.xticks(
                            x[::passo], 
                            CNPJ_EFD_AMST[nm_agrup][::passo], 
                            rotation=45, 
                            ha="right",
                            fontsize=12
                        )

            plt.grid(alpha=0.2)
            plt.tight_layout()
            st.html("""<p style="text-align: justify; text-indent: 40px; padding-top: 20px">
                       Para melhor visualizarmos segue o gráfico com a região de classificação ABC e as amostras sorteadas. 
                       Como observa-se as amostras se concentram na região de maior criticidade.                     
                       </p>
                    """)
            col1ka, col2ka, col3ka = st.columns([1,2,1], gap='small')
            with col2ka:
                st.pyplot(fig17b)
            plt.close()

            plt.savefig(f"{local}//RELATORIOS//figuras//amostra_NFe_{nome}.png", dpi=300, bbox_inches='tight')
        if len(CNPJ_EFD_INV)>0:
            grafico_A(CNPJ_EFD_INV, 'EFD_INV_NC', 'CNPJ_EFD')
 
        if len(CNPJ_EFD_CON)>0:
            st.html("""<p style="text-align: justify; text-indent: 40px; padding-top: 20px">
                       A seguir procedimento similar para itens de despesa.                     
                       </p>
                    """)
            st.write(CNPJ_EFD_CON)
            grafico_A(CNPJ_EFD_CON, 'EFD_DESP_NC', 'CNPJ_EFD')
        
        if len(CNPJ_ERP)>0:
            st.html("""<p style="text-align: justify; text-indent: 40px; padding-top: 20px">
                        Com base na análise de conciliação fiscal realizada entre os sistemas ERP e EFD ICMS, foram identificados 
                        itens que não apresentaram correspondência perfeita entre as bases de dados, tabela abaixo. Do total de registros não 
                        conciliados presentes na tabela ERP, procedeu-se com um filtro adicional para selecionar 
                        especificamente aqueles operações cujo CFOP (Código Fiscal de Operações e Prestações) está associado 
                        a transações de investimento.                     
                       </p>
                    """)
            st.dataframe(CNPJ_ERP, width='stretch', hide_index=True)
            st.html(f"""<p style="text-align: justify; text-indent: 40px; padding-top: 20px">
                        A seleção por CFOP de investimento ({txt_CFOP}) visa priorizar a análise de operações que envolvem aquisições de 
                        bens para o ativo imobilizado, capitalização ou outras movimentações dessa natureza. 
                        Esta etapa de filtragem permitiu isolar um subconjunto mais crítico dos registros 
                        não conciliados para aprofundamento analítico. Para garantir uma amostragem representativa e 
                        metodologicamente consistente, aplicou-se um processo de sorteio por unidades monetárias. Esta abordagem 
                        assegura que os casos selecionados para fiscalização reflitam adequadamente a população total de não 
                        conciliações relacionadas a investimentos, evitando vieses de seleção e permitindo inferências 
                        estatisticamente válidas sobre as causas-raiz dos discrepâncias identificadas. Os casos sorteados serão 
                        analisados, considerando: verificação do documento fiscal, conferência com ERP e EFD ICMS, avaliação da adequação da 
                        classificação fiscal ou no ERP e identificação de possíveis erros de digitação.                   
                        </p>
                        """)
            
            CNPJ_ERP = (CNPJ_ERP
                        .groupby(['Txt_Nom_Forn','CNPJ','Cd_CFOP'], dropna=False)
                        .agg(
                            VL_TOTAL= ('VL_ITEM', 'sum'),
                            QTD_NFE = ('VL_ITEM', 'count'), 
                        )
                        .reset_index()
                        .sort_values(by='VL_TOTAL', ascending=False)
                        )
            CNPJ_ERP_INV = CNPJ_ERP[CNPJ_ERP['Cd_CFOP'].isin(LST_CFOP_INV) & (CNPJ_ERP['VL_TOTAL']>0)].copy().reset_index(drop=True)
            CNPJ_ERP_CON = CNPJ_ERP[(~CNPJ_ERP['Cd_CFOP'].isin(LST_CFOP_INV)) & (CNPJ_ERP['VL_TOTAL']>0)].copy().reset_index(drop=True)
        
        if len(CNPJ_ERP_INV)>0:
            grafico_A(CNPJ_ERP_INV, 'ERP_INV_NC', 'CNPJ')
 
        if len(CNPJ_ERP_CON)>0:
            st.html("""<p style="text-align: justify; text-indent: 40px; padding-top: 20px">
                       A seguir procedimento similar para itens de despesa.                     
                       </p>
                    """)
            grafico_A(CNPJ_ERP_CON, 'ERP_DESP_NC', 'CNPJ')

        st.html("""<p style="text-align: justify; text-indent: 40px; padding-top: 20px">
                        O sistema de análise utiliza diversas variáveis para identificar riscos e situações específicas 
                        nas operações. A variável <strong>OBS_SFF_ST</strong> indica possibilidade de substituição tributária, 
                        enquanto <strong>OBS_SFF_DIFAL</strong> sinaliza operações com diferimento de ICMS. 
                        Já <strong>OBS_SFF_IMP</strong> identifica possíveis operações de importação que requerem atenção especial.
                        A variável <strong>SIT_CONC</strong> representa o resultado da conciliação fiscal conforme a heurística 
                        definida previamente, indicando o nível de correspondência entre os dados do ERP e o sistema fiscal. 
                        O <strong>Cd_Estrato</strong>, por sua vez, é um indicador de risco calculado com base em múltiplos fatores 
                        que avaliam a criticidade da operação.
                        O cálculo do Cd_Estrato considera o <strong>Peso_SIT_CONC</strong>, que atribui pontuação 0 para operações 
                        conciliadas e 10 para não conciliadas. O <strong>Peso_CFOP</strong> adiciona 3 pontos se o CFOP possuir 
                        sufixo de investimento, ou 1 ponto caso contrário. O <strong>Peso_Materialidade</strong> é determinado 
                        pelo logaritmo de base 10 da diferença em valor entre as bases analisadas.
                        O <strong>Fator_Risco</strong> é obtido através da soma dos pesos mencionados anteriormente. 
                        A classificação final do risco segue a seguinte escala: quando o Fator_Risco é superior a 20 pontos, 
                        o Cd_Estrato é considerado <strong>crítico</strong> e a operação deve ser obrigatoriamente avaliada; 
                        valores entre 15 e 20 indicam <strong>risco alto</strong>; operações com Fator_Risco igual a zero 
                        são classificadas como <strong>risco zero</strong>; e valores entre 0 e 15 são considerados 
                        <strong>risco residual</strong>, indicando menor prioridade de análise.
                    </p>
                """)

@st.fragment()
def _vis_006(bd_path="", st=None, empresa = "", bd_path2="", local="", apr2=False):
    with sl.connect(bd_path2) as bd:
        if not existe_tabela('CONSOL_TOT_QTD_EC', bd):
            return
        st.html(f"""<h3>
                    Conciliação da aplicação dos materiais com as compras declaradas</h3>
                    <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                    a conciliação, em valor e quantidade, entre compras e as quantidades do razão de ODI, 
                    razão de ODC, almoxarifado e de ODS.</p>
                    """)
        sSQL = """SELECT * FROM CONSOL_TOT_QTD_EC"""
        ANL_LST_TUC = carga_sqlite_cache(sSQL, bd)
        for n in ANL_LST_TUC.columns.to_list():
            if n[:2].upper() in ['VL', 'QT']:
                ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True)

        if existe_tabela('TAB_CALC_BP', bd):
            st.html(f"""<h2>Memória de cálculo do VF atualizado</h2>
                        <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                        o memorial de cálculo para determinação do valor de fábrica, visão analítica.</p><br>
                        """)
            sSQL = """
                    SELECT * FROM TAB_CALC_BP

                    """
            ANL_LST_TUC1 = carga_sqlite_cache(sSQL, bd)
            ANL_LST_TUC1 = conv_num(ANL_LST_TUC1, lista = ['VL', 'QT'])

            st.dataframe(ANL_LST_TUC1, width='stretch', hide_index=True)

        if existe_tabela('TAB_OUTLIERS', bd):
            st.html(f"""<h2>Análise de OUTLIERS</h2>
                        <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                        entender o porquê de estar sendo indicado a existência de OUTLIERS nas compras. 
                        Abaixo é apresentado s resultados.</p><br>
                        """)
            sSQL = """
                    SELECT * FROM TAB_OUTLIERS

                    """
            ANL_LST_TUC2 = carga_sqlite_cache(sSQL, bd)
            for n in ANL_LST_TUC2.columns.to_list():
                if n in ['DELTA_PC', 'VAR_PER']:
                    ANL_LST_TUC2[n] = ANL_LST_TUC2[n].fillna(0).apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['VL', 'Q1', 'Q3', 'QT', 'CM', 'IN', 'ME', 'ST', 'DE', 
                                    'MA', 'LI']:
                    ANL_LST_TUC2[n] = ANL_LST_TUC2[n].fillna(0).apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            st.dataframe(ANL_LST_TUC2, width='stretch', hide_index=True)

        if existe_tabela('TAB_FIM_BPC', bd):
            st.html(f"""<h2>Resumo do BC UC</h2>
                        """)
            
            img1 = st.columns([1, 1, 1], gap='small')
            with img1[1]:
                st.image('Imagens/VF_F1.png', caption="Representação da Análise do BP", width='stretch')
            st.html("""
                        <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                        entender os valores obtidos no processamento dos dados encaminhados em decorrência do Manual de Dados. 
                        Nesta etapa do cálculo, busca-se os dados do extrato de compra e faz um 
                        cruzamento pelo código de material com o ROA. Deste cruzamento, faz-se a 
                        classificação dos itens (TUCAGEM e Natureza de gasto). Busca-se fazer o 
                        rateio do financeiro do ICMS e do VL_ODC, caso ocorra. No fim, prepara-se 
                        uma estatistica descritiva, por item, com valores máximo, mínimo e desvio 
                        padrão (identificar maiores variações). Também se aplica os fatores de 
                        atualização, de acordo com a TUCAGEM definida anteriormente. No fim, 
                        consolida-se os resultados em duas formas: TUCAGEM e Item.
                        Abaixo é apresentado os resultados:</p>
                        """)
            sSQL = """
                    SELECT * FROM TAB_FIM_BPC

                    """
            ANL_LST_TUC3 = carga_sqlite_cache(sSQL, bd)
            for n in ANL_LST_TUC3.columns.to_list():
                if n in ['DELTA_PC', 'VAR_PER']:
                    ANL_LST_TUC3[n] = ANL_LST_TUC3[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['VL', 'Q1', 'Q3', 'QT', 'CM', 'IN', 'ME', 'ST', 'DE', 
                                    'MA', 'LI']:
                    ANL_LST_TUC3[n] = ANL_LST_TUC3[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            st.dataframe(ANL_LST_TUC3, width='stretch', hide_index=True)

        if existe_tabela('BP_COMP', bd):
            st.html(f"""<h2>
                        Resumo comparação entre cálculo e valor encaminhado</h2>
                        <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                        entender os valores obtidos no processamento dos dados encaminhados na SDI-001. 
                        Abaixo é apresentado resultados para análise.</p>
                        """)
            sSQL = """
                    SELECT * FROM BP_COMP

                    """
            ANL_LST_TUC4 = carga_sqlite_cache(sSQL, bd)
            for n in ANL_LST_TUC4.columns.to_list():
                
                if n in ['DELTA_PC', 'VAR_PER', 'TST_04']:
                    if not (ANL_LST_TUC4[n].dtype == 'object'):
                        ANL_LST_TUC4[n] = ANL_LST_TUC4[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['VL', 'Q1', 'Q3', 'QT', 'CM', 'IN', 'ME', 'ST', 'DE', 
                                    'MA', 'LI']:
                    if not (ANL_LST_TUC4[n].dtype == 'object'):
                        ANL_LST_TUC4[n] = ANL_LST_TUC4[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            st.dataframe(ANL_LST_TUC4, width='stretch', hide_index=True)

@st.fragment()
def _vis_007(bd_path="", st=None):
    with sl.connect(bd_path) as bd:
        if not existe_tabela('TAB_OUTLIERS', bd):
            return
        st.html(f"""<h2 style="text-align: center;font-size: 30px;">
                            Itens que apresentam variações significativas</h2>
                    <p  style="text-align: justify;text-indent: 40px">Itens que tem valores 
                    que são um padrão diferente do esperado. Isso inclui compras muito 
                    eficientes ou ineficientes, que alteram significativamente o valor
                        médio ponderado. Pode ocorrer, também, de haver concentração em dois 
                    preços; importante avaliar. É importante avaliar as notas associados 
                    aos itens destacados. Leia o relatório de Cálculos para análise 
                    completa. Pode não ter ocorrências (quadro desabilitado).</p><br>
                    """)

        if existe_tabela('TAB_OUTLIERS', bd):
            sSQL = """SELECT DISTINCT * FROM TAB_OUTLIERS;"""
            teste = pd.read_sql(sSQL, bd)
            LST_ITENS3 = teste[teste['OBS_FISC'] != 'OK']['COD_ITEM'].drop_duplicates().to_list()
            LST_ITENS3 = sorted(LST_ITENS3)
            TST1 = tuple(LST_ITENS3)
            cols5A = st.columns([0.4,0.6], gap='small')

            with cols5A[0]:
                opcao5 = st.selectbox(
                                        "Selecione o item",
                                        TST1
                                    )

            if opcao5:
                df_filt4 = teste[teste['COD_ITEM'] == opcao5].copy()

                nome = df_filt4['CMU'].mean()
                box_trace = go.Box(y=df_filt4['CMU'], boxpoints='all', name='CMU_ITEM',
                                    jitter=0.3, pointpos=-1.8, marker_color='royalblue',
                                    boxmean='sd')
 
                fig = go.Figure(data=[box_trace])
                fig.update_layout(title=f'Valor médio de todos os registros do código {opcao5}.',
                                    yaxis_title='R$/UND')
                
                a = f"{nome:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                fig.add_annotation(
                                        x=1,
                                        y=1.0,
                                        xref="paper",
                                        yref="paper",
                                        text=f"Valor médio de R$ {a}",
                                        showarrow=False
                                    )
                img1 = st.columns([1, 5, 1], gap='small')
                with img1[1]:
                    st.plotly_chart(fig, width='stretch')

                st.html(f"""
                            <p style="text-align: justify;text-indent: 40px;">Itens que 
                            chamaram atenção:</p>
                            """)
                df = df_filt4[df_filt4['OBS_FISC'] != 'OK']                
                for n in df.columns.to_list():
                    if n[:2].upper() in ['VL', 'QT']:
                        if not (df[n].dtype == 'object'):
                            df[n] = df[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

                st.dataframe(df, width='stretch', hide_index=True)
                
        else:
            if st:
                st.error('Falha ao importar o arquivo TST_04 da base local.')
            else:
                raise UserWarning('Falha ao importar o arquivo TST_04 da base local.')  

        if existe_tabela('BP_COMP', bd):
            sSQL = """SELECT DISTINCT * FROM BP_COMP;"""
            BP_COMP = pd.read_sql(sSQL, bd)
            LST_ITENS4 = BP_COMP['Nr_TUC_AVL'].drop_duplicates().to_list()
            if len(LST_ITENS4)>0:
                st.divider()
                st.html(f"""<h2 style="text-align: center;font-size: 30px;">
                            Comparação entre dados do LAUDO e cálculo</h2>
        
                            <p  style="text-align: justify;text-indent: 40px">Espera-se encontrar uma 
                            reta. Caso ocorram diversos segmentos de reta, é necessário ver a existência 
                            de divergências entre os dados apresentados e os empregados no 
                            cálculo da avaliadora. Caso o valor calculado seja zero, verifique o modelo empregado
                            pela fiscalização para identificar a origem. Leia o relatório de Cálculos para análise 
                            completa. Pode não ter ocorrências (quadro desabilitado).</p><br>
                            """)
                LST_ITENS4 = sorted(item for item in LST_ITENS4
                                    if item is not None and item != "")
                TST2 = tuple(LST_ITENS4)
                cols6A = st.columns([0.4,0.6], gap='small')

                with cols6A[0]:
                    opcao6 = st.selectbox(
                                            "Selecione o item",
                                            TST2
                                        )
                if opcao6:
                    df_filt5 = BP_COMP.loc[BP_COMP['Nr_TUC_AVL'] == opcao6].copy()            
                    for n in ['VL_VF_UNIT_AT_AVL', 'VL_UNI_AT_SIM']:
                        if n[:2].upper() in ['VL']:
                            if (df_filt5[n].dtype == 'object'):
                                df_filt5[n] = df_filt5[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                                df_filt5[n] = df_filt5[n].fillna(0)
                    df_filt5 = df_filt5.sort_values(by='VL_VF_UNIT_AT_AVL')

                    correlation = np.corrcoef(df_filt5['VL_VF_UNIT_AT_AVL'], df_filt5['VL_UNI_AT_SIM'])[0, 1]

                    coefficients = np.polyfit(df_filt5['VL_VF_UNIT_AT_AVL'], df_filt5['VL_UNI_AT_SIM'], 1)
                    trendline = np.polyval(coefficients, df_filt5['VL_VF_UNIT_AT_AVL'])
                    
                    std_dev = np.mean(df_filt5['VL_UNI_AT_SIM'])*0.25
                    upper_band = trendline + std_dev
                    lower_band = trendline - std_dev
                    
                    fig1 = px.scatter(df_filt5, x='VL_VF_UNIT_AT_AVL', y='VL_UNI_AT_SIM')
                    fig1.add_scatter(x=df_filt5['VL_VF_UNIT_AT_AVL'], y=trendline, mode='lines', 
                                    name='Linha de Tendência')
                    fig1.add_scatter(x=df_filt5['VL_VF_UNIT_AT_AVL'], y=upper_band, fill='tonexty', fillcolor='rgba(173, 216, 230, 0.1)', mode='lines', line=dict(color='lightblue'),
                                        name='Banda de 1,25 vezes a média')
                    fig1.add_scatter(x=df_filt5['VL_VF_UNIT_AT_AVL'], y=lower_band, fill='tonexty', fillcolor='rgba(173, 216, 230, 0.1)', mode='lines', line=dict(color='lightblue'), name='Banda de 0,75 vezes a média')
                    fig1.update_layout(
                                        title=f"Gráfico de Dispersão entre o VF da avaliadora e o calculado para {opcao6}",
                                        xaxis_title='Valor de fábrica, VF, avaliadora (R$)',
                                        yaxis_title='Valor de fábrica, VF, calculado (R$)'
                                        )
                    
                    a = f"{correlation:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    fig1.add_annotation(
                                            x=0.02,
                                            y=1,
                                            xref="paper",
                                            yref="paper",
                                            text=f"Correlação: {a}",
                                            showarrow=False
                                        )
                    img2 = st.columns([1, 5, 1], gap='small')
                    with img2[1]:
                        st.plotly_chart(fig1, width='stretch')

def visualizador_BC(st = None):
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
                <h2>Análise do Banco de Compras</h2>

                <hr></hr>
                                
                <h3>Observações iniciais</h3>
                <div style="text-align: justify;text-indent: 40px; padding-top: 10px">Esse é um documento base 
                        para se executar análise do banco de compras e do valor de fábrica do material. Pode-se 
                        alterar o arquivo, porém somente será aplicado a versão original para análise do 
                        valor empregado no laudo. Sugere-se usar este arquivo como base para modificações e 
                        inclusões de análises, para discussões com a fiscalização.<p></p></div>


                <h3>Licença Pública Geral GNU (GPL)</h3>
                <div style="text-align: justify; padding-top: 10px">Versão 3, 29 de junho de 2007<p></p></div>
                <div style="text-align: justify">Copyright (C) 2025, SFF/ANEEL.<p></p></div>
                <div style="text-align: justify;text-indent: 40px; padding-top: 10px">Este é um documento de uso livre: você pode redistribuí-lo ou modificá-lo sob os termos da Licença Pública Geral GNU, conforme publicada pela Free Software Foundation, tanto na versão 3 da Licença, ou qualquer versão posterior. Ele é distribuído na expectativa de que seja útil, mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM PROPÓSITO ESPECÍFICO. Consulte a Licença Pública Geral GNU para obter mais detalhes, no sitio <a>http://www.gnu.org/licenses/</a>.<p></p></div>

                <hr></hr>
                                
                <h3>Normas</h3>

                <div style="text-align: justify;text-indent: 40px">Conforme PRORET 2.3, item 4.1.1.1, §41 e 
                                §42:<br><br></div>

                <p style='text-align: justify;padding-left:60px;'><i>40. Os equipamentos principais são aqueles definidos como
                                Unidades de Cadastro – UC, ou unidades de Adição e/ou Retirada – UAR, pelo 
                                MCPSE. Para os equipamentos principais, o valor de um bem novo, idêntico ou 
                                similar ao avaliado é obtido a partir do Banco de Preços da 
                                Concessionária.</i></p>

                <p style='text-align: justify; padding-left:60px;'><i>41. Entende-se como Banco de Preços da Concessionária o 
                                banco formado com base em informações de todas as compras efetivamente 
                                realizadas pela concessionária, incluindo os custos de Ordem de Compra (ODC),
                                sendo que, para apuração do valor unitário médio ponderado na data-base do 
                                laudo da RTP, deverão ser consideradas, por código de material, todas as 
                                aquisições dos bens ocorridas no último ciclo tarifário da empresa, 
                                compreendido entre as datas-bases do laudo atual e do anterior. </i></p>

                <div style="text-align: justify;text-indent: 40px;">Assim, de acordo com o PRORET 2.3, 
                                versão 2C, item 44, o valor de fábrica, VF, é calculado pela equação 
                                abaixo:</div>""")

    st.markdown(r"""
                    $$
                    \large
                    \begin{aligned}
                    VF = C_{EP} + C_{ODC} + C_{ICMS}
                    \end{aligned}
                    $$
                    """)
                    

    st.html("""<div style="text-align: justify;text-indent: 40px">Em que:
                    <ul style="text-align: justify;text-indent: 80px; margin-left: 40px;">
                        <li><b>VF</b> = Valor de fábrica;</li>
                        <li><b>C<sub>EP</sub></b> = Custo do equipamento principal (nota fiscal), <b>sem ICMS</b>;</li>
                        <li><b>C<sub>ODC</sub></b> = Parcela do custo com a ordem de compra, associado ao equipamento, conforme MCSE;</li>
                        <li><b>C<sub>ICMS</sub></b> = Parcela do ICMS a ser incorporada ao valor de fábrica.</li>
                    </ul></div>
                <div style="text-align: justify; text-indent: 40px;">
                        Nada obstante, ressalte-se o §45:<br><br>
                    </div>
                    <div>
                    <p style="text-align: justify; padding-left: 60px;">
                        <i>45. Os bens deverão ser atualizados de acordo com as fórmulas 
                        paramétricas constantes do Anexo III deste Submódulo. 
                        Deverá ser considerada a data de pagamento do bem e os valores 
                        deverão ser atualizados para a data-base do laudo.</i>
                    </p>
                    </div>
                    <hr></hr>
                    
                """)
    st.html("""
                <h3>Análise do Financeiro do ICMS</h3>
                <hr></hr>
                <h3>Normas</h3>
                <div style="text-align: justify; text-indent: 40px;">
                    Conforme PRORET 2.3, item 4.1.1.1, §43:
                </div>

                <p style="text-align: justify; padding-left: 60px;padding-top: 10px;">
                    <i style="text-align: justify; text-indent: 0px;">Os impostos recuperáveis, conforme legislação em vigor, bem como os eventuais descontos ou
                    benefícios para compra eventualmente identificados, devem ser excluídos dos valores das compras
                    praticadas pela concessionária. No caso do ICMS, deverá ser agregada a parcela não recuperável do
                    imposto e o adicional decorrente da perda financeira do fluxo de crédito da parcela recuperável.</i>
                </p>

                <div style="text-align: justify; text-indent: 40px;">
                    Assim, de acordo com o PRORET 2.3, versão 2C, item 44, no caso do ICMS, deverá ser agregada a parcela não recuperável do imposto e o adicional decorrente da perda financeira do fluxo de crédito da parcela recuperável. Logo, o valor de ICMS a ser incorporado ao valor de fábrica é calculado pela equação abaixo:
                </div> 
                """)
    
    st.markdown("""
                $$
                \large
                C_{ICMS} = C_{ICMS(NR)} + \\frac{C_{ICMS(R)}}{n \\cdot i} \\cdot \\left ( \\frac{1}{\\left( 1+i \\right )^{n}} + n \\cdot i -1\\right )
                $$

                Em que:

                """)
    st.markdown(r"""
                    $$
                        \begin{array}{rl}
                            C_{ICMS} & = \text{Parcela do ICMS a ser incorporado ao valor de fábrica;} \\
                            C_{ICMS(NR)} & = \text{Parcela do ICMS não recuperável;} \\
                            C_{ICMS(R)} & = \text{Parcela do ICMS recuperável;} \\
                            i & = \text{Taxa de desconto mensal;} \\
                            n & = \text{Número de meses a recuperar (48).}
                        \end{array}
                    $$
                    """)
    
    st.markdown("""
                <div style="text-align: justify; text-indent: 40px;">
                    Sendo que a taxa de desconto mensal, <i>i</i>, é dada por:
                </div>

                $$
                \large
                i = \\left ( 1 + r_{wacc} \\right)^{\\frac{1}{12}} - 1
                $$

                <div style="text-align: justify; text-indent: 40px;">
                    <p>Lembrando que: 
                </div>

                """, unsafe_allow_html=True)
    
    st.markdown(r"""
                
                $$
                \large
                \begin{aligned}
                r_{wacc} & = \text{é o custo médio ponderado de capital anual.}
                \end{aligned}
                $$
                """, unsafe_allow_html=True)


    st.html("""<p  style="text-align: justify; padding-left: 60px;padding-top: 10px;">A equação será aplicada item a item do 
                imobilizado. Assim, para a extração de dados do ICMS sobre o Ativo Imobilizado (CIAP) iremos empregar o EFD ICMS. 
                Nele, o Bloco G opera de forma encadeada para demonstrar o cálculo das parcelas de crédito. O registro G125 é a 
                base da movimentação, onde se registram a entrada, a baixa e a apropriação de cada bem, servindo para 
                detalhar o valor do ICMS passível de apropriação. Já o registro G130 identifica especificamente o documento 
                fiscal (nota fiscal) que originou o bem, vinculando o ativo ao seu fornecedor e garantindo a rastreabilidade 
                do crédito. Por fim, o registro G140 discrimina os valores das parcelas, segregando o que é recuperável 
                (proporcional às saídas tributadas) e o que é não recuperável (proporcional às saídas isentas ou não tributadas), 
                assegurando que o somatório dessas frações reflita o crédito mensal do imposto a que a empresa tem direito.</p>
            
                <p  style="text-align: justify; padding-left: 60px;padding-top: 10px;">Optamos por essa forma, pois a metodologia 
                de rateio, de forma proporcional, comumente emrpegada, apresenta uma limitação estrutural: ao consolidar valores 
                e redistribuí-los proporcionalmente, desconsidera a cronologia individualizada das compras, isto é, a influência 
                do tempo e contextos da época. Essa distorção não é corrigível por índices de preços, uma vez que tais 
                indicadores refletem médias inflacionárias e são incapazes de capturar oportunidades de mercado (ganhos de 
                oportunidade) ou momentos de estresse financeiro específicos de cada ativo. Empregando a abertura do CIAP se 
                preserva a integridade da parcela de ICMS, garantindo que a atualização reflita a realidade econômica do momento 
                da aquisição, e não uma média aritmética descolada dos eventos de mercado.</p>
            
                <a href="https://www.gov.br/aneel/pt-br/centrais-de-conteudos/procedimentos-regulatorios/proret" target="_blank">
                    Visite o sitio da Aneel para mais detalhes!
                </a><br>
                <a href="http://sped.rfb.gov.br/pasta/show/1573" target="_blank">
                    Visite o sitio do SPED para mais detalhes!
                </a>

                <hr></hr>

                """)
    st.html("""<h3>Resultado das análises</h3>
                    <hr></hr>
                <p  style="text-align: justify;text-indent: 40px;margin-top:20px;">Abaixo pode-se selecionar se irá
                buscar dados de CNPJ com problemas. Primeiro faz-se um cálculo com valores default, caso
                queira buscar, mude a configuração.</p><br>""")
    
    apr2 = st.toggle("Buscar dados de CNPJ das empresas não conciliadas, lado EFD?", value=False, width='stretch')
    st.divider()

    executar_vis(_vis_001, bd_EFD_path, st, empresa, bd_path)
    executar_vis(_vis_002, bd_EFD_path, st, empresa, bd_path)
    executar_vis(_vis_003, bd_EFD_path, st, empresa, bd_path)
    executar_vis(_vis_004, bd_EFD_path, st, empresa, bd_path)
    executar_vis(_vis_005, bd_EFD_path, st, empresa, bd_path, local, apr2)
    executar_vis(_vis_006, bd_EFD_path, st, empresa, bd_path, local)
    executar_vis(_vis_007, bd_path, st)

    

    
        
    
