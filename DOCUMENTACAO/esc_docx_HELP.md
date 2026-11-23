# Referência de Funções

## Índice

- [exportar_texto](#funcao-1)

---

<a id="funcao-1"></a>

## exportar_texto

Exporta um texto para um arquivo especificado.

Cria ou sobrescreve um arquivo em um caminho determinado e escreve o texto fornecido nele. Se 'sobrescrever' for False, adiciona uma nova linha antes do texto existente.

### Assinatura

```python
def exportar_texto(caminho: str, nm: str, texto: str, sobrescrever: bool = True):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `caminho` | `str` | Caminho onde o arquivo será salvo. |
| `nm` | `str` | Nome do arquivo a ser criado ou sobrescrito. |
| `texto` | `str` | Texto que será escrito no arquivo. |
| `sobrescrever` | `bool` | Indica se o arquivo deve ser sobrescrito (True) ou adicionado ao final (False). |

### Retorno

**Tipo:** `str`

Mensagem de sucesso indicando que a operação foi concluída.

### Dependências

- `decoradores.monitor_completo`
- `os`

<details>
<summary>Visualizar código-fonte</summary>

```python
def exportar_texto(caminho: str, nm: str, texto: str, sobrescrever: bool = True):

    if not os.path.exists(caminho):
        os.makedirs(caminho, exist_ok=True)

    arquivo = os.path.join(caminho, nm)
    modo = "w" if sobrescrever else "a"

    if not sobrescrever:
        texto = "\n" + texto

    with open(arquivo, modo, encoding="utf-8") as f:
        f.write(texto)

    return "OK"
```

</details>

---
