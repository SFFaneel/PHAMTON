from __future__ import annotations

import getpass
import json
import socket
import sqlite3
import traceback
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from .manifesto_exec_detalhes import contexto_rastreamento


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")

@contextmanager
def _connect(
                db_path: sqlite3.Connection | str | Path,
            ) -> Iterator[sqlite3.Connection]:

    if isinstance(db_path, sqlite3.Connection):
        yield db_path
        return

    if not isinstance(db_path, (str, Path)):
        raise TypeError(
                            "db_path deve ser str, Path ou sqlite3.Connection"
                        )

    path = Path(db_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path), timeout=30)

    try:
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.execute("PRAGMA foreign_keys = ON")

        yield conn
        conn.commit()

    except BaseException:
        conn.rollback()
        raise

    finally:
        conn.close()
    
def inicializa_database(db_path: sqlite3.Connection | str | Path) -> None:
    with _connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tbl_manifesto_execucao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execucao_id TEXT NOT NULL UNIQUE,
                script_nome TEXT NOT NULL,
                script_versao TEXT NOT NULL,
                executado_por TEXT NOT NULL,
                hostname TEXT,
                iniciado_em TEXT NOT NULL,
                finalizado_em TEXT,
                estado TEXT NOT NULL CHECK(estado IN ('RODANDO','SUCESSO','FALHA')),
                erro_tipo TEXT,
                erro_mensagem TEXT,
                erro_rastreamento TEXT,
                parametros TEXT CHECK(parametros IS NULL OR json_valid(parametros)),
                CHECK(estado = 'RODANDO' OR finalizado_em IS NOT NULL),
                CHECK(estado != 'FALHA' OR erro_mensagem IS NOT NULL)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_manifesto_script ON tbl_manifesto_execucao(script_nome, iniciado_em)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_manifesto_estado ON tbl_manifesto_execucao(estado, iniciado_em)")


def inicio_execucao(
                        db_path: sqlite3.Connection | str | Path,
                        script_nome: str,
                        script_versao: str = "1.0.0",
                        parametros: Any = None,
                    ) -> str:

    if not script_nome or not script_nome.strip():
        raise ValueError("script_nome é obrigatório")
    if not script_versao or not script_versao.strip():
        raise ValueError("script_versao é obrigatório")
    params_json = json.dumps(parametros, ensure_ascii=False, allow_nan=False) if parametros is not None else None
    inicializa_database(db_path)
    execucao_id  = str(uuid.uuid4())
    with _connect(db_path) as conn:
        conn.execute("""
            INSERT INTO tbl_manifesto_execucao (
                execucao_id, script_nome, script_versao, executado_por,
                hostname, iniciado_em, estado, parametros
            ) VALUES (?, ?, ?, ?, ?, ?, 'RODANDO', ?)
        """, (execucao_id, script_nome, script_versao,
              getpass.getuser(), socket.gethostname(), _utc_now(), params_json))
    return execucao_id


def execucao_finalizada(
                            db_path: sqlite3.Connection | str | Path,
                            execucao_id: str,
                            sucesso: bool = True,
                            erro: BaseException | str | None = None,
                        ) -> None:
    
    if not sucesso and erro is None:
        raise ValueError("Uma falha precisa conter um erro")
    erro_tipo = erro_mensagem = erro_rastreamento = None
    if not sucesso:
        if isinstance(erro, BaseException):
            erro_tipo = type(erro).__name__
            erro_mensagem = str(erro) or erro_tipo
            erro_rastreamento = "".join(traceback.format_exception(type(erro), erro, erro.__traceback__))
        else:
            erro_tipo = "Falha Manual"
            erro_mensagem = str(erro) or "Falha não especificada"
    with _connect(db_path) as conn:
        cursor = conn.execute("""
            UPDATE tbl_manifesto_execucao
               SET finalizado_em = ?, estado = ?, erro_tipo = ?,
                   erro_mensagem = ?, erro_rastreamento = ?
             WHERE execucao_id = ? AND estado = 'RODANDO'
        """, (_utc_now(), "SUCESSO" if sucesso else "FALHA",
              erro_tipo, erro_mensagem, erro_rastreamento, execucao_id))
        if cursor.rowcount != 1:
            raise ValueError(f"Execução inexistente ou já finalizada: {execucao_id}")


@contextmanager
def execucao_trilha(
                        db_path: sqlite3.Connection | str | Path,
                        script_nome: str,
                        script_versao: str = "1.0.0",
                        parametros: Any = None,
                    ) -> Iterator[str]:


    execucao_id = inicio_execucao(
                                    db_path,
                                    script_nome,
                                    script_versao,
                                    parametros,
                                )

    try:
        with contexto_rastreamento(db_path, execucao_id):
            yield execucao_id

    except BaseException as exc:
        try:
            execucao_finalizada(
                                    db_path,
                                    execucao_id,
                                    sucesso=False,
                                    erro=exc,
                                )
        except Exception as erro_auditoria:
            exc.add_note(
                            "Não foi possível registrar a falha "
                            f"no manifesto: {erro_auditoria}"
                        )
        raise

    else:
        execucao_finalizada(
                                db_path,
                                execucao_id,
                                sucesso=True,
                            )


def busca_execucao(db_path: sqlite3.Connection | str | Path, execucao_id : str) -> dict[str, Any] | None:

    inicializa_database(db_path)
    with _connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM tbl_manifesto_execucao WHERE execucao_id  = ?", (execucao_id ,)).fetchone()
        return dict(row) if row is not None else None


def lista_execucoes(
                        db_path: sqlite3.Connection | str | Path,
                        script_nome: str | None = None,
                        estado: str | None = None,
                        limite: int = 100,
                    ) -> list[dict[str, Any]]:
  
    if not isinstance(limite, int) or isinstance(limite, bool) or limite < 1:
        raise ValueError("limite deve ser um inteiro positivo")
    if estado is not None and estado not in ("RODANDO", "SUCESSO", "FALHA"):
        raise ValueError("estado inválido")
    inicializa_database(db_path)
    sql = "SELECT * FROM tbl_manifesto_execucao WHERE 1=1"
    args: list[Any] = []
    if script_nome is not None:
        sql += " AND script_nome = ?"
        args.append(script_nome)
    if estado is not None:
        sql += " AND estado = ?"
        args.append(estado)
    sql += " ORDER BY iniciado_em DESC, id DESC LIMIT ?"
    args.append(limite)
    with _connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(sql, args).fetchall()]


def busca_log_execucao(execucao_id : str, name: str = "execucao"):

    import logging

    if not execucao_id  or not execucao_id .strip():
        raise ValueError("execucao_id  é obrigatório")
    return logging.LoggerAdapter(logging.getLogger(name), {"execucao_id ": execucao_id })