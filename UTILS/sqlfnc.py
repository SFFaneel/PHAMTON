import pandas as pd
import duckdb, tempfile
import sqlite3 as sl
import os, json
from dbfread import DBF
import streamlit as st
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import shutil
from pathlib import Path
from contextlib import nullcontext
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import DML, Keyword

def colunas_tabela(con, tabela):
    modulo = type(con).__module__

    if modulo.startswith("sqlite3"):
        resultado = con.execute(
                                    f'PRAGMA table_info("{tabela}")'
                                ).fetchall()
        return [col[1] for col in resultado]

    elif modulo.startswith("_duckdb") or modulo.startswith("duckdb"):
        resultado = con.execute(
                                    f'DESCRIBE "{tabela}"'
                                ).fetchall()

        return [col[0] for col in resultado]

    else:
        raise TypeError(
                            f"Tipo de conexão não suportado: {type(con)}"
                        )

def colunas_sel(sql):
    stmt = sqlparse.parse(sql)[0]
    cols = []
    lendo = False

    for token in stmt.tokens:
        if token.ttype is DML and token.value.upper() == "SELECT":
            lendo = True
            continue

        if lendo:
            if token.ttype is Keyword and token.value.upper() == "FROM":
                break

            if isinstance(token, IdentifierList):
                for item in token.get_identifiers():
                    cols.append(item.get_alias() or item.get_real_name())

            elif isinstance(token, Identifier):
                cols.append(token.get_alias() or token.get_real_name())

    return cols

def sanear_csv_mod(
                    diretorio: str,
                    arq: str,
                    st=None
                  ):
    origem = Path(diretorio) / arq
    dir_original = Path(diretorio) / "csv_ori"
    dir_rejeitado = Path(diretorio) / "csv_rej"

    if not origem.exists():
        return {
                    "status": "erro",
                    "motivo": "arquivo não encontrado",
                    "arquivo": arq,
                    "linhas_totais": 0,
                    "linhas_alteradas": 0,
                }

    log_path = dir_original / "processados.json"
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            log = json.load(f)
    else:
        log = {}

    if arq in log:
        return {
                    "status": "saneado",
                    "motivo": "arquivo processado",
                    "arquivo": arq,
                    "linhas_totais": log[arq]["linhas_totais"],
                    "linhas_alteradas": log[arq]["linhas_alteradas"]
                }

    dir_original.mkdir(parents=True, exist_ok=True)
    dir_rejeitado.mkdir(parents=True, exist_ok=True)

    original_backup = dir_original / arq
    rejeitado_path = dir_rejeitado / arq.replace(".csv", "_alteradas.txt")

    if original_backup.exists():
        return {
                    "status": "ignorado",
                    "motivo": "arquivo já saneado anteriormente",
                    "arquivo": arq,
                    "linhas_totais": None,
                    "linhas_alteradas": None
                }

    proibidos = (
                    ["\x00",  "\u01fc", "\ufeff", "\ufffd", '"', '\r'] +
                    [chr(i) for i in range(1, 9)] +
                    [chr(11), chr(12), chr(14), chr(15)]
                )

    tabela_remocao = {ord(ch): None for ch in proibidos}

    def limpar_linha(linha_bytes: bytes) -> tuple[str, bool]:
        conteudo_original = linha_bytes.rstrip(b"\r\n")
        texto_decodificado = conteudo_original.decode(
                                                        "utf-8",
                                                        errors="ignore",
                                                     )

        texto_limpo = texto_decodificado.translate(
                                                        tabela_remocao
                                                    )

        bytes_limpos = texto_limpo.encode("utf-8")
        foi_alterada = bytes_limpos != conteudo_original

        return texto_limpo, foi_alterada

    total_linhas = 0
    linhas_alteradas = 0
    total_bytes = origem.stat().st_size if origem.exists() else 0
    bytes_lidos = 0

    spinner_ctx = st.spinner(f"Saneando arquivo {arq}") if st else nullcontext()
    with spinner_ctx:
        if st:
            progresso = st.progress(0, text=f"Processando {arq}...")
            status = st.empty()
        else:
            progresso = None
            status = None

        tam_arq = os.path.getsize(origem) / (1024 * 1024)
        if tam_arq < 100:
            shutil.copy2(origem, original_backup)

        fd, tmp_path_str = tempfile.mkstemp(dir=diretorio, suffix=".tmp")
        os.close(fd)
        tmp_path = Path(tmp_path_str)

        try:
            with open(origem, "rb") as fin, \
                 open(tmp_path, "wb") as fout, \
                 open(rejeitado_path, "w", encoding="utf-8", newline="\n") as frej:

                for numero_linha, linha_bytes in enumerate(
                                                                fin,
                                                                start=1,
                                                            ):
                    total_linhas += 1
                    bytes_lidos += len(linha_bytes)

                    linha_limpa, foi_alterada = limpar_linha(
                                                                linha_bytes
                                                            )

                    if foi_alterada:
                        linhas_alteradas += 1
                        original_legivel = linha_bytes.rstrip(
                                                                    b"\r\n"
                                                                ).decode(
                                                                    "utf-8",
                                                                    errors="backslashreplace",
                                                                )

                        frej.write(
                                        f"Linha {numero_linha}: "
                                        f"{original_legivel}\n"
                                    )

                    fout.write(
                                    linha_limpa.encode("utf-8") + b"\n"
                                )

                    if (
                            st
                            and total_bytes > 0
                            and numero_linha % 5000 == 0
                        ):
                        percentual = min(
                                            bytes_lidos / total_bytes,
                                            1.0,
                                        )

                        progresso.progress(
                                                percentual,
                                                text=(
                                                    f"Processando {arq}... "
                                                    f"{total_linhas:,} linhas"
                                                ).replace(",", "."),
                                            )

                        status.text(
                                        (
                                            f"Lidas: {total_linhas:,} | "
                                            f"Alteradas: {linhas_alteradas:,}"
                                        ).replace(",", ".")
                                    )


            os.replace(tmp_path, origem)

            if (
                    linhas_alteradas == 0
                    and rejeitado_path.exists()
                ):
                rejeitado_path.unlink()

            log[arq] = {
                            "data_processamento": datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "tamanho_bytes": origem.stat().st_size,
                            "nome": arq,
                            "codificacao_saida": "utf-8",
                            "linhas_totais": total_linhas,
                            "linhas_alteradas": linhas_alteradas,
                        }

            # O log precisa ser atualizado mesmo sem Streamlit.
            with open(
                        log_path,
                        "w",
                        encoding="utf-8",
                    ) as f:
                json.dump(
                            log,
                            f,
                            indent=4,
                            ensure_ascii=False,
                        )

            if st:
                progresso.empty()
                status.text(
                                (
                                    f"Finalizado {arq} | "
                                    f"Lidas: {total_linhas:,} | "
                                    f"Alteradas: {linhas_alteradas:,}"
                                ).replace(",", ".")
                            )

        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()

            if st:
                progresso.empty()
                status.empty()

            raise

    return {
                "status": "saneado",
                "motivo": "arquivo processado",
                "arquivo": arq,
                "linhas_totais": total_linhas,
                "linhas_alteradas": linhas_alteradas
            }

def sanear_csv(
                    diretorio: str,
                    arq: str,
                    encoding: str = "windows-1252",
                    st=None
                ):
    origem = Path(diretorio) / arq
    dir_original = Path(diretorio) / "csv_ori"
    dir_rejeitado = Path(diretorio) / "csv_rej"

    log_path = dir_original / "processados.json"
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            log = json.load(f)
    else:
        log = {}

    if arq in log:
        return {
                    "status": "saneado",
                    "motivo": "arquivo processado",
                    "arquivo": arq,
                    "linhas_totais": log[arq]["linhas_totais"],
                    "linhas_alteradas": log[arq]["linhas_alteradas"]
                }

    dir_original.mkdir(parents=True, exist_ok=True)
    dir_rejeitado.mkdir(parents=True, exist_ok=True)

    original_backup = dir_original / arq
    rejeitado_path = dir_rejeitado / arq.replace(".csv", "_alteradas.txt")

    if original_backup.exists():
        return {
                    "status": "ignorado",
                    "motivo": "arquivo já saneado anteriormente",
                    "arquivo": arq,
                    "linhas_totais": None,
                    "linhas_alteradas": None
                }

    proibidos = (
                    ["\x00", "\xC7", "\xC3", "\u01fc", "\ufeff", "\ufffd", '"', '\r'] +
                    [chr(i) for i in range(0xC1, 0xCA)] +
                    [chr(i) for i in range(1, 9)] +
                    [chr(11), chr(12), chr(14), chr(15)]
                )

    tabela_remocao = {ord(ch): None for ch in proibidos}

    def limpar_linha(linha: str) -> str:
        linha = linha.translate(tabela_remocao)
        return "".join(c for c in linha if ord(c) <= 255)

    total_linhas = 0
    linhas_alteradas = 0

    total_bytes = origem.stat().st_size if origem.exists() else 0
    bytes_lidos = 0

    spinner_ctx = st.spinner(f"Saneando arquivo {arq}") if st else nullcontext()
    with spinner_ctx:
        if st:
            progresso = st.progress(0, text=f"Processando {arq}...")
            status = st.empty()
        else:
            progresso = None
            status = None

        tam_arq = os.path.getsize(origem) / (1024 * 1024)
        if tam_arq < 100:
            shutil.copy2(origem, original_backup)

        fd, tmp_path = tempfile.mkstemp(dir=diretorio, suffix=".tmp")
        os.close(fd)

        try:
            with open(origem, "r", encoding=encoding, errors="replace", newline="") as fin, \
                 open(tmp_path, "w", encoding=encoding, newline="") as fout, \
                 open(rejeitado_path, "w", encoding="utf-8", newline="") as frej:

                for i, linha in enumerate(fin, start=1):
                    total_linhas += 1
                    bytes_lidos += len(linha.encode(encoding, errors="replace"))

                    linha_original = linha.rstrip("\r\n")
                    linha_limpa = limpar_linha(linha_original)

                    if linha_limpa != linha_original:
                        linhas_alteradas += 1
                        frej.write(linha_original + "\n")

                    fout.write(linha_limpa + "\n")

                    if st and total_bytes > 0 and (i % 5000 == 0):
                        pct = min(bytes_lidos / total_bytes, 1.0)
                        progresso.progress(
                            pct,
                            text=f"Processando {arq}... {total_linhas:,} linhas".replace(",",".")
                        )
                        status.text(
                            f"Lidas: {total_linhas:,} | Alteradas: {linhas_alteradas:,}".replace(",",".")
                        )

            os.replace(tmp_path, origem)

            if linhas_alteradas == 0 and rejeitado_path.exists():
                rejeitado_path.unlink()

            if st:
                progresso.empty()
                status.text(
                                f"Finalizado {arq}| Lidas: {total_linhas:,} | Alteradas: {linhas_alteradas:,}".replace(",",".")
                            )
                

                log[arq] = {
                                    "data_processamento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "tamanho_bytes": os.path.getsize(origem),
                                    "nome": arq,
                                    "linhas_totais": total_linhas,
                                    "linhas_alteradas": linhas_alteradas
                            }
                    
                with open(log_path, 'w') as f:
                    json.dump(log, f, indent=4)


        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            if st:
                progresso.empty()
                status.empty()
            raise

    return {
                "status": "saneado",
                "motivo": "arquivo processado",
                "arquivo": arq,
                "linhas_totais": total_linhas,
                "linhas_alteradas": linhas_alteradas
            }

