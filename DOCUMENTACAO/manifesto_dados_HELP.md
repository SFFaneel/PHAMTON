# Referência de Funções

## Índice

- [sha256](#funcao-1)
- [atomic_json](#funcao-2)
- [carregar_csv](#funcao-3)
- [comparar](#funcao-4)
- [dados_equivalentes](#funcao-5)
- [criar_manifesto_multi](#funcao-6)

---

<a id="funcao-1"></a>

## sha256

Calcula o hash SHA-256 de um arquivo.

Gera um hash SHA-256 para o conteúdo de um arquivo especificado, lendo-o em blocos de 1MB por vez para evitar uso excessivo de memória com arquivos grandes.

### Assinatura

```python
def sha256(path: Path) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `path` | `Path` | Caminho do arquivo cujo hash SHA-256 será calculado. |

### Retorno

**Tipo:** `str`

Hash SHA-256 gerado para o conteúdo do arquivo, representado como uma string hexadecimal de 64 caracteres.

### Dependências

- `hashlib`

<details>
<summary>Visualizar código-fonte</summary>

```python
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()
```

</details>

---

<a id="funcao-2"></a>

## atomic_json

Salva um objeto Python como um arquivo JSON de forma atômica.

Cria um arquivo temporário, escreve o objeto em formato JSON nele e então renomeia para o caminho final. Isso garante que a operação seja atômica, evitando problemas com leituras parciais ou corrompimentos de arquivos.

### Assinatura

```python
def atomic_json(path: Path, obj: dict) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `path` | `Path` | Caminho completo onde o arquivo JSON será salvo. |
| `obj` | `dict` | Objeto Python que será convertido em formato JSON e salvo no arquivo. |

### Retorno

**Tipo:** `None`

Nenhum valor é retornado.

### Dependências

- `{'nome': 'json', 'categoria': 'import'}`
- `{'nome': 'os', 'categoria': 'import'}`
- `{'nome': 'tempfile', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def atomic_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.tmp-', suffix='.json')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
```

</details>

---

<a id="funcao-3"></a>

## carregar_csv

Carrega um arquivo CSV e retorna um DataFrame com o índice definido pela coluna-chave.

A função carrega um arquivo CSV utilizando as opções de separador, codificação e tipo de dado. Verifica a integridade dos dados, incluindo cabeçalhos duplicados, ausência de colunas-chave, IDs vazios e IDs duplicados. Se a coluna-chave for 'ID', ela tenta encontrar uma alternativa no formato 'ID' (case-insensitive).

### Assinatura

```python
def carregar_csv(path: Path, chave: str, sep: str, encoding: str) -> pd.DataFrame:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `path` | `Path` | Caminho para o arquivo CSV a ser carregado. |
| `chave` | `str` | Nome da coluna que será usada como índice do DataFrame. |
| `sep` | `str` | Separador utilizado no arquivo CSV (por exemplo, ',' ou '	'). |
| `encoding` | `str` | Codificação do arquivo CSV. |

### Retorno

**Tipo:** `pd.DataFrame`

DataFrame carregado a partir do arquivo CSV, com o índice definido pela coluna-chave.

### Exceções

- **`ValueError`**: Quando há cabeçalhos duplicados no arquivo CSV.
- **`ValueError`**: Quando o arquivo CSV está vazio e não possui colunas.
- **`ValueError`**: Quando a coluna-chave 'ID' não é encontrada no DataFrame.
- **`ValueError`**: Quando há IDs vazios no arquivo CSV.
- **`ValueError`**: Quando há IDs duplicados no arquivo CSV.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def carregar_csv(path: Path, chave: str, sep: str, encoding: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=sep, encoding=encoding, dtype=str, keep_default_na=False)
    if df.columns.duplicated().any():
        raise ValueError('Cabeçalhos duplicados')
    if df.empty and len(df.columns) == 0:
        raise ValueError('CSV sem colunas')
    if chave == 'ID' and chave not in df.columns:
        chave = next((nome for nome in df.columns if nome.upper().startswith('ID')), df.columns[0])
    if chave not in df.columns:
        raise ValueError(f'Coluna-chave ausente: {chave}')
    if df[chave].eq('').any() or df[chave].isna().any():
        raise ValueError('IDs vazios')
    if df[chave].duplicated().any():
        raise ValueError('IDs duplicados')
    return df.set_index(chave), chave
```

</details>

---

<a id="funcao-4"></a>

## comparar

Compara dois DataFrames e retorna informações sobre as linhas adicionadas, removidas e alteradas.

A função compara dois DataFrames (`antigo` e `novo`) baseados em uma chave comum. Retorna três DataFrames: um com as linhas adicionadas no novo DataFrame, outro com as linhas removidas do antigo DataFrame e um terceiro com as alterações nas colunas.

### Assinatura

```python
def comparar(antigo: pd.DataFrame | None, novo: pd.DataFrame, chave: str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `antigo` | `pd.DataFrame \| None` | DataFrame anterior para comparação. Se `None`, considera-se que não há dados anteriores. |
| `novo` | `pd.DataFrame` | DataFrame atual para comparação. |
| `chave` | `str` | Nome da coluna usada como chave para a comparação. |

### Exceções

- **`ValueError`**: Quando o nome da chave do DataFrame antigo não corresponde à chave fornecida.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def comparar(antigo: pd.DataFrame | None, novo: pd.DataFrame, chave: str):
    if antigo is None:
        return (novo.reset_index(), pd.DataFrame(columns=[chave, *novo.columns]),
                pd.DataFrame(columns=[chave, 'coluna', 'valor_anterior', 'valor_novo']))
    if antigo.index.name != chave:
        raise ValueError(f'Chave histórica incompatível: {antigo.index.name} != {chave}')
    adicionados = novo.index.difference(antigo.index, sort=False)
    removidos = antigo.index.difference(novo.index, sort=False)
    comuns = novo.index.intersection(antigo.index, sort=False)
    linhas = []
    for coluna in sorted(set(antigo.columns) | set(novo.columns)):
        a = antigo[coluna].reindex(comuns) if coluna in antigo else pd.Series('', index=comuns)
        b = novo[coluna].reindex(comuns) if coluna in novo else pd.Series('', index=comuns)
        for identificador, anterior, atual in zip(comuns, a, b):
            if anterior != atual:
                linhas.append({chave: identificador, 'coluna': coluna,
                               'valor_anterior': anterior, 'valor_novo': atual})
    return (novo.loc[adicionados].reset_index(), antigo.loc[removidos].reset_index(),
            pd.DataFrame(linhas, columns=[chave, 'coluna', 'valor_anterior', 'valor_novo']))
```

</details>

---

<a id="funcao-5"></a>

## dados_equivalentes

Verifica se dois DataFrames são equivalentes em termos de estrutura e conteúdo.

Compara dois DataFrames para determinar se eles têm as mesmas colunas, o mesmo número de linhas e os mesmos índices. Além disso, verifica se os valores correspondentes nas duas estruturas são iguais.

### Assinatura

```python
def dados_equivalentes(antigo: pd.DataFrame, novo: pd.DataFrame) -> bool:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `antigo` | `pd.DataFrame` | O DataFrame original a ser comparado. |
| `novo` | `pd.DataFrame` | O DataFrame que será comparado com o original. |

### Retorno

**Tipo:** `bool`

True se os DataFrames são equivalentes, False caso contrário.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def dados_equivalentes(antigo: pd.DataFrame, novo: pd.DataFrame) -> bool:
    if set(antigo.columns) != set(novo.columns):
        return False
    if len(antigo) != len(novo) or set(antigo.index) != set(novo.index):
        return False
    colunas = sorted(novo.columns)
    return antigo.reindex(index=novo.index, columns=colunas).equals(novo[colunas])
```

</details>

---

<a id="funcao-6"></a>

## criar_manifesto_multi

Cria um manifesto para um arquivo de dados, realizando uma auditoria e comparando com versões anteriores.

A função cria um novo manifesto para um arquivo de dados, realizando uma auditoria e comparando com versões anteriores. Ela verifica a integridade do arquivo, gera relatórios de inclusões, exclusões e alterações, e atualiza o índice de versões.

### Assinatura

```python
# Consulte o código-fonte de criar_manifesto_multi
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `arquivo` | `str \| Path` | Caminho para o arquivo de dados a ser auditado. |
| `id_arquivo` | `str` | Identificador único do arquivo, usado para organizar os arquivos de auditoria. |
| `diretorio_auditoria` | `str \| Path` | Diretório onde os arquivos de auditoria serão armazenados. |
| `chave` | `str` | Chave primária usada para identificar registros no arquivo. |
| `sep` | `str` | Separador usado no arquivo de dados. |
| `encoding` | `str` | Codificação do arquivo de dados. |
| `st` | `Não especificado` | Parâmetro não utilizado no código fornecido. |
| `timeout_lock` | `float` | Tempo limite para bloqueio, não utilizado no código fornecido. |

### Retorno

**Tipo:** `dict`

Dicionário contendo informações sobre a ingestão e o resultado da auditoria.

### Exceções

- **`FileNotFoundError`**: Quando o arquivo de origem não é encontrado.
- **`ValueError`**: Quando o `id_arquivo` contém caracteres inválidos ou quando a chave primária muda entre versões.
- **`RuntimeError`**: Quando o arquivo de origem é alterado durante a leitura.
- **`FileExistsError`**: Quando os artefatos da próxima versão já existem, indicando uma publicação interrompida.

### Dependências

- `datetime.datetime`
- `json`
- `os`
- `pandas`
- `pathlib.Path`
- `re`
- `shutil`
- `tempfile`
- `uuid`

<details>
<summary>Visualizar código-fonte</summary>

```python
def criar_manifesto_multi(
                            arquivo: str | Path, id_arquivo: str,
                            diretorio_auditoria: str | Path = 'auditoria', chave: str = 'ID',
                            sep: str = '|', encoding: str = 'latin-1', st=None,
                            timeout_lock: float = 60.0,
                        ) -> dict:
    origem = Path(arquivo).resolve()
    raiz_geral = Path(diretorio_auditoria).resolve()
    if not origem.is_file():
        raise FileNotFoundError(origem)
    if raiz_geral == origem or raiz_geral in origem.parents:
        raise ValueError('Arquivo operacional dentro da pasta de auditoria')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', id_arquivo):
        raise ValueError('id_arquivo deve conter apenas letras, números, _ ou -')
    raiz = raiz_geral / id_arquivo
    raiz.mkdir(parents=True, exist_ok=True)

    manifestos, versoes, comparacoes = (raiz / nome for nome in ('MANIFESTOS', 'VERSOES', 'COMPARACOES'))
    indice_path = manifestos / 'indice.json'
    indice = json.loads(indice_path.read_text(encoding='utf-8')) if indice_path.exists() else {'schema': 5, 'versoes': [], 'ingestoes': []}
    historico = indice['versoes']
    ingestoes = indice.get('ingestoes', [])
    anterior = historico[-1] if historico else None

    stage = Path(tempfile.mkdtemp(prefix='.stage-', dir=raiz))
    publicados = []
    try:
        copia_csv = stage / 'entrada.csv'
        hash_antes = sha256(origem)
        shutil.copyfile(origem, copia_csv)
        hash_entrada = sha256(copia_csv)
        if hash_entrada != hash_antes or sha256(origem) != hash_antes:
            raise RuntimeError('Arquivo de origem alterado durante a leitura')
        novo, chave_resolvida = carregar_csv(copia_csv, chave, sep, encoding)
        registro_ingestao = {
            'id': f'ing-{uuid.uuid4().hex}',
            'recebido_em_utc': datetime.now(timezone.utc).isoformat(),
            'arquivo_origem': origem.name,
            'sha256_origem': hash_entrada,
            'tamanho_origem_bytes': copia_csv.stat().st_size,
        }
        if anterior and anterior['sha256_origem'] == hash_entrada:
            registro_ingestao.update(versao=anterior['versao'], status='sem_alteracao')
            atomic_json(indice_path, {**indice, 'schema': 5, 'ingestoes': [*ingestoes, registro_ingestao]})
            return {
                'status': 'sem_alteracao', 'versao': anterior['versao'],
                'sha256_origem': hash_entrada, 'motivo': 'hash_identico',
                'id_ingestao': registro_ingestao['id'],
            }
        antigo = None
        if anterior:
            if anterior['chave'] != chave_resolvida:
                raise ValueError('A chave primária mudou entre versões')
            snapshot = raiz / anterior['snapshot']
            if sha256(snapshot) != anterior['sha256_snapshot']:
                raise ValueError('Integridade do snapshot anterior comprometida')
            antigo = pd.read_parquet(snapshot, engine='pyarrow')
            antigo.index.name = chave_resolvida

        incluidos, excluidos, alterados = comparar(antigo, novo, chave_resolvida)
        numero = int(anterior['versao'][1:]) + 1 if anterior else 1
        versao = f'v{numero:04d}'
        destino = versoes / f'{versao}.parquet'
        rel_dir = comparacoes / (f"{anterior['versao']}_{versao}" if anterior else f'inicial_{versao}')
        manifesto_path = manifestos / f'{versao}.json'
        if any(p.exists() for p in (destino, rel_dir, manifesto_path)):
            raise FileExistsError('Artefatos da próxima versão já existem; verificar publicação interrompida')

        snapshot_stage = stage / 'snapshot.parquet'
        novo.to_parquet(snapshot_stage, engine='pyarrow', compression='snappy', index=True)
        rel_stage = stage / 'comparacao'
        rel_stage.mkdir()
        relatorios = {}
        for nome, df in (('incluidos', incluidos), ('excluidos', excluidos), ('alterados', alterados)):
            p = rel_stage / f'{nome}.parquet'
            df.to_parquet(p, engine='pyarrow', compression='snappy', index=False)
            relatorios[nome] = {'caminho': str((rel_dir / p.name).relative_to(raiz)), 'sha256': sha256(p)}

        match = re.search(r'_(\d{8})\.csv$', origem.name, flags=re.I)
        info = {
            'tipo': id_arquivo, 'versao': versao,
            'criado_em_utc': datetime.now(timezone.utc).isoformat(),
            'arquivo_origem': origem.name,
            'data_nome_yyyymmdd': match.group(1) if match else None,
            'sha256_origem': hash_entrada,
            'sha256_snapshot': sha256(snapshot_stage),
            'tamanho_origem_bytes': copia_csv.stat().st_size,
            'snapshot': str(destino.relative_to(raiz)),
            'versao_anterior': anterior['versao'] if anterior else None,
            'chave': chave_resolvida, 'separador': sep, 'encoding': encoding,
            'colunas': [chave_resolvida, *novo.columns.tolist()],
            'colunas_adicionadas': sorted(set(novo.columns) - set(antigo.columns)) if antigo is not None else list(novo.columns),
            'colunas_removidas': sorted(set(antigo.columns) - set(novo.columns)) if antigo is not None else [],
            'alteracao_dados': bool(antigo is None or not dados_equivalentes(antigo, novo)),
            'total_registros': len(novo), 'incluidos': len(incluidos),
            'excluidos': len(excluidos),
            'registros_alterados': int(alterados[chave_resolvida].nunique()) if not alterados.empty else 0,
            'campos_alterados': len(alterados), 'relatorios': relatorios,
        }
        atomic_json(stage / 'manifesto.json', info)
        for pasta in (versoes, manifestos, comparacoes):
            pasta.mkdir(parents=True, exist_ok=True)
        os.replace(snapshot_stage, destino)
        publicados.append(destino)
        os.replace(rel_stage, rel_dir)
        publicados.append(rel_dir)
        os.replace(stage / 'manifesto.json', manifesto_path)
        publicados.append(manifesto_path)

        registro_ingestao.update(versao=versao, status='nova_versao')
        atomic_json(indice_path, {
            **indice, 'schema': 5, 'versoes': [*historico, info],
            'ingestoes': [*ingestoes, registro_ingestao],
        })
        return {'status': 'nova_versao', 'id_ingestao': registro_ingestao['id'], **info}
    except Exception:
        for p in reversed(publicados):
            if p.is_dir():
                shutil.rmtree(p)
            elif p.exists():
                p.unlink()
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)
```

</details>

---
