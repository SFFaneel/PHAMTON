import streamlit as st
import sqlite3 as sl
import pandas as pd
import plotly.express as px
import datetime
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

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

from SRC.calculos import importar_dados

@st.fragment()
def _vis_001(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if existe_tabela('ANL_PP', bd):
            st.html(f"""<h2 style="text-align: center;font-size: 30px;">
                        Avaliação do ponto de partida</h2>
                        <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                        o ponto de partida, abaixo, obtidos pela comparação do arquivo PPBB e dos 
                        dados do memorando encaminhado à area de tarifas. 
                        Há diferenças significativas? Verifique e justifique. 
                        Abaixo é apresentado apenas os resultados, leia o relatório 
                        de Cálculos para análise completa.</p>
                        """)
            
            sSQL = """SELECT * FROM ANL_PP"""
            ANL_LST_TUC = pd.read_sql(sSQL, bd)
            for n in ANL_LST_TUC.columns.to_list():
                if n[:2].upper() in ['VL', 'QT', 'DI']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))

            tab0 =st.columns([1, 5, 1], gap='small', vertical_alignment="center")
            with tab0[1]:
                st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True)

@st.fragment()
def _vis_002(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if existe_tabela('ANL_TST_BX', bd):
            st.divider()
            st.html(f"""<h2 style="text-align: center;font-size: 30px;">
                        Avaliação das baixas processadas</h2>
                        <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                        as baixas processadas, abaixo, obtidos pela comparação do arquivo PPBB e dos 
                        dados do arquivo de baixas. As unidades informadas, e demais dados, estão adequados? 
                        Há diferenças significativas? Verifique e justifique. 
                        Abaixo é apresentado apenas os resultados, leia o relatório 
                        de Cálculos para análise completa.</p>
                        """)
            
            sSQL = """SELECT * FROM ANL_TST_BX"""
            ANL_LST_TUC = pd.read_sql(sSQL, bd)
    
            BL_DFimp = ANL_LST_TUC.groupby(['Nr_TUC'], 
                                dropna=False)[['QTD_AIS_PP','QTD_AIS_PC','QTD_BXS_APL',
                                                'QTD_INI_BXS','QTD_FIM_BXS','QTD_BXS_CTB',
                                                'Qtd_INI_INC','Qtd_FIM_INC', 
                                                'QTD_BXS_CTB_INC']].sum().reset_index()
            BL_DFimp['TST_BXS_BL'] = 'OK'
            BL_DFimp.loc[((-abs(BL_DFimp['QTD_BXS_APL']) + 
                            abs(BL_DFimp['QTD_BXS_CTB'])) / 
                            abs(BL_DFimp['QTD_BXS_CTB'])) > 0.1,
                            'TST_BXS_BL']='DIVERGÊNCIA ENTRE ARQUIVO BAIXAS E PCBB/PPBB'
    
            for n in ANL_LST_TUC.columns.to_list():
                if n[:2].upper() in ['VL', 'QT', 'DI']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab0 =st.columns([1, 5, 1], gap='small', vertical_alignment="center")
            with tab0[1]:
                st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True)
    
            st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                    as baixas processadas, abaixo, obtidos pela comparação do arquivo PPBB e dos 
                    dados do arquivo de baixas, desprezando as unidades.
                    Há diferenças significativas? Não há diferenças, mas no caso anterior 
                    havia? Verifique e justifique. 
                    Abaixo é apresentado apenas os resultados, leia o relatório 
                    de Cálculos para análise completa.</p>
                    """)
    
            for n in BL_DFimp.columns.to_list():
                if n[:2].upper() in ['VL', 'QT', 'DI']:
                    BL_DFimp[n] = BL_DFimp[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC']:
                    BL_DFimp[n] = BL_DFimp[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab1 =st.columns([1, 5, 1], gap='small', vertical_alignment="center")
            with tab1[1]:
                st.dataframe(BL_DFimp, width='stretch', hide_index=True)

@st.fragment()
def _vis_003(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if existe_tabela('ANL_BB_CMP', bd):
            st.divider()
            st.html(f"""<h2 style="text-align: center;font-size: 30px;">
                        Resultado analítico das avaliações</h2>
                        <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                        os testes processados sobre a base blindada. Há resultados divergentes? 
                        Verifique e justifique. Abaixo é apresentado apenas os 100 primeiros 
                        resultados, leia o relatório de Cálculos para análise completa.</p><br>
                        """)
            
            sSQL = """SELECT * FROM ANL_BB_CMP LIMIT 100"""
            ANL_LST_TUC = pd.read_sql(sSQL, bd)
    
            for n in ANL_LST_TUC.columns.to_list():
                if not (ANL_LST_TUC[n].dtype == 'object'):
                    if n[:2].upper() in ['VL', 'QT']:
                        ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    elif n[:3].upper() in ['DEP','TX_']:
                        ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            config = {
                    "Dt_Lcmto": st.column_config.DateColumn("Data de Lançamento", format="DD/MM/YYYY"),
                    "Dt_REF_DADOS_ANT": st.column_config.DateColumn("Data base Laudo Anterior", format="DD/MM/YYYY"),
                    "Dt_REF_DADOS_AT": st.column_config.DateColumn("Data base Laudo Atual", format="DD/MM/YYYY"),
                } 
            try:
                ANL_LST_TUC = ANL_LST_TUC.drop(columns=['Cd_Emp_x','dt_ARQ_x','Cd_Emp_y','dt_ARQ_y'])
            except:
                pass
            tab0 =st.columns([1, 5, 1], gap='small', vertical_alignment="center")
            with tab0[1]:
                st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True, column_config=config)    
    
            sSQL = """SELECT TST_AVAL_DEP FROM ANL_BB_CMP"""
            ANL_LST_TUC = pd.read_sql(sSQL, bd)
    
            df_PROV = ANL_LST_TUC['TST_AVAL_DEP'].value_counts().reset_index()
            df_PROV.columns = ['Variável', 'Ocorrências']
    
            st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Observe a distribuição de
                    ocorrências no teste de depreciação da blindada e busque entender e justificar
                    os resultados.</p>
                    """)
    
            fig = px.treemap(
                        df_PROV, 
                        path=["Variável"], 
                        values="Ocorrências", 
                        title="📊 Distribuição de Ocorrências no Teste de Depreciação Acumulada",
                        color="Ocorrências",
                        color_continuous_scale=px.colors.sequential.Teal, 
                    )
            fig.update_layout(
                        title_font=dict(size=20, family="Arial, sans-serif", color="black"),
                        margin=dict(t=40, l=10, r=10, b=10),  
                        paper_bgcolor="white",  
                        plot_bgcolor="white",
                        treemapcolorway=["#005f73", "#0a9396", "#94d2bd", "#e9d8a6", "#ee9b00"],  # Cores elegantes
                    )
            
            fig.update_traces(
                        textinfo="label+percent entry", 
                        hovertemplate="<b>%{label}</b><br>Ocorrências: %{value}<br>Proporção: %{percentParent:.1%}",
                        marker=dict(line=dict(width=1, color='black')) 
                    )
            img0 =st.columns([1, 3, 1], gap='small', vertical_alignment="center")
            with img0[1]:
                st.plotly_chart(fig)

