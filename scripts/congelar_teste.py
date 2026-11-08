"""Congela o conjunto de teste (Fase 3): aplica o split dev/test e grava o hash.

Só deve ser rodado depois da aprovação do gabarito pelo Pedro. Gera avaliacao/teste.jsonl e
avaliacao/teste.lock (sha256). As fases seguintes usam `carregar_congelado`, que confere o hash.

Uso:  python scripts/congelar_teste.py
"""

from __future__ import annotations

import hashlib
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.avaliacao.casos import CANDIDATAS, LOCK, TESTE, carregar, gravar  # noqa: E402
from src.avaliacao.split import dividir  # noqa: E402
from src.config import RAIZ, carregar_config  # noqa: E402


def main() -> int:
    if TESTE.exists():
        print(f"{TESTE.relative_to(RAIZ)} já existe: o conjunto está congelado. Nada feito.")
        return 1
    cfg = carregar_config()["avaliacao"]
    casos = dividir(carregar(CANDIDATAS), cfg["split_dev"], cfg["split_seed"])
    gravar(casos, TESTE)
    sha = hashlib.sha256(TESTE.read_bytes()).hexdigest()
    LOCK.write_text(f"{sha}  teste.jsonl\n", encoding="utf-8", newline="\n")
    print(f"{TESTE.relative_to(RAIZ)}: {dict(Counter(c.split for c in casos))}; sha256 {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
