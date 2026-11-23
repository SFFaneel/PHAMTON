# Referência de Funções

## Índice

- [_utc_now](#funcao-1)
- [_connect](#funcao-2)
- [inicializa_database](#funcao-3)
- [inicio_execucao](#funcao-4)
- [execucao_finalizada](#funcao-5)
- [execucao_trilha](#funcao-6)
- [busca_execucao](#funcao-7)
- [lista_execucoes](#funcao-8)
- [busca_log_execucao](#funcao-9)

---

<a id="funcao-1"></a>

## _utc_now

Retorna a data e hora atual no formato UTC.

Obtém a data e hora atual em UTC e formata-a como uma string ISO 8601, incluindo microsegundos.

### Assinatura

```python
def _utc_now() -> str:
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Retorno

**Tipo:** `str`

Data e hora no formato UTC em ISO 8601 com microsegundos.

### Dependências

- `datetime.datetime`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")
```

</details>

---

<a id="funcao-2"></a>

## _connect

Estabelece uma conexão com um banco de dados SQLite e retorna uma iteração sobre essa conexão.

A função `_connect` é responsável por estabelecer uma conexão com um banco de dados SQLite. Ela aceita como parâmetro `db_path`, que pode ser uma instância de `sqlite3.Connection`, uma string ou um objeto do tipo `Path`. A função retorna um iterador sobre a conexão, garantindo que ela seja fechada corretamente após o uso.

### Assinatura

```python
# Consulte o código-fonte de _connect
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `db_path` | `sqlite3.Connection \| str \| Path` | Caminho para o banco de dados SQLite ou uma instância já aberta de `sqlite3.Connection`. |

### Retorno

**Tipo:** `Iterator[sqlite3.Connection]`

Iterador que produz a conexão com o banco de dados SQLite.

### Exceções

- **`TypeError`**: Quando `db_path` não é uma instância de `str`, `Path` ou `sqlite3.Connection`.

### Dependências

- `pathlib.Path`
- `sqlite3`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _connect(
                db_path: sqlite3.Connection | str | Path,
            ) -> Iterator[sqlite3.Connection]:

    if isinstance(db_path, sqlite3.Connection):
        yield db_path
        return

    if not isinstance(db_path, (str, Path)):
        raise TypeError(
                            "db_path deve ser str, Path ou sqlite3.Connection"
                        )

    path = Path(db_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path), timeout=30)

    try:
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.execute("PRAGMA foreign_keys = ON")

        yield conn
        conn.commit()

    except BaseException:
        conn.rollback()
        raise

    finally:
        conn.close()
```

</details>

---

<a id="funcao-3"></a>

## inicializa_database

Inicializa a base de dados SQLite para armazenar informações sobre execuções de scripts.

Cria uma tabela chamada 'tbl_manifesto_execucao' se ela não existir e adiciona índices para melhorar o desempenho das consultas. A tabela contém campos para identificar a execução, detalhes do script, estado da execução e informações de erro.

### Assinatura

```python
def inicializa_database(db_path: sqlite3.Connection | str | Path) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `db_path` | `sqlite3.Connection \| str \| Path` | Caminho para o arquivo do banco de dados SQLite ou uma conexão existente. |

### Retorno

**Tipo:** `None`

Nenhum valor é retornado.

### Dependências

- `sqlite3`

<details>
<summary>Visualizar código-fonte</summary>

```python
def inicializa_database(db_path: sqlite3.Connection | str | Path) -> None:
    with _connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tbl_manifesto_execucao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execucao_id TEXT NOT NULL UNIQUE,
                script_nome TEXT NOT NULL,
                script_versao TEXT NOT NULL,
                executado_por TEXT NOT NULL,
                hostname TEXT,
                iniciado_em TEXT NOT NULL,
                finalizado_em TEXT,
                estado TEXT NOT NULL CHECK(estado IN ('RODANDO','SUCESSO','FALHA')),
                erro_tipo TEXT,
                erro_mensagem TEXT,
                erro_rastreamento TEXT,
                parametros TEXT CHECK(parametros IS NULL OR json_valid(parametros)),
                CHECK(estado = 'RODANDO' OR finalizado_em IS NOT NULL),
                CHECK(estado != 'FALHA' OR erro_mensagem IS NOT NULL)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_manifesto_script ON tbl_manifesto_execucao(script_nome, iniciado_em)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_manifesto_estado ON tbl_manifesto_execucao(estado, iniciado_em)")
```

</details>

---

<a id="funcao-4"></a>

## inicio_execucao

Inicia a execução de um script em um banco de dados SQLite.

Registra uma nova execução no banco de dados, armazenando informações sobre o script e seus parâmetros. Valida se os nomes do script e da versão estão presentes e não vazios. Gera um ID único para a execução e insere registros no banco de dados.

### Assinatura

```python
# Consulte o código-fonte de inicio_execucao
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `db_path` | `sqlite3.Connection \| str \| Path` | Conexão com o banco de dados ou caminho do arquivo do banco de dados. |
| `script_nome` | `str` | Nome do script a ser executado. |
| `script_versao` | `str` | Versão do script a ser executado. |
| `parametros` | `Any` | Parâmetros adicionais para o script, serializados em JSON. |

### Retorno

**Tipo:** `str`

ID único gerado para a execução do script.

### Exceções

- **`ValueError`**: Quando o nome do script ou da versão está vazio.

### Dependências

- `getpass`
- `json`
- `socket`
- `uuid`

<details>
<summary>Visualizar código-fonte</summary>

```python
def inicio_execucao(
                        db_path: sqlite3.Connection | str | Path,
                        script_nome: str,
                        script_versao: str = "1.0.0",
                        parametros: Any = None,
                    ) -> str:

    if not script_nome or not script_nome.strip():
        raise ValueError("script_nome é obrigatório")
    if not script_versao or not script_versao.strip():
        raise ValueError("script_versao é obrigatório")
    params_json = json.dumps(parametros, ensure_ascii=False, allow_nan=False) if parametros is not None else None
    inicializa_database(db_path)
    execucao_id  = str(uuid.uuid4())
    with _connect(db_path) as conn:
        conn.execute("""
            INSERT INTO tbl_manifesto_execucao (
                execucao_id, script_nome, script_versao, executado_por,
                hostname, iniciado_em, estado, parametros
            ) VALUES (?, ?, ?, ?, ?, ?, 'RODANDO', ?)
        """, (execucao_id, script_nome, script_versao,
              getpass.getuser(), socket.gethostname(), _utc_now(), params_json))
    return execucao_id
```

</details>

---

<a id="funcao-5"></a>

## execucao_finalizada

Atualiza o status de execução em um banco de dados SQLite.

Esta função atualiza o registro de uma execução no banco de dados, marcando-a como finalizada e registrando informações sobre seu sucesso ou falha. Se a execução falhar, é necessário fornecer um erro correspondente.

### Assinatura

```python
# Consulte o código-fonte de execucao_finalizada
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `db_path` | `sqlite3.Connection \| str \| Path` | Conexão existente com o banco de dados ou caminho para o arquivo do banco de dados. |
| `execucao_id` | `str` | Identificador único da execução a ser atualizada. |
| `sucesso` | `bool` | Indica se a execução foi concluída com sucesso. Se for `False`, é necessário fornecer um erro. |
| `erro` | `BaseException \| str \| None` | Erro ocorrido durante a execução, se houver. Se `sucesso` for `False`, este parâmetro é obrigatório. |

### Retorno

**Tipo:** `None`

Nenhum valor retornado.

### Exceções

- **`ValueError`**: Quando uma falha é indicada (`sucesso=False`) mas nenhum erro foi fornecido.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def execucao_finalizada(
                            db_path: sqlite3.Connection | str | Path,
                            execucao_id: str,
                            sucesso: bool = True,
                            erro: BaseException | str | None = None,
                        ) -> None:
    
    if not sucesso and erro is None:
        raise ValueError("Uma falha precisa conter um erro")
    erro_tipo = erro_mensagem = erro_rastreamento = None
    if not sucesso:
        if isinstance(erro, BaseException):
            erro_tipo = type(erro).__name__
            erro_mensagem = str(erro) or erro_tipo
            erro_rastreamento = "".join(traceback.format_exception(type(erro), erro, erro.__traceback__))
        else:
            erro_tipo = "Falha Manual"
            erro_mensagem = str(erro) or "Falha não especificada"
    with _connect(db_path) as conn:
        cursor = conn.execute("""
            UPDATE tbl_manifesto_execucao
               SET finalizado_em = ?, estado = ?, erro_tipo = ?,
                   erro_mensagem = ?, erro_rastreamento = ?
             WHERE execucao_id = ? AND estado = 'RODANDO'
        """, (_utc_now(), "SUCESSO" if sucesso else "FALHA",
              erro_tipo, erro_mensagem, erro_rastreamento, execucao_id))
        if cursor.rowcount != 1:
            raise ValueError(f"Execução inexistente ou já finalizada: {execucao_id}")
```

</details>

---

<a id="funcao-6"></a>

## execucao_trilha

Executa um script em uma trilha e retorna o ID da execução.

Esta função inicia a execução de um script em uma trilha, rastreia seu progresso e finaliza com sucesso ou falha. Ela utiliza um contexto de rastreamento para monitorar a execução e registra os resultados no banco de dados.

### Assinatura

```python
# Consulte o código-fonte de execucao_trilha
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `db_path` | `sqlite3.Connection \| str \| Path` | Conexão com o banco de dados ou caminho do arquivo do banco de dados. |
| `script_nome` | `str` | Nome do script a ser executado. |
| `script_versao` | `str` | Versão do script a ser executado. |
| `parametros` | `Any` | Parâmetros adicionais para o script, se necessário. |

### Retorno

**Tipo:** `Iterator[str]`

Iterador que retorna o ID da execução.

### Exceções

- **`BaseException`**: Qualquer exceção que ocorra durante a execução do script será capturada e rethrown com uma nota adicional indicando um problema na auditoria.

### Dependências

- `manifesto_exec_detalhes.contexto_rastreamento`

<details>
<summary>Visualizar código-fonte</summary>

```python
def execucao_trilha(
                        db_path: sqlite3.Connection | str | Path,
                        script_nome: str,
                        script_versao: str = "1.0.0",
                        parametros: Any = None,
                    ) -> Iterator[str]:


    execucao_id = inicio_execucao(
                                    db_path,
                                    script_nome,
                                    script_versao,
                                    parametros,
                                )

    try:
        with contexto_rastreamento(db_path, execucao_id):
            yield execucao_id

    except BaseException as exc:
        try:
            execucao_finalizada(
                                    db_path,
                                    execucao_id,
                                    sucesso=False,
                                    erro=exc,
                                )
        except Exception as erro_auditoria:
            exc.add_note(
                            "Não foi possível registrar a falha "
                            f"no manifesto: {erro_auditoria}"
                        )
        raise

    else:
        execucao_finalizada(
                                db_path,
                                execucao_id,
                                sucesso=True,
                            )
```

</details>

---

<a id="funcao-7"></a>

## busca_execucao

Busca uma execução no banco de dados.

Realiza a busca por uma execução específica no banco de dados utilizando o ID da execução fornecido. Retorna os detalhes da execução como um dicionário ou None se não encontrar.

### Assinatura

```python
def busca_execucao(db_path: sqlite3.Connection | str | Path, execucao_id : str) -> dict[str, Any] | None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `db_path` | `sqlite3.Connection \| str \| Path` | Caminho para o banco de dados ou conexão já estabelecida. |
| `execucao_id` | `str` | ID da execução que será buscada no banco de dados. |

### Retorno

**Tipo:** `dict[str, Any] | None`

Detalhes da execução encontrada como um dicionário ou None se não encontrar.

### Dependências

- `_connect`
- `conn.execute`
- `dict`
- `fetchone`
- `inicializa_database`

<details>
<summary>Visualizar código-fonte</summary>

```python
def busca_execucao(db_path: sqlite3.Connection | str | Path, execucao_id : str) -> dict[str, Any] | None:

    inicializa_database(db_path)
    with _connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM tbl_manifesto_execucao WHERE execucao_id  = ?", (execucao_id ,)).fetchone()
        return dict(row) if row is not None else None
```

</details>

---

<a id="funcao-8"></a>

## lista_execucoes

Lista execuções de scripts em um banco de dados SQLite.

Retorna uma lista de dicionários contendo as informações das execuções de scripts armazenadas no banco de dados SQLite, filtrando por nome do script e estado, se especificados. O resultado é limitado pelo número fornecido.

### Assinatura

```python
# Consulte o código-fonte de lista_execucoes
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `db_path` | `sqlite3.Connection \| str \| Path` | Conexão SQLite ou caminho para o arquivo do banco de dados. |
| `script_nome` | `str \| None` | Nome do script a ser filtrado. Se None, não há filtro por nome. |
| `estado` | `str \| None` | Estado da execução a ser filtrado (RODANDO, SUCESSO, FALHA). Se None, não há filtro por estado. |
| `limite` | `int` | Número máximo de resultados a serem retornados. Deve ser um inteiro positivo. |

### Retorno

**Tipo:** `list[dict[str, Any]]`

Lista de dicionários contendo informações das execuções filtradas.

### Exceções

- **`ValueError`**: Quando o valor de 'limite' não é um inteiro positivo.
- **`ValueError`**: Quando o valor de 'estado' não é válido (RODANDO, SUCESSO, FALHA).

### Dependências

- `{'nome': '_connect', 'categoria': 'chamada', 'descricao': 'Função para estabelecer uma conexão com o banco de dados.'}`
- `{'nome': 'args.append', 'categoria': 'chamada', 'descricao': 'Método para adicionar elementos à lista de argumentos SQL.'}`
- `{'nome': 'conn.execute', 'categoria': 'chamada', 'descricao': 'Método para executar uma consulta SQL no banco de dados.'}`
- `{'nome': 'dict', 'categoria': 'chamada', 'descricao': 'Função para converter um objeto Row em um dicionário.'}`
- `{'nome': 'fetchall', 'categoria': 'chamada', 'descricao': 'Método para recuperar todos os resultados de uma consulta SQL.'}`
- `{'nome': 'inicializa_database', 'categoria': 'chamada', 'descricao': 'Função para inicializar o banco de dados, se necessário.'}`
- `{'nome': 'isinstance', 'categoria': 'chamada', 'descricao': 'Função para verificar o tipo de um objeto.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def lista_execucoes(
                        db_path: sqlite3.Connection | str | Path,
                        script_nome: str | None = None,
                        estado: str | None = None,
                        limite: int = 100,
                    ) -> list[dict[str, Any]]:
  
    if not isinstance(limite, int) or isinstance(limite, bool) or limite < 1:
        raise ValueError("limite deve ser um inteiro positivo")
    if estado is not None and estado not in ("RODANDO", "SUCESSO", "FALHA"):
        raise ValueError("estado inválido")
    inicializa_database(db_path)
    sql = "SELECT * FROM tbl_manifesto_execucao WHERE 1=1"
    args: list[Any] = []
    if script_nome is not None:
        sql += " AND script_nome = ?"
        args.append(script_nome)
    if estado is not None:
        sql += " AND estado = ?"
        args.append(estado)
    sql += " ORDER BY iniciado_em DESC, id DESC LIMIT ?"
    args.append(limite)
    with _connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(sql, args).fetchall()]
```

</details>

---

<a id="funcao-9"></a>

## busca_log_execucao

Cria um adaptador de logger para rastrear logs com base em uma execução específica.

Esta função cria e retorna um adaptador de logger que adiciona o ID da execução como um contexto no registro dos logs. Lança um erro se o ID da execução não for fornecido ou for uma string vazia.

### Assinatura

```python
def busca_log_execucao(execucao_id : str, name: str = "execucao"):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `execucao_id` | `str` | Identificador único da execução que será usado para rastrear os logs. |
| `name` | `str` | Nome do logger a ser adaptado. O padrão é 'execucao'. |

### Retorno

**Tipo:** `Não especificado`

Adaptador de logger configurado com o ID da execução.

### Exceções

- **`ValueError`**: Quando o ID da execução não é fornecido ou é uma string vazia.

### Dependências

- `logging`

<details>
<summary>Visualizar código-fonte</summary>

```python
def busca_log_execucao(execucao_id : str, name: str = "execucao"):

    import logging

    if not execucao_id  or not execucao_id .strip():
        raise ValueError("execucao_id  é obrigatório")
    return logging.LoggerAdapter(logging.getLogger(name), {"execucao_id ": execucao_id })
```

</details>

---
