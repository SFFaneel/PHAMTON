import pandas as pd, numpy as np
import time

from datetime import datetime, date
import matplotlib.pyplot as plt
from scipy import stats
import os, geopandas as gpd
from scipy.signal import savgol_filter, find_peaks
from scipy.stats import bootstrap

import UTILS.sqlfnc as sql
from UTILS.sqlfnc import existe_tabela, max_arq
from UTILS import monitor_completo, sortear_amostra_bdgd
from RELATORIOS.imprimir_xlsx import ax_escreve_excel_md2
from MANIFESTO import (
                        registrar_artefato,
                        registrar_evento
                      )

import sqlite3 as sl
from typing import Iterable, List, Dict, Optional
import streamlit as st
import xlsxwriter
from dbfread import DBF
from pathlib import Path

os.environ["SHAPE_RESTORE_SHX"] = "YES"

@monitor_completo(st.session_state.LOGGER)
def conciliar(
                df_FIS: pd.DataFrame,
                df_CTB: pd.DataFrame,
                chaves: list[list[str]],
                fis_val_col: str = "VL_TOTAL",
                ctb_val_col: str = "VL_VOC",
                sai_col: str = "VL_AJST",
                decimal: int | None = None,
            ):
    """
    Ajusta df_FIS para fechar com df_CTB em cada nível de chave.
    Retorna df_FIS com coluna sai_col ajustada + flags FLG_NCL/FLG_CONC.
    """
    df = df_FIS.copy().reset_index(drop=True)

    if "_row_id" not in df.columns:
        df["_row_id"] = np.arange(len(df))

    # coluna de saída
    if sai_col not in df.columns:
        df[sai_col] = pd.to_numeric(df[fis_val_col], errors="coerce").fillna(0.0)
    else:
        df[sai_col] = pd.to_numeric(df[sai_col], errors="coerce").fillna(0.0)

    # flags
    if "FLG_NCL" not in df.columns:
        df["FLG_NCL"] = False

    # CTB normalizado
    ctb = df_CTB.copy()
    ctb[ctb_val_col] = pd.to_numeric(ctb[ctb_val_col], errors="coerce").fillna(0.0)

    def aplicar_ajuste_nivel(df_grp: pd.DataFrame, meta_total: float):
        soma_atual = df_grp[sai_col].sum()
        if np.isclose(soma_atual, 0.0):
            # distribuição por Qtd_BDGD se existir e somar > 0; senão uniforme por quantidade de linhas
            if "Qtd_BDGD" in df_grp.columns:
                peso = pd.to_numeric(df_grp["Qtd_BDGD"], errors="coerce").fillna(0.0)
                wsum = peso.sum()
                if wsum > 0:
                    df_grp[sai_col] = (peso / wsum) * meta_total
                    return df_grp
            n = len(df_grp)
            if n > 0:
                df_grp[sai_col] = meta_total / n
            return df_grp
        fator = meta_total / soma_atual
        df_grp[sai_col] = df_grp[sai_col] * fator
        return df_grp

    for k in chaves:
        meta_nivel = (
            ctb.groupby(k, dropna=False, as_index=False)[ctb_val_col]
            .sum()
            .rename(columns={ctb_val_col: "__meta__"})
        )

        trab = df.merge(meta_nivel, on=k, how="left", sort=False)
        trab["FLG_NCL_lvl"] = trab["__meta__"].isna()
        trab["__meta__"] = trab["__meta__"].fillna(trab[sai_col])
        def ajustar(grp):
            meta = grp["__meta__"].iloc[0]
            return aplicar_ajuste_nivel(grp, meta)

        trab = (
            trab.groupby(k, group_keys=False, dropna=False)
                .apply(ajustar)
                .reset_index(drop=True)
        )

        df = df.merge(
            trab[["_row_id", sai_col, "FLG_NCL_lvl"]],
            on="_row_id", how="left", suffixes=("", "_new")
        )
        df[sai_col] = df[f"{sai_col}_new"].fillna(df[sai_col])
        df["FLG_NCL"] = df["FLG_NCL"] | trab.set_index("_row_id")["FLG_NCL_lvl"].reindex(df["_row_id"]).fillna(False).values
        df.drop(columns=[f"{sai_col}_new", "FLG_NCL_lvl"], inplace=True)

    # arredondamento final opcional
    if decimal is not None:
        df[sai_col] = df[sai_col].round(decimal)
    # flag conciliado (opcionalmente 0/1)
    df["FLG_CONC"] = (~df["FLG_NCL"]).astype(int)

    return df

@monitor_completo(st.session_state.LOGGER)
def _sql_rm(nmLD: str, suf: str) -> str:
    return f"""
                WITH base AS (
                SELECT
                    'Ramal' AS TipoEquipamento,
                    L.COD_ID AS CodigoLinha,
                    T1.NOME   AS NomeLinha,
                    T1.TEN_NOM AS TensaoLinha,
                    T1.DESCR  AS DescrLinha, L.UNI_TR_MT, L.UNI_TR_AT,
                    L.CONJ, L.SUB, L.ODI, L.TI, L.CM,
                    COALESCE(COND.TUC_FAS, COND.TUC_NEU) AS TUC,
                    COALESCE(COND.A1_FAS,  COND.A1_NEU)  AS A1,
                    COALESCE(COND.A2_FAS,  COND.A2_NEU)  AS A2,
                    COALESCE(COND.A3_FAS,  COND.A3_NEU)  AS A3,
                    COALESCE(COND.A4_FAS,  COND.A4_NEU)  AS A4,
                    COALESCE(COND.A5_FAS,  COND.A5_NEU)  AS A5,
                    COALESCE(COND.A6_FAS,  COND.A6_NEU)  AS A6,
                    L.FAS_CON, COND.CND_FAS, COND.FTRCNV, COND.UAR,
                    L.SITCONT, L.COMP,
                    CASE
                    WHEN COND.FORM_CAB IN (0,1) THEN 'Singelo'
                    WHEN COND.FORM_CAB = 2     THEN 'Multiplexado Duplex'
                    WHEN COND.FORM_CAB = 3     THEN 'Multiplexado Triplex'
                    WHEN COND.FORM_CAB = 4     THEN 'Multiplexado Quadruplex'
                    WHEN COND.FORM_CAB = 5     THEN 'Interno de subestação'
                    WHEN COND.FORM_CAB = 6     THEN 'Concêntrico Monofásico'
                    WHEN COND.FORM_CAB = 7     THEN 'Concêntrico Bifásico'
                    WHEN COND.FORM_CAB = 8     THEN 'Concêntrico Trifásico'
                    ELSE 'Código inválido'
                    END AS TP_CABO,
                    CASE
                    WHEN COND.FORM_CAB IN (1,6) THEN 1
                    WHEN COND.FORM_CAB IN (2,7) THEN 2
                    WHEN COND.FORM_CAB IN (3,8) THEN 3
                    WHEN COND.FORM_CAB = 4 THEN 4
                    ELSE 1
                    END AS COND_CABO
                FROM {nmLD}{suf} L
                LEFT JOIN CTMT{suf} T1 ON L.CTMT = T1.COD_ID
                LEFT JOIN SEGCON{suf} COND ON L.TIP_CND = COND.COD_ID
                WHERE L.TIP_INST IN ('RD_AER_URB','RD_AER_RUR', 'RD_SUBT_URB', 'RD_SUBT_RUR', 'RD_SUBM')
                    AND L.SITCONT IN ('AT1','SF','RT') AND L.POS = 'PD'
                ),
                calc AS (
                SELECT
                    *,
                    CAST(((LENGTH(FAS_CON) + COND_CABO - 1) * 1.0 / COND_CABO) AS INTEGER) AS CABOS_FISICOS
                FROM base
                )
                SELECT
                TipoEquipamento, CodigoLinha, NomeLinha, TensaoLinha, UNI_TR_MT, UNI_TR_AT, SUB,
                DescrLinha, CONJ, ODI, TI, CM,
                TUC, A1, A2, A3, A4, A5, A6,
                FAS_CON, CND_FAS, FTRCNV, TP_CABO, COND_CABO, CABOS_FISICOS,
                UAR, SITCONT,
                COALESCE(SUM(COMP * CABOS_FISICOS * CND_FAS), 0)                 AS Qtd_BDGD_m,
                COALESCE(SUM(COMP * CABOS_FISICOS * CND_FAS * FTRCNV), 0)        AS Qtd_BDGD_kg
                FROM calc
                GROUP BY
                TipoEquipamento, CodigoLinha, NomeLinha, TensaoLinha, UNI_TR_MT, UNI_TR_AT, SUB,
                DescrLinha, CONJ, ODI, TI, CM,
                TUC, A1, A2, A3, A4, A5, A6,
                FAS_CON, CND_FAS, FTRCNV, TP_CABO, COND_CABO, CABOS_FISICOS, UAR, SITCONT
                ;"""

@monitor_completo(st.session_state.LOGGER)
def texto_explicativo_rm(nmLD: str) -> str:
    return f"""
                <p style="text-align: justify; text-indent: 40px">
                Para cada ramal, calculamos as quantidades físicas de condutores modeladas na BDGD,
                agrupadas por atributos técnicos (ex.: código da linha, tensão, configuração de fases e tipo de cabo). 
                A consulta integra cadastro (RAMAL) e características de condutores (SEGCON).
                A coluna <b>CABOS_FISICOS</b> aplica arredondamento para cima conforme a relação entre fases e condutores por cabo, e
                <b>Qtd_BDGD</b> consolida comprimento ponderado por cabos físicos e número de condutores por fase, promovendo uma
                quantificação coerente da materialidade dos circuitos para fiscalização e alocação patrimonial.
                </p>
                <hr/>
                """

@monitor_completo(st.session_state.LOGGER)
def texto_exp_postes_rm(nmLD: str) -> str:
    return f"""
                <p style="text-align: justify; text-indent: 40px">
                Também, buscamos as estruturas de suporte associadas aos ramais, vinculando cada registro 
                ao circuito (CTMT) e ao conjunto (CONJ). Os dados são obtidos de RD_ESTR em junção com 
                o cadastro de linhas (CTMT) e, obtidas por meio da tabela de pontos notáveis 
                (PN_CON_1/PN_CON_2). Aplica-se filtro por TIP_INST ('RD_AER_URB','RD_AER_RUR', 'RD_SUBT_URB', 'RD_SUBT_RUR', 'RD_SUBM') e SITCONT (AT1, SF, RT) 
                para refletir ativos em operação. Cada estrutura é qualificada por atributos técnicos — TIP_PN 
                (tipo de ponto), ESTR (tipologia da estrutura), MAT (material) e ESF (classe de esforço) — 
                com padronização de ausências como “ND”, garantindo consistência de rótulos. Lembre-se, estruturas podem
                ser compartilhadas por mais de um circuito. Por isso, temos duas colunas para indicar os circuitos que
                usam a estrutura.
                </p>
                <hr/>
                """
@monitor_completo(st.session_state.LOGGER)
def cnt_bloco_rm(nmLD: str, suf: str, bd, tabelas_existentes: set, st = None):
    if f"{nmLD}{suf}" not in tabelas_existentes:
        texto = f"<p style='text-align: justify; text-indent: 40px'>Não há ramais nesta empresa.</p><hr/>",
        return texto, pd.DataFrame()

    texto = texto_explicativo_rm(nmLD)
    sqlq = _sql_rm(nmLD, suf)
    df = pd.read_sql(sqlq, bd)
    if len(df):
        return texto, df
    else:
        label = nmLD[-2:]
        texto = f"<p style='text-align: justify; text-indent: 40px'>Não há linhas para ramal nesta empresa.</p><hr/>"
        return texto, pd.DataFrame()

@monitor_completo(st.session_state.LOGGER)
def ponnot_filtrados_rm(nmLD: str, suf: str) -> str:
    xx  = "MT"
    tbl = f"{nmLD}{suf}"
    return f"""
            WITH base AS (
                            SELECT PN_CON_1 AS PN, CT{xx} AS CT
                            FROM {tbl}
                            WHERE TIP_INST IN ('RD_AER_URB','RD_AER_RUR', 'RD_SUBT_URB', 'RD_SUBT_RUR', 'RD_SUBM')
                            UNION ALL
                            SELECT PN_CON_2 AS PN, CT{xx} AS CT
                            FROM {tbl}
                            WHERE TIP_INST IN ('RD_AER_URB','RD_AER_RUR', 'RD_SUBT_URB', 'RD_SUBT_RUR', 'RD_SUBM')
                        ),
                clean AS (
                            SELECT PN, CT
                            FROM base
                            WHERE PN IS NOT NULL AND PN <> '' AND CT IS NOT NULL AND CT <> ''
                            GROUP BY PN, CT
                        ),
                pn_agg AS (
                            SELECT
                                PN,
                                COUNT(*)                         AS CT_QTDE,
                                GROUP_CONCAT(CT, ',')            AS CT_LIST,
                                json_group_array(CT)             AS CT_JSON   -- requer JSON1 (SQLite)
                            FROM clean
                            GROUP BY PN
                            )
                SELECT
                    t.COD_ID,
                    t.TIP_PN, t.ESTR, t.MAT, t.ESF, t.ALT,
                    t.CONJ, t.MUN, t.ODI, t.TI, t.CM,
                    t.TUC, t.A1, t.A2, t.A3, t.A4, t.A5, t.A6, t.UAR,
                    t.SITCONT, t.DESCR,
                    1 AS Qtd_BDGD,
                    p.CT_QTDE,
                    p.CT_LIST,
                    p.CT_JSON
                FROM PONNOT{suf} t
                LEFT JOIN pn_agg p
                ON p.PN = t.COD_ID
                WHERE t.SITCONT IN ('AT1','SF','RT') AND t.TI IN (93, 96,'93','96')
                AND TIP_INST IN ('RD_AER_URB','RD_AER_RUR', 'RD_SUBT_URB', 'RD_SUBT_RUR', 'RD_SUBM');
            """

@monitor_completo(st.session_state.LOGGER)
def _mk_ax_rd(nmLD: str):
    """Campos extras (para SSDMT e SSDBT). Retorna tuple: (select_extra, group_by_extra, label_setor)"""
    if nmLD in ["SSDMT", "SSDBT"]:
        select_extra = "T1.BARR, T1.SUB, T1.UNI_TR_AT,"
        group_extra  = "BARR, SUB, UNI_TR_AT,"
        label = "MT"
    else:
        select_extra = ""
        group_extra  = ""
        label = "AT"
    return select_extra, group_extra, label

@monitor_completo(st.session_state.LOGGER)
def _sql_rd(nmLD: str, suf: str) -> str:
    sel_extra, grp_extra, label = _mk_ax_rd(nmLD)
    return f"""
                WITH base AS (
                SELECT
                    'RD_{nmLD[-2:]}' AS TipoEquipamento,
                    L.COD_ID AS CodigoLinha,
                    T1.NOME   AS NomeLinha,
                    T1.TEN_NOM AS TensaoLinha,
                    T1.DESCR  AS DescrLinha, {sel_extra}
                    L.CONJ, L.CT_COD_OP, L.ODI, L.TI, L.CM,
                    COALESCE(COND.TUC_FAS, COND.TUC_NEU) AS TUC,
                    COALESCE(COND.A1_FAS,  COND.A1_NEU)  AS A1,
                    COALESCE(COND.A2_FAS,  COND.A2_NEU)  AS A2,
                    COALESCE(COND.A3_FAS,  COND.A3_NEU)  AS A3,
                    COALESCE(COND.A4_FAS,  COND.A4_NEU)  AS A4,
                    COALESCE(COND.A5_FAS,  COND.A5_NEU)  AS A5,
                    COALESCE(COND.A6_FAS,  COND.A6_NEU)  AS A6,
                    L.FAS_CON, COND.CND_FAS, COND.FTRCNV, COND.UAR,
                    L.SITCONT, L.COMP,
                    CASE
                    WHEN COND.FORM_CAB IN (0,1) THEN 'Singelo'
                    WHEN COND.FORM_CAB = 2     THEN 'Multiplexado Duplex'
                    WHEN COND.FORM_CAB = 3     THEN 'Multiplexado Triplex'
                    WHEN COND.FORM_CAB = 4     THEN 'Multiplexado Quadruplex'
                    WHEN COND.FORM_CAB = 5     THEN 'Interno de subestação'
                    WHEN COND.FORM_CAB = 6     THEN 'Concêntrico Monofásico'
                    WHEN COND.FORM_CAB = 7     THEN 'Concêntrico Bifásico'
                    WHEN COND.FORM_CAB = 8     THEN 'Concêntrico Trifásico'
                    ELSE 'Código inválido'
                    END AS TP_CABO,
                    CASE
                    WHEN COND.FORM_CAB IN (1,6) THEN 1
                    WHEN COND.FORM_CAB IN (2,7) THEN 2
                    WHEN COND.FORM_CAB IN (3,8) THEN 3
                    WHEN COND.FORM_CAB = 4 THEN 4
                    ELSE 1
                    END AS COND_CABO
                FROM {nmLD}{suf} L
                LEFT JOIN CT{label}{suf} T1 ON L.CT{label} = T1.COD_ID
                LEFT JOIN SEGCON{suf}    COND ON L.TIP_CND = COND.COD_ID
                WHERE L.TIP_INST IN ('RD_AER_URB','RD_AER_RUR', 'RD_SUBT_URB', 'RD_SUBT_RUR', 'RD_SUBM')
                    AND L.SITCONT IN ('AT1','SF','RT')
                ),
                calc AS (
                SELECT
                    *,
                    CAST(((LENGTH(FAS_CON) + COND_CABO - 1) * 1.0 / COND_CABO) AS INTEGER) AS CABOS_FISICOS
                FROM base
                )
                SELECT
                TipoEquipamento, CodigoLinha, NomeLinha, TensaoLinha, {grp_extra}
                DescrLinha, CONJ, CT_COD_OP, ODI, TI, CM,
                TUC, A1, A2, A3, A4, A5, A6,
                FAS_CON, CND_FAS, FTRCNV, TP_CABO, COND_CABO, CABOS_FISICOS,
                UAR, SITCONT,
                COALESCE(SUM(COMP * CABOS_FISICOS * CND_FAS), 0)                 AS Qtd_BDGD_m,
                COALESCE(SUM(COMP * CABOS_FISICOS * CND_FAS * FTRCNV), 0)        AS Qtd_BDGD_kg
                FROM calc
                GROUP BY
                TipoEquipamento, CodigoLinha, NomeLinha, TensaoLinha, {grp_extra}
                DescrLinha, CONJ, CT_COD_OP, ODI, TI, CM,
                TUC, A1, A2, A3, A4, A5, A6,
                FAS_CON, CND_FAS, FTRCNV, TP_CABO, COND_CABO, CABOS_FISICOS, UAR, SITCONT
                ;"""

@monitor_completo(st.session_state.LOGGER)
def texto_explicativo_rd(nmLD: str) -> str:
    _, _, label = _mk_ax_rd(nmLD)
    return f"""
                <p style="text-align: justify; text-indent: 40px">
                Para cada rede (no caso, RD {nmLD[-2:]}), calculamos as quantidades físicas de condutores modeladas na BDGD,
                agrupadas por atributos técnicos (ex.: código da linha, tensão, configuração de fases e tipo de cabo). A consulta integra
                cadastro (CT{nmLD[-2:]}), segmentos ({nmLD}) e características de condutores (SEGCON).
                A coluna <b>CABOS_FISICOS</b> aplica arredondamento para cima conforme a relação entre fases e condutores por cabo, e
                <b>Qtd_BDGD</b> consolida comprimento ponderado por cabos físicos e número de condutores por fase, promovendo uma
                quantificação coerente da materialidade dos circuitos para fiscalização e alocação patrimonial.
                </p>
                <hr/>
                """

@monitor_completo(st.session_state.LOGGER)
def texto_exp_postes_rd(nmLD: str) -> str:
    label = nmLD[-2:]
    return f"""
                <p style="text-align: justify; text-indent: 40px">
                Também, buscamos as estruturas de suporte associadas às linhas (RD {label}), vinculando cada registro 
                ao circuito (CT{label}) e ao conjunto (CONJ). Os dados são obtidos de RD_ESTR_{label} em junção com 
                o cadastro de linhas (CT{label}) e, obtidas por meio da tabela de pontos notáveis 
                (PN_CON_1/PN_CON_2). Aplica-se filtro por TIP_INST ('RD_AER_URB','RD_AER_RUR', 'RD_SUBT_URB', 'RD_SUBT_RUR', 'RD_SUBM') e SITCONT (AT1, SF, RT) 
                para refletir ativos em operação. Cada estrutura é qualificada por atributos técnicos — TIP_PN 
                (tipo de ponto), ESTR (tipologia da estrutura), MAT (material) e ESF (classe de esforço) — 
                com padronização de ausências como “ND”, garantindo consistência de rótulos. Lembre-se, estruturas podem
                ser compartilhadas por mais de um circuito. Por isso, temos duas colunas para indicar os circuitos que
                usam a estrutura.
                </p>
                <hr/>
                """

@monitor_completo(st.session_state.LOGGER)
def cnt_bloco_rd(nmLD: str, suf: str, bd, tabelas_existentes: set, st=None):
    if f"{nmLD}{suf}" not in tabelas_existentes:
        label = nmLD[-2:]
        texto = f"<p style='text-align: justify; text-indent: 40px'>Não há redes para {label} nesta empresa.</p><hr/>"
        return texto, pd.DataFrame()
    
    if (not sql.existe_tabela(f"CT{nmLD[-2:]}_AT", bd)) and (nmLD[-2:] != 'BT'):
        texto = f"<p style='text-align: justify; text-indent: 40px'>Não há linhas para CT{nmLD[-2:]}_AT nesta empresa.</p><hr/>"
        return texto, pd.DataFrame()
    
    texto = texto_explicativo_rd(nmLD)
    sqlq = _sql_rd(nmLD, suf)
    df = pd.read_sql(sqlq, bd)
    if len(df)>0:
        return texto, df
    else:
        label = nmLD[-2:]
        return texto, pd.DataFrame()

@monitor_completo(st.session_state.LOGGER)
def ponnot_filtrados_rd(nmLD: str, suf: str) -> str:
    _, _, xx  = _mk_ax_rd(nmLD)
    tbl = f"{nmLD}{suf}"
    if nmLD == 'SSDAT':
        return ""
    if nmLD == 'SSDMT':
        grp_TI = ('40','41','42','43', 40, 41, 42, 43)
    if nmLD == 'SSDBT':
        return ""
    return f"""
            WITH base AS (
                            SELECT PN_CON_1 AS PN, CT{xx} AS CT
                            FROM {tbl}
                            WHERE TIP_INST IN ('RD_AER_URB','RD_AER_RUR', 'RD_SUBT_URB', 'RD_SUBT_RUR', 'RD_SUBM')
                            UNION ALL
                            SELECT PN_CON_2 AS PN, CT{xx} AS CT
                            FROM {tbl}
                            WHERE TIP_INST IN ('RD_AER_URB','RD_AER_RUR', 'RD_SUBT_URB', 'RD_SUBT_RUR', 'RD_SUBM')
                        ),
                clean AS (
                            SELECT PN, CT
                            FROM base
                            WHERE PN IS NOT NULL AND PN <> '' AND CT IS NOT NULL AND CT <> ''
                            GROUP BY PN, CT
                        ),
                pn_agg AS (
                            SELECT
                                PN,
                                COUNT(*)                         AS CT_QTDE,
                                GROUP_CONCAT(CT, ',')            AS CT_LIST,
                                json_group_array(CT)             AS CT_JSON   -- requer JSON1 (SQLite)
                            FROM clean
                            GROUP BY PN
                            )
                SELECT
                    t.COD_ID,
                    t.TIP_PN, t.ESTR, t.MAT, t.ESF, t.ALT,
                    t.CONJ, t.MUN, t.ODI, t.TI, t.CM,
                    t.TUC, t.A1, t.A2, t.A3, t.A4, t.A5, t.A6, t.UAR,
                    t.SITCONT, t.DESCR,
                    1 AS Qtd_BDGD,
                    p.CT_QTDE,
                    p.CT_LIST,
                    p.CT_JSON
                FROM PONNOT{suf} t
                LEFT JOIN pn_agg p
                ON p.PN = t.COD_ID
                WHERE t.SITCONT IN ('AT1','SF','RT') AND t.TI IN {grp_TI} AND
                TIP_INST IN ('RD_AER_URB','RD_AER_RUR', 'RD_SUBT_URB', 'RD_SUBT_RUR', 'RD_SUBM');
            """

