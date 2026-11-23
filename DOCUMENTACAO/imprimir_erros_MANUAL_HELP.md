# Referência de Funções

## Índice

- [_texto_pdf](#funcao-1)
- [_escrever](#funcao-2)
- [_percentual_erros](#funcao-3)
- [grafico_resultado](#funcao-4)
- [_revisar](#funcao-5)
- [_criar_revisor](#funcao-6)
- [_criar_resumidor](#funcao-7)
- [_fechar](#funcao-8)
- [_detalhar_tabela](#funcao-9)
- [imprime](#funcao-10)
- [cor](#funcao-11)
- [__init__](#funcao-12)
- [header](#funcao-13)
- [footer](#funcao-14)
- [capa](#funcao-15)

---

<a id="funcao-1"></a>

## _texto_pdf

Converte um valor em uma string e normaliza caracteres específicos.

A função recebe qualquer tipo de objeto, o converte para string e substitui os caracteres '—' e '–' por '-'. Em seguida, encoda a string em 'latin-1' e decodifica novamente, substituindo quaisquer erros de codificação.

### Assinatura

```python
def _texto_pdf(valor: object) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `object` | Valor que será convertido em string e normalizado. |

### Retorno

**Tipo:** `str`

String resultante após a conversão, substituição de caracteres e codificação/decodificação.

### Dependências

- `decode`
- `replace`
- `str`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _texto_pdf(valor: object) -> str:
    texto = str(valor).replace('—', '-').replace('–', '-')
    return texto.encode('latin-1', errors='replace').decode('latin-1')
```

</details>

---

<a id="funcao-2"></a>

## _escrever

Escreve texto em um documento PDF.

Insere o texto fornecido no documento PDF, ajustando a fonte e o tamanho conforme especificado. O texto pode ser exibido em negrito ou normal.

### Assinatura

```python
def _escrever(pdf: FPDF, texto: object, *, tamanho: int = 10, negrito: bool = False) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `pdf` | `FPDF` | Objeto do documento PDF onde o texto será escrito. |
| `texto` | `object` | Texto a ser escrito no documento PDF. Deve ser compatível com a função `_texto_pdf`. |
| `tamanho` | `int` | Tamanho da fonte do texto, em pontos. O valor padrão é 10. |
| `negrito` | `bool` | Indica se o texto deve ser exibido em negrito. O valor padrão é False. |

### Retorno

**Tipo:** `None`

A função não retorna nenhum valor.

### Dependências

- `{'nome': '_texto_pdf', 'categoria': 'chamada'}`
- `{'nome': 'pdf.multi_cell', 'categoria': 'chamada'}`
- `{'nome': 'pdf.set_font', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _escrever(pdf: FPDF, texto: object, *, tamanho: int = 10, negrito: bool = False) -> None:
    pdf.set_font('Courier', 'B' if negrito else '', tamanho)
    pdf.multi_cell(0, 6, _texto_pdf(texto), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
```

</details>

---

<a id="funcao-3"></a>

## _percentual_erros

Calcula o percentual de erros em um DataFrame com base na coluna 'Qtd'.

Esta função calcula o percentual de erros em um DataFrame, considerando a coluna 'Qtd' e um tamanho total especificado. Se o tamanho for menor ou igual a zero, uma exceção é lançada. A função também verifica se a coluna 'Qtd' existe no DataFrame; caso contrário, outra exceção é levantada.

### Assinatura

```python
def _percentual_erros(df: pd.DataFrame, tamanho: int | float) -> float:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `pd.DataFrame` | DataFrame contendo os dados a serem analisados. |
| `tamanho` | `int \| float` | Total de linhas analisadas, que deve ser maior que zero. |

### Retorno

**Tipo:** `float`

Percentual de erros calculado como a soma dos valores numéricos na coluna 'Qtd' dividida pelo tamanho total multiplicada por 100.

### Exceções

- **`ValueError`**: Lancada quando o tamanho de linhas analisadas é menor ou igual a zero.
- **`ValueError`**: Lancada quando a coluna 'Qtd' não está presente no DataFrame.

### Dependências

- `{'nome': 'pandas', 'categoria': 'imports'}`
- `{'nome': 'ValueError', 'categoria': 'chamadas'}`
- `{'nome': 'fillna', 'categoria': 'chamadas'}`
- `{'nome': 'float', 'categoria': 'chamadas'}`
- `{'nome': 'pd.to_numeric', 'categoria': 'chamadas'}`
- `{'nome': 'sum', 'categoria': 'chamadas'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _percentual_erros(df: pd.DataFrame, tamanho: int | float) -> float:
    if tamanho <= 0:
        raise ValueError('O total de linhas analisadas deve ser maior que zero.')
    if 'Qtd' not in df.columns:
        raise ValueError("Coluna obrigatória ausente: 'Qtd'.")
    return float(pd.to_numeric(df['Qtd'], errors='coerce').fillna(0).sum()) / tamanho * 100
```

</details>

---

<a id="funcao-4"></a>

## grafico_resultado

Gera um gráfico de erro com base em dados fornecidos e salva em um caminho especificado.

A função calcula o percentual de erros, ajusta esse valor em relação a uma média setor e gera um gráfico comparativo entre o valor geral e a meta. O gráfico é salvo em um diretório específico.

### Assinatura

```python
def grafico_resultado(df_IMPR, tamanho, path, st=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df_IMPR` | `Não especificado` | DataFrame contendo os dados de impressão. |
| `tamanho` | `Não especificado` | Tamanho dos dados a serem considerados. |
| `path` | `Não especificado` | Caminho onde o gráfico será salvo. |
| `st` | `Não especificado` | Parâmetro opcional que pode ser usado para alguma operação específica, mas não é documentado no código fornecido. |

### Retorno

**Tipo:** `Não especificado`

Fator calculado com base no percentual de erros e a média setor.

### Dependências

- `{'nome': 'matplotlib.pyplot', 'categoria': 'import'}`
- `{'nome': 'numpy', 'categoria': 'import'}`
- `{'nome': 'pathlib.Path', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def grafico_resultado(df_IMPR, tamanho, path, st=None):
    percentual = _percentual_erros(df_IMPR, tamanho)
    fator = percentual / MEDIA_SETOR
    destino = Path(path) / 'IMAGENS' / 'grafico_erro.png'
    destino.parent.mkdir(parents=True, exist_ok=True)

    metas = [META_ERROS, MEDIA_SETOR]
    valores = [percentual, MEDIA_SETOR]
    categorias = ['ERROS', 'ERROS SETOR']

    def cor(valor: float, meta: float):
        distancia = (valor - meta) / meta
        intensidade = min(1.0, abs(distancia))
        return (1.0, 1.0 - intensidade, 1.0 - intensidade) if distancia >= 0 else (1.0 - intensidade, 1.0, 1.0 - intensidade)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    try:
        pos = np.arange(len(categorias))
        largura = 0.35
        ax.bar(pos, metas, largura, color='green', label='Meta / referência')
        ax.bar(pos + largura, valores, largura, color=[cor(v, m) for v, m in zip(valores, metas)], label='Valor geral')
        ax.set_ylabel('%')
        ax.set_title('ERROS (INDICADOR)')
        ax.set_xticks(pos + largura / 2, categorias)
        ax.grid(axis='y', alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(destino, dpi=150)
    finally:
        plt.close(fig)
    return fator
```

</details>

---

<a id="funcao-5"></a>

## _revisar

Revisa um texto utilizando um objeto revisor.

Aplica a revisão de um texto por meio de um objeto revisor, que pode ser None. Caso ocorra uma exceção durante o processo de revisão, o texto original é retornado e uma mensagem de erro é registrada no log.

### Assinatura

```python
def _revisar(revisor, texto: str, instrucao: str = '') -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `revisor` | `Não especificado` | Objeto responsável pela revisão do texto. Pode ser None. |
| `texto` | `str` | Texto que será revisado. |
| `instrucao` | `str` | Instruções adicionais para a revisão. Padrão é uma string vazia. |

### Retorno

**Tipo:** `str`

Texto revisado ou o texto original em caso de falha na revisão.

### Exceções

- **`Exception`**: Qualquer exceção que ocorra durante a chamada ao método `revisar` do objeto revisor.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _revisar(revisor, texto: str, instrucao: str = '') -> str:
    if revisor is None:
        return texto
    try:
        return str(revisor.revisar(texto, instrucao_extra=instrucao))
    except Exception:
        LOG.exception('Falha na revisão por IA; usando texto original.')
        return texto
```

</details>

---

<a id="funcao-6"></a>

## _criar_revisor

Cria uma instância de RevisorLLM se usar_ia for True e st estiver disponível.

A função verifica se a IA deve ser usada e se o estado da sessão (st) está disponível. Se ambos forem verdadeiros, tenta importar e criar uma instância de RevisorLLM com o modelo armazenado em st.session_state.modelo. Caso contrário, retorna None.

### Assinatura

```python
def _criar_revisor(usar_ia: bool, st=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `usar_ia` | `bool` | Indica se a revisão por IA deve ser utilizada. |
| `st` | `Não especificado` | Estado da sessão, que deve conter o modelo para o RevisorLLM. |

### Retorno

**Tipo:** `Não especificado`

Instância de RevisorLLM se usar_ia for True e st estiver disponível; caso contrário, None.

### Exceções

- **`Exception`**: Caso ocorra qualquer exceção ao tentar importar ou criar a instância de RevisorLLM.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _criar_revisor(usar_ia: bool, st=None):
    if not usar_ia or not st:
        return None
    try:
        from ai_funcoes import RevisorLLM
        return RevisorLLM(modelo= st.session_state.modelo)
    except Exception:
        LOG.exception('RevisorLLM indisponível; relatório seguirá sem revisão.')
        return None
```

</details>

---

<a id="funcao-7"></a>

## _criar_resumidor

Cria um resumidor de relatório usando IA se a opção for ativa.

A função verifica se o uso da IA está ativado. Se estiver, tenta importar e instanciar a classe `ResumoValidador` do módulo `ai_funcoes`. Caso contrário, retorna `None`. Em caso de falha na importação ou criação do resumidor, registra uma exceção e também retorna `None`.

### Assinatura

```python
def _criar_resumidor(usar_ia: bool, st=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `usar_ia` | `bool` | Indica se o resumidor de IA deve ser criado. |
| `st` | `Não especificado` | Objeto de estado do Streamlit, usado para acessar o modelo de IA armazenado na sessão. |

### Retorno

**Tipo:** `Não especificado`

Instância da classe `ResumoValidador` se a criação for bem-sucedida; caso contrário, `None`.

### Exceções

- **`Exception`**: Exceção genérica lançada durante o processo de importação ou instanciamento do resumidor de IA.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _criar_resumidor(usar_ia: bool, st=None):
    if not usar_ia:
        return None
    try:
        from ai_funcoes import ResumoValidador
        return ResumoValidador(model=st.session_state.modelo)
    except Exception:
        LOG.exception('ResumoValidador indisponível; relatório seguirá sem resumo por IA.')
        return None
```

</details>

---

<a id="funcao-8"></a>

## _fechar

Fecha um recurso se ele não for `None` e tiver o método `close()`.

Tenta fechar um recurso fornecido, caso ele seja uma instância de um objeto que possui o método `close()`. Caso ocorra uma exceção durante a tentativa de fechar o recurso, ela é capturada e registrada como uma exceção de log.

### Assinatura

```python
def _fechar(recurso) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `recurso` | `Não especificado` | Recurso que será fechado se ele não for `None` e tiver o método `close()`. |

### Retorno

**Tipo:** `None`

Nenhum valor é retornado.

### Dependências

- `{'nome': 'LOG.exception', 'categoria': 'chamada', 'descricao': 'Função utilizada para registrar exceções de log.'}`
- `{'nome': 'hasattr', 'categoria': 'chamada', 'descricao': 'Função utilizada para verificar se um objeto tem um determinado atributo ou método.'}`
- `{'nome': 'recurso.close', 'categoria': 'chamada', 'descricao': 'Método chamado no recurso para fechar o mesmo.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _fechar(recurso) -> None:
    if recurso is not None and hasattr(recurso, 'close'):
        try:
            recurso.close()
        except Exception:
            LOG.exception('Falha ao fechar recurso de IA.')
```

</details>

---

<a id="funcao-9"></a>

## _detalhar_tabela

Detalha uma tabela em um documento PDF.

Esta função adiciona detalhes de uma tabela a um documento PDF, incluindo um resumo gerado por um objeto `resumidor`, se fornecido. Ela também lista os erros encontrados na tabela e suas quantidades correspondentes.

### Assinatura

```python
def _detalhar_tabela(pdf: _PDFValidador, tabela: str, df: pd.DataFrame, resumidor) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `pdf` | `_PDFValidador` | Objeto que representa o documento PDF a ser modificado. |
| `tabela` | `str` | Nome da tabela sendo detalhada. |
| `df` | `pd.DataFrame` | DataFrame contendo os dados da tabela a serem detalhados. |
| `resumidor` | `Não especificado` | Objeto que pode gerar um resumo dos dados da tabela. Se for `None`, nenhum resumo será gerado. |

### Retorno

**Tipo:** `None`

A função não retorna nenhum valor.

### Exceções

- **`Exception`**: Caso ocorra uma exceção durante a geração do resumo, ela será capturada e registrada no log.

### Dependências

- `{'nome': 'datetime.datetime', 'categoria': 'import', 'descricao': 'Utilizado para obter a data atual.'}`
- `{'nome': 'LOG.exception', 'categoria': 'chamada', 'descricao': 'Registra uma exceção no log.'}`
- `{'nome': '_escrever', 'categoria': 'chamada', 'descricao': 'Função auxiliar para escrever texto no documento PDF.'}`
- `{'nome': 'amostra.iterrows', 'categoria': 'chamada', 'descricao': 'Itera sobre as linhas do DataFrame amostra.'}`
- `{'nome': 'datetime.today', 'categoria': 'chamada', 'descricao': 'Obtém a data atual.'}`
- `{'nome': 'df.drop_duplicates', 'categoria': 'chamada', 'descricao': 'Remove duplicatas do DataFrame.'}`
- `{'nome': 'head', 'categoria': 'chamada', 'descricao': 'Retorna as primeiras linhas do DataFrame.'}`
- `{'nome': 'len', 'categoria': 'chamada', 'descricao': 'Calcula o comprimento de um objeto iterável.'}`
- `{'nome': 'linha.get', 'categoria': 'chamada', 'descricao': 'Obtém o valor de uma chave em um dicionário, retornando um valor padrão se a chave não existir.'}`
- `{'nome': 'pdf.add_page', 'categoria': 'chamada', 'descricao': 'Adiciona uma nova página ao documento PDF.'}`
- `{'nome': 'pdf.ln', 'categoria': 'chamada', 'descricao': 'Insere um espaço vertical no documento PDF.'}`
- `{'nome': 'resumidor.gerar_resumo', 'categoria': 'chamada', 'descricao': 'Gera um resumo dos dados da tabela usando o objeto `resumidor`.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _detalhar_tabela(pdf: _PDFValidador, tabela: str, df: pd.DataFrame, resumidor) -> None:
    pdf.add_page()
    _escrever(pdf, f'Tabela: {tabela}', tamanho=12, negrito=True)
    pdf.ln(4)
    amostra = df.drop_duplicates().head(5000)
    if resumidor is not None:
        try:
            resumo = resumidor.gerar_resumo(amostra, max_linhas=5000)
            if resumo:
                _escrever(pdf, resumo)
                pdf.ln(4)
        except Exception:
            LOG.exception('Não foi possível resumir a tabela %s', tabela)

    _escrever(pdf, f'Total de tipos de erros encontrados: {len(df.drop_duplicates())}.')
    if len(df.drop_duplicates()) >= 5000:
        _escrever(pdf, 'O relatório apresenta no máximo 5000 tipos de erros nesta tabela.')
    _escrever(pdf, 'A seguir, os erros por tipo, quantidade e exemplos de registros:')
    pdf.ln(4)
    campos = ['Campo', 'Descrição do Erro', 'Qtd', 'Exemplos (Amostra, linha do arquivo)']
    for _, linha in amostra.iterrows():
        campo, descricao, qtd, exemplos = (linha.get(c, '') for c in campos)
        texto = (f"- O campo '{campo}' apresentou o seguinte erro: {descricao}. "
                 f'Ocorreu em {qtd} registro(s). Exemplos: {exemplos}.')
        _escrever(pdf, texto)
        pdf.ln(2)
    pdf.ln(4)
    _escrever(pdf, f"Finalizado em {datetime.today():%d/%m/%Y}, tabela {tabela}.", negrito=True)
```

</details>

---

<a id="funcao-10"></a>

## imprime

Gera um relatório PDF com os resultados da validação estrutural dos arquivos enviados.

A função cria um relatório em PDF contendo a análise de inconsistências encontradas nos dados. O relatório inclui categorias de erros, média setorial e gráficos, se disponíveis. Caso ocorram erros durante o processo, uma exceção é lançada.

### Assinatura

```python
def imprime(FATOR, df_IMPR, cd_EMP, tbl_avl, path, tipo_erro, st=None, IA=False):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `FATOR` | `Não especificado` | Indicador relativo à média setorial. |
| `df_IMPR` | `Não especificado` | DataFrame contendo os resultados da validação dos dados. |
| `cd_EMP` | `Não especificado` | Código da empresa. |
| `tbl_avl` | `Não especificado` | Lista de tabelas avaliadas. |
| `path` | `Não especificado` | Caminho onde o relatório será salvo. |
| `tipo_erro` | `Não especificado` | Tipo de erro associado à validação. |
| `st` | `Não especificado` | Objeto Streamlit para atualização da barra de progresso, se aplicável. |
| `IA` | `Não especificado` | Indica se a validação foi realizada por um assistente de inteligência artificial. |

### Retorno

**Tipo:** `Não especificado`

Mensagem indicando o sucesso na geração do relatório ou uma exceção em caso de erro.

### Exceções

- **`TypeError`**: Quando 'df_IMPR' não é um pandas.DataFrame.
- **`ValueError`**: Quando há colunas obrigatórias ausentes no DataFrame 'df_IMPR'.

### Dependências

- `{'nome': 'datetime.datetime', 'categoria': 'importado', 'descricao': 'Utilizado para obter a data atual.'}`
- `{'nome': 'pathlib.Path', 'categoria': 'importado', 'descricao': 'Utilizado para manipulação de caminhos de arquivo.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def imprime(FATOR, df_IMPR, cd_EMP, tbl_avl, path, tipo_erro, st=None, IA=False):

    if not isinstance(df_IMPR, pd.DataFrame):
        raise TypeError('df_IMPR deve ser um pandas.DataFrame.')
    destino = Path(path) / 'RELATORIOS' / f'erros_{datetime.today():%Y%m%d}.pdf'
    destino.parent.mkdir(parents=True, exist_ok=True)
    pdf = _PDFValidador(cd_EMP)
    revisor = _criar_revisor(IA, st=st)
    resumidor = None
    barra = None
    try:
        abertura = ('Este relatório apresenta os resultados da validação estrutural dos arquivos enviados. '
                    'As inconsistências devem ser corrigidas ou justificadas antes da análise subsequente.')
        pdf.capa(_revisar(revisor, abertura, 'Se necessário, complemente em até três parágrafos.'))
        pdf.add_page()
        _escrever(pdf, 'Introdução', tamanho=14, negrito=True)
        _escrever(pdf, 'O validador verifica integridade e qualidade dos dados. As principais categorias incluem:')
        categorias = [
            'Dependência: validade de um campo condicionada a outro.',
            'Valores possíveis: valor fora do conjunto permitido.',
            'Tipo: incompatibilidade com o tipo esperado.',
            'Formato: informação fora do padrão exigido.',
            'Ausência: campo obrigatório não preenchido.',
            'Cruzamento interno: inconsistência entre campos do mesmo registro.',
        ]
        _escrever(pdf, _revisar(revisor, '\n'.join(f'{i}. {x}' for i, x in enumerate(categorias, 1)),
                              'Preserve os seis itens e a numeração.'))
        pdf.ln(5)
        _escrever(pdf, 'Corrija ou justifique as ocorrências e execute novamente a validação.')
        pdf.ln(5)
        if tbl_avl and len(df_IMPR) > 5000:
            _escrever(pdf, 'Em razão do limite de ocorrências, as tabelas avaliadas incluem:')
            for tabela in tbl_avl:
                _escrever(pdf, f'- {tabela}')
        _escrever(pdf, f'Indicador relativo à média setorial: {float(FATOR):.2f} vez(es).')
        if FATOR > 3:
            avaliacao = 'Indicador crítico: a empresa merece atenção especial.'
        elif FATOR > 1:
            avaliacao = 'Indicador acima da média: recomenda-se melhorar a qualidade dos dados.'
        else:
            avaliacao = 'Indicador dentro da faixa de referência; o objetivo continua sendo zerar os erros.'
        _escrever(pdf, avaliacao)
        grafico = Path(path) / 'IMAGENS' / 'grafico_erro.png'
        if grafico.is_file():
            pdf.ln(5)
            pdf.image(str(grafico), x=Align.C, w=145)
        else:
            LOG.warning('Gráfico não encontrado em %s; PDF gerado sem imagem.', grafico)

        if df_IMPR.empty:
            pdf.add_page()
            _escrever(pdf, 'Nenhuma inconsistência registrada no conjunto informado.', tamanho=12)
        else:
            obrigatorias = {'Nm_TAB', 'Campo', 'Descrição do Erro', 'Qtd', 'Exemplos (Amostra, linha do arquivo)'}
            faltantes = obrigatorias - set(df_IMPR.columns)
            if faltantes:
                raise ValueError(f'Colunas obrigatórias ausentes: {sorted(faltantes)}')
            tabelas = df_IMPR['Nm_TAB'].dropna().drop_duplicates().tolist()
            resumidor = _criar_resumidor(IA)
            if st is not None and tabelas:
                barra = st.progress(0, text='Iniciando relatório')
            for indice, tabela in enumerate(tabelas, 1):
                dados = df_IMPR.loc[df_IMPR['Nm_TAB'] == tabela]
                _detalhar_tabela(pdf, str(tabela), dados, resumidor)
                if barra is not None:
                    barra.progress(indice / len(tabelas), text=f'Tabela {tabela}: {indice}/{len(tabelas)}')
        pdf.output(str(destino))
        LOG.info('PDF gerado: %s', destino)
        return 'OK'
    finally:
        if barra is not None:
            barra.empty()
        _fechar(resumidor)
        _fechar(revisor)
```

</details>

---

<a id="funcao-11"></a>

## cor

Calcula a cor com base na distância entre um valor e uma meta.

A função calcula a intensidade de vermelho, verde e azul com base na distância do valor fornecido em relação à meta. A intensidade é limitada entre 0 e 1. Se o valor for maior ou igual à meta, a cor será mais vermelha; se for menor, a cor será mais verde.

### Assinatura

```python
def cor(valor: float, meta: float):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `float` | O valor numérico para o qual a distância é calculada em relação à meta. |
| `meta` | `float` | O valor de referência usado para calcular a distância. |

### Retorno

**Tipo:** `(float, float, float)`

Uma tupla representando as intensidades RGB da cor calculada.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def cor(valor: float, meta: float):
        distancia = (valor - meta) / meta
        intensidade = min(1.0, abs(distancia))
        return (1.0, 1.0 - intensidade, 1.0 - intensidade) if distancia >= 0 else (1.0 - intensidade, 1.0, 1.0 - intensidade)
```

</details>

---

<a id="funcao-12"></a>

## __init__

Inicializa uma instância da classe, configurando parâmetros específicos.

Este método é responsável por inicializar uma nova instância da classe, chamando o construtor da superclasse e configurando propriedades internas relacionadas à empresa e layout de página.

### Assinatura

```python
def __init__(self, empresa: object):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Referência à instância atual da classe. |
| `empresa` | `object` | Objeto representando a empresa associada à instância. |

### Dependências

- `{'chamadas': ['__init__', 'self.alias_nb_pages', 'self.set_auto_page_break', 'self.set_left_margin', 'self.set_right_margin', 'super']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def __init__(self, empresa: object):
        super().__init__()
        self.empresa = empresa
        self.alias_nb_pages()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_left_margin(25)
        self.set_right_margin(20)
```

</details>

---

<a id="funcao-13"></a>

## header

Exibe um cabeçalho na página, exceto na primeira.

Se não for a primeira página, configura o estilo e exibe um texto centralizado com uma linha abaixo. A função é usada em contextos onde cabeçalhos específicos são necessários após a primeira página.

### Assinatura

```python
def header(self):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém o método. |

### Dependências

- `self.cell`
- `self.line`
- `self.ln`
- `self.page_no`
- `self.set_draw_color`
- `self.set_font`
- `self.set_text_color`

<details>
<summary>Visualizar código-fonte</summary>

```python
def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Courier', 'B', 9)
        self.set_text_color(110, 110, 110)
        self.cell(0, 9, 'RESULTADO DO VALIDADOR', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_draw_color(160, 160, 160)
        self.line(20, 20, 190, 20)
        self.ln(9)
        self.set_text_color(0, 0, 0)
```

</details>

---

<a id="funcao-14"></a>

## footer

Gera o rodapé da página em um documento PDF.

Se não for a primeira página, adiciona o número da página no rodapé do documento PDF. Utiliza uma fonte Courier Italic de tamanho 8 e cor cinza para exibir o texto.

### Assinatura

```python
def footer(self):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém o método. |

### Dependências

- `self.cell`
- `self.page_no`
- `self.set_font`
- `self.set_text_color`
- `self.set_y`

<details>
<summary>Visualizar código-fonte</summary>

```python
def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font('Courier', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', align='C')
```

</details>

---

<a id="funcao-15"></a>

## capa

Adiciona uma capa ao documento PDF.

Esta função adiciona uma página ao documento PDF, preenche-a com um fundo escuro e exibe o título do relatório seguido por uma seção de etapa de validação de estrutura. Se fornecido, um texto adicional é incluído abaixo da seção de validação.

### Assinatura

```python
def capa(self, texto: str = ''):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que chama a função. |
| `texto` | `str` | Texto adicional a ser exibido abaixo da seção de validação. Se não for fornecido, nenhum texto extra será adicionado. |

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def capa(self, texto: str = ''):
        self.add_page()
        self.set_fill_color(48, 48, 48)
        self.rect(0, 0, 210, 297, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 22)
        self.ln(65)
        self.multi_cell(0, 13, _texto_pdf(f'Relatório de Análise\nEmpresa {self.empresa}'), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 13)
        self.ln(10)
        self.multi_cell(0, 9, 'Etapa de Validação de Estrutura', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if texto:
            self.ln(22)
            self.set_font('Helvetica', '', 11)
            self.multi_cell(0, 7, _texto_pdf(texto), align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
```

</details>

---
