import os, re, concurrent.futures, time, tempfile, uuid, glob
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import pandas as pd
from pandas.tseries.offsets import DateOffset
import numpy as np
import UTILS.sqlfnc as sql
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
from xlsxwriter.utility import xl_col_to_name
import locale, duckdb, json
from RELATORIOS.imprimir_xlsx import imprime_lado_AvsB, imprimi_F0_ABT, imprimi_F1_ABT
from SRC.calculos import conv_num
from pandas.tseries.offsets import MonthEnd
import sqlite3 as sl
from math import isnan, ceil, log
from scipy.stats import binom, hypergeom
from UTILS import monitor_completo  
import streamlit as st, chardet
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans, KMeans
from sklearn.metrics import silhouette_score
from sklearn.ensemble import IsolationForest
import matplotlib.ticker as mtick
import seaborn as sns
from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap
from MANIFESTO import (
                        registrar_artefato,
                        registrar_evento
                      )
from UTILS import (bsc_dados_reg)

@st.fragment()
def _vis_001(ROA_NG = pd.DataFrame(), st = None, COR_OK="#2eee34", COR_WARN = "#fcc72a",
            COR_CRIT = "#b60101"):
    if ROA_NG.empty:
        return
    return

@monitor_completo(st.session_state.LOGGER)
def limpar_arq(origem = None, st = None):
    if origem == None:
        return
    
    def limpar_linha(linha):
        return re.sub(r"[^\x20-\x7E\n\t]", "", linha)
    
    with open(origem, "rb") as f:
        raw = f.read(500000)
        enc = chardet.detect(raw)["encoding"] or "latin-1"

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8")
    with open(origem, "r", encoding=enc, errors="ignore") as fin:
        for linha in fin:
            temp.write(limpar_linha(linha))
    temp.close()
    return temp.name

@monitor_completo(st.session_state.LOGGER)
def rac_st(x1 = False, CNTR="CRIAR", st = None, bd = None):
    if 'tra_dir' in st.session_state:
        local = st.session_state.tra_dir
        empresa = st.session_state.nm_empr
        ano = st.session_state.dt_fim.year

        if not bd:
            bd = sl.connect(f'{local}\BD_LOCAL\{empresa}_{ano}.db')

        Dt_ARQ = sql.max_arq('ROA', bd, empresa=empresa)
        if Dt_ARQ:
            df_DEC = pd.read_sql_query("SELECT * FROM ROA WHERE dt_ARQ = ? LIMIT 1", bd, params=(Dt_ARQ,))
            if 'FLG_DIR' in df_DEC.columns:
                txt_ax = 't1.FLG_DIR, '
            else:
                txt_ax = ''
            
            if st:
                progresso = st.progress(0, "Iniciando avaliação de serviços versus materiais")
            if CNTR !="CRIAR":
                if st: 
                    st.divider()
                    st.markdown(f"""<h2 style="text-align: center;font-size: 30px;">
                                    Resultado do processamento</h2>
                                    """,  
                                    unsafe_allow_html = True)
                        
                    st.divider()
                    st.markdown("""
                                <p  style="text-align: justify;text-indent: 40px">Estão sendo apresentados os valores remanescentes 
                                (VL_AJUSTADO), o valor do ajuste (VL_AJUSTE) e o valor total da obra, discriminados por tipo de 
                                ajuste (Txt_DESCR_SFF) dentro de cada natureza de gasto (Cd_NG). É uma representação que decorre da avaliação das listas
                                de materiais e de serviços. Essa estrutura permite identificar a parcela mantida capitalizada, daquela 
                                reclassificada como despesa, bem como o montante consolidado por obra (VL_OBRA) e participação do item 
                                (Pct_OBRA) sobre o valor total dos investimentos no projeto.</p>""", unsafe_allow_html = True)

            arquivo_roa = [
                                os.path.join(rf"{local}\DADOS_BRUTOS_MANUAL", f)
                                for f in os.listdir(rf"{local}\DADOS_BRUTOS_MANUAL")
                                if f.lower().endswith('.csv') and (f.lower()[:4]=="roa_")
                            ]
            arquivo_ros = [
                                os.path.join(rf"{local}\DADOS_BRUTOS_MANUAL", f)
                                for f in os.listdir(rf"{local}\DADOS_BRUTOS_MANUAL")
                                if f.lower().endswith('.csv') and (f.lower()[:4]=="ros_") and (f.lower()[:5]!="ros_v") and (f.lower()[:5]!="ros_a")
                            ]
            arquivo_LS = [
                                os.path.join(f"{local}\AIS_ANLS", f)
                                for f in os.listdir(f"{local}/AIS_ANLS")
                                if f.lower().endswith('.csv') and (f.lower()[:10]=="lst_ser_aj")
                            ]
            arquivo_LM = [
                                os.path.join(f"{local}\AIS_ANLS", f)
                                for f in os.listdir(f"{local}/AIS_ANLS")
                                if f.lower().endswith('.csv') and (f.lower()[:10]=="lst_mat_aj")
                            ]

            if st: progresso.progress(2, "Limpando caracteres inválidos nos arquivos")
            for n in [arquivo_roa,arquivo_ros,arquivo_LS,arquivo_LM]:
                caminho = n[0]
                barra = caminho.rfind("\\")
                sql.sanear_csv(
                                    diretorio = caminho[:barra],
                                    arq = caminho[barra+1:] , st = st                                  
                                )

            if CNTR !="CRIAR":
                if st: 
                    st.divider()
                    cols = st.columns(5,gap='small')
                    with cols[2]:
                        x1 = st.button("(Re)Fazer", help = "Caso queira refazer os cálculos, basta pressionar este botão.", key="btn2")
                    st.divider()

            if len(arquivo_roa):
                if st: progresso.progress(20, "Gerando arquivo ROA completo")
                if (not os.path.exists(f'{local}/AIS_ANLS/ROA_AUG_{empresa}.csv')) or x1:      
                    con = duckdb.connect()
                    erro = {}
                    sucesso = False
                    for enc in ['CP1252', 'latin-1', 'utf-8']:
                        
                        try:    
                            sSQL = f"""
                                COPY (
                                        WITH
                                        roa_base AS (
                                            SELECT *
                                            FROM read_csv_auto('{arquivo_roa[0]}',
                                                delim='|',
                                                null_padding=true,
                                                encoding='{enc}',
                                                parallel=true,
                                                all_varchar=true
                                            )
                                        ),

                                        ls_norm AS (
                                            SELECT *
                                            FROM (
                                                SELECT *,
                                                    ROW_NUMBER() OVER (
                                                        PARTITION BY Nr_TI, COD_ITEM
                                                        ORDER BY Nr_TI
                                                    ) AS rn
                                                FROM read_csv_auto('{arquivo_LS[0]}',
                                                    delim='|',
                                                    null_padding=true,
                                                    encoding='{enc}',
                                                    parallel=true,
                                                    all_varchar=true
                                                )
                                                WHERE Nr_TI IS NOT NULL
                                                AND NULLIF(TRIM(CAST(Nr_TI AS VARCHAR)), '') IS NOT NULL
                                                AND TRY_CAST(Nr_TI AS INT64) IS NOT NULL
                                            )
                                            WHERE rn = 1
                                        ),

                                        lm_norm AS (
                                            SELECT *
                                            FROM (
                                                SELECT *,
                                                    ROW_NUMBER() OVER (
                                                        PARTITION BY Nr_TI, COD_ITEM
                                                        ORDER BY Nr_TI
                                                    ) AS rn
                                                FROM read_csv_auto('{arquivo_LM[0]}',
                                                    delim='|',
                                                    null_padding=true,
                                                    encoding='{enc}',
                                                    parallel=true,
                                                    all_varchar=true
                                                )
                                                WHERE Nr_TI IS NOT NULL
                                                AND NULLIF(TRIM(CAST(Nr_TI AS VARCHAR)), '') IS NOT NULL
                                                AND TRY_CAST(Nr_TI AS INT64) IS NOT NULL
                                            )
                                            WHERE rn = 1
                                        ),

                                        ros AS (
                                            SELECT *
                                            FROM read_csv_auto('{arquivo_ros[0]}',
                                                delim='|',
                                                null_padding=true,
                                                encoding='{enc}',
                                                parallel=true,
                                                all_varchar=true
                                            )
                                        ),

                                        roa_final AS (
                                            SELECT
                                                t1.Ide_RO_Analitico,
                                                t1.Cd_ODI,
                                                t1.Cd_SubODI,
                                                t1.Cd_Cls_Custo,
                                                CAST(t1.COD_ITEM AS VARCHAR) AS COD_ITEM,

                                                CASE
                                                    WHEN CAST(t1.Cd_NG AS VARCHAR) IN ('1','2') THEN COALESCE(t3.DESCR_ITEM, '')
                                                    WHEN CAST(t1.Cd_NG AS VARCHAR) = '4' THEN COALESCE(t2.DESCR_ITEM, '')
                                                    ELSE ''
                                                END AS DESCR_ITEM,

                                                t1.Cd_NG,
                                                t1.Cd_CA,
                                                t1.FLG_PLPT,

                                                CASE
                                                    WHEN ABS(REPLACE(COALESCE(NULLIF(TRIM(t1.Qtd), ''), '0'), ',', '.')::DOUBLE) < 0.001
                                                    THEN 0
                                                    ELSE REPLACE(COALESCE(NULLIF(TRIM(t1.Qtd), ''), '0'), ',', '.')::DOUBLE
                                                END AS Qtd,

                                                t1.Unidade,

                                                CASE
                                                    WHEN ABS(REPLACE(t1.VL_tot, ',', '.')::DOUBLE) < 0.001
                                                    THEN 0
                                                    ELSE REPLACE(t1.VL_tot, ',', '.')::DOUBLE
                                                END AS VL_tot,

                                                CAST(t1.Dt_Lcmto AS DATE) AS Dt_Lcmto,
                                                t1.Cd_Pedido,
                                                t1.Txt_Doc,
                                                t1.Nr_TI,
                                                t1.Nr_TUC,
                                                t1.Nr_A1,
                                                t1.Nr_A2,
                                                t1.Nr_A3,
                                                t1.Nr_A4,
                                                t1.Nr_A5,
                                                t1.Nr_A6,
                                                t1.Txt_Nom_Forn,
                                                t1.Nr_NF,
                                                t1.Nr_ItemNF,
                                                t1.Nr_SerieNF,
                                                t1.CNPJ_Forn,
                                                t1.FLG_DOA_OE,
                                                t1.FLG_INCOR_OE,
                                                t1.Cd_ATIP,
                                                {txt_ax}
                                                t2.Txt_Class,
                                                t2.Txt_Desc,

                                                CASE
                                                    WHEN CAST(t1.Cd_NG AS VARCHAR) = '4' THEN
                                                        CASE WHEN t4.Cd_Tipo_Obra IN ('3','7','12')
                                                            THEN REPLACE(COALESCE(t2.Vl_Default_Man, '1'), ',', '.')::DOUBLE
                                                            ELSE REPLACE(COALESCE(t2.Vl_Default_Inv, '1'), ',', '.')::DOUBLE
                                                        END
                                                    WHEN CAST(t1.Cd_NG AS VARCHAR) IN ('1','2') THEN
                                                        CASE WHEN t4.Cd_Tipo_Obra IN ('3','7','12')
                                                            THEN REPLACE(COALESCE(t3.Vl_Default_Man, '1'), ',', '.')::DOUBLE
                                                            ELSE REPLACE(COALESCE(t3.Vl_Default_Inv, '1'), ',', '.')::DOUBLE
                                                        END
                                                    ELSE 1
                                                END AS Vl_Default,

                                                CASE
                                                    WHEN CAST(t1.Cd_NG AS VARCHAR) = '4' THEN COALESCE(t2.Txt_OBS_SFF, '')
                                                    WHEN CAST(t1.Cd_NG AS VARCHAR) IN ('1','2') THEN COALESCE(t3.Txt_OBS_SFF, '')
                                                    ELSE ''
                                                END AS Txt_OBS_SFF,

                                                CASE
                                                    WHEN CAST(t1.Cd_NG AS VARCHAR) = '4' THEN COALESCE(t2.CD_Nm_Reg_ST, '')
                                                    WHEN CAST(t1.Cd_NG AS VARCHAR) IN ('1','2') THEN COALESCE(t3.CD_Nm_Reg_ST, '')
                                                    ELSE ''
                                                END AS Cd_Nm_Reg

                                            FROM roa_base t1
                                            LEFT JOIN ls_norm t2
                                                ON t1.Nr_TI = t2.Nr_TI
                                                AND CAST(t1.COD_ITEM AS VARCHAR) = CAST(t2.COD_ITEM AS VARCHAR)
                                            LEFT JOIN lm_norm t3
                                                ON t1.Nr_TI = t3.Nr_TI
                                                AND CAST(t1.COD_ITEM AS VARCHAR) = CAST(t3.COD_ITEM AS VARCHAR)
                                            LEFT JOIN ros t4
                                                ON t1.Cd_SubODI = t4.Cd_SubODI
                                        )

                                        SELECT *
                                        FROM roa_final
                                        ORDER BY Cd_SubODI, Ide_RO_Analitico
                                        )
                                        TO '{local}/AIS_ANLS/ROA_AUG_{empresa}.csv'
                                        (FORMAT CSV, HEADER, DELIMITER '|');

                            """
                            con.execute(sSQL)
                            sucesso = True
                            if st:
                                registrar_artefato(st.session_state.database_MAN, 
                                                    st.session_state.execucao_id, 
                                                    file_path = rf'{local}/AIS_ANLS/ROA_AUG_{empresa}.csv',
                                                    tipo_artefato = "SAIDA", 
                                                    calcular_hash = True)
                            break
                        except Exception as e:
                            erro[enc] = e
                        if sucesso:
                            break
                
                if len(erro)>0:
                    if st: 
                        st.text(erro)
                        registrar_evento(st.session_state.database_MAN, 
                                        st.session_state.execucao_id, 
                                        nome_evento = 'racionalizacao_servicos',
                                        mensagem = f'Falhou na consolidação do ROA.', 
                                        nivel = 'ERRO',
                                        detalhes = {'erro' : "Encodings incorretos"})
                    raise UserWarning("Você tem problema de codificação do arquivo.")

                if st: progresso.progress(40, "Iniciando racionalização...")
                df = pd.DataFrame()
                con = duckdb.connect()
                for fim_linha in [r"\r\n",r"\n",r"\r"]: 
                    try:   
                        sSQL = f"""
                                    WITH roa AS (
                                    SELECT
                                        Cd_SubODI,
                                        'NG_' || Cd_NG AS Cd_NG,
                                        COALESCE(REPLACE(REPLACE(Txt_OBS_SFF, 'ok', 'ND'), 'OK', 'ND'),'ND') AS Txt_OBS_SFF,
                                        SUM(COALESCE(VL_tot,0) * COALESCE(Vl_Default,1)) AS Soma_Valor,
                                        SUM(COALESCE(VL_tot,0) * (1-COALESCE(Vl_Default,1))) AS Soma_Valor_AJST
                                    FROM
                                        read_csv('{local}/AIS_ANLS/ROA_AUG_{empresa}.csv',
                                                    delim='|',
                                                    header=true,
                                                    quote='"',
                                                    escape='"', 
                                                    sample_size=-1,
                                                    strict_mode=false,
                                                    null_padding=true,
                                                    new_line='{fim_linha}')
                                    /*WHERE Nr_TI not in ('70','71','72','80','81','82','90','91','94','95','97','99',
                                                        70,71,72,80,81,82,90,91,94,95,97,99)*/
                                    GROUP BY
                                        Cd_SubODI,
                                        Cd_NG,
                                        Txt_OBS_SFF
                                    ORDER BY
                                        Cd_SubODI,
                                        Cd_NG,
                                        Txt_OBS_SFF
                                    ),
                                    totais AS (
                                    SELECT
                                        Cd_SubODI,
                                        SUM(Soma_Valor) + SUM(Soma_Valor_AJST) AS Total
                                    FROM
                                        roa
                                    GROUP BY
                                        Cd_SubODI
                                    ),
                                    base AS (
                                    SELECT
                                        t1.Cd_SubODI,
                                        Cd_NG,
                                        Txt_OBS_SFF,
                                        Soma_Valor AS VL_AJUSTADO,
                                        Soma_Valor_AJST AS VL_AJUSTE,
                                        (Soma_Valor+Soma_Valor_AJST)/Total AS Pct_OBRA,
                                        Total VL_OBRA
                                    FROM
                                        roa t1 left join totais t2
                                        on t1.Cd_SubODI = t2.Cd_SubODI
                                    ORDER BY
                                        t1.Cd_SubODI,
                                        Cd_NG,
                                        Txt_OBS_SFF
                                    )
                                    select * from base
                                    """
                        df = con.execute(sSQL).fetchdf()
                        break
                    except Exception as e:
                        if st: 
                            st.warning(f"{e}")
                        else:
                            print(f"{e}")
                
                if len(df)==0:
                    raise UserWarning("Problemas na leitura do ROA_AUG")
                df_TOT = df[df['Cd_NG']=='NG_1'].groupby('Cd_SubODI',dropna = False)[['VL_AJUSTADO','VL_AJUSTE']].sum().reset_index()
                df_TOT['TOTAL_NG_1'] = df_TOT['VL_AJUSTADO'] + df_TOT['VL_AJUSTE']
                df = df.merge(df_TOT[['Cd_SubODI','TOTAL_NG_1']], on = 'Cd_SubODI', how = 'left')
                df['Pct_UC_PROJ'] = df['TOTAL_NG_1'] / df['VL_OBRA']

                df_TOT = df[df['Cd_NG']=='NG_2'].groupby('Cd_SubODI',dropna = False)[['VL_AJUSTADO','VL_AJUSTE']].sum().reset_index()
                df_TOT['TOTAL_NG_2'] = df_TOT['VL_AJUSTADO'] + df_TOT['VL_AJUSTE']
                df = df.merge(df_TOT[['Cd_SubODI','TOTAL_NG_2']], on = 'Cd_SubODI', how = 'left')
                df['Pct_COM_PROJ'] = df['TOTAL_NG_2'] / df['VL_OBRA']

                df_PROV = df[df.columns.to_list()[:7]].copy()
                for n in df_PROV.columns.to_list():
                    if n[:2].upper() == 'VL':
                        df_PROV[n] = df_PROV[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    elif n[:2].upper() == 'PC':
                        df_PROV[n] = df_PROV[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                if CNTR !="CRIAR":
                    if st: 
                        st.dataframe(df_PROV, width='content', hide_index=True)
                    else:
                        print(df_PROV)

                df_AX = df[['Cd_SubODI', 'TOTAL_NG_1', 'TOTAL_NG_2', 'Pct_UC_PROJ', 'Pct_COM_PROJ']].drop_duplicates()
                df_TOT = df.groupby('Cd_SubODI',dropna = False)[['VL_AJUSTADO','VL_AJUSTE']].sum().reset_index()
                df_TOT = df_TOT.merge(df_AX, how='left', on = 'Cd_SubODI')
                df_TOT['OBS_SFF_TP_PROJ'] = "NO"
                df_TOT.loc[(df_TOT['Pct_UC_PROJ'] < 0.05), 'OBS_SFF_TP_PROJ'] = "OBRA DE MANUTENÇÃO"
                df_TOT.loc[(df_TOT['Pct_UC_PROJ'] < 0.05) & (df_TOT['Pct_COM_PROJ'] > 0.1), 'OBS_SFF_TP_PROJ'] = "OBRA PARECE SER DE MANUTENÇÃO, DEVIDO AOS GRANDES CUSTOS DE COM"
                df_TOT.loc[(df_TOT['Pct_UC_PROJ'] < 0.05) & (df_TOT['Pct_COM_PROJ'] < 0.05), 'OBS_SFF_TP_PROJ'] = "OBRA PARECE SER DE MANUTENÇÃO, DEVIDO AOS GRANDES CUSTOS DE CA, RELATIVAMENTE AO TODO"
                
                df_TOT['VL_AJUSTADO_FINAL'] = 0  # valor padrão
                df_TOT.loc[df_TOT['OBS_SFF_TP_PROJ'] == 'NO', 'VL_AJUSTADO_FINAL'] = df_TOT['VL_AJUSTADO']

                df_TOT['VL_AJUSTE_FINAL'] = df_TOT['VL_AJUSTE']  # valor padrão
                df_TOT.loc[df_TOT['OBS_SFF_TP_PROJ'] != 'NO', 'VL_AJUSTE_FINAL'] = df_TOT['VL_AJUSTADO'] + df_TOT['VL_AJUSTE']
                
                df_PROV = df_TOT.copy()
                for n in df_PROV.columns.to_list():
                    if n[:2].upper() == 'VL':
                        df_PROV[n] = df_PROV[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    elif n[:2].upper() == 'PC':
                        df_PROV[n] = df_PROV[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))

                if st: progresso.progress(70, "Buscando dados do ROS...")
                df_PROV['Cd_SubODI'] = df_PROV['Cd_SubODI'].astype(str)
                if sql.existe_tabela('ROS', bd):
                    sSQL = """
                        SELECT Cd_SubODI,
                            Txt_Desc_PRJ,
                            CASE Cd_Tipo_Obra
                                WHEN 1 THEN 'Ampliação/Expansão'
                                WHEN 2 THEN 'Construção'
                                WHEN 3 THEN 'Manutenção'
                                WHEN 4 THEN 'Melhoria/Reforma'
                                WHEN 5 THEN 'Administrativo'
                                WHEN 6 THEN 'Incorporação'
                                WHEN 7 THEN 'Melhoria/Reforma'
                                WHEN 8 THEN 'PEE'
                                WHEN 9 THEN 'PED'
                                WHEN 10 THEN 'Manutenção'
                                WHEN 11 THEN 'Medição'
                                WHEN 12 THEN 'Medição'
                            END AS Txt_TP_OBRA,
                            CASE Cd_Tipo_Obra
                                WHEN 1 THEN 'Investimento'
                                WHEN 2 THEN 'Investimento'
                                WHEN 3 THEN 'Manutenção'
                                WHEN 4 THEN 'Investimento'
                                WHEN 5 THEN 'Investimento'
                                WHEN 6 THEN 'Investimento'
                                WHEN 7 THEN 'Manutenção'
                                WHEN 8 THEN 'Investimento'
                                WHEN 9 THEN 'Investimento'
                                WHEN 10 THEN 'Investimento'
                                WHEN 11 THEN 'Investimento'
                                WHEN 12 THEN 'Manutenção'
                            END AS Txt_CLS_OBRA,
                            Dt_Inic_Proj,
                            Dt_Energ,
                            Dt_Uniti,
                            Cd_ODD
                        FROM ROS

                    """
                    try:
                        ROS = pd.read_sql(sSQL, bd)
                    except:
                        sSQL = """
                                    SELECT Cd_SubODI,
                                        Txt_Desc_ODI AS Txt_Desc_PRJ,
                                        CASE Cd_Tipo_Obra
                                            WHEN 1 THEN 'Ampliação/Expansão'
                                            WHEN 2 THEN 'Construção'
                                            WHEN 3 THEN 'Manutenção'
                                            WHEN 4 THEN 'Melhoria/Reforma'
                                            WHEN 5 THEN 'Administrativo'
                                            WHEN 6 THEN 'Incorporação'
                                            WHEN 7 THEN 'Melhoria/Reforma'
                                            WHEN 8 THEN 'PEE'
                                            WHEN 9 THEN 'PED'
                                            WHEN 10 THEN 'Manutenção'
                                            WHEN 11 THEN 'Medição'
                                            WHEN 12 THEN 'Medição'
                                        END AS Txt_TP_OBRA,
                                        CASE Cd_Tipo_Obra
                                            WHEN 1 THEN 'Investimento'
                                            WHEN 2 THEN 'Investimento'
                                            WHEN 3 THEN 'Manutenção'
                                            WHEN 4 THEN 'Investimento'
                                            WHEN 5 THEN 'Investimento'
                                            WHEN 6 THEN 'Investimento'
                                            WHEN 7 THEN 'Manutenção'
                                            WHEN 8 THEN 'Investimento'
                                            WHEN 9 THEN 'Investimento'
                                            WHEN 10 THEN 'Investimento'
                                            WHEN 11 THEN 'Investimento'
                                            WHEN 12 THEN 'Manutenção'
                                        END AS Txt_CLS_OBRA,
                                        Dt_Inic_Proj,
                                        Dt_Energ,
                                        Dt_Uniti,
                                        Cd_ODD
                                    FROM ROS

                                """
                        ROS = pd.read_sql(sSQL, bd)
                    df_PROV = df_PROV.merge(ROS, how='left', on = 'Cd_SubODI')

                df_PROV.to_csv(f'{local}/AIS_ANLS/ANL_MANUTENCAO_LISTAS_{empresa}.csv', index=False, 
                                sep="|", decimal=',', encoding="Latin-1", header = True, chunksize=100_000)
                if st:
                    registrar_artefato(st.session_state.database_MAN, 
                                        st.session_state.execucao_id, 
                                        file_path = rf'{local}/AIS_ANLS/ANL_MANUTENCAO_LISTAS_{empresa}.csv',
                                        tipo_artefato = "SAIDA", 
                                        calcular_hash = True)
                            
                VTR = f"{df_TOT['VL_AJUSTADO_FINAL'] .sum():,.2f}".replace(",","x").replace(".",",").replace("x",".")
                VAST = f"{df_TOT['VL_AJUSTE_FINAL'] .sum():,.2f}".replace(",","x").replace(".",",").replace("x",".")
                filtro = df_TOT['OBS_SFF_TP_PROJ'] != 'NO'
                valor = (
                    df_TOT.loc[filtro, 'VL_AJUSTE_FINAL'].sum() +
                    df_TOT.loc[filtro, 'VL_AJUSTADO_FINAL'].sum()
                    )
                VMAN = f"{valor:,.2f}".replace(",", "x").replace(".", ",").replace("x", ".")
                if CNTR !="CRIAR":
                    st.divider()
                    st.markdown(f"""
                            <p  style="text-align: justify;text-indent: 40px">Agora vamos consolidar os dados, apontando os
                            valores de ajustes totais e observando se a obra é de manutenção (baixos valores para os ativos 
                            imobilizados no projeto). Caso não concorde com a classificação, apresentar o estudo definindo que
                            a obra deve ser capitalizada. Foram executados R$ {VAST} de ajuste por listas e obras consideradas como
                            de despesa, resultando num valor de R$ {VTR}. Do valor de ajuste, há R$ {VMAN}, que são
                            consideradas obras de manutenção indevidamente capitalizadas.</p>""", unsafe_allow_html = True)
                    st.dataframe(df_PROV, width='content', hide_index=True)

                progresso.progress(80, "Resumindo cálculo de racionalização...")
                con = duckdb.connect()    
                sSQL = f"""
                            WITH roa_ST AS (
                                SELECT
                                    Cd_SubODI,
                                    COALESCE(TRY_CAST(Cd_Nm_REG AS DOUBLE), 0) AS Cd_Nm_REG,
                                    GREATEST(
                                        0,
                                        SUM(COALESCE(CAST(VL_tot AS DOUBLE), 0))
                                    ) AS Soma_Valor,
                                    GREATEST(
                                        0,
                                        SUM(COALESCE(CAST(Qtd AS DOUBLE), 0))
                                    ) AS Soma_Qtd
                                FROM read_csv_auto(
                                        '{local}/AIS_ANLS/ROA_AUG_{empresa}.csv',
                                        delim='|',
                                        null_padding=true,
                                        parallel = true,
                                        all_varchar = true
                                    )
                                WHERE 
                                    Nr_TI NOT IN (70,71,72,80,81,82,90,91,94,95,97,99)
                                    AND CAST(Cd_NG AS VARCHAR) IN ('4')
                                GROUP BY
                                    Cd_SubODI,
                                    Cd_Nm_REG
                            ),

                            roa_MAT AS (
                                SELECT
                                    Cd_SubODI,
                                    COALESCE(TRY_CAST(Cd_Nm_REG AS DOUBLE), 0) AS Cd_Nm_REG,
                                    GREATEST(
                                        0,
                                        SUM(COALESCE(CAST(VL_tot AS DOUBLE), 0))
                                    ) AS Soma_Valor,
                                    GREATEST(
                                        0,
                                        SUM(COALESCE(CAST(Qtd AS DOUBLE), 0))
                                    ) AS Soma_Qtd
                                FROM read_csv_auto(
                                        '{local}/AIS_ANLS/ROA_AUG_{empresa}.csv',
                                        delim='|',
                                        null_padding=true,
                                        parallel = true,
                                        all_varchar = true
                                    )
                                WHERE 
                                    Nr_TI NOT IN (70,71,72,80,81,82,90,91,94,95,97,99)
                                    AND CAST(Cd_NG AS VARCHAR) IN ('1','2')
                                GROUP BY
                                    Cd_SubODI,
                                    Cd_Nm_REG
                            ),

                            totais AS (
                                SELECT 
                                    COALESCE(t1.Cd_SubODI, t2.Cd_SubODI) AS Cd_SubODI,
                                    COALESCE(CAST(t1.Cd_Nm_REG AS DOUBLE), CAST(t2.Cd_Nm_REG AS DOUBLE)) AS Cd_Nm_REG,
                                    COALESCE(t1.Soma_Qtd,   0) AS Qtd_ST,
                                    COALESCE(t2.Soma_Qtd,   0) AS Qtd_MAT,
                                    COALESCE(t1.Soma_Valor, 0) AS VL_ST,
                                    COALESCE(t2.Soma_Valor, 0) AS VL_MAT,

                                    CASE
                                        WHEN COALESCE(t1.Soma_Qtd, 0) > 0 
                                        THEN COALESCE(t1.Soma_Valor, 0) / COALESCE(t1.Soma_Qtd,  0)
                                        ELSE 0
                                    END AS VL_CMU_ST,

                                    CASE 
                                        WHEN (COALESCE(t1.Soma_Qtd, 0) - COALESCE(t2.Soma_Qtd,  0)) > 0
                                        THEN (COALESCE(t1.Soma_Qtd, 0) - COALESCE(t2.Soma_Qtd,  0))
                                        ELSE 0
                                    END AS Qdt_AJS
                                FROM
                                    roa_ST  t1
                                    FULL JOIN roa_MAT t2 
                                    ON  t1.Cd_SubODI = t2.Cd_SubODI
                                    AND t1.Cd_Nm_REG = t2.Cd_Nm_REG
                            )

                            SELECT * 
                            FROM totais
                            WHERE Cd_Nm_REG > 0
                            ORDER BY 
                                Cd_SubODI,
                                Cd_Nm_REG;
                            """

                df = con.execute(sSQL).fetchdf()
                df_PROV = df[df['Cd_Nm_REG'].notnull()].copy()
                df_PROV['VL_AJST'] = df_PROV['Qdt_AJS'] * df_PROV['VL_CMU_ST']
                vLAJ = f"{df_PROV['VL_AJST'] .sum():,.2f}".replace(",","x").replace(".",",").replace("x",".")
                df_PROV = df_PROV[df_PROV['VL_AJST'] != 0]
                
                mapa = {
                            1: "Condutor nu",
                            2: "Condutor Protegido",
                            3: "Banco de Capacitores",
                            4: "Chave Fusível",
                            5: "Chave Seccionadora",
                            6: "Chave Seccionadora Carga",
                            7: "Cruzeta",
                            8: "Haste de Aterramento",
                            9: "Isolador Disco",
                            10: "Isolador Pino",
                            11: "Para-raios",
                            12: "Pino",
                            13: "Poste",
                            14: "Regulador de Tensão",
                            15: "Religador Monofásico",
                            16: "Religador Trifásico",
                            17: "Seccionalizador de cerca",
                            18: "Seccionalizador Monofásico",
                            19: "Seccionalizador Trifásico",
                            20: "Torre",
                            21: "Transformador Distribuição Bifásico",
                            22: "Transformador Distribuição Monofásico",
                            23: "Transformador Distribuição Trifásico",
                            24: "Medidor",
                            25: "Transformador de Força",
                            26: "Transformador de Corrente",
                            27: "Transformador de Potencial",
                            28: "Disjuntor",
                            29: "Fibra Óptica",
                            30: "Ramal",
                            31: "Demais isoladores",
                            32: "Estrutura",
                            33: "Controle de Religador"
                        }
                df_PROV['Nm_EQP'] = df_PROV['Cd_Nm_REG'].map(mapa)
                df_PROV.to_csv(f'{local}/AIS_ANLS/RAC_ST_{empresa}.csv', index=False, 
                                sep="|", decimal=',', encoding="Latin-1", header = True, chunksize=100_000)
                if st:
                    registrar_artefato(st.session_state.database_MAN, 
                                        st.session_state.execucao_id, 
                                        file_path = rf'{local}/AIS_ANLS/RAC_ST_{empresa}.csv',
                                        tipo_artefato = "SAIDA", 
                                        calcular_hash = True)
                for n in df_PROV.columns.to_list():
                    if n[:2].upper() == 'VL':
                        df_PROV[n] = df_PROV[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    elif n[:2].upper() == 'PC':
                        df_PROV[n] = df_PROV[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))

                if CNTR !="CRIAR":
                    st.divider()
                    st.markdown(f"""
                            <p  style="text-align: justify;text-indent: 40px">Será realizado análise específica sempre que 
                            for identificada uma divergência entre a quantidade de serviços executados, medida em unidades 
                            de serviço, e a quantidade de materiais utilizados, de forma a garantir a coerência técnica 
                            entre os registros de execução e os de consumo de materiais, assegurando maior consistência 
                            nos dados e a adequada apuração dos investimentos apresentados. Dito isso, identificamos R$
                            {vLAJ} em possíveis ajustes.</p>""", unsafe_allow_html = True)
                    st.dataframe(df_PROV, width='content', hide_index=True)


                sSQL = f"""
                            WITH roa AS (
                                    SELECT
                                        *
                                    FROM
                                        read_csv_auto('{local}/AIS_ANLS/ROA_AUG_{empresa}.csv',
                                                    delim='|',
                                                    null_padding=true,
                                                    parallel = true,
                                                    all_varchar = true)
                                    WHERE 
                                        Nr_TI NOT IN ('70','71','72','80','81','82','90','91','94','95','97','99',
                                                    70,71,72,80,81,82,90,91,94,95,97,99)
                                    
                                ),
                                itens as (
                                    SELECT DISTINCT COD_ITEM 
                                    FROM roa WHERE Vl_Default != 1 or Vl_Default != '1'
                                ),
                                projetos as (
                                    SELECT DISTINCT Cd_SubODI
                                    FROM roa WHERE COD_ITEM IN (SELECT * FROM itens)
                                )
                                SELECT t1.* 
                                FROM roa t1 right join projetos t2 on t1.Cd_SubODI = t2.Cd_SubODI;
                            """
                df = con.execute(sSQL).fetchdf()
                
                df['Cd_SubODI'] = df['Cd_SubODI'].astype(str)
                ROS['Cd_SubODI'] = ROS['Cd_SubODI'].astype(str)

                df = df.merge(ROS, how = 'left', on = 'Cd_SubODI')

                if len(df)>0:
                    df.to_csv(f'{local}/AIS_ANLS/projetos_{empresa}.csv', index=False, 
                                    sep="|", decimal=',',  header = True, chunksize=100_000)
                    if st:
                        registrar_artefato(st.session_state.database_MAN, 
                                            st.session_state.execucao_id, 
                                            file_path = rf'{local}/AIS_ANLS/projetos_{empresa}.csv',
                                            tipo_artefato = "SAIDA", 
                                            calcular_hash = True)
                    df_PROV = df.copy()

                    for n in df_PROV.columns.to_list():
                        if (df_PROV[n].dtype == 'object') and (n[:2].upper() == 'VL'):
                            df_PROV[n] = df_PROV[n].fillna("0")
                            df_PROV[n] = df_PROV[n].apply(lambda x: f"{float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                        elif (df_PROV[n].dtype == 'object') and (n[:2].upper() == 'PC'):
                            df_PROV[n] = df_PROV[n].fillna("0")
                            df_PROV[n] = df_PROV[n].apply(lambda x: f"{float(x):,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
                    
                    if CNTR !="CRIAR":
                        st.divider()
                        st.markdown(f"""<h2 style="text-align: center;font-size: 30px;">
                            Resultado da Racionalização de Serviços</h2>
                                <p  style="text-align: justify;text-indent: 40px">Segue lista de projetos que foram ajustados pelas 
                                    listas de materiais e de serviços, primeiros 200 registros.</p>""", unsafe_allow_html = True)
                        st.dataframe(df_PROV.head(200), width='content', hide_index=True)
                progresso.progress(95, "Salvando...")
                sSQL = f"""
                            COPY (
                                WITH roa_ST AS (
                                    SELECT
                                        CAST(Cd_SubODI AS VARCHAR) AS Cd_SubODI,
                                        COALESCE(TRY_CAST(Cd_Nm_REG AS DOUBLE), 0) AS Cd_Nm_REG,
                                        GREATEST(
                                            0,
                                            SUM(
                                                COALESCE(
                                                    CAST(
                                                        REGEXP_REPLACE(
                                                            CAST(VL_tot AS VARCHAR),
                                                            '[^0-9.-Ee]',
                                                            ''
                                                        ) AS DOUBLE
                                                    ),
                                                    0
                                                )
                                            )
                                        ) AS Soma_Valor,

                                        GREATEST(
                                            0,
                                            SUM(
                                                COALESCE(
                                                    CAST(
                                                        REGEXP_REPLACE(
                                                            CAST(Qtd AS VARCHAR),
                                                            '[^0-9.-Ee]',
                                                            ''
                                                        ) AS DOUBLE
                                                    ),
                                                    0
                                                )
                                            )
                                        ) AS Soma_Qtd

                                    FROM read_csv_auto('{local}/AIS_ANLS/ROA_AUG_{empresa}.csv',
                                                    delim='|',
                                                    null_padding=true,
                                                    parallel = true,
                                                    all_varchar = true)

                                    WHERE 
                                        Nr_TI NOT IN (70,71,72,80,81,82,90,91,94,95,97,99)
                                        AND CAST(
                                            REGEXP_REPLACE(
                                                CAST(Cd_NG AS VARCHAR),
                                                '[^0-9.-Ee]',
                                                ''
                                            ) AS INTEGER
                                        ) = 4

                                    GROUP BY
                                        Cd_SubODI,
                                        Cd_Nm_REG
                                ),

                                roa_MAT AS (
                                    SELECT
                                        CAST(Cd_SubODI AS VARCHAR) AS Cd_SubODI,
                                        COALESCE(TRY_CAST(Cd_Nm_REG AS DOUBLE), 0) AS Cd_Nm_REG,
                                        GREATEST(
                                            0,
                                            SUM(
                                                COALESCE(
                                                    CAST(
                                                        REGEXP_REPLACE(
                                                            CAST(VL_tot AS VARCHAR),
                                                            '[^0-9.-Ee]',
                                                            ''
                                                        ) AS DOUBLE
                                                    ),
                                                    0
                                                )
                                            )
                                        ) AS Soma_Valor,

                                        GREATEST(
                                            0,
                                            SUM(
                                                COALESCE(
                                                    CAST(
                                                        REGEXP_REPLACE(
                                                            CAST(Qtd AS VARCHAR),
                                                            '[^0-9.-Ee]',
                                                            ''
                                                        ) AS DOUBLE
                                                    ),
                                                    0
                                                )
                                            )
                                        ) AS Soma_Qtd

                                    FROM read_csv_auto('{local}/AIS_ANLS/ROA_AUG_{empresa}.csv',
                                                    delim='|', header=true,
                                                    all_varchar=true)

                                    WHERE 
                                        Nr_TI NOT IN (70,71,72,80,81,82,90,91,94,95,97,99)
                                        AND CAST(
                                            REGEXP_REPLACE(
                                                CAST(Cd_NG AS VARCHAR),
                                                '[^0-9.-Ee]',
                                                ''
                                            ) AS INTEGER
                                        ) IN (1,2)

                                    GROUP BY
                                        Cd_SubODI,
                                        Cd_Nm_REG
                                )

                                SELECT *
                                FROM roa_ST
                                FULL JOIN roa_MAT USING (Cd_SubODI, Cd_Nm_REG)

                            ) TO '{local}/AIS_ANLS/ROA_AJS_SERV_{empresa}.csv'
                            (FORMAT CSV, HEADER, DELIMITER '|');
                            """
                con.execute(sSQL)
                if st:
                    registrar_artefato(st.session_state.database_MAN, 
                                        st.session_state.execucao_id, 
                                        file_path = rf'{local}/AIS_ANLS/ROA_AJS_SERV_{empresa}.csv',
                                        tipo_artefato = "SAIDA", 
                                        calcular_hash = True)

                progresso.progress(100, "Finalizado")
            progresso.empty()
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def bsc_nr_amst(N=1, confianca=0.95, erro_aceitavel=0.05, erros_esperados=0):
    res = calcular_tamanho_amostra(
                                    N=N, 
                                    confianca=confianca, 
                                    erro_aceitavel=erro_aceitavel, 
                                    erros_esperados=erros_esperados
                                )
    risco = calcular_risco_amostral(
                                        n=res['tamanho_amostra'], 
                                        N=N, 
                                        erro_aceitavel=erro_aceitavel, 
                                        erros_esperados=erros_esperados
                                    )

    return res, risco

@monitor_completo(st.session_state.LOGGER)
def _calcular_binomial(alpha, erro_aceitavel, erros_esperados):
    """
    Calcula tamanho da amostra usando distribuição binomial
    """
    if erros_esperados == 0:
        # Fórmula simples para 0 erros esperados
        n = ceil(log(alpha) / log(1 - erro_aceitavel))
    else:
        # Para múltiplos erros, usa busca iterativa
        n = erros_esperados
        while True:
            prob = binom.cdf(erros_esperados, n, erro_aceitavel)
            if prob <= alpha:
                break
            n += 1
    return n

@monitor_completo(st.session_state.LOGGER)
def _calcular_hipergeometrica(N, D, alpha, erros_esperados):
    """
    Calcula tamanho da amostra usando distribuição hipergeométrica
    """
    n = erros_esperados
    while n <= N:
        prob = hypergeom.cdf(erros_esperados, N, D, n)
        if prob <= alpha:
            break
        n += 1
    return n

@monitor_completo(st.session_state.LOGGER)
def calcular_risco_amostral(n, N, erro_aceitavel=0.05, erros_esperados=0, metodo='auto'):
    """
        Calcula o risco real (alpha) para um dado tamanho de amostra
    """
    D = ceil(N * erro_aceitavel)
    if metodo == 'auto':
        if N <= 1000:
            metodo = 'hipergeometrica'
        else:
            metodo = 'binomial'
    
    if metodo == 'binomial':
        risco = binom.cdf(erros_esperados, n, erro_aceitavel)
    else:
        risco = hypergeom.cdf(erros_esperados, N, D, n)
    
    return {
                'tamanho_amostra': n,
                'risco_real': risco,
                'nivel_confianca_real': 1 - risco,
                'metodo': metodo
            }

@monitor_completo(st.session_state.LOGGER)
def calcular_tamanho_amostra(N, confianca=0.95, erro_aceitavel=0.05, erros_esperados=0, metodo='auto'):
    """
    Calcula o tamanho da amostra baseado na distribuição binomial ou hipergeométrica.
    
    Parâmetros:
    -----------
    N : int                                       |  Tamanho da população
    confianca : float, opcional (padrão=0.95)     |  Nível de confiança (ex: 0.95 para 95%)
    erro_aceitavel : float, opcional (padrão=0.05)|  Taxa de erro tolerável na população (ex: 0.05 para 5%)
    erros_esperados : int, opcional (padrão=0)    |  Número de erros esperados na amostra
    metodo : str, opcional (padrão='auto')        |  'binomial', 'hipergeometrica' ou 'auto' (escolhe automaticamente baseado no tamanho da população)
    
    Retorna:
    --------
    dict | Dicionário com tamanho da amostra, método usado e informações adicionais
    """
    
    alpha = 1 - confianca
    D = ceil(N * erro_aceitavel)  # Número de itens defeituosos na população
    
    # Escolha automática do método
    if metodo == 'auto':
        if N <= 1000:
            metodo = 'hipergeometrica'
        else:
            metodo = 'binomial'
    
    if metodo == 'binomial':
        n = _calcular_binomial(alpha, erro_aceitavel, erros_esperados)
    else:  # hipergeometrica
        n = _calcular_hipergeometrica(N, D, alpha, erros_esperados)
    
    # Garantir que a amostra não seja maior que a população
    n = min(n, N)
    
    return {
                'tamanho_amostra': n,
                'metodo': metodo,
                'nivel_confianca': confianca,
                'erro_aceitavel': erro_aceitavel,
                'erros_esperados': erros_esperados,
                'tamanho_populacao': N,
                'max_erros_aceitaveis': erros_esperados
            }

@monitor_completo(st.session_state.LOGGER)
def _ano_2_to_4(a):
    if pd.isna(a): 
        return np.nan
    a = int(a)
    if a < 0: 
        return np.nan
    if a < 50:
        return 2000 + a
    if a < 100:
        return 1900 + a
    return a

@monitor_completo(st.session_state.LOGGER)
def corrigir_dt_inex(df, col_data, csv, *, dia1=True):
    """
    Corrige datas inexistentes (ex.: 31/06 -> 30/06) em df[col_data],
    salva um CSV com as correções e devolve (df_corrigido).
    """
    df = df.copy()
    s = df[col_data]

    # 1) Conversao direta
    parsed_ok = pd.to_datetime(s, dayfirst=dia1, errors="coerce")

    # 2) Para o que falhou (NaT), tentamos extrair D/M/Y e capear o dia ao fim do mês
    mask_bad = parsed_ok.isna() & s.notna()
    s_bad = s[mask_bad].astype(str).str.strip()

    if dia1:
        # D/M/Y (31/06/2024, 31-06-24, 31.06.24)
        rgx = r"^\s*(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{2,4})\s*$"
        extr = s_bad.str.extract(rgx)
        d = pd.to_numeric(extr[0], errors="coerce")
        m = pd.to_numeric(extr[1], errors="coerce")
        y = extr[2].apply(_ano_2_to_4)
    else:
        # Y/M/D (2024/06/31, 2024-06-31, 2024.06.31)
        rgx = r"^\s*(\d{2,4})[\/\-.](\d{1,2})[\/\-.](\d{1,2})\s*$"
        extr = s_bad.str.extract(rgx)
        y = extr[0].apply(_ano_2_to_4)
        m = pd.to_numeric(extr[1], errors="coerce")
        d = pd.to_numeric(extr[2], errors="coerce")

    # Monta um "primeiro dia do mês" para obter o fim do mês
    base_ym = pd.to_datetime(
        {"year": y, "month": m, "day": 1},
        errors="coerce"
    )
    # Dia máximo do mês (NaT -> NaN)
    max_dia = (base_ym + MonthEnd(0)).dt.day

    # Capeia o dia
    d_cap = np.minimum(d, max_dia)

    # Reconstroi a data corrigida (alguns continuarão NaT se m ou y inválidos)
    parsed_fixed = pd.to_datetime(
        {"year": y, "month": m, "day": d_cap},
        errors="coerce"
    )

    # 3) Junta: usa parsed_ok onde deu certo; senão tenta parsed_fixed
    parsed_final = parsed_ok.copy()
    parsed_final[mask_bad] = parsed_fixed

    # 4) Monta log de correções
    log = pd.DataFrame({
        "index": df.index,
        "original": s.astype(str),
        "antes_correcao": parsed_ok.astype("datetime64[ns]"),
        "depois_correcao": parsed_final.astype("datetime64[ns]"),
    })

    # status
    status = np.where(
        log["antes_parse"].notna(), "inalterado",
        np.where(log["depois_correcao"].notna(), "corrigido", "irrecuperável")
    )
    log["status"] = status

    # Filtra para salvar só linhas com algum problema (corrigido/irrecuperável)
    log_out = log[log["status"] != "inalterado"].copy()

    # 5) Aplica no DataFrame e salva CSV do log
    df[col_data] = parsed_final
    log_out.to_csv(csv, index=False, sep="|", decimal=",", encoding="Latin-1", chunksize=100_000)

    return df

@monitor_completo(st.session_state.LOGGER)
def processar_batch(data_inicio, data_fim, arquivo_saida, diretorio_base):
    #vamos limitar os itens para cardinalidade menor que n (100 por default)
    caminho_saida = os.path.join(diretorio_base, "BD_LOCAL", arquivo_saida)
    estornos_parquet = os.path.join(diretorio_base, "BD_LOCAL", "estornos.parquet")
    lancamentos_parquet = os.path.join(diretorio_base, "BD_LOCAL", "lancamentos.parquet")

    if not os.path.isfile(estornos_parquet) or not os.path.isfile(lancamentos_parquet):
        raise FileNotFoundError("Arquivos parquet de estornos/lancamentos não encontrados.")

    inicio = time.perf_counter()
    # Cria banco temporário em disco, com nome único
    os.makedirs(os.path.join(diretorio_base, "BD_TEMP"), exist_ok=True)
    temp_path = os.path.join(diretorio_base, "BD_TEMP", f"temp_{uuid.uuid4().hex[:8]}.duckdb")

    try:
        con = duckdb.connect(temp_path)
        con.execute("INSTALL parquet; LOAD parquet;")

        con.execute(f"""
            CREATE TABLE estornos AS 
            SELECT * FROM read_parquet('{estornos_parquet}')
            WHERE data BETWEEN DATE '{data_inicio}' AND DATE '{data_fim}'
        """)

        con.execute(f"""
            CREATE TABLE lancamentos AS 
            SELECT * FROM read_parquet('{lancamentos_parquet}')
            WHERE data BETWEEN DATE '{data_inicio}' AND DATE '{data_fim}'
        """)

        con.execute("""
            WITH pares AS (
                SELECT 
                    e.Ide_RO_Analitico AS id_estorno,
                    l.Ide_RO_Analitico AS id_lancamento,
                    e.Cd_SubODI AS projeto_origem,
                    l.Cd_SubODI AS projeto_destino,
                    e.data AS data_estorno,
                    l.data AS data_lancamento,
                    e.valor_real AS valor_estorno,
                    l.valor_real AS valor_lancamento,
                    e.valor_abs,
                    DATEDIFF('day', e.data, l.data) AS dias_diferenca
                FROM estornos e
                JOIN lancamentos l 
                    ON e.valor_abs = l.valor_abs
                    AND e.Cd_SubODI != l.Cd_SubODI
            ),
            filtrados AS (
                SELECT * FROM pares
                WHERE ABS(dias_diferenca) <= 5
            ),
            ranked AS (
                SELECT * FROM filtrados
                WHERE dias_diferenca IS NOT NULL
                QUALIFY ROW_NUMBER() OVER (
                    PARTITION BY id_estorno
                    ORDER BY ABS(dias_diferenca)
                ) = 1
            )
            SELECT COUNT(*) FROM ranked;
        """)

        qtd = con.fetchone()[0]
        if qtd > 0:
            con.execute(f"""
            COPY (
                WITH pares AS (
                    SELECT 
                        e.Ide_RO_Analitico AS id_estorno,
                        l.Ide_RO_Analitico AS id_lancamento,
                        e.Cd_SubODI AS projeto_origem,
                        l.Cd_SubODI AS projeto_destino,
                        e.data AS data_estorno,
                        l.data AS data_lancamento,
                        e.valor_real AS valor_estorno,
                        l.valor_real AS valor_lancamento,
                        e.valor_abs,
                        DATEDIFF('day', e.data, l.data) AS dias_diferenca
                    FROM estornos e
                    JOIN lancamentos l 
                        ON e.valor_abs = l.valor_abs
                        AND e.Cd_SubODI != l.Cd_SubODI
                ),
                filtrados AS (
                    SELECT * FROM pares
                    WHERE ABS(dias_diferenca) <= 5
                ),
                ranked AS (
                    SELECT * FROM filtrados
                    WHERE dias_diferenca IS NOT NULL
                    QUALIFY ROW_NUMBER() OVER (
                        PARTITION BY id_estorno
                        ORDER BY ABS(dias_diferenca)
                    ) = 1
                )
                SELECT * FROM ranked
            ) TO '{caminho_saida}' (FORMAT 'parquet');
        """)

        con.close()

    finally:
        # Remove o arquivo manualmente após o uso
        if os.path.exists(temp_path):
            os.remove(temp_path)

    fim = time.perf_counter()
    return (f"{data_inicio} to {data_fim}", fim - inicio)

@monitor_completo(st.session_state.LOGGER)
def NR_TI_ROA(dir, st=None):
    """
    Retorna um DataFrame com as colunas:
      - Cd_SubODI
      - Nr_TI (a mais relevante por projeto)
      - limite_usado (dias), seguindo regras
    """
    # Arquivos alvo
    padrao = os.path.join(dir, "DADOS_BRUTOS_MANUAL", "[rR][oO][aA]_*.[cC][sS][vV]")
    arquivos = glob.glob(padrao)
    if not arquivos:
        # Nada encontrado
        return pd.DataFrame(columns=["Cd_SubODI", "Nr_TI", "limite_usado"])

    # Determinar NR_GR (para limites) se st estiver disponível
    if st:
        GRPS = pd.read_csv("tabelas//TBL_GRUPOS.csv", sep="|", decimal=',', on_bad_lines='skip', encoding="Latin-1")
        empresa = st.session_state.nm_empr
 
        Cd_EMP = sql.bsc_cd_aneel(empresa)
        filtro = GRPS['Cd_ANEEL'] == int(Cd_EMP)
        grps_empresa = GRPS[filtro]
        if grps_empresa.empty:
            raise ValueError(f"Nenhum dado encontrado para Cd_ANEEL = {Cd_EMP}")
        rg_rec = grps_empresa[grps_empresa['DT_REF'] == grps_empresa['DT_REF'].max()]
        NR_GR = int(rg_rec['Nr_GRUPO'].iloc[-1])
        # Limites conforme grupo
        dict_lim = {
            'RDA': 30 * (5 if NR_GR in [1, 2, 3] else 3),
            'RDS': 30 * (6 if NR_GR in [1, 2, 3] else 4),
            'LD':  30 * (12 if NR_GR in [1, 2, 3] else 14),
            'SE':  30 * (9 if NR_GR in [1, 2, 3] else 8),
            'SM':  90,
            'DEMAIS': 90
        }
    else:
        dict_lim = {'RDA': 90, 'RDS': 90, 'LD': 90, 'SE': 90, 'SM': 90, 'DEMAIS': 90}

    # Monta a consulta (tentando Latin-1 e, se falhar, UTF-8)
    con = duckdb.connect()
    glob_str = padrao.replace("\\", "/")

    @monitor_completo(st.session_state.LOGGER)
    def run_query(encoding):
        sSQL = f"""
            WITH dados AS (
                SELECT 
                    Cd_SubODI,
                    Nr_TI,
                    REPLACE(REPLACE(REPLACE(VL_tot, '.', ''), ',', '.'),'/','')::DOUBLE AS valor
                FROM read_csv_auto('{glob_str}',
                                   delim='|',
                                   encoding='{encoding}',
                                   null_padding=true,
                                   sample_size=-1,
                                   ignore_errors=true,
                                   header=TRUE)
            ),
            agregado AS (
                SELECT 
                    Cd_SubODI,
                    Nr_TI,
                    SUM(valor) AS soma_valor
                FROM dados
                GROUP BY 1,2
            ),
            ranked AS (
                SELECT 
                    Cd_SubODI,
                    Nr_TI,
                    soma_valor,
                    ROW_NUMBER() OVER (PARTITION BY Cd_SubODI ORDER BY soma_valor DESC) AS rn
                FROM agregado
            )
            SELECT Cd_SubODI, Nr_TI
            FROM ranked
            WHERE rn = 1
        """
        return con.execute(sSQL).fetchdf()

    try:
        df_top = run_query("latin-1")
    except Exception:
        df_top = run_query("utf-8")

    if df_top.empty:
        # Sem dados válidos
        df_top["limite_usado"] = []
        return df_top

    # Calcula o limite_usado conforme Nr_TI
    df_top["Nr_TI"] = df_top["Nr_TI"].fillna(1).astype("Int64")
    ti = df_top["Nr_TI"].astype(int)

    cond_SE = ((ti.between(30, 34)) | (ti.between(50, 54)))
    cond_LD = ((ti.between(35, 39)) | (ti.between(55, 69)))
    cond_RDS = ti.between(42, 44)
    cond_RDA = ti.isin([40, 41])

    limite = np.select(
        [
            cond_SE,
            cond_LD,
            cond_RDS,
            cond_RDA
        ],
        [
            dict_lim['SE'],
            dict_lim['LD'],
            dict_lim['RDS'],
            dict_lim['RDA']
        ],
        default=dict_lim['DEMAIS']
    )

    df_top["limite_usado"] = limite.astype(int)
    return df_top

@monitor_completo(st.session_state.LOGGER)
def NR_TI_PROJ(projeto, dir, st=None):
    # Lista de arquivos CSV no diretório
    arquivo_csv = [
        os.path.join(rf"{dir}\DADOS_BRUTOS_MANUAL", f)
        for f in os.listdir(rf"{dir}\DADOS_BRUTOS_MANUAL")
        if f.lower().endswith('.csv') and (f.lower()[:4]=="roa_")
    ]
    if len(arquivo_csv)>0:
        con = duckdb.connect()
        # Consulta completa
        try:
            sSQL = f"""
                    WITH dados AS (
                        SELECT 
                            Nr_TI,
                            REPLACE(VL_tot, ',', '.')::DOUBLE AS valor
                        FROM read_csv_auto('{arquivo_csv[0]}',
                                            delim='|',
                                            encoding='latin-1',
                                            header=true,
                                            ignore_errors=true)
                        WHERE Cd_SubODI = '{projeto}'
                    ),
                    agregado AS (
                        SELECT 
                            Nr_TI,
                            SUM(valor) AS soma_valor
                        FROM dados
                        GROUP BY Nr_TI
                    )
                    SELECT Nr_TI
                    FROM agregado
                    ORDER BY soma_valor DESC
                    LIMIT 1
                    """
            Nr_TI = int(con.execute(sSQL).fetchone()[0])
        except:
            sSQL = f"""
                WITH dados AS (
                    SELECT 
                        Nr_TI,
                        REPLACE(REPLACE(VL_tot, '.',''), ',', '.')::DOUBLE AS valor
                    FROM read_csv_auto('{arquivo_csv[0]}',
                                        delim='|',
                                        encoding='utf-8',
                                        header=true,
                                        ignore_errors=true)
                    WHERE Cd_SubODI = '{projeto}'
                ),
                agregado AS (
                    SELECT 
                        Nr_TI,
                        SUM(valor) AS soma_valor
                    FROM dados
                    GROUP BY Nr_TI
                )
                SELECT Nr_TI
                FROM agregado
                ORDER BY soma_valor DESC
                LIMIT 1
                """
            Nr_TI = int(con.execute(sSQL).fetchone()[0])

        if st:
            GRPS = pd.read_csv("tabelas//TBL_GRUPOS.csv",sep="|",decimal=',',on_bad_lines='skip',encoding="Latin-1");
            empresa = st.session_state.nm_empr
            Cd_EMP = sql.bsc_cd_aneel(empresa)
            filtro = GRPS['Cd_ANEEL'] == int(Cd_EMP)
            grps_empresa = GRPS[filtro]
            if grps_empresa.empty:
                raise ValueError(f"Nenhum dado encontrado para Cd_ANEEL = {Cd_EMP}")

            registro_mais_recente = grps_empresa[grps_empresa['DT_REF'] == grps_empresa['DT_REF'].max()]
            NR_GR = registro_mais_recente['Nr_GRUPO'].iloc[-1]
            dict_lim = {
                'RDA': 30 * (5 if NR_GR in [1, 2, 3] else 3),
                'RDS': 30 * (6 if NR_GR in [1, 2, 3] else 4),
                'LD':  30 * (12 if NR_GR in [1, 2, 3] else 14),
                'SE':  30 * (9 if NR_GR in [1, 2, 3] else 8),
                'SM':  90,
                'DEMAIS': 90
            }

            if (30 <= Nr_TI <= 34) or (50 <= Nr_TI <= 54):
                limite_usado = dict_lim['SE']
            elif (35 <= Nr_TI <= 39) or (55 <= Nr_TI <= 69):
                limite_usado = dict_lim['LD']
            elif 42 <= Nr_TI <= 44:
                limite_usado = dict_lim['RDS']
            elif Nr_TI in [40, 41]:
                limite_usado = dict_lim['RDA']
            else:
                limite_usado = 90
        else:
            limite_usado = 90

        return limite_usado, Nr_TI
    else:
        return 90, "ND"

@monitor_completo(st.session_state.LOGGER)
def calcular_kpis(df, projeto, dir, lim = 0.1, eps=1, st=None):
    """
    Calcula múltiplos indicadores para uma série temporal acumulada, com base em uma coluna de datas e uma coluna de valores acumulados.
    
    Indicadores retornados:
    - CTA: Centralidade Temporal Acumulada (ideal = 0, varia de -1 a 1)
    - ID: Irregularidade da Derivada (oscilações + reversões de sentido)
    - IRange: número de derivadas intensas [lim_inf, lim_sup]
    - IED_dias: Maior período consecutivo com derivada próxima de zero (em dias)
    - KPI_CRESC (%): Porcentagem de variações negativas no acumulado
    - KPI_GAP (%): Porcentagem do tempo total sem movimento desde o último valor positivo
    - FLG_MOP: True se houver lançamento de MOP sem material superior a um dado período (60 dias)
    - FLG_ST: True se houver lançamento de ST sem material superior a um dado período (60 dias)
    - FLG_JOA: True se houver lançamento de JOA sem material superior a um dado período (60 dias)
    - IEg_dias: Maior período consecutivo sem lançamentos de qualquer natureza de gasto (em dias)
    - IEuc_dias: Maior período consecutivo sem lançamentos de natureza de gasto UC/UAR (em dias)
    - CA_TOT: participação de mão de obra no total do projeto
    - UC_TOT: participaçao de UC/UAR no total do projeto
    - CMD: custo médio do projeto por dia de execução

    Parâmetros:
    - df: DataFrame com colunas 'data' (yyyy/mm/dd) e 'cumulativo'
    - lim_inf, lim_inf: valores percentuais para análise de faixa
    - eps: limiar para considerar derivada como zero

    Retorna:
    - Dicionário com os indicadores
    """

    PER_TI, Nr_TI = NR_TI_PROJ(projeto, dir, st)

    limite_superior = lim * df['cumulativo'].max()
    limite_inferior = - lim * df['cumulativo'].max()
    epsilon_estagnacao = eps

    # Normalização de tempo e valores
    t = (df['data'] - df['data'].min()) / (df['data'].max() - df['data'].min())
    t = t.astype(float)
    y = df['cumulativo']
    y_norm = (y - y.min()) / (y.max() - y.min()) if (y.max() != y.min()) else y

    # CTA
    peso_total = y_norm.sum()
    CTA = 0 if peso_total == 0 else 2 * ((t * y_norm).sum() / peso_total - 0.5)

    # ID_desv_pad
    # vamos usar IQR/mediana para evitar os problemas de saltos que ocorrem e provocariam altas derivadas.
    dy = y.diff().dropna()
    dy_pos = dy[dy > 0]
    p_low, p_high = 5, 95
    if len(dy_pos) >= 10:
        lo, hi = np.percentile(dy_pos, p_low), np.percentile(dy_pos, p_high)
        dy_clip = dy_pos.clip(lower=lo, upper=hi)
    else:
        dy_clip = dy_pos.copy()

    if len(dy_clip) >= 4:
        q1, q3 = np.percentile(dy_clip, [25, 75])
        iqr = q3 - q1
    else:
        iqr = dy_clip.std()

    mediana = np.median(dy_clip) if len(dy_clip) > 0 else 0
    eps = 1e-9
    denom = max(mediana, eps)
    ID_desv_pad = iqr / denom

    reversoes = ((dy * dy.shift(1)) < 0).sum()
    desvio_relativo = dy.std() / dy.mean() if dy.mean() != 0 else 0
    # O desvio padrão sobre a média da derivada indica quão consistente é a taxa de variação da função no intervalo observado. 
    # É uma forma de quantificar a irregularidade no ritmo de crescimento ou decrescimento.
    # Valores baixos indicam que o valor acumulado da obra cresce de forma regular
    # Valores maiores indicam mudanças de ritmo significativas na obra, isto é, acelarações abruptas, ajustes de lançamentos anteriores

    ID_desv_pad = desvio_relativo 

    # O número de reversões indica a frequência de mudança do sentido de variação
    ID_rev = reversoes / max(len(dy) - 1, 1)

    # IRange — baseado na derivada (balanços fortes)
    # número de vezes em que a derivada foi maior que o limiar
    incursao_range = 0
    if limite_inferior is not None and limite_superior is not None:
        dy = y.diff().fillna(0)
        fora_faixa = (dy < limite_inferior) | (dy > limite_superior)
        em_excursao = False
        for f in fora_faixa:
            if f and not em_excursao:
                incursao_range += 1
                em_excursao = True
            elif not f and em_excursao:
                em_excursao = False

    # IED (maior tempo parado, baseado na derivada)
    dy_abs = dy.abs()
    dt = df['data'].diff().dt.total_seconds() / (60 * 60 * 24)  # em dias
    estagnado = (dy_abs < epsilon_estagnacao)
    tempo_bloco = 0
    blocos_duracao = []

    for i in range(1, len(df)):
        if estagnado.iloc[i-1]:
            tempo_bloco += dt.iloc[i]
        else:
            if tempo_bloco > 0:
                blocos_duracao.append(tempo_bloco)
                tempo_bloco = 0
    if tempo_bloco > 0:
        blocos_duracao.append(tempo_bloco)

    IED = max(blocos_duracao) if blocos_duracao else 0.0
    IED = 0 if IED <= PER_TI else IED

    # KPI_CRESC: percentual de quebras no crescimento
    cumul_diff = df['cumulativo'].diff()
    n_violacoes = (cumul_diff < 0).sum()
    kpi_cresc = round((n_violacoes / (len(df) - 1)), 2)

    # KPI_GAP: tempo final sem movimentação para UC
    data_inicio = df['data'].min()
    data_fim = df['data'].max()
    duracao_total = (data_fim - data_inicio).days
    ultimo_positivo = df[(df['valor'] > 0) & (df['Cd_NG'] == 1)]['data'].max()
    dias_sem_mov = (data_fim - ultimo_positivo).days if not pd.isnull(ultimo_positivo) else duracao_total
    kpi_gap = dias_sem_mov

    
    KPI_PER = duracao_total / PER_TI if PER_TI != 0 else 0
    

    df['mes_ano'] = df['data'].dt.to_period('M')
    meses_mat = df.loc[df['Cd_NG'].isin([1,2,'1','2']), 'mes_ano'].unique()
    df['FLG_MAT'] = df['mes_ano'].isin(meses_mat)

    @monitor_completo(st.session_state.LOGGER)
    def sem_mat_2_meses_antes(mes):
        mes_atual = mes.to_timestamp()
        m1 = (mes_atual - DateOffset(months=1)).to_period("M")
        m2 = (mes_atual - DateOffset(months=2)).to_period("M")
        return (m1 not in meses_mat) and (m2 not in meses_mat)

    df["FLG_MOP_tmp"] = df.apply(
                                    lambda x: sem_mat_2_meses_antes(x["mes_ano"]) 
                                    if str(x["Cd_NG"]) == "3" else False, 
                                    axis=1
                                )

    df["FLG_ST_tmp"] = df.apply(
                                    lambda x: sem_mat_2_meses_antes(x["mes_ano"]) 
                                    if str(x["Cd_NG"]) == "4" else False, 
                                    axis=1
                                )

    df["FLG_JOA_tmp"] = df.apply(
                                    lambda x: sem_mat_2_meses_antes(x["mes_ano"]) 
                                    if str(x["Cd_NG"]) == "5" else False, 
                                    axis=1
                                )
    FLG_MOP = df["FLG_MOP_tmp"].any()
    FLG_ST  = df["FLG_ST_tmp"].any()
    FLG_JOA = df["FLG_JOA_tmp"].any()

    # IEg_dias (maior tempo parado, baseado lançamentos)
    dt = df['data'].diff().dt.total_seconds() / (60 * 60 * 24)  # em dias
    IEg_dias = dt.max()

    # IEuc_dias (maior tempo parado, baseado lançamentos de UC/UAR)
    df1 =df.copy()
    df1.loc[len(df1)] = df1.iloc[-1]
    df1.iloc[-1, 0] = 1
    dt = df1[df1['Cd_NG'].isin([1,2,'1','2'])]['data'].diff().dt.total_seconds() / (60 * 60 * 24)  # em dias
    IEuc_dias = dt.max()

    # CA_TOT (relação de CA sobre o total da obra)
    CA_TOT = df[df['Cd_NG'].isin([3,4,'3','4'])]['valor'].sum() / df['valor'].sum()

    # UC_TOT (relação de UC/UAR sobre o total da obra)
    UC_TOT = df[df['Cd_NG'].isin([1,'1'])]['valor'].sum() / df['valor'].sum()

    # CMD (custo médio da obra por dia de execução)
    if (df['data'].max() - df['data'].min()).days > 0:
        CMD = df['valor'].sum() / (df['data'].max() - df['data'].min()).days
    else:
        CMD = df['valor'].sum()


    return {
        'CTA': CTA,
        'ID_desv_pad': ID_desv_pad,
        'ID_rev': ID_rev,
        'IRange': incursao_range,
        'IED_dias': IED,
        'KPI_CRESC (%)': kpi_cresc,
        'KPI_GAP (dias)': kpi_gap,
        'KPI_PER': KPI_PER,
        'FLG_MOP' : FLG_MOP,
        'FLG_ST' : FLG_ST,
        'FLG_JOA' : FLG_JOA,
        'IEg_dias' : IEg_dias,
        'IEuc_dias' : IEuc_dias,
        'CA_TOT' : CA_TOT,
        'UC_TOT': UC_TOT,
        'CMD' : CMD,
        'Nr_TI' : Nr_TI
    }

@monitor_completo(st.session_state.LOGGER)
def bsc_ddsTI(dir, st=None, refazer = False):
    arquivo = Path(rf"{dir}\BD_LOCAL") / "df_caract.parquet"
    if arquivo.is_file() and not refazer:
        df_caract = pd.read_parquet(rf"{dir}\BD_LOCAL\df_caract.parquet")
        return df_caract
    arquivo_csv = [
                    os.path.join(rf"{dir}\DADOS_BRUTOS_MANUAL", f)
                    for f in os.listdir(rf"{dir}\DADOS_BRUTOS_MANUAL")
                    if f.lower().endswith('.csv') and (f.lower()[:4]=="roa_")
                  ]
    if len(arquivo_csv)>0:        
        con = duckdb.connect()
        df = None

        for enc in ["CP1252", "latin-1", "utf-8", "utf-8-sig"]:
            try:
                sSQL = """
                    WITH dados AS (
                        SELECT
                            Nr_TI,
                            Cd_SubODI,

                            SUM(
                                TRY_CAST(
                                    REPLACE(
                                        REPLACE(VL_tot, '.', ''),
                                        ',', '.'
                                    ) AS DOUBLE
                                )
                            ) AS valor,

                            DATE_DIFF(
                                'day',
                                MIN(TRY_CAST(Dt_Lcmto AS DATE)),
                                MAX(TRY_CAST(Dt_Lcmto AS DATE))
                            ) AS per_dias

                        FROM read_csv(
                                        ?,
                                        delim='|',
                                        header=true,
                                        null_padding=true,
                                        encoding=?,
                                        parallel=true,
                                        all_varchar=true
                                    )

                        GROUP BY
                            Nr_TI,
                            Cd_SubODI
                    ),

                    dados_cmu AS (
                        SELECT
                            Nr_TI,
                            Cd_SubODI,
                            valor,
                            per_dias,

                            CASE
                                WHEN per_dias <> 0
                                    THEN valor / per_dias
                                ELSE valor
                            END AS cmd_obra

                        FROM dados
                    )

                    SELECT *
                    FROM dados_cmu
                """

                df = con.execute(
                                    sSQL,
                                    [str(arquivo_csv[0]), enc]
                                ).fetchdf()
                break

            except Exception as e:
                st.write(f"Erro com encoding {enc}: {e}")
                continue

        if df is None:
            raise RuntimeError("Não foi possível processar o CSV com as codificações testadas.")

        df_caract = df.groupby("Nr_TI")["cmd_obra"].agg(
                media="mean",
                desvio_padrao="std",
                q1=lambda x: x.quantile(0.25),
                q3=lambda x: x.quantile(0.75)
            ).reset_index()

        df_caract.to_parquet(rf"{dir}\BD_LOCAL\df_caract.parquet")
        return df_caract  
    return pd.DataFrame()

@monitor_completo(st.session_state.LOGGER)
def bsc_proj(dir, projeto):
    # Lista de arquivos CSV no diretório
    arquivo_csv = [
        os.path.join(rf"{dir}\DADOS_BRUTOS_MANUAL", f)
        for f in os.listdir(rf"{dir}\DADOS_BRUTOS_MANUAL")
        if f.lower().endswith('.csv') and (f.lower()[:4]=="roa_")
    ]
    if len(arquivo_csv)>0:
        con = duckdb.connect()
        # Consulta completa
        try:
            sSQL = f"""
                WITH dados AS (
                    SELECT 
                        Cd_NG,
                        Cd_SubODI,
                        REPLACE(REPLACE(VL_tot, '.',''), ',', '.')::DOUBLE AS valor,
                        CAST(Dt_Lcmto AS DATE) AS data
                    FROM read_csv_auto('{arquivo_csv[0]}',
                                        delim='|',
                                        encoding='latin-1',
                                        header=true,
                                        ignore_errors=true)
                    WHERE Cd_SubODI = '{projeto}'
                    ORDER BY data
                ),

                ordenado AS (
                    SELECT *, 
                        SUM(valor) OVER (ORDER BY data ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulativo
                    FROM dados
                )

                SELECT * FROM ordenado
                ORDER BY data
            """
            return con.execute(sSQL).fetchdf()
        except:
            sSQL = f"""
                WITH dados AS (
                    SELECT 
                        Cd_NG,
                        Cd_SubODI,
                        REPLACE(REPLACE(VL_tot, '.',''), ',', '.')::DOUBLE AS valor,
                        CAST(Dt_Lcmto AS DATE) AS data
                    FROM read_csv_auto('{arquivo_csv[0]}',
                                        delim='|',
                                        encoding='utf-8',
                                        header=true,
                                        ignore_errors=true)
                    WHERE Cd_SubODI = '{projeto}'
                    ORDER BY data
                ),

                ordenado AS (
                    SELECT *, 
                        SUM(valor) OVER (ORDER BY data ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulativo
                    FROM dados
                )

                SELECT * FROM ordenado
                ORDER BY data
            """
            return con.execute(sSQL).fetchdf()  
    return pd.DataFrame()

@monitor_completo(st.session_state.LOGGER)
def bsc_proj_dd(dir, projeto):
    arquivo_csv = [
        os.path.join(rf"{dir}\DADOS_BRUTOS_MANUAL", f)
        for f in os.listdir(rf"{dir}\DADOS_BRUTOS_MANUAL")
        if f.lower().endswith('.csv') and (f.lower()[:4]=="ros_") and (f.lower()[:5]!="ros_v")
    ]
    if len(arquivo_csv)>0:
        con = duckdb.connect()
        try:
            sSQL = f"""
                        SELECT *
                        FROM read_csv_auto('{arquivo_csv[0]}',
                                        delim='|',
                                        encoding='latin-1',
                                        header=true,
                                        ignore_errors=false)
                        WHERE Cd_SubODI = '{projeto}'
                    """
            return con.execute(sSQL).fetchdf()
        except:
            sSQL = f"""
                    SELECT *
                    FROM read_csv_auto('{arquivo_csv[0]}',
                                    delim='|',
                                    encoding='utf-8',
                                    header=true,
                                    ignore_errors=false)
                    WHERE Cd_SubODI = '{projeto}'
                """
        return con.execute(sSQL).fetchdf()
    return pd.DataFrame()

@monitor_completo(st.session_state.LOGGER)
def detectar_encoding(caminho):
    from pathlib import Path
    dados = Path(caminho).read_bytes()

    if dados.startswith(b"\xef\xbb\xbf"):
        return "utf-8"

    try:
        dados.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "latin-1"

@monitor_completo(st.session_state.LOGGER)         
def estornos(diretorio_base, bd, empresa, st=None):
    arquivo_csv = [
                    os.path.join(rf"{diretorio_base}\DADOS_BRUTOS_MANUAL", f)
                    for f in os.listdir(rf"{diretorio_base}\DADOS_BRUTOS_MANUAL")
                    if f.lower().endswith('.csv') and (f.lower()[:4]=="roa_")
                ]
    if len(arquivo_csv)>0:
        teste = sql.sanear_csv_mod(
                                diretorio = rf"{st.session_state.tra_dir}\DADOS_BRUTOS_MANUAL",
                                arq = arquivo_csv[0], st = st                                    
                            )

        if st: a = st.progress(10, "Fazendo a análise de movimentação entre obras usando estornos...")
        con = duckdb.connect(f"{diretorio_base}/BD_LOCAL/temp.duckdb")
        con.execute("PRAGMA temp_directory='D:/'")
        con.execute("PRAGMA max_temp_directory_size='200GiB'")
        try:
            if st: a.progress(11, "Buscando dados...")
            arquivo = str(arquivo_csv[0])
            encoding = detectar_encoding(arquivo)
            con.execute(f"""
                CREATE OR REPLACE TABLE base_dados AS
                SELECT Ide_RO_Analitico,
                Cd_SubODI,
                Dt_Lcmto,
                VL_tot,
                COUNT(*) OVER (PARTITION BY VL_tot) AS ocorrencias 
                FROM read_csv(?, delim='|',encoding=?, header=true, ignore_errors=false)
            """, [arquivo, encoding])
        except Exception as e:
            if st: 
                st.error(f"Erro na Etapa 1 (cruzamento de dados), arquivo {arquivo_csv[0]}: {e}")
                registrar_evento(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                nome_evento = 'consolidacao_roa_estornos',
                                mensagem = f'Falhou na consolidação do ROA.', 
                                nivel = 'ERRO',
                                detalhes = {'erro' : e})
            raise

        try:
            if st: a.progress(20, "Filtrando e convertendo dados...")
            con.execute("""
                CREATE OR REPLACE TABLE dados_transformados AS
                SELECT 
                    Ide_RO_Analitico,
                    Cd_SubODI,
                    Dt_Lcmto,
                    VL_tot,
                    REPLACE(REPLACE(VL_tot, '.',''), ',', '.')::DOUBLE AS valor_real,
                    ABS(REPLACE(REPLACE(VL_tot, '.',''), ',', '.')::DOUBLE) AS valor_abs,
                    REPLACE(REPLACE(VL_tot, '.',''), ',', '.')::DOUBLE < 0 AS eh_estorno,
                    CAST(Dt_Lcmto AS DATE) AS data
                FROM base_dados
                WHERE VL_tot IS NOT NULL AND Dt_Lcmto IS NOT NULL AND (ocorrencias < 100)
            """)
        except Exception as e:
            if st: 
                st.error(f"Erro na Etapa 2 (conversao de dados): {e}")
                registrar_evento(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                nome_evento = 'consolidacao_roa_estornos',
                                mensagem = f'Falhou na consolidação do ROA.', 
                                nivel = 'ERRO',
                                detalhes = {'erro' : e})
            raise

        df_freq_maior_100 = con.execute("""
                                        SELECT *
                                        FROM (
                                            SELECT 
                                                Ide_RO_Analitico,
                                                Cd_SubODI,
                                                Dt_Lcmto,
                                                VL_tot,
                                                REPLACE(REPLACE(VL_tot, '.',''), ',', '.')::DOUBLE AS valor_real,
                                                ABS(REPLACE(REPLACE(VL_tot, '.',''), ',', '.')::DOUBLE) AS valor_abs,
                                                REPLACE(REPLACE(VL_tot, '.',''), ',', '.')::DOUBLE < 0 AS eh_estorno,
                                                CAST(Dt_Lcmto AS DATE) AS data,
                                                COUNT(*) OVER (PARTITION BY REPLACE(REPLACE(VL_tot, '.',''), ',', '.')::DOUBLE) AS ocorrencias
                                            FROM base_dados
                                            WHERE VL_tot IS NOT NULL AND Dt_Lcmto IS NOT NULL
                                        ) sub
                                        WHERE ocorrencias >= 100
                                    """).fetchdf()
        df_freq_maior_100.to_csv(f"{diretorio_base}/AIS_ANLS/TST_LCMTO_FREQ_ELEVADA_{empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
        df_freq_maior_100.to_sql('TST_LCMTO_FREQ_ELEVADA', bd, if_exists='replace', index=False)
        if st:
            registrar_artefato(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                file_path = rf"{diretorio_base}/AIS_ANLS/TST_LCMTO_FREQ_ELEVADA_{empresa}.csv",
                                tipo_artefato = "SAIDA", 
                                calcular_hash = True)
        try:
            if st: a.progress(35, "Separa estornos e lançamentos...")
            con.execute("CREATE OR REPLACE TABLE estornos AS SELECT * FROM dados_transformados WHERE eh_estorno")
            con.execute("CREATE OR REPLACE TABLE lancamentos AS SELECT * FROM dados_transformados WHERE NOT eh_estorno")
            con.execute(f"""
                    COPY (
                        SELECT * FROM dados_transformados WHERE eh_estorno
                    ) TO '{diretorio_base}/BD_LOCAL/estornos.parquet' (FORMAT 'parquet')
                """)
                
            con.execute(f"""
                            COPY (
                                SELECT * FROM dados_transformados WHERE NOT eh_estorno
                            ) TO '{diretorio_base}/BD_LOCAL/lancamentos.parquet' (FORMAT 'parquet')
                        """)
        except Exception as e:
            if st: 
                st.error(f"Erro na Etapa 3 (estornos e lançamentos): {e}")
                registrar_evento(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                nome_evento = 'consolidacao_roa_estornos',
                                mensagem = f'Falhou na segregação entre estornos e lançamentos.', 
                                nivel = 'ERRO',
                                detalhes = {'erro' : e})
            raise

        try:
            if st: a.progress(40, "Cruza lançamentos e estornos com filtro temporal e de valor...")
            NUM_THREADS = 4
            DELTA_MES = 5

            min_data, max_data = con.execute("""
                                                SELECT MIN(Dt_Lcmto), MAX(Dt_Lcmto) FROM estornos
                                            """).fetchone()

            data_atual = min_data
            batches = []
            while data_atual < max_data:
                data_proximo = min(data_atual + timedelta(days=DELTA_MES), max_data)
                arquivo_saida = os.path.join(f"{diretorio_base}/BD_LOCAL/", f"batch_{data_atual.strftime('%Y%m%d')}_{data_proximo.strftime('%Y%m%d')}.parquet")
                batches.append((data_atual, data_proximo, arquivo_saida))
                data_atual = data_proximo + timedelta(days=1)
            
            tempos = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
                futures = [executor.submit(processar_batch, inicio, fim, saida, diretorio_base) for (inicio, fim, saida) in batches]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        tempos.append(future.result())
                    except Exception as e:
                        if st: 
                            st.error(f"Erro no processamento de batch: {e}")
                            registrar_evento(st.session_state.database_MAN, 
                                            st.session_state.execucao_id, 
                                            nome_evento = 'consolidacao_roa_estornos',
                                            mensagem = f'Erro na análise por BATCH para associação de lançamentos e de estornos.', 
                                            nivel = 'ERRO',
                                            detalhes = {'erro' : e})
                        continue
            
            try:
                con.execute(f"""
                                CREATE OR REPLACE TABLE mov_cruz AS
                                SELECT * FROM read_parquet('{diretorio_base}/BD_LOCAL/batch_*.parquet')
                            """)
            except Exception as e:
                if st: 
                    st.error(f"Erro ao executar consulta final: {e}")
                    registrar_evento(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                nome_evento = 'consolidacao_roa_estornos',
                                mensagem = f'Erro na consulta final.', 
                                nivel = 'ERRO',
                                detalhes = {'erro' : e})

            for _, _, arquivo in batches:
                try:
                    if os.path.isfile(arquivo):
                        os.remove(arquivo)
                except Exception as e:
                    if st: st.warning(f"Não foi possível remover o arquivo {arquivo}: {e}")
                    continue

            tempos.sort(key=lambda x: x[0])
            nomes_batches = [str(t[0]) for t in tempos]
            tempos_execucao = [t[1] for t in tempos]
            if st: 
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.bar(nomes_batches, tempos_execucao)
                step = max(len(nomes_batches) // 20, 1) 
                xticks_idx = list(range(0, len(nomes_batches), step))
                if len(nomes_batches) - 1 not in xticks_idx:
                    xticks_idx.append(len(nomes_batches) - 1)
                ax.set_xticks(xticks_idx)
                ax.set_xticklabels([nomes_batches[i] for i in xticks_idx], rotation=45)

                ax.set_ylabel("Tempo (s)")
                ax.set_title("Tempo de execução por batch")
                ax.grid(True)
                fig.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            
        except Exception as e:
            if st: 
                st.error(f"Erro na Etapa 4 (cruzamento estornos e lançamentos): {e}")
                registrar_evento(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                nome_evento = 'cruzamento_estorno_lancamentos',
                                mensagem = f'Falhou na ação de cruzar estornos e lançamentos.', 
                                nivel = 'ERRO',
                                detalhes = {'erro' : e})
            raise

        try:
            if st: a.progress(45, "Seleciona os melhores pares...")
            con.execute("""
                            CREATE OR REPLACE TABLE melhores_pares AS
                            SELECT * FROM (
                                SELECT *,
                                    ROW_NUMBER() OVER (
                                        PARTITION BY id_estorno
                                        ORDER BY ABS(dias_diferenca)
                                    ) AS rank_lanc
                                FROM mov_cruz
                            )
                            WHERE rank_lanc = 1
                        """)
        except Exception as e:
            if st: 
                st.error(f"Erro na Etapa 5 (melhores pares): {e}")
                registrar_evento(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                nome_evento = 'teste_melhores_pares',
                                mensagem = f'Falhou na busca de melhores pares para lançamentos repetidos.', 
                                nivel = 'ERRO',
                                detalhes = {'erro' : e})

        try:
            mov_obras = con.execute("""
                                        SELECT * FROM melhores_pares ORDER BY data_estorno
                                    """).df()
            mov_obras.to_sql('tst_mov_obras', bd, if_exists='replace', index=False)
            mov_obras.to_csv(f"{diretorio_base}/AIS_ANLS/TST_MOV_OBRAS_{empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
            if st:
                registrar_artefato(st.session_state.database_MAN, 
                                    st.session_state.execucao_id, 
                                    file_path = rf"{diretorio_base}/AIS_ANLS/TST_MOV_OBRAS_{empresa}.csv",
                                    tipo_artefato = "SAIDA", 
                                    calcular_hash = True)
        except Exception as e:
            if st: 
                st.error(f"Erro ao executar consulta final: {e}")
                registrar_evento(st.session_state.database_MAN, 
                                 st.session_state.execucao_id, 
                                 nome_evento = 'teste_mov_obras',
                                 mensagem = f'Falhou na geração do arquivo TST_MOV_OBRAS_{empresa}.csv.', 
                                 nivel = 'ERRO',
                                 detalhes = {'erro' : e})

        enc = 'CP1252'    
        if st: a.progress(50, "Fazendo a análise de percentual de estornos nas obras...")
        sSQL = f"""
                        WITH dados AS (
                            SELECT 
                                Cd_SubODI AS projeto,
                                REPLACE(REPLACE(VL_tot, '.',''), ',', '.')::DOUBLE < 0 AS eh_estorno
                            FROM read_csv_auto('{arquivo_csv[0]}', delim='|',
                                            null_padding=true, 
                                            encoding='{enc}',
                                            parallel=true,
                                            all_varchar=true)
                        )
                        SELECT 
                            projeto,
                            COUNT(*) AS total,
                            SUM(eh_estorno::INTEGER) AS estornos,
                            ROUND(100.0 * SUM(eh_estorno::INTEGER) / COUNT(*), 2) AS pct_estornos
                        FROM dados
                        GROUP BY projeto
                        ORDER BY pct_estornos DESC
                        """
        if st: a.progress(65, "Fazendo a análise de percentual de estornos por data...")
        res_est = con.execute(sSQL).fetchdf()
        res_est.to_sql('tst_pct_est', bd, if_exists='replace', index=False)
        res_est.to_csv(f"{diretorio_base}/AIS_ANLS/TST_PCT_EST_{empresa}.csv", sep="|", decimal=',', chunksize=100_000)
        if st:
            registrar_artefato(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                file_path = rf"{diretorio_base}/AIS_ANLS/TST_PCT_EST_{empresa}.csv",
                                tipo_artefato = "SAIDA", 
                                calcular_hash = True)
        
        sSQL = f"""
                        WITH dados AS (
                            SELECT 
                                CAST(Dt_Lcmto AS DATE) AS data,
                                REPLACE(REPLACE(VL_tot, '.',''), ',', '.')::DOUBLE < 0 AS eh_estorno
                            FROM read_csv_auto('{arquivo_csv[0]}', delim='|',
                                            null_padding=true, 
                                            encoding='{enc}',
                                            parallel=true,
                                            all_varchar=true)
                        )
                        SELECT 
                            data,
                            COUNT(*) AS total,
                            SUM(eh_estorno::INTEGER) AS estornos,
                            ROUND(100.0 * SUM(eh_estorno::INTEGER) / COUNT(*), 2) AS pct_estornos
                        FROM dados
                        GROUP BY data
                        ORDER BY data
                        """

        res_est_dt = con.execute(sSQL).fetchdf()
        res_est_dt.to_sql('tst_pct_est_dt', bd, if_exists='replace', index=False)
        res_est_dt.to_csv(f"{diretorio_base}/AIS_ANLS/TST_PCT_EST_{empresa}_data.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
        if st:
            registrar_artefato(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                file_path = rf"{diretorio_base}/AIS_ANLS/TST_PCT_EST_{empresa}_data.csv",
                                tipo_artefato = "SAIDA", 
                                calcular_hash = True)
            
        if st: a.progress(80, "Fazendo a análise de percentual de ajustes nas obras...")
        erro = {}
        for enc in ['CP1252', 'latin-1', 'utf-8']:
            try:
                sSQL = f"""
                            WITH dados AS (
                                SELECT 
                                    Cd_SubODI AS projeto,
                                    REPLACE(REPLACE(VL_tot, '.',''), ',', '.')::DOUBLE AS valor,
                                    CAST(Dt_Lcmto AS DATE) AS data
                                FROM read_csv('{arquivo_csv[0]}',
                                            delim='|',
                                            null_padding=true, 
                                            encoding='{enc}',
                                            parallel=true,
                                            all_varchar=true)
                            ),

                            max_data AS (
                                SELECT projeto, MAX(data) AS data_fim, MIN(data) AS data_ini,
                                DATEDIFF('day', MIN(data), MAX(data)) AS dias_duracao
                                FROM dados
                                GROUP BY projeto
                            ),

                            estornos AS (
                                SELECT projeto, SUM(valor) AS soma_estornos
                                FROM dados
                                WHERE valor < 0
                                GROUP BY projeto
                            ),

                            lancamentos AS (
                                SELECT projeto, SUM(valor) AS soma_lancamentos
                                FROM dados
                                WHERE valor >= 0
                                GROUP BY projeto
                            ),

                            ajustes_finais AS (
                                SELECT d.projeto, SUM(d.valor) AS soma_ajustes_finais
                                FROM dados d
                                JOIN max_data m ON d.projeto = m.projeto
                                WHERE d.data >= m.data_fim - INTERVAL 15 DAY
                                AND m.dias_duracao > 90
                                GROUP BY d.projeto
                            ),

                            totais AS (
                                SELECT projeto, SUM(valor) AS total_valor
                                FROM dados
                                GROUP BY projeto
                            )

                            SELECT 
                                t.projeto,
                                total_valor,
                                COALESCE(e.soma_estornos, 0) AS soma_estornos,
                                COALESCE(l.soma_lancamentos, 0) AS soma_lancamentos,
                                ROUND(100.0 * COALESCE(ABS(e.soma_estornos), 0) / NULLIF(total_valor, 0), 2) AS pct_estorno_valor,
                                COALESCE(a.soma_ajustes_finais, 0) AS soma_ajustes_finais,
                                ROUND(100.0 * COALESCE(a.soma_ajustes_finais, 0) / NULLIF(total_valor, 0), 2) AS pct_ajuste_finais_valor,
                                ROUND(100.0 * COALESCE(e.soma_estornos, 0) / NULLIF(total_valor + COALESCE(l.soma_lancamentos, 0), 0), 2) AS pct_ajuste_obra
                            FROM totais t
                            LEFT JOIN estornos e ON t.projeto = e.projeto
                            LEFT JOIN lancamentos l ON t.projeto = l.projeto
                            LEFT JOIN ajustes_finais a ON t.projeto = a.projeto
                            ORDER BY soma_estornos DESC, pct_ajuste_obra DESC
                            """

                pct_ajst = con.execute(sSQL).fetchdf()
                break
            except Exception as e:
                erro[enc] = e
                if st:
                    registrar_evento(st.session_state.database_MAN, 
                                    st.session_state.execucao_id, 
                                    nome_evento = 'consolidacao_roa_estornos',
                                    mensagem = f'Falhou na determinação do percentual usando encoding {enc}.', 
                                    nivel = 'ERRO',
                                    detalhes = {'erro' : e})

        if len(erro)>0:
            st.text(erro)
            raise UserWarning("Você tem problema de codificação do arquivo.")
        pct_ajst.to_sql('tst_pct_ajst', bd, if_exists='replace', index=False)
        pct_ajst.to_csv(f"{diretorio_base}/AIS_ANLS/TST_PCT_AJST_{empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
        if st:
            registrar_artefato(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                file_path = rf"{diretorio_base}/AIS_ANLS/TST_PCT_AJST_{empresa}.csv",
                                tipo_artefato = "SAIDA", 
                                calcular_hash = True)
        if st: a.progress(100, "Finalizado análise de estornos.")
        return "OK"

    else:
        return "Falhou"

@monitor_completo(st.session_state.LOGGER)
def tst_ALT(df_01, df_02, obs, nome):
    @monitor_completo(st.session_state.LOGGER)
    def nome_DF(df):
        for nome, obj in globals().items():
            if obj is df and isinstance(obj, pd.DataFrame):
                return nome
        return None
    col_DES = [col for col in df_02.columns if col.startswith("Id")]

    if len(df_02[df_02['OBS_FISC'] == obs]) !=0:
        df_02['Nm_Arq'] = nome
        df_02['Id_SEQ'] = df_02[col_DES[0]]
        df_01 = pd.concat([df_01,df_02[['Id_SEQ', 'Nm_Arq',"OBS_FISC"]][df_02['OBS_FISC'] == obs]], ignore_index = True)
    return df_01

@monitor_completo(st.session_state.LOGGER)
def anl_AIS_BAIXAS(con, dir_arq_saida,Empresa, st = None):
    #Faz um teste sobre a classificação das UC (código) e se são UC ou UAR do arquivo de baixas
    #now = datetime.now()
    #if st:
        #avl = st.success(f"  Hora de início, AIS/BAIXAS: {now.strftime('%H:%M:%S')}")
    txtALERTAS = pd.DataFrame(columns = ["Id_SEQ","Nm_Arq","OBS_FISC"])

    
    dt_ARQ = sql.max_arq("BAIXAS", con, Empresa)
    if dt_ARQ:
        SQLq = f"""
            SELECT *
            FROM BAIXAS t1 WHERE dt_ARQ = {dt_ARQ}
            """
        BAIXAS = pd.read_sql(SQLq, con)
    else:
        if st:
            st.error("Falha ao importar o arquivo BAIXAS da base local.")
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo BAIXAS da base local.')


    BAIXAS['OBS_FISC'] = 'OK'
    """
    TBL_TUC = pd.read_csv("tabelas\TBL_TUC.csv",sep="|",decimal=',',on_bad_lines='skip',encoding="Latin-1",dtype=str);
    TBL_TUC.fillna('ND', inplace = True)
    if 'Txt_DESC_TECN' in BAIXAS.columns:
        BAIXAS = BAIXAS.rename(columns={'Txt_DESC_TECN':'txt_Desc_Bem'})
    for UC in TBL_TUC['Ide_TUC']:
        texDESCR = TBL_TUC[TBL_TUC['Ide_TUC'] == UC]['PLV_CHV'].to_list()
        if len(texDESCR[0]) > 3:
            LST_ITENS = texDESCR[0].split(',')
            BUSCA = '|'.join([f'{item}' for item in LST_ITENS])
            BUSCA = '(?i)' + BUSCA
            BAIXAS.loc[(~(BAIXAS['txt_Desc_Bem'].str.contains(BUSCA, na=False))) & (BAIXAS['Nr_TUC'] == UC),'OBS_FISC'] = 'Verificar se o código UC é compatível com descrição'
    """
    # Carrega a tabela
    TBL_TUC = bsc_dados_reg('TBL_TUC').fillna('ND')

    # Renomeia
    if 'Txt_DESC_TECN' in BAIXAS.columns:
        BAIXAS = BAIXAS.rename(columns={'Txt_DESC_TECN':'txt_Desc_Bem'})

    # Pré-processa a TBL_TUC em um dicionário
    mapa_busca = {}
    for _, row in TBL_TUC.iterrows():
        UC = row['Ide_TUC']
        if len(row['PLV_CHV']) > 3:
            LST_ITENS = row['PLV_CHV'].split(',')
            BUSCA = '(?i)' + '|'.join(map(re.escape, LST_ITENS)) 
            mapa_busca[UC] = BUSCA

    # Aplica em lote, uma vez por UC
    for UC, BUSCA in mapa_busca.items():
        mask = (BAIXAS['Nr_TUC'] == UC) & (~BAIXAS['txt_Desc_Bem'].str.contains(BUSCA, na=False, regex=True))
        BAIXAS.loc[mask, 'OBS_FISC'] = 'Verificar se o código UC é compatível com descrição'
    txtALERTAS = tst_ALT(txtALERTAS, BAIXAS, 'Verificar se o código UC é compatível com descrição', 'BAIXAS')

    LST_UAR = ['relé', 'rele', 'retificador', 'concentrador', 'cobertura', 'switch', 'baterias', 'conversor', 'serv',
              'servicos', 'serviços', 'transmissor de dados', 'utr', 'unidade de terminal', 'unidade terminal',
              'supervisor', 'voltimetro', 'voltímetro', 'cobertura', 'telhado', 'remota', 'rf', 'computador',
              'pc', 'microcomputador', 'inversor', 'cj de buchas', 'sincronizador', 'mostrador remoto', 'mostrador',
              'nobreak', 'modem', 'mesh', 'conversor dc/dc', 'ethernet', 'amplificador', 'gprs', 'detector de falta',
              'detector', 'roteador', 'monitor', 'teclado', 'terminal', 'trocador', 'transceptor', 'gerador',
              'no break', 'indicadores', 'cpu', 'relê', 'relè']
    BUSCA = '|'.join([f'{item}' for item in LST_UAR])
    BUSCA = '(?i)' + BUSCA
    BAIXAS['TESTE_UAR'] = BAIXAS['txt_Desc_Bem'].str.contains(BUSCA)
    BAIXAS.loc[((BAIXAS['TESTE_UAR'] == True) & (BAIXAS['Cd_UAR'] != 'UAR')),'OBS_FISC'] = 'Verificar se é UAR'
    txtALERTAS = tst_ALT(txtALERTAS, BAIXAS, 'Verificar se é UAR', 'BAIXAS')
    
    #Faz um teste sobre a classificação das UC (código) e se são UC ou UAR do arquivo AIS
    
    dt_ARQ = sql.max_arq("AIS", con, Empresa)
    if dt_ARQ:
        SQLq = f"""
            SELECT *
            FROM AIS t1 WHERE dt_ARQ = {dt_ARQ}
            """
        AIS = pd.read_sql(SQLq, con)
    else:
        if st:
            st.error('Falha ao importar o arquivo AIS da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS da base local.')
        
    AIS['OBS_FISC'] = 'OK'
    """
    for UC in TBL_TUC['Ide_TUC']:
        texDESCR = TBL_TUC[TBL_TUC['Ide_TUC'] == UC]['PLV_CHV'].to_list()
        if len(texDESCR[0]) > 3:
            LST_ITENS = texDESCR[0].split(',')
            BUSCA = '|'.join([f'{item}' for item in LST_ITENS])
            BUSCA = '(?i)' + BUSCA
            AIS.loc[(AIS['FLG_PER']=='1') & (AIS['Cd_UAR'] != 'UAR') &  (~(AIS['txt_Desc_Bem'].str.contains(BUSCA, na=False))),'OBS_FISC'] = 'Verificar se o código UC é compatível com descrição'
    """
    # Aplica em lote, uma vez por UC
    for UC, BUSCA in mapa_busca.items():
        mask = (AIS['Nr_TUC'] == UC) & (~AIS['txt_Desc_Bem'].str.contains(BUSCA, na=False, regex=True))
        AIS.loc[mask, 'OBS_FISC'] = 'Verificar se o código UC é compatível com descrição'

    txtALERTAS = tst_ALT(txtALERTAS, AIS, 'Verificar se o código UC é compatível com descrição', 'AIS')

    LST_UAR = ['relé', 'rele', 'retificador', 'concentrador', 'cobertura', 'switch', 'baterias', 'conversor', 'serv',
              'servicos', 'serviços', 'transmissor de dados', 'utr', 'unidade de terminal', 'unidade terminal',
              'supervisor', 'voltimetro', 'voltímetro', 'cobertura', 'telhado', 'remota', 'rf', 'computador',
              'pc', 'microcomputador', 'inversor', 'cj de buchas', 'sincronizador', 'mostrador remoto', 'mostrador',
              'nobreak', 'modem', 'mesh', 'conversor dc/dc', 'ethernet', 'amplificador', 'gprs', 'detector de falta',
              'detector', 'roteador', 'monitor', 'teclado', 'terminal', 'trocador', 'transceptor', 'gerador',
              'no break', 'indicadores', 'cpu', 'relê', 'relè', 'bucha', 'suporte', 'bateria', 'serviço', 'servico',
              'terminal', 'conversor', 'cc/cc']
    BUSCA = '|'.join([f'{item}' for item in LST_UAR])
    BUSCA = '(?i)' + BUSCA
    AIS['TESTE_UAR'] = AIS['txt_Desc_Bem'].str.contains(BUSCA)
    AIS.loc[(AIS['FLG_PER']=='1') & (AIS['Cd_UAR'] != 'UAR') & (AIS['TESTE_UAR'] == True),'OBS_FISC'] = 'Verificar se é UAR'
    txtALERTAS = tst_ALT(txtALERTAS, AIS, 'Verificar se é UAR', 'AIS')

    LST_TI = ['30', '31', '32', '33', '34', '50', '51', '52', '53', '54']
    BUSCA = '|'.join([f'{item}' for item in LST_TI])
    AIS['TESTE_TI'] = AIS['Nr_TI'].str.contains(BUSCA)
    AIS.loc[(AIS['FLG_PER']=='1') & (AIS['Nr_TUC'] == '295') & (AIS['Cd_UAR'] != 'UAR') & (AIS['TESTE_TI'] == True),'OBS_FISC'] = 'VERIFICAR, PARECE SER TUC 205, §62: PRORET 2.3'
    txtALERTAS = tst_ALT(txtALERTAS, AIS, 'VERIFICAR, PARECE SER TUC 205, §62: PRORET 2.3', 'AIS')

    txtALERTAS.to_sql('txtALERTAS', con, if_exists='replace', index=False)
    txtALERTAS.to_csv(f"{dir_arq_saida}//ANL_AIS_BAIXAS_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    #now = datetime.now()
    #if st:
        #avl.success(f"  Hora de fim, AIS/BAIXAS: {now.strftime('%H:%M:%S')}")
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def anl_AIS_COM_MED(con, dir_arq_saida, Empresa, st = None):
    LST_TI = [(x) for x in range(10, 30)] + [(x) for x in range(70, 91)] + [94, 95, 97, 99]
    LST_TI += [str(x) for x in range(10, 30)] + [str(x) for x in range(70, 91)] + [94, 95, 97, 99]
    FILTRO_TI = f"{LST_TI}".replace("[","(").replace("]",")")

    SQLq = f"""
                SELECT t1.Nr_TI, t1.Nr_TUC, t1.Nr_A1, t1.Nr_A3, t1.Cd_UAR, t1.Qtd_AIS
                FROM AIS t1 WHERE dt_ARQ = ? AND t1.Nr_TI NOT IN {FILTRO_TI}
                AND t1.Nr_TUC IN (295,'295')
            """
    AIS = sql.imp_tbl_forma_001("AIS", SQLq=SQLq, con=con, st=st, Empresa=Empresa)
    
    if (AIS['Qtd_AIS'].dtype == 'object') and ('Qtd_AIS' in AIS.columns.to_list()):
        AIS['Qtd_AIS'] = pd.to_numeric(AIS['Qtd_AIS'].str.replace(",","."), errors='coerce')

    COMERC = sql.imp_tbl_forma_001("COMERCIAL_MEDIDORES", con=con, st=st, Empresa=Empresa)

    if st.session_state.dt_fim >= date.today():
        st.warning(f"  Buscando alternativa para INCR, período intercalar de análise. Início em: {datetime.now().strftime('%H:%M:%S')}")
        SQLq = f"""
                SELECT t1.Nr_TI, t1.Nr_TUC, t1.Nr_A1, t1.Nr_A3, t1.Cd_UAR, t1.Qtd_AIS,
                "1" AS FLG_ELIG, "1" AS Cd_CONC
                FROM AIS t1 WHERE dt_ARQ = ? AND FLG_PER = "1" AND t1.Nr_TI NOT IN {FILTRO_TI}
                AND t1.Nr_TUC IN (295,'295')
                """
        INC = sql.imp_tbl_forma_001("AIS", SQLq=SQLq, con=con, st=st, Empresa=Empresa)
    else:
        SQLq = f"""
                    SELECT t1.Nr_TI, t1.Nr_TUC, t1.Nr_A1, t1.Nr_A3, t1.Cd_UAR, 
                            t1.Qtd_AIS, t1.FLG_ELIG, t1.Cd_CONC
                    FROM INCR t1 WHERE dt_ARQ = ? AND t1.Nr_TI NOT IN {FILTRO_TI}
                    AND t1.Nr_TUC IN (295,'295')
                    """
        INC = sql.imp_tbl_forma_001("INCR", SQLq=SQLq, con=con, st=st, Empresa=Empresa)

    if (INC['Qtd_AIS'].dtype == 'object') and ('Qtd_AIS' in INC.columns.to_list()):    
        INC['Qtd_AIS'] = INC['Qtd_AIS'].apply(lambda x: x.replace(",", ".") if isinstance(x, str) else x)
        INC['Qtd_AIS'] = pd.to_numeric(INC['Qtd_AIS'], errors='coerce')

    dt_ARQ = sql.max_arq("PPBB", con, Empresa)
    if dt_ARQ:
        try:
            dt_ARQ1 = sql.max_arq("PCBB", con, Empresa)
            if dt_ARQ1:
                SQLq = f"""
                    SELECT t1.Nr_TI,t1.Nr_TUC,t1.Nr_A1,t1.Nr_A3,t1.Cd_UAR,t2.Qtd_AISa
                    FROM PPBB t1 LEFT JOIN PCBB t2 ON t1.Id_SEQ_PP = t2.Id_SEQ_PP
                    WHERE t2.FLG_ELIG = '1' AND t2.Cd_CONC = '1' AND  t1.dt_ARQ = {dt_ARQ} AND  t2.dt_ARQ = {dt_ARQ1}
                    AND t1.Nr_TI NOT IN {FILTRO_TI} AND t1.Nr_TUC IN (295,'295')
                    """
            else:
                SQLq = f"""
                    SELECT t1.Nr_TI,t1.Nr_TUC,t1.Nr_A1,t1.Nr_A3,t1.Cd_UAR,t1.Qtd_AIS AS Qtd_AISa
                    FROM PPBB t1 
                    WHERE t1.FLG_ELIG = '1' AND t1.Cd_CONC = '1' AND  t1.dt_ARQ = {dt_ARQ}
                    AND t1.Nr_TI NOT IN {FILTRO_TI} AND t1.Nr_TUC IN (295,'295')
                    """
            BB = pd.read_sql(SQLq, con)
        except:
            if dt_ARQ1:
                SQLq = f"""
                    SELECT t1.Nr_TI,t1.Nr_TUC,t1.Nr_A1,t1.Nr_A3,t1.Cd_UAR,t2.Qtd_AISa
                    FROM PPBB t1 LEFT JOIN PCBB t2 ON t1.Id_SEQ_PP = t2.Id_SEQ_PP
                    WHERE t2.FLG_ELIG = '1' AND t1.Cd_CONC = '1' AND  t1.dt_ARQ = {dt_ARQ} AND  t2.dt_ARQ = {dt_ARQ1}
                    AND t1.Nr_TI NOT IN {FILTRO_TI} AND t1.Nr_TUC IN (295,'295')
                    """
            else:
                SQLq = f"""
                    SELECT t1.Nr_TI,t1.Nr_TUC,t1.Nr_A1,t1.Nr_A3,t1.Cd_UAR,t1.Qtd_AIS AS Qtd_AISa
                    FROM PPBB t1 
                    WHERE t1.FLG_ELIG = '1' AND t1.Cd_CONC = '1' AND  t1.dt_ARQ = {dt_ARQ}
                    AND t1.Nr_TI NOT IN {FILTRO_TI} AND t1.Nr_TUC IN (295,'295')
                    """
            BB = pd.read_sql(SQLq, con)
    else:
        if st.session_state.dt_fim >= date.today():
            st.warning(f"  Buscando alternativa para BB, período intercalar de análise. Início em: {datetime.now().strftime('%H:%M:%S')}")
            dt_ARQ = sql.max_arq("AIS", con, Empresa)
            if dt_ARQ:
                SQLq = f"""
                        SELECT t1.Nr_TI, t1.Nr_TUC, t1.Nr_A1, t1.Nr_A3, t1.Cd_UAR, t1.Qtd_AIS as Qtd_AISa
                        FROM AIS t1 WHERE dt_ARQ = {dt_ARQ} AND FLG_PER = "0" AND t1.Nr_TI NOT IN {FILTRO_TI}
                        AND t1.Nr_TUC IN (295,'295')
                        """
                BB = pd.read_sql(SQLq, con)
            elif st:
                st.error('Falha ao importar o arquivo da blindada da base local.')
                return None
            else:
                raise UserWarning('Falha ao importar o arquivo da blindada da base local.')

    TBL_TI = pd.read_csv("tabelas\TBL_TI.csv",sep="|",decimal=',',on_bad_lines='skip',encoding="Latin-1",dtype=str);
    
    if BB['Qtd_AISa'].dtype == 'object':
        BB['Qtd_AISa'] = pd.to_numeric(BB['Qtd_AISa'].str.replace(",","."), errors='coerce')
    
    TOT_MED_AIS = AIS[(AIS['Nr_TUC'] == '295') & (AIS['Cd_UAR'] != 'UAR')
                     & (AIS['Nr_A1'].isin(['01', '1','11','13']))].groupby(['Nr_TI','Nr_A1','Nr_A3'],dropna=False)['Qtd_AIS'].sum().reset_index()
    TOT_MED_AIS = TOT_MED_AIS.merge(TBL_TI, how = 'left', right_on ='Id_TI', left_on = 'Nr_TI')
    TOT_MED_AIS = TOT_MED_AIS[['Nr_TI', 'Nr_A1', 'Nr_A3', 'Txt_Class', 'Txt_Desc', 'Qtd_AIS']]
    TOT_MED_AIS['OBS_SFF'] = 'NO'
    TOT_MED_AIS.loc[TOT_MED_AIS['Txt_Class'].str.startswith("SD"),'OBS_SFF'] = 'VERIFICAR, PARECE SER TUC 205, §62: PRORET 2.3'
    TOT_MED_AIS.loc[TOT_MED_AIS['Txt_Class'].str.startswith("RA"),'OBS_SFF'] = 'APRESENTAR NT SOBRE USO DE MEDIDORES EM REDES DE DISTRIBUIÇÃO'
    TOT_MED_AIS.loc[(TOT_MED_AIS['Nr_A3'] == '0'),'OBS_SFF'] = 'VERIFICAR PORQUE A3 É ZERO'
    TOT_MED_AIS.loc[(TOT_MED_AIS['Nr_TI'] == '92') | (TOT_MED_AIS['Nr_TI'] == '97'),'OBS_SFF'] = 'VERIFICAR, PARECE SER SISTEMA DE PROTEÇÃO, MEDIÇÃO E AUTOMAÇÃO'
    TOT_MED_AIS.to_csv(f"{dir_arq_saida}//ANL_MEDIDORES_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf"{dir_arq_saida}//ANL_MEDIDORES_{Empresa}.csv",
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    TOT_MED_AIS.to_sql(f'ANL_MEDIDORES_{Empresa}', con, if_exists='replace', index=False)
    
    TOT_MED_AIS['TIPO'] = 'ND'
    TOT_MED_AIS.loc[(TOT_MED_AIS['Nr_A1'] == '1') | (TOT_MED_AIS['Nr_A1'] == '01'), 'TIPO'] = 'ELETROMECÂNICO'
    TOT_MED_AIS.loc[(TOT_MED_AIS['Nr_A1'] == '11') | (TOT_MED_AIS['Nr_A1'] == '13'), 'TIPO'] = 'ELETRÔNICO'
    TOT_MED_AIS['Nr_FASES'] = TOT_MED_AIS['Nr_A3'].str[-1]
    TOT_MED_AIS = TOT_MED_AIS[(TOT_MED_AIS['OBS_SFF'] == 'NO') & (TOT_MED_AIS['Nr_FASES'] != '0')].groupby(['TIPO', 'Nr_FASES'],dropna=False)['Qtd_AIS'].sum().reset_index()

    try:
        TOT_MED_COM = COMERC.groupby(['Cd_TIP_MED','Nr_Fases'],dropna=False)['Cd_MED'].count().reset_index()
    except:
        TOT_MED_COM = COMERC.groupby(['Cd_TIP_MED','Nr_fases'],dropna=False)['Cd_MED'].count().reset_index()
        TOT_MED_COM = TOT_MED_COM.rename(columns={'Nr_fases' : 'Nr_Fases'})
    TOT_MED_COM['TIPO'] = 'ELETRÔNICO'
    TOT_MED_COM.loc[TOT_MED_COM['Cd_TIP_MED'] == '0', 'TIPO'] = 'ELETROMECÂNICO'
    TOT_MED_COM = TOT_MED_COM[['TIPO', 'Nr_Fases', 'Cd_MED']]
    TOT_MED_COM.columns = ['TIPO', 'Nr_FASES', 'Qtd_COM']
    TOT_MED_COM = TOT_MED_COM.groupby(['TIPO', 'Nr_FASES'], dropna = False)['Qtd_COM'].sum().reset_index()
    
    TOT_MED_INC = INC[(INC['Nr_TUC'] == '295') & (INC['Cd_UAR'] != 'UAR') & (INC['FLG_ELIG'] == '1') 
                      & (INC['Cd_CONC'] == '1') & (INC['Nr_A1'].isin(['1','11','13']))].groupby(['Nr_TI','Nr_A1','Nr_A3'],dropna=False)['Qtd_AIS'].sum().reset_index()
    TOT_MED_BB = BB[(BB['Nr_TUC']=='295') & (BB['Nr_A1'].isin(['1','11','13']))].groupby(['Nr_TI','Nr_A1',
                                                                             'Nr_A3'],dropna=False)['Qtd_AISa'].sum().reset_index()
    chave = ['Nr_TI','Nr_A1','Nr_A3']
    TST_ESQ = TOT_MED_INC.merge(TOT_MED_BB, how = 'left', on = chave)
    TST_DIR = TOT_MED_INC.merge(TOT_MED_BB, how = 'right', on = chave)
    LAUDO = pd.concat([TST_ESQ, TST_DIR]).drop_duplicates()
    LAUDO.fillna(0, inplace=True)

    LAUDO['Qtd_LAUDO'] = LAUDO['Qtd_AISa'] + LAUDO['Qtd_AIS']
    LAUDO = LAUDO[['Nr_TI','Nr_A1','Nr_A3','Qtd_LAUDO']]

    LAUDO['TIPO'] = 'ND'
    LAUDO.loc[(LAUDO['Nr_A1'] == '1') | (LAUDO['Nr_A1'] == '01'), 'TIPO'] = 'ELETROMECÂNICO'
    LAUDO.loc[(LAUDO['Nr_A1'] == '11') | (LAUDO['Nr_A1'] == '13'), 'TIPO'] = 'ELETRÔNICO'
    LAUDO['Nr_FASES'] = LAUDO['Nr_A3'].str[-1]
    LAUDO = LAUDO[(LAUDO['Nr_FASES'] != '0')].groupby(['TIPO', 'Nr_FASES'],dropna=False)['Qtd_LAUDO'].sum().reset_index()

    TOT_MED_AIS = TOT_MED_AIS.merge(TOT_MED_COM, how = 'outer', on =['TIPO', 'Nr_FASES'])
    TOT_MED_AIS = TOT_MED_AIS.merge(LAUDO, how = 'outer', on =['TIPO', 'Nr_FASES'])
    TOT_MED_AIS = TOT_MED_AIS.fillna(0)

    cols = ['Qtd_AIS', 'Qtd_COM', 'Qtd_LAUDO']  # exemplo
    totais = TOT_MED_AIS[cols].sum()

    TOT_MED_AIS.loc['TOTAL'] = {col: totais[col] for col in cols}
    TOT_MED_AIS.iloc[-1,0] = 'TOTAL'
    TOT_MED_AIS.iloc[-1,1] = 'NA'

    TOT_MED_AIS['DELTA_AIS_COM'] = (
                                        TOT_MED_AIS['Qtd_AIS'] - TOT_MED_AIS['Qtd_COM']
                                    ) / TOT_MED_AIS['Qtd_AIS'].replace(0, np.nan)

    TOT_MED_AIS['DELTA_AIS_COM'] = TOT_MED_AIS['DELTA_AIS_COM'].fillna(np.inf)

    TOT_MED_AIS['DELTA_LAUDO_COM'] = (
                                            TOT_MED_AIS['Qtd_LAUDO'] - TOT_MED_AIS['Qtd_COM']
                                        ) / TOT_MED_AIS['Qtd_LAUDO'].replace(0, np.nan)

    TOT_MED_AIS['DELTA_LAUDO_COM'] = TOT_MED_AIS['DELTA_LAUDO_COM'].fillna(np.inf)

    MED_AIS = TOT_MED_AIS['Qtd_AIS'].sum()
    MED_COM = TOT_MED_AIS['Qtd_COM'].sum()
    MED_LAUDO = TOT_MED_AIS['Qtd_LAUDO'].sum()
    a1 = f"{(MED_AIS - MED_COM) / MED_COM:.2%}".replace(",", "X").replace(".", ",").replace("X", ".")
    a2 = f"{(MED_LAUDO - MED_COM) / MED_COM:.2%}".replace(",", "X").replace(".", ",").replace("X", ".")

    TOT_MED_AIS['OBS_SFF_AIS_COM'] = 'NO'
    if (MED_AIS - MED_COM) / MED_COM >= 0.05:
        TOT_MED_AIS['OBS_SFF_AIS_COM'] = 'Medidores comerciais declarados não sustentam a quantidade de medidores imobilizados'
        TOT_MED_AIS.loc[abs(TOT_MED_AIS['DELTA_AIS_COM']) >= 0.05, 'OBS_SFF_AIS_COM'] = f'Justificar a diferença no TIPO, FASE e global ({a1} de diferença)'
    else:
        TOT_MED_AIS.loc[abs(TOT_MED_AIS['DELTA_AIS_COM']) >= 0.05, 'OBS_SFF_AIS_COM'] = 'Justificar a diferença no TIPO, FASE'

    TOT_MED_AIS['OBS_SFF_LAUDO_COM'] = 'NO'
    if (MED_LAUDO - MED_COM) / MED_COM >= 0.05:
        TOT_MED_AIS['OBS_SFF_LAUDO_COM'] = 'Medidores comerciais declarados não sustentam a quantidade de medidores do laudo'
        TOT_MED_AIS.loc[abs(TOT_MED_AIS['DELTA_LAUDO_COM']) >= 0.05, 'OBS_SFF_LAUDO_COM'] = f'Justificar a diferença no TIPO, FASE e global ({a2} de diferença)'
    else:
        TOT_MED_AIS.loc[abs(TOT_MED_AIS['DELTA_LAUDO_COM']) >= 0.05, 'OBS_SFF_LAUDO_COM'] = 'Justificar a diferença no TIPO, FASE'

    TOT_MED_AIS[['Qtd_AIS', 'Qtd_COM', 'Qtd_LAUDO']] = TOT_MED_AIS[['Qtd_AIS', 'Qtd_COM', 'Qtd_LAUDO']].map(lambda x: locale.format_string('%.2f', x, grouping=True))
    TOT_MED_AIS[['DELTA_AIS_COM','DELTA_LAUDO_COM']] = TOT_MED_AIS[['DELTA_AIS_COM','DELTA_LAUDO_COM']].map(lambda x: '{:.2%}'.format(x))
    TOT_MED_AIS.to_sql('TOT_MED_AIS', con, if_exists='replace', index=False)
    TOT_MED_AIS.to_csv(f"{dir_arq_saida}//ANL_MEDIDORES_TIPO_FASE_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf"{dir_arq_saida}//ANL_MEDIDORES_TIPO_FASE_{Empresa}.csv",
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def anl_AIS_ROA(con, dir_arq_saida, Empresa, st = None):
    import pandas as pd
from datetime import datetime

@monitor_completo(st.session_state.LOGGER)
def anl_AIS_ROA(con, dir_arq_saida, Empresa, st=None):

    def _to_dt(s):
        return pd.to_datetime(s, errors="coerce")
    def _to_num(s):
        if pd.api.types.is_numeric_dtype(s):
            return pd.to_numeric(s, errors="coerce")
        return pd.to_numeric(s.astype(str).str.replace(",", "."), errors="coerce")

    SQLq = f"""SELECT 
                    FLG_PER, 
                    Nr_TI, 
                    Cd_SubODI, 
                    VL_VOC, 
                    Dt_Imob 
                FROM 
                    AIS 
                WHERE 
                    dt_ARQ = ?"""
    
    AIS = sql.imp_tbl_forma_001("AIS", SQLq = SQLq, con=con, Empresa=Empresa)
    AIS["VL_VOC"] = _to_num(AIS["VL_VOC"])
    AIS["Dt_Imob"] = _to_dt(AIS["Dt_Imob"])

    SQLq = f"""SELECT 
                     Ide_RO_Analitico, 
                     Cd_SubODI, 
                     Nr_TI, 
                     VL_tot, 
                     Cd_NG, 
                     Dt_Lcmto 
                FROM 
                    ROA 
                WHERE 
                    dt_ARQ = ?"""
    
    ROA = sql.imp_tbl_forma_001("ROA", SQLq = SQLq, con=con, st=st, Empresa=Empresa)
    ROA["VL_tot"] = _to_num(ROA["VL_tot"])
    ROA["Dt_Lcmto"] = _to_dt(ROA["Dt_Lcmto"])
    ROA["Cd_NG"] = ROA["Cd_NG"].astype(str).fillna("")

    SQLq = f"""SELECT 
                    * 
                FROM 
                    ROS 
                WHERE 
                    dt_ARQ = ?"""
    
    ROS = sql.imp_tbl_forma_001("ROS", SQLq = SQLq, con=con, st=st, Empresa=Empresa) 
    for n in ["Pct_OE", "VL_CA_ST_ODD", "VL_CA_MOP_ODD"]:
        if n in ROS.columns:
            ROS[n] = _to_num(ROS[n])
        else:
            ROS[n] = 0.0

    SQLq = f"""SELECT 
                    * 
                FROM 
                    LST_OBRAS_EMERG 
                WHERE 
                    dt_ARQ = ?"""
    
    OBR_EM = sql.imp_tbl_forma_001("LST_OBRAS_EMERG", SQLq = SQLq, con=con, st=st, Empresa=Empresa)

    ROAp = ROA[["Ide_RO_Analitico", "Cd_SubODI", "Dt_Lcmto", "VL_tot"]].merge(
                    ROS[["Cd_SubODI", "Dt_Inic_Proj", "Dt_Uniti"]], how="outer", on="Cd_SubODI",
                    indicator=True
                )
    for col in ["Dt_Lcmto", "Dt_Inic_Proj", "Dt_Uniti"]:
        ROAp[col] = _to_dt(ROAp[col])
    
    ROAp['OBS_SFF'] = ROAp['_merge'].map({
                                                'both': 'Conciliado',
                                                'left_only': 'Presente no ROA, ausente no ROS: não foi unitizado ainda?',
                                                'right_only': 'Presente no ROS, ausente no ROA: imobilização direta? transitou por ODS?'
                                            })
    ROAp = ROAp.drop(columns=['_merge'])
    ROAp["FLG_FP"] = (
                        (ROAp["Dt_Lcmto"] < ROAp["Dt_Inic_Proj"]) |
                        (ROAp["Dt_Lcmto"] > ROAp["Dt_Uniti"])
                    ).astype(int)

    ROAp.to_csv(
                    f"{dir_arq_saida}//ANL_DTS_FP_LANC_ROS_{Empresa}.csv",
                    sep="|", decimal=",", encoding="Latin-1", index=False, chunksize=100_000
                )
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//ANL_DTS_FP_LANC_ROS_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    ROAp.to_sql("ANL_DTS_FP_LANC_ROS", con, if_exists="replace", index=False)

    ais_per = AIS.query("FLG_PER == '1'").copy()
    TOT_AIS = (
                    ais_per
                    .groupby(["Nr_TI", "Cd_SubODI"], dropna=False, as_index=False)["VL_VOC"]
                    .sum()
                )
    TOT_AIS_dt = (
                    ais_per
                    .groupby(["Nr_TI", "Cd_SubODI"], dropna=False, as_index=False)["Dt_Imob"]
                    .max()
                    .rename(columns={"Dt_Imob": "Dt_Imob"})
                )

    tot_roa_pvt = (
                        ROA.pivot_table(
                            values="VL_tot",
                            index=["Nr_TI", "Cd_SubODI"],
                            columns="Cd_NG",
                            aggfunc="sum",
                            fill_value=0.0,
                        )
                        .reset_index()
                    )

    map_cols = {
                    "1": "VL_UC_ROA",
                    "2": "VL_COM_ROA",
                    "3": "VL_MOP_ROA",
                    "4": "VL_ST_ROA",
                    "5": "VL_JOA_ROA",
                    "6": "VL_OUT_ROA",
                }
    for code, name in map_cols.items():
        if code not in tot_roa_pvt.columns:
            tot_roa_pvt[code] = 0.0
        tot_roa_pvt[name] = tot_roa_pvt[code].astype(float)

    cols_keep = ["Nr_TI", "Cd_SubODI"] + list(map_cols.values())
    TOT_ROA = tot_roa_pvt[cols_keep].copy()
    TOT_ROA["VL_TOT_ROA"] = TOT_ROA[list(map_cols.values())].sum(axis=1)

    TOT_ROA_dt = (
                    ROA.groupby(["Nr_TI", "Cd_SubODI"], as_index=False)
                    .agg(Dt_Lcmto_Min=("Dt_Lcmto", "min"), 
                         Dt_Lcmto_Max=("Dt_Lcmto", "max"))
                )

    TOT_ROA["OBS_SFF_ROA"] = "NO"
    TOT_ROA.loc[(TOT_ROA["VL_UC_ROA"] <= 0) | (TOT_ROA["VL_TOT_ROA"] <= 0), "OBS_SFF_ROA"] = "OBRA É DESPESA"
    TOT_ROA.loc[TOT_ROA["VL_UC_ROA"].eq(TOT_ROA["VL_TOT_ROA"]), "OBS_SFF_ROA"] = "OBRA SOMENTE COM UC, JUSTIFICAR"
    mask_share = (TOT_ROA["VL_UC_ROA"] / TOT_ROA["VL_TOT_ROA"]).fillna(0) <= 0.05
    TOT_ROA.loc[mask_share & TOT_ROA["VL_UC_ROA"].gt(0), "OBS_SFF_ROA"] = \
        "OBRA COM CA/COM SIGNIFICATIVO, JUSTIFICAR PORQUE SERIA INVESTIMENTO"

    RO_TOT = pd.merge(TOT_ROA, ROS, on="Cd_SubODI", how="outer")
    RO_TOT = pd.merge(RO_TOT, TOT_ROA_dt, on=["Nr_TI", "Cd_SubODI"], how="left")

    for c in ["Dt_Inic_Proj", "Dt_Uniti", "Dt_Energ"]:
        if c in RO_TOT.columns:
            RO_TOT[c] = _to_dt(RO_TOT[c])
        else:
            RO_TOT[c] = pd.NaT

    LST_ITENS = ["3", "7", "12"]
    RO_TOT["OBS_SFF_ROS"] = "NO"

    RO_TOT.loc[
                    (RO_TOT["Dt_Inic_Proj"].notna()) & (RO_TOT["Dt_Lcmto_Min"].notna()) &
                    ((RO_TOT["Dt_Inic_Proj"] - RO_TOT["Dt_Lcmto_Min"]).dt.days > 0),
                    "OBS_SFF_ROS"
                ] = "Verificar data de início do projeto, posterior ao primeiro lançamento do ROA"

    RO_TOT.loc[
                (RO_TOT["Dt_Uniti"].notna()) & (RO_TOT["Dt_Lcmto_Max"].notna()) &
                ((RO_TOT["Dt_Uniti"] - RO_TOT["Dt_Lcmto_Max"]).dt.days > 90),
                "OBS_SFF_ROS"
            ] = "Verificar data de unitização, superior a 90 dias do último lançamento do ROA"

    RO_TOT.loc[
                (RO_TOT["Dt_Uniti"].notna()) & (RO_TOT["Dt_Energ"].notna()) &
                ((RO_TOT["Dt_Uniti"] - RO_TOT["Dt_Energ"]).dt.days > 90),
                "OBS_SFF_ROS"
            ] = "Verificar data de unitização, superior a 90 dias da energização"

    for c in ["VL_CA_ST_ODD", "VL_CA_MOP_ODD"]:
        if c not in RO_TOT.columns:
            RO_TOT[c] = 0.0
    RO_TOT.loc[
                RO_TOT["Cd_Tipo_Obra"].astype(str).isin(LST_ITENS) &
                RO_TOT["VL_CA_ST_ODD"].eq(0) & RO_TOT["VL_CA_MOP_ODD"].eq(0),
                "OBS_SFF_ROS"
            ] = "Deveria haver ODD, verifique justificativa empresa"


    RO_TOT["Pct_OE"] = RO_TOT.get("Pct_OE", 0.0).fillna(0.0)
    RO_TOT["VL_OE"] = (RO_TOT.get("VL_TOT_ROA", 0.0).fillna(0.0) * RO_TOT["Pct_OE"]).astype(float)

    RO_TOT = RO_TOT.merge(TOT_AIS, on = ["Nr_TI", "Cd_SubODI"], how="right")
    RO_TOT = RO_TOT.merge(TOT_AIS_dt, on = ["Nr_TI", "Cd_SubODI"], how="right")
    RO_TOT["Dt_Imob"] = _to_dt(RO_TOT["Dt_Imob"])

    RO_TOT["VL_TOT_ROA"] = RO_TOT.get("VL_TOT_ROA", 0.0).fillna(0.0)
    RO_TOT["DELTA"] = (RO_TOT["VL_VOC"] - RO_TOT["VL_TOT_ROA"]) / RO_TOT["VL_TOT_ROA"].replace(0, pd.NA)
    RO_TOT["DELTA"] = RO_TOT["DELTA"].fillna(0.0)

    RO_TOT["OBS_SFF_AIS"] = "NO"
    RO_TOT.loc[RO_TOT.get("VL_UC_ROA").isna(), "OBS_SFF_AIS"] = "Ausente no ROA, averiguar se é imobilização direta."
    RO_TOT.loc[
                    RO_TOT["VL_UC_ROA"].notna() &
                    (RO_TOT["Dt_Uniti"].notna()) & (RO_TOT["Dt_Imob"].notna()) &
                    ((RO_TOT["Dt_Uniti"] - RO_TOT["Dt_Imob"]).dt.days != 0),
                    "OBS_SFF_AIS"
                ] = "Verificar data imobilização informada no ROS, não confere com AIS"
    RO_TOT.loc[
                RO_TOT["VL_UC_ROA"].notna() & (RO_TOT["DELTA"].abs() > 0.05),
                "OBS_SFF_AIS"
            ] = "Justificar a variação do valor do AIS para ROA"

    if not OBR_EM.empty:
        OBR_EM = OBR_EM.rename(columns = {'DT_CHEG': 'Dt_CHEG', 'DT_REST': 'Dt_REST'})
        merge_oemg = (
                        ROS.merge(OBR_EM, how="inner", left_on="Cd_SubODI", right_on="Nr_Ordem")
                        [["Cd_SubODI", "Dt_CHEG", "Dt_REST", "Txt_OCORR", "Txt_Causa"]]
                    )
        RO_TOT = RO_TOT.merge(merge_oemg, how="left", on="Cd_SubODI")
        for n in ["Txt_OCORR", "Txt_Causa"]:
            RO_TOT[n] = RO_TOT[n].fillna("NO")
        for dcol in ["Dt_CHEG", "Dt_REST"]:
            RO_TOT[dcol] = _to_dt(RO_TOT[dcol])

        RO_TOT["OBS_SFF_OBR_EMERG"] = "NO"
        is_emerg = RO_TOT["Txt_Causa"].ne("NO")
        tipo_emerg = RO_TOT.get("Cd_Tipo_Obra", "").astype(str).isin(["3", "7", "12"])
        dif_Imob_REST = (RO_TOT["Dt_Imob"] - RO_TOT["Dt_REST"]).dt.days

        RO_TOT.loc[is_emerg & tipo_emerg & (dif_Imob_REST > 29),
                "OBS_SFF_OBR_EMERG"] = "Verificar data imobilização informada no ROS, não confere com data de Obras Emergenciais"
        RO_TOT.loc[is_emerg & (~tipo_emerg),
                "OBS_SFF_OBR_EMERG"] = "Verificar tipo de obra (teria de ser manutenção), não confere com dados de Obras Emergenciais"
        RO_TOT.loc[is_emerg & (~tipo_emerg) & (dif_Imob_REST > 29),
                "OBS_SFF_OBR_EMERG"] = "Verificar data imobilização informada no ROS e tipo de obra (teria de ser manutenção), não confere com dados de Obras Emergenciais"

    RO_TOT.to_sql("ANL_ROA_ROS_AIS_OEMG_CMP", con, if_exists="replace", index=False)
    RO_TOT.to_csv(
                        f"{dir_arq_saida}//ANL_ROA_ROS_AIS_OEMG_CMP_{Empresa}.csv",
                        sep="|", decimal=",", encoding="Latin-1", index=False, chunksize=100_000
                    )
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//ANL_ROA_ROS_AIS_OEMG_CMP_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)

    return "OK"

@monitor_completo(st.session_state.LOGGER)
def anl_LST_TUC(con, dir_arq_saida, Empresa, st = None):
    dt_ARQ = sql.max_arq("ROA", con, Empresa)
    if dt_ARQ:
        SQLq = f"""
            SELECT t1.Nr_TI, t1.Cd_SubODI, t1.Nr_TUC, t1.Qtd, t1.VL_tot
            FROM ROA t1 WHERE t1.Cd_NG = '1' AND t1.dt_ARQ = {dt_ARQ}
            """
        ROA = pd.read_sql(SQLq, con)
        ROA['VL_tot'] = pd.to_numeric(ROA['VL_tot'].replace(",","."), errors = 'coerce')
        ROA['Qtd'] = pd.to_numeric(ROA['Qtd'].replace(",","."), errors = 'coerce')
    else:
        if st:
            st.error('Falha ao importar o arquivo ROA da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ROA da base local.')

    TBL_TI = bsc_dados_reg('TBL_TI')
    TBL_TUC = bsc_dados_reg('TBL_TUC')
    dic = dict(zip(TBL_TUC['Ide_TUC'], TBL_TUC['Txt_Desc']))
    dic['000'] = 'Erro de preenchimento no ROA'

    ROA = ROA.sort_values(by=['Nr_TI', 'Cd_SubODI'])
    ROA_gr = ROA.groupby(['Nr_TI', 'Cd_SubODI', 'Nr_TUC'],dropna=False)[['Qtd', 'VL_tot']].sum().reset_index()

    df = ROA_gr.copy()
    df['Chave'] = df['Nr_TUC'].astype(str).str.zfill(3)
    df['Chave'] = df.groupby(['Nr_TI', 'Cd_SubODI'],dropna=False)['Chave'].transform(lambda x: ''.join(x))

    tbl_AX = df['Chave'].copy().drop_duplicates().reset_index()
    tbl_AX['Cd_GRP'] = 1
    tbl_AX['Cd_GRP'] = tbl_AX['Cd_GRP'].cumsum()
    df = df.groupby(['Nr_TI', 'Cd_SubODI', 'Chave'],dropna=False)[['Qtd','VL_tot']].sum().reset_index()
    df = df.merge(tbl_AX, on ='Chave', how = 'left')[['Nr_TI', 'Cd_SubODI', 'Cd_GRP', 'Chave', 'Qtd','VL_tot']]
    
    tam = int(df['Chave'].str.len().max()/3)
    for i in range(tam):
        nm_col = f'TUC{i}'
        df[nm_col] = [text[i*3:i*3+3] if len(text) >= (i*3+3) else 'ND' for text in df['Chave']]
        df[nm_col] = df[nm_col].replace(dic)
    df = df.merge(TBL_TI, left_on = 'Nr_TI', right_on = 'Id_TI', how = 'left').drop(columns=['Chave','Nr_TI', 'Id_TI', 'TP_JOA'])
    
    df.to_sql('ANL_LST_TUC', con, if_exists='replace', index=False)
    df.to_csv(f"{dir_arq_saida}//ANL_LST_TUC_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//ANL_LST_TUC_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def ger_LSTS(con, dir_arq_saida, Empresa, st = None):

    SQLq = f"""
            SELECT DISTINCT t1.Nr_TI, t1.COD_ITEM, SUM(t1.Qtd) AS Qtd, SUM(t1.VL_tot) AS VL_tot
            FROM ROA t1 WHERE t1.dt_ARQ = ? AND (t1.Cd_NG = '1' OR t1.Cd_NG = '2')
            GROUP BY t1.Nr_TI, t1.COD_ITEM
            """
    ROA = sql.imp_tbl_forma_001("ROA", SQLq, con, st, Empresa)
    ROA['VL_tot'] = pd.to_numeric(ROA['VL_tot'].replace(",","."), errors = 'coerce')
    ROA['Qtd'] = pd.to_numeric(ROA['Qtd'].replace(",","."), errors = 'coerce')

    LST_MAT = sql.imp_tbl_forma_001("LST_MAT", SQLq=None, con=con, st=st, Empresa=Empresa)
    TBL_TI = bsc_dados_reg('TBL_TI')
    LST_MAT_AJ = (
                    ROA.merge(
                        LST_MAT,
                        how='outer',
                        on='COD_ITEM',
                        indicator=True
                    )
                    .merge(
                        TBL_TI,
                        left_on='Nr_TI',
                        right_on='Id_TI',
                        how='left'
                    )
                )
    
    LST_MAT_AJ = LST_MAT_AJ.rename(columns={'_merge': 'Marcacao'})
    LST_MAT_AJ['Marcacao'] = LST_MAT_AJ['Marcacao'].map({
                                                            'both': 'Conciliado',
                                                            'left_only': 'Presente no ROA, ausente na Lista',
                                                            'right_only': 'Presente na Lista, ausente no ROA'
                                                        })

    LST_MAT_AJ = LST_MAT_AJ[
                                ['Nr_TI', 'Txt_Class', 'Txt_Desc',
                                'COD_ITEM', 'DESCR_ITEM', 'Nr_FC',
                                'CD_Nm_Reg', 'CD_Nm_Reg_ST', 'Qtd', 'VL_tot', 'Marcacao']
                            ]
    
    LST_MAT_AJ['Vl_Default_Man'] = 1 
    LST_MAT_AJ['Vl_Default_Inv'] = 1
    LST_MAT_AJ['Txt_OBS_SFF'] = [[] for _ in range(len(LST_MAT_AJ))]

    def erro_msg(df, cond, msg):
        df.loc[cond, 'Txt_OBS_SFF'] = df.loc[cond, 'Txt_OBS_SFF'].apply(lambda x: x + [msg])

    erro_msg(LST_MAT_AJ, LST_MAT_AJ['Marcacao'] == 'Presente no ROA, ausente na Lista', 'Presente no ROA, ausente na Lista')
    erro_msg(LST_MAT_AJ, LST_MAT_AJ['Marcacao'] == 'Presente na Lista, ausente no ROA', 'Presente na Lista, ausente no ROA')
    erro_msg(LST_MAT_AJ, LST_MAT_AJ['Qtd'] <= 0, 'Justificar quantidade zerada')
    erro_msg(LST_MAT_AJ, LST_MAT_AJ['VL_tot'] < 0, 'Justificar porque extorno é maior do que lançamento')
    erro_msg(LST_MAT_AJ, LST_MAT_AJ['Txt_Class'] == 'GER', 'Justificar esse material de geração')
    cond = ~ LST_MAT_AJ['DESCR_ITEM'].str.contains(r'\b[A-Za-z]{4,}\b', regex=True, na=False)
    erro_msg(LST_MAT_AJ, cond, "Verifique a descrição")

    LST_BSC = ['poste', 'haste', 'secc', 'isolador', 'pino', 'chave', 'cruzeta', 'trd', 'trf', 'trafo',
               'transformador', 'capacitor', 'raio', 'pára', 'para-raio', 'cerca', 'cabo', 'condutor',
               'religador', 'regulador']
    BUSCA = '|'.join([f'{item}' for item in LST_BSC])
    BUSCA = '(?i)' + BUSCA

    LST_MAT_AJ['TESTE_BSC'] = LST_MAT_AJ['DESCR_ITEM'].str.contains(BUSCA, na=False)
    erro_msg(LST_MAT_AJ, (LST_MAT_AJ['TESTE_BSC']) & (LST_MAT_AJ['CD_Nm_Reg'].isnull()), 
             'Verificar se deveria informar CD_Nm_Reg')
    
    LST_BSC = [' ip ', 'fotoelétrico', 'fotoeletrico', 'pública', 'publica', 'lumin']
    BUSCA = '|'.join([f'{item}' for item in LST_BSC])
    BUSCA = '(?i)' + BUSCA
    LST_MAT_AJ['TESTE_BSC'] = LST_MAT_AJ['DESCR_ITEM'].str.contains(BUSCA, na = False)
    erro_msg(LST_MAT_AJ, LST_MAT_AJ['TESTE_BSC'], 'Verificar se é IP')
    erro_msg(LST_MAT_AJ, LST_MAT_AJ['COD_ITEM'].isnull(), 'Verificar porque não foi informado o código')
    LST_MAT_AJ['Txt_OBS_SFF'] = LST_MAT_AJ['Txt_OBS_SFF'].apply(lambda msg: '; '.join(msg) if msg else '')
    
    LST_MAT_AJ = LST_MAT_AJ.drop_duplicates(subset = ['Nr_TI', 'COD_ITEM'])
    crit1 = (LST_MAT_AJ['CD_Nm_Reg'] != LST_MAT_AJ['CD_Nm_Reg_ST']) & LST_MAT_AJ['CD_Nm_Reg_ST'].isnull()
    LST_MAT_AJ.loc[crit1, 'CD_Nm_Reg_ST'] = LST_MAT_AJ['CD_Nm_Reg']
    LST_MAT_AJ[['Nr_TI', 'Txt_Class', 'Txt_Desc', 'COD_ITEM', 'DESCR_ITEM', 'Nr_FC', 
                'CD_Nm_Reg', 'Qtd', 'VL_tot','Vl_Default_Man', 'Vl_Default_Inv',
                'Txt_OBS_SFF','CD_Nm_Reg_ST']].to_csv(f"{dir_arq_saida}//LST_MAT_AJ_{Empresa}.csv", 
                                                      sep="|", 
                                                      decimal=',', 
                                                      encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//LST_MAT_AJ_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    SQLq =  f"""
                SELECT DISTINCT t1.Nr_TI, t1.COD_ITEM, t1.Cd_Cls_Custo, SUM(t1.Qtd) AS Qtd, SUM(t1.VL_tot) AS VL_tot
                FROM ROA t1 WHERE t1.Cd_NG = '4' AND t1.dt_ARQ = ? GROUP BY t1.Nr_TI, t1.COD_ITEM, t1.Cd_Cls_Custo
                """
    ROA = sql.imp_tbl_forma_001("ROA", SQLq, con, st, Empresa)
    ROA['VL_tot'] = pd.to_numeric(ROA['VL_tot'].replace(",","."), errors = 'coerce')
    ROA['Qtd'] = pd.to_numeric(ROA['Qtd'].replace(",","."), errors = 'coerce')

    LST_SER = sql.imp_tbl_forma_001("LST_SERV", SQLq=None, con=con, st=st, Empresa=Empresa)
    
    LST_SER_AJ = (
                    ROA.merge(
                        LST_SER,
                        how='outer',
                        on='COD_ITEM',
                        indicator=True
                    )
                    .merge(
                        TBL_TI,
                        left_on='Nr_TI',
                        right_on='Id_TI',
                        how='left'
                    )
                )
    
    LST_SER_AJ = LST_SER_AJ.rename(columns={'_merge': 'Marcacao'})
    LST_SER_AJ['Marcacao'] = LST_SER_AJ['Marcacao'].map({
                                                            'both': 'Conciliado',
                                                            'left_only': 'Presente no ROA, ausente na Lista',
                                                            'right_only': 'Presente na Lista, ausente no ROA'
                                                        })

    LST_SER_AJ = LST_SER_AJ[
                                ['Nr_TI', 'Txt_Class', 'Txt_Desc', 'COD_ITEM', 
                                 'DESCR_ITEM', 'Cd_Cls_Custo', 'CD_Nm_Reg_ST', 'Qtd', 'VL_tot', 
                                 'Marcacao']
                            ]
    
    LST_SER_AJ['Vl_Default_Man'] = 1 
    LST_SER_AJ['Vl_Default_Inv'] = 1

    LST_SER_AJ['Txt_OBS_SFF'] = [[] for _ in range(len(LST_SER_AJ))]
    erro_msg(LST_SER_AJ, LST_SER_AJ['Marcacao'] == 'Presente no ROA, ausente na Lista', 'Presente no ROA, ausente na Lista')
    erro_msg(LST_SER_AJ, LST_SER_AJ['Marcacao'] == 'Presente na Lista, ausente no ROA', 'Presente na Lista, ausente no ROA')
    erro_msg(LST_SER_AJ, LST_SER_AJ['Qtd'] <= 0, 'Justificar quantidade zerada')
    erro_msg(LST_SER_AJ, LST_SER_AJ['VL_tot'] < 0, 'Justificar porque extorno é maior do que lançamento')
    erro_msg(LST_SER_AJ, LST_SER_AJ['Txt_Class'] == 'GER', 'Justificar esse serviço de geração')
    erro_msg(LST_SER_AJ, LST_SER_AJ['COD_ITEM'].isnull(), 'Verificar porque não foi informado o código')
    cond = ~ LST_SER_AJ['DESCR_ITEM'].str.contains(r'\b[A-Za-z]{4,}\b', regex=True, na=False)
    erro_msg(LST_SER_AJ, cond, "Verifique a descrição")

    LST_SER_AJ = LST_SER_AJ.drop_duplicates(subset = ['Nr_TI', 'COD_ITEM', 'Cd_Cls_Custo'])
    LST_SER_AJ['Txt_OBS_SFF'] = LST_SER_AJ['Txt_OBS_SFF'].apply(lambda msg: '; '.join(msg) if msg else '')
    LST_SER_AJ[['Nr_TI', 'Txt_Class', 'Txt_Desc', 'COD_ITEM', 'DESCR_ITEM', 
                'Cd_Cls_Custo', 'Qtd', 'VL_tot', 'Vl_Default_Man', 'Vl_Default_Inv', 
                'Txt_OBS_SFF','CD_Nm_Reg_ST']].to_csv(f"{dir_arq_saida}//LST_SER_AJ_{Empresa}.csv", 
                                                                 sep="|", 
                                                                 decimal=',', 
                                                                 encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//LST_SER_AJ_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    LST_SER_AJ[
                    [
                        'Nr_TI', 'Txt_Class', 'Txt_Desc', 'COD_ITEM', 'DESCR_ITEM',
                        'Cd_Cls_Custo', 'Qtd', 'VL_tot', 'Vl_Default_Man', 'Vl_Default_Inv',
                        'Txt_OBS_SFF', 'CD_Nm_Reg_ST'
                    ]
              ].to_sql(
                            name='LST_SER_AJ',
                            con=con,
                            if_exists='replace',
                            index=False
                        )
    LST_MAT_AJ[
                    [
                        'Nr_TI', 'Txt_Class', 'Txt_Desc', 'COD_ITEM', 'DESCR_ITEM', 'Nr_FC', 
                        'CD_Nm_Reg', 'Qtd', 'VL_tot','Vl_Default_Man', 'Vl_Default_Inv',
                        'Txt_OBS_SFF','CD_Nm_Reg_ST'
                    ]
                ].to_sql(
                            name='LST_MAT_AJ', 
                            con=con, 
                            if_exists='replace', 
                            index=False
                        )
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def processar_datas_limites(ROA: pd.DataFrame, dict_lim: dict) -> pd.DataFrame:
    # Converte colunas
    df = ROA.copy()
    df['Dt_Lcmto'] = pd.to_datetime(df['Dt_Lcmto'], errors='coerce')
    df['Nr_TI'] = pd.to_numeric(df['Nr_TI'], errors='coerce')
    
    # Inicializa as colunas
    df['DT_MIN'] = df['Dt_Lcmto']
    df['DT_MAX'] = df['Dt_Lcmto']

    # Define regras de faixa e limites
    regras = [
        ((df['Nr_TI'].between(30, 34)) | (df['Nr_TI'].between(50, 54)), dict_lim['SE']),
        ((df['Nr_TI'].between(35, 39)) | (df['Nr_TI'].between(55, 69)), dict_lim['LD']),
        ((df['Nr_TI'].between(42, 44)), dict_lim['RDS']),
        ((df['Nr_TI'].isin([40, 41])), dict_lim['RDA'])
    ]

    # Aplica regras
    for condicao, limite in regras:
        delta = pd.Timedelta(days=limite)
        df.loc[condicao, 'DT_MIN'] = df['Dt_Lcmto'] - delta
        df.loc[condicao, 'DT_MAX'] = df['Dt_Lcmto'] + delta

    # Default para os demais
    default_delta = pd.Timedelta(days=dict_lim['DEMAIS'])
    df.loc[df['DT_MIN'] == df['Dt_Lcmto'], 'DT_MIN'] = df['Dt_Lcmto'] - default_delta
    df.loc[df['DT_MAX'] == df['Dt_Lcmto'], 'DT_MAX'] = df['Dt_Lcmto'] + default_delta

    # Seleciona e ordena
    df = df[['Cd_SubODI', 'DT_MIN', 'DT_MAX']].drop_duplicates()
    df = df.sort_values(by=['Cd_SubODI', 'DT_MIN']).reset_index(drop=True)

    # Cálculo de VL_JAN
    df['VL_JAN'] = ((df['DT_MAX'] - df['DT_MIN']).dt.days / 2).apply(np.floor)

    # Cálculo de 'vc'
    df['vc'] = (df['DT_MAX'].shift() - df['DT_MIN']).dt.days
    df.loc[df['Cd_SubODI'] != df['Cd_SubODI'].shift(), 'vc'] = 1
    df.loc[(df['Cd_SubODI'] == df['Cd_SubODI'].shift()) & (df['vc'] >= 0), 'vc'] = 0
    df.loc[(df['Cd_SubODI'] == df['Cd_SubODI'].shift()) & (df['vc'] < 0), 'vc'] = 1

    # Datas relativas DT_MINr e DT_MAXr
    df['DT_MINr'] = df['DT_MIN'].where(df['vc'] == 1, df['DT_MIN'].shift())
    df['DT_MAXr'] = df['DT_MAX']

    return df

@monitor_completo(st.session_state.LOGGER)
def ajustar_dados_final(df: pd.DataFrame) -> pd.DataFrame:
    CLC_DT_PER = df.copy()

    DT_MINant = CLC_DT_PER.iloc[0, 1]
    DT_MAXant = CLC_DT_PER.iloc[0, 2]
    soma = 1

    DT_MINr = [DT_MINant]
    DT_MAXr = [DT_MAXant]
    vc_acumulado = [soma]

    for i in range(1, len(CLC_DT_PER)):
        atual_vc = CLC_DT_PER.iloc[i, 4]
        atual_subodi = CLC_DT_PER.iloc[i, 0]
        anterior_subodi = CLC_DT_PER.iloc[i - 1, 0]

        if atual_vc == 0:
            DT_MINr.append(DT_MINant)
        else:
            DT_MINant = CLC_DT_PER.iloc[i, 1]
            DT_MAXant = CLC_DT_PER.iloc[i, 2]
            DT_MINr.append(DT_MINant)

        if atual_subodi != anterior_subodi:
            soma = 1
        else:
            soma += atual_vc
        vc_acumulado.append(soma)

    CLC_DT_PER.iloc[:, 4] = vc_acumulado
    CLC_DT_PER.iloc[:, 5] = DT_MINr

    CLC_DT_PER = CLC_DT_PER.sort_values(by=['DT_MINr','DT_MAXr'])
    Cd_SUBODI = CLC_DT_PER[['Cd_SubODI','VL_JAN']].drop_duplicates()
    Cd_SUBODI = Cd_SUBODI.groupby(['Cd_SubODI'], dropna=False).size().reset_index(name='cnt')
    LST_SUBODI = Cd_SUBODI[Cd_SUBODI['cnt']>1]['Cd_SubODI'].drop_duplicates().to_list()
    CLC_DT_PER['FLG_MISTA'] = 0
    CLC_DT_PER.loc[CLC_DT_PER['Cd_SubODI'].isin(LST_SUBODI),'FLG_MISTA'] = 1
    CLC_DT_PER = CLC_DT_PER.drop_duplicates(subset=['Cd_SubODI', 'vc'], keep='last')

    return CLC_DT_PER

@monitor_completo(st.session_state.LOGGER)
def configurar_sqlite_pragmas(conexao, modo='leitura'):
    """
    Aplica PRAGMAs otimizados para leitura ou leitura/escrita no SQLite.

    Parâmetros:
        conexao: conexão sqlite3 ativa.
        modo (str): 'leitura' ou 'escrita'.
    """
    if modo == 'leitura':
        conexao.execute("PRAGMA synchronous = OFF")
        conexao.execute("PRAGMA journal_mode = WAL")
    elif modo == 'escrita':
        conexao.execute("PRAGMA synchronous = NORMAL")
        conexao.execute("PRAGMA journal_mode = WAL")
    else:
        raise ValueError("Modo deve ser 'leitura' ou 'escrita'")

    conexao.execute("PRAGMA temp_store = MEMORY")
    conexao.execute("PRAGMA cache_size = 100000")

@monitor_completo(st.session_state.LOGGER)
def configurar_sqlite_para_desempenho(con):
    con.execute("PRAGMA synchronous = OFF")
    con.execute("PRAGMA journal_mode = WAL")
    con.execute("PRAGMA temp_store = MEMORY")
    con.execute("PRAGMA cache_size = 100000")

@monitor_completo(st.session_state.LOGGER)
def anl_FLXTMP(con, dir_arq_saida, Empresa, st = None, df_CARACT = pd.DataFrame()):
    saida = Path(dir_arq_saida)
    saida.mkdir(parents=True, exist_ok=True)

    Cd_EMP = sql.bsc_cd_aneel(Empresa)
    if not Cd_EMP:
        if st is not None:
            st.error('Falha ao buscar o código da empresa na Aneel.')
            return None
        raise ValueError('Falha ao buscar o código da empresa na Aneel.')
    
    configurar_sqlite_pragmas(con, modo='leitura')
    cursor = con.cursor()
    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_roa_dt_arq_cd_ng ON ROA(dt_ARQ, Cd_NG)
                  """)
    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_roa_arq_ng_subodi ON ROA(dt_ARQ, Cd_NG, Cd_SubODI)
                    """)
    con.commit()
    
    dt_ARQ = sql.max_arq("ROA", con, Empresa)
    if dt_ARQ:
        SQLq = """
                SELECT DISTINCT Nr_TI, Cd_SubODI, Dt_Lcmto
                FROM ROA
                WHERE Cd_NG = ? AND dt_ARQ = ?
               """
        ROA = pd.read_sql(SQLq, con, params=('1', dt_ARQ))
    else:
        if st:
            st.error('Falha ao importar o arquivo ROA da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ROA da base local.')

    GRPS = pd.read_csv("tabelas//TBL_GRUPOS.csv",sep="|",decimal=',',on_bad_lines='skip',encoding="Latin-1");
    filtro = GRPS['Cd_ANEEL'] == int(Cd_EMP)
    grps_empresa = GRPS[filtro]
    if grps_empresa.empty:
        raise ValueError(f"Nenhum dado encontrado para Cd_ANEEL = {Cd_EMP}")

    registro_mais_recente = grps_empresa[grps_empresa['DT_REF'] == grps_empresa['DT_REF'].max()]
    NR_GR = registro_mais_recente['Nr_GRUPO'].iloc[-1]
    dict_lim = {
                    'RDA': 30 * (5 if NR_GR in [1, 2, 3] else 3),
                    'RDS': 30 * (6 if NR_GR in [1, 2, 3] else 4),
                    'LD':  30 * (12 if NR_GR in [1, 2, 3] else 14),
                    'SE':  30 * (9 if NR_GR in [1, 2, 3] else 8),
                    'SM':  90,
                    'DEMAIS': 90
                }
    
    CLC_DT_PER = processar_datas_limites(ROA, dict_lim)
    CLC_DT_PER = ajustar_dados_final(CLC_DT_PER)
    configurar_sqlite_pragmas(con, modo='escrita')
    CLC_DT_PER.to_sql('DT_FLX_TEMP', con, if_exists='replace', index=False)
    CLC_DT_PER.to_csv(f"{dir_arq_saida}//DT_FLX_TEMP_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//DT_FLX_TEMP_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
        
    DD_LMT_ROA = pd.pivot_table(CLC_DT_PER, values = ['DT_MINr', 'DT_MAXr'], columns = ['vc'], index = ['Cd_SubODI']).reset_index()
    DD_LMT_ROA.columns = [ n + str(l).replace(".0","") for n,l  in DD_LMT_ROA.columns.to_list()]

    min_cols = sorted([col for col in DD_LMT_ROA.columns if col.startswith('DT_MINr')],
                    key=lambda x: int(x.removeprefix('DT_MINr')))
    max_cols = sorted([col for col in DD_LMT_ROA.columns if col.startswith('DT_MAXr')],
                    key=lambda x: int(x.removeprefix('DT_MAXr')))

    DD_LMT_ROA[min_cols] = DD_LMT_ROA[min_cols].ffill(axis=1)
    DD_LMT_ROA[max_cols] = DD_LMT_ROA[max_cols].ffill(axis=1)

    DD_LMT_ROA.to_sql('DD_LMT_ROA', con, if_exists='replace', index=False)
    DD_LMT_ROA.to_csv(f"{dir_arq_saida}//DD_LMT_ROA_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//DD_LMT_ROA_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
        
    configurar_sqlite_pragmas(con, modo='leitura')
    dt_ARQ = sql.max_arq("ROA", con, Empresa)
    if dt_ARQ:
        try:
            SQLq = """
                    SELECT Ide_RO_Analitico, Cd_SubODI, Dt_Lcmto, VL_tot
                    FROM ROA
                    WHERE dt_ARQ = ?
                """
            ROA = pd.read_sql(SQLq, con, params=(dt_ARQ,))
        except:
            SQLq = """
                    SELECT Id_ROA_Analitico AS Ide_RO_Analitico, Cd_SubODI, Dt_Lcmto, VL_tot
                    FROM ROA
                    WHERE dt_ARQ = ?
                """
            ROA = pd.read_sql(SQLq, con, params=(dt_ARQ,))
        ROA['VL_tot'] = pd.to_numeric(ROA['VL_tot'].astype(str).str.replace(',', '.', regex=False), errors='coerce')
    else:
        if st:
            st.error('Falha ao importar o arquivo ROA da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ROA da base local.')

    ROA = ROA.merge(DD_LMT_ROA, how='left', on='Cd_SubODI')
    status = np.zeros(len(ROA), dtype=bool)
    ROA['Dt_Lcmto'] = pd.to_datetime(ROA['Dt_Lcmto'], errors = 'coerce')

    vc_max = int(CLC_DT_PER['vc'].max())
    for n in range(1, vc_max + 1):
        col_min = f'DT_MINr{n}'
        col_max = f'DT_MAXr{n}'
        in_between = ROA['Dt_Lcmto'].between(ROA[col_min], ROA[col_max])
        status |= in_between  
        status |= (ROA['VL_tot'] < 0)

    ROA['FLG_TMP'] = np.where(status, 1, 0)
    
    configurar_sqlite_para_desempenho(con)
    safe_chunksize = 999 // len(ROA.columns)
    ROA.to_sql(
                    'LCMTO_FLX_TEMP',
                    con,
                    if_exists='replace',
                    index=False,
                    method='multi',
                    chunksize=safe_chunksize
                )
    ROA.to_csv(
                    f"{dir_arq_saida}/LCMTO_FLX_TEMP_{Empresa}.csv",
                    sep="|",
                    decimal=',',
                    encoding="Latin-1",
                    index=False,
                    chunksize=100000
                )
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}/LCMTO_FLX_TEMP_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    ROA['VL_tot'] = ROA['VL_tot'].fillna(0)
    RES = (
                ROA.loc[ROA['FLG_TMP'] == 0, ['Cd_SubODI', 'VL_tot']]
                .groupby('Cd_SubODI', dropna=False, sort=False)['VL_tot']
                .sum()
                .reset_index()
            )
    RES.to_sql('AJST_FLX_TEMP', con, if_exists='replace', index=False)
    RES.to_csv(f"{dir_arq_saida}//AJST_FLX_TEMP_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}/AJST_FLX_TEMP_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)

    con.execute("CREATE INDEX IF NOT EXISTS idx_roa_dt_arq_ti_cd_subodi ON ROA(dt_ARQ, Nr_TI, Cd_SubODI)")
    configurar_sqlite_pragmas(con, modo='leitura')
    dt_ARQ = sql.max_arq("ROA", con, Empresa)
    if dt_ARQ:
        SQLq = f"""
            SELECT 
                t1.Nr_TI, 
                t1.Cd_SubODI, 
                MIN(t1.Dt_Lcmto) AS INI_ROA, 
                MAX(t1.Dt_Lcmto) AS FIM_ROA
            FROM 
                ROA t1 
            WHERE 
                t1.dt_ARQ = ? 
            GROUP BY 
                t1.Nr_TI, 
                t1.Cd_SubODI;
            """
        ROA = pd.read_sql(SQLq, con, params=(dt_ARQ,))

        SQLq = f"""
            SELECT 
                t1.Nr_TI, 
                t1.Cd_SubODI, 
                t1.Dt_Lcmto, 
                sum(t1.VL_tot) as VL_tot, 
                sum(t1.Qtd) as Qtd
            FROM 
                ROA t1 
            WHERE 
                t1.dt_ARQ = ? AND  (t1.Nr_TI = '96' OR t1.Nr_TI = '93') 
            GROUP BY 
                t1.Nr_TI, 
                t1.Cd_SubODI, 
                t1.Dt_Lcmto;
            """
        ROAdt = pd.read_sql(SQLq, con, params=(dt_ARQ,))

        SQLq = f"""
            SELECT 
                t1.Nr_TI, 
                t1.Cd_SubODI, 
                sum(t1.VL_tot) as VL_tot
            FROM 
                ROA t1 
            WHERE 
                t1.dt_ARQ = ?
            GROUP BY 
                t1.Nr_TI, 
                t1.Cd_SubODI;
            """
        ROAvoct = pd.read_sql(SQLq, con, params=(dt_ARQ,))

    else:
        if st:
            st.error('Falha ao importar o arquivo ROA da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ROA da base local.')

    ROA['FIM_ROA'] = pd.to_datetime(ROA['FIM_ROA'], errors = 'coerce')
    ROA['INI_ROA'] = pd.to_datetime(ROA['INI_ROA'], errors = 'coerce')
    ROAdt['Dt_Lcmto'] = pd.to_datetime(ROAdt['Dt_Lcmto'], errors = 'coerce')

    def ident_platos(df, per=90):
        df = df.sort_values('Dt_Lcmto')
        df_interp = (
                        df[['Dt_Lcmto', 'VL_tot']]
                        .set_index('Dt_Lcmto')
                        .resample('D')
                        .sum()
                        .interpolate('linear')
                    )
        derivada = df_interp['VL_tot'].diff()
        limite_derivada = 0.01 * df_interp['VL_tot'].sum()
        plato = ((derivada.abs() < limite_derivada) | (df_interp['VL_tot'] < 0))

        grupos = plato.ne(plato.shift()).cumsum()
        tamanhos = plato.groupby(grupos).transform('sum')
        validos = plato & tamanhos.ge(per)

        intervalos = (
                        pd.DataFrame({
                            'inicio': df_interp.index,
                            'fim': df_interp.index,
                            'grupo': grupos.to_numpy(),
                            'valido': validos.to_numpy()
                        })
                        .loc[lambda x: x['valido']]
                        .groupby('grupo', sort=False)
                        .agg(inicio=('inicio', 'min'),
                            fim=('fim', 'max'))
                    )

        if intervalos.empty:
            df['FLG_OBR_INT'] = False
            return df

        datas = df['Dt_Lcmto'].to_numpy(dtype='datetime64[ns]')
        inicios = intervalos['inicio'].to_numpy(dtype='datetime64[ns]')
        fins = intervalos['fim'].to_numpy(dtype='datetime64[ns]')

        pos = np.searchsorted(inicios, datas, side='right') - 1
        resultado = np.zeros(len(df), dtype=bool)
        mascara = pos >= 0
        resultado[mascara] = (datas[mascara] <= fins[pos[mascara]])
        df['FLG_OBR_INT'] = resultado

        return df

    df_resultados = []
    for Cd_SubODI, df_PROV in ROAdt.groupby('Cd_SubODI'):
        df_PROV = ident_platos(df_PROV)
        if df_PROV['FLG_OBR_INT'].any():
            df_PROV['OBS'] = "Existem platôs consideráveis nesse projeto, o que indica problemas de contabilização."
        else:
            df_PROV['OBS'] = "NO"
        df_resultados.append(df_PROV)

    df_SAIDA = pd.concat(df_resultados, ignore_index=True)
    df_SAIDA.to_sql('ANL_PLATOS_MED', con, if_exists='replace', index=False)
    df_SAIDA.to_csv(f"{dir_arq_saida}//ANL_PLATOS_MED_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}/ANL_PLATOS_MED_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    ROA['DELTA'] = (ROA['FIM_ROA'] - ROA['INI_ROA']).dt.days
    ROA['ANL_PER'] = "NO"
    ROA.loc[ROA['DELTA'] == 0, 'ANL_PER'] = 'Verificar o porquê de todos os lançamentos serem no mesmo dia'

    dict_TI = {}
    dict_TI['RDA'] = ['40','41','42','43','44']
    dict_TI['SM'] = ['93','96']
    dict_TI['LD'] = ['35','36','37','38','39','55','56','57','58','59','65','66','67','68','69']
    dict_TI['SE'] = ['30','31','32','33','34','50','51','52','53','54']

    LST_TI = ROA['Nr_TI'].drop_duplicates().to_list()
    for n in dict_TI:
        LST_TI = list(set(LST_TI) - set(dict_TI[n]))
    dict_TI['DEMAIS'] = LST_TI

    for n in dict_TI:    
        ROA.loc[(ROA['DELTA'] > dict_lim[n]) & (ROA['Nr_TI'].isin(dict_TI[n])), 'ANL_PER'] = 'Verificar a distribuição dos lançamentos no tempo, há um motivo para a obra estar acima?'
        ROA.loc[(ROA['DELTA'] > 365) & (ROA['Nr_TI'].isin(dict_TI[n])) & (n=='RDA'), 'ANL_PER'] = 'Obra plurianual de redes, possível ajuste, há um motivo para a obra estar acima?'
        ROA.loc[(ROA['DELTA'] > 365) & (ROA['Nr_TI'].isin(dict_TI[n])) & (n=='SM'), 'ANL_PER'] = 'Obra plurianual de medição, possível ajuste, há um motivo para a obra estar acima?'
        ROA.loc[(ROA['DELTA'] > 180) & (ROA['Nr_TI'].isin(dict_TI[n])) & (n=='DEMAIS'), 'ANL_PER'] = 'Possível ajuste, há um motivo para a obra estar acima?'

    ROA = ROA.merge(ROAvoct, how = 'left', on = ['Nr_TI', 'Cd_SubODI'])

    def fnc_int(indicadores, df_dd):
        interpretacoes = {}
        perc = 0.1
        cta = indicadores['CTA']
        if abs(cta) < 0.1:
            interpretacoes['CTA'] = "isso indica que há distribuição temporal bem balanceada de lançamentos"
        elif cta < -0.5:
            interpretacoes['CTA'] = "isso indica que há alta concentração de lançamentos no início da série"
        elif cta > 0.5:
            interpretacoes['CTA'] = "isso indica que há alta concentração de lançamentos no final da série"
        else:
            interpretacoes['CTA'] = "indicando distribuição temporal levemente enviesada de lançamentos"

        data_ranges = [
                        # CV <= 20%, Inversões <= 10%
                        {
                            "Faixa CV da derivada": "≤ 20%",
                            "Faixa % Inversões": "≤ 10%",
                            "Classificação": "Baixo / Baixo",
                            "Interpretação": "a obra apresenta taxa de crescimento contínuo, com baixa quantidade de ajustes."
                        },
                        # CV <= 20%, Inversões > 10%
                        {
                            "Faixa CV da derivada": "≤ 20%",
                            "Faixa % Inversões": "> 10%",
                            "Classificação": "Baixo / Alto",
                            "Interpretação": "a obra apresenta taxa de crescimento contínuo, mas alterna constantemente com ajustes ocorrendo em frequência considerável."
                        },
                        # CV > 20%, Inversões ≤ 10%
                        {
                            "Faixa CV da derivada": "> 20%",
                            "Faixa % Inversões": "≤ 10%",
                            "Classificação": "Alto / Baixo",
                            "Interpretação": "a obra apresenta variações significativas na taxa de crescimento, indicando boa possibilidade de períodos parados ou lançamentos concentrados ou poucos registros na obra. No entanto, a frequência de ajustes parece baixa."
                        },
                        # CV > 20%, Inversões > 10%
                        {
                            "Faixa CV da derivada": "> 20%",
                            "Faixa % Inversões": "> 10%",
                            "Classificação": "Alto / Alto",
                            "Interpretação": "a obra apresenta variações significativas na taxa de crescimento, indicando boa possibilidade de períodos parados ou lançamentos concentrados ou poucos registros na obra. Ademais, a frequência de ajustes é alta."
                        },
                    ]

        if (indicadores['ID_desv_pad'] <= 0.2) and (indicadores['ID_rev'] <= 0.1):
            interpretacoes['ID'] = data_ranges[0]['Interpretação']
        elif (indicadores['ID_desv_pad'] <= 0.2) and (indicadores['ID_rev'] > 0.1):
            interpretacoes['ID'] = data_ranges[1]['Interpretação']
        elif (indicadores['ID_desv_pad'] > 0.2) and (indicadores['ID_rev'] <= 0.1):
            interpretacoes['ID'] = data_ranges[2]['Interpretação']
        else:
            interpretacoes['ID'] = data_ranges[3]['Interpretação']

        irange = indicadores['IRange']
        if irange == 0:
            interpretacoes['IRange'] = f"não houve lançamentos em que a derivada superou {perc:.2%} do valor da obra"
        else:
            interpretacoes['IRange'] = f"{irange} excursão(ões) em que a derivada superou {perc:.2%} do valor da obra"

        ied = indicadores['IED_dias']
        if ied == 0:
            interpretacoes['IED_dias'] = "quantidade de dias parado não supera limiar regulatório da tipologia"
        else:
            interpretacoes['IED_dias'] = "estagnação prolongada detectada, quantidade de dias parado supera limiar regulatório da tipologia"

        kpi_cresc = indicadores['KPI_CRESC (%)']
        if kpi_cresc == 0:
            interpretacoes['KPI_CRESC (%)'] = "indicando crescimento sempre positivo"
        elif kpi_cresc < 0.1:
            interpretacoes['KPI_CRESC (%)'] = "indicando existência de pequenas quedas pontuais, isto é, menos de 10% dos lançamentos conduzem a reduções do acumulado"
        else:
            interpretacoes['KPI_CRESC (%)'] = "indicando variações negativas frequentes no acumulado, isto é, 10% ou mais dos lançamento conduzem a reduções do acumulado"

        kpi_gap = indicadores['KPI_GAP (dias)']
        if kpi_gap < 30:
            interpretacoes['KPI_GAP (dias)'] = "indicando que inexiste longos períodos de inatividade recente, antes da unitização"
        elif kpi_gap < 90:
            interpretacoes['KPI_GAP (dias)'] = "indicando que há um período relevante de inatividade, antes da unitização, mas dentro dos 90 dias"
        else:
            interpretacoes['KPI_GAP (dias)'] = "indicando inatividade prolongada ao final da série, antes da unitização, superior aos 90 dias"

        kpi_gap = indicadores['KPI_PER']
        if kpi_gap <= 1.0:
            interpretacoes['KPI_PER'] = "o período da obra encontra-se conforme o perfil regulatório"
        elif kpi_gap <= 1.5:
            interpretacoes['KPI_PER'] = "o período da obra encontra-se acima do perfil regulatório"
        else:
            interpretacoes['KPI_PER'] = "o período da obra encontra-se muito acima do perfil regulatório"

        CMD = f"{indicadores['CMD']:,.2f}".replace(".","x").replace(",",".").replace("x",",")
        if indicadores['CMD'] == 0:
            interpretacoes['CMD'] = "O valor está zerado."
        else:
            interpretacoes['CMD'] = f"O valor médio por dia de projeto é de R$ {CMD}."
        if indicadores['Nr_TI'] != "ND":
            if len(df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']])==1:
                MED = f"{df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']]['media'].iloc[0]:,.2f}".replace(".","x").replace(",",".").replace("x",",")
                DES_PAD = f"{df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']]['desvio_padrao'].iloc[0]:,.2f}".replace(".","x").replace(",",".").replace("x",",")
                Q1 = f"{df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']]['q1'].iloc[0]:,.2f}".replace(".","x").replace(",",".").replace("x",",")
                Q2 = f"{df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']]['q3'].iloc[0]:,.2f}".replace(".","x").replace(",",".").replace("x",",")

                interpretacoes['CMD'] += f""" Para esta tipologia, {indicadores['Nr_TI']}, temos média de R$ {MED},
                com desvio padrão de R$ {DES_PAD}. O primeiro quartil é R$ {Q1} e o terceiro quartil é R$ {Q2}."""

        UC_TOT = indicadores['UC_TOT']
        if UC_TOT == 0:
            interpretacoes['UC_TOT'] = "entendemos não ser investimento, trata-se de despesa por não ter material capitalizável"
        elif UC_TOT <= 0.1:
            interpretacoes['UC_TOT'] = f"chamou atenção a baixa participação de itens capitalizáveis, {UC_TOT:.2%}"
        else:
            interpretacoes['UC_TOT'] = f"a participação de itens capitalizáveis é de {UC_TOT:.2%}"
        
        if (indicadores['KPI_PER']>1) and (len(df_dd)):
            try: 
                aa = df_dd['Txt_Desc_ODI'].iloc[0]
            except:
                aa = "sem descrição"
            texto = f"""
                Foi analisado os lançamentos do razão de uma obra, {aa}. A obra
                iniciou em {df_dd['Dt_Inic_Proj'].iloc[0]} e foi energizada em {df_dd['Dt_Energ'].iloc[0]}.
                A transferência para o ativo imobilizado ocorreu em {df_dd['Dt_Uniti'].iloc[0]}. Obtemos o valor
                de {indicadores['KPI_CRESC (%)']:.2%} para a proporção de vezes em que o valor acumulado (coluna 'cumulativo')
                possui 'quebras' no crescimento (delta de cumulativo < 0); {interpretacoes['KPI_CRESC (%)']}. Obtemos o valor
                de {indicadores['KPI_GAP (dias)']:.2f} dias sem movimentações positivas de UC/UAR
                (valor > 0) no final da obra, em relação à data de unitização do projeto; {interpretacoes['KPI_GAP (dias)']}.
                Obtemos o valor de {indicadores['CTA']:.2f} para a distribuição temporal de lançamentos do projeto; {interpretacoes['CTA']}.
                Obtemos o valor de {indicadores['ID_desv_pad']:.2%} para irregularidade da derivada e {indicadores['ID_rev']:.2%} para reversões de sentido, dos lançamentos do projeto; {interpretacoes['ID']}
                Obtemos o valor de {indicadores['IRange']:.2f} para o número de vezes que ocorre uma derivada relevante nos lançamentos do projeto; isto é, {interpretacoes['IRange']}.
                Obtemos o valor de {int(indicadores['IED_dias'])} para o maior período consecutivo com derivada próxima de zero (em dias) nos lançamentos do projeto; isto é, {interpretacoes['IED_dias']}.
                Obtemos o valor de {indicadores['KPI_PER']:.2f} para a relação período da obra sobre o regulatório para a TI do projeto; assim, {interpretacoes['KPI_PER']}.
                No geral, tivemos {indicadores['IEg_dias']} dias como máxima distância entre lançamentos de qualquer natureza de gasto.
                Por sua vez, tivemos {indicadores['IEuc_dias']} dias como máxima distância entre lançamentos de natureza de gasto de UC/UAR,
                considerando o último lançamento como proxy de UC/UAR também. Nada obstante, nessa obra temos que cerca de
                {indicadores['CA_TOT']:.2%} representam os custos de mão de obra no projeto, considerando o valor total da obra.
                Nesta obra, {interpretacoes['UC_TOT']}. {interpretacoes['CMD']}
                """
        elif len(df_dd):
            try: 
                aa = df_dd['Txt_Desc_ODI'].iloc[0]
            except:
                aa = "sem descrição"
            texto = f"""
                Foi analisado os lançamentos do razão de uma obra, {aa}. A obra
                iniciou em {df_dd['Dt_Inic_Proj'].iloc[0]} e foi energizada em {df_dd['Dt_Energ'].iloc[0]}.
                A transferência para o ativo imobilizado ocorreu em {df_dd['Dt_Uniti'].iloc[0]}.
                No geral, tivemos {indicadores['IEg_dias']} dias como máxima distância entre lançamentos de qualquer natureza de gasto.
                Por sua vez, tivemos {indicadores['IEuc_dias']} dias como máxima distância entre lançamentos de natureza de gasto de UC/UAR,
                considerando o último lançamento como proxy de UC/UAR também.  Nada obstante, nessa obra temos que cerca de
                {indicadores['CA_TOT']:.2%} representam os custos de mão de obra no projeto, considerando o valor total da obra.
                Obtemos o valor de {indicadores['KPI_PER']:.2f} para a relação período da obra sobre o regulatório para a TI do projeto; assim, {interpretacoes['KPI_PER']}.
                Nesta obra, {interpretacoes['UC_TOT']}. {interpretacoes['CMD']}
                """
        else:
            texto = "Essa obra não foi declarada no ROS."
        if indicadores['FLG_MOP']:
            texto += """Há lançamentos de MOP, sem lançamentos de material no mês."""
        if indicadores['FLG_ST']:
            texto += """Há lançamentos de ST, sem lançamentos de material no mês."""
        if indicadores['FLG_JOA']:
            texto += """Há lançamentos de JOA, sem lançamentos de material no mês."""
        return texto
        
    now = datetime.now()

    tese = NR_TI_ROA(st.session_state.tra_dir, st)
    df_PR_all = ler_roa_uv(st.session_state.tra_dir, Empresa, st.session_state.dt_fim.year, st)
    tese['Cd_SubODI'] = tese['Cd_SubODI'].astype(str)
    df_PR_all = df_PR_all.merge(tese, how = 'left', on = 'Cd_SubODI')  
    df_dd_all = ler_ros_uv(st.session_state.tra_dir, Empresa, st.session_state.dt_fim.year, st)
    df_PR_all['data'] = pd.to_datetime(df_PR_all['data'])
    projetos = sorted(df_PR_all['Cd_SubODI'].dropna().unique().tolist())
    df_TOT = []
    
    if st:
        pb = st.progress(0.0, text="Análise das obras")
   
    CHECKPOINT_CICLO = 1000
    TMP_NOME  = "KPIS_checkpoint.csv" 
    ARQ_TOT = os.path.join(dir_arq_saida, TMP_NOME)
    def ler_arq(ARQ_TOT):
        if not os.path.exists(ARQ_TOT):
            return set()
        try:
            usecols = ["Cd_SubODI"]
            chk = pd.read_csv(ARQ_TOT, sep="|", encoding="Latin-1", usecols=usecols, dtype={"Cd_SubODI": str})
            return set(chk["Cd_SubODI"].dropna().astype(str).unique())
        except Exception:
            return set()
    processados = ler_arq(ARQ_TOT)

    batch = [] 
    total = len(projetos)
    art = st.success(f"Iniciando análise dos batchs.") if st else None
    
    for i, prj in enumerate(projetos, 1):
        prj_str = str(prj)
        if prj_str in processados:
            if st:
                art.write(f"Pulando {prj_str} (já feita análise).")
            continue

        df_PR = df_PR_all[df_PR_all['Cd_SubODI'] == prj]
        df_dd = df_dd_all[df_dd_all.get('Cd_SubODI', None) == prj] if not df_dd_all.empty and 'Cd_SubODI' in df_dd_all else pd.DataFrame()

        indicadores = calcular_kpis_uv(df_PR, prj, st.session_state.tra_dir, lim=0.1, eps=1.0, st = st)

        indicadores['texto'] = fnc_int(indicadores, df_dd)
        indicadores['Cd_SubODI'] = prj
        batch.append(indicadores)

        if (len(processados) + len(batch)) % CHECKPOINT_CICLO == 0:
            if not batch:
                continue
            df_batch = pd.DataFrame(batch)
            write_header = not os.path.exists(ARQ_TOT)
            df_batch.to_csv(
                                ARQ_TOT,
                                sep="|",
                                decimal=",",
                                index=False,
                                encoding="Latin-1",
                                mode="a",
                                header=write_header, chunksize=100_000
                            )
            batch.clear()
            processados = ler_arq(ARQ_TOT)
            if st:
                art.success(f"Checkpoint salvo: {len(processados)} projetos.")

        if st:
            pb.progress(i/total, text=f"Análise de {prj} ({i}/{total})")
    
    if batch:
        df_batch = pd.DataFrame(batch)
        write_header = not os.path.exists(ARQ_TOT)
        df_batch.to_csv(
                            ARQ_TOT,
                            sep="|",
                            decimal=",",
                            index=False,
                            encoding="Latin-1",
                            mode="a",
                            header=write_header, chunksize=100_000
                        )
    if art: art.empty()
    df_TOT = pd.read_csv(ARQ_TOT, sep="|", encoding="Latin-1", dtype={"Cd_SubODI": str})
    df_TOT['Nr_TI'] = df_TOT['Nr_TI'].astype(str)
    ROA = ROA.merge(df_TOT, how = 'left', on =['Cd_SubODI', 'Nr_TI'])

    ROA.to_sql('ANL_PER_OBRA', con, if_exists='replace', index=False)
    ROA.to_csv(f"{dir_arq_saida}//ANL_PER_OBRA_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}/ANL_PER_OBRA_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def anl_RACcom(con, dir_arq_saida, Empresa, st=None):
    dic_CD = {
                '1':  ('Condutor Nu (rede primária)',          'COND_NU'),
                '2':  ('Condutor Isolado (rede primária)',     'COND_ISO'),
                '3':  ('Banco de Capacitores',                 'BC'),
                '4':  ('Chave Fusível',                        'CHV_FUS'),
                '5':  ('Chave Seccionadora',                   'CHV_SEC'),
                '6':  ('Chave Seccionadora Carga',             'CHV_SEC_CRG'),
                '7':  ('Cruzeta',                              'CZT'),
                '8':  ('Haste de Aterramento',                 'HASTE'),
                '9':  ('Isolador Disco',                       'ISOL_DIS'),
                '10': ('Isolador Pino',                        'ISOL_PIN'),
                '11': ('Para-raios',                           'PR_RAIO'),
                '12': ('Pino',                                 'PIN'),
                '13': ('Poste',                                'PST'),
                '14': ('Regulador de Tensão',                  'REG'),
                '15': ('Religador Monofásico',                 'REL1'),
                '16': ('Religador Trifásico',                  'REL3'),
                '17': ('Seccionalizador de cerca',             'SECC_CERCA'),
                '18': ('Seccionalizador Monofásico',           'SECC1'),
                '19': ('Seccionalizador Trifásico',            'SECC3'),
                '20': ('Torre',                                'TOR'),
                '21': ('Transformador Distribuição Bifásico',  'TRD2'),
                '22': ('Transformador Distribuição Monofásico','TRD1'),
                '23': ('Transformador Distribuição Trifásico', 'TRD3'),
            }

    tbl_CD_Nm = (
                    pd.DataFrame.from_dict(dic_CD, orient='index', columns=['Nm_Reg', 'VAR_Reg'])
                    .reset_index(names='CD_Nm_Reg')
                )
    SQLq = f"""
            SELECT 
                t1.Nr_TI,
                t1.Cd_SubODI,
                t1.COD_ITEM,
                t1.Cd_NG,
                SUM(CAST(REPLACE(t1.Qtd, ',', '.') AS REAL)) AS Qtd,
                t1.Unidade,
                SUM(CAST(REPLACE(t1.VL_tot, ',', '.') AS REAL)) AS VL_tot
            FROM ROA AS t1
            WHERE 
                t1.dt_ARQ = ?
                AND (
                        t1.Nr_TI IN ('40', '41') OR t1.Nr_TI IN (40, 41)
                    )
                AND (
                        t1.Cd_NG IN ('1', '2') OR t1.Cd_NG IN (1, 2)
                    )
            GROUP BY 
                t1.Nr_TI,
                t1.Cd_SubODI,
                t1.COD_ITEM,
                t1.Cd_NG,
                t1.Unidade
            """
    ROA = sql.imp_tbl_forma_001("ROA", SQLq = SQLq, con=con, st=st, Empresa=Empresa)
   
    b1 = False   
    if os.path.exists(f"{dir_arq_saida}/LST_MAT_AJ_{Empresa}.csv"):
        try:
            LST_MAT = pd.read_csv(f"{dir_arq_saida}/LST_MAT_AJ_{Empresa}.csv",sep="|",decimal=','
                          , on_bad_lines='skip', dtype=str, 
                          usecols = ['Nr_TI', 'COD_ITEM', 'CD_Nm_Reg', 'Nr_FC', 'Vl_Default_Man', 'Vl_Default_Inv']);
        except:
            LST_MAT = pd.read_csv(f"{dir_arq_saida}/LST_MAT_AJ_{Empresa}.csv",sep="|",decimal=','
                          , on_bad_lines='skip', dtype=str, encoding='latin-1',
                          usecols = ['Nr_TI', 'COD_ITEM', 'CD_Nm_Reg', 'Nr_FC', 'Vl_Default_Man', 'Vl_Default_Inv']);
    else:
        LST_MAT = sql.imp_tbl_forma_001("LST_MAT", con=con, st=st, Empresa=Empresa)

    LST_MAT['Nr_FC'] = (
                            LST_MAT['Nr_FC']
                            .astype(str)
                            .str.replace(",", ".", regex=False)
                            .replace("None", np.nan)
                            .pipe(pd.to_numeric, errors="coerce")
                            .fillna(1.0)
                        )
    LST_MAT['COD_ITEMchv'] = LST_MAT['COD_ITEM'].astype(str).str.zfill(25)
    ROA['COD_ITEMchv'] = ROA['COD_ITEM'].astype(str).str.zfill(25)
    chaves_merge = ['COD_ITEMchv'] if b1 else ['Nr_TI', 'COD_ITEMchv']

    ROA = ROA.merge(LST_MAT[['Nr_TI', 'COD_ITEM', 'COD_ITEMchv', 'CD_Nm_Reg', 'Nr_FC']].drop_duplicates(subset=chaves_merge),
                    how='left', on=chaves_merge, suffixes=("_ROA","_LST_MAT"))
    ROA['Nr_FC'] = ROA['Nr_FC'].fillna(1.0)
    ROA = (
            ROA
            .drop(columns=['COD_ITEMchv','COD_ITEM_LST_MAT'])
            .rename(columns = {'COD_ITEM_ROA':'COD_ITEM'})
          )

    ROA.loc[ROA['Unidade'].astype(str).str.upper().isin(["M","MT"]), 'Nr_FC'] = 1.0
    ROA['Qtd'] = ROA['Qtd'] / ROA['Nr_FC']
    ROA_RAC_COM = (ROA[['Nr_TI', 'Cd_SubODI', 'COD_ITEM', 'CD_Nm_Reg', 'Cd_NG', 'Qtd', 'VL_tot']]
                   .query("CD_Nm_Reg.notnull()")
                   .merge(tbl_CD_Nm[['CD_Nm_Reg','VAR_Reg']],
                        how='left', on='CD_Nm_Reg'))
    
    ROA_RAC_COM = (
                        ROA_RAC_COM
                        .groupby(by=['Nr_TI', 'Cd_SubODI', 'VAR_Reg', 'Cd_NG'], dropna=False)[['Qtd', 'VL_tot']]
                        .sum()
                        .reset_index()
                  )

    ROA_RAC_COM['CMU'] = ROA_RAC_COM['VL_tot'] / ROA_RAC_COM['Qtd']
    ROA_RAC_COM['Cd_NG'] = ROA_RAC_COM['Cd_NG'].map({'1': 'UC', '2': 'COM'}).fillna(ROA_RAC_COM['Cd_NG'])

    ROA_RAC_COM['PV_QTD'] = f'Qtd_' + ROA_RAC_COM['VAR_Reg'] + '_' + ROA_RAC_COM['Cd_NG']
    ROA_RAC_COM['PV_CMU'] = f'VL_'  + ROA_RAC_COM['VAR_Reg'] + '_' + ROA_RAC_COM['Cd_NG']

    def gerar_resumo(df, valor_col, label_col):
        resumo = (
                    pd.pivot_table(
                        df,
                        index=['Nr_TI', 'Cd_SubODI'],
                        columns=[label_col],
                        values=[valor_col],
                        fill_value=0,
                        aggfunc='sum'
                    )
                    .reset_index()
                )
        resumo.columns = [col if col else idx for idx, col in resumo.columns.to_list()]
        return resumo

    RESUMO_QTD = gerar_resumo(ROA_RAC_COM, 'Qtd', 'PV_QTD')
    RESUMO_VAL = gerar_resumo(ROA_RAC_COM, 'CMU', 'PV_CMU')
    RESUMO = RESUMO_QTD.merge(RESUMO_VAL, on=['Nr_TI', 'Cd_SubODI'], how='left')
    
    RESUMO.to_sql('RESUMO_MAT_CMU_QTD', con, if_exists='replace', index=False)
    RESUMO.to_csv(f"{dir_arq_saida}//RESUMO_MAT_CMU_QTD_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//RESUMO_MAT_CMU_QTD_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
        
    NT_COM = sql.imp_tbl_forma_001("NT_COM", con=con, st=st, Empresa=Empresa)
    SQLq = f"""
            SELECT 
                t1.Cd_SubODI, 
                CAST(SUBSTR(t1.Dt_Inic_Proj, 1, 4) AS REAL) as ANO, 
                t1.Nr_Fases
            FROM 
                ROS t1 
            WHERE 
                t1.dt_ARQ = ?
            """
    ROS = sql.imp_tbl_forma_001("ROS",SQLq=SQLq, con=con, st=st, Empresa=Empresa)
    if ROS.empty:
        SQLq = f"""
            SELECT 
                t1.Cd_SubODI,
                CAST(strftime('%Y', MIN(t1.Dt_Lcmto)) AS INTEGER) AS ANO,
                1 AS Nr_Fases
            FROM ROA t1
            WHERE 
                t1.dt_ARQ = ?
            GROUP BY 
                t1.Cd_SubODI
            """
        ROS = sql.imp_tbl_forma_001("ROA",SQLq=SQLq, con=con, st=st, Empresa=Empresa)

    RESUMO = ROS.merge(RESUMO, how = 'right', on = 'Cd_SubODI')
    
    lst_VAR_Reg = [v[1] for v in dic_CD.values()]
    colunas_existentes = set(RESUMO.columns)

    for n in ('UC', 'COM'):
        for var in lst_VAR_Reg:
            for prefix in ('Qtd', 'VL'):
                col = f'{prefix}_{var}_{n}'
                if col not in colunas_existentes:
                    RESUMO[col] = 0
                    colunas_existentes.add(col)

    VAR_CALC = {f'Qtd_{v[1]}_{n}': RESUMO.columns.get_loc(f'Qtd_{v[1]}_{n}')
                for n in ('UC', 'COM') for v in dic_CD.values()}

    NT_COM['QTD_NORM'] = (
                            NT_COM['QTD_NORM']
                            .astype(str)
                            .str.replace(r'\.0$', '', regex=True)
                        )
    NT_COM.iloc[:, 2] = (
                            NT_COM.iloc[:, 2]
                            .fillna('0')
                            .astype(str)
                            .str.replace(',', '.', regex=False)
                            .astype(float)
                        )

    dic_NT_COM = { 'Qtd_BC_CHFUS_RAR' : 0, 'Qtd_BC_CHFUS_RAU' : 0, 'Qtd_BC_CRZT_CNV_RAR' : 0, 'Qtd_BC_CRZT_CNV_RAU' : 0, 
                  'Qtd_BC_HA_RAR' : 0, 'Qtd_BC_HA_RAU' : 0, 'Qtd_BC_PR_RAR' : 0, 'Qtd_BC_PR_RAU' : 0, 'Qtd_CHFUS_CRZT_CNV_RAR' : 0, 
                  'Qtd_CHFUS_CRZT_CNV_RAU' : 0, 'Qtd_CHFUS_RD_CNV_RAR' : 0, 'Qtd_CHFUS_RD_CNV_RAU' : 0, 
                  'Qtd_CHSECC_CRZT_CNV_RAR' : 0, 'Qtd_CHSECC_CRZT_CNV_RAU' : 0, 'Qtd_CHSECC_PR_RAR' : 0, 
                  'Qtd_CHSECC_PR_RAU' : 0, 'Qtd_CHSECCc_CHFUS_RAR' : 0, 'Qtd_CHSECCc_CHFUS_RAU' : 0, 
                  'Qtd_CHSECCc_CRZT_CH_RAR' : 0, 'Qtd_CHSECCc_CRZT_CH_RAU' : 0, 'Qtd_CHSECCc_HA_RAR' : 0, 
                  'Qtd_CHSECCc_HA_RAU' : 0, 'Qtd_CHSECCc_PR_RAR' : 0, 'Qtd_CHSECCc_PR_RAU' : 0, 'Qtd_MAX_CRUZT_PST_RDR' : 0, 
                  'Qtd_MAX_CRUZT_PST_RDU' : 0, 'Qtd_MAX_ISOL_DIS_PST_RDR' : 0, 'Qtd_MAX_ISOL_DIS_PST_RDU' : 0, 
                  'Qtd_MAX_ISOL_PIN_PST_RDR' : 0, 'Qtd_MAX_ISOL_PIN_PST_RDU' : 0, 'Qtd_PR_CRZT_CNV_RAR' : 0, 
                  'Qtd_PR_CRZT_CNV_RAU' : 0, 'Qtd_PR_HA_RAR' : 0, 'Qtd_PR_HA_RAU' : 0, 'Qtd_PR_RD_CNV_RAR' : 0, 
                  'Qtd_PR_RD_CNV_RAU' : 0, 'Qtd_REG_CHFUS_RAR' : 0, 'Qtd_REG_CHFUS_RAU' : 0, 'Qtd_REG_CRZT_ESC_RAR' : 0, 
                  'Qtd_REG_CRZT_ESC_RAU' : 0, 'Qtd_REG_CRZT_REG_RAR' : 0, 'Qtd_REG_CRZT_REG_RAU' : 0, 'Qtd_REG_HA_RAR' : 0, 
                  'Qtd_REG_HA_RAU' : 0, 'Qtd_REG_PR_RAR' : 0, 'Qtd_REG_PR_RAU' : 0, 'Qtd_REL1_CHFUS_RAR' : 0, 
                  'Qtd_REL1_CHFUS_RAU' : 0, 'Qtd_REL1_CRZT_CNV_RAR' : 0, 'Qtd_REL1_CRZT_CNV_RAU' : 0, 'Qtd_REL1_HA_RAR' : 0, 
                  'Qtd_REL1_HA_RAU' : 0, 'Qtd_REL1_PR_RAR' : 0, 'Qtd_REL1_PR_RAU' : 0, 'Qtd_REL3_CHFUS_RAR' : 0, 
                  'Qtd_REL3_CHFUS_RAU' : 0, 'Qtd_REL3_CRZT_CNV_RAR' : 0, 'Qtd_REL3_CRZT_CNV_RAU' : 0, 'Qtd_REL3_HA_RAR' : 0, 
                  'Qtd_REL3_HA_RAU' : 0, 'Qtd_REL3_PR_RAR' : 0, 'Qtd_REL3_PR_RAU' : 0, 'Qtd_SECC1_CHFUS_RAR' : 0, 
                  'Qtd_SECC1_CHFUS_RAU' : 0, 'Qtd_SECC1_CRZT_CH_RAR' : 0, 'Qtd_SECC1_CRZT_CH_RAU' : 0, 'Qtd_SECC1_HA_RAR' : 0, 
                  'Qtd_SECC1_HA_RAU' : 0, 'Qtd_SECC1_PR_RAR' : 0, 'Qtd_SECC1_PR_RAU' : 0, 'Qtd_SECC3_CHFUS_RAR' : 0, 
                  'Qtd_SECC3_CHFUS_RAU' : 0, 'Qtd_SECC3_CRZT_CH_RAR' : 0, 'Qtd_SECC3_CRZT_CH_RAU' : 0, 'Qtd_SECC3_HA_RAR' : 0, 
                  'Qtd_SECC3_HA_RAU' : 0, 'Qtd_SECC3_PR_RAR' : 0, 'Qtd_SECC3_PR_RAU' : 0, 'Qtd_TRD1_CHFUS_RAR' : 0, 
                  'Qtd_TRD1_CHFUS_RAU' : 0, 'Qtd_TRD1_CRZT_CNV_RAR' : 0, 'Qtd_TRD1_CRZT_CNV_RAU' : 0, 'Qtd_TRD1_PR_RAR' : 0, 
                  'Qtd_TRD1_PR_RAU' : 0, 'Qtd_TRD2_CHFUS_RAR' : 0, 'Qtd_TRD2_CHFUS_RAU' : 0, 'Qtd_TRD2_CRZT_CNV_RAR' : 0, 
                  'Qtd_TRD2_CRZT_CNV_RAU' : 0, 'Qtd_TRD2_PR_RAR' : 0, 'Qtd_TRD2_PR_RAU' : 0, 'Qtd_TRD3_CHFUS_RAR' : 0, 
                  'Qtd_TRD3_CHFUS_RAU' : 0, 'Qtd_TRD3_CRZT_CNV_RAR' : 0, 'Qtd_TRD3_CRZT_CNV_RAU' : 0, 'Qtd_TRD3_PR_RAR' : 0, 
                  'Qtd_TRD3_PR_RAU' : 0, 'VL_VAO_RDR' : 0, 'VL_VAO_RDU' : 0, 'VL_VAO_MIN_RAU' : 1, 'VL_VAO_MIN_RAR' : 1, 
                  'VL_RAM_MIN_RAU' : 1, 'VL_RAM_MIN_RAR' : 1, 'Qtd_TRD1_HA_RAR' : 0, 'Qtd_TRD1_HA_RAU' : 0, 
                  'Qtd_TRD2_HA_RAR' : 0, 'Qtd_TRD2_HA_RAU' : 0, 'Qtd_TRD3_HA_RAR' : 0, 'Qtd_TRD3_HA_RAU' : 0 }

    dic_NT_COM.update(
                            dict(zip(NT_COM.iloc[:, 1], NT_COM.iloc[:, 2]))
                        )

    RESUMO['Nr_Fases'] = pd.to_numeric(RESUMO['Nr_Fases'], errors = 'coerce')
    RESUMO.loc[RESUMO['Nr_Fases'] == 0, 'Nr_Fases'] = 1

    def limitar_positivo(df, col):
        df[col] = np.ceil(np.maximum(df[col], 0))

    def condicional(df, col, expr_rar, expr_rau):
        if col not in df.columns:
            df[col] = 0

        mask_rar = df['Nr_TI'].astype(str) == '41'
        mask_rau = df['Nr_TI'].astype(str) == '40'

        df.loc[mask_rar, col] = expr_rar.loc[mask_rar]
        df.loc[mask_rau, col] = expr_rau.loc[mask_rau]

        limitar_positivo(df, col)

    # ==========================================================
    # Cálculo de estruturas equivalentes
    # ==========================================================
    @monitor_completo(st.session_state.LOGGER)
    def calcular_postes(df, dic):
        df['PST_EQV'] = np.where(
                                    df['Nr_TI'] == '41',
                                    ((df['Qtd_COND_NU_UC'] + df['Qtd_COND_ISO_UC']) / df['Nr_Fases']) / dic['VL_VAO_RDR'],
                                    ((df['Qtd_COND_NU_UC'] + df['Qtd_COND_ISO_UC']) / df['Nr_Fases']) / dic['VL_VAO_RDU']
                                )
        df['PST_EQV'] = np.ceil(df['PST_EQV'])
        df['TIPO_OBRA'] = np.where(
                                        df['PST_EQV'] == 0,
                                        'Troca/Instalação equipamento',
                                        np.where(
                                            (df['PST_EQV'] - (df['Qtd_PST_UC'] + df['Qtd_TOR_UC'])) > (0.2 * df['PST_EQV']),
                                            np.where(df['PST_EQV'] == 1, 'Troca/Instalação equipamento', 'Recondutoramento'),
                                            'Incremento Rede'
                                        )
                                    )

        df['PST_CALC'] = np.where(
                                        (df['Qtd_PST_UC'] + df['Qtd_TOR_UC']) > df['PST_EQV'],
                                        df['Qtd_PST_UC'] + df['Qtd_TOR_UC'],
                                        df['PST_EQV']
                                    )

    # ==========================================================
    # Cálculo de cruzetas sem equipamento
    # ==========================================================
    @monitor_completo(st.session_state.LOGGER)
    def calcular_cruzetas(df, dic):
        def calcula_expr(df, dic, sufixo):
            d = {k: v for k, v in dic.items() if k.endswith(sufixo)}
            return (
                        (d[f'Qtd_REL1_CRZT_CNV_{sufixo}'] * df['Qtd_REL1_UC']
                        + d[f'Qtd_REL3_CRZT_CNV_{sufixo}'] * df['Qtd_REL3_UC']
                        + d[f'Qtd_SECC1_CRZT_CH_{sufixo}'] * df['Qtd_SECC1_UC']
                        + d[f'Qtd_SECC3_CRZT_CH_{sufixo}'] * df['Qtd_SECC3_UC']
                        + d[f'Qtd_TRD1_CRZT_CNV_{sufixo}'] * df['Qtd_TRD1_UC']
                        + d[f'Qtd_TRD2_CRZT_CNV_{sufixo}'] * df['Qtd_TRD2_UC']
                        + d[f'Qtd_TRD3_CRZT_CNV_{sufixo}'] * df['Qtd_TRD3_UC']
                        + (d[f'Qtd_REG_CRZT_ESC_{sufixo}'] / 3 
                        + d[f'Qtd_REG_CRZT_REG_{sufixo}']) * df['Qtd_REG_UC']
                        + d[f'Qtd_BC_CRZT_CNV_{sufixo}'] * df['Qtd_BC_UC']
                        + d[f'Qtd_CHSECCc_CRZT_CH_{sufixo}'] * df['Qtd_CHV_SEC_CRG_UC']
                        + 2 * df['Qtd_CHV_SEC_UC'] / np.maximum(df['Nr_Fases'], 1)
                        + d[f'Qtd_PR_CRZT_CNV_{sufixo}'] 
                            * (df['Qtd_PR_RAIO_UC'] + df['Qtd_PR_RAIO_COM']) / np.maximum(df['Nr_Fases'], 1)
                        + d[f'Qtd_CHFUS_CRZT_CNV_{sufixo}'] 
                            * (df['Qtd_CHV_FUS_UC'] + df['Qtd_CHV_FUS_COM'])
                            / np.maximum(df['Nr_Fases'], 1)
                        )
                    )

        expr_rar = calcula_expr(df, dic, "RAR")
        expr_rau = calcula_expr(df, dic, "RAU")
        condicional(df, 'Qtd_CRZ_SCHV_EQ_NORM', expr_rar, expr_rau)

    # ==========================================================
    # Hastes de aterramento
    # ==========================================================
    @monitor_completo(st.session_state.LOGGER)
    def calcular_haste(df, dic):
        def calcula_expr_HA(df, dic, sufixo):
            nr_fases = np.maximum(df['Nr_Fases'], 1)
            return (
                        dic[f'Qtd_PR_HA_{sufixo}'] * (df['Qtd_PR_RAIO_COM'] * 2) / nr_fases
                        + df['PST_CALC'] / 2
                        + df['Qtd_SECC_CERCA_COM'] / nr_fases
                        + dic[f'Qtd_BC_HA_{sufixo}'] * df['Qtd_BC_UC']
                        + dic[f'Qtd_CHSECCc_HA_{sufixo}'] * df['Qtd_CHV_SEC_CRG_UC']
                        + dic[f'Qtd_REG_HA_{sufixo}'] * df['Qtd_REG_UC']
                        + dic[f'Qtd_REL1_HA_{sufixo}'] * df['Qtd_REL1_UC']
                        + dic[f'Qtd_REL3_HA_{sufixo}'] * df['Qtd_REL3_UC']
                        + dic[f'Qtd_SECC1_HA_{sufixo}'] * df['Qtd_SECC1_UC']
                        + dic[f'Qtd_SECC3_HA_{sufixo}'] * df['Qtd_SECC3_UC']
                        + dic[f'Qtd_TRD1_HA_{sufixo}'] * df['Qtd_TRD1_UC']
                        + dic[f'Qtd_TRD2_HA_{sufixo}'] * df['Qtd_TRD2_UC']
                        + dic[f'Qtd_TRD3_HA_{sufixo}'] * df['Qtd_TRD3_UC']
                    )
        expr_rar = calcula_expr_HA(df, dic, "RAR")
        expr_rau = calcula_expr_HA(df, dic, "RAU")
        condicional(df, 'Qtd_HASTE_NORM', expr_rar, expr_rau)

    # ==========================================================
    # Para-raios
    # ==========================================================
    @monitor_completo(st.session_state.LOGGER)
    def calcular_para_raios(df, dic):
        def calcula_expr_PR(df, dic, sufixo):
            fator_rd = dic[f'Qtd_PR_RD_CNV_{sufixo}']
            nr_fases = np.maximum(df['Nr_Fases'], 1)
            base = (
                        dic[f'Qtd_REG_PR_{sufixo}'] * df['Qtd_REG_UC']
                        + dic[f'Qtd_REL1_PR_{sufixo}'] * df['Qtd_REL1_UC']
                        + dic[f'Qtd_REL3_PR_{sufixo}'] * df['Qtd_REL3_UC']
                        + dic[f'Qtd_BC_PR_{sufixo}'] * df['Qtd_BC_UC']
                        + dic[f'Qtd_CHSECC_PR_{sufixo}'] * df['Qtd_CHV_SEC_UC']
                        + dic[f'Qtd_CHSECCc_PR_{sufixo}'] * df['Qtd_CHV_SEC_CRG_UC']
                        + dic[f'Qtd_SECC1_PR_{sufixo}'] * df['Qtd_SECC1_UC']
                        + dic[f'Qtd_SECC3_PR_{sufixo}'] * df['Qtd_SECC3_UC']
                        + df['Qtd_TRD1_UC']
                        + 2 * df['Qtd_TRD2_UC']
                        + 3 * df['Qtd_TRD3_UC']
                    )

            condutores = df['Qtd_COND_NU_UC'] + df['Qtd_COND_ISO_UC']
            pr_calc = condutores / fator_rd / nr_fases

            ajuste_fases = np.where(
                                        pr_calc < nr_fases,
                                        nr_fases,
                                        round(pr_calc, 0)
                                    )

            return base + ajuste_fases
        expr_rar = calcula_expr_PR(df, dic, "RAR")
        expr_rau = calcula_expr_PR(df, dic, "RAU")
        condicional(df, 'Qtd_PR_RAIO_NORM', expr_rar, expr_rau)

    # ==========================================================
    # Chaves fusíveis
    # ==========================================================
    @monitor_completo(st.session_state.LOGGER)
    def calcular_chaves_fusiveis(df, dic):
        def calcula_expr_CHFUS(df, dic, sufixo):
            fator_rd = dic[f'Qtd_CHFUS_RD_CNV_{sufixo}']
            fator_rd = max(fator_rd, 1e-9) 
            nr_fases = np.maximum(df['Nr_Fases'], 1)
            base = (
                        dic[f'Qtd_REG_CHFUS_{sufixo}'] * df['Qtd_REG_UC']
                        + dic[f'Qtd_REL1_CHFUS_{sufixo}'] * df['Qtd_REL1_UC']
                        + dic[f'Qtd_REL3_CHFUS_{sufixo}'] * df['Qtd_REL3_UC']
                        + dic[f'Qtd_BC_CHFUS_{sufixo}'] * df['Qtd_BC_UC']
                        + dic[f'Qtd_CHSECCc_CHFUS_{sufixo}'] * df['Qtd_CHV_SEC_CRG_UC']
                        + dic[f'Qtd_SECC1_CHFUS_{sufixo}'] * df['Qtd_SECC1_UC']
                        + dic[f'Qtd_SECC3_CHFUS_{sufixo}'] * df['Qtd_SECC3_UC']
                        + df['Qtd_TRD1_UC']
                        + 2 * df['Qtd_TRD2_UC']
                        + 3 * df['Qtd_TRD3_UC']
                    )
            condutores = df['Qtd_COND_NU_UC'] + df['Qtd_COND_ISO_UC']
            chfus_calc = condutores / fator_rd / nr_fases
            ajuste_fases = np.where(
                                        chfus_calc < nr_fases,
                                        nr_fases,
                                        round(chfus_calc, 0)
                                    )

            return base + ajuste_fases
        expr_rar = calcula_expr_CHFUS(df, dic, "RAR")
        expr_rau = calcula_expr_CHFUS(df, dic, "RAU")
        condicional(df, 'Qtd_CHV_FUS_NORM', expr_rar, expr_rau)

    # ==========================================================
    # Valores normativos por poste
    # ==========================================================
    @monitor_completo(st.session_state.LOGGER)
    def calcular_normas_por_poste(df, dic):
        base_crz = np.where(
                                df['Nr_TI'] == '41',
                                dic['Qtd_MAX_CRUZT_PST_RDR'] * df['PST_CALC'],
                                dic['Qtd_MAX_CRUZT_PST_RDU'] * df['PST_CALC']
                            )
        df['Qtd_CRZ_NORM'] = np.where(df['Nr_Fases'] > 1, base_crz, 0)
        df['Qtd_ISOL_DIS_NORM'] = np.where(
                                                df['Nr_TI'] == '41',
                                                (dic['Qtd_MAX_ISOL_DIS_PST_RDR'] ) * df['PST_CALC'],
                                                (dic['Qtd_MAX_ISOL_DIS_PST_RDU'] ) * df['PST_CALC']
                                            )

        df['Qtd_ISOL_PIN_NORM'] = np.where(
                                                df['Nr_TI'] == '41',
                                                (dic['Qtd_MAX_ISOL_PIN_PST_RDR'] ) * df['PST_CALC'],
                                                (dic['Qtd_MAX_ISOL_PIN_PST_RDU'] ) * df['PST_CALC']
                                            )

    # ==========================================================
    # Ajustes e valores adicionais
    # ==========================================================
    @monitor_completo(st.session_state.LOGGER)
    def calcular_ajustes(df, dic):
        df['Qtd_AJS_CRZ'] = np.maximum(df['Qtd_CZT_COM'] - df['Qtd_CRZ_SCHV_EQ_NORM'] - df['Qtd_CRZ_NORM'], 0)
        df['Qtd_AJS_ISOL_DIS'] = np.maximum(df['Qtd_ISOL_DIS_COM'] - df['Qtd_ISOL_DIS_NORM'], 0)
        df['Qtd_AJS_ISOL_PIN'] = np.maximum(df['Qtd_ISOL_PIN_COM'] - df['Qtd_ISOL_PIN_NORM'], 0)
        df['Qtd_AJS_PIN']      = np.maximum(df['Qtd_PIN_COM'] - df['Qtd_ISOL_PIN_NORM'], 0)
        df['Qtd_AJS_HASTE'] = np.maximum(df['Qtd_HASTE_COM'] - df['Qtd_HASTE_NORM'], 0)
        df['Qtd_AJS_PR_RAIO'] = np.maximum(df['Qtd_PR_RAIO_COM'] - (df['Qtd_PR_RAIO_NORM'] - df['Qtd_PR_RAIO_UC']), 0)
        df['Qtd_AJS_CHV_FUS'] = np.maximum(df['Qtd_CHV_FUS_COM'] - (df['Qtd_CHV_FUS_NORM'] -  df['Qtd_CHV_FUS_UC']), 0)

        cols_ajs = [c for c in df.columns if c.startswith('Qtd_AJS')]
        df[cols_ajs] = df[cols_ajs].apply(np.ceil)

        cols_val = ['VL_CZT_COM', 'VL_ISOL_DIS_COM', 'VL_ISOL_PIN_COM',
                    'VL_HASTE_COM', 'VL_PR_RAIO_COM', 'VL_CHV_FUS_COM']
        for c in cols_val:
            if c in df:
                media = df.loc[(df[c].notnull()) & (df[c] > 0), c].mean()
                df[c] = df[c].fillna(media if not np.isnan(media) else 0)

        df['VL_AJS_CRZ'] = df['Qtd_AJS_CRZ'] * df['VL_CZT_COM']
        df['VL_AJS_ISOL_DIS'] = df['Qtd_AJS_ISOL_DIS'] * df['VL_ISOL_DIS_COM']
        df['VL_AJS_ISOL_PIN'] = df['Qtd_AJS_ISOL_PIN'] * df['VL_ISOL_PIN_COM']
        df['VL_AJS_PIN']       = df['Qtd_AJS_PIN']       * df['VL_PIN_COM']
        df['VL_AJS_HASTE'] = df['Qtd_AJS_HASTE'] * df['VL_HASTE_COM']
        df['VL_AJS_PR_RAIO'] = df['Qtd_AJS_PR_RAIO'] * df['VL_PR_RAIO_COM']
        df['VL_AJS_CHV_FUS'] = df['Qtd_AJS_CHV_FUS'] * df['VL_CHV_FUS_COM']

    # ==========================================================
    # Função principal
    # ==========================================================
    @monitor_completo(st.session_state.LOGGER)
    def calcular_normativos(df, dic):
        calcular_postes(df, dic)
        calcular_cruzetas(df, dic)
        calcular_haste(df, dic)
        calcular_para_raios(df, dic)
        calcular_chaves_fusiveis(df, dic)
        calcular_normas_por_poste(df, dic)
        calcular_ajustes(df, dic)

        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(0, inplace=True)
        return df

    # ==========================================================
    # Execução
    # ==========================================================
    RESUMO = calcular_normativos(RESUMO, dic_NT_COM)
    NT_CMU = sql.imp_tbl_forma_001("NT_CMU", con=con, st=st, Empresa=Empresa)

    dic_NT = {
                    '1' : 'VL_ST_ChFus_RAR_Unit',
                    '2' : 'VL_ST_ChFus_RAU_Unit',
                    '3' : 'VL_ST_Crzta_RAR_Unit',
                    '4' : 'VL_ST_Crzta_RAU_Unit',
                    '5' : 'VL_ST_Haste_RAR_Unit',
                    '6' : 'VL_ST_Haste_RAU_Unit',
                    '7' : 'VL_ST_Isol_Dis_RAR_Unit',
                    '8' : 'VL_ST_Isol_Dis_RAU_Unit',
                    '9' : 'VL_ST_Isol_Pin_RAR_Unit',
                    '10' : 'VL_ST_Isol_Pin_RAU_Unit',
                    '11' : 'VL_ST_Pin_RAR_Unit',
                    '12' : 'VL_ST_Pin_RAU_Unit',
                    '13' : 'VL_ST_Praio_RAR_Unit',
                    '14' : 'VL_ST_Praio_RAU_Unit'
            }
    dic_NT_CMU = {}
    NT_CMU['Ano_Ref'] = pd.to_numeric(NT_CMU['Ano_Ref'], errors = 'coerce')

    for n in NT_CMU['Ano_Ref'].drop_duplicates().to_list():
        df = NT_CMU[NT_CMU['Ano_Ref'] == n].copy()
        dic_NT_CMU[n] = {}
        for k in range(len(df)):
            if isinstance(df.iloc[k, 2], str):
                df.iloc[k, 2] = df.iloc[k, 2].replace(",", ".")
                if df.iloc[k, 2] == "":
                    df.iloc[k, 2] = "0.0"
            dic_NT_CMU[n][dic_NT[df.iloc[k,3]]] = float(df.fillna(0).iloc[k,2])


    df_CMU = pd.DataFrame.from_dict(dic_NT_CMU).T.reset_index()
    df_CMU.columns = ['ANO', 'VL_ST_ChFus_RAR_Unit', 'VL_ST_ChFus_RAU_Unit', 'VL_ST_Crzta_RAR_Unit',
         'VL_ST_Crzta_RAU_Unit', 'VL_ST_Haste_RAR_Unit', 'VL_ST_Haste_RAU_Unit', 'VL_ST_Isol_Dis_RAR_Unit',
         'VL_ST_Isol_Dis_RAU_Unit', 'VL_ST_Isol_Pin_RAR_Unit', 'VL_ST_Isol_Pin_RAU_Unit', 'VL_ST_Pin_RAR_Unit',
         'VL_ST_Pin_RAU_Unit', 'VL_ST_Praio_RAR_Unit', 'VL_ST_Praio_RAU_Unit']
    RESUMO['ANO'] = pd.to_numeric(RESUMO['ANO'], errors='coerce')
    RESUMO = RESUMO.merge(df_CMU, how = 'left', on = ['ANO'])

    df_CMU = df_CMU.sort_values('ANO')
    for nm_col in ['VL_ST_ChFus_RAR_Unit', 'VL_ST_ChFus_RAU_Unit', 'VL_ST_Crzta_RAR_Unit',
         'VL_ST_Crzta_RAU_Unit', 'VL_ST_Haste_RAR_Unit', 'VL_ST_Haste_RAU_Unit', 'VL_ST_Isol_Dis_RAR_Unit',
         'VL_ST_Isol_Dis_RAU_Unit', 'VL_ST_Isol_Pin_RAR_Unit', 'VL_ST_Isol_Pin_RAU_Unit', 'VL_ST_Pin_RAR_Unit',
         'VL_ST_Pin_RAU_Unit', 'VL_ST_Praio_RAR_Unit', 'VL_ST_Praio_RAU_Unit']:
        valor_antigo = df_CMU[nm_col].dropna().iloc[0]
        RESUMO[nm_col] = RESUMO[nm_col].fillna(valor_antigo)

    RESUMO['VL_AJS_CA_CRZ'] = ((RESUMO['VL_ST_Crzta_RAR_Unit']).where(RESUMO['Nr_TI'] == '41',RESUMO['VL_ST_Crzta_RAU_Unit']) 
                               * RESUMO['Qtd_AJS_CRZ'])
    RESUMO['VL_AJS_CA_ISOL_DIS'] = ((RESUMO['VL_ST_Isol_Dis_RAR_Unit']).where(RESUMO['Nr_TI'] == '41',RESUMO['VL_ST_Isol_Dis_RAU_Unit']) 
                               * RESUMO['Qtd_AJS_ISOL_DIS'])
    RESUMO['VL_AJS_CA_ISOL_PIN'] = ((RESUMO['VL_ST_Isol_Pin_RAR_Unit']).where(RESUMO['Nr_TI'] == '41',RESUMO['VL_ST_Isol_Pin_RAU_Unit']) 
                               * RESUMO['Qtd_AJS_ISOL_PIN'])
    RESUMO['VL_AJS_CA_PIN'] = ((RESUMO['VL_ST_Pin_RAR_Unit']).where(RESUMO['Nr_TI'] == '41',RESUMO['VL_ST_Pin_RAU_Unit']) 
                               * RESUMO['Qtd_AJS_PIN'])
    RESUMO['VL_AJS_CA_HASTE'] = ((RESUMO['VL_ST_Haste_RAR_Unit']).where(RESUMO['Nr_TI'] == '41',RESUMO['VL_ST_Haste_RAU_Unit']) 
                               * RESUMO['Qtd_AJS_HASTE'])
    RESUMO['VL_AJS_CA_PR_RAIO'] = ((RESUMO['VL_ST_Praio_RAR_Unit']).where(RESUMO['Nr_TI'] == '41',RESUMO['VL_ST_Praio_RAU_Unit']) 
                               * RESUMO['Qtd_AJS_PR_RAIO'])
    RESUMO['VL_AJS_CA_CHV_FUS'] = ((RESUMO['VL_ST_ChFus_RAR_Unit']).where(RESUMO['Nr_TI'] == '41',RESUMO['VL_ST_ChFus_RAU_Unit']) 
                               * RESUMO['Qtd_AJS_CHV_FUS'])
    tbl_RES = RESUMO.groupby(['Nr_TI', 'Cd_SubODI'],dropna=False)[['VL_AJS_CRZ', 'VL_AJS_ISOL_DIS', 'VL_AJS_ISOL_PIN', 
                             'VL_AJS_PIN', 'VL_AJS_HASTE', 'VL_AJS_PR_RAIO',
                             'VL_AJS_CHV_FUS', 'VL_AJS_CA_CRZ', 'VL_AJS_CA_ISOL_DIS', 'VL_AJS_CA_ISOL_PIN', 
                             'VL_AJS_CA_PIN', 'VL_AJS_CA_HASTE', 'VL_AJS_CA_PR_RAIO',
                             'VL_AJS_CA_CHV_FUS']].sum().reset_index()

    tbl_RES.to_sql('RESUMO_AJS_RAC_COM', con, if_exists='replace', index=False)
    tbl_RES.to_csv(f"{dir_arq_saida}//RESUMO_AJS_RAC_COM_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//RESUMO_AJS_RAC_COM_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    RESUMO.to_sql('ANALITICO_AJS_RAC_COM', con, if_exists='replace', index=False)
    RESUMO.to_csv(f"{dir_arq_saida}//ANALITICO_AJS_RAC_COM_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//ANALITICO_AJS_RAC_COM_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def ANL_ODD(con, dir_arq_saida, Empresa, st = None):
    dt_ARQ = sql.max_arq("BAIXAS", con, Empresa)
    if dt_ARQ:
        SQLq = f"""
            SELECT *
            FROM BAIXAS t1 WHERE t1.dt_ARQ = {dt_ARQ}
            """
        BAIXAS = pd.read_sql(SQLq, con)
    else:
        if st:
            st.error('Falha ao importar o arquivo BAIXAS da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo BAIXAS da base local.')

    for n in BAIXAS.columns.to_list():
        if n[:2] in ['VL','Qt','Nr']:
            if isinstance(BAIXAS[n], str):
                BAIXAS[n] = BAIXAS[n].replace(",", ".")
            BAIXAS[n]=pd.to_numeric(BAIXAS[n],errors='coerce')
        elif n[:2] == 'Dt':
            BAIXAS[n]=pd.to_datetime(BAIXAS[n], errors='coerce',format='ISO8601')

    dt_ARQ = sql.max_arq("ROD", con, Empresa)
    if dt_ARQ:
        SQLq = f"""
            SELECT *
            FROM ROD t1 WHERE t1.dt_ARQ = '{dt_ARQ}'
            """
        ROD = pd.read_sql(SQLq, con)
    else:
        if st:
            st.error('Falha ao importar o arquivo ROD da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ROD da base local.')

    for n in ROD.columns.to_list():
        if n[:2] in ['Nr','Qt','VL'] and (ROD[n].dtype == 'object'):
            ROD[n]=pd.to_numeric(ROD[n].str.replace(',','.'),errors='coerce')

    dt_ARQ = sql.max_arq("ROS", con, Empresa)
    
    if dt_ARQ:
        SQLq = f"""
            SELECT *
            FROM ROS t1 WHERE t1.dt_ARQ = {dt_ARQ}
            """
        ROS = pd.read_sql(SQLq, con)
    else:
        if st:
            st.error('Falha ao importar o arquivo ROS da base local.')
            st.write(dt_ARQ)
            raise
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ROS da base local.')
        
    for n in ROS.columns.to_list():
        if (n[:2] in ['VL','Qt','Nr']) and (ROS[n].dtype == 'object'):
            ROS[n]=pd.to_numeric(ROS[n].str.replace(',','.',regex=True), errors='coerce')

    chave = ['Nr_TI','Nr_TUC','Nr_A1','Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5','Nr_A6']
    BX_CNL = BAIXAS[BAIXAS['Cd_UAR'] != 'UAR'].groupby(chave, dropna = False)[['Qtd_INI','Qtd_FIN','VL_VOC_INI','VL_VOC_FIN']].sum().reset_index()
    BX_CNL['QTD_BX'] = BX_CNL['Qtd_FIN'] - BX_CNL['Qtd_INI']
    BX_CNL['VL_BX'] = BX_CNL['VL_VOC_FIN'] - BX_CNL['VL_VOC_INI']
    BX_CNL.drop(['Qtd_INI','Qtd_FIN','VL_VOC_INI','VL_VOC_FIN'], axis=1,inplace=True)
    
    ROD_CNL = ROD[ROD['Nr_TUC'].notnull()].groupby(chave, dropna = False)[['Qtd','VL_tot']].sum().reset_index()
    TST_ESQ = BX_CNL.merge(ROD_CNL, how = 'left', on = chave)
    TST_DIR = BX_CNL.merge(ROD_CNL, how = 'right', on = chave)
    TST_TOT = pd.concat([TST_ESQ, TST_DIR]).drop_duplicates()
    
    TST_TOT['TST'] = 'NO'
    TST_TOT.loc[TST_TOT['QTD_BX'].isnull(), 'TST'] = 'Por que há dado no arquivo de ODD e não no de baixas?'
    TST_TOT.loc[TST_TOT['Qtd'].isnull(), 'TST'] = 'Por que há dado no arquivo de baixas e não no de ODD?'
    TST_TOT['Qtd'] = TST_TOT['Qtd'].fillna(0)
    TST_TOT['QTD_BX'] = TST_TOT['QTD_BX'].fillna(0)
    TST_TOT.loc[(TST_TOT['QTD_BX'] != 0) & 
                (abs(TST_TOT['Qtd'] - TST_TOT['QTD_BX']) / abs(TST_TOT['QTD_BX']) > 0.01) 
                ,'TST'] = 'Por que há diferença de quantidades?'
    TST_TOT.loc[(TST_TOT['QTD_BX'] != 0) & 
                (abs(TST_TOT['Qtd']-TST_TOT['QTD_BX'])/abs(TST_TOT['QTD_BX']) < 0.01) & (TST_TOT['VL_BX'] != 0) & (abs(TST_TOT['VL_tot']-TST_TOT['VL_BX'])/abs(TST_TOT['VL_BX']) > 0.1),'TST'] = 'Por que há diferença de valor?'
    TST_TOT.to_sql('ANL_BXS_ODD_TUCAGEM', con, if_exists='replace', index=False)
    TST_TOT.to_csv(f"{dir_arq_saida}//ANL_BXS_ODD_TUCAGEM_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//ANL_BXS_ODD_TUCAGEM_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    teste2 = ROS[['Cd_SubODI','Cd_ODD']].drop_duplicates()
    try:
        teste = ROD.groupby(['Cd_SubODI'], dropna = False)['VL_tot'].sum().reset_index()
        teste = teste.merge(teste2, how = 'left', on = 'Cd_SubODI')
    except:
        teste = ROD.groupby(['Cd_ODD'], dropna = False)['VL_tot'].sum().reset_index()
        teste = teste.merge(teste2, how = 'left', on = 'Cd_ODD')

    teste = teste[teste['Cd_SubODI'].isnull()][['Cd_ODD', 'VL_tot']].drop_duplicates()
    teste['TST'] = 'NO'
    teste.loc[abs(teste['VL_tot'])>1,'TST'] = 'Explicar do que se trata essa desativação e porque não houve obra associada'
    teste.to_sql('ANL_ODD_SEM_SUBODI_ASSOC', con, if_exists='replace', index=False)
    teste.to_csv(f"{dir_arq_saida}//ANL_ODD_SEM_SUBODI_ASSOC_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//ANL_ODD_SEM_SUBODI_ASSOC_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)

    teste2 = ROS[['Cd_SubODI','Cd_ODD','VL_CA_ST_ODD','VL_CA_MOP_ODD']].drop_duplicates()

    try:
        teste = pd.pivot_table(ROD[ROD['Cd_NG'].isin(['3','4'])],values = 'VL_tot', index = ['Cd_SubODI'], columns = ['Cd_NG'],
                                aggfunc = 'sum', dropna= False).reset_index()
        teste.columns = ['Cd_SubODI','VL_CA_MOP_ODD_ori', 'VL_CA_ST_ODD_ori']
        teste2 = teste2.merge(teste, how = 'left', on = 'Cd_SubODI')
    except:
        teste = pd.pivot_table(ROD[ROD['Cd_NG'].isin(['3','4'])],values = 'VL_tot', index = ['Cd_ODD'], columns = ['Cd_NG'],
                                aggfunc = 'sum', dropna= False).reset_index()
        teste.columns = ['Cd_ODD','VL_CA_MOP_ODD_ori', 'VL_CA_ST_ODD_ori']
        teste2 = teste2.merge(teste, how = 'left', on = 'Cd_ODD')

    for n in ['VL_CA_MOP_ODD_ori', 'VL_CA_ST_ODD_ori','VL_CA_ST_ODD','VL_CA_MOP_ODD']:
        teste2[n] = teste2[n].fillna(0)
    teste2['TST'] = 'NO'
    teste2.loc[(abs(teste2['VL_CA_ST_ODD'] + teste2['VL_CA_MOP_ODD'] - teste2['VL_CA_ST_ODD_ori'] - teste2['VL_CA_MOP_ODD_ori'])<1)
                ,'TST'] = 'OK'
    teste2.loc[(abs(teste2['VL_CA_ST_ODD'] + teste2['VL_CA_MOP_ODD'] - teste2['VL_CA_ST_ODD_ori'] - teste2['VL_CA_MOP_ODD_ori'])<1)
                & (abs(teste2['VL_CA_ST_ODD'] - teste2['VL_CA_ST_ODD_ori'])>1)
                ,'TST'] = 'Possivel inversão na classificação de natureza de gasto em um dos arquivos (ROS ou ROD), justificar.'
    teste2.loc[((teste2['VL_CA_ST_ODD'] + teste2['VL_CA_MOP_ODD'] - teste2['VL_CA_ST_ODD_ori'] - teste2['VL_CA_MOP_ODD_ori'])<-1)
                ,'TST'] = 'Dados de CA lançados no ROS são menores que os do arquivo de ODD, justificar.'
    teste2.loc[((teste2['VL_CA_ST_ODD'] + teste2['VL_CA_MOP_ODD'] - teste2['VL_CA_ST_ODD_ori'] - teste2['VL_CA_MOP_ODD_ori'])>1)
                ,'TST'] = 'Dados de CA lançados no ROS são maiores que os do arquivo de ODD, justificar.'
    teste2.to_sql('ANL_ROS_ODD_CA', con, if_exists='replace', index=False)
    teste2.to_csv(f"{dir_arq_saida}//ANL_ROS_ODD_CA_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//ANL_ROS_ODD_CA_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def anl_OBRAS_EMERG(con, dir_arq_saida,Empresa, st=None):
    dt_ARQ = sql.max_arq("LST_OBRAS_EMERG", con, Empresa)
    if not dt_ARQ:
        if st: st.warning("Falta arquivo de obras emergenciais")
        return None

    dt_ARQ = sql.max_arq("LST_MAT_OBRAS_EMERG", con, Empresa)
    if not dt_ARQ:
        if st: st.warning("Falta arquivo de materiais de obras emergenciais")
        return None

    if st:
        pgr = st.progress(0, "Criando indexes nas tabelas necessárias, caso inexista indexes.")

    con.execute("CREATE INDEX IF NOT EXISTS idx_roa_dt_arq_ng ON ROA(dt_ARQ, Cd_NG);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_roa_cod_item ON ROA(COD_ITEM);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_roa_cd_subodi ON ROA(Cd_SubODI);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_lst_mat_cod_item ON LST_MAT(COD_ITEM);")

    if st: pgr.progress(5, "Buscando arquivo de baixas.")
    dt_ARQ = sql.max_arq("BAIXAS", con, Empresa)
    if dt_ARQ:
        SQLq = f"""
            SELECT *
            FROM BAIXAS t1 WHERE t1.dt_ARQ = {dt_ARQ}
            """
        BAIXAS = pd.read_sql(SQLq, con)
    else:
        if st:
            st.error('Falha ao importar o arquivo BAIXAS da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo BAIXAS da base local.')

    for n in BAIXAS.columns.to_list():
        if n[:2] in ['VL','Qt','Nr']:
            if BAIXAS[n].dtype == 'object':
                BAIXAS[n]=pd.to_numeric(BAIXAS[n].str.replace(',','.',regex=True),errors='coerce')
        elif n[:2] == 'Dt':
            BAIXAS[n]=pd.to_datetime(BAIXAS[n], errors='coerce',format='%Y/%m/%d')


    if st: pgr.progress(10, "Buscando arquivo do ROA.")

    def importar_roa(
                        con,
                        Empresa,
                        sql,
                        st=None
                    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

        colunas = {
                        "ROA": [
                            "COD_ITEM",
                            "Nr_TUC_ROA",
                            "DESCR_ITEM",
                            "Nr_FC",
                        ],
                        "ROAq": [
                            "Ide_RO_Analitico",
                            "Nr_TUC_ROA",
                            "DESCR_ITEM",
                            "Nr_FC",
                            "Cd_SubODI",
                            "Dt_Lcmto",
                            "QTD_UC",
                        ],
                        "ROAca": [
                            "Cd_SubODI",
                            "VL_CA",
                        ],
                    }

        def dataframe_vazio(tipo: str) -> pd.DataFrame:
            return pd.DataFrame(columns=colunas[tipo])

        def tratar_erro(mensagem: str):
            if st is not None:
                st.error(mensagem)
                return (
                            dataframe_vazio("ROA"),
                            dataframe_vazio("ROAq"),
                            dataframe_vazio("ROAca"),
                        )

            raise UserWarning(mensagem)

        dt_roa = sql.max_arq("ROA", con, Empresa)
        dt_lst_mat = sql.max_arq("LST_MAT", con, Empresa)

        if not dt_roa:
            return tratar_erro(
                                    "Falha ao importar o arquivo ROA da base local."
                                )

        if not dt_lst_mat:
            return tratar_erro(
                                    "Falha ao importar o arquivo LST_MAT da base local."
                                )

        query = f"""
                        WITH
                        ROA_f AS (
                            SELECT
                                Ide_RO_Analitico,
                                COD_ITEM,
                                Nr_TUC,
                                Cd_SubODI,
                                Dt_Lcmto,
                                Qtd
                            FROM ROA
                            WHERE dt_ARQ = ?
                            AND Cd_NG = '1'
                        ),

                        LST_MAT_f AS (
                            SELECT
                                COD_ITEM,
                                DESCR_ITEM,
                                Nr_FC
                            FROM LST_MAT
                            WHERE dt_ARQ = ?
                        ),

                        ROA_itens AS (
                            SELECT DISTINCT
                                'ROA'                  AS origem,
                                NULL                   AS Ide_RO_Analitico,
                                r.COD_ITEM             AS COD_ITEM,
                                r.Nr_TUC               AS Nr_TUC_ROA,
                                m.DESCR_ITEM           AS DESCR_ITEM,
                                m.Nr_FC                AS Nr_FC,
                                NULL                   AS Cd_SubODI,
                                NULL                   AS Dt_Lcmto,
                                NULL                   AS QTD_UC,
                                NULL                   AS VL_CA
                            FROM ROA_f AS r
                            LEFT JOIN LST_MAT_f AS m
                                ON r.COD_ITEM = m.COD_ITEM
                        ),

                        ROA_quantidades AS (
                            SELECT
                                'ROAq'                 AS origem,
                                Ide_RO_Analitico       AS Ide_RO_Analitico,
                                NULL                   AS COD_ITEM,
                                r.Nr_TUC               AS Nr_TUC_ROA,
                                m.DESCR_ITEM           AS DESCR_ITEM,
                                m.Nr_FC                AS Nr_FC,
                                r.Cd_SubODI            AS Cd_SubODI,
                                r.Dt_Lcmto             AS Dt_Lcmto,
                                SUM(r.Qtd)             AS QTD_UC,
                                NULL                   AS VL_CA
                            FROM ROA_f AS r
                            LEFT JOIN LST_MAT_f AS m
                                ON r.COD_ITEM = m.COD_ITEM
                            GROUP BY
                                r.Ide_RO_Analitico,
                                r.Nr_TUC,
                                r.Cd_SubODI,
                                r.Dt_Lcmto,
                                m.DESCR_ITEM,
                                m.Nr_FC
                        ),

                        ROA_custos_adicionais AS (
                            SELECT
                                'ROAca'                AS origem,
                                NULL                   AS Ide_RO_Analitico,
                                NULL                   AS COD_ITEM,
                                NULL                   AS Nr_TUC_ROA,
                                NULL                   AS DESCR_ITEM,
                                NULL                   AS Nr_FC,
                                Cd_SubODI              AS Cd_SubODI,
                                NULL                   AS Dt_Lcmto,
                                NULL                   AS QTD_UC,
                                SUM(VL_tot)            AS VL_CA
                            FROM ROA
                            WHERE dt_ARQ = ?
                            AND Cd_CA IN ('1','2','3','4','5','6')
                            GROUP BY
                                Cd_SubODI
                        )

                        SELECT * FROM ROA_itens

                        UNION ALL

                        SELECT * FROM ROA_quantidades

                        UNION ALL

                        SELECT * FROM ROA_custos_adicionais
                    """

        try:
            resultado = pd.read_sql_query(
                                                query,
                                                con,
                                                params=(
                                                    dt_roa,
                                                    dt_lst_mat,
                                                    dt_roa,
                                                ),
                                            )

        except Exception as erro:
            mensagem = (
                            "Falha ao consultar os dados de ROA e LST_MAT "
                            f"na base local: {erro}"
                        )
            return tratar_erro(mensagem)

        resultados = {}

        for origem, colunas_origem in colunas.items():
            resultados[origem] = (
                                    resultado.loc[
                                        resultado["origem"].eq(origem),
                                        colunas_origem,
                                    ]
                                    .reset_index(drop=True)
                                )

        return (
                    resultados["ROA"],
                    resultados["ROAq"],
                    resultados["ROAca"],
                )
    
    ROA, ROAq, ROAca = importar_roa(
                                        con=con,
                                        Empresa=Empresa,
                                        sql=sql,
                                        st=st,
                                    )

    if st: pgr.progress(15, "Buscando arquivo do ROD.")
    ROD = sql.imp_tbl_forma_001("ROD", con=con, st=st, Empresa=Empresa)
    if st: pgr.progress(20, "Buscando arquivo ROS.")
    ROS = sql.imp_tbl_forma_001("ROS", con=con, st=st, Empresa=Empresa)
    if st: pgr.progress(25, "Buscando arquivo LST_OBRAS_EMERG.")
    OBR_EM = sql.imp_tbl_forma_001("LST_OBRAS_EMERG", con=con, st=st, Empresa=Empresa)
    if st: pgr.progress(30, "Buscando arquivo LST_MAT_OBRAS_EMERG.")
    OBR_EM_MAT = sql.imp_tbl_forma_001("LST_MAT_OBRAS_EMERG", con=con, st=st, Empresa=Empresa)

    for n in ROD.columns.to_list():
        if n[:2] in ['Nr']:
            ROD[n]=pd.to_numeric(ROD[n].str.replace(',','.'), errors='coerce')
    
    if st: pgr.progress(35, "Iniciando análises.")
    df_prov = ROA.groupby('COD_ITEM', dropna=False, as_index=False).agg({'Nr_TUC_ROA': list})

    df_prov.columns = ['COD_ITEM','LST_UC']
    
    ROA = ROA.merge(df_prov, how='left', on = 'COD_ITEM')
    ROA.drop_duplicates(subset='COD_ITEM', inplace = True)

    df1 = OBR_EM_MAT.merge(
                                ROA,
                                how="left",
                                on="COD_ITEM",
                                validate="m:m"
                            )
    df1["Nr_TUC"] = df1["Nr_TUC"].astype("string").str.strip()
    df1["LST_UC"] = df1["LST_UC"].apply(
                                            lambda valor: valor
                                            if isinstance(valor, (list, tuple, set))
                                            else []
                                        )

    df1["OBS_SFF"] = "NO"

    tem_tuc_roa = df1["Nr_TUC_ROA"].notna()
    tem_tuc_oe = df1["Nr_TUC"].notna()

    df1.loc[
                tem_tuc_roa & ~tem_tuc_oe,
                "OBS_SFF"
            ] = "Por que este material não foi TUCADO?"


    df1.loc[
                ~tem_tuc_roa & tem_tuc_oe,
                "OBS_SFF"
            ] = "Por que este material está TUCADO no arquivo OE?"


    df1.loc[
                ~tem_tuc_roa & ~tem_tuc_oe,
                "OBS_SFF"
            ] = "Tem certeza de que se trata de UC/UAR?"

    tuc_divergente = pd.Series(
                                [
                                    pd.notna(tuc)
                                    and lista is not None
                                    and tuc not in lista
                                    for tuc, lista in zip(df1["Nr_TUC"], df1["LST_UC"])
                                ],
                                index=df1.index
                            )

    df1.loc[
                tem_tuc_roa & tem_tuc_oe & tuc_divergente,
                "OBS_SFF"
            ] = (
                    "Por que a TUCAGEM entre o ROA e a lista de materiais "
                    "de obras emergenciais difere?"
                )

    df1_resultado = df1.loc[df1["Nr_TUC_ROA"].notna()].copy()
    df1_resultado['LST_UC'] = df1_resultado['LST_UC'].apply(json.dumps)
    df1_resultado.to_sql('Tst_OEM_MAT', con, if_exists='replace', index=False)
    df1_resultado.to_csv(f"{dir_arq_saida}//Tst_OEM_MAT_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//Tst_OEM_MAT_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    OBR_EM = OBR_EM.rename(columns={'Tp_EQP' : 'TP_EQP'})

    campos_obrigatorios = [
                            "TP_EQP",
                            "Cd_CONJ",
                            "Dt_REST",
                            "Dt_CHEG",
                            "Hr_REST",
                            "Hr_CHEG",
                            "Txt_OCORR",
                          ]

    mascara_ausentes = (
                            OBR_EM[campos_obrigatorios]
                            .isna()
                            .any(axis=1)
                            |
                            OBR_EM[campos_obrigatorios]
                            .astype("string")
                            .apply(lambda coluna: coluna.str.strip().eq(""))
                            .any(axis=1)
                        )

    df1 = OBR_EM.loc[mascara_ausentes].copy()
    
    if st:
        pgr.progress(
                        40,
                        "Verificando dados ausentes no arquivo de obras emergenciais."
                    )

    df1["CAMPOS_AUSENTES"] = df1[campos_obrigatorios].apply(
                                                                lambda linha: ", ".join(
                                                                    campo
                                                                    for campo, valor in linha.items()
                                                                    if pd.isna(valor) or str(valor).strip() == ""
                                                                ),
                                                                axis=1,
                                                            )

    if len(df1)>0:
        df1["OBS_SFF"] = (
                                "DADOS AUSENTES: "
                                + df1["CAMPOS_AUSENTES"]
                                + ". PREENCHER OU JUSTIFICAR."
                            )

        df1.to_sql('Tst_OEM', con, if_exists='replace', index=False)
        df1.to_csv(f"{dir_arq_saida}//Tst_OEM_{Empresa}.csv", sep="|", decimal=',', encoding="utf-8", chunksize=100_000)
        if st:
            registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf"{dir_arq_saida}//Tst_OEM_{Empresa}.csv",
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)

    df1 = OBR_EM[~(OBR_EM['TP_EQP'].isnull() | OBR_EM['Cd_CONJ'].isnull() | OBR_EM['Dt_REST'].isnull() | OBR_EM['Dt_CHEG'].isnull()
          | OBR_EM['Hr_REST'].isnull() | OBR_EM['Hr_CHEG'].isnull() | OBR_EM['Txt_OCORR'].isnull())].copy()
    df2 = OBR_EM_MAT[OBR_EM_MAT['Nr_TUC'].notnull()][['Id_OBR_EM','COD_ITEM','Nr_TUC','Qtd']].copy()
    df3 = pd.pivot_table(df2, index=['Id_OBR_EM'],columns=['Nr_TUC'],values='Qtd', dropna=False, aggfunc='sum').reset_index()
    df3 = df3.fillna(0)
    df3['Id_OBR_EM'] = df3['Id_OBR_EM'].astype(str)
    df1n = df1.merge(df3, how='outer',on='Id_OBR_EM', indicator=True)
    dic_mot = {
                'both' : 'NO',
                'left_only' : 'Apenas na lista de obras, sem material',
                'right_only' : 'Apenas na lista de materiais, sem obra',
              }
    df1n['OBS01'] = df1n['_merge'].replace(dic_mot)
    df2n = df1[['Id_OBR_EM','Nr_Ordem','Txt_OCORR','Dt_REST']]
    df2n = df2n.merge(df2, how='outer', on='Id_OBR_EM', indicator=True)
    df2n['OBS01'] = df2n['_merge'].replace(dic_mot)

    def relacionar_dataframes(
                                df_a: pd.DataFrame,
                                    df_b: pd.DataFrame,
                                    coluna_indice_a: str,
                                    coluna_indice_b: str,
                                    coluna_codigo: str,
                                    coluna_data: str,
                                    coluna_quantidade: str,
                                    peso_codigo: float = 0.60,
                                    peso_data: float = 0.25,
                                    peso_quantidade: float = 0.15,
                                    escala_data_dias: float = 30,
                                    quantidade_candidatos: int = 1,
                                    janela_data_dias: int = 90,
                                    candidatos_por_data: int = 20,
                                ) -> pd.DataFrame:


        soma_pesos = peso_codigo + peso_data + peso_quantidade

        if not np.isclose(soma_pesos, 1.0):
            raise ValueError(
                                "A soma dos pesos deve ser igual a 1. "
                                f"Soma informada: {soma_pesos:.4f}"
                            )

        if quantidade_candidatos < 1:
            raise ValueError(
                                "quantidade_candidatos deve ser maior ou igual a 1."
                            )

        if candidatos_por_data < quantidade_candidatos:
            raise ValueError(
                                "candidatos_por_data deve ser maior ou igual a "
                                "quantidade_candidatos."
                            )

        if escala_data_dias <= 0:
            raise ValueError("escala_data_dias deve ser maior que zero.")

        if janela_data_dias < 0:
            raise ValueError("janela_data_dias não pode ser negativa.")

        colunas_a = [
                        coluna_indice_a,
                        coluna_codigo,
                        coluna_data,
                        coluna_quantidade,
                    ]

        colunas_b = [
                        coluna_indice_b,
                        coluna_codigo,
                        coluna_data,
                        coluna_quantidade,
                    ]

        faltantes_a = [
                            coluna for coluna in colunas_a
                            if coluna not in df_a.columns
                        ]

        faltantes_b = [
                            coluna for coluna in colunas_b
                            if coluna not in df_b.columns
                        ]

        if faltantes_a:
            raise KeyError(
                                f"Colunas ausentes no DataFrame A: {faltantes_a}"
                            )

        if faltantes_b:
            raise KeyError(
                                f"Colunas ausentes no DataFrame B: {faltantes_b}"
                            )

        a = (
                df_a[colunas_a]
                .rename(
                    columns={
                        coluna_indice_a: "INDEX_A",
                        coluna_codigo: "CODIGO",
                        coluna_data: "DATA_A",
                        coluna_quantidade: "QTD_A",
                    }
                )
                .copy()
            )

        b = (
                df_b[colunas_b]
                .rename(
                    columns={
                        coluna_indice_b: "INDEX_B",
                        coluna_codigo: "CODIGO",
                        coluna_data: "DATA_B",
                        coluna_quantidade: "QTD_B",
                    }
                )
                .copy()
            )

        for dataframe in (a, b):
            dataframe["CODIGO"] = (
                                    dataframe["CODIGO"]
                                    .astype("string")
                                    .str.strip()
                                    .str.zfill(3)
                                )

        a["DATA_A"] = (
                            pd.to_datetime(
                                a["DATA_A"],
                                format="%Y-%m-%d",
                                errors="coerce",
                            )
                            + pd.offsets.MonthEnd(0)
                        )

        b["DATA_B"] = (
                            pd.to_datetime(
                                b["DATA_B"],
                                format="%Y-%m-%d",
                                errors="coerce",
                            )
                            + pd.offsets.MonthEnd(0)
                        )

        a["QTD_A"] = pd.to_numeric(a["QTD_A"], errors="coerce")
        b["QTD_B"] = pd.to_numeric(b["QTD_B"], errors="coerce")

        a_validos = a.dropna(subset=["CODIGO", "DATA_A"]).copy()
        b_validos = b.dropna(subset=["CODIGO", "DATA_B"]).copy()
        a_validos = a_validos.sort_values(
                                                ["DATA_A", "CODIGO", "INDEX_A"]
                                            )
        b_validos = b_validos.sort_values(
                                                ["DATA_B", "CODIGO", "INDEX_B"]
                                            )
        tolerancia = pd.Timedelta(days=janela_data_dias)

        anterior = pd.merge_asof(
                                    a_validos,
                                    b_validos,
                                    left_on="DATA_A",
                                    right_on="DATA_B",
                                    by="CODIGO",
                                    direction="backward",
                                    tolerance=tolerancia,
                                    allow_exact_matches=True,
                                )

        posterior = pd.merge_asof(
                                    a_validos,
                                    b_validos,
                                    left_on="DATA_A",
                                    right_on="DATA_B",
                                    by="CODIGO",
                                    direction="forward",
                                    tolerance=tolerancia,
                                    allow_exact_matches=True,
                                )

        candidatos = pd.concat(
                                    [anterior, posterior],
                                    ignore_index=True,
                                )

        candidatos = candidatos.dropna(subset=["INDEX_B"])

        candidatos = candidatos.drop_duplicates(
                                                    subset=["INDEX_A", "INDEX_B"]
                                                )

        candidatos["CODIGO_A"] = candidatos["CODIGO"]
        candidatos["CODIGO_B"] = candidatos["CODIGO"]

        candidatos["SIM_CODIGO"] = 1.0

        candidatos["DIF_DATA_DIAS"] = (
                                            candidatos["DATA_A"] - candidatos["DATA_B"]
                                        ).abs().dt.days

        candidatos["SIM_DATA"] = np.exp(
                                            -candidatos["DIF_DATA_DIAS"] / escala_data_dias
                                        )

        candidatos["DIF_QTD"] = (
                                    candidatos["QTD_A"] - candidatos["QTD_B"]
                                ).abs()

        denominador = (
                            candidatos[["QTD_A", "QTD_B"]]
                            .abs()
                            .max(axis=1)
                        )

        candidatos["SIM_QTD"] = np.where(
                                            denominador.eq(0),
                                            np.where(
                                                candidatos["DIF_QTD"].eq(0),
                                                1.0,
                                                0.0,
                                            ),
                                            1 - candidatos["DIF_QTD"] / denominador,
                                        )

        candidatos["SIM_QTD"] = (
                                    candidatos["SIM_QTD"]
                                    .clip(lower=0, upper=1)
                                    .fillna(0)
                                )

        candidatos["SCORE"] = (
                                    peso_codigo * candidatos["SIM_CODIGO"]
                                    + peso_data * candidatos["SIM_DATA"]
                                    + peso_quantidade * candidatos["SIM_QTD"]
                                )

        candidatos = (
                            candidatos
                            .sort_values(
                                [
                                    "INDEX_A",
                                    "SCORE",
                                    "DIF_DATA_DIAS",
                                    "DIF_QTD",
                                ],
                                ascending=[True, False, True, True],
                                na_position="last",
                            )
                            .groupby("INDEX_A", sort=False, as_index=False)
                            .head(quantidade_candidatos)
                            .copy()
                        )

        candidatos["POSICAO_CANDIDATO"] = (
                                            candidatos
                                            .groupby("INDEX_A", sort=False)
                                            .cumcount()
                                            .add(1)
                                        )

        colunas_resultado = [
                                "INDEX_A",
                                "INDEX_B",
                                "POSICAO_CANDIDATO",
                                "CODIGO_A",
                                "CODIGO_B",
                                "DATA_A",
                                "DATA_B",
                                "QTD_A",
                                "QTD_B",
                                "SIM_CODIGO",
                                "DIF_DATA_DIAS",
                                "SIM_DATA",
                                "DIF_QTD",
                                "SIM_QTD",
                                "SCORE",
                            ]

        return (
                    candidatos[colunas_resultado]
                    .sort_values(["INDEX_A", "POSICAO_CANDIDATO"])
                    .reset_index(drop=True)
                )
    ROAqANL = ROAq.reset_index()[['index','Ide_RO_Analitico','Nr_TUC_ROA','Dt_Lcmto','QTD_UC']].rename(columns={'Nr_TUC_ROA':'Nr_TUC',
                                                                                             'QTD_UC' : 'QTD'})

    df2nANL = df2n.reset_index()[['index','Nr_Ordem','Nr_TUC','Dt_REST','Qtd']].rename(columns={'Dt_REST':'Dt_Lcmto',
                                                                                             'Qtd' : 'QTD'})
    relacao = relacionar_dataframes(
                                    df_a=ROAqANL,
                                    df_b=df2nANL,
                                    coluna_indice_a="Ide_RO_Analitico",
                                    coluna_indice_b="Nr_Ordem",
                                    coluna_codigo="Nr_TUC",
                                    coluna_data="Dt_Lcmto",
                                    coluna_quantidade="QTD",
                                    quantidade_candidatos=1,
                                )
    saida = relacao.drop_duplicates(subset=['INDEX_B'], keep='first')

    saida.to_csv(f"{dir_arq_saida}//Tst_CONC_BAIXAS_ROA_{Empresa}.csv", sep="|", decimal=',', encoding="utf-8", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//Tst_CONC_BAIXAS_ROA_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    df_COMB = saida[saida['SCORE']==1].copy()

    if len(df_COMB)>0:
        df_COMB = df_COMB[['INDEX_A','INDEX_B']].copy().rename(columns={'INDEX_A' : 'Ide_RO_Analitico','INDEX_B' : 'Nr_Ordem'})

        ladoA = df_COMB.merge(ROAq, how='left', on = 'Ide_RO_Analitico')
        ladoB = df2n[df2n['Nr_TUC'].notnull()][['Nr_Ordem','Nr_TUC','Txt_OCORR','Qtd']]
        ladoB.columns = ['Nr_Ordem', 'Nr_TUC','Txt_OCORR','Qtd_OCORR']

        if len(ladoA)>0:
            ladoA.columns = ['Ide_RO_Analitico', 'Nr_Ordem', 'Nr_TUC', 'DESCR_ITEM','Nr_FC', 'Cd_SubODI', 'Dt_Lcmto','QTD_UC']
            teste = ladoA.merge(ladoB, how='outer', on = ['Nr_Ordem', 'Nr_TUC'], indicator=True)
            dic_map = {
                "both" : "NO",
                "left_only" : "Somente no ROA",
                "right_only" : "Algoritmo falhou na localização do material no ROA (UC, DATA e QTD)"
            }
            teste['OBS1'] = teste["_merge"].replace(dic_map)
            for k in teste.columns.to_list():
                if (k in ['Qtd_OCORR','QTD_UC','Nr_FC']) & (teste[k].dtype == 'object'):
                    teste[k] = pd.to_numeric(teste[k].str.replace(",","."), errors='coerce')

            if st: pgr.progress(45, "Quantidades divergentes entre ROA e Obras Emergenciais.")

            teste['DELTA'] = teste['QTD_UC'].fillna(0) - teste['Qtd_OCORR'].fillna(0)
            teste['OBS2'] = 'NO'
            teste.loc[abs(teste['DELTA']) > 0.1, 'OBS2'] = 'Quantidades não conferem, entre ROA e Obras Emergenciais'
            teste['OBS_SFF'] = np.where(teste['OBS1'] != "NO",
                                        teste['OBS1'],
                                        np.where(teste['OBS2'] != "NO",
                                        teste['OBS2'],
                                        "NO"
                                        )

                                        )
            teste = teste.drop(columns=['_merge','OBS1','OBS2'])
            teste.to_sql('Tst_QTD_MAT_ROA_OBR_EM', con, if_exists='replace', index=False)
            teste.to_csv(f"{dir_arq_saida}//Tst_QTD_MAT_ROA_OBR_EM_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
            if st:
                registrar_artefato(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                file_path = rf"{dir_arq_saida}//Tst_QTD_MAT_ROA_OBR_EM_{Empresa}.csv",
                                tipo_artefato = "SAIDA", 
                                calcular_hash = True)
    if st:
        pgr.empty()
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def anl_LADO_A_vs_B(con, dir_arq_saida, Empresa, dt_ini_proc, dt_fim_proc, st=None):
    if not sql.existe_tabela('ORIGEM_ATIVOS_INCREMENTAL', con):
        st.error("Inexiste arquivo para lado A e B")
        return
    if st.session_state.dt_fim > date.today():
        st.info("Teste não aplicado na anual")
        return None
    
    SQLq = f"""
                SELECT 
                    t1.Nr_TUC,
                    t1.Cd_UND_AIS AS UNID_INCR,
                    SUM(t1.Qtd_AIS) AS QTD_INCR 
                FROM 
                    INCR t1 
                WHERE 
                    t1.dt_ARQ = ? AND t1.Cd_CONC IN (1,3) AND t1.FLG_ELIG=1 AND t1.Cd_UAR <> 'UAR'
                GROUP BY 
                    t1.Nr_TUC,
                    t1.Cd_UND_AIS
            """
    INCR = sql.imp_tbl_forma_001('INCR', SQLq=SQLq, con=con, st=st, Empresa=Empresa)

    dt_arq = sql.max_arq("INCR", con, empresa=Empresa)
    if dt_arq:
        con.execute("DROP TABLE IF EXISTS TB_INCR_RESUMO_LADO_A")

        con.execute(f"""
                            CREATE TABLE TB_INCR_RESUMO_LADO_A AS
                            SELECT 
                                t1.Nr_TUC,
                                t1.COD_ITEM,
                                t1.Txt_DESC_TECN,
                                t1.Cd_UND_AIS AS UNID_INCR,
                                SUM(t1.Qtd_AIS) AS QTD_INCR 
                            FROM INCR t1
                            WHERE 
                                t1.dt_ARQ = ?
                                AND t1.Cd_CONC IN (1,3)
                                AND t1.FLG_ELIG = 1
                                AND t1.Cd_UAR <> 'UAR'
                            GROUP BY 
                                t1.Nr_TUC,
                                t1.COD_ITEM,
                                t1.Txt_DESC_TECN,
                                t1.Cd_UND_AIS
                        """, (dt_arq,))

        con.commit()

    SQLq = f"""
            SELECT 
                t1.Nr_TUC,
                SUM(t1.Qtd_AIS) AS QTD_INCRinc, 
                t1.Cd_UND_AIS AS UNID_INCRinc
            FROM 
                INCR t1 
            WHERE 
                t1.FLG_INCOR_OE = 1 AND t1.dt_ARQ = ? AND t1.Cd_CONC IN (1,3) AND t1.FLG_ELIG=1
            GROUP BY 
                t1.Nr_TUC,
                t1.Cd_UND_AIS
            """
    INCRinc = sql.imp_tbl_forma_001('INCR', SQLq=SQLq, con=con, st=st, Empresa=Empresa)

    SQLq = f"""
            SELECT 
                t1.Nr_TUC,
                SUM(t1.Qtd_AIS) AS QTD_INCRdoa, 
                t1.Cd_UND_AIS AS UNID_INCRdoa
            FROM 
                INCR t1 
            WHERE 
                t1.FLG_DOA_OE = 1 AND t1.dt_ARQ = ? AND t1.Cd_CONC IN (1,3) AND t1.FLG_ELIG=1
            GROUP BY 
                t1.Nr_TUC,
                t1.Cd_UND_AIS
            """
    INCRdoa = sql.imp_tbl_forma_001('INCR', SQLq=SQLq, con=con, st=st, Empresa=Empresa)

   
    if st.session_state.dt_fim >= date.today():
        st.warning(f"Buscando alternativa para INCR, período intercalar de análise. Início em: {datetime.now().strftime('%H:%M:%S')}")
        SQLq = f"""
                    SELECT
                        t1.Nr_TUC, 
                        SUM(t1.Qtd) AS QTD_INCR, 
                        t1.Unidade AS UNID_INCR
                    FROM 
                        ROA t1 LEFT JOIN ROS t2 
                    ON 
                        t1.Cd_SubODI=t2.Cd_SubODI
                    WHERE 
                        t1.dt_ARQ = ? AND t2.dt_ARQ = ? AND t1.Cd_NG  = "1"
                    GROUP BY 
                        t1.Nr_TUC,
                        t1.Unidade
                    """
        INCR = sql.imp_tbl_forma_002('INCR', 'ROS', SQLq=SQLq, con=con, st=st, Empresa=Empresa)

        SQLq = f"""
                    SELECT
                        t1.Nr_TUC, 
                        SUM(t1.Qtd) AS QTD_INCR, 
                        t1.Unidade AS UNID_INCR
                    FROM 
                        ROA t1 LEFT JOIN ROS t2 
                    ON 
                        t1.Cd_SubODI=t2.Cd_SubODI
                    WHERE 
                        t1.dt_ARQ = ? AND t2.dt_ARQ = ? AND t1.Cd_NG  = "1" AND t2.Cd_Tipo_OE = "8"
                    GROUP BY 
                        t1.Nr_TUC,
                        t1.Unidade
                    """
        INCRinc = sql.imp_tbl_forma_002('INCR', 'ROS', SQLq=SQLq, con=con, st=st, Empresa=Empresa)

        SQLq = f"""
                    SELECT
                        t1.Nr_TUC, 
                        SUM(t1.Qtd) AS QTD_INCR, 
                        t1.Unidade AS UNID_INCR
                    FROM 
                        ROA t1 LEFT JOIN ROS t2 
                    ON 
                        t1.Cd_SubODI=t2.Cd_SubODI
                    WHERE 
                        t1.dt_ARQ = ? AND t2.dt_ARQ = ? AND t1.Cd_NG  = "1" AND t2.Cd_Tipo_OE = "4"
                    GROUP BY 
                        t1.Nr_TUC,
                        t1.Unidade
                    """
        INCRdoa = sql.imp_tbl_forma_002('INCR', 'ROS', SQLq=SQLq, con=con, st=st, Empresa=Empresa)

    SQLq = f"""
            SELECT 
                t1.COD_ITEM,
                SUM(t1.Qtd) AS QTD_AO, 
                t1.Cd_UND AS UNID_AO
            FROM 
                AO t1 
            WHERE 
                t1.dt_ARQ = ? AND t1.Dt_LCMTO = (SELECT MAX(Dt_LCMTO) FROM AO)
            GROUP BY 
                t1.COD_ITEM,
                t1.Cd_UND
            """
    AO = sql.imp_tbl_forma_001('AO', SQLq=SQLq, con=con, st=st, Empresa=Empresa)
    AO.to_sql("TB_AO_LADO_A", con, if_exists='replace', index=False)

    SQLq = f"""
                SELECT
                    t1.COD_ITEM, 
                    t1.Unidade AS UND_ROA,
                    t2.DESCR_ITEM,
                    t1.Nr_TUC,
                    SUM(t1.Qtd) AS QTD_ROA  
                FROM ROA t1
                LEFT JOIN LST_MAT t2 
                    ON t1.COD_ITEM = t2.COD_ITEM
                    AND t2.dt_ARQ = ?
                WHERE 
                    t1.Cd_NG = 1
                    AND t1.dt_ARQ = ?
                GROUP BY
                    t1.COD_ITEM, 
                    t1.Unidade,
                    t2.DESCR_ITEM,
                    t1.Nr_TUC
            """
    ROA = sql.imp_tbl_forma_002('LST_MAT', 'ROA', SQLq=SQLq, con=con, st=st, Empresa=Empresa)
    ROA.to_sql("TB_ROA_LADO_A", con, if_exists='replace', index=False)

    SQLq = """
                SELECT 
                    t1.Nr_TUC,
                    t1.Unidade AS UNID_ROA,
                    SUM(t1.Qtd) AS QTD_ROA
                FROM 
                    ROA t1
                WHERE 
                    t1.Cd_NG = 1 AND t1.dt_ARQ = ?
                GROUP BY 
                    t1.Nr_TUC,
                    t1.Unidade
            """
    ROAq = sql.imp_tbl_forma_001('ROA', SQLq=SQLq, con=con, st=st, Empresa=Empresa)

    SQLq = """
                SELECT 
                    t1.Nr_TUC,
                    SUM(t1.VL_tot) AS VL_TOT
                FROM 
                    ROA t1
                WHERE 
                    t1.Cd_NG = 1 AND t1.dt_ARQ = ?
                GROUP BY 
                    t1.Nr_TUC
                ORDER BY 
                    VL_TOT DESC
            """
    ROAv = sql.imp_tbl_forma_001('ROA', SQLq=SQLq, con=con, st=st, Empresa=Empresa)

    SQLq = f"""
             SELECT 
                t1.Nr_TUC,
                t1.UNID_AIS,
                t1.QTD_AIC_ANT,
                t1.QTD_ALM_ANT,
                t1.QTD_AIC_AT,
                t1.QTD_ALM_AT,
                t1.QTD_REF,
                t1.QTD_CMP,
                t1.QTD_TURN,
                t1.QTD_REAP,
                t1.QTD_INC,
                t1.QTD_DOA
            FROM 
                ORIGEM_ATIVOS_INCREMENTAL t1 
            WHERE 
                t1.dt_ARQ = ? 
            """
    ORI = sql.imp_tbl_forma_001('ORIGEM_ATIVOS_INCREMENTAL', SQLq=SQLq, con=con, st=st, Empresa=Empresa)
    ORI = conv_num(ORI, 'QTD')
    
    SQLq = f"""
                SELECT 
                    t1.COD_ITEM,
                    t1.Nr_TUC,
                    SUM(t1.Qtd) AS QTD_REFa, 
                    t1.Unidade AS UNID_REF
                FROM 
                    REFORMADOS_INCREMENTAL t1 
                WHERE 
                    t1.dt_ARQ = ?
                GROUP BY 
                    t1.COD_ITEM,
                    t1.Nr_TUC,
                    t1.Unidade
            """
    REF = sql.imp_tbl_forma_001('REFORMADOS_INCREMENTAL', SQLq=SQLq, con=con, st=st, Empresa=Empresa)
    REF.to_sql("TB_REF_LADO_A", con, if_exists='replace', index=False)
    
    SQLq = f"""
                SELECT 
                    COD_ITEM,
                    Cd_Unid AS UNID_EC, 
                    SUM(Qtd) AS QTD_EC
                FROM 
                    BP_EC t1
                WHERE 
                    t1.dt_ARQ = ? 
                    AND (Dt_NF  BETWEEN date('""" + dt_ini_proc.strftime("%Y-%m-%d") + """') 
                    AND date('""" + dt_fim_proc.strftime("%Y-%m-%d") + """'))
                GROUP BY 
                    t1.COD_ITEM,
                    t1.Cd_Unid;
            """
    EC = sql.imp_tbl_forma_001('BP_EC', SQLq=SQLq, con=con, st=st, Empresa=Empresa)
    EC.to_sql("TB_EC_LADO_A", con, if_exists='replace', index=False)

    SQLq = """
                SELECT 
                    t1.Nr_TUC,
                    t1.Unidade AS UNID_AIC_ANT,
                    SUM(t1.Qtd) AS QTD_ROA_AIC_ANT
                FROM 
                    ROAaicANT t1
                WHERE 
                    t1.Cd_NG = 1 AND t1.dt_ARQ = ?
                GROUP BY 
                    t1.Nr_TUC,
                    t1.Unidade
            """
    ROAaicANTq = sql.imp_tbl_forma_001('ROAaicANT', SQLq=SQLq, con=con, st=st, Empresa=Empresa)

    dt_arq = sql.max_arq("ROAaicANT", con, empresa=Empresa)
    if dt_arq:
        con.execute("DROP TABLE IF EXISTS TB_ROAaicANT_RESUMO_LADO_A")

        con.execute(f"""
                            CREATE TABLE TB_ROAaicANT_RESUMO_LADO_A AS
                            SELECT 
                                t1.Nr_TUC,
                                t1.COD_ITEM,
                                t1.Unidade AS UNID_AIC,
                                SUM(t1.Qtd) AS QTD_ROA_AIC_ANT
                            FROM ROAaicANT t1
                            WHERE 
                                t1.dt_ARQ = ?
                            GROUP BY 
                                t1.Nr_TUC,
                                t1.COD_ITEM,
                                t1.Unidade
                        """, (dt_arq,))

        con.commit()
    SQLq = """
                SELECT 
                    t1.Nr_TUC,
                    t1.Unidade AS UNID_AIC_AT,
                    SUM(t1.Qtd) AS QTD_ROA_AIC_AT
                FROM 
                    ROAaicAT t1
                WHERE 
                    t1.Cd_NG = 1 AND t1.dt_ARQ = ?
                GROUP BY 
                    t1.Nr_TUC,
                    t1.Unidade
            """
    ROAaicATq = sql.imp_tbl_forma_001('ROAaicAT', SQLq=SQLq, con=con, st=st, Empresa=Empresa)
    dt_arq = sql.max_arq("ROAaicAT", con, empresa=Empresa)
    if dt_arq:
        con.execute("DROP TABLE IF EXISTS TB_ROAaicAT_RESUMO_LADO_A")

        con.execute(f"""
                            CREATE TABLE TB_ROAaicAT_RESUMO_LADO_A AS
                            SELECT 
                                t1.Nr_TUC,
                                t1.COD_ITEM,
                                t1.Unidade AS UNID_AIC,
                                SUM(t1.Qtd) AS QTD_ROA_AIC_ANT
                            FROM ROAaicAT t1
                            WHERE 
                                t1.dt_ARQ = ?
                            GROUP BY 
                                t1.Nr_TUC,
                                t1.COD_ITEM,
                                t1.Unidade
                        """, (dt_arq,))

        con.commit()

    ROAv['VL_CUM'] = ROAv['VL_TOT'].cumsum()
    total_vl = ROAv['VL_TOT'].sum()
    ROAv['PCT_CUM'] = ROAv['VL_CUM'] / total_vl

    ROAv['RAT'] = 'C'
    ROAv.loc[ROAv['PCT_CUM'] <= 0.95, 'RAT'] = 'B'
    ROAv.loc[ROAv['PCT_CUM'] <= 0.85, 'RAT'] = 'A'

    LST_UC_INC = set([
                        '125','130','160','165','190','195','200','210','255','295',
                        '310','330','340','345','560','565','570','575','580','605'
                    ])

    ROAv['FLG_ANL'] = ROAv['Nr_TUC'].isin(LST_UC_INC).astype(int)
    ROAv.to_sql('Tst_ABC_ROA', con, if_exists='replace', index=False)
    LST_UC_ANL = (
                    ROAv.loc[(ROAv['RAT'].isin(['A','B'])) & (ROAv['FLG_ANL'] == 1), 'Nr_TUC']
                    .drop_duplicates()
                    .tolist()
                 )

    df_PROV = (
                ROA.loc[ROA['Nr_TUC'].isin(LST_UC_ANL), ['Nr_TUC','UND_ROA']]
                .drop_duplicates()
                .copy()
              )
    
    assert not df_PROV.duplicated(['Nr_TUC','UND_ROA']).any(), "Duplicatas em df_PROV"
    assert not ORI.duplicated(['Nr_TUC','UNID_AIS']).any(), "Duplicatas em ORI"

    df1 = df_PROV.merge(
                            ORI,
                            how='outer',
                            left_on=['Nr_TUC','UND_ROA'],
                            right_on=['Nr_TUC','UNID_AIS'],
                            suffixes=("_ROA", "_ORI"),
                            indicator=True
                        )

    merge_map = {
                    'both': 'Conciliado',
                    'left_only': 'Presente no ROA, possível inconsistência',
                    'right_only': 'Presente no ORIGEM, possível inconsistência'
                }

    df1['OBS_SFF'] = df1['_merge'].map(merge_map)
    df1 = df1.drop(columns='_merge')

    df1.to_sql('Tst_CONS_ROA_ORI', con, if_exists='replace', index=False)

    
    df_uc = df_PROV[['Nr_TUC']].merge(
                                        ORI,
                                        how='outer',
                                        on='Nr_TUC',
                                        indicator=True
                                    )

    df_uc['OBS_SFF_ORI_vs_ROA'] = df_uc['_merge'].map({
                                                        'both': 'Conciliado',
                                                        'left_only': 'Presente no ROA',
                                                        'right_only': 'Presente no ORIGEM'
                                                    })

    df_uc = df_uc.drop(columns='_merge').sort_values(['Nr_TUC','UNID_AIS'])


    df1n = df_uc.merge(
                        ROAq.loc[ROAq['Nr_TUC'].isin(LST_UC_ANL)],
                        how='outer',
                        left_on=['Nr_TUC','UNID_AIS'],
                        right_on=['Nr_TUC','UNID_ROA'],
                        indicator=True
                    )

    df1n['OBS_SFF_ORI_vs_ROA_QTD'] = df1n['_merge'].map({
                                                            'both': 'Qtd em ambas',
                                                            'left_only': 'Qtd ORIGEM',
                                                            'right_only': 'Qtd ROA'
                                                        })

    df1n = df1n.drop(columns='_merge')


    df1o = df1n.merge(
                        INCR.loc[INCR['Nr_TUC'].isin(LST_UC_ANL)],
                        how='outer',
                        left_on=['Nr_TUC','UNID_AIS'],
                        right_on=['Nr_TUC','UNID_INCR'],
                        indicator=True
                    )

    df1o['OBS_SFF_ORI_vs_INC_QTD'] = df1o['_merge'].map({
                                                            'both': 'Qtd em ambas',
                                                            'left_only': 'Qtd ORIGEM',
                                                            'right_only': 'Qtd INCR'
                                                        })

    df1o = df1o.drop(columns='_merge')

    df_PROV_ao = AO.merge(ROA, how='left', on='COD_ITEM')

    df_AO_agg = (
                    df_PROV_ao.groupby(['Nr_TUC','UNID_AO'], as_index=False)['QTD_AO']
                    .sum()
                )

    df1p = df1o.merge(
                        df_AO_agg.loc[df_AO_agg['Nr_TUC'].isin(LST_UC_ANL)],
                        how='outer',
                        left_on=['Nr_TUC','UNID_AIS'],
                        right_on=['Nr_TUC','UNID_AO'],
                        indicator=True
                    )

    df1p['OBS_SFF_ORI_vs_AO_QTD'] = df1p['_merge'].map({
                                                        'both': 'Qtd em ambas',
                                                        'left_only': 'Qtd ORIGEM',
                                                        'right_only': 'Qtd AO'
                                                    })

    df1p = df1p.drop(columns='_merge')

    qtd_cols = [c for c in df1p.columns if c.startswith('QTD')]
    unid_cols = [c for c in df1p.columns if c.startswith('UNID')]

    df1p[qtd_cols] = df1p[qtd_cols].fillna(0)
    df1p[unid_cols] = df1p[unid_cols].fillna('NO')

    df1p['QTD_LADO_A'] = 0
    df1p['QTD_LADO_B'] = 0
    df1p['DELTA'] = 0
    df1p['OBS_SFF'] = 'NO'
    
    ratio = (df1p['QTD_ROA'] - df1p['QTD_INCR']) / df1p['QTD_INCR']
    df1p['OBS_SFF'] = 'NO'
    df1p.loc[(df1p['QTD_INCR'] > 0) & (ratio > 0.01), 'OBS_SFF'] = \
        'Glosas aplicadas, verificar motivo.'
    df1p.loc[(df1p['QTD_INCR'] > 0) & (ratio < -0.01), 'OBS_SFF'] = \
        'Inserções aplicadas, verificar motivo.'
    df1p.loc[abs(df1p['QTD_AO'] - df1p['QTD_ALM_AT']) > 0.01, 'OBS_SFF'] = \
        'Almoxarifado AO vs Origem divergente.'

    df1p1 = df1p.merge(INCRinc[INCRinc['Nr_TUC'].isin(LST_UC_ANL)], how='outer', left_on = ['Nr_TUC','UNID_AIS'], 
                       right_on=['Nr_TUC','UNID_INCRinc'], suffixes = ("_ORI", "_INCRinc"), indicator=True)
    
    df1p1['OBS_SFF_ORI_vs_INCRinc_QTD'] = df1p1['_merge'].map({
                                                        'both': 'Qtd em ambas',
                                                        'left_only': 'Qtd ORIGEM',
                                                        'right_only': 'Qtd INCRinc'
                                                    })

    df1p1 = df1p1.drop(columns='_merge')
    df1p1['QTD_INCRinc'] = df1p1['QTD_INCRinc'].fillna(0)
    df1p1['UNID_INCRinc'] = df1p1['UNID_INCRinc'].fillna('NO')
    df1p1['OBS_SFF_incorp'] = 'NO'
    df1p1.loc[abs(df1p1['QTD_INC'] - df1p1['QTD_INCRinc']) > 0.01,
             'OBS_SFF_incorp'] = 'Inconsistência entre arquivo Incremental e Origem para dados de incorporação'

    df1p1 = df1p1.merge(INCRdoa[INCRdoa['Nr_TUC'].isin(LST_UC_ANL)], how='outer', left_on = ['Nr_TUC','UNID_AIS'],
                        right_on=['Nr_TUC','UNID_INCRdoa'], suffixes = ("_ORI", "_INCRdoa"), indicator=True)
    df1p1['OBS_SFF_ORI_vs_INCRdoa_QTD'] = df1p1['_merge'].map({
                                                        'both': 'Qtd em ambas',
                                                        'left_only': 'Qtd ORIGEM',
                                                        'right_only': 'Qtd INCRdoa'
                                                    })

    df1p1 = df1p1.drop(columns='_merge')
    df1p1['QTD_INCRdoa'] = df1p1['QTD_INCRdoa'].fillna(0)
    df1p1['UNID_INCRdoa'] = df1p1['UNID_INCRdoa'].fillna('NO')
    df1p1['OBS_SFF_doa'] = 'NO'
    df1p1.loc[abs(df1p1['QTD_DOA'] - df1p1['QTD_INCRdoa']) > 0.01,
             'OBS_SFF_doa'] = 'Inconsistência entre arquivo Incremental e Origem para dados de doação'

    df1p1 = df1p1.merge(REF[REF['Nr_TUC'].isin(LST_UC_ANL)][['Nr_TUC','QTD_REFa','UNID_REF']], left_on = ['Nr_TUC','UNID_AIS'],
                        right_on=['Nr_TUC','UNID_REF'], how = 'outer', suffixes = ("_ORI", "_REF"), indicator=True)
    df1p1['OBS_SFF_ORI_vs_REF_QTD'] = df1p1['_merge'].map({
                                            'both': 'Com quantidade declarada em ambas as tabelas',
                                            'left_only': 'Quantidade presente no ORIGEM',
                                            'right_only': 'Quantidade presente no REFORMADOS'
                                        })

    df1p1 = df1p1.drop(columns='_merge')
    df1p1['QTD_REFa'] = df1p1['QTD_REFa'].fillna(0)
    df1p1['UNID_REF'] = df1p1['UNID_REF'].fillna('NO')
    df1p1['OBS_SFF_ref'] = 'NO'
    df1p1.loc[abs(df1p1['QTD_REF'] - df1p1['QTD_REFa']) > 0.01,
             'OBS_SFF_ref'] = 'Inconsistência entre arquivo Reformas e Origem para dados de reforma'

    df_PROV_ec = EC.merge(ROA, how='left', on='COD_ITEM')
    df_EC_agg = (
                    df_PROV_ec.groupby(['Nr_TUC','UNID_EC'], as_index=False)['QTD_EC']
                    .sum()
                )
 
    df1p1 = df1p1.merge(df_EC_agg[df_EC_agg['Nr_TUC'].isin(LST_UC_ANL)], how='outer', left_on = ['Nr_TUC','UNID_AIS'],
                        right_on=['Nr_TUC','UNID_EC'], suffixes = ("_ORI", "_EC"), indicator=True)
    df1p1['OBS_SFF_ORI_vs_EC_QTD'] = df1p1['_merge'].map({
                                            'both': 'Com quantidade declarada em ambas as tabelas',
                                            'left_only': 'Quantidade presente no ORIGEM',
                                            'right_only': 'Quantidade presente no EC'
                                        })

    df1p1 = df1p1.drop(columns='_merge')
    df1p1 = df1p1.drop_duplicates()
    df1p1['QTD_EC'] = df1p1['QTD_EC'].fillna(0)
    df1p1['UNID_EC'] = df1p1['UNID_EC'].fillna('NO')
    df1p1['OBS_SFF_ec'] = 'NO'
    df1p1.loc[abs(df1p1['QTD_CMP'] - df1p1['QTD_EC']) > 0.01,
             'OBS_SFF_ec'] = 'Inconsistência entre arquivo Compras e Origem para dados de compras'
    

    df1p1 = df1p1.merge(ROAaicANTq[ROAaicANTq['Nr_TUC'].isin(LST_UC_ANL)], how='outer', left_on = ['Nr_TUC','UNID_AIS'],
                        right_on=['Nr_TUC','UNID_AIC_ANT'], suffixes = ("_ORI", "_EC"), indicator=True)
    df1p1['OBS_SFF_ORI_vs_AIC_ANT_QTD'] = df1p1['_merge'].map({
                                            'both': 'Com quantidade declarada em ambas as tabelas',
                                            'left_only': 'Quantidade presente no ORIGEM',
                                            'right_only': 'Quantidade presente no AIC ANT'
                                        })

    df1p1 = df1p1.drop(columns='_merge')
    df1p1 = df1p1.drop_duplicates()
    df1p1['QTD_ROA_AIC_ANT'] = df1p1['QTD_ROA_AIC_ANT'].fillna(0)
    df1p1['UNID_AIC_ANT'] = df1p1['UNID_AIC_ANT'].fillna('NO')
    df1p1['OBS_SFF_AIC_ANT'] = 'NO'
    df1p1.loc[abs(df1p1['QTD_AIC_ANT'] - df1p1['QTD_ROA_AIC_ANT']) > 0.01,
             'OBS_SFF_AIC_ANT'] = 'Inconsistência entre arquivo AIC anterior e Origem para dados de compras'
    
    df1p1 = df1p1.merge(ROAaicATq[ROAaicATq['Nr_TUC'].isin(LST_UC_ANL)], how='outer', left_on = ['Nr_TUC','UNID_AIS'],
                        right_on=['Nr_TUC','UNID_AIC_AT'], suffixes = ("_ORI", "_EC"), indicator=True)
    df1p1['OBS_SFF_ORI_vs_AIC_AT_QTD'] = df1p1['_merge'].map({
                                            'both': 'Com quantidade declarada em ambas as tabelas',
                                            'left_only': 'Quantidade presente no ORIGEM',
                                            'right_only': 'Quantidade presente no AIC AT'
                                        })

    df1p1 = df1p1.drop(columns='_merge')
    df1p1 = df1p1.drop_duplicates()
    df1p1['QTD_ROA_AIC_AT'] = df1p1['QTD_ROA_AIC_AT'].fillna(0)
    df1p1['UNID_AIC_AT'] = df1p1['UNID_AIC_AT'].fillna('NO')
    df1p1['OBS_SFF_AIC_AT'] = 'NO'
    df1p1.loc[abs(df1p1['QTD_AIC_AT'] - df1p1['QTD_ROA_AIC_AT']) > 0.01,
             'OBS_SFF_AIC_AT'] = 'Inconsistência entre arquivo AIC atual e Origem para dados de compras'
    
    df1p1 = df1p1[['Nr_TUC', 'UNID_AIS', 'QTD_AIC_ANT', 'QTD_ALM_ANT', 'QTD_AIC_AT', 'QTD_ALM_AT', 'QTD_REF', 'QTD_CMP', 
                  'QTD_TURN', 'QTD_REAP', 'QTD_INC', 'QTD_DOA', 'QTD_ROA', 'UNID_ROA', 'QTD_INCR', 'UNID_INCR', 
                  'QTD_AO', 'UNID_AO', 'QTD_INCRinc', 'UNID_INCRinc', 'QTD_INCRdoa', 'UNID_INCRdoa', 'QTD_REFa', 'UNID_REF',
                  'QTD_EC', 'UNID_EC', 'QTD_ROA_AIC_ANT', 'UNID_AIC_ANT', 'QTD_ROA_AIC_AT', 'UNID_AIC_AT', 
                  'QTD_LADO_A', 'QTD_LADO_B', 'DELTA', 'OBS_SFF_ORI_vs_ROA', 'OBS_SFF_ORI_vs_ROA_QTD', 'OBS_SFF_ORI_vs_INC_QTD', 
                  'OBS_SFF_ORI_vs_AO_QTD', 'OBS_SFF', 'OBS_SFF_ORI_vs_INCRinc_QTD', 'OBS_SFF_incorp', 
                  'OBS_SFF_ORI_vs_INCRdoa_QTD', 'OBS_SFF_doa', 'OBS_SFF_ORI_vs_REF_QTD', 'OBS_SFF_ref', 'OBS_SFF_ORI_vs_EC_QTD', 
                  'OBS_SFF_ec', 'OBS_SFF_ORI_vs_AIC_ANT_QTD', 'OBS_SFF_AIC_ANT', 'OBS_SFF_ORI_vs_AIC_AT_QTD', 'OBS_SFF_AIC_AT']]
    
    qtd_cols = [c for c in df1p1.columns if c.startswith('QTD')]
    unid_cols = [c for c in df1p1.columns if c.startswith('UNID')]
    obs_cols = [c for c in df1p1.columns if c.startswith('OBS')]

    df1p1[qtd_cols] = df1p1[qtd_cols].fillna(0)
    df1p1[unid_cols] = df1p1[unid_cols].fillna('NO')
    for col in obs_cols:
        if pd.api.types.is_categorical_dtype(df1p1[col]):
            df1p1[col] = df1p1[col].cat.add_categories(['Não se aplica'])
    df1p1[obs_cols] = df1p1[obs_cols].fillna('Não se aplica')


    df1p1.to_sql('Tst_LDAvB', con, if_exists='replace', index=False)
    x = imprime_lado_AvsB(dir_arq_saida, Empresa, df1p1, con=con, st=st)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf'{dir_arq_saida}/LADO_A_vs_B_{Empresa}.xlsx',
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def ROS_VAL(bd, dir_arq_saida, dir_arq_dados, Empresa, st=None):

    if not (os.path.exists(f"{dir_arq_saida}/LST_MAT_AJ_{Empresa}.csv") and
                os.path.exists(f"{dir_arq_saida}/LST_SER_AJ_{Empresa}.csv")):
        st.error(f'Inexiste listas, para poder terminar. Por favor, salvar no diretório {f"{dir_arq_saida}"}.') 
        registrar_evento(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        nome_evento = 'ros_validado',
                        mensagem = f'Falhou na elaboração do arquivo ROS_VAL.', 
                        nivel = 'ERRO',
                        detalhes = {'erro' : f'Inexiste listas, para poder terminar. Por favor, salvar no diretório {f"{dir_arq_saida}"}.'})
        return

    def gerar_resumo_ajustes(ROAm, TOT_ROA):
        df = ROAm.groupby(['Nr_TI', 'Cd_SubODI'], dropna=False)[[
            'VL_CONS', 'VL_AJS', 'VL_AJS_FLX', 'VL_AJS_MAT', 'VL_AJS_SER', 'VL_AJS_UC']].sum().reset_index()
        df['VL_CONS'] = np.where(df['VL_CONS'] < 0, 0, df['VL_CONS'])
        return TOT_ROA.merge(df, on=['Nr_TI', 'Cd_SubODI'], how='left').drop(columns='FLG_AJS_UC')
    
    def aplicar_ajustes(ROA, TOT_ROA, lst_mat, lst_ser):
        lst_mat['Nr_TI'] = lst_mat['Nr_TI'].astype(str)
        ROA['Nr_TI'] = ROA['Nr_TI'].astype(str)
        TOT_ROA['Nr_TI'] = TOT_ROA['Nr_TI'].astype(str)
        lst_ser['Cd_Cls_Custo'] = lst_ser['Cd_Cls_Custo'].astype(str)
        ROA['Cd_Cls_Custo'] = ROA['Cd_Cls_Custo'].astype(str)
        ROA['COD_ITEM'] = ROA['COD_ITEM'].astype(str)
        lst_mat['COD_ITEM'] = lst_mat['COD_ITEM'].astype(str)

        ROAm = ROA.merge(lst_mat, how='left', on=['Nr_TI', 'COD_ITEM'])
        ROAm['TP_OBRA'] = np.where(ROAm['Cd_Tipo_Obra'].isin([3, 7, 12]), 'M', 'I')

        ROAm['FP_MAT'] = 1
        mask = ROAm['Cd_NG'].isin(['1', '2'])
        ROAm.loc[mask, 'FP_MAT'] = np.where(
                                                ROAm.loc[mask, 'TP_OBRA'] == 'M',
                                                ROAm.loc[mask, 'Vl_Default_Man'],
                                                ROAm.loc[mask, 'Vl_Default_Inv']
                                            )
        ROAm.drop(columns=['Cd_Tipo_Obra', 'Vl_Default_Man', 'Vl_Default_Inv'], inplace=True)

        ROAm = ROAm.merge(lst_ser, how='left', on=['Nr_TI', 'COD_ITEM', 'Cd_Cls_Custo'])
        ROAm['FP_SER'] = 1
        mask = ROAm['Cd_NG'] == '4'
        ROAm.loc[mask, 'FP_SER'] = np.where(
                                                ROAm.loc[mask, 'TP_OBRA'] == 'M',
                                                ROAm.loc[mask, 'Vl_Default_Man'],
                                                ROAm.loc[mask, 'Vl_Default_Inv']
                                            )
        ROAm.drop(columns=['Vl_Default_Man', 'Vl_Default_Inv'], inplace=True)

        ROAm[['FP_MAT', 'FP_SER']] = ROAm[['FP_MAT', 'FP_SER']].apply(pd.to_numeric, errors='coerce')
        ROAm = ROAm.merge(TOT_ROA[['Nr_TI', 'Cd_SubODI', 'FLG_AJS_UC']], how='left', on=['Nr_TI', 'Cd_SubODI'])

        ROAm['VL_CONS'] = ROAm['VL_tot'] * ROAm['FP_MAT'] * ROAm['FP_SER'] * ROAm['FLG_TMP'] * ROAm['FLG_AJS_UC']
        ROAm['VL_AJS'] = ROAm['VL_tot'] - ROAm['VL_CONS']
        ROAm['VL_AJS_FLX'] = ROAm['VL_tot'] * (1 - ROAm['FLG_TMP'])
        ROAm['VL_AJS_MAT'] = ROAm['VL_tot'] * (1 - ROAm['FP_MAT'])
        ROAm['VL_AJS_SER'] = ROAm['VL_tot'] * (1 - ROAm['FP_SER'])
        ROAm['VL_AJS_UC'] = ROAm['VL_tot'] * (1 - ROAm['FLG_AJS_UC'])
        ROAm.to_sql('RESUMO_ROS_AJST', bd, if_exists='replace', index=False)
        return ROAm

    def pivot_roa(ROA):
        pivot = pd.pivot_table(ROA, values='VL_tot', index=['Nr_TI', 'Cd_SubODI'], columns='Cd_NG', aggfunc='sum', fill_value=0).reset_index()
        for col in [5, 6]:
            if col not in pivot.columns:
                pivot[col] = 0
        pivot.columns = ['Nr_TI', 'Cd_SubODI'] + [f'VL_{nome}_ROA' for nome in ['UC', 'COM', 'MOP', 'ST', 'JOA', 'OUT']]
        pivot['VL_TOT_ROA'] = pivot.filter(like='VL_').sum(axis=1)
        pivot['FLG_AJS_UC'] = (pivot['VL_UC_ROA'] / pivot['VL_TOT_ROA'] >= 0.1).astype(int)
        return pivot

    con = duckdb.connect()
    def log(msg):
        if st:
            status.text(msg)

    def caminho_csv(nome):
        return os.path.join(dir_arq_dados, f"{nome}_{Empresa}.csv").replace("\\", "/")

    def ler_csv_ajuste(nome, usecols):
        path = caminho_csv(nome)
        try:
            return pd.read_csv(path, sep="|", decimal=",", on_bad_lines='skip', dtype=str, usecols=usecols, encoding='latin-1')
        except:
            return pd.read_csv(path, sep="|", decimal=",", on_bad_lines='skip', dtype=str, usecols=usecols)

    def carregar_roa():
        caminho = dir_arq_saida.replace("/AIS_ANLS","")
        arquivo_roa = [
                            os.path.join(rf"{caminho}\DADOS_BRUTOS_MANUAL", f)
                            for f in os.listdir(rf"{caminho}\DADOS_BRUTOS_MANUAL")
                            if f.lower().endswith('.csv') and (f.lower()[:4]=="roa_")
                        ]
        
        Dt_ARQ = sql.max_arq('ROA', bd, Empresa)
        if Dt_ARQ:
            sSQL = f"""
                    WITH ROA_BASE AS (
                        SELECT 
                            t1.Ide_RO_Analitico, 
                            t1.Nr_TI, 
                            t1.Cd_SubODI, 
                            t1.Cd_Cls_Custo, 
                            t1.COD_ITEM, 
                            t1.Cd_NG, 
                            CAST(REPLACE(t1.Qtd, ',', '.') AS DOUBLE) AS Qtd, 
                            CAST(REPLACE(t1.VL_tot, ',', '.') AS DOUBLE) AS VL_tot, 
                            CAST(t1.Dt_Lcmto AS DATE) AS Dt_Lcmto
                        FROM read_csv_auto('{arquivo_roa[0]}',
                                            delim='|',
                                            encoding='latin-1',
                                            header=true, sample_size=-1,
                                            ignore_errors=false) AS t1
                    ),
                    FLG_TEMP AS (
                        SELECT 
                            t1.Ide_RO_Analitico, 
                            t1.FLG_TMP 
                        FROM read_csv_auto('{caminho}/AIS_ANLS/LCMTO_FLX_TEMP_{Empresa}.csv',
                                            delim='|',
                                            encoding='latin-1',
                                            header=true, sample_size=-1,
                                            ignore_errors=false) AS t1
                    )
                    SELECT 
                        t1.Ide_RO_Analitico, 
                        t1.Nr_TI, 
                        t1.Cd_SubODI, 
                        t1.Cd_Cls_Custo, 
                        t1.COD_ITEM, 
                        t1.Cd_NG, 
                        t1.Qtd, 
                        t1.VL_tot, 
                        t1.Dt_Lcmto, 
                        COALESCE(t2.FLG_TMP, 0) AS FLG_TMP
                    FROM ROA_BASE t1
                    LEFT JOIN FLG_TEMP t2
                    ON t1.Ide_RO_Analitico = t2.Ide_RO_Analitico
                    """
        df = con.execute(sSQL).fetchdf()

        
        return df
    
    if st:
        progress = st.progress(0)
        status = st.empty()

    log("Iniciando validação do ROS...")
    progress.progress(5)

    ROA = carregar_roa()
 
    progress.progress(10)
    log("ROA carregado.")

    sSQL = f"""
                SELECT Cd_SubODI, Cd_Tipo_Obra FROM ROS WHERE dt_ARQ = ?
            """
    ROS = sql.imp_tbl_forma_001("ROS", sSQL, bd, st, Empresa)
    ROS['Cd_SubODI'] = ROS['Cd_SubODI'].astype(str)
    ROA['Cd_SubODI'] = ROA['Cd_SubODI'].astype(str)
    ROA_CMP = ROA.merge(ROS, how='left', on='Cd_SubODI')
    
    progress.progress(20)
    log("ROS carregado.")

    TOT_ROA = pivot_roa(ROA_CMP)
    progress.progress(30)
    log("Subtotais do ROA calculado.")

    lst_mat = ler_csv_ajuste("LST_MAT_AJ", ['Nr_TI', 'COD_ITEM', 'Vl_Default_Man', 'Vl_Default_Inv'])
    lst_ser = ler_csv_ajuste("LST_SER_AJ", ['Nr_TI', 'COD_ITEM', 'Cd_Cls_Custo', 'Vl_Default_Man', 'Vl_Default_Inv'])
    progress.progress(40)
    log("Arquivos de ajuste carregados.")

    ROAm = aplicar_ajustes(ROA_CMP, TOT_ROA, lst_mat, lst_ser)
    progress.progress(60)
    log("Ajustes aplicados.")

    TOT_ROAa = gerar_resumo_ajustes(ROAm, TOT_ROA)
    progress.progress(75)
    log("Resumo de ajustes gerado.")

    if not sql.existe_tabela("RESUMO_AJS_RAC_COM", bd):
        raise RuntimeError("Falha ao importar o ajuste de racionalização da base local.")
    sSQL = "SELECT * FROM RESUMO_AJS_RAC_COM"
    AJS_RAC = pd.read_sql(sSQL, bd)
    colunas_somar = [col for col in AJS_RAC.columns if col not in ['Nr_TI', 'Cd_SubODI']]
    AJS_RAC['VL_AJS_RAC'] = AJS_RAC[colunas_somar].sum(axis=1)
    AJS_RAC.drop(columns=colunas_somar, inplace=True)
    TOT_ROAa = TOT_ROAa.merge(AJS_RAC, how='left', on=['Nr_TI', 'Cd_SubODI'])

    progress.progress(85)
    log("RAC aplicado.")

    try:
        df_RAC_ST = pd.read_csv(f'{dir_arq_dados}/RAC_ST_{Empresa}.csv', sep="|", decimal=',', encoding="Latin-1")
        df_RAC_ST = df_RAC_ST.groupby(by=['Cd_SubODI'], dropna=False)['VL_AJST'].sum().reset_index()
        df_RAC_ST.columns = ['Cd_SubODI', 'VL_AJS_ST']
        TOT_ROAa = TOT_ROAa.merge(df_RAC_ST, how='left', on=['Cd_SubODI'])
        progress.progress(90)
        log("RAST aplicado.")
    except:
        TOT_ROAa['VL_AJS_ST'] = 0
        progress.progress(90)
        log("RAST não aplicado.")

    TOT_ROAa['VL_AJS_ST'] = TOT_ROAa['VL_AJS_ST'].fillna(0)
    TOT_ROAa['VL_AJS_RAC'] = TOT_ROAa['VL_AJS_RAC'].fillna(0)
    TOT_ROAa['VL_AJS_TOT'] = TOT_ROAa['VL_AJS_ST'] + TOT_ROAa['VL_AJS_RAC']
    TOT_ROAa['VL_CONSf'] = TOT_ROAa['VL_CONS']
    TOT_ROAa['VL_AJSf'] = TOT_ROAa['VL_AJS']
    TOT_ROAa.loc[TOT_ROAa['VL_AJS_TOT'] > 0, 'VL_CONSf'] = (TOT_ROAa['VL_CONS'] - TOT_ROAa['VL_AJS_TOT']).where(
                                                            (TOT_ROAa['VL_CONS'] - TOT_ROAa['VL_AJS_TOT']) > 0, 0)
    TOT_ROAa.loc[TOT_ROAa['VL_AJS_TOT'] > 0, 'VL_AJSf'] = TOT_ROAa['VL_AJS'] +  (TOT_ROAa['VL_AJS_TOT']).where(
                                                            (TOT_ROAa['VL_CONS'] - TOT_ROAa['VL_AJS_TOT']) > 0, TOT_ROAa['VL_CONS'])
    TOT_ROAa.to_csv(f"{dir_arq_saida}//RESUMO_AJS_SubODI_{Empresa}.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    TOT_ROAa.to_sql('RESUMO_AJS_SubODI', con, if_exists='replace', index=False)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                        st.session_state.execucao_id, 
                        file_path = rf"{dir_arq_saida}//RESUMO_AJS_SubODI_{Empresa}.csv",
                        tipo_artefato = "SAIDA", 
                        calcular_hash = True)

    progress.progress(100)
    log("RESUMO por projeto criado.")

    return "OK"

@monitor_completo(st.session_state.LOGGER)
def ler_roa_uv(dir_base: str, empresa: str, ano: int, st = None):
    bd = sl.connect(f'{dir_base}\BD_LOCAL\{empresa}_{ano}.db')
    dt_ARQ = sql.max_arq("ROA", bd, empresa)
    if dt_ARQ:
        sSQL = f"""WITH dados AS (
                                    SELECT
                                        Cd_NG,
                                        Cd_SubODI,
                                        CAST(REPLACE(VL_tot, ',', '.') AS REAL) AS valor,
                                        date(REPLACE(Dt_Lcmto, '/', '-')) AS data
                                    FROM ROA WHERE Dt_ARQ = {dt_ARQ}
                                    )
                                    SELECT
                                    Cd_NG, Cd_SubODI, valor, data,
                                    SUM(valor) OVER (
                                        PARTITION BY Cd_SubODI
                                        ORDER BY data
                                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                                    ) AS cumulativo
                                    FROM dados
                                    WHERE data IS NOT NULL         -- datas inválidas (ex.: 31/06) viram NULL e são filtradas aqui
                                    ORDER BY Cd_SubODI, data;"""

        try:
            df = pd.read_sql(sSQL, bd)
            return df
        except Exception:
            pass
    return pd.DataFrame()

@monitor_completo(st.session_state.LOGGER)
def ler_ros_uv(dir_base: str, empresa: str, ano: int, st = None):
    bd = sl.connect(f'{dir_base}\BD_LOCAL\{empresa}_{ano}.db')
    dt_ARQ = sql.max_arq("ROS", bd, empresa)
    if dt_ARQ:
        sSQL = f"SELECT * FROM ROS WHERE dt_ARQ = {dt_ARQ}"
        try:
            df = pd.read_sql(sSQL, bd)
            return df
        except Exception:
            pass
    return pd.DataFrame()

@monitor_completo(st.session_state.LOGGER)
def calcular_kpis_uv(df, projeto, dir_base, lim=0.1, eps=1.0, st = None):
    # Pré-condições
    if df.empty:
        return {k: np.nan for k in [
            'CTA','ID_desv_pad','ID_rev','IRange','IED_dias','KPI_CRESC (%)','KPI_GAP (dias)',
            'KPI_PER','FLG_MOP','FLG_ST','FLG_JOA','IEg_dias','IEuc_dias','CA_TOT','UC_TOT','CMD','Nr_TI'
        ]}
    df = df.sort_values('data').copy()

    # Se tiver essa função externa, mantém; senão, coloque stub:
    try:
        PER_TI = df['limite_usado'].iloc[-1]
        Nr_TI  = df['Nr_TI'].iloc[-1] 
    except NameError:
        PER_TI, Nr_TI = 0, ""

    y = df['cumulativo'].astype(float)

    
    t = (df['data'] - df['data'].min()) / (df['data'].max() - df['data'].min())
    t = t.astype(float)

    # normalização de y
    y_min, y_max = float(y.min()), float(y.max())
    y_norm = (y - y_min) / (y_max - y_min) if y_max != y_min else y * 0.0

    # CTA
    peso_total = y_norm.sum()
    CTA = 0.0 if peso_total == 0 else 2.0 * ((t * y_norm).sum() / peso_total - 0.5)

    # Derivada
    dy = y.diff()
    # ID_rev (reversões de sinal)
    ID_rev = float(((dy * dy.shift(1)) < 0).sum()) / max(len(dy) - 1, 1)
    # ID_desv_pad (desvio/ média)
    m = dy.mean()
    ID_desv_pad = float(dy.std() / m) if m and m != 0 else 0.0

    # IRange: contagem de “incursões” fora da faixa
    amp = y_max if y_max != 0 else 1.0
    lim_sup = lim * amp
    lim_inf = -lim * amp
    dy0 = dy.fillna(0)
    fora = (dy0 < lim_inf) | (dy0 > lim_sup)
    IRange = int((fora & ~fora.shift(fill_value=False)).sum())

    # IED: maior período consecutivo com |dy| < eps (em dias)
    dt = df['data'].diff().dt.total_seconds().fillna(0.0) / 86400.0
    estagnado = dy0.abs() < eps
    # agrupa “runs” de estagnação e soma durações por run
    grp = estagnado.ne(estagnado.shift(fill_value=False)).cumsum()
    blocos = dt.where(estagnado).groupby(grp).sum(min_count=1)
    IED = float(blocos.max()) if blocos.size else 0.0
    #IED = 0.0 if (PER_TI and IED <= PER_TI) else IED

    # KPI_CRESC: % de variações negativas no acumulado
    n_neg = (dy < 0).sum()
    KPI_CRESC = round(float(n_neg) / max(len(df) - 1, 1), 2)

    # KPI_GAP: dias desde último positivo de UC (Cd_NG==1) até o fim
    data_inicio, data_fim = df['data'].iloc[0], df['data'].iloc[-1]
    duracao_total = (data_fim - data_inicio).days
    ultimo_pos = df.loc[(df['valor'] > 0) & (df['Cd_NG'].astype(str) == '1'), 'data'].max()
    KPI_GAP = int((data_fim - ultimo_pos).days) if pd.notna(ultimo_pos) else int(duracao_total)

    KPI_PER = float(duracao_total) / PER_TI if PER_TI else 0.0

    # Flags de material por mês
    df['mes_ano'] = df['data'].dt.to_period('M')
    meses_mat = df.loc[df['Cd_NG'].isin([1,2,'1','2']), 'mes_ano'].unique()
    df['FLG_MAT'] = df['mes_ano'].isin(meses_mat)
    def sem_mat_2_meses_antes(mes):
        mes_atual = mes.to_timestamp()
        m1 = (mes_atual - DateOffset(months=1)).to_period("M")
        m2 = (mes_atual - DateOffset(months=2)).to_period("M")
        return (m1 not in meses_mat) and (m2 not in meses_mat)

    df["FLG_MOP_tmp"] = df.apply(
                                    lambda x: sem_mat_2_meses_antes(x["mes_ano"]) 
                                    if str(x["Cd_NG"]) == "3" else False, 
                                    axis=1
                                )

    df["FLG_ST_tmp"] = df.apply(
                                    lambda x: sem_mat_2_meses_antes(x["mes_ano"]) 
                                    if str(x["Cd_NG"]) == "4" else False, 
                                    axis=1
                                )

    df["FLG_JOA_tmp"] = df.apply(
                                    lambda x: sem_mat_2_meses_antes(x["mes_ano"]) 
                                    if str(x["Cd_NG"]) == "5" else False, 
                                    axis=1
                                )
    FLG_MOP = df["FLG_MOP_tmp"].any()
    FLG_ST  = df["FLG_ST_tmp"].any()
    FLG_JOA = df["FLG_JOA_tmp"].any()

    # IEg_dias: maior intervalo entre quaisquer lançamentos
    IEg_dias = float(dt.max()) if len(df) > 1 else 0.0

    # IEuc_dias: maior intervalo entre lançamentos de UC/UAR
    mask_uc = df['Cd_NG'].astype(str).isin(['1','2'])
    if mask_uc.sum() > 1:
        IEuc_dias = float(df.loc[mask_uc, 'data'].diff().dt.total_seconds().fillna(0.0).div(86400.0).max())
    else:
        IEuc_dias = 0.0

    # CA_TOT, UC_TOT
    total = float(df['valor'].sum())
    if total == 0:
        CA_TOT = UC_TOT = 0.0
    else:
        CA_TOT = float(df[df['Cd_NG'].astype(str).isin(['3','4'])]['valor'].sum()) / total
        UC_TOT = float(df[df['Cd_NG'].astype(str).isin(['1'])]['valor'].sum()) / total

    # CMD
    dias_exec = max((data_fim - data_inicio).days, 0)
    CMD = float(total) / dias_exec if dias_exec > 0 else float(total)

    return {
        'CTA': float(CTA),
        'ID_desv_pad': float(ID_desv_pad),
        'ID_rev': float(ID_rev),
        'IRange': int(IRange),
        'IED_dias': float(IED),
        'KPI_CRESC (%)': float(KPI_CRESC),
        'KPI_GAP (dias)': int(KPI_GAP),
        'KPI_PER': float(KPI_PER),
        'FLG_MOP': bool(FLG_MOP),
        'FLG_ST': bool(FLG_ST),
        'FLG_JOA': bool(FLG_JOA),
        'IEg_dias': float(IEg_dias),
        'IEuc_dias': float(IEuc_dias),
        'CA_TOT': float(CA_TOT),
        'UC_TOT': float(UC_TOT),
        'CMD': float(CMD),
        'Nr_TI': str(Nr_TI)
    }

@monitor_completo(st.session_state.LOGGER)
def teste(con, dir_arq_saida, Empresa, st = None, df_CARACT = pd.DataFrame()):
    def fnc_int(indicadores, df_dd):
        interpretacoes = {}
        perc = 0.1
        # --- CTA ---
        cta = indicadores['CTA']
        if abs(cta) < 0.1:
            interpretacoes['CTA'] = "isso indica que há distribuição temporal bem balanceada de lançamentos"
        elif cta < -0.5:
            interpretacoes['CTA'] = "isso indica que há alta concentração de lançamentos no início da série"
        elif cta > 0.5:
            interpretacoes['CTA'] = "isso indica que há alta concentração de lançamentos no final da série"
        else:
            interpretacoes['CTA'] = "indicando distribuição temporal levemente enviesada de lançamentos"

        # --- ID ---
        data_ranges = [
                        # CV <= 20%, Inversões <= 10%
                        {
                            "Faixa CV da derivada": "≤ 20%",
                            "Faixa % Inversões": "≤ 10%",
                            "Classificação": "Baixo / Baixo",
                            "Interpretação": "a obra apresenta taxa de crescimento contínuo, com baixa quantidade de ajustes."
                        },
                        # CV <= 20%, Inversões > 10%
                        {
                            "Faixa CV da derivada": "≤ 20%",
                            "Faixa % Inversões": "> 10%",
                            "Classificação": "Baixo / Alto",
                            "Interpretação": "a obra apresenta taxa de crescimento contínuo, mas alterna constantemente com ajustes ocorrendo em frequência considerável."
                        },
                        # CV > 20%, Inversões ≤ 10%
                        {
                            "Faixa CV da derivada": "> 20%",
                            "Faixa % Inversões": "≤ 10%",
                            "Classificação": "Alto / Baixo",
                            "Interpretação": "a obra apresenta variações significativas na taxa de crescimento, indicando boa possibilidade de períodos parados ou lançamentos concentrados ou poucos registros na obra. No entanto, a frequência de ajustes parece baixa."
                        },
                        # CV > 20%, Inversões > 10%
                        {
                            "Faixa CV da derivada": "> 20%",
                            "Faixa % Inversões": "> 10%",
                            "Classificação": "Alto / Alto",
                            "Interpretação": "a obra apresenta variações significativas na taxa de crescimento, indicando boa possibilidade de períodos parados ou lançamentos concentrados ou poucos registros na obra. Ademais, a frequência de ajustes é alta."
                        },
                    ]

        if (indicadores['ID_desv_pad'] <= 0.2) and (indicadores['ID_rev'] <= 0.1):
            interpretacoes['ID'] = data_ranges[0]['Interpretação']
        elif (indicadores['ID_desv_pad'] <= 0.2) and (indicadores['ID_rev'] > 0.1):
            interpretacoes['ID'] = data_ranges[1]['Interpretação']
        elif (indicadores['ID_desv_pad'] > 0.2) and (indicadores['ID_rev'] <= 0.1):
            interpretacoes['ID'] = data_ranges[2]['Interpretação']
        else:
            interpretacoes['ID'] = data_ranges[3]['Interpretação']

        # --- IRange ---
        irange = indicadores['IRange']
        if irange == 0:
            interpretacoes['IRange'] = f"não houve lançamentos em que a derivada superou {perc:.2%} do valor da obra"
        else:
            interpretacoes['IRange'] = f"{irange} excursão(ões) em que a derivada superou {perc:.2%} do valor da obra"

        # --- IED ---
        ied = indicadores['IED_dias']
        if ied == 0:
            interpretacoes['IED_dias'] = "quantidade de dias parado não supera limiar regulatório da tipologia"
        else:
            interpretacoes['IED_dias'] = "estagnação prolongada detectada, quantidade de dias parado supera limiar regulatório da tipologia"

        # --- KPI_CRESC ---
        kpi_cresc = indicadores['KPI_CRESC (%)']
        if kpi_cresc == 0:
            interpretacoes['KPI_CRESC (%)'] = "indicando crescimento sempre positivo"
        elif kpi_cresc < 0.1:
            interpretacoes['KPI_CRESC (%)'] = "indicando existência de pequenas quedas pontuais, isto é, menos de 10% dos lançamentos conduzem a reduções do acumulado"
        else:
            interpretacoes['KPI_CRESC (%)'] = "indicando variações negativas frequentes no acumulado, isto é, 10% ou mais dos lançamento conduzem a reduções do acumulado"

        # --- KPI_GAP ---
        kpi_gap = indicadores['KPI_GAP (dias)']
        if kpi_gap < 30:
            interpretacoes['KPI_GAP (dias)'] = "indicando que inexiste longos períodos de inatividade recente, antes da unitização"
        elif kpi_gap < 90:
            interpretacoes['KPI_GAP (dias)'] = "indicando que há um período relevante de inatividade, antes da unitização, mas dentro dos 90 dias"
        else:
            interpretacoes['KPI_GAP (dias)'] = "indicando inatividade prolongada ao final da série, antes da unitização, superior aos 90 dias"

        # --- KPI_PER ---
        kpi_gap = indicadores['KPI_PER']
        if kpi_gap <= 1.0:
            interpretacoes['KPI_PER'] = "o período da obra encontra-se conforme o perfil regulatório"
        elif kpi_gap <= 1.5:
            interpretacoes['KPI_PER'] = "o período da obra encontra-se acima do perfil regulatório"
        else:
            interpretacoes['KPI_PER'] = "o período da obra encontra-se muito acima do perfil regulatório"

        # --- CMD ---
        CMD = f"{indicadores['CMD']:,.2f}".replace(".","x").replace(",",".").replace("x",",")
        if indicadores['CMD'] == 0:
            interpretacoes['CMD'] = "O valor está zerado."
        else:
            interpretacoes['CMD'] = f"O valor médio por dia de projeto é de R$ {CMD}."
        if indicadores['Nr_TI'] != "ND":
            if len(df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']])==1:
                MED = f"{df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']]['media'].iloc[0]:,.2f}".replace(".","x").replace(",",".").replace("x",",")
                DES_PAD = f"{df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']]['desvio_padrao'].iloc[0]:,.2f}".replace(".","x").replace(",",".").replace("x",",")
                Q1 = f"{df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']]['q1'].iloc[0]:,.2f}".replace(".","x").replace(",",".").replace("x",",")
                Q2 = f"{df_CARACT[df_CARACT['Nr_TI']==indicadores['Nr_TI']]['q3'].iloc[0]:,.2f}".replace(".","x").replace(",",".").replace("x",",")

                interpretacoes['CMD'] += f""" Para esta tipologia, {indicadores['Nr_TI']}, temos média de R$ {MED},
                com desvio padrão de R$ {DES_PAD}. O primeiro quartil é R$ {Q1} e o terceiro quartil é R$ {Q2}."""

        # --- UC_TOT ---
        UC_TOT = indicadores['UC_TOT']
        if UC_TOT == 0:
            interpretacoes['UC_TOT'] = "entendemos não ser investimento, trata-se de despesa por não ter material capitalizável"
        elif UC_TOT <= 0.1:
            interpretacoes['UC_TOT'] = f"chamou atenção a baixa participação de itens capitalizáveis, {UC_TOT:.2%}"
        else:
            interpretacoes['UC_TOT'] = f"a participação de itens capitalizáveis é de {UC_TOT:.2%}"
        

        if indicadores['KPI_PER']>1:
            texto = f"""
                Foi analisado os lançamentos do razão de uma obra, {df_dd['Txt_Desc_ODI'].iloc[0]}. A obra
                iniciou em {df_dd['Dt_Inic_Proj'].iloc[0]} e foi energizada em {df_dd['Dt_Energ'].iloc[0]}.
                A transferência para o ativo imobilizado ocorreu em {df_dd['Dt_Uniti'].iloc[0]}. Obtemos o valor
                de {indicadores['KPI_CRESC (%)']:.2%} para a proporção de vezes em que o valor acumulado (coluna 'cumulativo')
                possui 'quebras' no crescimento (delta de cumulativo < 0); {interpretacoes['KPI_CRESC (%)']}. Obtemos o valor
                de {indicadores['KPI_GAP (dias)']:.2f} dias sem movimentações positivas de UC/UAR
                (valor > 0) no final da obra, em relação à data de unitização do projeto; {interpretacoes['KPI_GAP (dias)']}.
                Obtemos o valor de {indicadores['CTA']:.2f} para a distribuição temporal de lançamentos do projeto; {interpretacoes['CTA']}.
                Obtemos o valor de {indicadores['ID_desv_pad']:.2%} para irregularidade da derivada e {indicadores['ID_rev']:.2%} para reversões de sentido, dos lançamentos do projeto; {interpretacoes['ID']}
                Obtemos o valor de {indicadores['IRange']:.2f} para o número de vezes que ocorre uma derivada relevante nos lançamentos do projeto; isto é, {interpretacoes['IRange']}.
                Obtemos o valor de {int(indicadores['IED_dias'])} para o maior período consecutivo com derivada próxima de zero (em dias) nos lançamentos do projeto; isto é, {interpretacoes['IED_dias']}.
                Obtemos o valor de {indicadores['KPI_PER']:.2f} para a relação período da obra sobre o regulatório para a TI do projeto; assim, {interpretacoes['KPI_PER']}.
                No geral, tivemos {indicadores['IEg_dias']} dias como máxima distância entre lançamentos de qualquer natureza de gasto.
                Por sua vez, tivemos {indicadores['IEuc_dias']} dias como máxima distância entre lançamentos de natureza de gasto de UC/UAR,
                considerando o último lançamento como proxy de UC/UAR também. Nada obstante, nessa obra temos que cerca de
                {indicadores['CA_TOT']:.2%} representam os custos de mão de obra no projeto, considerando o valor total da obra.
                Nesta obra, {interpretacoes['UC_TOT']}. {interpretacoes['CMD']}
                """
        else:
            texto = f"""
                Foi analisado os lançamentos do razão de uma obra, {df_dd['Txt_Desc_ODI'].iloc[0]}. A obra
                iniciou em {df_dd['Dt_Inic_Proj'].iloc[0]} e foi energizada em {df_dd['Dt_Energ'].iloc[0]}.
                A transferência para o ativo imobilizado ocorreu em {df_dd['Dt_Uniti'].iloc[0]}.
                No geral, tivemos {indicadores['IEg_dias']} dias como máxima distância entre lançamentos de qualquer natureza de gasto.
                Por sua vez, tivemos {indicadores['IEuc_dias']} dias como máxima distância entre lançamentos de natureza de gasto de UC/UAR,
                considerando o último lançamento como proxy de UC/UAR também.  Nada obstante, nessa obra temos que cerca de
                {indicadores['CA_TOT']:.2%} representam os custos de mão de obra no projeto, considerando o valor total da obra.
                Obtemos o valor de {indicadores['KPI_PER']:.2f} para a relação período da obra sobre o regulatório para a TI do projeto; assim, {interpretacoes['KPI_PER']}.
                Nesta obra, {interpretacoes['UC_TOT']}. {interpretacoes['CMD']}
                """
        if indicadores['FLG_MOP']:
            texto += """Há lançamentos de MOP, sem lançamentos de material no mês."""
        if indicadores['FLG_ST']:
            texto += """Há lançamentos de ST, sem lançamentos de material no mês."""
        if indicadores['FLG_JOA']:
            texto += """Há lançamentos de JOA, sem lançamentos de material no mês."""
        return texto
    # Leitura única  
    tese = NR_TI_ROA(st.session_state.tra_dir, st)
    df_PR_all = ler_roa_uv(st.session_state.tra_dir, Empresa, st.session_state.dt_fim.year, st)
    df_PR_all = df_PR_all.merge(tese, how = 'left', on = 'Cd_SubODI')
    df_dd_all = ler_ros_uv(st.session_state.tra_dir, Empresa, st.session_state.dt_fim.year, st)
    
    df_PR_all['data'] = pd.to_datetime(df_PR_all['data'])
    projetos = sorted(df_PR_all['Cd_SubODI'].dropna().unique().tolist())
    df_TOT = []
    
    if st:
        pb = st.progress(0.0, text="Análise das obras")
   
    for i, prj in enumerate(projetos, 1):
        df_PR = df_PR_all[df_PR_all['Cd_SubODI'] == prj]
        df_dd = df_dd_all[df_dd_all.get('Cd_SubODI', None) == prj] if not df_dd_all.empty and 'Cd_SubODI' in df_dd_all else pd.DataFrame()

        indicadores = calcular_kpis_uv(df_PR, prj, st.session_state.tra_dir, lim=0.1, eps=1.0, st = st)

        try:
            indicadores['texto'] = fnc_int(indicadores, df_dd)
        except NameError:
            indicadores['texto'] = ""
        indicadores['Cd_SubODI'] = prj
        df_TOT.append(indicadores)

        if st:
            pb.progress(i/len(projetos), text=f"Análise de {prj} ({i}/{len(projetos)})")

@monitor_completo(st.session_state.LOGGER)
def ais_roa_conc_cmp(bd = None, dir_trab = None, empresa = None, st = None):
    a = st.progress(0, "Iniciando o cálculo")
    dir_trabm = dir_trab.replace("AIS_ANLS","")
    arquivo_csv = [
                        os.path.join(rf"{dir_trabm}DADOS_BRUTOS_MANUAL", f)
                        for f in os.listdir(rf"{dir_trabm}\DADOS_BRUTOS_MANUAL")
                        if f.lower().endswith('.csv') and (f.lower()[:4]=="roa_")
                    ]
    arq = arquivo_csv[0].replace("\\","/")

    lst_UC_nus = (
                    "100","105","110","112","115","140","145","150","155","170","175","185","205","215",
                    "220","225","240","245","260","275","280","285","300","320","335","350","355","360",
                    "365","370","375","380","385","390","395","400","405","410","415","420","425","430",
                    "435","440","445","450","455","460","465","470","475","480","485","490","500","505",
                    "510","515","520","525","530","550","555","585","590","595","600","610"
                 )

    chaves = ['Cd_ODI','Cd_SubODI','Nr_TI', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6',
               'UND', 'Ano']
    suf_esq = '_ROA'
    suf_dir = '_AIS'
    
    a.progress(5, "Importando o ROA...")

    erro = {}
    df_ROA = pd.DataFrame()
    for enc in ['CP1252', 'latin-1', 'utf-8', 'utf-8-sig' ]:
        try:
            SQLq = f"""
                        SELECT 
                            CAST(Cd_ODI AS STRING) AS Cd_ODI,
                            CAST(Cd_SubODI AS STRING) AS Cd_SubODI,
                            TRY_CAST(TRIM(Nr_TI) AS INTEGER) AS Nr_TI,
                            TRY_CAST(TRIM(Nr_TUC) AS INTEGER) AS Nr_TUC,
                            TRY_CAST(TRIM(Nr_A1) AS INTEGER) AS Nr_A1,
                            TRY_CAST(TRIM(Nr_A2) AS INTEGER) AS Nr_A2,
                            TRY_CAST(TRIM(Nr_A3) AS INTEGER) AS Nr_A3,
                            TRY_CAST(TRIM(Nr_A4) AS INTEGER) AS Nr_A4,
                            TRY_CAST(TRIM(Nr_A5) AS INTEGER) AS Nr_A5,
                            TRY_CAST(TRIM(Nr_A6) AS INTEGER) AS Nr_A6,
                            UPPER(TRIM(Unidade)) AS UND,
                            CAST(
                                    strftime(
                                        strptime(Dt_Lcmto, '%Y/%m/%d'),
                                        '%Y'
                                    ) AS DOUBLE
                                ) AS Ano,
                            SUM(REPLACE(REPLACE(Qtd, '.',''), ',', '.')::DOUBLE) AS Qtd
                        FROM read_csv('{arq}', delim='|',
                                                null_padding=true, 
                                                encoding = '{enc}',
                                                parallel = true,
                                                all_varchar = true)
                        WHERE Cd_NG = '1' AND Nr_TUC NOT IN {lst_UC_nus}
                        GROUP BY ALL
                        """
            df_ROA = duckdb.query(SQLq).to_df()
            break
        except Exception as e:
            erro[enc] = e

    if df_ROA.empty:
        st.write(erro)
        raise UserWarning("Falhou leitura do ROA")
    a.progress(10, "Importando o AIS...")
    dt_ARQ = sql.max_arq("AIS", bd, empresa)
    if dt_ARQ:
        SQLq = f"""
            SELECT 
                    Cd_ODI,
                    CAST(Cd_SubODI AS TEXT) as Cd_SubODI,
                    CAST(Nr_TI AS INTEGER) AS Nr_TI,
                    CAST(Nr_TUC AS INTEGER) AS Nr_TUC,
                    CAST(Nr_A1 AS INTEGER) AS Nr_A1,
                    CAST(Nr_A2 AS INTEGER) AS Nr_A2,
                    CAST(Nr_A3 AS INTEGER) AS Nr_A3,
                    CAST(Nr_A4 AS INTEGER) AS Nr_A4,
                    CAST(Nr_A5 AS INTEGER) AS Nr_A5,
                    CAST(Nr_A6 AS INTEGER) AS Nr_A6,
                    UPPER(TRIM(Cd_UND_AIS)) AS UND,
                    CASE
                        -- Formato ISO (YYYY-MM-DD)
                        WHEN Dt_Imob GLOB '[0-9][0-9][0-9][0-9]-*-*' THEN
                            CAST(strftime('%Y', Dt_Imob) AS INTEGER)

                        -- Formato brasileiro (DD/MM/YYYY)
                        WHEN Dt_Imob GLOB '[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]' THEN
                            CAST(strftime(
                                '%Y',
                                substr(Dt_Imob, 7, 4) || '-' || substr(Dt_Imob, 4, 2) || '-' || substr(Dt_Imob, 1, 2)
                            ) AS INTEGER)

                        -- Caso não seja nenhum dos formatos conhecidos
                        ELSE NULL
                    END AS Ano,
                    SUM(Qtd_AIS) AS Qtd
                FROM AIS
                WHERE dt_ARQ = '{dt_ARQ}' AND FLG_PER = '1' AND Nr_TUC NOT IN {lst_UC_nus}
                GROUP BY
                    Cd_ODI, Cd_SubODI,
                    CAST(Nr_TI AS INTEGER),
                    CAST(Nr_TUC AS INTEGER),
                    CAST(Nr_A1 AS INTEGER), CAST(Nr_A2 AS INTEGER), CAST(Nr_A3 AS INTEGER),
                    CAST(Nr_A4 AS INTEGER), CAST(Nr_A5 AS INTEGER), CAST(Nr_A6 AS INTEGER),
                    UPPER(TRIM(Cd_UND_AIS)),
                    CAST(strftime('%Y', Dt_Imob) AS INTEGER)
            """
        df_AIS = pd.read_sql(SQLq, bd)
    else:
        if st:
            st.error('Falha ao importar o arquivo AIS da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS da base local.')


    left  = df_ROA.copy()
    right = df_AIS.copy()

    etapas = [
                (['Cd_ODI','Cd_SubODI','Nr_TI', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6','UND'], False),
                (['Cd_ODI','Cd_SubODI','Nr_TI', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6'], False),
                (['Cd_ODI','Cd_SubODI','Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6'], False),
                (['Cd_ODI','Cd_SubODI','Nr_TUC'], False),
                (['Cd_SubODI','Nr_TUC'], False),
                (['Nr_TUC'], False)               
             ]

    conciliados = []
    etapa_num = 1

    colunas = ["Nr_Etapa", "Qtd_CONC", "Qtd_CONC_OK", "Qtd_CONC_DIV", f"Qtd_AUS{suf_dir}", f"Qtd_AUS{suf_esq}"]
    df_REL = pd.DataFrame(columns=colunas)

    
    total_etapas = len(etapas)

    for etapa_num, (chaves, usa_ano) in enumerate(etapas, start=1):
        progresso = min(10 + 5 * etapa_num, 100)

        a.progress(
                        progresso,
                        (
                            "Fazendo conciliação do ROA com AIS, "
                            f"chave completa, etapa {etapa_num}/{total_etapas}..."
                        ),
                    )

        if usa_ano:
            left = left.assign(ANO=left["Ano"])
            right = right.assign(ANO=right["Ano"])

        colunas_etapa = [*chaves, "Qtd"]

        colunas_ausentes_left = [
                                    coluna
                                    for coluna in colunas_etapa
                                    if coluna not in left.columns
                                ]

        colunas_ausentes_right = [
                                    coluna
                                    for coluna in colunas_etapa
                                    if coluna not in right.columns
                                ]

        if colunas_ausentes_left:
            st.write(left)

            raise UserWarning(
                                "Colunas ausentes na base esquerda, "
                                f"etapa {etapa_num}: {colunas_ausentes_left}"
                            )

        if colunas_ausentes_right:
            st.write(right)

            raise UserWarning(
                                "Colunas ausentes na base direita, "
                                f"etapa {etapa_num}: {colunas_ausentes_right}"
                            )

        left_ini = left[colunas_etapa].copy()
        right_ini = right[colunas_etapa].copy()

        left_ini = (
                        left_ini
                        .groupby(chaves, dropna=False, as_index=False)["Qtd"]
                        .sum()
                    )

        right_ini = (
                        right_ini
                        .groupby(chaves, dropna=False, as_index=False)["Qtd"]
                        .sum()
                    )


        duplicados_left = left_ini.duplicated(chaves, keep=False)
        duplicados_right = right_ini.duplicated(chaves, keep=False)
        if duplicados_left.sum() + duplicados_right.sum() > 0:
            st.warning(
                        f"Etapa {etapa_num}: "
                        f"{duplicados_left.sum()} registros duplicados à esquerda e "
                        f"{duplicados_right.sum()} à direita."
                    )
        qtd_esq = f"Qtd{suf_esq}"
        qtd_dir = f"Qtd{suf_dir}"

        merged = left_ini.merge(
                                    right_ini,
                                    on=chaves,
                                    how="inner",
                                    suffixes=(suf_esq, suf_dir),
                                    validate="many_to_many",
                                )

        if merged.empty:
            continue

        merged["etapa_conciliacao"] = etapa_num

        chaves_conciliadas = merged[chaves].drop_duplicates()

        left_residual = left_ini.merge(
                                            chaves_conciliadas,
                                            on=chaves,
                                            how="left",
                                            indicator=True,
                                            validate="many_to_one",
                                        )

        left_residual = (
                                left_residual
                                .loc[left_residual["_merge"].eq("left_only")]
                                .drop(columns="_merge")
                            )

        right_residual = right_ini.merge(
                                            chaves_conciliadas,
                                            on=chaves,
                                            how="left",
                                            indicator=True,
                                            validate="many_to_one",
                                        )

        right_residual = (
                                right_residual
                                .loc[right_residual["_merge"].eq("left_only")]
                                .drop(columns="_merge")
                            )

        qtd_iguais = merged[qtd_esq].eq(merged[qtd_dir])
        qtd_divergentes = ~qtd_iguais

        dados_relatorio = {
                                "Nr_Etapa": etapa_num,
                                "Qtd_CONC": len(merged),
                                "Qtd_CONC_OK": int(qtd_iguais.sum()),
                                "Qtd_CONC_DIV": int(qtd_divergentes.sum()),
                                f"Qtd_AUS{suf_esq}": len(left_residual),
                                f"Qtd_AUS{suf_dir}": len(right_residual),
                            }

        df_REL = pd.concat(
                                [
                                    df_REL,
                                    pd.DataFrame([dados_relatorio]),
                                ],
                                ignore_index=True,
                            )

        df_prov = merged.copy()

        df_prov[qtd_esq] = pd.to_numeric(
                                            df_prov[qtd_esq],
                                            errors="coerce",
                                        ).fillna(0.0)

        df_prov[qtd_dir] = pd.to_numeric(
                                            df_prov[qtd_dir],
                                            errors="coerce",
                                        ).fillna(0.0)

        df_prov["DELTA"] = df_prov[qtd_esq] - df_prov[qtd_dir]

        qtd_conciliada = df_prov[[qtd_esq, qtd_dir]].min(axis=1)
        df_prov[qtd_esq] = qtd_conciliada
        df_prov[qtd_dir] = qtd_conciliada

        saldo_esquerda = (
                            df_prov
                            .loc[df_prov["DELTA"].gt(0), chaves + ["DELTA"]]
                            .rename(columns={"DELTA": "Qtd"})
                        )

        saldo_direita = (
                            df_prov
                            .loc[df_prov["DELTA"].lt(0), chaves + ["DELTA"]]
                            .rename(columns={"DELTA": "Qtd"})
                        )

        saldo_direita["Qtd"] = saldo_direita["Qtd"].abs()

        conciliado_etapa = df_prov[
                                    chaves
                                    + [
                                        qtd_esq,
                                        qtd_dir,
                                        "etapa_conciliacao",
                                    ]
                                ].copy()

        left = pd.concat(
                            [
                                left_residual,
                                saldo_esquerda,
                            ],
                            ignore_index=True,
                        )

        right = pd.concat(
                            [
                                right_residual,
                                saldo_direita,
                            ],
                            ignore_index=True,
                        )

        conciliados.append(conciliado_etapa)

        if left.empty or right.empty:
            break

    if len(conciliados) == 0:
        return pd.DataFrame(), left, right 
    
    df_conciliado = pd.concat(conciliados, ignore_index=True)
    for col in ['Cd_ODI','Cd_SubODI','Nr_TI', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6','UND']:
        if col not in df_conciliado:
            try:
                etapas[0][0].remove(col)
            except Exception as e:
                st.text(col)
                st.write(df_conciliado)
                st.write(etapas[0][0])
                raise UserWarning(f"Problemas nas Etapas: {e}")
    df_conciliado = df_conciliado.sort_values(["etapa_conciliacao"] + etapas[0][0])

    df_REL['TOT_CONC'] = df_REL['Qtd_CONC'].cumsum()
    df_REL['TOT_REG'] = df_REL['TOT_CONC'] + df_REL[f'Qtd_AUS{suf_esq}'] + df_REL[f'Qtd_AUS{suf_dir}']
    df_REL['Pct_CONC'] = (df_REL['TOT_CONC'] - df_REL['Qtd_CONC_DIV']) / df_REL['TOT_REG']

    PEP_UC_ROA  = df_ROA.copy()
    PEP_UC_AIS = df_AIS.copy()

    PEP_UC_ROA = PEP_UC_ROA.groupby(['Cd_SubODI','Nr_TUC'], dropna=False)['Qtd'].sum().reset_index()
    PEP_UC_AIS = PEP_UC_AIS.groupby(['Cd_SubODI','Nr_TUC'], dropna=False)['Qtd'].sum().reset_index()

    PEP_UC_CMP = PEP_UC_ROA.merge(PEP_UC_AIS, how='outer', on=['Cd_SubODI','Nr_TUC'], suffixes=('_ROA','_AIS'), indicator=True)
    PEP_UC_CMP['Qtd_ROA'] = PEP_UC_CMP['Qtd_ROA'].fillna(0)
    PEP_UC_CMP['Qtd_AIS'] = PEP_UC_CMP['Qtd_AIS'].fillna(0)
    PEP_UC_CMP['DIF (nesse caso não se faz compensação inter-projetos)'] = PEP_UC_CMP['Qtd_ROA'] - PEP_UC_CMP['Qtd_AIS']
    dic_UC_PEP = {
                        'both' : f'NO',
                        'left_only' : f'Sobra do ROA',
                        'right_only' : f'Sobra do AIS',
                }
    PEP_UC_CMP['OBS_SFF_01'] = PEP_UC_CMP['_merge'].astype(str).replace(dic_UC_PEP)
    
    diferenca_maior = ~np.isclose(PEP_UC_CMP['Qtd_ROA'], PEP_UC_CMP['Qtd_AIS'], rtol=0.001, atol=0.0)
    positivos = (PEP_UC_CMP['Qtd_ROA'] - PEP_UC_CMP['Qtd_AIS']) > 0
    PEP_UC_CMP['OBS_SFF_02'] = 'NO'
    PEP_UC_CMP.loc[diferenca_maior & positivos, 'OBS_SFF_02'] = 'Verificar as divergências de quantidade. Sobra ROA.'
    PEP_UC_CMP.loc[diferenca_maior & ~positivos, 'OBS_SFF_02'] = 'Verificar as divergências de quantidade. Sobra AIS.'

    PEP_UC_CMP['OBS_SFF'] = (
                                np.where(PEP_UC_CMP['OBS_SFF_01'] == "NO",
                                         np.where(PEP_UC_CMP['OBS_SFF_02'] == "NO",
                                                  "NO",
                                                  PEP_UC_CMP['OBS_SFF_02']
                                                 ),
                                         PEP_UC_CMP['OBS_SFF_01']
                                        )
                            )
    PEP_UC_CMP = PEP_UC_CMP.drop(columns=['_merge','OBS_SFF_02','OBS_SFF_01'])

    a.progress(50, "Salvando arquivo com conciliação com chave completa...")
    with pd.ExcelWriter(rf'{dir_trab}/REL_CONCILIACAO_INCR_QTD_CHV_CMP.xlsx', engine='xlsxwriter') as writer:
        df_REL.to_excel(writer, sheet_name="REL_CONC", index=False)
        df_conciliado.to_excel(writer, sheet_name="Conciliados", index=False)
        PEP_UC_CMP.to_excel(writer, sheet_name="Conciliados_PRJ_UC", index=False)
        left.to_excel(writer, sheet_name="Nao_Conciliados_ROA", index=False)
        right.to_excel(writer, sheet_name="Nao_Conciliados_AIS", index=False)
        

        for sheet_name in ["REL_CONC","Conciliados","Conciliados_PRJ_UC","Nao_Conciliados_ROA","Nao_Conciliados_AIS"]:
            worksheet = writer.sheets[sheet_name]
            df = {  "REL_CONC": df_REL,
                    "Conciliados": df_conciliado, 
                    "Conciliados_PRJ_UC": PEP_UC_CMP,
                    "Nao_Conciliados_ROA": left,
                    "Nao_Conciliados_AIS": right}[sheet_name]

            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 2
                worksheet.set_column(i, i, max_len)

    if st:
        registrar_artefato(st.session_state.database_MAN, 
                           st.session_state.execucao_id, 
                           file_path = rf'{dir_trab}/REL_CONCILIACAO_INCR_QTD_CHV_CMP.xlsx',
                           tipo_artefato = "SAIDA", 
                           calcular_hash = True)
    df_REL.to_sql('RESUMO_QTD_AIS_ROA_CHV_CMP', bd, if_exists='replace', index=False)
    a.progress(60, "Salvando arquivo com conciliação com chave completa...")
    df_AIS_UC = df_AIS.groupby(by=['Nr_TUC','UND'], dropna=False)['Qtd'].sum().reset_index()
    df_ROA_UC = df_ROA.groupby(by=['Nr_TUC','UND'], dropna=False)['Qtd'].sum().reset_index()

    a.progress(70, "Fazendo a conciliação com chave simples...")
    merged = df_AIS_UC.merge(
                                df_ROA_UC,
                                on=['Nr_TUC','UND'],
                                how="outer",
                                suffixes=(suf_esq, suf_dir),
                                indicator=True
                            )
    
    faltando_no_AIS = merged[merged["_merge"] == "left_only"][['Nr_TUC','UND','Qtd_ROA','Qtd_AIS']]
    faltando_no_ROA = merged[merged["_merge"] == "right_only"][['Nr_TUC','UND','Qtd_ROA','Qtd_AIS']]
    conciliados     = merged[merged["_merge"] == "both"][['Nr_TUC','UND','Qtd_ROA','Qtd_AIS']]

    conciliados['DELTA'] = (conciliados['Qtd_ROA'] - conciliados['Qtd_AIS']) / (conciliados['Qtd_AIS'] + 1e-6)

    df_AIS_UC = df_AIS.groupby(by=['Nr_TUC'], dropna=False)['Qtd'].sum().reset_index()
    df_ROA_UC = df_ROA.groupby(by=['Nr_TUC'], dropna=False)['Qtd'].sum().reset_index()

    merged = df_AIS_UC.merge(
                                df_ROA_UC,
                                on=['Nr_TUC'],
                                how="outer",
                                suffixes=(suf_esq, suf_dir),
                                indicator=True
                            )
    
    faltando_no_AIS2 = merged[merged["_merge"] == "left_only"][['Nr_TUC','Qtd_ROA','Qtd_AIS']]
    faltando_no_ROA2 = merged[merged["_merge"] == "right_only"][['Nr_TUC','Qtd_ROA','Qtd_AIS']]
    conciliados2     = merged[merged["_merge"] == "both"][['Nr_TUC','Qtd_ROA','Qtd_AIS']]

    conciliados2['DELTA'] = (conciliados2['Qtd_ROA'] - conciliados2['Qtd_AIS']) / (conciliados2['Qtd_AIS'] + 1e-6)

    a.progress(75, "Salvando a conciliação com chave simples...")
    with pd.ExcelWriter(f'{dir_trab}/REL_CONCILIACAO_INCR_QTD_CHV_SMP.xlsx', engine='xlsxwriter') as writer:
        conciliados.to_excel(writer, sheet_name="Conciliados_UC_UND", index=False)
        faltando_no_ROA.to_excel(writer, sheet_name="Nao_Conciliados_ROA_UC_UND", index=False)
        faltando_no_AIS.to_excel(writer, sheet_name="Nao_Conciliados_AIS_UC_UND", index=False)
        conciliados2.to_excel(writer, sheet_name="Conciliados_UC", index=False)
        faltando_no_ROA2.to_excel(writer, sheet_name="Nao_Conciliados_ROA_UC", index=False)
        faltando_no_AIS2.to_excel(writer, sheet_name="Nao_Conciliados_AIS_UC", index=False)

        for sheet_name in ["Conciliados_UC_UND", "Nao_Conciliados_ROA_UC_UND", "Nao_Conciliados_AIS_UC_UND",
                           "Conciliados_UC", "Nao_Conciliados_ROA_UC", "Nao_Conciliados_AIS_UC"]:
            worksheet = writer.sheets[sheet_name]
            df = {  
                    "Conciliados_UC_UND": conciliados, 
                    "Nao_Conciliados_ROA_UC_UND": faltando_no_ROA,
                    "Nao_Conciliados_AIS_UC_UND": faltando_no_AIS,
                    "Conciliados_UC": conciliados, 
                    "Nao_Conciliados_ROA_UC": faltando_no_ROA,
                    "Nao_Conciliados_AIS_UC": faltando_no_AIS}[sheet_name]

            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 2
                worksheet.set_column(i, i, max_len)

    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_trab}/REL_CONCILIACAO_INCR_QTD_CHV_SMP.xlsx',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    conciliados.to_sql('RESUMO_QTD_AIS_ROA_CHV_SMP_UC', bd, if_exists='replace', index=False)
    conciliados2.to_sql('RESUMO_QTD_AIS_ROA_CHV_SMP', bd, if_exists='replace', index=False)
    faltando_no_AIS2.to_sql('RESUMO_QTD_NC_AIS_ROA_CHV_SMP', bd, if_exists='replace', index=False)
    faltando_no_ROA2.to_sql('RESUMO_QTD_NC_AIS_ROA_CHV_SMP2', bd, if_exists='replace', index=False)
    a.progress(80, "Fazendo a conciliação com chave ODI+SUB_ODI+TI, em Valor, entre ROA e AIS, por TI...")

    erro = {}
    df_ROA = pd.DataFrame()
    for enc in ['CP1252', 'latin-1', 'utf-8', 'utf-8-sig' ]:
        try:
            SQLq = f"""
                        SELECT 
                            CAST(Cd_ODI AS STRING) AS Cd_ODI,
                            CAST(Cd_SubODI AS STRING) AS Cd_SubODI,
                            TRY_CAST(TRIM(Nr_TI) AS INTEGER) AS Nr_TI,
                            SUM(
                                TRY_CAST(
                                    REPLACE(
                                        REPLACE(TRIM(VL_tot), '.', ''),
                                        ',', '.'
                                    ) AS DOUBLE
                                )
                            ) AS VL
                        FROM read_csv(
                            '{arq}',
                            delim='|',
                            null_padding=true,
                            encoding='{enc}',
                            parallel=true,
                            all_varchar=true
                        )
                        GROUP BY ALL;
                    """
            df_ROA = duckdb.query(SQLq).to_df()
            break
        except Exception as e:
            erro[enc] = e
            
    if df_ROA.empty:
        st.write(erro)
        raise UserWarning("Falhou leitura do ROA")

    a.progress(82, "Importando o AIS...")
    dt_ARQ = sql.max_arq("AIS", bd, empresa)
    if dt_ARQ:
        SQLq = f"""
            SELECT 
                    CAST(Cd_ODI AS TEXT) AS Cd_ODI,
                    CAST(Cd_SubODI AS TEXT) AS Cd_SubODI,
                    CAST(Nr_TI AS INTEGER) AS Nr_TI,
                    SUM(VL_VOC) AS VL
                FROM AIS
                WHERE dt_ARQ = '{dt_ARQ}' AND FLG_PER = '1'
                GROUP BY
                    Cd_ODI,Cd_SubODI,
                    CAST(Nr_TI AS INTEGER)
            """
        df_AIS = pd.read_sql(SQLq, bd)
    else:
        if st:
            st.error('Falha ao importar o arquivo AIS da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS da base local.')

    left  = df_ROA.copy()
    right = df_AIS.copy()

    merged = left.merge(
                                right,
                                on=["Cd_ODI","Cd_SubODI","Nr_TI"],
                                how="outer",
                                suffixes=("_ROA", "_AIS"),
                                indicator=True
                            )
    faltando_no_ROA = merged[merged["_merge"] == "left_only"][["Cd_ODI","Cd_SubODI","Nr_TI",'VL_ROA','VL_AIS']].copy()
    faltando_no_AIS = merged[merged["_merge"] == "right_only"][["Cd_ODI","Cd_SubODI","Nr_TI",'VL_ROA','VL_AIS']].copy()
    conciliados     = merged[merged["_merge"] == "both"][["Cd_ODI","Cd_SubODI","Nr_TI",'VL_ROA','VL_AIS']].copy()

    conciliados['DELTA'] = (conciliados['VL_ROA'] - conciliados['VL_AIS']) / (conciliados['VL_AIS'] + 1e-6)

    a.progress(90, "Fazendo a conciliação com chave TI, em Valor, entre ROA e AIS, por TI...")
    df_AIS_UC = df_AIS.groupby(by=['Nr_TI'], dropna=False)['VL'].sum().reset_index()
    df_ROA_UC = df_ROA.groupby(by=['Nr_TI'], dropna=False)['VL'].sum().reset_index()
    
    merged = df_AIS_UC.merge(
                                df_ROA_UC,
                                on=["Nr_TI"],
                                how="outer",
                                suffixes=("_AIS", "_ROA"),
                                indicator=True
                            )
    
    faltando_no_ROA2 = merged[merged["_merge"] == "left_only"][["Nr_TI",'VL_ROA','VL_AIS']].copy()
    faltando_no_AIS2 = merged[merged["_merge"] == "right_only"][["Nr_TI",'VL_ROA','VL_AIS']].copy()
    conciliados2     = merged[merged["_merge"] == "both"][["Nr_TI",'VL_ROA','VL_AIS']].copy()

    conciliados2['DELTA'] = (conciliados2['VL_ROA'] - conciliados2['VL_AIS']) / (conciliados2['VL_AIS'] + 1e-6)

    a.progress(95, "Salvando a conciliação, em Valor, entre ROA e AIS, por TI...")
    with pd.ExcelWriter(f'{dir_trab}/REL_CONCILIACAO_INCR_VL_CHV_SMP.xlsx', engine='xlsxwriter') as writer:
        conciliados.to_excel(writer, sheet_name="Conciliados_UC_UND", index=False)
        faltando_no_ROA.to_excel(writer, sheet_name="Nao_Conciliados_ROA_UC_UND", index=False)
        faltando_no_AIS.to_excel(writer, sheet_name="Nao_Conciliados_AIS_UC_UND", index=False)
        conciliados2.to_excel(writer, sheet_name="Conciliados_UC", index=False)
        faltando_no_ROA2.to_excel(writer, sheet_name="Nao_Conciliados_ROA_UC", index=False)
        faltando_no_AIS2.to_excel(writer, sheet_name="Nao_Conciliados_AIS_UC", index=False)

        for sheet_name in ["Conciliados_UC_UND", "Nao_Conciliados_ROA_UC_UND", "Nao_Conciliados_AIS_UC_UND",
                           "Conciliados_UC", "Nao_Conciliados_ROA_UC", "Nao_Conciliados_AIS_UC"]:
            worksheet = writer.sheets[sheet_name]
            df = {  
                    "Conciliados_UC_UND": conciliados, 
                    "Nao_Conciliados_ROA_UC_UND": faltando_no_ROA,
                    "Nao_Conciliados_AIS_UC_UND": faltando_no_AIS,
                    "Conciliados_UC": conciliados2, 
                    "Nao_Conciliados_ROA_UC": faltando_no_ROA2,
                    "Nao_Conciliados_AIS_UC": faltando_no_AIS2}[sheet_name]

            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 2
                worksheet.set_column(i, i, max_len)

    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_trab}/REL_CONCILIACAO_INCR_VL_CHV_SMP.xlsx',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    conciliados.to_sql('RESUMO_VL_AIS_ROA_CHV_SMP_UC', bd, if_exists='replace', index=False)
    conciliados2.to_sql('RESUMO_VL_AIS_ROA_CHV_SMP', bd, if_exists='replace', index=False)
    a.empty()
    #now = datetime.now()
    #avl.success(f"  Hora de término, Análise ROA/AIS: {now.strftime('%H:%M:%S')}")
    return None

@monitor_completo(st.session_state.LOGGER)
def ros_rod_baixas_cmp(bd = None, dir_trab = None, empresa = None, st = None):
    if st: a = st.progress(0, "Iniciando o cálculo")
    dir_trabm = dir_trab.replace("AIS_ANLS","")
    arquivo_csv = [
                        os.path.join(f"{dir_trabm}DADOS_BRUTOS_MANUAL", f)
                        for f in os.listdir(rf"{dir_trabm}\DADOS_BRUTOS_MANUAL")
                        if f.lower().endswith('.csv') and (f.lower()[:4]=="rod_")
                    ]
    arq = arquivo_csv[0].replace("\\","/")
    suf_esq = '_ROD'
    suf_dir = '_ROS'
    
    if st: a.progress(5, "Importando o ROD...")

    erro = {}
    for enc in ['CP1252', 'latin-1', 'utf-8']:
        try:
            SQLq = f"""SELECT *
                                FROM (
                                        SELECT 
                                            CAST(Cd_ODD AS STRING) AS Cd_ODD,
                                            Cd_NG,
                                            SUM(REPLACE(REPLACE(REPLACE(VL_tot, '|-|','0'), '.',''), ',', '.')::DOUBLE) AS VL
                                        FROM read_csv('{arq}', 
                                                delim='|',
                                                null_padding=true, 
                                                encoding='{enc}',
                                                sample_size=-1,
                                                parallel=true)
                                        GROUP BY 
                                            Cd_ODD,
                                            Cd_NG
                                    )
                                PIVOT (
                                            SUM(VL) FOR Cd_NG IN (
                                                1 AS VL_ROD_UC,
                                                2 AS VL_ROD_COM,
                                                3 AS VL_ROD_MOP,
                                                4 AS VL_ROD_ST,
                                                5 AS VL_ROD_JOA,
                                                6 AS VL_ROD_Outros
                                            )
                                        );
                        """
            df_ROD = duckdb.query(SQLq).to_df()
            break
        except Exception as e:
            erro[enc] = e
            registrar_evento(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            nome_evento = 'conciliacao_rod_ros',
                            mensagem = f'Falhou na leitura do ROD com encoding {enc}.', 
                            nivel = 'ERRO',
                            detalhes = {'erro' : e})
            df_ROD = pd.DataFrame()

    if len(df_ROD)==0:
        st.text(erro)
        raise UserWarning("Você tem problema de codificação do arquivo.")

    if st: a.progress(10, "Importando o ROS...")
    dt_ARQ = sql.max_arq("ROS", bd, empresa, st)
    if dt_ARQ:
        SQLq = f"""
            SELECT 
                    CAST(Cd_ODD AS TEXT) AS Cd_ODD,
                    Txt_JUST_ODD,
                    SUM(VL_CA_ST_ODD) AS VL_ROS_ST,
                    SUM(VL_CA_MOP_ODD) AS VL_ROS_MOP
                FROM ROS
                WHERE dt_ARQ = '{dt_ARQ}'
                GROUP BY Cd_ODD,
                         Txt_JUST_ODD
        """
        df_ROS = pd.read_sql(SQLq, bd)

    else:
        if st:
            st.error('Falha ao importar o arquivo ROS da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ROS da base local.')

    suf_esq = "_ROD"  
    suf_dir = "_ROS"  
    left  = df_ROD.copy()
    right = df_ROS.copy()
    merged = left.merge(
                                right,
                                on=["Cd_ODD"],
                                how="outer",
                                suffixes=(suf_esq, suf_dir),
                                indicator=True
                            )
    
    colunas = ["Cd_ODD","Txt_JUST_ODD",'VL_ROD_UC',
                'VL_ROD_COM','VL_ROD_MOP','VL_ROD_ST',
                'VL_ROD_JOA','VL_ROD_Outros','VL_ROS_MOP',
                'VL_ROS_ST']
    faltando_no_ROD = merged[merged["_merge"] == "left_only"][colunas]
    faltando_no_ROS = merged[merged["_merge"] == "right_only"][colunas]
    conciliados     = merged[merged["_merge"] == "both"][colunas]
    conciliados['VL_ROD_MOP'] = conciliados['VL_ROD_MOP'].fillna(0)
    conciliados['VL_ROD_ST'] = conciliados['VL_ROD_ST'].fillna(0)

    conciliados['DELTA'] = round((abs(conciliados['VL_ROS_MOP']) + abs(conciliados['VL_ROS_ST']) 
                             - abs(conciliados['VL_ROD_MOP']) - abs(conciliados['VL_ROD_ST']))
                             / (abs(conciliados['VL_ROD_MOP']) + abs(conciliados['VL_ROD_ST']) + 1e-6),0)

    if st: a.progress(35, "Importando o ROD Qtd...")

    SQLq = f"""SELECT 
                    CAST(Cd_ODD AS STRING) AS Cd_ODD,
                    CAST(replace(CAST(Nr_TUC AS VARCHAR), '.', '') AS INTEGER) AS Nr_TUC,
                    SUM(CAST(REPLACE(REPLACE(CAST(Qtd AS VARCHAR), '.', ''), ',', '.') AS FLOAT)) AS Qtd
                FROM read_csv_auto('{arq}', delim='|', null_padding=true, ignore_errors=true)
                WHERE Cd_NG = '1'
                GROUP BY 
                    Cd_ODD,
                    Nr_TUC;
                """
    df_ROD = duckdb.query(SQLq).to_df()

    if st: a.progress(50, "Buscando arquivo BAIXAS Qtd...")
    dt_ARQ = sql.max_arq("BAIXAS", bd, empresa)
    if dt_ARQ:
        SQLq = f"""
            SELECT 
                    CAST(Cd_ODD AS TEXT) AS Cd_ODD,
                    CAST(Nr_TUC AS INTEGER) AS Nr_TUC,
                    (SUM(CAST(REPLACE(REPLACE(Qtd_INI, ',', '.'),'/','') AS DOUBLE)) - SUM(CAST(REPLACE(REPLACE(Qtd_FIN, ',', '.'),'/','') AS DOUBLE))) AS Qtd
                FROM BAIXAS
                WHERE dt_ARQ = '{dt_ARQ}'
                GROUP BY Cd_ODD,
                         Nr_TUC
        """
        df_BAIXAS = pd.read_sql(SQLq, bd)

    else:
        if st:
            st.error('Falha ao importar o arquivo BAIXAS da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo BAIXAS da base local.')
        
    suf_esq = "_ROD"  
    suf_dir = "_BAIXAS"  
    left  = df_ROD.copy()
    right = df_BAIXAS.copy()

    merged = left.merge(
                                right,
                                on=["Cd_ODD","Nr_TUC"],
                                how="outer",
                                suffixes=(suf_esq, suf_dir),
                                indicator=True
                            )
    
    if st: a.progress(75, "Conciliando...")
    colunas = ["Cd_ODD","Nr_TUC",'Qtd_ROD','Qtd_BAIXAS']
    faltando_no_ROD2 = merged[merged["_merge"] == "left_only"][colunas]
    faltando_no_BAIXAS = merged[merged["_merge"] == "right_only"][colunas]
    conciliados2    = merged[merged["_merge"] == "both"][colunas]
    conciliados2['Qtd_ROD'] = conciliados2['Qtd_ROD'].fillna(0)

    conciliados2['DELTA'] = round((abs(conciliados2['Qtd_BAIXAS']) - abs(conciliados2['Qtd_ROD']))
                             / (abs(conciliados2['Qtd_ROD']) + 1e-6),0)

    if st: a.progress(95, "Salvando a conciliação, em Valor, entre ROD, ROS e BAIXAS...")
    with pd.ExcelWriter(f'{dir_trab}/REL_CONCILIACAO_ROD_ROS_BAIXAS.xlsx', engine='xlsxwriter') as writer:
        conciliados.to_excel(writer, sheet_name="Conciliados_VL_ST_MOP", index=False)
        faltando_no_ROD.to_excel(writer, sheet_name="Nao_Conciliados_ROD_VL_ST_MOP", index=False)
        faltando_no_ROS.to_excel(writer, sheet_name="Nao_Conciliados_ROS_VL_ST_MOP", index=False)
        conciliados2.to_excel(writer, sheet_name="Conciliados_Qtd", index=False)
        faltando_no_ROD2.to_excel(writer, sheet_name="Nao_Conciliados_ROD_Qtd", index=False)
        faltando_no_BAIXAS.to_excel(writer, sheet_name="Nao_Conciliados_BAIXAS_Qtd", index=False)

        for sheet_name in ["Conciliados_VL_ST_MOP", "Nao_Conciliados_ROD_VL_ST_MOP", "Nao_Conciliados_ROS_VL_ST_MOP",
                           "Conciliados_Qtd", "Nao_Conciliados_ROD_Qtd", "Nao_Conciliados_BAIXAS_Qtd"]:
            worksheet = writer.sheets[sheet_name]
            df = {  
                    "Conciliados_VL_ST_MOP": conciliados, 
                    "Nao_Conciliados_ROD_VL_ST_MOP": faltando_no_ROD,
                    "Nao_Conciliados_ROS_VL_ST_MOP": faltando_no_ROS,
                    "Conciliados_Qtd": conciliados2, 
                    "Nao_Conciliados_ROD_Qtd": faltando_no_ROD2,
                    "Nao_Conciliados_BAIXAS_Qtd": faltando_no_BAIXAS}[sheet_name]

            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 2
                worksheet.set_column(i, i, max_len)

    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_trab}/REL_CONCILIACAO_ROD_ROS_BAIXAS.xlsx',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    conciliados.to_sql('Conciliados_VL_ST_MOP', bd, if_exists='replace', index=False)
    conciliados2.to_sql('Conciliados_Qtd', bd, if_exists='replace', index=False)
    faltando_no_ROD.to_sql('Nao_Conciliados_ROD_VL_ST_MOP', bd, if_exists='replace', index=False)
    faltando_no_ROD2.to_sql('Nao_Conciliados_ROD_Qtd', bd, if_exists='replace', index=False)
    faltando_no_ROS.to_sql('Nao_Conciliados_ROS_VL_ST_MOPP', bd, if_exists='replace', index=False)
    faltando_no_BAIXAS.to_sql('Nao_Conciliados_BAIXAS_Qtd', bd, if_exists='replace', index=False)

    SQLq = f"""SELECT *
                        FROM (
                                SELECT 
                                    Cd_ODD,
                                    Cd_NG,
                                    Cd_CA,
                                    SUM(CAST(REPLACE(REPLACE(REPLACE(REPLACE(VL_tot, '.',''), '|-|','0'), ',', '.'),'/','') AS DOUBLE)) AS VL
                                FROM read_csv_auto('{arq}', delim='|', null_padding=true, ignore_errors=true)
                                WHERE Cd_NG IN ('3','4')
                                GROUP BY 
                                    Cd_ODD,
                                    Cd_NG,
                                    Cd_CA
                             )
                        PIVOT (
                                    SUM(VL) FOR Cd_CA IN (
                                        1 AS VL_FRT_TRN,
                                        2 AS VL_PRJ,
                                        3 AS VL_GER,
                                        4 AS VL_FISC,
                                        5 AS VL_MONT,
                                        6 AS VL_SUP
                                    )
                                );
                """
    df_ROD_CA = duckdb.query(SQLq).to_df()
    df_ROD_CA.fillna(0).to_sql('ROD_CA_TP', bd, if_exists='replace', index=False)
    if st: a.empty()

    return None

@monitor_completo(st.session_state.LOGGER)
def abertura_voc(st=None, anl_inv=False, html_config = True):

    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    with sl.connect(f'{local}\BD_LOCAL\{empresa}_{ano}.db') as bd:
        if True:
            if html_config:
                if not anl_inv:
                    st.divider()
                    collls = st.columns([5,1,5], gap='small')
                    with collls[1]:
                        refazer = st.button("Refazer")
                else:
                    refazer = False
            else:
                refazer = True
            st.divider()
            if not sql.existe_tabela("TST_ABERTURA_PROJETOS_TI", bd) or refazer:
                with duckdb.connect() as con:
                    df = None
                    ultimo_erro = None
  
                    for fim_linha in [r"\r\n",r"\n",r"\r"]: 
                        try:   
                            SQLq = f"""
                                    SELECT 
                                        Cd_SubODI, 
                                        Nr_TI, 
                                        Cd_NG, 
                                        Cd_CA,
                                        COALESCE(FLG_DIR,0) AS FLG_DIR,
                                        SUM(COALESCE(VL_tot,0)) AS VL_TOT
                                    FROM 
                                        read_csv('{local}/AIS_ANLS/ROA_AUG_{empresa}.csv',
                                                        delim='|',
                                                        header=true,
                                                        quote='"',
                                                        escape='"', 
                                                        sample_size=-1,
                                                        strict_mode=false,
                                                        null_padding=true,
                                                        new_line='{fim_linha}') 
                                    GROUP BY
                                        Cd_SubODI, Nr_TI, Cd_NG, Cd_CA, COALESCE(FLG_DIR,0)
                                    ORDER BY
                                        Cd_SubODI, Nr_TI, Cd_NG, Cd_CA, COALESCE(FLG_DIR,0)

                                """
                            df = con.execute(SQLq).fetchdf()
                            break
                        except Exception as e:
                            ultimo_erro = e
                            st.warning(e)
                    if df is None:
                        st.warning("Sem FLG_DIR, fazendo por premissa.")
                        for fim_linha in [r"\r\n",r"\n",r"\r"]: 
                            try:   
                                SQLq = f"""
                                        SELECT 
                                            Cd_SubODI, 
                                            Nr_TI, 
                                            Cd_NG, 
                                            Cd_CA,
                                            SUM(COALESCE(VL_tot,0)) AS VL_TOT
                                        FROM 
                                            read_csv('{local}/AIS_ANLS/ROA_AUG_{empresa}.csv',
                                                            delim='|',
                                                            header=true,
                                                            quote='"',
                                                            escape='"', 
                                                            sample_size=-1,
                                                            strict_mode=false,
                                                            null_padding=true,
                                                            new_line='{fim_linha}') 
                                        GROUP BY
                                            Cd_SubODI, Nr_TI, Cd_NG, Cd_CA

                                    """
                                df = con.execute(SQLq).fetchdf()
                                break
                            except Exception as e:
                                ultimo_erro = e
                                st.warning(e)

                    if df is None:
                        raise UserWarning(
                                                f"Problemas na leitura do ROA_AUG. Último erro: {ultimo_erro}"
                                            )

                    if len(df) == 0:
                        raise UserWarning("Problemas no ROA_AUG")

                    SQLq = f"""
                            SELECT 
                                Cd_SubODI, 
                                Nr_TI, 
                                Cd_NG, 
                                Cd_CA,
                                Cd_Cls_Custo,
                                SUM(COALESCE(VL_tot,0)) AS VL_TOT
                            FROM 
                                read_csv('{local}/AIS_ANLS/ROA_AUG_{empresa}.csv',
                                                delim='|',
                                                header=true,
                                                quote='"',
                                                escape='"', 
                                                sample_size=-1,
                                                strict_mode=false,
                                                null_padding=true,
                                                new_line='{fim_linha}') 
                            GROUP BY
                                Cd_SubODI, Nr_TI, Cd_NG, Cd_CA, Cd_Cls_Custo

                        """
                    df_CLS_CST = con.execute(SQLq).fetchdf()
                    SQLq = f"""
                                        SELECT 
                                            *
                                        FROM 
                                            DSC_CLS_CUSTO t1 
                                        WHERE 
                                            t1.dt_ARQ = ?
                                    """
                    df_desc_cls_cst = sql.imp_tbl_forma_001('DSC_CLS_CUSTO', SQLq = SQLq, con = bd, st=st, Empresa=empresa)
                    if len(df_desc_cls_cst)>0:
                        df_desc_cls_cst['Cd_Cls_Custo'] = df_desc_cls_cst['Cd_Cls_Custo'].astype(str)
                        df_CLS_CST['Cd_Cls_Custo'] = df_CLS_CST['Cd_Cls_Custo'].astype(str)

                        df_CLS_CST = df_CLS_CST.merge(df_desc_cls_cst, on='Cd_Cls_Custo', how='outer', indicator=True)
                        dic_map = {
                                        'both' : 'NO',
                                        'left_only' : 'Preencher no arquivo DSC_CLS_CUSTO',
                                        'right_only' : 'Não empregado no ROA'
                                    }
                        df_CLS_CST['OBS_SFF'] = df_CLS_CST['_merge'].replace(dic_map)
                        df_CLS_CST = df_CLS_CST[['Cd_SubODI', 'Nr_TI', 'Cd_NG', 'Cd_CA',
                                                'Cd_Cls_Custo', 'Txt_Cls_Custo', 'VL_TOT',
                                                'OBS_SFF']]
                        df_CLS_CST.to_sql('TST_ABERTURA_PROJETOS_CLS_CST', bd, if_exists='replace', index=False)

                    #Suporte tem de ser indireto.
                    if 'FLG_DIR' in df.columns:
                        df.loc[df['Cd_CA'].fillna(0) == 6, 'FLG_DIR'] = 0
                    else:
                        df['FLG_DIR'] = 0
                        df.loc[df['Cd_CA'].fillna(0) == 5, 'FLG_DIR'] = 1
                    
                    ROA_NG = (df
                            .pivot_table(values="VL_TOT", index=["Cd_SubODI", "Nr_TI"], 
                                        columns="Cd_NG", aggfunc="sum", dropna=False, fill_value=0)
                            .rename_axis(columns=None)
                            .reset_index())
                    for n in range(1, 7):
                        if n not in ROA_NG.columns:
                            ROA_NG[n] = 0
                    ROA_NG = ROA_NG.rename(columns = {1 : 'VL_UC_TOT', 2 : 'VL_COM_TOT', 3 : 'VL_MOP_TOT',
                                                4 : 'VL_ST_TOT', 5 : 'VL_JOA_TOT', 6 : 'VL_OUT_TOT'})
                    
                    #====================================================================================4
                    for tipo in ['3','4']:
                        df_tipo = df[df['Cd_NG'].astype(str) == tipo].copy()
                        df_tipo['Cd_CA'] = df_tipo['Cd_CA'].astype('Int16').fillna(9)
                        df_tipo['CA_DIR'] = (
                                                df_tipo['Cd_CA'].astype(str)
                                                + '_'
                                                + df_tipo['FLG_DIR'].astype('Int16').astype(str)
                                                )
                        ROA_NGax = (df_tipo
                                .pivot_table(values="VL_TOT", index=["Cd_SubODI", "Nr_TI"], 
                                            columns='CA_DIR', aggfunc="sum", dropna=False, fill_value=0)
                                .rename_axis(columns=None)
                                .reset_index())
                        
                        for n in [1,2,3,4,5,6,9]:
                            for n1 in range(0,2):
                                if f'{n}_{n1}' not in ROA_NGax.columns:
                                    ROA_NGax[f'{n}_{n1}'] = 0.
                        if tipo=='3':
                            tag = 'MOP'
                        else:
                            tag = 'ST'

                        dic_ren_col = {}

                        for nm_col in ROA_NGax.columns:
                            if nm_col in ['Cd_SubODI','Nr_TI']:
                                continue
                            if nm_col == '1_0':
                                dic_ren_col[nm_col] = f'VL_{tag}_FRETE_IND'
                            elif nm_col == '1_1':
                                dic_ren_col[nm_col] = f'VL_{tag}_FRETE_DIR'
                            elif nm_col == '2_0':
                                dic_ren_col[nm_col] = f'VL_{tag}_PROJETO_IND'
                            elif nm_col == '2_1':
                                dic_ren_col[nm_col] = f'VL_{tag}_PROJETO_DIR'
                            elif nm_col == '3_0':
                                dic_ren_col[nm_col] = f'VL_{tag}_GERENCIAMENTO_IND'
                            elif nm_col == '3_1':
                                dic_ren_col[nm_col] = f'VL_{tag}_GERENCIAMENTO_DIR'
                            elif nm_col == '4_0':
                                dic_ren_col[nm_col] = f'VL_{tag}_FISC_IND'
                            elif nm_col == '4_1':
                                dic_ren_col[nm_col] = f'VL_{tag}_FISC_DIR'
                            elif nm_col == '5_0':
                                dic_ren_col[nm_col] = f'VL_{tag}_MONTAGEM_IND'
                            elif nm_col == '5_1':
                                dic_ren_col[nm_col] = f'VL_{tag}_MONTAGEM_DIR'
                            elif nm_col == '6_0':
                                dic_ren_col[nm_col] = f'VL_{tag}_SUPORTE_IND'
                            elif nm_col == '6_1':
                                dic_ren_col[nm_col] = f'VL_{tag}_SUPORTE_DIR'
                            elif nm_col == '9_0':
                                dic_ren_col[nm_col] = f'VL_{tag}_ND_IND'
                            elif nm_col == '9_1':
                                dic_ren_col[nm_col] = f'VL_{tag}_ND_DIR' 
                        
                        ROA_NGax = ROA_NGax.rename(columns = dic_ren_col)

                        lst_dir = [nm for nm in ROA_NGax if '_DIR' in nm]
                        lst_ind = [nm for nm in ROA_NGax if '_IND' in nm]

                        
                        ROA_NGax[f'VL_{tag}_DIRETO'] = ROA_NGax[lst_dir].sum(axis=1)
                        ROA_NGax[f'VL_{tag}_INDIRETO'] = ROA_NGax[lst_ind].sum(axis=1)
                         
                        ROA_NG = ROA_NG.merge(ROA_NGax, how='left', on = ["Cd_SubODI", "Nr_TI"])
                        ROA_NG = ROA_NG.fillna(0)
                    #====================================================================================
                    ROA_NG[f'Pct_TESTE01'] = np.where((ROA_NG['VL_MOP_DIRETO'] + ROA_NG['VL_ST_DIRETO'] + ROA_NG['VL_UC_TOT']  + ROA_NG['VL_COM_TOT'])>0,
                        (ROA_NG['VL_MOP_INDIRETO'] + ROA_NG['VL_ST_INDIRETO']) /
                        (ROA_NG['VL_MOP_DIRETO'] + ROA_NG['VL_ST_DIRETO'] + ROA_NG['VL_UC_TOT']  + ROA_NG['VL_COM_TOT']),
                        0
                        )
                    ROA_NG[f'Pct_TESTE02'] = np.where((ROA_NG['VL_MOP_DIRETO'] + ROA_NG['VL_ST_DIRETO'] + ROA_NG['VL_MOP_INDIRETO']  + ROA_NG['VL_ST_INDIRETO'])>0,
                        (ROA_NG['VL_MOP_INDIRETO'] + ROA_NG['VL_ST_INDIRETO']) /
                        (ROA_NG['VL_MOP_DIRETO'] + ROA_NG['VL_ST_DIRETO'] + ROA_NG['VL_MOP_INDIRETO']  + ROA_NG['VL_ST_INDIRETO']),
                        0
                        )    
                    ROA_NG['VL_TOT'] = ROA_NG[['VL_UC_TOT','VL_COM_TOT','VL_MOP_TOT','VL_ST_TOT','VL_JOA_TOT','VL_OUT_TOT']].sum(axis=1)
                    itens_ANL = []
                    for tag in ['MOP','ST']:
                        for n1 in ['FRETE','PROJETO','GERENCIAMENTO','FISC','MONTAGEM','SUPORTE','ND']:
                            for n2 in ['DIR','IND']:
                                ROA_NG[f'Pct_{tag}_{n1}_{n2}'] = (
                                    ROA_NG[f'VL_{tag}_{n1}_{n2}'] /
                                    (ROA_NG['VL_MOP_DIRETO'] + ROA_NG['VL_ST_DIRETO'] + ROA_NG['VL_UC_TOT']  + ROA_NG['VL_COM_TOT'])
                                    )
                                itens_ANL.append(f'Pct_{tag}_{n1}_{n2}')
                    #====================================================================================
                    ROA_NG = ROA_NG[ROA_NG['VL_TOT']!=0].copy()

                    ROA_NG_PRORI = (ROA_NG
                                    .groupby('Cd_SubODI')[['VL_UC_TOT','VL_COM_TOT','VL_MOP_TOT','VL_ST_TOT','VL_JOA_TOT','VL_OUT_TOT','VL_TOT']]
                                    .sum()
                                    .reset_index())
                    ROA_NG = ROA_NG.merge(ROA_NG_PRORI, how='left', on='Cd_SubODI', suffixes=("_TI","_PROJ"))
                    ROA_NG = ROA_NG.sort_values(by=['Cd_SubODI','Nr_TI'])

                    
                    ROA_NG['Pct_JOA_TI'] = (ROA_NG['VL_JOA_TOT_TI'] / (ROA_NG['VL_TOT_TI'] - ROA_NG['VL_JOA_TOT_TI'] - ROA_NG['VL_OUT_TOT_TI']))
                    ROA_NG['Pct_JOA_PROJ'] = (ROA_NG['VL_JOA_TOT_PROJ'] / (ROA_NG['VL_TOT_PROJ'] - ROA_NG['VL_JOA_TOT_PROJ'] - ROA_NG['VL_OUT_TOT_PROJ']))
                    ROA_NG['REL_JOA'] = (np.where(ROA_NG['Pct_JOA_TI'].notnull() & (ROA_NG['Pct_JOA_TI'] !=0),
                                                        ROA_NG['Pct_JOA_PROJ'].fillna(1) / ROA_NG['Pct_JOA_TI'].fillna(1),
                                                        np.where(ROA_NG['Pct_JOA_PROJ'].notnull() & (ROA_NG['Pct_JOA_PROJ'] !=0),
                                                        0,
                                                        1)))

                    ROA_NG["Pct_COM_UC"] = np.where(ROA_NG['VL_UC_TOT_TI'] != 0,
                                                    ROA_NG["VL_COM_TOT_TI"] / ROA_NG["VL_UC_TOT_TI"],
                                                    0)
                    ROA_NG["Pct_MOP_ST"] = (ROA_NG["VL_MOP_TOT_TI"] + ROA_NG["VL_ST_TOT_TI"]) / (ROA_NG["VL_UC_TOT_TI"] +  ROA_NG["VL_COM_TOT_TI"])

                    ROA_NG["FLG_sem_uc"] = ROA_NG["VL_UC_TOT_TI"].abs() <= 0.01
                    ROA_NG["FLG_sem_com"] = ROA_NG["VL_COM_TOT_TI"].abs() <= 0.01
                    ROA_NG["FLG_sem_ca"] = (ROA_NG["VL_MOP_TOT_TI"] + ROA_NG["VL_ST_TOT_TI"]).abs() <= 0.01
                    ROA_NG["FLG_COM_alto"] = ROA_NG["Pct_COM_UC"] > 0.40
                    ROA_NG["FLG_CA_alto"] = ROA_NG["Pct_MOP_ST"] > 0.60
                    ROA_NG["FLG_COM_baixo"] = (ROA_NG["Pct_COM_UC"] < 0.05) & (ROA_NG["Pct_COM_UC"] > 0.01)
                    ROA_NG["FLG_CA_baixo"] = (ROA_NG["Pct_MOP_ST"] < 0.10) & (ROA_NG["Pct_MOP_ST"] > 0.01)

                    SQLq = f"""
                                        SELECT 
                                            *
                                        FROM 
                                            ROS t1 
                                        WHERE 
                                            t1.dt_ARQ = ?
                                        GROUP BY
                                            t1.Cd_SubODI
                                    """
                    ROS = sql.imp_tbl_forma_001('ROS', SQLq = SQLq, con = bd, st=st, Empresa=empresa)
                    ROA_NG['Cd_SubODI'] = ROA_NG['Cd_SubODI'].astype(str)
                    ROS['Cd_SubODI'] = ROS['Cd_SubODI'].astype(str)

                    ROA_NG = (ROA_NG.merge(ROS[['Cd_SubODI','Txt_Desc_PRJ','Pct_OE','Cd_Tipo_OE']], how = 'left', on = 'Cd_SubODI'))
                    ROA_NG["FLG_INC_DOA"] = ROA_NG["Cd_Tipo_OE"].astype(str).isin(['4','7'])
                    
                    base_cols = [
                                    "VL_UC_TOT_TI",
                                    "VL_COM_TOT_TI",
                                    "VL_MOP_TOT_TI",
                                    "VL_ST_TOT_TI",
                                    "VL_JOA_TOT_TI",
                                    "VL_TOT_TI"
                                ]

                    ROA_NG["log_valor"] = np.log10(ROA_NG["VL_TOT_PROJ"].clip(lower=0) + 1)
                    for col in base_cols[:-1]:
                        ROA_NG[f"Pct_{col}"] = np.where(
                                                            ROA_NG["VL_TOT_TI"] != 0, 
                                                            ROA_NG[col] / ROA_NG["VL_TOT_TI"],
                                                            0
                                                        )

                    caract = [
                                    "Pct_VL_UC_TOT_TI",
                                    "Pct_VL_COM_TOT_TI",
                                    "Pct_VL_MOP_TOT_TI",
                                    "Pct_VL_ST_TOT_TI",
                                    "Pct_VL_JOA_TOT_TI",
                                    "Pct_COM_UC",
                                    'Pct_MOP_ST',
                                    "REL_JOA",
                                    "log_valor"
                                ] + itens_ANL

                    
                    MIN_N_TI = 5         
                    K_MIN = 5
                    K_MAX = 20              
                    K_CAP = 8              
                    SAMPLE_FOR_K = 20000   
                    BATCH_SIZE = 10000    
                    RANDOM_STATE = 42

                    ROA_NG = ROA_NG.copy()
                    ROA_NG["cluster_ti"] = np.nan
                    ROA_NG["k_ti"] = np.nan
                    ROA_NG["ti_status"] = "NAO_PROCESSADO"

                    for ti, grupo in ROA_NG.groupby("Nr_TI", sort=False):
                        idx = grupo.index
                        n_ti = len(idx)

                        if n_ti < MIN_N_TI:
                            ROA_NG.loc[idx, "cluster_ti"] = -1
                            ROA_NG.loc[idx, "ti_status"] = f"SEM_MASSA(<{MIN_N_TI})"
                            continue

                        X_ti_df = ROA_NG.loc[idx, caract].replace([np.inf, -np.inf], np.nan)

                        imputer = SimpleImputer(strategy="median")
                        X_imp = imputer.fit_transform(X_ti_df)

                        var = X_imp.var(axis=0)
                        cols_ok = var > 0
                        if not np.all(cols_ok):
                            X_imp = X_imp[:, cols_ok]

                        if X_imp.shape[1] == 0:
                            ROA_NG.loc[idx, "cluster_ti"] = -1
                            ROA_NG.loc[idx, "ti_status"] = "SEM_VARIACAO"
                            continue
                        scaler = StandardScaler()
                        X_scaled = scaler.fit_transform(X_imp).astype("float32")

                        if n_ti > SAMPLE_FOR_K:
                            rng = np.random.default_rng(RANDOM_STATE)
                            samp = rng.choice(n_ti, size=SAMPLE_FOR_K, replace=False)
                            X_for_k = X_scaled[samp]
                        else:
                            X_for_k = X_scaled

                        k_max_eff = min(K_MAX, K_CAP, len(X_for_k) - 1)
                        if k_max_eff < K_MIN:
                            ROA_NG.loc[idx, "cluster_ti"] = -1
                            ROA_NG.loc[idx, "ti_status"] = "SEM_K_VALIDO"
                            continue

                        best_k = K_MIN
                        best_score = -1.0

                        for k in range(K_MIN, k_max_eff + 1):
                            km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
                            labels_k = km.fit_predict(X_for_k)

                            if len(np.unique(labels_k)) < 2:
                                score = -1.0
                            else:
                                score = silhouette_score(X_for_k, labels_k)

                            if score > best_score:
                                best_score = score
                                best_k = k

                        try:
                            if n_ti < 2000:
                                model = KMeans(n_clusters=best_k, random_state=RANDOM_STATE, n_init=10)
                            else:
                                model = MiniBatchKMeans(
                                                            n_clusters=best_k,
                                                            batch_size=min(BATCH_SIZE, n_ti),
                                                            random_state=RANDOM_STATE,
                                                        )

                            labels = model.fit_predict(X_scaled)

                            ROA_NG.loc[idx, "cluster_ti"] = labels
                            ROA_NG.loc[idx, "k_ti"] = best_k
                            ROA_NG.loc[idx, "ti_status"] = "OK"

                        except Exception as e:
                            ROA_NG.loc[idx, "cluster_ti"] = -1
                            ROA_NG.loc[idx, "k_ti"] = best_k
                            ROA_NG.loc[idx, "ti_status"] = f"ERRO:{type(e).__name__}"
                    
                    
                    benchmark = (
                                    ROA_NG.groupby(["Nr_TI","cluster_ti"])
                                    .agg(
                                        Pct_COM_med=("Pct_COM_UC", "mean"),
                                        Pct_COM_std=("Pct_COM_UC", "std"),
                                        Pct_CA_med=("Pct_MOP_ST", "mean"),
                                        Pct_CA_std=("Pct_MOP_ST", "std")
                                    )
                                )
                    
                    benchmark['Pct_COM_std'] = benchmark['Pct_COM_std'].fillna(0)
                    benchmark['Pct_CA_std'] = benchmark['Pct_CA_std'].fillna(0)

                    ROA_NG = ROA_NG.merge(benchmark, on=["Nr_TI","cluster_ti"], how="left")

                    ROA_NG['Pct_COM_med'] = ROA_NG['Pct_COM_med'].fillna(ROA_NG['Pct_COM_UC'])
                    ROA_NG['Pct_CA_med'] = ROA_NG['Pct_CA_med'].fillna(ROA_NG['Pct_MOP_ST'])
                    ROA_NG["z_COM_TI"] = (
                                            (ROA_NG["Pct_COM_UC"] - ROA_NG["Pct_COM_med"]) /
                                            ROA_NG["Pct_COM_std"]
                                         )

                    ROA_NG["z_CA_TI"] = (
                                            (ROA_NG["Pct_MOP_ST"] - ROA_NG["Pct_CA_med"]) /
                                            ROA_NG["Pct_CA_std"]
                                        )

                    ROA_NG["FLG_outlier_COM"] = ROA_NG["z_COM_TI"].abs() > 3
                    ROA_NG["FLG_outlier_CA"] = ROA_NG["z_CA_TI"].abs() > 3

                    ROA_NG["FLG_JOA_distorcido"] = (ROA_NG["REL_JOA"] - 1).abs() > 0.01 
                                
                    ROA_NG["COM_faixa_inf"] = ROA_NG["Pct_COM_med"] - ROA_NG["Pct_COM_std"]
                    ROA_NG["COM_faixa_sup"] = ROA_NG["Pct_COM_med"] + ROA_NG["Pct_COM_std"]

                    ROA_NG["CA_faixa_inf"] = ROA_NG["Pct_CA_med"] - ROA_NG["Pct_CA_std"]
                    ROA_NG["CA_faixa_sup"] = ROA_NG["Pct_CA_med"] + ROA_NG["Pct_CA_std"]

                    ROA_NG["FLG_COM_fora_faixa"] = (
                                                        (ROA_NG["Pct_COM_UC"] < ROA_NG["COM_faixa_inf"]) |
                                                        (ROA_NG["Pct_COM_UC"] > ROA_NG["COM_faixa_sup"])
                                                    )

                    ROA_NG["FLG_CA_fora_faixa"] = (
                                                        (ROA_NG["Pct_MOP_ST"] < ROA_NG["CA_faixa_inf"]) |
                                                        (ROA_NG["Pct_MOP_ST"] > ROA_NG["CA_faixa_sup"])
                                                    )

                    
                    ROA_NG["anomalia"] = np.nan
                    ROA_NG["score_iso"] = np.nan
                    ROA_NG["iso_status"] = "NAO_PROCESSADO"

                    for (ti, cluster), grupo in ROA_NG.groupby(["Nr_TI", "cluster_ti"]):
                        idx = grupo.index
                        n = len(idx)
                        if n < 15:
                            ROA_NG.loc[idx, "iso_status"] = f"SEM_MASSA_CLUSTER({n})"
                            ROA_NG.loc[idx, "anomalia"] = np.nan
                            continue

                        X_cluster = (
                                        ROA_NG.loc[idx, caract]
                                        .replace([np.inf, -np.inf], np.nan)
                                    )

                        imputer = SimpleImputer(strategy="median")
                        X_imp = imputer.fit_transform(X_cluster)

                        var = X_imp.var(axis=0)
                        cols_ok = var > 0
                        X_imp = X_imp[:, cols_ok]

                        if X_imp.shape[1] == 0:
                            ROA_NG.loc[idx, "iso_status"] = "SEM_VARIACAO"
                            continue

                        scaler = StandardScaler()
                        X_scaled = scaler.fit_transform(X_imp).astype("float32")

                        try:
                            iso = IsolationForest(
                                                    contamination=0.02,
                                                    random_state=42,
                                                    n_jobs=-1
                                                )

                            pred = iso.fit_predict(X_scaled)
                            score = iso.decision_function(X_scaled)

                            ROA_NG.loc[idx, "anomalia"] = pred
                            ROA_NG.loc[idx, "score_iso"] = score
                            ROA_NG.loc[idx, "iso_status"] = "OK"

                        except Exception as e:
                            ROA_NG.loc[idx, "iso_status"] = f"ERRO:{type(e).__name__}"
                    
                    ROA_NG["ML_intensidade"] = np.where(
                                                            ROA_NG["anomalia"] == -1,
                                                            np.clip(-ROA_NG["score_iso"], 0, 1),
                                                            0
                                                        )

                    # Avaliação da estrutura do CA:
                    t1 = 0.25
                    t2 = 0.20
                    desvio_t1 = ROA_NG['Pct_TESTE01'] > t1
                    desvio_t2 = ROA_NG['Pct_TESTE02'] > t2
                    
                    ROA_NG['OBS_MO'] = np.select(
                                    [
                                        ~desvio_t1 & ~desvio_t2,
                                        desvio_t1 & ~desvio_t2,
                                        ~desvio_t1 & desvio_t2,
                                        desvio_t1 & desvio_t2,
                                    ],
                                    [
                                        f'OK - aderente à premissa de obra com método de alocação direto (CA indireto abaixo de {t1:,.0%} do projeto e CA indireto abaixo de {t2:,.0%} do CA)',
                                        f'Avaliar - custos indiretos de mão de obra acima de {t1:,.0%} dos custos diretos da obra',
                                        f'Avaliar - custos indiretos de mão de obra acima do limite esperado, {t2:,.0%}, em relação à mão de obra total',
                                        f'Avaliar - desvio nos testes de custos indiretos de mão de obra sobre diretos da obra, {t1:,.0%}, e sobre mão de obra total, {t2:,.0%}',
                                    ],
                                    default=''
                                )
                    

                    ROA_NG["FLG_TESTE01"] = (
                                                (ROA_NG["Pct_TESTE01"] > t1) | ROA_NG["Pct_TESTE01"].isna()
                                            ).astype(int)

                    ROA_NG["FLG_TESTE02"] = (
                                                (ROA_NG["Pct_TESTE02"] >= t2) | ROA_NG["Pct_TESTE02"].isna()
                                            ).astype(int)
                    ROA_NG["FLG_TESTE_AMBOS"] = (
                                                    (ROA_NG["FLG_TESTE01"] == 1) & (ROA_NG["FLG_TESTE02"] == 1)
                                                ).astype(int)
                    
                    ROA_NG["FLG_TI"] = ROA_NG["Nr_TI"].astype(str).isin(['70','71','72','80','81','82','90','91','94','95','99'])
                    ROA_NG["valor_anomalia"] = (
                                                    ROA_NG["FLG_sem_uc"] * 1
                                                    + ROA_NG["FLG_sem_com"] * 5
                                                    + ROA_NG["FLG_sem_ca"] * 5
                                                    + ROA_NG["FLG_outlier_COM"] * 2
                                                    + ROA_NG["FLG_outlier_CA"] * 2
                                                    + ROA_NG["FLG_JOA_distorcido"] * 3
                                                    + ROA_NG["ML_intensidade"] * 3
                                                    + ROA_NG["log_valor"] * 0.1
                                                    + ROA_NG["FLG_TESTE01"] * 3
                                                    + ROA_NG["FLG_TESTE02"] * 3
                                                    + ROA_NG["FLG_TESTE_AMBOS"] * 3

                                                ) * (1- ROA_NG["FLG_INC_DOA"]) * (1 - ROA_NG["FLG_TI"])
                    

                    ROA_NG["risco"] = np.select(
                                                    [
                                                        ROA_NG["valor_anomalia"] >= 15,
                                                        ROA_NG["valor_anomalia"] >= 5
                                                    ],
                                                    [
                                                        "ALTO_RISCO",
                                                        "MEDIO_RISCO"
                                                    ],
                                                    default="BAIXO_RISCO"
                                                )

                    ROA_NG["motivo_sem_uc"] = np.where(ROA_NG["FLG_sem_uc"] & (~ROA_NG["FLG_INC_DOA"]) & (~ROA_NG["FLG_TI"]), "Sem UC; ", "")
                    ROA_NG["motivo_indireto"] = np.where(ROA_NG["FLG_TESTE01"] & (~ROA_NG["FLG_INC_DOA"]) & (~ROA_NG["FLG_TI"]), "Mão de obra indireta alta no custo da obra; ", "")
                    ROA_NG["motivo_indireto_mo"] = np.where(ROA_NG["FLG_TESTE02"] & (~ROA_NG["FLG_INC_DOA"]) & (~ROA_NG["FLG_TI"]), "Mão de obra indireta alta na mão de obra; ", "")
                    ROA_NG["motivo_sem_com"] = np.where(ROA_NG["FLG_sem_com"] & (~ROA_NG["FLG_INC_DOA"]) & (~ROA_NG["FLG_TI"]), "Sem COM; ", "")
                    ROA_NG["motivo_sem_ca"] = np.where(ROA_NG["FLG_sem_ca"] & (~ROA_NG["FLG_INC_DOA"]) & (~ROA_NG["FLG_TI"]), "Sem CA; ", "")
                    ROA_NG["motivo_COM_alto"] = np.where(ROA_NG["FLG_COM_alto"] & (~ROA_NG["FLG_INC_DOA"]) & (~ROA_NG["FLG_TI"]), "COM alto; ", "")
                    ROA_NG["motivo_CA_alto"] = np.where(ROA_NG["FLG_CA_alto"] & (~ROA_NG["FLG_INC_DOA"]) & (~ROA_NG["FLG_TI"]), "CA alto; ", "")
                    ROA_NG["motivo_COM_baixo"] = np.where(ROA_NG["FLG_COM_baixo"] & (~ROA_NG["FLG_INC_DOA"]) & (~ROA_NG["FLG_TI"]), "COM baixo; ", "")
                    ROA_NG["motivo_CA_baixo"] = np.where(ROA_NG["FLG_CA_baixo"] & (~ROA_NG["FLG_INC_DOA"]) & (~ROA_NG["FLG_TI"]), "CA baixo; ", "")
                    ROA_NG["motivo_outlier_COM"] = np.where(ROA_NG["FLG_outlier_COM"] & (~ROA_NG["FLG_INC_DOA"]) & (~ROA_NG["FLG_TI"]), "Outlier COM; ", "")
                    ROA_NG["motivo_outlier_CA"] = np.where(ROA_NG["FLG_outlier_CA"] & (~ROA_NG["FLG_INC_DOA"]) & (~ROA_NG["FLG_TI"]), "Outlier CA; ", "")
                    ROA_NG["motivo_JOA"] = np.where(ROA_NG["FLG_JOA_distorcido"] & (~ROA_NG["FLG_INC_DOA"]) & (~ROA_NG["FLG_TI"]), "JOA distorcido; ", "")
                    ROA_NG["motivo_ML"] = np.where((ROA_NG["anomalia"] == -1) & (~ROA_NG["FLG_INC_DOA"]) & (~ROA_NG["FLG_TI"]), "Anomalia ML; ", "")

                    ROA_NG["motivo_risco"] = (
                                                    ROA_NG["motivo_sem_uc"]
                                                    + ROA_NG["motivo_sem_com"]
                                                    + ROA_NG["motivo_sem_ca"]
                                                    + ROA_NG["motivo_COM_alto"]
                                                    + ROA_NG["motivo_CA_alto"]
                                                    + ROA_NG["motivo_COM_baixo"]
                                                    + ROA_NG["motivo_CA_baixo"]
                                                    + ROA_NG["motivo_outlier_COM"]
                                                    + ROA_NG["motivo_outlier_CA"]
                                                    + ROA_NG["motivo_JOA"]
                                                    + ROA_NG["motivo_ML"]
                                                    + ROA_NG["motivo_indireto"]
                                                    + ROA_NG["motivo_indireto_mo"]
                                                )
                    ROA_NG["motivo_risco"] = (
                                                ROA_NG["motivo_risco"]
                                                .str.rstrip("; ")
                                                .replace("", "Sem desvios relevantes (incorporação/doação ou TI associada a BAR)")
                                            )
                    cols_motivo_aux = [
                                            "motivo_sem_uc",
                                            "motivo_sem_com",
                                            "motivo_sem_ca",
                                            "motivo_COM_alto",
                                            "motivo_CA_alto",
                                            "motivo_COM_baixo",
                                            "motivo_CA_baixo",
                                            "motivo_outlier_COM",
                                            "motivo_outlier_CA",
                                            "motivo_JOA",
                                            "motivo_ML",
                                            "motivo_indireto",
                                            "motivo_indireto_mo"
                                        ]

                    ROA_NG.drop(columns=cols_motivo_aux, inplace=True, errors="ignore")
                    ROA_NG.to_sql('TST_ABERTURA_PROJETOS_TI', bd, if_exists='replace', index=False)
                    
            else:
                ROA_NG = sql.carga_sqlite_cache("SELECT * FROM TST_ABERTURA_PROJETOS_TI", bd)

            if not html_config:
                return
            st.html(""" <h2>Análise da estrutura de custos do ROA</h2>
                        <div style="
                            padding:12px 14px;
                            border-radius:10px;
                            background:rgba(17,17,17,0.05);
                            border:1px solid rgba(0,0,0,0.08);
                            margin-bottom:12px;
                            line-height:1.45;
                        ">
                        <p  style="text-align: justify;text-indent: 40px">Os gráficos a seguir apresentam o perfil de custo dos projetos na tipologia selecionada (Nr_TI).
                        O <b>eixo X</b> representa o percentual de <b>Componentes Menores (COM)</b> em relação ao total do projeto,
                        enquanto o <b>eixo Y</b> mostra o percentual de <b>CA</b>, calculado como a soma de <b>Serviços de Terceiros (ST)</b>
                        e <b>Mão de Obra Própria (MOP)</b>.  

                        Cada ponto corresponde a um projeto. As <b>cores</b> indicam os <b>clusters</b> (grupos com composições semelhantes),
                        e os projetos identificados como <b>outliers</b> pelo modelo de anomalia são destacados visualmente. Ainda, a análise da 
                        distribuição dos custos revela padrões distintos: projetos com alta participação de UC/UAR (acima de 50%) e baixo percentual 
                        de componentes menores (abaixo de 15%) caracterizam empreendimentos como subestações e sistemas de controle, onde o valor 
                        concentra-se em equipamentos especializados, transformadores e sistemas de proteção. Por outro lado, projetos com menor CA 
                        (abaixo de 50%) e maior participação de materiais menores (acima de 25%) tipicamente representam obras de redes de distribuição; 
                        já para linhas espera-se CA maior. Sistemas de medição, dependendo do tipo podem variar. Consideraremos quadrantes de referência 
                        em 50% de CA e 20% de compomentes menores. 
                        </p>

                        </div>
                        """)
            
            df = ROA_NG.copy()
            df['Pct_CA'] = df["Pct_VL_ST_TOT_TI"] + df["Pct_VL_JOA_TOT_TI"]
            
            plt.style.use("default")
            COR_OK = "#2eee34"
            COR_WARN = "#fcc72a"
            COR_CRIT = "#b60101"

            for ti in df["Nr_TI"].drop_duplicates().sort_values().to_list():
                df_ti = df[df["Nr_TI"] == ti]

                max_x = df_ti["Pct_VL_COM_TOT_TI"].max()
                max_y = df_ti["Pct_CA"].max()

                if str(ti) in ['30','31','32','33','34']:
                    COMpct = 0.05
                    CApct = 0.40
                elif str(ti) in ['35','36','37','38','39']:
                    COMpct = 0.10
                    CApct = 1.40
                elif str(ti) in ['50','51','52','53','54']:
                    COMpct = 0.05
                    CApct = 0.40
                elif str(ti) in ['55','56','57','58','59']:
                    COMpct = 0.10
                    CApct = 1.40
                elif str(ti) in ['40']:
                    COMpct = 0.25
                    CApct = 0.65
                elif str(ti) in ['41']:
                    COMpct = 0.25
                    CApct = 0.60
                elif str(ti) in ['42']:
                    COMpct = 0.10
                    CApct = 0.65
                elif str(ti) in ['65','66','67','68','69']:
                    COMpct = 0.10
                    CApct = 0.75
                elif str(ti) in ['93']:
                    COMpct = 0.10
                    CApct = 0.30
                elif str(ti) in ['96']:
                    COMpct = 0.10
                    CApct = 0.35
                elif str(ti) in ['98','99']:
                    COMpct = 0.00
                    CApct = 0.05 
                else:
                    COMpct = 0.20
                    CApct = 0.50   

                fig, ax = plt.subplots()
                ax.set_facecolor("#f7f7f7")
                fig.patch.set_facecolor("white")


                ax.axhline(y=CApct, color='black', linestyle=':', linewidth=1)
                ax.axvline(x=COMpct, color='black', linestyle=':', linewidth=1)
                ax.scatter(
                                df_ti["Pct_VL_COM_TOT_TI"],
                                df_ti["Pct_CA"],
                                c=df_ti["cluster_ti"],  
                                cmap="tab10",
                                s=28,
                                alpha=0.55,
                                edgecolors="none"
                            )
                
                outliers = df_ti[df_ti["anomalia"] == -1]

                ax.scatter(
                            outliers["Pct_VL_COM_TOT_TI"],
                            outliers["Pct_CA"],
                            color="#d2cece",
                            marker="x",
                            s=45,
                            linewidths=1.2,
                            label="Outliers"
                        )

                centroides = df_ti.groupby("cluster_ti").agg(
                                                                COM=("Pct_VL_COM_TOT_TI","mean"),
                                                                CA=("Pct_CA","mean")
                                                            )

                ax.scatter( centroides["COM"], centroides["CA"], 
                            s=90,
                            color="#f2f628",
                            label="Centróides")
                ax.grid(True, linestyle="--", linewidth=0.4, alpha=0.25)
                ax.set_title(f"TI {ti}", fontsize=11)
                ax.set_xlabel("Percentual de Componentes Menores (COM) — % do UC/UAR", fontsize=9)
                ax.set_ylabel("Percentual de CA (ST + MOP) — % do (UC/UAR + COM)", fontsize=9)
                ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'{x:,.2%}'.replace(".",",")))
                ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'{x:,.2%}'.replace(".",",")))
                ax.tick_params(axis='both', labelsize=8)
                ax.set_xlim(0, max_x)
                ax.set_ylim(0, max_y)
                
                x_min, x_max = 0, max_x
                y_min, y_max = 0, max_y

                x_ref = COMpct
                y_ref = CApct

                ax.legend(frameon=False, fontsize=8, loc="upper right")

                def nota_quadrante(ax, x, y, nota):
                    ax.text(
                                x, y, nota,
                                fontsize=9,
                                ha='center',
                                va='center'
                            )

                tem_esq = x_min < x_ref
                tem_dir = x_max > x_ref
                tem_inf = y_min < y_ref
                tem_sup = y_max > y_ref

                x_esq = (x_min + min(x_ref, x_max)) / 2 if tem_esq else None
                x_dir = (max(x_ref, x_min) + x_max) / 2 if tem_dir else None
                y_inf = (y_min + min(y_ref, y_max)) / 2 if tem_inf else None
                y_top = (max(y_ref, y_min) + y_max) / 2 if tem_sup else None

                if tem_dir and tem_sup:
                    nota_quadrante(ax, x_dir, y_top, 'Q1')

                if tem_dir and tem_inf:
                    nota_quadrante(ax, x_dir, y_inf, 'Q2')

                if tem_esq and tem_inf:
                    nota_quadrante(ax, x_esq, y_inf, 'Q3')

                if tem_esq and tem_sup:
                    nota_quadrante(ax, x_esq, y_top, 'Q4')

                dic_plt = {
                                'Q1': 'CA e COM intensivo   ',
                                'Q3': 'CA e COM moderados',
                                'Q2': 'COM intensivo           ',
                                'Q4': 'CA intensivo               '
                            }
                texto_legenda = " \n".join([f"{k} = {v}" for k, v in dic_plt.items()])
                plt.text(0.5, -0.30, texto_legenda, 
                        transform=ax.transAxes, 
                        ha="center", 
                        fontsize=8, 
                        bbox=dict(boxstyle="round", facecolor="#dfedd9", alpha=0.5))
                

                fig1, ax1 = plt.subplots()
                ax1.set_facecolor("#f7f7f7")
                fig1.patch.set_facecolor("white")


                ax1.axhline(y=CApct, color='black', linestyle=':', linewidth=1)
                ax1.axvline(x=COMpct, color='black', linestyle=':', linewidth=1)
                ax1.scatter(
                                df_ti["Pct_VL_COM_TOT_TI"],
                                df_ti["Pct_CA"],
                                c=df_ti["cluster_ti"],  
                                cmap="tab10",
                                s=28,
                                alpha=0.55,
                                edgecolors="none"
                            )
                
                ax1.grid(True, linestyle="--", linewidth=0.4, alpha=0.25)
                ax1.set_title(f"TI {ti}", fontsize=11)
                ax1.set_xlabel("Percentual de Componentes Menores (COM) — % do UC/UAR", fontsize=9)
                ax1.set_ylabel("Percentual de CA (ST + MOP) — % do (UC/UAR + COM)", fontsize=9)
                ax1.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'{x:,.2%}'.replace(".",",")))
                ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'{x:,.2%}'.replace(".",",")))
                ax1.tick_params(axis='both', labelsize=8)
                ax1.set_xlim(0, max_x)
                ax1.set_ylim(0, max_y)
                
                x_min, x_max = 0, max_x
                y_min, y_max = 0, max_y

                x_ref = COMpct
                y_ref = CApct

                ax1.legend(frameon=False, fontsize=8, loc="upper right")

                tem_esq = x_min < x_ref
                tem_dir = x_max > x_ref
                tem_inf = y_min < y_ref
                tem_sup = y_max > y_ref

                x_esq = (x_min + min(x_ref, x_max)) / 2 if tem_esq else None
                x_dir = (max(x_ref, x_min) + x_max) / 2 if tem_dir else None
                y_inf = (y_min + min(y_ref, y_max)) / 2 if tem_inf else None
                y_top = (max(y_ref, y_min) + y_max) / 2 if tem_sup else None

                if tem_dir and tem_sup:
                    nota_quadrante(ax1, x_dir, y_top, 'Q1')

                if tem_dir and tem_inf:
                    nota_quadrante(ax1, x_dir, y_inf, 'Q2')

                if tem_esq and tem_inf:
                    nota_quadrante(ax1, x_esq, y_inf, 'Q3')

                if tem_esq and tem_sup:
                    nota_quadrante(ax1, x_esq, y_top, 'Q4')

                dic_plt = {
                                'Q1': 'CA e COM intensivo   ',
                                'Q3': 'CA e COM moderados',
                                'Q2': 'COM intensivo           ',
                                'Q4': 'CA intensivo               '
                            }
                texto_legenda = " \n".join([f"{k} = {v}" for k, v in dic_plt.items()])
                plt.text(0.5, -0.30, texto_legenda, 
                        transform=ax1.transAxes, 
                        ha="center", 
                        fontsize=8, 
                        bbox=dict(boxstyle="round", facecolor="#dfedd9", alpha=0.5))


                col = st.columns([4,1,4], gap='large')
                with col[0]:
                    st.pyplot(fig)
                    plt.savefig(f"{local}//RELATORIOS//figuras//cluster_TI_{ti}_{empresa}.png", dpi=300, bbox_inches='tight')
                    plt.close(fig)
                with col[2]:
                    st.pyplot(fig1)
                    plt.savefig(f"{local}//RELATORIOS//figuras//cluster_TI_{ti}_{empresa}_limpo.png", dpi=300, bbox_inches='tight')
                    plt.close(fig1)

            _vis_001(ROA_NG, st, COR_OK, COR_WARN, COR_CRIT)

        arq_voc_aberto = os.path.join(
                                        st.session_state.tra_dir,
                                        "INC_ANLS",
                                        f"VOC_ABERTO.csv"
                                    )

        if not anl_inv:
            SQLq = f"""
                        SELECT 
                            Id_SEQ_INC,
                            Cd_CC,Cd_ODI,
                            Cd_SubODI,
                            Nr_TI,
                            Nr_CM,
                            Nr_TUC,
                            Nr_A1,
                            Nr_A2,
                            Nr_A3,
                            Nr_A4,
                            Nr_A5,
                            Nr_A6,
                            Cd_UAR,
                            Cd_UC,
                            Cd_Patrim,
                            Cd_DIG_INC,
                            COD_ITEM,
                            Qtd_AIS,
                            Cd_UND_AIS,
                            VL_VOC,
                            Dt_Imob,
                            Dt_CNTB_AJST,
                            VL_DEP_ACUM,
                            VL_VOC_VF,
                            VL_VOC_COM,
                            VL_VOC_CA,
                            VL_VOC_JOA,
                            VL_VOC_VF_AVAL,
                            VL_VOC_COM_AVAL,
                            VL_VOC_CA_AVAL,
                            VL_VOC_JOA_AVAL,
                            FLG_DOA_OE,
                            FLG_INCOR_OE,
                            FLG_PLPT_OE,
                            FLG_REG,
                            FLG_ELIG,
                            Cd_CONC,
                            Cd_TP_AVAL
                        FROM 
                            INCR t1 
                        WHERE 
                            t1.dt_ARQ = ?
                    """
            INCR = sql.imp_tbl_forma_001('INCR', SQLq = SQLq, con = bd, st=st, Empresa=empresa)
                
            for nm in ['Qtd_AIS','VL_VOC','VL_DEP_ACUM','VL_VOC_VF','VL_VOC_COM','VL_VOC_CA','VL_VOC_JOA','VL_VOC_VF_AVAL',
                    'VL_VOC_COM_AVAL','VL_VOC_CA_AVAL','VL_VOC_JOA_AVAL','VL_VNR_UC','VL_IAI_UC','VL_DAC_UC','VL_VMU_UC',
                    'VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC','Pct_IA','VL_VNR_VF_UNIT','VL_VNR_COM_UNIT','VL_VNR_CA_UNIT',
                    'VL_VNR_JOA']:
                if (nm in INCR.columns) and (INCR[nm].dtype == 'object'):
                    INCR[nm] = pd.to_numeric(INCR[nm].astype(str).str.replace(',','.'), 
                                                                errors='coerce',
                                                                downcast='float')
        elif os.path.exists(arq_voc_aberto):
            df_VOC_ABT = pd.read_csv(arq_voc_aberto, sep="|", dtype=str, encoding="latin-1")
            lst_col = [ f"{nm}" for nm in df_VOC_ABT.columns]
            df_VOC_ABT.columns = ['Ide_ABT_VOC'] + lst_col[1:]

            nm_col = [ix for ix in df_VOC_ABT.columns if ix.upper()[:6]== f"VL"]
            for nm in nm_col:
                if df_VOC_ABT[nm].dtype == 'object':
                    df_VOC_ABT[nm] = (df_VOC_ABT[nm]
                                        .str.replace(",", "x", regex=False)
                                        .str.replace(".", "", regex=False)
                                        .str.replace("x", ".", regex=False))
                    df_VOC_ABT[nm] = pd.to_numeric(df_VOC_ABT[nm], errors='coerce')
            st.write(df_VOC_ABT)
            raise
        else:
            st.warning("Sem dados para análise")
            cols3a = st.columns([3,1,3,1,3], gap='small')
            with cols3a[1]:
                impr1 = st.button("Imprimir F0")
            if impr1:
                imprimi_F0_ABT(f'{local}\AIS_ANLS', bd, empresa, st=st)

            return
        if not sql.existe_tabela("TST_VL_VF_TAB_ROA", bd) or refazer:
            SQLq = f"""
                        SELECT 
                            t1.Cd_SubODI, 
                            t1.COD_ITEM,
                            t1.Nr_TI,
                            t1.Nr_TUC,
                            t1.Nr_A1,
                            t1.Nr_A2,
                            t1.Nr_A3,
                            t1.Nr_A4,
                            t1.Nr_A5,
                            t1.Nr_A6,
                            t1.Unidade AS Cd_UND_AIS,
                            t1.Dt_Lcmto,
                            SUM(
                                CASE 
                                    WHEN Qtd LIKE '%,%' THEN CAST(REPLACE(Qtd, ',', '.') AS REAL)
                                    ELSE CAST(Qtd AS REAL)
                                END
                            ) AS Qtd_ROA, 
                            SUM(
                                CASE 
                                    WHEN VL_tot LIKE '%,%' THEN CAST(REPLACE(VL_tot, ',', '.') AS REAL)
                                    ELSE CAST(VL_tot AS REAL)
                                END
                            ) AS VL_tot,
                            SUM(CASE WHEN VL_tot LIKE '%,%' THEN CAST(REPLACE(VL_tot, ',', '.') AS REAL) ELSE CAST(VL_tot AS REAL) END) / 
                            NULLIF(SUM(CASE WHEN Qtd LIKE '%,%' THEN CAST(REPLACE(Qtd, ',', '.') AS REAL) ELSE CAST(Qtd AS REAL) END), 0) AS VL_CMU

                        FROM 
                            ROA t1 
                        WHERE 
                            dt_ARQ = ? AND t1.Cd_NG = '1'
                        GROUP BY 
                            t1.Cd_SubODI, 
                            t1.COD_ITEM,
                            t1.Nr_TI,
                            t1.Nr_TUC,
                            t1.Nr_A1,
                            t1.Nr_A2,
                            t1.Nr_A3,
                            t1.Nr_A4,
                            t1.Nr_A5,
                            t1.Nr_A6,
                            t1.Unidade,
                            t1.Dt_Lcmto;
                    """
            df_VL_VF_ROA = sql.imp_tbl_forma_001('ROA', SQLq = SQLq, con = bd, st=st, Empresa=empresa)
            df_VL_VF_ROA.to_sql('TST_VL_VF_TAB_ROA', bd, if_exists='replace', index=False)
        else:
            SQLq = f"""
                        SELECT 
                            *
                        FROM 
                            TST_VL_VF_TAB_ROA
                    """
            
            df_VL_VF_ROA = sql.carga_sqlite_cache(SQLq, bd)

        df_VL_VF_ROA['Dt_Lcmto'] = pd.to_datetime(df_VL_VF_ROA['Dt_Lcmto'])
        df_VL_VF_ROA['OBS_SFF'] = 'NO'
        df_VL_VF_ROA.loc[(df_VL_VF_ROA['Qtd_ROA'].abs() <= 1e-3) &
                        (df_VL_VF_ROA['VL_tot'].abs() >= 1e-3), 'OBS_SFF'] = 'Verifique Quantidade'
        
        def conc_VF(df_VL_VF_ROA, INCR, chave = ['Cd_SubODI','COD_ITEM'], sufixos = ("", "_ROA")):
            VL_VF_ROA = (df_VL_VF_ROA[df_VL_VF_ROA['OBS_SFF'] == 'NO']
                    .groupby(by=chave)
                    .agg(
                    VL_CMU_MAX = ('VL_CMU', 'max'),
                    VL_CMU_MIN=('VL_CMU', 'min'),
                    VL_CMU_MEDIA=('VL_CMU', 'mean'),
                    VL_SOMA=('VL_tot', 'sum'),
                    VL_CMU_DP=('VL_CMU', 'std'),
                    QTD_OCOR=('VL_CMU', 'count'),
                    QTD_SOMA=('Qtd_ROA', 'sum'),
                        )
                    .reset_index()
                    .fillna(0))
            
            VL_VF_ROA['VL_CMU_CV'] = (np.where(VL_VF_ROA['VL_CMU_MEDIA'] != 0,
                                            VL_VF_ROA['VL_CMU_DP'] / VL_VF_ROA['VL_CMU_MEDIA'],
                                            0)).round(4)
            VL_VF_ROA['VL_UNT'] = VL_VF_ROA['VL_CMU_MEDIA'].round(2)
            VL_VF_ROA['VL_UNT_MAX'] = (VL_VF_ROA['VL_UNT'] + 2 * VL_VF_ROA['VL_CMU_DP']).round(2)
            VL_VF_ROA['VL_UNT_MIN'] = (VL_VF_ROA['VL_UNT'] - 2 * VL_VF_ROA['VL_CMU_DP']).round(2).clip(lower=0)
                    
            crit = VL_VF_ROA['VL_SOMA'] <= 0
            VL_VF_ROA.loc[crit, ['VL_UNT', 'VL_UNT_MAX', 'VL_UNT_MIN']] = 0
                                
            VL_VF_ROA['OBS_SFF_VF_ROA'] = 'NO'
            VL_VF_ROA.loc[VL_VF_ROA['VL_SOMA'] == 0, 'OBS_SFF_VF_ROA'] = "Ativo estornado"
            VL_VF_ROA.loc[(VL_VF_ROA['VL_SOMA'] < 0) &
                        (VL_VF_ROA['OBS_SFF_VF_ROA'] == 'NO'), 'OBS_SFF_VF_ROA'] = "Verificar diferença do estorno em relação ao lançamento"
            VL_VF_ROA.loc[(VL_VF_ROA['QTD_SOMA'].abs() <= 1e-3) &
                            (VL_VF_ROA['VL_SOMA'].abs() >= 1e-3) &
                        (VL_VF_ROA['OBS_SFF_VF_ROA'] == 'NO'), 'OBS_SFF_VF_ROA'] = 'Verifique Quantidade'
            VL_VF_ROA.loc[(VL_VF_ROA['QTD_SOMA'].abs() >= 1e-3) &
                            (VL_VF_ROA['VL_SOMA'].abs() <= 1e-3) &
                        (VL_VF_ROA['OBS_SFF_VF_ROA'] == 'NO'), 'OBS_SFF_VF_ROA'] = 'Verifique Quantidade'
            VL_VF_ROA.loc[(VL_VF_ROA['VL_CMU_CV'].abs() > 0.4) &
                        (VL_VF_ROA['OBS_SFF_VF_ROA'] == 'NO'), 'OBS_SFF_VF_ROA'] = 'Por que valor médio unitário varia tanto?'

            INCR = INCR.merge(VL_VF_ROA, how='left', on = chave, suffixes=sufixos)
            return INCR
        
        INCR1 = conc_VF(df_VL_VF_ROA, INCR, chave = ['Cd_SubODI','COD_ITEM'], sufixos = ("", "_ROA"))
        crit = INCR1['OBS_SFF_VF_ROA'].isnull()
        INCR1 = INCR1[~crit].copy()
        INCR1['TIPO_CONC'] = 'COD_ITEM'

        INCR2 = conc_VF(df_VL_VF_ROA, INCR[crit], chave = ['Cd_SubODI','Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                    'Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_UND_AIS'], sufixos = ("_COD_ITEM", "_TI"))
        crit = INCR2['OBS_SFF_VF_ROA'].isnull()
        INCR3 = INCR2[crit].copy()
        INCR2 = INCR2[~crit].copy()
        INCR2['TIPO_CONC'] = 'TUCAGEM'
        INCR3['TIPO_CONC'] = 'NÃO CONCILIADO'

        INCRanl = pd.concat([INCR1, INCR2, INCR3], ignore_index=True)
        lst_stm = ['100', '105', '110', '112', '115', '140', '145', '150', '155', '170', '175', '185', '205', '215', '220', '225', '240', '245', '260', 
                '275', '280', '285', '300', '320', '335', '350', '355', '360', '365', '370', '375', '380', '385', '390', '395', '400', '405', '410', 
                '415', '420', '425', '430', '435', '440', '445', '450', '455', '460', '465', '470', '475', '480', '485', '490', '500', '505', '510', 
                '515', '520', '525', '530', '550', '555', '585', '590', '595', '600', '610']

        INCRanl['FLG_STM'] = INCRanl['Nr_TUC'].isin(lst_stm)
        tol = 0.01
        INCRanl['FLG_RNG'] = (
                                np.where((INCRanl['VL_VOC_VF_AVAL'] >= (INCRanl['VL_UNT_MIN'] * INCRanl['QTD_SOMA'] - tol)) & 
                                        (INCRanl['VL_VOC_VF_AVAL'] <= (INCRanl['VL_UNT_MAX'] * INCRanl['QTD_SOMA'] + tol)), 
                                        True, 
                                        False)
                            )
        
        INCRanl['Pct_DESVIO'] = (
                                        np.where(INCRanl['FLG_RNG'], 
                                                0,
                                                np.where(INCRanl['VL_VOC_VF_AVAL'] !=0, 
                                                ((INCRanl['VL_VOC_VF_AVAL'] - INCRanl['VL_UNT'] * INCRanl['QTD_SOMA']) / INCRanl['VL_VOC_VF_AVAL']).round(5),
                                                (INCRanl['VL_VOC_VF_AVAL'] - INCRanl['VL_UNT'] * INCRanl['QTD_SOMA']).round(5)
                                                ))
                                    )
        INCRanl.loc[INCRanl['Pct_DESVIO'] <= 0.001, 'Pct_DESVIO'] = 0
        INCRanl.loc[INCRanl['Pct_DESVIO'] <= 0.001, 'FLG_RNG'] = True

        cri1 = (~INCRanl['FLG_STM']) & (~INCRanl['FLG_RNG']) & INCRanl['Pct_DESVIO'].notnull() & (INCRanl['VL_CMU_DP']==0)
        cri2 = (~INCRanl['FLG_STM']) & (~INCRanl['FLG_RNG']) & INCRanl['Pct_DESVIO'].notnull() & (INCRanl['VL_CMU_DP']!=0)
        cri3 = INCRanl['VL_CMU_CV'] >= 0.3
        cri4 = INCRanl['TIPO_CONC'] == 'NÃO CONCILIADO'
        cri5 = ((INCRanl['FLG_DOA_OE']=='1') | (INCRanl['FLG_INCOR_OE']=='1')) 
        cri6 = (INCRanl['FLG_ELIG']=='0') | (INCRanl['Cd_CONC']=='2')

        INCRanl['OBS_SFF_VF'] = "NO"
        INCRanl.loc[cri6 & (INCRanl['OBS_SFF_VF'] == "NO"), 'OBS_SFF_VF'] = "Inelegível ou sobra contábil."
        INCRanl.loc[cri5 & (INCRanl['OBS_SFF_VF'] == "NO"), 'OBS_SFF_VF'] = "Obra de doação ou de incorporação, deve ser atualizado pelo IPCA."
        INCRanl.loc[cri1 & (INCRanl['OBS_SFF_VF'] == "NO"), 'OBS_SFF_VF'] = "Desvio no VF declarado em relação ao (>=0,1%) obtido a partir do ROA"
        INCRanl.loc[cri2 & (INCRanl['OBS_SFF_VF'] == "NO"), 'OBS_SFF_VF'] = "Desvio no VF declarado em relação ao (>=0,1%) obtido a partir do ROA, mesmo considerando 2 desvios padrão"
        INCRanl.loc[cri3 & (INCRanl['OBS_SFF_VF'] == "NO"), 'OBS_SFF_VF'] = "Coeficiente de variação do material alto no projeto: há outliers? itens com códigos errados? erro de estorno? variação agressiva de preços?"
        INCRanl.loc[cri4 & (INCRanl['OBS_SFF_VF'] == "NO"), 'OBS_SFF_VF'] = "Item não conciliado: código do item está correto (ROA ou INCR)? tucagem está correta (ROA ou INCR)?"
        
        st.html(""" <h2>Análise da da abertura do VF do arquivo INCR pelo ROA</h2>
                        <div style="
                            padding:12px 14px;
                            border-radius:10px;
                            background:rgba(17,17,17,0.05);
                            border:1px solid rgba(0,0,0,0.08);
                            margin-bottom:12px;
                            line-height:1.45;
                        ">
                        <p  style="text-align: justify;text-indent: 40px">Compara-se o razão analítico de obras (ROA) com o valor 
                        de fábrica do componente principal (UC/UAR) para avaliar a consistência do valor atribuído ao projeto no 
                        arquivo de valoração do incremental, identificando possíveis discrepâncias que possam indicar inconsistências 
                        na abertura apresentada. Abaixo temos o resultado analítico:   
                        </p>
                        </div>
                        """)
        
        st.dataframe(INCRanl.head(1000), width='stretch', hide_index=True)
        INCRanl.to_sql('TST_VL_VF_TAB_ROAf', bd, if_exists='replace', index=False)
        df_saida = (INCRanl
                    .groupby(by=['OBS_SFF_VF'])
                    .agg(
                    VL_SOMA=('VL_VOC', 'sum')
                        )
                    .reset_index()
                    .fillna(0))
        
        df_saida['Pct_Item'] = df_saida['VL_SOMA'] / df_saida['VL_SOMA'].sum()
        for n in df_saida.columns.to_list():
            if (n[:2].upper() == 'VL') & pd.api.types.is_numeric_dtype(df_saida[n]):
                df_saida[n] = df_saida[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            elif (n[:2].upper() == 'PC') & pd.api.types.is_numeric_dtype(df_saida[n]):
                df_saida[n] = df_saida[n].apply(lambda x: f"{x:,.4%}".replace(",", "X").replace(".", ",").replace("X", "."))

        config = {
                    "OBS_SFF_VF": st.column_config.TextColumn("Observação de análise"),
                    "VL_SOMA": st.column_config.TextColumn("Valor total observado com esta observação (R$)"),
                    "Pct_Item": st.column_config.TextColumn("Participação no total do Incremental")
                }
        
        st.html(""" 
                        <div style="
                            padding:12px 14px;
                            border-radius:10px;
                            background:rgba(17,17,17,0.05);
                            border:1px solid rgba(0,0,0,0.08);
                            margin-bottom:12px;
                            line-height:1.45;
                        ">
                        <p  style="text-align: justify;text-indent: 40px">A seguir temos o resultado sintético:   
                        </p>
                        </div>
                        """)
        cols3 = st.columns([1,3,1], gap='small')
        with cols3[1]:
            st.dataframe(df_saida.head(1000), width='stretch', hide_index=True,  column_config=config)


        plt.style.use('seaborn-v0_8')
        sns.set_palette("viridis")

        dic_plt = {}
        for ix, nm in enumerate(INCRanl['OBS_SFF_VF'].unique()):
            dic_plt[nm] = f'TIPO {ix+1}'

        texto_legenda = " \n".join([f"{v} = {k}" for k, v in dic_plt.items()])

        heatmap_data = INCRanl.replace(dic_plt).copy()

        heatmap_data = heatmap_data.pivot_table(
                                            index='Nr_TI',
                                            columns='OBS_SFF_VF', 
                                            values='VL_SOMA',
                                            aggfunc='sum',
                                            fill_value=0
                                        )

        heatmap_percent = (heatmap_data / heatmap_data.sum().sum()) * 100

        fig, ax = plt.subplots(figsize=(14, 10))

        colors = ['#f7fbff', '#4292c6', '#08306b']
        custom_cmap = LinearSegmentedColormap.from_list('custom_blue', colors)

        sns.heatmap(
                        heatmap_percent,
                        annot=True,
                        fmt='.2f',                    
                        cmap=custom_cmap,
                        linewidths=0.5,
                        linecolor='white',
                        cbar_kws={'label': 'Percentual (%)'},
                        ax=ax
                    )

        ax.set_title('Distribuição do valor por TI e Tipo de Observação\n(Valores em % do Total)',
                    fontsize=12, fontweight='bold', pad=20)
        ax.set_xlabel('Tipo de Observação', fontsize=8, fontweight='bold')
        ax.set_ylabel('TI', fontsize=10, fontweight='bold')
        ax.tick_params(axis='both', labelsize=10, width=2, length=5)

        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)

        plt.text(0.5, -0.30, texto_legenda, 
                transform=ax.transAxes, 
                ha="center", 
                fontsize=10, 
                bbox=dict(boxstyle="round", facecolor='#4292c6', alpha=0.5))

        plt.tight_layout()
        st.html(""" 
                        <div style="
                            padding:12px 14px;
                            border-radius:10px;
                            background:rgba(17,17,17,0.05);
                            border:1px solid rgba(0,0,0,0.08);
                            margin-bottom:12px;
                            line-height:1.45;
                        ">
                        <p  style="text-align: justify;text-indent: 40px">A seguir temos o resultado sintético, aberto por TI:   
                        </p>
                        </div>
                        """)
        cols3a = st.columns([1,3,1], gap='small')
        with cols3a[1]:
            st.pyplot(fig)
            plt.close(fig)

        if not sql.existe_tabela("TST_VL_JOA_TAB_ROA", bd) or refazer:
            SQLq = f"""
                        SELECT 
                            t1.Cd_SubODI, t1.Nr_TI, t1.Cd_NG, 
                            SUM(
                                CASE 
                                    WHEN VL_tot LIKE '%,%' THEN CAST(REPLACE(VL_tot, ',', '.') AS REAL)
                                    ELSE CAST(VL_tot AS REAL)
                                END
                            ) AS VL_TOT
                        FROM 
                            ROA t1 
                        WHERE 
                            t1.dt_ARQ = ?
                        GROUP BY
                            t1.Cd_SubODI, t1.Nr_TI, t1.Cd_NG
                    """
            ROA_JOA = sql.imp_tbl_forma_001('ROA', SQLq = SQLq, con = bd, st=st, Empresa=empresa)
            for nm in ROA_JOA.columns.to_list():
                if ROA_JOA[nm].dtype == 'object' and nm[:2].upper() in ["VL"]:
                    ROA_JOA[nm] = pd.to_numeric(ROA_JOA[nm].astype(str).str.replace(',','.'), 
                                                                errors='coerce',
                                                                downcast='float')
            ROA_JOA = (ROA_JOA
                    .pivot_table(values="VL_TOT", index=["Cd_SubODI", "Nr_TI"], 
                                columns="Cd_NG", aggfunc="sum", dropna=False, fill_value=0)
                    .rename_axis(columns=None)
                    .reset_index())
            for n in range(1, 7):
                if f"{n}" not in ROA_JOA.columns:
                    ROA_JOA[f"{n}"] = 0
            ROA_JOA = ROA_JOA.rename(columns = {'1' : 'VL_UC_TOT', '2' : 'VL_COM_TOT', '3' : 'VL_MOP_TOT',
                                        '4' : 'VL_ST_TOT', '5' : 'VL_JOA_TOT', '6' : 'VL_OUT_TOT'})
            ROA_JOA['VL_TOT'] = ROA_JOA[['VL_UC_TOT','VL_COM_TOT','VL_MOP_TOT','VL_ST_TOT','VL_JOA_TOT','VL_OUT_TOT']].sum(axis=1)
            VL_01 = ROA_JOA[ROA_JOA['VL_TOT'] < 0].copy()
            if len(VL_01)>0:
                st.warning("Empresa fez marcação de TI equivocada, pois estornos estão em TI diferentes, resultando em projetos, Cd_SubODI e Nr_TI, com saldos negativos.")
                VL_01.to_sql("TI_SLD_NEGATIVO", bd, if_exists='replace', index=False)
            ROA_JOA = ROA_JOA[ROA_JOA['VL_TOT'] > 0]
            ROA_JOA.to_sql('TST_VL_JOA_TAB_ROA', bd, if_exists='replace', index=False)
        else:
            SQLq = f"""
                        SELECT 
                            *
                        FROM 
                            TST_VL_JOA_TAB_ROA
                    """
            ROA_JOA = sql.carga_sqlite_cache(SQLq, bd)

        ROA_JOA['VL_TOT'] = ROA_JOA[['VL_UC_TOT','VL_COM_TOT','VL_MOP_TOT','VL_ST_TOT']].sum(axis=1)
        ROA_JOA = ROA_JOA.groupby(by=['Cd_SubODI','Nr_TI'])[['VL_JOA_TOT','VL_TOT']].sum().reset_index()
        
        ROA_JOA['Pct_JOA_ROA'] = (ROA_JOA['VL_JOA_TOT'] / (ROA_JOA['VL_TOT']))

        # Em tese, deveria refletir o JOA do ROA...
        LIM_JOA_PRJ = (INCR
                .groupby(by=['Cd_SubODI','Nr_TI'])
                .agg(
                    VL_JOA = ('VL_VOC_JOA_AVAL', 'sum'),
                    VL_VF=('VL_VOC_VF_AVAL', 'sum'),
                    VL_COM=('VL_VOC_COM_AVAL', 'sum'),
                    VL_CA=('VL_VOC_CA_AVAL', 'sum'),
                        )
                    .assign(
                            PCT_JOA_PRJ = lambda x: x['VL_JOA'] / (x['VL_VF'] + x['VL_COM'] + x['VL_CA'])
                    )
                .reset_index()
                .drop(columns=['VL_JOA','VL_VF','VL_COM','VL_CA'])
                )

        LIM_JOA_PRJ['PCT_JOA_PRJ'] = LIM_JOA_PRJ['PCT_JOA_PRJ'].fillna(0)
        LIM_JOA_PRJ = LIM_JOA_PRJ.merge(ROA_JOA[['Cd_SubODI','Nr_TI','Pct_JOA_ROA']], how='left', on =['Cd_SubODI','Nr_TI'])
        INCR = INCR.merge(LIM_JOA_PRJ, how = 'left', on =['Cd_SubODI','Nr_TI'])
        INCR['Pct_JOA_ROA'] = INCR['Pct_JOA_ROA'].fillna(0)
        crt = np.isclose(INCR['Pct_JOA_ROA'].fillna(0), 
                        INCR['PCT_JOA_PRJ'].fillna(0), 
                        rtol=0.001)
        
        INCR.loc[~crt, 'TESTE_JOA_ROA'] = "Divergência no JOA apresentado no projeto pela avaliadora"
        INCR.loc[crt, 'TESTE_JOA_ROA'] = "NO"

        crt = (INCR['Pct_JOA_ROA'].fillna(0) -  INCR['PCT_JOA_PRJ'].fillna(0)) > 0
        INCR.loc[crt, 'TESTE_JOA_ROA'] = "NO, ROA maior que o informado"
        INCR.to_sql('TST_VL_JOA_TAB_ROAf', bd, if_exists='replace', index=False)
        st.html(""" <h2>Análise da da abertura do JOA do arquivo INCR pelo ROA</h2>
                        <div style="
                            padding:12px 14px;
                            border-radius:10px;
                            background:rgba(17,17,17,0.05);
                            border:1px solid rgba(0,0,0,0.08);
                            margin-bottom:12px;
                            line-height:1.45;
                        ">
                        <p  style="text-align: justify;text-indent: 40px">Compara-se o razão analítico de obras (ROA) com o valor 
                        do JOA do projeto apresentado no laudo para avaliar a consistência do valor atribuído ao projeto no 
                        arquivo de valoração do incremental, identificando possíveis discrepâncias que possam indicar inconsistências 
                        na abertura apresentada. Abaixo temos o resultado analítico:   
                        </p>
                        </div>
                        """)
        
        st.dataframe(INCR.head(1000), width='stretch', hide_index=True)

        df_saida = (INCR
                    .groupby(by=['TESTE_JOA_ROA','Cd_TP_AVAL'])
                    .agg(
                    VL_SOMA=('VL_VOC', 'sum')
                        )
                    .reset_index()
                    .fillna(0))
        
        df_saida['Pct_Item'] = df_saida['VL_SOMA'] / df_saida['VL_SOMA'].sum()
        for n in df_saida.columns.to_list():
            if (n[:2].upper() == 'VL') & pd.api.types.is_numeric_dtype(df_saida[n]):
                df_saida[n] = df_saida[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            elif (n[:2].upper() == 'PC') & pd.api.types.is_numeric_dtype(df_saida[n]):
                df_saida[n] = df_saida[n].apply(lambda x: f"{x:,.4%}".replace(",", "X").replace(".", ",").replace("X", "."))

        config = {
                    "TESTE_JOA_ROA": st.column_config.TextColumn("Observação de análise"),
                    "VL_SOMA": st.column_config.TextColumn("Valor total observado com esta observação (R$)"),
                    "Pct_Item": st.column_config.TextColumn("Participação no total do Incremental"),
                    'Cd_TP_AVAL': st.column_config.TextColumn("Tipo de método de avaliação")
                }
        st.html("""     
                        <div style="
                            padding:12px 14px;
                            border-radius:10px;
                            background:rgba(17,17,17,0.05);
                            border:1px solid rgba(0,0,0,0.08);
                            margin-bottom:12px;
                            line-height:1.45;
                        ">
                        <p  style="text-align: justify;text-indent: 40px">A seguir temos o resultado sintético:   
                        </p>
                        </div>
                        """)
        cols3 = st.columns([1,3,1], gap='small')
        with cols3[1]:
            st.dataframe(df_saida, width='stretch', hide_index=True,  column_config=config)
        if False:
            st.html("""     <h2>Saídas em excel</h2>
                            <div style="
                                padding:12px 14px;
                                border-radius:10px;
                                background:rgba(17,17,17,0.05);
                                border:1px solid rgba(0,0,0,0.08);
                                margin-bottom:12px;
                                line-height:1.45;
                            ">
                            <p  style="text-align: justify;text-indent: 40px">Caso queira as saídas em Excel, pressione F0 para a
                            a análise da distribuição do VOC e F1 para a análise do VF e do JOA.   
                            </p>
                            </div>
                            """)
            cols3a = st.columns([3,1,3,1,3], gap='small')
            with cols3a[1]:
                impr1 = st.button("Imprimir F0")
            if not anl_inv:
                with cols3a[3]:
                    impr = st.button("Imprimir F1")
                
                if impr:
                    imprimi_F1_ABT(f'{local}\AIS_ANLS', bd, empresa, st=st)
            if impr1:
                imprimi_F0_ABT(f'{local}\AIS_ANLS', bd, empresa, st=st)
    return ROA_NG


def analise_mop(st=None, bd=None, empresa=None, dir_trab=None):

    if not (bd and sql.existe_tabela('MOP', bd)):
        if st:
            st.warning("Faltam dados de MOP")
        else:
            print("Faltam dados de MOP")
        return False
    
    df_GO = bsc_dados_reg('Bd_GO')
    df_GO.columns = df_GO.columns.str.replace('\ufeff', '', regex=False).str.replace('ï»¿', '', regex=False)

    Cd_EMP = sql.bsc_cd_aneel(empresa)
    df_GO = df_GO[df_GO['IdeAgente']==Cd_EMP]
    df_GO['DT_REF'] = pd.to_datetime(df_GO['AnmCompetencia'].astype(str) + '01', format='%Y%m%d')
    df_GO['Cd_CC'] = df_GO['NumConta'].astype(str)
    df_GO = df_GO[['DT_REF','Cd_CC','DscConta','VlrDebito','VlrCredito','VlrSaldo']].copy().rename(
        columns={'DscConta': 'Dsc_Conta', 'VlrDebito': 'VL_DEB_BMP', 'VlrCredito' : 'VL_CRED_BMP',
                 'VlrSaldo' : 'VL_SLD_BMP'})

    df_GO = df_GO[(df_GO['DT_REF'].dt.date >= st.session_state.dt_ini) & 
                  (df_GO['DT_REF'].dt.date <= st.session_state.dt_fim) &
                  (df_GO['Cd_CC'].str.startswith(('6105305','6105306')))].sort_values(['DT_REF','Cd_CC'])
    
    df_MOP = sql.imp_tbl_forma_001('MOP', con=bd, st=st, Empresa=empresa)
    df_MOP_RUBRICAS = sql.imp_tbl_forma_001('MOP_RUBRICAS', con=bd, st=st, Empresa=empresa)
    df_RUBR = bsc_dados_reg('tbl_rubricas')
    df_MOP_RUBRICAS = df_MOP_RUBRICAS.merge(df_RUBR, how = 'left', on = 'COD_RUBRICA', indicator=True)

    if len(df_MOP_RUBRICAS[df_MOP_RUBRICAS['_merge'] != 'both'])>0:
        saida = df_MOP_RUBRICAS[df_MOP_RUBRICAS['_merge'] != 'both'].copy()
        saida = saida[['Id_Ext_MOP_RUB','Id_Ext_MOP_FOPAG','COD_RUBRICA','VL_RUBR','IND_RUBR']].copy()
        saida['OBS_SFF'] = "Preencher o COD_RUBRICA"
        saida.to_csv(rf"{dir_trab}/tst_rubricas.csv", sep="|", decimal=',', encoding="Latin-1", chunksize=100_000, index=False)
        saida.to_sql('tbl_tst_rubricas', bd, index=False, if_exists='replace')
        if st:
            registrar_artefato(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                file_path = rf'{dir_trab}/tst_rubricas.csv',
                                tipo_artefato = "SAIDA", 
                                calcular_hash = True)
        
    df_MOP_RUBRICAS = df_MOP_RUBRICAS.drop(columns='_merge')
    df_MOP_RUBRICAS['Nm_RUBRICA'] = df_MOP_RUBRICAS['Nm_RUBRICA'].fillna('Outras')
    df_MOP_RUBRICAS['VL_RUBR'] = pd.to_numeric(df_MOP_RUBRICAS['VL_RUBR'].str.replace(",","."), errors='coerce').fillna(0)
    lst_RUB_excluir = cod_excluir = [
                                        '1099','1210','1211','1217','1299','1300','1401','1403','1899','2501','2502','6105','9989',
                                    ]
    df_MOP_RUBRICAS['FLG_EXC'] = df_MOP_RUBRICAS['COD_RUBRICA'].isin(lst_RUB_excluir) | df_MOP_RUBRICAS['COD_RUBRICA'].isnull() | df_MOP_RUBRICAS['Nm_RUBRICA'].isin(['Outras'])
    df_MOP_RUBRICAS['Nm_RUBRICA'] = np.where(
                                                df_MOP_RUBRICAS['FLG_EXC'],
                                                df_MOP_RUBRICAS['Nm_RUBRICA'] + ' (Excluir)',
                                                df_MOP_RUBRICAS['Nm_RUBRICA']
                                            )
    lst_RUB = df_MOP_RUBRICAS[df_MOP_RUBRICAS['Nm_RUBRICA'].notnull()]['Nm_RUBRICA'].drop_duplicates().to_list()
    df_MOP_RUBRICASh = (
                            df_MOP_RUBRICAS.pivot_table(
                                index=['Id_Ext_MOP_FOPAG'],
                                columns='Nm_RUBRICA',
                                values='VL_RUBR',
                                aggfunc='sum',
                                fill_value=0
                            )
                            .reset_index()
                        )
    
    df_MOP_ANLS = df_MOP.merge(df_MOP_RUBRICASh, how = 'outer', on = 'Id_Ext_MOP_FOPAG', indicator=True)

    dic = {
            'both' : 'NO',
            'left_only' : 'Somente no arquivo de MOP',
            'right_only' : 'Somente no arquivo de MOP_RUBRICAS'
          }
    df_MOP_ANLS['OBS_SFF'] = df_MOP_ANLS['_merge'].map(dic)
    df_MOP_ANLS = df_MOP_ANLS.drop(columns='_merge')

    for n in df_MOP_ANLS.columns:
        if (n[:2].upper() in ['VL','HR']) or (n in lst_RUB):
            df_MOP_ANLS[n] = pd.to_numeric(df_MOP_ANLS[n].astype(str).str.replace(",","."), errors='coerce').fillna(0)
        elif n != 'OBS_SFF':
            df_MOP_ANLS[n] = df_MOP_ANLS[n].fillna("ND")

    df_MOP_ANLS['VL_TOTAL_RUBRICAS'] = df_MOP_ANLS[lst_RUB].sum(axis=1).round(2)
    rub_cons = [nm for nm in lst_RUB if 'Excluir' not in nm]
    
    df_MOP_ANLS['VL_TOTAL_RUBRICAS_CONS_ODI'] = df_MOP_ANLS[rub_cons].sum(axis=1).round(2)
    df_MOP_ANLS['Pct_RUBRICAS_CONS_ODI'] = df_MOP_ANLS['VL_TOTAL_RUBRICAS_CONS_ODI'].fillna(0) / (df_MOP_ANLS['VL_TOTAL_RUBRICAS'].fillna(1) + 1e-6)
    df_MOP_ANLS['VL_DIF'] = (df_MOP_ANLS['VL_FOPAG'] - df_MOP_ANLS['VL_TOTAL_RUBRICAS']).round(2)
    tol = 0.01
    df_MOP_ANLS['FLG_CONC'] = df_MOP_ANLS['VL_DIF'].abs() <= tol

    mask1 = df_MOP_ANLS['Hr_Efetivas'] < 1
    df_HRef = df_MOP_ANLS[~mask1].groupby(['Dsc_Cargo','Cd_Depto','Dt_CMPT'])['Hr_Efetivas'].max().reset_index().drop_duplicates()
    df_MOP_ANLS = df_MOP_ANLS.merge(df_HRef, how='left', on = ['Dsc_Cargo','Cd_Depto','Dt_CMPT'], suffixes=("","_cor"))
    df_MOP_ANLS.loc[~mask1, 'Hr_Efetivas_cor'] = df_MOP_ANLS.loc[~mask1, 'Hr_Efetivas']

    df_MOP_ANLS['Hr_ODS_calc'] = (df_MOP_ANLS['Hr_OPEX'].clip(lower=0) - df_MOP_ANLS['Hr_ODD'].clip(lower=0)).round(2).clip(lower=0)
    df_MOP_ANLS['DIF_HR_TOTAL'] = (df_MOP_ANLS['Hr_Efetivas_cor'] - df_MOP_ANLS['Hr_CAPEX'].clip(lower=0) - df_MOP_ANLS['Hr_OPEX'].clip(lower=0)).round(2)

    erro_opex = df_MOP_ANLS['DIF_HR_TOTAL'] > tol

    df_MOP_ANLS['Hr_OPEX_REC'] = np.where(
                                            erro_opex,
                                            df_MOP_ANLS['Hr_Efetivas_cor'].clip(lower=0) - df_MOP_ANLS['Hr_CAPEX'].clip(lower=0),
                                            df_MOP_ANLS['Hr_OPEX'].clip(lower=0)
                                        )

    df_MOP_ANLS['Hr_ODS'] = np.where(
                                        erro_opex,
                                        df_MOP_ANLS['Hr_OPEX_REC'].clip(lower=0) - df_MOP_ANLS['Hr_ODD'].clip(lower=0),
                                        df_MOP_ANLS['Hr_ODS_calc'].clip(lower=0)
                                    )

    df_MOP_ANLS['Hr_OPEX_REC'] = df_MOP_ANLS['Hr_OPEX_REC'].round(2)
    df_MOP_ANLS['Hr_ODS'] = df_MOP_ANLS['Hr_ODS'].round(2)
    
    obs = []
    cols_hrs = ['Hr_Efetivas_cor', 'Hr_CAPEX', 'Hr_OPEX', 'Hr_ODD']
    hr_invalida = df_MOP_ANLS['Hr_Efetivas'].abs() <= tol
    obs.append(np.where(
                            hr_invalida,
                            'Hr_Efetivas igual a zero. Registro inválido para análise das horas.',
                            ''
                        ))
    obs.append(np.where(
                            df_MOP_ANLS[cols_hrs].isna().any(axis=1) 
                            & (~hr_invalida),
                            'Há valores ausentes em horas.',
                            ''
                        ))

    obs.append(np.where(
                            df_MOP_ANLS[cols_hrs].lt(0).any(axis=1)
                            & (~hr_invalida),
                            'Há valores negativos em horas.',
                            ''
                        ))

    obs.append(np.where(
                            (df_MOP_ANLS['DIF_HR_TOTAL'].abs() > tol)
                            & (~hr_invalida),
                            'Hr_CAPEX + Hr_OPEX não confere com Hr_Efetivas.',
                            ''
                        ))

    obs.append(np.where(
                            erro_opex
                            & (~hr_invalida),
                            'Hr_OPEX menor que Hr_ODD; Hr_ODS ficaria negativa. Recalculada Hr_OPEX por Hr_Efetivas - Hr_CAPEX.',
                            ''
                        ))

    obs.append(np.where(
                            (df_MOP_ANLS['Hr_ODS'] < -tol)
                            & (~hr_invalida),
                            'Hr_ODS permanece negativa após recálculo.',
                            ''
                        ))

    df_MOP_ANLS['OBS_HRS'] = (
                        pd.DataFrame(obs).T
                        .apply(lambda x: ' '.join([v for v in x if v]), axis=1)
                    )

    df_MOP_ANLS['OBS_HRS'] = df_MOP_ANLS['OBS_HRS'].replace('', 'OK')

    teste = df_MOP_ANLS['Hr_Efetivas_cor'].fillna(0) >= (df_MOP_ANLS['Hr_CAPEX'].fillna(0)+df_MOP_ANLS['Hr_ODD'].fillna(0)+df_MOP_ANLS['Hr_ODS'].fillna(0))
    df_MOP_ANLS.loc[teste, 'Pct_ODI'] = df_MOP_ANLS.loc[teste, 'Hr_CAPEX'].fillna(0) / (df_MOP_ANLS.loc[teste, 'Hr_Efetivas_cor'].fillna(1)+1e-6)
    df_MOP_ANLS.loc[teste, 'Pct_ODD'] = df_MOP_ANLS.loc[teste, 'Hr_ODD'].fillna(0) / (df_MOP_ANLS.loc[teste, 'Hr_Efetivas_cor'].fillna(1)+1e-6)
    df_MOP_ANLS.loc[teste, 'Pct_ODS'] = df_MOP_ANLS.loc[teste, 'Hr_ODS'].fillna(0) / (df_MOP_ANLS.loc[teste, 'Hr_Efetivas_cor'].fillna(1)+1e-6)

    df_MOP_ANLS.loc[~teste, 'Pct_ODI'] = 0
    df_MOP_ANLS.loc[~teste, 'Pct_ODD'] = 0
    df_MOP_ANLS.loc[~teste, 'Pct_ODS'] = 0

    df_MOP_ANLS['VL_ODI_REF_SFF'] = (np.where(df_MOP_ANLS['FLG_CONC'],
                                    df_MOP_ANLS['Pct_ODI'] * df_MOP_ANLS['VL_TOTAL_RUBRICAS'],
                                    np.where(df_MOP_ANLS['Pct_ODI']>0,
                                             df_MOP_ANLS['Pct_ODI'] *df_MOP_ANLS['VL_FOPAG']   
                                             ,0)
                                    ))


    df_MOP_ANLS['VL_ODI_DIF'] = (df_MOP_ANLS['VL_ODI_REF_SFF'] - df_MOP_ANLS['VL_FOPAG_CAPEX']).round(2)
    df_MOP_ANLS['OBS_VL_CAPEX'] = np.where(
                                            df_MOP_ANLS['VL_ODI_DIF'] < -1,
                                            "Glosar R$ " + (
                                                df_MOP_ANLS['VL_ODI_DIF']
                                                .abs()
                                                .map(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                                            ),
                                            np.where(
                                                (df_MOP_ANLS['Pct_ODI'] +
                                                df_MOP_ANLS['Pct_ODD'] +
                                                df_MOP_ANLS['Pct_ODS']) == 0,
                                                "Verificar dados informados",
                                                "NO"
                                        ))
    
    df_MOP_ANLS['DT_REF'] = (pd.to_datetime(df_MOP_ANLS['Dt_CMPT'], errors='coerce')
                                            .dt.strftime('%Y/%m/%d')
                                            .fillna('ND'))
    def bsc_mop(tabela):
        if not sql.existe_tabela(tabela, bd):
            return pd.DataFrame()
        
        if not sql.existe_tabela(f"RES_{tabela}", bd):
            df_MOPh = pd.DataFrame()
            SQLq = f"""
                        SELECT
                            COALESCE(Cd_CA, '-1') AS Cd_CA,
                            Dt_Lcmto,
                            VL_tot
                        FROM {tabela}
                        WHERE Cd_NG = 3 AND Dt_ARQ = ?
                        ;
                """
            df_MOP = sql.imp_tbl_forma_001(tabela, SQLq, bd, st, empresa)
            df_MOP['VL_tot'] = pd.to_numeric(df_MOP['VL_tot'].str.replace(",","."), errors='coerce')
            df_MOP['Dt_Lcmto'] = pd.to_datetime(
                                            df_MOP['Dt_Lcmto'].astype(str).str[:7] + '-01',
                                            format='%Y-%m-%d',
                                            errors='coerce'
                                        )
            df_MOP = df_MOP.groupby(['Cd_CA','Dt_Lcmto'], dropna=False)['VL_tot'].sum().reset_index()
            
            dic_MOP = {
                            '-1' : f'VL_NCLS_{tabela}',
                            '1' : f'VL_Frete_{tabela}',
                            '2' : f'VL_Projeto_{tabela}',
                            '3' : f'VL_Gerenciamento_{tabela}',
                            '4' : f'VL_Fiscalização_{tabela}',
                            '5' : f'VL_Montagem_{tabela}',
                            '6' : f'VL_Suporte_{tabela}'

                        }

            df_MOP['Cd_CA'] = df_MOP['Cd_CA'].astype(str).replace(dic_MOP)
            df_MOPh = (
                                    df_MOP.pivot_table(
                                        index=['Dt_Lcmto'],
                                        columns='Cd_CA',
                                        values='VL_tot',
                                        aggfunc='sum',
                                        fill_value=0
                                    )
                                    .reset_index()
                                    .sort_values(by='Dt_Lcmto')
                                )
            soma = df_MOP['Cd_CA'].drop_duplicates().to_list()
            if f'VL_Suporte_{tabela}' in soma:
                soma.remove(f'VL_Suporte_{tabela}')
            df_MOPh['VL_TOTAL_MOP_ROA'] = df_MOPh[soma].sum(axis=1).round(2)
            df_MOPh = df_MOPh.rename(columns={'Dt_Lcmto':'DT_REF', 'VL_TOTAL_MOP_ROA' : f'VL_TOTAL_MOP_{tabela}'})
            df_MOPh.to_sql(f"RES_{tabela}", bd, if_exists='replace', index=False)
        else:
            df_MOPh = pd.read_sql(f"SELECT * FROM RES_{tabela}", bd)
        return df_MOPh

    df_MOP_ROA = bsc_mop('ROA')
    df_MOP_ROAic = bsc_mop('ROAaicAT')
    if len(df_MOP_ROAic)>0:
        df_MOP_CMP_INV = df_MOP_ROA.merge(df_MOP_ROAic, how='outer', on='DT_REF', indicator=True)
        dic = {
                    'both' : 'NO',
                    'left_only' : 'Somente no arquivo de AIS',
                    'right_only' : 'Somente no arquivo de AIC'
                }
        df_MOP_CMP_INV['OBS_SFF_ROAs'] = df_MOP_CMP_INV['_merge'].map(dic)
        df_MOP_CMP_INV = df_MOP_CMP_INV.drop(columns='_merge')
    else:
        df_MOP_CMP_INV = df_MOP_ROA.copy()
        df_MOP_CMP_INV['OBS_SFF_ROAs'] = "SEM AIC"
        for nm in df_MOP_CMP_INV.columns:
            if nm[-4:].upper() == '_ROA':
                df_MOP_CMP_INV[f'{nm}aicAT'] = 0.

    for nm in df_MOP_CMP_INV.columns:
        if nm[:2].upper() in ['VL']:
            df_MOP_CMP_INV[nm] = df_MOP_CMP_INV[nm].fillna(0)

    df_MOP_CMP_INV['VL_TOT_RO'] = df_MOP_CMP_INV['VL_TOTAL_MOP_ROAaicAT'] + df_MOP_CMP_INV['VL_TOTAL_MOP_ROA']
    df_MOP_FOPAG = df_MOP_ANLS[df_MOP_ANLS['DT_REF'] != "ND"][['DT_REF', 'VL_ODI_REF_SFF','VL_FOPAG_CAPEX']].copy()
    df_MOP_FOPAG['DT_REF'] = pd.to_datetime(
                                    df_MOP_FOPAG['DT_REF'],
                                    format='%Y/%m/%d',
                                    errors='coerce'
                                )
    df_MOP_FOPAG = df_MOP_FOPAG.groupby('DT_REF', dropna=False)[['VL_ODI_REF_SFF','VL_FOPAG_CAPEX']].sum().reset_index()
    df_MOP_CMP_INV['DT_REF'] = pd.to_datetime(df_MOP_CMP_INV['DT_REF'], errors='coerce')
    df_MOP_FOPAG['DT_REF'] = pd.to_datetime(df_MOP_FOPAG['DT_REF'], errors='coerce')
    df_MOP_CMP_INV = df_MOP_CMP_INV.merge(df_MOP_FOPAG, how='outer', on='DT_REF')
    df_MOP_CMP_INV['VL_ODI_REF_SFF'] = df_MOP_CMP_INV['VL_ODI_REF_SFF'].fillna(0)
    df_MOP_CMP_INV['VL_FOPAG_CAPEX'] = df_MOP_CMP_INV['VL_FOPAG_CAPEX'].fillna(0)

    df_MOP_CMP_INV.to_sql('tbl_comparativa_mop_fopag_roa', bd, if_exists='replace', index=False)
    df_MOP_ANLS.to_sql('tbl_analises_mop', bd, if_exists='replace', index=False)

    df_MOP_CMP_INV.to_csv(rf'{dir_trab}/tbl_comparativa_mop_fopag_roa.csv', sep="|", decimal=',', encoding="Latin-1", chunksize=100_000, index=False)
    df_MOP_ANLS.to_csv(rf'{dir_trab}/tbl_analises_mop.csv', sep="|", decimal=',', encoding="Latin-1", chunksize=100_000, index=False)

    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_trab}/tbl_comparativa_mop_fopag_roa.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        registrar_artefato(st.session_state.database_MAN, 
                                    st.session_state.execucao_id, 
                                    file_path = rf'{dir_trab}/tbl_analises_mop.csv',
                                    tipo_artefato = "SAIDA", 
                                    calcular_hash = True)
    
    with pd.ExcelWriter(f'{dir_trab}/REL_CONCILIACAO_MOP_BMP_{empresa}.xlsx', engine='xlsxwriter') as writer:
        df_MOP_ANLS.to_excel(writer, sheet_name="REL_MOP", index=False)
        df_MOP_CMP_INV.to_excel(writer, sheet_name="REL_MOP_ROA", index=False)
        df_MOP_RUBRICAS.to_excel(writer, sheet_name="REL_RUBRICAS", index=False)
        df_GO.to_excel(writer, sheet_name="REL_PESSOAL_BMP", index=False)
        
        workbook = writer.book
        ws_ver = workbook.add_worksheet("VERIFICAR")

        formato_header = workbook.add_format({
                                                'bold': True,
                                                'font_name': 'Calibri',
                                                'font_size': 10,
                                                'bg_color': "#BEC1B9",
                                                'border': 1,
                                                'align': 'center',
                                                'valign': 'vcenter',
                                                'text_wrap': True
                                            })

        formato_dados = workbook.add_format({
                                                'font_name': 'Calibri',
                                                'font_size': 8,
                                                'valign': 'vcenter',
                                                'border': 1,
                                                'align': 'center',
                                            })
        formato_data = workbook.add_format({
                                                'font_name': 'Calibri',
                                                'font_size': 8,
                                                'num_format': 'dd/mm/yyyy',
                                                'valign': 'vcenter',
                                                'border': 1,
                                                'align': 'center',
                                            })
        formato_numero = workbook.add_format({
                                                'font_name': 'Calibri',
                                                'font_size': 8,
                                                'num_format': '#,##0.00',
                                                'valign': 'vcenter',
                                                'border': 1,
                                                'align': 'center',
                                            })
        
        for sheet_name in ["REL_MOP","REL_MOP_ROA","REL_RUBRICAS","REL_PESSOAL_BMP"]:
            worksheet = writer.sheets[sheet_name]
            df = {  "REL_MOP": df_MOP_ANLS,
                    "REL_MOP_ROA": df_MOP_CMP_INV, 
                    "REL_RUBRICAS": df_MOP_RUBRICAS,
                    "REL_PESSOAL_BMP": df_GO}[sheet_name].copy()
            
            for col_num, value in enumerate(df.columns):
                worksheet.write(0, col_num, value, formato_header)

            worksheet.set_row(0, 12.5)
            for i, col in enumerate(df.columns):
                if col[:4].upper()=='DT_R':
                    df[col] = pd.to_datetime(df[col], format = "%Y-%m-%d %H:%M:%S", errors="coerce")
                max_len = max(
                                df[col].astype(str).map(len).max(),
                                len(str(col))
                             ) + 2
                worksheet.set_row(i, 12.5)
                if pd.api.types.is_datetime64_any_dtype(df[col]) or (col[:4].upper()=='DT_R'):
                    worksheet.set_column(i, i, max_len, formato_data)
                elif pd.api.types.is_numeric_dtype(df[col]):
                    worksheet.set_column(i, i, max_len, formato_numero)
                else:
                    worksheet.set_column(i, i, max_len, formato_dados)

            worksheet.hide_gridlines(2)
            worksheet.freeze_panes(1, 0)

        headers = [
                    "DT_REF",
                    "VL_MOP_FOLHA",
                    "VL_BMP_FOLHA_PESSOAL",
                    "VL_BMP_FOLHA_ADM",
                    "Diferença",
                    "VL_MOP_FOLHA_CAPEX",
                    "VL_BMP_FOLHA_CAPEX_PESSOAL",
                    "VL_BMP_FOLHA_CAPEX_ADM",
                    "Diferença",
                    "VL_MOP_RO",
                    "Diferença",
                  ]
        
        for c, h in enumerate(headers):
            max_len = len(str(h)) + 2
            ws_ver.write(0, c, h)
            ws_ver.set_column(c, c, max_len, formato_header)
        worksheet.set_row(0, 12.5)

        df_GO["DT_REF"] = pd.to_datetime(df_GO["DT_REF"], errors="coerce")
        df_MOP_ANLS["DT_REF"] = pd.to_datetime(df_MOP_ANLS["DT_REF"], errors="coerce")
        chaves = sorted(
                            set(df_GO["DT_REF"]).union(df_MOP_ANLS[df_MOP_ANLS["DT_REF"].notnull()]["DT_REF"])
                        )
        for r, chave in enumerate(chaves, start=1):
            worksheet.set_row(r, 12.5)
            ws_ver.write(r, 0, chave, formato_data)
            col_chvmop = xl_col_to_name(df_MOP_ANLS.columns.get_loc("DT_REF"))
            ws_ver.write_formula(
                                    r, 1,
                                    f'=SUMIFS(REL_MOP!$N:$N,REL_MOP!${col_chvmop}:${col_chvmop},A{r+1})',
                                    formato_numero
                                )
            ws_ver.write_formula(
                                    r, 2,
                                    f'=SUMIFS(REL_PESSOAL_BMP!$D:$D,REL_PESSOAL_BMP!$A:$A,A{r+1},REL_PESSOAL_BMP!$B:$B,"6105305*")',
                                    formato_numero
                                )
            ws_ver.write_formula(
                                    r, 3,
                                    f'=SUMIFS(REL_PESSOAL_BMP!$D:$D,REL_PESSOAL_BMP!$A:$A,A{r+1},REL_PESSOAL_BMP!$B:$B,"6105306*")',
                                    formato_numero
                                )
            ws_ver.write_formula(
                                    r, 4,
                                    f'=B{r+1}-C{r+1}',
                                    formato_numero
                                )
            ws_ver.write_formula(
                                    r, 5,
                                    f'=SUMIFS(REL_MOP!$O:$O,REL_MOP!${col_chvmop}:${col_chvmop},A{r+1})',
                                    formato_numero
                                )
            ws_ver.write_formula(
                                    r, 6,
                                    f'=SUMIFS(REL_PESSOAL_BMP!$E:$E,REL_PESSOAL_BMP!$A:$A,A{r+1},REL_PESSOAL_BMP!$B:$B,"6105305*")',
                                    formato_numero
                                )
            ws_ver.write_formula(
                                    r, 7,
                                    f'=SUMIFS(REL_PESSOAL_BMP!$E:$E,REL_PESSOAL_BMP!$A:$A,A{r+1},REL_PESSOAL_BMP!$B:$B,"6105306*")',
                                    formato_numero
                                )
            ws_ver.write_formula(
                                    r, 8,
                                    f'=F{r+1}-G{r+1}',
                                    formato_numero
                                )
            col_chvroa = xl_col_to_name(df_MOP_CMP_INV.columns.get_loc("VL_TOT_RO"))
            ws_ver.write_formula(
                                    r, 9,
                                    f'=SUMIFS(REL_MOP_ROA!${col_chvroa}:${col_chvroa},REL_MOP_ROA!$A:$A,A{r+1})',
                                    formato_numero
                                )
            ws_ver.write_formula(
                                    r, 10,
                                    f'=G{r+1}-J{r+1}',
                                    formato_numero
                                )
            
        ws_ver.hide_gridlines(2)
        ws_ver.freeze_panes(1, 0)

    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_trab}/REL_CONCILIACAO_MOP_BMP_{empresa}.xlsx',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)