"""Normalização de datas e bairros para a consulta à agenda de paradas (Fase 7).

Datas: regras próprias para as formas mais comuns ("hoje", "amanhã", "depois de amanhã",
"nesta sexta-feira", "dia 13", "13 de novembro", "13/11"), relativas à data de referência; o
dateparser (pt-BR) fica como último recurso, porque não entende várias dessas formas.

Bairros: comparação sem acento e sem maiúsculas com os distritos da agenda; prefixo comum a
vários distritos ("Jardim", "Itaim", "Vila") é ambíguo; erros de grafia pelo rapidfuzz.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from typing import Literal

import dateparser
from rapidfuzz import fuzz, process
from unidecode import unidecode

MESES = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}
DIAS_SEMANA = {
    "segunda": 0,
    "terca": 1,
    "quarta": 2,
    "quinta": 3,
    "sexta": 4,
    "sabado": 5,
    "domingo": 6,
}
NOTA_MINIMA_BAIRRO = 85
FOLGA_BAIRRO = 5  # o melhor candidato precisa ganhar do segundo por esta margem


def _norm(texto: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9/ ]", " ", unidecode(texto).lower()).split())


def resolver_data(texto: str, referencia: dt.date) -> dt.date | None:
    t = _norm(texto)
    if re.search(r"\bdepois de amanha\b", t):
        return referencia + dt.timedelta(days=2)
    if re.search(r"\bamanha\b", t):
        return referencia + dt.timedelta(days=1)
    if re.search(r"\bhoje\b", t):
        return referencia
    if re.search(r"\bontem\b", t):
        return referencia - dt.timedelta(days=1)
    if m := re.search(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b", t):
        dia, mes, ano = int(m[1]), int(m[2]), m[3]
        ano = int(ano) + (2000 if ano and len(ano) == 2 else 0) if ano else referencia.year
        return _data_valida(ano, mes, dia)
    meses = "|".join(MESES)
    if m := re.search(rf"\b(\d{{1,2}})(?: de)? ({meses})\b(?: de (\d{{4}}))?", t):
        return _data_valida(int(m[3] or referencia.year), MESES[m[2]], int(m[1]))
    if m := re.search(r"\bdia (\d{1,2})\b", t):
        dia = int(m[1])
        mes, ano = referencia.month, referencia.year
        if dia < referencia.day:
            mes, ano = (1, ano + 1) if mes == 12 else (mes + 1, ano)
        return _data_valida(ano, mes, dia)
    dias = "|".join(DIAS_SEMANA)
    if m := re.search(rf"\b(proxim[oa] )?({dias})(?:[ -]feira)?\b( que vem)?", t):
        alvo = DIAS_SEMANA[m[2]]
        delta = (alvo - referencia.weekday()) % 7
        if delta == 0 and (m[1] or m[3]):
            delta = 7
        return referencia + dt.timedelta(days=delta)
    if len(t.split()) > 4:  # frase inteira: o dateparser acharia datas em "30 horas" etc.
        return None
    base = dt.datetime.combine(referencia, dt.time(12))
    achado = dateparser.parse(
        texto,
        languages=["pt"],
        settings={"RELATIVE_BASE": base, "PREFER_DATES_FROM": "future"},
    )
    return achado.date() if achado else None


def _data_valida(ano: int, mes: int, dia: int) -> dt.date | None:
    try:
        return dt.date(ano, mes, dia)
    except ValueError:
        return None


@dataclass
class Bairro:
    situacao: Literal["ok", "ambiguo", "desconhecido", "ausente"]
    nome: str | None = None
    consultado: str = ""
    candidatos: list[str] = field(default_factory=list)


_PREPOSICOES = re.compile(r"^(?:bairro|distrito|no|na|em|do|da|de)\s+")


def resolver_bairro(nome: str | None, bairros: list[str]) -> Bairro:
    if not nome or not nome.strip():
        return Bairro("ausente")
    alvo = _norm(nome)
    while _PREPOSICOES.match(alvo):
        alvo = _PREPOSICOES.sub("", alvo)
    por_norma = {_norm(b): b for b in bairros}
    if alvo in por_norma:
        return Bairro("ok", por_norma[alvo], nome)
    prefixo = [b for n, b in por_norma.items() if n.startswith(alvo + " ")]
    if len(prefixo) == 1:
        return Bairro("ok", prefixo[0], nome)
    if len(prefixo) > 1:
        return Bairro("ambiguo", None, nome, sorted(prefixo))
    melhores = process.extract(alvo, list(por_norma), scorer=fuzz.ratio, limit=2)
    if melhores and melhores[0][1] >= NOTA_MINIMA_BAIRRO:
        if len(melhores) == 1 or melhores[0][1] - melhores[1][1] >= FOLGA_BAIRRO:
            return Bairro("ok", por_norma[melhores[0][0]], nome)
        return Bairro("ambiguo", None, nome, sorted(por_norma[m[0]] for m in melhores))
    return Bairro("desconhecido", None, nome)


_FIM_TRECHO = (
    r"(?=\s+(?:amanha|hoje|depois|nesta|neste|esta|este|proxim|no dia|dia|na data|"
    r"segunda|terca|quarta|quinta|sexta|sabado|domingo|e |\d)|[?.!,;]|$)"
)


def bairro_no_texto(pergunta: str, bairros: list[str]) -> str | None:
    """Contingência: o trecho depois de "no/na/em" que for um bairro, ou um distrito citado.

    Nomes de até 2 letras ("Sé") só valem depois de preposição: "se" é palavra comum.
    """
    t = _norm(pergunta)
    for m in re.finditer(rf"\b(?:no|na|em)\s+([a-z ]+?){_FIM_TRECHO}", t):
        trecho = m[1].strip()
        if not trecho or re.match(r"(?:minha|meu|sua|seu|casa|rua|conta|luz)\b", trecho):
            continue
        if resolver_bairro(trecho, bairros).situacao in ("ok", "ambiguo"):
            return trecho
    # Depois de "de", o nome costuma ser outra coisa ("equipamento de saúde").
    citados = [
        b
        for b in bairros
        if len(_norm(b)) > 2
        and re.search(rf"(?<!\bde )(?<!\bda )(?<!\bdo )\b{re.escape(_norm(b))}\b", t)
    ]
    return max(citados, key=len) if citados else None
