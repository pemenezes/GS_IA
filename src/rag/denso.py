"""Índice denso (FAISS, busca exata por produto interno) e seu manifesto de versão."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from src.config import RAIZ
from src.ingestao import base

DIR_INDICES = RAIZ / "base" / "indices"
ARQ_FAISS = DIR_INDICES / "denso.faiss"
ARQ_MANIFESTO = DIR_INDICES / "manifesto.json"


def assinatura_base(chunks: list[dict[str, Any]], cfg_emb: dict[str, Any]) -> str:
    """Hash dos trechos indexados e do modelo: se mudar, o índice precisa ser refeito."""
    h = hashlib.sha256()
    for c in chunks:
        h.update(c["chunk_id"].encode())
        h.update(hashlib.sha256(c["texto"].encode()).digest())
    h.update(f"{cfg_emb['modelo']}@{cfg_emb.get('revisao')}|{cfg_emb['max_length']}".encode())
    return h.hexdigest()


def construir(chunks: list[dict[str, Any]], vetores: np.ndarray, cfg_emb: dict[str, Any]) -> None:
    DIR_INDICES.mkdir(parents=True, exist_ok=True)
    indice = faiss.IndexFlatIP(vetores.shape[1])
    indice.add(vetores)
    faiss.write_index(indice, str(ARQ_FAISS))
    manifesto = {
        "assinatura": assinatura_base(chunks, cfg_emb),
        "modelo": cfg_emb["modelo"],
        "revisao": cfg_emb.get("revisao"),
        "dimensao": int(vetores.shape[1]),
        "n_trechos": len(chunks),
        "chunk_ids": [c["chunk_id"] for c in chunks],
    }
    ARQ_MANIFESTO.write_text(json.dumps(manifesto, ensure_ascii=False), encoding="utf-8")


def carregar(chunks: list[dict[str, Any]], cfg_emb: dict[str, Any]) -> faiss.Index:
    if not ARQ_FAISS.exists():
        raise FileNotFoundError("índice denso ausente: rode scripts/construir_indices.py")
    manifesto = json.loads(ARQ_MANIFESTO.read_text(encoding="utf-8"))
    if manifesto["assinatura"] != assinatura_base(chunks, cfg_emb):
        raise RuntimeError("índice desatualizado em relação à base: rode construir_indices.py")
    return faiss.read_index(str(ARQ_FAISS))


def trechos_indexaveis() -> list[dict[str, Any]]:
    """Ordem fixa: versionados e depois locais (gov.br), como em carregar_chunks."""
    return base.carregar_chunks(incluir_locais=True)
