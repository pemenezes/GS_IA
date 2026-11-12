"""Serviço do Luz Cidadã (Fase 10, parte antecipada): API e página de teste.

  uvicorn src.servico.app:app --port 8000      # e abra http://localhost:8000

Rotas:
- GET  /                página HTML para testar o assistente;
- POST /v1/perguntar    {"pergunta": str, "origem": "texto|voz|ocr", "config": "C0|C1|C2|C2M"};
- GET  /v1/configs      configurações disponíveis;
- GET  /health          status.

A pergunta passa pelo mascaramento de dados pessoais antes de ir ao modelo. O log (JSONL em
logs/) guarda só o hash da pergunta, a configuração, a latência e os ids das fontes.
"""

from __future__ import annotations

import contextlib
import copy
import dataclasses
import datetime as dt
import hashlib
import json
import tempfile
import threading
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from src.config import RAIZ, carregar_config
from src.servico.pii import mascarar

PAGINA = Path(__file__).resolve().parent / "static" / "index.html"
LOGS = RAIZ / "logs"
DESCRICOES = {
    "C0": "LLM sozinho, sem a base de normas (só para comparação)",
    "C1": "Busca nas normas e resposta com citação",
    "C2": "C1 com agente (agenda de paradas programadas)",
    "C2M": "C2 com multiconsulta: reformulações, reranker e 5 trechos (recomendado)",
}
PADRAO = "C2M"


class Pergunta(BaseModel):
    pergunta: str = Field(min_length=3, max_length=1000)
    origem: Literal["texto", "voz", "ocr"] = "texto"
    config: Literal["C0", "C1", "C2", "C2M"] = PADRAO


def construir_pipelines(cfg: dict[str, Any]) -> dict[str, Any]:
    """C0, C1, C2 e C2 com a correção M, com um só retriever e a agenda no próprio processo."""
    from fastapi.testclient import TestClient

    from src.agente.agente import C2
    from src.paradas_api import db
    from src.paradas_api.app import criar_app as criar_api_paradas
    from src.paradas_api.fonte import ClienteParadasHTTP
    from src.rag.pipeline import C0, C1, chamar_ollama
    from src.rag.retriever import Retriever

    csv_ = RAIZ / cfg["api_paradas"]["arquivo_csv"]
    caminho_db = Path(tempfile.gettempdir()) / "luz_cidada_paradas.sqlite"
    db.criar(caminho_db, csv_)
    fonte = ClienteParadasHTTP(
        "http://testserver", cliente=TestClient(criar_api_paradas(caminho_db, csv_))
    )
    retriever = Retriever(cfg)
    llm = chamar_ollama(cfg)
    cfg_m = copy.deepcopy(cfg)
    cfg_m["llm"]["num_ctx"] = max(cfg["llm"]["num_ctx"], 6144)  # 5 trechos
    return {
        "C0": C0(cfg, llm=llm),
        "C1": C1(cfg, retriever=retriever, llm=llm),
        "C2": C2(cfg, fonte=fonte, retriever=retriever, llm=llm),
        "C2M": C2(
            cfg_m,
            fonte=fonte,
            retriever=retriever,
            llm=chamar_ollama(cfg_m),
            correcoes=frozenset("M"),
        ),
    }


def _fontes_detalhadas(resposta: dict[str, Any], chunks: dict[str, dict]) -> list[dict]:
    saida = []
    for f in resposta.get("fontes", []):
        c = chunks.get(f["id"], {})
        saida.append(
            {
                **f,
                "documento": c.get("fonte")
                or ("Agenda de paradas programadas (simulada)" if f["tipo"] == "api" else None),
                "rotulo": c.get("rotulo_doc"),
                "artigo": c.get("artigo"),
                "url": c.get("url"),
            }
        )
    return saida


