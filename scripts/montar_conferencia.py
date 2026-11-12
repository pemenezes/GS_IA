"""Documento da conferência manual do test (Fase 8), a partir das saídas e da pré-classificação.

  python scripts/montar_conferencia.py

Grava avaliacao/revisao/conferencia_test.md (versionado; citações de páginas gov.br trocadas
por hash) e avaliacao/runs/local/conferencia_test_completa.md (completo, fora do git).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

from src.avaliacao.casos import carregar_congelado  # noqa: E402
from src.config import RAIZ  # noqa: E402
from src.rag import denso  # noqa: E402

RUNS = RAIZ / "avaliacao" / "runs" / "local" / "geracao"
PRE = RAIZ / "avaliacao" / "revisao" / "conferencia_pre.yaml"
SAIDA = RAIZ / "avaliacao" / "revisao" / "conferencia_test.md"
SAIDA_LOCAL = RAIZ / "avaliacao" / "runs" / "local" / "conferencia_test_completa.md"
Q = "qwen3_4b-instruct-2507-q4_K_M"
ROTULO = {"correta": "✅ correta", "parcial": "🟡 parcial", "incorreta": "❌ incorreta"}

CABECALHO = """# Conferência manual do test (Fase 8)

**Para:** Pedro. **Itens:** {n}. Cada item traz a pergunta, o gabarito que você aprovou na Fase 3,
a resposta do sistema, as fontes citadas e a **minha pré-classificação**. Basta confirmar ou
corrigir. Você pode responder no chat só com as discordâncias, por exemplo: "C2 T-018: correta".

**Critérios**
- **Veredito:** ✅ correta (responde o que foi perguntado, de acordo com o gabarito); 🟡 parcial
  (o núcleo está certo, mas falta algo pedido ou há um detalhe duvidoso); ❌ incorreta (o núcleo
  está errado ou não responde).
- **Afirma algo falso?** Sim se a resposta **ou o trecho citado** contém uma afirmação falsa
  (prazo, valor, regra ou citação inventada). É a medida manual de alucinação.
- **Recusas do C0:** a recusa **nega uma regra que existe** ("não há prazo", "não há desconto")?

Ficam de fora, porque já estão medidas sem ambiguidade:
- as recusas de perguntas respondíveis no C1 e no C2, que contam como recusa indevida;
- as perguntas "não consta" e fora do domínio, todas recusadas;
- as dinâmicas, conferidas pelos registros da agenda.

As respostas do C1 iguais às do C2 não se repetem: só entram as 5 que diferem.
{aviso}
"""
AVISO_VERSIONADO = (
    "\n> Nesta versão, as citações de páginas gov.br aparecem como hash (licença CC BY-ND). "
    "A versão completa está em `avaliacao/runs/local/{local}`.\n"
)


def _ler(nome: str) -> dict[str, dict]:
    with open(RUNS / f"{nome}.jsonl", encoding="utf-8") as f:
        return {(x := json.loads(linha))["id"]: x for linha in f if linha.strip()}


def _citacao(f: dict, govbr: set[str], mascarar: bool) -> str:
    texto = f["trecho_citado"]
    if mascarar and f["id"].strip("[] ") in govbr:
        h = hashlib.sha256(texto.encode()).hexdigest()[:12]
        texto = f"[página gov.br; sha256 {h}]"
    return f"  - `{f['id']}`: {texto}"


def _bloco(cfg: str, caso, x: dict, pre: dict, govbr: set[str], mascarar: bool) -> str:
    r = x["saida"]["resposta"]
    linhas = [
        f"### {cfg} · {caso.id} ({caso.tipo})",
        f"**Pergunta:** {caso.pergunta}",
        f"**Gabarito:** {caso.resposta_gabarito} *(fatos-chave: {', '.join(caso.fatos_chave)})*",
        f"**Resposta do {cfg}:** {r['resposta']}",
    ]
    if r["fontes"]:
        linhas.append("**Fontes citadas:**")
        linhas += [_citacao(f, govbr, mascarar) for f in r["fontes"]]
    if "nega_regra" in pre:
        linhas.append(f"**Pré-classificação:** nega uma regra que existe? **{pre['nega_regra']}**")
    else:
        linhas.append(
            f"**Pré-classificação:** {ROTULO[pre['veredito']]} · afirma algo falso? "
            f"**{pre['falso']}**"
        )
    if pre.get("nota"):
        linhas.append(f"*{pre['nota']}*")
    return "\n\n".join(linhas)


CABECALHO_POS = """# Conferência pós-correção do test (Fase 8): C2 com as correções A e C

**Para:** Pedro. **Itens:** {n}. São as respostas do C2 com as correções A (reescrita da pergunta)
e C (busca híbrida com reranker) cujo **sentido mudou** em relação à conferência do C2 original.
Os critérios são os mesmos. Responda no chat só com as discordâncias.

