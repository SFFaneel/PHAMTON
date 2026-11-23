import pandas as pd, sqlite3 as sl, numpy as np
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
from scipy.signal import find_peaks
import UTILS.sqlfnc as sql
from SRC.ais_funcoes import bsc_nr_amst
from math import sqrt
from UTILS import monitor_completo  
import streamlit as st
from typing import Union, Optional, List
from MANIFESTO import (
                        registrar_artefato,
                        registrar_evento
                      )

@monitor_completo(st.session_state.LOGGER)
def TCCU(st=None):
    if st == None:
        return "Falhou"
    
    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year

    bd = sl.connect(f'{local}\BD_LOCAL\{empresa}_{ano}.db')

    SQLq = f"""
                SELECT
                    Cd_ODI,
                    Cd_SubODI,
                    Nr_TI,
                    Nr_TUC,
                    Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5, Nr_A6, COD_ITEM,

                    CASE 
                        WHEN Qtd_AIS = '' THEN 0 
                        ELSE CAST(Qtd_AIS AS REAL)
                    END AS Qtd,

                    CASE 
                        WHEN VL_VOC = '' THEN 0 
                        ELSE CAST(VL_VOC AS REAL)
                    END AS VL_VOC,
                    CAST(VL_VOC_VF_AVAL AS REAL) AS VL_VOC_VF_AVAL,
                    CAST(VL_VOC_COM_AVAL AS REAL) AS VL_VOC_COM_AVAL,
                    CAST(VL_VOC_CA_AVAL AS REAL) AS VL_VOC_CA_AVAL,
                    CAST(VL_VOC_JOA_AVAL AS REAL) AS VL_VOC_JOA_AVAL
                FROM INCR WHERE FLG_ELIG = 1 AND Cd_CONC = 1 AND (FLG_OAT = 0 OR Cd_TP_AVAL = 2) AND Dt_ARQ = ?

            """

    df_cu = sql.imp_tbl_forma_001("INCR", SQLq, bd, st, empresa)
    
    df_cu['CM_UC'] = np.where(
                                    df_cu['Qtd'] != 0,
                                    df_cu['VL_VOC_VF_AVAL'] / df_cu['Qtd'],
                                    df_cu['VL_VOC_VF_AVAL']
                              )
    df_cu['CM_COM'] = np.where(
                                    df_cu['Qtd'] != 0,
                                    df_cu['VL_VOC_COM_AVAL'] / df_cu['Qtd'],
                                    df_cu['VL_VOC_COM_AVAL']
                              )
    df_cu['CM_CA'] = np.where(
                                    df_cu['Qtd'] != 0,
                                    df_cu['VL_VOC_CA_AVAL'] / df_cu['Qtd'],
                                    df_cu['VL_VOC_CA_AVAL']
                              )
    df_cu['CM_JOA'] = np.where(
                                    df_cu['Qtd'] != 0,
                                    df_cu['VL_VOC_JOA_AVAL'] / df_cu['Qtd'],
                                    df_cu['VL_VOC_JOA_AVAL']
                              )

    def calc_iqr_limiar(s):
        Q1 = s.quantile(0.25)
        Q3 = s.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        return lower, upper
    
    def calc_percentil_limiar(s, lower_q=0.05, upper_q=0.95):
        lower = s.quantile(lower_q)
        upper = s.quantile(upper_q)
        return lower, upper

    def calc_z(s):
        med = s.median()
        MAD = (np.abs(s - med)).median()
        rob_z = (s - med) / (1.4826 * MAD) if MAD != 0 else np.zeros_like(s)
        return rob_z

    def UC_TI(df, Nr_TI):
        df_ti = df[df['Nr_TI'] == Nr_TI].copy()
        if df_ti.empty:
            return []

        df_ti['UC_Tupla'] = df_ti.apply(
                                            lambda row: tuple(
                                                row[['Nr_TUC','Nr_A1','Nr_A2','Nr_A3','Nr_A4','Nr_A5','Nr_A6','COD_ITEM']]
                                            ),
                                            axis=1
                                       )

        contagens = df_ti['UC_Tupla'].value_counts().to_dict()
        df_ti['Qtd_UC'] = df_ti['UC_Tupla'].map(contagens)
        return df_ti

    cols_cu = ['CM_UC', 'CM_COM', 'CM_CA', 'CM_JOA', 'Qtd']
    df_cu[cols_cu] = df_cu[cols_cu].fillna(0)
    LST_TI = ['40','41','93','96']


    df_sai = pd.DataFrame()
    for Nr_TI in LST_TI:
        Grp_UC = UC_TI(df_cu, Nr_TI) 
        if len(Grp_UC)==0:
            continue  
         
        Grp_UCanl = Grp_UC[Grp_UC['Qtd_UC'] > 5].copy()
        tuplas_unicas = sorted(set(Grp_UCanl['UC_Tupla']))
        for comb in tuplas_unicas:
            df_FILTRO = Grp_UCanl[Grp_UCanl['UC_Tupla'] == comb].copy()
            scaler = RobustScaler()
            X = scaler.fit_transform(df_FILTRO[cols_cu])

            iso = IsolationForest(
                                    contamination=0.01, 
                                    n_estimators=200,
                                    random_state=42
                                )
            df_FILTRO['FLG_MV_OUT'] = (iso.fit_predict(X) == -1)
            texto = """Esse registro é estatisticamente diferente do padrão geral, dada a tipologia, tucagem e não ser atípica.
            Recomendamos revisar o registro analítico no ERP. Exemplo: o custo da UC está incorretamente classificado, ou foi 
            lançado em TI diferente; os custos de CA, COM estão inflando indevidamente certas obras; o 
            custo elevado ou muito baixo tem justificativa técnica (ex.: obra em terreno difícil, tecnologia diferente, 
            reaproveitamento de materiais; item muito antigo no estoque etc).
            """
            df_FILTRO['ANOMALIA'] = np.where(df_FILTRO['FLG_MV_OUT'], texto, 'NO')
            for col in cols_cu:
                df_FILTRO[f'{col}_Zr'] = calc_z(df_FILTRO[col])
                df_FILTRO[f'{col}_Zr_OUT'] = np.abs(df_FILTRO[f'{col}_Zr']) > 3.5

            df_FILTRO['FLG_UV_OUT'] = df_FILTRO[[f'{c}_Zr_OUT' for c in cols_cu]].any(axis=1)

            if len(df_sai):
                df_sai = pd.concat([df_sai, df_FILTRO], ignore_index=True)
            else:
                df_sai = df_FILTRO.copy()  

    def texto_severidade(nivel):
        if nivel == 3:
            return "Outlier Forte (Alta prioridade): valor extremo e estrutura multivariada atípica."
        elif nivel == 2:
            return "Outlier Multivariado (Média prioridade): combinação rara sem valor individual extremo."
        elif nivel == 1:
            return "Outlier Univariado (Baixa prioridade): valor individual extremo sem estrutura atípica."
        else:
            return "Normal (Sem ação)."
    def calc_severidade(row):
        if row['FLG_UV_OUT'] and row['FLG_MV_OUT']:
            return 3
        elif row['FLG_MV_OUT']:
            return 2
        elif row['FLG_UV_OUT']:
            return 1
        else:
            return 0

    df_sai['SEVERIDADE'] = df_sai.apply(calc_severidade, axis=1)
    df_sai['SEVERIDADE_TEXTO'] = df_sai['SEVERIDADE'].apply(texto_severidade)
    df_ordenado = df_sai.sort_values('ANOMALIA').reset_index(drop=True)
    saida = f"{local}\\AIS_ANLS\\ANL_ANOMALIAS_CMU.csv"
    df_ordenado.to_csv(saida, sep='|', index=False, decimal=',')
    df_ordenado['UC_Tupla'] = df_ordenado['UC_Tupla'].apply(lambda x: '|'.join(map(str, x)) if isinstance(x, tuple) else str(x))
    df_ordenado.to_sql('tbl_anomalias_cmu', bd, if_exists='replace', index=False)
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def banda_otima(X, cv=3, seed=None):
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    mask = np.isfinite(X).all(axis=1)
    X = X[mask]
    if len(X) == 0:
        raise ValueError("X ficou vazio após remover NaN/inf.")
    if seed is not None:
        np.random.seed(seed)

    n, d = X.shape
    std = np.std(X, axis=0).mean()

    h_silverman = 1.06 * std * n ** (-1 / (d + 4))

    if len(X) > 1000:
        idx = np.random.choice(len(X), 1000, replace=False)
        X_sub = X[idx]
    else:
        X_sub = X

    h_min = max(h_silverman * 0.3, 1e-3)
    h_max = h_silverman * 3
    grid_vals = np.linspace(h_min, h_max, 10)

    grid = GridSearchCV(
                            KernelDensity(kernel='gaussian'),
                            {'bandwidth': grid_vals},
                            cv=cv,
                            n_jobs=-1
                        )
    grid.fit(X_sub)
    h_best = grid.best_estimator_.bandwidth


    h_refino = np.linspace(h_best * 0.8, h_best * 1.2, 6)
    grid_refino = GridSearchCV(
                                    KernelDensity(kernel='gaussian'),
                                    {'bandwidth': h_refino},
                                    cv=cv,
                                    n_jobs=-1
                                )
    grid_refino.fit(X_sub)
    h_otimo = grid_refino.best_estimator_.bandwidth

    return h_otimo

