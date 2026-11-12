"""Busca com múltiplas consultas (Fase 8B, opção B): reformulações da pergunta pelo LLM.

A pergunta do cidadão raramente usa as palavras da norma ("cortar a luz" x "suspensão do
fornecimento"; "conta de quatro meses atrás" x "fatura vencida há mais de 90 dias"). O LLM
escreve algumas reformulações no vocabulário das normas; cada uma é buscada, e os rankings são
juntados por RRF. O portão pode usar o maior cosseno entre a pergunta e as reformulações.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from src.rag.retriever import Candidato, rrf
from src.rag.schema import schema_para_llm

SISTEMA_REFORMULACAO = """Você ajuda a buscar trechos de normas sobre direitos do consumidor de \
energia elétrica (REN 1.000/2021 da ANEEL, PRODIST, leis da tarifa social, CDC). Reescreva a \
pergunta do usuário de 3 formas diferentes, como alguém que conhece os termos dessas normas \
escreveria. Por exemplo: "cortar a luz" vira "suspensão do fornecimento"; "conta atrasada" vira \
"inadimplemento" ou "fatura vencida e não paga"; "trocar o nome da conta" vira "alteração de \
titularidade". Corrija erros de grafia. Mantenha todos os detalhes do caso (quem, a situação, o \
prazo ou o valor perguntado). Não responda à pergunta. Responda APENAS no JSON do schema."""


class Reformulacoes(BaseModel):
    reformulacoes: list[str] = Field(min_length=1, max_length=3)


SCHEMA_REFORMULACAO = schema_para_llm(Reformulacoes)


def reformular(pergunta: str, llm: Any) -> list[str]:
    """Até 3 reformulações; em caso de falha do LLM, nenhuma (a busca usa só a pergunta)."""
    msgs = [
        {"role": "system", "content": SISTEMA_REFORMULACAO},
        {"role": "user", "content": f"Pergunta: {pergunta}"},
    ]
    try:
        corpo = llm(msgs, SCHEMA_REFORMULACAO)
        lista = json.loads(corpo["message"]["content"])["reformulacoes"]
    except Exception:  # noqa: BLE001
        return []
    # Leitura tolerante: aproveita as primeiras 3 strings mesmo se vierem mais.
    return [x.strip() for x in lista if isinstance(x, str) and x.strip()][:3]


def buscar_multi(
    retriever: Any,
    consultas: list[str],
    k: int,
    reranker: bool = False,
    pergunta_reranker: str | None = None,
    candidatos: int = 20,
) -> tuple[list[Candidato], float]:
    """Junta os rankings densos das consultas por RRF; opcionalmente reranqueia pela pergunta.

    Devolve os k melhores e o maior cosseno denso entre as consultas (nota do portão).
    """
    por_id: dict[str, Candidato] = {}
    rankings, melhor = [], 0.0
    for q in consultas:
        cands = retriever.buscar(q, k=candidatos, modo="denso", reranker=False)
        if cands:
            melhor = max(melhor, float(cands[0].score_denso))
        ids = []
        for c in cands:
            por_id.setdefault(c.chunk_id, c)
            ids.append(c.chunk_id)
        rankings.append(ids)
    pontos = rrf(rankings, getattr(retriever, "cfg_ret", {}).get("rrf_k", 60))
    ordem = sorted(pontos, key=lambda i: -pontos[i])[:candidatos]
    fundidos = [por_id[i] for i in ordem]
    for c in fundidos:
        c.score = pontos[c.chunk_id]
    if reranker and fundidos:
        retriever._reranquear(pergunta_reranker or consultas[0], fundidos)
        fundidos.sort(key=lambda c: -c.score)
    return fundidos[:k], melhor


def rebaixar_paginas_com_alerta(cands: list[Candidato], k: int) -> list[Candidato]:
    """Páginas com alerta de desatualização vão para o fim quando há atos normativos na lista."""
    atos = [c for c in cands if not c.chunk.get("alerta")]
    if not atos:
        return cands[:k]
    return (atos + [c for c in cands if c.chunk.get("alerta")])[:k]
