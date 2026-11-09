"""Interface de fonte de paradas programadas, usada pelo agente (Fase 7).

A implementação atual consulta a API simulada por HTTP. Uma fonte real (dados da distribuidora
ou a API da ANEEL prevista no PRODIST Módulo 4, item 113, hoje restrita à ANEEL) só precisaria
implementar o mesmo protocolo.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx


@dataclass
class ResultadoParadas:
    bairro_encontrado: bool
    bairro: str | None
    data: dt.date
    paradas: list[dict[str, Any]] = field(default_factory=list)


class FonteParadas(Protocol):
    def buscar(self, bairro: str, data: dt.date) -> ResultadoParadas: ...

    def bairros(self, q: str = "") -> list[str]: ...


class ClienteParadasHTTP:
    """Cliente da API simulada; erros de rede ou de tempo sobem como httpx.HTTPError."""

    def __init__(self, base_url: str, timeout: float = 5, cliente: httpx.Client | None = None):
        self.http = cliente or httpx.Client(base_url=base_url, timeout=timeout)

    def buscar(self, bairro: str, data: dt.date) -> ResultadoParadas:
        r = self.http.get("/paradas", params={"bairro": bairro, "data": data.isoformat()})
        r.raise_for_status()
        corpo = r.json()
        return ResultadoParadas(
            bairro_encontrado=corpo.get("bairro_encontrado", False),
            bairro=corpo.get("bairro"),
            data=data,
            paradas=corpo.get("paradas", []),
        )

    def bairros(self, q: str = "") -> list[str]:
        r = self.http.get("/bairros", params={"q": q})
        r.raise_for_status()
        return r.json()["bairros"]