@monitor_completo(st.session_state.LOGGER)
def TCKdEa1a6(st=None):
    if st == None:
        return "Falhou"
    
    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year

    bd = sl.connect(f'{local}\BD_LOCAL\{empresa}_{ano}.db')

    query = """
    WITH base AS (
                    SELECT Ide_RO_Analitico, Nr_TI, Nr_TUC,
                           Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5, Nr_A6
                    FROM ROA WHERE Cd_NG = 1
                )
                SELECT * FROM base;
    """

    df_atr = pd.read_sql_query(query, bd)
    df_anls = pd.DataFrame()

    grupos = [
        {'filtro': (df_atr['Nr_TUC'] == '565'), 'nome': 'Transformador de Distribuição'},
        {'filtro': (df_atr['Nr_TUC'] == '255') & (df_atr['Nr_A1'] == '1'), 'nome': 'Poste'},
        {'filtro': (df_atr['Nr_TUC'] == '255') & (df_atr['Nr_A1'] == '2'), 'nome': 'Torre'},
        {'filtro': (df_atr['Nr_TUC'] == '295') & (df_atr['Nr_A1'] == '1'), 'nome': 'Medidor Eletromecânico'},
        {'filtro': (df_atr['Nr_TUC'] == '295') & (df_atr['Nr_A1'] == '11'), 'nome': 'Medidor Eletronico'},
        {'filtro': (df_atr['Nr_TUC'] == '125') & (df_atr['Nr_A1'] == '1'),  'nome': 'Banco de Capacitor Parelelo'},
        {'filtro': (df_atr['Nr_TUC'] == '125') & (df_atr['Nr_A1'] == '2'), 'nome': 'Banco de Capacitor Parelelo'},
        {'filtro': (df_atr['Nr_TUC'] == '160'),  'nome': 'Chave'},
        {'filtro': (df_atr['Nr_TUC'] == '190') & (df_atr['Nr_A1'] == '1'),  'nome': 'Condutor (>=69kV)'},
        {'filtro': (df_atr['Nr_TUC'] == '190') & (df_atr['Nr_A1'] == '2'),  'nome': 'Condutor (<69kV)'},
        {'filtro': (df_atr['Nr_TUC'] == '190') & (df_atr['Nr_A1'] == '3'),  'nome': 'Cadeia de Isoladores'},
        {'filtro': (df_atr['Nr_TUC'] == '210') & (df_atr['Nr_A1'] == '1'),  'nome': 'Disjuntor (>=69kV)'},
        {'filtro': (df_atr['Nr_TUC'] == '210') & (df_atr['Nr_A1'] == '2'),  'nome': 'Disjuntor (<69kV)'},
        {'filtro': (df_atr['Nr_TUC'] == '210') & (df_atr['Nr_A1'] == '3'),  'nome': 'Disjuntor (SF6)'},
        {'filtro': (df_atr['Nr_TUC'] == '310') & (df_atr['Nr_A1'] == '1'),  'nome': 'Para-raios'},
        {'filtro': (df_atr['Nr_TUC'] == '340') & (df_atr['Nr_A1'] == '1'),  'nome': 'Regulador'},
        {'filtro': (df_atr['Nr_TUC'] == '345') & (df_atr['Nr_A1'] == '1'),  'nome': 'Religador'},
        {'filtro': (df_atr['Nr_TUC'] == '575') & (df_atr['Nr_A1'] == '1'),  'nome': 'TC'},
        {'filtro': (df_atr['Nr_TUC'] == '575') & (df_atr['Nr_A1'] == '2'),  'nome': 'TC'},
    ]

    a = st.progress(0, "Iniciando")
    total = len(grupos)

    for i, grupo in enumerate(grupos):
        a.progress(
                        int((i + 1) / total * 100),
                        f"Iniciado grupo {grupo['nome']} ({i + 1}/{total})"
                    )

        df_prov = df_atr[grupo['filtro']].copy()
        if df_prov.empty:
            continue

        cols_kde = ['Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6']

        X_df = df_prov[cols_kde].apply(pd.to_numeric, errors='coerce')
        X_np = X_df.to_numpy(dtype=float)

        mask_valid = np.isfinite(X_np).all(axis=1)
        X_valid = X_np[mask_valid]
        df_prov['score_kde'] = np.nan
        df_prov['anomalia'] = 'NO'

        if len(X_valid) > 3:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_valid)

            h_otimo = banda_otima(X_scaled, cv=3)

            idx = np.random.choice(
                                        len(X_scaled),
                                        size=min(1000, len(X_scaled)),
                                        replace=False
                                    )
            X_fit = X_scaled[idx]

            if len(X_fit) == 0:
                raise ValueError("Não há observações válidas após a amostragem para ajuste do KDE.")

            kde = KernelDensity(kernel='gaussian', bandwidth=h_otimo).fit(X_fit)
            scores_valid = kde.score_samples(X_scaled)
            score_series = pd.Series(np.nan, index=df_prov.index, dtype=float)
            score_series.loc[mask_valid] = scores_valid

            df_prov['score_kde'] = score_series

            limiar = np.percentile(scores_valid, 1)
            mask_anom = df_prov['score_kde'] < limiar
            df_prov.loc[mask_anom, 'anomalia'] = (
                                                    f"{grupo['nome']}: valor de atributos com combinação rara."
                                                 )

        df_anom = df_prov[df_prov['anomalia'] != 'NO']
        if not df_anom.empty:
            df_anls = pd.concat([df_anls, df_anom], ignore_index=True)

        a.progress(
                        int((i + 1) / total * 100),
                        f"Concluído grupo {grupo['nome']} ({i + 1}/{total})"
                    )

    saida = f"{local}\\AIS_ANLS\\ANL_ANOMALIAS_ATRIBUTOS_A1A6.csv"
    df_anls.to_csv(saida, sep='|', index=False, decimal=',')
    df_anls.to_sql('tbl_atributos_anomalos_A1A6', bd, if_exists='replace', index=False)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf"{local}\\AIS_ANLS\\ANL_ANOMALIAS_ATRIBUTOS_A1A6.csv",
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        a.empty()
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def TCKdE(st=None):
    if st == None:
        return "Falhou"
    
    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year

    bd = sl.connect(f'{local}\BD_LOCAL\{empresa}_{ano}.db')

    query = """
    WITH base AS (
                    SELECT Ide_RO_Analitico, Nr_TI, Nr_TUC,
                           Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5, Nr_A6
                    FROM ROA WHERE Cd_NG = 1
                )
                SELECT * FROM base;
    """

    df_atr = pd.read_sql_query(query, bd)

    df_anls = pd.DataFrame()

    # Define os grupos e atributos a analisar
    grupos = [
        {'filtro': (df_atr['Nr_TUC'] == '565'), 'atributos': ['Nr_A2', 'Nr_A3', 'Nr_A4'], 'nome': 'Transformador de Distribuição'},
        {'filtro': (df_atr['Nr_TUC'] == '255') & (df_atr['Nr_A1'] == '1'), 'atributos': ['Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5'], 'nome': 'Poste'},
        {'filtro': (df_atr['Nr_TUC'] == '255') & (df_atr['Nr_A1'] == '2'), 'atributos': ['Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5'], 'nome': 'Torre'},
        {'filtro': (df_atr['Nr_TUC'] == '295') & (df_atr['Nr_A1'] == '1'), 'atributos': ['Nr_A2', 'Nr_A3'], 'nome': 'Medidor Eletromecânico'},
        {'filtro': (df_atr['Nr_TUC'] == '295') & (df_atr['Nr_A1'] == '11'), 'atributos': ['Nr_A2', 'Nr_A3'], 'nome': 'Medidor Eletronico'},
        {'filtro': (df_atr['Nr_TUC'] == '125') & (df_atr['Nr_A1'] == '1'), 'atributos': ['Nr_A2', 'Nr_A4'], 'nome': 'Banco de Capacitor Parelelo'},
        {'filtro': (df_atr['Nr_TUC'] == '125') & (df_atr['Nr_A1'] == '2'), 'atributos': ['Nr_A2', 'Nr_A4'], 'nome': 'Banco de Capacitor Parelelo'},
        {'filtro': (df_atr['Nr_TUC'] == '160'), 'atributos': ['Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A6'], 'nome': 'Chave'},
        {'filtro': (df_atr['Nr_TUC'] == '190') & (df_atr['Nr_A1'] == '1'), 'atributos': ['Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5'], 'nome': 'Condutor (>=69kV)'},
        {'filtro': (df_atr['Nr_TUC'] == '190') & (df_atr['Nr_A1'] == '2'), 'atributos': ['Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5'], 'nome': 'Condutor (<69kV)'},
        {'filtro': (df_atr['Nr_TUC'] == '210') & (df_atr['Nr_A1'] == '1'), 'atributos': ['Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A6'], 'nome': 'Disjuntor (>=69kV)'},
        {'filtro': (df_atr['Nr_TUC'] == '210') & (df_atr['Nr_A1'] == '2'), 'atributos': ['Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A6'], 'nome': 'Disjuntor (<69kV)'},
        {'filtro': (df_atr['Nr_TUC'] == '210') & (df_atr['Nr_A1'] == '3'), 'atributos': ['Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A6'], 'nome': 'Disjuntor (SF6)'},
        {'filtro': (df_atr['Nr_TUC'] == '310') & (df_atr['Nr_A1'] == '1'), 'atributos': ['Nr_A2'], 'nome': 'Para-raios'},
        {'filtro': (df_atr['Nr_TUC'] == '340') & (df_atr['Nr_A1'] == '1'), 'atributos': ['Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5'], 'nome': 'Regulador'},
        {'filtro': (df_atr['Nr_TUC'] == '345') & (df_atr['Nr_A1'] == '1'), 'atributos': ['Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A6'], 'nome': 'Religador'},
        {'filtro': (df_atr['Nr_TUC'] == '575') & (df_atr['Nr_A1'] == '1'), 'atributos': ['Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5'], 'nome': 'TC'},
        {'filtro': (df_atr['Nr_TUC'] == '575') & (df_atr['Nr_A1'] == '2'), 'atributos': ['Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5'], 'nome': 'TC'},
    ]

    a = st.progress(0,"Iniciando")
    total = len(grupos)
    for i, grupo in enumerate(grupos):
        a.progress(int((i + 1) / total * 100),
                   f"Iniciado grupo {grupo['nome']} ({i + 1}/{total})")
        df_prov = df_atr[grupo['filtro']].copy()
        if df_prov.empty:
            continue
        for cmp in grupo['atributos']:
            X = df_prov[[cmp]].astype(float).values  # garante tipo numérico
            if len(X)>3:
                X = np.asarray(X, dtype=float)
                if X.ndim == 1:
                    X = X.reshape(-1, 1)
                mask_valid = np.isfinite(X).all(axis=1)
                X_valid = X[mask_valid]
                if len(X_valid) == 0:
                    raise ValueError("Não há observações válidas em X após remover NaN/inf.")

                h_otimo = banda_otima(X, cv=3)
                idx = np.random.choice(len(X), size=min(2000, len(X)), replace=False)
                X_fit = np.asarray(X[idx], dtype=float)

                if X_fit.ndim == 1:
                    X_fit = X_fit[np.isfinite(X_fit)]
                    X_fit = X_fit.reshape(-1, 1)
                else:
                    X_fit = X_fit[np.isfinite(X_fit).all(axis=1)]

                if len(X_fit) == 0:
                    raise ValueError("Não há observações válidas após remover NaN/inf de X[idx].")
                
                kde = KernelDensity(kernel='gaussian', bandwidth=h_otimo).fit(X_fit)
                scores = np.full(X.shape[0], np.nan)
                scores[mask_valid] = kde.score_samples(X_valid)

                df_prov['score_kde'] = scores

                limiar = np.percentile(scores, 1)
                df_prov['anomalia'] = np.where(scores < limiar, f'{grupo["nome"]}: valor de {cmp} anômalo', 'NO')

                df_anom = df_prov[df_prov['anomalia'] != 'NO']
                if not df_anom.empty:
                    df_anls = pd.concat([df_anls, df_anom], ignore_index=True)
            else:
                continue
        a.progress(int((i + 1) / total * 100),
                   f"Concluído grupo {grupo['nome']} ({i + 1}/{total})")

    saida = f"{local}\\AIS_ANLS\\ANL_ANOMALIAS_ATRIBUTOS.csv"
    df_anls.to_csv(saida, sep='|', index=False, decimal=',')
    df_anls.to_sql('tbl_atributos_anomalos', bd, if_exists='replace', index=False)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf"{local}\\AIS_ANLS\\ANL_ANOMALIAS_ATRIBUTOS.csv",
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        a.empty()
    return "OK"

