"""Mascaramento de dados pessoais antes de enviar a pergunta ao modelo e antes de registrar logs.

O serviço não precisa de dados pessoais para responder (seção 8 do plano). Os padrões cobrem
CPF, CNPJ, e-mail, telefone, CEP e números longos (instalação, cliente, protocolo). Números
curtos ("40 dias", "30 horas", "2 salários") continuam, porque fazem parte da pergunta.
"""

from __future__ import annotations

import re

PADROES = [
    ("[EMAIL]", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("[CNPJ]", re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")),
    ("[CPF]", re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")),
    ("[TELEFONE]", re.compile(r"(?:\+?55\s?)?\(?\b\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b")),
    ("[CEP]", re.compile(r"\b\d{5}-\d{3}\b")),
    ("[NUMERO]", re.compile(r"\b\d{7,}\b")),
]


def mascarar(texto: str) -> tuple[str, list[str]]:
    """Devolve o texto mascarado e os tipos de dado encontrados (sem os valores)."""
    encontrados = []
    for rotulo, padrao in PADROES:
        texto, n = padrao.subn(rotulo, texto)
        if n:
            encontrados.append(rotulo.strip("[]").lower())
    return texto, encontrados
