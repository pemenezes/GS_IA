"""Avaliação da busca (Fase 4): ablação no dev, limiar de recusa e medição final no test.

  python scripts/avaliar_recuperacao.py ablacao   # dev: denso/BM25/híbrido × reranker
  python scripts/avaliar_recuperacao.py limiar    # dev + calibração: varre τ (FPR ≤ 5%)
  python scripts/avaliar_recuperacao.py final     # test, uma vez, com a configuração escolhida

Saídas em avaliacao/retrieval/.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.avaliacao.casos import carregar_congelado  # noqa: E402
from src.avaliacao.recuperacao import (  # noqa: E402
    NEGATIVOS,
    RESPONDIVEIS,
    posicao_primeiro_gold,
    resumir,
    todos_gold_no_topo,
)
from src.config import RAIZ, carregar_config  # noqa: E402
from src.rag.retriever import Retriever  # noqa: E402

SAIDA = RAIZ / "avaliacao" / "retrieval"
CALIBRACAO = SAIDA / "calibracao.jsonl"
KS = (1, 3, 5)
VARIANTES = [
    ("denso", False),
    ("bm25", False),
    ("hibrido", False),
    ("denso", True),
    ("bm25", True),
    ("hibrido", True),
]


def _rodar(ret: Retriever, casos, modo: str, reranker: bool, vetores: dict) -> list[dict]:
    linhas = []
    for c in casos:
        t0 = time.perf_counter()
        cands = ret.buscar(
            c.pergunta, k=max(KS), modo=modo, reranker=reranker, vetor=vetores.get(c.id)
        )
        lat = time.perf_counter() - t0
        ranking = [x.chunk_id for x in cands]
        linhas.append(
            {
                "id": c.id,
                "tipo": c.tipo,
                "split": c.split,
                "gold": c.chunk_ids_gold,
                "gold_v2": c.gold_v2,
                "ranking": ranking,
                "posicao_v1": posicao_primeiro_gold(ranking, c.chunk_ids_gold),
                "posicao": posicao_primeiro_gold(ranking, c.gold_v2),
                "todos_gold": {k: todos_gold_no_topo(ranking, c.chunk_ids_gold, k) for k in KS},
                "latencia_s": round(lat, 3),
            }
        )
    return linhas


def _resumo_v1(linhas: list[dict]) -> dict:
    return resumir([{**x, "posicao": x["posicao_v1"]} for x in linhas], KS)


def _vetores(ret: Retriever, perguntas: dict[str, str]) -> dict:
    """Vetores das consultas na CPU (como em produção), uma vez só por pergunta."""
    return {i: ret.vetor_consulta(p) for i, p in perguntas.items()}


def ablacao(cfg: dict) -> None:
    ret = Retriever(cfg)
    casos = [c for c in carregar_congelado("dev") if c.tipo in RESPONDIVEIS]
    vetores = _vetores(ret, {c.id: c.pergunta for c in casos})
    tabela, detalhes = [], {}
    for modo, rr in VARIANTES:
        linhas = _rodar(ret, casos, modo, rr, vetores)
        r = resumir(linhas, KS)["total"]
        r1 = _resumo_v1(linhas)["total"]
        nome = f"{modo}{'+reranker' if rr else ''}"
        lat = sorted(x["latencia_s"] for x in linhas)
        tabela.append(
            {
                "variante": nome,
                "n": r["n"],
                **{f"recall@{k}": round(r[f"recall@{k}"], 3) for k in KS},
                **{f"acertos@{k}": r[f"acertos@{k}"] for k in KS},
                "ic95@3": f"[{r['ic@3'][0]:.2f}; {r['ic@3'][1]:.2f}]",
                "mrr": round(r["mrr"], 3),
                **{f"recall@{k}_v1": round(r1[f"recall@{k}"], 3) for k in KS},
                "latencia_p50_s": lat[len(lat) // 2],
                "latencia_max_s": lat[-1],
            }
        )
        detalhes[nome] = {
            "por_tipo": resumir(linhas, KS),
            "por_tipo_v1": _resumo_v1(linhas),
            "linhas": linhas,
        }
        print(
            f"  {nome:<18} v2: r@1={r['recall@1']:.3f} r@3={r['recall@3']:.3f} "
            f"r@5={r['recall@5']:.3f} mrr={r['mrr']:.3f} | v1: r@1={r1['recall@1']:.3f} "
            f"r@3={r1['recall@3']:.3f} | p50={lat[len(lat) // 2]:.2f}s"
        )
    _csv(SAIDA / "ablacao_dev.csv", tabela)
    (SAIDA / "ablacao_dev_detalhes.json").write_text(
        json.dumps(detalhes, ensure_ascii=False, indent=1, default=list), encoding="utf-8"
    )
    melhor = max(tabela, key=lambda t: (t["recall@3"], t["recall@1"], -t["latencia_p50_s"]))
    print(
        f"\nescolha pelo critério (recall@3, depois recall@1, depois latência): "
        f"{melhor['variante']}"
    )


def _nota_portao(ret: Retriever, pergunta: str, reranker: bool, vetor) -> float:
    if reranker:
        return ret.buscar(pergunta, k=1, modo="hibrido", reranker=True, vetor=vetor)[0].score
    return ret.melhor_cosseno(pergunta, vetor)


def limiar(cfg: dict) -> None:
    ret = Retriever(cfg)
    usar_rr = bool(cfg["retrieval"].get("reranker"))
    dev = carregar_congelado("dev")
    itens = [
        {
            "id": c.id,
            "pergunta": c.pergunta,
            "origem": "dev",
            "subtipo": c.tipo,
            "rotulo": "responder" if c.tipo in RESPONDIVEIS else "recusar",
        }
        for c in dev
        if c.tipo in RESPONDIVEIS + NEGATIVOS
    ]
    with open(CALIBRACAO, encoding="utf-8") as f:
        itens += [{**json.loads(x), "origem": "calibracao"} for x in f if x.strip()]
    for it in itens:
        it["nota"] = round(_nota_portao(ret, it["pergunta"], usar_rr, None), 4)
    pos = sorted(i["nota"] for i in itens if i["rotulo"] == "responder")
    # Decisão do Pedro (08/11, opção B): o portão cuida do fora do domínio; as "não consta"
    # do domínio ficam para a recusa do LLM (gatilho b da Fase 1), só reportadas aqui.
    neg = sorted((i["nota"] for i in itens if i["subtipo"] == "fora_dominio"), reverse=True)
    max_fp = int(0.05 * len(neg))
    # Aceita se nota >= τ. Com no máximo max_fp negativas acima, τ fica logo acima da
    # (max_fp+1)-ésima maior nota negativa: é o menor τ que respeita o limite.
    corte = neg[max_fp]
    tau = round(corte + 1e-4, 4)
    tpr = sum(p >= tau for p in pos) / len(pos)
    fpr = sum(n >= tau for n in neg) / len(neg)
    nao_consta = [i["nota"] for i in itens if i["subtipo"] == "nao_consta"]
    curva = []
    for t in sorted({i["nota"] for i in itens}):
        curva.append(
            {
                "tau": t,
                "tpr": sum(p >= t for p in pos) / len(pos),
                "fpr": sum(n >= t for n in neg) / len(neg),
                "nao_consta_aceitas": sum(n >= t for n in nao_consta) / len(nao_consta),
            }
        )
    por_subtipo = {}
    for st in sorted({i["subtipo"] for i in itens}):
        sel = [i for i in itens if i["subtipo"] == st]
        por_subtipo[st] = {"n": len(sel), "aceitas": sum(i["nota"] >= tau for i in sel)}
    resultado = {
        "nota": "reranker (top-1)" if usar_rr else "cosseno denso (top-1)",
        "criterio": "maior TPR das respondíveis com no máximo 5% das perguntas fora do "
        "domínio passando (opção B, Pedro, 08/11/2026); 'não consta' recusadas pelo LLM",
        "tau": tau,
        "tpr": round(tpr, 3),
        "fpr": round(fpr, 3),
        "n_positivas": len(pos),
        "n_negativas": len(neg),
        "por_subtipo": por_subtipo,
    }
    (SAIDA / "limiar.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _csv(
        SAIDA / "limiar_notas.csv",
        [{k: i[k] for k in ("id", "origem", "subtipo", "rotulo", "nota")} for i in itens],
    )
    _csv(SAIDA / "limiar_curva.csv", curva)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


def final(cfg: dict) -> None:
    tau = cfg["retrieval"]["limiar_recusa"]
    if tau is None:
        raise SystemExit("defina retrieval.limiar_recusa (etapa limiar) antes da medição final")
    destino = SAIDA / "resultados_test.json"
    if destino.exists():
        raise SystemExit(f"{destino.name} já existe: a medição no test é feita uma única vez")
    ret = Retriever(cfg)
    usar_rr = bool(cfg["retrieval"].get("reranker"))
    modo = "hibrido" if cfg["retrieval"]["hibrido"] else "denso"
    saida = {}
    for split in ("dev", "test"):
        casos = carregar_congelado(split)
        resp = [c for c in casos if c.tipo in RESPONDIVEIS]
        linhas = _rodar(ret, resp, modo, usar_rr, {})
        portao = []
        for c in casos:
            if c.tipo in RESPONDIVEIS + NEGATIVOS:
                nota = _nota_portao(ret, c.pergunta, usar_rr, None)
                portao.append(
                    {"id": c.id, "tipo": c.tipo, "nota": round(nota, 4), "aceita": nota >= tau}
                )
        saida[split] = {
            "recuperacao": resumir(linhas, KS),
            "recuperacao_v1": _resumo_v1(linhas),
            "linhas": linhas,
            "portao": portao,
        }
        r = saida[split]["recuperacao"]["total"]
        aceitas = {
            t: (
                sum(p["aceita"] for p in portao if p["tipo"] == t),
                sum(1 for p in portao if p["tipo"] == t),
            )
            for t in RESPONDIVEIS + NEGATIVOS
        }
        print(
            f"{split}: r@1={r['recall@1']:.3f} ({r['acertos@1']}/{r['n']}) "
            f"r@3={r['recall@3']:.3f} ({r['acertos@3']}/{r['n']}) mrr={r['mrr']:.3f} | "
            f"portão (aceitas/total) {aceitas}"
        )
    saida["configuracao"] = {
        "modo": modo,
        "reranker": cfg["retrieval"].get("reranker"),
        "top_k_final": cfg["retrieval"]["top_k_final"],
        "tau": tau,
    }
    destino.write_text(
        json.dumps(saida, ensure_ascii=False, indent=1, default=list), encoding="utf-8"
    )


def _csv(caminho: Path, linhas: list[dict]) -> None:
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("etapa", choices=["ablacao", "limiar", "final"])
    args = ap.parse_args()
    cfg = carregar_config()
    SAIDA.mkdir(parents=True, exist_ok=True)
    {"ablacao": ablacao, "limiar": limiar, "final": final}[args.etapa](cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