def conv_num(df, lista = ['VL']):
    lst = df.columns.to_list()
    for nm in lst:
        if df[nm].dtype == 'object' and nm[:2].upper() in lista:
            df[nm] = pd.to_numeric(df[nm].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')
            df[nm]  = df[nm] .fillna(0)
    return df

def importar_dados_duckdb(
                            nome_tabela,
                            con,
                            Empresa,
                            colunas,
                            col_faltante=None,
                            valor_padrao=None,
                            inibir=False,
                            itens=None,
                            st=None
                        ):
    erro = {}
    df = pd.DataFrame()

    dt_ARQ = max_arq(nome_tabela, con, Empresa)

    if dt_ARQ:
        cod_empresa = f"00000{bsc_cd_aneel(Empresa)}"[-5:]

        arq = os.path.join(
                                rf"{st.session_state.tra_dir}\DADOS_BRUTOS_MANUAL",
                                f"{nome_tabela}_{cod_empresa}_{dt_ARQ}.csv"
                            )

        sanear_csv(
                        diretorio=rf"{st.session_state.tra_dir}\DADOS_BRUTOS_MANUAL",
                        arq=f"{nome_tabela}_{cod_empresa}_{dt_ARQ}.csv",
                        st=st
                    )

        for enc in [
                        "CP1252",
                        "latin-1",
                        "utf-8",
                        "utf-8-sig"
                    ]:
            try:
                if itens == None:
                    SQLq = f"""
                        SELECT *
                        FROM read_csv(
                            '{arq}',
                            delim='|',
                            null_padding=true,
                            encoding='{enc}',
                            parallel=true,
                            all_varchar=true
                        );
                    """

                else:
                    SQLq = f"""
                        SELECT {itens}
                        FROM read_csv(
                            '{arq}',
                            delim='|',
                            null_padding=true,
                            encoding='{enc}',
                            parallel=true,
                            all_varchar=true
                        );
                    """

                df = duckdb.query(SQLq).to_df()

                df = conv_num(
                                    df,
                                    colunas
                                )

                if col_faltante and col_faltante not in df.columns:
                    df[col_faltante] = valor_padrao

                return df, erro

            except Exception as e:
                erro[enc] = e

        return df, erro

    else:
        if inibir:
            return pd.DataFrame(), erro

        mensagem = (
                        f"Falha ao importar o arquivo "
                        f"{nome_tabela} da base local."
                    )

        if st:
            st.error(mensagem)
            return pd.DataFrame(), erro

        else:
            raise UserWarning(mensagem)

def bsc_dd_mop_st(tipo="ROA", ax = "Cd_SubODI", NG = '3', local = ""):
    dir_trabm = local
    arquivo_csv = [
                        os.path.join(rf"{dir_trabm}\DADOS_BRUTOS_MANUAL", f)
                        for f in os.listdir(rf"{dir_trabm}\DADOS_BRUTOS_MANUAL")
                        if f.lower().endswith('.csv') and (f.lower()[:4]== f"{tipo.lower()}_")
                    ]
    
    arq = arquivo_csv[0].replace("\\","/").replace("\\","/")
    arquivo_csv = [
                        os.path.join(rf"{dir_trabm}\DADOS_BRUTOS_MANUAL", f)
                        for f in os.listdir(rf"{dir_trabm}\DADOS_BRUTOS_MANUAL")
                        if f.lower().endswith('.csv') and ((f.lower()[:4]=="ros_") & (f.lower()[:5]!="ros_v") & (f.lower()[:5]!="ros_a"))
                    ]
    arq1 = arquivo_csv[0].replace("\\","/")
    sanear_csv(
                        diretorio = rf"{st.session_state.tra_dir}\DADOS_BRUTOS_MANUAL",
                        arq = arq, st = st                                    
                    )
    sanear_csv(
                        diretorio = rf"{st.session_state.tra_dir}\DADOS_BRUTOS_MANUAL",
                        arq = arq1, st = st                                    
                    )
    
    for enc in ['CP1252', 'latin-1', 'utf-8']:
        try:
            SQLq = f"""
                        WITH T1 AS (
                                    SELECT 
                                        CAST({ax} AS STRING) AS {ax},
                                        CAST(Nr_TI AS STRING) AS Nr_TI,
                                        CAST(Cd_CA AS STRING) AS Cd_CA,
                                        SUM(
                                            CAST(
                                                REPLACE(
                                                    REPLACE(VL_tot, '.', ''), 
                                                    ',', '.'
                                                ) AS DOUBLE
                                            )
                                        ) AS VL_TOTAL
                                    FROM read_csv_auto('{arq}',
                                        delim='|',
                                        null_padding=true, 
                                        encoding='{enc}',
                                        parallel=true,
                                        all_varchar=true,
                                        strict_mode=false
                                    ) WHERE Cd_NG = {NG}
                                    GROUP BY {ax}, Nr_TI, Cd_CA
                                ),

                                T2 AS (
                                    SELECT
                                        CAST({ax} AS STRING) AS {ax},
                                        CAST(Cd_Tipo_Obra AS STRING) AS Cd_Tipo_Obra
                                    FROM read_csv_auto('{arq1}',
                                        delim='|',
                                        null_padding=true, 
                                        encoding='{enc}',
                                        parallel=true,
                                        all_varchar=true,
                                        strict_mode=false
                                    )
                                ),

                                ti AS (
                                        SELECT
                                            CAST(Id_TI AS STRING)        AS Id_TI,
                                            CAST(Txt_Class AS STRING)    AS Txt_Class
                                        FROM read_csv_auto('tabelas/TBL_TI.csv',
                                            delim='|',
                                            null_padding=true,
                                            encoding='CP1252'
                                        )
                                    )

                                SELECT
                                    ti.Txt_Class AS Txt_TI,
                                    T2.Cd_Tipo_Obra,
                                    T1.Cd_CA,
                                    SUM(T1.VL_TOTAL) AS VL_CA
                                FROM T1
                                LEFT JOIN T2
                                    ON T1.{ax} = T2.{ax}
                                    LEFT JOIN ti ON T1.Nr_TI = ti.Id_TI
                                GROUP BY 
                                    T2.Cd_Tipo_Obra,
                                    ti.Txt_Class,
                                    T1.Cd_CA
                                ORDER BY
                                    T2.Cd_Tipo_Obra,
                                    ti.Txt_Class,
                                    T1.Cd_CA;
                    """
            df = duckdb.query(SQLq).to_df()
            break
        except Exception as e:
            st.error(e)
            df= pd.DataFrame()
    
    if df.empty:
        raise UserWarning("Você tem problema de codificação do arquivo.")
    df['Cd_Tipo_Obra'] = df['Cd_Tipo_Obra'].fillna('0')
    df['Cd_TIPO'] = df['Cd_Tipo_Obra']

    dic_CA = {"0" : "NA",
            "1" : "VL_FRT_TRN",
            "2" : "VL_PRJ",
            "3" : "VL_GER",
            "4" : "VL_FISC",
            "5" : "VL_MONT",
            "6" : "VL_SUP"}
    
    dic_TP1 = { "0" : "NA",
                '1' : 'Ampliação/Expansão',
                '2' : 'Construção',
                '3' : 'Manutenção',
                '4' : 'Melhoria/Reforma',
                '5' : 'Administrativo',
                '6' : 'Administrativo',
                '7' : 'Incorporação',
                '8' : 'PEE',
                '9' : 'PED',
                '10' : 'Manutenção',
                '11' : 'Medição',
                '12' : 'Medição'
                }
    dic_TP2 = { "0" : "NA",
                '1' : 'Investimento',
                '2' : 'Investimento',
                '3' : 'Manutenção',
                '4' : 'Investimento',
                '5' : 'Investimento',
                '6' : 'Manutenção',
                '7' : 'Investimento',
                '8' : 'Investimento',
                '9' : 'Investimento',
                '10' : 'Investimento',
                '11' : 'Investimento',
                '12' : 'Manutenção'
                }
    
    df = df[["Txt_TI", "Cd_TIPO", "Cd_Tipo_Obra", "Cd_CA", "VL_CA"]]
    df["Cd_CA"] = df["Cd_CA"].map(dic_CA)
    df["Cd_TIPO"] = df["Cd_TIPO"].map(dic_TP2)
    df["Cd_Tipo_Obra"] = df["Cd_Tipo_Obra"].map(dic_TP1)
    df = df.fillna("ND")

    for enc in ['CP1252', 'latin-1', 'utf-8']:
        try:
            SQLq = f"""
                WITH T1 AS (
                            SELECT 
                                CAST({ax} AS STRING) AS {ax},
                                CAST(Nr_TI AS STRING) AS Nr_TI,
                                CAST(Cd_CA AS STRING) AS Cd_CA,
                                SUM(
                                    CAST(
                                        REPLACE(
                                            REPLACE(VL_tot, '.', ''), 
                                            ',', '.'
                                        ) AS DOUBLE
                                    )
                                ) AS VL_TOTAL
                            FROM read_csv_auto('{arq}',
                                delim='|',
                                null_padding=true, 
                                encoding='{enc}',
                                parallel=true,
                                all_varchar=true,
                                strict_mode=false
                            )
                            GROUP BY {ax}, Nr_TI, Cd_CA
                        ),

                        T2 AS (
                            SELECT
                                CAST({ax} AS STRING) AS {ax},
                                CAST(Cd_Tipo_Obra AS STRING) AS Cd_Tipo_Obra
                            FROM read_csv_auto('{arq1}',
                                delim='|',
                                null_padding=true, 
                                encoding='{enc}',
                                parallel=true,
                                all_varchar=true,
                                strict_mode=false
                            )
                        ),

                        ti AS (
                                SELECT
                                    CAST(Id_TI AS STRING)        AS Id_TI,
                                    CAST(Txt_Class AS STRING)    AS Txt_Class
                                FROM read_csv_auto('tabelas/TBL_TI.csv',
                                    delim='|',
                                    null_padding=true,
                                    encoding='CP1252'
                                )
                            )

                        SELECT
                            ti.Txt_Class AS Txt_TI,
                            T2.Cd_Tipo_Obra,
                            SUM(T1.VL_TOTAL) AS VL_GLOBAL
                        FROM T1
                        LEFT JOIN T2
                            ON T1.{ax} = T2.{ax}
                            LEFT JOIN ti ON T1.Nr_TI = ti.Id_TI
                        GROUP BY 
                            T2.Cd_Tipo_Obra,
                            ti.Txt_Class
                        ORDER BY
                            T2.Cd_Tipo_Obra,
                            ti.Txt_Class;
            """
            df1 = duckdb.query(SQLq).to_df()
            break
        except Exception as e:
            st.error(e)
            df= pd.DataFrame()
    
    if df1.empty:
        raise UserWarning("Você tem problema de codificação do arquivo.")

    df1['Cd_Tipo_Obra'] = df1['Cd_Tipo_Obra'].fillna('0')
    df1['Cd_TIPO'] = df1['Cd_Tipo_Obra']
    df1 = df1[["Txt_TI", "Cd_TIPO", "Cd_Tipo_Obra", "VL_GLOBAL"]]
    df1["Cd_TIPO"] = df1["Cd_TIPO"].map(dic_TP2)
    df1["Cd_Tipo_Obra"] = df1["Cd_Tipo_Obra"].map(dic_TP1)
    df1 = df1.fillna("ND")

    df = (
            df.merge(
                        df1,
                        how='outer',
                        on=['Txt_TI', 'Cd_TIPO', 'Cd_Tipo_Obra'],
                        indicator=True
                    )
            )
    
    df = df.rename(columns={'_merge': 'OBS_SFF'})
    df['OBS_SFF'] = df['OBS_SFF'].map({
                                        'both': 'TI possui MOP',
                                        'left_only': 'MOP não possui TI declarada',
                                        'right_only': 'TI não possui MOP'
                                    })
    df['VL_CA'] = df['VL_CA'].fillna(0)
    df['VL_GLOBAL'] = df['VL_GLOBAL'].fillna(0)
    df['Pct_TI_CA_ATV'] = df['VL_CA'] / df['VL_GLOBAL']
    df = df[["Txt_TI", "Cd_TIPO", "Cd_Tipo_Obra", "Cd_CA", 'VL_CA', 'Pct_TI_CA_ATV', 'OBS_SFF']]
    return df

def tabela_existe(conn, nome):
    try:
        resultado = conn.execute(f"SELECT 1 FROM {nome} LIMIT 1").fetchone()
        return resultado is not None
    except Exception:
        return False

def tab_CVA(bdduck, todos_arq = False, dt_fim = None, refaz = False):
    try:
        bsc = [linha[0] for linha in bdduck.execute("SHOW TABLES").fetchall()]      

        tabelas = [
                        n for n in bsc
                        if n.startswith("Arq") and not n.endswith("plano")
                    ]
        selects = [
                        f"""
                        SELECT
                            '{n}' AS nm_ARQ,
                            STRPTIME("COL_3", '%d%m%Y') AS COL_3,
                            STRPTIME("COL_4", '%d%m%Y') AS COL_4,
                            SUBSTR("COL_3", 5, 4) AS ANO
                        FROM {n}
                        WHERE "COL_1" = '0000'
                        """
                        for n in tabelas
                    ]
        sSQL = "\nUNION ALL\n".join(selects)
        df_arq = bdduck.execute(sSQL).fetchdf()
        df_arq = df_arq.sort_values("COL_3")
        
        LST_TBL = []
        total_anos = len(df_arq['ANO'].unique())
        progress_bar = st.progress(0)
        status_text = st.empty()
        ibpg = 0

        if not todos_arq:
            df_arq = df_arq[df_arq['ANO'].astype(int) >= (dt_fim.year - 1)]

        for ano, grupo in df_arq.groupby('ANO'):
            if (not refaz) and (f"nv_ARQ{ano}" in bsc):
                continue
            arquivos = grupo['nm_ARQ'].tolist()
            progress_percent = int((ibpg / total_anos) * 100)
            progress_bar.progress(progress_percent)
            status_text.text(f"Processando ano {ano}... ({ibpg + 1}/{total_anos})")
            if len(arquivos) == 1:
                LST_TBL.append(arquivos[0])
                continue
            nome_destino = f"nv_ARQ{ano}"

            if nome_destino not in bsc:
                selects = [f"SELECT * FROM {nm}" for nm in arquivos]
                sSQL = f"""
                            DROP TABLE IF EXISTS nv_ARQ{ano};
                            CREATE TABLE nv_ARQ{ano} AS
                            {' UNION ALL '.join(selects)};
                        """
                bdduck.execute(sSQL)
                LST_TBL.append(f"nv_ARQ{ano}")
            ibpg += 1
            
        status_text.text("Processamento concluído!")
        return LST_TBL
    except Exception as e:
        raise UserWarning(f"Falhou agregação: {e}")


def existe_dk(bdduck, tabela):
    return bdduck.execute(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_name = '{tabela}' 
                """).fetchone()[0] > 0

def configurar_sqlite_pragmas(conexao, modo='leitura'):
    """
    Aplica PRAGMAs otimizados para leitura ou leitura/escrita no SQLite.

    Parâmetros:
        conexao: conexão sqlite3 ativa.
        modo (str): 'leitura' ou 'escrita'.
    """
    if modo == 'leitura':
        conexao.execute("PRAGMA synchronous = OFF")
        conexao.execute("PRAGMA journal_mode = OFF")
    elif modo == 'escrita':
        conexao.execute("PRAGMA synchronous = NORMAL")
        conexao.execute("PRAGMA journal_mode = WAL")
    else:
        raise ValueError("Modo deve ser 'leitura' ou 'escrita'")

    conexao.execute("PRAGMA temp_store = MEMORY")
    conexao.execute("PRAGMA cache_size = 100000")

def configurar_sqlite_para_desempenho(con):
    con.execute("PRAGMA synchronous = OFF")
    con.execute("PRAGMA journal_mode = MEMORY")
    con.execute("PRAGMA temp_store = MEMORY")
    con.execute("PRAGMA cache_size = 100000")

def PLANO_CONTAS(bd = None, bsc = None, st=None):
    st.divider()
    try:
        df = pd.DataFrame()
        sSQL = f"""
                    SELECT *
                    FROM TST_PLANO
                    """
        df = bd.execute(sSQL).fetchdf()

        df_TESTE = df[(df['COD_NAT']=='01')].copy()
        df_TESTE['FLG_CX'] = False
        lst_CNT_SUP = df_TESTE[df_TESTE['Txt_Desc'].isin(['Equivalentes de Caixa',
                                                'Numerário',
                                                'Numerário em Trânsito',
                                                'Contas Bancárias à Vista',
                                                'Ordens de Pagamento Emitidas',
                                                ])]['COD_CTA_SUP'].drop_duplicates().to_list()
        i=1
        while True:
            df_PROV = df_TESTE[df_TESTE['COD_CTA_SUP'].isin(lst_CNT_SUP)]
            if len(df_PROV[df_PROV['NIVEL']=='4']) or (i==5):
                break
            else:
                lst_CNT_SUP = df_TESTE[df_TESTE['COD_CTA'].isin(
                    df_PROV['COD_CTA_SUP'].drop_duplicates().to_list())]['COD_CTA_SUP'].drop_duplicates().to_list()
            i += 1
        i=4
        lst_CNT_SUP = df_PROV[df_PROV['NIVEL']=='4']['COD_CTA'].drop_duplicates().to_list()
        lst_CX = []
        while i<8:
            df_PROV = df_TESTE[df_TESTE['COD_CTA_SUP'].isin(lst_CNT_SUP)]
            if len(df_PROV):
                lst_CX += df_PROV['COD_CTA'].drop_duplicates().to_list()
            lst_CNT_SUP = df_PROV[df_PROV['COD_CTA_SUP'].isin(lst_CNT_SUP)]['COD_CTA'].drop_duplicates().to_list()
            i += 1

        df_TESTE = df_TESTE[['COD_CTA','CTA','FLG_CX']].drop_duplicates(subset=['COD_CTA','CTA']).reset_index(drop='index')
        df_TESTE.loc[df_TESTE['COD_CTA'].isin(lst_CX),'FLG_CX'] = True

        df_TESTE = df_TESTE.sort_values(by=['COD_CTA'])
        bd.register("temp_df", df_TESTE)
        bd.execute("CREATE OR REPLACE TABLE plano_contas AS SELECT * FROM temp_df")
        bd.unregister("temp_df")

    except:
        return pd.DataFrame()
        
    st.divider()
    return df_TESTE

def listar_tabelas(conexao):
    """
    Retorna uma lista com os nomes das tabelas em uma conexão SQLite existente.
    Em caso de erro, retorna um dicionário com a chave 'erro' e a mensagem.

    Parâmetros:
    conexao (sqlite3.Connection): Objeto de conexão SQLite.

    Retorna:
    list | dict: Lista de nomes das tabelas ou dicionário com erro.
    """
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = [linha[0] for linha in cursor.fetchall()]
        return tabelas
    except sl.Error as e:
        return {'erro': str(e)}

def lst_tab(banco):
    banco_de_dados = banco
    conexao = sl.connect(banco_de_dados)
    df_tabelas = pd.read_sql("SELECT name AS 'Nome da Tabela' FROM sqlite_master WHERE type='table';", conexao)
    conexao.close()
    return df_tabelas


def apagar_tbl(nm_tbl, conn):
    c = conn.cursor()
    try:
        c.execute("DROP TABLE " + nm_tbl)
        conn.commit()
        return f"Tabela {nm_tbl} excluída com sucesso!"
    except:
        return f"Ocorreu um erro ao excluir a tabela {nm_tbl}."

def executar_query(sql, conn):
    c = conn.cursor()
    try:
        c.execute(sql)
        conn.commit()
        return "Atualização executada com sucesso!"
    except:
        return "Ocorreu um erro ao executar a atualização."

def existe_tabela(nm_tbl, conn, registros=True):
    c = None
    try:
        if isinstance(conn, str):
            conn = sl.connect(conn)
        c = conn.cursor()

        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nm_tbl,))
        if not c.fetchone():
            return False

        if registros:
            c.execute(f"SELECT 1 FROM {nm_tbl} LIMIT 1")
            return bool(c.fetchone())
        else:
            return True

    except sl.Error as e:
        print(f"Erro ao verificar a tabela '{nm_tbl}': {e}")
        return False

    finally:
        if c is not None:
            c.close()

def cria_DB(local=None, apagar = True, empresa = 'ND', ano = 0):

    if local==None or empresa == 'ND' or ano == 0:
        return None
    if apagar:
        try:
            os.remove(f'{local}\{empresa}_{ano}.db')
        except:
            st.error(f"Sem permissão para deletar o arquivo {local}\{empresa}_{ano}.db.")

    con = sl.connect(f'{local}\{empresa}_{ano}.db')
    return con

def criar_tabela(nome_tabela, dados, bd, colunas=None):
    if not existe_tabela(nome_tabela, bd):
        if colunas:
            df = pd.DataFrame(dados, columns=colunas)
        else:
            df = pd.DataFrame(dados)
        df.to_sql(nome_tabela, bd)

def cria_DBdbf(dir_arq_dbf, dir_arq_base, sufixo = "ANT", apagar = True, empresa = 'ND', ano = 0):
    """
    Função para criar banco de dados, com arquivos dbf.
    
    Args:
        dir_arq_dbf (str): Nome do local com os arquivos a serem carregados.
        dir_arq_base (str): Nome do local em que se salva a base.
        sufixo (str): Indica se são os dados atuais ou anteriores ('ANT', default).
        empresa (str): Nome da empresa ('ND', default).
        ano (int): Ano de Referência (0, default).
    """
    LST_ARQ = os.listdir(dir_arq_dbf)
    if len(LST_ARQ)==0:
        st.error(f"Faltam arquivos para importar no diretório: {dir_arq_dbf}")
        return "Falhou"
    if apagar:
        try:
            os.remove(f'{dir_arq_base}//BDGD_{sufixo}_{empresa}_{ano}.db')
        except:
            st.error(f"Sem permissão para deletar o arquivo {dir_arq_base}//BDGD_{sufixo}_{empresa}_{ano}.db.")

    con = sl.connect(f'{dir_arq_base}//BDGD_{sufixo}_{empresa}_{ano}.db')
    
    LST_TBL = ['BAR', 'EQSIAT', 'EQTRM', 'EQTRSX', 'EQTRD', 'EQTRS', 'EQTRSX', 'EQME', 'EQRE', 'EQSE', 'PONNOT', 'RAMLIG',
               'SEGCON', 'SSDMT', 'SSDBT', 'SUB', 'SSDAT', 'UNCRAT', 'UNCRMT', 'UNREAT', 'UNREMT', 'UNSEAT',
               'UNSEMT', 'UNSEBT', 'UNCRBT', 'UNTRD', 'UNTRS', 'EQCR', 'EQTRAT', 'EQTRMT', 'UNTRAT', 
               'UNTRMT', 'CONJ', 'CTAT', 'CTMT', 'UCAT', 'UCMT', 'UCBT', 'UGAT', 'UGMT', 'UGBT', 'BAY']
    
    
    i=0
    nr_arq = len(LST_ARQ) + 1
    progresso = st.progress(i  * 100 // nr_arq, text= f"Analisando arquivo {LST_ARQ[0]}...")
    
    start = time.time()
    for arq in LST_ARQ:
        
        if arq.lower().endswith(".dbf"):
            progresso.progress(i  * 100 // nr_arq, text= f"Importando arquivo {arq}...")
            i += 1
            if arq.find('_') == -1:
                Nm_TBL = arq[: arq.find('.')]
            else:
                Nm_TBL = arq[: arq.find('_')]
            if Nm_TBL in LST_TBL:
                encodings_tentativas = [None, 'latin-1', 'cp437', 'cp1252', 'cp850', 'utf-8']
                tabela = None
                for enc in encodings_tentativas:
                    try:
                        with DBF(f"{dir_arq_dbf}/{arq}", encoding=enc) as tbl:
                            tabela = [record for record in tbl]
                            break 
                    except Exception as e:
                        st.warning(e)

                try:
                    df = pd.DataFrame(iter(tabela))
                    if Nm_TBL in ['SSDMT', 'SSDBT', 'SSDAT', 'UNCRAT', 'UNCRMT', 'UNREAT', 'UNREMT', 'UNSEAT',
                                  'UNSEMT', 'UNSEBT', 'UNCRBT', 'UNTRAT', 'UNTRMT', 'CTAT', 'CTMT', 'UCAT', 
                                  'UCMT', 'UCBT', 'UGAT', 'UGMT', 'UGBT']:

                        df['GRU_TEN'] = Nm_TBL[-2:]
                        
                except:
                    st.write(tabela)
                    st.write(Nm_TBL)
                    raise
                df.to_sql(Nm_TBL + '_' + sufixo, con, if_exists = 'append')
    end = time.time()
    progresso.progress(100, text=f"Carregou arquivos na database BDGD {sufixo}, diretório BD_LOCAL, em {end - start:.2f} segundos.")
    con.close()
    return "OK"

def imp_sped(dir_arq_SPED, dir_arq_base, SPED, empresa, ano, apagar=False):
    column_names = [i for i in range(0, 42)]
    LST_ARQ = os.listdir(dir_arq_SPED)
    if apagar:
        try:
            os.remove(f'{dir_arq_base}\{SPED}_{empresa}_{ano}.db')
        except:
            st.error(f"Não é possível apagar, pois inexiste o arquivo {dir_arq_base}\{SPED}_{empresa}_{ano}.db.")

    with sl.connect(f'{dir_arq_base}\{SPED}_{empresa}_{ano}.db') as bd:

        if (len(LST_ARQ)>0) and bd:
            
            if existe_tabela('LST_ARQ', bd):
                df_arq = pd.read_sql("SELECT * FROM LST_ARQ", bd)
            else:
                df_arq = pd.DataFrame(columns=['Dt_REF','CNPJ','Nm_Arq'])

            nr_arq = len(LST_ARQ) + 1
            progresso = st.progress(0, text= f"Iniciando importação...")
            
            for i, arq in enumerate(LST_ARQ):
                if arq in df_arq['Nm_Arq'].drop_duplicates().to_list():
                    continue
                if arq.upper().endswith(".TXT"):
                    sanear_csv(dir_arq_SPED, arq, st=st)
                    progresso.progress(i  * 100 // nr_arq, text= f"Importando arquivo {arq}...")
                    arq_cam=f"{dir_arq_SPED}//{arq}"
                    df=pd.read_csv(arq_cam, sep="|", decimal=',', on_bad_lines='skip', encoding="Latin-1",
                                header = None, names=column_names, lineterminator='\n', dtype=str);
                    lst_BLC = df[df[0].isnull()][1].drop_duplicates().to_list()
                    if SPED == 'EFD_ICMS':
                        Nr_CNPJ = df.iloc[0,7]
                        Dt_INI = datetime.strptime(df.iloc[0,4], "%d%m%Y")
                        Dt_FIM = datetime.strptime(df.iloc[0,5], "%d%m%Y")
                    elif SPED == "ECD":
                        Nr_CNPJ = df.iloc[0,6]
                        Dt_INI = datetime.strptime(df.iloc[0,3], "%d%m%Y")
                        Dt_FIM = datetime.strptime(df.iloc[0,4], "%d%m%Y")
                    else:
                        df_arq = pd.DataFrame({'Dt_INI': [0], 'Dt_FIM': [0], 'CNPJ': ['0'], 'Nm_Arq': ['Estrutura SPED não reconhecida!']})
                        return df_arq

                    nv_arq = {'Dt_INI': Dt_INI, 'Dt_FIM': Dt_FIM, 'CNPJ': Nr_CNPJ, 'Nm_Arq': arq}
                    if len(df_arq)==0:
                        df_arq = pd.DataFrame([nv_arq])
                    else:
                        df_arq = pd.concat([df_arq, pd.DataFrame([nv_arq])], ignore_index=True)

                    indice = df_arq[(df_arq['Dt_INI']==Dt_INI) & (df_arq['Dt_FIM']==Dt_FIM) & (df_arq['CNPJ']==Nr_CNPJ) & (df_arq['Nm_Arq']==arq)].index.tolist()[0]
                    
                    df1 = df[df[1].isin(lst_BLC)].copy()
                    ult_col = next((col for col in reversed(df1.columns) if df1[col].notna().any()), None)
                    df1 = df1.iloc[:, 1:ult_col]
                    df1['IND_ARQ'] = indice
                    df1.to_sql(f"Arq_{indice}", bd, if_exists='replace', index=False)

            df_arq.to_sql("LST_ARQ", bd, if_exists='replace', index=False)
            SQLq = """
                        SELECT
                                page_count as Nr_PAG,
                                freelist_count as Nr_PAG_LIV,
                                page_size as TAM_PAG,
                                ROUND(page_count * page_size / 1024.0 / 1024.0 / 1024.0, 2) AS db_TAM_GB,
                                ROUND(freelist_count * page_size / 1024.0 / 1024.0 / 1024.0, 2) AS LIVRE_GB,
                                ROUND(100.0 * freelist_count / page_count, 2) AS Pct_LIVRE
                                FROM (
                                SELECT
                                    (SELECT page_count FROM pragma_page_count) AS page_count,
                                    (SELECT freelist_count FROM pragma_freelist_count) AS freelist_count,
                                    (SELECT page_size FROM pragma_page_size) AS page_size
                                );
                   """
            df2 = pd.read_sql(SQLq, bd)
            st.divider()
            st.info("Abaixo temos os dados finais do banco.")
            st.write(df2)
            st.divider()
        progresso.progress(100, text= f"Finalizada Importação de {SPED}!")
        return df_arq
    
def imp_sped_ecf_duckdb(dir_arq_SPED, dir_arq_base, SPED, empresa, ano):
    column_names = [i for i in range(0, 42)]
    LST_ARQ = os.listdir(dir_arq_SPED)
    try:
        os.remove(f'{dir_arq_base}\{SPED}_{empresa}_{ano}.duckdb')
    except:
        st.error(f"Inexiste o arquivo {dir_arq_base}\{SPED}_{empresa}_{ano}.duckdb.")

    with duckdb.connect(f'{dir_arq_base}\{SPED}_{empresa}_{ano}.duckdb') as bd:
        if (len(LST_ARQ)>0) and bd:
            df_arq = pd.DataFrame(columns=['Dt_REF','CNPJ','Nm_Arq'])
            nr_arq = len(LST_ARQ) + 1
            progresso = st.progress(0, text= f"Iniciando importação...")
            
            for i, arq in enumerate(LST_ARQ):
                if arq.upper().endswith(".TXT"):
                    sanear_csv(dir_arq_SPED, arq, st=st)
                    progresso.progress(i  * 100 // nr_arq, text= f"Importando arquivo {arq}...")
                    arq_cam=f"{dir_arq_SPED}//{arq}"
                    cabeca_info = bd.execute(f"""
                                                    SELECT * FROM read_csv_auto('{arq_cam}', sep='|', decimal=',', 
                                                    encoding='Latin-1', header=False, sample_size=1)
                                                """).fetchone()
                    
                    if SPED == 'EFD_ICMS':
                        Nr_CNPJ, Dt_INI_str, Dt_FIM_str = cabeca_info[7], cabeca_info[4], cabeca_info[5]
                    elif SPED == "ECD":
                        Nr_CNPJ, Dt_INI_str, Dt_FIM_str = cabeca_info[6], cabeca_info[3], cabeca_info[4]
                    else:
                        st.error("Estrutura SPED não reconhecida!")
                        return df_arq
                    
                    Dt_INI = datetime.strptime(str(Dt_INI_str), "%d%m%Y")
                    Dt_FIM = datetime.strptime(str(Dt_FIM_str), "%d%m%Y")
                    nv_arq = {'Dt_INI': Dt_INI, 'Dt_FIM': Dt_FIM, 'CNPJ': Nr_CNPJ, 'Nm_Arq': arq}
                    df_arq = pd.concat([df_arq, pd.DataFrame([nv_arq])], ignore_index=True)
                    indice = df_arq.index[-1]

                    bd.execute(f"""
                                    CREATE TABLE IF NOT EXISTS Arq_{indice} AS 
                                    SELECT 
                                        *, 
                                        {indice} AS IND_ARQ 
                                    FROM read_csv_auto(
                                        '{arq_cam}', 
                                        sep='|', 
                                        decimal_separator=',',
                                        null_padding=true, 
                                        encoding='Latin-1', 
                                        header=False, 
                                        names={column_names},
                                        parallel = true,
                                        all_varchar = true
                                    )
                                    WHERE column0 IS NULL
                                """)

            bd.execute("CREATE TABLE IF NOT EXISTS LST_ARQ AS SELECT * FROM df_arq")
        progresso.progress(100, text= f"Finalizada Importação de {SPED}!")
        return df_arq
    
def imp_sped_vchunk(dir_arq_SPED, dir_arq_base, SPED, empresa, ano):
    # para empresas grandes os arquivos possuem muitos registros. Para evitar uso excessivo de memória vamos
    # fazer leitura por lotes
    def extrair_metadados_sped(chunk: pd.DataFrame, sped: str) -> dict:
        if sped == "EFD_ICMS":
            return {
                        "CNPJ": chunk.iloc[0, 7],
                        "Dt_INI": datetime.strptime(chunk.iloc[0, 4], "%d%m%Y"),
                        "Dt_FIM": datetime.strptime(chunk.iloc[0, 5], "%d%m%Y"),
                    }
        elif sped == "ECD":
            return {
                        "CNPJ": chunk.iloc[0, 6],
                        "Dt_INI": datetime.strptime(chunk.iloc[0, 3], "%d%m%Y"),
                        "Dt_FIM": datetime.strptime(chunk.iloc[0, 4], "%d%m%Y"),
                    }

        raise ValueError("Estrutura SPED não reconhecida!")

    def obter_blocos(chunk: pd.DataFrame) -> list:
        return (
                    chunk.loc[chunk[0].isnull(), 1]
                    .drop_duplicates()
                    .to_list()
                )

    def ultima_coluna_com_dados(df: pd.DataFrame):
        return next(
                        (col for col in reversed(df.columns) if df[col].notna().any()),
                        None
                    )

    def carregar_controle(bd) -> pd.DataFrame:
        try:
            df = pd.read_sql("SELECT * FROM LST_ARQ", bd)

        except Exception:
            df = pd.DataFrame(columns=[
                                "IND_ARQ", "Dt_INI", "Dt_FIM", "CNPJ", "Nm_Arq",
                                "STATUS", "DH_ATUALIZACAO"
                            ])

        for col in ["IND_ARQ", "Dt_INI", "Dt_FIM", "CNPJ", "Nm_Arq", "STATUS", "DH_ATUALIZACAO"]:
            if col not in df.columns:
                df[col] = None

        return df

    def salvar_controle(df_arq: pd.DataFrame, bd):
        df_save = df_arq.copy()

        if "Dt_INI" in df_save.columns:
            df_save["Dt_INI"] = pd.to_datetime(df_save["Dt_INI"], errors="coerce").dt.strftime("%Y-%m-%d")
        if "Dt_FIM" in df_save.columns:
            df_save["Dt_FIM"] = pd.to_datetime(df_save["Dt_FIM"], errors="coerce").dt.strftime("%Y-%m-%d")
        if "DH_ATUALIZACAO" in df_save.columns:
            df_save["DH_ATUALIZACAO"] = pd.to_datetime(df_save["DH_ATUALIZACAO"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")

        df_save.to_sql("LST_ARQ", bd, if_exists="replace", index=False)

    def proximo_indice(df_arq: pd.DataFrame) -> int:
        if df_arq.empty:
            return 0

        serie = pd.to_numeric(df_arq["IND_ARQ"], errors="coerce").dropna()
        if serie.empty:
            return 0

        return int(serie.max()) + 1

    def obter_ou_criar_registro_arquivo(df_arq: pd.DataFrame, metadados: dict, nome_arquivo: str):
        filtro = df_arq["Nm_Arq"].astype(str).eq(str(nome_arquivo))
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if filtro.any():
            idx = df_arq.index[filtro][0]
            ind_arq = int(pd.to_numeric(df_arq.loc[idx, "IND_ARQ"], errors="coerce"))
            df_arq.loc[idx, "Dt_INI"] = metadados["Dt_INI"]
            df_arq.loc[idx, "Dt_FIM"] = metadados["Dt_FIM"]
            df_arq.loc[idx, "CNPJ"] = metadados["CNPJ"]
            df_arq.loc[idx, "STATUS"] = "PROCESSANDO"
            df_arq.loc[idx, "DH_ATUALIZACAO"] = agora
        else:
            ind_arq = proximo_indice(df_arq)
            novo_registro = {
                                "IND_ARQ": ind_arq,
                                "Dt_INI": metadados["Dt_INI"],
                                "Dt_FIM": metadados["Dt_FIM"],
                                "CNPJ": metadados["CNPJ"],
                                "Nm_Arq": nome_arquivo,
                                "STATUS": "PROCESSANDO",
                                "DH_ATUALIZACAO": agora
                            }
            df_arq = pd.concat([df_arq, pd.DataFrame([novo_registro])], ignore_index=True)
            idx = df_arq.index[-1]

        return df_arq, idx, ind_arq

    def atualizar_status(df_arq: pd.DataFrame, idx: int, status: str):
        df_arq.loc[idx, "STATUS"] = status
        df_arq.loc[idx, "DH_ATUALIZACAO"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return df_arq
    
    column_names = list(range(500))
    LST_ARQ = os.listdir(dir_arq_SPED)
    db_path = os.path.join(dir_arq_base, f"{SPED}_{empresa}_{ano}.db")

    with sl.connect(db_path) as bd:
        df_arq = carregar_controle(bd)

        if len(LST_ARQ) > 0:
            arquivos_txt = [arq for arq in LST_ARQ if arq.upper().endswith(".TXT")]
            nr_arq = max(len(arquivos_txt), 1)
            progresso = st.progress(0, text="Iniciando importação...")
            chunksize = 250_000

            for i, arq in enumerate(arquivos_txt, start=1):
                filtro_existente = df_arq["Nm_Arq"].astype(str).eq(str(arq))
                
                if filtro_existente.any():
                    idx_existente = df_arq.index[filtro_existente][0]
                    status_existente = str(df_arq.loc[idx_existente, "STATUS"])

                    if status_existente == "CONCLUIDO":
                        progresso.progress(i * 100 // nr_arq, text=f"Arquivo já carregado, ignorando: {arq}")
                        continue

                try:
                    #sanear_csv(dir_arq_SPED, arq, st=st)
                    progresso.progress(i * 100 // nr_arq, text=f"Importando arquivo {arq}...")
                    arq_cam = os.path.join(dir_arq_SPED, arq)
                    reader = pd.read_csv(
                                            arq_cam,
                                            decimal=",",
                                            sep="|",
                                            encoding="Latin-1",
                                            header=None,
                                            names=column_names,
                                            dtype=str,
                                            chunksize=chunksize,
                                            low_memory=True,
                                            engine="c",
                                            on_bad_lines="warn",
                                        )

                    lst_blc = None
                    indice = None
                    idx_registro = None
                    with st.spinner("Em progresso..."):
                        try:
                            bd.execute("PRAGMA journal_mode = WAL;")
                            bd.execute("PRAGMA synchronous = NORMAL;")
                            bd.execute("PRAGMA temp_store = MEMORY;")
                            bd.execute("PRAGMA cache_size = -200000;")

                            bd.execute("BEGIN")

                            erro_estrutura = False
                            lst_blc = None
                            indice = None

                            for n_chunk, chunk in enumerate(reader, start=1):
                                progresso.progress(
                                                        i * 100 // nr_arq,
                                                        text=f"Importando arquivo {arq}, lote {n_chunk}..."
                                                   )

                                if n_chunk == 1:
                                    try:
                                        metadados = extrair_metadados_sped(chunk, SPED)
                                    except ValueError:
                                        if filtro_existente.any():
                                            df_arq = atualizar_status(df_arq, idx_existente, "ERRO")
                                        else:
                                            novo = pd.DataFrame([{
                                                                    "IND_ARQ": proximo_indice(df_arq),
                                                                    "Dt_INI": None,
                                                                    "Dt_FIM": None,
                                                                    "CNPJ": None,
                                                                    "Nm_Arq": arq,
                                                                    "STATUS": "ERRO",
                                                                    "DH_ATUALIZACAO": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                                }])
                                            df_arq = pd.concat([df_arq, novo], ignore_index=True)

                                        salvar_controle(df_arq, bd)
                                        st.warning(f"Estrutura SPED não reconhecida no arquivo {arq}.")
                                        erro_estrutura = True
                                        break

                                    lst_blc = obter_blocos(chunk)
                                    df_arq, idx_registro, indice = obter_ou_criar_registro_arquivo(df_arq, metadados, arq)
                                    salvar_controle(df_arq, bd)

                                    bd.execute(f'DROP TABLE IF EXISTS "Arq_{indice}"')

                                df1 = chunk[chunk[1].isin(lst_blc)].copy()

                                if df1.empty:
                                    continue

                                ult_col = ultima_coluna_com_dados(df1)
                                if ult_col is None:
                                    continue

                                df1 = df1.iloc[:, 1:ult_col + 1].copy()
                                df1["IND_ARQ"] = indice
                                ncols = len(df1.columns)
                                df1.to_sql(
                                                f"Arq_{indice}",
                                                bd,
                                                if_exists="append",
                                                index=False,
                                                chunksize=20000,
                                            )

                            bd.commit()

                        except Exception:
                            bd.rollback()
                            raise
                    if idx_registro is not None:
                        df_arq = atualizar_status(df_arq, idx_registro, "CONCLUIDO")
                        salvar_controle(df_arq, bd)

                except Exception as e:
                    filtro_erro = df_arq["Nm_Arq"].astype(str).eq(str(arq))
                    if filtro_erro.any():
                        idx_erro = df_arq.index[filtro_erro][0]
                        df_arq = atualizar_status(df_arq, idx_erro, "ERRO")
                        salvar_controle(df_arq, bd)

                    st.warning(f"Erro ao importar {arq}: {e}")
                    continue

        progresso.progress(100, text=f"Finalizada Importação de {SPED}!")
        return df_arq
        
def bsc_cd_aneel(empresa):
    df = pd.read_csv(
        'tabelas/TBL_EMPRESAS.csv',
        decimal=',',
        on_bad_lines='skip',
        sep="|",
        encoding="Latin-1",
        usecols=['Cd_ANEEL', 'Nm_EMPRESA'],
        dtype = {'Cd_ANEEL' : int}
    )
    
    df = df.loc[df['Nm_EMPRESA'] == empresa, 'Cd_ANEEL']

    return df.iloc[0] if not df.empty else None

def bsc_cd_TODOS(empresa):
    df = pd.read_csv(
        'tabelas/TBL_EMPRESAS.csv',
        decimal=',',
        on_bad_lines='skip',
        sep="|",
        encoding="Latin-1"
    )
    
    df = df[df['Nm_EMPRESA'] == empresa].copy()

    return df if not df.empty else None

    
def max_arq(tabela, bd, empresa, st=None):
    if existe_tabela(tabela, bd):
        
        df_emp = pd.read_csv(
                                'tabelas/TBL_EMPRESAS.csv',
                                decimal=',',
                                on_bad_lines='skip',
                                sep="|",
                                encoding="Latin-1",
                                usecols=['Cd_ANEEL', 'Nm_EMPRESA'],
                                dtype = {'Cd_ANEEL' : int}
                            )
        df_emp.rename(columns={'Cd_ANEEL': 'Cd_Emp'}, inplace=True)

        sSQL = f"""
                    SELECT Cd_Emp + 0 AS Cd_Emp, MAX(dt_ARQ) AS dt_ARQ
                    FROM {tabela}
                    GROUP BY Cd_Emp
                """
        df = pd.read_sql(sSQL, bd)
        df = df.merge(df_emp, how='left', on='Cd_Emp')
        df = df.loc[df['Nm_EMPRESA'] == empresa, 'dt_ARQ']
        return df.iloc[0] if not df.empty else None
    else:
        return None
    
def imp_sped_duck(dir_arq_SPED, dir_arq_base, SPED, empresa, ano, apagar_base=False):
    column_names = [i for i in range(0, 42)]
    caminho_bd = os.path.join(dir_arq_base, f"{SPED}_{empresa}_{ano}.duckdb")

    if apagar_base and os.path.exists(caminho_bd):
        os.remove(caminho_bd)

    if not os.path.exists(dir_arq_SPED):
        st.error(f"Pasta inexistente: {dir_arq_SPED}")
        return pd.DataFrame(columns=['Dt_INI', 'Dt_FIM', 'CNPJ', 'Nm_Arq'])

    LST_ARQ = [f for f in os.listdir(dir_arq_SPED) if f.upper().endswith(".TXT")]

    with duckdb.connect(caminho_bd) as bd:

        bd.execute("""
                        CREATE TABLE IF NOT EXISTS controle_importacao (
                            nome_arquivo VARCHAR PRIMARY KEY,
                            data_importacao TIMESTAMP,
                            dt_ini TIMESTAMP,
                            dt_fim TIMESTAMP,
                            cnpj VARCHAR,
                            tabela_destino VARCHAR,
                            indice_arquivo BIGINT
                        )
                    """)

        arquivos_importados = set()
        try:
            res = bd.execute("SELECT nome_arquivo FROM controle_importacao").fetchall()
            arquivos_importados = {x[0] for x in res}
        except:
            arquivos_importados = set()

        arquivos_para_importar = [arq for arq in LST_ARQ if arq not in arquivos_importados]

        try:
            df_arq_existente = bd.execute("""
                                                SELECT dt_ini AS Dt_INI,
                                                    dt_fim AS Dt_FIM,
                                                    cnpj AS CNPJ,
                                                    nome_arquivo AS Nm_Arq
                                                FROM controle_importacao
                                                ORDER BY dt_ini, nome_arquivo
                                            """).fetchdf()
        except:
            df_arq_existente = pd.DataFrame(columns=['Dt_INI', 'Dt_FIM', 'CNPJ', 'Nm_Arq'])

        if len(LST_ARQ) == 0:
            st.info("Nenhum arquivo TXT encontrado.")
            return df_arq_existente

        if not arquivos_para_importar:
            st.info("Todos os arquivos já foram importados anteriormente.")
            return df_arq_existente

        df_novos = pd.DataFrame(columns=['Dt_INI', 'Dt_FIM', 'CNPJ', 'Nm_Arq'])

        total = len(arquivos_para_importar)
        progresso = st.progress(0, text="Iniciando importação...")

        try:
            prox_indice = bd.execute("""
                                        SELECT COALESCE(MAX(indice_arquivo), -1) + 1
                                        FROM controle_importacao
                                    """).fetchone()[0]
        except:
            prox_indice = 0

        for i, arq in enumerate(arquivos_para_importar, start=1):
            progresso.progress((i - 1) * 100 // total, text=f"Importando arquivo {arq}...")

            arq_cam = os.path.join(dir_arq_SPED, arq)

            try:
                df = pd.read_csv(
                    arq_cam,
                    sep="|",
                    decimal=",",
                    on_bad_lines="skip",
                    encoding="Latin-1",
                    header=None,
                    names=column_names,
                    lineterminator="\n",
                    dtype=str
                )
            except Exception as e:
                st.error(f"Erro ao ler {arq}: {e}")
                continue

            if df.empty:
                st.warning(f"Arquivo vazio ou sem linhas válidas: {arq}")
                continue

            nm_col = [f"COL_{j}" for j in range(len(df.columns))]
            df.columns = nm_col

            try:
                lst_BLC = df[df["COL_0"].isnull()]["COL_1"].drop_duplicates().to_list()
            except Exception as e:
                st.error(f"Erro ao identificar blocos em {arq}: {e}")
                continue

            try:
                if SPED == "EFD_ICMS":
                    Nr_CNPJ = df.iloc[0, 7]
                    Dt_INI = datetime.strptime(df.iloc[0, 4], "%d%m%Y")
                    Dt_FIM = datetime.strptime(df.iloc[0, 5], "%d%m%Y")
                elif SPED == "ECD":
                    Nr_CNPJ = df.iloc[0, 6]
                    Dt_INI = datetime.strptime(df.iloc[0, 3], "%d%m%Y")
                    Dt_FIM = datetime.strptime(df.iloc[0, 4], "%d%m%Y")
                else:
                    st.error("Estrutura SPED não reconhecida.")
                    return pd.DataFrame({
                        'Dt_INI': [None],
                        'Dt_FIM': [None],
                        'CNPJ': ['0'],
                        'Nm_Arq': ['Estrutura SPED não reconhecida!']
                    })
            except Exception as e:
                st.error(f"Erro ao extrair metadados de {arq}: {e}")
                continue

            nv_arq = {
                'Dt_INI': Dt_INI,
                'Dt_FIM': Dt_FIM,
                'CNPJ': Nr_CNPJ,
                'Nm_Arq': arq
            }
            df_novos = pd.concat([df_novos, pd.DataFrame([nv_arq])], ignore_index=True)

            indice = prox_indice
            prox_indice += 1

            try:
                df1 = df[df["COL_1"].isin(lst_BLC)].copy()

                ult_col = next(
                    (col for col in reversed(df1.columns) if df1[col].notna().any()),
                    None
                )

                if ult_col is None:
                    st.warning(f"Arquivo sem colunas úteis após filtro: {arq}")
                    continue

                df1 = df1.iloc[:, 1:df1.columns.to_list().index(ult_col)]
                df1['IND_ARQ'] = indice

                temp_table_name = f"temp_df_{indice}"
                final_table_name = f"Arq_{indice}"

                bd.register(temp_table_name, df1)
                bd.execute(f"CREATE OR REPLACE TABLE {final_table_name} AS SELECT * FROM {temp_table_name}")
                bd.unregister(temp_table_name)

                bd.execute("""
                    INSERT INTO controle_importacao (
                        nome_arquivo,
                        data_importacao,
                        dt_ini,
                        dt_fim,
                        cnpj,
                        tabela_destino,
                        indice_arquivo
                    )
                    VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)
                """, [arq, Dt_INI, Dt_FIM, Nr_CNPJ, final_table_name, indice])

            except Exception as e:
                try:
                    bd.unregister(temp_table_name)
                except:
                    pass
                st.error(f"Erro ao gravar {arq} no DuckDB: {e}")
                continue

        try:
            df_arq = bd.execute("""
                SELECT dt_ini AS Dt_INI,
                       dt_fim AS Dt_FIM,
                       cnpj AS CNPJ,
                       nome_arquivo AS Nm_Arq
                FROM controle_importacao
                ORDER BY dt_ini, nome_arquivo
            """).fetchdf()
        except:
            df_arq = pd.concat([df_arq_existente, df_novos], ignore_index=True)

        bd.register("temp_lst_arq", df_arq)
        bd.execute("CREATE OR REPLACE TABLE LST_ARQ AS SELECT * FROM temp_lst_arq")
        bd.unregister("temp_lst_arq")

        progresso.progress(100, text=f"Finalizada Importação de {SPED}!")

        if not df_novos.empty:
            st.success(f"{len(df_novos)} novo(s) arquivo(s) importado(s).")
        else:
            st.info("Nenhum novo arquivo foi importado.")

        return df_arq
    
def processa_arquivo(arq, dir_arq_SPED, SPED, index, total):
    arq_cam = os.path.join(dir_arq_SPED, arq)
    column_names = [f"COL_{i}" for i in range(40)]

    try:
        df = pd.read_csv(
            arq_cam, sep="|", decimal=',', on_bad_lines='skip',
            encoding="Latin-1", header=None, names=column_names,
            lineterminator='\n', dtype=str
        )

        if SPED == 'EFD_ICMS':
            Nr_CNPJ = df.iloc[0, 7]
            Dt_INI = datetime.strptime(df.iloc[0, 4], "%d%m%Y")
            Dt_FIM = datetime.strptime(df.iloc[0, 5], "%d%m%Y")
        elif SPED == "ECD":
            Nr_CNPJ = df.iloc[0, 6]
            Dt_INI = datetime.strptime(df.iloc[0, 3], "%d%m%Y")
            Dt_FIM = datetime.strptime(df.iloc[0, 4], "%d%m%Y")
        else:
            return None, None

        lst_BLC = df[df["COL_0"].isnull()]["COL_1"].drop_duplicates().to_list()
        df1 = df[df["COL_1"].isin(lst_BLC)].copy()
        ult_col = next((col for col in reversed(df1.columns) if df1[col].notna().any()), None)
        ult_idx = df1.columns.get_loc(ult_col) + 1
        df1 = df1.iloc[:, 1:ult_idx]
        df1['IND_ARQ'] = index

        return {
            'Dt_INI': Dt_INI, 'Dt_FIM': Dt_FIM,
            'CNPJ': Nr_CNPJ, 'Nm_Arq': arq, 'DF': df1
        }

    except Exception as e:
        st.error(f"[{index+1}/{total}] Erro no arquivo {arq}: {e}")
        return None


def imp_sped_duck1(dir_arq_SPED, dir_arq_base, SPED, empresa, ano):
    """
    Cria a base de dados vetorizado colunar, para SPED.
    """
    caminho_bd = os.path.join(dir_arq_base, f"{SPED}_{empresa}_{ano}.duckdb")

    if os.path.exists(caminho_bd):
        os.remove(caminho_bd)

    bd = duckdb.connect(caminho_bd)
    LST_ARQ = [f for f in os.listdir(dir_arq_SPED) if f.upper().endswith(".TXT")]

    df_arq = pd.DataFrame(columns=['Dt_INI', 'Dt_FIM', 'CNPJ', 'Nm_Arq'])
    progresso = st.progress(0, text="Iniciando importação...")

    resultados = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futuros = [executor.submit(processa_arquivo, arq, dir_arq_SPED, SPED, i, len(LST_ARQ)) for i, arq in enumerate(LST_ARQ)]
        for i, futuro in enumerate(futuros):
            resultado = futuro.result()
            progresso.progress((i+1) * 100 // len(LST_ARQ), text=f"[{i+1}/{len(LST_ARQ)}] Processado")
            if resultado:
                df_arq.loc[len(df_arq)] = [resultado['Dt_INI'], resultado['Dt_FIM'], resultado['CNPJ'], resultado['Nm_Arq']]
                tabela = resultado['DF']
                nm_tabela = f"Arq_{i}"
                bd.register("temp_tbl", tabela)
                bd.execute(f"CREATE OR REPLACE TABLE {nm_tabela} AS SELECT * FROM temp_tbl")
                bd.unregister("temp_tbl")

    # Salva metadados
    bd.register("temp_lst_arq", df_arq)
    bd.execute("CREATE OR REPLACE TABLE LST_ARQ AS SELECT * FROM temp_lst_arq")
    bd.unregister("temp_lst_arq")

    bd.close()
    progresso.progress(100, text=f"Finalizada Importação de {SPED}!")
    return df_arq

def imp_sped_duck3(dir_arq_SPED, dir_arq_base, SPED, empresa, ano, apagar_base=False):
    
    import tempfile
    caminho_bd = os.path.join(dir_arq_base, f"{SPED}_{empresa}_{ano}.duckdb")
    if apagar_base and os.path.exists(caminho_bd):
        os.remove(caminho_bd)
    with duckdb.connect(caminho_bd) as bd:

        bd.execute("""
                        CREATE TABLE IF NOT EXISTS controle_importacao (
                            nome_arquivo VARCHAR PRIMARY KEY,
                            data_importacao TIMESTAMP,
                            cnpj VARCHAR,
                            dt_ini VARCHAR,
                            dt_fim VARCHAR,
                            total_linhas_arquivo BIGINT,
                            total_linhas_tmp BIGINT,
                            total_linhas_final BIGINT,
                            importacao_ok BOOLEAN
                        )
                    """)
        arquivos_importados = set()
        try:
            result = bd.execute("SELECT nome_arquivo FROM controle_importacao").fetchall()
            arquivos_importados = {row[0] for row in result}
        except:
            pass

        arquivos_disponiveis = [f for f in os.listdir(dir_arq_SPED) if f.upper().endswith('.TXT')]
        arquivos_para_importar = [f for f in arquivos_disponiveis if f not in arquivos_importados]

        if not arquivos_para_importar:
            st.info("Todos os arquivos já foram importados anteriormente.")
            result = bd.execute("""
                                    SELECT dt_ini, dt_fim, cnpj, nome_arquivo,
                                        total_linhas_arquivo, total_linhas_tmp,
                                        total_linhas_final, importacao_ok
                                    FROM controle_importacao
                                """).fetchall()
            df = pd.DataFrame(result, columns=[
                                    'dt_ini', 'dt_fim', 'cnpj', 'nome_arq',
                                    'linhas_arquivo', 'linhas_tmp', 'linhas_final', 'importacao_ok'
                                ])
            for campo in ['dt_ini', 'dt_fim']:
                df[campo] = pd.to_datetime(df[campo], errors="coerce", format="%d%m%Y")
            return df
        
        progresso = st.progress(0, text="Iniciando importação...")
        metadados = []
        
        for idx, nome_arq in enumerate(arquivos_para_importar):
            caminho = os.path.join(dir_arq_SPED, nome_arq)
            progresso.progress(idx * 100 // len(arquivos_para_importar), 
                               text=f"Importando {idx+1}/{len(arquivos_para_importar)}: {nome_arq}")

            enc = "latin-1"
            with st.spinner(f"Limpando arquivo {nome_arq}."):
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8', errors='replace') as f_out:
                    arquivo_limpo = f_out.name       
                    with open(caminho, 'r', encoding=enc, errors='replace') as f_in:
                        total_linhas_arquivo = 0
                        for linha in f_in:
                            f_out.write(linha.replace('"', "").replace("'", ""))
                            total_linhas_arquivo += 1
                        
            tabela_tmp = f"tmp_arq_{idx}"
            tabela_raw = f"Arq_{idx}_raw"
            tabela_final = f"Arq_{idx}"

            with st.spinner(f"Detectando colunas {nome_arq}."):
                preview_query = f"""
                    SELECT * FROM read_csv_auto(
                        '{arquivo_limpo}',
                        delim='|',
                        header=False,
                        quote=NULL,
                        escape=NULL,
                        all_varchar=true,
                        strict_mode=false,
                        null_padding=true
                    )
                    LIMIT 1;
                """
                try:
                    df_preview = bd.execute(preview_query).fetchdf()
                    colunas_existentes = df_preview.columns.tolist()
                except Exception as e:
                    raise RuntimeError(f"Erro ao tentar inspecionar colunas do arquivo: {e}")

            with st.spinner(f"Carregando arquivo {nome_arq}."):
                selects = []
                for c in range(40):
                    col_name = f"column{str(c).zfill(2)}"
                    alias = f"COL_{c}"
                    selects.append(f"{col_name} AS {alias}" if col_name in colunas_existentes else f"NULL AS {alias}")

                nomes_colunas = ", ".join(selects)

                bd.execute(f"""
                                CREATE OR REPLACE TABLE {tabela_tmp} AS
                                SELECT {nomes_colunas},
                                    row_number() OVER () AS ordem
                                FROM read_csv_auto(
                                    '{arquivo_limpo}',
                                    delim='|',
                                    header=False,
                                    quote=NULL,
                                    escape=NULL,
                                    all_varchar=true,
                                    strict_mode=false,
                                    null_padding=true
                                );
                            """)
                total_linhas_tmp = bd.execute(f"SELECT COUNT(*) FROM {tabela_tmp}").fetchone()[0]
                resultado = bd.sql(f"SELECT * FROM {tabela_tmp}").fetchdf()
                if SPED == 'EFD_ICMS':
                    cnpj, dt_ini, dt_fim = bd.execute(
                        f"SELECT COL_7, COL_4, COL_5 FROM {tabela_tmp} LIMIT 1"
                    ).fetchone()
                elif SPED == 'ECD':
                    cnpj, dt_ini, dt_fim = bd.execute(
                        f"SELECT COL_6, COL_3, COL_4 FROM {tabela_tmp} LIMIT 1"
                    ).fetchone()
                else:
                    st.error(f"Tipo SPED inválido em {nome_arq}")
                    continue

                bd.execute(f"""
                            CREATE OR REPLACE TABLE {tabela_final} AS
                            SELECT *
                            FROM {tabela_tmp}
                            WHERE COL_1 IN (
                                SELECT DISTINCT COL_1
                                FROM {tabela_tmp}
                                WHERE COL_0 IS NULL
                            )
                            ORDER BY ordem;
                        """)
                total_linhas_final = bd.execute(f"SELECT COUNT(*) FROM {tabela_final}").fetchone()[0]
                importacao_ok = (total_linhas_arquivo == total_linhas_tmp)
                metadados.append((dt_ini, dt_fim, cnpj, nome_arq))

                bd.execute("""
                                INSERT OR REPLACE INTO controle_importacao (
                                    nome_arquivo, data_importacao, cnpj, dt_ini, dt_fim,
                                    total_linhas_arquivo, total_linhas_tmp, total_linhas_final, importacao_ok
                                )
                                VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                nome_arq, cnpj, dt_ini, dt_fim,
                                total_linhas_arquivo, total_linhas_tmp, total_linhas_final, importacao_ok
                            ))
                bd.execute(f"DROP TABLE IF EXISTS {tabela_tmp}")

            if os.path.exists(arquivo_limpo):
                os.remove(arquivo_limpo)

            st.success(f"Feito {nome_arq}.")
        
        result = bd.execute("""
                                SELECT dt_ini, dt_fim, cnpj, nome_arquivo,
                                    total_linhas_arquivo, total_linhas_tmp,
                                    total_linhas_final, importacao_ok
                                FROM controle_importacao
                            """).fetchall()

        df = pd.DataFrame(result, columns=[
                            'dt_ini', 'dt_fim', 'cnpj', 'nome_arq',
                            'linhas_arquivo', 'linhas_tmp', 'linhas_final', 'importacao_ok'
                        ])

        for campo in ['dt_ini', 'dt_fim']:
            df[campo] = pd.to_datetime(df[campo], errors="coerce", format="%d%m%Y")

        progresso.progress(100, text="Importação finalizada!")

        falhas = df[~df["importacao_ok"]]
        if not falhas.empty:
            st.warning(f"{len(falhas)} arquivo(s) com divergência entre linhas do arquivo e linhas importadas.")
            st.write(falhas)
        else:
            st.success("Todos os arquivos tiveram todas as linhas importadas.")

    return df


