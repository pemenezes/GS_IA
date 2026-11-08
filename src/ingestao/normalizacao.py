"""Normalização de texto e separação das notas de redação."""

from __future__ import annotations

import re
import unicodedata

_PALAVRAS_NOTA = (
    r"Inclu[íi]d[oa]s?|Reda[çc][ãa]o\s+dada|Acrescid[oa]s?|Alterad[oa]s?|Revogad[oa]s?|"
    r"Renumerad[oa]s?|Vide|Vig\s?[êe]ncia|Promulga[çc][ãa]o|Suprimid[oa]s?|Express[ãa]o|"
    r"Retificad[oa]s?|Republicad[oa]s?|Convers[ãa]o|Regulamento|Prorroga[çc][ãa]o|"
    r"Produ[çc][ãa]o\s+de\s+efeitos?|Efeitos?|Suspens[oa]|Decis[ãa]o\s+judicial"
)
# Notas entre parênteses, com até um nível de parênteses internos.
NOTA_RE = re.compile(r"\(\s*(?:" + _PALAVRAS_NOTA + r")\b(?:[^()]|\([^()]*\))*\)", re.IGNORECASE)
_VETADO_RE = re.compile(r"\(\s*(?:VETAD[OA]|vetad[oa])\s*\)")


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFC", texto)
    texto = texto.replace("\xa0", " ").replace("\u200b", "").replace("\t", " ")
    texto = re.sub(r"(\d)\s*[°˚]", r"\1º", texto)
    texto = re.sub(r"\b([Nn])\s+[oº](s?)(?=\s*\d)", r"\1º\2", texto)
    texto = re.sub(r"(\d)\s+º", r"\1º", texto)
    texto = re.sub(r"((?:Art\.|§)\s*\d+)\s+o\b", r"\1º", texto)
    texto = re.sub(r"\bArt\.(?=\d)", "Art. ", texto)
    texto = re.sub(r"§(?=\d)", "§ ", texto)
    texto = re.sub(r"\.{5,}", " (...) ", texto)
    texto = re.sub(r"[ \r\n]+", " ", texto)
    texto = re.sub(r"\s+([,.;:)])", r"\1", texto)
    texto = re.sub(r"\(\s+", "(", texto)
    return texto.strip()


def separar_notas(texto: str) -> tuple[str, list[str]]:
    """Remove as notas de redação do texto e as devolve à parte."""
    notas = [normalizar(m.group(0)) for m in NOTA_RE.finditer(texto)]
    limpo = NOTA_RE.sub(" ", texto)
    return normalizar(limpo), notas


_ROTULO_DISPOSITIVO = (
    r"(?:Art\.\s*\d+[\wº]*(?:-[A-Z]+)?\.?|§\s*\d+º?(?:-[A-Z]+)?\.?|Par[áa]grafo\s+[úu]nico\.?|"
    r"[IVXLCDM]+(?:-[A-Z]+)?\s*[-–]|[a-z]\)|\d+(?:-[A-Z]+)?(?:\.\d+)*\.)"
)
_SO_ROTULO_RE = re.compile(
    r"^\s*" + _ROTULO_DISPOSITIVO + r"\s*(?:\(?\s*(?:revogad[oa]s?|vetad[oa]s?|suprimid[oa]s?)"
    r"\s*\)?)?\s*[.;:,]?\s*$",
    re.IGNORECASE,
)


def e_dispositivo_vazio(texto: str) -> bool:
    """True se sobrou só o rótulo (ex.: "§ 2º", "III -", "Art. 5º (Revogado)")."""
    return bool(_SO_ROTULO_RE.match(_VETADO_RE.sub(" ", texto)))
