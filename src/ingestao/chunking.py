"""Chunking estrutural: uma unidade vira um trecho, e só as longas são divididas."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from src.ingestao.estrutura import Unidade


class Tokenizador:
    """Conta tokens com o tokenizador do modelo de embeddings (o limite vale para ele)."""

    def __init__(self, modelo: str, revisao: str | None = None) -> None:
        from transformers import AutoTokenizer

        self._tok = AutoTokenizer.from_pretrained(modelo, revision=revisao)
        self.contar = lru_cache(maxsize=200_000)(self._contar)

    def _contar(self, texto: str) -> int:
        return len(self._tok(texto, add_special_tokens=False)["input_ids"])


@dataclass
class Parametros:
    alvo: int = 250
    minimo: int = 60
    maximo: int = 400
    sobreposicao: int = 40
    prefixo_contexto: bool = True

    @classmethod
    def do_config(cls, cfg: dict[str, Any]) -> Parametros:
        c = cfg["chunking"]
        return cls(
            c["alvo_tokens"],
            c["min_tokens"],
            c["max_tokens"],
            c["overlap_tokens"],
            c["prefixo_contexto"],
        )


def prefixo(rotulo_doc: str, u: Unidade) -> str:
    partes = [rotulo_doc, *u.hierarquia]
    if u.rotulo not in ("Texto", "Introdução") or not u.hierarquia:
        partes.append(u.rotulo)
    return " > ".join(partes)


def _quebrar_linha(linha: str, tok: Tokenizador, limite: int) -> list[str]:
    """Divide uma linha longa demais em frases e, em último caso, em palavras."""
    if tok.contar(linha) <= limite:
        return [linha]
    pedacos = re.split(r"(?<=[.;:])\s+", linha)
    if len(pedacos) == 1:
        pedacos = linha.split(" ")
    if len(pedacos) == 1:
        return [linha]
    partes, atual = [], ""
    for pedaco in pedacos:
        candidato = f"{atual} {pedaco}" if atual else pedaco
        if atual and tok.contar(candidato) > limite:
            partes.append(atual)
            atual = pedaco
        else:
            atual = candidato
    if atual:
        partes.append(atual)
    return [sub for parte in partes for sub in _quebrar_linha(parte, tok, limite)]


_PAI_RE = re.compile(r"^(Art\.?\s*\d|§\s*\d|Par[áa]grafo\s+[úu]nico|\d+(?:-[A-Z])?\.\s)")
_FILHO_RE = re.compile(r"^([IVXLCDM]+(?:-[A-Z]+)?\s*[-–]|[a-z]\)|\d+(?:-[A-Z])?(?:\.\d+)+\.\s)")


def truncar(linha: str, tok: Tokenizador, limite: int) -> str:
    if tok.contar(linha) <= limite:
        return linha
    saida: list[str] = []
    for palavra in linha.split(" "):
        if tok.contar(" ".join([*saida, palavra, "(...)"])) > limite:
            break
        saida.append(palavra)
    return " ".join([*saida, "(...)"])


def dividir(
    cab: str, linhas: list[str], tok: Tokenizador, p: Parametros, repetir: list[str] | None = None
) -> list[list[str]]:
    """Agrupa linhas em partes de ~alvo tokens (≤ máximo).

    Uma parte que começa num inciso, alínea ou subitem repete a linha "pai" (artigo, parágrafo ou
    item), truncada em `sobreposicao` tokens; nas demais, repete a última linha se ela for curta.
    """
    repetir = repetir or []
    custo_fixo = tok.contar(cab) + sum(tok.contar(r) + 1 for r in repetir) + 1
    limite_linha = max(p.maximo - custo_fixo - p.sobreposicao, 50)
    linhas = [pedaco for linha in linhas for pedaco in _quebrar_linha(linha, tok, limite_linha)]
    pais: list[str | None] = []
    ultimo_pai = None
    for linha in linhas:
        pais.append(ultimo_pai if _FILHO_RE.match(linha) else None)
        if _PAI_RE.match(linha):
            ultimo_pai = linha
    partes: list[list[str]] = []
    atual: list[str] = []
    custo = custo_fixo
    for i, linha in enumerate(linhas):
        c = tok.contar(linha) + 1
        if atual and (custo + c > p.alvo):
            partes.append(atual)
            anterior = atual
            atual, custo = [], custo_fixo
            if p.sobreposicao and not repetir:
                contexto = truncar(pais[i], tok, p.sobreposicao) if pais[i] else anterior[-1]
                cc = tok.contar(contexto) + 1
                if cc <= p.sobreposicao + 1 and custo + cc + c <= p.maximo:
                    atual, custo = [contexto], custo + cc
        atual.append(linha)
        custo += c
    if atual:
        partes.append(atual)
    if len(partes) > 1:
        ultima = partes[-1]
        custo_ultima = custo_fixo + sum(tok.contar(x) + 1 for x in ultima)
        juntas = partes[-2] + [x for x in ultima if x not in partes[-2][-1:]]
        custo_juntas = custo_fixo + sum(tok.contar(x) + 1 for x in juntas)
        if custo_ultima - custo_fixo < p.minimo and custo_juntas <= p.maximo:
            partes = partes[:-2] + [juntas]
    return [repetir + parte for parte in partes]


def chunks_da_unidade(
    rotulo_doc: str, u: Unidade, tok: Tokenizador, p: Parametros
) -> list[tuple[str, str, bool]]:
    """Devolve [(sufixo_id, texto, contem_tabela)] para a unidade."""
    cab = prefixo(rotulo_doc, u) if p.prefixo_contexto else ""
    if u.tabela:
        primeira = u.tabela[0]
        tem_cabecalho = (
            len(u.tabela) > 1
            and len(primeira) > 1
            and all(len(c) <= 40 and not re.search(r"\d", c) for c in primeira)
        )
        corpo = u.tabela[1:] if tem_cabecalho else u.tabela
        linhas = [" | ".join(c) for c in corpo]
        repetir = (u.linhas[:1] if u.linhas else []) + (
            [" | ".join(primeira)] if tem_cabecalho else []
        )
        grupos = dividir(cab, linhas, tok, p, repetir=repetir)
        tabela = True
    else:
        texto = "\n".join([cab, *u.linhas]) if cab else "\n".join(u.linhas)
        if tok.contar(texto) <= p.maximo:
            return [("", texto, any(" | " in x for x in u.linhas) or _tem_formula(texto))]
        grupos = dividir(cab, u.linhas, tok, p)
        tabela = any(" | " in x for x in u.linhas)
    saida = []
    for k, g in enumerate(grupos, start=1):
        texto = "\n".join([cab, *g]) if cab else "\n".join(g)
        saida.append((f"-p{k}" if len(grupos) > 1 else "", texto, tabela or _tem_formula(texto)))
    return saida


def _tem_formula(texto: str) -> bool:
    """Equações e tabelas de PDF saem achatadas na extração: o trecho é marcado como tal."""
    return bool(re.search(r"\b(Equação|Tabela|Figura)\s+\d+", texto)) or texto.count(" = ") >= 2