@monitor_completo(st.session_state.LOGGER)    
def _auto_banda_silverman(y: np.ndarray) -> float:
    y = np.asarray(y).ravel()
    n = len(y)
    if n < 2:
        return 0.1
    sigma = np.std(y, ddof=1)
    iqr = np.subtract(*np.percentile(y, [75, 25]))
    h = 0.9 * min(sigma, iqr / 1.34) * n ** (-1/5)
    return max(float(h), 1e-3)

@monitor_completo(st.session_state.LOGGER)
def _auto_banda_cv(
                            y: np.ndarray,
                            sample_weight: np.ndarray | None = None,
                            grid: np.ndarray | None = None,
                            cv: int | None = None,
                            random_state: int | None = 42
                        ) -> float:

    y = np.asarray(y).reshape(-1, 1)
    n = len(y)
    if grid is None:
        grid = np.logspace(-2, 1, 40)
    cv = min(10, n) if (cv is None or cv > n) else cv

    class _KDEw(KernelDensity):
        def fit(self, X, y=None, sample_weight=None):
            return super().fit(X, sample_weight=sample_weight)

    search = GridSearchCV(
        _KDEw(kernel='gaussian'),
        {'bandwidth': grid},
        cv=cv,
        n_jobs=1
    )
    search.fit(y, **({'sample_weight': sample_weight} if sample_weight is not None else {}))
    bw = float(search.best_estimator_.bandwidth)
    return max(bw, 1e-3)

