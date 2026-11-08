"""Constrói o índice denso (bge-m3 + FAISS) da base (Fase 4).

A indexação usa a GPU em fp16 (config: embeddings.dispositivo_indexacao); antes, descarrega os
modelos do Ollama para liberar VRAM. O BM25 é reconstruído em memória a cada uso (segundos).

Uso:  python scripts/construir_indices.py [--cpu]
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import carregar_config  # noqa: E402
from src.rag import denso, llm_ollama  # noqa: E402
from src.rag.embeddings import codificar  # noqa: E402


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cpu", action="store_true", help="indexar na CPU (mais lento)")
    args = ap.parse_args()
    cfg = carregar_config()
    disp = "cpu" if args.cpu else cfg["embeddings"]["dispositivo_indexacao"]
    if disp == "cuda":
        try:
            for m in llm_ollama.modelos_carregados(cfg["llm"]["host"]):
                llm_ollama.descarregar(cfg["llm"]["host"], m["name"])
                print(f"Ollama: {m['name']} descarregado para liberar VRAM")
        except Exception as e:  # noqa: BLE001
            print(f"(Ollama indisponível, seguindo: {e})")
    chunks = denso.trechos_indexaveis()
    t0 = time.perf_counter()
    vetores = codificar([c["texto"] for c in chunks], cfg["embeddings"], disp, lote=32)
    denso.construir(chunks, vetores, cfg["embeddings"])
    print(
        f"{len(chunks)} trechos indexados em {disp} ({time.perf_counter() - t0:.0f} s), "
        f"dimensão {vetores.shape[1]} -> {denso.ARQ_FAISS.relative_to(denso.RAIZ)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
