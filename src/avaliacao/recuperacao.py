"""Métricas de recuperação (Fase 4): recall@k, MRR e intervalo de Wilson."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

RESPONDIVEIS = ("direta", "coloquial", "ruido", "multi_trecho")
NEGATIVOS = ("nao_consta", "fora_dominio")


def wilson(acertos: int, n: int, confianca: float = 0.95) -> tuple[float, float]:
    """Intervalo de confiança de Wilson para uma proporção (bom com n pequeno)."""
    if n == 0:
        return (0.0, 0.0)
    z = {0.90: 1.6449, 0.95: 1.96, 0.99: 2.5758}[confianca]
    p = acertos / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    margem = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centro - margem), min(1.0, centro + margem))


def posicao_primeiro_gold(ranking: list[str], gold: list[str]) -> int:
    """Posição (1-based) do primeiro trecho gold no ranking; 0 se não aparece."""
    for pos, cid in enumerate(ranking, start=1):
        if cid in gold:
            return pos
    return 0


def todos_gold_no_topo(ranking: list[str], gold: list[str], k: int) -> bool:
    return set(gold) <= set(ranking[:k])


def resumir(
    linhas: list[dict[str, Any]], ks: tuple[int, ...] = (1, 3, 5), confianca: float = 0.95
) -> dict[str, dict[str, Any]]:
    """Agrega por tipo e no total. Cada linha: {"tipo", "posicao", "todos_gold": {k: bool}}."""
    grupos: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for linha in linhas:
        grupos[linha["tipo"]].append(linha)
        grupos["total"].append(linha)
    saida = {}
    for nome, itens in grupos.items():
        n = len(itens)
        r: dict[str, Any] = {"n": n}
        for k in ks:
            acertos = sum(1 for i in itens if 0 < i["posicao"] <= k)
            r[f"recall@{k}"] = acertos / n
            r[f"acertos@{k}"] = acertos
            r[f"ic@{k}"] = wilson(acertos, n, confianca)
        r["mrr"] = sum(1 / i["posicao"] for i in itens if i["posicao"]) / n
        multi = [i for i in itens if i["tipo"] == "multi_trecho"]
        if multi:
            for k in ks:
                r[f"todos_gold@{k}"] = sum(i["todos_gold"][k] for i in multi) / len(multi)
        saida[nome] = r
    return saida
