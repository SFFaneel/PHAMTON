# Referência de Funções

## Índice

- [sortear_amostra_bdgd](#funcao-1)
- [executar_vis](#funcao-2)
- [liberar_logger](#funcao-3)
- [bsc_dados_reg](#funcao-4)
- [configurar_logger](#funcao-5)
- [monitor_completo](#funcao-6)
- [calcular_n_hiper](#funcao-7)
- [inserir_tabelas_no_fluxo](#funcao-8)
- [gerar_id](#funcao-9)
- [salvar_binario](#funcao-10)
- [carregar_binario](#funcao-11)
- [json_para_html](#funcao-12)
- [criar_tab_html](#funcao-13)
- [elementos_para_json](#funcao-14)
- [mapear_secoes_por_pagina](#funcao-15)
- [encontrar_secao](#funcao-16)
- [inferir_nivel_titulo](#funcao-17)
- [vincular_tabelas](#funcao-18)
- [decidir_estrategia](#funcao-19)
- [pdf_tem_texto](#funcao-20)
- [extrair_tabelas](#funcao-21)
- [extrair_elementos](#funcao-22)
- [bsc_imagen_base64](#funcao-23)
- [determinar_tipo](#funcao-24)
- [converter_decimal](#funcao-25)
- [fmt_num](#funcao-26)
- [ajs_txt](#funcao-27)
- [resumo_por_tipo_mao_de_obra](#funcao-28)
- [resumo_por_fase](#funcao-29)
- [resumo_consolidado](#funcao-30)
- [obter_fatores](#funcao-31)
- [ajustar_data](#funcao-32)
- [determinar_tipo](#funcao-33)
- [converter_decimal](#funcao-34)
- [ler_metadados](#funcao-35)
- [marcar_outliers](#funcao-36)
- [gerar_resumo_contabil](#funcao-37)
- [formato_val](#funcao-38)
- [conciliar_tolerancia](#funcao-39)
- [bsc_dados2](#funcao-40)
- [bsc_dados_parquet](#funcao-41)
- [bsc_dados](#funcao-42)
- [ams_lcmto](#funcao-43)
- [vpl_regulatorio_com_depreciacao](#funcao-44)
- [breakeven_com_perda_vida_util](#funcao-45)
- [desenhar_grafo_hierarquico](#funcao-46)
- [bsc_dados_Cd_CC](#funcao-47)
- [comparar_componentes](#funcao-48)
- [_garante_dir_saida](#funcao-49)
- [_lognormal_mu_media](#funcao-50)
- [_std_seguro](#funcao-51)
- [df_dict_to_json](#funcao-52)
- [df_json_to_dict](#funcao-53)
- [salvar_df](#funcao-54)
- [carregar_df](#funcao-55)
- [consultar_empresa](#funcao-56)
- [decorador](#funcao-57)
- [get_tag](#funcao-58)
- [obter_fatores](#funcao-59)
- [ensure_cols](#funcao-60)
- [localizar_pipes_excedentes](#funcao-61)
- [testar_csv](#funcao-62)
- [ajustar_data](#funcao-63)
- [criar_layout_hierarquico](#funcao-64)
- [ajustar_data](#funcao-65)
- [con_str](#funcao-66)
- [wrapper](#funcao-67)
- [media_y_pais](#funcao-68)
- [try_parse](#funcao-69)
- [formatar_dms](#funcao-70)
- [dms_to_dd](#funcao-71)

---

<a id="funcao-1"></a>

## sortear_amostra_bdgd

Sorteia uma amostra de dados de um banco de dados DBF e salva em um arquivo CSV.

A função sorteia uma quantidade especificada de registros de diferentes tabelas do banco de dados DBF, utilizando uma semente para garantir a reproducibilidade. Os registros sorteados são salvos em um arquivo CSV com instruções de verificação.

### Assinatura

```python
# Consulte o código-fonte de sortear_amostra_bdgd
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `pasta_dbf` | `str` | Caminho para a pasta contendo os arquivos DBF. |
| `quantidade` | `int` | Quantidade de registros a serem sorteados por tabela. |
| `semente` | `int` | Semente para o gerador de números aleatórios, garantindo a reproducibilidade. |
| `arquivo_saida` | `str` | Nome do arquivo CSV onde os registros sorteados serão salvos. |

### Retorno

**Tipo:** `pandas.DataFrame`

DataFrame contendo a amostra de registros sorteados, com as colunas 'TABELA_BDGD' e 'COD_ID'.

### Exceções

- **`FileNotFoundError`**: Quando a pasta especificada não é encontrada.
- **`ValueError`**: Quando a quantidade de registros solicitados é menor que 1.

### Dependências

- `collections.defaultdict`
- `csv`
- `dbfread.DBF`
- `numpy`
- `pandas`
- `pathlib.Path`
- `re`
- `streamlit`

<details>
<summary>Visualizar código-fonte</summary>

```python
def sortear_amostra_bdgd(
                            pasta_dbf,
                            quantidade=5,
                            semente=20251028,
                            arquivo_saida="amostra_extracao_bdgd.csv"
                        ):
    
    from dbfread import DBF
    from collections import defaultdict
    import re

    pasta = Path(pasta_dbf.replace("BDGD_ANLS","BDGD_AT"))
    
    if not pasta.is_dir():
        raise FileNotFoundError(f"Pasta não encontrada: {pasta}")

    if quantidade < 1:
        raise ValueError("A quantidade deve ser maior que zero.")

    lst_DBF = ['EQME','EQRE','EQCR','EQSE','EQTRAT','EQTRMT','EQTRM','PONNOT','SEGCON','RAMLIG','SSDAT','SSDMT','SSDBT']
    arquivos = defaultdict(list)

    for arq in pasta.rglob("*"):
        if arq.is_file() and arq.suffix.lower() == ".dbf":
            nome = arq.stem.upper()
            tabela = re.sub(r"_\d+$", "", nome)
            if tabela in lst_DBF:
                arquivos[tabela].append(arq)

    rng = np.random.default_rng(semente)
    amostras = []
    a = st.empty()
    for tabela in dict.fromkeys(str(t).strip().upper() for t in lst_DBF):
        a.info(f"Sorteando {tabela}")
        caminhos = sorted(arquivos.get(tabela, []))
        if not caminhos:
            st.warning(f"Nenhum arquivo DBF encontrado para {tabela}")
            continue
        codigos = set()

        for caminho in caminhos:
            a.info(f"Sorteando {tabela}: {caminho}")
            dbf = DBF(str(caminho), load=False, char_decode_errors="replace")
            if "COD_ID" not in dbf.field_names:
                st.warning(f"Campo COD_ID não encontrado em {caminho.name}")
                continue
            for registro in dbf:
                codigo = registro["COD_ID"]
                if codigo is not None and str(codigo).strip():
                    codigos.add(str(codigo).strip())
        
        if not codigos:
            st.warning(f"Nenhum COD_ID válido em {tabela}")
            continue

        codigos = sorted(codigos)
        total = len(dbf)
        n = min(quantidade, total)
        sorteados = rng.choice(codigos, size=n, replace=False)
        amostras.extend(
                            {
                                "TABELA_BDGD": tabela,
                                "COD_ID": str(codigo)
                            }
                            for codigo in sorteados
                        )
    a.empty()
    df_amostra = pd.DataFrame(amostras, columns=["TABELA_BDGD", "COD_ID"])

    if not df_amostra.empty:

        df_amostra = df_amostra.sort_values(["TABELA_BDGD", "COD_ID"]).reset_index(drop=True)
        pasta = Path(pasta_dbf.replace("BDGD_ANLS",""))
        import csv
        with open(pasta / arquivo_saida, mode="w", newline="\n", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="|")
            writer.writerow(["TABELA_BDGD", "COD_ID"])

            for registro in amostras:
                writer.writerow([registro["TABELA_BDGD"],registro["COD_ID"]])

            writer.writerow([])
            writer.writerow([])
            writer.writerow(["INSTRUÇÕES PARA VERIFICAÇÃO DA EXTRAÇÃO BDGD"])
            writer.writerow([
                                "Objetivo",
                                "Avaliar a fidelidade dos dados extraídos dos sistemas de origem "
                                "e apresentados nos arquivos DBF da BDGD."
                            ])

            writer.writerow([
                                "Orientação geral",
                                "Não será conferido todos os campos de cada equipamento. "
                                "Será selecionado de 3 a 5 atributos relevantes por tabela."
                            ])

            writer.writerow([])
            writer.writerow(["VERIFICAÇÃO", "OBJETIVO"])

            instrucoes = [
                            (
                                "Identificador do registro",
                                "Confirmar a correspondência entre o COD_ID do DBF "
                                "e o registro no sistema de origem."
                            ),
                            (
                                "Atributo técnico principal",
                                "Verificar a fidelidade do dado técnico extraído."
                            ),
                            (
                                "Relacionamento",
                                "Conferir a associação com instalação, circuito "
                                "ou outro elemento cadastral."
                            ),
                            (
                                "Situação cadastral",
                                "Verificar se o registro deveria constar na extração, "
                                "considerando sua situação na data de referência."
                            ),
                            (
                                "Campo complementar",
                                "Avaliar o preenchimento e eventuais transformações "
                                "dos dados durante a extração."
                            )
                        ]

            writer.writerows(instrucoes)

            writer.writerow([])
            writer.writerow(["VERIFICAÇÃO DO UNIVERSO DA EXTRAÇÃO"])

            writer.writerow([
                                "Quantidade de registros",
                                "Conferir a quantidade de registros extraídos por tabela "
                                "com o universo definido na consulta de origem."
                            ])

            writer.writerow([
                                "Filtros aplicados",
                                "Verificar os critérios de seleção e exclusão utilizados "
                                "na rotina de extração."
                            ])

            writer.writerow([
                                "Data de referência",
                                "Confirmar a data-base dos dados extraídos e sua "
                                "compatibilidade com a consulta ao sistema."
                            ])

            writer.writerow([])
            writer.writerow([
                                "OBSERVAÇÃO",
                                "A conferência dos registros sorteados não permite identificar, "
                                "isoladamente, equipamentos que deveriam ter sido extraídos "
                                "e foram omitidos. Por isso, também verificaremos "
                                "o universo da extração, os filtros e a data de referência."
                            ])

    return df_amostra
```

</details>

---

<a id="funcao-2"></a>

## executar_vis

Executa uma função e captura quaisquer exceções que possam ocorrer.

A função `executar_vis` executa a função fornecida (`funcao`) com os argumentos posicionais (`*args`) e nomeados (`**kwargs`). Se ocorrer uma exceção, ela é capturada e um erro é exibido no Streamlit com detalhes do erro.

### Assinatura

```python
def executar_vis(funcao, *args, **kwargs):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `funcao` | `Não especificado` | Função a ser executada. |
| `args` | `Não especificado` | Argumentos posicionais para a função. |
| `kwargs` | `Não especificado` | Argumentos nomeados para a função. |

### Retorno

**Tipo:** `Não especificado`

O resultado da execução da função ou `None` se ocorrer uma exceção.

### Dependências

- `{'nome': 'streamlit', 'categoria': 'imports', 'descricao': 'Biblioteca utilizada para exibir mensagens de erro no Streamlit.'}`
- `{'nome': 'traceback', 'categoria': 'imports', 'descricao': 'Módulo utilizado para capturar e formatar a pilha de chamadas em caso de exceção.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def executar_vis(funcao, *args, **kwargs):
    try:
        return funcao(*args, **kwargs)
    except Exception as e:
        nome_funcao = funcao.__name__

        st.error(f"Erro na função {nome_funcao}: {e}")
        with st.expander(f"Detalhes do erro - {nome_funcao}"):
            st.code(traceback.format_exc(), language="python")

        return None
```

</details>

---

<a id="funcao-3"></a>

## liberar_logger

Libera os loggers que estão associados a um diretório específico.

Remove todos os handlers de arquivo (FileHandler) dos loggers que têm como base o diretório fornecido ou qualquer subdiretório. Também remove um logger específico armazenado na sessão do Streamlit se ele for uma instância de Logger.

### Assinatura

```python
def liberar_logger(diretorio: Path) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `diretorio` | `Path` | Diretório para o qual os loggers associados serão removidos. |

### Retorno

**Tipo:** `None`

Nenhum valor é retornado.

### Dependências

- `logging`
- `pathlib.Path`
- `streamlit`

<details>
<summary>Visualizar código-fonte</summary>

```python
def liberar_logger(diretorio: Path) -> None:
    diretorio = diretorio.resolve()
    loggers = [logging.getLogger()]
    for obj in logging.Logger.manager.loggerDict.values():
        if isinstance(obj, logging.Logger):
            loggers.append(obj)
    for logger in loggers:
        for handler in logger.handlers[:]:
            if not isinstance(handler, logging.FileHandler):
                continue
            arquivo = Path(handler.baseFilename).resolve()
            if arquivo == diretorio or diretorio in arquivo.parents:
                logger.removeHandler(handler)
                handler.flush()
                handler.close()
    if "LOGGER" in st.session_state:
        logger_sessao = st.session_state.LOGGER
        if isinstance(logger_sessao, logging.Logger):
            st.session_state.pop("LOGGER", None)
```

</details>

---

<a id="funcao-4"></a>

## bsc_dados_reg

Lê dados regulatórios a partir de arquivos CSV ou CSS.

A função lê dados regulatórios a partir de arquivos CSV ou CSS com base no tipo especificado. Se o nome da tabela não for fornecido, um aviso será emitido. O padrão é ler uma tabela CSV.

### Assinatura

```python
def bsc_dados_reg(nome=None, tipo='Tabela'):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `nome` | `Não especificado` | Nome do arquivo a ser lido (sem extensão). |
| `tipo` | `Não especificado` | Tipo de dado a ser lido ('Tabela' ou 'Estilo_CSS'). O padrão é 'Tabela'. |

### Retorno

**Tipo:** `Não especificado`

Conteúdo do arquivo lido, que pode ser uma tabela CSV ou um estilo CSS.

### Exceções

- **`UserWarning`**: Quando o nome da tabela não é fornecido.
- **`UserWarning`**: Quando o tipo especificado não é implementado ('Tabela' ou 'Estilo_CSS').

### Dependências

- `{'nome': 'pandas', 'categoria': 'imports', 'descricao': 'Biblioteca utilizada para ler arquivos CSV.'}`
- `{'nome': 'UserWarning', 'categoria': 'chamadas', 'descricao': 'Classe usada para emitir avisos.'}`
- `{'nome': 'f.read', 'categoria': 'chamadas', 'descricao': 'Método usado para ler o conteúdo de um arquivo CSS.'}`
- `{'nome': 'open', 'categoria': 'chamadas', 'descricao': 'Função usada para abrir arquivos.'}`
- `{'nome': 'pd.read_csv', 'categoria': 'chamadas', 'descricao': 'Método usado para ler arquivos CSV com pandas.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def bsc_dados_reg(nome=None, tipo='Tabela'):
    if not nome:
        raise UserWarning("Deve ser informado o nome da tabela regulatória!")
    if tipo=='Tabela':
        return pd.read_csv(rf'tabelas\{nome}.csv', sep="|", encoding="Latin-1", dtype=str)
    elif tipo == 'Estilo_CSS':
        with open(rf"tabelas/{nome}.css") as f:
            return f.read()
    else:
        raise UserWarning(f"Tipo ({tipo}) não implementado!")
```

</details>

---

<a id="funcao-5"></a>

## configurar_logger

Configura um logger para registrar mensagens de log em arquivo e console.

Esta função configura um logger que registra as mensagens de log em dois locais: um arquivo de log específico e a saída padrão do console. O nome do arquivo de log é gerado com base no nome fornecido e na data atual, o diretório onde os logs serão armazenados pode ser especificado, e o nível de log pode ser ajustado.

### Assinatura

```python
# Consulte o código-fonte de configurar_logger
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `nome_arquivo` | `Não especificado` | Nome do arquivo de log. O valor padrão é 'PHANTO_FANG'. |
| `diretorio_logs` | `Não especificado` | Diretório onde os logs serão armazenados. O valor padrão é 'logs'. |
| `nivel` | `Não especificado` | Nível de log a ser registrado. O valor padrão é `logging.INFO`. |

### Retorno

**Tipo:** `Não especificado`

Logger configurado e pronto para uso.

### Dependências

- `datetime.datetime`
- `logging`
- `os`

<details>
<summary>Visualizar código-fonte</summary>

```python
def configurar_logger(
                        nome_arquivo="PHANTO_FANG",
                        diretorio_logs="logs",
                        nivel=logging.INFO
                    ):


    os.makedirs(diretorio_logs, exist_ok=True)
    caminho_log = os.path.join(diretorio_logs, f"{nome_arquivo}_{datetime.now():%Y%m%d}.log")
    logging.captureWarnings(True)
    logger = logging.getLogger()
    logger.setLevel(nivel)
    formatacao = logging.Formatter(
                                        '%(asctime)s [%(levelname)s] %(message)s',
                                        datefmt='%Y-%m-%d %H:%M:%S'
                                    )

    arquivo_handler = logging.FileHandler(caminho_log, encoding="utf-8")
    arquivo_handler.setFormatter(formatacao)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatacao)
    logger.addHandler(arquivo_handler)
    logger.addHandler(console_handler)

    return logger
```

</details>

---

<a id="funcao-6"></a>

## monitor_completo

Decorator para monitorar a execução de funções, registrando informações de sucesso ou erro.

O decorator `monitor_completo` registra o tempo de execução e o caminho do arquivo que chamou a função. Em caso de sucesso, ele informa o tempo gasto; em caso de erro, ele registra o tempo gasto e detalhes do erro.

### Assinatura

```python
def monitor_completo(logger):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `logger` | `Não especificado` | Objeto de logger utilizado para registrar informações de sucesso ou erro. |

### Retorno

**Tipo:** `Não especificado`

Decorator que retorna uma função decorada com a funcionalidade de monitoramento.

### Dependências

- `{'nome': 'functools.wraps', 'categoria': 'import', 'descricao': 'Utilizado para preservar informações da função original após a aplicação do decorator.'}`
- `{'nome': 'inspect', 'categoria': 'import', 'descricao': 'Utilizado para obter informações sobre o chamador da função.'}`
- `{'nome': 'os', 'categoria': 'import', 'descricao': 'Utilizado para manipular caminhos de arquivo.'}`
- `{'nome': 'time', 'categoria': 'import', 'descricao': 'Utilizado para medir o tempo de execução da função.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def monitor_completo(logger):

    def decorador(funcao):
        @wraps(funcao)
        def wrapper(*args, **kwargs):
            inicio = time.perf_counter()
            stack = inspect.stack()
            caller_frame = stack[1]
            caminho_arquivo = caller_frame.filename
            nome_arquivo = os.path.basename(caminho_arquivo)
            try:
                resultado = funcao(*args, **kwargs)
                duracao = time.perf_counter() - inicio
                logger.info(f"SUCESSO em '{funcao.__name__}', chamado por {nome_arquivo}: {duracao:.4f}s")    
                return resultado
            except Exception as e:
                duracao = time.perf_counter() - inicio
                logger.error(f"ERRO em '{funcao.__name__}' após {duracao:.4f}s | Detalhe: {e}")
                raise e       
        return wrapper
    return decorador
```

</details>

---

<a id="funcao-7"></a>

## calcular_n_hiper

Calcula o tamanho mínimo de uma amostra para garantir um certo nível de confiança e margem de erro em um teste hipotético.

Esta função utiliza a distribuição hipergeométrica para determinar o tamanho mínimo da amostra necessária, com base no número total de itens na população (N), na taxa de erro tolerável e no nível de confiança desejado. A função retorna o tamanho da amostra calculado.

### Assinatura

```python
def calcular_n_hiper(N, taxa_erro_toleravel = 0.05, confianca=0.95):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `N` | `Não especificado` | Número total de itens na população. |
| `taxa_erro_toleravel` | `Não especificado` | Margem de erro aceitável para o teste hipotético. |
| `confianca` | `Não especificado` | Nível de confiança desejado para a amostra. |

### Retorno

**Tipo:** `Não especificado`

Tamanho mínimo da amostra necessária para atender aos critérios de confiança e margem de erro especificados.

### Dependências

- `scipy.stats.hypergeom`

<details>
<summary>Visualizar código-fonte</summary>

```python
def calcular_n_hiper(N, taxa_erro_toleravel = 0.05, confianca=0.95):
    alpha = 1 - confianca
    K = max(1, int(N * taxa_erro_toleravel))
    
    for n in range(1, N + 1):
        if hypergeom.pmf(0, N, K, n) <= alpha:
            return n
    return N
```

</details>

---

<a id="funcao-8"></a>

## inserir_tabelas_no_fluxo

Insere tabelas em um documento de acordo com o tipo especificado.

A função insere tabelas em um documento, podendo ser feito por seção e página ou apenas por página. Ela manipula a estrutura do documento para adicionar as tabelas na posição correta.

### Assinatura

```python
def inserir_tabelas_no_fluxo(doc: dict, tipo = "nPos", st = None) -> dict:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `doc` | `dict` | O documento onde as tabelas serão inseridas. |
| `tipo` | `Não especificado` | O tipo de inserção a ser realizado. Pode ser 'nPos' para inserir por seção e página ou outro valor para inserir apenas por página. |
| `st` | `Não especificado` | Parâmetro não utilizado no código fornecido. |

### Retorno

**Tipo:** `dict`

O documento com as tabelas inseridas.

### Dependências

- `{'nome': 'collections.defaultdict', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def inserir_tabelas_no_fluxo(doc: dict, tipo = "nPos", st = None) -> dict:
    tabelas = doc.get("tabelas", {})
    if tipo == "nPos":
        t_por_sec_pag = defaultdict(list)
        for tid, t in tabelas.items():
            sec = t.get("secao")
            pag = t.get("pagina")
            if sec and pag:
                t_por_sec_pag[(sec, pag)].append((tid, t))

        for sec in doc.get("secao", []):
            titulo = sec["titulo"]
            conteudo = sec.get("conteudo", [])
            
            prim_idx_pag = {}
            for idx, blc in enumerate(conteudo):
                p = blc.get("pagina")
                if p and p not in prim_idx_pag:
                    prim_idx_pag[p] = idx

            insercao = []
            for (sec_tit, pag), tabelas_lista in t_por_sec_pag.items():
                if sec_tit != titulo:
                    continue
                tabelas_lista = sorted(tabelas_lista, key=lambda x: x[0])
                pos = prim_idx_pag.get(pag, len(conteudo))
                offset = 0
                for tid, t in tabelas_lista:
                    insercao.append((
                                        pos + offset,
                                        {
                                            "tipo": "tabela",
                                            "tabela_id": tid,
                                            "pagina": pag,
                                            "linhas": t.get("linhas") or t.get("data")
                                        }
                                    ))
                    offset += 1

            for pos, blc in sorted(insercao, key=lambda x: x[0]):
                conteudo.insert(pos, blc)

            sec["conteudo"] = conteudo
    else:
        it = 1
        for secao in doc["secao"]:
            conteudo = secao["conteudo"]
            novos_blocos = []

            for blc in conteudo:
                agr = True
                for nm, tabela in tabelas.items():
                    if tabela["pagina"] != blc["pagina"]:
                        continue              
                    if blc.get("y_inf") and (blc["y_inf"] > tabela["y_sup"]):
                        if not tabela.get("_inserida"): 
                            novos_blocos.append({
                                                    "tipo": "tabela",
                                                    "pagina": tabela["pagina"],
                                                    "linhas": tabela.get("linhas") or tabela.get("data")
                                                })
                            tabela["_inserida"] = True
                        novos_blocos.append(blc)
                        agr = False
                    elif blc.get("y_inf") and (blc["y_inf"] < tabela["y_sup"]):
                        novos_blocos.append(blc)
                        agr = False
                        if not tabela.get("_inserida"):
                            novos_blocos.append({
                                                    "tipo": "tabela",
                                                    "pagina": tabela["pagina"],
                                                    "linhas": tabela.get("linhas") or tabela.get("data")
                                                })
                            tabela["_inserida"] = True     
                if agr:
                    novos_blocos.append(blc)
                        
            for nm, tabela in tabelas.items():
                if not tabela.get("_inserida") and tabela["pagina"] == secao["pagina"]:
                    novos_blocos.append({
                                            "tipo": "tabela",
                                            "pagina": tabela["pagina"],
                                            "linhas": tabela.get("rows") or tabela.get("data")
                                        })
                    tabela["_inserida"] = True

            secao["conteudo"] = novos_blocos

    return doc
```

</details>

---

<a id="funcao-9"></a>

## gerar_id

Gera um identificador a partir de um texto, removendo caracteres especiais e normalizando.

A função remove caracteres especiais, espaços em branco e substitui alguns símbolos por outros. Se o resultado for vazio ou começar com um dígito, adiciona um prefixo padrão.

### Assinatura

```python
def gerar_id(texto, prefixo="sec"):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `texto` | `Não especificado` | Texto original a partir do qual será gerado o identificador. |
| `prefixo` | `Não especificado` | Prefixo adicionado ao início do identificador se necessário. |

### Retorno

**Tipo:** `Não especificado`

Identificador gerado a partir do texto fornecido.

### Dependências

- `re`
- `unicodedata`

<details>
<summary>Visualizar código-fonte</summary>

```python
def gerar_id(texto, prefixo="sec"):
    texto = ''.join(char for char in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(char))
    texto = texto.replace("\t", " ")
    texto = re.sub(r"\(-\)", "_red_", texto)
    texto = re.sub(r"&", "_", texto)
    texto = re.sub(r"\/", "_", texto)
    texto = re.sub(r",", "_e_", texto)
    texto = re.sub(r"[.\s]+", "-", texto)
    texto = re.sub(r"-{2,}", "-", texto)
    texto = texto.lower()
    if not texto or texto[0].isdigit():
        texto = f"{prefixo}-{texto}"
    return texto
```

</details>

---

<a id="funcao-10"></a>

## salvar_binario

Salva um objeto Python em um arquivo binário gzip.

Serializa um objeto Python e o salva em um arquivo binário utilizando a biblioteca pickle, com compressão gzip.

### Assinatura

```python
def salvar_binario(obj, path):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `obj` | `Não especificado` | Objeto Python que será serializado e salvo. |
| `path` | `Não especificado` | Caminho do arquivo onde o objeto será salvo. |

### Dependências

- `gzip`
- `pickle`

<details>
<summary>Visualizar código-fonte</summary>

```python
def salvar_binario(obj, path):
    with gzip.open(path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
```

</details>

---

<a id="funcao-11"></a>

## carregar_binario

Carrega um objeto Python serializado em formato binário.

Abre um arquivo no modo de leitura binária e carrega o conteúdo serializado utilizando a biblioteca pickle.

### Assinatura

```python
def carregar_binario(path):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `path` | `Não especificado` | Caminho do arquivo binário a ser carregado. |

### Retorno

**Tipo:** `Não especificado`

Objeto Python deserializado do arquivo binário.

### Dependências

- `gzip`
- `pickle`

<details>
<summary>Visualizar código-fonte</summary>

```python
def carregar_binario(path):
    with gzip.open(path, "rb") as f:
        return pickle.load(f)
```

</details>

---

<a id="funcao-12"></a>

## json_para_html

Converte um documento JSON em HTML.

Transforma uma estrutura de documento JSON em código HTML, gerando seções, títulos, parágrafos, listas e tabelas. O resultado é uma string contendo o código HTML completo.

### Assinatura

```python
def json_para_html(doc, st=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `doc` | `Não especificado` | Estrutura JSON representando o documento a ser convertido. |
| `st` | `Não especificado` | Parâmetro não utilizado no código fornecido. Pode ser ignorado. |

### Retorno

**Tipo:** `Não especificado`

String contendo o código HTML gerado a partir do documento JSON.

### Dependências

- `{'nome': 'criar_tab_html', 'categoria': 'chamada'}`
- `{'nome': 'gerar_id', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def json_para_html(doc, st=None):
    html = []
    for secao in doc["secao"]:
        olflag = False
        id = gerar_id(secao["titulo"])
        html.append(f"""<section class="main-section" id="{id}">""")
        html.append(f"<h{secao['nivel']}>{secao['titulo']}</h{secao['nivel']}>")

        for item in secao["conteudo"]:
            if item["tipo"] == "paragrafo":
                if olflag:
                    olflag = False
                    html.append(f"""</ul>""")
                html.append(f"<p>{item['texto']}</p>")

            elif item["tipo"] == "lista_item":
                if not olflag:
                    olflag = True
                    html.append(f"""<ul>""")
                html.append(f"<li>{item['texto']}</li>")

            elif item["tipo"] == "imagem_ocr":
                if olflag:
                    olflag = False
                    html.append(f"""</ul>""")
                html.append(f"<p class='ocr'>{item['texto']}</p>")

            elif item["tipo"] == "tabela":
                if olflag:
                    olflag = False
                    html.append(f"""</ul>""")
                html.append(criar_tab_html(item["linhas"]))
        html.append(f"""</section>""")
    
    html_saida = """
                    <!--Baseado num modelo fornecido durante o curso da freecode.org-->\n
                    <!DOCTYPE html>\n
                    <html lang="pt-pt">\n
                    \t<head>
                    \t\t<link rel="stylesheet" type="text/css" href="MCPSE.css">\n
                    \t</head>\n
                    <main>\n
                    <body>\n
                """
    html_saida += "\n".join(html)
    html_saida += """
                        </main>\n
                        </body>\n
                        <script>\n
                        document.querySelectorAll('.nav-link').forEach(anchor => {\n
                            anchor.addEventListener('click', function (e) {\n
                                const targetId = this.getAttribute('href');\n
                                if (targetId.startsWith('#')) {\n
                                    e.preventDefault();\n
                                    const targetElement = document.querySelector(targetId);\n
                                    if (targetElement) {\n
                                        targetElement.scrollIntoView({ behavior: 'smooth' });\n
                                    }\n
                                }\n
                            });\n
                        });\n
                        </script>\n
                        </html>
                    """
    return html_saida
```

</details>

---

<a id="funcao-13"></a>

## criar_tab_html

Cria uma tabela HTML a partir de uma lista de linhas.

Gera um código HTML representando uma tabela, onde cada linha da lista é convertida em uma linha da tabela. A primeira linha é tratada como cabeçalho (thead), e as demais linhas como corpo (tbody). Valores nulos são substituídos por strings vazias e caracteres especiais são escapados.

### Assinatura

```python
def criar_tab_html(linhas):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `linhas` | `Não especificado` | Lista de listas, onde cada sublista representa uma linha da tabela. |

### Retorno

**Tipo:** `Não especificado`

Código HTML representando a tabela.

### Dependências

- `html`

<details>
<summary>Visualizar código-fonte</summary>

```python
def criar_tab_html(linhas):
    if not linhas:
        return "<!-- tabela vazia -->"
    saida = ["<div>"]
    saida.append("""<table class="tabela-dados">""")
    saida.append("<thead>")
    for r_i, linha in enumerate(linhas):
        saida.append("<tr>")
        for celula in linha:
            cel_txt = "" if celula is None else str(celula)
            cel_txt = htmllib.escape(cel_txt)
            tag = "th" if r_i == 0 else "td"
            saida.append(f"<{tag}>{cel_txt}</{tag}>")
        saida.append("</tr>")
        if r_i == 0:
            saida.append("</thead>")
            saida.append("<tbody>")
    saida.append("</tbody>")
    saida.append("</table>")
    saida.append("</div>")
    return "\n".join(saida)
```

</details>

---

<a id="funcao-14"></a>

## elementos_para_json

Converte uma lista de elementos em um formato JSON estruturado.

A função percorre uma lista de elementos e organiza informações relevantes em uma estrutura JSON. Ela filtra elementos vazios ou sem coordenadas, cria seções para títulos e adiciona conteúdo como parágrafos, itens de lista e imagens OCR a essas seções.

### Assinatura

```python
def elementos_para_json(elementos):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `elementos` | `Não especificado` | Lista de elementos que serão convertidos em JSON. |

### Retorno

**Tipo:** `Não especificado`

Estrutura JSON contendo as seções e conteúdo organizado.

### Dependências

- `{'nome': 'append', 'categoria': 'método', 'descricao': 'Método usado para adicionar elementos a uma lista.'}`
- `{'nome': 'el.text.strip', 'categoria': 'método', 'descricao': 'Método que remove espaços em branco do início e fim de uma string.'}`
- `{'nome': 'inferir_nivel_titulo', 'categoria': 'função', 'descricao': 'Função que infere o nível de um título com base no texto.'}`
- `{'nome': 'isinstance', 'categoria': 'método', 'descricao': 'Método usado para verificar se um objeto é uma instância de uma classe específica.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def elementos_para_json(elementos):
    doc = {"secao": []}
    secao_atual = None

    for el in elementos:
        if not el.text or not el.metadata or not el.metadata.coordinates:
            continue

        coord = el.metadata.coordinates.points
        sup_esq     = coord[0] # (x1, y1)
        sup_dir    = coord[1] # (x2, y2)
        inf_dir = coord[2] # (x3, y3)
        inf_esq  = coord[3] # (x4, y4)

        x1, y1 = sup_esq
        x2, y2 = sup_dir
        x3, y3 = inf_dir
        x4, y4 = inf_esq

        if isinstance(el, (Header, Footer)):
            continue

        if isinstance(el, Title):
            secao_atual = {
                                "titulo": el.text.strip(),
                                "nivel": inferir_nivel_titulo(el.text),
                                "pagina": el.metadata.page_number,
                                "conteudo": [],
                                "y_sup": y1,
                                "y_inf": y2,
                                "x_esq": x1,
                                "x_dir": x2
                            }
            doc["secao"].append(secao_atual)

        elif secao_atual:
            if isinstance(el, NarrativeText):
                secao_atual["conteudo"].append({
                                                    "tipo": "paragrafo",
                                                    "texto": el.text.strip(),
                                                    "pagina": el.metadata.page_number,
                                                    "y_sup": y1,
                                                    "y_inf": y2,
                                                    "x_esq": x1,
                                                    "x_dir": x2
                                                })

            elif isinstance(el, ListItem):
                secao_atual["conteudo"].append({
                                                    "tipo": "lista_item",
                                                    "texto": el.text.strip(),
                                                    "pagina": el.metadata.page_number,
                                                    "y_sup": y1,
                                                    "y_inf": y2,
                                                    "x_esq": x1,
                                                    "x_dir": x2
                                                })

            elif isinstance(el, Image) and el.text:
                secao_atual["conteudo"].append({
                                                    "tipo": "imagem_ocr",
                                                    "texto": el.text.strip(),
                                                    "pagina": el.metadata.page_number,
                                                    "y_sup": y1,
                                                    "y_inf": y2,
                                                    "x_esq": x1,
                                                    "x_dir": x2
                                                })

    return doc
```

</details>

---

<a id="funcao-15"></a>

## mapear_secoes_por_pagina

Mapeia títulos de seções por páginas em um documento.

Itera sobre as seções do documento e cria um dicionário onde as chaves são os números das páginas e os valores são listas de títulos de seções presentes nessas páginas. Se uma página não tiver nenhuma seção, ela ainda será incluída no dicionário com uma lista vazia.

### Assinatura

```python
def mapear_secoes_por_pagina(doc):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `doc` | `Não especificado` | Um objeto representando o documento, que deve conter uma chave 'secao' contendo uma lista de dicionários com as chaves 'pagina' e 'titulo'. |

### Retorno

**Tipo:** `Não especificado`

Um dicionário onde as chaves são números de página e os valores são listas de títulos de seções.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def mapear_secoes_por_pagina(doc):
    mapa = {}
    for s in doc["secao"]:
        mapa.setdefault(s["pagina"], []).append(s["titulo"])
    return mapa
```

</details>

---

<a id="funcao-16"></a>

## encontrar_secao

Encontra a seção mais recente em um mapa de páginas.

Itera sobre as páginas do mapa em ordem decrescente, retornando a seção associada à primeira página encontrada no mapa. Caso nenhuma página seja encontrada, retorna `None`.

### Assinatura

```python
def encontrar_secao(pagina, mapa):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `pagina` | `Não especificado` | Página inicial para a busca. |
| `mapa` | `Não especificado` | Dicionário onde as chaves são números de página e os valores são listas de seções. |

### Retorno

**Tipo:** `Não especificado`

Seção mais recente encontrada ou `None` se nenhuma página for encontrada no mapa.

### Dependências

- `range`

<details>
<summary>Visualizar código-fonte</summary>

```python
def encontrar_secao(pagina, mapa):
    for p in range(pagina, 0, -1):
        if p in mapa:
            return mapa[p][-1]
    return None
```

</details>

---

<a id="funcao-17"></a>

## inferir_nivel_titulo

Infere o nível de um título com base em sua estrutura numérica.

A função analisa o título para determinar seu nível, onde o nível é inferido pela presença de números decimais. Se não houver números decimais, assume-se que o nível seja 1. O nível máximo pode ser especificado através do parâmetro `max_nivel`.

### Assinatura

```python
def inferir_nivel_titulo(titulo: str, max_nivel=6) -> int:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `titulo` | `str` | Título a ser analisado para inferir o nível. |
| `max_nivel` | `Não especificado` | Nível máximo permitido. O valor padrão é 6. |

### Retorno

**Tipo:** `int`

Nível inferido do título, limitado pelo `max_nivel`.

### Dependências

- `re`

<details>
<summary>Visualizar código-fonte</summary>

```python
def inferir_nivel_titulo(titulo: str, max_nivel=6) -> int:
    m = re.match(r"^(\d+(?:\.\d+)*)", titulo)
    if not m:
        return 1

    nivel = m.group(1).count(".") + 1
    return min(nivel, max_nivel)
```

</details>

---

<a id="funcao-18"></a>

## vincular_tabelas

Vincula tabelas a seções em um documento.

A função vincula cada tabela em uma lista a uma seção específica do documento, utilizando um mapa de seções por página. As tabelas são atribuídas IDs únicas e associadas às suas respectivas seções. O resultado é um documento com as tabelas vinculadas.

### Assinatura

```python
def vincular_tabelas(doc, tabelas):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `doc` | `Não especificado` | O documento que contém as tabelas a serem vinculadas. |
| `tabelas` | `Não especificado` | Uma lista de tabelas a serem vinculadas ao documento. |

### Retorno

**Tipo:** `Não especificado`

O documento com as tabelas vinculadas.

### Dependências

- `{'nome': 'mapear_secoes_por_pagina', 'categoria': 'chamada', 'descricao': 'Função que cria um mapa de seções por página no documento.'}`
- `{'nome': 'encontrar_secao', 'categoria': 'chamada', 'descricao': 'Função que encontra a seção associada à página de uma tabela.'}`
- `{'nome': 'enumerate', 'categoria': 'chamada', 'descricao': 'Função utilizada para enumerar as tabelas, atribuindo IDs únicas.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def vincular_tabelas(doc, tabelas):
    mapa = mapear_secoes_por_pagina(doc)

    for i, tabela in enumerate(tabelas, start=1):
        tabela["id"] = f"tabela_{i:03d}"
        tabela["secao"] = encontrar_secao(tabela["pagina"], mapa)

    doc["tabelas"] = {t["id"]: t for t in tabelas}
    return doc
```

</details>

---

<a id="funcao-19"></a>

## decidir_estrategia

Decide a estratégia com base nas informações fornecidas.

A função verifica se há texto, texto ruim ou tabela na informação e retorna 'hi_res' se qualquer uma dessas condições for verdadeira. Caso contrário, retorna 'fast'.

### Assinatura

```python
def decidir_estrategia(info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `info` | `Não especificado` | Informações que incluem a presença de texto, texto ruim e tabela. |

### Retorno

**Tipo:** `Não especificado`

Estratégia decidida ('hi_res' ou 'fast').

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def decidir_estrategia(info):
    if not info["tem_texto"] or info["texto_ruim"] or info["tem_tabela"]:
        return "hi_res"
    return "fast"
```

</details>

---

<a id="funcao-20"></a>

## pdf_tem_texto

Verifica se um PDF contém texto e tabelas, e aplica uma estratégia baseada nesses critérios.

A função verifica se o PDF tem mais de 300 caracteres em suas primeiras páginas. Se não tiver, retorna True. Caso contrário, analisa a proporção de letras e símbolos para determinar se o texto é considerado 'ruim'. Também verifica se há tabelas nas primeiras páginas do PDF. A estratégia final é decidida pela função `decidir_estrategia`.

### Assinatura

```python
def pdf_tem_texto(arq, min_caracts=500, max_pag=5):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `arq` | `Não especificado` | Caminho para o arquivo PDF a ser analisado. |
| `min_caracts` | `Não especificado` | Número mínimo de caracteres em texto para considerar que o PDF tem texto (padrão é 500). |
| `max_pag` | `Não especificado` | Número máximo de páginas a serem analisadas para verificar o conteúdo do PDF (padrão é 5). |

### Retorno

**Tipo:** `Não especificado`

Resultado da estratégia decidida pela função `decidir_estrategia`, que pode variar dependendo dos critérios de texto e tabelas.

### Dependências

- `{'nome': 'pdfplumber', 'tipo': None, 'categoria': 'externa', 'descricao': 'Biblioteca utilizada para extrair tabelas do PDF.'}`
- `{'nome': 'pypdf', 'tipo': None, 'categoria': 'externa', 'descricao': 'Biblioteca utilizada para ler o conteúdo do PDF.'}`
- `{'nome': 're', 'tipo': None, 'categoria': 'built-in', 'descricao': 'Módulo padrão do Python para operações de expressões regulares.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def pdf_tem_texto(arq, min_caracts=500, max_pag=5):

    info = {
                "tem_texto": False,
                "texto_ruim": False,
                "tem_tabela": False
            }

    reader = pypdf.PdfReader(arq)
    texto = ""
    for page in reader.pages[:5]:
        texto += page.extract_text() or ""

    texto = texto.strip()
    info["tem_texto"] = len(texto) > 300

    if len(texto) < min_caracts:
        return True

    if info["tem_texto"]:
        letras = len(re.findall(r"[A-Za-zÀ-ÿ]", texto))
        simbolos = len(re.findall(r"[^A-Za-zÀ-ÿ\s]", texto))
        info["texto_ruim"] = simbolos / max(letras + simbolos, 1) > 0.4

    with pdfplumber.open(arq) as pdf:
        for page in pdf.pages[:max_pag]:
            if page.extract_tables():
                info["tem_tabela"] = True
                break

    return decidir_estrategia(info), info
```

</details>

---

<a id="funcao-21"></a>

## extrair_tabelas

Extrai tabelas de um arquivo PDF.

A função lê um arquivo PDF e extrai todas as tabelas presentes, retornando uma lista de dicionários com informações sobre cada tabela, incluindo a página em que ela se encontra, os dados da tabela, e as coordenadas y-superior e y-inferior.

### Assinatura

```python
def extrair_tabelas(arq, st = None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `arq` | `Não especificado` | Caminho para o arquivo PDF que será lido. |
| `st` | `Não especificado` | Parâmetro não utilizado na função. Deve ser None. |

### Retorno

**Tipo:** `Não especificado`

Lista de dicionários, onde cada dicionário representa uma tabela extraída do PDF e contém as seguintes chaves: 'pagina', 'data', 'y_sup' e 'y_inf'.

### Dependências

- `pdfplumber`

<details>
<summary>Visualizar código-fonte</summary>

```python
def extrair_tabelas(arq, st = None):
    tabelas = []

    with pdfplumber.open(arq) as pdf:
        tabelas = []
        for i, page in enumerate(pdf.pages):
            for tabela in page.find_tables():
                linhas = tabela.extract()
                tabelas.append({
                                "pagina": i + 1,
                                "data": linhas,
                                "y_sup": tabela.bbox[1],
                                "y_inf": tabela.bbox[3],
                              })
    return tabelas
```

</details>

---

<a id="funcao-22"></a>

## extrair_elementos

Extrai elementos de um arquivo PDF usando uma estratégia específica.

Esta função utiliza a biblioteca `unstructured` para extrair elementos de um arquivo PDF. A estratégia pode ser 'Fast' ou outra definida, e os resultados incluem quebras de página.

### Assinatura

```python
def extrair_elementos(arq, estrategia = 'Fast'):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `arq` | `Não especificado` | Arquivo PDF a ser processado. |
| `estrategia` | `Não especificado` | Estratégia utilizada para extrair elementos do PDF. Pode ser 'Fast' ou outra definida. |

### Retorno

**Tipo:** `Não especificado`

Resultados da extração de elementos do PDF, que podem incluir texto e quebras de página.

### Dependências

- `{'nome': 'unstructured.partition.pdf.partition_pdf', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def extrair_elementos(arq, estrategia = 'Fast'):
    return partition_pdf(
                            filename=str(arq),
                            strategy=estrategia,
                            include_page_breaks=True,
                            url=None
                        )
```

</details>

---

<a id="funcao-23"></a>

## bsc_imagen_base64

Converte uma imagem em formato base64.

Lê o conteúdo de um arquivo de imagem e o codifica em base64 para facilitar a transmissão ou armazenamento em formatos que não suportam binários diretamente.

### Assinatura

```python
def bsc_imagen_base64(path):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `path` | `Não especificado` | Caminho do arquivo de imagem que será convertido. |

### Retorno

**Tipo:** `Não especificado`

Representação base64 da imagem.

### Dependências

- `base64`

<details>
<summary>Visualizar código-fonte</summary>

```python
def bsc_imagen_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
```

</details>

---

<a id="funcao-24"></a>

## determinar_tipo

Determina o tipo de dado com base na primeira parte da string.

A função verifica se a coluna começa com 'VL', 'PCT' ou 'QTD' para classificar como 'float'. Se contiver 'DT', é classificado como 'date'. Caso contrário, retorna 'str'.

### Assinatura

```python
def determinar_tipo(coluna):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `coluna` | `Não especificado` | A string a ser analisada para determinar o tipo de dado. |

### Retorno

**Tipo:** `Não especificado`

O tipo de dado ('float', 'date' ou 'str') inferido da coluna.

### Dependências

- `coluna.upper`
- `upper`

<details>
<summary>Visualizar código-fonte</summary>

```python
def determinar_tipo(coluna):
    if "VL" == coluna[0:2].upper() or "PCT" == coluna[0:3].upper() or "QTD" == coluna[0:3].upper():
        return 'float'
    elif "DT" in coluna.upper():
        return 'date'
    else:
        return 'str'
```

</details>

---

<a id="funcao-25"></a>

## converter_decimal

Converte um valor decimal representado como string de ponto e vírgula em um número float.

A função aceita tanto pontos quanto vírgulas como separadores decimais. Se o valor for uma string, ele será convertido para float após a substituição dos caracteres. Caso contrário, o valor original é retornado sem alterações.

### Assinatura

```python
def converter_decimal(valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `Não especificado` | Valor decimal representado como string de ponto e vírgula. |

### Retorno

**Tipo:** `Não especificado`

Número float convertido ou valor original se não for uma string.

### Dependências

- `float`
- `isinstance`
- `replace`

<details>
<summary>Visualizar código-fonte</summary>

```python
def converter_decimal(valor):
    return float(valor.replace('.','').replace(',', '.')) if isinstance(valor, str) and ',' in valor else valor
```

</details>

---

<a id="funcao-26"></a>

## fmt_num

Formata um número, substituindo vírgula por underline e ponto por vírgula.

A função formata um número, substituindo vírgula por underline e ponto por vírgula. Se o valor for `None` ou um número não finito (NaN ou Inf), retorna 'N/A'.

### Assinatura

```python
def fmt_num(x, dec=2):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `x` | `Não especificado` | O número a ser formatado. |
| `dec` | `Não especificado` | Número de casas decimais para formatação. O padrão é 2. |

### Retorno

**Tipo:** `Não especificado`

O número formatado como uma string, ou 'N/A' se o valor for inválido.

### Dependências

- `numpy`

<details>
<summary>Visualizar código-fonte</summary>

```python
def fmt_num(x, dec=2):
    if x is None or (isinstance(x, float) and (np.isnan(x) or np.isinf(x))):
        return "N/A"
    return f"{x:,.{dec}f}".replace(",", "_").replace(".", ",").replace("_", ".")
```

</details>

---

<a id="funcao-27"></a>

## ajs_txt

Substitui certas tags e estilos em um texto.

A função substitui tags HTML específicas e estilos de justificativa por padrões alternativos. As alterações incluem a remoção de estilos de alinhamento e indentação, bem como a substituição de tags `<p>` por `<p1>`. A função aceita um texto opcional como parâmetro.

### Assinatura

```python
def ajs_txt(texto=""):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `texto` | `Não especificado` | Texto que será alterado. Se não for fornecido, o valor padrão é uma string vazia. |

### Retorno

**Tipo:** `Não especificado`

Texto alterado conforme as regras especificadas.

### Dependências

- `{'nome': 'dic_subs.items', 'categoria': 'chamada', 'descricao': 'Itera sobre os itens do dicionário de substituições.'}`
- `{'nome': 'texto_alter.replace', 'categoria': 'chamada', 'descricao': 'Substitui as ocorrências das chaves no texto por seus respectivos valores.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def ajs_txt(texto=""):
    dic_subs = {
                        "  style='text-align: justify;text-indent: 40px'": "",
                        '  style="text-align: justify;text-indent: 40px"': "",
                        "<p>": "<p1>",
                        "</p>": "</p1>",
                        "<b>": "",
                        "</b>": ""
                    }

    texto_alter = texto
    for vh, nv in dic_subs.items():
        texto_alter = texto_alter.replace(vh, nv)
    return texto_alter
```

</details>

---

<a id="funcao-28"></a>

## resumo_por_tipo_mao_de_obra

Gera um resumo por tipo de mão de obra com base em um DataFrame.

A função processa um DataFrame para calcular a quantidade de ocorrências, valor total e distribuição por fase para dois tipos específicos de mão de obra (MOP e ST).

### Assinatura

```python
def resumo_por_tipo_mao_de_obra(df):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `Não especificado` | DataFrame contendo os dados a serem processados. |

### Retorno

**Tipo:** `Não especificado`

Dicionário com resumos para cada tipo de mão de obra (MOP e ST), incluindo quantidade de ocorrências, valor total e distribuição por fase.

### Dependências

- `len`
- `sum`
- `to_dict`

<details>
<summary>Visualizar código-fonte</summary>

```python
def resumo_por_tipo_mao_de_obra(df):
    fases = ['VL_FRT_TRN', 'VL_PRJ', 'VL_GER', 'VL_FISC', 'VL_MONT', 'VL_SUP']
    retorno = {}
    for tipo, nome in [(3, 'MOP'), (4, 'ST')]:
        subset = df[df['Cd_NG'] == tipo]
        retorno[nome] = {
            'Qtd_OCOR': len(subset),
            'VL_TOT': subset[fases].sum().sum(),
            'VL_Fase': subset[fases].sum().to_dict()
        }
    return retorno
```

</details>

---

<a id="funcao-29"></a>

## resumo_por_fase

Gera um resumo agregado por fase a partir de um DataFrame.

A função calcula a soma dos valores para cada fase especificada e retorna os resultados em um dicionário.

### Assinatura

```python
def resumo_por_fase(df):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `Não especificado` | DataFrame contendo as colunas 'VL_FRT_TRN', 'VL_PRJ', 'VL_GER', 'VL_FISC', 'VL_MONT' e 'VL_SUP'. |

### Retorno

**Tipo:** `Não especificado`

Dicionário com a soma dos valores para cada fase.

### Dependências

- `sum`
- `to_dict`

<details>
<summary>Visualizar código-fonte</summary>

```python
def resumo_por_fase(df):
    fases = ['VL_FRT_TRN', 'VL_PRJ', 'VL_GER', 'VL_FISC', 'VL_MONT', 'VL_SUP']
    return df[fases].sum().to_dict()
```

</details>

---

<a id="funcao-30"></a>

## resumo_consolidado

Gera um resumo consolidado de valores financeiros a partir de um DataFrame.

A função calcula o total geral, o total próprio e o total de terceiros com base em colunas específicas do DataFrame fornecido. Utiliza filtros para distinguir entre diferentes categorias de valores (VL_FRT_TRN, VL_PRJ, VL_GER, VL_FISC, VL_MONT, VL_SUP).

### Assinatura

```python
def resumo_consolidado(df):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `Não especificado` | DataFrame contendo as colunas 'VL_FRT_TRN', 'VL_PRJ', 'VL_GER', 'VL_FISC', 'VL_MONT', 'VL_SUP' e a coluna 'Cd_NG'. |

### Retorno

**Tipo:** `Não especificado`

Um dicionário contendo os totais consolidados: 'VL_CA_TOT' (total geral), 'VL_CA_MOP' (total próprio) e 'VL_CA_ST' (total de terceiros).

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def resumo_consolidado(df):
    fases = ['VL_FRT_TRN', 'VL_PRJ', 'VL_GER', 'VL_FISC', 'VL_MONT', 'VL_SUP']  
    total_geral = df[fases].sum().sum()
    total_propria = df[df['Cd_NG'] == 3][fases].sum().sum()
    total_terceiros = df[df['Cd_NG'] == 4][fases].sum().sum()
    return {
                'VL_CA_TOT': total_geral,
                'VL_CA_MOP': total_propria,
                'VL_CA_ST': total_terceiros
            }
```

</details>

---

<a id="funcao-31"></a>

## obter_fatores

Obtém fatores de cálculo com base em códigos específicos.

Determina os fatores de multiplicação e sinal para um determinado código de natureza (COD_NAT) e código de conta (COD_CTA). Os valores retornados são usados em cálculos financeiros ou contábeis.

### Assinatura

```python
def obter_fatores(COD_NAT, COD_CTA):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `COD_NAT` | `Não especificado` | Código de natureza que determina a regra de fatores. |
| `COD_CTA` | `Não especificado` | Código da conta que pode influenciar o resultado dos fatores, dependendo do código de natureza. |

### Retorno

**Tipo:** `Não especificado`

Quatro valores: dois fatores de multiplicação e um sinal ('D' para débito ou 'C' para crédito).

### Dependências

- `{'nome': 'COD_CTA.startswith', 'tipo': None, 'categoria': 'chamada', 'descricao': 'Método usado para verificar se o código da conta começa com um determinado caractere.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def obter_fatores(COD_NAT, COD_CTA):
    if COD_NAT == '01':
        return -1, -1, 1, 'D'
    elif COD_NAT in ['02', '03']:
        return 1, -1, 1, 'C'
    elif COD_NAT == '04':
        return (-1, -1, 1, 'D') if COD_CTA.startswith('7') else (1, -1, 1, 'C')
    elif COD_NAT == '05':
        return (-1, -1, 1, 'D') if COD_CTA.startswith('5') else (1, -1, 1, 'C')
    return 1, 1, 1, 'C'
```

</details>

---

<a id="funcao-32"></a>

## ajustar_data

Ajusta uma data para o primeiro dia do mês.

Recebe uma string representando uma data e retorna a mesma data ajustada para o primeiro dia do mês correspondente. A função suporta datas no formato 'DD/MM/YYYY' e 'YYYY-MM-DD'.

### Assinatura

```python
def ajustar_data(data_str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `data_str` | `Não especificado` | String representando a data no formato 'DD/MM/YYYY' ou 'YYYY-MM-DD'. |

### Retorno

**Tipo:** `Não especificado`

Data ajustada para o primeiro dia do mês, no formato 'YYYY/MM/01'.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def ajustar_data(data_str):
    data_str = str(data_str)
    if "/" in data_str:
        partes = data_str.split("/")
    elif "-" in data_str:
        partes = data_str.split("-")
    ano = partes[0]
    mes = partes[1].zfill(2)
    return f"{ano}/{mes}/01"
```

</details>

---

<a id="funcao-33"></a>

## determinar_tipo

Determina o tipo de dado com base na primeira parte da string.

A função verifica se a coluna começa com 'VL', 'PCT' ou 'QTD' para classificar como 'float'. Se contiver 'DT', é classificado como 'date'. Caso contrário, retorna 'str'.

### Assinatura

```python
def determinar_tipo(coluna):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `coluna` | `Não especificado` | A string a ser analisada para determinar o tipo de dado. |

### Retorno

**Tipo:** `Não especificado`

O tipo de dado ('float', 'date' ou 'str') inferido da coluna.

### Dependências

- `coluna.upper`
- `upper`

<details>
<summary>Visualizar código-fonte</summary>

```python
def determinar_tipo(coluna):
    if "VL" == coluna[0:2].upper() or "PCT" == coluna[0:3].upper() or "QTD" == coluna[0:3].upper():
        return 'float'
    elif "DT" in coluna.upper():
        return 'date'
    else:
        return 'str'
```

</details>

---

<a id="funcao-34"></a>

## converter_decimal

Converte um valor de string representando um número decimal em um tipo float.

A função tenta converter uma string que representa um número decimal em um valor do tipo float. Se o valor não for uma string, é retornado como está. A função também lida com notações científicas e substitui vírgulas por pontos para conversões de números decimais.

### Assinatura

```python
def converter_decimal(valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `Não especificado` | Valor a ser convertido. Se não for uma string, é retornado como está. |

### Retorno

**Tipo:** `Não especificado`

Valor convertido para float ou None se o valor não pode ser convertido.

### Exceções

- **`ValueError`**: Lançada internamente pela função `float()` quando o valor não é um número válido.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def converter_decimal(valor):
    if not isinstance(valor, str):
        return valor
    valor = valor.strip()

    if not valor:
        return None

    try:
        if "e" in valor.lower():
            return float(valor)

        if "," in valor:
            return float(valor.replace(".", "").replace(",", "."))

        return float(valor)

    except ValueError:
        return None
```

</details>

---

<a id="funcao-35"></a>

## ler_metadados

Lê metadados de imagens JPEG, HEIC e processa informações geográficas.

A função lê metadados de imagens no formato JPEG e HEIC em um diretório especificado. Ela extrai informações como latitude, longitude, data de criação, software utilizado e verifica indícios de qualidade dos dados. Os resultados são armazenados em DataFrames e salvos em arquivos CSV e banco de dados SQL.

### Assinatura

```python
def ler_metadados(caminho_arquivo, bd, st=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `caminho_arquivo` | `Não especificado` | Caminho do diretório contendo as imagens a serem processadas. |
| `bd` | `Não especificado` | Conexão com o banco de dados onde os resultados serão armazenados. |
| `st` | `Não especificado` | Objeto Streamlit para atualização de progresso. Se None, não há atualização do progresso. |

### Retorno

**Tipo:** `tuple[int]`

Quantidade de imagens processadas e indícios encontrados.

### Dependências

- `{'nome': 'imports', 'itens': ['exifread', 'geopandas', 'numpy', 'os', 'pandas', 'streamlit']}`
- `{'nome': 'chamadas', 'itens': ['any', 'arquivo.lower', 'astype', 'between', 'df.drop_duplicates', 'df.merge', 'df.sort_values', 'df.to_csv', 'df.to_sql', 'df1.to_csv', 'df1.to_sql', 'dms_to_dd', 'dt.total_seconds', 'endswith', 'enumerate', 'exifread.process_file', 'fillna', 'float', 'formatar_dms', 'get_tag', 'gpd.GeoDataFrame', 'gpd.points_from_xy', 'gpd.read_file', 'gpd.sjoin', 'gpd.sjoin_nearest', 'gt', 'indicios.append', 'int', 'len', 'notna', 'np.arcsin', 'np.clip', 'np.cos', 'np.radians', 'np.sin', 'np.sqrt', 'np.where', 'open', 'os.path.getsize', 'os.path.isfile', 'os.path.join', 'os.walk', 'pd.DataFrame', 'pd.to_datetime', 'pd.to_numeric', 'pontos.to_crs', 'printable.lower', 'progresso.empty', 'progresso.progress', 'reset_index', 'resultados.append', 'round', 'shift', 'st.progress', 'str.contains', 'sum']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def ler_metadados(caminho_arquivo, bd, st=None):
    def get_tag(nome, default=None):
        return tags[nome].printable if nome in tags else default
    
    resultados = []
    indicios = []
    total = sum(1 for _ in os.walk(caminho_arquivo))
    if st: progresso = st.progress(0, text="Processando arquivos...")

    for i, (root, dirs, files) in enumerate(os.walk(caminho_arquivo), start=1):
        progresso.progress(i / total, text=f"Processando diretório {root}, {i}/{total}")
        for arquivo in files:
            if arquivo.lower().endswith((".jpg", ".jpeg", ".heic")):
                caminho = os.path.join(root, arquivo)
                tamanho = os.path.getsize(caminho)
                if tamanho == 0:
                    indicios.append({
                                        "arquivo": arquivo,
                                        "indicio_1": "Arquivo está corrompido, reenviar.",
                                        "indicio_2": "",
                                        "indicio_3": "",
                                        "caminho" : caminho,
                                    })
                    continue

                with open(caminho, "rb") as img_file:
                    tags = exifread.process_file(img_file, details=False)

                    def formatar_dms(dms, ref):
                        graus = float(dms[0].num) / float(dms[0].den)
                        minutos = float(dms[1].num) / float(dms[1].den)
                        segundos = float(dms[2].num) / float(dms[2].den)
                        return f"{int(graus)}°{int(minutos)}'{segundos:.2f}\"{ref}"

                    def dms_to_dd(dms, ref):
                        deg, min_, sec = [float(x.num) / float(x.den) for x in dms]
                        dd = deg + min_ / 60 + sec / 3600
                        if ref in ["S", "W"]:
                            dd *= -1
                        return dd
                        
                    lat_ref = get_tag("GPS GPSLatitudeRef", "Sem metadados de latitude.") 
                    lat = tags["GPS GPSLatitude"].values if "GPS GPSLatitude" in tags else "Sem metados de latitude."
                    lon_ref =  get_tag("GPS GPSLongitudeRef", "Sem metadados de longitude.")
                    lon = tags["GPS GPSLongitude"].values if "GPS GPSLongitude" in tags else "Sem metados de longitude."
                
                    if lat_ref != "Sem metadados de latitude.":
                        lat_dms_str = formatar_dms(lat, lat_ref)
                        lon_dms_str = formatar_dms(lon, lon_ref)
                        lat = dms_to_dd(lat, lat_ref)
                        lon = dms_to_dd(lon, lon_ref)
                    else:
                        lat_dms_str = ""
                        lon_dms_str = ""

                    data = {}
                    for tag in ["EXIF DateTimeOriginal", "Image DateTime", "EXIF DateTimeDigitized", "Image Software"]:
                        data[tag] = get_tag(tag, f"Sem metadados {tag}.")
                            
                    resultados.append({
                                            "arquivo": arquivo,
                                            "latitude": lat,
                                            "longitude": lon,
                                            "lat_dms" : lat_dms_str,
                                            "lon_dms" : lon_dms_str,
                                            "caminho" : caminho,
                                            "data_original": data["EXIF DateTimeOriginal"],
                                            "data_digitizacao": data["EXIF DateTimeDigitized"],
                                            "data_modificacao": data["Image DateTime"],
                                            "software": data['Image Software']
                                        })
                    #print(f"O arquivo {caminho_arquivo}/{arquivo} possui latitude {lat:.2f}, longitude {lon:.2f}, data {data}.")
                
                    IND1 = "SEM DADOS"
                    IND2 = "SEM DADOS"
                    IND3 = "SEM DADOS"
                    if "EXIF DateTimeOriginal" in tags and "Image DateTime" in tags:
                        if tags["EXIF DateTimeOriginal"].printable != tags["Image DateTime"].printable:
                            IND1 = "Datas divergentes"
                        else:
                            IND1 = "Datas convergentes"

                    if "Image Software" in tags:
                        sw = tags["Image Software"].printable.lower()
                        if any(app in sw for app in ["photoshop", "lightroom", "snapseed", "vsco"]):
                            IND2 = f"Software de edição detectado: {sw}"
                        else:
                            IND2 = f"""Software {tags["Image Software"].printable}."""

                    if "Image Make" not in tags or "Image Model" not in tags:
                        IND3 = "Marca/Modelo ausentes"
                    else:
                        IND3 = f"""Marca {tags["Image Make"].printable}, modelo {tags["Image Model"].printable}."""

                    indicios.append({
                                        "arquivo": arquivo,
                                        "indicio_1": IND1,
                                        "indicio_2": IND2,
                                        "indicio_3": IND3,
                                        "caminho" : caminho,
                                    })
        progresso.empty()
                    
    df = pd.DataFrame(resultados)
    df1 = df[~df["longitude"].str.contains("Sem metados", na=False)]
    df1["longitude1"] = pd.to_numeric(df1["longitude"], errors='coerce')
    df1["latitude1"] = pd.to_numeric(df1["latitude"], errors='coerce')

    if st and (len(df1)>0):
        
        pontos = gpd.GeoDataFrame(
                                    df1,
                                    geometry=gpd.points_from_xy(
                                        df1["longitude1"],
                                        df1["latitude1"]
                                    ),
                                    crs="EPSG:4326"
                                )
        dir_bdgd = os.path.join(f"{st.session_state.tra_dir}/BDGD_AT/CONSOL","SUB.dbf")
        if os.path.isfile(dir_bdgd):
            poligonos = gpd.read_file(dir_bdgd)
            pontos = pontos.to_crs(poligonos.crs)
            res_001 = gpd.sjoin(
                                    pontos,
                                    poligonos,
                                    how="left",
                                    predicate="within"
                                 )
            res_001["FLG_IND_SE"] = res_001["index_right"].notna()
            df = df.merge(res_001[["longitude","latitude","NOME","FLG_IND_SE"]], how='left', on=["longitude","latitude"])
        dir_bdgd = os.path.join(f"{st.session_state.tra_dir}/BDGD_AT/CONSOL","PONNOT.dbf")
        if os.path.isfile(dir_bdgd):
            ponnot = gpd.read_file(dir_bdgd)
            df1 = df[
                        (~df["longitude"].str.contains("Sem metados", na=False)) &
                        (df["FLG_IND_SE"]==0)
                    ]
            df1["longitude1"] = pd.to_numeric(df1["longitude"], errors='coerce')
            df1["latitude1"] = pd.to_numeric(df1["latitude"], errors='coerce')
            pontos = gpd.GeoDataFrame(
                                        df1,
                                        geometry=gpd.points_from_xy(
                                            df1["longitude1"],
                                            df1["latitude1"]
                                        ),
                                        crs="EPSG:4326"
                                     )
            pontos = pontos.to_crs(poligonos.crs)
            res_002 = gpd.sjoin_nearest(
                                    pontos,
                                    ponnot, 
                                    how="left",
                                    max_distance=10,
                                    distance_col="distancia_m"
                                )
            res_002["FLG_IND_PONNOT"] = res_002["distancia_m"].notna()
            df = df.merge(res_002[["longitude","latitude","COD_ID","TIP_INST","POS","SITCONT","distancia_m","FLG_IND_PONNOT"]], how='left', on=["longitude","latitude"])

        df["Dt_REF"] = pd.to_datetime(
                                            df['data_original'],
                                            format="%Y:%m:%d %H:%M:%S",
                                            errors="coerce"
                                        )
        df = df.sort_values("Dt_REF").reset_index(drop=True)
        df["longitude1"] = pd.to_numeric(df["longitude"], errors='coerce').fillna(0)
        df["latitude1"] = pd.to_numeric(df["latitude"], errors='coerce').fillna(0)
        df["latitude_anterior"] = df["latitude1"].shift()
        df["longitude_anterior"] = df["longitude1"].shift()
        df["data_anterior"] = df["Dt_REF"].shift()

        df["intervalo_s"] = (
                                df["Dt_REF"] - df["data_anterior"]
                            ).dt.total_seconds()
        df["intervalo_min"] = df["intervalo_s"] / 60
        mesmo_dia = (
                        df["Dt_REF"].dt.date
                        == df["data_anterior"].dt.date
                    )

        coordenadas_validas = (
                                df["latitude1"].between(-90, 90)
                                    & df["latitude_anterior"].between(-90, 90)
                                    & df["longitude1"].between(-180, 180)
                                    & df["longitude_anterior"].between(-180, 180)
                                )

        intervalo_valido = df["intervalo_s"] > 0

        calcular = mesmo_dia & coordenadas_validas & intervalo_valido
        raio_terra = 6_371_008.8

        lat1 = np.radians(df["latitude_anterior"])
        lon1 = np.radians(df["longitude_anterior"])
        lat2 = np.radians(df["latitude1"])
        lon2 = np.radians(df["longitude1"])

        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        a = (
                np.sin(delta_lat / 2) ** 2
                + np.cos(lat1)
                * np.cos(lat2)
                * np.sin(delta_lon / 2) ** 2
            )


        distancia_calculada = (
                                    2 * raio_terra * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
                                )

        df["distancia_entre_fotos_m"] = np.where(
                                                    calcular,
                                                    distancia_calculada,
                                                    np.nan
                                                )
        df["velocidade_media_kmh"] = np.where(
                                                calcular,
                                                (df["distancia_entre_fotos_m"] / df["intervalo_s"]) * 3.6,
                                                np.nan
                                            )


        salto = (
                    mesmo_dia
                    & df["intervalo_min"].gt(60)
                )

        df["parada"] = salto

        df.loc[
                salto,
                ["distancia_m", "velocidade_media_kmh"]
            ] = 0.0


        df.loc[
                    df["data_anterior"].notna() & ~mesmo_dia,
                    "parada"
                ] = True

        df = df.drop_duplicates('arquivo')
        df["OBS_SFF"] = "NO"
        df["FLG_IND_SE"] = df["FLG_IND_SE"].fillna(False).astype(bool)
        df["FLG_IND_PONNOT"] = df["FLG_IND_PONNOT"].fillna(False).astype(bool)
        mascara_sem_metadados = df["longitude"].astype("string").str.contains(
                                                                                "Sem metados",
                                                                                case=False,
                                                                                na=False
                                                                            )
        df.loc[
                    mascara_sem_metadados,
                    "OBS_SFF"
                ] = "Metadados espaciais não disponíveis"

        mascara_verificar = (
                                (df["OBS_SFF"] == "NO")
                                & (~df["FLG_IND_SE"])
                                & (~df["FLG_IND_PONNOT"])
                            )

        df.loc[
                    mascara_verificar,
                    "OBS_SFF"
                ] = "Não está próximo a uma entidade geográfica testada (SE e PONNOT)"
        mascara = df["FLG_IND_PONNOT"] & (~df["FLG_IND_SE"])
        df.loc[mascara, "OBS_SFF"] = (
                                        "Próximo a um ponto notável, a "
                                        + df.loc[mascara, "distancia_m"].round(2).astype(str)
                                        + " m. Se for SE e foi concilado por PONNOT, verifique."
                                    )
        mascara = (~df["FLG_IND_PONNOT"]) & (df["FLG_IND_SE"])
        df.loc[mascara, "OBS_SFF"] = (
                                        "Próximo a uma SE. Se não for item de SE, verifique."
                                        )
    df1 = pd.DataFrame(indicios)
    if len(df)>0:
        df.to_csv(f"{caminho_arquivo}/saida_metadados.csv", index=False, encoding='latin-1', sep = "|", decimal=",")
        df.to_sql('tbl_FOTOS', bd, if_exists='replace', index=False)
    if len(df1)>0:
        df1.to_csv(f"{caminho_arquivo}/saida_metadados_indicios.csv", index=False, encoding='latin-1', sep = "|", decimal=",")
        df1.to_sql('tbl_FOTOS_indicios', bd, if_exists='replace', index=False)
    return len(df), len(df)
```

</details>

---

<a id="funcao-36"></a>

## marcar_outliers

Marca outliers em um DataFrame com base em uma coluna específica e um método de detecção.

A função marca os valores considerados outliers em uma coluna do DataFrame, utilizando métodos como Z-score ou IQR. Os outliers são marcados com um novo flag na coluna especificada.

### Assinatura

```python
def marcar_outliers(df, coluna='VL_DC', metodo='iqr', limiar=3, nome_flag='Outlier'):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `DataFrame` | O DataFrame contendo os dados a serem analisados. |
| `coluna` | `str` | Nome da coluna no DataFrame que será usada para detectar outliers. |
| `metodo` | `str` | Método de detecção de outliers. Pode ser 'zscore' ou 'iqr'. |
| `limiar` | `float` | Limite multiplicativo para definir os valores como outliers. |
| `nome_flag` | `str` | Nome da coluna que será adicionada ao DataFrame para indicar outliers. |

### Retorno

**Tipo:** `DataFrame`

O DataFrame original com uma nova coluna 'nome_flag' marcando os valores como outliers.

### Exceções

- **`ValueError`**: Quando o método especificado não é 'iqr' ou 'zscore'.

### Dependências

- `numpy`
- `scipy.stats.zscore`

<details>
<summary>Visualizar código-fonte</summary>

```python
def marcar_outliers(df, coluna='VL_DC', metodo='iqr', limiar=3, nome_flag='Outlier'):
    df = df.copy()

    if metodo == 'zscore':
        z_scores = zscore(df[coluna].dropna())
        abs_z_scores = np.abs(z_scores)
        outliers = abs_z_scores > limiar
        df[nome_flag] = False
        df.loc[df[coluna].dropna().index[outliers], nome_flag] = True

    elif metodo == 'iqr':
        Q1 = df[coluna].quantile(0.25)
        Q3 = df[coluna].quantile(0.75)
        IQR = Q3 - Q1
        limite_inferior = Q1 - limiar * IQR
        limite_superior = Q3 + limiar * IQR
        df[nome_flag] = (df[coluna] < limite_inferior) | (df[coluna] > limite_superior)

    else:
        raise ValueError("Método inválido. Use 'iqr' ou 'zscore'.")

    return df
```

</details>

---

<a id="funcao-37"></a>

## gerar_resumo_contabil

Gera um resumo contábil a partir de dois DataFrames: um com dados financeiros e outro com o plano de contas.

A função processa os dados financeiros, calcula o saldo inicial e final para cada conta, e gera um resumo hierárquico considerando o plano de contas. O resultado inclui valores de débito e crédito por mês e é consolidado em uma estrutura hierárquica.

### Assinatura

```python
def gerar_resumo_contabil(df, df_plano):   
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `Não especificado` | DataFrame contendo os dados financeiros. |
| `df_plano` | `Não especificado` | DataFrame contendo o plano de contas, incluindo a natureza das contas e outros detalhes hierárquicos. |

### Retorno

**Tipo:** `Não especificado`

DataFrame consolidado com resumo contábil hierárquico.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def gerar_resumo_contabil(df, df_plano):   
    def obter_fatores(natureza, cod_cta):
        if natureza == '01':
            return -1, -1, 1, 'D'
        elif natureza in ['02', '03']:
            return 1, -1, 1, 'C'
        elif natureza == '04':
            return (-1, -1, 1, 'D') if cod_cta.startswith('7') else (1, -1, 1, 'C')
        elif natureza == '05':
            return (-1, -1, 1, 'D') if cod_cta.startswith('5') else (1, -1, 1, 'C')
        return 1, -1, 1, 'C'
    
    # Parte 1 – Pré-processamento dos dados
    if 'Dt_REF' in df.columns:
        df_ax = df[df['COL_1'].str.startswith('I1')][['COL_1','COL_2','COL_3','COL_4','COL_5','COL_6','COL_7','COL_8','COL_9','Dt_REF']].copy()
    else:
        df_ax = df[df['COL_1'].str.startswith('I1')][['COL_1','COL_2','COL_3','COL_4','COL_5','COL_6','COL_7','COL_8','COL_9']].copy()
        df_ax.loc[df_ax['COL_1'] == 'I150', 'Dt_REF'] = df_ax['COL_2']
        df_ax['Dt_REF'] = pd.to_datetime(df_ax['Dt_REF'].fillna(method='ffill'), format='%d%m%Y')
    df_ax = df_ax[df_ax['COL_1'] != 'I150'][['COL_2','COL_3','COL_4','COL_5','COL_6','COL_7','COL_8','COL_9','Dt_REF']]
    df_ax.columns = [
        'COD_CTA', 'COD_CCUS', 'VL_SLD_INI', 'IND_DC_INI',
        'VL_DEB', 'VL_CRED', 'VL_SLD_FIN', 'IND_DC_FIN', 'Dt_REF'
    ]
    for col in ['VL_SLD_INI', 'VL_DEB', 'VL_CRED', 'VL_SLD_FIN']:
        if df_ax[col].dtype == 'object':
            df_ax[col] = pd.to_numeric(df_ax[col].str.replace(',', '.'), errors='coerce')
    
    # Parte 2 – Geração do resumo por conta (vetorizado com groupby)
    resumo_list = []
    meses = [f"{n:02}" for n in range(1, 13)]
    
    # Itera por cada conta (grupo)
    for cc, grupo in df_ax.groupby('COD_CTA'):
        # Obter "natureza" da conta a partir do plano (segunda coluna)
        # Como pode não estar no plano, faremos a busca reduzindo o grau
        natureza = None
        for nrc in range(len(cc)+1,0,-1):
            if len(df_plano.loc[df_plano['COD_CTA'] == cc[:nrc]])>0:
                natureza = df_plano.loc[df_plano['COD_CTA'] == cc[:nrc]].iloc[0, 1]
                break
        if natureza is None:
            for digito in cc:
                if digito != "0":
                    filtro = df_plano.loc[df_plano['COD_CTA'] == digito]
                    if not filtro.empty:
                        natureza = filtro.iloc[0, 1]
                    break
        FT_SALDO, FT_DEV, FT_CRD, TP_CNT = obter_fatores(natureza, cc)
        
        grupo = grupo.copy()
        grupo['MES'] = grupo['Dt_REF'].dt.strftime('%m')
        
        # Cálculo do saldo inicial (usa o primeiro VL_SLD_INI e o último IND_DC_INI)
        FT_AJST_ini = 1 if grupo['IND_DC_INI'].iloc[-1] == TP_CNT else -1
        dic_temp = {
            "COD_CTA": cc,
            "VL_SLD_INI": grupo['VL_SLD_INI'].iloc[0] * FT_SALDO * FT_AJST_ini,
            "IND_DC_INI": grupo['IND_DC_INI'].iloc[0]
        }
        
        # Para cada mês, coleta os valores de débito e crédito (assumindo 1 registro por mês)
        for mes in meses:
            reg_mes = grupo.loc[grupo['MES'] == mes]
            if not reg_mes.empty:
                dic_temp[f"VL_DEB_{mes}"] = reg_mes['VL_DEB'].iloc[0] * FT_DEV
                dic_temp[f"VL_CRED_{mes}"] = reg_mes['VL_CRED'].iloc[0] * FT_CRD
            else:
                dic_temp[f"VL_DEB_{mes}"] = 0
                dic_temp[f"VL_CRED_{mes}"] = 0
        
        # Cálculo do saldo final (usa o último VL_SLD_FIN e IND_DC_FIN)
        FT_AJST_fin = 1 if grupo['IND_DC_FIN'].iloc[-1] == TP_CNT else -1
        dic_temp["VL_SLD_FIN"] = grupo['VL_SLD_FIN'].iloc[-1] * FT_SALDO * FT_AJST_fin
        dic_temp["IND_DC_FIN"] = grupo['IND_DC_FIN'].iloc[-1]
        
        resumo_list.append(dic_temp)
    
    RESUMO_CTB = pd.DataFrame(resumo_list)
    
    # Parte 3 – Merge com o plano de contas e consolidação hierárquica
    BP_ECD = df_plano.merge(RESUMO_CTB, how='left', on='COD_CTA')
    
    # Preenche NaNs nas colunas de valores com 0
    vl_cols = [col for col in RESUMO_CTB.columns if col.startswith('VL')]
    BP_ECD[vl_cols] = BP_ECD[vl_cols].fillna(0)
    
    # Consolidação hierárquica: para cada nível (do mais baixo para o mais alto)
    niveis = sorted(BP_ECD['NIVEL'].unique(), key=lambda x: int(x), reverse=True)
    for nivel in niveis:
        # Seleciona os registros do nível atual (filhos)
        filhos = BP_ECD[BP_ECD['NIVEL'] == nivel]
        if not filhos.empty:
            # Agrupa os filhos por seu código de conta superior e soma as colunas de valor
            agregados = filhos.groupby('COD_CTA_SUP')[vl_cols].sum().reset_index()
            # Atualiza os registros dos pais com os valores agregados
            for _, row in agregados.iterrows():
                pai = row['COD_CTA_SUP']
                for col in vl_cols:
                    BP_ECD.loc[BP_ECD['COD_CTA'] == pai, col] = row[col]
    
    return BP_ECD
```

</details>

---

<a id="funcao-38"></a>

## formato_val

Verifica se uma data está no formato especificado.

Tenta converter a string de data para o formato dado. Retorna True se a conversão for bem-sucedida, caso contrário, retorna False.

### Assinatura

```python
def formato_val(data, formato):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `data` | `Não especificado` | String representando uma data. |
| `formato` | `Não especificado` | Formato de data esperado para a string 'data'. |

### Retorno

**Tipo:** `bool`

True se a data estiver no formato especificado, False caso contrário.

### Exceções

- **`ValueError`**: Lançada pela função `datetime.strptime` quando a string de data não corresponde ao formato esperado.

### Dependências

- `datetime.datetime`

<details>
<summary>Visualizar código-fonte</summary>

```python
def formato_val(data, formato):
    try:
        datetime.strptime(data, formato)
        return True
    except ValueError:
        return False
```

</details>

---

<a id="funcao-39"></a>

## conciliar_tolerancia

Concilia dois dataframes, A e B, por (data, valor) com tolerância absoluta no valor (± tol).

A função realiza um pareamento 1-a-1 entre os dois dataframes baseado em colunas de data e valor, considerando uma tolerância absoluta. Os resultados incluem linhas conciliadas, linhas não conciliadas de A e B, e uma coluna 'observacao' indicando a situação.

### Assinatura

```python
# Consulte o código-fonte de conciliar_tolerancia
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `A` | `pd.DataFrame` | O primeiro dataframe a ser conciliado. |
| `B` | `pd.DataFrame` | O segundo dataframe a ser conciliado. |
| `date_col` | `str` | Nome da coluna de data nos dois dataframes. |
| `value_col` | `str` | Nome da coluna de valor nos dois dataframes. |
| `tol` | `float` | Tolerância absoluta para o paramento dos valores. |

### Retorno

**Tipo:** `pd.DataFrame`

DataFrame contendo as linhas conciliadas, não conciliadas de A e B, com uma coluna 'observacao' indicando a situação.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def conciliar_tolerancia(
                                A: pd.DataFrame,
                                B: pd.DataFrame,
                                date_col: str = "data",
                                value_col: str = "valor",
                                tol: float = 0.01,  
                            ) -> pd.DataFrame:
    """
    Concilia dois dataframes, A e B, por (data, valor) com tolerância absoluta no valor (± tol).
    Pareamento 1-a-1 (cada linha casa com no máx. uma do outro lado).
    Retorna um DataFrame com:
       - linhas conciliadas,
       - A não conciliado,
       - B não conciliado,
    e a coluna 'observacao' indicando a situação.

    Observações:
      - Datas são normalizadas para 'date' (descarta hora).
      - Dentro de cada data, valores são ordenados e pareados por varredura
        (greedy), respeitando a tolerância |vA - vB| <= tol.
      - Outras colunas são preservadas com sufixos _A e _B.
    """

    A2 = A.copy()
    B2 = B.copy()

    # normaliza data para date; valores para float
    A2[date_col] = pd.to_datetime(A2[date_col], errors="coerce").dt.date
    B2[date_col] = pd.to_datetime(B2[date_col], errors="coerce").dt.date
    A2[value_col] = pd.to_numeric(A2[value_col], errors="coerce")
    B2[value_col] = pd.to_numeric(B2[value_col], errors="coerce")

    # guarda ID de linha original dos dataframes analisados
    A2 = A2.reset_index().rename(columns={"index": "_row_id_A"})
    B2 = B2.reset_index().rename(columns={"index": "_row_id_B"})

    # Vamos criar um conjunto com as datas possíveis de ambos os dataframes
    all_dates = pd.Series(pd.concat([A2[date_col], B2[date_col]])).dropna().unique()

    # matches coletados: tuplas (row_id_A, row_id_B)
    # Então, cada match é uma lista de tuplas, onde cada tupla contém os índices originais de cada dataframe. 
    # A lista matches começa como vazia e pode ser preenchida com tuplas durante o programa.
    matches: List[Tuple[int, int]] = []

    # --- vamos varer cada data disponível em ambos os datasets, em busca de matchs
    for d in all_dates:
        # kind="stable" é um parâmetro que garante que o algoritmo de ordenação seja estável, 
        # mantendo o mesmo índice para elementos com valores idênticos.
        # ordena as listas considerando o valor
        subA = A2[A2[date_col] == d][[value_col, "_row_id_A"]].sort_values(value_col, kind="stable")
        subB = B2[B2[date_col] == d][[value_col, "_row_id_B"]].sort_values(value_col, kind="stable")
        #inicia os contadores e listas com os dados de valores e indices dos dataframes A e B para a data em análise
        i = j = 0
        valsA = subA[value_col].to_list()
        idsA  = subA["_row_id_A"].to_list()
        valsB = subB[value_col].to_list()
        idsB  = subB["_row_id_B"].to_list()

        # vamos iterar sobre as listas de valores de A e B
        while i < len(valsA) and j < len(valsB):
            # Inicia as variáveis a e b, com os dados das lista e calcula a diferença
            a, b = valsA[i], valsB[j]
            diff = a - b
            # se a diferença é menor que a tolerância temos um match
            if abs(diff) <= tol:
                # Guarda o match na variável match, usando os índices como tupla
                matches.append((idsA[i], idsB[j]))
                i += 1
                j += 1
            else:
                # Ele observa a diferença. Caso seja positiva, dá um passo na lista de dataframe B,
                # caso negativa, no dataframe A.
                if diff < 0:
                    i += 1
                else:
                    j += 1

    # --- identifica os ids dos conciliados
    matched_A_ids = {ra for ra, _ in matches}
    matched_B_ids = {rb for _, rb in matches}

    # --- busca os não conciliados
    a_unmatched = A2[~A2["_row_id_A"].isin(matched_A_ids)]
    b_unmatched = B2[~B2["_row_id_B"].isin(matched_B_ids)]

    # monta DF conciliados via merge em row_ids pareados
    if matches:
        df_pairs = pd.DataFrame(matches, columns=["_row_id_A", "_row_id_B"])
        conciliados = df_pairs.merge(A2, on="_row_id_A", how="left").merge(B2, on="_row_id_B", how="left", suffixes=("_A", "_B"))
    else:
        conciliados = pd.DataFrame(columns=["_row_id_A","_row_id_B"] + [*A2.columns] + [*B2.columns])

    # colunas base e extras
    cols_base = [f"{date_col}_A", f"{value_col}_A", f"{date_col}_B", f"{value_col}_B"]
    cols_A_extra = [c for c in A2.columns if c not in ["_row_id_A", date_col, value_col]]
    cols_B_extra = [c for c in B2.columns if c not in ["_row_id_B", date_col, value_col]]

    if len(conciliados):
        conciliados = conciliados.rename(columns={
            f"{date_col}_A": f"{date_col}_A",
            f"{value_col}_A": f"{value_col}_A",
            f"{date_col}_B": f"{date_col}_B",
            f"{value_col}_B": f"{value_col}_B",
        })
        conciliados.insert(0, "OBS", "Conciliado")
    else:
        conciliados = pd.DataFrame(columns=["OBS", "_row_id_A", "_row_id_B"] + cols_base + cols_A_extra + cols_B_extra)

    # A não conciliado (preenche _B como NA)
    if len(a_unmatched):
        a_nc = a_unmatched.copy()
        a_nc.insert(0, "OBS", "A não conciliado")
        a_nc["_row_id_B"] = pd.NA
        # renomeia base para ter _A e _B explícitos
        a_nc = a_nc.rename(columns={date_col: f"{date_col}_A", value_col: f"{value_col}_A"})
        a_nc[f"{date_col}_B"] = pd.NA
        a_nc[f"{value_col}_B"] = pd.NA
    else:
        a_nc = pd.DataFrame(columns=["OBS", "_row_id_A", "_row_id_B"] + cols_base + cols_A_extra)

    # B não conciliado (preenche _A como NA)
    if len(b_unmatched):
        b_nc = b_unmatched.copy()
        b_nc.insert(0, "OBS", "B não conciliado")
        b_nc["_row_id_A"] = pd.NA
        b_nc = b_nc.rename(columns={date_col: f"{date_col}_B", value_col: f"{value_col}_B"})
        b_nc[f"{date_col}_A"] = pd.NA
        b_nc[f"{value_col}_A"] = pd.NA
    else:
        b_nc = pd.DataFrame(columns=["OBS", "_row_id_A", "_row_id_B"] + cols_base + cols_B_extra)

    def ensure_cols(df, cols):
        """
            Função para garantir a presença de todas as colunas em uma DataFrame.

            Argumentos:
            - df (DataFrame): A DataFrame na qual as colunas serão verificadas e eventualmente adicionadas.
            - cols (list): Uma lista de strings representando os nomes das colunas que devem ser garantidas na DataFrame.

            Processo:
            - Para cada coluna em `cols`, a função verifica se ela já existe na DataFrame `df`.
            - Se uma coluna estiver ausente, a função adiciona essa coluna à DataFrame, preenchendo todos os valores com `pd.NA`.
            - Após o processamento, a função retorna uma nova DataFrame contendo apenas as colunas que foram verificadas e eventualmente adicionadas.

            Útil:
            - É especialmente útil quando você precisa garantir que uma DataFrame contenha todas as colunas necessárias antes de realizar operações de análise ou processamento, por exemplo, para modelagem estatística ou machine learning.
        """
        for c in cols:
            if c not in df.columns:
                df[c] = pd.NA
        return df[cols]

    ordered_cols = (
        ["OBS", "_row_id_A", "_row_id_B"]
        + cols_base
        + cols_A_extra
        + cols_B_extra
    )

    conciliados = ensure_cols(conciliados, ordered_cols)
    a_nc       = ensure_cols(a_nc,       ordered_cols)
    b_nc       = ensure_cols(b_nc,       ordered_cols)

    df_AB = pd.concat([conciliados, a_nc, b_nc], ignore_index=True)
    # ordena por data (A/B), valor (A/B) e observacao
    sort_keys = [c for c in [f"{date_col}_A", f"{date_col}_B", f"{value_col}_A", f"{value_col}_B", "OBS"] if c in df_AB.columns]
    df_AB = df_AB.sort_values(by=sort_keys, kind="stable").reset_index(drop=True)

    return df_AB
```

</details>

---

<a id="funcao-40"></a>

## bsc_dados2

Processa e normaliza dados de uma base de dados, retornando um DataFrame com os dados ajustados.

A função `bsc_dados2` processa e normaliza dados de uma base de dados, utilizando arquivos CSV para obter informações. Ela verifica a existência de uma tabela específica na base de dados e, se não existir ou se o parâmetro `REF` for verdadeiro, realiza várias etapas de leitura, limpeza e transformação dos dados. O resultado é um DataFrame contendo os dados ajustados.

### Assinatura

```python
def bsc_dados2(bd, empresa, ano1, lst_lcto = None, TIP = None, REF = False, st=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `bd` | `Não especificado` | Conexão com a base de dados onde os dados serão inseridos. |
| `empresa` | `Não especificado` | Identificador da empresa para filtrar os dados. |
| `ano1` | `Não especificado` | Ano de referência para o qual os dados serão ajustados e inseridos na base de dados. |
| `lst_lcto` | `Não especificado` | Lista de identificadores de lançamentos a serem processados. Se for uma lista com um único elemento, ele será convertido em uma string. |
| `TIP` | `Não especificado` | Tipo de dados a serem processados. |
| `REF` | `Não especificado` | Indica se deve refletir os dados na base de dados existente. |
| `st` | `Não especificado` | Objeto Streamlit para exibir mensagens de erro ou informações. |

### Retorno

**Tipo:** `DataFrame`

DataFrame contendo os dados ajustados e normalizados.

### Exceções

- **`UserWarning`**: Quando ocorre um problema de codificação do arquivo CSV.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def bsc_dados2(bd, empresa, ano1, lst_lcto = None, TIP = None, REF = False, st=None):
    
    if existe_tabela(f"TBL_LCMT_CVA_{TIP}_{ano1}", bd) and (not REF):
        sSQL = f"SELECT * FROM TBL_LCMT_CVA_{TIP}_{ano1}"
        return pd.read_sql(sSQL,bd)
    

    ###############################################################################################
    df_PART = pd.DataFrame()
    dt_ARQ = max_arq('LD_PTD', bd, empresa)
    dt_ARQ1 = max_arq('LD_LCMTO', bd, empresa)
    if not dt_ARQ1:
        dt_ARQ1 = max_arq('LD_LCMTO_', bd, empresa)
        
    Cd_EMP = f"00000{bsc_cd_aneel(empresa)}"[-5:]
    if len(lst_lcto) == 1:
        filtro_lcto = f"({lst_lcto[0]})"
    else:
        filtro_lcto = lst_lcto
    
    erro = {}

    try:
        sanear_csv(
                            diretorio = f"{st.session_state.tra_dir}/SDI_001",
                            arq = f"LD_LCMTO_{Cd_EMP}_{dt_ARQ1}.csv", st = st                                    
                        )
        sanear_csv(
                            diretorio = f"{st.session_state.tra_dir}/SDI_001",
                            arq = f"LD_PTD_{Cd_EMP}_{dt_ARQ}.csv" , st = st                                  
                        )
    except Exception as e:
        st.error(e)
        return pd.DataFrame()
    
    def localizar_pipes_excedentes(
                                    caminho,
                                    qtd_pipes_esperada,
                                    limite=100,
                                ):
        erros = []

        with open(caminho, "rb") as arquivo:
            for numero_linha, linha in enumerate(arquivo, start=1):
                qtd_pipes = linha.count(b"|")

                if qtd_pipes > qtd_pipes_esperada:
                    erros.append({
                                    "linha": numero_linha,
                                    "pipes": qtd_pipes,
                                    "esperado": qtd_pipes_esperada,
                                    "trecho": linha[:500],
                                })

                    if len(erros) >= limite:
                        break

        return erros
    
    def testar_csv(caminho, encoding):
        with duckdb.connect() as con:
            return con.execute(
                                    """
                                    SELECT COUNT(*)
                                    FROM read_csv(
                                        ?,
                                        delim = '|',
                                        header = true,
                                        encoding = ?,
                                        all_varchar = true,
                                        parallel = false,
                                        null_padding = true,
                                        strict_mode = false,
                                        ignore_errors = false
                                    )
                                    """,
                                    [str(caminho), encoding],
                                ).fetchone()[0]
        
    FLG_TST = True
    nm1 = rf'{st.session_state.tra_dir}\\SDI_001\\LD_LCMTO_{Cd_EMP}_{dt_ARQ1}.csv'
    nm2 = rf'{st.session_state.tra_dir}\\SDI_001\\LD_PTD_{Cd_EMP}_{dt_ARQ}.csv'
    
    for enc in ['utf-8', 'CP1252', 'latin-1', ]:
        con = None
        try:
            con = duckdb.connect()
            if FLG_TST:
                try:
                    for arqx, arquivo in enumerate([nm1, nm2]):
                        qtd = testar_csv(arquivo, enc)
                        FLG_TST = False
                except Exception as e:
                    st.error(f"{enc}, {arquivo}, {type(e).__name__}, {e}")
                    erros_lcmto = localizar_pipes_excedentes(
                                                                arquivo,
                                                                qtd_pipes_esperada= (4 + arqx*2),
                                                            )
                    st.write(erros_lcmto)
                    raise

            SQLq = f"""
                            WITH tbl_temp_lcmto AS (
                            SELECT 
                                NUM_LCTO,
                                Dt_LCMTO,
                                IND_LCMTO,
                                VL_LCMTO
                            FROM (
                                SELECT 
                                    NUM_LCTO,
                                    Dt_LCMTO,
                                    IND_LCMTO,
                                    Id_SEQ_LCMTO,
                                    VL_LCMTO,
                                    ROW_NUMBER() OVER (
                                        PARTITION BY NUM_LCTO 
                                        ORDER BY Id_SEQ_LCMTO ASC
                                    ) AS row_num
                                FROM read_csv(
                                    {nm1},
                                    delim='|',
                                    null_padding=true, 
                                    encoding='{enc}',
                                    parallel=true,
                                    all_varchar=true
                                )
                            )
                            WHERE row_num = 1
                        )

                        SELECT 
                            REPLACE(TRY_CAST(t1.Cd_CC AS STRING),'.0','') AS COD_CTA, 
                            t1.COD_CCUS, 
                            TRY_CAST(REPLACE(t1.VL_DC,',','.') AS DOUBLE) AS VL_DC, 
                            t1.IND_DC, 
                            '' AS NUM_ARQ, 
                            '' AS COD_HIST_PAD, 
                            t1.HIST AS COD_HIST, 
                            '' AS COD_PART, 
                            REPLACE(TRY_CAST(t2.NUM_LCTO AS STRING),'.0','') AS NUM_LCTO, 
                            t2.Dt_LCMTO, 
                            TRY_CAST(REPLACE(t2.VL_LCMTO,',','.') AS DOUBLE) AS VL_LCTO, 
                            t2.IND_LCMTO AS IND_LCTO, 
                            '' AS DT_LCTO_EXT, 
                            t2.Dt_LCMTO AS Dt_REF
                        FROM read_csv(
                                {nm2},
                                delim='|',
                                null_padding=true, 
                                encoding='{enc}',
                                parallel=true,
                                all_varchar=true
                        ) t1
                        LEFT JOIN tbl_temp_lcmto t2 
                            ON t1.NUM_LCTO = t2.NUM_LCTO
                        WHERE REPLACE(CAST(t1.NUM_LCTO AS STRING),'.0','') IN {filtro_lcto}
                    """
            df_PART = con.sql(SQLq).df()
            break
        except Exception as e:
            erro[enc] = e
            df_PART= pd.DataFrame()
        finally:
            if con is not None:
                try:
                    con.close()
                except Exception:
                    pass

    if len(df_PART)==0:
        try:
            df = pd.read_csv(nm2, sep='|', encoding='latin-1', dtype=str, on_bad_lines="error",)
            df1 = pd.read_csv(nm1, sep='|', encoding='latin-1', dtype=str, on_bad_lines="error",)
            df1["_ordem"] = pd.to_numeric(
                                                    df1["Id_SEQ_LCMTO"],
                                                    errors="coerce",
                                                )

            df1 = (
                        df1
                        .sort_values(
                                        ["NUM_LCTO", "_ordem"],
                                        na_position="last",
                                    )
                        .drop_duplicates(
                                            subset="NUM_LCTO",
                                            keep="first",
                                        )
                        [
                            [
                                "NUM_LCTO",
                                "Dt_LCMTO",
                                "IND_LCMTO",
                                "VL_LCMTO",
                            ]
                        ]
                    )
            filtro_lcto_normalizado = {
                                        str(valor).strip().removesuffix(".0")
                                        for valor in filtro_lcto
                                    }
            df["NUM_LCTO"] = (
                                    df["NUM_LCTO"]
                                    .astype(str)
                                    .str.strip()
                                    .str.replace(r"\.0$", "", regex=True)
                                )

            df1["NUM_LCTO"] = (
                                    df1["NUM_LCTO"]
                                    .astype(str)
                                    .str.strip()
                                    .str.replace(r"\.0$", "", regex=True)
                                )

            df = df[
                        df["NUM_LCTO"].isin(filtro_lcto_normalizado)
                    ].copy()
            
            df_PART = df.merge(
                                    df1,
                                    on="NUM_LCTO",
                                    how="left",
                                    suffixes=("", "_LCMTO"),
                                )
            
            df_PART["COD_CTA"] = (
                                    df_PART["Cd_CC"]
                                        .astype(str)
                                        .str.replace(r"\.0$", "", regex=True)
                                )

            df_PART["VL_DC"] = pd.to_numeric(
                                                df_PART["VL_DC"]
                                                .astype(str)
                                                .str.replace(",", ".", regex=False),
                                                errors="coerce",
                                            )

            df_PART["VL_LCTO"] = pd.to_numeric(
                                                    df_PART["VL_LCMTO"]
                                                    .astype(str)
                                                    .str.replace(",", ".", regex=False),
                                                    errors="coerce",
                                                )

            df_PART["NUM_ARQ"] = ""
            df_PART["COD_HIST_PAD"] = ""
            df_PART["COD_HIST"] = df_PART["HIST"]
            df_PART["COD_PART"] = ""
            df_PART["IND_LCTO"] = df_PART["IND_LCMTO"]
            df_PART["DT_LCTO_EXT"] = ""
            df_PART["Dt_REF"] = df_PART["Dt_LCMTO"]
            df_PART = df_PART[
                                [
                                    "COD_CTA",
                                    "COD_CCUS",
                                    "VL_DC",
                                    "IND_DC",
                                    "NUM_ARQ",
                                    "COD_HIST_PAD",
                                    "COD_HIST",
                                    "COD_PART",
                                    "NUM_LCTO",
                                    "Dt_LCMTO",
                                    "VL_LCTO",
                                    "IND_LCTO",
                                    "DT_LCTO_EXT",
                                    "Dt_REF",
                                ]
                                ]
        except Exception as e:
            erro['read_csv'] = f"Falhou mesmo usando read_csv: {e}"
            st.text(erro)
            raise UserWarning("Você tem problema de codificação do arquivo.")

    def ajustar_data(data_str):
        if "/" in data_str:
            partes = data_str.split('/')
        else:
            partes = data_str.split('-')
        ano = partes[0]
        mes = partes[1].zfill(2)
        return f"{ano}/{mes}/01"
    
    if len(df_PART)>0:
        df_PART['Dt_REF'] = df_PART['Dt_REF'].ffill()
        df_PART['Dt_REF'] = df_PART['Dt_REF'].astype(str).apply(ajustar_data)
        df_PART['Dt_REF'] = pd.to_datetime(df_PART['Dt_REF'], format='%Y/%m/%d', errors='coerce')
        df_PART['Dt_REF'] = df_PART['Dt_REF'].ffill()
        df_PART[df_PART['Dt_REF'].dt.year == ano1].to_sql(f"TBL_LCMT_CVA_{TIP}_{ano1}", bd, if_exists='replace', index=False)
        return df_PART[df_PART['Dt_REF'].dt.year==ano1]
    else:
        return (pd.DataFrame(columns=['COD_CTA', 'COD_CCUS', 'VL_DC', 'IND_DC', 'NUM_ARQ', 'COD_HIST_PAD', 
                            'COD_HIST', 'COD_PART', 'NUM_LCTO', 'Dt_LCMTO', 'VL_LCTO', 'IND_LCTO', 
                            'DT_LCTO_EXT', 'Dt_REF', 'FLG_CX', 'OBS_LCTO']))
```

</details>

---

<a id="funcao-41"></a>

## bsc_dados_parquet

Processa e salva dados em formato Parquet, filtrando e transformando conforme especificado.

A função `bsc_dados_parquet` realiza várias operações para processar e salvar dados em formato Parquet. Ela verifica a existência de arquivos Parquet locais e, se necessário, executa consultas SQL para gerar novos arquivos Parquet com os dados filtrados e transformados. Além disso, ela cria uma tabela temporária e realiza junções entre tabelas Parquet e a tabela temporária.

### Assinatura

```python
def bsc_dados_parquet(n1=2020, TIP = None, lst = None, bdduck = None, st=None, refaz = False):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `n1` | `Não especificado` | Ano de referência para os dados. |
| `TIP` | `Não especificado` | Tipo específico dos dados a serem processados. |
| `lst` | `Não especificado` | Lista de valores utilizada para filtrar os dados. |
| `bdduck` | `Não especificado` | Objeto utilizado para executar consultas SQL no banco de dados. |
| `st` | `Não especificado` | Estado da sessão do Streamlit, usado para acessar diretórios locais. |
| `refaz` | `Não especificado` | Indica se os arquivos Parquet devem ser recriados mesmo que já existam. |

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def bsc_dados_parquet(n1=2020, TIP = None, lst = None, bdduck = None, st=None, refaz = False):
    if (TIP != None) and (lst != None):
        parquet_file = os.path.join(
                                        st.session_state.tra_dir,
                                        "BD_LOCAL",
                                        f"partidas_{n1}.parquet"
                                    )
        familia_file = os.path.join(
                                        st.session_state.tra_dir,
                                        "BD_LOCAL",
                                        f"familia_{n1}.parquet"
                                    )
        if refaz or (not (os.path.exists(parquet_file))):
            bdduck.execute(f"""
                            COPY (
                                SELECT "COL_1", "COL_2", "COL_3", "COL_4", "COL_5", 
                                    "COL_6", "COL_7", "COL_8", "COL_9"
                                FROM nv_ARQ{n1}
                                WHERE "COL_1" LIKE 'I2%'
                            ) TO '{parquet_file}' (FORMAT PARQUET);
                          """)
        if refaz or (not (os.path.exists(familia_file))):
            bdduck.execute(f"""
                                COPY (
                                    WITH marcados AS (
                                        SELECT *,
                                            CASE 
                                                WHEN "COL_1" = 'I200' THEN "COL_2" 
                                            END AS nome_pai,
                                            ROW_NUMBER() OVER () AS posicao
                                        FROM read_parquet('{parquet_file}')
                                    ),
                                    familia AS (
                                        SELECT *,
                                            LAST_VALUE(nome_pai IGNORE NULLS) 
                                                OVER (ORDER BY posicao) AS pai_grupo
                                        FROM marcados
                                    )
                                    SELECT *
                                    FROM familia
                                ) TO '{familia_file}' (FORMAT PARQUET);
                            """)
        
        bdduck.execute("DROP TABLE IF EXISTS tmp_lst;")
        bdduck.execute("CREATE TEMP TABLE tmp_lst(valor VARCHAR);")
        bdduck.executemany(
                                "INSERT INTO tmp_lst VALUES (?)",
                                [(x,) for x in lst]
                            )
        
        bdduck.execute(f"""
                            DROP TABLE IF EXISTS TBL_LCMT_CVA_{TIP}_{n1};
                            CREATE TABLE TBL_LCMT_CVA_{TIP}_{n1} AS
                            SELECT *
                            FROM read_parquet(?) f
                            WHERE f.pai_grupo IN (
                                SELECT f2.pai_grupo
                                FROM read_parquet(?) f2
                                INNER JOIN tmp_lst l
                                    ON f2.COL_2 = l.valor
                                WHERE f2.COL_1 = 'I200'
                            );
                        """, [familia_file, familia_file])
```

</details>

---

<a id="funcao-42"></a>

## bsc_dados

Executa consultas SQL para criar índices e tabelas temporárias em um banco de dados.

A função cria um índice se o tipo e a lista forem fornecidos, e então executa uma consulta complexa que filtra registros com base em certos critérios. A consulta envolve várias etapas como seleção de colunas, criação de tabelas temporárias e filtragem por condições específicas.

### Assinatura

```python
def bsc_dados(n1=2020, TIP = None, lst = None, bdduck = None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `n1` | `Não especificado` | Ano do arquivo a ser processado. |
| `TIP` | `Não especificado` | Tipo de dados a serem filtrados. |
| `lst` | `Não especificado` | Lista de valores para filtrar na coluna COL_2. |
| `bdduck` | `Não especificado` | Conexão com o banco de dados onde as operações serão realizadas. |

### Dependências

- `bdduck.execute`

<details>
<summary>Visualizar código-fonte</summary>

```python
def bsc_dados(n1=2020, TIP = None, lst = None, bdduck = None):
    if (TIP != None) and (lst != None):
        bdduck.execute(f"CREATE INDEX IF NOT EXISTS idx_col1_{n1} ON nv_ARQ{n1} (\"COL_1\");")
        bdduck.execute(f"""
                        DROP TABLE IF EXISTS TBL_LCMT_CVA_{TIP}_{n1};
                        CREATE TABLE TBL_LCMT_CVA_{TIP}_{n1} AS
                        WITH partidas AS (
                            SELECT  t1."COL_1",
                                    t1."COL_2",
                                    t1."COL_3",
                                    t1."COL_4",
                                    t1."COL_5",
                                    t1."COL_6",
                                    t1."COL_7",
                                    t1."COL_8",
                                    t1."COL_9"
                            FROM nv_ARQ{n1} t1 WHERE t1."COL_1" LIKE 'I2%'
                        ),
                        marcados AS (
                            SELECT *,
                                CASE WHEN COL_1 = 'I200' THEN COL_2 END AS nome_pai,
                                ROW_NUMBER() OVER () AS posicao
                            FROM partidas
                        ),
                        familia AS (
                            SELECT *,
                                LAST_VALUE(nome_pai IGNORE NULLS) OVER (ORDER BY posicao) AS pai_grupo
                            FROM marcados
                        )
                        SELECT *
                        FROM familia
                        WHERE pai_grupo IN (
                            SELECT pai_grupo FROM familia
                            WHERE COL_1 = 'I200' AND COL_2 IN {lst}
                        )
                        """)
```

</details>

---

<a id="funcao-43"></a>

## ams_lcmto

Seleciona amostras de um DataFrame com base em critérios específicos.

A função `ams_lcmto` seleciona amostras de um DataFrame com base em várias condições, incluindo dias antes e depois de uma data específica, valores negativos, períodos críticos e itens relevantes. Também permite a definição de uma semente para reproducibilidade dos resultados.

### Assinatura

```python
# Consulte o código-fonte de ams_lcmto
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `pd.DataFrame` | DataFrame contendo os dados a serem analisados. |
| `nr_dias_antes` | `int` | Número de dias antes da data de lançamento para considerar na amostragem. |
| `nr_dias_depois` | `int` | Número de dias depois da data de lançamento para considerar na amostragem. |
| `semente` | `int` | Semente para o gerador de números aleatórios, para garantir reproducibilidade dos resultados. |
| `st` | `Não especificado` | Objeto Streamlit para exibir mensagens de aviso. |

### Retorno

**Tipo:** `pd.DataFrame`

DataFrame com as amostras selecionadas e os critérios aplicados.

### Exceções

- **`ValueError`**: Quando há colunas ausentes no DataFrame.

### Dependências

- `numpy`
- `pandas`
- `streamlit`

<details>
<summary>Visualizar código-fonte</summary>

```python
def ams_lcmto(
                df: pd.DataFrame = None,
                nr_dias_antes: int = 10,
                nr_dias_depois: int = 10,
                semente: int = 42,
                st=None
             ) -> pd.DataFrame:
    COLS_NEC = ["Ide_RO_Analitico", "Cd_NG", "COD_ITEM", "Cd_CA", "Qtd", "Unidade", "VL_tot", "Dt_Lcmto"]

    dds_aus = set(COLS_NEC) - set(df.columns)
    if dds_aus:
        raise ValueError(f"Colunas ausentes: {dds_aus}")
    if semente is not None:
        np.random.seed(semente)
    df_sai = df.copy()
    df_sai["Dt_Lcmto"] = pd.to_datetime(df_sai["Dt_Lcmto"], format='mixed')
    df_sai = df_sai.sort_values(by='Dt_Lcmto')
    if df_sai["Dt_Lcmto"].isna().any():
        raise ValueError("Há Dt_Lcmto inválidas (NaT). Corrija antes de prosseguir.")

    if df_sai["VL_tot"].isna().any():
       st.warning("Há VL_tot inválidos (NaN). Corrija antes de prosseguir.")
       df_sai["VL_tot"] = df_sai["VL_tot"].fillna(0)
    
    df_sai["selecionado_fiscalizacao"] = False
    df_sai["criterio"] = ""

    # Alguns projetos podem ter reduzido de lançamentos, neste caso analisa-se a totalidade dos lançamentos
    # Usaremos todos os lançamentos do projeto, antes de buscar itens criticos para definir se é obra toda
    # ou parcial para avaliar
    n = calcular_n_hiper(len(df_sai), taxa_erro_toleravel = 0.05, confianca=0.95)
    if len(df_sai) <= n:
        df_sai["selecionado_fiscalizacao"] = True
        df_sai["criterio"] = "O projeto possui população menor que o mínimo de elementos a ser amostrado (100%)"
        return df_sai

    # Lançamentos negativos indicam correções de diferentes tipos: estornos (retorno ao estoque), mutação entre projetos,
    # erros de apropriação, etc.. A fiscalização objetiva entender os fatos geradores dessas correções e avaliar os procedimentos
    # da empresa, por isso o critério será análise de 100% dos itens

    crit_neg = df_sai["VL_tot"] < 0
    df_sai.loc[crit_neg, "selecionado_fiscalizacao"] = True
    df_sai.loc[crit_neg, "criterio"] = "Valor Negativo (100%)"

    # Análise de períodos críticos: fechamento da obra, fechamentos de informações contábeis: anual e trimestral
    max_DT = pd.to_datetime(df_sai["Dt_Lcmto"].max())
    min_DT = pd.to_datetime(df_sai["Dt_Lcmto"].min())
    intervalo = pd.date_range(start=min_DT, end=max_DT, freq='QE')
    if len(intervalo)>0:
        LST_DTS_CORTE = intervalo.tolist()
    else:
        LST_DTS_CORTE = []
    #if max_DT not in LST_DTS_CORTE:
    #    LST_DTS_CORTE.append(max_DT)
        
    dts = pd.to_datetime(LST_DTS_CORTE)
    janelas_inicio = dts - pd.Timedelta(days=nr_dias_antes)
    janelas_fim = dts + pd.Timedelta(days=nr_dias_depois)
    
    data_lancamento = df_sai["Dt_Lcmto"].values[:, None]
    
    crit_janela = (
                        (data_lancamento >= janelas_inicio.values) & 
                        (data_lancamento <= janelas_fim.values)
                    ).any(axis=1)


    df_sai.loc[crit_janela, "selecionado_fiscalizacao"] = True
    crit_jan_amp = crit_janela & (df_sai["criterio"] == "")
    df_sai.loc[crit_jan_amp, "criterio"] = "Período crítico (100% janela)"

    # Filtrar itens negativos, só aplico em itens positivos a amostragem
    # Antes, vamos retirar itens criticos, por valor significativo no projeto
    # Criterio é ser maior que o IA 
    rem = df_sai[(~df_sai["selecionado_fiscalizacao"]) & (df_sai["VL_tot"] > 0)].copy()
    if rem.empty:
        return df_sai[df_sai["selecionado_fiscalizacao"]].copy()
    

    # Alguns projetos podem ter elementos que são relevantes, considerando o projeto, iremos buscar o valor que representa os 5% maiores
    limiar_lcmto_relevante = df_sai["VL_tot"].quantile(0.95)
    crit_rel = df_sai["VL_tot"] >= limiar_lcmto_relevante
    df_sai.loc[crit_rel, "selecionado_fiscalizacao"] = True
    df_sai.loc[crit_rel, "criterio"] = "Valor Relevante (100%)"

    # Agora faço a amostragem
    rem = df_sai[(~df_sai["selecionado_fiscalizacao"])].copy()
    if rem.empty:
        return df_sai[df_sai["selecionado_fiscalizacao"]].copy()
    
    n = calcular_n_hiper(len(rem), taxa_erro_toleravel = 0.05, confianca=0.95)
    if len(rem)<= n:
        # Não há elementos para sortear considerando os elementos críticos
        crit_corte = df_sai["criterio"] == ""
        df_sai.loc[crit_corte, "selecionado_fiscalizacao"] = True
        df_sai.loc[crit_corte, "criterio"] = "Excluído elementos críticos, há poucos elementos, fazer 100%"
        return df_sai
    else:
        
        total_rem = rem["VL_tot"].sum()
        intervalo = total_rem / n
        rem = rem.sort_values(by='Dt_Lcmto')
        rem['VL_SLD_ACM'] = rem["VL_tot"].cumsum()
        
        pontos_de_corte = np.arange(intervalo / 2, total_rem, intervalo)
        indices_pos = np.searchsorted(rem['VL_SLD_ACM'].values, pontos_de_corte)
        indices_pos = indices_pos[indices_pos < len(rem)]
        amostra_indices_reais = rem.index[indices_pos]
        if len(amostra_indices_reais) > 0:
            lst_crit = rem.loc[amostra_indices_reais]['Ide_RO_Analitico'].drop_duplicates().to_list()
            crit_amst = df_sai['Ide_RO_Analitico'].isin(lst_crit)
            df_sai.loc[crit_amst, "selecionado_fiscalizacao"] = True
            df_sai.loc[crit_amst, "criterio"] = "Selecionado por sorteio"
    return df_sai
```

</details>

---

<a id="funcao-44"></a>

## vpl_regulatorio_com_depreciacao

Calcula o Valor Presente Líquido (VPL) regulatorio considerando a depreciação.

Este método calcula o VPL regulatorio para um investimento, levando em conta a vida útil do ativo, o atraso e a taxa de desconto WACC. A depreciação é aplicada anualmente e os valores são atualizados conforme o tempo.

### Assinatura

```python
# Consulte o código-fonte de vpl_regulatorio_com_depreciacao
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `investimento` | `float` | Valor inicial do investimento. |
| `vida_util` | `int` | Número de anos úteis do ativo. |
| `atraso` | `int` | Número de anos até o início dos benefícios financeiros. |
| `wacc` | `float` | Taxa de desconto ponderada (WACC) usada para calcular os valores presentes. |

### Retorno

**Tipo:** `float`

Valor Presente Líquido regulatorio do investimento.

### Dependências

- `{'nome': 'max', 'categoria': 'chamada', 'descricao': 'Função usada para calcular o número de anos reconhecidos.'}`
- `{'nome': 'range', 'categoria': 'chamada', 'descricao': 'Função usada no loop for para iterar sobre os anos.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def vpl_regulatorio_com_depreciacao(
                                        investimento: float,
                                        vida_util: int,
                                        atraso: int,
                                        wacc: float,
                                    ) -> float:

    dep_anual = investimento / vida_util
    dep_acum = atraso * dep_anual
    base = investimento - dep_acum

    vpl = -investimento

    anos_reconhecidos = max(vida_util - atraso, 0)

    for t in range(1, anos_reconhecidos + 1):
        remuneracao = base * wacc
        cota = dep_anual
        receita = remuneracao + cota

        vpl += receita / ((1 + wacc) ** (atraso + t))

        base -= dep_anual

    return vpl
```

</details>

---

<a id="funcao-45"></a>

## breakeven_com_perda_vida_util

Calcula o ponto de equilíbrio (breakeven) considerando perdas de vida útil e atrasos regulatorios.

Esta função calcula o ponto de equilíbrio para diferentes combinações de vida útil total, atraso regulatorio e vida útil reconhecida. Utiliza um investimento real como base e retorna uma tabela com os resultados normalizados pelo investimento.

### Assinatura

```python
# Consulte o código-fonte de breakeven_com_perda_vida_util
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `wacc` | `float` | Taxa de retorno mínima exigida (WACC) para o cálculo. |
| `atraso_anos` | `Iterable[int]` | Intervalo de anos considerados para o atraso regulatorio. |
| `vidas_uteis` | `Iterable[int]` | Intervalo de vida útil total considerado. |
| `investimento_real` | `Optional[float]` | Valor do investimento real utilizado no cálculo (padrão é 1.0). |

### Retorno

**Tipo:** `List[Dict]`

Lista de dicionários contendo os resultados para cada combinação de vida útil total, atraso regulatorio e vida útil reconhecida.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def breakeven_com_perda_vida_util(
                                    wacc: float,
                                    atraso_anos: Iterable[int] = range(0, 5),
                                    vidas_uteis: Iterable[int] = range(5, 51),
                                    investimento_real: Optional[float] = 1.0,
                                  ) -> List[Dict]:

    resultados = []

    for N in vidas_uteis:
        if N <= 0:
            continue

        for atr in atraso_anos:
            N_rec = max(N - atr, 0)

            vpl_norm = vpl_regulatorio_com_depreciacao(
                                                            investimento=investimento_real,
                                                            vida_util=N,
                                                            atraso=atr,
                                                            wacc=wacc,
                                                        )

            row =   {
                        "vida_util_total": N,
                        "atraso_regulatorio": atr,
                        "vida_util_reconhecida": N_rec,
                        "vpl_normalizado": vpl_norm / investimento_real
                    }

            resultados.append(row)

    return pd.DataFrame(resultados)
```

</details>

---

<a id="funcao-46"></a>

## desenhar_grafo_hierarquico

Desenha um grafo hierárquico com base em um DataFrame e um dicionário de níveis.

A função cria um grafo direcionado hierárquico a partir dos dados fornecidos, utilizando uma estrutura de categorias definida no dicionário de níveis. O grafo é visualizado usando Streamlit e inclui informações sobre os nós e arestas, além de estatísticas do grafo.

### Assinatura

```python
# Consulte o código-fonte de desenhar_grafo_hierarquico
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `Não especificado` | DataFrame contendo os dados a serem visualizados no grafo. |
| `dicionario_niveis` | `Não especificado` | Dicionário onde as chaves são os níveis hierárquicos e os valores são listas de colunas que definem as categorias a serem agrupadas no nível correspondente. |
| `valor_total` | `Não especificado` | Valor total dos dados, usado para calcular proporções nos nós do grafo. |
| `nm_cat` | `Não especificado` | Nome da coluna que contém o valor a ser somado e exibido no grafo. |
| `figsize` | `Não especificado` | Tamanho da figura do gráfico, definido como uma tupla (largura, altura). |
| `st` | `Não especificado` | Objeto Streamlit para renderizar a interface do usuário. |

### Retorno

**Tipo:** `Não especificado`

Grafo direcionado hierárquico criado, ou None se algum parâmetro necessário estiver ausente ou inválido.

### Dependências

- `collections.defaultdict`
- `matplotlib.colors`
- `matplotlib.pyplot`
- `networkx`
- `numpy`
- `pandas`
- `streamlit`

<details>
<summary>Visualizar código-fonte</summary>

```python
def desenhar_grafo_hierarquico(
                               df = None, 
                               dicionario_niveis = None, 
                               valor_total = None,
                               nm_cat = None, 
                               figsize=(15, 10),
                               st = None):
    
    if df.empty:
        st.warning("DataFrame está vazio.")
        return None
    
    if (st == None):
        st.warning("Sem streamlit está vazio.")
        return None
        
    if not dicionario_niveis:
        st.warning("Dicionário de níveis está vazio.")
        return None
    
    G = nx.DiGraph()
    mapeamento_categorias = {}
    proxima_cor = 0

    Nr_NOS = 1
    for key, value in dicionario_niveis.items():
        Nr_NOS += len(df.groupby(value, dropna=False)[nm_cat].count().reset_index())
    cmap = plt.get_cmap('tab20')
    if Nr_NOS <= 20:
        cores_base = [mcolors.rgb2hex(cmap(i)) for i in range(Nr_NOS)]
    else:
        cmap_expandido = plt.get_cmap('turbo')
        cores_base = [mcolors.rgb2hex(cmap_expandido(i)) for i in np.linspace(0.1, 0.9, Nr_NOS)]
    G.add_node("Total", nivel=0, valor=valor_total, label="Total")
    mapeamento_categorias["Total"] = cores_base[0]

    for nivel, colunas in sorted(dicionario_niveis.items()):
        nivel_int = int(nivel)
        colunas_validas = [col for col in colunas if col in df.columns]
        if len(colunas_validas) != len(colunas):
            st.warning(f"Algumas colunas do nível {nivel} não existem no DataFrame: {set(colunas) - set(colunas_validas)}")
            continue
        grupo = df.groupby(colunas_validas)[nm_cat].sum().reset_index()

        for _, row in grupo.iterrows():
            nome_no = "_".join([str(row[col]) for col in colunas_validas])
            valor_no = row[nm_cat]
            valores_no = [str(row[col]) for col in colunas_validas]
            label_no = " / ".join(valores_no) + f"\n{valor_no:,.0f}"
            categoria = valores_no[-1] if valores_no else "Sem Categoria"
            if nivel_int == 1 and valores_no:
                categoria = valores_no[0]
            categoria_composta = categoria
            G.add_node(nome_no, nivel=int(nivel), valor=valor_no, label=label_no, valores=valores_no, categoria=categoria,
                      categoria_cmp=categoria_composta)
            if categoria_composta not in mapeamento_categorias:
                mapeamento_categorias[categoria_composta] = cores_base[proxima_cor % len(cores_base)]
                proxima_cor += 5
            if int(nivel) == 1:
                pai = "Total"
            else:
                nivel_anterior = (int(nivel) - 1)
                if nivel_anterior in dicionario_niveis:
                    colunas_pai = dicionario_niveis[nivel_anterior]
                    valores_pai = [str(row[col]) for col in colunas_pai]
                    pai = "_".join(valores_pai)
                else:
                    pai = "Total"
            
            if pai in G.nodes and pai != nome_no:
                proporcao = valor_no / valor_total
                G.add_edge(pai, nome_no, peso=proporcao, label=f"{proporcao:.1%}")
    
    if len(G.nodes()) <= 1:
        st.warning("Grafo não possui nós suficientes para visualização.")
        return G
    
    def criar_layout_hierarquico(G):
        pos = {}
        niveis = {}
        
        for node in G.nodes():
            nivel = G.nodes[node]['nivel']
            if nivel not in niveis:
                niveis[nivel] = []
            niveis[nivel].append(node)
        
        x_spacing = 1.25
        y_spacing = 0.6

        def media_y_pais(n):
            pais = list(G.predecessors(n))
            if not pais:
                return 0
            return sum(pos[p][1] for p in pais if p in pos) / len(pais)
        
        for nivel in sorted(niveis):
            nos = niveis[nivel]

            if nivel > 0:
                nos = sorted(nos, key=media_y_pais)

            y_offset = - (len(nos) - 1) * y_spacing / 2
            x_pos = nivel * x_spacing
            if nivel == 1:
                fx = x_pos

            for i, n in enumerate(nos):
                y_pos = y_offset + i * y_spacing
                pos[n] = (x_pos, y_pos)
        
        return pos, fx
    
    pos, fx = criar_layout_hierarquico(G)
    
    tamanhos = []
    for node in G.nodes():
        valor = G.nodes[node]['valor']
        tamanho = (valor / valor_total) * 500 + 100
        tamanhos.append(tamanho)
    
    cores_nos = []
    for node in G.nodes():
        categoria_composta = G.nodes[node].get('categoria_cmp')
        cor = mapeamento_categorias.get(categoria_composta, 'gray')
        cores_nos.append(cor)

    cores_edges = []
    espessuras = []
    for u, v in G.edges():
        peso = G[u][v]['peso']
        espessura = max(peso * 12 + 1, 0.5)
        espessuras.append(espessura)

        cor = "#228B22" if ((v in ['NO', '3-CONCILIADO', 'CFOP INVESTIMENTO']) or( v[:5] in ['REGRA', 'NO_RE'])) else "#960018"
        cores_edges.append(cor)
    
    max_nos = max(
                    len([n for n in G.nodes() if G.nodes[n]['nivel'] == nivel])
                    for nivel in set(nx.get_node_attributes(G, 'nivel').values())
                )

    fig, ax = plt.subplots(figsize=(18, max_nos * 0.2))
    
    nx.draw_networkx_nodes(G, pos, node_size=tamanhos, node_color=cores_nos, alpha=0.7, edgecolors='#ffffff', linewidths=1.5, ax=ax)
    nx.draw_networkx_edges(G, pos, width=espessuras, alpha=0.5, edge_color=cores_edges, arrowstyle='-|>', 
                           connectionstyle="arc3,rad=0.05", arrowsize=15, ax=ax)
    labels = {node: G.nodes[node]['label'] for node in G.nodes()}
    for node, (x, y) in pos.items():
        if x <= fx:
            ax.text(x, y, labels[node], fontsize=8, ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    edge_labels = {}
    for u, v in G.edges():
        proporcao = G[u][v]['peso']
        if proporcao > 0.001:
            edge_labels[(u, v)] = f"{G[u][v]['label']}".replace(".",",")
    
    if edge_labels:
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, ax=ax)
    ax.axis('off')
    all_x = [pos[node][0] for node in G.nodes()]
    all_y = [pos[node][1] for node in G.nodes()]
    ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
    ax.set_ylim(min(all_y) - 1, max(all_y) + 1)
    plt.tight_layout()
    col1, col2 = st.columns([4,1], gap='small')
    with col1:
        st.subheader("Grafo")
        st.pyplot(fig)
    with col2:
        st.subheader("Estatísticas do Grafo")
        st.metric("Valor Total", f"{valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.metric("Total de Nós", len(G.nodes()))
        st.metric("Total de Arestas", len(G.edges()))
    st.subheader("Legenda")
    categorias_por_nivel = defaultdict(list)
    categorias_por_nivel1 = defaultdict(list)
    for node in G.nodes():
        nivel = G.nodes[node]['nivel']
        if nivel == 0:
            continue
        categoria = G.nodes[node].get('categoria_cmp')
        if categoria not in categorias_por_nivel[nivel]:
            lmp = categoria.rfind("→")
            categorias_por_nivel[nivel].append(categoria)
            categorias_por_nivel1[nivel].append(categoria[lmp+1:])
    
    for nivel in sorted(categorias_por_nivel.keys()):
        if nivel == 0:
            continue
        st.markdown(f"**Nível {nivel}:**")
        with st.container(border=True):
            cols = st.columns(4)
            for i, categoria in enumerate(sorted(categorias_por_nivel[nivel])):
                col_idx = i % 4
                if categoria in mapeamento_categorias:
                    cor_hex = mcolors.to_hex(mapeamento_categorias[categoria])
                    idx = categorias_por_nivel[nivel].index(categoria)
                    vlx = categorias_por_nivel1[nivel][idx]
                    with cols[col_idx]:
                        st.markdown(f"<span style='color:{cor_hex}; font-weight:bold'>■</span> {vlx}", 
                                unsafe_allow_html=True)
    col1a, col2a, col3a = st.columns([3,0.5,3], gap='small')
    with col1a:
        st.subheader("Dados dos Nós")
        dados_nos = []
        for node in G.nodes():
            dados_nos.append({
                'Nó': node,
                'Nível': G.nodes[node]['nivel'],
                'Valor': G.nodes[node]['valor'],
                'Proporção do Total': f"{(G.nodes[node]['valor'] / valor_total * 100):.1f}%"
            })
        st.dataframe(pd.DataFrame(dados_nos))

    with col3a:    
        st.subheader("Dados das Arestas")
        dados_arestas = []
        for u, v in G.edges():
            dados_arestas.append({
                'De': u,
                'Para': v,
                'Proporção': G[u][v]['label'],
                'Valor Pai': G.nodes[u]['valor'],
                'Valor Filho': G.nodes[v]['valor']
            })
        st.dataframe(pd.DataFrame(dados_arestas))
    
    return G
```

</details>

---

<a id="funcao-47"></a>

## bsc_dados_Cd_CC

Processa e normaliza dados de contas correntes (CC) para um banco específico em um determinado ano.

A função lê arquivos CSV, sanitiza-os, processa os dados e salva o resultado em uma tabela SQL. Ela suporta múltiplas encodings e trata erros de codificação ao ler os arquivos.

### Assinatura

```python
def bsc_dados_Cd_CC(bd, empresa, ano1, lst_lcto = None, TIP = None, REF = False, st=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `bd` | `Não especificado` | Conexão com o banco de dados onde os dados serão armazenados. |
| `empresa` | `Não especificado` | Identificador da empresa para filtrar os dados. |
| `ano1` | `Não especificado` | Ano para o qual os dados serão processados e armazenados. |
| `lst_lcto` | `Não especificado` | Lista de contas correntes a serem processadas. Se for uma lista com um único elemento, deve estar entre parênteses. |
| `TIP` | `Não especificado` | Tipo de tabela onde os dados serão armazenados. |
| `REF` | `Não especificado` | Indica se a operação é uma referência (opcional). |
| `st` | `Não especificado` | Objeto Streamlit para interação com a interface do usuário. |

### Retorno

**Tipo:** `Não especificado`

DataFrame contendo os dados processados e normalizados, ou um DataFrame vazio se nenhum dado for encontrado.

### Exceções

- **`UserWarning`**: Lancado quando ocorre um problema de codificação no arquivo CSV.

### Dependências

- `{'nome': 'UTILS.bsc_cd_aneel', 'categoria': 'import'}`
- `{'nome': 'UTILS.existe_tabela', 'categoria': 'import'}`
- `{'nome': 'UTILS.max_arq', 'categoria': 'import'}`
- `{'nome': 'UTILS.sanear_csv', 'categoria': 'import'}`
- `{'nome': 'duckdb', 'categoria': 'import'}`
- `{'nome': 'pandas', 'categoria': 'import'}`
- `{'nome': 'streamlit', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def bsc_dados_Cd_CC(bd, empresa, ano1, lst_lcto = None, TIP = None, REF = False, st=None):
    
    if existe_tabela(f"TBL_LCMT_CVA_{TIP}_{ano1}", bd) and (not REF):
        sSQL = f"SELECT * FROM TBL_LCMT_CVA_{TIP}_{ano1}"
        return pd.read_sql(sSQL,bd)

    df_PART = pd.DataFrame()
    dt_ARQ = max_arq('LD_PTD', bd, empresa)
    dt_ARQ1 = max_arq('LD_LCMTO', bd, empresa)
    Cd_EMP = f"00000{bsc_cd_aneel(empresa)}"[-5:]
    if len(lst_lcto) == 1:
        filtro_lcto = f"({lst_lcto[0]})"
    else:
        filtro_lcto = lst_lcto
    
    erro = {}
    # antes de importar é relevante sanear arquivos, pode haver problemas de sistemas legados
    # ao exportar o arquivo, gerando linhas malformatadas. Iremos limpar os campos para evitar
    # problemas de leitura, mantendo o arquivo original e as linhas alteradas para rastreabilidade

    sanear_csv(
                        diretorio = f"{st.session_state.tra_dir}/SDI_001",
                        arq = f"LD_LCMTO_{Cd_EMP}_{dt_ARQ1}.csv", st = st                                    
                    )
    sanear_csv(
                        diretorio = f"{st.session_state.tra_dir}/SDI_001",
                        arq = f"LD_PTD_{Cd_EMP}_{dt_ARQ}.csv" , st = st                                  
                    )
    
    with duckdb.connect() as con:
        for enc in ['CP1252', 'latin-1', 'utf-8']:
            try:
                SQLq = f"""
                            WITH tbl_temp_lcmto AS (
                            SELECT 
                                NUM_LCTO,
                                Dt_LCMTO,
                                IND_LCMTO,
                                VL_LCMTO
                            FROM (
                                SELECT 
                                    NUM_LCTO,
                                    Dt_LCMTO,
                                    IND_LCMTO,
                                    Id_SEQ_LCMTO,
                                    VL_LCMTO,
                                    ROW_NUMBER() OVER (
                                        PARTITION BY NUM_LCTO 
                                        ORDER BY Id_SEQ_LCMTO ASC
                                    ) AS row_num
                                FROM read_csv(
                                    '{st.session_state.tra_dir}\\SDI_001\\LD_LCMTO_{Cd_EMP}_{dt_ARQ1}.csv',
                                    delim='|',
                                    null_padding=true, 
                                    encoding='{enc}',
                                    parallel=true,
                                    all_varchar=true
                                )
                            )
                            WHERE row_num = 1
                        )

                        SELECT 
                            REPLACE(CAST(t1.Cd_CC AS STRING),'.0','') AS COD_CTA, 
                            t1.COD_CCUS, 
                            CAST(REPLACE(t1.VL_DC,',','.') AS FLOAT) AS VL_DC, 
                            t1.IND_DC, 
                            '' AS NUM_ARQ, 
                            '' AS COD_HIST_PAD, 
                            t1.HIST AS COD_HIST, 
                            '' AS COD_PART, 
                            REPLACE(CAST(t2.NUM_LCTO AS STRING),'.0','') AS NUM_LCTO, 
                            t2.Dt_LCMTO, 
                            CAST(REPLACE(t2.VL_LCMTO,',','.') AS FLOAT) AS VL_LCTO, 
                            t2.IND_LCMTO AS IND_LCTO, 
                            '' AS DT_LCTO_EXT, 
                            t2.Dt_LCMTO AS Dt_REF
                        FROM read_csv(
                                '{st.session_state.tra_dir}\\SDI_001\\LD_PTD_{Cd_EMP}_{dt_ARQ}.csv',
                                delim='|',
                                null_padding=true, 
                                encoding='{enc}',
                                parallel=true,
                                all_varchar=true
                        ) t1
                        LEFT JOIN tbl_temp_lcmto t2 
                            ON t1.NUM_LCTO = t2.NUM_LCTO
                        WHERE REPLACE(CAST(t1.Cd_CC AS STRING),'.0','') IN {filtro_lcto}
                    """
                df_PART = con.sql(SQLq).df()
                break
            except Exception as e:
                erro[enc] = e
                df_PART= pd.DataFrame()

    
    if len(df_PART)==0:
        st.text(erro)
        raise UserWarning("Você tem problema de codificação do arquivo.")

    def ajustar_data(data_str):
        if "/" in data_str:
            partes = data_str.split('/')
        else:
            partes = data_str.split('-')
        ano = partes[0]
        mes = partes[1].zfill(2)
        return f"{ano}/{mes}/01"
    
    if len(df_PART)>0:
        df_PART['Dt_REF'] = df_PART['Dt_REF'].ffill()
        df_PART['Dt_REF'] = df_PART['Dt_REF'].astype(str).apply(ajustar_data)
        df_PART['Dt_REF'] = pd.to_datetime(df_PART['Dt_REF'], format='%Y/%m/%d', errors='coerce')
        df_PART['Dt_REF'] = df_PART['Dt_REF'].ffill()
        df_PART[df_PART['Dt_REF'].dt.year == ano1].to_sql(f"TBL_LCMT_CVA_{TIP}_{ano1}", bd, if_exists='replace', index=False)
        return df_PART[df_PART['Dt_REF'].dt.year==ano1]
    else:
        return (pd.DataFrame(columns=['COD_CTA', 'COD_CCUS', 'VL_DC', 'IND_DC', 'NUM_ARQ', 'COD_HIST_PAD', 
                            'COD_HIST', 'COD_PART', 'NUM_LCTO', 'Dt_LCMTO', 'VL_LCTO', 'IND_LCTO', 
                            'DT_LCTO_EXT', 'Dt_REF', 'FLG_CX', 'OBS_LCTO']))
```

</details>

---

<a id="funcao-48"></a>

## comparar_componentes

Compara diferentes componentes e bases de dados em um DataFrame.

A função compara valores entre diferentes componentes e bases, calculando diferenças e critérios de desvio. Ela também gera mensagens de alerta para colunas faltantes e cria um relatório com estatísticas dos resultados.

### Assinatura

```python
# Consulte o código-fonte de comparar_componentes
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `Não especificado` | DataFrame contendo os dados a serem comparados. |
| `componentes` | `Não especificado` | Lista de componentes a serem comparados. |
| `bases` | `Não especificado` | Lista de bases de dados a serem comparadas. |
| `criterio` | `Não especificado` | Criterio de desvio para considerar um valor como fora do padrão. |
| `st` | `Não especificado` | Objeto Streamlit para exibir mensagens de alerta. |

### Retorno

**Tipo:** `Não especificado`

Um DataFrame contendo os resultados da comparação e um segundo DataFrame com estatísticas dos resultados.

### Dependências

- `numpy`
- `pandas`
- `streamlit`

<details>
<summary>Visualizar código-fonte</summary>

```python
def comparar_componentes(df, 
                         componentes = ['UC', 'COM', 'CA', 'JOA'], 
                         bases = ['AVAL', 'CONS', 'TOT', 'TOT_ROA'],
                         criterio=0.01,
                         st = None):
    
    def con_str(num):
        return f"{num:,.2f}".replace(",","x").replace(".",",").replace("x",".")
    
    colunas_aval = [f"VL_{comp}_AVAL" for comp in componentes if f"VL_{comp}_AVAL" in df.columns]
    colunas_cons = [f"VL_{comp}_CONS" for comp in componentes if f"VL_{comp}_CONS" in df.columns]
    colunas_tot = [f"VL_{comp}_TOT" for comp in componentes if f"VL_{comp}_TOT" in df.columns]
    colunas_tot_roa = [f"VL_{comp}_TOT_ROA" for comp in componentes if f"VL_{comp}_TOT_ROA" in df.columns]
    
    if colunas_aval and colunas_cons:
        df['TOTAL_AVAL'] = df[colunas_aval].sum(axis=1)
        df['TOTAL_CONS'] = df[colunas_cons].sum(axis=1)
        dif_total_aval_cons = (df['TOTAL_AVAL'] - df['TOTAL_CONS']).abs()
        crit_total_aval_cons = dif_total_aval_cons > criterio
        
        df['TESTE_TOTAL_AVAL_CONS'] = np.where(
                                                crit_total_aval_cons,
                                                f"TOTAL AVAL ≠ CONS",
                                                "TOTAL AVAL = CONS"
                                             )
    
    if colunas_tot and colunas_tot_roa:
        df['TOTAL_TOT'] = df[colunas_tot].sum(axis=1)
        df['TOTAL_TOT_ROA'] = df[colunas_tot_roa].sum(axis=1)
        dif_total_tot_roa = (df['TOTAL_TOT'] - df['TOTAL_TOT_ROA']).abs()
        crit_total_tot_roa = dif_total_tot_roa > criterio
        
        df['TESTE_TOTAL_TOT_ROA'] = np.where(
                                                crit_total_tot_roa,
                                                f"TOTAL TOT ≠ TOT_ROA",
                                                "TOTAL  TOT = TOT_ROA"
                                            )
        
    resultados_componentes = []
    for componente in componentes:
        colunas_necessarias = [f"VL_{componente}_{base}" for base in bases]
        colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
        
        if colunas_faltantes:
            st.warning(f"Componente {componente} - Colunas faltantes: {colunas_faltantes}")
            continue
        
        dif1 = (df[f"VL_{componente}_{bases[0]}"].abs() - df[f"VL_{componente}_{bases[1]}"].abs()).abs()
        dif2 = (df[f"VL_{componente}_{bases[2]}"].abs() - df[f"VL_{componente}_{bases[3]}"].abs()).abs()

        crit1 = dif1 > criterio
        crit2 = dif2 > criterio

        total_itens = len(df)
        itens_crit1 = crit1.sum()
        itens_crit2 = crit2.sum()
        itens_ambos = (crit1 & crit2).sum()

        mensagens = []

        for idx in df.index:
            msg_parts = []
            
            if crit1[idx]:
                msg_parts.append(f"Incremental ≠ ROS_VAL (dif: {con_str(dif1[idx])}, dist_crit: {con_str(dif1[idx]-criterio)})")
            
            if crit2[idx]:
                msg_parts.append(f"ROA ≠ ROS_VAL (dif: {con_str(dif2[idx])}, dist_crit: {con_str(dif2[idx]-criterio)})")
            
            if msg_parts:
                mensagem = " | ".join(msg_parts)
            else:
                mensagem = "Valores consistentes"
            
            mensagens.append(mensagem)
        
        df[f'AVAL_{componente}'] = mensagens
        df[f'DIF_{componente}_{bases[0]}_{bases[1]}'] = dif1
        df[f'DIF_{componente}_{bases[2]}_{bases[3]}'] = dif2
        df[f'DIST_CRIT1_{componente}'] = dif1 - criterio
        df[f'DIST_CRIT2_{componente}'] = dif2 - criterio
        
        stats = {
                    'Componente': componente,
                    'Total_Itens': total_itens,
                    'Itens_Crit1': itens_crit1,
                    'Itens_Crit2': itens_crit2, 
                    'Itens_Ambos_Crit': itens_ambos,
                    'Pct_Crit1': (itens_crit1 / total_itens * 100),
                    'Pct_Crit2': (itens_crit2 / total_itens * 100),
                    'Media_Dif1': dif1.mean(),
                    'Max_Dif1': dif1.max(),
                    'Media_Dif2': dif2.mean(),
                    'Max_Dif2': dif2.max()
                }
        
        resultados_componentes.append(stats)
    
    df_relatorio = pd.DataFrame(resultados_componentes)
    
    return df, df_relatorio
```

</details>

---

<a id="funcao-49"></a>

## _garante_dir_saida

Garante que o diretório de saída existe.

Verifica se o diretório especificado existe e, caso contrário, cria-o. Aceita tanto strings quanto objetos `Path` do módulo `pathlib` como entrada.

### Assinatura

```python
def _garante_dir_saida(dir_saida: str | Path) -> Path:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `dir_saida` | `str \| Path` | Caminho para o diretório de saída. Pode ser uma string ou um objeto `Path`. |

### Retorno

**Tipo:** `Path`

Objeto `Path` representando o diretório garantido.

### Dependências

- `pathlib.Path`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _garante_dir_saida(dir_saida: str | Path) -> Path:
    path = Path(dir_saida)
    path.mkdir(parents=True, exist_ok=True)
    return path
```

</details>

---

<a id="funcao-50"></a>

## _lognormal_mu_media

Calcula o valor de mu para uma distribuição log-normal com base na média e no desvio padrão.

Esta função ajusta a média da distribuição log-normal, garantindo que seja maior ou igual a um valor mínimo (1e-9), e então calcula o parâmetro mu usando a fórmula inversa do lognormal.

### Assinatura

```python
def _lognormal_mu_media(vl_media: float, sigma: float) -> float:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `vl_media` | `float` | A média da distribuição log-normal desejada. |
| `sigma` | `float` | O desvio padrão da distribuição log-normal desejada. |

### Retorno

**Tipo:** `float`

O valor de mu calculado para a distribuição log-normal.

### Dependências

- `math`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _lognormal_mu_media(vl_media: float, sigma: float) -> float:
    vl_media = max(vl_media, 1e-9)
    return math.log(vl_media) - (sigma**2) / 2.0
```

</details>

---

<a id="funcao-51"></a>

## _std_seguro

Calcula a desvio padrão amostral de uma série de dados.

Computa o desvio padrão amostral de uma série de dados utilizando a função `std` do pandas, com um grau de liberdade (ddof) igual a 1. Se a série tiver apenas um elemento ou for vazia, retorna 0.0. Caso o resultado seja NaN, também retorna 0.0.

### Assinatura

```python
def _std_seguro(series: pd.Series) -> float:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `series` | `pd.Series` | Série de dados para a qual será calculado o desvio padrão amostral. |

### Retorno

**Tipo:** `float`

Desvio padrão amostral da série de dados.

### Dependências

- `numpy`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _std_seguro(series: pd.Series) -> float:
    val = float(series.std(ddof=1)) if len(series) > 1 else 0.0
    if np.isnan(val):
        return 0.0
    return val
```

</details>

---

<a id="funcao-52"></a>

## df_dict_to_json

Converte colunas de um DataFrame que contêm dicionários ou listas em formato JSON.

A função itera sobre cada coluna do DataFrame e, se a coluna conter valores do tipo dicionário ou lista, os converte em uma string JSON. Caso contrário, o valor é mantido inalterado.

### Assinatura

```python
def df_dict_to_json(df: pd.DataFrame) -> pd.DataFrame:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `pd.DataFrame` | DataFrame contendo colunas que podem ser dicionários ou listas. |

### Retorno

**Tipo:** `pd.DataFrame`

Novo DataFrame com as mesmas colunas, mas onde os valores de dicionário e lista foram convertidos em strings JSON.

### Dependências

- `json`

<details>
<summary>Visualizar código-fonte</summary>

```python
def df_dict_to_json(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    for col in df_out.columns:
        if df_out[col].apply(lambda x: isinstance(x, (dict, list))).any():
            df_out[col] = df_out[col].apply(
                                                lambda x: json.dumps(x, ensure_ascii=False)
                                                if isinstance(x, (dict, list))
                                                else x
                                            )
    return df_out
```

</details>

---

<a id="funcao-53"></a>

## df_json_to_dict

Converte colunas de um DataFrame que contêm JSON em dicionários Python.

A função itera sobre cada coluna do DataFrame e, se a coluna for do tipo object (string), tenta analisar o conteúdo como JSON. Se a análise for bem-sucedida, a string é convertida em um dicionário; caso contrário, o valor original é mantido.

### Assinatura

```python
def df_json_to_dict(df: pd.DataFrame) -> pd.DataFrame:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `pd.DataFrame` | DataFrame contendo colunas que podem ser JSON. |

### Retorno

**Tipo:** `pd.DataFrame`

Novo DataFrame com as colunas de JSON convertidas em dicionários Python.

### Dependências

- `json`

<details>
<summary>Visualizar código-fonte</summary>

```python
def df_json_to_dict(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    for col in df_out.columns:
        if df_out[col].dtype == object:
            def try_parse(x):
                if isinstance(x, str):
                    x_str = x.strip()
                    if (x_str.startswith("{") and x_str.endswith("}")) or \
                       (x_str.startswith("[") and x_str.endswith("]")):
                        try:
                            return json.loads(x_str)
                        except Exception:
                            return x
                return x
            df_out[col] = df_out[col].apply(try_parse)
    return df_out
```

</details>

---

<a id="funcao-54"></a>

## salvar_df

Salva um DataFrame em formato pickle.

Cria o diretório de destino, se necessário, e salva o DataFrame fornecido no caminho especificado em formato pickle.

### Assinatura

```python
def salvar_df(df: pd.DataFrame, caminho: str | Path):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `pd.DataFrame` | DataFrame a ser salvo. |
| `caminho` | `str \| Path` | Caminho onde o DataFrame será salvo, pode ser uma string ou um objeto Path. |

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def salvar_df(df: pd.DataFrame, caminho: str | Path):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_pickle(caminho)
```

</details>

---

<a id="funcao-55"></a>

## carregar_df

Carrega um DataFrame a partir de um arquivo pickle.

Lê um arquivo pickle e retorna o conteúdo como um DataFrame do pandas.

### Assinatura

```python
def carregar_df(caminho: str | Path) -> pd.DataFrame:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `caminho` | `str \| Path` | Caminho para o arquivo pickle que será carregado. |

### Retorno

**Tipo:** `pd.DataFrame`

DataFrame do pandas contendo os dados carregados.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def carregar_df(caminho: str | Path) -> pd.DataFrame:
    return pd.read_pickle(caminho)
```

</details>

---

<a id="funcao-56"></a>

## consultar_empresa

Consulta informações de uma empresa pelo CNPJ.

Realiza uma requisição à API BrasilAPI para obter dados sobre a empresa associada ao CNPJ fornecido. O CNPJ é sanitizado para remover caracteres não numéricos antes da consulta.

### Assinatura

```python
def consultar_empresa(cnpj):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cnpj` | `Não especificado` | CNPJ da empresa a ser consultada. |

### Retorno

**Tipo:** `Não especificado`

Dados da empresa em formato JSON, ou uma mensagem de erro se a consulta falhar.

### Exceções

- **`requests.exceptions.HTTPError`**: Quando ocorre um erro HTTP durante a requisição à API.

### Dependências

- `requests`

<details>
<summary>Visualizar código-fonte</summary>

```python
def consultar_empresa(cnpj):

    cnpj = "".join(filter(str.isdigit, cnpj))
    
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        dados = response.json()
        
        
        return dados
    except requests.exceptions.HTTPError as err:
        return f"Erro na consulta: {err}"
```

</details>

---

<a id="funcao-57"></a>

## decorador

Decorator que mede e registra o tempo de execução de uma função.

O decorator `decorador` envolve a função fornecida, medindo seu tempo de execução e registrando tanto os sucessos quanto os erros em um logger. Ele também captura informações sobre o arquivo chamador da função.

### Assinatura

```python
def decorador(funcao):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `funcao` | `Não especificado` | Função que será decorada e cujo tempo de execução será medido. |

### Retorno

**Tipo:** `Não especificado`

A função original, com o tempo de execução registrado.

### Exceções

- **`Exception`**: Qualquer exceção lançada pela função decorada será re Lançada após ser registrada no logger.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def decorador(funcao):
        @wraps(funcao)
        def wrapper(*args, **kwargs):
            inicio = time.perf_counter()
            stack = inspect.stack()
            caller_frame = stack[1]
            caminho_arquivo = caller_frame.filename
            nome_arquivo = os.path.basename(caminho_arquivo)
            try:
                resultado = funcao(*args, **kwargs)
                duracao = time.perf_counter() - inicio
                logger.info(f"SUCESSO em '{funcao.__name__}', chamado por {nome_arquivo}: {duracao:.4f}s")    
                return resultado
            except Exception as e:
                duracao = time.perf_counter() - inicio
                logger.error(f"ERRO em '{funcao.__name__}' após {duracao:.4f}s | Detalhe: {e}")
                raise e       
        return wrapper
```

</details>

---

<a id="funcao-58"></a>

## get_tag

Obtém a representação imprimível de uma tag pelo nome.

Retorna a representação imprimível da tag especificada, ou um valor padrão se a tag não for encontrada no dicionário 'tags'.

### Assinatura

```python
def get_tag(nome, default=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `nome` | `Não especificado` | Nome da tag que será buscada. |
| `default` | `Não especificado` | Valor padrão a ser retornado se a tag não for encontrada. |

### Retorno

**Tipo:** `Não especificado`

Representação imprimível da tag ou o valor padrão fornecido.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def get_tag(nome, default=None):
        return tags[nome].printable if nome in tags else default
```

</details>

---

<a id="funcao-59"></a>

## obter_fatores

Obtém fatores de contabilidade com base na natureza e código da conta.

Determina os fatores de contabilidade (fator1, fator2, fator3, tipo) com base na natureza da operação e no código da conta. Os valores padrão são geralmente positivos e o tipo é 'C' (Crédito), exceto quando a natureza for '01' ou '04' e o código da conta começar por '7' ou '5', respectivamente, que resultam em um débito ('D').

### Assinatura

```python
def obter_fatores(natureza, cod_cta):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `natureza` | `Não especificado` | Natureza da operação contábil. |
| `cod_cta` | `Não especificado` | Código da conta contábil. |

### Retorno

**Tipo:** `Não especificado`

Quatro valores (fator1, fator2, fator3, tipo) que representam os fatores de contabilidade.

### Dependências

- `cod_cta.startswith`

<details>
<summary>Visualizar código-fonte</summary>

```python
def obter_fatores(natureza, cod_cta):
        if natureza == '01':
            return -1, -1, 1, 'D'
        elif natureza in ['02', '03']:
            return 1, -1, 1, 'C'
        elif natureza == '04':
            return (-1, -1, 1, 'D') if cod_cta.startswith('7') else (1, -1, 1, 'C')
        elif natureza == '05':
            return (-1, -1, 1, 'D') if cod_cta.startswith('5') else (1, -1, 1, 'C')
        return 1, -1, 1, 'C'
```

</details>

---

<a id="funcao-60"></a>

## ensure_cols

Garante a presença de todas as colunas em uma DataFrame.

A função verifica se cada coluna especificada na lista `cols` existe na DataFrame `df`. Se uma coluna estiver ausente, ela é adicionada à DataFrame, preenchendo todos os valores com `pd.NA`. A função retorna uma nova DataFrame contendo apenas as colunas que foram verificadas e eventualmente adicionadas.

### Assinatura

```python
def ensure_cols(df, cols):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `Não especificado` | DataFrame na qual as colunas serão verificadas e eventualmente adicionadas. |
| `cols` | `Não especificado` | Lista de strings representando os nomes das colunas que devem ser garantidas na DataFrame. |

### Retorno

**Tipo:** `Não especificado`

Nova DataFrame contendo apenas as colunas verificadas e eventualmente adicionadas.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def ensure_cols(df, cols):
        """
            Função para garantir a presença de todas as colunas em uma DataFrame.

            Argumentos:
            - df (DataFrame): A DataFrame na qual as colunas serão verificadas e eventualmente adicionadas.
            - cols (list): Uma lista de strings representando os nomes das colunas que devem ser garantidas na DataFrame.

            Processo:
            - Para cada coluna em `cols`, a função verifica se ela já existe na DataFrame `df`.
            - Se uma coluna estiver ausente, a função adiciona essa coluna à DataFrame, preenchendo todos os valores com `pd.NA`.
            - Após o processamento, a função retorna uma nova DataFrame contendo apenas as colunas que foram verificadas e eventualmente adicionadas.

            Útil:
            - É especialmente útil quando você precisa garantir que uma DataFrame contenha todas as colunas necessárias antes de realizar operações de análise ou processamento, por exemplo, para modelagem estatística ou machine learning.
        """
        for c in cols:
            if c not in df.columns:
                df[c] = pd.NA
        return df[cols]
```

</details>

---

<a id="funcao-61"></a>

## localizar_pipes_excedentes

Localiza linhas com mais pipes do que o esperado em um arquivo binário.

A função lê um arquivo binário e verifica se cada linha contém mais pipes (|) do que o número esperado. Se encontrar mais pipes do que o limite estabelecido, adiciona a linha ao resultado com detalhes sobre o erro. O processo é interrompido quando o limite de erros é atingido.

### Assinatura

```python
# Consulte o código-fonte de localizar_pipes_excedentes
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `caminho` | `Não especificado` | Caminho para o arquivo binário que será lido. |
| `qtd_pipes_esperada` | `Não especificado` | Quantidade de pipes esperados por linha. |
| `limite` | `Não especificado` | Limite máximo de erros a serem retornados. O padrão é 100. |

### Retorno

**Tipo:** `Não especificado`

Lista de dicionários contendo detalhes dos erros encontrados, incluindo linha, número de pipes, esperado e trecho da linha.

### Dependências

- `enumerate`
- `erros.append`
- `len`
- `linha.count`
- `open`

<details>
<summary>Visualizar código-fonte</summary>

```python
def localizar_pipes_excedentes(
                                    caminho,
                                    qtd_pipes_esperada,
                                    limite=100,
                                ):
        erros = []

        with open(caminho, "rb") as arquivo:
            for numero_linha, linha in enumerate(arquivo, start=1):
                qtd_pipes = linha.count(b"|")

                if qtd_pipes > qtd_pipes_esperada:
                    erros.append({
                                    "linha": numero_linha,
                                    "pipes": qtd_pipes,
                                    "esperado": qtd_pipes_esperada,
                                    "trecho": linha[:500],
                                })

                    if len(erros) >= limite:
                        break

        return erros
```

</details>

---

<a id="funcao-62"></a>

## testar_csv

Testa um arquivo CSV retornando o número de linhas.

Realiza a leitura de um arquivo CSV utilizando a biblioteca DuckDB e retorna o número total de linhas no arquivo. O arquivo é lido com delimitador '|', considerando que tem cabeçalho e todas as colunas são tratadas como strings.

### Assinatura

```python
def testar_csv(caminho, encoding):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `caminho` | `Não especificado` | Caminho do arquivo CSV a ser testado. |
| `encoding` | `Não especificado` | Codificação do arquivo CSV. |

### Retorno

**Tipo:** `Não especificado`

Número de linhas no arquivo CSV.

### Dependências

- `duckdb`

<details>
<summary>Visualizar código-fonte</summary>

```python
def testar_csv(caminho, encoding):
        with duckdb.connect() as con:
            return con.execute(
                                    """
                                    SELECT COUNT(*)
                                    FROM read_csv(
                                        ?,
                                        delim = '|',
                                        header = true,
                                        encoding = ?,
                                        all_varchar = true,
                                        parallel = false,
                                        null_padding = true,
                                        strict_mode = false,
                                        ignore_errors = false
                                    )
                                    """,
                                    [str(caminho), encoding],
                                ).fetchone()[0]
```

</details>

---

<a id="funcao-63"></a>

## ajustar_data

Ajusta uma data para o primeiro dia do mês.

Recebe uma string de data no formato 'YYYY-MM-DD' ou 'YYYY/MM/DD' e retorna a mesma data ajustada para o primeiro dia do mês, no formato 'YYYY/MM/01'.

### Assinatura

```python
def ajustar_data(data_str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `data_str` | `Não especificado` | String representando uma data no formato 'YYYY-MM-DD' ou 'YYYY/MM/DD'. |

### Retorno

**Tipo:** `Não especificado`

Data ajustada para o primeiro dia do mês, no formato 'YYYY/MM/01'.

### Dependências

- `data_str.split`
- `zfill`

<details>
<summary>Visualizar código-fonte</summary>

```python
def ajustar_data(data_str):
        if "/" in data_str:
            partes = data_str.split('/')
        else:
            partes = data_str.split('-')
        ano = partes[0]
        mes = partes[1].zfill(2)
        return f"{ano}/{mes}/01"
```

</details>

---

<a id="funcao-64"></a>

## criar_layout_hierarquico

Cria um layout hierárquico para um grafo.

Organiza os nós de um grafo em uma estrutura hierárquica, onde cada nível representa uma profundidade diferente. Os nós são posicionados com base na sua hierarquia e nas posições dos seus pais.

### Assinatura

```python
def criar_layout_hierarquico(G):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `G` | `Não especificado` | O grafo a ser layoutizado, onde cada nó deve ter um atributo 'nivel' que indica sua profundidade na hierarquia. |

### Retorno

**Tipo:** `Não especificado`

Um dicionário contendo as posições (x, y) de cada nó no layout e a posição final do primeiro nó do nível 1.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def criar_layout_hierarquico(G):
        pos = {}
        niveis = {}
        
        for node in G.nodes():
            nivel = G.nodes[node]['nivel']
            if nivel not in niveis:
                niveis[nivel] = []
            niveis[nivel].append(node)
        
        x_spacing = 1.25
        y_spacing = 0.6

        def media_y_pais(n):
            pais = list(G.predecessors(n))
            if not pais:
                return 0
            return sum(pos[p][1] for p in pais if p in pos) / len(pais)
        
        for nivel in sorted(niveis):
            nos = niveis[nivel]

            if nivel > 0:
                nos = sorted(nos, key=media_y_pais)

            y_offset = - (len(nos) - 1) * y_spacing / 2
            x_pos = nivel * x_spacing
            if nivel == 1:
                fx = x_pos

            for i, n in enumerate(nos):
                y_pos = y_offset + i * y_spacing
                pos[n] = (x_pos, y_pos)
        
        return pos, fx
```

</details>

---

<a id="funcao-65"></a>

## ajustar_data

Ajusta uma data para o primeiro dia do mês.

Recebe uma string de data no formato 'YYYY-MM-DD' ou 'YYYY/MM/DD' e retorna a mesma data ajustada para o primeiro dia do mês, no formato 'YYYY/MM/01'.

### Assinatura

```python
def ajustar_data(data_str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `data_str` | `Não especificado` | String representando uma data no formato 'YYYY-MM-DD' ou 'YYYY/MM/DD'. |

### Retorno

**Tipo:** `Não especificado`

Data ajustada para o primeiro dia do mês, no formato 'YYYY/MM/01'.

### Dependências

- `data_str.split`
- `zfill`

<details>
<summary>Visualizar código-fonte</summary>

```python
def ajustar_data(data_str):
        if "/" in data_str:
            partes = data_str.split('/')
        else:
            partes = data_str.split('-')
        ano = partes[0]
        mes = partes[1].zfill(2)
        return f"{ano}/{mes}/01"
```

</details>

---

<a id="funcao-66"></a>

## con_str

Converte um número em uma string formatada com duas casas decimais, substituindo vírgulas por pontos e vice-versa.

A função formata o número fornecido para ter duas casas decimais. Em seguida, realiza a troca de vírgulas por pontos e vice-versa, retornando o resultado como uma string.

### Assinatura

```python
def con_str(num):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `num` | `Não especificado` | Número que será formatado. |

### Retorno

**Tipo:** `Não especificado`

String formatada com duas casas decimais e troca de vírgulas por pontos e vice-versa.

### Dependências

- `replace`

<details>
<summary>Visualizar código-fonte</summary>

```python
def con_str(num):
        return f"{num:,.2f}".replace(",","x").replace(".",",").replace("x",".")
```

</details>

---

<a id="funcao-67"></a>

## wrapper

Função decoradora que mede e registra o tempo de execução de outra função.

A função `wrapper` é um decorador que envolve outra função (`funcao`) para medir seu tempo de execução. Ele também registra informações sobre a chamada, incluindo o nome do arquivo e o tempo gasto na execução. Em caso de erro, ele registra uma mensagem de erro com detalhes.

### Assinatura

```python
def wrapper(*args, **kwargs):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `args` | `Não especificado` | Argumentos posicionais passados para a função decorada. |
| `kwargs` | `Não especificado` | Argumentos nomeados passados para a função decorada. |

### Retorno

**Tipo:** `Não especificado`

O resultado da execução da função decorada (`funcao`).

### Exceções

- **`Exception`**: Qualquer exceção lançada pela função decorada é re-lançada após ser registrada.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def wrapper(*args, **kwargs):
            inicio = time.perf_counter()
            stack = inspect.stack()
            caller_frame = stack[1]
            caminho_arquivo = caller_frame.filename
            nome_arquivo = os.path.basename(caminho_arquivo)
            try:
                resultado = funcao(*args, **kwargs)
                duracao = time.perf_counter() - inicio
                logger.info(f"SUCESSO em '{funcao.__name__}', chamado por {nome_arquivo}: {duracao:.4f}s")    
                return resultado
            except Exception as e:
                duracao = time.perf_counter() - inicio
                logger.error(f"ERRO em '{funcao.__name__}' após {duracao:.4f}s | Detalhe: {e}")
                raise e
```

</details>

---

<a id="funcao-68"></a>

## media_y_pais

Calcula a média dos valores associados aos pais de um nó em uma estrutura de grafo.

A função calcula a média dos valores associados aos nós que são pais do nó 'n' em um grafo representado por 'G'. Se o nó 'n' não tiver pais, a função retorna 0. A média é calculada considerando apenas os pais que possuem um valor associado no dicionário 'pos'.

### Assinatura

```python
def media_y_pais(n):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `n` | `Não especificado` | O nó para o qual se deseja calcular a média dos valores de seus pais. |

### Retorno

**Tipo:** `float`

A média dos valores associados aos pais do nó 'n'. Retorna 0 se o nó não tiver pais.

### Dependências

- `{'nome': 'G.predecessors', 'categoria': 'chamada', 'descricao': "Método que retorna os nós predecessores do nó 'n' no grafo 'G'."}`
- `{'nome': 'len', 'categoria': 'chamada', 'descricao': 'Função que retorna o número de elementos em uma sequência.'}`
- `{'nome': 'list', 'categoria': 'chamada', 'descricao': 'Função que cria uma lista a partir de um iterável.'}`
- `{'nome': 'sum', 'categoria': 'chamada', 'descricao': 'Função que retorna a soma dos elementos de um iterável.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def media_y_pais(n):
            pais = list(G.predecessors(n))
            if not pais:
                return 0
            return sum(pos[p][1] for p in pais if p in pos) / len(pais)
```

</details>

---

<a id="funcao-69"></a>

## try_parse

Tenta analisar uma string como JSON.

Se a entrada for uma string que parece ser um objeto JSON (iniciada por '{' e terminada por '}', ou iniciada por '[' e terminada por ']'), tenta convertê-la em um objeto Python. Caso contrário, retorna a entrada original.

### Assinatura

```python
def try_parse(x):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `x` | `Não especificado` | Entrada que pode ser uma string representando um JSON. |

### Retorno

**Tipo:** `Não especificado`

Objeto Python resultante da análise do JSON, ou a entrada original se não for um JSON válido.

### Dependências

- `json`

<details>
<summary>Visualizar código-fonte</summary>

```python
def try_parse(x):
                if isinstance(x, str):
                    x_str = x.strip()
                    if (x_str.startswith("{") and x_str.endswith("}")) or \
                       (x_str.startswith("[") and x_str.endswith("]")):
                        try:
                            return json.loads(x_str)
                        except Exception:
                            return x
                return x
```

</details>

---

<a id="funcao-70"></a>

## formatar_dms

Formata um ângulo em formato DMS (graus, minutos, segundos) e referência.

Converte três partes de um ângulo em formato DMS (graus, minutos, segundos) e uma referência (N/S ou E/W) em uma string formatada.

### Assinatura

```python
def formatar_dms(dms, ref):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `dms` | `Não especificado` | Uma lista de três objetos que representam os graus, minutos e segundos do ângulo. |
| `ref` | `Não especificado` | A referência geográfica (N/S para latitude ou E/W para longitude). |

### Retorno

**Tipo:** `Não especificado`

Uma string formatada representando o ângulo em DMS.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def formatar_dms(dms, ref):
                        graus = float(dms[0].num) / float(dms[0].den)
                        minutos = float(dms[1].num) / float(dms[1].den)
                        segundos = float(dms[2].num) / float(dms[2].den)
                        return f"{int(graus)}°{int(minutos)}'{segundos:.2f}\"{ref}"
```

</details>

---

<a id="funcao-71"></a>

## dms_to_dd

Converte coordenadas de graus, minutos e segundos (DMS) para decimal (DD).

Esta função converte uma coordenada geográfica representada em graus, minutos e segundos (DMS) para um formato decimal (DD), considerando a referência Norte (N) ou Sul (S) e Leste (E) ou Oeste (W).

### Assinatura

```python
def dms_to_dd(dms, ref):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `dms` | `Não especificado` | Uma sequência de três valores representando graus, minutos e segundos. |
| `ref` | `Não especificado` | Referência geográfica ('N', 'S', 'E' ou 'W'). |

### Retorno

**Tipo:** `Não especificado`

Coordenada em formato decimal (DD).

### Dependências

- `float`

<details>
<summary>Visualizar código-fonte</summary>

```python
def dms_to_dd(dms, ref):
                        deg, min_, sec = [float(x.num) / float(x.den) for x in dms]
                        dd = deg + min_ / 60 + sec / 3600
                        if ref in ["S", "W"]:
                            dd *= -1
                        return dd
```

</details>

---
