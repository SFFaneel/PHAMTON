# Referência de Funções

## Índice

- [_conectar](#funcao-1)
- [_tabelas_existentes](#funcao-2)
- [_colunas](#funcao-3)
- [_descricao_html](#funcao-4)
- [visualizar_manifesto_exec](#funcao-5)

---

<a id="funcao-1"></a>

## _conectar

Conecta a um banco de dados SQLite.

Estabelece uma conexão com um banco de dados SQLite localizado no caminho especificado. Verifica se o arquivo do banco de dados existe antes de tentar a conexão.

### Assinatura

```python
def _conectar(database: str | Path) -> sqlite3.Connection:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `database` | `str \| Path` | Caminho para o arquivo do banco de dados SQLite. |

### Retorno

**Tipo:** `sqlite3.Connection`

Conexão estabelecida com o banco de dados.

### Exceções

- **`FileNotFoundError`**: Quando o arquivo do banco de dados não é encontrado no caminho especificado.

### Dependências

- `pathlib.Path`
- `sqlite3`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _conectar(database: str | Path) -> sqlite3.Connection:
    caminho = Path(database).expanduser().resolve()
    if not caminho.is_file():
        raise FileNotFoundError(f"Banco de auditoria não encontrado: {caminho}")
    return sqlite3.connect(caminho.as_uri() + "?mode=ro", uri=True, timeout=10)
```

</details>

---

<a id="funcao-2"></a>

## _tabelas_existentes

Obtém um conjunto de nomes das tabelas existentes em uma conexão SQLite.

Executa uma consulta SQL para recuperar os nomes de todas as tabelas no banco de dados associado à conexão fornecida e retorna esses nomes como um conjunto de strings.

### Assinatura

```python
def _tabelas_existentes(conn: sqlite3.Connection) -> set[str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `conn` | `sqlite3.Connection` | Conexão SQLite estabelecida com o banco de dados. |

### Retorno

**Tipo:** `set[str]`

Conjunto contendo os nomes das tabelas existentes no banco de dados.

### Dependências

- `{'nome': 'sqlite3', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _tabelas_existentes(conn: sqlite3.Connection) -> set[str]:
    return {
        linha[0] for linha in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
```

</details>

---

<a id="funcao-3"></a>

## _colunas

Recupera as colunas de uma tabela no banco de dados SQLite.

Executa um comando SQL para obter informações sobre as colunas de uma tabela específica e retorna os nomes dessas colunas.

### Assinatura

```python
def _colunas(conn: sqlite3.Connection, tabela: str) -> list[str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `conn` | `sqlite3.Connection` | Conexão com o banco de dados SQLite. |
| `tabela` | `str` | Nome da tabela do qual as colunas serão recuperadas. |

### Retorno

**Tipo:** `list[str]`

Lista de nomes das colunas na tabela especificada.

### Dependências

- `sqlite3`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _colunas(conn: sqlite3.Connection, tabela: str) -> list[str]:
    return [linha[1] for linha in conn.execute(f'PRAGMA table_info("{tabela}")')]
```

</details>

---

<a id="funcao-4"></a>

## _descricao_html

Gera uma descrição HTML formatada com um título, objetivo e tabela.

A função cria uma seção HTML estilizada contendo um título em letras maiúsculas, um parágrafo de texto e uma tabela. Utiliza a biblioteca `html` para escapar caracteres especiais nos textos fornecidos.

### Assinatura

```python
def _descricao_html(titulo: str, objetivo: str, tabela: str) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `titulo` | `str` | Título da seção, exibido em letras maiúsculas. |
| `objetivo` | `str` | Texto descrevendo o objetivo ou conteúdo da seção. |
| `tabela` | `str` | Conteúdo da tabela a ser exibido dentro da seção. |

### Retorno

**Tipo:** `str`

String contendo o código HTML gerado.

### Dependências

- `html`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _descricao_html(titulo: str, objetivo: str, tabela: str) -> str:
    return f"""
                <section style="font-family:system-ui,sans-serif; border:1px solid #d7dce2;
                                border-radius:12px; padding:16px 20px; margin:6px 0 18px;">
                <div style="font-size:12px; font-weight:700; letter-spacing:.08em;
                            color:#65758b; text-transform:uppercase;">{html.escape(titulo)}</div>
                <p style="font-size:15px; line-height:1.55; margin:8px 0;">
                    {html.escape(objetivo)}
                </p>
                </section>
                """
```

</details>

---

<a id="funcao-5"></a>

## visualizar_manifesto_exec

Visualiza o Manifesto Eletrônico de Execuções em uma interface web utilizando Streamlit.

A função `visualizar_manifesto_exec` é responsável por carregar e exibir os dados do Manifesto Eletrônico de Execuções em uma interface web interativa usando a biblioteca Streamlit. Ela permite visualizar detalhes sobre as execuções, eventos, métricas, artefatos e chamadas auxiliares.

### Assinatura

```python
def visualizar_manifesto_exec(database: str | Path, st=None) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `database` | `str \| Path` | Caminho para o banco de dados SQLite que contém os registros do Manifesto Eletrônico de Execuções. |
| `st` | `Não especificado` | Objeto Streamlit usado para criar a interface web. Se não for fornecido, a função retornará imediatamente. |

### Retorno

**Tipo:** `None`

A função não retorna nenhum valor explícito.

### Exceções

- **`OSError`**: Quando ocorre um erro ao abrir o banco de dados.
- **`sqlite3.Error`**: Quando ocorre um erro relacionado à operação do banco de dados SQLite.
- **`pd.errors.DatabaseError`**: Quando ocorre um erro ao ler os dados do banco de dados usando pandas.

### Dependências

- `{'nome': 'UTILS.bsc_dados_reg', 'categoria': 'importação'}`
- `{'nome': 'pandas', 'categoria': 'importação'}`
- `{'nome': 'TABELAS.items', 'categoria': 'chamada'}`
- `{'nome': '_colunas', 'categoria': 'chamada'}`
- `{'nome': '_conectar', 'categoria': 'chamada'}`
- `{'nome': '_descricao_html', 'categoria': 'chamada'}`
- `{'nome': '_tabelas_existentes', 'categoria': 'chamada'}`
- `{'nome': 'conn.execute', 'categoria': 'chamada'}`
- `{'nome': 'df.to_csv', 'categoria': 'chamada'}`
- `{'nome': 'encode', 'categoria': 'chamada'}`
- `{'nome': 'fetchall', 'categoria': 'chamada'}`
- `{'nome': 'fetchone', 'categoria': 'chamada'}`
- `{'nome': 'list', 'categoria': 'chamada'}`
- `{'nome': 'max', 'categoria': 'chamada'}`
- `{'nome': 'next', 'categoria': 'chamada'}`
- `{'nome': 'pd.read_sql_query', 'categoria': 'chamada'}`
- `{'nome': 'replace', 'categoria': 'chamada'}`
- `{'nome': 'st.caption', 'categoria': 'chamada'}`
- `{'nome': 'st.columns', 'categoria': 'chamada'}`
- `{'nome': 'st.container', 'categoria': 'chamada'}`
- `{'nome': 'st.dataframe', 'categoria': 'chamada'}`
- `{'nome': 'st.download_button', 'categoria': 'chamada'}`
- `{'nome': 'st.error', 'categoria': 'chamada'}`
- `{'nome': 'st.html', 'categoria': 'chamada'}`
- `{'nome': 'st.info', 'categoria': 'chamada'}`
- `{'nome': 'st.number_input', 'categoria': 'chamada'}`
- `{'nome': 'st.selectbox', 'categoria': 'chamada'}`
- `{'nome': 'st.tabs', 'categoria': 'chamada'}`
- `{'nome': 'zip', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def visualizar_manifesto_exec(database: str | Path, st=None) -> None:
    if not st:
        return
    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
    st.html(f"<style>{css}</style>")
    cols1 = st.columns([1,5,1], gap='small')
    with cols1[1]:
        with st.container() as borda:
            st.html("""
                        <style>
                        .manifesto-ajuda {
                            font-family: inherit;
                            line-height: 1.65;
                            color: var(--text-color);
                        }

                        .manifesto-ajuda h1 {
                            text-align: center;
                            font-size: 1.5rem;
                            margin-bottom: 24px;
                        }

                        .manifesto-ajuda h2 {
                            font-size: 1.1rem;
                            font-weight: 650;
                            margin: 22px 0 10px;
                        }

                        .manifesto-ajuda p {
                            margin: 8px 0;
                            font-size: 0.92rem;
                            text-align: justify;
                            text-indent: 40px;
                        }

                        .manifesto-ajuda .destaque {
                            background: var(--secondary-background-color);
                            border-left: 3px solid #4F8DBD;
                            padding: 12px 16px;
                            border-radius: 5px;
                            margin: 18px 0;
                        }

                        .manifesto-ajuda .destaque p {
                            text-indent: 0;
                            margin: 0;
                        }
                    </style>

                    <section class="manifesto-ajuda">

                        <h1>Visualização do Manifesto Eletrônico de Execuções</h1>

                        <h2>O que é o Manifesto Eletrônico de Execuções?</h2>

                        <p  style="text-align: justify;text-indent: 40px">
                            O <strong>Manifesto Eletrônico de Execuções</strong> é um mecanismo
                            de registro e acompanhamento das rotinas computacionais
                            utilizadas no processamento, na validação e na análise
                            dos dados. Sua finalidade é documentar a execução dos
                            programas, identificando quando foram iniciados,
                            quais procedimentos foram realizados, quais recursos
                            foram utilizados e quais resultados foram produzidos.
                        </p>

                        <p  style="text-align: justify;text-indent: 40px">
                            Cada execução recebe um identificador único, que permite
                            relacionar o processamento principal às operações
                            auxiliares, aos eventos registrados, às métricas
                            calculadas e aos arquivos envolvidos. Esses registros
                            são armazenados em um banco de dados SQLite, formando
                            um histórico estruturado e consultável das atividades.
                        </p>

                        <h2>Importância para a auditoria do processo de fiscalização</h2>

                        <p  style="text-align: justify;text-indent: 40px">
                            O manifesto contribui para a
                            <strong>rastreabilidade, transparência e
                            reprodutibilidade dos procedimentos</strong>.
                            Ao registrar a sequência das operações e seus
                            resultados, permite identificar a origem de falhas,
                            examinar o comportamento das rotinas e verificar
                            quais etapas foram efetivamente executadas.
                            Também oferece subsídios para avaliar o desempenho
                            dos processos e documentar as evidências técnicas
                            que fundamentam as atividades de fiscalização.
                        </p>

                        <h2>Como funciona o registro das execuções?</h2>

                        <p  style="text-align: justify;text-indent: 40px">
                            O registro é iniciado juntamente com a rotina
                            monitorada e permanece associado ao processamento
                            até sua conclusão. Durante esse período, o sistema
                            pode armazenar acontecimentos relevantes, indicadores
                            quantitativos, referências a arquivos e informações
                            sobre as chamadas de funções auxiliares.
                            Ao término, são registrados o estado final da
                            execução e, quando aplicável, os detalhes de
                            eventuais falhas.
                        </p>

                        <div class="destaque">
                            <p  style="text-align: justify;text-indent: 40px">
                                <strong>Importante:</strong> a conclusão bem-sucedida
                                de uma execução não significa necessariamente
                                que todos os dados analisados foram aprovados.
                                O manifesto distingue o funcionamento técnico
                                do programa dos resultados das regras de validação.
                                Uma rotina pode ser concluída normalmente e,
                                ainda assim, identificar arquivos ou registros
                                com inconsistências.
                            </p>
                        </div>

                        <h2>Consulta e interpretação dos registros</h2>

                        <p  style="text-align: justify;text-indent: 40px">
                            As informações são organizadas em tabelas relacionadas
                            pelo identificador da execução. Essa estrutura permite
                            consultar tanto o histórico geral dos processamentos
                            quanto os detalhes de uma execução específica.
                            Nas abas a seguir, são apresentados os registros
                            disponíveis, acompanhados da descrição da finalidade
                            de cada tabela e dos respectivos dados armazenados.
                        </p>

                    </section>
                        """)
    try:
        with _conectar(database) as conn:
            existentes = _tabelas_existentes(conn)
            ids = []
            if "tbl_manifesto_execucao" in existentes:
                ids = [
                    row[0] for row in conn.execute(
                        'SELECT execucao_id FROM "tbl_manifesto_execucao" '
                        'ORDER BY iniciado_em DESC LIMIT 1000'
                    ).fetchall()
                ]
    except (OSError, sqlite3.Error) as exc:
        st.error(f"Não foi possível abrir o banco de auditoria: {exc}")
        return

    cols2 = st.columns([2,5,2], gap='small')
    with cols2[1]:
        with st.container() as borda1:
            st.html("""<h2 style='text-align: center;'>Resultados do Manifesto Eletrônico de Execuções</h2>
                        <p style="text-align: justify; text-indent: 40px; line-height: 1.65;">
                            Organizamos os registros de
                            rastreabilidade dos procedimentos computacionais em cinco categorias
                            complementares, apresentadas nas abas a seguir:
                            <strong>Execuções</strong>, que documenta a identificação, o período
                            de processamento e o estado final das rotinas;
                            <strong>Eventos</strong>, que registra os acontecimentos, avisos e
                            ocorrências relevantes;
                            <strong>Métricas</strong>, que reúne indicadores quantitativos
                            sobre o processamento;
                            <strong>Artefatos</strong>, que identifica os arquivos utilizados
                            ou produzidos; e <strong>Chamadas</strong>, que acompanha a execução
                            das funções auxiliares e seus respectivos resultados.
                            Cada aba representa, portanto, uma dimensão específica do manifesto,
                            permitindo consultar os registros de forma individualizada ou
                            correlacioná-los por meio do identificador único da execução.
                        </p>
                        """)
            cols3 = st.columns([2,4,2], gap='small')
            with cols3[1]:
                escolha = st.selectbox(
                                            "Filtrar por execução",
                                            options=["Todas as execuções", *ids],
                                            key="manifesto_filtro_execucao",
                                        )
                execucao_id = None if escolha == "Todas as execuções" else escolha
            
            abas = st.tabs(list(TABELAS))
            for aba, (rotulo, (tabela, titulo, objetivo)) in zip(abas, TABELAS.items()):
                with aba:
                    st.html(_descricao_html(titulo, objetivo, tabela))
                    if tabela not in existentes:
                        st.info("Esta tabela ainda não foi criada no banco selecionado.")
                        continue

                    try:
                        with _conectar(database) as conn:
                            colunas = _colunas(conn, tabela)
                            filtrar = execucao_id is not None and "execucao_id" in colunas
                            where = ' WHERE "execucao_id" = ?' if filtrar else ""
                            parametros = (execucao_id,) if filtrar else ()
                            total = conn.execute(
                                                    f'SELECT COUNT(*) FROM "{tabela}"{where}', parametros
                                                 ).fetchone()[0]

                            _, c1, _,  c2, _ = st.columns([1,2,1,2,1], gap='small')
                            with c1:
                                pagina_tam = st.selectbox(
                                                            "Linhas por página", [25, 50, 100, 250],
                                                            index=1, key=f"manifesto_tamanho_{tabela}"
                                                        )
                            total_paginas = max(1, (total + pagina_tam - 1) // pagina_tam)
                            with c2:
                                pagina = st.number_input(
                                                            "Página", min_value=1, max_value=total_paginas,
                                                            value=1, step=1, key=f"manifesto_pagina_{tabela}"
                                                        )

                            data_col = next(
                                                (c for c in ("criado_em", "iniciado_em") if c in colunas),
                                                None,
                                            )
                            ordem = f'"{data_col}" DESC' if data_col else "rowid DESC"
                            consulta = (
                                            f'SELECT * FROM "{tabela}"{where} ORDER BY {ordem} '
                                            "LIMIT ? OFFSET ?"
                                        )
                            df = pd.read_sql_query(
                                                        consulta, conn,
                                                        params=(*parametros, pagina_tam, (pagina - 1) * pagina_tam),
                                                    )

                        st.caption(f"{total:,} registro(s) encontrado(s).".replace(",", "."))
                        st.dataframe(df, hide_index=True)
                        st.download_button(
                                                "Exportar página em CSV",
                                                data=df.to_csv(index=False, sep="|").encode("latin-1"),
                                                file_name=f"{tabela}_pagina_{pagina}.csv",
                                                mime="text/csv",
                                                key=f"manifesto_exportar_{tabela}",
                                                disabled=df.empty,
                                            )
                        if "detalhes" in df.columns or "parametros" in df.columns:
                            st.caption("Campos JSON são exibidos como texto na grade.")
                    except (OSError, sqlite3.Error, pd.errors.DatabaseError) as exc:
                        st.error(f"Falha ao consultar {tabela}: {exc}")
```

</details>

---
