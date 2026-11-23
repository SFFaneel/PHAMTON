# Referência de Funções

## Índice

- [imp_SPED_EFD_ICMS](#funcao-1)
- [imp_SPED_ECD](#funcao-2)

---

<a id="funcao-1"></a>

## imp_SPED_EFD_ICMS

Realiza a importação dos arquivos EFD ICMS/IPI e processa os dados.

Esta função verifica se o diretório de trabalho está configurado, inicializa o banco de dados e realiza a importação dos arquivos EFD ICMS/IPI. Caso já existam dados no banco de dados, eles são carregados para uma tabela em um dataframe.

### Assinatura

```python
def imp_SPED_EFD_ICMS():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Exceções

- **`Exception`**: Caso ocorra qualquer erro durante o processo de importação.

### Dependências

- `MANIFESTO.execucao_trilha`
- `MANIFESTO.inicializa_database`
- `MANIFESTO.inicializa_detalhes`
- `MANIFESTO.inicializar_rastreamento`
- `MANIFESTO.registrar_artefato`
- `MANIFESTO.registrar_evento`
- `UTILS.bsc_dados_reg`
- `UTILS.imp_sped`
- `os`
- `pandas`
- `pathlib.Path`
- `sqlite3`
- `streamlit`

<details>
<summary>Visualizar código-fonte</summary>

```python
def imp_SPED_EFD_ICMS():
    if not 'tra_dir' in st.session_state:
        st.html("""
                    <div class="mensagem_tipo_1">
                        <p class="mensagem-fade-in">
                            Você deve configurar o diretório de trabalho na aba <i>Criar Pasta de Trabalho</i>, barra lateral.
                        </p>
                    </div>
                """)
        return

    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
    st.html(f"<style>{css}</style>")
    raiz = Path(local)
    caminho_manifesto = raiz / "MANIFESTO" / "TRILHA_EXEC" / "execucoes.db"
    caminho_manifesto.parent.mkdir(parents=True, exist_ok=True)
    inicializa_database(str(caminho_manifesto))
    inicializa_detalhes(str(caminho_manifesto))
    inicializar_rastreamento(str(caminho_manifesto))
    database = str(caminho_manifesto)

    df_arq = pd.DataFrame()
    col1 = st.columns([1,5,1], gap='small')
    with col1[1]:
        st.html("""<h1>Importação dos arquivos EFD ICMS/IPI</h1><br><br>
                        <p  style="text-align: justify;text-indent: 40px">Nesta etapa 
                        do processo, realiza-se o carregamento dos arquivos correspondentes
                        às escriturações fiscais do ICMS e IPI.</p><br>
                """)

        _, cola, _, _, _, colb = st.columns([1,2,1,1,1,4], gap='small')

        with colb:
            apagar = st.checkbox("Apagar banco de dados?", value=False, help="Caso queira reimportar tudo, check")
        with cola:
            importar = st.button("Importar EFD ICMS", key="IMPORTAR_EFD_ICMS")

        if importar:
            try:
                with execucao_trilha(
                                    db_path=database, script_nome="Importação EFD ICMS/IPI",
                                    parametros={"empresa": empresa, "ano": ano},
                                    ) as execucao_id:
                    registrar_evento(database, execucao_id, "IMPORTACAO_INICIADA_EFD_ICMS_IPI",
                                        mensagem=f"Iniciando importação de arquivo(s)")
                    df_arq = imp_sped(f"{local}/EFD_ICMS", f"{local}/BD_LOCAL", "EFD_ICMS", empresa, ano, apagar)
                    registrar_artefato(database, execucao_id, str(f"{local}/EFD_ICMS"), "ENTRADA")
                    registrar_evento(database, execucao_id, "IMPORTACAO_FINALIZADA_EFD_ICMS_IPI",
                                        mensagem=f"Finalizada importação de arquivo(s)")

            except Exception as e:
                st.error(f"Encontrado o seguinte erro: {e}.")
                registrar_evento(database, execucao_id, "ARQUIVO_EFD_ICMS_IPI_REPROVADO",
                                    mensagem=f"{local}/EFD_ICMS", nivel="ERRO",
                                    detalhes={"erro": str(e)})
        else:
            db_path = os.path.join( f"{local}/BD_LOCAL", f"EFD_ICMS_{empresa}_{ano}.db")
            with sl.connect(db_path) as bd:
                try:
                    df_arq = pd.read_sql("SELECT * FROM LST_ARQ", bd)
                except:
                    df_arq = pd.DataFrame()

        if not df_arq.empty:
            st.html("""
                    <p>Tabela de arquivos:</p>
                    """)

            config = {
                        "Dt_INI": st.column_config.DateColumn("Data de Início", format="DD/MM/YYYY"),
                        "Dt_FIM": st.column_config.DateColumn("Data de Fim", format="DD/MM/YYYY"),
                        "CNPJ": st.column_config.TextColumn("CNPJ"),
                        "Nm_Arq": st.column_config.TextColumn("Nome do arquivo de origem do dado"),
                    }
            if len(df_arq)>0:
                df_arq['Dt_INI'] = pd.to_datetime(df_arq['Dt_INI'])
                df_arq = df_arq.sort_values(by="Dt_INI")
                st.dataframe(df_arq, width='stretch', hide_index=True,  column_config=config)
```

</details>

---

<a id="funcao-2"></a>

## imp_SPED_ECD

Realiza a importação dos arquivos ECD (Escriturações Contábeis Digitais) e processa os dados.

A função verifica se o diretório de trabalho foi configurado, inicializa o banco de dados e realiza a importação dos arquivos ECD. Caso ocorra algum erro durante o processo, ele é registrado e uma mensagem de erro é exibida.

### Assinatura

```python
def imp_SPED_ECD():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Dependências

- `{'nome': 'MANIFESTO.execucao_trilha', 'tipo': 'função', 'descricao': 'Função para executar uma trilha de processamento.'}`
- `{'nome': 'MANIFESTO.inicializa_database', 'tipo': 'função', 'descricao': 'Função para inicializar o banco de dados.'}`
- `{'nome': 'MANIFESTO.inicializa_detalhes', 'tipo': 'função', 'descricao': 'Função para inicializar detalhes do processo.'}`
- `{'nome': 'MANIFESTO.inicializar_rastreamento', 'tipo': 'função', 'descricao': 'Função para inicializar o rastreamento do processo.'}`
- `{'nome': 'MANIFESTO.registrar_artefato', 'tipo': 'função', 'descricao': 'Função para registrar artefatos no banco de dados.'}`
- `{'nome': 'MANIFESTO.registrar_evento', 'tipo': 'função', 'descricao': 'Função para registrar eventos no banco de dados.'}`
- `{'nome': 'UTILS.bsc_dados_reg', 'tipo': 'função', 'descricao': 'Função para obter dados de registro.'}`
- `{'nome': 'UTILS.existe_dk', 'tipo': 'função', 'descricao': 'Função para verificar a existência de uma tabela no banco de dados.'}`
- `{'nome': 'UTILS.imp_sped_duck3', 'tipo': 'função', 'descricao': 'Função para importar arquivos ECD usando DuckDB.'}`
- `{'nome': 'duckdb', 'tipo': 'biblioteca', 'descricao': 'Biblioteca para manipulação de bancos de dados DuckDB.'}`
- `{'nome': 'os', 'tipo': 'biblioteca', 'descricao': 'Biblioteca padrão do Python para operações do sistema operacional.'}`
- `{'nome': 'pandas', 'tipo': 'biblioteca', 'descricao': 'Biblioteca de dados e análise em Python.'}`
- `{'nome': 'pathlib.Path', 'tipo': 'classe', 'descricao': 'Classe para manipulação de caminhos de arquivo.'}`
- `{'nome': 'streamlit', 'tipo': 'biblioteca', 'descricao': 'Biblioteca para criação de aplicativos web em Python.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def imp_SPED_ECD():

    if not  'tra_dir' in st.session_state:
        st.html("""
                    <div class="mensagem_tipo_1">
                        <p class="mensagem-fade-in">
                            Você deve configurar o diretório de trabalho na aba <i>Criar Pasta de Trabalho</i>, barra lateral.
                        </p>
                    </div>
                """)
        return
    
    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
    st.html(f"<style>{css}</style>")
    raiz = Path(local)
    caminho_manifesto = raiz / "MANIFESTO" / "TRILHA_EXEC" / "execucoes.db"
    caminho_manifesto.parent.mkdir(parents=True, exist_ok=True)
    inicializa_database(str(caminho_manifesto))
    inicializa_detalhes(str(caminho_manifesto))
    inicializar_rastreamento(str(caminho_manifesto))
    database = str(caminho_manifesto)

    caminho_bd = os.path.join(f"{local}/BD_LOCAL", f"ecd_{empresa}_{ano}.duckdb")


    col1 = st.columns([1,5,1], gap='small')
    with col1[1]:
        st.html("""<h1>Importação dos arquivos ECD</h1><br><br>
            <p  style="text-align: justify;text-indent: 40px">Nesta etapa do processo, 
            realiza-se o carregamento dos arquivos correspondentes
            às escriturações contábeis digitais, ECD.</p>
            """)

        _, cola, _ = st.columns([5,2,5], gap='small')
        
        with cola:
            importar = st.button("Importar ECD", key="IMPORTAR_ECD")

        if importar:
            try:
                with execucao_trilha(
                                    db_path=database, script_nome="Importação ECD",
                                    parametros={"empresa": empresa, "ano": ano},
                                    ) as execucao_id:
                    registrar_evento(database, execucao_id, "IMPORTACAO_INICIADA_ECD",
                                        mensagem=f"Iniciando importação de arquivo(s)")
                    
                    df_arq = imp_sped_duck3(f"{local}/ECD", f"{local}/BD_LOCAL", "ECD", empresa, ano)
                    registrar_artefato(database, execucao_id, str(f"{local}/ECD"), "ENTRADA")
                    registrar_evento(database, execucao_id, "IMPORTACAO_FINALIZADA_ECD",
                                        mensagem=f"Finalizada importação de arquivo(s)")
            except Exception as e:
                st.error(f"{e}")
                df_arq = pd.DataFrame({'Dt_INI': [0], 'Dt_FIM': [0], 'CNPJ': ['0'], 'Nm_Arq': ['0']})
                registrar_evento(database, execucao_id, "ARQUIVO_ECD_REPROVADO",
                                    mensagem=f"{local}/ECD", nivel="ERRO",
                                    detalhes={"erro": str(e)})

        with duckdb.connect(caminho_bd) as bd:
            if existe_dk(bd, "controle_importacao"):
                df_arq = bd.execute("SELECT * FROM controle_importacao").fetchdf()
                st.html("""
                        <p>Tabela de arquivos:</p>
                        """)

                config = {
                            "Dt_INI": st.column_config.DateColumn("Data de Início", format="DD/MM/YYYY"),
                            "Dt_FIM": st.column_config.DateColumn("Data de Fim", format="DD/MM/YYYY"),
                            "CNPJ": st.column_config.TextColumn("CNPJ"),
                            "Nm_Arq": st.column_config.TextColumn("Nome do arquivo de origem do dado"),
                            
                        }
                if len(df_arq) > 0:
                    df_arq = df_arq.sort_values(by="dt_ini")
                    st.dataframe(df_arq, width='stretch', hide_index=True,  column_config=config)
```

</details>

---
