import streamlit as st
import sqlite3 as sl
import pandas as pd
import datetime
from pathlib import Path

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
        if existe_tabela('ANL_BMP_MANUAL', bd):
            st.html(f"""<h2>Dados analíticos do BMP e do Manual de Dados</h2>
                    <p  style="text-align: justify;text-indent: 40px">Avalie abaixo os dados
                    da comparação com os dados do BMP. Se houver diferenças, questione a empresa.</p>
                    """)
            
            sSQL = """SELECT * FROM ANL_BMP_MANUAL"""
            ANL_LST_TUC = pd.read_sql(sSQL, bd)
            for n in ANL_LST_TUC.columns.to_list():
                if ANL_LST_TUC[n].dtype == 'object' and n[:2].upper() in ["VL","QT","PC"]:
                    ANL_LST_TUC[n] = pd.to_numeric(ANL_LST_TUC[n].astype(str).str.replace(',','.'), 
                                                                errors='coerce',
                                                                downcast='float')
    
                if n[:2].upper() in ['VL', 'QT']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab0 =st.columns([1, 5, 1])
            with tab0[1]:
                st.dataframe(ANL_LST_TUC, use_container_width=True, hide_index=True)

@st.fragment()
def _vis_002(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if existe_tabela('ANL_OE_UN', bd):
            st.html(f"""<h2>Dados analíticos para o cálculo de OE (5A)</h2>
                    <p  style="text-align: justify;text-indent: 40px">Avalie abaixo os dados
                    da distribuição analítica da OE ao longo do ciclo. 
                    Há diferenças significativas em relação ao laudo? Verifique e justifique. 
                    Abaixo é apresentado os resultados, leia o relatório 
                    de Cálculos para análise completa.</p>
                    """)
            
            sSQL = """SELECT * FROM ANL_OE_UN"""
            ANL_LST_TUC = pd.read_sql(sSQL, bd)
            for n in ANL_LST_TUC.columns.to_list():
                if ANL_LST_TUC[n].dtype == 'object' and n[:2].upper() in ["VL","QT","PC"]:
                    ANL_LST_TUC[n] = pd.to_numeric(ANL_LST_TUC[n].astype(str).str.replace(',','.'), 
                                                                errors='coerce',
                                                                downcast='float')
    
                if n[:2].upper() in ['VL', 'QT']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab0 =st.columns([1, 5, 1])
            with tab0[1]:
                st.dataframe(ANL_LST_TUC, use_container_width=True, hide_index=True)
    
            st.html("""
                    <p  style="text-align: justify;text-indent: 40px">Avalie abaixo os dados
                    da distribuição sintética da OE ao longo do ciclo. 
                    Há diferenças significativas em relação ao laudo? Verifique e justifique. 
                    Abaixo é apresentado os resultados, leia o relatório 
                    de Cálculos para análise completa.</p><br>
                    """)
            
            sSQL = """SELECT * FROM ANL_OE_FIM"""
            ANL_LST_TUC = pd.read_sql(sSQL, bd)
            for n in ANL_LST_TUC.columns.to_list():
                if ANL_LST_TUC[n].dtype == 'object' and n[:2].upper() in ["VL","QT","PC"]:
                    ANL_LST_TUC[n] = pd.to_numeric(ANL_LST_TUC[n].astype(str).str.replace(',','.'), 
                                                                errors='coerce',
                                                                downcast='float')
    
                if n[:2].upper() in ['VL', 'QT']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab1 =st.columns([1, 5, 1])
            with tab1[1]:
                st.dataframe(ANL_LST_TUC, use_container_width=True, hide_index=True)
    
            st.html(f"""<h2>Dados resultantes do cálculo de OE (5B)</h2>
                        <p  style="text-align: justify;text-indent: 40px">Avalie abaixo os dados
                        dos cálculos resultantes da OE ao longo do ciclo. A primeira tabela apresenta
                        o resultado da movimentação da blindada, com as principais variáveis.
                        Há diferenças significativas em relação ao laudo? Verifique e justifique. 
                        Abaixo é apresentado os resultados, leia o relatório 
                        de Cálculos para análise completa.</p>
                        """)
            
            sSQL = """SELECT * FROM ANL_OE_BB"""
            ANL_LST_TUC = pd.read_sql(sSQL, bd)
            for n in ANL_LST_TUC.columns.to_list():
                if ANL_LST_TUC[n].dtype == 'object' and n[:2].upper() in ["VA"]:
                    ANL_LST_TUC[n] = pd.to_numeric(ANL_LST_TUC[n].astype(str).str.replace(',','.'), 
                                                                errors='coerce',
                                                                downcast='float')
    
                if n[:2].upper() in ['VA']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab2 =st.columns([1, 5, 1])
            with tab2[1]:
                st.dataframe(ANL_LST_TUC, use_container_width=True, hide_index=True)
    
            st.html("""
                    <p  style="text-align: justify;text-indent: 40px">A seguir temos a tabela 
                    que apresenta o resultado da movimentação da incremental, 
                    com as principais variáveis. Não lançamentos no incremental, mas há nos 
                    arquivos de OE incremental, faz sentido isso?
                    Há diferenças significativas em relação ao laudo? Verifique e justifique. 
                    Abaixo é apresentado os resultados, leia o relatório 
                    de Cálculos para análise completa.</p>
                    """)
            
            sSQL = """SELECT * FROM ANL_OE_BI"""
            ANL_LST_TUC = pd.read_sql(sSQL, bd)
            for n in ANL_LST_TUC.columns.to_list():
                if ANL_LST_TUC[n].dtype == 'object' and n[:2].upper() in ["VA"]:
                    ANL_LST_TUC[n] = pd.to_numeric(ANL_LST_TUC[n].astype(str).str.replace(',','.'), 
                                                                errors='coerce',
                                                                downcast='float')
    
                if n[:2].upper() in ['VA']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC']:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab3 =st.columns([1, 5, 1])
            with tab3[1]:
                st.dataframe(ANL_LST_TUC, use_container_width=True, hide_index=True)

@st.fragment()
def _vis_003(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if existe_tabela('ANL_TX_AMT_OE', bd):
            st.html(f"""<h2>Teste da Taxa de Depreciação Contábil</h2>
                        <p  style="text-align: justify;text-indent: 40px">Avalie abaixo os dados
                    da avaliação analítica da taxa de depreciação contábil, visão analítica,
                    na movimentação tanto da OE incremental quanto blindada. 
                    Há diferenças significativas em relação ao laudo? Verifique e justifique. 
                    Abaixo é apresentado os resultados, leia o relatório 
                    de Cálculos para análise completa.</p>
                    """)
            
            sSQL = """SELECT * FROM ANL_TX_AMT_OE"""
            ANL_LST_TUC = pd.read_sql(sSQL, bd)
            for n in ANL_LST_TUC.columns.to_list():
                if ANL_LST_TUC[n].dtype == 'object' and n[:2].upper() in ["VL","QT","PC","TX","LI"]:
                    ANL_LST_TUC[n] = pd.to_numeric(ANL_LST_TUC[n].astype(str).str.replace(',','.'), 
                                                                errors='coerce',
                                                                downcast='float')
    
                if n[:2].upper() in ['VL', 'QT',"LI"]:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC',"TX"]:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab0 =st.columns([1, 5, 1])
            with tab0[1]:
                st.dataframe(ANL_LST_TUC, use_container_width=True, hide_index=True)

@st.fragment()
def _vis_004(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        dt_ARQ = max_arq("OE_AJS", bd, empresa)
        if dt_ARQ:
            st.html(f"""<h2>Lista de ajustes aplicados no cálculo</h2>
                        <p  style="text-align: justify;text-indent: 40px">Avalie a lista de ajustes
                    abaixo e evidencie e valide os dados apresentados, nos papéis de trabalho. 
                    Há diferenças significativas em relação ao laudo? Verifique e justifique. 
                    Abaixo é apresentado os resultados, leia o relatório 
                    de Cálculos para análise completa.</p><br>
                    """)
            
            sSQL = """SELECT * FROM OE_AJS"""
            ANL_LST_TUC = pd.read_sql(sSQL, bd)
            for n in ANL_LST_TUC.columns.to_list():
                if ANL_LST_TUC[n].dtype == 'object' and n[:2].upper() in ["VL","QT","PC","TX","LI"]:
                    ANL_LST_TUC[n] = pd.to_numeric(ANL_LST_TUC[n].astype(str).str.replace(',','.'), 
                                                                errors='coerce',
                                                                downcast='float')
    
                if n[:2].upper() in ['VL', 'QT',"LI"]:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC',"TX"]:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    
            tab0 =st.columns([1, 5, 1])
            with tab0[1]:
                st.dataframe(ANL_LST_TUC, use_container_width=True, hide_index=True)

@st.fragment()
def _vis_005(bd_path="", st=None, empresa = "", bd_path2=""):
    with sl.connect(bd_path) as bd:
        if existe_tabela('ANL_IPCA_OE', bd):
            st.html(f"""<h2>Dados de IPCA empregados</h2>
                    <p  style="text-align: justify;text-indent: 40px">Para simples conferência
                        dos indicadores econômicos aplicado nos cálculos.</p><br>
                    """)
            
            sSQL = """SELECT * FROM ANL_IPCA_OE"""
            ANL_LST_TUC = pd.read_sql(sSQL, bd)
            for n in ANL_LST_TUC.columns.to_list():
                if ANL_LST_TUC[n].dtype == 'object' and n[:2].upper() in ["NR", "VL","QT","PC","TX","LI"]:
                    ANL_LST_TUC[n] = pd.to_numeric(ANL_LST_TUC[n].astype(str).str.replace(',','.'), 
                                                                errors='coerce',
                                                                downcast='float')
    
                if n[:2].upper() in ['VL', 'QT',"LI", "NR"]:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                elif n[:2].upper() in ['PC',"TX"]:
                    ANL_LST_TUC[n] = ANL_LST_TUC[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
            
            ANL_LST_TUC["DT_CMPT"] = pd.to_datetime(ANL_LST_TUC["DT_CMPT"], errors='coerce')
            config = {
                    "DT_CMPT": st.column_config.DateColumn("Data de Competência", format="DD/MM/YYYY"),
                } 
            tab0 =st.columns([1, 5, 1], gap='small', vertical_alignment="center")
            with tab0[1]:
                st.dataframe(ANL_LST_TUC, use_container_width=True, hide_index=True, column_config=config)
            with tab0[2]:
                st.download_button(label="📥 Baixar CSV",
                                    data=ANL_LST_TUC.to_csv(index=False, sep="|", decimal=",").encode("utf-8"),
                                    file_name="dados_ipca.csv",
                                    mime="text/csv",
                                    key=f"ipca_chv"
                                    )

def visualizador_OE(st = None):
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
                <h2>Análise das Obrigações Especiais</h2>
                <hr>

                <h3>Observações iniciais</h3>
                <div style="text-align: justify; text-indent: 40px;">
                    Esse é um documento base para se executar análise das obrigações
                especiais. Pode-se alterar o arquivo, porém somente será aplicado a versão original 
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
                <div style="text-align: justify; text-indent: 40px;">
                    Conforme PRORET 2.3, item 3.2.1, o valor monetário referente às 
                Obrigações Especiais da base blindada será obtido atualizando-se o valor 
                aprovado na revisão tarifária anterior pela variação do IPCA. Nenhum valor 
                deverá ser deduzido das Obrigações Especiais a título de baixas efetuadas 
                na base blindada.
                </div>
                <div style="text-align: justify;text-indent: 40px; padding-top: 10px;">
                Nada obstante, o item 5.3 trata das obrigações especiais 
                da base incremental. Destaca-se os §§134, 136 e 137:<br></div>
                <p style='text-align: justify;padding-left: 60px; padding-top: 10px;'><i>
                134. Para determinação do valor atualizado das Obrigações Especiais a ser 
                considerado como parcela redutora na base de remuneração, deverá ser 
                aplicada a variação verificada entre o Valor Novo de Reposição total e 
                o Valor Original Contábil não depreciado da conta “Máquinas e Equipamentos”, 
                sobre o saldo das Obrigações Especiais. No caso da aplicação do Banco de 
                Preços Referenciais, o valor novo de reposição será o resultante dentro 
                dos limites de reconhecimento, conforme critérios deste Submódulo.</i></p>
                <p style='text-align: justify;padding-left: 60px; padding-top: 10px;'><i>
                136. Para os investimentos relacionados ao Programa Luz para Todos – PLpT, 
                na participação das fontes de recursos referentes à Conta de Desenvolvimento 
                Energético – CDE, Estados, Municípios e Reserva Global de Reversão – RGR, 
                serão considerados os montantes efetivamente realizados, caso o contrato 
                já tenha sido integralmente executado fisicamente e liquidados junto à 
                ELETROBRAS ou, então, proporcionalizados quando o contrato ainda estiver 
                em execução.</i></p>
                <p style='text-align: justify;padding-left: 60px; padding-top: 10px;'><i>
                137. Como forma de demonstração dos valores de obrigações especiais, as 
                concessionárias deverão, no Laudo de Avaliação, incluir o Demonstrativo de 
                Obrigações Especiais, o qual deverá mostrar os valores Brutos e Líquidos 
                de Obrigações Especiais. Para tanto, o percentual acumulado da amortização 
                contábil deverá ser mantido para a amortização das Obrigações Especiais 
                avaliadas.</i></p>

                <div style="text-align: justify;text-indent: 40px">
                <a href="https://www.gov.br/aneel/pt-br/centrais-de-conteudos/procedimentos-regulatorios/proret">Visite o sitio da Aneel para mais detalhes!</a>
                </div>
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
    
    