@monitor_completo(st.session_state.LOGGER)
def val_qtd_RTE(
                    df_t0, df_t1, df_t2, cols_chave, col_qtd,
                    relaxar=True, t1 = None, t2 = None,
                    meia_vida_anos=3,
                    usar_cv=True,
                    grid_bw=None,
                    cv_folds=None,
                    banda_min=1e-3,
                    jitter_inteiros=True,
                    jitter_scale=0.05,
                    max_n_ref=5000,
                    seed=42,
                ):

    rng = np.random.default_rng(seed)
    data_t1, data_t2 = map(pd.Timestamp, [t1, t2])

    lam = np.log(2) / float(meia_vida_anos)

    def peso_exp(data):
        delta = (data_t2 - pd.Timestamp(data)).days / 365.0
        return np.exp(-lam * delta)

    w_t1, w_t2 = peso_exp(data_t1), peso_exp(data_t2)

    resultados = []
    df_ref = pd.concat([
                            df_t1.assign(__peso=w_t1),
                            df_t2.assign(__peso=w_t2)
                        ], ignore_index=True)
    df_ref = df_ref.dropna(subset=[col_qtd])

    def achar_referencia(chave_dict):
        if not relaxar:
            mask = np.ones(len(df_ref), dtype=bool)
            for k, v in chave_dict.items():
                mask &= df_ref[k] == v
            grupo = df_ref[mask]
            return grupo, cols_chave

        for i in range(len(cols_chave), 0, -1):
            subset = cols_chave[:i]
            mask = np.ones(len(df_ref), dtype=bool)
            for k in subset:
                mask &= df_ref[k] == chave_dict[k]
            grupo = df_ref[mask]
            if not grupo.empty:
                return grupo, subset
        return pd.DataFrame(), [] 

    for _, linha in df_t0.iterrows():
        chave = {k: linha[k] for k in cols_chave}
        qtd_t0 = float(linha[col_qtd])
        grp, subset = achar_referencia(chave)

        if grp.empty or grp.shape[0] < 2:
            resultados.append({**chave,
                               "nivel_relaxamento": None,
                               "qtd_t0": qtd_t0,
                               "q_low": np.nan, "q_med": np.nan, "q_high": np.nan,
                               "banda": np.nan,
                               "score": 0.0,
                               "metodo": "sem_referencia", "escala": 1.0, "legenda_escala" : "",
                               "modas": 0, "observacao": "Sem dados de referência.",
                               "consistente": None})
            continue

        if grp.shape[0] > max_n_ref:
            grp = grp.iloc[rng.choice(grp.index, size=max_n_ref, replace=False)]

        q_ref = grp[col_qtd].astype(float).to_numpy()
        w_ref = grp["__peso"].astype(float).to_numpy()
        n_ref = len(q_ref)
        metodo = None
        num_modas = 0
        observacao = ""

        max_abs = np.max(np.abs(q_ref))
        if max_abs > 1e3:
            fator_escala = 10 ** np.floor(np.log10(max_abs) - 3)
            q_ref = q_ref / fator_escala
            qtd_t0 = qtd_t0 / fator_escala
            escala_label = f"/{fator_escala:,.0f}"
        else:
            fator_escala = 1.0
            escala_label = ""

        if n_ref < 5:
            qmin, qmax = np.min(q_ref), np.max(q_ref)
            delta = 0.1 + 0.02 * (5 - n_ref)  
            q_low = qmin * (1 - delta)
            q_high = qmax * (1 + delta)
            q_med = np.median(q_ref)
            score = 0.5 
            metodo = "intervalo_empirico"
            observacao = f"Amostra pequena (n={n_ref}). Faixa empírica ±{delta*100:.1f}%."
            resultados.append({
                **chave,
                "nivel_relaxamento": len(subset),
                "qtd_t0": qtd_t0,
                "q_low": q_low, "q_med": q_med, "q_high": q_high,
                "banda": np.nan,
                "score": score,
                "metodo": metodo, "escala": fator_escala, "legenda_escala" : escala_label,
                "modas": 0, "observacao": observacao,
                "consistente": q_low <= qtd_t0 <= q_high
            })
            continue

        if n_ref > max_n_ref:
            grp = grp.iloc[rng.choice(grp.index, size=max_n_ref, replace=False)]
            q_ref = grp[col_qtd].astype(float).to_numpy()
            w_ref = grp["__peso"].astype(float).to_numpy()

        if jitter_inteiros and np.all(np.equal(np.mod(q_ref, 1), 0)):
            q_ref = q_ref + rng.uniform(-jitter_scale, jitter_scale, size=q_ref.size)

        try:
            if usar_cv:
                bw = _auto_banda_cv(q_ref, sample_weight=w_ref, grid=grid_bw, cv=cv_folds, random_state=seed)
                metodo = "kde_cv"
            else:
                raise RuntimeError("CV desativado")
        except Exception:
            bw = _auto_banda_silverman(q_ref)
            metodo = "kde_silverman"

        bw = float(max(bw, banda_min))

        kde = KernelDensity(kernel="gaussian", bandwidth=bw)
        kde.fit(q_ref.reshape(-1, 1), sample_weight=w_ref)
        q_min, q_max = float(q_ref.min()), float(q_ref.max())
        pad = 0.1 * max(1.0, (q_max - q_min))
        grid = np.linspace(q_min - pad, q_max + pad, 400).reshape(-1, 1)
        logdens = kde.score_samples(grid)
        dens = np.exp(logdens)
        dens /= dens.sum()
        cdf = np.cumsum(dens)

        peaks, _ = find_peaks(dens, prominence=0.01)
        num_modas = len(peaks)
        if num_modas >= 2:
            observacao = f"Distribuição multimodal ({num_modas} modas) — interpretação visual recomendada."
        else:
            observacao = "Distribuição unimodal."

        q_low = grid[np.searchsorted(cdf, 0.025)][0]
        q_med = grid[np.searchsorted(cdf, 0.5)][0]
        q_high = grid[np.searchsorted(cdf, 0.975)][0]
        logp = kde.score_samples(np.array([[qtd_t0]]))[0]
        score = float(np.exp(logp - logdens.max()))
        if np.isnan(score) or score < 1e-20:
            score = 0.0

        resultados.append({
            **chave,
            "nivel_relaxamento": len(subset),
            "qtd_t0": qtd_t0,
            "q_low": float(q_low), "q_med": float(q_med), "q_high": float(q_high),
            "banda": bw,
            "score": score,
            "metodo": metodo, "escala": fator_escala, "legenda_escala" : escala_label,
            "modas": num_modas, "observacao": observacao,
            "consistente": (q_low <= qtd_t0 <= q_high)
        })

    return pd.DataFrame(resultados)