As demais herdam o veredito que você já deu ao C2 original:
- **mesma resposta:** {mesma};
- **redação diferente, mesmo sentido:** {sentido};
- **continuam recusadas:** {recusadas}.

O test já tinha sido visto quando as correções foram feitas; por isso esta medição é rotulada
"pós-correção" e não substitui o placar oficial.
{aviso}
"""


CABECALHO_T2 = """# Conferência do test novo, T2 (Fase 8B)

**Para:** Pedro. **Itens:** {n}. O T2 foi medido uma única vez, com o sistema congelado. Entram:
- **C2 original:** todas as respostas dadas às perguntas respondíveis;
- **C2 final** (qwen3 4B q4 com as correções C, D, E e V): só as respostas cujo **sentido mudou**.

Os critérios são os mesmos das conferências anteriores. Responda no chat só com as discordâncias,
por exemplo: "C2 T2-11: correta".

No C2 final, as demais respostas herdam o veredito do C2 original:
- **mesma resposta:** {mesma};
- **redação diferente, mesmo sentido:** {sentido};
- **continuam recusadas:** {recusadas};
- **nova recusa (contingência):** {nova}.
{aviso}
"""


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    pos = "--pos-correcao" in sys.argv
    t2 = "--t2" in sys.argv
    if t2:
        from src.avaliacao.casos import carregar_test2

        casos = {c.id: c for c in carregar_test2()}
    else:
        casos = {c.id: c for c in carregar_congelado("test")}
    if t2:
        arq_pre = PRE.with_name("conferencia_t2_pre.yaml")
    else:
        arq_pre = PRE.with_name("conferencia_pos_pre.yaml") if pos else PRE
    dados = yaml.safe_load(arq_pre.read_text(encoding="utf-8"))
    pre = dados["itens"]
    govbr = {c["chunk_id"] for c in denso.trechos_indexaveis() if not c.get("versionado", True)}
    if t2:
        runs = {"C2": _ler(f"C2_test2_{Q}"), "C2_final": _ler(f"C2_test2_{Q}_corrCDEV")}
        secoes = [
            ("C2", "C2", "## 1. C2 original: respostas dadas às perguntas respondíveis"),
            ("C2_final", "C2_final", "## 2. C2 final: respostas cujo sentido mudou"),
        ]
        saida = SAIDA.with_name("conferencia_t2.md")
        saida_local = SAIDA_LOCAL.with_name("conferencia_t2_completa.md")
        h = dados["herdadas_c2_final"]
        cabecalho = CABECALHO_T2.format(
            n="{n}",
            mesma=", ".join(h["mesma_resposta"]),
            sentido=", ".join(h["mesmo_sentido"]),
            recusadas=", ".join(h["continuam_recusadas"]),
            nova=", ".join(h["recusa_nova"]),
            aviso="{aviso}",
        )
    elif pos:
        runs = {"C2_AC": _ler(f"C2_test_{Q}_corrAC")}
        secoes = [("C2_AC", "C2_AC", "## Respostas do C2 + A + C cujo sentido mudou")]
        saida = SAIDA.with_name("conferencia_pos_correcao.md")
        saida_local = SAIDA_LOCAL.with_name("conferencia_pos_correcao_completa.md")
        h = dados["herdadas"]
        cabecalho = CABECALHO_POS.format(
            n="{n}",
            mesma=", ".join(h["mesma_resposta"]),
            sentido=", ".join(h["mesmo_sentido"]),
            recusadas=", ".join(h["continuam_recusadas"]),
            aviso="{aviso}",
        )
    else:
        runs = {cfg: _ler(f"{cfg}_test_{Q}") for cfg in ("C0", "C1", "C2")}
        secoes = [
            ("C2", "C2", "## 1. C2: respostas dadas às perguntas respondíveis"),
            ("C1", "C1", "## 2. C1: só as respostas que diferem do C2"),
            ("C0", "C0", "## 3. C0 (sem a base): respostas dadas"),
            ("C0_recusas", "C0", "## 4. C0: recusas de perguntas respondíveis"),
        ]
        saida, saida_local, cabecalho = SAIDA, SAIDA_LOCAL, CABECALHO
    n = sum(len(pre[k]) for k, _, _ in secoes)
    for destino, mascarar in ((saida, True), (saida_local, False)):
        aviso = AVISO_VERSIONADO.format(local=saida_local.name) if mascarar else ""
        partes = [cabecalho.format(n=n, aviso=aviso)]
        for chave, cfg, titulo in secoes:
            partes.append(titulo)
            for id_, p in pre[chave].items():
                partes.append(_bloco(cfg, casos[id_], runs[cfg][id_], p, govbr, mascarar))
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text("\n\n".join(partes) + "\n", encoding="utf-8", newline="\n")
    print(f"{n} itens em {saida.relative_to(RAIZ)} e {saida_local.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
