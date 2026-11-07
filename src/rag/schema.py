"""Schema de saída do assistente (Apêndice B.1 do plano)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Fonte(BaseModel):
    tipo: Literal["norma", "api"]
    id: str = Field(description="chunk_id da base ou id do registro da API")
    trecho_citado: str = Field(max_length=400, description="cópia literal do trecho usado")


class Resposta(BaseModel):
    resposta: str = Field(description="linguagem simples, frases curtas")
    recusa: bool
    motivo_recusa: str | None = None
    fontes: list[Fonte] = []
    confianca: Literal["alta", "media", "baixa"]
