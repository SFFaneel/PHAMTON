# Referência de Funções

## Índice

- [duplo_positivo](#funcao-1)
- [inteiro_positivo](#funcao-2)
- [texto_maximo](#funcao-3)
- [data_inc](#funcao-4)
- [gerar_modelos](#funcao-5)
- [gerar_invalidos](#funcao-6)
- [gerar_obrigatorios](#funcao-7)
- [aplicar_invalido](#funcao-8)
- [test_modelo_valido](#funcao-9)
- [test_modelo_invalido](#funcao-10)
- [test_campos_obrigatorios](#funcao-11)
- [test_campos_extras](#funcao-12)

---

<a id="funcao-1"></a>

## duplo_positivo

Gera uma lista de valores para um campo específico.

A função cria uma lista contendo diferentes tipos de valores (zero, negativo, não numérico e vazio) associados ao campo fornecido. Cada valor é descrito em uma string.

### Assinatura

```python
def duplo_positivo(campo):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `campo` | `Não especificado` | Nome do campo para o qual os valores serão gerados. |

### Retorno

**Tipo:** `Não especificado`

Lista de dicionários, cada um contendo informações sobre um valor específico.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def duplo_positivo(campo):
    return [
                {
                    "campo": campo,
                    "valor": "0.",
                    "descricao": "Valor zero",
                },
                {
                    "campo": campo,
                    "valor": "-1.",
                    "descricao": "Valor negativo",
                },
                {
                    "campo": campo,
                    "valor": "abc",
                    "descricao": "Valor não numérico",
                },
                {
                    "campo": campo,
                    "valor": "",
                    "descricao": "Valor vazio",
                },
            ]
```

</details>

---

<a id="funcao-2"></a>

## inteiro_positivo

Gera uma lista de exemplos para um campo específico.

A função cria uma lista contendo diferentes tipos de valores, incluindo zero, negativo, não numérico e vazio, todos associados ao campo fornecido.

### Assinatura

```python
def inteiro_positivo(campo):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `campo` | `Não especificado` | Nome do campo para o qual os exemplos serão gerados. |

### Retorno

**Tipo:** `Não especificado`

Lista de dicionários, cada um contendo informações sobre um exemplo.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def inteiro_positivo(campo):
    return [
                {
                    "campo": campo,
                    "valor": "0",
                    "descricao": "Valor zero",
                },
                {
                    "campo": campo,
                    "valor": "-1",
                    "descricao": "Valor negativo",
                },
                {
                    "campo": campo,
                    "valor": "abc",
                    "descricao": "Valor não numérico",
                },
                {
                    "campo": campo,
                    "valor": "",
                    "descricao": "Valor vazio",
                },
            ]
```

</details>

---

<a id="funcao-3"></a>

## texto_maximo

Gera um texto com o valor 'X' repetido acima de um determinado limite de caracteres.

A função cria uma lista contendo um único dicionário. Esse dicionário possui as chaves 'campo', 'valor' e 'descricao'. O valor é uma string composta por 'X' repetidas vezes, onde o número de repetições é igual ao limite fornecido mais um.

### Assinatura

```python
def texto_maximo(campo, limite):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `campo` | `Não especificado` | Nome do campo associado ao texto gerado. |
| `limite` | `Não especificado` | Limite de caracteres que o valor 'X' deve ultrapassar. |

### Retorno

**Tipo:** `Não especificado`

Lista contendo um único dicionário com as informações do campo, valor e descrição.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def texto_maximo(campo, limite):
    return [
                {
                    "campo": campo,
                    "valor": "X" * (limite + 1),
                    "descricao": f"Texto acima de {limite} caracteres",
                },
            ]
```

</details>

---

<a id="funcao-4"></a>

## data_inc

Gera uma lista de objetos contendo informações sobre diferentes formatos inválidos para um campo específico.

A função cria uma lista de objetos, cada um representando um formato inválido que o campo pode ter. Cada objeto contém o nome do campo, o valor com o formato inválido e uma descrição explicativa.

### Assinatura

```python
def data_inc(campo):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `campo` | `Não especificado` | Nome do campo para o qual os formatos inválidos serão gerados. |

### Retorno

**Tipo:** `Não especificado`

Lista de objetos, cada um com informações sobre um formato inválido do campo.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def data_inc(campo):
    return [
                {
                    "campo": campo,
                    "valor": "01/01/2025",
                    "descricao": f"{campo} com formato inválido (dd/mm/yyyy).",
                },
                {
                    "campo": campo,
                    "valor": "12/21/2025",
                    "descricao": f"{campo} com formato inválido (mm/dd/yyyy).",
                },
                {
                    "campo": campo,
                    "valor": "",
                    "descricao": f"{campo} com formato inválido (vazio).",
                },
                {
                    "campo": campo,
                    "valor": "20250225",
                    "descricao": f"{campo} com formato inválido (yyyymmdd).",
                },
                {
                    "campo": campo,
                    "valor": "2025-02-25",
                    "descricao": f"{campo} com formato inválido (yyyy-mm-dd).",
                },
            ]
```

</details>

---

<a id="funcao-5"></a>

## gerar_modelos

Gera parâmetros de teste para diferentes casos de modelos.

Itera sobre uma lista de casos de modelos e gera parâmetros de teste utilizando a função `pytest.param` do módulo pytest. Cada caso é identificado pelo nome da classe do modelo correspondente.

### Assinatura

```python
def gerar_modelos():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Retorno

**Tipo:** `Não especificado`

Parâmetros de teste gerados para cada caso de modelo.

### Dependências

- `pytest`

<details>
<summary>Visualizar código-fonte</summary>

```python
def gerar_modelos():
    for caso in CASOS_MODELOS:
        yield pytest.param(
                                caso,
                                id=caso["modelo"].__name__,
                            )
```

</details>

---

<a id="funcao-6"></a>

## gerar_invalidos

Gera parâmetros de teste inválidos para modelos.

Itera sobre uma lista de casos de modelo e gera parâmetros de teste inválidos utilizando a biblioteca pytest. Cada caso contém um modelo e uma lista de valores inválidos associados a ele. Os parâmetros gerados incluem o caso completo, o valor inválido específico e uma string de identificação única.

### Assinatura

```python
def gerar_invalidos():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Retorno

**Tipo:** `Não especificado`

Parâmetros de teste inválidos gerados pela função.

### Dependências

- `pytest`

<details>
<summary>Visualizar código-fonte</summary>

```python
def gerar_invalidos():
    for caso in CASOS_MODELOS:
        modelo = caso["modelo"]

        for invalido in caso["invalidos"]:
            yield pytest.param(
                                    caso,
                                    invalido,
                                    id=(
                                        f"{modelo.__name__}-"
                                        f"{invalido['campo']}-"
                                        f"{invalido['descricao']}"
                                    ),
                                )
```

</details>

---

<a id="funcao-7"></a>

## gerar_obrigatorios

Gera parâmetros para testes de campos obrigatórios em modelos.

Itera sobre uma lista de casos de modelo e identifica os campos que são obrigatórios, gerando parâmetros para testes utilizando a biblioteca pytest.

### Assinatura

```python
def gerar_obrigatorios():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Retorno

**Tipo:** `Não especificado`

Parâmetros gerados para testes de campos obrigatórios.

### Dependências

- `pytest`

<details>
<summary>Visualizar código-fonte</summary>

```python
def gerar_obrigatorios():
    for caso in CASOS_MODELOS:
        modelo = caso["modelo"]

        for campo, info in modelo.model_fields.items():
            if info.is_required():
                yield pytest.param(
                                        caso,
                                        campo,
                                        id=f"{modelo.__name__}-{campo}-obrigatorio",
                                    )
```

</details>

---

<a id="funcao-8"></a>

## aplicar_invalido

Aplica uma operação de alteração, adição ou remoção em um conjunto de dados.

Esta função recebe dois parâmetros: `dados_validos`, que é um dicionário representando os dados válidos, e `invalido`, que contém informações sobre a operação a ser realizada. A função realiza uma cópia dos dados válidos para evitar modificá-los diretamente.

### Assinatura

```python
def aplicar_invalido(dados_validos, invalido):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `dados_validos` | `dict` | Dicionário contendo os dados válidos que serão modificados. |
| `invalido` | `dict` | Dicionário contendo informações sobre a operação a ser realizada, incluindo o tipo de operação (`operacao`), o campo alvo (`campo`) e o valor a ser usado (`valor`). |

### Retorno

**Tipo:** `dict`

Novo dicionário com as modificações aplicadas.

### Exceções

- **`ValueError`**: Quando a operação especificada não é suportada.

### Dependências

- `copy.deepcopy`

<details>
<summary>Visualizar código-fonte</summary>

```python
def aplicar_invalido(dados_validos, invalido):
    dados = deepcopy(dados_validos)

    operacao = invalido.get("operacao", "alterar")
    campo = invalido["campo"]

    if operacao in ("alterar", "adicionar"):
        dados[campo] = invalido["valor"]

    elif operacao == "remover":
        dados.pop(campo)

    else:
        raise ValueError(
                            f"Operação não suportada: {operacao}"
                        )

    return dados
```

</details>

---

<a id="funcao-9"></a>

## test_modelo_valido

Testa se os dados são válidos para um modelo específico.

Valida os dados fornecidos contra um modelo especificado, utilizando a função `model_validate` do modelo. Lança uma exceção caso os dados não sejam válidos.

### Assinatura

```python
def test_modelo_valido(caso):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `caso` | `Não especificado` | Um dicionário contendo o modelo e os dados a serem validados. |

### Dependências

- `pytest`

<details>
<summary>Visualizar código-fonte</summary>

```python
def test_modelo_valido(caso):
    modelo = caso["modelo"]
    dados = caso["valido"]

    instancia = modelo.model_validate(dados)

    assert isinstance(instancia, modelo)
```

</details>

---

<a id="funcao-10"></a>

## test_modelo_invalido

Testa um modelo com dados inválidos para verificar a geração de erros de validação.

A função testa um modelo utilizando dados válidos e inválidos. Ela aplica as alterações inválidas aos dados válidos, tenta validar o modelo com os dados modificados e verifica se ocorrem erros de validação conforme esperado. Se especificado, também verifica o tipo do erro gerado.

### Assinatura

```python
def test_modelo_invalido(caso, invalido):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `caso` | `Não especificado` | Um dicionário contendo os dados necessários para o teste, incluindo um modelo válido e uma lista de alterações inválidas. |
| `invalido` | `Não especificado` | Uma lista de dicionários, onde cada dicionário contém informações sobre uma alteração inválida a ser aplicada aos dados válidos. |

### Dependências

- `pytest`

<details>
<summary>Visualizar código-fonte</summary>

```python
def test_modelo_invalido(caso, invalido):
    modelo = caso["modelo"]

    dados = aplicar_invalido(
                                caso["valido"],
                                invalido,
                            )

    modelo.model_validate(caso["valido"])

    with pytest.raises(ValidationError) as exc:
        modelo.model_validate(dados)

    erros = exc.value.errors()

    campo_esperado = invalido["campo"]

    assert any(
                    erro["loc"] == (campo_esperado,)
                    for erro in erros
                ), (
                    f"Esperado erro no campo {campo_esperado}. "
                    f"Erros encontrados: {erros}"
                )

    if "tipo_erro" in invalido:
        assert any(
                        erro["loc"] == (campo_esperado,)
                        and erro["type"] == invalido["tipo_erro"]
                        for erro in erros
                    )
```

</details>

---

<a id="funcao-11"></a>

## test_campos_obrigatorios

Testa se um campo é obrigatório em um modelo de dados.

Valida que a remoção de um campo obrigatório resulta em uma exceção de validação.

### Assinatura

```python
def test_campos_obrigatorios(caso, campo):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `caso` | `Não especificado` | Caso de teste contendo o modelo e os dados válidos. |
| `campo` | `Não especificado` | Nome do campo que deve ser removido para testar a validação. |

### Exceções

- **`ValidationError`**: Quando o campo obrigatório é removido e não há tratamento adequado.

### Dependências

- `pytest`

<details>
<summary>Visualizar código-fonte</summary>

```python
def test_campos_obrigatorios(caso, campo):
    modelo = caso["modelo"]
    dados = caso["valido"].copy()

    dados.pop(campo)

    with pytest.raises(ValidationError) as exc:
        modelo.model_validate(dados)

    assert any(
                    erro["loc"] == (campo,)
                    and erro["type"] == "missing"
                    for erro in exc.value.errors()
                )
```

</details>

---

<a id="funcao-12"></a>

## test_campos_extras

Testa se um modelo rejeita campos extras em dados de entrada.

A função testa a capacidade do modelo para rejeitar campos que não estão definidos no esquema. Ele cria uma cópia dos dados válidos, adiciona um campo inexistente e valida os dados usando o método `model_validate` do modelo. Se o campo extra for rejeitado corretamente, a função passa.

### Assinatura

```python
def test_campos_extras(caso):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `caso` | `Não especificado` | Um dicionário contendo informações sobre o caso de teste, incluindo um modelo e dados válidos. |

### Exceções

- **`ValidationError`**: Quando ocorre uma validação de erro durante a chamada de `model_validate`.

### Dependências

- `pytest`

<details>
<summary>Visualizar código-fonte</summary>

```python
def test_campos_extras(caso):
    modelo = caso["modelo"]
    dados = caso["valido"].copy()

    dados["campo_inexistente"] = "teste"

    with pytest.raises(ValidationError) as exc:
        modelo.model_validate(dados)

    assert any(
                erro["loc"] == ("campo_inexistente",)
                and erro["type"] == "extra_forbidden"
                for erro in exc.value.errors()
                )
```

</details>

---
