# Referência de Funções

## Índice

- [listar_arquivos_auditados](#funcao-1)
- [carregar_indice](#funcao-2)
- [_ind_visual_manifesto](#funcao-3)
- [visual_manifesto](#funcao-4)

---

<a id="funcao-1"></a>

## listar_arquivos_auditados

Lista os nomes de pastas que contêm o arquivo 'indice.json' dentro da pasta 'MANIFESTOS'.

A função percorre recursivamente a estrutura de diretórios a partir do caminho fornecido e retorna uma lista ordenada dos nomes das pastas que possuem um arquivo chamado 'indice.json' na subpasta 'MANIFESTOS'. Se o caminho fornecido não for um diretório, a função retorna uma lista vazia.

### Assinatura

```python
def listar_arquivos_auditados(raiz: Path) -> list[str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `raiz` | `Path` | Caminho do diretório raiz para iniciar a busca. |

### Retorno

**Tipo:** `list[str]`

Lista ordenada dos nomes das pastas que contêm o arquivo 'indice.json' na subpasta 'MANIFESTOS'.

### Dependências

- `os.path`

<details>
<summary>Visualizar código-fonte</summary>

```python
def listar_arquivos_auditados(raiz: Path) -> list[str]:
    if not raiz.is_dir():
        return []

    return sorted(
                        pasta.name
                        for pasta in raiz.iterdir()
                        if pasta.is_dir()
                        and (pasta / "MANIFESTOS" / "indice.json").is_file()
                    )
```

</details>

---

<a id="funcao-2"></a>

## carregar_indice

Carrega o índice JSON a partir de um caminho especificado.

Abre e lê um arquivo JSON localizado em um diretório específico, retornando seu conteúdo como um dicionário Python.

### Assinatura

```python
def carregar_indice(raiz: Path, id_arquivo: str) -> dict:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `raiz` | `Path` | Caminho raiz onde os arquivos estão localizados. |
| `id_arquivo` | `str` | Identificador do arquivo que contém o índice JSON. |

### Retorno

**Tipo:** `dict`

Conteúdo do arquivo JSON carregado como um dicionário Python.

### Dependências

- `json`

<details>
<summary>Visualizar código-fonte</summary>

```python
def carregar_indice(raiz: Path, id_arquivo: str) -> dict:
    caminho = raiz / id_arquivo / "MANIFESTOS" / "indice.json"

    with caminho.open("r", encoding="utf-8") as f:
        return json.load(f)
```

</details>

---

<a id="funcao-3"></a>

## _ind_visual_manifesto

Gera um manifesto de dados com base em um resultado de auditoria.

Esta função cria uma interface interativa utilizando a biblioteca Streamlit para exibir detalhes sobre alterações em um conjunto de dados. Ela verifica o status do resultado e, se houver alterações, apresenta informações sobre os registros incluídos, excluídos e alterados, além dos metadados.

### Assinatura

```python
def _ind_visual_manifesto(resultado: dict, raiz_auditoria: str | Path):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `resultado` | `dict` | Um dicionário contendo detalhes do resultado da auditoria, como status, versão, alterações de dados, etc. |
| `raiz_auditoria` | `str \| Path` | O caminho para a raiz onde os arquivos de relatório estão armazenados. |

### Dependências

- `{'nome': 'pandas', 'categoria': 'import'}`
- `{'nome': 'pathlib.Path', 'categoria': 'import'}`
- `{'nome': 'streamlit', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _ind_visual_manifesto(resultado: dict, raiz_auditoria: str | Path):
    if resultado["status"] == "sem_alteracao":
        st.info(
                    f"Arquivo já versionado: {resultado['versao']}. "
                    "SHA-256 idêntico ao da última versão."
                )
        return

    raiz = Path(raiz_auditoria) / resultado["tipo"]

    st.subheader("Manifesto de Dados")

    st.caption(
                    f"{resultado['tipo']} · {resultado['arquivo_origem']} · "
                    f"{resultado['versao']}"
                )

    if resultado["alteracao_dados"]:
        st.success("Nova versão com alterações de dados")
    else:
        st.info("Nova versão sem alterações de dados")

    resumo, alteracoes, metadados = st.tabs(
                                                ["Resumo", "Alterações", "Metadados"]
                                            )

    with resumo:
        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total de registros", resultado["total_registros"])
        c2.metric("Incluídos", resultado["incluidos"])
        c3.metric("Excluídos", resultado["excluidos"])
        c4.metric("Alterados", resultado["registros_alterados"])

        st.write("Versão anterior:", resultado["versao_anterior"])
        st.write("Campos alterados:", resultado["campos_alterados"])

        st.write("Colunas adicionadas:", resultado["colunas_adicionadas"])
        st.write("Colunas removidas:", resultado["colunas_removidas"])

    with alteracoes:
        relatorios = resultado["relatorios"]

        for titulo, nome in (
                                ("Registros incluídos", "incluidos"),
                                ("Registros excluídos", "excluidos"),
                                ("Campos alterados", "alterados"),
                            ):
            with st.expander(titulo):
                caminho = raiz / relatorios[nome]["caminho"]
                df = pd.read_parquet(caminho)

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )

    with metadados:
        st.json(resultado)

        st.code(
                    resultado["sha256_origem"],
                    language=None,
                )
```

</details>

---

<a id="funcao-4"></a>

## visual_manifesto

Visualiza o Manifesto Eletrônico de Dados em uma interface Streamlit.

Esta função carrega e exibe detalhes sobre o Manifesto Eletrônico de Dados, permitindo a consulta de versões específicas dos arquivos auditados. Utiliza um layout Streamlit para apresentar informações de forma organizada e interativa.

### Assinatura

```python
def visual_manifesto(raiz_auditoria: str | Path, st = None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `raiz_auditoria` | `str \| Path` | Caminho para a raiz do diretório onde os arquivos auditados estão armazenados. |
| `st` | `Streamlit` | Objeto Streamlit usado para criar a interface da web. Se não for fornecido, a função não realizará nenhuma operação de visualização. |

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def visual_manifesto(raiz_auditoria: str | Path, st = None):

    if not st:
        return

    # Estilo CSS consolidado
    RAIZ = Path(__file__).resolve().parent.parent
    with open(RAIZ / "tabelas/estilo_001.css") as f:
        css = f.read()
    st.html(f"<style>{css}</style>")

    with st.container():
        col1 = st.columns([1,5,1], gap='small')
        with col1[1]:
            st.html("""
                        <style>
                        .manifesto-ajuda {
                            font-family: inherit;
                            line-height: 1.65;
                            color: var(--text-color);
                        }

                        .manifesto-ajuda h3 {
                            font-size: 1.15rem;
                            font-weight: 650;
                            margin: 0 0 12px;
                        }

                        .manifesto-ajuda h4 {
                            font-size: 0.95rem;
                            font-weight: 650;
                            margin: 20px 0 8px;
                        }

                        .manifesto-ajuda p {
                            margin: 8px 0;
                            font-size: 0.92rem;
                        }

                        .manifesto-ajuda .destaque {
                            background: var(--secondary-background-color);
                            border-left: 3px solid #4F8DBD;
                            padding: 12px 16px;
                            border-radius: 5px;
                            margin: 14px 0;
                        }

                        .manifesto-ajuda table {
                            width: 100%;
                            border-collapse: collapse;
                            font-size: 0.88rem;
                            margin-top: 10px;
                        }

                        .manifesto-ajuda th,
                        .manifesto-ajuda td {
                            padding: 9px 12px;
                            text-align: left;
                            border-bottom: 1px solid rgba(128,128,128,0.25);
                        }

                        .manifesto-ajuda th {
                            background: var(--secondary-background-color);
                            font-weight: 600;
                        }

                        .manifesto-ajuda .observacao {
                            font-size: 0.85rem;
                            opacity: 0.8;
                            margin-top: 15px;
                        }
                        </style>

                        
                        <section>
                            <h1 style="text-align: center;">Visualização do Manifesto Eletrônico de Dados</h1>

                            <h2>O que é o Manifesto Eletrônico?</h2>

                            <p  style="text-align: justify;text-indent: 40px">
                                O <strong>Manifesto Eletrônico de Dados</strong> é um registro digital
                                que documenta o recebimento, a identificação, o versionamento e as
                                alterações dos arquivos utilizados no processo de fiscalização.
                                Sua finalidade é estabelecer um histórico dos dados
                                recebidos, permitindo identificar qual arquivo foi processado,
                                quando foi recebido, qual versão representa e quais alterações
                                ocorreram em relação à versão anterior.
                                Cada arquivo CSV é identificado por uma assinatura de integridade
                                denominada <strong>hash SHA-256</strong>. Quando essa assinatura
                                difere da última versão registrada, o sistema cria uma nova versão,
                                preservando uma cópia integral dos dados em formato Parquet,
                                acompanhada de um manifesto JSON e relatórios de comparação.
                            </p>

                            <h2>Importância para o processo de auditoria do processo de fiscalização</h2>

                            <p  style="text-align: justify;text-indent: 40px">
                                O manifesto eletrônico fortalece a confiabilidade dos procedimentos
                                de auditoria do processo de fiscalização por meio de cinco princípios:
                            </p>

                            <ul>
                                <li>
                                    <strong>Rastreabilidade:</strong> permite reconstruir o histórico
                                    dos arquivos recebidos e identificar as versões utilizadas
                                    em cada etapa do processamento.
                                </li>
                                <li>
                                    <strong>Integridade:</strong> utiliza hashes SHA-256 para detectar
                                    alterações nos arquivos e verificar a integridade das cópias
                                    armazenadas.
                                </li>
                                <li>
                                    <strong>Transparência:</strong> documenta inclusões, exclusões,
                                    modificações de registros e alterações na estrutura dos dados.
                                </li>
                                <li>
                                    <strong>Reprodutibilidade:</strong> preserva versões completas,
                                    permitindo repetir análises e investigar divergências.
                                </li>
                                <li>
                                    <strong>Evidência de fiscalização:</strong> produz registros
                                    estruturados que apoiam a documentação dos procedimentos
                                    e a fundamentação das conclusões do fiscal.
                                </li>
                            </ul>

                            <h2>O manifesto no fluxo de processamento</h2>

                            <p  style="text-align: justify;text-indent: 40px">
                                O manifesto é gerado <strong>antes da importação</strong>.
                                Essa sequência permite registrar as características do arquivo
                                recebido antes da execução das etapas seguintes.
                            </p>

                            <ol style="padding-left: 80px;padding-right: 50px;">
                                <li  style="text-align: justify;text-indent: 40px">
                                    <strong>Manifesto eletrônico:</strong> identifica o arquivo,
                                    verifica seu histórico, registra uma nova versão quando
                                    necessário e documenta as diferenças em relação à anterior.<br>
                                </li>
                                <li   style="text-align: justify;text-indent: 40px">
                                    <strong>Validação:</strong> verifica a conformidade dos dados
                                    com as regras de qualidade, consistência e estrutura estabelecidas.<br>
                                </li>
                                <li   style="text-align: justify;text-indent: 40px">
                                    <strong>Importação:</strong> incorpora os dados ao ambiente
                                    de destino conforme os critérios definidos no processo.<br>
                                </li>
                            </ol>

                            <h2>Como interpretar os resultados</h2>

                            <p  style="text-align: justify;text-indent: 40px">
                                Relevante distinguir <strong>alteração do arquivo</strong>
                                de <strong>alteração dos dados</strong>.
                                Uma nova versão é criada quando o hash SHA-256 do arquivo CSV
                                é diferente do registrado na última versão. Entretanto, essa
                                diferença pode resultar apenas de mudanças na representação
                                do arquivo, sem modificações efetivas nos registros.
                                Por isso, o manifesto apresenta separadamente os registros
                                incluídos, excluídos e alterados, a quantidade de campos
                                modificados e as mudanças na estrutura das colunas.
                                <strong>Uma nova versão não significa necessariamente que os dados
                                foram modificados ou aprovados.</strong> O manifesto documenta
                                o recebimento e o histórico do arquivo. A aprovação depende
                                da etapa de validação e dos resultados de processamento.
                            </p>

                            <h2>Contribuição para a confiabilidade da fiscalização</h2>

                            <p  style="text-align: justify;text-indent: 40px">
                                O Manifesto Eletrônico de Dados constitui um mecanismo de
                                <strong>controle, rastreabilidade e preservação de evidências
                                digitais</strong>.
                                Ao manter um histórico verificável das versões recebidas,
                                reduz o risco de utilização inadvertida de arquivos incorretos,
                                facilita a identificação de divergências e oferece suporte
                                para revisões, inspeções e reexecução dos procedimentos de auditoria do
                                processo de fiscalização.
                                Seu principal benefício é permitir que o fiscal não apenas
                                analise os dados disponíveis, mas também compreenda
                                <strong>sua origem, sua evolução e as evidências que sustentam
                                sua utilização</strong>.
                            </p>
                        </section>



                            <h2>Como interpretar o Manifesto de Dados</h2>

                            <p  style="text-align: justify;text-indent: 40px">
                                O manifesto registra o histórico das versões de um arquivo,
                                permitindo identificar quando uma nova versão foi recebida
                                e quais alterações ocorreram em seus dados.
                                O processamento acontece antes da etapa de importação, 
                                preservando uma cópia completa dos dados
                                recebidos em formato <strong>Parquet</strong>.
                            </p>

                            <h3 style="padding-left: 40px;">a) Regra de versionamento</h3>
                            <div class="destaque">
                                <p  style="text-align: justify;text-indent: 40px">
                                    Cada arquivo recebido é identificado por seu hash
                                    <strong>SHA-256</strong>. Se o hash for diferente do
                                    registrado na última versão, uma nova versão será criada,
                                    mesmo que os registros permaneçam iguais.
                                    Se o hash for idêntico, o arquivo será reconhecido
                                    como sem alteração e nenhuma nova versão será gerada.
                                </p>
                            </div>

                            <h3 style="padding-left: 40px;">b) Como ler os indicadores</h3>

                            <table>
                                <thead>
                                    <tr>
                                        <th>Indicador</th>
                                        <th>Significado</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Versão</td>
                                        <td>
                                            Identificador sequencial do arquivo recebido,
                                            como v0001, v0002 e v0003.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Total de registros</td>
                                        <td>
                                            Quantidade de registros existentes na versão atual.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Incluídos</td>
                                        <td>
                                            Registros cujos identificadores não existiam
                                            na versão anterior.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Excluídos</td>
                                        <td>
                                            Registros existentes na versão anterior que
                                            não aparecem na versão atual.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Registros alterados</td>
                                        <td>
                                            Quantidade de registros que tiveram pelo menos
                                            um campo modificado.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Campos alterados</td>
                                        <td>
                                            Quantidade total de valores modificados.
                                            Um mesmo registro pode apresentar várias alterações.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Colunas adicionadas ou removidas</td>
                                        <td>
                                            Mudanças na estrutura do arquivo em relação
                                            à versão anterior.
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <h3 style="padding-left: 40px;">c) Como interpretar os relatórios</h3>

                            <p  style="text-align: justify;text-indent: 40px">
                                <strong>Incluídos:</strong> apresenta os registros completos
                                encontrados apenas na versão atual.
                            </p>

                            <p  style="text-align: justify;text-indent: 40px">
                                <strong>Excluídos:</strong> apresenta os registros completos
                                que existiam apenas na versão anterior.
                            </p>

                            <p  style="text-align: justify;text-indent: 40px">
                                <strong>Alterados:</strong> apresenta o identificador do registro,
                                a coluna modificada, o valor anterior e o novo valor.
                                Cada linha representa a alteração de um campo.
                            </p>

                            <div class="destaque">
                                <p   style="text-align: justify;text-indent: 40px;margin-bottom: 2rem;"><strong>Importante: 
                                nova versão não significa alteração dos dados.</strong></p>
                                <p  style="text-align: justify;text-indent: 40px">
                                    Diferenças na ordem das linhas, na codificação ou na
                                    representação do CSV podem modificar seu SHA-256
                                    sem alterar os valores dos registros.
                                    Nesses casos, uma nova versão é criada, mas os indicadores
                                    de alteração podem permanecer zerados.
                                </p>
                            </div>

                            <h3 style="padding-left: 40px;">d) Rastreabilidade e integridade</h3>

                            <p  style="text-align: justify;text-indent: 40px">
                                Cada versão possui um snapshot completo em Parquet,
                                um manifesto JSON e relatórios de comparação.
                                Os hashes SHA-256 permitem verificar a integridade
                                dos arquivos registrados.
                                O manifesto documenta o recebimento e as diferenças entre versões.
                                Ele não representa a aprovação dos dados. A verificação de qualidade
                                e a autorização para importação são realizadas nas etapas seguintes
                                do processamento.
                            </p>


                        """)

            raiz = Path(raiz_auditoria).resolve()
            diretorios = listar_arquivos_auditados(raiz)
            col2 = st.columns([1,6,1], gap='small')
            with col2[1]:
                with st.container(border=True):
                    st.html("<h2>Consulta de Manifestos</h2>")
                    if not diretorios:
                        st.info("Nenhum manifesto foi encontrado.")
                        return
                    st.divider()
                    col3 = st.columns([1,6,1,6,1], gap='small')
                    with col3[1]:
                        id_arquivo = st.selectbox(
                                                    "Arquivo auditado",
                                                    options=diretorios,
                                                    key="manifesto_arquivo",
                                                )
                    indice = carregar_indice(raiz, id_arquivo)
                    versoes = indice.get("versoes", [])
                    if not versoes:
                        st.info("Este arquivo ainda não possui versões registradas.")
                        return
                    versoes = list(reversed(versoes))

                    with col3[3]:
                        versao_selecionada = st.selectbox(
                                                            "Versão do manifesto",
                                                            options=[item["versao"] for item in versoes],
                                                            key="manifesto_versao",
                                                        )

                    manifesto = next(
                                        item
                                        for item in versoes
                                        if item["versao"] == versao_selecionada
                                    )
                    
                    texto = f"""<p  style="text-align: justify;text-indent: 40px">Arquivo <b>{manifesto["arquivo_origem"]}</b>,"""
                    st.divider()
                    if manifesto["alteracao_dados"]:
                        st.html(texto + f""" <b>versão com alterações de dados</b> em relação ao anterior.</p>""")
                    else:
                        st.html(texto + f""" <b>versão sem alterações de dados</b> em relação ao anterior.</p>""")

                    c1, c2, c3, c4, c5, c6 = st.columns(6)

                    c2.metric("Total de registros", manifesto["total_registros"])
                    c3.metric("Incluídos", manifesto["incluidos"])
                    c4.metric("Excluídos", manifesto["excluidos"])
                    c5.metric("Alterados", manifesto["registros_alterados"])

                    st.divider()
                    aba_resumo, aba_comparacao, aba_json = st.tabs(
                                                                        ["Resumo", "Comparações", "Manifesto JSON"]
                                                                    )

                    with aba_resumo:
                        st.html(f"""<p  style="text-align: justify;text-indent: 40px">Versão anterior: {manifesto["versao_anterior"]}""")
                        st.html(f"""<p  style="text-align: justify;text-indent: 40px">Campos alterados: {manifesto["campos_alterados"]}""")
                        st.html(f"""<p  style="text-align: justify;text-indent: 40px">Colunas adicionadas: {manifesto["colunas_adicionadas"]}""")
                        st.html(f"""<p  style="text-align: justify;text-indent: 40px">Colunas removidas: {manifesto["colunas_removidas"]}""")

                    with aba_comparacao:
                        

                        relatorios = manifesto.get("relatorios", {})

                        for nome in ("incluidos", "excluidos", "alterados"):
                            relatorio = relatorios.get(nome)

                            if relatorio is None:
                                continue

                            caminho = raiz / id_arquivo / relatorio["caminho"]

                            with st.expander(nome.capitalize()):
                                if caminho.is_file():
                                    df = pd.read_parquet(caminho)
                                    st.dataframe(df, use_container_width=True)
                                else:
                                    st.warning(f"Relatório não encontrado: {nome}")

                    with aba_json:
                        st.json(manifesto)
                        st.html("Segue o HASH:")
                        st.code(
                                    manifesto.get("sha256_origem", {}),
                                    language=None,
                                )
```

</details>

---
