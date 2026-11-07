"""Carregamento do config.yaml com sobrescritas por variáveis de ambiente."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
CONFIG_PADRAO = RAIZ / "config.yaml"


def carregar_config(caminho: str | Path = CONFIG_PADRAO) -> dict[str, Any]:
    load_dotenv(RAIZ / ".env")
    with open(caminho, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if host := os.getenv("OLLAMA_HOST"):
        cfg["llm"]["host"] = host if host.startswith("http") else f"http://{host}"
    return cfg
