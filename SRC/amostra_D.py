import streamlit as st, os
import sqlite3 as sl
from pathlib import Path
from SRC.calculos import (
                        sorteio, 
                        tst_cod_sisbase
                        )
from UTILS import (
                    importar_dados_duckdb, 
                    max_arq,
                    exportar_texto,
                    enc_outliers,
                    bsc_dados_reg,
                    existe_tabela
                  )
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from RELATORIOS import imprimi_F0_AMS
from datetime import date
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

@st.fragment
def relatorio(dir_nome: str = None, con: sl.Connection = None, empresa: str = None, st = None, num_A = 0, num_B = 0):
    n = imprimi_F0_AMS(dir_nome, con, empresa, st, num_A, num_B)
    return n

@st.fragment
def analises_ti(st = None, LST_TI = [], dd_SORT = None):
    cols = st.columns([1,2,1], gap='small')
    with cols[1]:
        at = st.selectbox(
                            "Selecione a TI para avaliar",
                            tuple(LST_TI),
                            1
                        )
    
    if at:
        Q1 = dd_SORT[dd_SORT['Nr_TI']==at]["VL_VOC"].quantile(0.25)
        Q3 = dd_SORT[dd_SORT['Nr_TI']==at]["VL_VOC"].quantile(0.75)
        IQR = Q3 - Q1

        df_FILT = enc_outliers(dd_SORT[dd_SORT['Nr_TI']==at], 'Nr_TI', 'VL_VOC')
        fig1 = make_subplots(
                                rows=2, cols=2,
                                subplot_titles=("COMPLETO", 
                                                "SEM OUTLIERS", 
                                                "SOMENTE OUTLIERS", 
                                                ""),
                            )
        
        fig1.add_trace(go.Violin(
                                y=dd_SORT[dd_SORT['Nr_TI'] == at]['VL_VOC'],
                                box_visible=True,
                                points="all",
                                name="Completo",
                                hoverinfo="y+name",
                            ), row=1, col=1)

        fig1.add_trace(go.Violin(
                                    y=df_FILT[df_FILT['FLG_OUTLIER'] == 0]['VL_VOC'],
                                    box_visible=True,
                                    points="all",
                                    name="Sem OUTLIERS",
                                    hoverinfo="y+name",
                                ), row=1, col=2)

        fig1.add_trace(go.Violin(
                            y=df_FILT[df_FILT['FLG_OUTLIER'] == 1]['VL_VOC'],
                            box_visible=True,
                            points="all",
                            name="Somente OUTLIERS",
                            hoverinfo="y+name",
                        ), row=2, col=1)

        fig1.update_layout(
                            yaxis_title="VL_VOC",
                            xaxis_title="Nr TI",
                            template="plotly_white",
                            width=800,
                            height=800,
                            showlegend=False,
                        )
        _, col2, _ = st.columns([1,2,1], gap ="large")
        with col2:
            st.plotly_chart(fig1)


