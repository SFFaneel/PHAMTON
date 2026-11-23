# Referência de Funções

## Índice

- [carregar_configuracao](#funcao-1)
- [salvar_configuracao](#funcao-2)
- [converter_data](#funcao-3)
- [validar_diretorio](#funcao-4)
- [criar_estrutura](#funcao-5)
- [aplicar_configuracao](#funcao-6)
- [confirmar_exclusao](#funcao-7)
- [iniciar](#funcao-8)

---

<a id="funcao-1"></a>

## carregar_configuracao

Carrega a configuração de trabalho a partir de um arquivo CSV.

A função carrega as configurações de trabalho a partir de um arquivo CSV, se existir. Caso contrário, retorna um dicionário padrão com valores vazios ou preenchidos com os últimos valores disponíveis no arquivo.

### Assinatura

```python
def carregar_configuracao() -> dict:
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Retorno

**Tipo:** `dict`

Configurações de trabalho carregadas.

### Exceções

- **`OSError`**: Quando ocorre um erro ao acessar o arquivo de configuração.
- **`ValueError`**: Quando a estrutura do arquivo CSV é inválida.
- **`pd.errors.ParserError`**: Quando ocorre um erro ao ler o arquivo CSV.

### Dependências

- `pandas`
- `pathlib.Path`
- `streamlit`

<details>
<summary>Visualizar código-fonte</summary>

```python
def carregar_configuracao() -> dict:
    padrao = {
                    "dir_trab": str(Path.home() / "Downloads" / "TRABALHO"),
                    "nm_emp": "",
                    "dt_ini": "",
                    "dt_fim": "",
                }

    if not ARQUIVO_CONFIG.is_file():
        return padrao

    try:
        df = pd.read_csv(
                            ARQUIVO_CONFIG,
                            sep="|",
                            encoding="Latin-1",
                            dtype=str,
                            keep_default_na=False,
                        )

        if not {"cat", "dado"}.issubset(df.columns):
            raise ValueError("Estrutura inválida de tbl_ini.csv")

        for campo in CAMPOS_CONFIG:
            valores = df.loc[df["cat"] == campo, "dado"]
            if not valores.empty:
                padrao[campo] = str(valores.iloc[-1])

    except (OSError, ValueError, pd.errors.ParserError) as erro:
        st.warning(f"Configuração anterior não carregada: {erro}")

    return padrao
```

</details>

---

<a id="funcao-2"></a>

## salvar_configuracao

Salva as configurações em um arquivo CSV.

Converte um dicionário de configurações em um DataFrame e salva-o em um arquivo CSV com separador de coluna como pipe (|) e codificação Latin-1. O arquivo é salvo no caminho especificado por ARQUIVO_CONFIG.

### Assinatura

```python
def salvar_configuracao(config: dict) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `config` | `dict` | Dicionário contendo as configurações a serem salvas. |

### Retorno

**Tipo:** `None`

Nenhum valor retornado.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def salvar_configuracao(config: dict) -> None:
    df = pd.DataFrame(
                        {
                            "cat": CAMPOS_CONFIG,
                            "dado": [
                                str(config[campo])
                                for campo in CAMPOS_CONFIG
                            ],
                        }
                    )

    df.to_csv(
                ARQUIVO_CONFIG,
                sep="|",
                encoding="Latin-1",
                index=False,
            )
```

</details>

---

<a id="funcao-3"></a>

## converter_data

Converte uma string de data em um objeto date.

Tenta converter uma string no formato 'YYYY-MM-DD' em um objeto date. Se a conversão falhar ou o valor for vazio, retorna o padrão fornecido.

### Assinatura

```python
def converter_data(valor: str, padrao: date) -> date:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `str` | String representando uma data no formato 'YYYY-MM-DD'. |
| `padrao` | `date` | Valor padrão a ser retornado em caso de falha na conversão. |

### Retorno

**Tipo:** `date`

Objeto date resultante da conversão ou o valor padrão.

### Exceções

- **`ValueError`**: Quando a string de data não está no formato 'YYYY-MM-DD'.

### Dependências

- `datetime.date`
- `datetime.datetime`

<details>
<summary>Visualizar código-fonte</summary>

```python
def converter_data(valor: str, padrao: date) -> date:
    if not valor:
        return padrao

    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError:
        return padrao
```

</details>

---

<a id="funcao-4"></a>

## validar_diretorio

Valida um caminho de diretório e retorna uma instância de Path.

Verifica se o caminho fornecido é válido, não sendo a raiz do disco, a pasta do usuário ou a pasta da aplicação. Caso contrário, lança exceções específicas.

### Assinatura

```python
def validar_diretorio(caminho: str) -> Path:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `caminho` | `str` | Caminho do diretório que será validado. |

### Retorno

**Tipo:** `Path`

Instância de Path representando o caminho válido.

### Exceções

- **`ValueError`**: Quando o caminho está vazio.
- **`ValueError`**: Quando o caminho é a raiz do disco.
- **`ValueError`**: Quando o caminho é a pasta do usuário.
- **`ValueError`**: Quando o caminho é a pasta da aplicação.

### Dependências

- `pathlib.Path`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_diretorio(caminho: str) -> Path:
    if not caminho.strip():
        raise ValueError("Informe o diretório de trabalho.")

    raiz = Path(caminho.strip()).expanduser().resolve()

    if raiz == Path(raiz.anchor):
        raise ValueError("Não é permitido usar a raiz do disco.")

    if raiz == Path.home().resolve():
        raise ValueError("Não é permitido usar a pasta do usuário.")

    if raiz == Path.cwd().resolve():
        raise ValueError(
                            "O diretório de trabalho não pode ser a pasta da aplicação."
                        )

    return raiz
```

</details>

---

<a id="funcao-5"></a>

## criar_estrutura

Cria uma estrutura de diretórios em um caminho especificado.

A função cria a estrutura de diretórios definida em `DIRETORIOS_TRABALHO` e adiciona dois diretórios extras: 'LOGS' e 'MANIFESTO/TRILHA_EXEC'. Se o caminho já existir, não será lançada uma exceção.

### Assinatura

```python
def criar_estrutura(raiz: Path) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `raiz` | `Path` | Caminho onde a estrutura de diretórios será criada. |

### Retorno

**Tipo:** `None`

A função não retorna nenhum valor.

### Dependências

- `{'nome': 'DIRETORIOS_TRABALHO', 'categoria': 'constante', 'descricao': 'Lista de diretórios a serem criados dentro do caminho raiz.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def criar_estrutura(raiz: Path) -> None:
    raiz.mkdir(parents=True, exist_ok=True)
    for nome in DIRETORIOS_TRABALHO:
        (raiz / nome).mkdir(parents=True, exist_ok=True)
    (raiz / "LOGS").mkdir(parents=True, exist_ok=True)
    (raiz / "MANIFESTO" / "TRILHA_EXEC").mkdir(
                                                    parents=True,
                                                    exist_ok=True,
                                                )
```

</details>

---

<a id="funcao-6"></a>

## aplicar_configuracao

Aplica uma configuração em um diretório raiz, utilizando informações de empresa e datas.

Esta função cria a estrutura necessária no diretório raiz, configura um logger, salva as informações de configuração e atualiza o estado da sessão do Streamlit com os dados fornecidos. Também registra uma mensagem de log indicando que a configuração foi concluída.

### Assinatura

```python
# Consulte o código-fonte de aplicar_configuracao
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `raiz` | `Path` | O diretório raiz onde as operações serão realizadas. |
| `empresa` | `str` | O nome da empresa associada à configuração. |
| `data_ini` | `date` | A data inicial para a configuração. |
| `data_fim` | `date` | A data final para a configuração. |

### Retorno

**Tipo:** `None`

Não retorna nenhum valor.

### Dependências

- `{'nome': 'MANIFESTO.execucao_trilha', 'categoria': 'chamada'}`
- `{'nome': 'UTILS.configurar_logger', 'categoria': 'chamada'}`
- `{'nome': 'streamlit', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def aplicar_configuracao(
                            raiz: Path,
                            empresa: str,
                            data_ini: date,
                            data_fim: date,
                        ) -> None:
 
    criar_estrutura(raiz)
    pasta_execucao = raiz / "MANIFESTO" / "TRILHA_EXEC"
    with execucao_trilha(
                            db_path=str(pasta_execucao / "execucoes.db"),
                            script_nome="inicio",
                            script_versao="1.0.0",
                        ):
        
        logger = configurar_logger(nome_arquivo=empresa, diretorio_logs=str(raiz / "LOGS"),)
        config = {
                    "dir_trab": str(raiz),
                    "nm_emp": empresa,
                    "dt_ini": data_ini.isoformat(),
                    "dt_fim": data_fim.isoformat(),
                 }

        salvar_configuracao(config)
        st.session_state.update(
                                    {
                                        "tra_dir": str(raiz),
                                        "nm_empr": empresa,
                                        "dt_ini": data_ini,
                                        "dt_fim": data_fim,
                                        "RTE": False,
                                        "SIST_CONFIG": True,
                                        "LOGGER": logger,
                                        "database_MAN" : "",
                                        "execucao_id" : ""
                                    }
                                )
        logger.info(
                        "Configuração concluída: empresa=%s, diretório=%s",
                        empresa,
                        raiz,
                    )
```

</details>

---

<a id="funcao-7"></a>

## confirmar_exclusao

Confirma a exclusão de arquivos em um diretório específico.

Exibe uma mensagem de aviso e dois botões para confirmar ou cancelar a exclusão de todos os arquivos em um diretório. Se confirmado, exclui o diretório e aplica uma configuração específica.

### Assinatura

```python
# Consulte o código-fonte de confirmar_exclusao
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `raiz` | `Path` | Caminho do diretório que será excluído. |
| `empresa` | `str` | Nome da empresa associada à exclusão. |
| `data_ini` | `date` | Data inicial para a configuração. |
| `data_fim` | `date` | Data final para a configuração. |

### Retorno

**Tipo:** `None`

Nenhum valor retornado.

### Exceções

- **`ValueError`**: Quando o destino não é um diretório comum.

### Dependências

- `{'nome': 'UTILS.liberar_logger', 'categoria': 'importado', 'descricao': 'Função para liberar o logger.'}`
- `{'nome': 'shutil', 'categoria': 'importado', 'descricao': 'Biblioteca para operações de sistema de arquivos.'}`
- `{'nome': 'streamlit', 'categoria': 'importado', 'descricao': 'Framework web para criação de interfaces de usuário.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def confirmar_exclusao(
                            raiz: Path,
                            empresa: str,
                            data_ini: date,
                            data_fim: date,
                        ) -> None:
    st.warning(
                    f"Todos os arquivos de **{raiz}** serão excluídos "
                    "permanentemente. Esta ação não pode ser desfeita."
                )

    _, col_sim, _, col_nao, _  = st.columns([1,2,1,2,1])

    with col_sim:
        if st.button(
                    "Sim, apagar",
                    type="primary",
                ):
            try:
                if raiz.exists():
                    if not raiz.is_dir() or raiz.is_symlink():
                        raise ValueError(
                                            "O destino não é um diretório comum."
                                        )
                    liberar_logger(raiz)
                    shutil.rmtree(raiz)

                aplicar_configuracao(
                                        raiz, empresa, data_ini, data_fim
                                    )
            except Exception as erro:
                st.error(f"Falha na configuração: {erro}")
                return

            st.session_state["config_sucesso"] = (
                                                    f"Diretório {raiz} configurado com sucesso."
                                                )
            st.rerun()

    with col_nao:
        if st.button(
                        "Não, cancelar",
                    ):
            st.rerun()
```

</details>

---

<a id="funcao-8"></a>

## iniciar

Inicia a interface do usuário e configura o ambiente de trabalho.

Carrega as configurações iniciais, carrega os dados necessários e exibe uma interface para seleção de empresa e período. Realiza validações e aplica a configuração no diretório de trabalho selecionado.

### Assinatura

```python
def iniciar() -> None:
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Retorno

**Tipo:** `None`

Nenhum valor retornado.

### Exceções

- **`Exception`**: Quando ocorre um erro durante a configuração do ambiente de trabalho.

### Dependências

- `UTILS.bsc_dados_reg`
- `datetime.date`
- `streamlit`

<details>
<summary>Visualizar código-fonte</summary>

```python
def iniciar() -> None:
    config = carregar_configuracao()
    css = bsc_dados_reg("estilo_001",tipo="Estilo_CSS")
    if isinstance(css, str) and css:
        st.html(f"<style>{css}</style>")

    st.html(
                    """<p style="text-align: justify;text-indent: 40px; padding-top: 10px">
                    Defina um diretório de trabalho. Caso já exista, 
                    seus arquivos serão preservados, exceto quando 
                    a opção de exclusão for selecionada.</p>"""
                )

    st.caption(f"Endereço do aplicativo: {st.context.url}")
    st.divider()
    apagar = st.checkbox("Excluir diretório, se existir", value=False,)

    tra_dir = st.text_input("Diretório de trabalho", value=config["dir_trab"],)
    empresas = bsc_dados_reg("TBL_EMPRESAS")

    if (not isinstance(empresas, pd.DataFrame) or "Nm_EMPRESA" not in empresas.columns):
        st.error("Não foi possível carregar o cadastro de empresas.")
        return

    lista_empresas = (
                        empresas["Nm_EMPRESA"]
                        .dropna()
                        .astype(str)
                        .drop_duplicates()
                        .tolist()
                    )

    if not lista_empresas:
        st.error("Nenhuma empresa cadastrada.")
        return

    empresa_padrao = config["nm_emp"]

    indice = (
                lista_empresas.index(empresa_padrao)
                if empresa_padrao in lista_empresas
                else 0
            )

    hoje = date.today()

    data_ini_padrao = converter_data(config["dt_ini"], hoje)
    data_fim_padrao = converter_data(config["dt_fim"], hoje)

    data_min_ini = (
                        date(1900, 1, 1)
                        if data_ini_padrao.year == 1900
                        else date(2019, 1, 1)
                    )

    data_max = date(hoje.year + 5, 12, 31)

    col1, col2, col3 = st.columns(3)

    with col1:
        empresa = st.selectbox(
                                "Empresa:",
                                lista_empresas,
                                index=indice,
                            )

    with col2:
        data_ini = st.date_input(
                                    "Data inicial período incremental:",
                                    value=data_ini_padrao,
                                    min_value=data_min_ini,
                                    max_value=data_max,
                                )

    with col3:
        data_fim = st.date_input(
                                    "Data final período incremental:",
                                    value=data_fim_padrao,
                                    min_value=date(hoje.year - 10, 1, 1),
                                    max_value=data_max,
                                )

    st.divider()

    _, centro, _ = st.columns([2, 1, 2])

    with centro:
        configurar = st.button(
                                    "(RE)Configurar",
                                    type="primary",
                                    use_container_width=True,
                                )

    if mensagem := st.session_state.pop("config_sucesso", None):
        st.success(mensagem)

    if not configurar:
        return

    if data_fim <= data_ini:
        st.error(
                    "A data final deve ser posterior à data inicial."
                )
        return

    try:
        raiz = validar_diretorio(tra_dir)

        if apagar and raiz.exists():
            confirmar_exclusao(
                                    raiz, empresa, data_ini, data_fim
                                )
            return

        with st.spinner("Configurando ambiente de trabalho..."):
            aplicar_configuracao(raiz, empresa, data_ini, data_fim)

        st.success(f"Diretório {raiz} configurado com sucesso.")

    except Exception as erro:
        st.error(f"Erro ao configurar ambiente: {erro}")
```

</details>

---
