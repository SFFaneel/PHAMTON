from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import pandas as pd
import streamlit as st

import UTILS.dados_bulldozer as bull
import VALIDADOR.validador_funcoes as VAL
from UTILS import (
                    criar_tabela, 
                    sanear_csv, 
                    existe_tabela,
                    determinar_tipo, 
                    converter_decimal,
                    bsc_dados_reg
                   )

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

PADRAO = re.compile(r"^(.+)_(\d{5})_(\d{8})\.csv$", re.IGNORECASE)

@dataclass
class ResultadoImportacao:
    importados: int = 0
    reprovados: list[str] = field(default_factory=list)
    linhas: int = 0

def _identificar(arquivo: Path) -> tuple[str, str, str]:
    match = PADRAO.fullmatch(arquivo.name)
    if match is None:
        raise ValueError("Nome inválido: esperado NOME_12345_YYYYMMDD.csv")
    from datetime import datetime
    tabela, empresa, data = match.groups()
    datetime.strptime(data, "%Y%m%d")
    return tabela, empresa, data

def _identificador_sql(nome: str) -> str:
    return "'" + nome.replace('"', '""') + "'"

@rastrear_funcao
def importar_csv(
                    arquivo: Path,
                    bd: sqlite3.Connection,
                    *,
                    sanear_csv: Callable,
                    determinar_tipo: Callable,
                    converter_decimal: Callable,
                    progresso: Callable[[str], None] | None = None,
                    chunksize: int = 250_000,
                ) -> int:

    tabela, empresa, data = _identificar(arquivo)
    
    colunas = pd.read_csv(arquivo, nrows=0, sep="|", encoding="Latin-1", dtype=str).columns.tolist()
    if not colunas:
        raise ValueError("Arquivo CSV sem cabeçalho")
    if len(colunas) != len(set(colunas)):
        raise ValueError("Cabeçalho com colunas duplicadas")
    if any(c in {"Cd_Emp", "dt_ARQ"} for c in colunas):
        raise ValueError("Cabeçalho contém coluna reservada: Cd_Emp ou dt_ARQ")

    tipos = {c: determinar_tipo(c) for c in colunas}
    conversores = {c: converter_decimal for c, tipo in tipos.items() if tipo == "float"}
    dtypes = {c: tipo for c, tipo in tipos.items() if tipo not in ("date", "float")}
    datas = [c for c, tipo in tipos.items() if tipo == "date"]
    tabela_sql = _identificador_sql(tabela)
    total = 0

    bd.execute("SAVEPOINT importacao_arquivo")
    try:
        existe = bd.execute(
                                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (tabela,)
                            ).fetchone() is not None
        if existe:
            info = bd.execute(f"PRAGMA table_info({tabela_sql})").fetchall()
            atuais = {row[1] for row in info}
            if not {"Cd_Emp", "dt_ARQ"}.issubset(atuais):
                raise ValueError(f"Tabela {tabela} sem colunas Cd_Emp/dt_ARQ")
            bd.execute(f"DELETE FROM {tabela_sql} WHERE Cd_Emp=? AND dt_ARQ=?", (empresa, data))

        reader = pd.read_csv(
                                arquivo, sep="|", encoding="Latin-1", decimal=",",
                                dtype=dtypes, converters=conversores, parse_dates=datas,
                                date_format="%Y/%m/%d", chunksize=chunksize,
                                engine="python", on_bad_lines="error",
                            )
        for numero, chunk in enumerate(reader, start=1):
            chunk["Cd_Emp"] = empresa
            chunk["dt_ARQ"] = data
            if not existe:
                cols = ", ".join(
                                    f'"{coluna}" TEXT'
                                    for coluna in chunk.columns
                                )

                bd.execute(f'CREATE TABLE IF NOT EXISTS {tabela_sql} ({cols})')
                existe = True
            atuais = {row[1] for row in bd.execute(f"PRAGMA table_info({tabela_sql})")}
            for coluna in chunk.columns:
                if coluna not in atuais:
                    bd.execute(f"ALTER TABLE {tabela_sql} ADD COLUMN {_identificador_sql(coluna)} TEXT")
            for coluna in datas:
                if coluna in chunk.columns:
                    chunk[coluna] = (
                                        pd.to_datetime(
                                            chunk[coluna],
                                            format="%Y/%m/%d",
                                            errors="coerce"
                                        )
                                        .dt.strftime("%Y-%m-%d")
                                    )
            chunk = chunk.astype(object).where(pd.notna(chunk), None)
            cols_sql = ", ".join(_identificador_sql(c) for c in chunk.columns)
            marcadores = ", ".join("?" for _ in chunk.columns)
            sql = f"INSERT INTO {tabela_sql} ({cols_sql}) VALUES ({marcadores})"
            bd.executemany(sql, chunk.itertuples(index=False, name=None))
            total += len(chunk)
            if progresso:
                progresso(f"{arquivo.name}: lote {numero} — {total:,} linhas")
        bd.execute("RELEASE SAVEPOINT importacao_arquivo")
        return total
    except Exception:
        bd.execute("ROLLBACK TO SAVEPOINT importacao_arquivo")
        bd.execute("RELEASE SAVEPOINT importacao_arquivo")
        raise