@monitor_completo(st.session_state.LOGGER)
def _valorar(
                A: pd.DataFrame,                 # itens a valorar (ex.: ODI, TI, TUC, A1..A6)
                B: pd.DataFrame,                 # tabela de preços (CMU) com as mesmas chaves (total ou parcial)
                *,
                preco_col: str = "VL_CMU_VOC",   # nome da coluna do preço unitário em B
                niveis: Optional[List[List[str]]] = None,  # níveis de chaves (em ordem de especificidade)
                fillvalue: float = 0.0,          # valor a usar quando nada casar
                qtd_col: Optional[str] = "QTD",  # se existir, calcula VL_total = QTD * preco_col
                na_symbol: str = "NA",           # padroniza nulos/ausentes nas chaves
                agg: str = "first",              # agregação quando há múltiplos preços por mesma chave: 'first'|'last'|'mean'|'max'|'min'...
                cache: Optional[Dict[str, pd.DataFrame]] = None,  # permite reuso de B agregada por nível entre chamadas
                usar_subpass_media: bool = True,              # ativa o subpasso de média residual
                preco_prev_col: str = "CMU_previsto"          # coluna em A com o CMU previsto (para média residual)
            ) -> pd.DataFrame:
    """
    Retorna A com colunas:
    - CMU_escolhido
    - nivel_escolhido (1 = mais específico)
    - FLG_SEM_PRECO (1 se não encontrou nenhum preço)
    - VL_total (se qtd_col for fornecida)
    """

    # -------- 1) Configura níveis padrão (mais -> menos específico) --------
    if niveis is None:
        niveis = [
                    ["ODI","TI","TUC","A1","A2","A3","A4","A5","A6"],  
                    ["ODI","TI","TUC","A1","A2","A3","A4","A5"],       
                    ["ODI","TI","TUC","A1","A2","A3","A4"],                 
                    ["ODI","TI","TUC","A1","A2","A3"],                           
                    ["ODI","TI","TUC","A1","A2"],                                                        
                    ["ODI","TI","TUC","A1"],
                    ["ODI","TI","TUC"],
                    ["TI","TUC"],
                    ["TUC"],                                                              
                    ]

    # -------- 2) Garantia de chaves --------
    def _garantia_cols(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
        sai = df.copy()
        for c in cols:
            if c not in sai.columns:
                sai[c] = pd.NA
        return sai

    # Todas as colunas que podem ser usadas em algum nível
    todas_cols: List[str] = sorted(set([c for lvl in niveis for c in lvl]))

    A_ = _garantia_cols(A, todas_cols)
    B_ = _garantia_cols(B, todas_cols + [preco_col])

    # Padroniza nulos para na_symbol e tudo como str (consistência de merge)
    def _norm_chv(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
        df = df.copy()
        for c in cols:
            df[c] = df[c].fillna(na_symbol).astype(str).str.strip()
        return df

    A_ = _norm_chv(A_, todas_cols)
    B_ = _norm_chv(B_, todas_cols)

    # -------- 3) Saída base --------
    sai = A_.copy()
    sai["CMU_escolhido"] = pd.NA
    sai["nivel_escolhido"] = pd.NA
    sai["metodo"] = pd.NA

    # -------- 4) Pré-agregação de B por nível (com cache opcional) --------
    cache = {} if cache is None else cache

    def _agg_level(dfB: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
        key = f"lvl::{','.join(cols)}::{preco_col}::{agg}"
        if key in cache:
            return cache[key]
        if agg in {"first", "last"}:
            # mantém uma linha por chave (primeiro/último não-nulo em preco_col)
            if agg == "first":
                df = dfB.sort_index().drop_duplicates(subset=cols, keep="first")
            else:
                df = dfB.sort_index().drop_duplicates(subset=cols, keep="last")
            df = df[cols + [preco_col]]
        else:
            df = dfB.groupby(cols, dropna=False, sort=False, as_index=False)[preco_col].agg(agg)
        cache[key] = df
        return df

    # Mmédia residual no A (CMU_previsto x QTD)
    def _media_residual(df_grp: pd.DataFrame, mask_unmatched_grp: np.ndarray) -> float:
        """
        Recebe o subdataframe do grupo (linhas daquele grupo no 'sai') e a máscara booleana
        indicando quais linhas (dentro do subdataframe) ainda não foram conciliadas.

        Retorna a média residual = (Σ CMU_previsto * QTD dos ainda não conciliados) / (Σ QTD dos ainda não conciliados),
        depois de descontar do total do grupo o que já foi conciliado.
        Nota: Isso equivale diretamente a calcular nos não conciliados, mas escreve-se de forma clara.
        """
        if (qtd_col is None) or (qtd_col not in df_grp.columns) or (preco_prev_col not in df_grp.columns):
            return np.nan

        # Converte numericamente, ignorando nulos
        qtd_tot = pd.to_numeric(df_grp[qtd_col], errors="coerce").fillna(0.0)
        cmu_prev_tot = pd.to_numeric(df_grp[preco_prev_col], errors="coerce")

        # Totais do grupo
        total_valor_prev = (cmu_prev_tot * qtd_tot).sum()
        total_qtd = qtd_tot.sum()

        if total_qtd <= 0:
            return np.nan

        # Já conciliados neste grupo (não na máscara)
        conc_mask = ~mask_unmatched_grp
        valor_conc = (cmu_prev_tot[conc_mask] * qtd_tot[conc_mask]).sum()
        qtd_conc = qtd_tot[conc_mask].sum()

        # Saldos
        valor_residual = total_valor_prev - valor_conc
        qtd_residual = total_qtd - qtd_conc

        if qtd_residual <= 0:
            return np.nan

        return float(valor_residual / qtd_residual)
    
    # -------- 5) Loop de cascateamento --------
    mask_unmatched = sai["CMU_escolhido"].isna()
    for i, cols in enumerate(niveis, start=1):
        if not mask_unmatched.any():
            break 

        subA = sai.loc[mask_unmatched, cols] 
        dfB_lvl = _agg_level(B_, cols)
        merged = subA.merge(dfB_lvl, how="left", on=cols)
        got = merged[preco_col].notna().to_numpy()
        if got.any():
            idx_out = sai.index[mask_unmatched]
            fill_idx = idx_out[got] 
            sai.loc[idx_out[got], "CMU_escolhido"] = merged.loc[got, preco_col].to_numpy()
            chave_str = ",".join(cols)
            sai.loc[idx_out[got], "nivel_escolhido"] = chave_str
            sai.loc[fill_idx, "metodo"] = "B"

        # atualiza máscara de quem ainda não casou
        mask_unmatched = sai["CMU_escolhido"].isna()
        # 5.b) Subpasso: média residual dentro do próprio nível (opcional)
        if usar_subpass_media and (qtd_col in sai.columns) and (preco_prev_col in sai.columns):
            # Considera somente quem ainda não casou neste nível
            pendentes = sai.loc[mask_unmatched, cols + ([qtd_col, preco_prev_col] if qtd_col else [])].copy()
            if not pendentes.empty:
                # Agrupar por chave do nível atual e calcular média residual por grupo
                # Para isso, vamos operar sobre o DF completo do nível (todos do grupo), mas preenchendo só nos pendentes.
                # Criamos chave do grupo
                grp_key = pd.util.hash_pandas_object(sai[cols].astype(str), index=False)
                # dicionário chave -> média residual
                media_residual_por_grp: Dict[int, float] = {}

                # Itera por grupos do nível atual
                for key_val, df_grp in sai.groupby(grp_key, sort=False):
                    # linhas deste grupo no DF total
                    idx_grp = df_grp.index
                    # dentro do grupo, quais estão pendentes
                    mask_grp_unmatched = sai.loc[idx_grp, "CMU_escolhido"].isna().to_numpy()

                    if mask_grp_unmatched.any():
                        mr = _media_residual(df_grp, mask_grp_unmatched)
                        if np.isfinite(mr):
                            media_residual_por_grp[key_val] = mr

                if media_residual_por_grp:
                    # Para cada grupo que tem média residual válida, preenche nos pendentes do grupo
                    grp_key_all = grp_key.loc[mask_unmatched]
                    idx_to_fill = sai.index[mask_unmatched]
                    # mapeia cada linha pendente para o valor do seu grupo (se existir)
                    mr_vals = [media_residual_por_grp.get(k, np.nan) for k in grp_key_all]
                    mr_vals = np.array(mr_vals, dtype=float)
                    ok = np.isfinite(mr_vals)
                    if ok.any():
                        fill_idx2 = idx_to_fill[ok]
                        chave_str = ",".join(cols) + " (MEDIA)"
                        sai.loc[fill_idx2, "CMU_escolhido"] = mr_vals[ok]
                        sai.loc[fill_idx2, "nivel_escolhido"] = chave_str
                        sai.loc[fill_idx2, "metodo"] = "MEDIA_RESIDUAL"

                        # Atualiza máscara
                        mask_unmatched = sai["CMU_escolhido"].isna()

    # -------- 6) Fechamento: preencher faltantes, flags e total --------
    sai["FLG_SEM_PRECO"] = sai["CMU_escolhido"].isna().astype("int8")
    sai["CMU_escolhido"] = pd.to_numeric(sai["CMU_escolhido"], errors="coerce")
    sai["CMU_escolhido"] = sai["CMU_escolhido"].fillna(fillvalue).astype(float)

    if qtd_col and qtd_col in sai.columns:
        sai["VL_total"] = pd.to_numeric(sai[qtd_col], errors="coerce").fillna(0.0) * sai["CMU_escolhido"].astype(float)


    return sai

@monitor_completo(st.session_state.LOGGER)
def _map(df, col, mapa):
    s = df[col].astype(str).fillna('')
    return s.map(lambda x: mapa.get(x, 'Código inválido'))

@monitor_completo(st.session_state.LOGGER)
def _mk_ax(nmLD: str):
    """Campos extras (apenas para SSDMT). Retorna tuple: (select_extra, group_by_extra, label_setor)"""
    if nmLD == "SSDMT":
        select_extra = "T1.BARR, T1.SUB, T1.UNI_TR_AT,"
        group_extra  = "BARR, SUB, UNI_TR_AT,"
        label = "MT"
    else:
        select_extra = ""
        group_extra  = ""
        label = "AT"
    return select_extra, group_extra, label

@monitor_completo(st.session_state.LOGGER)
def _sql_linha(nmLD: str, suf: str) -> str:
    sel_extra, grp_extra, _ = _mk_ax(nmLD)
    return f"""
                WITH base AS (
                SELECT
                    'LD {nmLD[-2:]}' AS TipoEquipamento,
                    L.COD_ID AS CodigoLinha,
                    T1.NOME   AS NomeLinha,
                    T1.TEN_NOM AS TensaoLinha,
                    T1.DESCR  AS DescrLinha, {sel_extra}
                    L.CONJ, L.CT_COD_OP, L.ODI, L.TI, L.CM,
                    COALESCE(COND.TUC_FAS, COND.TUC_NEU) AS TUC,
                    COALESCE(COND.A1_FAS,  COND.A1_NEU)  AS A1,
                    COALESCE(COND.A2_FAS,  COND.A2_NEU)  AS A2,
                    COALESCE(COND.A3_FAS,  COND.A3_NEU)  AS A3,
                    COALESCE(COND.A4_FAS,  COND.A4_NEU)  AS A4,
                    COALESCE(COND.A5_FAS,  COND.A5_NEU)  AS A5,
                    COALESCE(COND.A6_FAS,  COND.A6_NEU)  AS A6,
                    L.FAS_CON, COND.CND_FAS, COND.FTRCNV, COND.UAR,
                    L.SITCONT, L.COMP,
                    CASE
                        WHEN COND.FORM_CAB IN (0,1) THEN 'Singelo'
                        WHEN COND.FORM_CAB = 2     THEN 'Multiplexado Duplex'
                        WHEN COND.FORM_CAB = 3     THEN 'Multiplexado Triplex'
                        WHEN COND.FORM_CAB = 4     THEN 'Multiplexado Quadruplex'
                        WHEN COND.FORM_CAB = 5     THEN 'Interno de subestação'
                        WHEN COND.FORM_CAB = 6     THEN 'Concêntrico Monofásico'
                        WHEN COND.FORM_CAB = 7     THEN 'Concêntrico Bifásico'
                        WHEN COND.FORM_CAB = 8     THEN 'Concêntrico Trifásico'
                        ELSE 'Código inválido'
                    END AS TP_CABO,
                    CASE
                        WHEN COND.FORM_CAB IN (1,6) THEN 1
                        WHEN COND.FORM_CAB IN (2,7) THEN 2
                        WHEN COND.FORM_CAB IN (3,8) THEN 3
                        WHEN COND.FORM_CAB = 4 THEN 4
                        ELSE 1
                    END AS COND_CABO
                FROM {nmLD}{suf} L
                LEFT JOIN  CT{nmLD[-2:]}{suf} T1 ON L.CT{nmLD[-2:]} = T1.COD_ID
                LEFT JOIN SEGCON{suf}    COND ON L.TIP_CND = COND.COD_ID
                WHERE L.TIP_INST IN ('LD_AER_{nmLD[-2:]}','LD_SUB_{nmLD[-2:]}')
                    AND L.SITCONT IN ('AT1','SF','RT')
                ),
                calc AS (
                SELECT
                    *,
                    CAST(((LENGTH(FAS_CON) + COND_CABO - 1) * 1.0 / COND_CABO) AS INTEGER) AS CABOS_FISICOS
                FROM base
                )
                SELECT
                TipoEquipamento, CodigoLinha, NomeLinha, TensaoLinha, {grp_extra}
                DescrLinha, CONJ, CT_COD_OP, ODI, TI, CM,
                TUC, A1, A2, A3, A4, A5, A6,
                FAS_CON, CND_FAS, FTRCNV, TP_CABO, COND_CABO, CABOS_FISICOS,
                UAR, SITCONT,
                COALESCE(SUM(COMP * CABOS_FISICOS * CND_FAS), 0)                 AS Qtd_BDGD_m,
                COALESCE(SUM(COMP * CABOS_FISICOS * CND_FAS * FTRCNV), 0)        AS Qtd_BDGD_kg
                FROM calc
                GROUP BY
                TipoEquipamento, CodigoLinha, NomeLinha, TensaoLinha, {grp_extra}
                DescrLinha, CONJ, CT_COD_OP, ODI, TI, CM,
                TUC, A1, A2, A3, A4, A5, A6,
                FAS_CON, CND_FAS, FTRCNV, TP_CABO, COND_CABO, CABOS_FISICOS, UAR, SITCONT
                ;"""

@monitor_completo(st.session_state.LOGGER)
def texto_explicativo(nmLD: str) -> str:
    _, _, label = _mk_ax(nmLD)
    return f"""
                <p style="text-align: justify; text-indent: 40px">
                Para cada linha (no caso LD {label}), calculamos as quantidades físicas de condutores modeladas na BDGD,
                agrupadas por atributos técnicos (ex.: código da linha, tensão, configuração de fases e tipo de cabo). A consulta integra
                cadastro (CT{nmLD[-2:]}), segmentos ({nmLD}) e características de condutores (SEGCON).
                A coluna <b>CABOS_FISICOS</b> aplica arredondamento para cima conforme a relação entre fases e condutores por cabo, e
                <b>Qtd_BDGD</b> consolida comprimento ponderado por cabos físicos e número de condutores por fase, promovendo uma
                quantificação coerente da materialidade dos circuitos para fiscalização e alocação patrimonial.
                </p>
                <hr/>
                """
@monitor_completo(st.session_state.LOGGER)
def texto_exp_postes(nmLD: str) -> str:
    _, _, label = _mk_ax(nmLD)
    return f"""
                <p style="text-align: justify; text-indent: 40px">
                Também, buscamos as estruturas de suporte associadas às linhas (LD {label}), vinculando cada registro 
                ao circuito (CT{label}) e ao conjunto (CONJ). Os dados são obtidos de LD_ESTR_{label} em junção com 
                o cadastro de linhas (CT{label}) e, obtidas por meio da tabela de pontos notáveis 
                (PN_CON_1/PN_CON_2). Aplica-se filtro por TIP_INST (LD_AER_{label}, LD_SUB_{label}) e SITCONT (AT1, SF, RT) 
                para refletir ativos em operação. Cada estrutura é qualificada por atributos técnicos — TIP_PN 
                (tipo de ponto), ESTR (tipologia da estrutura), MAT (material) e ESF (classe de esforço) — 
                com padronização de ausências como “ND”, garantindo consistência de rótulos. Lembre-se, estruturas podem
                ser compartilhadas por mais de um circuito. Por isso, temos duas colunas para indicar os circuitos que
                usam a estrutura.
                </p>
                <hr/>
                """

@monitor_completo(st.session_state.LOGGER)
def cnt_bloco(nmLD: str, suf: str, bd, tabelas_existentes: set, st = None):
    if f"{nmLD}{suf}" not in tabelas_existentes:
        _, _, label = _mk_ax(nmLD)
        f"<p style='text-align: justify; text-indent: 40px'>Não há linhas para {label} nesta empresa.</p><hr/>"
        return
    if not sql.existe_tabela(f"CT{nmLD[-2:]}_AT", bd):
        f"<p style='text-align: justify; text-indent: 40px'>Não há linhas para CT{nmLD[-2:]}_AT nesta empresa.</p><hr/>",
        return

    sqlq = _sql_linha(nmLD, suf)
    df = pd.read_sql(sqlq, bd)
    if len(df):
        return texto_explicativo(nmLD), df
    else:
        return texto_explicativo(nmLD), pd.DataFrame()

@monitor_completo(st.session_state.LOGGER)
def ponnot_filtrados(nmLD: str, suf: str) -> str:
    xx  = nmLD[-2:] 
    tbl = f"{nmLD}{suf}"
    return f"""
                WITH base AS (
                                SELECT PN_CON_1 AS PN, CT{xx} AS CT
                                FROM {tbl}
                                WHERE TIP_INST IN ('LD_AER_{xx}','LD_SUB_{xx}')
                                UNION ALL
                                SELECT PN_CON_2 AS PN, CT{xx} AS CT
                                FROM {tbl}
                                WHERE TIP_INST IN ('LD_AER_{xx}','LD_SUB_{xx}')
                            ),
                    clean AS (
                                SELECT PN, CT
                                FROM base
                                WHERE PN IS NOT NULL AND PN <> '' AND CT IS NOT NULL AND CT <> ''
                                GROUP BY PN, CT
                            ),
                    pn_agg AS (
                                SELECT
                                    PN,
                                    COUNT(*)                         AS CT_QTDE,
                                    GROUP_CONCAT(CT, ',')            AS CT_LIST,
                                    json_group_array(CT)             AS CT_JSON
                                FROM clean
                                GROUP BY PN
                                )
                    SELECT
                        t.COD_ID,
                        t.TIP_PN, t.ESTR, t.MAT, t.ESF, t.ALT,
                        t.CONJ, t.MUN, t.ODI, t.TI, t.CM,
                        t.TUC, t.A1, t.A2, t.A3, t.A4, t.A5, t.A6, t.UAR,
                        t.SITCONT, t.DESCR,
                        1 AS Qtd_BDGD,
                        p.CT_QTDE,
                        p.CT_LIST,
                        p.CT_JSON
                    FROM PONNOT{suf} t
                    LEFT JOIN pn_agg p
                    ON p.PN = t.COD_ID
                    WHERE t.SITCONT IN ('AT1','SF','RT')
                    AND t.TIP_INST IN ('LD_AER_{xx}','LD_SUB_{xx}');
            """

@monitor_completo(st.session_state.LOGGER)
def _frag_select(src: str, suf: str) -> str:
    t = f"{src}{suf}"
    if src == "UCAT":
        return f"""SELECT 
        t1.COD_ID, t1.PN_CON, NULL AS RAMAL, t1.PAC,
        t1.CTAT, NULL AS CTMT, NULL AS UNI_TR_AT, NULL AS UNI_TR_MT,
        t1.SUB, t1.CONJ, t1.MUN, t1.SIT_ATIV, t1.DAT_CON,
        CAST(t1.CAR_INST AS REAL) AS CAR_INST,
        CAST(t1.DEM_CONT AS REAL) AS DEM_CONT,
        t1.TIP_SIST, NULL AS POT_INST, t1.CNAE, t1.GRU_TEN
        FROM {t} t1"""
    if src == "UCMT":
        return f"""SELECT 
        t1.COD_ID, t1.PN_CON, NULL AS RAMAL, t1.PAC,
        NULL AS CTAT, t1.CTMT, t1.UNI_TR_AT, NULL AS UNI_TR_MT,
        t1.SUB, t1.CONJ, t1.MUN, t1.SIT_ATIV, t1.DAT_CON,
        CAST(t1.CAR_INST AS REAL) AS CAR_INST,
        CAST(t1.DEM_CONT AS REAL) AS DEM_CONT,
        t1.TIP_SIST, NULL AS POT_INST, t1.CNAE, t1.GRU_TEN
        FROM {t} t1"""
    if src == "UCBT":
        return f"""SELECT 
        t1.COD_ID, t1.PN_CON, t1.RAMAL, t1.PAC,
        NULL AS CTAT, t1.CTMT, t1.UNI_TR_AT, t1.UNI_TR_MT,
        t1.SUB, t1.CONJ, t1.MUN, t1.SIT_ATIV, t1.DAT_CON,
        CAST(t1.CAR_INST AS REAL) AS CAR_INST,
        NULL AS DEM_CONT,
        t1.TIP_SIST, NULL AS POT_INST, t1.CNAE, t1.GRU_TEN
        FROM {t} t1"""
    if src == "UGAT":
        return f"""SELECT 
        t1.COD_ID, t1.PN_CON, NULL AS RAMAL, t1.PAC,
        t1.CTAT, NULL AS CTMT, NULL AS UNI_TR_AT, NULL AS UNI_TR_MT,
        t1.SUB, t1.CONJ, t1.MUN, t1.SIT_ATIV, t1.DAT_CON,
        NULL AS CAR_INST,
        CAST(t1.DEM_CONT AS REAL) AS DEM_CONT,
        t1.TIP_SIST, CAST(t1.POT_INST AS REAL) AS POT_INST, t1.CNAE, t1.GRU_TEN
        FROM {t} t1"""
    if src == "UGMT":
        return f"""SELECT 
        t1.COD_ID, t1.PN_CON, NULL AS RAMAL, t1.PAC,
        NULL AS CTAT, t1.CTMT, t1.UNI_TR_AT, NULL AS UNI_TR_MT,
        t1.SUB, t1.CONJ, t1.MUN, t1.SIT_ATIV, t1.DAT_CON,
        NULL AS CAR_INST,
        CAST(t1.DEM_CONT AS REAL) AS DEM_CONT,
        t1.TIP_SIST, CAST(t1.POT_INST AS REAL) AS POT_INST, t1.CNAE, t1.GRU_TEN
        FROM {t} t1"""
    if src == "UGBT":
        return f"""SELECT 
        t1.COD_ID, t1.PN_CON, NULL AS RAMAL, t1.PAC,
        NULL AS CTAT, t1.CTMT, t1.UNI_TR_AT, t1.UNI_TR_MT,
        t1.SUB, t1.CONJ, t1.MUN, t1.SIT_ATIV, t1.DAT_CON,
        NULL AS CAR_INST,
        CAST(t1.DEM_CONT AS REAL) AS DEM_CONT,
        t1.TIP_SIST, CAST(t1.POT_INST AS REAL) AS POT_INST, t1.CNAE, t1.GRU_TEN
        FROM {t} t1"""
    raise ValueError(src)

@monitor_completo(st.session_state.LOGGER)
def carregar_uc_unificada(
                            bd: sl.Connection,
                            suf: str,
                            tabelas_existentes: set[str],
                            dst_table: str = "UC_UNIFIC",
                            criar_indices: bool = True,
                            pragmas_carga: bool = True,
                            COLS = None
                        ) -> dict[str, int]:

        SRC = ["UCAT","UCMT","UCBT","UGAT","UGMT","UGBT"]

        def _get_pragma(name: str):
            return bd.execute(f"PRAGMA {name}").fetchone()[0]

        old = {}
        if pragmas_carga:
            for p in ("journal_mode","synchronous","temp_store","cache_size"):
                try:
                    old[p] = _get_pragma(p)
                except Exception:
                    old[p] = None

            bd.execute("PRAGMA journal_mode=WAL")
            bd.execute("PRAGMA synchronous=OFF")
            bd.execute("PRAGMA temp_store=MEMORY")
            bd.execute("PRAGMA cache_size=-200000")

        bd.execute(f"DROP TABLE IF EXISTS {dst_table}")
        bd.execute(f"CREATE TABLE {dst_table} ({COLS})")
        bd.execute("BEGIN IMMEDIATE")
        counts: dict[str, int] = {}
        try:
            for src in SRC:
                if f"{src}{suf}" in tabelas_existentes:
                    frag = _frag_select(src, suf)
                    n_src = bd.execute(f"SELECT COUNT(*) FROM ({frag})").fetchone()[0]
                    counts[src] = int(n_src)
                    bd.execute(f"INSERT INTO {dst_table} SELECT * FROM ({frag})")
            bd.execute("COMMIT")
        except Exception as e:
            bd.execute("ROLLBACK")
            # Restaura PRAGMAs antes de propagar erro
            if pragmas_carga:
                try:
                    if old.get("journal_mode") is not None:
                        bd.execute(f"PRAGMA journal_mode={old['journal_mode']}")
                    if old.get("synchronous") is not None:
                        bd.execute(f"PRAGMA synchronous={old['synchronous']}")
                    if old.get("temp_store") is not None:
                        bd.execute(f"PRAGMA temp_store={old['temp_store']}")
                    if old.get("cache_size") is not None:
                        bd.execute(f"PRAGMA cache_size={old['cache_size']}")
                except Exception:
                    pass
            raise e

        # Índices após a carga
        if criar_indices:
            bd.execute(f"CREATE INDEX IF NOT EXISTS idx_{dst_table}_pn     ON {dst_table}(PN_CON)")
            bd.execute(f"CREATE INDEX IF NOT EXISTS idx_{dst_table}_ctat   ON {dst_table}(CTAT)")
            bd.execute(f"CREATE INDEX IF NOT EXISTS idx_{dst_table}_ctmt   ON {dst_table}(CTMT)")
            bd.execute(f"CREATE INDEX IF NOT EXISTS idx_{dst_table}_conj   ON {dst_table}(CONJ)")
            bd.execute(f"CREATE INDEX IF NOT EXISTS idx_{dst_table}_sit    ON {dst_table}(SIT_ATIV)")
            bd.execute("PRAGMA analyze")

        # Restaura PRAGMAs
        if pragmas_carga:
            try:
                if old.get("journal_mode") is not None:
                    bd.execute(f"PRAGMA journal_mode={old['journal_mode']}")
                if old.get("synchronous") is not None:
                    bd.execute(f"PRAGMA synchronous={old['synchronous']}")
                if old.get("temp_store") is not None:
                    bd.execute(f"PRAGMA temp_store={old['temp_store']}")
                if old.get("cache_size") is not None:
                    bd.execute(f"PRAGMA cache_size={old['cache_size']}")
            except Exception:
                pass

        # Checagem total
        total = bd.execute(f"SELECT COUNT(*) FROM {dst_table}").fetchone()[0]
        counts["TOTAL"] = int(total)
        return counts

@monitor_completo(st.session_state.LOGGER)
def busca_ENERGIA(bd, tipo="AT"):
    cursor = bd.cursor()
    VL_ENE = 0
    if sql.existe_tabela(f'UCAT_{tipo}', bd):
        sSQL = f"""SELECT 
                    SUM(
                        COALESCE(ENE_P_01, 0) +
                        COALESCE(ENE_P_02, 0) +
                        COALESCE(ENE_P_03, 0) +
                        COALESCE(ENE_P_04, 0) +
                        COALESCE(ENE_P_05, 0) +
                        COALESCE(ENE_P_06, 0) +
                        COALESCE(ENE_P_07, 0) +
                        COALESCE(ENE_P_08, 0) +
                        COALESCE(ENE_P_09, 0) +
                        COALESCE(ENE_P_10, 0) +
                        COALESCE(ENE_P_11, 0) +
                        COALESCE(ENE_P_12, 0) +
                        COALESCE(ENE_F_01, 0) +
                        COALESCE(ENE_F_02, 0) +
                        COALESCE(ENE_F_03, 0) +
                        COALESCE(ENE_F_04, 0) +
                        COALESCE(ENE_F_05, 0) +
                        COALESCE(ENE_F_06, 0) +
                        COALESCE(ENE_F_07, 0) +
                        COALESCE(ENE_F_08, 0) +
                        COALESCE(ENE_F_09, 0) +
                        COALESCE(ENE_F_10, 0) +
                        COALESCE(ENE_F_11, 0) +
                        COALESCE(ENE_F_12, 0)
                    ) AS EN_AT
                FROM UCAT_{tipo};"""
        cursor.execute(sSQL)
        VL_ENE += cursor.fetchone()[0]
    if sql.existe_tabela(f'UCMT_{tipo}', bd):
        sSQL = f"""SELECT 
                    SUM(
                        COALESCE(ENE_01, 0) +
                        COALESCE(ENE_02, 0) +
                        COALESCE(ENE_03, 0) +
                        COALESCE(ENE_04, 0) +
                        COALESCE(ENE_05, 0) +
                        COALESCE(ENE_06, 0) +
                        COALESCE(ENE_07, 0) +
                        COALESCE(ENE_08, 0) +
                        COALESCE(ENE_09, 0) +
                        COALESCE(ENE_10, 0) +
                        COALESCE(ENE_11, 0) +
                        COALESCE(ENE_12, 0)
                    ) AS EN_MT
                FROM UCMT_{tipo};"""
        cursor.execute(sSQL)
        VL_ENE += cursor.fetchone()[0]
    if sql.existe_tabela(f'UCBT_{tipo}', bd):
        sSQL = f"""SELECT 
                    SUM(
                        COALESCE(ENE_01, 0) +
                        COALESCE(ENE_02, 0) +
                        COALESCE(ENE_03, 0) +
                        COALESCE(ENE_04, 0) +
                        COALESCE(ENE_05, 0) +
                        COALESCE(ENE_06, 0) +
                        COALESCE(ENE_07, 0) +
                        COALESCE(ENE_08, 0) +
                        COALESCE(ENE_09, 0) +
                        COALESCE(ENE_10, 0) +
                        COALESCE(ENE_11, 0) +
                        COALESCE(ENE_12, 0)
                    ) AS EN_BT
                FROM UCMT_{tipo};"""
        cursor.execute(sSQL)
        VL_ENE += cursor.fetchone()[0]
    return VL_ENE

@monitor_completo(st.session_state.LOGGER)
def segcon_AT(nm_arq, db, df, var, sufixo):
    sSQL = f"""
        SELECT 
            t1.COD_ID AS TIP_CND,
            'LD_AT' AS TIP_INST,
            (SELECT t2.DESCR FROM TCABOGEOM_{sufixo} t2 WHERE t1.GEOM_CAB=t2.COD_ID) AS GEOM_CAB,
            (SELECT t3.DESCR FROM TCABOFOR_{sufixo} t3 WHERE t1.FORM_CAB=t3.COD_ID) AS FORM_CAB,
            (SELECT t4.DESCR FROM TCABOMAT_{sufixo} t4 WHERE t1.MAT_FAS_1=t4.COD_ID) AS MAT_FAS_1,
            (SELECT t4.DESCR FROM TCABOMAT_{sufixo} t4 WHERE t1.MAT_FAS_2=t4.COD_ID) AS MAT_FAS_2,
            (SELECT t4.DESCR FROM TCABOMAT_{sufixo} t4 WHERE t1.MAT_FAS_3=t4.COD_ID) AS MAT_FAS_3,
            (SELECT t4.DESCR FROM TCABOMAT_{sufixo} t4 WHERE t1.MAT_NEU=t4.COD_ID) AS MAT_NEU,
            (SELECT t6.DESCR FROM TCABOISO_{sufixo} t6 WHERE t1.ISO_FAS_1=t6.COD_ID) AS ISO_FAS_1,
            (SELECT t6.DESCR FROM TCABOISO_{sufixo} t6 WHERE t1.ISO_FAS_2=t6.COD_ID) AS ISO_FAS_2,
            (SELECT t6.DESCR FROM TCABOISO_{sufixo} t6 WHERE t1.ISO_FAS_3=t6.COD_ID) AS ISO_FAS_3,
            (SELECT t6.DESCR FROM TCABOISO_{sufixo} t6 WHERE t1.ISO_NEU=t6.COD_ID) AS ISO_NEU,
            t1.CND_FAS,
            t1.FTRCNV,
            (SELECT t7.DESCR FROM TCABOBIT_{sufixo} t7 WHERE t1.BIT_FAS_1=t7.COD_ID) AS BIT_FAS_1,
            (SELECT t7.DESCR FROM TCABOBIT_{sufixo} t7 WHERE t1.BIT_FAS_2=t7.COD_ID) AS BIT_FAS_2,
            (SELECT t7.DESCR FROM TCABOBIT_{sufixo} t7 WHERE t1.BIT_FAS_3=t7.COD_ID) AS BIT_FAS_3,
            (SELECT t7.DESCR FROM TCABOBIT_{sufixo} t7 WHERE t1.BIT_NEU=t7.COD_ID) AS BIT_NEU
        FROM {nm_arq} t1

        """
    df_LD_AT_AT = pd.read_sql(sSQL, db)
    df = df.merge(df_LD_AT_AT, how='left', on='TIP_CND')

    df.loc[df['FORM_CAB'] =='Singelo', "Qtd_kg"] = (
            df['CND_FAS'] /  df['FTRCNV'] * df[var]
            * (df['BIT_FAS_1'].apply(lambda x: 0 if pd.isna(x) or x == 'Não informado' else 1) +
            df['BIT_FAS_2'].apply(lambda x: 0 if pd.isna(x) or x == 'Não informado' else 1) +
            df['BIT_FAS_3'].apply(lambda x: 0 if pd.isna(x) or x == 'Não informado' else 1) +
            df['BIT_NEU'].apply(lambda x: 0 if pd.isna(x) or x == 'Não informado' else 1))
    )
    return df

@monitor_completo(st.session_state.LOGGER)
def bsc_dd_CR(nm_tbl, bd, pasta, local):
    if nm_tbl[-3:] == 'ANT':
            sufixo = "ANT"
    else:
        sufixo = "M10"
    if sql.existe_tabela('TUNI_M10', bd):
        sSQL = "SELECT * FROM TUNI_M10"
        TUNI_AT = pd.read_sql(sSQL,bd)
        LST_TUNI = f"""{(
                    TUNI_AT.loc[TUNI_AT['Unidade'] == 'Unidade Compensadora de Reativo', 'COD_ID']
                    .drop_duplicates()
                    .astype(str)
                    .tolist()
                    )}"""[1:-1]
    if sql.existe_tabela('TUNI_ANT', bd):
        sSQL = "SELECT * FROM TUNI_ANT"
        TUNI_AT = pd.read_sql(sSQL,bd)
        LST_TUNI = f"""{(
                    TUNI_AT.loc[TUNI_AT['Unidade'] == 'Unidade Compensadora de Reativo', 'COD_ID']
                    .drop_duplicates()
                    .astype(str)
                    .tolist()
                    )}"""[1:-1]

    if sql.existe_tabela(f'{nm_tbl}', bd):
        try:
            sSQL = f"""
                SELECT 
                    t1.COD_ID AS COD_ID_EQRE,
                    TIP_INST, GRU_TEN,
                    UN_CR AS COD_ID_UNCR,
                    t2.DESCR,
                    ODI
                FROM {nm_tbl} t1
                LEFT JOIN TGRUTEN_{sufixo} t2 ON t1.GRU_TEN=t2.COD_ID
                WHERE t1.TIP_INST IN ("SE_AT", "SE_MT") AND
                t1.SITCONT IN ("AT1", "SF")
                """
            df_EQCR_AT = pd.read_sql(sSQL, bd)
        except Exception as e:
            st.warning(f"Problemas, erro: {e}")
            sSQL = f"""
            SELECT 
                t1.COD_ID AS COD_ID_EQRE,
                TIP_INST, GRU_TEN,
                UN_CR AS COD_ID_UNCR,
                t2.DESCR,
                ODI
            FROM {nm_tbl} t1
            LEFT JOIN TGRUTEN_ANT t2 ON t1.GRU_TEN=t2.COD_ID
            WHERE t1.TIP_INST IN ("SE_AT", "SE_MT") AND
            t1.SITCONT IN ("AT1", "SF")
            """
            df_EQCR_AT = pd.read_sql(sSQL, bd)
    df_EQCR_AT = df_EQCR_AT.drop_duplicates()    
    dic_cmp_sql = {
        'UNCRAT' : "COD_ID, SUB,  CONJ,  TIP_UNID, POT_NOM,  BANC",
        'UNCRMT' : "COD_ID, SUB,  CONJ,  TIP_UNID, POT_NOM,  BANC, CTMT, UNI_TR_AT",
        'UNCRBT' : "COD_ID, SUB,  CONJ,  TIP_UNID, POT_NOM,  BANC, CTMT, UNI_TR_AT, UNI_TR_MT",
        }
    df_UNCR = pd.DataFrame()
    for nm_tab in ['UNCRAT','UNCRMT','UNCRBT']:
        if os.path.exists(f"{local}/{pasta}/CONSOL/{nm_tab}.shp"):    
            df_PR = gpd.read_file(f"{local}/{pasta}/CONSOL/{nm_tab}.shp", 
                                    engine='pyogrio', 
                                    use_arrow  =True,
                                    sql=f"""SELECT {dic_cmp_sql[nm_tab]} FROM "{nm_tab}" 
                                        WHERE TIP_UNID IN ({LST_TUNI}) AND  POS = 'PD'
                                        AND  SIT_ATIV = 'AT'""")   
                    
            if not df_PR.crs:
                df_PR = df_PR.set_crs("EPSG:4674")
            df_PR['GRU_TEN'] = nm_tab[-2:]
            if df_UNCR.empty:
                df_UNCR = df_PR.copy()
            else:
                df_UNCR = pd.concat([df_UNCR,df_PR], ignore_index=True)

    try:
        sSQL = "SELECT * FROM TPOTRTV_M10"
        TPOTRTV_AT = pd.read_sql(sSQL, bd)
    except:
        sSQL = "SELECT * FROM TPOTRTV_ANT"
        TPOTRTV_AT = pd.read_sql(sSQL, bd)
        
    mapeamento = TPOTRTV_AT.set_index('COD_ID')['DESCR'].to_dict()
    df_UNCR['POT_NOM'] = df_UNCR['COD_ID'].map(mapeamento)
    df_UNCR = df_UNCR.fillna("ND")
    df_UNCR = df_UNCR.merge(TUNI_AT[['COD_ID','TIPO_UNIDADE']], how='left', 
                                    left_on = 'TIP_UNID', right_on = 'COD_ID',
                                    suffixes = ('_UNCR','_TUNI'))
    df_UNCR = df_UNCR.drop(columns=['COD_ID_TUNI', 'TIP_UNID'])
    df_EQCR_AT = df_EQCR_AT.merge(df_UNCR, how = 'left', on=['COD_ID_UNCR','GRU_TEN'],
                                suffixes=("_EQ","_GEO"))
    return df_EQCR_AT

@monitor_completo(st.session_state.LOGGER)
def bsc_dd_REG(nm_tbl, bd, pasta, local = ""):
    if nm_tbl[-3:] == 'ANT':
        sufixo = "ANT"
    else:
        sufixo = "M10"
    if sql.existe_tabela('TUNI_M10', bd):
        sSQL = "SELECT * FROM TUNI_M10"
        TUNI_AT = pd.read_sql(sSQL,bd)
        LST_TUNI = f"""{(
                    TUNI_AT.loc[TUNI_AT['Unidade'] == 'Unidade Reguladora', 'COD_ID']
                    .drop_duplicates()
                    .astype(str)
                    .tolist()
                    )}"""[1:-1]
    if sql.existe_tabela('TUNI_ANT', bd):
        sSQL = "SELECT * FROM TUNI_ANT"
        TUNI_AT = pd.read_sql(sSQL,bd)
        LST_TUNI = f"""{(
                    TUNI_AT.loc[TUNI_AT['Unidade'] == 'Unidade Reguladora', 'COD_ID']
                    .drop_duplicates()
                    .astype(str)
                    .tolist()
                    )}"""[1:-1]

    if sql.existe_tabela(f'{nm_tbl}', bd):
        try:
            sSQL = f"""
                SELECT 
                    t1.COD_ID AS COD_ID_EQRE,
                    TIP_INST,
                    GRU_TEN,
                    UN_RE AS COD_ID_UNRE,
                    t2.DESCR AS POT_NOM,
                    t3.DESCR AS REL_TP,
                    t4.DESCR AS REL_TC,
                    t5.DESCR AS COR_NOM,
                    ODI
                FROM {nm_tbl} t1 LEFT JOIN TRELTP_{sufixo} t3 ON t1.REL_TP=t3.COD_ID
                LEFT JOIN TPOTAPRT_{sufixo} t2 ON t1.POT_NOM=t2.COD_ID LEFT JOIN TRELTC_{sufixo} t4
                ON t1.REL_TC=t4.COD_ID LEFT JOIN TCOR_{sufixo} t5 ON t5.COD_ID=t1.COR_NOM
                WHERE t1.SITCONT IN ("AT1", "SF")
                """
            df_EQRE_AT = pd.read_sql(sSQL, bd)
        except Exception as e:
            st.warning(f"Problemas, erro: {e}")
            sSQL = f"""
            SELECT 
                t1.COD_ID AS COD_ID_EQRE,
                TIP_INST,
                GRU_TEN,
                UN_RE AS COD_ID_UNRE,
                t2.DESCR AS POT_NOM,
                t3.DESCR AS REL_TP,
                t4.DESCR AS REL_TC,
                t5.DESCR AS COR_NOM,
                ODI
            FROM {nm_tbl} t1 LEFT JOIN TRELTP_ANT t3 ON t1.REL_TP=t3.COD_ID
            LEFT JOIN TPOTAPRT_ANT t2 ON t1.POT_NOM=t2.COD_ID LEFT JOIN TRELTC_ANT t4
            ON t1.REL_TC=t4.COD_ID LEFT JOIN TCOR_ANT t5 ON t5.COD_ID=t1.COR_NOM
            WHERE t1.SITCONT IN ("AT1", "SF")
            """
        df_EQRE_AT = pd.read_sql(sSQL, bd)
        

    dic_cmp_sql = {
        'UNREAT' : "COD_ID, SUB,  CONJ,  TIP_UNID, TIP_REGU,  BANC",
        'UNREMT' : "COD_ID, SUB,  CONJ,  TIP_UNID, TIP_REGU,  BANC, CTMT, UNI_TR_AT",
        }
    df_UNRE = pd.DataFrame()
    for nm_tab in ['UNREAT','UNREMT']:
        if os.path.exists(f"{local}/{pasta}/CONSOL/{nm_tab}.shp"):    
            df_PR = gpd.read_file(f"{local}/{pasta}/CONSOL/{nm_tab}.shp", 
                                    engine='pyogrio', 
                                    use_arrow  =True,
                                    sql=f"""SELECT {dic_cmp_sql[nm_tab]} FROM "{nm_tab}" 
                                        WHERE TIP_UNID IN ({LST_TUNI}) AND  POS = 'PD'
                                        AND  SIT_ATIV = 'AT'""")         
            if not df_PR.crs:
                df_PR = df_PR.set_crs("EPSG:4674")
            df_PR['GRU_TEN'] = nm_tab[-2:]
            if df_UNRE.empty:
                df_UNRE = df_PR.copy()
            else:
                df_UNRE = pd.concat([df_UNRE,df_PR], ignore_index=True)
    df_UNRE = df_UNRE.fillna("ND")
    df_UNRE = df_UNRE.merge(TUNI_AT[['COD_ID','TIPO_UNIDADE']], how='left', 
                                    left_on = 'TIP_UNID', right_on = 'COD_ID',
                                    suffixes = ('_UNRE','_TUNI'))
    df_UNRE.drop(columns=['COD_ID_TUNI', 'TIP_UNID'])

    df_EQRE_AT = df_EQRE_AT.merge(df_UNRE, how = 'left', on=['COD_ID_UNRE','GRU_TEN'],
                                suffixes=("_EQ","_GEO"))
    return df_EQRE_AT

@monitor_completo(st.session_state.LOGGER)
def bsc_dd_SEC(nm_tbl, bd, pasta, local = ""):
    if nm_tbl[-3:] == 'ANT':
        sufixo = "ANT"
    else:
        sufixo = "M10"

    if sql.existe_tabela('TUNI_M10', bd):
        sSQL = "SELECT * FROM TUNI_M10"
        TUNI_AT = pd.read_sql(sSQL,bd)
        LST_TUNI = f"""{(
                    TUNI_AT.loc[TUNI_AT['Unidade'] == 'Unidade Seccionadora', 'COD_ID']
                    .drop_duplicates()
                    .astype(str)
                    .tolist()
                    )}"""[1:-1]
    if sql.existe_tabela('TUNI_ANT', bd):
        sSQL = "SELECT * FROM TUNI_ANT"
        TUNI_AT = pd.read_sql(sSQL,bd)
        LST_TUNI = f"""{(
                    TUNI_AT.loc[TUNI_AT['Unidade'] == 'Unidade Seccionadora', 'COD_ID']
                    .drop_duplicates()
                    .astype(str)
                    .tolist()
                    )}"""[1:-1]
        
    if sql.existe_tabela(f'{nm_tbl}', bd):
        try:
            sSQL = f"""
                SELECT 
                    t1.COD_ID AS COD_ID_EQSE,
                    TIP_INST,
                    GRU_TEN,
                    UN_SE AS COD_ID_UNSE,
                    t2.DESCR AS CLAS_TEN,
                    t3.DESCR AS ELO_FSV,
                    t4.DESCR AS MEI_ISO,
                    t5.DESCR AS COR_NOM,
                    ODI
                FROM {nm_tbl} t1 LEFT JOIN TCAPELFU_{sufixo} t3 ON t1.ELO_FSV=t3.COD_ID
                LEFT JOIN TCLATEN_{sufixo} t2 ON t1.CLAS_TEN=t2.COD_ID LEFT JOIN TMEIISO_{sufixo} t4
                ON t1.MEI_ISO=t4.COD_ID LEFT JOIN TCOR_{sufixo} t5 ON t5.COD_ID=t1.COR_NOM
                WHERE t1.CLAS_TEN IN (SELECT t3.COD_ID FROM TCLATEN_{sufixo} t3) AND
                t1.SITCONT IN ("AT1", "SF")
                """
            df_EQSE_AT = pd.read_sql(sSQL, bd)
        except Exception as e:
            st.warning(f"Falhou! Analise: {e}")
            sSQL = f"""
            SELECT 
                t1.COD_ID AS COD_ID_EQSE,
                '' AS TIP_INST,
                '' AS GRU_TEN,
                '' AS COD_ID_UNSE,
                t2.DESCR AS CLAS_TEN,
                t3.DESCR AS ELO_FSV,
                t4.DESCR AS MEI_ISO,
                t5.DESCR AS COR_NOM,
                ODI
            FROM {nm_tbl} t1 LEFT JOIN TCAPELFU_ANT t3 ON t1.ELO_FSV=t3.COD_ID
            LEFT JOIN TCLATEN_ANT t2 ON t1.CLAS_TEN=t2.COD_ID LEFT JOIN TMEIISO_ANT t4
            ON t1.MEI_ISO=t4.COD_ID LEFT JOIN TCOR_ANT t5 ON t5.COD_ID=t1.COR_NOM
            WHERE t1.CLAS_TEN IN (SELECT t3.COD_ID FROM TCLATEN_ANT t3) AND
            t1.SITCONT IN ("AT1", "SF")
            """
        df_EQSE_AT = pd.read_sql(sSQL, bd)
    dic_cmp_sql = {
                        'UNSEAT' : "COD_ID, SUB,  CONJ,  TIP_UNID, TLCD",
                        'UNSEMT' : "COD_ID, SUB,  CONJ,  TIP_UNID, TLCD, CTMT, UNI_TR_AT, ARE_LOC",
                        'UNSEBT' : "COD_ID, SUB,  CONJ,  TIP_UNID, TLCD, CTMT, UNI_TR_AT, UNI_TR_MT, ARE_LOC",
                    }
    df_UNSE = pd.DataFrame()
    for nm_tab in ['UNSEAT','UNSEMT','UNSEBT']:
        if os.path.exists(f"{local}/{pasta}/CONSOL/{nm_tab}.shp"):    
            try:
                df_PR = gpd.read_file(f"{local}/{pasta}/CONSOL/{nm_tab}.shp", 
                                    engine='pyogrio', 
                                    use_arrow  =True,
                                    sql=f"""SELECT {dic_cmp_sql[nm_tab]} FROM "{nm_tab}" 
                                        WHERE TIP_UNID IN ({LST_TUNI}) AND  POS = 'PD'
                                        AND  SIT_ATIV = 'AT'""")
            except Exception as e:
                st.warning(e)
                if "UNI_TR_AT" in f"{e}":
                    df_PR = pd.DataFrame()
                else:
                    st.text(nm_tab)
                    raise 
            if not df_PR.empty:        
                if not df_PR.crs:
                    df_PR = df_PR.set_crs("EPSG:4674")
                df_PR['GRU_TEN'] = nm_tab[-2:]
            if df_UNSE.empty:
                df_UNSE = df_PR.copy()
            else:
                df_UNSE = pd.concat([df_UNSE,df_PR], ignore_index=True)
    df_UNSE = df_UNSE.fillna("ND")
    if len(df_UNSE)>0:
        df_UNSE = df_UNSE.merge(TUNI_AT[['COD_ID','TIPO_UNIDADE']], how='left', 
                                        left_on = ['TIP_UNID'], right_on = ['COD_ID'],
                                        suffixes = ('_UNSE','_TUNI'))
        df_UNSE.drop(columns=['COD_ID_TUNI', 'TIP_UNID'])

        df_EQSE_AT = df_EQSE_AT.merge(df_UNSE, how = 'left', on=['COD_ID_UNSE','GRU_TEN'],
                                    suffixes=("_EQ","_GEO"))
    return df_EQSE_AT

@monitor_completo(st.session_state.LOGGER)
def combina_arq_shp(dir, nome, nm_dir):

    pasta_saida = os.path.join(dir, nm_dir)

    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    arquivo_saida = os.path.join(pasta_saida, f"{nome}.shp")

    if not os.path.exists(arquivo_saida):

        shapefiles = [
                        os.path.join(dir, f)
                        for f in os.listdir(dir)
                        if f.lower().endswith(".shp")
                        and f[:len(nome)] == nome
                    ]

        if not shapefiles:
            raise FileNotFoundError(
                                        f"Nenhum shapefile encontrado para {nome}"
                                    )

        encodings_tentativas = [
                                    None,
                                    "latin-1",
                                    "cp1252",
                                    "cp850",
                                    "utf-8"
                                ]

        geo_dfs = []

        for shapefile in shapefiles:

            leitura_ok = False
            ultimo_erro = None

            for encoding in encodings_tentativas:

                try:
                    gdf = gpd.read_file(
                                            shapefile,
                                            engine="pyogrio",
                                            use_arrow=True,
                                            encoding=encoding
                                        )

                    geo_dfs.append(gdf)
                    leitura_ok = True
                    break

                except Exception as e:
                    ultimo_erro = e

            if not leitura_ok:
                raise RuntimeError(
                                        f"Erro ao ler o arquivo:\n"
                                        f"{shapefile}\n\n"
                                        f"Último erro:\n{ultimo_erro}"
                                    )

        combined_gdf = gpd.GeoDataFrame(
                                            pd.concat(geo_dfs, ignore_index=True),
                                            crs=geo_dfs[0].crs
                                        )

        combined_gdf.to_file(
                                arquivo_saida,
                                engine="pyogrio"
                            )

    return "OK"

@monitor_completo(st.session_state.LOGGER)
def csv_to_local(dir, db, nome, st=None):
    """
    Lê todos os arquivos CSV de um diretório e salva os dados em um banco SQLite.
    
    Parâmetros:
    - dir (str): Caminho para o diretório contendo os arquivos CSV.
    - db_path (str): Caminho para o arquivo SQLite onde os dados serão salvos.
    
    Retorno:
    - None: Os dados são salvos diretamente no banco SQLite.
    """
    avl = st.success(f"Iniciando...")
    for filename in os.listdir(dir):
        if filename.upper().endswith(".CSV"):  # Filtrar apenas arquivos CSV
            csv_path = os.path.join(dir, filename)
            
            # Ler o arquivo CSV
            try:
                df = pd.read_csv(
                    csv_path, 
                    encoding="ansi",
                    sep=",",
                    lineterminator="\n",
                    dtype=str
                )
                
                # Nome da tabela será o nome do arquivo sem extensão
                table_name = os.path.splitext(filename)[0]
                
                # Salvar no SQLite
                df.to_sql(f'{table_name}_{nome}', db, if_exists="replace", index=False)
                avl.success(f"Tabela '{table_name}' criada com sucesso no SQLite.")
            
            except Exception as e:
                st.error(f"Erro ao processar o arquivo {filename}: {e}")
    
    # Fechar a conexão com o banco
    avl.success("Finalizado!")

@monitor_completo(st.session_state.LOGGER)
def RCP_base_V11(con, dir_arq_base, empresa = 'ND', ano = 0, st = None, sufixo ="AT"): 
    start = time.time()
    if st:
        avl = st.progress(0, text= "Lendo os dados dos conjuntos...")

    def validar_chave(conn, tabela, colunas, where="1=1"):
        chave = ", ".join(colunas)
        sql = f"""
                    SELECT {chave}, COUNT(*) AS qtd
                    FROM {tabela}
                    WHERE {where}
                    GROUP BY {chave}
                    HAVING COUNT(*) > 1
                    LIMIT 1
                """
        duplicado = conn.execute(sql).fetchone()
        if duplicado:
            st.html(f"""
                        <p style="text-align: justify;">
                            <strong>Validação da Integridade dos Relacionamentos:</strong>
                            Antes da execução das consultas SQL, é verificada a unicidade das chaves
                            de relacionamento entre as tabelas, por meio da análise de sua multiplicidade.
                            Esse procedimento assegura a cardinalidade esperada de até um registro por
                            chave em cada tabela (1:1), prevenindo duplicações decorrentes das operações
                            de junção (<em>JOIN</em>) e possíveis distorções nas contagens e nos resultados
                            consolidados. Eventuais inconsistências são identificadas previamente,
                            proporcionando maior confiabilidade, rastreabilidade e integridade
                            ao processamento dos dados. No caso, falhou: chave não única na tabela <strong>{tabela}</strong>,
                            chave <strong>{colunas}</strong>, com filtro <strong>{where}</strong>, gerando a tupla com a 
                            chave e quantidade de ocorrências: <strong>{duplicado}</strong>.
                        </p>
                        """)

    if sufixo=="AT":
        data_hoje = date.today().strftime("%Y%m%d")
        semente = int(data_hoje)
        arquivo_saida = rf"BDGD_ANLS\amostra_bdgd_{data_hoje}.csv"
        sortear_amostra_bdgd(rf'{dir_arq_base}', quantidade=5, semente=semente, arquivo_saida=arquivo_saida)

    df_CONJ = pd.DataFrame()
    if existe_tabela(f"CONJ_{sufixo}", con):
        SQLq = f"""
            SELECT *
            FROM CONJ_{sufixo} t1
            """
        df_CONJ = pd.read_sql(SQLq, con)

    df_CONJ.to_feather(f'{dir_arq_base}//df_CONJ_{sufixo}.feather')

    if st:
        avl.progress(10, text= "Lendo os dados dos transformadores de medida...")
        registrar_artefato(st.session_state.database_MAN, 
                                    st.session_state.execucao_id, 
                                    file_path = rf'{dir_arq_base}//df_CONJ_{sufixo}.feather',
                                    tipo_artefato = "SAIDA", 
                                    calcular_hash = True)
    
    validar_chave(con, f"EQTRM_{sufixo}", ['COD_ID'])
    df_TRME = pd.DataFrame()
    if existe_tabela(f"EQTRM_{sufixo}", con):
        SQLq = f"""
            SELECT DISTINCT t1.COD_ID, t1.SUB, t1.PAC, t1.TIP_UNID, t1.TIP_INST, t1.UC_UG, t1.GRU_TEN, t1.ODI, 
                            t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC, 
                            t1.DAT_IMO, COUNT(t1.SITCONT) AS Qtd
            FROM EQTRM_{sufixo} t1 
            WHERE t1.SITCONT in ('AT1','RT','SF')
            GROUP BY t1.COD_ID, t1.SUB, t1.PAC, t1.TIP_UNID, t1.TIP_INST, t1.UC_UG, t1.GRU_TEN, t1.ODI, 
                     t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC, 
                     t1.DAT_IMO
            """
        df_TRME = pd.read_sql(SQLq, con)
    df_TRME.to_feather(f'{dir_arq_base}//df_TRM_{sufixo}.feather')
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//df_TRM_{sufixo}.feather',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        avl.progress(20, text= "Lendo os dados dos transformadores de distribuição...")

    validar_chave(con, f"EQTRMT_{sufixo}", ['UNI_TR_MT'], 
                        "SITCONT IN ('AT1','RT','SF') "
                        "AND TIP_INST NOT IN ('SE_MT', 'SE_AT')")
    validar_chave(con, f"UNTRMT_{sufixo}", ['COD_ID'], "POS = 'PD' ")

    df_TRD = pd.DataFrame()
    if existe_tabela(f"EQTRMT_{sufixo}", con):
        SQLq = f"""
            SELECT DISTINCT t1.COD_ID, t1.UNI_TR_MT, t1.CLAS_TEN, t1.POT_NOM, t1.LIG, t1.FAS_CON, t1.TEN_PRI, t1.TEN_SEC,
                            t1.TEN_TER,t1.LIG_FAS_P,t1.LIG_FAS_S,t1.LIG_FAS_T, t1.ODI, 
                            t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC, 
                            t1.DAT_IMO, t2.DAT_CON, t2.CONJ, t2.BANC, t2.TIP_TRAFO, COUNT(t1.SITCONT) AS Qtd
            FROM EQTRMT_{sufixo} t1 LEFT JOIN UNTRMT_{sufixo} t2 ON t1.UNI_TR_MT = t2.COD_ID
            WHERE t1.SITCONT in ('AT1','RT','SF') AND t2.POS = 'PD' AND t1.TIP_INST NOT IN ('SE_MT', 'SE_AT')
            GROUP BY t1.COD_ID, t1.UNI_TR_MT, t1.CLAS_TEN, t1.POT_NOM, t1.LIG, t1.FAS_CON, t1.TEN_PRI, t1.TEN_SEC,
                     t1.TEN_TER,t1.LIG_FAS_P,t1.LIG_FAS_S,t1.LIG_FAS_T, t1.ODI, 
                     t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC, 
                     t1.DAT_IMO, t2. DAT_CON, t2.CONJ, t2.BANC, t2.TIP_TRAFO
            """
        df_TRD = pd.read_sql(SQLq, con)
    df_TRD.to_feather(f'{dir_arq_base}//df_TRD_{sufixo}.feather')
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//df_TRD_{sufixo}.feather',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)

        avl.progress(30, text= "Lendo os dados dos transformadores de força...")
    
    df_TRSE = pd.DataFrame()
    validar_chave(con, f"EQTRAT_{sufixo}", ['UNI_TR_AT'], 
                            "SITCONT IN ('AT1','RT','SF') ")
    validar_chave(con, f"UNTRAT_{sufixo}", ['COD_ID'], "POS = 'PD'")
    validar_chave(con, f"EQTRMT_{sufixo}", ['UNI_TR_MT'], 
                            "SITCONT IN ('AT1','RT','SF') "
                            "AND TIP_INST IN ('SE_MT', 'SE_AT')")
    validar_chave(con, f"UNTRMT_{sufixo}", ['COD_ID'], "POS = 'PD' ")
    SQLq = ""
    if existe_tabela(f"EQTRAT_{sufixo}", con):

        SQLq = f"""
            SELECT DISTINCT t1.COD_ID, t1.UNI_TR_AT, t1.CLAS_TEN, t1.POT_NOM, t1.LIG, t1.FAS_CON, t1.TEN_PRI, t1.TEN_SEC, t1.TEN_TER, 
                            t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC, 
                            t1.DAT_IMO, t2.DAT_CON, t2.CONJ, t2.BANC, t2.TIP_TRAFO, t2.ARE_LOC, COUNT(t1.SITCONT) AS Qtd
            FROM EQTRAT_{sufixo} t1 LEFT JOIN UNTRAT_{sufixo} t2 ON t1.UNI_TR_AT = t2.COD_ID
            WHERE t1.SITCONT in ('AT1','RT','SF') AND t2.POS = 'PD'
            GROUP BY t1.COD_ID, t1.UNI_TR_AT, t1.CLAS_TEN, t1.POT_NOM, t1.LIG, t1.FAS_CON, t1.TEN_PRI, t1.TEN_SEC, t1.TEN_TER,
                     t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC, 
                     t1.DAT_IMO, t2.DAT_CON, t2.CONJ, t2.BANC, t2.TIP_TRAFO, t2.ARE_LOC
            """
    
    if existe_tabela(f"EQTRMT_{sufixo}", con):
        texto = ""
        if SQLq != "":
            texto = " UNION ALL "
        SQLq += f""" {texto} 
        SELECT DISTINCT t1.COD_ID, t1.UNI_TR_MT AS UNI_TR_AT, t1.CLAS_TEN, t1.POT_NOM, t1.LIG, t1.FAS_CON, t1.TEN_PRI, t1.TEN_SEC, t1.TEN_TER, 
                        t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC, 
                        t1.DAT_IMO, t2.DAT_CON, t2.CONJ, t2.BANC, t2.TIP_TRAFO, t2.ARE_LOC, COUNT(t1.SITCONT) AS Qtd
        FROM EQTRMT_{sufixo} t1 LEFT JOIN UNTRMT_{sufixo} t2 ON t1.UNI_TR_MT = t2.COD_ID
        WHERE t1.SITCONT in ('AT1','RT','SF') AND t2.POS = 'PD' AND t1.TIP_INST IN ('SE_MT', 'SE_AT')
        GROUP BY t1.COD_ID, t1.UNI_TR_MT, t1.CLAS_TEN, t1.POT_NOM, t1.LIG, t1.FAS_CON, t1.TEN_PRI, t1.TEN_SEC, t1.TEN_TER,
                    t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC, 
                    t1.DAT_IMO, t2.DAT_CON, t2.CONJ, t2.BANC, t2.TIP_TRAFO, t2.ARE_LOC
        """

    if SQLq != "":
        df_TRSE = pd.read_sql(SQLq, con)
        df_TRSE.to_feather(f'{dir_arq_base}//df_TRSE_{sufixo}.feather')
        if st:
            registrar_artefato(st.session_state.database_MAN, 
                                st.session_state.execucao_id, 
                                file_path = rf'{dir_arq_base}//df_TRSE_{sufixo}.feather',
                                tipo_artefato = "SAIDA", 
                                calcular_hash = True)

    if st: avl.progress(35, text= "Criando a tabela unificada de UC e UG...")
    df_MED = pd.DataFrame()
    if not existe_tabela(f"UC_UG_{sufixo}", con):
        SQLq = ""
        LST_TBL = [f'UCAT_{sufixo}', f'UCMT_{sufixo}', f'UCBT_{sufixo}', f'UGAT_{sufixo}', f'UGMT_{sufixo}', f'UGBT_{sufixo}']
        for nm in LST_TBL:
            if existe_tabela(nm, con):
                SQLq = "SELECT t1.COD_ID, t1.SUB, t1.CONJ, t1.MUN, t1.DAT_CON, t1.GRU_TEN FROM " + nm + " t1" if SQLq == "" else SQLq + " UNION SELECT t1.COD_ID, t1.SUB, t1.CONJ, t1.MUN, t1.DAT_CON, t1.GRU_TEN FROM " + nm + " t1"
        
                df_MED = pd.read_sql(SQLq, con)
                df_MED.to_sql(f"UC_UG_{sufixo}", con, if_exists = 'replace')
    if st: avl.progress(40, text= "Lendo os dados de medidores...")
    df_MED = pd.DataFrame()
    
    validar_chave(
                    con,
                    f"EQME_{sufixo}",
                    ["UC_UG", "GRU_TEN"],
                    "SITCONT IN ('AT1','RT','SF') "
                    "AND A1 IN ('01','1','11','13',1,11,13)"
                )

    validar_chave(
                        con,
                        f"UC_UG_{sufixo}",
                        ["COD_ID", "GRU_TEN"]
                    )
      
    if existe_tabela(f"EQME_{sufixo}", con):
        SQLq = f"""
            SELECT DISTINCT t1.COD_ID, t1.UC_UG, t1.TIP_INST, t1.TIP_UNID, t1.FAS_CON, t1.TIPMED, t1.GRU_TEN,
                            t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, 
                            t1.DAT_IMO, t2.DAT_CON, t2.CONJ, t2.SUB, t2.MUN, COUNT(t1.SITCONT) AS Qtd
            FROM EQME_{sufixo} t1 LEFT JOIN UC_UG_{sufixo} t2 ON (t1.UC_UG = t2.COD_ID) and (t1.GRU_TEN = t2.GRU_TEN)
            WHERE t1.SITCONT in ('AT1','RT','SF') AND t1.A1 in ('01','1', '11', '13', 1, 11, 13)
            GROUP BY t1.COD_ID, t1.UC_UG, t1.TIP_INST, t1.TIP_UNID, t1.FAS_CON, t1.TIPMED, t1.GRU_TEN,
                     t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, 
                     t1.DAT_IMO, t2.DAT_CON, t2.CONJ, t2.SUB, t2.MUN
            """
        df_MED = pd.read_sql(SQLq, con)

    df_MED.to_feather(f'{dir_arq_base}//df_MED_{sufixo}.feather')
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//df_MED_{sufixo}.feather',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        avl.progress(50, text= "Lendo os dados de capacitores...")

    df_EQCR = pd.DataFrame()
    if not existe_tabela("UNCR_AT", con):
        SQLq = ""
        LST_TBL = [f'UNCRAT_{sufixo}', f'UNCRMT_{sufixo}',f'UNCRBT_{sufixo}']
        for nm in LST_TBL:
            if existe_tabela(nm, con):
                SQLq = "SELECT t1.COD_ID, t1.POT_NOM, t1.SUB, t1.CONJ, t1.MUN, t1.DAT_CON, t1.POS, t1.BANC, t1.TIP_UNID, t1.FAS_CON, t1.GRU_TEN FROM " + nm + " t1" if SQLq == "" else SQLq + " UNION SELECT t1.COD_ID, t1.POT_NOM, t1.SUB, t1.CONJ, t1.MUN, t1.DAT_CON, t1.POS, t1.BANC, t1.TIP_UNID, t1.FAS_CON, t1.GRU_TEN FROM " + nm + " t1"
                df_EQCR = pd.read_sql(SQLq, con)
                df_EQCR.to_sql(f"UNCR_{sufixo}", con, if_exists = 'replace')
    df_EQCR = pd.DataFrame()
    validar_chave(
                    con,
                    f"EQCR_{sufixo}",
                    ["UN_CR", "GRU_TEN"],
                    "SITCONT IN ('AT1','RT','SF') "
                )
    validar_chave(con, f"UNCR_{sufixo}", ["COD_ID", "GRU_TEN"], "POS = 'PD'")

    if existe_tabela(f"EQCR_{sufixo}", con):
        SQLq = f"""
            SELECT DISTINCT t1.COD_ID, t1.UN_CR, t1.TIP_INST, t1.GRU_TEN, t2.FAS_CON, t2.POT_NOM,
                            t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC,
                            t1.DAT_IMO, t2.DAT_CON, t2.CONJ, t2.SUB, t2.MUN, t2.BANC, t2.TIP_UNID, COUNT(t1.SITCONT) AS Qtd
            FROM EQCR_{sufixo} t1 LEFT JOIN UNCR_{sufixo} t2 ON (t1.UN_CR = t2.COD_ID) and (t1.GRU_TEN = t2.GRU_TEN)
            WHERE t1.SITCONT in ('AT1','RT','SF') AND t2.POS = 'PD'
            GROUP BY t1.COD_ID, t1.UN_CR, t1.TIP_INST, t1.GRU_TEN, t2.FAS_CON, t2.POT_NOM,
                     t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC,
                     t1.DAT_IMO, t2.DAT_CON, t2.CONJ, t2.SUB, t2.MUN, t2.BANC, t2.TIP_UNID
            """
        df_EQCR = pd.read_sql(SQLq, con)
    df_EQCR.to_feather(f'{dir_arq_base}//df_EQCR_{sufixo}.feather')
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//df_EQCR_{sufixo}.feather',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        avl.progress(60, text= "Lendo os dados de reguladores...")
    df_EQRE = pd.DataFrame()
    if not existe_tabela(f"UNRE_{sufixo}", con):
        SQLq = ""
        LST_TBL = [f'UNREMT_{sufixo}', f'UNREBT_{sufixo}']
        for nm in LST_TBL:
            if existe_tabela(nm, con):
                SQLq = "SELECT t1.COD_ID, t1.SUB, t1.CONJ, t1.MUN, t1.DAT_CON, t1.POS, t1.BANC, t1.TIP_UNID, t1.FAS_CON, t1.GRU_TEN FROM " + nm + " t1" if SQLq == "" else SQLq + " UNION SELECT t1.COD_ID, t1.SUB, t1.CONJ, t1.MUN, t1.DAT_CON, t1.POS, t1.BANC, t1.TIP_UNID, t1.FAS_CON, t1.GRU_TEN FROM " + nm + " t1"
                df_EQRE = pd.read_sql(SQLq, con)
                df_EQRE.to_sql(f"UNRE_{sufixo}", con, if_exists = 'replace')
    df_EQRE = pd.DataFrame()
    validar_chave(
                    con,
                    f"EQRE_{sufixo}",
                    ["UN_RE", "GRU_TEN"],
                    "SITCONT IN ('AT1','RT','SF') "
                )
    validar_chave(con, f"UNRE_{sufixo}", ["COD_ID", "GRU_TEN"], "POS = 'PD'")
    if existe_tabela(f"EQRE_{sufixo}", con):
        SQLq = f"""
            SELECT DISTINCT t1.COD_ID, t1.UN_RE, t1.TIP_INST, t1.POT_NOM, t1.TEN_REG, t1.COR_NOM, t1.REL_TP, t1.REL_TC,
                            t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC,
                            t1.DAT_IMO, t2.DAT_CON, t2.CONJ, t2.SUB, t2.MUN, t2.BANC, t2.TIP_UNID, COUNT(t1.SITCONT) AS Qtd
            FROM EQRE_{sufixo} t1 LEFT JOIN UNRE_{sufixo} t2 ON (t1.UN_RE = t2.COD_ID) and (t1.GRU_TEN = t2.GRU_TEN)
            WHERE t1.SITCONT in ('AT1','RT','SF') AND t2.POS = 'PD'
            GROUP BY t1.COD_ID, t1.UN_RE, t1.TIP_INST, t1.POT_NOM, t1.TEN_REG, t1.COR_NOM, t1. REL_TP, t1. REL_TC,
                     t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC,
                     t1.DAT_IMO, t2.DAT_CON, t2.CONJ, t2.SUB, t2.MUN, t2.BANC, t2.TIP_UNID
            """
        df_EQRE = pd.read_sql(SQLq, con)
    df_EQRE.to_feather(f'{dir_arq_base}//df_EQRE_{sufixo}.feather')

    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//df_EQRE_{sufixo}.feather',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        avl.progress(70, text= "Lendo os dados de seccionadores...")
    df_EQSE = pd.DataFrame()
    if not existe_tabela(f"UNSE_{sufixo}", con):
        SQLq = ""
        LST_TBL = [f'UNSEAT_{sufixo}', f'UNSEMT_{sufixo}', f'UNSEBT_{sufixo}']
        for nm in LST_TBL:
            if existe_tabela(nm, con):
                SQLa = "SELECT * FROM " + nm + " t1"
                df_EQSE = pd.read_sql(SQLa, con)
                if len(df_EQSE) > 0:
                    SQLq = "SELECT t1.COD_ID, t1.SUB, t1.CONJ, t1.MUN, t1.DAT_CON, t1.POS, t1.TLCD, t1.TIP_UNID, t1.GRU_TEN FROM " + nm + " t1" if SQLq == "" else SQLq + " UNION SELECT t1.COD_ID, t1.SUB, t1.CONJ, t1.MUN, t1.DAT_CON, t1.POS, t1.TLCD, t1.TIP_UNID, t1.GRU_TEN FROM " + nm + " t1"
                    df_EQSE = pd.read_sql(SQLq, con)
                    df_EQSE.to_sql(f"UNSE_{sufixo}", con, if_exists = 'replace')

    validar_chave(
                    con,
                    f"EQSE_{sufixo}",
                    ["UN_SE", "GRU_TEN"],
                    "SITCONT IN ('AT1','RT','SF') "
                )
    validar_chave(con, f"UNSE_{sufixo}", ["COD_ID", "GRU_TEN"], "POS = 'PD'")
    if existe_tabela(f"EQSE_{sufixo}", con):
        SQLq = f"""
            SELECT DISTINCT t1.COD_ID, t1.UN_SE, t1.TIP_INST, t1.CLAS_TEN, t1.MEI_ISO, t1.COR_NOM, t1.FAS_CON, t1.ABER_CRG,
                            t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC,
                            t1.DAT_IMO, t2.DAT_CON, t2.CONJ, t2.SUB, t2.MUN, t2.TLCD, t2.TIP_UNID, COUNT(t1.SITCONT) AS Qtd
            FROM EQSE_{sufixo} t1 LEFT JOIN UNSE_{sufixo} t2 ON (t1.UN_SE = t2.COD_ID) and (t1.GRU_TEN = t2.GRU_TEN)
            WHERE t1.SITCONT in ('AT1','RT','SF') AND t2.POS = 'PD'
            GROUP BY t1.COD_ID, t1.UN_SE, t1.TIP_INST, t1.CLAS_TEN, t1.MEI_ISO, t1.COR_NOM, t1.FAS_CON, t1.ABER_CRG,
                     t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.IDUC,
                     t1.DAT_IMO
            """
        df_EQSE = pd.read_sql(SQLq, con)

    df_EQSE.to_feather(f'{dir_arq_base}//df_EQSE_{sufixo}.feather')
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                                    st.session_state.execucao_id, 
                                    file_path = rf'{dir_arq_base}//df_EQSE_{sufixo}.feather',
                                    tipo_artefato = "SAIDA", 
                                    calcular_hash = True)
        avl.progress(80, text= "Lendo os dados de estruturas...")
    df_ESTR = pd.DataFrame()
    validar_chave(
                        con,
                        f"PONNOT_{sufixo}",
                        ["COD_ID"],
                        "SITCONT IN ('AT1','RT','SF') "
                        "AND POS = 'PD' AND (TIP_PN = 'POS' or TIP_PN = 'TOR' or TIP_PN = 'PSE')"
                    )
    if existe_tabela(f"PONNOT_{sufixo}", con):
        SQLq = f"""
            SELECT DISTINCT t1.COD_ID, t1.TIP_INST, t1.TIP_PN, t1.ESTR, t1.MAT, t1.ESF, t1.ALT,
                            t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.ARE_LOC,
                            t1.CONJ, t1.MUN, COUNT(t1.SITCONT) AS Qtd
            FROM PONNOT_{sufixo} t1
            WHERE t1.SITCONT in ('AT1','RT','SF') AND t1.POS = 'PD' AND (TIP_PN = 'POS' or TIP_PN = 'TOR' or TIP_PN = 'PSE')
            GROUP BY t1.COD_ID, t1.TIP_INST, t1.TIP_PN, t1.ESTR, t1.MAT, t1.ESF, t1.ALT,
                     t1.ODI, t1.TI, t1.CM, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.UAR, t1.ARE_LOC,
                     t1.CONJ, t1.MUN
            """
        df_ESTR = pd.read_sql(SQLq, con)
    df_ESTR.to_feather(f'{dir_arq_base}//df_ESTR_{sufixo}.feather')

    if st:
        registrar_artefato(st.session_state.database_MAN, 
                                            st.session_state.execucao_id, 
                                            file_path = rf'{dir_arq_base}//df_ESTR_{sufixo}.feather',
                                            tipo_artefato = "SAIDA", 
                                            calcular_hash = True)
        avl.progress(90, text= "Lendo os dados de condutores...")
    LST_TBL = [f'SSDAT_{sufixo}', f'SSDMT_{sufixo}', f'SSDBT_{sufixo}', f'RAMLIG_{sufixo}']
    df_COND = pd.DataFrame()
    for nm in LST_TBL:
        if existe_tabela(nm, con):
            SQLq = """
                    SELECT DISTINCT t1.FAS_CON, t1.TIP_CND, t1.ODI, t1.TI, t1.SITCONT, t1.POS, t1.DESCR, t1.ARE_LOC,
                           t1.CONJ, t2.BIT_FAS_1, t2.BIT_FAS_2, t2.BIT_FAS_3, t2.BIT_NEU, t2.MAT_FAS_1, t2.MAT_FAS_2,
                           t2.MAT_FAS_3, t2.MAT_NEU, t2.ISO_FAS_1, t2.ISO_FAS_2, t2.ISO_FAS_3, t2.ISO_NEU, 
                           t2.CND_FAS, t2.TUC_FAS, t2.TUC_NEU, t2.FORM_CAB, t2.GEOM_CAB, t2.UAR,
                           t2.A1_FAS, t2.A2_FAS, t2.A3_FAS, t2.A4_FAS, t2.A5_FAS, t2.A6_FAS,
                           t2.A1_NEU, t2.A2_NEU, t2.A3_NEU, t2.A4_NEU, t2.A5_NEU, t2.A6_NEU, t2.FTRCNV, SUM(t1.COMP) AS COMP
                    FROM """ + nm + f""" t1 LEFT JOIN SEGCON_{sufixo} t2
                    ON t1.TIP_CND = t2.cod_id WHERE t1.POS = 'PD'
                    GROUP BY t1.FAS_CON, t1.TIP_CND, t1.ODI, t1.TI, t1.SITCONT,t1.POS, t1.DESCR, t1.ARE_LOC,
                             t1.CONJ, t2.BIT_FAS_1, t2.BIT_FAS_2, t2.BIT_FAS_3, t2.BIT_NEU, t2.MAT_FAS_1, t2.MAT_FAS_2,
                             t2.MAT_FAS_3, t2.MAT_NEU, t2.ISO_FAS_1, t2.ISO_FAS_2, t2.ISO_FAS_3, t2.ISO_NEU, 
                             t2.CND_FAS, t2.TUC_FAS, t2.TUC_NEU, t2.FORM_CAB, t2.GEOM_CAB, t2.UAR,
                             t2.A1_FAS, t2.A2_FAS, t2.A3_FAS, t2.A4_FAS, t2.A5_FAS, t2.A6_FAS,
                             t2.A1_NEU, t2.A2_NEU, t2.A3_NEU, t2.A4_NEU, t2.A5_NEU, t2.A6_NEU, t2.FTRCNV
                   """
            df = pd.read_sql(SQLq, con)
            df_COND = pd.concat([df_COND, df])
    
    df_COND['FTRCNV'] = df_COND['FTRCNV'].fillna('1')
    df_COND['CND_FAS'] = df_COND['CND_FAS'].fillna('1')
    df_COND['FTRCNV'] = df_COND['FTRCNV'].astype(float)
    df_COND['CND_FAS'] = df_COND['CND_FAS'].astype(float)

    df_COND = df_COND.fillna('0',)
    lst_TUCagem = ['TUC_FAS', 'TUC_NEU', 'A1_FAS', 'A2_FAS', 'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU']
    for n in lst_TUCagem:
        df_COND[n] = pd.to_numeric(df_COND[n], errors = 'coerce') if len(df_COND[n]) > 0 else None

    tbl_FC = pd.read_csv("tabelas//tbl_FC_cabos.csv", sep="|", decimal=',', on_bad_lines='skip', encoding="Latin-1");

    df_COND = df_COND.merge(tbl_FC, how = 'left', left_on = ['TUC_FAS', 'A1_FAS', 'A2_FAS', 'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS'], right_on = ['Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6'])
    df_COND = df_COND[['CONJ', 'FAS_CON', 'TIP_CND', 'ODI', 'TI', 'SITCONT', 'POS', 'DESCR',
     'BIT_FAS_1', 'BIT_FAS_2', 'BIT_FAS_3', 'BIT_NEU', 'MAT_FAS_1', 'MAT_FAS_2', 'MAT_FAS_3', 'MAT_NEU', 'ISO_FAS_1',
     'ISO_FAS_2', 'ISO_FAS_3', 'ISO_NEU', 'CND_FAS', 'TUC_FAS', 'TUC_NEU', 'FORM_CAB', 'A1_FAS', 'A2_FAS',
     'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU', 'FTRCNV', 
     'COMP', 'VL_FC']]
    df_COND.columns = ['CONJ', 'FAS_CON', 'TIP_CND', 'ODI', 'TI', 'SITCONT', 'POS', 'DESCR',
     'BIT_FAS_1', 'BIT_FAS_2', 'BIT_FAS_3', 'BIT_NEU', 'MAT_FAS_1', 'MAT_FAS_2', 'MAT_FAS_3', 'MAT_NEU', 'ISO_FAS_1',
     'ISO_FAS_2', 'ISO_FAS_3', 'ISO_NEU', 'CND_FAS', 'TUC_FAS', 'TUC_NEU', 'FORM_CAB', 'A1_FAS', 'A2_FAS',
     'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU', 'FTRCNV', 
     'COMP', 'VL_FC_FAS']
    df_COND['VL_FC_FAS'].fillna(1, inplace = True)
    df_COND = df_COND.merge(tbl_FC, how = 'left', left_on = ['TUC_NEU', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU'], right_on = ['Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6'])
    df_COND = df_COND[['CONJ', 'FAS_CON', 'TIP_CND', 'ODI', 'TI', 'SITCONT', 'POS', 'DESCR',
     'BIT_FAS_1', 'BIT_FAS_2', 'BIT_FAS_3', 'BIT_NEU', 'MAT_FAS_1', 'MAT_FAS_2', 'MAT_FAS_3', 'MAT_NEU', 'ISO_FAS_1',
     'ISO_FAS_2', 'ISO_FAS_3', 'ISO_NEU', 'CND_FAS', 'TUC_FAS', 'TUC_NEU', 'FORM_CAB', 'A1_FAS', 'A2_FAS',
     'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU', 'FTRCNV', 
     'COMP', 'VL_FC_FAS', 'VL_FC']]
    df_COND.columns = ['CONJ', 'FAS_CON', 'TIP_CND', 'ODI', 'TI', 'SITCONT', 'POS', 'DESCR',
     'BIT_FAS_1', 'BIT_FAS_2', 'BIT_FAS_3', 'BIT_NEU', 'MAT_FAS_1', 'MAT_FAS_2', 'MAT_FAS_3', 'MAT_NEU', 'ISO_FAS_1',
     'ISO_FAS_2', 'ISO_FAS_3', 'ISO_NEU', 'CND_FAS', 'TUC_FAS', 'TUC_NEU', 'FORM_CAB', 'A1_FAS', 'A2_FAS',
     'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU', 'FTRCNV', 
     'COMP', 'VL_FC_FAS', 'VL_FC_NEU']
    df_COND['VL_FC_NEU'].fillna(1, inplace = True)

    df_COND['FT_MUL_FAS'] = 1
    df_COND['FT_MUL_NEU'] = 0

    df_COND.loc[(df_COND['FAS_CON'].isin(['AX', 'BX', 'CX', 'AN', 'BN', 'CN', 'A', 'B', 'C'])) & (df_COND['FORM_CAB'].isin(['1', '6']) ),'FT_MUL_FAS'] = 1
    df_COND.loc[(df_COND['FAS_CON'].isin(['ABN', 'ACN', 'CAN', 'BCN', 'AB', 'AC', 'CA', 'BC'])) & (df_COND['FORM_CAB'].isin(['1', '6']) ),'FT_MUL_FAS'] = 2
    df_COND.loc[(df_COND['FAS_CON'].isin(['ABCN', 'ABC'])) & (df_COND['FORM_CAB'].isin(['1', '6']) ),'FT_MUL_FAS'] = 3
    df_COND.loc[(df_COND['FAS_CON'].isin(['N'])),'FT_MUL_FAS'] = 0
    df_COND.loc[(df_COND['FAS_CON'].isin(['ABCN', 'ABN', 'ACN', 'CAN', 'BCN', 'AN', 'BN', 'CN', 'N'])) & (df_COND['FORM_CAB'].isin(['1', '6'])),'FT_MUL_NEU'] = 1

    df_COND.loc[df_COND['A3_FAS'].isin([2, 3, 4, 5, 9]), 'FTRCNV'] = 1
    df_COND.loc[df_COND['A3_FAS'].isin([2, 3, 4, 5, 9]), 'VL_FC_FAS'] = 1
    df_COND.loc[df_COND['A3_FAS'].isin([2, 3, 4, 5, 9]), 'VL_FC_NEU'] = 1
    df_COND['TST_FTRCNV'] = 'OK'
    df_COND.loc[df_COND['A3_FAS'].isin([1, 6, 7, 8]) & ((df_COND['FTRCNV'] / df_COND['VL_FC_FAS']) > 10), 'TST_FTRCNV'] =  'AVALIAR, FATOR DEVE ESTAR EM kg/km'
    df_COND['Qtd_F'] = df_COND['COMP'] * (df_COND['FT_MUL_FAS'] * df_COND['VL_FC_FAS'] * df_COND['CND_FAS'])
    df_COND['Qtd_N'] = df_COND['COMP'] * (df_COND['FT_MUL_NEU'] * df_COND['VL_FC_NEU'])
    df_COND["CONJ"] = df_COND["CONJ"].astype(str)
    df_COND.to_feather(f'{dir_arq_base}//df_COND_{sufixo}.feather')
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//df_COND_{sufixo}.feather',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    
    RCP_BDGD_AT = df_COND[df_COND['Qtd_F'] > 0][['ODI', 'TI', 'TUC_FAS', 'A1_FAS', 'A2_FAS', 'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS', 'Qtd_F']]
    RCP_BDGD_AT.columns = ['ODI', 'TI', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'Qtd']

    df = df_COND[df_COND['Qtd_N'] > 0][['ODI', 'TI', 'TUC_NEU', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU', 'Qtd_N']]
    df.columns = ['ODI', 'TI', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'Qtd']
    RCP_BDGD_AT = pd.concat([RCP_BDGD_AT, df])

    lst_TUCagem = ['TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6']
    for n in lst_TUCagem:
        df_EQCR[n] = pd.to_numeric(df_EQCR[n], errors = 'coerce') if len(df_EQCR) > 0 else None
        df_EQRE[n] = pd.to_numeric(df_EQRE[n], errors = 'coerce') if len(df_EQRE) > 0 else None
        df_MED[n] = pd.to_numeric(df_MED[n], errors = 'coerce') if len(df_MED) > 0 else None
        df_EQSE[n] = pd.to_numeric(df_EQSE[n], errors = 'coerce') if len(df_EQSE) > 0 else None
        df_TRME[n] = pd.to_numeric(df_TRME[n], errors = 'coerce') if len(df_TRME) > 0 else None
        df_TRD[n] = pd.to_numeric(df_TRD[n], errors = 'coerce') if len(df_TRD) > 0 else None
        df_TRSE[n] = pd.to_numeric(df_TRSE[n], errors = 'coerce') if len(df_TRSE) > 0 else None
        df_ESTR[n] = pd.to_numeric(df_ESTR[n], errors = 'coerce') if len(df_ESTR) > 0 else None

    def agrega(RCP_BDGD_AT, df):
        cols = ['ODI', 'TI', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'Qtd']
        return pd.concat([RCP_BDGD_AT, df[cols]]) if not df.empty else RCP_BDGD_AT

    RCP_BDGD_AT = agrega(RCP_BDGD_AT, df_EQCR)
    RCP_BDGD_AT = agrega(RCP_BDGD_AT, df_EQRE)
    RCP_BDGD_AT = agrega(RCP_BDGD_AT, df_MED)

    RCP_BDGD_AT = agrega(RCP_BDGD_AT, df_EQSE)
    RCP_BDGD_AT = agrega(RCP_BDGD_AT, df_TRME)

    RCP_BDGD_AT = agrega(RCP_BDGD_AT, df_TRD)

    RCP_BDGD_AT = agrega(RCP_BDGD_AT, df_TRSE)
    RCP_BDGD_AT = agrega(RCP_BDGD_AT, df_ESTR[(df_ESTR['TIP_PN'] == 'POS') | (df_ESTR['TIP_PN'] == 'PSE')])

    LST_TI = [str(x) for x in range(9, 30)] + [str(x) for x in range(69, 93)] + ['94', '95', '97', '99']
    RCP_BDGD_AT = RCP_BDGD_AT[~RCP_BDGD_AT['TI'].isin(LST_TI)]
    RCP_BDGD_AT = RCP_BDGD_AT.groupby(['ODI', 'TI', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6'], dropna=False)['Qtd'].sum().reset_index()
    RCP_BDGD_AT.to_feather(f'{dir_arq_base}//RCP_BDGD_{sufixo}.feather')
    RCP_BDGD_AT.to_sql(f'RCP_BDGD_{sufixo}', con, if_exists='replace', index=False)
    end = time.time()
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//RCP_BDGD_{sufixo}.feather',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        avl.progress(100, text= "Finalizado!!")
        st.success(f'Criou o RCP da BDGD {sufixo} em {f"{end - start: .2f}".replace(".",",")} segundos.')

    return "OK"

@monitor_completo(st.session_state.LOGGER)
def RCP_base_M10(dir_arq_base, con, empresa = 'ND', ano = 0, st = None, sufixo="ANT"):
    start = time.time()
    if st:
        avl = st.progress(0, text= "Lendo os dados dos conjuntos...")

    df_EQCR = pd.DataFrame()
    df_EQRE = pd.DataFrame()
    df_MED = pd.DataFrame()
    df_EQSEC = pd.DataFrame()
    df_TRM = pd.DataFrame()
    df_TRD = pd.DataFrame()
    df_TRSE = pd.DataFrame()
    df_ESTR = pd.DataFrame()
    df_TRSEX = pd.DataFrame()
    
    if st:
        avl.progress(10, text= "Lendo os dados de estruturas...")
    if existe_tabela(f"PONNOT_{sufixo}", con):
            sSQL = f"SELECT * FROM PONNOT_{sufixo}"
            df_ESTR = pd.read_sql(sSQL, con)
            SQLq = f"""
            SELECT DISTINCT ODI, TI, TUC, A1, A2, A3, A4, A5, A6, ARE_LOC, TIP_PN, POS, ESTR, MAT, ESF, ALT,
            CONJ, MUN, COUNT(CM) AS Qtd
            FROM PONNOT_{sufixo} WHERE SITCONT in ('AT1','RT','SF')
            AND (TIP_PN = 'POS' or TIP_PN = 'TOR' or TIP_PN = 'PSE') AND POS = 'PD'
            GROUP BY ODI, TI, TUC, A1, A2, A3, A4, A5, A6, ARE_LOC, TIP_PN, POS, ESTR, MAT, ESF, ALT,
            CONJ, MUN
            """
            df_ESTR = pd.read_sql(SQLq, con)

    df_ESTR.to_feather(f'{dir_arq_base}//df_ESTR_{sufixo}.feather')
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//df_ESTR_{sufixo}.feather',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        
    if existe_tabela(f"UNTRS_{sufixo}", con):
        SQLq = f"""
            SELECT DISTINCT t1.ODI, t1.POS, t1.CLAS_TEN, t1.POT_NOM, t1.LIG,
            t1.FAS_CON, t1.TEN_PRI, t1.TEN_SEC, t1.TEN_TER, t2.ARE_LOC,
            t1.TI, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.DAT_IMO, t2.DAT_CON, COUNT(t1.SITCONT) AS Qtd

            FROM EQTRS_{sufixo} t1 LEFT JOIN UNTRS_{sufixo} t2 ON
            (t1.PAC_1 = t2.PAC_1) AND (t1.PAC_2 = t2.PAC_2)
            WHERE t1.SITCONT in ('AT1','RT','SF') AND t1.POS = 'PD'
            GROUP BY t1.ODI, t1.POS, t1.CLAS_TEN, t1.POT_NOM, t1.LIG,
            t1.FAS_CON, t1.TEN_PRI, t1.TEN_SEC, t1.TEN_TER, t2.ARE_LOC,
            t1.TI, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.DAT_IMO, t2.DAT_CON
            """
        df_TRSE = pd.read_sql(SQLq, con)
    
    df_TRSE.to_feather(f'{dir_arq_base}//df_TRSE_{sufixo}.feather')
    if st:
        avl.progress(20, text= "Lendo os dados de transformadores de força...")
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//df_TRSE_{sufixo}.feather',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    
    if existe_tabela(f"EQTRSX_{sufixo}", con):
        SQLq = f"""
            SELECT DISTINCT t1.ODI, t2.POS, t1.TIP_UNID, t2.NOM,
            t1.TI, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.DAT_IMO, COUNT(t1.SITCONT) AS Qtd

            FROM EQTRSX_{sufixo} t1 LEFT JOIN SUB_{sufixo} t2 ON
            (t1.SUB = t2.COD_ID)
            WHERE t1.SITCONT in ('AT1','RT','SF') AND t2.POS = 'PD'
            GROUP BY t1.ODI, t2.POS, t1.TIP_UNID, t2.NOM,
            t1.TI, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.DAT_IMO
            """
        df_TRSEX = pd.read_sql(SQLq, con)
        df_TRSEX.to_feather(f'{dir_arq_base}//df_TRSEX_{sufixo}.feather')
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//df_TRSEX_{sufixo}.feather',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)

    if st:
        avl.progress(30, text= "Lendo os dados de transformadores auxiliares...")
    if existe_tabela(f"UNTRD_{sufixo}", con):
        SQLq = f"""
            SELECT DISTINCT t1.ODI, t2.TIP_UNID, t1.CLAS_TEN, t1.POT_NOM, t1.LIG,
            t1.FAS_CON, t1.TEN_PRI, t1.TEN_SEC, t1.TEN_TER, t2.ARE_LOC,
            t2.CAP_ELO, t2.CAP_CHA, t2.TIP_TRAFO,
            t1.TI, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.DAT_IMO, t2.DAT_CON, COUNT(t1.SITCONT) AS Qtd

            FROM EQTRD_{sufixo} t1 LEFT JOIN UNTRD_{sufixo} t2 ON
            (t1.PAC_1 = t2.PAC_1) AND (t1.PAC_2 = t2.PAC_2)
            WHERE t1.SITCONT in ('AT1','RT','SF') AND t2.POS = 'PD'
            GROUP BY t1.ODI, t2.TIP_UNID, t1.CLAS_TEN, t1.POT_NOM, t1.LIG,
            t1.FAS_CON, t1.TEN_PRI, t1.TEN_SEC, t1.TEN_TER, t2.ARE_LOC,
            t2.CAP_ELO, t2.CAP_CHA, t2.TIP_TRAFO,
            t1.TI, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.DAT_IMO, t2.DAT_CON
            """
        df_TRD = pd.read_sql(SQLq, con)
    df_TRD.to_feather(f'{dir_arq_base}//df_TRD_{sufixo}.feather')
    if st:
        avl.progress(40, text= "Lendo os dados de transformadores de distribuição...")
        registrar_artefato(st.session_state.database_MAN, 
                                    st.session_state.execucao_id, 
                                    file_path = rf'{dir_arq_base}//df_TRD_{sufixo}.feather',
                                    tipo_artefato = "SAIDA", 
                                    calcular_hash = True)
    
    if existe_tabela(f"EQME_{sufixo}", con):
        SQLq = f"""
                SELECT DISTINCT t1.ODI, t1.TIP_UNID,
                t1.TI, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.DAT_IMO, COUNT(t1.SITCONT) AS Qtd
                FROM EQTRM_{sufixo} t1
                WHERE t1.SITCONT in ('AT1','RT','SF')
                GROUP BY t1.ODI, t1.TIP_UNID,
                t1.TI, t1.TUC, t1.A1, t1.A2, t1.A3, t1.A4, t1.A5, t1.A6, t1.DAT_IMO
               """
        df_TRM = pd.read_sql(SQLq, con)
    df_TRM.to_feather(f'{dir_arq_base}//df_TRM_{sufixo}.feather')
    if st:
        avl.progress(50, text= "Lendo os dados de transformadores de medição...")
        registrar_artefato(st.session_state.database_MAN, 
                                    st.session_state.execucao_id, 
                                    file_path = rf'{dir_arq_base}//df_TRM_{sufixo}.feather',
                                    tipo_artefato = "SAIDA", 
                                    calcular_hash = True)
    
    LST_ATV = [f'UNSEMT_{sufixo}', f'UNSEBT_{sufixo}', f'UNSEAT_{sufixo}']
    df_UNISEC = pd.DataFrame()
    for nm in LST_ATV:  
        if existe_tabela(nm, con):
            SQLq = f"""
                    SELECT PAC_1, PAC_2, POS, TIP_UNID, DAT_CON, TLCD
                    FROM {nm} WHERE POS = 'PD'"""

            df = pd.read_sql(SQLq, con)
            df_UNISEC = pd.concat([df_UNISEC, df])
    
    if existe_tabela(f"EQSE_{sufixo}", con):
        SQLq = f"""
                SELECT PAC_1, PAC_2, CLAS_TEN, ELO_FSV, MEI_ISO, COR_NOM,
                FAS_CON, ODI, TI, TUC, A1, A2, A3, A4, A5, A6, ABER_CRG, DAT_IMO
                FROM EQSE_{sufixo} WHERE SITCONT in ('AT1','RT','SF')
               """
        df_EQSEC = pd.read_sql(SQLq, con)

    df_EQSEC = df_EQSEC.merge(df_UNISEC, on = ['PAC_1', 'PAC_2'], how = 'left' )
    df_EQSEC['Qtd'] = 1

    df_EQSEC = df_EQSEC.groupby(['CLAS_TEN', 'ELO_FSV', 'MEI_ISO', 'COR_NOM', 'FAS_CON', 'ODI', 'TUC', 'TI', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'ABER_CRG', 'DAT_IMO', 'POS', 'TIP_UNID', 'DAT_CON'],dropna=False)['Qtd'].sum().reset_index()
    df_EQSEC.to_feather(f'{dir_arq_base}//df_EQSE_{sufixo}.feather')
    if st:
        avl.progress(60, text= "Lendo os dados de seccionadoras...")
        registrar_artefato(st.session_state.database_MAN, 
                                    st.session_state.execucao_id, 
                                    file_path = rf'{dir_arq_base}//df_EQSE_{sufixo}.feather',
                                    tipo_artefato = "SAIDA", 
                                    calcular_hash = True)

    if existe_tabela(f"EQME_{sufixo}", con):
        SQLq = f"""
                SELECT DISTINCT t2.ODI, t2.TIP_UNID, t2.FAS_CON, t2.TIPMED,
                t2.TI, t2.TUC, t2.A1, t2.A2, t2.A3, t2.A4, t2.A5, t2.A6, t2.DAT_IMO, COUNT(t2.SITCONT) AS Qtd
                FROM EQME_{sufixo} t2 
                WHERE t2.SITCONT in ('AT1','RT','SF') AND t2.A1 in ('01','1','11','13',1,11,13)
                GROUP BY t2.ODI, t2.TIP_UNID, t2.FAS_CON, t2.TIPMED,
                t2.TI, t2.TUC, t2.A1, t2.A2, t2.A3, t2.A4, t2.A5, t2.A6, t2.DAT_IMO
               """
        df_MED = pd.read_sql(SQLq, con)
    df_MED.to_feather(f'{dir_arq_base}//df_MED_{sufixo}.feather')
    if st:
        avl.progress(70, text= "Lendo os dados de medidores...")
        registrar_artefato(st.session_state.database_MAN, 
                                            st.session_state.execucao_id, 
                                            file_path = rf'{dir_arq_base}//df_MED_{sufixo}.feather',
                                            tipo_artefato = "SAIDA", 
                                            calcular_hash = True)
    
    df_UNIRE = pd.DataFrame()
    LST_ATV = [f"UNREMT_{sufixo}", f'UNREBT_{sufixo}', f'UNREAT_{sufixo}']

    for nm in LST_ATV:  
        if existe_tabela(nm, con):
            SQLq = """
                    SELECT PAC_1, PAC_2, POS, TIP_UNID, DAT_CON, FAS_CON, SIT_ATIV
                    FROM """ + nm + " WHERE POS = 'PD'"

            df = pd.read_sql(SQLq, con)
            df_UNIRE = pd.concat([df_UNIRE, df])

    if existe_tabela(f"EQRE_{sufixo}", con):
        SQLq = f"""
                SELECT PAC_1, PAC_2, POT_NOM, TIP_REGU, TEN_REG, LIG_FAS_P,
                LIG_FAS_S, COR_NOM, REL_TP, REL_TC, ODI, TI, TUC, A1, A2, A3, A4, A5, A6, DAT_IMO
                FROM EQRE_{sufixo} WHERE SITCONT in ('AT1','RT','SF')
               """
        df_EQRE = pd.read_sql(SQLq, con)

        df_EQRE = df_EQRE.merge(df_UNIRE, on = ['PAC_1', 'PAC_2'], how = 'left' )
        df_EQRE['Qtd'] = 1
        df_EQRE.fillna('ND', inplace = True)

        df_EQRE = df_EQRE.groupby(['POT_NOM', 'TIP_REGU', 'TEN_REG', 'LIG_FAS_P', 'LIG_FAS_S', 'COR_NOM', 'REL_TP', 'REL_TC', 'ODI', 'TI', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'POS', 'TIP_UNID', 'FAS_CON', 'SIT_ATIV', 'DAT_CON', 'DAT_IMO'],dropna=False)['Qtd'].sum().reset_index()
        df_EQRE.to_feather(f'{dir_arq_base}//df_EQRE_{sufixo}.feather')
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//df_EQRE_{sufixo}.feather',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        avl.progress(80, text= "Lendo os dados de reguladores...")
        
    df_UNICR = pd.DataFrame()
    LST_ATV = [f"UNCRMT_{sufixo}", f'UNCRBT_{sufixo}', f'UNCRAT_{sufixo}']

    for nm in LST_ATV:  
        if existe_tabela(nm, con):
            SQLq = """
                    SELECT PAC_1, PAC_2, POS, TIP_UNID, DAT_CON, FAS_CON, SIT_ATIV, ARE_LOC, BANC, POT_NOM
                    FROM """ + nm + " WHERE POS = 'PD'"

            df = pd.read_sql(SQLq, con)
            df_UNICR = pd.concat([df_UNICR, df])

    if existe_tabela(f"EQCR_{sufixo}", con):
        SQLq = f"""
                SELECT PAC_1, PAC_2, ODI, TI, TUC, A1, A2, A3, A4, A5, A6, DAT_IMO
                FROM EQCR_{sufixo} WHERE SITCONT in ('AT1','RT','SF') AND
                (TUC = '125' OR TUC = '130')
               """
        df_EQCR = pd.read_sql(SQLq, con)


    df_EQCR = df_EQCR.merge(df_UNICR, on = ['PAC_1', 'PAC_2'], how = 'left' )

    df_EQCR['Qtd'] = 1
    df_EQCR.fillna('ND', inplace = True)
    df_EQCR = df_EQCR.groupby(['ODI', 'TI', 'ARE_LOC', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'POS', 'TIP_UNID', 'FAS_CON', 'BANC', 'POT_NOM', 'SIT_ATIV', 'DAT_CON', 'DAT_IMO'],dropna=False)['Qtd'].sum().reset_index()
    df_EQCR['BANC'] = pd.to_numeric(df_EQCR['BANC'], errors = 'coerce')
    df_EQCR.to_feather(f'{dir_arq_base}//df_EQCR_{sufixo}.feather')
    
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                                            st.session_state.execucao_id, 
                                            file_path = rf'{dir_arq_base}//df_EQCR_{sufixo}.feather',
                                            tipo_artefato = "SAIDA", 
                                            calcular_hash = True)
        avl.progress(90, text= "Lendo os dados de capacitores...")
    LST_TBL = [f'SSDAT_{sufixo}', f'SSDMT_{sufixo}', f'SSDBT_{sufixo}', f'RAMLIG_{sufixo}']
    df_COND = pd.DataFrame()
    for nm in LST_TBL:
        if existe_tabela(nm, con):
            SQLq = """
                    SELECT DISTINCT t1.CONJ, t1.FAS_CON, t1.TIP_CND, t1.ODI_FAS, t1.TI_FAS, t1.SITCONTFAS, t1.ODI_NEU, 
                           t1.TI_NEU, t1.SITCONTNEU, t1.POS, t1.DESCR, t2.BIT_FAS_1, t2.BIT_FAS_2, t2.BIT_FAS_3, t2.BIT_NEU, 
                           t2.MAT_FAS_1, t2.MAT_FAS_2, t2.MAT_FAS_3, t2.MAT_NEU, t2.ISO_FAS_1, t2.ISO_FAS_2, t2.ISO_FAS_3, t2.ISO_NEU, 
                           t2.CM_FAS, t2.TUC_FAS, t2.CM_NEU, t2.TUC_NEU, t2.FORM_CAB,
                           t2.A1_FAS, t2.A2_FAS, t2.A3_FAS, t2.A4_FAS, t2.A5_FAS, t2.A6_FAS,
                           t2.A1_NEU, t2.A2_NEU, t2.A3_NEU, t2.A4_NEU, t2.A5_NEU, t2.A6_NEU, SUM(t1.COMP) AS COMP
                    FROM """ + nm + f""" t1 LEFT JOIN SEGCON_{sufixo} t2
                    ON t1.TIP_CND = t2.cod_id WHERE t1.POS = 'PD'
                    GROUP BY t1.CONJ, t1.FAS_CON, t1.TIP_CND, t1.ODI_FAS, t1.TI_FAS, t1.SITCONTFAS, t1.ODI_NEU, 
                             t1.TI_NEU, t1.SITCONTNEU, t1.POS, t1.DESCR, t2.BIT_FAS_1, t2.BIT_FAS_2, t2.BIT_FAS_3, t2.BIT_NEU, 
                             t2.MAT_FAS_1, t2.MAT_FAS_2, t2.MAT_FAS_3, t2.MAT_NEU, t2.ISO_FAS_1, t2.ISO_FAS_2, t2.ISO_FAS_3, t2.ISO_NEU, 
                             t2.CM_FAS, t2.TUC_FAS, t2.CM_NEU, t2.TUC_NEU, t2.FORM_CAB,
                             t2.A1_FAS, t2.A2_FAS, t2.A3_FAS, t2.A4_FAS, t2.A5_FAS, t2.A6_FAS,
                             t2.A1_NEU, t2.A2_NEU, t2.A3_NEU, t2.A4_NEU, t2.A5_NEU, t2.A6_NEU
                   """
            df = pd.read_sql(SQLq, con)
            df_COND = pd.concat([df_COND, df])

    if st:
        avl.progress(95, text= "Lendo os dados de condutores...")
    lst_TUCagem = ['TUC_FAS', 'TUC_NEU', 'A1_FAS', 'A2_FAS', 'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU']
    for n in lst_TUCagem:
        df_COND[n] = pd.to_numeric(df_COND[n], errors = 'coerce') if len(df_COND[n]) > 0 else None

    tbl_FC = pd.read_csv("tabelas//tbl_FC_cabos.csv", sep="|",decimal=',',on_bad_lines='skip',encoding="Latin-1");

    df_COND = df_COND.merge(tbl_FC, how = 'left', left_on = ['TUC_FAS', 'A1_FAS', 'A2_FAS', 'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS'], right_on = ['Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6'])
    df_COND = df_COND[['CONJ', 'FAS_CON', 'TIP_CND', 'ODI_FAS', 'TI_FAS', 'SITCONTFAS', 'ODI_NEU', 'TI_NEU', 'SITCONTNEU', 'POS', 'DESCR',
     'BIT_FAS_1', 'BIT_FAS_2', 'BIT_FAS_3', 'BIT_NEU', 'MAT_FAS_1', 'MAT_FAS_2', 'MAT_FAS_3', 'MAT_NEU', 'ISO_FAS_1',
     'ISO_FAS_2', 'ISO_FAS_3', 'ISO_NEU', 'CM_FAS', 'TUC_FAS', 'CM_NEU', 'TUC_NEU', 'FORM_CAB', 'A1_FAS', 'A2_FAS',
     'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU', 'COMP', 'VL_FC']]
    df_COND.columns = ['CONJ', 'FAS_CON', 'TIP_CND', 'ODI_FAS', 'TI_FAS', 'SITCONTFAS', 'ODI_NEU', 'TI_NEU', 'SITCONTNEU', 'POS', 'DESCR',
     'BIT_FAS_1', 'BIT_FAS_2', 'BIT_FAS_3', 'BIT_NEU', 'MAT_FAS_1', 'MAT_FAS_2', 'MAT_FAS_3', 'MAT_NEU', 'ISO_FAS_1',
     'ISO_FAS_2', 'ISO_FAS_3', 'ISO_NEU', 'CM_FAS', 'TUC_FAS', 'CM_NEU', 'TUC_NEU', 'FORM_CAB', 'A1_FAS', 'A2_FAS',
     'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU', 'COMP', 'VL_FC_FAS']
    df_COND['VL_FC_FAS'] = df_COND['VL_FC_FAS'].fillna(1)
    df_COND = df_COND.merge(tbl_FC, how = 'left', left_on = ['TUC_NEU', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU'], right_on = ['Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6'])
    df_COND = df_COND[['CONJ', 'FAS_CON', 'TIP_CND', 'ODI_FAS', 'TI_FAS', 'SITCONTFAS', 'ODI_NEU', 'TI_NEU', 'SITCONTNEU', 'POS', 'DESCR',
     'BIT_FAS_1', 'BIT_FAS_2', 'BIT_FAS_3', 'BIT_NEU', 'MAT_FAS_1', 'MAT_FAS_2', 'MAT_FAS_3', 'MAT_NEU', 'ISO_FAS_1',
     'ISO_FAS_2', 'ISO_FAS_3', 'ISO_NEU', 'CM_FAS', 'TUC_FAS', 'CM_NEU', 'TUC_NEU', 'FORM_CAB', 'A1_FAS', 'A2_FAS',
     'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU', 'COMP', 'VL_FC_FAS', 'VL_FC']]
    df_COND.columns = ['CONJ', 'FAS_CON', 'TIP_CND', 'ODI_FAS', 'TI_FAS', 'SITCONTFAS', 'ODI_NEU', 'TI_NEU', 'SITCONTNEU', 'POS', 'DESCR',
     'BIT_FAS_1', 'BIT_FAS_2', 'BIT_FAS_3', 'BIT_NEU', 'MAT_FAS_1', 'MAT_FAS_2', 'MAT_FAS_3', 'MAT_NEU', 'ISO_FAS_1',
     'ISO_FAS_2', 'ISO_FAS_3', 'ISO_NEU', 'CM_FAS', 'TUC_FAS', 'CM_NEU', 'TUC_NEU', 'FORM_CAB', 'A1_FAS', 'A2_FAS',
     'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU', 'COMP', 'VL_FC_FAS', 'VL_FC_NEU']
    df_COND['VL_FC_NEU'] = df_COND['VL_FC_NEU'].fillna(1)

    df_COND['FT_MUL_FAS'] = 1
    df_COND['FT_MUL_NEU'] = 0
    df_COND.loc[(df_COND['FAS_CON'].isin(['AX', 'BX', 'CX', 'AN', 'BN', 'CN', 'A', 'B', 'C'])) & (df_COND['FORM_CAB'].isin(['1', '6']) ),'FT_MUL_FAS'] = 1
    df_COND.loc[(df_COND['FAS_CON'].isin(['ABN', 'ACN', 'CAN', 'BCN', 'AB', 'AC', 'CA', 'BC'])) & (df_COND['FORM_CAB'].isin(['1', '6']) ),'FT_MUL_FAS'] = 2
    df_COND.loc[(df_COND['FAS_CON'].isin(['ABCN', 'ABC'])) & (df_COND['FORM_CAB'].isin(['1', '6']) ),'FT_MUL_FAS'] = 3
    df_COND.loc[(df_COND['FAS_CON'].isin(['N'])) & (df_COND['FORM_CAB'].isin(['1', '6'])) & (df_COND['FORM_CAB'].isin(['1', '6'])),'FT_MUL_FAS'] = 0


    df_COND.loc[(df_COND['FAS_CON'].isin(['ABCN', 'ABN', 'ACN', 'CAN', 'BCN', 'AN', 'BN', 'CN', 'N'])) & (df_COND['FORM_CAB'].isin(['1', '6']) ),'FT_MUL_NEU'] = 1

    df_COND['Qtd_F'] = df_COND['COMP'] * (df_COND['FT_MUL_FAS'] * df_COND['VL_FC_FAS'])
    df_COND['Qtd_N'] = df_COND['COMP'] * (df_COND['FT_MUL_NEU'] * df_COND['VL_FC_NEU'])

    df_COND.to_feather(f'{dir_arq_base}//df_COND_{sufixo}.feather')
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//df_COND_{sufixo}.feather',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    RCP_BDGD_ANT = df_COND[df_COND['Qtd_F'] > 0][['ODI_FAS', 'TI_FAS', 'TUC_FAS', 'A1_FAS', 'A2_FAS', 'A3_FAS', 'A4_FAS', 'A5_FAS', 'A6_FAS', 'Qtd_F']]
    RCP_BDGD_ANT.columns = ['ODI', 'TI', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'Qtd']

    df = df_COND[df_COND['Qtd_N'] > 0][['ODI_NEU', 'TI_NEU', 'TUC_NEU', 'A1_NEU', 'A2_NEU', 'A3_NEU', 'A4_NEU', 'A5_NEU', 'A6_NEU', 'Qtd_N']]
    df.columns = ['ODI', 'TI', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'Qtd']
    RCP_BDGD_ANT = pd.concat([RCP_BDGD_ANT, df])

    if st:
        avl.progress(97, text= "Consolidando...")
    lst_TUCagem = ['TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6']
    for n in lst_TUCagem:
        df_EQCR[n] = pd.to_numeric(df_EQCR[n], errors = 'coerce') if len(df_EQCR) > 0 else None
        df_EQRE[n] = pd.to_numeric(df_EQRE[n], errors = 'coerce') if len(df_EQRE) > 0 else None
        df_MED[n] = pd.to_numeric(df_MED[n], errors = 'coerce') if len(df_MED) > 0 else None
        df_EQSEC[n] = pd.to_numeric(df_EQSEC[n], errors = 'coerce') if len(df_EQSEC) > 0 else None
        df_TRM[n] = pd.to_numeric(df_TRM[n], errors = 'coerce') if len(df_TRM) > 0 else None
        df_TRD[n] = pd.to_numeric(df_TRD[n], errors = 'coerce') if len(df_TRD) > 0 else None
        df_TRSE[n] = pd.to_numeric(df_TRSE[n], errors = 'coerce') if len(df_TRSE) > 0 else None
        df_ESTR[n] = pd.to_numeric(df_ESTR[n], errors = 'coerce') if len(df_ESTR) > 0 else None
        df_TRSEX[n] = pd.to_numeric(df_TRSEX[n], errors = 'coerce') if len(df_TRSEX) > 0 else None

    def agrega(RCP_BDGD_ANT, df):
        cols = ['ODI', 'TI', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'Qtd']
        return pd.concat([RCP_BDGD_ANT, df[cols]]) if not df.empty else RCP_BDGD_ANT

    RCP_BDGD_ANT = agrega(RCP_BDGD_ANT, df_EQCR)
    RCP_BDGD_ANT = agrega(RCP_BDGD_ANT, df_EQRE)
    RCP_BDGD_ANT = agrega(RCP_BDGD_ANT, df_MED)
    RCP_BDGD_ANT = agrega(RCP_BDGD_ANT, df_EQSEC)
    RCP_BDGD_ANT = agrega(RCP_BDGD_ANT, df_TRSEX)
    RCP_BDGD_ANT = agrega(RCP_BDGD_ANT, df_TRM)
    RCP_BDGD_ANT = agrega(RCP_BDGD_ANT, df_TRD)
    RCP_BDGD_ANT = agrega(RCP_BDGD_ANT, df_TRSE)
    RCP_BDGD_ANT = agrega(RCP_BDGD_ANT, df_ESTR)

    LST_TI = [str(x) for x in range(9, 30)] + [str(x) for x in range(69, 93)] + ['94', '95', '97', '98', '99']
    RCP_BDGD_ANT = RCP_BDGD_ANT[~RCP_BDGD_ANT['TI'].isin(LST_TI)]
    RCP_BDGD_ANT = RCP_BDGD_ANT.groupby(['ODI', 'TI', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6'],dropna=False)['Qtd'].sum().reset_index()
    RCP_BDGD_ANT.to_feather(f'{dir_arq_base}//RCP_BDGD_{sufixo}.feather')
    RCP_BDGD_ANT.to_sql(f'RCP_BDGD_{sufixo}', con, if_exists='replace', index=False)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//RCP_BDGD_{sufixo}.feather',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        avl.progress(100, text= "Finalizado!")
        end = time.time()
        st.success(f"Criou o RCP da BDGD {sufixo} em {f'{end - start: .2f}'.replace('.',',')} segundos.")
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def RCP_TOT(dir_arq_base, con, Empresa, st=None):
    now = datetime.now() 
    if st:         avl = st.success(f"  Hora de início, consolidação de RCP: {now.strftime('%H:%M:%S')}")   
    dt_ARQ = max_arq("AIS", con, Empresa)         
    df1 = pd.read_sql(f"""SELECT MAX(date(Dt_Imob)) AS DT FROM  AIS t1
                            WHERE t1.dt_ARQ = {dt_ARQ}
                            AND t1.FLG_PER  = '1'""", con)
    ano_corrente = pd.to_datetime(df1['DT']).dt.year.iloc[-1]
    
    RCP_BDGD_ANT = pd.read_feather(f'{dir_arq_base}//BDGD_ANLS//RCP_BDGD_ANT.feather')
    RCP_BDGD_AT = pd.read_feather(f'{dir_arq_base}//BDGD_ANLS//RCP_BDGD_AT.feather')

    nm_BASE = Path(dir_arq_base) / "BDGD_AT" / "BASE.dbf"
    data_corte = f"{ano_corrente}-01-01"
    if nm_BASE.exists():
        try:
            dbf = DBF(nm_BASE)
            df_ano = pd.DataFrame(iter(dbf))
        except:
            dbf = DBF(nm_BASE, encoding='utf-8')
            df_ano = pd.DataFrame(iter(dbf))
        data_corte = pd.to_datetime(df_ano['DAT_EXT'], format="%d/%m/%Y").dt.strftime("%Y-%m-%d").iloc[-1]

    LST_TI = [(x) for x in range(69, 93)] + [94, 95, 97, 99]
    LST_TI +=  [str(x) for x in range(69, 93)] + [94, 95, 97, 99]
    FILTRO_TI = f"{LST_TI}".replace("[","(").replace("]",")")
    FILTRO_UC = ['125', '130', '160', '190', '210', '255', '295', '330', '340', '345', '545', '565', '570', '575']
    dt_ARQ = max_arq("INCR", con, Empresa)
    if dt_ARQ and (st.session_state.dt_fim <= date.today()):
        SQLq = f"""
            SELECT Cd_UAR, Nr_TI, Nr_TUC, Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5,
            Nr_A6, Qtd_AIS, FLG_ELIG, Cd_CONC
            FROM INCR t1 WHERE t1.dt_ARQ = {dt_ARQ} AND (t1.FLG_ELIG = '1' AND t1.Cd_CONC IN ('1', '3'))
            AND ((t1.Nr_TI not in {FILTRO_TI}) | (t1.Nr_TUC='570')) AND t1.Cd_UAR <> 'UAR'
            
            """
        RCP_INC = pd.read_sql(SQLq, con)
        if (RCP_INC['Qtd_AIS'].dtype == 'object'):
            RCP_INC['Qtd_AIS'] = pd.to_numeric(RCP_INC['Qtd_AIS'].str.replace(",","."), errors='coerce')
    else:
        if st.session_state.dt_fim >= date.today():
            avl.warning(f"  Buscando alternativa para INCR, período intercalar de análise. Início em: {now.strftime('%H:%M:%S')}")
            dt_ARQ = max_arq("AIS", con, Empresa)
            if dt_ARQ:
                SQLq = f"""
                        SELECT Cd_UAR, Nr_TI, Nr_TUC, Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5,
                        Nr_A6, Qtd_AIS, "1" AS FLG_ELIG, "1" AS Cd_CONC
                        FROM AIS t1
                        WHERE t1.dt_ARQ = {dt_ARQ}
                        AND t1.FLG_PER  = "1"
                        AND ((t1.Nr_TI not in {FILTRO_TI}) | ((t1.Nr_TI='98'))) AND t1.Cd_UAR <> 'UAR'
                        """
                if st.session_state.dt_fim >= date.today():
                    SQLq += f"""
                            AND date(Dt_Imob) < ?
                            """
                    RCP_INC = pd.read_sql(SQLq, con, params=(data_corte,))

                    SQLq = f"""
                            SELECT Cd_ODI, Cd_UAR, Nr_TI, Nr_TUC, Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5,
                            Nr_A6, (Qtd_INI-Qtd_FIN) AS Qtd_AIS, "1" AS FLG_ELIG, "1" AS Cd_CONC
                            FROM BAIXAS t1
                            WHERE t1.dt_ARQ = {dt_ARQ}
                            AND t1.Nr_TI not in {FILTRO_TI} AND t1.Cd_UAR <> 'UAR'
                            AND date(Dt_Imob) < ?  AND date(Dt_Imob) >= ? AND date(Dt_BX) < ?
                            """
                    RCP_BAIXAS = pd.read_sql(SQLq, con, params=(data_corte, st.session_state.dt_ini, data_corte))
                    RCP_INC = pd.concat([RCP_INC, RCP_BAIXAS], ignore_index=True)
                else:
                    RCP_INC = pd.read_sql(SQLq, con)
                if (RCP_INC['Qtd_AIS'].dtype == 'object'):
                    RCP_INC['Qtd_AIS'] = pd.to_numeric(RCP_INC['Qtd_AIS'].str.replace(",","."), errors='coerce')
            elif st:
                avl.error('Falha ao importar o arquivo INCR da base local.')
                return None
        else:
            raise UserWarning('Falha ao importar o arquivo INCR da base local.')

    dt_ARQ = max_arq("AIS", con, Empresa)
    if dt_ARQ:
        SQLq = f"""
            SELECT Cd_UAR, Nr_TI, Nr_TUC, Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5,
            Nr_A6, Qtd_AIS
            FROM AIS t1 WHERE t1.dt_ARQ = {dt_ARQ}
            AND ((t1.Nr_TI not in {FILTRO_TI}) | (t1.Nr_TUC='570')) AND t1.Cd_UAR <> 'UAR'
            """
        if st.session_state.dt_fim >= date.today():
            SQLq += f"""
                    AND date(Dt_Imob) < ?
                    """
            RCP_AIS = pd.read_sql(SQLq, con, params = (data_corte,))
            SQLq = f"""
                            SELECT Cd_ODI, Cd_UAR, Nr_TI, Nr_TUC, Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5,
                            Nr_A6, (Qtd_INI-Qtd_FIN) AS Qtd_AIS, "1" AS FLG_ELIG, "1" AS Cd_CONC
                            FROM BAIXAS t1
                            WHERE t1.dt_ARQ = {dt_ARQ}
                            AND t1.Nr_TI not in {FILTRO_TI} AND t1.Cd_UAR <> 'UAR'
                            AND date(Dt_Imob) < ?  AND date(Dt_BX) < ?
                            """
            RCP_BAIXAS = pd.read_sql(SQLq, con, params=(data_corte, data_corte))
            RCP_AIS = pd.concat([RCP_AIS, RCP_BAIXAS], ignore_index=True)
        else:
            RCP_AIS = pd.read_sql(SQLq, con)
        if (RCP_AIS['Qtd_AIS'].dtype == 'object'):
            RCP_AIS['Qtd_AIS'] = pd.to_numeric(RCP_AIS['Qtd_AIS'].str.replace(",","."), errors='coerce')
    else:
        if st:
            avl.error('Falha ao importar o arquivo AIS da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS da base local.')

    dt_ARQ = max_arq("BAIXAS", con, Empresa)
    if dt_ARQ:
        if st.session_state.dt_fim <= date.today():
            SQLq = f"""
                SELECT Cd_UAR, Nr_TI, Nr_TUC, Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5,
                Nr_A6, Qtd_INI, Qtd_FIN, FLG_AJST_CTB
                FROM BAIXAS t1 WHERE (t1.dt_ARQ = {dt_ARQ}) AND (t1.FLG_AJST_CTB in (0,'0'))
                AND ((t1.Nr_TI not in {FILTRO_TI})) AND (t1.Cd_UAR <> 'UAR')
                """
            RCP_BAIXAS = pd.read_sql(SQLq, con)
        else:
            SQLq = f"""
                SELECT Cd_UAR, Nr_TI, Nr_TUC, Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5,
                Nr_A6, Qtd_INI, Qtd_FIN, FLG_AJST_CTB
                FROM BAIXAS t1 WHERE (t1.dt_ARQ = {dt_ARQ}) AND (t1.FLG_AJST_CTB in (0,'0'))
                AND ((t1.Nr_TI not in {FILTRO_TI})) AND (t1.Cd_UAR <> 'UAR')
                AND date(Dt_BX) < ?
                """
            RCP_BAIXAS = pd.read_sql(SQLq, con, params=(data_corte, ))

        for cmp in ['Qtd_INI', 'Qtd_FIN']:
            if (RCP_BAIXAS[cmp].dtype == 'object'):
                RCP_BAIXAS[cmp] = pd.to_numeric(RCP_BAIXAS[cmp].str.replace(",","."), errors='coerce')
    else:
        if st:
            avl.error('Falha ao importar o arquivo BAIXAS da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo BAIXAS da base local.')

    dt_ARQ = max_arq("PPBB", con, Empresa)
    if dt_ARQ:
        SQLq = f"""
            SELECT t1.Id_SEQ_PP, t1.Cd_UAR, t1.Nr_TI, t1.Nr_TUC, t1.Nr_A1, t1.Nr_A2, t1.Nr_A3, t1.Nr_A4, t1.Nr_A5,
            t1.Nr_A6, t1.Qtd_AIS, t1.FLG_ELIG, t1.Cd_CONC
            FROM PPBB t1 WHERE t1.dt_ARQ = {dt_ARQ}
            """
        RCP_PPBB = pd.read_sql(SQLq, con)
        if (RCP_PPBB['Qtd_AIS'].dtype == 'object'):
            RCP_PPBB['Qtd_AIS'] = pd.to_numeric(RCP_PPBB['Qtd_AIS'].str.replace(",","."), errors='coerce')
    else:
        if st.session_state.dt_fim >= date.today():
            #avl.warning(f"  Buscando alternativa para INCR, período intercalar de análise. Início em: {now.strftime('%H:%M:%S')}")
            dt_ARQ = max_arq("AIS", con, Empresa)
            if dt_ARQ:
                SQLq = f"""
                        SELECT Ide_AIS AS Id_SEQ_PP, Cd_UAR, Nr_TI, Nr_TUC, Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5,
                        Nr_A6, Qtd_AIS, "1" AS FLG_ELIG, "1" AS Cd_CONC
                        FROM AIS t1
                        WHERE t1.dt_ARQ = {dt_ARQ}
                        AND t1.FLG_PER  = "0"
                        AND ((t1.Nr_TI not in {FILTRO_TI})) AND t1.Cd_UAR <> 'UAR'
                        """
                if st.session_state.dt_fim >= date.today():
                    SQLq += f"""
                            AND date(Dt_Imob) < ?
                            """
                    RCP_PPBB = pd.read_sql(SQLq, con, params = (data_corte,))
                else:
                    RCP_PPBB = pd.read_sql(SQLq, con)
                if (RCP_PPBB['Qtd_AIS'].dtype == 'object'):
                    RCP_PPBB['Qtd_AIS'] = pd.to_numeric(RCP_PPBB['Qtd_AIS'].str.replace(",","."), errors='coerce')
            elif st:
                avl.error('Falha ao importar o arquivo PPBB da base local.')
                return None
        else:
            raise UserWarning('Falha ao importar o arquivo PPBB da base local.')
        
    dt_ARQ = max_arq("PCBB", con, Empresa)
    if dt_ARQ:
        try:
            SQLq = f"""
                SELECT t1.Id_SEQ_PP, t1.Qtd_AISa, t1.FLG_ELIG, t1.Cd_CONC
                FROM PCBB t1 WHERE t1.dt_ARQ = {dt_ARQ})
                """
            RCP_PCBB = pd.read_sql(SQLq, con)
        except:
            SQLq = f"""
                SELECT t1.Id_SEQ_PP, t1.Qtd_AISa, t1.FLG_ELIG, t2.Cd_CONC
                FROM PCBB t1 LEFT JOIN PPBB t2 on t1.Id_SEQ_PP = t2.Id_SEQ_PP
                WHERE t1.dt_ARQ = {dt_ARQ} AND ((t1.FLG_ELIG = '1') AND t2.Cd_CONC IN ('1', '3'))
                """
            RCP_PCBB = pd.read_sql(SQLq, con)
        if (RCP_PCBB['Qtd_AISa'].dtype == 'object'):
            RCP_PCBB['Qtd_AISa'] = pd.to_numeric(RCP_PCBB['Qtd_AISa'].str.replace(",","."), errors='coerce')
    else:
        if st.session_state.dt_fim >= date.today():
            dt_ARQ = max_arq("AIS", con, Empresa)
            if dt_ARQ:
                SQLq = f"""
                        SELECT Ide_AIS AS Id_SEQ_PP, Qtd_AIS as Qtd_AISa
                        FROM AIS t1
                        WHERE t1.dt_ARQ = {dt_ARQ}
                        AND t1.FLG_PER  = "0"
                        AND ((t1.Nr_TI not in {FILTRO_TI}) | ((t1.Nr_TI='98') AND (t1.Nr_TUC='570'))) AND t1.Cd_UAR <> 'UAR'
                        """
                if st.session_state.dt_fim >= date.today():
                    SQLq += f"""
                            AND date(Dt_Imob) < ?
                            """
                    RCP_PCBB = pd.read_sql(SQLq, con, params = (data_corte,))
                else:
                    RCP_PCBB = pd.read_sql(SQLq, con)
                if (RCP_PCBB['Qtd_AISa'].dtype == 'object'):
                    RCP_PCBB['Qtd_AISa'] = pd.to_numeric(RCP_PCBB['Qtd_AISa'].str.replace(",","."), errors='coerce')
            elif st:
                avl.error('Falha ao importar o arquivo PCBB da base local.')
                return None
        else:
            raise UserWarning('Falha ao importar o arquivo PCBB da base local.')

    def filtrar_df(df, grupo = ['TUC'], atr = 'A1', col = 'Qtd'):
        exc_295 = (df[grupo[0]].astype(str).isin(['295']) & ~df[atr].astype(str).isin(['01', '1', '11', '13']))
        exc_190 = (df[grupo[0]].astype(str).isin(['190']) & df[atr].astype(str).isin(['3','03']))
        return (df.loc[~(exc_295 | exc_190)].groupby(grupo, dropna=False, as_index=False)[col].sum())

    RCP_BDGD_AT_TOT = filtrar_df(RCP_BDGD_AT)
    RCP_BDGD_AT_TOT = RCP_BDGD_AT_TOT.rename(columns={'Qtd': 'Qtd_BDGD_AT'})

    RCP_BDGD_ANT_TOT = filtrar_df(RCP_BDGD_ANT)
    RCP_BDGD_ANT_TOT.columns = ['TUC', 'Qtd_BDGD_ANT']

    RCP_AIS_TOT = filtrar_df(RCP_AIS, ['Nr_TUC'], 'Nr_A1', 'Qtd_AIS')
    RCP_AIS_TOT.columns = ['TUC', 'Qtd_AIS']

    RCP_INC_TOT = filtrar_df(RCP_INC, ['Nr_TUC'], 'Nr_A1', 'Qtd_AIS')
    RCP_INC_TOT.columns = ['TUC', 'Qtd_INC']

    RCP_BXS_TOT = filtrar_df(RCP_BAIXAS, ['Nr_TUC'], 'Nr_A1', ['Qtd_INI', 'Qtd_FIN'])
    RCP_BXS_TOT.columns = ['TUC', 'Qtd_INI', 'Qtd_FIN']
    RCP_BXS_TOT['Qtd_BXS'] = RCP_BXS_TOT['Qtd_FIN'] - RCP_BXS_TOT['Qtd_INI']
    RCP_BXS_TOT = RCP_BXS_TOT[['TUC', 'Qtd_BXS']]

    RCP_BB = RCP_PPBB.merge(RCP_PCBB, how = 'outer', on ='Id_SEQ_PP', suffixes=("_PPBB","_PCBB"), indicator=True, validate="1:1")
    RCP_BB['OBS_LAUDO_BLINDADO'] = np.where(RCP_BB['_merge']=='left_only',
                                                        f'Somente PPBB',
                                                        np.where(RCP_BB['_merge']=='right_only',
                                                        f'Somente PCBB',
                                                        'AMBOS'
                                                        )
                                                        )
    RCP_BB = RCP_BB.drop(columns=['_merge'])

    crit_div = RCP_BB["FLG_ELIG_PPBB"].fillna("B") != RCP_BB["FLG_ELIG_PCBB"].fillna("B")                    
    RCP_BB.loc[crit_div, "OBS_LAUDO_BLINDADO"] += (" | CRÍTICA: mudou eligibilidade")
    crit_div = RCP_BB["Cd_CONC_PPBB"].fillna("B") != RCP_BB["Cd_CONC_PCBB"].fillna("B")                    
    RCP_BB.loc[crit_div, "OBS_LAUDO_BLINDADO"] += (" | CRÍTICA: mudou conciliação")
    RCP_BB.to_csv(f'{dir_arq_base}/BDGD_ANLS/CRITICA_BASE_BLINDADA.csv', sep="|", index=False, encoding="latin-1", decimal=",")
    crit1 = ((RCP_BB['Cd_UAR'] != 'UAR') & 
             (~RCP_BB['Nr_TI'].isin(list(FILTRO_TI))) & 
             (RCP_BB['FLG_ELIG_PCBB'].astype(str)=='1') & 
             (RCP_BB['Cd_CONC_PCBB'].astype(str).isin(['1','3'])))
    RCP_BB = RCP_BB[crit1]
    RCP_BB_TOT = filtrar_df(RCP_BB, ['Nr_TUC'], 'Nr_A1', ['Qtd_AIS','Qtd_AISa'])

    RCP_BB_TOT['Qtd_AIS_BX_BB'] = RCP_BB_TOT['Qtd_AIS'] - RCP_BB_TOT['Qtd_AISa']
    RCP_BB_TOT = RCP_BB_TOT.drop(columns=['Qtd_AIS'])
    RCP_BB_TOT.columns = ['TUC', 'Qtd_BB', 'Qtd_AIS_BX_BB']

    RCP_BDGD_AT_TOT['TUC'] = RCP_BDGD_AT_TOT['TUC'].astype(str)
    RCP_BDGD_ANT_TOT['TUC'] = RCP_BDGD_ANT_TOT['TUC'].astype(str)

    def fnc_agr_RCP(df1 = pd.DataFrame(), df2 = pd.DataFrame(), nm_01 = "", nm_02 = ""):
        RCP_TOT = df1.merge(df2, how = 'outer', on = 'TUC', indicator=True)
        nm_pdr = f"OBS_SFF_CONC_{nm_01}_vs_{nm_02}".replace(" ","_")
        RCP_TOT[nm_pdr] = np.where(RCP_TOT['_merge']=='left_only',
                                                    f'Somente {nm_01}',
                                                    np.where(RCP_TOT['_merge']=='right_only',
                                                    f'Somente {nm_02}',
                                                    'NO'
                                                    )
                                                    )
        return RCP_TOT.drop(columns=['_merge'])

    RCP_TOT = fnc_agr_RCP(RCP_BDGD_AT_TOT, RCP_BDGD_ANT_TOT, nm_01 = "BDGD AT", nm_02 = "BDGD ANT")
    RCP_TOT = fnc_agr_RCP(RCP_TOT, RCP_AIS_TOT[RCP_AIS_TOT['TUC'].isin(FILTRO_UC)], nm_01 = "RCP PASSO 01", nm_02 = "AIS")
    RCP_TOT = fnc_agr_RCP(RCP_TOT, RCP_INC_TOT[RCP_INC_TOT['TUC'].isin(FILTRO_UC)], nm_01 = "RCP PASSO 02", nm_02 = "INCR")
    RCP_TOT = fnc_agr_RCP(RCP_TOT, RCP_BXS_TOT[RCP_BXS_TOT['TUC'].isin(FILTRO_UC)], nm_01 = "RCP PASSO 03", nm_02 = "BAIXAS")
    RCP_TOT = fnc_agr_RCP(RCP_TOT, RCP_BB_TOT[RCP_BB_TOT['TUC'].isin(FILTRO_UC)], nm_01 = "RCP PASSO 04", nm_02 = "BLINDADA")
    RCP_TOT['OBS_SFF'] = ''
    RCP_TOT = RCP_TOT[['TUC', 'Qtd_BDGD_AT', 'Qtd_BDGD_ANT', 'Qtd_AIS', 'Qtd_INC', 'Qtd_BXS', 'Qtd_BB', 
                       'Qtd_AIS_BX_BB', 'OBS_SFF', 'OBS_SFF_CONC_BDGD_AT_vs_BDGD_ANT', 'OBS_SFF_CONC_RCP_PASSO_01_vs_AIS', 
                       'OBS_SFF_CONC_RCP_PASSO_02_vs_INCR', 'OBS_SFF_CONC_RCP_PASSO_03_vs_BAIXAS', 
                       'OBS_SFF_CONC_RCP_PASSO_04_vs_BLINDADA']]
    
    etapas = [
                ("BDGD AT", "BDGD ANT"),
                ("RCP PASSO 01", "AIS"),
                ("RCP PASSO 02", "INCR"),
                ("RCP PASSO 03", "BAIXAS"),
                ("RCP PASSO 04", "BLINDADA")
            ]
    lst_COLS = []
    for nm in RCP_TOT.columns:
        if nm[:3].upper() == 'QTD':
            RCP_TOT[nm] = RCP_TOT[nm].fillna(0)
        if nm[:3].upper() == 'OBS':
            RCP_TOT[nm] = RCP_TOT[nm].fillna("INEXISTE")
            lst_COLS.append(nm)

    for i, (nm_df1, nm_df2) in enumerate(etapas):

        nm_col = (f"OBS_SFF_CONC_{nm_df1}_vs_{nm_df2}".replace(" ", "_"))
        status = RCP_TOT[nm_col].fillna("INEXISTE")

        if i == 0:
            mensagens = np.select(
                                    [
                                        status.eq("NO"),
                                        status.eq(f"Somente {nm_df1}"),
                                        status.eq(f"Somente {nm_df2}"),
                                        status.eq("INEXISTE")
                                    ],
                                    [
                                        "BDGD: presente em ambas",
                                        "BDGD: apenas em BDGD AT",
                                        "BDGD: apenas em BDGD ANT",
                                        "BDGD: ausente em ambas"
                                    ],
                                    default="BDGD: situação não identificada"
                                )

        else:
            mensagens = np.select(
                                    [
                                        status.eq("NO"),
                                        status.eq(f"Somente {nm_df1}"),
                                        status.eq(f"Somente {nm_df2}"),
                                        status.eq("INEXISTE")
                                    ],
                                    [
                                        f"Base {nm_df2}: presente no acumulado e na base",
                                        f"Base {nm_df2}: ausente na base",
                                        f"Base {nm_df2}: incluída pela base",
                                        f"Base {nm_df2}: ausente em ambos"
                                    ],
                                    default=f"{nm_df2}: situação não identificada"
                                )

        separador = "" if i == 0 else " | "
        RCP_TOT["OBS_SFF"] += (separador + pd.Series(mensagens, index=RCP_TOT.index))
        RCP_TOT = RCP_TOT.drop(columns=[nm_col])

    crit_div = ~np.isclose(RCP_TOT["Qtd_BXS"].abs(), RCP_TOT["Qtd_AIS_BX_BB"].abs(), atol = 0.01)
    diferenca = (RCP_TOT["Qtd_BXS"].abs() - RCP_TOT["Qtd_AIS_BX_BB"].abs())
    msg = pd.Series(
                        np.select(
                            [
                                diferenca > 0,
                                diferenca < 0
                            ],
                            [
                                "(arquivo de Baixas superior ao movimentado no laudo)",
                                "(arquivo de Baixas inferior ao movimentado no laudo)"
                            ],
                            default=""
                        ),
                        index=RCP_TOT.index
                    )
    RCP_TOT.loc[crit_div, "OBS_SFF"] += (" | CRÍTICA: Divergência quantitativa entre "
                                            "BAIXAS e AIS_BX_BB. "
                                            "Qtd. BAIXAS: "
                                            + RCP_TOT.loc[crit_div, "Qtd_BXS"].map("{:g}".format)
                                            + "; Qtd. AIS_BX_BB: "
                                            + RCP_TOT.loc[crit_div, "Qtd_AIS_BX_BB"].map("{:g}".format)
                                            + "; Diferença: "
                                            + diferenca.loc[crit_div].map("{:+g}".format)
                                            + " "
                                            + msg.loc[crit_div]
                                            + "."
                                        )

    RCP_TOT['BDGD_PREV'] = (RCP_TOT['Qtd_BDGD_ANT'].abs() + RCP_TOT['Qtd_INC'].abs() - RCP_TOT['Qtd_BXS'].abs()).fillna(0)
    RCP_TOT['Qtd_LAUDO'] = (RCP_TOT['Qtd_INC'].abs() + RCP_TOT['Qtd_BB'].abs()).fillna(0)
    RCP_TOT['DT_BDGD_AT_MUT'] = ((RCP_TOT['BDGD_PREV'].abs() - RCP_TOT['Qtd_BDGD_AT'].abs()) / RCP_TOT['Qtd_BDGD_AT'].abs()).fillna(0)
    RCP_TOT['DT_BDGD_AT_AIS'] = ((RCP_TOT['Qtd_AIS'].abs() - RCP_TOT['Qtd_BDGD_AT'].abs()) / RCP_TOT['Qtd_BDGD_AT'].abs()).fillna(0)
    RCP_TOT['DT_BDGD_AT_LAUDO'] = ((RCP_TOT['Qtd_INC'].abs() + RCP_TOT['Qtd_BB'].abs() - RCP_TOT['Qtd_BDGD_AT'].abs()) / RCP_TOT['Qtd_BDGD_AT'].abs()).fillna(0)

    RCP_TOT.to_sql(f'RCP_TOT', con, if_exists='replace', index=False)
    RCP_TOT.to_csv(f'{dir_arq_base}/BDGD_ANLS/RCP_TOT.csv', sep="|", index=False, encoding="latin-1", decimal=",")
    now = datetime.now() 
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}/BDGD_ANLS/RCP_TOT.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        avl.success(f"  Hora de fim, consolidação de RCP: {now.strftime('%H:%M:%S')}") 
    
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def plt_grafico(diretorio, con, st=None):
    sSQL = """
            SELECT * FROM RCP_TOT WHERE TUC > 0 AND TUC <> ''

           """
    RCP_TOT = pd.read_sql(sSQL, con)
    if len(RCP_TOT)>0:
        # Preparando os dados
        LST_CAT = RCP_TOT['TUC'].drop_duplicates().to_list()
        RCP_TOT['DT_BDGD_AT_MUTp'] = RCP_TOT['DT_BDGD_AT_MUT'] * 100
        RCP_TOT['DT_BDGD_AT_AISp'] = RCP_TOT['DT_BDGD_AT_AIS'] * 100

        # Criando o gráfico
        fig, ax = plt.subplots(figsize=(12, 4))

        # Adicionando linhas horizontais e regiões de referência
        limite_superior = 5
        limite_inferior = -5
        ax.axhspan(limite_inferior, limite_superior, color='green', alpha=0.1, label='Região com Valores Aceitáveis')

        # Adicionando as barras
        ax.bar(LST_CAT, RCP_TOT['DT_BDGD_AT_MUTp'], label='Teste Mutação', alpha=0.5, width=0.4, color='#e74c3c')
        ax.bar(LST_CAT, RCP_TOT['DT_BDGD_AT_AISp'], label='Teste AIS', alpha=0.5, width=0.4, color='#9b59b6')

        # Adicionando rótulos e título
        ax.set_xlabel('UC', fontname='Calibri', fontsize=10)
        ax.set_ylabel('VAR (%)', fontname='Calibri', fontsize=10)
        ax.set_title('Gráfico de variação por UC para a base completa', fontname='Calibri', fontsize=12)
        ax.set_xticks(range(len(LST_CAT)))
        ax.set_xticklabels(LST_CAT, rotation=90, fontname='Calibri', fontsize=9)
        ax.tick_params(axis='y', labelsize=9)

        # Adicionando linhas de grid e legenda
        ax.grid(True)
        ax.legend(prop={'family': 'Calibri', 'size': 10})

        # Exibindo o gráfico no Streamlit
        if st:
            st.pyplot(fig)
        temp_arq = f"{diretorio}/IMAGENS/TST_MUTACAO_BDGD.png"
        plt.savefig(temp_arq, dpi = 500)    
        plt.close(fig)
        return "OK"
    else:
        return None
    
@monitor_completo(st.session_state.LOGGER)
def reconcilia_dfs(df_esq: pd.DataFrame, 
                   df_dir: pd.DataFrame, st=None,
                   col_data: str = "DATA", suf_esq: str = "_BDGD", suf_dir: str = "_AIS") -> pd.DataFrame:


    left  = df_esq.copy()
    right = df_dir.copy()
    


    #a partir da segunda etapa de conciliação a cardinalidade pode ser diferente de 1:1, desse modo
    #vamos incluir uma etapa de consolidação, para evitarmos isso. Nesse sentido, vamos fazer um
    #reagrupamento a cada fase de conciliação.
    etapas = [
        (["ODI","TI","TUC","A1","A2","A3","A4","A5","A6", col_data], False),
        (["ODI","TI","TUC","A1","A2","A3","A4","A5","A6","ANO"], True),
        (["ODI","TI","TUC","A1","A2","A3","A4","A5","A6"], False),
        (["ODI","TUC","A1","A2","A3","A4","A5","A6"], False),
        (["TUC","A1","A2","A3","A4","A5","A6"], False),
        (["TUC"], False)              
    ]

    conciliados = []
    etapa_num = 1

    colunas = ["Nr_Etapa", "Qtd_CONC", "Qtd_CONC_OK", "Qtd_CONC_DIV", f"Qtd_AUS{suf_dir}", f"Qtd_AUS{suf_esq}"]
    df_REL = pd.DataFrame(columns=colunas)

    for chaves, usa_ano in etapas:

        if usa_ano:
            left["ANO"]  = pd.to_datetime(left[col_data]).dt.year
            right["ANO"] = pd.to_datetime(right[col_data]).dt.year
            
        left_ini = left[chaves + ['Qtd']]
        right_ini = right[chaves + ['Qtd']]
        if etapa_num != 1:
            left_ini = left_ini.groupby(chaves, dropna=False)['Qtd'].sum().reset_index()
            right_ini = right_ini.groupby(chaves, dropna=False)['Qtd'].sum().reset_index()
        
        merged = left_ini.merge(
                                    right_ini,
                                    on = chaves,
                                    how = "inner",
                                    suffixes = (suf_esq, suf_dir),
                                    indicator = False
                                )

        if not merged.empty:
            merged["etapa_conciliacao"] = etapa_num

            left  = left_ini.merge(merged[chaves], on=chaves, how="left", indicator=True)
            left  = left [left ["_merge"] == "left_only"].drop(columns="_merge")

            right = right_ini.merge(merged[chaves], on=chaves, how="left", indicator=True)
            right = right[right["_merge"] == "left_only"].drop(columns="_merge")

            criterio = merged[f'Qtd{suf_esq}'] == merged[f'Qtd{suf_dir}']
            criterio1 = merged[f'Qtd{suf_esq}'] != merged[f'Qtd{suf_dir}']

            dados = {
                        "Nr_Etapa": etapa_num,
                        "Qtd_CONC": len(merged),
                        "Qtd_CONC_OK": criterio.sum(),
                        "Qtd_CONC_DIV": criterio1.sum(),
                        f"Qtd_AUS{suf_esq}": len(left),
                        f"Qtd_AUS{suf_dir}": len(right)
                    }
            df_REL = pd.concat([df_REL, pd.DataFrame([dados])], ignore_index=True)

            df_PROV = merged.copy()
            df_PROV['DELTA'] = df_PROV[f'Qtd{suf_esq}'] - df_PROV[f'Qtd{suf_dir}']
            df_PROV.loc[df_PROV['DELTA']<0, f'Qtd{suf_dir}'] = df_PROV.loc[df_PROV['DELTA']<0, f'Qtd{suf_esq}']
            df_PROV.loc[df_PROV['DELTA']>0, f'Qtd{suf_esq}'] = df_PROV.loc[df_PROV['DELTA']>0, f'Qtd{suf_dir}']


            df_PROV_ESQ = df_PROV[df_PROV['DELTA']>0][chaves + ['DELTA']].rename(columns={'DELTA' : 'Qtd'})
            df_PROV_DIR = df_PROV[df_PROV['DELTA']<0][chaves + ['DELTA']].rename(columns={'DELTA' : 'Qtd'})

            df_PROV = df_PROV[chaves + [f'Qtd{suf_esq}',f'Qtd{suf_dir}','etapa_conciliacao']]
            df_PROV_DIR['Qtd'] = df_PROV_DIR['Qtd'].astype(float).abs()
            
            merged = df_PROV.copy()
            left = pd.concat([left,df_PROV_ESQ], ignore_index=True)
            right = pd.concat([right,df_PROV_DIR], ignore_index=True)

            conciliados.append(merged)

        etapa_num += 1

        if left.empty or right.empty:
            break

    if len(conciliados) == 0:
        return pd.DataFrame(), left, right, df_REL 
    
    df_conciliado = pd.concat(conciliados, ignore_index=True)
    for col in ["ODI","TI","TUC","A1","A2","A3","A4","A5","A6","DATA"]:
        if col not in df_conciliado:
            etapas[0][0].remove(col)
    df_conciliado.sort_values(["etapa_conciliacao"] + etapas[0][0], inplace=True)

    df_REL['TOT_CONC'] = df_REL['Qtd_CONC'].cumsum()
    df_REL['TOT_REG'] = df_REL['TOT_CONC'] + df_REL[f'Qtd_AUS{suf_esq}'] + df_REL[f'Qtd_AUS{suf_dir}']
    df_REL['Pct_CONC'] = (df_REL['TOT_CONC'] - df_REL['Qtd_CONC_DIV']) / df_REL['TOT_REG']
    return df_conciliado, left, right, df_REL 

@monitor_completo(st.session_state.LOGGER)    
def anl_incr_rcp(dir_entrada, con, Empresa, INI_INC, FIM_INC, st=None, FLG_INCR=True):
    LST_DF = ['df_EQCR_AT', 'df_EQRE_AT', 'df_EQSE_AT', 'df_MED_AT', 'df_TRM_AT', 'df_TRD_AT', 'df_TRSE_AT']
    LST_CLN = ['ODI', 'TI', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'Qtd', 'DAT_IMO']

    RCP_INC = pd.DataFrame()
    LST_TI = [(x) for x in range(69, 93)] + [94, 95, 97, 99]
    FILTRO_TI = f"{LST_TI}".replace("[","(").replace("]",")")
    FILTRO_UC = "(125, 130, 160, 210, 295, 330, 340, 345, 545, 565, 570, 575)"
    lst_TUCagem = ['TI', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'Qtd']

    for nm in LST_DF:
        if not os.path.exists(f"{dir_entrada}/BDGD_ANLS/{nm}.feather"):
            continue
        try:
            df = pd.read_feather(f"{dir_entrada}/BDGD_ANLS/{nm}.feather", columns=LST_CLN)
        except Exception as e:
            df = pd.read_feather(f"{dir_entrada}/BDGD_ANLS/{nm}.feather")
            if len(df)==0:
                st.warning(f"Não há registros para {nm}!")
                continue
            st.write(df)
            raise UserWarning(f"Avalie a estrutura do arquivo {nm}: {e}.")
        df['DAT_IMO'] = pd.to_datetime(df['DAT_IMO'], format = "%d/%m/%Y",  errors ='coerce').dt.date
        for n in lst_TUCagem:
            df[n] = pd.to_numeric(df[n], errors = 'coerce') if len(df) > 0 else None

        if FLG_INCR:
            try:
                df = df[(df['DAT_IMO'] >= INI_INC) & (df['DAT_IMO'] <= FIM_INC) & (~df['TI'].isin(LST_TI))].reset_index()
            except:
                df = df[(df['DAT_IMO'] >= pd.to_datetime(INI_INC,format="%Y-%m-%d")) & (df['DAT_IMO'] <= pd.to_datetime(FIM_INC,format="%Y-%m-%d")) & (~df['TI'].isin(LST_TI))].reset_index()
        
        df = df.groupby(['ODI', 'TI', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'DAT_IMO'], dropna=False)['Qtd'].sum().reset_index()
        RCP_INC = pd.concat([RCP_INC, df], ignore_index=True)

    RCP_INC.columns = ['ODI_BDGD', 'TI_BDGD', 'TUC_BDGD', 'A1_BDGD', 'A2_BDGD', 'A3_BDGD',
                   'A4_BDGD', 'A5_BDGD', 'A6_BDGD', 'DAT_IMO_BDGD', 'Qtd_BDGD']

    dt_ARQ = max_arq("AIS", con, Empresa)
    if dt_ARQ:
        df1 = pd.read_sql(f"""SELECT MAX(date(Dt_Imob)) AS DT FROM  AIS t1
                WHERE t1.dt_ARQ = {dt_ARQ}
                AND t1.FLG_PER  = '1'""", con)
        ano_corrente = pd.to_datetime(df1['DT']).dt.year.iloc[-1]
        data_corte = f"{ano_corrente}-01-01"
        nm_BASE = Path(dir_entrada) / "BDGD_AT" / "BASE.dbf"
        if nm_BASE.exists():
            try:
                dbf = DBF(nm_BASE)
                df_ano = pd.DataFrame(iter(dbf))
            except:
                dbf = DBF(nm_BASE, encoding='utf-8')
                df_ano = pd.DataFrame(iter(dbf))
            data_corte = pd.to_datetime(df_ano['DAT_EXT'], format="%d/%m/%Y").dt.strftime("%Y-%m-%d").iloc[-1]
            
    if FLG_INCR:
        dt_ARQ = max_arq("INCR", con, Empresa)
        if dt_ARQ and (st.session_state.dt_fim < date.today()):
            SQLq = f"""
                SELECT Cd_ODI, Cd_UAR, Nr_TI, Nr_TUC, Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5,
                Nr_A6, CAST(Qtd_AIS AS REAL) AS Qtd_AIS, FLG_ELIG, Cd_CONC
                FROM INCR t1 WHERE t1.dt_ARQ = {dt_ARQ} AND (t1.FLG_ELIG = '1' AND t1.Cd_CONC IN ('1','3'))
                AND t1.Nr_TI not in {FILTRO_TI} AND t1.Cd_UAR <> 'UAR' AND Nr_TUC in {FILTRO_UC}
                
                """
            RCP_INClaudo = pd.read_sql(SQLq, con)
            lst_TUCagem = ['Nr_TI', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6', 'Qtd_AIS']
            for n in lst_TUCagem:
                if (RCP_INClaudo[n].dtype == 'object'):
                    RCP_INClaudo[n] = pd.to_numeric(RCP_INClaudo[n].str.replace(",","."), errors='coerce')
        else:
            if st.session_state.dt_fim >= date.today():
                #avl.warning(f"  Buscando alternativa para INCR, período intercalar de análise. Início em: {now.strftime('%H:%M:%S')}")
                dt_ARQ = max_arq("AIS", con, Empresa)
                if dt_ARQ:                
                    SQLq = f"""
                            SELECT Cd_ODI, Cd_UAR, Nr_TI, Nr_TUC, Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5,
                            Nr_A6, Qtd_AIS, "1" AS FLG_ELIG, "1" AS Cd_CONC
                            FROM AIS t1
                            WHERE t1.dt_ARQ = {dt_ARQ}
                            AND t1.FLG_PER  = "1"
                            AND t1.Nr_TI not in {FILTRO_TI} AND t1.Cd_UAR <> 'UAR' AND Nr_TUC in {FILTRO_UC}
                            AND date(Dt_Imob) < ?
                            """
                    RCP_INClaudo = pd.read_sql(SQLq, con, params=(data_corte,))
                    
                    SQLq = f"""
                            SELECT Cd_ODI, Cd_UAR, Nr_TI, Nr_TUC, Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5,
                            Nr_A6, (Qtd_INI-Qtd_FIN) AS Qtd_AIS, "1" AS FLG_ELIG, "1" AS Cd_CONC
                            FROM BAIXAS t1
                            WHERE t1.dt_ARQ = {dt_ARQ}
                            AND t1.Nr_TI not in {FILTRO_TI} AND t1.Cd_UAR <> 'UAR' AND Nr_TUC in {FILTRO_UC}
                            AND date(Dt_Imob) < ?  AND date(Dt_Imob) >= ? AND date(Dt_BX) < ?
                            """
                    RCP_BAIXAS = pd.read_sql(SQLq, con, params=(data_corte, INI_INC, data_corte))
                    RCP_INClaudo = pd.concat([RCP_INClaudo, RCP_BAIXAS], ignore_index=True)

                    if (RCP_INClaudo['Qtd_AIS'].dtype == 'object'):
                        RCP_INClaudo['Qtd_AIS'] = pd.to_numeric(RCP_INClaudo['Qtd_AIS'].str.replace(",","."), errors='coerce')

                elif st:
                    st.error('Falha ao importar o arquivo INCR da base local.')
                    return None
            else:
                raise UserWarning('Falha ao importar o arquivo INCR da base local.')
            
    dt_ARQ = max_arq("AIS", con, Empresa)
    if FLG_INCR:
        
        if dt_ARQ:
            SQLq = f"""
                SELECT Cd_ODI, Cd_UAR, Nr_TI, Nr_TUC, coalesce(Nr_A1,0) as Nr_A1, coalesce(Nr_A2,0) as Nr_A2, coalesce(Nr_A3,0) as Nr_A3, 
                coalesce(Nr_A4,0) as Nr_A4, coalesce(Nr_A5,0) as Nr_A5,
                coalesce(Nr_A6,0) as Nr_A6, CAST(Qtd_AIS AS REAL) AS Qtd_AIS, Dt_Imob
                FROM AIS t1 WHERE t1.dt_ARQ = {dt_ARQ}
                AND t1.Nr_TI not in {FILTRO_TI} AND t1.Cd_UAR <> 'UAR' AND t1.FLG_PER = '1'
                AND Nr_TUC in {FILTRO_UC}
                """    
    elif dt_ARQ:
            SQLq = f"""
                SELECT Cd_ODI, Cd_UAR, Nr_TI, Nr_TUC, coalesce(Nr_A1,0) as Nr_A1, coalesce(Nr_A2,0) as Nr_A2, coalesce(Nr_A3,0) as Nr_A3, 
                coalesce(Nr_A4,0) as Nr_A4, coalesce(Nr_A5,0) as Nr_A5,
                coalesce(Nr_A6,0) as Nr_A6, CAST(Qtd_AIS AS REAL) AS Qtd_AIS, Dt_Imob
                FROM AIS t1 WHERE t1.dt_ARQ = {dt_ARQ}
                AND t1.Nr_TI not in {FILTRO_TI} AND t1.Cd_UAR <> 'UAR'
                AND Nr_TUC in {FILTRO_UC}
                """

    if dt_ARQ:
        if st.session_state.dt_fim >= date.today():
            SQLq += f"""
                    AND date(Dt_Imob) < ?
                    """
            RCP_AIS = pd.read_sql(SQLq, con, params = (data_corte,))
        else:
            RCP_AIS = pd.read_sql(SQLq, con)

        RCP_AIS = RCP_AIS.groupby(['Cd_ODI', 'Nr_TI', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5',
                                       'Nr_A6', 'Dt_Imob'])['Qtd_AIS'].sum().reset_index()
        
        lst_TUCagem = ['Nr_TI', 'Nr_TUC', 'Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6', 'Qtd_AIS']
        for n in lst_TUCagem:
            if (RCP_AIS[n].dtype == 'object'):
                RCP_AIS[n] = pd.to_numeric(RCP_AIS[n], errors = 'coerce') if len(RCP_AIS) > 0 else None
        RCP_AIS.columns = ['ODI_AIS', 'TI_AIS', 'TUC_AIS', 'A1_AIS', 'A2_AIS', 'A3_AIS',
                            'A4_AIS', 'A5_AIS', 'A6_AIS', 'DAT_IMO_AIS', 'Qtd_AIS']
        RCP_AIS['DAT_IMO_AIS'] = pd.to_datetime(RCP_AIS['DAT_IMO_AIS'], errors='coerce').dt.date
    else:
        if st:
            st.error('Falha ao importar o arquivo AIS da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS da base local.')
        

    RCP_AIS['ODI_AIS'] = RCP_AIS['ODI_AIS'].apply(str)

    df_AIS = RCP_AIS.groupby(['ODI_AIS', 'TI_AIS', 'TUC_AIS', 'A1_AIS', 'A2_AIS', 'A3_AIS', 'A4_AIS', 'A5_AIS', 'A6_AIS', 'DAT_IMO_AIS'])[['Qtd_AIS']].sum().reset_index()
    df_INC = RCP_INC.groupby(['ODI_BDGD', 'TI_BDGD', 'TUC_BDGD', 'A1_BDGD', 'A2_BDGD', 'A3_BDGD', 'A4_BDGD', 'A5_BDGD', 'A6_BDGD', 'DAT_IMO_BDGD'])[['Qtd_BDGD']].sum().reset_index()

    RCP_TOT_ESQ = df_INC.merge(df_AIS, how = 'left', left_on = ['ODI_BDGD', 'TI_BDGD', 'TUC_BDGD', 'A1_BDGD', 'A2_BDGD', 'A3_BDGD', 'A4_BDGD', 'A5_BDGD', 'A6_BDGD', 'DAT_IMO_BDGD'], right_on = ['ODI_AIS', 'TI_AIS', 'TUC_AIS', 'A1_AIS', 'A2_AIS', 'A3_AIS', 'A4_AIS', 'A5_AIS', 'A6_AIS', 'DAT_IMO_AIS'])
    RCP_TOT_DIR = df_INC.merge(df_AIS, how = 'right', left_on = ['ODI_BDGD', 'TI_BDGD', 'TUC_BDGD', 'A1_BDGD', 'A2_BDGD', 'A3_BDGD', 'A4_BDGD', 'A5_BDGD', 'A6_BDGD', 'DAT_IMO_BDGD'], right_on = ['ODI_AIS', 'TI_AIS', 'TUC_AIS', 'A1_AIS', 'A2_AIS', 'A3_AIS', 'A4_AIS', 'A5_AIS', 'A6_AIS', 'DAT_IMO_AIS'])
    col_nm = ['ODI_BDGD', 'TI_BDGD', 'TUC_BDGD', 'A1_BDGD', 'A2_BDGD', 'A3_BDGD', 'A4_BDGD', 'A5_BDGD', 'A6_BDGD', 'DAT_IMO_BDGD',
            'Qtd_BDGD', 'ODI_AIS', 'TI_AIS', 'TUC_AIS', 'A1_AIS', 'A2_AIS', 'A3_AIS', 'A4_AIS', 'A5_AIS', 'A6_AIS', 
            'DAT_IMO_AIS', 'Qtd_AIS']
    RCP_TOT_AUS = RCP_TOT_ESQ.merge(RCP_TOT_DIR, how = 'outer', on = col_nm)
    RCP_TOT_CNC = RCP_TOT_ESQ.merge(RCP_TOT_DIR, how = 'inner', on = col_nm)
    RCP_TOT = pd.concat([RCP_TOT_AUS[(RCP_TOT_AUS['ODI_BDGD'].isnull()) | (RCP_TOT_AUS['ODI_AIS'].isnull())], RCP_TOT_CNC])
    RCP_TOT = RCP_TOT.fillna("NC")

    df_BDGDesq = RCP_TOT[RCP_TOT['ODI_BDGD'] != 'NC'][['ODI_BDGD','TI_BDGD','TUC_BDGD','A1_BDGD','A2_BDGD','A3_BDGD',
                       'A4_BDGD','A5_BDGD','A6_BDGD','DAT_IMO_BDGD','Qtd_BDGD']].rename(columns = {
                       'ODI_BDGD' : 'ODI','TI_BDGD' : 'TI', 'TUC_BDGD' : 'TUC','A1_BDGD' : 'A1',
                       'A2_BDGD': 'A2','A3_BDGD' : 'A3', 'A4_BDGD' : 'A4','A5_BDGD' : 'A5', 
                       'A6_BDGD' : 'A6', 'DAT_IMO_BDGD': 'DATA', 'Qtd_BDGD': 'Qtd'})
    df_AISdir = RCP_TOT[RCP_TOT['ODI_AIS'] != 'NC'][['ODI_AIS','TI_AIS','TUC_AIS','A1_AIS','A2_AIS','A3_AIS',
                       'A4_AIS','A5_AIS','A6_AIS','DAT_IMO_AIS','Qtd_AIS']].rename(columns = {
                       'ODI_AIS' : 'ODI','TI_AIS' : 'TI', 'TUC_AIS' : 'TUC','A1_AIS' : 'A1',
                       'A2_AIS': 'A2','A3_AIS' : 'A3', 'A4_AIS' : 'A4','A5_AIS' : 'A5', 
                       'A6_AIS' : 'A6', 'DAT_IMO_AIS': 'DATA', 'Qtd_AIS': 'Qtd'})
    
    try:
        df_CONC, df_BDGDnc, df_AISnc, df_REL = reconcilia_dfs(df_BDGDesq, df_AISdir, st)
    except Exception as e:
        st.error(f"Falhou: {e}")
        return "Falhou"
    
    if len(df_CONC)==0:
        st.error("Conciliação não executada, verifique arquivo")
        return "Falhou"
    
    if FLG_INCR:
        nm_excel = rf'{dir_entrada}/BDGD_ANLS/REL_CONCILIACAO_INCR.xlsx'
        nm_sql ="_INCR"
    else:
        nm_excel = rf'{dir_entrada}/BDGD_ANLS/REL_CONCILIACAO_CMP.xlsx'
        nm_sql ="_CMP"
    
    df_REL.to_sql(f'REL_RCP_MTnv{nm_sql}', con, if_exists='replace', index=False)
    df_CONC.to_sql(f'REL_RCP_CONC_MTnv{nm_sql}', con, if_exists='replace', index=False)
    df_BDGDnc.to_sql(f'REL_RCP_BDGDnc_MTnv{nm_sql}', con, if_exists='replace', index=False)
    df_AISnc.to_sql(f'REL_RCP_AISnc_MTnv{nm_sql}', con, if_exists='replace', index=False)

    with pd.ExcelWriter(nm_excel, engine='xlsxwriter') as writer:
        df_REL.to_excel(writer, sheet_name="REL_CONC", index=False)
        df_CONC.to_excel(writer, sheet_name="Conciliados", index=False)
        df_BDGDnc.to_excel(writer, sheet_name="Nao_Conciliados_BDGD", index=False)
        df_AISnc.to_excel(writer, sheet_name="Nao_Conciliados_AIS", index=False)

        for sheet_name in ["REL_CONC","Conciliados", "Nao_Conciliados_BDGD", "Nao_Conciliados_AIS"]:
            worksheet = writer.sheets[sheet_name]
            df = {  "REL_CONC": df_REL,
                    "Conciliados": df_CONC, 
                    "Nao_Conciliados_BDGD": df_BDGDnc,
                    "Nao_Conciliados_AIS": df_AISnc}[sheet_name]

            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 2
                worksheet.set_column(i, i, max_len)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = nm_excel,
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
        
    RCP_TOT['TESTE'] = 'OK'
    RCP_TOT.loc[(RCP_TOT['Qtd_BDGD'] != RCP_TOT['Qtd_AIS']), 'TESTE'] = "Qtd DIV"
    RCP_TOT.loc[RCP_TOT['DAT_IMO_BDGD'] == 'NC', 'TESTE'] = "Ausente BDGD"
    RCP_TOT.loc[RCP_TOT['DAT_IMO_AIS'] == 'NC', 'TESTE'] = "Ausente AIS"

    RCP_TOT.to_sql(f'REL_RCP_TOT{nm_sql}', con, if_exists='replace', index=False)
    RCP_TOT.to_csv(f'{dir_entrada}/BDGD_ANLS/REL_RCP_TOT{nm_sql}.csv', sep="|", index=False)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_entrada}/BDGD_ANLS/REL_RCP_TOT{nm_sql}.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)

    RCP_INC['DAT_IMO_BDGD'] = pd.to_datetime(RCP_INC['DAT_IMO_BDGD'], errors ='coerce')
    RCP_AIS['DAT_IMO_AIS'] = pd.to_datetime(RCP_AIS['DAT_IMO_AIS'], errors='coerce')
    RCP_INC['ANO_INC'] = RCP_INC['DAT_IMO_BDGD'].dt.year
    RCP_AIS['ANO_AIS'] = RCP_AIS['DAT_IMO_AIS'].dt.year
    

    df_AIS = RCP_AIS.groupby(['TI_AIS', 'TUC_AIS', 'A1_AIS', 'A2_AIS', 'A3_AIS', 'A4_AIS', 'A5_AIS', 'A6_AIS', 'ANO_AIS'])[['Qtd_AIS']].sum().reset_index()
    df_INC = RCP_INC.groupby(['TI_BDGD', 'TUC_BDGD', 'A1_BDGD', 'A2_BDGD', 'A3_BDGD', 'A4_BDGD', 'A5_BDGD', 'A6_BDGD', 'ANO_INC'])[['Qtd_BDGD']].sum().reset_index()

    merge_cols_left = ['TI_BDGD', 'TUC_BDGD', 'A1_BDGD', 'A2_BDGD', 'A3_BDGD', 'A4_BDGD', 'A5_BDGD', 'A6_BDGD', 'ANO_INC']
    merge_cols_right = ['TI_AIS', 'TUC_AIS', 'A1_AIS', 'A2_AIS', 'A3_AIS', 'A4_AIS', 'A5_AIS', 'A6_AIS', 'ANO_AIS']
    all_cols = merge_cols_left + ['Qtd_BDGD'] + merge_cols_right + ['Qtd_AIS']

    RCP_TOT_ESQ = df_INC.merge(df_AIS, how='left', left_on=merge_cols_left, right_on=merge_cols_right)
    RCP_TOT_DIR = df_INC.merge(df_AIS, how='right', left_on=merge_cols_left, right_on=merge_cols_right)

    RCP_TOT_AUS = RCP_TOT_ESQ.merge(RCP_TOT_DIR, how='outer', on=all_cols)
    RCP_TOT_CNC = RCP_TOT_ESQ.merge(RCP_TOT_DIR, how='inner', on=all_cols)

    RCP_TOT = pd.concat([
                            RCP_TOT_AUS[(RCP_TOT_AUS['TI_BDGD'].isnull()) | (RCP_TOT_AUS['TI_AIS'].isnull())], 
                            RCP_TOT_CNC
                        ]).fillna("NC")
    RCP_TOT['Qtd_BDGD'] = RCP_TOT['Qtd_BDGD'].replace("NC", pd.NA)
    RCP_TOT['Qtd_BDGD'] = RCP_TOT['Qtd_BDGD'].fillna(0)
    RCP_TOT['Qtd_AIS'] = RCP_TOT['Qtd_AIS'].replace("NC", pd.NA)
    RCP_TOT['Qtd_AIS'] = RCP_TOT['Qtd_AIS'].fillna(0)

    RCP_TOT['TESTE'] = "OK"
    RCP_TOT.loc[RCP_TOT['Qtd_BDGD'] != RCP_TOT['Qtd_AIS'], 'TESTE'] = "Qtd DIV"
    RCP_TOT.loc[RCP_TOT['TUC_BDGD'] == 'NC', 'TESTE'] = "Ausente BDGD"
    RCP_TOT.loc[RCP_TOT['TUC_AIS'] == 'NC', 'TESTE'] = "Ausente AIS"
    RCP_TOT.to_csv(f'{dir_entrada}/BDGD_ANLS/REL_RCP_TOT{nm_sql}_ANO.csv', sep="|", index=False)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_entrada}/BDGD_ANLS/REL_RCP_TOT{nm_sql}_ANO.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)

    REL_RCP_CMP = RCP_TOT.groupby(['TESTE'], as_index=False).size().rename(columns={'size': 'QTD_OCOR'})
    RCP_TOT['TUC'] = RCP_TOT['TUC_AIS'].combine_first(RCP_TOT['TUC_BDGD'])

    REL_RCP_CMPa = RCP_TOT.groupby(['TESTE', 'TUC'], dropna=False, as_index=False)[['Qtd_AIS', 'Qtd_BDGD']].sum()

    REL_RCP_CMP.to_sql(f'REL_RCP_TOT_SEM_TI{nm_sql}', con, if_exists='replace', index=False)
    for nm in ['Ausente AIS', 'Ausente BDGD']:
        if len(REL_RCP_CMPa[REL_RCP_CMPa['TESTE'] == nm])>0:
            REL_RCP_CMPa.loc[REL_RCP_CMPa['TESTE'] == nm, nm.replace("Ausente","Qtd")] = 0
    REL_RCP_CMPa = REL_RCP_CMPa.reset_index()
    REL_RCP_CMPa['Qtd_BDGD'] += 0.0001
    REL_RCP_CMPa['Erro'] = (
                            (REL_RCP_CMPa['Qtd_AIS'] - REL_RCP_CMPa['Qtd_BDGD']) / 
                            REL_RCP_CMPa['Qtd_BDGD'].where(REL_RCP_CMPa['Qtd_BDGD'] != 0, REL_RCP_CMPa['Qtd_AIS'])
                            )

    REL_RCP_CMPa.to_sql(f'REL_RCP_TOT_AB_UC{nm_sql}', con, if_exists='replace', index=False)

    RCP_INC = RCP_INC.groupby(['TUC_BDGD'],dropna=False)['Qtd_BDGD'].sum().reset_index()
    RCP_AIS = RCP_AIS.groupby(['TUC_AIS'],dropna=False)['Qtd_AIS'].sum().reset_index()

    RCP_TOT_ESQ = RCP_INC.merge(RCP_AIS, how = 'left', left_on = ['TUC_BDGD'], right_on = ['TUC_AIS'])
    RCP_TOT_DIR = RCP_INC.merge(RCP_AIS, how = 'right', left_on = ['TUC_BDGD'], right_on = ['TUC_AIS'])
    RCP_TOT = pd.concat([RCP_TOT_ESQ, RCP_TOT_DIR]).drop_duplicates()

    if FLG_INCR:
        RCP_laudo = RCP_INClaudo.groupby(['Nr_TUC'],dropna=False)['Qtd_AIS'].sum().reset_index()
        RCP_laudo.columns = ['TUC_INC', 'Qtd_INC']

        if (RCP_laudo['TUC_INC'].dtype == 'object'):
            RCP_laudo['TUC_INC'] = pd.to_numeric(RCP_laudo['TUC_INC'].str.replace(",","."), errors='coerce')

        RCP_TOT_ESQ = RCP_INC.merge(RCP_laudo, how = 'left', left_on = ['TUC_BDGD'], right_on = ['TUC_INC'])
        RCP_TOT_DIR = RCP_INC.merge(RCP_laudo, how = 'right', left_on = ['TUC_BDGD'], right_on = ['TUC_INC'])
        RCP_TOT1 = pd.concat([RCP_TOT_ESQ, RCP_TOT_DIR]).drop_duplicates()

        RCP_TOT = RCP_TOT.merge(RCP_TOT1[RCP_TOT1['TUC_BDGD'].notnull()], how='left', on = ['TUC_BDGD','Qtd_BDGD'])

    RCP_TOT.fillna(0, inplace = True)
    RCP_TOT['DIF_AIS'] = RCP_TOT['Qtd_BDGD'] - RCP_TOT['Qtd_AIS']
    RCP_TOT['PCT_DIF_AIS'] = RCP_TOT['DIF_AIS'] / RCP_TOT['Qtd_BDGD']

    if FLG_INCR:
        RCP_TOT['DIF_LAUDO'] = RCP_TOT['Qtd_BDGD'] - RCP_TOT['Qtd_INC']
        RCP_TOT['PCT_DIF_LAUDO'] = RCP_TOT['DIF_LAUDO'] / RCP_TOT['Qtd_BDGD']

    RCP_TOT.to_sql(f'REL_RCP_BDGD_AIS_UC{nm_sql}', con, if_exists='replace', index=False)
    return "OK"

@monitor_completo(st.session_state.LOGGER)
def vao_medio(dir_saida, Empresa, LOCa = True, VAO_MIN = 0.5, df_SMT = None, st=None, nome= 'REDE', pct=0.1):
        if not st:
            return None
        if LOCa:
            LOC = 'UB'
        else:
            LOC = 'NU'

        st.markdown(f"""<h2 style="text-align: center;font-size: 30px;">
                    Análise do Vão Mínimo, {nome} {LOC}, OUTLIERS (<{f"{VAO_MIN:,.2f}".replace(".",",")}m e >200m.)</h2>
                    """,  
                    unsafe_allow_html=True)

        df = df_SMT[(df_SMT['COMP'] <= 200) & (df_SMT['COMP'] > VAO_MIN) & (df_SMT['ARE_LOC'] == LOC)]
        valor_05pct = df['COMP'].quantile(0.05)
        df1 = df_SMT[(df_SMT['COMP'] <= valor_05pct) & (df_SMT['COMP'] > VAO_MIN) & (df_SMT['ARE_LOC'] == LOC)]
        valor_025pct = df['COMP'].quantile(pct/100)

        comp = pd.to_numeric(df["COMP"], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        comp = comp[comp > 0].to_numpy(dtype=float)
        if len(comp) < 30:
            raise ValueError("A amostra deve conter pelo menos 30 comprimentos válidos.")
        percentis = np.arange(0.5, 5.01, 0.10)
        comprimentos = np.percentile(comp, percentis)

        resultado = pd.DataFrame({"Percentil": percentis, "Comprimento_m": comprimentos})
        delta = resultado['Percentil'].iloc[1] - resultado['Percentil'].iloc[0]
        janela = 9 
        grau = 3
        margem = janela // 2
        idx_util = slice(margem, -margem)

        def analisar_cauda_percentis(amostra_comp: np.ndarray):
            q = np.percentile(amostra_comp, percentis)
            q_s = savgol_filter(q, window_length=janela, polyorder=grau)
            d1 = savgol_filter(q, window_length=janela, polyorder=grau, deriv=1, delta=delta)
            d2 = savgol_filter(q, window_length=janela, polyorder=grau, deriv=2, delta=delta)

            amp_q = max(np.ptp(q), 1e-9)
            amp_p = np.ptp(percentis)
            d1_norm = d1 * (amp_p / amp_q)
            d2_norm = d2 * ((amp_p ** 2) / amp_q)
            curvatura = np.abs(d2_norm) / np.power(1.0 + d1_norm ** 2, 1.5)

            p_int = percentis[idx_util]
            q_int = q[idx_util]
            d1_int = d1[idx_util]
            curv_int = curvatura[idx_util]
            d2_int = d2[idx_util]

            cv_d1 = np.std(d1_int) / (np.mean(np.abs(d1_int)) + 1e-9)
            prom_min = max(np.ptp(d1_int) * 0.12, 1e-6)
            modas_idx, _ = find_peaks(-d1_int,prominence=prom_min,distance=3)

            if cv_d1 < 0.18:
                tipo_dist = "Uniforme"
            elif len(modas_idx) >= 2:
                tipo_dist = "Multimodal"
            elif len(modas_idx) == 1:
                tipo_dist = "Unimodal"
            else:
                tipo_dist = "Sem moda interna"

            prom_curv = max(np.ptp(curv_int) * 0.20, 1e-10)
            transicoes_idx, propriedades = find_peaks(curv_int,prominence=prom_min,distance=3)

            if len(transicoes_idx) > 0:
                idx_transicao = int(transicoes_idx[0])
                p_escolhido = float(p_int[idx_transicao])
                comp_escolhido = float(q_int[idx_transicao])
            else:
                idx_p1 = int(np.argmin(np.abs(p_int - 1.0)))
                p_escolhido = float(p_int[idx_p1])
                comp_escolhido = float(q_int[idx_p1])

            return {
                        "q": q, "q_suave": q_s, "d1": d1, "d2": d2, "curvatura": curvatura,
                        "tipo": tipo_dist, "p_otimo": p_escolhido, "comp_otimo": comp_escolhido
                    }

        analise_base = analisar_cauda_percentis(comp)
        comprimentos = analise_base["q"]
        q_suave = analise_base["q_suave"]
        d1 = analise_base["d1"]
        d2 = analise_base["d2"]
        curvatura = analise_base["curvatura"]

        resultado = pd.DataFrame({
                                    "Percentil": percentis,
                                    "Comprimento_m": comprimentos,
                                    "Q_suave": q_suave,
                                    "Derivada_1": d1,
                                    "Derivada_2": d2,
                                    "Curvatura": curvatura,
                                }).iloc[idx_util].reset_index(drop=True)

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].hist(comp, bins='auto', color='blue', density=True)
        axes[0].set_title('Distribuição para comprimento')
        axes[0].set_xlabel('Comprimento (m)')
        axes[0].set_ylabel('Densidade')
        axes[0].axvline(comp.min(), color='black', linestyle='dashed', label='MIN: {:.1f}'.format(comp.min()))
        axes[0].axvline(comp.max(), color='black', linestyle='dashed', label='MAX: {:.1f}'.format(comp.max()))
        axes[0].axvline(np.median(comp), color='black', linestyle='dashed', label='MEDIANA: {:.1f}'.format(np.median(comp)))
        axes[0].legend()

        axes[1].hist(comp, bins='auto', cumulative=True, color='blue', density=True)
        axes[1].set_title('Distribuição cumulativa comprimento')
        axes[1].set_xlabel('Comprimento (m)')
        axes[1].set_ylabel('Probabilidade')

        if nome == "RAMAL":
            valor_025pct = max(valor_025pct, 2)
        else:
            valor_025pct = max(valor_025pct, 5)

        txt_ax = f"{pct/100:.2%}".replace(".",",")
        axes[1].axvline(valor_025pct, color='green', linestyle='dashed', 
                label=f'{txt_ax} de {nome} ≤ {valor_025pct:.2f} m')
        axes[1].legend()

        stats.probplot(comp, dist="norm", plot=axes[2])
        axes[2].set_title('Distribuição normal de probabilidade para comprimento')
        axes[2].set_xlabel('Quantis teóricos')
        axes[2].set_ylabel('Quantis observados')

        plt.tight_layout()
        temp_arq = rf"{dir_saida}/IMAGENS/VAO_MEDIO_{nome}_{LOC}_{Empresa}.png"
        plt.savefig(temp_arq, dpi = 500)
        if st:
            st.pyplot(fig)
    
        plt.close(fig)

        st.html("""
                        <h3>
                        Metodologia — Savitzky–Golay, Derivadas e Smoothed Bootstrap — para análise do Vão Mínimo
                        </h3>
        
                        <p  style="text-align: justify;text-indent: 40px">
                        O algoritmo utiliza o filtro de Savitzky–Golay para suavizar a curva de quantis (0,5% a 5%)
                e estimar analiticamente suas derivadas de 1ª e 2ª ordem. A topologia da cauda é classificada em
                Uniforme, Multimodal ou Unimodal, e a estabilidade é avaliada via bootstrap.</p>
                        """)
        fig2, axes2 = plt.subplots(1, 1, figsize=(15, 5))
        axes2.hist(df1['COMP'],  bins='auto', color='blue', density=True)
        axes2.set_title('Distribuição cumulativa comprimento dos itens que compõe o percentil 5%')
        axes2.set_xlabel('Comprimento (m)')
        axes2.set_ylabel('Densidade')

        axes2.axvline(valor_05pct, color='green', linestyle='dashed', 
                label=f'5% de {nome} ≤ {valor_05pct:.2f} m'.replace(".",","))
        axes2.legend()
        plt.tight_layout()
        temp_arq = rf"{dir_saida}/IMAGENS/VAO_PCT05_{nome}_{LOC}_{Empresa}.png"
        plt.savefig(temp_arq, dpi = 500)
        if st:
            st.pyplot(fig2)
        plt.close(fig2)

        fig, axes = plt.subplots(1, 3, figsize=(15, 5),
                         sharex=True)

        axes[0].plot(resultado["Percentil"], resultado["Comprimento_m"], "o-", markersize=4,
                    label="Quantis observados")
        axes[0].plot(resultado["Percentil"], resultado["Q_suave"], "--", linewidth=2,
                    label="Curva suavizada")
        axes[0].set_ylabel("Comprimento (m)")
        axes[0].legend()

        axes[1].plot(resultado["Percentil"], resultado["Derivada_1"], color="tab:orange")
        axes[1].set_ylabel("dQ / dp (Inverso da Densidade)")

        axes[2].plot(resultado["Percentil"], resultado["Derivada_2"], color="tab:green")
        axes[2].axhline(0, color="black", linestyle="--")
        axes[2].set_ylabel("d²Q / dp²")
        axes[2].set_xlabel("Percentil (%)")

        for ax in axes:
            ax.grid(alpha=0.3)

        plt.tight_layout()
        if st:
            st.pyplot(fig)
        plt.close(fig)
        p_util = resultado["Percentil"].to_numpy()
        c_util = resultado["Comprimento_m"].to_numpy()
        curv_util = resultado["Curvatura"].to_numpy()
        picos, propriedades = find_peaks(
                                            curv_util,
                                            prominence=max(np.ptp(curv_util) * 0.10, 1e-10),
                                            distance=2
                                        )

        candidatos = pd.DataFrame({
                                        "Percentil": percentis[picos],
                                        "Comprimento_m": comprimentos[picos],
                                        "Curvatura_abs": curvatura[picos],
                                        "Proeminencia": propriedades["prominences"]
                                    })

        candidatos = candidatos.sort_values("Proeminencia", ascending=False).reset_index(drop=True)
        fig, ax = plt.subplots(figsize=(15, 6))

        ax.plot(p_util, curv_util, label="Curvatura normalizada κ(p)")
        ax.scatter(p_util[picos], curv_util[picos],color="red", zorder=3, label="Candidatos (Picos)")

        for i in picos:
            ax.annotate(
                            f"P{percentis[i]:.2f}".replace(".",","),
                            (p_util[i], curv_util[i]),
                            xytext=(0, 8),
                            textcoords="offset points",
                            ha="center"
                        )

        ax.set_xlabel("Percentil (%)")
        ax.set_ylabel("Curvatura κ(p)")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        if st:
            st.pyplot(fig)
        plt.close(fig)

        rng = np.random.default_rng(42)
        n_boot = 500
        n_obs = len(comp)

        iqr_comp = np.percentile(comp, 75) - np.percentile(comp, 25)
        sigma_s = min(np.std(comp, ddof=1), iqr_comp / 1.34) if iqr_comp > 0 else np.std(comp, ddof=1)
        h_silverman = 0.9 * sigma_s * (n_obs ** (-0.2)) * 0.25 

        p_boot = np.empty(n_boot)
        l_boot = np.empty(n_boot)
        tipos_boot = []
        usar_bootstrap_suavizado = False
        for b in range(n_boot):
            amostra = rng.choice(comp, size=n_obs, replace=True)
            if usar_bootstrap_suavizado and h_silverman > 0:
                amostra = np.clip(amostra + rng.normal(0.0, h_silverman, size=n_obs), comp.min(), None)
            res_b = analisar_cauda_percentis(amostra)
            p_boot[b] = res_b["p_otimo"]
            l_boot[b] = res_b["comp_otimo"]
            tipos_boot.append(res_b["tipo"])

        serie_tipos = pd.Series(tipos_boot).value_counts(normalize=True) * 100
        classe_dominante = serie_tipos.index[0]
        consistencia_pct = serie_tipos.iloc[0]
        mascara_dominante = np.asarray(tipos_boot) == classe_dominante
        l_boot_dominante = l_boot[mascara_dominante]
        p_boot_dominante = p_boot[mascara_dominante]
        vao_min_estatistico = float(np.median(l_boot_dominante))
        ic_95_inf, ic_95_sup = np.percentile(l_boot_dominante, [2.5, 97.5])
        vao_min_confiavel = max(vao_min_estatistico, 0)
        estabilidade_alerta = False #consistencia_pct < 80.0

        fig, axes = plt.subplots(1, 2, figsize=(15, 5))

        axes[0].hist(p_boot, bins=np.arange(0.5, 5.15, 0.2),
                    edgecolor="black", color="steelblue")
        axes[0].axvline(np.median(p_boot), color="red", linestyle="--", label=f"Mediana: P{np.median(p_boot):.2f}%".replace(".",","))
        axes[0].set_title(f"Classe dominante: {classe_dominante} ({consistencia_pct:.1f}%)".replace(".",",") + (" — INSTÁVEL" if estabilidade_alerta else ""))
        axes[0].set_xlabel("Percentil candidato (%)")
        axes[0].set_ylabel("Frequência no Bootstrap")
        axes[0].legend()

        axes[1].hist(l_boot_dominante, bins=25, edgecolor="black", color="steelblue")
        axes[1].axvline(vao_min_confiavel, color="red", linestyle="--", label=f"Mínimo Confiável: {vao_min_confiavel:.2f} m".replace(".",","))
        axes[1].axvline(ic_95_inf, color="orange", linestyle=":", label=f"IC 95%: [{ic_95_inf:.2f}m, {ic_95_sup:.2f}m]".replace(".",","))
        axes[1].axvline(ic_95_sup, color="orange", linestyle=":")
        axes[1].axvline(vao_min_estatistico, color="red", linestyle="--", label=f"Mediana estatística: {vao_min_estatistico:.2f} m".replace(".",","))
        axes[1].axvline(vao_min_confiavel, color="green", linestyle="--", label=f"Corte operacional: {vao_min_confiavel:.2f} m".replace(".",","))
        axes[1].set_title("Bootstrap do estimador — classe dominante")
        axes[1].set_xlabel("Comprimento candidato (m)")
        axes[1].set_ylabel("Frequência no Bootstrap")
        axes[1].legend()

        plt.tight_layout()
        if st:
            st.pyplot(fig)
        plt.close(fig)
  
        extensao_total = comp.sum()
        resultado["N_excluidos"] = [np.sum(comp <= limite) for limite in resultado["Comprimento_m"]]
        resultado["Extensao_excluida_m"] = [comp[comp <= limite].sum() for limite in resultado["Comprimento_m"]]
        resultado["Extensao_excluida_pct"] = 100.0 * resultado["Extensao_excluida_m"] / extensao_total

        fig, ax = plt.subplots(figsize=(15, 5))
        ax.plot(resultado["Comprimento_m"], resultado["Extensao_excluida_pct"], marker="o", label="Curva de impacto")
        ax.axvline(
            vao_min_confiavel, color="red", linestyle="--",
            label=f"Corte Recomendado ({vao_min_confiavel:.2f} m)".replace(".",","))
        
        ax.set_xlabel("Comprimento mínimo adotado (m)")
        ax.set_ylabel("Extensão total excluída (%)")
        ax.set_title("Impacto dos limites mínimos na extensão da rede")
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        if st:
            st.pyplot(fig)
        plt.close(fig)

        return None    


def eqp_rsv(dir_arq_base, sufixo, con, con1, st=None):

    if isinstance(con1, str):
        con1 = sl.connect(con1)
    colunas = [
                    "COD_ID", "TIP_INST", "ODI", "TI", "CM", "TUC", "A1", "A2", 
                    "A3", "A4", "A5", "A6", "UAR", "SITCONT", "DAT_IMO"
                ]
    df_RES = pd.DataFrame(columns=colunas)
    if sql.existe_tabela(f'EQTRAT_{sufixo}', con):
        df_TRSE = pd.read_sql(f'''SELECT COD_ID, TIP_INST, ODI, TI, CM, TUC, A1, A2, A3, A4, A5, A6, UAR, 
                                    SITCONT, DAT_IMO 
                            FROM EQTRAT_{sufixo} WHERE TI = 98 or SITCONT = "RT"''', con)
        df_RES = pd.concat([df_RES,df_TRSE], ignore_index=True)
    if sql.existe_tabela(f'EQTRM_{sufixo}', con):
        df_TRM = pd.read_sql(f'''SELECT 
                                    COD_ID, TIP_INST, ODI, TI, CM, TUC, A1, A2, A3, A4, A5, A6, UAR, 
                                    SITCONT, DAT_IMO 
                             FROM EQTRM_{sufixo} WHERE TI = 98 or SITCONT = "RT"''', con)
        df_RES = pd.concat([df_RES,df_TRM], ignore_index=True)
    if sql.existe_tabela(f'EQTRMT_{sufixo}', con):
        df_TRD = pd.read_sql(f'''SELECT 
                                    COD_ID, TIP_INST, ODI, TI, CM, TUC, A1, A2, A3, A4, A5, A6, UAR, 
                                    SITCONT, DAT_IMO 
                             FROM EQTRMT_{sufixo} WHERE TI = 98 or SITCONT = "RT"''', con)
        df_RES = pd.concat([df_RES,df_TRD], ignore_index=True)
    if sql.existe_tabela(f'EQRE_{sufixo}', con):
        df_RE = pd.read_sql(f'''SELECT 
                                    COD_ID, TIP_INST, ODI, TI, CM, TUC, A1, A2, A3, A4, A5, A6, UAR, 
                                    SITCONT, DAT_IMO 
                             FROM EQRE_{sufixo} WHERE TI = 98 or SITCONT = "RT"''', con)
        df_RES = pd.concat([df_RES,df_RE], ignore_index=True)
    if sql.existe_tabela(f'EQSE_{sufixo}', con):
        df_SE = pd.read_sql(f'''SELECT 
                                    COD_ID, TIP_INST, ODI, TI, CM, TUC, A1, A2, A3, A4, A5, A6, UAR, 
                                    SITCONT, DAT_IMO 
                             FROM EQSE_{sufixo} WHERE TI = 98 or SITCONT = "RT"''', con)
        df_RES = pd.concat([df_RES,df_SE], ignore_index=True)
    if sql.existe_tabela(f'EQCR_{sufixo}', con):
        df_CR = pd.read_sql(f'''SELECT 
                                    COD_ID, TIP_INST, ODI, TI, CM, TUC, A1, A2, A3, A4, A5, A6, UAR, 
                                    SITCONT, DAT_IMO 
                             FROM EQCR_{sufixo} WHERE TI = 98 or SITCONT = "RT"''', con)
        df_RES = pd.concat([df_RES,df_CR], ignore_index=True)
    if sql.existe_tabela(f'EQME_{sufixo}', con):
        df_MD = pd.read_sql(f'''SELECT 
                                    COD_ID, TIP_INST, ODI, TI, CM, TUC, A1, A2, A3, A4, A5, A6, UAR, 
                                    SITCONT, DAT_IMO 
                             FROM EQME_{sufixo} WHERE TI = 98 or SITCONT = "RT"''', con)
        df_RES = pd.concat([df_RES,df_MD], ignore_index=True)
    if sql.existe_tabela(f'PONNOT_{sufixo}', con):
        df_EST = pd.read_sql(f'''SELECT 
                                    COD_ID, TIP_INST, ODI, TI, CM, TUC, A1, A2, A3, A4, A5, A6, UAR, 
                                    SITCONT, '' AS DAT_IMO 
                             FROM PONNOT_{sufixo} WHERE TI = 98 or SITCONT = "RT"''', con)
        df_RES = pd.concat([df_RES,df_EST], ignore_index=True)
    df_RES['Qtd_BDGD'] = 1

    SQLq = f"""
                SELECT
                    Ide_AIS,
                    Cd_ODI AS ODI,
                    Nr_TI AS TI,
                    Nr_CM AS CM,
                    Nr_TUC AS TUC,
                    Nr_A1 AS A1,
                    Nr_A2 AS A2,
                    Nr_A3 AS A3,
                    Nr_A4 AS A4,
                    Nr_A5 AS A5,
                    Nr_A6 AS A6,
                    Cd_UAR,
                    CAST(Qtd_AIS AS REAL) AS Qtd_AIS,
                    Dt_Imob,
                    CAST(VL_VOC AS REAL) AS VL_VOC,
                    CAST(VL_DEP_ACUM AS REAL) AS VL_DEP_ACUM
                FROM 
                    AIS 
                WHERE 
                    dt_ARQ = ? AND Nr_TI = 98
            """
    AIS = sql.imp_tbl_forma_001("AIS",SQLq=SQLq, con=con1, st=st, Empresa=st.session_state.nm_empr)

    AIS['OBS_SFF'] = 'NO'

    obs_uar = """Justificar que atende aos critérios do item 6.3.6, parágrafo 2, alínea b: 
    Entende-se por Reserva Imobilizada a Unidade de Cadastro – UC, ou conjunto de bens, que, por
    razões de ordem técnica voltada à garantia e confiabilidade do sistema elétrico, 
    embora não estando em serviço, esteja à disposição e que poderá entrar em operação de imediato. Sua
    contabilização obedece a todos os preceitos do Imobilizado em serviço, inclusive no que se refere
    à depreciação."""

    obs_depreciado = "Justificar bem 100% depreciado como reserva."

    mask_uar = AIS['Cd_UAR'].eq('UAR')
    mask_depreciado = (AIS['VL_VOC'] - AIS['VL_DEP_ACUM']).abs().lt(0.01)

    AIS.loc[mask_uar, 'OBS_SFF'] = obs_uar

    AIS.loc[mask_depreciado, 'OBS_SFF'] = AIS.loc[mask_depreciado, 'OBS_SFF'].apply(
                                                lambda x: obs_depreciado if x == 'NO' else f"{x}\n\n{obs_depreciado}"
                                            )
    AIS.to_csv(rf'{dir_arq_base}/RESERVAS_AIS.csv', sep="|", index=False)
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}/RESERVAS_AIS.csv',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)
    AIS.to_sql('TBL_RESERVAS_AIS', con1, if_exists='replace', index=False)
    chave = ['ODI', 'TI', 'CM', 'TUC', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6']
    df_AIS = (
                AIS[AIS['Cd_UAR'] != 'UAR']
                .groupby(chave, dropna=False)
                .agg(Qtd_AIS=('Qtd_AIS', 'sum'))
                .reset_index()
            )
    df_bdgd = (
                df_RES
                .groupby(chave, dropna=False)
                .agg(Qtd_BDGD=('Qtd_BDGD', 'sum'))
                .reset_index()
            )
    df_anls = df_AIS.merge(df_bdgd, how='outer', on = chave, suffixes=("_AIS","_BDGD"), indicator=True)
    df_anls['Qtd_BDGD'] = df_anls['Qtd_BDGD'].fillna(0)
    df_anls['Qtd_AIS'] = df_anls['Qtd_AIS'].fillna(0)
    df_anls['TST_QTD'] = (df_anls['Qtd_AIS'].fillna(0) - df_anls['Qtd_BDGD'].fillna(0)).abs() < 0.01
    df_anls['OBS'] = np.select(
                                [
                                    df_anls['_merge'].isin(['left_only']) & (df_anls['Qtd_AIS'].fillna(0) == 0),
                                    df_anls['_merge'].isin(['right_only']) & (df_anls['Qtd_BDGD'].fillna(0) == 0),
                                    df_anls['_merge'].isin(['left_only', 'right_only']),
                                    df_anls['_merge'].eq('both') & (~df_anls['TST_QTD'].astype(bool))
                                ],
                                [
                                    'Justificar quantidade zerada no AIS.',
                                    'Justificar quantidade zerada na BDGD.',
                                    'Fazer conciliação.',
                                    'Solicitar avaliação das quantidades. Se for anual, pode ser referência das bases.'
                                ],
                                default='NO'
                            )
    df_anls = df_anls.drop(columns=['_merge','TST_QTD'])
    df_anls.to_sql('TBL_RESERVAS_CONCILIACAO', con1, if_exists='replace', index=False)

    workbook = xlsxwriter.Workbook(rf'{dir_arq_base}//Saida_RESERVAS_CONCILIACAO.xlsx',
    {'nan_inf_to_errors': True})

    worksheet1 = workbook.add_worksheet('BDGD')
    worksheet2 = workbook.add_worksheet('AIS')
    worksheet3 = workbook.add_worksheet('CONCILIACAO')

    workbook.set_calc_mode('auto')
    workbook.use_zip64()

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'right'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 16,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})

    linhasAMAIS=8
    worksheet1.merge_range('C5:O5', f'CÁLCULO PROVISÓRIO: {st.session_state.nm_empr}', tituloP)

    formatos = {}
    lst_txt = []
    lst_moe = []
    lst_num = []
    lst_dt = []
    lst_pct = []
    for col, n in enumerate(df_RES.columns):
        if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
            lst_txt.append(col)
        elif n[:3].upper() in ['VL_']:
            lst_moe.append(col)
        elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
            lst_num.append(col)
        elif n[:3].upper() in ['DT_']:
            lst_dt.append(col)
        elif n[:3].upper() in ['ALI']:
            lst_pct.append(col)
        
    if len(lst_txt)>0:
        formatos[tuple(lst_txt)] = texto
    if len(lst_moe)>0:
        formatos[tuple(lst_moe)] = currency_format
    if len(lst_num)>0:
        formatos[tuple(lst_num)] = number_format
    if len(lst_dt)>0:
        formatos[tuple(lst_dt)] = data_format
    if len(lst_pct)>0:
        formatos[tuple(lst_pct)] = percentual_format

    x1 = ax_escreve_excel_md2(worksheet1, df_RES, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    worksheet2.merge_range('C5:O5', f'CÁLCULO PROVISÓRIO: {st.session_state.nm_empr}', tituloP)

    formatos = {}
    lst_txt = []
    lst_moe = []
    lst_num = []
    lst_dt = []
    lst_pct = []
    for col, n in enumerate(AIS.columns):
        if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
            lst_txt.append(col)
        elif n[:3].upper() in ['VL_']:
            lst_moe.append(col)
        elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
            lst_num.append(col)
        elif n[:3].upper() in ['DT_']:
            lst_dt.append(col)
        elif n[:3].upper() in ['ALI']:
            lst_pct.append(col)
        
    if len(lst_txt)>0:
        formatos[tuple(lst_txt)] = texto
    if len(lst_moe)>0:
        formatos[tuple(lst_moe)] = currency_format
    if len(lst_num)>0:
        formatos[tuple(lst_num)] = number_format
    if len(lst_dt)>0:
        formatos[tuple(lst_dt)] = data_format
    if len(lst_pct)>0:
        formatos[tuple(lst_pct)] = percentual_format

    x1 = ax_escreve_excel_md2(worksheet2, AIS, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    
    worksheet3.merge_range('C5:O5', f'CÁLCULO PROVISÓRIO: {st.session_state.nm_empr}', tituloP)

    formatos = {}
    lst_txt = []
    lst_moe = []
    lst_num = []
    lst_dt = []
    lst_pct = []
    for col, n in enumerate(df_anls.columns):
        if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
            lst_txt.append(col)
        elif n[:3].upper() in ['VL_']:
            lst_moe.append(col)
        elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
            lst_num.append(col)
        elif n[:3].upper() in ['DT_']:
            lst_dt.append(col)
        elif n[:3].upper() in ['ALI']:
            lst_pct.append(col)
        
    if len(lst_txt)>0:
        formatos[tuple(lst_txt)] = texto
    if len(lst_moe)>0:
        formatos[tuple(lst_moe)] = currency_format
    if len(lst_num)>0:
        formatos[tuple(lst_num)] = number_format
    if len(lst_dt)>0:
        formatos[tuple(lst_dt)] = data_format
    if len(lst_pct)>0:
        formatos[tuple(lst_pct)] = percentual_format

    x1 = ax_escreve_excel_md2(worksheet3, df_anls, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    workbook.close()
    if st:
        registrar_artefato(st.session_state.database_MAN, 
                            st.session_state.execucao_id, 
                            file_path = rf'{dir_arq_base}//Saida_RESERVAS_CONCILIACAO.xlsx',
                            tipo_artefato = "SAIDA", 
                            calcular_hash = True)