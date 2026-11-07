"""Constrói a base de conhecimento (Fase 2): download, extração e chunking.

Uso:
  python scripts/construir_base.py                  # todas as etapas
  python scripts/construir_base.py --etapa download # só baixar
  python scripts/construir_base.py --etapa base     # só extrair e gerar os trechos
  python scripts/construir_base.py --etapa download --ids D01 D02 --forcar

Os atos oficiais já estão versionados em base/raw/. As páginas gov.br (licença CC BY-ND) são
baixadas para base/local/, que fica fora do git. Alguns servidores da ANEEL bloqueiam clientes
HTTP (403); nesse caso, ver scripts/importar_download_navegador.py.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import carregar_config  # noqa: E402
from src.ingestao import base, download  # noqa: E402


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", choices=["download", "base", "todas"], default="todas")
    ap.add_argument("--ids", nargs="+", help="só estes documentos no download (ex.: D01 D07)")
    ap.add_argument("--forcar", action="store_true", help="baixa de novo mesmo se já existir")
    args = ap.parse_args()

    manifesto = download.carregar_manifesto()
    if args.etapa in ("download", "todas"):
        print("== download ==")
        download.baixar_todos(manifesto, ids=args.ids, forcar=args.forcar)
    if args.etapa in ("base", "todas"):
        print("== extração e chunking ==")
        r = base.construir(manifesto, carregar_config())
        tokens = [c["n_tokens"] for c in r["chunks"]]
        print(
            f"\n{len(r['chunks'])} trechos ({sum(c['versionado'] for c in r['chunks'])} "
            f"versionados), tokens: mín {min(tokens)}, máx {max(tokens)}, "
            f"média {sum(tokens) / len(tokens):.0f}"
        )
        print("descartes por motivo:", dict(Counter(d["motivo"] for d in r["descartes"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
