from __future__ import annotations

import hashlib, zipfile
import functools
import time
import traceback
import json
import math
import sqlite3
from contextlib import contextmanager
from contextvars import ContextVar
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Any, Callable, TypeVar
from uuid import uuid4

Database = str | Path | sqlite3.Connection
F = TypeVar('F', bound=Callable[..., Any])
_contexto: ContextVar[tuple[str, str] | None] = ContextVar('validador_execucao', default=None)
_chamada: ContextVar[str | None] = ContextVar('validador_chamada', default=None)

def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()

def caminho_auditoria(database: sqlite3.Connection | str | Path) -> str:
    if isinstance(database, sqlite3.Connection):
        rows = database.execute('PRAGMA database_list').fetchall()
        main = next((r[2] for r in rows if r[1] == 'main'), '')
        if not main:
            raise ValueError('Conexão em memória não suporta auditoria independente; forneça um caminho SQLite.')
        return str(Path(main).resolve())
    if isinstance(database, (str, Path)):
        path = str(database)
        if path == ':memory:' or path.startswith('file:'):
            raise ValueError('Use um caminho de arquivo SQLite, não URI ou :memory:, para auditoria independente.')
        return str(Path(path).expanduser().resolve())
    raise TypeError('Database deve ser str, pathlib.Path ou sqlite3.Connection')

@contextmanager
def _conexao(database: Database) -> Iterator[sqlite3.Connection]:
    if isinstance(database, sqlite3.Connection):
        yield database
    elif isinstance(database, str):
        if not database:
            raise ValueError('Database não pode ser vazio')
        conn = sqlite3.connect(database, timeout=30)
        try:
            conn.execute('PRAGMA foreign_keys = ON')
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        raise TypeError('Database deve ser str ou sqlite3.Connection')

_SCHEMA = """
                CREATE TABLE IF NOT EXISTS tbl_execucao_eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execucao_id TEXT NOT NULL,
                    criado_em TEXT NOT NULL,
                    nivel TEXT NOT NULL CHECK(nivel IN ('DEBUG','INFO','ALERTA','ERRO','CRITICO')),
                    nome_evento TEXT NOT NULL,
                    mensagem TEXT,
                    detalhes TEXT CHECK(detalhes IS NULL OR json_valid(detalhes)),
                    FOREIGN KEY(execucao_id) REFERENCES tbl_manifesto_execucao(execucao_id)
                );
                CREATE TABLE IF NOT EXISTS tbl_execucao_metricas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execucao_id TEXT NOT NULL,
                    criado_em TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    valor REAL NOT NULL,
                    unidade TEXT,
                    FOREIGN KEY(execucao_id) REFERENCES tbl_manifesto_execucao(execucao_id)
                );
                CREATE TABLE IF NOT EXISTS tbl_execucao_artefatos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execucao_id TEXT NOT NULL,
                    criado_em TEXT NOT NULL,
                    tipo_artefato TEXT NOT NULL CHECK(tipo_artefato IN ('ENTRADA','SAIDA')),
                    file_path TEXT NOT NULL,
                    sha256 TEXT,
                    size_bytes INTEGER CHECK(size_bytes IS NULL OR size_bytes >= 0),
                    FOREIGN KEY(execucao_id) REFERENCES tbl_manifesto_execucao(execucao_id)
                );
                CREATE INDEX IF NOT EXISTS idx_eventos_execucao ON tbl_execucao_eventos(execucao_id,criado_em);
                CREATE INDEX IF NOT EXISTS idx_metricas_execucao ON tbl_execucao_metricas(execucao_id,nome);
                CREATE INDEX IF NOT EXISTS idx_artefatos_execucao ON tbl_execucao_artefatos(execucao_id,tipo_artefato);
                """

def inicializa_detalhes(database: Database) -> None:
    with _conexao(database) as conn:
        for statement in _SCHEMA.split(';'):
            if statement.strip():
                conn.execute(statement)

def serializar_json(obj):
    if isinstance(obj, BaseException):
        return {
            "tipo_erro": type(obj).__name__,
            "mensagem": str(obj)
        }

    return str(obj)

def registrar_evento(database: Database, execucao_id: str, nome_evento: str,
                     mensagem: str | None = None, nivel: str = 'INFO',
                     detalhes: dict | None = None) -> int:
    nivel = nivel.upper()
    if nivel not in {'DEBUG','INFO','ALERTA','ERRO','CRITICO'}:
        raise ValueError('Nível inválido')
    payload = json.dumps(detalhes, ensure_ascii=False, allow_nan=False, default=serializar_json) if detalhes is not None else None
    with _conexao(database) as conn:
        cursor = conn.execute('''INSERT INTO tbl_execucao_eventos
            (execucao_id, criado_em, nivel, nome_evento, mensagem, detalhes)
            VALUES (?,?,?,?,?,?)''', (execucao_id, _agora(), nivel, nome_evento, mensagem, payload))
        return cursor.lastrowid

def registrar_metrica(database: Database, execucao_id: str, nome: str,
                      valor: float, unidade: str | None = None) -> int:
    numero = float(valor)
    if not math.isfinite(numero):
        raise ValueError('Valor deve ser finito')
    with _conexao(database) as conn:
        cursor = conn.execute('''INSERT INTO tbl_execucao_metricas
            (execucao_id, criado_em, nome, valor, unidade) VALUES (?,?,?,?,?)''',
            (execucao_id, _agora(), nome, numero, unidade))
        return cursor.lastrowid

