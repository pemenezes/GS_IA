"""Pacote de revisão do gabarito v2 (trechos gold equivalentes), para aprovação do Pedro.

Lê avaliacao/gold_equivalentes.yaml e grava avaliacao/revisao/revisao_gold_v2.md com, para cada
grupo, as perguntas, o gold original e cada equivalente proposto (texto do trecho se for ato
oficial; só o link se for página gov.br).

Uso:  python scripts/montar_gold_v2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

from src.avaliacao.casos import carregar_congelado  # noqa: E402
from src.config import RAIZ  # noqa: E402
from src.ingestao.base import carregar_chunks  # noqa: E402

FONTE = RAIZ / "avaliacao" / "gold_equivalentes.yaml"
DESTINO = RAIZ / "avaliacao" / "revisao" / "revisao_gold_v2.md"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    dados = yaml.safe_load(FONTE.read_text(encoding="utf-8"))
    por_id = {c["chunk_id"]: c for c in carregar_chunks()}
    casos = carregar_congelado()
    faltando = [
        e["chunk_id"] for g in dados["grupos"].values() for e in g if e["chunk_id"] not in por_id
    ]
    if faltando:
        raise SystemExit(f"trechos inexistentes: {faltando}")
    total = sum(len(g) for g in dados["grupos"].values())
    linhas = [
        "# Revisão do gabarito v2: trechos gold equivalentes",
        "",
        f"Status: **{dados['status']}**. {total} equivalentes em {len(dados['grupos'])} "
        "grupos. Aprovar significa: o trecho, sozinho, responde à pergunta com a regra "
        "vigente, tanto quanto o gold original.",
        "",
    ]
    for grupo, equivalentes in dados["grupos"].items():
        do_grupo = [c for c in casos if c.grupo == grupo]
        linhas += [f"## {grupo}", ""]
        linhas += [f"- **{c.id}** ({c.tipo}, {c.split}): {c.pergunta}" for c in do_grupo]
        linhas += [
            "",
            f"Gold original: {', '.join(f'`{g}`' for g in do_grupo[0].chunk_ids_gold)}",
            "",
        ]
        for e in equivalentes:
            ch = por_id[e["chunk_id"]]
            linhas.append(f"### `{e['chunk_id']}` · {e['motivo']}")
            if ch["versionado"]:
                linhas += ["", "```text", ch["texto"][:1200], "```"]
            else:
                linhas += ["", f"Página gov.br (texto só local): {ch['url']}"]
            linhas += ["", "☐ aprovar  ☐ recusar", ""]
    DESTINO.write_text("\n".join(linhas), encoding="utf-8", newline="\n")
    print(f"{total} equivalentes -> {DESTINO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