@monitor_completo(st.session_state.LOGGER)
def TCKdeIndicadores(st=None):
    if st == None:
        return "Falhou"
    
    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year

    bd = sl.connect(f'{local}\BD_LOCAL\{empresa}_{ano}.db')

    if sql.existe_tabela("ANL_PER_OBRA",bd):
        df = pd.read_sql("SELECT * FROM ANL_PER_OBRA", bd)
    else:
        raise Exception("Erro na leitura da tabela no BD: ANL_PER_OBRA")

    with st.spinner("Avaliando outliers pelos indicadores..."):
        numeric_cols = [
                            "DELTA", "VL_tot", "CTA", "ID_desv_pad", "ID_rev", "IRange",
                            "IED_dias", "KPI_CRESC (%)", "KPI_GAP (dias)", "KPI_PER",
                            "IEg_dias", "IEuc_dias", "CA_TOT", "UC_TOT", "CMD"
                        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col].replace(",","."), errors='coerce')

        results = []
        for ti, group in df.groupby("Nr_TI"):
            
            X = group[numeric_cols].copy()
            
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            iso = IsolationForest(
                                    contamination=0.01,  
                                    random_state=42
                                 )
            
            iso.fit(X_scaled)
            
            scores = iso.decision_function(X_scaled)
            pred = iso.predict(X_scaled)
            
            group_result = group[["Nr_TI", "Cd_SubODI","VL_tot"]].copy()
            group_result["GRAU_ANOMALIA"] = scores
            group_result["FLG_OUT"] = (pred == -1).astype(int)
            
            results.append(group_result)

        df_outliers = pd.concat(results).reset_index(drop=True)

    df_outliers = df_outliers.sort_values(["Nr_TI", "GRAU_ANOMALIA"])
    df_outliers.to_sql('ANL_OUTLIERS_INDICADORES', bd, if_exists='replace', index=False)

    df_outliers.to_csv(rf'{local}\AIS_ANLS\ANL_OUTLIERS_INDICADORES_{empresa}_{ano}.csv', sep="|", decimal=',', encoding="Latin-1", chunksize=100_000)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{local}\AIS_ANLS\ANL_OUTLIERS_INDICADORES_{empresa}_{ano}.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)

    return "Ok"