def df_to_duck(df, table_name, conn, if_exists="append"):
    conn.register("tmp_df", df)

    if if_exists == "replace":
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM tmp_df")
    else:
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM tmp_df")
        conn.execute(f"INSERT INTO {table_name} SELECT * FROM tmp_df")

def dataframe_vazio(colunas: list = None, tipo: str = None) -> pd.DataFrame:
    if colunas is None:
        colunas = []
    return pd.DataFrame(columns=colunas, dtype=tipo)

def tratar_erro(nome: str = None, mensagem: str = None, st=None, colunas = None, tipo = None):
    if nome is None:
        return
    if st is not None:
        st.error(mensagem)
        return dataframe_vazio(colunas, tipo)
    raise UserWarning(mensagem)

def imp_tbl_forma_001(nm_tbl: Optional[str] = None, SQLq: Optional[str] = None, con=None, st=None, Empresa=None) -> pd.DataFrame:
    if nm_tbl == None or con == None or Empresa == None:
        raise UserWarning("Erro por não informar tabela ou conexão ou empresa")
    try:
        dt_ARQ = max_arq(nm_tbl, con, Empresa)
        if dt_ARQ:
            if SQLq == None:
                SQLq = f"""
                    SELECT *
                    FROM {nm_tbl} t1 WHERE t1.dt_ARQ = ?
                    """
            df = pd.read_sql(SQLq, con, params=(dt_ARQ,))
            return df
        else:
            if st:
                st.error(f'Falha ao importar o arquivo {nm_tbl}, inexiste na base local indicada.')
                if SQLq:
                    colunas = colunas_sel(SQLq)
                    df = pd.DataFrame(columns=colunas)
                else:
                    df = pd.DataFrame()
                return df
            else:
                raise UserWarning(f'Falha ao importar o arquivo {nm_tbl}, inexiste na base local indicada.')
    except Exception as e:
        tratar_erro(nm_tbl, e, st)
        
