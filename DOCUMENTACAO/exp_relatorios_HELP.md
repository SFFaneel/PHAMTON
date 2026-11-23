# Referência de Funções

## Índice

- [imprimir_BC](#funcao-1)
- [imprimir_ABT](#funcao-2)
- [imprimir_INCR](#funcao-3)
- [imprimir_OE](#funcao-4)
- [imprimir_BB](#funcao-5)
- [exportar](#funcao-6)

---

<a id="funcao-1"></a>

## imprimir_BC

Imprime relatórios de compras (F0, F1 e F2) a partir dos bancos de dados fornecidos.

Esta função conecta-se a dois bancos de dados SQLite (`bd_path` e `bd_EFD_path`) e imprime relatórios de compras (F0, F1 e F2) com base nas interações do usuário através de botões em uma interface Streamlit. Os parâmetros `st`, `local` e `empresa` são utilizados para configurar a interface e o contexto da impressão.

### Assinatura

```python
def imprimir_BC(bd_path = "", bd_EFD_path = "", st = None, local = "", empresa = ""):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `bd_path` | `Não especificado` | Caminho do banco de dados principal. |
| `bd_EFD_path` | `Não especificado` | Caminho do banco de dados EFD. |
| `st` | `Não especificado` | Objeto Streamlit para a interface da aplicação. |
| `local` | `Não especificado` | Local onde os arquivos serão salvos. |
| `empresa` | `Não especificado` | Nome da empresa para o relatório. |

### Dependências

- `{'nome': 'imprimir_xlsx.imprimi_F0_BP', 'tipo': 'função'}`
- `{'nome': 'imprimir_xlsx.imprimi_F1_BP', 'tipo': 'função'}`
- `{'nome': 'imprimir_xlsx.imprimi_F2_BP', 'tipo': 'função'}`
- `{'nome': 'sqlite3', 'tipo': 'biblioteca'}`
- `{'nome': 'streamlit', 'tipo': 'biblioteca'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
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
```

</details>

---

<a id="funcao-2"></a>

## imprimir_ABT

Imprime relatórios ABT (Anotações de Balanço e Demonstração) utilizando bancos de dados SQLite.

Esta função cria uma interface interativa usando Streamlit para selecionar entre dois tipos de relatórios ABT: F0 ABERTURA e F1 ABERTURA. Cada tipo de relatório é gerado a partir de um banco de dados SQLite especificado pelo usuário.

### Assinatura

```python
def imprimir_ABT(bd_path = "", bd_EFD_path = "", st = None, local = "", empresa = ""):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `bd_path` | `Não especificado` | Caminho para o banco de dados SQLite principal. |
| `bd_EFD_path` | `Não especificado` | Caminho para o banco de dados SQLite da EFD (Eletrônica Fiscal Digital). |
| `st` | `Não especificado` | Objeto Streamlit usado para criar a interface interativa. |
| `local` | `Não especificado` | Caminho local onde os arquivos de relatório serão salvos. |
| `empresa` | `Não especificado` | Nome da empresa para o qual os relatórios estão sendo gerados. |

### Dependências

- `{'nome': 'imprimir_xlsx.imprimi_F0_ABT', 'categoria': 'importado'}`
- `{'nome': 'imprimir_xlsx.imprimi_F1_ABT', 'categoria': 'importado'}`
- `{'nome': 'sqlite3', 'categoria': 'importado'}`
- `{'nome': 'streamlit', 'categoria': 'importado'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
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
```

</details>

---

<a id="funcao-3"></a>

## imprimir_INCR

Imprime dados incrementais de um banco de dados EFD e BD.

Esta função cria uma interface interativa utilizando Streamlit para permitir o usuário selecionar entre dois botões ('F0 INCREMENTAL' e 'F1 INCREMENTAL'). Cada botão, quando pressionado, chama uma função específica para imprimir dados incrementais de um banco de dados EFD e BD. A função também utiliza SQLite3 para conexão com os bancos de dados.

### Assinatura

```python
def imprimir_INCR(bd_path = "", bd_EFD_path = "", st = None, local = "", empresa = ""):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `bd_path` | `Não especificado` | Caminho do arquivo do banco de dados principal. |
| `bd_EFD_path` | `Não especificado` | Caminho do arquivo do banco de dados EFD. |
| `st` | `Não especificado` | Objeto Streamlit para criar a interface interativa. |
| `local` | `Não especificado` | Local onde os arquivos incrementais estão armazenados. |
| `empresa` | `Não especificado` | Nome da empresa associada aos dados. |

### Dependências

- `{'nome': 'imprimir_xlsx.imprimi_F0_INCR', 'tipo': 'função', 'categoria': 'importado'}`
- `{'nome': 'imprimir_xlsx.imprimi_F1_INCR', 'tipo': 'função', 'categoria': 'importado'}`
- `{'nome': 'sqlite3', 'tipo': 'biblioteca', 'categoria': 'importado'}`
- `{'nome': 'streamlit', 'tipo': 'biblioteca', 'categoria': 'importado'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
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
```

</details>

---

<a id="funcao-4"></a>

## imprimir_OE

Imprime relatórios OE (Operações e Estoque) utilizando bancos de dados SQLite.

Esta função cria uma interface Streamlit para selecionar entre dois tipos de relatórios OE (F0 e F1) e imprime esses relatórios usando funções específicas. Os bancos de dados SQLite são utilizados para obter os dados necessários.

### Assinatura

```python
def imprimir_OE(bd_path = "", bd_EFD_path = "", st = None, local = "", empresa = ""):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `bd_path` | `Não especificado` | Caminho do banco de dados principal. |
| `bd_EFD_path` | `Não especificado` | Caminho do banco de dados EFD (Eletrônico Fiscal Digital). |
| `st` | `Não especificado` | Objeto Streamlit para criar a interface. |
| `local` | `Não especificado` | Local onde os arquivos de relatório serão salvos. |
| `empresa` | `Não especificado` | Nome da empresa para o qual os relatórios serão gerados. |

### Dependências

- `{'nome': 'imprimir_xlsx.imprimi_F0_OE', 'tipo': 'função', 'categoria': 'externa'}`
- `{'nome': 'imprimir_xlsx.imprimi_F1_OE', 'tipo': 'função', 'categoria': 'externa'}`
- `{'nome': 'sqlite3', 'tipo': 'biblioteca', 'categoria': 'externa'}`
- `{'nome': 'streamlit', 'tipo': 'biblioteca', 'categoria': 'externa'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
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
```

</details>

---

<a id="funcao-5"></a>

## imprimir_BB

Imprime dados de um banco de dados EFD (Eletrônico Fiscal Digital) em uma interface Streamlit.

A função conecta a um banco de dados SQLite e, se o botão 'F0 BB' for pressionado, imprime dados específicos no formato XLSX usando outra função chamada `imprimi_F0_BB`. A interface é construída com componentes do Streamlit.

### Assinatura

```python
def imprimir_BB(bd_path = "", bd_EFD_path = "", st = None, local = "", empresa = ""):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `bd_path` | `Não especificado` | Caminho para o banco de dados SQLite. |
| `bd_EFD_path` | `Não especificado` | Caminho para o banco de dados EFD. |
| `st` | `Não especificado` | Objeto Streamlit usado para criar a interface da aplicação. |
| `local` | `Não especificado` | Local onde os dados serão salvos ou exibidos. |
| `empresa` | `Não especificado` | Nome da empresa associada aos dados. |

### Dependências

- `{'nome': 'imprimir_xlsx.imprimi_F0_BB', 'tipo': 'função', 'categoria': 'externa'}`
- `{'nome': 'sqlite3', 'tipo': 'biblioteca', 'categoria': 'externa'}`
- `{'nome': 'streamlit', 'tipo': 'biblioteca', 'categoria': 'externa'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def imprimir_BB(bd_path = "", bd_EFD_path = "", st = None, local = "", empresa = ""):
    with sl.connect(bd_path) as bd:

        colas = st.columns([1, 2, 1, 2, 1, 2, 1, 2, 1], gap='small')
        with colas[3]:
            F0 = st.button("F0 BB", width='stretch', key = "imprime_F0_BB")

        st.divider()
        
        with sl.connect(bd_EFD_path) as bd_EFD:
            if F0:
                n1 = imprimi_F0_BB(f'{local}\BB_ANLS',bd, empresa, st)
```

</details>

---

<a id="funcao-6"></a>

## exportar

Exporta dados para o Streamlit, incluindo a geração de HTML e manipulação de bancos de dados.

A função exporta dados para o Streamlit, utilizando informações armazenadas em sessões do Streamlit. Ela cria um arquivo de banco de dados SQLite e inicializa detalhes e rastreamento. A função também imprime diferentes tipos de relatórios dependendo do processo selecionado.

### Assinatura

```python
def exportar(st=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `st` | `object` | Objeto Streamlit para interação com a interface web. |

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
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
```

</details>

---
