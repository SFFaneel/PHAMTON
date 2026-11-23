# Referência de Funções

## Índice

- [visualizar_docs](#funcao-1)

---

<a id="funcao-1"></a>

## visualizar_docs

Visualiza documentos e arquivos em diferentes abas de uma interface Streamlit.

A função `visualizar_docs` exibe conteúdo HTML e PDF em diferentes abas de uma interface Streamlit. Ela lê arquivos CSS e HTML para renderizar o conteúdo, além de lidar com a visualização de um arquivo PDF específico.

### Assinatura

```python
def visualizar_docs(st=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `st` | `streamlit` | Objeto Streamlit usado para criar e gerenciar a interface da aplicação. |

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def visualizar_docs(st=None):
    st.info("Visite regularmente o sitio da Aneel para versão mais atualizada.", icon="🚨")
    tab1, tab4, tab2, tab3, tab5 = st.tabs(["MCPSE", "PRORET 2.3", "MCSE", "ROCT", "MDFEF"])

    with tab1:
        with open("html//MCPSE.css", encoding="utf-8", mode="r") as css_file:
            css_arq = css_file.read()
        with open("html//MCPSE.html", encoding="utf-8", mode="r") as html_file:
            html_arq = html_file.read()

        full_html = f"<style>{css_arq}</style>{html_arq}"

        with st.container(border=True):
            html(full_html, height=800, scrolling=True)

    with tab4:
        with open("html//MCPSE.css", encoding="utf-8", mode="r") as css_file:
            css_arq2 = css_file.read()
        with open("html//PRORET_2_3.html", encoding="utf-8", mode="r") as html_file:
            html_arq2 = html_file.read()

        full_html2 = f"<style>{css_arq2}</style>{html_arq2}"

        with st.container(border=True):
            html(full_html2, height=800, scrolling=True)
    with tab2:
        with open("html//MCPSE.css", encoding="utf-8", mode="r") as css_file:
            css_arq1 = css_file.read()
        with open("html//MCSE.html", encoding="utf-8", mode="r") as html_file:
            html_arq1 = html_file.read()

        full_html1 = f"<style>{css_arq1}</style>{html_arq1}"

        with st.container(border=True):
            html(full_html1, height=800, scrolling=True)
    with tab3:
        with open("html//MCPSE.css", encoding="utf-8", mode="r") as css_file:
                    css_arq1 = css_file.read()
        with open("html//ROCTax.html", encoding="utf-8", mode="r") as html_file:
            html_arq1 = html_file.read()

        full_html1 = f"<style>{css_arq1}</style>{html_arq1}"

        with st.container(border=True):
            html(full_html1, height=800, scrolling=True)
    with tab5:
        caminho = Path(r"html\Manual_Dados_SFF_Rev1.3.pdf")
        if caminho.is_file():
            st.pdf(caminho.read_bytes(), height=600)
        else:
            st.error(f"Arquivo não encontrado: {caminho}")
```

</details>

---