def imp_tbl_forma_002(nm_tbl1: Optional[str] = None, nm_tbl2: Optional[str] = None,
                      SQLq: Optional[str] = None, con=None, st=None, Empresa=None) -> pd.DataFrame:
    if nm_tbl1 == None or nm_tbl2 == None or con == None or Empresa == None:
        raise UserWarning("Erro por não informar tabela(s) ou conexão ou empresa")
    try:
        dt_ARQ = max_arq(nm_tbl1, con, Empresa)
        dt_ARQ1 = max_arq(nm_tbl2, con, Empresa)
        if dt_ARQ:
            if SQLq == None:
                raise UserWarning("Consulta não é opcional")
            df = pd.read_sql(SQLq, con, params=(dt_ARQ, dt_ARQ1))
            return df
        else:
            if st:
                st.error(f'Falha ao importar o arquivo {nm_tbl1} ou {nm_tbl2}, inexiste na base local indicada.')
                return pd.DataFrame()
            else:
                raise UserWarning(f'Falha ao importar o arquivo {nm_tbl1} ou {nm_tbl2}, inexiste na base local indicada.')
    except Exception as e:
        tratar_erro(nm_tbl1, e, st)


import duckdb
import pandas as pd
import sqlite3
from typing import Optional

def imp_tbl_forma_002dk(nm_tbl1: Optional[str] = None, nm_tbl2: Optional[str] = None, SQLq: Optional[str] = None,
    con=None, st=None, Empresa=None) -> pd.DataFrame:

    if any(x is None for x in (nm_tbl1, nm_tbl2, con, Empresa)):
        raise UserWarning("Erro por não informar tabela(s), conexão ou empresa")

    try:
        dt_ARQ = max_arq(nm_tbl1, con, Empresa)
        dt_ARQ1 = max_arq(nm_tbl2, con, Empresa)

        if dt_ARQ is None or dt_ARQ1 is None:
            raise UserWarning(f"Arquivo {nm_tbl1} ou {nm_tbl2} inexistente.")

        if SQLq is None:
            raise UserWarning("Consulta não é opcional")

        caminho = con.execute("PRAGMA database_list").fetchone()[2]

        if not caminho:
            raise ValueError("Banco SQLite sem caminho de arquivo.")
        con.commit()
        with duckdb.connect(database=":memory:") as db:
            db.execute("INSTALL sqlite")
            db.execute("LOAD sqlite")
            caminho_sql = caminho.replace("'", "''")
            db.execute(f"ATTACH '{caminho_sql}' AS origem (TYPE SQLITE, READ_ONLY)")
            df = db.execute(SQLq, [dt_ARQ, dt_ARQ1]).df()

        return df

    except Exception as e:
        tratar_erro(nm_tbl1, e, st)
        return pd.DataFrame()
    
