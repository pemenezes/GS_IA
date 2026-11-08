"""Divisão dev/test estratificada por tipo e respeitando grupos (Fase 3)."""

from __future__ import annotations

import random
from collections import Counter, defaultdict

from src.avaliacao.casos import Caso


def dividir(casos: list[Caso], frac_dev: float = 0.4, semente: int = 42) -> list[Caso]:
    """Atribui grupos inteiros a dev até atingir ~frac_dev de cada tipo; o resto vai para test."""
    por_grupo: dict[str, list[Caso]] = defaultdict(list)
    for c in casos:
        por_grupo[c.grupo].append(c)
    total = Counter(c.tipo for c in casos)
    rng = random.Random(semente)
    alvo = _maiores_restos(total, frac_dev, rng)
    grupos = sorted(por_grupo)
    rng.shuffle(grupos)
    # Grupos com mais tipos primeiro: são os mais difíceis de encaixar sem estourar o alvo.
    grupos.sort(key=lambda g: -len({c.tipo for c in por_grupo[g]}))
    em_dev: Counter[str] = Counter()
    dev: set[str] = set()
    for g in grupos:
        tipos = Counter(c.tipo for c in por_grupo[g])
        if all(em_dev[t] + n <= alvo[t] for t, n in tipos.items()):
            dev.add(g)
            em_dev.update(tipos)
    return [c.model_copy(update={"split": "dev" if c.grupo in dev else "test"}) for c in casos]


def _maiores_restos(total: Counter[str], frac: float, rng: random.Random) -> dict[str, int]:
    """Cotas por tipo que somam round(frac * N): piso de cada tipo + sobras pelos maiores restos."""
    exatos = {t: n * frac for t, n in total.items()}
    alvo = {t: int(x) for t, x in exatos.items()}
    sobra = round(frac * sum(total.values())) - sum(alvo.values())
    tipos = sorted(exatos)
    rng.shuffle(tipos)
    for t in sorted(tipos, key=lambda t: -(exatos[t] - alvo[t]))[:sobra]:
        alvo[t] += 1
    return alvo
