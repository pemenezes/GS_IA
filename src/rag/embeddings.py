"""Embeddings bge-m3 (sentence-transformers), na revisão travada do config.yaml."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np


@lru_cache(maxsize=4)
def carregar_modelo(nome: str, revisao: str | None, dispositivo: str, max_length: int) -> Any:
    from sentence_transformers import SentenceTransformer

    kwargs = {"model_kwargs": {"torch_dtype": "float16"}} if dispositivo == "cuda" else {}
    modelo = SentenceTransformer(nome, device=dispositivo, revision=revisao, **kwargs)
    modelo.max_seq_length = max_length
    return modelo


def codificar(
    textos: list[str], cfg_emb: dict[str, Any], dispositivo: str | None = None, lote: int = 16
) -> np.ndarray:
    """Vetores float32 normalizados (produto interno = cosseno)."""
    disp = dispositivo or cfg_emb["dispositivo_consulta"]
    modelo = carregar_modelo(cfg_emb["modelo"], cfg_emb.get("revisao"), disp, cfg_emb["max_length"])
    vetores = modelo.encode(
        textos,
        batch_size=lote,
        normalize_embeddings=cfg_emb["normalizar"],
        convert_to_numpy=True,
        show_progress_bar=len(textos) > 100,
    )
    return np.asarray(vetores, dtype="float32")