def imp_tbl_forma_003(param = [],
                      SQLq: Optional[str] = None, 
                      con=None, 
                      st=None, 
                      Empresa=None,
                      FLG_ERRO = True) -> pd.DataFrame:
    if not Empresa:
        raise UserWarning("Empresa não informada.")

    if not param:
        raise UserWarning("Tabela(s) não informada(s).")

    if con is None:
        raise UserWarning("Conexão não informada.")

    if SQLq is None:
        raise UserWarning("Consulta não informada.")
    
    
    dd_tpl = tuple(max_arq(p, con, Empresa) for p in param)
    if any(v is None for v in dd_tpl) and not FLG_ERRO:
        faltantes = [
                        tabela for tabela, dt_arq in zip(param, dd_tpl)
                        if dt_arq is None
                    ]

        msg = (
                    "Falha ao importar arquivo(s). "
                    f"Inexistente(s) na base local: {', '.join(faltantes)}."
                )

        if st:
            st.error(msg)
            return pd.DataFrame()

        raise UserWarning(msg)
    
    qtd_placeholders = SQLq.count("?")

    if qtd_placeholders != len(dd_tpl):
        raise ValueError(
                            f"Quantidade de parâmetros incompatível com a SQL: "
                            f"a consulta possui {qtd_placeholders} placeholder(s), "
                            f"mas foram gerado(s) {len(dd_tpl)} parâmetro(s): {param}."
                        )
    return pd.read_sql(SQLq, con, params=dd_tpl)

        
