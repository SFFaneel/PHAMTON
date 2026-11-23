import streamlit as st
import sqlite3 as sl
import pandas as pd, os
import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
import plotly.express as px
from RELATORIOS import imprimi_F0_CRONO
from openpyxl import load_workbook
from datetime import datetime, date
from UTILS import (
                    importar_dados_duckdb, 
                    max_arq,
                    exportar_texto,
                    enc_outliers,
                    bsc_dados_reg,
                    existe_tabela
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

def matriz_mestra():
    if not 'tra_dir' in st.session_state:
        st.html("""
                        <div class="mensagem_tipo_1">
                            <p class="mensagem-fade-in">
                                Você deve configurar o diretório de trabalho na aba <i>Criar Pasta de Trabalho</i>, barra lateral.
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

    st.html("""
                <h1>Planejamento de atividades</h1>
                <br></br>
                <div style="text-align: justify; text-indent: 40px;">
                Preencha os dados a seguir com as principais informações de fiscalização.
                Após preencher ou editar, salve os dados. Caso já tenha sido executado,
                os dados serão recuperados montando a visão tabular analítica e por gráfico
                de Gantt.
                </div>
                """
                )
    
    st.divider()
    bd_path = f'{local}/BD_LOCAL/{empresa}_{ano}.db'
    with sl.connect(bd_path) as bd:
        if existe_tabela('tbl_DD_CAB', bd):
            SQLq = f"""
                        SELECT *
                        FROM tbl_DD_CAB  
                """
            df_CAB = pd.read_sql(SQLq, bd)
        else:
            dt_INI = st.session_state.dt_ini.strftime("%Y/%m/%d")
            dt_FIM = st.session_state.dt_fim.strftime("%Y/%m/%d")
            
            dic_CAB = {
                'Funcao' : ['Empresa Fiscalizada', 'Avaliadora', 'Credenciada',
                        ],
                'Dado' : [f"{empresa}","G","H"
                        ],
                'Evento' : ['Início Período Incremental','Final Período Incremental',''],
                'Data' : [dt_INI, dt_FIM, '',
                        ],
            }

            df_CAB = pd.DataFrame.from_dict(dic_CAB)    


    st.html("""<h2>Dados gerais do trabalho de revisão</h2>""")
    cntDC = st.container(border=True)
    
    with cntDC:
        config = {
                    "Data": st.column_config.TextColumn("Data Evento"),
                    "Funcao" : st.column_config.TextColumn("Informação")
                } 
        df_NVCAB = st.data_editor(df_CAB, hide_index=True, disabled=("Funcao","Evento"),
                                column_config=config, width='stretch',
                                on_change=None)
        colAs = st.columns([1,1,2,1,1], gap='small')
        with colAs[2]:
            salva1 = st.button("Salvar", key="CRON01", width='stretch')

    if salva1 and (not df_NVCAB.empty):
        with sl.connect(bd_path) as bd:
            with execucao_trilha(
                                db_path=database, script_nome="Dados_Gerais_Fiscalizacao",
                                parametros={"empresa": empresa, "ano": ano},
                                ) as execucao_id:
                registrar_evento(database, execucao_id, "Salvando_GERAIS",
                                 mensagem = "Salvo informações gerais do trabalho de fiscalização")
            df_NVCAB.to_sql('tbl_DD_CAB', bd, if_exists='replace', index=False)
            df_CAB = df_NVCAB.copy()

    st.divider()
    with sl.connect(bd_path) as bd:
        if existe_tabela('tbl_DD_GERAIS_PLAN', bd):
            SQLq = f"""
                        SELECT *
                        FROM tbl_DD_GERAIS_PLAN  
                """
            df_DG = pd.read_sql(SQLq, bd)
        else:
            if st.session_state.dt_fim >= date.today():
                dt_INI = date.today()
                dt_FIM = date.today() + relativedelta(months=2, days=1)
            else:
                dt_INI = st.session_state.dt_fim.replace(day=1) + relativedelta(months=2, days=1)
                dt_FIM = st.session_state.dt_fim.replace(day=1) + relativedelta(months=5, days=1)
            dt_INI1 = dt_INI + relativedelta(months=1)
            dt_FIM1 = dt_INI + relativedelta(months=1, days=5)
            dic_DG = {
                            'Funcao' : ['Coordenador SFF', 'Fiscal 01 SFF', 'Fiscal 02 SFF',
                                    'Credenciado Coordenador', 'Credenciado 01 AUD',
                                    'Credenciado 02 AUD',],
                            'Profissional' : ["A","B","C","D","E","F"
                                    ],
                            'Evento' : ['Início de fiscalização','Finalização de fiscalização', 'Início em campo',
                                    'Finalização em campo','',''],
                            'Data' : [dt_INI.strftime("%Y/%m/%d"), dt_FIM.strftime("%Y/%m/%d"), 
                                      dt_INI1.strftime("%Y/%m/%d"), dt_FIM1.strftime("%Y/%m/%d"),'','',
                                    ],
                        }

            df_DG = pd.DataFrame.from_dict(dic_DG)    


    st.html("""<h2>Dados gerais da equipe</h2>
                """
                )
    cntDG = st.container(border=True)
    
    with cntDG:
        config = {
                    "Data": st.column_config.TextColumn("Data Evento"),
                    "Funcao" : st.column_config.TextColumn("Função")
                } 
        df_NVDG = st.data_editor(df_DG, hide_index=True, disabled=("Funcao","Evento"),
                                column_config=config, width='stretch',
                                on_change=None)
        colBs = st.columns([1,1,2,1,1], gap='small')
        with colBs[2]:
            salva2 = st.button("Salvar", key="CRON02", width='stretch')

    
    if salva2 and (not df_NVDG.empty):
        with sl.connect(bd_path) as bd:
            with execucao_trilha(
                                db_path=database, script_nome="Dados_Gerais_Equipe",
                                parametros={"empresa": empresa, "ano": ano},
                                ) as execucao_id:
                registrar_evento(database, execucao_id, "Salvando_Equipe",
                                    mensagem = "Salvo informações de Equipe de fiscalização")
            df_NVDG.to_sql('tbl_DD_GERAIS_PLAN', bd, if_exists='replace', index=False)
        df_DG = df_NVDG.copy()

    st.divider()

    dic_MM = {
                "DISTRIBUIDORA ANUAL" : "tbl_cronograma_A2",
                "DISTRIBUIDORA PERIÓDICA" : "tbl_cronograma_A1",
                "DISTRIBUIDORA EXTRAORDINÁRIA" : "tbl_cronograma_A1",
                "TRANSMISSORA PRORROGADA" : "",
                "TRANSMISSORA LICITADA" : "",
            }

    st.html("""<h2>Dados gerais das etapas de fiscalização</h2>
               <p style="text-align: justify; text-indent: 40px;">
               Selecione o planejamento de acordo com a Matriz Mestra do ROCT.</p>""")

    default_valor = 1
    with sl.connect(bd_path) as bd:
        if (existe_tabela('tbl_PLANEJAMENTO', bd)):
            try:
                df_001 = pd.read_sql('SELECT TP_FISC FROM tbl_PLANEJAMENTO WHERE TP_FISC IS NOT NULL ORDER BY TP_FISC ASC LIMIT 1', bd)
            except:
                cursor = bd.cursor()
                cursor.execute("DROP TABLE IF EXISTS tbl_PLANEJAMENTO")
                bd.commit()
                st.rerun()
            if 'Cd_Teste' not in df_001.columns:
                cursor = bd.cursor()
                cursor.execute("DROP TABLE IF EXISTS tbl_PLANEJAMENTO")
                bd.commit()
                st.rerun()
            if not df_001.empty:
                opcao_sqlite = df_001['TP_FISC'].values[0]
                default_valor = list(dic_MM.keys()).index(opcao_sqlite)
                
    colEs = st.columns([1,1,1], gap='small')
    with colEs[0]:
        opcao_selecionada = st.radio(
                                        "Selecione Matriz Mestra para planejamento:",
                                        options=dic_MM.keys(),
                                        index = default_valor,
                                        help="Leia o ROCT para definição completa"
                                    )
    st.html(f"""<h3>Cronograma base para fiscalização de {opcao_selecionada}</h3>""")
    if dic_MM[opcao_selecionada] != "":
        with sl.connect(bd_path) as bd:
            if (not existe_tabela('tbl_PLANEJAMENTO', bd)) or salva2:
                if opcao_selecionada == "DISTRIBUIDORA ANUAL":
                    
                    if df_NVDG.iloc[0,-1] == "":
                        dt_INI = date.today()
                    else:
                        dt_INI = pd.to_datetime(df_NVDG.iloc[0,-1], format ="%Y/%m/%d")
                else:
                    dt_INI = st.session_state.dt_fim.replace(day=1) + relativedelta(months=3, days=1)
                df_PP = pd.read_csv(rf"tabelas\{dic_MM[opcao_selecionada]}.csv", sep="|", encoding="Latin-1")

                for dt in ['Dt_INI', 'Dt_FIM']:
                    df_PP[dt] = df_PP[dt].apply(lambda x: (dt_INI + pd.Timedelta(days=x)).strftime("%d/%m/%Y"))
                for cm in ['EXEC', 'REV', 'APR']:
                    df_PP[cm] = ""
                df_PP['SIT'] = False
            else:
                SQLq = f"""
                            SELECT *
                            FROM tbl_PLANEJAMENTO  
                    """
                df_PP = pd.read_sql(SQLq, bd)


        df_PP['TP_FISC'] = opcao_selecionada


        lst_exec = [''] + df_DG['Profissional'].drop_duplicates().to_list()
        lst_rev = [''] + df_DG[df_DG['Funcao'].isin(['Coordenador SFF',
                    'Credenciado Coordenador'])]['Profissional'].drop_duplicates().to_list()
        lst_apr = [''] + df_DG[df_DG['Funcao'].isin(['Coordenador SFF',
                    ])]['Profissional'].drop_duplicates().to_list()
        
        cnt = st.container(border=True)
        st.html(
                        """
                        <div style="overflow-x: auto; max-height: 800px;">
                        """
                    )
        with cnt:
            tab1, tab2 = st.tabs(["Dados do Cronograma", "Diagrama de Gantt"])
            config = {
                            'Arq_ENT' : st.column_config.TextColumn("Arquivo de Entrada de Análise"),
                            'Arq_SAI' : st.column_config.TextColumn("Arquivo de Saída de Análise"),
                            'Dt_INI' : st.column_config.TextColumn("Data de início da Análise"),
                            'Dt_FIM' : st.column_config.TextColumn("Data de término da Análise"),
                            'Dt_APR' : st.column_config.TextColumn("Data de aprovação da Análise"),
                            'EXEC' : st.column_config.SelectboxColumn("Executado por",options=lst_exec,default=""),
                            'REV' : st.column_config.SelectboxColumn("Revisado por",options=lst_rev,default=""),
                            'APR' : st.column_config.SelectboxColumn("Aprovado por",options=lst_apr,default=""),
                            'SIT' : st.column_config.CheckboxColumn("(Re)aprovado (ativo, se sim)", default=False),
                            'OBS' : st.column_config.TextColumn("Principais observações sobre os testes e resultados"),
                        }
            with tab1:
                st.subheader("Edição dos Dados do Cronograma")
                st.info("""Procure atualizar com o andamento dos trabalhos. Com isto você pode 
                        gerenciar melhor os trabalhos.""")
                df_edit = st.data_editor(df_PP, hide_index=True, disabled=("Item"),
                                    column_config=config, width='stretch',
                                    key="data_editor", num_rows="dynamic")
                
            with tab2:
                st.subheader("Diagrama de Gantt")
                st.info("""Ferramenta visual que fornece visão organizada das tarefas. Exibe linhas de tempo 
                        para cada uma das tarefas, representadas como barras horizontais, indicando
                        início e fim, a sequencialidade ou o paralelismo de atividades, a distribuição de
                        recursos (humanos, financeiros, materiais) entre as tarefas, as tarefas 
                        concluídas, em andamento e pendentes. Ainda, permite antecipar riscos devido aos atrasos de etapas ou
                        até conflitos de dependência, ajustar prazos e realocar recursos conforme necessário.""")
                
                df_GANT = df_PP.copy()
                df_GANT['Dt_INI'] = pd.to_datetime(df_GANT['Dt_INI'], format = '%d/%m/%Y', errors = 'coerce')
                df_GANT['Dt_FIM'] = pd.to_datetime(df_GANT['Dt_FIM'], format = '%d/%m/%Y', errors = 'coerce')
                df_GANT['EXEC1'] = df_GANT['SIT'].apply(lambda x: 100 if x else 0)
                df_GANT['CAT'] = df_GANT['Item'].str[:1]
                grupos = df_GANT['CAT'].unique()
                pessoas = df_GANT['EXEC'].unique()
                colDs = st.columns(2, gap='small')
                with colDs[0]:
                    ref =  st.radio(
                                        "Forma de agregação",
                                        ["Grupos de atividades", "Executor das atividades"],
                                        index=0,
                                    )
                with colDs[1]:
                    if ref == "Grupos de atividades":
                        ref1 = st.multiselect(
                                                "Selecione o grupo de atividades",
                                                options=grupos,
                                                default=grupos,
                                            )
                        cor = "EXEC1"
                        df_GRAF = df_GANT[df_GANT["CAT"].isin(ref1)]
                        txt_leg = "Execução"
                    elif ref == "Executor das atividades":
                        ref2 = st.multiselect(
                                                "Selecione o executor",
                                                options=pessoas,
                                                default=pessoas,
                                            )
                        cor = "EXEC"
                        df_GRAF = df_GANT[df_GANT["EXEC"].isin(ref2)]
                        txt_leg = "Pessoas"
                if ref:

                    hoje = pd.Timestamp.today().normalize()
                    df_GRAF["Item_Gantt"] = (
                                                df_GRAF["Item"]
                                                .astype(str)
                                                .str.extract(r"^([\d\.]+)", expand=False)
                                                .fillna(df_GRAF["Item"].astype(str))
                                            )

                    df_GRAF["Grupo"] = df_GRAF["Item_Gantt"].str.extract(r"^(\d+)", expand=False)

                    df_GRAF["Dt_INI"] = pd.to_datetime(df_GRAF["Dt_INI"])
                    df_GRAF["Dt_FIM"] = pd.to_datetime(df_GRAF["Dt_FIM"])

                    df_GRAF["DURACAO_DIAS"] = (df_GRAF["Dt_FIM"] - df_GRAF["Dt_INI"]).dt.days + 1

                    total_atividades = len(df_GRAF)
                    total_grupos = df_GRAF["Grupo"].nunique()
                    dt_ini_crono = df_GRAF["Dt_INI"].min()
                    dt_fim_crono = df_GRAF["Dt_FIM"].max()
                    prazo_total = (dt_fim_crono - dt_ini_crono).days + 1

                    ativ_em_andamento = df_GRAF[
                                                    (df_GRAF["Dt_INI"] <= hoje) & 
                                                    (df_GRAF["Dt_FIM"] >= hoje)
                                                ].shape[0]

                    ativ_vencidas = df_GRAF[df_GRAF["Dt_FIM"] < hoje].shape[0]
                    ativ_nao_iniciadas = df_GRAF[df_GRAF["Dt_INI"] > hoje].shape[0]
                    maior_atividade = df_GRAF["DURACAO_DIAS"].max()

                    st.html(f"""
                                <div style="
                                    display: grid;
                                    grid-template-columns: repeat(4, 1fr);
                                    gap: 16px;
                                    margin-bottom: 24px;
                                ">
                                    <div style="background:#ffffff; padding:18px; border-radius:16px; box-shadow:0 4px 14px rgba(0,0,0,0.06);">
                                        <div style="font-size:13px; color:#6c757d;">Atividades</div>
                                        <div style="font-size:28px; font-weight:700;">{total_atividades}</div>
                                    </div>

                                    <div style="background:#ffffff; padding:18px; border-radius:16px; box-shadow:0 4px 14px rgba(0,0,0,0.06);">
                                        <div style="font-size:13px; color:#6c757d;">Grupos/Fases</div>
                                        <div style="font-size:28px; font-weight:700;">{total_grupos}</div>
                                    </div>

                                    <div style="background:#ffffff; padding:18px; border-radius:16px; box-shadow:0 4px 14px rgba(0,0,0,0.06);">
                                        <div style="font-size:13px; color:#6c757d;">Prazo total</div>
                                        <div style="font-size:28px; font-weight:700;">{prazo_total} dias</div>
                                    </div>

                                    <div style="background:#ffffff; padding:18px; border-radius:16px; box-shadow:0 4px 14px rgba(0,0,0,0.06);">
                                        <div style="font-size:13px; color:#6c757d;">Fim previsto</div>
                                        <div style="font-size:28px; font-weight:700;">{dt_fim_crono:%d/%m/%Y}</div>
                                    </div>
                                </div>

                                <div style="
                                    display: grid;
                                    grid-template-columns: repeat(3, 1fr);
                                    gap: 16px;
                                    margin-bottom: 24px;
                                ">
                                    <div style="background:#f8f9fb; padding:16px; border-radius:14px;">
                                        <div style="font-size:13px; color:#6c757d;">Em andamento</div>
                                        <div style="font-size:24px; font-weight:700;">{ativ_em_andamento}</div>
                                    </div>

                                    <div style="background:#f8f9fb; padding:16px; border-radius:14px;">
                                        <div style="font-size:13px; color:#6c757d;">Não iniciadas</div>
                                        <div style="font-size:24px; font-weight:700;">{ativ_nao_iniciadas}</div>
                                    </div>

                                    <div style="background:#f8f9fb; padding:16px; border-radius:14px;">
                                        <div style="font-size:13px; color:#6c757d;">Concluídas/Vencidas</div>
                                        <div style="font-size:24px; font-weight:700;">{ativ_vencidas}</div>
                                    </div>
                                </div>
                                """)
                    

                    altura = max(700, len(df_GRAF) * 22)

                    fig = px.timeline(
                                        df_GRAF,
                                        x_start="Dt_INI",
                                        x_end="Dt_FIM",
                                        y="Item_Gantt",
                                        color="Grupo",
                                        hover_name="Item",
                                        template="simple_white",
                                    )
                    
                    fig.add_vline(
                                        x=hoje,
                                        line_width=2,
                                        line_dash="dash",
                                        line_color="gray"
                                    )

                    fig.add_annotation(
                                            x=hoje,
                                            y=1,
                                            xref="x",
                                            yref="paper",
                                            text="Hoje",
                                            showarrow=False,
                                            yshift=12,
                                            font=dict(size=12, color="gray")
                                        )

                    fig.update_traces(
                                        width=0.55,
                                        opacity=0.82,
                                        marker=dict(line=dict(width=0)),
                                        hovertemplate=(
                                            "<b>%{hovertext}</b><br>"
                                            "Início: %{base|%d/%m/%Y}<br>"
                                            "Fim: %{x|%d/%m/%Y}<extra></extra>"
                                        ),
                                    )

                    fig.update_layout(
                                            title=dict(
                                                text="<b>Cronograma de Atividades</b>",
                                                x=0.5,
                                                font=dict(size=24)
                                            ),
                                            height=altura,
                                            margin=dict(l=20, r=20, t=70, b=40),
                                            plot_bgcolor="rgba(248,249,251,1)",
                                            paper_bgcolor="white",
                                            font=dict(family="Segoe UI", size=12),
                                            legend=dict(
                                                title="Grupo",
                                                orientation="h",
                                                y=1.05,
                                                x=1,
                                                xanchor="right",
                                                yanchor="bottom"
                                            ),
                                            xaxis=dict(
                                                title="Período",
                                                showgrid=True,
                                                gridcolor="rgba(0,0,0,0.08)"
                                            ),
                                            yaxis=dict(
                                                title="",
                                                showgrid=True,
                                                gridcolor="rgba(0,0,0,0.035)"
                                            )
                                        )

                    fig.update_yaxes(
                                        autorange="reversed",
                                        categoryorder="array",
                                        categoryarray=df_GRAF["Item_Gantt"].unique()
                                    )
                    ab = st.columns([1,3,1], gap='large')
                    with ab[1]:
                        os.makedirs(rf"{st.session_state.tra_dir}/RELATORIOS/figuras/", exist_ok=True)
                        fig.write_image(rf"{st.session_state.tra_dir}/RELATORIOS/figuras/grantt.png")
                        st.plotly_chart(fig, width='stretch')

        st.markdown("</div>", unsafe_allow_html=True)
        _, col1, _, col3, _, col5, _ = st.columns([1,2,1,2,1,2,1], gap='small')

        with col1:
            salva3 = st.button("Salvar", key="CRON04", width='stretch')

        with col3:
            at2 = st.button("EXCEL", key="CRON05", width='stretch')

        with col5:
            at3 = st.button("Importar", key="CRON06", width='stretch')

        if salva3:
            with sl.connect(bd_path) as bd:
                with execucao_trilha(
                                    db_path=database, script_nome="Dados_Cronograma_Fiscalizacao",
                                    parametros={"empresa": empresa, "ano": ano},
                                    ) as execucao_id:
                    registrar_evento(database, execucao_id, "Salvando_CRONOGRAMA",
                                        mensagem = "Salvo informações cronograma do trabalho de fiscalização")
                df_edit.to_sql('tbl_PLANEJAMENTO', bd, if_exists='replace', index=False)
            df_PP = df_edit.copy()
            st.info("Salvo com sucesso!")
        if at3:
            with execucao_trilha(
                                db_path=database, script_nome="Dados_Cronograma_Fiscalizacao",
                                parametros={"empresa": empresa, "ano": ano},
                                ) as execucao_id:
                try:
                    registrar_evento(database, execucao_id, "Importando_arquivo_CRONOGRAMA",
                                    mensagem = "Importando dados externos do cronograma do trabalho de fiscalização")
                    nm_arq = f'{st.session_state.tra_dir}/RELATORIOS/Saida_CRONO_F0.xlsx'
                    registrar_artefato(database, execucao_id, nm_arq, "ENTRADA")
                    wb = load_workbook(nm_arq, data_only=True)
                    planilha = wb['CAPA']

                    df_CAB = pd.DataFrame({
                                            'Funcao': ['Empresa Fiscalizada', 'Avaliadora', 'Credenciada'],
                                            'Dado': [planilha[f'D{n}'].value for n in range(10, 13)],
                                            'Evento': ['Início Período Incremental', 'Final Período Incremental', ''],
                                            'Data': [planilha[f'F{n}'].value if n < 12 else '' for n in range(10, 13)],
                                        })
                    with sl.connect(bd_path) as bd:
                        df_CAB.to_sql('tbl_DD_CAB', bd, if_exists='replace', index=False)

                    df_DG = pd.DataFrame({
                                            'Funcao': [
                                                        'Coordenador SFF', 
                                                        'Fiscal 01 SFF', 
                                                        'Fiscal 02 SFF',
                                                        'Credenciado Coordenador', 
                                                        'Credenciado 01 AUD', 
                                                        'Credenciado 02 AUD'
                                                    ],
                                            'Profissional': [planilha[f'D{n}'].value for n in range(15, 21)],
                                            'Evento': [
                                                'Início de fiscalização', 'Finalização de fiscalização', 'Início em campo',
                                                'Finalização em campo', '', ''
                                            ],
                                            'Data': [planilha[f'F{n}'].value if n < 19 else '' for n in range(15, 21)],
                                        })
                    with sl.connect(bd_path) as bd:
                        df_DG.to_sql('tbl_DD_GERAIS_PLAN', bd, if_exists='replace', index=False)

                    df_PP = pd.read_excel(
                                                nm_arq, sheet_name='ATIVIDADES',
                                                usecols='C:M', skiprows=8, nrows=300,
                                                engine='openpyxl'
                                            )
                    df_PP = df_PP[df_PP['Dt_INI'].notnull()]
                    df_PP['Dt_INI'] = df_PP['Dt_INI'].dt.strftime('%d/%m/%Y')
                    df_PP['Dt_FIM'] = df_PP['Dt_FIM'].dt.strftime('%d/%m/%Y')
                    df_PP['SIT'] = df_PP['SIT'].astype(bool)
                    with sl.connect(bd_path) as bd:
                        df_PP.to_sql('tbl_PLANEJAMENTO', bd, if_exists='replace', index=False)
                    st.rerun()
                    st.info("Importado com sucesso!")
                except Exception as e:
                    st.error(f"Erro na importação: {e}")
                    registrar_evento(database, execucao_id, "ARQUIVO_REPROVADO",
                                    mensagem=f"Importcao arquivo CRONOGRAMA FALHOU", nivel="ERRO",
                                    detalhes={"erro": f"{e}"})
        if at2:
            with execucao_trilha(
                                db_path=database, script_nome="Dados_Cronograma_Fiscalizacao",
                                parametros={"empresa": empresa, "ano": ano},
                                ) as execucao_id:
                registrar_evento(database, execucao_id, "Exportando_arquivo_CRONOGRAMA",
                                                    mensagem = "Exportando dados externos do cronograma do trabalho de fiscalização")
                nm_arq = f'{st.session_state.tra_dir}/RELATORIOS/Saida_CRONO_F0.xlsx'
                x = imprimi_F0_CRONO(df_CAB, df_DG, df_PP, f'{local}\RELATORIOS', empresa, st)
                st.info("Exportado com sucesso!")
                registrar_artefato(database, execucao_id, nm_arq, "SAIDA")
    else:
        st.warning("Em implementação!", icon="🚜")

        