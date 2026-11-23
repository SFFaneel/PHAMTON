# Referência de Funções

## Índice

- [_vis_001](#funcao-1)
- [_vis_002](#funcao-2)
- [_vis_003](#funcao-3)
- [_vis_004](#funcao-4)
- [visualizador_BPR](#funcao-5)

---

<a id="funcao-1"></a>

## _vis_001

Processa dados de um banco de dados SQLite e gera relatórios visuais e tabelares.

A função `_vis_001` realiza várias operações em um banco de dados SQLite, incluindo a carga de dados, processamento dos mesmos e a geração de gráficos e tabelas para análise. Ela utiliza várias funções auxiliares e bibliotecas como pandas, plotly e streamlit.

### Assinatura

```python
def _vis_001(bd_path="", st=None, empresa = "", bd_path2="", local = ""):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `bd_path` | `str` | Caminho do arquivo SQLite. |
| `st` | `objeto` | Objeto streamlit para renderização de componentes interativos. |
| `empresa` | `str` | Nome da empresa. |
| `bd_path2` | `str` | Caminho do segundo arquivo SQLite (opcional). |
| `local` | `str` | Local onde os relatórios serão salvos. |

### Retorno

**Tipo:** `tuple`

Retorna vários DataFrames e um diretório com os gráficos gerados.

### Exceções

- **`UserWarning`**: Lancado quando há erros na importação de dados do DuckDB.

### Dependências

- `{'nome': 'UTILS.carga_sqlite_cache', 'categoria': 'import'}`
- `{'nome': 'UTILS.existe_tabela', 'categoria': 'import'}`
- `{'nome': 'UTILS.imp_tbl_forma_001', 'categoria': 'import'}`
- `{'nome': 'UTILS.importar_dados_duckdb', 'categoria': 'import'}`
- `{'nome': 'numpy', 'categoria': 'import'}`
- `{'nome': 'os', 'categoria': 'import'}`
- `{'nome': 'pandas', 'categoria': 'import'}`
- `{'nome': 'plotly.graph_objects', 'categoria': 'import'}`
- `{'nome': 'plotly.subplots.make_subplots', 'categoria': 'import'}`
- `{'nome': 'sqlite3', 'categoria': 'import'}`
- `{'nome': 'streamlit', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _vis_001(bd_path="", st=None, empresa = "", bd_path2="", local = ""):
    with sl.connect(bd_path) as bd:
        if not existe_tabela("BASE_INCR_COMP_A1", bd):
            return
        df = carga_sqlite_cache("SELECT * FROM BASE_INCR_COMP_A1", bd)
        df_BPUAR = imp_tbl_forma_001("BP_UAR", SQLq=None, con=bd, st=st, Empresa=empresa)
        df_BAIXAS = imp_tbl_forma_001("BAIXAS", SQLq=None, con=bd, st=st, Empresa=empresa)
        df_BAIXAS['Dt_Imob'] = pd.to_datetime(df_BAIXAS['Dt_Imob'], errors='coerce')
        df_BAIXAS = df_BAIXAS[(df_BAIXAS['FLG_AJST_CTB'].astype(str)=='0') & (df_BAIXAS['Dt_Imob'] < pd.Timestamp(st.session_state.dt_ini))]
        df_BAIXAS['Qtd_INI'] = pd.to_numeric(df_BAIXAS['Qtd_INI'].astype(str).str.replace(",","."), errors='coerce')
        df_BAIXAS['Qtd_FIN'] = pd.to_numeric(df_BAIXAS['Qtd_FIN'].astype(str).str.replace(",","."), errors='coerce')
    
        df_INCR = df[['Id_SEQ_INC', 'Id_AIS', 'Cd_CC', 'Cd_ODI', 'Cd_SubODI', 'Nr_TI', 'Nr_CM', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 
                    'Nr_A4', 'Nr_A5', 'Nr_A6', 'Cd_UAR', 'Cd_UC', 'Cd_Patrim', 'Cd_DIG_INC', 'COD_ITEM', 'Qtd_AIS', 'Cd_UND_AIS', 
                    'VL_VOC', 'Dt_Imob', 'Dt_CNTB_AJST', 'VL_DEP_ACUM', 'VL_VOC_VF', 'VL_VOC_COM', 'VL_VOC_CA', 'VL_VOC_JOA', 
                    'VL_VOC_VF_AVAL', 'VL_VOC_COM_AVAL', 'VL_VOC_CA_AVAL', 'VL_VOC_JOA_AVAL', 'Cd_ODD', 'Dt_BX', 'Txt_DESC_TECN', 
                    'Txt_CLS_TNS', 'FLG_RSV', 'Cd_ODI_ENG', 'Cd_TP_AVAL', 'Cd_SISBASE', 'Cd_SISBASE_SFF', 'Id_BP', 'TP_BEM', 'VL_VNR_UC', 'VL_IAI_UC', 
                    'VL_DAC_UC', 'VL_VMU_UC', 'VL_IAD_UC', 'VL_VBR_UC', 'VL_100DEP_UC', 'Pct_IA', 'VL_VNR_VF_UNIT', 'VL_VNR_COM_UNIT', 
                    'VL_VNR_CA_UNIT', 'VL_VNR_JOA', 'FLG_DOA_OE', 'FLG_INCOR_OE', 'FLG_PLPT_OE', 'FLG_OAT', 'FLG_REG', 'FLG_ELIG', 
                    'Cd_CONC', 'Cd_ABCC', 'Cd_NumFIS', 'Dt_REF_DADOS', 'FA_IPCA', 'FA_COGE', 'Cd_Q1A', 'VL_COM_AT']]
    
        df_INCR['VL_VOC_VFa'] = df_INCR['VL_VOC_VF'].fillna(0) * df_INCR['FA_COGE'].fillna(1)
        df_INCR['VL_VOCa'] = (df_INCR['VL_VOC'] - df_INCR['VL_VOC_VF'].fillna(0)) * df_INCR['FA_IPCA'] + df_INCR['VL_VOC_VFa']
    
        df_INCR['Id_BP'] = df_INCR['Id_BP'].fillna(0)
        df_INCR['Id_BP'] = df_INCR['Id_BP'].astype(str)
    
        df_ANLS_01 = (df_INCR[(df_INCR['FLG_ELIG'].astype(str)=='1') & (df_INCR['Cd_CONC'].astype(str).isin(['1','3']))]
                    .groupby(['Cd_TP_AVAL','Nr_TI', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 
                    'Nr_A4', 'Nr_A5', 'Nr_A6', 'Cd_SISBASE','Id_BP', 'Cd_UAR', 'Cd_UND_AIS'], dropna=False)[['Qtd_AIS','VL_VOC_VFa','VL_VOCa','VL_VNR_UC']]
                    .sum()
                    .reset_index()
                    .sort_values(by=['Cd_TP_AVAL','VL_VOCa'], ascending=False))
    
        df_ANLS_01['VAR_ABS'] = df_ANLS_01['VL_VNR_UC'].fillna(0) - df_ANLS_01['VL_VOCa'].fillna(0)
        df_ANLS_01['Pct_TOT'] = df_ANLS_01['VL_VNR_UC'].fillna(0) / df_ANLS_01['VL_VNR_UC'].fillna(0).sum()
        df_ANLS_01['IMPACTO'] = df_ANLS_01['VAR_ABS'].abs() * df_ANLS_01['Pct_TOT']
        df_ANLS_01 = df_ANLS_01.sort_values(by=['IMPACTO'], ascending=False)
        df_BPUAR['Qtd'] = pd.to_numeric(df_BPUAR['Qtd'].astype(str).str.replace("-","0"), errors='coerce')
        df_BPUAR['Id_BP'] = df_BPUAR['Id_BP'].astype(str)
    
        df_ANLS_01 = df_ANLS_01.merge(df_BPUAR[['Id_BP','Qtd','VL_VF','VL_ICMS','VL_ODC','VL_VF_UNIT_AT']], how = 'left', on = 'Id_BP')
        df_ANLS_01['VAR_ABS_FIS'] = df_ANLS_01['Qtd_AIS'].fillna(0) - df_ANLS_01['Qtd'].fillna(0)
        df_ANLS_01['VL_VF_UNIT_AT'] = pd.to_numeric(
                                                        df_ANLS_01['VL_VF_UNIT_AT'],
                                                        errors='coerce'
                                                    )
        df_ANLS_01['VAR_ABS_CTB'] = df_ANLS_01['VL_VOC_VFa'].fillna(0)/df_ANLS_01['Qtd_AIS'].fillna(1) - df_ANLS_01['VL_VF_UNIT_AT'].fillna(0)
    
        df_ANLS_01['FLG_QTD'] = 0
        df_ANLS_01.loc[(df_ANLS_01['Cd_TP_AVAL'].astype(str)=='2') &
                    (df_ANLS_01['VAR_ABS_FIS']>1), 'FLG_QTD'] = 1
    
        df_sorted = df_ANLS_01.sort_values(by="VL_VOCa", ascending=True)
        total_voca = df_sorted["VL_VOCa"].sum()
        total_vnr = df_sorted["VL_VNR_UC"].sum()
    
        fig = make_subplots(
                                rows=1,
                                cols=2,
                                column_widths=[0.75, 0.25], 
                                horizontal_spacing=0.08, 
                                subplot_titles=(
                                    "Comparação por NR_TI",
                                    "Total Global",
                                ),
                            )
    
        fig.add_trace(
                            go.Bar(
                                y=df_sorted["Nr_TI"].astype(str),
                                x=df_sorted["VL_VOCa"],
                                name="VOCa",
                                orientation="h",
                                marker_color="#2b5c8f",
                                hovertemplate="<b>TI %{y}</b><br>VOCa: %{x:,.2f}<extra></extra>",
                            ),
                            row=1,
                            col=1,
                        )
    
        fig.add_trace(
                        go.Bar(
                            y=df_sorted["Nr_TI"].astype(str),
                            x=df_sorted["VL_VNR_UC"],
                            name="VNR",
                            orientation="h",
                            marker_color="#e06d53",
                            hovertemplate="<b>TI %{y}</b><br>VNR: %{x:,.2f}<extra></extra>",
                        ),
                        row=1,
                        col=1,
                    )
    
        fig.add_trace(
                            go.Bar(
                                x=["VOCa Total", "VNR Total"],
                                y=[total_voca, total_vnr],
                                name="Total Global",
                                marker_color=["#2b5c8f", "#e06d53"],
                                text=[f"{total_voca:,.0f}".replace(",","."), f"{total_vnr:,.0f}".replace(",",".")],
                                textposition="auto",
                                hovertemplate="<b>%{x}</b><br>Total: %{y:,.2f}<extra></extra>",
                                showlegend=False,
                            ),
                            row=1,
                            col=2,
                        )
    
        relacao = total_vnr / total_voca if total_voca != 0 else 0
        texto_relacao = f"VNR/VOCa = {relacao:,.2%}".replace(",","x").replace(".",",").replace("x",".")
        fig.add_annotation(
                                x=0.5,
                                y=max(total_voca, total_vnr) * 1.10,
                                text=texto_relacao,
                                showarrow=False,
                                font=dict(
                                    size=14,
                                    color="#222222"
                                ),
                                bgcolor="rgba(255,255,255,0.85)",
                                bordercolor="#999999",
                                borderwidth=1,
                                row=1,
                                col=2,
                            )
    
        fig.update_layout(
                            barmode="group",
                            bargap=0.3,
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            legend=dict(
                                orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=0.75
                            ),
                            margin=dict(l=60, r=20, t=100, b=40),
                            height=600,
                        )
    
    
        fig.update_xaxes(
                            title_text="Valores", showgrid=True, gridcolor="#eeeeee", row=1, col=1
                        )
        fig.update_yaxes(title_text="Número NR_TI", type="category", row=1, col=1)
        fig.update_xaxes(showgrid=False, row=1, col=2)
        fig.update_yaxes(
                            title_text="Valores Totais", showgrid=True, gridcolor="#eeeeee", row=1, col=2
                        )
    
        
        st.html(
                    """
                        <h2>
                            VOCa versus VNR
                        </h2>
                        <p style="text-align: justify;text-indent: 40px">
                            O painel apresenta uma visão bidimensional dos indicadores. À <b>esquerda (Proporção 3x1)</b>, 
                            está detalhado o comportamento individual por <b>Nr_TI</b>. À <b>direita</b>, a barra vertical consolida o <b>Total Global</b> acumulado, 
                            facilitando a comparação imediata do volume financeiro total entre as duas métricas.
                        </p>
                    """, width='stretch'
                )
        st.plotly_chart(fig, width='stretch')
        dir_FIG = rf"{local}/RELATORIOS/figuras"
        os.makedirs(dir_FIG, exist_ok=True)

        fig.write_image(
                            f"{dir_FIG}/VNR_VOCa.png",
                            width=1920,
                            height=1080,
                            scale=2
                        )
        if not existe_tabela('tbl_ATIPICIDADE',bd):
            df_ROA, erro = importar_dados_duckdb('ROA', bd, empresa, colunas=["VL_tot"], itens="Cd_SubODI, Cd_ATIP, VL_tot", st=st)
            df_ROA['Cd_ATIP'] = df_ROA['Cd_ATIP'].fillna("0")
            df_ROA['VL_tot'] = pd.to_numeric(df_ROA['VL_tot'].str.replace(",","."), errors="coerce").fillna(0)
            df_ROA = df_ROA.groupby(["Cd_SubODI", "Cd_ATIP"], dropna=False)['VL_tot'].sum().reset_index()
            dic_atip = {
                            '0': 'Sem atipicidade',
                            '1': 'Expansão em linha viva',
                            '2': 'Recondutoramento de circuitos',
                            '3': 'Recapacitação de linhas',
                            '4': 'Instalação ou substituição de UAR que não seja a própria UC',
                            '5': 'Redes e linhas de distribuição subterrâneas ou submersas (todas as TUC associadas)',
                            '6': 'Estruturas tipo torre (TUC 255.02)',
                            '7': 'Estruturas tipo poste em Linhas de Distribuição (TUC 255.01)',
                            '8': 'Sistemas especiais de medição',
                            '9': 'Novas tecnologias, ainda não modularizadas',
                            '10': 'Outros'
                        }
            df_ROA['Cd_ATIP'] = df_ROA['Cd_ATIP'].map(dic_atip)
            if len(erro)==0:
                df_ROA.to_sql("tbl_ATIPICIDADE", bd, if_exists="replace", index=False)
            else:
                st.erro("Verifique os erros a seguir")
                st.write(erro)
                raise UserWarning("Não se pode continuar até arrumar o arquivo.")
        else:
            df_ROA = pd.read_sql("SELECT * FROM tbl_ATIPICIDADE", bd)
    
    
        df_ANLS_01voc = df_INCR.copy()
        df_ANLS_01voc["VL_COM_AT"] = df_ANLS_01voc["VL_COM_AT"].fillna(0)
    
        condicoes = [
                        df_ANLS_01voc["FLG_DOA_OE"].astype(str).eq("1") & df_ANLS_01voc["Cd_TP_AVAL"].eq("1"),
                        df_ANLS_01voc["FLG_INCOR_OE"].astype(str).eq("1") & df_ANLS_01voc["Cd_TP_AVAL"].eq("1"),
                        df_ANLS_01voc["FLG_OAT"].astype(str).eq("1") & df_ANLS_01voc["Cd_TP_AVAL"].eq("1"),
                        df_ANLS_01voc["Cd_SISBASE_SFF"].eq("ND") & df_ANLS_01voc["Cd_TP_AVAL"].eq("1"),
                        df_ANLS_01voc["VL_COM_AT"].astype(str).eq('0') & df_ANLS_01voc["Cd_TP_AVAL"].eq("1"),
                        df_ANLS_01voc["Id_BP"].astype(str).eq('0') & df_ANLS_01voc["Cd_TP_AVAL"].eq("1"),
                        df_ANLS_01voc["Cd_SISBASE"].ne(df_ANLS_01voc["Cd_SISBASE_SFF"]) & df_ANLS_01voc["Cd_TP_AVAL"].eq("1"),
                        df_ANLS_01voc["Cd_TP_AVAL"].ne("1")
                    ]
    
        valores = [
                        "VOC - Doação",
                        "VOC - Incorporação",
                        "VOC - Obra atípica",
                        "VOC - Sem SISBASE",
                        "VOC - Sem COM/CA no BPR",
                        "VOC - Sem valor de fábrica no banco",
                        "Avaliar - Diverge na classificação SISBASE",
                        "BPR ou ORC"
                    ]
    
        df_ANLS_01voc["JST_VOC"] = np.select(
                                                condicoes,
                                                valores,
                                                default="NO"
                                            )
        df_P1 = df_ANLS_01voc[df_ANLS_01voc["Cd_TP_AVAL"].eq("1")].groupby("JST_VOC", dropna=False)['VL_VNR_UC'].sum().reset_index()
        
        df_P2 = df_ANLS_01voc[df_ANLS_01voc["Cd_TP_AVAL"].eq("2")].groupby("JST_VOC", dropna=False)['VL_VNR_UC'].sum().reset_index()
        df_P3 = df_ANLS_01voc[~df_ANLS_01voc["Cd_TP_AVAL"].isin(["1","2"])].groupby("JST_VOC", dropna=False)['VL_VNR_UC'].sum().reset_index()
        df_P1['TP_AVAL'] = "Atualizado"
        df_P2['TP_AVAL'] = "BPR"
        df_P2['JST_VOC'] = "BPR"
        df_P3['TP_AVAL'] = "Demais"
        df_P3['JST_VOC'] = "Demais"
        df_P = pd.concat([df_P1,df_P2,df_P3], ignore_index=True)
    
        df_pareto = (
                        df_P
                        .groupby(["JST_VOC", "TP_AVAL"], as_index=False)["VL_VNR_UC"]
                        .sum()
                    )
        df_pareto = df_pareto.sort_values(
                                            ["TP_AVAL","JST_VOC"],
                                            ascending=False
                                        )
        df_pareto["VNR_MM"] = df_pareto["VL_VNR_UC"] / 1_000_000
        df_pareto["PERC_ACUM"] = (
                                        df_pareto["VL_VNR_UC"].cumsum()
                                        / df_pareto["VL_VNR_UC"].sum()
                                        * 100
                                    )
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
                        go.Bar(
                            x=df_pareto["JST_VOC"],
                            y=df_pareto["VNR_MM"],
                            text=df_pareto["VNR_MM"].round(1),
                            textposition="outside",
                            name="VNR (R$ MM)",
                        ),
                        secondary_y=False,
                    )
        fig.add_trace(
                        go.Scatter(
                            x=df_pareto["JST_VOC"],
                            y=df_pareto["PERC_ACUM"],
                            mode="lines+markers",
                            name="% Acumulado",
                            text=[f"{v:.1f}%" for v in df_pareto["PERC_ACUM"]],
                            textposition="top center",
                            textfont=dict(size=11),
                            hovertemplate=
                                "<b>%{x}</b><br>" +
                                "% Acumulado: %{y:.1f}%<extra></extra>",
                        ),
                        secondary_y=True,
                    )
        fig.update_yaxes(
                            title_text="VNR (R$ milhões)",
                            secondary_y=False
                        )
    
        max_vnr = df_pareto["VNR_MM"].max()
        fig.update_yaxes(
                            title_text="% acumulado",
                            range=[0, max_vnr * 1.18],
                            secondary_y=False
                        )
        fig.add_hline(
                        y=80,
                        line_dash="dash",
                        line_color="red",
                        secondary_y=True
                    )
        fig.update_layout(
                            title={
                                "text": "Decomposição do VNR por motivo de avaliação",
                                "x": 0.5,
                                "xanchor": "center",
                                "font": {
                                    "size": 18,
                                    "color": "#111111"
                                }
                            }
                        )
        st.html("""

                        <h3>Decomposição do VNR por motivo de avaliação</h3>
    
                        <p style="text-align: justify;text-indent: 40px">
                        Espera-se que o <b>BPR</b> seja preponderante na composição do VNR,
                        representando, em regra, mais de <b>50%</b> do valor analisado.
                        Quando a participação do BPR é elevada, especialmente acima de <b>70%</b>,
                        isso pode indicar que a empresa não apresentou volume relevante de
                        <b>obras atípicas</b> ou uso de SisBASE que favorece o VNR. Nesses casos, 
                        o enquadramento pelo BPR pode ser vantajoso para a concessionária, pois a 
                        análise tende a não refletir situações atípicas que poderiam justificar 
                        valores inferiores ao BPR.
                        <br><br>
    
                        Por outro lado, uma participação do BPR inferior a <b>50%</b> é um sinal
                        de atenção. Nessa hipótese, recomenda-se verificar se há concentração
                        relevante de <b>obras atípicas</b>, ausência ou baixa representatividade
                        de compras enquadradas no BPR, possíveis erros de classificação na
                        avaliação, ou ainda efeitos expressivos decorrentes de <b>doações</b> e
                        <b>incorporações</b>.</p>

                    """)
        st.plotly_chart(fig, width='stretch')
        fig.write_image(
                            f"{dir_FIG}/Distribuicao_MTD_VL.png",
                            width=1920,
                            height=1080,
                            scale=2
                        )
    return df_INCR, dir_FIG, df_ROA, df_ANLS_01, df_BPUAR, df_BAIXAS
```

</details>

---

<a id="funcao-2"></a>

## _vis_002

Gera um gráfico de barras mostrando o impacto das atipicidades usando ROA como referência.

A função processa os dados fornecidos em `df_INCR` e `df_ROA`, calcula a porcentagem e valor total dos atipicidades, gera um gráfico de barras e exibe ele em uma interface Streamlit. Se `df_INCR` estiver vazio, a função retorna sem fazer nada.

### Assinatura

```python
# Consulte o código-fonte de _vis_002
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `bd_path` | `Não especificado` | Caminho para o banco de dados SQLite. |
| `st` | `Não especificado` | Objeto Streamlit para renderizar a interface gráfica. |
| `empresa` | `Não especificado` | Nome da empresa (não utilizado no código). |
| `bd_path2` | `Não especificado` | Caminho para o segundo banco de dados SQLite (não utilizado no código). |
| `local` | `Não especificado` | Localização (não utilizado no código). |
| `df_INCR` | `Não especificado` | DataFrame contendo os dados de atipicidade. |
| `dir_FIG` | `Não especificado` | Diretório onde o gráfico será salvo como imagem. |
| `df_ROA` | `Não especificado` | DataFrame contendo os dados de ROA. |

### Dependências

- `{'imports': ['pandas', 'plotly.express', 'sqlite3', 'streamlit'], 'chamadas': ['agg', 'apply', 'df_ROA.groupby', 'fig.update_layout', 'fig.update_traces', 'fig.update_xaxes', 'fig.update_yaxes', 'fig.write_image', 'graf_atip.sort_values', 'map', 'max', 'pd.DataFrame', 'px.bar', 'replace', 'sl.connect', 'st.fragment', 'st.html', 'st.plotly_chart', 'sum']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _vis_002(bd_path="", st=None, empresa = "", bd_path2="", local = "", 
             df_INCR = pd.DataFrame(), dir_FIG = "", df_ROA = pd.DataFrame()):
    if df_INCR.empty:
        return
    with sl.connect(bd_path) as bd:
        graf_atip = (
                        df_ROA.groupby(['Cd_ATIP'], as_index=False)
                        .agg(VL_tot=('VL_tot', 'sum'))
                    )
        graf_atip['Perc'] = graf_atip['VL_tot'] / graf_atip['VL_tot'].sum()
        graf_atip['VL_milhoes'] = graf_atip['VL_tot'] / 1_000_000
        graf_atip = graf_atip.sort_values('VL_tot', ascending=True)
        graf_atip['Label'] = (
                                graf_atip['Cd_ATIP']
                            )
        graf_atip['Texto'] = (
                                'R$ ' + graf_atip['VL_milhoes'].map(lambda x: f'{x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')) +
                                ' mi | ' +
                                graf_atip['Perc'].map(lambda x: f'{x:.2%}'.replace('.', ','))
                            )
        graf_atip['Cor'] = graf_atip['Cd_ATIP'].apply(
                                                        lambda x: 'Sem atipicidade' if x == 'Sem atipicidade' else 'Com atipicidade'
                                                    )
        fig = px.bar(
                        graf_atip,
                        x='VL_milhoes',
                        y='Label',
                        orientation='h',
                        text='Texto',
                        color='Cor',
                        color_discrete_map={
                            'Sem atipicidade': '#BDBDBD',
                            'Com atipicidade': '#2F6DB3'
                        },
                        hover_data={
                            'VL_tot': ':,.2f',
                            'VL_milhoes': False,
                            'Perc': ':.2%',
                            'Cd_ATIP': True,
                            'Label': False,
                            'Cor': False,
                            'Texto': False
                        }
                    )
    
        fig.update_traces(
                            textposition='outside',
                            marker_line_width=0,
                            opacity=0.9
                        )
        
        fig.update_layout(
                            title={
                                'text': 'Impacto das Atipicidades, usando ROA como referência',
                                'x': 0.01,
                                'xanchor': 'left'
                            },
                            xaxis_title='Valor total — R$ milhões',
                            yaxis_title=None,
                            template='plotly_white',
                            height=550,
                            showlegend=False
                        )
        xmax = graf_atip['VL_milhoes'].max() * 1.18
        fig.update_xaxes(
                            showgrid=True,
                            range=[0, xmax],
                            gridcolor='rgba(0,0,0,0.08)',
                            zeroline=False
                        )
    
        fig.update_yaxes(
                                automargin=True
                            )
    
        st.html(
                    """
                    
                        <h2
                            Análise de impacto da atipicidade pelo ROA
                        </h2>
                        <p sstyle="text-align: justify;text-indent: 40px">
                            O gráfico abaixo apresenta o comportamento consolidado para as avaliações da atipicidade.
                        </p>
                    """, width='stretch'
                )
        st.plotly_chart(fig, width="stretch")
        fig.write_image(
                            f"{dir_FIG}/VL_ATIP_ROA.png",
                            width=1920,
                            height=1080,
                            scale=2
                        )
```

</details>

---

<a id="funcao-3"></a>

## _vis_003

Sem resumo disponível.

### Assinatura

```python
# Consulte o código-fonte de _vis_003
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `bd_path` | `Não especificado` |  |
| `st` | `Não especificado` |  |
| `empresa` | `Não especificado` |  |
| `bd_path2` | `Não especificado` |  |
| `local` | `Não especificado` |  |
| `df_INCR` | `Não especificado` |  |
| `dir_FIG` | `Não especificado` |  |
| `df_ROA` | `Não especificado` |  |
| `df_ANLS_01` | `Não especificado` |  |
| `df_BPUAR` | `Não especificado` |  |

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _vis_003(bd_path="", st=None, empresa = "", bd_path2="", local = "", 
             df_INCR = pd.DataFrame(), dir_FIG = "", df_ROA = pd.DataFrame(),
             df_ANLS_01 = pd.DataFrame(), df_BPUAR = pd.DataFrame()):
    if df_ANLS_01.empty:
        return
    with sl.connect(bd_path) as bd:
        st.html(
                    """
                        <h2>
                            Análise de Desvios e Tendência Combinada
                        </h2>
                        <p style="text-align: justify;text-indent: 40px">
                            O gráfico abaixo apresenta o comportamento consolidado para as avaliações do tipo 
                            <span style="background-color: #e8f0fe; color: #1a73e8; padding: 2px 6px; border-radius: 4px; font-weight: 500; font-size: 0.85rem;">Cd_TP_AVAL: BPR</span>. 
                            As barras indicam o <b>Delta Individual</b> de cada SisBase, permitindo identificar oscilações pontuais, 
                            enquanto a curva tracejada reflete a <b>Tendência Acumulada</b> progressiva, ordenada para destacar a trajetória macro dos desvios.
                        </p>
                    """, width='stretch'
                )
        df_deltas = df_ANLS_01[df_ANLS_01["Cd_TP_AVAL"].astype(str) == "2"].copy()
        df_deltas["Cd_SISBASE"] = df_deltas["Cd_SISBASE"].astype(str)
    
        df_deltas1 = (
                        df_deltas.groupby("Cd_SISBASE")["VAR_ABS"].sum().reset_index()
                    )
    
        df_deltas1 = df_deltas1.sort_values(by="VAR_ABS", ascending=True)
        df_deltas1["ACC_ABS"] = df_deltas1["VAR_ABS"].cumsum()
    
        df_deltas1 = df_deltas1.sort_values(by="ACC_ABS", ascending=True)
    
    
        cores = [
                    "#2b5c8f" if val >= 0 else "#e06d53" for val in df_deltas1["VAR_ABS"]
                ]
    
    
        fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    
        fig.add_trace(
                        go.Bar(
                            x=df_deltas1["Cd_SISBASE"],
                            y=df_deltas1["VAR_ABS"],
                            name="Delta Individual",
                            marker_color=cores,
                            text=[f"{val:+,.0f}" for val in df_deltas1["VAR_ABS"]],
                            textposition="outside",
                            hovertemplate="<b>Sistema: %{x}</b><br>Delta: %{y:+,.2f}<extra></extra>",
                        ),
                        secondary_y=False,
                    )
    
        fig.add_trace(
                        go.Scatter(
                            x=df_deltas1["Cd_SISBASE"],
                            y=df_deltas1["ACC_ABS"],
                            name="Total Acumulado",
                            mode="lines+markers",
                            line=dict(
                                color="#222222", width=3, dash="dash"
                            ),
                            marker=dict(size=8, color="#222222", symbol="circle"),
                            hovertemplate="<b>Acumulado até %{x}:</b><br>%{y:,.2f}<extra></extra>",
                        ),
                        secondary_y=True,
                    )
    
    
        fig.update_layout(
                            title={
                                "text": "Análise Combinada: Deltas vs. Evolução Acumulada",
                                "y": 0.95,
                                "x": 0.5,
                                "xanchor": "center",
                                "font": {"size": 18, "color": "#111111"},
                            },
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(
                                title="Código Sisbase (Cd_SISBASE)",
                                type="category",
                                tickangle=-45,
                            ),
                            yaxis=dict(
                                title="Delta Individual (VAR_ABS)",
                                showgrid=True,
                                gridcolor="#eeeeee",
                                zeroline=True,
                                zerolinecolor="#999999",
                                zerolinewidth=1.5,
                            ),
                            yaxis2=dict(
                                title="Tendência Acumulada (ACC_ABS)",
                                showgrid=False,
                            ),
                            legend=dict(
                                orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1
                            ),
                            margin=dict(l=60, r=60, t=100, b=80),
                            height=600,
                        )
        st.plotly_chart(fig, width='stretch')
        fig.write_image(
                            f"{dir_FIG}/EVL_ACM_SISBASE.png",
                            width=1920,
                            height=1080,
                            scale=2
                        )
    
        df_deltas = df_ANLS_01[df_ANLS_01["Cd_TP_AVAL"].astype(str) == "2"].copy()
        df_deltas["Cd_SISBASE"] = df_deltas["Cd_SISBASE"].astype(str)
        
        df_deltas = df_deltas.sort_values(by=["VAR_ABS"], ascending=False)
        
        cores = [
                    "#2b5c8f" if val >= 0 else "#e06d53" for val in df_deltas["VAR_ABS"]
                ]
    
        fig_deltas = go.Figure(
                                go.Bar(
                                    x=df_deltas["Cd_SISBASE"].astype(str),
                                    y=df_deltas["VAR_ABS"],
                                    marker_color=cores, 
                                    text=[f"{val:+,.0f}" for val in df_deltas["VAR_ABS"]],
                                    textposition="outside",
                                    hovertemplate="<b>Sistema: %{x}</b><br>Delta: %{y:+,.2f}<extra></extra>",
                                )
                            )
        fig_deltas.update_layout(
                                    title={
                                        "text": "Variação Absoluta (Deltas) por Cd_Sisbase",
                                        "y": 0.95,
                                        "x": 0.5,
                                        "xanchor": "center",
                                        "font": {"size": 18, "color": "#111111"},
                                    },
                                    paper_bgcolor="rgba(0,0,0,0)",  # Fundo transparente para o Streamlit
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    xaxis=dict(
                                        title="Código Sisbase (Cd_Sisbase)",
                                        type="category",
                                        tickangle=-45,
                                        linecolor="#cccccc",
                                    ),
                                    yaxis=dict(
                                        title="Delta (VAR_ABS)",
                                        showgrid=True,
                                        gridcolor="#eeeeee",
                                        zeroline=True,
                                        zerolinecolor="#999999",
                                        zerolinewidth=1.5,
                                    ),
                                    margin=dict(l=60, r=40, t=80, b=80),
                                    height=550,
                                )
        
        st.html(
                    """
                        <p style="text-align: justify;text-indent: 40px">
                            O gráfico abaixo, por sua vez, apresenta o comportamento aberto para as avaliações do tipo 
                            <span style="background-color: #e8f0fe; color: #1a73e8; padding: 2px 6px; border-radius: 4px; font-weight: 500; font-size: 0.85rem;">Cd_TP_AVAL: BPR</span>. 
                            As barras indicam o <b>Delta Individual</b> de cada SisBase.
                        </p>
                    """, width='stretch'
                )
        st.plotly_chart(fig_deltas, width='stretch')
        fig.write_image(
                            f"{dir_FIG}/VAR_ABS_SISBASE.png",
                            width=1920,
                            height=1080,
                            scale=2
                        )
    
        st.html(
                    """
                        <p style="text-align: justify;text-indent: 40px">
                            O gráfico abaixo apresenta a decomposição da <b>variação absoluta</b> observada nas avaliações do tipo 
                            <span style="background-color: #e8f0fe; color: #1a73e8; padding: 2px 6px; border-radius: 4px; font-weight: 500; font-size: 0.85rem;">Cd_TP_AVAL: BPR</span>, 
                            considerando simultaneamente o <b>material instalado</b> e os custos associados à sua instalação. 
                            Cada barra horizontal representa um <b>Cd_SISBASE</b>, que consolida o custo de mão de obra e de componentes menores utilizados no processo de instalação, 
                            enquanto as segmentações internas da barra indicam a contribuição de cada <b>Id_BP</b>, correspondente ao material instalado.
                            Como a quantidade de materiais pode ser elevada, a legenda foi removida para preservar a leitura visual do gráfico; 
                            a identificação de cada <b>Id_BP</b> pode ser consultada diretamente ao posicionar o cursor sobre os segmentos da barra.
                        </p>
                    """,
                    width="stretch"
                )
    
        df_deltas = df_ANLS_01[df_ANLS_01["Cd_TP_AVAL"].astype(str) == "2"].copy()
        df_deltas["Cd_SISBASE"] = df_deltas["Cd_SISBASE"].astype(str)
        df_deltas["Id_BP"] = df_deltas["Id_BP"].astype(str)
        df_deltas["Nr_TI"] = df_deltas["Nr_TI"].astype(str)
    
        df_plot = (
                        df_deltas
                        .groupby(["Nr_TI", "Cd_SISBASE", "Id_BP"], as_index=False)["VAR_ABS"]
                        .sum()
                        .sort_values(["Nr_TI", "VAR_ABS"], ascending=[True, True])
                    )
    
        ordem_sisbase = (
                            df_plot
                            .groupby(["Nr_TI", "Cd_SISBASE"])["VAR_ABS"]
                            .sum()
                            .reset_index()
                            .sort_values(["Nr_TI", "VAR_ABS"], ascending=[True, True])
                        )
    
        ordem_sisbase_lista = ordem_sisbase["Cd_SISBASE"].tolist()
    
        fig_deltas = px.bar(
                                df_plot,
                                x="VAR_ABS",
                                y="Cd_SISBASE",
                                color="Id_BP",
                                orientation="h",
                                category_orders={"Cd_SISBASE": ordem_sisbase_lista},
                                text=df_plot["VAR_ABS"].map(lambda v: f"{v:+,.0f}"),
                                title="Variação Absoluta por Cd_Sisbase e Id_BP",
                                labels={
                                    "VAR_ABS": "Delta (VAR_ABS)",
                                    "Cd_SISBASE": "Código Sisbase",
                                    "Id_BP": "Id_BP"
                                },
                            )
        
        cores_faixa = [
                        "rgba(173,216,230,1)",
                        "rgba(245,245,245,1)"
                    ]
    
        ifaixa = 0
        for nr_ti, grupo in ordem_sisbase.groupby("Nr_TI", sort=False):
    
            primeiro_sisbase = grupo["Cd_SISBASE"].iloc[0]
            ultimo_sisbase = grupo["Cd_SISBASE"].iloc[-1]
    
            fig_deltas.add_hrect(
                                    y0=primeiro_sisbase,
                                    y1=ultimo_sisbase,
                                    fillcolor=cores_faixa[ifaixa % 2],
                                    opacity=0.10,
                                    layer="below",
                                    line_width=3,
                                    line_color="black",
                                )
    
            fig_deltas.add_annotation(
                                        x=1.01,
                                        xref="paper",
                                        y=grupo["Cd_SISBASE"].iloc[len(grupo) // 2],
                                        yref="y",
                                        text=f"{nr_ti}",
                                        showarrow=False,
                                        xanchor="left",
                                        font=dict(size=11),
                                    )
            ifaixa += 1
    
        fig_deltas.update_traces(
                                    hovertemplate=
                                    "<b>SisBase:</b> %{y}<br>" +
                                    "<b>Id_BP:</b> %{fullData.name}<br>" +
                                    "<b>Delta:</b> %{x:+,.2f}<extra></extra>"
                                )
    
        fig_deltas.update_layout(
                                    barmode="relative",
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    xaxis=dict(
                                        title="Delta (VAR_ABS)",
                                        showgrid=True,
                                        gridcolor="#eeeeee",
                                        zeroline=True,
                                        zerolinecolor="#999999",
                                        zerolinewidth=1.5,
                                    ),
                                    yaxis=dict(
                                        title="Código Sisbase (Cd_SISBASE)",
                                        type="category",
                                    ),
                                    showlegend=False,
                                    margin=dict(l=120, r=40, t=90, b=60),
                                    height=max(550, 22 * df_plot["Cd_SISBASE"].nunique()),
                                )
    
    
        st.plotly_chart(fig_deltas, width="stretch")
        fig.write_image(
                            f"{dir_FIG}/VAR_ABS_SISBASE_idBP.png",
                            width=1920,
                            height=1080,
                            scale=2
                        )
    
        st.html(
                    """

                        <p style="text-align: justify;text-indent: 40px">
                            Os dados tabulares empregados são apresentados abaixo.
                        </p>
                    """, width='stretch'
                )
        st.dataframe(df_ANLS_01, width='stretch', hide_index=True)
    
        df_ANLS_01['VL_VF_AT'] = df_ANLS_01['VL_VF_UNIT_AT'] * df_ANLS_01['Qtd']
        df_ANLS_01b = (df_ANLS_01[df_ANLS_01["Cd_TP_AVAL"].astype(str) == "2"]
                    .groupby(['Id_BP', 'Cd_UND_AIS'], dropna=False)[['Qtd_AIS','VL_VOC_VFa','Qtd','VL_VF_AT']]
                    .sum()
                    .reset_index()
                    .rename(columns={'Qtd':'Qtd_BPUAR'}))
        df_PROV = df_INCR[['Id_BP', 'Txt_DESC_TECN']].drop_duplicates(subset=['Id_BP'], keep='first')
        df_ANLS_01b = df_ANLS_01b.merge(df_PROV, how='left', on = 'Id_BP')
        df_ANLS_01b['VL_VF_VOC_UNIT_AT'] = df_ANLS_01b['VL_VOC_VFa'] / df_ANLS_01b['Qtd_AIS']
        df_ANLS_01b['VL_VF_UNIT_AT'] = df_ANLS_01b['VL_VF_AT'] / (df_ANLS_01b['Qtd_BPUAR'] + 1e-4)
        df_ANLS_01b = df_ANLS_01b[['Id_BP', 'Txt_DESC_TECN', 'Cd_UND_AIS','Qtd_AIS','VL_VF_VOC_UNIT_AT','Qtd_BPUAR','VL_VF_UNIT_AT']]
    
    
        df_mat = df_ANLS_01b.copy()
    
        cols_num = [
                        "VL_VF_VOC_UNIT_AT",
                        "VL_VF_UNIT_AT",
                        "Qtd_AIS",
                        "Qtd_BPUAR",
                    ]
    
        df_mat["Id_BP"] = df_mat["Id_BP"].astype(str)
        df_mat["Txt_DESC_TECN"] = df_mat["Txt_DESC_TECN"].astype(str)
    
        df_plot = (
                        df_mat
                        .groupby(["Id_BP", "Txt_DESC_TECN"], as_index=False)
                        .agg(
                            VL_VF_VOC_UNIT_AT=("VL_VF_VOC_UNIT_AT", "mean"),
                            VL_VF_UNIT_AT=("VL_VF_UNIT_AT", "mean"),
                            Qtd_AIS=("Qtd_AIS", "sum"),
                            Qtd_BPUAR=("Qtd_BPUAR", "sum"),
                        )
                    )
    
        df_plot["DELTA_UNIT"] = (
                                    df_plot["VL_VF_UNIT_AT"] - df_plot["VL_VF_VOC_UNIT_AT"]
                                )
    
        df_plot["VAR_PERC_UNIT"] = np.where(
                                                df_plot["VL_VF_VOC_UNIT_AT"] != 0,
                                                (df_plot["VL_VF_UNIT_AT"] / df_plot["VL_VF_VOC_UNIT_AT"] - 1) * 100,
                                                np.nan
                                            )
    
        df_plot["PESO_COMPRAS_PERC"] = np.where(
                                                    df_plot["Qtd_AIS"] != 0,
                                                    (df_plot["Qtd_BPUAR"] / df_plot["Qtd_AIS"]) * 100,
                                                    np.nan
                                                )
    
        df_plot["ADERENCIA_VOLUME"] = np.where(
                                                    (df_plot["Qtd_AIS"] > 0) & (df_plot["Qtd_BPUAR"] > 0),
                                                    np.minimum(df_plot["Qtd_AIS"], df_plot["Qtd_BPUAR"])
                                                    / np.maximum(df_plot["Qtd_AIS"], df_plot["Qtd_BPUAR"]),
                                                    0
                                                )
    
        df_plot["ADERENCIA_VOLUME_PERC"] = df_plot["ADERENCIA_VOLUME"] * 100
        df_plot["IMPACTO_POTENCIAL"] = (
                                            df_plot["DELTA_UNIT"] * df_plot["Qtd_AIS"]
                                        )
        LIMIAR_REPRESENTATIVIDADE = 0.50
    
        df_plot["LIMIAR_REPRESENTATIVIDADE"] = (
                                                    df_plot["ADERENCIA_VOLUME"] < LIMIAR_REPRESENTATIVIDADE
                                                )
        
        df_plot["FAIXA_ADERENCIA"] = np.select(
                                                [
                                                    df_plot["PESO_COMPRAS_PERC"].between(80, 120),
    
                                                    (
                                                        df_plot["PESO_COMPRAS_PERC"].between(50, 80, inclusive="left")
                                                    ) | (
                                                        df_plot["PESO_COMPRAS_PERC"].between(120, 150, inclusive="right")
                                                    ),
    
                                                    (
                                                        df_plot["PESO_COMPRAS_PERC"].between(20, 50, inclusive="left")
                                                    ) | (
                                                        df_plot["PESO_COMPRAS_PERC"].between(150, 300, inclusive="right")
                                                    ),
                                                ],
                                                [
                                                    "Alta",
                                                    "Moderada",
                                                    "Baixa",
                                                ],
                                                default="Crítica"
                                            )
    
        cores_aderencia = {
                                "Alta": "#2b8a3e",
                                "Moderada": "#aff04e",
                                "Baixa": "#fdbf14",
                                "Crítica": "#fc0303"
                            }
        df_representativo = df_plot[
                                        ~df_plot["LIMIAR_REPRESENTATIVIDADE"]
                                    ].copy()
    
        df_outlier = df_plot[
                                df_plot["LIMIAR_REPRESENTATIVIDADE"]
                            ].copy()
        st.html(
                    f"""
                        <p style="text-align: justify;text-indent: 40px">
                            A análise a seguir busca avaliar a representatividade do preço de compra dos materiais frente ao volume 
                            efetivamente imobilizado. Para isso, calcula-se uma métrica de aderência entre o volume comprado 
                            (<b>Qtd_BPUAR</b>) e o volume instalado (<b>Qtd_AIS</b>), considerando a razão entre o menor e o maior 
                            volume observado. Dessa forma, situações em que compras e imobilizações apresentam magnitudes semelhantes 
                            tendem a possuir alta aderência, enquanto diferenças relevantes entre esses volumes reduzem a 
                            representatividade do preço de aquisição como referência para o custo instalado.
    
                            Com base nesse indicador, os materiais foram segmentados utilizando um limiar de aderência de <b>50%</b>. 
                            Acima desse patamar, considera-se que o preço de compra possui representatividade suficiente para 
                            suportar análises econômicas da base instalada. Abaixo desse limite, recomenda-se análise 
                            dos resultados, uma vez que os volumes movimentados no período podem não refletir adequadamente a 
                            composição do ativo imobilizado.
    
                            A aderência entre os volumes comprados e imobilizados descreve sobre a eficiência do ciclo de utilização 
                            dos materiais. Baixos níveis de aderência podem indicar que parte relevante dos itens adquiridos permanece 
                            em estoque ou em ordens em curso por períodos prolongados antes de seu reconhecimento tarifário, ou, em 
                            sentido contrário, que as imobilizações estão sendo realizadas com base em estoques constituídos em 
                            ciclos anteriores.
    
                            Sob a perspectiva gerencial, a redução do intervalo entre a aquisição dos materiais e sua efetiva 
                            imobilização tende a aumentar a aderência observada, tornando os preços de compra mais representativos 
                            dos investimentos realizados. Além de melhorar a qualidade das análises econômicas e da formação de 
                            custos, reduzindo capital imobilizado, custos de armazenagem, riscos de obsolescência e distorções entre 
                            os movimentos de compra e a execução dos investimentos e os custos reconhecidos na base.
    
                        </p>
                    """,
                    width="stretch"
                )
    
        df_rep_plot = df_representativo.sort_values(
                                                        "IMPACTO_POTENCIAL",
                                                        ascending=True
                                                    )
        df_rep_plot["COR"] = (
                                df_rep_plot["FAIXA_ADERENCIA"]
                                .map(cores_aderencia)
                            )
        fig_rep = px.bar(
                            df_rep_plot,
                            x="IMPACTO_POTENCIAL",
                            y="Id_BP",
                            orientation="h",
                            custom_data=[
                                "Txt_DESC_TECN",
                                "VL_VF_VOC_UNIT_AT",
                                "VL_VF_UNIT_AT",
                                "DELTA_UNIT",
                                "VAR_PERC_UNIT",
                                "Qtd_AIS",
                                "Qtd_BPUAR",
                                "PESO_COMPRAS_PERC",
                                "ADERENCIA_VOLUME_PERC",
                            ],
                            title="Materiais representativos: impacto potencial da variação de preço",
                            labels={
                                "IMPACTO_POTENCIAL": "Impacto potencial",
                                "Id_BP": "Material instalado",
                                "color": "",
                            },
                        )
    
        fig_rep.update_traces(
                                    text=df_rep_plot["IMPACTO_POTENCIAL"].map(lambda v: f"{v:+,.0f}"),
                                    textposition="outside",
                                    marker_color=df_rep_plot["COR"],
                                    hovertemplate=
                                        "<b>Material instalado:</b> %{y}<br>"
                                        "<b>Descrição:</b> %{customdata[0]}<br><br>"
                                        "<b>Impacto potencial:</b> %{x:+,.2f}<br>"
                                        "<b>Custo unitizado instalado:</b> %{customdata[1]:,.2f}<br>"
                                        "<b>Custo médio aquisição:</b> %{customdata[2]:,.2f}<br>"
                                        "<b>Delta unitário:</b> %{customdata[3]:+,.2f}<br>"
                                        "<b>Variação unitária:</b> %{customdata[4]:+,.2f}%<br><br>"
                                        "<b>Qtd imobilizada:</b> %{customdata[5]:,.2f}<br>"
                                        "<b>Qtd compras:</b> %{customdata[6]:,.2f}<br>"
                                        "<b>Peso compras/base:</b> %{customdata[7]:,.2f}%<br>"
                                        "<b>Aderência de volume:</b> %{customdata[8]:,.2f}%"
                                        "<extra></extra>"
                                )
    
        fig_rep.update_layout(
                                showlegend=False,
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                xaxis=dict(
                                    title="Impacto potencial = Delta unitário × Qtd_AIS",
                                    showgrid=True,
                                    gridcolor="#eeeeee",
                                    zeroline=True,
                                    zerolinecolor="#999999",
                                    zerolinewidth=1.5,
                                ),
                                yaxis=dict(
                                    title="Material instalado (Id_BP)",
                                    type="category",
                                ),
                                margin=dict(l=160, r=60, t=90, b=80),
                                height=max(550, 22 * df_rep_plot["Id_BP"].nunique()),
                            )
    
        st.plotly_chart(fig_rep, width="stretch")
    
        df_out_plot = df_outlier.sort_values(
                                                "ADERENCIA_VOLUME_PERC",
                                                ascending=True
                                            )
    
        fig_out = px.bar(
                            df_out_plot,
                            x="ADERENCIA_VOLUME_PERC",
                            y="Id_BP",
                            orientation="h",
                            custom_data=[
                                "Txt_DESC_TECN",
                                "Qtd_AIS",
                                "Qtd_BPUAR",
                                "PESO_COMPRAS_PERC",
                                "VL_VF_VOC_UNIT_AT",
                                "VL_VF_UNIT_AT",
                                "VAR_PERC_UNIT",
                                "IMPACTO_POTENCIAL",
                            ],
                            title="Materiais não representativos: baixa aderência entre compras e imobilização",
                            labels={
                                "ADERENCIA_VOLUME_PERC": "Aderência de volume (%)",
                                "Id_BP": "Material instalado",
                            },
                        )
    
        fig_out.update_traces(
                                    marker_color="#e06d53",
                                    text=df_out_plot["ADERENCIA_VOLUME_PERC"].map(lambda v: f"{v:,.1f}%"),
                                    textposition="outside",
                                    hovertemplate=
                                        "<b>Material instalado:</b> %{y}<br>"
                                        "<b>Descrição:</b> %{customdata[0]}<br><br>"
                                        "<b>Aderência de volume:</b> %{x:,.2f}%<br>"
                                        "<b>Qtd imobilizada:</b> %{customdata[1]:,.2f}<br>"
                                        "<b>Qtd compras:</b> %{customdata[2]:,.2f}<br>"
                                        "<b>Peso compras/base:</b> %{customdata[3]:,.2f}%<br><br>"
                                        "<b>Custo unitizado instalado:</b> %{customdata[4]:,.2f}<br>"
                                        "<b>Custo médio aquisição:</b> %{customdata[5]:,.2f}<br>"
                                        "<b>Variação unitária:</b> %{customdata[6]:+,.2f}%<br>"
                                        "<b>Impacto potencial:</b> %{customdata[7]:+,.2f}"
                                        "<extra></extra>"
                                )
    
        fig_out.add_vline(
                            x=LIMIAR_REPRESENTATIVIDADE * 100,
                            line_width=2,
                            line_dash="dash",
                            line_color="#999999",
                            annotation_text=f"Limite Representatividade: {LIMIAR_REPRESENTATIVIDADE:.2%}",
                            annotation_position="top right"
                        )
    
        fig_out.update_layout(
                                showlegend=False,
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                xaxis=dict(
                                    title="Aderência = min(Qtd_AIS, Qtd_BPUAR) / max(Qtd_AIS, Qtd_BPUAR)",
                                    range=[0, max(5, min(100, LIMIAR_REPRESENTATIVIDADE * 100 * 1.4))],
                                    showgrid=True,
                                    gridcolor="#eeeeee",
                                    zeroline=True,
                                    zerolinecolor="#999999",
                                ),
                                yaxis=dict(
                                    title="Material instalado (Id_BP)",
                                    type="category",
                                ),
                                margin=dict(l=160, r=60, t=90, b=80),
                                height=max(450, 24 * df_out_plot["Id_BP"].nunique()),
                            )
    
        st.plotly_chart(fig_out, width="stretch")
        faixas_risco = ["Baixa", "Crítica"]
        df_risco = df_plot[
                                (
                                    df_plot["FAIXA_ADERENCIA"].isin(faixas_risco)
                                )
                                | (
                                    df_plot.get("OUTLIER_REPRESENTATIVIDADE", False)
                                )
                            ].copy()
    
        df_risco["IMPACTO_ABS"] = df_risco["IMPACTO_POTENCIAL"].abs()
        df_risco = df_risco.sort_values(
                                            "IMPACTO_ABS",
                                            ascending=False
                                        )
        total = df_risco["IMPACTO_ABS"].sum()
        df_risco["PARTICIPACAO"] = (
                                        df_risco["IMPACTO_ABS"] / total
                                    )
        df_risco["PARTICIPACAO_ACUM"] = (
                                            df_risco["PARTICIPACAO"].cumsum()
                                        )
        df_risco["CLASSE_ABC"] = np.select(
                                            [
                                                df_risco["PARTICIPACAO_ACUM"] <= 0.80,
                                                df_risco["PARTICIPACAO_ACUM"] <= 0.95,
                                            ],
                                            [
                                                "A",
                                                "B",
                                            ],
                                            default="C"
                                        )
        
        df_tabela_abc = (
                            df_risco[
                                ["Id_BP", "Txt_DESC_TECN", "IMPACTO_ABS", "CLASSE_ABC"]
                            ]
                            .sort_values(["CLASSE_ABC", "IMPACTO_ABS"], ascending=[True, False])
                            .copy()
                        )
    
        cores_abc = {
                        "A": {"bg": "#fdecea", "fg": "#b42318"},
                        "B": {"bg": "#fff4e5", "fg": "#b54708"},
                        "C": {"bg": "#eaf7ef", "fg": "#1f7a3f"},
                    }
    
        linhas_html = ""
    
        for _, row in df_tabela_abc.iterrows():
            classe = row["CLASSE_ABC"]
            cor = cores_abc.get(classe, {"bg": "#f2f4f7", "fg": "#344054"})
    
            linhas_html += f"""
                                <tr>
                                    <td>{html.escape(str(row["Id_BP"]))}</td>
                                    <td>{html.escape(str(row["Txt_DESC_TECN"]))}</td>
                                    <td style="text-align:right;">{row["IMPACTO_ABS"]:,.2f}</td>
                                    <td style="text-align:center;">
                                        <span style="
                                            background-color:{cor["bg"]};
                                            color:{cor["fg"]};
                                            padding:4px 10px;
                                            border-radius:999px;
                                            font-weight:600;
                                            font-size:0.80rem;
                                        ">
                                            Classe {html.escape(str(classe))}
                                        </span>
                                    </td>
                                </tr>
                            """
    
        st.html(
                    f"""
                            <p style="text-align: justify;text-indent: 40px">
                                A tabela abaixo apresenta os materiais classificados pelo método <b>ABC</b>, considerando o 
                                <b>impacto potencial absoluto</b>. A classe <b>A</b> reúne os itens de maior relevância econômica, 
                                responsáveis pela maior parcela acumulada do impacto; a classe <b>B</b> representa relevância 
                                intermediária; e a classe <b>C</b> concentra os itens de menor contribuição individual.
                            </p>

                        <div style="
                            overflow-x:auto;
                            border:1px solid #e5e7eb;
                            border-radius:10px;
                        ">
                            <table style="
                                width:100%;
                                border-collapse:collapse;
                                font-size:0.88rem;
                            ">
                                <thead>
                                    <tr style="background-color:#f8fafc;">
                                        <th style="text-align:left; padding:10px 12px; border-bottom:1px solid #e5e7eb;">Id_BP</th>
                                        <th style="text-align:left; padding:10px 12px; border-bottom:1px solid #e5e7eb;">Descrição técnica</th>
                                        <th style="text-align:right; padding:10px 12px; border-bottom:1px solid #e5e7eb;">Impacto absoluto</th>
                                        <th style="text-align:center; padding:10px 12px; border-bottom:1px solid #e5e7eb;">Classe ABC</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {linhas_html}
                                </tbody>
                            </table>
                        </div><br>
                        <div style="
                            margin-bottom:12px;
                            padding:18px 20px;
                            background:linear-gradient(90deg, rgba(43, 92, 143, 0.06) 0%, rgba(255,255,255,0) 100%);
                            border-left:4px solid #2b5c8f;
                            border-radius:0 8px 8px 0;
                        ">
                            <p style="
                                margin:0;
                                color:#555555;
                                font-size:0.95rem;
                                line-height:1.6;
                                text-align:justify;
                            ">
                                A tabela abaixo apresenta os dados brutos empregados.
                            </p>
                        </div>
                    """,
                    width="stretch"
                )
        
        st.dataframe(df_risco, width='stretch', hide_index=True)
    
        ids_classe_a = (
                            df_risco.loc[
                                df_risco["CLASSE_ABC"] == "A",
                                "Id_BP"
                            ]
                            .astype(str)
                            .unique()
                        )
    
        df_BPUAR["Id_BP"] = df_BPUAR["Id_BP"].astype(str)
        df_BPUAR_A = (
                        df_BPUAR[
                            df_BPUAR["Id_BP"].isin(ids_classe_a)
                        ]
                        .copy()
                    )
        cod_itens = "', '".join(df_BPUAR_A['COD_ITEM'])
    
        dt_ARQ = max_arq("BP_EC", bd, empresa, st)
        if dt_ARQ:
            SQLq = f"""SELECT 
                                Dt_NF,
                                COD_ITEM,
                                Txt_Desc_Mat,
                                FLG_TPNF * Qtd AS Qtd,
                                Cd_Unid,
                                VL_TOT_LIQ,
                                VL_TOT_ICMS,
                                VL_TOT_IPI,
                                VL_DIFAL,
                                VL_ST
                        FROM 
                            BP_EC 
                        WHERE 
                            Dt_ARQ = '{dt_ARQ}' AND COD_ITEM in ('{cod_itens}') AND FLG_TP = 1 AND FLG_BPR = 1
                        ORDER BY
                            COD_ITEM, Dt_NF"""
            df_BPEC = pd.read_sql(SQLq, bd)
            for campo in ['Dt_NF']:
                df_BPEC[campo] = pd.to_datetime(df_BPEC[campo], errors="coerce", format="%Y-%m-%d")
            for campo in ['Qtd','VL_TOT_LIQ','VL_TOT_ICMS','VL_TOT_IPI','VL_DIFAL','VL_ST']:
                df_BPEC[campo] = pd.to_numeric(df_BPEC[campo], errors="coerce")
    
            df_BPEC = (df_BPEC
                    .groupby(['COD_ITEM','Txt_Desc_Mat','Cd_Unid','Dt_NF'], dropna=False)[['Qtd','VL_TOT_LIQ',
                                'VL_TOT_ICMS','VL_TOT_IPI','VL_DIFAL','VL_ST']]
                        .sum()
                        .reset_index())
                                
            df_BPEC['VL_UNIT_HIST'] = (
                                        (df_BPEC['VL_TOT_LIQ'].fillna(0) +
                                        df_BPEC['VL_TOT_ICMS'].fillna(0) +
                                        df_BPEC['VL_TOT_IPI'].fillna(0) +
                                        df_BPEC['VL_ST'].fillna(0))  / df_BPEC['Qtd'].fillna(1)
                                    )
            df_BPEC = df_BPEC.sort_values(by=['COD_ITEM','Dt_NF'])
            
            df_hist_base = df_BPEC.copy()
    
            df_hist_base["COD_ITEM"] = df_hist_base["COD_ITEM"].astype(str)
            df_hist_base = df_hist_base[
                                            (df_hist_base["Dt_NF"].notna()) &
                                            (df_hist_base["Qtd"] > 0) &
                                            (df_hist_base["VL_UNIT_HIST"].notna())
                                        ].copy()
    
            df_hist_base["PERIODO"] = df_hist_base["Dt_NF"].dt.to_period("M").dt.to_timestamp()
    
            df_hist_base["VL_TOTAL_HIST"] = (
                                                df_hist_base["Qtd"] * df_hist_base["VL_UNIT_HIST"]
                                            )
            
            st.html(
                        """
                            <p style="text-align: justify;text-indent: 40px">
                                Os gráficos a seguir detalham o histórico de aquisições dos materiais classificados como 
                                <b>Classe A</b> na análise ABC de impacto potencial. O objetivo é compreender a dinâmica temporal 
                                das compras e avaliar em que medida os preços observados no período recente são representativos da 
                                formação de custo desses materiais ao longo do tempo.
                            </p>
    
                            <p style="text-align: justify;text-indent: 40px">
                                Em cada gráfico, as barras representam as quantidades adquiridas em cada período e os rótulos sobre 
                                elas indicam o valor médio unitário histórico das compras realizadas. A linha tracejada mostra a 
                                evolução do valor médio acumulado histórico, permitindo identificar a influência de compras relevantes 
                                na formação do custo médio do material. Os indicadores apresentados abaixo de cada gráfico complementam 
                                a análise ao evidenciar aspectos como concentração das aquisições, frequência dos ciclos de compra, 
                                estabilidade dos preços e idade média do estoque.
                            </p>
    
                            <p style="text-align: justify;text-indent: 40px">
                                Os indicadores apresentados abaixo de cada gráfico complementam essa análise. A <b>Quantidade Total Comprada</b> 
                                representa o volume acumulado de aquisições observado no histórico. O indicador <b>Maior Compra / Total</b> 
                                mede o grau de concentração das aquisições, evidenciando a dependência de eventos específicos de compra. 
                                O <b>Tempo Médio entre Compras</b> indica a frequência típica dos ciclos de reposição. A <b>Idade Média Ponderada</b> 
                                estima há quanto tempo, em média, os materiais atualmente considerados foram adquiridos, ponderando os volumes 
                                comprados em cada período. Por fim, o <b>Coeficiente de Variação (CV) do Preço Histórico</b> mede a estabilidade 
                                dos preços praticados ao longo do tempo, permitindo distinguir materiais com comportamento de custo mais previsível 
                                daqueles sujeitos a maior volatilidade.
                            </p>
    
                            <p style="text-align: justify;text-indent: 40px">
                                Em conjunto, essas informações permitem identificar materiais cujos preços são formados por poucas compras de 
                                grande volume, materiais com aquisições recorrentes e estáveis, bem como situações em que o custo atualmente 
                                observado pode refletir decisões de compra realizadas há vários anos. Sob a ótica da gestão de estoques, a análise 
                                auxilia na avaliação do sincronismo entre aquisição e utilização dos materiais, contribuindo para a compreensão dos 
                                efeitos do ciclo de suprimento sobre os custos dos ativos e para a identificação de oportunidades de redução do tempo 
                                entre a compra e sua efetiva imobilização.
                            </p>
                        """,
                        width="stretch"
                    )
            for cod_item in sorted(df_hist_base["COD_ITEM"].unique()):
    
                df_item = df_hist_base[
                                            df_hist_base["COD_ITEM"] == cod_item
                                        ].copy()
    
                desc_item = (
                                df_item["Txt_Desc_Mat"].dropna().astype(str).iloc[0]
                                if not df_item["Txt_Desc_Mat"].dropna().empty
                                else ""
                            )
    
                cd_unid = (
                                df_item["Cd_Unid"].dropna().astype(str).iloc[0]
                                if "Cd_Unid" in df_item.columns and not df_item["Cd_Unid"].dropna().empty
                                else ""
                            )
    
                df_plot_item = (
                                    df_item
                                    .groupby("PERIODO", as_index=False)
                                    .agg(
                                        QTD_COMPRA=("Qtd", "sum"),
                                        VL_TOTAL_HIST=("VL_TOTAL_HIST", "sum"),
                                    )
                                )
    
                df_plot_item["VL_MEDIO_HIST"] = np.where(
                                                            df_plot_item["QTD_COMPRA"] != 0,
                                                            df_plot_item["VL_TOTAL_HIST"] / df_plot_item["QTD_COMPRA"],
                                                            np.nan
                                                        )
    
                df_plot_item = df_plot_item.sort_values("PERIODO")
    
                df_plot_item["QTD_ACUM"] = df_plot_item["QTD_COMPRA"].cumsum()
                df_plot_item["VL_TOTAL_ACUM"] = df_plot_item["VL_TOTAL_HIST"].cumsum()
    
                df_plot_item["VL_MEDIO_ACUM_HIST"] = np.where(
                                                                    df_plot_item["QTD_ACUM"] != 0,
                                                                    df_plot_item["VL_TOTAL_ACUM"] / df_plot_item["QTD_ACUM"],
                                                                    np.nan
                                                                )
    
                fig = make_subplots(specs=[[{"secondary_y": True}]])
    
                fig.add_trace(
                                go.Bar(
                                    x=df_plot_item["PERIODO"],
                                    y=df_plot_item["QTD_COMPRA"],
                                    name="Quantidade comprada",
                                    text=df_plot_item["VL_MEDIO_HIST"].map(lambda v: f"{v:,.2f}"),
                                    textposition="outside",
                                    hovertemplate=
                                        "<b>Período:</b> %{x|%m/%Y}<br>"
                                        "<b>Qtd comprada:</b> %{y:,.2f}<br>"
                                        "<b>Valor médio histórico:</b> %{text}<extra></extra>",
                                ),
                                secondary_y=False,
                            )
    
                fig.add_trace(
                                go.Scatter(
                                    x=df_plot_item["PERIODO"],
                                    y=df_plot_item["VL_MEDIO_ACUM_HIST"],
                                    name="Valor médio acumulado histórico",
                                    mode="lines+markers",
                                    line=dict(width=3, dash="dash"),
                                    marker=dict(size=7),
                                    hovertemplate=
                                        "<b>Período:</b> %{x|%m/%Y}<br>"
                                        "<b>Valor médio acumulado:</b> %{y:,.2f}<extra></extra>",
                                ),
                                secondary_y=True,
                            )
    
                fig.update_layout(
                    title={
                        "text": f"Histórico de compras — {cod_item} | {desc_item}",
                        "x": 0.5,
                        "xanchor": "center",
                        "font": {"size": 15},
                    },
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(
                        title="Período da compra",
                        tickformat="%m/%Y",
                        showgrid=False,
                    ),
                    yaxis=dict(
                        title=f"Quantidade comprada {f'({cd_unid})' if cd_unid else ''}",
                        showgrid=True,
                        gridcolor="#eeeeee",
                        zeroline=True,
                        zerolinecolor="#999999",
                    ),
                    yaxis2=dict(
                        title="Valor médio acumulado histórico",
                        showgrid=False,
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                    ),
                    margin=dict(l=70, r=70, t=90, b=70),
                    height=520,
                )
    
                st.plotly_chart(fig, width="stretch")
                qtd_total = df_plot_item["QTD_COMPRA"].sum()
                maior_compra = df_plot_item["QTD_COMPRA"].max()
                pct_maior_compra = (
                                        maior_compra / qtd_total * 100
                                        if qtd_total != 0
                                        else 0
                                    )
    
                datas_compra = df_plot_item.loc[
                                                    df_plot_item["QTD_COMPRA"] > 0,
                                                    "PERIODO"
                                                ].sort_values()
    
                intervalos = datas_compra.diff().dt.days.dropna()
                tempo_medio_entre_compras = (
                                                intervalos.mean()
                                                if not intervalos.empty
                                                else np.nan
                                            )
    
                maior_intervalo_sem_compras = (
                                                    intervalos.max()
                                                    if not intervalos.empty
                                                    else np.nan
                                                )
    
                cv_preco = (
                                df_plot_item["VL_MEDIO_HIST"].std()
                                / df_plot_item["VL_MEDIO_HIST"].mean()
                                * 100
                                if df_plot_item["VL_MEDIO_HIST"].mean() != 0
                                else np.nan
                            )
    
                data_ref = df_hist_base["Dt_NF"].max()
    
                df_idade = df_item.copy()
                df_idade["IDADE_DIAS"] = (
                                            data_ref - df_idade["Dt_NF"]
                                        ).dt.days
    
                idade_media_ponderada = (
                                            (df_idade["IDADE_DIAS"] * df_idade["Qtd"]).sum()
                                            / df_idade["Qtd"].sum()
                                            if df_idade["Qtd"].sum() != 0
                                            else np.nan
                                        )
    
                idade_media_anos = idade_media_ponderada / 365 if pd.notna(idade_media_ponderada) else np.nan
                qtd_total = f"{qtd_total:,.0f}".replace(",","x").replace(".",",").replace("x",".")
                pct_maior_compra = f"{pct_maior_compra:,.1f}".replace(",","x").replace(".",",").replace("x",".")
                tempo_medio_entre_compras = f"{tempo_medio_entre_compras:,.0f}".replace(",","x").replace(".",",").replace("x",".")
                idade_media_anos = f"{idade_media_anos:,.1f}".replace(",","x").replace(".",",").replace("x",".")
                cv_preco = f"{cv_preco:,.1f}".replace(",","x").replace(".",",").replace("x",".")
    
                st.html(
                            f"""
                            <div style="
                                font-family:'Source Sans Pro', -apple-system, BlinkMacSystemFont, sans-serif;
                                display:grid;
                                grid-template-columns:repeat(5, 1fr);
                                gap:12px;
                                margin-top:-10px;
                                margin-bottom:35px;
                            ">
                                <div style="padding:14px 16px; border:1px solid #e5e7eb; border-radius:10px; background:#ffffff;">
                                    <div style="font-size:0.75rem; color:#667085; margin-bottom:4px;">Qtd total comprada</div>
                                    <div style="font-size:1.25rem; font-weight:700; color:#111827;">{qtd_total}</div>
                                </div>
    
                                <div style="padding:14px 16px; border:1px solid #e5e7eb; border-radius:10px; background:#ffffff;">
                                    <div style="font-size:0.75rem; color:#667085; margin-bottom:4px;">Maior compra / total</div>
                                    <div style="font-size:1.25rem; font-weight:700; color:#111827;">{pct_maior_compra}%</div>
                                </div>
    
                                <div style="padding:14px 16px; border:1px solid #e5e7eb; border-radius:10px; background:#ffffff;">
                                    <div style="font-size:0.75rem; color:#667085; margin-bottom:4px;">Tempo médio entre compras</div>
                                    <div style="font-size:1.25rem; font-weight:700; color:#111827;">
                                        {tempo_medio_entre_compras} dias
                                    </div>
                                </div>
    
                                <div style="padding:14px 16px; border:1px solid #e5e7eb; border-radius:10px; background:#ffffff;">
                                    <div style="font-size:0.75rem; color:#667085; margin-bottom:4px;">Idade média ponderada</div>
                                    <div style="font-size:1.25rem; font-weight:700; color:#111827;">
                                        {idade_media_anos} anos
                                    </div>
                                </div>
    
                                <div style="padding:14px 16px; border:1px solid #e5e7eb; border-radius:10px; background:#ffffff;">
                                    <div style="font-size:0.75rem; color:#667085; margin-bottom:4px;">CV do preço histórico</div>
                                    <div style="font-size:1.25rem; font-weight:700; color:#111827;">
                                        {cv_preco}%
                                    </div>
                                </div>
                            </div>
                            """,
                            width="stretch"
                        )
```

</details>

---

<a id="funcao-4"></a>

## _vis_004

Sem resumo disponível.

### Assinatura

```python
# Consulte o código-fonte de _vis_004
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `bd_path` | `string` |  |
| `st` | `objeto` |  |
| `empresa` | `string` |  |
| `bd_path2` | `string` |  |
| `local` | `string` |  |
| `df_INCR` | `DataFrame` |  |
| `dir_FIG` | `string` |  |
| `df_ROA` | `DataFrame` |  |
| `df_ANLS_01` | `DataFrame` |  |
| `df_BPUAR` | `DataFrame` |  |
| `df_BAIXAS` | `DataFrame` |  |

### Dependências

- `SRC.calculos`
- `UTILS.imp_tbl_forma_001`
- `numpy`
- `pandas`
- `plotly.express`
- `plotly.graph_objects`
- `plotly.subplots.make_subplots`
- `sqlite3`
- `streamlit`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _vis_004(bd_path="", st=None, empresa = "", bd_path2="", local = "", 
             df_INCR = pd.DataFrame(), dir_FIG = "", df_ROA = pd.DataFrame(),
             df_ANLS_01 = pd.DataFrame(), df_BPUAR = pd.DataFrame(),
             df_BAIXAS = pd.DataFrame()):
    if df_BAIXAS.empty:
        return
    with sl.connect(bd_path) as bd:
        df_ANLS_02 = (df_BAIXAS[(df_BAIXAS['FLG_AJST_CTB'].astype(str)=='0')]
                    .groupby(['Nr_TI', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 
                    'Nr_A4', 'Nr_A5', 'Nr_A6', 'Cd_UAR', 'Cd_UND_AIS'], dropna=False)[['Qtd_INI','Qtd_FIN','VL_VOC_INI','VL_VOC_FIN']]
                    .sum()
                    .reset_index())
            
        
        df_ANLS_02['Qtd_BAIXAS'] = df_ANLS_02['Qtd_INI'].fillna(0) - df_ANLS_02['Qtd_FIN'].fillna(0)
        df_ANLS_02['Cd_SISBASE'] ="ND"
        LST_TUC = df_ANLS_02[(df_ANLS_02['Cd_UAR'] != 'UAR')][['Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                                'Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_SISBASE']].drop_duplicates()
    
        LST_TUC = clcpr.tst_cod_sisbase(LST_TUC, st.session_state.dt_fim, st=st)
        df_ANLS_02 = df_ANLS_02.merge(LST_TUC[['Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                                'Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_SISBASE_SFF','Cd_FOR_COGE_SFF',
                                                'Nr_FAM_SFF']], how='left', on =['Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                                'Nr_A3','Nr_A4','Nr_A5','Nr_A6'])
        df_ANLS_02 = df_ANLS_02.drop(columns='Cd_SISBASE')
        df_ANLS_02['Cd_SISBASE_SFF'] = df_ANLS_02['Cd_SISBASE_SFF'].fillna("ND")
        for n in [1,2,3,4,5,6]:
            df_ANLS_01[f"Nr_A{n}"] = (
                                        df_ANLS_01[f"Nr_A{n}"].astype(str).str.rjust(2, "0")
                                    )
        df_ANLS_01a = (df_ANLS_01[df_ANLS_01['Cd_SISBASE'] != "ND"].groupby(["Cd_TP_AVAL","Nr_TI","Nr_TUC",'Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6',
                                        "Cd_SISBASE","Cd_UAR","Cd_UND_AIS"],dropna=False)[["Qtd_AIS","VL_VOC_VFa","VL_VOCa",
                                        "VL_VNR_UC"]].sum().reset_index())
        df_ANLS_02 = df_ANLS_01a.merge(df_ANLS_02[df_ANLS_02['Cd_SISBASE_SFF'] != "ND"][[
                                'Nr_TI','Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_SISBASE_SFF','Cd_FOR_COGE_SFF',
                                'Nr_FAM_SFF','Cd_UND_AIS','Qtd_BAIXAS']], how='outer', on =['Nr_TI','Nr_TUC','Nr_A1',
                                'Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6'], suffixes =("_INCR", "_BAIXAS"), 
                                indicator=True)  
        df_ANLS_02.loc[df_ANLS_02['Cd_SISBASE'].isnull(), 'Cd_SISBASE'] = df_ANLS_02.loc[df_ANLS_02['Cd_SISBASE'].isnull(), 'Cd_SISBASE_SFF']
        df_ANLS_02a = df_ANLS_02[['Nr_TI','Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_SISBASE',
                            'Qtd_AIS','Cd_UND_AIS_INCR','Qtd_BAIXAS','Cd_UND_AIS_BAIXAS']].copy()
        
        df_ANLS_02a['Qtd_BAIXAS'] = df_ANLS_02a['Qtd_BAIXAS'].fillna(0)
        df_ANLS_02a['Qtd_AIS'] = df_ANLS_02a['Qtd_AIS'].fillna(0)
        df_ANLS_02a = df_ANLS_02a.groupby(['Nr_TI','Cd_SISBASE'], dropna=False)[['Qtd_AIS','Qtd_BAIXAS']].sum().reset_index()
    
        tbl_sisbase = pd.read_csv(rf"tabelas/tbl_nomes_sisbase.csv", sep="|", encoding="utf-8")
        df_ANLS_02a = df_ANLS_02a.merge(tbl_sisbase, how='left', on = 'Cd_SISBASE').rename(columns={'Qtd_AIS':'Qtd_INC'})
    
        st.html(
                    """
                        <p style="text-align: justify;text-indent: 40px">
                            A análise a seguir busca comparar os movimentos de <b>adição</b> e <b>baixa</b> dos ativos, com o objetivo 
                            de identificar possíveis padrões de substituição, renovação ou desmobilização dos investimentos realizados. 
                            Em condições ideais, essa comparação seria efetuada diretamente no nível dos materiais instalados. Contudo, 
                            o arquivo de baixas não possui a identificação do material (<b>COD_ITEM</b>), impossibilitando a associação 
                            direta entre os itens adicionados e posteriormente baixados.
                        </p>
    
                        <p style="text-align: justify;text-indent: 40px">
                            Diante dessa limitação, a análise foi conduzida utilizando o <b>Cd_SISBASE</b> como elemento comum entre as 
                            duas bases de dados. Dessa forma, as adições passam a ser avaliadas de forma agregada por sistema, deixando-se 
                            de lado a segregação por <b>COD_ITEM</b>. Essa abordagem é particularmente adequada porque uma mesma adição pode 
                            envolver a instalação conjunta de diversos materiais, enquanto as baixas são registradas apenas no nível do sistema.
                        </p>
    
                        <p style="text-align: justify;text-indent: 40px">
                            Assim, os resultados apresentados devem ser interpretados como uma comparação entre os volumes e valores de 
                            adições e baixas associados a cada <b>Cd_SISBASE</b>, permitindo avaliar a dinâmica de renovação dos ativos e 
                            identificar sistemas nos quais os investimentos recentes podem estar associados à substituição de componentes 
                            anteriormente instalados ou à expansão da base existente.
                        </p>
                    """,
                    width="stretch"
                )
        st.dataframe(df_ANLS_02a, width='stretch', hide_index=True)
        
        df_AISant = imp_tbl_forma_001("AISant", SQLq=None, con=bd, st=st, Empresa=empresa)
        df_AISat = imp_tbl_forma_001("AIS", SQLq=None, con=bd, st=st, Empresa=empresa)
        df_AISant['Qtd_AIS'] = pd.to_numeric(df_AISant['Qtd_AIS'].astype(str), errors='coerce')
        df_AISat['Qtd_AIS'] = pd.to_numeric(df_AISat['Qtd_AIS'].astype(str), errors='coerce')
    
        df_AISant_gr = (df_AISant
                        .groupby(by=['Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                    'Nr_A3','Nr_A4','Nr_A5','Nr_A6',
                                    'Cd_UND_AIS','Cd_UAR'], dropna=False)['Qtd_AIS']
                        .sum()
                        .reset_index()
                        .rename(columns={'Qtd_AIS':'Qtd_AIS_ANT'}))
        df_AISant_gr["Cd_UAR"] = (
                                    df_AISant_gr["Cd_UAR"]
                                    .astype(str)
                                    .replace({"000": "TUC", "UC" : "TUC"})
                                )
    
        df_AISant_gr.loc[
                            df_AISant_gr["Cd_UAR"] != "TUC",
                            "Cd_UAR"
                        ] = "UAR"
        df_AISat_gr = (df_AISat
                        .groupby(by=['Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                    'Nr_A3','Nr_A4','Nr_A5','Nr_A6',
                                    'Cd_UND_AIS','Cd_UAR'], dropna=False)['Qtd_AIS']
                        .sum()
                        .reset_index()
                        .rename(columns={'Qtd_AIS':'Qtd_AIS_AT'}))
        
        df_ANLS_03 = df_AISant_gr.merge(df_AISat_gr, how='outer', on = ['Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                    'Nr_A3','Nr_A4','Nr_A5','Nr_A6',
                                    'Cd_UND_AIS','Cd_UAR'], indicator=True)
        df_ANLS_03['Cd_SISBASE'] ="ND"
        LST_TUC = df_ANLS_03[(df_ANLS_03['Cd_UAR'] != 'UAR')][['Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                                'Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_SISBASE']].drop_duplicates()
    
        LST_TUC = clcpr.tst_cod_sisbase(LST_TUC, st.session_state.dt_fim, st=st)
        df_ANLS_03 = df_ANLS_03.merge(LST_TUC[['Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                                'Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_SISBASE_SFF','Cd_FOR_COGE_SFF',
                                                'Nr_FAM_SFF']], how='left', on =['Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                                'Nr_A3','Nr_A4','Nr_A5','Nr_A6'])
        df_ANLS_03 = df_ANLS_03.drop(columns='Cd_SISBASE')
        df_ANLS_03['Cd_SISBASE_SFF'] = df_ANLS_03['Cd_SISBASE_SFF'].fillna("ND")
    
        df_ANLS_03['Txt_AIS'] = np.where(
                                            df_ANLS_03["_merge"] == "both",
                                            "Presente em ambos os períodos",
                                            np.where(
                                                df_ANLS_03["_merge"] == "left_only",
                                                "Inexiste no AIS atual, 100% baixado",
                                                "Inexiste no AIS anterior, novo ativo"
                                            )
                                        )
        df_ANLS_03 = df_ANLS_03.drop(columns=['_merge','Cd_FOR_COGE_SFF','Nr_FAM_SFF']).rename(columns={'Cd_SISBASE_SFF':'Cd_SISBASE'})
        df_ANLS_03["Qtd_AIS_ANT"] = pd.to_numeric(df_ANLS_03["Qtd_AIS_ANT"], errors="coerce")
        df_ANLS_03["Qtd_AIS_AT"]  = pd.to_numeric(df_ANLS_03["Qtd_AIS_AT"], errors="coerce")
        
        df_ANLS_03 = (df_ANLS_03[(df_ANLS_03['Cd_UAR'] != 'UAR') & (df_ANLS_03['Cd_SISBASE'] != 'ND')]
                    .groupby(['Nr_TI','Cd_SISBASE'], dropna=False)[['Qtd_AIS_ANT','Qtd_AIS_AT']]
                    .sum()
                    .reset_index())
        df_ANLS_03 = df_ANLS_02a.merge(df_ANLS_03, how='outer', on=['Nr_TI','Cd_SISBASE'], indicator=True)
        
        denominador = df_ANLS_03["Qtd_AIS_ANT"].replace(0, np.nan)
    
        divergencia = (
                            (df_ANLS_03["Qtd_AIS_ANT"] - df_ANLS_03["Qtd_AIS_AT"]).abs()
                            / denominador
                        ).fillna(0)
    
        df_ANLS_03["Txt_AIS"] = np.where(
                                            df_ANLS_03["_merge"].eq("both"),
                                            "Executado movimentação no período incremental.",
                                            np.where(
                                                df_ANLS_03["Qtd_AIS_ANT"] > 0.01,
                                                np.where(
                                                    divergencia > 0.01,
                                                    "Arquivos AIS, atual e anterior, divergem, verificar.",
                                                    "Inexiste movimentação no período incremental."
                                                ),
                                                "Ativo não existente na posição anterior do AIS."
                                            )
                                        )
        
        
        df_ANLS_03 = df_ANLS_03.drop(columns=['_merge','Txt_desc_geral'])
        df_ANLS_03 = df_ANLS_03.merge(tbl_sisbase, how='left', on = 'Cd_SISBASE')
        df_ANLS_03['Qtd_INC'] = df_ANLS_03['Qtd_INC'].fillna(0)
        df_ANLS_03['Qtd_BAIXAS'] = df_ANLS_03['Qtd_BAIXAS'].fillna(0)
    
        cols_num = [
                        "Cd_SISBASE",
                        "Qtd_AIS_ANT",
                        "Qtd_AIS_AT",
                        "Qtd_INC",
                        "Qtd_BAIXAS",
                    ]
        df_base = df_ANLS_03[df_ANLS_03['Cd_SISBASE'] != "ND"][cols_num].copy()
        df_base["SALDO_ESPERADO"] = (
                                        df_base["Qtd_AIS_ANT"]
                                        + df_base["Qtd_INC"]
                                        - df_base["Qtd_BAIXAS"]
                                    )
        
        df_base["DIF_CONCILIACAO"] = (
                                        df_base["Qtd_AIS_AT"] - df_base["SALDO_ESPERADO"]
                                    )
        df_base["TAXA_EXPANSAO"] = np.where(
                                                df_base["Qtd_AIS_ANT"] != 0,
                                                df_base["Qtd_INC"] / df_base["Qtd_AIS_ANT"] * 100,
                                                np.nan
                                            )
        df_base["TAXA_RENOVACAO"] = np.where(
                                                df_base["Qtd_AIS_ANT"] != 0,
                                                df_base["Qtd_BAIXAS"] / df_base["Qtd_AIS_ANT"] * 100,
                                                np.nan
                                            )
    
        df_base["CRESCIMENTO_LIQ"] = np.where(
                                                df_base["Qtd_AIS_ANT"] != 0,
                                                (df_base["Qtd_INC"] - df_base["Qtd_BAIXAS"]) / df_base["Qtd_AIS_ANT"] * 100,
                                                np.nan
                                            )
    
        df_base["INDICE_SUBSTITUICAO"] = np.where(
                                                        df_base["Qtd_INC"] != 0,
                                                        df_base["Qtd_BAIXAS"] / df_base["Qtd_INC"] * 100,
                                                        np.nan
                                                    )
        df_base["DINAMICA_BASE"] = np.select(
                                                [
                                                    (df_base["CRESCIMENTO_LIQ"] > 10) & (df_base["INDICE_SUBSTITUICAO"] < 50),
                                                    (df_base["CRESCIMENTO_LIQ"] > 10) & (df_base["INDICE_SUBSTITUICAO"] >= 50),
                                                    (df_base["CRESCIMENTO_LIQ"].between(-10, 10)) & (df_base["INDICE_SUBSTITUICAO"] >= 50),
                                                    (df_base["CRESCIMENTO_LIQ"] < -10),
                                                ],
                                                [
                                                    "Expansão",
                                                    "Expansão com renovação",
                                                    "Renovação",
                                                    "Contração",
                                                ],
                                                default="Estabilidade"
                                            )
        st.html(
                    """
                        <p style="text-align: justify;text-indent: 40px">
                            Em complemento, a seguir se avalia a dinâmica da base instalada a partir da posição inicial, das adições, das baixas
                            e da posição final dos ativos. O objetivo é identificar se os movimentos observados representam expansão,
                            renovação, substituição ou contração da base, considerando o <b>Cd_SISBASE</b> como unidade comum de comparação
                            entre os arquivos de adições e baixas.
                        </p>
                        <p style="text-align: justify;text-indent: 40px">
                            No gráfico, o eixo horizontal representa a taxa de renovação, medida pelas baixas em relação à base inicial,
                            enquanto o eixo vertical apresenta o crescimento líquido, calculado pela diferença entre adições e baixas
                            sobre a base inicial. Pontos acima de zero indicam expansão da base, enquanto pontos abaixo de zero indicam
                            redução líquida. O tamanho dos pontos representa a posição final da base instalada.
                        </p>
                    """,
                    width="stretch"
                )
        df_base["Qtd_AIS_AT"] = pd.to_numeric(
                                                df_base["Qtd_AIS_AT"],
                                                errors="coerce"
                                            ).fillna(0)
    
        df_base["Qtd_AIS_AT_SIZE"] = df_base["Qtd_AIS_AT"].clip(lower=0)
        df_base["TAXA_RENOVACAO"] = df_base["TAXA_RENOVACAO"].replace([np.inf, -np.inf], np.nan).fillna(0)
        df_base["CRESCIMENTO_LIQ"] = df_base["CRESCIMENTO_LIQ"].replace([np.inf, -np.inf], np.nan).fillna(0)
        df_base["x"] = df_base["Qtd_BAIXAS"]
        df_base["y"] = df_base["Qtd_INC"] - df_base["Qtd_BAIXAS"]
        fig = px.scatter(
                            df_base,
                            x="x",
                            y="y",
                            size="Qtd_AIS_AT_SIZE",
                            color="DINAMICA_BASE",
                            hover_data=[
                                "Cd_SISBASE",
                                "Qtd_AIS_ANT",
                                "Qtd_INC",
                                "Qtd_BAIXAS",
                                "Qtd_AIS_AT",
                                "INDICE_SUBSTITUICAO",
                                "DIF_CONCILIACAO",
                            ],
                            title="Dinâmica da Base Instalada por Cd_SISBASE",
                            labels={
                                "x": "Baixas",
                                "y": "Variação líquida dos ativos (INCR - BAIXAS)",
                                "Qtd_AIS_AT": "Base final",
                                "DINAMICA_BASE": "Dinâmica",
                            },
                        )
    
        fig.add_hline(y=0, line_dash="dash", line_color="#999999")
        fig.add_vline(x=0, line_dash="dash", line_color="#999999")
    
        fig.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            height=650,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1,
                            ),
                        )
    
        st.plotly_chart(fig, width="stretch")
    
        df_resumo = df_base[
                            [
                                "Cd_SISBASE",
                                "Qtd_AIS_ANT",
                                "Qtd_INC",
                                "Qtd_BAIXAS",
                                "Qtd_AIS_AT",
                                "CRESCIMENTO_LIQ",
                                "TAXA_EXPANSAO",
                                "TAXA_RENOVACAO",
                                "INDICE_SUBSTITUICAO",
                                "DIF_CONCILIACAO",
                                "DINAMICA_BASE",
                            ]
                        ].sort_values("CRESCIMENTO_LIQ", ascending=False)
    
        st.dataframe(df_resumo, width="stretch", hide_index=True)
    
        df_bar = df_base.copy()
        df_bar["Cd_SISBASE"] = df_bar["Cd_SISBASE"].astype(str)
        df_bar["Qtd_AIS_ANT"] = df_bar["Qtd_AIS_ANT"].fillna(0)
        df_bar["Qtd_AIS_AT"] = df_bar["Qtd_AIS_AT"].fillna(0)
        df_bar["BASE_APOS_ADICOES"] = df_bar["Qtd_AIS_ANT"] + df_bar["Qtd_INC"]
        df_bar["BASE_APOS_BAIXAS"] = (
                                            df_bar["BASE_APOS_ADICOES"] - df_bar["Qtd_BAIXAS"]
                                        ).clip(lower=0)
        df_bar["DIF_CONCILIACAO"] = df_bar["Qtd_AIS_AT"] - df_bar["BASE_APOS_BAIXAS"]
        df_bar["DIF_CONCILIACAO_ABS"] = df_bar["DIF_CONCILIACAO"].abs()
        df_bar["DIF_CONCILIACAO_PERC"] = np.where(
                                                    df_bar["Qtd_AIS_AT"] != 0,
                                                    df_bar["DIF_CONCILIACAO"] / df_bar["Qtd_AIS_AT"] * 100,
                                                    np.nan
                                                )
        df_bar["MOV_TOTAL"] = (
                                    df_bar["Qtd_INC"].abs()
                                    + df_bar["Qtd_BAIXAS"].abs()
                                )
        df_bar["RELEVANCIA"] = (
                                    df_bar["MOV_TOTAL"]
                                    + df_bar["DIF_CONCILIACAO_ABS"]
                                )
        df_bar["DINAMICA"] = np.select(
                                            [
                                                df_bar["Qtd_INC"] > df_bar["Qtd_BAIXAS"],
                                                df_bar["Qtd_INC"] < df_bar["Qtd_BAIXAS"],
                                                df_bar["Qtd_INC"] == df_bar["Qtd_BAIXAS"],
                                            ],
                                            [
                                                "Expansão líquida",
                                                "Redução líquida",
                                                "Renovação / estabilidade",
                                            ],
                                            default="Sem movimento",
                                        )
    
        df_bar["ALERTA_CONCILIACAO"] = np.where(
                                                    df_bar["DIF_CONCILIACAO_ABS"] > 0,
                                                    "Com diferença",
                                                    "Conciliado",
                                                )
    
        df_bar["ESCALA"] = np.select(
                                        [
                                            df_bar["Qtd_AIS_AT"] >= 1_000_000,
                                            df_bar["Qtd_AIS_AT"].between(100_000, 1_000_000, inclusive="left"),
                                            df_bar["Qtd_AIS_AT"].between(10_000, 100_000, inclusive="left"),
                                        ],
                                        [
                                            "Acima de 1 milhão",
                                            "Entre 100 mil e 1 milhão",
                                            "Entre 10 mil e 100 mil",
                                        ],
                                        default="Abaixo de 10 mil",
                                    )
        df_bar = df_bar.sort_values("BASE_APOS_BAIXAS", ascending=True)
        df_long = []
        for _, row in df_bar.iterrows():
            sis = row["Cd_SISBASE"]
            df_long.extend([
                            {
                                "Cd_SISBASE": sis,
                                "ESCALA": row["ESCALA"],
                                "Etapa": "1. AIS inicial",
                                "BASE_TRANSPARENTE": 0,
                                "VALOR_TOTAL": row["Qtd_AIS_ANT"],
                                "VALOR_COLORIDO": row["Qtd_AIS_ANT"],
                                "COR": "#2b5c8f",
                                "TEXTO": f'{row["Qtd_AIS_ANT"]:,.2f}'.replace(",","x").replace(".",",").replace("x","."),
                                "DIF_CONCILIACAO": row["DIF_CONCILIACAO"],
                                "DIF_CONCILIACAO_PERC": row["DIF_CONCILIACAO_PERC"],
                                "DINAMICA": row["DINAMICA"],
                                "ALERTA_CONCILIACAO": row["ALERTA_CONCILIACAO"],
                                "RELEVANCIA": row["RELEVANCIA"],
                            },
                            {
                                "Cd_SISBASE": sis,
                                "ESCALA": row["ESCALA"],
                                "Etapa": "2. Adições",
                                "BASE_TRANSPARENTE": row["Qtd_AIS_ANT"],
                                "VALOR_TOTAL": row["BASE_APOS_ADICOES"],
                                "VALOR_COLORIDO": row["Qtd_INC"],
                                "COR": "#4c78a8",
                                "TEXTO": f'+{row["Qtd_INC"]:,.2f}'.replace(",","x").replace(".",",").replace("x","."),
                                "DIF_CONCILIACAO": row["DIF_CONCILIACAO"],
                                "DIF_CONCILIACAO_PERC": row["DIF_CONCILIACAO_PERC"],
                                "DINAMICA": row["DINAMICA"],
                                "ALERTA_CONCILIACAO": row["ALERTA_CONCILIACAO"],
                                "RELEVANCIA": row["RELEVANCIA"],
                            },
                            {
                                "Cd_SISBASE": sis,
                                "ESCALA": row["ESCALA"],
                                "Etapa": "3. Baixas",
                                "BASE_TRANSPARENTE": row["BASE_APOS_BAIXAS"],
                                "VALOR_TOTAL": row["BASE_APOS_ADICOES"],
                                "VALOR_COLORIDO": row["Qtd_BAIXAS"],
                                "COR": "#e06d53",
                                "TEXTO": f'-{row["Qtd_BAIXAS"]:,.2f}'.replace(",","x").replace(".",",").replace("x","."),
                                "DIF_CONCILIACAO": row["DIF_CONCILIACAO"],
                                "DIF_CONCILIACAO_PERC": row["DIF_CONCILIACAO_PERC"],
                                "DINAMICA": row["DINAMICA"],
                                "ALERTA_CONCILIACAO": row["ALERTA_CONCILIACAO"],
                                "RELEVANCIA": row["RELEVANCIA"],
                            },
                            {
                                "Cd_SISBASE": sis,
                                "ESCALA": row["ESCALA"],
                                "Etapa": "4. AIS final informado",
                                "BASE_TRANSPARENTE": 0,
                                "VALOR_TOTAL": row["Qtd_AIS_AT"],
                                "VALOR_COLORIDO": row["Qtd_AIS_AT"],
                                "COR": "#2b8a3e",
                                "TEXTO": f'{row["Qtd_AIS_AT"]:,.2f}'.replace(",","x").replace(".",",").replace("x","."),
                                "DIF_CONCILIACAO": row["DIF_CONCILIACAO"],
                                "DIF_CONCILIACAO_PERC": row["DIF_CONCILIACAO_PERC"],
                                "DINAMICA": row["DINAMICA"],
                                "ALERTA_CONCILIACAO": row["ALERTA_CONCILIACAO"],
                                "RELEVANCIA": row["RELEVANCIA"],
                            },
                            {
                                "Cd_SISBASE": sis,
                                "ESCALA": row["ESCALA"],
                                "Etapa": "5. Dif. conciliação",
                                "BASE_TRANSPARENTE": 0,
                                "VALOR_COLORIDO": row["DIF_CONCILIACAO_ABS"],
                                "VALOR_TOTAL": row["DIF_CONCILIACAO"],
                                "COR": "#7b2cbf" if row["DIF_CONCILIACAO_ABS"] > 0 else "#d0d5dd",
                                "TEXTO": f'{row["DIF_CONCILIACAO"]:+,.0f}'.replace(",","x").replace(".",",").replace("x","."),
                                "DIF_CONCILIACAO": row["DIF_CONCILIACAO"],
                                "DIF_CONCILIACAO_PERC": row["DIF_CONCILIACAO_PERC"],
                                "DINAMICA": row["DINAMICA"],
                                "ALERTA_CONCILIACAO": row["ALERTA_CONCILIACAO"],
                                "RELEVANCIA": row["RELEVANCIA"],
                            },
                        ])
    
        df_long = pd.DataFrame(df_long)
        df_long["EIXO_Y"] = (
                                df_long["Cd_SISBASE"]
                                + " | "
                                + df_long["Etapa"]
                            )
        
        ordem_escalas = [
                            "Acima de 1 milhão",
                            "Entre 100 mil e 1 milhão",
                            "Entre 10 mil e 100 mil",
                            "Abaixo de 10 mil",
                        ]
        
        fig = make_subplots(
                                rows=4,
                                cols=1,
                                shared_xaxes=False,
                                vertical_spacing=0.025,
                                subplot_titles=ordem_escalas,
                            )
        
        for i, escala in enumerate(ordem_escalas, start=1):
            df_sub = df_long[df_long["ESCALA"] == escala].copy()
            if df_sub.empty:
                continue
            ordem_sis = (
                            df_bar[df_bar["ESCALA"] == escala]
                            .sort_values(["DIF_CONCILIACAO_ABS", "MOV_TOTAL"], ascending=[True, True])
                            ["Cd_SISBASE"]
                            .tolist()
                        )
            ordem_y = []
            for sis in ordem_sis:
                ordem_y.extend([
                                    f"{sis} | 1. AIS inicial",
                                    f"{sis} | 2. Adições",
                                    f"{sis} | 3. Baixas",
                                    f"{sis} | 4. AIS final informado",
                                    f"{sis} | 5. Dif. conciliação",
                                ])
            ordem_y = list(dict.fromkeys(ordem_y))
            df_sub["EIXO_Y"] = pd.Categorical(
                                                df_sub["EIXO_Y"],
                                                categories=ordem_y,
                                                ordered=True,
                                            )
            df_sub = df_sub.sort_values("EIXO_Y", ascending=False)
    
            fig.add_trace(
                            go.Bar(
                                x=df_sub["BASE_TRANSPARENTE"],
                                y=df_sub["EIXO_Y"],
                                orientation="h",
                                marker_color="rgba(0,0,0,0)",
                                hoverinfo="skip",
                                showlegend=False,
                            ),
                            row=i,
                            col=1,
                        )
            fig.add_trace(
                            go.Bar(
                                x=df_sub["VALOR_COLORIDO"],
                                y=df_sub["EIXO_Y"],
                                orientation="h",
                                marker_color=df_sub["COR"],
                                text=df_sub["TEXTO"],
                                textposition="outside",
                                customdata=np.stack([
                                    df_sub["Cd_SISBASE"],
                                    df_sub["Etapa"],
                                    df_sub["VALOR_TOTAL"],
                                    df_sub["DIF_CONCILIACAO"],
                                    df_sub["DIF_CONCILIACAO_PERC"],
                                    df_sub["DINAMICA"],
                                    df_sub["ALERTA_CONCILIACAO"],
                                ], axis=-1),
                                hovertemplate=
                                    "<b>Cd_SISBASE:</b> %{customdata[0]}<br>"
                                    "<b>Etapa:</b> %{customdata[1]}<br>"
                                    "<b>Parcela destacada:</b> %{x:,.0f}<br>"
                                    "<b>Valor total / saldo:</b> %{customdata[2]:,.0f}<br><br>"
                                    "<b>Dif. conciliação:</b> %{customdata[3]:+,.0f}<br>"
                                    "<b>Dif. conciliação %:</b> %{customdata[4]:+,.2f}%<br>"
                                    "<b>Dinâmica:</b> %{customdata[5]}<br>"
                                    "<b>Status:</b> %{customdata[6]}"
                                    "<extra></extra>",
                                showlegend=False,
                            ),
                            row=i,
                            col=1,
                        )
    
            fig.update_yaxes(
                                title_text="",
                                automargin=True,
                                row=i,
                                col=1,
                            )
    
            fig.update_xaxes(
                                title_text="Quantidade",
                                showgrid=True,
                                gridcolor="#eeeeee",
                                zeroline=True,
                                zerolinecolor="#999999",
                                row=i,
                                col=1,
                            )
        fig.update_layout(
                            title={
                                "text": "Dinâmica da Base Instalada, quantidade, por Cd_SISBASE — por faixa de escala",
                                "x": 0.5,
                                "xanchor": "center",
                            },
                            barmode="stack",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=250, r=90, t=120, b=80),
                            height=max(700, 5 * len(df_long)),
                        )
        st.html(
                    """
                        <p style="text-align: justify;text-indent: 40px">
                            O gráfico a seguir apresenta a dinâmica da base instalada por <b>Cd_SISBASE</b>, comparando a posição
                            inicial dos ativos, as adições realizadas ao longo do período, as baixas registradas e a posição final
                            observada. Como o arquivo de baixas não possui identificação dos materiais individuais
                            (<b>COD_ITEM</b>), a análise foi conduzida em nível de sistema, utilizando o <b>Cd_SISBASE</b> como
                            elemento comum entre as bases de adições e baixas.
                        </p>
    
                        <p style="text-align: justify;text-indent: 40px">
                            Para cada sistema são apresentadas cinco etapas: posição inicial, adições, baixas, posição final 
                            informada e diferença de conciliação.
                        </p>
    
                        <p style="text-align: justify;text-indent: 40px">
                            Essa visualização permite identificar sistemas em processo de expansão, renovação ou
                            redução da base instalada. Sistemas com adições significativamente superiores às baixas
                            tendem a indicar crescimento da infraestrutura. Já sistemas com elevados volumes de
                            baixas acompanhados de adições sugerem processos de substituição ou renovação de ativos.
                            Diferenças relevantes entre a posição final calculada e a posição final informada podem,
                            ainda, indicar a existência de reclassificações, ajustes cadastrais ou movimentos não
                            capturados diretamente pelas bases analisadas.
                        </p>
                    """,
                    width="stretch"
                )
        st.plotly_chart(fig, width="stretch")
        st.html(
                    """
                    <div style="
                        font-family:'Source Sans Pro', -apple-system, BlinkMacSystemFont, sans-serif;
                        display:flex;
                        flex-wrap:wrap;
                        gap:18px;
                        align-items:center;
                        margin-top:-10px;
                        margin-bottom:20px;
                        font-size:0.88rem;
                        color:#555;
                    ">
                        <span><b style="color:#2b5c8f;">■</b> AIS inicial</span>
                        <span><b style="color:#4c78a8;">■</b> Adições</span>
                        <span><b style="color:#e06d53;">■</b> Baixas</span>
                        <span><b style="color:#2b8a3e;">■</b> AIS final informado</span>
                        <span><b style="color:#7b2cbf;">■</b> Diferença de conciliação</span>
                        <span><b style="color:#d0d5dd;">■</b> Sem diferença</span>
                    </div>
                    """,
                    width="stretch"
                )
        
        st.html(
                    """
                        <p style="text-align: justify;text-indent: 40px">
                            A tabela abaixo apresenta, em formato tabular, as mesmas etapas utilizadas na visualização gráfica da 
                            dinâmica da base instalada por <b>Cd_SISBASE</b>. Para cada sistema, são detalhadas a posição inicial, 
                            as adições, as baixas, a posição final informada e a diferença de conciliação entre o saldo esperado 
                            e o saldo efetivamente registrado.
                        </p>
    
                        <p style="text-align: justify;text-indent: 40px">
                            Essa visão permite consultar os valores de forma analítica, facilitando a identificação de sistemas com 
                            maior movimentação, diferenças de conciliação, expansão líquida, redução da base ou renovação/estabilidade. 
                            A tabela complementa o gráfico ao permitir ordenações, filtros e inspeções pontuais dos registros.
                        </p>
                    """,
                    width="stretch"
                )
        df_long_tab = df_bar[
                                [
                                    "Cd_SISBASE",
                                    "ESCALA",
                                    "Qtd_AIS_ANT",
                                    "Qtd_INC",
                                    "Qtd_BAIXAS",
                                    "BASE_APOS_BAIXAS",
                                    "Qtd_AIS_AT",
                                    "DIF_CONCILIACAO",
                                    "DIF_CONCILIACAO_PERC",
                                    "DINAMICA",
                                    "ALERTA_CONCILIACAO",
                                ]
                            ].copy()
    
        df_long_tab = df_long_tab.rename(
                                        columns={
                                            "ESCALA": "Faixa de escala",
                                            "Qtd_AIS_ANT": "AIS inicial",
                                            "Qtd_INC": "Adições",
                                            "Qtd_BAIXAS": "Baixas",
                                            "BASE_APOS_BAIXAS": "Saldo esperado",
                                            "Qtd_AIS_AT": "AIS final informado",
                                            "DIF_CONCILIACAO": "Dif. conciliação",
                                            "DIF_CONCILIACAO_PERC": "Dif. conciliação (%)",
                                            "DINAMICA": "Dinâmica",
                                            "ALERTA_CONCILIACAO": "Status conciliação",
                                        }
                                    )
        
        df_long_tab = df_long_tab.sort_values(
                                                ["Dif. conciliação (%)", "Faixa de escala", "Cd_SISBASE"], ascending=False
                                            )
        df_long_tab.to_csv(rf"{local}/RELATORIOS/mutacao_AIS.csv", index=False, encoding='utf-8', sep = "|")
        st.dataframe(df_long_tab[df_long_tab['Dif. conciliação (%)'].abs() >= 1], width="stretch", hide_index=True)
```

</details>

---

<a id="funcao-5"></a>

## visualizador_BPR

Visualiza dados utilizando uma interface Streamlit.

A função visualizador_BPR é responsável por configurar e inicializar um ambiente de visualização de dados, carregando informações necessárias e executando várias visualizações específicas. Ela utiliza o Streamlit para criar a interface do usuário e interage com bancos de dados e arquivos.

### Assinatura

```python
def visualizador_BPR(st = None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `st` | `objeto` | Objeto Streamlit usado para criar a interface da aplicação. |

### Dependências

- `{'nome': 'MANIFESTO.inicializa_database', 'tipo': 'função'}`
- `{'nome': 'MANIFESTO.inicializa_detalhes', 'tipo': 'função'}`
- `{'nome': 'MANIFESTO.inicializar_rastreamento', 'tipo': 'função'}`
- `{'nome': 'UTILS.bsc_dados_reg', 'tipo': 'função'}`
- `{'nome': 'UTILS.executar_vis', 'tipo': 'função'}`
- `{'nome': 'pathlib.Path', 'tipo': 'classe'}`
- `{'nome': 'streamlit', 'tipo': 'biblioteca'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def visualizador_BPR(st = None):
    if not'tra_dir' in st.session_state:
        st.html("""
                    <p style="text-align: justify;text-indent: 40px">
                    Você deve configurar o diretório de trabalho, empresa e período
                    na aba <i>Criar Pasta de Trabalho</i>, barra lateral.</p>
                """)
        return

    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
    dds = bsc_dados_reg('TBL_EMPRESAS')
    lst_emp = dds['Nm_EMPRESA'].drop_duplicates().to_list()
    st.html(f"<style>{css}</style>")
    raiz = Path(local)
    caminho_manifesto = raiz / "MANIFESTO" / "TRILHA_EXEC" / "execucoes.db"
    caminho_manifesto.parent.mkdir(parents=True, exist_ok=True)
    inicializa_database(str(caminho_manifesto))
    inicializa_detalhes(str(caminho_manifesto))
    inicializar_rastreamento(str(caminho_manifesto))
    database = str(caminho_manifesto)
    bd_path = f'{local}/BD_LOCAL/{empresa}_{ano}.db'
    bd_BDGDAT_path = f'{local}/BD_LOCAL/BDGD_AT_{empresa}_{ano}.db'
    bd_BDGDANT_path = f'{local}/BD_LOCAL/BDGD_ANT_{empresa}_{ano}.db'
    bd_EFD_path = f'{local}\BD_LOCAL\EFD_ICMS_{empresa}_{ano}.db'
    df_INCR, dir_FIG, df_ROA, df_ANLS_01, df_BPUAR, df_BAIXAS = executar_vis(_vis_001, bd_path, st, empresa, bd_EFD_path, local)
    executar_vis(_vis_002, bd_path, st, empresa, bd_EFD_path, local, df_INCR, dir_FIG, df_ROA)
    executar_vis(_vis_003, bd_path, st, empresa, bd_EFD_path, local, df_INCR, dir_FIG, df_ROA, df_ANLS_01, df_BPUAR)
    executar_vis(_vis_004, bd_path, st, empresa, bd_EFD_path, local, df_INCR, dir_FIG, df_ROA, df_ANLS_01, df_BPUAR, df_BAIXAS)
```

</details>

---