def preparar_tabelas(bd):
    criar_tabela("II_MCPSE", bull.dic_ATR_TNS_II_MCPSE, bd)
    criar_tabela("IIIA_MCPSE", bull.dic_ATR_POT_IIIA_MCPSE, bd)
    criar_tabela("IIIB_MCPSE", bull.dic_ATR_POT_IIIB_MCPSE, bd)
    criar_tabela("IV_MCPSE", bull.dic_ATR_NrFases_IV_MCPSE, bd)
    criar_tabela("V_MCPSE", bull.dic_ATR_COR_IV_MCPSE, bd)
    criar_tabela("VI_MCPSE", bull.dic_ATR_TPCONTROLE_VI_MCPSE, bd)
    criar_tabela("VII_MCPSE", bull.dic_ATR_TPISOLAMENTO_VII_MCPSE, bd)
    criar_tabela("VIII_MCPSE", bull.dic_ATR_BITOLA_VIII_MCPSE, bd)
    criar_tabela("IX_MCPSE", bull.dic_ATR_ALTURA_IX_MCPSE, bd)
    criar_tabela("X_MCPSE", bull.dic_ATR_ESFORCO_X_MCPSE, bd)
    criar_tabela("XI_MCPSE", bull.dic_ATR_RELT_XI_MCPSE, bd)
    criar_tabela("XII_MCPSE", bull.dic_ATR_RELC_XII_MCPSE, bd)
    criar_tabela("XIII_MCPSE", bull.dic_ATR_CLSE_XIII_MCPSE, bd)
    criar_tabela("XIV_MCPSE", bull.dic_ATR_RELT_XIV_MCPSE, bd)
    criar_tabela("XV_MCPSE", bull.dic_ATR_COR_XV_MCPSE, bd)

    criar_tabela(
                    "tbl_CFOP",
                    [(item.value[0], item.value[1]) for item in VAL.ValoresCFOP],
                    bd,
                    ["CFOP", "Txt_DESC"],
                )

    criar_tabela(
                    "tbl_TPSERV",
                    [(item.name, item.value) for item in VAL.ValoresTPSERV],
                    bd,
                    ["TP_SERV", "Txt_DESC"],
                )

    criar_tabela(
                    "tbl_RACCOM",
                    [(item.name, item.value) for item in VAL.ValoresRACCOM],
                    bd,
                    ["Nm_Variavel", "Txt_DESC"],
                )

    criar_tabela(
                    "tbl_TUC",
                    [(item.value[0], item.value[1]) for item in VAL.ValoresTUC],
                    bd,
                    ["Nr_TUC", "Txt_DESC"],
                )

    criar_tabela(
                    "tbl_TI",
                    [(item.name, item.value) for item in VAL.ValoresTI],
                    bd,
                    ["Nr_TI", "Txt_DESC"],
                )

    criar_tabela(
                    "tbl_CCOE",
                    [(item.value[0], item.value[1]) for item in VAL.ValoresCCOE],
                    bd,
                    ["Cd_CC", "Txt_DESC"],
                )

    criar_tabela(
                    "tbl_CC",
                    [
                        tuple(item.value[0][:7])
                        for item in VAL.ValoresCC
                    ],
                    bd,
                    [
                        "Cd_CC", "Txt_VAR1", "Txt_VAR2", "Txt_VAR3",
                        "TP_ATIVO", "Cd_5", "Txt_VAR4"
                    ],
                )