@monitor_completo(st.session_state.LOGGER)
def identificar_outliers(df, tipo = "Cd_ODD"):
    fases = ['VL_FRT_TRN', 'VL_PRJ', 'VL_GER', 'VL_FISC', 'VL_MONT', 'VL_SUP']
    outliers = {}

    for fase in fases:
        Q1 = df[fase].quantile(0.25)
        Q3 = df[fase].quantile(0.75)
        IQR = Q3 - Q1
        limite_sup = Q3 + 1.5 * IQR

        outliers[fase] = df[df[fase] > limite_sup][[tipo, fase]]

    return outliers

@monitor_completo(st.session_state.LOGGER)
def resumo_por_projeto(df = pd.DataFrame(), tipo = "Cd_ODD", seed = 32, nm_var = 'VL_tot',
                       nm_crit = ['Nr_TI','Cd_SubODI'], st = None):
    
    if seed is not None:
        np.random.seed(seed)    
    df = df.reset_index(drop=True)
    if tipo == "Cd_ODD":
        fases = ['VL_FRT_TRN', 'VL_PRJ', 'VL_GER', 'VL_FISC', 'VL_MONT', 'VL_SUP']
        df['VL_TOT_PRJ'] = df[fases].sum(axis=1)
        resumo = (
                    df.groupby(tipo)[fases + ['VL_TOT_PRJ']]
                    .sum()
                    .sort_values(by='VL_TOT_PRJ', ascending=False)
                    .reset_index()
                )

        resumo['VL_ACUM'] = resumo['VL_TOT_PRJ'].cumsum()
        total_geral = resumo['VL_TOT_PRJ'].sum()
        resumo['Pct_PRJ'] = resumo['VL_TOT_PRJ'] / total_geral
        if isinstance(tipo, list):
            tp_anls = tipo[0] if len(tipo)<=1 else tipo[1]
        else:
            tp_anls = tipo
    else:
        resumo = (
                    df.groupby(nm_crit)[[nm_var]]
                    .sum()
                    .sort_values(by=nm_var, ascending=False)
                    .reset_index()
                )
        resumo['VL_ACUM'] = resumo[nm_var].cumsum()
        total_geral = resumo[nm_var].sum()
        resumo['Pct_PRJ'] = resumo[nm_var] / total_geral
        if isinstance(nm_crit, list):
            tp_anls = nm_crit[0] if len(nm_crit)<=1 else nm_crit[1]
        else:
            tp_anls = nm_crit
    
    resumo['Pct_ACM'] = resumo['Pct_PRJ'].cumsum()
    resumo['CLS_ABC'] = resumo['Pct_ACM'].apply(
                                                    lambda x: 'A' if x <= 0.80 else ('B' if x <= 0.95 else 'C')
                                                )

    N = len(resumo)
    res, risco = bsc_nr_amst(N=N, confianca=0.95, erro_aceitavel=0.05, erros_esperados=0)
    tamanho_amostra = res['tamanho_amostra']
    res["tamanho_amostra"] = f"{res['tamanho_amostra']:,.2f}".replace(",","x").replace(".",",").replace("x",".")
    res["metodo"] = f"{res['metodo']}"
    res["nivel_confianca"] = f"{res['nivel_confianca']:,.2%}".replace(",","x").replace(".",",").replace("x",".")
    res["erro_aceitavel"] = f"{res['erro_aceitavel']:,.2%}".replace(",","x").replace(".",",").replace("x",".")
    res["erros_esperados"] = f"{res['erros_esperados']:,.2f}".replace(",","x").replace(".",",").replace("x",".")
    res["tamanho_populacao"] = f"{res['tamanho_populacao']:,.2f}".replace(",","x").replace(".",",").replace("x",".")
    res["max_erros_aceitaveis"] = f"{res['max_erros_aceitaveis']:,.2f}".replace(",","x").replace(".",",").replace("x",".")
    risco["risco_real"] = f"{risco['risco_real']:,.2%}".replace(",","x").replace(".",",").replace("x",".")
    risco["nivel_confianca_real"] = f"{risco['nivel_confianca_real']:,.2%}".replace(",","x").replace(".",",").replace("x",".")

    texto_anl = (
                    f"<p  style='text-align: justify;text-indent: 40px'>Com base no método {res['metodo']}, foi calculado um tamanho de amostra de "
                    f"{res['tamanho_amostra']} indivíduos para uma população de {res['tamanho_populacao']}, "
                    f"considerando nível de confiança de {res['nivel_confianca']}, erro aceitável de "
                    f"{res['erro_aceitavel']} e {res['erros_esperados']} erros esperados; ao aplicar esse "
                    f"plano amostral, obteve-se um risco real de {risco['risco_real']} e um nível de "
                    f"confiança real de {risco['nivel_confianca_real']}.</p>"
                )

    IA = total_geral / tamanho_amostra
    R = np.random.uniform(0, IA)
    pontos = [R + i * IA for i in range(tamanho_amostra)]
    amostra_final = []
    selecionados = set()

    for p in pontos:
        linha = resumo[resumo['VL_ACUM'] >= p].head(1)
        if linha.empty:
            continue
        if isinstance(tp_anls, list):
            col = tp_anls[0]
        else:
            col = tp_anls
        try:
            proj = linha.loc[linha.index[0], col]    
        except:
            proj = linha.iloc[0,0]  
        
        if proj in selecionados:
            idx = resumo.loc[(resumo[col] == proj) & resumo[col].notnull()].index[0]
            while idx < len(resumo) and resumo.loc[idx, col] in selecionados:
                idx += 1
            if idx < len(resumo):
                proj = resumo.loc[idx, col]
            else:
                continue
        
        amostra_final.append(proj)
        selecionados.add(proj)

    amostra_final = list(dict.fromkeys(amostra_final))
    resumo['FLG_AMST'] = resumo[tp_anls].isin(amostra_final).astype(int)

    return resumo, amostra_final, IA, R, texto_anl

