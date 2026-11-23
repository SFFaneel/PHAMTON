# Referência de Funções

## Índice

- [imp_CVA](#funcao-1)

---

<a id="funcao-1"></a>

## imp_CVA

Realiza a importação dos dados do Banco de Pagamentos da CVA.

A função verifica se o diretório de trabalho está configurado e, em seguida, realiza a importação dos arquivos correspondentes aos dados do banco de pagamentos de CVA. O processo envolve a leitura de vários arquivos SAS7BDAT, manipulação dos dados e armazenamento no banco de dados SQLite.

### Assinatura

```python
def imp_CVA():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Dependências

- `{'nome': 'MANIFESTO.execucao_trilha', 'tipo': 'função', 'descricao': 'Função para gerenciar a execução de trilhas.'}`
- `{'nome': 'MANIFESTO.inicializa_database', 'tipo': 'função', 'descricao': 'Função para inicializar o banco de dados.'}`
- `{'nome': 'MANIFESTO.inicializa_detalhes', 'tipo': 'função', 'descricao': 'Função para inicializar detalhes do processo.'}`
- `{'nome': 'MANIFESTO.inicializar_rastreamento', 'tipo': 'função', 'descricao': 'Função para inicializar o rastreamento do processo.'}`
- `{'nome': 'MANIFESTO.registrar_evento', 'tipo': 'função', 'descricao': 'Função para registrar eventos durante a execução.'}`
- `{'nome': 'UTILS.bsc_cd_aneel', 'tipo': 'função', 'descricao': 'Função para obter o código ANEEL da empresa.'}`
- `{'nome': 'UTILS.bsc_dados_reg', 'tipo': 'função', 'descricao': 'Função para obter dados de registro.'}`
- `{'nome': 'UTILS.existe_tabela', 'tipo': 'função', 'descricao': 'Função para verificar a existência de uma tabela no banco de dados.'}`
- `{'nome': 'pandas', 'tipo': 'biblioteca', 'descricao': 'Biblioteca para manipulação de dados em Python.'}`
- `{'nome': 'pathlib.Path', 'tipo': 'classe', 'descricao': 'Classe para manipulação de caminhos de arquivo e diretórios.'}`
- `{'nome': 'pyreadstat', 'tipo': 'biblioteca', 'descricao': 'Biblioteca para leitura de arquivos SAS7BDAT.'}`
- `{'nome': 'sqlite3', 'tipo': 'biblioteca', 'descricao': 'Biblioteca para manipulação de bancos de dados SQLite.'}`
- `{'nome': 'streamlit', 'tipo': 'biblioteca', 'descricao': 'Biblioteca para criação de aplicativos web em Python.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def imp_CVA():
    if not 'tra_dir' in st.session_state:
        st.html("""
                <p style="text-align: justify;text-indent: 40px">Você 
                deve configurar o diretório de trabalho na aba <i>Criar 
                Pasta de Trabalho</i>, barra lateral.</p>
            """)
        return

    pasta = Path.cwd() / "BD_CVA"
    if not pasta.is_dir():
        st.warning("Não é possível rodar CVA nesta máquina.")
        return

    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    raiz = Path(local)
    caminho_manifesto = raiz / "MANIFESTO" / "TRILHA_EXEC" / "execucoes.db"
    caminho_manifesto.parent.mkdir(parents=True, exist_ok=True)
    inicializa_database(str(caminho_manifesto))
    inicializa_detalhes(str(caminho_manifesto))
    inicializar_rastreamento(str(caminho_manifesto))
    database = str(caminho_manifesto)
    bd_path = f'{local}\BD_LOCAL\{empresa}_{ano}.db'
    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
    st.html(f"<style>{css}</style>")
    col1a = st.columns([1,5,1], gap='small')
    with col1a[1]:
        st.html("""<h1>Importação dos dados do Banco de Pagamentos da CVA</h1><br><br>
            <p style="text-align: justify;text-indent: 40px">Nesta etapa do processo, 
            realiza-se o carregamento dos arquivos correspondentes
            aos dados do banco de pagamentos de CVA.</p><br>
            """)
        st.divider()
        col2a = st.columns(5, gap='small')
        with col2a[2]:
            importar = st.button("Importar CVA", key = "IMPORTAR_CVA")
        if importar:
            st.divider()
            a = st.status("Iniciando importação de dados do banco de pagamentos...")
            with execucao_trilha(
                                        db_path=database, script_nome="Importação de dados do Banco de Pagamentos",
                                        parametros={"empresa": empresa, "ano": ano},
                                     ) as execucao_id:
            
                registrar_evento(database, execucao_id, "IMPORTACAO_INICIADA_BP_CVA",
                                     mensagem=f"Iniciando importação de dados do banco de pagamentos")
                registrar_evento(database, execucao_id, "IDENTIFICANDO_ARQUIVOS_BP_CVA",
                                                     mensagem=f"Identificando dados do banco de pagamentos")

                df_CVA_ARQ, metadado_ARQ = pyreadstat.read_sas7bdat("BD_CVA/work_query_for_sas_arquivodu_cmp.sas7bdat", encoding='utf-8') 
                df_CVA_ARQ = df_CVA_ARQ[df_CVA_ARQ['CodAgt']==(bsc_cd_aneel(empresa))]
                df_CVA_PROC, metadado_PROC = pyreadstat.read_sas7bdat('BD_CVA/controleprocessamentoitem_cmp.sas7bdat', encoding='utf-8')
                df_CVA_PROC = df_CVA_PROC[['IdeArquivoCVA','DthCargaArquivo','CodRecebimentoArquivo']]
                df_CVA_PROC.columns = ['IdeArquivoCVA','DthCargaArquivo','CodRecArq']
                df_CVA_ARQ = df_CVA_ARQ.merge(df_CVA_PROC, how='left', on = 'CodRecArq', suffixes=("","_PROC_CVA"))

                for dt in ['DthCargaArquivo','DatIniRecArq','DatFimRecArq']:
                    if dt in df_CVA_ARQ:
                        if df_CVA_ARQ[dt].dtype == 'object':
                            try:
                                df_CVA_ARQ[dt] = pd.to_datetime(df_CVA_ARQ[dt], format='%d%b%Y:%H:%M:%S.%f')
                            except:
                                df_CVA_ARQ[dt] = pd.to_datetime(df_CVA_ARQ[dt], format='%d%b%Y:%H:%M:%S')

                df_CVA_ARQ['Nr_VERSAO'] = pd.to_numeric(df_CVA_ARQ['NomArqRecArq'].str[34:37], errors='coerce')
                df_CVA_ARQ['Dt_REF'] = pd.to_datetime("01" + df_CVA_ARQ['NomArqRecArq'].str[26:28] + df_CVA_ARQ['NomArqRecArq'].str[28:32], format = "%d%m%Y", errors='coerce')
                df_CVA_ARQ.sort_values(by = ['Dt_REF','Nr_VERSAO'], ascending = [True, False], inplace=True)
                df_CVA_ARQ['Nr_VERSAO_MAX'] = df_CVA_ARQ.groupby("Dt_REF", dropna=False)['Nr_VERSAO'].transform('max')
                df_CVA_ARQ = df_CVA_ARQ[df_CVA_ARQ['Nr_VERSAO'] == df_CVA_ARQ['Nr_VERSAO_MAX']]
                df_CVA_ARQ.drop(columns = ['Nr_VERSAO_MAX'], inplace=True)

                with  sl.connect(bd_path) as bd:
                    df_CVA_ARQ.to_sql('tbl_ARQ_BP', bd, if_exists='replace', index=False)
                
                dic_arq = {'Energia' : 'consumoenergia_cmp',
                        'RB' : 'redebasica_cmp',
                        'PROINFA' : 'proinfa_cmp',
                        'CDE' : 'cde_cmp',
                        'CDE_ENERGIA' : 'cdeenergiaRevenda_cmp',
                        'CFURH' : 'cfurh_cmp',
                        'Itaipu' : 'itaipu_cmp'
                        }
                
                lst_ARQ = df_CVA_ARQ['IdeArquivoCVA'].drop_duplicates().to_list()
                z=1
                for key, value in dic_arq.items():
                    registrar_evento(database, execucao_id, f"BUSCANDO_ARQUIVOS_{key}",
                                        mensagem=f"Copiando dados de {key}")
                    a.status(f"Importando {key}...")
                    lst_encoding = ['LATIN1','UTF-8','WINDOWS-1252',]
                    for enc in lst_encoding:
                        try:
                            a1 = st.status(f"     Importando {key}, encoder {enc}...")
                            df_PROV, metadado_PROV = pyreadstat.read_sas7bdat(rf"BD_CVA/{value}.sas7bdat", encoding=enc) 
                            break
                        except:
                            a1.update(label=f"     Falhou {key}, encoder {enc}!", state="error")
                            pass
                    
                    if len(df_PROV):
                        df_PROV = df_PROV[df_PROV['IdeArquivoCVA'].isin(lst_ARQ)].copy()
                        df_PROV.to_sql(key, bd, if_exists='replace', index=False)
                        a1.update(label=f"     Importado {key}, encoder {enc}!", state="complete")
                    z += 1
                    registrar_evento(database, execucao_id, f"TERMINADO_ARQUIVOS_{key}",
                                     mensagem=f"Copiado dados de {key}")
                a.update(label=f"Finalizado importação de dados do banco de pagamentos para {empresa}!", state="complete")
                registrar_evento(database, execucao_id, f"TERMINADO_COPIA_BP_CVA",
                                 mensagem=f"Terminado cópia de arquivos do banco de pagamentos de CVA")

        with  sl.connect(bd_path) as bd:
            if existe_tabela('tbl_ARQ_BP', bd):
                st.divider()
                st.html("""
                        <p style="text-align: justify;text-indent: 40px">A seguir apresentamos a 
                        tabela de arquivos empregados na análise:</p>
                        """)

                sSQL = f"""
                        SELECT *
                        FROM tbl_ARQ_BP
                        """
                df_tabela = pd.read_sql(sSQL, bd)
                st.dataframe(df_tabela, width='content', hide_index=True)
```

</details>

---