def AMOSTRAS_D():
    if not 'tra_dir' in st.session_state:
        st.html("""
                    <div class="mensagem_tipo_1">
                        <p class="mensagem-fade-in">
                            Você deve configurar o diretório de trabalho na aba 
                            <i>Criar Pasta de Trabalho</i>, barra lateral.
                        </p>
                    </div>
                """)
        return
    
    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
    st.html(f"<style>{css}</style>")
    FLG_INTERCALAR = False
    raiz = Path(local)
    caminho_manifesto = raiz / "MANIFESTO" / "TRILHA_EXEC" / "execucoes.db"
    caminho_manifesto.parent.mkdir(parents=True, exist_ok=True)
    inicializa_database(str(caminho_manifesto))
    inicializa_detalhes(str(caminho_manifesto))
    inicializar_rastreamento(str(caminho_manifesto))
    database = str(caminho_manifesto)

    if st.session_state.dt_fim >= date.today():
        FLG_INTERCALAR = True

    st.html(f"""<h1>Amostragem de projetos</h1><br><br>""")
    if FLG_INTERCALAR:
        st.warning("""Trata-se de período intercalar.""")
    st.divider()
    cols = st.columns(5, gap='small')
    with cols[2]:
        refazer = st.button("Refazer Amostragem", key="amostragem")
    st.divider()
    
    bd_str = f'{local}\BD_LOCAL\{empresa}_{ano}.db'

    with sl.connect(bd_str) as bd:
        df_AIS, erros_AIS = importar_dados_duckdb("AIS", bd, empresa, ['VL', 'QT'], st=st)

    if len(erros_AIS)>0:
        st.html('<p  style="text-align: justify;text-indent: 40px">Avalie os erros a seguir:</p>')
        st.dataframe(erros_AIS, width='stretch', hide_index=True)


    if not FLG_INTERCALAR:
        with sl.connect(bd_str) as bd:
            df_INC, erros_INC = importar_dados_duckdb("INCR", bd, empresa, ['VL', 'QT'], st=st)
            if len(df_INC) == 0:
                dt_ARQ = max_arq("INCR", bd, empresa)
                if dt_ARQ:
                    df_INC = pd.read_sql(f"SELECT * FROM INCR WHERE dt_ARQ = '{dt_ARQ}'", bd)
                    for nm in df_INC.columns:
                        if nm[:2].upper() in ['VL', 'QT']:
                            df_INC[nm] = pd.to_numeric(df_INC[nm].str.replace("-","0"))
                else:
                    raise UserWarning("Problema na leitura do INCR")
    else:
        df_INC = df_AIS[df_AIS['FLG_PER'] == '1'][['Cd_SubODI', 'Nr_TI', 'VL_VOC']]
        df_INC['Cd_TP_AVAL'] = '1'
        df_INC['VL_VNR_UC'] = df_INC['VL_VOC']

    with sl.connect(bd_str) as bd:
        df_ROS, erros_ROS = importar_dados_duckdb("ROS", bd, empresa, ['VL', 'QT'], st=st)
        if len(df_ROS) == 0:
            dt_ARQ = max_arq("ROS", bd, empresa)
            if dt_ARQ:
                df_ROS = pd.read_sql(f"SELECT * FROM ROS WHERE dt_ARQ = '{dt_ARQ}'", bd)
            else:
                raise UserWarning("Problema na leitura do ROS")
    

    if len(df_AIS)==0:
        st.text("AIS")
        st.write(df_AIS)
        st.text("ROS")
        st.write(df_ROS)
        raise UserWarning("PROBLEMAS DE LEITURA")

    if 'Cd_Tipo_OE' not in df_ROS.columns:
        df_ROS['Cd_Tipo_OE']='0'
    
    df_ROS = df_ROS[df_ROS['Cd_Tipo_OE']=='3'].copy()
    if len(df_ROS):
        LST_SUBROGACAO = df_ROS['Cd_SubODI'].drop_duplicates().to_list()
    else:
        LST_SUBROGACAO = None

    df_AIS['Cd_CC'] = df_AIS['Cd_CC'].astype(str)
    df_BRR_BAR = bsc_dados_reg("tbl_CNTB")
    df_AIS = df_AIS[df_AIS['FLG_PER'].isin([1,'1'])]
    
    try:                                         
        df_INC = df_INC[(df_INC['FLG_ELIG'].fillna(0).astype(str)=='1') & (df_INC['Cd_CONC'].astype(str).isin(['1','3']) )].copy()
    except:
        df_INC = df_AIS[df_AIS['FLG_PER'] == '1'][['Cd_CC', 'Cd_SubODI', 'Nr_TI', 'Cd_UAR',
                                                'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 
                                                'Nr_A5', 'Nr_A6', 'VL_VOC']]
        
        df_INC['Cd_SISBASE'] = "ND"
        LST_TUC = df_INC[(df_INC['Cd_UAR'] != 'UAR')][['Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                                'Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_SISBASE']].drop_duplicates()
        LST_TUC = tst_cod_sisbase(LST_TUC, st.session_state.dt_fim)
        df_INC = df_INC.merge(LST_TUC, how='left', on = ['Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                                        'Nr_A3','Nr_A4','Nr_A5','Nr_A6',
                                                        'Cd_SISBASE'])
        df_INC['Cd_TP_AVAL'] = '1'

        INFRA = bsc_dados_reg("TBL_TUC_INFRA")
        ORCAM = bsc_dados_reg("TBL_TUC_ORC")
        tbl_CNTB = bsc_dados_reg("tbl_CNTB")

        lst_OE = ORCAM[ORCAM['Nr_A1'] == 0]['Nr_TUC'].drop_duplicates().tolist()
        lst_CNT_OE = tbl_CNTB[tbl_CNTB['Nm_RZ_ANAL'] == 
                    'Edificações, obras civis e benfeitorias']['Cd_CC'].drop_duplicates().tolist()
        df_INC.loc[df_INC['Nr_TUC'].isin(lst_OE) & 
                df_INC['Cd_CC'].isin(lst_CNT_OE), 'Cd_TP_AVAL'] = '4'
        df_INC.loc[df_INC['Cd_SISBASE_SFF'].notnull() & df_INC['Cd_SISBASE_SFF'] != "ND", 'Cd_TP_AVAL'] = '2'
        df_INC.groupby(by=['Cd_SubODI','Nr_TI','Cd_TP_AVAL'], dropna=False)['VL_VOC'].sum().reset_index()
        df_INC['VL_VNR_UC'] = df_INC['VL_VOC']

    df_AIS = df_AIS.merge(df_BRR_BAR, how='left', on = 'Cd_CC')
    lista_CC_EST = df_AIS[df_AIS['Nm_CLASS'].isnull()]['Cd_CC'].drop_duplicates().to_list()

    dd_SORT = df_INC[['Cd_SubODI','Nr_TI','Cd_TP_AVAL','VL_VNR_UC', 'VL_VOC']].copy()
    dd_SORT['Cd_SubODI'] = dd_SORT['Cd_SubODI'].str.lstrip('0')

    df_RES = dd_SORT.groupby('Cd_TP_AVAL', dropna=False)[['VL_VNR_UC','VL_VOC']].sum().reset_index()

    TP_AVAL_significado = {
                                '1': 'Atualizado',
                                '2': 'BPR',
                                '3': 'BPC',
                                '4': 'Orçamento',
                                '5': 'BPC-PLPT'
                            }
    
    df_RES['Cd_TP_AVAL'] = df_RES['Cd_TP_AVAL'].replace(TP_AVAL_significado)
    LST_TI = sorted(dd_SORT['Nr_TI'].drop_duplicates().to_list())

    st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Antes de discutirmos
                    a amostragem é interessante observamos as distribuições dos investimentos
                    por TI. Nessa análise vamos observar a base completa, a base sem
                    outliers e a base somente com os outliers. Iremos usar a representação
                    do tipo violino que permite para análise de distribuição de dados. Combina 
                    as funcionalidades de um histograma (distribuição) com um box-plot 
                    (estatísticas descritivas), oferecendo uma visão interessante para observar
                    outliers, a concentração dos projetos por valor, comportamento de extremos,
                    variabilidade dos dados, concentração, etc. Use os gráficos para entender
                    como as obras se distribuem.</p>
                    """)

    analises_ti(st, LST_TI, dd_SORT)

    with sl.connect(bd_str) as bd:
        if (not existe_tabela('tbl_anl_outliers', bd)) or refazer:
            with execucao_trilha(
                            db_path=database, script_nome="Seleção de amostras para a pasta de obras",
                            parametros={"empresa": empresa, "ano": ano, "populacao" : len(df_AIS)},
                         ) as execucao_id:
                vx_ID = execucao_id
                registrar_evento(database, execucao_id, "Avaliando OUTLIERS AIS, TI vs VOC",
                                mensagem=f"Iniciando importação de {len(df_AIS)} arquivo(s)")
                df_AIS = enc_outliers(df_AIS, 'Nr_TI', 'VL_VOC')
                df_AIS.to_sql("tbl_anl_outliers", bd, if_exists='replace', index=False)
        else:
            df_AIS = pd.read_sql("SELECT * FROM tbl_anl_outliers", bd)

    a = len(df_AIS[df_AIS['FLG_OUTLIER'] == 1])
    st.html(f"""<p  style="text-align: justify;text-indent: 40px">A seguir apresentamos as obras,
                por TI, das consideradas como outliers ({a} obras):</p><br>
                    """)
    df_FILT = df_AIS.copy()
    for n in ['VL_VOC','VL_VNR_UC']:
        if n in df_AIS.columns:
            df_FILT[n] = df_FILT[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.dataframe(df_FILT[df_FILT['FLG_OUTLIER'] == 1], width='stretch', hide_index=True)

    if (a/len(df_AIS)>0.01):
        lst_INC = [0,1]
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">A proporção de outliers é alta e
                    indica que os dados possuem uma grande dispersão ou distribuição incomum, 
                    como caudas longas (distribuição não normal). Como estamos tratando de operações de
                    investimento, as obras podem ser muito maiores ou menores do que a média, tanto em valor 
                    quanto em unidades físicas. Nesse sentido avalie a lista e caso entenda que esteja dentro do 
                    esperado, isto é, nenhuma obra parece ser diferente do usual, não altere a amostra gerada. Caso 
                    contrário, agregue a obra à lista de amostras para análise. Por enquanto, não iremos excluir as
                    obras por entendermos não ser outliers.
                    </p>
                    """)
    else:
        lst_INC = [0]
        st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie os outliers, além das
                    obras selecionadas a seguir.
                    </p>
                    
                    <p  style="text-align: justify;text-indent: 40px">Outro fator de atenção é o critério
                de valoração. O VOC ou é critério de valoração ou é usado como referencial para limitar
                os outros critérios. Considerando que alguns dados são regulatórios é possível que a empresa
                faça um deslocamento de valores de investimento para operacional. Nesse sentido, chamamos a atenção
                para que se avalie nas amostras que estejam empregando um método de valoração que não
                o VOC atualizado, se ocorreu deslocamento de investimento para operacional. Ademais, a base incremental possui
                a seguinte distribuição, em valor novo de reposição, VNR, por tipo de avaliação:</p>
                    """)
    fig = px.pie(
                    df_RES,
                    names='Cd_TP_AVAL',
                    values='VL_VNR_UC',
                    title=f"Distribuição do VNR - Empresa {empresa}",
                    color_discrete_sequence=px.colors.sequential.Teal 
                )
    fig.update_traces(
                        textinfo='percent+label', 
                        hoverinfo='label+value+percent',  
                        pull=[0.1 if v == max(df_RES['VL_VNR_UC']) else 0 for v in df_RES['VL_VNR_UC']],  
                        marker=dict(line=dict(color='white', width=2)) 
                    )

    fig.update_layout(
                        title=dict(
                            text=f"Distribuição do VNR - Empresa {empresa}",
                            font=dict(size=15, family="Arial, sans-serif", color="black"),
                            x=0, 
                            y=0.95
                        ),
                        legend=dict(
                            title="Categorias",
                            font=dict(size=12, family="Arial"),
                            orientation="h", 
                            x=0.5,
                            y=-0.1,
                            xanchor="center",
                            yanchor="top"
                        ),
                        margin=dict(t=50, b=50, l=50, r=50),
                        showlegend=True,
                        template="plotly_white"
                    )
    _, col2a, _ = st.columns([1,2,1], gap = "large")
    with col2a:
        st.plotly_chart(fig)

    if len(lst_INC)<=1:
        df_AIS = df_AIS[df_AIS['FLG_OUTLIER'].isin(lst_INC)].copy()

    M = df_AIS['VL_VOC'].sum() 
    p = 0.05   
    MR = p * M 

    M_esc = f"{M:,.2f}".replace(".","x").replace(",", ".").replace("x",",")
    MR_esc = f"{MR:,.2f}".replace(".","x").replace(",", ".").replace("x",",")
    p_esc = f"{p:,.2%}".replace(".","x").replace(",", ".").replace("x",",")
    
    st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Para isso empregaremos a 
                    <b>Amostragem por Unidade Monetária</b>,
                    metodologia utilizada em auditorias financeiras para assegurar a 
                    confiabilidade dos registros contábeis, utilizando princípios estatísticos 
                    baseados na distribuição hipergeométrica ou binomial. Essa técnica é 
                    eficaz para identificar erros ou distorções em registros de 
                    maior valor monetário, conferindo maior peso às transações de maior 
                    relevância. Assim, aplicaremos essa abordagem para avaliar a conformidade 
                    dos registros do AIS, considerando um nível de confiança de 95% e 
                    estabelecendo a proporção máxima de erros aceitáveis para determinar a 
                    aprovação do AIS apresentado. O conjunto de lançamentos contábeis, {empresa},
                    totalizou R$ {M_esc}. A diferença máxima estimada é de R$ {MR_esc}, que 
                    representa {p_esc} de erro. Assim, o número de amostras, considerando que
                    a quantidade de erros previstas é zero, possuindo um índice de confiabilidade
                    de 3, é dada por:</p>
                    """)
    
    texto = f"""
                <p style="text-align: justify;text-indent: 40px"> Para a primeira fase de 
                    amostragem, empregamos AUM e utilizamos princípios estatísticos baseados na distribuição 
                    hipergeométrica ou binomial para definição das amostras. Essa técnica é 
                    eficaz para identificar erros ou distorções em registros de 
                    maior valor monetário, conferindo maior peso às transações de maior 
                    relevância. Assim, aplicaremos essa abordagem para avaliar a conformidade 
                    dos registros do AIS, considerando um nível de confiança de 95% e 
                    estabelecendo a proporção máxima de erros aceitáveis para determinar a 
                    aprovação do AIS apresentado. O conjunto de lançamentos contábeis, {empresa},
                    totalizou R$ {M_esc}. A diferença máxima estimada é de R$ {MR_esc}, que 
                    representa {p_esc} de erro. Assim, o número de amostras, considerando que
                    a quantidade de erros previstas é zero, possuindo um índice de confiabilidade
                    de 3, é dada por:</p>
                    <INSERIR>equacao2.png</INSERIR>
            """
    
    st.markdown(
                    """
                        $$
                        \large
                        n = \\frac{C_{i,\\alpha}}{p} = \\frac{3}{0,05} = 60 
                        $$
                    """,
                    unsafe_allow_html=True
                )

    df_AIS_SORT = df_AIS[(df_AIS['Nm_CLASS'] == 'BRR')].reset_index(drop=True).copy()
    with sl.connect(bd_str) as bd:
        df_ROA, erros_ROA = importar_dados_duckdb("ROA", bd, empresa, ['VL', 'QT'], itens = "Cd_SubODI, Nr_TI, VL_tot", st=st)

    df_AIS_SORT = df_ROA[df_ROA['Cd_SubODI'].isin(df_AIS_SORT['Cd_SubODI'].drop_duplicates().to_list())].copy()

    A = df_ROA['Cd_SubODI'].drop_duplicates().to_list()
    B = df_AIS['Cd_SubODI'].drop_duplicates().to_list()
    faltando_em_B = list(set(A) - set(B))
    faltando_em_A = list(set(B) - set(A))
    itens_htmlB = ", ".join([f"{item}" for item in faltando_em_B])
    itens_htmlA = ", ".join([f"{item}" for item in faltando_em_A])
    if (len(itens_htmlB) + len(itens_htmlA)) > 0:
        st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Importante avaliarmos se houve ausências no AIS ou no ROA. A
                seguir sumarizamos os dados.</p>
                    """)

    if len(itens_htmlB) > 0:
        texto_html = f"""
                        <div style="background-color: #ffdde1; padding: 15px; border-left: 5px solid #ff4b4b; border-radius: 4px;">
                            <strong style="color: #ff4b4b; font-size: 16px;">Atenção: Os seguintes itens estão em falta no AIS (presentes no ROA):</strong>
                            <ul style="margin-top: 10px; color: #333333; font-weight: 500;">
                                {itens_htmlB}
                            </ul>
                        </div>
                        """
        st.html(texto_html)
    if len(itens_htmlA) > 0:
        texto_html = f"""
                        <div style="background-color: #ffdde1; padding: 15px; border-left: 5px solid #ff4b4b; border-radius: 4px;">
                            <strong style="color: #ff4b4b; font-size: 16px;">Atenção: Os seguintes itens estão em falta no ROA (presentes no AIS):</strong>
                            <ul style="margin-top: 10px; color: #333333; font-weight: 500;">
                                {itens_htmlA}
                            </ul>
                        </div>
                        """
        st.html(texto_html)

    df_AIS_SORT = df_AIS_SORT.rename(columns={'VL_tot':'VL_VOC'})
    df_AIS_SORT["Nr_TI"] = df_AIS_SORT["Nr_TI"].fillna(0)

    with sl.connect(bd_str) as bd:
        if (not existe_tabela('tbl_PROP_amostras', bd)) or refazer:
            registrar_evento(database, vx_ID, "Avaliando quantidade de amostras por TI",
                            mensagem=f"Definindo o número de amostras por TI")
            df_LIM = df_AIS_SORT.groupby(["Nr_TI"], dropna=False)['VL_VOC'].count().reset_index()
            df_LIM =  df_LIM.rename(columns={'VL_VOC': 'LIMITE'})
            df_PROP = df_AIS_SORT.groupby(["Nr_TI"], dropna=False)['VL_VOC'].sum().reset_index()
            df_PROP['n'] = np.ceil(df_PROP['VL_VOC'] / df_PROP['VL_VOC'].sum() * 60)
            while True:
                df_PROP = df_PROP.merge(df_LIM, on="Nr_TI", how="left")
                df_PROP['EXCESSO'] = np.maximum(df_PROP['n'] - df_PROP['LIMITE'], 0)
                df_PROP['n'] = np.minimum(df_PROP['n'], df_PROP['LIMITE'])
                excesso_total = df_PROP['EXCESSO'].sum()
                if excesso_total == 0:
                    break
                df_PROP['MARGEM'] = df_PROP['LIMITE'] - df_PROP['n']
                total_margem = df_PROP['MARGEM'].sum()
                if total_margem > 0:
                    df_PROP['REDISTRIBUIR'] = np.ceil((df_PROP['MARGEM'] / total_margem) * excesso_total)
                    df_PROP['n'] += df_PROP['REDISTRIBUIR']
                else:
                    break
                df_PROP = df_PROP.drop(columns=['MARGEM', 'REDISTRIBUIR'])

            df_PROP = df_PROP.drop(columns=['EXCESSO','LIMITE', 'VL_VOC'])
            df_PROP.to_sql("tbl_PROP_amostras", bd, if_exists='replace', index=False)
            registrar_evento(database, vx_ID, "Avaliando quantidade de amostras por TI",
                             mensagem=f"Definido o número de amostras por TI")
        else:
            df_PROP = pd.read_sql("SELECT * FROM tbl_PROP_amostras", bd)
    
    st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Vamos agora distribuir a 
                    a amostra por extratos, TI, considerando a proporção em valor, assim, temos
                    a seguinte amostra por TI:</p><br>
                    """)
    colcs = st.columns([1,2,1], gap='small')
    
    with colcs[1]:
        st.dataframe(df_PROP, width='stretch', hide_index=True)
    axTXT = "<p>Vamos agora distribuir a a amostra por extratos, TI, considerando a proporção em valor, assim, temos a seguinte amostra: "
    
    for _, row in df_PROP.iterrows():
        zz1 = f"{row['n']:,.0f}".replace(",", ".")
        axTXT += (f"para a TI '{row['Nr_TI']}' tem-se '{zz1}' amostras, ")
        axTXT = axTXT[:-2]
        axTXT += ".</p>"
        texto += axTXT
    
    df_PROV = df_AIS_SORT.groupby(['Cd_SubODI','Nr_TI'], dropna=False)['VL_VOC'].sum().reset_index()

    with sl.connect(bd_str) as bd:
        if (not existe_tabela('tbl_TI_sorteio_amostras', bd)) or refazer:
            registrar_evento(database, vx_ID, "Definindo quais projetos constituem as amostras por TI",
                            mensagem=f"Definindo quais projetos serão avaliados por TI")
            df_TI_SORTEIO = pd.DataFrame()
            lst_PRJ = []
            nm_arq_ciclo = rf"{local}/RELATORIOS/LST_OBRAS_FISC_CICLO.csv"
            if os.path.isfile(nm_arq_ciclo):
                df_projetos_avaliados_ciclo = pd.read_csv(nm_arq_ciclo, sep="|", encoding="Latin-1")
                lst_projetos_avaliados_ciclo = df_projetos_avaliados_ciclo['Cd_SubODI'].drop_duplicates().to_list()
            else:
                lst_projetos_avaliados_ciclo = []

            for n in df_PROP['Nr_TI'].to_list():  
                df_TI_SORTEIO = pd.concat([df_TI_SORTEIO,
                                    sorteio(df_PROV[df_PROV['Nr_TI']==n][['Nr_TI', 'Cd_SubODI','VL_VOC']], 
                                    'VL_VOC', ['Cd_SubODI','Nr_TI'], 
                                    df_PROP[df_PROP['Nr_TI']==n].iloc[0,-1], 42, lista_extra=LST_SUBROGACAO, sorteados=None, st = st,
                                    lista_bloqueio=lst_projetos_avaliados_ciclo)],
                                    ignore_index=True)
                if len(df_TI_SORTEIO) > df_PROP['n'].sum():
                    st.text(n)
                    st.write(df_TI_SORTEIO)
                    raise

            df_TI_SORTEIO = df_TI_SORTEIO.drop_duplicates(subset=['Cd_SubODI', 'Nr_TI'])
            
            df_TI_SORTEIO.to_sql("tbl_TI_sorteio_amostras", bd, if_exists='replace', index=False)
            registrar_evento(database, vx_ID, "Definindo quais projetos constituem as amostras por TI",
                                        mensagem=f"Amostras de projetos, que serão avaliados por TI, definidas")
        else:
            df_TI_SORTEIO = pd.read_sql("SELECT * FROM tbl_TI_sorteio_amostras", bd)    

    M_esc1 = f"{df_AIS_SORT['VL_VOC'].sum():,.2f}".replace(".","x").replace(",", ".").replace("x",",")
    p_esc1 = f"{3/len(df_TI_SORTEIO):,.2%}".replace(".","x").replace(",", ".").replace("x",",")
    MR_esc1 = f"{df_AIS_SORT['VL_VOC'].sum()*3/len(df_TI_SORTEIO):,.2f}".replace(".","x").replace(",", ".").replace("x",",")
    
    st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Assim, o conjunto de 
                    lançamentos contábeis, associados a BRR, da {empresa}, totalizou R$ 
                    {M_esc1}. Escolhemos {int(len(df_TI_SORTEIO))} amostras, sendo que a 
                    diferença máxima estimada é de R$ {MR_esc1}, que representa {p_esc1} 
                    de erro.</p>
            """)
    
    texto += f"""
                <p style="text-align: justify;text-indent: 40px">Assim, o conjunto de 
                    lançamentos contábeis, associados a BRR, da {empresa}, totalizou R$ 
                    {M_esc1}. Escolhemos {int(len(df_TI_SORTEIO))} amostras, sendo que a 
                    diferença máxima estimada é de R$ {MR_esc1}, que representa {p_esc1} 
                    de erro.</p>
            """
    st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">Abaixo temos as 
                    obras sorteadas para fins de análise em campo:</p><br>
                    """)
    df_TI_SORTEIO.columns = ['Cd_SubODI','Nr_TI','VL_VOC_TOT', "Limite_Inferior", "Limite_Superior"]

    axTXT = df_TI_SORTEIO['Cd_SubODI'].drop_duplicates().to_list()
    texto += "<p style='text-align: justify;text-indent: 40px'>As obras sorteadas são: "
    texto += ", ".join(axTXT)
    texto += "</p>"

    with sl.connect(bd_str) as bd:
        df_TI_SORTEIO.to_sql("tbl_AMOSTRAS", bd, if_exists='replace', index=False)
        df_AIS.to_sql("tbl_CLS_AIS", bd, if_exists='replace', index=False)
    
    for n in ["Limite_Inferior", "Limite_Superior", "VL_VOC_TOT"]:
        df_TI_SORTEIO[n] = df_TI_SORTEIO[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    colbs = st.columns([1,4,1], gap='small')
    with colbs[1]:
        st.dataframe(df_TI_SORTEIO, hide_index=True)
        st.download_button(
                                "Exportar CSV",
                                data=df_TI_SORTEIO.to_csv(index=False, sep="|").encode("latin-1"),
                                file_name=f"Dados_projetos_sorteados.csv",
                                mime="text/csv",
                                key=f"Dados_projetos_sorteados",
                                disabled=df_TI_SORTEIO.empty,
                            )

    total = f"{df_ROA['VL_tot'].sum():,.2f}".replace(",","x").replace(".",",").replace("x",".")
    txt_odi = ", ".join(df_TI_SORTEIO['Cd_SubODI'].unique())
    st.html(f"""
                    <p  style="text-align: justify;text-indent: 40px">O investimento total é de R$ {total}. Segue obras: <b>{txt_odi}</b></p>
                    """)
    st.divider()

    st.html("""
                <h2>Exportação para o Excel</h2>

                <hr></hr>
                                
                <div style="text-align: justify;text-indent: 40px; padding-top: 10px"><p>Exportar resultados 
                            para o Excel é feito devido à sua difusão como ferramenta de análise 
                            neste tipo de trabalho. Entendemos, nesse momento, que facilita a adoção, 
                            reduzindo a necessidade de treinamento adicional. Além disso, sua 
                            compatibilidade com diversos formatos e integração com outras aplicações 
                            garantem que os dados possam ser compartilhados e analisados. A seguir,
                            resumimos os tipos de exportação.</p></div>
                <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                            <p><b>F0</b>: O arquivo de saída SAIDA_F0_AMOSTRA, 
                            apresenta as obras a serem amostradas. O fiscal deverá preencher os campos
                            e discutir com a coordenação os resultados.</p>
                            </div>

                """)
    st.divider()
    colas = st.columns([5,2,5], gap='small')
    with colas[1]:
        F0 = st.button("Imprimir Amostras")
    st.divider()
    if F0:
        with sl.connect(bd_str) as bd:
            n = relatorio(f'{local}\RELATORIOS', bd, empresa, st,
                                    df_AIS_SORT['VL_VOC'].sum()*3/len(df_TI_SORTEIO),
                                    df_AIS_SORT['VL_VOC'].sum()*0.0025)

    texto += "<p style='text-align: justify;text-indent: 40px'>A segunda etapa deve ser executada pela credenciada. </p>"
    dir_esc = f"{local}//RELATORIOS//textos".replace("\\","/").replace("/","/")
    xEsc = exportar_texto(dir_esc, f"AMST_DESC.txt", texto, True)

        