def executar_importacao(
                            *,
                            local: str | Path,
                            empresa: str,
                            ano: int,
                            sanear_csv: Callable,
                            determinar_tipo: Callable,
                            converter_decimal: Callable,
                            preparar_tabelas: Callable[[sqlite3.Connection], None] | None = None,
                            progresso: Callable[[str], None] | None = None,
                        ) -> ResultadoImportacao:
    raiz = Path(local)
    caminho_manifesto = raiz / "MANIFESTO" / "TRILHA_EXEC" / "execucoes.db"
    caminho_manifesto.parent.mkdir(parents=True, exist_ok=True)
    inicializa_database(str(caminho_manifesto))
    inicializa_detalhes(str(caminho_manifesto))
    inicializar_rastreamento(str(caminho_manifesto))

    origem = raiz / "DADOS_BRUTOS_MANUAL"
    destino = raiz / "BD_LOCAL" / f"{empresa}_{ano}.db"
    with sqlite3.connect(str(destino)) as bd:
        bd.execute("PRAGMA foreign_keys = ON")

    if not origem.is_dir():
        raise FileNotFoundError(f"Diretório de CSVs não encontrado: {origem}")
    if not destino.is_file():
        raise FileNotFoundError(f"Banco de destino não encontrado: {destino}")

    arquivos = sorted(p for p in origem.iterdir() if p.is_file()
                      and p.suffix.lower() == ".csv" and not p.name.upper().startswith("IPCA"))
    resultado = ResultadoImportacao()
    database = str(caminho_manifesto)
    with execucao_trilha(
                            db_path=database, script_nome="Importação Manual de Dados SFF",
                            parametros={"empresa": empresa, "ano": ano, "arquivos": len(arquivos)},
                         ) as execucao_id:

        registrar_evento(database, execucao_id, "IMPORTACAO_INICIADA",
                         mensagem=f"Iniciando importação de {len(arquivos)} arquivo(s)")
        with sqlite3.connect(destino) as bd:
            if preparar_tabelas:
                preparar_tabelas(bd)
                bd.commit()
            for indice, arquivo in enumerate(arquivos, start=1):
                if progresso:
                    progresso(f"Arquivo {indice}/{len(arquivos)}: {arquivo.name}")
                try:
                    _identificar(arquivo)
                    linhas = importar_csv(
                                            arquivo, bd, sanear_csv=sanear_csv,
                                            determinar_tipo=determinar_tipo,
                                            converter_decimal=converter_decimal, progresso=progresso,
                                            )
                    bd.commit()
                except Exception as exc:
                    bd.rollback()
                    resultado.reprovados.append(arquivo.name)
                    registrar_evento(database, execucao_id, "ARQUIVO_REPROVADO",
                                     mensagem=f"{arquivo.name}: {exc}", nivel="ERRO",
                                     detalhes={"arquivo": arquivo.name, "erro": str(exc)})
                    st.error(f"{arquivo.name}: {exc}")
                    continue
                resultado.importados += 1
                resultado.linhas += linhas
                registrar_evento(database, execucao_id, "ARQUIVO_IMPORTADO",
                                 mensagem=f"{arquivo.name}: {linhas} linha(s)")
                registrar_artefato(database, execucao_id, str(arquivo), "ENTRADA")

        for nome, valor, unidade in (
                                        ("arquivos_importados", resultado.importados, "arquivos"),
                                        ("arquivos_reprovados", len(resultado.reprovados), "arquivos"),
                                        ("linhas_importadas", resultado.linhas, "linhas"),
                                    ):
            registrar_metrica(database, execucao_id, nome, valor, unidade)
        registrar_evento(database, execucao_id, "IMPORTACAO_CONCLUIDA",
                         mensagem=f"Importados: {resultado.importados}; reprovados: {len(resultado.reprovados)}")
    return resultado

@st.fragment
def imp_arq(
                            *, sanear_csv: Callable, determinar_tipo: Callable,
                            converter_decimal: Callable,
                            preparar_tabelas: Callable[[sqlite3.Connection], None] | None = None,
                        ) -> None:
    if "tra_dir" not in st.session_state:
        st.warning("Configure o diretório de trabalho antes de importar.")
        return
    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
    st.html(f"<style>{css}</style>")

    with st.container():
        col1 = st.columns([1,5,1], gap='small')
        with col1[1]:
            st.html("<h1>Importação dos arquivos do Manual de Dados da SFF</h1>")
            st.html("""
                            <p  style="text-align: justify;text-indent: 40px">
                            Nesta etapa, carregamos 
                            os Arquivos CSV do Manual de Dados na base local.
                            É relevante que tenha sido processada a etapa de validação 
                            dos arquivos, pois alguns dos
                            erros podem provocar problemas na importação.</p>
                        """)
            col2 = st.columns(5, gap='small')
            with col2[2]:
                importar = st.button("Importar")
            if importar:
                progresso = st.empty()
                try:
                    with st.spinner("Importando arquivos..."):
                        resultado = executar_importacao(
                                                            local=local, empresa=empresa, ano=ano,
                                                            sanear_csv=sanear_csv,
                                                            determinar_tipo=determinar_tipo,
                                                            converter_decimal=converter_decimal,
                                                            preparar_tabelas=preparar_tabelas,
                                                            progresso=progresso.info,
                                                        )
                        raiz = criar_manifesto()
                except Exception as exc:
                    raise  UserWarning((f"Falha técnica na importação: {exc}"))
                else:
                    progresso.empty()
                    st.success(f"{resultado.importados} arquivo(s) importado(s); {resultado.linhas} linha(s).")
                    if resultado.reprovados:
                        st.warning(f"{len(resultado.reprovados)} arquivo(s) reprovado(s).")
                        st.dataframe(pd.DataFrame({"Arquivo reprovado": resultado.reprovados}), hide_index=True)

def imp_arq_dados():
    imp_arq(
                            sanear_csv=sanear_csv,
                            determinar_tipo=determinar_tipo,
                            converter_decimal=converter_decimal,
                            preparar_tabelas=preparar_tabelas,
                        )
    