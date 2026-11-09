"""Banco SQLite da API de paradas: carga a partir do CSV versionado, consulta e escrita."""

from __future__ import annotations

import csv
import datetime as dt
import sqlite3
from pathlib import Path
from typing import Any

from src.paradas_api.gerador import COLUNAS, FUSO, UTC, iso, normalizar_bairro

ESQUEMA = """
CREATE TABLE IF NOT EXISTS paradas (
    id TEXT PRIMARY KEY,
    distrito TEXT NOT NULL,
    bairro TEXT NOT NULL,
    bairro_norm TEXT NOT NULL,
    inicio_utc TEXT NOT NULL,
    fim_utc TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('manutencao_programada', 'obra', 'poda')),
    motivo TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN ('agendada', 'em_andamento', 'concluida', 'cancelada')),
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_paradas_bairro ON paradas (bairro_norm, inicio_utc);
"""


def conectar(caminho: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(caminho, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def criar(caminho: Path, csv_origem: Path) -> None:
    """(Re)cria o banco a partir do CSV gerado com a semente fixa."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.unlink(missing_ok=True)
    with open(csv_origem, encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f))
    conn = conectar(caminho)
    with conn:
        conn.executescript(ESQUEMA)
        conn.executemany(
            f"INSERT INTO paradas ({', '.join(COLUNAS)}, bairro_norm) "
            f"VALUES ({', '.join('?' * len(COLUNAS))}, ?)",
            [[x[c] for c in COLUNAS] + [normalizar_bairro(x["bairro"])] for x in linhas],
        )
    conn.close()


def para_dict(linha: sqlite3.Row) -> dict[str, Any]:
    d = {c: linha[c] for c in COLUNAS}
    for campo in ("inicio", "fim"):
        t = dt.datetime.strptime(d[f"{campo}_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        d[f"{campo}_local"] = t.astimezone(FUSO).isoformat()
    return d


def bairros(conn: sqlite3.Connection) -> list[str]:
    return [r[0] for r in conn.execute("SELECT DISTINCT bairro FROM paradas ORDER BY bairro")]


def buscar(
    conn: sqlite3.Connection, bairro: str | None, data: dt.date | None, status: str | None
) -> list[dict[str, Any]]:
    """Paradas do bairro (nome normalizado) que tocam a data local, opcionalmente por status."""
    sql, args = "SELECT * FROM paradas WHERE 1 = 1", []
    if bairro:
        sql += " AND bairro_norm = ?"
        args.append(normalizar_bairro(bairro))
    if data:
        inicio = dt.datetime.combine(data, dt.time(0), FUSO)
        sql += " AND inicio_utc < ? AND fim_utc > ?"
        args += [iso(inicio + dt.timedelta(days=1)), iso(inicio)]
    if status:
        sql += " AND status = ?"
        args.append(status)
    return [para_dict(r) for r in conn.execute(sql + " ORDER BY inicio_utc, id", args)]


def obter(conn: sqlite3.Connection, id_: str) -> dict[str, Any] | None:
    r = conn.execute("SELECT * FROM paradas WHERE id = ?", [id_]).fetchone()
    return para_dict(r) if r else None


def proximo_id(conn: sqlite3.Connection) -> str:
    ultimo = conn.execute(
        "SELECT MAX(CAST(SUBSTR(id, 5) AS INTEGER)) FROM paradas WHERE id GLOB 'PAR-[0-9]*'"
    ).fetchone()[0]
    return f"PAR-{(ultimo or 0) + 1:05d}"


def inserir(conn: sqlite3.Connection, registro: dict[str, str]) -> None:
    with conn:
        conn.execute(
            f"INSERT INTO paradas ({', '.join(COLUNAS)}, bairro_norm) "
            f"VALUES ({', '.join('?' * len(COLUNAS))}, ?)",
            [registro[c] for c in COLUNAS] + [normalizar_bairro(registro["bairro"])],
        )


def atualizar(conn: sqlite3.Connection, id_: str, campos: dict[str, str]) -> None:
    with conn:
        conn.execute(
            f"UPDATE paradas SET {', '.join(f'{c} = ?' for c in campos)} WHERE id = ?",
            [*campos.values(), id_],
        )
