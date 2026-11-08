"""Busca nos trechos da base: densa (bge-m3/FAISS), lexical (BM25), híbrida (RRF) e reranker."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Literal

import numpy as np

from src.rag import denso
from src.rag.embeddings import codificar
from src.rag.lexico import IndiceBM25

Modo = Literal["denso", "bm25", "hibrido"]


@dataclass
class Candidato:
    chunk: dict[str, Any]
    score: float  # nota usada na ordenação final (RRF, cosseno, BM25 ou reranker)
    score_denso: float | None = None
    score_bm25: float | None = None
    score_rerank: float | None = None
    posicoes: dict[str, int] = field(default_factory=dict)

    @property
    def chunk_id(self) -> str:
        return self.chunk["chunk_id"]


def rrf(rankings: list[list[int]], k: int = 60) -> dict[int, float]:
    """Reciprocal Rank Fusion: soma de 1/(k + posição), com posição começando em 1."""
    pontos: dict[int, float] = {}
    for ranking in rankings:
        for pos, i in enumerate(ranking, start=1):
            pontos[i] = pontos.get(i, 0.0) + 1.0 / (k + pos)
    return pontos


@lru_cache(maxsize=2)
def _carregar_reranker(nome: str, revisao: str | None, dispositivo: str) -> Any:
    from sentence_transformers import CrossEncoder

    kwargs = {}
    if dispositivo == "cuda":
        import torch

        kwargs["model_kwargs"] = {"torch_dtype": torch.float16}
    return CrossEncoder(nome, revision=revisao, device=dispositivo, max_length=512, **kwargs)


class Retriever:
    def __init__(self, cfg: dict[str, Any], chunks: list[dict[str, Any]] | None = None) -> None:
        self.cfg = cfg
        self.cfg_ret = cfg["retrieval"]
        self.chunks = chunks if chunks is not None else denso.trechos_indexaveis()
        self.indice = denso.carregar(self.chunks, cfg["embeddings"])
        self.bm25 = IndiceBM25(self.chunks)

    def vetor_consulta(self, consulta: str) -> np.ndarray:
        return codificar([consulta], self.cfg["embeddings"])[0]

    def _denso(self, vetor: np.ndarray, n: int) -> tuple[list[int], dict[int, float]]:
        scores, idx = self.indice.search(vetor[None, :], n)
        pares = [(int(i), float(s)) for i, s in zip(idx[0], scores[0], strict=True) if i >= 0]
        return [i for i, _ in pares], dict(pares)

    def _bm25(self, consulta: str, n: int) -> tuple[list[int], dict[int, float]]:
        scores = self.bm25.scores(consulta)
        ordem = sorted(range(len(scores)), key=lambda i: -scores[i])[:n]
        return ordem, {i: float(scores[i]) for i in ordem}

    def buscar(
        self,
        consulta: str,
        k: int | None = None,
        modo: Modo = "hibrido",
        reranker: bool | None = None,
        vetor: np.ndarray | None = None,
    ) -> list[Candidato]:
        k = k or self.cfg_ret["top_k_final"]
        n = self.cfg_ret["candidatos"]
        usar_reranker = bool(self.cfg_ret.get("reranker")) if reranker is None else reranker
        vetor = self.vetor_consulta(consulta) if vetor is None and modo != "bm25" else vetor

        ord_d, sc_d = self._denso(vetor, n) if modo != "bm25" else ([], {})
        ord_b, sc_b = self._bm25(consulta, n) if modo != "denso" else ([], {})
        if modo == "denso":
            ordem, nota = ord_d, sc_d
        elif modo == "bm25":
            ordem, nota = ord_b, sc_b
        else:
            nota = rrf([ord_d, ord_b], self.cfg_ret["rrf_k"])
            ordem = sorted(nota, key=lambda i: -nota[i])[:n]
        cands = [
            Candidato(
                self.chunks[i],
                nota[i],
                sc_d.get(i),
                sc_b.get(i),
                posicoes={
                    "denso": ord_d.index(i) + 1 if i in sc_d else 0,
                    "bm25": ord_b.index(i) + 1 if i in sc_b else 0,
                },
            )
            for i in ordem
        ]
        if usar_reranker and cands:
            self._reranquear(consulta, cands)
            cands.sort(key=lambda c: -c.score)
        return cands[:k]

    def _reranquear(self, consulta: str, cands: list[Candidato]) -> None:
        conf = self.cfg_ret.get("reranker") or self.cfg_ret.get("reranker_ablacao") or {}
        modelo = _carregar_reranker(
            conf.get("modelo", "BAAI/bge-reranker-v2-m3"),
            conf.get("revisao"),
            conf.get("dispositivo", "cpu"),
        )
        notas = modelo.predict([(consulta, c.chunk["texto"]) for c in cands], batch_size=8)
        for c, s in zip(cands, notas, strict=True):
            c.score_rerank = float(s)
            c.score = float(s)

    def melhor_cosseno(self, consulta: str, vetor: np.ndarray | None = None) -> float:
        """Similaridade do trecho mais próximo na busca densa (nota do portão de recusa)."""
        vetor = self.vetor_consulta(consulta) if vetor is None else vetor
        return float(self.indice.search(vetor[None, :], 1)[0][0][0])
