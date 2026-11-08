"""Busca lexical (BM25) sobre os trechos da base."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from rank_bm25 import BM25Okapi
from unidecode import unidecode

_PALAVRAS_VAZIAS = (
    "a o e de do da dos das em no na nos nas um uma uns umas por para com sem que se ou ao aos "
    "as os pelo pela pelos pelas seu sua seus suas ser ter sao foi deve devem como mais nao eu "
    "meu minha me lhe isso esta este essa esse tem ha qual quais quando onde quanto sobre entre "
    "ate ja tambem muito"
)
STOPWORDS = set(_PALAVRAS_VAZIAS.split())


def tokenizar(texto: str) -> list[str]:
    texto = unidecode(texto.lower())
    return [t for t in re.findall(r"[a-z0-9]+", texto) if t not in STOPWORDS and len(t) > 1]


@dataclass
class Resultado:
    chunk: dict[str, Any]
    score: float


class IndiceBM25:
    def __init__(self, chunks: list[dict[str, Any]]) -> None:
        self.chunks = chunks
        self._bm25 = BM25Okapi([tokenizar(c["texto"]) for c in chunks])

    def buscar(self, consulta: str, k: int = 5) -> list[Resultado]:
        scores = self._bm25.get_scores(tokenizar(consulta))
        ordem = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
        return [Resultado(self.chunks[i], float(scores[i])) for i in ordem]