@monitor_completo(st.session_state.LOGGER)
def maior_impacto(df, col_valor='DV', limite=0.80):

    df_aux = df[[col_valor]].copy()
    df_aux['abs_valor'] = df_aux[col_valor].abs()
    df_aux_ord = df_aux.sort_values(by='abs_valor', ascending=False)
    total_abs = df_aux_ord['abs_valor'].sum()
    df_aux_ord['contrib'] = df_aux_ord['abs_valor'] / total_abs
    df_aux_ord['acumulado'] = df_aux_ord['contrib'].cumsum()
    idx_top = df_aux_ord[df_aux_ord['acumulado'] <= limite].index.tolist()

    if df_aux_ord['acumulado'].iloc[len(idx_top)] < limite:
        idx_top.append(df_aux_ord.index[len(idx_top)])
    df['FLG_EXP'] = 0
    df.loc[df.index.isin(idx_top), 'FLG_EXP'] = 1
    return df

@monitor_completo(st.session_state.LOGGER)
def analise_FISHER(df_at: pd.DataFrame, y1: float | None = None, y2: float | None = None):
    
    cols = ['ativo','un','p1','q1','p2','q2']
    df_at.columns = cols
    
    df = df_at.copy()

    for col in ['p1','q1','p2','q2']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    
    C1 = float((df['p1'] * df['q1']).sum())
    C2 = float((df['p2'] * df['q2']).sum())
    dC = C2 - C1
    
    EP_L = float(((df['p2'] - df['p1']) * df['q1']).sum())
    EP_P = float(((df['p2'] - df['p1']) * df['q2']).sum())
    EP_F = 0.5 * (EP_L + EP_P)
    
    EQ_L = float(((df['q2'] - df['q1']) * df['p1']).sum())
    EQ_P = float(((df['q2'] - df['q1']) * df['p2']).sum())
    EQ_F = 0.5 * (EQ_L + EQ_P)
    
    denom_L_preco = float((df['p1'] * df['q1']).sum())
    num_L_preco   = float((df['p2'] * df['q1']).sum())
    PL = (num_L_preco / denom_L_preco) if denom_L_preco != 0 else np.nan
    
    denom_P_preco = float((df['p1'] * df['q2']).sum())
    num_P_preco   = float((df['p2'] * df['q2']).sum())
    PP = (num_P_preco / denom_P_preco) if denom_P_preco != 0 else np.nan
    
    PF = sqrt(PL * PP) if (PL > 0 and PP > 0) else np.nan
    
    denom_L_qty = float((df['p1'] * df['q1']).sum())
    num_L_qty   = float((df['p1'] * df['q2']).sum())
    QL = (num_L_qty / denom_L_qty) if denom_L_qty != 0 else np.nan
    
    denom_P_qty = float((df['p2'] * df['q1']).sum())
    num_P_qty   = float((df['p2'] * df['q2']).sum())
    QP = (num_P_qty / denom_P_qty) if denom_P_qty != 0 else np.nan
    
    QF = sqrt(QL * QP) if (QL > 0 and QP > 0) else np.nan
    
    razao_check = (C2 / C1) if C1 != 0 else np.nan
    razao_fisher = PF * QF if (not np.isnan(PF) and not np.isnan(QF)) else np.nan
    check_fech = (abs(razao_check - razao_fisher) < 1e-8) if (not np.isnan(razao_check) and not np.isnan(razao_fisher)) else False
    
    prod_index = np.nan
    prod_pct = np.nan
    unit_custo_razao = np.nan
    if y1 is not None and y2 is not None and y1 != 0 and y2 != 0:
        prod_index = (y2 / y1) / QF if (QF and QF != 0 and not np.isnan(QF)) else np.nan
        prod_pct = (prod_index - 1.0) * 100.0 if not np.isnan(prod_index) else np.nan
        unit_custo_razao = ( (C2 / y2) / (C1 / y1) ) if (C1 != 0 and y1 != 0) else np.nan
    
    sumario = {
                    'C1_total': [C1],
                    'C2_total': [C2],
                    'Delta_C': [dC],
                    'EP_Fisher': [EP_F],
                    'EQ_Fisher': [EQ_F],
                    'EP_mais_EQ_igual_DeltaC': [abs((EP_F + EQ_F) - dC) < 1e-8],
                    'Indice_Preco_Fisher(PF)': [PF],
                    'Indice_Quantidade_Fisher(QF)': [QF],
                    'C2/C1': [razao_check],
                    'PF*QF': [razao_fisher],
                    'Check_(C2/C1 == PF*QF)': [check_fech],
                    'Prod_Ind_(saida_vs_ent_qdt)': [prod_index],
                    'Prod_%_var': [prod_pct],
                    'Unit_custo_razao_((C2/y2)/(C1/y1))': [unit_custo_razao],
                    'y1': [y1],
                    'y2': [y2]
                }
    df_res = pd.DataFrame(sumario)
    
    df_dt = df[['ativo','un','p1','q1','p2','q2']].copy()
    df_dt['Custo1'] = df_dt['p1']*df_dt['q1']
    df_dt['Custo2'] = df_dt['p2']*df_dt['q2']
    df_dt['DeltaCusto'] = df_dt['Custo2'] - df_dt['Custo1']
    df_dt['EP_L'] = (df_dt['p2'] - df_dt['p1']) * df_dt['q1']
    df_dt['EP_P'] = (df_dt['p2'] - df_dt['p1']) * df_dt['q2']
    df_dt['EP_F'] = 0.5 * (df_dt['EP_L'] + df_dt['EP_P'])
    df_dt['EQ_L'] = (df_dt['q2'] - df['q1']) * df_dt['p1']
    df_dt['EQ_P'] = (df_dt['q2'] -df_dt['q1']) * df_dt['p2']
    df_dt['EQ_F'] = 0.5 * (df_dt['EQ_L'] + df_dt['EQ_P'])
    
    cols = ['ativo','un','p1','q1','p2','q2','Custo1','Custo2','DeltaCusto','EP_F','EQ_F','EP_L','EP_P','EQ_L','EQ_P']
    df_dt = df_dt[cols]
    
    return df_res, df_dt

