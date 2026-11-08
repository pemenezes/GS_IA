"""Amostra de controle de qualidade da base (Fase 2): 20 trechos sorteados com seed fixa.

Para cada trecho confere, de forma automática:
  - fidelidade: cada linha do corpo existe no texto extraído do original (sem notas de redação);
  - fronteira: o corpo começa pelo rótulo do dispositivo citado e termina em fim de frase;
  - metadados obrigatórios preenchidos.
Grava base/qc_amostra.md (só atos oficiais) e base/local/qc_amostra_govbr.md (páginas gov.br).

Uso:  python scripts/qc_amostra.py [--n 20] [--seed 42]
"""

from __future__ import annotations

import argparse
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import RAIZ  # noqa: E402
from src.ingestao import base, download  # noqa: E402
from src.ingestao.extracao import extrair_arquivo  # noqa: E402
from src.ingestao.normalizacao import separar_notas  # noqa: E402

OBRIGATORIOS = [
    "chunk_id",
    "doc_id",
    "fonte",
    "url",
    "artigo",
    "data_consulta",
    "vigencia",
    "licenca",
    "sha256_doc",
    "n_tokens",
    "texto",
]
FIM_OK = (".", ";", ":", ")", "”", "?", "!")


def _texto_fonte(doc: dict, sha: str) -> str:
    for arq, reg in base.arquivos_do_documento(doc):
        if reg["sha256"] == sha:
            ex = extrair_arquivo(doc, arq.read_bytes())
            partes = []
            for b in ex.blocos:
                if b.linhas_tabela:
                    partes += [
                        " | ".join(separar_notas(c)[0] for c in linha) for linha in b.linhas_tabela
                    ]
                else:
                    partes.append(separar_notas(b.texto)[0])
            return "\n".join(partes)
    raise ValueError(f"{doc['id']}: original com sha {sha[:12]} não encontrado")


def conferir(c: dict, fonte: str) -> dict:
    corpo = c["texto"].split("\n")[1:]
    # Linha de contexto truncada termina em " (...)": confere-se o início dela.
    faltando = [
        linha for linha in corpo if (linha[:-6] if linha.endswith(" (...)") else linha) not in fonte
    ]
    rotulo = c["artigo"]
    m = re.match(r"(Art\. \d+)", rotulo)
    primeira_parte = not re.search(r"-p(\d+)$", c["chunk_id"]) or c["chunk_id"].endswith("-p1")
    if m and primeira_parte:
        inicio_ok = corpo[0].startswith(m.group(1))
    elif rotulo.startswith("Item ") and primeira_parte:
        inicio_ok = corpo[0].startswith(rotulo.split(" ", 1)[1] + ".")
    else:
        inicio_ok = True
    final = corpo[-1].rstrip()
    fim_ok = final.endswith(FIM_OK) or bool(re.search(r";\s*(e|ou)$", final)) or c["contem_tabela"]
    meta_ok = all(c.get(k) not in (None, "") for k in OBRIGATORIOS)
    return {
        "fiel": not faltando,
        "faltando": faltando,
        "inicio": inicio_ok,
        "fim": fim_ok,
        "meta": meta_ok,
    }


def relatorio(amostra: list[dict], docs: dict, titulo: str) -> str:
    linhas = [
        f"# {titulo}",
        "",
        "Gerado por `scripts/qc_amostra.py`. Colunas automáticas: **fiel** (todas as linhas "
        "existem no original extraído), **início** (começa no rótulo do dispositivo), "
        "**fim** (termina em fim de frase, em '; e'/'; ou' entre incisos, ou é tabela), "
        "**meta** (metadados completos).",
        "",
        "| # | chunk_id | dispositivo | tokens | fiel | início | fim | meta |",
        "|---|---|---|---:|:---:|:---:|:---:|:---:|",
    ]
    detalhes = []
    sim = {True: "ok", False: "**não**"}
    for i, c in enumerate(amostra, start=1):
        r = conferir(c, _texto_fonte(docs[c["doc_id"]], c["sha256_doc"]))
        linhas.append(
            f"| {i} | `{c['chunk_id']}` | {c['artigo'][:50]} | {c['n_tokens']} | "
            f"{sim[r['fiel']]} | {sim[r['inicio']]} | {sim[r['fim']]} | {sim[r['meta']]} |"
        )
        detalhes += [
            f"### {i}. `{c['chunk_id']}`",
            "",
            f"- Fonte: {c['fonte']} ({c['url']})",
            f"- Hierarquia: {' > '.join(c['hierarquia']) or '—'}",
            f"- Notas de redação: {'; '.join(c['notas_redacao']) or '—'}",
            f"- Vigência: {c['vigencia']}",
            "",
        ]
        if r["faltando"]:
            detalhes += ["Linhas não encontradas no original:", ""]
            detalhes += [f"- {x[:200]}" for x in r["faltando"]] + [""]
        detalhes += ["```text", c["texto"], "```", ""]
    return "\n".join(linhas + ["", "## Trechos sorteados", ""] + detalhes)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    docs = {d["id"]: d for d in download.carregar_manifesto()["documentos"]}
    todos = base.carregar_chunks()
    versionados = [c for c in todos if c["versionado"]]
    locais = [c for c in todos if not c["versionado"]]
    rng = random.Random(args.seed)
    amostra = sorted(rng.sample(versionados, args.n), key=lambda c: c["chunk_id"])
    destino = RAIZ / "base" / "qc_amostra.md"
    destino.write_text(
        relatorio(amostra, docs, "Controle de qualidade: amostra de trechos"), encoding="utf-8"
    )
    print(f"{destino.relative_to(RAIZ)}: {len(amostra)} trechos")
    if locais:
        amostra_local = sorted(rng.sample(locais, min(5, len(locais))), key=lambda c: c["chunk_id"])
        destino_local = RAIZ / "base" / "local" / "qc_amostra_govbr.md"
        destino_local.write_text(
            relatorio(amostra_local, docs, "Controle de qualidade: páginas gov.br (local)"),
            encoding="utf-8",
        )
        print(f"{destino_local.relative_to(RAIZ)}: {len(amostra_local)} trechos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
