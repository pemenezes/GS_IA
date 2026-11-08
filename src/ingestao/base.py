"""Pipeline da base: extrai, estrutura, divide em trechos e grava os artefatos da Fase 2."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from src.config import RAIZ
from src.ingestao import download
from src.ingestao.chunking import Parametros, Tokenizador, chunks_da_unidade
from src.ingestao.estrutura import estruturar
from src.ingestao.extracao import extrair_arquivo

CHUNKS = RAIZ / "base" / "chunks.jsonl"
CHUNKS_LOCAL = RAIZ / "base" / "local" / "chunks_govbr.jsonl"
FONTES = RAIZ / "base" / "fontes.csv"
DESCARTES = RAIZ / "base" / "descartes.csv"

COLUNAS_FONTES = [
    "id",
    "documento",
    "orgao",
    "tipo_fonte",
    "formato",
    "licenca",
    "n_trechos",
    "n_tokens",
    "url",
    "url_final",
    "data_acesso",
    "versao_fonte",
    "sha256",
    "recorte",
    "texto_versionado",
    "metodo_download",
]


def arquivos_do_documento(doc: dict[str, Any]) -> list[tuple[Path, dict[str, Any]]]:
    pasta = download.dir_raw(doc)
    caminho = pasta / download.REGISTRO
    registros = json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else []
    saida = []
    for reg in sorted(registros, key=lambda r: r["arquivo"]):
        if reg["doc_id"] == doc["id"] and (pasta / reg["arquivo"]).exists():
            saida.append((pasta / reg["arquivo"], reg))
    if not saida:
        raise FileNotFoundError(f"{doc['id']}: original não baixado (rode a etapa download)")
    return saida


def _versao_fonte(doc: dict[str, Any], reg: dict[str, Any], meta: dict[str, str]) -> str:
    if doc["tipo_fonte"] == "pagina_explicativa":
        return f"página modificada em {meta['modificado_em']}" if meta.get("modificado_em") else ""
    nome = reg["url_final"].rsplit("/", 1)[-1]
    m = re.search(r"_v_?(\d+(?:\.\d+)*[A-Z]?)", nome, re.IGNORECASE)
    versao = f"arquivo {nome}" + (f" (versão {m.group(1)})" if m else "")
    if reg.get("last_modified"):
        versao += f"; Last-Modified {reg['last_modified']}"
    return versao


def processar_documento(
    doc: dict[str, Any], tok: Tokenizador, p: Parametros
) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, Any]]:
    arquivos = arquivos_do_documento(doc)
    chunks: list[dict[str, Any]] = []
    descartes: list[dict[str, str]] = []
    versoes = []
    for idx, (arq, reg) in enumerate(arquivos, start=1):
        ex = extrair_arquivo(doc, arq.read_bytes())
        est = estruturar(doc, ex, pagina=idx if len(arquivos) > 1 else None)
        versoes.append(_versao_fonte(doc, reg, ex.metadados))
        vigencia = f"versão disponível na fonte oficial em {reg['data_acesso'][:10]}" + (
            f"; {versoes[-1]}" if versoes[-1] else ""
        )
        for motivo, trecho in est.descartes:
            descartes.append(
                {
                    "doc_id": doc["id"],
                    "motivo": motivo,
                    "trecho": trecho[:120] if doc["versionar_texto"] else "",
                }
            )
        for u in est.unidades:
            for sufixo, texto, tabela in chunks_da_unidade(doc["rotulo"], u, tok, p):
                chunks.append(
                    {
                        "chunk_id": f"{doc['id']}-{u.uid}{sufixo}",
                        "doc_id": doc["id"],
                        "fonte": doc["documento"],
                        "rotulo_doc": doc["rotulo"],
                        "url": reg["url_final"],
                        "artigo": u.rotulo,
                        "hierarquia": u.hierarquia,
                        "pagina": u.pagina,
                        "data_publicacao": doc.get("data_publicacao"),
                        "data_consulta": reg["data_acesso"][:10],
                        "vigencia": vigencia,
                        "licenca": doc["licenca"],
                        "sha256_doc": reg["sha256"],
                        "tipo_fonte": doc["tipo_fonte"],
                        "versionado": doc["versionar_texto"],
                        "notas_redacao": sorted(set(u.notas)),
                        "contem_tabela": tabela,
                        "alerta": doc.get("alerta"),
                        "n_tokens": tok.contar(texto),
                        "texto": texto,
                    }
                )
    info = {
        "arquivos": arquivos,
        "versao_fonte": " / ".join(v for v in versoes if v),
    }
    return chunks, descartes, info


def construir(manifesto: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    tok = Tokenizador(cfg["embeddings"]["modelo"], cfg["embeddings"].get("revisao"))
    p = Parametros.do_config(cfg)
    todos: list[dict[str, Any]] = []
    todos_descartes: list[dict[str, str]] = []
    linhas_fontes = []
    for doc in manifesto["documentos"]:
        chunks, descartes, info = processar_documento(doc, tok, p)
        todos += chunks
        todos_descartes += descartes
        regs = [reg for _, reg in info["arquivos"]]
        linhas_fontes.append(
            {
                "id": doc["id"],
                "documento": doc["documento"],
                "orgao": doc["orgao"],
                "tipo_fonte": doc["tipo_fonte"],
                "formato": doc["formato"],
                "licenca": doc["licenca"],
                "n_trechos": len(chunks),
                "n_tokens": sum(c["n_tokens"] for c in chunks),
                "url": " ".join(doc["urls"]),
                "url_final": " ".join(r["url_final"] for r in regs),
                "data_acesso": " ".join(r["data_acesso"] for r in regs),
                "versao_fonte": info["versao_fonte"],
                "sha256": " ".join(r["sha256"] for r in regs),
                "recorte": _descrever_recorte(doc["recorte"]),
                "texto_versionado": "sim"
                if doc["versionar_texto"]
                else "não (CC BY-ND; só link e hash)",
                "metodo_download": " ".join(r.get("metodo", "automatico") for r in regs),
            }
        )
        print(f"  {doc['id']}: {len(chunks)} trechos, {len(descartes)} descartes")

    ids = Counter(c["chunk_id"] for c in todos)
    repetidos = [i for i, n in ids.items() if n > 1]
    if repetidos:
        raise ValueError(f"chunk_id repetido: {repetidos[:5]}")

    _gravar_jsonl(CHUNKS, [c for c in todos if c["versionado"]])
    _gravar_jsonl(CHUNKS_LOCAL, [c for c in todos if not c["versionado"]])
    _gravar_csv(FONTES, COLUNAS_FONTES, linhas_fontes)
    _gravar_csv(DESCARTES, ["doc_id", "motivo", "trecho"], todos_descartes)
    return {"chunks": todos, "descartes": todos_descartes, "fontes": linhas_fontes}


def _descrever_recorte(recorte: dict[str, Any]) -> str:
    tipo = recorte["tipo"]
    if tipo == "titulo":
        texto = f"só o Título {recorte['titulo']}"
    elif tipo == "secoes":
        texto = "seções " + ", ".join(recorte["secoes"])
    elif tipo == "dispositivos_proprios":
        texto = "só dispositivos próprios (sem artigos que alteram outras normas)"
    else:
        texto = "integral"
    if recorte.get("excluir_anexos"):
        texto += ", sem os Anexos " + " e ".join(recorte["excluir_anexos"])
    return texto


def _gravar_jsonl(caminho: Path, linhas: list[dict[str, Any]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        for linha in linhas:
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")


def _gravar_csv(caminho: Path, colunas: list[str], linhas: list[dict[str, Any]]) -> None:
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colunas, lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)


def carregar_chunks(incluir_locais: bool = True) -> list[dict[str, Any]]:
    """Trechos para as fases seguintes: os versionados mais os gerados localmente."""
    caminhos = [CHUNKS] + ([CHUNKS_LOCAL] if incluir_locais and CHUNKS_LOCAL.exists() else [])
    saida = []
    for caminho in caminhos:
        with open(caminho, encoding="utf-8") as f:
            saida += [json.loads(linha) for linha in f if linha.strip()]
    return saida
