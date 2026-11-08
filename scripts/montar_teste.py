"""Monta as candidatas da Fase 3 e o pacote de revisão do gabarito.

Lê avaliacao/candidatas.yaml, gera as perguntas de ruído a partir das coloquiais indicadas,
valida o schema e grava:
  - avaliacao/teste_candidatas.jsonl
  - avaliacao/revisao/revisao_gabarito.md (trechos gold com os fatos-chave destacados)

Uso:  python scripts/montar_teste.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

from src.avaliacao.casos import CANDIDATAS, Caso, gravar  # noqa: E402
from src.avaliacao.ruido import ruido_de_voz  # noqa: E402
from src.config import RAIZ  # noqa: E402
from src.ingestao.base import carregar_chunks  # noqa: E402
from src.rag.lexico import IndiceBM25  # noqa: E402

FONTE = RAIZ / "avaliacao" / "candidatas.yaml"
REVISAO = RAIZ / "avaliacao" / "revisao" / "revisao_gabarito.md"
RECUSA = {"nao_consta", "fora_dominio"}


def montar() -> list[Caso]:
    dados = yaml.safe_load(FONTE.read_text(encoding="utf-8"))
    brutos = {c["id"]: c for c in dados["casos"]}
    casos = []
    for c in dados["casos"]:
        c = dict(c)
        if c["tipo"] == "ruido":
            origem = brutos[c.pop("ruido_de")]
            base = {k: v for k, v in origem.items() if k not in ("id", "tipo", "pergunta")}
            semente = int(re.sub(r"\D", "", c["id"]))
            c = {
                **base,
                **c,
                "origem": "voz",
                "pergunta": ruido_de_voz(origem["pergunta"], semente),
                "observacoes": f"Versão com ruído de voz de {origem['id']}.",
            }
        c.setdefault("deve_recusar", c["tipo"] in RECUSA)
        c.setdefault("requer_api", c["tipo"] == "dinamica")
        casos.append(Caso.model_validate(c))
    return casos


def _destacar(texto: str, fatos: list[str]) -> str:
    for f in sorted(fatos, key=len, reverse=True):
        texto = texto.replace(f, f"**{f}**")
    return texto


def revisao(casos: list[Caso]) -> str:
    chunks = carregar_chunks()
    por_id = {c["chunk_id"]: c for c in chunks}
    indice = IndiceBM25(chunks)
    linhas = [
        "# Revisão do gabarito (Fase 3)",
        "",
        "Para cada pergunta, confira a resposta gabarito e os fatos-chave contra o trecho oficial "
        "(fatos em **negrito** dentro do trecho) e marque uma decisão. Páginas gov.br aparecem só "
        "com o link (licença CC BY-ND: o texto não vai para o repositório).",
        "",
        "Decisões: ✅ aprovar · ✏️ ajustar (escreva o ajuste) · ❌ trocar a pergunta.",
        "",
        "| Tipo | Quantidade |",
        "|---|---:|",
    ]
    contagem: dict[str, int] = {}
    for c in casos:
        contagem[c.tipo] = contagem.get(c.tipo, 0) + 1
    linhas += [f"| {t} | {n} |" for t, n in contagem.items()] + [""]
    for c in casos:
        linhas += [
            f"## {c.id} · {c.tipo} · tema `{c.tema}` · grupo {c.grupo}",
            "",
            f"**Pergunta:** {c.pergunta}",
            "",
            f"**Resposta gabarito:** {c.resposta_gabarito}",
            "",
        ]
        if c.fatos_chave:
            linhas.append(
                "**Fatos-chave (cópia literal do trecho):** "
                + " · ".join(f"`{f}`" for f in c.fatos_chave)
            )
        if c.fatos_proibidos:
            linhas.append(
                "**Fatos proibidos (regra antiga/revogada):** "
                + " · ".join(f"`{f}`" for f in c.fatos_proibidos)
            )
        if c.api_esperada:
            a = c.api_esperada
            linhas.append(
                f"**API esperada:** bairro `{a.bairro}`, data `{a.data}`, situação "
                f"`{a.situacao}`, registros {a.registros_esperados or '—'}"
            )
        if c.observacoes:
            linhas.append(f"**Observação:** {c.observacoes}")
        linhas.append("")
        for cid in c.chunk_ids_gold:
            ch = por_id[cid]
            if ch["versionado"]:
                linhas += [
                    f"<details><summary>Trecho <code>{cid}</code> · {ch['fonte']}</summary>",
                    "",
                    _destacar(ch["texto"], c.fatos_chave),
                    "",
                    f"Fonte: {ch['url']}",
                    "",
                    "</details>",
                    "",
                ]
            else:
                linhas += [f"- Trecho `{cid}` (página gov.br, texto só local): {ch['url']}", ""]
        if c.tipo == "nao_consta":
            linhas += [
                "Trechos mais parecidos na base (BM25), para confirmar que a resposta não está lá:",
                "",
            ]
            for r in indice.buscar(c.pergunta, 3):
                corpo = r.chunk["texto"].split("\n", 1)[-1].replace("\n", " ")
                corpo = corpo[:160] if r.chunk["versionado"] else "(texto gov.br só local)"
                linhas.append(f"- `{r.chunk['chunk_id']}` ({r.score:.1f}): {corpo}")
            linhas.append("")
        linhas += [
            "**Decisão:** ☐ ✅ aprovar  ☐ ✏️ ajustar  ☐ ❌ trocar  ·  Comentário: ____",
            "",
            "---",
            "",
        ]
    return "\n".join(linhas)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    casos = montar()
    gravar(casos, CANDIDATAS)
    REVISAO.parent.mkdir(parents=True, exist_ok=True)
    REVISAO.write_text(revisao(casos), encoding="utf-8", newline="\n")
    print(f"{len(casos)} candidatas -> {CANDIDATAS.relative_to(RAIZ)}")
    print(f"pacote de revisão -> {REVISAO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
