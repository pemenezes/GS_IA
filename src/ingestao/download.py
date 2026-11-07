"""Download das fontes do manifesto, com hash e registro de acesso."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import httpx
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import RAIZ

MANIFESTO = RAIZ / "base" / "manifesto.yaml"
DIR_RAW = RAIZ / "base" / "raw"
DIR_LOCAL_RAW = RAIZ / "base" / "local" / "raw"
REGISTRO = "downloads.json"
USER_AGENT = (
    "Mozilla/5.0 (compatible; LuzCidada/0.1; projeto academico FIAP; "
    "+https://github.com/pemenezes/GS_IA)"
)
EXTENSAO = {"HTML": ".html", "PDF": ".pdf"}


def carregar_manifesto(caminho: Path = MANIFESTO) -> dict[str, Any]:
    with open(caminho, encoding="utf-8") as f:
        return yaml.safe_load(f)


def dir_raw(doc: dict[str, Any]) -> Path:
    return DIR_RAW if doc["versionar_texto"] else DIR_LOCAL_RAW


def sha256(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2, max=30), reraise=True)
def _get(cliente: httpx.Client, url: str) -> httpx.Response:
    r = cliente.get(url)
    r.raise_for_status()
    return r


def desescapar_json_html(html: str) -> str:
    """Páginas do gov.br embutem o conteúdo como JSON escapado (\\u003C, \\", \\u002F)."""
    trocas = {'\\"': '"', "\\u002F": "/", "\\u003C": "<", "\\u003E": ">", "\\u0026": "&"}
    for de, para in trocas.items():
        html = html.replace(de, para)
    return html


def resolver_versao_vigente(html: str, rotulo: str) -> str:
    """Acha o link "versão vigente" que segue o rótulo (ex.: "Módulo 8") na página de listagem."""
    html = desescapar_json_html(html)
    padrao = (
        r"(?<![A-Za-zÀ-ÿ])" + re.escape(rotulo) + r"\s*-[^<]{0,200}?"
        r"<a\b[^>]*?href=\"([^\"]+)\"[^>]*>\s*vers(?:ã|&atilde;)o vigente"
    )
    m = re.search(padrao, html)
    if not m:
        raise ValueError(f"link 'versão vigente' não encontrado para {rotulo!r}")
    return m.group(1)


def baixar_documento(
    doc: dict[str, Any], cliente: httpx.Client, forcar: bool = False
) -> list[dict[str, Any]]:
    """Baixa as URLs de um documento e devolve um registro por arquivo."""
    destino = dir_raw(doc)
    destino.mkdir(parents=True, exist_ok=True)
    registros = []
    for i, url in enumerate(doc["urls"]):
        url_final = url
        if doc.get("resolver"):
            url_final = resolver_versao_vigente(_get(cliente, url).text, doc["resolver"])
        sufixo = f"_{i + 1}" if len(doc["urls"]) > 1 else ""
        arquivo = destino / f"{doc['id']}{sufixo}{EXTENSAO[doc['formato']]}"
        if arquivo.exists() and not forcar:
            dados = arquivo.read_bytes()
            anterior = _registro_anterior(destino, arquivo.name)
            registros.append(anterior or _registro(doc, url, url_final, arquivo, dados, {}))
            continue
        r = _get(cliente, url_final)
        arquivo.write_bytes(r.content)
        registros.append(_registro(doc, url, url_final, arquivo, r.content, r.headers))
    return registros


def _registro(
    doc: dict[str, Any], url: str, url_final: str, arquivo: Path, dados: bytes, cab: Any
) -> dict[str, Any]:
    return {
        "doc_id": doc["id"],
        "arquivo": arquivo.name,
        "url": url,
        "url_final": url_final,
        "sha256": sha256(dados),
        "bytes": len(dados),
        "data_acesso": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "content_type": cab.get("content-type", ""),
        "last_modified": cab.get("last-modified", ""),
    }


def _registro_anterior(destino: Path, nome: str) -> dict[str, Any] | None:
    caminho = destino / REGISTRO
    if not caminho.exists():
        return None
    for reg in json.loads(caminho.read_text(encoding="utf-8")):
        if reg["arquivo"] == nome:
            return reg
    return None


def baixar_todos(
    manifesto: dict[str, Any], ids: list[str] | None = None, forcar: bool = False
) -> list[dict[str, Any]]:
    docs = [d for d in manifesto["documentos"] if not ids or d["id"] in ids]
    todos: list[dict[str, Any]] = []
    falhas: list[tuple[str, str]] = []
    with httpx.Client(
        headers={"User-Agent": USER_AGENT}, timeout=120, follow_redirects=True
    ) as cliente:
        for doc in docs:
            try:
                regs = baixar_documento(doc, cliente, forcar=forcar)
            except (httpx.HTTPError, ValueError) as e:
                falhas.append((doc["id"], str(e).splitlines()[0]))
                print(f"  {doc['id']}: FALHOU ({falhas[-1][1]})")
                continue
            todos.extend(regs)
            for reg in regs:
                print(f"  {reg['doc_id']}: {reg['arquivo']} ({reg['bytes'] / 1024:.0f} KB)")
    for destino in (DIR_RAW, DIR_LOCAL_RAW):
        _gravar_registro(destino, [r for r in todos if (destino / r["arquivo"]).exists()])
    if falhas:
        print(f"\n{len(falhas)} documento(s) sem download: {', '.join(i for i, _ in falhas)}")
    return todos


def _gravar_registro(destino: Path, novos: list[dict[str, Any]]) -> None:
    if not novos:
        return
    caminho = destino / REGISTRO
    atuais = json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else []
    por_arquivo = {r["arquivo"]: r for r in atuais if (destino / r["arquivo"]).exists()}
    por_arquivo.update({r["arquivo"]: r for r in novos})
    regs = sorted(por_arquivo.values(), key=lambda r: r["arquivo"])
    caminho.write_text(json.dumps(regs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