def imp_tbl_forma_000(nm_tbl: Optional[str] = None, SQLq: Optional[str] = None, 
                      con=None, st=None, lst_cnv=[], workbook = None) -> pd.DataFrame:
    if nm_tbl == None or con == None:
        raise UserWarning("Erro por não informar tabela ou conexão")
    try:
        if existe_tabela(nm_tbl, con):
            if SQLq == None:
                SQLq = f"""
                    SELECT *
                    FROM {nm_tbl} 
                    """
            df = pd.read_sql(SQLq, con)
            for n in lst_cnv:
                if (n in df.columns) and (df[n].dtype == 'object'):
                    df[n] = pd.to_numeric(df[n].astype(str).str.replace(',','.'), 
                                                                errors='coerce',
                                                                downcast='float')
            return df
        else:
            if st:
                if workbook: workbook.close()
                st.error(f'Falha ao importar o arquivo {nm_tbl}, inexiste na base local indicada.')
                return pd.DataFrame()
            else:
                raise UserWarning(f'Falha ao importar o arquivo {nm_tbl}, inexiste na base local indicada.')
    except Exception as e:
        tratar_erro('nm_tbl', e, st)
        
def _limpar_arquivo_em_chunks(origem, destino, encoding="latin-1", chunk_size=8 * 1024 * 1024):
    tabela = str.maketrans("", "", "\"'")
    with open(origem, "r", encoding=encoding, errors="replace") as f_in, \
         open(destino, "w", encoding="utf-8", errors="replace") as f_out:
        while True:
            bloco = f_in.read(chunk_size)
            if not bloco:
                break
            f_out.write(bloco.translate(tabela))


