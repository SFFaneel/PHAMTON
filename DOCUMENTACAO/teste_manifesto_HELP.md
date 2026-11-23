# Referência de Funções

## Índice

- [pasta_sessao](#funcao-1)
- [ambiente](#funcao-2)
- [indice](#funcao-3)
- [requer_parquet](#funcao-4)
- [teste_sha256_reflete_bytes](#funcao-5)
- [teste_carregar_csv_preserva_zeros_e_vazios](#funcao-6)
- [teste_carregar_csv_rejeita_ids_invalidos](#funcao-7)
- [teste_comparar_inclusoes_exclusoes_e_campos](#funcao-8)
- [teste_dados_equivalentes_ignora_ordem](#funcao-9)
- [teste_primeira_versao_snapshot_e_manifesto](#funcao-10)
- [teste_hash_igual_nao_cria_versao_mas_registra_ingestao](#funcao-11)
- [teste_hash_diferente_com_dados_iguais_cria_versao](#funcao-12)
- [teste_modificacoes_registradas_no_manifesto](#funcao-13)
- [teste_alteracao_de_esquema](#funcao-14)
- [teste_historicos_independentes_por_tipo](#funcao-15)
- [teste_snapshot_adulterado_e_detectado](#funcao-16)
- [teste_csv_invalido_nao_publica_versao](#funcao-17)
- [teste_arquivo_inexistente](#funcao-18)
- [teste_id_arquivo_invalido](#funcao-19)
- [teste_arquivo_origem_dentro_da_auditoria](#funcao-20)
- [teste_snapshot_completo_preserva_todos_os_valores](#funcao-21)
- [teste_manifesto_json_hashes_contagens_e_relatorios](#funcao-22)
- [teste_tipos_tem_indices_e_snapshots_independentes](#funcao-23)
- [teste_esquema_adicao_e_remocao_manifestos_e_snapshots](#funcao-24)
- [teste_falha_publicacao_preserva_indice](#funcao-25)
- [escrever](#funcao-26)
- [processar](#funcao-27)
- [falhar_snapshot](#funcao-28)
- [falhar_relatorio](#funcao-29)
- [falhar_indice](#funcao-30)

---

<a id="funcao-1"></a>

## pasta_sessao

Cria uma pasta temporária para sessões de teste.

A função cria duas pastas: DOWNLOADS e DIRETORIO_TESTES, garantindo que elas existam. Em seguida, cria uma pasta temporária única para a sessão de teste com um prefixo específico e retorna seu caminho.

### Assinatura

```python
def pasta_sessao():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Retorno

**Tipo:** `Path`

Caminho da pasta temporária criada para a sessão de teste.

### Dependências

- `pathlib.Path`
- `pytest`
- `tempfile`

<details>
<summary>Visualizar código-fonte</summary>

```python
def pasta_sessao():
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    DIRETORIO_TESTES.mkdir(parents=True, exist_ok=True)
    pasta = Path(tempfile.mkdtemp(prefix='sessao-', dir=DIRETORIO_TESTES))
    yield pasta
```

</details>

---

<a id="funcao-2"></a>

## ambiente

Cria um ambiente de trabalho para processamento de dados.

Esta função cria uma estrutura de diretórios e arquivos necessários para o processamento de dados, incluindo a criação de um arquivo CSV e uma pasta para auditoria. Também define funções auxiliares para escrever texto em um arquivo e processar os dados.

### Assinatura

```python
def ambiente(pasta_sessao, tmp_path):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `pasta_sessao` | `Não especificado` | Caminho da pasta onde será criada a estrutura de trabalho. |
| `tmp_path` | `Não especificado` | Objeto Path do módulo tempfile, contendo informações sobre o caminho temporário. |

### Retorno

**Tipo:** `Não especificado`

Não há retorno explícito. A função retorna funções auxiliares para escrever em arquivos e processar dados.

### Dependências

- `{'nome': 'MANIFESTO.criar_manifesto_multi', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def ambiente(pasta_sessao, tmp_path):
    pasta = pasta_sessao / tmp_path.name
    pasta.mkdir(parents=True, exist_ok=False)
    arquivo = pasta / 'clientes.csv'
    raiz = pasta / 'auditoria'

    def escrever(texto, *, encoding='utf-8'):
        arquivo.write_text(texto, encoding=encoding)
        return arquivo

    def processar(id_arquivo='CLIENTES', **kwargs):
        return criar_manifesto_multi(arquivo, id_arquivo, raiz, encoding='utf-8', **kwargs)

    return arquivo, raiz, escrever, processar
```

</details>

---

<a id="funcao-3"></a>

## indice

Carrega o índice de manifestos a partir de um arquivo JSON.

Lê e retorna o conteúdo do arquivo 'indice.json' localizado em uma estrutura de diretórios específica, dependendo dos parâmetros fornecidos.

### Assinatura

```python
def indice(raiz, tipo='CLIENTES'):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `raiz` | `Não especificado` | Caminho base para a estrutura de diretórios. |
| `tipo` | `Não especificado` | Tipo de dados, que determina o subdiretório dentro da raiz. |

### Retorno

**Tipo:** `Não especificado`

Conteúdo do arquivo 'indice.json' carregado como um objeto Python.

### Dependências

- `json`

<details>
<summary>Visualizar código-fonte</summary>

```python
def indice(raiz, tipo='CLIENTES'):
    return json.loads((raiz / tipo / 'MANIFESTOS' / 'indice.json').read_text(encoding='utf-8'))
```

</details>

---

<a id="funcao-4"></a>

## requer_parquet

Verifica se a biblioteca 'pyarrow' está instalada para executar testes de snapshots.

A função verifica a disponibilidade da biblioteca 'pyarrow'. Se não estiver instalada, um aviso é exibido e os testes de snapshots são ignorados.

### Assinatura

```python
def requer_parquet():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Dependências

- `pytest`

<details>
<summary>Visualizar código-fonte</summary>

```python
def requer_parquet():
    pytest.importorskip('pyarrow', reason='Testes de snapshots exigem pyarrow')
```

</details>

---

<a id="funcao-5"></a>

## teste_sha256_reflete_bytes

Testa a função sha256 para verificar se o hash de um arquivo permanece inalterado após uma modificação.

A função escreve dois conteúdos diferentes em um arquivo temporário e verifica se o hash SHA-256 do arquivo é alterado conforme esperado. O primeiro conteúdo contém quebras de linha simples, enquanto o segundo contém quebras de linha Windows (CRLF).

### Assinatura

```python
def teste_sha256_reflete_bytes(tmp_path):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `tmp_path` | `Não especificado` | Diretório temporário fornecido pelo pytest para criar arquivos. |

### Dependências

- `{'nome': 'MANIFESTO.sha256', 'tipo': None, 'categoria': 'import'}`
- `{'nome': 'hashlib', 'tipo': None, 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_sha256_reflete_bytes(tmp_path):
    arquivo = tmp_path / 'entrada.csv'
    arquivo.write_bytes(b'ID|NOME\n1|ANA\n')
    assert sha256(arquivo) == hashlib.sha256(arquivo.read_bytes()).hexdigest()
    anterior = sha256(arquivo)
    arquivo.write_bytes(b'ID|NOME\r\n1|ANA\r\n')
    assert sha256(arquivo) != anterior
```

</details>

---

<a id="funcao-6"></a>

## teste_carregar_csv_preserva_zeros_e_vazios

Testa a função carregar_csv para garantir que zeros e valores vazios sejam preservados no DataFrame resultante.

A função testa o comportamento da função carregar_csv ao ler um arquivo CSV, verificando se os zeros e valores vazios são mantidos corretamente no DataFrame gerado. O teste cria um arquivo temporário com dados que incluem zeros e valores vazios, lê esses dados usando a função carregar_csv e verifica se o resultado é conforme esperado.

### Assinatura

```python
def teste_carregar_csv_preserva_zeros_e_vazios(tmp_path):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `tmp_path` | `Não especificado` | Caminho temporário fornecido pelo pytest para criar arquivos de teste. |

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_carregar_csv_preserva_zeros_e_vazios(tmp_path):
    arquivo = tmp_path / 'dados.csv'
    arquivo.write_text('ID|NOME|OBS\n001|ANA|\n002|JOAO|OK\n', encoding='utf-8')
    df, chave = carregar_csv(arquivo, 'ID', '|', 'utf-8')
    assert chave == 'ID'
    assert df.index.tolist() == ['001', '002']
    assert df.loc['001', 'OBS'] == ''
```

</details>

---

<a id="funcao-7"></a>

## teste_carregar_csv_rejeita_ids_invalidos

Testa a função carregar_csv para rejeitar IDs inválidos em um arquivo CSV.

A função verifica se o carregamento de um arquivo CSV rejeita linhas com IDs inválidos, conforme especificado pelo parâmetro 'erro'.

### Assinatura

```python
def teste_carregar_csv_rejeita_ids_invalidos(tmp_path, conteudo, erro):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `tmp_path` | `Não especificado` | Caminho temporário para criar o arquivo CSV. |
| `conteudo` | `Não especificado` | Conteúdo do arquivo CSV a ser carregado, como uma string. |
| `erro` | `Não especificado` | Mensagem de erro esperada ao rejeitar IDs inválidos. |

### Dependências

- `{'nome': 'MANIFESTO.carregar_csv', 'tipo': 'função', 'categoria': 'importação'}`
- `{'nome': 'pytest.raises', 'tipo': 'contexto', 'categoria': 'importação'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_carregar_csv_rejeita_ids_invalidos(tmp_path, conteudo, erro):
    arquivo = tmp_path / 'dados.csv'
    arquivo.write_text(conteudo, encoding='utf-8')
    with pytest.raises(ValueError, match=erro):
        carregar_csv(arquivo, 'ID', '|', 'utf-8')
```

</details>

---

<a id="funcao-8"></a>

## teste_comparar_inclusoes_exclusoes_e_campos

Testa a função comparar para identificar inclusões, exclusões e alterações entre dois DataFrames.

A função compara dois DataFrames (antigo e novo) baseados em uma chave especificada ('ID') e retorna três DataFrames: um com os registros incluídos no novo DataFrame, outro com os registros excluídos do antigo DataFrame e o terceiro com as alterações nos valores dos campos.

### Assinatura

```python
def teste_comparar_inclusoes_exclusoes_e_campos():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Dependências

- `MANIFESTO.comparar`
- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_comparar_inclusoes_exclusoes_e_campos():
    antigo = pd.DataFrame({'ID': ['1', '2'], 'NOME': ['ANA', 'JOAO']}).set_index('ID')
    novo = pd.DataFrame({'ID': ['2', '3'], 'NOME': ['JOSE', 'MARIA']}).set_index('ID')
    incluidos, excluidos, alterados = comparar(antigo, novo, 'ID')
    assert incluidos.to_dict('records') == [{'ID': '3', 'NOME': 'MARIA'}]
    assert excluidos.to_dict('records') == [{'ID': '1', 'NOME': 'ANA'}]
    assert alterados.to_dict('records') == [
                                                {'ID': '2', 'coluna': 'NOME', 'valor_anterior': 'JOAO', 'valor_novo': 'JOSE'}
                                            ]
```

</details>

---

<a id="funcao-9"></a>

## teste_dados_equivalentes_ignora_ordem

Testa a equivalência entre dois DataFrames, ignorando a ordem das linhas.

A função verifica se dois DataFrames são equivalentes, considerando apenas os valores e ignorando a ordem das linhas. A comparação é realizada usando uma função chamada `dados_equivalentes` que deve estar definida em um módulo chamado `MANIFESTO.dados_equivalentes`. O teste inclui duas verificações: uma onde os DataFrames são equivalentes e outra onde eles não são, devido a uma diferença no valor de uma coluna.

### Assinatura

```python
def teste_dados_equivalentes_ignora_ordem():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Dependências

- `MANIFESTO.dados_equivalentes`
- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_dados_equivalentes_ignora_ordem():
    antigo = pd.DataFrame({'ID': ['1', '2'], 'NOME': ['ANA', 'JOAO'], 'UF': ['SP', 'RJ']}).set_index('ID')
    novo = pd.DataFrame({'UF': ['RJ', 'SP'], 'ID': ['2', '1'], 'NOME': ['JOAO', 'ANA']}).set_index('ID')
    assert dados_equivalentes(antigo, novo)
    novo.loc['1', 'NOME'] = 'MARIA'
    assert not dados_equivalentes(antigo, novo)
```

</details>

---

<a id="funcao-10"></a>

## teste_primeira_versao_snapshot_e_manifesto

Testa a primeira versão do snapshot e manifesto.

Executa uma série de verificações para garantir que o processo de criação do snapshot e manifestos funcione corretamente. Valida os resultados, hashes SHA-256 e existência dos arquivos gerados.

### Assinatura

```python
def teste_primeira_versao_snapshot_e_manifesto(ambiente):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ambiente` | `Não especificado` | Ambiente de teste contendo funções necessárias para a execução do teste. |

### Dependências

- `{'nome': 'MANIFESTO.sha256', 'tipo': None, 'categoria': 'import'}`
- `{'nome': 'pandas', 'tipo': None, 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_primeira_versao_snapshot_e_manifesto(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n001|ANA\n002|JOAO\n')
    resultado = processar()
    assert resultado['status'] == 'nova_versao'
    assert resultado['versao'] == 'v0001'
    assert resultado['incluidos'] == 2
    assert resultado['excluidos'] == 0
    assert resultado['alteracao_dados'] is True
    pasta = raiz / 'CLIENTES'
    snapshot = pasta / resultado['snapshot']
    assert snapshot.suffix == '.parquet'
    assert sha256(snapshot) == resultado['sha256_snapshot']
    assert pd.read_parquet(snapshot).loc['001', 'NOME'] == 'ANA'
    assert (pasta / 'MANIFESTOS' / 'v0001.json').exists()
    for nome in ('incluidos', 'excluidos', 'alterados'):
        rel = resultado['relatorios'][nome]
        caminho = pasta / rel['caminho']
        assert caminho.exists()
        assert sha256(caminho) == rel['sha256']
    assert len(indice(raiz)['ingestoes']) == 1
```

</details>

---

<a id="funcao-11"></a>

## teste_hash_igual_nao_cria_versao_mas_registra_ingestao

Testa o comportamento da função quando um hash é igual, não criando uma nova versão mas registrando a ingestão.

A função verifica se, ao processar dados com o mesmo hash que já foi processado anteriormente, não é criada uma nova versão e se a ingestão é registrada corretamente. É verificado também se o histórico de ingestões contém as informações esperadas.

### Assinatura

```python
def teste_hash_igual_nao_cria_versao_mas_registra_ingestao(ambiente):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ambiente` | `Não especificado` | Ambiente de execução que inclui funções para escrever, processar e obter o índice. |

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_hash_igual_nao_cria_versao_mas_registra_ingestao(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    primeira = processar()
    segunda = processar()
    assert segunda['status'] == 'sem_alteracao'
    assert segunda['motivo'] == 'hash_identico'
    assert segunda['versao'] == primeira['versao']
    historico = indice(raiz)
    assert len(historico['versoes']) == 1
    assert len(historico['ingestoes']) == 2
    assert historico['ingestoes'][1]['sha256_origem'] == primeira['sha256_origem']
```

</details>

---

<a id="funcao-12"></a>

## teste_hash_diferente_com_dados_iguais_cria_versao

Testa a criação de uma nova versão ao processar dados iguais em um ambiente específico.

A função testa se, ao processar dados idênticos duas vezes em um ambiente configurado, é criada uma nova versão com SHA256 diferente e sem alterações nos dados. Verifica também a consistência do índice de versões e ingestões.

### Assinatura

```python
def teste_hash_diferente_com_dados_iguais_cria_versao(ambiente):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ambiente` | `Não especificado` | Ambiente configurado para o teste, contendo funções `escrever`, `indice`, `len`, `processar` e `requer_parquet`. |

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_hash_diferente_com_dados_iguais_cria_versao(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n2|JOAO\n')
    primeira = processar()
    escrever('ID|NOME\n2|JOAO\n1|ANA\n')
    segunda = processar()
    assert segunda['status'] == 'nova_versao'
    assert segunda['versao'] == 'v0002'
    assert segunda['sha256_origem'] != primeira['sha256_origem']
    assert segunda['alteracao_dados'] is False
    assert (segunda['incluidos'], segunda['excluidos'], segunda['campos_alterados']) == (0, 0, 0)
    assert len(indice(raiz)['versoes']) == 2
    assert len(indice(raiz)['ingestoes']) == 2
```

</details>

---

<a id="funcao-13"></a>

## teste_modificacoes_registradas_no_manifesto

Testa as modificações registradas no manifesto de clientes.

A função simula a leitura e processamento de um arquivo Parquet, escreve novos dados, verifica alterações e valida os resultados.

### Assinatura

```python
def teste_modificacoes_registradas_no_manifesto(ambiente):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ambiente` | `Não especificado` | Ambiente contendo funções para escrita, processamento e requisição de Parquet. |

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_modificacoes_registradas_no_manifesto(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n2|JOAO\n')
    processar()
    escrever('ID|NOME\n2|JOSE\n3|MARIA\n')
    segunda = processar()
    assert segunda['versao_anterior'] == 'v0001'
    assert segunda['alteracao_dados'] is True
    assert segunda['incluidos'] == 1
    assert segunda['excluidos'] == 1
    assert segunda['registros_alterados'] == 1
    assert segunda['campos_alterados'] == 1
    alterados = pd.read_parquet(raiz / 'CLIENTES' / segunda['relatorios']['alterados']['caminho'])
    assert alterados.iloc[0].to_dict() == {
                                                'ID': '2', 'coluna': 'NOME', 'valor_anterior': 'JOAO', 'valor_novo': 'JOSE'
                                            }
```

</details>

---

<a id="funcao-14"></a>

## teste_alteracao_de_esquema

Testa a alteração de esquema em um ambiente específico.

A função realiza uma série de operações no ambiente fornecido, escrevendo dados e processando-os para verificar as alterações no esquema dos dados. Verifica a adição de novas colunas, remoção de colunas e alteração de dados.

### Assinatura

```python
def teste_alteracao_de_esquema(ambiente):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ambiente` | `Não especificado` | Ambiente onde as operações serão realizadas. |

### Dependências

- `escrever`
- `processar`
- `requer_parquet`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_alteracao_de_esquema(ambiente):
    requer_parquet()
    _, _, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    processar()
    escrever('ID|NOME|UF\n1|ANA|SP\n')
    segunda = processar()
    assert segunda['colunas_adicionadas'] == ['UF']
    assert segunda['colunas_removidas'] == []
    assert segunda['alteracao_dados'] is True
    escrever('ID|UF\n1|SP\n')
    terceira = processar()
    assert terceira['colunas_removidas'] == ['NOME']
    assert terceira['alteracao_dados'] is True
```

</details>

---

<a id="funcao-15"></a>

## teste_historicos_independentes_por_tipo

Testa a independência dos históricos por tipo em um ambiente específico.

A função testa se os históricos de diferentes tipos (CLIENTES e PRODUTOS) são independentes, verificando que possuem a mesma versão e que cada um tem apenas uma versão registrada no índice.

### Assinatura

```python
def teste_historicos_independentes_por_tipo(ambiente):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ambiente` | `Não especificado` | Ambiente de teste contendo funções para escrever, processar e verificar índices. |

### Dependências

- `{'nome': 'requer_parquet', 'tipo': None, 'categoria': 'chamada'}`
- `{'nome': 'escrever', 'tipo': None, 'categoria': 'chamada'}`
- `{'nome': 'indice', 'tipo': None, 'categoria': 'chamada'}`
- `{'nome': 'len', 'tipo': None, 'categoria': 'chamada'}`
- `{'nome': 'processar', 'tipo': None, 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_historicos_independentes_por_tipo(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    a = processar('CLIENTES')
    b = processar('PRODUTOS')
    assert a['versao'] == b['versao'] == 'v0001'
    assert len(indice(raiz, 'CLIENTES')['versoes']) == 1
    assert len(indice(raiz, 'PRODUTOS')['versoes']) == 1
```

</details>

---

<a id="funcao-16"></a>

## teste_snapshot_adulterado_e_detectado

Testa a detecção de adulteração em um snapshot.

A função simula uma situação onde um arquivo parquet é alterado e verifica se o processo detecta essa modificação, lançando uma exceção `ValueError` com a mensagem 'Integridade do snapshot'.

### Assinatura

```python
def teste_snapshot_adulterado_e_detectado(ambiente):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ambiente` | `Não especificado` | Ambiente de teste contendo funções e objetos necessários para o processo. |

### Exceções

- **`ValueError`**: Quando a integridade do snapshot é violada.

### Dependências

- `pytest`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_snapshot_adulterado_e_detectado(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    primeira = processar()
    snapshot = raiz / 'CLIENTES' / primeira['snapshot']
    snapshot.write_bytes(snapshot.read_bytes() + b'alteracao')
    escrever('ID|NOME\n1|JOSE\n')
    with pytest.raises(ValueError, match='Integridade do snapshot'):
        processar()
    assert len(indice(raiz)['versoes']) == 1
```

</details>

---

<a id="funcao-17"></a>

## teste_csv_invalido_nao_publica_versao

Testa a não publicação de uma versão CSV inválida.

A função testa o comportamento do sistema ao processar um arquivo CSV com duplicados. Ela verifica se a versão é corretamente rejeitada e se as estruturas de dados internas permanecem consistentes.

### Assinatura

```python
def teste_csv_invalido_nao_publica_versao(ambiente):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ambiente` | `Não especificado` | Ambiente de teste contendo funções para escrever, verificar existência, obter índice e processar dados. |

### Exceções

- **`ValueError`**: Quando o arquivo CSV contém duplicados.

### Dependências

- `pytest`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_csv_invalido_nao_publica_versao(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    processar()
    escrever('ID|NOME\n1|ANA\n1|JOAO\n')
    with pytest.raises(ValueError, match='duplicados'):
        processar()
    assert len(indice(raiz)['versoes']) == 1
    assert len(indice(raiz)['ingestoes']) == 1
    assert not (raiz / 'CLIENTES' / 'VERSOES' / 'v0002.parquet').exists()
```

</details>

---

<a id="funcao-18"></a>

## teste_arquivo_inexistente

Testa a função `criar_manifesto_multi` ao tentar criar um arquivo que não existe.

A função verifica se a exceção `FileNotFoundError` é lançada quando o arquivo especificado para criação não existe.

### Assinatura

```python
def teste_arquivo_inexistente(tmp_path):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `tmp_path` | `Não especificado` | Caminho temporário fornecido pelo pytest. |

### Dependências

- `MANIFESTO.criar_manifesto_multi`
- `pytest`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_arquivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        criar_manifesto_multi(tmp_path / 'ausente.csv', 'CLIENTES', tmp_path / 'auditoria')
```

</details>

---

<a id="funcao-19"></a>

## teste_id_arquivo_invalido

Testa a função `criar_manifesto_multi` com um arquivo de ID inválido.

Cria um arquivo CSV temporário com dados inválidos e verifica se a função lança uma exceção `ValueError` quando o ID do arquivo é inválido.

### Assinatura

```python
def teste_id_arquivo_invalido(tmp_path):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `tmp_path` | `Não especificado` | Caminho temporário fornecido pelo pytest para criar arquivos. |

### Exceções

- **`ValueError`**: Quando o ID do arquivo é inválido.

### Dependências

- `{'nome': 'MANIFESTO.criar_manifesto_multi', 'categoria': 'importado', 'descricao': 'Função que será chamada para criar o manifesto.'}`
- `{'nome': 'pytest.raises', 'categoria': 'importado', 'descricao': 'Método pytest usado para verificar a exceção lançada.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_id_arquivo_invalido(tmp_path):
    arquivo = tmp_path / 'dados.csv'
    arquivo.write_text('ID|NOME\n1|ANA\n', encoding='utf-8')
    with pytest.raises(ValueError, match='id_arquivo'):
        criar_manifesto_multi(arquivo, '../CLIENTES', tmp_path / 'auditoria', encoding='utf-8')
```

</details>

---

<a id="funcao-20"></a>

## teste_arquivo_origem_dentro_da_auditoria

Testa a função `criar_manifesto_multi` para verificar se ela lança uma exceção quando o arquivo de origem está dentro da pasta de auditoria.

A função cria um diretório 'auditoria' e um arquivo 'dados.csv' dentro dele. Em seguida, tenta criar um manifesto multi usando a função `criar_manifesto_multi` e espera que uma exceção `ValueError` seja lançada com a mensagem 'dentro da pasta'.

### Assinatura

```python
def teste_arquivo_origem_dentro_da_auditoria(tmp_path):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `tmp_path` | `Não especificado` | Caminho temporário fornecido pelo pytest para criar arquivos e diretórios. |

### Exceções

- **`ValueError`**: Quando o arquivo de origem está dentro da pasta de auditoria.

### Dependências

- `MANIFESTO.criar_manifesto_multi`
- `pytest`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_arquivo_origem_dentro_da_auditoria(tmp_path):
    raiz = tmp_path / 'auditoria'
    raiz.mkdir()
    arquivo = raiz / 'dados.csv'
    arquivo.write_text('ID|NOME\n1|ANA\n', encoding='utf-8')
    with pytest.raises(ValueError, match='dentro da pasta'):
        criar_manifesto_multi(arquivo, 'CLIENTES', raiz, encoding='utf-8')
```

</details>

---

<a id="funcao-21"></a>

## teste_snapshot_completo_preserva_todos_os_valores

Testa a função de processamento de snapshot que preserva todos os valores.

A função realiza um teste para garantir que o processo de snapshot preserva corretamente todos os valores dos dados, incluindo IDs, nomes, CEPs e observações. Verifica se os índices, colunas e valores individuais estão conforme esperado.

### Assinatura

```python
def teste_snapshot_completo_preserva_todos_os_valores(ambiente):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ambiente` | `Não especificado` | Ambiente de teste contendo funções e objetos necessários para a execução do teste. |

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_snapshot_completo_preserva_todos_os_valores(ambiente):
    requer_parquet()
    arquivo, raiz, escrever, processar = ambiente
    escrever('ID|NOME|CEP|OBS\n001|ANA|01001000|\n002|JOAO|00000001|OK\n')
    resultado = processar()
    snapshot = raiz / 'CLIENTES' / resultado['snapshot']
    dados = pd.read_parquet(snapshot, engine='pyarrow')
    assert dados.index.name == 'ID'
    assert dados.index.tolist() == ['001', '002']
    assert dados.columns.tolist() == ['NOME', 'CEP', 'OBS']
    assert dados.loc['001'].to_dict() == {'NOME': 'ANA', 'CEP': '01001000', 'OBS': ''}
    assert dados.loc['002'].to_dict() == {'NOME': 'JOAO', 'CEP': '00000001', 'OBS': 'OK'}
    assert len(dados) == resultado['total_registros'] == 2
```

</details>

---

<a id="funcao-22"></a>

## teste_manifesto_json_hashes_contagens_e_relatorios

Testa a geração de manifestos JSON com hashes, contagens e relatórios.

A função realiza uma série de verificações para garantir que o processo de geração de manifestos JSON funcione corretamente. Ela lê arquivos parquet, escreve dados temporários, processa informações e valida os resultados contra expectativas.

### Assinatura

```python
def teste_manifesto_json_hashes_contagens_e_relatorios(ambiente):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ambiente` | `Não especificado` | Ambiente de execução contendo funções para leitura, escrita e processamento. |

### Dependências

- `{'nome': 'MANIFESTO.sha256', 'tipo': None, 'categoria': 'import'}`
- `{'nome': 'hashlib', 'tipo': None, 'categoria': 'import'}`
- `{'nome': 'json', 'tipo': None, 'categoria': 'import'}`
- `{'nome': 'pandas', 'tipo': None, 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_manifesto_json_hashes_contagens_e_relatorios(ambiente):
    requer_parquet()
    arquivo, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n2|JOAO\n')
    processar()
    escrever('ID|NOME\n2|JOSE\n3|MARIA\n')
    resultado = processar()
    pasta = raiz / 'CLIENTES'
    manifesto = json.loads((pasta / 'MANIFESTOS' / 'v0002.json').read_text(encoding='utf-8'))
    assert manifesto['versao'] == 'v0002'
    assert manifesto['versao_anterior'] == 'v0001'
    assert manifesto['sha256_origem'] == hashlib.sha256(arquivo.read_bytes()).hexdigest()
    assert manifesto['sha256_snapshot'] == sha256(pasta / manifesto['snapshot'])
    assert manifesto['total_registros'] == 2
    assert (manifesto['incluidos'], manifesto['excluidos']) == (1, 1)
    assert (manifesto['registros_alterados'], manifesto['campos_alterados']) == (1, 1)
    for nome, quantidade in [('incluidos', 1), ('excluidos', 1), ('alterados', 1)]:
        rel = manifesto['relatorios'][nome]
        caminho = pasta / rel['caminho']
        assert caminho.is_file()
        assert sha256(caminho) == rel['sha256']
        assert len(pd.read_parquet(caminho, engine='pyarrow')) == quantidade
    assert indice(raiz)['versoes'][-1] == manifesto
```

</details>

---

<a id="funcao-23"></a>

## teste_tipos_tem_indices_e_snapshots_independentes

Testa a independência dos índices e snapshots entre diferentes tipos de dados em um ambiente.

A função verifica que os índices e snapshots dos clientes e produtos são independentes, mesmo que ambos sejam processados no mesmo ambiente. Ela também garante que as versões dos dados estejam corretamente atualizadas e que os dados lidos a partir dos snapshots sejam consistentes.

### Assinatura

```python
def teste_tipos_tem_indices_e_snapshots_independentes(ambiente):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ambiente` | `Não especificado` | Ambiente de teste contendo funções para escrever, processar e requerer parquet. |

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_tipos_tem_indices_e_snapshots_independentes(ambiente):
    requer_parquet()
    arquivo, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    clientes = processar('CLIENTES')
    escrever('ID|NOME\n1|PRODUTO A\n')
    produtos = processar('PRODUTOS')
    assert clientes['versao'] == produtos['versao'] == 'v0001'
    assert len(indice(raiz, 'CLIENTES')['versoes']) == 1
    assert len(indice(raiz, 'PRODUTOS')['versoes']) == 1
    df_clientes = pd.read_parquet(raiz / 'CLIENTES' / clientes['snapshot'])
    df_produtos = pd.read_parquet(raiz / 'PRODUTOS' / produtos['snapshot'])
    assert df_clientes.loc['1', 'NOME'] == 'ANA'
    assert df_produtos.loc['1', 'NOME'] == 'PRODUTO A'
```

</details>

---

<a id="funcao-24"></a>

## teste_esquema_adicao_e_remocao_manifestos_e_snapshots

Testa a adição e remoção de manifestos e snapshots em um ambiente específico.

A função realiza uma série de operações no ambiente fornecido, escrevendo dados, processando-os e verificando as alterações nos manifestos e snapshots. Utiliza pandas para manipulação de dados e requer a presença do módulo parquet.

### Assinatura

```python
def teste_esquema_adicao_e_remocao_manifestos_e_snapshots(ambiente):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ambiente` | `Não especificado` | Ambiente contendo funções necessárias para a execução dos testes. |

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_esquema_adicao_e_remocao_manifestos_e_snapshots(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    processar()
    escrever('ID|NOME|UF\n1|ANA|SP\n')
    segundo = processar()
    assert segundo['colunas_adicionadas'] == ['UF']
    assert segundo['colunas_removidas'] == []
    assert pd.read_parquet(raiz / 'CLIENTES' / segundo['snapshot']).loc['1', 'UF'] == 'SP'
    escrever('ID|UF\n1|SP\n')
    terceiro = processar()
    assert terceiro['colunas_adicionadas'] == []
    assert terceiro['colunas_removidas'] == ['NOME']
    assert pd.read_parquet(raiz / 'CLIENTES' / terceiro['snapshot']).columns.tolist() == ['UF']
```

</details>

---

<a id="funcao-25"></a>

## teste_falha_publicacao_preserva_indice

Testa a falha na publicação de um índice e verifica se o índice original é preservado.

A função simula uma falha durante a publicação do índice, seja no snapshot ou no relatório, e verifica se o índice original permanece inalterado. Também garante que as versões e ingestões não sejam atualizadas em caso de falha.

### Assinatura

```python
def teste_falha_publicacao_preserva_indice(ambiente, monkeypatch, ponto_falha):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ambiente` | `Não especificado` | Ambiente de teste contendo funções para escrever, processar e obter o índice. |
| `monkeypatch` | `Não especificado` | Objeto usado para modificar comportamentos durante os testes. |
| `ponto_falha` | `Não especificado` | Ponto onde a falha será simulada ('snapshot' ou 'relatorio'). |

### Exceções

- **`OSError`**: Quando ocorre uma falha simulada durante a publicação do índice.

### Dependências

- `inspect`
- `pathlib.Path`
- `pytest`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste_falha_publicacao_preserva_indice(ambiente, monkeypatch, ponto_falha):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    processar()
    indice_path = raiz / 'CLIENTES' / 'MANIFESTOS' / 'indice.json'
    indice_antes = indice_path.read_bytes()
    escrever('ID|NOME\n1|MARIA\n')

    if ponto_falha == 'snapshot':
        original = pd.DataFrame.to_parquet
        def falhar_snapshot(self, path, *args, **kwargs):
            if Path(path).name == 'snapshot.parquet':
                raise OSError('Falha simulada no snapshot')
            return original(self, path, *args, **kwargs)
        monkeypatch.setattr(pd.DataFrame, 'to_parquet', falhar_snapshot)
    elif ponto_falha == 'relatorio':
        original = pd.DataFrame.to_parquet
        def falhar_relatorio(self, path, *args, **kwargs):
            if Path(path).name == 'alterados.parquet':
                raise OSError('Falha simulada no relatório')
            return original(self, path, *args, **kwargs)
        monkeypatch.setattr(pd.DataFrame, 'to_parquet', falhar_relatorio)
    else:
        import inspect

        modulo_real = inspect.getmodule(criar_manifesto_multi)

        assert modulo_real is not None

        original = modulo_real.atomic_json

        def falhar_indice(path, dados):
            if Path(path).resolve() == indice_path.resolve():
                raise OSError(
                    'Falha simulada na publicação do índice'
                )

            return original(path, dados)

        monkeypatch.setattr(
                                modulo_real,
                                'atomic_json',
                                falhar_indice
                            )

    with pytest.raises(OSError, match='Falha simulada'):
        processar()
    assert indice_path.read_bytes() == indice_antes
    assert len(indice(raiz)['versoes']) == 1
    assert len(indice(raiz)['ingestoes']) == 1
    pasta = raiz / 'CLIENTES'
    assert not (pasta / 'VERSOES' / 'v0002.parquet').exists()
    assert not (pasta / 'MANIFESTOS' / 'v0002.json').exists()
    assert not (pasta / 'COMPARACOES' / 'v0001_v0002').exists()
```

</details>

---

<a id="funcao-26"></a>

## escrever

Escreve um texto em um arquivo.

Esta função escreve o conteúdo fornecido em um arquivo, utilizando a codificação especificada. Se a codificação não for fornecida, será usada 'utf-8' por padrão.

### Assinatura

```python
def escrever(texto, *, encoding='utf-8'):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `texto` | `Não especificado` | Conteúdo que será escrito no arquivo. |
| `encoding` | `Não especificado` | Codificação utilizada para escrever o texto no arquivo. O padrão é 'utf-8'. |

### Retorno

**Tipo:** `Não especificado`

O objeto do arquivo após a escrita.

### Dependências

- `arquivo.write_text`

<details>
<summary>Visualizar código-fonte</summary>

```python
def escrever(texto, *, encoding='utf-8'):
        arquivo.write_text(texto, encoding=encoding)
        return arquivo
```

</details>

---

<a id="funcao-27"></a>

## processar

Processa um arquivo e cria um manifesto múltiplo.

A função processa um arquivo especificado pelo parâmetro `id_arquivo` e utiliza argumentos adicionais (`kwargs`) para configurar a criação do manifesto. O padrão é usar o arquivo 'CLIENTES' e codificação UTF-8.

### Assinatura

```python
def processar(id_arquivo='CLIENTES', **kwargs):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `id_arquivo` | `Não especificado` | Identificador do arquivo a ser processado. O valor padrão é 'CLIENTES'. |
| `kwargs` | `Não especificado` | Argumentos adicionais para configurar a criação do manifesto. |

### Dependências

- `{'imports': ['MANIFESTO.criar_manifesto_multi'], 'chamadas': ['criar_manifesto_multi']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def processar(id_arquivo='CLIENTES', **kwargs):
        return criar_manifesto_multi(arquivo, id_arquivo, raiz, encoding='utf-8', **kwargs)
```

</details>

---

<a id="funcao-28"></a>

## falhar_snapshot

Simula uma falha ao tentar criar um snapshot parquet.

A função verifica se o nome do arquivo é 'snapshot.parquet' e, em caso afirmativo, lança uma exceção `OSError` para simular uma falha no processo de criação do snapshot. Caso contrário, a função chama o método original com os argumentos fornecidos.

### Assinatura

```python
def falhar_snapshot(self, path, *args, **kwargs):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém este método. |
| `path` | `Não especificado` | Caminho para o arquivo onde será criado o snapshot. |
| `args` | `Não especificado` | Argumentos adicionais passados ao método original. |
| `kwargs` | `Não especificado` | Palavras-chave adicionais passadas ao método original. |

### Exceções

- **`OSError`**: Quando o nome do arquivo é 'snapshot.parquet', indicando uma falha simulada no processo de criação do snapshot.

### Dependências

- `pathlib.Path`

<details>
<summary>Visualizar código-fonte</summary>

```python
def falhar_snapshot(self, path, *args, **kwargs):
            if Path(path).name == 'snapshot.parquet':
                raise OSError('Falha simulada no snapshot')
            return original(self, path, *args, **kwargs)
```

</details>

---

<a id="funcao-29"></a>

## falhar_relatorio

Simula uma falha ao processar um relatório específico.

A função verifica se o arquivo especificado pelo caminho é 'alterados.parquet'. Se for, lança uma exceção `OSError` simulando uma falha. Caso contrário, chama a função original com os mesmos argumentos.

### Assinatura

```python
def falhar_relatorio(self, path, *args, **kwargs):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe. |
| `path` | `Não especificado` | Caminho do arquivo a ser processado. |
| `args` | `Não especificado` | Argumentos adicionais passados para a função original. |
| `kwargs` | `Não especificado` | Parâmetros nomeados adicionais passados para a função original. |

### Exceções

- **`OSError`**: Quando o arquivo é 'alterados.parquet', simulando uma falha no processamento.

### Dependências

- `pathlib.Path`

<details>
<summary>Visualizar código-fonte</summary>

```python
def falhar_relatorio(self, path, *args, **kwargs):
            if Path(path).name == 'alterados.parquet':
                raise OSError('Falha simulada no relatório')
            return original(self, path, *args, **kwargs)
```

</details>

---

<a id="funcao-30"></a>

## falhar_indice

Simula uma falha ao tentar publicar um índice.

A função verifica se o caminho fornecido é igual ao caminho do índice. Se for, lança uma exceção `OSError` simulando uma falha na publicação do índice. Caso contrário, chama a função original com os mesmos parâmetros.

### Assinatura

```python
def falhar_indice(path, dados):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `path` | `Não especificado` | Caminho para o arquivo ou diretório. |
| `dados` | `Não especificado` | Dados associados ao caminho fornecido. |

### Exceções

- **`OSError`**: Quando o caminho é igual ao caminho do índice, simulando uma falha na publicação.

### Dependências

- `pathlib.Path`

<details>
<summary>Visualizar código-fonte</summary>

```python
def falhar_indice(path, dados):
            if Path(path).resolve() == indice_path.resolve():
                raise OSError(
                    'Falha simulada na publicação do índice'
                )

            return original(path, dados)
```

</details>

---
