# Referência de Funções

## Índice

- [pagina_manifesto](#funcao-1)
- [pagina_ECD](#funcao-2)
- [pagina_CVA](#funcao-3)
- [visual](#funcao-4)
- [criar_rel](#funcao-5)
- [ler_normas](#funcao-6)

---

<a id="funcao-1"></a>

## pagina_manifesto

Exibe uma interface de usuário com duas abas: 'DADOS' e 'EXECUÇÃO'.

A função cria uma interface de usuário utilizando Streamlit, dividida em duas abas. A aba 'EXECUÇÃO' exibe um manifesto de execução, enquanto a aba 'DADOS' exibe dados relacionados.

### Assinatura

```python
def pagina_manifesto():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Dependências

- `{'nome': 'MANIFESTO.visual_manifesto', 'tipo': 'função', 'descricao': 'Função que visualiza dados.'}`
- `{'nome': 'MANIFESTO.visualizar_manifesto_exec', 'tipo': 'função', 'descricao': 'Função que visualiza um manifesto de execução.'}`
- `{'nome': 'pathlib.Path', 'tipo': 'classe', 'descricao': 'Classe para manipulação de caminhos de arquivo.'}`
- `{'nome': 'streamlit', 'tipo': 'biblioteca', 'descricao': 'Biblioteca para criação de interfaces web interativas.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
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
```

</details>

---

<a id="funcao-2"></a>

## pagina_ECD

Executa a função de leitura inicial do ECD (Eletrônico da Contabilidade Digital) se o arquivo 'anl_desc_hist.py' existir no diretório atual.

A função verifica a existência do arquivo 'anl_desc_hist.py' no diretório atual. Se o arquivo existir, ele importa e executa a função `inic_ECD_leitura` definida nesse arquivo.

### Assinatura

```python
def pagina_ECD():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Dependências

- `{'tipo': 'anl_desc_hist.inic_ECD_leitura', 'descricao': "Função que será chamada se o arquivo 'anl_desc_hist.py' existir."}`
- `{'tipo': 'pathlib.Path', 'descricao': 'Classe utilizada para manipulação de caminhos de arquivos.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def pagina_ECD():
        caminho_CVA = Path.cwd() / "anl_desc_hist.py"
        if caminho_CVA.exists():
            from anl_desc_hist import inic_ECD_leitura
            inic_ECD_leitura()
```

</details>

---

<a id="funcao-3"></a>

## pagina_CVA

Executa a função `calc_CVA` do módulo `anl_ECD_CVA_PTD.py`.

A função localiza o arquivo `anl_ECD_CVA_PTD.py` no diretório de trabalho atual e, se encontrado, importa e executa a função `calc_CVA` definida nesse módulo.

### Assinatura

```python
def pagina_CVA():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Dependências

- `{'tipo': 'anl_ECD_CVA_PTD.calc_CVA', 'descricao': 'Função a ser executada.'}`
- `{'tipo': 'pathlib.Path', 'descricao': 'Classe utilizada para manipulação de caminhos de arquivo.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def pagina_CVA():
        caminho_CVA = Path.cwd() / "anl_ECD_CVA_PTD.py"
        if caminho_CVA.exists():
            from anl_ECD_CVA_PTD import calc_CVA
            calc_CVA()
```

</details>

---

<a id="funcao-4"></a>

## visual

Invoca a função de visualização.

Esta função chama outra função chamada 'visualizar' passando um parâmetro 'st'. A função não possui parâmetros adicionais e não retorna nenhum valor explícito.

### Assinatura

```python
def visual():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Dependências

- `SRC.visualizar`

<details>
<summary>Visualizar código-fonte</summary>

```python
def visual():
        visualizar(st)
```

</details>

---

<a id="funcao-5"></a>

## criar_rel

Cria um relatório utilizando a função de exportação.

Esta função invoca a função `exportar` do módulo `RELATORIOS` para criar e exportar um relatório. Não recebe nenhum parâmetro e não retorna nada explícito.

### Assinatura

```python
def criar_rel():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Dependências

- `RELATORIOS.exportar`

<details>
<summary>Visualizar código-fonte</summary>

```python
def criar_rel():
        exportar(st)
```

</details>

---

<a id="funcao-6"></a>

## ler_normas

Lê e exibe as normas utilizando uma função de visualização.

Esta função não recebe nenhum parâmetro e chama outra função para visualizar os documentos relacionados às normas. Não há retorno explícito definido no código fornecido.

### Assinatura

```python
def ler_normas():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Dependências

- `UTILS.visualizar_docs`

<details>
<summary>Visualizar código-fonte</summary>

```python
def ler_normas():
        visualizar_docs(st)
```

</details>

---
