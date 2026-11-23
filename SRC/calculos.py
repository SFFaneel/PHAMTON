import pandas as pd, duckdb
import os, time, re, ollama, json, joblib
from pandas.tseries.offsets import MonthEnd
import streamlit as st
import sqlite3 as sl
from datetime import datetime, timedelta, date
import UTILS.sqlfnc as sql
import numpy as np
import UTILS.dados_bulldozer as bullD
from dateutil.relativedelta import relativedelta
from pandas.tseries.offsets import MonthBegin
from pandas.tseries.offsets import DateOffset
from UTILS.indicadores_economicos import busca_ipca
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import datetime as bibDTAX
from typing import Optional, Dict, Any
from io import BytesIO
import datetime as dt1
from  UTILS.ai_funcoes import compara_materiais
from UTILS.fcs_gerais import comparar_componentes
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from MANIFESTO import (
                        visual_manifesto, 
                        criar_manifesto,
                        execucao_trilha,
                        rastrear_funcao,
                        registrar_evento,
                        registrar_metrica,
                        registrar_artefato,
                        inicializa_database,
                        inicializa_detalhes,
                        inicializar_rastreamento,
                      )

def bsc_dd_CIAP(bd = None, st = None) -> pd.DataFrame:
    if bd == None:
        return pd.DataFrame()

    BL_G = sql.imp_tbl_forma_000(nm_tbl = 'BL_G', con=bd, st=st)
    df_Gfinal = BL_G.copy()
    df_Gfinal = df_Gfinal[[str(i) for i in range(1, 11)] + ['DT_INI', 'Nm_Arq']]

    crit = df_Gfinal['1'] == 'G110'
    col_sel = ['DT_INI', 'DT_FIM', 'SALDO_IN_ICMS', 'SOM_PARC','VL_TRIB_EXP','VL_TOTAL', 'IND_PER_SAI', 'ICMS_APROP','SOM_ICMS_OC']
    df_Gfinal[col_sel] = None
    for i, n in enumerate(col_sel):
        df_Gfinal.loc[crit, n] = df_Gfinal.loc[crit, f'{i+2}']
        df_Gfinal[n] = df_Gfinal[n].ffill()
    df_Gfinal = df_Gfinal[~crit]

    crit = (df_Gfinal['1'] == 'G125') & (df_Gfinal['4'].isin(["MC", "IM", "IA", "AT"]))
    critf = (df_Gfinal['1'] == 'G125')
    col_sel = ['COD_IND_BEM','DT_MOV','TIPO_MOV','VL_IMOB_ICMS_OP','VL_IMOB_ICMS_ST','VL_IMOB_ICMS_FRT',
            'VL_IMOB_ICMS_DIF','NUM_PARC','VL_PARC_PASS']
    df_Gfinal[col_sel] = None
    for i, n in enumerate(col_sel):
        df_Gfinal.loc[crit, n] = df_Gfinal.loc[crit, f'{i+2}']
        df_Gfinal[n] = df_Gfinal[n].ffill()
    df_Gfinal = df_Gfinal[~critf]

    crit = (df_Gfinal['1'] == 'G130')
    col_sel = ['IND_EMIT','COD_PART','COD_MOD','SERIE','NUM_DOC','CHV_NFE_CTE','DT_DOC','NUM_DA']
    df_Gfinal[col_sel] = None
    for i, n in enumerate(col_sel):
        df_Gfinal.loc[crit, n] = df_Gfinal.loc[crit, f'{i+2}']
        df_Gfinal[n] = df_Gfinal[n].ffill()
    crit = (df_Gfinal['1'] == 'G140')
    df_Gfinal = df_Gfinal[crit]

    df_Gfinal = df_Gfinal.rename(columns={'2':'NUM_ITEM', '3':'COD_ITEM', '4': 'QTDE', '5' : 'UNID',
                                        '6' : 'VL_ICMS_OP_APLICADO', '7' : 'VL_ICMS_ST_APLICADO', 
                                        '8' : 'VL_ICMS_FRT_APLICADO', '9' : 'VL_ICMS_DIF_APLICADO'})

    return df_Gfinal[['Nm_Arq', 'DT_INI', 'DT_FIM', 'SALDO_IN_ICMS', 'SOM_PARC', 'VL_TRIB_EXP',  'VL_TOTAL',  
                        'IND_PER_SAI', 'ICMS_APROP',  'SOM_ICMS_OC',  'COD_IND_BEM',  'DT_MOV',  'TIPO_MOV',  
                        'VL_IMOB_ICMS_OP',  'VL_IMOB_ICMS_ST',  'VL_IMOB_ICMS_FRT', 'VL_IMOB_ICMS_DIF',  'NUM_PARC',  
                        'VL_PARC_PASS',  'IND_EMIT',  'COD_PART',  'COD_MOD',  'SERIE',  'NUM_DOC',  'CHV_NFE_CTE',
                        'DT_DOC',  'NUM_DA', 'NUM_ITEM', 'COD_ITEM', 'QTDE', 'UNID', 'VL_ICMS_OP_APLICADO', 
                        'VL_ICMS_ST_APLICADO', 'VL_ICMS_FRT_APLICADO', 'VL_ICMS_DIF_APLICADO']]

def bsc_memo(Dt_Ref, Cd_EMP, Cd_EMP2 = None, data_ref = None):
    MEMO_SFF=pd.read_csv('tabelas\\tbl_resumo_BB.csv', decimal=',', sep="|",
                         header = 0, encoding="Latin-1", dtype=str)
    try:
        dt_REF = (datetime.strptime(Dt_Ref[:8] + '28', '%Y-%m-%d').date() + 
              timedelta(days=4))
    except:
        dt_REF = (datetime.strptime(Dt_Ref[:8] + '28', '%Y/%m/%d').date() + 
              timedelta(days=4))
    dt_REF = dt_REF - timedelta(days=dt_REF.day) 
    crit1 = (MEMO_SFF['Id_Agente'].astype(str) == str(Cd_EMP)) & (MEMO_SFF['DT_REF'] == dt_REF.strftime('%Y/%m/%d'))
    if Cd_EMP2:
        crit2 = (MEMO_SFF['Id_Agente'].astype(str) == str(Cd_EMP2)) & (MEMO_SFF['DT_REF'] == data_ref.strftime('%Y/%m/%d'))
        MEMO_PP=MEMO_SFF[crit1 | crit2][['Nm_Item','VL_ITEM']]
    else:
        MEMO_PP=MEMO_SFF[crit1][['Nm_Item','VL_ITEM']]
    MEMO_PP.columns=['Nm_Item','VL_MEMO_SGT']
    MEMO_PP = conv_num(MEMO_PP)
    MEMO_PP = MEMO_PP.groupby("Nm_Item", dropna=False)['VL_MEMO_SGT'].sum().reset_index()
    return MEMO_PP

def importar_dados_duckdb(nome_tabela, con, Empresa, colunas, col_faltante=None, valor_padrao=None, inibir=False):
    erro = {}
    df = pd.DataFrame()
    dt_ARQ = sql.max_arq(nome_tabela, con, Empresa)
    if dt_ARQ:
        cod_empresa = f"00000{sql.bsc_cd_aneel(Empresa)}"[-5:]
        arq = os.path.join(f"{st.session_state.tra_dir}\SDI_001",f"{nome_tabela}_{cod_empresa}_{dt_ARQ}.csv")
        for enc in ['latin-1', 'utf-8', 'CP1252']:
            try:
                SQLq = f"""
                            SELECT *
                            FROM 
                            read_csv_auto('{arq}',
                                        delim='|',
                                        null_padding=true, 
                                        encoding = '{enc}',
                                        parallel = true,
                                        all_varchar = true);
                    """
                df = duckdb.query(SQLq).to_df()
                df = conv_num(df, colunas)
                return df, erro
                if col_faltante and col_faltante not in df.columns:
                    df[col_faltante] = valor_padrao
            except Exception as e:
                erro[enc] = e
        
        return df, erro
    else:
        if inibir:
            return pd.DataFrame(), erro
        mensagem = f'Falha ao importar o arquivo {nome_tabela} da base local.'
        if st:
            st.error(mensagem)
            return pd.DataFrame(), erro
        else:
            raise UserWarning(mensagem)

def importar_dados(nome_tabela, con, Empresa, colunas, col_faltante=None, valor_padrao=None, inibir=False):
    dt_ARQ = sql.max_arq(nome_tabela, con, Empresa)
    if dt_ARQ:
        SQLq = f"""
                    SELECT *
                    FROM {nome_tabela} t1 WHERE dt_ARQ = {dt_ARQ};
               """
        df = pd.read_sql(SQLq, con)
        df = conv_num(df, colunas)
        
        if col_faltante and col_faltante not in df.columns:
            df[col_faltante] = valor_padrao
        
        return df
    else:
        if inibir:
            return pd.DataFrame()
        mensagem = f'Falha ao importar o arquivo {nome_tabela} da base local.'
        if st:
            st.error(mensagem)
            return None
        else:
            raise UserWarning(mensagem)


def conv_num(df, lista = ['VL']):
    lst = df.columns.to_list()
    for nm in lst:
        if df[nm].dtype == 'object' and nm[:2].upper() in lista:
            df[nm] = pd.to_numeric(df[nm].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')
            df[nm]  = df[nm] .fillna(0)
    return df

def anl_var(df, nm_Index, nm_VARd, nm_VARi, OAT):
    varX = nm_VARd.replace('CMU','VOC')
    tt = ['0'] if OAT == 'INCLUIR' else ['0', '1']
    teste = df[df['FLG_OAT'].isin(tt)][[nm_Index, nm_VARi, nm_VARd, 'Qtd_AIS']].copy()
    teste[varX] = teste[nm_VARd] * teste['Qtd_AIS']
    teste.columns = [nm_Index, nm_VARi, nm_VARd, 'Qtd','VL_TOT']
    # Calculando o IQR por código
    iqr_cd = teste.groupby(nm_VARi)[nm_VARd].apply(calculate_iqr).reset_index().copy()
    iqr_cd.columns = [nm_VARi, 'INTERQ']
    teste = teste.merge(iqr_cd, how = 'left', on = nm_VARi)

    iqr_cd = teste.groupby(nm_VARi)[nm_VARd].apply(calculate_Q1).reset_index().copy()
    iqr_cd.columns = [nm_VARi, 'Q1']
    teste = teste.merge(iqr_cd, how = 'left', on = nm_VARi)

    iqr_cd = teste.groupby(nm_VARi)[nm_VARd].apply(calculate_Q3).reset_index().copy()
    iqr_cd.columns = [nm_VARi, 'Q3']
    teste = teste.merge(iqr_cd, how = 'left', on = nm_VARi)

    iqr_cd = teste.groupby(nm_VARi)[nm_VARd].apply(calculate_median).reset_index().copy()
    iqr_cd.columns = [nm_VARi, 'MEDIANA']
    teste = teste.merge(iqr_cd, how = 'left', on = nm_VARi)

    iqr_cd = teste.groupby(nm_VARi)[nm_VARd].apply(calculate_std).reset_index().copy()
    iqr_cd.columns = [nm_VARi, 'STD']
    teste = teste.merge(iqr_cd, how = 'left', on = nm_VARi)

    teste['DESV_ABS'] = abs(teste[nm_VARd] - teste['MEDIANA'])
    iqr_cd = teste.groupby(nm_VARi)['DESV_ABS'].apply(calculate_std).reset_index().copy()
    iqr_cd.columns = [nm_VARi, 'MAD']
    teste = teste.merge(iqr_cd, how = 'left', on = nm_VARi)

    teste['LIM_INF'] = teste['Q1'] - (1.5 * teste['INTERQ'])
    teste.loc[teste['LIM_INF'] < 0, 'LIM_INF'] = 0
    teste['LIM_SUP'] = teste['Q3'] + (1.5 * teste['INTERQ'])

    teste['ANL_OUTLIER'] = 'OK'


    teste.loc[(abs(teste[nm_VARd] - teste['MEDIANA']) > (2 * teste['MAD']) ), 'ANL_OUTLIER'] = 'OUTLIER, CRITÉRIO MAD'
    teste.loc[(teste[nm_VARd]<teste['LIM_INF']) | (teste[nm_VARd]>teste['LIM_SUP']), 'ANL_OUTLIER'] = 'OUTLIER, CRITÉRIO TUKEY'

    iqr_cd = teste.groupby(nm_VARi)[['VL_TOT', 'Qtd']].apply(calculate_vlu).reset_index()
    iqr_cd.columns = [nm_VARi, 'VL_MED_ORI']
    teste = teste.merge(iqr_cd, how = 'left', on = nm_VARi)

    iqr_cd = teste[teste['ANL_OUTLIER'] == 'OK'].groupby(nm_VARi)[['VL_TOT', 'Qtd']].apply(calculate_vlu).reset_index()
    iqr_cd.columns = [nm_VARi, 'VL_MED_MDF']
    teste = teste.merge(iqr_cd, how = 'left', on = nm_VARi)
    teste.fillna(0, inplace = True)
    teste['DELTA_PC'] = (teste['VL_MED_MDF'] - teste['VL_MED_ORI']) / teste['VL_MED_ORI']
    teste['OBS_FISC'] = 'OK'
    teste.loc[(teste['ANL_OUTLIER'] != 'OK') & ((teste['DELTA_PC']) < -0.05), 'OBS_FISC'] = 'Avaliar este lançamento'
    teste.loc[(teste['VL_TOT'] == 0), 'OBS_FISC'] = 'Justificar valor zerado'
    
    return teste

def fnc_ajs_df(df, VARV=[], VARP=[]):
    for n in df.columns.to_list():
        if df[n].dtype != 'object':
            if n[:2].upper() in VARV:
                df[n] = df[n].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            elif n[:3].upper() in VARP:
                df[n] = df[n].apply(lambda x: f"{x:,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
        else:
            if n[:2].upper() in VARV:
                df[n] = df[n].apply(lambda x: f"{float(x.replace(',', '.')):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            elif n[:3].upper() in VARP:
                df[n] = df[n].apply(lambda x: f"{float(x.replace(',', '.')):,.2%}".replace(",", "X").replace(".", ",").replace("X", "."))
    return df   

def calculate_iqr(group):
    q1 = group.quantile(0.25)
    q3 = group.quantile(0.75)
    return q3 - q1

def calculate_Q1(group):
    q1 = group.quantile(0.25)
    return q1

def calculate_Q3(group):
    q3 = group.quantile(0.75)
    return q3

def calculate_median(group):
    q3 = group.median()
    return q3

def calculate_std(group):
    q3 = group.std()
    return q3

def calculate_vlu(group):
    q3 = group.iloc[:, 0].sum() / group.iloc[:, 1].sum()
    return q3

def tst_ALT(df_01, df_02, obs):
    if len(df_02[df_02['OBS_FISC'] == obs]):
        df_01 = pd.concat([df_01,df_02[[df_02.columns.to_list()[0],"OBS_FISC"]][df_02['OBS_FISC'] == obs]], ignore_index = True)
    return df_01

def valor_na_data_min_max(group):
    datas_validas = group['Dt_NF'].dropna()

    if datas_validas.empty:
        return pd.Series({
                            'Dt_Min': pd.NaT,
                            'Valor_Dt_Min': 0,
                            'Dt_Max': pd.NaT,
                            'Valor_Dt_Max': 0
                        })

    idx_min = datas_validas.idxmin()
    idx_max = datas_validas.idxmax()
    
    return pd.Series({
                        'Dt_min': group.loc[idx_min, 'Dt_NF'],
                        'Dt_max': group.loc[idx_max, 'Dt_NF'],
                        'VL_Dt_min': group.loc[idx_min, 'VL_UNI_AT'],
                        'VL_Dt_max': group.loc[idx_max, 'VL_UNI_AT']
                    })

def processar_cnpj(cnpj, BL_C, BL_G, BL_Z, bd_EFD, progresso=None, st=None, pct=100, idx=0):

    lst_arq = BL_Z[(BL_Z['1'] == '0000') & (BL_Z['7'] == cnpj)]['Nm_Arq'].drop_duplicates().to_list()
    BL_C = BL_C[BL_C['Nm_Arq'].isin(lst_arq)].copy()
    BL_G = BL_G[BL_G['Nm_Arq'].isin(lst_arq)].copy()
    BL_Z = BL_Z[BL_Z['Nm_Arq'].isin(lst_arq)].copy()
    dt_ini_proc = pd.to_datetime('1900/01/01',format="%Y/%m/%d", errors='coerce')
    dt_fim_proc = pd.to_datetime('1900/01/01',format="%Y/%m/%d", errors='coerce')
    for n1 in BL_Z[(BL_Z['1'] == '0000') & (BL_Z['7'] == cnpj)]['4'].drop_duplicates().to_list():
        if dt_ini_proc == pd.to_datetime('1900/01/01',format="%Y/%m/%d", errors='coerce'):
            dt_ini_proc = pd.to_datetime(f'{n1[-4:]}/{n1[2:4]}/{n1[:2]}',format="%Y/%m/%d", errors='coerce')
        elif dt_ini_proc > pd.to_datetime(f'{n1[-4:]}/{n1[2:4]}/{n1[:2]}',format="%Y/%m/%d", errors='coerce'):
            dt_ini_proc = pd.to_datetime(f'{n1[-4:]}/{n1[2:4]}/{n1[:2]}',format="%Y/%m/%d", errors='coerce')
        if dt_fim_proc == pd.to_datetime('1900/01/01',format="%Y/%m/%d", errors='coerce'):
            dt_fim_proc = pd.to_datetime(f'{n1[-4:]}/{n1[2:4]}/{n1[:2]}', format="%Y/%m/%d", errors='coerce')
        elif dt_fim_proc < pd.to_datetime(f'{n1[-4:]}/{n1[2:4]}/{n1[:2]}',format="%Y/%m/%d", errors='coerce'):
            dt_fim_proc = pd.to_datetime(f'{n1[-4:]}/{n1[2:4]}/{n1[:2]}', format="%Y/%m/%d", errors='coerce')

    if progresso: progresso.progress(int(10*pct/100 +  + idx * pct), text="Tratando dados G110...")
    BL_G110 = BL_G[BL_G['1'] == 'G110'].copy()
    BL_G110 = BL_G110[[str(i) for i in range(1, 11)] + ['DT_INI', 'Nm_Arq']]
    BL_G110.columns = ['REG', 'DT_INI', 'DT_FIM', 'SALDO_IN_ICMS', 'SOM_PARC',
                       'VL_TRIB_EXP', 'VL_TOTAL', 'IND_PER_SAI', 'ICMS_APROP',
                       'SOM_ICMS_OC', 'DATA', 'Nm_Arq']
    for col in ['SALDO_IN_ICMS', 'SOM_PARC', 'VL_TRIB_EXP', 'VL_TOTAL', 'ICMS_APROP', 'SOM_ICMS_OC']:
        BL_G110[col] = pd.to_numeric(BL_G110[col].str.replace(',', '.'), errors='coerce')
    BL_G110['DT_INI'] = pd.to_datetime(BL_G110['DT_INI'], format='%d%m%Y', errors='coerce')
    BL_G110['DT_FIM'] = pd.to_datetime(BL_G110['DT_FIM'], format='%d%m%Y', errors='coerce')
    BL_G110 = BL_G110.sort_values(by=['DT_INI'])
    BL_G110['IND_PER_SAI'] = BL_G110['VL_TRIB_EXP'] / BL_G110['VL_TOTAL']

    if progresso: progresso.progress(int(20*pct/100), text="Tratando dados 0300...")
    BL_0300 = BL_Z[BL_Z['1'] == '0300'].copy().iloc[:, :7]
    
    BL_0300.columns = ['REG', 'COD_IND_BEM', 'IDENT_MERC', 'DESCR_ITEM', 'COD_PRNC', 'COD_CTA', 'NR_PARC']
    BL_0300 = BL_0300.drop_duplicates(subset=['COD_IND_BEM', 'DESCR_ITEM'])

    if progresso: progresso.progress(int(30*pct/100 + idx * pct), text="Tratando dados G125...")
    BL_G126 = pd.DataFrame()
    BL_G125 = BL_G[(BL_G['1'] == 'G125') & (BL_G['4'].isin(['IM', 'IA']))].copy()
    if len(BL_G125)==0:
        BL_G125 = BL_G[(BL_G['1'] == 'G125') & (BL_G['4'].isin(['SI']))].copy()
        BL_G126 = BL_G[BL_G['1'] == 'G126'].copy()

    BL_G125 = BL_G125[[str(i) for i in range(1, 11)] + ['DT_INI', 'Nm_Arq']]
    BL_G125.columns = ['REG', 'COD_IND_BEM', 'DT_MOV', 'TIPO_MOV', 'VL_IMOB_ICMS_OP',
                       'VL_IMOB_ICMS_ST', 'VL_IMOB_ICMS_FRT', 'VL_IMOB_ICMS_DIF',
                       'NUM_PARC', 'VL_PARC_PASS', 'DT_INI', 'Nm_Arq']
    for col in ['VL_IMOB_ICMS_OP', 'VL_IMOB_ICMS_ST', 'VL_IMOB_ICMS_DIF']:
        BL_G125[col] = pd.to_numeric(BL_G125[col].str.replace(',', '.'), errors='coerce').fillna(0)
    BL_G125['DT_MOV'] = pd.to_datetime(BL_G125['DT_MOV'], format='%d%m%Y', errors='coerce')
    BL_G125 = BL_G125.merge(BL_0300[['COD_IND_BEM', 'DESCR_ITEM']], on='COD_IND_BEM', how='left')

    if progresso: progresso.progress(int(40*pct/100 + idx * pct), text="Consolidando G125 por mês...")
    BL_G125['DT_INI'] = BL_G125['DT_MOV'].dt.to_period("M").dt.to_timestamp()
    BL_G125_CNL = BL_G125.groupby('DT_INI')[['VL_IMOB_ICMS_OP', 'VL_IMOB_ICMS_DIF', 'VL_IMOB_ICMS_ST']].sum()
    BL_G125_CNL['VL_TOT_ICMS'] = BL_G125_CNL.sum(axis=1)
    BL_G125_CNL.columns = ['VL_ICMS_COMPRA_ATIVO', 'VL_DIFAL_COMPRA_ATIVO', 'VL_SUBST_TRIB', 'VL_TOT_ICMS']

    if progresso: progresso.progress(int(50*pct/100 + idx * pct), text="Processando WACC...")
    tbl_wacc = pd.read_csv('tabelas/tbl_WACC.csv', sep='|', encoding='Latin-1')
    tbl_wacc['DT_VIG'] = pd.to_datetime(tbl_wacc['DT_VIG'].str.replace('/', ''), format='%Y%m%d')
    tbl_wacc['Vl_WACC_REAL'] = pd.to_numeric(tbl_wacc['Vl_WACC_REAL'], errors='coerce')
    
    meses = pd.date_range(dt_ini_proc, dt_fim_proc, freq='MS', name='DT_VIG')
    tbl_wacc_mes = pd.DataFrame(meses)
    tbl_wacc_mes = tbl_wacc_mes.merge(tbl_wacc, how='left', on='DT_VIG')
    tbl_wacc_mes=tbl_wacc_mes.drop(tbl_wacc_mes.columns[[2,3]], axis=1)
    tbl_wacc_mes.loc[0,'Vl_WACC_REAL'] = tbl_wacc[tbl_wacc['DT_VIG']<=tbl_wacc_mes['DT_VIG'][0]]['Vl_WACC_REAL'].iloc[-1]
    tbl_wacc_mes['Vl_WACC_REAL']=tbl_wacc_mes['Vl_WACC_REAL'].ffill() 
    tbl_wacc_mes.columns=['DT_INI','Tx_WACC']

    if progresso: progresso.progress(int(60*pct/100 + idx * pct), text="Unindo G110 + G125 + WACC...")
    BL_G125cmp = BL_G110.merge(BL_G125_CNL, on='DT_INI', how='left')
    BL_G125cmp['COEF_CRED_EST'] = BL_G125cmp['VL_TRIB_EXP'] / BL_G125cmp['VL_TOTAL']
    BL_G125cmp['VL_CRED_ICMS'] = BL_G125cmp['COEF_CRED_EST'] * BL_G125cmp['VL_TOT_ICMS']
    BL_G125cmp = BL_G125cmp.merge(tbl_wacc_mes, on='DT_INI', how='right').fillna(0)
    BL_G125cmp['CD_TB_ICMS'] = range(1, len(BL_G125cmp) + 1)
    n = 48
    
    df_future = pd.concat([BL_G125cmp.tail(1)] * n, ignore_index=True)
    df_future['DT_FIM'] = pd.to_datetime(df_future['DT_FIM'], errors='coerce')
    for i in range(n):
        df_future.at[i, 'DT_INI'] = df_future.at[i, 'DT_INI'] + pd.DateOffset(months=i+1)
        df_future.at[i, 'DT_FIM'] = (df_future.at[i, 'DT_FIM'] + pd.DateOffset(months=i+1)).replace(day=1) + pd.offsets.MonthEnd(0)
        df_future.at[i, 'CD_TB_ICMS'] = df_future.at[i, 'CD_TB_ICMS'] + i + 1
    df_final = pd.concat([BL_G125cmp, df_future], ignore_index=True)
    VL_COEF = BL_G125cmp.loc[BL_G125cmp['CD_TB_ICMS'] <= len(BL_G125cmp), 'COEF_CRED_EST'].mean()
    df_final.loc[df_final['CD_TB_ICMS'] > len(BL_G125cmp), 'COEF_CRED_EST'] = VL_COEF

    df_final['VL_SALDO_AMT'] = -df_final['VL_TOT_ICMS'] / n
    df_final['VL_SALDO_RED'] = df_final['VL_TOT_ICMS'].shift(n, fill_value = 0) / n
    df_final.loc[df_final['CD_TB_ICMS'] > len(BL_G125cmp), ['VL_CRED_ICMS', 'VL_SALDO_AMT', 'Tx_WACC']] = 0
    df_final['VL_SALDO_AMT'] = df_final['VL_SALDO_AMT'].cumsum()
    df_final['VL_SALDO_RED'] = df_final['VL_SALDO_RED'].cumsum()
    df_final['VL_SALDO_ACUMULADO'] = df_final['VL_CRED_ICMS'].cumsum()
    df_final['VL_ICMS_CREDIT'] = -(df_final['VL_SALDO_AMT'] + df_final['VL_SALDO_RED'])
    df_final['VL_ICMS_CRED'] = df_final['VL_ICMS_CREDIT'] * df_final['COEF_CRED_EST']
    df_final['VL_ICMS_NCRED'] = df_final['VL_ICMS_CREDIT'] * (1 - df_final['COEF_CRED_EST'])

    if progresso: progresso.progress(int(80*pct/100 + idx * pct), text="Calculando ICMS financeiro...")
    WACC_POND = df_final['Tx_WACC'].sum() / len(BL_G125cmp)
    WACC_MES = (1 + WACC_POND) ** (1 / 12) - 1
    VL_CRED = df_final['VL_ICMS_CRED'].sum()
    VL_NCRED = df_final['VL_ICMS_NCRED'].sum()
    CICMS_R = VL_CRED / (n * WACC_MES)
    VP = VL_NCRED + CICMS_R * ((1 / (1 + WACC_MES)**n) + n * WACC_MES - 1)

    resultado = pd.DataFrame({
        'Item': ['WACC Ponderado (%)', 'i (%)', 'Cicms(NR) (R$)', 'Cicms(R) (R$)', 'VP (R$)', 'n'],
        'Valor': [round(WACC_POND * 100, 4), round(WACC_MES * 100, 4),
                  round(VL_NCRED, 2), round(VL_CRED, 2), round(VP, 2), n]
    })

    if progresso: progresso.progress(int(90*pct/100 + idx * pct), text="Salvando resultados...")
    resultado.to_sql(f"tbl_icms_fin_{cnpj}", bd_EFD, if_exists='replace', index=False)
    BL_G110.to_sql(f"BLF_G110_{cnpj}", bd_EFD, if_exists='replace', index=False)
    BL_G125.to_sql(f"BLF_G125_{cnpj}", bd_EFD, if_exists='replace', index=False)
    for col in df_final.columns:
        if col.upper()[:2] == 'DT':
            df_final[col] = pd.to_datetime(df_final[col], errors='coerce')
            df_final[col] = df_final[col].dt.strftime('%Y/%m/%d')
    df_final.to_sql(f"BLF_G125cmp_{cnpj}", bd_EFD, if_exists='replace', index=False)
    tbl_wacc_mes.to_sql(f"tbl_wacc_mes_{cnpj}", bd_EFD, if_exists='replace', index=False)

    BL_UN = BL_G110.merge(BL_G125_CNL, on='DT_INI',how='left')
    BL_UN = BL_UN[['REG', 'DT_INI', 'DT_FIM', 'SALDO_IN_ICMS', 'SOM_PARC', 'VL_TRIB_EXP', 'VL_TOTAL', 
                 'IND_PER_SAI', 'ICMS_APROP', 'SOM_ICMS_OC','VL_ICMS_COMPRA_ATIVO', 'VL_DIFAL_COMPRA_ATIVO', 
                 'VL_SUBST_TRIB', 'VL_TOT_ICMS', 'DATA', 'Nm_Arq']]

    BL_UN.to_sql(f"BLF_UN_{cnpj}", bd_EFD, if_exists='replace', index=False)

    return resultado, BL_G110, BL_G125, BL_G126, BL_G125cmp, BL_UN


def calc_fin_icms(bd_EFD, dt_ini_proc, dt_fim_proc, progresso=None, st=None):
    if progresso:
        progresso.progress(0, text="Buscando dados do SPED...")

    tbl_nms = pd.read_sql("SELECT * FROM LST_ARQ", con=bd_EFD)
    BL_C_list, BL_G_list, BL_Z_list = [], [], []

    for _, row in tbl_nms.iterrows():
        dt_ini_col, Nm_Arq, tabela_nome = row['Dt_INI'], row['Nm_Arq'], f"ARQ_{row.name}"

        def query_bloco(blocos):
            return pd.read_sql(f"""
                SELECT t1.*, DATE('{dt_ini_col}') AS DT_INI, '{Nm_Arq}' AS Nm_Arq
                FROM {tabela_nome} t1
                WHERE t1.'1' in {tuple(blocos)}
            """, con=bd_EFD)

        BL_C_list.append(query_bloco(['C100', 'C170', 'C195', 'C197']))
        BL_G_list.append(query_bloco(['G110', 'G125', 'G126', 'G130', 'G140']))
        BL_Z_list.append(query_bloco(['0000', '0600', '0150', '0200', '0300', '0305']))

    BL_C = pd.concat(BL_C_list, ignore_index=True)
    BL_G = pd.concat(BL_G_list, ignore_index=True)
    BL_Z = pd.concat(BL_Z_list, ignore_index=True)

    BL_C.to_sql("BL_C", bd_EFD, if_exists='replace', index=False)
    BL_G.to_sql("BL_G", bd_EFD, if_exists='replace', index=False)
    BL_Z.to_sql("BL_Z", bd_EFD, if_exists='replace', index=False)

    lst_cnpj = BL_Z[BL_Z['1'] == '0000']['7'].drop_duplicates().to_list()
    total_cnpjs = len(lst_cnpj)
    resultados = []

    for idx, cnpj in enumerate(lst_cnpj):
        pct = int(100 / total_cnpjs)
        resultado, BL_G110, BL_G125, BL_G126, BL_G125cmp, BL_UN = processar_cnpj(cnpj, BL_C, BL_G, BL_Z, bd_EFD, progresso, st, pct,idx)
        resultados.append(resultado)

    return resultado, BL_G110, BL_G125, BL_G126, BL_G125cmp, BL_UN

def calc_fin_icms_ant(bd_EFD, dt_ini_proc, dt_fim_proc,  progresso=None, st=None):
    if progresso:
        progresso.progress(0, text="Buscando dados do SPED...")
    SQLq = """
                SELECT * FROM LST_ARQ ORDER BY Dt_INI
        """
    tbl_nms = pd.read_sql(SQLq, con=bd_EFD)

    BL_C = pd.DataFrame()
    BL_G = pd.DataFrame()
    BL_Z = pd.DataFrame()

    for n in tbl_nms.index:        
        dt_ini_col = tbl_nms.iloc[n, 0]
        dt_fim_col = tbl_nms.iloc[n, 1]
        Nm_Arq = tbl_nms.iloc[n, 3]
        tabela_nome = f"ARQ_{n}"

        SQLq = f"""
                    SELECT t1.*, 
                    DATE('{dt_ini_col}') AS DT_INI,
                    '{Nm_Arq}' AS Nm_Arq
                    FROM {tabela_nome} t1
                    WHERE t1.'1' in ('C100', 'C170', 'C195', 'C197')
                """
        if len(BL_C)==0:
            BL_C = pd.read_sql(SQLq, con=bd_EFD)
        else:
            df_PROV = pd.read_sql(SQLq, con=bd_EFD)
            BL_C = pd.concat([BL_C, df_PROV],ignore_index=True)

        SQLq = f"""
                    SELECT t1.*, 
                    DATE('{dt_ini_col}') AS DT_INI, 
                    '{Nm_Arq}' AS Nm_Arq
                    FROM {tabela_nome} t1
                    WHERE t1.'1' in ('G110', 'G125', 'G126')
                """
        if len(BL_G)==0:
            BL_G = pd.read_sql(SQLq, con=bd_EFD)
        else:
            df_PROV = pd.read_sql(SQLq, con=bd_EFD)
            BL_G = pd.concat([BL_G, df_PROV],ignore_index=True)

        SQLq = f"""
                    SELECT t1.*, 
                    DATE('{dt_ini_col}') AS DT_INI, 
                    '{Nm_Arq}' AS Nm_Arq
                    FROM {tabela_nome} t1
                    WHERE t1.'1' in ('0000', '0600', '0150', '0200', '0300', '0305')
                """
        if len(BL_Z)==0:
            BL_Z = pd.read_sql(SQLq, con=bd_EFD)
        else:
            df_PROV = pd.read_sql(SQLq, con=bd_EFD)
            BL_Z = pd.concat([BL_Z, df_PROV],ignore_index=True)

    BL_C.to_sql("BL_C", bd_EFD, if_exists='replace', index=False)
    BL_G.to_sql("BL_G", bd_EFD, if_exists='replace', index=False)
    BL_Z.to_sql("BL_Z", bd_EFD, if_exists='replace', index=False)

    if progresso:
        progresso.progress(10, text="Tratando dados G110...")

    BL_G110 = BL_G[BL_G['1']=='G110'].copy()
    col_names_G110=['REG','DT_INI','DT_FIM','SALDO_IN_ICMS','SOM_PARC',
                'VL_TRIB_EXP','VL_TOTAL','IND_PER_SAI','ICMS_APROP',
                'SOM_ICMS_OC','DATA','Nm_ARQ']
    cols = [str(col) for col in range(1,11)] + ['DT_INI', 'Nm_Arq']
    BL_G110 = BL_G110[cols]
    BL_G110.columns = col_names_G110
    for i in col_names_G110:
        BL_G110[i] = BL_G110[i].replace(',','.', regex=True)
        if i in ["DT_INI", "DT_FIM"]:
            BL_G110[i] = pd.to_datetime(BL_G110[i], format='%d%m%Y')
        elif i not in ['REG', 'DATA', 'Nm_ARQ']:
            BL_G110[i] = pd.to_numeric(BL_G110[i], errors='coerce')

    BL_G110['IND_PER_SAI']=BL_G110['VL_TRIB_EXP']/BL_G110['VL_TOTAL']

    if progresso:
        progresso.progress(20, text="Tratando dados 0300...")
    BL_0300 = BL_Z[BL_Z['1']=='0300'].copy()
    col_names_0300=['REG','COD_IND_BEM','IDENT_MERC','DESCR_ITEM','COD_PRNC',
                    'COD_CTA','NR_PARC']
    cols = [str(col) for col in range(1,8)] 
    BL_0300=BL_0300[cols]
    BL_0300.columns=col_names_0300
    BL_0300=BL_0300.drop_duplicates(subset = ['REG','COD_IND_BEM','IDENT_MERC','DESCR_ITEM','COD_PRNC',
                    'COD_CTA','NR_PARC'])
    BL_0300_right=BL_0300[['COD_IND_BEM','DESCR_ITEM']].drop_duplicates(subset=['COD_IND_BEM'])

    if progresso:
        progresso.progress(30, text="Tratando dados G125...")
    BL_G125 = pd.DataFrame()
    BL_G126 = pd.DataFrame()
    BL_G125 = BL_G[(BL_G['1']=='G125') & ((BL_G['4']=='IM') | (BL_G['4']=='IA'))].copy()

    if len(BL_G125) == 0:
        BL_G125=BL_G[(BL_G['1']=='G125') & ((BL_G['4']=='SI'))].copy()
        BL_G126=BL_G[(BL_G['1']=='G126')].copy()

    col_names_G125=['REG','COD_IND_BEM','DT_MOV','TIPO_MOV','VL_IMOB_ICMS_OP',
                    'VL_IMOB_ICMS_ST','VL_IMOB_ICMS_FRT','VL_IMOB_ICMS_DIF','NUM_PARC',
                    'VL_PARC_PASS','DATA','Nm_ARQ']
    cols = [str(col) for col in range(1,11)] + ['DT_INI', 'Nm_Arq']
    BL_G125=BL_G125[cols]
    BL_G125.columns=col_names_G125
    for i in col_names_G125:
        BL_G125[i]=BL_G125[i].replace(',','.', regex=True)
        if i[0:2]=='VL':
            BL_G125[i]=BL_G125[i].fillna(0)
            BL_G125[i]=pd.to_numeric(BL_G125[i],errors='coerce')
        elif i=='DT_MOV':
            BL_G125[i]=pd.to_datetime(BL_G125[i], format='%d%m%Y')
    BL_G125=BL_G125.merge(BL_0300_right,on='COD_IND_BEM',how='left')

    BL_G125a = BL_G125.copy()
    BL_G125a['DT_INI'] = BL_G125a['DT_MOV'].to_numpy().astype('datetime64[M]')
    BL_G125_CNL_DT=BL_G125a.groupby('DT_INI')[['VL_IMOB_ICMS_OP','VL_IMOB_ICMS_DIF','VL_IMOB_ICMS_ST']].sum()
    col_names_G125_CNL_DT = ['VL_ICMS_COMPRA_ATIVO','VL_DIFAL_COMPRA_ATIVO','VL_SUBST_TRIB','VL_TOT_ICMS']
    BL_G125_CNL_DT['VL_TOT_ICMS'] = BL_G125_CNL_DT['VL_IMOB_ICMS_OP'] + BL_G125_CNL_DT['VL_IMOB_ICMS_DIF']+BL_G125_CNL_DT['VL_IMOB_ICMS_ST']
    BL_G125_CNL_DT.columns = col_names_G125_CNL_DT

    if progresso:
        progresso.progress(40, text="Manipulando dados G125...")
    BL_G125cmp=BL_G110.merge(BL_G125_CNL_DT,on='DT_INI',how='left')
    BL_G125cmp=BL_G125cmp.drop(BL_G125cmp.columns[[0,2,3,4,7,8,9,10,11]], axis=1)
    BL_G125cmp['COEF_CRED_EST']=BL_G125cmp['VL_TRIB_EXP']/BL_G125cmp['VL_TOTAL']
    BL_G125cmp['VL_CRED_ICMS']=(BL_G125cmp['VL_TRIB_EXP']/BL_G125cmp['VL_TOTAL'])*BL_G125cmp['VL_TOT_ICMS']
    BL_G125cmp.fillna(0,inplace=True)

    #buscar os dados das taxas de capital
    if progresso:
        progresso.progress(50, text="Importando dados do WACC...")
    tbl_wacc=pd.read_csv('tabelas\\tbl_WACC.csv',sep="|",encoding="Latin-1", dtype=str)
    tbl_wacc['Vl_WACC_REAL']=pd.to_numeric(tbl_wacc['Vl_WACC_REAL'],errors='coerce')
    tbl_wacc['DT_VIG']=pd.to_datetime(tbl_wacc['DT_VIG'].replace('/','',regex=True), format='%Y%m%d')

    if progresso:
        progresso.progress(60, text="Tratando WACC para o período incremental...")
    lst_mes = pd.date_range(start=dt_ini_proc, end=dt_fim_proc, freq='MS', name='DT_VIG')
    tbl_wacc_mes = pd.DataFrame(lst_mes)
    tbl_wacc_mes=tbl_wacc_mes.merge(tbl_wacc, on='DT_VIG', how='left')
    tbl_wacc_mes=tbl_wacc_mes.drop(tbl_wacc_mes.columns[[2,3]], axis=1)
    tbl_wacc_mes.loc[0,'Vl_WACC_REAL']=tbl_wacc[tbl_wacc['DT_VIG']<=tbl_wacc_mes['DT_VIG'][0]]['Vl_WACC_REAL'].iloc[-1]
    tbl_wacc_mes['Vl_WACC_REAL']=tbl_wacc_mes['Vl_WACC_REAL'].ffill()
    tbl_wacc_mes.columns=['DT_INI','Tx_WACC']

    nr_a = (dt_fim_proc.year - dt_ini_proc.year) * 12 + dt_fim_proc.month - dt_ini_proc.month + 1

    cols_name = ['CD_TB_ICMS','DT_INI','VL_TRIB_EXP','VL_TOTAL',
                'VL_ICMS_COMPRA_ATIVO','VL_DIFAL_COMPRA_ATIVO','VL_SUBST_TRIB',
                'VL_TOT_ICMS','COEF_CRED_EST','VL_CRED_ICMS','Tx_WACC']
    BL_G125cmp1 = BL_G125cmp.merge(tbl_wacc_mes,on='DT_INI',how='right')

    if progresso:
        progresso.progress(70, text="Fazendo os cálculos...")
    n = 48
    df = BL_G125cmp1[-1:]
    for i in range(1,n):
        df = pd.concat([df,BL_G125cmp1[-1:]],ignore_index=True)
    BL_G125cmp1 = pd.concat([BL_G125cmp1,df],ignore_index=True)
    BL_G125cmp1['CD_TB_ICMS'] = 1
    BL_G125cmp1['CD_TB_ICMS'] = BL_G125cmp1['CD_TB_ICMS'].cumsum()
    BL_G125cmp1 = BL_G125cmp1[cols_name]

    VL_COEFTRB=BL_G125cmp1[BL_G125cmp1['CD_TB_ICMS'] <= nr_a]['COEF_CRED_EST'].mean()
    BL_G125cmp1['VL_SALDO_AMT']=-BL_G125cmp1['VL_TOT_ICMS']/n
    BL_G125cmp1['VL_SALDO_RED']=BL_G125cmp1['VL_TOT_ICMS'].shift(periods=n,fill_value=0)/n
    BL_G125cmp1.loc[BL_G125cmp1['CD_TB_ICMS']>nr_a,'VL_SALDO_AMT']=0
    BL_G125cmp1.loc[BL_G125cmp1['CD_TB_ICMS']>nr_a,'VL_CRED_ICMS']=0
    BL_G125cmp1.loc[BL_G125cmp1['CD_TB_ICMS']>nr_a,'Tx_WACC']=0
    BL_G125cmp1.loc[BL_G125cmp1['CD_TB_ICMS']>nr_a,'COEF_CRED_EST']=VL_COEFTRB
    BL_G125cmp1['VL_SALDO_AMT']=BL_G125cmp1['VL_SALDO_AMT'].cumsum()
    BL_G125cmp1['VL_SALDO_RED']=BL_G125cmp1['VL_SALDO_RED'].cumsum()
    BL_G125cmp1['VL_SALDO_ACUMULADO']=BL_G125cmp1['VL_CRED_ICMS'].cumsum()#+BL_G125cmp1['VL_SALDO_AMT']+BL_G125cmp1['VL_SALDO_RED']
    BL_G125cmp1['VL_ICMS_CREDIT']=-(BL_G125cmp1['VL_SALDO_AMT']+BL_G125cmp1['VL_SALDO_RED'])
    BL_G125cmp1['VL_ICMS_CRED']=BL_G125cmp1['VL_ICMS_CREDIT']*BL_G125cmp1['COEF_CRED_EST']
    BL_G125cmp1['VL_ICMS_NCRED']=BL_G125cmp1['VL_ICMS_CREDIT']*(1-BL_G125cmp1['COEF_CRED_EST'])
    BL_G125cmp1.drop(['VL_TOT_ICMS'], axis=1, inplace=True)

    VL_WACC=BL_G125cmp1['Tx_WACC'].sum()
    WACC_POND=VL_WACC/nr_a
    WACC_MES=((1+WACC_POND)**(1/12))-1
    VL_ICMS_CRED=BL_G125cmp1['VL_ICMS_CRED'].sum()
    VL_ICMS_NCRED=BL_G125cmp1['VL_ICMS_NCRED'].sum()
    CICMS_R=VL_ICMS_CRED/(n*WACC_MES)
    VP=(VL_ICMS_NCRED+(VL_ICMS_CRED/(n*WACC_MES))*((1/(1+WACC_MES)**n)+n*WACC_MES-1))

    dic={
            'Item': ['WACC Ponderado (%)','i (%)','Cicms(NR) (R$)','Cicms(R) (R$)','VP (R$)', 'n'],
            'Valor':[round(WACC_POND*100,4),round(WACC_MES*100,4),round(VL_ICMS_NCRED,2),round(VL_ICMS_CRED,2),round(VP,2), n]
        }

    df = pd.DataFrame(dic)
    if progresso:
        progresso.progress(90, text="Salvando Resultados...")
    df.to_sql(f"tbl_icms_fin", bd_EFD, if_exists='replace', index=False)
    BL_G110.to_sql(f"BLF_G110_{n}", bd_EFD, if_exists='replace', index=False)
    BL_G125.to_sql(f"BLF_G125_{n}", bd_EFD, if_exists='replace', index=False)
    if len(BL_G126)>0:
        BL_G126.to_sql(f"BLF_G126_{n}", bd_EFD, if_exists='replace', index=False)
    BL_G125cmp1.to_sql(f"BLF_G125cmp_{n}", bd_EFD, if_exists='replace', index=False)
    tbl_wacc_mes.to_sql(f"tbl_wacc_mes_{n}", bd_EFD, if_exists='replace', index=False)

    BL_UN=BL_G110.merge(BL_G125_CNL_DT,on='DT_INI',how='left')
    BL_UN=BL_UN[['REG', 'DT_INI', 'DT_FIM', 'SALDO_IN_ICMS', 'SOM_PARC', 'VL_TRIB_EXP', 'VL_TOTAL', 'IND_PER_SAI', 'ICMS_APROP', 'SOM_ICMS_OC',
    'VL_ICMS_COMPRA_ATIVO', 'VL_DIFAL_COMPRA_ATIVO', 'VL_SUBST_TRIB', 'VL_TOT_ICMS', 'DATA', 'Nm_ARQ']]

    BL_UN.to_sql(f"BLF_UN_{n}", bd_EFD, if_exists='replace', index=False)

    return df, BL_G110, BL_G125, BL_G126, BL_G125cmp1, BL_UN

def pre_dados(dir_arq_saida, dt_ini_proc, dt_fim_proc, FLG_ARQ, ICMS_FLG, VL_ODC, con, con_efd, Empresa, ano, st=None,apr1=False,FLG_DIFAL=False):
    if isinstance(con, str):
        con = sl.connect(con)
    
    if st:
        avl = st.progress(0, "Iniciando preparação de dados para análise...")
    if sql.existe_tabela("tbl_FCOGE", con):
        SQLq = f"""
                SELECT *
                FROM tbl_FCOGE 
            """
        tbl_FCOGE = pd.read_sql(SQLq, con)
    else:
        if st.session_state.dt_fim <= date.today():
            if st:
                st.error('Falha ao importar o arquivo tbl_FCOGE da base local.')
                return None
            else:
                raise UserWarning('Falha ao importar o arquivo tbl_FCOGE da base local.')
        else:
            st.warning('Trata-se processo intercalar, será empregado IPCA nas análises.')
            ipca = busca_ipca()[['Dt_REF', 'Nr_IPCA']].rename(columns={'Dt_REF': 'DT_CMPT'})
            idx = ipca.copy()
            idx['DT_CMPT'] = pd.to_datetime(idx['DT_CMPT']).dt.to_period('M').dt.to_timestamp()
            idx['Nr_IPCA'] = pd.to_numeric(idx['Nr_IPCA'], errors='coerce')
            idx = idx.sort_values('DT_CMPT').drop_duplicates('DT_CMPT', keep='last')

            dt_ini_m = pd.to_datetime("01-01-2015").to_period('M').to_timestamp()
            dt_fim_m = pd.to_datetime(st.session_state.dt_fim).to_period('M').to_timestamp()
            if dt_fim_m < dt_ini_m:
                raise ValueError("A data fornecida deve ser ≥ 2015-01-01.")
            
            meses = pd.date_range(start=dt_ini_m, end=dt_fim_m, freq='MS')
            base = pd.DataFrame({'DT_CMPT': meses})
            out = base.merge(idx, on='DT_CMPT', how='left')
            out['Nr_IPCA'] = out['Nr_IPCA'].ffill()
            if out['Nr_IPCA'].isna().any():
                primeiro = out['Nr_IPCA'].dropna().iloc[0]
                out['Nr_IPCA'] = out['Nr_IPCA'].fillna(primeiro)

            out['DT_INI'] = (out['DT_CMPT'] + pd.offsets.MonthBegin(1))
            out['DT_FIM'] = dt_fim_m
            out['FC'] = out['Nr_IPCA'] / out.iloc[-1,1]
            out = out[['Nr_IPCA','DT_INI','DT_FIM','DT_CMPT','FC']].rename(columns={'Nr_IPCA' : 'Nr_COGE','DT_CMPT' : 'DT_REF'})

            lst_COGE =['FCM0019','FCM0083','FCM0085','FCM0102','FCM0111','FCM0112','FCM0113','FCM0114','FCM0115','FCM0116',
                       'FCM0117','FCM0118','FCM0119','FCM0130','FCM0148','FCM0149','FCM0153','FCM0177','FCM0178','FCM0182',
                       'FCM0186','FCM0187','FCM0188','FCM0195','FCM0200','FCM0214','FCM0235','FCM0236','FCM0259','FCM0261',
                       'FCM0281','FCM0302','FCM0307','FCM0308','FCM0329','FCM0402','FCM0403','FCM0407','FCM0424','FCM0455',
                       'FCM0457','FCM0458','FCM0459','FCM0460','FCM0461','FCM0462','FCM0463','FCM0464','FCM0465','FCM0466',
                       'FCM0467','FCM0468','FCM0469','FCM0470','FCM0471','FCM0472','FCM0473','FCM0474','FCM0475','FCM0476',
                       'FCM0477','FCM0478','FCM0479','FCM0480','FCM0481','FCM0482','FCM0483','FCM0484','FCM0485','FCM0486',
                       'FCM0487','FCM0488','FCM0489','FCM0490','FCM0491','FCM0492','FCM0493','FCM0494','FCM0495','FCM0496',
                       'FCM0497','FCM0498','FCM0499','FCM0500','FCM0501','FCM0502','FCM0503','FCM0504','FCM0505','FCM0506',
                       'FCM0507','FCM0508','FCM0509','FCM0510','FCM0511','FCM0512','FCM0513','FCM0514','FCM0515','FCM0516',
                       'FCM0517','FCM0518','FCM0519','FCM0520','FCM0521','FCM0522','FCM0523','FCM0524','FCM0525','FCM0526',
                       'FCM0527','FCM0528','FCM0529','FCM0530','FCM0531','FCM0532','FCM0533','FCM0534','FCM0535','FCM0536',
                       'FCM0537','FCM0538','FCM0539','FCM0540','FCM0541','FCM0542','FCM0543','FCM0544','FCM0545','FCM0546',
                       'FCM0547','FCM0548','FCM0549','FCM0550','FCM0551','FCM0552','FCM0553','FCM0554','FCM0556','FCM0557',
                       'FCM0558','FCM0559','FCM0560','FCM0561','FCM0562','FCM0563','FCM0564','FCM0565','FCM0566','FCM0567',
                       'FCM0568','FCM0569','FCM0570','FCM0571','FCM0572','FCM0573','FCM0574','FCM0575','FCM0576','FCM0577',
                       'FCM0578','FCM0579','FCM0580','FCM0581','FCM0582','FCM0583','FCM0584','FCM0585','FCM0586','FCM0587',
                       'FCM0588','FCM0589','FCM0590','FCM0591','FCM0592','FCM0593','FCM0594','FCM0595','FCM0596','FCM0597',
                       'FCM0598','FCM0599','FCM0600','FCM0601','FCM0602','FCM0603','FCM0604','FCM0605','FCM0606','FCM0607',
                       'FCM0608','FCM0609','FCM0610','FCM0611','FCM0612','FCM0613','FCM0614','FCM0615','FCM0616','FCM0617',
                       'FCM0618','FCM0619','FCM0620','FCM0621','FCM0622','FCM0623','FCM0624','FCM0625','FCM0626','FCM0627',
                       'FCM0628','FCM0629','FCM0630','FCM0631','FCM0632','FCM0633','FCM0634','FCM0635','FCM0636','FCM0637',
                       'FCM0638','FCM0639','FCM0640','FCM0641','FCM0642','FCM0643','FCM0644','FCM0645','FCM0646','FCM0647',
                       'FCM0648','FCM0649','FCM0650','FCM0651','FCM0652','FCM0653','FCM0654','FCM0655','FCM0656','FCM0657',
                       'FCM0658','FCM0659','FCM0660','FCM0661','FCM0662','FCM0663','FCM0664','FCM0665','FCM0666','FCM0667',
                       'FCM0668','FCM0669','FCM0670','FCM0671','FCM0672','FCM0673','FCM0674','FCM0675','FCM0676','FCM0677',
                       'FCM0678','FCM0679','FCM0680','FCM0681','FCM0682','FCM0683','FCM0684','FCM0685','FCM0686','FCM0687',
                       'FCM0688','FCM0689','FCM0690','FCM0691','FCM0692','FCM0693','FCM0694','FCM0695','FCM0696','FCM0697',
                       'FCM0698','FCM0699','FCM0700','FCM0701','FCM0702','FCM0703','FCM0704','FCM0705','FCM0706','FCM0707',
                       'FCM0708','FCM0709','FCM0710','FCM0711','FCM0712','FCM0713','FCM0714','FCM0715','FCM0716','FCM0717',
                       'FCM0718','FCM0719','FCM0720','FCM0721','FCM0722','FCM0723','FCM0724','FCM0725','FCM0726','FCM0727',
                       'FCM0728','FCM0729','FCM0730','FCM0731','FCM0732','FCM0733','FCM0734','FCM0735','FCM0736','FCM0737',
                       'FCM0738','FCM0739','FCM0740','FCM0741','FCM0742','FCM0743','FCM0744','FCM0745','FCM0746','FCM0747',
                       'FCM0748','FCM0749','FCM0750','FCM0751','FCM0752','FCM0753','FCM0754','FCM0755','FCM0756','FCM0757',
                       'FCM0758','FCM0759','FCM0760','FCM0761','FCM0762','FCM0763','FCM0764','FCM0765','FCM0766','FCM0767',
                       'FCM0768','FCM0769','FCM0770','FCM0771','FCM0772','FCM0773','FCS0018','FCS0025','FCS0026','FCS0036',
                       'FCS0056','FCS0057','FCS0059','FCS0098','FCS0099','FCS0100','FCS0101','FCS0102','FCS0103','FCS0104',
                       'FCS0105','FCS0106','FCS0111','FCS0124','FCS0128','FCS0129','FCS0130','FCS0131','FCS0132','FCS0133',
                       'FCS0134','FCS0135','FCS0136','FCS0137','FCS0138','FCS0139','FCS0140','FCS0141','FCS0142','FCS0143',
                       'FCS0144','FCS0145','FCS0146','FCS0147','FCS0148','FCS0149','FCS0150','FCS0151','FCS0152','FCS0153',
                       'FCS0154','FCS0155','FCS0156','FCS0157','FCS0158','FCS0159','FCS0160','FCS0161','FCS0162','FCS0163',
                       'FCS0164','FCS0165','FCS0166']
            

            for i, n in enumerate(lst_COGE):
                out['Cd_FOR_COGE'] = n
                if i == 0:
                    tbl_FCOGE = out[['Cd_FOR_COGE','Nr_COGE','DT_INI','DT_FIM','DT_REF','FC']]
                else:
                    tbl_FCOGE = pd.concat([tbl_FCOGE, out[['Cd_FOR_COGE','Nr_COGE','DT_INI','DT_FIM','DT_REF','FC']]], ignore_index=True)

            tbl_FCOGE.to_sql("tbl_FCOGE",con, if_exists='replace',index=False)

    if st:
        avl.progress(10, "Importando SPED EFD ICMS, bloco C...")
    sql.configurar_sqlite_pragmas(con_efd, modo='leitura')
    
    SQLq = """
            SELECT 
                    *
            FROM BL_C t1  
           """
    BL_C = sql.imp_tbl_forma_000('BL_C', SQLq = SQLq, con = con_efd, st=st)
    if st: avl.progress(20, "Importando SPED EFD ICMS, bloco 0...")

    BL_Z = sql.imp_tbl_forma_000('BL_Z', 
                                  SQLq=f"""
                                            SELECT  t1.[1], t1.[2], t1.[3], t1.[4], t1.[5], t1.[6], t1.[7],
                                                    t1.[8], t1.[9], t1.[10], t1.[11], t1.[12], t1.[13]
                                            FROM BL_Z t1
                                            WHERE t1.[1] in ('0150','0200')
                                        """, 
                                  con = con_efd, st=st)
    
    if st: avl.progress(23, "Importando SPED EFD ICMS, bloco G110...")
    tabelas = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", con = con_efd)
    tabelas = tabelas['name'].tolist()
    cnpjs = [t.split('_')[-1] for t in tabelas if t.startswith('BLF_G110_')]
    cnpjs = sorted(set(cnpjs))
 
    if len(cnpjs)>0:
        SQLq = f"""
                SELECT *, {cnpjs[0]} as CNPJ_COMP
                FROM BLF_G110_{cnpjs[0]} 
                
                """
        if len(cnpjs)>1:
            for i, cnpj in enumerate(cnpjs):
                if (i>0) and sql.existe_tabela(f'BLF_G110_{cnpjs[0]}', con_efd):
                    SQLq += f""" UNION ALL
                            SELECT *, {cnpj} as CNPJ_COMP
                            FROM BLF_G110_{cnpj} 
                            """
        
        BLF_G110 = sql.imp_tbl_forma_000(f'BLF_G110_{cnpjs[0]}', 
                                         SQLq, 
                                         con = con_efd, st=st)
         
    if st: avl.progress(25, "Importando tabela com resultado do cálculo do financeiro de ICMS...")
        
    tbl_icms_fin = {}
    
    for i, cnpj in enumerate(cnpjs):
        tbl_icms_fin[i] = sql.imp_tbl_forma_000(f'tbl_icms_fin_{cnpj}', 
                                         con = con_efd, 
                                         st=st)
        
    if st: avl.progress(35, "Importando tabela do ROA...")
    if (not sql.existe_tabela("ResultadosROA", con)) or apr1:
        SQLq = """
                    WITH ResultadosROA AS (
                        SELECT
                            t1.COD_ITEM,
                            t1.Cd_NG,
                            t1.Nr_TUC,
                            t1.Nr_A1,
                            t1.Nr_A2,
                            t1.Nr_A3,
                            t1.Nr_A4,
                            t1.Nr_A5,
                            t1.Nr_A6,
                            SUM(CAST(REPLACE(t1.Qtd, ',', '.') AS REAL)) AS Qtd,
                            SUM(CAST(REPLACE(t1.VL_tot, ',', '.') AS REAL)) AS VL_TOT
                        FROM
                            ROA t1
                        WHERE
                            t1.dt_ARQ = ? 
                            AND t1.Cd_NG IN (1, 2)
                        GROUP BY
                            t1.COD_ITEM, t1.Cd_NG, t1.Nr_TUC, t1.Nr_A1, t1.Nr_A2, 
                            t1.Nr_A3, t1.Nr_A4, t1.Nr_A5, t1.Nr_A6
                    )
                    SELECT * FROM ResultadosROA WHERE Qtd>0 AND VL_TOT>0;
                """
        ROA = sql.imp_tbl_forma_001('ROA', SQLq, con = con, st=st, Empresa=Empresa)
        ROA.to_sql("ResultadosROA", con, if_exists='replace', index=False)
    else:
        ROA = pd.read_sql('SELECT * FROM ResultadosROA', con)
    if st: avl.progress(45, "Importando tabela do INCR...")

    INCR = sql.imp_tbl_forma_001('INCR', 
                                  SQLq=f"""
                                            SELECT  
                                                t1.Nr_TUC, t1.Nr_A1, t1.Nr_A2, t1.Nr_A3,
                                                t1.Nr_A4, t1.Nr_A5, t1.Nr_A6,
                                                t1.Cd_UAR, t1.COD_ITEM, t1.Txt_DESC_TECN, t1.Cd_TP_AVAL, 
                                                SUM(CAST(REPLACE(t1.Qtd_AIS, ',', '.') AS REAL)) AS Qtd
                                            FROM 
                                                INCR t1 
                                            WHERE 
                                                t1.dt_ARQ = ? 
                                            GROUP BY 
                                                t1.Nr_TUC, t1.Nr_A1, t1.Nr_A2, t1.Nr_A3,
                                                t1.Nr_A4, t1.Nr_A5, t1.Nr_A6,
                                                t1.Cd_UAR, t1.COD_ITEM, t1.Txt_DESC_TECN, 
                                                t1.Cd_TP_AVAL
                                        """, 
                                  con = con, st=st, Empresa=Empresa)    
    if len(INCR) == 0:
        if st.session_state.dt_fim <= date.today():
            if st: avl.progress(47, "Falhou INCR e não é intercalar...")
            if st:
                st.error('Falha ao importar o arquivo INCR da base local.')
                return None
            else:
                raise UserWarning('Falha ao importar o arquivo INCR da base local.')
        else:
            if st: avl.progress(47, "Buscando INCR por proxy...")
            SQLq = """
                    WITH
                    ROA_FILTRADA AS (
                        SELECT
                            Nr_TUC,
                            Nr_A1,
                            Nr_A2,
                            Nr_A3,
                            Nr_A4,
                            Nr_A5,
                            Nr_A6,
                            COD_ITEM,
                            TRY_CAST(REPLACE(Qtd, ',', '.') AS DOUBLE) AS Qtd
                        FROM origem.ROA
                        WHERE dt_ARQ = ?
                        AND Cd_NG IN (1, '1')
                        AND Nr_TUC IN (
                            '125', '160', '190', '210',
                            '255', '295', '310', '325',
                            '340', '345', '565', '570',
                            '575', '580'
                        )
                    ),
                    MATERIAIS AS (
                        SELECT
                            COD_ITEM,
                            DESCR_ITEM
                        FROM origem.LST_MAT
                        WHERE dt_ARQ = ?
                    ),
                    RESULTADOS AS (
                        SELECT
                            t1.Nr_TUC,
                            t1.Nr_A1,
                            t1.Nr_A2,
                            t1.Nr_A3,
                            t1.Nr_A4,
                            t1.Nr_A5,
                            t1.Nr_A6,
                            'NA' AS Cd_UAR,
                            t1.COD_ITEM,
                            t2.DESCR_ITEM AS Txt_DESC_TECN,
                            '2' AS Cd_TP_AVAL,
                            SUM(t1.Qtd) AS Qtd
                        FROM ROA_FILTRADA t1
                        INNER JOIN MATERIAIS t2
                            ON t1.COD_ITEM = t2.COD_ITEM
                        GROUP BY
                            t1.Nr_TUC,
                            t1.Nr_A1,
                            t1.Nr_A2,
                            t1.Nr_A3,
                            t1.Nr_A4,
                            t1.Nr_A5,
                            t1.Nr_A6,
                            t1.COD_ITEM,
                            t2.DESCR_ITEM
                    )
                    SELECT *
                    FROM RESULTADOS
                    WHERE Qtd > 0;
                """
            INCR = sql.imp_tbl_forma_002dk('ROA','LST_MAT', SQLq, con = con, st=st, Empresa=Empresa)

    if st: avl.progress(49, "Buscando tucagem do arquivo INCR...")
    LST_TUC = (
                    INCR[~((INCR['Nr_TUC'] == '135') & 
                        (INCR['Nr_A1'] == '2')) & (INCR['Nr_TUC'] != '265') & (INCR['Cd_UAR'] != 'UAR')].loc[
                        (INCR['Cd_TP_AVAL'] == '2') &
                        (INCR['COD_ITEM'].notnull()) &
                        (INCR['COD_ITEM'] != '0'),
                        ['COD_ITEM', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6']
                    ]
                    .drop_duplicates('COD_ITEM')
                )

    if st: avl.progress(50, "Importando tabela da lista de material...")
    LST_MAT = sql.imp_tbl_forma_001('LST_MAT', con = con, st=st, Empresa=Empresa)
    BP_EC = sql.imp_tbl_forma_001('BP_EC', con = con, st=st, Empresa=Empresa)
    
    for coluna in ['CNPJ_Forn','Cd_NCM']:
        BP_EC[coluna] = BP_EC[coluna].str.replace(r"[^a-zA-Z0-9,]", "", regex=True)
    
    if len(BP_EC[BP_EC.duplicated(keep=False)])>0:
        BP_EC[BP_EC[BP_EC.columns.to_list()[1:]].duplicated(keep=False)].to_csv(f'{dir_arq_saida}/TBL_EC_REP_{Empresa}.csv', 
              index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
        if st:
            registrar_artefato(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                file_path = rf'{dir_arq_saida}/TBL_EC_REP_{Empresa}.csv',
                                tipo_artefato = "SAIDA", 
                                calcular_hash = True)
    if st:  avl.progress(60, "Importando tabela com o valor de fábrica de avaliação...")
    BP_UAR = sql.imp_tbl_forma_001('BP_UAR', con = con, st=st, Empresa=Empresa)

    if len(BP_UAR) == 0:
        #Alternativa para intercalar
        SQLq = """
                WITH Resultados AS (
                    SELECT
                        t1.COD_ITEM,
                        t1.Nr_TUC,
                        t1.Nr_A1,
                        t1.Nr_A2,
                        t1.Nr_A3,
                        t1.Nr_A4,
                        t1.Nr_A5,
                        t1.Nr_A6,
                        SUM(CAST(REPLACE(t1.Qtd, ',', '.') AS REAL)) AS Qtd,
                        SUM(CAST(REPLACE(t1.VL_tot, ',', '.') AS REAL)) AS VL_VF,
                        0 AS VL_ICMS,
                        0 AS VL_ODC,
                        '' AS Nr_FORM
                    FROM
                        ROA t1
                    WHERE
                        t1.dt_ARQ = ?
                        AND t1.Cd_NG IN (1, '1')
                        AND t1.Nr_TUC IN ('125', '160', '190', '210', '255', '295', '310', '325', 
                                        '340', '345', '565', '570', '575', '580')
                    GROUP BY
                        t1.COD_ITEM,
                        t1.Nr_TUC,
                        t1.Nr_A1,
                        t1.Nr_A2,
                        t1.Nr_A3,
                        t1.Nr_A4,
                        t1.Nr_A5,
                        t1.Nr_A6
                        
                )
                SELECT * FROM Resultados WHERE Qtd>0;
            """
        BP_UAR = sql.imp_tbl_forma_001('ROA', SQLq, con = con, st=st, Empresa=Empresa)
        BP_UAR['VL_VF_UNIT_AT'] = np.where(BP_UAR['Qtd']>0,
                                           BP_UAR['VL_VF']/BP_UAR['Qtd'],
                                           BP_UAR['VL_VF'])
    if not ('COD_ITEM_DE' in BP_UAR.columns.to_list()):
        BP_UAR['COD_ITEM_DE']=BP_UAR['COD_ITEM']
    BP_UAR.loc[BP_UAR['COD_ITEM_DE'].isnull(), 'COD_ITEM_DE'] = BP_UAR.loc[BP_UAR['COD_ITEM_DE'].isnull(), 'COD_ITEM']       
    
    if st: avl.progress(65, "Importando tabela com o fluxo de pagamentos...")
    BPFP_UAR = sql.imp_tbl_forma_001('BPFP_UAR', con = con, st=st, Empresa=Empresa)    
    
    lst_BPR = BP_UAR['COD_ITEM'].drop_duplicates().to_list()
    BP_EC.loc[BP_EC['COD_ITEM'].isin(lst_BPR), 'Cd_NG'] = '1'

    if 'ALIQ_DIFAL' in BP_EC.columns:
        for nm in ['ALIQ_ICMS', 'ALIQ_ST', 'ALIQ_DIFAL', 'VL_TOT_LIQ', 'VL_TOT_IPI']:
            BP_EC[nm] = pd.to_numeric(BP_EC[nm].astype(str).str.replace(",","."), errors='coerce')
        base = (BP_EC['VL_TOT_LIQ'].fillna(0) + BP_EC['VL_TOT_IPI'].fillna(0))
        aliq_icms = BP_EC['ALIQ_ICMS'].fillna(0)
        aliq_st = BP_EC['ALIQ_ST'].fillna(0)
        aliq_difal = BP_EC['ALIQ_DIFAL'].fillna(0)
        denominador = aliq_icms + aliq_st + aliq_difal

        BP_EC['VL_DIFAL'] = np.where(
                                        denominador != 0,
                                        base * aliq_difal / denominador.replace(0, np.nan),
                                        0.0
                                    )
        BP_EC['VL_ST'] = np.where(
                                    denominador != 0,
                                    base * aliq_st / denominador.replace(0, np.nan),
                                    0.0
                                )
    dic = { nm : f'{nm[:2].upper()}{nm[2:]}' for nm in BP_EC.columns if nm.upper().startswith("VL")}
    BP_EC = BP_EC.rename(columns = dic)    

    # Vamos analisar se todas as NFe possuem dados no BPFP, caso não, geramos arquivo de alerta
    tst01 = BP_EC[['Id_Ext_CMP','Nr_NF','Nr_SerieNF','CNPJ_Forn','Dt_NF','Txt_Desc_Mat','FLG_BPR',
                   'VL_TOT_ICMS','VL_TOT_IPI','VL_TOT_LIQ','VL_DIFAL']].copy().drop_duplicates().sort_values(['Nr_NF','Nr_SerieNF','CNPJ_Forn','Dt_NF','Txt_Desc_Mat'])
    for nm in ['VL_TOT_ICMS','VL_TOT_IPI','VL_TOT_LIQ','VL_DIFAL']:
        tst01[nm] = pd.to_numeric(tst01[nm].astype(str).str.replace(",","."), errors='coerce').fillna(0)

    tst01["VL_TOT_ITEM"] = tst01["VL_TOT_ICMS"].fillna(0) + tst01["VL_TOT_IPI"].fillna(0) + tst01["VL_TOT_LIQ"].fillna(0) + tst01["VL_DIFAL"].fillna(0)
    tst01['VL_TOT_EC'] = (
                        tst01.groupby( ['Nr_NF', 'Nr_SerieNF', 'CNPJ_Forn', 'Dt_NF'],
                        dropna=False)['VL_TOT_ITEM'].transform('sum')
                        )
    
    tst02 = BPFP_UAR.copy()
    tst02['VL_Parcela'] = pd.to_numeric(tst02['VL_Parcela'].str.replace(",","."), errors='coerce').fillna(0)
    tst02 = tst02.groupby(['Id_Ext_CMP'], dropna=False).agg(
                                                                VL_TOT_Parcela=('VL_Parcela', "sum"),
                                                                QTD_Parcela=('VL_Parcela', "count")
                                                            ).reset_index()
    
    tst01['Id_Ext_CMP'] = tst01['Id_Ext_CMP'].astype(str)
    tst02['Id_Ext_CMP'] = tst02['Id_Ext_CMP'].astype(str)
    tst01 = tst01.merge(tst02, how = 'outer', on = ['Id_Ext_CMP'], suffixes=("_EC","_FlxPG"), indicator=True)
    dic_anl = {
                    'both':'NO',
                    'left_only' : 'foi encontrado apenas no EC',
                    'right_only' : 'foi encontrado apenas no fluxo de pagamentos'
              }
    

    tst01["OBS1"] = tst01["_merge"].replace(dic_anl)
    tst04 = tst01[['Nr_NF','Nr_SerieNF','CNPJ_Forn','Dt_NF','VL_TOT_Parcela','QTD_Parcela']].sort_values(by=['VL_TOT_Parcela'], ascending=False).drop_duplicates(subset=['Nr_NF','Nr_SerieNF','CNPJ_Forn','Dt_NF'], keep='first')
    chaves = ['Nr_NF','Nr_SerieNF','CNPJ_Forn','Dt_NF']
    colunas_preencher = ['VL_TOT_Parcela','QTD_Parcela']

    tst03 = tst01.merge(
                                tst04[chaves + colunas_preencher],
                                on=chaves,
                                how="left",
                                suffixes=("", "_B"),
                                validate="m:1"
                            )
    
    criterio = tst03['VL_TOT_Parcela'].isnull() & tst03[f"VL_TOT_Parcela_B"].notnull()
    tst03.loc[criterio, "OBS1"] = "NO"

    for coluna in colunas_preencher:
        tst03[coluna] = tst03[coluna].fillna(
                                                tst03[f"{coluna}_B"]
                                            )
    tst03 = tst03.drop(
                            columns=[f"{coluna}_B" for coluna in colunas_preencher]
                        )

    criterio = np.isclose(tst03["VL_TOT_Parcela"].fillna(0), tst03["VL_TOT_EC"].fillna(0), rtol=0.01)
    tst03['OBS2'] = 'diferença dentro da tolerância'
    tst03.loc[~criterio, "OBS2"] = 'diferença acima da tolerância, não confere fluxo de pagamentos com nota'
    tst03['OBS3'] = 'Pertence ao banco de compras'
    tst03.loc[tst01['FLG_BPR'].astype(str) == '0', 'OBS3'] = 'Não é empregado no banco de compras'
    
    cols = ["OBS3", "OBS2", "OBS1"]
    tst03["OBS_SFF"] = (
                        np.where(tst03["OBS1"] != "NO",
                                    tst03["OBS1"],
                                    np.where(tst03["OBS3"] != "Não é empregado no banco de compras",
                                            tst03[["OBS3","OBS2"]].replace("NO", "")
                                                                        .fillna("")
                                                                        .agg(", ".join, axis=1)
                                                                        .str.strip(", "),
                                            tst03["OBS3"]
                                            )
                                    )
                    )
    
    tst03 = tst03.drop(columns=["OBS3", "OBS2", "OBS1","_merge"])
    tst03.to_csv(f'{dir_arq_saida}/TBL_Fluxo_Pagamento_{Empresa}.csv', index=False, 
              sep="|", decimal=',', encoding="Latin-1", header = True)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/TBL_Fluxo_Pagamento_{Empresa}.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)

    try:    
        LST_CFOP = pd.read_csv('tabelas/tbl_CFOP.csv', sep="|",encoding="Latin-1", dtype=str)
    except:
        LST_CFOP = pd.DataFrame()

    if st: avl.progress(70, "Preparando Lista de Materiais do SPED...")

    sql.configurar_sqlite_pragmas(con, modo='escrita')
    df = BL_C.copy()

    df['Cd_NFe'] = np.where(df['1']== 'C100', 1, 0)
    df['Cd_NFe'] = df['Cd_NFe'].cumsum()

    df_C100 = df[df['1']=='C100'].copy()
    df_C170 = df[df['1']=='C170'].copy()

    
    col_names_C100=['IND_OPER','IND_EMIT','COD_PART','COD_MOD',
                    'COD_SIT','SER','NUM_DOC','CHV_NFE','DT_DOC',
                    'DT_E_S','VL_DOC','IND_PGTO','VL_DESC_NF','VL_ABAT_NT',
                    'VL_MERC','IND_FRT','VL_FRT','VL_SEG','VL_OUT_DA',
                    'VL_BC_ICMS_NF','VL_ICMS_NF','VL_BC_ICMS_ST_NF','VL_ICMS_ST_NF',
                    'VL_IPI_NF','VL_PIS_NF','VL_COFINS_NF','VL_PIS_ST_NF','VL_COFINS_ST_NF','Cd_NFe']

    col_names_C170=['NUM_ITEM','COD_ITEM_SPD','DESCR_COMPL','QTD',
                    'UNID','VL_ITEM','VL_DESC','IND_MOV','CST_ICMS',
                    'Cd_CFOP','COD_NAT','VL_BC_ICMS','ALIQ_ICMS','VL_ICMS',
                    'VL_BC_ICMS_ST','ALIQ_ST','VL_ICMS_ST','IND_APUR','CST_IPI',
                    'COD_ENQ','VL_BC_IPI','ALIQ_IPI','VL_IPI',
                    'CST_PIS','VL_BC_PIS','ALIQ_PIS','QUANT_BC_PIS','ALIQ_PIS_R$',
                    'VL_PIS','CST_COFINS','VL_BC_COFINS','ALIQ_COFINS','QUANT_BC_COFINS',
                    'ALIQ_COFINS_R$','VL_COFINS','COD_CTA','DATA','Nm_ARQ','Cd_NFe']


    try:
        df_C100 = df_C100.iloc[:, list(range(1, 29)) + [len(df_C100.columns) - 1]]
    except:
        df_C100 = df_C100.iloc[:, list(range(1, 29)) + [42]]
    df_C100.columns = col_names_C100

    try:
        df_C170 = df_C170.iloc[:, list(range(1, 37)) + [len(df_C170.columns) - 3, len(df_C170.columns) - 2, len(df_C170.columns) - 1]]
    except:
        df_C170 = df_C170.iloc[:, list(range(1, 37)) + [41, 42, 43]]
    df_C170.columns = col_names_C170

    df_0200 = BL_Z[BL_Z['1']=='0200'][['2','3','6','7','8','9','10','11','12','13']].copy()
    df_0200.columns=['COD_ITEM_SPD','DESCR_COMPL','UNID_INV_EFD','TIPO_ITEM_EFD',
                     'COD_NCM_EFD','EX_IPI_EFD','COD_GEN_EFD','COD_LST_EFD','ALIQ_ICMS_EFD','CEST_EFD']
    map_dic = {
                '00' : 'Mercadoria para Revenda',
                '01' : 'Matéria-prima',
                '02' : 'Embalagem',
                '03' : 'Produto em Processo',
                '04' : 'Produto Acabado',
                '05' : 'Subproduto',
                '06' : 'Produto Intermediário',
                '07' : 'Material de Uso e Consumo',
                '08' : 'Ativo Imobilizado',
                '09' : 'Serviços',
                '10' : 'Outros insumos',
                '99' : 'Outras'
            }
    df_0200['TIPO_ITEM_EFD'] = df_0200['TIPO_ITEM_EFD'].map(map_dic)
    df_0200 = df_0200.drop_duplicates(subset=['COD_ITEM_SPD'], keep='first')

    df_0200['COD_ITEM_SPD']=df_0200['COD_ITEM_SPD'].str.pad(25,side='left',fillchar='0')
    df_C170['COD_ITEM_SPD']=df_C170['COD_ITEM_SPD'].str.pad(25,side='left',fillchar='0')

    #arquivo gerado, para auxílio na conciliação das listas de materiais SPED vs ROA
    #vamos buscar os materiais declarados no SPED e vamos salvar a lista
    df = df_C170[['COD_ITEM_SPD']].drop_duplicates()
    df = df.merge(df_0200, how='left', on = 'COD_ITEM_SPD')
    df.to_csv(f'{dir_arq_saida}/TBL_MAT_SPED_{Empresa}.csv', index=False, 
              sep="|", decimal=',', encoding="Latin-1", header = True)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/TBL_MAT_SPED_{Empresa}.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    df.to_sql("TBL_MAT_SPED", con, if_exists='replace', index=False)
    df_0200.to_sql("df_0200", con, if_exists='replace', index=False)

    #vamos buscar os materiais declarados no ROA e vamos segregar entre COM e UC
    LST_ROA = ROA[['COD_ITEM', 'Cd_NG']].drop_duplicates()

    if st:
        avl.progress(75, "Preparando Lista de Materiais Empregados no Ativo Imobilizado do SPED...")

    #Lista CFOP de simples remessa
    LST_CFOP_SR = ['2552', '2557', '1552', '1557', '1916', '2916']
    # Lista de CFOP de investimento
    LST_CFOP_INV = ['1406', '1551', '1553', '1555', '2406', '2553', '2551', '2555']

    # Filtrando df_C170 e removendo duplicatas somente bens de ativo
    df = df_C170[['COD_ITEM_SPD']].drop_duplicates()
    df = df.merge(df_0200, how='left', on='COD_ITEM_SPD')
    # Ajustando formato de COD_ITEM_SPD em LST_MAT_SDI
    LST_MAT['COD_ITEM_SPD'] = LST_MAT['COD_ITEM_SPD'].str.zfill(25)

    # Merge com LST_MAT_SDI, LST_ROA_UC e LST_ROA_COM
    # Vou buscar entender se os materiais da lista estão no ROA e no SPED
    # A referência é SPED. Caso haja itens não usados no SPED fico sem COD_ITEM
    
    df2 = df.merge(LST_MAT, on='COD_ITEM_SPD', how='outer', suffixes=("","_MAT"), indicator=True)
    map_res = {
                'both' : 'NO',
                'left_only' : 'Somente EFD, verifique código',
                'right_only' : 'Somente ERP, verifique código',
              }
    df2['OBS_CONC_ERP_EFD'] = df2['_merge'].map(map_res)
    df2 = df2.drop(columns = '_merge')
    df2 = df2.merge(LST_ROA, on='COD_ITEM', how='outer', suffixes=("","_ROA_UC"), indicator=True)

    df2.loc[(df2['COD_ITEM'].notnull()) & (df2['COD_ITEM_SPD'].isnull()) & (df2['_merge'] == 'both'), 'OBS_CONC_ERP_ROA'] = 'Somente ERP, bem do ativo imobilizado, conciliado ROA'
    df2.loc[(df2['COD_ITEM'].notnull()) & (df2['COD_ITEM_SPD'].isnull()) & (df2['_merge'] == 'left_only'), 'OBS_CONC_ERP_ROA'] = 'Somente ERP, verifique código, bem de consumo? Ausente ROA'
    df2.loc[(df2['COD_ITEM'].notnull()) & (df2['COD_ITEM_SPD'].isnull()) & (df2['_merge'] == 'right_only'), 'OBS_CONC_ERP_ROA'] = 'Somente ROA, verifique código na lista de material'

    df2.loc[(df2['COD_ITEM'].notnull()) & (df2['COD_ITEM_SPD'].notnull()) & (df2['_merge'] == 'both'), 'OBS_CONC_ERP_ROA'] = 'NO'
    df2.loc[(df2['COD_ITEM'].notnull()) & (df2['COD_ITEM_SPD'].notnull()) & (df2['_merge'] == 'left_only'), 'OBS_CONC_ERP_ROA'] = 'No EFD e no ERP, verifique código, bem de consumo? Ausente ROA'
    df2.loc[(df2['COD_ITEM'].notnull()) & (df2['COD_ITEM_SPD'].notnull()) & (df2['_merge'] == 'right_only'), 'OBS_CONC_ERP_ROA'] = 'No EFD e no ROA, verifique código na lista de material'

    mask_efd_ativo = (df2['COD_ITEM'].isnull()) & (df2['COD_ITEM_SPD'].notnull()) & (df2['TIPO_ITEM_EFD'] == 'Ativo Imobilizado')
    df2.loc[mask_efd_ativo, 'OBS_CONC_ERP_ROA'] = 'Somente EFD, verifique código, pois parece ser ativo imobilizado, pode estar em ODC ou ODS'

    tipos_outros = [col for col in df2['TIPO_ITEM_EFD'].unique() if col != 'Ativo Imobilizado']

    for col in tipos_outros:
        mask_outros = (df2['COD_ITEM'].isnull()) & (df2['COD_ITEM_SPD'].notnull()) & (df2['TIPO_ITEM_EFD'] == col)
        df2.loc[mask_outros, 'OBS_CONC_ERP_ROA'] = f'Somente EFD, verifique código, {col}'
    df2 = df2.drop(columns = '_merge')

    # Sugiro ver com a empresa os casos em que não houve conciliação do ponto de vista do SPED, COD_ITEM NULO
    df2.to_csv(f'{dir_arq_saida}/TBL_MAT_SPED_NCeC_{Empresa}.csv', index=False, 
              sep="|", decimal=',', encoding="Latin-1", header = True)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/TBL_MAT_SPED_NCeC_{Empresa}.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    # Filtrando valores não nulos de COD_ITEM
    df3 = df2.copy()
    # Criando lst_MAT_VF
    lst_MAT_VF = df3[['COD_ITEM_SPD', 'COD_ITEM', 'Cd_NG']].drop_duplicates().copy()
    
    # Preenchemos os dados nulos com o valor da base recíproca
    lst_MAT_VF.loc[lst_MAT_VF['COD_ITEM'].isnull(), 'COD_ITEM'] = lst_MAT_VF.loc[lst_MAT_VF['COD_ITEM'].isnull(), 'COD_ITEM_SPD']
    lst_MAT_VF.loc[lst_MAT_VF['COD_ITEM_SPD'].isnull(), 'COD_ITEM_SPD'] = lst_MAT_VF.loc[lst_MAT_VF['COD_ITEM_SPD'].isnull(), 'COD_ITEM']
    lst_MAT_VF['COD_ITEM_SPD'] = lst_MAT_VF['COD_ITEM_SPD'].fillna('0').str.zfill(25)

    lst_MAT_VF.to_csv(f'{dir_arq_saida}/TBL_MAT_ATIVOS_SPED_{Empresa}.csv', index=False, 
              sep="|", decimal=',', encoding="Latin-1", header = True)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/TBL_MAT_ATIVOS_SPED_{Empresa}.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    lst_MAT_VF.to_sql("TBL_MAT_ATIVOS_SPED", con, if_exists='replace', index=False)
    df_C170['COD_ITEM_SPD'] = df_C170['COD_ITEM_SPD'].str.pad(25,side='left',fillchar='0')
    # Caso haja conciliação teremos como fazer o de-para ROA. Caso não, será irreduntante o passo
    
    LST_ITENS_SPED_VF = df_C170.merge(lst_MAT_VF, on='COD_ITEM_SPD', how='inner')
    
    dd = LST_ITENS_SPED_VF[['Cd_NFe']].drop_duplicates()

    LST_NF_SPED_VF = df_C100.merge(dd, on='Cd_NFe', how='inner')
    LST_NF_SPED_VF = LST_NF_SPED_VF.merge(LST_ITENS_SPED_VF, on='Cd_NFe', how='inner')
    LST_NF_SPED_VF = LST_NF_SPED_VF.fillna(0)
    # Definição de colunas numéricas e de data
    cols_numericas = {
                        'IND_OPER', 'IND_EMIT', 'COD_MOD', 'VL_DOC', 'IND_PGTO', 'VL_DESC_NF', 
                        'VL_ABAT_NT', 'VL_MERC', 'IND_FRT', 'VL_FRT', 'VL_SEG', 'VL_OUT_DA',
                        'VL_BC_ICMS_NF', 'VL_ICMS_NF', 'VL_BC_ICMS_ST_NF', 'VL_ICMS_ST_NF', 
                        'VL_IPI_NF', 'VL_PIS_NF', 'VL_COFINS_NF', 'VL_PIS_ST_NF', 'VL_COFINS_ST_NF',
                        'QTD', 'VL_ITEM', 'VL_DESC', 'IND_MOV', 'CST_ICMS', 
                        'VL_BC_ICMS', 'ALIQ_ICMS', 'VL_ICMS', 'VL_BC_ICMS_ST', 'ALIQ_ST', 
                        'VL_ICMS_ST', 'IND_APUR', 'CST_IPI', 'COD_ENQ', 'VL_BC_IPI', 'ALIQ_IPI', 
                        'VL_IPI', 'CST_PIS', 'VL_BC_PIS', 'ALIQ_PIS', 'QUANT_BC_PIS', 
                        'ALIQ_PIS_R$', 'VL_PIS', 'CST_COFINS', 'VL_BC_COFINS', 'ALIQ_COFINS', 
                        'QUANT_BC_COFINS', 'ALIQ_COFINS_R$', 'VL_COFINS'
                    }

    cols_datas = {'DT_DOC', 'DT_E_S'}

    # Convertendo colunas numéricas
    for col in cols_numericas & set(LST_NF_SPED_VF.columns):
        if LST_NF_SPED_VF[col].dtype == 'object':
            LST_NF_SPED_VF[col] = pd.to_numeric(
                LST_NF_SPED_VF[col].astype(str).str.replace(',', '.'), errors='coerce'
            )
        if col in ['ALIQ_ICMS', 'ALIQ_IPI', 'ALIQ_PIS', 'ALIQ_COFINS']:
            LST_NF_SPED_VF.loc[LST_NF_SPED_VF[col] > 1, col] =LST_NF_SPED_VF.loc[LST_NF_SPED_VF[col] > 1, col] / 100
    
    # Convertendo colunas de data
    for col in cols_datas & set(LST_NF_SPED_VF.columns):
        if LST_NF_SPED_VF[col].dtype == 'object':
            LST_NF_SPED_VF[col] = pd.to_datetime(
                LST_NF_SPED_VF[col], format='%d%m%Y', errors='coerce'
            ).dt.date

    # Buscando dados das empresas fornecedoras
    BL_0150f = (
                    BL_Z.loc[BL_Z['1'] == '0150', ['2', '3', '5']]
                    .drop_duplicates(subset='2')
                    .rename(columns={'2': 'COD_PART', '3': 'Nm_EMP', '5': 'CNPJ'})
                    .sort_values(by='COD_PART', ascending=True)
                )

    #Nesse teste, observamos se os itens que estão no ROA estão ou não na lista de materiais entregue e nas NFe de entrada dos
    #arquivos SPED.
    #Lista material SPED
    cols = ['COD_PART', 'COD_SIT', 'SER','NUM_DOC', 'CHV_NFE', 'DT_DOC', 'DT_E_S', 'VL_DOC', 'IND_PGTO',
            'VL_DESC_NF', 'VL_ABAT_NT', 'VL_MERC', 'IND_FRT', 'VL_FRT', 'VL_SEG','VL_OUT_DA','VL_ICMS_ST_NF','COD_ITEM_SPD',
            'DESCR_COMPL', 'QTD', 'UNID', 'VL_ITEM', 'VL_DESC', 'IND_MOV','CST_ICMS', 'Cd_CFOP','ALIQ_ICMS','CST_IPI',
            'VL_BC_IPI', 'ALIQ_IPI', 'VL_IPI', 'CST_PIS', 'CST_COFINS', 'NUM_ITEM','COD_ITEM','Cd_NG']
    
    # LADO EFD feito:
    
    LST_NF_SPED_VFa = LST_NF_SPED_VF[cols].merge(BL_0150f, on='COD_PART', how='left')

    LST_MAT_SPED = LST_NF_SPED_VFa[['COD_ITEM_SPD','DESCR_COMPL']].drop_duplicates(subset='COD_ITEM_SPD', keep='first').rename(columns={'COD_ITEM_SPD':'COD_ITEM'})

    TST_04 = (
                ROA.loc[ROA['Cd_NG'].isin(['1','2']), ['COD_ITEM', 'Cd_NG', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3',
                                            'Nr_A4', 'Nr_A5', 'Nr_A6']]
                .sort_values(by=['COD_ITEM', 'Cd_NG'])
                .drop_duplicates(subset=['COD_ITEM'], keep='first')
            )
    
    TST_04 = TST_04.merge(LST_MAT, on = 'COD_ITEM', how = 'left')

    with st.spinner("Fazendo correlação de descrição entre SPED e Lista Material"):
        df_cmp = compara_materiais(LST_MAT_SPED, 
                        TST_04, 
                        "DESCR_COMPL",
                        "DESCR_ITEM",
                        top_k=3,
                        st=st)

    dds_df2 = TST_04[["COD_ITEM", "DESCR_ITEM"]].drop_duplicates()
    df_cmp["COD_ITEM_LST_MAT_ESP"] = df_cmp["IDX_MATCH"].map(dds_df2["COD_ITEM"])
    df_cmp["DESCR_ITEM_LST_MAT_ESP"] = df_cmp["IDX_MATCH"].map(dds_df2["DESCR_ITEM"])

    TST_04 = TST_04.merge(df_cmp[["COD_ITEM", "DESCR_COMPL","COD_ITEM_LST_MAT_ESP","DESCR_ITEM_LST_MAT_ESP","CLASSE_MATCH","SCORE_SIM"]], 
                        left_on = 'COD_ITEM', 
                        right_on = 'COD_ITEM_LST_MAT_ESP',
                        how='outer', 
                        suffixes=("_LST_MAT","_CMP_EMB"), indicator=True)

    
    ROAint = ROA.groupby(by='COD_ITEM', dropna=False)[['Qtd','VL_TOT']].sum().reset_index()
    TST_04 = TST_04.merge(ROAint,
                        left_on = 'COD_ITEM_LST_MAT_ESP', 
                        right_on = 'COD_ITEM',
                        how='left')
    
    
    TST_04 = TST_04.drop(columns=['COD_ITEM','_merge'])
    TST_04 = TST_04.sort_values(by=['COD_ITEM_LST_MAT','SCORE_SIM'])
    TST_04['Pnd_VL'] = np.log1p(TST_04['VL_TOT'].abs()) / np.log(10)
    TST_04['Pnd_NG'] = np.where(
                                    TST_04['Cd_NG']=='1',
                                    10,
                                    1
                                )
    TST_04['Pnd_NG'] = TST_04['Pnd_NG'].fillna(0)
    TST_04['Pnd_CONC'] = np.where(
                                    TST_04['CLASSE_MATCH']=='PROVAVEL',
                                    0,
                                    np.where(
                                                TST_04['CLASSE_MATCH']=='NEBULOSO',
                                                0.5,
                                                1
                                            )
                                )
    TST_04['FLG_BPR'] = 0
    TSTint = INCR[(INCR['Cd_TP_AVAL'].astype(str) == '2') & (INCR['Cd_UAR']=='UC')].copy()
    lst_UC = TSTint['COD_ITEM'].drop_duplicates().to_list()
    TST_04.loc[TST_04['COD_ITEM_LST_MAT_ESP'].isin(lst_UC), 'FLG_BPR'] = 1
    TST_04['Pnd_BPR'] = np.where(
                                    TST_04['FLG_BPR']==1,
                                    2,
                                    1
                                )
    TST_04['Fator_Risco'] = TST_04['Pnd_VL'] * 0.1 + TST_04['Pnd_NG'] * TST_04['Pnd_BPR'] + TST_04['Pnd_CONC']
    TSTint = TST_04.groupby(by='COD_ITEM_LST_MAT_ESP', dropna=False)[['DESCR_ITEM_LST_MAT_ESP']].count().reset_index().rename(columns={'DESCR_ITEM_LST_MAT_ESP' : 'Qtd_CONC'})
    TST_04 = TST_04.merge(TSTint,
                        on = 'COD_ITEM_LST_MAT_ESP',
                        how='left')
    TST_04['Qtd_CONC'] = np.where(
                                    TST_04['Cd_NG']=='1',
                                    TST_04['Qtd_CONC'],
                                    0
                                )

    TSTint = TST_04.groupby('COD_ITEM_LST_MAT_ESP')['Cd_NG'].nunique().reset_index().rename(columns={'Cd_NG':'FLG_NG'})
    TST_04 = TST_04.merge(TSTint,
                        on = 'COD_ITEM_LST_MAT_ESP',
                        how='left')
    TST_04.loc[TST_04['FLG_NG'].isnull(), 'FLG_NG'] = np.where(
                                                                TST_04[TST_04['FLG_NG'].isnull()]['Cd_NG'].astype(str)=='1',
                                                                1.,
                                                                0.
                                                            )
    #Caso a empresa não preencha o código SPED apresentar a conciliação a seguir.
    TST_04['TST_CONC_LST_MAT'] = 'NO'
    TST_04.loc[(TST_04['FLG_NG']>1) & 
            (TST_04['Fator_Risco']>=20), 'TST_CONC_LST_MAT'] = 'CRITICO, MATERIAL EMPREGADO COMO COM E UC/UAR'
    TST_04.loc[(TST_04['FLG_NG']>1) & 
            (TST_04['TST_CONC_LST_MAT'] == 'NO'), 'TST_CONC_LST_MAT'] = 'MATERIAL EMPREGADO COMO COM E UC/UAR'
    TST_04.loc[(TST_04['TST_CONC_LST_MAT'] == 'NO') & (TST_04['CLASSE_MATCH'] == 'PROVAVEL') &
            (TST_04['Fator_Risco']>=20), 'TST_CONC_LST_MAT'] = 'CRÍTICO, PEDIR PARA EMPRESA PREENCHER O COD_ITEM_SPD EM LST_MAT'
    TST_04.loc[(TST_04['TST_CONC_LST_MAT'] == 'NO') & (TST_04['CLASSE_MATCH'] == 'PROVAVEL') & 
            (TST_04['Fator_Risco']>0), 'TST_CONC_LST_MAT'] = 'NÃO CRÍTICO, PEDIR PARA EMPRESA PREENCHER O COD_ITEM_SPD EM LST_MAT'
    TST_04.loc[(TST_04['CLASSE_MATCH'] != 'PROVAVEL') & (TST_04['Fator_Risco']>=20) &
            (TST_04['Cd_NG'].isin(['1','2'])), 
            'TST_CONC_LST_MAT'] = 'CRITICO, POUCO PROVAVEL QUE A CONCILIAÇÂO ESTEJA CORRETA'
    TST_04.loc[(TST_04['CLASSE_MATCH'] != 'PROVAVEL') & (TST_04['Fator_Risco']> 0) &
            (TST_04['Cd_NG'].isin(['1','2'])), 
            'TST_CONC_LST_MAT'] = 'NÃO CRITICO, POUCO PROVAVEL QUE A CONCILIAÇÂO ESTEJA CORRETA'
    TST_04.loc[TST_04['COD_ITEM_LST_MAT'].notnull() & TST_04['VL_TOT'].isnull() &
            (TST_04['FLG_BPR']==0), 'TST_CONC_LST_MAT'] = 'NÃO CRITICO, COM, VERIFICAR SE ESTÁ NO ROA'
    TST_04.loc[(TST_04['COD_ITEM_LST_MAT'].notnull()) & TST_04['VL_TOT'].isnull() &
            (TST_04['FLG_BPR']==0), 
            'TST_CONC_LST_MAT'] = 'NÃO CRITICO, COM, VERIFICAR SE ESTÁ NO ROA'
    TST_04.loc[(TST_04['COD_ITEM_LST_MAT'].notnull()) & TST_04['VL_TOT'].isnull() &
            (TST_04['FLG_BPR']==1), 
            'TST_CONC_LST_MAT'] = 'CRITICO, UC/UAR, VERIFICAR SE ESTÁ NO ROA'
    TST_04 = TST_04.drop(columns=['FLG_NG'])
    TST_04.to_sql("TST_04", con, if_exists='replace', index=False)

    # restringindo ao período incremental, somente com CFOP investimento.

    LST_NF_SPED_VFa = LST_NF_SPED_VFa.loc[(LST_NF_SPED_VFa['DT_DOC'] >= dt_ini_proc)
                        & (LST_NF_SPED_VFa['DT_DOC'] <= dt_fim_proc)]
    
    if st: avl.progress(80, "Preparando dados do extrato de compras e do SPED para comparação...")

    # O processo anterior costuma não apresentar resultados satisfatórios, pois há divergências de códigos
    # Assim, faremos conciliação do extrato de compras com o SPED
    # adequando nome de alguns campos.
    BP_EC_CONC = BP_EC.copy()

    BP_EC_CONC = BP_EC_CONC.rename(columns = {'CNPJ_Forn':'CNPJ', 'Nr_SerieNF':'SER', 
                                              'Nr_NF':'NUM_DOC','Nr_Item_NF':'NUM_ITEM', 
                                              'Cd_NFe':'CHV_NFE', 'Qtd':'QTD', 
                                              'VL_TOT_LIQ':'VL_ITEM' })
    
    LST_NF_SPED_VFa['CHV_NFE'] = LST_NF_SPED_VFa['CHV_NFE'].astype(str).str.slice(0, 44)

    
    BP_EC_CONC['CHV_NFE'] = BP_EC_CONC['CHV_NFE'].astype(str).str.slice(0, 44)
    BP_EC_CONC['QTD'] = pd.to_numeric(BP_EC_CONC['QTD'].astype(str), errors='coerce')
    BP_EC_CONC['VL_ITEM'] = pd.to_numeric(BP_EC_CONC['VL_ITEM'].astype(str).str.replace(",","."), errors='coerce')
    BP_EC_CONC['VL_TOT_ICMS'] = pd.to_numeric(BP_EC_CONC['VL_TOT_ICMS'].astype(str).str.replace(",","."), errors='coerce')
    BP_EC_CONC['VL_TOT_IPI'] = pd.to_numeric(BP_EC_CONC['VL_TOT_IPI'].astype(str).str.replace(",","."), errors='coerce')
    BP_EC_CONC['VL_ST'] = pd.to_numeric(BP_EC_CONC['VL_ST'].astype(str).str.replace(",","."), errors='coerce')

    campos_efd = LST_NF_SPED_VFa.columns.to_list()
    campos_erp = BP_EC_CONC.columns.to_list()

    def pad(x, n):
        return x.zfill(n)
    
    BP_EC_CONC.columns = BP_EC_CONC.columns.str.replace('\ufeff', '').str.replace('ï»¿','')

    base_ec = BP_EC_CONC[['Id_Ext_CMP','CHV_NFE','CNPJ','SER','NUM_DOC','Dt_NF','Cd_CFOP']].copy()
    base_ec["aamm"] = pd.to_datetime(base_ec["Dt_NF"], format="mixed").dt.strftime("%y%m")
    base_ec["mod"] = '55'
    for col, tam in [("aamm", 4), ("CNPJ", 14), ("SER", 3), ("NUM_DOC", 9)]:
        base_ec[col] = base_ec[col].fillna('0').map(lambda x: pad(x, tam))

    base_efd =LST_NF_SPED_VFa[['CHV_NFE']].drop_duplicates().copy()
    base_efd["chave_limpa"] = base_efd['CHV_NFE'].astype(str).str.replace(r"\D", "", regex=True)
    base_efd = base_efd[base_efd["chave_limpa"].str.len() == 44].copy()
    base_efd["aamm"]  = base_efd["chave_limpa"].str.slice(2, 6)
    base_efd["CNPJ"]  = base_efd["chave_limpa"].str.slice(6, 20)
    base_efd["mod"]   = base_efd["chave_limpa"].str.slice(20, 22)
    base_efd["SER"] = base_efd["chave_limpa"].str.slice(22, 25)
    base_efd["NUM_DOC"]   = base_efd["chave_limpa"].str.slice(25, 34)

    base_cmp = base_ec.merge(base_efd, how='outer', on =["aamm","CNPJ","mod","SER","NUM_DOC"], indicator=True, suffixes=("_EC","_EFD"))
    map_res = {
                    'both' : 'Possível candidata a chave',
                    'left_only' : 'Pelos dados infomados no ERP não há correlação possível, verifique',
                    'right_only' : 'Pelos dados do EFD, não foi possível encontrar candidatos no ERP, verifique',
                }
    base_cmp['IND_CONC'] = base_cmp['_merge'].replace(map_res)
    base_cmp = base_cmp.drop(columns='_merge')
    base_cmp.to_csv(f"{dir_arq_saida}/TBL_BSC_CHVS_NFe.csv", index=False, sep="|", decimal=',', encoding="Latin-1")
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/TBL_BSC_CHVS_NFe.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    dec = 2
    tol = 0.01
    BP_EC_CONC['FLG_AMBOS'] = False
    BP_EC_CONC['FLG_MATCH'] = False
    BP_EC_CONC['FLG_ANOMALIA'] = False
    BP_EC_CONC['FLG_NFe_CMP'] = False
    LST_NF_SPED_VFa['FLG_USADO'] = False
    LST_NF_SPED_VFa['FLG_NFe_CMP'] = False
    BP_EC_CONC['TIPO_MATCH'] = None
    LST_NF_SPED_VFa = LST_NF_SPED_VFa.drop_duplicates(subset=['CHV_NFE', 'NUM_ITEM'])
    
    nfe = BP_EC_CONC['CHV_NFE'].drop_duplicates().to_list()
    #nfe = ['35210953224127000584550030002734451542737978']

    def chv_ax(valor1 = None, valor2 = None, unidade = None):
        ax = [str(nm) for nm in [valor1, valor2, unidade] if nm is not None]
        return f"|".join(ax)
    
    # Esta condicional é para quando testamos cálculos
    if apr1 or not sql.existe_tabela('TBL_LST_NF_SPED_VFa', con):
        bar_con_item = st.progress(0, f"Aplicando regras de conciliação 0/{len(nfe)}...")
        for ic, chv in enumerate(nfe):
            bar_con_item.progress(int(100*ic/len(nfe)), f"Aplicando regras de conciliação {ic}/{len(nfe)}...")
            erp_nf = BP_EC_CONC.loc[BP_EC_CONC['CHV_NFE'] == chv].copy()
            efd_nf = LST_NF_SPED_VFa.loc[(LST_NF_SPED_VFa['CHV_NFE'] == chv) & (~LST_NF_SPED_VFa['FLG_USADO'])].copy()

            efd_map = {}
            efd_map1 = {}
            efd_map2 = {}
            efd_map3 = {}
            efd_map4 = {}
            match = False

            for r in efd_nf.itertuples():
                if (
                        str(r.COD_SIT).zfill(2) == '06'
                        
                    ):
                    key = chv_ax(0, round(r.VL_ITEM, dec), r.UNID)
                    key1 = chv_ax(0, round(r.VL_ITEM, dec))
                    key2 = chv_ax(0, r.UNID)
                    key3 = chv_ax(0)
                    key4 = chv_ax(round(r.VL_ITEM, dec))
                    
                else:
                    key = chv_ax(round(r.QTD, dec), round(r.VL_ITEM, dec), r.UNID)
                    key1 = chv_ax(round(r.QTD, dec), round(r.VL_ITEM, dec))
                    key2 = chv_ax(round(r.QTD, dec), r.UNID)
                    key3 = chv_ax(round(r.QTD, dec))
                    key4 = chv_ax(round(r.VL_ITEM, dec))

                efd_map.setdefault(key, []).append(r.Index)
                efd_map1.setdefault(key1, []).append(r.Index)
                efd_map2.setdefault(key2, []).append(r.Index)
                efd_map3.setdefault(key3, []).append(r.Index)
                efd_map4.setdefault(key4, []).append(r.Index)

            for r in erp_nf.itertuples():
                keys = [
                            chv_ax(round(r.QTD, dec), round(r.VL_ITEM, dec), r.Cd_Unid),
                            chv_ax(round(r.QTD, dec), round(r.VL_ITEM + r.VL_TOT_ICMS + r.VL_ST, dec), r.Cd_Unid),
                            chv_ax(round(r.QTD, dec), round(r.VL_ITEM + r.VL_TOT_ICMS + r.VL_ST + r.VL_TOT_IPI, dec), r.Cd_Unid),
                            chv_ax(round(r.QTD, dec), round(r.VL_ITEM + r.VL_TOT_ICMS + r.VL_TOT_IPI, dec), r.Cd_Unid),
                            chv_ax(round(r.QTD, dec), round(r.VL_ITEM + r.VL_TOT_ICMS, dec), r.Cd_Unid),
                        ]
                
                for idf, key in enumerate(keys, start=1):
                    if (key) in efd_map and efd_map[(key)]:
                        idx_efd = efd_map[(key)].pop(0)
                        for c in campos_efd:
                            col_dest = c if c not in campos_erp else f"{c}_EFD"
                            BP_EC_CONC.at[r.Index, col_dest] = LST_NF_SPED_VFa.at[idx_efd, c]

                        BP_EC_CONC.at[r.Index, 'FLG_MATCH'] = True
                        LST_NF_SPED_VFa.at[idx_efd, 'FLG_USADO'] = True
                        BP_EC_CONC.at[r.Index, 'TIPO_MATCH'] = f'REGRA_{idf}'
                        match = True
                        if str(LST_NF_SPED_VFa.at[idx_efd, 'COD_SIT']).zfill(2) == '06':
                            BP_EC_CONC.at[idx_efd, 'FLG_NFe_CMP'] = True
                            LST_NF_SPED_VFa.at[idx_efd, 'FLG_NFe_CMP'] = True
                        break

                if not match:
                   keys = [
                            chv_ax(round(r.QTD, dec), round(r.VL_ITEM, dec)),
                            chv_ax(round(r.QTD, dec), round(r.VL_ITEM + r.VL_TOT_ICMS + r.VL_ST, dec)),
                            chv_ax(round(r.QTD, dec), round(r.VL_ITEM + r.VL_TOT_ICMS + r.VL_ST + r.VL_TOT_IPI, dec)),
                            chv_ax(round(r.QTD, dec), round(r.VL_ITEM + r.VL_TOT_ICMS + r.VL_TOT_IPI, dec)),
                            chv_ax(round(r.QTD, dec), round(r.VL_ITEM + r.VL_TOT_ICMS, dec)),
                        ]
                   
                   for idf, key in enumerate(keys, start=1):
                       if (key) in efd_map1 and efd_map1[(key)]:
                           idx_efd = efd_map1[(key)].pop(0)
                           for c in campos_efd:
                               col_dest = c if c not in campos_erp else f"{c}_EFD"
                               BP_EC_CONC.at[r.Index, col_dest] = LST_NF_SPED_VFa.at[idx_efd, c]

                           BP_EC_CONC.at[r.Index, 'FLG_MATCH'] = True
                           LST_NF_SPED_VFa.at[idx_efd, 'FLG_USADO'] = True
                           BP_EC_CONC.at[r.Index, 'TIPO_MATCH'] = f'REGRA_{idf}_sem_unidade'
                           match = True
                           if str(LST_NF_SPED_VFa.at[idx_efd, 'COD_SIT']).zfill(2) == '06':
                               BP_EC_CONC.at[idx_efd, 'FLG_NFe_CMP'] = True
                               LST_NF_SPED_VFa.at[idx_efd, 'FLG_NFe_CMP'] = True
                           break 
                                
                if not match:
                    keys = [
                            chv_ax(round(r.QTD, dec), r.Cd_Unid),
                           ]
                    # Chave quantidade key2, quantidade e unidade
                    for idf, key in enumerate(keys, start=1):
                        if (key) in efd_map2 and efd_map2[(key)]:
                            idx_efd = efd_map2[(key)].pop(0)
                            for c in campos_efd:
                                col_dest = c if c not in campos_erp else f"{c}_EFD"
                                BP_EC_CONC.at[r.Index, col_dest] = LST_NF_SPED_VFa.at[idx_efd, c]

                            BP_EC_CONC.at[r.Index, 'FLG_MATCH'] = True
                            LST_NF_SPED_VFa.at[idx_efd, 'FLG_USADO'] = True
                            BP_EC_CONC.at[r.Index, 'TIPO_MATCH'] = f'REGRA_QTD_COM_UND'
                            match = True
                            if str(LST_NF_SPED_VFa.at[idx_efd, 'COD_SIT']).zfill(2) == '06':
                                BP_EC_CONC.at[idx_efd, 'FLG_NFe_CMP'] = True
                                LST_NF_SPED_VFa.at[idx_efd, 'FLG_NFe_CMP'] = True
                            break
                if not match:
                    keys = [
                            chv_ax(round(r.QTD, dec)),
                           ]
                    # Chave quantidade key2, somente quantidade
                    for idf, key in enumerate(keys, start=1):
                        if (key) in efd_map3 and efd_map3[(key)]:
                            idx_efd = efd_map3[(key)].pop(0)
                            for c in campos_efd:
                                col_dest = c if c not in campos_erp else f"{c}_EFD"
                                BP_EC_CONC.at[r.Index, col_dest] = LST_NF_SPED_VFa.at[idx_efd, c]

                            BP_EC_CONC.at[r.Index, 'FLG_MATCH'] = True
                            LST_NF_SPED_VFa.at[idx_efd, 'FLG_USADO'] = True
                            BP_EC_CONC.at[r.Index, 'TIPO_MATCH'] = f'REGRA_QTD_SEM_UND'
                            match = True
                            if str(LST_NF_SPED_VFa.at[idx_efd, 'COD_SIT']).zfill(2) == '06':
                                BP_EC_CONC.at[idx_efd, 'FLG_NFe_CMP'] = True
                                LST_NF_SPED_VFa.at[idx_efd, 'FLG_NFe_CMP'] = True
                            break
                if not match:
                    keys = [
                            chv_ax(round(r.VL_ITEM, dec)),
                            chv_ax(round(r.VL_ITEM + r.VL_TOT_ICMS + r.VL_ST, dec)),
                            chv_ax(round(r.VL_ITEM + r.VL_TOT_ICMS + r.VL_ST + r.VL_TOT_IPI, dec)),
                            chv_ax(round(r.VL_ITEM + r.VL_TOT_ICMS + r.VL_TOT_IPI, dec)),
                            chv_ax(round(r.VL_ITEM + r.VL_TOT_IPI, dec)),
                        ]
                    # Chave valor key4, somente valor
                    for idf, key in enumerate(keys, start=1):
                        if (key) in efd_map4 and efd_map4[(key)]:
                            idx_efd = efd_map4[(key)].pop(0)
                            for c in campos_efd:
                                col_dest = c if c not in campos_erp else f"{c}_EFD"
                                BP_EC_CONC.at[r.Index, col_dest] = LST_NF_SPED_VFa.at[idx_efd, c]

                            BP_EC_CONC.at[r.Index, 'FLG_MATCH'] = True
                            LST_NF_SPED_VFa.at[idx_efd, 'FLG_USADO'] = True
                            BP_EC_CONC.at[r.Index, 'TIPO_MATCH'] = f'REGRA_{idf}_VALOR'
                            match = True
                            if str(LST_NF_SPED_VFa.at[idx_efd, 'COD_SIT']).zfill(2) == '06':
                                BP_EC_CONC.at[idx_efd, 'FLG_NFe_CMP'] = True
                                LST_NF_SPED_VFa.at[idx_efd, 'FLG_NFe_CMP'] = True
                            break
                if not match:
                    BP_EC_CONC.at[r.Index, 'FLG_ANOMALIA'] = True

        #Queremos que as NFe presentes no EFD não conciliadas apareçam no BP_EC_CONC
        bar_con_item.empty()
        df_origem = LST_NF_SPED_VFa.loc[
                                        LST_NF_SPED_VFa["FLG_USADO"] == False,
                                        campos_efd
                                        ].copy()
        mapa_nomes = {
                        c: f"{c}_EFD"
                        for c in campos_efd
                        if c in campos_erp
                    }
        df_origem = df_origem.rename(columns=mapa_nomes)
        BP_EC_CONC = pd.concat(
                                    [BP_EC_CONC, df_origem],
                                    ignore_index=True
                                )

        
        LST_CFOP_INV = ['406', '551', '553', '555', '933']
        LST_CFOP_SR = ['552', '557', '916', '916'] 
        LST_CFOP_COM = ['908','909','910','911','912','913','914','917','918','919']
        
        BP_EC_CONC['Cd_CFOP'] = (
                                    BP_EC_CONC['Cd_CFOP']
                                    .astype(str)
                                    .str.replace(",", "")
                                    .str.replace(".", "")
                                    .str.zfill(4)
                                )
        BP_EC_CONC['Cd_CFOP_PREF'] = BP_EC_CONC['Cd_CFOP'].astype(str).str[0]
        BP_EC_CONC['Cd_CFOP_SUF'] = BP_EC_CONC['Cd_CFOP'].astype(str).str[1:]
        BP_EC_CONC["FLG_INTER_ESTADUAL"] = BP_EC_CONC['Cd_CFOP_PREF'].isin(["2", "6"])
        BP_EC_CONC["FLG_INTERNACIONAL"] = BP_EC_CONC['Cd_CFOP_PREF'].isin(["3", "7"])

        BP_EC_CONC["Prob_DIFAL"] = np.select(
                                                [
                                                    (BP_EC_CONC["FLG_INTER_ESTADUAL"]) &
                                                    (BP_EC_CONC['Cd_CFOP_PREF'].isin(["2", "6"]))
                                                ],
                                                ["ALTA"],
                                                default="ZERO"
                                            )

        BP_EC_CONC.loc[BP_EC_CONC["FLG_INTERNACIONAL"], "Prob_DIFAL"] = "ZERO"

        mask_cfop = BP_EC_CONC['Cd_CFOP'].str.match(r"^\d4\d{2}$", na=False)
        mask_cst = BP_EC_CONC['CST_ICMS'].isin(['10','60','70','53','201','202','203','500'])

        BP_EC_CONC['flag_ST'] = (mask_cfop | mask_cst).astype(int)
        ncm_estatisca = (
                            BP_EC_CONC
                            .assign(NCM4=BP_EC_CONC['Cd_NCM'].astype(str).str[:4])
                            .groupby('NCM4')
                            .agg(
                                freq_ST=('flag_ST', 'mean'),
                                volume=('flag_ST', 'count')
                            )
                        )
        NCM_ST_auto = ncm_estatisca[
                                    (ncm_estatisca['freq_ST'] > 0.8) & (ncm_estatisca['volume'] > 30)
                                ].index
        mask_ncm_auto = (
                            BP_EC_CONC['Cd_NCM'].astype(str).str[:4].isin(NCM_ST_auto)
                        )
        BP_EC_CONC['Prob_ST'] = 'ZERO'
        BP_EC_CONC.loc[mask_cfop | mask_cst | mask_ncm_auto, 'Prob_ST'] = 'ALTA'

        BP_EC_CONC = BP_EC_CONC.drop(columns=['flag_ST'])
        BP_EC_CONC["VL_ST"] = pd.to_numeric(BP_EC_CONC["VL_ST"].astype(str).replace(",","."), errors="coerce").fillna(0)
        BP_EC_CONC["VL_DIFAL"] = pd.to_numeric(BP_EC_CONC["VL_DIFAL"].astype(str).replace(",","."), errors="coerce").fillna(0)
        if "Vl_II" in BP_EC_CONC.columns:
            BP_EC_CONC = BP_EC_CONC.rename(columns = {"Vl_BC" : "VL_BC", "Vl_II" : "VL_II", "Vl_IOF" : "VL_IOF", "Vl_Desp_ADU" : "VL_Desp_ADU",})
        BP_EC_CONC["VL_II"] = pd.to_numeric(BP_EC_CONC["VL_II"].astype(str).replace(",","."), errors="coerce").fillna(0)
        BP_EC_CONC["VL_Desp_ADU"] = pd.to_numeric(BP_EC_CONC["VL_Desp_ADU"].astype(str).replace(",","."), errors="coerce").fillna(0)
        BP_EC_CONC["VL_IOF"] = pd.to_numeric(BP_EC_CONC["VL_IOF"].astype(str).replace(",","."), errors="coerce").fillna(0)
        
        for cmp in ['ST', 'DIFAL']:
            mask_zero = (BP_EC_CONC[f'Prob_{cmp}'] == 'ZERO')
            mask_VL = (BP_EC_CONC[f'VL_{cmp}'] != 0)
            cond1 = (~mask_zero) & (~mask_VL)
            cond2 = mask_zero & mask_VL
            
            BP_EC_CONC[f"OBS_SFF_{cmp}"] = np.select(
                                                        [cond1, cond2],
                                                        [
                                                            f"Esperava-se ter, critério CFOP, CST e NCM estatístico, mas não existe VL_{cmp}, avalie particularidade",
                                                            f"Esperava-se não ter, critério CFOP, CST e NCM estatístico, mas existe VL_{cmp}, avalie particularidade"
                                                        ],
                                                        default=f"NO"
                                                    )
        BP_EC_CONC[f"OBS_SFF_IMP"] = np.where(
                                                BP_EC_CONC[f'FLG_INTERNACIONAL'] & ((BP_EC_CONC[f'VL_II'] +
                                                                                    BP_EC_CONC[f'VL_Desp_ADU'] +
                                                                                    BP_EC_CONC[f'VL_IOF']) == 0),
                                                "Possivelmente, existe despesas de importação, avalie",
                                                "NO"
                                            )
        BP_EC_CONC[f"OBS_SFF_IMP"] = np.where(
                                                ~BP_EC_CONC[f'FLG_INTERNACIONAL'] & ((BP_EC_CONC[f'VL_II'] +
                                                                                    BP_EC_CONC[f'VL_Desp_ADU'] +
                                                                                    BP_EC_CONC[f'VL_IOF']) != 0),
                                                "Possivelmente, inexiste despesas de importação, dado o CFOP, avalie",
                                                "NO"
                                            )

        BP_EC_CONC['RES_CONC'] = 'NO'
        BP_EC_CONC.loc['RES_CONC'] = 'NO'
        
        BP_EC_CONC['FLG_DIFAL'] = (np.where((BP_EC_CONC['Cd_CFOP_PREF'] == '2') & 
                                            (BP_EC_CONC['Cd_CFOP_SUF'].isin(LST_CFOP_INV)), 1, 0))
        
        # É possível ter em ambo e não ter conciliado
        chv_nfe_efd_clean = BP_EC_CONC['CHV_NFE_EFD'].dropna().unique()
        chv_nfe_bp_clean = BP_EC_CONC['CHV_NFE'].dropna().unique()
        BP_EC_CONC['FLG_AMBOS_EFD'] = BP_EC_CONC['CHV_NFE'].isin(chv_nfe_efd_clean)
        BP_EC_CONC['FLG_AMBOS_BP'] = BP_EC_CONC['CHV_NFE_EFD'].isin(chv_nfe_bp_clean)
        BP_EC_CONC['FLG_AMBOS'] = BP_EC_CONC['FLG_AMBOS_EFD'] | BP_EC_CONC['FLG_AMBOS_BP']
        BP_EC_CONC.drop(['FLG_AMBOS_EFD', 'FLG_AMBOS_BP'], axis=1, inplace=True)

        BP_EC_CONC['SIT_CONC'] = "NO"
        BP_EC_CONC.loc[(BP_EC_CONC['Id_Ext_CMP'].notnull()) &
                       (BP_EC_CONC['CHV_NFE'].isnull()), 'SIT_CONC'] = "SOMENTE ERP"
        BP_EC_CONC.loc[(BP_EC_CONC['Id_Ext_CMP'].notnull()) &
                       (~BP_EC_CONC['FLG_AMBOS']) &
                        (BP_EC_CONC['SIT_CONC'] == 'NO'), 'SIT_CONC'] = "SOMENTE ERP"
        BP_EC_CONC.loc[(BP_EC_CONC['Id_Ext_CMP'].isnull()) &
                    (~BP_EC_CONC['FLG_AMBOS']) &
                    (BP_EC_CONC['SIT_CONC'] == 'NO'), 'SIT_CONC'] = "SOMENTE EFD"

        BP_EC_CONC['QTD'] = pd.to_numeric(BP_EC_CONC["QTD"].astype(str).str.replace(',', '.'), errors="coerce").fillna(0)
        BP_EC_CONC['QTD_EFD'] = pd.to_numeric(BP_EC_CONC["QTD_EFD"].astype(str).str.replace(',', '.'), errors="coerce").fillna(0)
        BP_EC_CONC['VL_TOT_ICMS'] = pd.to_numeric(BP_EC_CONC["VL_TOT_ICMS"].astype(str).str.replace(',', '.'), errors="coerce").fillna(0)
        BP_EC_CONC['VL_TOT_IPI'] = pd.to_numeric(BP_EC_CONC["VL_TOT_IPI"].astype(str).str.replace(',', '.'), errors="coerce").fillna(0)
        BP_EC_CONC['VL_ST'] = pd.to_numeric(BP_EC_CONC["VL_ST"].astype(str).str.replace(',', '.'), errors="coerce").fillna(0)
        BP_EC_CONC['VL_ITEM'] = pd.to_numeric(BP_EC_CONC["VL_ITEM"].astype(str).str.replace(',', '.'), errors="coerce").fillna(0)
        BP_EC_CONC['VL_ITEM_EFD'] = pd.to_numeric(BP_EC_CONC["VL_ITEM_EFD"].astype(str).str.replace(',', '.'), errors="coerce").fillna(0)
        BP_EC_CONC['VL_IPI'] = pd.to_numeric(BP_EC_CONC["VL_IPI"].astype(str).str.replace(',', '.'), errors="coerce").fillna(0)

        BP_EC_CONC['DIV_QTD'] = round(BP_EC_CONC['QTD'].abs() - BP_EC_CONC['QTD_EFD'].abs(), dec)
        
        cols = [
                    'VL_ITEM_EFD', 'VL_ITEM', 'VL_TOT_ICMS',
                    'VL_ST', 'VL_TOT_IPI', 'VL_IPI'
                ]

        BP_EC_CONC[cols] = BP_EC_CONC[cols].apply(pd.to_numeric, errors='coerce').fillna(0)

        calc = pd.DataFrame(index=BP_EC_CONC.index)

        calc['DIV_VL_1'] = (
                                BP_EC_CONC['VL_ITEM_EFD'].abs()
                                - BP_EC_CONC['VL_ITEM'].abs()
                                - BP_EC_CONC['VL_TOT_ICMS'].abs()
                                - BP_EC_CONC['VL_ST'].abs()
                                - BP_EC_CONC['VL_TOT_IPI'].abs()
                            ).round(dec)

        calc['DIV_VL_2'] = (
                                BP_EC_CONC['VL_ITEM_EFD'].abs()
                                - BP_EC_CONC['VL_ITEM'].abs()
                                - BP_EC_CONC['VL_TOT_ICMS'].abs()
                                - BP_EC_CONC['VL_TOT_IPI'].abs()
                            ).round(dec)

        calc['DIV_VL_3'] = (
                                BP_EC_CONC['VL_ITEM_EFD'].abs()
                                + BP_EC_CONC['VL_IPI'].abs()
                                - BP_EC_CONC['VL_ST'].abs()
                                - BP_EC_CONC['VL_ITEM'].abs()
                                - BP_EC_CONC['VL_TOT_ICMS'].abs()
                                - BP_EC_CONC['VL_TOT_IPI'].abs()
                            ).round(dec)

        calc['DIV_VL_4'] = (
                                BP_EC_CONC['VL_ITEM_EFD'].abs()
                                + BP_EC_CONC['VL_IPI'].abs()
                                - BP_EC_CONC['VL_ITEM'].abs()
                                - BP_EC_CONC['VL_TOT_ICMS'].abs()
                                - BP_EC_CONC['VL_TOT_IPI'].abs()
                            ).round(dec)

        BP_EC_CONC['DIV_VL'] = calc.abs().min(axis=1)
        idx_menor = calc.abs().to_numpy().argmin(axis=1)

        BP_EC_CONC['DIV_VL'] = calc.to_numpy()[
                                                    range(len(calc)),
                                                    idx_menor
                                                ]
        
        BP_EC_CONC['FORMULA_DIV_VL'] = calc.columns[idx_menor]

        BP_EC_CONC.loc[(BP_EC_CONC['FLG_AMBOS']) &
                    (BP_EC_CONC['DIV_QTD'].abs() > tol) &
                    (BP_EC_CONC['DIV_VL'].abs() > tol) &
                    (BP_EC_CONC['SIT_CONC'] == 'NO'), 'SIT_CONC'] = "Conciliada, mas com diferença em valor e quantidade"
        
        BP_EC_CONC.loc[(BP_EC_CONC['FLG_AMBOS']) &
                    (BP_EC_CONC['DIV_QTD'].abs()> tol) &
                    (BP_EC_CONC['DIV_VL'].abs() <= tol) &
                    (BP_EC_CONC['SIT_CONC'] == 'NO') &
                    (BP_EC_CONC['TIPO_MATCH'].str[:7]!="REGRA_Q"), 'SIT_CONC'] = "Conciliada, mas com diferença em quantidade"
        
        BP_EC_CONC['DIV_VL_PERC'] = (
                                        BP_EC_CONC['DIV_VL'].abs() /
                                        BP_EC_CONC['VL_ITEM_EFD'].abs()
                                    ).replace([np.inf, -np.inf], np.nan).fillna(0)
        
        mask1 = (
                            BP_EC_CONC['FLG_AMBOS']
                            & (BP_EC_CONC['DIV_QTD'].abs() <= tol)
                            & (BP_EC_CONC['DIV_VL_PERC'] > tol)
                            & (BP_EC_CONC['SIT_CONC'] == 'NO')
                        )
        dic_formula = {
                            'DIV_VL_1': 'VL_EFD - VL_Item - VL_ICMS - VL_ST - VL_IPI',
                            'DIV_VL_2': 'VL_EFD - VL_Item - VL_ICMS - VL_IPI',
                            'DIV_VL_3': 'VL_EFD + VL_IPI - VL_ST - VL_Item - VL_ICMS - VL_IPI',
                            'DIV_VL_4': 'VL_EFD + VL_IPI - VL_Item - VL_ICMS - VL_IPI'
                        }

        BP_EC_CONC['FORMULA_DIV_VL'] = (
                                            BP_EC_CONC['FORMULA_DIV_VL']
                                            .map(dic_formula)
                                            .fillna(BP_EC_CONC['FORMULA_DIV_VL'])
                                        )

        BP_EC_CONC.loc[mask1, 'SIT_CONC'] = (
                                                "Conciliada, mas com diferença em valor - "
                                                + BP_EC_CONC.loc[mask1, 'FORMULA_DIV_VL'].astype(str)
                                            )
        
        BP_EC_CONC.loc[(BP_EC_CONC['FLG_AMBOS']) & (BP_EC_CONC['TIPO_MATCH'].isnull()) &
                    (BP_EC_CONC['QTD_EFD'].abs() <= tol) &
                    (BP_EC_CONC['VL_ITEM_EFD'].abs() <= tol), 
                    'SIT_CONC'] = "SOMENTE ERP"
        
        BP_EC_CONC.loc[(BP_EC_CONC['FLG_AMBOS']) & (BP_EC_CONC['TIPO_MATCH'].isnull()) &
                    (BP_EC_CONC['QTD'].abs() <= tol) &
                    (BP_EC_CONC['VL_ITEM'].abs() <= tol), 
                    'SIT_CONC'] = "SOMENTE EFD"
        
        BP_EC_CONC.loc[(BP_EC_CONC['SIT_CONC'] == "NO") & (BP_EC_CONC['TIPO_MATCH'].str.contains('sem_unidade')), 
                      'SIT_CONC'] = "CONCILIADO, PORÉM JUSTIFIQUE UNIDADES"
        
        mapa_pesos = {
                        'NO': 0,
                        'SOMENTE ERP': 10,
                        'SOMENTE EFD': 10,
                        'Conciliada, mas com diferença em valor e quantidade': 8,
                        'Conciliada, mas com diferença em valor': 6,
                        'Conciliada, mas com diferença em quantidade': 6
                    }
        BP_EC_CONC['Peso_SIT_CONC'] = BP_EC_CONC['SIT_CONC'].map(mapa_pesos).fillna(0)
        BP_EC_CONC.loc[BP_EC_CONC['Id_Ext_CMP'].isnull(), 'Cd_CFOP_SUF'] = BP_EC_CONC.loc[BP_EC_CONC['Id_Ext_CMP'].isnull(), 'Cd_CFOP_EFD'].str[1:]
        condicoes = [
                        BP_EC_CONC['Cd_CFOP_SUF'].isin(LST_CFOP_INV)
                    ]
        escolhas = [3.0]
        BP_EC_CONC['Peso_CFOP'] = np.select(condicoes, escolhas, default=1.0)
        BP_EC_CONC['Peso_Materialidade'] = np.log1p(BP_EC_CONC['DIV_VL'].abs()) / np.log(10)

        BP_EC_CONC['Fator_Risco'] = round(BP_EC_CONC['Peso_CFOP'] * BP_EC_CONC['Peso_SIT_CONC'] + (BP_EC_CONC['Peso_Materialidade']), dec)
        BP_EC_CONC['Cd_Estrato'] = np.select(
                                    [
                                        (BP_EC_CONC['Cd_CFOP_SUF'].isin(LST_CFOP_INV)) & (BP_EC_CONC['Fator_Risco'] > 20),
                                        (BP_EC_CONC['Cd_CFOP_SUF'].isin(LST_CFOP_INV)) & (BP_EC_CONC['Fator_Risco'] > 10),
                                        (~BP_EC_CONC['Cd_CFOP_SUF'].isin(LST_CFOP_INV)) & (BP_EC_CONC['Fator_Risco'] > 5),
                                        (BP_EC_CONC['SIT_CONC'] == 'NO'),
                                        (BP_EC_CONC['FLG_TP'].astype(str) == '0'),
                                        BP_EC_CONC['Cd_CFOP_SUF'].isin(LST_CFOP_SR),
                                        BP_EC_CONC['Cd_CFOP_SUF'].isin(LST_CFOP_COM),
                                        (BP_EC_CONC['FLG_TPNF'].astype(str) == '0')
                                    ],
                                    ['1-CRITICO', '2-ALTO', '3-BAIXO', '4-CONCILIADO','5-REFORMA','6-Simples Remessa','7-Demais',
                                     '8-Nota Complementar'],
                                    default='9-RESIDUAL'
                                )

        probs = {'1-CRITICO': 0.7, '2-ALTO': 0.20, '3-BAIXO': 0.025, '4-CONCILIADO': 0.00, '9-RESIDUAL': 0.025, 
                 '5-REFORMA': 0.00, '6-Simples Remessa':0.00, '7-Demais':0.00, '8-Nota Complementar': 0.05}
        df['Prob_amostra'] = BP_EC_CONC['Cd_Estrato'].map(probs)

        # Definição da amostra
        df_pop = BP_EC_CONC.loc[
                                (BP_EC_CONC["SIT_CONC"] != 'NO') &
                                (BP_EC_CONC["Fator_Risco"] > 0)
                            ].copy()
        df_pop['CHV_NFE_AGR'] = df_pop["CHV_NFE"].replace("", np.nan).combine_first(df_pop["CHV_NFE_EFD"].replace("", np.nan))
        df_pop = df_pop[['CHV_NFE_AGR','Cd_Estrato','Fator_Risco']]

        idx = (
                    df_pop
                    .groupby('CHV_NFE_AGR', dropna=False)['Fator_Risco']
                    .idxmax()
                )

        df_pop = df_pop.loc[idx].reset_index(drop=True)
        amostra_alto = df_pop.loc[
                                    df_pop["Cd_Estrato"] == "1-CRITICO"
                                ].copy()
        df_medio = df_pop.loc[df_pop["Cd_Estrato"] == "2-ALTO"].copy()
        if len(df_medio)>0:
            n_medio = int(len(df_medio) * 0.20)
            amostra_medio = df_medio.sample(
                                                n=n_medio,
                                                weights=df_medio["Fator_Risco"],
                                                random_state=42
                                            )
        else:
            amostra_medio = df_medio
        df_baixo = df_pop.loc[df_pop["Cd_Estrato"] == "3-RESIDUAL"].copy()
        if len(df_baixo)>0:
            n_baixo = max(1, int(len(df_baixo) * 0.05))
            amostra_baixo = df_baixo.sample(
                                                n=n_baixo,
                                                weights=df_baixo["Fator_Risco"].abs(),
                                                random_state=42
                                            )
        else:
            amostra_baixo = df_baixo
        amostra_final = pd.concat(
                                        [amostra_alto, amostra_medio, amostra_baixo],
                                        ignore_index=True
                                )
        
        # IPI, análise
        df_tipi = pd.read_csv(r"tabelas\tbl_tipi.csv", 
                 sep='|', 
                 names=['Cd_NCM','Cd_EXTIPI','Txt_Descr_NCM','ALIQ_IPI_TIPI'],
                 header=0,
                 usecols=[0, 1, 2, 3],
                 index_col=False, 
                 encoding='latin-1')
        df_tipi['Cd_NCM'] = df_tipi['Cd_NCM'].str.replace('.', '', regex=False).str.strip()
        df_tipi['ALIQ_IPI_TIPI'] = df_tipi['ALIQ_IPI_TIPI'].str.strip()
        df_tipi['Pct_IPI_TIPI'] = df_tipi['ALIQ_IPI_TIPI'].str.replace("NT","0").fillna('0').str.replace(",",".").astype(float)/100
        df_tipi['Cd_EXTIPI'] = np.where(df_tipi['Cd_EXTIPI'].notnull(),
                                    df_tipi['Cd_EXTIPI'],
                                    '0')
        df_tipi = df_tipi.drop_duplicates(subset=['Cd_NCM','Cd_EXTIPI'])
        BP_EC_CONC['Cd_EXTIPI'] = BP_EC_CONC['Cd_EXTIPI'].fillna("0")
        BP_EC_CONC = BP_EC_CONC.merge(df_tipi, how = 'left', on = ['Cd_NCM','Cd_EXTIPI'])

        crit1 = ( 
                    (BP_EC_CONC['CST_IPI'] == "01") & 
                    (BP_EC_CONC['ALIQ_IPI'].str.replace("NO","0").fillna('0').str.replace(",",".").astype(float) != 0.)
                )
        crit2 = ( 
                    (BP_EC_CONC['CST_IPI'] == "02") & 
                    (BP_EC_CONC['ALIQ_IPI'].str.replace("NO","0").fillna('0').str.replace(",",".").astype(float) != 0.)
                )
        crit3 = ( 
                    (BP_EC_CONC['CST_IPI'] == "03") & 
                    (BP_EC_CONC['ALIQ_IPI'].str.replace("NO","0").fillna('0').str.replace(",",".").astype(float) != 0.)
                )
        crit4 = ( 
                    (BP_EC_CONC['CST_IPI'] == "04") & 
                    (BP_EC_CONC['ALIQ_IPI'].str.replace("NO","0").fillna('0').str.replace(",",".").astype(float) != 0.)
                )
        crit5 = ( 
                    (BP_EC_CONC['CST_IPI'] == "05") & 
                    (BP_EC_CONC['ALIQ_IPI'].str.replace("NO","0").fillna('0').str.replace(",",".").astype(float) != 0.)
                )
        
        crit6 = ( 
                    (BP_EC_CONC['CST_IPI'].isin(["00","49"])) & 
                    (BP_EC_CONC['ALIQ_IPI'].str.replace("NO","0").fillna('0').str.replace(",",".").astype(float) != 0.) &
                    (BP_EC_CONC['Pct_IPI_TIPI'] == 0.)
                )
        crit7 = ( 
                    (BP_EC_CONC['CST_IPI'].isin(["00","49"])) & 
                    (BP_EC_CONC['ALIQ_IPI'].str.replace("NO","0").fillna('0').str.replace(",",".").astype(float) == 0.) &
                    (BP_EC_CONC['Pct_IPI_TIPI'] != 0.)
                )
        crit8 = ( 
                    (BP_EC_CONC['CST_IPI'].isin(["00","49"])) & 
                    (BP_EC_CONC['ALIQ_IPI'].str.replace("NO","0").fillna('0').str.replace(",",".").astype(float) != 0.) &
                    (BP_EC_CONC['Pct_IPI_TIPI'] != 0.) & 
                    (((BP_EC_CONC['ALIQ_IPI'].str.replace("NO","0").fillna('0').str.replace(",",".").astype(float)) -
                    (BP_EC_CONC['Pct_IPI_TIPI'])).abs() > .01)
                )

        BP_EC_CONC['OBS_IPI_TIPI'] = "NO"
        BP_EC_CONC.loc[crit1, 'OBS_IPI_TIPI'] = 'Rever, entrada tributada com alíquota zero'
        BP_EC_CONC.loc[crit2, 'OBS_IPI_TIPI'] = 'Rever, entrada isenta'
        BP_EC_CONC.loc[crit3, 'OBS_IPI_TIPI'] = 'Rever, entrada não-tributada (Ex: produtos "NT" na TIPI)'
        BP_EC_CONC.loc[crit4, 'OBS_IPI_TIPI'] = 'Rever, entrada imune'
        BP_EC_CONC.loc[crit5, 'OBS_IPI_TIPI'] = 'Rever, entrada com suspensão'
        BP_EC_CONC.loc[crit6, 'OBS_IPI_TIPI'] = 'Rever, deveria ser zero pela TIPI'
        BP_EC_CONC.loc[crit7, 'OBS_IPI_TIPI'] = 'Rever, indicar regra tributária para isenção'
        BP_EC_CONC.loc[crit8, 'OBS_IPI_TIPI'] = 'Rever, indicar motivo de divergência de alíqutas IPI'
        
        LST_NF_SPED_VFa.to_sql('TBL_LST_NF_SPED_VFa', con, if_exists='replace', index=False)
        #st.write(BP_EC_CONC[BP_EC_CONC['CHV_NFE']=='35251123153291000153550000000087721716837624'])
        BP_EC_CONC.to_sql('TBL_BP_EC_CONC', con, if_exists='replace', index=False)
        LST_NF_SPED_VFa.to_csv(f"{dir_arq_saida}/TBL_SPED_dados.csv", index=False, sep="|", decimal=',', encoding="Latin-1")
        BP_EC_CONC.to_csv(f"{dir_arq_saida}/TBL_EC_dados.csv", index=False, sep="|", decimal=',', encoding="Latin-1")
        if st:
            registrar_artefato(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                file_path = rf'{dir_arq_saida}/TBL_SPED_dados.csv',
                                tipo_artefato = "SAIDA", 
                                calcular_hash = True)
            registrar_artefato(st.session_state.database_MAN, 
                                            st.session_state.execucao_id, 
                                            file_path = rf'{dir_arq_saida}/TBL_EC_dados.csv',
                                            tipo_artefato = "SAIDA", 
                                            calcular_hash = True)
        if len(amostra_final)>0:
            amostra_final.to_sql('TBL_AMOSTRAS_NFe', con, if_exists='replace', index=False)
            amostra_final.to_csv(f"{dir_arq_saida}/Amostra_NFe.csv", index=False, sep="|", decimal=',', encoding="Latin-1")
            if st:
                registrar_artefato(st.session_state.database_MAN, 
                                    st.session_state.execucao_id, 
                                    file_path = rf'{dir_arq_saida}/Amostra_NFe.csv',
                                    tipo_artefato = "SAIDA", 
                                    calcular_hash = True)
    else:
        LST_NF_SPED_VFa = pd.read_sql('SELECT * FROM TBL_LST_NF_SPED_VFa', con)
        BP_EC_CONC = pd.read_sql('SELECT * FROM TBL_BP_EC_CONC', con)
        BP_EC_CONC = BP_EC_CONC.drop(columns='FLG_BPR')
        BP_EC_CONC = BP_EC_CONC.merge(BP_EC[['Id_Ext_CMP', 'FLG_BPR']], how='left', on = 'Id_Ext_CMP')
    
    #st.write(BP_EC_CONC[BP_EC_CONC['CHV_NFE']=='35251004856422000114550000000337701524258610'])
    #st.write(BP_EC_CONC[BP_EC_CONC['CHV_NFE']=='35210953224127000584550030002734451542737978'])
    #raise
    #Sintese
    erp_nf = BP_EC_CONC.groupby('CHV_NFE', dropna=False).agg(
                                            qtd_erp=('QTD', 'sum'),
                                            vl_icms = ('VL_TOT_ICMS', 'sum'),
                                            vl_ipi = ('VL_TOT_IPI', 'sum'),
                                            vl_erp=('VL_ITEM', 'sum')
                                        ).reset_index()

    efd_nf = (BP_EC_CONC
              .groupby('CHV_NFE_EFD', dropna=False).agg(
                                                            qtd_efd=('QTD_EFD', 'sum'),
                                                            vl_efd=('VL_ITEM_EFD', 'sum')
                                                        )
              .reset_index()
              .rename(columns = {'CHV_NFE_EFD':'CHV_NFE'}))
    
    conc_nf = erp_nf.merge(
                            efd_nf,
                            on='CHV_NFE',
                            how='outer',
                            indicator=True
                        )
    
    conc_nf['VL_ERP_TOT'] = conc_nf['vl_erp'].round(2)
    conc_nf['VL_EFD_TOT'] = conc_nf['vl_efd'].round(2)
    conc_nf['TST_GLB_QTD'] = "DIV"
    conc_nf['TST_GLB_VL'] = "DIV"
    conc_nf['TST_GLB'] = "DIV"
    conc_nf.loc[
                    (conc_nf['qtd_efd'].abs() - conc_nf['qtd_erp'].abs()).abs()/conc_nf[['qtd_erp', 'qtd_efd']].abs().max(axis=1) < 0.1,
                    'TST_GLB_QTD'
                ] = 'OK'
    masc_vl = (
                    conc_nf['vl_efd'].notna() &
                    conc_nf['vl_erp'].notna() &
                    (conc_nf['vl_efd'].abs() - conc_nf['vl_erp'].abs()).abs()/conc_nf[['vl_erp', 'vl_efd']].abs().max(axis=1) < 1
                )
    conc_nf.loc[masc_vl, 'TST_GLB_VL'] = 'OK'

    masc_vl_imp = (
                    (
                        conc_nf['vl_efd'].abs() -
                        (
                            conc_nf['vl_erp'].abs() +
                            conc_nf['vl_icms'].abs() +
                            conc_nf['vl_ipi'].abs()
                        )
                    ).abs() < 1
                )

    conc_nf.loc[masc_vl_imp, 'TST_GLB_VL'] = 'OK'
    conc_nf.loc[masc_vl_imp, 'VL_ERP_TOT'] = (
                                                conc_nf['vl_erp'].abs() +
                                                conc_nf['vl_icms'].abs() +
                                                conc_nf['vl_ipi'].abs()
                                              ).abs().round(2)

    masc_vl_imp1 = (
                    (
                        conc_nf['vl_efd'].abs() -
                        (
                            conc_nf['vl_erp'].abs() +
                            conc_nf['vl_icms'].abs()
                        )
                    ).abs() < 1
                )

    conc_nf.loc[masc_vl_imp1, 'TST_GLB_VL'] = 'OK'
    conc_nf.loc[
                    (conc_nf['TST_GLB_QTD'] == 'OK') &
                    (conc_nf['TST_GLB_VL'] == 'OK'),
                    'TST_GLB'
                ] = 'OK'
    conc_nf.loc[masc_vl_imp1, 'VL_ERP_TOT'] = (
                                                conc_nf['vl_erp'].abs() +
                                                conc_nf['vl_icms'].abs()
                                              ).abs().round(2)

    conc_nf.to_sql('LST_NFe_CONC', con, if_exists='replace', index=False)

    LST_ITENS_CORR = BP_EC_CONC[BP_EC_CONC['Id_Ext_CMP'].notnull() & (BP_EC_CONC['FLG_MATCH']==1) & (BP_EC_CONC['FLG_ANOMALIA']==0)].copy()
    LST_ITENS_CORR = LST_ITENS_CORR.drop_duplicates(subset=['Id_Ext_CMP'], keep='first')

    LST_ITENS_NCORR_EC = BP_EC_CONC[BP_EC_CONC['Id_Ext_CMP'].notnull() & BP_EC_CONC['FLG_MATCH']==0].copy()
    LST_ITENS_NCORR = LST_NF_SPED_VFa[LST_NF_SPED_VFa['FLG_USADO']==0].copy()

    LST_ITENS_NCORR.to_sql('LST_ITENS_NCORR', con, if_exists='replace', index=False)
    LST_ITENS_CORR.to_sql('LST_ITENS_CORR', con, if_exists='replace', index=False)
    LST_ITENS_NCORR_EC.to_sql('LST_ITENS_NCORR_EC', con, if_exists='replace', index=False)

    if st: avl.progress(84, "Testando itens do BP_EC...")

    """
    Vamos criar arquivo de alertas sobre os dados informados pela empresa; são testes simples 
    de consistência, que devem ser observados. Caso a empresa não tenha informado um dado 
    relevante será gerado um alerta para que forneça. Caso a empresa informe
    não ter esse dado, deve ser requerida todas as notas de entrada (de ativos e não ativos) 
    para o período incremental, no formato XML, para que a SFF produza uma base 
    comparativa de dados a partir das informações das NFe/NFCe.
    """
    txtALERTAS = pd.DataFrame(columns = ["Id_Ext_CMP","OBS_FISC"])

    #Resumo de revisões que devem ser executadas no arquivo BP_EC.
    BP_ECpr = BP_EC_CONC.copy()
    
    BP_ECpr['OBS_FISC'] = 0

    BP_ECpr['VL_DIFAL'] = pd.to_numeric(BP_ECpr['VL_DIFAL'], errors='coerce')
    BP_ECpr['VL_DIFAL'] = BP_ECpr['VL_DIFAL'].fillna(0)
    criterio = (BP_ECpr['Prob_DIFAL'] == 'ALTA') & (BP_ECpr['VL_DIFAL']<0.1)
    BP_ECpr.loc[criterio, 'OBS_FISC'] = f'Verificar se possui DIFAL, pelo CFOP.'
    txtALERTAS = tst_ALT(txtALERTAS, BP_ECpr, f'Verificar se possui DIFAL, pelo CFOP.')
    criterio = (BP_ECpr['Prob_DIFAL'] != 'ALTA') & (BP_ECpr['VL_DIFAL']>=0.1)
    BP_ECpr.loc[criterio, 'OBS_FISC'] = f'Verificar se possui DIFAL, pelo CFOP, indica que não.'
    txtALERTAS = tst_ALT(txtALERTAS, BP_ECpr, f'Verificar se possui DIFAL, pelo CFOP, indica que não.')

    BP_ECpr['VL_ST'] = pd.to_numeric(BP_ECpr['VL_ST'], errors='coerce')
    BP_ECpr['VL_ST'] = BP_ECpr['VL_ST'].fillna(0)
    criterio = (BP_ECpr['Prob_ST'] == 'ALTA') & (BP_ECpr['VL_ST']<0.1)
    BP_ECpr.loc[criterio, 'OBS_FISC'] = f'Verificar se possui ST, pelo CFOP.'
    txtALERTAS = tst_ALT(txtALERTAS, BP_ECpr, f'Verificar se possui ST, pelo CFOP.')
    criterio = (BP_ECpr['Prob_ST'] != 'ALTA') & (BP_ECpr['VL_ST']>=0.1)
    BP_ECpr.loc[criterio, 'OBS_FISC'] = f'Verificar se possui ST, pelo CFOP, indica que não.'
    txtALERTAS = tst_ALT(txtALERTAS, BP_ECpr, f'Verificar se possui ST, pelo CFOP, indica que não.')

    criterio = (BP_ECpr['COD_SIT'] == '02')
    BP_ECpr.loc[criterio, 'OBS_FISC'] = f'Verificar se a NFe é cancelada, COD_SIT 02 no SPED EFD ICMS.'
    txtALERTAS = tst_ALT(txtALERTAS, BP_ECpr, f'Verificar se a NFe é cancelada, COD_SIT 02 no SPED EFD ICMS.')
    criterio = (BP_ECpr['FLG_TPNF'] == '1') & (BP_ECpr['COD_SIT'] == '06')
    BP_ECpr.loc[criterio, 'OBS_FISC'] = f'Verificar se a NFe é complementar, COD_SIT 06 no SPED EFD ICMS.'
    txtALERTAS = tst_ALT(txtALERTAS, BP_ECpr, f'Verificar se a NFe é complementar, COD_SIT 06 no SPED EFD ICMS.')
    criterio = (BP_ECpr['FLG_TPNF'] == '0') & (BP_ECpr['FLG_NFe_CMP'] != '06')
    BP_ECpr.loc[criterio, 'OBS_FISC'] = f'Verificar se a NFe é normal, COD_SIT diferente de 06 no SPED EFD ICMS.'
    txtALERTAS = tst_ALT(txtALERTAS, BP_ECpr, f'Verificar se a NFe é normal, COD_SIT diferente de 06 no SPED EFD ICMS.')
    BP_ECpr = pd.DataFrame()
    for n in ['Cd_NCM','Cd_CFOP','CST_ICMS','CST_IPI']:
        BP_EC.loc[(BP_EC[n].isnull()), 'OBS_FISC'] = f'Explicar porque não foi informado {n}. É obrigatório!'
        txtALERTAS = tst_ALT(txtALERTAS, BP_EC, f'Explicar porque não foi informado {n}. É obrigatório!')
    BP_EC.loc[(BP_EC['CST_IPI'].isin(['01','02','03','04','05','51','52','53','54','55'])) &
            (BP_EC['ALIQ_IPI'] != '0'),
            'OBS_FISC'] = f'Explicar porque foi informado alíquota IPI para situação não tributada'
    txtALERTAS = tst_ALT(txtALERTAS, BP_EC, f'Explicar porque foi informado alíquota IPI para situação não tributada')
    lst_CST = ['30','40','41','50','103','203','300','400']
    BP_EC.loc[(BP_EC['CST_ICMS'].isin(lst_CST)) &
            (BP_EC['ALIQ_ICMS'] != '0'),
            'OBS_FISC'] = f'Explicar porque foi informado alíquota ICMS para situação não tributada'
    txtALERTAS = tst_ALT(txtALERTAS, BP_EC, f'Explicar porque foi informado alíquota ICMS para situação não tributada')

    lst_CST = ['10','60','70','201','202','203','500']
    BP_EC.loc[(BP_EC['CST_ICMS'].isin(lst_CST)) &
            (BP_EC['VL_ST'] == '0'),
            'OBS_FISC'] = f'Explicar porque não foi informado alíquota ST para situação tributada'
    txtALERTAS = tst_ALT(txtALERTAS, BP_EC, f'Explicar porque não foi informado alíquota ST para situação tributada')
    if "Vl_II" in BP_EC.columns:
        BP_EC = BP_EC.rename(columns = {"Vl_BC" : "VL_BC", "Vl_II" : "VL_II", "Vl_IOF" : "VL_IOF", "Vl_Desp_ADU" : "VL_Desp_ADU",})
    BP_EC.loc[(BP_EC['FLG_IMP'] == '1') &
            ((BP_EC['VL_II'] == '0') | (BP_EC['VL_IOF'] == '0') | (BP_EC['VL_BC'] == '0')
            | (BP_EC['VL_Desp_ADU'] == '0')),
            'OBS_FISC'] = f'Explicar porque não foi informado dados sobre a importação'
    txtALERTAS = tst_ALT(txtALERTAS, BP_EC, f'Explicar porque não foi informado dados sobre a importação')
    BP_EC.loc[
            (~(BP_EC['Cd_NG'].isin(['1','2']))),
            'OBS_FISC'] = f'Explicar porque não foi informado Cd_NG para este CFOP. É ativo!'
    
    if st.session_state.dt_fim <= date.today():
        txtALERTAS = tst_ALT(txtALERTAS, BP_EC, f'Explicar porque não foi informado Cd_NG para este CFOP. É ativo!')
        s1 = (BP_UAR['COD_ITEM'].drop_duplicates().to_list())
        BP_EC.loc[(BP_EC['COD_ITEM'].isin(s1)) &
                (BP_EC['FLG_BPR'] == '0'),
                'OBS_FISC'] = f'Inconsistência entre FLG_BPR e arquivo BP_UAR. Revisar!'
        txtALERTAS = tst_ALT(txtALERTAS, BP_EC, f'Inconsistência entre FLG_BPR e arquivo BP_UAR. Revisar!')

    #caso haja um problema, deve-se retificar. Caso esteja correto, deve-se apresentar a justificativa.
    txtALERTAS.to_csv(f"{dir_arq_saida}/BP_EC_ALERTAS_.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    txtALERTAS.to_sql("BP_EC_ALERTAS", con, if_exists='replace', index=False)

    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/BP_EC_ALERTAS_.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        avl.progress(86, "Avaliando a natureza do material (UC ou COM), ROA vs EC...")
    
    BP_EC_CONC = BP_EC_CONC.rename(columns={'VL_IPI' : 'VL_IPI_EFD'})
    if 'CNPJ_COMP' not in BP_EC_CONC.columns:
        tabelas = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", con=con_efd)
        tabelas = tabelas['name'].tolist()
        cnpjs = [t.split('_')[-1] for t in tabelas if t.startswith('BLF_G110_')]
        cnpjs = sorted(set(cnpjs))
        if len(cnpjs)==1:
            BP_EC_CONC['CNPJ_COMP'] = cnpjs[0]
        else:
            BP_EC_CONC['CNPJ_COMP'] = cnpjs[0]
            st.warning(f"Usado {cnpjs[0]}, falta CNPJ_COMP e não consigo identificar")
            
    col_f1 = ['Id_Ext_CMP', 'COD_ITEM', 'Cd_NG', 'Cd_Pedido', 'Txt_Nom_Forn', 'Cd_Forn',  'CNPJ', 'SER', 'NUM_DOC', 
              'Dt_NF', 'Txt_Desc_Mat', 'Cd_NCM', 'Cd_EXTIPI', 'Cd_CFOP', 'QTD', 'Cd_Unid', 'CST_ICMS', 'ALIQ_ICMS', 
              'CST_IPI', 'ALIQ_IPI', 'VL_TOT_ICMS', 'VL_TOT_IPI', 'VL_ITEM', 'FLG_BPR', 'FLG_TP', 'VL_DIFAL', 'VL_ST', 
              'FLG_ICMS', 'FLG_TPNF', 'FLG_IMP', 'VL_BC', 'VL_Desp_ADU', 
              'VL_II', 'VL_IOF', 'CHV_NFE', 'COD_SIT', 'CNPJ_EFD','SER_EFD','NUM_DOC_EFD','DT_DOC','DT_E_S','VL_DOC',
              'IND_PGTO', 'VL_DESC_NF','VL_ABAT_NT','VL_MERC','IND_FRT','VL_FRT','VL_SEG','VL_OUT_DA','VL_ICMS_ST_NF',
              'COD_ITEM_SPD','DESCR_COMPL','QTD_EFD', 'UNID', 'NUM_ITEM_EFD','VL_ITEM_EFD','VL_DESC','IND_MOV','CST_ICMS_EFD',
              'Cd_CFOP_EFD','ALIQ_ICMS_EFD','CST_IPI_EFD','VL_BC_IPI','ALIQ_IPI_EFD','VL_IPI_EFD', 'Nm_EMP', 'CNPJ_COMP']


    BP_EC_AVAL = BP_EC_CONC[col_f1].copy()
    BP_EC_AVAL = BP_EC_AVAL.rename(columns={'VL_ITEM': 'VL_TOT_LIQ', 'ALIQ_ICMS': 'ALIQ_ICMS_EC', 'ALIQ_IPI': 'ALIQ_IPI_EC'})
    
    LST_ROA = LST_ROA.sort_values(['COD_ITEM','Cd_NG']).drop_duplicates(subset=['COD_ITEM'])
    LST_ROA.columns = ['COD_ITEM','Cd_NG_ROA']

    BP_EC_AVAL = BP_EC_AVAL.merge(LST_ROA, on='COD_ITEM', how='left')
    
    criterio = ((BP_EC_AVAL['Cd_NG'].astype(str)=='1') &  BP_EC_AVAL['Cd_NG_ROA'].notnull()
                & (BP_EC_AVAL['Cd_NG'].astype(str)!=BP_EC_AVAL['Cd_NG_ROA'].astype(str)))
    teste = BP_EC_AVAL[['Id_Ext_CMP', 'COD_ITEM', 'Cd_NG','Cd_NG_ROA']].copy()
    teste['OBS_SFF'] = 'NO'
    teste.loc[criterio, 'OBS_SFF'] = 'Verifique a classificação de UC/COM'
    criterio = BP_EC_AVAL['Cd_NG'].astype(str).isin(['1','2'])
    teste.loc[~criterio, 'OBS_SFF'] = 'Bens de uso ou de consumo ou de revenda'
    teste[teste['COD_ITEM'].notnull()].to_csv(f"{dir_arq_saida}/BP_EC_UC_COM_.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/BP_EC_UC_COM_.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    # Criando uma cópia de LST_ROA com colunas renomeadas
    LST_ROAec = LST_ROA.rename(columns={'Cd_NG': 'Cd_NG_ROA'})
    # Merge entre LST_ITENS_NCORR_EC e LST_ROAec
    LST_ITENS_NCORR_EC = LST_ITENS_NCORR_EC.merge(LST_ROAec, on='COD_ITEM', how='left')

    BP_EC_AVAL['TST_NG'] = BP_EC_AVAL['Cd_NG']==BP_EC_AVAL['Cd_NG_ROA']
    BP_EC_AVAL = BP_EC_AVAL.rename(columns={'Cd_NG':'Cd_NG_EC'})
    LST_TUC = BP_EC_AVAL[BP_EC_AVAL['Cd_NG_EC']=='1'][['COD_ITEM','Txt_Desc_Mat']]
    if st: avl.progress(87, "Criando a Lista de UC com fatores de ajuste de preços Aneel...")
    if st.session_state.dt_fim <= date.today():
        # Buscando códigos informados no arquivo BP_UAR
        LST_TUC_BPUAR = BP_UAR[['COD_ITEM', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6']].drop_duplicates()
        # Realizando merge para complementar dados
        LST_TUC = (
                        LST_TUC.merge(LST_TUC_BPUAR, on='COD_ITEM', how='outer', indicator=True)
                        [['COD_ITEM', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6', 'Txt_Desc_Mat']]
                        .drop_duplicates()
                  )
        
        # Como o arquivo trás apenas itens BPR, vamos buscar a tucagem do ROA ou do INCR
        LST_INCuc = (
                    INCR[['COD_ITEM', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6']]
                    .drop_duplicates('COD_ITEM')
                    )
        
        LST_TUC = LST_TUC.set_index('COD_ITEM')
        LST_INCuc = LST_INCuc.set_index('COD_ITEM')
        LST_TUC.update(LST_INCuc)
    else:
        # pode ser intercalar, sem arquivo BP_UAR e INCR
        cols_nulas = {c: None for c in ['Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6']}
        LST_TUC = LST_TUC.assign(**cols_nulas).set_index('COD_ITEM')

    LST_ROAuc = (
                ROA[ROA['Cd_NG'] == '1'][['COD_ITEM', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6']]
                    .drop_duplicates('COD_ITEM')
                )
    
    LST_ROAuc = LST_ROAuc.set_index('COD_ITEM')
    LST_TUC.update(LST_ROAuc)
    LST_TUC = LST_TUC.reset_index()
    # Pode haver compras para AIC e AO, por isso:
    crit_TUC =LST_TUC['Nr_TUC'].isnull()
    if len(LST_TUC[crit_TUC])>0:
        LST_TUC[crit_TUC].to_csv(f"{dir_arq_saida}/TUC_UC_FALTANTESpr.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
        if st: 
            registrar_artefato(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                file_path = rf'{dir_arq_saida}/TUC_UC_FALTANTESpr.csv',
                                tipo_artefato = "SAIDA", 
                                calcular_hash = True)
    caminho_completo = os.path.join(dir_arq_saida, "TUC_UC_FALTANTES.csv")
    if os.path.exists(caminho_completo):
        LST_TUC_AX = pd.read_csv(caminho_completo, sep='|', usecols=['COD_ITEM','Nr_TUC','Nr_A1','Nr_A2',
                            'Nr_A3','Nr_A4','Nr_A5','Nr_A6'], dtype=str, encoding="Latin-1")
        LST_TUC_AX = LST_TUC_AX.set_index('COD_ITEM')
        LST_TUC = LST_TUC.set_index("COD_ITEM")
        LST_TUC.update(LST_TUC_AX)
        LST_TUC = LST_TUC.reset_index()
    
    LST_TUC = LST_TUC.drop(columns='Txt_Desc_Mat')
    # Buscando a codificação da Aneel
    LST_TUC = bullD.FCOG_ATR(LST_TUC, dt_fim_proc, st)
    LST_TUC.to_csv(f"{dir_arq_saida}/DADOS_TUCAGEM.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/DADOS_TUCAGEM.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        
    BP_EC_AVALa = BP_EC_AVAL.merge(LST_TUC, on=['COD_ITEM'],how='left')
    BP_EC_AVALa = BP_EC_AVALa.merge(BP_UAR[['COD_ITEM','Nr_FORM']].drop_duplicates(), how='left', on = 'COD_ITEM')
    BP_EC_AVALa = BP_EC_AVALa.rename(columns={'Nr_FORM' : 'Cd_FOR_COGE_AVL', 'Cd_FOR_COGE' : 'Cd_FOR_COGE_SFF'})
    BP_EC_AVALa['Tst_FCOGE'] = np.where(BP_EC_AVALa['Cd_FOR_COGE_AVL'].fillna("ND") != BP_EC_AVALa['Cd_FOR_COGE_SFF'].fillna("ND"),
                                        "Avaliar a divergência do FCOGE",
                                        "NA")
    BP_EC_AVALa['Cd_FOR_COGE'] = BP_EC_AVALa['Cd_FOR_COGE_AVL'].fillna('FCM0403')
    colns_FCOGE = ['Id_Ext_CMP','COD_ITEM','Cd_NG_EC','Cd_Pedido','Txt_Nom_Forn','CNPJ',
                   'SER','NUM_DOC','Dt_NF','Txt_Desc_Mat','Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6',
                   'Cd_FOR_COGE_SFF','Cd_FOR_COGE_AVL','Tst_FCOGE','Cd_FOR_COGE']
    BP_EC_AVALa[BP_EC_AVALa['Cd_NG_EC'].astype(str) == '1'][colns_FCOGE].to_excel(f"{dir_arq_saida}/TAB_AVAL_FCOGE.xlsx", index=False)

    #os não classificados será atualizados por IPCA (FCM0403)
    BP_EC_AVALa.loc[(BP_EC_AVALa['Cd_FOR_COGE'].isnull()) | 
                    (BP_EC_AVALa['Cd_FOR_COGE']=='ND'),'Cd_FOR_COGE']='FCM0403'

    #P4: agregar dados de pagamento
    #Vamos colocar os valores de pagamento e de data em colunas ao inves de linhas
    for n in ['Id_Ext_CMP','Nr_Parcela','VL_Parcela']:
        if n in BPFP_UAR.columns and BPFP_UAR[n].dtype == 'object':
            BPFP_UAR[n] = pd.to_numeric(BPFP_UAR[n].astype(str).str.replace(',','.'), errors='coerce')

    if 'Dt_PMTO' in BPFP_UAR.columns and BPFP_UAR['Dt_PMTO'].dtype == 'object':
        BPFP_UAR['Dt_PMTO'] = pd.to_datetime(BPFP_UAR['Dt_PMTO'], errors='coerce')
    if 'Id_Ext_CMP' in BP_EC_AVALa.columns and BP_EC_AVALa['Id_Ext_CMP'].dtype == 'object':
        BP_EC_AVALa['Id_Ext_CMP'] = pd.to_numeric(BP_EC_AVALa['Id_Ext_CMP'].astype(str).str.replace(',','.'), errors='coerce')
    
    if st: avl.progress(89, "Preenchendo pagamentos...")
    #Pode-se usar um projetado ou o arquivo entregue pela empresa

    BP_EC_AVALa['Dt_NF'] = pd.to_datetime(BP_EC_AVALa['Dt_NF'].astype(str).str.strip(), format='ISO8601', errors='coerce')

    # Existe uma situação que envolve a multiplicidade de itens e possível interpretação do agente quanto a forma de 
    # enviar. Para isto, vamos fazer uma agregação dos dados informados no arquivo de pagamentos pela chave complexa
    # CNPJ, SER, NUM_DOC. Depois faremos um rateio proporcional dos pagamentos pelos valores dos itens. Temos a possibilidade
    # de simular por uma data fictícia, porém, o FISCAL é o responsável pela decisão.

  
    BP_EC_AVALa['CNPJ'] = BP_EC_AVALa['CNPJ'].fillna("CNPJ_AUS")
    BP_EC_AVALa['SER'] = BP_EC_AVALa['SER'].fillna("SER_AUS")
    BP_EC_AVALa['NUM_DOC'] = BP_EC_AVALa['NUM_DOC'].fillna("NUM_DOC_AUS")

    # Teste de verificação de parcelas
    verificacao = (
                    BPFP_UAR.groupby('Id_Ext_CMP')
                    .agg(
                        qtd_registros=('Nr_Parcela', 'size'),
                        max_parcela=('Nr_Parcela', 'max')
                    )
                    .assign(ok=lambda x: x['qtd_registros'] == x['max_parcela'])
                  )

    inconsistentes = verificacao[~verificacao['ok']].reset_index()
    inconsistentes.to_csv(f"{dir_arq_saida}/Nr_PARCELA_INCONSISTENTES_REGISTROS.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    inconsistentes.to_sql("Nr_PARCELA_INCONSISTENTES_REGISTROS", con, if_exists='replace', index=False)
    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/Nr_PARCELA_INCONSISTENTES_REGISTROS.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)

    BPFP_UAR['FLG_data_ausente'] = (BPFP_UAR
                                     .groupby('Id_Ext_CMP')['Dt_PMTO']
                                     .transform(lambda x: x.isna().any()))
    
    if BPFP_UAR['FLG_data_ausente'].sum()>0:
        BPFP_UAR[BPFP_UAR['FLG_data_ausente']].to_csv(f"{dir_arq_saida}/Faltam_pagamentos_EC.csv", 
                                    index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
        if st: 
            registrar_artefato(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                file_path = rf'{dir_arq_saida}/Faltam_pagamentos_EC.csv',
                                tipo_artefato = "SAIDA", 
                                calcular_hash = True)
    if not FLG_ARQ:
        BP_EC_AVALa['FP_PGTO_1'] = 1
        BP_EC_AVALa['DT_PC_1'] = (BP_EC_AVALa['Dt_NF'] + timedelta(days=30)).dt.strftime('%d/%m/%Y')
        BP_EC_AVALa['Nr_Parcela'] = 1
        nm_col_vPC = ['FP_PGTO_1']
        nm_col_dPC = ['DT_PC_1']
    else:
        CHV_AX = BP_EC_AVALa[['Id_Ext_CMP', 'CNPJ', 'SER', 'NUM_DOC', 'VL_TOT_ICMS', 'VL_TOT_IPI', 'VL_TOT_LIQ']]
        cols = ['CNPJ', 'SER', 'NUM_DOC']
        idx_series = pd.Series(CHV_AX.index.astype(str), index=CHV_AX.index)
        for c in cols:
            CHV_AX[c] = CHV_AX[c].replace(f'{c}_AUS', np.nan).replace('', np.nan).fillna(idx_series)

        BPFP_UARm = BPFP_UAR.merge(CHV_AX[['Id_Ext_CMP', 'CNPJ', 'SER', 'NUM_DOC']], how='left', on=['Id_Ext_CMP'])
        VL_NFe = CHV_AX.groupby(by=['CNPJ', 'SER', 'NUM_DOC'],dropna=False)[['VL_TOT_ICMS', 'VL_TOT_IPI', 'VL_TOT_LIQ']].sum().reset_index()
        VL_NFe['VL_NFe_ERP'] = VL_NFe['VL_TOT_ICMS'] + VL_NFe['VL_TOT_IPI'] + VL_NFe['VL_TOT_LIQ']

        BPFP_UARm1 =   (
                            BPFP_UARm.groupby(['CNPJ', 'SER', 'NUM_DOC', 'Dt_PMTO'], dropna=False)[['VL_Parcela']]
                            .sum()
                            .reset_index()
                        )

        BPFP_UARm2 =   (
                            BPFP_UARm.groupby(['CNPJ', 'SER', 'NUM_DOC'], dropna=False)[['VL_Parcela']]
                            .sum()
                            .reset_index()
                        )

        BPFP_UARm1 = BPFP_UARm1.merge(BPFP_UARm2, on=['CNPJ', 'SER', 'NUM_DOC'], 
                                      how='left', suffixes=("_PARCELAS","_GLOBAL"))
        BPFP_UARm1 = BPFP_UARm1.merge(VL_NFe[['CNPJ', 'SER', 'NUM_DOC','VL_NFe_ERP']], on=['CNPJ', 'SER', 'NUM_DOC'], 
                                      how='left', suffixes=("_BPFP","_ERP"))

        BPFP_UARm1['FP_GR'] = np.where(BPFP_UARm1['VL_Parcela_GLOBAL'] / BPFP_UARm1['VL_NFe_ERP'] > 1,
                                       1,
                                       BPFP_UARm1['VL_Parcela_GLOBAL'] / BPFP_UARm1['VL_NFe_ERP'])
        BPFP_UARm1['FP_PGTO'] = BPFP_UARm1['VL_Parcela_PARCELAS'] / BPFP_UARm1['VL_Parcela_GLOBAL']
        BPFP_UARm1['Nr_Parcela'] = BPFP_UARm1.groupby(['CNPJ', 'SER', 'NUM_DOC']).cumcount().add(1)
        
        BPFP_UARm = BPFP_UARm1[['CNPJ', 'SER', 'NUM_DOC', 'FP_GR', 'Nr_Parcela', 'Dt_PMTO', 'FP_PGTO']]
        BPFPb = BPFP_UARm.pivot_table(index=['CNPJ', 'SER', 'NUM_DOC', 'FP_GR'], columns='Nr_Parcela', values='FP_PGTO').reset_index()
        BPFPb = BPFPb.fillna(0)
        BPFPb.columns = ['CNPJ', 'SER', 'NUM_DOC', 'FP_GR'] + [f'FP_PGTO_{col}' for col in BPFPb.columns if col not in ['CNPJ', 'SER', 'NUM_DOC', 'FP_GR']]
        nm_col_vPC = [col for col in BPFPb.columns if col not in ['CNPJ', 'SER', 'NUM_DOC', 'FP_GR']]
        BPFPc = BPFP_UARm.pivot_table(index=['CNPJ', 'SER', 'NUM_DOC'], columns='Nr_Parcela', values='Dt_PMTO').reset_index()
        colunas_alvo = [f'DT_PC_{col}' for col in BPFPc.columns if col not in ['CNPJ', 'SER', 'NUM_DOC']]
        BPFPc.columns = ['CNPJ', 'SER', 'NUM_DOC'] + colunas_alvo
        nm_col_dPC = colunas_alvo

        BPFP = BPFPb.merge(BPFPc, on=['CNPJ', 'SER', 'NUM_DOC'], how='left')
        BPFP['Nr_Parcela'] = BPFP[colunas_alvo].notna().sum(axis=1)

        BP_EC_AVALa = BP_EC_AVALa.merge(BPFP, on=['CNPJ', 'SER', 'NUM_DOC'], how='outer', suffixes=("","_BPFP"), indicator=True)
        map_res = {
                        'both' : 'NO',
                        'left_only' : 'Somente ERP, verifique',
                        'right_only' : 'Somente arquivo pagamentos, verifique',
                    }
        BP_EC_AVALa['IND_CONC'] = BP_EC_AVALa['_merge'].replace(map_res)
        BP_EC_AVALa = BP_EC_AVALa.drop(columns='_merge')
    
    if st: avl.progress(90, "Preenchendo dados do tipo de pagamento e de frete...")

    BP_EC_AVALa=BP_EC_AVALa.merge(LST_CFOP, on=['Cd_CFOP'], how='left')
    BP_EC_AVALc=BP_EC_AVALa.copy()

    # Mapeamento de valores para 'IND_PGTO'
    pgto_mapping = {
                        0: 'A VISTA',
                        1: 'A PRAZO',
                        2: 'OUTROS'
                    }
    BP_EC_AVALc['IND_PGTO'] = BP_EC_AVALc['IND_PGTO'].replace(pgto_mapping)

    # Mapeamento de valores para 'IND_FRT'
    frt_mapping = {
                        0: 'Contratação de frete por conta do Remetente (CIF)',
                        1: 'Contratação de frete por conta do Destinatário (FOB)',
                        2: 'Contratação de frete por conta de Terceiros',
                        3: 'Transporte próprio por conta do Remetente',
                        4: 'Transporte próprio por conta do Destinatário',
                        9: 'Sem cobrança de frete'
                    }
    BP_EC_AVALc['IND_FRT'] = BP_EC_AVALc['IND_FRT'].replace(frt_mapping)

    if st: avl.progress(91, "Consolidação de quantidades EC vs ROA vs SPED...")
    
    if not sql.existe_tabela("CONSOL_TOT_QTD_FISICO", con) or apr1:
        SQLq = """
                    WITH ResultadosROA AS (
                        SELECT
                            t1.COD_ITEM,
                            t1.Unidade AS Cd_Unid,
                            SUM(CAST(REPLACE(t1.Qtd, ',', '.') AS REAL)) AS QTD_ROA
                        FROM
                            ROA t1
                        WHERE
                            t1.dt_ARQ = ? 
                            AND t1.Cd_NG IN (1, 2)
                        GROUP BY
                            t1.COD_ITEM, t1.Unidade
                    )
                    SELECT * FROM ResultadosROA WHERE QTD_ROA>0;
                """
        CONSOL_ROA = sql.imp_tbl_forma_001('ROA', SQLq, con = con, st=st, Empresa=Empresa)
        CONSOL_ROA['QTD_ROA'] = CONSOL_ROA['QTD_ROA'].fillna(0)

        SQLq = """
                    WITH ResultadosAO AS (
                        SELECT 
                            t1.COD_ITEM, 
                            t1.Cd_UND AS Cd_Unid, 
                            SUM(CAST(REPLACE(t1.Qtd, ',', '.') AS REAL)) AS QTD_AO
                        FROM 
                            AO t1
                        WHERE 
                            t1.dt_ARQ = ? 
                            AND DATE(t1.Dt_LCMTO) = (SELECT MAX(DATE(Dt_LCMTO)) FROM AO)
                        GROUP BY 
                            t1.COD_ITEM, t1.Cd_UND
                    )
                    SELECT * FROM ResultadosAO WHERE QTD_AO > 0;
                """
        CONSOL_AO = sql.imp_tbl_forma_001('AO', SQLq, con = con, st=st, Empresa=Empresa)
        if len(CONSOL_AO)>0:
            CONSOL_AO['QTD_AO'] = CONSOL_AO['QTD_AO'].fillna(0)
        else:
            CONSOL_AO = pd.DataFrame(columns=['COD_ITEM','Cd_Unid','QTD_AO'])

        SQLq = """
                    WITH ResultadosAO AS (
                        SELECT
                            t1.COD_ITEM,
                            t1.Unidade AS Cd_Unid,
                            SUM(CAST(REPLACE(t1.Qtd, ',', '.') AS REAL)) AS QTD_ROA_CURSO
                        FROM
                            ROAaicAT t1
                        WHERE
                            t1.dt_ARQ = ? 
                        GROUP BY
                            t1.COD_ITEM, t1.Unidade
                    )
                    SELECT * FROM ResultadosAO WHERE QTD_ROA_CURSO>0;
                """
        CONSOL_ROA_CURSO = sql.imp_tbl_forma_001('ROAaicAT', SQLq, con = con, st=st, Empresa=Empresa)
        if len(CONSOL_ROA_CURSO)==0:
            CONSOL_ROA_CURSO = pd.DataFrame(columns=[
                                "COD_ITEM",
                                "Cd_Unid",
                                "QTD_ROA_CURSO"
                            ])
        CONSOL_ROA_CURSO['QTD_ROA_CURSO'] = CONSOL_ROA_CURSO['QTD_ROA_CURSO'].fillna(0)

        SQLq = """
                    WITH ResultadosAO AS (
                        SELECT
                            t1.COD_ITEM,
                            t1.Unidade AS Cd_Unid,
                            SUM(CAST(REPLACE(t1.Qtd, ',', '.') AS REAL)) AS QTD_MAN
                        FROM
                            ROAserv t1
                        WHERE
                            t1.dt_ARQ = ? 
                        GROUP BY
                            t1.COD_ITEM, t1.Unidade
                    )
                    SELECT * FROM ResultadosAO WHERE QTD_MAN>0;
                """
        CONSOL_MAN = sql.imp_tbl_forma_001('ROAserv', SQLq, con = con, st=st, Empresa=Empresa)
        if CONSOL_MAN.empty:
            SQLq = """
                    WITH ResultadosAO AS (
                        SELECT
                            t1.COD_ITEM,
                            t1.Unidade AS Cd_Unid,
                            SUM(CAST(REPLACE(t1.Qtd, ',', '.') AS REAL)) AS QTD_MAN
                        FROM
                            RAserv t1
                        WHERE
                            t1.dt_ARQ = ? 
                        GROUP BY
                            t1.COD_ITEM, t1.Unidade
                    )
                    SELECT * FROM ResultadosAO WHERE QTD_MAN>0;
                """
            CONSOL_MAN = sql.imp_tbl_forma_001('RAserv', SQLq, con = con, st=st, Empresa=Empresa)
        if CONSOL_MAN.empty:
            st.warning("Não foi enviado o Razão de Serviços (ODS). Verificar o motivo.")
            CONSOL_MAN = pd.DataFrame([{
                                            "COD_ITEM": "avazio",
                                            "Cd_Unid": "NA",
                                            "QTD_MAN": 0
                                        }])
        CONSOL_MAN['QTD_MAN'] = CONSOL_MAN['QTD_MAN'].fillna(0)
        
        CONSOL_TOT = CONSOL_ROA.merge(CONSOL_ROA_CURSO, how='outer', on = ['COD_ITEM', 'Cd_Unid'], indicator=True)
        map_res = {
                    'both' : 'AIS e AIC',
                    'left_only' : 'Somente AIS',
                    'right_only' : 'Somente AIS',
                }
        CONSOL_TOT['IND_DESTINO_ODI_CURSO_IMOB'] = CONSOL_TOT['_merge'].replace(map_res)
        CONSOL_TOT = CONSOL_TOT.drop(columns='_merge')

        CONSOL_TOT = CONSOL_TOT.merge(CONSOL_AO, how='outer', on = ['COD_ITEM', 'Cd_Unid'], indicator=True)
        map_res = {
                    'both' : 'Imobilizado e Estoque',
                    'left_only' : 'Imobilizado',
                    'right_only' : 'Estoque',
                }
        CONSOL_TOT['IND_DESTINO_ODI_ESTOQUE'] = CONSOL_TOT['_merge'].replace(map_res)
        CONSOL_TOT = CONSOL_TOT.drop(columns='_merge')

        CONSOL_TOT = CONSOL_TOT.merge(CONSOL_MAN, how='outer', on = ['COD_ITEM', 'Cd_Unid'], indicator=True)
        map_res = {
                    'both' : 'Investimento/Estoque e Manutenção',
                    'left_only' : 'Investimento/Estoque',
                    'right_only' : 'Manutenção',
                }
        CONSOL_TOT['IND_DESTINO_ODI_ODS'] = CONSOL_TOT['_merge'].replace(map_res)
        CONSOL_TOT = CONSOL_TOT.drop(columns='_merge')

        CONSOL_TOT['QTD'] = (CONSOL_TOT['QTD_ROA'].fillna(0) +
                            CONSOL_TOT['QTD_ROA_CURSO'].fillna(0) +
                            CONSOL_TOT['QTD_MAN'].fillna(0) +
                            CONSOL_TOT['QTD_AO'].fillna(0))
        
        CONSOL_TOT.to_sql("CONSOL_TOT_QTD_FISICO", con, if_exists='replace', index=False)
    else:
        CONSOL_TOT = pd.read_sql("SELECT * FROM CONSOL_TOT_QTD_FISICO", con)

    lst_cnvt=['QTD','VL_TOT_IPI','VL_TOT_LIQ','VL_TOT_ICMS','VL_ODC','VL_ICMS_FIN',
            'VL_ITEM','VL_DESC_NF','VL_ABAT_NT','VL_DIFAL','VL_ST','FLG_ICMS']
    for nm in lst_cnvt:
        if nm in BP_EC_AVALc.columns and BP_EC_AVALc[nm].dtype == 'object':
            BP_EC_AVALc[nm] = pd.to_numeric(BP_EC_AVALc[nm].astype(str).str.replace(',','.'), errors='coerce')

    LST_BPR = BP_UAR['COD_ITEM'].drop_duplicates().to_list()
    BP_EC_AVALc.loc[BP_EC_AVALc['QTD'] != 0, 'FLG_TPNF'] = '1'
    if (BP_EC_AVALc['FLG_ICMS']=='1').sum() < (0.1 * len(BP_EC_AVALc)):
        BP_EC_AVALc.loc[(BP_EC_AVALc['VL_TOT_ICMS'] != 0), 'FLG_ICMS'] = '1'
    if (BP_EC_AVALc['FLG_BPR']=='1').sum() < (0.1 * len(BP_EC_AVALc)):
        BP_EC_AVALc.loc[BP_EC_AVALc['COD_ITEM'].isin(LST_BPR) & BP_EC_AVALc['Cd_CFOP'].isin(LST_CFOP_INV), 'FLG_BPR'] = '1'
        
    simples_remessa = BP_EC_AVALc[BP_EC_AVALc['Cd_CFOP'].isin(['1552','1554','2552','2554'])].copy()
    manutencao = BP_EC_AVALc[BP_EC_AVALc['Cd_CFOP'].isin(['1915','1916','2915','2916'])].copy()

    simples_remessa.to_csv(f"{dir_arq_saida}/simples_remessa_EC.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    manutencao.to_csv(f"{dir_arq_saida}/manutencao_EC.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)

    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/simples_remessa_EC.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        registrar_artefato(st.session_state.database_MAN, 
                                    st.session_state.execucao_id, 
                                    file_path = rf'{dir_arq_saida}/manutencao_EC.csv',
                                    tipo_artefato = "SAIDA", 
                                    calcular_hash = True)
    if 'COD_SIT' in BP_EC_AVALc.columns:
        mask = BP_EC_AVALc['COD_SIT'].astype(str).eq('06')
        if mask.any():
            st.warning(
                "Foram detectadas notas complementares (COD_SIT = 06). "
                "As quantidades dessas notas serão zeradas."
            )

            BP_EC_AVALc.loc[mask, ['QTD', 'QTD_EFD']] = 0

    if 'FLG_TPNF' in BP_EC_AVALc.columns:
        mask1 = BP_EC_AVALc['FLG_TPNF'].astype(str).eq('0')
        mask2 = BP_EC_AVALc['QTD'] != 0
        
        if mask1.any() and mask2.any():
            st.warning(
                "Foram detectadas notas complementares (FLG_TPNF = 0). "
                "As quantidades dessas notas serão zeradas."
            )

            BP_EC_AVALc.loc[mask1 & mask2, ['QTD', 'QTD_EFD']] = 0
        
        mask3 = BP_EC_AVALc['QTD_EFD'] != 0
        if mask1.any() and mask3.any():
            st.warning(
                "Foram detectadas notas complementares (FLG_TPNF = 0). "
                "As quantidades dessas notas serão zeradas no lado do EFD."
            )
            BP_EC_AVALc.loc[mask1 & mask2, ['QTD_EFD']] = 0

    
    if 'QTD' in BP_EC_AVAL.columns and BP_EC_AVAL['QTD'].dtype == 'object':
        BP_EC_AVAL['QTD'] = pd.to_numeric(BP_EC_AVAL['QTD'].astype(str).str.replace(',','.'), errors='coerce')
    
    BP_EC_AVAL['QTD'] = BP_EC_AVAL['QTD'].fillna(0)
    CONSOL_EC = BP_EC_AVAL[BP_EC_AVAL['Cd_NG_EC'].isin(['1','2'])].groupby(['COD_ITEM','Txt_Desc_Mat','Cd_Unid'], dropna=False)[['QTD']].sum().reset_index()
    CONSOL_TOTs = CONSOL_TOT.merge(CONSOL_EC,on='COD_ITEM',how='outer', suffixes=("_FIS","_ERP"), indicator=True)
    CONSOL_EFD = (
                    BP_EC_AVAL[BP_EC_AVAL['Cd_NG_EC']
                    .isin(['1','2'])]
                    .groupby(['COD_ITEM','UNID'], dropna=False)[['QTD_EFD']]
                    .sum().reset_index()
                    .rename(columns={"UNID":'Cd_Unid_EFD'})
                )
    CONSOL_TOTs = CONSOL_TOTs.rename(columns={'_merge':'_merge_ERP'})
    CONSOL_TOTs = CONSOL_TOTs.merge(CONSOL_EFD,on='COD_ITEM',how='outer', suffixes=("","_EFD"), indicator=True)

    for col in ['QTD_ROA','QTD_ROA_CURSO','QTD_MAN','QTD_AO','QTD_FIS', 'QTD_ERP', 'QTD_EFD']:
        CONSOL_TOTs[col] = CONSOL_TOTs[col].fillna(0)

    CONSOL_TOTs = CONSOL_TOTs.groupby(by=['COD_ITEM','Txt_Desc_Mat','Cd_Unid_ERP','QTD_ROA','QTD_ROA_CURSO',
                                      'QTD_MAN','QTD_AO','QTD_FIS','QTD_ERP'])[['QTD_EFD']].sum().reset_index()

    fis = CONSOL_TOTs['QTD_FIS']
    erp = CONSOL_TOTs['QTD_ERP']
    efd = CONSOL_TOTs['QTD_EFD']

    fis_igual_erp = abs(fis - erp) < 0.1
    fis_igual_efd = abs(fis - efd) < 0.1
    erp_igual_efd = abs(erp - efd) < 0.1
    todas_iguais = fis_igual_erp & fis_igual_efd

    CONSOL_TOTs['OBS_SFF'] = ""
    # Caso 1: FIS = ERP = EFD
    crit = todas_iguais & (CONSOL_TOTs['OBS_SFF'] == "")
    CONSOL_TOTs.loc[crit, 'OBS_SFF'] = """Bens com destino rastreado, conforme dados apresentados, é igual ao dado obtido 
                                      nas compras informadas e obtidos do ERP e as quantidades declaradas ao FISCO, 
                                      EFD. Condição esperada.""".replace("\n","")
    
    # Caso 2: FIS = ERP ≠ EFD
    crit = fis_igual_erp & ~fis_igual_efd & (CONSOL_TOTs['OBS_SFF'] == "")
    CONSOL_TOTs.loc[crit, 'OBS_SFF'] = CONSOL_TOTs.loc[crit].apply(
                                      lambda x: f"""Bens com destino rastreado, conforme dados apresentados, é igual ao dado obtido 
                                      nas compras informadas e obtidos do ERP ({x['QTD_FIS']}), mas diferente das quantidades 
                                      declaradas ao FISCO, EFD ({x['QTD_EFD']}). Possível inconsistência no dado do EFD.""".replace("\n",""), 
                                       axis=1
                                    )
    
    # Caso 3: FIS = EFD ≠ ERP
    crit = fis_igual_efd & ~fis_igual_erp & (CONSOL_TOTs['OBS_SFF'] == "")
    CONSOL_TOTs.loc[crit, 'OBS_SFF'] = CONSOL_TOTs.loc[crit].apply(
                                      lambda x: f"""Bens com destino rastreado, conforme dados apresentados, é igual ao dado obtido 
                                      nas compras informadas ao FISCO, EFD ({x['QTD_FIS']}), mas diferente das quantidades 
                                      declaradas nas compras, ERP ({x['QTD_ERP']}). Possível inconsistência no dado do ERP.""".replace("\n",""), 
                                       axis=1
                                    )

    def demais_casos(fis, erp, efd, OBS_SFF):
        if fis == 0 and erp == 0 and efd == 0 and (OBS_SFF == ""):
            return "Todas as quantidades são zero. Condição não esperada."
        elif fis == 0 and erp == 0 and efd > 0 and (OBS_SFF == ""):
            return f"FIS e ERP zerados, mas EFD apresenta quantidade ({efd}). Possível inconsistência no dado do EFD."
        elif fis == 0 and erp > 0 and efd == 0 and (OBS_SFF == ""):
            return f"FIS e EFD zerados, mas ERP apresenta quantidade ({erp}). Possível inconsistência no dado do ERP."
        elif fis == 0 and (erp != 0 or efd != 0) and (OBS_SFF == ""):
            return f"FIS zerados, mas ERP ({erp}), ou EFD ({erp}), apresenta quantidade. Sem destino rastreado."
        elif erp == 0 and fis > 0 and efd == 0 and (OBS_SFF == ""):
            return f"ERP e EFD zerados, mas FIS apresenta quantidade ({fis}). Sem destino rastreado (AIC, Estoque ou ODS). Observar teste LADO A vs B, para itens de risco."
        elif fis > erp and fis > efd and efd == efd and (OBS_SFF == ""):
            return f"FIS ({fis}) maior que ERP ({erp}) e EFD ({efd}). Condição possível, pode ser AIC anterior, compras do ciclo anterior. Observar teste LADO A vs B, para itens de risco."
        elif erp > fis and erp == efd and (OBS_SFF == ""):
            return f"ERP ({erp}) maior que FIS ({fis}) e igual a EFD ({efd}). Sem destino rastreado (AIC, Estoque ou ODS). Observar teste LADO A vs B, para itens de risco."
        elif erp > fis and efd < erp and (OBS_SFF == ""):
            return f"Todas diferentes. ERP ({erp}) maior que FIS ({fis}) e EFD ({efd}). Possível inconsistência de conciliação."
        elif erp > fis and efd > erp and (OBS_SFF == ""):
            return f"Todas diferentes. ERP ({erp}) maior que FIS ({fis}) e maior que EFD ({efd}). Possível inconsistência de conciliação."
        elif (OBS_SFF == ""):
            return f"Quantidades: FIS ({fis}), ERP ({erp}), EFD ({efd}). Situação específica a analisar."

    crit = CONSOL_TOTs['OBS_SFF'] == ""
    CONSOL_TOTs.loc[crit, 'OBS_SFF'] = CONSOL_TOTs.loc[crit].apply(
                                       lambda row: demais_casos(row['QTD_FIS'], row['QTD_ERP'], row['QTD_EFD'], row['OBS_SFF']), 
                                       axis=1
                                        )

    TUC_ROA = ROA[(ROA['Cd_NG']=='1')][['COD_ITEM','Nr_TUC']]
    TUC_ROA = TUC_ROA.drop_duplicates(['COD_ITEM'], keep='first')

    CONSOL_TOTs = CONSOL_TOTs[['COD_ITEM','Txt_Desc_Mat','Cd_Unid_ERP','QTD_ROA','QTD_ROA_CURSO','QTD_MAN','QTD_AO',
                               'QTD_FIS','QTD_ERP','QTD_EFD','OBS_SFF']].merge(TUC_ROA, how='left', on='COD_ITEM')
    
    crit = CONSOL_TOTs['Txt_Desc_Mat'].isnull()
    LST_AUS = CONSOL_TOTs[crit]['COD_ITEM'].drop_duplicates().to_list()
    LST_MAT_SDI = LST_MAT[LST_MAT['COD_ITEM'].isin(LST_AUS)][['COD_ITEM', 'DESCR_ITEM']].copy()
    if len(LST_MAT_SDI)>0:
        map_dic = LST_MAT_SDI.set_index('COD_ITEM')['DESCR_ITEM'].to_dict()
        CONSOL_TOTs.loc[crit, 'Txt_Desc_Mat'] = CONSOL_TOTs.loc[crit, 'COD_ITEM']
        CONSOL_TOTs =  CONSOL_TOTs.rename(columns=map_dic)

    CONSOL_TOTs.to_sql("CONSOL_TOT_QTD_EC", con, if_exists='replace', index=False)

    if st: avl.progress(92, "Determinação de alocação do ICMS entre UC e COM...")

    #fazendo o rateio do valor da ODC    
    if 'VL_ODC' not in BP_EC_AVALc.columns:
        df_ODC = sql.imp_tbl_forma_001('BP_EC', con = con, st=st, Empresa=Empresa)
        if len(df_ODC) and 'VL_ODC' in df_ODC.columns:
            df_ODC['Id_Ext_CMP'] = df_ODC['Id_Ext_CMP'].astype(str)
            df_ODC['VL_ODC'] = pd.to_numeric(df_ODC['VL_ODC'].astype(str).str.replace(',','.'), errors='coerce')
            BP_EC_AVALc['Id_Ext_CMP'] = BP_EC_AVALc['Id_Ext_CMP'].astype(str)
            BP_EC_AVALc = BP_EC_AVALc.merge(df_ODC[['Id_Ext_CMP', 'VL_ODC']], how='left', on='Id_Ext_CMP')
            BP_EC_AVALc['VL_ODC'] = BP_EC_AVALc['VL_ODC'].fillna(0)
        else:
            BP_EC_AVALc['VL_ODC'] = 0

    crit = BP_EC_AVALc['VL_TOT_LIQ'] > 0
    somas_itens = BP_EC_AVALc.loc[crit, ['VL_TOT_LIQ', 'VL_TOT_ICMS', 'VL_TOT_IPI']].sum()
    VL_GER_ODC = somas_itens.sum()

    if BP_EC_AVALc['VL_ODC'].sum() == 0:
        if (VL_GER_ODC != 0) & (BP_EC_AVALc['VL_ODC'].sum() == 0):
            BP_EC_AVALc['VL_ODC'] = round(VL_ODC/VL_GER_ODC*(BP_EC_AVALc['VL_TOT_LIQ']+
                                        BP_EC_AVALc['VL_TOT_ICMS']+BP_EC_AVALc['VL_TOT_IPI']),2)
    

    if st: avl.progress(92, "Buscando o valor do financeiro de ICMS...")

    if ICMS_FLG != 0:
        def converter_num(value):
            if isinstance(value, str):
                value = value.replace(",", ".")
            return pd.to_numeric(value, errors='coerce')
        
        if len(cnpjs)==1:
            i = converter_num(tbl_icms_fin[0].iloc[1, 1]) / 100
            n = converter_num(tbl_icms_fin[0].iloc[-1, 1])
        else:
            v1 = 0
            for i1, cnpj in enumerate(cnpjs):
                v2 = converter_num(tbl_icms_fin[i1].iloc[2, 1]) / 100
                if v1 < v2:
                    v1 = v2
                    i = tbl_icms_fin[i1].iloc[1, 1] / 100
                    n = tbl_icms_fin[i1].iloc[-1, 1]

        FR = (1 / (n * i)) * ((1 / (1 + i) ** n) + n * i - 1)
        tbl_G110a = BLF_G110.copy()
        try:
            tbl_G110a.iloc[:, 3:9] = tbl_G110a.iloc[:, 3:9].apply(
                lambda x: pd.to_numeric(x.astype(str).str.replace(",", "."), errors='coerce'))
            tbl_G110a = tbl_G110a.iloc[:, [1, 7, 12]]
            tbl_G110a.columns = ['DT_REF', 'FR_ICMS', 'CNPJ_COMP']
        except:
            tbl_G110a = pd.DataFrame({
                                        'DT_REF': [pd.Timestamp('1960-01-01')],
                                        'FR_ICMS': [0.0],
                                        'CNPJ_COMP' : ''
                                    })
    else:
        if 'DT_REF' not in BP_EC_AVALc.columns:
            BP_EC_AVALc['DT_REF'] = pd.to_datetime(BP_EC_AVALc['Dt_NF'])
            BP_EC_AVALc["DT_REF"] = BP_EC_AVALc["DT_REF"].dt.to_period("M").dt.to_timestamp()
        tbl_G110a = BP_EC_AVALc[['DT_REF']].drop_duplicates().reset_index(drop=True)
        FR = 0
        tbl_G110a['FR_ICMS'] = 0
        tbl_G110a['CNPJ_COMP'] = ''


    tbl_G110a['FR'] = FR
    tbl_G110a['DT_REF'] = pd.to_datetime(tbl_G110a['DT_REF'], errors='coerce')
    tbl_G110a.sort_values(by=['DT_REF'], inplace=True)
    
    for nm in BP_EC_AVALc.columns.to_list():
        if BP_EC_AVALc[nm].dtype == 'object' and nm[:2].upper() in ["VL", "AL"]:
            BP_EC_AVALc[nm] = pd.to_numeric(BP_EC_AVALc[nm].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')

    if st: avl.progress(93, "Rateando financeiro do ICMS...")

    cols_aliq = ['ALIQ_ICMS_EC', 'ALIQ_IPI_EC']
    for n in cols_aliq:
        BP_EC_AVALc.loc[BP_EC_AVALc[n]>1, n] = BP_EC_AVALc.loc[BP_EC_AVALc[n]>1, n]/100
    BP_EC_AVALc['VL_IPI'] = BP_EC_AVALc['VL_TOT_IPI']
    BP_EC_AVALc['VL_ICMS'] = BP_EC_AVALc['VL_TOT_ICMS']
    BP_EC_AVALc['FLG_ICMS'] = (BP_EC_AVALc['VL_TOT_ICMS'] != 0).astype(int)
    BP_EC_AVALc['DT_REF'] = BP_EC_AVALc['Dt_NF'].values.astype('datetime64[M]')

    BP_EC_AVALc['CNPJ_COMP'] = BP_EC_AVALc['CNPJ_COMP'].astype(str).str.zfill(14)
    tbl_G110a['CNPJ_COMP'] = tbl_G110a['CNPJ_COMP'].astype(str).str.zfill(14)

    BP_EC_AVALc = BP_EC_AVALc.merge(tbl_G110a, how='left', on=['DT_REF', 'CNPJ_COMP'])
    BP_EC_AVALc[['VL_CALC_ICMS_TOT', 'VL_CALC_ICMS_NR']] = 0

    if ICMS_FLG == 1:
        # Vamos buscar os dados do CIAP
        if (not sql.existe_tabela("tbl_CIAP", con)) or apr1:
            with st.spinner("Buscando dados do CIAP..."):
                df_CIAP = bsc_dd_CIAP(con_efd, st=st)
            for col in df_CIAP.columns:
                if col[:2].upper() == 'DT':
                    df_CIAP[col] = pd.to_datetime(df_CIAP[col], format="%d%m%Y", errors='coerce')
                elif (col[:2].upper() in ['VL', 'IN']) and (df_CIAP[col].dtype == 'object'):
                    df_CIAP[col] = pd.to_numeric(df_CIAP[col].astype(str).str.replace(',','.'), 
                                                                errors='coerce',
                                                                downcast='float')
            df_CIAP.to_sql("tbl_CIAP", con, if_exists='replace', index=False)
        else:
            df_CIAP = pd.read_sql("SELECT * FROM tbl_CIAP", con)

        cols = ['Nm_Arq','DT_INI','IND_PER_SAI','COD_IND_BEM','DT_MOV','TIPO_MOV',
                'IND_EMIT','COD_PART','COD_MOD','SERIE','NUM_DOC','CHV_NFE_CTE',
                'DT_DOC', 'NUM_ITEM', 'COD_ITEM', 'QTDE', 'UNID','VL_ICMS_OP_APLICADO',
                'VL_ICMS_ST_APLICADO', 'VL_ICMS_FRT_APLICADO', 'VL_ICMS_DIF_APLICADO']
        
        df_CIAP = df_CIAP[cols].rename(columns = {
            'Nm_Arq' : 'Nm_Arq_EFD','DT_INI' : 'DT_INI_CIAP', 'IND_PER_SAI' : 'IND_PER_SAI_CIAP',
            'COD_IND_BEM' : 'COD_IND_BEM_CIAP', 'DT_MOV' : 'DT_MOV_CIAP', 'TIPO_MOV' : 'TIPO_MOV_CIAP', 'IND_EMIT' : 'IND_EMIT_CIAP',
            'COD_PART' : 'COD_PART_CIAP', 'COD_MOD' : 'COD_MOD_CIAP', 'SERIE' : 'SERIE_CIAP', 'NUM_DOC' : 'NUM_DOC_CIAP',
            'CHV_NFE_CTE' : 'CHV_NFE', 'DT_DOC' : 'DT_DOC_CIAP', 'NUM_ITEM' : 'NUM_ITEM_EFD', 'COD_ITEM' : 'COD_ITEM_CIAP', 
            'QTDE' : 'QTDE_CIAP', 'UNID' : 'UNID_CIAP', 'VL_ICMS_OP_APLICADO' : 'VL_ICMS_OP_APLICADO_CIAP',
            'VL_ICMS_ST_APLICADO' : 'VL_ICMS_ST_APLICADO_CIAP', 'VL_ICMS_FRT_APLICADO' : 'VL_ICMS_FRT_APLICADO_CIAP', 
            'VL_ICMS_DIF_APLICADO' : 'VL_ICMS_DIF_APLICADO_CIAP'
        })
    else:
        # Essa empresa não possui dados de CIAP, todo ICMS é custo, não possui parcela de remuneração financeira
        df_CIAP = pd.DataFrame(columns=[
                                    "Nm_Arq_EFD",
                                    "DT_INI_CIAP",
                                    "IND_PER_SAI_CIAP",
                                    "COD_IND_BEM_CIAP",
                                    "DT_MOV_CIAP",
                                    "TIPO_MOV_CIAP",
                                    "IND_EMIT_CIAP",
                                    "COD_PART_CIAP",
                                    "COD_MOD_CIAP",
                                    "SERIE_CIAP",
                                    "NUM_DOC_CIAP",
                                    "CHV_NFE",
                                    "DT_DOC_CIAP",
                                    "NUM_ITEM_EFD",
                                    "COD_ITEM_CIAP",
                                    "QTDE_CIAP",
                                    "UNID_CIAP",
                                    "VL_ICMS_OP_APLICADO_CIAP",
                                    "VL_ICMS_ST_APLICADO_CIAP",
                                    "VL_ICMS_FRT_APLICADO_CIAP",
                                    "VL_ICMS_DIF_APLICADO_CIAP"
                                ])
    df_CIAP = df_CIAP.drop_duplicates(['CHV_NFE','NUM_ITEM_EFD'])
    BP_EC_AVALc = BP_EC_AVALc.merge(df_CIAP, how = 'outer', on = ['CHV_NFE','NUM_ITEM_EFD'], suffixes=("","_CIAP"), indicator=True)
    
    map_res = {
                'both' : 'CIAP e EFD ou ERP',
                'left_only' : 'Somente EFD ou ERP, verifique',
                'right_only' : 'Somente CIAP, verifique',
              }
    BP_EC_AVALc['IND_CONC_CIAP'] = BP_EC_AVALc['_merge'].replace(map_res)
    BP_EC_AVALc = BP_EC_AVALc.drop(columns='_merge')

    # existe itens que não se creditaram, mas que são compras efetuadas no período incremental
    # vamos aplicar o valor médio para o período.
    df_CIAP['DT_DOC_CIAP'] = pd.to_datetime(df_CIAP['DT_DOC_CIAP']).dt.to_period('M').dt.to_timestamp()
    dt_ini_proc = pd.to_datetime(dt_ini_proc)
    dt_fim_proc = pd.to_datetime(dt_fim_proc)
    df_IND_PER_SAI_CIAP = (df_CIAP[df_CIAP['DT_DOC_CIAP'].between(dt_ini_proc, dt_fim_proc, inclusive='both')]
                            .assign(total=df_CIAP[['VL_ICMS_OP_APLICADO_CIAP',
                                                   'VL_ICMS_ST_APLICADO_CIAP',
                                                   'VL_ICMS_FRT_APLICADO_CIAP',
                                                   'VL_ICMS_DIF_APLICADO_CIAP']]
                            .sum(axis=1))
                            .groupby('DT_DOC_CIAP', dropna=False)
                            .agg(
                                    IND_PER_SAI_CIAP=('IND_PER_SAI_CIAP', 'mean'),
                                    VL_ICMS=('total', 'sum')
                                )
                            .reset_index()
                            .assign(VL_ICMS_REC=lambda x: x['IND_PER_SAI_CIAP'] * x['VL_ICMS'])
                           )
    
    # excluir outliers da média, CV do indice de apropriação costuma ser baixo. Por isso usamos Tukey
    q1 = df_IND_PER_SAI_CIAP['IND_PER_SAI_CIAP'].quantile(0.25)
    q3 = df_IND_PER_SAI_CIAP['IND_PER_SAI_CIAP'].quantile(0.75)
    iqr = q3 - q1

    limite_inf = q1 - 1.5 * iqr
    limite_sup = q3 + 1.5 * iqr

    df_IND_PER_SAI_CIAP['FLG_OUTLIER'] = np.where(df_IND_PER_SAI_CIAP['IND_PER_SAI_CIAP'].between(limite_inf, limite_sup),
                                                  0,
                                                  1                                                    
                                                 )

    df_IND_PER_SAI_CIAP.to_sql("IND_PER_SAI_CIAP", con, if_exists='replace', index=False)
    df_IND_PER_SAI_CIAP = df_IND_PER_SAI_CIAP[df_IND_PER_SAI_CIAP['FLG_OUTLIER']==0]
    if ICMS_FLG:
        IND_MEDIA_PER_SAI_CIAP = np.where(df_IND_PER_SAI_CIAP['VL_ICMS'].sum() == 0,
                                      1,
                                      df_IND_PER_SAI_CIAP['VL_ICMS_REC'].sum() / df_IND_PER_SAI_CIAP['VL_ICMS'].sum()
                                      )
    else:
        IND_MEDIA_PER_SAI_CIAP = 1

    
    BP_EC_AVALc['VL_CALC_ICMS_TOT_CIAP'] = (BP_EC_AVALc['VL_ICMS_OP_APLICADO_CIAP'].fillna(0) +
                                            BP_EC_AVALc['VL_ICMS_ST_APLICADO_CIAP'].fillna(0) + 
                                            BP_EC_AVALc['VL_ICMS_FRT_APLICADO_CIAP'].fillna(0) + 
                                            BP_EC_AVALc['VL_ICMS_DIF_APLICADO_CIAP'].fillna(0))
    
    itens_declarados_CIAP = set(
                            BP_EC_AVALc.loc[
                                (BP_EC_AVALc['IND_CONC_CIAP'] != 'Somente EFD ou ERP, verifique') &
                                BP_EC_AVALc['IND_CONC_CIAP'].notnull(),
                                'COD_ITEM'
                            ]
                        )

    cd_itens_crd = [
                        item
                        for item in BP_EC_AVALc[BP_EC_AVALc['COD_ITEM'].notnull()]['COD_ITEM'].drop_duplicates()
                        if item in itens_declarados_CIAP
                    ]
    IND_CIAP_MEDIO = BP_EC_AVALc[BP_EC_AVALc['IND_PER_SAI_CIAP'].notnull()]['IND_PER_SAI_CIAP'].mean()
    mask = BP_EC_AVALc['COD_ITEM'].isin(cd_itens_crd) & BP_EC_AVALc['IND_PER_SAI_CIAP'].isnull()
    BP_EC_AVALc.loc[mask, 'IND_PER_SAI_CIAP'] = IND_CIAP_MEDIO
    BP_EC_AVALc.loc[BP_EC_AVALc['IND_PER_SAI_CIAP'].isnull(), 'IND_PER_SAI_CIAP'] = 0
    nova_obs = "Item não usado no CIAP, porém detectado que usualmente tem direito a crédito"
    BP_EC_AVALc['IND_CONC_CIAP'] = BP_EC_AVALc['IND_CONC_CIAP'].astype('string')
    BP_EC_AVALc.loc[mask, 'IND_CONC_CIAP'] = (
                                        BP_EC_AVALc.loc[mask, 'IND_CONC_CIAP']
                                        .fillna('')
                                        .astype(str)
                                        .str.rstrip()
                                        + np.where(
                                            BP_EC_AVALc.loc[mask, 'IND_CONC_CIAP'].fillna('').str.strip().eq(''),
                                            '',
                                            ' | '
                                        )
                                        + nova_obs
                                    )              

    aliquotas_internas = {
                            'AC': 0.190,
                            'AL': 0.205,
                            'AP': 0.180,
                            'AM': 0.200,
                            'BA': 0.205,
                            'CE': 0.200,
                            'DF': 0.200,
                            'ES': 0.170,
                            'GO': 0.190,
                            'MA': 0.230,
                            'MT': 0.170,
                            'MS': 0.170,
                            'MG': 0.180,
                            'PA': 0.190,
                            'PB': 0.200,
                            'PR': 0.195,
                            'PE': 0.205,
                            'PI': 0.225,
                            'RJ': 0.200,
                            'RN': 0.200,
                            'RS': 0.170,
                            'RO': 0.195,
                            'RR': 0.200,
                            'SC': 0.170,
                            'SP': 0.180,
                            'SE': 0.200,
                            'TO': 0.200,
                        }
    
    # Teste razoabilidade DIFAL
    df_DIFAL = BP_EC_AVALc[[ 'Id_Ext_CMP','Txt_Nom_Forn','Cd_Forn','CNPJ','SER','NUM_DOC',
                            'Dt_NF','Txt_Desc_Mat','Cd_NCM','Cd_EXTIPI','Cd_CFOP','VL_TOT_ICMS',
                                'VL_DIFAL','VL_TOT_IPI','VL_TOT_LIQ','VL_ST']].copy()
    df_0000 = pd.read_sql("SELECT t1.[9] AS UF FROM Arq_0 t1 WHERE t1.[1] = '0000'", con_efd) 
    df_DIFAL['UF'] = df_0000.iloc[0,0].upper()
    df_DIFAL['ALIQ_INTERNA_UF'] = aliquotas_internas[df_0000.iloc[0,0].upper()]
    df_DIFAL['ALIQ_INTERNA_UF'] = df_DIFAL['ALIQ_INTERNA_UF'].fillna(0.17)

    icms_nfe = df_DIFAL['VL_TOT_ICMS']
    ipi_nfe = df_DIFAL['VL_TOT_IPI']
    valor_liquido = df_DIFAL['VL_TOT_LIQ']
    difal_informado = df_DIFAL['VL_DIFAL']
    aliquota_interna = df_DIFAL['ALIQ_INTERNA_UF']

    df_DIFAL['DIFAL_ESPERADO'] = (
                                    (
                                        aliquota_interna
                                        .div(1 - aliquota_interna)
                                        .mul(ipi_nfe + valor_liquido)
                                    )
                                    - icms_nfe
                                ).round(2)
    mask = df_DIFAL['Cd_CFOP'].str[:1] != '2'
    df_DIFAL.loc[mask, 'DIFAL_ESPERADO'] = 0
    df_DIFAL['DIFAL_ESPERADO'] = df_DIFAL['DIFAL_ESPERADO'].clip(lower=0)
    df_DIFAL['DIFERENCA_DIFAL'] = (
                                        difal_informado - df_DIFAL['DIFAL_ESPERADO']
                                    ).round(2)
    tolerancia = 0.02

    df_DIFAL['DIFAL_CORRETO'] = (
                                    df_DIFAL['ALIQ_INTERNA_UF'].notna()
                                    & df_DIFAL['DIFERENCA_DIFAL'].ge(tolerancia)
                                )

    df_DIFAL['STATUS_DIFAL'] = np.select(
                                            [
                                                df_DIFAL['ALIQ_INTERNA_UF'].isna(),
                                                df_DIFAL['DIFAL_CORRETO'],
                                            ],
                                            [
                                                'UF NÃO ENCONTRADA',
                                                'OK',
                                            ],
                                            default='DIVERGENTE',
                                        )

    df_DIFAL[df_DIFAL['Cd_CFOP'].isin(LST_CFOP_INV)].to_csv(f"{dir_arq_saida}/difal_EC.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/difal_EC.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    #BP_EC_AVALc.loc[mask, 'VL_CALC_ICMS_TOT_CIAP'] = BP_EC_AVALc.loc[mask, 'VL_TOT_ICMS'] + BP_EC_AVALc.loc[mask, 'VL_DIFAL']

    BP_EC_AVALc['VL_CALC_ICMS_NR_CIAP'] = BP_EC_AVALc['VL_CALC_ICMS_TOT_CIAP'].fillna(0) * (1 - BP_EC_AVALc['IND_PER_SAI_CIAP'].fillna(0))
    #BP_EC_AVALc.loc[mask, 'VL_CALC_ICMS_NR_CIAP'] = BP_EC_AVALc.loc[mask, 'VL_CALC_ICMS_TOT_CIAP']
    # vamos limitar os itens que deu problema
    if FLG_DIFAL:
        mask = (
                    df_DIFAL['ALIQ_INTERNA_UF'].notna()
                    & df_DIFAL['DIFERENCA_DIFAL'].gt(tolerancia)
                    & df_DIFAL['VL_DIFAL'].abs().gt(tolerancia)
                )

        BP_EC_AVALc.loc[mask, 'VL_DIFAL'] = df_DIFAL.loc[mask, 'DIFAL_ESPERADO']

    
    if ICMS_FLG == 1:
        base_icms = BP_EC_AVALc['VL_TOT_ICMS'].fillna(0) + BP_EC_AVALc['VL_DIFAL'].fillna(0)
        BP_EC_AVALc.loc[BP_EC_AVALc['FLG_ICMS'] == 1, 
                        'VL_CALC_ICMS_TOTs'] = (
                            base_icms * BP_EC_AVALc['FR_ICMS'] * BP_EC_AVALc['FR'] + 
                            base_icms * (1 - BP_EC_AVALc['FR_ICMS'])
                            )
        BP_EC_AVALc['VL_CALC_ICMS_TOTs'] = BP_EC_AVALc['VL_CALC_ICMS_TOTs'].fillna(0)
        BP_EC_AVALc.loc[BP_EC_AVALc['FLG_ICMS'] == 1, 'VL_CALC_ICMS_NRs'] =(
                            base_icms * (1 -BP_EC_AVALc['FR_ICMS'])
                            )
        BP_EC_AVALc['VL_CALC_ICMS_NRs'] = BP_EC_AVALc['VL_CALC_ICMS_NRs'].fillna(0)

        # Pode ocorrer de não encontrar CIAP.
        # Se a empresa afirma que credita ICMS, FLG_ICMS, usamos o CIAP do EFD, caso não tenha EFD, presumimos a partir do ECD
        mask =  BP_EC_AVALc['VL_CALC_ICMS_TOT_CIAP'] != 0
        BP_EC_AVALc.loc[(BP_EC_AVALc['FLG_ICMS'] == 1) & mask, 
                        'VL_CALC_ICMS_TOT'] = (
                            BP_EC_AVALc['VL_CALC_ICMS_TOT_CIAP'] * BP_EC_AVALc['FR_ICMS'] * BP_EC_AVALc['FR'] + 
                            BP_EC_AVALc['VL_CALC_ICMS_NR_CIAP'] + (BP_EC_AVALc['VL_TOT_ICMS'].fillna(0) + 
                            BP_EC_AVALc['VL_DIFAL'].fillna(0) - BP_EC_AVALc['VL_CALC_ICMS_TOT_CIAP']).clip(0)
                            )
        BP_EC_AVALc.loc[(BP_EC_AVALc['FLG_ICMS'] == 1) & mask, 'VL_CALC_ICMS_NR'] =(
                            BP_EC_AVALc['VL_CALC_ICMS_NR_CIAP'] + (BP_EC_AVALc['VL_TOT_ICMS'].fillna(0) + 
                            BP_EC_AVALc['VL_DIFAL'].fillna(0) - BP_EC_AVALc['VL_CALC_ICMS_TOT_CIAP']).clip(0)
                            )

        BP_EC_AVALc.loc[(BP_EC_AVALc['FLG_ICMS'] == 1) & (~mask), 'VL_CALC_ICMS_NR'] =(
                                    BP_EC_AVALc.loc[(BP_EC_AVALc['FLG_ICMS'] == 1) & (~mask), 'VL_CALC_ICMS_NRs']
                                    )
        BP_EC_AVALc.loc[(BP_EC_AVALc['FLG_ICMS'] == 1) & (~mask), 
                        'VL_CALC_ICMS_TOT'] = (
                            BP_EC_AVALc.loc[(BP_EC_AVALc['FLG_ICMS'] == 1) & (~mask), 
                                                    'VL_CALC_ICMS_TOTs'] 
                            )
        
    else:
        fator_corrigido = BP_EC_AVALc[['VL_TOT_ICMS', 'VL_DIFAL']].sum(axis=1)
        for coluna in ['VL_CALC_ICMS_TOT','VL_CALC_ICMS_NR','VL_CALC_ICMS_TOTs','VL_CALC_ICMS_NRs']:
            BP_EC_AVALc[coluna] = fator_corrigido

    LST_MAT_SDI = LST_MAT[['COD_ITEM', 'Cd_DE_PARA']].copy()
    LST_MAT_SDI['Cd_DE_PARA'] = LST_MAT_SDI['Cd_DE_PARA'].fillna(LST_MAT_SDI['COD_ITEM'])
    BP_EC_AVALd = BP_EC_AVALc.loc[BP_EC_AVALc['Cd_NG_EC'] == '1'].merge(LST_MAT_SDI, on='COD_ITEM', how='left')

    BP_EC_AVALc.to_sql("BP_EC_AVALc", con, if_exists='replace', index=False)
    BP_EC_AVALd['FLG_BPR'] = BP_EC_AVALd['FLG_BPR'].replace('', '0')
    BP_EC_AVALd['Cd_JUN'] = 'N'
    BP_EC_AVALd.to_csv(f"{dir_arq_saida}/EC_completo.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/EC_completo.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    nom_col = (['FLG_BPR','FLG_TP','CNPJ','SER','NUM_DOC','Dt_NF','COD_ITEM','Cd_JUN','Cd_DE_PARA',
           'Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','Txt_Desc_Mat','DESCR_COMPL','Cd_Unid','QTD',
           'VL_ITEM_EFD','VL_DESC_NF','VL_ABAT_NT','VL_TOT_LIQ','VL_IPI','VL_ICMS','VL_DIFAL','VL_ST','VL_ODC',
           'VL_CALC_ICMS_TOTs', 'VL_CALC_ICMS_NRs', 'VL_CALC_ICMS_TOT', 'VL_CALC_ICMS_NR', 'FLG_ICMS','FLG_TPNF', 
           'Nm_Arq_EFD', 'DT_INI_CIAP',  'IND_PER_SAI_CIAP', 'COD_IND_BEM_CIAP',  'DT_MOV_CIAP',  'TIPO_MOV_CIAP',  
           'IND_EMIT_CIAP', 'COD_PART_CIAP',  'COD_MOD_CIAP', 'SERIE_CIAP', 'NUM_DOC_CIAP', 'DT_DOC_CIAP', 
           'COD_ITEM_CIAP', 'QTDE_CIAP', 'UNID_CIAP', 'VL_ICMS_OP_APLICADO_CIAP', 'VL_ICMS_ST_APLICADO_CIAP', 
           'VL_ICMS_FRT_APLICADO_CIAP', 'VL_ICMS_DIF_APLICADO_CIAP','Cd_FOR_COGE'] + nm_col_vPC + 
            nm_col_dPC + ['FLG_IMP'])

    if st: avl.progress(95, "Atualizando o fluxo financeiro de pagamentos...")

    TAB_CALC_BP = BP_EC_AVALd[nom_col].copy()

    crit = (TAB_CALC_BP['VL_CALC_ICMS_TOT'] == 0) | TAB_CALC_BP['VL_CALC_ICMS_TOT'].isnull()
    TAB_CALC_BP.loc[crit, ['VL_CALC_ICMS_TOT','VL_CALC_ICMS_NR']] = (TAB_CALC_BP.loc[crit, 'VL_ICMS'].fillna(0) +
                                                                     TAB_CALC_BP.loc[crit, 'VL_DIFAL'].fillna(0) )

    TAB_CALC_BP['CHAVE'] = 1
    TAB_CALC_BP['CHAVE'] = TAB_CALC_BP['CHAVE'].cumsum()
    
    cols = []
    tbl_FCOGE['DT_REF'] = pd.to_datetime(tbl_FCOGE['DT_REF'], errors='coerce')

    for k, nm_dt in enumerate(nm_col_dPC):
        df = TAB_CALC_BP[['Cd_FOR_COGE', nm_dt, 'CHAVE']].copy()
        df[nm_dt] = pd.to_datetime(df[nm_dt], format="%d/%m/%Y", errors='coerce')
        df[nm_dt] = df[nm_dt] + MonthBegin(-1) #+ DateOffset(months=1)
        df.columns = ['Cd_FOR_COGE','DT_REF','CHAVE']
        df = df.merge(tbl_FCOGE, how='left', on=['Cd_FOR_COGE', 'DT_REF'])
        df = df[['CHAVE', 'DT_REF', 'FC']]
        df.columns = ['CHAVE', f'DT_REF_{k+1}', f'FC_{k+1}']
        if k==0:
            df_FIM = df.copy()
        else:
            df_FIM = df_FIM.merge(df[['CHAVE', f'DT_REF_{k+1}', f'FC_{k+1}']], how='left', on=['CHAVE'])
        cols= cols + [f'FC_{k+1}']

    TAB_CALC_BP=TAB_CALC_BP.merge(df_FIM, on=['CHAVE'], how='left')
    TAB_CALC_BP['Dt_NF'] = pd.to_datetime(TAB_CALC_BP['Dt_NF'], format='%Y/%m/%d', errors='coerce')

    sumCOL = []
    TAB_CALC_BP['VL_TOT_LIQ'] = TAB_CALC_BP['VL_TOT_LIQ'].fillna(0)
    TAB_CALC_BP['VL_IPI'] = TAB_CALC_BP['VL_IPI'].fillna(0)
    TAB_CALC_BP['VL_ODC'] = TAB_CALC_BP['VL_ODC'].fillna(0)
    TAB_CALC_BP['VL_CALC_ICMS_TOT'] = TAB_CALC_BP['VL_CALC_ICMS_TOT'].fillna(0)
    TAB_CALC_BP['VL_CALC_ICMS_NR'] = TAB_CALC_BP['VL_CALC_ICMS_NR'].fillna(0)
    
    dt_ini = pd.to_datetime(dt_ini_proc, errors='coerce')
    dt_fim = pd.to_datetime(dt_fim_proc, errors='coerce')

    # caso uma parcela seja superior ao período incremental, todas as parcelas são a preços históricos
    cond_dt_ref_sup_dt_fim = pd.concat([TAB_CALC_BP[f'DT_REF_{k+1}'] > dt_fim for k, _ in enumerate(nm_col_dPC)],axis=1).any(axis=1)

    for nr, n in enumerate(nm_col_vPC):
        TAB_CALC_BP.loc[cond_dt_ref_sup_dt_fim, f'FC_{nr+1}'] = 1

    for nr, n in enumerate(nm_col_vPC):
        TAB_CALC_BP[n] = TAB_CALC_BP[n].fillna(0)
        TAB_CALC_BP[f'FC_{nr+1}'] = TAB_CALC_BP[f'FC_{nr+1}'].fillna(1)
        TAB_CALC_BP[f'VL_PC_AT_{nr+1}']=(
                                            (
                                                TAB_CALC_BP['VL_TOT_LIQ'] + TAB_CALC_BP['VL_IPI'] + TAB_CALC_BP['VL_ODC'] + 
                                                TAB_CALC_BP['VL_CALC_ICMS_TOT']
                                            ) * TAB_CALC_BP[n] * TAB_CALC_BP[f'FC_{nr+1}']
                                        )
        sumCOL.append(f'VL_PC_AT_{nr+1}')
        
    TAB_CALC_BP['VL_PC_AT'] = TAB_CALC_BP[sumCOL].sum(axis=1)

    condicoes = [
                    ((TAB_CALC_BP[f'DT_REF_{k+1}'] <= (dt_fim + pd.Timedelta(days=30))) & 
                    (TAB_CALC_BP[f'DT_REF_{k+1}'] >= dt_ini)) | TAB_CALC_BP[f'DT_REF_{k+1}'].isnull()
                    for k, _ in enumerate(nm_col_dPC)
                ]

    TAB_CALC_BP['PER_INC'] = pd.concat(condicoes, axis=1).any(axis=1).astype(int)
    TAB_CALC_BP.to_sql("TAB_CALC_BP", con, if_exists='replace', index=False)
    TAB_CALC_BP.to_excel(f"{dir_arq_saida}/TAB_CALC_BP.xlsx", index=False)
    #Sintese do resultado do banco de preços do VF

    mask = ((TAB_CALC_BP['VL_PC_AT'] == 0) 
            & (TAB_CALC_BP['FLG_TP'].astype(str)=='1') 
            & (TAB_CALC_BP['FLG_BPR'].astype(str)=='1')
            & (TAB_CALC_BP['PER_INC']==1) 
            & (TAB_CALC_BP['QTD'].fillna(0)!=0))
    
    teste_FlxPG = TAB_CALC_BP[mask][['CNPJ', 'SER', 'NUM_DOC', 'Dt_NF']].drop_duplicates().copy()
    teste_FlxPG.to_csv(rf"{dir_arq_saida}/dados_BPFP_ausentes.csv", sep="|", decimal=",", encoding='latin-1', index=False)
    teste_FlxPG.to_sql('tbl_FlxPG_AUS', con, if_exists='replace', index=False)    
    TAB_CALC_BP.to_excel(f"{dir_arq_saida}/TAB_ORG.xlsx", index=False)

    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/dados_BPFP_ausentes.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        registrar_artefato(st.session_state.database_MAN, 
                                    st.session_state.execucao_id, 
                                    file_path = rf'{dir_arq_saida}/TAB_ORG.xlsx',
                                    tipo_artefato = "SAIDA", 
                                    calcular_hash = True)
  
    TAB_ORG = TAB_CALC_BP[(TAB_CALC_BP['VL_PC_AT'] != 0) & (TAB_CALC_BP['FLG_TP'].astype(str)=='1') & (TAB_CALC_BP['FLG_BPR'].astype(str)=='1')
                        & (TAB_CALC_BP['PER_INC']==1) & (TAB_CALC_BP['QTD']>=0)].copy()
    
    TAB_ORG = (TAB_ORG[TAB_ORG['QTD'] >= 0]
               .groupby(by=['Cd_DE_PARA','CNPJ','SER','NUM_DOC','Dt_NF'],dropna=False)[['QTD','VL_PC_AT']]
               .sum().reset_index())

    TAB_ORG['VL_UNI_AT'] = TAB_ORG['VL_PC_AT'] / TAB_ORG['QTD']
    TAB_ORG['VL_UNI_AT'] = TAB_ORG['VL_UNI_AT'].fillna(0)

    TAB_SOMA = (TAB_ORG
                .groupby('Cd_DE_PARA',dropna=False)[['QTD','VL_PC_AT']]
                .sum().reset_index()
                .rename(columns={'Cd_DE_PARA':'COD_ITEM'}))
    
    TAB_SOMA['VL_UNI_AT'] = TAB_SOMA['VL_PC_AT']/TAB_SOMA['QTD']

    TAB_MIN = (TAB_ORG
               .groupby('Cd_DE_PARA',dropna=False)[['VL_UNI_AT']]
               .min().reset_index()
               .rename(columns={'Cd_DE_PARA':'COD_ITEM', 'VL_UNI_AT':'VL_UNI_MIN'}))
    
    TAB_MAX = (TAB_ORG
               .groupby('Cd_DE_PARA', dropna=False)[['VL_UNI_AT']]
               .max().reset_index()
               .rename(columns={'Cd_DE_PARA':'COD_ITEM', 'VL_UNI_AT':'VL_UNI_MAX'}))
    
    TAB_STD = (TAB_ORG
               .groupby('Cd_DE_PARA',dropna=False)[['VL_UNI_AT']]
               .std().reset_index()
               .rename(columns={'Cd_DE_PARA':'COD_ITEM', 'VL_UNI_AT':'VL_UNI_STD'}))

    TAB_MIN_MAX = (TAB_ORG
                   .groupby('Cd_DE_PARA')
                   .apply(valor_na_data_min_max).reset_index()
                   .rename(columns={'Cd_DE_PARA':'COD_ITEM'}))
    
    TAB_QTD_CMP = (TAB_ORG
                   .groupby('Cd_DE_PARA')[['VL_UNI_AT']]
                   .count().reset_index()
                   .rename(columns={'Cd_DE_PARA':'COD_ITEM', 'VL_UNI_AT':'QTD_CMP'}))
    
    TAB_CARAC = (TAB_CALC_BP[['Cd_DE_PARA','Nr_TUC','Nr_A1','Nr_A2','Nr_A3',
                              'Nr_A4','Nr_A5','Nr_A6','Cd_FOR_COGE']]
                              .rename(columns={'Cd_DE_PARA':'COD_ITEM'})
                              .drop_duplicates('COD_ITEM'))

    TAB_FIM = ( 
                TAB_SOMA
                .merge(TAB_MIN, how='left', on = 'COD_ITEM')
                .merge(TAB_MAX, how='left', on = 'COD_ITEM')
                .merge(TAB_STD, how='left', on = 'COD_ITEM')
                .merge(TAB_QTD_CMP, how='left', on = 'COD_ITEM')
                .merge(TAB_MIN_MAX, how='left', on = 'COD_ITEM')
               )
    
    TAB_FIM['CV'] = (TAB_FIM['VL_UNI_STD'] / TAB_FIM['VL_UNI_AT'])
    TAB_FIM['CV'] = TAB_FIM['CV'].fillna(0)
    TAB_FIM['FCr'] = TAB_FIM['VL_Dt_max'] / TAB_FIM['VL_Dt_min']
    TAB_FIM['VAR_PER'] = (TAB_FIM['VL_UNI_MAX'] - TAB_FIM['VL_UNI_MIN']) / TAB_FIM['VL_UNI_MIN']
    TAB_FIM['VAR_PER1'] = (TAB_FIM['VL_Dt_max'] - TAB_FIM['VL_Dt_min']) / TAB_FIM['VL_Dt_min']
    TAB_FIM['IND_MAT'] = round(np.log1p(TAB_FIM['VL_PC_AT'].abs()) / np.log(10), 2)
    TAB_FIM['OBS_SFF'] = ""
    TAB_FIM = TAB_FIM.sort_values(by=['VL_PC_AT'], ascending=False)
    TAB_FIM['Pct_ACM'] = TAB_FIM['VL_PC_AT'].cumsum()
    TAB_FIM['Pct_ACM'] = TAB_FIM['Pct_ACM'] / TAB_FIM['VL_PC_AT'].sum()

    crit_HF = TAB_FIM['QTD_CMP'] < 10
    crit_CV_EST = TAB_FIM['CV'] <= 0.15
    crit_CV_INZ = (TAB_FIM['CV'] > 0.15) & (TAB_FIM['CV'] <= 0.30)
    crit_CV_CRIT = TAB_FIM['CV'] > 0.30
    crit_SUB = TAB_FIM['VAR_PER1'] > 0.05
    crit_DES = TAB_FIM['VAR_PER1'] < -0.05
    crit_MAT = TAB_FIM['Pct_ACM'] < 0.85

    TAB_FIM.loc[crit_HF, 'OBS_SFF'] = "Histórico em formação ou compra esporádica, serve como referência de teto e piso."
    TAB_FIM.loc[~crit_HF & 
                crit_CV_EST & 
                crit_SUB, 
                'OBS_SFF'] = "Histórico de compra indica preços estáveis, tendência de subida, baseado na primeira e última compra."
    TAB_FIM.loc[~crit_HF & 
                crit_CV_EST & 
                crit_DES, 
                'OBS_SFF'] = "Histórico de compra indica preços estáveis, tendência de queda, baseado na primeira e última compra."
    TAB_FIM.loc[~crit_HF & 
                crit_CV_EST & 
                ~crit_DES & 
                ~crit_SUB, 
                'OBS_SFF'] = "Histórico de compra indica preços estáveis, sem tendência."
    TAB_FIM.loc[~crit_HF & 
                crit_CV_CRIT & 
                crit_MAT &
                crit_SUB, 
                'OBS_SFF'] = "Histórico de compra indica preços instáveis, oscilações nas compras, com materialidade, tendência de alta, baseado na primeira e última compra."
    TAB_FIM.loc[~crit_HF & 
                crit_CV_CRIT & 
                crit_MAT &
                crit_DES, 
                'OBS_SFF'] = "Histórico de compra indica preços instáveis, alta variabilidade, oscilações nas compras, com materialidade, tendência de queda, baseado na primeira e última compra."
    TAB_FIM.loc[~crit_HF & 
                crit_CV_CRIT & 
                ~crit_MAT, 
                'OBS_SFF'] = "Histórico de compra indica preços instáveis, alta variabilidade, oscilações nas compras, sem materialidade."
    TAB_FIM.loc[~crit_HF & 
                crit_CV_INZ & 
                crit_DES & 
                crit_MAT, 
                'OBS_SFF'] = "Histórico de compra indica dispersão moderada, oscilações nas compras podem ser efeitos sazonais ou descontos, com materialidade, tendência de queda, baseado na primeira e última compra."
    TAB_FIM.loc[~crit_HF & 
                crit_CV_INZ & 
                crit_SUB & 
                crit_MAT, 
                'OBS_SFF'] = "Histórico de compra indica dispersão moderada, oscilações nas compras podem ser efeitos sazonais ou descontos, com materialidade, tendência de alta, baseado na primeira e última compra."
    TAB_FIM.loc[~crit_HF & 
                crit_CV_INZ & 
                ~crit_MAT, 
                'OBS_SFF'] = "Histórico de compra indica dispersão moderada, oscilações nas compras podem ser efeitos sazonais ou descontos, sem materialidade."

    TAB_FIM = TAB_FIM.merge(TAB_CARAC, how='left', on='COD_ITEM')
    TAB_FIM=TAB_FIM[['COD_ITEM','Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_FOR_COGE',
                     'QTD','VL_PC_AT','QTD_CMP','VL_UNI_AT','VL_UNI_MIN','VL_UNI_MAX','VL_UNI_STD',
                     'Dt_min','VL_Dt_min','Dt_max','VL_Dt_max','VAR_PER','CV','FCr','IND_MAT','OBS_SFF']]
    
    TAB_FIM.to_sql("TAB_FIM", con, if_exists='replace', index=False)
    TAB_FIM.to_excel(f"{dir_arq_saida}/tab_fim.xlsx", index=False)
    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/tab_fim.xlsx',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    
    #cálculo do custo unitário por codificação contábil
    TAB_FIM_ax = TAB_FIM[(TAB_FIM['Cd_FOR_COGE']!='ND') & (TAB_FIM['Cd_FOR_COGE'].notnull())].copy()
    TAB_FIM_BPC=TAB_FIM_ax.groupby(['Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_FOR_COGE'])[['QTD','VL_PC_AT']].sum().reset_index()
    TAB_FIM_BPC['VL_UNI_AT']=TAB_FIM_BPC['VL_PC_AT']/TAB_FIM_BPC['QTD']
    TAB_FIM_BPC.to_sql("TAB_FIM_BPC", con, if_exists='replace', index=False)

    #montagem do custo unitário por COD_ITEM
    TAB_COR_ITEM = TAB_FIM[(TAB_FIM['Cd_FOR_COGE']!='ND') & (TAB_FIM['Cd_FOR_COGE'].notnull())][['COD_ITEM','Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_FOR_COGE','QTD','VL_PC_AT']].copy()
    TAB_COR_ITEM.groupby(['COD_ITEM','Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_FOR_COGE'], dropna=False)[['QTD','VL_PC_AT']].sum().reset_index()
    TAB_COR_ITEM['VL_UNI_AT'] = TAB_COR_ITEM['VL_PC_AT'] / TAB_COR_ITEM['QTD']
    TAB_COR_ITEM.to_sql("TAB_COR_ITEM", con, if_exists='replace', index=False)
    TAB_COR_ITEM.to_excel(f"{dir_arq_saida}/tab_COR_ITEM.xlsx", index=False)
    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_saida}/tab_COR_ITEM.xlsx',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)

    if st: avl.progress(98, "Avaliando OUTLIERS...")

    #Foi agregado esse teste para ajudar a encontrar itens outliers, usando TUKEY
    teste = TAB_CALC_BP[(TAB_CALC_BP['FLG_TP'].astype(str)=='1') & (TAB_CALC_BP['FLG_TPNF'].astype(str)=='1')].copy()
    col_ANL = ['COD_ITEM', 'CNPJ', 'SER','NUM_DOC', 'Dt_NF', 'Txt_Desc_Mat', 'QTD', 'Cd_Unid', 'VL_ICMS',
               'VL_IPI', 'VL_TOT_LIQ', 'VL_PC_AT']

    teste = teste[col_ANL]
    teste['CMU'] = teste['VL_PC_AT'] / teste['QTD']
    teste['COD_ITEM'] = teste['COD_ITEM'].fillna("ND")
    TAB_MIN = (teste
               .groupby('COD_ITEM')[['CMU']]
               .min().reset_index()
               .rename(columns={'CMU':'CMU_MIN'}))
    TAB_MAX = (teste
               .groupby('COD_ITEM')[['CMU']]
               .max().reset_index()
               .rename(columns={'CMU':'CMU_MAX'}))

    teste = ( 
                teste
                .merge(TAB_MIN, how='left', on = 'COD_ITEM')
                .merge(TAB_MAX, how='left', on = 'COD_ITEM')
            )

    # Calculando o IQR por código
    iqr_cd = teste.groupby('COD_ITEM')['CMU'].apply(calculate_iqr).reset_index()
    iqr_cd.columns = ['COD_ITEM', 'INTERQ']
    teste = teste.merge(iqr_cd, how = 'left', on = 'COD_ITEM')

    iqr_cd = teste.groupby('COD_ITEM')['CMU'].apply(calculate_Q1).reset_index()
    iqr_cd.columns = ['COD_ITEM', 'Q1']
    teste = teste.merge(iqr_cd, how = 'left', on = 'COD_ITEM')

    iqr_cd = teste.groupby('COD_ITEM')['CMU'].apply(calculate_Q3).reset_index()
    iqr_cd.columns = ['COD_ITEM', 'Q3']
    teste = teste.merge(iqr_cd, how = 'left', on = 'COD_ITEM')

    iqr_cd = teste.groupby('COD_ITEM')['CMU'].apply(calculate_median).reset_index()
    iqr_cd.columns = ['COD_ITEM', 'MEDIANA']
    teste = teste.merge(iqr_cd, how = 'left', on = 'COD_ITEM')

    iqr_cd = teste.groupby('COD_ITEM')['CMU'].apply(calculate_std).reset_index()
    iqr_cd.columns = ['COD_ITEM', 'STD']
    teste = teste.merge(iqr_cd, how = 'left', on = 'COD_ITEM')

    teste['DESV_ABS'] = abs(teste['CMU'] - teste['MEDIANA'])
    iqr_cd = teste.groupby('COD_ITEM')['DESV_ABS'].apply(calculate_std).reset_index()
    iqr_cd.columns = ['COD_ITEM', 'MAD']
    teste = teste.merge(iqr_cd, how = 'left', on = 'COD_ITEM')

    teste['LIM_INF'] = teste['Q1'] - 1.5 * teste['INTERQ']
    teste.loc[teste['LIM_INF']<0, 'LIM_INF'] = 0
    teste['LIM_SUP'] = teste['Q3'] + 1.5 * teste['INTERQ']

    teste['ANL_OUTLIER'] = 'OK'

    teste['VAR_PER'] = (teste['CMU_MAX']-teste['CMU_MIN'])/teste['CMU_MIN']

    teste.loc[(abs(teste['CMU'] - teste['MEDIANA']) > 2 * teste['MAD'] ) & (teste['MAD'] > 0.1), 'ANL_OUTLIER'] = 'OUTLIER, CRITÉRIO MAD'
    teste.loc[(teste['CMU']<teste['LIM_INF']) | (teste['CMU']>teste['LIM_SUP']), 'ANL_OUTLIER'] = 'OUTLIER, CRITÉRIO TUKEY'

    iqr_cd = teste.groupby('COD_ITEM')[['VL_PC_AT', 'QTD']].apply(calculate_vlu).reset_index()

    iqr_cd.columns = ['COD_ITEM', 'VL_MED_ORI']
    teste = teste.merge(iqr_cd, how = 'left', on = 'COD_ITEM')

    iqr_cd = teste[(teste['ANL_OUTLIER'] == 'OK') | 
               (abs(teste['VAR_PER']) <= ((1.05**(dt_fim_proc.year-dt_ini_proc.year))-1))].groupby('COD_ITEM')[['VL_PC_AT', 
                                                                        'QTD']].apply(calculate_vlu).reset_index()
    iqr_cd.columns = ['COD_ITEM', 'VL_MED_MDF']
    teste = teste.merge(iqr_cd, how = 'left', on = 'COD_ITEM')
    teste.fillna(0, inplace = True)
    teste['DELTA_PC'] = (teste['VL_MED_MDF'] - teste['VL_MED_ORI']) / teste['VL_MED_ORI']
    teste['OBS_FISC'] = 'OK'
    teste.loc[(teste['ANL_OUTLIER'] != 'OK') & ((teste['DELTA_PC']) < -0.05) & (teste['CMU'] > teste['MEDIANA'])
            , 'OBS_FISC'] = 'Avaliar este lançamento, considerando todos os materiais deste código'
    teste.loc[(teste['DELTA_PC'] == -1) & (abs(teste['VAR_PER']) > ((1.05**(dt_fim_proc.year-dt_ini_proc.year))-1)), 'OBS_FISC'] = 'Avaliar este material, há uma variação significativa de preços (relação máximo/mínimo).'
    teste.loc[(teste['VL_PC_AT'] == 0), 'OBS_FISC'] = 'Avaliar este material, valor atualizado igual a zero (faltam dados no EC informado).'

    teste.loc[(teste['ANL_OUTLIER'] != 'OK') & ((teste['DELTA_PC']) > 0.05) & ((teste['MEDIANA']/teste['CMU'] > 5)
                                                                            | (teste['MEDIANA']/teste['CMU'] < 0.2))
            ,'OBS_FISC'] = 'Avaliar este lançamento, possível erro de lançamento'
    
    for col in teste.columns:
        if (teste[col].dtype == object) & (col[:2]=='Dt'):
            try:
                teste[col] = pd.to_datetime(teste[col], errors='coerce')
            except:
                pass
    teste.to_sql("TAB_OUTLIERS", con, if_exists='replace', index=False)    
      
    if st: avl.progress(99, "Comparando com dado da SDI-001...")
    if st.session_state.dt_fim <= date.today():
        if 'QTD' in BP_UAR.columns:
            BP_UAR = BP_UAR.rename(columns={'QTD': 'Qtd'})
        BP_UAR = BP_UAR[['Id_BP','COD_ITEM','Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','Qtd',
            'VL_VF','VL_ICMS','VL_ODC','Nr_FORM','VL_VF_UNIT_AT','Txt_OBS','COD_ITEM_DE']]
        lst_VLS = ['Qtd','VL_VF','VL_ICMS','VL_ODC','VL_VF_UNIT_AT']

        for nm in lst_VLS:
            if nm in BP_UAR.columns and BP_UAR[nm].dtype == 'object':
                BP_UAR[nm]=pd.to_numeric(BP_UAR[nm].astype(str).str.replace(',','.'), errors='coerce')
            
        BP_COMP = (
                    BP_UAR
                    .merge(TAB_COR_ITEM, on='COD_ITEM', how='outer', suffixes=("_AVL","_SIM"), indicator=True)
                    .rename(columns = {'Qtd' : 'Qtd_AVL', 'VL_VF' : 'VL_VF_AVL', 'VL_ICMS' : 'VL_ICMS_AVL',
                                       'VL_ODC' : 'VL_ODC_AVL', 'Nr_FORM' : 'Nr_FORM_AVL', 
                                       'VL_VF_UNIT_AT' : 'VL_VF_UNIT_AT_AVL', 'Txt_OBS' : 'Txt_OBS_AVL',
                                       'QTD': 'Qtd_SIM', 'VL_PC_AT' : 'VL_PC_AT_SIM', 'VL_UNI_AT':'VL_UNI_AT_SIM'})
                  )

        merge_map = {
                            'both': 'NO',
                            'left_only': 'Somente avaliadora',
                            'right_only': 'Somente simulado'
                        }
        BP_COMP['IND_CONC'] = BP_COMP['_merge'].replace(merge_map)
        BP_COMP = BP_COMP.drop(columns='_merge')
        BP_COMP = BP_COMP.merge(LST_ROA, on='COD_ITEM', how='left')
        x = BP_COMP.groupby(['COD_ITEM_DE'], dropna = False)[['Qtd_SIM','VL_PC_AT_SIM']].sum().reset_index()
        BP_COMP = BP_COMP.merge(x, on='COD_ITEM_DE', how='left', suffixes=("","_PRV"))
        
        BP_COMP['Qtd_SIM'] = BP_COMP['Qtd_SIM_PRV']
        BP_COMP['VL_PC_AT_SIM'] = BP_COMP['VL_PC_AT_SIM_PRV']
        BP_COMP = BP_COMP.drop(columns = ['Qtd_SIM_PRV','VL_PC_AT_SIM_PRV'])

        BP_COMP['VL_UNI_AT_SIM'] = BP_COMP['VL_PC_AT_SIM'] / BP_COMP['Qtd_SIM']
        BP_COMP['DELTA_Q'] = BP_COMP['Qtd_AVL'] - BP_COMP['Qtd_SIM']
        BP_COMP['DELTA_VL'] = BP_COMP['VL_VF_UNIT_AT_AVL'] - BP_COMP['VL_UNI_AT_SIM']

        BP_COMP['TST_01'] = 'ND'
        BP_COMP['TST_02'] = 'EMPREGADO ROA'
        BP_COMP['TST_03'] = 'AUSENTE LADO ANÁLISE: data pagamento fora do período ou não informado EC'

        crit_tuc_conc = BP_COMP['Nr_TUC_SIM'].eq(BP_COMP['Nr_TUC_AVL'])
        crit_tuc_null = BP_COMP['Nr_TUC_SIM'].isna()

        crit_cd_ng_null = BP_COMP['Cd_NG_ROA'].isna()
        crit_cd_ng_2 = BP_COMP['Cd_NG_ROA'].eq('2')

        crit_form_equal = BP_COMP['Nr_FORM_AVL'].eq(BP_COMP['Cd_FOR_COGE'])
        crit_form_notnull = BP_COMP['Cd_FOR_COGE'].notna()

        crit_form_nao_padrao = ~BP_COMP['Nr_FORM_AVL'].isin(['FCM0403', 'IPCA'])

        BP_COMP.loc[crit_tuc_conc, 'TST_01'] = 'CÓDIGO TUC CONCILIADO COM ROA'
        BP_COMP.loc[crit_tuc_null, 'TST_01'] = 'SEM CÓDIGO TUC NO ROA'
        BP_COMP.loc[crit_cd_ng_null, 'TST_01'] = 'SEM LANÇAMENTO NO ROA'

        BP_COMP.loc[
                        crit_tuc_null & BP_COMP['TST_02'].eq('EMPREGADO ROA'),
                        'TST_01'
                    ] = 'VERIFICAR DADOS AVALIADORA'

        BP_COMP.loc[crit_cd_ng_null, 'TST_02'] = 'AUSENTE NO ROA'

        BP_COMP.loc[
                        BP_COMP['Cd_NG_ROA'].notna() & crit_cd_ng_2,
                        'TST_02'
                    ] = 'EMPREGADO NO ROA, PORÉM COMO COM'

        BP_COMP.loc[crit_form_equal, 'TST_03'] = 'OK'

        BP_COMP.loc[
                        ~crit_form_equal & crit_form_notnull,
                        'TST_03'
                    ] = 'VERIFICAR Cd_FOR_COGE'

        BP_COMP.loc[
                        crit_tuc_null,
                        'TST_03'
                    ] = 'CÓDIGO AUSENTE NO ARQUIVO INC (BPR)'

        cond_sem_fcoge = crit_form_nao_padrao

        regras_fcoge = [
                            (
                                BP_COMP['Nr_TUC_AVL'].eq('135') & BP_COMP['Nr_A1_AVL'].eq('02') & cond_sem_fcoge,
                                'BARRAMENTO FLEXÍVEL, SEM FCOGE PRORET'
                            ),
                            (
                                BP_COMP['Nr_TUC_AVL'].eq('135') & BP_COMP['Nr_A1_AVL'].eq('01') & cond_sem_fcoge,
                                'BARRAMENTO RÍGIDO, SEM FCOGE PRORET'
                            ),
                            (
                                BP_COMP['Nr_TUC_AVL'].eq('265') & cond_sem_fcoge,
                                'SUPORTE, SEM FCOGE PRORET'
                            ),
                            (
                                BP_COMP['Nr_TUC_AVL'].eq('305') & cond_sem_fcoge,
                                'PAINEL, SEM FCOGE PRORET'
                            ),
                        ]

        for cond, msg in regras_fcoge:
            BP_COMP.loc[cond, 'TST_03'] = msg

        BP_COMP['TST_04'] = 'ND'

        mask_delta = BP_COMP['DELTA_VL'].ne('ND') & BP_COMP['VL_UNI_AT_SIM'].notna() & BP_COMP['VL_UNI_AT_SIM'].ne(0)

        BP_COMP.loc[mask_delta, 'TST_04'] = (
                                                BP_COMP.loc[mask_delta, 'DELTA_VL'].astype(float)
                                                / BP_COMP.loc[mask_delta, 'VL_UNI_AT_SIM'].astype(float)
                                            )
        LST_MAT_EC = TAB_CALC_BP[['COD_ITEM','Txt_Desc_Mat']].drop_duplicates('COD_ITEM')
        BP_COMP = BP_COMP.merge(LST_MAT_EC,on='COD_ITEM',how='left')

        BP_COMP.to_sql("BP_COMP", con, if_exists='replace', index=False)
        BP_COMP.to_excel(f"{dir_arq_saida}/bp_comp.xlsx", index=False)
        if st: 
            registrar_artefato(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                file_path = rf'{dir_arq_saida}/bp_comp.xlsx',
                                tipo_artefato = "SAIDA", 
                                calcular_hash = True)
        
    if st: avl.progress(100, "Finalizado!")
    return "OK"

def calc_incr(dir_arq_saida, dt_ini_proc, dt_fim_proc, ROA_RD, depr, con, Empresa, ano, st=None):
    
    if st: avl = st.progress(0, text = 'Iniciando os cálculos dos ativos incrementais, carregando IPCA...')
    ipca = busca_ipca(st)[['Dt_REF', 'Nr_IPCA']].rename(columns={'Dt_REF': 'DT_CMPT'})
    if st: avl.progress(5, text = 'Comparando os dados do VOC do arquivo Incremental com os valores ajustados pela Fiscalização...')

    SQLq = f"""
            SELECT 
                t1.Cd_SubODI, t1.VL_UAR_FISC, t1.VL_COM_FISC, t1.VL_MOP_FISC, t1.VL_ST_FISC,
                t1.VL_JOA_FISC, t1.VL_OUT_FISC, t1.VL_UC_ROA, t1.VL_COM_ROA, t1.VL_MOP_ROA,
                t1.VL_ST_ROA, t1.VL_JOA_ROA, t1.VL_OUT_ROA
            FROM 
                ROS_VAL t1 
            WHERE 
                t1.dt_ARQ = ? 
            """
    ROS_AJS = sql.imp_tbl_forma_001('ROS_VAL', SQLq = SQLq, con = con, st=st, Empresa=Empresa)

    SQLq = f"""
            SELECT 
                t1.Cd_ODI, t1.Cd_SubODI, t1.Pct_OE, t1.Cd_Tipo_OE
            FROM 
                ROS t1 
            WHERE 
                t1.dt_ARQ = ? 
            """
    ROS_SINT = sql.imp_tbl_forma_001('ROS', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
    
    if ROA_RD and (len(ROS_AJS) > 0):
        SQLq = f"""
                    SELECT 
                        t1.Cd_SubODI_ROS, t1.Cd_SubODI_AIS
                    FROM 
                        CD_SUBODI t1 
                    WHERE 
                        t1.dt_ARQ = ? 
                """
        DE_PARA_SUBODI = sql.imp_tbl_forma_001('CD_SUBODI', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
        if len(DE_PARA_SUBODI) > 0:
            DE_PARA_SUBODI.drop_duplicates('Cd_SubODI_ROS', inplace = True)
            ROS_AJS['Cd_SubODI'] = ROS_AJS['Cd_SubODI'].map(DE_PARA_SUBODI.set_index('Cd_SubODI_ROS')['Cd_SubODI_AIS'])

    for nm in ROS_AJS.columns.to_list():
        if ROS_AJS[nm].dtype == 'object' and nm[:2].upper() in ["VL"]:
            ROS_AJS[nm] = pd.to_numeric(ROS_AJS[nm].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')
    if len(ROS_AJS) != 0:
        ROA_TOT = (ROS_AJS[['Cd_SubODI','VL_UAR_FISC','VL_COM_FISC','VL_MOP_FISC','VL_ST_FISC',
                         'VL_JOA_FISC','VL_OUT_FISC','VL_UC_ROA','VL_COM_ROA','VL_MOP_ROA','VL_ST_ROA',
                         'VL_JOA_ROA','VL_OUT_ROA']]
                         .copy()
                         .rename(columns = {'VL_UAR_FISC' : 'VL_UC_CONS', 'VL_COM_FISC' : 'VL_COM_CONS',
                                            'VL_MOP_FISC' : 'VL_MOP_CONS', 'VL_ST_FISC' : 'VL_ST_CONS',
                                            'VL_JOA_FISC' : 'VL_JOA_CONS', 'VL_OUT_FISC' : 'VL_OUT_CONS',
                                            'VL_UC_ROA' : 'VL_UC_TOT', 'VL_COM_ROA' : 'VL_COM_TOT',
                                            'VL_MOP_ROA' : 'VL_MOP_TOT', 'VL_ST_ROA' : 'VL_ST_TOT',
                                            'VL_JOA_ROA' : 'VL_JOA_TOT', 'VL_OUT_ROA' : 'VL_OUT_TOT'})
                        .fillna(0))
    else:
        if st: st.error('Deves colocar o ROS_VALIDADO no arquivo de entrada.')
        else: raise UserWarning('Deves colocar o ROS_VALIDADO no arquivo de entrada.')

    SQLq = f"""
                SELECT 
                    t1.Cd_SubODI, t1.VL_VOC, t1.VL_VOC_VF_AVAL AS VL_UC_AVAL, t1.VL_VOC_COM_AVAL AS VL_COM_AVAL, 
                    t1.VL_VOC_CA_AVAL AS VL_CA_AVAL, t1.VL_VOC_JOA_AVAL AS VL_JOA_AVAL, t1.COD_ITEM, t1.Qtd_AIS, t1.Nr_TUC,
                    t1.Nr_A1, t1.Cd_UAR, t1.Cd_UND_AIS
                FROM 
                    INCR t1 
                WHERE 
                    t1.dt_ARQ = ?
            """
    INCR = sql.imp_tbl_forma_001('INCR', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
    
    for nm in INCR.columns.to_list():
        if INCR[nm].dtype == 'object' and nm[:2].upper() in ["VL", "QT"]:
            INCR[nm] = pd.to_numeric(INCR[nm].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')          
    INC_RES = (INCR
                .groupby(['Cd_SubODI'], dropna=False)[['VL_VOC','VL_UC_AVAL','VL_COM_AVAL',
                                                      'VL_CA_AVAL', 'VL_JOA_AVAL']]
                .sum()
                .reset_index())
    INC_RES['VL_CONS_INC'] = (INC_RES['VL_UC_AVAL'] + INC_RES['VL_COM_AVAL'] +
                              INC_RES['VL_CA_AVAL'] + INC_RES['VL_JOA_AVAL'])

    if sql.existe_tabela("ROA_PIVOT_NG_TOTAL", con):
        ROA = pd.read_sql("SELECT * FROM ROA_PIVOT_NG_TOTAL", con)
    else:
        SQLq = f"""
                    SELECT 
                        t1.Cd_SubODI, t1.Cd_NG, sum(t1.VL_tot) AS VL_TOT
                    FROM 
                        ROA t1 
                    WHERE 
                        t1.dt_ARQ = ?
                    GROUP BY
                        t1.Cd_SubODI, t1.Cd_NG
                """
        ROA = sql.imp_tbl_forma_001('ROA', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
        for nm in ROA.columns.to_list():
            if ROA[nm].dtype == 'object' and nm[:2].upper() in ["VL", "QT"]:
                ROA[nm] = pd.to_numeric(ROA[nm].astype(str).str.replace(',','.'), 
                                                            errors='coerce',
                                                            downcast='float')
        ROA = (ROA
                .pivot_table(values="VL_TOT", index="Cd_SubODI", 
                            columns="Cd_NG", aggfunc="sum", dropna=False, fill_value=0)
                .rename_axis(columns=None)
                .reset_index())
        for n in range(1, 7):
            if f"{n}" not in ROA.columns:
                ROA[f"{n}"] = 0
        ROA = ROA.rename(columns = {'1' : 'VL_UC_TOT', '2' : 'VL_COM_TOT', '3' : 'VL_MOP_TOT',
                                    '4' : 'VL_ST_TOT', '5' : 'VL_JOA_TOT', '6' : 'VL_OUT_TOT'})
        
        ROA.to_sql("ROA_PIVOT_NG_TOTAL", con, if_exists='replace', index=False)

    ROA['VL_CA_TOT'] = ROA['VL_MOP_TOT'] + ROA['VL_ST_TOT']
    # Projeto em mais de uma TI
    if len(ROA_TOT) != len(ROA_TOT.drop_duplicates('Cd_SubODI')):
        ROA_TOT = (ROA_TOT
                  .groupby(['Cd_SubODI'], dropna=False)[['VL_UC_CONS','VL_COM_CONS','VL_MOP_CONS',
                                                          'VL_ST_CONS','VL_JOA_CONS','VL_OUT_CONS',
                                                          'VL_UC_TOT','VL_COM_TOT','VL_MOP_TOT',
                                                          'VL_ST_TOT','VL_JOA_TOT','VL_OUT_TOT']]
                  .sum()
                  .reset_index())
    ROA_TOT['VL_CA_CONS'] = ROA_TOT['VL_MOP_CONS'] + ROA_TOT['VL_ST_CONS']
    ROA_TOT['VL_CA_TOT'] = ROA_TOT['VL_MOP_TOT'] + ROA_TOT['VL_ST_TOT']
    LST_SISTEMAS = ['100', '105', '110', '112', '115', '140', '145', '150', '155', '170', '175', '185', '205', '215', '220', '225', '240', '245', '260', 
                    '275', '280', '285', '300', '320', '335', '350', '355', '360', '365', '370', '375', '380', '385', '390', '395', '400', '405', '410', 
                    '415', '420', '425', '430', '435', '440', '445', '450', '455', '460', '465', '470', '475', '480', '485', '490', '500', '505', '510', 
                    '515', '520', '525', '530', '550', '555', '585', '590', '595', '600', '610']

    TST_CMP2 = INC_RES.merge(ROA_TOT[['Cd_SubODI', 'VL_UC_CONS','VL_COM_CONS','VL_CA_CONS',
                                    'VL_JOA_CONS','VL_UC_TOT','VL_COM_TOT','VL_CA_TOT',
                                    'VL_JOA_TOT']], how='left', on='Cd_SubODI', indicator=True)
    map_dict = {
                'both' : 'NO',
                'left_only': 'Somente no arquivo INCR, verificar',
                'right_only' : 'Somente no arquivo ROS_VAL, verificar'
            }
    TST_CMP2['OBS_CONC_ROS_VAL_vs_INCR'] = TST_CMP2['_merge'].map(map_dict)
    TST_CMP2 = TST_CMP2.drop(columns = '_merge')

    TST_CMP2 = TST_CMP2.merge(ROA[['Cd_SubODI', 'VL_UC_TOT','VL_COM_TOT','VL_CA_TOT',
                                'VL_JOA_TOT']], how='left', on='Cd_SubODI', indicator=True, suffixes=("","_ROA"))
    map_dict = {
                'both' : 'NO',
                'left_only': 'Somente no arquivo INCR/ROS_VAL, verificar',
                'right_only' : 'Somente no arquivo ROA, verificar'
            }
    TST_CMP2['OBS_CONC_ROA_vs_INCR'] = TST_CMP2['_merge'].map(map_dict)
    TST_CMP2 = TST_CMP2.drop(columns = '_merge')
    TST_CMP2, df_relatorio = comparar_componentes(TST_CMP2)
    TST_CMP2.to_sql("TST_CMP2_INCR", con, if_exists='replace', index=False)
    ipca.to_sql("IPCA_INCR", con, if_exists='replace', index=False)

    if st: avl.progress(10, text = 'Comparação de quantidade por código de material entre INCR e ROA...')

    SQLq = f"""
                SELECT 
                    t1.Cd_SubODI, t1.COD_ITEM, SUM(CAST(COALESCE(t1.Qtd,'0') AS REAL)) AS Qtd, 
                    t1.Nr_TUC, t1.Nr_A1, t1.Unidade
                FROM 
                    ROA t1 
                WHERE 
                    t1.dt_ARQ = ? AND t1.Cd_NG = 1
                GROUP BY
                    t1.Cd_SubODI, t1.COD_ITEM, t1.Nr_TUC, t1.Nr_A1, t1.Unidade
            """
    ROA = sql.imp_tbl_forma_001('ROA', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
    
    SQLq = f"""
                SELECT 
                    t1.COD_ITEM, t1.DESCR_ITEM, 
                    CAST(COALESCE(REPLACE(t1.Nr_FC, ',', '.'),'1') AS REAL) AS Nr_FC
                FROM 
                    LST_MAT t1 
                WHERE t1.dt_ARQ = ?
            """
    LST_MAT_SDI = sql.imp_tbl_forma_001('LST_MAT', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
    ROA_RES = (ROA
            .groupby(['Nr_TUC', 'COD_ITEM','Unidade'], dropna = False)[['Qtd']]
            .sum()
            .reset_index()
            .rename(columns={'Unidade' : 'Cd_UND', 'Qtd' : 'QTD_ROA'}))
    INCR_RES = (INCR[INCR['Cd_UAR'] != 'UAR']
                .groupby(['Nr_TUC','COD_ITEM','Cd_UND_AIS'], dropna = False)[['Qtd_AIS']]
                .sum()
                .reset_index()
                .rename(columns={'Cd_UND_AIS' : 'Cd_UND', 'Qtd_AIS' : 'QTD_INC'}))

    TST_CMP3 = INCR_RES.merge(ROA_RES, how='left', on=['Nr_TUC','COD_ITEM','Cd_UND'], indicator=True)
    TST_CMP3['FLG_EXC'] = np.where(TST_CMP3['Nr_TUC'].isin(LST_SISTEMAS),
                                True,
                                False)
    map_dict = {
                'both' : 'Ambos',
                'left_only': 'Somente no arquivo INCR',
                'right_only' : 'Somente no arquivo ROA'
            }
    TST_CMP3['OBS_CONC_ROA_vs_INCR'] = TST_CMP3['_merge'].map(map_dict)
    TST_CMP3 = TST_CMP3.drop(columns = '_merge') 
    TST_CMP3[['QTD_INC','QTD_ROA']] = TST_CMP3[['QTD_INC','QTD_ROA']].fillna(0)
    TST_CMP3['PCT_VAR'] = np.where(TST_CMP3['QTD_INC']>0,
                                    (TST_CMP3['QTD_INC']-TST_CMP3['QTD_ROA'])/TST_CMP3['QTD_INC'],
                                    np.inf)
    
    TST_CMP3=TST_CMP3.merge(LST_MAT_SDI, how='left', on='COD_ITEM')
    TST_CMP3['DESCR_ITEM'] = TST_CMP3['DESCR_ITEM'].fillna('AUSENTE TABELA LST_MAT')
    TST_CMP3['Nr_FC'] = TST_CMP3['Nr_FC'].fillna(1)
    crit1 = ((TST_CMP3['OBS_CONC_ROA_vs_INCR'] == 'Ambos') & (TST_CMP3['PCT_VAR'].abs()<0.001) &
            (~TST_CMP3['FLG_EXC']))
    crit2 = ((TST_CMP3['OBS_CONC_ROA_vs_INCR'] == 'Somente no arquivo INCR') &
            (~TST_CMP3['FLG_EXC']) & ( TST_CMP3['DESCR_ITEM'] == 'AUSENTE TABELA LST_MAT'))
    crit3 = ((TST_CMP3['OBS_CONC_ROA_vs_INCR'] == 'Somente no arquivo INCR') &
            (~TST_CMP3['FLG_EXC']) & ( TST_CMP3['DESCR_ITEM'] != 'AUSENTE TABELA LST_MAT'))
    crit4 = ((TST_CMP3['OBS_CONC_ROA_vs_INCR'] == 'Somente no arquivo ROA') &
            (~TST_CMP3['FLG_EXC']) & ( TST_CMP3['DESCR_ITEM'] == 'AUSENTE TABELA LST_MAT'))
    crit5 = ((TST_CMP3['OBS_CONC_ROA_vs_INCR'] == 'Somente no arquivo ROA') &
            (~TST_CMP3['FLG_EXC']) & ( TST_CMP3['DESCR_ITEM'] != 'AUSENTE TABELA LST_MAT'))
    crit6 = ((TST_CMP3['OBS_CONC_ROA_vs_INCR'] == 'Ambos') &
            (~TST_CMP3['FLG_EXC']) & (TST_CMP3['PCT_VAR'] >= 0.001))
    crit7 = ((TST_CMP3['OBS_CONC_ROA_vs_INCR'] == 'Ambos') &
            (~TST_CMP3['FLG_EXC']) & (TST_CMP3['PCT_VAR'] <= -0.001))
    
    TST_CMP3.loc[crit1, 'OBS_SFF'] = 'NO'
    TST_CMP3.loc[crit2, 'OBS_SFF'] = 'Código ausente na lista material e no ROA, preencher o código ou justificar'
    TST_CMP3.loc[crit3, 'OBS_SFF'] = 'Código ausente no ROA, preencher o código ou justificar'
    TST_CMP3.loc[crit4, 'OBS_SFF'] = 'Código ausente na lista material e no INCR, preencher o código ou justificar'
    TST_CMP3.loc[crit5, 'OBS_SFF'] = 'Código ausente no INCR, preencher o código ou justificar'
    TST_CMP3.loc[crit6, 'OBS_SFF'] = 'Variação positiva, incremental maior que ROA (sobra física?), justificar'
    TST_CMP3.loc[crit7, 'OBS_SFF'] = 'Confirmar se foram feitos ajustes na unitização'
    TST_CMP3.loc[TST_CMP3['FLG_EXC'], 'OBS_SFF'] = '''Tratado como sistema, isto é, cujas unidades de medida são 
                        distintas (por exemplo, itens contabilizados em unidades, conjunto funcional, massa, construções, ou outras 
                        métricas específicas) e que, por natureza, não são comparáveis diretamente aos valores do ROA.'''.replace("\n","")

    TST_CMP3.to_sql("TST_CMP3_INCR", con, if_exists='replace', index=False)

    if st: avl.progress(15, text = 'Comparação de quantidade por Código de UC e A1 entre ROA, AIS e INCR...')
    
    SQLq = f"""
                SELECT 
                    t1.Cd_SubODI, t1.COD_ITEM, SUM(CAST(COALESCE(Qtd_AIS,'0') AS REAL)) AS Qtd_AIS, 
                    t1.Nr_TUC, t1.Nr_A1, t1.Cd_UND_AIS
                FROM 
                    AIS t1 
                WHERE 
                    t1.dt_ARQ = ? AND t1.FLG_PER = 1
                GROUP BY
                    t1.Cd_SubODI, t1.COD_ITEM, t1.Nr_TUC, t1.Nr_A1, t1.Cd_UND_AIS
            """
    AIS = sql.imp_tbl_forma_001('AIS', SQLq = SQLq, con = con, st=st, Empresa=Empresa)

    for nm in AIS.columns.to_list():
        if nm[:2].upper() in ["VL", "QT"] and AIS[nm].dtype == 'object':
            AIS[nm] = pd.to_numeric(AIS[nm].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')       
    ROA_RES = (ROA
            .groupby(['Nr_TUC','Nr_A1','Unidade'], dropna=False)[['Qtd']]
            .sum()
            .reset_index()
            .rename(columns={'Unidade' : 'Cd_UND', 'Qtd' : 'QTD_ROA'}))
    ROA_RES['Nr_A1'] = ROA_RES['Nr_A1'].str.lstrip('0')

    INCR_RES = (INCR[INCR['Cd_UAR'] != 'UAR']
                .groupby(['Nr_TUC','Nr_A1','Cd_UND_AIS'], dropna=False)[['Qtd_AIS']]
                .sum()
                .reset_index()
                .rename(columns={'Cd_UND_AIS' : 'Cd_UND', 'Qtd_AIS' : 'QTD_INC'}))
    INCR_RES['Nr_A1'] = INCR_RES['Nr_A1'].str.lstrip('0')

    AIS_RES = (AIS.groupby(['Nr_TUC','Nr_A1','Cd_UND_AIS'], dropna=False)[['Qtd_AIS']]
            .sum()
            .reset_index()
            .rename(columns={'Cd_UND_AIS' : 'Cd_UND', 'Qtd_AIS' : 'QTD_AIS'}))
    AIS_RES['Nr_A1'] = AIS_RES['Nr_A1'].str.lstrip('0')

    TST_CMP4 = INCR_RES.merge(ROA_RES, how='left', on=['Nr_TUC','Nr_A1','Cd_UND'], indicator=True)
    TST_CMP4['FLG_EXC'] = np.where(TST_CMP4['Nr_TUC'].isin(LST_SISTEMAS),
                                True,
                                False)
    map_dict = {
                'both' : 'Ambos',
                'left_only': 'Somente no arquivo INCR',
                'right_only' : 'Somente no arquivo ROA'
            }
    TST_CMP4['OBS_CONC_ROA_vs_INCR'] = TST_CMP4['_merge'].map(map_dict)
    TST_CMP4 = TST_CMP4.drop(columns = '_merge') 
    TST_CMP4[['QTD_INC','QTD_ROA']] = TST_CMP4[['QTD_INC','QTD_ROA']].fillna(0)
    TST_CMP4['PCT_VAR'] = np.where(TST_CMP4['QTD_INC']>0,
                                    (TST_CMP4['QTD_INC']-TST_CMP4['QTD_ROA'])/TST_CMP4['QTD_INC'],
                                    np.inf)
    
    crit1 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR'] == 'Ambos') & (TST_CMP4['PCT_VAR'].abs()<0.001) &
            (~TST_CMP4['FLG_EXC']))
    crit2 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR'] == 'Somente no arquivo INCR') &
            (~TST_CMP4['FLG_EXC']))
    crit3 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR'] == 'Somente no arquivo ROA') &
            (~TST_CMP4['FLG_EXC']))
    crit6 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR'] == 'Ambos') &
            (~TST_CMP4['FLG_EXC']) & (TST_CMP4['PCT_VAR'] >= 0.001))
    crit7 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR'] == 'Ambos') &
            (~TST_CMP4['FLG_EXC']) & (TST_CMP4['PCT_VAR'] <= -0.001))
    
    TST_CMP4.loc[crit1, 'OBS_SFF_INCR_vs_ROA'] = 'NO'
    TST_CMP4.loc[crit2, 'OBS_SFF_INCR_vs_ROA'] = 'Material ausente no ROA (sobra física?), justificar'
    TST_CMP4.loc[crit3, 'OBS_SFF_INCR_vs_ROA'] = 'Material ausente no INC (sobra contábil?), justificar'
    TST_CMP4.loc[crit6, 'OBS_SFF_INCR_vs_ROA'] = 'Variação positiva, incremental maior que ROA (sobra física?), justificar'
    TST_CMP4.loc[crit7, 'OBS_SFF_INCR_vs_ROA'] = 'Confirmar se foram feitos ajustes na unitização'
    TST_CMP4.loc[TST_CMP4['FLG_EXC'], 'OBS_SFF_INCR_vs_ROA'] = '''Tratado como sistema, isto é, cujas unidades de medida são 
                        distintas (por exemplo, itens contabilizados em unidades, conjunto funcional, massa, construções, ou outras 
                        métricas específicas) e que, por natureza, não são comparáveis diretamente aos valores do ROA.'''.replace("\n","")
    
    TST_CMP4 = TST_CMP4.merge(AIS_RES, how='left', on=['Nr_TUC','Nr_A1','Cd_UND'], indicator=True)
    TST_CMP4['FLG_EXC'] = np.where(TST_CMP4['Nr_TUC'].isin(LST_SISTEMAS),
                                True,
                                False)
    map_dict = {
                'both' : 'Ambos',
                'left_only': 'Somente no arquivo INCR/ROA',
                'right_only' : 'Somente no arquivo AIS'
            }
    TST_CMP4['OBS_CONC_ROA_vs_INCR_vs_AIS'] = TST_CMP4['_merge'].map(map_dict)
    TST_CMP4 = TST_CMP4.drop(columns = '_merge') 
    TST_CMP4[['QTD_INC','QTD_ROA','QTD_AIS']] = TST_CMP4[['QTD_INC','QTD_ROA','QTD_AIS']].fillna(0)
    TST_CMP4['PCT_VAR_AIS'] = np.where(TST_CMP4['QTD_INC']>0,
                                    (TST_CMP4['QTD_INC']-TST_CMP4['QTD_AIS'])/TST_CMP4['QTD_INC'],
                                    np.inf)
    
    crit1 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR_vs_AIS'] == 'Ambos') & (TST_CMP4['PCT_VAR_AIS'].abs()<0.001) &
            (~TST_CMP4['FLG_EXC']))
    crit2 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR_vs_AIS'] == 'Somente no arquivo INCR/ROA') &
            (~TST_CMP4['FLG_EXC']))
    crit3 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR_vs_AIS'] == 'Somente no arquivo AIS') &
            (~TST_CMP4['FLG_EXC']))
    crit6 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR_vs_AIS'] == 'Ambos') &
            (~TST_CMP4['FLG_EXC']) & (TST_CMP4['PCT_VAR_AIS'] >= 0.001))
    crit7 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR_vs_AIS'] == 'Ambos') &
            (~TST_CMP4['FLG_EXC']) & (TST_CMP4['PCT_VAR_AIS'] <= -0.001))
    
    TST_CMP4.loc[crit1, 'OBS_SFF_INCR_vs_ROA_vs_AIS'] = 'NO'
    TST_CMP4.loc[crit2, 'OBS_SFF_INCR_vs_ROA_vs_AIS'] = 'Material ausente no ROA (sobra física?), justificar'
    TST_CMP4.loc[crit3, 'OBS_SFF_INCR_vs_ROA_vs_AIS'] = 'Material ausente no INC (sobra contábil?), justificar'
    TST_CMP4.loc[crit6, 'OBS_SFF_INCR_vs_ROA_vs_AIS'] = 'Variação positiva, incremental maior que ROA (sobra física?), justificar'
    TST_CMP4.loc[crit7, 'OBS_SFF_INCR_vs_ROA_vs_AIS'] = 'Confirmar se foram feitos ajustes na unitização'
    TST_CMP4.loc[TST_CMP4['FLG_EXC'], 'OBS_SFF_INCR_vs_ROA_vs_AIS'] = '''Tratado como sistema, isto é, cujas unidades de medida são 
                        distintas (por exemplo, itens contabilizados em unidades, conjunto funcional, massa, construções, ou outras 
                        métricas específicas) e que, por natureza, não são comparáveis diretamente aos valores do ROA.'''.replace("\n","")

    TST_CMP4[['Nr_TUC', 'Nr_A1', 'Cd_UND', 'QTD_INC', 'QTD_ROA', 'QTD_AIS', 'FLG_EXC', 'PCT_VAR', 'PCT_VAR_AIS',  
            'OBS_CONC_ROA_vs_INCR', 'OBS_SFF_INCR_vs_ROA', 'OBS_CONC_ROA_vs_INCR_vs_AIS', 
            'OBS_SFF_INCR_vs_ROA_vs_AIS']].to_sql("TST_CMP4_INCR", con, if_exists='replace', index=False)

    if st: avl.progress(20, text = 'Comparação por Código de Projeto, UC e A1 entre ROA, AIS e INCR...')


    ROA_RES = (ROA
            .groupby(['Cd_SubODI','Nr_TUC','Nr_A1','Unidade'], dropna=False)[['Qtd']]
            .sum()
            .reset_index()
            .rename(columns={'Unidade' : 'Cd_UND', 'Qtd' : 'QTD_ROA'}))
    ROA_RES['Nr_A1'] = ROA_RES['Nr_A1'].str.lstrip('0')

    INCR_RES = (INCR[INCR['Cd_UAR'] != 'UAR']
                .groupby(['Cd_SubODI','Nr_TUC','Nr_A1','Cd_UND_AIS'], dropna=False)[['Qtd_AIS']]
                .sum()
                .reset_index()
                .rename(columns={'Cd_UND_AIS' : 'Cd_UND', 'Qtd_AIS' : 'QTD_INC'}))
    INCR_RES['Nr_A1'] = INCR_RES['Nr_A1'].str.lstrip('0')

    AIS_RES = (AIS.groupby(['Cd_SubODI','Nr_TUC','Nr_A1','Cd_UND_AIS'], dropna=False)[['Qtd_AIS']]
            .sum()
            .reset_index()
            .rename(columns={'Cd_UND_AIS' : 'Cd_UND', 'Qtd_AIS' : 'QTD_AIS'}))
    AIS_RES['Nr_A1'] = AIS_RES['Nr_A1'].str.lstrip('0')

    TST_CMP4 = INCR_RES.merge(ROA_RES, how='left', on=['Cd_SubODI','Nr_TUC','Nr_A1','Cd_UND'], indicator=True)
    TST_CMP4['FLG_EXC'] = np.where(TST_CMP4['Nr_TUC'].isin(LST_SISTEMAS),
                                True,
                                False)
    map_dict = {
                'both' : 'Ambos',
                'left_only': 'Somente no arquivo INCR',
                'right_only' : 'Somente no arquivo ROA'
            }
    TST_CMP4['OBS_CONC_ROA_vs_INCR'] = TST_CMP4['_merge'].map(map_dict)
    TST_CMP4 = TST_CMP4.drop(columns = '_merge') 
    TST_CMP4[['QTD_INC','QTD_ROA']] = TST_CMP4[['QTD_INC','QTD_ROA']].fillna(0)
    TST_CMP4['PCT_VAR'] = np.where(TST_CMP4['QTD_INC']>0,
                                    (TST_CMP4['QTD_INC']-TST_CMP4['QTD_ROA'])/TST_CMP4['QTD_INC'],
                                    np.inf)
    
    crit1 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR'] == 'Ambos') & (TST_CMP4['PCT_VAR'].abs()<0.001) &
            (~TST_CMP4['FLG_EXC']))
    crit2 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR'] == 'Somente no arquivo INCR') &
            (~TST_CMP4['FLG_EXC']))
    crit3 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR'] == 'Somente no arquivo ROA') &
            (~TST_CMP4['FLG_EXC']))
    crit6 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR'] == 'Ambos') &
            (~TST_CMP4['FLG_EXC']) & (TST_CMP4['PCT_VAR'] >= 0.001))
    crit7 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR'] == 'Ambos') &
            (~TST_CMP4['FLG_EXC']) & (TST_CMP4['PCT_VAR'] <= -0.001))
    
    TST_CMP4.loc[crit1, 'OBS_SFF_INCR_vs_ROA'] = 'NO'
    TST_CMP4.loc[crit2, 'OBS_SFF_INCR_vs_ROA'] = 'Material ausente no ROA (sobra física?), justificar'
    TST_CMP4.loc[crit3, 'OBS_SFF_INCR_vs_ROA'] = 'Material ausente no INC (sobra contábil?), justificar'
    TST_CMP4.loc[crit6, 'OBS_SFF_INCR_vs_ROA'] = 'Variação positiva, incremental maior que ROA (sobra física?), justificar'
    TST_CMP4.loc[crit7, 'OBS_SFF_INCR_vs_ROA'] = 'Confirmar se foram feitos ajustes na unitização'
    TST_CMP4.loc[TST_CMP4['FLG_EXC'], 'OBS_SFF_INCR_vs_ROA'] = '''Tratado como sistema, isto é, cujas unidades de medida são 
                        distintas (por exemplo, itens contabilizados em unidades, conjunto funcional, massa, construções, ou outras 
                        métricas específicas) e que, por natureza, não são comparáveis diretamente aos valores do ROA.'''.replace("\n","")
    
    TST_CMP4 = TST_CMP4.merge(AIS_RES, how='left', on=['Cd_SubODI','Nr_TUC','Nr_A1','Cd_UND'], indicator=True)
    TST_CMP4['FLG_EXC'] = np.where(TST_CMP4['Nr_TUC'].isin(LST_SISTEMAS),
                                True,
                                False)
    map_dict = {
                'both' : 'Ambos',
                'left_only': 'Somente no arquivo INCR/ROA',
                'right_only' : 'Somente no arquivo AIS'
            }
    TST_CMP4['OBS_CONC_ROA_vs_INCR_vs_AIS'] = TST_CMP4['_merge'].map(map_dict)
    TST_CMP4 = TST_CMP4.drop(columns = '_merge') 
    TST_CMP4[['QTD_INC','QTD_ROA','QTD_AIS']] = TST_CMP4[['QTD_INC','QTD_ROA','QTD_AIS']].fillna(0)
    TST_CMP4['PCT_VAR_AIS'] = np.where(TST_CMP4['QTD_INC']>0,
                                    (TST_CMP4['QTD_INC']-TST_CMP4['QTD_AIS'])/TST_CMP4['QTD_INC'],
                                    np.inf)
    
    crit1 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR_vs_AIS'] == 'Ambos') & (TST_CMP4['PCT_VAR_AIS'].abs()<0.001) &
            (~TST_CMP4['FLG_EXC']))
    crit2 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR_vs_AIS'] == 'Somente no arquivo INCR/ROA') &
            (~TST_CMP4['FLG_EXC']))
    crit3 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR_vs_AIS'] == 'Somente no arquivo AIS') &
            (~TST_CMP4['FLG_EXC']))
    crit6 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR_vs_AIS'] == 'Ambos') &
            (~TST_CMP4['FLG_EXC']) & (TST_CMP4['PCT_VAR_AIS'] >= 0.001))
    crit7 = ((TST_CMP4['OBS_CONC_ROA_vs_INCR_vs_AIS'] == 'Ambos') &
            (~TST_CMP4['FLG_EXC']) & (TST_CMP4['PCT_VAR_AIS'] <= -0.001))
    
    TST_CMP4.loc[crit1, 'OBS_SFF_INCR_vs_ROA_vs_AIS'] = 'NO'
    TST_CMP4.loc[crit2, 'OBS_SFF_INCR_vs_ROA_vs_AIS'] = 'Material ausente no ROA (sobra física?), justificar'
    TST_CMP4.loc[crit3, 'OBS_SFF_INCR_vs_ROA_vs_AIS'] = 'Material ausente no INC (sobra contábil?), justificar'
    TST_CMP4.loc[crit6, 'OBS_SFF_INCR_vs_ROA_vs_AIS'] = 'Variação positiva, incremental maior que ROA (sobra física?), justificar'
    TST_CMP4.loc[crit7, 'OBS_SFF_INCR_vs_ROA_vs_AIS'] = 'Confirmar se foram feitos ajustes na unitização'
    TST_CMP4.loc[TST_CMP4['FLG_EXC'], 'OBS_SFF_INCR_vs_ROA_vs_AIS'] = '''Tratado como sistema, isto é, cujas unidades de medida são 
                        distintas (por exemplo, itens contabilizados em unidades, conjunto funcional, massa, construções, ou outras 
                        métricas específicas) e que, por natureza, não são comparáveis diretamente aos valores do ROA.'''.replace("\n","")

    TST_CMP4[['Cd_SubODI', 'Nr_TUC', 'Nr_A1', 'Cd_UND', 'QTD_INC', 'QTD_ROA', 'QTD_AIS', 'FLG_EXC', 'PCT_VAR', 'PCT_VAR_AIS',  
            'OBS_CONC_ROA_vs_INCR', 'OBS_SFF_INCR_vs_ROA', 'OBS_CONC_ROA_vs_INCR_vs_AIS', 
            'OBS_SFF_INCR_vs_ROA_vs_AIS']].to_sql("TST_CMP5_INCR", con, if_exists='replace', index=False)

    if st: avl.progress(22, text = 'Calculando JOA por tipologia...')

    TX_JOA_APL = tbl_JOA(dir_arq_saida, con, Empresa, ano, st)
    TX_JOA_APL.to_sql("TX_JOA_APL", con, if_exists='replace', index=False)

    if st: avl.progress(25, text = 'Testando código SISBASE...')

    INCR = sql.imp_tbl_forma_001('INCR', con = con, st=st, Empresa=Empresa)

    for nm in ['Qtd_AIS','VL_VOC','VL_DEP_ACUM','VL_VOC_VF','VL_VOC_COM','VL_VOC_CA','VL_VOC_JOA','VL_VOC_VF_AVAL',
               'VL_VOC_COM_AVAL','VL_VOC_CA_AVAL','VL_VOC_JOA_AVAL','VL_VNR_UC','VL_IAI_UC','VL_DAC_UC','VL_VMU_UC',
               'VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC','Pct_IA','VL_VNR_VF_UNIT','VL_VNR_COM_UNIT','VL_VNR_CA_UNIT',
               'VL_VNR_JOA']:
        if (nm in INCR.columns) and (INCR[nm].dtype == 'object'):
            INCR[nm] = pd.to_numeric(INCR[nm].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')

    INCR['Cd_SISBASE'] = INCR['Cd_SISBASE'].fillna("ND")
    LST_BPR = ['BCS', 'CHS', 'CCO', 'CFR', 'DSJ', 'LUM', 'PRS', 'PRR', 'REA', 'RGS', 'RLS', 'TRA', 
               'CDL', 'PST', 'TRF', 'TMS', 'MRD', 'CDR', 'TRD', 'BNC', 'CHV', 'REG', 'REL', 'TSA']
    INCR.loc[~INCR['Cd_SISBASE'].str.startswith(tuple(LST_BPR)), 'Cd_SISBASE'] = 'ND'

    LST_TUC = INCR[(INCR['Cd_UAR'] != 'UAR') & 
                (INCR['Cd_CONC'] == '1') & 
                (INCR['FLG_ELIG'] == '1')][['Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                                            'Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_SISBASE']].drop_duplicates()

    LST_TUC = tst_cod_sisbase(LST_TUC, dt_fim_proc, st=st)
    LST_TUC.to_sql("TST_CD_SISBASE", con, if_exists='replace', index=False)

    txtALERTAS = pd.DataFrame(columns = ["Id_SEQ_INC","OBS_FISC"])

    ipca.columns=['DT_IMB_BASE','Nr_IPCA_REF_IMB']
    if 'Cd_Q5' in INCR.columns:
        INCRini = INCR[['Id_SEQ_INC','Id_AIS','Cd_CC','Cd_ODI','Cd_SubODI','Nr_TI','Nr_CM','Nr_TUC',
                    'Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_UAR','Cd_UC','Cd_Patrim','Cd_DIG_INC',
                    'COD_ITEM','Qtd_AIS','Cd_UND_AIS','VL_VOC','Dt_Imob','Dt_CNTB_AJST','VL_DEP_ACUM',
                    'VL_VOC_VF','VL_VOC_COM','VL_VOC_CA','VL_VOC_JOA','VL_VOC_VF_AVAL','VL_VOC_COM_AVAL',
                    'VL_VOC_CA_AVAL','VL_VOC_JOA_AVAL','Cd_ODD','Dt_BX','Txt_DESC_TECN','Txt_CLS_TNS',
                    'FLG_RSV','Cd_ODI_ENG','Cd_TP_AVAL','Cd_SISBASE','Id_BP','TP_BEM','VL_VNR_UC',
                    'VL_IAI_UC','VL_DAC_UC','VL_VMU_UC','VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC','Pct_IA',
                    'VL_VNR_VF_UNIT','VL_VNR_COM_UNIT','VL_VNR_CA_UNIT','VL_VNR_JOA','FLG_DOA_OE',
                    'FLG_INCOR_OE','FLG_PLPT_OE','FLG_OAT','FLG_REG','FLG_ELIG','Cd_CONC','Cd_ABCC',
                    'Cd_NumFIS','Dt_REF_DADOS'] + ['Cd_Q5']].copy()
    else:
        INCRini = INCR[['Id_SEQ_INC','Id_AIS','Cd_CC','Cd_ODI','Cd_SubODI','Nr_TI','Nr_CM','Nr_TUC',
                    'Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_UAR','Cd_UC','Cd_Patrim','Cd_DIG_INC',
                    'COD_ITEM','Qtd_AIS','Cd_UND_AIS','VL_VOC','Dt_Imob','Dt_CNTB_AJST','VL_DEP_ACUM',
                    'VL_VOC_VF','VL_VOC_COM','VL_VOC_CA','VL_VOC_JOA','VL_VOC_VF_AVAL','VL_VOC_COM_AVAL',
                    'VL_VOC_CA_AVAL','VL_VOC_JOA_AVAL','Cd_ODD','Dt_BX','Txt_DESC_TECN','Txt_CLS_TNS',
                    'FLG_RSV','Cd_ODI_ENG','Cd_TP_AVAL','Cd_SISBASE','Id_BP','TP_BEM','VL_VNR_UC',
                    'VL_IAI_UC','VL_DAC_UC','VL_VMU_UC','VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC','Pct_IA',
                    'VL_VNR_VF_UNIT','VL_VNR_COM_UNIT','VL_VNR_CA_UNIT','VL_VNR_JOA','FLG_DOA_OE',
                    'FLG_INCOR_OE','FLG_PLPT_OE','FLG_OAT','FLG_REG','FLG_ELIG','Cd_CONC','Cd_ABCC',
                    'Cd_NumFIS','Dt_REF_DADOS']].copy()
        INCRini['Cd_Q5'] = None

    if st: avl.progress(28, text = 'Buscando IPCA...')

    

    cols_datas = {'Dt_Imob', 'Dt_CNTB_AJST','Dt_REF_DADOS','Dt_BX'}

    for col in cols_datas & set(INCR.columns):
        if INCR[col].dtype == 'object':
            INCR[col] = pd.to_datetime(INCR[col], errors='coerce')

    DD_GRP = pd.read_csv("tabelas/TBL_GRUPOS.csv",sep="|",decimal=',',on_bad_lines='skip',
                     encoding="Latin-1");

    DD_GRP = DD_GRP[DD_GRP['Cd_ANEEL'] == sql.bsc_cd_aneel(Empresa)]

    for i in range(len(DD_GRP)):
        INCRini.loc[INCRini['Dt_Imob'] >= DD_GRP.iloc[i,2],'Nr_GRUPO']=DD_GRP.iloc[i,1]
    
    TI = pd.read_csv("tabelas/TBL_TI.csv",sep="|",decimal=',',on_bad_lines='skip',encoding="Latin-1",dtype=str);
    
    TB_TI = TI[['Id_TI', 'TP_JOA']].drop_duplicates().rename(columns={'Id_TI': 'Nr_TI'})

    INCRini = INCRini.merge(TB_TI, how='left', on='Nr_TI')
    INCRini['TP_JOA'] = INCRini['TP_JOA'].fillna("ND")
    INCRini.loc[(INCRini['Nr_GRUPO'] < 4) & (INCRini['TP_JOA'] != 'ND'), 'TP_JOA'] += '_123'
    INCRini.loc[(INCRini['Nr_GRUPO'] > 3) & (INCRini['TP_JOA'] != 'ND'), 'TP_JOA'] += '_45'
    INCRini=INCRini.merge(TX_JOA_APL, how='left', on='TP_JOA')
    INCRini['Tx_JOA'] = INCRini['Tx_JOA'].fillna(0)
    INCRini['LIM_JOA'] = 0
    INCRini['TST_JOA'] = 'OK'

    INCRini = INCRini.merge(LST_TUC, how='left', 
            on=['Nr_TI','Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_SISBASE'])
    INCRini.loc[(INCR['Cd_TP_AVAL'] != '2') | (INCR['Cd_UAR'] == 'UAR') | (INCR['Cd_CONC'] != '1') | (INCR['FLG_ELIG'] != '1'), 'TESTE_Cd'] = 'NA'

    dt_ref_base = pd.to_datetime(INCR.loc[0, 'Dt_REF_DADOS']).replace(day=1)

    dt1 = pd.to_datetime(INCRini['Dt_Imob'], format='mixed').dt.to_period('M')
    dt2 = pd.to_datetime(INCRini['Dt_CNTB_AJST'], format='mixed').dt.to_period('M')
    DT_MAIS_ANTIGA = pd.to_datetime(pd.concat([dt1, dt2], axis=1).min(axis=1).astype(str) + '-01')

    INCRini = INCRini.assign(
                                DT_REF_BASE=dt_ref_base,
                                Dt_Imob = pd.to_datetime(INCRini['Dt_Imob']).dt.normalize(),
                                DT_IMB_BASE = DT_MAIS_ANTIGA
                            )
    mask1 = (INCRini['FLG_DOA_OE'].astype(str) == '1') & (INCRini['FLG_INCOR_OE'].astype(str) == '1')
    INCRini.loc[mask1, 'DT_IMB_BASE'] = INCRini.loc[mask1, 'Dt_Imob']

    ipca['DT_IMB_BASE'] = ipca['DT_IMB_BASE'].to_numpy().astype('datetime64[M]')
    dt_ref_base = pd.to_datetime(INCR.loc[0, 'Dt_REF_DADOS']).to_numpy().astype('datetime64[M]')

    try:
        INCRini['Nr_IPCA_REF_BASE'] = ipca.loc[ipca['DT_IMB_BASE'] == dt_ref_base, 'Nr_IPCA_REF_IMB'].iloc[-1]
    except:
        st.warning(f"IPCA não encontrado para a data-base {dt_ref_base:%m/%Y}")
        raise UserWarning("Problema na data de referência do Laudo")
    
    INCRini = INCRini.merge(ipca, how='left', on='DT_IMB_BASE')
    INCRini.loc[(INCRini['DT_IMB_BASE'] < pd.to_datetime('01/01/1996')) 
                & (INCRini['Nr_IPCA_REF_IMB'].isnull()), 'Nr_IPCA_REF_IMB'] = 1260.9
    INCRini['FA_IPCA'] = INCRini['Nr_IPCA_REF_BASE'] / INCRini['Nr_IPCA_REF_IMB']

    if st: avl.progress(30, text = 'Buscando Naturezas de Gasto do ROA...')

    INCRini['FLG_EXC'] = np.where(INCRini['Nr_TUC'].isin(LST_SISTEMAS),
                                    True,
                                    False)

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
                    ) AS VL_tot 
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
                    t1.Unidade;
            """
    df_VL_VF_ROA = sql.imp_tbl_forma_001('ROA', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
    VL_VF_ROA = (df_VL_VF_ROA
                .groupby(by=['Cd_SubODI','COD_ITEM'])[['Qtd_ROA','VL_tot']]
                .sum()
                .reset_index())
    VL_VF_ROA[f'VL_VF_ROA'] = np.where(VL_VF_ROA['Qtd_ROA'] != 0,
                                        VL_VF_ROA['VL_tot'] / VL_VF_ROA['Qtd_ROA'],
                                        VL_VF_ROA['VL_tot'])
    
    INCRini = INCRini.merge(VL_VF_ROA, how='left', on = ['Cd_SubODI','COD_ITEM'])
    
    VL_VF_ROA = (df_VL_VF_ROA
                .groupby(by=['Cd_SubODI','Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                            'Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_UND_AIS'])[['Qtd_ROA','VL_tot']]
                .sum()
                .reset_index())
    
    VL_VF_ROA[f'VL_VF_ROA'] = np.where(VL_VF_ROA['Qtd_ROA'] != 0,
                                        VL_VF_ROA['VL_tot'] / VL_VF_ROA['Qtd_ROA'],
                                        VL_VF_ROA['VL_tot'])

    INCRini = INCRini.merge(VL_VF_ROA, how='left', on = ['Cd_SubODI','Nr_TI','Nr_TUC','Nr_A1','Nr_A2',
                            'Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_UND_AIS'], suffixes=("_UNT1", "_UNT2"))
    
    condicao_1 = INCRini[f'Qtd_ROA_UNT1'].notnull()
    condicao_2 = INCRini[f'Qtd_ROA_UNT2'].notnull()
    INCRini[f'Qtd_ROA'] = np.where(
                                            condicao_1,
                                            INCRini[f'Qtd_ROA_UNT1'],
                                            np.where(
                                                        condicao_2,
                                                        INCRini[f'Qtd_ROA_UNT2'],
                                                        None
                                                    )
                                        )
    
    condicao_1 = INCRini[f'VL_VF_ROA_UNT1'].notnull()
    condicao_2 = INCRini[f'VL_VF_ROA_UNT2'].notnull()
    tol = 0.01
    INCRini[f'VL_VF_ROA'] = np.where(
                                            condicao_1,
                                            INCRini[f'VL_VF_ROA_UNT1'],
                                            np.where(
                                                        condicao_2,
                                                        INCRini[f'VL_VF_ROA_UNT2'],
                                                        None
                                                    )
                                        )
    
    condicao_3 = INCRini['FLG_INCOR_OE'].astype(str)=='1'
    condicao_4 = INCRini['FLG_PLPT_OE'].astype(str)=='1'
    condicao_5 = INCRini['FLG_DOA_OE'].astype(str)=='1'
    condicao_6 = INCRini['Nr_TI'].astype(str).isin(['70','71','72','80','81','82','94','95','97','99'])
    condicao_7 = INCRini['FLG_EXC'] 
    
    tol = 0.05
    crit = np.isclose(INCRini['VL_VOC_VF_AVAL'].fillna(0)/INCRini['Qtd_AIS'].fillna(1e-6),
              INCRini['VL_VF_ROA'].fillna(0),
              rtol = tol) 
    crit1 = np.isclose(INCRini['Qtd_AIS'].fillna(0),
              INCRini['Qtd_ROA'].fillna(0),
              rtol = tol)
    
    INCRini.loc[~crit, 'TST_VF_ROA_AVL'] = "Valor diverge"
    INCRini.loc[condicao_7, 'TST_VF_ROA_AVL'] = "NA, no ROA é composto por diversos itens (sistema) ou se trata de apropriação direta."
    INCRini.loc[condicao_6, 'TST_VF_ROA_AVL'] = "NA, TI não avaliada."
    INCRini.loc[condicao_5, 'TST_VF_ROA_AVL'] = "NA, doação."
    INCRini.loc[condicao_4, 'TST_VF_ROA_AVL'] = "NA, PLPT."
    INCRini.loc[condicao_3, 'TST_VF_ROA_AVL'] = "NA, incorporação."
    INCRini.loc[crit, 'TST_VF_ROA_AVL'] = "NO"
    INCRini.loc[~crit1, 'TST_VF_ROA_AVL'] = "Problemas na quantidade."
    INCRini['VL_VF_ROA'] = INCRini['VL_VF_ROA'] * INCRini['Qtd_AIS']
    INCRini = INCRini.drop(columns=['Qtd_ROA_UNT1','VL_tot_UNT1','VL_VF_ROA_UNT1',
                                    'Qtd_ROA_UNT2','VL_tot_UNT2','VL_VF_ROA_UNT2'])

    
    #############################################################################################################################
    #                  TESTE DE VALOR DO VALOR DE FÁBRICA E DA QUANTIDADE APRESENTADA NO LAUDO COM O DO ROA                     #
    #compara-se o valor total do VF, para evitar problemas de unidades entre arquivos. Excluem-se um grupo de UC, consideradas  #
    #que são um sistema (um agrupamento de materiais e serviços no ROA, não tendo relação 1 para 1)                             #
    #############################################################################################################################
    LST_TUCVF = pd.read_csv('tabelas/TBL_TUC_VF.csv', usecols=['Ide_TUC'],
                            sep="|",decimal=',',on_bad_lines='skip',
                            encoding="Latin-1")['Ide_TUC'].tolist()

    INCRini['TST_QTD_ROA_AVL'] = 'NO'
    INCRini.loc[(INCRini['Cd_CONC'] == '2'), ['TST_QTD_ROA_AVL','TST_VF_ROA_AVL']]='Não se aplica, sobra contábil'
    INCRini.loc[(INCRini['FLG_ELIG'] != '1'), ['TST_QTD_ROA_AVL','TST_VF_ROA_AVL']]='Não se aplica, inelegível'
    INCRini.loc[((INCRini['Qtd_ROA'] - INCRini['Qtd_AIS']) < 0) & 
                (INCRini['Cd_TP_AVAL'].isin(['1','2']) & (INCRini['Cd_CONC'].isin(['1','3']))
                & (INCRini['FLG_ELIG'] == '1') ),'TST_QTD_ROA_AVL'] = 'DIFERE, OBSERVE UNIDADE OU AJUSTE'
    INCRini.loc[condicao_7, 'TST_QTD_ROA_AVL'] =  "NA, no ROA é composto por diversos itens (sistema) ou se trata de apropriação direta."

    if st: avl.progress(35, text = 'Buscando COGE...')

    SQLq = f"""
                SELECT 
                    t1.Cd_FOR_COGE AS Cd_FOR_COGE_SFF,
                    t1.DT_REF AS DT_IMB_BASE,
                    MIN(t1.FC) AS FA_COGE
                FROM 
                    tbl_FCOGE t1
                GROUP BY 
                    t1.Cd_FOR_COGE, t1.DT_REF;
            """
    TBL_FCOGE = sql.imp_tbl_forma_000('tbl_FCOGE', SQLq = SQLq, con = con, st=st) 
    TBL_FCOGE1 = TBL_FCOGE.copy()
    TBL_FCOGE['DT_IMB_BASE'] = TBL_FCOGE['DT_IMB_BASE'].to_numpy().astype('datetime64[M]')
    

    TBL_FCOGE1['DT_IMB_BASE'] = (
                                    pd.to_datetime(TBL_FCOGE1['DT_IMB_BASE'])
                                    + MonthEnd(0)
                                )

    if st: avl.progress(38, text = 'Buscando o valor de fábrica informado na SDI-001...')

    SQLq = f"""
                SELECT 
                    t1.COD_ITEM, COALESCE(t1.Cd_DE_PARA, t1.COD_ITEM) AS Cd_DE_PARA
                FROM 
                    LST_MAT t1 
                WHERE 
                    dt_ARQ = ?
                GROUP BY 
                    t1.COD_ITEM, t1.Cd_DE_PARA;
            """
    LST_MAT_SDI = sql.imp_tbl_forma_001('LST_MAT', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
    if len(LST_MAT_SDI) == 0:
        SQLq = f"""
                    SELECT 
                        t1.COD_ITEM, t1.COD_ITEM AS Cd_DE_PARA
                    FROM 
                        BP_UAR t1 
                    WHERE 
                        dt_ARQ = ?
                    GROUP BY 
                        t1.COD_ITEM;
                """
        LST_MAT_SDI = sql.imp_tbl_forma_001('BP_UAR', SQLq = SQLq, con = con, st=st, Empresa=Empresa)

    if st: avl.progress(39, text = 'Buscando valores de ajusta COGE...')

    INCRini = INCRini.merge(LST_MAT_SDI, how = 'left', on = 'COD_ITEM')
    INCRini['Cd_DE_PARA'] = INCRini['Cd_DE_PARA'].replace({None: np.nan, 'None': np.nan})
    bsc_vt = INCRini['Cd_DE_PARA'].isnull()
    INCRini.loc[bsc_vt,'Cd_DE_PARA'] = INCRini.loc[bsc_vt, 'COD_ITEM']

    INCRini = INCRini.merge(TBL_FCOGE, how = 'left', on = ['Cd_FOR_COGE_SFF','DT_IMB_BASE'])
    INCRini.loc[INCRini['FA_COGE'].isnull() 
                & (INCRini['TESTE_Cd'].isin(['OK'])), 'TESTE_Cd'] = 'Falhou ao buscar indice COGE, foi descontinuado?'
    

    if st: avl.progress(42, text = 'Verificando LIMITE do JOA...')

    #############################################################################################################################
    #                                 LIMITE DO JOA, QUANDO FOR EMPREGADO O VALOR CONTABILIZADO                                 #
    #caso seja o valor atualizado, limitar o JOA.                                                                               #
    #############################################################################################################################

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
    ROA_JOA = sql.imp_tbl_forma_001('ROA', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
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
        VL_01.to_sql("TI_SLD_NEGATIVO", con, if_exists='replace', index=False)
    # Vamos eliminar projetos com abertura errada.
    ROA_JOA = ROA_JOA[ROA_JOA['VL_TOT'] > 0]

    ROA_JOA['Pct_JOA_ROA'] = (ROA_JOA['VL_JOA_TOT'] / (ROA_JOA['VL_TOT']))

    # Em tese, deveria refletir o JOA do ROA...
    LIM_JOA_PRJ = (INCRini
               .groupby(by=['Cd_SubODI'], dropna=False)
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
    ROA_JOAp = (ROA_JOA
                .groupby('Cd_SubODI',dropna=False)[['VL_UC_TOT','VL_COM_TOT','VL_MOP_TOT','VL_ST_TOT','VL_JOA_TOT','VL_OUT_TOT','VL_TOT']]
                .sum()
                .fillna(0)
                .assign(
                        Pct_JOA_ROA = lambda x: x['VL_JOA_TOT'] / (x['VL_UC_TOT'] + x['VL_COM_TOT'] + x['VL_MOP_TOT'] + x['VL_ST_TOT'])
                )
                .reset_index())
    
    LIM_JOA_PRJ = LIM_JOA_PRJ.merge(ROA_JOAp[['Cd_SubODI','Pct_JOA_ROA']], how='left', on ='Cd_SubODI')

    INCRini = INCRini.merge(LIM_JOA_PRJ, how = 'left', on ='Cd_SubODI')

    crt = (
                (INCRini['PCT_JOA_PRJ'].abs() - INCRini['Pct_JOA_ROA'].fillna(0).abs()).abs()
                / INCRini['Pct_JOA_ROA'].fillna(0).abs().replace(0, 1)
            ) > 0.01
    
    crt_TPAVL = INCRini['Cd_TP_AVAL'].astype(str) == '1'
    INCRini.loc[crt & crt_TPAVL, 'TESTE_JOA_ROA'] = "Divergência no JOA apresentado no projeto pela avaliadora"
    INCRini.loc[~crt | ~crt_TPAVL, 'TESTE_JOA_ROA'] = "NO"

    cols_atual = ['VL_VOC_VF', 'VL_VOC_COM', 'VL_VOC_CA']
    soma_atual = INCRini[cols_atual].sum(axis=1)
    cols_aval = ['VL_VOC_VF_AVAL', 'VL_VOC_COM_AVAL', 'VL_VOC_CA_AVAL']
    soma_aval = INCRini[cols_aval].sum(axis=1)

    COM_CA1 = INCRini[['VL_VOC_COM', 'VL_VOC_CA']].sum(axis=1)
    COM_CA2 = INCRini[['VL_VOC_COM_AVAL', 'VL_VOC_CA_AVAL']].sum(axis=1)

    INCRini['VL_VOC_COMpCA'] = (
                                    np.where((COM_CA1==0) & (COM_CA2==0),
                                             0,
                                             np.where((COM_CA1==0) & (COM_CA2!=0),
                                             COM_CA2,
                                             np.where((COM_CA1!=0) & (COM_CA2==0),
                                             COM_CA1,
                                             np.where(COM_CA1 > COM_CA2, COM_CA2, COM_CA1))))
                                )
    INCRini['Tst_COMpCA'] = 'NO'

    INCRini.loc[(INCRini['VL_VOC_COMpCA'].abs() < 0.01) &
                ((INCRini['VL_VOC_VF'].fillna(0).abs() > 0.01) | 
                 (INCRini['VL_VOC_VF_AVAL'].fillna(0).abs() > 0.01)) &
                 (INCRini['PCT_JOA_PRJ']==0) & 
                 ((INCRini['VL_VOC_VF'].fillna(0).abs() - INCRini['VL_VF_ROA'].fillna(0).abs()).abs() > 0.01), 'Tst_COMpCA'] = "Deveria ter aberto o VOC, justificar"

    INCRini['Tst_COMpCA'] = (
                                    np.where((COM_CA1==0) & (COM_CA2==0),
                                             "SEM ABERTURA",
                                             np.where((COM_CA1==0) & (COM_CA2!=0),
                                             "AVALIADORA ABRIU, EMPRESA NÃO",
                                             np.where((COM_CA1!=0) & (COM_CA2==0),
                                             "EMPRESA ABRIU, AVALIADORA NÃO",
                                             INCRini['Tst_COMpCA'])))
                                )
    
    INCRini['VL_VOC_AVL_sjoa'] = np.where(soma_atual > soma_aval, soma_aval, soma_atual)

    INCRini['LIM_JOA'] = np.where(  INCRini['Tx_JOA'] < INCRini['PCT_JOA_PRJ'],
                                    INCRini['Tx_JOA'] * INCRini['VL_VOC_AVL_sjoa'],
                                    INCRini['PCT_JOA_PRJ'] * INCRini['VL_VOC_AVL_sjoa']
                                  )
    INCRini.loc[(INCRini['Nr_TI'] == '93') | (INCRini['Nr_TI'] == '96'), 'LIM_JOA'] = 0 
    
    INCRini['dif_abertura'] = (abs(INCRini['VL_VOC_JOA_AVAL']) - abs(INCRini['LIM_JOA'])).round(2)
    INCRini['limite_formatado'] = abs(INCRini['LIM_JOA']).round(2)
    INCRini['valor_formatado'] = (abs(INCRini['VL_VOC_JOA_AVAL'])).round(2)

    condicao_1 = ~(np.isclose(INCRini['VL_VOC_JOA_AVAL'].abs(), INCRini['LIM_JOA'].abs(), rtol=0.001)) & (INCRini['Cd_TP_AVAL'].astype(str) == '1')
    condicao_2 = INCRini['Tx_JOA'] < INCRini['PCT_JOA_PRJ']
    condicao_3 = (INCRini['VL_VF_ROA'].fillna(0) > tol)

    INCRini['TST_JOA'] = np.where(
                                    condicao_1,
                                    np.where(
                                        condicao_2,
                                        "JOA regulatório, " + INCRini['Tx_JOA'].apply(lambda x: f"{x:,.2%}".replace(".", ",")) + 
                                        ", é menor que o contábil, " + INCRini['PCT_JOA_PRJ'].apply(lambda x: f"{x:,.2%}".replace(".", ",")) + 
                                        ", aplicar regulatório. Logo limitar JOA (valor da abertura é R$" + INCRini['dif_abertura'].astype(str) + 
                                        " superior ao limite de R$" + INCRini['limite_formatado'].astype(str) + ", do registro)",
                                        "JOA regulatório, " + INCRini['Tx_JOA'].apply(lambda x: f"{x:,.2%}".replace(".", ",")) + 
                                        ", é maior que o contábil, " + INCRini['PCT_JOA_PRJ'].apply(lambda x: f"{x:,.2%}".replace(".", ",")) + 
                                        ". No entanto, justificar o valor (R$ " + INCRini['valor_formatado'].astype(str) + ") ser maior do que o limite regulatório empregado " +
                                        "(R$" + INCRini['limite_formatado'].astype(str) + "), do registro" 
                                    ),
                                    'OK'
                                )

    INCRini = INCRini.drop(columns=['dif_abertura','limite_formatado','valor_formatado'])
    INCRini = INCRini[['Id_SEQ_INC', 'Id_AIS', 'Cd_CC', 'Cd_ODI', 'Cd_SubODI', 'Nr_TI', 'Nr_CM', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 
                       'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6', 'Cd_UAR', 'Cd_UC', 'Cd_Patrim', 'Cd_DIG_INC', 'COD_ITEM', 'Qtd_AIS', 
                       'Cd_UND_AIS', 'VL_VOC', 'Dt_Imob', 'Dt_CNTB_AJST', 'VL_DEP_ACUM', 'VL_VOC_VF', 'VL_VOC_COM', 
                       'VL_VOC_CA', 'VL_VOC_JOA', 'VL_VOC_VF_AVAL', 'VL_VOC_COM_AVAL', 'VL_VOC_CA_AVAL', 'VL_VOC_JOA_AVAL', 
                       'Cd_ODD', 'Dt_BX', 'Txt_DESC_TECN', 'Txt_CLS_TNS', 'FLG_RSV', 'Cd_ODI_ENG', 'Cd_TP_AVAL', 'Cd_SISBASE', 
                       'Id_BP', 'TP_BEM', 'VL_VNR_UC', 'VL_IAI_UC', 'VL_DAC_UC', 'VL_VMU_UC', 'VL_IAD_UC', 'VL_VBR_UC', 
                       'VL_100DEP_UC', 'Pct_IA', 'VL_VNR_VF_UNIT', 'VL_VNR_COM_UNIT', 'VL_VNR_CA_UNIT', 'VL_VNR_JOA', 
                       'FLG_DOA_OE', 'FLG_INCOR_OE', 'FLG_PLPT_OE', 'FLG_OAT', 'FLG_REG', 'FLG_ELIG', 'Cd_CONC', 'Cd_ABCC', 
                       'Cd_NumFIS', 'Dt_REF_DADOS', 'Cd_Q5', 'FLG_EXC', 'Nr_GRUPO', 'TP_JOA', 'Tx_JOA', 'PCT_JOA_PRJ', 'Pct_JOA_ROA', 
                       'LIM_JOA', 'TST_JOA','Cd_SISBASE_SFF', 'TESTE_Cd', 'Cd_FOR_COGE_SFF', 
                       'Nr_FAM_SFF', 'DT_REF_BASE', 'DT_IMB_BASE','Nr_IPCA_REF_BASE', 'Nr_IPCA_REF_IMB', 
                       'FA_IPCA', 'Qtd_ROA', 'VL_VF_ROA', 'VL_VOC_COMpCA','TST_VF_ROA_AVL','TST_QTD_ROA_AVL','Tst_COMpCA',
                       'Cd_DE_PARA','FA_COGE', 'VL_VOC_AVL_sjoa']].copy()
    
    #############################################################################################################################
    #############################################################################################################################
    #                                                Calcular o VOC atualizado                                                  #
    #############################################################################################################################
    if st: avl.progress(45, text = 'Calculando VOC atualizado...')

    INCRini['TST_ROA_AVL'] = 'NO'
    INCRini.loc[(INCRini['VL_VOC_AVL_sjoa'] == 0) & (INCRini['Cd_CONC'].isin(['1','3']))
                & (INCRini['FLG_ELIG'] == '1'),'TST_ROA_AVL'] = 'Arquivo INCR não informou o VOC após ajustes'
    INCRini['VL_JOA_IMB_AT'] = np.minimum(INCRini['VL_VOC_JOA_AVAL'], 
                                          INCRini['LIM_JOA']) * INCRini['FA_IPCA']
    INCRini.loc[INCRini['Nr_TI'].isin(['93', '96']), 'VL_JOA_IMB_AT'] = 0

    cols_atual = ['VL_VOC_COM', 'VL_VOC_CA']
    cols_aval = ['VL_VOC_COM_AVAL', 'VL_VOC_CA_AVAL']

    soma_atual = INCRini[cols_atual].sum(axis=1)
    soma_aval = INCRini[cols_aval].sum(axis=1)

    INCRini['VL_VOC_COM_CA_IMB'] = np.where(
                                                soma_atual <= 0,
                                                soma_aval,
                                                np.where(
                                                    soma_aval <= 0,
                                                    soma_atual,
                                                    np.minimum(soma_atual, soma_aval)
                                                )
                                            )
    INCRini['VL_VOC_COM_CA_IMB'] = INCRini['VL_VOC_COM_CA_IMB'].clip(lower=0)
    INCRini['VL_VOC_VF_IMB'] = np.where(INCRini['VL_VOC_COM_CA_IMB']==0,
                                            0,
                                        np.where(    
                                                    soma_atual <= 0,
                                                    INCRini['VL_VOC_VF_AVAL'], 
                                                    np.where(
                                                    soma_aval <= 0,
                                                    INCRini['VL_VOC'], 
                                                    np.minimum(INCRini['VL_VOC_VF'], INCRini['VL_VOC_VF_AVAL'])
                                                )
                                       )
                                       )
    
    INCRini['VL_VOC_COM_CA_IMB_AT'] = INCRini['VL_VOC_COM_CA_IMB'] * INCRini['FA_IPCA']
    
    # Por default, IPCA
    INCRini['VL_VOC_VF_IMB_AT'] = INCRini['VL_VOC_VF_IMB'] * INCRini['FA_IPCA']

    # Se tiver fator COGE, SISBASE = ND e for avaliação VOC ou BPR
    tem_coge = INCRini['FA_COGE'].notna()
    tp_aval_valido = INCRini['Cd_TP_AVAL'].astype(str).isin(['1', '2'])
    sisbase_nd = ~INCRini['Cd_FOR_COGE_SFF'].astype(str).str.startswith('FCM')
    eh_doacao = INCRini['FLG_DOA_OE'].astype(str).eq('1')
    eh_inc = INCRini['FLG_INCOR_OE'].astype(str).eq('1')
    nao_zero = INCRini['VL_VOC_COM_CA_IMB_AT'] > 0
    lim_data = INCRini['DT_IMB_BASE'] > pd.to_datetime('31/05/2016', format='%d/%m/%Y')

    crit = tem_coge & tp_aval_valido & ~sisbase_nd & ~eh_doacao & ~eh_inc & nao_zero & lim_data

    INCRini.loc[crit, 'VL_VOC_VF_IMB_AT'] = (
                                                INCRini.loc[crit, 'VL_VOC_VF_IMB'] * INCRini.loc[crit, 'FA_COGE']
                                            )

    # Soma dos componentes
    INCRini['VL_VOCsjoa_IMB_AT'] = (
                                        INCRini['VL_VOC_COM_CA_IMB_AT'] + INCRini['VL_VOC_VF_IMB_AT']
                                    )

    # Se não houver abertura do VOC, exceto Reserva
    com_ca_sem_abertura = INCRini['VL_VOC_COM_CA_IMB_AT'].abs().le(0.01)
    eh_ti_98 = INCRini['Nr_TI'].astype(str).eq('98')
    eh_reserva = INCRini['FLG_RSV'].astype(str).eq('1')

    nao_aplica_regra = eh_ti_98 | eh_reserva
    crit = com_ca_sem_abertura | ~nao_aplica_regra 

    # Se CA não estiver aberto e se não for reserva, aplica-se IPCA
    INCRini.loc[crit, 'VL_VOCsjoa_IMB_AT'] = (
                                                INCRini.loc[crit, 'VL_VOC'] * INCRini.loc[crit, 'FA_IPCA']
                                             )

    tem_VF = INCRini['VL_VOC_VF'].abs().gt(0.01)
    tem_COGE = INCRini['Cd_FOR_COGE_SFF'].astype(str).str.startswith("FCM") & ~INCRini['Cd_FOR_COGE_SFF'].astype(str).eq('FCM0403')
    crit1 = tem_VF & nao_aplica_regra & tem_COGE
    crit2 = (~tem_VF | ~tem_COGE) & nao_aplica_regra

    INCRini.loc[crit1, 'VL_VOCsjoa_IMB_AT'] = (
                                                    INCRini.loc[crit1, 'VL_VOC_VF'] * INCRini.loc[crit, 'FA_COGE']
                                                 )
    INCRini.loc[crit2, 'VL_VOCsjoa_IMB_AT'] = (
                                                    INCRini.loc[crit2, 'VL_VOC'] * INCRini.loc[crit, 'FA_IPCA']
                                                 )

    if st: avl.progress(49, text = 'Buscando dados de COM e CA do BPR...')
    INCRini['OBS_FISC'] = 'NO'

    #############################################################################################################################
    #############################################################################################################################
    #                                                PREPARANDO OS DADOS PARA O BPR                                             #
    #############################################################################################################################
    BPR=pd.read_csv('tabelas/tbl_BPR_DADOS.csv',sep="|",decimal=',',
                    on_bad_lines='skip',encoding="Latin-1",dtype=str);
    BPR['DT_REF']=pd.to_datetime(BPR['DT_REF'])
    BPR['DT_APL']=pd.to_datetime(BPR['DT_APL'])
    for c in ['Nr_GRUPO','VL_COM','VL_CA']:
        BPR[c]=pd.to_numeric(BPR[c].str.replace(',','.'), errors='coerce')
        BPR[c] = BPR[c].fillna(0)

    if st: avl.progress(50, text = 'Buscando dados de VF do banco de preços da avaliadora...')

    SQLq = f"""
                SELECT 
                    COD_ITEM AS Cd_DE_PARA,
                    t1.Nr_FORM AS Cd_FRM_COGE_VF_AVAL, 
                    MIN(CAST(REPLACE(t1.VL_VF_UNIT_AT, ',', '.') AS REAL)) AS VL_VF
                FROM 
                    BP_UAR t1 
                WHERE 
                    dt_ARQ = ?
                GROUP BY 
                    t1.COD_ITEM, Nr_FORM;
            """
    BP_VF = sql.imp_tbl_forma_001('BP_UAR', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
    BPR_AX = BPR[['DT_REF', 'DT_APL']].drop_duplicates()
    INCRini = INCRini.merge(BP_VF, how='left', on = 'Cd_DE_PARA', suffixes=('', '_y'))

    if st: avl.progress(51, text = 'Verificando qual o BPR vigente...')

    teste = INCRini[['DT_IMB_BASE']].reset_index()
    dt_ref_list = BPR['DT_REF'].drop_duplicates().sort_values().tolist()
    for i in dt_ref_list:
        ia = BPR_AX.loc[BPR_AX['DT_REF'] == i, 'DT_APL'].values  
        if ia.size > 0:  
            teste.loc[((teste['DT_IMB_BASE'] - ia[0]) / np.timedelta64(1, 'D') >= 0), 'DT_REF'] = i

    DT_BPR = teste[['DT_IMB_BASE','DT_REF']].drop_duplicates()
    INCRini = INCRini.merge(DT_BPR, how='left', on='DT_IMB_BASE')
    INCRini = INCRini.merge(BPR, how='left', on=['Cd_SISBASE','Nr_GRUPO','DT_REF'])

    if st: avl.progress(52, text = 'Atualizando o BPR...')

    ipca.columns=['DT_REF','Nr_IPCA_REF_COM_CA']
    INCRini=INCRini.merge(ipca, how='left', on='DT_REF')
    INCRini['VL_COM_AT']=INCRini['VL_COM']/INCRini['Nr_IPCA_REF_COM_CA']*INCRini['Nr_IPCA_REF_BASE']
    INCRini['VL_CA_AT']=INCRini['VL_CA']/INCRini['Nr_IPCA_REF_COM_CA']*INCRini['Nr_IPCA_REF_BASE']

    if st: avl.progress(53, text = 'Verificando se é obra de INFRAESTRUTURA ou de ORÇAMENTO...')
    
    #############################################################################################################################
    #############################################################################################################################
    #                                                AVALIANDO SE OBRA INFRA OU OE                                              #
    #############################################################################################################################
    INFRA = pd.read_csv("tabelas/TBL_TUC_INFRA.csv",sep="|",decimal=',',on_bad_lines='skip',
                        encoding="Latin-1",dtype=str);
    
    INCRini['FLG_INFRA'] = 0
    lst_INFRA = INFRA.loc[INFRA['Nr_A1'] == '0', 'Nr_TUC'].drop_duplicates()
    INCRini.loc[INCRini['Nr_TUC'].isin(lst_INFRA), 'FLG_INFRA'] = 1

    lst_INFRA = INFRA.loc[INFRA['Nr_A1'] != '0', 'Nr_TUC'].drop_duplicates()
    axA1 = INFRA.groupby('Nr_TUC')['Nr_A1'].last()
    INCRini.loc[(INCRini['Nr_TUC'].isin(lst_INFRA)) & 
                (INCRini['Nr_A1'] == INCRini['Nr_TUC'].map(axA1)), 'FLG_INFRA'] = 1

    ORCAM = pd.read_csv("tabelas/TBL_TUC_ORC.csv",sep="|",decimal=',',on_bad_lines='skip',
                        encoding="Latin-1",dtype=str);
    tbl_CNTB = pd.read_csv("tabelas/tbl_CNTB.csv",sep="|",decimal=',',on_bad_lines='skip',
                        encoding="Latin-1",dtype=str);
    
    lst_OE = ORCAM[ORCAM['Nr_A1'] == '0']['Nr_TUC'].drop_duplicates().tolist()
    lst_CNT_OE = tbl_CNTB[tbl_CNTB['Nm_RZ_ANAL'] == 
                'Edificações, obras civis e benfeitorias']['Cd_CC'].drop_duplicates().tolist()

    INCRini['FLG_ORC'] = 0
    INCRini.loc[INCRini['Nr_TUC'].isin(lst_OE) & 
                INCRini['Cd_CC'].isin(lst_CNT_OE), 'FLG_ORC'] = 1

    if st: avl.progress(55, text = 'Classificando a Tipologia...')

    TI_AX = TI[['Id_TI', 'Txt_Class']].rename(columns={'Id_TI': 'Nr_TI', 'Txt_Class': 'Cd_TI'})
    INCRini=INCRini.merge(TI_AX,how='left',on='Nr_TI')

    SQLq = f"""
                SELECT 
                    Id_COM_CA,
                    Nr_TI as Cd_TI,
                    PCT_COM,
                    PCT_CA,
                    FLG_PLPT as FLG_PLPT_OE
                FROM 
                    COM_CA_BPC t1 
                WHERE
                    dt_ARQ = ?
            """
    COM_CA_BPC = sql.imp_tbl_forma_001('COM_CA_BPC', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
    if len(COM_CA_BPC) == 0:
        COM_CA_BPC = pd.DataFrame(columns = ['Id_COM_CA','Cd_TI','Pct_COM','Pct_CA','FLG_PLPT_OE'])


    INCRini = INCRini.merge(COM_CA_BPC[['Cd_TI','FLG_PLPT_OE','Pct_COM','Pct_CA']], how='left', on=['Cd_TI','FLG_PLPT_OE'])
    INCRini = INCRini.merge(ROS_SINT, how='outer', on = ['Cd_ODI','Cd_SubODI'], suffixes=("","_ROS"), indicator=True)

    map_dict = {
                'both' : 'NO',
                'left_only' : 'Presente no INCR, verifique se Cd_ODI e Cd_SubODI estão corretos ou se há justificativa da empresa.',
                'right_only' : 'Presente no ROS, verifique se Cd_ODI e Cd_SubODI estão corretos ou se há justificativa da empresa.',
                }

    INCRini['TST_ROS'] = INCRini['_merge'].map(map_dict)
    INCRini['Pct_OE'] = pd.to_numeric(INCRini['Pct_OE'].astype(str).replace(",","."), errors='coerce')
    INCRini = INCRini.drop(columns=['_merge'])
    INCRini['VL_OE_INCR'] = INCRini['Pct_OE'].fillna(0.) * INCRini['VL_VOC'].fillna(0.)

    map_dict = {
                '0': 'NA',
                '1': 'PlPT',
                '2': 'MLA', 
                '3': 'Subvenção de CCC',
                '4': 'Doações',
                '5': 'Participação Financeira do Consumidor',
                '6': 'Repasses de Recursos dos Governos Federal, Estadual, Distrital e Municipal',
                '7': 'Incorporação',
                '8': 'Outros',
                }

    INCRini['Tipo_OE'] = INCRini['Cd_Tipo_OE'].fillna('0').map(map_dict)
    INCRini['OBS_OE'] = ""
    tst_ros_ok = INCRini['TST_ROS'].eq('NO')
    tipo_oe = INCRini['Cd_Tipo_OE'].fillna('0').astype(str)
    flg_doa = INCRini['FLG_DOA_OE'].astype(str)
    flg_incor = INCRini['FLG_INCOR_OE'].astype(str)

    def add_obs(mask, texto):
        INCRini.loc[mask, 'OBS_OE'] += texto + "; "


    add_obs(
                ~tst_ros_ok,
                "Refazer o teste após corrigir arquivos ROS ou INCR"
            )

    add_obs(
                tst_ros_ok & tipo_oe.eq('4') & flg_doa.ne('1'),
                "FLG_DOA_OE deve ser unitário ou Cd_Tipo_OE, no ROS, está incorreto"
            )

    add_obs(
                tst_ros_ok & tipo_oe.ne('4') & flg_doa.eq('1'),
                "Cd_Tipo_OE, no ROS, deve ser 4 ou FLG_DOA_OE, no INCR, está incorreto"
            )

    add_obs(
                tst_ros_ok & tipo_oe.eq('7') & flg_incor.ne('1'),
                "FLG_INCOR_OE deve ser unitário ou Cd_Tipo_OE, no ROS, está incorreto"
            )

    add_obs(
                tst_ros_ok & tipo_oe.ne('7') & flg_incor.eq('1'),
                "Cd_Tipo_OE, no ROS, deve ser 7 ou FLG_INCOR_OE, no INCR, está incorreto"
            )

    INCRini['OBS_OE'] = (
                            INCRini['OBS_OE']
                            .str.rstrip('; ')
                            .replace('', 'NO')
                        )

    df_PROB = INCRini[INCRini['Id_SEQ_INC'].isnull()][['Cd_ODI','Cd_SubODI','TST_ROS']].copy()
    df_PROB.to_csv(rf"{dir_arq_saida}/dados_ros_inc_div.csv", sep="|", decimal=",", encoding='latin-1', index=False)
    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf"{dir_arq_saida}/dados_ros_inc_div.csv",
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)

    INCRini = INCRini[INCRini['Id_SEQ_INC'].notnull()].copy().reset_index(drop=True)

    if st: avl.progress(57, text = 'Verificando método de avaliação...')

    #############################################################################################################################
    #############################################################################################################################
    #                                                    MÉTODO DE AVALIAÇÃO                                                    #
    #############################################################################################################################
    INCRini['MTD_AVAL']='A'
    invalido_sff = ['', '0', 'ND']
    invalido_vals = [0, '', '0',  'ND']

    mask = (
                ~INCRini['Cd_SISBASE_SFF'].isin(invalido_sff) &
                INCRini['VL_VF'].notna() &
                INCRini['VL_COM'].notna() &
                INCRini['VL_CA'].notna() &
                ~INCRini['VL_COM'].fillna("ND").isin(invalido_vals) &
                ~INCRini['VL_CA'].fillna("ND").isin(invalido_vals) &
                ~INCRini['VL_VF'].fillna("ND").isin(invalido_vals)
            )

    INCRini.loc[mask, 'MTD_AVAL'] = 'BPR'
    INCRini.loc[(INCRini['Dt_Imob'] < datetime.strptime('2016-06-01', "%Y-%m-%d")) &
                (INCRini['VL_VF'] != 0) & (INCRini['VL_VF'] != 'ND'),'MTD_AVAL'] = 'BPC'
    INCRini.loc[(INCRini['Cd_TP_AVAL'] == '5') & (INCRini['FLG_PLPT_OE'] == '1') &
                (INCRini['VL_VF'] != 0) & (INCRini['VL_VF'] != 'ND'),'MTD_AVAL'] = 'BPC'
    INCRini.loc[(INCRini['FLG_INFRA'] == 1), 'MTD_AVAL'] = 'A'
    INCRini.loc[(INCRini['FLG_OAT'] == '1') & (INCRini['Cd_TP_AVAL'] != '2'), 'MTD_AVAL'] = 'A'
    INCRini.loc[(INCRini['FLG_DOA_OE']=='1'), 'MTD_AVAL'] = 'A'
    INCRini.loc[(INCRini['FLG_INCOR_OE']=='1'), 'MTD_AVAL']='A'
    INCRini.loc[(INCRini['FLG_RSV']=='1'), 'MTD_AVAL']='A'
    INCRini.loc[(INCRini['Cd_UAR'] == 'UAR'), 'MTD_AVAL']='A'
    INCRini.loc[(INCRini['Nr_TI']=='98'), 'MTD_AVAL']='A'
    INCRini.loc[INCRini['Cd_Tipo_OE'].astype(str).isin(['3','4','7']), 'MTD_AVAL']='A'
    INCRini.loc[(INCRini['FLG_ORC']==1) | (INCRini['Cd_TP_AVAL'] == '4'),'MTD_AVAL'] = 'ORC'

    INCRini['VL_VF_TOT'] = 0
    INCRini['VL_COM_TOT'] = 0
    INCRini['VL_CA_TOT'] = 0
    INCRini['VL_JOA_TOT'] = 0
    INCRini = INCRini.drop(columns=['Cd_Tipo_OE'])
    if st: avl.progress(59, text = 'Calculando VNR...')
    #############################################################################################################################
    #############################################################################################################################
    #                                                         VALOR BPC                                                         #
    #############################################################################################################################
    colunas = ['Cd_Patrim','Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6']
    INCRini['CHV_FAM'] = INCRini[colunas].astype(str).agg('_'.join, axis=1)
    

    familias = INCRini[INCRini['Cd_TP_AVAL']=='2'].groupby('CHV_FAM')['Cd_UAR'].nunique()
    cd_familias = familias[familias > 1].index    
    INCRini.loc[INCRini['CHV_FAM'].isin(cd_familias),'MTD_AVAL'] = 'BPR_F'

    # Verificar se existe VF para o item principal da familia
    familias_VF = INCRini[
                            (INCRini['MTD_AVAL']=='BPR_F') &
                            (INCRini['Cd_UAR']!='UAR') &
                            (INCRini['VL_VF'].fillna(0) == 0)
                         ]['CHV_FAM'].unique()

    INCRini.loc[INCRini['CHV_FAM'].isin(familias_VF) & (INCRini['MTD_AVAL'] == 'BPR_F'), 'MTD_AVAL'] = 'A'
    INCRini.loc[INCRini['CHV_FAM'].isin(cd_familias),'TST_VF_ROA_AVL'] = 'Família e BPR, fazer testes'

    bprf = INCRini['MTD_AVAL']=='BPR_F'
    bpr = INCRini['MTD_AVAL']=='BPR'
    orc = INCRini['MTD_AVAL'] == 'ORC'
    bpc = INCRini['MTD_AVAL'] == 'BPC'
    if len(COM_CA_BPC) > 0:
        INCRini['VL_VF'].fillna(0, inplace=True)
        INCRini.loc[bpc, 'VL_VF_TOT'] = INCRini['VL_VF'].where(INCRini['VL_VF'] != 0, INCRini['VL_VNR_VF_UNIT']) * INCRini['Qtd_AIS']
        INCRini.loc[bpc, 'VL_COM_TOT'] = INCRini['VL_VF_TOT'] * INCRini['Pct_COM']
        INCRini.loc[bpc, 'VL_CA_TOT'] = (INCRini['VL_VF_TOT'] + INCRini['VL_COM_TOT']) * INCRini['Pct_CA']
        INCRini.loc[bpc, 'VL_JOA_TOT'] = (INCRini['VL_VF_TOT'] + INCRini['VL_COM_TOT'] + 
        INCRini['VL_CA_TOT']) * INCRini['Tx_JOA']
        INCRini.loc[bpc, 'VL_BPRC_TOT'] = INCRini.loc[bpc, ['VL_VF_TOT', 'VL_COM_TOT', 
                                                            'VL_CA_TOT', 'VL_JOA_TOT']].sum(axis=1)

    #############################################################################################################################
    #############################################################################################################################
    #                                                         VALOR BPR                                                         #
    #############################################################################################################################
    INCRini.loc[bpr,'VL_VF_TOT'] = INCRini['VL_VF']*INCRini['Qtd_AIS']
    INCRini.loc[bpr,'VL_COM_TOT'] = INCRini['VL_COM_AT']*INCRini['Qtd_AIS']
    INCRini.loc[bpr,'VL_CA_TOT'] = INCRini['VL_CA_AT']*INCRini['Qtd_AIS']
    somaVOC_Cd_PATR = INCRini[bprf].groupby('Cd_Patrim')['VL_VOC'].transform('sum')
    INCRini.loc[bprf,'VL_VF_TOT'] = INCRini['VL_VF']*INCRini['Qtd_AIS']*INCRini['VL_VOC']/somaVOC_Cd_PATR
    INCRini.loc[bprf,'VL_COM_TOT'] = INCRini['VL_COM_AT']*INCRini['Qtd_AIS']*INCRini['VL_VOC']/somaVOC_Cd_PATR
    INCRini.loc[bprf,'VL_CA_TOT'] = INCRini['VL_CA_AT']*INCRini['Qtd_AIS']*INCRini['VL_VOC']/somaVOC_Cd_PATR
    INCRini.loc[bpr | bprf,'VL_JOA_TOT'] = ((INCRini['VL_VF_TOT'] + INCRini['VL_COM_TOT'] +
                                    INCRini['VL_CA_TOT'])*INCRini['Tx_JOA'])
    INCRini.loc[bpr | bprf,'VL_BPRC_TOT'] = INCRini.loc[bpr | bprf,['VL_VF_TOT', 'VL_COM_TOT', 
                                                    'VL_CA_TOT', 'VL_JOA_TOT']].sum(axis=1)
    INCRini.loc[INCRini['MTD_AVAL'].str.startswith('BPR'), 'MTD_AVAL'] = 'BPR'
    #############################################################################################################################
    #############################################################################################################################
    #                                                         FATOR AJUSTE                                                      #
    #############################################################################################################################
    # Vamos considerar os itens marcados pela avaliadora, considerando que a versão final estará conciliadda
    BASE_BPR = INCRini[INCRini['Cd_TP_AVAL'].astype(str) == '2'].groupby('Cd_TI', dropna=False)[['VL_VOCsjoa_IMB_AT','VL_BPRC_TOT','VL_JOA_TOT']].sum().reset_index()
    BASE_BPR['PER_VAR']=(BASE_BPR['VL_BPRC_TOT'] - BASE_BPR['VL_JOA_TOT'])/BASE_BPR['VL_VOCsjoa_IMB_AT']
    BASE_BPR['Cd_ANL'] = 'OK'
    BASE_BPR['FT_AJS']=1
    AJ90 = BASE_BPR['PER_VAR']<0.9
    AJ110 = BASE_BPR['PER_VAR']>1.1
    BASE_BPR.loc[AJ90,'Cd_ANL'] = 'LIM 90%'
    BASE_BPR.loc[AJ110,'Cd_ANL'] ='LIM 110%'
    BASE_BPR.loc[AJ90,'FT_AJS'] = 0.9/BASE_BPR['PER_VAR']
    BASE_BPR.loc[AJ110,'FT_AJS'] = 1.1/BASE_BPR['PER_VAR']
    BASE_BPR_AX = BASE_BPR[['Cd_TI','Cd_ANL','FT_AJS']]
    INCRini = INCRini.merge(BASE_BPR_AX, how='left', on='Cd_TI')

    INCRini.loc[bpr | bprf,'VL_BPR_TOT_AJS'] = (((INCRini.loc[bpr | bprf,'VL_CA_TOT'] + 
                                          INCRini.loc[bpr | bprf,'VL_COM_TOT'])*INCRini.loc[bpr | bprf,'FT_AJS'] + 
                                          INCRini.loc[bpr | bprf,'VL_VF_TOT'] )* (1 + INCRini.loc[bpr | bprf,'Tx_JOA']))

    
    #############################################################################################################################
    #############################################################################################################################
    #                                                           VNR                                                             #
    #############################################################################################################################
    INCRini['VL_VNR_SFF'] = INCRini['VL_VOCsjoa_IMB_AT'] + INCRini['VL_JOA_IMB_AT']
    INCRini.loc[bpr | bprf,'VL_VNR_SFF'] = INCRini['VL_BPR_TOT_AJS']
    INCRini.loc[bpc & (INCRini['VL_BPRC_TOT'] > 0),'VL_VNR_SFF'] = INCRini['VL_BPRC_TOT']
    INCRini.loc[orc,'VL_VNR_SFF'] = INCRini['VL_VNR_UC']

    mask = ((INCRini['FLG_ELIG'].fillna('0').astype(str) == '0') | 
            (INCRini['Cd_CONC'].fillna('2').astype(str) == '2'))

    INCRini.loc[mask,'VL_VNR_SFF'] = 0

    map_dict = {
                    '1' : 'A',
                    '2' : 'BPR',
                    '3' : 'BPC',
                    '4' : 'ORC'
                }

    INCRini['TST_AX'] = INCRini['Cd_TP_AVAL'].map(map_dict)
    INCRini.loc[INCRini['TST_AX'].isnull(), 'TST_AX'] = INCRini.loc[INCRini['TST_AX'].isnull(), 'MTD_AVAL']    
    INCRini['Pct_Delta_VNR'] = (
                                    (INCRini['VL_VNR_SFF'] - INCRini['VL_VNR_UC']) /
                                    INCRini['VL_VNR_SFF'].replace(0, np.nan).fillna(INCRini['VL_VNR_UC'])
                                )
    INCRini.loc[(INCRini['VL_VNR_SFF'] == 0) & (INCRini['VL_VNR_UC'] == 0), 'Pct_Delta_VNR'] = np.inf
    
    tol = 0.005
    condicao_1 = INCRini['MTD_AVAL'] != INCRini['TST_AX']
    condicao_2 = INCRini['Pct_Delta_VNR'] > tol
    condicao_3 = INCRini['Pct_Delta_VNR'] < -tol

    INCRini['TST_VNR'] = np.where(
        condicao_1,
        np.where(
            condicao_2,
            "O método de valoração simulado, pela SFF, " + INCRini['MTD_AVAL'] + ", difere do aplicado pela avaliadora, " + INCRini['TST_AX'] + "."
            " Isso resulta em uma diferença a maior, simulado maior.",
            np.where(condicao_3,
            "O método de valoração simulado, pela SFF, " + INCRini['MTD_AVAL'] + ", difere do aplicado pela avaliadora, " + INCRini['TST_AX'] + "."
            " Isso resulta em uma diferença a menor, simulado menor.",
            "VNR simulado de acordo com o apresentado")
        ),
        np.where(
            condicao_2,
            "O método de valoração simulado, pela SFF, " + INCRini['MTD_AVAL'] + ", concorda com o aplicado pela avaliadora, " + INCRini['TST_AX'] + "."
            " Todavia há uma diferença a maior, simulado maior.",
            np.where(condicao_3,
            "O método de valoração simulado, pela SFF, " + INCRini['MTD_AVAL'] + ", concorda com o do aplicado pela avaliadora, " + INCRini['TST_AX'] + "."
            " Todavia há uma diferença a menor, simulado menor.",
            "VNR simulado de acordo com o apresentado")
        )
    )

    df_TESTE = (INCRini.groupby(['TST_AX','MTD_AVAL','TST_VNR'])
                .agg(
                        VL_PCT_MEDIA = ('Pct_Delta_VNR', 'mean'),
                        VL_PCT_MIN = ('Pct_Delta_VNR', 'min'),
                        VL_PCT_MAX = ('Pct_Delta_VNR', 'max'),
                        VL_PCT_STD = ('Pct_Delta_VNR', 'std'),
                        QTD_OCOR = ('Pct_Delta_VNR', 'count'),
                        VL_VNR_AVAL = ('VL_VNR_UC', 'sum'),
                        VL_VNR_SFF = ('VL_VNR_SFF', 'sum')
                    )
                .reset_index()
                .assign(
                        PCT_AVAL_TOT = lambda x: x['VL_VNR_AVAL'] / INCRini['VL_VNR_UC'].sum()
                )
                )

    df_TESTE.to_sql("AVL_VNR_SIMULADO", con, if_exists='replace', index=True)
    INCRini = INCRini.drop(columns = ['TST_AX'])
    INCRini['TESTE_ORC'] = 'OK'
    tst_ORC = INCRini[INCRini['Cd_TP_AVAL'].astype(str)=='4'].copy()
    if len(tst_ORC)>0:
        tst_ORC['VL_VOC_ORCa'] = tst_ORC['VL_VOC'] * tst_ORC['FA_IPCA']
        tst_ORC = tst_ORC.groupby('Cd_SubODI', dropna=False)[['VL_VOC_ORCa','VL_VNR_UC']].sum().reset_index()
        tst_ORC['REL'] = tst_ORC['VL_VOC_ORCa'].fillna(0) / (tst_ORC['VL_VNR_UC'].fillna(0) + 1e-6)
        tst_ORC['FLG'] = (tst_ORC['REL'] > 1.3) | (tst_ORC['REL'] < 0.76923)
        INCRini.loc[orc & INCRini['Cd_SubODI'].isin(tst_ORC[tst_ORC['FLG']]['Cd_SubODI'].to_list()),'TESTE_ORC'] = 'Avaliadora deve justificar as diferenças deste orçamento'
    
    INCRini.loc[bpr | bprf,'Cd_ANL'] = 'NA'
    INCRini.loc[~(bpr | bprf),'FT_AJS'] = 1
    INCRini.loc[bpr | bprf,'TST_JOA'] = 'OK'
    INCRini.loc[INCRini['Cd_CONC'].astype(str) == '2', 'VL_VNR_SFF'] = 0
    INCRini=INCRini.merge(tbl_CNTB, how='left', on='Cd_CC')
    LST_TI = (
            list(range(10, 30)) + list(range(70, 80)) + [82, 94, 95, 97, 99] +
            [str(x) for x in range(10, 30)] + [str(x) for x in range(70, 80)] + ['82', '94', '95', '97', '99']
            )
    
    INCRini.loc[(INCRini['TP_BEM'].astype(str) == '4'),'Nm_CLASS'] = 'BAR'

    dic_Q1A = {
    '1.1' : (INCRini['Cd_CC'].astype(str).isin(['123310101','123310401','123320101',
                                                 '123320401','123330101','123330401',
                                                 '123340101','123350101']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Servidões permanentes')),
    '1.2' : (INCRini['Cd_CC'].astype(str).isin(['123310103','123310403','123320103',
                                                 '123320403','123330103','123330403',
                                                 '123340103','123350103']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Softwares')),
    '1.3' : (INCRini['Cd_CC'].astype(str).isin(['123310199','123310499','123320199',
                                                 '123320499','123330199','123330499',
                                                 '123340199','123350199']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Outros')),
    '2.1' : (INCRini['Cd_CC'].astype(str).isin(['123210101','123210402']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Terrenos')),                                             
    '2.2' : (INCRini['Cd_CC'].astype(str).isin(['123220101','123220402','123230101','123230402']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Terrenos')),
    '2.3' : (INCRini['Cd_CC'].astype(str).isin(['123240101']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Terrenos')),
    '2.4' : (INCRini['Cd_CC'].astype(str).isin(['123250101']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Terrenos')),
    '3' : (INCRini['Cd_CC'].astype(str).isin(['123210102','123210402']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Reservatórios, barragens e adutoras')),
    '4.1' : (INCRini['Cd_CC'].astype(str).isin(['123210103','123210403']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Edificações, obras civis e benfeitorias')),
    '4.2' : (INCRini['Cd_CC'].astype(str).isin(['123220103','123220403','123230103','123230403']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Edificações, obras civis e benfeitorias')),
    '4.3' : (INCRini['Cd_CC'].astype(str).isin(['123240103']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Edificações, obras civis e benfeitorias')),
    '4.4' : (INCRini['Cd_CC'].astype(str).isin(['123250103']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Edificações, obras civis e benfeitorias')),
    '5.1' : (INCRini['Cd_CC'].astype(str).isin(['123210104','123210404']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Máquinas e equipamentos')),
    '5.2' : (INCRini['Cd_CC'].astype(str).isin(['123220104','123220404','123230104','123230404']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Máquinas e equipamentos')),
    '5.3' : (INCRini['Cd_CC'].astype(str).isin(['123240104']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Máquinas e equipamentos')),
    '5.4' : (INCRini['Cd_CC'].astype(str).isin(['123250104']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Máquinas e equipamentos')),
    '6.1' : (INCRini['Cd_CC'].astype(str).isin(['123210105','123210405']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Veículos')),
    '6.2' : (INCRini['Cd_CC'].astype(str).isin(['123220105','123220405','123230105','123230405']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Veículos')),
    '6.3' : (INCRini['Cd_CC'].astype(str).isin(['123240105']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Veículos')),
    '6.4' : (INCRini['Cd_CC'].astype(str).isin(['123250105']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Veículos')),
    '7.1' : (INCRini['Cd_CC'].astype(str).isin(['123210106','123210406']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Móveis e utensílios')),
    '7.2' : (INCRini['Cd_CC'].astype(str).isin(['123220106','123220406','123230106','123230406']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Móveis e utensílios')),
    '7.3' : (INCRini['Cd_CC'].astype(str).isin(['123240106']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Móveis e utensílios')),
    '7.4' : (INCRini['Cd_CC'].astype(str).isin(['123250106']) &
                                                 (INCRini['Nm_RZ_ANAL'].astype(str) == 'Móveis e utensílios'))}
    
    for Cd_1A, crit in dic_Q1A.items():
        INCRini.loc[crit, 'Cd_Q1A'] = Cd_1A

    INCRini.loc[(INCRini['TP_BEM'].astype(str) == '4') &  INCRini['Cd_Q1A'].astype(str).isin(['1.1']), 'Cd_Q1A'] = '1.3'
    INCRini.loc[(INCRini['TP_BEM'].astype(str) == '4') &  INCRini['Cd_Q1A'].astype(str).isin(['2.1',
                                                                                              '2.2']), 'Cd_Q1A'] = '2.3'
    INCRini.loc[(INCRini['TP_BEM'].astype(str) == '4') &  INCRini['Cd_Q1A'].astype(str).isin(['4.1',
                                                                                              '4.2']), 'Cd_Q1A'] = '4.3'
    INCRini.loc[(INCRini['TP_BEM'].astype(str) == '4') &  INCRini['Cd_Q1A'].astype(str).isin(['5.1',
                                                                                              '5.2']), 'Cd_Q1A'] = '5.3'
    mask1 = INCRini['Nr_TI'].astype(str).isin(['70','71','72','80','81','82','90','91','94','95'])
    INCRini.loc[mask1 &  INCRini['Cd_Q1A'].astype(str).isin(['2.1','2.2']), 'Nm_CLASS'] = 'BAR'
    INCRini.loc[mask1 &  INCRini['Cd_Q1A'].astype(str).isin(['4.1','4.2']), 'Nm_CLASS'] = 'BAR'
    INCRini.loc[mask1 &  INCRini['Cd_Q1A'].astype(str).isin(['5.1','5.2']), 'Nm_CLASS'] = 'BAR'
    INCRini.loc[mask1 &  INCRini['Cd_Q1A'].astype(str).isin(['2.1','2.2']), 'Cd_Q1A'] = '2.3'
    INCRini.loc[mask1 &  INCRini['Cd_Q1A'].astype(str).isin(['4.1','4.2']), 'Cd_Q1A'] = '4.3'
    INCRini.loc[mask1 &  INCRini['Cd_Q1A'].astype(str).isin(['5.1','5.2']), 'Cd_Q1A'] = '5.3'
    
    ex_Cd_Q5 = INCRini['Cd_Q5'].isnull()
    dif_Cd_Q5 = ~ex_Cd_Q5 & (INCRini['Cd_Q5'] != INCRini['Cd_Q1A'])
    INCRini['OBS_Cd_Q5'] = ''

    def add_obs1(mask, texto):
        if callable(texto):
            texto = texto(INCRini.loc[mask])

        if isinstance(texto, pd.Series):
            INCRini.loc[mask, 'OBS_Cd_Q5'] += texto.astype(str) + "; "
        else:
            INCRini.loc[mask, 'OBS_Cd_Q5'] += str(texto) + "; "

    add_obs1(
                ~tst_ros_ok,
                "Refazer o teste após corrigir arquivos ROS ou INCR"
            )
    add_obs1(
                ex_Cd_Q5,
                "Pedir para a avaliadora preencher o campo Cd_Q5 no arquivo INCR"
            )
    add_obs1(
                dif_Cd_Q5,
                lambda df: (
                                "Avaliar se a classificação do quadro resumo da STR está correta. "
                                "Cd_Q1A: " + df['Cd_Q1A'].fillna('ausente').astype(str)
                            )
            )

    INCRini['OBS_Cd_Q5'] = (
                            INCRini['OBS_Cd_Q5']
                            .str.rstrip('; ')
                            .replace('', 'NO')
                        )
    
    mask1 = INCRini['Id_SEQ_INC'].notnull()
    df_ALERTA = INCRini[mask1][['Id_SEQ_INC','OBS_Cd_Q5']].copy().rename(columns={'OBS_Cd_Q5':'OBS_FISC'})
    txtALERTAS = pd.concat([txtALERTAS,df_ALERTA], ignore_index=True)

    mask1 = INCRini['TST_JOA'].notnull() & (INCRini['TST_JOA'] !='OK')
    df_ALERTA = INCRini[mask1][['Id_SEQ_INC','TST_JOA']].copy().rename(columns={'TST_JOA':'OBS_FISC'})
    txtALERTAS = pd.concat([txtALERTAS,df_ALERTA], ignore_index=True)

    mask1 = INCRini['TST_VF_ROA_AVL'].notnull() & (INCRini['TST_VF_ROA_AVL'] !='NO')
    df_ALERTA = INCRini[mask1][['Id_SEQ_INC','TST_VF_ROA_AVL']].copy().rename(columns={'TST_VF_ROA_AVL':'OBS_FISC'})
    txtALERTAS = pd.concat([txtALERTAS,df_ALERTA], ignore_index=True)

    mask1 = INCRini['TST_QTD_ROA_AVL'].notnull() & (~INCRini['TST_QTD_ROA_AVL'].isin(['NO',
                    'NA, no ROA é composto por diversos itens (sistema) ou se trata de apropriação direta.']))
    df_ALERTA = INCRini[mask1][['Id_SEQ_INC','TST_QTD_ROA_AVL']].copy().rename(columns={'TST_QTD_ROA_AVL':'OBS_FISC'})
    txtALERTAS = pd.concat([txtALERTAS,df_ALERTA], ignore_index=True)

    mask1 = INCRini['Tst_COMpCA'].notnull() & (~INCRini['Tst_COMpCA'].isin(['NO']))
    df_ALERTA = INCRini[mask1][['Id_SEQ_INC','Tst_COMpCA']].copy().rename(columns={'Tst_COMpCA':'OBS_FISC'})
    txtALERTAS = pd.concat([txtALERTAS,df_ALERTA], ignore_index=True)

    mask1 = INCRini['OBS_FISC'].notnull() & (~INCRini['OBS_FISC'].isin(['NO']))
    df_ALERTA = INCRini[mask1][['Id_SEQ_INC','OBS_FISC']].copy().rename(columns={'OBS_FISC':'OBS_FISC'})
    txtALERTAS = pd.concat([txtALERTAS,df_ALERTA], ignore_index=True)

    mask1 = INCRini['TST_ROS'].notnull() & (~INCRini['TST_ROS'].isin(['NO']))
    df_ALERTA = INCRini[mask1][['Id_SEQ_INC','TST_ROS']].copy().rename(columns={'TST_ROS':'OBS_FISC'})
    txtALERTAS = pd.concat([txtALERTAS,df_ALERTA], ignore_index=True)

    mask1 = INCRini['OBS_OE'].notnull() & (~INCRini['OBS_OE'].isin(['NO']))
    df_ALERTA = INCRini[mask1][['Id_SEQ_INC','OBS_OE']].copy().rename(columns={'OBS_OE':'OBS_FISC'})
    txtALERTAS = pd.concat([txtALERTAS,df_ALERTA], ignore_index=True)

    mask1 = INCRini['TST_VNR'].notnull() & (~INCRini['TST_VNR'].isin(['VNR simulado de acordo com o apresentado']))
    df_ALERTA = INCRini.loc[
                                mask1,
                                ['Id_SEQ_INC', 'TST_VNR', 'Pct_Delta_VNR']
                            ].copy()
    df_ALERTA['TST_VNR'] = (
                                df_ALERTA['TST_VNR'].astype(str)
                                + " (diferença percentual: "
                                + df_ALERTA['Pct_Delta_VNR'].map('{:.2%}'.format)
                                + ")"
                            )
    df_ALERTA = (
                    df_ALERTA[['Id_SEQ_INC', 'TST_VNR']]
                    .rename(columns={'TST_VNR': 'OBS_FISC'})
                )
    txtALERTAS = pd.concat([txtALERTAS,df_ALERTA], ignore_index=True)

    if st: avl.progress(64, text = 'Calculando Depreciação...')

    AIS_TX = INCRini[['Id_SEQ_INC','Cd_CC','Nr_TUC','Nr_A1','Nr_A2','Dt_CNTB_AJST','Dt_Imob',
                'DT_IMB_BASE','VL_VOC','VL_DEP_ACUM','VL_VNR_UC','VL_DAC_UC','Dt_REF_DADOS',
                'Cd_CONC']].copy()

    AIS_TX = calc_tx_md(AIS_TX, depr)
    INCRini = INCRini.merge(AIS_TX, how='left', on='Id_SEQ_INC')
    #############################################################################################################################
    if st: avl.progress(75, text = 'Verificando datas de imobilização em relação à energização...')
    SQLq = f"""
                SELECT 
                    t1.Cd_SubODI, 
                    t1.Dt_Energ,
                    DATETIME(t1.Dt_Energ, '+90 days') AS DT_LIM_UNIT
                FROM 
                    ROS t1 
                WHERE 
                    dt_ARQ = ?
                GROUP BY 
                    Cd_SubODI;
            """
    ROS = sql.imp_tbl_forma_001('ROS', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
    SQLq = f"""
                SELECT 
                    t1.Cd_Patrim, 
                    t1.Cd_DIG_INC,
                    t1.Dt_Energ,
                    DATETIME(t1.Dt_Energ, '+90 days') AS DT_LIM_UNIT
                FROM 
                    DT_ENERG t1 
                WHERE 
                    dt_ARQ = ?
                GROUP BY 
                    Cd_Patrim, Cd_DIG_INC;
            """
    DT_ENERG = sql.imp_tbl_forma_001('DT_ENERG', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
    if len(DT_ENERG)>0:
        INCRini = INCRini.merge(DT_ENERG, how='left', on=['Cd_Patrim', 'Cd_DIG_INC'])
    else:
        INCRini = INCRini.merge(ROS, how='left', on=['Cd_SubODI'])

    INCRini['TST_DT_IMOB'] = 'OK'
    INCRini.loc[INCRini['Dt_Energ'] > INCRini['Dt_CNTB_AJST'],
            'TST_DT_IMOB'] = 'DATA DE ENERGIZAÇÃO MAIOR QUE A DATA CONTÁBIL AJUSTADA INFORMADA'
    INCRini.loc[INCRini['Dt_CNTB_AJST'] > INCRini['DT_LIM_UNIT'],
            'TST_DT_IMOB'] = """ATRASO NA UNITIZAÇÃO, APÓS CORREÇÃO DA AVALIADORA, (>90 DIAS 
                                DA ENERGIZAÇÃO)"""
    INCRini.loc[INCRini['Dt_Energ'].isnull(),
                'TST_DT_IMOB'] = 'DATA DE ENERGIZAÇÃO NÃO INFORMADA'
    INCRini.loc[(INCRini['FLG_DOA_OE'].astype(str) == '1') & (INCRini['TST_DT_IMOB'] != 'OK'),
                'TST_DT_IMOB'] = 'DOAÇÃO, TESTE NÃO SE APLICA'
    INCRini.loc[(INCRini['FLG_INCOR_OE'].astype(str) == '1') & (INCRini['TST_DT_IMOB'] != 'OK'),
                'TST_DT_IMOB'] = 'INCORPORAÇÃO, TESTE NÃO SE APLICA'
    INCRini.loc[((INCRini['FLG_ELIG'] == '0') | (INCRini['Cd_CONC'] != '1')), 
                ['VL_VNR_SFF', 'VL_AJUSTE', 'CT_AJUSTE']] = 0

    mask1 = INCRini['TST_DT_IMOB'].notnull() & (~INCRini['TST_DT_IMOB'].isin(['OK']))
    df_ALERTA = INCRini[mask1][['Id_SEQ_INC','TST_DT_IMOB']].copy().rename(columns={'TST_DT_IMOB':'OBS_FISC'})
    txtALERTAS = pd.concat([txtALERTAS,df_ALERTA], ignore_index=True)
    txtALERTAS = txtALERTAS.drop_duplicates()

    resumo = INCRini.groupby(by=['Cd_TP_AVAL','MTD_AVAL'],dropna=False)[['VL_VNR_SFF','VL_VNR_UC']].sum().reset_index()
    resumo['DELTA'] = resumo['VL_VNR_UC']  - resumo['VL_VNR_SFF'] 
    resumo["Pct"] = resumo['DELTA'] / resumo['DELTA'].sum()*100

    if st: avl.progress(85, text = 'Analisando o almoxarifado...')
    
    SQLq = f"""
                SELECT 
                    *
                FROM 
                    AO t1 
                WHERE 
                    dt_ARQ = ?;
            """
    ALMOX = sql.imp_tbl_forma_001('AO', SQLq = SQLq, con = con, st=st, Empresa=Empresa)
    LST_MAT_INC = INCR[['COD_ITEM','Txt_DESC_TECN']].drop_duplicates()
    LST_MAT_INC = LST_MAT_INC.fillna('ND')
    if 'CD_CC' in ALMOX.columns:
        ALMOX = ALMOX.rename(columns = {'IDE_SEQ_AO' : 'Id_SEQ_AO', 'CD_CC' : 'Cd_CC', 'DT_LCMTO' : 'Dt_LCMTO', 
                                        'VL_SALDO':'VL_LCMTO', 'QTD' : 'Qtd', 'CD_UND': 'Cd_UND', 
                                        'TXT_DESC_TECN' : 'Txt_DESC_TECN', 'FLG_SCT' : 'FLG_CLS'})
    elif 'FLG_SCT' in ALMOX.columns:
        ALMOX = ALMOX.rename(columns = {'IDE_SEQ_AO' : 'Id_SEQ_AO', 'CD_CC' : 'Cd_CC', 'DT_LCMTO' : 'Dt_LCMTO', 
                                        'VL_SALDO':'VL_LCMTO', 'QTD' : 'Qtd', 'CD_UND': 'Cd_UND', 
                                        'TXT_DESC_TECN' : 'Txt_DESC_TECN', 'FLG_SCT' : 'FLG_CLS'})

    ALMOX = ALMOX[~ALMOX['Cd_CC'].isin(['1107204', '1107203', '1107206'])]
    ALMOX = ALMOX.merge(LST_MAT_INC, how='left', on='COD_ITEM')
    ALMOX['COD_ITEM'] = ALMOX['COD_ITEM'].fillna('0')
    ALMOX['FLG_CLS_SFF'] = ALMOX['FLG_CLS']
    cod_item_zero = ALMOX['COD_ITEM'] == '0'
    cod_uar = ALMOX['COD_ITEM'].isin(INCRini['COD_ITEM'].drop_duplicates().to_list())
    ALMOX.loc[cod_item_zero | cod_uar, 'FLG_CLS_SFF'] = '1'
    ALMOX = ALMOX.drop(columns='Txt_DESC_TECN_y')
    ALMOX = ALMOX[['Id_SEQ_AO', 'Cd_CC', 'COD_ITEM', 'Dt_LCMTO', 'VL_LCMTO', 
                     'Qtd', 'Cd_UND', 'Txt_DESC_TECN_x', 'FLG_CLS', 
                     'FLG_CLS_SFF']].rename(columns={
                                                            'Txt_DESC_TECN_x': 'Txt_DESC_TECN'
                                                        })
    ALMOX['VL_LCMTO'] = pd.to_numeric(ALMOX['VL_LCMTO'].replace(',', '.'), errors='coerce')
    ALMOX['Dt_LCMTO'] = pd.to_datetime(ALMOX['Dt_LCMTO'], errors='coerce')
    
    VL_MENSAL = ALMOX.loc[ALMOX['FLG_CLS_SFF'] == '0'].groupby('Dt_LCMTO', 
                                                               as_index=False)['VL_LCMTO'].sum()
    if st: avl.progress(90, text = 'Salvando arquivos...')

    BASE_INC = {
                    '(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)': 0,
                    '(2) Índice de Aproveitamento Integral': 0,
                    '(3) Obrigações Especiais Bruta': 0,
                    '(4) Bens Totalmente Depreciados': 0,
                    '(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)': 0,
                    '(6) Depreciação Acumulada': 0,
                    '(7) AIS Líquido (Valor de Mercado em Uso)': 0,
                    '(8) Índice de Aproveitamento Depreciado': 0,
                    '(9) Valor da Base de Remuneração (VBR)': 0,
                    '(10) Almoxarifado em Operação': 0,
                    '(11) Ativo Diferido': 0,
                    '(12) Obrigações Especiais Liquida': 0,
                    '(13) Terrenos e Servidões': 0
                }

    BASE_INC['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = (
        BASE_INC['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
        BASE_INC['(2) Índice de Aproveitamento Integral'] - 
        BASE_INC['(3) Obrigações Especiais Bruta'] - 
        BASE_INC['(4) Bens Totalmente Depreciados'])
    BASE_INC['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)'] = (
        BASE_INC['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
        BASE_INC['(6) Depreciação Acumulada'] - 
        BASE_INC['(8) Índice de Aproveitamento Depreciado'] + 
        BASE_INC['(10) Almoxarifado em Operação'] + 
        BASE_INC['(11) Ativo Diferido'] - 
        BASE_INC['(12) Obrigações Especiais Liquida'] + 
        BASE_INC['(13) Terrenos e Servidões'])
    Cd_EMP = sql.bsc_cd_aneel(Empresa)
    arq = os.path.join(dir_arq_saida, f'tbl_resumo_INC_{Cd_EMP}.csv')
    if os.path.exists(arq):
        tbl_resumo = pd.read_csv(arq, sep="|", header=None, encoding="Latin-1")
        for n in range(len(tbl_resumo)):
            BASE_INC[tbl_resumo.loc[n, 0]] = tbl_resumo.loc[n, tbl_resumo.columns[-1]]
    
    if INCRini['Cd_Q5'].notnull().sum() == len(INCRini):
        colAGR = 'Cd_Q5'
    else:
        colAGR = 'Cd_Q1A'

    Cd1 = (INCRini['FLG_ELIG'].astype(str) == '1') & (INCRini['Cd_CONC'].astype(str).isin(['1','3'])) & (INCRini[colAGR].isin(['4.2', '5.2']))
    Cd2 = (INCRini['FLG_REG'].astype(str) == '1') & (INCRini['FLG_ELIG'].astype(str) == '1') & (INCRini['Cd_CONC'].astype(str).isin(['1','3'])) & (INCRini[colAGR].isin(['1.1', '2.2']))

    IMP_INCR = {
                '(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)': INCRini.loc[Cd1, 'VL_VNR_UC'].sum(),
                '(2) Índice de Aproveitamento Integral': INCRini.loc[Cd1, 'VL_IAI_UC'].sum(),
                '(3) Obrigações Especiais Bruta': BASE_INC['(3) Obrigações Especiais Bruta'],
                '(4) Bens Totalmente Depreciados': INCRini.loc[Cd1, 'VL_100DEP_UC'].sum(),
                '(6) Depreciação Acumulada': INCRini.loc[Cd1, 'VL_DAC_UC'].sum(),
                '(7) AIS Líquido (Valor de Mercado em Uso)': INCRini.loc[Cd1, 'VL_VMU_UC'].sum(),
                '(8) Índice de Aproveitamento Depreciado': INCRini.loc[Cd1, 'VL_IAD_UC'].sum(),
                '(9) Valor da Base de Remuneração (VBR)': INCRini.loc[Cd1, 'VL_VBR_UC'].sum(),
                '(10) Almoxarifado em Operação': VL_MENSAL['VL_LCMTO'].mean(),
                '(11) Ativo Diferido': 0,
                '(12) Obrigações Especiais Liquida': BASE_INC['(12) Obrigações Especiais Liquida'],
                '(13) Terrenos e Servidões': INCRini.loc[Cd2, 'VL_VBR_UC'].sum()
            }

    IMP_INCR['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = (
        IMP_INCR['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
        IMP_INCR['(2) Índice de Aproveitamento Integral'] - 
        IMP_INCR['(3) Obrigações Especiais Bruta'] - 
        IMP_INCR['(4) Bens Totalmente Depreciados'])
    IMP_INCR['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)'] = (
        IMP_INCR['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
        IMP_INCR['(6) Depreciação Acumulada'] - 
        IMP_INCR['(8) Índice de Aproveitamento Depreciado'] + 
        IMP_INCR['(10) Almoxarifado em Operação'] + 
        IMP_INCR['(11) Ativo Diferido'] - 
        IMP_INCR['(12) Obrigações Especiais Liquida'] + 
        IMP_INCR['(13) Terrenos e Servidões'])
    df1 = pd.DataFrame.from_dict(IMP_INCR, orient='index', columns=['Valor'])

    df1.to_csv(arq, header=False, sep="|", encoding="Latin-1")
    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = arq,
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    df1.to_sql("RES_INCR_QDTAR", con, if_exists='replace', index=True)

    IMP_INCR_SFF = {}
    IMP_INCR_SFF['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] = INCRini.loc[Cd1, 'VL_VNR_SFF'].sum()
    IMP_INCR_SFF['(2) Índice de Aproveitamento Integral'] = INCRini.loc[Cd1, 'VL_IAI_UC'].sum()
    IMP_INCR_SFF['(3) Obrigações Especiais Bruta'] = BASE_INC['(3) Obrigações Especiais Bruta']
    IMP_INCR_SFF['(4) Bens Totalmente Depreciados'] = INCRini.loc[Cd1, 'VL_100DEP_UC'].sum()
    IMP_INCR_SFF['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = (
        IMP_INCR_SFF['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)']
        - IMP_INCR_SFF['(2) Índice de Aproveitamento Integral']
        - IMP_INCR_SFF['(3) Obrigações Especiais Bruta']
        - IMP_INCR_SFF['(4) Bens Totalmente Depreciados']
    )
    IMP_INCR_SFF['(6) Depreciação Acumulada'] = (
        INCRini.loc[Cd1, 'VL_DAC_UC'].sum() #+ INCRini.loc[Cd1, 'VL_AJUSTE'].sum()
    )
    IMP_INCR_SFF['(7) AIS Líquido (Valor de Mercado em Uso)'] = (
        IMP_INCR_SFF['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)']
        - IMP_INCR_SFF['(6) Depreciação Acumulada']
    )
    IMP_INCR_SFF['(8) Índice de Aproveitamento Depreciado'] = INCRini.loc[Cd1, 'VL_IAD_UC'].sum()
    IMP_INCR_SFF['(9) Valor da Base de Remuneração (VBR)'] = (
        IMP_INCR_SFF['(7) AIS Líquido (Valor de Mercado em Uso)']
        - IMP_INCR_SFF['(8) Índice de Aproveitamento Depreciado']
    )
    IMP_INCR_SFF['(10) Almoxarifado em Operação'] = VL_MENSAL['VL_LCMTO'].mean()
    IMP_INCR_SFF['(11) Ativo Diferido'] = 0
    IMP_INCR_SFF['(12) Obrigações Especiais Liquida'] = BASE_INC['(12) Obrigações Especiais Liquida']
    IMP_INCR_SFF['(13) Terrenos e Servidões'] = (
        INCRini.loc[Cd2, 'VL_VNR_SFF'].sum()
        - INCRini.loc[Cd2, 'VL_IAD_UC'].sum()
    )
    IMP_INCR_SFF['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)'] = (
        IMP_INCR_SFF['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)']
        - IMP_INCR_SFF['(6) Depreciação Acumulada']
        - IMP_INCR_SFF['(8) Índice de Aproveitamento Depreciado']
        + IMP_INCR_SFF['(10) Almoxarifado em Operação']
        + IMP_INCR_SFF['(11) Ativo Diferido']
        - IMP_INCR_SFF['(12) Obrigações Especiais Liquida']
        + IMP_INCR_SFF['(13) Terrenos e Servidões']
    )

    df1_SFF = pd.DataFrame.from_dict(IMP_INCR_SFF, orient='index', columns=['Valor'])
    df1_SFF.to_sql("RES_INCR_QDTAR_SFF", con, if_exists='replace', index=True)
    
    LST_CD = [1,2,3,4]
    LST_NM = ['GER', 'DIST', 'ADM', 'COMER']
    BASE_INCavl = []
    BASE_INCanl = []
    df_AVL = pd.DataFrame()
    df_SFF = pd.DataFrame()
    for cd in LST_CD:
        Cd1 = (INCRini['FLG_ELIG'].astype(str) == '1') & (INCRini['Cd_CONC'].astype(str).isin(['1','3'])) & (INCRini[colAGR].isin([f'4.{cd}', f'5.{cd}',f'6.{cd}', f'7.{cd}']))
        if cd == 2:
            Cd2 = (INCRini['FLG_REG'].astype(str) == '1') & (INCRini['FLG_ELIG'].astype(str) == '1') & (INCRini['Cd_CONC'].astype(str).isin(['1','3'])) & (INCRini[colAGR].isin([f'1.1', f'2.{cd}']))
            VL_ALM = VL_MENSAL['VL_LCMTO'].mean()
            OEBR = BASE_INC['(3) Obrigações Especiais Bruta']
            OELQ = BASE_INC['(12) Obrigações Especiais Liquida']
        else:
            Cd2 = (INCRini['FLG_REG'].astype(str) == '1') & (INCRini['FLG_ELIG'].astype(str) == '1') & (INCRini['Cd_CONC'].astype(str).isin(['1','3'])) & (INCRini[colAGR].isin([f'2.{cd}']))
            VL_ALM = 0
            OEBR = 0
            OELQ = 0
        if cd == 3:
            Cd1 = Cd1 | (INCRini['FLG_ELIG'].astype(str) == '1') & (INCRini['Cd_CONC'].astype(str).isin(['1','3'])) & (INCRini[colAGR].isin([f'1.2', f'1.3']))

        BASE_INCavl += [{
                    '(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)': INCRini.loc[Cd1, 'VL_VNR_UC'].sum(),
                    '(2) Índice de Aproveitamento Integral': INCRini.loc[Cd1, 'VL_IAI_UC'].sum(),
                    '(3) Obrigações Especiais Bruta': OEBR,
                    '(4) Bens Totalmente Depreciados': INCRini.loc[Cd1, 'VL_100DEP_UC'].sum(),
                    '(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)': 0,
                    '(6) Depreciação Acumulada': INCRini.loc[Cd1, 'VL_DAC_UC'].sum(),
                    '(7) AIS Líquido (Valor de Mercado em Uso)': INCRini.loc[Cd1, 'VL_VMU_UC'].sum(),
                    '(8) Índice de Aproveitamento Depreciado': INCRini.loc[Cd1, 'VL_IAD_UC'].sum(),
                    '(9) Valor da Base de Remuneração (VBR)': INCRini.loc[Cd1, 'VL_VBR_UC'].sum(),
                    '(10) Almoxarifado em Operação': VL_ALM,
                    '(11) Ativo Diferido': 0,
                    '(12) Obrigações Especiais Liquida': OELQ,
                    '(13) Terrenos e Servidões': INCRini.loc[Cd2, 'VL_VBR_UC'].sum(),
                  }]
        
        BASE_INCavl[-1]['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)'] = (
            BASE_INCavl[-1]['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
            BASE_INCavl[-1]['(6) Depreciação Acumulada'] -
            BASE_INCavl[-1]['(8) Índice de Aproveitamento Depreciado'] + 
            BASE_INCavl[-1]['(10) Almoxarifado em Operação'] +
            BASE_INCavl[-1]['(11) Ativo Diferido'] - 
            BASE_INCavl[-1]['(12) Obrigações Especiais Liquida'] + 
            BASE_INCavl[-1]['(13) Terrenos e Servidões']
        )
        BASE_INCavl[-1]['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = (
            BASE_INCavl[-1]['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
            BASE_INCavl[-1]['(2) Índice de Aproveitamento Integral'] -
            BASE_INCavl[-1]['(3) Obrigações Especiais Bruta'] - 
            BASE_INCavl[-1]['(4) Bens Totalmente Depreciados'])
        
        if len(df_AVL)==0:
            df_AVL = pd.DataFrame.from_dict(BASE_INCavl[-1], orient='index').reset_index()
            df_AVL.columns = ['Nm_Item', f'VL_ITEM_{LST_NM[cd-1]}_AVL']
        else:
            dfP = pd.DataFrame.from_dict(BASE_INCavl[-1], orient='index').reset_index()
            dfP.columns = ['Nm_Item', f'VL_ITEM_{LST_NM[cd-1]}_AVL']
            df_AVL = df_AVL.merge(dfP, on = 'Nm_Item', how = 'left')

        BASE_INCanl += [{
                    '(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)': INCRini.loc[Cd1, 'VL_VNR_SFF'].sum(),
                    '(2) Índice de Aproveitamento Integral': INCRini.loc[Cd1, 'VL_IAI_UC'].sum(),
                    '(3) Obrigações Especiais Bruta': OEBR,
                    '(4) Bens Totalmente Depreciados': INCRini.loc[Cd1, 'VL_100DEP_UC'].sum(),
                    '(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)': 0,
                    '(6) Depreciação Acumulada': INCRini.loc[Cd1, 'VL_DAC_UC'].sum(),
                    '(7) AIS Líquido (Valor de Mercado em Uso)': INCRini.loc[Cd1, 'VL_VMU_UC'].sum(),
                    '(8) Índice de Aproveitamento Depreciado': INCRini.loc[Cd1, 'VL_IAD_UC'].sum(),
                    '(9) Valor da Base de Remuneração (VBR)': INCRini.loc[Cd1, 'VL_VBR_UC'].sum(),
                    '(10) Almoxarifado em Operação': VL_ALM,
                    '(11) Ativo Diferido': 0,
                    '(12) Obrigações Especiais Liquida': OELQ,
                    '(13) Terrenos e Servidões': INCRini.loc[Cd2, 'VL_VBR_UC'].sum(),
                  }]
        
        BASE_INCanl[-1]['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)'] = (
            BASE_INCanl[-1]['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
            BASE_INCanl[-1]['(6) Depreciação Acumulada'] -
            BASE_INCanl[-1]['(8) Índice de Aproveitamento Depreciado'] + 
            BASE_INCanl[-1]['(10) Almoxarifado em Operação'] +
            BASE_INCanl[-1]['(11) Ativo Diferido'] - 
            BASE_INCanl[-1]['(12) Obrigações Especiais Liquida'] + 
            BASE_INCanl[-1]['(13) Terrenos e Servidões']
        )
        BASE_INCanl[-1]['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = (
            BASE_INCanl[-1]['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
            BASE_INCanl[-1]['(2) Índice de Aproveitamento Integral'] -
            BASE_INCanl[-1]['(3) Obrigações Especiais Bruta'] - 
            BASE_INCanl[-1]['(4) Bens Totalmente Depreciados'])
        
        if len(df_SFF)==0:
            df_SFF = pd.DataFrame.from_dict(BASE_INCanl[-1], orient='index').reset_index()
            df_SFF.columns = ['Nm_Item', f'VL_ITEM_{LST_NM[cd-1]}_SFF']
        else:
            dfP = pd.DataFrame.from_dict(BASE_INCanl[-1], orient='index').reset_index()
            dfP.columns = ['Nm_Item', f'VL_ITEM_{LST_NM[cd-1]}_SFF']
            df_SFF = df_SFF.merge(dfP, on = 'Nm_Item', how = 'left')

    df_AVL['VL_ITEM_TOT_AVL'] = df_AVL.iloc[:, -4:].sum(axis=1)
    df_SFF['VL_ITEM_TOT_SFF'] = df_SFF.iloc[:, -4:].sum(axis=1)
    df_TOT = df_AVL.merge(df_SFF, on = 'Nm_Item', how = 'left')
    df_TOT.to_sql("BASE_INCR_COMP", con, if_exists='replace', index=False)
    INCRini.to_sql("BASE_INCR_COMP_A1", con, if_exists='replace', index=False)

    SQLq = f"""
                SELECT 
                    t1.Cd_SubODI, 
                    (CASE WHEN t1.Cd_Tipo_OE = 3 THEN 1 ELSE 0 END) AS FLG_CCC
                FROM 
                    ROS t1 
                WHERE 
                    dt_ARQ = ?
                GROUP BY 
                    Cd_SubODI;
            """
    ROS = sql.imp_tbl_forma_001('ROS', SQLq = SQLq, con = con, st=st, Empresa=Empresa)

    INCRinia = INCRini.merge(ROS, on = 'Cd_SubODI', how = 'left')
    BASE_INCR1=INCRinia[(INCRinia['Nm_CLASS']=='BRR') & (INCRinia['FLG_ELIG']=='1') & (INCRinia['Cd_CONC']=='1') & (INCRinia['FLG_DOA_OE']=='1')][[colAGR,'VL_VOC','VL_VOC_VF_AVAL','VL_VOC_COM_AVAL','VL_VOC_CA_AVAL','VL_VOC_JOA_AVAL','VL_VNR_UC','VL_IAI_UC','VL_DAC_UC','VL_VMU_UC','VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC']]
    BASE_INCR=BASE_INCR1.groupby(colAGR, dropna = False)[['VL_VOC','VL_VOC_VF_AVAL','VL_VOC_COM_AVAL','VL_VOC_CA_AVAL','VL_VOC_JOA_AVAL','VL_VNR_UC','VL_IAI_UC','VL_DAC_UC','VL_VMU_UC','VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC']].sum().reset_index()
    BASE_INCR.to_csv(f"{dir_arq_saida}\\BASE_INCR_DEMAIS_{Cd_EMP}.csv",index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    BASE_INCR.to_sql("BASE_INCR_DEMAIS", con, if_exists='replace', index=False)
    BASE_INCR1=INCRinia[(INCRinia['Nm_CLASS']=='BRR') & (INCRinia['FLG_ELIG']=='1') & (INCRinia['Cd_CONC']=='1') & ((INCRini['FLG_INCOR_OE']=='1'))][[colAGR,'VL_VOC','VL_VOC_VF_AVAL','VL_VOC_COM_AVAL','VL_VOC_CA_AVAL','VL_VOC_JOA_AVAL','VL_VNR_UC','VL_IAI_UC','VL_DAC_UC','VL_VMU_UC','VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC']]
    BASE_INCR=BASE_INCR1.groupby(colAGR, dropna = False)[['VL_VOC','VL_VOC_VF_AVAL','VL_VOC_COM_AVAL','VL_VOC_CA_AVAL','VL_VOC_JOA_AVAL','VL_VNR_UC','VL_IAI_UC','VL_DAC_UC','VL_VMU_UC','VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC']].sum().reset_index()
    BASE_INCR.to_csv(f"{dir_arq_saida}\\BASE_INCR_IR_{Cd_EMP}.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    BASE_INCR.to_sql("BASE_INCR_IR", con, if_exists='replace', index=False)
    BASE_INCR1=INCRinia[(INCRinia['Nm_CLASS']=='BRR') & (INCRinia['FLG_ELIG']=='1') & (INCRinia['Cd_CONC']=='1') & (INCRinia['FLG_PLPT_OE']=='1')][[colAGR,'VL_VOC','VL_VOC_VF_AVAL','VL_VOC_COM_AVAL','VL_VOC_CA_AVAL','VL_VOC_JOA_AVAL','VL_VNR_UC','VL_IAI_UC','VL_DAC_UC','VL_VMU_UC','VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC']]
    BASE_INCR=BASE_INCR1.groupby(colAGR, dropna = False)[['VL_VOC','VL_VOC_VF_AVAL','VL_VOC_COM_AVAL','VL_VOC_CA_AVAL','VL_VOC_JOA_AVAL','VL_VNR_UC','VL_IAI_UC','VL_DAC_UC','VL_VMU_UC','VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC']].sum().reset_index()
    BASE_INCR.to_csv(f"{dir_arq_saida}\\BASE_INCR_PLPT_{Cd_EMP}.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    BASE_INCR.to_sql("BASE_INCR_PLPT", con, if_exists='replace', index=False)
    BASE_INCR1=INCRinia[(INCRinia['Nm_CLASS']=='BRR') & (INCRinia['FLG_ELIG']=='1') & (INCRinia['Cd_CONC']=='1') & (INCRinia['FLG_CCC']=='1')][[colAGR,'VL_VOC','VL_VOC_VF_AVAL','VL_VOC_COM_AVAL','VL_VOC_CA_AVAL','VL_VOC_JOA_AVAL','VL_VNR_UC','VL_IAI_UC','VL_DAC_UC','VL_VMU_UC','VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC']]
    BASE_INCR=BASE_INCR1.groupby([colAGR], dropna = False)[['VL_VOC','VL_VOC_VF_AVAL','VL_VOC_COM_AVAL','VL_VOC_CA_AVAL','VL_VOC_JOA_AVAL','VL_VNR_UC','VL_IAI_UC','VL_DAC_UC','VL_VMU_UC','VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC']].sum().reset_index()
    BASE_INCR.to_csv(f"{dir_arq_saida}\\BASE_INCR_CCC_{Cd_EMP}.csv",index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    BASE_INCR.to_sql("BASE_INCR_CCC", con, if_exists='replace', index=False)
    
    if st: 
        avl.progress(90, text = 'Salvando dados processados...')
        for nm_arq_art in [f'BASE_INCR_DEMAIS_{Cd_EMP}.csv',f'BASE_INCR_IR_{Cd_EMP}.csv',
                           f'BASE_INCR_PLPT_{Cd_EMP}.csv',f'BASE_INCR_CCC_{Cd_EMP}.csv']:
            registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf"{dir_arq_saida}\\{nm_arq_art}",
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)

    INCRini.to_sql("ANL_INCREMENTAL", con, if_exists='replace', index=False)
    BASE_BPR.to_sql("ANL_LIMITES_VOC", con, if_exists='replace', index=False)
    ALMOX.to_sql("ANL_ALMOX", con, if_exists='replace', index=False)
    VL_MENSAL.to_sql("ANL_VL_MENSAL", con, if_exists='replace', index=False)

    if st: avl.progress(95, text = 'Resumindo alertas...')

    # ============================================================================================
    # Teste de condutores mínimos
    # ============================================================================================
    SQLq = f"""
                SELECT 
                    t1.Nm_Variavel, 
                    MIN(CAST(t1.QTD_NORM AS REAL)) AS QTD_NORM
                FROM 
                    NT_COM t1 
                WHERE 
                    t1.dt_ARQ = ?
                GROUP BY 
                    t1.Nm_Variavel;
            """
    NT_COM = sql.imp_tbl_forma_001('NT_COM', SQLq = SQLq, con = con, st=st, Empresa=Empresa)

    SQLq = f"""
                SELECT 
                    t1.COD_ITEM, 
                    t1.Nr_FC
                FROM 
                    LST_MAT t1 
                WHERE 
                    t1.dt_ARQ = ?
                GROUP BY 
                    t1.COD_ITEM;
            """
    LST_MAT = sql.imp_tbl_forma_001('LST_MAT', SQLq = SQLq, con = con, st=st, Empresa=Empresa)

    SQLq = f"""
                SELECT 
                    t1.Cd_SubODI, 
                    COALESCE(CAST(t1.Nr_Fases AS REAL), 1) Nr_Fases
                FROM 
                    ROS t1 
                WHERE 
                    t1.dt_ARQ = ?
                GROUP BY 
                    t1.Cd_SubODI;
            """
    ROS = sql.imp_tbl_forma_001('ROS', SQLq = SQLq, con = con, st=st, Empresa=Empresa)

    try:
        var = ["VL_VAO_MIN_RAR", "VL_VAO_MIN_RAU", "VL_RAM_MIN_RAR", "VL_RAM_MIN_RAU"]
        var_norm = (
                        NT_COM.loc[NT_COM['Nm_Variavel'].isin(var), ['Nm_Variavel', 'QTD_NORM']]
                        .set_index('Nm_Variavel')['QTD_NORM']
                   )
        VAO_RUR = var_norm.get("VL_VAO_MIN_RAR", 5.0)
        VAO_URB = var_norm.get("VL_VAO_MIN_RAU", 5.0)
        VAO_RAM_RUR = var_norm.get("VL_RAM_MIN_RAR", 2.0)
        VAO_RAM_URB = var_norm.get("VL_RAM_MIN_RAU", 2.0)
    except:
        VAO_RUR = 5
        VAO_URB = 5
        VAO_RAM_RUR = 2
        VAO_RAM_URB = 2

    tst_cnd = (
                        (INCRini['FLG_ELIG'] == '1') &
                        (INCRini['Cd_CONC'] == '1') &
                        (INCRini['Nr_TUC'] == '190') &
                        (INCRini['Nr_A1'].astype(str).str[-1:].isin(['1', '2'])) &
                        (INCRini['Cd_UAR'] != 'UAR')
                    )

    if st: avl.progress(97, text = 'Testando condutores...')
    TST_CND = INCRini.loc[tst_cnd, ['Id_SEQ_INC', 'Cd_SubODI', 'Nr_TI', 'COD_ITEM', 
                                    'Txt_DESC_TECN', 'Qtd_AIS', 'Cd_UND_AIS', 'Nr_A4']].copy()
    
    TST_CND = TST_CND.merge(LST_MAT, how = 'left', on = 'COD_ITEM')
    TST_CND['Nr_FC'] = (
                            TST_CND['Nr_FC']
                            .astype(str)
                            .replace(['None', 'nan', 'NaN'], None) 
                            .str.replace(",", ".")
                            .astype(float)
                            .fillna(1)
                        )
    TST_CND.loc[TST_CND['Nr_FC']==0, 'Nr_FC'] = 1
    TST_CND = TST_CND.merge(ROS, how = 'left', on = 'Cd_SubODI')
    LST_ATR_CABOS = [str(i) for i in range(57,100)] + ['05','07','09','5','7','9','19']
    TST_CND.loc[TST_CND['Nr_A4'].astype(str).isin(LST_ATR_CABOS),'Nr_Fases'] = 1
    TST_CND['Qtd'] = (TST_CND['Qtd_AIS'] / TST_CND['Nr_FC']) / TST_CND['Nr_Fases'].fillna(1)
    df_AX = TST_CND.groupby(['Cd_SubODI', 'COD_ITEM'], dropna=False)['Qtd'].sum().reset_index().rename(columns={'Qtd':'Qtd_PROJ'})
    TST_CND = TST_CND.merge(df_AX, how='left', on =['Cd_SubODI', 'COD_ITEM'])

    TST_CND['OBS_FISC'] = 'NO'
    msg_erro = 'Valor do vão estimado menor do que o mínimo apresentado. Justificar.'
    TST_CND.loc[(TST_CND['Nr_TI'] == '40') & (TST_CND['Qtd_PROJ'] < VAO_URB), 'OBS_FISC'] = msg_erro
    TST_CND.loc[(TST_CND['Nr_TI'] == '41') & (TST_CND['Qtd_PROJ'] < VAO_RUR), 'OBS_FISC'] = msg_erro
    TST_CND.loc[(TST_CND['Nr_TI'] == '93') & (TST_CND['Qtd_PROJ'] < VAO_RAM_URB), 'OBS_FISC'] = msg_erro
    TST_CND.loc[(TST_CND['Nr_TI'] == '96') & (TST_CND['Qtd_PROJ'] < VAO_RAM_RUR), 'OBS_FISC'] = msg_erro
    TST_CND.to_sql("TST_VAO_MIN_INCR", con, if_exists='replace', index=False)

    TST_CND.to_csv(f"{dir_arq_saida}\\TST_CONDUTORES_MIN_{Cd_EMP}.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf"{dir_arq_saida}\\TST_CONDUTORES_MIN_{Cd_EMP}.csv",
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    # ============================================================================================
    # Teste de medicao indireta
    # ============================================================================================
    if st: avl.progress(97, text = 'Testando medicao indireta...')
    LST_UC = ['190','295','575']
    TST_MED = INCRini[(INCRini['FLG_ELIG'] == '1') & (INCRini['Cd_CONC'] == '1') & 
                      (INCRini['Nr_TI'].isin(['93','96']))
            ][['Id_SEQ_INC','Cd_SubODI','Nr_TUC','COD_ITEM','Txt_DESC_TECN','Qtd_AIS',
               'Cd_UND_AIS','Cd_UAR']]
    TST_MED.columns = ['Id_SEQ_INC','Cd_SubODI','Nr_TUC','COD_ITEM','Txt_DESC_TECN','Qtd_AIS','Cd_UND_AIS','Cd_UAR']
    TST_MED['OBS_FISC'] = 'NO'
    TST_MED.loc[(~(TST_MED['Nr_TUC'].isin(LST_UC))),'OBS_FISC'] = 'Justificar a inclusão desta UC em medição.'
    TST_MED.loc[(TST_MED['Nr_TUC'] == '575') & (TST_MED['Cd_UAR'] == 'UAR'), 'OBS_FISC'] = 'Identificar a UC pai.'
    TST_MED.to_sql("TST_MED_INCR", con, if_exists='replace', index=False)
    TST_MED.to_csv(f"{dir_arq_saida}\\TST_MEDIDORES_{Cd_EMP}.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf"{dir_arq_saida}\\TST_MEDIDORES_{Cd_EMP}.csv",
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    regras_alertas = [

        (
            (INCRini['Cd_TP_AVAL'].astype(str) == '1')  
            & (INCRini['VL_VF'] > 0)
            & (INCRini['VL_COM'] > 0)
            & (INCRini['VL_CA'] > 0)
            & (INCRini['FLG_DOA_OE'].astype(str) == '0')
            & (INCRini['FLG_INCOR_OE'].astype(str) == '0')
            & (INCRini['FLG_PLPT_OE'].astype(str) == '0')
            & (INCRini['FLG_OAT'].astype(str) == '0')
            & (INCRini['FLG_ELIG'].astype(str) == '1')
            & (INCRini['FLG_REG'].astype(str) == '1')
            & (INCRini['Cd_CONC'].astype(str).isin(['1','3'])),
            'Explicar porque não foi empregado o BPR para avaliação.'
        ),


        (
            (INCRini['Nm_ATVD'] == 'Geração')  
            & (~INCRini['Nr_TI'].isin(['10','11','12','13','14','15','16','17','18','19',
                                       10,11,12,13,14,15,16,17,18,19])),
            'Explicar porque há ativos da conta contábil de atividade geração, nesta TI.'
        ),
        (
            (INCRini['VL_VOC_JOA'] != 0) | 
            ((INCRini['VL_VNR_JOA'] == 0) & (~INCRini['Nr_TI'].isin(['10','11','12','13','14','15','16','17',
            '18','19','20','21','22','23','24','25','26','27','28','29','70','71','72','80','81','82',
            '90','91','92','93','94','95','96','97','98','99',10,11,12,13,14,15,16,17,
             18,19,20,21,22,23,24,25,26,27,28,29,70,71,72,80,81,82,90,91,92,93,94,95,96,97,98,99]))),
            'Explicar porque avaliadora não apresentou JOA na coluna VL_VNR_JOA.'
        ),
        ( (INCRini['Nr_TUC'].isin(['535',535]) & (INCRini['Nr_IPCA_REF_IMB'] * 5000 / 3403.73 > INCRini['VL_VOC']/INCRini['Qtd_AIS'])) & INCRini['FLG_ELIG'].isin(['1',1]),
         'Inelígivel por ser inferior a R$ 5.000, atualizados pelo IPCA na data de imobilização.'

        ),
        ( (INCRini['Cd_TP_AVAL'].isin(['2',2,'3',3]) & (INCRini['FLG_OAT'].isin(['1',1]))),
         'Está como valoração por BPR/BPC e como atípica, um dos dados é inconsistente.'

        ),
        ( (INCRini['Nr_TUC'].isin(['235',235,'230',230]) & (1200 > INCRini['VL_VOC']/INCRini['Qtd_AIS'])) & INCRini['FLG_ELIG'].isin(['1',1]),
         'Inelígivel por ser inferior a R$ 1.200, conforme MCPSE e Lei 12.973/2014, art. 15.'

        ),
        (
            (((INCRini['VL_VOC_VF_AVAL']+INCRini['VL_VOC_COM_AVAL']+INCRini['VL_VOC_CA_AVAL']+
              INCRini['VL_VOC_JOA_AVAL']) * INCRini['FA_IPCA'] / INCRini['VL_VNR_UC']) > 1.2)
              & (INCRini['Cd_TP_AVAL'] == '2'),
            'Explicar porque o VOC atualizado, pelo IPCA, está acima de 20% do VNR (variação de CA ou de COM em relação ao BPR e do banco de compras).'
        ),
        (
            (((INCRini['VL_VOC_VF_AVAL']+INCRini['VL_VOC_COM_AVAL']+INCRini['VL_VOC_CA_AVAL']+
              INCRini['VL_VOC_JOA_AVAL']) * INCRini['FA_IPCA'] / INCRini['VL_VNR_UC']) < 0.8)
              & (INCRini['Cd_TP_AVAL'] == '2'),
            'Explicar porque o VOC atualizado, pelo IPCA, está abaixo de 20% do VNR (variação de CA ou de COM em relação ao BPR e do banco de compras).'
        ),
        (
            ((INCRini['VL_VOCsjoa_IMB_AT'] >= 0) | 
            ((INCRini['VL_VOC_COM_AVAL'] == 0) & (INCRini['VL_VOC_CA_AVAL'] == 0))) & 
            INCRini['Nr_TI'].isin([380,385,390,400,405,420,425,430,435,
            440,445,450,455,465,470,475,490,500,505,510,515,525,530,355,360,365,370,615,
            610,'380','385','390','400','405','420','425','430','435','440','445','450',
            '455','465','470','475','490','500','505','510','515','525','530','355','360',
            '365','370','615','610']),
            'Explicar porque não foi feita abertura do VOC.'
        ),
        (
            (INCRini['MTD_AVAL'] == 'BPC') & (INCRini['Cd_TP_AVAL'] != '3'),
            'Por que não foi empregado BPC?'
        ),
        (
            (INCRini['MTD_AVAL'] != 'BPR') & (INCRini['Cd_TP_AVAL'] == '2') & 
            (INCRini['Cd_SISBASE_SFF'].isin(['', 0, 'ND']) | INCRini['Cd_SISBASE_SFF'].isnull()),
            'Explicar como foi aplicado o BPR se não foi identificado Cd_SISBASE pela SFF.'
        ),
        (
            (INCRini['Cd_TP_AVAL'].isin(['3', '2'])) & 
            (INCRini['VL_VF'].isin(['', 0, 'ND']) | INCRini['VL_VF'].isnull()),
            'Explicar como foi aplicado o BPR/BPC se não foi identificado VF no arquivo BP_UAR pela SFF.'
        ),
        (
            (INCRini['Cd_TP_AVAL'].isin(['3', '2'])) & 
            (INCRini['COD_ITEM'].isin(['', 0, 'ND']) | INCRini['COD_ITEM'].isnull()),
            'Explicar como foi aplicado o BPR/BPC se não foi identificado COD_ITEM pela SFF.'
        ),
        (
            (INCRini['MTD_AVAL'] != 'BPR') & (INCRini['Cd_TP_AVAL'] == '2') & 
            (INCRini['VL_VF'].isin([0, 'ND']) | INCRini['VL_VF'].isnull()),
            'Explicar como foi aplicado o BPR se não foi identificado o VF do item na tabela (ou o COD_ITEM está faltando) pela SFF.'
        ),
        (
            (INCRini['MTD_AVAL'] == 'BPC') & (INCRini['VL_BPRC_TOT'] == 0),
            'Verifique ou declare código de item, embora BPC, usado A'
        ),
        (
            (INCRini['TST_VF_ROA_AVL'] == 'DIFERE') & (INCRini['Cd_TP_AVAL'] == '1'),
            'Justificar porque o VF do VOC da avaliadora difere do valor do ROA'
        ),
        (
            (INCRini['TP_BEM'].astype(str) != '4') & ((INCRini['Nm_CLASS'] == 'BAR')),
            'Justificar porque não seria BAR, TP_BEM está diferente de 4 e conta contábil é de BAR.'
        ),
        (
            (INCRini['TESTE_ORC'] != 'OK'),
            'Justificar variação entre o valor do orçamento e o VOC'
        ),
        (
            (INCRini['DT_APL'].isnull()) & (INCRini['Cd_TP_AVAL'] == '2'),
            'Justificar porque aplicou BPR em período não coberto pelos bancos'
        ),
        (
            INCRini['Nr_TUC'].isin(['190',190]) & INCRini['Nr_A1'].isin(['2', 2, 1, '1']) &
            (INCRini['Nr_A4'].isin(['36', '37', 36, 37])) & INCRini['FLG_ELIG'].isin(['1',1]),
            'Justificar o uso de condutores de bitola 1,5 ou 2,5mm2, indicar também porque seria unitizado'
        ),
        (
            (INCRini['Nr_TI'].notnull()) & 
            (~INCRini['TESTE_Cd'].isin(['ND', 'OK'])) & 
            (INCRini['Cd_UAR'] != 'UAR') & 
            (INCRini['Cd_TP_AVAL'] == '2') & 
            (INCRini['MTD_AVAL'] == 'BPR'),
            'Justificar na aba Teste_CdSisbase a divergência no Cd_Sisbase'
        ),
        (
            (INCRini['Cd_TP_AVAL'].isin(['2', '3'])) & 
            ((abs(INCRini['VL_VNR_VF_UNIT'] - INCRini['VL_VF']) / INCRini['VL_VNR_VF_UNIT']) > 0.05),
            'Justificar porque o VF está diferente entre arquivo BP_UAR e INCR'
        ),
        (
            (INCRini['MTD_AVAL'] == 'ORC') & 
            (INCRini['Cd_TP_AVAL'] != '4') & 
            ((INCRini['FA_IPCA'] * INCRini['VL_VOC']) < INCRini['VL_VNR_UC']),
            'Justificar porque não foi orçado'
        ),
        (
            INCRini['Nr_TI'].isnull() &
            (INCRini['FLG_ELIG'].astype(str) == '1') &
            (INCRini['Cd_CONC'].astype(str).isin(['1','3'])),
            'Justificar a inexistência de código de TI'
        ),
        (
            (INCRini['Dt_Imob'] > INCRini['DT_LIM_UNIT']) & 
            (INCRini['Dt_Imob'] == INCRini['Dt_CNTB_AJST']),
            'Data contábil ajustada não deve ser igual a de imobilização'
        ),
        (
            (INCRini['Cd_TP_AVAL'] == '2') & (INCRini['Cd_UAR'] == 'UAR'),
            'Verifique a classificação Cd_TP_AVAL ou Cd_UAR, estão inconsistentes'
        ),
        (
            (INCRini['CT_AJUSTE'] != 0),
            'Verificar o critério de depreciação ou as taxas aplicadas'
        ),
        (
            (INCRini['TESTE_ORC'] != 'OK'),
            'Verificar a variação da obra orçada em relação ao VOC atualizado'
        ),
        (
            (INCRini['TST_JOA'] != 'OK') & (INCRini['Cd_TP_AVAL'] != '1') & 
            (INCRini['VL_VOC_JOA_AVAL'] != 0),
            'Verificar se o JOA apropriado pela avaliadora foi limitado'
        ),
        (
            (INCRini['TST_JOA'] != 'OK') & (INCRini['Cd_TP_AVAL'] != '1') & 
            (INCRini['VL_VNR_JOA'] != 0) & (INCRini['Nr_TI'].astype(str).isin(['10','11','12','13','14','15','16','17',
            '18','19','20','21','22','23','24','25','26','27','28','29','70','71','72','80','81','82',
            '90','91','92','93','94','95','96','97','98','99'])),
            'TI não deve ter JOA, verificar se o valor apropriado pela avaliadora foi zerado'
        )

    ]  

    tis_bar = [
                    '70', '71', '72',
                    '80', '81', '82',
                    '90', '91', '94', '95', '97', '99'
                ]
    mask_ti = INCRini['Nr_TI'].isin(tis_bar)
    mask_tp_bem = INCRini['TP_BEM'].astype(str).eq('4')
    if 'Cd_Q5' in INCRini.columns:
        mask_bar = INCRini['Cd_Q5'].astype(str).isin(['4.2', '5.2'])
    else:
        mask_bar = INCRini['Nm_CLASS'].eq('BRR')

    regras_alertas.append((
                                mask_ti & mask_bar,
                                'Verificar se ativo pode ser BAR, pela TI'
                            ))

    regras_alertas.append((
                            mask_tp_bem & mask_bar,
                            'Verificar se ativo pode ser BAR, marcação do TP_BEM'
                        ))         


    if st: avl.progress(98, text = 'Validando regras...')
    for Cd, msg in regras_alertas:
        INCRini.loc[Cd, 'OBS_FISC'] = msg
        txtALERTAS = tst_ALT(txtALERTAS, INCRini, msg)

    TBL_TUC = pd.read_csv("tabelas/TBL_TUC.csv", sep="|", decimal=',',
                          on_bad_lines='skip', encoding="Latin-1", dtype=str);
    TBL_TUC.fillna('ND', inplace = True)

    dic_TUC = {
                    row['Ide_TUC']: row['PLV_CHV'].split(',')
                    for _, row in TBL_TUC.dropna(subset=['PLV_CHV']).iterrows()
               }

    if st: avl.progress(98, text = 'Verificando UC/UAR...')
    msg = 'Verificar se o código UC é compatível com descrição'
    for UC, LST_ITENS in dic_TUC.items():
        if any(len(item) > 3 for item in LST_ITENS):
             BUSCA =  f"(?i){'|'.join([re.escape(item) for item in LST_ITENS])}"
             INCRini.loc[(
                        ~(INCRini['Txt_DESC_TECN'].str.contains(BUSCA, na=False, regex=True)) &
                        (INCRini['Nr_TUC'] == UC) &
                        (INCRini['Cd_CONC'] != '2')), 'OBS_FISC'] = msg

    txtALERTAS = tst_ALT(txtALERTAS, INCRini, msg)

    LST_UAR = ['relé', 'rele', 'retificador', 'concentrador', 'cobertura', 'switch', 'baterias', 'conversor', 'serv',
            'servicos', 'serviços', 'transmissor de dados', 'utr', 'unidade de terminal', 'unidade terminal',
            'supervisor', 'voltimetro', 'voltímetro', 'cobertura', 'telhado', 'remota', 'rf', 'computador',
            'pc', 'microcomputador', 'janela', 'cj de buchas', 'sincronizador', 'mostrador remoto', 'mostrador',
            'nobreak', 'modem', 'mesh', 'conversor dc/dc', 'ethernet', 'amplificador', 'gprs', 'detector de falta',
            'detector', 'roteador', 'monitor', 'teclado', 'terminal', 'trocador', 'transceptor', 'gerador',
            'no break', 'indicadores', 'cpu', 'relê', 'relè']
    BUSCA =  f"(?i){'|'.join([re.escape(item) for item in LST_UAR])}"
    INCRini['TESTE_UAR'] = INCRini['Txt_DESC_TECN'].str.contains(BUSCA)

    arq_prob = rf"{dir_arq_saida}/modelo_uc.pkl"
    arq_prob1 = rf"{dir_arq_saida}/vetor_uc.pkl"

    @st.cache_resource
    def carregar_modelo(caminho):
        with open(caminho, 'rb') as f:
            return joblib.load(caminho)
        
    if os.path.exists(arq_prob) & os.path.exists(arq_prob1):
        modelo = carregar_modelo(arq_prob)
        vetor = carregar_modelo(arq_prob1)
    else:
        tipos = {
                    "Txt_DESC_TECN": str, 
                    "FLG_UC": bool
                }

        df_treino = pd.read_csv(
                                    "tabelas/bsd_dd_treinamento.csv", 
                                    sep="|", 
                                    decimal=',',
                                    on_bad_lines='skip', 
                                    encoding="Latin-1", 
                                    dtype=tipos
                                )
        X = df_treino['Txt_DESC_TECN'].fillna('')
        y = df_treino['FLG_UC']

        vetor = TfidfVectorizer(ngram_range=(1,2))
        X_vet = vetor.fit_transform(X)
        modelo = LogisticRegression()
        modelo.fit(X_vet, y)

        joblib.dump(modelo, 'modelo_uc.pkl')
        joblib.dump(vetor, 'vetor_uc.pkl')    

    df_unico = INCRini[['Txt_DESC_TECN']].drop_duplicates().copy()
    X_anl = df_unico['Txt_DESC_TECN'].fillna('')
    X_vet_anl = vetor.transform(X_anl)
    df_unico['PROB_UC'] = modelo.predict_proba(X_vet_anl)[:,1]
    df_unico['CLASS_UC'] = (df_unico['PROB_UC'] > 0.5).astype(int)

    INCRini = INCRini.merge(df_unico, on='Txt_DESC_TECN', how='left')
    if st: avl.progress(98, text = 'Verificando UC/UAR, machine learning...')
    msg = 'Verificar se é UAR, algoritmo ML'
    INCRini.loc[((INCRini['TESTE_UAR'] == True) & (INCRini['Cd_UAR'] != 'UAR')) |
                ((INCRini['Cd_UAR'] != 'UAR') & (INCRini['CLASS_UC'] == 0)),
                'OBS_FISC'] = msg
    txtALERTAS = tst_ALT(txtALERTAS, INCRini, msg)

    LST_BPR = ['BCS', 'CHS', 'CCO', 'CFR', 'DSJ', 'LUM', 'PRS', 'PRR', 'REA', 'RGS', 'RLS', 'TRA', 'TSA', 
            'CDL', 'PST', 'TRF', 'TMS', 'MRD', 'CDR', 'TRD', 'BNC', 'CHV', 'REG', 'REL']
    msg = 'Verificar o Cd_SISBASE ou Cd_TP_AVAL'
    INCRini['TESTE_BPR_VAL'] = INCRini['Cd_SISBASE'].str.startswith(tuple(LST_BPR))
    INCRini.loc[((INCRini['TESTE_BPR_VAL'] == False) & (INCRini['Cd_TP_AVAL'] == '2')),
                'OBS_FISC'] = msg
    txtALERTAS = tst_ALT(txtALERTAS, INCRini, msg)

    LST_BAR = ['adm', 'administrativo','gerência','regional','regionais','almoxarifado','almox','deposito','depos','estacio',
            'estacionamento','móvel','mobilia','escritório','escr','oficina','lab','laboratório','labor','laboratorio',
            'operação','operacao','gis','scada','software','programa','microsoft','erp','oracle','sap','gestão','comercial',
            'financeiro','empresarial','teleatendimento','microcomputador','alicate','multimetro','multímetro','terrometro',
            'fenda','talha','densímetro','fasímetro','aferidor','serra','moto','licença', 'monitor', 'impressora', 'notebook', 'hd externo',
            'no-break', 'projetor', 'totem', 'tv', 'informática', 'osciloscópio', 'empilhadeira', 'esmeril', 'balança', 'rádio', 'celular', 'mesa',
            'cadeira', 'armário', 'balcão', 'gaveteiro', 'geladeira', 'máquina de gelo']
    msg = 'Verificar se ativo pode ser BAR'
    BUSCA =  f"(?i){'|'.join([re.escape(item) for item in LST_BAR])}"
    INCRini['TESTE_BAR_VAL'] = INCRini['Cd_SISBASE'].str.contains(BUSCA)
    INCRini.loc[((INCRini['TESTE_BAR_VAL'] == True) & (INCRini['Nm_CLASS'] == 'BRR')),
                'OBS_FISC'] = msg
    txtALERTAS = tst_ALT(txtALERTAS, INCRini, msg)
    lst_EXC = ['DOAÇÃO, TESTE NÃO SE APLICA','NO','INCORPORAÇÃO, TESTE NÃO SE APLICA']
    txtALERTAS[~txtALERTAS['OBS_FISC'].isin(lst_EXC)].to_csv(f"{dir_arq_saida}\\BASE_INCR_ALERTAS_{Cd_EMP}.csv", index=False, sep="|", decimal=',', encoding="Latin-1", header = True)
    txtALERTAS[~txtALERTAS['OBS_FISC'].isin(lst_EXC)].to_sql('TST_ALERTAS_INCR', con, if_exists='replace', index = False)

    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf"{dir_arq_saida}\\BASE_INCR_ALERTAS_{Cd_EMP}.csv",
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        avl.progress(100, text = 'Finalizado!')

    return "OK"

def tbl_JOA(dire, bd, empresa, ano, st=None, RTE=False, Dt_INI = None, Dt_FIM = None):

    local = f"{dire}".replace("INC_ANLS","BD_LOCAL")
    TX_DES = pd.read_csv("tabelas/tbl_desembolso_JOA.csv", sep="|",decimal=',',
                         on_bad_lines='skip',encoding="Latin-1");
    TX_DES = TX_DES.fillna(0)
    TX_DES['N'] = 1
    TX_DES['N'] = TX_DES['N'].cumsum()
    LST_TX_DES = ['RDA_123','RDS_123','LD_123','SE_123','RDA_45','RDS_45','LD_45','SE_45']
    con = False
    if not RTE:
        con = sl.connect(f'{local}\EFD_ICMS_{empresa}_{ano}.db')
        tabelas = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", con=con)
        tabelas = tabelas['name'].tolist()
        cnpjs = [t.split('_')[-1] for t in tabelas if t.startswith('BLF_G110_')]
        cnpjs = sorted(set(cnpjs))

        tbl_icms_fin = {}
        if sql.existe_tabela(f"tbl_icms_fin_{cnpjs[0]}", con):
            for i, cnpj in enumerate(cnpjs):
                SQLq = f"""
                            SELECT *
                            FROM tbl_icms_fin_{cnpj} t1 
                    """
                tbl_icms_fin[i] = pd.read_sql(SQLq, con)
        else:
            if st:
                st.error('Falha ao importar o arquivo tbl_icms_fin da base local.')
                return None
            else:
                raise UserWarning('Falha ao importar o arquivo tbl_icms_fin da base local.')
    
        if len(cnpjs) == 1:
            TX_DES['WACCp'] = tbl_icms_fin[0].iloc[0,1]/100
        else:
            v1 = 0
            for i1, cnpj in enumerate(cnpjs):
                v2 = tbl_icms_fin[i1].iloc[2, 1]
                if v1 < v2:
                    v1 = v2
                    TX_DES['WACCp'] = tbl_icms_fin[i1].iloc[0,1]/100
            #raise Exception("Você deve ajustar para o valor da empresa resultante, pós-fusão.")
    else:
        tbl_wacc = pd.read_csv('tabelas/tbl_WACC.csv', sep='|', encoding='Latin-1')
        tbl_wacc['DT_VIG'] = pd.to_datetime(tbl_wacc['DT_VIG'].str.replace('/', ''), format='%Y%m%d')
        tbl_wacc['Vl_WACC_REAL'] = pd.to_numeric(tbl_wacc['Vl_WACC_REAL'], errors='coerce')
        meses = pd.date_range(Dt_INI, Dt_FIM, freq='MS', name='DT_VIG')
        tbl_wacc_mes = pd.DataFrame(meses)
        tbl_wacc_mes = tbl_wacc_mes.merge(tbl_wacc, how='left', on='DT_VIG')
        tbl_wacc_mes=tbl_wacc_mes.drop(tbl_wacc_mes.columns[[2,3]], axis=1)
        tbl_wacc_mes.loc[0,'Vl_WACC_REAL'] = tbl_wacc[tbl_wacc['DT_VIG']<=tbl_wacc_mes['DT_VIG'][0]]['Vl_WACC_REAL'].iloc[-1]
        tbl_wacc_mes['Vl_WACC_REAL']=tbl_wacc_mes['Vl_WACC_REAL'].ffill() 
        tbl_wacc_mes.columns=['DT_INI','Tx_WACC']
        if not tbl_wacc_mes.empty and 'Tx_WACC' in tbl_wacc_mes:
            TX_DES['WACCp'] = tbl_wacc_mes['Tx_WACC'].mean()
        else:
            TX_DES['WACCp'] = np.nan

    for i in LST_TX_DES:
            N = TX_DES[TX_DES[i] > 0].shape[0]
            TX_DES[f'{i}_FLX']=((1+TX_DES['WACCp'])**((N+1-TX_DES['N'])/12)-1)*TX_DES[i]/100
            TX_DES.loc[TX_DES[f'{i}_FLX']<=0, f'{i}_FLX'] = 0

    TX_DES.loc['Total']=TX_DES.sum()
    TX_DES.loc['Total', ['IND_DES', 'N', 'WACCp']] = '', '', ''
 

    TX_DES.to_sql("TX_DES", bd, if_exists='replace', index=False)

    TX_JOA_APL = TX_DES.loc[TX_DES.index[-1], ['RDA_123_FLX','RDS_123_FLX','LD_123_FLX','SE_123_FLX','RDA_45_FLX','RDS_45_FLX','LD_45_FLX','SE_45_FLX']].reset_index()
    TX_JOA_APL.columns = ['TP_JOA','Tx_JOA']
    TX_JOA_APL['TP_JOA'] = TX_JOA_APL['TP_JOA'].str.replace("_FLX","",regex=True)

    return TX_JOA_APL

def tst_cod_sisbase(LST_TUC, D2, st=None):
    LST_TUC['Cd_SISBASE_SFF']='ND'
    lst=['Nr_TI','Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6']
    for c in lst:
        if LST_TUC[c].dtype == 'object':
            LST_TUC[f"{c}_x"] = pd.to_numeric(LST_TUC[c].str.replace(',','.'),errors='coerce')
        else:
            LST_TUC[f"{c}_x"] = LST_TUC[c]
            LST_TUC[c] = LST_TUC[c]
    
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_A4_x>3) & (LST_TUC.Nr_A4_x<26) & (LST_TUC.Nr_TI_x>29) & 
                (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='BCS301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_A4_x>27) & (LST_TUC.Nr_A4_x<50) & (LST_TUC.Nr_TI_x>29) & 
                (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='BCS302'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_A4_x>50) & (LST_TUC.Nr_A4_x<60) & (LST_TUC.Nr_TI_x>29) & 
                (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='BCS303'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_A4_x>69) & (LST_TUC.Nr_A4_x<75) & (LST_TUC.Nr_TI_x>29) & 
                (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='BCS304'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_A4_x==75) & (LST_TUC.Nr_TI_x>29) & 
                (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='BCS305'
    #Banco de capacitores em paralelo, SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_A4_x>3) & (LST_TUC.Nr_A4_x<26) & (LST_TUC.Nr_TI_x>49) & 
                (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='BCS306'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_A4_x>27) & (LST_TUC.Nr_A4_x<50) & (LST_TUC.Nr_TI_x>49) & 
                (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='BCS307'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_A4_x>50) & (LST_TUC.Nr_A4_x<60) & (LST_TUC.Nr_TI_x>49) & 
                (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='BCS308'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_A4_x>69) & (LST_TUC.Nr_A4_x<75) & (LST_TUC.Nr_TI_x>49) & 
                (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='BCS309'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_A4_x==75) & (LST_TUC.Nr_TI_x>49) &
                (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='BCS310'
    #Banco de capacitores em paralelo, RAU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='BNC101'
    #Banco de capacitores em paralelo, RAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='BNC111'
    #Banco de capacitores em paralelo, LAU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_TI_x>34) & (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='BNC201'
    #Banco de capacitores em paralelo, LAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==125) & (LST_TUC.Nr_TI_x>57) & (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='BNC202'
    #Chaves, SDU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>39) & (LST_TUC.Nr_A3_x<90) & 
                (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CHS301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<38) & 
                (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CHS302'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>39) & (LST_TUC.Nr_A3_x<90) & 
                (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CHS303'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<38) & 
                (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CHS304'
    #Chaves, SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>39) & (LST_TUC.Nr_A3_x<90) & 
                (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CHS305'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<38) & 
                (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CHS306'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>39) & (LST_TUC.Nr_A3_x<90) & 
                (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CHS307'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<38) & 
                (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CHS308'
    #Chaves, RAU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (((LST_TUC.Nr_A1_x>0) & (LST_TUC.Nr_A1_x<7)) |
                                        ((LST_TUC.Nr_A1_x>11) & (LST_TUC.Nr_A1_x<21))) & 
                (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='CHV101'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='CHV102'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A1_x==10) & (LST_TUC.Nr_A4_x!=1) & 
                (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='CHV103'
    #Chaves, RAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (((LST_TUC.Nr_A1_x>0) & (LST_TUC.Nr_A1_x<7)) |
                                        ((LST_TUC.Nr_A1_x>11) & (LST_TUC.Nr_A1_x<21))) & 
                (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='CHV111'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='CHV112'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A1_x==10) & (LST_TUC.Nr_A4_x!=1) & 
                (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='CHV113'
    #Chaves, LAU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>39) & (LST_TUC.Nr_A3_x<91) & 
                (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x>34) & (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CHV201'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<38) & 
                (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x>34) & (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CHV202'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>27) & (LST_TUC.Nr_A3_x<91) & 
                (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x>34) & (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CHV203'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<26) & 
                (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x>34) & (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CHV204'
    #Chaves, LAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>39) & (LST_TUC.Nr_A3_x<61) & 
                (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x>57) & (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CHV205'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<38) & 
                (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x>57) & (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CHV206'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>27) & (LST_TUC.Nr_A3_x<91) & 
                (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x>57) & (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CHV207'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==160) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<26) & 
                (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x>57) & (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CHV208'
    #Condutor, SDU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>29) & 
                (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CDL301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (((LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & 
                (LST_TUC.Nr_A2_x<11))) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CDL302'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>4) & 
                (LST_TUC.Nr_A2_x<9) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CDL303'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CDL304'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (((LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & (LST_TUC.Nr_A2_x<11))) & 
                (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CDL305'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>4) & 
                (LST_TUC.Nr_A2_x<8) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CDL306'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>1) & (LST_TUC.Nr_A5_x<5) & 
                (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CDL307'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<11) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>1) & 
                (LST_TUC.Nr_A5_x<5) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CDL308'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x>1) & 
                (LST_TUC.Nr_A5_x<5) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CDL309'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x>1) & (LST_TUC.Nr_A5_x<5) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CDL310'
    #Condutor, SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>49) & 
                (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CDL311'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (((LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & 
                (LST_TUC.Nr_A2_x<11))) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CDL312'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>4) & 
                (LST_TUC.Nr_A2_x<9) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CDL313'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CDL314'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (((LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & 
                (LST_TUC.Nr_A2_x<11))) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CDL315'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>4) & 
                (LST_TUC.Nr_A2_x<8) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CDL316'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>1) & (LST_TUC.Nr_A5_x<5) & 
                (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CDL317'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<11) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>1) & 
                (LST_TUC.Nr_A5_x<5) & (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CDL318'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x>1) & 
                (LST_TUC.Nr_A5_x<5) & (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CDL319'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x>1) & (LST_TUC.Nr_A5_x<5) & (LST_TUC.Nr_TI_x>49) & 
                (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CDL320'

    #Condutor, RAx
    for n in [0,1]:
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & (LST_TUC.Nr_A3_x==1) & 
        (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x== (40 + n)),'Cd_SISBASE_SFF']='CDR'+ str(112 - 11*(1-n))
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & 
        (((LST_TUC.Nr_A2_x>1) & (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & (LST_TUC.Nr_A2_x<11))) & 
        (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x == (40 + n)),'Cd_SISBASE_SFF']='CDR'+ str(113 - 11*(1-n))
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>4) & (LST_TUC.Nr_A2_x<9) & 
        (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x == (40 + n)),'Cd_SISBASE_SFF']='CDR'+ str(114 - 11*(1-n))
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & (LST_TUC.Nr_A3_x>1) & 
        (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x == (40 + n)),'Cd_SISBASE_SFF']='CDR'+ str(115 - 11*(1-n))
        LST_TUC.loc[((LST_TUC.Nr_TUC_x == 190) & (LST_TUC.Nr_A1_x < 3) & (LST_TUC.Nr_A5_x == 1) & (LST_TUC.Nr_TI_x == (40 + n)) &
        (((LST_TUC.Nr_A2_x>1) & (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & (LST_TUC.Nr_A2_x<11))) &
        (((LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<6)) | ((LST_TUC.Nr_A3_x == 9)))),'Cd_SISBASE_SFF'] = 'CDR'+ str(116 - 11*(1-n))
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (((LST_TUC.Nr_A2_x>1) & (LST_TUC.Nr_A2_x<5)) |
        ((LST_TUC.Nr_A2_x>8) & (LST_TUC.Nr_A2_x<11))) & (LST_TUC.Nr_A3_x>5) & (LST_TUC.Nr_A3_x<9) & 
        (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x == (40 + n)),'Cd_SISBASE_SFF']='CDR'+ str(117 - 11*(1-n))
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>4) & (LST_TUC.Nr_A2_x<9) & 
        (LST_TUC.Nr_A3_x>5) & (LST_TUC.Nr_A3_x<100) & (LST_TUC.Nr_A5_x==1) &
        (LST_TUC.Nr_TI_x == (40 + n)),'Cd_SISBASE_SFF']='CDR'+ str(118 - 11*(1-n))
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & (LST_TUC.Nr_A3_x==1) & 
        (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x == (40 + n)),'Cd_SISBASE_SFF']='CDR'+ str(119 - 11*(1-n))
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>1) & (LST_TUC.Nr_A2_x<11) & 
        (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x == (40 + n)),'Cd_SISBASE_SFF']='CDR'+ str(120 - 11*(1-n))
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & (LST_TUC.Nr_A3_x>1) & 
        (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x == (40 + n)),'Cd_SISBASE_SFF']='CDR'+ str(121 - 11*(1-n))
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>1) & (LST_TUC.Nr_A2_x<11) & 
        (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x!=1) &
        (LST_TUC.Nr_TI_x == (40 + n)),'Cd_SISBASE_SFF'] ='CDR'+ str(122 - 11*(1-n))

    #Condutor, LAU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>34) & 
                (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CDL201'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (((LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & 
                (LST_TUC.Nr_A2_x<11))) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x>34) & (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CDL202'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>4) & 
                (LST_TUC.Nr_A2_x<9) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x>34) & (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CDL203'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x>34) & (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CDL204'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (((LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & 
                (LST_TUC.Nr_A2_x<11))) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>34) & (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CDL205'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>4) & 
                (LST_TUC.Nr_A2_x<8) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>34) & (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CDL206'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>1) & (LST_TUC.Nr_A5_x<5) & 
                (LST_TUC.Nr_TI_x>34) & (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CDL207'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<11) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>1) & 
                (LST_TUC.Nr_A5_x<5) & (LST_TUC.Nr_TI_x>34) & (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CDL208'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x>1) & 
                (LST_TUC.Nr_A5_x<5) & (LST_TUC.Nr_TI_x>34) & (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CDL209'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x>1) & (LST_TUC.Nr_A5_x<5) & (LST_TUC.Nr_TI_x>34) & 
                (LST_TUC.Nr_TI_x<40),'Cd_SISBASE_SFF']='CDL210'
    #Condutor, LAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>57) & 
                (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CDL211'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (((LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & 
                (LST_TUC.Nr_A2_x<11))) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x>57) & (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CDL212'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>4) & 
                (LST_TUC.Nr_A2_x<9) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x>57) & (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CDL213'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x>57) & (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CDL214'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (((LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & 
                (LST_TUC.Nr_A2_x<11))) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>57) & (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CDL215'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>4) & 
                (LST_TUC.Nr_A2_x<8) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>57) & (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CDL216'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>1) & (LST_TUC.Nr_A5_x<5) & 
                (LST_TUC.Nr_TI_x>57) & (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CDL217'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<11) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>1) & 
                (LST_TUC.Nr_A5_x<5) & (LST_TUC.Nr_TI_x>57) & (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CDL218'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x>1) & 
                (LST_TUC.Nr_A5_x<5) & (LST_TUC.Nr_TI_x>57) & (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CDL219'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x<3) & (LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x>1) & (LST_TUC.Nr_A5_x<5) & (LST_TUC.Nr_TI_x>57) & 
                (LST_TUC.Nr_TI_x<60),'Cd_SISBASE_SFF']='CDL220'
    #Condutor, SMU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='CDR401'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (((LST_TUC.Nr_A2_x>1) &
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & 
                (LST_TUC.Nr_A2_x<11))) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='CDR402'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x>4) & 
                (LST_TUC.Nr_A2_x<9) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='CDR403'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x==1) &
                (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='CDR404'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (((LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x<11) & (LST_TUC.Nr_A2_x>8))) & 
                (((LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<6)) | (LST_TUC.Nr_A3_x==9)) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='CDR405'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (((LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & 
                (LST_TUC.Nr_A2_x<11))) & (LST_TUC.Nr_A3_x>5) & (LST_TUC.Nr_A3_x<9) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='CDR406'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x>4) & 
                (LST_TUC.Nr_A2_x<9) & (LST_TUC.Nr_A3_x>5) & (LST_TUC.Nr_A3_x<100) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='CDR407'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='CDR408'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<11) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x!=1) & 
                (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='CDR409'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x!=1) & 
                (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='CDR410'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<11) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='CDR411'
    #Condutor, SMR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='CDR412'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (((LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & 
                (LST_TUC.Nr_A2_x<11))) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='CDR413'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x>4) & 
                (LST_TUC.Nr_A2_x<9) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='CDR414'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='CDR415'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (((LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & 
                (LST_TUC.Nr_A2_x<11))) & (((LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<6)) | (LST_TUC.Nr_A3_x==9)) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='CDR416'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (((LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<5)) | ((LST_TUC.Nr_A2_x>8) & 
                (LST_TUC.Nr_A2_x<11))) & (LST_TUC.Nr_A3_x>5) & (LST_TUC.Nr_A3_x<9) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='CDR417'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x>4) & 
                (LST_TUC.Nr_A2_x<9) & (LST_TUC.Nr_A3_x>5) & (LST_TUC.Nr_A3_x<100) & 
                (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='CDR418'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='CDR419'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<11) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x!=1) & 
                (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='CDR420'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x==1) & 
                (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & (LST_TUC.Nr_A5_x!=1) & 
                (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='CDR421'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==190) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_A2_x>1) & 
                (LST_TUC.Nr_A2_x<11) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_A3_x<10) & 
                (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='CDR422'
    #Conversor de corrente, SDU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==195) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x>29) & 
                (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CCO301'
    #Conversor de corrente, SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==195) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x>49) & 
                (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CCO302'
    #Conversor de frequencia, SDU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==200) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x>29) & 
                (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='CFR301'
    #Conversor de frequencia, SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==200) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x>49) & 
                (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='CFR302'

    #Disjuntor, SDU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==1) & (((LST_TUC.Nr_A2_x==99)) | ((LST_TUC.Nr_A2_x>68) & 
                (LST_TUC.Nr_A2_x<90))) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_A6_x>30) & (LST_TUC.Nr_A6_x<41) & 
                (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='DSJ301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==1) & (((LST_TUC.Nr_A2_x==99)) | ((LST_TUC.Nr_A2_x>68) & 
                (LST_TUC.Nr_A2_x<90))) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_A6_x>4) & (LST_TUC.Nr_A6_x<26) & 
                (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='DSJ302'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==2) & ((LST_TUC.Nr_A2_x<61) | ((LST_TUC.Nr_A2_x>89) & 
                (LST_TUC.Nr_A2_x<99))) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>29) & 
                (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='DSJ303'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==1) & (((LST_TUC.Nr_A2_x==99)) | ((LST_TUC.Nr_A2_x>68) & 
                (LST_TUC.Nr_A2_x<90))) & (LST_TUC.Nr_A5_x==2) & (LST_TUC.Nr_A6_x>30) & (LST_TUC.Nr_A6_x<41) & 
                (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='DSJ304'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>68) & 
                (LST_TUC.Nr_A2_x<90) )) & (LST_TUC.Nr_A5_x==2) & (LST_TUC.Nr_A6_x>4) & (LST_TUC.Nr_A6_x<26) & 
                (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='DSJ305'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==2) & ((LST_TUC.Nr_A2_x<61) | ((LST_TUC.Nr_A2_x>89) & 
                (LST_TUC.Nr_A2_x<99))) & (LST_TUC.Nr_A5_x==2) & (LST_TUC.Nr_TI_x>29) & 
                (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='DSJ306'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==3) & (LST_TUC.Nr_A2_x>68) & 
                (LST_TUC.Nr_A2_x<85) & (LST_TUC.Nr_A3_x>33) & (LST_TUC.Nr_A3_x<76) & 
                (LST_TUC.Nr_A4_x==4) & (LST_TUC.Nr_A5_x==2) & (LST_TUC.Nr_A6_x>30) & 
                (LST_TUC.Nr_A6_x<41) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='DSJ307'
    #Disjuntor, SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==1) &
                ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>68) & (LST_TUC.Nr_A2_x<90))) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_A6_x>30) & (LST_TUC.Nr_A6_x<41) & ((LST_TUC.Nr_TI_x>19) 
                & (LST_TUC.Nr_TI_x<24) | (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55)),'Cd_SISBASE_SFF']='DSJ308'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A2_x==99) | 
                ((LST_TUC.Nr_A2_x>68) & (LST_TUC.Nr_A2_x<90))) & (LST_TUC.Nr_A5_x==1) & 
                (LST_TUC.Nr_A6_x>4) & (LST_TUC.Nr_A6_x<26) & ((LST_TUC.Nr_TI_x>19) 
                & (LST_TUC.Nr_TI_x<24) | (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55)),'Cd_SISBASE_SFF']='DSJ309'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==2) & 
                ((LST_TUC.Nr_A2_x<61) | ((LST_TUC.Nr_A2_x>89) & (LST_TUC.Nr_A2_x<99))) & (LST_TUC.Nr_A5_x==1) & 
                ((LST_TUC.Nr_TI_x>19) 
                & (LST_TUC.Nr_TI_x<24) | (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55)),'Cd_SISBASE_SFF']='DSJ310'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A2_x==99) | 
                ((LST_TUC.Nr_A2_x>68) & (LST_TUC.Nr_A2_x<90))) & (LST_TUC.Nr_A5_x==2) & 
                (LST_TUC.Nr_A6_x>30) & (LST_TUC.Nr_A6_x<41) & ((LST_TUC.Nr_TI_x>19) 
                & (LST_TUC.Nr_TI_x<24) | (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55)),'Cd_SISBASE_SFF']='DSJ311'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==1) & 
                ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>68) & (LST_TUC.Nr_A2_x<90))) & (LST_TUC.Nr_A5_x==2) & 
                (LST_TUC.Nr_A6_x>4) & (LST_TUC.Nr_A6_x<26) & ((LST_TUC.Nr_TI_x>19) 
                & (LST_TUC.Nr_TI_x<24) | (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55)),'Cd_SISBASE_SFF']='DSJ312'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==2) & (((LST_TUC.Nr_A2_x<61) & (LST_TUC.Nr_A5_x==2)) | 
                ((LST_TUC.Nr_A2_x>89) & (LST_TUC.Nr_A2_x<99))) & 
                ((LST_TUC.Nr_TI_x>19) 
                & (LST_TUC.Nr_TI_x<24) | (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55)),'Cd_SISBASE_SFF']='DSJ313'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==210) & (LST_TUC.Nr_A1_x==3) & (LST_TUC.Nr_A2_x>68) & (LST_TUC.Nr_A2_x<85) & 
                (LST_TUC.Nr_A3_x>33) & (LST_TUC.Nr_A3_x<76) & (LST_TUC.Nr_A4_x==4) & (LST_TUC.Nr_A5_x==2) & 
                (LST_TUC.Nr_A6_x>30) & (LST_TUC.Nr_A6_x<41) & ((LST_TUC.Nr_TI_x>19) 
                & (LST_TUC.Nr_TI_x<24) | (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55)),'Cd_SISBASE_SFF']='DSJ314'
    #Poste, SDU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>4) & 
                (LST_TUC.Nr_A5_x<15) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='PST301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>14) & 
                (LST_TUC.Nr_A5_x<19) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='PST302'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>18) & 
                (LST_TUC.Nr_A5_x<29) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='PST303'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A4_x>3) & 
                (LST_TUC.Nr_A4_x<14) & ((LST_TUC.Nr_A5_x<3) | ((LST_TUC.Nr_A5_x>29) & (LST_TUC.Nr_A5_x<100))) & 
                (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='PST304'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A4_x>13) & 
                (LST_TUC.Nr_A4_x<92) & ((LST_TUC.Nr_A5_x<3) | ((LST_TUC.Nr_A5_x>29) & (LST_TUC.Nr_A5_x<100))) & 
                (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='PST305'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==2) & (LST_TUC.Nr_A5_x>79) & 
                (LST_TUC.Nr_A5_x<82) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='PST306'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==2) & (LST_TUC.Nr_A5_x>81) & 
                (LST_TUC.Nr_A5_x<84) & (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='PST307'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x>2) & (LST_TUC.Nr_A3_x<5) & 
                (LST_TUC.Nr_TI_x>29) & (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='PST308'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==5) & (LST_TUC.Nr_TI_x>29) & 
                (LST_TUC.Nr_TI_x<35),'Cd_SISBASE_SFF']='PST309'

    #Poste, SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>4) & 
                (LST_TUC.Nr_A5_x<15) & (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='PST310'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>14) & 
                (LST_TUC.Nr_A5_x<19) & (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='PST311'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>18) & 
                (LST_TUC.Nr_A5_x<29) & (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='PST312'

    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A4_x>3) & 
                (LST_TUC.Nr_A4_x<14) & ((LST_TUC.Nr_A5_x<3) | ((LST_TUC.Nr_A5_x>29) & (LST_TUC.Nr_A5_x<100))) & 
                (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='PST313'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A4_x>13) & 
                (LST_TUC.Nr_A4_x<92) & ((LST_TUC.Nr_A5_x<3) | ((LST_TUC.Nr_A5_x>29) & (LST_TUC.Nr_A5_x<100))) & 
                (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='PST314'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==2) & (LST_TUC.Nr_A5_x>79) & 
                (LST_TUC.Nr_A5_x<82) & (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='PST315'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==2) & (LST_TUC.Nr_A5_x>81) & 
                (LST_TUC.Nr_A5_x<84) & (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='PST316'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x>2) & (LST_TUC.Nr_A3_x<5) & 
                (LST_TUC.Nr_TI_x>49) & (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='PST317'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==5) & (LST_TUC.Nr_TI_x>49) &
                (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='PST318'
    #Poste, RAU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>4) & 
                (LST_TUC.Nr_A5_x<15) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='PST101'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>14) & 
                (LST_TUC.Nr_A5_x<19) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='PST102'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>18) & 
                (LST_TUC.Nr_A5_x<29) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='PST103'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A4_x>3) & 
                (LST_TUC.Nr_A4_x<14) & ((LST_TUC.Nr_A5_x<3) | ((LST_TUC.Nr_A5_x>29) & (LST_TUC.Nr_A5_x<100)))
                & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='PST104'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A4_x>13) & 
                (LST_TUC.Nr_A4_x<92) & ((LST_TUC.Nr_A5_x<3) | ((LST_TUC.Nr_A5_x>29) & (LST_TUC.Nr_A5_x<100))) & 
                (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='PST105'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==2) & (LST_TUC.Nr_A5_x>79) & 
                (LST_TUC.Nr_A5_x<82) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='PST106'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==2) & (LST_TUC.Nr_A5_x>81) & 
                (LST_TUC.Nr_A5_x<84) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='PST107'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x>2) & (LST_TUC.Nr_A3_x<5) & 
                (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='PST108'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==5) & 
                (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='PST109'
    #Poste, RAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>4) & 
                (LST_TUC.Nr_A5_x<15) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='PST110'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>14) & 
                (LST_TUC.Nr_A5_x<19) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='PST111'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A5_x>18) & 
                (LST_TUC.Nr_A5_x<29) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='PST112'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A4_x>3) & 
                (LST_TUC.Nr_A4_x<14) & ((LST_TUC.Nr_A5_x<3) | ((LST_TUC.Nr_A5_x>29) & (LST_TUC.Nr_A5_x<100))) & 
                (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='PST113'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_A4_x>13) & 
                (LST_TUC.Nr_A4_x<92) & ((LST_TUC.Nr_A5_x<3) | ((LST_TUC.Nr_A5_x>29) & (LST_TUC.Nr_A5_x<100))) & 
                (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='PST114'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==2) & (LST_TUC.Nr_A5_x>79) & 
                (LST_TUC.Nr_A5_x<82) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='PST115'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==2) & (LST_TUC.Nr_A5_x>81) & 
                (LST_TUC.Nr_A5_x<84) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='PST116'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x>2) & (LST_TUC.Nr_A3_x<5) & 
                (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='PST117'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==255) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A3_x==5) & 
                (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='PST118'
    #Luminária, SDU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==290) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x>29) & 
                (LST_TUC.Nr_TI_x<34),'Cd_SISBASE_SFF']='LUM301'
    #Luminária, SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==290) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x>49) & 
                (LST_TUC.Nr_TI_x<55),'Cd_SISBASE_SFF']='LUM311'
    #Luminária, RAU
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==290) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='LUM101'
    #Luminária, RAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==290) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='LUM111'
    #Medição, SMU/SMR
    tip=[93,96]
    offset=0
    for n in tip:
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==295) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==11)) & ((LST_TUC.Nr_A2_x==10) | ((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=3))) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_TI_x==n),'Cd_SISBASE_SFF']='MRD4' + str('0' + str(1+9*offset))[-2:]
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==295) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==11)) & ((LST_TUC.Nr_A2_x==10) | ((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=3))) & (LST_TUC.Nr_A3_x>1) & (LST_TUC.Nr_TI_x==n),'Cd_SISBASE_SFF']='MRD4' + str('0' + str(2+9*offset))[-2:]
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==295) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==11)) & (LST_TUC.Nr_A2_x==4) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_TI_x==n),'Cd_SISBASE_SFF']='MRD4' + str('0' + str(3+9*offset))[-2:]
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==295) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==11)) & (LST_TUC.Nr_A2_x==4) & (LST_TUC.Nr_A3_x!=1) & (LST_TUC.Nr_TI_x==n),'Cd_SISBASE_SFF']='MRD4' + str('0' + str(4+9*offset))[-2:]
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==295) & (LST_TUC.Nr_A1_x==13) & (LST_TUC.Nr_A2_x==4) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_TI_x==n),'Cd_SISBASE_SFF']='MRD4' + str('0' + str(5+9*offset))[-2:]
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==295) & (LST_TUC.Nr_A1_x==13) & (LST_TUC.Nr_A2_x==4) & (LST_TUC.Nr_A3_x!=1) & (LST_TUC.Nr_TI_x==n),'Cd_SISBASE_SFF']='MRD4' + str('0' + str(6+9*offset))[-2:]
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==295) & ((LST_TUC.Nr_A1_x>=16) & (LST_TUC.Nr_A1_x<=17)) & ((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=10)) & (LST_TUC.Nr_A3_x==1) & (LST_TUC.Nr_TI_x==n),'Cd_SISBASE_SFF']='MRD4' + str('0' + str(7+9*offset))[-2:]
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==295) & ((LST_TUC.Nr_A1_x>=16) & (LST_TUC.Nr_A1_x<=17)) & ((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=10)) & (LST_TUC.Nr_A3_x!=1) & (LST_TUC.Nr_TI_x==n),'Cd_SISBASE_SFF']='MRD4' + str('0' + str(8+9*offset))[-2:]
        LST_TUC.loc[(LST_TUC.Nr_TUC_x==295) & (LST_TUC.Nr_A1_x==18) & ((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=10))  & (LST_TUC.Nr_TI_x==n),'Cd_SISBASE_SFF']='MRD4' + str('0' + str(9+9*offset))[-2:]
        offset=offset+1
    #Pára-raios, SDU/SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==310) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==99) | ((LST_TUC.Nr_A3_x>=69) & (LST_TUC.Nr_A3_x<=89))) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='PRS301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==310) & (LST_TUC.Nr_A1_x==1) & (((LST_TUC.Nr_A3_x>=1) & (LST_TUC.Nr_A3_x<=60)) | ((LST_TUC.Nr_A3_x>=90) & (LST_TUC.Nr_A3_x<=98))) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='PRS302'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==310) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==99) | ((LST_TUC.Nr_A3_x>=69) & (LST_TUC.Nr_A3_x<=89))) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='PRS303'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==310) & (LST_TUC.Nr_A1_x==1) & (((LST_TUC.Nr_A3_x>=1) & (LST_TUC.Nr_A3_x<=60)) | ((LST_TUC.Nr_A3_x>=90) & (LST_TUC.Nr_A3_x<=98))) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='PRS304'
    #Pára-raios, RAU/RAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==310) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='PRS101'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==310) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='PRS111'
    #Pára-raios, LAU/LAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==310) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==99) | ((LST_TUC.Nr_A3_x>=69) & (LST_TUC.Nr_A3_x<=89))) & (LST_TUC.Nr_TI_x>=35) & (LST_TUC.Nr_TI_x<=39),'Cd_SISBASE_SFF']='PRS201'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==310) & (LST_TUC.Nr_A1_x==1) & (((LST_TUC.Nr_A3_x>=1) & (LST_TUC.Nr_A3_x<=60)) | ((LST_TUC.Nr_A3_x>=90) & (LST_TUC.Nr_A3_x<=98))) & (LST_TUC.Nr_TI_x>=35) & (LST_TUC.Nr_TI_x<=39),'Cd_SISBASE_SFF']='PRS202'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==310) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==99) | ((LST_TUC.Nr_A3_x>=69) & (LST_TUC.Nr_A3_x<=89))) & (LST_TUC.Nr_TI_x>=58) & (LST_TUC.Nr_TI_x<=59),'Cd_SISBASE_SFF']='PRS203'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==310) & (LST_TUC.Nr_A1_x==1) & (((LST_TUC.Nr_A3_x>=1) & (LST_TUC.Nr_A3_x<=60)) | ((LST_TUC.Nr_A3_x>=90) & (LST_TUC.Nr_A3_x<=98))) & (LST_TUC.Nr_TI_x>=58) & (LST_TUC.Nr_TI_x<=59),'Cd_SISBASE_SFF']='PRS204'
    #Protetor de rede, SDU/SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==325) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='PRR301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==325) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='PRR302'
    #Protetor de rede, RAU/RAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==325) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='PRR101'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==325) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='PRR111'
    #Reator, SDU/SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==330) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='REA301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==330) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='REA302'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==330) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='REA303'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==330) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='REA304'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==330) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='REA305'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==330) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='REA306'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==330) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='REA307'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==330) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='REA308'
    #Regulador, SDU/SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==2) | (LST_TUC.Nr_A3_x==4) | (LST_TUC.Nr_A3_x==6) | ((LST_TUC.Nr_A3_x>=65) & (LST_TUC.Nr_A3_x<=99))) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='RGS301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==1) | (LST_TUC.Nr_A3_x==3) | (LST_TUC.Nr_A3_x==5) | ((LST_TUC.Nr_A3_x>=7) & (LST_TUC.Nr_A3_x<=64))) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='RGS302'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==2) | (LST_TUC.Nr_A3_x==4) | (LST_TUC.Nr_A3_x==6) | ((LST_TUC.Nr_A3_x>=61) & (LST_TUC.Nr_A3_x<=99))) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='RGS303'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==1) | (LST_TUC.Nr_A3_x==3) | (LST_TUC.Nr_A3_x==5) | ((LST_TUC.Nr_A3_x>=7) & (LST_TUC.Nr_A3_x<=60))) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='RGS304'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==2) | (LST_TUC.Nr_A3_x==4) | (LST_TUC.Nr_A3_x==6) | ((LST_TUC.Nr_A3_x>=65) & (LST_TUC.Nr_A3_x<=99))) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='RGS305'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==1) | (LST_TUC.Nr_A3_x==3) | (LST_TUC.Nr_A3_x==5) | ((LST_TUC.Nr_A3_x>=7) & (LST_TUC.Nr_A3_x<=64))) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='RGS306'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==2) | (LST_TUC.Nr_A3_x==4) | (LST_TUC.Nr_A3_x==6) | ((LST_TUC.Nr_A3_x>=61) & (LST_TUC.Nr_A3_x<=99))) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='RGS307'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==1) | (LST_TUC.Nr_A3_x==3) | (LST_TUC.Nr_A3_x==5) | ((LST_TUC.Nr_A3_x>=7) & (LST_TUC.Nr_A3_x<=60))) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='RGS308'
    #Regulador, RAU/RAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='REG101'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='REG111'
    #Regulador, LAU/LAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==2) | (LST_TUC.Nr_A3_x==4) | (LST_TUC.Nr_A3_x==6) | ((LST_TUC.Nr_A3_x>=65) & (LST_TUC.Nr_A3_x<=99))) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x>=35) & (LST_TUC.Nr_TI_x<=39),'Cd_SISBASE_SFF']='REG201'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==1) | (LST_TUC.Nr_A3_x==3) | (LST_TUC.Nr_A3_x==5) | ((LST_TUC.Nr_A3_x>=7) & (LST_TUC.Nr_A3_x<=64))) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x>=35) & (LST_TUC.Nr_TI_x<=39),'Cd_SISBASE_SFF']='REG202'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==2) | (LST_TUC.Nr_A3_x==4) | (LST_TUC.Nr_A3_x==6) | ((LST_TUC.Nr_A3_x>=61) & (LST_TUC.Nr_A3_x<=99))) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>=35) & (LST_TUC.Nr_TI_x<=39),'Cd_SISBASE_SFF']='REG203'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==1) | (LST_TUC.Nr_A3_x==3) | (LST_TUC.Nr_A3_x==5) | ((LST_TUC.Nr_A3_x>=7) & (LST_TUC.Nr_A3_x<=60))) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>=35) & (LST_TUC.Nr_TI_x<=39),'Cd_SISBASE_SFF']='REG204'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==2) | (LST_TUC.Nr_A3_x==4) | (LST_TUC.Nr_A3_x==6) | ((LST_TUC.Nr_A3_x>=65) & (LST_TUC.Nr_A3_x<=99))) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x>=58) & (LST_TUC.Nr_TI_x<=59),'Cd_SISBASE_SFF']='REG205'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==1) | (LST_TUC.Nr_A3_x==3) | (LST_TUC.Nr_A3_x==5) | ((LST_TUC.Nr_A3_x>=7) & (LST_TUC.Nr_A3_x<=64))) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_TI_x>=58) & (LST_TUC.Nr_TI_x<=59),'Cd_SISBASE_SFF']='REG206'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==2) | (LST_TUC.Nr_A3_x==4) | (LST_TUC.Nr_A3_x==6) | ((LST_TUC.Nr_A3_x>=61) & (LST_TUC.Nr_A3_x<=99))) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>=58) & (LST_TUC.Nr_TI_x<=59),'Cd_SISBASE_SFF']='REG207'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==340) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A3_x==1) | (LST_TUC.Nr_A3_x==3) | (LST_TUC.Nr_A3_x==5) | ((LST_TUC.Nr_A3_x>=7) & (LST_TUC.Nr_A3_x<=60))) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_TI_x>=58) & (LST_TUC.Nr_TI_x<=59),'Cd_SISBASE_SFF']='REG208'
    #Religador, SDU/SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==345) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A6_x>=31) & (LST_TUC.Nr_A6_x<=40) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='RLS301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==345) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A6_x>=5) & (LST_TUC.Nr_A6_x<=25) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='RLS302'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==345) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A6_x>=31) & (LST_TUC.Nr_A6_x<=40) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='RLS303'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==345) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A6_x>=5) & (LST_TUC.Nr_A6_x<=25) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='RLS304'
    #Religador, RAU/RAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==345) & (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='REL101'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==345) & (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='REL102'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==345) & (LST_TUC.Nr_A4_x!=1) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='REL111'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==345) & (LST_TUC.Nr_A4_x==1) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='REL112'
    #Religador, LAU/LAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==345) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A6_x>=31) & (LST_TUC.Nr_A6_x<=40) & (LST_TUC.Nr_TI_x>=35) & (LST_TUC.Nr_TI_x<=39),'Cd_SISBASE_SFF']='REL201'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==345) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A6_x>=5) & (LST_TUC.Nr_A6_x<=25) & (LST_TUC.Nr_TI_x>=35) & (LST_TUC.Nr_TI_x<=39),'Cd_SISBASE_SFF']='REL202'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==345) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A6_x>=31) & (LST_TUC.Nr_A6_x<=40) & (LST_TUC.Nr_TI_x>=58) & (LST_TUC.Nr_TI_x<=59),'Cd_SISBASE_SFF']='REL203'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==345) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_A6_x>=5) & (LST_TUC.Nr_A6_x<=25) & (LST_TUC.Nr_TI_x>=58) & (LST_TUC.Nr_TI_x<=59),'Cd_SISBASE_SFF']='REL204'
    #Transformador de aterramento, SDU/SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==560) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TRA301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==560) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='TRA303'
    #Transformador de distribuição, RAU/RAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & ((LST_TUC.Nr_A4_x==1) | (LST_TUC.Nr_A4_x==3)) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='TRD101'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & (LST_TUC.Nr_A4_x==5) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='TRD102'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & ((LST_TUC.Nr_A4_x==7) | (LST_TUC.Nr_A4_x==9)) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='TRD103'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & ((LST_TUC.Nr_A4_x==2) | (LST_TUC.Nr_A4_x==4) | (LST_TUC.Nr_A4_x==6) | ((LST_TUC.Nr_A4_x>=11) & (LST_TUC.Nr_A4_x<=99))) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='TRD104'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & ((LST_TUC.Nr_A4_x==1) | (LST_TUC.Nr_A4_x==3) | (LST_TUC.Nr_A4_x==5) | (LST_TUC.Nr_A4_x==7) | (LST_TUC.Nr_A4_x==9)) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='TRD105'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & (LST_TUC.Nr_A4_x>=11) & (LST_TUC.Nr_A4_x<=21) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='TRD106'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & (LST_TUC.Nr_A4_x>=23) & (LST_TUC.Nr_A4_x<=27) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='TRD107'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & (LST_TUC.Nr_A4_x==29) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='TRD108'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & ((LST_TUC.Nr_A4_x==2) | (LST_TUC.Nr_A4_x==4) | (LST_TUC.Nr_A4_x==6) | ((LST_TUC.Nr_A4_x>=31) & (LST_TUC.Nr_A4_x<=99))) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==40),'Cd_SISBASE_SFF']='TRD109'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & ((LST_TUC.Nr_A4_x==1) | (LST_TUC.Nr_A4_x==3)) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='TRD110'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & (LST_TUC.Nr_A4_x==5) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='TRD111'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & ((LST_TUC.Nr_A4_x==7) | (LST_TUC.Nr_A4_x==9)) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='TRD112'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & ((LST_TUC.Nr_A4_x==2) | (LST_TUC.Nr_A4_x==4) | (LST_TUC.Nr_A4_x==6) | ((LST_TUC.Nr_A4_x>=11) & (LST_TUC.Nr_A4_x<=99))) & (LST_TUC.Nr_A5_x==1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='TRD113'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & ((LST_TUC.Nr_A4_x==1) | (LST_TUC.Nr_A4_x==3) | (LST_TUC.Nr_A4_x==5) | (LST_TUC.Nr_A4_x==7) | (LST_TUC.Nr_A4_x==9)) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='TRD114'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & (LST_TUC.Nr_A4_x>=11) & (LST_TUC.Nr_A4_x<=21) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='TRD115'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & (LST_TUC.Nr_A4_x>=23) & (LST_TUC.Nr_A4_x<=27) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='TRD116'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & (LST_TUC.Nr_A4_x==29) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='TRD117'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==565) & ((LST_TUC.Nr_A1_x==1) | (LST_TUC.Nr_A1_x==5)) & ((LST_TUC.Nr_A4_x==2) | (LST_TUC.Nr_A4_x==4) | (LST_TUC.Nr_A4_x==6) | ((LST_TUC.Nr_A4_x>=31) & (LST_TUC.Nr_A4_x<=99))) & (LST_TUC.Nr_A5_x!=1) & (LST_TUC.Nr_A6_x>=1) & (LST_TUC.Nr_A6_x<=2) & (LST_TUC.Nr_TI_x==41),'Cd_SISBASE_SFF']='TRD118'
    #Transformador força, SDU/SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==570) & ((LST_TUC.Nr_A4_x==1) | (LST_TUC.Nr_A4_x==3) | (LST_TUC.Nr_A4_x==5) | (LST_TUC.Nr_A4_x==7) | (LST_TUC.Nr_A4_x==9) | ((LST_TUC.Nr_A4_x>=9) & (LST_TUC.Nr_A4_x<=77))) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TRF301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==570) & ((LST_TUC.Nr_A4_x>=78) & (LST_TUC.Nr_A4_x<=82)) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TRF302'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==570) & ((LST_TUC.Nr_A4_x>=83) & (LST_TUC.Nr_A4_x<=86)) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TRF303'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==570) & ((LST_TUC.Nr_A4_x>=87) & (LST_TUC.Nr_A4_x<=91)) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TRF304'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==570) & ((LST_TUC.Nr_A4_x==2) | (LST_TUC.Nr_A4_x==4) | (LST_TUC.Nr_A4_x==6) | ((LST_TUC.Nr_A4_x>=92) & (LST_TUC.Nr_A4_x<=99))) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TRF305'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==570) & ((LST_TUC.Nr_A4_x==1) | (LST_TUC.Nr_A4_x==3) | (LST_TUC.Nr_A4_x==5) | (LST_TUC.Nr_A4_x==7) | (LST_TUC.Nr_A4_x==9) | ((LST_TUC.Nr_A4_x>=9) & (LST_TUC.Nr_A4_x<=77))) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='TRF306'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==570) & ((LST_TUC.Nr_A4_x>=78) & (LST_TUC.Nr_A4_x<=82)) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='TRF307'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==570) & ((LST_TUC.Nr_A4_x>=83) & (LST_TUC.Nr_A4_x<=86)) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='TRF308'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==570) & ((LST_TUC.Nr_A4_x>=87) & (LST_TUC.Nr_A4_x<=91)) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='TRF309'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==570) & ((LST_TUC.Nr_A4_x==2) | (LST_TUC.Nr_A4_x==4) | (LST_TUC.Nr_A4_x==6) | ((LST_TUC.Nr_A4_x>=92) & (LST_TUC.Nr_A4_x<=99))) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='TRF310'
    #Transformador medição, SDU/SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS302'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS303'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS304'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==11) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS305'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==11) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS306'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==12) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS307'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==12) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS308'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==13) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS309'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==13) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS310'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==20) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS311'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==20) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==1) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS312'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==2) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS313'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==2) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS314'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==2) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS315'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==2) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS316'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==11) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==2) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS317'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==11) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==2) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS318'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==12) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==2) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS319'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==12) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==2) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS320'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==13) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==2) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS321'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==13) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==2) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS322'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==20) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==2) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS323'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==20) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==2) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TMS324'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==1) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS325'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==1) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS326'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==1) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS327'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==1) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS328'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==11) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==1) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS329'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==11) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==1) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS330'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==12) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==1) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS331'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==12) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==1) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS332'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==13) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==1) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS333'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==13) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==1) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS334'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==20) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==1) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS335'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==20) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==1) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS336'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==2) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS337'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==2) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS338'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==2) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS339'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==2) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS340'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==11) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==2) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS341'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==11) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==2) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS342'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==12) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==2) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS343'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==12) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==2) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS344'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==13) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==2) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS345'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==13) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==2) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS346'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==20) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_A6_x==2) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS347'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==20) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_A6_x==2) & (((LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54)) | ((LST_TUC.Nr_TI_x>=20) & (LST_TUC.Nr_TI_x<=23))),'Cd_SISBASE_SFF']='TMS348'
    #Transformador medição, SMU/SMR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='TMS401'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='TMS402'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==20) & (LST_TUC.Nr_TI_x==93),'Cd_SISBASE_SFF']='TMS403'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='TMS411'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='TMS412'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==20) & (LST_TUC.Nr_TI_x==96),'Cd_SISBASE_SFF']='TMS413'
    #Transformador medição, LAU/LAR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_TI_x>=35) & (LST_TUC.Nr_TI_x<=39),'Cd_SISBASE_SFF']='TMS201'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_TI_x>=35) & (LST_TUC.Nr_TI_x<=39),'Cd_SISBASE_SFF']='TMS202'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_TI_x>=35) & (LST_TUC.Nr_TI_x<=39),'Cd_SISBASE_SFF']='TMS203'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_TI_x>=35) & (LST_TUC.Nr_TI_x<=39),'Cd_SISBASE_SFF']='TMS204'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_TI_x>=58) & (LST_TUC.Nr_TI_x<=59),'Cd_SISBASE_SFF']='TMS205'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==1) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_TI_x>=58) & (LST_TUC.Nr_TI_x<=59),'Cd_SISBASE_SFF']='TMS206'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & ((LST_TUC.Nr_A2_x==99) | ((LST_TUC.Nr_A2_x>=69) & (LST_TUC.Nr_A2_x<=89))) & (LST_TUC.Nr_TI_x>=58) & (LST_TUC.Nr_TI_x<=59),'Cd_SISBASE_SFF']='TMS207'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==575) & (LST_TUC.Nr_A1_x==2) & (((LST_TUC.Nr_A2_x>=1) & (LST_TUC.Nr_A2_x<=60)) | ((LST_TUC.Nr_A2_x>=90) & (LST_TUC.Nr_A2_x<=98))) & (LST_TUC.Nr_TI_x>=58) & (LST_TUC.Nr_TI_x<=59),'Cd_SISBASE_SFF']='TMS208'
    #Transformador auxiliar, SDU/SDR
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==580) & ((LST_TUC.Nr_A4_x==2) | (LST_TUC.Nr_A4_x==4) | (LST_TUC.Nr_A4_x==6) | ((LST_TUC.Nr_A4_x>=41) & (LST_TUC.Nr_A4_x<=99))) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TSA301'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==580) & ((LST_TUC.Nr_A4_x==1) | (LST_TUC.Nr_A4_x==3) | (LST_TUC.Nr_A4_x==5) | ((LST_TUC.Nr_A4_x>=7) & (LST_TUC.Nr_A4_x<=40))) & (LST_TUC.Nr_TI_x>=30) & (LST_TUC.Nr_TI_x<=34),'Cd_SISBASE_SFF']='TSA302'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==580) & ((LST_TUC.Nr_A4_x==2) | (LST_TUC.Nr_A4_x==4) | (LST_TUC.Nr_A4_x==6) | ((LST_TUC.Nr_A4_x>=41) & (LST_TUC.Nr_A4_x<=99))) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='TSA303'
    LST_TUC.loc[(LST_TUC.Nr_TUC_x==580) & ((LST_TUC.Nr_A4_x==1) | (LST_TUC.Nr_A4_x==3) | (LST_TUC.Nr_A4_x==5) | ((LST_TUC.Nr_A4_x>=7) & (LST_TUC.Nr_A4_x<=40))) & (LST_TUC.Nr_TI_x>=50) & (LST_TUC.Nr_TI_x<=54),'Cd_SISBASE_SFF']='TSA304'

    LST_TUC=LST_TUC[['Nr_TI','Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_SISBASE','Cd_SISBASE_SFF']]
    LST_TUC['Cd_SISBASE']=LST_TUC['Cd_SISBASE'].fillna('ND')
    LST_TUC['TESTE_Cd'] = np.where(LST_TUC['Cd_SISBASE'] == LST_TUC['Cd_SISBASE_SFF'],'OK','Justificar')
    LST_TUC = bullD.FCOG_ATR(LST_TUC, D2, st)


    LST_TUC.columns = ['Nr_TI','Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','Cd_SISBASE','Cd_SISBASE_SFF','TESTE_Cd','Cd_FOR_COGE_SFF','Nr_FAM_SFF']
    return LST_TUC
   
def calc_tx_md(AIS_TX, depr):
    AIS_TX['Dt_REF_DADOS'] = AIS_TX['Dt_REF_DADOS'].iloc[0]
    tbl_tx_dep=pd.read_csv('tabelas/tbl_tx_dep.csv', sep="|", encoding="Latin-1", dtype=str)
    list_campos=['VL_VU','Tx_REN674','Tx_REN367','Tx_REN240']
    for nm in list_campos:
        if (tbl_tx_dep[nm].dtype == 'object') and (nm in tbl_tx_dep.columns):
            tbl_tx_dep[nm] = pd.to_numeric(tbl_tx_dep[nm].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')
    for nm in ['Nr_A1', 'Nr_A2']:
        if (AIS_TX[nm].dtype == 'object') and (nm in AIS_TX.columns):
            AIS_TX[f'{nm}num'] = pd.to_numeric(AIS_TX[nm].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')
        else:
            AIS_TX[f'{nm}num'] = AIS_TX[f'{nm}']
            AIS_TX[f'{nm}'] = AIS_TX[f'{nm}'].astype(str)

    # Inicializando Ide_TUC_A1 com Nr_TUC
    AIS_TX['Ide_TUC_A1'] = AIS_TX['Nr_TUC']
    map_UC_A1 = {
                                ('190', 3): '190.03',
                                ('615', 3): '615.03',
                                ('160', 5): '160.05',
                                ('575', 11): '575.11',
                                ('575', 12): '575.12',
                                ('575', 13): '575.13',
                                ('575', 20): '575.20',
                                ('295', 1): '295.01',
                                ('295', 11): '295.11',
                                ('295', 13): '295.13',
                                ('295', 16): '295.16',
                                ('295', 17): '295.17',
                                ('295', 18): '295.18',
                                ('605', 1): '605.01',
                                ('605', 10): '605.10',
                                ('605', 15): '605.15',
                                ('590', 1): '590.01',
                                ('590', 5): '590.05',
                                ('590', 10): '590.10',
                                ('590', 15): '590.15',
                                ('565', 3): '565.03',
                                ('565', 4): '565.04',
                                ('565', 5): '565.05'
                            }
    
    lst_TUC_TEN = ['125', '130', '215', '255']
    TEN = AIS_TX['Nr_TUC'].isin(lst_TUC_TEN)
    AIS_TX.loc[TEN, 'Ide_TUC_A1'] = AIS_TX['Nr_TUC'] + '.' + AIS_TX['Nr_A1'].str.zfill(2)
    lst_TUC_TEN = ['160', '340', '575']
    TEN_maior_69 = AIS_TX['Nr_TUC'].isin(lst_TUC_TEN) & (AIS_TX['Nr_A2num'] >= 69)
    TEN_menor_69 = AIS_TX['Nr_TUC'].isin(lst_TUC_TEN) & (AIS_TX['Nr_A2num'] < 69)
    AIS_TX.loc[TEN_maior_69, 'Ide_TUC_A1'] = AIS_TX['Nr_TUC'] + '>=69'
    AIS_TX.loc[TEN_menor_69, 'Ide_TUC_A1'] = AIS_TX['Nr_TUC'] + '<69'
    # Tratamento para Nr_TUC == '190'
    uc190_1 = (AIS_TX['Nr_TUC'] == '190') & (AIS_TX['Nr_A1num'] == 1)
    uc190_2 = (AIS_TX['Nr_TUC'] == '190') & (AIS_TX['Nr_A1num'] == 2)
    AIS_TX.loc[uc190_1, 'Ide_TUC_A1'] = '190>=69'
    AIS_TX.loc[uc190_2, 'Ide_TUC_A1'] = '190<69'
    AIS_TX['Ide_TUC_A1'] = AIS_TX.apply(lambda row: map_UC_A1.get(
                                        (row['Nr_TUC'], row['Nr_A1num']), row['Ide_TUC_A1']), 
                                         axis=1)

    AIS_TX = AIS_TX.merge(tbl_tx_dep, on='Ide_TUC_A1', how='left')
    # Definição de vigência das resoluções
    AIS_TX['DT_REF_634'] = pd.Timestamp('2012-01-01')
    AIS_TX['DT_REF_367'] = pd.Timestamp('2009-07-01')
    # Garantindo que as colunas de data estão no formato correto
    AIS_TX['Dt_CNTB_AJST'] = pd.to_datetime(AIS_TX['Dt_CNTB_AJST'], errors='coerce')
    AIS_TX['Dt_Imob'] = pd.to_datetime(AIS_TX['Dt_Imob'], errors='coerce')
    AIS_TX['Dt_REF_DADOS'] = pd.to_datetime(AIS_TX['Dt_REF_DADOS'], errors='coerce')
    # Definição da data de referência DT1 (menor data entre Dt_IMOB e Dt_CNTB_AJST)
    AIS_TX['DT1'] = AIS_TX[['Dt_Imob', 'Dt_CNTB_AJST']].min(axis=1)

    # Cálculo de Nr_MESES (diferença em meses entre Dt_REF_DADOS e DT1)
    AIS_TX['Nr_MESES'] = (AIS_TX['Dt_REF_DADOS'].dt.year - AIS_TX['DT1'].dt.year) * 12 + \
                        (AIS_TX['Dt_REF_DADOS'].dt.month - AIS_TX['DT1'].dt.month)
    # Ajuste de Nr_MESES se o dia de Dt_REF_DADOS for menor que o dia de DT1
    AIS_TX.loc[AIS_TX['Dt_REF_DADOS'].dt.day < AIS_TX['DT1'].dt.day, 'Nr_MESES'] -= 1

    AIS_TX['CT_ADICIONAL_DEP'] = 0
    c1 = AIS_TX['DT1'].dt.day == 1
    c2 = AIS_TX['Dt_Imob'] == AIS_TX['Dt_CNTB_AJST']
    c3 = (depr == "***Mês seguinte***")
    c4 = (depr == "***Próprio mês***")
    AIS_TX.loc[(c1 & c2 & c3) | c4,'CT_ADICIONAL_DEP'] = 1

    def dif_meses(d1, d2):
        return (d1.dt.year - d2.dt.year) * 12 + (d1.dt.month - d2.dt.month)
    
    for var, tx, base1, base2 in zip(
            ['VAR_01', 'VAR_02', 'VAR_03', 'VAR_04', 'VAR_05'], 
            ['Tx_REN674', 'Tx_REN367', 'Tx_REN240', 'Tx_REN367', 'Tx_REN674'],
            ['Dt_REF_DADOS', 'DT_REF_634', 'DT_REF_367', 'DT_REF_634', 'Dt_REF_DADOS'],
            ['DT_REF_634', 'DT_REF_367', 'DT1', 'DT1', 'DT1']
        ):
        AIS_TX[var] =( (dif_meses(AIS_TX[base1], AIS_TX[base2]) + 
                        AIS_TX['CT_ADICIONAL_DEP'])* AIS_TX[tx] / 12) 
    
    AIS_TX['CT_DEP_REN240'] = AIS_TX['VAR_03'].clip(lower=0, upper=1)

    c1 = AIS_TX['CT_DEP_REN240'] !=0
    c2 = (AIS_TX['VAR_02']+AIS_TX['VAR_03']) > 1
    c3 = AIS_TX['VAR_04'].between(0, 1)

    AIS_TX['CT_DEP_REN367'] = 0
    AIS_TX['CT_DEP_REN367'] = np.where(c2 & c1, 1 - AIS_TX['CT_DEP_REN240'], 
                                                AIS_TX['CT_DEP_REN367'])
    AIS_TX['CT_DEP_REN367'] = np.where((~c2) & c1, AIS_TX['VAR_02'], AIS_TX['CT_DEP_REN367'])
    AIS_TX['CT_DEP_REN367'] = np.where(c3 & (~c1), AIS_TX['VAR_04'], AIS_TX['CT_DEP_REN367'])

    c1 = AIS_TX['CT_DEP_REN367'] != 0
    c2 = (AIS_TX['VAR_03']+AIS_TX['VAR_02']+AIS_TX['VAR_01']) > 1
    c3 = AIS_TX['VAR_05'].between(0, 1)

    AIS_TX['CT_DEP_REN634']=0
    AIS_TX['CT_DEP_REN634'] = np.where(c2 & c1, 1 - (AIS_TX['VAR_03'] + AIS_TX['VAR_02']), AIS_TX['CT_DEP_REN634'])
    AIS_TX['CT_DEP_REN634'] = np.where((~c2) & c1, AIS_TX['VAR_01'], AIS_TX['CT_DEP_REN634'])
    AIS_TX['CT_DEP_REN634'] = np.where(c3 & (~c1), AIS_TX['VAR_05'], AIS_TX['CT_DEP_REN634'])
    AIS_TX['CT_DEP_REN634'] = AIS_TX['CT_DEP_REN634'].clip(lower=0)

    AIS_TX['CT_DEP_TOT'] = 0
    AIS_TX['DEP_ACUM_REN240'] = AIS_TX['CT_DEP_REN240']
    AIS_TX['DEP_ACUM_REN367'] = AIS_TX['CT_DEP_REN367']
    AIS_TX['DEP_ACUM_REN674'] = AIS_TX['CT_DEP_REN634']
    AIS_TX['CT_DEP_REN240'] = (AIS_TX['CT_DEP_REN240'] / AIS_TX['Tx_REN240']) * 12
    AIS_TX['CT_DEP_REN367'] = (AIS_TX['CT_DEP_REN367'] / AIS_TX['Tx_REN367']) * 12
    AIS_TX['CT_DEP_REN634'] = (AIS_TX['CT_DEP_REN634'] / AIS_TX['Tx_REN674']) * 12
    AIS_TX['CT_DEP_TOT'] = AIS_TX[['CT_DEP_REN240', 'CT_DEP_REN367', 'CT_DEP_REN634']].sum(axis=1)
    AIS_TX['DEP_ACUM_TOT'] = AIS_TX[['DEP_ACUM_REN674', 'DEP_ACUM_REN367', 'DEP_ACUM_REN240']].sum(axis=1)
    AIS_TX['DEP_ACUM_LAUDO'] = AIS_TX['VL_DAC_UC'].div(AIS_TX['VL_VNR_UC']).fillna(0)

    
    LST_A1=['125','160','190','255','295','575','590','605','615']
    LST_A2=['160','340','575']
    AIS_TX['TST_AVAL_DEP']='OK'
    AIS_TX.loc[abs(AIS_TX['VL_VNR_UC'])<=0.01,
               'TST_AVAL_DEP'] = 'VNR ZERADO'
    AIS_TX.loc[(abs(AIS_TX['VL_VNR_UC'])<=0.01) & (AIS_TX['Cd_CONC']=='2'),
               'TST_AVAL_DEP'] = 'VNR ZERADO, SOBRA CONTÁBIL'
    AIS_TX.loc[((AIS_TX['DEP_ACUM_LAUDO']-AIS_TX['DEP_ACUM_TOT'])>0.0005) & 
               (abs(AIS_TX['VL_VNR_UC'])>=0.01),'TST_AVAL_DEP'] = 'VERIFICAR(-), SEM AJUSTE'
    AIS_TX.loc[((AIS_TX['DEP_ACUM_LAUDO']-AIS_TX['DEP_ACUM_TOT'])<-0.0005) & 
               (abs(AIS_TX['VL_VNR_UC'])>=0.01),'TST_AVAL_DEP'] = 'VERIFICAR(+), COM AJUSTE'
    AIS_TX.loc[(AIS_TX['VL_VU'].isnull()),
               'TST_AVAL_DEP'] = 'VERIFIQUE ATRIBUTOS DO ITEM, ARQUIVO INC'
    AIS_TX.loc[(AIS_TX['Nr_TUC'].isin(LST_A1)) & (AIS_TX['Nr_A1num']==0),
               'TST_AVAL_DEP']='VERIFIQUE ATRIBUTO A1 DO ITEM, ARQUIVO INC'
    AIS_TX.loc[(AIS_TX['Nr_TUC'].isin(LST_A2)) & (AIS_TX['Nr_A2num']==0),
               'TST_AVAL_DEP']='VERIFIQUE ATRIBUTO A2 DO ITEM, ARQUIVO INC'

    AIS_TX['VL_AJUSTE'] = (-AIS_TX['DEP_ACUM_LAUDO'] + AIS_TX['DEP_ACUM_TOT']) * AIS_TX['VL_VNR_UC']
    AIS_TX['CT_AJUSTE'] = round((-AIS_TX['DEP_ACUM_LAUDO'] + AIS_TX['DEP_ACUM_TOT']) / AIS_TX['Tx_REN674'] * 12, 0)
    ajuste = AIS_TX['TST_AVAL_DEP'].isin(['VNR ZERADO', 'OK'])
    vl_neg = AIS_TX['VL_AJUSTE'] < 0
    ct_neg = AIS_TX['CT_AJUSTE'] < 0
    AIS_TX.loc[ajuste | vl_neg, 'VL_AJUSTE'] = 0
    AIS_TX.loc[ajuste | ct_neg, 'CT_AJUSTE'] = 0
    AIS_TX = AIS_TX.fillna(0)
    AIS_TX.drop(columns=['Cd_CC','Nr_TUC','Nr_A1','Nr_A2','Dt_Imob','Dt_CNTB_AJST','VL_VOC','VL_VNR_UC',
                     'VL_DAC_UC','Dt_REF_DADOS','Nr_A1num','Nr_A2num','VAR_01','VAR_02','VAR_03',
                     'VAR_04','VAR_05','VL_DEP_ACUM','DT_IMB_BASE','DT1','Cd_CONC'],
                       inplace = True)

    return AIS_TX

def calc_bb(dir_arq_saida, dt_ini, dt_fim, con, Empresa, ano, st=None, opcao = False, nm_empr=None, data_ref = None):
    def modif(aaa):
        aaa.columns = ['Cd_CC', 'VL_SALDO_INIC']
        aaa['Cd_CC'] = aaa['Cd_CC'].astype(str)
        aaa['TP_SLD'] = 'BRT'
        aaa.loc[(aaa['Cd_CC'].str[5:7] == '02') | (aaa['Cd_CC'].str[5:7] == '05'),'TP_SLD'] = 'AMT'
        aaa.loc[aaa['TP_SLD'] == 'BRT', 'VL_SALDO_INIC'] = (aaa['VL_SALDO_INIC'])
        aaa.loc[aaa['TP_SLD'] == 'AMT', 'VL_SALDO_INIC'] = (aaa['VL_SALDO_INIC']) 
        return aaa
    
    if st: avl = st.progress(0, "Iniciando os cálculos...")

    PPBB = importar_dados("PPBB", con, Empresa, ['VL', 'QT'])
    Cd_EMP = sql.bsc_cd_aneel(Empresa)
    if 'Cd_ANEEL' not in PPBB.columns:
        PPBB['Cd_ANEEL'] = Cd_EMP

    PPBB = PPBB.rename(columns = {"CD_ODI":"Cd_ODI", "CD_SubODI":"Cd_SubODI"})

    if PPBB is not None:
        PPBB['Cd_CC'] = PPBB['Cd_CC'].str.replace(".", "")
    if st: avl.progress(10, "Importando bases...")
    
    if (st.session_state.dt_fim < bibDTAX.date.today()):
        PCBB = importar_dados("PCBB", con, Empresa, ['VL', 'QT'], 'FLG_ELIG', '')
    else:
        st.write("Em implantação")

    if st:
        avl.progress(18, "Buscando dados das baixas...")
    BAIXAS = importar_dados("BAIXAS", con, Empresa, ['VL', 'QT'], 'FLG_AJST_CTB', '0')

    OE_SDINIC = importar_dados("OE_SDINIC", con, Empresa, ['VL'], inibir=True)
    OE_REAV = importar_dados("OE_REAV", con, Empresa, ['VL'], inibir=True)
    OE_AJST = importar_dados("OE_AJST", con, Empresa, ['VL'], inibir=True)
    
    if((PPBB is None) or (PCBB is None) or (BAIXAS is None) or (OE_SDINIC is None) or 
       (OE_REAV is None) or (OE_AJST is None)):
        return None
    
    if st:
        avl.progress(25, "Construindo arquivo PCBB...")
    
    MEMO_SFF = pd.DataFrame()
    cd_ag2 = None

    if opcao:
        cd_ag2 = sql.bsc_cd_aneel(nm_empr)
        try:
            if len(PPBB['Cd_ANEEL'].drop_duplicates().to_list()) > 1:
                for i, cd in enumerate(PPBB['Cd_ANEEL'].drop_duplicates().to_list()):
                    dfpr = bsc_memo(PPBB[PPBB['Cd_ANEEL']==cd].iloc[0,-4], cd, cd_ag2, data_ref)
                    if len(MEMO_SFF) == 0:
                        MEMO_SFF = dfpr.copy()
                    else:
                        MEMO_SFF = MEMO_SFF.merge(dfpr, how='left', on = 'Nm_Item', suffixes=("_ori","_nv"))
                        MEMO_SFF['VL_MEMO_SGT'] = MEMO_SFF['VL_MEMO_SGT_ori'] + MEMO_SFF['VL_MEMO_SGT_nv']
                        MEMO_SFF = MEMO_SFF.drop(columns= ['VL_MEMO_SGT_ori','VL_MEMO_SGT_nv'])
            else:
                MEMO_SFF = bsc_memo(PPBB[PPBB['Cd_ANEEL']==cd].iloc[0,-4], cd, cd_ag2, data_ref)
        except:
            MEMO_SFF = bsc_memo(PPBB.iloc[0,-3], Cd_EMP, cd_ag2, data_ref)
    else:
        lst_cols = PPBB.columns.to_list()
        _ind = lst_cols.index("Dt_REF_DADOS") - len(lst_cols)
        MEMO_SFF = bsc_memo(PPBB.iloc[0,_ind], Cd_EMP)

    VL_AJST_AMT = 0
    VL_AJST_SB = 0
    dt_ARQ = sql.max_arq("OE_AGR", con, Empresa)
    if dt_ARQ:
        SQLq = f"""
                    SELECT 
                        *
                    FROM OE_AGR t1 WHERE dt_ARQ = {dt_ARQ};
               """
        OE_AGR = pd.read_sql(SQLq, con)
        OE_AGR = conv_num(OE_AGR)


    dt_ARQ = sql.max_arq("OE_AJS", con, Empresa)
    if dt_ARQ:
        SQLq = f"""
                    SELECT 
                        *
                    FROM OE_AJS t1 WHERE dt_ARQ = {dt_ARQ};
               """
        OE_AJST = pd.read_sql(SQLq, con)
        OE_AJST = conv_num(OE_AJST)

    
    if not OE_AJST.empty:
        if 'VL_SALDO_AJUSTE' not in OE_AJST.columns and 'VL_SALDO_AJS' in OE_AJST.columns:
            OE_AJST = OE_AJST.rename(columns={'VL_SALDO_AJS': 'VL_SALDO_AJUSTE'})

        OE_AJST['FLG_INC'] = OE_AJST['FLG_INC'].astype(str)
        OE_AJST['Cd_CC'] = OE_AJST['Cd_CC'].astype(str)

        flg_ajuste = OE_AJST['FLG_INC'].eq('0')
        cc_amortizacao = OE_AJST['Cd_CC'].str[5:7].isin(['02', '05'])

        ajustes_flg = OE_AJST.loc[flg_ajuste]
        ajustes_amt = OE_AJST.loc[flg_ajuste & cc_amortizacao, 'VL_SALDO_AJUSTE']
        ajustes_sb = OE_AJST.loc[flg_ajuste & ~cc_amortizacao, 'VL_SALDO_AJUSTE']

        if not ajustes_flg.empty:

            qtd_amt = len(OE_AJST.loc[cc_amortizacao])
            qtd_sb = len(OE_AJST.loc[~cc_amortizacao])

            if qtd_amt != qtd_sb:
                if st:
                    st.warning(
                                    "Verificar arquivo de ajustes, pois há ajustes de saldo bruto "
                                    "ou de amortização sem contrapartida."
                                )


            if not ajustes_amt.empty:
                VL_AJST_AMT += (ajustes_amt.sum())

            if not ajustes_sb.empty:
                VL_AJST_SB += (ajustes_sb.sum())

    try:
        OE_SI = OE_AGR.groupby(['Cd_CC'], dropna=False)[['VL_SLD_INI']].sum().reset_index()
        OE_RE = OE_AGR.groupby(['Cd_CC'], dropna=False)[['VL_SLD_REAV']].sum().reset_index()
    except:
        OE_SI = OE_SDINIC.groupby(['Cd_CC'], dropna=False)[['VL_SALDO_INIC']].sum().reset_index()
        if 'VL_SALDO_INIC' in OE_REAV.columns:
            OE_RE = OE_REAV.groupby(['Cd_CC'], dropna=False)[['VL_SALDO_INIC']].sum().reset_index()
        else:
            OE_RE = OE_REAV.groupby(['Cd_CC'], dropna=False)[['VL_SALDO']].sum().reset_index()

    OE_SI = modif(OE_SI)
    OE_RE = modif(OE_RE)
    OE_BR = abs(OE_SI[OE_SI['TP_SLD']=='BRT']['VL_SALDO_INIC'].sum() +
                OE_RE[OE_RE['TP_SLD']=='BRT']['VL_SALDO_INIC'].sum())
    OE_AMT = abs(OE_SI[OE_SI['TP_SLD']=='AMT']['VL_SALDO_INIC'].sum() +
                 OE_RE[OE_RE['TP_SLD']=='AMT']['VL_SALDO_INIC'].sum())

    REF_PP=PPBB[(PPBB['FLG_ELIG']=='1') & PPBB['Cd_CONC'].isin(['1', '3'])].groupby('Cd_Q5', dropna=False)[['VL_VOC','VL_VNR_UC',
               'VL_IAI_UC','VL_DAC_UC','VL_VMU_UC','VL_IAD_UC','VL_VBR_UC',
               'VL_100DEP_UC']].sum().reset_index()

    BASE_PP = {
                '(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)': REF_PP[REF_PP['Cd_Q5'].isin(['4.2', '5.2'])]['VL_VNR_UC'].sum(),
                '(2) Índice de Aproveitamento Integral': REF_PP[REF_PP['Cd_Q5'].isin(['4.2', '5.2'])]['VL_IAI_UC'].sum(),
                '(3) Obrigações Especiais Bruta': -(-OE_BR + VL_AJST_SB*0),
                '(4) Bens Totalmente Depreciados': REF_PP[REF_PP['Cd_Q5'].isin(['4.2', '5.2'])]['VL_100DEP_UC'].sum(),
                '(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)': REF_PP[REF_PP['Cd_Q5'].isin(['4.2', '5.2'])]['VL_VBR_UC'].sum(),
                '(6) Depreciação Acumulada': REF_PP[REF_PP['Cd_Q5'].isin(['4.2', '5.2'])]['VL_DAC_UC'].sum(),
                '(7) AIS Líquido (Valor de Mercado em Uso)': REF_PP[REF_PP['Cd_Q5'].isin(['4.2', '5.2'])]['VL_VMU_UC'].sum(),
                '(8) Índice de Aproveitamento Depreciado': REF_PP[REF_PP['Cd_Q5'].isin(['4.2', '5.2'])]['VL_IAD_UC'].sum(),
                '(9) Valor da Base de Remuneração (VBR)': REF_PP[REF_PP['Cd_Q5'].isin(['4.2', '5.2'])]['VL_VBR_UC'].sum(),
                '(10) Almoxarifado em Operação': MEMO_SFF[MEMO_SFF['Nm_Item'] == '(10) Almoxarifado em Operação'].iloc[-1, -1],
                '(11) Ativo Diferido': 0,
                '(12) Obrigações Especiais Liquida': -(-OE_BR + VL_AJST_SB*0 + OE_AMT + VL_AJST_AMT*0),
                '(13) Terrenos e Servidões': REF_PP[REF_PP['Cd_Q5'].isin(['1.1', '2.2'])]['VL_VBR_UC'].sum(),
            }

    BASE_PPg = {
                    '(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)': REF_PP[REF_PP['Cd_Q5'].isin(['4.1', '5.1'])]['VL_VNR_UC'].sum(),
                    '(2) Índice de Aproveitamento Integral': REF_PP[REF_PP['Cd_Q5'].isin(['4.1', '5.1'])]['VL_IAI_UC'].sum(),
                    '(3) Obrigações Especiais Bruta': 0,
                    '(4) Bens Totalmente Depreciados': REF_PP[REF_PP['Cd_Q5'].isin(['4.1', '5.1'])]['VL_100DEP_UC'].sum(),
                    '(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)': 0,
                    '(6) Depreciação Acumulada': REF_PP[REF_PP['Cd_Q5'].isin(['4.1', '5.1'])]['VL_DAC_UC'].sum(),
                    '(7) AIS Líquido (Valor de Mercado em Uso)': REF_PP[REF_PP['Cd_Q5'].isin(['4.1', '5.1'])]['VL_VMU_UC'].sum(),
                    '(8) Índice de Aproveitamento Depreciado': REF_PP[REF_PP['Cd_Q5'].isin(['4.1', '5.1'])]['VL_IAD_UC'].sum(),
                    '(9) Valor da Base de Remuneração (VBR)': REF_PP[REF_PP['Cd_Q5'].isin(['4.1', '5.1'])]['VL_VBR_UC'].sum(),
                    '(10) Almoxarifado em Operação': 0,
                    '(11) Ativo Diferido': 0,
                    '(12) Obrigações Especiais Liquida': 0,
                    '(13) Terrenos e Servidões': REF_PP[REF_PP['Cd_Q5'].isin(['2.1'])]['VL_VBR_UC'].sum(),
                }

    BASE_PPa = {
                    '(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)': REF_PP[REF_PP['Cd_Q5'].isin(['4.3', '5.3'])]['VL_VNR_UC'].sum(),
                    '(2) Índice de Aproveitamento Integral': REF_PP[REF_PP['Cd_Q5'].isin(['4.3', '5.3'])]['VL_IAI_UC'].sum(),
                    '(3) Obrigações Especiais Bruta': 0,
                    '(4) Bens Totalmente Depreciados': REF_PP[REF_PP['Cd_Q5'].isin(['4.3', '5.3'])]['VL_100DEP_UC'].sum(),
                    '(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)': 0,
                    '(6) Depreciação Acumulada': REF_PP[REF_PP['Cd_Q5'].isin(['4.3', '5.3'])]['VL_DAC_UC'].sum(),
                    '(7) AIS Líquido (Valor de Mercado em Uso)': REF_PP[REF_PP['Cd_Q5'].isin(['4.3', '5.3'])]['VL_VMU_UC'].sum(),
                    '(8) Índice de Aproveitamento Depreciado': REF_PP[REF_PP['Cd_Q5'].isin(['4.3', '5.3'])]['VL_IAD_UC'].sum(),
                    '(9) Valor da Base de Remuneração (VBR)': REF_PP[REF_PP['Cd_Q5'].isin(['4.3', '5.3'])]['VL_VBR_UC'].sum(),
                    '(10) Almoxarifado em Operação': 0,
                    '(11) Ativo Diferido': 0,
                    '(12) Obrigações Especiais Liquida': 0,
                    '(13) Terrenos e Servidões': REF_PP[REF_PP['Cd_Q5'].isin(['2.3'])]['VL_VBR_UC'].sum(),
                }

    BASE_PPc = {
                    '(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)': REF_PP[REF_PP['Cd_Q5'].isin(['4.4', '5.4'])]['VL_VNR_UC'].sum(),
                    '(2) Índice de Aproveitamento Integral': REF_PP[REF_PP['Cd_Q5'].isin(['4.4', '5.4'])]['VL_IAI_UC'].sum(),
                    '(3) Obrigações Especiais Bruta': 0,
                    '(4) Bens Totalmente Depreciados': REF_PP[REF_PP['Cd_Q5'].isin(['4.4', '5.4'])]['VL_100DEP_UC'].sum(),
                    '(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)': 0,
                    '(6) Depreciação Acumulada': REF_PP[REF_PP['Cd_Q5'].isin(['4.4', '5.4'])]['VL_DAC_UC'].sum(),
                    '(7) AIS Líquido (Valor de Mercado em Uso)': REF_PP[REF_PP['Cd_Q5'].isin(['4.4', '5.4'])]['VL_VMU_UC'].sum(),
                    '(8) Índice de Aproveitamento Depreciado': REF_PP[REF_PP['Cd_Q5'].isin(['4.4', '5.4'])]['VL_IAD_UC'].sum(),
                    '(9) Valor da Base de Remuneração (VBR)': REF_PP[REF_PP['Cd_Q5'].isin(['4.4', '5.4'])]['VL_VBR_UC'].sum(),
                    '(10) Almoxarifado em Operação': 0,
                    '(11) Ativo Diferido': 0,
                    '(12) Obrigações Especiais Liquida':0,
                    '(13) Terrenos e Servidões': REF_PP[REF_PP['Cd_Q5'].isin(['2.4'])]['VL_VBR_UC'].sum(),
                }

    BASE_PP['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)'] = (
        BASE_PP['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
        BASE_PP['(6) Depreciação Acumulada'] -
        BASE_PP['(8) Índice de Aproveitamento Depreciado'] + 
        BASE_PP['(10) Almoxarifado em Operação'] +
        BASE_PP['(11) Ativo Diferido'] - 
        BASE_PP['(12) Obrigações Especiais Liquida'] + 
        BASE_PP['(13) Terrenos e Servidões']
    )
    BASE_PP['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = (
        BASE_PP['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
        BASE_PP['(2) Índice de Aproveitamento Integral'] -
        BASE_PP['(3) Obrigações Especiais Bruta'] - 
        BASE_PP['(4) Bens Totalmente Depreciados'])
    
    BASE_PPg['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)'] = (
        BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
        BASE_PPg['(6) Depreciação Acumulada'] -
        BASE_PPg['(8) Índice de Aproveitamento Depreciado'] + 
        BASE_PPg['(10) Almoxarifado em Operação'] +
        BASE_PPg['(11) Ativo Diferido'] - 
        BASE_PPg['(12) Obrigações Especiais Liquida'] + 
        BASE_PPg['(13) Terrenos e Servidões']
    )
    BASE_PPg['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = (
        BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
        BASE_PPg['(2) Índice de Aproveitamento Integral'] -
        BASE_PPg['(3) Obrigações Especiais Bruta'] - 
        BASE_PPg['(4) Bens Totalmente Depreciados'])
    
    BASE_PPa['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)'] = (
        BASE_PPa['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
        BASE_PPa['(6) Depreciação Acumulada'] -
        BASE_PPa['(8) Índice de Aproveitamento Depreciado'] + 
        BASE_PPa['(10) Almoxarifado em Operação'] +
        BASE_PPa['(11) Ativo Diferido'] - 
        BASE_PPa['(12) Obrigações Especiais Liquida'] + 
        BASE_PPa['(13) Terrenos e Servidões']
    )
    BASE_PPa['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = (
        BASE_PPa['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
        BASE_PPa['(2) Índice de Aproveitamento Integral'] -
        BASE_PPa['(3) Obrigações Especiais Bruta'] - 
        BASE_PPa['(4) Bens Totalmente Depreciados'])
    
    BASE_PPc['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)'] = (
        BASE_PPc['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
        BASE_PPc['(6) Depreciação Acumulada'] -
        BASE_PPc['(8) Índice de Aproveitamento Depreciado'] + 
        BASE_PPc['(10) Almoxarifado em Operação'] +
        BASE_PPc['(11) Ativo Diferido'] - 
        BASE_PPc['(12) Obrigações Especiais Liquida'] + 
        BASE_PPc['(13) Terrenos e Servidões']
    )
    BASE_PPc['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = (
        BASE_PPc['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] - 
        BASE_PPc['(2) Índice de Aproveitamento Integral'] -
        BASE_PPc['(3) Obrigações Especiais Bruta'] - 
        BASE_PPc['(4) Bens Totalmente Depreciados'])

    if st:
        avl.progress(40, "Testando ponto de partida, calculando baixas aplicadas pela avaliadora...")
    df_PP = pd.DataFrame.from_dict(BASE_PP, orient='index').reset_index()
    df_PP.columns = ['Nm_Item','VL_SDI_PPD']
    df_PPg = pd.DataFrame.from_dict(BASE_PPg, orient='index').reset_index()
    df_PPg.columns = ['Nm_Item','VL_SDI_PPG']
    df_PP = df_PP.merge(df_PPg, how='left', on ='Nm_Item')
    df_PPa = pd.DataFrame.from_dict(BASE_PPa, orient='index').reset_index()
    df_PPa.columns = ['Nm_Item','VL_SDI_PPA']
    df_PP = df_PP.merge(df_PPa, how='left', on ='Nm_Item')
    df_PPc = pd.DataFrame.from_dict(BASE_PPc, orient='index').reset_index()
    df_PPc.columns = ['Nm_Item','VL_SDI_PPC']
    df_PP = df_PP.merge(df_PPc, how='left', on ='Nm_Item')

    df_PP = df_PP.merge(MEMO_SFF, how = 'left', on='Nm_Item')
    df_PP['DIF'] = df_PP['VL_SDI_PPD'] + df_PP['VL_SDI_PPG'] - df_PP['VL_MEMO_SGT']

    BBcmp = PPBB.merge(PCBB, how='left', on='Id_SEQ_PP').rename(
        columns = { 'FLG_ELIG_x' : 'FLG_ELIG', 
                    'Cd_CONC_x' : 'Cd_CONC',
                    'VL_VNR_UC_x' : 'VL_VNR_UC_ANT', 
                    'VL_IAI_UC_x' : 'VL_IAI_UC_ANT', 
                    'VL_DAC_UC_x' : 'VL_DAC_UC_ANT', 
                    'VL_VMU_UC_x' : 'VL_VMU_UC_ANT', 
                    'VL_IAD_UC_x' : 'VL_IAD_UC_ANT', 
                    'VL_VBR_UC_x' : 'VL_VBR_UC_ANT', 
                    'VL_100DEP_UC_x' : 'VL_100DEP_UC_ANT', 
                    'Dt_REF_DADOS_x' : 'Dt_REF_DADOS_ANT', 
                    'VL_VNR_UC_y' : 'VL_VNR_UC_AT', 
                    'VL_IAI_UC_y' : 'VL_IAI_UC_AT', 
                    'VL_DAC_UC_y' : 'VL_DAC_UC_AT', 
                    'VL_VMU_UC_y' : 'VL_VMU_UC_AT', 
                    'VL_IAD_UC_y' : 'VL_IAD_UC_AT', 
                    'VL_VBR_UC_y' : 'VL_VBR_UC_AT', 
                    'VL_100DEP_UC_y' : 'VL_100DEP_UC_AT', 
                    'Dt_REF_DADOS_y' : 'Dt_REF_DADOS_AT', 
                    'FLG_ELIG_y' : 'FLG_ELIG_AT', 
                    'Cd_CONC_y' : 'Cd_CONC_AT', })

    BBcmp.loc[BBcmp['FLG_ELIG_AT'] == '', 'FLG_ELIG_AT'] = BBcmp['FLG_ELIG']

    if st:
        avl.progress(45, "Comparando arquivo de baixas com a execução da avaliadora...")
    BBcmp['Dt_REF_DADOS_AT'] = pd.to_datetime(BBcmp['Dt_REF_DADOS_AT'], errors='coerce')
    BBcmp['Dt_REF_DADOS_ANT'] = pd.to_datetime(BBcmp['Dt_REF_DADOS_ANT'], errors='coerce')
    BBcmp['Dt_REF_DADOS_AT'] = BBcmp['Dt_REF_DADOS_AT'].ffill()
    BBcmp['Dt_REF_DADOS_ANT'] = BBcmp['Dt_REF_DADOS_ANT'].ffill()
    BBcmp['Qtd_AIS'] = BBcmp['Qtd_AIS'].fillna(0,)
    BBcmp['Qtd_AISa'] = BBcmp['Qtd_AISa'].fillna(0)
    BBcmp['Cd_UND_AIS'] = BBcmp['Cd_UND_AIS'].fillna('ND')
    BBcmp['QTD_BXS_INF'] = BBcmp['Qtd_AIS'] - BBcmp['Qtd_AISa']

    QTD_BXinf=BBcmp.groupby(['Nr_TUC','Cd_UND_AIS'], 
                    dropna=False)[['Qtd_AIS','Qtd_AISa','QTD_BXS_INF']].sum().reset_index()
    
    BXS = BAIXAS.copy()
    try:
        BXS['Cd_UND_AIS'] = BXS['Cd_UND_AIS'].fillna('ND')
    except:
        BXS['Cd_UND_AIS'] = BXS['Cd_UNID_AIS'].fillna('ND')
        BXS.drop(columns = 'Cd_UNID_AIS', inplace=True)

    BXS['Dt_Imob']=BXS['Dt_Imob'].replace('#N/D','1970/01/01').replace('00/01/1900','1970/01/01')
    BXS['Dt_Imob']=pd.to_datetime(BXS['Dt_Imob'], errors='coerce')
    try:
        BXS['Dt_BX']=pd.to_datetime(BXS['Dt_BX'], errors='coerce')
    except:
        BXS['Dt_BX']=pd.to_datetime(BXS['Dt_Baixa'], errors='coerce')
        BXS.drop(columns = 'Dt_Baixa', inplace=True)

    BXS['Dt_Imob'] = BXS['Dt_Imob'].ffill()
    BXS['Dt_BX'] = BXS['Dt_BX'].ffill()
    BXS['Qtd_INI'] = BXS['Qtd_INI'].fillna(0)
    BXS['Qtd_FIN'] = BXS['Qtd_FIN'].fillna(0)
    BXS['Cd_UND_AIS'] = BXS['Cd_UND_AIS'].fillna('ND')

    lst_cmp = BXS.columns.to_list()
    if not ('FLG_PER' in lst_cmp):
        BXS['FLG_PER'] = '0'
        BXS.loc[BXS['Dt_Imob'] > pd.Timestamp(dt_ini), 'FLG_PER'] = '1'
    if not ('FLG_ANT' in lst_cmp):
        BXS['FLG_ANT'] = '0'
    if not ('FLG_AJST_CTB' in lst_cmp):
        BXS['FLG_AJST_CTB'] = '0'

    BXS_CTB = BXS[(BXS['FLG_PER'] == '0') & 
                  (BXS['FLG_ANT'] == '0') &
                  (BXS['FLG_AJST_CTB'] == '0')].groupby(['Nr_TUC','Cd_UND_AIS'],
                                        dropna=False)[['Qtd_INI','Qtd_FIN']].sum().reset_index()
    BXS_CTB_INC = BXS[(BXS['FLG_PER'] == '1') & 
                      (BXS['FLG_ANT'] == '0') &
                      (BXS['FLG_AJST_CTB'] == '0')].groupby(['Nr_TUC','Cd_UND_AIS'],
                                        dropna=False)[['Qtd_INI','Qtd_FIN']].sum().reset_index()

    TST_BX = QTD_BXinf.merge(BXS_CTB, how='outer',on=['Nr_TUC','Cd_UND_AIS'])
    TST_BX.columns = ['Nr_TUC','Cd_UND_AIS','QTD_AIS_PP','QTD_AIS_PC',
                      'QTD_BXS_APL','QTD_INI_BXS','QTD_FIM_BXS']
    TST_BX = TST_BX.fillna(0)
    TST_BX['QTD_BXS_CTB'] = TST_BX['QTD_INI_BXS']-TST_BX['QTD_FIM_BXS']

    TST_AX = TST_BX.groupby(['Nr_TUC'], 
                            dropna=False)[['QTD_BXS_APL','QTD_BXS_CTB']].sum().reset_index()
    
    criterio = np.isclose(TST_BX['QTD_BXS_APL'].abs(),
                        TST_BX['QTD_BXS_CTB'].abs(),
                        rtol=0.01)
    TST_AX['TST_IG'] = TST_AX['QTD_BXS_APL'] - TST_AX['QTD_BXS_CTB']
    TST_AX.drop(columns=['QTD_BXS_APL','QTD_BXS_CTB'], inplace = True)

    TST_BX=TST_BX.merge(TST_AX, how='left', on='Nr_TUC')
    TST_BX['TST_CNST'] = 'OK'
    TST_BX.loc[(abs(TST_BX['QTD_BXS_APL']-TST_BX['QTD_BXS_CTB']) > 0.1) & 
               (abs(TST_BX['TST_IG']) < 0.1),
               'TST_CNST'] = 'AVALIAR UNIDADES INFORMADAS, ND SIGNIFICA UNIDADE AUSENTE NO PPBB'
    TST_BX.loc[((TST_BX['QTD_BXS_CTB']-TST_BX['QTD_BXS_APL']) > 0.1) & criterio,
               'TST_CNST'] = 'AVALIAR QUANTIDADES BAIXADAS'

    TST_BX.drop(columns=['TST_IG'], inplace = True)

    BXS_CTB_INC.columns = ['Nr_TUC','Cd_UND_AIS','Qtd_INI_INC','Qtd_FIM_INC']
    BXS_CTB_INC['QTD_BXS_CTB_INC'] = BXS_CTB_INC['Qtd_INI_INC'] - BXS_CTB_INC['Qtd_FIM_INC']
    TST_BX = TST_BX.merge(BXS_CTB_INC, how='outer', on=['Nr_TUC','Cd_UND_AIS'])
    TST_BX = TST_BX.fillna(0)
    ipca = busca_ipca()
    BBcmp['VL_VNR_CA_BX']=0
    BBcmp.loc[BBcmp['Qtd_AIS'] > 0,
              'VL_VNR_CA_BX'] = BBcmp['VL_VNR_UC_ANT'] / BBcmp['Qtd_AIS'] * BBcmp['QTD_BXS_INF']

    try:
        Nr_IPCA_AT = ipca[ipca['Dt_REF'] == BBcmp.loc[0,'Dt_REF_DADOS_AT'].strftime("%Y-%m-01")].iloc[0,-1]
        Nr_IPCA_ANT = ipca[ipca['Dt_REF'] == BBcmp.loc[0,'Dt_REF_DADOS_ANT'].strftime("%Y-%m-01")].iloc[0,-1]
    except:
        Nr_IPCA_ANT = ipca.loc[ipca['Dt_REF'] == (pd.to_datetime(st.session_state.dt_ini) - pd.DateOffset(months=1)), ipca.columns[-1]]
        Nr_IPCA_ANT = Nr_IPCA_ANT.iloc[0] if not Nr_IPCA_ANT.empty else ipca.iloc[-1, -1] 
        Nr_IPCA_AT  = ipca.loc[ipca['Dt_REF'] == pd.to_datetime(st.session_state.dt_fim).replace(day=1), ipca.columns[-1]]
        Nr_IPCA_AT  = Nr_IPCA_AT .iloc[0] if not Nr_IPCA_AT .empty else ipca.iloc[-1, -1]

    BBcmp['Nr_IPCA_ANT'] = Nr_IPCA_ANT
    BBcmp['Nr_IPCA_AT'] = Nr_IPCA_AT
    BBcmp['FA_AT'] = Nr_IPCA_AT / Nr_IPCA_ANT

    BBcmp['VL_VNR_CA_BX_LAUDO'] = BBcmp['VL_VNR_UC_ANT']-BBcmp['VL_VNR_UC_AT'] / BBcmp['FA_AT']
    BBcmp['TST_VL_BX']='OK'
    BBcmp.loc[(abs(BBcmp['VL_VNR_CA_BX_LAUDO'] - BBcmp['VL_VNR_CA_BX']) > 0.1) &
              (BBcmp['VL_VNR_CA_BX'] != 0),
              'TST_VL_BX'] = 'JUSTIFIQUE O VALOR DA BAIXA'
    BBcmp['VL_VNR_UC_ANT_MOV'] = (BBcmp['VL_VNR_UC_ANT'] - BBcmp['VL_VNR_CA_BX']) * BBcmp['FA_AT']
    BBcmp['TST_VL_VNR'] = 'OK'
    BBcmp.loc[(abs(BBcmp['VL_VNR_UC_ANT_MOV'] - BBcmp['VL_VNR_UC_AT']) > 0.1) &
              (BBcmp['VL_VNR_CA_BX'] == 0),
              'TST_VL_VNR'] = 'VERIFIQUE A ATUALIZAÇÃO'
    
    if st:
        avl.progress(80, "Analisando a depreciação acumulada apresentada...")

    AIS_TX = BBcmp[['Nr_TI','Nr_TUC','Nr_A1','Nr_A2']].copy().drop_duplicates()
    AIS_TX = ass_tx_dep(AIS_TX, st)
    if st:
        avl.progress(85, "Associando as taxas de depreciação aos ativos...")
    
    BBcmp = BBcmp.merge(AIS_TX, on = ['Nr_TUC','Nr_A1','Nr_A2'], how='left')

    BBcmp['CTS_PER'] = (BBcmp['Dt_REF_DADOS_AT'].dt.year - 
                         BBcmp['Dt_REF_DADOS_ANT'].dt.year) * 12 + \
                        (BBcmp['Dt_REF_DADOS_AT'].dt.month - 
                         BBcmp['Dt_REF_DADOS_ANT'].dt.month)

    BBcmp['DEP_ACM_ANT'] = (BBcmp['VL_DAC_UC_ANT'] / BBcmp['VL_VNR_UC_ANT']).where(
                            BBcmp['VL_VNR_UC_ANT'] != 0, 0)
    BBcmp['DEP_ACM_PER'] = (BBcmp['CTS_PER'] * BBcmp['Tx_REN674']) / 12
    BBcmp['DEP_ACM_CALC'] = (BBcmp['DEP_ACM_ANT'] + BBcmp['DEP_ACM_PER']).where(
                            (BBcmp['DEP_ACM_ANT'] + BBcmp['DEP_ACM_PER']) < 1, 1)
    BBcmp['DEP_ACM_LAUDO'] = (BBcmp['VL_DAC_UC_AT'] / BBcmp['VL_VNR_UC_AT']).where(
                              BBcmp['VL_VNR_UC_AT'] != 0, 0)
    if st:
        avl.progress(90, "Efetuando testes da depreciação...")

    BBcmp['TST_AVAL_DEP']='OK'
    BBcmp.loc[abs(BBcmp['VL_VNR_UC_AT']) <=0.01 , 'TST_AVAL_DEP'] = 'VNR ZERADO'
    BBcmp.loc[((BBcmp['DEP_ACM_LAUDO'] - BBcmp['DEP_ACM_CALC']) > 0.0001) 
               & (abs(BBcmp['VL_VNR_UC_AT']) >= 0.01), 'TST_AVAL_DEP'] = 'VERIFICAR(-)'
    BBcmp.loc[((BBcmp['DEP_ACM_LAUDO'] - BBcmp['DEP_ACM_CALC']) < -0.0001) 
               & (abs(BBcmp['VL_VNR_UC_AT']) >= 0.01), 'TST_AVAL_DEP'] = 'VERIFICAR(+)'
    BBcmp.loc[(BBcmp['VL_VU'].isnull()),
               'TST_AVAL_DEP'] = 'VERIFIQUE ATRIBUTOS DO ITEM, ARQUIVO PPBB'
    BBcmp.loc[(BBcmp['Nr_TUC'].isin(['125','160','190','255','295','575','590','605','615'])) 
               & (BBcmp['Nr_A1']=='0'), 
              'TST_AVAL_DEP'] = 'VERIFIQUE ATRIBUTO A1 DO ITEM, ARQUIVO PPBB'
    BBcmp.loc[(BBcmp['Nr_TUC'].isin(['160','340','575'])) 
               & (BBcmp['Nr_A2']=='0'), 
              'TST_AVAL_DEP'] = 'VERIFIQUE ATRIBUTO A2 DO ITEM, ARQUIVO PPBB'
    BBcmp['TST_AVAL_ARQ_PP']='NO'
    BBcmp.loc[~BBcmp['FLG_ELIG'].isin(['0', '1']),
              'TST_AVAL_ARQ_PP'] = 'FLG_ELIG DEVE SER: ELEGÍVEL=1 OU INELEGÍVEL=0'
    BBcmp.loc[~BBcmp['Cd_CONC'].isin(['1', '2', '3']),
              'TST_AVAL_ARQ_PP'] = 'Cd_CONC DEVE SER: Conciliado=1; Sobra Contábil=2; Sobra física=3'
    BBcmp.loc[BBcmp['Nr_TUC'].isin(['205', '555']) & (BBcmp['VL_DEP_ACUM'] != 0),
              'TST_AVAL_ARQ_PP'] = 'AVALIAR VL_DEP_ACUM DECLARADO'

    if st:
        avl.progress(95, "Salvando resultados...")

    CHAVES_BASE = [
        "(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)",
        "(2) Índice de Aproveitamento Integral",
        "(3) Obrigações Especiais Bruta",
        "(4) Bens Totalmente Depreciados",
        "(6) Depreciação Acumulada",
        "(7) AIS Líquido (Valor de Mercado em Uso)",
        "(8) Índice de Aproveitamento Depreciado",
        "(9) Valor da Base de Remuneração (VBR)",
        "(10) Almoxarifado em Operação",
        "(11) Ativo Diferido",
        "(12) Obrigações Especiais Liquida",
        "(13) Terrenos e Servidões",
    ]

    IMP_BB = {chave: 0 for chave in CHAVES_BASE}
    def at_tbl(resumo_dict, filename, con):
        if sql.existe_tabela(filename, con):
            df_resumo = pd.read_sql(f"SELECT * FROM {filename}", con)
            for _, row in df_resumo.iterrows():
                resumo_dict[row[0]] = row[1] if isinstance(row[1], (int, float)) else 0

    at_tbl(IMP_BB, "RES_BB_QDTAR_SFF", con)

    REF_PP=BBcmp[(BBcmp['FLG_ELIG_AT'] =='1') & (BBcmp['Cd_CONC_AT'].isin(['1','3']))].groupby('Cd_Q5',
                dropna=False)[['VL_VOCa','VL_VNR_UC_AT','VL_IAI_UC_AT','VL_DAC_UC_AT',
                'VL_VMU_UC_AT','VL_IAD_UC_AT','VL_VBR_UC_AT',
                'VL_100DEP_UC_AT']].sum().reset_index()
    REF_PP.columns=['Cd_Q5','VL_VOC','VL_VNR_UC','VL_IAI_UC','VL_DAC_UC','VL_VMU_UC',
                    'VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC']

    BASE_PP['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] = REF_PP[(REF_PP['Cd_Q5']=='4.2') | (REF_PP['Cd_Q5']=='5.2')]['VL_VNR_UC'].sum()
    BASE_PP['(2) Índice de Aproveitamento Integral'] = REF_PP[(REF_PP['Cd_Q5']=='4.2') | (REF_PP['Cd_Q5']=='5.2') ]['VL_IAI_UC'].sum()
    BASE_PP['(4) Bens Totalmente Depreciados'] = REF_PP[(REF_PP['Cd_Q5']=='4.2') | (REF_PP['Cd_Q5']=='5.2')]['VL_100DEP_UC'].sum()
    BASE_PP['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = BASE_PP['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)']-BASE_PP['(2) Índice de Aproveitamento Integral']-BASE_PP['(3) Obrigações Especiais Bruta']-BASE_PP['(4) Bens Totalmente Depreciados']
    BASE_PP['(6) Depreciação Acumulada'] = REF_PP[(REF_PP['Cd_Q5']=='4.2') | (REF_PP['Cd_Q5']=='5.2')]['VL_DAC_UC'].sum()
    BASE_PP['(7) AIS Líquido (Valor de Mercado em Uso)'] = REF_PP[(REF_PP['Cd_Q5']=='4.2') | (REF_PP['Cd_Q5']=='5.2')]['VL_VMU_UC'].sum()
    BASE_PP['(8) Índice de Aproveitamento Depreciado'] = REF_PP[(REF_PP['Cd_Q5']=='4.2') | (REF_PP['Cd_Q5']=='5.2')]['VL_IAD_UC'].sum()
    BASE_PP['(9) Valor da Base de Remuneração (VBR)'] = REF_PP[(REF_PP['Cd_Q5']=='4.2') | (REF_PP['Cd_Q5']=='5.2')]['VL_VBR_UC'].sum()
    BASE_PP['(10) Almoxarifado em Operação'] = 0
    BASE_PP['(11) Ativo Diferido'] = 0
    BASE_PP['(13) Terrenos e Servidões'] = REF_PP[(REF_PP['Cd_Q5']=='1.1') | (REF_PP['Cd_Q5']=='2.2')]['VL_VBR_UC'].sum()
    BASE_PP['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)']=BASE_PP['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)']-BASE_PP['(6) Depreciação Acumulada']-BASE_PP['(8) Índice de Aproveitamento Depreciado']+BASE_PP['(10) Almoxarifado em Operação']+BASE_PP['(11) Ativo Diferido']-BASE_PP['(12) Obrigações Especiais Liquida']+BASE_PP['(13) Terrenos e Servidões']

    BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] = REF_PP[(REF_PP['Cd_Q5']=='4.1') | (REF_PP['Cd_Q5']=='5.1')]['VL_VNR_UC'].sum()
    BASE_PPg['(2) Índice de Aproveitamento Integral'] = REF_PP[(REF_PP['Cd_Q5']=='4.1') | (REF_PP['Cd_Q5']=='5.1') ]['VL_IAI_UC'].sum()
    BASE_PPg['(4) Bens Totalmente Depreciados'] = REF_PP[(REF_PP['Cd_Q5']=='4.1') | (REF_PP['Cd_Q5']=='5.1')]['VL_100DEP_UC'].sum()
    BASE_PPg['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)']-BASE_PPg['(2) Índice de Aproveitamento Integral']-BASE_PPg['(3) Obrigações Especiais Bruta']-BASE_PPg['(4) Bens Totalmente Depreciados']
    BASE_PPg['(6) Depreciação Acumulada'] = REF_PP[(REF_PP['Cd_Q5']=='4.1') | (REF_PP['Cd_Q5']=='5.1')]['VL_DAC_UC'].sum()
    BASE_PPg['(7) AIS Líquido (Valor de Mercado em Uso)'] = REF_PP[(REF_PP['Cd_Q5']=='4.1') | (REF_PP['Cd_Q5']=='5.1')]['VL_VMU_UC'].sum()
    BASE_PPg['(8) Índice de Aproveitamento Depreciado'] = REF_PP[(REF_PP['Cd_Q5']=='4.1') | (REF_PP['Cd_Q5']=='5.1')]['VL_IAD_UC'].sum()
    BASE_PPg['(9) Valor da Base de Remuneração (VBR)'] = REF_PP[(REF_PP['Cd_Q5']=='4.1') | (REF_PP['Cd_Q5']=='5.1')]['VL_VBR_UC'].sum()
    BASE_PPg['(10) Almoxarifado em Operação'] = 0
    BASE_PPg['(11) Ativo Diferido'] = 0
    BASE_PPg['(13) Terrenos e Servidões'] = REF_PP[(REF_PP['Cd_Q5']=='2.1')]['VL_VBR_UC'].sum()
    BASE_PPg['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)']=BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)']-BASE_PPg['(6) Depreciação Acumulada']-BASE_PPg['(8) Índice de Aproveitamento Depreciado']+BASE_PPg['(10) Almoxarifado em Operação']+BASE_PPg['(11) Ativo Diferido']-BASE_PPg['(12) Obrigações Especiais Liquida']+BASE_PPg['(13) Terrenos e Servidões']

    df = pd.DataFrame.from_dict(BASE_PP, orient="index", columns=['Valor']).reset_index()
    df.columns = ['Item','VL_SALDO_D']

    dfg = pd.DataFrame.from_dict(BASE_PPg, orient="index", columns=['Valor']).reset_index()
    dfg.columns = ['Item','VL_SALDO_G']

    df = df.merge(dfg, how='left', on = "Item")

    BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] = REF_PP[(REF_PP['Cd_Q5']=='4.3') | (REF_PP['Cd_Q5']=='5.3')]['VL_VNR_UC'].sum()
    BASE_PPg['(2) Índice de Aproveitamento Integral'] = REF_PP[(REF_PP['Cd_Q5']=='4.3') | (REF_PP['Cd_Q5']=='5.3') ]['VL_IAI_UC'].sum()
    BASE_PPg['(4) Bens Totalmente Depreciados'] = REF_PP[(REF_PP['Cd_Q5']=='4.3') | (REF_PP['Cd_Q5']=='5.3')]['VL_100DEP_UC'].sum()
    BASE_PPg['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)']-BASE_PPg['(2) Índice de Aproveitamento Integral']-BASE_PPg['(3) Obrigações Especiais Bruta']-BASE_PPg['(4) Bens Totalmente Depreciados']
    BASE_PPg['(6) Depreciação Acumulada'] = REF_PP[(REF_PP['Cd_Q5']=='4.3') | (REF_PP['Cd_Q5']=='5.3')]['VL_DAC_UC'].sum()
    BASE_PPg['(7) AIS Líquido (Valor de Mercado em Uso)'] = REF_PP[(REF_PP['Cd_Q5']=='4.3') | (REF_PP['Cd_Q5']=='5.3')]['VL_VMU_UC'].sum()
    BASE_PPg['(8) Índice de Aproveitamento Depreciado'] = REF_PP[(REF_PP['Cd_Q5']=='4.3') | (REF_PP['Cd_Q5']=='5.3')]['VL_IAD_UC'].sum()
    BASE_PPg['(9) Valor da Base de Remuneração (VBR)'] = REF_PP[(REF_PP['Cd_Q5']=='4.3') | (REF_PP['Cd_Q5']=='5.3')]['VL_VBR_UC'].sum()
    BASE_PPg['(10) Almoxarifado em Operação'] = 0
    BASE_PPg['(11) Ativo Diferido'] = 0
    BASE_PPg['(13) Terrenos e Servidões'] = REF_PP[(REF_PP['Cd_Q5']=='2.3')]['VL_VBR_UC'].sum()
    BASE_PPg['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)']=BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)']-BASE_PPg['(6) Depreciação Acumulada']-BASE_PPg['(8) Índice de Aproveitamento Depreciado']+BASE_PPg['(10) Almoxarifado em Operação']+BASE_PPg['(11) Ativo Diferido']-BASE_PPg['(12) Obrigações Especiais Liquida']+BASE_PPg['(13) Terrenos e Servidões']

    dfg = pd.DataFrame.from_dict(BASE_PPg, orient="index", columns=['Valor']).reset_index()
    dfg.columns = ['Item','VL_SALDO_A']

    df = df.merge(dfg, how='left', on = "Item")

    BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] = REF_PP[(REF_PP['Cd_Q5']=='4.4') | (REF_PP['Cd_Q5']=='5.4')]['VL_VNR_UC'].sum()
    BASE_PPg['(2) Índice de Aproveitamento Integral'] = REF_PP[(REF_PP['Cd_Q5']=='4.4') | (REF_PP['Cd_Q5']=='5.4') ]['VL_IAI_UC'].sum()
    BASE_PPg['(4) Bens Totalmente Depreciados'] = REF_PP[(REF_PP['Cd_Q5']=='4.4') | (REF_PP['Cd_Q5']=='5.4')]['VL_100DEP_UC'].sum()
    BASE_PPg['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)']-BASE_PPg['(2) Índice de Aproveitamento Integral']-BASE_PPg['(3) Obrigações Especiais Bruta']-BASE_PPg['(4) Bens Totalmente Depreciados']
    BASE_PPg['(6) Depreciação Acumulada'] = REF_PP[(REF_PP['Cd_Q5']=='4.4') | (REF_PP['Cd_Q5']=='5.4')]['VL_DAC_UC'].sum()
    BASE_PPg['(7) AIS Líquido (Valor de Mercado em Uso)'] = REF_PP[(REF_PP['Cd_Q5']=='4.4') | (REF_PP['Cd_Q5']=='5.4')]['VL_VMU_UC'].sum()
    BASE_PPg['(8) Índice de Aproveitamento Depreciado'] = REF_PP[(REF_PP['Cd_Q5']=='4.4') | (REF_PP['Cd_Q5']=='5.4')]['VL_IAD_UC'].sum()
    BASE_PPg['(9) Valor da Base de Remuneração (VBR)'] = REF_PP[(REF_PP['Cd_Q5']=='4.4') | (REF_PP['Cd_Q5']=='5.4')]['VL_VBR_UC'].sum()
    BASE_PPg['(10) Almoxarifado em Operação'] = 0
    BASE_PPg['(11) Ativo Diferido'] = 0
    BASE_PPg['(13) Terrenos e Servidões'] = REF_PP[(REF_PP['Cd_Q5']=='2.4')]['VL_VBR_UC'].sum()
    BASE_PPg['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)']=BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)']-BASE_PPg['(6) Depreciação Acumulada']-BASE_PPg['(8) Índice de Aproveitamento Depreciado']+BASE_PPg['(10) Almoxarifado em Operação']+BASE_PPg['(11) Ativo Diferido']-BASE_PPg['(12) Obrigações Especiais Liquida']+BASE_PPg['(13) Terrenos e Servidões']

    dfg = pd.DataFrame.from_dict(BASE_PPg, orient="index", columns=['Valor']).reset_index()
    dfg.columns = ['Item','VL_SALDO_C']

    df = df.merge(dfg, how='left', on = "Item")

    for j in [6,7]:
        for i in [1,2,3,4]:
            BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)'] = REF_PP[(REF_PP['Cd_Q5']==f'{j}.{i}')]['VL_VNR_UC'].sum()
            BASE_PPg['(2) Índice de Aproveitamento Integral'] = REF_PP[(REF_PP['Cd_Q5']==f'{j}.{i}') ]['VL_IAI_UC'].sum()
            BASE_PPg['(4) Bens Totalmente Depreciados'] = REF_PP[(REF_PP['Cd_Q5']==f'{j}.{i}')]['VL_100DEP_UC'].sum()
            BASE_PPg['(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)'] = BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)']-BASE_PPg['(2) Índice de Aproveitamento Integral']-BASE_PPg['(3) Obrigações Especiais Bruta']-BASE_PPg['(4) Bens Totalmente Depreciados']
            BASE_PPg['(6) Depreciação Acumulada'] = REF_PP[(REF_PP['Cd_Q5']==f'{j}.{i}')]['VL_DAC_UC'].sum()
            BASE_PPg['(7) AIS Líquido (Valor de Mercado em Uso)'] = REF_PP[(REF_PP['Cd_Q5']==f'{j}.{i}')]['VL_VMU_UC'].sum()
            BASE_PPg['(8) Índice de Aproveitamento Depreciado'] = REF_PP[(REF_PP['Cd_Q5']==f'{j}.{i}')]['VL_IAD_UC'].sum()
            BASE_PPg['(9) Valor da Base de Remuneração (VBR)'] = REF_PP[(REF_PP['Cd_Q5']==f'{j}.{i}')]['VL_VBR_UC'].sum()
            BASE_PPg['(10) Almoxarifado em Operação'] = 0
            BASE_PPg['(11) Ativo Diferido'] = 0
            BASE_PPg['(13) Terrenos e Servidões'] = REF_PP[(REF_PP['Cd_Q5']==f'{j}.{i}')]['VL_VBR_UC'].sum()
            BASE_PPg['(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)']=BASE_PPg['(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)']-BASE_PPg['(6) Depreciação Acumulada']-BASE_PPg['(8) Índice de Aproveitamento Depreciado']+BASE_PPg['(10) Almoxarifado em Operação']+BASE_PPg['(11) Ativo Diferido']-BASE_PPg['(12) Obrigações Especiais Liquida']+BASE_PPg['(13) Terrenos e Servidões']

            dfg = pd.DataFrame.from_dict(BASE_PPg, orient="index", columns=['Valor']).reset_index()
            Nm = 'D' if i==2 else 'G' if i==1 else 'A' if i==3 else 'C'
            TP = 'VEICULO' if j==6 else 'MOVEIS_UTENSILIOS'
            dfg.columns = ['Item',f'VL_{TP}_{Nm}']

            df = df.merge(dfg, how='left', on = "Item")
        
    df.to_csv(f"{dir_arq_saida}\\tbl_resumo_BB_{Cd_EMP}.csv", header=False, index=False, sep="|", decimal=',', encoding="Latin-1")
    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf"{dir_arq_saida}\\tbl_resumo_BB_{Cd_EMP}.csv",
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    df.to_sql("RES_BB_QDTAR_SFF", con, if_exists='replace', index=True)

    df_PP.to_sql("ANL_PP", con, if_exists='replace', index=False)
    BBcmp.to_sql("ANL_BB_CMP", con, if_exists='replace', index=False)
    TST_BX.to_sql("ANL_TST_BX", con, if_exists='replace', index=False)
    df.to_sql("RESUMO_BB", con, if_exists='replace')

    if st:
        avl.progress(100, "Finalizado")
            
    return ""

def ass_tx_dep(AIS_TX, st=None):
    
    #Vamos fazer algumas suposições caso não tenha sido declarados alguns atributos relevantes
    AIS_TX['Nr_A1x'] = AIS_TX['Nr_A1']
    AIS_TX['Nr_A2x'] = AIS_TX['Nr_A2']
    AIS_TX.loc[(AIS_TX['Nr_A1'].isnull() | (AIS_TX['Nr_A1'].isin(['0','00',0])))  & (AIS_TX['Nr_TUC'].isin(['125','130'])), 'Nr_A1'] = '02'
    AIS_TX.loc[(AIS_TX['Nr_A1'].isnull() | (AIS_TX['Nr_A1'].isin(['0','00',0]))) & (AIS_TX['Nr_TUC'] == '215'), 'Nr_A1'] = '09'
    AIS_TX.loc[(AIS_TX['Nr_A1'].isnull() | (AIS_TX['Nr_A1'].isin(['0','00',0])))  & (AIS_TX['Nr_TUC'].isin(['255','295'])), 'Nr_A1'] = '01'
    AIS_TX.loc[(AIS_TX['Nr_A1'].isnull() | (AIS_TX['Nr_A1'].isin(['0','00',0])))  & (AIS_TX['Nr_TUC'].isin(['205','555'])), 'Nr_A1'] = '00'

    AIS_TX.loc[(AIS_TX['Nr_A1'].isnull() | (AIS_TX['Nr_A1'].isin(['0','00',0])))  & (AIS_TX['Nr_TUC'] == '190'), 'Nr_A1'] = '01'
    AIS_TX.loc[(AIS_TX['Nr_A1'].isnull() | (AIS_TX['Nr_A1'].isin(['0','00',0]))) & (AIS_TX['Nr_TUC'] == '190') &
               AIS_TX['Nr_TI'].isin(['40','41','42','43','44','93','96','30','31','32','35','36','37',
                                     '50','51','52','55','56','57','65','66','67']), 'Nr_A1'] = '02'
    

    AIS_TX = AIS_TX[['Nr_TUC','Nr_A1','Nr_A2','Nr_A1x','Nr_A2x']]
    AIS_TX = AIS_TX.drop_duplicates()
    
    for nm in ['Nr_A1', 'Nr_A2']:
        if (AIS_TX[nm].dtype == 'object') and (nm in AIS_TX.columns):
            AIS_TX[f'{nm}num'] = pd.to_numeric(AIS_TX[nm].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')
        else:
            AIS_TX[f'{nm}num'] = AIS_TX[f'{nm}']
            #AIS_TX[f'{nm}'] = AIS_TX[f'{nm}'].astype(str)

    # Inicializando Ide_TUC_A1 com Nr_TUC
    AIS_TX['Ide_TUC_A1'] = AIS_TX['Nr_TUC']
    
    lst_TUC_TEN = ['125', '130', '215', '255']
    TEN = AIS_TX['Nr_TUC'].isin(lst_TUC_TEN)
    AIS_TX.loc[TEN, 'Ide_TUC_A1'] = AIS_TX['Nr_TUC'] + '.' + AIS_TX['Nr_A1'].str.zfill(2)
    lst_TUC_TEN = ['160', '340', '575']
    TEN_maior_69 = AIS_TX['Nr_TUC'].isin(lst_TUC_TEN) & (AIS_TX['Nr_A2num'] >= 69)
    TEN_menor_69 = AIS_TX['Nr_TUC'].isin(lst_TUC_TEN) & (AIS_TX['Nr_A2num'] < 69)
    AIS_TX.loc[TEN_maior_69, 'Ide_TUC_A1'] = AIS_TX['Nr_TUC'] + '>=69'
    AIS_TX.loc[TEN_menor_69, 'Ide_TUC_A1'] = AIS_TX['Nr_TUC'] + '<69'
    uc190_1 = (AIS_TX['Nr_TUC'] == '190') & (AIS_TX['Nr_A1num'] == 1)
    uc190_2 = (AIS_TX['Nr_TUC'] == '190') & (AIS_TX['Nr_A1num'] == 2)
    AIS_TX.loc[uc190_1, 'Ide_TUC_A1'] = '190>=69'
    AIS_TX.loc[uc190_2, 'Ide_TUC_A1'] = '190<69'

    map_UC_A1 = {
                                ('190', 3): '190.03',
                                ('615', 3): '615.03',
                                ('160', 5): '160.05',
                                ('575', 11): '575.11',
                                ('575', 12): '575.12',
                                ('575', 13): '575.13',
                                ('575', 20): '575.20',
                                ('295', 1): '295.01',
                                ('295', 11): '295.11',
                                ('295', 13): '295.13',
                                ('295', 16): '295.16',
                                ('295', 17): '295.17',
                                ('295', 18): '295.18',
                                ('605', 1): '605.01',
                                ('605', 10): '605.10',
                                ('605', 15): '605.15',
                                ('590', 1): '590.01',
                                ('590', 5): '590.05',
                                ('590', 10): '590.10',
                                ('590', 15): '590.15',
                                ('565', 3): '565.03',
                                ('565', 4): '565.04',
                                ('565', 5): '565.05',
                                ('575', 11): '575.11',
                                ('575', 12): '575.12',
                                ('575', 13): '575.13',
                                ('575', 20): '575.20'
                            }
    AIS_TX['Ide_TUC_A1'] = AIS_TX.apply(lambda row: map_UC_A1.get(
                                        (row['Nr_TUC'], row['Nr_A1num']), row['Ide_TUC_A1']), 
                                         axis=1)
    

    tbl_tx_dep=pd.read_csv('tabelas\\tbl_tx_dep.csv',sep="|",encoding="Latin-1", dtype=str)
    list_campos=['VL_VU','Tx_REN674','Tx_REN367','Tx_REN240']
    for cmp in list_campos:
        tbl_tx_dep[cmp]=pd.to_numeric(tbl_tx_dep[cmp], errors='coerce')
    
    AIS_TX.drop(columns=['Nr_A1num','Nr_A2num'], inplace = True)
    AIS_TX = AIS_TX.merge(tbl_tx_dep, on=['Ide_TUC_A1'], how='left')
    AIS_TX = AIS_TX.drop(columns = ['Nr_A1','Nr_A2'])
    AIS_TX = AIS_TX.rename(columns = {'Nr_A1x' : 'Nr_A1', 'Nr_A2x' : 'Nr_A2'})

    return AIS_TX

def enc_outliers(df, grupo, valor):
    """
    Adiciona uma coluna 'FLG_OUTLIER' ao DataFrame para identificar outliers por grupo.
    
    Parameters:
    - df: DataFrame
    - grupo: Coluna usada para agrupar (ex.: 'Nr_TI')
    - valor: Coluna numérica para análise (ex.: 'VL_VOC')
    
    Returns:
    - DataFrame com a coluna 'FLG_OUTLIER'.
    """
    # Criar uma cópia para evitar modificar o original
    df = df.copy()
    
    # Função para calcular limites de outliers para cada grupo
    def det_flags(grupo):
        Q1 = grupo[valor].quantile(0.25)
        Q3 = grupo[valor].quantile(0.75)
        IQR = Q3 - Q1
        lower_fence = Q1 - 3 * IQR
        upper_fence = Q3 + 3 * IQR
        grupo['FLG_OUTLIER'] = (grupo[valor] < lower_fence) | (grupo[valor] > upper_fence)
        return grupo
    
    df = df.groupby(grupo).apply(det_flags)
    return df

def sorteio(
            df, 
            coluna_valor, 
            coluna_identificador, 
            n, seed=None, 
            lista_extra=None, 
            sorteados = None, 
            st = None, 
            lista_bloqueio=[]
            ):

    def escolher_item(grupo, lista_bloqueio):
        sorteado = grupo.sample(1)
        idx = sorteado.index[0]
        identificador = sorteado["Cd_SubODI"].iloc[0]
        if identificador not in lista_bloqueio:
            return sorteado

        posicoes = grupo.index.tolist()
        pos_atual = posicoes.index(idx)

        if pos_atual < (len(posicoes) - 1):
            for prox_pos in range(pos_atual + 1, len(posicoes)):
                prox_idx = posicoes[prox_pos]
                prox_id = grupo.loc[prox_idx, "Cd_SubODI"]
                if prox_id not in lista_bloqueio:
                    return grupo.loc[[prox_idx]]
        else:
            for ant_pos in range(pos_atual - 1, 0, -1):
                ant_idx = posicoes[ant_pos]
                ant_id = grupo.loc[ant_idx, "Cd_SubODI"]
                if ant_id not in lista_bloqueio:
                    return grupo.loc[[ant_idx]]
        
        st.warning(f"Falhou no {identificador}, possível único elemento.")
        return pd.DataFrame(columns = [
                                            'Cd_SubODI',
                                            'Nr_TI',
                                            'VL_VOC',
                                            'Limite_Inferior',
                                            'Limite_Superior'
                                        ])

    if seed is not None:
        np.random.seed(seed)

    df = df.sort_values(by=coluna_valor).reset_index(drop=True)
    resultados = []
   
    df["Intervalo"], bins = pd.qcut(df[coluna_valor], q=int(n), labels=False, duplicates="drop", retbins=True)
    df.loc[df["Intervalo"] == 0, "Limite_Inferior"] = 0
    df.loc[df["Intervalo"] == 0, "Limite_Superior"] = df.loc[df["Intervalo"] == 0, coluna_valor]
    
    for i in range(len(bins) - 1):
        df.loc[df["Intervalo"] == i, "Limite_Inferior"] = bins[i]
        df.loc[df["Intervalo"] == i, "Limite_Superior"] = bins[i + 1]
    
    if sorteados != None:
        amostra = df[df['Cd_SubODI'].isin(sorteados)].copy()
        amostra = amostra[coluna_identificador + [coluna_valor, "Limite_Inferior", "Limite_Superior"]].reset_index(drop=True)
        return amostra
    
    amostra = (df.groupby("Intervalo", group_keys=False).apply(lambda x: escolher_item(x, lista_bloqueio)))
    
    if lista_extra:
        extras = df[df['Cd_SubODI'].isin(lista_extra)].copy()
    else:
        extras = pd.DataFrame()

    resultados.append(amostra[coluna_identificador + [coluna_valor, "Limite_Inferior", "Limite_Superior"]].reset_index(drop=True))
    if len(extras):
        resultados.append(extras[coluna_identificador + [coluna_valor, "Limite_Inferior", "Limite_Superior"]].reset_index(drop=True))

    return pd.concat(resultados).reset_index(drop=True)

def resumo(con, st=None):
    import pandas as pd
    Empresa = st.session_state.nm_empr
    if sql.existe_tabela('ANL_BB_CMP', con):
        SQLq_PC = """
            SELECT
                Id_SEQ_PP AS Id_SEQ,
                Cd_CICLO,
                Id_AIS,
                Cd_PAT_LAUDO,
                Cd_ODI,
                Cd_SubODI,
                Cd_CC,
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
                COD_ITEM,
                Txt_DESC_TECN,
                Qtd_AISa AS Qtd_AIS,
                Cd_UND_AIS,
                VL_VOCa AS VL_VOC,
                COALESCE(VL_VOCa * DEP_ACM_CALC, 0) AS VL_DEP_ACUM,
                Dt_Lcmto AS Dt_Imob,
                VL_VNR_UC_AT AS VL_VNR_UC,
                VL_IAI_UC_AT AS VL_IAI_UC,
                VL_DAC_UC_AT AS VL_DAC_UC,
                VL_VMU_UC_AT AS VL_VMU_UC,
                VL_IAD_UC_AT AS VL_IAD_UC,
                VL_VBR_UC_AT AS VL_VBR_UC,
                VL_100DEP_UC_AT AS VL_100DEP_UC,
                Pct_IAI AS Pct_IA,
                FLG_ELIG_AT AS FLG_ELIG,
                Cd_CONC_AT AS Cd_CONC,
                Cd_Q5,
                Cd_Q7,
                Dt_REF_DADOS_AT AS Dt_REF_DADOS
            FROM ANL_BB_CMP
        """
        df_PC = sql.imp_tbl_forma_000("ANL_BB_CMP", SQLq=SQLq_PC, con=con)

        SQLq_PB = """
            SELECT
                Id_SEQ_PP AS Id_SEQ,
                Cd_CICLO,
                Id_AIS,
                Cd_PAT_LAUDO,
                Cd_ODI,
                Cd_SubODI,
                Cd_CC,
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
                COD_ITEM,
                Txt_DESC_TECN,
                Qtd_AIS,
                Cd_UND_AIS,
                VL_VOC,
                VL_DEP_ACUM,
                Dt_Lcmto AS Dt_Imob,
                VL_VNR_UC_ANT AS VL_VNR_UC,
                VL_IAI_UC_ANT AS VL_IAI_UC,
                VL_DAC_UC_ANT AS VL_DAC_UC,
                VL_VMU_UC_ANT AS VL_VMU_UC,
                VL_IAD_UC_ANT AS VL_IAD_UC,
                VL_VBR_UC_ANT AS VL_VBR_UC,
                VL_100DEP_UC_ANT AS VL_100DEP_UC,
                coalesce(1 - VL_IAI_UC_ANT/VL_VNR_UC_ANT,0) AS Pct_IA,
                FLG_ELIG,
                Cd_CONC,
                Cd_Q5,
                Cd_Q7,
                Dt_REF_DADOS_AT AS Dt_REF_DADOS
            FROM ANL_BB_CMP
        """
        df_PB = sql.imp_tbl_forma_000("ANL_BB_CMP", SQLq=SQLq_PB, con=con)

    # Verifica se tabela ANL_INCREMENTAL existe
    if (st.session_state.dt_fim < dt1.date.today()):
        try:
            SQLq_INC = """
                SELECT
                    Id_SEQ_INC AS Id_SEQ,
                    Id_AIS,
                    Cd_Patrim AS Cd_PAT_LAUDO,
                    Cd_DIG_INC,
                    Cd_ODI,
                    Cd_SubODI,
                    Cd_CC,
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
                    COD_ITEM,
                    Txt_DESC_TECN,
                    Qtd_AIS,
                    Cd_UND_AIS,
                    VL_VOC,
                    VL_DEP_ACUM,
                    Dt_Imob,
                    VL_VNR_UC,
                    VL_IAI_UC,
                    VL_DAC_UC,
                    VL_VMU_UC,
                    VL_IAD_UC,
                    VL_VBR_UC,
                    VL_100DEP_UC,
                    COALESCE(VL_IAI_UC / NULLIF(VL_VNR_UC, 0), 0) AS Pct_IA,
                    FLG_ELIG,
                    Cd_CONC,
                    Cd_Q5,
                    '' AS Cd_Q7,
                    Dt_REF_DADOS
                FROM INCR WHERE dt_ARQ = ?
            """
            df_INC = sql.imp_tbl_forma_001("INCR", SQLq=SQLq_INC, con=con, st=st, Empresa=Empresa)
        except:
            SQLq_INC = """
                SELECT
                    Id_SEQ_INC AS Id_SEQ,
                    Id_AIS,
                    Cd_Patrim AS Cd_PAT_LAUDO,
                    Cd_DIG_INC,
                    Cd_ODI,
                    Cd_SubODI,
                    Cd_CC,
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
                    COD_ITEM,
                    Txt_DESC_TECN,
                    Qtd_AIS,
                    Cd_UND_AIS,
                    VL_VOC,
                    VL_DEP_ACUM,
                    Dt_Imob,
                    VL_VNR_UC,
                    VL_IAI_UC,
                    VL_DAC_UC,
                    VL_VMU_UC,
                    VL_IAD_UC,
                    VL_VBR_UC,
                    VL_100DEP_UC,
                    COALESCE(VL_IAI_UC / NULLIF(VL_VNR_UC, 0), 0) AS Pct_IA,
                    FLG_ELIG,
                    Cd_CONC,
                    '' AS Cd_Q7,
                    Dt_REF_DADOS
                FROM INCR WHERE dt_ARQ = ?
            """
            df_INC = sql.imp_tbl_forma_001("INCR", SQLq=SQLq_INC, con=con, st=st, Empresa=Empresa)

            df_Cd1A = pd.read_csv(
                                    f"tabelas/tbl_CNTB.csv",
                                    sep="|",
                                    decimal=",",
                                    encoding="latin-1",
                                    header=0,
                                    usecols = ['Cd_CC','Cd_Q1A'],
                                    dtype={
                                                "Cd_CC": str,
                                                "Cd_Q1A": str,
                                            } 
                                )
            df_INC = df_INC.merge(df_Cd1A, how = 'left', on= 'Cd_CC')
            df_INC = df_INC.rename(columns={"Cd_Q1A":"Cd_Q5",
                                            })

        for n in ['VL_VNR_UC','VL_VOC','VL_DEP_ACUM','Qtd_AIS','VL_IAI_UC','VL_DAC_UC','VL_VMU_UC',
                  'VL_IAD_UC','VL_VBR_UC','VL_100DEP_UC',]:
            if (n in df_INC.columns) and (df_INC[n].dtype == 'object'):
                df_INC[n] = pd.to_numeric(df_INC[n].astype(str).str.replace(',','.'), 
                                                            errors='coerce',
                                                            downcast='float')
    else:
        
        ano = st.session_state.dt_fim.year
        caminho = os.path.join(f"{st.session_state.tra_dir}/INC_ANLS", f"provINCR_{Empresa}_{ano}.csv")
        if os.path.isfile(caminho):
            with st.spinner("Lendo"):
                df_INC = pd.read_csv(
                                    f"{st.session_state.tra_dir}/INC_ANLS/provINCR_{Empresa}_{ano}.csv",
                                    sep="|",
                                    decimal=",",
                                    encoding="latin-1",
                                    header=0,
                                    dtype={
                                                "Cd_CC": str,
                                                "Cd_ODI": str,
                                                "Cd_SubODI": str,
                                                "Cd_Patrim": str,
                                                "COD_ITEM": str,
                                                "Cd_ODD": str,
                                                "Cd_ODI_ENG": str,
                                                "Cd_TP_AVAL": str,
                                                "Cd_SISBASE": str,
                                                "Cd_ABCC": str,
                                                "Cd_NumFIS": str,
                                            } 
                                )
                df_Cd1A = pd.read_csv(
                                    f"tabelas/tbl_CNTB.csv",
                                    sep="|",
                                    decimal=",",
                                    encoding="latin-1",
                                    header=0,
                                    usecols = ['Cd_CC','Cd_Q1A'],
                                    dtype={
                                                "Cd_CC": str,
                                                "Cd_Q1A": str,
                                            } 
                                )
                df_INC = df_INC.merge(df_Cd1A, how = 'left', on= 'Cd_CC')
                df_INC = df_INC.rename(columns={"Id_SEQ_INC" : "Id_SEQ", "Cd_Q1A":"Cd_Q5",
                                                "Cd_Patrim" : "Cd_PAT_LAUDO"})
                df_INC['Cd_Q7'] = ''
                df_INC = df_INC.drop(columns=['Pct_OE_ROS'])

    # Une PC com Incremental
    df_TOT = pd.concat([df_PC, df_INC], ignore_index=True)
    
    # Conversão para tipos eficientes
    df_TOT['Cd_CONC'] = df_TOT['Cd_CONC'].astype('category')
    df_TOT['FLG_ELIG'] = df_TOT['FLG_ELIG'].astype('category')
    df_PB['Cd_CONC'] = df_PB['Cd_CONC'].astype('category')
    df_PB['FLG_ELIG'] = df_PB['FLG_ELIG'].astype('category')

    # Agrupamento filtrado por condição
    col_valores = ['Qtd_AIS','VL_VNR_UC', 'VL_IAI_UC', 'VL_DAC_UC', 'VL_VMU_UC','VL_IAD_UC', 'VL_VBR_UC', 'VL_100DEP_UC']
    df_TOT['Cd_UND_AIS'] = df_TOT['Cd_UND_AIS'].str.upper()

    df_ANL = (
                df_TOT.query("Cd_CONC == '1' and FLG_ELIG == '1'")
                .groupby(['Cd_UND_AIS', 'Cd_Q5', 'Nr_TI', 'Nr_TUC'], dropna=False, as_index=False)[col_valores]
                .sum()
            )

    df_PB['Cd_UND_AIS'] = df_PB['Cd_UND_AIS'].str.upper()
    df_INT = (
                df_PB.query("Cd_CONC == '1' and FLG_ELIG == '1'")
                .groupby(['Cd_UND_AIS', 'Cd_Q5', 'Nr_TI', 'Nr_TUC'], dropna=False, as_index=False)[col_valores]
                .sum()
            )

    # Junção única com indicador
    df_COMB = df_INT.merge(df_ANL, on=['Cd_Q5', 'Nr_TI', 'Nr_TUC', 'Cd_UND_AIS'], how='outer', suffixes=('_ANT', '_AT'), indicator=True)
    for n in df_COMB.columns:
        if n[:2] == "VL": df_COMB[n] = df_COMB[n].fillna(0)
    map_res = {
                'both' : 'Presente em ambas',
                'left_only' : 'Somente na anterior, baixado',
                'right_only' : 'Somente na nova, adicionado',
              }
    df_COMB['OBS_CONC_BASE_ANT_x_ATUAL'] = df_COMB['_merge'].map(map_res)
    df_COMB = df_COMB.drop(columns = '_merge')
    df_COMB = df_COMB.drop_duplicates()
    df_COMB = df_COMB.sort_values(by = ['Cd_Q5','Nr_TI', 'Nr_TUC', 'Cd_UND_AIS'])

    df_COMB.to_sql("ANL_RESULTADO_TOTAL", con, if_exists='replace', index=False)

    return "OK"

def calc_taxa(AIS_TX, con, PLPT, st=None):
    # Carregar tabela de taxas de depreciação
    tbl_tx_dep = pd.read_csv('tabelas/tbl_tx_dep.csv', sep="|", encoding="Latin-1", dtype=str)

    if PLPT == 'PLPT':
        try:
            AIS_TX = AIS_TX[AIS_TX['Nr_TI'].isin(['40','41','93','96'])][['Cd_CC', 'Nr_TUC', 'Nr_A1','Nr_A2','Dt_Imob','VL_VOC','VL_VOC_MV','Vl_Dep_Acum',
                        'VL_DEP_ACUM_MV']] 
        except:
                AIS_TX = AIS_TX[AIS_TX['Nr_TI'].isin(['40','41','93','96'])][['Cd_CC', 'Nr_TUC', 'Nr_A1','Nr_A2','Dt_Imob','VL_VOC','VL_VOC_MV','VL_DEP_ACUM',
                        'VL_DEP_ACUM_MV']]   
    else:
        try:
            AIS_TX = AIS_TX[['Cd_CC', 'Nr_TUC', 'Nr_A1','Nr_A2','Dt_Imob','VL_VOC','VL_VOC_MV','Vl_Dep_Acum',
                        'VL_DEP_ACUM_MV']]
        except:
            AIS_TX = AIS_TX[['Cd_CC', 'Nr_TUC', 'Nr_A1','Nr_A2','Dt_Imob','VL_VOC','VL_VOC_MV','VL_DEP_ACUM',
                    'VL_DEP_ACUM_MV']]

    
    # Converter colunas numéricas
    list_campos = ['VL_VU', 'Tx_REN674', 'Tx_REN367', 'Tx_REN240']
    tbl_tx_dep[list_campos] = tbl_tx_dep[list_campos].apply(pd.to_numeric, errors='coerce')

    # Carregar tabela auxiliar de análise contábil
    tbl_cntb_anl = pd.read_csv('tabelas/tbl_CNTB.csv', sep="|", encoding="Latin-1", dtype=str)

    # Carregar tabela auxiliar de equivalencia plano de contas antigo atual
    # Vamos substituir as contas antigas, pela sua equivalente, caso tenha
    tbl_cntb_eqv = pd.read_csv('tabelas/tbl_CNTB_NVMDL.csv', sep="|", encoding="Latin-1", dtype=str)
    map_dic = tbl_cntb_eqv.set_index('Cd_CCa')['Cd_CCn'].to_dict()
    AIS_TX['Cd_CC'] = AIS_TX['Cd_CC'].map(map_dic).fillna(AIS_TX['Cd_CC'])

    # Ajustar formato de 'Cd_CC' e fazer merge com tabela contábil
    AIS_TX['Cd_CC'] = AIS_TX['Cd_CC'].str[:9]
    AIS_TX = AIS_TX.merge(tbl_cntb_anl, on='Cd_CC', how='left')
    
    # Listar códigos únicos de Cd_CC onde Nm_ATVD é nulo
    cd_cc_faltantes = AIS_TX.loc[AIS_TX['Nm_ATVD'].isnull(), 'Cd_CC'].drop_duplicates().to_list()
    
    if len(cd_cc_faltantes)>0:
        if st:
            if st: st.warning(f"Verifique se o grupo de contas a seguir são de depreciação ou se falta alguma no cálculo: {cd_cc_faltantes}.")
        
    for nm in list_campos:
        if (tbl_tx_dep[nm].dtype == 'object') and (nm in tbl_tx_dep.columns):
            tbl_tx_dep[nm] = pd.to_numeric(tbl_tx_dep[nm].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')
    for nm in ['Nr_A1', 'Nr_A2']:
        if (AIS_TX[nm].dtype == 'object') and (nm in AIS_TX.columns):
            AIS_TX[f'{nm}num'] = pd.to_numeric(AIS_TX[nm].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')
        else:
            AIS_TX[f'{nm}num'] = AIS_TX[f'{nm}']
            AIS_TX[f'{nm}'] = AIS_TX[f'{nm}'].astype(str)

    AIS_TX = AIS_TX.rename(columns = {'Vl_Dep_Acum' : 'VL_DEP_ACUM'})
    
    for nm in ['VL_VOC','VL_DEP_ACUM','VL_VOC_MV','VL_DEP_ACUM_MV']:
        if (AIS_TX[nm].dtype == 'object') and (nm in AIS_TX.columns):
            AIS_TX[nm] = pd.to_numeric(AIS_TX[nm].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')

    # Inicializando Ide_TUC_A1 com Nr_TUC
    AIS_TX['Ide_TUC_A1'] = AIS_TX['Nr_TUC']
    map_UC_A1 = {
                                ('190', 3): '190.03',
                                ('615', 3): '615.03',
                                ('160', 5): '160.05',
                                ('575', 11): '575.11',
                                ('575', 12): '575.12',
                                ('575', 13): '575.13',
                                ('575', 20): '575.20',
                                ('295', 1): '295.01',
                                ('295', 11): '295.11',
                                ('295', 13): '295.13',
                                ('295', 16): '295.16',
                                ('295', 17): '295.17',
                                ('295', 18): '295.18',
                                ('605', 1): '605.01',
                                ('605', 10): '605.10',
                                ('605', 15): '605.15',
                                ('590', 1): '590.01',
                                ('590', 5): '590.05',
                                ('590', 10): '590.10',
                                ('590', 15): '590.15',
                                ('565', 3): '565.03',
                                ('565', 4): '565.04',
                                ('565', 5): '565.05'
                            }
    
    lst_TUC_TEN = ['125', '130', '215', '255']
    TEN = AIS_TX['Nr_TUC'].isin(lst_TUC_TEN)
    AIS_TX.loc[TEN, 'Ide_TUC_A1'] = AIS_TX['Nr_TUC'] + '.' + AIS_TX['Nr_A1'].str.zfill(2)
    lst_TUC_TEN = ['160', '340', '575']
    TEN_maior_69 = AIS_TX['Nr_TUC'].isin(lst_TUC_TEN) & (AIS_TX['Nr_A2num'] >= 69)
    TEN_menor_69 = AIS_TX['Nr_TUC'].isin(lst_TUC_TEN) & (AIS_TX['Nr_A2num'] < 69)
    AIS_TX.loc[TEN_maior_69, 'Ide_TUC_A1'] = AIS_TX['Nr_TUC'] + '>=69'
    AIS_TX.loc[TEN_menor_69, 'Ide_TUC_A1'] = AIS_TX['Nr_TUC'] + '<69'
    # Tratamento para Nr_TUC == '190'
    uc190_1 = (AIS_TX['Nr_TUC'] == '190') & (AIS_TX['Nr_A1num'] == 1)
    uc190_2 = (AIS_TX['Nr_TUC'] == '190') & (AIS_TX['Nr_A1num'] == 2)
    AIS_TX.loc[uc190_1, 'Ide_TUC_A1'] = '190>=69'
    AIS_TX.loc[uc190_2, 'Ide_TUC_A1'] = '190<69'

    AIS_TX['Ide_TUC_A1'] = AIS_TX.apply(lambda row: map_UC_A1.get(
                                        (row['Nr_TUC'], row['Nr_A1num']), row['Ide_TUC_A1']), 
                                        axis=1)
    AIS_TX['Dt_Imob']=pd.to_datetime(AIS_TX['Dt_Imob'], errors='coerce')
    AIS_TX['VL_100_DEP']=0
    
    AIS_TX.loc[((abs(AIS_TX['VL_VOC'].fillna(0) + AIS_TX['VL_VOC_MV'].fillna(0))-
                abs(AIS_TX['VL_DEP_ACUM'].fillna(0) + AIS_TX['VL_DEP_ACUM_MV'].fillna(0)))
                <.1) , 'VL_100_DEP']= AIS_TX['VL_VOC'].fillna(0) + AIS_TX['VL_VOC_MV'].fillna(0)

    AIS_TX = AIS_TX.merge(tbl_tx_dep, on='Ide_TUC_A1', how='left')
    AIS_TX['VL_ULT_MES'] = (AIS_TX['VL_VOC'].fillna(0) + AIS_TX['VL_VOC_MV'].fillna(0)).abs() * AIS_TX['Tx_REN674'] / 12
    AIS_TX.loc[AIS_TX['VL_100_DEP'] > 0, 'VL_ULT_MES'] = 0

    # Agrupamento por atividade, classe, TUC e Ide_TUC_A1
    AIS_TX_UC = AIS_TX.groupby(['Nm_ATVD', 'Nm_CLASS', 
                        'Nr_TUC', 'Ide_TUC_A1'])[['VL_VOC', 'VL_VOC_MV', 
                                                'VL_100_DEP', 'VL_ULT_MES']].sum()
    if PLPT == 'PLPT':
        AIS_TX_UC.to_sql("AIS_TX_UC_PLPT", con, if_exists='replace', index=True)
    elif PLPT == 'SOTI':
        AIS_TX_UC.to_sql("AIS_TX_UC_TI_BAR", con, if_exists='replace', index=True)
    elif PLPT == 'VNR':
        AIS_TX_UC.to_sql("AIS_TX_UC_VNR", con, if_exists='replace', index=True)
    else:
        AIS_TX_UC.to_sql("AIS_TX_UC", con, if_exists='replace', index=True)

    # Filtragem e agrupamento excluindo Nr_TUC 555 e 205
    AIS_TX_ATV = (AIS_TX[~AIS_TX['Nr_TUC'].isin(['555', '205'])]
                .groupby(['Nm_ATVD', 'Nm_CLASS'])[['VL_VOC', 'VL_VOC_MV', 'VL_100_DEP', 'VL_ULT_MES']]
                .sum())

    # Cálculo da taxa média, evitando divisão por zero
    denominador = (AIS_TX_ATV['VL_VOC'] + AIS_TX_ATV['VL_VOC_MV'] - AIS_TX_ATV['VL_100_DEP']).replace(0, pd.NA)
    AIS_TX_ATV['TX_MED'] = 12 * AIS_TX_ATV['VL_ULT_MES'] / denominador
    if PLPT == 'PLPT':
        AIS_TX_ATV.to_sql("AIS_TX_ATV_PLPT", con, if_exists='replace', index=True)
    elif PLPT == 'SOTI':
        AIS_TX_ATV.to_sql("AIS_TX_ATV_TI_BAR", con, if_exists='replace', index=True)
    elif PLPT == 'VNR':
        AIS_TX_ATV.to_sql("AIS_TX_ATV_VNR", con, if_exists='replace', index=True)
    else:
        AIS_TX_ATV.to_sql("AIS_TX_ATV", con, if_exists='replace', index=True)
    return AIS_TX_ATV

def calc_oe_nv(dir_arq_saida, dt_ini_proc, dt_fim_proc, TX_AMT_OE, con, Empresa, ano, st=None):
    if st: pgr = st.progress(0, "Iniciando os cálculos")
    if st: n1 = st.info(f"""Buscando os dados fornecidos pela empresa.""", icon = "1️⃣")

    OE_AJST = sql.imp_tbl_forma_001("OE_AJS", con=con, st=st, Empresa=Empresa)
    OE_AJST = conv_num(OE_AJST)
    OE_AGR = sql.imp_tbl_forma_001("OE_AGR", con=con, st=st, Empresa=Empresa)
    OE_AGR = conv_num(OE_AGR)
    OE_AGR.loc[OE_AGR['TP_OE'].fillna('').str.upper().str.startswith('OUT'), 'TP_OE'] = 'OUTROS'

    OE_BMP = pd.read_csv("tabelas/Bd_OE.csv",sep="|")
    Cd_EMP = sql.bsc_cd_aneel(Empresa)
    OE_BMP = OE_BMP[OE_BMP['IdeAgente']==Cd_EMP]
    OE_BMP['Dt_REF'] = pd.to_datetime(OE_BMP['AnmCompetencia'].astype(str) + '01', format='%Y%m%d')
    OE_BMP['Cd_CC'] = OE_BMP['NumConta'].astype(str)
    OE_BMP = OE_BMP[['Dt_REF','Cd_CC','DscConta','VlrDebito','VlrCredito','VlrSaldo']].copy().rename(
        columns={'DscConta': 'Dsc_Conta', 'VlrDebito': 'VL_DEB_BMP', 'VlrCredito' : 'VL_CRED_BMP',
                 'VlrSaldo' : 'VL_SLD_BMP'})

    OE_BMP = OE_BMP[(OE_BMP['Dt_REF'].dt.date >= st.session_state.dt_ini) & (OE_BMP['Dt_REF'].dt.date <= st.session_state.dt_fim)]
    lst_itens = [a for a in OE_AGR.columns if (a[-2:-1].upper() == '.') or (a[-1:].upper() == 'n')]
    for an in lst_itens:
        if an in OE_AGR.columns:
            OE_AGR = OE_AGR.drop(columns=an)
    lst_columns = [a for a in OE_AGR.columns if (a[:4].upper() == 'VL_M')]

    lst_datas = [pd.to_datetime(st.session_state.dt_ini) + relativedelta(months=(int(a[7:])-1)) for a in lst_columns]
    
    OE_MANUAL = OE_AGR.groupby('Cd_CC', dropna=True)[lst_columns].sum().reset_index()
    OE_MANUAL.columns = ['Cd_CC'] + lst_datas
    OE_MANUAL = pd.melt(
                            OE_MANUAL, 
                            id_vars=['Cd_CC'],
                            var_name='Dt_REF',
                            value_name='VL_LCMTO_MANUAL'
                        )
    OE_MANUAL['Dt_REF'] = pd.to_datetime(OE_MANUAL['Dt_REF'])
    OE_COMP = OE_MANUAL.merge(OE_BMP, how = 'outer', on =['Cd_CC','Dt_REF'], suffixes=("_MANUAL","_BMP"), indicator=True)

    map_res = {
                'both' : 'NO',
                'left_only' : 'Somente Manual de Dados, verifique informação',
                'right_only' : 'Somente BMP, verifique informação',
              }
    OE_COMP['OBS_CONC_MANUAL_BMP'] = OE_COMP['_merge'].map(map_res)
    if pd.api.types.is_categorical_dtype(OE_COMP['OBS_CONC_MANUAL_BMP']):
        OE_COMP['OBS_CONC_MANUAL_BMP'] = (
                                            OE_COMP['OBS_CONC_MANUAL_BMP']
                                            .cat.add_categories(['Somente BMP, porém AIC em curso, logo não deve constar no incremental de OE'])
                                        )
        
    lst_OEcurso = ['2223103','2223106', '2223203', '2223206', '2223303', '2223306', '2223403', '2223503']
    mask = OE_COMP['Cd_CC'].str[:7].isin(lst_OEcurso) & (OE_COMP['OBS_CONC_MANUAL_BMP'] == 'Somente BMP, verifique informação')
    OE_COMP.loc[mask, 'OBS_CONC_MANUAL_BMP'] = 'Somente BMP, porém AIC em curso, logo não deve constar no incremental de OE'

    OE_COMP = OE_COMP.drop(columns = '_merge')
    OE_COMP['VL_LCMTO_MANUAL'] = OE_COMP['VL_LCMTO_MANUAL'].fillna(0)
    OE_COMP['AX'] = OE_COMP['Cd_CC'].map(str).str[5:7]

    OE_COMP['DELTA'] = np.where(OE_COMP['AX'].isin(['1','2']),
        OE_COMP['VL_LCMTO_MANUAL'].fillna(0).abs() - OE_COMP['VL_DEB_BMP'].fillna(0).abs() + OE_COMP['VL_CRED_BMP'].fillna(0).abs(),
        OE_COMP['VL_LCMTO_MANUAL'].fillna(0).abs() + OE_COMP['VL_DEB_BMP'].fillna(0).abs() - OE_COMP['VL_CRED_BMP'].fillna(0).abs())
    OE_COMP['OBS_SFF'] = np.where((OE_COMP['DELTA'].abs()>0.01) & 
                                  (OE_COMP['OBS_CONC_MANUAL_BMP'] != 'Somente BMP, porém AIC em curso, logo não deve constar no incremental de OE'),
                                  "JUSTIFICAR DIFERENÇA",
                                  "NO")
    
    OE_COMP = OE_COMP.sort_values(by=['Cd_CC','Dt_REF'])
    OE_COMP.to_sql("ANL_BMP_MANUAL", con, if_exists='replace', index=False)

    nm_columns = []
    for nm in OE_AGR.columns:
        if nm[:2].upper() == 'VL':
            nm_columns.append(f"VL{nm[2:]}")
        else:
            nm_columns.append(nm)

    OE_AGR.columns = nm_columns
  
    if st: pgr.progress(5, "Iniciando os cálculos")
    if st: n1.info(f"""Buscando dados de IPCA.""", icon = "1️⃣")

    ipca = busca_ipca()[['Dt_REF', 'Nr_IPCA']].rename(columns={'Dt_REF': 'DT_CMPT'}) 
    ipca_anterior = ipca.loc[ipca['DT_CMPT'] == (pd.to_datetime(dt_ini_proc) - pd.DateOffset(months=1)), ipca.columns[-1]]
    ipca_anterior = ipca_anterior.iloc[0] if not ipca_anterior.empty else ipca.iloc[-1, -1] 
    ipca_final = ipca.loc[ipca['DT_CMPT'] == pd.to_datetime(dt_fim_proc).replace(day=1), ipca.columns[-1]]
    ipca_final = ipca_final.iloc[0] if not ipca_final.empty else ipca.iloc[-1, -1]

    if st: pgr.progress(10, "Iniciando os cálculos")
    if st: n1.info(f"""Buscando arquivo incremental.""", icon = "1️⃣")

    LST_TI = "70, 71, 72, 80, 82, 90, 91, 94, 95, 97, 99"
    LST_TI = ""
    if st.session_state.dt_fim <= date.today():
        SQLq = f"""
                    SELECT 
                        t1.Cd_CC,
                        t1.Nr_TUC,
                        t1.Nr_A1,
                        t1.Nr_A2,
                        t1.Dt_Imob,
                        t1.VL_VNR_UC AS VL_VOC,
                        0 AS VL_VOC_MV,
                        t1.VL_DAC_UC AS VL_DEP_ACUM,
                        0 AS VL_DEP_ACUM_MV,
                        t1.Nr_TI
                    FROM INCR t1 WHERE dt_ARQ = ?
                    AND t1.Cd_Q5 IN ('4.2','5.2')
                    AND t1.FLG_ELIG = 1 AND t1.Cd_CONC IN (1,'1',3,'3');
               """
        INC_TX = sql.imp_tbl_forma_001("INCR", con=con, st=st, Empresa=Empresa)

    else:
        SQLq = f"""
                    SELECT 
                        t1.Cd_CC,
                        t1.Nr_TUC,
                        t1.Nr_A1,
                        t1.Nr_A2,
                        t1.Dt_Imob,
                        t1.VL_VNR_UC AS VL_VOC,
                        0 AS VL_VOC_MV,
                        t1.VL_DAC_UC AS VL_DEP_ACUM,
                        0 AS VL_DEP_ACUM_MV,
                        t1.Nr_TI
                    FROM tbl_provINCR t1 WHERE
                    t1.Nr_TI not in ({LST_TI})
                    AND t1.FLG_ELIG IN (1, '1') AND t1.Cd_CONC IN (1,'1',3,'3');
            """

        INC_TX = sql.imp_tbl_forma_000("tbl_provINCR", con=con, st=st)

    
    if st: pgr.progress(20, "Iniciando os cálculos")
    if st: n1.info(f"""Buscando dados da blindada.""", icon = "2️⃣")

    if st.session_state.dt_fim <= date.today():
        SQLq = f"""
                    SELECT 
                        t1.Cd_CC,
                        t1.Nr_TUC,
                        t1.Nr_A1,
                        t1.Nr_A2,
                        t1.Dt_Lcmto AS Dt_Imob,
                        t2.VL_VNR_UC AS VL_VOC,
                        0 AS VL_VOC_MV,
                        t2.VL_DAC_UC AS VL_DEP_ACUM,
                        0 AS VL_DEP_ACUM_MV,
                        t1.Nr_TI
                    FROM PPBB t1 LEFT JOIN
                    PCBB t2 ON t1.Id_SEQ_PP = t2.Id_SEQ_PP
                    WHERE t1.dt_ARQ = ?  AND t2.dt_ARQ = ?
                    AND t1.Cd_Q5 IN ('4.2','5.2')
                    AND t2.FLG_ELIG IN (1,'1') AND t2.Cd_CONC IN (1,'1',3,'3') 
                    ;
                """
        BBPP_TX = sql.imp_tbl_forma_002("PPBB", "PCBB", SQLq=SQLq, con=con, st=st, Empresa=Empresa)
    else:
        SQLq = f"""
                    SELECT 
                        t1.Cd_CC,
                        t1.Nr_TUC,
                        t1.Nr_A1,
                        t1.Nr_A2,
                        t1.Dt_Lcmto AS Dt_Imob,
                        t1.VL_VNR_UC AS VL_VOC,
                        0 AS VL_VOC_MV,
                        t1.VL_DAC_UC AS VL_DEP_ACUM,
                        0 AS VL_DEP_ACUM_MV,
                        t1.Nr_TI
                    FROM PPBB t1
                    WHERE t1.dt_ARQ = ?
                    AND t1.Cd_Q5 IN ('4.2','5.2')
                    AND t1.FLG_ELIG = 1 AND t1.Cd_CONC IN (1,'1',3,'3') ;
                """
        BBPP_TX = sql.imp_tbl_forma_001("PPBB", SQLq=SQLq, con=con, st=st, Empresa=Empresa)

    if BBPP_TX.empty:
        SQLq = f"""
                    SELECT 
                        t1.Cd_CC,
                        t1.Nr_TUC,
                        t1.Nr_A1,
                        t1.Nr_A2,
                        t1.Dt_Lcmto AS Dt_Imob,
                        t1.VL_VNR_UC AS VL_VOC,
                        0 AS VL_VOC_MV,
                        t1.VL_DAC_UC AS VL_DEP_ACUM,
                        0 AS VL_DEP_ACUM_MV,
                        t1.Nr_TI
                    FROM PPBB t1 
                    WHERE t1.dt_ARQ = ?
                    AND  t1.Cd_Q5 IN ('4.2','5.2')
                    AND t1.FLG_ELIG = 1 AND t1.Cd_CONC IN (1,'1',3,'3') ;
            """
        BBPP_TX = sql.imp_tbl_forma_001("PPBB", SQLq=SQLq, con=con, st=st, Empresa=Empresa)

    df_TX_VNR = pd.DataFrame()
    if len(BBPP_TX)>0 and len(INC_TX)>0:
        df_TX_VNR = pd.concat([BBPP_TX,INC_TX], ignore_index=True)

    SQLq = f"""
                SELECT 
                    t1.Cd_CC,
                    t1.Nr_TUC,
                    t1.Nr_A1,
                    t1.Nr_A2,
                    t1.Dt_Imob,
                    t1.VL_VOC,
                    t1.VL_VOC_MV,
                    t1.VL_DEP_ACUM,
                    t1.VL_DEP_ACUM_MV,
                    t1.Nr_TI
                FROM AIS t1 WHERE dt_ARQ = ?
                and t1.Nr_TI not in ({LST_TI});
            """
    AIS_TX = sql.imp_tbl_forma_001("AIS", SQLq=SQLq, con=con, st=st, Empresa=Empresa)

    SQLq = f"""
                SELECT 
                    t1.Cd_CC,
                    t1.Nr_TUC,
                    t1.Nr_A1,
                    t1.Nr_A2,
                    t1.Dt_Imob,
                    t1.VL_VOC,
                    t1.VL_VOC_MV,
                    t1.VL_DEP_ACUM,
                    t1.VL_DEP_ACUM_MV,
                    t1.Nr_TI
                FROM AIS t1 WHERE dt_ARQ = ?;
            """
    AIS_TX_CMP = sql.imp_tbl_forma_001("AIS", SQLq=SQLq, con=con, st=st, Empresa=Empresa)


    if st: pgr.progress(30, "Iniciando os cálculos")
    if st: n1.info(f"""Calculando taxas médias de depreciação.""", icon = "3️⃣")


    AIS_TX_ATV_CMP = calc_taxa(AIS_TX_CMP, con, 'SOTI', st)
    AIS_TX_ATV_PLPT = calc_taxa(AIS_TX, con, 'PLPT', st)
    AIS_TX_ATV = calc_taxa(AIS_TX, con, 'TSEMTI', st)
    AIS_TX_ATV_VNR = calc_taxa(df_TX_VNR, con, 'VNR', st)

    if st: pgr.progress(35, "Iniciando os cálculos")
    if st: n1.info(f"""Executando os ajustes do período incremental.""", icon = "4️⃣")
    col_val = [col for col in OE_AGR.columns if col[:4].upper() == "VL_M"]
    nr_a = (dt_fim_proc.year - dt_ini_proc.year) * 12 + dt_fim_proc.month - dt_ini_proc.month + 1
    if len(col_val) != nr_a:
        st.warning("""O arquivo encaminhado é inconsistente com as datas empregadas como período incremental. 
                   Vamos considerar apenas as do período incremental. Caso haja mais, cortaremos, caso haja 
                   menos usaremos zero.""")
        if len(col_val) > (nr_a + 1):
            col_usar = [f"VL_Mes_{col + 1}" for col in range(nr_a)]
            OE_AGR = OE_AGR[['Id_OE','Cd_CC','TP_OE', 'VL_SLD_INI', 'VL_SLD_REAV', 'Dt_REF'] + col_usar]
        else:
            for col in range(len(col_val),nr_a + 1):
                if f"VL_Mes_{col}" not in OE_AGR.columns:
                    OE_AGR[f"VL_Mes_{col}"] = 0
    
    dic_agr = {
                    0 : 'Saldo Bruto de Obrigação Especial da Blindada',
                    1 : 'Saldo Bruto de Obrigação Especial Reavaliação',
                    2 : 'Saldo Bruto de Obrigação Especial da Incremental da Incorporação de Redes',
                    3 : 'Saldo Bruto de Obrigação Especial da Incremental do PLPT',
                    4 : 'Saldo Bruto de Obrigação Especial da Incremental do MLA',
                    5 : 'Saldo Bruto de Obrigação Especial da Incremental do Reembolso de CCC',
                    6 : 'Saldo Bruto de Obrigação Especial da Incremental de Outros',
                    7 : 'Saldo Bruto de Obrigação Especial',
                    8 : 'Taxa média de depreciação de atividade, anual',
                    9 : 'Taxa média de depreciação de atividade, mensal',
                    10 : 'Cota de amortização de Obrigação Especial da Blindada',
                    11 : 'Cota de amortização de Obrigação Especial Reavaliação',
                    12 : 'Cota de amortização de Obrigação Especial da Incorporação de Redes',
                    13 : 'Cota de amortização de Obrigação Especial do PLPT',
                    14 : 'Cota de amortização de Obrigação Especial do MLA',
                    15 : 'Cota de amortização de Obrigação Especial do Reembolso de CCC',
                    16 : 'Cota de amortização de Obrigação Especial da Incremental de Outros',
                    17 : 'Cota de amortização de Obrigação Especial'
                }

    if ('OE_AJST' in locals()) and (not OE_AJST.empty):
        for n in range(len(OE_AJST)):
            lst = OE_AJST.columns.to_list()
            posicao = lst.index('FLG_INC') - len(lst)
            if 'TP_OE' in OE_AJST.columns:
                posicao = lst.index('TP_OE') - len(lst)
                TP_OE = OE_AJST.iloc[n, posicao]
            else:
                TP_OE = 'OUTROS'
            if OE_AJST.iloc[n, posicao] == '1':
                if OE_AJST.iloc[n, 1] in ['Devoluções/Baixas OE', 'kit PLPT VOC OE']:
                    continue
                st.text(OE_AJST.iloc[n, 4])   
                dt_ini = pd.to_datetime(OE_AGR[(OE_AGR['Cd_CC'] == OE_AJST.iloc[n, 4]) &
                                 (OE_AGR['TP_OE'] == TP_OE)].iloc[-1,5])
                dt_fim =  pd.to_datetime(OE_AJST.iloc[n, 3])
                delta = (dt_fim.year - dt_ini.year) * 12 + dt_fim.month - dt_ini.month
                if (f"VL_Mes_{delta}" in OE_AGR.columns) & (len(OE_AGR[(OE_AGR['Cd_CC'] == OE_AJST.iloc[n, 4]) &
                                    (OE_AGR['TP_OE'] == TP_OE)]) == 1):
                    OE_AGR.loc[(OE_AGR['Cd_CC'] == OE_AJST.iloc[n, 4]) &
                                    (OE_AGR['TP_OE'] == TP_OE), f"VL_Mes_{delta}"] += OE_AJST.iloc[n, 2]
                else:
                    st.warning("Não foi possível fazer este ajuste, verifique os dados informados:")
                    st.write(OE_AJST.iloc[n, :].T)
            else:
                crit = (OE_AGR['Cd_CC'] == OE_AJST.iloc[n, 4]) & (OE_AGR['TP_OE'] == TP_OE)
                OE_AGR.loc[crit, 'VL_SLD_INI']  = (OE_AGR.loc[crit, 'VL_SLD_INI'] + OE_AJST.loc[n,'VL_SALDO_AJS'])

    if st: pgr.progress(50, "Iniciando os cálculos")
    if st: n1.info(f"""Calculando a atualização e depreciação das OE, 5B.""", icon = "5️⃣")
    OE_AGR['AX'] = OE_AGR['Cd_CC'].map(str).str[5:7]
    colAX = [col for col in OE_AGR.columns if col[:4].upper() == "VL_M"]
    colunas = ['TP_OE', 'Dt_REF', 'VL_SLD_INI'] + colAX
    n_linhas = len(dic_agr)
    n_colunas = len(colunas)

    SB_BB = pd.DataFrame(index=range(n_linhas), columns=colunas)
    SB_BB[['VL_SLD_INI'] + colAX] = 0
    SB_BB['Dt_REF'] = OE_AGR['Dt_REF'].iloc[0]
    for i, n in enumerate(['VL_SLD_INI', 'VL_SLD_REAV', 'IR', 'PLPT', 'MLPA', 'CCC', 'OUTROS']):
        if i in [0,1]:
            SB_BB.iloc[i,0] = dic_agr[i]
            SB_BB.iloc[i,2:] = [OE_AGR[OE_AGR['AX'].isin(['01', '04'])][n].sum()] * (len(colAX) + 1)
        else:
            SB_BB.iloc[i,0] = dic_agr[i]
            df = OE_AGR[OE_AGR['AX'].isin(['01', '04']) & (OE_AGR['TP_OE'] == n)][colAX].copy()
            SB_BB.iloc[i,3:] = df.sum()
            for n in range(3, nr_a + 4):
                if f"VL_Mes_{n-2}" in SB_BB.columns:
                    SB_BB.iloc[i, n] = SB_BB.iloc[i, n] + SB_BB.iloc[i, n - 1]

    i += 1        
    SB_BB.iloc[i, 0] = dic_agr[i]
    SB_BB.iloc[i, 1] = SB_BB.iloc[0, 1]
    SB_BB.iloc[i, 2] = SB_BB.iloc[:i-1, 2].sum()
    for n in range(3, nr_a + 4):
        if f"VL_Mes_{n-2}" in SB_BB.columns:
            SB_BB.iloc[i, n] = SB_BB.iloc[:i, n].sum()

    SB_BB.iloc[8,0] = dic_agr[8]
    SB_BB.iloc[9,0] = dic_agr[9]

    for i, n in enumerate(['VL_SLD_INI', 'VL_SLD_REAV', 'IR', 'PLPT', 'MLPA', 'CCC', 'OUTROS']):
        if i in [0,1]:
            SB_BB.iloc[i + 10, 0] = dic_agr[i + 10]
            SB_BB.iloc[i + 10, 2] = [OE_AGR[OE_AGR['AX'].isin(['02', '05'])][n].sum()]
        else:
            SB_BB.iloc[i + 10, 0] = dic_agr[i + 10]
            df = OE_AGR[OE_AGR['AX'].isin(['02', '05']) & (OE_AGR['TP_OE'] == n)][colAX].copy()
            SB_BB.iloc[i + 10, 3:] = df.sum()
        for n in range(3, nr_a + 4):
            if f"VL_Mes_{n-2}" in SB_BB.columns:
                SB_BB.iloc[i + 10, n] = 0
    i += 11        
    SB_BB.iloc[i, 0] = dic_agr[i]
    SB_BB.iloc[i, 1] = SB_BB.iloc[0, 1]
    SB_BB.iloc[i, 2] = SB_BB.iloc[10 : i, 2].sum()
    SB_BB.loc[len(SB_BB)] = 0
    SB_BB.iloc[-1, 0] = "COTA MENSAL INFORMADA"
    SB_BB.iloc[-1, 1] = SB_BB.iloc[0, 1]
    df_TX = AIS_TX_ATV_VNR.reset_index()
    TX_MD = df_TX[(df_TX['Nm_ATVD'] == 'Distribuição') & (df_TX['Nm_CLASS'] == 'BRR')].iloc[-1, -1]

    for n in range(3, nr_a + 3):
        if f"VL_Mes_{n-2}" in SB_BB.columns:
            nm_COL = f"VL_Mes_{n-2}"
        elif f"Vl_Mes_{n-2}" in SB_BB.columns:
            nm_COL = f"Vl_Mes_{n-2}"
        else:
            raise UserWarning(f"fAvalie arquivo OE_AGR: VL_Mes_{n-2}")
        if nm_COL in SB_BB.columns:
            TOT_COT_AMT_MES = OE_AGR[OE_AGR['AX'].isin(['02', '05'])][nm_COL].sum()
            if TX_AMT_OE:
                SB_BB.iloc[9, n] = TX_MD / 12
            else:
                if TOT_COT_AMT_MES > 0:
                    SB_BB.iloc[9, n] = (TOT_COT_AMT_MES) / abs(SB_BB.iloc[0:7, n-1].sum())
                else:
                    SB_BB.iloc[9, n] = SB_BB.iloc[9, 3:n-1].median()
            SB_BB.iloc[8, n] = 12 * SB_BB.iloc[9, n]
            
            SB_BB.iloc[10, n] = SB_BB.iloc[9, n] * abs(SB_BB.iloc[0, n - 1]) + SB_BB.iloc[10, n-1]
            SB_BB.iloc[11, n] = SB_BB.iloc[9, n] * abs(SB_BB.iloc[1, n - 1]) + SB_BB.iloc[11, n-1]
            SB_BB.iloc[12, n] = SB_BB.iloc[9, n] * abs(SB_BB.iloc[2, n - 1]) + SB_BB.iloc[12, n-1]
            SB_BB.iloc[13, n] = SB_BB.iloc[9, n] * abs(SB_BB.iloc[3, n - 1]) + SB_BB.iloc[13, n-1]
            SB_BB.iloc[14, n] = SB_BB.iloc[9, n] * abs(SB_BB.iloc[4, n - 1]) + SB_BB.iloc[14, n-1]
            SB_BB.iloc[15, n] = SB_BB.iloc[9, n] * abs(SB_BB.iloc[5, n - 1]) + SB_BB.iloc[15, n-1]
            SB_BB.iloc[16, n] = SB_BB.iloc[9, n] * abs(SB_BB.iloc[6, n - 1]) + SB_BB.iloc[16, n-1]
            SB_BB.iloc[i, n] = SB_BB.iloc[10:i, n].sum()
            SB_BB.iloc[-1, n] = TOT_COT_AMT_MES

    
    OE_AGR.to_sql("ANL_OE_UN", con, if_exists='replace', index=False)
    SB_BB.to_sql("ANL_OE_FIM", con, if_exists='replace', index=False)

    if st: pgr.progress(70, "Executando teste")
    if st: n1.info(f"""Verificando a taxa média das OE.""", icon = "6️⃣")

    OEAMT_TX_TESTE = (SB_BB[SB_BB['TP_OE'] == 'Taxa média de depreciação de atividade, anual'][colAX]
                      .T
                      .reset_index()
                      .rename(columns = {"index" : "Mes", 8 : 'Tx_APL'}))
    
    Q1 = OEAMT_TX_TESTE['Tx_APL'].quantile(0.25)
    Q3 = OEAMT_TX_TESTE['Tx_APL'].quantile(0.75)
    IQR = Q3 - Q1
    OEAMT_TX_TESTE['LIM_APL_SUP'] = Q1 + 1.5 * IQR
    OEAMT_TX_TESTE['LIM_APL_INF'] = Q1 - 1.5 * IQR
    OEAMT_TX_TESTE['Tx_VNR'] = TX_MD / 12

    OEAMT_TX_TESTE['TESTE'] = "NO"
    OEAMT_TX_TESTE.loc[(OEAMT_TX_TESTE['Tx_APL'] > OEAMT_TX_TESTE['LIM_APL_SUP']) |
                       (OEAMT_TX_TESTE['Tx_APL'] < OEAMT_TX_TESTE['LIM_APL_INF']), 'TESTE'] = "AVALIAR A TAXA NESTE MÊS"

    OEAMT_TX_TESTE.to_sql("ANL_TX_AMT_OE", con, if_exists='replace', index=False)
    ipca['DT_CMPT'] = pd.to_datetime(ipca['DT_CMPT'], errors = 'coerce')
    ipca.to_sql("ANL_IPCA_OE", con, if_exists='replace', index=False)

    #VAMOS FAZER OS AJUSTES
    VL_VOC = {"DEMAIS": 1, "IR": 1, "PLPT": 1, "CCC": 1}
    VL_VNR = {"DEMAIS": 1, "IR": 1, "PLPT": 1, "CCC": 1}
    Cd_EMP = sql.bsc_cd_aneel(Empresa)
    dir_anls = dir_arq_saida.replace("OE_ANLS","INC_ANLS")
    arquivos_tipo = ["DEMAIS", "IR", "PLPT", "CCC"]

    if st: pgr.progress(80, "Atualizando")
    if st: n1.info(f"""Atualizando os dados.""", icon = "7️⃣")

    lst_COL = sql.colunas_tabela(con, "INCR")

    if sql.existe_tabela("INCR", con) and ('Cd_Q5' in lst_COL):
        SQLq = """SELECT 
                    Cd_SubODI, 
                    VL_VOC, 
                    VL_VNR_UC,
                    Pct_OE,
                    FLG_INCOR_OE,
                    FLG_PLPT_OE, 
                    Cd_Q5
                 FROM 
                    INCR 
                 WHERE 
                    dt_ARQ = ? AND FLG_ELIG=1 AND Cd_CONC IN (1,3)"""
        INCR = sql.imp_tbl_forma_001("INCR", SQLq=SQLq, con=con, st=st, Empresa=Empresa)
        INCR['VL_VOC'] = pd.to_numeric(INCR['VL_VOC'].astype(str).str.replace(",","."), errors='coerce').fillna(0)
        INCR['VL_VNR_UC'] = pd.to_numeric(INCR['VL_VNR_UC'].astype(str).str.replace(",","."), errors='coerce').fillna(0)
        INCR['Pct_OE'] = pd.to_numeric(INCR['Pct_OE'].astype(str).str.replace(",","."), errors='coerce').fillna(0)
        SQLq = """SELECT 
                    Cd_SubODI,
                    Pct_OE, 
                    Cd_Tipo_OE
                FROM
                    ROS
                WHERE 
                    dt_ARQ = ?;"""
        ROS = sql.imp_tbl_forma_001("ROS", SQLq=SQLq, con=con, st=st, Empresa=Empresa)
        ROS['Pct_OE'] = pd.to_numeric(ROS['Pct_OE'].astype(str).str.replace(",","."), errors='coerce').fillna(0)
        dd_ANLS = INCR.merge(ROS, how='left', on='Cd_SubODI', suffixes=("_INCR","_ROS"))

        arquivos_tipo = ["DEMAIS", "IR", "PLPT", "CCC"]
        dic_tipo ={
                    "DEMAIS" : ['4','5','6','8'], 
                    "IR" : ['7'], 
                    "PLPT": ['1', '2'], 
                    "CCC" : ['3']
                  }

        for nm in arquivos_tipo:
            somaVOC =  1
            somaVNR =  1
            df_PROV = dd_ANLS[dd_ANLS['Cd_Tipo_OE'].isin(dic_tipo[nm])].copy()
            if len(df_PROV) > 0:
                somaVOC =  df_PROV['VL_VOC'].sum()
                somaVNR =  df_PROV['VL_VNR_UC'].sum()
            else:
                if nm == "IR":
                    df_PROV = dd_ANLS[dd_ANLS['FLG_INCOR_OE'].astype(str)=='1'].copy()
                    if len(df_PROV) > 0:
                        somaVOC =  df_PROV['VL_VOC'].sum()
                        somaVNR =  df_PROV['VL_VNR_UC'].sum()
                elif nm == "PLPT":
                    df_PROV = dd_ANLS[dd_ANLS['FLG_PLPT_OE'].astype(str)=='1'].copy()
                    if len(df_PROV) > 0:
                        somaVOC =  df_PROV['VL_VOC'].sum()
                        somaVNR =  df_PROV['VL_VNR_UC'].sum()
                else:
                    mask = ((dd_ANLS['FLG_INCOR_OE'].astype(str)!='1') & 
                           (dd_ANLS['FLG_PLPT_OE'].astype(str)!='1') &
                           ((dd_ANLS['Pct_OE_INCR']>0) | (dd_ANLS['Pct_OE_ROS']>0)))
                    df_PROV = dd_ANLS[mask].copy()
                    if len(df_PROV) > 0:
                                            somaVOC =  df_PROV['VL_VOC'].sum()
                                            somaVNR =  df_PROV['VL_VNR_UC'].sum()
            VL_VOC[nm] = somaVOC
            VL_VNR[nm] = somaVNR 

    else:
        for tipo in arquivos_tipo:
            arq = f"BASE_INCR_{tipo}_{Cd_EMP}.csv"
            cam_arq = os.path.join(dir_anls, arq)

            if os.path.exists(cam_arq):
                try:
                    BASE_INCR = pd.read_csv(cam_arq, sep="|", header=None, 
                                            encoding="Latin-1", dtype=str)
                except:
                    continue
                if BASE_INCR.empty:
                    if st: st.warning(f"O arquivo {arq} está vazio.")
                    continue
                cols = [2, 3, 4, 5, 6, 7, 8, 9]
                BASE_INCR[cols] = BASE_INCR[cols].apply(pd.to_numeric, errors="coerce")
                filtro_52 = BASE_INCR[BASE_INCR[1] == "5.2"]
                if filtro_52.empty:
                    if st: st.warning(f"Não há dados para '5.2' no arquivo {arq}.")
                    continue
                ultima_linha = filtro_52.iloc[-1]
                VL_VOC[tipo] = ultima_linha[[3, 4, 5, 6]].sum(min_count=1)
                VL_VNR[tipo] = ultima_linha[7]

    if ('OE_AJST' in locals()) and (not OE_AJST.empty):
        DEV = OE_AJST.loc[OE_AJST['Txt_AJS'] == 'Devoluções/Baixas OE', 'VL_SALDO_AJS']
        DEV = DEV.sum() if not DEV.empty else 0
    
        kit_PLPT = OE_AJST.loc[OE_AJST['Txt_AJS'] == 'kit PLPT VOC OE', 'VL_SALDO_AJS']
        kit_PLPT = kit_PLPT.sum() if not kit_PLPT.empty else 0
        OE_AJST['AX'] = OE_AJST['Cd_CC'].map(str).str[5:7]
        AJS_BB = OE_AJST.loc[OE_AJST['FLG_INC'].isin([0,'0']) & OE_AJST['AX'].isin(['01', '04']), 'VL_SALDO_AJS']
        AJS_BB = AJS_BB.sum() if not AJS_BB.empty else 0
    else:
        DEV = 0
        kit_PLPT = 0
        AJS_BB = 0

    def bsc_uv(df, cnd):
        filtro = df[df['TP_OE'] == cnd]
        if not filtro.empty:
            ultima_coluna = df.columns[-1]
            valor = filtro[ultima_coluna].iloc[0]
            return valor if pd.notna(valor) else 0 
        return 0
    

    saldo_inicial = SB_BB.iloc[0, -1] + SB_BB.iloc[1, -1] if len(SB_BB) else 0
    saldo_atualizado = (saldo_inicial - DEV - AJS_BB) * (ipca_final / ipca_anterior)
    amortizacao_blindada = bsc_uv(SB_BB, 'Cota de amortização de Obrigação Especial da Blindada')
    amortizacao_reavaliacao = bsc_uv(SB_BB, 'Cota de amortização de Obrigação Especial Reavaliação')
    total_amortizacao = amortizacao_blindada + amortizacao_reavaliacao
    percentual_amortizacao = (total_amortizacao / abs(saldo_inicial) * 100) if saldo_inicial != 0 else 0
    valor_amortizacao = saldo_atualizado * (total_amortizacao / abs(saldo_inicial)) if saldo_inicial != 0 else 0
    saldo_liquido_atualizado = saldo_atualizado * (1 - (total_amortizacao / abs(saldo_inicial))) if saldo_inicial != 0 else saldo_atualizado

    dic_ax = {
                'Item': [
                    'Saldo da Obrigação Especial Ciclo Anterior (R$)',
                    'IPCA Ciclo Anterior',
                    'Devoluções/Baixas OE (R$)',
                    'Valor Saldo OE após Baixas (R$)',
                    'IPCA Data Laudo',
                    'Saldo da OE atualizado (R$)',
                    'Percentual de amortização (%)',
                    'Valor Amortização (R$)',
                    'Saldo Líquido Atualizado (R$)'
                ],
                'Valor': [
                    saldo_inicial,
                    ipca_anterior,
                    DEV,
                    saldo_inicial - DEV,
                    ipca_final,
                    saldo_atualizado,
                    percentual_amortizacao,
                    valor_amortizacao,
                    saldo_liquido_atualizado
                ]
            }
    df_BB = pd.DataFrame(data=dic_ax)
    df_BB.to_sql("ANL_OE_BB", con, if_exists='replace', index=False)   
    
    sb_ir = bsc_uv(SB_BB, 'Saldo Bruto de Obrigação Especial da Incremental da Incorporação de Redes')
    sb_plpt = (bsc_uv(SB_BB, 'Saldo Bruto de Obrigação Especial da Incremental do PLPT') +
               bsc_uv(SB_BB, 'Saldo Bruto de Obrigação Especial da Incremental do MLA'))
    sb_ccc = bsc_uv(SB_BB, 'Saldo Bruto de Obrigação Especial da Incremental do Reembolso de CCC')
    sb_demais = bsc_uv(SB_BB, 'Saldo Bruto de Obrigação Especial da Incremental de Outros')
    

    amortizacao_ir = bsc_uv(SB_BB, 'Cota de amortização de Obrigação Especial da Incorporação de Redes')
    amortizacao_plpt = (bsc_uv(SB_BB, 'Cota de amortização de Obrigação Especial do PLPT') +
                        bsc_uv(SB_BB, 'Cota de amortização de Obrigação Especial do MLA'))
    amortizacao_ccc = bsc_uv(SB_BB, 'Cota de amortização de Obrigação Especial do Reembolso de CCC')
    amortizacao_demais = bsc_uv(SB_BB, 'Cota de amortização de Obrigação Especial da Incremental de Outros')

    # Vamos fazer um fallback, caso haja problemas de conciliação do incremental
    if (abs(sb_demais) > 0) and (VL_VOC['DEMAIS'] == 1):
        if VL_VOC['IR'] > 1:
            VL_VOC['DEMAIS'] = VL_VOC['IR']
            VL_VNR['DEMAIS'] = VL_VNR['IR']
        elif VL_VOC['PLPT'] > 1:
            VL_VOC['DEMAIS'] = VL_VOC['PLPT']
            VL_VNR['DEMAIS'] = VL_VNR['PLPT']
        elif VL_VOC['CCC'] > 1:
            VL_VOC['DEMAIS'] = VL_VOC['CCC']
            VL_VNR['DEMAIS'] = VL_VNR['CCC']
        else:
            st.warning("Verifique arquivo incremental, marcação de OE")
    
    if (abs(sb_ir) > 0) and (VL_VOC['IR'] == 1):
        if VL_VOC['DEMAIS'] > 1:
            VL_VOC['IR'] = VL_VOC['DEMAIS']
            VL_VNR['IR'] = VL_VNR['DEMAIS']
        elif VL_VOC['PLPT'] > 1:
            VL_VOC['IR'] = VL_VOC['PLPT']
            VL_VNR['IR'] = VL_VNR['PLPT']
        elif VL_VOC['CCC'] > 1:
            VL_VOC['IR'] = VL_VOC['CCC']
            VL_VNR['IR'] = VL_VNR['CCC']
        else:
            st.warning("Verifique arquivo incremental, marcação de OE")
    
    if (abs(sb_plpt) > 0) and (VL_VOC['PLPT'] == 1):
        if VL_VOC['DEMAIS'] > 1:
            VL_VOC['PLPT'] = VL_VOC['DEMAIS']
            VL_VNR['PLPT'] = VL_VNR['DEMAIS']
        elif VL_VOC['IR'] > 1:
            VL_VOC['PLPT'] = VL_VOC['IR']
            VL_VNR['PLPT'] = VL_VNR['IR']
        elif VL_VOC['CCC'] > 1:
            VL_VOC['PLPT'] = VL_VOC['CCC']
            VL_VNR['PLPT'] = VL_VNR['CCC']
        else:
            st.warning("Verifique arquivo incremental, marcação de OE")

    if (abs(sb_ccc) > 0) and (VL_VOC['CCC'] == 1):
        if VL_VOC['DEMAIS'] > 1:
            VL_VOC['CCC'] = VL_VOC['DEMAIS']
            VL_VNR['CCC'] = VL_VNR['DEMAIS']
        elif VL_VOC['IR'] > 1:
            VL_VOC['CCC'] = VL_VOC['IR']
            VL_VNR['CCC'] = VL_VNR['IR']
        elif VL_VOC['PLPT'] > 1:
            VL_VOC['CCC'] = VL_VOC['PLPT']
            VL_VNR['CCC'] = VL_VNR['PLPT']
        else:
            st.warning("Verifique arquivo incremental, marcação de OE")

    dic_ax = {
                'Item': [
                    'VOC Máquinas Equipamentos (VOC_ME) (R$)', 
                    'VOC de OE Incremental (VOC_OE) (R$)', 
                    'kit PLPT VOC OE (R$)', 
                    'Saldo bruto da OE incremental, VOC (R$)', 
                    'VOC_OE/VOC_ME', 
                    'VNR Máquinas Equipamentos (VNR_ME) (R$)', 
                    'Índice de atualização', 
                    'Saldo bruto da OE incremental Atualizado (R$)', 
                    'Percentual de amortização (%)', 
                    'Valor amortização (R$)', 
                    'Saldo Líquido Atualizado (R$)'
                ],
                'Demais' : [
                    VL_VOC['DEMAIS'], 
                    abs(sb_demais), 
                    0, 
                    abs(sb_demais), 
                    abs(sb_demais) / VL_VOC['DEMAIS'], 
                    VL_VNR['DEMAIS'], 
                    VL_VNR['DEMAIS'] / VL_VOC['DEMAIS'], 
                    abs(sb_demais) * VL_VNR['DEMAIS'] / VL_VOC['DEMAIS'], 
                    amortizacao_demais / abs(sb_demais) * 100, 
                    abs(sb_demais) * VL_VNR['DEMAIS'] / VL_VOC['DEMAIS'] * amortizacao_demais / abs(sb_demais), 
                    abs(sb_demais) * VL_VNR['DEMAIS'] / VL_VOC['DEMAIS'] * (1 - amortizacao_demais / abs(sb_demais)), 
                ],
                'IR' : [
                    VL_VOC['IR'], 
                    abs(sb_ir), 
                    0, 
                    abs(sb_ir), 
                    abs(sb_ir) / VL_VOC['IR'], 
                    VL_VNR['IR'], 
                    VL_VNR['IR'] / VL_VOC['IR'], 
                    abs(sb_ir) * VL_VNR['IR'] / VL_VOC['IR'], 
                    amortizacao_ir / abs(sb_ir) * 100 if abs(sb_ir) != 0 else 0, 
                    abs(sb_ir) * VL_VNR['IR'] / VL_VOC['IR'] * amortizacao_ir / abs(sb_ir) if abs(sb_ir) != 0 else 0, 
                    abs(sb_ir) * VL_VNR['IR'] / VL_VOC['IR'] * (1 - (amortizacao_ir / abs(sb_ir) if abs(sb_ir) != 0 else 0) ), 
                ],
                'PLPT' : [
                    VL_VOC['PLPT'], 
                    abs(sb_plpt), 
                    kit_PLPT, 
                    kit_PLPT + abs(sb_plpt), 
                    (kit_PLPT + abs(sb_plpt)) / VL_VOC['PLPT'], 
                    VL_VNR['PLPT'], 
                    VL_VNR['PLPT'] / VL_VOC['PLPT'], 
                    (kit_PLPT + abs(sb_plpt)) *  VL_VNR['PLPT'] / VL_VOC['PLPT'], 
                    abs(amortizacao_plpt) / abs(kit_PLPT + abs(sb_plpt)) * 100 if abs(kit_PLPT - abs(sb_plpt)) != 0 else 0, 
                    abs(kit_PLPT + abs(sb_plpt)) *  VL_VNR['PLPT'] / VL_VOC['PLPT'] * abs(amortizacao_plpt) / abs(kit_PLPT + abs(sb_plpt)) if abs(kit_PLPT + abs(sb_plpt)) != 0 else 0, 
                    abs(kit_PLPT + abs(sb_plpt)) *  VL_VNR['PLPT'] / VL_VOC['PLPT'] * (1 - (abs(amortizacao_plpt) / abs(kit_PLPT + abs(sb_plpt)) if abs(kit_PLPT + abs(sb_plpt)) != 0 else 0)), 
                ],
                'REEMB. CCC' : [
                    VL_VOC['CCC'], 
                    abs(sb_ccc), 
                    0, 
                    abs(sb_ccc), 
                    abs(sb_ccc) / VL_VOC['CCC'], 
                    VL_VNR['CCC'], 
                    VL_VNR['CCC'] / VL_VOC['CCC'], 
                    abs(sb_ccc) * VL_VNR['CCC'] / VL_VOC['CCC'], 
                    amortizacao_ccc / abs(sb_ccc) * 100 if sb_ccc != 0 else 0, 
                    abs(sb_ccc) * VL_VNR['CCC'] / VL_VOC['CCC'] * amortizacao_ccc / abs(sb_ccc) if sb_ccc != 0 else 0, 
                    abs(sb_ccc) * VL_VNR['CCC'] / VL_VOC['CCC'] * (1 - (amortizacao_ccc / abs(sb_ccc) if sb_ccc != 0 else 0)), 
                ]
            }
    df_BI = pd.DataFrame(data=dic_ax).fillna(0)
    df_BI.to_sql("ANL_OE_BI", con, if_exists='replace', index=False)

    #################################################################################
    pgr.empty()

    VOC_OE_INC = abs(df_BI[df_BI['Item'] == 'Saldo bruto da OE incremental Atualizado (R$)'].iloc[0,1:].sum())
    AMT_OE_INC = abs(df_BI[df_BI['Item'] == 'Saldo Líquido Atualizado (R$)'].iloc[0,1:].sum())

    VOC_OE = abs(df_BB[df_BB['Item'] == 'Saldo da OE atualizado (R$)'].iloc[0,-1]) 
    AMT_OE = abs(df_BB[df_BB['Item'] == 'Saldo Líquido Atualizado (R$)'].iloc[0,-1])

    CHAVES_BASE = [
                    "(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)",
                    "(2) Índice de Aproveitamento Integral",
                    "(3) Obrigações Especiais Bruta",
                    "(4) Bens Totalmente Depreciados",
                    "(6) Depreciação Acumulada",
                    "(7) AIS Líquido (Valor de Mercado em Uso)",
                    "(8) Índice de Aproveitamento Depreciado",
                    "(9) Valor da Base de Remuneração (VBR)",
                    "(10) Almoxarifado em Operação",
                    "(11) Ativo Diferido",
                    "(12) Obrigações Especiais Liquida",
                    "(13) Terrenos e Servidões",
                ]

    IMP_INCR = {chave: 0 for chave in CHAVES_BASE}
    IMP_BB = IMP_INCR.copy()

    dir_INC = dir_arq_saida.replace("OE_ANLS", "INC_ANLS")
    dir_BB = dir_arq_saida.replace("OE_ANLS", "BB_ANLS")

    def at_tbl(resumo_dict, filename, con):
        if sql.existe_tabela(filename, con):
            df_resumo = pd.read_sql(f"SELECT * FROM {filename}", con)
            for _, row in df_resumo.iterrows():
                resumo_dict[row[0]] = row[1] if isinstance(row[1], (int, float)) else 0

    at_tbl(IMP_INCR, "RES_INCR_QDTAR_SFF", con)
    at_tbl(IMP_BB, "RES_BB_QDTAR_SFF", con)

    def calc_OE(imp_dict, VOC_OE, AMT_OE, FA_OE):
        imp_dict["(3) Obrigações Especiais Bruta"] = abs(VOC_OE * FA_OE)
        imp_dict["(12) Obrigações Especiais Liquida"] = abs(AMT_OE * FA_OE)
        imp_dict["(5) Base de Remuneração Bruta = (1)-(2)-(3)-(4)"] = (
                                            imp_dict["(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)"]
                                            - imp_dict["(2) Índice de Aproveitamento Integral"]
                                            - imp_dict["(3) Obrigações Especiais Bruta"]
                                            - imp_dict["(4) Bens Totalmente Depreciados"]
                                        )
        imp_dict["(14) Base de Remuneração Líquida Total = (1)-(6)-(8)+(10)+(11)-(12)+(13)"] = (
                                            imp_dict["(1) Ativo Imobilizado em Serviço (Valor Novo de Reposição)"]
                                            - imp_dict["(6) Depreciação Acumulada"]
                                            - imp_dict["(8) Índice de Aproveitamento Depreciado"]
                                            + imp_dict["(10) Almoxarifado em Operação"]
                                            + imp_dict["(11) Ativo Diferido"]
                                            - imp_dict["(12) Obrigações Especiais Liquida"]
                                            + imp_dict["(13) Terrenos e Servidões"]
                                        )

    calc_OE(IMP_INCR, VOC_OE_INC, AMT_OE_INC, 1)
    calc_OE(IMP_BB, VOC_OE, AMT_OE, 1)

    def salvar_csv(data_dict, filename, tabela):
        df = pd.DataFrame.from_dict(data_dict, orient="index", columns=['Valor'])
        df.to_csv(f"{filename}", header=False, index=False, sep="|", decimal=',', encoding="Latin-1")
        df.to_sql(tabela, con, if_exists='replace', index=True)

    salvar_csv(IMP_INCR, f"{dir_INC}\\tbl_resumo_INC_{Cd_EMP}.csv", "RES_INCR_QDTAR_SFF")
    salvar_csv(IMP_BB, f"{dir_BB}\\tbl_resumo_BB_{Cd_EMP}.csv", "RES_BB_QDTAR_SFF")

    if st: 
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf"{dir_INC}\\tbl_resumo_INC_{Cd_EMP}.csv",
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf"{dir_BB}\\tbl_resumo_BB_{Cd_EMP}.csv",
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    
    return "OK"