def registrar_artefato(database: Database, execucao_id: str, file_path: str,
                       tipo_artefato: str, calcular_hash: bool = True) -> int:
    tipo_artefato = tipo_artefato.upper()
    if tipo_artefato not in {'ENTRADA','SAIDA'}:
        raise ValueError('Tipo de artefato deve ser ENTRADA ou SAIDA')
    
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Artefato não encontrado: {path}")

    if path.is_dir():
        return
    
    path = Path(file_path).expanduser().resolve()
    digest = None
    size = path.stat().st_size
    if calcular_hash:
        digest_obj = hashlib.sha256()
        with path.open('rb') as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b''):
                digest_obj.update(block)
        digest = digest_obj.hexdigest()

    with _conexao(database) as conn:
        cursor = conn.execute('''INSERT INTO tbl_execucao_artefatos
            (execucao_id, criado_em, tipo_artefato, file_path, sha256, size_bytes)
            VALUES (?,?,?,?,?,?)''',
            (execucao_id, _agora(), tipo_artefato, str(path), digest, size))
        return cursor.lastrowid

def listar_detalhes(database: Database, execution_id: str) -> dict:
    with _conexao(database) as conn:
        result = {}
        for key, table in [('eventos','tbl_execucao_eventos'),('metricas','tbl_execucao_metricas'),('artefatos','tbl_execucao_artefatos')]:
            cursor = conn.execute(f'SELECT * FROM {table} WHERE execucao_id = ? ORDER BY id', (execution_id,))
            names = [col[0] for col in cursor.description]
            result[key] = [dict(zip(names, row)) for row in cursor.fetchall()]
        return result

def inicializar_rastreamento(database: sqlite3.Connection | str | Path) -> None:
    path = caminho_auditoria(database)
    with _conexao(path) as conn:
        parent = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='tbl_manifesto_execucao'").fetchone()
        if not parent:
            raise RuntimeError('Crie a tabela de execução de manifesto antes de inicializar o rastreamento.')
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS tbl_execucao_chamadas (
                chamada_id TEXT PRIMARY KEY,
                execucao_id TEXT NOT NULL,
                chamada_parente_id TEXT,
                nome_funcao TEXT NOT NULL,
                nome_modulo TEXT NOT NULL,
                iniciado_em TEXT NOT NULL,
                finalizado_em TEXT,
                duracao_ms REAL,
                estado TEXT NOT NULL CHECK (estado IN ('RODANDO','SUCESSO','FALHA')),
                tipo_erro TEXT,
                mensagem_erro TEXT,
                trilha_erro TEXT,
                FOREIGN KEY(execucao_id) REFERENCES tbl_manifesto_execucao(execucao_id),
                FOREIGN KEY(chamada_parente_id) REFERENCES tbl_execucao_chamadas(chamada_id)
            );
            CREATE INDEX IF NOT EXISTS idx_execucao_chamadas_execucao
                ON tbl_execucao_chamadas(execucao_id, iniciado_em);
            CREATE INDEX IF NOT EXISTS idx_execucao_chamadas_parente
                ON tbl_execucao_chamadas(chamada_parente_id);
        ''')

@contextmanager
def contexto_rastreamento(database: sqlite3.Connection | str | Path, execucao_id: str) -> Iterator[None]:
    path = caminho_auditoria(database)
    inicializar_rastreamento(path)
    token_exec = _contexto.set((path, execucao_id))
    token_call = _chamada.set(None)
    try:
        yield
    finally:
        _chamada.reset(token_call)
        _contexto.reset(token_exec)


def rastrear_funcao(func: F) -> F:
    if __import__('inspect').iscoroutinefunction(func):
        raise TypeError('Rastrear funcao suporta apenas funções síncronas.')

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        ctx = _contexto.get()
        if ctx is None:
            return func(*args, **kwargs)
        path, execucao_id = ctx
        parent_id = _chamada.get()
        call_id = str(uuid4())
        with _conexao(path) as conn:
            conn.execute('''INSERT INTO tbl_execucao_chamadas
                (chamada_id, execucao_id, chamada_parente_id, nome_funcao,
                 nome_modulo, iniciado_em, estado)
                VALUES (?, ?, ?, ?, ?, ?, 'RODANDO')''',
                (call_id, execucao_id, parent_id, func.__qualname__, func.__module__, _agora()))
        token = _chamada.set(call_id)
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except BaseException as exc:
            with _conexao(path) as conn:
                conn.execute('''UPDATE tbl_execucao_chamadas SET finalizado_em=?, duracao_ms=?,
                    estado='FALHA', tipo_erro=?, mensagem_erro=?,trilha_erro=?
                    WHERE chamada_id=?''', (_agora(), (time.perf_counter()-start)*1000,
                    type(exc).__name__, str(exc), traceback.format_exc(), call_id))
            raise
        else:
            with _conexao(path) as conn:
                conn.execute('''UPDATE tbl_execucao_chamadas SET finalizado_em=?, duracao_ms=?,
                    estado='SUCESSO' WHERE chamada_id=?''',
                    (_agora(), (time.perf_counter()-start)*1000, call_id))
            return result
        finally:
            _chamada.reset(token)

    return wrapper  

def listar_chamadas(database: sqlite3.Connection | str | Path, execucao_id: str) -> list[dict[str, Any]]:
    path = caminho_auditoria(database)
    with _conexao(path) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute('''SELECT * FROM tbl_execucao_chamadas
            WHERE execucao_id=? ORDER BY iniciado_em, rowid''', (execucao_id,))]
