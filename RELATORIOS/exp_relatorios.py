from __future__ import annotations
from .imprimir_xlsx import (
                            imprimi_F0_BP,
                            imprimi_F1_BP,
                            imprimi_F2_BP,
                            imprimi_F3_BP,
                            imprimi_F0_ABT,
                            imprimi_F1_ABT,
                            imprimi_F0_INCR,
                            imprimi_F1_INCR,
                            imprimi_F0_OE,
                            imprimi_F1_OE,
                            imprimi_F0_BB
                           )
import re
import sqlite3 as sl
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
import pandas as pd
import streamlit as st
import UTILS.dados_bulldozer as bull
import VALIDADOR.validador_funcoes as VAL
from UTILS import (
                    criar_tabela, 
                    sanear_csv, 
                    existe_tabela,
                    determinar_tipo, 
                    converter_decimal,
                    bsc_dados_reg
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
def imprimir_BC(bd_path = "", bd_EFD_path = "", st = None, local = "", empresa = ""):
    with sl.connect(bd_path) as bd:
        FLG_ARQ = st.checkbox("Fluxo de pagamento: arquivo (ativo), se projeção (inativo)",
                                              value = True, width='stretch')
        colas = st.columns([1, 2, 1, 2, 1, 2, 1, 2, 1], gap='small')
        with colas[1]:
            F0 = st.button("F0 COMPRAS", width='stretch', key = "imprime_F0_COMPRAS")
        with colas[3]:
            F1 = st.button("F1 COMPRAS", width='stretch', key = "imprime_F1_COMPRAS")
        with colas[5]:
            F2 = st.button("F2 COMPRAS", width='stretch', key = "imprime_F2_COMPRAS")
        st.divider()
        
        with sl.connect(bd_EFD_path) as bd_EFD:
            if F0:
                n1 = imprimi_F0_BP(f'{local}\BP_ANLS', bd, empresa, st)
            if F1:
                n2 = imprimi_F1_BP(f'{local}\BP_ANLS', bd, bd_EFD, empresa, st.session_state.dt_ini, st.session_state.dt_fim, FLG_ARQ, st)
            if F2:
                n3 = imprimi_F2_BP(f'{local}\BP_ANLS', bd, empresa, st.session_state.dt_ini, st.session_state.dt_fim, FLG_ARQ, st)

@st.fragment()
def imprimir_ABT(bd_path = "", bd_EFD_path = "", st = None, local = "", empresa = ""):
    with sl.connect(bd_path) as bd:

        colas = st.columns([1, 2, 1, 2, 1, 2, 1, 2, 1], gap='small')
        with colas[3]:
            F0 = st.button("F0 ABERTURA", width='stretch', key = "imprime_F0_ABERTURA")
        with colas[5]:
            F1 = st.button("F1 ABERTURA", width='stretch', key = "imprime_F1_ABERTURA")
        st.divider()
        
        with sl.connect(bd_EFD_path) as bd_EFD:
            if F0:
                n1 = imprimi_F0_ABT(f'{local}\AIS_ANLS',bd, empresa, st)        
            if F1:
                n2 = imprimi_F1_ABT(f'{local}\AIS_ANLS',bd, empresa, st)

@st.fragment()
def imprimir_INCR(bd_path = "", bd_EFD_path = "", st = None, local = "", empresa = ""):
    with sl.connect(bd_path) as bd:

        colas = st.columns([1, 2, 1, 2, 1, 2, 1, 2, 1], gap='small')
        with colas[3]:
            F0 = st.button("F0 INCREMENTAL", width='stretch', key = "imprime_F0_INCREMENTAL")
        with colas[5]:
            F1 = st.button("F1 INCREMENTAL", width='stretch', key = "imprime_F1_INCREMENTAL")
        st.divider()
        
        with sl.connect(bd_EFD_path) as bd_EFD:
            if F0:
                n1 = imprimi_F0_INCR(f'{local}\INC_ANLS',bd, empresa, st)        
            if F1:
                n2 = imprimi_F1_INCR(f'{local}\INC_ANLS',bd, empresa, st)

@st.fragment()
def imprimir_OE(bd_path = "", bd_EFD_path = "", st = None, local = "", empresa = ""):
    with sl.connect(bd_path) as bd:

        colas = st.columns([1, 2, 1, 2, 1, 2, 1, 2, 1], gap='small')
        with colas[3]:
            F0 = st.button("F0 OE", width='stretch', key = "imprime_F0_OE")
        with colas[5]:
            F1 = st.button("F1 OE", width='stretch', key = "imprime_F1_OE")
        st.divider()
        
        with sl.connect(bd_EFD_path) as bd_EFD:
            if F0:
                n1 = imprimi_F0_OE(f'{local}\OE_ANLS',bd, empresa, st)        
            if F1:
                n2 = imprimi_F1_OE(f'{local}\OE_ANLS',bd, empresa, st)

@st.fragment()
def imprimir_BB(bd_path = "", bd_EFD_path = "", st = None, local = "", empresa = ""):
    with sl.connect(bd_path) as bd:

        colas = st.columns([1, 2, 1, 2, 1, 2, 1, 2, 1], gap='small')
        with colas[3]:
            F0 = st.button("F0 BB", width='stretch', key = "imprime_F0_BB")

        st.divider()
        
        with sl.connect(bd_EFD_path) as bd_EFD:
            if F0:
                n1 = imprimi_F0_BB(f'{local}\BB_ANLS',bd, empresa, st)        


def exportar(st=None):
    if st is None:
        import streamlit as st

    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
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
    st.html(f"""<h1 style="text-align: center;">Trilha de Exportação de Resultados</h1><br><br>
                <p  style="text-align: justify;text-indent: 40px">Nesta aba temos as exportações 
                de resultados.</p>  
                <hr></hr>
                        
            """)

    with sl.connect(bd_path) as bd:
        if (existe_tabela('tbl_PLANEJAMENTO', bd)):
            tbl_PLAN = pd.read_sql('SELECT * FROM tbl_PLANEJAMENTO WHERE TP_FISC IS NOT NULL ORDER BY TP_FISC ASC', bd)
            if not tbl_PLAN.empty:
                processo = tbl_PLAN['TP_FISC'].values[0]
            else:
                st.error("Tem de ser feito o planejamento")
                return
        else:
            st.error("Tem de ser feito o planejamento")
            return

    cols = st.columns([1,10,1], gap='small')
    with cols[1]:
        with st.container(border=True):
            if processo == 'DISTRIBUIDORA PERIÓDICA':
                with st.container(border=True, vertical_alignment='center'):
                    st.html(f""" <h1>DISTRIBUIDORA EM REVISÃO {empresa}</h1>
                                <br><br><br>
                                <h2>BANCO DE COMPRAS</h2>
                
                                <hr></hr>
                                                
                                <div style="text-align: justify;text-indent: 40px; padding-top: 10px"><p>Exportar resultados 
                                            para o Excel é feita devido à sua difusão como ferramenta de análise 
                                            neste tipo de trabalho. Entendemos, nesse momento, que facilita a adoção, 
                                            reduzindo a necessidade de treinamento adicional. Além disso, sua 
                                            compatibilidade com diversos formatos e integração com outras aplicações 
                                            garantem que os dados possam ser compartilhados e analisados. A seguir,
                                            resumimos os tipos de exportação.</p><br></div>
                                <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                            <p><b>F0</b>: foi executada a conciliação entre EFD ICMS e ERP (arquivo F0). Verifique
                                            a consistência agregada e desagregada com a empresa.</p>
                                            </div>
                                <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                            <p><b>F1</b>: apresenta-se os resultados da análise do extrato de compras. 
                                            Na primeira aba tem-se o cruzamento do extrato de compras com os dados do SPED 
                                            e do INC (indicando dados do SPED como CFOP e outras informações; adicionalmente 
                                            se inclui os dados de fluxo de pagamento, fórmula COGE, rateio do financeiro de 
                                            ICMS (existe um tratamento específico entre as parcelas recuperavel e não 
                                            recuperável no que se refere a atualização) e de ODC, e classificação contábil 
                                            do item (que é a empregada no INC)). A segunda aba, EC_UC_UAR_BASE, consolida 
                                            os itens que são UAR. Notar que somente não se emprega as notas complementares 
                                            e também não se emprega os bens reformados. A aba VF_DESCR_ITEM, apresenta as 
                                            estatísticas descritivas dos itens, salientando os de maior variação no 
                                            período. A aba BC_VF_UC, apresenta a consolidação por TUCAGEM, aba BC_VF_ITEM, 
                                            apresenta a consolidação por COD_ITEM.</p>
                                            </div>
                                <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                            <p><b>F2</b>: é efetuada uma comparação entre o BP_UAR apresentado e os dados 
                                            calculados. Verifica-se a fórmula COGE, se o item foi empregado no ROA, e a 
                                            variação nos resultados.</p>
                                            </div>
                
                            """)
                    
                    imprimir_BC(bd_path, bd_EFD_path, st, local, empresa)

                    st.html("""
                                                    <h2>ABERTURA DO AIS</h2>
                                    
                                                    <hr></hr>
                                                                    
                                                    <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                                                <p><b>F0</b>: foi feita a análise da distribuição dos custos por projeto e TI, considerando
                                                                 natureza de gasto e tipo de atividade (arquivo F0). Discuta
                                                                a consistência desagregada com a empresa, isto é, os critérios alocativos para projetos.</p>
                                                                </div>
                                                    <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                                                <p><b>F1</b>: apresenta-se os resultados da análise do valor de fábrica do ROA e o resultante
                                                                do processo de abertura fornecido pela empresa. Adicionalmente, também, se discute a abertura
                                                                do JOA.</p>
                                                                </div>
                                                    
                                                """)
                    imprimir_ABT(bd_path, bd_EFD_path, st, local, empresa)
                    st.html("""
                                <h2>ANÁLISE DO LAUDO INCREMENTAL</h2>
                
                                <hr></hr>
                                                
                                <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                            <p><b>F0</b>: foi feita a análise do VOC informado no arquivo incremental,
                                            comparando-o com os resultados da avaliação do AIS.</p>
                                            </div>
                                <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                            <p><b>F1</b>: apresenta-se os resultados da emulação do laudo, confrontando
                                            com o entregue.</p>
                                            </div>
                                
                            """)
                    imprimir_INCR(bd_path, bd_EFD_path, st, local, empresa)

                    st.html("""
                                <h2>ANÁLISE DA MOVIMENTAÇÃO DE OE</h2>
                
                                <hr></hr>
                                                
                                <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                            <p><b>F0</b>: é elaborado o demonstrativo das obrigações, tanto do 
                                            incremental quando da blindada. O arquivo de saída SAIDA_F0_OE_xxxx, 
                                            sintetiza os resultados. Temos: relatório do BMP, 
                                            demonstrativo de Obrigações Especiais, 
                                            <b>aba OE5a</b>; demonstrativo da consolidação por atividade, <b>aba OE5b</b>;
                                            teste das taxas de amortização empregadas, <b>aba TSTE_TX_AMT_CNTB</b>;
                                            descrição dos ajustes efetuados na incremental e blindada, <b>aba LISTA_AJUSTES</b>;
                                            dados de IPCA, <b>aba TABELA_IPCA</b>.</p>
                                            </div>
                                <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                            <p><b>F1</b>: sintetiza os resultados de cálculo da taxa média de depreciação, 
                                            <b>aba Resumo_UC</b>; demonstrativo de consolidação por atividade, 
                                            <b>aba Tx_MED_ATIVD</b>.</p>
                                            </div>
                                
                            """)
                    imprimir_OE(bd_path, bd_EFD_path, st, local, empresa)
                    st.html("""
                                <h2>ANÁLISE DA MOVIMENTAÇÃO DA BB</h2>
                
                                <hr></hr>
                                                
                                <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                            <p><b>F0</b>: O arquivo de saída SAIDA_F0_BB, 
                                            sintetiza os resultados. Temos: o comparativo entre MEMO, encaminhado para 
                                            a área de tarifas, e o arquivo de PPBB, <b>ABA TESTE_PP</b>;
                                            teste de quantidade de baixas por UC e unidade, <b>ABA TESTE_BAIXAS</b>;
                                            teste de quantidade de baixas por UC, <b>ABA TESTE_BAIXAS_UC</b>;
                                            resumo dos dados, <b>ABA RESUMO</b>; e 
                                            memorial dos cálculos, <b>DIVERSAS ABAS NOMEADAS como <i>TESTE_VNRx</i></b></b>.</p>
                                            </div>
                                
                            """)
                    imprimir_BB(bd_path, bd_EFD_path, st, local, empresa)
            elif processo == 'DISTRIBUIDORA ANUAL':
                            with st.container(border=True, vertical_alignment='center'):
                                st.html(f""" <h1>DISTRIBUIDORA {empresa}</h1>
                                            <br><br><br>
                                            <h2>BANCO DE COMPRAS</h2>
                            
                                            <hr></hr>
                                                            
                                            <div style="text-align: justify;text-indent: 40px; padding-top: 10px"><p>Exportar resultados 
                                                        para o Excel é feita devido à sua difusão como ferramenta de análise 
                                                        neste tipo de trabalho. Entendemos, nesse momento, que facilita a adoção, 
                                                        reduzindo a necessidade de treinamento adicional. Além disso, sua 
                                                        compatibilidade com diversos formatos e integração com outras aplicações 
                                                        garantem que os dados possam ser compartilhados e analisados. A seguir,
                                                        resumimos os tipos de exportação.</p><br></div>
                                            <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                                        <p><b>F0</b>: foi executada a conciliação entre EFD ICMS e ERP (arquivo F0). Verifique
                                                        a consistência agregada e desagregada com a empresa.</p>
                                                        </div>
                                            <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                                        <p><b>F1</b>: apresenta-se os resultados da análise do extrato de compras. 
                                                        Na primeira aba tem-se o cruzamento do extrato de compras com os dados do SPED 
                                                        e do INC (indicando dados do SPED como CFOP e outras informações; adicionalmente 
                                                        se inclui os dados de fluxo de pagamento, fórmula COGE, rateio do financeiro de 
                                                        ICMS (existe um tratamento específico entre as parcelas recuperavel e não 
                                                        recuperável no que se refere a atualização) e de ODC, e classificação contábil 
                                                        do item (que é a empregada no INC)). A segunda aba, EC_UC_UAR_BASE, consolida 
                                                        os itens que são UAR. Notar que somente não se emprega as notas complementares 
                                                        e também não se emprega os bens reformados. A aba VF_DESCR_ITEM, apresenta as 
                                                        estatísticas descritivas dos itens, salientando os de maior variação no 
                                                        período. A aba BC_VF_UC, apresenta a consolidação por TUCAGEM, aba BC_VF_ITEM, 
                                                        apresenta a consolidação por COD_ITEM.</p>
                                                        </div>
                                            <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                                        <p><b>F2</b>: é efetuada uma comparação entre o BP_UAR apresentado e os dados 
                                                        calculados. Verifica-se a fórmula COGE, se o item foi empregado no ROA, e a 
                                                        variação nos resultados.</p>
                                                        </div>
                                            <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                                        <p><b>F3</b>: são testes de quantidades entre o ROA e o EC e o SPED. O que não 
                                                        for do EC deve ter origem ou do estoque inicial, obras em curso ou 
                                                        reutilizações.</p>
                                                        </div>
                            
                                        """)
                                
                                imprimir_BC(bd_path, bd_EFD_path, st, local, empresa)
            
                                st.html("""
                                                                <h2>ABERTURA DO AIS</h2>
                                                
                                                                <hr></hr>
                                                                                
                                                                <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                                                            <p><b>F0</b>: foi feita a análise da distribuição dos custos por projeto e TI, considerando
                                                                             natureza de gasto e tipo de atividade (arquivo F0). Discuta
                                                                            a consistência desagregada com a empresa, isto é, os critérios alocativos para projetos.</p>
                                                                            </div>
                                                                <div style="text-align: justify;padding-left: 60px; padding-top: 10px">            
                                                                            <p><b>F1</b>: apresenta-se os resultados da análise do valor de fábrica do ROA e o resultante
                                                                            do processo de abertura fornecido pela empresa. Adicionalmente, também, se discute a abertura
                                                                            do JOA.</p>
                                                                            </div>
                                                                
                                                            """)
                                imprimir_ABT(bd_path, bd_EFD_path, st, local, empresa)
            else:
                st.warning(f"Não implantado para {processo}")