@st.fragment()
def _vis_004(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if existe_tabela('RESUMO_BB', bd):
            st.html(f"""<h2 style="text-align: center;font-size: 30px;">
                        Resumo da Base Blindada, após Movimentação</h2>
                        <p  style="text-align: justify;text-indent: 40px">Avalie os resultados para
                    o resumo da base blindada. Abaixo é apresentado apenas os resultados, leia o relatório 
                    de Cálculos para análise completa.</p>
                    """)
            
            sSQL = """SELECT * FROM RESUMO_BB"""
            ANL_LST_TUC = pd.read_sql(sSQL, bd)

            for n in ANL_LST_TUC.columns.to_list():
                if n[:2].upper() in ['VL', 'QT', 'DI']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab0 =st.columns([1, 5, 1], gap='small', vertical_alignment="center")
            with tab0[1]:
                st.dataframe(ANL_LST_TUC, width='stretch', hide_index=True)

@st.fragment()
def _vis_005(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if (existe_tabela('BP_COMP', bd)):
            if existe_tabela('RESUMO_BB', bd):
                st.html(f"""<h2 style="text-align: center;font-size: 30px;">
                            Evolução no tempo de baixas</h2>
                            """)
                if existe_tabela('ANL_BB_CMP', bd):
                    st.html("""
                            <p  style="text-align: justify;text-indent: 40px">A primeira 
                            análise é observar a distribuição em quantidade e valor das baixas,
                            por ano civil consolidado, apresentadas nas visões contábil e laudo. 
                            Usa-se um heatmap para visão geral. Esperamos uma concentração maior
                            em UC de redes (condutores e postes e transformadores de distribuição), 
                            concentrados nos anos iniciais da análise. É possível que no laudo tenha
                            datas muito antigas, investigar os motivos, caso aconteça.
                            </p><br>
                            """)
    
                    BAIXAS = importar_dados("BAIXAS", bd, empresa, ['VL', 'QT'], 'FLG_AJST_CTB', '0')
                    BAIXAS['Dt_Imob'] = pd.to_datetime(BAIXAS['Dt_Imob'], errors='coerce')
                    BAIXAS = BAIXAS.rename(columns={'Dt_Baixa': 'Dt_BX', 'Cd_UNID_AIS': 'Cd_UND_AIS'})
                    try:
                        BAIXAS['Dt_BX'] = pd.to_datetime(BAIXAS['Dt_BX'], errors='coerce')
                    except:
                        BAIXAS['Dt_BX'] = pd.to_datetime(BAIXAS['Dt_Baixa'], errors='coerce')
                        BAIXAS = BAIXAS.drop(columns="Dt_Baixa")
    
                    BAIXAS_INC = BAIXAS[BAIXAS['Dt_Imob'] >= pd.Timestamp(st.session_state.dt_ini)]
                    BAIXAS_BB = BAIXAS[BAIXAS['Dt_Imob'] < pd.Timestamp(st.session_state.dt_ini)]
    
                    sSQL = """
                        SELECT 
                                Id_SEQ_PP, 
                                Cd_CICLO, 
                                Id_AIS, 
                                Cd_PAT_LAUDO, 
                                Cd_ODI, 
                                Cd_SubODI, 
                                Cd_CC, 
                                Nr_TI, 
                                Nr_CM, 
                                Nr_TUC,
                                Nr_A1, 
                                Nr_A2, 
                                Nr_A3, 
                                Nr_A4, 
                                Nr_A5, 
                                Nr_A6, 
                                Cd_UAR, 
                                Cd_UC, 
                                COD_ITEM, 
                                Txt_DESC_TECN, 
                                Qtd_AIS,
                                Cd_UND_AIS, 
                                VL_VOC, 
                                VL_DEP_ACUM, 
                                Dt_Lcmto, 
                                FLG_ELIG, 
                                Cd_CONC, 
                                Cd_Q5, 
                                Cd_Q7,
                                Dt_REF_DADOS_ANT, 
                                Id_BX_INC, 
                                Qtd_AISa, 
                                VL_VOCa, 
                                FLG_ELIG_AT, 
                                QTD_BXS_INF, 
                                VL_VNR_CA_BX FROM ANL_BB_CMP
    
                        """
                    BBcmp = pd.read_sql(sSQL, bd)
    
                    BBanl = BBcmp[(BBcmp['QTD_BXS_INF'] != 0) | (BBcmp['VL_VNR_CA_BX'] != 0)].copy()
                    BBanl = BBanl.fillna(0)
                    BBanl['QTD_BX'] = BBanl['Qtd_AISa'] - BBanl['Qtd_AIS']
                    BBanl['VOC_BX'] = BBanl['VL_VOCa'] - BBanl['VL_VOC']
    
                    BXS_CNL = BAIXAS_BB.groupby(['Nr_TUC','Cd_UAR','Cd_UND_AIS','Dt_Imob','Dt_BX'],
                                        dropna=False)[['Qtd_INI', 'Qtd_FIN','VL_VOC_INI',
                                                        'VL_VOC_FIN']].sum().reset_index()
                    BXS_CNL['QTD_BX'] = BXS_CNL['Qtd_FIN'] - BXS_CNL['Qtd_INI']
                    BXS_CNL['VOC_BX'] = BXS_CNL['VL_VOC_FIN'] - BXS_CNL['VL_VOC_INI']
                    BXS_CNL['Dt_Imob'] = pd.to_datetime(BXS_CNL["Dt_Imob"], errors='coerce').dt.date
                    BBanl['Dt_Lcmto'] = pd.to_datetime(BBanl["Dt_Lcmto"], errors='coerce').dt.date
    
                    teste = BXS_CNL.groupby(['Nr_TUC', 'Dt_Imob'], dropna=False)[["QTD_BX", "VOC_BX"]].sum().reset_index()
                    teste1 = BBanl.groupby(['Nr_TUC', 'Dt_Lcmto'], dropna=False)[["QTD_BX", "VOC_BX"]].sum().reset_index()
                    cols = st.columns([.05,.05,.8,.05,.05], gap='small')
                    with cols[2]:
                        escol = st.radio(
                                    "Defina o tipo de análise",
                                    ["QTD_BX", "VOC_BX"]
                                )
                    if escol:
                        pivot_df = teste.pivot(index='Nr_TUC', columns='Dt_Imob', values=escol)
                        fig = go.Figure(
                                            data = go.Heatmap(
                                                z=pivot_df.values,  
                                                x=pivot_df.columns,  
                                                y=pivot_df.index,    
                                                colorscale="electric",  
                                                colorbar=dict(title="Valor"),
                                            )
                                        )
                        fig.update_layout(
                                            title=f"BAIXAS CONTÁBEIS DECLARADAS: {'Quantidades baixadas' if escol == 'QTD_BX' else 'Valores baixados'}",
                                            xaxis_title="Ano de Baixa",
                                            yaxis_title="UC",
                                            font=dict(family="Calibri", size=12),
                                            template="plotly_white"
                                        )
                        st.plotly_chart(fig)
                        pivot_df1 = teste1.pivot(index='Nr_TUC', columns='Dt_Lcmto', values=escol)
                        fig1 = go.Figure(
                                            data = go.Heatmap(
                                                z=pivot_df1.values,  
                                                x=pivot_df1.columns,  
                                                y=pivot_df1.index,    
                                                colorscale="electric",  
                                                colorbar=dict(title="Valor"),
                                            )
                                        )
                        fig1.update_layout(
                                                title=f"BAIXAS LAUDO DECLARADAS: {'Quantidades baixadas' if escol == 'QTD_BX' else 'Valores baixados'}",
                                                xaxis_title="Ano de Baixa",
                                                yaxis_title="UC",
                                                font=dict(family="Calibri", size=12),
                                                template="plotly_white"
                                            )
                        st.plotly_chart(fig1)
    
                    LST_TUC = BXS_CNL['Nr_TUC'].drop_duplicates().to_list()
                    LST_TUC = sorted(LST_TUC)
                    st.html("""
                            <p  style="text-align: justify;text-indent: 40px">Também podemos
                            observar as baixas por UC, e ano, na perspectiva do laudo e da
                            contabilidade. Em tese, elas devem ser muito próximas. Caso não, sugere-se
                            investigar.
                            </p><br>
                            """)
    
                    col1s = st.columns([.05,.05,.8,.05,.05], gap='small')
                    with col1s[2]:
                        escol1 = st.selectbox(
                                                "Escolha a UC a ser analisada",
                                                tuple(LST_TUC),
                                                index=None,
                                                placeholder="UC...",
                                            )
                    dt_ini_datetime = datetime.datetime.combine(st.session_state.dt_ini, datetime.datetime.min.time())
                    if escol1:
                        dados1 = BXS_CNL[(BXS_CNL['Nr_TUC'] == escol1) 
                                            & (BXS_CNL['Cd_UAR'] != 'UAR')].copy()
                        dados1 = dados1.sort_values(by='Dt_Imob')
                        dados1['ACUM'] = dados1['QTD_BX'].cumsum()
    
                        dados2 = BBanl[(BBanl['Nr_TUC'] == escol1) 
                                        & (BBanl['Cd_UAR'] != 'UAR')].copy()
                        dados2 = dados2.sort_values(by='Dt_Lcmto')
                        dados2['ACUM'] = dados2['QTD_BX'].cumsum()
                        x = -100
                        if len(dados2) != 0:
                            x = (dados2.iloc[-1,-1] - dados1.iloc[-1,-1])/dados2.iloc[-1,-1] * 100 if dados2.iloc[-1,-1] !=0 else 'ND'
                        fig2 = go.Figure()
                        fig2.add_trace(go.Scatter(x=dados2["Dt_Lcmto"], y=abs(dados2['ACUM']), 
                                                    fill='tozeroy', mode='none', 
                                                    name='Baixas da UC, Laudo'))
                        fig2.add_trace(go.Scatter(x=dados1["Dt_Imob"], y=abs(dados1['ACUM']), 
                                                    fill='tozeroy', mode='none', 
                                                    name='Baixas da UC, Contábil'))
                        # Configuração do layout
                        fig2.update_layout(title = f'Evolução das baixas no tempo da UC {escol1}.',
                                        xaxis_title='Ano',
                                        yaxis_title='Quantidade')
                        fig2.update_layout(xaxis=dict(range=[datetime.datetime(1950, 1, 1), dt_ini_datetime]))
                        if x == -100:
                            fig.add_annotation(
                                x=1,
                                y=1.0,
                                xref="paper",
                                yref="paper",
                                text=f"Deveria ter baixas no laudo, porque não ocorreu?",
                                showarrow=False
                            )
                        else:
                            a = f"{x:.2f}".replace(".",",")
                            fig2.add_annotation(
                                x=1,
                                y=1.0,
                                xref="paper",
                                yref="paper",
                                text=f"A baixa do laudo é {a}% {'acima' if x>0 else 'abaixo'} da contábil, referência laudo",
                                showarrow=False
                            )
                        st.plotly_chart(fig2)
    
                        LST_CICLOS = dados2['Cd_CICLO'].drop_duplicates().to_list()
                        LST_CICLOS = sorted(LST_CICLOS)
                        st.html("""
                            <p  style="text-align: justify;text-indent: 40px">Por fim, apresentamos
                                a distribuição das baixas por ciclo, na perspectiva do laudo.
                            </p><br>
                            """)
                        
                        esquema_cores = {
                                            'BB1': 'rgba(0,0,128,0.5)',
                                            'BB2': 'rgba(65,105,225,0.5)', 
                                            'BB3': 'rgba(30,144,255,0.5)',
                                            'BB4': 'rgba(100,149,237,0.5)',
                                            'BB5': 'rgba(135,206,235,0.5)',
                                            'BB6': 'rgba(0,191,255,0.5)',
                                            'BB7': 'rgba(0,0,128,0.5)'
                                        }
                        fig3 = go.Figure()
                        for i in LST_CICLOS:
                            dados3 = BBanl[(BBanl['Nr_TUC'] == escol1) & 
                                            (BBanl['Cd_UAR'] != 'UAR')].copy()
                            dados3 = dados3.sort_values(by='Dt_Lcmto')
                            
                            dados3['New_Value'] = dados3.apply(lambda x : x['QTD_BX'] if (x['Cd_CICLO'] == i) else np.nan, axis=1)
                            c = dados3['New_Value'].cumsum()
                            dados3['ACUM'] = c.mask(dados3['Cd_CICLO'] != i).ffill()
                            fig3.add_trace(go.Scatter(x=dados3["Dt_Lcmto"], y=abs(dados3['ACUM']), fill='tonexty', mode='none',
                                                    line=dict(color=esquema_cores.get(i, 'rgba(0, 0, 0,0.1)')),
                                                    fillcolor=esquema_cores.get(i, 'rgba(0, 0, 0, 0.1)'),
                                                    stackgroup='one', name= f"Baixas da UC, {i}"))
                    
                        fig3.update_layout(title = f'Evolução das baixas no tempo da UC {escol1}, visão do laudo, por ciclo.',
                                        xaxis_title='Ano',
                                        yaxis_title='Quantidade',
                                        showlegend=True,  
                                        legend=dict(
                                        title="Ciclo de revisão",
                                        orientation="v")
                                    )
                        st.plotly_chart(fig3)

def visualizador_BB(st = None):
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
                <h2>Análise da Blindada</h2>
                <hr>

                <h3>Observações iniciais</h3>
                <div style="text-align: justify; text-indent: 40px;">
                    Esse é um documento base para se executar análise da base blindada. 
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

                <hr>

                <h3>Normas</h3>
                <div style="text-align: justify;text-indent: 40px; padding-top: 10px">
                Conforme PRORET 2.3, item 3.2.1, deve ser executado o seguinte:<p></p></div>

                <p style='text-align: justify; padding-left:60px;'><i>a) Devem ser expurgadas da base blindada 
                as baixas ocorridas entre as datas-bases da revisão tarifária anterior e 
                da atual.</i></p>

                <p style='text-align: justify; padding-left:60px;'><i>b) após a exclusão dessas baixas, os 
                valores remanescentes de cada bem da base blindada devem ser atualizados,
                    ano a ano, pela variação do IPCA.</i></p>

                <p style='text-align: justify; padding-left:60px;'><i>d) deve ser levado em consideração o
                    efeito da depreciação acumulada ocorrida entre as datas-bases da revisão
                    tarifária anterior e a atual, obtendo-se o valor da base de remuneração 
                blindada atualizada.</i></p>

                <p style='text-align: justify; padding-left:60px;'><i>e) os Índices de Aproveitamentos – IA,
                    referentes aos bens da base blindada, deverão ser revistos, conforme 
                critérios estabelecidos neste Submódulo.</i></p>
                <a href="https://www.gov.br/aneel/pt-br/centrais-de-conteudos/procedimentos-regulatorios/proret">Visite o sitio da Aneel para mais detalhes!</a>
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
