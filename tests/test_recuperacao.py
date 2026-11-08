"""Testes da Fase 4 sem modelo: RRF, métricas, Wilson e assinatura do índice."""

import pytest

from src.avaliacao.recuperacao import (
    posicao_primeiro_gold,
    resumir,
    todos_gold_no_topo,
    wilson,
)
from src.rag.denso import assinatura_base
from src.rag.retriever import rrf

CFG_EMB = {"modelo": "m", "revisao": "r", "max_length": 512}


def test_rrf_bate_com_conta_feita_a_mao():
    pontos = rrf([[10, 20, 30], [30, 10]], k=60)
    assert pontos[10] == pytest.approx(1 / 61 + 1 / 62)
    assert pontos[20] == pytest.approx(1 / 62)
    assert pontos[30] == pytest.approx(1 / 63 + 1 / 61)
    assert sorted(pontos, key=lambda i: -pontos[i]) == [10, 30, 20]


def test_posicao_e_todos_gold():
    ranking = ["a", "b", "c", "d"]
    assert posicao_primeiro_gold(ranking, ["c", "z"]) == 3
    assert posicao_primeiro_gold(ranking, ["z"]) == 0
    assert todos_gold_no_topo(ranking, ["a", "c"], 3)
    assert not todos_gold_no_topo(ranking, ["a", "d"], 3)


def test_resumir_recall_mrr_por_tipo():
    linhas = [
        {"tipo": "direta", "posicao": 1, "todos_gold": {1: True, 3: True}},
        {"tipo": "direta", "posicao": 3, "todos_gold": {1: False, 3: True}},
        {"tipo": "ruido", "posicao": 0, "todos_gold": {1: False, 3: False}},
        {"tipo": "multi_trecho", "posicao": 2, "todos_gold": {1: False, 3: False}},
    ]
    r = resumir(linhas, ks=(1, 3))
    assert r["total"]["recall@1"] == 0.25
    assert r["total"]["recall@3"] == 0.75
    assert r["total"]["mrr"] == pytest.approx((1 + 1 / 3 + 1 / 2) / 4)
    assert r["direta"]["acertos@3"] == 2
    assert r["total"]["todos_gold@3"] == 0.0


def test_wilson_conhecido():
    baixo, alto = wilson(15, 16)
    assert baixo == pytest.approx(0.717, abs=0.002)
    assert alto == pytest.approx(0.989, abs=0.002)
    assert wilson(0, 0) == (0.0, 0.0)


def test_assinatura_do_indice_muda_com_texto_ou_modelo():
    chunks = [{"chunk_id": "x", "texto": "um"}, {"chunk_id": "y", "texto": "dois"}]
    base = assinatura_base(chunks, CFG_EMB)
    assert base == assinatura_base([dict(c) for c in chunks], CFG_EMB)
    alterado = [chunks[0], {"chunk_id": "y", "texto": "dois!"}]
    assert assinatura_base(alterado, CFG_EMB) != base
    assert assinatura_base(chunks, {**CFG_EMB, "revisao": "outra"}) != base
