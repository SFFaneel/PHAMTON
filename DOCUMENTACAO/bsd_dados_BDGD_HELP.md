# Referência de Funções

## Índice

- [criar_RCP_BDGD](#funcao-1)
- [sel_eq](#funcao-2)
- [formatar_grupo](#funcao-3)
- [cte_modelo](#funcao-4)
- [tabela](#funcao-5)
- [subquery_uniao](#funcao-6)
- [cte_simples](#funcao-7)
- [sql_na](#funcao-8)
- [cte_bay](#funcao-9)
- [cte_bar](#funcao-10)
- [cte_eqtrm](#funcao-11)
- [cte_eqtrmtmt](#funcao-12)
- [cte_eqtrat](#funcao-13)
- [cte_unificado](#funcao-14)
- [sql_final](#funcao-15)
- [unidades_existentes](#funcao-16)
- [uniao_unidades](#funcao-17)

---

<a id="funcao-1"></a>

## criar_RCP_BDGD

Sem resumo disponível.

### Assinatura

```python
def criar_RCP_BDGD(suf="_AT", st=None, x1=False):
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def criar_RCP_BDGD(suf="_AT", st=None, x1=False):
    if not st:
        st.warning("Falhou")
        return pd.DataFrame()

    if 'tra_dir' in st.session_state:
        local = st.session_state.tra_dir
        empresa = st.session_state.nm_empr
        ano = st.session_state.dt_fim.year

        with sl.connect(rf'{local}\BD_LOCAL\BDGD{suf}_{empresa}_{ano}.db') as bd:
            if suf=="_AT":
                st.html(f"""<h1>Busca dos dados da BDGD atual</h1><br>
                        <p  style="text-align: justify;text-indent: 40px">
                        Vamos buscar os dados da BDGD atual, fazendo um RCP físico.   
                        </p>
                        <hr/>        
                    """)
            else:
                st.html(f"""<h1>Busca dos dados da BDGD anterior</h1><br>
                        <p  style="text-align: justify;text-indent: 40px">
                        Vamos buscar os dados da BDGD anterior, fazendo um RCP físico.   
                        </p>
                        <hr/>          
                    """)
            LST_TBL = [f'UNCRBT{suf}', f'UNCRMT{suf}', f'UNCRAT{suf}',
                    f'UNREBT{suf}', f'UNREMT{suf}', f'UNREAT{suf}',
                    f'UNSEBT{suf}', f'UNSEMT{suf}', f'UNSEAT{suf}',
                    f'UCAT{suf}', f'UCMT{suf}', f'UCBT{suf}',
                    f'UGAT{suf}', f'UGMT{suf}', f'UGBT{suf}',
                    f'SSDAT{suf}', f'SSDMT{suf}', f'SSDBT{suf}',
                    f'RAMLIG{suf}']
            tabelas_existentes = [t for t in LST_TBL if tabela_existe(bd, t)]

            cols_texto = st.columns([1,8,1], gap='small')
            
            with cols_texto[1]:
                if x1 or (not existe_tabela("UC_UNIFIC", bd)):

                    COLS = """
                                COD_ID    TEXT,
                                PN_CON    TEXT,
                                RAMAL     TEXT,
                                PAC       TEXT,
                                CTAT      TEXT,
                                CTMT      TEXT,
                                UNI_TR_AT TEXT,
                                UNI_TR_MT TEXT,
                                SUB       TEXT,
                                CONJ      TEXT,
                                MUN       TEXT,
                                SIT_ATIV  TEXT,
                                DAT_CON   TEXT,
                                CAR_INST  REAL,
                                DEM_CONT  REAL,
                                TIP_SIST  TEXT,
                                POT_INST  REAL,
                                CNAE TEXT,
                                GRU_TEN TEXT
                            """
                    if x1 or (not existe_tabela("UC_UNIFIC", bd)):
                        with st.spinner("Fazendo a agregação de UC e UG..."):
                            rel = carregar_uc_unificada(
                                                        bd=bd,
                                                        suf=suf,
                                                        tabelas_existentes=tabelas_existentes,
                                                        dst_table="UC_UNIFIC",
                                                        criar_indices=True,
                                                        pragmas_carga=True,
                                                        COLS=COLS
                                                    )
                        for nm, valor in rel.items():
                            st.write(f"{nm} possui {valor} itens.")

                    st.html(f"""<br><p  style="text-align: justify;text-indent: 40px">
                        A consulta, a seguir, tem como objetivo identificar, para cada subestação (SE), as quantidades físicas de 
                        equipamentos modeladas na base da BDGD, agrupando por tipo, localização e características técnicas. 
                        Os dados são extraídos de diversas entidades representativas dos equipamentos instalados ou associados às 
                        SE, com destaque para aqueles ligados diretamente à subestação (ex.: BAY, BARRAMENTO) e aqueles vinculados 
                        por meio de entidades geográficas (ex.: transformadores, seccionadores, compensadores). A coluna Qtd_BDGD 
                        representa a quantidade consolidada por combinação de atributos técnicos, sendo que os itens cujo campo 
                        CONJ (modelado indiretamente pela junção dos campos TI, TUC, A1 a A6) possuem valor distinto de 'NA' 
                        são tratados como alocações diretas — ou seja, com correspondência física com o conjunto. Já nos casos 
                        em que CONJ equivale a 'NA', os equipamentos são considerados como parte de uma agregação coletiva e, 
                        portanto, serão rateados por critério, oportunamente explicitado. Essa distinção permite analisar com o melhor
                        grau de granularidade a modelagem patrimonial por subestação.   
                        </p>
                        <hr/>        
                    """)
                
                    ESQUEMA_EQ = [
                                    "TipoEquipamento",
                                    "Subestacao",
                                    "CodigoEquipamento",
                                    "DescricaoEquipamento",
                                    "ODI",
                                    "TI",
                                    "TUC",
                                    "A1",
                                    "A2",
                                    "A3",
                                    "A4",
                                    "A5",
                                    "A6",
                                    "UAR",
                                    "IDUC",
                                    "SITCONT",
                                    "DAT_IMO",
                                    "CONJ",
                                    "Qtd_BDGD",
                                ]

                    COLUNAS_T1 = [
                                    "T1.COD_ID",
                                    "T1.DESCR",
                                    "T1.ODI",
                                    "T1.TI",
                                    "T1.TUC",
                                    "T1.A1",
                                    "T1.A2",
                                    "T1.A3",
                                    "T1.A4",
                                    "T1.A5",
                                    "T1.A6",
                                    "T1.UAR",
                                    "T1.IDUC",
                                    "T1.SITCONT",
                                    "T1.DAT_IMO"
                                ]
                    def sel_eq(
                                    tipo,
                                    sub,
                                    cod,
                                    descr,
                                    odi,
                                    ti,
                                    tuc,
                                    a1,
                                    a2,
                                    a3,
                                    a4,
                                    a5,
                                    a6,
                                    uar,
                                    iduc,
                                    sitcont,
                                    dat_imo,
                                    conj,
                                    qtd="COUNT(*)",
                                ):
                        return f"""
                                    SELECT
                                        '{tipo}'  AS TipoEquipamento,
                                        {sub}     AS Subestacao,
                                        {cod}     AS CodigoEquipamento,
                                        {descr}   AS DescricaoEquipamento,
                                        {odi}     AS ODI,
                                        {ti}      AS TI,
                                        {tuc}     AS TUC,
                                        {a1}      AS A1,
                                        {a2}      AS A2,
                                        {a3}      AS A3,
                                        {a4}      AS A4,
                                        {a5}      AS A5,
                                        {a6}      AS A6,
                                        {uar}     AS UAR,
                                        {iduc}    AS IDUC,
                                        {sitcont} AS SITCONT,
                                        {dat_imo} AS DAT_IMO,
                                        {conj}    AS CONJ,
                                        {qtd}     AS Qtd_BDGD
                                """
                    
                    def formatar_grupo(cols):
                        return ",\n            ".join(cols)

                    def cte_modelo(nome, select_sql, from_sql, where_sql, grupo_colunas):
                        grupo_sql = formatar_grupo(grupo_colunas)
                        return f"""
                                    {nome} AS (
                                        {select_sql}
                                        {from_sql}
                                        {where_sql}
                                        GROUP BY
                                            {grupo_sql}
                                    )
                                    """.strip()
                    def tabela(nome_base, suf):
                        return f"{nome_base}{suf}"
                    
                    def subquery_uniao(tabelas_un):
                        return "\n            UNION ALL\n            ".join(
                            f"SELECT COD_ID, SUB, CONJ, GRU_TEN FROM {t}"
                            for t in tabelas_un
                        )
                    
                    def cte_simples(
                                            nome,
                                            tipo,
                                            tabela_base,
                                            suf,
                                            join_sql,
                                            where_sql,
                                            conj_expr,
                                        ):
                        select_sql = sel_eq(
                                            tipo=tipo,
                                            sub="S.COD_ID",
                                            cod="COALESCE(NULLIF(T1.UC_UG,''), S.COD_ID)",
                                            descr="T1.DESCR",
                                            odi="T1.ODI",
                                            ti="T1.TI",
                                            tuc="T1.TUC",
                                            a1="T1.A1",
                                            a2="T1.A2",
                                            a3="T1.A3",
                                            a4="T1.A4",
                                            a5="T1.A5",
                                            a6="T1.A6",
                                            uar="T1.UAR",
                                            iduc="T1.IDUC",
                                            sitcont="T1.SITCONT",
                                            dat_imo="T1.DAT_IMO",
                                            conj=conj_expr,
                                        )

                        from_sql = f"""
                                        FROM {tabela(tabela_base, suf)} T1
                                        {join_sql}
                                    """

                        grupo_cols = ["S.COD_ID", "UCG.COD_ID", *COLUNAS_T1, conj_expr]

                        return cte_modelo(
                                            nome=nome,
                                            select_sql=select_sql,
                                            from_sql=from_sql,
                                            where_sql=where_sql,
                                            grupo_colunas=grupo_cols,
                                        )
                    def sql_na():
                            return "'NA'"
                    
                    def cte_bay(suf):
                        bar_odi_por_sub = f"""
                                            SELECT
                                                SUB,
                                                ODI
                                            FROM {tabela("BAR", suf)}
                                        """
                        
                        select_sql = sel_eq(
                                                tipo="BAY",
                                                sub="S.COD_ID",
                                                cod="T1.COD_ID",
                                                descr="T1.DESCR",
                                                odi="R.ODI",
                                                ti=sql_na(),
                                                tuc=sql_na(),
                                                a1=sql_na(),
                                                a2=sql_na(),
                                                a3=sql_na(),
                                                a4=sql_na(),
                                                a5=sql_na(),
                                                a6=sql_na(),
                                                uar=sql_na(),
                                                iduc=sql_na(),
                                                sitcont=sql_na(),
                                                dat_imo=sql_na(),
                                                conj=sql_na(),
                                            )

                        from_sql = f"""
                                        FROM {tabela("BAY", suf)} T1
                                        LEFT JOIN {tabela("SUB", suf)} S
                                            ON T1.SUB = S.COD_ID
                                        LEFT JOIN (
                                            {bar_odi_por_sub}
                                        ) R
                                            ON R.SUB = T1.SUB
                                    """

                        where_sql = """
                                        WHERE T1.POS = 'PD'
                                    """

                        grupo_cols = [
                                            "S.COD_ID",
                                            "T1.COD_ID",
                                            "T1.DESCR",
                                            "R.ODI",
                                        ]

                        return cte_modelo(
                                            nome="BAY_SUB",
                                            select_sql=select_sql,
                                            from_sql=from_sql,
                                            where_sql=where_sql,
                                            grupo_colunas=grupo_cols,
                                        )


                    def cte_bar(suf):
                        select_sql = sel_eq(
                                                tipo="BARRAMENTO",
                                                sub="S.COD_ID",
                                                cod="T1.COD_ID",
                                                descr="T1.DESCR",
                                                odi="T1.ODI",
                                                ti="T1.TI",
                                                tuc="T1.TUC",
                                                a1="T1.A1",
                                                a2="T1.A2",
                                                a3="T1.A3",
                                                a4="T1.A4",
                                                a5="T1.A5",
                                                a6="T1.A6",
                                                uar="T1.UAR",
                                                iduc="T1.IDUC",
                                                sitcont="T1.SITCONT",
                                                dat_imo="T1.DAT_IMO",
                                                conj=sql_na(),
                                            )

                        from_sql = f"""
                                        FROM {tabela("BAR", suf)} T1
                                        LEFT JOIN {tabela("SUB", suf)} S
                                            ON T1.SUB = S.COD_ID
                                    """

                        where_sql = """
                                        WHERE T1.POS = 'PD'
                                    """

                        grupo_cols = [
                                            "S.COD_ID",
                                            *COLUNAS_T1,
                                        ]

                        return cte_modelo(
                                            nome="BAR_SUB",
                                            select_sql=select_sql,
                                            from_sql=from_sql,
                                            where_sql=where_sql,
                                            grupo_colunas=grupo_cols,
                                        )


                    def cte_eqtrm(suf):
                        join_sql = f"""
                                        LEFT JOIN {tabela("SUB", suf)} S
                                            ON T1.SUB = S.COD_ID
                                        LEFT JOIN UC_UNIFIC UCG
                                            ON T1.UC_UG = UCG.COD_ID
                                        AND UCG.GRU_TEN = T1.GRU_TEN
                                    """

                        where_sql = """
                                        WHERE T1.TIP_INST IN ('SE_MT', 'SE_AT')
                                        AND T1.SITCONT IN ('AT1', 'SF', 'RT')
                                    """

                        return cte_simples(
                                                nome="EQTRM_SUB",
                                                tipo="EQTRM",
                                                tabela_base="EQTRM",
                                                suf=suf,
                                                join_sql=join_sql,
                                                where_sql=where_sql,
                                                conj_expr="UCG.CONJ",
                                            )


                    def cte_eqtrmtmt():
                        select_sql = sel_eq(
                                                tipo="TRAFO MT-MT",
                                                sub="S.COD_ID",
                                                cod="UNT.COD_ID",
                                                descr="T1.DESCR",
                                                odi="T1.ODI",
                                                ti="T1.TI",
                                                tuc="T1.TUC",
                                                a1="T1.A1",
                                                a2="T1.A2",
                                                a3="T1.A3",
                                                a4="T1.A4",
                                                a5="T1.A5",
                                                a6="T1.A6",
                                                uar="T1.UAR",
                                                iduc="T1.IDUC",
                                                sitcont="T1.SITCONT",
                                                dat_imo="T1.DAT_IMO",
                                                conj="UNT.CONJ",
                                            )

                        from_sql = """
                                        FROM EQTRMT_AT T1
                                        LEFT JOIN UNTRMT_AT UNT
                                            ON T1.UNI_TR_MT = UNT.COD_ID
                                        LEFT JOIN SUB_AT S
                                            ON UNT.SUB = S.COD_ID
                                    """

                        where_sql = """
                                        WHERE T1.TIP_INST IN ('SE_MT', 'SE_AT')
                                        AND T1.SITCONT IN ('AT1', 'SF', 'RT')
                                    """

                        grupo_cols = [
                                        "S.COD_ID",
                                        *COLUNAS_T1,
                                        "UNT.CONJ",
                                        "UNT.COD_ID",
                                    ]

                        return cte_modelo(
                                            nome="EQTRMTMT_SUB",
                                            select_sql=select_sql,
                                            from_sql=from_sql,
                                            where_sql=where_sql,
                                            grupo_colunas=grupo_cols,
                                        )

                    def cte_eqtrat(suf):
                        select_sql = sel_eq(
                                                tipo="TRAFO AT-MT",
                                                sub="S.COD_ID",
                                                cod="UNT.COD_ID",
                                                descr="T1.DESCR",
                                                odi="T1.ODI",
                                                ti="T1.TI",
                                                tuc="T1.TUC",
                                                a1="T1.A1",
                                                a2="T1.A2",
                                                a3="T1.A3",
                                                a4="T1.A4",
                                                a5="T1.A5",
                                                a6="T1.A6",
                                                uar="T1.UAR",
                                                iduc="T1.IDUC",
                                                sitcont="T1.SITCONT",
                                                dat_imo="T1.DAT_IMO",
                                                conj="UNT.CONJ",
                                            )

                        from_sql = f"""
                                        FROM {tabela("EQTRAT", suf)} T1
                                        LEFT JOIN UNTRAT_AT UNT
                                            ON T1.UNI_TR_AT = UNT.COD_ID
                                        LEFT JOIN SUB_AT S
                                            ON UNT.SUB = S.COD_ID
                                    """

                        where_sql = """
                                        WHERE T1.TIP_INST IN ('SE_MT', 'SE_AT')
                                        AND T1.SITCONT IN ('AT1', 'SF', 'RT')
                                    """

                        grupo_cols = [
                                        "S.COD_ID",
                                        *COLUNAS_T1,
                                        "UNT.CONJ",
                                        "UNT.COD_ID",
                                    ]

                        return cte_modelo(
                                            nome="EQTRAT_SUB",
                                            select_sql=select_sql,
                                            from_sql=from_sql,
                                            where_sql=where_sql,
                                            grupo_colunas=grupo_cols,
                                        )

                    def cte_unificado(nome_cte, tabela_eq, campo_join, tabelas_un, suf):
                        if not tabelas_un:
                            return ""

                        select_sql = sel_eq(
                                            tipo=nome_cte.replace("_UNS", ""),
                                            sub="S.COD_ID",
                                            cod="UNT.COD_ID",
                                            descr="T1.DESCR",
                                            odi="T1.ODI",
                                            ti="T1.TI",
                                            tuc="T1.TUC",
                                            a1="T1.A1",
                                            a2="T1.A2",
                                            a3="T1.A3",
                                            a4="T1.A4",
                                            a5="T1.A5",
                                            a6="T1.A6",
                                            uar="T1.UAR",
                                            iduc="T1.IDUC",
                                            sitcont="T1.SITCONT",
                                            dat_imo="T1.DAT_IMO",
                                            conj="UNT.CONJ",
                                        )

                        from_sql = f"""
                                        FROM {tabela(tabela_eq, suf)} T1
                                        LEFT JOIN (
                                            {subquery_uniao(tabelas_un)}
                                        ) UNT
                                            ON T1.{campo_join} = UNT.COD_ID
                                        AND T1.GRU_TEN = UNT.GRU_TEN
                                        LEFT JOIN {tabela("SUB", suf)} S
                                            ON UNT.SUB = S.COD_ID
                                    """

                        where_sql = """
                                        WHERE T1.TIP_INST IN ('SE_MT', 'SE_AT')
                                        AND T1.SITCONT IN ('AT1', 'SF', 'RT')
                                    """

                        grupo_cols = [
                                        "S.COD_ID",
                                        *COLUNAS_T1,
                                        "UNT.CONJ",
                                        "UNT.COD_ID",
                                    ]

                        return cte_modelo(
                                            nome=nome_cte,
                                            select_sql=select_sql,
                                            from_sql=from_sql,
                                            where_sql=where_sql,
                                            grupo_colunas=grupo_cols,
                                        )

                    def sql_final(ctes):
                        cols = ", ".join(ESQUEMA_EQ)

                        union_sql = "\nUNION ALL\n".join(
                                                            f"SELECT {cols} FROM {cte}"
                                                            for cte in ctes
                                                        )
                        cte_p1 = ",\n".join(ctes_sql)
                        return f"""
                                    WITH
                                    {cte_p1}

                                    SELECT
                                        {cols}
                                    FROM (
                                        {union_sql}
                                    ) BASE
                                    ;
                                """.strip()


                    tabs_cr = [
                                    f"UNCRBT{suf}",
                                    f"UNCRMT{suf}",
                                    f"UNCRAT{suf}",
                                ]
                    tabs_cr = [t for t in tabs_cr if t in tabelas_existentes]

                    tabs_re = [
                                    f"UNREBT{suf}",
                                    f"UNREMT{suf}",
                                    f"UNREAT{suf}",
                                ]
                    tabs_re = [t for t in tabs_re if t in tabelas_existentes]

                    tabs_se = [
                                    f"UNSEBT{suf}",
                                    f"UNSEMT{suf}",
                                    f"UNSEAT{suf}",
                                ]
                    tabs_se = [t for t in tabs_se if t in tabelas_existentes]
                    ctes_sql = [
                                    cte_bay(suf),
                                    cte_bar(suf),
                                    cte_eqtrm(suf),
                                    cte_eqtrmtmt(),
                                    cte_eqtrat(suf),
                                ]

                    cte_eqcr = cte_unificado("EQCR_UNS", "EQCR", "UN_CR", tabs_cr, suf)
                    cte_eqre = cte_unificado("EQRE_UNS", "EQRE", "UN_RE", tabs_re, suf)
                    cte_eqse = cte_unificado("EQSE_UNS", "EQSE", "UN_SE", tabs_se, suf)

                    if cte_eqcr:
                        ctes_sql.append(cte_eqcr)

                    if cte_eqre:
                        ctes_sql.append(cte_eqre)

                    if cte_eqse:
                        ctes_sql.append(cte_eqse)

                    ctes_resultado = [
                                        "BAY_SUB",
                                        "BAR_SUB",
                                        "EQTRM_SUB",
                                        "EQTRMTMT_SUB",
                                        "EQTRAT_SUB",
                                    ]

                    if cte_eqcr:
                        ctes_resultado.append("EQCR_UNS")

                    if cte_eqre:
                        ctes_resultado.append("EQRE_UNS")

                    if cte_eqse:
                        ctes_resultado.append("EQSE_UNS")

                    SQLq = sql_final(ctes_resultado)        
                    df_SE = pd.read_sql(SQLq, bd)

                    ax = (
                            df_SE.groupby(['Subestacao','CONJ'], dropna=False)
                                .agg(CONJ_COUNT = ('CONJ', 'count'))
                                .reset_index()
                        )

                    df_SE = df_SE.sort_values(
                                                by=["Subestacao","TipoEquipamento","TUC","ODI"],
                                                key=lambda col: col.isna(),
                                                kind="stable"
                                            ).reset_index(drop=True)
                    df_SE['ODI'] = df_SE['ODI'].ffill()
                    for n in df_SE.columns.to_list():
                        if n[:2].upper() == 'QT':
                            df_SE[n] = df_SE[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

                    st.dataframe(df_SE, width='stretch', hide_index=True)  

                    dic_ATIVOS = {}
                    dic_ATIVOS['SE'] = df_SE

                    map_tip_pn = {
                                    '': 'ND','0':'ND',
                                    'PIS':'Ponto interno subestação','PSA':'Ponto de saída de circuito de média tensão',
                                    'PSU':'Ponto subterrâneo','POS':'Poste','TOR':'Torre','PSE':'Ponto de suporte de equipamento',
                                    'PSB':'Ponto de suporte de barramento','PEC':'Ponto de entrada de condomínio','PMF':'Ponto de medição de fronteira',
                                    'FLT':'Fly-tap','PFL':'Ponto de fim de linha','CXP':'Caixa de passagem','PON':'Pontalete','DRV':'Derivação'
                                }

                    map_tip_pn = {**{'': 'ND', '0': 'ND'}, **{k:v for k,v in map_tip_pn.items() if isinstance(k,str)}}

                    map_estr = {
                        '': 'ND','0':'ND','AT':'Autoportante','CA':'Cabine','CI':'Circular','CP':'Contra poste','CD':'Curvo duplo',
                        'CS':'Curvo simples','DT':'Duplo T','ES':'Estaiada','HH':'(2 Colunas e Viga Central)','OR':'Ornamental',
                        'QU':'Quadrado','RE':'Retangular','ST':'Sextavado','TO':'Torre ou Treliça','TG':'Triangular','TL':'Trilho',
                        'TS':'Trilho simples','TP':'Trusspole','TU':'Tubular','TQ':'Tubular – Seção quadrada'
                    }

                    map_mat = {
                        '': 'ND','0':'ND','AC':'Aço','CA':'Mista (Concreto e Aço)','CO':'Concreto','CL':'Concreto leve','EC':'Em compósito',
                        'FE':'Ferro','CQ':'Madeira','ME':'Madeira eucalipto','MQ':'Madeira quadrado','MT':'Metálica','AV':'Alvenaria'
                    }

                    map_esf_especial = {
                        '66':'Leve (Madeira)','67':'Médio (Madeira)','68':'Pesado (Madeira)','69':'Extra Pesado (Madeira)',
                        '70':'22 (Trilho)','71':'32 (Trilho)','72':'42 (Trilho)'
                    }
                    map_esf_numerico = {
                        '1':'50 daN','2':'75 daN','3':'90 daN','4':'100 daN','5':'150 daN','6':'200 daN','77':'250 daN','7':'300 daN',
                        '8':'400 daN','9':'450 daN','10':'500 daN','11':'600 daN','12':'700 daN','13':'750 daN','14':'800 daN',
                        '15':'850 daN','16':'900 daN','17':'950 daN','18':'1000 daN','19':'1050 daN','20':'1100 daN','21':'1150 daN',
                        '22':'1200 daN','23':'1250 daN','24':'1300 daN','25':'1350 daN','26':'1400 daN','27':'1450 daN','28':'1500 daN',
                        '29':'1550 daN','30':'1600 daN','31':'1650 daN','32':'1700 daN','33':'1750 daN','34':'1800 daN','73':'1900 daN',
                        '35':'2000 daN','74':'2100 daN','75':'2200 daN','76':'2300 daN','36':'2400 daN','37':'2500 daN','38':'2600 daN',
                        '39':'2700 daN','40':'2800 daN','41':'2900 daN','42':'3000 daN','43':'3100 daN','44':'3200 daN','45':'3300 daN',
                        '46':'3400 daN','47':'3500 daN','48':'3600 daN','49':'3700 daN','50':'3800 daN','51':'3900 daN','52':'4000 daN',
                        '53':'4100 daN','54':'4200 daN','55':'4300 daN','56':'4400 daN','57':'4500 daN','58':'4600 daN','59':'4700 daN',
                        '60':'4800 daN','61':'4900 daN','62':'5000 daN','63':'5100 daN','64':'5600 daN','65':'5700 daN'
                    }
                    map_esf = {**{'': 'ND','0':'ND'}, **map_esf_numerico, **map_esf_especial}

                    map_alt = {'0' : 'Não informado ou não aplicável', '1' : '4,3 m', '2' : '4,5 m', '3' : '5 m', '4' : '6 m', '5' : '7 m', 
                            '6' : '7,5 m', '7' : '8 m', '8' : '8,5 m', '9' : '9 m', '10' : '10 m', '11' : '10,5 m', '12' : '11 m', 
                            '13' : '12 m', '14' : '13 m', '15' : '14 m', '16' : '15 m', '17' : '16 m', '18' : '17 m', '19' : '17,5 m', 
                            '20' : '18 m', '21' : '19 m', '22' : '20 m', '23' : '20,5 m', '24' : '21 m', '25' : '21,5 m', '26' : '22 m', 
                            '27' : '23 m', '28' : '23,5 m', '29' : '24 m', '30' : '24,6 m', '31' : '25 m', '32' : '26 m', '33' : '26,6 m', 
                            '34' : '27 m', '35' : '27,6 m', '36' : '27,7 m', '37' : '28 m', '38' : '28,6 m', '39' : '28,7 m', '40' : '29 m', 
                            '41' : '29,6 m', '42' : '29,7 m', '43' : '30 m', '44' : '30,2 m', '45' : '31 m', '46' : '32 m', '47' : '33 m', 
                            '48' : '34 m', '49' : '35 m', '50' : '36 m', '51' : '37 m', '52' : '38 m', '53' : '39 m', '54' : '40 m', 
                            '55' : '42 m', '56' : '43 m', '57' : '44 m', '58' : '45 m', '59' : '46 m', '60' : '47 m', '61' : '48 m', 
                            '62' : '49 m', '63' : '50 m', '64' : '51 m', '65' : '52 m', '70' : '53 m', '66' : '54 m', '71' : '55 m', 
                            '72' : '56 m', '73' : '57 m', '74' : '58 m', '75' : '59 m', '76' : '60 m', '77' : '61 m', '78' : '62 m', 
                            '79' : '63 m', '67' : '64 m', '80' : '65 m', '68' : '66 m', '81' : '67 m', '82' : '68 m', '83' : '69 m', 
                            '84' : '70 m', '85' : '71 m', '86' : '72 m', '87' : '73 m', '88' : '74 m', '89' : '75 m', '90' : '76 m', 
                            '91' : '77 m', '92' : '78 m', '93' : '79 m', '94' : '80 m', '95' : '81 m', '96' : '82 m', '97' : '83 m', 
                            '69' : '84 m', '98' : '85 m', '99' : '86 m', '100' : '87 m', '101' : '88 m', '102' : '89 m', '103' : '90 m'
                            }
                    
                    SQLest = ""
                    
                    for nmLD in ["SSDAT", "SSDMT"]:
                        texto, dic_ATIVOS[f'df_LD_{nmLD[-2:]}'] = cnt_bloco(nmLD, suf, bd, tabelas_existentes, st=st)
                        if len(dic_ATIVOS[f'df_LD_{nmLD[-2:]}']):
                            _, _, label = _mk_ax(nmLD)
                            st.html(
                                            f"<p style='text-align: justify; text-indent: 40px'>Resultado para linhas em {label} nesta empresa.</p><hr/>"
                                        )
                            st.dataframe(dic_ATIVOS[f'df_LD_{nmLD[-2:]}'], width='stretch', hide_index=True)
                        else:
                            _, _, label = _mk_ax(nmLD)
                            st.html(
                                            f"<p style='text-align: justify; text-indent: 40px'>Não há linhas de distribuição para {label} nesta empresa.</p><hr/>"
                                        )
                        if f"{nmLD}{suf}" in tabelas_existentes:
                            df = pd.read_sql(ponnot_filtrados(nmLD, suf), bd)
                            df['TIP_PN_DESC']  = _map(df, 'TIP_PN', map_tip_pn)
                            df['TIP_ESTR']     = _map(df, 'ESTR',   map_estr)
                            df['TIP_MAT']      = _map(df, 'MAT',    map_mat)
                            df['TIP_ESF']      = _map(df, 'ESF',    map_esf)
                            df['TIP_ALT']      = _map(df, 'ALT',    map_alt)

                            df = df.drop(columns=['TIP_PN', 'ESTR','MAT', 'ESF', 'ALT'])
                            dic_ATIVOS[f'df_LD_ESTR_{nmLD[-2:]}'] = df.copy()
                            if f"{nmLD}{suf}" not in tabelas_existentes:
                                _, _, label = _mk_ax(nmLD)
                                st.html(
                                    f"""<p style='text-align: justify; text-indent: 40px'>Não há linhas para {label} nesta 
                                    empresa.</p><hr/>"""
                                )
                            else:
                                if len(df):
                                    st1 = st.html(texto_exp_postes(nmLD))
                                    st.dataframe(df, width='stretch', hide_index=True)

                    def unidades_existentes(prefixos, suf, tabelas_existentes):
                        tabs = [f"{p}{suf}" for p in prefixos]
                        return [t for t in tabs if t in tabelas_existentes]


                    def uniao_unidades(tabs):
                        return " UNION ALL ".join(
                            f"SELECT COD_ID, SUB, CONJ, GRU_TEN FROM {t}"
                            for t in tabs
                        )
                    
                    dic_EQ = {
                                'LD': ('LD_AER_MT', 'LD_AER_AT', 'LD_SUB_MT', 'LD_SUB_AT'),
                                'RD': ('RD_AER_URB', 'RD_AER_RUR', 'RD_SUBT_URB', 'RD_SUBT_RUR', 'RD_SUBM')
                            }
                    
                    for chave, valor in dic_EQ.items():
                        tabs_cr = unidades_existentes(
                                                        ["UNCRBT", "UNCRMT", "UNCRAT"],
                                                        suf,
                                                        tabelas_existentes
                                                    )
                        if tabs_cr:
                            SQLq_ECR = f""",EQCR_UNS AS (
                                SELECT 
                                    'EQCR_{chave}' AS TipoEquipamento,
                                    S.COD_ID AS Subestacao,
                                    UNT.COD_ID AS CodigoEquipamento,
                                    T1.DESCR AS DescricaoEquipamento,
                                    T1.ODI,
                                    T1.TI,
                                    T1.TUC,
                                    T1.A1,
                                    T1.A2,
                                    T1.A3,
                                    T1.A4,
                                    T1.A5,
                                    T1.A6,
                                    T1.UAR,
                                    T1.IDUC,
                                    T1.SITCONT,
                                    T1.DAT_IMO,
                                    UNT.CONJ,
                                    COUNT(*) AS Qtd_BDGD
                                FROM (
                                        {uniao_unidades(tabs_cr)}
                                    ) UNT
                                LEFT JOIN EQCR{suf} T1
                                    ON T1.UN_CR = UNT.COD_ID
                                AND T1.GRU_TEN = UNT.GRU_TEN
                                LEFT JOIN SUB{suf} S ON UNT.SUB = S.COD_ID
                                WHERE T1.TIP_INST IN {valor}
                                AND T1.SITCONT IN ('AT1','SF','RT')
                                GROUP BY
                                    S.COD_ID,
                                    T1.DESCR,
                                    T1.ODI,
                                    T1.TI,
                                    T1.TUC,
                                    T1.A1,
                                    T1.A2,
                                    T1.A3,
                                    T1.A4,
                                    T1.A5,
                                    T1.A6,
                                    T1.UAR,
                                    T1.IDUC,
                                    T1.SITCONT,
                                    T1.DAT_IMO,
                                    UNT.CONJ,
                                    UNT.COD_ID
                            )"""
                        else:
                            SQLq_ECR = ""

                        tabs_re = unidades_existentes(
                                                        ["UNREBT", "UNREMT", "UNREAT"],
                                                        suf,
                                                        tabelas_existentes
                                                    )

                        if tabs_re:
                            SQLq_RE = f""",EQRE_UNS AS (
                                SELECT 
                                    'EQRE_{chave}' AS TipoEquipamento,
                                    S.COD_ID AS Subestacao,
                                    UNT.COD_ID AS CodigoEquipamento,
                                    T1.DESCR AS DescricaoEquipamento,
                                    T1.ODI,
                                    T1.TI,
                                    T1.TUC,
                                    T1.A1,
                                    T1.A2,
                                    T1.A3,
                                    T1.A4,
                                    T1.A5,
                                    T1.A6,
                                    T1.UAR,
                                    T1.IDUC,
                                    T1.SITCONT,
                                    T1.DAT_IMO,
                                    UNT.CONJ,
                                    COUNT(*) AS Qtd_BDGD
                                FROM (
                                    {uniao_unidades(tabs_re)}
                                ) UNT
                                LEFT JOIN EQRE{suf} T1
                                    ON T1.UN_RE = UNT.COD_ID
                                AND T1.GRU_TEN = UNT.GRU_TEN
                                LEFT JOIN SUB{suf} S ON UNT.SUB = S.COD_ID
                                WHERE T1.TIP_INST IN {valor}
                                AND T1.SITCONT IN ('AT1','SF','RT')
                                GROUP BY
                                    S.COD_ID,
                                    T1.DESCR,
                                    T1.TI,
                                    T1.TUC,
                                    T1.A1,
                                    T1.A2,
                                    T1.A3,
                                    T1.A4,
                                    T1.A5,
                                    T1.A6,
                                    T1.UAR,
                                    T1.IDUC,
                                    T1.SITCONT,
                                    T1.DAT_IMO,
                                    UNT.CONJ,
                                    UNT.COD_ID
                            )"""
                        else:
                            SQLq_RE = ""

                        tabs_se = unidades_existentes(
                                                        ["UNSEBT", "UNSEMT", "UNSEAT"],
                                                        suf,
                                                        tabelas_existentes
                                                    )

                        if tabs_se:
                            SQLq_SE = f""",EQSE_UNS AS (
                                SELECT 
                                    'EQSE_{chave}' AS TipoEquipamento,
                                    S.COD_ID AS Subestacao,
                                    UNT.COD_ID AS CodigoEquipamento,
                                    T1.DESCR AS DescricaoEquipamento,
                                    T1.ODI,
                                    T1.TI,
                                    T1.TUC,
                                    T1.A1,
                                    T1.A2,
                                    T1.A3,
                                    T1.A4,
                                    T1.A5,
                                    T1.A6,
                                    T1.UAR,
                                    T1.IDUC,
                                    T1.SITCONT,
                                    T1.DAT_IMO,
                                    UNT.CONJ,
                                    COUNT(*) AS Qtd_BDGD
                                FROM (
                                    {uniao_unidades(tabs_se)}
                                ) UNT
                                LEFT JOIN EQSE{suf} T1
                                    ON T1.UN_SE = UNT.COD_ID
                                AND T1.GRU_TEN = UNT.GRU_TEN
                                LEFT JOIN SUB{suf} S ON UNT.SUB = S.COD_ID
                                WHERE T1.TIP_INST IN {valor}
                                AND T1.SITCONT IN ('AT1','SF','RT')
                                GROUP BY
                                    S.COD_ID,
                                    T1.DESCR,
                                    T1.TI,
                                    T1.TUC,
                                    T1.A1,
                                    T1.A2,
                                    T1.A3,
                                    T1.A4,
                                    T1.A5,
                                    T1.A6,
                                    T1.UAR,
                                    T1.IDUC,
                                    T1.SITCONT,
                                    T1.DAT_IMO,
                                    UNT.CONJ,
                                    UNT.COD_ID
                            )"""
                        else:
                            SQLq_SE = ""

                        SQLq = f"""
                                    WITH
                                    EQTRAT_SUB AS (
                                        SELECT 'TRAFO_{chave}' AS TipoEquipamento,
                                            S.COD_ID AS Subestacao,
                                            UNT.COD_ID AS CodigoEquipamento,
                                            T1.DESCR AS DescricaoEquipamento,
                                            T1.ODI,
                                            T1.TI,
                                            T1.TUC,
                                            T1.A1,
                                            T1.A2,
                                            T1.A3,
                                            T1.A4,
                                            T1.A5,
                                            T1.A6,
                                            T1.UAR,
                                            T1.IDUC,
                                            T1.SITCONT,
                                            T1.DAT_IMO,
                                            UNT.CONJ,
                                            COUNT(*) AS Qtd_BDGD
                                        FROM UNTRAT{suf} UNT
                                        LEFT JOIN EQTRAT{suf} T1 ON T1.UNI_TR_AT = UNT.COD_ID
                                        LEFT JOIN SUB{suf} S ON UNT.SUB = S.COD_ID
                                        WHERE T1.TIP_INST IN {valor}
                                        AND T1.SITCONT IN ('AT1','SF','RT')
                                        GROUP BY
                                            S.COD_ID,
                                            T1.DESCR,
                                            T1.TI,
                                            T1.TUC,
                                            T1.A1,
                                            T1.A2,
                                            T1.A3,
                                            T1.A4,
                                            T1.A5,
                                            T1.A6,
                                            T1.UAR,
                                            T1.IDUC,
                                            T1.SITCONT,
                                            T1.DAT_IMO,
                                            UNT.CONJ,
                                            UNT.COD_ID
                                    ),
                                    EQTRMTMT_SUB AS ( 
                                        SELECT 
                                            'TRAFO MT-BT' AS TipoEquipamento, 
                                            S.COD_ID AS Subestacao, 
                                            UNT.COD_ID AS CodigoEquipamento, 
                                            T1.DESCR AS DescricaoEquipamento, 
                                            T1.ODI, T1.TI, T1.TUC, T1.A1, T1.A2, T1.A3, T1.A4, T1.A5, T1.A6, 
                                            T1.UAR, T1.IDUC, T1.SITCONT,
                                            T1.DAT_IMO, UNT.CONJ, 
                                            COUNT(*) AS Qtd_BDGD 
                                        FROM UNTRMT{suf} UNT 
                                        LEFT JOIN EQTRMT{suf} T1 
                                        ON T1.UNI_TR_MT = UNT.COD_ID 
                                        LEFT JOIN SUB{suf} S ON UNT.SUB = S.COD_ID 
                                        WHERE T1.TIP_INST IN {valor} AND T1.SITCONT IN ('AT1','SF','RT') 
                                        GROUP BY S.COD_ID, T1.DESCR, T1.TI, T1.TUC, T1.A1, T1.A2, T1.A3, T1.A4, T1.A5, 
                                        T1.A6, T1.UAR, T1.IDUC, T1.SITCONT,
                                            T1.DAT_IMO, UNT.CONJ, UNT.COD_ID ),
                                    EQTRM_SUB AS (
                                        SELECT 'EQTRM_{chave}' AS TipoEquipamento,
                                            S.COD_ID AS Subestacao,
                                            UCG.COD_ID AS CodigoEquipamento,
                                            T1.DESCR AS DescricaoEquipamento,
                                            T1.ODI,
                                            T1.TI,
                                            T1.TUC,
                                            T1.A1,
                                            T1.A2,
                                            T1.A3,
                                            T1.A4,
                                            T1.A5,
                                            T1.A6,
                                            T1.UAR,
                                            T1.IDUC,
                                            T1.SITCONT,
                                            T1.DAT_IMO,
                                            COALESCE(UCG.CONJ,'NA') AS CONJ,
                                            COUNT(*) AS Qtd_BDGD
                                        FROM EQTRM{suf} T1
                                        LEFT JOIN SUB{suf} S ON T1.SUB = S.COD_ID
                                        LEFT JOIN UC_UNIFIC UCG ON T1.UC_UG = UCG.COD_ID
                                        WHERE T1.TIP_INST IN {valor}
                                        AND T1.SITCONT IN ('AT1','SF','RT')
                                        GROUP BY
                                            S.COD_ID,
                                            T1.DESCR,
                                            T1.TI,
                                            T1.TUC,
                                            T1.A1,
                                            T1.A2,
                                            T1.A3,
                                            T1.A4,
                                            T1.A5,
                                            T1.A6,
                                            T1.UAR,
                                            T1.IDUC,
                                            T1.SITCONT,
                                            T1.DAT_IMO,
                                            UCG.COD_ID
                                    ),

                                    PONNOT_SUB AS (
                                        SELECT 
                                            CASE
                                                WHEN T1.TIP_PN = '0' THEN 'NINF_{chave}'
                                                WHEN T1.TIP_PN = 'PIS' THEN 'Ponto_interno_subestacao_{chave}'
                                                WHEN T1.TIP_PN = 'PSA' THEN 'Ponto_saida_circuito_media_tensao_{chave}'
                                                WHEN T1.TIP_PN = 'PSU ' THEN 'Ponto_subterraneo_{chave}'
                                                WHEN T1.TIP_PN = 'POS' THEN 'POSTE_{chave}'
                                                WHEN T1.TIP_PN = 'TOR' THEN 'TORRE_{chave}'
                                                WHEN T1.TIP_PN = 'PSE ' THEN 'Ponto_suporte_equipamento_{chave}'
                                                WHEN T1.TIP_PN = 'PSB' THEN 'Ponto_suporte_barramento_{chave}'
                                                WHEN T1.TIP_PN = 'PEC' THEN 'Ponto_entrada_condominio_{chave}'
                                                WHEN T1.TIP_PN = 'PMF' THEN 'Ponto_medicao_fronteira_{chave}'
                                                WHEN T1.TIP_PN = 'FLT' THEN 'Fly_tap_{chave}'
                                                WHEN T1.TIP_PN = 'PFL' THEN 'Ponto_fim_linha_{chave}'
                                                WHEN T1.TIP_PN = 'CXP' THEN 'Caixa_passagem_{chave}'
                                                WHEN T1.TIP_PN = 'PON' THEN 'Pontalete_{chave}'
                                                WHEN T1.TIP_PN = 'DRV' THEN 'Derivacao_{chave}'
                                                ELSE 'Codigo_invalido_{chave}'
                                            END AS TipoEquipamento,
                                            S.SUB AS Subestacao,
                                            T1.COD_ID AS CodigoEquipamento,
                                            T1.DESCR AS DescricaoEquipamento,
                                            T1.ODI,
                                            T1.TI,
                                            T1.TUC,
                                            T1.A1,
                                            T1.A2,
                                            T1.A3,
                                            T1.A4,
                                            T1.A5,
                                            T1.A6,
                                            T1.UAR,
                                            'NA' AS IDUC,
                                            T1.SITCONT,
                                            '' AS DAT_IMO,
                                            T1.CONJ,
                                            COUNT(*) AS Qtd_BDGD
                                        FROM PONNOT{suf} T1
                                        LEFT JOIN (SELECT DISTINCT ODI, SUB FROM BAR{suf}) S ON T1.ODI = S.ODI
                                        WHERE T1.TIP_INST IN {valor}
                                        AND T1.SITCONT IN ('AT1','SF','RT') AND T1.TIP_PN NOT IN ('POS','TOR')
                                        GROUP BY
                                            S.SUB,
                                            T1.DESCR,
                                            T1.TI,
                                            T1.TUC,
                                            T1.A1,
                                            T1.A2,
                                            T1.A3,
                                            T1.A4,
                                            T1.A5,
                                            T1.A6,
                                            T1.UAR,
                                            T1.SITCONT
                                    )

                                    {SQLq_ECR}
                                    {SQLq_RE}
                                    {SQLq_SE}

                                    SELECT * FROM EQTRM_SUB
                                    UNION ALL SELECT * FROM EQTRAT_SUB
                                    UNION ALL SELECT * FROM EQTRMTMT_SUB
                                    UNION ALL SELECT * FROM PONNOT_SUB
                                    { "UNION ALL SELECT * FROM EQCR_UNS" if SQLq_ECR else "" }
                                    { "UNION ALL SELECT * FROM EQRE_UNS" if SQLq_RE else "" }
                                    { "UNION ALL SELECT * FROM EQSE_UNS" if SQLq_SE else "" }
                                    ;
                        """

                        df_LD = pd.read_sql(SQLq, bd)

                        if len(df_LD):
                            df_LD = df_LD.sort_values(
                                    by=["Subestacao","TipoEquipamento","TUC","ODI"],
                                    key=lambda col: col.isna(),
                                    kind="stable"
                                ).reset_index(drop=True)
                            df_LD['ODI'] = df_LD['ODI'].ffill()
                            for n in df_LD.columns.to_list():
                                if n[:2].upper() == 'QT':
                                    df_LD[n] = df_LD[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                            st.html(
                                    f"""<p style='text-align: justify; text-indent: 40px'>A seguir, temos os equipamentos e estruturas de suporte, 
                                    que não seja poste ou torre, para {chave}, 
                                    para a empresa, conforme modelados na BDGD, agrupando por tipo, localização e características técnicas. 
                                    Os dados são extraídos de entidades que representam equipamentos instalados ao longo dos circuitos ou 
                                    associados por referência geográfica aos seus segmentos (ex.: chaves seccionadoras, religadores, 
                                    transformadores, bancos de capacitores, reguladores de tensão). A coluna Qtd_BDGD representa a 
                                    quantidade consolidada por combinação de atributos técnicos; os itens cujo campo CONJ (derivado de TI, 
                                    TUC e A1–A6) seja distinto de “NA” são tratados como alocações diretas ao conjunto/trecho correspondente. 
                                    Quando CONJ = “NA”, os equipamentos são considerados parte de uma agregação coletiva e serão rateados 
                                    conforme critério a ser explicitado. Essa distinção assegura a granularidade adequada para a modelagem 
                                    patrimonial por circuito e rede, preservando a rastreabilidade físico-contábil.</p><hr/>"""
                                )
                            st.dataframe(df_LD, width='stretch', hide_index=True)
                            dic_ATIVOS[chave] =  df_LD  

                    SQLest = ""

                    for nmLD in ["SSDAT", "SSDMT", "SSDBT"]:
                        texto, dic_ATIVOS[f'df_RD_{nmLD[-2:]}'] = cnt_bloco_rd(nmLD, suf, bd, tabelas_existentes, st=st)
                        
                        label = nmLD[-2:]
                        if f'df_RD_{nmLD[-2:]}' in dic_ATIVOS.keys() and hasattr(dic_ATIVOS[f'df_RD_{nmLD[-2:]}'], '__len__') and len(dic_ATIVOS[f'df_RD_{nmLD[-2:]}']):
                            st.html(texto)
                            st.html(
                                        f"""<p style='text-align: justify; text-indent: 40px'>A seguir o resultado para as redes 
                                        de {label} nesta empresa.</p><hr/>"""
                                    )
                            st.dataframe(dic_ATIVOS[f'df_RD_{nmLD[-2:]}'], width='stretch', hide_index=True)
                        
                            if f"{nmLD}{suf}" in tabelas_existentes:
                                SQLq = ponnot_filtrados_rd(nmLD, suf)
                                
                                if SQLq == "":
                                    continue
                                df = pd.read_sql(SQLq, bd)

                                df['TIP_PN_DESC']  = _map(df, 'TIP_PN', map_tip_pn)
                                df['TIP_ESTR']     = _map(df, 'ESTR',   map_estr)
                                df['TIP_MAT']      = _map(df, 'MAT',    map_mat)
                                df['TIP_ESF']      = _map(df, 'ESF',    map_esf)
                                df['TIP_ALT']      = _map(df, 'ALT',    map_alt)

                                df = df.drop(columns=['TIP_PN', 'ESTR','MAT', 'ESF', 'ALT'])
                                dic_ATIVOS[f'df_RD_ESTR_{nmLD[-2:]}'] = df.copy()
                                label = nmLD[-2:]
                                if f"{nmLD}{suf}" not in tabelas_existentes:
                                    st.html(
                                                f"""<p style='text-align: justify; text-indent: 40px'>Não há estruturas 
                                                para redes de  {label} nesta empresa.</p><hr/>"""
                                            )
                                else:
                                    if len(df):
                                        st.html(texto_exp_postes_rd(nmLD))
                                        st.dataframe(df.head(10000), width='stretch', hide_index=True)
                        else:
                            st.html(
                                        f"""<p style='text-align: justify; text-indent: 40px'>Não há redes para {label} 
                                        nesta empresa.</p><hr/>"""
                                    )
                    
                    
                    SQLest = ""
                    
                    for nmLD in ["RAMLIG"]:
                        texto, dic_ATIVOS[f'df_RAMAIS'] = cnt_bloco_rm(nmLD, suf, bd, tabelas_existentes, st)
                        if len(dic_ATIVOS[f'df_RAMAIS']):
                            st.html(texto)
                            st.dataframe(dic_ATIVOS[f'df_RAMAIS'].head(10000), width='stretch', hide_index=True)
                        else:
                            st.html(
                                        f"""<p style='text-align: justify; text-indent: 40px'>Não há ramal 
                                        nesta empresa.</p><hr/>"""
                                    )
                            continue

                        if f"{nmLD}{suf}" in tabelas_existentes:
                            SQLq =  ponnot_filtrados_rm(nmLD, suf)   
                            df = pd.read_sql(SQLq, bd)
                            df['TIP_PN_DESC']  = _map(df, 'TIP_PN', map_tip_pn)
                            df['TIP_ESTR']     = _map(df, 'ESTR',   map_estr)
                            df['TIP_MAT']      = _map(df, 'MAT',    map_mat)
                            df['TIP_ESF']      = _map(df, 'ESF',    map_esf)
                            df['TIP_ALT']      = _map(df, 'ALT',    map_alt)

                            df = df.drop(columns=['TIP_PN', 'ESTR','MAT', 'ESF', 'ALT'])
                            dic_ATIVOS[f'df_RAMAIS_EST'] = df.copy()
                            if f"{nmLD}{suf}" not in tabelas_existentes:
                                st.html(
                                    f"<p style='text-align: justify; text-indent: 40px'>Não há estruturas em ramais nesta empresa.</p><hr/>"
                                )
                            else:
                                if len(df):
                                    st.html(texto_exp_postes_rm(nmLD))
                                    st.dataframe(df.head(10000), width='stretch', hide_index=True)

                    SQLq_EQMED = f"""
                                            SELECT 
                                                'EQMED_{chave}' AS TipoEquipamento, 
                                                'NA' AS Subestacao, 
                                                UCG.COD_ID AS CodigoEquipamento, 
                                                'ND' AS DescricaoEquipamento,
                                                CASE
                                                    WHEN T1.TIPMED IN (0,1) THEN 'Analógico'
                                                    WHEN T1.TIPMED = 2     THEN 'Digital'
                                                    ELSE 'Código inválido'
                                                END AS TP_MED,
                                                CASE
                                                    WHEN T1.TIP_UNID = 1  THEN 'Comparador fiscal ou concentrado'
                                                    WHEN T1.TIP_UNID = 2  THEN 'Medidor eletromecânico'
                                                    WHEN T1.TIP_UNID = 3  THEN 'Medidor eletrônico'
                                                    WHEN T1.TIP_UNID = 52 THEN 'Módulos de Display e/ou Corte-Religa separados do medidor'
                                                    ELSE 'Código inválido'
                                                END AS TP_UNIDADE,
                                                T1.FAS_CON,
                                                T1.ODI,
                                                T1.TI,
                                                T1.TUC,
                                                T1.A1,
                                                T1.A2,
                                                T1.A3,
                                                T1.A4,
                                                T1.A5,
                                                T1.A6,
                                                T1.UAR,
                                                T1.GRU_TEN,
                                                T1.SITCONT,
                                                T1.DAT_IMO,
                                                COALESCE(UCG.CONJ, 'NA') AS CONJ,
                                                COUNT(*) AS Qtd_BDGD
                                            FROM UC_UNIFIC UCG 
                                            LEFT JOIN  EQME{suf} T1
                                                ON T1.UC_UG = UCG.COD_ID AND T1.GRU_TEN=UCG.GRU_TEN
                                            WHERE T1.SITCONT IN ('AT1','SF','RT')
                                            GROUP BY
                                                T1.TIPMED,
                                                T1.TIP_UNID,
                                                T1.FAS_CON,
                                                T1.ODI,
                                                T1.TI,
                                                T1.TUC,
                                                T1.A1,
                                                T1.A2,
                                                T1.A3,
                                                T1.A4,
                                                T1.A5,
                                                T1.A6,
                                                T1.UAR,
                                                T1.GRU_TEN,
                                                T1.SITCONT,
                                                T1.DAT_IMO,
                                                UCG.CONJ,
                                                UCG.COD_ID
                                        
                                    """

                    df_MED = pd.read_sql(SQLq_EQMED, bd)
                    if len(df_MED):
                        # Texto explicativo
                        st.html(f"""<p style="text-align: justify; text-indent: 40px">
                                A consulta a seguir tem como objetivo identificar as quantidades físicas de
                                <b>equipamentos de medição de energia elétrica</b> modeladas na base BDGD, agrupando por tipo de medição,
                                unidade do medidor e características técnicas. Os dados são obtidos da entidade de medidores
                                (EQME), contemplando atributos como <i>TIPMED</i> (analógico/digital), <i>TIP_UNID</i> (comparador fiscal, 
                                eletromecânico, eletrônico, módulos de display/corte-religa), <i>FAS_CON</i> (configuração de fases) e 
                                <i>GRU_TEN</i> (grupo de tensão), além de referências patrimoniais (ODI, TI, TUC, A1–A6, UAR).
                                A coluna <b>Qtd_BDGD</b> representa a quantidade consolidada por combinação de atributos técnicos; itens cujo
                                campo <b>CONJ</b> (derivado da junção de TI, TUC e A1–A6) possuam valor distinto de 'NA' são tratados como
                                <b>alocações diretas</b> — com correspondência física explícita ao conjunto. Nos casos em que <b>CONJ</b> 
                                equivale a 'NA', os medidores são considerados <b>agregações coletivas</b> e, portanto, sujeitos a rateio 
                                por critério específico, oportunamente explicitado. Essa distinção permite analisar, com maior granularidade,
                                a modelagem patrimonial dos sistemas de medição por conjunto, assegurando rastreabilidade entre o cadastro
                                técnico e a consolidação quantitativa.
                            </p>
                            <hr/>       
                        """)
                        st.dataframe(df_MED.head(10000), width='stretch', hide_index=True)
                        dic_ATIVOS[f'df_MED'] = df_MED.copy()

                    for tabela, dado in dic_ATIVOS.items():
                        if dado is not None and not dado.empty:
                            dado.to_sql(
                                            f"ANL_CMU_{tabela}",
                                            bd,
                                            if_exists='replace',
                                            index=False
                                        )

                resumo_bdgd = pd.DataFrame()
                
                for nm, tbl in dic_ATIVOS.items():  
                    if len(tbl)==0:
                        continue   
                    if nm in ["SE", "RD"]:
                        df1 = tbl.copy()
                        df1.columns = ["Tipo","Local","Codigo","Descricao","ODI",
                                        "TI","TUC","A1","A2","A3","A4","A5","A6",
                                        "UAR","IDUC","SITCONT",'DAT_IMO',"CONJ","Qtd_BDGD"]
                    elif nm in ["df_LD_AT","df_RD_MT", "df_RD_BT", "df_RAMAIS"]:
                        df1 = tbl[["TipoEquipamento","NomeLinha","CodigoLinha","DescrLinha","ODI",
                                "TI","TUC","A1","A2","A3","A4","A5","A6","UAR","TP_CABO","SITCONT",
                                "CONJ","Qtd_BDGD_m","Qtd_BDGD_kg"]].copy()
                        df1["TP_CABO"] = ""
                        df1["Qtd_BDGD"] = df1["Qtd_BDGD_kg"]
                        df1.loc[df1["A3"].isin(['1','01',1]), "Qtd_BDGD"] = df1["Qtd_BDGD_m"]
                        df1 = df1.drop(columns=['Qtd_BDGD_kg','Qtd_BDGD_m'])
                        df1.columns = ["Tipo","Local","Codigo","Descricao","ODI",
                                        "TI","TUC","A1","A2","A3","A4","A5","A6",
                                        "UAR","IDUC","SITCONT","CONJ","Qtd_BDGD"]
                        df1['DAT_IMO'] = None
                    elif nm in ["df_LD_ESTR_AT", "df_LD_ESTR_MT", "df_LD_ESTR_BT", "df_RD_ESTR_AT", 
                                "df_RD_ESTR_MT","df_RD_ESTR_BT", "df_RAMAIS_EST"]:
                        df1 = tbl[["TIP_PN_DESC","CT_LIST","COD_ID","DESCR","ODI",
                                "TI","TUC","A1","A2","A3","A4","A5","A6","UAR","TIP_MAT","SITCONT",
                                "CONJ","Qtd_BDGD"]].copy()
                        df1["TIP_MAT"] = ""
                        df1.columns = ["Tipo","Local","Codigo","Descricao","ODI",
                                        "TI","TUC","A1","A2","A3","A4","A5","A6",
                                        "UAR","IDUC","SITCONT","CONJ","Qtd_BDGD"]
                        df1['DAT_IMO'] = None
                    elif nm == 'df_MED':
                        df1 = tbl[["TipoEquipamento","Subestacao","CodigoEquipamento","DescricaoEquipamento",
                                "ODI","TI","TUC","A1","A2","A3","A4","A5","A6","UAR","GRU_TEN","SITCONT","DAT_IMO",
                                "CONJ","Qtd_BDGD"]].copy()
                        df1["GRU_TEN"] = ""
                        df1.columns = ["Tipo","Local","Codigo","Descricao","ODI",
                                        "TI","TUC","A1","A2","A3","A4","A5","A6",
                                        "UAR","IDUC","SITCONT","DAT_IMO","CONJ","Qtd_BDGD"]
                    elif nm == 'df_TD':
                        continue
                        df1 = tbl[["TipoEquipamento","Subestacao","CodigoEquipamento","DescricaoEquipamento",
                                "ODI","TI","TUC","A1","A2","A3","A4","A5","A6","UAR","SITCONT","DAT_IMO",
                                "CONJ","Qtd_BDGD"]].copy()
                        df1["GRU_TEN"] = "MT"
                        df1.columns = ["Tipo","Local","Codigo","Descricao","ODI",
                                        "TI","TUC","A1","A2","A3","A4","A5","A6",
                                        "UAR","IDUC","SITCONT","DAT_IMO","CONJ","Qtd_BDGD"]
                    elif nm == 'LD':
                        df1 = tbl[["TipoEquipamento","Subestacao","CodigoEquipamento","DescricaoEquipamento",
                                "ODI","TI","TUC","A1","A2","A3","A4","A5","A6","UAR","IDUC","SITCONT","DAT_IMO",
                                "CONJ","Qtd_BDGD"]].copy()
                        df1.columns = ["Tipo","Local","Codigo","Descricao","ODI",
                                        "TI","TUC","A1","A2","A3","A4","A5","A6",
                                        "UAR","IDUC","SITCONT","DAT_IMO","CONJ","Qtd_BDGD"]
                    else:
                        st.divider()
                        st.error(f"{nm} não está feita ainda!")
                        st.write(tbl)
                        st.divider()
                        raise
                        
                    if df1['Qtd_BDGD'].dtype == 'object':
                        df1['Qtd_BDGD'] = pd.to_numeric(df1['Qtd_BDGD'].str.replace(".","").str.replace(",","."), errors='coerce')
                    if not len(resumo_bdgd):
                        resumo_bdgd = df1[["Tipo","Local","Codigo","Descricao","ODI",
                                            "TI","TUC","A1","A2","A3","A4","A5","A6","UAR","IDUC","SITCONT","DAT_IMO","CONJ","Qtd_BDGD",
                                            ]].copy()
                    else:
                        resumo_bdgd = pd.concat([resumo_bdgd, df1[["Tipo","Local","Codigo","Descricao","ODI",
                                            "TI","TUC","A1","A2","A3","A4","A5","A6","UAR","IDUC","SITCONT","DAT_IMO","CONJ","Qtd_BDGD",
                                            ]]], ignore_index=True)
                resumo_bdgd.to_sql(f"RESUMO_BDGD{suf}",
                            bd,
                            if_exists='replace',
                            index=False)
                return resumo_bdgd
```

</details>

---

<a id="funcao-2"></a>

## sel_eq

Gera uma string SQL para consulta de equipamentos.

A função cria uma consulta SQL SELECT com os parâmetros fornecidos, que representam diferentes campos de um equipamento. O parâmetro 'qtd' define a coluna de contagem retornada na consulta.

### Assinatura

```python
# Consulte o código-fonte de sel_eq
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `tipo` | `Não especificado` | Tipo do equipamento. |
| `sub` | `Não especificado` | Subestação onde o equipamento está localizado. |
| `cod` | `Não especificado` | Código do equipamento. |
| `descr` | `Não especificado` | Descrição detalhada do equipamento. |
| `odi` | `Não especificado` | ODI (Operational Data Identifier) do equipamento. |
| `ti` | `Não especificado` | TI (Technical Information) do equipamento. |
| `tuc` | `Não especificado` | TUC (Technical Unit Code) do equipamento. |
| `a1` | `Não especificado` | Atributo 1 do equipamento. |
| `a2` | `Não especificado` | Atributo 2 do equipamento. |
| `a3` | `Não especificado` | Atributo 3 do equipamento. |
| `a4` | `Não especificado` | Atributo 4 do equipamento. |
| `a5` | `Não especificado` | Atributo 5 do equipamento. |
| `a6` | `Não especificado` | Atributo 6 do equipamento. |
| `uar` | `Não especificado` | UAR (Unit of Account) do equipamento. |
| `iduc` | `Não especificado` | IDUC (Unique Document Code) do equipamento. |
| `sitcont` | `Não especificado` | Situação contábil do equipamento. |
| `dat_imo` | `Não especificado` | Data de imobilização do equipamento. |
| `conj` | `Não especificado` | Conjunto ao qual o equipamento pertence. |
| `qtd` | `Não especificado` | Coluna de contagem retornada na consulta. Valor padrão é 'COUNT(*)'. |

### Retorno

**Tipo:** `Não especificado`

String SQL gerada.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def sel_eq(
                                    tipo,
                                    sub,
                                    cod,
                                    descr,
                                    odi,
                                    ti,
                                    tuc,
                                    a1,
                                    a2,
                                    a3,
                                    a4,
                                    a5,
                                    a6,
                                    uar,
                                    iduc,
                                    sitcont,
                                    dat_imo,
                                    conj,
                                    qtd="COUNT(*)",
                                ):
                        return f"""
                                    SELECT
                                        '{tipo}'  AS TipoEquipamento,
                                        {sub}     AS Subestacao,
                                        {cod}     AS CodigoEquipamento,
                                        {descr}   AS DescricaoEquipamento,
                                        {odi}     AS ODI,
                                        {ti}      AS TI,
                                        {tuc}     AS TUC,
                                        {a1}      AS A1,
                                        {a2}      AS A2,
                                        {a3}      AS A3,
                                        {a4}      AS A4,
                                        {a5}      AS A5,
                                        {a6}      AS A6,
                                        {uar}     AS UAR,
                                        {iduc}    AS IDUC,
                                        {sitcont} AS SITCONT,
                                        {dat_imo} AS DAT_IMO,
                                        {conj}    AS CONJ,
                                        {qtd}     AS Qtd_BDGD
                                """
```

</details>

---

<a id="funcao-3"></a>

## formatar_grupo

Formata uma lista de colunas em uma única string separada por vírgulas e novas linhas.

Concatena os elementos de uma lista de strings, utilizando uma vírgula seguida por um espaço e uma nova linha como delimitador. Se a lista estiver vazia, retorna uma string vazia.

### Assinatura

```python
def formatar_grupo(cols):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cols` | `list[str]` | Lista de strings que serão concatenadas. |

### Retorno

**Tipo:** `str`

String formatada com os elementos da lista separados por vírgula e nova linha.

### Dependências

- `join`

<details>
<summary>Visualizar código-fonte</summary>

```python
def formatar_grupo(cols):
                        return ",\n            ".join(cols)
```

</details>

---

<a id="funcao-4"></a>

## cte_modelo

Gera uma consulta SQL para um modelo CTE (Common Table Expression).

Esta função cria uma consulta SQL que define um CTE com base em seleções, fontes e condições específicas. O resultado é uma string formatada que pode ser usada em consultas SQL mais complexas.

### Assinatura

```python
def cte_modelo(nome, select_sql, from_sql, where_sql, grupo_colunas):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `nome` | `Não especificado` | Nome do CTE a ser gerado. |
| `select_sql` | `Não especificado` | Parte da consulta SQL que especifica os campos a serem selecionados. |
| `from_sql` | `Não especificado` | Parte da consulta SQL que especifica a fonte dos dados. |
| `where_sql` | `Não especificado` | Parte da consulta SQL que define as condições de filtro. |
| `grupo_colunas` | `Não especificado` | Lista de colunas a serem usadas na cláusula GROUP BY. |

### Retorno

**Tipo:** `Não especificado`

String formatada representando o CTE SQL gerado.

### Dependências

- `{'nome': 'formatar_grupo', 'categoria': 'chamada', 'descricao': 'Função que formata a cláusula GROUP BY com base nas colunas fornecidas.'}`
- `{'nome': 'strip', 'categoria': 'chamada', 'descricao': 'Método de string que remove espaços em branco no início e no fim da string resultante.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def cte_modelo(nome, select_sql, from_sql, where_sql, grupo_colunas):
                        grupo_sql = formatar_grupo(grupo_colunas)
                        return f"""
                                    {nome} AS (
                                        {select_sql}
                                        {from_sql}
                                        {where_sql}
                                        GROUP BY
                                            {grupo_sql}
                                    )
                                    """.strip()
```

</details>

---

<a id="funcao-5"></a>

## tabela

Concatena um nome base com um sufixo.

A função concatena dois argumentos, um nome base e um sufixo, retornando a combinação deles como uma única string.

### Assinatura

```python
def tabela(nome_base, suf):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `nome_base` | `Não especificado` | O nome base que será concatenado. |
| `suf` | `Não especificado` | O sufixo que será adicionado ao nome base. |

### Retorno

**Tipo:** `Não especificado`

A string resultante da concatenação de `nome_base` e `suf`.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def tabela(nome_base, suf):
                        return f"{nome_base}{suf}"
```

</details>

---

<a id="funcao-6"></a>

## subquery_uniao

Cria uma subquery que une várias tabelas usando UNION ALL.

Concatena consultas SELECT de múltiplas tabelas em uma única consulta utilizando o operador UNION ALL. Cada tabela é selecionada para as colunas COD_ID, SUB, CONJ e GRU_TEN.

### Assinatura

```python
def subquery_uniao(tabelas_un):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `tabelas_un` | `Não especificado` | Lista de nomes das tabelas a serem unidas. |

### Retorno

**Tipo:** `Não especificado`

String contendo a consulta SQL resultante da união das tabelas.

### Dependências

- `join`

<details>
<summary>Visualizar código-fonte</summary>

```python
def subquery_uniao(tabelas_un):
                        return "\n            UNION ALL\n            ".join(
                            f"SELECT COD_ID, SUB, CONJ, GRU_TEN FROM {t}"
                            for t in tabelas_un
                        )
```

</details>

---

<a id="funcao-7"></a>

## cte_simples

Gera uma consulta SQL comum table expression (CTE) simplificada.

Esta função cria uma CTE a partir de uma tabela base, aplicando joins e filtros específicos. Utiliza funções auxiliares para gerar partes da consulta SQL.

### Assinatura

```python
# Consulte o código-fonte de cte_simples
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `nome` | `Não especificado` | Nome da CTE a ser gerada. |
| `tipo` | `Não especificado` | Tipo de consulta SQL a ser executado. |
| `tabela_base` | `Não especificado` | Nome da tabela base para a consulta. |
| `suf` | `Não especificado` | Sufixo opcional para a tabela base. |
| `join_sql` | `Não especificado` | SQL adicional para joins na consulta. |
| `where_sql` | `Não especificado` | Filtro WHERE adicionais para a consulta. |
| `conj_expr` | `Não especificado` | Expressão de conjunto para adicionar à consulta. |

### Retorno

**Tipo:** `Não especificado`

CTE gerada como resultado da função.

### Dependências

- `{'nome': 'cte_modelo', 'categoria': 'chamada', 'descricao': 'Função que gera a CTE final com os parâmetros fornecidos.'}`
- `{'nome': 'sel_eq', 'categoria': 'chamada', 'descricao': 'Função auxiliar para gerar parte da consulta SQL de seleção.'}`
- `{'nome': 'tabela', 'categoria': 'chamada', 'descricao': 'Função que retorna o nome completo da tabela, considerando o sufixo opcional.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def cte_simples(
                                            nome,
                                            tipo,
                                            tabela_base,
                                            suf,
                                            join_sql,
                                            where_sql,
                                            conj_expr,
                                        ):
                        select_sql = sel_eq(
                                            tipo=tipo,
                                            sub="S.COD_ID",
                                            cod="COALESCE(NULLIF(T1.UC_UG,''), S.COD_ID)",
                                            descr="T1.DESCR",
                                            odi="T1.ODI",
                                            ti="T1.TI",
                                            tuc="T1.TUC",
                                            a1="T1.A1",
                                            a2="T1.A2",
                                            a3="T1.A3",
                                            a4="T1.A4",
                                            a5="T1.A5",
                                            a6="T1.A6",
                                            uar="T1.UAR",
                                            iduc="T1.IDUC",
                                            sitcont="T1.SITCONT",
                                            dat_imo="T1.DAT_IMO",
                                            conj=conj_expr,
                                        )

                        from_sql = f"""
                                        FROM {tabela(tabela_base, suf)} T1
                                        {join_sql}
                                    """

                        grupo_cols = ["S.COD_ID", "UCG.COD_ID", *COLUNAS_T1, conj_expr]

                        return cte_modelo(
                                            nome=nome,
                                            select_sql=select_sql,
                                            from_sql=from_sql,
                                            where_sql=where_sql,
                                            grupo_colunas=grupo_cols,
                                        )
```

</details>

---

<a id="funcao-8"></a>

## sql_na

Retorna a string 'NA'.

A função retorna a string 'NA', que é frequentemente usada para representar valores ausentes ou não aplicáveis em dados tabulares.

### Assinatura

```python
def sql_na():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Retorno

**Tipo:** `str`

String contendo o valor 'NA'.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def sql_na():
                            return "'NA'"
```

</details>

---

<a id="funcao-9"></a>

## cte_bay

Gera uma consulta SQL comum table expression (CTE) para a tabela BAY.

A função cria uma CTE que combina dados da tabela BAY, SUB e BAR_odi_por_sub. Filtra os resultados onde a posição é 'PD'.

### Assinatura

```python
def cte_bay(suf):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `suf` | `Não especificado` | Sufixo utilizado para referenciar tabelas. |

### Retorno

**Tipo:** `Não especificado`

Objeto resultante da função cte_modelo com a consulta SQL gerada.

### Dependências

- `cte_modelo`
- `sel_eq`
- `sql_na`
- `tabela`

<details>
<summary>Visualizar código-fonte</summary>

```python
def cte_bay(suf):
                        bar_odi_por_sub = f"""
                                            SELECT
                                                SUB,
                                                ODI
                                            FROM {tabela("BAR", suf)}
                                        """
                        
                        select_sql = sel_eq(
                                                tipo="BAY",
                                                sub="S.COD_ID",
                                                cod="T1.COD_ID",
                                                descr="T1.DESCR",
                                                odi="R.ODI",
                                                ti=sql_na(),
                                                tuc=sql_na(),
                                                a1=sql_na(),
                                                a2=sql_na(),
                                                a3=sql_na(),
                                                a4=sql_na(),
                                                a5=sql_na(),
                                                a6=sql_na(),
                                                uar=sql_na(),
                                                iduc=sql_na(),
                                                sitcont=sql_na(),
                                                dat_imo=sql_na(),
                                                conj=sql_na(),
                                            )

                        from_sql = f"""
                                        FROM {tabela("BAY", suf)} T1
                                        LEFT JOIN {tabela("SUB", suf)} S
                                            ON T1.SUB = S.COD_ID
                                        LEFT JOIN (
                                            {bar_odi_por_sub}
                                        ) R
                                            ON R.SUB = T1.SUB
                                    """

                        where_sql = """
                                        WHERE T1.POS = 'PD'
                                    """

                        grupo_cols = [
                                            "S.COD_ID",
                                            "T1.COD_ID",
                                            "T1.DESCR",
                                            "R.ODI",
                                        ]

                        return cte_modelo(
                                            nome="BAY_SUB",
                                            select_sql=select_sql,
                                            from_sql=from_sql,
                                            where_sql=where_sql,
                                            grupo_colunas=grupo_cols,
                                        )
```

</details>

---

<a id="funcao-10"></a>

## cte_bar

Gera uma consulta CTE (Common Table Expression) para barramentos.

A função cria uma consulta CTE que seleciona dados de barramentos, filtrando por posição e realizando junções com outras tabelas. A consulta é personalizada com base em parâmetros específicos.

### Assinatura

```python
def cte_bar(suf):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `suf` | `Não especificado` | Sufixo utilizado para referenciar tabelas e colunas. |

### Retorno

**Tipo:** `Não especificado`

CTE gerada com os dados dos barramentos filtrados.

### Dependências

- `cte_modelo`
- `sel_eq`
- `sql_na`
- `tabela`

<details>
<summary>Visualizar código-fonte</summary>

```python
def cte_bar(suf):
                        select_sql = sel_eq(
                                                tipo="BARRAMENTO",
                                                sub="S.COD_ID",
                                                cod="T1.COD_ID",
                                                descr="T1.DESCR",
                                                odi="T1.ODI",
                                                ti="T1.TI",
                                                tuc="T1.TUC",
                                                a1="T1.A1",
                                                a2="T1.A2",
                                                a3="T1.A3",
                                                a4="T1.A4",
                                                a5="T1.A5",
                                                a6="T1.A6",
                                                uar="T1.UAR",
                                                iduc="T1.IDUC",
                                                sitcont="T1.SITCONT",
                                                dat_imo="T1.DAT_IMO",
                                                conj=sql_na(),
                                            )

                        from_sql = f"""
                                        FROM {tabela("BAR", suf)} T1
                                        LEFT JOIN {tabela("SUB", suf)} S
                                            ON T1.SUB = S.COD_ID
                                    """

                        where_sql = """
                                        WHERE T1.POS = 'PD'
                                    """

                        grupo_cols = [
                                            "S.COD_ID",
                                            *COLUNAS_T1,
                                        ]

                        return cte_modelo(
                                            nome="BAR_SUB",
                                            select_sql=select_sql,
                                            from_sql=from_sql,
                                            where_sql=where_sql,
                                            grupo_colunas=grupo_cols,
                                        )
```

</details>

---

<a id="funcao-11"></a>

## cte_eqtrm

Gera uma consulta SQL comuns table expressions (CTE) para a tabela EQTRM.

A função cria uma CTE chamada 'EQTRM_SUB' que realiza junções e filtra dados da tabela EQTRM com base em certas condições de instalação e situação do contrato. A função utiliza outras funções auxiliares para gerar partes específicas da consulta SQL.

### Assinatura

```python
def cte_eqtrm(suf):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `suf` | `Não especificado` | Sufixo utilizado na referência à tabela 'SUB' e em outras partes da consulta. |

### Retorno

**Tipo:** `Não especificado`

CTE SQL gerada como uma string.

### Dependências

- `{'nome': 'cte_simples', 'categoria': 'chamada', 'descricao': 'Função auxiliar que gera a CTE simples com os parâmetros fornecidos.'}`
- `{'nome': 'tabela', 'categoria': 'chamada', 'descricao': "Função auxiliar que retorna o nome da tabela 'SUB' com o sufixo especificado."}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def cte_eqtrm(suf):
                        join_sql = f"""
                                        LEFT JOIN {tabela("SUB", suf)} S
                                            ON T1.SUB = S.COD_ID
                                        LEFT JOIN UC_UNIFIC UCG
                                            ON T1.UC_UG = UCG.COD_ID
                                        AND UCG.GRU_TEN = T1.GRU_TEN
                                    """

                        where_sql = """
                                        WHERE T1.TIP_INST IN ('SE_MT', 'SE_AT')
                                        AND T1.SITCONT IN ('AT1', 'SF', 'RT')
                                    """

                        return cte_simples(
                                                nome="EQTRM_SUB",
                                                tipo="EQTRM",
                                                tabela_base="EQTRM",
                                                suf=suf,
                                                join_sql=join_sql,
                                                where_sql=where_sql,
                                                conj_expr="UCG.CONJ",
                                            )
```

</details>

---

<a id="funcao-12"></a>

## cte_eqtrmtmt

Gera uma consulta SQL comum table expression (CTE) para equipamentos de transformação MT-MT.

A função cria uma CTE que seleciona dados de equipamentos de transformação MT-MT, filtrando por tipos específicos e situações contábeis. A consulta é composta por partes SELECT, FROM e WHERE, e utiliza funções personalizadas para seleção dos dados.

### Assinatura

```python
def cte_eqtrmtmt():
```

### Parâmetros

Esta função não possui parâmetros documentados.

### Retorno

**Tipo:** `Não especificado`

CTE gerada como resultado da função.

### Dependências

- `cte_modelo`
- `sel_eq`

<details>
<summary>Visualizar código-fonte</summary>

```python
def cte_eqtrmtmt():
                        select_sql = sel_eq(
                                                tipo="TRAFO MT-MT",
                                                sub="S.COD_ID",
                                                cod="UNT.COD_ID",
                                                descr="T1.DESCR",
                                                odi="T1.ODI",
                                                ti="T1.TI",
                                                tuc="T1.TUC",
                                                a1="T1.A1",
                                                a2="T1.A2",
                                                a3="T1.A3",
                                                a4="T1.A4",
                                                a5="T1.A5",
                                                a6="T1.A6",
                                                uar="T1.UAR",
                                                iduc="T1.IDUC",
                                                sitcont="T1.SITCONT",
                                                dat_imo="T1.DAT_IMO",
                                                conj="UNT.CONJ",
                                            )

                        from_sql = """
                                        FROM EQTRMT_AT T1
                                        LEFT JOIN UNTRMT_AT UNT
                                            ON T1.UNI_TR_MT = UNT.COD_ID
                                        LEFT JOIN SUB_AT S
                                            ON UNT.SUB = S.COD_ID
                                    """

                        where_sql = """
                                        WHERE T1.TIP_INST IN ('SE_MT', 'SE_AT')
                                        AND T1.SITCONT IN ('AT1', 'SF', 'RT')
                                    """

                        grupo_cols = [
                                        "S.COD_ID",
                                        *COLUNAS_T1,
                                        "UNT.CONJ",
                                        "UNT.COD_ID",
                                    ]

                        return cte_modelo(
                                            nome="EQTRMTMT_SUB",
                                            select_sql=select_sql,
                                            from_sql=from_sql,
                                            where_sql=where_sql,
                                            grupo_colunas=grupo_cols,
                                        )
```

</details>

---

<a id="funcao-13"></a>

## cte_eqtrat

Gera uma consulta SQL comum table expression (CTE) para dados de equipamentos de transformação.

A função cria uma CTE que seleciona e filtra dados de equipamentos de transformação, utilizando tabelas relacionadas e condições específicas. A consulta é personalizada com base em parâmetros como tipo, subcategoria, código, descrição, etc., e retorna os resultados agrupados por várias colunas.

### Assinatura

```python
def cte_eqtrat(suf):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `suf` | `Não especificado` | Sufixo utilizado para referenciar a tabela principal. |

### Retorno

**Tipo:** `Não especificado`

CTE gerada com os dados filtrados e agrupados.

### Dependências

- `{'nome': 'cte_modelo', 'categoria': 'chamada'}`
- `{'nome': 'sel_eq', 'categoria': 'chamada'}`
- `{'nome': 'tabela', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def cte_eqtrat(suf):
                        select_sql = sel_eq(
                                                tipo="TRAFO AT-MT",
                                                sub="S.COD_ID",
                                                cod="UNT.COD_ID",
                                                descr="T1.DESCR",
                                                odi="T1.ODI",
                                                ti="T1.TI",
                                                tuc="T1.TUC",
                                                a1="T1.A1",
                                                a2="T1.A2",
                                                a3="T1.A3",
                                                a4="T1.A4",
                                                a5="T1.A5",
                                                a6="T1.A6",
                                                uar="T1.UAR",
                                                iduc="T1.IDUC",
                                                sitcont="T1.SITCONT",
                                                dat_imo="T1.DAT_IMO",
                                                conj="UNT.CONJ",
                                            )

                        from_sql = f"""
                                        FROM {tabela("EQTRAT", suf)} T1
                                        LEFT JOIN UNTRAT_AT UNT
                                            ON T1.UNI_TR_AT = UNT.COD_ID
                                        LEFT JOIN SUB_AT S
                                            ON UNT.SUB = S.COD_ID
                                    """

                        where_sql = """
                                        WHERE T1.TIP_INST IN ('SE_MT', 'SE_AT')
                                        AND T1.SITCONT IN ('AT1', 'SF', 'RT')
                                    """

                        grupo_cols = [
                                        "S.COD_ID",
                                        *COLUNAS_T1,
                                        "UNT.CONJ",
                                        "UNT.COD_ID",
                                    ]

                        return cte_modelo(
                                            nome="EQTRAT_SUB",
                                            select_sql=select_sql,
                                            from_sql=from_sql,
                                            where_sql=where_sql,
                                            grupo_colunas=grupo_cols,
                                        )
```

</details>

---

<a id="funcao-14"></a>

## cte_unificado

Gera uma consulta SQL CTE (Common Table Expression) unificada.

A função cria uma consulta SQL CTE com base em várias tabelas e condições específicas. Ela utiliza funções auxiliares para gerar partes da consulta, como a seleção de colunas, o join entre tabelas e as cláusulas WHERE.

### Assinatura

```python
def cte_unificado(nome_cte, tabela_eq, campo_join, tabelas_un, suf):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `nome_cte` | `Não especificado` | Nome do CTE que será gerado. |
| `tabela_eq` | `Não especificado` | Tabela principal utilizada na consulta. |
| `campo_join` | `Não especificado` | Campo utilizado para o join entre a tabela principal e as tabelas unificadas. |
| `tabelas_un` | `Não especificado` | Lista de tabelas que serão unidas à consulta principal. |
| `suf` | `Não especificado` | Sufixo utilizado para referenciar as tabelas. |

### Retorno

**Tipo:** `Não especificado`

Consulta SQL CTE gerada como uma string.

### Dependências

- `{'nome': 'cte_modelo', 'categoria': 'chamada'}`
- `{'nome': 'sel_eq', 'categoria': 'chamada'}`
- `{'nome': 'subquery_uniao', 'categoria': 'chamada'}`
- `{'nome': 'tabela', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def cte_unificado(nome_cte, tabela_eq, campo_join, tabelas_un, suf):
                        if not tabelas_un:
                            return ""

                        select_sql = sel_eq(
                                            tipo=nome_cte.replace("_UNS", ""),
                                            sub="S.COD_ID",
                                            cod="UNT.COD_ID",
                                            descr="T1.DESCR",
                                            odi="T1.ODI",
                                            ti="T1.TI",
                                            tuc="T1.TUC",
                                            a1="T1.A1",
                                            a2="T1.A2",
                                            a3="T1.A3",
                                            a4="T1.A4",
                                            a5="T1.A5",
                                            a6="T1.A6",
                                            uar="T1.UAR",
                                            iduc="T1.IDUC",
                                            sitcont="T1.SITCONT",
                                            dat_imo="T1.DAT_IMO",
                                            conj="UNT.CONJ",
                                        )

                        from_sql = f"""
                                        FROM {tabela(tabela_eq, suf)} T1
                                        LEFT JOIN (
                                            {subquery_uniao(tabelas_un)}
                                        ) UNT
                                            ON T1.{campo_join} = UNT.COD_ID
                                        AND T1.GRU_TEN = UNT.GRU_TEN
                                        LEFT JOIN {tabela("SUB", suf)} S
                                            ON UNT.SUB = S.COD_ID
                                    """

                        where_sql = """
                                        WHERE T1.TIP_INST IN ('SE_MT', 'SE_AT')
                                        AND T1.SITCONT IN ('AT1', 'SF', 'RT')
                                    """

                        grupo_cols = [
                                        "S.COD_ID",
                                        *COLUNAS_T1,
                                        "UNT.CONJ",
                                        "UNT.COD_ID",
                                    ]

                        return cte_modelo(
                                            nome=nome_cte,
                                            select_sql=select_sql,
                                            from_sql=from_sql,
                                            where_sql=where_sql,
                                            grupo_colunas=grupo_cols,
                                        )
```

</details>

---

<a id="funcao-15"></a>

## sql_final

Gera uma consulta SQL final a partir de múltiplas CTEs (Common Table Expressions).

A função combina várias CTEs em uma única consulta SQL utilizando UNION ALL, e retorna essa consulta formatada como uma string.

### Assinatura

```python
def sql_final(ctes):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ctes` | `Não especificado` | Lista de nomes das CTEs que serão combinadas. |

### Retorno

**Tipo:** `Não especificado`

String contendo a consulta SQL final formatada.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def sql_final(ctes):
                        cols = ", ".join(ESQUEMA_EQ)

                        union_sql = "\nUNION ALL\n".join(
                                                            f"SELECT {cols} FROM {cte}"
                                                            for cte in ctes
                                                        )
                        cte_p1 = ",\n".join(ctes_sql)
                        return f"""
                                    WITH
                                    {cte_p1}

                                    SELECT
                                        {cols}
                                    FROM (
                                        {union_sql}
                                    ) BASE
                                    ;
                                """.strip()
```

</details>

---

<a id="funcao-16"></a>

## unidades_existentes

Filtra tabelas existentes com base em prefixos e sufixo.

Esta função filtra uma lista de tabelas existentes, retornando apenas aquelas que correspondem a um determinado padrão formado por prefixos e sufixo.

### Assinatura

```python
def unidades_existentes(prefixos, suf, tabelas_existentes):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `prefixos` | `Não especificado` | Lista de prefixos utilizados para formar o padrão. |
| `suf` | `Não especificado` | Sufixo utilizado para formar o padrão. |
| `tabelas_existentes` | `Não especificado` | Lista de tabelas existentes que serão filtradas. |

### Retorno

**Tipo:** `Não especificado`

Lista de tabelas existentes que correspondem ao padrão formado por prefixos e sufixo.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def unidades_existentes(prefixos, suf, tabelas_existentes):
                        tabs = [f"{p}{suf}" for p in prefixos]
                        return [t for t in tabs if t in tabelas_existentes]
```

</details>

---

<a id="funcao-17"></a>

## uniao_unidades

Cria uma string SQL que une várias tabelas usando UNION ALL.

Concatena consultas SELECT de múltiplas tabelas em uma única consulta utilizando o operador UNION ALL. Cada tabela é selecionada para as colunas COD_ID, SUB, CONJ e GRU_TEN.

### Assinatura

```python
def uniao_unidades(tabs):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `tabs` | `Não especificado` | Lista de nomes das tabelas a serem unidas. |

### Retorno

**Tipo:** `Não especificado`

String SQL resultante da união das consultas SELECT.

### Dependências

- `join`

<details>
<summary>Visualizar código-fonte</summary>

```python
def uniao_unidades(tabs):
                        return " UNION ALL ".join(
                            f"SELECT COD_ID, SUB, CONJ, GRU_TEN FROM {t}"
                            for t in tabs
                        )
```

</details>

---
