# Referência de Funções

## Índice

- [rastrear_metados](#funcao-1)
- [dados_fotos_inv](#funcao-2)

---

<a id="funcao-1"></a>

## rastrear_metados

Rastreia metadados de um arquivo e registra métricas no banco de dados.

Esta função lê os metadados de um arquivo utilizando uma função fornecida, e então registra duas métricas no banco de dados: a quantidade total de arquivos encontrados e a quantidade de arquivos com índícios. Retorna essas duas quantidades como um par de inteiros.

### Assinatura

```python
# Consulte o código-fonte de rastrear_metados
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `arquivo` | `Path` | Caminho para o arquivo que será analisado. |
| `bd` | `sl.Connection` | Conexão com o banco de dados onde as métricas serão registradas. |
| `st` | `Não especificado` | Parâmetro opcional que pode ser utilizado pela função `ler_metadados`. |
| `ler_metadados` | `Callable` | Função que lê os metadados do arquivo e retorna dois valores: a quantidade de arquivos encontrados e a quantidade de arquivos com índícios. |
| `database` | `Não especificado` | Nome da base de dados onde as métricas serão registradas. |
| `execucao_id` | `Não especificado` | ID da execução que está sendo monitorada. |

### Retorno

**Tipo:** `tuple[int, int]`

Um par de inteiros representando a quantidade total de arquivos encontrados e a quantidade de arquivos com índícios.

### Dependências

- `{'nome': 'MANIFESTO.registrar_metrica', 'tipo': 'função', 'categoria': 'importada'}`
- `{'nome': 'UTILS.ler_metadados', 'tipo': 'função', 'categoria': 'importada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def rastrear_metados(
                    arquivo: Path,
                    bd: sl.Connection,
                    st = None,
                    *,
                    ler_metadados: Callable,
                    database,
                    execucao_id,
                ) -> tuple[int, int]:
    y_meta, y_ind = ler_metadados(arquivo, bd, st)
    registrar_metrica(
                            database,
                            execucao_id,
                            "arquivos_encontrados",
                            y_meta,
                        )
    registrar_metrica(
                                database,
                                execucao_id,
                                "arquivos_encontrados_com_indícios",
                                y_ind,
                            )
    return y_meta, y_ind
```

</details>

---

<a id="funcao-2"></a>

## dados_fotos_inv

Gera um painel para análise de metadados das fotos de inventário.

A função verifica se o diretório de trabalho está configurado e, em seguida, inicializa uma série de operações relacionadas a dados, banco de dados e relatórios. Ela também cria botões para reprocessar e gerar um checklist, além de exibir resumos das fotos analisadas e indícios associados.

### Assinatura

```python
def dados_fotos_inv():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Dependências

- `{'nome': 'MANIFESTO.execucao_trilha', 'tipo': 'função'}`
- `{'nome': 'MANIFESTO.inicializa_database', 'tipo': 'função'}`
- `{'nome': 'MANIFESTO.inicializa_detalhes', 'tipo': 'função'}`
- `{'nome': 'MANIFESTO.inicializar_rastreamento', 'tipo': 'função'}`
- `{'nome': 'MANIFESTO.registrar_artefato', 'tipo': 'função'}`
- `{'nome': 'MANIFESTO.registrar_evento', 'tipo': 'função'}`
- `{'nome': 'RELATORIOS.imp_ck_list', 'tipo': 'função'}`
- `{'nome': 'UTILS.bsc_dados_reg', 'tipo': 'função'}`
- `{'nome': 'UTILS.existe_tabela', 'tipo': 'função'}`
- `{'nome': 'pandas', 'tipo': 'biblioteca'}`
- `{'nome': 'pathlib.Path', 'tipo': 'classe'}`
- `{'nome': 'sqlite3', 'tipo': 'biblioteca'}`
- `{'nome': 'streamlit', 'tipo': 'biblioteca'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def dados_fotos_inv():
    if not 'tra_dir' in st.session_state:
        st.html("""
                    <p>Você deve configurar o diretório de trabalho na aba 
                    <i>Criar Pasta de Trabalho</i>, barra lateral.</p>
                """)
        return
    
    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
    st.html(f"<style>{css}</style>")

    caminho_manifesto = Path(local) / "MANIFESTO" / "TRILHA_EXEC" / "execucoes.db"
    caminho_manifesto.parent.mkdir(parents=True, exist_ok=True)
    inicializa_database(str(caminho_manifesto))
    inicializa_detalhes(str(caminho_manifesto))
    inicializar_rastreamento(str(caminho_manifesto))
    database = str(caminho_manifesto)
    pasta_fotos = Path(local) / "IMAGENS_SUMARIO"

    bd = sl.connect(f'{local}\BD_LOCAL\{empresa}_{ano}.db')

    col1a = st.columns([1,5,1], gap='small')
    with col1a[1]:
        st.html(f"""<h1>Painel para Análises de Metadados das Fotos de Inventário</h1><br><br>
                    <p  style="text-align: justify;text-indent: 40px">Desenvolvido para 
                    apoiar a análise de laudos técnicos por meio da leitura automatizada de metadados de 
                    imagens, especialmente data, hora e coordenadas de geolocalização. A partir das 
                    informações EXIF incorporadas nos arquivos fotográficos, é possível verificar se as 
                    fotos foram capturadas no local e período compatíveis com o objeto analisado, garantindo 
                    maior confiabilidade, rastreabilidade e adequação das evidências visuais utilizadas. 
                    Ao identificar automaticamente possíveis inconsistências temporais ou espaciais, o 
                    sistema contribui para a validação e integridade dos registros apresentados no laudo.
                    Para reprocessar use o botão a seguir.""")
        st.divider()
        cols = st.columns([1,2,1,2,1], gap='small')
        with cols[1]:
            x = st.button("(Re)Fazer", key="ANL_FOTOS_INV")
        with cols[3]:
            x1 = st.button("Check List", key="CHECKLIST_LAUDO")
        st.divider()
        if x1:
            with execucao_trilha(
                                    db_path=database, script_nome="APOIO_ANL_LAUDO",
                                    parametros={"empresa": empresa, "ano": ano},
                                ) as execucao_id:
        
                registrar_evento(database, execucao_id, "GERACAO_ARQ_APOIO_LAUDO_INICIADO",
                                    mensagem=f"Iniciando geração de arquivo de apoio para análise do Sumário Executivo")
                saida = imp_ck_list(f'{local}//RELATORIOS//checklist_sumario.xlsx', dados)
                registrar_artefato(database, execucao_id, f'{local}//RELATORIOS//checklist_sumario.xlsx', "SAIDA")
                registrar_evento(database, execucao_id, "GERACAO_ARQ_APOIO_LAUDO_FINALIZADO",
                                mensagem=f"Finalizado geração de arquivo de apoio para análise do Sumário Executivo")
            if saida == "Falhou":
                st.warning("Geração do checklist falhou!")

            else:
                st.info(f"Executado com sucesso, arquivo na pasta {local}/RELATORIOS/checklist_sumario.xlsx.")

        if x:
            
            if not pasta_fotos.is_dir():
                st.warning(
                    f"Diretório de imagens não encontrado: {pasta_fotos}"
                )
            with st.spinner("Lendo metadados das fotos"):
                with execucao_trilha(
                                        db_path=database, script_nome="Leitura_METADADOS_FOTOS",
                                        parametros={"empresa": empresa, "ano": ano},
                                    ) as execucao_id:
            
                    registrar_evento(database, execucao_id, "IMPORTACAO_LEITURA_METADADOS_FOTOS_INICIADO",
                                        mensagem=f"Iniciando leitura de de metadados das fotos de inventário")
                    try:
                        y1, y2 = rastrear_metados(
                                                        pasta_fotos,
                                                        bd,
                                                        st,
                                                        ler_metadados=ler_metadados,
                                                        database=database,
                                                        execucao_id=execucao_id,
                                                    )
                        registrar_evento(database, execucao_id, "IMPORTACAO_LEITURA_METADADOS_FOTOS_FINALIZADO",
                                            mensagem=f"Finalizado leitura de metadados das fotos de inventário")
                    except Exception as e:
                        registrar_evento(database, execucao_id, "ARQUIVO_REPROVADO",
                                            mensagem=f"GERACAO ARQAPOIO METDADOS FALHOU", nivel="ERRO",
                                            detalhes={"erro": f"{e}"})

        if (existe_tabela('tbl_FOTOS', bd)):
            cont1, _, cont2 = st.columns([15,1,15], gap = 'small')
            with cont1:
                with st.container(border=True):
                    st.html(f"""<h3 style="text-align: center;">Resumo Fotos Analisadas</h3><br>
                                <p  style="text-align: justify;text-indent: 40px">Resumo das fotos 
                                disponiveis na pasta {pasta_fotos} e que foram avaliadas.""")
                    sSQL = "SELECT * FROM tbl_FOTOS"
                    df = pd.read_sql(sSQL, bd)
                    config = {
                                "arquivo": st.column_config.TextColumn("Foto"),
                                "latitude": st.column_config.TextColumn("Latitude"),
                                "longitude": st.column_config.TextColumn("Longitude"),
                                "lat_dms": st.column_config.TextColumn("Latitude DMS"),
                                "lon_dms": st.column_config.TextColumn("Longitude DMS"),
                                "data_original": st.column_config.TextColumn("Data Original"),
                                "data_digitizacao": st.column_config.TextColumn("Data Digitalização"),
                                "data_modificacao": st.column_config.TextColumn("Data Modificação"),
                                "software": st.column_config.TextColumn("Software")
                            }
                    st.dataframe(df, width='stretch', hide_index=True,  column_config=config)
                    st.download_button(
                                        "Exportar em CSV",
                                        data=df.to_csv(index=False, sep="|").encode("latin-1"),
                                        file_name=f"fotos_metadados.csv",
                                        mime="text/csv",
                                        key=f"fotos_exportar_dados",
                                        disabled=df.empty,
                                      )
            
            if (existe_tabela('tbl_FOTOS_indicios', bd)):
                with cont2:
                    with st.container(border=True):
                        st.html(f"""<h3 style="text-align: center;">Resumo de Indícios</h3><br>
                                    <p  style="text-align: justify;text-indent: 40px">Resumo das fotos 
                                    disponiveis na pasta {pasta_fotos} e indícios.""")
                        sSQL = "SELECT * FROM tbl_FOTOS_indicios"
                        df1 = pd.read_sql(sSQL, bd)
                        df1 = df1.replace(r'^\s*$', "ND", regex=True).fillna("ND")
                        config = {
                                    "arquivo": st.column_config.TextColumn("Foto"),
                                    "indicio_1": st.column_config.TextColumn("Indicio de datas"),
                                    "indicio_2": st.column_config.TextColumn("Indicio de Software"),
                                    "indicio_3": st.column_config.TextColumn("Indicio de Marca/Modelo")
                                }
                        st.dataframe(df1, width='stretch', hide_index=True,  column_config=config)
                        st.download_button(
                                            "Exportar em CSV",
                                            data=df1.to_csv(index=False, sep="|").encode("latin-1"),
                                            file_name=f"fotos_metadados_indicios.csv",
                                            mime="text/csv",
                                            key=f"fotos_exportar_dados1",
                                            disabled=df.empty,
                                            )
        else:
            st.warning("Sem fotos para analisar!")
```

</details>

---
