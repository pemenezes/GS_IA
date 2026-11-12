"""Opção B da Fase 8B: compara variantes da busca no "dev ampliado" (test original + T2).

  python scripts/avaliar_busca.py

O test original e o T2 já foram vistos, então aqui eles servem para escolher a busca; o efeito
final é medido depois como pós-correção. Métricas automáticas, sem gerar respostas:
- recall@3 e recall@5 (gabarito v2) nas 60 perguntas respondíveis com gold;
- portão: respondíveis aceitas (inclui as 15 da calibração) e negativas aceitas (não consta e
  fora do domínio do test, do T2 e da calibração).

As reformulações do LLM (multiconsulta) ficam em avaliacao/busca/reformulacoes.json, para a
medição poder ser repetida. Saídas em avaliacao/busca/.
"""

from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.avaliacao.casos import carregar_congelado, carregar_test2  # noqa: E402
from src.avaliacao.recuperacao import NEGATIVOS, RESPONDIVEIS, wilson  # noqa: E402
from src.config import RAIZ, carregar_config  # noqa: E402
from src.rag.multiconsulta import buscar_multi, rebaixar_paginas_com_alerta, reformular  # noqa: E402
from src.rag.pipeline import chamar_ollama  # noqa: E402
from src.rag.retriever import Retriever  # noqa: E402

SAIDA = RAIZ / "avaliacao" / "busca"
CACHE = SAIDA / "reformulacoes.json"
CALIBRACAO = RAIZ / "avaliacao" / "retrieval" / "calibracao.jsonl"


def _perguntas() -> tuple[list, list[dict]]:
    casos = carregar_congelado() + carregar_test2()
    resp = [c for c in casos if c.tipo in RESPONDIVEIS]
    portao = [{"id": c.id, "pergunta": c.pergunta, "grupo": "respondivel"} for c in resp]
    portao += [
        {"id": c.id, "pergunta": c.pergunta, "grupo": c.tipo} for c in casos if c.tipo in NEGATIVOS
    ]
    with open(CALIBRACAO, encoding="utf-8") as f:
        for x in map(json.loads, f):
            portao.append({"id": x["id"], "pergunta": x["pergunta"], "grupo": x["subtipo"]})
    return resp, portao


def _fracao(itens: list[dict], acerto, filtro=lambda x: True) -> str:
    sel = [x for x in itens if filtro(x)]
    return f"{sum(bool(acerto(x)) for x in sel)}/{len(sel)}"


def _reformulacoes(cfg: dict, perguntas: list[str]) -> dict[str, list[str]]:
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    faltam = [p for p in dict.fromkeys(perguntas) if p not in cache]
    if faltam:
        llm = chamar_ollama(cfg)
        for i, p in enumerate(faltam, 1):
            cache[p] = reformular(p, llm)
            if i % 20 == 0:
                print(f"  reformulações: {i}/{len(faltam)}", flush=True)
        SAIDA.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return cache


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cfg = carregar_config()
    cfg["retrieval"]["candidatos"] = 20
    tau = cfg["retrieval"]["limiar_recusa"]
    resp, portao = _perguntas()
    reform = _reformulacoes(cfg, [c.pergunta for c in resp] + [x["pergunta"] for x in portao])
    r = Retriever(cfg)
    vetores: dict[str, object] = {}

    def vet(q: str):
        if q not in vetores:
            vetores[q] = r.vetor_consulta(q)
        return vetores[q]

    buscar_original = r.buscar

    def buscar_cache(q, k=None, modo="hibrido", reranker=None, vetor=None):
        # Cada consulta é codificada uma vez só, entre todas as variantes.
        return buscar_original(q, k=k, modo=modo, reranker=reranker, vetor=vet(q))

    r.buscar = buscar_cache

    def variante(nome: str, p: str) -> tuple[list[str], float]:
        consultas = [p, *reform.get(p, [])]
        k = 5 if nome.endswith("k5") else 3
        base = nome.rsplit("_", 1)[0]
        if base == "denso":
            c = r.buscar(p, k=k, modo="denso", reranker=False)
            return [x.chunk_id for x in c], float(c[0].score_denso)
        if base in ("hib_rr", "hib_rr_faq"):
            c = r.buscar(p, k=10, modo="hibrido", reranker=True)
            c = rebaixar_paginas_com_alerta(c, k) if base.endswith("faq") else c[:k]
            return [x.chunk_id for x in c], r.melhor_cosseno(p, vet(p))
        if base in ("mq", "mq_rr", "mq_rr_faq"):
            rr = base != "mq"
            c, nota = buscar_multi(r, consultas, k=10, reranker=rr, pergunta_reranker=p)
            c = rebaixar_paginas_com_alerta(c, k) if base.endswith("faq") else c[:k]
            return [x.chunk_id for x in c], nota
        raise ValueError(nome)

    nomes = [
        f"{b}_{k}"
        for b in ("denso", "hib_rr", "hib_rr_faq", "mq", "mq_rr", "mq_rr_faq")
        for k in ("k3", "k5")
    ]
    tabela, detalhes = [], {}
    for nome in nomes:
        t0 = time.perf_counter()
        linhas = []
        for c in resp:
            ids, nota = variante(nome, c.pergunta)
            pos = next((i + 1 for i, x in enumerate(ids) if x in c.gold_v2), 0)
            linhas.append(
                {
                    "id": c.id,
                    "tipo": c.tipo,
                    "conjunto": "T2" if c.id.startswith("T2") else "T1",
                    "pos": pos,
                    "nota": round(nota, 4),
                    "todos_gold": all(g in ids for g in c.chunk_ids_gold),
                }
            )
        notas = {x["id"]: variante(nome, x["pergunta"])[1] for x in portao}
        hit = sum(x["pos"] > 0 for x in linhas)
        lo, hi = wilson(hit, len(linhas))
        linha = {
            "variante": nome,
            "recall": _fracao(linhas, lambda x: x["pos"] > 0),
            "recall_taxa": round(hit / len(linhas), 3),
            "ic95": f"[{lo:.2f}; {hi:.2f}]",
            "recall_T1": _fracao(linhas, lambda x: x["pos"] > 0, lambda x: x["conjunto"] == "T1"),
            "recall_T2": _fracao(linhas, lambda x: x["pos"] > 0, lambda x: x["conjunto"] == "T2"),
            "voz": _fracao(linhas, lambda x: x["pos"] > 0, lambda x: x["tipo"] == "ruido"),
            "todos_gold_multi": _fracao(
                linhas, lambda x: x["todos_gold"], lambda x: x["tipo"] == "multi_trecho"
            ),
            "segundos": round(time.perf_counter() - t0, 1),
        }
        for grupo, coluna in (
            ("respondivel", "portao_respondiveis"),
            ("fora_dominio", "portao_fora_aceitas"),
            ("nao_consta", "portao_nao_consta_aceitas"),
        ):
            linha[coluna] = _fracao(
                portao, lambda x, ns=notas: ns[x["id"]] >= tau, lambda x, g=grupo: x["grupo"] == g
            )
        tabela.append(linha)
        detalhes[nome] = linhas
        print(
            {
                k: linha[k]
                for k in (
                    "variante",
                    "recall",
                    "recall_T1",
                    "recall_T2",
                    "voz",
                    "portao_respondiveis",
                    "portao_fora_aceitas",
                )
            },
            flush=True,
        )
    SAIDA.mkdir(parents=True, exist_ok=True)
    with open(SAIDA / "variantes.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(tabela[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(tabela)
    (SAIDA / "variantes_detalhes.json").write_text(
        json.dumps(detalhes, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
