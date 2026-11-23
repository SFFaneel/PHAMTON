# Referência de Funções

## Índice

- [_agora](#funcao-1)
- [caminho_auditoria](#funcao-2)
- [_conexao](#funcao-3)
- [inicializa_detalhes](#funcao-4)
- [serializar_json](#funcao-5)
- [registrar_evento](#funcao-6)
- [registrar_metrica](#funcao-7)
- [registrar_artefato](#funcao-8)
- [listar_detalhes](#funcao-9)
- [inicializar_rastreamento](#funcao-10)
- [contexto_rastreamento](#funcao-11)
- [rastrear_funcao](#funcao-12)
- [listar_chamadas](#funcao-13)
- [wrapper](#funcao-14)

---

<a id="funcao-1"></a>

## _agora

Retorna a data e hora atual em formato ISO 8601 UTC.

Obtém a data e hora atual no fuso horário UTC e formata-a como uma string conforme o padrão ISO 8601.

### Assinatura

```python
def _agora() -> str:
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Retorno

**Tipo:** `str`

Data e hora atual em formato ISO 8601 UTC.

### Dependências

- `datetime.datetime`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()
```

</details>

---

<a id="funcao-2"></a>

## caminho_auditoria

Obtém o caminho do arquivo SQLite associado a uma conexão de banco de dados.

Retorna o caminho absoluto do arquivo SQLite associado à conexão fornecida. Se a conexão for em memória, lança um erro. Caso contrário, retorna o caminho resolvido e expandido do arquivo SQLite.

### Assinatura

```python
def caminho_auditoria(database: sqlite3.Connection | str | Path) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `database` | `sqlite3.Connection \| str \| Path` | Conexão de banco de dados ou caminho para um arquivo SQLite. |

### Retorno

**Tipo:** `str`

Caminho absoluto do arquivo SQLite associado à conexão.

### Exceções

- **`ValueError`**: Quando a conexão em memória não suporta auditoria independente; forneça um caminho SQLite.
- **`ValueError`**: Quando o caminho é ':memory:' ou começa com 'file:', use um caminho de arquivo SQLite, não URI ou :memory:, para auditoria independente.
- **`TypeError`**: Quando o tipo do parâmetro database não é sqlite3.Connection, str ou Path.

### Dependências

- `pathlib.Path`

<details>
<summary>Visualizar código-fonte</summary>

```python
def caminho_auditoria(database: sqlite3.Connection | str | Path) -> str:
    if isinstance(database, sqlite3.Connection):
        rows = database.execute('PRAGMA database_list').fetchall()
        main = next((r[2] for r in rows if r[1] == 'main'), '')
        if not main:
            raise ValueError('Conexão em memória não suporta auditoria independente; forneça um caminho SQLite.')
        return str(Path(main).resolve())
    if isinstance(database, (str, Path)):
        path = str(database)
        if path == ':memory:' or path.startswith('file:'):
            raise ValueError('Use um caminho de arquivo SQLite, não URI ou :memory:, para auditoria independente.')
        return str(Path(path).expanduser().resolve())
    raise TypeError('Database deve ser str, pathlib.Path ou sqlite3.Connection')
```

</details>

---

<a id="funcao-3"></a>

## _conexao

Estabelece uma conexão com um banco de dados SQLite.

A função `_conexao` é responsável por estabelecer e gerenciar a conexão com um banco de dados SQLite. Ela aceita tanto uma instância de `sqlite3.Connection` quanto uma string que representa o caminho para o arquivo do banco de dados. Se a conexão for bem-sucedida, ela retorna um iterador que pode ser usado para realizar operações no banco de dados.

### Assinatura

```python
def _conexao(database: Database) -> Iterator[sqlite3.Connection]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `database` | `Database` | Instância de `sqlite3.Connection` ou string com o caminho do arquivo do banco de dados. |

### Retorno

**Tipo:** `Iterator[sqlite3.Connection]`

Iterador que pode ser usado para realizar operações no banco de dados.

### Exceções

- **`TypeError`**: Quando o tipo do parâmetro `database` não é válido (neither `sqlite3.Connection` nor string).
- **`ValueError`**: Quando a string fornecida para o banco de dados está vazia.

### Dependências

- `{'nome': 'sqlite3', 'categoria': 'importado'}`
- `{'nome': 'TypeError', 'categoria': 'chamada'}`
- `{'nome': 'ValueError', 'categoria': 'chamada'}`
- `{'nome': 'conn.close', 'categoria': 'chamada'}`
- `{'nome': 'conn.commit', 'categoria': 'chamada'}`
- `{'nome': 'conn.execute', 'categoria': 'chamada'}`
- `{'nome': 'conn.rollback', 'categoria': 'chamada'}`
- `{'nome': 'isinstance', 'categoria': 'chamada'}`
- `{'nome': 'sqlite3.connect', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _conexao(database: Database) -> Iterator[sqlite3.Connection]:
    if isinstance(database, sqlite3.Connection):
        yield database
    elif isinstance(database, str):
        if not database:
            raise ValueError('Database não pode ser vazio')
        conn = sqlite3.connect(database, timeout=30)
        try:
            conn.execute('PRAGMA foreign_keys = ON')
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        raise TypeError('Database deve ser str ou sqlite3.Connection')
```

</details>

---

<a id="funcao-4"></a>

## inicializa_detalhes

Inicializa detalhes no banco de dados.

Executa uma série de instruções SQL para inicializar detalhes no banco de dados fornecido. As instruções são obtidas do atributo `_SCHEMA` e executadas em uma conexão com o banco de dados.

### Assinatura

```python
def inicializa_detalhes(database: Database) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `database` | `Database` | Conexão ou objeto de banco de dados que será inicializado. |

### Retorno

**Tipo:** `None`

Nenhum valor é retornado.

### Dependências

- `_SCHEMA.split`
- `_conexao`
- `conn.execute`
- `statement.strip`

<details>
<summary>Visualizar código-fonte</summary>

```python
def inicializa_detalhes(database: Database) -> None:
    with _conexao(database) as conn:
        for statement in _SCHEMA.split(';'):
            if statement.strip():
                conn.execute(statement)
```

</details>

---

<a id="funcao-5"></a>

## serializar_json

Serializa um objeto em formato JSON.

Converte um objeto Python em uma representação JSON. Se o objeto for uma instância de `BaseException`, retorna um dicionário com o tipo de erro e a mensagem associada. Caso contrário, retorna uma string representando o objeto.

### Assinatura

```python
def serializar_json(obj):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `obj` | `Não especificado` | Objeto Python que será serializado. |

### Retorno

**Tipo:** `Não especificado`

Representação JSON do objeto ou dicionário com informações de erro.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def serializar_json(obj):
    if isinstance(obj, BaseException):
        return {
            "tipo_erro": type(obj).__name__,
            "mensagem": str(obj)
        }

    return str(obj)
```

</details>

---

<a id="funcao-6"></a>

## registrar_evento

Registra um evento no banco de dados.

Insere informações sobre um evento em uma tabela específica do banco de dados, incluindo detalhes adicionais se fornecidos.

### Assinatura

```python
# Consulte o código-fonte de registrar_evento
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `database` | `Database` | Conexão com o banco de dados onde o evento será registrado. |
| `execucao_id` | `str` | Identificador único da execução associada ao evento. |
| `nome_evento` | `str` | Nome do evento a ser registrado. |
| `mensagem` | `str \| None` | Mensagem associada ao evento (opcional). |
| `nivel` | `str` | Nível de severidade do evento, deve ser uma das opções: 'DEBUG', 'INFO', 'ALERTA', 'ERRO', 'CRITICO'. |
| `detalhes` | `dict \| None` | Detalhes adicionais sobre o evento em formato de dicionário (opcional). |

### Retorno

**Tipo:** `int`

ID do registro do evento inserido no banco de dados.

### Exceções

- **`ValueError`**: Quando o nível fornecido não é uma das opções válidas.

### Dependências

- `json`

<details>
<summary>Visualizar código-fonte</summary>

```python
def registrar_evento(database: Database, execucao_id: str, nome_evento: str,
                     mensagem: str | None = None, nivel: str = 'INFO',
                     detalhes: dict | None = None) -> int:
    nivel = nivel.upper()
    if nivel not in {'DEBUG','INFO','ALERTA','ERRO','CRITICO'}:
        raise ValueError('Nível inválido')
    payload = json.dumps(detalhes, ensure_ascii=False, allow_nan=False, default=serializar_json) if detalhes is not None else None
    with _conexao(database) as conn:
        cursor = conn.execute('''INSERT INTO tbl_execucao_eventos
            (execucao_id, criado_em, nivel, nome_evento, mensagem, detalhes)
            VALUES (?,?,?,?,?,?)''', (execucao_id, _agora(), nivel, nome_evento, mensagem, payload))
        return cursor.lastrowid
```

</details>

---

<a id="funcao-7"></a>

## registrar_metrica

Registra uma métrica no banco de dados.

Insere uma nova métrica na tabela 'tbl_execucao_metricas' do banco de dados, associada a uma execução específica. Valida se o valor é finito e lança um erro caso contrário.

### Assinatura

```python
# Consulte o código-fonte de registrar_metrica
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `database` | `Database` | Conexão com o banco de dados onde a métrica será registrada. |
| `execucao_id` | `str` | Identificador único da execução à qual a métrica pertence. |
| `nome` | `str` | Nome da métrica sendo registrada. |
| `valor` | `float` | Valor numérico da métrica a ser registrado. |
| `unidade` | `str \| None` | Unidade de medida da métrica (opcional). |

### Retorno

**Tipo:** `int`

ID do registro da métrica inserido no banco de dados.

### Exceções

- **`ValueError`**: Quando o valor não é finito.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def registrar_metrica(database: Database, execucao_id: str, nome: str,
                      valor: float, unidade: str | None = None) -> int:
    numero = float(valor)
    if not math.isfinite(numero):
        raise ValueError('Valor deve ser finito')
    with _conexao(database) as conn:
        cursor = conn.execute('''INSERT INTO tbl_execucao_metricas
            (execucao_id, criado_em, nome, valor, unidade) VALUES (?,?,?,?,?)''',
            (execucao_id, _agora(), nome, numero, unidade))
        return cursor.lastrowid
```

</details>

---

<a id="funcao-8"></a>

## registrar_artefato

Registra um artefato em uma base de dados.

Insere informações sobre um artefato (arquivo) em uma tabela específica da base de dados, incluindo o tipo do artefato e opcionalmente seu hash SHA-256. Verifica a existência do arquivo e valida o tipo do artefato.

### Assinatura

```python
# Consulte o código-fonte de registrar_artefato
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `database` | `Database` | Conexão com a base de dados onde os dados serão registrados. |
| `execucao_id` | `str` | Identificador da execução associada ao artefato. |
| `file_path` | `str` | Caminho do arquivo a ser registrado. |
| `tipo_artefato` | `str` | Tipo do artefato, deve ser 'ENTRADA' ou 'SAIDA'. |
| `calcular_hash` | `bool` | Indica se o hash SHA-256 do arquivo deve ser calculado. |

### Retorno

**Tipo:** `int`

ID da linha inserida na tabela de artefatos.

### Exceções

- **`ValueError`**: Quando o tipo de artefato não é 'ENTRADA' ou 'SAIDA'.
- **`FileNotFoundError`**: Quando o arquivo especificado pelo caminho não existe.

### Dependências

- `{'nome': 'hashlib', 'categoria': 'import', 'descricao': 'Biblioteca utilizada para calcular o hash SHA-256 do arquivo.'}`
- `{'nome': 'pathlib.Path', 'categoria': 'import', 'descricao': 'Classe usada para manipulação de caminhos de arquivos.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def registrar_artefato(database: Database, execucao_id: str, file_path: str,
                       tipo_artefato: str, calcular_hash: bool = True) -> int:
    tipo_artefato = tipo_artefato.upper()
    if tipo_artefato not in {'ENTRADA','SAIDA'}:
        raise ValueError('Tipo de artefato deve ser ENTRADA ou SAIDA')
    
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Artefato não encontrado: {path}")

    if path.is_dir():
        return
    
    path = Path(file_path).expanduser().resolve()
    digest = None
    size = path.stat().st_size
    if calcular_hash:
        digest_obj = hashlib.sha256()
        with path.open('rb') as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b''):
                digest_obj.update(block)
        digest = digest_obj.hexdigest()

    with _conexao(database) as conn:
        cursor = conn.execute('''INSERT INTO tbl_execucao_artefatos
            (execucao_id, criado_em, tipo_artefato, file_path, sha256, size_bytes)
            VALUES (?,?,?,?,?,?)''',
            (execucao_id, _agora(), tipo_artefato, str(path), digest, size))
        return cursor.lastrowid
```

</details>

---

<a id="funcao-9"></a>

## listar_detalhes

Lista detalhes de execução a partir de uma base de dados.

Recupera informações sobre eventos, métricas e artefatos associados a uma execução específica, retornando-os em um dicionário estruturado.

### Assinatura

```python
def listar_detalhes(database: Database, execution_id: str) -> dict:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `database` | `Database` | Conexão à base de dados onde os detalhes estão armazenados. |
| `execution_id` | `str` | Identificador único da execução para a qual os detalhes são recuperados. |

### Retorno

**Tipo:** `dict`

Dicionário contendo listas de eventos, métricas e artefatos associados à execução especificada.

### Dependências

- `_conexao`
- `conn.execute`
- `cursor.fetchall`
- `dict`
- `zip`

<details>
<summary>Visualizar código-fonte</summary>

```python
def listar_detalhes(database: Database, execution_id: str) -> dict:
    with _conexao(database) as conn:
        result = {}
        for key, table in [('eventos','tbl_execucao_eventos'),('metricas','tbl_execucao_metricas'),('artefatos','tbl_execucao_artefatos')]:
            cursor = conn.execute(f'SELECT * FROM {table} WHERE execucao_id = ? ORDER BY id', (execution_id,))
            names = [col[0] for col in cursor.description]
            result[key] = [dict(zip(names, row)) for row in cursor.fetchall()]
        return result
```

</details>

---

<a id="funcao-10"></a>

## inicializar_rastreamento

Inicializa o rastreamento em uma base de dados SQLite.

Cria as tabelas necessárias para o rastreamento se elas ainda não existirem e verifica a existência da tabela 'tbl_manifesto_execucao'. Caso contrário, lança um erro indicando que a tabela deve ser criada antes de inicializar o rastreamento.

### Assinatura

```python
def inicializar_rastreamento(database: sqlite3.Connection | str | Path) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `database` | `sqlite3.Connection \| str \| Path` | Conexão existente com a base de dados ou caminho para o arquivo da base de dados. |

### Retorno

**Tipo:** `None`

Nenhum valor retornado.

### Exceções

- **`RuntimeError`**: Quando a tabela 'tbl_manifesto_execucao' não existe.

### Dependências

- `sqlite3.Connection`
- `str`
- `Path`
- `RuntimeError`
- `_conexao`
- `caminho_auditoria`

<details>
<summary>Visualizar código-fonte</summary>

```python
def inicializar_rastreamento(database: sqlite3.Connection | str | Path) -> None:
    path = caminho_auditoria(database)
    with _conexao(path) as conn:
        parent = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='tbl_manifesto_execucao'").fetchone()
        if not parent:
            raise RuntimeError('Crie a tabela de execução de manifesto antes de inicializar o rastreamento.')
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS tbl_execucao_chamadas (
                chamada_id TEXT PRIMARY KEY,
                execucao_id TEXT NOT NULL,
                chamada_parente_id TEXT,
                nome_funcao TEXT NOT NULL,
                nome_modulo TEXT NOT NULL,
                iniciado_em TEXT NOT NULL,
                finalizado_em TEXT,
                duracao_ms REAL,
                estado TEXT NOT NULL CHECK (estado IN ('RODANDO','SUCESSO','FALHA')),
                tipo_erro TEXT,
                mensagem_erro TEXT,
                trilha_erro TEXT,
                FOREIGN KEY(execucao_id) REFERENCES tbl_manifesto_execucao(execucao_id),
                FOREIGN KEY(chamada_parente_id) REFERENCES tbl_execucao_chamadas(chamada_id)
            );
            CREATE INDEX IF NOT EXISTS idx_execucao_chamadas_execucao
                ON tbl_execucao_chamadas(execucao_id, iniciado_em);
            CREATE INDEX IF NOT EXISTS idx_execucao_chamadas_parente
                ON tbl_execucao_chamadas(chamada_parente_id);
        ''')
```

</details>

---

<a id="funcao-11"></a>

## contexto_rastreamento

Cria um contexto de rastreamento para uma execução específica.

Este gerador configura o ambiente de rastreamento, inicializa os logs e prepara o contexto para a execução identificada por `execucao_id`. Após a execução, ele limpa o contexto e os logs.

### Assinatura

```python
def contexto_rastreamento(database: sqlite3.Connection | str | Path, execucao_id: str) -> Iterator[None]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `database` | `sqlite3.Connection \| str \| Path` | Conexão com o banco de dados ou caminho para o arquivo do banco de dados. |
| `execucao_id` | `str` | Identificador único da execução que está sendo rastreada. |

### Retorno

**Tipo:** `Iterator[None]`

Um iterador vazio, indicando que a função não retorna um valor explícito.

### Dependências

- `{'nome': '_chamada.reset', 'categoria': 'chamada'}`
- `{'nome': '_chamada.set', 'categoria': 'chamada'}`
- `{'nome': '_contexto.reset', 'categoria': 'chamada'}`
- `{'nome': '_contexto.set', 'categoria': 'chamada'}`
- `{'nome': 'caminho_auditoria', 'categoria': 'chamada'}`
- `{'nome': 'inicializar_rastreamento', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def contexto_rastreamento(database: sqlite3.Connection | str | Path, execucao_id: str) -> Iterator[None]:
    path = caminho_auditoria(database)
    inicializar_rastreamento(path)
    token_exec = _contexto.set((path, execucao_id))
    token_call = _chamada.set(None)
    try:
        yield
    finally:
        _chamada.reset(token_call)
        _contexto.reset(token_exec)
```

</details>

---

<a id="funcao-12"></a>

## rastrear_funcao

Rastreia a execução de uma função, registrando informações sobre chamadas e erros em um banco de dados.

A função `rastrear_funcao` envolve outra função (`func`) em um decorador que registra detalhes da execução, incluindo tempo de início, duração e estado (sucesso ou falha). Se ocorrer uma exceção, ela é registrada no banco de dados. A função suporta apenas funções síncronas.

### Assinatura

```python
def rastrear_funcao(func: F) -> F:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `func` | `F` | Função a ser rastreada. |

### Retorno

**Tipo:** `F`

A função decorada, que mantém o mesmo tipo e comportamento da função original.

### Exceções

- **`TypeError`**: Lancado se a função passada for assíncrona.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def rastrear_funcao(func: F) -> F:
    if __import__('inspect').iscoroutinefunction(func):
        raise TypeError('Rastrear funcao suporta apenas funções síncronas.')

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        ctx = _contexto.get()
        if ctx is None:
            return func(*args, **kwargs)
        path, execucao_id = ctx
        parent_id = _chamada.get()
        call_id = str(uuid4())
        with _conexao(path) as conn:
            conn.execute('''INSERT INTO tbl_execucao_chamadas
                (chamada_id, execucao_id, chamada_parente_id, nome_funcao,
                 nome_modulo, iniciado_em, estado)
                VALUES (?, ?, ?, ?, ?, ?, 'RODANDO')''',
                (call_id, execucao_id, parent_id, func.__qualname__, func.__module__, _agora()))
        token = _chamada.set(call_id)
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except BaseException as exc:
            with _conexao(path) as conn:
                conn.execute('''UPDATE tbl_execucao_chamadas SET finalizado_em=?, duracao_ms=?,
                    estado='FALHA', tipo_erro=?, mensagem_erro=?,trilha_erro=?
                    WHERE chamada_id=?''', (_agora(), (time.perf_counter()-start)*1000,
                    type(exc).__name__, str(exc), traceback.format_exc(), call_id))
            raise
        else:
            with _conexao(path) as conn:
                conn.execute('''UPDATE tbl_execucao_chamadas SET finalizado_em=?, duracao_ms=?,
                    estado='SUCESSO' WHERE chamada_id=?''',
                    (_agora(), (time.perf_counter()-start)*1000, call_id))
            return result
        finally:
            _chamada.reset(token)

    return wrapper
```

</details>

---

<a id="funcao-13"></a>

## listar_chamadas

Lista chamadas associadas a uma execução específica no banco de dados.

Recupera todas as chamadas de uma execução identificada por `execucao_id` do banco de dados, ordenando-as pelo tempo de início e ID da linha.

### Assinatura

```python
def listar_chamadas(database: sqlite3.Connection | str | Path, execucao_id: str) -> list[dict[str, Any]]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `database` | `sqlite3.Connection \| str \| Path` | Conexão existente com o banco de dados ou caminho para o arquivo do banco de dados. |
| `execucao_id` | `str` | Identificador único da execução cujas chamadas serão listadas. |

### Retorno

**Tipo:** `list[dict[str, Any]]`

Lista de dicionários contendo informações sobre cada chamada associada à execução especificada.

### Dependências

- `_conexao`
- `caminho_auditoria`
- `conn.execute`
- `dict`

<details>
<summary>Visualizar código-fonte</summary>

```python
def listar_chamadas(database: sqlite3.Connection | str | Path, execucao_id: str) -> list[dict[str, Any]]:
    path = caminho_auditoria(database)
    with _conexao(path) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute('''SELECT * FROM tbl_execucao_chamadas
            WHERE execucao_id=? ORDER BY iniciado_em, rowid''', (execucao_id,))]
```

</details>

---

<a id="funcao-14"></a>

## wrapper

Wrapper para monitorar e registrar chamadas de funções.

Este wrapper é responsável por monitorar e registrar todas as chamadas de funções, incluindo informações sobre o contexto da execução, tempo de execução, estado (sucesso ou falha), e qualquer exceção lançada. Ele utiliza uma conexão com um banco de dados para armazenar essas informações.

### Assinatura

```python
def wrapper(*args: Any, **kwargs: Any) -> Any:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `args` | `Any` | Argumentos posicionais passados para a função. |
| `kwargs` | `Any` | Argumentos de palavra-chave passados para a função. |

### Retorno

**Tipo:** `Any`

O resultado da chamada à função original.

### Exceções

- **`BaseException`**: Qualquer exceção lançada pela função original é reexcluída após ser registrada no banco de dados.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def wrapper(*args: Any, **kwargs: Any) -> Any:
        ctx = _contexto.get()
        if ctx is None:
            return func(*args, **kwargs)
        path, execucao_id = ctx
        parent_id = _chamada.get()
        call_id = str(uuid4())
        with _conexao(path) as conn:
            conn.execute('''INSERT INTO tbl_execucao_chamadas
                (chamada_id, execucao_id, chamada_parente_id, nome_funcao,
                 nome_modulo, iniciado_em, estado)
                VALUES (?, ?, ?, ?, ?, ?, 'RODANDO')''',
                (call_id, execucao_id, parent_id, func.__qualname__, func.__module__, _agora()))
        token = _chamada.set(call_id)
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except BaseException as exc:
            with _conexao(path) as conn:
                conn.execute('''UPDATE tbl_execucao_chamadas SET finalizado_em=?, duracao_ms=?,
                    estado='FALHA', tipo_erro=?, mensagem_erro=?,trilha_erro=?
                    WHERE chamada_id=?''', (_agora(), (time.perf_counter()-start)*1000,
                    type(exc).__name__, str(exc), traceback.format_exc(), call_id))
            raise
        else:
            with _conexao(path) as conn:
                conn.execute('''UPDATE tbl_execucao_chamadas SET finalizado_em=?, duracao_ms=?,
                    estado='SUCESSO' WHERE chamada_id=?''',
                    (_agora(), (time.perf_counter()-start)*1000, call_id))
            return result
        finally:
            _chamada.reset(token)
```

</details>

---
