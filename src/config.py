"""Carregamento do config.yaml com sobrescritas por variáveis de ambiente."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
CONFIG_PADRAO = RAIZ / "config.yaml"
PORTA_OLLAMA = 11434


def url_ollama(valor: str) -> str:
    """URL do cliente a partir de OLLAMA_HOST, que o próprio servidor Ollama usa para o bind.

    Valores comuns no servidor ("0.0.0.0", ":11434", "localhost") viram uma URL que o cliente
    consegue usar: esquema http, host 127.0.0.1 no lugar de um endereço curinga e porta 11434.
    """
    v = valor.strip()
    if "://" not in v:
        v = f"http://{v}"
    partes = urlsplit(v)
    host = partes.hostname or "127.0.0.1"
    if host in ("0.0.0.0", "::"):
        host = "127.0.0.1"
    if ":" in host:
        host = f"[{host}]"
    return f"{partes.scheme}://{host}:{partes.port or PORTA_OLLAMA}"


def carregar_config(caminho: str | Path = CONFIG_PADRAO) -> dict[str, Any]:
    load_dotenv(RAIZ / ".env")
    with open(caminho, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if host := os.getenv("OLLAMA_HOST"):
        cfg["llm"]["host"] = url_ollama(host)
    return cfg
