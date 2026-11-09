"""Roteador do agente: o LLM decide se a pergunta precisa da agenda e/ou das normas.

Se a chamada falha ou o JSON não passa no schema, regras de contingência decidem. Se o LLM
pede a agenda mas não extrai o bairro ou a data, as regras completam o que falta.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ValidationError
from unidecode import unidecode

from src.agente import prompts
from src.agente.normalizacao import bairro_no_texto, resolver_data
from src.rag.schema import schema_para_llm


class Roteamento(BaseModel):
    precisa_agenda: bool
    precisa_normas: bool
    bairro: str | None
    data: str | None
    # Parte da pergunta sobre regras, reescrita sozinha: numa pergunta mista, o texto da agenda
    # baixa a similaridade com as normas e o portão recusaria.
    pergunta_normas: str | None = None


SCHEMA_ROTEADOR = schema_para_llm(Roteamento)

_AGENDA = re.compile(
    r"\b(manutenc\w*|parada\w*|desligament\w*|programad\w*|vai faltar (a )?luz|vai ter falta|"
    r"interrupc\w* programad\w*|vai (desligar|cortar) a luz (para|por) (manutenc|obra|poda))"
)
_FUTURO = re.compile(
    r"\b(hoje|amanha|depois de amanha|nest[ae]|proxim[oa]|que vem|dia \d|\d{1,2}/\d{1,2}|"
    r"segunda|terca|quarta|quinta|sexta|sabado|domingo|vai ter|vai faltar|vai haver|havera)\b"
)
_NORMAS = re.compile(
    r"\b(direito|prazo|antecedencia|avisar|aviso|indeniz\w*|compensa\w*|ressarc\w*|lei|regra|"
    r"obrigad\w*|tem que|precisa[m]?)\b"
)


@dataclass
class ResultadoRoteador:
    roteamento: Roteamento
    origem: Literal["llm", "llm+regras", "regras"]
    bruto: str = ""
    erro: str = ""


def por_regras(pergunta: str, bairros: list[str]) -> Roteamento:
    t = unidecode(pergunta).lower()
    agenda = bool(_AGENDA.search(t) and _FUTURO.search(t))
    return Roteamento(
        precisa_agenda=agenda,
        precisa_normas=not agenda or bool(_NORMAS.search(t)),
        bairro=bairro_no_texto(pergunta, bairros) if agenda else None,
        data=None,
    )


def rotear(pergunta: str, llm: Any, bairros: list[str], referencia: Any) -> ResultadoRoteador:
    try:
        corpo = llm(prompts.mensagens_roteador(pergunta), SCHEMA_ROTEADOR)
        bruto = corpo["message"]["content"]
        rot = Roteamento.model_validate_json(bruto)
    except (ValidationError, KeyError, ValueError) as e:
        return ResultadoRoteador(por_regras(pergunta, bairros), "regras", "", str(e)[:300])
    except Exception as e:  # noqa: BLE001 (falha de rede ou do Ollama vira contingência)
        return ResultadoRoteador(por_regras(pergunta, bairros), "regras", "", repr(e)[:300])
    origem: Literal["llm", "llm+regras"] = "llm"
    if rot.precisa_agenda:
        if not rot.bairro and (b := bairro_no_texto(pergunta, bairros)):
            rot.bairro, origem = b, "llm+regras"
        if rot.data and resolver_data(rot.data, referencia) is None:
            # Expressão que as regras não entendem: tenta a pergunta inteira.
            rot.data, origem = None, "llm+regras"
        if not rot.bairro and not rot.data and resolver_data(pergunta, referencia) is None:
            # Sem lugar e sem data não há consulta à agenda: é pergunta sobre a regra
            # ("como faço para ser avisado antes de uma manutenção?").
            rot = Roteamento(precisa_agenda=False, precisa_normas=True, bairro=None, data=None)
            origem = "llm+regras"
    return ResultadoRoteador(rot, origem, bruto)
