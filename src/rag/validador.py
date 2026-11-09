"""Validador da saída do gerador (Fase 5): schema, citação verificável, recusa e números.

Regras:
  (a) JSON conforme o schema e as regras do Apêndice B.1;
  (b) o id de cada fonte é um dos trechos fornecidos ao modelo;
  (c) o trecho_citado existe no trecho (cópia exata após normalização ou casamento aproximado);
      se o texto citado está em outro trecho fornecido, o id é corrigido e a correção registrada;
  (d) uma recusa traz o motivo e não traz números (sem resposta substantiva);
  (f) todo número da resposta aparece nos trechos fornecidos, na pergunta ou na data de hoje;
  (g) a resposta está em português (defesa contra injeção que pede outro idioma).
A regra (e), uma tentativa de reparo e depois a recusa, fica no pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from rapidfuzz import fuzz

from src.rag.schema import Resposta, classificar_saida

NOTA_MINIMA_APROXIMADA = 90
MIN_CARACTERES_CITACAO = 15  # citação curta ("24 horas") casaria com trechos demais

_ASPAS = str.maketrans({"“": '"', "”": '"', "„": '"', "‘": "'", "’": "'", "–": "-", "—": "-"})
_MARCADOR_LISTA = re.compile(r"^\s*\d{1,2}[.)]\s", re.MULTILINE)
_NUMERO = re.compile(r"\d+(?:[.,]\d+)*")
_MILHAR = re.compile(r"^\d{1,3}(?:\.\d{3})+$")


def normalizar_texto(t: str) -> str:
    t = t.translate(_ASPAS).replace("\u00ad", "")
    t = re.sub(r"-\s*\n\s*", "", t)
    return re.sub(r"\s+", " ", t).strip().lower()


def _limpar_citacao(t: str) -> str:
    t = normalizar_texto(t)
    t = re.sub(r"^(\.\.\.|…)\s*|\s*(\.\.\.|…)$", "", t)
    return t.strip(" \"'")


def casar_citacao(citado: str, texto: str) -> tuple[str, float]:
    """Devolve ("exato" | "aproximado" | "nenhum", nota 0–100)."""
    c, t = _limpar_citacao(citado), normalizar_texto(texto)
    if len(c) < MIN_CARACTERES_CITACAO:
        return "nenhum", 0.0
    if c in t:
        return "exato", 100.0
    nota = fuzz.partial_ratio(c, t)
    return ("aproximado" if nota >= NOTA_MINIMA_APROXIMADA else "nenhum"), round(nota, 1)


_PT = {
    "de",
    "a",
    "o",
    "que",
    "e",
    "do",
    "da",
    "em",
    "um",
    "para",
    "com",
    "não",
    "uma",
    "os",
    "no",
    "na",
    "por",
    "mais",
    "as",
    "dos",
    "se",
    "ao",
    "das",
    "à",
    "é",
    "sua",
    "seu",
    "ou",
}
_EN = {
    "the",
    "of",
    "and",
    "to",
    "in",
    "is",
    "you",
    "that",
    "it",
    "for",
    "with",
    "are",
    "on",
    "have",
    "be",
    "this",
    "or",
    "if",
    "your",
    "by",
    "who",
    "can",
    "must",
    "people",
}


def parece_ingles(texto: str) -> bool:
    """Heurística por palavras funcionais: mais palavras típicas do inglês do que do português."""
    palavras = re.findall(r"[a-zà-ú]+", texto.lower())
    return sum(p in _EN for p in palavras) > sum(p in _PT for p in palavras)


def _canon_numero(n: str) -> str:
    n = n.rstrip(".,")
    if _MILHAR.match(n):
        return n.replace(".", "")
    return n


def numeros(texto: str) -> set[str]:
    """Números de um texto, sem marcadores de lista ("1. ", "2) ") e com milhar normalizado."""
    texto = _MARCADOR_LISTA.sub(" ", texto)
    return {_canon_numero(n) for n in _NUMERO.findall(texto)}


@dataclass
class Verificacao:
    resposta: Resposta | None
    categoria: str  # ok | regras | schema | json (de classificar_saida)
    erros: list[str] = field(default_factory=list)
    citacoes: list[dict[str, Any]] = field(default_factory=list)
    numeros_sem_base: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.resposta is not None and not self.erros


def validar(
    conteudo: str, chunks: dict[str, dict[str, Any]], pergunta: str = "", data: str = ""
) -> Verificacao:
    """Valida a saída de C1 contra os trechos fornecidos (chunk_id -> trecho)."""
    resp, categoria = classificar_saida(conteudo)
    v = Verificacao(resp, categoria)
    if resp is None:
        v.erros.append(
            {
                "json": "A saída não é um JSON válido.",
                "schema": "O JSON não segue o schema (campos ou tipos errados).",
                "regras": "Com recusa=false, fontes precisa ter pelo menos um item.",
            }[categoria]
        )
        return v

    if parece_ingles(resp.resposta):
        v.erros.append("A resposta precisa estar em português do Brasil.")
    if resp.recusa:
        if not (resp.motivo_recusa or "").strip():
            v.erros.append("Na recusa, preencha motivo_recusa.")
        if numeros(resp.resposta):
            v.erros.append("Na recusa, a resposta não pode trazer números, prazos ou valores.")
        return v

    for f in resp.fontes:
        original = f.id
        # Trechos de norma por padrão; registros da agenda (C2) trazem tipo_citacao="api".
        chunk = chunks.get(f.id.strip().strip("[]"))
        if chunk is not None and chunk.get("tipo_citacao", "norma") != f.tipo:
            chunk = None
        casamento, nota = casar_citacao(f.trecho_citado, chunk["texto"]) if chunk else ("nenhum", 0)
        if casamento == "nenhum":
            # Citação literal de outro trecho fornecido: a fonte existe, só o id está trocado.
            for cid, c in chunks.items():
                if c.get("tipo_citacao", "norma") != f.tipo:
                    continue
                cas, nt = casar_citacao(f.trecho_citado, c["texto"])
                if cas != "nenhum":
                    chunk, casamento, nota, f.id = c, cas, nt, cid
                    break
        if chunk is None:
            v.citacoes.append(
                {"id": original, "fornecido": False, "casamento": "nenhum", "nota": 0}
            )
            v.erros.append(f"A fonte {original!r} não é um dos trechos fornecidos.")
            continue
        v.citacoes.append(
            {
                "id": chunk["chunk_id"],
                "fornecido": True,
                "casamento": casamento,
                "nota": nota,
                **(
                    {"id_original": original}
                    if original.strip().strip("[]") != chunk["chunk_id"]
                    else {}
                ),
            }
        )
        if casamento == "nenhum":
            v.erros.append(
                f"O trecho_citado da fonte {chunk['chunk_id']} não aparece no trecho: copie "
                "literalmente uma frase dele."
            )

    base = " ".join(
        [pergunta, data.replace("-", " ")]
        + [f"{c['fonte']} {c.get('data_publicacao') or ''} {c['texto']}" for c in chunks.values()]
    )
    v.numeros_sem_base = sorted(numeros(resp.resposta) - numeros(base))
    if v.numeros_sem_base:
        v.erros.append(
            "A resposta tem números que não estão nos trechos: "
            + ", ".join(v.numeros_sem_base)
            + ". Use só números escritos nos trechos."
        )
    return v