def imp_sped_duck3v20(dir_arq_SPED, dir_arq_base, SPED, empresa, ano):
    caminho_bd = os.path.join(dir_arq_base, f"{SPED}_{empresa}_{ano}.duckdb")

    if os.path.exists(caminho_bd):
        os.remove(caminho_bd)

    arquivos = sorted(
                        f for f in os.listdir(dir_arq_SPED)
                        if f.upper().endswith(".TXT")
                    )

    if not arquivos:
        return pd.DataFrame(columns=["dt_ini", "dt_fim", "cnpj", "nome_arq"])

    total_colunas = 40
    colunas_duck = {f"column{str(i).zfill(2)}": "VARCHAR" for i in range(total_colunas)}

    metadados = []
    progresso = st.progress(0, text="Iniciando importação...")

    with duckdb.connect(caminho_bd) as bd:
        bd.execute("PRAGMA threads = 4")
        bd.execute("PRAGMA enable_progress_bar = false")

        for idx, nome_arq in enumerate(arquivos):
            caminho_origem = os.path.join(dir_arq_SPED, nome_arq)
            tabela_tmp = f"tmp_arq_{idx}"
            tabela_final = f"Arq_{idx}"

            progresso.progress(
                                    idx * 100 // len(arquivos),
                                    text=f"Importando {idx + 1}/{len(arquivos)}: {nome_arq}"
                                )

            with tempfile.NamedTemporaryFile(
                                                mode="w",
                                                delete=False,
                                                suffix=".csv",
                                                encoding="utf-8"
                                            ) as f_tmp:
                arquivo_limpo = f_tmp.name

            try:
                with st.spinner(f"Limpando arquivo {nome_arq}..."):
                    _limpar_arquivo_em_chunks(caminho_origem, arquivo_limpo, encoding="latin-1")

                with st.spinner(f"Carregando arquivo {nome_arq} no DuckDB..."):

                    bd.execute(f"""
                        CREATE OR REPLACE TABLE {tabela_tmp} AS
                        SELECT
                            column00 AS COL_0,
                            column01 AS COL_1,
                            column02 AS COL_2,
                            column03 AS COL_3,
                            column04 AS COL_4,
                            column05 AS COL_5,
                            column06 AS COL_6,
                            column07 AS COL_7,
                            column08 AS COL_8,
                            column09 AS COL_9,
                            column10 AS COL_10,
                            column11 AS COL_11,
                            column12 AS COL_12,
                            column13 AS COL_13,
                            column14 AS COL_14,
                            column15 AS COL_15,
                            column16 AS COL_16,
                            column17 AS COL_17,
                            column18 AS COL_18,
                            column19 AS COL_19,
                            column20 AS COL_20,
                            column21 AS COL_21,
                            column22 AS COL_22,
                            column23 AS COL_23,
                            column24 AS COL_24,
                            column25 AS COL_25,
                            column26 AS COL_26,
                            column27 AS COL_27,
                            column28 AS COL_28,
                            column29 AS COL_29,
                            column30 AS COL_30,
                            column31 AS COL_31,
                            column32 AS COL_32,
                            column33 AS COL_33,
                            column34 AS COL_34,
                            column35 AS COL_35,
                            column36 AS COL_36,
                            column37 AS COL_37,
                            column38 AS COL_38,
                            column39 AS COL_39,
                            row_number() OVER () AS ordem
                        FROM read_csv(
                            '{arquivo_limpo}',
                            delim='|',
                            header=false,
                            columns={colunas_duck},
                            header=False,
                            quote=NULL,
                            escape=NULL,
                            all_varchar=true,
                            strict_mode=false,
                            null_padding=true
                        );
                    """)

                with st.spinner(f"Extraindo metadados de {nome_arq}..."):
                    if SPED == "EFD_ICMS":
                        sql_meta = f"""
                                        SELECT COL_7, COL_4, COL_5
                                        FROM {tabela_tmp}
                                        LIMIT 1
                                    """
                    elif SPED == "ECD":
                        sql_meta = f"""
                                        SELECT COL_6, COL_3, COL_4
                                        FROM {tabela_tmp}
                                        LIMIT 1
                                    """
                    else:
                        st.error(f"Tipo SPED inválido em {nome_arq}")
                        bd.execute(f"DROP TABLE IF EXISTS {tabela_tmp}")
                        continue

                    resultado = bd.execute(sql_meta).fetchone()
                    cnpj, dt_ini, dt_fim = resultado if resultado else (None, None, None)

                with st.spinner(f"Filtrando registros válidos de {nome_arq}..."):
                    bd.execute(f"""
                                    CREATE OR REPLACE TABLE {tabela_final} AS
                                    SELECT t.*
                                    FROM {tabela_tmp} t
                                    SEMI JOIN (
                                        SELECT DISTINCT COL_1
                                        FROM {tabela_tmp}
                                        WHERE COL_0 IS NULL
                                    ) v
                                    ON t.COL_1 = v.COL_1
                                    ORDER BY t.ordem
                                """)

                bd.execute(f"DROP TABLE IF EXISTS {tabela_tmp}")
                metadados.append((dt_ini, dt_fim, cnpj, nome_arq))

            finally:
                if os.path.exists(arquivo_limpo):
                    os.remove(arquivo_limpo)

        bd.execute("""
                        CREATE OR REPLACE TABLE LST_ARQ (
                            Dt_INI VARCHAR,
                            Dt_FIM VARCHAR,
                            CNPJ VARCHAR,
                            Nm_Arq VARCHAR
                        )
                    """)

        if metadados:
            df_meta = pd.DataFrame(
                                        metadados,
                                        columns=["Dt_INI", "Dt_FIM", "CNPJ", "Nm_Arq"]
                                    )
            bd.register("tmp_lst_arq_df", df_meta)
            bd.execute("INSERT INTO LST_ARQ SELECT * FROM tmp_lst_arq_df")
            bd.unregister("tmp_lst_arq_df")

        progresso.progress(100, text="Importação finalizada!")

    df = pd.DataFrame(metadados, columns=["dt_ini", "dt_fim", "cnpj", "nome_arq"])
    if not df.empty:
        df["dt_ini"] = pd.to_datetime(df["dt_ini"], errors="coerce", format="%d%m%Y")
        df["dt_fim"] = pd.to_datetime(df["dt_fim"], errors="coerce", format="%d%m%Y")

    return df
        
def listar_tabelas(conn, db_type='sqlite'):
    if db_type == "sqlite":
        query = """
        SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name;
        """
    elif db_type == "duckdb":
        query = "SHOW TABLES;"
    else:
        raise ValueError("Banco não suportado")

    return [row[0] for row in conn.execute(query).fetchall()]

@st.cache_data(ttl=3600, show_spinner="Buscando e colocando em cache os dados...")
def carga_sqlite_cache(SQLq = None, _bd = None, parametros = None):
    if parametros == None:
        df = pd.read_sql(SQLq, _bd)
    else:
        df = pd.read_sql(SQLq, _bd, params=parametros)
    return df