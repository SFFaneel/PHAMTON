import logging
import streamlit as st, base64
from pathlib import Path

if "LOGGER" not in st.session_state:
    logger = logging.getLogger("brr_sff")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
        )
        logger.addHandler(handler)

    st.session_state.LOGGER = logger

from SRC import (
                    iniciar,
                    AMOSTRAS_D,
                    matriz_mestra,
                    trilha_fisc,
                    visualizar
                )
from VALIDADOR import (
                        VALIDADOR_D,
                      )
from MANIFESTO import (
                        visualizar_manifesto_exec,
                        visual_manifesto
                      )
from DATABASE_MAN import (
                            imp_arq_dados,
                            imp_BDGD,
                            imp_COGE,
                            imp_SPED_EFD_ICMS,
                            imp_SPED_ECD,
                            dados_fotos_inv
                        )
from RELATORIOS import exportar
from UTILS import visualizar_docs

imagem_fundo = "imagens/bull_bck.png"
imagem_icon = "imagens/bull.png"

with open(imagem_fundo, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode()

st.set_page_config(page_title="Phantom's Fang 2026", 
                   page_icon=imagem_icon, 
                   layout="wide",
                   initial_sidebar_state="auto",
                   menu_items={
                                    'Get help': 'https://www.gov.br/aneel/pt-br/centrais-de-conteudos/manuais-modelos-e-instrucoes/informacoes-economico-financeiras',
                                    'Report a bug': "mailto: sff_brr@aneel.gov.br?subject=Relato%20Falha",
                                    'About': "# Versão 3, fase Phantom's Fang!"
                               }
                    )
if "page" not in st.session_state:
    st.session_state.page = "CONFIGURAR"
if "nm_empr" not in st.session_state:
    st.session_state.nm_empr = "Fase III"
if "texto_ini" not in st.session_state:
    st.session_state.texto_ini = ""
if "modelo" not in st.session_state:
    st.session_state.modelo = "qwen3:8b"
if "txt_HELP" not in st.session_state:
    st.session_state.txt_HELP = []    
if "SIST_CONFIG" not in st.session_state:
    st.session_state.SIST_CONFIG = False
if "Tipo_concessao" not in st.session_state:
    st.session_state.Tipo_concessao = "Distribuição"

cor_estado = "#047e31" if st.session_state.SIST_CONFIG else "#920606"
cor_esmae = "#b0c3b7" if st.session_state.SIST_CONFIG else "#E9AAAA"

col1 = st.columns([1,8,1], gap='small')
with col1[1]:
    st.html(
                    f"""
                        <style>
                        @import url('fonts.googleapis.com');

                        .cabecalho {{
                            background: rgba(255, 255, 255, 0.05);
                            backdrop-filter: blur(10px);
                            -webkit-backdrop-filter: blur(10px);
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            border-radius: 20px;
                            padding: 1.5rem 2rem;
                            display: flex;
                            align-items: center;
                            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
                            margin-bottom: 2rem;
                            width: 100%;
                        }}

                        .empresa {{
                            font-family: 'Plus Jakarta Sans', sans-serif !important;
                            font-weight: 800 !important;
                            font-size: clamp(1.8rem, 4vw, 2.8rem) !important;
                            background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            margin: 0 !important;
                            flex-grow: 1;
                            text-align: center;
                            letter-spacing: -0.02em;
                        }}

                        .estado-bola {{
                            width: 20px;
                            height: 20px;
                            background-color: {cor_estado};
                            border-radius: 50%;
                            box-shadow: 0 0 15px {cor_estado};
                            animation: esmae_bola 2s infinite ease-in-out;
                            transition: all 0.5s ease;
                        }}

                        @keyframes esmae_bola {{
                            0% {{ transform: scale(0.9); opacity: 0.6; box-shadow: 0 0 10px {cor_esmae}; }}
                            50% {{ transform: scale(1.1); opacity: 1; box-shadow: 0 0 30px {cor_esmae}; }}
                            100% {{ transform: scale(0.9); opacity: 0.6; box-shadow: 0 0 10px {cor_esmae}; }}
                        }}

                        .estado {{
                            display: flex;
                            align-items: center;
                            gap: 12px;
                            background: rgba(0, 0, 0, 0.2);
                            padding: 8px 16px;
                            border-radius: 50px;
                            border: 1px solid rgba(255, 255, 255, 0.05);
                        }}

                        .texto_estado {{
                            font-family: 'Plus Jakarta Sans', sans-serif;
                            font-size: 0.7rem;
                            color: {cor_estado};
                            text-transform: uppercase;
                            letter-spacing: 1.5px;
                        }}

                        [data-testid="stAppViewContainer"] {{
                            background-image: url("data:image/png;base64,{img_base64}");
                            background-size: cover;
                            background-position: center;
                            background-repeat: no-repeat;
                            background-attachment: fixed;
                        }}
                        
                        header[data-testid="stHeader"] {{
                            background-color: none !important;
                            background-image: none !important;
                            opacity: 1 !important;
                            height: 3.75rem !important;
                        }}

                        header[data-testid="stHeader"]::before {{
                            content: none !important;
                        }}

                        [data-testid="stTopLevelNavigation"] {{
                            background-color: none !important;
                        }}

                        [data-testid="stTopLevelNavigation"] button p {{
                            color: #ffffff !important;
                            font-weight: 600 !important;
                        }}

                        .stApp {{
                            margin-top: 0px !important;
                        }}

                        [data-testid="stAppViewBlockContainer"] {{
                            background: transparent !important;
                        }}

                        [data-testid="stSidebarNav"] {{
                            background-color: #FFFFF !important;
                            background-image: none !important;
                            opacity: 1 !important;
                            width: 300px !important;
                        }}

                        [data-testid="stSidebarNavItems"] a {{
                            background-color: transparent !important;
                            background-image: none !important;
                            color: #FFFFFF !important;
                            border-radius: 8px !important;
                            margin-bottom: 5px !important;
                            transition: background-color 0.3s ease;
                        }}

                        [data-testid="stSidebarNavItems"] a[aria-current="page"] {{
                            background-color: #2E2E2E !important;
                            border-left: 4px solid #4CAF50 !important;
                            font-weight: bold !important;
                        }}

                        [data-testid="stSidebarNavItems"] a:hover {{
                            background-color: #333333 !important;
                        }}


                        h1 {{
                            font-family: 'Inter', sans-serif !important;
                            background: linear-gradient(90deg, #1e293b, #64748b) !important;
                            -webkit-background-clip: text !important;
                            -webkit-text-fill-color: transparent !important;
                            font-weight: 800 !important;
                            font-size: clamp(0.8rem, 4vw, 3.2rem) !important;
                            text-shadow: 2px 2px 10px rgba(0,0,0,0.1);
                            margin-bottom: 0px !important;
                        }}

                        .block-container {{
                            padding-left: 0% !important;
                            padding-right: 0% !important;
                            max-width: 95% !important;
                        }}

                        hr.full-line {{
                            border: 0;
                            height: 2px;
                            background: linear-gradient(to right, transparent, #4CAF50, transparent);
                            margin: 20px 0;
                        }}

                        .plotly-wrapper {{
                            width: 80%; /* Ajuste conforme necessário */
                            margin: 32px auto;
                            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.18) !important;
                            border-radius: 14px !important;
                            overflow: hidden;
                            transition: transform 200ms ease, box-shadow 200ms ease !important;
                            background-color: white;
                        }}

                        .plotly-wrapper:hover {{
                            transform: translateY(-6px) scale(1.02) !important;
                            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.28) !important;
                            z-index: 10;
                        }}
                        </style>
                    """
                )

    nome_empresa = st.session_state.nm_empr.replace("_", " ")
    estado = "Sistema Ativo" if st.session_state.SIST_CONFIG else "Aguardando"

    st.html(f"""
                <div class="cabecalho">
                <div style="flex: 1; display: flex; justify-content: flex-start;">
                    <div class="estado">
                        <div class="estado-bola"></div>
                        <span class="texto_estado">{estado}</span>
                    </div>
                </div>
                <div style="flex: 5;">
                    <h1 class="empresa">{nome_empresa}</h1>
                </div>
                <div style="flex: 1;"></div>
            """)

    def pagina_manifesto():
        pasta_manifesto = (
                                Path(st.session_state.tra_dir)
                                / "MANIFESTO"
                                / "TRILHA_EXEC"
                            )
        raiz = (
                    Path(st.session_state.tra_dir)
                    / "MANIFESTO"
                    / "TRILHA_DADOS"
                )
        database = str(pasta_manifesto / "execucoes.db")
        tabs = st.tabs(['DADOS','EXECUÇÃO'])
        with tabs[1]:
            visualizar_manifesto_exec(database, st)
        with tabs[0]:
            visual_manifesto(raiz, st=st)

    def pagina_ECD():
        caminho_CVA = Path.cwd() / "anl_desc_hist.py"
        if caminho_CVA.exists():
            from anl_desc_hist import inic_ECD_leitura
            inic_ECD_leitura()
    
    def visual():
        visualizar(st)

    def criar_rel():
        exportar(st)

    def ler_normas():
        visualizar_docs(st)

    paginas = {
                        'CONFIGURAR:': [
                            st.Page(iniciar, title="DEFINÇÃO DO TRABALHO", icon=":material/home:")
                        ],
                        'VALIDAR:': [
                            st.Page(VALIDADOR_D, title="MANUAL DE DADOS", icon=":material/fact_check:")
                        ],
                        'IMPORTAR:': [
                            st.Page(imp_arq_dados, title="MANUAL DADOS", icon=":material/layers:"),
                            st.Page(imp_BDGD, title="BDGD", icon=":material/layers:"),
                            st.Page(imp_COGE, title="COGE", icon=":material/layers:"),
                            st.Page(imp_SPED_EFD_ICMS, title="EFD ICMS IPI", icon=":material/layers:"),
                            st.Page(imp_SPED_ECD, title="ECD", icon=":material/upload_file:"),
                            st.Page(dados_fotos_inv, title="Fotos inventário", icon=":material/upload_file:")
                        ],
                        'PLANEJAR:': [
                            st.Page(AMOSTRAS_D, title="Amostras de Obras", icon=":material/grid_view:"),
                            st.Page(matriz_mestra, title="Cronograma", icon=":material/checklist:")
                        ],
                        'EXECUTAR:': [
                            st.Page(trilha_fisc, title="Trilha de Fiscalização", icon="📐")
                        ],
                        'VISUALIZAR:': [
                                        st.Page(visual, title="DASHBOARD", icon="📐")
                                    ],
                        'EXPORTAR RESULTADOS:': [
                            st.Page(criar_rel, title="Exportação", icon=":material/assessment:")
                        ],
                        'MANIFESTO': [
                            st.Page(pagina_manifesto, title="Manifesto Execução", icon=":material/manage_search:")
                        ],
                        'HELP:': [
                            st.Page(ler_normas, title="LEGISLAÇÃO", icon=":material/description:")
                        ]
                    }


    pg = st.navigation(paginas, position="top")
    pg.run()    