def criar_app(pipelines: dict[str, Any] | None = None, chunks: dict | None = None) -> FastAPI:
    """`pipelines` e `chunks` podem ser injetados (testes); senão, são carregados na partida."""
    estado: dict[str, Any] = {"pipelines": pipelines, "chunks": chunks, "erro": None}
    trava = threading.Lock()  # um LLM local: uma pergunta por vez

    @contextlib.asynccontextmanager
    async def _ciclo(_app: FastAPI):
        # Carrega os modelos em segundo plano: a página abre na hora e mostra "carregando".
        if estado["pipelines"] is None:
            threading.Thread(target=_carregar_em_segundo_plano, daemon=True).start()
        yield

    app = FastAPI(
        title="Luz Cidadã",
        version="1.0",
        description="Assistente informativo sobre direitos do consumidor de energia.",
        lifespan=_ciclo,
    )

    def _carregar() -> None:
        if estado["pipelines"] is None:
            cfg = carregar_config()
            estado["pipelines"] = construir_pipelines(cfg)
            # Aquece o modelo de embeddings e o reranker antes da primeira pergunta.
            estado["pipelines"]["C1"].retriever.buscar("aquecimento", reranker=True)
        if estado["chunks"] is None:
            from src.rag import denso

            estado["chunks"] = {c["chunk_id"]: c for c in denso.trechos_indexaveis()}

    def _carregar_em_segundo_plano() -> None:
        with trava:
            try:
                _carregar()
            except Exception as e:  # noqa: BLE001
                estado["erro"] = repr(e)[:300]

    @app.get("/", include_in_schema=False)
    def pagina() -> FileResponse:
        return FileResponse(PAGINA, media_type="text/html; charset=utf-8")

    @app.get("/health")
    def health() -> dict:
        return {
            "status": "erro" if estado["erro"] else "ok",
            "carregado": estado["pipelines"] is not None and estado["chunks"] is not None,
            "erro": estado["erro"],
        }

    @app.get("/v1/configs")
    def configs() -> dict:
        return {"padrao": PADRAO, "configs": DESCRICOES}

    @app.post("/v1/perguntar")
    def perguntar(p: Pergunta) -> dict:
        texto, dados = mascarar(p.pergunta)
        with trava:
            try:
                _carregar()
            except Exception as e:  # noqa: BLE001
                raise HTTPException(503, f"o assistente não conseguiu carregar: {e}") from e
            s = estado["pipelines"][p.config].responder(texto, origem=p.origem)
        saida = dataclasses.asdict(s)
        resposta = s.resposta.model_dump() if s.resposta else None
        corpo = {
            "config": p.config,
            "resposta": resposta,
            "fontes": _fontes_detalhadas(resposta or {}, estado["chunks"]),
            "origem_resposta": s.origem,
            "latencia_s": s.latencia_s,
            "nota_portao": s.nota_portao,
            "trechos": saida["trechos"],
            "roteamento": {k: v for k, v in (s.roteamento or {}).items() if k != "bruto"} or None,
            "consultas": saida["consultas"],
            "dados_pessoais_mascarados": dados,
            "aviso": "Orientação informativa; não substitui o atendimento da distribuidora, "
            "da ANEEL ou de um advogado.",
        }
        _registrar(p, s, dados)
        return corpo

    return app


def _registrar(p: Pergunta, s: Any, dados: list[str]) -> None:
    """Log sem dados pessoais: hash da pergunta, configuração, latência, recusa e fontes."""
    LOGS.mkdir(exist_ok=True)
    linha = {
        "quando": dt.datetime.now().isoformat(timespec="seconds"),
        "pergunta_sha256": hashlib.sha256(p.pergunta.encode()).hexdigest()[:16],
        "config": p.config,
        "origem": p.origem,
        "latencia_s": s.latencia_s,
        "recusa": bool(s.resposta and s.resposta.recusa),
        "origem_resposta": s.origem,
        "fontes": [f.id for f in (s.resposta.fontes if s.resposta else [])],
        "dados_pessoais_mascarados": dados,
    }
    with open(LOGS / "servico.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")


_APP: FastAPI | None = None


def __getattr__(nome: str) -> FastAPI:
    """`app` só é montado quando pedido (uvicorn), para os testes injetarem pipelines falsos."""
    global _APP
    if nome != "app":
        raise AttributeError(nome)
    if _APP is None:
        _APP = criar_app()
    return _APP
