"""Gera requirements-lock.txt (freeze completo) em UTF-8, com o índice do PyTorch CUDA.

Uso:  python scripts/gerar_lock.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INDICE_TORCH = "https://download.pytorch.org/whl/cu128"


def main() -> int:
    freeze = subprocess.run(
        [sys.executable, "-m", "pip", "freeze", "--exclude-editable"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    # Só ASCII: no Windows o pip lê requirements na codificação local, não em UTF-8.
    cabecalho = (
        "# Freeze completo do ambiente de referencia (Windows, Python 3.12, CUDA 12.8).\n"
        "# Gerado por scripts/gerar_lock.py; nao editar a mao.\n"
        f"--extra-index-url {INDICE_TORCH}\n"
    )
    destino = RAIZ / "requirements-lock.txt"
    destino.write_text(cabecalho + freeze, encoding="utf-8", newline="\n")
    print(f"{destino.name}: {len(freeze.splitlines())} pacotes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
