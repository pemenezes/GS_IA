"""API de paradas programadas (simulada), Apêndice B.2 do plano.

  uvicorn src.paradas_api.app:app --port 8001

Leitura aberta; escrita (POST e PATCH) exige o header X-API-Key igual à variável de ambiente
indicada em api_paradas.api_key_env (PARADAS_API_KEY, no .env). Os dados são simulados: ver
docs/dados_simulados.md.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import os
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field, model_validator

from src.config import RAIZ, carregar_config
from src.paradas_api import db
from src.paradas_api.gerador import UTC, iso, normalizar_bairro

Tipo = Literal["manutencao_programada", "obra", "poda"]
Status = Literal["agendada", "em_andamento", "concluida", "cancelada"]
CHAVE_EXEMPLO = "troque-esta-chave"  # valor do .env.example: não vale como chave


class ParadaNova(BaseModel):
    bairro: str
    inicio: dt.datetime = Field(description="ISO 8601 com fuso, ex.: 2026-11-20T09:00:00-03:00")
    fim: dt.datetime
    tipo: Tipo
    motivo: str = Field(min_length=3, max_length=200)
    status: Status = "agendada"

    @model_validator(mode="after")
    def _intervalo(self) -> ParadaNova:
        if self.inicio.tzinfo is None or self.fim.tzinfo is None:
            raise ValueError("inicio e fim precisam de fuso horário")
        if self.fim <= self.inicio:
            raise ValueError("fim deve ser depois de inicio")
        return self


class ParadaAlteracao(BaseModel):
    inicio: dt.datetime | None = None
    fim: dt.datetime | None = None
    motivo: str | None = Field(default=None, min_length=3, max_length=200)
    status: Status | None = None


def criar_app(caminho_db: Path, csv_origem: Path, env_chave: str = "PARADAS_API_KEY") -> FastAPI:
    if not caminho_db.exists():
        db.criar(caminho_db, csv_origem)
    conn = db.conectar(caminho_db)
    sha_dados = hashlib.sha256(csv_origem.read_bytes()).hexdigest()
    nomes = db.bairros(conn)
    por_norma = {normalizar_bairro(b): b for b in nomes}

    app = FastAPI(
        title="Paradas programadas (simulada)",
        version="1.0",
        description="Dados simulados, calibrados com interrupções programadas da Enel SP "
        "(dados abertos da ANEEL, ODbL). Não use para decisões reais.",
    )

    def exigir_chave(x_api_key: Annotated[str | None, Header()] = None) -> None:
        chave = os.getenv(env_chave, "")
        if not chave or chave == CHAVE_EXEMPLO:
            raise HTTPException(503, "escrita desativada: defina a chave da API no .env")
        if not x_api_key or not hmac.compare_digest(x_api_key, chave):
            raise HTTPException(401, "chave de API ausente ou inválida (header X-API-Key)")

    @app.get("/health")
    def health() -> dict:
        n = conn.execute("SELECT COUNT(*) FROM paradas").fetchone()[0]
        return {"status": "ok", "simulada": True, "registros": n, "sha256_dados": sha_dados}

    @app.get("/bairros")
    def listar_bairros(q: str = "") -> dict:
        alvo = normalizar_bairro(q)
        return {"bairros": [b for b in nomes if alvo in normalizar_bairro(b)]}

    @app.get("/paradas")
    def listar_paradas(
        bairro: str | None = None,
        data: Annotated[dt.date | None, Query(description="YYYY-MM-DD (horário local)")] = None,
        status: Status | None = None,
    ) -> dict:
        resposta: dict = {"bairro": None, "data": data.isoformat() if data else None}
        if bairro is not None:
            canonico = por_norma.get(normalizar_bairro(bairro))
            if canonico is None:
                return {
                    **resposta,
                    "bairro_encontrado": False,
                    "paradas": [],
                    "aviso": "bairro não encontrado; veja GET /bairros?q=...",
                }
            resposta.update(bairro=canonico, bairro_encontrado=True)
        return {**resposta, "paradas": db.buscar(conn, bairro, data, status)}

    @app.get("/paradas/{id_}")
    def obter_parada(id_: str) -> dict:
        registro = db.obter(conn, id_)
        if registro is None:
            raise HTTPException(404, "parada não encontrada")
        return registro

    @app.post("/paradas", status_code=201, dependencies=[Depends(exigir_chave)])
    def criar_parada(p: ParadaNova) -> dict:
        canonico = por_norma.get(normalizar_bairro(p.bairro))
        if canonico is None:
            raise HTTPException(422, "bairro não encontrado; veja GET /bairros")
        agora = iso(dt.datetime.now(UTC))
        registro = {
            "id": db.proximo_id(conn),
            "distrito": canonico,
            "bairro": canonico,
            "inicio_utc": iso(p.inicio),
            "fim_utc": iso(p.fim),
            "tipo": p.tipo,
            "motivo": p.motivo,
            "status": p.status,
            "criado_em": agora,
            "atualizado_em": agora,
        }
        db.inserir(conn, registro)
        return db.obter(conn, registro["id"])

    @app.patch("/paradas/{id_}", dependencies=[Depends(exigir_chave)])
    def alterar_parada(id_: str, p: ParadaAlteracao) -> dict:
        atual = db.obter(conn, id_)
        if atual is None:
            raise HTTPException(404, "parada não encontrada")
        campos = {k: v for k, v in p.model_dump(exclude_none=True).items()}
        for k in ("inicio", "fim"):
            if k in campos:
                if campos[k].tzinfo is None:
                    raise HTTPException(422, f"{k} precisa de fuso horário")
                campos[f"{k}_utc"] = iso(campos.pop(k))
        if campos.get("inicio_utc", atual["inicio_utc"]) >= campos.get("fim_utc", atual["fim_utc"]):
            raise HTTPException(422, "fim deve ser depois de inicio")
        if not campos:
            return atual
        campos["atualizado_em"] = iso(dt.datetime.now(UTC))
        db.atualizar(conn, id_, campos)
        return db.obter(conn, id_)

    return app


_APP: FastAPI | None = None


def __getattr__(nome: str) -> FastAPI:
    """`app` só é montado quando pedido (uvicorn), para os testes usarem um banco temporário."""
    global _APP
    if nome != "app":
        raise AttributeError(nome)
    if _APP is None:
        cfg = carregar_config()["api_paradas"]
        _APP = criar_app(RAIZ / cfg["arquivo_db"], RAIZ / cfg["arquivo_csv"], cfg["api_key_env"])
    return _APP
