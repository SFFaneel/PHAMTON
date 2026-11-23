# Referência de Funções

## Índice

- [visualizar](#funcao-1)

---

<a id="funcao-1"></a>

## visualizar

Visualiza resultados de acordo com o processo selecionado.

Esta função visualiza os resultados baseados no processo selecionado, utilizando abas para diferentes tipos de visualizações. Se nenhum processo for encontrado ou estiver incompleto, exibe mensagens de erro.

### Assinatura

```python
def visualizar(st=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `st` | `streamlit` | Objeto Streamlit para interação com a interface do usuário. |

### Dependências

- `{'nome': 'DASHBOARDS.visualizador_AIS', 'tipo': 'módulo'}`
- `{'nome': 'DASHBOARDS.visualizador_BB', 'tipo': 'módulo'}`
- `{'nome': 'DASHBOARDS.visualizador_BC', 'tipo': 'módulo'}`
- `{'nome': 'DASHBOARDS.visualizador_BDGD', 'tipo': 'módulo'}`
- `{'nome': 'DASHBOARDS.visualizador_INCR', 'tipo': 'módulo'}`
- `{'nome': 'DASHBOARDS.visualizador_OE', 'tipo': 'módulo'}`
- `{'nome': 'DASHBOARDS.visualizador_resumo_cmp', 'tipo': 'módulo'}`
- `{'nome': 'SRC.ais_funcoes.abertura_voc', 'tipo': 'módulo'}`
- `{'nome': 'UTILS.bsc_dados_reg', 'tipo': 'módulo'}`
- `{'nome': 'UTILS.existe_tabela', 'tipo': 'módulo'}`
- `{'nome': 'datetime.date', 'tipo': 'biblioteca Python'}`
- `{'nome': 'pandas', 'tipo': 'biblioteca Python'}`
- `{'nome': 'sqlite3', 'tipo': 'biblioteca Python'}`
- `{'nome': 'streamlit', 'tipo': 'biblioteca Python'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def visualizar(st=None):
    if st is None:
        import streamlit as st

    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
    st.html(f"<style>{css}</style>")
    bd_path = f'{local}/BD_LOCAL/{empresa}_{ano}.db'
    st.html(f"""<h1 style="text-align: center;">Trilha de Visualização de Resultados</h1><br><br>
                <p  style="text-align: justify;text-indent: 40px">Nesta aba temos as visualizações 
                de resultados. Guie-se pelo seletor abaixo:</p>  
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
                abas = ['AIS', 'BDGD', 'ABERTURA VOC', 'BANCO COMPRAS', 
                        'INCREMENTAL', 'MOVIMENTAÇÃO OE', 'MOVIMENTAÇÃO BB',
                        'RESUMO']
                tab = st.tabs(abas)
                
                with tab[0]:
                    visualizador_AIS(st)
                with tab[1]:
                    visualizador_BDGD(st)
                with tab[2]:
                    if st.session_state.dt_fim > date.today():
                        abertura_voc(st, True, html_config = True)
                    else:
                        abertura_voc(st, html_config = True)
                with tab[3]:
                    visualizador_BC(st)
                with tab[4]:
                    visualizador_INCR(st)
                with tab[5]:
                    visualizador_OE(st)     
                with tab[7]:
                    visualizador_resumo_cmp(st) 
                with tab[6]:
                    visualizador_BB(st)
            elif processo == 'DISTRIBUIDORA ANUAL':
                abas = ['AIS', 'BDGD', 'ABERTURA VOC', 'BANCO COMPRAS']
                tab = st.tabs(abas)

                with tab[0]:
                    visualizador_AIS(st)
                with tab[1]:
                    visualizador_BDGD(st)
                with tab[2]:
                    if st.session_state.dt_fim > date.today():
                        abertura_voc(st, True, html_config = True)
                    else:
                        abertura_voc(st, html_config = True)
                with tab[3]:
                    visualizador_BC(st)
            else:
                st.warning(f"Não implantado para {processo}")
```

</details>

---
