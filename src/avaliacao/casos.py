"""Schema dos casos de teste (Fase 3) e carregamento do conjunto."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from src.config import RAIZ

TESTE = RAIZ / "avaliacao" / "teste.jsonl"
CANDIDATAS = RAIZ / "avaliacao" / "teste_candidatas.jsonl"
LOCK = RAIZ / "avaliacao" / "teste.lock"

Tipo = Literal[
    "direta", "coloquial", "ruido", "multi_trecho", "nao_consta", "fora_dominio", "dinamica"
]

COMPOSICAO = {
    "direta": 18,
    "coloquial": 12,
    "ruido": 6,
    "multi_trecho": 6,
    "nao_consta": 6,
    "fora_dominio": 6,
    "dinamica": 6,
}


class ApiEsperada(BaseModel):
    """Consulta que o agente deve fazer e o que a API simulada deve devolver."""

    bairro: str | None
    data: str | None = Field(description="YYYY-MM-DD, resolvida a partir da data_referencia")
    registros_esperados: list[str] = []
    situacao: Literal["com_parada", "sem_parada", "bairro_ambiguo"]


class Caso(BaseModel):
    id: str
    split: Literal["dev", "test", "pendente"] = "pendente"
    tipo: Tipo
    grupo: str
    tema: str
    origem: Literal["texto", "voz"] = "texto"
    pergunta: str
    deve_recusar: bool
    requer_api: bool = False
    chunk_ids_gold: list[str] = []
    # Gabarito v2 (Fase 4): trechos que respondem tanto quanto o gold original.
    gold_equivalentes: list[str] = []
    resposta_gabarito: str
    fatos_chave: list[str] = []
    fatos_proibidos: list[str] = []
    armadilha_temporal: bool = False
    api_esperada: ApiEsperada | None = None
    observacoes: str = ""

    @model_validator(mode="after")
    def _coerencia(self) -> Caso:
        if self.tipo in ("nao_consta", "fora_dominio"):
            if not self.deve_recusar or self.chunk_ids_gold or self.fatos_chave:
                raise ValueError(f"{self.id}: recusa sem gold e sem fatos-chave")
        elif self.tipo == "dinamica":
            if not self.requer_api or self.api_esperada is None:
                raise ValueError(f"{self.id}: dinâmica exige requer_api e api_esperada")
        else:
            if self.deve_recusar or not self.chunk_ids_gold or not self.fatos_chave:
                raise ValueError(f"{self.id}: respondível exige gold e fatos-chave")
        if self.tipo == "multi_trecho" and len(self.chunk_ids_gold) < 2:
            raise ValueError(f"{self.id}: multi-trecho exige 2 ou mais trechos gold")
        if self.tipo == "ruido" and self.origem != "voz":
            raise ValueError(f"{self.id}: ruído tem origem voz")
        if self.armadilha_temporal and not self.fatos_proibidos:
            raise ValueError(f"{self.id}: armadilha temporal exige fatos proibidos")
        if self.gold_equivalentes and not self.chunk_ids_gold:
            raise ValueError(f"{self.id}: equivalentes exigem um gold original")
        return self

    @property
    def gold_v2(self) -> list[str]:
        return self.chunk_ids_gold + [
            g for g in self.gold_equivalentes if g not in self.chunk_ids_gold
        ]


def carregar(caminho: Path = TESTE) -> list[Caso]:
    with open(caminho, encoding="utf-8") as f:
        return [Caso.model_validate_json(linha) for linha in f if linha.strip()]


def carregar_congelado(split: str | None = None) -> list[Caso]:
    """Conjunto de teste congelado; falha se o arquivo não bater com o hash de teste.lock."""
    sha = hashlib.sha256(TESTE.read_bytes()).hexdigest()
    if sha != LOCK.read_text(encoding="utf-8").split()[0]:
        raise RuntimeError("avaliacao/teste.jsonl mudou depois de congelado (hash diferente)")
    casos = carregar(TESTE)
    return [c for c in casos if split is None or c.split == split]


def gravar(casos: list[Caso], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        for c in casos:
            f.write(json.dumps(c.model_dump(), ensure_ascii=False) + "\n")
