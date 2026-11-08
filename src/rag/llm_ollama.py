"""Cliente mínimo da API REST do Ollama (chat com saída JSON estruturada)."""

from __future__ import annotations

from typing import Any

import httpx


def opcoes_do_config(cfg_llm: dict[str, Any]) -> dict[str, Any]:
    return {
        "num_ctx": cfg_llm["num_ctx"],
        "temperature": cfg_llm["temperature"],
        "top_p": cfg_llm["top_p"],
        "seed": cfg_llm["seed"],
        "num_predict": cfg_llm["num_predict"],
    }


def versao(host: str, timeout: float = 5) -> str:
    r = httpx.get(f"{host}/api/version", timeout=timeout)
    r.raise_for_status()
    return r.json()["version"]


def modelos_locais(host: str, timeout: float = 5) -> list[dict[str, Any]]:
    r = httpx.get(f"{host}/api/tags", timeout=timeout)
    r.raise_for_status()
    return r.json().get("models", [])


def modelos_carregados(host: str, timeout: float = 5) -> list[dict[str, Any]]:
    r = httpx.get(f"{host}/api/ps", timeout=timeout)
    r.raise_for_status()
    return r.json().get("models", [])


def descarregar(host: str, modelo: str, timeout: float = 30) -> None:
    httpx.post(
        f"{host}/api/generate", json={"model": modelo, "keep_alive": 0}, timeout=timeout
    ).raise_for_status()


def chat_json(
    host: str,
    modelo: str,
    mensagens: list[dict[str, str]],
    schema: dict[str, Any] | None,
    opcoes: dict[str, Any],
    think: bool | None = False,
    keep_alive: str | int = "30m",
    timeout: float = 300,
) -> dict[str, Any]:
    """Chama /api/chat sem streaming e devolve o corpo bruto da resposta do Ollama.

    Com `schema=None` não há saída estruturada (geração livre), para medir o efeito do `format`.
    """
    payload: dict[str, Any] = {
        "model": modelo,
        "messages": mensagens,
        "stream": False,
        "options": opcoes,
        "keep_alive": keep_alive,
    }
    if schema is not None:
        payload["format"] = schema
    if think is not None:
        payload["think"] = think
    r = httpx.post(f"{host}/api/chat", json=payload, timeout=timeout)
    # Modelos sem suporte a "thinking" podem rejeitar o campo `think`.
    if r.status_code == 400 and "think" in r.text and "think" in payload:
        payload.pop("think")
        r = httpx.post(f"{host}/api/chat", json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()
