from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import streamlit as st, os, glob, json, csv, time
import pandas as pd, re, sqlite3 as sl, math, numpy as np
from pydantic import BaseModel, Field, ValidationError, model_validator, field_validator, PrivateAttr, ConfigDict
from typing import List, Optional, Any, ClassVar
from decimal import Decimal, InvalidOperation
from enum import Enum
from datetime import datetime, date
from pydantic_core import PydanticCustomError
import unicodedata
from typing import Callable

TUC_IPCA = frozenset({'535', '230', '235'})

CFOPS_BPR = {
                "1406",
                "1551",
                "1553",
                "1555",
                "2406",
                "2551",
                "2553",
                "2555",
            }

CST_ICMS_COM_ICMS = {"00", "10", "20"}
CST_ICMS_COM_ST = {"10", "60", "70"}

@lru_cache(maxsize=4)
def referencias_incr(pasta='tabelas'):
    pasta = Path(pasta)
    infra = pd.read_csv(pasta / 'TBL_TUC_INFRA.csv', sep='|', encoding='latin-1', dtype=str,
                        usecols=['Nr_TUC', 'Nr_A1']).fillna('')
    orca = pd.read_csv(pasta / 'TBL_TUC_ORC.csv', sep='|', encoding='latin-1', dtype=str,
                       usecols=['Nr_TUC', 'Nr_A1']).fillna('')
    ipca = pd.read_csv(pasta / 'IPCA.csv', sep='|', encoding='latin-1',
                       usecols=['Dt_REF', 'Nr_IPCA'], dtype=str)
    ipca['Dt_REF'] = pd.to_datetime(ipca['Dt_REF'], format="%Y-%m-%d", errors='coerce', dayfirst=True)
    ipca['Nr_IPCA'] = pd.to_numeric(ipca['Nr_IPCA'].str.replace(',', '.', regex=False), errors='coerce')
    ipca = (ipca.dropna(subset=['Dt_REF', 'Nr_IPCA'])
                .sort_values('Dt_REF').drop_duplicates('Dt_REF', keep='last'))
    if ipca.empty:
        raise ValueError('Tabela IPCA não contém datas e índices válidos')
    infra0 = set(infra.loc[infra['Nr_A1'].eq('0'), 'Nr_TUC'])
    infrapar = set(map(tuple, infra.loc[infra['Nr_A1'].ne('0'), ['Nr_TUC', 'Nr_A1']].to_numpy()))
    orca0 = set(orca.loc[orca['Nr_A1'].eq('0'), 'Nr_TUC'])
    return infra0, infrapar, orca0, ipca

def gravar_agregado_incr(
                            base_agregada: pd.DataFrame,
                            nr_lote: int,
                            pasta: str = "tabelas/agregados_incr"
                        ) -> None:

    destino = Path(pasta)
    destino.mkdir(parents=True, exist_ok=True)

    colunas = [
                    "Nr_TI",
                    "Nr_TUC",
                    "Cd_TP_AVAL",
                    "COD_ITEM",
                    "VOC_ATUALIZADO",
                    "VOC_VF_ATUALIZADO",
                    "VNR",
                    "VNR_VF_TOTAL",
                    "Qtd_AIS"
                ]

    df = base_agregada[colunas].copy()

    for campo in ["Nr_TI", "Nr_TUC", "Cd_TP_AVAL","COD_ITEM"]:
        df[campo] = df[campo].astype("string").str.strip()

    for campo in ["VOC_ATUALIZADO", "VNR", "VNR_VF_TOTAL", "VOC_VF_ATUALIZADO", "Qtd_AIS"]:
        df[campo] = pd.to_numeric(df[campo], errors="coerce")

    df = df.loc[
                    df["Cd_TP_AVAL"].isin(["1", "2"])
                    & df["Nr_TI"].notna()
                    & df["Nr_TUC"].notna()
                    & df["Nr_TI"].ne("")
                    & df["Nr_TUC"].ne("")
                    & np.isfinite(df["VOC_ATUALIZADO"])
                    & np.isfinite(df["VNR"])
                    & df["VOC_ATUALIZADO"].gt(0)
                    & df["VNR"].ge(0)
                ]

    agregado = (
                    df.groupby(
                        ["Nr_TI", "Nr_TUC", "Cd_TP_AVAL", "COD_ITEM"],
                        as_index=False
                    )
                    .agg(
                        VOCa=("VOC_ATUALIZADO", "sum"),
                        VNR=("VNR", "sum"),
                        Qtd_Registros=("VNR", "size"),
                        VOC_VF_ATUALIZADO=("VOC_VF_ATUALIZADO", "sum"),
                        VNR_VF_TOTAL=("VNR_VF_TOTAL", "sum"),
                        Qtd_AIS=("Qtd_AIS", "sum"),
                    )
                )

    arquivo = destino / f"INCR_agregado_lote_{nr_lote:06d}.parquet"
    temporario = destino / f"INCR_agregado_lote_{nr_lote:06d}.tmp.parquet"

    agregado.to_parquet(temporario, index=False)
    temporario.replace(arquivo)

def consolidar_agregados_incr(
                                pasta: str = "tabelas/agregados_incr"
                            ) -> pd.DataFrame:

    arquivos = sorted(
                        Path(pasta).glob("INCR_agregado_lote_*.parquet")
                    )

    if not arquivos:
        return pd.DataFrame()

    parciais = [
                    pd.read_parquet(arquivo)
                    for arquivo in arquivos
                ]

    df = pd.concat(parciais, ignore_index=True)

    return (
                df.groupby(
                    ["Nr_TI", "Nr_TUC", "Cd_TP_AVAL", "COD_ITEM"],
                    as_index=False
                )
                .agg(
                    VOCa=("VOCa", "sum"),
                    VNR=("VNR", "sum"),
                    Qtd_Registros=("Qtd_Registros", "sum"),
                    VOC_VF_ATUALIZADO=("VOC_VF_ATUALIZADO", "sum"),
                    VNR_VF_TOTAL=("VNR_VF_TOTAL", "sum"),
                    Qtd_AIS=("Qtd_AIS", "sum")
                )
            )

def analisar_vf_agregado_incr(consolidado: pd.DataFrame) -> pd.DataFrame:

    niveis = {
                "TI/TUC/COD_ITEM": ["Nr_TI", "Nr_TUC", "COD_ITEM", "Cd_TP_AVAL"],
                "TI/COD_ITEM": ["Nr_TI", "COD_ITEM", "Cd_TP_AVAL"],
                "TUC/COD_ITEM": ["Nr_TUC", "COD_ITEM", "Cd_TP_AVAL"],
                "COD_ITEM": ["COD_ITEM", "Cd_TP_AVAL"],            
            }

    resultados = []

    for nivel, chaves in niveis.items():

        df = (
                consolidado
                .groupby(chaves, as_index=False, dropna=False)
                .agg(
                    VOC_VF_ATUALIZADO=("VOC_VF_ATUALIZADO", "sum"),
                    VNR_VF_TOTAL=("VNR_VF_TOTAL", "sum"),
                    Qtd_AIS=("Qtd_AIS", "sum"),
                )
            )

        df = df.loc[df["Qtd_AIS"].gt(0)].copy()

        df["VOC_VF_UNIT_ATUALIZADO"] = (
                                            df["VOC_VF_ATUALIZADO"] / df["Qtd_AIS"]
                                        )

        df["VNR_VF_UNIT"] = (
                                df["VNR_VF_TOTAL"] / df["Qtd_AIS"]
                            )

        df = df.loc[df["VOC_VF_UNIT_ATUALIZADO"].gt(0)].copy()

        df["Diferenca_Pct"] = (
                                    df["VNR_VF_UNIT"] / df["VOC_VF_UNIT_ATUALIZADO"] - 1
                                ) * 100

        df["Limite_Pct"] = 15.0

        df = df.loc[df["Diferenca_Pct"].abs().gt(15)].copy()

        if df.empty:
            continue

        df["Nivel"] = nivel
        df["Nr_TI"] = df.get("Nr_TI", pd.NA)
        df["Nr_TUC"] = df.get("Nr_TUC", pd.NA)
        df["COD_ITEM"] = df.get("COD_ITEM", pd.NA)

        resultados.append(df)

    if not resultados:
        return pd.DataFrame()

    return pd.concat(resultados, ignore_index=True)

def analisar_agregados_incr(
                                consolidado: pd.DataFrame
                            ) -> pd.DataFrame:

    if consolidado.empty:
        return pd.DataFrame()

    niveis = {
                "TI/TUC": ["Nr_TI", "Nr_TUC", "Cd_TP_AVAL"],
                "TI": ["Nr_TI", "Cd_TP_AVAL"],
                "TUC": ["Nr_TUC", "Cd_TP_AVAL"],
                "TP_AVAL": ["Cd_TP_AVAL"]
            }

    resultados = []

    for nivel, chaves in niveis.items():

        df = (
                    consolidado.groupby(
                        chaves,
                        as_index=False
                    )
                    .agg(
                        VOCa=("VOCa", "sum"),
                        VNR=("VNR", "sum"),
                        Qtd_Registros=("Qtd_Registros", "sum")
                    )
                )

        df = df.loc[df["VOCa"].gt(0)].copy()

        df["Diferenca_Pct"] = (
                                    (df["VNR"] / df["VOCa"]) - 1
                                ) * 100

        df["Limite_Pct"] = np.where(
                                        df["Cd_TP_AVAL"].eq("2"),
                                        5.0,
                                        2.0
                                    )

        df = df.loc[
                        df["Diferenca_Pct"].abs() > df["Limite_Pct"]
                    ].copy()

        if df.empty:
            continue

        df["Nivel"] = nivel

        if "Nr_TI" not in df.columns:
            df["Nr_TI"] = pd.NA

        if "Nr_TUC" not in df.columns:
            df["Nr_TUC"] = pd.NA

        resultados.append(df)

    if not resultados:
        return pd.DataFrame()

    return pd.concat(resultados, ignore_index=True)

def gerar_alertas_incr_vf_agregados(
                                    divergencias: pd.DataFrame
                                ) -> list[dict]:

    erros = []

    if divergencias.empty:
        return erros

    for registro in divergencias.itertuples(index=False):

        identificacao = []

        if pd.notna(registro.Nr_TI):
            identificacao.append(f"Nr_TI={registro.Nr_TI}")

        if pd.notna(registro.Nr_TUC):
            identificacao.append(f"Nr_TUC={registro.Nr_TUC}")

        if pd.notna(registro.COD_ITEM):
            identificacao.append(f"COD_ITEM={registro.COD_ITEM}")

        diferenca = float(registro.Diferenca_Pct)
        sentido = "acima" if diferenca > 0 else "abaixo"

        mensagem = (
                        f"Agregação {registro.Nivel}: "
                        f"{', '.join(identificacao)}; "
                        f"Cd_TP_AVAL={registro.Cd_TP_AVAL}; "
                        f"VNR VF unitário {abs(diferenca):,.2f}% {sentido} "
                        f"do VOC VF unitário atualizado pelo IPCA; "
                        f"tolerância ±15% "
                    ).replace(",","@").replace(".",",").replace("@",".")

        erros.append({
                        "type": "value_error",
                        "severidade": "ALERTA",
                        "loc": ("tabela", 0, "VL_VNR_UC"),
                        "msg": f"Alerta: {mensagem}",
                        "input": None,
                        "ctx": {"error": ValueError(mensagem)},
                        "etapa": 0,
                        "nivel_agregacao": registro.Nivel,
                        "Nr_TI": registro.Nr_TI,
                        "Nr_TUC": registro.Nr_TUC,
                        "diferenca_pct": round(diferenca, 2)
                    })

    return erros

def gerar_alertas_incr_agregados(
                                    divergencias: pd.DataFrame
                                ) -> list[dict]:

    erros = []

    if divergencias.empty:
        return erros

    for registro in divergencias.itertuples(index=False):

        identificacao = []

        if pd.notna(registro.Nr_TI):
            identificacao.append(f"Nr_TI={registro.Nr_TI}")

        if pd.notna(registro.Nr_TUC):
            identificacao.append(f"Nr_TUC={registro.Nr_TUC}")

        diferenca = float(registro.Diferenca_Pct)
        sentido = "acima" if diferenca > 0 else "abaixo"

        mensagem = (
                        f"Agregação {registro.Nivel}: "
                        f"{', '.join(identificacao)}; "
                        f"Cd_TP_AVAL={registro.Cd_TP_AVAL}; "
                        f"VNR {abs(diferenca):,.2f}% {sentido} "
                        f"do VOC atualizado pelo IPCA; "
                        f"tolerância ±{registro.Limite_Pct:.0f}%; "
                        f"{registro.Qtd_Registros} registros"
                    ).replace(",","@").replace(".",",").replace("@",".")

        erros.append({
                        "type": "value_error",
                        "severidade": "ALERTA",
                        "loc": ("tabela", 0, "VL_VNR_UC"),
                        "msg": f"Alerta: {mensagem}",
                        "input": None,
                        "ctx": {"error": ValueError(mensagem)},
                        "etapa": 0,
                        "nivel_agregacao": registro.Nivel,
                        "Nr_TI": registro.Nr_TI,
                        "Nr_TUC": registro.Nr_TUC,
                        "diferenca_pct": round(diferenca, 2)
                    })

    return erros

def validar_vnr_voc_ipca(
                            x: pd.DataFrame,
                            ipca: pd.DataFrame,
                            deslocamento: int = 0
                        ) -> list[dict]:

    erros = []

    def col(nome):
        return x[nome].astype("string").fillna("").str.strip()

    def num(nome):
        return pd.to_numeric(
                                col(nome).str.replace(",", ".", regex=False),
                                errors="coerce"
                            )

    tipo = col("Cd_TP_AVAL")
    voc = num("VL_VOC")
    vnr = num("VL_VNR_UC")
    voc_vf = num("VL_VOC_VF")

    dt_imob = (
                    pd.to_datetime(
                        col("Dt_Imob"),
                        format="%Y/%m/%d",
                        errors="coerce"
                    )
                    .dt.to_period("M")
                    .dt.to_timestamp(how="start")
                )

    dt_ref = (
                pd.to_datetime(
                    col("Dt_REF_DADOS"),
                    format="%Y/%m/%d",
                    errors="coerce"
                )
                .dt.to_period("M")
                .dt.to_timestamp(how="start")
            )

    elegiveis = (
                    tipo.isin(["1", "2"])
                    & voc.gt(0)
                    & vnr.notna()
                    & dt_imob.notna()
                    & dt_ref.notna()
                    & dt_ref.ge(dt_imob)
                )

    ids = np.flatnonzero(elegiveis.to_numpy(dtype=bool))

    if not len(ids):
        return erros

    base = pd.DataFrame({
                            "idx": ids,
                            "ini": dt_imob.iloc[ids].dt.to_period("M").dt.to_timestamp().to_numpy(),
                            "ref": dt_ref.iloc[ids].dt.to_period("M").dt.to_timestamp().to_numpy()
                        })

    tabela = ipca[["Dt_REF", "Nr_IPCA"]].copy()
    tabela = tabela.dropna(subset=["Dt_REF"])

    if tabela.empty:
        return erros

    ini = base[["idx", "ini"]].merge(
                                        tabela.rename(columns={"Dt_REF": "ini", "Nr_IPCA": "ipca_ini"}),
                                        on="ini",
                                        how="left",
                                        validate="many_to_one"
                                    )

    ref = base[["idx", "ref"]].merge(
                                        tabela.rename(columns={"Dt_REF": "ref", "Nr_IPCA": "ipca_ref"}),
                                        on="ref",
                                        how="left",
                                        validate="many_to_one"
                                    )

    fatores = ini[["idx", "ipca_ini"]].merge(
                                                ref[["idx", "ipca_ref"]],
                                                on="idx",
                                                how="inner",
                                                validate="one_to_one"
                                            )

    validos = (
                    fatores["ipca_ini"].gt(0)
                    & fatores["ipca_ref"].gt(0)
                )

    fatores = fatores.loc[validos]

    if fatores.empty:
        return erros

    idx = fatores["idx"].to_numpy(dtype=int)

    voc_atualizado = (
                        voc.iloc[idx].to_numpy(dtype=float)
                        * fatores["ipca_ref"].to_numpy(dtype=float)
                        / fatores["ipca_ini"].to_numpy(dtype=float)
                    )

    voc_vf_atualizado = (
                            voc_vf.iloc[idx].to_numpy(dtype=float)
                            * fatores["ipca_ref"].to_numpy(dtype=float)
                            / fatores["ipca_ini"].to_numpy(dtype=float)
                        )

    vnr_valores = vnr.iloc[idx].to_numpy(dtype=float)
    vnr_vf_valores = (num("VL_VNR_VF_UNIT").iloc[idx].to_numpy()
                      * num("Qtd_AIS").iloc[idx].to_numpy())

    base_agregada = pd.DataFrame({
                                    "idx": idx,
                                    "Nr_TI": col("Nr_TI").iloc[idx].to_numpy(),
                                    "Nr_TUC": col("Nr_TUC").iloc[idx].to_numpy(),
                                    "COD_ITEM": col("COD_ITEM").iloc[idx].to_numpy(),
                                    "Cd_TP_AVAL": tipo.iloc[idx].to_numpy(),
                                    "VOC_ATUALIZADO": voc_atualizado,
                                    "VOC_VF_ATUALIZADO": voc_vf_atualizado,
                                    "VNR": vnr_valores,
                                    "VNR_VF_TOTAL": vnr_vf_valores,
                                    "Qtd_AIS": num("Qtd_AIS").iloc[idx].to_numpy()
                                })
    base_agregada = base_agregada.loc[
                                        np.isfinite(base_agregada["VOC_ATUALIZADO"])
                                        & np.isfinite(base_agregada["VNR"])
                                        & base_agregada["VOC_ATUALIZADO"].gt(0)
                                        & base_agregada["VNR"].ge(0)
                                    ]
    
    return base_agregada

def validar_incr_bloco(df: pd.DataFrame, deslocamento: int = 0,
                        pasta='tabelas', dt_fim=None) -> list[dict]:

    if df.empty:
        return []

    x = df.reset_index(drop=True)
    n = len(x)
    erros = []

    def col(nome):
        if nome not in x.columns:
            return pd.Series('', index=x.index, dtype='string')
        return x[nome].astype('string').fillna('').str.strip()

    def num(nome):
        return pd.to_numeric(col(nome).str.replace(',', '.', regex=False), errors='coerce')

    def emitir(mascara, campo, mensagem):
        if isinstance(mascara, pd.Series):
            indices = np.flatnonzero(mascara.fillna(False).to_numpy(dtype=bool))
        else:
            indices = np.flatnonzero(np.asarray(mascara, dtype=bool))
        for i in indices:
            erros.append({
                            'type': 'value_error',
                            'loc': ('tabela', int(i), campo),
                            'msg': f'Value error, {mensagem}',
                            'input': x.at[int(i), campo] if campo in x else None,
                            'ctx': {'error': ValueError(mensagem)},
                            'etapa': deslocamento,
                        })

    tipo = col('Cd_TP_AVAL')
    tuc = col('Nr_TUC')
    a1 = col('Nr_A1')
    sis = col('Cd_SISBASE')
    oat = col('FLG_OAT')
    elg = col("FLG_ELIG")
    conc = col("Cd_CONC")

    emitir(tipo.eq('2') & (sis.eq('') | sis.eq('NA')) & elg.eq('1') & conc.isin(['1', '3']),
           'Cd_SISBASE', 'Cd_SISBASE obrigatório quando Cd_TP_AVAL é 2 (BPR)')
    emitir(tipo.eq('2') & oat.eq('1') & elg.eq('1') & conc.isin(['1', '3']), 'FLG_OAT',
           'Obra avaliada por BPR não pode ser atípica')

    infra0, infrapar, orca0, ipca = referencias_incr(str(pasta))
    pares = pd.MultiIndex.from_arrays([tuc, a1])
    infraestrutura = tuc.isin(infra0) | pd.Series(pares.isin(infrapar), index=x.index)
    emitir(infraestrutura & tipo.ne('1') & elg.eq('1') & conc.isin(['1', '3']), 'Cd_TP_AVAL',
           'Registro de infraestrutura exige Cd_TP_AVAL igual a 1')
    emitir(tuc.isin(orca0) & tipo.ne('4') & elg.eq('1') & conc.isin(['1', '3']), 'Cd_TP_AVAL',
           'Registro de orçamento exige Cd_TP_AVAL igual a 4')

    vnr, iai = num('VL_VNR_UC'), num('VL_IAI_UC')
    emitir(vnr.gt(0) & iai.div(vnr).add(0.000001).gt(0.2), 'VL_IAI_UC',
           'Não aproveitamento do ativo superior a 20% do VNR')

    dt_imob = pd.to_datetime(col('Dt_Imob'), errors='coerce', dayfirst=True)
    dt_ref = pd.to_datetime(col('Dt_REF_DADOS'), errors='coerce', dayfirst=True)
    if dt_fim is not None:
        limite_data = pd.to_datetime(dt_fim, dayfirst=True)
        emitir(dt_ref.notna() & dt_ref.gt(limite_data), 'Dt_REF_DADOS',
               'Data de referência posterior à data final do trabalho')
    qtd, voc = num('Qtd_AIS'), num('VL_VOC')
    especial = tuc.isin(TUC_IPCA)

    emitir(especial & dt_ref.notna() & dt_imob.notna() & dt_ref.lt(dt_imob),
           'Dt_REF_DADOS', 'Data de referência anterior à data de imobilização')

    emitir(especial & qtd.notna() & qtd.le(0), 'Qtd_AIS',
           'Quantidade deve ser positiva para cálculo de atualização monetária')

    campos_voc = (
                    'VL_VOC_VF',
                    'VL_VOC_COM',
                    'VL_VOC_CA',
                    'VL_VOC_JOA',
                )

    campos_aval = (
                        'VL_VOC_VF_AVAL',
                        'VL_VOC_COM_AVAL',
                        'VL_VOC_CA_AVAL',
                        'VL_VOC_JOA_AVAL',
                    )

    voc = num('VL_VOC')
    componentes_voc = pd.DataFrame(
                                        {campo: num(campo) for campo in campos_voc},
                                        index=x.index
                                    )

    componentes_aval = pd.DataFrame(
                                        {campo: num(campo) for campo in campos_aval},
                                        index=x.index
                                    )
    emitir(
                voc.lt(0),
                'VL_VOC',
                'VL_VOC não pode ser negativo'
            )


    for campo in campos_voc:
        emitir(
                    componentes_voc[campo].lt(0),
                    campo,
                    f'{campo} não pode ser negativo'
                )
    for campo in campos_aval:
        emitir(
                    componentes_aval[campo].lt(0),
                    campo,
                    f'{campo} não pode ser negativo'
                )
    validos_voc = (
                        voc.notna()
                        & componentes_voc.notna().all(axis=1)
                        & componentes_voc.ge(0).all(axis=1)
                        & voc.ge(0)
                    )    
    soma_voc = componentes_voc.sum(axis=1, min_count=4)
    tolerancia = 0.01
    emitir(
                validos_voc
                & (voc - soma_voc).abs().gt(tolerancia),
                'VL_VOC',
                'VL_VOC difere da soma de VL_VOC_VF, '
                'VL_VOC_COM, VL_VOC_CA e VL_VOC_JOA'
            )
    validos_aval = (
                        voc.notna()
                        & voc.ge(0)
                        & componentes_aval.notna().all(axis=1)
                        & componentes_aval.ge(0).all(axis=1)
                    )
    soma_aval = componentes_aval.sum(axis=1, min_count=4)

    emitir(
                validos_aval
                & soma_aval.gt(voc + tolerancia),
                'VL_VOC',
                'Soma dos componentes avaliados '
                '(VL_VOC_*_AVAL) superior a VL_VOC'
            )
    
    elegiveis = especial & dt_imob.notna() & dt_ref.notna() & dt_ref.ge(dt_imob) & qtd.gt(0) & voc.notna()
    ids = np.flatnonzero(elegiveis.to_numpy(dtype=bool))
    if len(ids):
        base = pd.DataFrame({'idx': ids, 'ini': dt_imob.iloc[ids].to_numpy(),
                             'ref': dt_ref.iloc[ids].to_numpy()})
        tabela = ipca[['Dt_REF', 'Nr_IPCA']].rename(columns={'Dt_REF': 'data', 'Nr_IPCA': 'indice'})
        ini = pd.merge_asof(base[['idx', 'ini']].sort_values('ini'),
                            tabela.rename(columns={'data': 'ini'}), on='ini', direction='backward')
        ref = pd.merge_asof(base[['idx', 'ref']].sort_values('ref'),
                            tabela.rename(columns={'data': 'ref'}), on='ref', direction='backward')
        fatores = (ini[['idx', 'indice']].rename(columns={'indice': 'ipca_ini'})
                   .merge(ref[['idx', 'indice']].rename(columns={'indice': 'ipca_ref'}), on='idx'))
        indices_invalidos = fatores['ipca_ini'].isna() | fatores['ipca_ref'].isna() | fatores['ipca_ini'].le(0)
        mascara = pd.Series(False, index=x.index)
        mascara.iloc[fatores.loc[indices_invalidos, 'idx'].to_numpy(dtype=int)] = True
        emitir(mascara, 'Dt_REF_DADOS', 'Índice IPCA ausente ou inválido para o período')
        ok = fatores.loc[~indices_invalidos].copy()
        if not ok.empty:
            idx = ok['idx'].to_numpy(dtype=int)
            atualizado = (voc.iloc[idx].to_numpy() / qtd.iloc[idx].to_numpy()
                          * ok['ipca_ref'].to_numpy() / ok['ipca_ini'].to_numpy())
            limite = np.where(tuc.iloc[idx].eq('535').to_numpy(),
                              ok['ipca_ref'].to_numpy() * 5000 / 3403.73, 1200.0)
            mascara = pd.Series(False, index=x.index)
            mascara.iloc[idx[atualizado < limite]] = True
            emitir(mascara, 'VL_VOC', 'Valor atualizado pelo IPCA inferior ao limite aplicável')

    return erros, ipca

class ValoresBPR(Enum):
    A1=('BCS301', '1'),
    A2=('BCS302', '2'),
    A3=('BCS303', '3'),
    A4=('BCS304', '4'),
    A5=('BCS305', '5'),
    A6=('BCS306', '6'),
    A7=('BCS307', '7'),
    A8=('BCS308', '8'),
    A9=('BCS309', '9'),
    A10=('BCS310', '10'),
    A11=('CHS301', '11'),
    A12=('CHS302', '12'),
    A13=('CHS303', '13'),
    A14=('CHS304', '14'),
    A15=('CCO301', '15'),
    A16=('CFR301', '16'),
    A17=('CHS305', '17'),
    A18=('CHS306', '18'),
    A19=('CHS307', '19'),
    A20=('CHS308', '20'),
    A21=('CCO302', '21'),
    A22=('CFR302', '22'),
    A23=('DSJ301', '23'),
    A24=('DSJ302', '24'),
    A25=('DSJ303', '25'),
    A26=('DSJ304', '26'),
    A27=('DSJ305', '27'),
    A28=('DSJ306', '28'),
    A29=('DSJ307', '29'),
    A30=('DSJ308', '30'),
    A31=('DSJ309', '31'),
    A32=('DSJ310', '32'),
    A33=('DSJ311', '33'),
    A34=('DSJ312', '34'),
    A35=('DSJ313', '35'),
    A36=('DSJ314', '36'),
    A37=('LUM301', '37'),
    A38=('PRS301', '38'),
    A39=('PRS302', '39'),
    A40=('PRR301', '40'),
    A41=('REA301', '41'),
    A42=('REA302', '42'),
    A43=('REA303', '43'),
    A44=('REA304', '44'),
    A45=('RGS301', '45'),
    A46=('RGS302', '46'),
    A47=('RGS303', '47'),
    A48=('RGS304', '48'),
    A49=('RLS301', '49'),
    A50=('RLS302', '50'),
    A51=('TRA301', '51'),
    A52=('TSA301', '52'),
    A53=('TSA302', '53'),
    A54=('LUM311', '54'),
    A55=('PRS303', '55'),
    A56=('PRS304', '56'),
    A57=('PRR302', '57'),
    A58=('REA305', '58'),
    A59=('REA306', '59'),
    A60=('REA307', '60'),
    A61=('REA308', '61'),
    A62=('RGS305', '62'),
    A63=('RGS306', '63'),
    A64=('RGS307', '64'),
    A65=('RGS308', '65'),
    A66=('RLS303', '66'),
    A67=('RLS304', '67'),
    A68=('TRA302', '68'),
    A69=('TSA303', '69'),
    A70=('TSA304', '70'),
    A71=('CDL301', '71'),
    A72=('CDL302', '72'),
    A73=('CDL303', '73'),
    A74=('CDL304', '74'),
    A75=('CDL305', '75'),
    A76=('CDL306', '76'),
    A77=('CDL307', '77'),
    A78=('CDL308', '78'),
    A79=('CDL309', '79'),
    A80=('CDL310', '80'),
    A81=('CDL311', '81'),
    A82=('CDL312', '82'),
    A83=('CDL313', '83'),
    A84=('CDL314', '84'),
    A85=('CDL315', '85'),
    A86=('CDL316', '86'),
    A87=('CDL317', '87'),
    A88=('CDL318', '88'),
    A89=('CDL319', '89'),
    A90=('CDL320', '90'),
    A91=('PST301', '91'),
    A92=('PST302', '92'),
    A93=('PST303', '93'),
    A94=('PST304', '94'),
    A95=('PST305', '95'),
    A96=('PST306', '96'),
    A97=('PST307', '97'),
    A98=('PST308', '98'),
    A99=('PST309', '99'),
    A100=('PST310', '100'),
    A101=('PST311', '101'),
    A102=('PST312', '102'),
    A103=('PST313', '103'),
    A104=('PST314', '104'),
    A105=('PST315', '105'),
    A106=('PST316', '106'),
    A107=('PST317', '107'),
    A108=('PST318', '108'),
    A109=('TRF301', '109'),
    A110=('TRF302', '110'),
    A111=('TRF303', '111'),
    A112=('TRF304', '112'),
    A113=('TRF305', '113'),
    A114=('TRF306', '114'),
    A115=('TRF307', '115'),
    A116=('TRF308', '116'),
    A117=('TRF309', '117'),
    A118=('TRF310', '118'),
    A119=('TMS301', '119'),
    A120=('TMS302', '120'),
    A121=('TMS303', '121'),
    A122=('TMS304', '122'),
    A123=('TMS305', '123'),
    A124=('TMS306', '124'),
    A125=('TMS307', '125'),
    A126=('TMS308', '126'),
    A127=('TMS309', '127'),
    A128=('TMS310', '128'),
    A129=('TMS311', '129'),
    A130=('TMS312', '130'),
    A131=('TMS313', '131'),
    A132=('TMS314', '132'),
    A133=('TMS315', '133'),
    A134=('TMS316', '134'),
    A135=('TMS317', '135'),
    A136=('TMS318', '136'),
    A137=('TMS319', '137'),
    A138=('TMS320', '138'),
    A139=('TMS321', '139'),
    A140=('TMS322', '140'),
    A141=('TMS323', '141'),
    A142=('TMS324', '142'),
    A143=('TMS325', '143'),
    A144=('TMS326', '144'),
    A145=('TMS327', '145'),
    A146=('TMS328', '146'),
    A147=('TMS329', '147'),
    A148=('TMS330', '148'),
    A149=('TMS331', '149'),
    A150=('TMS332', '150'),
    A151=('TMS333', '151'),
    A152=('TMS334', '152'),
    A153=('TMS335', '153'),
    A154=('TMS336', '154'),
    A155=('TMS337', '155'),
    A156=('TMS338', '156'),
    A157=('TMS339', '157'),
    A158=('TMS340', '158'),
    A159=('TMS341', '159'),
    A160=('TMS342', '160'),
    A161=('TMS343', '161'),
    A162=('TMS344', '162'),
    A163=('TMS345', '163'),
    A164=('TMS346', '164'),
    A165=('TMS347', '165'),
    A166=('TMS348', '166'),
    A167=('MRD401', '167'),
    A168=('MRD402', '168'),
    A169=('MRD403', '169'),
    A170=('MRD404', '170'),
    A171=('MRD405', '171'),
    A172=('MRD406', '172'),
    A173=('MRD407', '173'),
    A174=('MRD408', '174'),
    A175=('MRD409', '175'),
    A176=('MRD410', '176'),
    A177=('MRD411', '177'),
    A178=('MRD412', '178'),
    A179=('MRD413', '179'),
    A180=('MRD414', '180'),
    A181=('MRD415', '181'),
    A182=('MRD416', '182'),
    A183=('MRD417', '183'),
    A184=('MRD418', '184'),
    A185=('CDR401', '185'),
    A186=('CDR402', '186'),
    A187=('CDR403', '187'),
    A188=('CDR404', '188'),
    A189=('CDR405', '189'),
    A190=('CDR406', '190'),
    A191=('CDR407', '191'),
    A192=('CDR408', '192'),
    A193=('CDR409', '193'),
    A194=('CDR410', '194'),
    A195=('CDR411', '195'),
    A196=('CDR412', '196'),
    A197=('CDR413', '197'),
    A198=('CDR414', '198'),
    A199=('CDR415', '199'),
    A200=('CDR416', '200'),
    A201=('CDR417', '201'),
    A202=('CDR418', '202'),
    A203=('CDR419', '203'),
    A204=('CDR420', '204'),
    A205=('CDR421', '205'),
    A206=('CDR422', '206'),
    A207=('TMS401', '207'),
    A208=('TMS402', '208'),
    A209=('TMS403', '209'),
    A210=('TMS411', '210'),
    A211=('TMS412', '211'),
    A212=('TMS413', '212'),
    A213=('CDR101', '213'),
    A214=('CDR102', '214'),
    A215=('CDR103', '215'),
    A216=('CDR104', '216'),
    A217=('CDR105', '217'),
    A218=('CDR106', '218'),
    A219=('CDR107', '219'),
    A220=('CDR108', '220'),
    A221=('CDR109', '221'),
    A222=('CDR110', '222'),
    A223=('CDR111', '223'),
    A224=('CDR112', '224'),
    A225=('CDR113', '225'),
    A226=('CDR114', '226'),
    A227=('CDR115', '227'),
    A228=('CDR116', '228'),
    A229=('CDR117', '229'),
    A230=('CDR118', '230'),
    A231=('CDR119', '231'),
    A232=('CDR120', '232'),
    A233=('CDR121', '233'),
    A234=('CDR122', '234'),
    A235=('PST101', '235'),
    A236=('PST102', '236'),
    A237=('PST103', '237'),
    A238=('PST104', '238'),
    A239=('PST105', '239'),
    A240=('PST106', '240'),
    A241=('PST107', '241'),
    A242=('PST108', '242'),
    A243=('PST109', '243'),
    A244=('PST110', '244'),
    A245=('PST111', '245'),
    A246=('PST112', '246'),
    A247=('PST113', '247'),
    A248=('PST114', '248'),
    A249=('PST115', '249'),
    A250=('PST116', '250'),
    A251=('PST117', '251'),
    A252=('PST118', '252'),
    A253=('TRD101', '253'),
    A254=('TRD102', '254'),
    A255=('TRD103', '255'),
    A256=('TRD104', '256'),
    A257=('TRD105', '257'),
    A258=('TRD106', '258'),
    A259=('TRD107', '259'),
    A260=('TRD108', '260'),
    A261=('TRD109', '261'),
    A262=('TRD110', '262'),
    A263=('TRD111', '263'),
    A264=('TRD112', '264'),
    A265=('TRD113', '265'),
    A266=('TRD114', '266'),
    A267=('TRD115', '267'),
    A268=('TRD116', '268'),
    A269=('TRD117', '269'),
    A270=('TRD118', '270'),
    A271=('BNC101', '271'),
    A272=('CHV101', '272'),
    A273=('CHV102', '273'),
    A274=('CHV103', '274'),
    A275=('LUM101', '275'),
    A276=('PRS101', '276'),
    A277=('PRR101', '277'),
    A278=('REG101', '278'),
    A279=('REL101', '279'),
    A280=('REL102', '280'),
    A281=('BNC111', '281'),
    A282=('CHV111', '282'),
    A283=('CHV112', '283'),
    A284=('CHV113', '284'),
    A285=('LUM111', '285'),
    A286=('PRS111', '286'),
    A287=('PRR111', '287'),
    A288=('REG111', '288'),
    A289=('REL111', '289'),
    A290=('REL112', '290'),
    A291=('CDL201', '291'),
    A292=('CDL202', '292'),
    A293=('CDL203', '293'),
    A294=('CDL204', '294'),
    A295=('CDL205', '295'),
    A296=('CDL206', '296'),
    A297=('CDL207', '297'),
    A298=('CDL208', '298'),
    A299=('CDL209', '299'),
    A300=('CDL210', '300'),
    A301=('CDL211', '301'),
    A302=('CDL212', '302'),
    A303=('CDL213', '303'),
    A304=('CDL214', '304'),
    A305=('CDL215', '305'),
    A306=('CDL216', '306'),
    A307=('CDL217', '307'),
    A308=('CDL218', '308'),
    A309=('CDL219', '309'),
    A310=('CDL220', '310'),
    A311=('BNC201', '311'),
    A312=('CHV201', '312'),
    A313=('CHV202', '313'),
    A314=('CHV203', '314'),
    A315=('CHV204', '315'),
    A316=('PRS201', '316'),
    A317=('PRS202', '317'),
    A318=('REG201', '318'),
    A319=('REG202', '319'),
    A320=('REG203', '320'),
    A321=('REG204', '321'),
    A322=('REL201', '322'),
    A323=('REL202', '323'),
    A324=('TMS201', '324'),
    A325=('TMS202', '325'),
    A326=('TMS203', '326'),
    A327=('TMS204', '327'),
    A328=('BNC202', '328'),
    A329=('CHV205', '329'),
    A330=('CHV206', '330'),
    A331=('CHV207', '331'),
    A332=('CHV208', '332'),
    A333=('PRS203', '333'),
    A334=('PRS204', '334'),
    A335=('REG205', '335'),
    A336=('REG206', '336'),
    A337=('REG207', '337'),
    A338=('REG208', '338'),
    A339=('REL203', '339'),
    A340=('REL204', '340'),
    A341=('TMS205', '341'),
    A342=('TMS206', '342'),
    A343=('TMS207', '343'),
    A344=('TMS208', '344'),
    
    def __new__(cls, valor):
        codigo, descricao = valor 
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def descricao(self) -> str:
        return self._descricao

    @classmethod
    def teste(cls, codigo: str) -> bool:
        """Verifica se um código está presente no Enum."""
        return codigo in cls._codigos()

    @classmethod
    def descricao_por_codigo(cls, codigo: str) -> str | None:
        """Retorna a descrição associada a um código."""
        return cls._mapa().get(codigo)

    @classmethod
    def _mapa(cls) -> dict[str, str]:
        """Retorna um dicionário {codigo: descricao}, cacheado."""
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache

    @classmethod
    def _codigos(cls) -> set[str]:
        """Retorna todos os códigos válidos."""
        return set(cls._mapa().keys())

class ValoresCMUst(Enum):
    A1 = ('1' , 'VL_ST_ChFus_RAR_Unit', 'Valor de instalação de chave fusível em rede aérea rural'),
    A2 = ('2' , 'VL_ST_ChFus_RAU_Unit', 'Valor de instalação de chave fusível em rede aérea urbana'),
    A3 = ('3' , 'VL_ST_Crzta_RAR_Unit', 'Valor de instalação de cruzeta em rede aérea rural'),
    A4 = ('4' , 'VL_ST_Crzta_RAU_Unit', 'Valor de instalação de cruzeta em rede aérea urbana'),
    A5 = ('5' , 'VL_ST_Haste_RAR_Unit', 'Valor de instalação de haste de aterramento em rede aérea rural'),
    A6 = ('6' , 'VL_ST_Haste_RAU_Unit', 'Valor de instalação de haste de aterramento em rede aérea urbana'),
    A7 = ('7' , 'VL_ST_Isol_Dis_RAR_Unit', 'Valor de instalação de isolador de disco em rede aérea rural'),
    A8 = ('8' , 'VL_ST_Isol_Dis_RAU_Unit', 'Valor de instalação de isolador de disco em rede aérea urbana'),
    A9 = ('9' , 'VL_ST_Isol_Pin_RAR_Unit', 'Valor de instalação de isolador de pino em rede aérea rural'),
    A10 = ('10' , 'VL_ST_Isol_Pin_RAU_Unit', 'Valor de instalação de isolador de pino em rede aérea urbana'),
    A11 = ('11' , 'VL_ST_Pin_RAR_Unit', 'Valor de instalação de pino em rede aérea rural'),
    A12 = ('12' , 'VL_ST_Pin_RAU_Unit', 'Valor de instalação de pino em rede aérea urbana'),
    A13 = ('13' , 'VL_ST_Praio_RAR_Unit', 'Valor de instalação de para-raio em rede aérea rural'),
    A14 = ('14' , 'VL_ST_Praio_RAU_Unit', 'Valor de instalação de para-raio em rede aérea urbana'),
    
    @classmethod
    def teste(cls, nro):
        for valor in cls:
            if valor.value[0][0] == nro:
                return True
        return False

class ValoresCFOP(Enum):
    A1 = ('1000','ENTRADAS OU AQUISIÇÕES DE SERVIÇOS DO ESTADO'),
    A2 = ('1100','COMPRAS PARA INDUSTRIALIZAÇÃO, PRODUÇÃO RURAL, COMERCIALIZAÇÃO OU PRESTAÇÃO DE SERVIÇOS'),
    A3 = ('1101','Compra para industrialização ou produção rural (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A4 = ('1102','Compra para comercialização'),
    A5 = ('1111','Compra para industrialização de mercadoria recebida anteriormente em consignação industrial'),
    A6 = ('1113','Compra para comercialização, de mercadoria recebida anteriormente em consignação mercantil'),
    A7 = ('1116','Compra para industrialização ou produção rural originada de encomenda para recebimento futuro (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A8 = ('1117','Compra para comercialização originada de encomenda para recebimento futuro'),
    A9 = ('1118','Compra de mercadoria para comercialização pelo adquirente origin rio, entregue pelo vendedor remetente ao destinat rio, em venda à ordem.'),
    A10 = ('1120','Compra para industrialização, em venda à ordem, j  recebida do vendedor remetente'),
    A11 = ('1121','Compra para comercialização, em venda à ordem, j  recebida do vendedor remetente'),
    A12 = ('1122','Compra para industrialização em que a mercadoria foi remetida pelo fornecedor ao industrializador sem transitar pelo estabelecimento adquirente'),
    A13 = ('1124','Industrialização efetuada por outra empresa'),
    A14 = ('1125','Industrialização efetuada por outra empresa quando a mercadoria remetida para utilização no processo de industrialização não transitou pelo estabelecimento adquirente da mercadoria'),
    A15 = ('1126','Compra para utilização na prestação de serviço sujeita ao ICMS (AJUSTE SINIEF 4, DE 9 DE JULHO DE 2010) - DECRETO 36.465/2011'),
    A16 = ('1128','Compra para utilização na prestação de serviço sujeita ao ISSQN(AJUSTE SINIEF 4, DE 9 DE JULHO DE 2010) efeitos a partir de 1§ de janeiro de 2011- DECRETO 36.465/2011'),
    A17 = ('1150','TRANSFERÊNCIAS PARA INDUSTRIALIZAÇÃO, PRODUÇÃO RURAL, COMERCIALIZAÇÃO OU PRESTAÇÃO DE SERVIÇOS (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A18 = ('1151','Transferˆncia para industrialização ou produção rural (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A19 = ('1152','Transferência para comercialização'),
    A20 = ('1153','Transferência de energia elétrica para distribuição'),
    A21 = ('1154','Transferência para utilização na prestação de serviço'),
    A22 = ('1200','DEVOLUÇÕES DE VENDAS DE PRODUÇÃO DO ESTABELECIMENTO, DE PRODUTOS DE TERCEIROS OU ANULAÇÕES DE VALORES'),
    A23 = ('1201','Devolução de venda de produção do estabelecimento'),
    A24 = ('1202','Devolução de venda de mercadoria adquirida ou recebida de terceiros'),
    A25 = ('1203','Devolução de venda de produção do estabelecimento, destinada à Zona Franca de Manaus ou µreas de Livre Com‚rcio'),
    A26 = ('1204','Devolução de venda de mercadoria adquirida ou recebida de terceiros, destinada à Zona Franca de Manaus ou µreas de Livre Com‚rcio'),
    A27 = ('1205','Anulação de valor relativo à prestação de serviço de comunicação'),
    A28 = ('1206','Anulação de valor relativo à prestação de serviço de transporte'),
    A29 = ('1207','Anulação de valor relativo à venda de energia elétrica'),
    A30 = ('1208','Devolução de produção do estabelecimento, remetida em Transferência'),
    A31 = ('1209','Devolução de mercadoria adquirida ou recebida de terceiros, remetida em Transferência'),
    A32 = ('1250','COMPRAS DE ENERGIA ELTRICA'),
    A33 = ('1251','Compra de energia elétrica para distribuição ou comercialização'),
    A34 = ('1252','Compra de energia elétrica por estabelecimento industrial'),
    A35 = ('1253','Compra de energia elétrica por estabelecimento comercial'),
    A36 = ('1254','Compra de energia elétrica por estabelecimento prestador de serviço de transporte'),
    A37 = ('1255','Compra de energia elétrica por estabelecimento prestador de serviço de comunicação'),
    A38 = ('1256','Compra de energia elétrica por estabelecimento de produtor rural'),
    A39 = ('1257','Compra de energia elétrica para consumo por demanda contratada'),
    A40 = ('1300','AQUISIÇÕES DE SERVIÇOS DE COMUNICAÇÃO'),
    A41 = ('1301','Aquisição de serviço de comunicação para execução de serviço da mesma natureza'),
    A42 = ('1302','Aquisição de serviço de comunicação por estabelecimento industrial'),
    A43 = ('1303','Aquisição de serviço de comunicação por estabelecimento comercial'),
    A44 = ('1304','Aquisição de serviço de comunicação por estabelecimento de prestador de serviço de transporte'),
    A45 = ('1305','Aquisição de serviço de comunicação por estabelecimento de geradora ou de distribuidora de energia elétrica'),
    A46 = ('1306','Aquisição de serviço de comunicação por estabelecimento de produtor rural'),
    A47 = ('1350','AQUISIÇÕES DE SERVIÇOS DE TRANSPORTE'),
    A48 = ('1351','Aquisição de serviço de transporte para execução de serviço da mesma natureza'),
    A49 = ('1352','Aquisição de serviço de transporte por estabelecimento industrial'),
    A50 = ('1353','Aquisição de serviço de transporte por estabelecimento comercial'),
    A51 = ('1354','Aquisição de serviço de transporte por estabelecimento de prestador de serviço de comunicação'),
    A52 = ('1355','Aquisição de serviço de transporte por estabelecimento de geradora ou de distribuidora de energia elétrica'),
    A53 = ('1356','Aquisição de serviço de transporte por estabelecimento de produtor rural'),
    A54 = ('1360','Aquisição de serviço de transporte por contribuinte-substituto em relação ao serviço de transporte (ACR) (Ajuste SINIEF 06/2007- Decreto n§ 30.861/2007) ?? a partir de 01.01.2008'),
    A55 = ('1400','ENTRADAS DE MERCADORIAS SUJEITAS AO REGIME DE SUBSTITUIÇÃO TRIBUTµRIA'),
    A56 = ('1401','Compra para industrialização ou produção rural de mercadoria sujeita ao regime de substituição tribut ria (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A57 = ('1403','Compra para comercialização em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A58 = ('1406','Compra de bem para o ativo imobilizado cuja mercadoria est  sujeita ao regime de substituição tribut ria'),
    A59 = ('1407','Compra de mercadoria para uso ou consumo cuja mercadoria est  sujeita ao regime de substituição tribut ria'),
    A60 = ('1408','Transferência para industrialização ou produção rural de mercadoria sujeita ao regime de substituição tribut ria (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A61 = ('1409','Transferência para comercialização em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A62 = ('1410','Devolução de venda de mercadoria, de produção do estabelecimento, sujeita ao regime de substituição tribut ria'),
    A63 = ('1411','Devolução de venda de mercadoria adquirida ou recebida de terceiros em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A64 = ('1414','Retorno de mercadoria de produção do estabelecimento, remetida para venda fora do estabelecimento, sujeita ao regime de substituição tribut ria'),
    A65 = ('1415','Retorno de mercadoria adquirida ou recebida de terceiros, remetida para venda fora do estabelecimento em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A66 = ('1450','SISTEMAS DE INTEGRAÇÃO'),
    A67 = ('1451','Retorno de animal do estabelecimento produtor'),
    A68 = ('1452','Retorno de insumo não utilizado na produção'),
    A69 = ('1500','ENTRADAS DE MERCADORIAS REMETIDAS PARA FORMAÇÃO DE LOTE OU COM FIM ESPECÍFICO DE EXPORTAÇÃO E EVENTUAIS DEVOLUÇÕES (NR Ajuste SINIEF 09/2005)'),
    A70 = ('1501','Entrada de mercadoria recebida com fim específico de exportação'),
    A71 = ('1503','Entrada decorrente de devolução de produto, de fabricação do estabelecimento, remetido com fim específico de exportação'),
    A72 = ('1504','Entrada decorrente de devolução de mercadoria remetida com fim específico de exportação, adquirida ou recebida de terceiros'),
    A73 = ('1505','Entrada decorrente de devolução simbólica de mercadoria remetida para formação de lote de exportação, de produto industrializado ou produzido pelo pr¢prio estabelecimento.'),
    A74 = ('1506','Entrada decorrente de devolução simbólica de mercadoria, adquirida ou recebida de terceiros, remetida para formação de lote de exportação.'),
    A75 = ('1550','OPERAÇÕES COM BENS DE ATIVO IMOBILIZADO E MATERIAIS PARA USO OU CONSUMO'),
    A76 = ('1551','Compra de bem para o ativo imobilizado'),
    A77 = ('1552','Transferência de bem do ativo imobilizado'),
    A78 = ('1553','Devolução de venda de bem do ativo imobilizado'),
    A79 = ('1554','Retorno de bem do ativo imobilizado remetido para uso fora do estabelecimento'),
    A80 = ('1555','Entrada de bem do ativo imobilizado de terceiro, remetido para uso no estabelecimento'),
    A81 = ('1556','Compra de material para uso ou consumo'),
    A82 = ('1557','Transferência de material para uso ou consumo'),
    A83 = ('1600','CRÉDITOS E RESSARCIMENTOS DE ICMS'),
    A84 = ('1601','Recebimento, por Transferência, de cr‚dito de ICMS'),
    A85 = ('1602','Recebimento, por Transferência, de saldo credor do ICMS, de outro estabelecimento da mesma empresa, para compensação de saldo devedor do imposto.'),
    A86 = ('1603','Ressarcimento de ICMS retido por substituição tribut ria'),
    A87 = ('1604','Lançamento do cr‚dito relativo à compra de bem para o ativo imobilizado'),
    A88 = ('1605','Recebimento, por Transferência, de saldo devedor do ICMS de outro estabelecimento da mesma empresa'),
    A89 = ('1650','ENTRADAS DE COMBUSTIVEIS, DERIVADOS OU NÇO DE PETRàLEO, E LUBRIFICANTES (ACR Ajuste SINIEF 9/2003 - a partir 01.01.2004)'),
    A90 = ('1651','Compra de combustível ou lubrificante para industrialização subseqente'),
    A91 = ('1652','Compra de combustível ou lubrificante para comercialização'),
    A92 = ('1653','Compra de combustível ou lubrificante por consumidor ou usu rio final'),
    A93 = ('1658','Transferência de combustível ou lubrificante para industrialização'),
    A94 = ('1659','Transferência de combustível ou lubrificante para comercialização'),
    A95 = ('1660','Devolução de venda de combustível ou lubrificante destinados à industrialização subseqente'),
    A96 = ('1661','Devolução de venda de combustível ou lubrificante destinados à comercialização'),
    A97 = ('1662','Devolução de venda de combustível ou lubrificante destinados a consumidor ou usu rio final'),
    A98 = ('1663','Entrada de combustível ou lubrificante para armazenagem'),
    A99 = ('1664','Retorno de combustível ou lubrificante remetidos para armazenagem'),
    A100 = ('1900','OUTRAS ENTRADAS DE MERCADORIAS OU AQUISIÇÕES DE SERVIÇOS'),
    A101 = ('1901','Entrada para industrialização por encomenda'),
    A102 = ('1902','Retorno de mercadoria remetida para industrialização por encomenda'),
    A103 = ('1903','Entrada de mercadoria remetida para industrialização e não aplicada no referido processo'),
    A104 = ('1904','Retorno de remessa para venda fora do estabelecimento'),
    A105 = ('1905','Entrada de mercadoria recebida para depósito em depósito fechado ou armazémgeral'),
    A106 = ('1906','Retorno de mercadoria remetida para depósito fechado ou armazémgeral'),
    A107 = ('1907','Retorno simbólico de mercadoria remetida para depósito fechado ou armazémgeral'),
    A108 = ('1908','Entrada de bem por conta de contrato de comodato'),
    A109 = ('1909','Retorno de bem remetido por conta de contrato de comodato'),
    A110 = ('1910','Entrada de bonificação, doação ou brinde'),
    A111 = ('1911','Entrada de amostra grátis'),
    A112 = ('1912','Entrada de mercadoria ou bem recebido para demonstração'),
    A113 = ('1913','Retorno de mercadoria ou bem remetido para demonstração'),
    A114 = ('1914','Retorno de mercadoria ou bem remetido para exposição ou feira'),
    A115 = ('1915','Entrada de mercadoria ou bem recebido para conserto ou reparo'),
    A116 = ('1916','Retorno de mercadoria ou bem remetido para conserto ou reparo'),
    A117 = ('1917','Entrada de mercadoria recebida em consignação mercantil ou industrial'),
    A118 = ('1918','Devolução de mercadoria remetida em consignação mercantil ou industrial'),
    A119 = ('1919','Devolução simbólica de mercadoria vendida ou utilizada em processo industrial, remetida anteriormente em consignação mercantil ou industrial'),
    A120 = ('1920','Entrada de vasilhame ou sacaria'),
    A121 = ('1921','Retorno de vasilhame ou sacaria'),
    A122 = ('1922','Lançamento efetuado a título de simples faturamento decorrente de compra para recebimento futuro'),
    A123 = ('1923','Entrada de mercadoria recebida do vendedor remetente, em venda à ordem'),
    A124 = ('1924','Entrada para industrialização por conta e ordem do adquirente da mercadoria, quando esta não transitar pelo estabelecimento do adquirente'),
    A125 = ('1925','Retorno de mercadoria remetida para industrialização por conta e ordem do adquirente da mercadoria, quando esta não transitar pelo estabelecimento do adquirente'),
    A126 = ('1926','Lançamento efetuado a título de reclassificação de mercadoria decorrente de formação de kit ou de sua desagregação'),
    A127 = ('1931','Lançamento efetuado pelo tomador do serviço de transporte, quando a responsabilidade de retenção do imposto for atribu¡da ao remetente ou alienante da mercadoria, pelo serviço de transporte realizado por transportador aut“nomo ou por transportador não-inscrito na Unidade da Federação onde se tenha iniciado o serviço.'),
    A128 = ('1932','Aquisição de serviço de transporte iniciado em Unidade da Federação diversa daquela onde esteja inscrito o prestador'),
    A129 = ('1933','Aquisição de serviço tributado pelo Imposto sobre serviços de Qualquer Natureza (Ajuste SINIEF 06/2005) (NR)'),
    A130 = ('1934','Entrada simbólica de mercadoria recebida para depósito fechado ou armazémgeral'),
    A131 = ('1949','Outra entrada de mercadoria ou prestação de serviço não especificada'),
    A132 = ('2000','ENTRADAS OU AQUISIÇÕES DE SERVIÇOS DE OUTROS ESTADOS'),
    A133 = ('2100','COMPRAS PARA INDUSTRIALIZAÇÃO, PRODUÇÃO RURAL, COMERCIALIZAÇÃO OU PRESTAÇÃO DE SERVIÇOS (NR Ajuste SINIEF 05/2005  (Decreto 28.868/2006)'),
    A134 = ('2101','Compra para industrialização ou produção rural (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A135 = ('2102','Compra para comercialização'),
    A136 = ('2111','Compra para industrialização de mercadoria recebida anteriormente em consignação industrial'),
    A137 = ('2113','Compra para comercialização, de mercadoria recebida anteriormente em consignação mercantil'),
    A138 = ('2116','Compra para industrialização ou produção rural originada de encomenda para recebimento futuro (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A139 = ('2117','Compra para comercialização originada de encomenda para recebimento futuro'),
    A140 = ('2118','Compra de mercadoria para comercialização pelo adquirente origin rio, entregue pelo vendedor remetente ao destinat rio, em venda à ordem'),
    A141 = ('2120','Compra para industrialização, em venda à ordem, j  recebida do vendedor remetente'),
    A142 = ('2121','Compra para comercialização, em venda à ordem, j  recebida do vendedor remetente'),
    A143 = ('2122','Compra para industrialização em que a mercadoria foi remetida pelo fornecedor ao industrializador sem transitar pelo estabelecimento adquirente'),
    A144 = ('2124','Industrialização efetuada por outra empresa'),
    A145 = ('2125','Industrialização efetuada por outra empresa quando a mercadoria remetida para utilização no processo de industrialização não transitou pelo estabelecimento adquirente da mercadoria'),
    A146 = ('2126','Compra para utilização na prestação de serviço sujeita ao ICMS (AJUSTE SINIEF 4, DE 9 DE JULHO DE 2010) - DECRETO 36.465/2011'),
    A147 = ('2128','Compra para utilização na prestação de serviço sujeita ao ISSQN(AJUSTE SINIEF 4, DE 9 DE JULHO DE 2010) efeitos a partir de 1§ de janeiro de 2011- DECRETO 36.465/2011'),
    A148 = ('2150','TRANSFERÊNCIAS PARA INDUSTRIALIZAÇÃO, PRODUÇÃO RURAL, COMERCIALIZAÇÃO OU PRESTAÇÃO DE SERVIÇOS (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A149 = ('2151','Transferência para industrialização ou produção rural (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A150 = ('2152','Transferência para comercialização'),
    A151 = ('2153','Transferência de energia elétrica para distribuição'),
    A152 = ('2154','Transferência para utilização na prestação de serviço'),
    A153 = ('2200','DEVOLUÇÕES DE VENDAS DE PRODUÇÃO DO ESTABELECIMENTO OU DE TERCEIROS OU ANULAÇÕES DE VALORES'),
    A154 = ('2201','Devolução de venda de produção do estabelecimento'),
    A155 = ('2202','Devolução de venda de mercadoria adquirida ou recebida de terceiros'),
    A156 = ('2203','Devolução de venda de produção do estabelecimento destinada à Zona Franca de Manaus ou µreas de Livre Com‚rcio'),
    A157 = ('2204','Devolução de venda de mercadoria adquirida ou recebida de terceiros, destinada à Zona Franca de Manaus ou µreas de Livre Com‚rcio'),
    A158 = ('2205','Anulação de valor relativo à prestação de serviço de comunicação'),
    A159 = ('2206','Anulação de valor relativo à prestação de serviço de transporte'),
    A160 = ('2207','Anulação de valor relativo à venda de energia elétrica'),
    A161 = ('2208','Devolução de produção do estabelecimento, remetida em Transferência.'),
    A162 = ('2209','Devolução de mercadoria adquirida ou recebida de terceiros e remetida em Transferência'),
    A163 = ('2250','COMPRAS DE ENERGIA ELÉTRICA'),
    A164 = ('2251','Compra de energia elétrica para distribuição ou comercialização'),
    A165 = ('2252','Compra de energia elétrica por estabelecimento industrial'),
    A166 = ('2253','Compra de energia elétrica por estabelecimento comercial'),
    A167 = ('2254','Compra de energia elétrica por estabelecimento prestador de serviço de transporte'),
    A168 = ('2255','Compra de energia elétrica por estabelecimento prestador de serviço de comunicação'),
    A169 = ('2256','Compra de energia elétrica por estabelecimento de produtor rural'),
    A170 = ('2257','Compra de energia elétrica para consumo por demanda contratada'),
    A171 = ('2300','AQUISIÇÕES DE SERVIÇOS DE COMUNICAÇÃO'),
    A172 = ('2301','Aquisição de serviço de comunicação para execução de serviço da mesma natureza'),
    A173 = ('2302','Aquisição de serviço de comunicação por estabelecimento industrial'),
    A174 = ('2303','Aquisição de serviço de comunicação por estabelecimento comercial'),
    A175 = ('2304','Aquisição de serviço de comunicação por estabelecimento de prestador de serviço de transporte'),
    A176 = ('2305','Aquisição de serviço de comunicação por estabelecimento de geradora ou de distribuidora de energia elétrica'),
    A177 = ('2306','Aquisição de serviço de comunicação por estabelecimento de produtor rural'),
    A178 = ('2350','AQUISIÇÕES DE SERVIÇOS DE TRANSPORTE'),
    A179 = ('2351','Aquisição de serviço de transporte para execução de serviço da mesma natureza'),
    A180 = ('2352','Aquisição de serviço de transporte por estabelecimento industrial'),
    A181 = ('2353','Aquisição de serviço de transporte por estabelecimento comercial'),
    A182 = ('2354','Aquisição de serviço de transporte por estabelecimento de prestador de serviço de comunicação'),
    A183 = ('2355','Aquisição de serviço de transporte por estabelecimento de geradora ou de distribuidora de energia elétrica'),
    A184 = ('2356','Aquisição de serviço de transporte por estabelecimento de produtor rural'),
    A185 = ('2400','ENTRADAS DE MERCADORIAS SUJEITAS AO REGIME DE SUBSTITUIÇÃO TRIBUTµRIA'),
    A186 = ('2401','Compra para industrialização ou produção rural de mercadoria sujeita ao regime de substituição tribut ria (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A187 = ('2403','Compra para comercialização em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A188 = ('2406','Compra de bem para o ativo imobilizado cuja mercadoria est  sujeita ao regime de substituição tribut ria'),
    A189 = ('2407','Compra de mercadoria para uso ou consumo cuja mercadoria est  sujeita ao regime de substituição tribut ria'),
    A190 = ('2408','Transferência para industrialização ou produção rural de mercadoria sujeita ao regime de substituição tribut ria (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A191 = ('2409','Transferência para comercialização em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A192 = ('2410','Devolução de venda de produção do estabelecimento, quando o produto estiver sujeito ao regime de substituição tribut ria'),
    A193 = ('2411','Devolução de venda de mercadoria adquirida ou recebida de terceiros em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A194 = ('2414','Retorno de produção do estabelecimento, remetida para venda fora do estabelecimento, quando o produto estiver sujeito ao regime de substituição tribut ria'),
    A195 = ('2415','Retorno de mercadoria adquirida ou recebida de terceiros, remetida para venda fora do estabelecimento em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A196 = ('2500','ENTRADAS DE MERCADORIAS REMETIDAS PARA FORMAÇÃO DE LOTE OU COM FIM ESPECÍFICO DE EXPORTAÇÃO E EVENTUAIS DEVOLUÇÕES (NR Ajuste SINIEF 09/2005)'),
    A197 = ('2501','Entrada de mercadoria recebida com fim específico de exportação'),
    A198 = ('2503','Entrada decorrente de devolução de produto industrializado pelo estabelecimento, remetido com fim específico de exportação'),
    A199 = ('2504','Entrada decorrente de devolução de mercadoria remetida com fim específico de exportação, adquirida ou recebida de terceiros'),
    A200 = ('2505','Entrada decorrente de devolução simbólica de mercadoria remetida para formação de lote de exportação, de produto industrializado ou produzido pelo pr¢prio estabelecimento.'),
    A201 = ('2506','Entrada decorrente de devolução simbólica de mercadoria, adquirida ou recebida de terceiros, remetida para formação de lote de exportação.'),
    A202 = ('2550','OPERAÇÕES COM BENS DE ATIVO IMOBILIZADO E MATERIAIS PARA USO OU CONSUMO'),
    A203 = ('2551','Compra de bem para o ativo imobilizado'),
    A204 = ('2552','Transferência de bem do ativo imobilizado'),
    A205 = ('2553','Devolução de venda de bem do ativo imobilizado'),
    A206 = ('2554','Retorno de bem do ativo imobilizado remetido para uso fora do estabelecimento'),
    A207 = ('2555','Entrada de bem do ativo imobilizado de terceiro, remetido para uso no estabelecimento'),
    A208 = ('2556','Compra de material para uso ou consumo'),
    A209 = ('2557','Transferência de material para uso ou consumo'),
    A210 = ('2600','CRÉDITOS E RESSARCIMENTOS DE ICMS'),
    A211 = ('2603','Ressarcimento de ICMS retido por substituição tribut ria'),
    A212 = ('2650','ENTRADAS DE COMBUSTIVEIS, DERIVADOS OU NÇO DE PETRàLEO, E LUBRIFICANTES (ACR Ajuste SINIEF 9/2003)'),
    A213 = ('2651','Compra de combustível ou lubrificante para industrialização subseqente'),
    A214 = ('2652','Compra de combustível ou lubrificante para comercialização'),
    A215 = ('2652','Compra de combustível ou lubrificante para comercialização'),
    A216 = ('2653','Compra de combustível ou lubrificante por consumidor ou usu rio final'),
    A217 = ('2658','Transferência de combustível ou lubrificante para industrialização'),
    A218 = ('2659','Transferência de combustível ou lubrificante para comercialização'),
    A219 = ('2660','Devolução de venda de combustível ou lubrificante destinados à industrialização subseqente'),
    A220 = ('2661','Devolução de venda de combustível ou lubrificante destinados à comercialização'),
    A221 = ('2662','Devolução de venda de combustível ou lubrificante destinados a consumidor ou usu rio final'),
    A222 = ('2663','Entrada de combustível ou lubrificante para armazenagem'),
    A223 = ('2664','Retorno de combustível ou lubrificante remetidos para armazenagem'),
    A224 = ('2900','OUTRAS ENTRADAS DE MERCADORIAS OU AQUISIÇÕES DE SERVIÇOS'),
    A225 = ('2901','Entrada para industrialização por encomenda'),
    A226 = ('2902','Retorno de mercadoria remetida para industrialização por encomenda'),
    A227 = ('2903','Entrada de mercadoria remetida para industrialização e não aplicada no referido processo'),
    A228 = ('2904','Retorno de remessa para venda fora do estabelecimento'),
    A229 = ('2905','Entrada de mercadoria recebida para depósito em depósito fechado ou armazémgeral'),
    A230 = ('2906','Retorno de mercadoria remetida para depósito fechado ou armazémgeral'),
    A231 = ('2907','Retorno simbólico de mercadoria remetida para depósito fechado ou armazémgeral'),
    A232 = ('2908','Entrada de bem por conta de contrato de comodato'),
    A233 = ('2909','Retorno de bem remetido por conta de contrato de comodato'),
    A234 = ('2910','Entrada de bonificação, doação ou brinde'),
    A235 = ('2911','Entrada de amostra grátis'),
    A236 = ('2912','Entrada de mercadoria ou bem recebido para demonstração'),
    A237 = ('2913','Retorno de mercadoria ou bem remetido para demonstração'),
    A238 = ('2914','Retorno de mercadoria ou bem remetido para exposição ou feira'),
    A239 = ('2915','Entrada de mercadoria ou bem recebido para conserto ou reparo'),
    A240 = ('2916','Retorno de mercadoria ou bem remetido para conserto ou reparo'),
    A241 = ('2917','Entrada de mercadoria recebida em consignação mercantil ou industrial'),
    A242 = ('2918','Devolução de mercadoria remetida em consignação mercantil ou industrial'),
    A243 = ('2919','Devolução simbólica de mercadoria vendida ou utilizada em processo industrial, remetida anteriormente em consignação mercantil ou industrial'),
    A244 = ('2920','Entrada de vasilhame ou sacaria'),
    A245 = ('2921','Retorno de vasilhame ou sacaria'),
    A246 = ('2922','Lançamento efetuado a título de simples faturamento decorrente de compra para recebimento futuro'),
    A247 = ('2923','Entrada de mercadoria recebida do vendedor remetente, em venda à ordem'),
    A248 = ('2924','Entrada para industrialização por conta e ordem do adquirente da mercadoria, quando esta não transitar pelo estabelecimento do adquirente'),
    A249 = ('2925','Retorno de mercadoria remetida para industrialização por conta e ordem do adquirente da mercadoria, quando esta não transitar pelo estabelecimento do adquirente'),
    A250 = ('2931','Lançamento efetuado pelo tomador do serviço de transporte, quando a responsabilidade de retenção do imposto for atribu¡da ao remetente ou alienante da mercadoria, pelo serviço de transporte realizado por transportador aut“nomo ou por transportador não-inscrito na Unidade da Federação onde se tenha iniciado o serviço '),
    A251 = ('2932','Aquisição de serviço de transporte iniciado em Unidade da Federação diversa daquela onde esteja inscrito o prestador'),
    A252 = ('2933','Aquisição de serviço tributado pelo Imposto Sobre serviços de Qualquer Natureza'),
    A253 = ('2934','Entrada simbólica de mercadoria recebida para depósito fechado ou armazémgeral'),
    A254 = ('2949','Outra entrada de mercadoria ou prestação de serviço não especificado'),
    A255 = ('3000','ENTRADAS OU AQUISIÇÕES DE SERVIÇOS DO EXTERIOR'),
    A256 = ('3100','COMPRAS PARA INDUSTRIALIZAÇÃO, PRODUÇÃO RURAL, COMERCIALIZAÇÃO OU PRESTAÇÃO DE SERVIÇOS (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A257 = ('3101','Compra para industrialização ou produção rural (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A258 = ('3102','Compra para comercialização'),
    A259 = ('3126','Compra para utilização na prestação de serviço sujeita ao ICMS (AJUSTE SINIEF 4, DE 9 DE JULHO DE 2010) efeitos a partir de 1§ de janeiro de 2011- DECRETO 36.465/2011'),
    A260 = ('3127','Compra para industrialização sob o regime de drawback'),
    A261 = ('3128','Compra para utilização na prestação de serviço sujeita ao ISSQN(AJUSTE SINIEF 4, DE 9 DE JULHO DE 2010) efeitos a partir de 1§ de janeiro de 2011- DECRETO 36.465/2011'),
    A262 = ('3200','DEVOLUÇÕES DE VENDAS DE PRODUÇÃO PRÓPRIA, DE TERCEIROS OU ANULAÇÕES DE VALORES'),
    A263 = ('3201','Devolução de venda de produção do estabelecimento'),
    A264 = ('3202','Devolução de venda de mercadoria adquirida ou recebida de terceiros'),
    A265 = ('3205','Anulação de valor relativo à prestação de serviço de comunicação'),
    A266 = ('3206','Anulação de valor relativo à prestação de serviço de transporte'),
    A267 = ('3207','Anulação de valor relativo à venda de energia elétrica'),
    A268 = ('3211','Devolução de venda de produção do estabelecimento sob o regime de drawback'),
    A269 = ('3250','COMPRAS DE ENERGIA ELÉTRICA'),
    A270 = ('3251','Compra de energia elétrica para distribuição ou comercialização'),
    A271 = ('3250','COMPRAS DE ENERGIA ELÉTRICA'),
    A272 = ('3301','Aquisição de serviço de comunicação para execução de serviço da mesma natureza'),
    A273 = ('3350','AQUISIÇÕES DE SERVIÇOS DE TRANSPORTE'),
    A274 = ('3351','Aquisição de serviço de transporte para execução de serviço da mesma natureza'),
    A275 = ('3352','Aquisição de serviço de transporte por estabelecimento industrial'),
    A276 = ('3353','Aquisição de serviço de transporte por estabelecimento comercial'),
    A277 = ('3354','Aquisição de serviço de transporte por estabelecimento de prestador de serviço de comunicação'),
    A278 = ('3355','Aquisição de serviço de transporte por estabelecimento de geradora ou de distribuidora de energia elétrica'),
    A279 = ('3356','Aquisição de serviço de transporte por estabelecimento de produtor rural'),
    A280 = ('3500','ENTRADAS DE MERCADORIAS REMETIDAS COM FIM ESPECÍFICO DE EXPORTAÇÃO E EVENTUAIS DEVOLUÇÕES'),
    A281 = ('3503','Devolução de mercadoria exportada que tenha sido recebida com fim específico de exportação'),
    A282 = ('3550','OPERAÇÕES COM BENS DE ATIVO IMOBILIZADO E MATERIAIS PARA USO OU CONSUMO'),
    A283 = ('3551','Compra de bem para o ativo imobilizado'),
    A284 = ('3553','Devolução de venda de bem do ativo imobilizado'),
    A285 = ('3556','Compra de material para uso ou consumo'),
    A286 = ('3650','ENTRADAS DE COMBUSTIVEIS, DERIVADOS OU NÇO DE PETRàLEO, E LUBRIFICANTES'),
    A287 = ('3651','Compra de combustível ou lubrificante para industrialização subseqente'),
    A288 = ('3652','Compra de combustível ou lubrificante para comercialização'),
    A289 = ('3653','Compra de combustível ou lubrificante por consumidor ou usu rio final'),
    A290 = ('3900','OUTRAS ENTRADAS DE MERCADORIAS OU AQUISIÇÕES DE SERVIÇOS'),
    A291 = ('3930','Lançamento efetuado a título de entrada de bem sob amparo de regime especial aduaneiro de admissÆo tempor ria'),
    A292 = ('3949','Outra entrada de mercadoria ou prestação de serviço não especificado'),
    A293 = ('5000','SAIDAS OU PRESTAÇÕES DE SERVIÇOS PARA O ESTADO'),
    A294 = ('5100','VENDAS DE PRODUÇÃO PRÓPRIA OU DE TERCEIROS'),
    A295 = ('5101','Venda de produção do estabelecimento'),
    A296 = ('5102','Venda de mercadoria adquirida ou recebida de terceiros'),
    A297 = ('5103','Venda de produção do estabelecimento efetuada fora do estabelecimento'),
    A298 = ('5104','Venda de mercadoria adquirida ou recebida de terceiros, efetuada fora do estabelecimento'),
    A299 = ('5105','Venda de produção do estabelecimento que não deva por ele transitar'),
    A300 = ('5106','Venda de mercadoria adquirida ou recebida de terceiros, que não deva por ele transitar'),
    A301 = ('5109','Venda de produção do estabelecimento destinada à Zona Franca de Manaus ou µreas de Livre Com‚rcio'),
    A302 = ('5110','Venda de mercadoria, adquirida ou recebida de terceiros, destinada à Zona Franca de Manaus ou µreas de Livre Comercio, de que trata o Anexo do Convˆnio SINIEF s/n, de 15 de dezembro de 1970, que dispäe sobre o Sistema Nacional Integrado de Informa‡äes Econ“mico-Fiscais'),
    A303 = ('5111','Venda de produção do estabelecimento remetida anteriormente em consignação industrial'),
    A304 = ('5112','Venda de mercadoria adquirida ou recebida de terceiros remetida anteriormente em consignação industrial'),
    A305 = ('5113','Venda de produção do estabelecimento remetida anteriormente em consignação mercantil'),
    A306 = ('5114','Venda de mercadoria adquirida ou recebida de terceiros remetida anteriormente em consignação mercantil'),
    A307 = ('5115','Venda de mercadoria adquirida ou recebida de terceiros, recebida anteriormente em consignação mercantil'),
    A308 = ('5116','Venda de produção do estabelecimento originada de encomenda para entrega futura'),
    A309 = ('5117','Venda de mercadoria adquirida ou recebida de terceiros, originada de encomenda para entrega futura'),
    A310 = ('5118','Venda de produção do estabelecimento entregue ao destinat rio por conta e ordem do adquirente origin rio, em venda à ordem'),
    A311 = ('5119','Venda de mercadoria adquirida ou recebida de terceiros entregue ao destinat rio por conta e ordem do adquirente origin rio, em venda à ordem'),
    A312 = ('5120','Venda de mercadoria adquirida ou recebida de terceiros entregue ao destinat rio pelo vendedor remetente, em venda à ordem'),
    A313 = ('5122','Venda de produção do estabelecimento remetida para industrialização, por conta e ordem do adquirente, sem transitar pelo estabelecimento do adquirente'),
    A314 = ('5123','Venda de mercadoria adquirida ou recebida de terceiros remetida para industrialização, por conta e ordem do adquirente, sem transitar pelo estabelecimento do adquirente'),
    A315 = ('5124','Industrialização efetuada para outra empresa'),
    A316 = ('5125','Industrialização efetuada para outra empresa quando a mercadoria recebida para utilização no processo de industrialização não transitar pelo estabelecimento adquirente da mercadoria'),
    A317 = ('5150','TRANSFERÊNCIAS DE PRODUÇÃO PRÓPRIA OU DE TERCEIROS'),
    A318 = ('5151','Transferência de produção do estabelecimento'),
    A319 = ('5152','Transferência de mercadoria adquirida ou recebida de terceiros'),
    A320 = ('5153','Transferência de energia elétrica'),
    A321 = ('5155','Transferência de produção do estabelecimento, que não deva por ele transitar'),
    A322 = ('5156','Transferência de mercadoria adquirida ou recebida de terceiros, que não deva por ele transitar'),
    A323 = ('5200','DEVOLUÇÕES DE COMPRAS PARA INDUSTRIALIZAÇÃO, PRODUÇÃO RURAL, COMERCIALIZAÇÃO OU ANULAÇÕES DE VALORES (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A324 = ('5201','Devolução de compra para industrialização ou produção rural (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A325 = ('5202','Devolução de compra para comercialização'),
    A326 = ('5205','Anulação de valor relativo a aquisição de serviço de comunicação'),
    A327 = ('5206','Anulação de valor relativo a aquisição de serviço de transporte'),
    A328 = ('5207','Anulação de valor relativo à compra de energia elétrica'),
    A329 = ('5208','Devolução de mercadoria recebida em Transferência para industrialização ou produção rural'),
    A330 = ('5209','Devolução de mercadoria recebida em Transferência para comercialização'),
    A331 = ('5210','Devolução de compra para utilização na prestação de serviço'),
    A332 = ('5250','VENDAS DE ENERGIA ELÉTRICA'),
    A333 = ('5251','Venda de energia elétrica para distribuição ou comercialização'),
    A334 = ('5252','Venda de energia elétrica para estabelecimento industrial'),
    A335 = ('5253','Venda de energia elétrica para estabelecimento comercial'),
    A336 = ('5254','Venda de energia elétrica para estabelecimento prestador de serviço de transporte'),
    A337 = ('5255','Venda de energia elétrica para estabelecimento prestador de serviço de comunicação'),
    A338 = ('5256','Venda de energia elétrica para estabelecimento de produtor rural'),
    A339 = ('5257','Venda de energia elétrica para consumo por demanda contratada'),
    A340 = ('5258','Venda de energia elétrica a não contribuinte'),
    A341 = ('5300','PRESTAÇÕES DE SERVIÇOS DE COMUNICAÇÃO'),
    A342 = ('5301','Prestação de serviço de comunicação para execução de serviço da mesma natureza'),
    A343 = ('5302','Prestação de serviço de comunicação a estabelecimento industrial'),
    A344 = ('5303','Prestação de serviço de comunicação a estabelecimento comercial'),
    A345 = ('5304','Prestação de serviço de comunicação a estabelecimento de prestador de serviço de transporte'),
    A346 = ('5305','Prestação de serviço de comunicação a estabelecimento de geradora ou de distribuidora de energia elétrica'),
    A347 = ('5306','Prestação de serviço de comunicação a estabelecimento de produtor rural'),
    A348 = ('5307','Prestação de serviço de comunicação a não contribuinte'),
    A349 = ('5350','PRESTAÇÕES DE SERVIÇOS DE TRANSPORTE'),
    A350 = ('5351','Prestação de serviço de transporte para execução de serviço da mesma natureza'),
    A351 = ('5352','Prestação de serviço de transporte a estabelecimento industrial'),
    A352 = ('5353','Prestação de serviço de transporte a estabelecimento comercial'),
    A353 = ('5354','Prestação de serviço de transporte a estabelecimento de prestador de serviço de comunicação'),
    A354 = ('5355','Prestação de serviço de transporte a estabelecimento de geradora ou de distribuidora de energia elétrica'),
    A355 = ('5356','Prestação de serviço de transporte a estabelecimento de produtor rural'),
    A356 = ('5357','Prestação de serviço de transporte a não contribuinte'),
    A357 = ('5359','Prestação de serviço de transporte a contribuinte ou a não-contribuinte, quando a mercadoria transportada esteja dispensada de emissão de Nota Fiscal '),
    A358 = ('5360','Prestação de serviço de transporte a contribuinte-substituto em relação ao serviço de transporte (ACR) (Ajuste SINIEF 06/2007- Decreto n§ 30.861/2007) ? a partir de 01.01.2008'),
    A359 = ('5400','SAIDAS DE MERCADORIAS SUJEITAS AO REGIME DE SUBSTITUIÇÃO TRIBUTµRIA'),
    A360 = ('5401','Venda de produção do estabelecimento quando o produto esteja sujeito ao regime de substituição tribut ria'),
    A361 = ('5402','Venda de produção do estabelecimento de produto sujeito ao regime de substituição tribut ria, em operação entre contribuintes substitutos do mesmo produto'),
    A362 = ('5403','Venda de mercadoria, adquirida ou recebida de terceiros, sujeita ao regime de substituição tribut ria, na condição de contribuinte-substituto'),
    A363 = ('5405','Venda de mercadoria, adquirida ou recebida de terceiros, sujeita ao regime de substituição tribut ria, na condição de contribuinte-substitu¡do'),
    A364 = ('5408','Transferência de produção do estabelecimento quando o produto estiver sujeito ao regime de substituição tribut ria'),
    A365 = ('5409','Transferência de mercadoria adquirida ou recebida de terceiros em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A366 = ('5410','Devolução de compra para industrialização de mercadoria sujeita ao regime de substituição tribut ria'),
    A367 = ('5411','Devolução de compra para comercialização em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A368 = ('5412','Devolução de bem do ativo imobilizado, em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A369 = ('5413','Devolução de mercadoria destinada ao uso ou consumo, em operação com mercadoria sujeita ao regime de substituição tribut ria.'),
    A370 = ('5414','Remessa de produção do estabelecimento para venda fora do estabelecimento, quando o produto estiver sujeito ao regime de substituição tribut ria'),
    A371 = ('5415','Remessa de mercadoria adquirida ou recebida de terceiros para venda fora do estabelecimento, em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A372 = ('5450','SISTEMAS DE INTEGRAÇÃO'),
    A373 = ('5451','Remessa de animal e de insumo para estabelecimento produtor'),
    A374 = ('5500','REMESSAS PARA FORMAÇÃO DE LOTE E COM FIM ESPECÍFICO DE EXPORTAÇÃO E EVENTUAIS DEVOLUÇÕES (NR Ajuste SINIEF 09/2005)'),
    A375 = ('5501','Remessa de produção do estabelecimento, com fim específico de exportação'),
    A376 = ('5502','Remessa de mercadoria adquirida ou recebida de terceiros, com fim específico de exportação'),
    A377 = ('5503','Devolução de mercadoria recebida com fim específico de exportação'),
    A378 = ('5504','Remessa de mercadoria para formação de lote de exportação, de produto industrializado ou produzido pelo pr¢prio estabelecimento.'),
    A379 = ('5505','Remessa de mercadoria, adquirida ou recebida de terceiros, para formação de lote de exportação.'),
    A380 = ('5550','OPERAÇÕES COM BENS DE ATIVO IMOBILIZADO E MATERIAIS PARA USO OU CONSUMO'),
    A381 = ('5551','Venda de bem do ativo imobilizado'),
    A382 = ('5552','Transferência de bem do ativo imobilizado'),
    A383 = ('5553','Devolução de compra de bem para o ativo imobilizado'),
    A384 = ('5554','Remessa de bem do ativo imobilizado para uso fora do estabelecimento'),
    A385 = ('5555','Devolução de bem do ativo imobilizado de terceiro, recebido para uso no estabelecimento'),
    A386 = ('5556','Devolução de compra de material de uso ou consumo'),
    A387 = ('5557','Transferência de material de uso ou consumo'),
    A388 = ('5600','CRÉDITOS E RESSARCIMENTOS DE ICMS'),
    A389 = ('5601','Transferência de cr‚dito de ICMS acumulado'),
    A390 = ('5602','Transferência de saldo credor do ICMS, para outro estabelecimento da mesma empresa, destinado à compensação de saldo devedor do ICMS'),
    A391 = ('5603','Ressarcimento de ICMS retido por substituição tribut ria'),
    A392 = ('5605','Transferência de saldo devedor do ICMS de outro estabelecimento da mesma empresa '),
    A393 = ('5606','Utilização de saldo credor do ICMS para extinção por compensação de d‚bitos fiscais'),
    A394 = ('5650','SAIDAS DE COMBUSTIVEIS, DERIVADOS OU NÇO DE PETRàLEO, E LUBRIFICANTES'),
    A395 = ('5651','Venda de combustível ou lubrificante de produção do estabelecimento destinados à industrialização subseqente'),
    A396 = ('5652','Venda de combustível ou lubrificante, de produção do estabelecimento, destinados à comercialização'),
    A397 = ('5653','Venda de combustível ou lubrificante, de produção do estabelecimento, destinados a consumidor ou usu rio final'),
    A398 = ('5654','Venda de combustível ou lubrificante, adquiridos ou recebidos de terceiros, destinados à industrialização subseqente'),
    A399 = ('5655','Venda de combustível ou lubrificante, adquiridos ou recebidos de terceiros, destinados à comercialização'),
    A400 = ('5656','Venda de combustível ou lubrificante, adquiridos ou recebidos de terceiros, destinados a consumidor ou usu rio final'),
    A401 = ('5657','Remessa de combustível ou lubrificante, adquiridos ou recebidos de terceiros, para venda fora do estabelecimento'),
    A402 = ('5658','Transferência de combustível ou lubrificante de produção do estabelecimento'),
    A403 = ('5659','Transferência de combustível ou lubrificante adquiridos ou recebidos de terceiros'),
    A404 = ('5660','Devolução de compra de combustível ou lubrificante adquiridos para industrialização subseqente'),
    A405 = ('5661','Devolução de compra de combustível ou lubrificante adquiridos para comercialização'),
    A406 = ('5662','Devolução de compra de combustível ou lubrificante adquiridos por consumidor ou usu rio final'),
    A407 = ('5663','Remessa para armazenagem de combustível ou lubrificante'),
    A408 = ('5664','Retorno de combustível ou lubrificante recebidos para armazenagem'),
    A409 = ('5665','Retorno simbólico de combustível ou lubrificante recebidos para armazenagem'),
    A410 = ('5666','Remessa, por conta e ordem de terceiros, de combustível ou lubrificante recebidos para armazenagem'),
    A411 = ('5667','Venda de combustível ou lubrificante a consumidor ou usu rio final estabelecido em outra Unidade da Federação'),
    A412 = ('5900','OUTRAS SAIDAS DE MERCADORIAS OU PRESTAÇÕES DE SERVIÇOS'),
    A413 = ('5901','Remessa para industrialização por encomenda'),
    A414 = ('5902','Retorno de mercadoria utilizada na industrialização por encomenda'),
    A415 = ('5903','Retorno de mercadoria recebida para industrialização e não aplicada no referido processo'),
    A416 = ('5904','Remessa para venda fora do estabelecimento'),
    A417 = ('5905','Remessa para depósito fechado ou armazémgeral'),
    A418 = ('5906','Retorno de mercadoria depositada em depósito fechado ou armazémgeral'),
    A419 = ('5907','Retorno simbólico de mercadoria depositada em depósito fechado ou armazémgeral'),
    A420 = ('5908','Remessa de bem por conta de contrato de comodato'),
    A421 = ('5909','Retorno de bem recebido por conta de contrato de comodato'),
    A422 = ('5910','Remessa em bonificação, doação ou brinde'),
    A423 = ('5911','Remessa de amostra grátis'),
    A424 = ('5912','Remessa de mercadoria ou bem para demonstração'),
    A425 = ('5913','Retorno de mercadoria ou bem recebido para demonstração'),
    A426 = ('5914','Remessa de mercadoria ou bem para exposição ou feira'),
    A427 = ('5915','Remessa de mercadoria ou bem para conserto ou reparo'),
    A428 = ('5916','Retorno de mercadoria ou bem recebido para conserto ou reparo'),
    A429 = ('5917','Remessa de mercadoria em consignação mercantil ou industrial'),
    A430 = ('5918','Devolução de mercadoria recebida em consignação mercantil ou industrial'),
    A431 = ('5919','Devolução simbólica de mercadoria vendida ou utilizada em processo industrial, recebida anteriormente em consignação mercantil ou industrial'),
    A432 = ('5920','Remessa de vasilhame ou sacaria'),
    A433 = ('5921','Devolução de vasilhame ou sacaria'),
    A434 = ('5922','Lançamento efetuado a título de simples faturamento decorrente de venda para entrega futura'),
    A435 = ('5923','Remessa de mercadoria por conta e ordem de terceiros, em venda à ordem ou em opera‡äes com armazémgeral ou depósito fechado. (NR AJUSTE SINIEF 14, DE 11 DE DEZEMBRO DE 2009)Vejamais[p2] efeitos a partir de 1§ de julho de 2010? DECRETO 37.993/2012.'),
    A436 = ('5924','Remessa para industrialização por conta e ordem do adquirente da mercadoria, quando esta não transitar pelo estabelecimento do adquirente'),
    A437 = ('5925','Retorno de mercadoria recebida para industrialização por conta e ordem do adquirente da mercadoria, quando aquela não transitar pelo estabelecimento do adquirente'),
    A438 = ('5926','Lançamento efetuado a título de reclassificação de mercadoria decorrente de formação de kit ou de sua desagregação'),
    A439 = ('5927','Lançamento efetuado a título de baixa de estoque decorrente de perda, roubo ou deterioração'),
    A440 = ('5928','Lançamento efetuado a título de baixa de estoque decorrente do encerramento da atividade da empresa'),
    A441 = ('5929','Lançamento efetuado em decorrência de emissão de documento fiscal relativo a operação ou prestação tamb‚m registrada em equipamento Emissor de Cupom Fiscal - ECF'),
    A442 = ('5931','Lançamento efetuado em decorrência da responsabilidade de retenção do imposto por substituição tribut ria, atribu¡da ao remetente ou alienante da mercadoria, pelo serviço de transporte realizado por transportador aut“nomo ou por transportador não inscrito na unidade da Federação onde iniciado o serviço'),
    A443 = ('5932','Prestação de serviço de transporte iniciada em unidade da Federação diversa daquela onde inscrito o prestador'),
    A444 = ('5933','Prestação de serviço tributado pelo Imposto Sobre serviços de Qualquer Natureza'),
    A445 = ('5934','Remessa simbólica de mercadoria depositada em armazémgeral ou depósito fechado. (AJUSTE SINIEF 14, DE 11 DE DEZEMBRO DE 2009) ? DECRETO 36.465/2011.'),
    A446 = ('5949','Outra sa¡da de mercadoria ou prestação de serviço não especificado'),
    A447 = ('6000','SAIDAS OU PRESTAÇÕES DE SERVIÇOS PARA OUTROS ESTADOS'),
    A448 = ('6101','Venda de produção do estabelecimento'),
    A449 = ('6102','Venda de mercadoria adquirida ou recebida de terceiros'),
    A450 = ('6103','Venda de produção do estabelecimento, efetuada fora do estabelecimento'),
    A451 = ('6104','Venda de mercadoria adquirida ou recebida de terceiros, efetuada fora do estabelecimento'),
    A452 = ('6105','Venda de produção do estabelecimento que não deva por ele transitar'),
    A453 = ('6106','Venda de mercadoria adquirida ou recebida de terceiros, que não deva por ele transitar'),
    A454 = ('6107','Venda de produção do estabelecimento, destinada a não contribuinte'),
    A455 = ('6108','Venda de mercadoria adquirida ou recebida de terceiros, destinada a não contribuinte'),
    A456 = ('6109','Venda de produção do estabelecimento destinada à Zona Franca de Manaus ou µreas de Livre Com‚rcio'),
    A457 = ('6110','Venda de mercadoria, adquirida ou recebida de terceiros, destinada à Zona Franca de Manaus ou µreas de Livre Com‚rcio, de que trata o Anexo do Convˆnio SINIEF s/n, de 15 de dezembro de 1970, que dispäe sobre o Sistema Nacional Integrado de Informa‡äes Econ“mico-Fiscais (Decreto n§ 26.955/2004) RETROAGINDO SEUS EFEITOS A 24.06.2004'),
    A458 = ('6111','Venda de produção do estabelecimento remetida anteriormente em consignação industrial'),
    A459 = ('6112','Venda de mercadoria adquirida ou recebida de Terceiros remetida anteriormente em consignação industrial'),
    A460 = ('6113','Venda de produção do estabelecimento remetida anteriormente em consignação mercantil'),
    A461 = ('6114','Venda de mercadoria adquirida ou recebida de terceiros remetida anteriormente em consignação mercantil'),
    A462 = ('6115','Venda de mercadoria adquirida ou recebida de terceiros, recebida anteriormente em consignação mercantil'),
    A463 = ('6116','Venda de produção do estabelecimento originada de encomenda para entrega futura'),
    A464 = ('6117','Venda de mercadoria adquirida ou recebida de terceiros, originada de encomenda para entrega futura'),
    A465 = ('6118','Venda de produção do estabelecimento entregue ao destinat rio por conta e ordem do adquirente origin rio, em venda à ordem'),
    A466 = ('6119','Venda de mercadoria adquirida ou recebida de terceiros entregue ao destinat rio por conta e ordem do adquirente origin rio, em venda à ordem'),
    A467 = ('6120','Venda de mercadoria adquirida ou recebida de terceiros entregue ao destinat rio pelo vendedor remetente, em venda à ordem'),
    A468 = ('6122','Venda de produção do estabelecimento remetida para industrialização, por conta e ordem do adquirente, sem transitar pelo estabelecimento do adquirente'),
    A469 = ('6123','Venda de mercadoria adquirida ou recebida de terceiros remetida para industrialização, por conta e ordem do adquirente, sem transitar pelo estabelecimento do adquirente'),
    A470 = ('6124','Industrialização efetuada para outra empresa'),
    A471 = ('6125','Industrialização efetuada para outra empresa quando a mercadoria recebida para utilização no processo de industrialização não transitar pelo estabelecimento adquirente da mercadoria'),
    A472 = ('6150','TRANSFERÊNCIAS DE PRODUÇÃO PRÓPRIA OU DE TERCEIROS'),
    A473 = ('6151','Transferência de produção do estabelecimento'),
    A474 = ('6152','Transferência de mercadoria adquirida ou recebida de terceiros'),
    A475 = ('6153','Transferência de energia elétrica'),
    A476 = ('6155','Transferência de produção do estabelecimento, que não deva por ele transitar'),
    A477 = ('6156','Transferência de mercadoria adquirida ou recebida de terceiros, que não deva por ele transitar'),
    A478 = ('6200','DEVOLUÇÕES DE COMPRAS PARA INDUSTRIALIZAÇÃO, COMERCIALIZAÇÃO OU ANULAÇÕES DE VALORES'),
    A479 = ('6201','Devolução de compra para industrialização ou produção rural (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A480 = ('6202','Devolução de compra para comercialização'),
    A481 = ('6205','Anulação de valor relativo a aquisição de serviço de comunicação'),
    A482 = ('6206','Anulação de valor relativo a aquisição de serviço de transporte'),
    A483 = ('6207','Anulação de valor relativo à compra de energia elétrica'),
    A484 = ('6208','Devolução de mercadoria recebida em Transferência para industrialização ou produção rural'),
    A485 = ('6209','Devolução de mercadoria recebida em Transferência para comercialização'),
    A486 = ('6210','Devolução de compra para utilização na prestação de serviço'),
    A487 = ('6250','VENDAS DE ENERGIA ELÉTRICA'),
    A488 = ('6251','Venda de energia elétrica para distribuição ou comercialização'),
    A489 = ('6252','Venda de energia elétrica para estabelecimento industrial'),
    A490 = ('6253','Venda de energia elétrica para estabelecimento comercial'),
    A491 = ('6254','Venda de energia elétrica para estabelecimento prestador de serviço de transporte'),
    A492 = ('6255','Venda de energia elétrica para estabelecimento prestador de serviço de comunicação'),
    A493 = ('6256','Venda de energia elétrica para estabelecimento de produtor rural'),
    A494 = ('6257','Venda de energia elétrica para consumo por demanda contratada'),
    A495 = ('6258','Venda de energia elétrica a não contribuinte'),
    A496 = ('6300','PRESTAÇÕES DE SERVIÇOS DE COMUNICAÇÃO'),
    A497 = ('6301','Prestação de serviço de comunicação para execução de serviço da mesma natureza'),
    A498 = ('6302','Prestação de serviço de comunicação a estabelecimento industrial'),
    A499 = ('6303','Prestação de serviço de comunicação a estabelecimento comercial'),
    A500 = ('6304','Prestação de serviço de comunicação a estabelecimento de prestador de serviço de transporte'),
    A501 = ('6305','Prestação de serviço de comunicação a estabelecimento de geradora ou de distribuidora de energia elétrica'),
    A502 = ('6306','Prestação de serviço de comunicação a estabelecimento de produtor rural'),
    A503 = ('6307','Prestação de serviço de comunicação a não contribuinte'),
    A504 = ('6350','PRESTAÇÕES DE SERVIÇOS DE TRANSPORTE'),
    A505 = ('6351','Prestação de serviço de transporte para execução de serviço da mesma natureza'),
    A506 = ('6352','Prestação de serviço de transporte a estabelecimento industrial'),
    A507 = ('6353','Prestação de serviço de transporte a estabelecimento comercial'),
    A508 = ('6354','Prestação de serviço de transporte a estabelecimento de prestador de serviço de comunicação'),
    A509 = ('6355','Prestação de serviço de transporte a estabelecimento de geradora ou de distribuidora de energia elétrica'),
    A510 = ('6356','Prestação de serviço de transporte a estabelecimento de produtor rural'),
    A511 = ('6357','Prestação de serviço de transporte a não contribuinte'),
    A512 = ('6359','Prestação de serviço de transporte a contribuinte ou a não-contribuinte, quando a mercadoria transportada esteja dispensada de emissão de Nota Fiscal '),
    A513 = ('6360','Prestação de serviço de transporte a contribuinte substituto em relação ao serviço de transporte  '),
    A514 = ('6400','SAIDAS DE MERCADORIAS SUJEITAS AO REGIME DE SUBSTITUIÇÃO TRIBUTµRIA'),
    A515 = ('6401','Venda de produção do estabelecimento quando o produto estiver sujeito ao regime de substituição tribut ria'),
    A516 = ('6402','Venda de produção do estabelecimento de produto sujeito ao regime de substituição tribut ria, em operação entre contribuintes substitutos do mesmo produto'),
    A517 = ('6403','Venda de mercadoria adquirida ou recebida de terceiros em operação com mercadoria sujeita ao regime de substituição tribut ria, na condição de contribuinte substituto'),
    A518 = ('6404','Venda de mercadoria sujeita ao regime de substituição tribut ria, cujo imposto j  tenha sido retido anteriormente'),
    A519 = ('6408','Transferência de produção do estabelecimento quando o produto estiver sujeito ao regime de substituição tribut ria'),
    A520 = ('6409','Transferência de mercadoria adquirida ou recebida de terceiros, sujeita ao regime de substituição tribut ria'),
    A521 = ('6410','Devolução de compra para industrialização ou ptrodução rural quando a mercadoria sujeita ao regime de substituição tribut ria'),
    A522 = ('6411','Devolução de compra para comercialização em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A523 = ('6412','Devolução de bem do ativo imobilizado, em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A524 = ('6413','Devolução de mercadoria destinada ao uso ou consumo, em operação com mercadoria sujeita ao regime de substituição tribut ria'),
    A525 = ('6414','Remessa de produção do estabelecimento para venda fora do estabelecimento, quando o produto estiver sujeito ao regime de substituição tribut ria'),
    A526 = ('6415','Remessa de mercadoria adquirida ou recebida de terceiros para venda fora do estabelecimento, quando a referida ração com mercadoria sujeita ao regime de substituição tribut ria'),
    A527 = ('6500','REMESSAS COM FIM ESPECÍFICO DE EXPORTAÇÃO E EVENTUAIS DEVOLUÇÕES'),
    A528 = ('6501','Remessa de produção do estabelecimento, com fim específico de exportação'),
    A529 = ('6502','Remessa de mercadoria adquirida ou recebida de terceiros, com fim específico de exportação'),
    A530 = ('6503','Devolução de mercadoria recebida com fim específico de exportação'),
    A531 = ('6504','Remessa de mercadoria para formação de lote de exportação, de produto industrializado ou produzido pelo pr¢prio estabelecimento.'),
    A532 = ('6505','Remessa de mercadoria, adquirida ou recebida de terceiros, para formação de lote de exportação.'),
    A533 = ('6550','OPERAÇÕES COM BENS DE ATIVO IMOBILIZADO E MATERIAIS PARA USO OU CONSUMO'),
    A534 = ('6551','Venda de bem do ativo imobilizado'),
    A535 = ('6552','Transferência de bem do ativo imobilizado'),
    A536 = ('6553','Devolução de compra de bem para o ativo imobilizado'),
    A537 = ('6554','Remessa de bem do ativo imobilizado para uso fora do estabelecimento'),
    A538 = ('6555','Devolução de bem do ativo imobilizado de terceiro, recebido para uso no estabelecimento'),
    A539 = ('6556','Devolução de compra de material de uso ou consumo'),
    A540 = ('6557','Transferência de material de uso ou consumo'),
    A541 = ('6600','CRÉDITOS E RESSARCIMENTOS DE ICMS'),
    A542 = ('6603','Ressarcimento de ICMS retido por substituição tribut ria'),
    A543 = ('6650','SAIDAS DE COMBUSTIVEIS, DERIVADOS OU NÇO DE PETRàLEO, E LUBRIFICANTE'),
    A544 = ('6651','Venda de combustível ou lubrificante, de produção do estabelecimento, destinados à industrialização subseqente'),
    A545 = ('6652','Venda de combustível ou lubrificante, de produção do estabelecimento, destinados à comercialização'),
    A546 = ('6653','Venda de combustível ou lubrificante, de produção do estabelecimento, destinados a consumidor ou usu rio final'),
    A547 = ('6654','Venda de combustível ou lubrificante, adquiridos ou recebidos de terceiros, destinados à industrialização subseqente'),
    A548 = ('6655','Venda de combustível ou lubrificante, adquiridos ou recebidos de terceiros, destinados à comercialização'),
    A549 = ('6656','Venda de combustível ou lubrificante, adquiridos ou recebidos de terceiros, destinados a consumidor ou usu rio final'),
    A550 = ('6657','Remessa de combustível ou lubrificante, adquiridos ou recebidos de terceiros, para venda fora do estabelecimento'),
    A551 = ('6658','Transferência de combustível ou lubrificante de produção do estabelecimento'),
    A552 = ('6659','Transferência de combustível ou lubrificante adquiridos ou recebidos de terceiros'),
    A553 = ('6660','Devolução de compra de combustível ou lubrificante adquiridos para industrialização subseqente'),
    A554 = ('6661','Devolução de compra de combustível ou lubrificante adquiridos para comercialização'),
    A555 = ('6662','Devolução de compra de combustível ou lubrificante adquiridos por consumidor ou usu rio final'),
    A556 = ('6663','Remessa para armazenagem de combustível ou lubrificante'),
    A557 = ('6664','Retorno de combustível ou lubrificante recebidos para armazenagem'),
    A558 = ('6665','Retorno simbólico de combustível ou lubrificante recebidos para armazenagem'),
    A559 = ('6666','Remessa, por conta e ordem de terceiros, de combustível ou lubrificante recebidos para armazenagem'),
    A560 = ('6667','Venda de combustível ou lubrificante a consumidor ou usu rio final estabelecido em outra Unidade da Federação diferente da que ocorrer o consumo'),
    A561 = ('6900','OUTRAS SAIDAS DE MERCADORIAS OU PRESTAÇÕES DE SERVIÇOS'),
    A562 = ('6901','Remessa para industrialização por encomenda'),
    A563 = ('6902','Retorno de mercadoria utilizada na industrialização por encomenda'),
    A564 = ('6903','Retorno de mercadoria recebida para industrialização e não aplicada no referido processo'),
    A565 = ('6904','Remessa para venda fora do estabelecimento'),
    A566 = ('6905','Remessa para depósito fechado ou armazémgeral'),
    A567 = ('6906','Retorno de mercadoria depositada em depósito fechado ou armazémgeral'),
    A568 = ('6907','Retorno simbólico de mercadoria depositada em depósito fechado ou armazémgeral'),
    A569 = ('6908','Remessa de bem por conta de contrato de comodato'),
    A570 = ('6909','Retorno de bem recebido por conta de contrato de comodato'),
    A571 = ('6910','Remessa em bonificação, doação ou brinde'),
    A572 = ('6911','Remessa de amostra grátis'),
    A573 = ('6912','Remessa de mercadoria ou bem para demonstração'),
    A574 = ('6913','Retorno de mercadoria ou bem recebido para demonstração'),
    A575 = ('6914','Remessa de mercadoria ou bem para exposição ou feira'),
    A576 = ('6915','Remessa de mercadoria ou bem para conserto ou reparo'),
    A577 = ('6916','Retorno de mercadoria ou bem recebido para conserto ou reparo'),
    A578 = ('6917','Remessa de mercadoria em consignação mercantil ou industrial'),
    A579 = ('6918','Devolução de mercadoria recebida em consignação mercantil ou industrial'),
    A580 = ('6919','Devolução simbólica de mercadoria vendida ou utilizada em processo industrial, recebida anteriormente em consignação mercantil ou industrial'),
    A581 = ('6920','Remessa de vasilhame ou sacaria'),
    A582 = ('6921','Devolução de vasilhame ou sacaria'),
    A583 = ('6922','Lançamento efetuado a título de simples faturamento decorrente de venda para entrega futura'),
    A584 = ('6923','Remessa de mercadoria por conta e ordem de terceiros, em venda à ordem ou em opera‡äes com armazémgeral ou depósito fechado Vejamais[p5](NR AJUSTE SINIEF 14, DE 11 DE DEZEMBRO DE 2009) efeitos a partir de 1§ de julho de 2010? DECRETO 36.465/2011.'),
    A585 = ('6924','Remessa para industrialização por conta e ordem do adquirente da mercadoria, quando esta não transitar pelo estabelecimento do adquirente'),
    A586 = ('6925','Retorno de mercadoria recebida para industrialização por conta e ordem do adquirente da mercadoria, quando aquela não transitar pelo estabelecimento do adquirente'),
    A587 = ('6929','Lançamento efetuado em decorrência de emissão de documento fiscal relativo a operação ou prestação tamb‚m registrada em equipamento Emissor de Cupom Fiscal - ECF'),
    A588 = ('6931','Lançamento efetuado em decorrência da responsabilidade de retenção do imposto por substituição tribut ria, atribu¡da ao remetente ou alienante da mercadoria, pelo serviço de transporte realizado por transportador aut“nomo ou por transportador não inscrito na unidade da Federação onde iniciado o serviço'),
    A589 = ('6932','Prestação de serviço de transporte iniciada em unidade da Federação diversa daquela onde inscrito o prestador'),
    A590 = ('6933','Prestação de serviço tributado pelo Imposto Sobre serviços de Qualquer Natureza'),
    A591 = ('6934','Remessa simbólica de mercadoria depositada em armazémgeral ou depósito fechado- (ACR AJUSTE SINIEF 14, DE 11 DE DEZEMBRO DE 2009) efeitos a partir de 1§ de julho de 2010 ? DECRETO 36.465/2011.'),
    A592 = ('6949','Outra sa¡da de mercadoria ou prestação de serviço não especificado'),
    A593 = ('7000','SAIDAS OU PRESTAÇÕES DE SERVIÇOS PARA O EXTERIOR'),
    A594 = ('7100','VENDAS DE PRODUÇÃO PRÓPRIA OU DE TERCEIROS'),
    A595 = ('7101','Venda de produção do estabelecimento'),
    A596 = ('7102','Venda de mercadoria adquirida ou recebida de terceiros'),
    A597 = ('7105','Venda de produção do estabelecimento, que não deva por ele transitar'),
    A598 = ('7106','Venda de mercadoria adquirida ou recebida de terceiros, que não deva por ele transitar'),
    A599 = ('7127','Venda de produção do estabelecimento sob o regime de drawback'),
    A600 = ('7200','DEVOLUÇÕES DE COMPRAS PARA INDUSTRIALIZAÇÃO, COMERCIALIZAÇÃO OU ANULAÇÕES DE VALORES'),
    A601 = ('7201','Devolução de compra para industrialização ou produção rural (NR Ajuste SINIEF 05/2005) (Decreto 28.868/2006)'),
    A602 = ('7202','Devolução de compra para comercialização'),
    A603 = ('7205','Anulação de valor relativo à aquisição de serviço de comunicação'),
    A604 = ('7206','Anulação de valor relativo a aquisição de serviço de transporte'),
    A605 = ('7207','Anulação de valor relativo à compra de energia elétrica'),
    A606 = ('7210','Devolução de compra para utilização na prestação de serviço'),
    A607 = ('7211','Devolução de compras para industrialização sob o regime de drawback'),
    A608 = ('7250','VENDAS DE ENERGIA ELÉTRICA'),
    A609 = ('7251','Venda de energia elétrica para o exterior'),
    A610 = ('7300','PRESTAÇÕES DE SERVIÇOS DE COMUNICAÇÃO'),
    A611 = ('7301','Prestação de serviço de comunicação para execução de serviço da mesma natureza'),
    A612 = ('7300','PRESTAÇÕES DE SERVIÇOS DE COMUNICAÇÃO'),
    A613 = ('7358','Prestação de serviço de transporte'),
    A614 = ('7500','EXPORTAÇÃO DE MERCADORIAS RECEBIDAS COM FIM ESPECÍFICO DE EXPORTAÇÃO'),
    A615 = ('7501','Exportação de mercadorias recebidas com fim específico de exportação'),
    A616 = ('7550','OPERAÇÕES COM BENS DE ATIVO IMOBILIZADO E MATERIAIS PARA USO OU CONSUMO'),
    A617 = ('7551','Venda de bem do ativo imobilizado'),
    A618 = ('7553','Devolução de compra de bem para o ativo imobilizado'),
    A619 = ('7556','Devolução de compra de material de uso ou consumo'),
    A620 = ('7650','SAIDAS DE COMBUSTIVEIS, DERIVADOS OU NÇO DE PETRàLEO, E LUBRIFICANTES'),
    A621 = ('7651','Venda de combustível ou lubrificante de produção do estabelecimento'),
    A622 = ('7654','Venda de combustível ou lubrificante adquiridos ou recebidos de terceiros'),
    A623 = ('7667','Venda de combustível ou lubrificante a consumidor ou usu rio final'),
    A624 = ('7900','OUTRAS SAIDAS DE MERCADORIA OU PRESTAÇÕES DE SERVIÇOS'),
    A625 = ('7930','Lançamento efetuado a título de devolução de bem cuja entrada tenha ocorrido sob amparo de regime especial aduaneiro de admissÆo tempor ria'),
    A626 = ('7949','Outra saída de mercadoria ou prestação de serviço não especificado'),

    
    def __new__(cls, valor):
        codigo, descricao = valor
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def descricao(self) -> str:
        return self._descricao

    @classmethod
    def teste(cls, codigo: str) -> bool:
        return codigo in cls._codigos()

    @classmethod
    def descricao_por_codigo(cls, codigo: str) -> str | None:
        return cls._mapa().get(codigo)

    @classmethod
    def _mapa(cls) -> dict[str, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache

    @classmethod
    def _codigos(cls) -> set[str]:
        return set(cls._mapa().keys())

class ValoresNmVAR(Enum):
    A1 = ('Qtd_BC_CHFUS_RAR' , 'Quantidade de chaves fusíveis usadas em banco de capacitores em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A2 = ('Qtd_BC_CHFUS_RAU' , 'Quantidade de chaves fusíveis usadas em banco de capacitores em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A3 = ('Qtd_BC_CRZT_CNV_RAR' , 'Quantidade de cruzetas usadas em banco de capacitores em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A4 = ('Qtd_BC_CRZT_CNV_RAU' , 'Quantidade de cruzetas usadas em banco de capacitores em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A5 = ('Qtd_BC_HA_RAR' , 'Quantidade de hastes de aterramentos usados em banco de capacitores em redes convencionais aéreas urbana conforme padrão da distribuidora'),
    A6 = ('Qtd_BC_HA_RAU' , 'Quantidade de hastes de aterramentos usados em banco de capacitores em redes convencionais aéreas urbana conforme padrão da distribuidora'),
    A7 = ('Qtd_BC_PR_RAR' , 'Quantidade de para-raios usadas em banco de capacitores em redes convencionais aéreas rural conforme padrão da distribuidora'),
    A8 = ('Qtd_BC_PR_RAU' , 'Quantidade de para-raios usadas em banco de capacitores em redes convencionais aéreas urbana conforme padrão da distribuidora'),
    A9 = ('Qtd_CHFUS_CRZT_CNV_RAR' , 'Quantidade de cruzetas usadas em chaves fusíveis em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A10 = ('Qtd_CHFUS_CRZT_CNV_RAU' , 'Quantidade de cruzetas usadas em chaves fusíveis em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A11 = ('Qtd_CHFUS_RD_CNV_RAR' , 'Quantidade, 1 Conjunto a cada x metros, de chaves fusíveis em redes aéreas convencionais rural conforme padrão da distribuidora (explicar em nota explicativa o padrão)'),
    A12 = ('Qtd_CHFUS_RD_CNV_RAU' , 'Quantidade, 1 Conjunto a cada x metros, de chaves fusíveis em redes aéreas convencionais urbana conforme padrão da distribuidora (explicar em nota explicativa o padrão)'),
    A13 = ('Qtd_CHSECC_CRZT_CNV_RAR' , 'Quantidade de cruzetas usadas em chaves seccionadoras em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A14 = ('Qtd_CHSECC_CRZT_CNV_RAU' , 'Quantidade de cruzetas usadas em chaves seccionadoras em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A15 = ('Qtd_CHSECC_PR_RAR' , 'Quantidade de para-raios usadas em chaves seccionadoras em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A16 = ('Qtd_CHSECC_PR_RAU' , 'Quantidade de para-raios usadas em chaves seccionadoras em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A17 = ('Qtd_CHSECCc_CHFUS_RAR' , 'Quantidade de chaves fusíveis usadas em chaves seccionadoras sob carga em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A18 = ('Qtd_CHSECCc_CHFUS_RAU' , 'Quantidade de chaves fusíveis usadas em chaves seccionadoras sob carga em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A19 = ('Qtd_CHSECCc_CRZT_CH_RAR' , 'Quantidade de cruzetas usadas em chaves seccionadoras sob carga em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A20 = ('Qtd_CHSECCc_CRZT_CH_RAU' , 'Quantidade de cruzetas usadas em chaves seccionadoras sob carga em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A21 = ('Qtd_CHSECCc_HA_RAR' , 'Quantidade de hastes de aterramento usadas em chaves seccionadoras sob carga em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A22 = ('Qtd_CHSECCc_HA_RAU' , 'Quantidade de hastes de aterramento usadas em chaves seccionadoras sob carga em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A23 = ('Qtd_CHSECCc_PR_RAR' , 'Quantidade de para-raios usadas em chaves seccionadoras sob carga em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A24 = ('Qtd_CHSECCc_PR_RAU' , 'Quantidade de para-raios usadas em chaves seccionadoras sob carga em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A25 = ('Qtd_MAX_CRUZT_PST_RDR' , 'Quantidade máxima de cruzetas por poste em rede aérea rural'),
    A26 = ('Qtd_MAX_CRUZT_PST_RDU' , 'Quantidade máxima de cruzetas por poste em rede aérea urbana'),
    A27 = ('Qtd_MAX_ISOL_DIS_PST_RDR' , 'Quantidade máxima de isoladores de disco por poste em rede aérea rural'),
    A28 = ('Qtd_MAX_ISOL_DIS_PST_RDU' , 'Quantidade máxima de isoladores de disco por poste em rede aérea urbana'),
    A29 = ('Qtd_MAX_ISOL_PIN_PST_RDR' , 'Quantidade máxima de isoladores de pino por poste em rede aérea rural'),
    A30 = ('Qtd_MAX_ISOL_PIN_PST_RDU' , 'Quantidade máxima de isoladores de pino por poste em rede aérea urbana'),
    A31 = ('Qtd_PR_CRZT_CNV_RAR' , 'Quantidade de cruzetas usadas em suporte de para-raios em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A32 = ('Qtd_PR_CRZT_CNV_RAU' , 'Quantidade de cruzetas usadas em suporte de para-raios em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A33 = ('Qtd_PR_HA_RAR' , 'Quantidade de hastes de aterramento usadas em suporte de para-raios em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A34 = ('Qtd_PR_HA_RAU' , 'Quantidade de hastes de aterramento usadas em suporte de para-raios em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A35 = ('Qtd_PR_RD_CNV_RAR' , 'Quantidade, 1 Conjunto a cada x metros, de para-raios em redes aéreas convencionais rural conforme padrão da distribuidora (explicar em nota explicativa o padrão)'),
    A36 = ('Qtd_PR_RD_CNV_RAU' , 'Quantidade, 1 Conjunto a cada x metros, de para-raios em redes aéreas convencionais urbana conforme padrão da distribuidora (explicar em nota explicativa o padrão)'),
    A37 = ('Qtd_REG_CHFUS_RAR' , 'Quantidade de chaves fusíveis usadas em reguladores em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A38 = ('Qtd_REG_CHFUS_RAU' , 'Quantidade de chaves fusíveis usadas em reguladores em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A39 = ('Qtd_REG_CRZT_ESC_RAR' , 'Quantidade de cruzetas usadas em suporte de escada em reguladores em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A40 = ('Qtd_REG_CRZT_ESC_RAU' , 'Quantidade de cruzetas usadas em suporte de escada em reguladores em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A41 = ('Qtd_REG_CRZT_REG_RAR' , 'Quantidade de cruzetas usadas em suporte de reguladores em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A42 = ('Qtd_REG_CRZT_REG_RAU' , 'Quantidade de cruzetas usadas em suporte de reguladores em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A43 = ('Qtd_REG_HA_RAR' , 'Quantidade de hastes de aterramento usadas em reguladores em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A44 = ('Qtd_REG_HA_RAU' , 'Quantidade de hastes de aterramento usadas em reguladores em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A45 = ('Qtd_REG_PR_RAR' , 'Quantidade de para-raios usado em reguladores em redes aéreas convencionais rural conforme padrão da distribuidora'),
    A46 = ('Qtd_REG_PR_RAU' , 'Quantidade de para-raios usados em reguladores em redes aéreas convencionais urbana conforme padrão da distribuidora'),
    A47 = ('Qtd_REL1_CHFUS_RAR' , 'Quantidade de chaves fusíveis usadas em religadores em redes aéreas convencionais monofásicas urbana conforme padrão da distribuidora'),
    A48 = ('Qtd_REL1_CHFUS_RAU' , 'Quantidade de chaves fusíveis usadas em religadores em redes aéreas convencionais monofásicas rurais conforme padrão da distribuidora'),
    A49 = ('Qtd_REL1_CRZT_CNV_RAR' , 'Quantidade de cruzetas usadas em religadores em redes aéreas convencionais monofásicas urbana conforme padrão da distribuidora'),
    A50 = ('Qtd_REL1_CRZT_CNV_RAU' , 'Quantidade de cruzetas usadas em religadores em redes aéreas convencionais monofásicas rurais conforme padrão da distribuidora'),
    A51 = ('Qtd_REL1_HA_RAR' , 'Quantidade de haste de aterramento usadas em religadores em redes aéreas convencionais monofásicas urbana conforme padrão da distribuidora'),
    A52 = ('Qtd_REL1_HA_RAU' , 'Quantidade de haste de aterramento usadas em religadores em redes aéreas convencionais monofásicas rurais conforme padrão da distribuidora'),
    A53 = ('Qtd_REL1_PR_RAR' , 'Quantidade de para-raios usadas em religadores em redes aéreas convencionais monofásicas urbana conforme padrão da distribuidora'),
    A54 = ('Qtd_REL1_PR_RAU' , 'Quantidade de para-raios usadas em religadores em redes aéreas convencionais monofásicas rurais conforme padrão da distribuidora'),
    A55 = ('Qtd_REL3_CHFUS_RAR' , 'Quantidade de chaves fusíveis usadas em religadores em redes aéreas convencionais trifásicas urbana conforme padrão da distribuidora'),
    A56 = ('Qtd_REL3_CHFUS_RAU' , 'Quantidade de chaves fusíveis usadas em religadores em redes aéreas convencionais trifásicas rurais conforme padrão da distribuidora'),
    A57 = ('Qtd_REL3_CRZT_CNV_RAR' , 'Quantidade de cruzetas usadas em religadores em redes aéreas convencionais trifásicas urbana conforme padrão da distribuidora'),
    A58 = ('Qtd_REL3_CRZT_CNV_RAU' , 'Quantidade de cruzetas usadas em religadores em redes aéreas convencionais trifásicas rurais conforme padrão da distribuidora'),
    A59 = ('Qtd_REL3_HA_RAR' , 'Quantidade de haste de aterramento usadas em religadores em redes aéreas convencionais trifásicas urbana conforme padrão da distribuidora'),
    A60 = ('Qtd_REL3_HA_RAU' , 'Quantidade de haste de aterramento usadas em religadores em redes aéreas convencionais trifásicas rurais conforme padrão da distribuidora'),
    A61 = ('Qtd_REL3_PR_RAR' , 'Quantidade de para-raios usadas em religadores em redes aéreas convencionais trifásicas urbana conforme padrão da distribuidora'),
    A62 = ('Qtd_REL3_PR_RAU' , 'Quantidade de para-raios usadas em religadores em redes aéreas convencionais trifásicas rurais conforme padrão da distribuidora'),
    A63 = ('Qtd_SECC1_CHFUS_RAR' , 'Quantidade chaves fusíveis por seccionalizador monofásico em redes aéreas rurais'),
    A64 = ('Qtd_SECC1_CHFUS_RAU' , 'Quantidade chaves fusíveis por seccionalizador monofásico em redes aéreas urbanas'),
    A65 = ('Qtd_SECC1_CRZT_CH_RAR' , 'Quantidade cruzetas por seccionalizador monofásico em redes aéreas rurais'),
    A66 = ('Qtd_SECC1_CRZT_CH_RAU' , 'Quantidade cruzetas por seccionalizador monofásico em redes aéreas urbanas'),
    A67 = ('Qtd_SECC1_HA_RAR' , 'Quantidade hastes de aterramento por seccionalizador monofásico em redes aéreas rurais'),
    A68 = ('Qtd_SECC1_HA_RAU' , 'Quantidade hastes de aterramento por seccionalizador monofásico em redes aéreas urbanas'),
    A69 = ('Qtd_SECC1_PR_RAR' , 'Quantidade para-raios por seccionalizador monofásico em redes aéreas rurais'),
    A70 = ('Qtd_SECC1_PR_RAU' , 'Quantidade para-raios por seccionalizador monofásico em redes aéreas urbanas'),
    A71 = ('Qtd_SECC3_CHFUS_RAR' , 'Quantidade chaves fusíveis por seccionalizador trifásico em redes aéreas rurais'),
    A72 = ('Qtd_SECC3_CHFUS_RAU' , 'Quantidade chaves fusíveis por seccionalizador trifásico em redes aéreas urbanas'),
    A73 = ('Qtd_SECC3_CRZT_CH_RAR' , 'Quantidade cruzetas por seccionalizador trifásico em redes aéreas rurais'),
    A74 = ('Qtd_SECC3_CRZT_CH_RAU' , 'Quantidade cruzetas por seccionalizador trifásico em redes aéreas urbanas'),
    A75 = ('Qtd_SECC3_HA_RAR' , 'Quantidade hastes de aterramento por seccionalizador trifásico em redes aéreas rurais'),
    A76 = ('Qtd_SECC3_HA_RAU' , 'Quantidade hastes de aterramento por seccionalizador trifásico em redes aéreas urbanas'),
    A77 = ('Qtd_SECC3_PR_RAR' , 'Quantidade para-raios por seccionalizador trifásico em redes aéreas rurais'),
    A78 = ('Qtd_SECC3_PR_RAU' , 'Quantidade para-raios por seccionalizador trifásico em redes aéreas urbanas'),
    A79 = ('Qtd_TRD1_CHFUS_RAR' , 'Quantidade chaves fusíveis por transformador monofásico em redes aéreas rurais'),
    A80 = ('Qtd_TRD1_CHFUS_RAU' , 'Quantidade chaves fusíveis por transformador monofásico em redes aéreas urbanas'),
    A81 = ('Qtd_TRD1_CRZT_CNV_RAR' , 'Quantidade cruzetas por transformador monofásico em redes aéreas rurais'),
    A82 = ('Qtd_TRD1_CRZT_CNV_RAU' , 'Quantidade cruzetas por transformador monofásico em redes aéreas urbanas'),
    A83 = ('Qtd_TRD1_PR_RAR' , 'Quantidade para-raios por transformador monofásico em redes aéreas rurais'),
    A84 = ('Qtd_TRD1_PR_RAU' , 'Quantidade para-raios por transformador monofásico em redes aéreas urbanas'),
    A85 = ('Qtd_TRD2_CHFUS_RAR' , 'Quantidade chaves fusíveis por transformador bifásico em redes aéreas rurais'),
    A86 = ('Qtd_TRD2_CHFUS_RAU' , 'Quantidade chaves fusíveis por transformador bifásico em redes aéreas urbanas'),
    A87 = ('Qtd_TRD2_CRZT_CNV_RAR' , 'Quantidade cruzetas por transformador bifásico em redes aéreas rurais'),
    A88 = ('Qtd_TRD2_CRZT_CNV_RAU' , 'Quantidade cruzetas por transformador bifásico em redes aéreas urbanas'),
    A89 = ('Qtd_TRD2_PR_RAR' , 'Quantidade para-raios por transformador bifásico em redes aéreas rurais'),
    A90 = ('Qtd_TRD2_PR_RAU' , 'Quantidade para-raios por transformador bifásico em redes aéreas urbanas'),
    A91 = ('Qtd_TRD3_CHFUS_RAR' , 'Quantidade chaves fusíveis por transformador trifásico em redes aéreas rurais'),
    A92 = ('Qtd_TRD3_CHFUS_RAU' , 'Quantidade chaves fusíveis por transformador trifásico em redes aéreas urbanas'),
    A93 = ('Qtd_TRD3_CRZT_CNV_RAR' , 'Quantidade cruzetas por transformador trifásico em redes aéreas rurais'),
    A94 = ('Qtd_TRD3_CRZT_CNV_RAU' , 'Quantidade cruzetas por transformador trifásico em redes aéreas urbanas'),
    A95 = ('Qtd_TRD3_PR_RAR' , 'Quantidade para-raios por transformador trifásico em redes aéreas rurais'),
    A96 = ('Qtd_TRD3_PR_RAU' , 'Quantidade para-raios por transformador trifásico em redes aéreas urbanas'),
    A97 = ('VL_VAO_RDR' , 'Distância entre vãos em redes aéreas rurais'),
    A98 = ('VL_VAO_RDU' , 'Distância entre vãos em redes aéreas urbanas'),
    A99 = ('VL_VAO_MIN_RAU' , 'Distância mínima para vão da distribuidora em rede aérea urbana'),
    A100 = ('VL_VAO_MIN_RAR' , 'Distância mínima para vão da distribuidora em rede aérea rural'),
    A101 = ('VL_RAM_MIN_RAU' , 'Distância mínima para ramal da distribuidora, em rede aérea urbana'),
    A102 = ('VL_RAM_MIN_RAR' , 'Distância mínima para ramal da distribuidora, em rede aérea rural'),
    A103 = ('Qtd_TRD1_HA_RAU' , 'Quantidade por por transformador monofásico em redes aéreas urbanas'),
    A104 = ('Qtd_TRD2_HA_RAU' , 'Quantidade por por transformador bifásico em redes aéreas urbanas'),
    A105 = ('Qtd_TRD3_HA_RAU' , 'Quantidade por por transformador trifásico em redes aéreas urbanas'),
    A106 = ('Qtd_TRD1_HA_RAR' , 'Quantidade por por transformador monofásico em redes aéreas rural'),
    A107 = ('Qtd_TRD2_HA_RAR' , 'Quantidade por por transformador bifásico em redes aéreas rural'),
    A108 = ('Qtd_TRD3_HA_RAR' , 'Quantidade por por transformador trifásico em redes aéreas rural'),
    A109 = ('Qtd_MAX_CRUZT_PST_RAR' , 'Quantidade máxima de cruzetas por poste em rede aérea rural'),
    A110 = ('Qtd_MAX_CRUZT_PST_RAU' , 'Quantidade máxima de cruzetas por poste em rede aérea urbana'),
    A111 = ('Qtd_MAX_ISOL_DIS_PST_RDR' , 'Quantidade máxima de isoladores de disco por poste em rede aérea rural'),
    A112 = ('Qtd_MAX_ISOL_DIS_PST_RDU' , 'Quantidade máxima de isoladores de disco por poste em rede aérea urbana'),
    A113 = ('Qtd_MAX_ISOL_PIN_PST_RDR' , 'Quantidade máxima de isoladores de pino por poste em rede aérea rural'),
    A114 = ('Qtd_MAX_ISOL_PIN_PST_RDU' , 'Quantidade máxima de isoladores de pino por poste em rede aérea urbana'),
    
    def __new__(cls, valor):
        codigo, descricao = valor
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def descricao(self) -> str:
        return self._descricao

    @classmethod
    def teste(cls, codigo: str) -> bool:
        return codigo in cls._codigos()

    @classmethod
    def descricao_por_codigo(cls, codigo: str) -> str | None:
        return cls._mapa().get(codigo)

    @classmethod
    def _mapa(cls) -> dict[str, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache

    @classmethod
    def _codigos(cls) -> set[str]:
        return set(cls._mapa().keys())

class ValoresTPSERV(Enum):
    A1 = ('1','Aferição'),
    A2 = ('2','Desativação'),
    A3 = ('3','Instalação'),
    A4 = ('4','Ligação'),
    A5 = ('5','Gerenciamento'),
    A6 = ('6','Substituição'),
    A7 = ('7','Vistoria'),
    A8 = ('8','Projeto'),
    A9 = ('9','Montagem'),
    A10 = ('10','Construção'),
    A11 = ('11','Outros'),
    
    def __new__(cls, valor):
        codigo, descricao = valor
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def descricao(self) -> str:
        return self._descricao

    @classmethod
    def teste(cls, codigo: str) -> bool:
        return codigo in cls._codigos()

    @classmethod
    def descricao_por_codigo(cls, codigo: str) -> str | None:
        return cls._mapa().get(codigo)

    @classmethod
    def _mapa(cls) -> dict[str, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache

    @classmethod
    def _codigos(cls) -> set[str]:
        return set(cls._mapa().keys())

class ValoresRACCOM(Enum):
    A1 = ('1','Condutor Nu (rede primária)'),
    A2 = ('2','Condutor Isolado (rede primária)'),
    A3 = ('3','Banco de Capacitores'),
    A4 = ('4','Chave Fusível'),
    A5 = ('5','Chave Seccionadora'),
    A6 = ('6','Chave Seccionadora Carga'),
    A7 = ('7','Cruzeta'),
    A8 = ('8','Haste de Aterramento'),
    A9 = ('9','Isolador Disco'),
    A10 = ('10','Isolador Pino'),
    A11 = ('11','Para-raios'),
    A12 = ('12','Pino'),
    A13 = ('13','Poste'),
    A14 = ('14','Regulador de Tensão'),
    A15 = ('15','Religador Monofásico'),
    A16 = ('16','Religador Trifásico'),
    A17 = ('17','Seccionalizador de cerca'),
    A18 = ('18','Seccionalizador Monofásico'),
    A19 = ('19','Seccionalizador Trifásico'),
    A20 = ('20','Torre'),
    A21 = ('21','Transformador Distribuição Bifásico'),
    A22 = ('22','Transformador Distribuição Monofásico'),
    A23 = ('23','Transformador Distribuição Trifásico'),
    
    def __new__(cls, valor):
        codigo, descricao = valor
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def descricao(self) -> str:
        return self._descricao

    @classmethod
    def teste(cls, codigo: str) -> bool:
        return codigo in cls._codigos()

    @classmethod
    def descricao_por_codigo(cls, codigo: str) -> str | None:
        return cls._mapa().get(codigo)

    @classmethod
    def _mapa(cls) -> dict[str, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache

    @classmethod
    def _codigos(cls) -> set[str]:
        return set(cls._mapa().keys())

class ValoresTUC(Enum):
    A1 = (100, 'ARMAZENAGEM, MANIPULACAO E TRANSPORTE DE COMBUSTIVEL LIQUIDO OU GASOSO')
    A2 = (105, 'ARMAZENAGEM, MANIPULACAO E TRANSPORTE DE COMBUSTIVEL NUCLEAR')
    A3 = (110, 'ARMAZENAGEM, MANIPULACAO E TRANSPORTE DE COMBUSTIVEL SOLIDO')
    A4 = (112, 'ARMAZENAGEM, MANIPULACAO E TRANSPORTE DE RESIDUO')
    A5 = (115, 'ARMAZENAGEM, MANIPULACAO E TRANSPORTE DE RESIDUO NUCLEAR')
    A6 = (120, 'BALANCA PARA VEICULOS DE CARGA')
    A7 = (125, 'BANCO DE CAPACITORES PARALELOS')
    A8 = (130, 'BANCO DE CAPACITORES SERIES')
    A9 = (135, 'BARRAMENTO')
    A10 = (140, 'CALDEIRA')
    A11 = (145, 'CAMARA E GALERIA')
    A12 = (150, 'CANAL DE DESCARGA')
    A13 = (155, 'CHAMINE')
    A14 = (160, 'CHAVE')
    A15 = (165, 'COMPENSADOR DE REATIVOS')
    A16 = (170, 'COMPORTA')
    A17 = (175, 'CONDENSADOR DE VAPOR')
    A18 = (180, 'CONDUTO E CANALETA')
    A19 = (185, 'CONDUTO FORCADO')
    A20 = (190, 'CONDUTOR')
    A21 = (195, 'CONVERSOR DE CORRENTE')
    A22 = (200, 'CONVERSOR DE FREQUENCIA')
    A23 = (205, 'DIREITO, MARCA E PATENTE')
    A24 = (210, 'DISJUNTOR')
    A25 = (215, 'EDIFICACAO')
    A26 = (220, 'ELEVADOR E TELEFERICO')
    A27 = (225, 'ENVOLTORIO OU ESFERA DE CONTENCAO DO EDIFICIO DO REATOR NUCLEAR')
    A28 = (230, 'EQUIPAMENTO GERAL')
    A29 = (235, 'EQUIPAMENTO GERAL DE INFORMATICA')
    A30 = (240, 'EQUIPAMENTOS DA TOMADA DAGUA')
    A31 = (245, 'EQUIPAMENTOS DO CICLO TERMICO')
    A32 = (250, 'ESTRADA DE ACESSO')
    A33 = (255, 'ESTRUTURA, POSTE ou TORRE')
    A34 = (260, 'ESTRUTURA DA TOMADA DAGUA')
    A35 = (265, 'ESTRUTURA SUPORTE DE EQUIPAMENTO E DE BARRAMENTO')
    A36 = (270, 'FIBRA OTICA')
    A37 = (275, 'GERADOR')
    A38 = (280, 'GERADOR DE VAPOR')
    A39 = (285, 'INSTALACOES DE RECREACAO E LAZER')
    A40 = (290, 'LUMINARIA')
    A41 = (295, 'MEDIDOR')
    A42 = (300, 'MOTOR DE COMBUSTAO INTERNA')
    A43 = (305, 'PAINEL, MESA DE COMANDO E CUBICULO')
    A44 = (310, 'PARARAIOS')
    A45 = (315, 'PONTE ROLANTE, GUINDASTE OU PORTICO')
    A46 = (320, 'PRECIPITADOR DE RESIDUOS, DESSULFURIZADOR')
    A47 = (325, 'PROTETOR DE REDE')
    A48 = (330, 'REATOR OU RESISTOR')
    A49 = (335, 'REATOR NUCLEAR')
    A50 = (340, 'REGULADOR DE TENSAO')
    A51 = (345, 'RELIGADOR')
    A52 = (350, 'RESERVATORIO, BARRAGEM E ADUTORA')
    A53 = (355, 'SISTEMA ANTIRUIDO')
    A54 = (360, 'SISTEMA DE ABASTECIMENTO DE AGUA')
    A55 = (365, 'SISTEMA DE AGUA DE ALIMENTACAO')
    A56 = (370, 'SISTEMA DE AGUA DE CIRCULACAO')
    A57 = (375, 'SISTEMA DE ALIMENTACAO DE ENERGIA')
    A58 = (380, 'SISTEMA DE AMOSTRAGEM PRIMARIO')
    A59 = (385, 'SISTEMA DE AR COMPRIMIDO')
    A60 = (390, 'SISTEMA DE AR E GASES DE COMBUSTAO')
    A61 = (395, 'SISTEMA DE ATERRAMENTO')
    A62 = (400, 'SISTEMA DE COLETA DE OLEO ISOLANTE')
    A63 = (405, 'SISTEMA DE COLETA E TRATAMENTO DE LIXO')
    A64 = (410, 'SISTEMA DE COMUNICACAO E PROTECAO CARRIER')
    A65 = (415, 'SISTEMA DE COMUNICACAO LOCAL')
    A66 = (420, 'SISTEMA DE CONDENSADO PARA PRODUCAO NUCLEAR')
    A67 = (425, 'SISTEMA DE CONTROLE QUIMICO E VOLUMETRICO')
    A68 = (430, 'SISTEMA DE DADOS METEOROLOGICOS, HIDROLOGICOS E SISMOLOGICOS')
    A69 = (435, 'SISTEMA DE DESCONTAMINACAO PARA PRODUCAO NUCLEAR')
    A70 = (440, 'SISTEMA DE DOSAGEM QUIMICA PARA PRODUCAO NUCLEAR')
    A71 = (445, 'SISTEMA DE DRENAGEM')
    A72 = (450, 'SISTEMA DE ESGOTO SANITARIO')
    A73 = (455, 'SISTEMA DE EXAUSTAO, VENTILACAO E AR CONDICIONADO')
    A74 = (460, 'SISTEMA DE ILUMINACAO E FORCA')
    A75 = (465, 'SISTEMA DE LUBRIFICACAO, DE OLEO DE REGULACAO E DE OLEO ISOLANTE OU PARA ISOLAMENTO')
    A76 = (470, 'SISTEMA DE MONITORACAO DA USINA')
    A77 = (475, 'SISTEMA DE MONITORACAO DO CIRCUITO PRIMARIO PARA PRODUCAO NUCLEAR')
    A78 = (480, 'SISTEMA DE PROTECAO CONTRA INCENDIO')
    A79 = (485, 'SISTEMA DE PROTECAO, MEDICAO E AUTOMACAO')
    A80 = (490, 'SISTEMA DE PULVERIZACAO DO ENVOLTORIO DE CONTENCAO')
    A81 = (495, 'SISTEMA DE RADIOCOMUNICACAO')
    A82 = (500, 'SISTEMA DE REFRIGERACAO DE EMERGENCIA DO NUCLEO DO REATOR')
    A83 = (505, 'SISTEMA DE REFRIGERACAO DO REATOR')
    A84 = (510, 'SISTEMA DE REFRIGERACAO E PURIFICACAO DO POCO DE COMBUSTIVEL USADO')
    A85 = (515, 'SISTEMA DE RESFRIAMENTO DE EQUIPAMENTOS')
    A86 = (520, 'SISTEMA DE VIGILANCIA ELETRONICA')
    A87 = (525, 'SISTEMA PARA GASEIFICACAO DE CARVAO')
    A88 = (530, 'SISTEMA DE VAPOR PARA PRODUCAO NUCLEAR')
    A89 = (535, 'SOFTWARE')
    A90 = (540, 'SUBESTACAO SF6')
    A91 = (545, 'SUBESTACAO UNITARIA')
    A92 = (550, 'SUPRIMENTO E TRATAMENTO DAGUA')
    A93 = (555, 'TERRENO')
    A94 = (560, 'TRANSFORMADOR DE ATERRAMENTO')
    A95 = (565, 'TRANSFORMADOR DE DISTRIBUICAO')
    A96 = (570, 'TRANSFORMADOR DE FORCA')
    A97 = (575, 'TRANSFORMADOR DE MEDIDA')
    A98 = (580, 'TRANSFORMADOR DE SERVICOS AUXILIARES')
    A99 = (585, 'TURBINA A GAS AERODERIVADO')
    A100 = (590, 'TURBINA EOLICA, AEROGERADOR')
    A101 = (595, 'TURBINA HIDRAULICA')
    A102 = (600, 'TURBINA A VAPOR, TURBO GERADOR')
    A103 = (605, 'UNIDADE DE GERACAO SOLAR FOTOVOLTAICA')
    A104 = (610, 'URBANIZACAO E BENFEITORIAS')
    A105 = (615, 'VEICULOS')
    A106 = (0, 'NA')
    
    def __init__(self, codigo: int, descricao: str):
        self._codigo = codigo
        self._descricao = descricao

    @property
    def codigo(self) -> int:
        return self._codigo

    @property
    def descricao(self) -> str:
        return self._descricao

    @classmethod
    def teste(cls, nro: int) -> bool:
        return nro in cls._codigos()

    @classmethod
    def descricao_por_codigo(cls, nro: int) -> str:
        return cls._mapa().get(nro)

    @classmethod
    def _mapa(cls) -> dict[int, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache

    @classmethod
    def _codigos(cls) -> set[int]:
        return set(cls._mapa().keys())


class ValoresTI(Enum):
    A1 = (10, 'Hidroelétrica'),
    A2 = (11, 'Térmica a Combustão – Óleo/Gás/Diesel'),
    A3 = (12, 'Térmica a Vapor – Carvão'),
    A4 = (13, 'Térmica a Vapor – Gás'),
    A5 = (14, 'Térmica a Vapor – Diesel/Querosene/Óleo'),
    A6 = (15, 'Térmica a Vapor – Biomassa'),
    A7 = (16, 'Térmica a Vapor – Nuclear'),
    A8 = (17, 'Solar'),
    A9 = (18, 'Eólica'),
    A10 = (19, 'Outras'),
    A11 = (20, 'Subestações em tensão menor que 230kV (DIT)'),
    A12 = (21, 'Subestações em tensão maior ou igual a 230kV e menor que 345kV'),
    A13 = (22, 'Subestações em tensão maior ou igual a 345kV e menor que 500kV'),
    A14 = (23, 'Subestações em tensão maior ou igual a 500kV'),
    A15 = (24, 'Linha de Transmissão em tensão menor que 138kV (DIT)'),
    A16 = (25, 'Linha de Transmissão em tensão maior ou igual a 138kV e menor que 230kV (DIT)'),
    A17 = (26, 'Linha de Transmissão em tensão maior ou igual a 230kV e menor que 345kV'),
    A18 = (27, 'Linha de Transmissão em tensão maior ou igual a 345kV e menor que 500kV'),
    A19 = (28, 'Linha de Transmissão em tensão maior ou igual a 500kV'),
    A20 = (29, 'Instalação de Transmissão de Interesse Restrito (Subestação ou Linha)'),
    A21 = (30, 'Subestações em tensão menor ou igual que 13,8kV'),
    A22 = (31, 'Subestações em tensão maior que 13,8kV e menor ou igual a 34,5kV'),
    A23 = (32, 'Subestações em tensão maior que 34,5kV e menor ou igual a 69kV'),
    A24 = (33, 'Subestações em tensão maior que 69kV e menor ou igual a 138kV'),
    A25 = (34, 'Subestações em tensão maior que 138kV e menor ou igual a 230kV'),
    A26 = (35, 'Linha de Distribuição em tensão menor ou igual que 13,8kV'),
    A27 = (36, 'Linha de Distribuição em tensão maior que 13,8kV e menor ou igual a 34,5kV'),
    A28 = (37, 'Linha de Distribuição em tensão maior que 34,5kV e menor ou igual a 69kV'),
    A29 = (38, 'Linha de Distribuição em tensão maior que 69kV e menor ou igual a 138 kV'),
    A30 = (39, 'Linha de Distribuição em tensão maior que 138kV e menor ou igual a 230kV'),
    A31 = (40, 'Redes de Distribuição Aérea Urbana'),
    A32 = (41, 'Redes de Distribuição Aérea Rural'),
    A33 = (42, 'Redes de Distribuição Subterrânea Urbana'),
    A34 = (43, 'Redes de Distribuição Subterrânea Rural'),
    A35 = (44, 'Redes de Distribuição Submersa'),
    A36 = (50, 'Subestações em tensão menor ou igual que 13,8kV'),
    A37 = (51, 'Subestações em tensão maior que 13,8kV e menor ou igual a 34,5kV'),
    A38 = (52, 'Subestações em tensão maior que 34,5kV e menor ou igual a 69kV'),
    A39 = (53, 'Subestações em tensão maior que 69kV e menor ou igual a 138kV'),
    A40 = (54, 'Subestações em tensão maior que 138kV e menor ou igual a 230kV'),
    A41 = (55, 'Linha de Distribuição em tensão menor ou igual que 13,8kV'),
    A42 = (56, 'Linha de Distribuição em tensão maior que 13,8kV e menor ou igual a 34,5kV'),
    A43 = (57, 'Linha de Distribuição em tensão maior que 34,5kV e menor ou igual a 69kV'),
    A44 = (58, 'Linha de Distribuição em tensão maior que 69kV e menor ou igual a 138 kV'),
    A45 = (59, 'Linha de Distribuição em tensão maior que 138kV e menor ou igual a 230kV'),
    A46 = (60, 'Linha de Transmissão em tensão menor que 138kV (DIT)'),
    A47 = (61, 'Linha de Transmissão em tensão maior ou igual a 138kV e menor que 230kV (DIT)'),
    A48 = (62, 'Linha de Transmissão em tensão maior ou igual a 230kV e menor que 345kV'),
    A49 = (63, 'Linha de Transmissão em tensão maior ou igual a 345kV e menor que 500kV'),
    A50 = (64, 'Linha de Transmissão em tensão maior ou igual a 500kV'),
    A51 = (65, 'Linha de Distribuição em tensão menor ou igual que 13,8kV'),
    A52 = (66, 'Linha de Distribuição em tensão maior que 13,8kV e menor ou igual a 34,5kV'),
    A53 = (67, 'Linha de Distribuição em tensão maior que 34,5kV e menor ou igual a 69kV'),
    A54 = (68, 'Linha de Distribuição em tensão maior que 69kV e menor ou igual a 138 kV'),
    A55 = (69, 'Linha de Distribuição em tensão maior que 138kV e menor ou igual a 230kV'),
    A56 = (70, 'Terrenos, edificações, obras civis e benfeitorias da Administração Central'),
    A57 = (71, 'Equipamento geral, o equipamento geral de informática e veículos da Administração Central'),
    A58 = (72, 'Sistema de Comunicação da Administração Central'),
    A59 = (80, 'Terrenos, edificações, obras civis e benfeitorias da Administração Específica'),
    A60 = (81, 'Equipamento geral, o equipamento geral de informática e veículos da Administração Específica'),
    A61 = (82, 'Sistema de Comunicação da Administração Específica'),
    A62 = (90, 'Terrenos, edificações, obras civis e benfeitorias que não integram outras ODI'),
    A63 = (91, 'Equipamento geral, o equipamento geral de informática e veículos que não integram ODI específicas'),
    A64 = (92, 'Sistemas de telecomunicação, telecontrole, teleprocessamento, proteção, controle e supervisão - Automação; cada sistema de comunicação (exceto o sistema de ondas portadoras “Carrier” que integra as ODI de Subestações e os sistemas de comunicação que integram as ODI Adm. Central e Adm. Específica)'),
    A65 = (93, 'Sistema de medição (que não integram as ODI de Usinas e de SE) área urbana'),
    A66 = (96, 'Sistema de medição (que não integram as ODI de Usinas e de SE) – área rural'),
    A67 = (94, 'Serviços Auxiliares gerais, inclusive Oficinas Eletromecânicas, Laboratórios e seus equipamentos'),
    A68 = (95, 'Apoio Operacional (exclusivo para ODI específicas de Usina e Subestação)'),
    A69 = (97, 'Sistema de despacho de carga'),
    A70 = (98, 'Reserva imobilizada (exceto equipamentos reservas exclusivos de usinas e subestações que integram ODI específicas)'),
    A71 = (99, 'Intangível (exceto servidões, que integram a ODI específica a que pertence)'),

    def __new__(cls, valor):
        codigo, descricao = valor
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def descricao(self) -> str:
        return self._descricao

    @classmethod
    def teste(cls, codigo: str) -> bool:
        return codigo in cls._codigos()

    @classmethod
    def descricao_por_codigo(cls, codigo: str) -> str | None:
        return cls._mapa().get(codigo)

    @classmethod
    def _mapa(cls) -> dict[str, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache

    @classmethod
    def _codigos(cls) -> set[str]:
        return set(cls._mapa().keys())
    
class ValoresCC(Enum):
    A1 = ('123310101','Geração','Usinas','Servidões permanentes','BRR','1.1','AIS'),
    A2 = ('123310103','Geração','Usinas','Softwares','BAR','1.2','AIS'),
    A3 = ('123310199','Geração','Usinas','Outros','BAR','1.3','AIS'),
    A4 = ('123210101','Geração','Usinas','Terrenos','BRR','2.1','AIS'),
    A5 = ('123210102','Geração','Usinas','Reservatórios, barragens e adutoras','BRR','3','AIS'),
    A6 = ('123210103','Geração','Usinas','Edificações, obras civis e benfeitorias','BRR','4.1','AIS'),
    A7 = ('123210104','Geração','Usinas','Máquinas e equipamentos','BRR','5.1','AIS'),
    A8 = ('123210105','Geração','Usinas','Veículos','BAR','6.1','AIS'),
    A9 = ('123210106','Geração','Usinas','Móveis e utensílios','BAR','7.1','AIS'),
    A10 = ('123310401','Geração','Sistema de transmissão de conexão','Servidões permanentes','BRR','1.1','AIS'),
    A11 = ('123310403','Geração','Sistema de transmissão de conexão','Softwares','BAR','1.2','AIS'),
    A12 = ('123310499','Geração','Sistema de transmissão de conexão','Outros','BAR','1.3','AIS'),
    A13 = ('123210401','Geração','Sistema de transmissão de conexão','Terrenos','BRR','2.1','AIS'),
    A14 = ('123210402','Geração','Sistema de transmissão de conexão','Reservatórios, barragens e adutoras','BRR','3','AIS'),
    A15 = ('123210403','Geração','Sistema de transmissão de conexão','Edificações, obras civis e benfeitorias','BRR','4.1','AIS'),
    A16 = ('123210404','Geração','Sistema de transmissão de conexão','Máquinas e equipamentos','BRR','5.1','AIS'),
    A17 = ('123210405','Geração','Sistema de transmissão de conexão','Veículos','BAR','6.1','AIS'),
    A18 = ('123210406','Geração','Sistema de transmissão de conexão','Móveis e utensílios','BAR','7.1','AIS'),
    A19 = ('123320101','Transmissão','Rede básica','Servidões permanentes','BRR','1.1','AIS'),
    A20 = ('123320103','Transmissão','Rede básica','Softwares','BAR','1.2','AIS'),
    A21 = ('123320199','Transmissão','Rede básica','Outros','BAR','1.3','AIS'),
    A22 = ('123220101','Transmissão','Rede básica','Terrenos','BRR','2.5','AIS'),
    A23 = ('123220103','Transmissão','Rede básica','Edificações, obras civis e benfeitorias','BRR','4.5','AIS'),
    A24 = ('123220104','Transmissão','Rede básica','Máquinas e equipamentos','BRR','5.5','AIS'),
    A25 = ('123220105','Transmissão','Rede básica','Veículos','BAR','6.5','AIS'),
    A26 = ('123220106','Transmissão','Rede básica','Móveis e utensílios','BAR','7.5','AIS'),
    A27 = ('123320401','Transmissão','Demais instalações / Demais instalações de transmissão','Servidões permanentes','BRR','1.1','AIS'),
    A28 = ('123320403','Transmissão','Demais instalações / Demais instalações de transmissão','Softwares','BAR','1.2','AIS'),
    A29 = ('123320499','Transmissão','Demais instalações / Demais instalações de transmissão','Outros','BAR','1.3','AIS'),
    A30 = ('123220401','Transmissão','Demais instalações / Demais instalações de transmissão','Terrenos','BRR','2.5','AIS'),
    A31 = ('123220403','Transmissão','Demais instalações / Demais instalações de transmissão','Edificações, obras civis e benfeitorias','BRR','4.5','AIS'),
    A32 = ('123220404','Transmissão','Demais instalações / Demais instalações de transmissão','Máquinas e equipamentos','BRR','5.5','AIS'),
    A33 = ('123220405','Transmissão','Demais instalações / Demais instalações de transmissão','Veículos','BAR','6.5','AIS'),
    A34 = ('123220406','Transmissão','Demais instalações / Demais instalações de transmissão','Móveis e utensílios','BAR','7.5','AIS'),
    A35 = ('123330101','Distribuição','Linhas, Redes e Subestações','Servidões permanentes','BRR','1.1','AIS'),
    A36 = ('123330103','Distribuição','Linhas, Redes e Subestações','Softwares','BAR','1.2','AIS'),
    A37 = ('123330199','Distribuição','Linhas, Redes e Subestações','Outros','BAR','1.3','AIS'),
    A38 = ('123230101','Distribuição','Linhas, Redes e Subestações','Terrenos','BRR','2.2','AIS'),
    A39 = ('123230103','Distribuição','Linhas, Redes e Subestações','Edificações, obras civis e benfeitorias','BRR','4.2','AIS'),
    A40 = ('123230104','Distribuição','Linhas, Redes e Subestações','Máquinas e equipamentos','BRR','5.2','AIS'),
    A41 = ('123230105','Distribuição','Linhas, Redes e Subestações','Veículos','BAR','6.2','AIS'),
    A42 = ('123230106','Distribuição','Linhas, Redes e Subestações','Móveis e utensílios','BAR','7.2','AIS'),
    A43 = ('123330401','Distribuição','Sistema de transmissão associado','Servidões permanentes','BRR','1.1','AIS'),
    A44 = ('123330403','Distribuição','Sistema de transmissão associado','Softwares','BAR','1.2','AIS'),
    A45 = ('123330499','Distribuição','Sistema de transmissão associado','Outros','BAR','1.3','AIS'),
    A46 = ('123230401','Distribuição','Sistema de transmissão associado','Terrenos','BRR','2.2','AIS'),
    A47 = ('123230403','Distribuição','Sistema de transmissão associado','Edificações, obras civis e benfeitorias','BRR','4.2','AIS'),
    A48 = ('123230404','Distribuição','Sistema de transmissão associado','Máquinas e equipamentos','BRR','5.2','AIS'),
    A49 = ('123230405','Distribuição','Sistema de transmissão associado','Veículos','BAR','6.2','AIS'),
    A50 = ('123230406','Distribuição','Sistema de transmissão associado','Móveis e utensílios','BAR','7.2','AIS'),
    A51 = ('123340101','Administração','Administração','Servidões permanentes','BAR','1.1','AIS'),
    A52 = ('123340103','Administração','Administração','Softwares','BAR','1.2','AIS'),
    A53 = ('123340199','Administração','Administração','Outros','BAR','1.3','AIS'),
    A54 = ('123240101','Administração','Administração','Terrenos','BAR','2.3','AIS'),
    A55 = ('123240103','Administração','Administração','Edificações, obras civis e benfeitorias','BAR','4.3','AIS'),
    A56 = ('123240104','Administração','Administração','Máquinas e equipamentos','BAR','5.3','AIS'),
    A57 = ('123240105','Administração','Administração','Veículos','BAR','6.3','AIS'),
    A58 = ('123240106','Administração','Administração','Móveis e utensílios','BAR','7.3','AIS'),
    A59 = ('123350101','Comercialização','Comercialização','Servidões permanentes','BAR','1.1','AIS'),
    A60 = ('123350103','Comercialização','Comercialização','Softwares','BAR','1.2','AIS'),
    A61 = ('123350199','Comercialização','Comercialização','Outros','BAR','1.3','AIS'),
    A62 = ('123250101','Comercialização','Comercialização','Terrenos','BAR','2.4','AIS'),
    A63 = ('123250103','Comercialização','Comercialização','Edificações, obras civis e benfeitorias','BAR','4.4','AIS'),
    A64 = ('123250104','Comercialização','Comercialização','Máquinas e equipamentos','BAR','5.4','AIS'),
    A65 = ('123250105','Comercialização','Comercialização','Veículos','BAR','6.4','AIS'),
    A66 = ('123250106','Comercialização','Comercialização','Móveis e utensílios','BAR','7.4','AIS'),

    
    A67 = ('123310201','Geração','Usinas','Servidões permanentes','BRR','1.1','DEPR_ACM'),
    A68 = ('123310203','Geração','Usinas','Softwares','BAR','1.2','DEPR_ACM'),
    A69 = ('123310299','Geração','Usinas','Outros','BAR','1.3','DEPR_ACM'),
    A70 = ('123210201','Geração','Usinas','Terrenos','BRR','2.1','DEPR_ACM'),
    A71 = ('123210202','Geração','Usinas','Reservatórios, barragens e adutoras','BRR','3','DEPR_ACM'),
    A72 = ('123210203','Geração','Usinas','Edificações, obras civis e benfeitorias','BRR','4.1','DEPR_ACM'),
    A73 = ('123210204','Geração','Usinas','Máquinas e equipamentos','BRR','5.1','DEPR_ACM'),
    A74 = ('123210205','Geração','Usinas','Veículos','BAR','6.1','DEPR_ACM'),
    A75 = ('123210206','Geração','Usinas','Móveis e utensílios','BAR','7.1','DEPR_ACM'),
    
    A76 = ('123320101','Transmissão','Rede básica','Servidões permanentes','BRR','1.1','DEPR_ACM'),
    A77 = ('123320103','Transmissão','Rede básica','Softwares','BAR','1.2','DEPR_ACM'),
    A78 = ('123320199','Transmissão','Rede básica','Outros','BAR','1.3','DEPR_ACM'),
    A79 = ('123220201','Transmissão','Rede básica','Terrenos','BRR','2.5','DEPR_ACM'),
    A80 = ('123220203','Transmissão','Rede básica','Edificações, obras civis e benfeitorias','BRR','4.5','DEPR_ACM'),
    A81 = ('123220204','Transmissão','Rede básica','Máquinas e equipamentos','BRR','5.5','DEPR_ACM'),
    A82 = ('123220205','Transmissão','Rede básica','Veículos','BAR','6.5','DEPR_ACM'),
    A83 = ('123220206','Transmissão','Rede básica','Móveis e utensílios','BAR','7.5','DEPR_ACM'),
    A84 = ('123320501','Transmissão','Demais instalações / Demais instalações de transmissão','Servidões permanentes','BRR','1.1','DEPR_ACM'),
    A85 = ('123320503','Transmissão','Demais instalações / Demais instalações de transmissão','Softwares','BAR','1.2','DEPR_ACM'),
    A86 = ('123320599','Transmissão','Demais instalações / Demais instalações de transmissão','Outros','BAR','1.3','DEPR_ACM'),
    A87 = ('123220501','Transmissão','Demais instalações / Demais instalações de transmissão','Terrenos','BRR','2.5','DEPR_ACM'),
    A88 = ('123220503','Transmissão','Demais instalações / Demais instalações de transmissão','Edificações, obras civis e benfeitorias','BRR','4.5','DEPR_ACM'),
    A89 = ('123220504','Transmissão','Demais instalações / Demais instalações de transmissão','Máquinas e equipamentos','BRR','5.5','DEPR_ACM'),
    A90 = ('123220505','Transmissão','Demais instalações / Demais instalações de transmissão','Veículos','BAR','6.5','DEPR_ACM'),
    A91 = ('123220506','Transmissão','Demais instalações / Demais instalações de transmissão','Móveis e utensílios','BAR','7.5','DEPR_ACM'),

    A92 = ('123330201','Distribuição','Linhas, Redes e Subestações','Servidões permanentes','BRR','1.1','DEPR_ACM'),
    A93 = ('123330203','Distribuição','Linhas, Redes e Subestações','Softwares','BAR','1.2','DEPR_ACM'),
    A94 = ('123330299','Distribuição','Linhas, Redes e Subestações','Outros','BAR','1.3','DEPR_ACM'),
    A95 = ('123230201','Distribuição','Linhas, Redes e Subestações','Terrenos','BRR','2.2','DEPR_ACM'),
    A96 = ('123230203','Distribuição','Linhas, Redes e Subestações','Edificações, obras civis e benfeitorias','BRR','4.2','DEPR_ACM'),
    A97 = ('123230204','Distribuição','Linhas, Redes e Subestações','Máquinas e equipamentos','BRR','5.2','DEPR_ACM'),
    A98 = ('123230205','Distribuição','Linhas, Redes e Subestações','Veículos','BAR','6.2','DEPR_ACM'),
    A99 = ('123230206','Distribuição','Linhas, Redes e Subestações','Móveis e utensílios','BAR','7.2','DEPR_ACM'),
    A100 = ('123330501','Distribuição','Sistema de transmissão associado','Servidões permanentes','BRR','1.1','DEPR_ACM'),
    A101 = ('123330503','Distribuição','Sistema de transmissão associado','Softwares','BAR','1.2','DEPR_ACM'),
    A102 = ('123330599','Distribuição','Sistema de transmissão associado','Outros','BAR','1.3','DEPR_ACM'),
    A103 = ('123230501','Distribuição','Sistema de transmissão associado','Terrenos','BRR','2.2','DEPR_ACM'),
    A104 = ('123230503','Distribuição','Sistema de transmissão associado','Edificações, obras civis e benfeitorias','BRR','4.2','DEPR_ACM'),
    A105 = ('123230504','Distribuição','Sistema de transmissão associado','Máquinas e equipamentos','BRR','5.2','DEPR_ACM'),
    A106 = ('123230505','Distribuição','Sistema de transmissão associado','Veículos','BAR','6.2','DEPR_ACM'),
    A107 = ('123230506','Distribuição','Sistema de transmissão associado','Móveis e utensílios','BAR','7.2','DEPR_ACM'),
    
    A108 = ('123340201','Administração','Administração','Servidões permanentes','BAR','1.1','DEPR_ACM'),
    A109 = ('123340203','Administração','Administração','Softwares','BAR','1.2','DEPR_ACM'),
    A110 = ('123340299','Administração','Administração','Outros','BAR','1.3','DEPR_ACM'),
    A111 = ('123240201','Administração','Administração','Terrenos','BAR','2.3','DEPR_ACM'),
    A112 = ('123240203','Administração','Administração','Edificações, obras civis e benfeitorias','BAR','4.3','DEPR_ACM'),
    A113 = ('123240204','Administração','Administração','Máquinas e equipamentos','BAR','5.3','DEPR_ACM'),
    A114 = ('123240205','Administração','Administração','Veículos','BAR','6.3','DEPR_ACM'),
    A115 = ('123240206','Administração','Administração','Móveis e utensílios','BAR','7.3','DEPR_ACM'),
    A116 = ('123350201','Comercialização','Comercialização','Servidões permanentes','BAR','1.1','DEPR_ACM'),
    A117 = ('123350203','Comercialização','Comercialização','Softwares','BAR','1.2','DEPR_ACM'),
    A118 = ('123350299','Comercialização','Comercialização','Outros','BAR','1.3','DEPR_ACM'),
    A119 = ('123250201','Comercialização','Comercialização','Terrenos','BAR','2.4','DEPR_ACM'),
    A120 = ('123250203','Comercialização','Comercialização','Edificações, obras civis e benfeitorias','BAR','4.4','DEPR_ACM'),
    A121 = ('123250204','Comercialização','Comercialização','Máquinas e equipamentos','BAR','5.4','DEPR_ACM'),
    A122 = ('123250205','Comercialização','Comercialização','Veículos','BAR','6.4','DEPR_ACM'),
    A123 = ('123250206','Comercialização','Comercialização','Móveis e utensílios','BAR','7.4','DEPR_ACM'),
    

    @classmethod
    def teste(cls, nro):
        for valor in cls:
            if valor.value[0][0] == nro:
                return True
        return False
    
    @classmethod
    def testeQ5(cls, nro):
        for valor in cls:
            if valor.value[0][5] == nro:
                return True
        return False

class ValoresCCOE(Enum):
    A0 = ('222310101', 'Participação da União, Estados e Municípios')
    A1 = ('222310102', 'Participação Financeira do Consumidor')
    A2 = ('222310103', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A3 = ('222310104', 'Programa de Eficiência Energética - PEE')
    A4 = ('222310105', 'Pesquisa e Desenvolvimento')
    A5 = ('222310106', 'Universalização do Serviço Público de Energia Elétrica')
    A6 = ('222310199', 'Outros')
    A7 = ('222310201', 'Participação da União, Estados e Municípios')
    A8 = ('222310202', 'Participação Financeira do Consumidor')
    A9 = ('222310203', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A10 = ('222310204', 'Programa de Eficiência Energética - PEE')
    A11 = ('222310205', 'Pesquisa e Desenvolvimento')
    A12 = ('222310206', 'Universalização do Serviço Público de Energia Elétrica')
    A13 = ('222310299', 'Outros')
    A14 = ('222310301', 'Participação da União, Estados e Municípios')
    A15 = ('222310302', 'Participação Financeira do Consumidor')
    A16 = ('222310303', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A17 = ('222310304', 'Programa de Eficiência Energética - PEE')
    A18 = ('222310305', 'Pesquisa e Desenvolvimento')
    A19 = ('222310306', 'Universalização do Serviço Público de Energia Elétrica')
    A20 = ('222310307', 'Valores Pendentes de Recebimento')
    A21 = ('222310308', 'Valores Não Aplicados')
    A22 = ('222310399', 'Outros')
    A23 = ('222310401', 'Participação da União, Estados e Municípios')
    A24 = ('222310402', 'Participação Financeira do Consumidor')
    A25 = ('222310403', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A26 = ('222310404', 'Programa de Eficiência Energética - PEE')
    A27 = ('222310405', 'Pesquisa e Desenvolvimento')
    A28 = ('222310406', 'Universalização do Serviço Público de Energia Elétrica')
    A29 = ('222310499', 'Outros')
    A30 = ('222310501', 'Participação da União, Estados e Municípios')
    A31 = ('222310502', 'Participação Financeira do Consumidor')
    A32 = ('222310503', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A33 = ('222310504', 'Programa de Eficiência Energética - PEE')
    A34 = ('222310505', 'Pesquisa e Desenvolvimento')
    A35 = ('222310506', 'Universalização do Serviço Público de Energia Elétrica')
    A36 = ('222310599', 'Outros')
    A37 = ('222310601', 'Participação da União, Estados e Municípios')
    A38 = ('222310602', 'Participação Financeira do Consumidor')
    A39 = ('222310603', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A40 = ('222310604', 'Programa de Eficiência Energética - PEE')
    A41 = ('222310605', 'Pesquisa e Desenvolvimento')
    A42 = ('222310606', 'Universalização do Serviço Público de Energia Elétrica')
    A43 = ('222310607', 'Valores Pendentes de Recebimento')
    A44 = ('222310608', 'Valores Não Aplicados')
    A45 = ('222310699', 'Outros')
    A46 = ('222320101', 'Participação da União, Estados e Municípios')
    A47 = ('222320102', 'Participação Financeira do Consumidor')
    A48 = ('222320103', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A49 = ('222320104', 'Programa de Eficiência Energética - PEE')
    A50 = ('222320105', 'Pesquisa e Desenvolvimento')
    A51 = ('222320106', 'Universalização do Serviço Público de Energia Elétrica')
    A52 = ('222320199', 'Outros')
    A53 = ('222320201', 'Participação da União, Estados e Municípios')
    A54 = ('222320202', 'Participação Financeira do Consumidor')
    A55 = ('222320203', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A56 = ('222320204', 'Programa de Eficiência Energética - PEE')
    A57 = ('222320205', 'Pesquisa e Desenvolvimento')
    A58 = ('222320206', 'Universalização do Serviço Público de Energia Elétrica')
    A59 = ('222320299', 'Outros')
    A60 = ('222320301', 'Participação da União, Estados e Municípios')
    A61 = ('222320302', 'Participação Financeira do Consumidor')
    A62 = ('222320303', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A63 = ('222320304', 'Programa de Eficiência Energética - PEE')
    A64 = ('222320305', 'Pesquisa e Desenvolvimento')
    A65 = ('222320306', 'Universalização do Serviço Público de Energia Elétrica')
    A66 = ('222320307', 'Valores Pendentes de Recebimento')
    A67 = ('222320308', 'Valores Não Aplicados')
    A68 = ('222320399', 'Outros')
    A69 = ('222320401', 'Participação da União, Estados e Municípios')
    A70 = ('222320402', 'Participação Financeira do Consumidor')
    A71 = ('222320403', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A72 = ('222320404', 'Programa de Eficiência Energética - PEE')
    A73 = ('222320405', 'Pesquisa e Desenvolvimento')
    A74 = ('222320406', 'Universalização do Serviço Público de Energia Elétrica')
    A75 = ('222320499', 'Outros')
    A76 = ('222320501', 'Participação da União, Estados e Municípios')
    A77 = ('222320502', 'Participação Financeira do Consumidor')
    A78 = ('222320503', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A79 = ('222320504', 'Programa de Eficiência Energética - PEE')
    A80 = ('222320505', 'Pesquisa e Desenvolvimento')
    A81 = ('222320506', 'Universalização do Serviço Público de Energia Elétrica')
    A82 = ('222320599', 'Outros')
    A83 = ('222320601', 'Participação da União, Estados e Municípios')
    A84 = ('222320602', 'Participação Financeira do Consumidor')
    A85 = ('222320603', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A86 = ('222320604', 'Programa de Eficiência Energética - PEE')
    A87 = ('222320605', 'Pesquisa e Desenvolvimento')
    A88 = ('222320606', 'Universalização do Serviço Público de Energia Elétrica')
    A89 = ('222320607', 'Valores Pendentes de Recebimento')
    A90 = ('222320608', 'Valores Não Aplicados')
    A91 = ('222320699', 'Outros')
    A92 = ('222330101', 'Participação da União, Estados e Municípios')
    A93 = ('222330102', 'Participação Financeira do Consumidor')
    A94 = ('222330103', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A95 = ('222330104', 'Programa de Eficiência Energética - PEE')
    A96 = ('222330105', 'Pesquisa e Desenvolvimento')
    A97 = ('222330106', 'Universalização do Serviço Público de Energia Elétrica')
    A98 = ('222330199', 'Outros')
    A99 = ('222330201', 'Participação da União, Estados e Municípios')
    A100 = ('222330202', 'Participação Financeira do Consumidor')
    A101 = ('222330203', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A102 = ('222330204', 'Programa de Eficiência Energética - PEE')
    A103 = ('222330205', 'Pesquisa e Desenvolvimento')
    A104 = ('222330206', 'Universalização do Serviço Público de Energia Elétrica')
    A105 = ('222330299', 'Outros')
    A106 = ('222330301', 'Participação da União, Estados e Municípios')
    A107 = ('222330302', 'Participação Financeira do Consumidor')
    A108 = ('222330303', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A109 = ('222330304', 'Programa de Eficiência Energética - PEE')
    A110 = ('222330305', 'Pesquisa e Desenvolvimento')
    A111 = ('222330306', 'Universalização do Serviço Público de Energia Elétrica')
    A112 = ('222330307', 'Valores Pendentes de Recebimento')
    A113 = ('222330308', 'Valores Não Aplicados')
    A114 = ('222330399', 'Outros')
    A115 = ('222330401', 'Participação da União, Estados e Municípios')
    A116 = ('222330402', 'Participação Financeira do Consumidor')
    A117 = ('222330403', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A118 = ('222330404', 'Programa de Eficiência Energética - PEE')
    A119 = ('222330405', 'Pesquisa e Desenvolvimento')
    A120 = ('222330406', 'Universalização do Serviço Público de Energia Elétrica')
    A121 = ('222330499', 'Outros')
    A122 = ('222330501', 'Participação da União, Estados e Municípios')
    A123 = ('222330502', 'Participação Financeira do Consumidor')
    A124 = ('222330503', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A125 = ('222330504', 'Programa de Eficiência Energética - PEE')
    A126 = ('222330505', 'Pesquisa e Desenvolvimento')
    A127 = ('222330506', 'Universalização do Serviço Público de Energia Elétrica')
    A128 = ('222330599', 'Outros')
    A129 = ('222330601', 'Participação da União, Estados e Municípios')
    A130 = ('222330602', 'Participação Financeira do Consumidor')
    A131 = ('222330603', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A132 = ('222330604', 'Programa de Eficiência Energética - PEE')
    A133 = ('222330605', 'Pesquisa e Desenvolvimento')
    A134 = ('222330606', 'Universalização do Serviço Público de Energia Elétrica')
    A135 = ('222330607', 'Valores Pendentes de Recebimento')
    A136 = ('222330608', 'Valores Não Aplicados')
    A137 = ('222330699', 'Outros')
    A138 = ('222340101', 'Participação da União, Estados e Municípios')
    A139 = ('222340102', 'Participação Financeira do Consumidor')
    A140 = ('222340103', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A141 = ('222340104', 'Programa de Eficiência Energética - PEE')
    A142 = ('222340105', 'Pesquisa e Desenvolvimento')
    A143 = ('222340106', 'Universalização do Serviço Público de Energia Elétrica')
    A144 = ('222340199', 'Outros')
    A145 = ('222340201', 'Participação da União, Estados e Municípios')
    A146 = ('222340202', 'Participação Financeira do Consumidor')
    A147 = ('222340203', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A148 = ('222340204', 'Programa de Eficiência Energética - PEE')
    A149 = ('222340205', 'Pesquisa e Desenvolvimento')
    A150 = ('222340206', 'Universalização do Serviço Público de Energia Elétrica')
    A151 = ('222340299', 'Outros')
    A152 = ('222340301', 'Participação da União, Estados e Municípios')
    A153 = ('222340302', 'Participação Financeira do Consumidor')
    A154 = ('222340303', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A155 = ('222340304', 'Programa de Eficiência Energética - PEE')
    A156 = ('222340305', 'Pesquisa e Desenvolvimento')
    A157 = ('222340306', 'Universalização do Serviço Público de Energia Elétrica')
    A158 = ('222340307', 'Valores Pendentes de Recebimento')
    A159 = ('222340308', 'Valores Não Aplicados')
    A160 = ('222340399', 'Outros')
    A161 = ('222350101', 'Participação da União, Estados e Municípios')
    A162 = ('222350102', 'Participação Financeira do Consumidor')
    A163 = ('222350103', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A164 = ('222350104', 'Programa de Eficiência Energética - PEE')
    A165 = ('222350105', 'Pesquisa e Desenvolvimento')
    A166 = ('222350106', 'Universalização do Serviço Público de Energia Elétrica')
    A167 = ('222350199', 'Outros')
    A168 = ('222350201', 'Participação da União, Estados e Municípios')
    A169 = ('222350202', 'Participação Financeira do Consumidor')
    A170 = ('222350203', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A171 = ('222350204', 'Programa de Eficiência Energética - PEE')
    A172 = ('222350205', 'Pesquisa e Desenvolvimento')
    A173 = ('222350206', 'Universalização do Serviço Público de Energia Elétrica')
    A174 = ('222350299', 'Outros')
    A175 = ('222350301', 'Participação da União, Estados e Municípios')
    A176 = ('222350302', 'Participação Financeira do Consumidor')
    A177 = ('222350303', 'Doações e Subvenções Destinadas a Investimentos no Serviço Concedido')
    A178 = ('222350304', 'Programa de Eficiência Energética - PEE')
    A179 = ('222350305', 'Pesquisa e Desenvolvimento')
    A180 = ('222350306', 'Universalização do Serviço Público de Energia Elétrica')
    A181 = ('222350307', 'Valores Pendentes de Recebimento')
    A182 = ('222350308', 'Valores Não Aplicados')
    A183 = ('222350399', 'Outros')
    A185 = ('Tx_MED_AMORT', 'Variável auxiliar para definição da taxa média de amortização do cálculo de movimentação de OE.')

    def __new__(cls, codigo, descricao):
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj
    
    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def descricao(self) -> str:
        return self._descricao

    @classmethod
    def teste(cls, codigo: str) -> bool:
        return codigo in cls._codigos()

    @classmethod
    def descricao_por_codigo(cls, codigo: str) -> str | None:
        return cls._mapa().get(codigo)

    @classmethod
    def _mapa(cls) -> dict[str, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache

    @classmethod
    def _codigos(cls) -> set[str]:
        return set(cls._mapa().keys())

def validar_duplicidades_global(
                                    dados,
                                    vistos,
                                    deslocamento=0,
                                    campo="Cd_SubODI"
                                ):
    erros = []

    for indice, registro in enumerate(dados):
        codigo = registro.get(campo)
        if codigo is None or codigo == "":
            continue

        linha_atual = deslocamento + indice + 2

        if codigo in vistos:
            primeira_linha = vistos[codigo]
            erros.append({
                            "type": "value_error",
                            "loc": ("tabela", indice, campo),
                            "input": codigo,
                            "msg": (
                                f"Duplicidade no campo {campo}. "
                                f"Primeira ocorrência na linha "
                                f"{primeira_linha}."
                            ),
                            "etapa": deslocamento
                        })
        else:
            vistos[codigo] = linha_atual

    return erros

def conv_flut(v) -> float:
    if v is None:
        return 0.0
    s = str(v).strip().replace(",", ".")
    if s == "":
        return 0.0
    return float(s)

def digitos(v) -> str:
    return "".join(ch for ch in str(v or "") if ch.isdigit())

def anl_lcmt(valores):
    n=0
    erros = []
    for chave, value in valores.items():
        if chave not in ['Id_OE_MOV','Id_OE_AMT','Cd_CC', 'Id_OE','Cd_CC','TP_OE','VL_SLD_INI','VL_SLD_REAV','Dt_REF']:
            if (chave[0:7] == "VL_Mes_"): n+=1
            if isinstance(value, str):
                if ('.' in value) and (',' in value):
                    erros.append(f"O campo '{chave}' não deve conter pontos como separadores de milhar.\n")
                try:
                    value_normalizado = float(value.replace(",", ".").strip())
                except ValueError:
                    erros.append(f"O campo '{chave}', tem um dado no formato inválido: {value}. Deve ser um número válido.\n")
            else:
                raise erros.append(f"O campo '{chave}' não é do tipo esperado.\n")
            if isinstance(chave,str):
                if (chave[0:7] != "VL_Mes_") and (chave != 'VL_Total'):
                    erros.append(f"O nome do atributo, {chave}, não segue o padrão solicitado (VL_Mes_xx ou VL_Total).\n")
                if (chave[0:7] == "VL_Mes_"):
                    if int(chave[7:])!=n:
                        erros.append(f"O campo '{chave}' não segue o padrão sequencial esperado: 'VL_Mes_{n}' era esperado.\n")
            else:
                erros.append(f"Atributo não é do tipo esperado.\n")
    return erros

def calc_digito(cnpj, posicao):
    pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    if posicao==1:
        pesos = pesos[1:]
    total = sum(int(cnpj[i]) * pesos[i] for i in range(len(pesos)))
    resto = total % 11
    return 0 if resto < 2 else 11 - resto

def validar_CNPJ(valor: str):
    if isinstance(valor, str):
        if (valor is None) or (isinstance(valor, float) and math.isnan(valor)) or (valor == '') or (str(valor) == '0'):
            return valor
        if len(valor) != 14 or valor == valor[0] * len(valor):
            raise ValueError(f' CNPJ inválido, número de caracteres diferente de 14 ou todos os números iguais.\n')
        try:
            valor_normalizado = int(valor.replace(",", ".").strip())
        except ValueError:
            raise ValueError(f" o valor deve ser um número decimal válido.\n")
        
        PRIDG = calc_digito(valor,1)
        SEGDG = calc_digito(valor,2)
        
        if valor[-2:-1] != str(PRIDG) or valor[-1:] != str(SEGDG):
            raise ValueError(' CNPJ inválido, dígito de verificação não confere.')
        
        return valor
    else:
        raise ValueError(f" o valor não é do tipo esperado.\n")
    
def val_dt(d1, d2):
    if d1==d2:
        return d1
    else:
        raise ValueError(f"Verifique a data de referência informada no arquivo {d1}.")

def validar_decimal(valor, vazio=False, min_val=None, max_val=None):
    if pd.isna(valor):
        if vazio:
            return valor
        raise ValueError("não pode estar vazio.\n")

    valor = str(valor).strip()

    if "." in valor and "," in valor:
        raise ValueError("não use ponto como separador de milhar.\n")

    try:
        num = float(valor.replace(",", "."))
    except ValueError:
        raise ValueError("valor deve ser numérico decimal válido.\n")

    if min_val is not None and num < min_val:
        raise ValueError(f"valor deve ser >= {min_val}.\n")

    if max_val is not None and num > max_val:
        raise ValueError(f"valor deve ser <= {max_val}.\n")

    return valor

def validar_lista(valor,
                  valores_permitidos,
                  descricao="valor",
                  vazio=False):

    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        if vazio:
            return valor
        raise ValueError(f"{descricao} não pode estar vazio.\n")

    v = str(valor).strip()
    exemplo = next(iter(valores_permitidos))

    if v == "" or v.lower() == "nan":
        if vazio:
            return valor
        raise ValueError(f"{descricao} não pode estar vazio.\n")
    
    if isinstance(exemplo, int):
        try:
            valor_int = int(v)
        except ValueError:
            raise ValueError(f"{descricao} deve ser um número inteiro.\n")

    if v not in valores_permitidos:
        raise ValueError(f"{descricao} '{v}' não é um código válido.\n")

    return valor

def validar_data(valor: Optional[str], vazio=False):
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        if vazio: return valor
        raise ValueError(" data não pode estar vazia.\n")

    v = str(valor).strip().lower()
    if v == "" or v == "nan":
        if vazio: return valor
        raise ValueError(" data não pode estar vazia.\n")
    valor = str(valor).strip()
    if not re.match(r'^\d{4}/\d{2}/\d{2}$', valor):
        raise ValueError(" data deve estar no formato aaaa/mm/dd.\n")
    try:
        data = datetime.strptime(valor, "%Y/%m/%d").date()
    except ValueError:
        raise ValueError(" data inválida.\n")
    return valor

def validar_texto(valor: str, campo: str, vazio=False, max_len=255, dominio = None,
    caracteres_invalidos=None,):
    if dominio is None:
        dominio = []
    if caracteres_invalidos is None:
        caracteres_invalidos = {"|"}
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        if vazio: return ""
        raise ValueError(f" campo '{campo}' não pode ser vazio.")
    valor = str(valor).strip()
    if valor == "" or valor.lower() == "nan":
        if vazio: return ""
        raise ValueError(f" {campo} não pode estar vazio.")
    
    encontrados = [
                        caractere
                        for caractere in caracteres_invalidos
                        if caractere in valor
                    ]

    if encontrados:
        representacao = ", ".join(
                                    repr(caractere)
                                    for caractere in encontrados
                                )

        raise ValueError(
                            f"O campo '{campo}' contém caractere(s) inválido(s) "
                            f"para o formato do arquivo: {representacao}."
                        )
    caracteres_invalidos = []
    caracteres_permitidos = {
                                "\t",
                                "\r",
                                "\n", 
                            }

    for posicao, caractere in enumerate(valor):
        codigo = ord(caractere)
        categoria = unicodedata.category(caractere)

        if categoria == "Cc" and caractere not in caracteres_permitidos:
            caracteres_invalidos.append({
                                            "posicao": posicao,
                                            "codigo": f"U+{codigo:04X}",
                                            "nome": unicodedata.name(
                                                caractere,
                                                "CARACTERE DE CONTROLE",
                                            ),
                                        })

    if caracteres_invalidos:
        detalhes = ", ".join(
                                f"posição {item['posicao']}: "
                                f"{item['codigo']} ({item['nome']})"
                                for item in caracteres_invalidos
                            )

        raise ValueError(
                            f"O campo '{campo}' contém caractere(s) de controle "
                            f"inválido(s): {detalhes}."
                        )
    if max_len and len(valor) > max_len:
        raise ValueError(f" {campo} excede {max_len} caracteres.\n")
    if (dominio != []) and (valor not in dominio):
        raise ValueError(f' seguir o padrão fornecido no manual de dados {dominio}.\n')
    return valor

def validar_inteiro(valor: str, campo: str, min_val=None, max_val=None, vazio=False):
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        if vazio: return ""
        raise ValueError(f" campo '{campo}' não pode ser vazio.")

    v = str(valor).strip().lower()
    if v == "" or v == "nan":
        if vazio: return ""
        raise ValueError(f" {campo} não pode estar vazio.")

    if not v.isdigit():
        raise ValueError(f" {campo} deve ser um número inteiro positivo.")
    num = int(v)
    
    if min_val is not None and num < min_val:
        raise ValueError(f" {campo} deve ser >= {min_val}.")
    if max_val is not None and num > max_val:
        raise ValueError(f" {campo} deve ser <= {max_val}.")
    return v

def validar_projeto_pep(Cd_SubODI: Optional[str], FLG_PER: str, linha: str):
    if FLG_PER == "1":
        if not Cd_SubODI:
            raise ValueError(f" Cd_SubODI deve ser informada, linha {linha}, se for apropriação direta usar APR_DIR.\n")
        if len(Cd_SubODI) > 255:
            raise ValueError(f" Cd_SubODI, linha {linha}, maior do que o número de caracteres permitido.\n")

def validar_tuc_ti(Nr_TUC: str, Nr_TI: str, linha: str, Nr_A1: str):
    if Nr_TI in {"10","11","12","13","14","15","16","17","18","19"}:
        raise ValueError(f" TUC {Nr_TUC} na TI {Nr_TI}, que não é típica de distribuidora, linha {linha}.\n")
    if (Nr_TUC == "570") and (Nr_TI not in {"20","21","22","23","30","31","32","33","34","50","51","52","53","54"}):
        raise ValueError(f" TUC 570 (Transformador de força) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "190") and (Nr_A1 != '3') and (Nr_TI in {"20","21","22","23","30","31","32","33","34","50","51","52","53","54"}):
        raise ValueError(f" TUC 190 (condutor) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "295") and (Nr_TI not in {"93","96"}):
        raise ValueError(f" TUC 295 (Medidor) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "535") and (Nr_TI not in {"99"}):
        raise ValueError(f" TUC 535 (Software) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "615") and (Nr_TI in {"20","21","22","23","24","25","26","27","28","29",
                                    "30","31","32","33","34","35","36","37","38","39",
                                    "50","51","52","53","54","55","56","57","58","59",
                                    "60","61","62","63","64","65","66","67","68","69",
                                    "10","11","12","13","14","15","16","17","18","19",
                                    "40","41","42","43","44","70","72","80","82","90",
                                    "92","93","94","96","97","98","99"}):

        raise ValueError(f" TUC 615 (Veículos) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "205") and (Nr_TI in {"20","21","22","23","30","31","32","33","34","50","51",
                                     "52","53","54","10","11","12","13","14","15","16","17",
                                     "18","19","40","41","42","43","44","70","71","72","80",
                                     "81","82","90","91","92","93","94","96","97","98","99"}):
        raise ValueError(f" TUC 205 (Direito, Marca, Patente) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "255") and (Nr_A1 in {'1'}) and (Nr_TI in {"20","21","22","23","24","25","26","27","28","29",
                                                        "30","31","32","33","34","35","36","37","38","39",
                                                        "50","51","52","53","54","55","56","57","58","59",
                                                        "60","61","62","63","64","65","66","67","68","69",
                                                        "10","11","12","13","14","15","16","17","18","19"}):
        raise ValueError(f" TUC 255 (poste) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "255") and (Nr_A1 in {'2'}) and (Nr_TI in {"40","41","42","43","93","96","20","21","22","23","24",
                                                        "30","31","32","33","34","50","51","52","53","54",
                                                        "60","61","62","63","64","10","11","12","13","14",
                                                        "15","16","17","18","19"}):
        raise ValueError(f" TUC 255 (torre) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "565") and (Nr_TI not in {"40","41","42","43"}):
        raise ValueError(f"TUC 565 (transformador de distribuição) não pode estar na TI {Nr_TI}, linha {linha}.\n")

def validar_tucs_proibidos(Nr_TUC: str, linha: str):
    TUC_PROIBIDOS = {
                        "100","105","110","112","115","140","145","150","155","170","175","185","225","240",
                        "245","260","275","280","300","320","335","350","360","365","370","390","405","420",
                        "425","430","435","440","470","475","490","500","505","510","515","525","530","585",
                        "590","595","600"
                    }
    if Nr_TUC in TUC_PROIBIDOS:
        nome = ValoresTUC.descricao_por_codigo(int(Nr_TUC))
        raise ValueError(f"TUC {Nr_TUC} ({nome}) não deveria existir em distribuidora, linha {linha}.\n")

def validar_cabos(Nr_TUC: str, Nr_A1: str, Nr_A3: str, Nr_A4: str, Nr_A5: str, v_UND: str, linha: str):
    if (Nr_TUC != "190") and (Nr_A1 not in {"3","03"}):
        return
    
    Nr_A3 = str(Nr_A3).zfill(2)
    Nr_A4 = str(Nr_A4).zfill(2)
    Nr_A5 = str(Nr_A5).zfill(2)
    UNI = str(v_UND).upper()

    if (UNI in ['M','MT']) and (Nr_A3 == '01'):
        raise ValueError(f" cabo nu deve ser kg, linha {linha}.\n")
    
    if (UNI in ['KG']) and (Nr_A3 != '01'):
        raise ValueError(f" cabo nu deve ser m, linha {linha}.\n")

    if Nr_A3 in {"01"} and Nr_A5 != "01":
        raise ValueError(f" cabo nu deve ter A5=1, linha {linha}.\n")

    if Nr_A3 not in {"01"}:
        grupo_a5_1 = {"60","62","64","65","66"}
        grupo_a5_2 = {"61","63","67","68","69","70"}
        grupo_a5_3 = {
                        "71","72","73","74","75","76","77","78","79","57","80","81","82",
                        "58","83","84","85","59","19","86","87","88","89","90","91","92",
                        "93","94","95"
                     }

        if( Nr_A4 in grupo_a5_1) and (Nr_A5 != "01"):
            raise ValueError(f" cabo multi-condutor A4={Nr_A4} deveria ter A5=01, linha {linha}.\n")

        if (Nr_A4 in grupo_a5_2) and (Nr_A5 != "02"):
            raise ValueError(f" cabo multi-condutor A4={Nr_A4} deveria ter A5=02, linha {linha}.\n")

        if (Nr_A4 in grupo_a5_3) and (Nr_A5 != "03"):
            raise ValueError(f" cabo multi-condutor A4={Nr_A4} deveria ter A5=03, linha {linha}.\n")

        todos_multi = grupo_a5_2 | grupo_a5_3
        if Nr_A4 in todos_multi and Nr_A5 == "01" and Nr_A3 not in {"01"}:
            raise ValueError(f" cabo multi-condutor com A5=1 inválido, linha {linha}.\n")

    return

def validar_administracao(Nr_TI: str, Cd_CC: str, linha: str):
    TIs_admin = {"70","71","72","90","91","94","99"}
    contas_admin = {"123340101","123340103","123340199","123240101","123240103","123240104","123240105","123240106"}
    if Nr_TI in TIs_admin and Cd_CC not in contas_admin:
        raise ValueError(f" para TI {Nr_TI} a conta contábil deve ser de administração, linha {linha}.\n")

def validar_torre_poste(Nr_TI: str, Nr_TUC: str, Nr_A1: str, linha: str):
    TIs_LT_LD = {"24","25","26","27","28","29","35","36","37","38","39","55","56","57",
                 "58","59","60","61","62","63","64"}
    if Nr_TI not in TIs_LT_LD and Nr_TUC == "255" and Nr_A1 == "2":
        raise ValueError(f" torre em TI diferente de LT/LD, linha {linha}.\n")
    if Nr_TI in TIs_LT_LD and Nr_TUC == "255" and Nr_A1 == "1":
        raise ValueError(f" poste em TI de LT/LD, linha {linha}.\n")

def validar_FLG_PER(v_dt_IMB: str, v_PER: str, linha: str):
    Dt_REF = st.session_state.dt_ini
    Dt_IMB = datetime.strptime(v_dt_IMB, "%Y/%m/%d").date()
    if (Dt_IMB < Dt_REF) and (v_PER=="1"):
        raise ValueError(f" FLG_PER deveria ser '0', linha {linha}.\n")
    if (Dt_IMB >= Dt_REF) and (v_PER=="0"):
        raise ValueError(f" FLG_PER deveria ser '1', linha {linha}.\n")
    
def validar_cm(Nr_TI: str, Nr_CM: Optional[str], linha: str):
    TIs_SE = {"20","21","22","23","30","31","32","33","34","50","51","52","53","54"}
    Nr_CM = str(Nr_CM)
    if Nr_TI in TIs_SE:
        if not Nr_CM or len(Nr_CM) != 3:
            raise ValueError(f" Nr_CM, linha {linha}, deve ter 3 algarismos numéricos para SE.\n")
        if Nr_CM[0] not in {"0","1","2","3","4"}:
            raise ValueError(f" primeiro dígito de Nr_CM inválido ({Nr_CM[0]}), linha {linha}.\n")
        if Nr_CM[0] != "0":
            raise ValueError(f" primeiro dígito de Nr_CM não é de SE de distribuição, linha {linha}.\n")
        if Nr_CM[2] not in {"0","1","2","3","4","5"}:
            raise ValueError(f" terceiro dígito de Nr_CM inválido ({Nr_CM[2]}), linha {linha}.\n")
    else:
        if Nr_CM not in {None,"","999"}:
            raise ValueError(f" Nr_CM, linha {linha}, tem de ser vazio ou 999 quando não for SE.\n")

def validar_ti_distribuicao(Nr_TI: str, linha: str):
    if 9 < int(Nr_TI) < 20:
        raise ValueError(f" Nr_TI {Nr_TI}, linha {linha}, indica instalação de geração.\n")
    if 19 < int(Nr_TI) < 30:
        raise ValueError(f" Nr_TI {Nr_TI}, linha {linha}, indica instalação de transmissão ou DIT.\n")
    if 59 < int(Nr_TI) < 65:
        raise ValueError(f" Nr_TI {Nr_TI}, linha {linha}, indica instalação de linha de transmissão.\n")
    
def validar_bem_individual(Nr_TI: str, Nr_TUC: str, Nr_A1: str, Nr_A2: str, Nr_A3: str, Nr_A4: str, 
                            Nr_A5: str, Nr_A6: str, Qtd: str, linha: str, Cd_UAR: str):
    regras = [
                {'TI_DE': 10, 'TI_ATE': 19, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 100, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 105, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 110, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 112, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 115, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 120, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 125, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 130, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 135, 'A1_DE': 1,  'A1_ATE': 2, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 135, 'A1_DE': 3,  'A1_ATE': 3, 'A2_DE': 69,  'A2_ATE': 90,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 135, 'A1_DE': 3,  'A1_ATE': 3, 'A2_DE': 99,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 140, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 145, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 150, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 155, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 165, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 170, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 175, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 185, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 195, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 200, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 205, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 210, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 215, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 220, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 225, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 240, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 245, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 250, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 260, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 265, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 270, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 275, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 280, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 285, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 300, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 305, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 315, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 320, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 330, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 335, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 340, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 69,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 340, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 99,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 345, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 350, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 355, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 360, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 365, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 370, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 375, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 380, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 385, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 390, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 400, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 405, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 410, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 415, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 420, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 425, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 430, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 435, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 440, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 445, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 450, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 455, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 460, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 465, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 470, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 475, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 480, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 485, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 490, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 495, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 500, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 505, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 510, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 515, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 520, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 525, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 530, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 535, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 540, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 545, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 550, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 555, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 560, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 570, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 575, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 69,  'A2_ATE': 90,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 575, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 99,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 580, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 585, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 590, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 595, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 600, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 610, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 615, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 20, 'TI_ATE': 23, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 20, 'TI_ATE': 39, 'TUC': 160, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 34,  'A2_ATE': 90,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 20, 'TI_ATE': 39, 'TUC': 160, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 99,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 20, 'TI_ATE': 39, 'TUC': 310, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 34,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 20, 'TI_ATE': 39, 'TUC': 310, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 99,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 30, 'TI_ATE': 34, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 50, 'TI_ATE': 54, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 50, 'TI_ATE': 69, 'TUC': 160, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 34,  'A2_ATE': 90,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 50, 'TI_ATE': 69, 'TUC': 160, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 99,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 50, 'TI_ATE': 69, 'TUC': 310, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 34,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 50, 'TI_ATE': 69, 'TUC': 310, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 99,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 72, 'TI_ATE': 72, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 82, 'TI_ATE': 82, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 92, 'TI_ATE': 92, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
             ]

    Nr_TUC = int(Nr_TUC)
    Nr_TI = int(Nr_TI)
    Nr_A1 = int(Nr_A1)
    Nr_A2 = int(Nr_A2)
    Nr_A3 = int(Nr_A3) 
    Nr_A4 = int(Nr_A4) 
    Nr_A5 = int(Nr_A5) 
    Nr_A6 = int(Nr_A6) 
    Qtd = float(Qtd.replace(".", "").replace(",", "."))

    candidatos = [
                    r for r in regras
                    if (
                        r["TI_DE"] <= Nr_TI <= r["TI_ATE"]
                        and r["TUC"] == Nr_TUC
                        and all(
                            r[f"A{i}_DE"] <= valor <= r[f"A{i}_ATE"]
                            for i, valor in enumerate(
                                [Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5, Nr_A6],
                                start=1,
                            )
                        )
                    )
                ]
    
    if candidatos and Qtd != 1.0 and Cd_UAR != "UAR":
        raise ValueError(
                            f"Bem de controle individual: TUC {Nr_TUC}, "
                            f"quantidade informada {Qtd}, deveria ser 1. "
                            f"ID: {linha}, Cd_UAR = {Cd_UAR}."
                        )

def localizar_arquivo(base_path: str, prefixo: str) -> str | None:
    arquivos = glob.glob(os.path.join(base_path, f"{prefixo}*.csv"))
    if arquivos:
        return arquivos[0]
    return None

class AIS(BaseModel):
    model_config = ConfigDict(extra="forbid")

    Ide_AIS: str
    Cd_CC: str
    Cd_ODI: str
    Cd_SubODI: str
    Nr_TI: str
    Nr_CM: str
    Nr_TUC: str
    Nr_A1: str
    Nr_A2: str
    Nr_A3: str
    Nr_A4: str
    Nr_A5: str
    Nr_A6: str
    txt_Desc_Bem: str
    Qtd_AIS: str
    Cd_UND_AIS: str
    Cd_UAR: str
    Cd_UC: str
    Cd_Patrim: str
    Cd_DIG_INC: str
    Dt_Imob: str
    VL_VOC: str
    VL_DEP_ACUM: str
    txt_OBS: Optional[str] = None
    Dt_CONT_INC_REDE: Optional[str] = None
    Cd_ODI_Ori: Optional[str] = None
    Nr_TI_Ori: Optional[str] = None
    VL_PROJ_ORI: Optional[str] = None
    Pct_PROJ_ORI: Optional[str] = None
    Dt_Ref_AIS: str
    FLG_PER: str
    Cd_NT: Optional[str] = None
    VL_VOC_MV: str
    VL_DEP_ACUM_MV: str
    Cd_ANEEL: str
    Cd_Cna_Ccd: str
    Cd_Tipo_OE: str
    Pct_OE: str
    Cd_ID_BDGD: Optional[str] = None
    COD_ITEM: Optional[str] = None
    Cd_Q5: Optional[str] = None
    Cd_Q7: Optional[str] = None
    Cd_MUN: Optional[str] = None

    _erros_registro: list[dict] = PrivateAttr(default_factory=list)

    @field_validator("Dt_Imob", "Dt_Ref_AIS", mode="before")
    @classmethod
    def validar_datas(cls, valor):
        return validar_data(valor)

    @field_validator("Dt_CONT_INC_REDE", mode="before")
    @classmethod
    def validar_data_opcional(cls, valor):
        return validar_data(valor, vazio=True)

    @field_validator("VL_VOC", "Qtd_AIS", mode="before")
    @classmethod
    def validar_decimais_positivos(cls, valor):
        return validar_decimal(valor, min_val=0)

    @field_validator(
        "VL_DEP_ACUM",
        "VL_VOC_MV",
        "VL_DEP_ACUM_MV",
        mode="before",
    )
    @classmethod
    def validar_decimais(cls, valor):
        return validar_decimal(valor)

    @field_validator("VL_PROJ_ORI", mode="before")
    @classmethod
    def validar_projeto_origem(cls, valor):
        return validar_decimal(valor, vazio=True, min_val=0)

    @field_validator("Pct_PROJ_ORI", "Pct_OE", mode="before")
    @classmethod
    def validar_percentuais(cls, valor):
        return validar_decimal(
            valor, vazio=True, min_val=0, max_val=1
        )

    @field_validator(
                        "Nr_A1", "Nr_A2", "Nr_A3",
                        "Nr_A4", "Nr_A5", "Nr_A6",
                        mode="before",
                    )
    @classmethod
    def validar_atributos(cls, valor, info):
        return validar_inteiro(
            valor, info.field_name, min_val=0, max_val=99
        )

    @field_validator("FLG_PER", mode="before")
    @classmethod
    def validar_flag(cls, valor, info):
        return validar_inteiro(
            valor, info.field_name, min_val=0, max_val=1
        )

    @field_validator("Cd_Tipo_OE", mode="before")
    @classmethod
    def validar_tipo_oe(cls, valor, info):
        return validar_inteiro(
            valor, info.field_name, min_val=0, max_val=8
        )

    @field_validator("Cd_DIG_INC", "Ide_AIS", mode="before")
    @classmethod
    def validar_inteiros_positivos(cls, valor, info):
        return validar_inteiro(
            valor, info.field_name, min_val=0
        )

    @field_validator("Cd_ANEEL", mode="before")
    @classmethod
    def validar_aneel(cls, valor, info):
        return validar_inteiro(
            valor, info.field_name,
            min_val=0, max_val=200000,
        )

    @field_validator(
                        "txt_Desc_Bem", "txt_OBS", "Cd_ID_BDGD",
                        "COD_ITEM", "Cd_Q5", "Cd_Q7", "Cd_MUN",
                        mode="before",
                    )
    @classmethod
    def validar_textos(cls, valor, info):
        return validar_texto(
            valor, info.field_name,
            vazio=True, max_len=1000,
        )

    @field_validator("Cd_UND_AIS", mode="before")
    @classmethod
    def validar_unidade(cls, valor, info):
        return validar_texto(
            valor, info.field_name, max_len=10
        )

    @field_validator("Cd_UAR", mode="before")
    @classmethod
    def validar_uar(cls, valor, info):
        return validar_texto(
            valor, info.field_name,
            max_len=3,
            dominio=["UAR", "TUC", "UC"],
        )

    @field_validator(
                        "Cd_UC", "Cd_Patrim", "Cd_ODI",
                        "Cd_NT", "Cd_Cna_Ccd",
                        mode="before",
                    )
    @classmethod
    def validar_codigos(cls, valor, info):
        return validar_texto(
                                valor,
                                info.field_name,
                                vazio=info.field_name == "Cd_NT",
                                max_len=25,
                            )

    @field_validator("Cd_CC")
    @classmethod
    def validar_cc(cls, valor, info):
        num = validar_inteiro(valor, info.field_name)

        if not ValoresCC.teste(valor):
            raise ValueError(
                f"{valor} não faz parte do domínio de CC."
            )

        return valor

    @field_validator("Nr_TUC")
    @classmethod
    def validar_tuc(cls, valor, info):
        num = validar_inteiro(
            valor, info.field_name,
            min_val=99, max_val=999,
        )

        if num not in (None, ""):
            if not ValoresTUC.teste(int(num)):
                raise ValueError(
                    "O dado não é válido como código de UC."
                )

        return valor

    @field_validator("Nr_TI")
    @classmethod
    def validar_ti(cls, valor, info):
        num = validar_inteiro(
            valor, info.field_name,
            min_val=1, max_val=100,
        )

        if num not in (None, ""):
            if not ValoresTI.teste(int(num)):
                raise ValueError(
                    "O dado não é válido como TI."
                )

        return valor

    @field_validator("Nr_TI_Ori")
    @classmethod
    def validar_ti_origem(cls, valor, info):
        num = validar_inteiro(
            valor, info.field_name,
            min_val=1, max_val=100,
            vazio=True,
        )

        if num in (None, "", " "):
            return valor

        if not ValoresTI.teste(int(num)):
            raise ValueError(
                f"O dado '{num}' não é válido como TI de origem."
            )

        return valor

    @model_validator(mode="wrap")
    @classmethod
    def capturar_erros_estrutura(cls, valores: Any, handler):
        try:
            return handler(valores)

        except ValidationError as exc:
            dados = (
                valores
                if isinstance(valores, dict)
                else valores.__dict__
            )

            obj = cls.model_construct(**dados)
            obj._erros_registro = exc.errors(
                include_url=False
            )

            return obj

class TabelaAIS(BaseModel):
    tabela: list[AIS]

    @model_validator(mode="after")
    def pipeline_validacao_completa(self):
        erros = []

        for indice, obj in enumerate(self.tabela):
            linha_id = getattr(
                obj, "Ide_AIS", None
            ) or f"Linha_{indice + 1}"

            campos_invalidos = self._coletar_erros_estrutura(
                obj=obj,
                indice=indice,
                erros=erros,
            )

            self._executar_regras_negocio(
                obj=obj,
                indice=indice,
                linha_id=linha_id,
                campos_invalidos=campos_invalidos,
                erros=erros,
            )

        if erros:
            raise ValidationError.from_exception_data(
                self.__class__.__name__,
                erros,
            )

        return self

    @staticmethod
    def _coletar_erros_estrutura(
                                        *,
                                        obj: AIS,
                                        indice: int,
                                        erros: list,
                                    ) -> set[str]:

        campos_invalidos = set()

        for erro in obj._erros_registro:
            loc = erro.get("loc", ())
            loc = (loc,) if isinstance(loc, str) else tuple(loc)

            if loc and isinstance(loc[0], str):
                campos_invalidos.add(loc[0])

            mensagem = f"[Estrutura] {erro.get('msg', '')}"

            erros.append({
                "type": "value_error",
                "loc": ("tabela", indice) + loc,
                "input": erro.get("input"),
                "ctx": {
                    "error": ValueError(mensagem),
                },
            })

        return campos_invalidos

    def _executar_regras_negocio(
                                    self, 
                                    *,
                                    obj: AIS,
                                    indice: int,
                                    linha_id,
                                    campos_invalidos: set[str],
                                    erros: list,
                                ) -> None:

        regras = [
            (
                validar_tuc_ti,
                "Nr_TUC",
                ("Nr_TUC", "Nr_TI", "Nr_A1"),
                (obj.Nr_TUC, obj.Nr_TI, linha_id, obj.Nr_A1),
            ),
            (
                validar_tucs_proibidos,
                "Nr_TUC",
                ("Nr_TUC",),
                (obj.Nr_TUC, linha_id),
            ),
            (
                validar_administracao,
                "Cd_CC",
                ("Nr_TI", "Cd_CC"),
                (obj.Nr_TI, obj.Cd_CC, linha_id),
            ),
            (
                validar_cm,
                "Nr_CM",
                ("Nr_TI", "Nr_CM"),
                (obj.Nr_TI, obj.Nr_CM, linha_id),
            ),
            (
                validar_ti_distribuicao,
                "Nr_TI",
                ("Nr_TI",),
                (obj.Nr_TI, linha_id),
            ),
            (
                validar_cabos,
                "Nr_TUC",
                (
                    "Nr_TUC", "Nr_A1", "Nr_A3",
                    "Nr_A4", "Nr_A5", "Cd_UND_AIS",
                ),
                (
                    obj.Nr_TUC, obj.Nr_A1, obj.Nr_A3,
                    obj.Nr_A4, obj.Nr_A5,
                    obj.Cd_UND_AIS, linha_id,
                ),
            ),
            (
                validar_torre_poste,
                "Nr_TI",
                ("Nr_TI", "Nr_TUC", "Nr_A1"),
                (obj.Nr_TI, obj.Nr_TUC, obj.Nr_A1, linha_id),
            ),
            (
                validar_FLG_PER,
                "FLG_PER",
                ("Dt_Imob", "FLG_PER"),
                (obj.Dt_Imob, obj.FLG_PER, linha_id),
            ),
            (
                validar_bem_individual,
                "Nr_TUC",
                (
                    "Nr_TI", "Nr_TUC",
                    "Nr_A1", "Nr_A2", "Nr_A3",
                    "Nr_A4", "Nr_A5", "Nr_A6",
                    "Qtd_AIS", "Cd_UAR",
                ),
                (
                    obj.Nr_TI, obj.Nr_TUC,
                    obj.Nr_A1, obj.Nr_A2, obj.Nr_A3,
                    obj.Nr_A4, obj.Nr_A5, obj.Nr_A6,
                    obj.Qtd_AIS, linha_id, obj.Cd_UAR,
                ),
            ),
        ]

        for func, campo, dependencias, args in regras:
            if campos_invalidos.intersection(dependencias):
                continue

            self._executar_regra(
                                    func=func,
                                    campo=campo,
                                    args=args,
                                    obj=obj,
                                    indice=indice,
                                    linha_id=linha_id,
                                    erros=erros,
                                )

    @staticmethod
    def _executar_regra(
                            *,
                            func: Callable,
                            campo: str,
                            args: tuple,
                            obj: AIS,
                            indice: int,
                            linha_id,
                            erros: list,
                        ) -> None:

        try:
            func(*args)

        except ValueError as exc:
            mensagem = (
                            f"[Regra Negocio] "
                            f"[ID: {linha_id}] {exc}"
                        )

            erros.append({
                            "type": "value_error",
                            "loc": ("tabela", indice, campo),
                            "input": getattr(obj, campo, None),
                            "ctx": {
                                "error": ValueError(mensagem),
                            },
                        })

class ROSV(BaseModel):
    Nr_TI: str
    Cd_SubODI: str
    VL_UC_ROA: str
    VL_COM_ROA: str
    VL_MOP_ROA: str
    VL_ST_ROA: str
    VL_JOA_ROA: str
    VL_OUT_ROA: str
    VL_TOT_ROA: str
    VL_UAR_FISC: str
    VL_COM_FISC: str
    VL_MOP_FISC: str
    VL_ST_FISC: str
    VL_JOA_FISC: str
    VL_OUT_FISC: str
    VL_TOT_FISC: str

    class Config:
        extra = 'forbid'
    
    TOLERANCIA: ClassVar[Decimal] = Decimal('0.01')
    COMPONENTES_ROA: ClassVar[tuple[str, ...]] = ('VL_UC_ROA', 'VL_COM_ROA', 'VL_MOP_ROA',
                       'VL_ST_ROA', 'VL_JOA_ROA', 'VL_OUT_ROA')
    COMPONENTES_FISC: ClassVar[tuple[str, ...]] = ('VL_UAR_FISC', 'VL_COM_FISC', 'VL_MOP_FISC',
                        'VL_ST_FISC', 'VL_JOA_FISC', 'VL_OUT_FISC')
    
    @field_validator('Nr_TI')
    @classmethod
    def validar_TI(cls, value, info):
        num = validar_inteiro(value, info.field_name, min_val=1, max_val=100, vazio=True)
        if not ValoresTI.teste(int(num)):
            raise ValueError(f'O valor {value!r} não é válido como TI.\n')
        return value

    @field_validator('Cd_SubODI', mode="before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=255)
            
    @field_validator('VL_UC_ROA','VL_COM_ROA','VL_MOP_ROA','VL_ST_ROA','VL_JOA_ROA','VL_OUT_ROA',
                     'VL_TOT_ROA','VL_UAR_FISC','VL_COM_FISC','VL_MOP_FISC','VL_ST_FISC',
                     'VL_JOA_FISC','VL_OUT_FISC','VL_TOT_FISC', mode='before')
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)

    @staticmethod
    def _decimal_br(value):
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        texto = str(value).strip()
        if ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        return Decimal(texto)

    @model_validator(mode='after')
    def validar_consistencia_valores(self):
        valores = {}
        for campo in (*self.COMPONENTES_ROA, 'VL_TOT_ROA',
                      *self.COMPONENTES_FISC, 'VL_TOT_FISC'):
            try:
                valores[campo] = self._decimal_br(getattr(self, campo))
            except (InvalidOperation, TypeError, ValueError):
                return self

        erros = []

        def adicionar(campo, mensagem):
            erros.append({
                            'type': 'value_error',
                            'loc': (campo,),
                            'input': getattr(self, campo),
                            'ctx': {'error': ValueError(mensagem)},
                        })

        for componentes, total, rotulo in (
                                                (self.COMPONENTES_ROA, 'VL_TOT_ROA', 'ROA'),
                                                (self.COMPONENTES_FISC, 'VL_TOT_FISC', 'FISC'),
                                            ):
            soma = sum((valores[c] for c in componentes), Decimal('0'))
            if abs(valores[total] - soma) > self.TOLERANCIA:
                adicionar(
                            total,
                            f'{total} ({valores[total]:.2f}) difere da soma dos '
                            f'componentes {rotulo} ({soma:.2f}).'
                        )
        pares = zip(
                        (*self.COMPONENTES_FISC, 'VL_TOT_FISC'),
                        (*self.COMPONENTES_ROA, 'VL_TOT_ROA'),
                    )
        for campo_fisc, campo_roa in pares:
            if valores[campo_fisc] > valores[campo_roa] + self.TOLERANCIA:
                adicionar(
                            campo_fisc,
                            f'{campo_fisc} ({valores[campo_fisc]:.2f}) não pode ser '
                            f'maior que {campo_roa} ({valores[campo_roa]:.2f}).'
                        )

        if erros:
            raise ValidationError.from_exception_data('ROSV', erros)
        return self

class TabelaROSV(BaseModel):
    tabela: list[ROSV]

class ROServ(BaseModel):
    Ide_RO_Sintetico: str
    Cd_ODS: str
    Cd_SubODS: str
    Txt_Desc_PRJ: str
    Cd_Tipo_Obra: str
    Dt_Inic_Proj: str
    Dt_Energ: str
    Dt_Uniti: str
    Pct_OE: str
    Nr_Fases: str
    VL_TEN: str
    Cd_ODD: str
    VL_CA_ST_ODD: str
    VL_CA_MOP_ODD: str
    Txt_JUST_ODD: str
    Cd_Tipo_OE: str

    class Config:
        extra = 'forbid'
    
    @field_validator('Ide_RO_Sintetico', mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name)
    
    @field_validator('Cd_Tipo_OE', mode="before")
    @classmethod
    def validar_ide1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=8, vazio=True)
    
    @field_validator('Cd_ODS')
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=25)
    
    @field_validator('Cd_SubODS', mode="before")
    @classmethod
    def validar_cda(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=255)
        
    @field_validator('Cd_ODD')
    @classmethod
    def validar_cdd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=255)
    
    @field_validator('Txt_Desc_PRJ', 'Txt_JUST_ODD', mode="before")
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
           
    @field_validator('Dt_Inic_Proj','Dt_Uniti', 'Dt_Energ', mode="before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value, vazio=True)
   
    @field_validator('VL_CA_ST_ODD', 'VL_CA_MOP_ODD', 'VL_TEN', mode="before")
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value, min_val=0, vazio=True)
               
    @field_validator('Pct_OE', mode="before")
    @classmethod
    def validar_vl_pct(cls, value):
        return validar_decimal(value, vazio=True, min_val=0)
    
    @field_validator('Cd_Tipo_Obra', mode="before")
    @classmethod
    def validar_tipo_obra(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=12, vazio=True)
        
    @field_validator('Nr_Fases', mode="before")
    @classmethod
    def validar_nr_fas(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3, vazio=True)
                   
class TabelaROServ(BaseModel):
    tabela: List[ROServ]
    
class ROS(BaseModel):
    Ide_RO_Sintetico: str
    Cd_ODI: str
    Cd_SubODI: str
    Txt_Desc_PRJ: str
    Cd_Tipo_Obra: str
    Dt_Inic_Proj: str
    Dt_Energ: str
    Dt_Uniti: str
    Pct_OE: str
    Nr_Fases: str
    VL_TEN: str
    Cd_ODD: str
    VL_CA_ST_ODD: str
    VL_CA_MOP_ODD: str
    Txt_JUST_ODD: str
    Cd_Tipo_OE: str

    class Config:
        extra = 'forbid'
    
    @field_validator('Ide_RO_Sintetico', mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name)
    
    @field_validator('Cd_Tipo_OE', mode="before")
    @classmethod
    def validar_ide1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=8)
    
    @field_validator('Cd_ODI')
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=25)
    
    @field_validator('Cd_SubODI', mode="before")
    @classmethod
    def validar_cda(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=255)
        
    @field_validator('Cd_ODD')
    @classmethod
    def validar_cdd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=255)
    
    @field_validator('Txt_Desc_PRJ', 'Txt_JUST_ODD', mode="before")
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
           
    @field_validator('Dt_Inic_Proj','Dt_Uniti', 'Dt_Energ', mode="before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value, vazio=True)
   
    @field_validator('VL_CA_ST_ODD', 'VL_CA_MOP_ODD', 'VL_TEN', mode="before")
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value, min_val=0, vazio=True)
               
    @field_validator('Pct_OE', mode="before")
    @classmethod
    def validar_vl_pct(cls, value):
        return validar_decimal(value, vazio=True, min_val=0)
    
    @field_validator('Cd_Tipo_Obra', mode="before")
    @classmethod
    def validar_tipo_obra(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=12)
        
    @field_validator('Nr_Fases', mode="before")
    @classmethod
    def validar_nr_fas(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3, vazio=True)
       
    @model_validator(mode="wrap")
    def verifica_dados(cls, values, handler):
        validation_error = None
        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        def to_date(v):
            if not v or str(v).strip() == "":
                return date(1920, 1, 1)
            try:
                return datetime.strptime(str(v).strip(), "%Y/%m/%d").date()
            except Exception:
                return date(1920, 1, 1)

        D1 = to_date(result.Dt_Inic_Proj)
        D2 = to_date(result.Dt_Energ)
        D3 = to_date(result.Dt_Uniti)

        linha = getattr(result, "Ide_RO_Sintetico", "")

        if D1 > D2:
            raise ValueError(f"Dt_Ini_Proj (linha {linha}) é mais recente que Dt_Energ.\n")
        if D1 > D3:
            raise ValueError(f"Dt_Ini_Proj (linha {linha}) é mais recente que Dt_Uniti.\n")
        if D2 > D3:
            raise ValueError(f"Dt_Energ (linha {linha}) é mais recente que Dt_Uniti.\n")

        if validation_error is not None:
            raise validation_error
        
        return result
            
class TabelaROS(BaseModel):
    tabela: List[ROS]
        
class CDSUBODIAIS(BaseModel):
    Cd_SubODI_AIS: str
    Cd_SubODI_ROS: str
    
    class Config:
        extra = 'forbid'
    
    @field_validator('Cd_SubODI_AIS','Cd_SubODI_ROS', mode="before")
    @classmethod
    def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=255)
               
class TabelaCDSUBODIAIS(BaseModel):
    tabela: List[CDSUBODIAIS]
        
class ROA(BaseModel):
    Ide_RO_Analitico: str
    Cd_ODI: str
    Cd_SubODI: str
    Cd_Cls_Custo: str
    COD_ITEM: str
    Cd_NG: str
    Cd_CA: str
    FLG_PLPT: str
    Qtd: str
    Unidade: str
    VL_tot: str
    Dt_Lcmto: str
    Cd_Pedido: str
    Txt_Doc: str
    Nr_TI: str
    Nr_TUC: str
    Nr_A1: str
    Nr_A2: str
    Nr_A3: str
    Nr_A4: str
    Nr_A5: str
    Nr_A6: str 
    Txt_Nom_Forn: str
    Nr_NF: str
    Nr_ItemNF: str
    Nr_SerieNF: str
    CNPJ_Forn: str
    FLG_DOA_OE: str
    FLG_INCOR_OE: str
    FLG_OAT: str
    Cd_ATIP: str
    Cd_AJST: str
    Cd_SubODI_MUT: str
    FLG_DIR: str | None = None

    class Config:
        extra = 'forbid'

    @field_validator('FLG_DIR', mode='before')
    @classmethod
    def validar_flg_dir(cls, value, info):
        if value is None or str(value).strip() == "":
            return None
        return validar_inteiro(
                                    value,
                                    info.field_name,
                                    min_val=0,
                                    max_val=1
                                )
    
    @field_validator('Cd_ATIP', mode="before")
    @classmethod
    def validar_vl_cda(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=10, vazio=True)
    
    @field_validator('CNPJ_Forn', mode="before")
    @classmethod
    def validar_cnpj(cls, value):
        return validar_CNPJ(value)
    
    @field_validator('Cd_NG', mode="before")
    @classmethod
    def validar_vl_cdng(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=7)
    
    @field_validator('Cd_CA', mode="before")
    @classmethod
    def validar_vl_cdca(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=6)
    
    @field_validator('VL_tot', 'Qtd', mode="before")
    @classmethod
    def validar_vl_voc(cls, value):
        return validar_decimal(value)
    
    @field_validator('Nr_TUC', mode="before")
    @classmethod
    def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=1000)
        if (nm != None) and (nm != '') and (not ValoresTUC.teste(int(value))):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm
        
    @field_validator('Nr_TI', mode="before")
    @classmethod
    def validar_TI(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=1, max_val=100)
        if not ValoresTI.teste(int(value)):
            raise ValueError(f'O dado não é válido como TI.\n')
        return nm
    
    @field_validator('Dt_Lcmto', mode="before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
    
    @field_validator('Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6', mode="before")
    @classmethod
    def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=0, max_val=99)
    
    @field_validator('Ide_RO_Analitico', mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name)
    
    @field_validator('Nr_NF', mode="before")
    @classmethod
    def validar_Txt_N(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=50)
        
    @field_validator('Unidade', 'Nr_ItemNF', 'Nr_SerieNF', mode="before")
    @classmethod
    def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=10)
        
    @field_validator('FLG_PLPT','FLG_DOA_OE','FLG_DOA_OE','FLG_INCOR_OE','FLG_OAT', mode="before")
    @classmethod
    def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
    
    @field_validator('Cd_AJST', mode="before")
    @classmethod
    def validar_FLGa(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=3)
   
    @field_validator('COD_ITEM','Cd_Cls_Custo','Cd_Pedido', mode="before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=25)
    
    @field_validator('Cd_ODI', mode="before")
    @classmethod
    def validar_cd1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
    
    @field_validator('Cd_SubODI', mode="before")
    @classmethod
    def validar_cd2(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)
    
    @field_validator('Cd_SubODI_MUT', mode="before")
    @classmethod
    def validar_cd21(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=255)
   
    @field_validator('Txt_Doc','Txt_Nom_Forn')
    @classmethod
    def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)  
    
    @model_validator(mode="wrap")
    @classmethod
    def verifica_dados(cls, values, handler):
        erros = []
        try:
            result = handler(values)
        except ValidationError as exc:
            erros.extend(
                            {
                                "type": erro["type"],
                                "loc": tuple(erro["loc"]),
                                "input": erro.get("input"),
                                **(
                                    {"ctx": erro["ctx"]}
                                    if "ctx" in erro
                                    else {}
                                )
                            }
                            for erro in exc.errors()
                        )


            result = cls.model_construct(**values)

        def obter(campo, padrao=None):
            return getattr(result, campo, padrao)

        def esta_vazio(valor):
            return (
                        valor is None
                        or (
                            isinstance(valor, str)
                            and valor.strip() == ""
                        )
                    )

        def adicionar_erro(campo, mensagem, valor=None):
            erros.append({
                            "type": "value_error",
                            "loc": (campo,),
                            "input": valor,
                            "ctx": {
                                "error": ValueError(mensagem)
                            }
                        })

        def converter_decimal(valor, campo):
            if esta_vazio(valor):
                return 0.0

            try:
                return float(
                                str(valor).strip().replace(",", ".")
                            )

            except (TypeError, ValueError):
                adicionar_erro(
                                    campo,
                                    f"Valor decimal inválido: {valor!r}",
                                    valor
                                )
                return None

        nr_ti = obter("Nr_TI")
        nr_tuc = obter("Nr_TUC")
        nr_a1 = obter("Nr_A1")
        nr_a3 = obter("Nr_A3")

        nr_atributos = [
                            obter(f"Nr_A{i}")
                            for i in range(1, 7)
                        ]

        cd_ca = obter("Cd_CA")
        cd_ng = obter("Cd_NG")
        flg_oat = obter("FLG_OAT")
        cd_atip = obter("Cd_ATIP")
        cod_item = obter("COD_ITEM")

        unidade = str(
                        obter("Unidade", "") or ""
                    ).strip().lower()

        qtd = converter_decimal(
                                    obter("Qtd"),
                                    "Qtd"
                                )

        vl_tot = converter_decimal(
                                        obter("VL_tot"),
                                        "VL_tot"
                                    )


        try:
            validar_ti_distribuicao(
                                        nr_ti,
                                        obter("Ide_RO_Analitico", "")
                                    )

        except ValueError as exc:
            adicionar_erro(
                                "Nr_TI",
                                str(exc),
                                nr_ti
                            )

        if qtd is not None and vl_tot is not None:
            if qtd * vl_tot < 0:
                adicionar_erro(
                                    "VL_tot",
                                    (
                                        "Sinal divergente entre "
                                        f"quantidade ({qtd}) "
                                        f"e valor ({vl_tot})."
                                    ),
                                    obter("VL_tot")
                                )

        if (
                str(nr_tuc) == "190"
                and str(nr_a1) in {"1", "2"}
            ):
            unidades_esperadas = (
                                    {"kg"}
                                    if str(nr_a3) == "1"
                                    else {"m", "mt"}
                                )

            if unidade not in unidades_esperadas:
                adicionar_erro(
                                    "Unidade",
                                    (
                                        "Unidade incompatível com "
                                        "a classificação TUC. "
                                        f"Esperado: {', '.join(sorted(unidades_esperadas))}."
                                    ),
                                    obter("Unidade")
                                )

        if (
                str(cd_ng) in {"3", "4"}
                and esta_vazio(cd_ca)
            ):
            adicionar_erro(
                            "Cd_CA",
                            (
                                "Cd_CA deve ser preenchido "
                                f"quando Cd_NG é {cd_ng}."
                            ),
                            cd_ca
                        )

        if (
                str(cd_ng) in {"1", "2", "4"}
                and esta_vazio(cod_item)
            ):
            adicionar_erro(
                                "COD_ITEM",
                                (
                                    "COD_ITEM deve ser preenchido "
                                    f"quando Cd_NG é {cd_ng}."
                                ),
                                cod_item
                            )

        if str(flg_oat) == "0":

            if str(cd_atip or "0").strip() != "0":
                adicionar_erro(
                                    "Cd_ATIP",
                                    (
                                        "Cd_ATIP deve ser zero "
                                        "quando FLG_OAT é 0."
                                    ),
                                    cd_atip
                                )

        elif str(flg_oat) == "1":

            try:
                cd_atip_int = int(
                                        str(cd_atip).strip()
                                    )
            except (TypeError, ValueError):
                cd_atip_int = None

            if cd_atip_int not in range(1, 11):
                adicionar_erro(
                                    "Cd_ATIP",
                                    (
                                        "Cd_ATIP deve estar entre "
                                        "1 e 10 quando FLG_OAT é 1."
                                    ),
                                    cd_atip
                                )

        tucagem_incompleta = (
                                esta_vazio(nr_tuc)
                                or any(
                                    esta_vazio(atributo)
                                    for atributo in nr_atributos
                                )
                            )

        if (
                str(cd_ng) == "1"
                and tucagem_incompleta
            ):
            campos_tucagem = [
                                "Nr_TUC",
                                "Nr_A1",
                                "Nr_A2",
                                "Nr_A3",
                                "Nr_A4",
                                "Nr_A5",
                                "Nr_A6"
                            ]

            for campo in campos_tucagem:
                valor = obter(campo)

                if esta_vazio(valor):
                    adicionar_erro(
                                        campo,
                                        (
                                            "Tucagem obrigatória "
                                            "quando Cd_NG é 1."
                                        ),
                                        valor
                                    )

        if erros:
            raise ValidationError.from_exception_data(
                                                        cls.__name__,
                                                        erros
                                                    )

        return result   
         
class TabelaROA(BaseModel):
    tabela: List[ROA]

class RAs(BaseModel):
    Ide_RO_Analitico: str
    Cd_ODS: str
    Cd_SubODS: str
    Cd_Cls_Custo: str
    COD_ITEM: str
    Cd_NG: str
    Cd_CA: str
    FLG_PLPT: str
    Qtd: str
    Unidade: str
    VL_tot: str
    Dt_Lcmto: str
    Cd_Pedido: str
    Txt_Doc: str
    Nr_TI: str
    Nr_TUC: str
    Nr_A1: str
    Nr_A2: str
    Nr_A3: str
    Nr_A4: str
    Nr_A5: str
    Nr_A6: str 
    Txt_Nom_Forn: str
    Nr_NF: str
    Nr_ItemNF: str
    Nr_SerieNF: str
    CNPJ_Forn: str
    FLG_DOA_OE: str
    FLG_INCOR_OE: str
    FLG_OAT: str
    Cd_ATIP: str
    Cd_AJST: str
    Cd_SubODI_MUT: str

    class Config:
        extra = 'forbid'
    
    @field_validator('Cd_ATIP', mode="before")
    @classmethod
    def validar_vl_cda(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=10, vazio=True)
    
    @field_validator('CNPJ_Forn', mode="before")
    @classmethod
    def validar_cnpj(cls, value):
        return validar_CNPJ(value)
    
    @field_validator('Cd_NG', mode="before")
    @classmethod
    def validar_vl_cdng(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=7)
    
    @field_validator('Cd_CA', mode="before")
    @classmethod
    def validar_vl_cdca(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=6)
    
    @field_validator('VL_tot', 'Qtd', mode="before")
    @classmethod
    def validar_vl_voc(cls, value):
        return validar_decimal(value)
    
    @field_validator('Nr_TUC', mode="before")
    @classmethod
    def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=1000)
        if (nm != None) and (nm != '') and (not ValoresTUC.teste(int(value))):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm
        
    @field_validator('Nr_TI', mode="before")
    @classmethod
    def validar_TI(cls, value, info):
        nm = validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=100)
        if not ValoresTI.teste(int(value)):
            raise ValueError(f'O dado não é válido como TI.\n')
        return nm
    
    @field_validator('Dt_Lcmto', mode="before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
    
    @field_validator('Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6', mode="before")
    @classmethod
    def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=0, max_val=99)
    
    @field_validator('Ide_RO_Analitico', mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name)
    
    @field_validator('Nr_NF', mode="before")
    @classmethod
    def validar_Txt_N(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=50)
        
    @field_validator('Unidade', 'Nr_ItemNF', 'Nr_SerieNF', mode="before")
    @classmethod
    def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=10)
        
    @field_validator('FLG_PLPT','FLG_DOA_OE','FLG_DOA_OE','FLG_INCOR_OE','FLG_OAT', mode="before")
    @classmethod
    def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
    
    @field_validator('Cd_AJST', mode="before")
    @classmethod
    def validar_FLGa(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=3)
   
    @field_validator('COD_ITEM','Cd_Cls_Custo','Cd_Pedido', mode="before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=25)
    
    @field_validator('Cd_ODS', mode="before")
    @classmethod
    def validar_cd1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
    
    @field_validator('Cd_SubODS', mode="before")
    @classmethod
    def validar_cd2(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)
    
    @field_validator('Cd_SubODI_MUT', mode="before")
    @classmethod
    def validar_cd21(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=255)
   
    @field_validator('Txt_Doc','Txt_Nom_Forn')
    @classmethod
    def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)  
    
class TabelaRAs(BaseModel):
    tabela: List[RAs]

class ROD(BaseModel):
    Ide_RO_Analitico: str
    Cd_ODI: str
    Cd_ODD: str
    Cd_Cls_Custo: str
    COD_ITEM: str
    Cd_NG: str
    Cd_CA: str
    FLG_PLPT: str
    Qtd: str
    Unidade: str
    VL_tot: str
    Dt_Lcmto: str
    Nr_TI: str
    Nr_TUC: str
    Nr_A1: str
    Nr_A2: str
    Nr_A3: str
    Nr_A4: str
    Nr_A5: str
    Nr_A6: str 
    Txt_Nom_Forn: str
    Nr_NF: str
    Nr_ItemNF: str
    Nr_SerieNF: str
    CNPJ_Forn: str

    class Config:
        extra = 'forbid'
    
    @field_validator('FLG_PLPT', mode="before")
    @classmethod
    def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
    
    @field_validator('CNPJ_Forn', mode="before")
    @classmethod
    def validar_cnpj(cls, value):
        return validar_CNPJ(value)
    
    @field_validator('Cd_NG', mode="before")
    @classmethod
    def validar_vl_cdng(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=7)
    
    @field_validator('Cd_CA', mode="before")
    @classmethod
    def validar_vl_cdca(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=6)
    
    @field_validator('VL_tot', 'Qtd', mode="before")
    @classmethod
    def validar_vl_voc(cls, value):
        return validar_decimal(value)
    
    @field_validator('Nr_TUC', mode="before")
    @classmethod
    def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=100, max_val=999, vazio=True)
        if  (nm != None) and (nm != '') and (not ValoresTUC.teste(int(value))):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm
        
    @field_validator('Nr_TI', mode="before")
    @classmethod
    def validar_TI(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=1, max_val=100, vazio=True)
        if (nm != None) and (nm != '') and (not ValoresTI.teste(int(value))):
            raise ValueError(f'O dado não é válido como TI.\n')
        return nm
    
    @field_validator('Dt_Lcmto', mode="before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
    
    @field_validator('Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6', mode="before")
    @classmethod
    def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99, vazio=True)
    
    @field_validator('Ide_RO_Analitico', mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name)
    
    @field_validator('Nr_NF', mode="before")
    @classmethod
    def validar_Txt_N(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=50)
        
    @field_validator('Unidade', 'Nr_ItemNF', 'Nr_SerieNF', mode="before")
    @classmethod
    def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=10)
          
    @field_validator('COD_ITEM','Cd_ODI', mode="before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
    
    @field_validator('Cd_Cls_Custo', mode="before")
    @classmethod
    def validar_cd2(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)
    
    @field_validator('Cd_ODD', mode="before")
    @classmethod
    def validar_cd1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)
   
    @field_validator('Txt_Nom_Forn', mode="before")
    @classmethod
    def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
    
class TabelaROD(BaseModel):
    tabela: List[ROD]

class DSCCLS(BaseModel):
    Cd_Cls_Custo: str
    Txt_Cls_Custo: str

    class Config:
        extra = 'forbid'
   
    @field_validator('Cd_Cls_Custo')
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
        
    @field_validator('Txt_Cls_Custo')
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)

class TabelaDSCCLS(BaseModel):
    tabela: List[DSCCLS]

class LSTMAT(BaseModel):
    COD_ITEM: str
    COD_ITEM_SPD: str
    DESCR_ITEM: str
    Nr_FC: str
    CD_Nm_Reg: str
    Cd_DE_PARA: str
    FLG_AGR: str
    CD_Nm_Reg_ST: str

    class Config:
        extra = 'forbid'
   
    @field_validator('COD_ITEM','COD_ITEM_SPD', mode="before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
    
    @field_validator('DESCR_ITEM', mode="before")
    @classmethod
    def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
    
    @field_validator('Cd_DE_PARA', mode="before")
    @classmethod
    def validar_depara(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)
        
    @field_validator('Nr_FC', mode="before")
    @classmethod
    def validar_FC(cls, value):
        return validar_decimal(value, vazio=True)
    
    @field_validator('FLG_AGR', mode="before")
    @classmethod
    def validar_FLG_AGR(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=False, min_val=0, max_val=1)
    
    @field_validator('CD_Nm_Reg', mode="before")
    @classmethod
    def validar_Cd_Nm(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=23)
    
    @field_validator('CD_Nm_Reg_ST', mode="before")
    @classmethod
    def validar_Cd_Nm1(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=33)


class TabelaLSTMAT(BaseModel):
    tabela: List[LSTMAT]
        
class LSTSER(BaseModel):
    COD_ITEM: str
    DESCR_ITEM: str
    FLG_OAT: str
    TP_SERV: str
    CD_Nm_Reg_ST: str
    FT_CNV_ST_MAT: str
    COD_ITEM_CDS: str

    class Config:
        extra = 'forbid'
        
    @field_validator('FLG_OAT', mode = "before")
    @classmethod
    def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
   
    @field_validator('COD_ITEM')
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
    
    @field_validator('COD_ITEM_CDS')
    @classmethod
    def validar_cd1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255, vazio=True)
        
    @field_validator('CD_Nm_Reg_ST', mode="before")
    @classmethod
    def validar_Cd_Nm(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=33)
    
    @field_validator('DESCR_ITEM', mode="before")
    @classmethod
    def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
    
    @field_validator('TP_SERV')
    @classmethod
    def validar_Cd_Nm1(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=11)
    
    @field_validator('FT_CNV_ST_MAT', mode="before")
    @classmethod
    def validar_FC(cls, value):
        return validar_decimal(value, vazio=True)
    
class TabelaLSTSER(BaseModel):
    tabela: List[LSTSER]
        
class LSTFCUM(BaseModel):
    COD_ITEM: str
    UNID_CONV: str
    FAT_CONV: str
    UNID_AIS: str

    class Config:
        extra = 'forbid'
   
    @field_validator('COD_ITEM', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
        
    @field_validator('UNID_CONV','UNID_AIS', mode = "before")
    @classmethod
    def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
        
    @field_validator('FAT_CONV', mode = "before")
    @classmethod
    def validar_fat(cls, value):
        return validar_decimal(value, min_val=0)

class TabelaLSTFCUM(BaseModel):
    tabela: List[LSTFCUM]
        
class LSTOBREMG(BaseModel):
    Id_OBR_EM: str
    Nr_Ordem: str
    Txt_OCORR: str
    Dt_INI: str
    Hr_INI: str
    Fr_INI: str
    Cd_CONJ: str
    Dt_AUT: str
    Hr_AUT: str
    Dt_CHEG: str
    Hr_CHEG: str
    Dt_REST: str
    Hr_REST: str
    Cd_PROJ: str
    TP_EQP: str
    Nr_TI: str
    Hr_ODI: str
    Hr_TOT: str
    Qtd_km_Desl: str
    Txt_Causa: str
    Txt_Nom_Forn: str
    Nr_NF: str
    Nr_ItemNF: str
    Nr_SerieNF: str
    CNPJ_Forn: str
        
    class Config:
        extra = 'forbid'
    
    @field_validator('Dt_INI','Dt_AUT','Dt_CHEG','Dt_REST')
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
            
    @field_validator('Hr_INI','Hr_AUT','Hr_CHEG','Hr_REST','Hr_ODI','Hr_TOT', mode="before")
    @classmethod
    def validar_Hr(cls, value):
        if isinstance(value, str):
            if (value is None) or (value == ''):
                raise ValueError(f'Não pode estar vazio.\n')
            if len(value) != 8:
                raise ValueError(f'O dado deve ter 8 caracteres.\n')
            if not re.match(r'^\d{2}:\d{2}:\d{2}$', value):
                raise ValueError(f'A data deve estar no formato HH:MM:SS.\n')
            return value
        else:
            raise ValueError(f"O valor não é do tipo esperado.\n")
     
    @field_validator('Nr_Ordem', mode="before")
    @classmethod
    def validar_cd3(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)
        
    @field_validator('TP_EQP', mode="before")
    @classmethod
    def validar_cd(cls, value,info):
        return validar_texto(value, info.field_name, max_len=25, dominio = ['LEVE','MÉDIA','PESADA','VIVA'])
        
    @field_validator('Cd_PROJ','Cd_CONJ', mode="before")
    @classmethod
    def validar_cd1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50)
        
    @field_validator('Txt_Nom_Forn', mode="before")
    @classmethod
    def validar_cd2(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000, vazio=True)
    
    @field_validator('Txt_Causa','Txt_OCORR', mode="before")
    @classmethod
    def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
    
    @field_validator('Fr_INI', mode="before")
    @classmethod
    def validar_frini(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=4)
    
    @field_validator('CNPJ_Forn', mode="before")
    @classmethod
    def validar_cnpj(cls, value):
        return validar_CNPJ(value)
    
    @field_validator('Nr_SerieNF', mode="before")
    @classmethod
    def validar_serie(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=999999, vazio=True)
        
    @field_validator('Nr_NF','Nr_ItemNF', mode="before")
    @classmethod
    def validar_nr(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True)
            
    @field_validator('Nr_TI', mode="before")
    @classmethod
    def validar_TI(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=1, max_val=100, vazio=True)
        if (nm != None) and (nm != '') and (not ValoresTI.teste(int(value))):
            raise ValueError(f'O dado não é válido como TI.\n')
        return nm
        
    @field_validator('Id_OBR_EM', mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)

class TabelaLSTOBREMG(BaseModel):
    tabela: List[LSTOBREMG]
        
class LSTMATEMG(BaseModel):
    Id_MAT_OBR_EM: str
    COD_ITEM: str
    Qtd: str
    Unidade: str
    Nr_TUC: str
    Nr_A1: str
    Nr_A2: str
    Nr_A3: str
    Nr_A4: str
    Nr_A5: str
    Nr_A6: str
    Id_OBR_EM: str

    class Config:
        extra = 'forbid'
        
    @field_validator('Qtd', mode="before")
    @classmethod
    def validar_FLG(cls, value):
        return validar_decimal(value, min_val=0)
        
    @field_validator('Unidade', mode="before")
    @classmethod
    def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
    
    @field_validator('COD_ITEM', mode="before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
        
    @field_validator('Nr_TUC', mode="before")
    @classmethod
    def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=100, max_val=999, vazio=True)
        if (nm != None) and (nm != '') and (not ValoresTUC.teste(int(value))):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm
        
    @field_validator('Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6', mode="before")
    @classmethod
    def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99, vazio=True)
        
    @field_validator('Id_MAT_OBR_EM','Id_OBR_EM', mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name,  vazio=True)
    
class TabelaLSTMATEMG(BaseModel):
    tabela: List[LSTMATEMG]

class tblDTenePat(BaseModel):
    Id_DT_ENERG: str
    Cd_Patrim: str
    Cd_DIG_INC: str
    Dt_Energ: str

    class Config:
        extra = 'forbid'
   
    @field_validator('Id_DT_ENERG', mode="before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)
    
    @field_validator('Cd_Patrim', mode="before")
    @classmethod
    def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
    
    @field_validator('Cd_DIG_INC', mode="before")
    @classmethod
    def validar_depara(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
        
    @field_validator('Dt_Energ', mode="before")
    @classmethod
    def validar_FC(cls, value):
        return validar_data(value)

class TabelaDTenePat(BaseModel):
    tabela: List[tblDTenePat]

class TBLMed(BaseModel):
    Ide_COM_MED: str
    Cd_MED: str
    COD_ITEM: str
    Cd_TIP_MED: str
    Cd_TP_MED: str
    Nr_fases: str
    Cd_CAP: str

    class Config:
        extra = 'forbid'
        
    @field_validator('Ide_COM_MED','Cd_CAP', mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)
        
    @field_validator('Cd_MED','COD_ITEM', mode="before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 25)
        
    @field_validator('Cd_TIP_MED','Cd_TP_MED', mode="before")
    @classmethod
    def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)

    @field_validator('Nr_fases', mode="before")
    @classmethod
    def validar_nr_fas(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)

class TabelaMed(BaseModel):
    tabela: List[TBLMed]

class TBLNTcom(BaseModel):
    Id_NRM_COM: str
    Nm_Variavel: str
    QTD_NORM: str

    class Config:
        extra = 'forbid'
        
    @field_validator('Id_NRM_COM', mode="before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Nm_Variavel', mode="before")
    @classmethod
    def validar_cd(cls, value, info):
        nm = validar_texto(value, info.field_name, max_len = 50)
        if (nm != None) and (nm != None) and (not ValoresNmVAR.teste(value)):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
  
    @field_validator('QTD_NORM', mode="before")
    @classmethod
    def validar_FLG(cls, value):
        return validar_decimal(value, min_val=0)   

class TabelaNTcom(BaseModel):
    tabela: List[TBLNTcom]
        
class TBLNTcmu(BaseModel):
    Ide_CMU_ST: str
    Ano_Ref: str
    VL_US_ST: str
    Cd_CMU_ST: str

    class Config:
        extra = 'forbid'
        
    @field_validator('Ide_CMU_ST', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Cd_CMU_ST', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=14)

    @field_validator('VL_US_ST', mode = "before")
    @classmethod
    def validar_us(cls, value):
        return validar_decimal(value, min_val=0)
    
    @field_validator('Ano_Ref', mode = "before")
    @classmethod
    def validar_ano(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val = 2000)

class TabelaNTcmu(BaseModel):
    tabela: List[TBLNTcmu]

class TBLOEagr(BaseModel):
    Id_OE: str
    Cd_CC: str
    TP_OE: str
    VL_SLD_INI: str
    VL_SLD_REAV: str
    Dt_REF: str
    
    class Config:
        extra='allow'

    @field_validator('VL_SLD_INI','VL_SLD_REAV', mode = "before")
    @classmethod
    def validar_vl(cls, v):
       return validar_decimal(v)

    @field_validator('Dt_REF', mode = "before")
    @classmethod
    def validar_dt(cls, v):
       return validar_data(v)

    @field_validator('TP_OE', mode = "before")
    @classmethod
    def validar_tp(cls, v, info):
       return validar_texto(v, info.field_name, dominio=["Outros","PLPT","IR","CCC","Tx_MED_AMORT"])
        
    @field_validator('Id_OE', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
       return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name, vazio=True)
        if (nm != '') and (nm != None) and (not ValoresCCOE.teste(value)):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo, desconsiderar caso seja linha de Tx_MED_AMORT.\n")
        return nm
    
    @model_validator(mode="wrap")
    @classmethod
    def validar_vls(cls, values, handler):
        validation_error = None
        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(
                                        exclude={'Id_OE_MOV', 'Cd_CC', 'TP_OE', 'VL_SLD_INI', 'VL_SLD_REAV', 'Dt_REF', None}
                                    )
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))
        if validation_error is not None:
            raise validation_error
        return result    
       
class TabelaOEagr(BaseModel):
    tabela: List[TBLOEagr]

class TBLOEajt(BaseModel):
    Id_OE_AJS: str
    Txt_AJS: str
    VL_SALDO_AJS: str
    Dt_REF: str
    Cd_CC: str
    FLG_INC: str

    class Config:
        extra = 'forbid'
        
    @field_validator('FLG_INC', mode = "before")
    @classmethod
    def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
        
    @field_validator('Id_OE_AJS', mode = "before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)
        
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
        
    @field_validator('VL_SALDO_AJS', mode = "before")
    @classmethod
    def validar_us(cls, value):
        return validar_decimal(value)
    
    @field_validator('Dt_REF', mode = "before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)

class TabelaOEajt(BaseModel):
    tabela: List[TBLOEajt]

class TBLOEsldini(BaseModel):
    Id_OE_SI: str
    Cd_CC: str
    VL_SALDO_INIC: str
    Dt_REF: str

    class Config:
        extra = 'forbid'
        
    @field_validator('Id_OE_SI', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm

    @field_validator('VL_SALDO_INIC', mode = "before")
    @classmethod
    def validar_us(cls, value):
        return validar_decimal(value)
    
    @field_validator('Dt_REF', mode = "before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)

class TabelaOEsldini(BaseModel):
    tabela: List[TBLOEsldini]
        
class TBLOEreav(BaseModel):
    Id_OE_REAV: str
    Cd_CC: str
    VL_SALDO: str
    Dt_REF: str

    class Config:
        extra = 'forbid'
        
    @field_validator('Id_OE_REAV', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm

    @field_validator('VL_SALDO', mode = "before")
    @classmethod
    def validar_us(cls, value):
        return validar_decimal(value)
    
    @field_validator('Dt_REF', mode = "before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)

class TabelaOEreav(BaseModel):
    tabela: List[TBLOEreav]

class TBLOEmov(BaseModel):
    Id_OE_MOV: str
    Cd_CC: str
    
    class Config:
        extra='allow'
        
    @field_validator('Id_OE_MOV', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
    
    @model_validator(mode="wrap")
    @classmethod
    def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_MOV', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result  
        
class TabelaOEmov(BaseModel):
    tabela: List[TBLOEmov]
        
class TBLOEamt(BaseModel):
    Id_OE_AMT: str
    Cd_CC: str
    
    class Config:
        extra='allow'
        
    @field_validator('Id_OE_AMT', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
        
    @model_validator(mode="wrap")
    @classmethod
    def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_AMT', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result
       
class TabelaOEamt(BaseModel):
    tabela: List[TBLOEamt]
               
class TBLOEirmov(BaseModel):
    Id_OE_MOV: str
    Cd_CC: str
    
    class Config:
        extra='allow'
        
    @field_validator('Id_OE_MOV', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
        
    @model_validator(mode="wrap")
    @classmethod
    def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_MOV', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result     
       
class TabelaOEirmov(BaseModel):
    tabela: List[TBLOEirmov]
        
class TBLOEiramt(BaseModel):
    Id_OE_AMT: str
    Cd_CC: str
    
    class Config:
        extra='allow'
        
    @field_validator('Id_OE_AMT', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm

    @model_validator(mode="wrap")
    @classmethod
    def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_AMT', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result   
   
class TabelaOEiramt(BaseModel):
    tabela: List[TBLOEiramt]
        
class TBLOEplptmov(BaseModel):
    Id_OE_MOV: str
    Cd_CC: str
    
    class Config:
        extra='allow'
        
    @field_validator('Id_OE_MOV', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm

    @model_validator(mode="wrap")
    @classmethod
    def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_MOV', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result     
  
class TabelaOEplptmov(BaseModel):
    tabela: List[TBLOEplptmov]
        
class TBLOEplptamt(BaseModel):
    Id_OE_AMT: str
    Cd_CC: str
    
    class Config:
        extra='allow'
        
    @field_validator('Id_OE_AMT', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
    
    @model_validator(mode="wrap")
    @classmethod
    def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_AMT', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result   
   
class TabelaOEplptamt(BaseModel):
    tabela: List[TBLOEplptamt]
        
class TBLOEcccmov(BaseModel):
    Id_OE_MOV: str
    Cd_CC: str
    
    class Config:
        extra='allow'
        
    @field_validator('Id_OE_MOV', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
    
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
 
    @model_validator(mode="wrap")
    @classmethod
    def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_MOV', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result     
     
class TabelaOEcccmov(BaseModel):
    tabela: List[TBLOEcccmov]
        
class TBLOEcccamt(BaseModel):
    Id_OE_AMT: str
    Cd_CC: str
    
    class Config:
        extra='allow'
        
    @field_validator('Id_OE_AMT', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
        
    @model_validator(mode="wrap")
    @classmethod
    def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_AMT', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result    

class TabelaOEcccamt(BaseModel):
    tabela: List[TBLOEcccamt]

class TBLBPec(BaseModel):
    Id_Ext_CMP: str
    COD_ITEM: str
    Cd_NG: str
    Cd_Pedido: str
    Txt_Nom_Forn: str
    Cd_Forn: str
    CNPJ_Forn: str
    Nr_SerieNF: str
    Nr_NF: str
    Dt_NF: str
    Nr_Item_NF: str
    Txt_Desc_Mat: str
    Cd_NCM: str
    Cd_EXTIPI: str
    Cd_CFOP: str
    Qtd: str
    Cd_Unid: str
    CST_ICMS: str
    ALIQ_ICMS: str
    CST_IPI: str
    ALIQ_IPI: str
    VL_TOT_ICMS: str
    VL_TOT_IPI: str
    VL_TOT_LIQ: str
    FLG_BPR: str
    FLG_TP: str
    Cd_NFe: str
    VL_DIFAL: str
    VL_ST: str
    FLG_ICMS: str
    FLG_TPNF: str
    FLG_IMP: str
    VL_BC: str
    VL_Desp_ADU: str
    VL_II: str
    VL_IOF: str
    VL_ODC: str | None = None

    model_config = ConfigDict(extra="forbid")
        
    @field_validator('Id_Ext_CMP', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('COD_ITEM', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
        
    @field_validator('CST_IPI', mode = "before")
    @classmethod
    def validar_cstipi(cls, value, info):
        return validar_texto(value, info.field_name, max_len=2, dominio=['00','01','02','03','04','05',
                                                                         '0','1','2','3','4','5','49',
                                                                  '50','51','52','53','54','55','99'])  
    @field_validator('CST_ICMS', mode = "before")
    @classmethod
    def validar_csticms(cls, value, info):
        return validar_texto(value, info.field_name, max_len=3, dominio=['0','10','30','40','41','50','51','60','70','90',
                                                                  '101','102','103','201','202','203','300','400','500','900',
                                                                  '100','200','300','400','500','600','700','800',
                                                                  '110','210','310','410','510','610','710','810',
                                                                  '120','220','320','420','520','620','720','820',
                                                                  '130','230','330','430','530','630','730','830',
                                                                  '140','240','340','440','540','640','740','840',
                                                                  '141','241','341','441','541','641','741','841',
                                                                  '150','250','350','450','550','650','750','850',
                                                                  '151','251','351','451','551','651','751','851',
                                                                  '260','360','460','560','760','860','270','370',
                                                                  '470','570','770','870','190','290','390','490',
                                                                  '590','690','790','890'])
        
    @field_validator('Cd_Pedido', 'Cd_Forn', mode = "before")
    @classmethod
    def validar_cdp(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)
    
    @field_validator('Txt_Nom_Forn','Txt_Desc_Mat', mode = "before")
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
        
    @field_validator('FLG_TPNF','FLG_IMP','FLG_TP','FLG_BPR', mode = "before")
    @classmethod
    def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
    
    @field_validator('VL_TOT_ICMS','VL_TOT_IPI','VL_TOT_LIQ','VL_BC','VL_Desp_ADU','VL_II',
                     'VL_IOF','Qtd', 'VL_DIFAL','VL_ST', mode = "before")
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value)

    @field_validator('VL_ODC', mode='before')
    @classmethod
    def validar_vl_odc(cls, value, info):

        if value is None or str(value).strip() == "":
            return None

        return validar_decimal(value)
    
    @field_validator('ALIQ_ICMS','ALIQ_IPI', mode = "before")
    @classmethod
    def validar_al(cls, value):
        return validar_decimal(value, min_val=0, max_val=1)
           
    @field_validator('Dt_NF', mode = "before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
        
    @field_validator('Cd_NG', mode = "before")
    @classmethod
    def validar_vl_cdng(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=7)
    
    @field_validator('Cd_Unid', mode = "before")
    @classmethod
    def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
    
    @field_validator('Cd_CFOP', mode = "before")
    @classmethod
    def validar_cfop(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCFOP.teste(value):
            raise ValueError(f"CFOP inválido, verifique se é válido na SEFAZ.\n")
        return nm
        
    @field_validator('Cd_NCM', mode = "before")
    @classmethod
    def validar_ncm(cls, value, info):
        return validar_inteiro(value, info.field_name)
    
    @field_validator('Cd_EXTIPI', mode = "before")
    @classmethod
    def validar_extipi(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, vazio=True)
        
    @field_validator('CNPJ_Forn', mode = "before")
    @classmethod
    def validar_cnpk(cls, value):
        numero = digitos(value)

        if len(numero) == 11:
            raise ValueError(
                                "O campo CNPJ_Forn contém 11 dígitos, "
                                "quantidade correspondente a um CPF. "
                                "Verifique se foi informado um CPF em vez de um CNPJ e se está correto."
                            )
        return validar_CNPJ(value)
    
    @field_validator('Nr_SerieNF', mode = "before")
    @classmethod
    def validar_serie(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=1000000)
        
    @field_validator('Nr_NF','Nr_Item_NF', mode = "before")
    @classmethod
    def validar_nr(cls, value, info):
        return validar_inteiro(value, info.field_name)
        
    @field_validator('Cd_NFe', mode = "before")
    @classmethod
    def validar_NFe(cls, value, info):
        if value is None or str(value).strip() == "":
            return ""
        chave = str(value).strip()
        if not chave.isascii() or not chave.isdigit():
            raise ValueError("Cd_NFe deve conter somente dígitos.")
        return chave
        
    @model_validator(mode="after")
    def verifica_dados(self):
        erros = []
        self._validar_cfop(erros)
        self._validar_chave_nfe(erros)
        self._validar_flags(erros)
        self._validar_ipi(erros)
        self._validar_icms(erros)
        self._validar_valores(erros)
        self._validar_aliquotas(erros)

        if erros:
            raise ValidationError.from_exception_data(type(self).__name__, erros)
        return self

    def _erro(self, erros: list, campo: str, mensagem: str) -> None:
        erros.append({
                        "type": PydanticCustomError("regra_negocio", mensagem),
                        "loc": (campo,),
                        "input": getattr(self, campo, None),
                    })

    @staticmethod
    def _texto(valor) -> str:
        return "" if valor is None else str(valor)

    def _valor(self, campo: str):
        return conv_flut(getattr(self, campo))

    @staticmethod
    def _normalizar_numero(valor) -> str:
        return str(valor or "").lstrip("0") or "0"

    def _validar_cfop(self, erros: list) -> None:
        cfop = self._texto(self.Cd_CFOP)
        if cfop.startswith(("4", "5", "6")):
            self._erro(erros, "Cd_CFOP", "CFOP de saída ao invés de entrada")

    def _validar_chave_nfe(self, erros: list) -> None:
        chave = digitos(self.Cd_NFe)
        if not chave:
            return

        if len(chave) != 44:
            self._erro(erros, "Cd_NFe", "Chave da NFe deve possuir 44 dígitos")
            return 

        for campo, descricao, trecho in (
                                            ("CNPJ_Forn", "CNPJ", chave[6:20]),
                                            ("Nr_SerieNF", "Número de série", chave[22:25]),
                                            ("Nr_NF", "Número da NFe", chave[25:34]),
                                        ):
            informado = digitos(getattr(self, campo))
            if self._normalizar_numero(trecho) != self._normalizar_numero(informado):
                self._erro(erros, campo, f"{descricao} não confere com a chave da NFe")

        data = self.Dt_NF
        if hasattr(data, "strftime"):
            ano_mes = data.strftime("%y%m")
        else:
            texto = self._texto(data)
            if len(texto) < 7 or texto[4:5] != "-":
                self._erro(erros, "Dt_NF", "Data da NFe inválida para comparação com a chave")
                return
            ano_mes = texto[2:4] + texto[5:7]

        if chave[2:6] != ano_mes:
            self._erro(erros, "Dt_NF", "Data da NFe não confere com a chave da NFe")

    def _validar_flags(self, erros: list) -> None:
        cfop = self._texto(self.Cd_CFOP)
        flg_icms = self._texto(self.FLG_ICMS)
        flg_bpr = self._texto(self.FLG_BPR)
        flg_tpnf = self._texto(self.FLG_TPNF)
        qtd = self._valor("Qtd")
        vl_icms = self._valor("VL_TOT_ICMS")
        vl_difal = self._valor("VL_DIFAL")

        if flg_icms != "0" and vl_difal + vl_icms < 0.1:
            self._erro(erros, "FLG_ICMS", "Verifique o FLG_ICMS")
        if flg_bpr in {"0", ""} and cfop in CFOPS_BPR:
            self._erro(erros, "FLG_BPR", "Verifique o FLG_BPR")
        if flg_tpnf == "0" and qtd != 0:
            self._erro(erros, "Qtd", "Nota complementar com quantidade diferente de zero")

    def _validar_ipi(self, erros: list) -> None:
        cst_ipi = self._texto(self.CST_IPI)
        if not cst_ipi.endswith("0") and self._valor("VL_TOT_IPI") != 0:
            self._erro(erros, "VL_TOT_IPI", "Verificar CST_IPI ou VL_TOT_IPI — parece isento")

    def _validar_icms(self, erros: list) -> None:
        cst_final = self._texto(self.CST_ICMS)[-2:]
        if cst_final not in CST_ICMS_COM_ICMS and self._valor("VL_TOT_ICMS") != 0:
            self._erro(erros, "VL_TOT_ICMS", "Verificar CST_ICMS ou VL_TOT_ICMS — não parece ter ICMS")
        if cst_final not in CST_ICMS_COM_ST and self._valor("VL_ST") != 0:
            self._erro(erros, "VL_ST", "Verificar CST_ICMS ou VL_ST — não parece ser ST")
        if cst_final not in CST_ICMS_COM_ICMS and self._valor("VL_DIFAL") != 0:
            self._erro(erros, "VL_DIFAL", "Verificar CST_ICMS ou VL_DIFAL — não parece ser DIFAL")

    def _validar_valores(self, erros: list) -> None:
        cfop = self._texto(self.Cd_CFOP)
        if (cfop in ['2101','2102','2551','2556','2406','2407']) and abs(self._valor("VL_DIFAL")) <= 1:
            self._erro(erros, "VL_DIFAL", f"Verificar VL_DIFAL — não parece correto; CFOP = {cfop}")
        if abs(self._valor("VL_TOT_LIQ")) <= 1:
            self._erro(erros, "VL_TOT_LIQ", "Verificar VL_TOT_LIQ — não parece correto")

    def _validar_aliquotas(self, erros: list) -> None:
        vl_ipi = self._valor("VL_TOT_IPI")
        vl_icms = self._valor("VL_TOT_ICMS")
        vl_liq = self._valor("VL_TOT_LIQ")
        total = vl_ipi + vl_icms + vl_liq
        if total <= 0:
            return
        if abs(vl_ipi / total - self._valor("ALIQ_IPI")) > 1e-6:
            self._erro(erros, "ALIQ_IPI", "Verificar ALIQ_IPI ou VL_TOT_IPI — não parecem corretos")
        if abs(vl_icms / total - self._valor("ALIQ_ICMS")) > 1e-3:
            self._erro(erros, "ALIQ_ICMS", "Verificar ALIQ_ICMS ou VL_TOT_ICMS — não parecem corretos")

class TabelaBPec(BaseModel):
    tabela: List[TBLBPec]
        
class TBLBPfpuar(BaseModel):
    Id_BP_FP: str
    Nr_Parcela: str
    VL_Parcela: str
    Dt_PMTO: str
    Txt_OBS: str
    Id_Ext_CMP: str
    Nr_DOC_COMP: str

    class Config:
        extra = 'forbid'  
            
    @field_validator('Id_BP_FP', 'Id_Ext_CMP', 'Nr_Parcela', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Txt_OBS', mode = "before")
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len = 1000)

    @field_validator('Nr_DOC_COMP', mode = "before")
    @classmethod
    def validar_txt1(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 50)
    
    @field_validator('VL_Parcela', mode = "before")
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)

    @field_validator('Dt_PMTO', mode = "before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
                   
class TabelaBPfpuar(BaseModel):
    tabela: List[TBLBPfpuar]
        
class TBLBPuar(BaseModel):
    Id_BP: str
    COD_ITEM: str
    Nr_TUC: str
    Nr_A1: str
    Nr_A2: str
    Nr_A3: str
    Nr_A4: str
    Nr_A5: str
    Nr_A6: str
    Qtd: str
    VL_VF: str
    VL_ICMS: str
    VL_ODC: str
    Nr_FORM: str
    VL_VF_UNIT_AT: str
    Txt_OBS: str
    COD_ITEM_DE: str

    class Config:
        extra = 'forbid'
        
    @field_validator('Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6', mode = "before")
    @classmethod
    def validar_nr_a1(cls, value, info):
         return validar_inteiro(value, info.field_name, min_val=0, max_val=99)
        
    @field_validator('Nr_TUC', mode = "before")
    @classmethod
    def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=100, max_val=999, vazio=True)
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm
            
    @field_validator('Id_BP', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
    
    @field_validator('COD_ITEM', mode = "before")
    @classmethod
    def validar_ITEM(cls, v, info):
        return validar_texto(v, info.field_name, max_len=25)
    
    @field_validator('COD_ITEM_DE', mode = "before")
    @classmethod
    def validar_ITEM1(cls, v, info):
        return validar_texto(v, info.field_name, vazio=True, max_len=25)
    
    @field_validator('Txt_OBS', mode = "before")
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
        
    @field_validator('Nr_FORM', mode = "before")
    @classmethod
    def validar_NRform(cls, value, info):
        return validar_texto(value, info.field_name, max_len=7)
    
    @field_validator('VL_VF_UNIT_AT', 'VL_VF','VL_ICMS','VL_ODC','Qtd', mode = "before")
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)

class TabelaBPuar(BaseModel):
    tabela: List[TBLBPuar]

class TBLCOMCABPCBPuar(BaseModel):
    Id_COM_CA: str
    Cd_TI: str
    PCT_COM: str
    PCT_CA: str
    FLG_PLPT_OE: str

    class Config:
        extra = 'forbid'
              
    @field_validator('Cd_TI', mode = "before")
    @classmethod
    def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=0, max_val=100)
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'O dado não é válido no domínio ({value}).\n')
        return nm
            
    @field_validator('Id_COM_CA', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
    
    @field_validator('PCT_COM','PCT_CA', mode = "before")
    @classmethod
    def validar_ITEM(cls, v):
        return validar_decimal(v, min_val=0)

    @field_validator('FLG_PLPT_OE', mode = "before")
    @classmethod
    def validar_FLG(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=0, max_val=1)

class TabelaCOMCABPC(BaseModel):
    tabela: List[TBLCOMCABPCBPuar]
        
class TBLReform(BaseModel):
    Id_RFM: str
    Id_Ext_CMP: str
    Cd_ODD: str
    Cd_PAT_ANT: str
    Cd_PAT_AT: str
    Dt_Baixa: str
    Dt_RFM: str
    Txt_RFM: Optional[str]
    VL_RFM: str
    Txt_Desc_Serv: Optional[str]
    Txt_Nom_Forn: Optional[str]
    Qtd: str
    Unidade: str
    Txt_Desc_Bem: str
    Nr_TUC: str
    Nr_A1: str
    Nr_A2: str
    Nr_A3: str
    Nr_A4: str
    Nr_A5: str
    Nr_A6: str
    Dt_RET_AMX: str
    Dt_RIMB: str
    Txt_Forma_Aval: Optional[str]
    Txt_OBS: Optional[str]
    COD_ITEM: Optional[str]

    class Config:
        extra = 'forbid'
        
    @field_validator('Dt_Baixa','Dt_RFM','Dt_RET_AMX', mode = "before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value, vazio=True)
            
    @field_validator('Dt_RIMB', mode = "before")
    @classmethod
    def validar_Dtr(cls, value):
        return validar_data(value, vazio=True)
    
    @field_validator('Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6', mode = "before")
    @classmethod
    def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99, vazio=True)
        
    @field_validator('Nr_TUC', mode = "before")
    @classmethod
    def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=100, max_val=999, vazio=True)
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm
            
    @field_validator('Id_RFM', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
    
    @field_validator('Id_Ext_CMP', mode = "before")
    @classmethod
    def validar_ide1(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1, vazio=True)
    
    @field_validator('Txt_OBS','Txt_RFM','Txt_Desc_Serv','Txt_Nom_Forn','Txt_Desc_Bem','Txt_Forma_Aval','COD_ITEM', mode = "before")
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000, vazio=True)
    
    @field_validator('Cd_ODD','Cd_PAT_ANT', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50, vazio=True)
            
    @field_validator('Cd_PAT_AT', mode = "before")
    @classmethod
    def validar_cdop(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50, vazio=True)
        
    @field_validator('Unidade', mode = "before")
    @classmethod
    def validar_NRform(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
    
    @field_validator('VL_RFM', 'Qtd', mode = "before")
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value)               

class TabelaReform(BaseModel):
    tabela: List[TBLReform]

class TBLbcserv(BaseModel):
    Id_Ext_SRV: str
    COD_ITEM: str
    Cd_NG: str
    Nm_ST: str
    CNPJ_Forn: str
    Nr_NF: str
    Nr_SerieNF: str
    Dt_NF: str
    Dt_CMPT: str
    Nr_Item_NF: str
    CHV_NFSe: str
    Cd_SERV: str
    Desc_SERV: str
    Nm_MUN: str
    Qtd_US: str
    Cd_Unid_US: str
    VL_SERV: str
    VL_DESC_INC: str
    VL_DESC_CON: str
    VL_BASE_ISS: str
    ALIQ_ISS: str
    VL_ISS: str
    FLG_RET: str
    VL_RET_ISS: str
    VL_LIQ_NFE: str
    Nr_DOC_COMP: str
    Cd_CNTR: str
    TP_FAT: str
    CD_Nm_Reg_ST: str
    Qtd_MAT: str
    VL_MAT: str
    Txt_OBS: str

    class Config:
        extra = 'forbid'  
            
    @field_validator('Id_Ext_SRV', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('Txt_OBS','Desc_SERV', mode = "before")
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 1000, vazio=True)

    @field_validator('Nr_DOC_COMP','Cd_SERV', mode = "before")
    @classmethod
    def validar_txt1(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 50)
    
    @field_validator('Qtd_US','VL_SERV','VL_DESC_INC','VL_DESC_CON','VL_BASE_ISS',
                     'VL_ISS','VL_RET_ISS','VL_LIQ_NFE', mode = "before")
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value)

    @field_validator('Dt_NF','Dt_CMPT', mode = "before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)

    @field_validator('ALIQ_ISS', mode = "before")
    @classmethod
    def validar_al(cls, value):
        return validar_decimal(value, min_val=0, max_val=1)
        
    @field_validator('Cd_NG', mode = "before")
    @classmethod
    def validar_vl_cdng(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=4, max_val=7)
    
    @field_validator('Cd_Unid_US', mode = "before")
    @classmethod
    def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
        
    @field_validator('CNPJ_Forn', mode = "before")
    @classmethod
    def validar_cnpj(cls, value):
        return validar_CNPJ(value)
    
    @field_validator('Nr_SerieNF', mode = "before")
    @classmethod
    def validar_serie(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=1000000)
        
    @field_validator('Nr_NF','Nr_Item_NF', 'Nr_SerieNF', mode = "before")
    @classmethod
    def validar_nr(cls, value, info):
        return validar_inteiro(value, info.field_name)
        
    @field_validator('CHV_NFSe', mode = "before")
    @classmethod
    def validar_NFe(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True)

    @field_validator('FLG_RET', mode = "before")
    @classmethod
    def validar_FLG(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=0, max_val=1)
    
    @field_validator('TP_FAT', mode = "before")
    @classmethod
    def validar_TPFAT(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1, max_val=10)

    @field_validator('COD_ITEM')
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)
    
    @field_validator('Nm_ST','Nm_MUN','Cd_CNTR')
    @classmethod
    def validar_cd1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=150)
    
    @model_validator(mode="wrap")
    @classmethod
    def verifica_dados(cls, values, handler):
        validation_error = None
        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        linha = getattr(result, "Id_Ext_SRV", "—")
        Cd_NG = getattr(result, "Cd_NG", None)
        Desc_SERV = getattr(result, "Desc_SERV", None)
        COD_ITEM = getattr(result, "COD_ITEM", None)

        if (Cd_NG != "4") and (Desc_SERV in ["", None]):
            raise ValueError(f"Deve ser declarada a descrição do serviço, linha {linha}.\n")
        if (Cd_NG == "4") and (COD_ITEM in ["", None]):
            raise ValueError(f"Deve ser declarada COD_ITEM do serviço, linha {linha}.\n")
        if validation_error is not None:
            raise validation_error

        return result
                   
class Tabelabcserv(BaseModel):
    tabela: List[TBLbcserv]

class TBLMp(BaseModel):
    Id_MUD_PAT: str
    Cd_PAT_AT: str
    Cd_DIG_INC_AT: str
    Cd_PAT_ANT: str
    Cd_DIG_INC_ANT: str
    Qtd: str
    Unidade: str
    Txt_Desc_Bem: str
    Nr_TUC: str
    Nr_A1: str
    Nr_A2: str
    Nr_A3: str
    Nr_A4: str
    Nr_A5: str
    Nr_A6: str
    Qtd_AT: str
    Unidade_AT: str
    Txt_Desc_Bem_AT: str
    Nr_TUC_AT: str
    Nr_A1_AT: str
    Nr_A2_AT: str
    Nr_A3_AT: str
    Nr_A4_AT: str
    Nr_A5_AT: str
    Nr_A6_AT: str
    Dt_MUT: str
    Txt_OBS: str

    class Config:
        extra = 'forbid'

    @field_validator('Dt_MUT', mode = "before")
    @classmethod
    def validar_ide(cls, v):
        return validar_data(v)

    @field_validator('Id_MUD_PAT', mode = "before")
    @classmethod
    def validar_ide1(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val = 1)
    
    @field_validator('Txt_OBS','Txt_Desc_Bem','Txt_Desc_Bem_AT', mode = "before")
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 1000)
    
    @field_validator('Unidade','Unidade_AT', mode = "before")
    @classmethod
    def validar_txt1(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 10)
    
    @field_validator('Cd_PAT_AT','Cd_PAT_ANT', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 50)

    @field_validator('Cd_DIG_INC_AT', 'Cd_DIG_INC_ANT', mode = "before")
    @classmethod
    def validar_ide2(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val = 0)
                   
    @field_validator('Qtd_AT', 'Qtd', mode = "before")
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value)

    @field_validator('Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6', 
                     'Nr_A1_AT', 'Nr_A2_AT', 'Nr_A3_AT', 'Nr_A4_AT', 'Nr_A5_AT',
                     'Nr_A6_AT', mode = "before")
    @classmethod
    def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99)
        
    @field_validator('Nr_TUC','Nr_TUC_AT', mode = "before")
    @classmethod
    def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=100, max_val=999, vazio=True)
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm

class TabelaMp(BaseModel):
    tabela: List[TBLMp]

class TBLBaixas(BaseModel):
    Id_BX_INC: str
    Cd_ODI: str
    Cd_ODD: str
    Cd_PAT_ANT: str
    Cd_PAT_AT: str
    Nr_TI: str
    Nr_CM: str
    Nr_TUC: str
    Nr_A1: str
    Nr_A2: str
    Nr_A3: str
    Nr_A4: str
    Nr_A5: str
    Nr_A6: str
    Txt_DESC_TECN: str
    Cd_UAR: str
    Cd_UC: str
    Cd_Patrim: str
    Cd_DIG_INC: str
    Cd_UND_AIS: str
    Qtd_INI: str
    VL_VOC_INI: str
    Dt_Imob: str
    Dt_BX: str
    Qtd_FIN: str
    VL_VOC_FIN: str
    Id_SEQ_PP: str
    Txt_OBS_PP: str
    Txt_OBS_ODD: str
    FLG_AJST_CTB: str
    FLG_PER: Optional[str]
    FLG_ANT: Optional[str]

    class Config:
        extra = 'forbid'    
    
    @field_validator('Cd_UAR', mode="before")
    @classmethod
    def validar_UAR(cls, value, info):
        return validar_texto(value, info.field_name, dominio=['UC','UAR','TUC'])
    
    @field_validator('Id_BX_INC', mode="before")
    @classmethod
    def validar_ide1(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
        
    @field_validator('FLG_AJST_CTB','FLG_PER','FLG_ANT', mode="before")
    @classmethod
    def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
        
    @field_validator('Cd_UC', 'Cd_Patrim','Cd_ODI','Cd_ODD', mode="before")
    @classmethod
    def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50)
    
    @field_validator('Cd_PAT_ANT', mode="before")
    @classmethod
    def validar_cds1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50, vazio=True)
        
    @field_validator('Cd_DIG_INC', mode="before")
    @classmethod
    def validar_dig_inc(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
             
    @field_validator('Dt_BX','Dt_Imob', mode="before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
            
    @field_validator('Nr_TI', mode="before")
    @classmethod
    def validar_TI(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=1, max_val=100, vazio=True)
        if not ValoresTI.teste(int(value)):
            raise ValueError(f'O dado não é válido como TI.\n')
        return nm
        
    @field_validator('Nr_TUC', mode = "before")
    @classmethod
    def validar_TUC(cls, value, info):
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return value
            
    @field_validator('Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6')
    @classmethod
    def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99)
           
    @field_validator('Cd_PAT_AT')
    @classmethod
    def validar_ide(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=50)
    
    @field_validator('Txt_OBS_PP','Txt_DESC_TECN','Txt_OBS_ODD')
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
    
    @field_validator('Cd_UND_AIS')
    @classmethod
    def validar_NRform(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
    
    @field_validator('Qtd_INI', 'VL_VOC_INI', 'Qtd_FIN', 'VL_VOC_FIN')
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value, min_val = 0)
                   
    @model_validator(mode="wrap")
    @classmethod
    def verifica_dados(cls, values, handler):
        validation_error = None
        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        linha = getattr(result, "Id_BX_INC", "—")
        Nr_CM = getattr(result, "Nr_CM", None)
        Nr_TI = getattr(result, "Nr_TI", None)

        try:
            validar_cm(Nr_TI, Nr_CM, linha)
            validar_ti_distribuicao(Nr_TI, linha)
        except ValueError as ex:
            raise ValueError(f"Erro: {ex}") from ex

        if validation_error is not None:
            raise validation_error

        return result

class TabelaBaixas(BaseModel):
    tabela: List[TBLBaixas]
               
class TBLDescODI(BaseModel):
    Id_ODI: str
    Cd_ODI: str
    Txt_DESC_ODI: str

    class Config:
        extra = 'forbid'
        
    @field_validator('Cd_ODI')
    @classmethod
    def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50)

    @field_validator('Txt_DESC_ODI')
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
    
    @field_validator('Id_ODI')
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
                   
class TabelaDescODI(BaseModel):
    tabela: List[TBLDescODI]

class TBLPPBB(BaseModel):
    Id_SEQ_PP: str
    Cd_CICLO: str
    Id_AIS: str
    Cd_PAT_LAUDO: str
    Cd_DIG_INC: str
    Cd_ODI: str
    Cd_SubODI: str
    Cd_CC: str
    Nr_TI: str
    Nr_CM: str
    Nr_TUC: str
    Nr_A1: str
    Nr_A2: str
    Nr_A3: str
    Nr_A4: str
    Nr_A5: str
    Nr_A6: str
    Cd_UAR: str
    Cd_UC: str
    COD_ITEM: str
    Txt_DESC_TECN: str
    Qtd_AIS: str
    Cd_UND_AIS: str
    VL_VOC: str
    VL_DEP_ACUM: str
    Dt_Lcmto: str
    FLG_ELIG: str
    Cd_CONC: str
    VL_VNR_UC: str
    VL_IAI_UC: str
    VL_DAC_UC: str
    VL_VMU_UC: str
    VL_IAD_UC: str
    VL_VBR_UC: str
    VL_100DEP_UC: str
    Cd_Q5: str
    Cd_Q7: str
    Pct_OE: str
    Dt_REF_DADOS: str

    class Config:
        extra = 'forbid'
    
    @field_validator('COD_ITEM', mode="before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)
    
    @field_validator('Dt_Lcmto','Dt_REF_DADOS', mode="before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
    
    @field_validator('FLG_ELIG', mode="before")
    @classmethod
    def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
        
    @field_validator('Id_SEQ_PP', mode="before")
    @classmethod
    def validar_ide3(cls, value, info):
         return validar_inteiro(value, info.field_name, min_val=1)
            
    @field_validator('Cd_Q5','Cd_Q7', mode="before")
    @classmethod
    def validar_ide2(cls, v, info):
        return validar_texto(v, info.field_name, max_len=5)
            
    @field_validator('Cd_CONC', mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)
            
    @field_validator('Cd_CICLO', mode="before")
    @classmethod
    def validar_ide1(cls, v, info):
        return validar_texto(v, info.field_name, max_len=10)
            
    @field_validator('Id_AIS', mode="before")
    @classmethod
    def validar_ideais(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
    
    @field_validator('Nr_TI', mode="before")
    @classmethod
    def validar_TI(cls, value, info):
        if (value is not None) and (not ValoresTI.teste(int(value))):
            raise ValueError(f'O dado não é válido como TI.\n')
        return value
        
    @field_validator('Nr_TUC', mode = "before")
    @classmethod
    def validar_TUC(cls, value, info):
        if (value is not None) and (not ValoresTUC.teste(int(value))):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return value
            
    @field_validator('Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6', mode = "before")
    @classmethod
    def validar_nr_a1(cls, value, info):
        validar_inteiro(value, info.field_name, min_val=0, max_val=99, vazio=True)
    
    @field_validator('Txt_DESC_TECN', mode = "before")
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
    
    @field_validator('Cd_ODI', mode = "before")
    @classmethod
    def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)

    @field_validator('Cd_UC','Cd_PAT_LAUDO','Cd_SubODI', mode = "before")
    @classmethod
    def validar_cds1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000, vazio=True)
        
    @field_validator('Cd_DIG_INC', mode = "before")
    @classmethod
    def validar_dig_inc(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
        
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_CC(cls, value):
        if not ValoresCC.teste(value):
            raise ValueError(f'{value} dado não faz parte do domínio.\n')
        return value
    
    @field_validator('Cd_UAR', mode = "before")
    @classmethod
    def validar_UAR(cls, value, info):
        return validar_texto(value, info.field_name, max_len=3, dominio = ['UC','UAR','TUC'])
            
    @field_validator('Cd_UND_AIS', mode = "before")
    @classmethod
    def validar_NRform(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
            
    @field_validator('Qtd_AIS', 'VL_VOC', 'VL_DEP_ACUM', 'VL_VNR_UC', 'VL_IAI_UC', 'Pct_OE',
                     'VL_DAC_UC', 'VL_VMU_UC', 'VL_IAD_UC', 'VL_VBR_UC', 'VL_100DEP_UC', mode = "before")
    @classmethod
    def validar_vl(cls, value, info):
        return validar_decimal(value, min_val=0)
                   
    @model_validator(mode="wrap")
    @classmethod
    def verifica_dados(cls, values, handler):
        validation_error = None
        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        linha = getattr(result, "Id_SEQ_PP", "—")
        Nr_CM = getattr(result, "Nr_CM", None)
        Nr_TI = getattr(result, "Nr_TI", None)
        Dt_REF = getattr(result, "Dt_REF_DADOS", None)
        dt_INI = (
                    pd.to_datetime(st.session_state.dt_ini)
                    - pd.Timedelta(days=1)
                ).strftime("%Y/%m/%d")

        try:
            val_dt(Dt_REF, dt_INI)
            validar_cm(Nr_TI, Nr_CM, linha)
            validar_ti_distribuicao(Nr_TI, linha)
        except ValueError as ex:
            raise ValueError(f"Erro: {ex}") from ex

        if validation_error is not None:
            raise validation_error

        return result

class TabelaPPBB(BaseModel):
    tabela: List[TBLPPBB]
              
class TBLPCBB(BaseModel):
    Id_SEQ_PP: str
    Id_BX_INC: str
    Qtd_AISa: str
    VL_VOCa: str
    VL_VNR_UC: str
    VL_IAI_UC: str
    VL_DAC_UC: str
    VL_VMU_UC: str
    VL_IAD_UC: str
    VL_VBR_UC: str
    VL_100DEP_UC: str
    Dt_REF_DADOS: str
    FLG_ELIG: str
    Pct_IAI: str
    Cd_CONC: str

    class Config:
        extra = 'forbid'
      
    @field_validator('Dt_REF_DADOS', mode = "before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
    
    @field_validator('FLG_ELIG', mode = "before")
    @classmethod
    def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
        
    @field_validator('Id_SEQ_PP', mode = "before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)
                       
    @field_validator('Cd_CONC', mode = "before")
    @classmethod
    def validar_ide1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)
                    
    @field_validator('Id_BX_INC', mode = "before")
    @classmethod
    def validar_ideais(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, vazio=True)
               
    @field_validator('Qtd_AISa', 'VL_VOCa', 'VL_VNR_UC', 'VL_IAI_UC', 'VL_DAC_UC', 'VL_VMU_UC', 
                     'VL_IAD_UC', 'VL_VBR_UC', 'VL_100DEP_UC', mode = "before")
    @classmethod
    def validar_vl(cls, value, info):
        return validar_decimal(value, info.field_name, min_val = 0)
            
    @field_validator('Pct_IAI', mode = "before")
    @classmethod
    def validar_vl_pct_ori(cls, value, info):
        return validar_decimal(value, info.field_name, min_val = 0, max_val = 1)

    @field_validator('Cd_CONC', mode="before")
    @classmethod
    def validar_ide2(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)
    
    @model_validator(mode="wrap")
    @classmethod
    def verifica_dados(cls, values, handler):
        validation_error = None
        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        linha = getattr(result, "Id_SEQ_PP", "—")
        Dt_REF = getattr(result, "Dt_REF_DADOS", None)
        dt_FIM = (
                    pd.to_datetime(st.session_state.dt_fim)
                    - pd.Timedelta(days=0)
                ).strftime("%Y/%m/%d")

        try:
            val_dt(Dt_REF, dt_FIM)
        except ValueError as ex:
            raise ValueError(f"Erro: {ex}") from ex

        if validation_error is not None:
            raise validation_error

        return result

class TabelaPCBB(BaseModel):
    tabela: List[TBLPCBB]

def _decimal_incr(valor):
    return Decimal(str(valor).strip().replace(",", "."))

def _validar_dominio_bpr(codigo):
    if not ValoresBPR.teste(codigo):
        raise ValueError("Cd_SISBASE não pertence ao domínio BPR")
    
class TBLINCR(BaseModel):
    Id_SEQ_INC: str
    Id_AIS: str
    Cd_CC: str
    Cd_ODI: str
    Cd_SubODI: str
    Nr_TI: str
    Nr_CM: str
    Nr_TUC: str
    Nr_A1: str
    Nr_A2: str
    Nr_A3: str
    Nr_A4: str
    Nr_A5: str
    Nr_A6: str
    Cd_UAR: str
    Cd_UC: str
    Cd_Patrim: str
    Cd_DIG_INC: str
    COD_ITEM: str
    Qtd_AIS: str
    Cd_UND_AIS: str
    VL_VOC: str
    Dt_Imob: str
    VL_DEP_ACUM: str
    VL_VOC_VF: str
    VL_VOC_COM: str
    VL_VOC_CA: str
    VL_VOC_JOA: str
    VL_VOC_VF_AVAL: str
    VL_VOC_COM_AVAL: str
    VL_VOC_CA_AVAL: str
    VL_VOC_JOA_AVAL: str
    Cd_ODD: str
    Dt_BX: str
    Txt_DESC_TECN: str
    Txt_CLS_TNS: str
    FLG_RSV: str
    Cd_ODI_ENG: str
    Cd_TP_AVAL: str
    Cd_SISBASE: str
    Id_BP: str
    TP_BEM: str
    VL_VNR_UC: str
    VL_IAI_UC: str
    VL_DAC_UC: str
    VL_VMU_UC: str
    VL_IAD_UC: str
    VL_VBR_UC: str
    VL_100DEP_UC: str
    Pct_IA: str
    VL_VNR_VF_UNIT: str
    VL_VNR_COM_UNIT: str
    VL_VNR_CA_UNIT: str
    VL_VNR_JOA: str
    FLG_DOA_OE: str
    FLG_INCOR_OE: str
    FLG_PLPT_OE: str
    FLG_OAT: str
    FLG_REG: str
    FLG_ELIG: str
    Cd_CONC: str
    Cd_ABCC: str
    Cd_NumFIS: str
    Dt_REF_DADOS: str
    Dt_CNTB_AJST: str
    Pct_OE: str
    Cd_Q5: str

    class Config:
        extra = 'forbid'

    @field_validator('Cd_Q5', mode="before")
    @classmethod
    def validar_ide2a(cls, v, info):
        return validar_texto(v, info.field_name, max_len=5)
    
    @field_validator('Pct_IA','Pct_OE', mode = "before")
    @classmethod
    def validar_vl_pct_ori(cls, value, info):
        return validar_decimal(value, info.field_name, min_val = 0, max_val = 1)

    @field_validator('Cd_CONC', mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)
    
    @field_validator('COD_ITEM','Cd_NumFIS')
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
    
    @field_validator('Cd_ODD','Cd_ODI_ENG','Cd_ABCC')
    @classmethod
    def validar_cdx(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=25)
    
    @field_validator('Dt_Imob','Dt_REF_DADOS')
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
            
    @field_validator('Dt_CNTB_AJST', 'Dt_BX')
    @classmethod
    def validar_Dt1(cls, value):
        return validar_data(value, vazio=True)
    
    @field_validator('FLG_ELIG','FLG_RSV','FLG_DOA_OE','FLG_INCOR_OE','FLG_PLPT_OE','FLG_OAT','FLG_REG')
    @classmethod
    def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
        
    @field_validator('Id_SEQ_INC')
    @classmethod
    def validar_ide1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)                  
            
    @field_validator('TP_BEM')
    @classmethod
    def validar_ide2(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1,max_val=4)
            
    @field_validator('Cd_TP_AVAL')
    @classmethod
    def validar_ide3(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1,max_val=5)
                       
    @field_validator('Id_AIS','Id_BP')
    @classmethod
    def validar_ideais(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=0, vazio=True)
    
    @field_validator('Nr_TI', mode="before")
    @classmethod
    def validar_TI(cls, value, info):
        numero = validar_inteiro(value, info.field_name)
        if not ValoresTI.teste(int(numero)):
            raise ValueError(f'O dado não é válido como TI.\n')
        return value
    
    @field_validator('Nr_TUC', mode = "before")
    @classmethod
    def validar_TUC(cls, value, info):
        numero = validar_inteiro(value, info.field_name)
        if not ValoresTUC.teste(int(numero)):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return value
            
    @field_validator('Nr_A1', 'Nr_A2', 'Nr_A3', 'Nr_A4', 'Nr_A5', 'Nr_A6', mode = "before")
    @classmethod
    def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99)
    
    @field_validator('Txt_DESC_TECN','Txt_CLS_TNS', mode = "before")
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
            
    @field_validator('Cd_SISBASE', mode = "before")
    @classmethod
    def validar_sisbase(cls, value, info):
        return validar_texto(value, info.field_name, max_len=6, vazio=True)
    
    @field_validator('Cd_UC','Cd_Patrim','Cd_ODI','Cd_SubODI', mode = "before")
    @classmethod
    def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)
        
    @field_validator('Cd_DIG_INC', mode = "before")
    @classmethod
    def validar_dig_inc(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
        
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_CC(cls, value):
        if not ValoresCC.teste(value):
            raise ValueError(f'{value} fora do domínio aceito.\n')
        return value
        
    @field_validator('Cd_UAR', mode = "before")
    @classmethod
    def validar_UAR(cls, value, info):
        return validar_texto(value, info.field_name, dominio = ['UC','TUC','UAR'])
            
    @field_validator('Cd_UND_AIS', mode = "before")
    @classmethod
    def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
            
    @field_validator('Qtd_AIS', 'VL_VOC', 'VL_DEP_ACUM', 'VL_VNR_UC', 'VL_IAI_UC',
                     'VL_DAC_UC', 'VL_VMU_UC', 'VL_IAD_UC', 'VL_VBR_UC', 'VL_100DEP_UC', 
                     'VL_VNR_VF_UNIT', 'VL_VNR_COM_UNIT', 'VL_VNR_CA_UNIT', 'VL_VNR_JOA',
                     'VL_VOC_VF', 'VL_VOC_COM', 'VL_VOC_CA','VL_VOC_JOA','VL_VOC_VF_AVAL',
                     'VL_VOC_COM_AVAL','VL_VOC_CA_AVAL','VL_VOC_JOA_AVAL', mode = "before")
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value)
    
    @model_validator(mode="wrap")
    @classmethod
    def validar_regras_de_dominio(cls, values, handler):
        erros = []
        invalidos = set()
        try:
            resultado = handler(values)
        except ValidationError as exc:
            erros.extend(exc.errors(include_url=False))
            invalidos = {e["loc"][0] for e in erros if e.get("loc")}
            if not isinstance(values, dict):
                raise
            resultado = cls.model_construct(**values)

        def texto(campo):
            valor = getattr(resultado, campo, None)
            return "" if valor is None else str(valor).strip()

        def validar_tp_bem(ti, tuc, cc, tp_bem, linha):
            try:
                ti_num = int(ti)
            except (ValueError, TypeError):
                ti_num = None
            try:
                tuc_num = int(tuc)
            except (ValueError, TypeError):
                tuc_num = None

            tp_bem = str(tp_bem).strip()
            cc = str(cc).strip()

            motivos = []

            if ti_num is not None and (
                                            70 <= ti_num <= 91
                                            or ti_num in {94, 95, 97, 99}
                                        ):
                motivos.append(f"Nr_TI={ti}")

            if tuc_num in {230, 235, 535}:
                motivos.append(f"Nr_TUC={tuc}")

            if re.fullmatch(r"1232\d0\d05", cc):
                motivos.append(f"Cd_CC={cc} (veículos)")

            if motivos and tp_bem != "4":
                raise ValueError(
                    f"Id_SEQ_INC={linha}: TP_BEM esperava-se ser 4 "
                    f"quando houver enquadramento em "
                    f"{', '.join(motivos)}. "
                    f"Valor informado: TP_BEM={tp_bem}."
                )
        def validar_voc_ca_avaliacao_2(tp_aval, voc_ca, com_voc, linha):
            if str(tp_aval).strip() != "2":
                return
            try:
                valor_ca = float(voc_ca)
            except (TypeError, ValueError):
                return

            if float(valor_ca) == 0:
                raise ValueError(
                    f"Id_SEQ_INC={linha}: Para Cd_TP_AVAL=2, "
                    "VL_VOC_CA não pode ser zero. "
                    f"VL_COM_VOC={com_voc}; VL_VOC_CA={voc_ca}."
                )

        def validar_pct_oe(flg_doa, flg_incor, flg_plpt, pct_oe, linha):

            flags = {
                        "FLG_DOA_OE": flg_doa,
                        "FLG_INCOR_OE": flg_incor,
                        "FLG_PLPT_OE": flg_plpt
                    }

            flags_ativas = [
                                campo
                                for campo, valor in flags.items()
                                if str(valor).strip() == "1"
                            ]

            if (not flags_ativas):
                return

            try:
                percentual = float(str(pct_oe).strip().replace(",", "."))
            except (ValueError, TypeError):
                return
            
            if not percentual > 0:
                raise ValueError(
                    f"Id_SEQ_INC={linha}: Pct_OE deve ser maior que zero "
                    f"quando pelo menos um dos indicadores "
                    f"{', '.join(flags_ativas)} for igual a 1. "
                    f"Valor informado: Pct_OE={pct_oe}."
                )

        def executar(campo, dependencias, funcao, *args):
            if any(dep in invalidos for dep in dependencias):
                return
            try:
                funcao(*args)
            except (ValueError, TypeError, ArithmeticError) as exc:
                mensagem = str(exc).strip()
                erros.append({
                                "type": "value_error",
                                "loc": (campo,),
                                "input": getattr(resultado, campo, None),
                                "ctx": {"error": ValueError(mensagem)},
                            })

        linha = texto("Id_SEQ_INC")
        ti, cm, cc = texto("Nr_TI"), texto("Nr_CM"), texto("Cd_CC")
        tuc, a1 = texto("Nr_TUC"), texto("Nr_A1")
        a3, a4, a5 = texto("Nr_A3"), texto("Nr_A4"), texto("Nr_A5")
        und = texto("Cd_UND_AIS")
        tp_aval = texto("Cd_TP_AVAL")
        voc_ca = texto("VL_VOC_CA")
        com_voc = texto("VL_COM_VOC")
        tp_bem = texto("TP_BEM")
        flg_doa = texto("FLG_DOA_OE")
        flg_incor = texto("FLG_INCOR_OE")
        flg_plpt = texto("FLG_PLPT_OE")
        pct_oe = texto("Pct_OE")

        executar("Nr_CM", ("Nr_TI", "Nr_CM"), validar_cm, ti, cm, linha)
        executar("Nr_TI", ("Nr_TI",), validar_ti_distribuicao, ti, linha)
        executar("Cd_CC", ("Nr_TI", "Cd_CC"), validar_administracao, ti, cc, linha)
        executar("Nr_TUC", ("Nr_TUC", "Nr_A1", "Nr_A3", "Nr_A4", "Nr_A5", "Cd_UND_AIS"),
                 validar_cabos, tuc, a1, a3, a4, a5, und, linha)
        executar("Nr_TUC", ("Nr_TI", "Nr_TUC", "Nr_A1"),
                 validar_torre_poste, ti, tuc, a1, linha)
        executar("Nr_TUC", ("Nr_TUC",), validar_tucs_proibidos, tuc, linha)
        executar("VL_VOC_CA", ("Cd_TP_AVAL", "VL_VOC_CA", "VL_COM_VOC"), validar_voc_ca_avaliacao_2,
                 tp_aval, voc_ca, com_voc, linha)
        executar("TP_BEM", ("TP_BEM",), validar_tp_bem, ti, tuc,
                    cc, tp_bem, linha)
        executar("Pct_OE", ("Pct_OE", "FLG_DOA_OE", "FLG_INCOR_OE", "FLG_PLPT_OE"), validar_pct_oe, 
                 flg_doa, flg_incor, flg_plpt, pct_oe, linha)

        if erros:
            raise ValidationError.from_exception_data(cls.__name__, erros)
        return resultado

class TabelaINCR(BaseModel):
    tabela: List[TBLINCR]


class TBLAO(BaseModel):
    Id_SEQ_AO: str
    Cd_CC: str
    COD_ITEM: str
    Dt_LCMTO: str
    VL_LCMTO: str
    Qtd: str
    Cd_UND: str
    Txt_DESC_TECN: str
    FLG_CLS: str
        
    class Config:
        extra = 'forbid'

    @field_validator('COD_ITEM', mode = "before")
    @classmethod
    def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
    
    @field_validator('Dt_LCMTO', mode = "before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
            
    @field_validator('FLG_CLS', mode = "before")
    @classmethod
    def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
        
    @field_validator('Id_SEQ_AO', mode = "before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)
        
    @field_validator('Txt_DESC_TECN', mode = "before")
    @classmethod
    def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
                   
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=9)
                    
    @field_validator('Cd_UND', mode = "before")
    @classmethod
    def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
            
    @field_validator('Qtd', 'VL_LCMTO', mode = "before")
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)
                   
class TabelaAO(BaseModel):
    tabela: List[TBLAO]

class TBLECD(BaseModel):
    Id_SEQ_DePara: str
    COD_CTA: str
    Cd_CC: str
    Dt_ALT: str

    class Config:
        extra = 'forbid'       
    
    @field_validator('Id_SEQ_DePara', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
   
    @field_validator('Dt_ALT', mode = "before")
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
                     
    @field_validator('Cd_CC', mode = "before")
    @classmethod
    def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=15)
                    
    @field_validator('COD_CTA', mode = "before")
    @classmethod
    def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=15)
            
class TabelaECD(BaseModel):
    tabela: List[TBLECD]

class TBLTDOMUC(BaseModel):
    Id_SEQ_UC_DOM: str
    Nr_TUC: str
    Cd_ATRB: str
    Txt_Tipo: str
    Cd_DEF_EMP: str
    Txt_DEF_EMP: str
    
    class Config:
        extra = 'forbid'

    @field_validator('Id_SEQ_UC_DOM', mode = "before")
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
    
    @field_validator('Nr_TUC', mode = "before")
    @classmethod
    def validar_TUC(cls, value):
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'{value} não pertence ao domínio da variável.\n')
        return value
                          
    @field_validator('Txt_Tipo','Cd_DEF_EMP', mode = "before")
    @classmethod
    def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
                    
    @field_validator('Txt_DEF_EMP','Cd_ATRB', mode = "before")
    @classmethod
    def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)


class TabelaTDOMUC(BaseModel):
    tabela: List[TBLTDOMUC]

class TBLORATINCR(BaseModel):
    Nr_TUC: str
    UNID_AIS: str
    QTD_AIC_ANT: str
    QTD_ALM_ANT: str
    QTD_AIC_AT: str
    QTD_ALM_AT: str
    QTD_REF: str
    QTD_CMP: str
    QTD_TURN: str
    QTD_REAP: str
    QTD_INC: str
    QTD_DOA: str

    class Config:
        extra = 'forbid'
        
    @field_validator('Nr_TUC', mode = 'before')
    @classmethod
    def validar_cd(cls, value):
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'{value} não pertence ao domínio da variável.\n')
        return value
        
    @field_validator('UNID_AIS', mode = 'before')
    @classmethod
    def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
           
    @field_validator('QTD_AIC_ANT','QTD_ALM_ANT','QTD_AIC_AT','QTD_ALM_AT','QTD_REF','QTD_CMP',
                     'QTD_TURN','QTD_REAP','QTD_INC','QTD_DOA', mode = 'before')
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)

class TabelaORATINCR(BaseModel):
    tabela: List[TBLORATINCR]

class TBLLDSDS(BaseModel):
    Id_SEQ_SDS: str
    Cd_CC: str
    COD_CCUS: str
    VL_DEB: str
    VL_CRED: str
    VL_SLD_INI: str
    IND_DC_INI: str
    VL_SLD_FIN: str
    IND_DC_FIN: str
    DT_INI: str
    DT_FIN: str

    class Config:
        extra = 'forbid'
        
    @field_validator('Cd_CC', mode = 'before')
    @classmethod
    def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=9)
                    
    @field_validator('COD_CCUS', mode = 'before')
    @classmethod
    def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
 
    @field_validator('Id_SEQ_SDS', mode = 'before')
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
            
    @field_validator('IND_DC_INI','IND_DC_FIN', mode = 'before')
    @classmethod
    def validar_IND(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1, dominio=['C','D'])
   
    @field_validator('DT_INI','DT_FIN', mode = 'before')
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value, vazio=True)
           
    @field_validator('VL_DEB','VL_CRED','VL_SLD_INI','VL_SLD_FIN', mode = 'before')
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)
            
class TabelaLDSDS(BaseModel):
    tabela: List[TBLLDSDS]
        
        
class TBLLDLCTMO(BaseModel):
    Id_SEQ_LCMTO: str
    NUM_LCTO: str
    Dt_LCMTO: str
    VL_LCMTO: str
    IND_LCMTO: str

    class Config:
        extra = 'forbid'
        
    @field_validator('NUM_LCTO', mode = 'before')
    @classmethod
    def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50)
                           
    @field_validator('Id_SEQ_LCMTO', mode = 'before')
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
            
    @field_validator('IND_LCMTO', mode = 'before')
    @classmethod
    def validar_IND(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1, dominio=['N','E','X'])
   
    @field_validator('Dt_LCMTO', mode = 'before')
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
           
    @field_validator('VL_LCMTO', mode = 'before')
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)

class TabelaLDLCTMO(BaseModel):
    tabela: List[TBLLDLCTMO]
        
class TBLLDPTD(BaseModel):
    Id_SEQ_PTD: str
    NUM_LCTO: str
    Cd_CC: str
    COD_CCUS: str
    VL_DC: str
    IND_DC: str
    HIST: str

    class Config:
        extra = 'forbid'
        
    @field_validator('HIST', mode = 'before')
    @classmethod
    def validar_hist(cls, value, info):
        return validar_texto(value, info.field_name, max_len=65535)

    @field_validator('Cd_CC', mode = 'before')
    @classmethod
    def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=15)
                    
    @field_validator('COD_CCUS', mode = 'before')
    @classmethod
    def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
        
    @field_validator('NUM_LCTO', mode = 'before')
    @classmethod
    def validar_NUM(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50)
                           
    @field_validator('Id_SEQ_PTD', mode = 'before')
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
            
    @field_validator('IND_DC', mode = 'before')
    @classmethod
    def validar_IND(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1, dominio=['C','D'])
             
    @field_validator('VL_DC', mode = 'before')
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)

class TabelaLDPTD(BaseModel):
    tabela: List[TBLLDPTD]

class TBLDTenerg(BaseModel):
    Id_DT_ENERG: str
    Cd_Patrim: str
    Cd_DIG_INC: str
    Dt_Energ: str

    class Config:
        extra = 'forbid'
        
    @field_validator('Cd_Patrim','Cd_DIG_INC', mode = 'before')
    @classmethod
    def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
                    
    @field_validator('Id_DT_ENERG', mode = 'before')
    @classmethod
    def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
            
    @field_validator('Dt_Energ', mode = 'before')
    @classmethod
    def validar_Dt(cls, value):
        return validar_data(value)
            
class TabelaDTenerg(BaseModel):
    tabela: List[TBLDTenerg]

class ROS_ABT_AJST(BaseModel):
    Nr_TI: str
    Cd_SubODI: str
    Cd_NG: str
    TP_AJST: str
    VL_AJST: str

    class Config:
        extra = 'forbid'
        
    @field_validator('Nr_TI', mode="before")
    @classmethod
    def validar_TI(cls, value, info):
        if not ValoresTI.teste(int(value)):
            raise ValueError(f'O dado não é válido como TI.\n')
        return value
                    
    @field_validator('Cd_SubODI', mode = "before")
    @classmethod
    def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)
            
    @field_validator('Cd_NG', mode = "before")
    @classmethod
    def validar_vl_cdng(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=6)
    
    @field_validator('TP_AJST', mode = "before")
    @classmethod
    def validar_vl_tpajst(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=12)
    
    @field_validator('VL_AJST', mode = 'before')
    @classmethod
    def validar_vl(cls, value):
        return validar_decimal(value)
            
class TabelaRosAbtAjst(BaseModel):
    tabela: List[ROS_ABT_AJST]

class ROS_ABT_CP(BaseModel):
    Cd_ODI: str
    Cd_SubODI: str
    Nr_TI: str
    Nr_CM: str
    Nr_TUC: str
    Nr_A1: str
    Nr_A2: str
    Nr_A3: str
    Nr_A4: str
    Nr_A5: str
    Nr_A6: str
    txt_Desc_Bem: str
    Qtd_AIS: str
    Cd_UND_AIS: str
    Cd_UAR: str
    Cd_UC: str
    Cd_Patrim: str
    Cd_DIG_INC: str
    Dt_Imob: str
    VL_VOC_SAN: str
    TP_BASE: str
    Ide_AIS: str


    class Config:
        extra = 'forbid'

    @field_validator('Dt_Imob', mode="before")
    @classmethod
    def validar_datas(cls, value):
        return validar_data(value)
        
    @field_validator('VL_VOC_SAN', 'Qtd_AIS', mode="before")
    @classmethod
    def validar_vl_voc(cls, value):
        return validar_decimal(value, min_val=0)
    
    @field_validator("Nr_A1", "Nr_A2", "Nr_A3", "Nr_A4", "Nr_A5", "Nr_A6", mode="before")
    def valida_nr_ax(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99)
    
    @field_validator('Cd_DIG_INC', mode="before")
    @classmethod
    def validar_dig_inc(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
    
    @field_validator('Ide_AIS', mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
    
    @field_validator("txt_Desc_Bem", mode="before")
    def valida_textos(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
    
    @field_validator('Cd_UND_AIS', mode="before")
    @classmethod
    def validar_UND(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)

    @field_validator('Cd_UAR', mode="before")
    @classmethod
    def validar_UAR(cls, value, info):
        return validar_texto(value, info.field_name, max_len=3, dominio = ['UAR','TUC','UC'])
    
    @field_validator('Cd_UC','Cd_Patrim','Cd_ODI','Cd_SubODI', mode="before")
    @classmethod
    def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=25) 
                   
    @field_validator('Nr_TUC')
    @classmethod
    def validar_TUC(cls, value, info):
        num = validar_inteiro(value, info.field_name, min_val=99, max_val=999)
        if (num != None) and (num != '') and (not ValoresTUC.teste(int(value))):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return value
           
    @field_validator('Nr_TI')
    @classmethod
    def validar_TI(cls, value, info):
        num = validar_inteiro(value, info.field_name, min_val=1, max_val=100)
        if not ValoresTI.teste(int(value)):
           raise ValueError(f'O dado não é válido como TI.\n')
        return value
               
    @field_validator('TP_BASE', mode = "before")
    @classmethod
    def validar_vl_tpajst(cls, value, info):
        return validar_texto(value, info.field_name, max_len=3, dominio = ['BRR','BAR'])
    
    @model_validator(mode="wrap")
    @classmethod
    def silenciador_de_erros(cls, values: any, handler):
        try:
            return handler(values)
        except ValidationError as e:
            errors_list = e.errors()
            dados = values if isinstance(values, dict) else values.__dict__
            obj_com_erro = cls.model_construct(**dados)
            object.__setattr__(obj_com_erro, "_erros_registro", errors_list)
            return obj_com_erro
            
class TabelaRosAbtCP(BaseModel):
    tabela: List[ROS_ABT_CP]

    @model_validator(mode="after")
    def pipeline_validacao_completa(self):
        raw_data = self.tabela 
        erros_consolidados = []

        for i, obj in enumerate(raw_data):
            
            try:
                linha_id = getattr(obj, 'Ide_AIS', f'Linha_{i+1}')
            except:
                linha_id = f'Linha_{i+1}'

            if hasattr(obj, "_erros_registro") and obj._erros_registro:
                for err in obj._erros_registro:
                    if isinstance(err['loc'], str): 
                        loc_tuple = (err['loc'],)
                    else:
                        loc_tuple = tuple(err['loc'])
                    
                    err['loc'] = ('tabela', i+1) + loc_tuple
                    err['msg'] = f"[Estrutura] {err['msg']}"
                    
                    if err.get('type') not in ['value_error', 'type_error', 'missing', 'int_parsing', 'float_parsing']:
                        err['type'] = PydanticCustomError('value_error', err['msg'])  
                    erros_consolidados.append(err)

            v_ti  = getattr(obj, 'Nr_TI', None)
            v_tuc = getattr(obj, 'Nr_TUC', None)
            v_cc  = getattr(obj, 'Cd_CC', None)
            v_cm  = getattr(obj, 'Nr_CM', None)
            v_a1  = getattr(obj, 'Nr_A1', None)
            v_a2  = getattr(obj, 'Nr_A2', None)
            v_a3  = getattr(obj, 'Nr_A3', None)
            v_a4  = getattr(obj, 'Nr_A4', None)
            v_a5  = getattr(obj, 'Nr_A5', None)
            v_a6  = getattr(obj, 'Nr_A6', None)
            v_dt_IMB  = getattr(obj, 'Dt_Imob', None)
            v_UND = getattr(obj, 'Cd_UND_AIS', None)
            v_Cd_UAR = getattr(obj, 'Cd_UAR', None)
            v_QTD = getattr(obj, 'Qtd_AIS', None)

            def check(func, campo, *args):
                try:
                    func(*args)
                except Exception as e:
                    erros_consolidados.append({
                        "type": "value_error",
                        "loc": ("tabela", i+1, campo),
                        "msg": f"[Regra Negocio] [ID: {linha_id}] {str(e)}",
                        "input": getattr(obj, campo, "N/A"),
                        "ctx": {'error': ValueError(str(e))}
                    })

            try:
                check(validar_tuc_ti, "Nr_TUC", v_tuc, v_ti, linha_id, v_a1)
                check(validar_tucs_proibidos, "Nr_TUC", v_tuc, linha_id)
                check(validar_administracao, "Cd_CC", v_ti, v_cc, linha_id)
                check(validar_cm, "Nr_CM", v_ti, v_cm, linha_id)
                check(validar_ti_distribuicao, "Nr_TI", v_ti, linha_id)
                check(validar_cabos, "Nr_TUC", v_tuc, v_a1, v_a3, v_a4, v_a5, v_UND, linha_id)
                check(validar_torre_poste, "Nr_TI", v_ti, v_tuc, v_a1, linha_id)
                check(validar_bem_individual, "Nr_TUC", v_ti, v_tuc, v_a1, v_a2, v_a3, v_a4, v_a5, v_a6, v_QTD, linha_id, v_Cd_UAR)

            except Exception as e_critico:
                erros_consolidados.append({
                    "type": "value_error",
                    "loc": ("tabela", i+1),
                    "msg": f"[ERRO CRÍTICO] Falha na linha {linha_id}: {str(e_critico)}",
                    "input": {},
                    "ctx": {'error': ValueError(str(e_critico))}
                })
                continue

        if erros_consolidados:
            raise ValidationError.from_exception_data(self.__class__.__name__, erros_consolidados)
        return self
    
class MOP_FOPAG(BaseModel):
    Id_Ext_MOP_FOPAG: str
    COD_CCUS: str
    COD_CTA: str
    IND_FL: str
    Cd_Matricula: str
    Dsc_Cargo: str
    Cd_Depto: str
    Dt_CMPT: str
    Txt_Ativ_Exec: str
    Hr_Efetivas: str
    Hr_CAPEX: str
    Hr_OPEX: str
    Hr_ODD: str
    VL_FOPAG: str
    VL_FOPAG_CAPEX: str
    VL_FOPAG_OPEX: str
    VL_FOPAG_ODD: str
    Txt_Obs: str

    _erros_registro: list = PrivateAttr(default_factory=list)

    class Config:
        extra = "forbid"

    @field_validator("Dt_CMPT", mode="before")
    @classmethod
    def validar_datas(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=7)

    @field_validator(
                        "VL_FOPAG",
                        "VL_FOPAG_CAPEX",
                        "VL_FOPAG_OPEX",
                        "VL_FOPAG_ODD",
                        "Hr_Efetivas",
                        "Hr_CAPEX",
                        "Hr_OPEX",
                        "Hr_ODD",
                        mode="before",
                    )
    @classmethod
    def validar_valores_e_horas(cls, value):
        return validar_decimal(value, min_val=0)

    @field_validator("Id_Ext_MOP_FOPAG", mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)

    @field_validator("Txt_Ativ_Exec", mode="before")
    @classmethod
    def valida_txt_ativ_exec(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=2000)

    @field_validator("Txt_Obs", mode="before")
    @classmethod
    def valida_txt_obs(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=65000)

    @field_validator("Dsc_Cargo", mode="before")
    @classmethod
    def valida_dsc_cargo(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=255)

    @field_validator("Cd_Matricula", "COD_CTA", "Cd_Depto", mode="before")
    @classmethod
    def validar_campos_texto_25(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)

    @field_validator("COD_CCUS", mode="before")
    @classmethod
    def validar_cod_ccus(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)

    @field_validator("IND_FL")
    @classmethod
    def validar_ind_fl(cls, value, info):
        num = validar_inteiro(value, info.field_name, min_val=1, max_val=7)

        if num not in (None, "") and not ValoresTUC.teste(int(value)):
            raise ValueError("O dado não é válido como código de tipo de folha.")

        return value

    @model_validator(mode="wrap")
    @classmethod
    def silenciador_de_erros(cls, values: any, handler):
        try:
            return handler(values)
        except ValidationError as e:
            errors_list = e.errors()
            dados = values if isinstance(values, dict) else values.__dict__
            obj_com_erro = cls.model_construct(**dados)
            object.__setattr__(obj_com_erro, "_erros_registro", errors_list)
            return obj_com_erro


class TabelaMOP_FOPAG(BaseModel):
    tabela: List[MOP_FOPAG]

    @model_validator(mode="after")
    def erros(self):
        erros = []

        for i, obj in enumerate(self.tabela):
            linha_id = getattr(obj, "Id_Ext_MOP_FOPAG", f"Linha_{i+1}")
            for err in getattr(obj, "_erros_registro", []):
                loc = err.get("loc", ())
                if isinstance(loc, str):
                    loc = (loc,)

                erros.append({
                                **err,
                                "loc": ("tabela", i, *loc),
                                "msg": f"[Estrutura] [ID: {linha_id}] {err.get('msg')}",
                            })

            def erro(campo, msg):
                erros.append({
                                "type": "value_error",
                                "loc": ("tabela", i, campo),
                                "msg": f"[Regra Negócio] [ID: {linha_id}] {msg}",
                                "input": getattr(obj, campo, None),
                                "ctx": {"error": ValueError(msg)},
                            })

            def dec(campo):
                val = getattr(obj, campo, None)
                if val in (None, ""):
                    return None
                try:
                    return Decimal(str(val).replace(",", "."))
                except Exception:
                    return None

            def soma_igual(total, partes, nome):
                v_total = dec(total)
                v_partes = [dec(c) for c in partes]

                if v_total is None or any(v is None for v in v_partes):
                    return

                soma = sum(v_partes, Decimal("0"))
                tolerancia = abs(v_total) * Decimal("0.01")

                if abs(v_total - soma) > tolerancia:
                    erro(
                            total,
                            f"{nome} inconsistente. {total} deve ser igual à soma de "
                            f"{' + '.join(partes)}. Informado: {v_total}; calculado: {soma}."
                        )

            dt_cmpt = getattr(obj, "Dt_CMPT", None)
            if not isinstance(dt_cmpt, str) or not re.fullmatch(r"\d{4}/(0[1-9]|1[0-2])", dt_cmpt):
                erro(
                        "Dt_CMPT",
                        "Dt_CMPT deve estar no formato aaaa/mm, por exemplo 2024/06."
                    )

            campos_horas = ["Hr_Efetivas", "Hr_CAPEX", "Hr_OPEX", "Hr_ODD"]

            for campo in campos_horas:
                v = dec(campo)
                if v is not None and v < 0:
                    erro(campo, f"{campo} não pode conter valor negativo.")

            soma_igual(
                            "Hr_Efetivas",
                            ["Hr_CAPEX", "Hr_OPEX"],
                            "Horas efetivas"
                        )

            hr_odd = dec("Hr_ODD")
            hr_opex = dec("Hr_OPEX")

            if hr_odd is not None and hr_opex is not None and hr_odd > hr_opex:
                erro("Hr_ODD", "Hr_ODD deve ser menor ou igual a Hr_OPEX.")

            hr_efetivas = dec("Hr_Efetivas")

            if hr_efetivas is not None and hr_efetivas != Decimal("44"):
                erro(
                        "Hr_Efetivas",
                        "Hr_Efetivas, em tese, deve corresponder a 44 horas semanais, nos termos gerais da CLT. "
                        "Caso haja jornada diversa, deve ser apresentada convenção, acordo coletivo ou justificativa aplicável."
                    )

            campos_valores = [
                                "VL_FOPAG",
                                "VL_FOPAG_CAPEX",
                                "VL_FOPAG_OPEX",
                                "VL_FOPAG_ODD",
                            ]

            for campo in campos_valores:
                v = dec(campo)
                if v is not None and v < 0:
                    erro(campo, f"{campo} não pode conter valor negativo.")

            soma_igual(
                            "VL_FOPAG",
                            ["VL_FOPAG_CAPEX", "VL_FOPAG_OPEX"],
                            "Valor da folha"
                        )

            vl_odd = dec("VL_FOPAG_ODD")
            vl_opex = dec("VL_FOPAG_OPEX")

            if vl_odd is not None and vl_opex is not None and vl_odd > vl_opex:
                erro(
                        "VL_FOPAG_ODD",
                        "VL_FOPAG_ODD deve ser menor ou igual a VL_FOPAG_OPEX."
                    )

        if erros:
            raise ValidationError.from_exception_data(
                                                        self.__class__.__name__,
                                                        erros
                                                    )

        return self

class MOP_RUBR(BaseModel):
    Id_Ext_MOP_RUB: str
    Id_Ext_MOP_FOPAG: str
    COD_RUBRICA: str
    VL_RUBR: str
    IND_RUBR: str

    CODIGOS_RUBRICAS: ClassVar[set[str]]  = {
                    '1000','1001','1002','1003','1004','1005','1006','1007','1009','1010','1011','1020','1021',
                    '1022','1023','1024','1040','1041','1050','1080','1099','1201','1202','1203','1204','1205',
                    '1206','1207','1208','1209','1210','1211','1212','1213','1214','1215','1216','1217','1225',
                    '1230','1299','1300','1350','1351','1352','1401','1402','1403','1404','1405','1406','1407',
                    '1409','1410','1411','1412','1601','1602','1603','1604','1619','1620','1621','1623','1629',
                    '1650','1651','1652','1800','1801','1802','1805','1806','1807','1808','1809','1810','1899',
                    '1901','2501','2502','2510','2801','2901','2902','2903','2920','2930','2999','3501','3505',
                    '3506','3508','3509','3510','3511','3520','3525','4010','4011','4050','4051','5001','5005',
                    '5501','5504','5510','6000','6001','6002','6003','6004','6006','6007','6101','6102','6103',
                    '6104','6105','6106','6107','6108','6119','6129','6901','6904','7001','7002','7003','7004',
                    '7005','7006','7007','7008','9200','9201','9202','9203','9205','9207','9208','9209','9210',
                    '9211','9212','9213','9214','9216','9217','9218','9219','9220','9221','9222','9223','9224',
                    '9225','9226','9230','9231','9232','9233','9240','9241','9242','9243','9244','9250','9254',
                    '9255','9258','9260','9270','9290','9291','9292','9293','9294','9299','9901','9902','9903',
                    '9904','9905','9906','9907','9908','9910','9911','9930','9931','9932','9933','9938','9939',
                    '9950','9951','9989'
                    }

    _erros_registro: list = PrivateAttr(default_factory=list)

    class Config:
        extra = "forbid"

    @field_validator("VL_RUBR", mode="before")
    @classmethod
    def validar_vl_rubr(cls, value):
        return validar_decimal(value, min_val=0)

    @field_validator("Id_Ext_MOP_FOPAG", "Id_Ext_MOP_RUB", mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)

    @field_validator("COD_RUBRICA", mode="before")
    @classmethod
    def validar_cod_rubrica(cls, value, info):
        return validar_lista(value, cls.CODIGOS_RUBRICAS, info.field_name, vazio=False)

    @field_validator("IND_RUBR", mode="before")
    @classmethod
    def validar_ind_rubr(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)

    @model_validator(mode="wrap")
    @classmethod
    def silenciador_de_erros(cls, values: any, handler):
        try:
            return handler(values)
        except ValidationError as e:
            dados = values if isinstance(values, dict) else values.__dict__
            obj_com_erro = cls.model_construct(**dados)
            object.__setattr__(obj_com_erro, "_erros_registro", e.errors())
            return obj_com_erro

class TabelaMOP_RUBR(BaseModel):
    tabela: List[MOP_RUBR]

    @model_validator(mode="after")
    def validar_tabela(self):
        erros = []

        for i, obj in enumerate(self.tabela):
            linha_id = getattr(obj, "Id_Ext_MOP_RUB", f"Linha_{i+1}")

            for err in getattr(obj, "_erros_registro", []):
                loc = err.get("loc", ())
                if isinstance(loc, str):
                    loc = (loc,)

                erros.append({
                    **err,
                    "loc": ("tabela", i, *loc),
                    "msg": f"[Estrutura] [ID: {linha_id}] {err.get('msg')}",
                })

        if erros:
            raise ValidationError.from_exception_data(
                self.__class__.__name__,
                erros
            )

        return self
    
class MOP_SERV(BaseModel):
    Id_Ext_MOP_ITEM: str
    Id_Ext_MOP_FOPAG: str
    IND_CAPEX: str
    CD_Nm_Reg_ST: str
    Qtd_ST: str

    CODIGOS_ST: ClassVar[set[str]]  = {str(n) for n in range(0,34)}

    _erros_registro: list = PrivateAttr(default_factory=list)

    class Config:
        extra = "forbid"

    @field_validator("Qtd_ST", mode="before")
    @classmethod
    def validar_vl_rubr(cls, value):
        return validar_decimal(value, min_val=0)

    @field_validator("Id_Ext_MOP_FOPAG", "Id_Ext_MOP_ITEM", mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)

    @field_validator("CD_Nm_Reg_ST", mode="before")
    @classmethod
    def validar_cod_rubrica(cls, value, info):
        return validar_lista(value, cls.CODIGOS_ST, info.field_name, vazio=False)

    @field_validator("IND_CAPEX", mode="before")
    @classmethod
    def validar_ind_rubr(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)

    @model_validator(mode="wrap")
    @classmethod
    def silenciador_de_erros(cls, values: any, handler):
        try:
            return handler(values)
        except ValidationError as e:
            dados = values if isinstance(values, dict) else values.__dict__
            obj_com_erro = cls.model_construct(**dados)
            object.__setattr__(obj_com_erro, "_erros_registro", e.errors())
            return obj_com_erro


class TabelaMOP_SERV(BaseModel):
    tabela: List[MOP_SERV]

    @model_validator(mode="after")
    def validar_tabela(self):
        erros = []

        for i, obj in enumerate(self.tabela):
            linha_id = getattr(obj, "Id_Ext_MOP_ITEM", f"Linha_{i+1}")

            for err in getattr(obj, "_erros_registro", []):
                loc = err.get("loc", ())
                if isinstance(loc, str):
                    loc = (loc,)

                erros.append({
                    **err,
                    "loc": ("tabela", i, *loc),
                    "msg": f"[Estrutura] [ID: {linha_id}] {err.get('msg')}",
                })

        if erros:
            raise ValidationError.from_exception_data(
                self.__class__.__name__,
                erros
            )

        return self
    
class ST_AB(BaseModel):
    Id_Ext_SRV_ABT: str
    Nr_NF: str
    Nr_SerieNF: str
    Dt_NF: str
    Cd_ODI: str
    Cd_SubODI: str
    Cd_ODD: str
    Pct_SubODI: str
    Pct_ODD: str
    TP_ALOC: str

    _erros_registro: list = PrivateAttr(default_factory=list)

    class Config:
        extra = "forbid"

    @field_validator('Dt_NF', mode="before")
    @classmethod
    def validar_datas(cls, value):
        return validar_data(value)

    @field_validator("Pct_SubODI", "Pct_ODD", mode="before")
    @classmethod
    def validar_vl_rubr(cls, value):
        return validar_decimal(value, min_val=0, max_val=1)

    @field_validator("Id_Ext_SRV_ABT", mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)

    @field_validator("TP_ALOC", mode="before")
    @classmethod
    def validar_cod_rubrica(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)

    @field_validator("Cd_ODI", "Cd_ODD", mode="before")
    @classmethod
    def validar_ind_rubr(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
    
    @field_validator("Nr_NF", mode="before")
    @classmethod
    def validar_text(cls, value, info):
        return validar_texto(value, info.field_name, max_len=20)
    
    @field_validator("Nr_SerieNF", mode="before")
    @classmethod
    def validar_text1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
    
    @field_validator("Cd_SubODI", mode="before")
    @classmethod
    def validar_text2(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)

    @model_validator(mode="wrap")
    @classmethod
    def silenciador_de_erros(cls, values: any, handler):
        try:
            return handler(values)
        except ValidationError as e:
            dados = values if isinstance(values, dict) else values.__dict__
            obj_com_erro = cls.model_construct(**dados)
            object.__setattr__(obj_com_erro, "_erros_registro", e.errors())
            return obj_com_erro


class TabelaST_AB(BaseModel):
    tabela: List[ST_AB]

    @model_validator(mode="after")
    def validar_tabela(self):
        erros = []

        for i, obj in enumerate(self.tabela):
            linha_id = getattr(obj, "Id_Ext_MOP_ITEM", f"Linha_{i+1}")

            for err in getattr(obj, "_erros_registro", []):
                loc = err.get("loc", ())
                if isinstance(loc, str):
                    loc = (loc,)

                erros.append({
                    **err,
                    "loc": ("tabela", i, *loc),
                    "msg": f"[Estrutura] [ID: {linha_id}] {err.get('msg')}",
                })

        if erros:
            raise ValidationError.from_exception_data(
                self.__class__.__name__,
                erros
            )

        return self
    
class ST_FP(BaseModel):
    Id_BS_FP: str
    Nr_Parcela: str
    VL_Parcela: str
    Dt_PMTO: str
    Txt_OBS: str
    Id_Ext_SRV: str
    Nr_DOC_COMP: str

    _erros_registro: list = PrivateAttr(default_factory=list)

    class Config:
        extra = "forbid"

    @field_validator('Dt_PMTO', mode="before")
    @classmethod
    def validar_datas(cls, value):
        return validar_data(value)

    @field_validator("VL_Parcela", mode="before")
    @classmethod
    def validar_vl_rubr(cls, value):
        return validar_decimal(value, min_val=0, max_val=1)

    @field_validator("Id_BS_FP", "Id_Ext_SRV", "Nr_Parcela", mode="before")
    @classmethod
    def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)

    @field_validator("Txt_OBS", mode="before")
    @classmethod
    def validar_cod_rubrica(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=255)

    @field_validator("Nr_DOC_COMP", mode="before")
    @classmethod
    def validar_ind_rubr(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)

    @model_validator(mode="wrap")
    @classmethod
    def silenciador_de_erros(cls, values: any, handler):
        try:
            return handler(values)
        except ValidationError as e:
            dados = values if isinstance(values, dict) else values.__dict__
            obj_com_erro = cls.model_construct(**dados)
            object.__setattr__(obj_com_erro, "_erros_registro", e.errors())
            return obj_com_erro


class TabelaST_FP(BaseModel):
    tabela: List[ST_FP]

    @model_validator(mode="after")
    def validar_tabela(self):
        erros = []

        for i, obj in enumerate(self.tabela):
            linha_id = getattr(obj, "Id_Ext_MOP_ITEM", f"Linha_{i+1}")

            for err in getattr(obj, "_erros_registro", []):
                loc = err.get("loc", ())
                if isinstance(loc, str):
                    loc = (loc,)

                erros.append({
                    **err,
                    "loc": ("tabela", i, *loc),
                    "msg": f"[Estrutura] [ID: {linha_id}] {err.get('msg')}",
                })

        if erros:
            raise ValidationError.from_exception_data(
                self.__class__.__name__,
                erros
            )

        return self
    
def ler_dados_csv(nome_arquivo, tam_lote = 50000, nr_lote = 1):
    tabela = []
    df_PRheader = pd.read_csv(nome_arquivo, sep="|", header = None,
                        encoding="latin-1", 
                        nrows = 2,
                        dtype = str )
    if len(df_PRheader)>1:
        try:
            df_PR = pd.read_csv(nome_arquivo, sep="|", header = None, 
                                encoding = "latin-1", 
                                skiprows = 1 + tam_lote * (nr_lote - 1), 
                                nrows = tam_lote,
                                dtype = str ,
                                keep_default_na=False)
        except Exception as e:
            if isinstance(e, pd.errors.EmptyDataError):
                st.warning(f"Problemas em {nome_arquivo}, não tem linhas (vazio), começando em {max((tam_lote + 1) * (nr_lote - 1), 1)}, mais {tam_lote} linhas.")
                df_PR = df_PRheader
                tam_reader = 0
                return tabela, tam_reader
            st.write(e)
            raise UserWarning(f"Problemas em {nome_arquivo}, começando em {max((tam_lote + 1) * (nr_lote - 1), 1)}, mais {tam_lote} linhas.")

        df_PR.columns = df_PRheader.iloc[0].tolist()
        tabela.append(df_PR.to_dict(orient='records'))
        tam_reader = len(df_PR)
    else:
        df_PR = df_PRheader
        tam_reader = 0
    return tabela, tam_reader

def validar_lote(dados_lote, tipo, p=None):
    erros = []
    try:
        if tipo in ['AIS', 'AISant', 'AISat']:
            TabelaAIS(**dados_lote)
        elif tipo in ['MOP']:
            TabelaMOP_FOPAG(**dados_lote)
        elif tipo in ['MOP_RUBRICAS']:
            TabelaMOP_RUBR(**dados_lote)
        elif tipo in ['MOP_SERVICOS']:
            TabelaMOP_SERV(**dados_lote)
        elif tipo in ['BS_ABT']:
            TabelaST_AB(**dados_lote)
        elif tipo in ['BS_FP']:
            TabelaST_FP(**dados_lote)
        elif tipo=='ROS':
            TabelaROS(**dados_lote)
        elif tipo=='DSC_CLS_CUSTO':
            TabelaDSCCLS(**dados_lote)
        elif tipo=='LST_FCUM':    
            TabelaLSTFCUM(**dados_lote)
        elif tipo=='LST_MAT':
            TabelaLSTMAT(**dados_lote)
        elif tipo=='LST_SERV':
            TabelaLSTSER(**dados_lote)
        elif tipo=='ROA':
            TabelaROA(**dados_lote)
        elif tipo=='ROD':
            TabelaROD(**dados_lote)
        elif tipo=='COMERCIAL_MEDIDORES':
            TabelaMed(**dados_lote)
        elif tipo=='NT_COM':
            TabelaNTcom(**dados_lote)
        elif tipo=='NT_CMU':
            TabelaNTcmu(**dados_lote)
        elif tipo=='OE_MOV':
            TabelaOEmov(**dados_lote)
        elif tipo=='OE_AMO':
            TabelaOEamt(**dados_lote)
        elif tipo == 'OE_SDINIC':
            TabelaOEsldini(**dados_lote)
        elif tipo == 'OE_REAV':
            TabelaOEreav(**dados_lote)
        elif tipo == 'OE_PLPTMOV':
            TabelaOEplptmov(**dados_lote)
        elif tipo == 'OE_PLPTAMO':
            TabelaOEplptamt(**dados_lote)
        elif tipo == 'OE_IRMOV':
            TabelaOEirmov(**dados_lote)
        elif tipo == 'OE_IRAMO':
            TabelaOEiramt(**dados_lote)
        elif tipo == 'OE_CCCMOV':
            TabelaOEcccmov(**dados_lote)
        elif tipo == 'OE_CCCAMO':
            TabelaOEcccamt(**dados_lote)
        elif tipo == 'OE_AJS':
            TabelaOEajt(**dados_lote)
        elif tipo == 'BP_EC':
            TabelaBPec(**dados_lote)
        elif tipo == 'BPFP_UAR':
            TabelaBPfpuar(**dados_lote)
        elif tipo == 'BP_UAR':
            TabelaBPuar(**dados_lote)
        elif tipo == 'REFORMADOS_INCREMENTAL':
            TabelaReform(**dados_lote)
        elif tipo == 'MUDANCA_PATRIMONIO':
            TabelaMp(**dados_lote)
        elif tipo == 'BAIXAS':
            TabelaBaixas(**dados_lote)
        elif tipo == 'DESC_ODI':
            TabelaDescODI(**dados_lote)
        elif tipo == 'PPBB':
            TabelaPPBB(**dados_lote)
        elif tipo == 'PCBB':
            TabelaPCBB(**dados_lote)
        elif tipo == 'INCR':
            TabelaINCR(**dados_lote)
        elif tipo == 'AO':
            TabelaAO(**dados_lote)
        elif tipo == 'ECDdepara':
            TabelaECD(**dados_lote)
        elif tipo == 'TDOMUC':
            TabelaTDOMUC(**dados_lote)
        elif tipo == 'LST_OBRAS_EMERG':
            TabelaLSTOBREMG(**dados_lote)
        elif tipo == 'LST_MAT_OBRAS_EMERG':
            TabelaLSTMATEMG(**dados_lote)
        elif tipo == 'ORIGEM_ATIVOS_INCREMENTAL':
            TabelaORATINCR(**dados_lote)
        elif tipo == 'LD_SALDO':
            TabelaLDSDS(**dados_lote)
        elif tipo == 'LD_LCMTO':
            TabelaLDLCTMO(**dados_lote)
        elif tipo == 'LD_PTD':
            TabelaLDPTD(**dados_lote)
        elif tipo == 'ROS_VAL':
            TabelaROSV(**dados_lote)
        elif tipo =='CD_SUBODI_AIS_ROS':
            TabelaCDSUBODIAIS(**dados_lote)
        elif tipo == 'COM_CA_BPC':
            TabelaCOMCABPC(**dados_lote)
        elif tipo == 'DT_ENERG':
            TabelaDTenerg(**dados_lote)
        elif tipo == 'OE_AGR':
            TabelaOEagr(**dados_lote)
        elif tipo == 'BS':
            Tabelabcserv(**dados_lote)
        elif tipo in ['ROAaicAT', 'ROAaicANT']:
            TabelaROA(**dados_lote)
        elif tipo in ['ROSaicAT', 'ROSaicANT']:
            TabelaROS(**dados_lote)
        elif tipo == 'ROS_ABT_AJST':
            TabelaRosAbtAjst(**dados_lote)
        elif tipo == 'ROS_ABT_CP':
            TabelaRosAbtCP(**dados_lote)
        elif tipo in ['ROAserv', 'RAserv']:
            TabelaRAs(**dados_lote)
        elif tipo in ['ROServ', 'RServ']:
            TabelaROServ(**dados_lote)
        else:
            return [f'Tabela {tipo} não modelada!']
    except ValidationError as e:
        for k in e.errors():
            k['etapa']=p
            erros.append(k)
    
    return erros

def validar_tabela_em_lotes_or(dados, tamanho_lote=100, tipo='', deslocamento=0):
    erros = []
    tabela = dados
    max_val = len(dados)
    a = st.progress(0,f"Rodando validação do {tipo}, 0/{max_val}.")
    for p in range(0, len(dados), tamanho_lote):
        a.progress(int((p / max_val) * 100), f"Rodando validação do {tipo}, {p}/{max_val}.")
        lote = {'tabela': tabela[p : (p + tamanho_lote)]}
        saida = validar_lote(lote, tipo, p)
        st.write(saida)
        erros.extend(validar_lote(lote, tipo, p))
    a.empty()
    return erros

def validar_tabela_em_lotes(dados, tamanho_lote_inicial=300, tipo='', deslocamento=0):
    erros = []
    tabela = dados
    max_val = len(dados)
    a = st.progress(0,f"Rodando validação do {tipo}, 0/{max_val}.")

    pos = 0
    tamanho_lote = tamanho_lote_inicial
    tamanho_min = 5
    tamanho_max = 2000
    alvo_segundos = 0.30
    fator_up = 1.25
    fator_down = 0.70
    pos = 0

    try:
        while pos < max_val:
            a.progress(int((pos / max_val) * 100), f"Rodando validação do {tipo}, {pos}/{max_val}. Passo otimizado: {tamanho_lote}.")
            lote_fim = min(pos + tamanho_lote, max_val)
            lote = {'tabela': tabela[pos:lote_fim]}
            inicio = time.time()
        
            erros.extend(validar_lote(lote, tipo, p = deslocamento + pos))
            
            duracao = time.time() - inicio
            
            if duracao < alvo_segundos * 0.7:
                tamanho_lote = int(min(tamanho_lote * fator_up, tamanho_max))
            elif duracao > alvo_segundos * 1.3:
                tamanho_lote = int(max(tamanho_lote * fator_down, tamanho_min))

            pos = lote_fim

            time.sleep(0.001)
    except Exception as e:
        st.write(f"Problema em {tipo}, {pos}. Mensagem {e}")
        st.write(lote)
        raise
    finally:
        a.empty()
    return erros

def anl_erro(erros, df_IMPR, tabela, tipo_erro = ['Erro de dependência, validação cruzada de campos.']):
    if len(erros)>0:
        for erro in erros:
            try:
                if erro['msg'] not in tipo_erro:
                    if erro['msg'].find('Duplicidade') < 0:
                        tipo_erro += [erro['msg']]
                    elif 'Duplicidade de ocorrência.' not in tipo_erro:
                        tipo_erro += ['Duplicidade de ocorrência.']
                if erro['type'] == 'missing':
                    a = f"Falta o campo: {erro['loc'][2]}."
                    if len(df_IMPR[df_IMPR['Erro'] == a]) != 0:
                        a = ""
                elif erro['type'] == 'extra_forbidden':
                    a = f"Campo adicional: {erro['loc'][2]}."
                    if len(df_IMPR[df_IMPR['Erro'] == a]) != 0:
                        a = ""
                elif erro['msg'].find('Duplicidade') >= 0:
                    a = 'Duplicidade de ocorrência.'
                else:
                    try:
                        linha = erro['loc'][1] + 2 + erro['etapa']
                        a = f"No campo {erro['loc'][2]}, linha {linha}, o valor está como {'vazio' if erro['input']=='' else erro['input']}, isso provoca erro.\n"
                    except:
                        a = "Sem detalhe"
                if a != "":
                    if a != "Sem detalhe":
                        if a == 'Duplicidade de ocorrência.':
                            pr = {'Erro' : [erro['msg']],
                                  'Tipo' : [a],
                                  'Tabela' : [tabela]}
                        else:
                            pr = {'Erro' : [a],
                                  'Tipo' : [erro['msg']],
                                  'Tabela' : [tabela]}
                    else:
                        pr = {'Erro' : [erro['msg']],
                              'Tipo' : ['Erro de dependência, validação cruzada de campos.'],
                              'Tabela' : [tabela]}
                    if len(df_IMPR)==0:
                        df_IMPR = pd.DataFrame(pr)
                    else:
                        df_IMPR = pd.concat([df_IMPR, pd.DataFrame(pr)], ignore_index=True)
            except:
                if 'Estrutura não modelada no validador' not in tipo_erro:
                    tipo_erro += ['Estrutura não modelada no validador']
                pr = {'Erro' : [f'Tabela {tabela} não modelada para validação.'],
                      'Tipo' : ['Estrutura não modelada no validador'],
                      'Tabela' : [tabela]}
                if len(df_IMPR)==0:
                    df_IMPR = pd.DataFrame(pr)
                else:
                    df_IMPR = pd.concat([df_IMPR, pd.DataFrame(pr)], ignore_index=True)
                
    return df_IMPR, tipo_erro

def limpar_texto_latin1(s):
    if isinstance(s, str):
        return s.encode("latin-1", errors="replace").decode("latin-1")
    return s

def gerar_relatorio_erros(lista_erros, nm_TBL="", tam_lote=1):
    agrupamento = {}

    regex_tags = re.compile(r"\[.*?\]")
    regex_linha = re.compile(
                                r"(?i)(linha|index|id)\s*[:_#-]?\s*\d+"
                            )
    regex_id = re.compile(
                            r"\[ID:\s*(.*?)\]",
                            flags=re.IGNORECASE
                        )

    with st.spinner(
                        f"Em progresso a consolidação dos erros do {nm_TBL}"
                    ):
        for erro in lista_erros:

            if isinstance(erro, dict):
                loc = erro.get("loc", ())
                msg_original = str(erro.get("msg", ""))
                etapa = erro.get("etapa", 0)
                tipo = erro.get("type", "")
                severidade = erro.get("severidade", "ERRO")
            else:
                loc = ()
                msg_original = str(erro)
                etapa = 0
                tipo = ""
                severidade = "ERRO"

            if not isinstance(loc, (tuple, list)):
                loc = ()

            indice_lote = next(
                                    (
                                        parte
                                        for parte in loc
                                        if isinstance(parte, int)
                                        and not isinstance(parte, bool)
                                    ),
                                    None
                                )


            if (
                    len(loc) >= 3
                    and isinstance(loc[-1], str)
                ):
                campo = loc[-1]

            elif tipo in ("missing", "extra_forbidden") and loc:
                campo = str(loc[-1])

            elif indice_lote is not None:
                campo = "Geral da Linha"

            else:
                campo = "Desconhecido"

            if indice_lote is not None:
                try:
                    index_linha = (
                        int(etapa or 0)
                        + indice_lote
                        + 2
                    )
                except (ValueError, TypeError):
                    index_linha = "?"
            else:
                index_linha = "?"

            if isinstance(erro, dict) and erro.get("nivel_agregacao"):
                id_exemplo = "Agregado"
            else:
                match_id = regex_id.search(msg_original)

                if match_id:
                    id_exemplo = match_id.group(1)
                else:
                    id_exemplo = str(index_linha)

            msg_limpa = regex_tags.sub("", msg_original)
            msg_limpa = regex_linha.sub("", msg_limpa)
            msg_limpa = re.sub(
                                    r"\s+",
                                    " ",
                                    msg_limpa
                                ).strip()

            if not msg_limpa:
                msg_limpa = "Erro não especificado"

            chave = (severidade, campo, msg_limpa)

            if chave not in agrupamento:
                agrupamento[chave] = {
                                        "Campo": campo,
                                        "Severidade": severidade,
                                        "Erro Padrão": msg_limpa,
                                        "Qtd": 0,
                                        "Exemplos": []
                                    }

            grupo = agrupamento[chave]
            grupo["Qtd"] += 1

            if (
                    len(grupo["Exemplos"]) < 10
                    and str(id_exemplo) not in grupo["Exemplos"]
                ):
                grupo["Exemplos"].append(str(id_exemplo))

    colunas = [
                    "Campo",
                    "Severidade",
                    "Descrição do Erro",
                    "Qtd",
                    "Exemplos (Amostra, linha do arquivo)",
                    "Nm_TAB"
                ]

    dados_finais = [
                        {
                            "Campo": grupo["Campo"],
                            "Severidade": grupo["Severidade"],
                            "Descrição do Erro": grupo["Erro Padrão"],
                            "Qtd": grupo["Qtd"],
                            "Exemplos (Amostra, linha do arquivo)": ", ".join(
                                grupo["Exemplos"]
                            ),
                            "Nm_TAB": nm_TBL
                        }
                        for grupo in agrupamento.values()
                    ]

    df = pd.DataFrame(dados_finais, columns=colunas)

    if not df.empty:
        df = df.sort_values(
                                by="Qtd",
                                ascending=False
                            ).reset_index(drop=True)

    return df