def sel_projetos(df, coluna_valor='soma_estornos', coluna_projeto = 'projeto', limite=60, seed=42):
    np.random.seed(seed)
    
    df = df.copy()
    df['VL_ABS'] = df[coluna_valor].abs()
    df = df.sort_values(by='VL_ABS', ascending=False)
    total = df['VL_ABS'].sum()
    df['VL_PROB'] = df['VL_ABS'] / total
    
    n_validos = (df['VL_PROB'] > 0).sum()
    if (df['VL_PROB'] > 0).sum() == 0:
        selecionados = []
    else:
        n = min(limite, (df['VL_PROB'] > 0).sum())
        selecionados = df.sample(
                                n=n,
                                weights=df['VL_PROB'],
                                replace=False,
                                random_state=seed
                             )[coluna_projeto].tolist()
    df['FLG_AMST'] = False
    df.loc[df[coluna_projeto].isin(selecionados), 'FLG_AMST'] = True
    df['VL_ACUM'] = df['VL_ABS'].cumsum()
    df['Pct_ACUM'] = df['VL_ACUM'] / total
    df['CLS_ABC'] = 'A'
    df.loc[df['Pct_ACUM']>=0.85, 'CLS_ABC'] = 'B'
    df.loc[df['Pct_ACUM']>=0.95, 'CLS_ABC'] = 'C'
    
    return selecionados, df[[coluna_projeto,'VL_ABS','VL_PROB','FLG_AMST','CLS_ABC','VL_ACUM']].reset_index(drop=True)

def enc_outliers(df: pd.DataFrame | None, grupo, valor: str | None) -> pd.DataFrame:
    df = df.copy()
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

def sorteio(df: pd.DataFrame | None, 
            coluna_valor: str | None, 
            coluna_identificador: str | None, 
            n: Optional[int] = None,
            seed: Optional[int] = 32,
            lista_extra: Optional[List] = None,
            sorteados: Optional[List] = None,
            metodo: str = "Simples",
            tipo = "Cd_ODI",
            st = None) -> pd.DataFrame:

    if seed is not None:
        np.random.seed(seed)

    if n is None:
        res, risco = bsc_nr_amst(N=len(df), confianca=0.95, erro_aceitavel=0.05, erros_esperados=0)
        n = res['tamanho_amostra']

    df = df.sort_values(by=coluna_valor, ascending =False).reset_index(drop=True)
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
    
    if metodo == "Simples":
        amostra = df.groupby("Intervalo").apply(lambda x: x.sample(1))
        if lista_extra:
            extras = df[df['Cd_SubODI'].isin(lista_extra)].copy()
        else:
            extras = pd.DataFrame()

        resultados.append(amostra[coluna_identificador + [coluna_valor, "Limite_Inferior", "Limite_Superior"]].reset_index(drop=True))
        if len(extras):
            resultados.append(extras[coluna_identificador + [coluna_valor, "Limite_Inferior", "Limite_Superior"]].reset_index(drop=True))

        return pd.concat(resultados).reset_index(drop=True)
    elif metodo == "Ponderada":       
        return sel_projetos(df, coluna_valor=coluna_valor, coluna_projeto = coluna_identificador, limite=n, seed=seed)
    elif metodo == "AUM":
        return resumo_por_projeto(df, tipo = tipo, seed = seed, nm_var = coluna_valor, nm_crit = [coluna_identificador], st=st)