"""Avaliação da geração (Fases 5 e 7): roda C0, C1 ou C2 sobre um conjunto e grava as saídas.

  python scripts/avaliar_geracao.py rodar --config C2 --conjunto dev [--modelo TAG]
         [--sem-estruturada]
  python scripts/avaliar_geracao.py resumo

Conjuntos: dev e test (congelados), calibracao (45 perguntas da Fase 4, só comportamento),
injecao (5 tentativas de prompt injection) e dinamicas_extra (13 perguntas sobre a agenda,
Fase 7). O test roda uma única vez, com a configuração do config.yaml (modelo e saída
estruturada). O C2 usa a API de paradas no próprio processo, recriada a partir do CSV.

Saídas em avaliacao/runs/geracao/ (versionadas; citações de páginas gov.br trocadas por hash) e
avaliacao/runs/local/geracao/ (completas, fora do git). Resumo em avaliacao/geracao/.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import datetime as dt
import functools
import json
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.avaliacao.casos import LOCK, Caso, carregar_congelado  # noqa: E402
from src.avaliacao.geracao import (  # noqa: E402
    avaliar_dinamica,
    avaliar_linha,
    mascarar_govbr,
    resumir,
)
from src.avaliacao.vram import MonitorVRAM  # noqa: E402
from src.config import RAIZ, carregar_config  # noqa: E402
from src.rag import denso, llm_ollama, prompt  # noqa: E402
from src.rag.pipeline import C0, C1, chamar_ollama  # noqa: E402
from src.rag.validador import numeros  # noqa: E402

RUNS = RAIZ / "avaliacao" / "runs" / "geracao"
RUNS_LOCAL = RAIZ / "avaliacao" / "runs" / "local" / "geracao"
RESUMO = RAIZ / "avaliacao" / "geracao"
CALIBRACAO = RAIZ / "avaliacao" / "retrieval" / "calibracao.jsonl"
INJECAO = RESUMO / "injecao.jsonl"
DINAMICAS_EXTRA = RAIZ / "avaliacao" / "agente" / "dinamicas_extra.jsonl"
CONJUNTOS = ["dev", "test", "calibracao", "injecao", "dinamicas_extra"]


def _ler_jsonl(arq: Path) -> list[dict[str, Any]]:
    with open(arq, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def _itens(conjunto: str) -> list[dict[str, Any]]:
    """Perguntas do conjunto: id, tipo, pergunta, Caso (dev e test) e o esperado da agenda."""
    if conjunto in ("dev", "test"):
        return [
            {
                "id": c.id,
                "tipo": c.tipo,
                "pergunta": c.pergunta,
                "caso": c,
                "requer_api": c.requer_api,
                "api_esperada": c.api_esperada.model_dump() if c.api_esperada else None,
            }
            for c in carregar_congelado(conjunto)
        ]
    if conjunto == "dinamicas_extra":
        return [{**x, "caso": None} for x in _ler_jsonl(DINAMICAS_EXTRA)]
    if conjunto == "calibracao":
        return [
            {**x, "tipo": x["subtipo"], "caso": None, "requer_api": False}
            for x in _ler_jsonl(CALIBRACAO)
        ]
    return [{**x, "tipo": "injecao", "caso": None} for x in _ler_jsonl(INJECAO)]


@functools.cache
def _contexto_agenda() -> tuple[dict[str, tuple[int, int]], list[str]]:
    """Hora local de início e de fim de cada parada simulada, e a lista de bairros."""
    from src.paradas_api.gerador import FUSO, carregar_distritos

    cfg = carregar_config()
    horas = {}
    with open(RAIZ / cfg["api_paradas"]["arquivo_csv"], encoding="utf-8") as f:
        for p in csv.DictReader(f):
            ini, fim = (
                dt.datetime.strptime(p[k], "%Y-%m-%dT%H:%M:%SZ")
                .replace(tzinfo=dt.UTC)
                .astimezone(FUSO)
                for k in ("inicio_utc", "fim_utc")
            )
            horas[p["id"]] = (ini.hour, fim.hour)
    return horas, carregar_distritos()


def _criar_c2(cfg: dict[str, Any], **kw: Any) -> Any:
    """C2 com a API de paradas no próprio processo (banco recriado a partir do CSV)."""
    from fastapi.testclient import TestClient

    from src.agente.agente import C2
    from src.paradas_api import db
    from src.paradas_api.app import criar_app
    from src.paradas_api.fonte import ClienteParadasHTTP

    caminho_db = RUNS_LOCAL.parent / "paradas_avaliacao.sqlite"
    csv_ = RAIZ / cfg["api_paradas"]["arquivo_csv"]
    db.criar(caminho_db, csv_)
    cliente = TestClient(criar_app(caminho_db, csv_))
    fonte = ClienteParadasHTTP("http://testserver", cliente=cliente)
    return C2(cfg, fonte=fonte, **kw)


def _slug(modelo: str) -> str:
    return modelo.replace(":", "_").replace("/", "_").replace(".", "")


def _nome_run(config: str, conjunto: str, modelo: str, estruturada: bool) -> str:
    return f"{config}_{conjunto}_{_slug(modelo)}{'' if estruturada else '_livre'}"


def _avaliar_sem_gabarito(item: dict[str, Any], saida: dict[str, Any]) -> dict[str, Any]:
    """Calibração e injeção: só comportamento (recusa, JSON, citação verificável)."""
    r = saida["resposta"]
    primeira = saida["tentativas"][0] if saida["tentativas"] else None
    ultima = saida["tentativas"][-1] if saida["tentativas"] else {}
    tipo = "respondivel" if item["tipo"] == "respondivel" else item["tipo"]
    m = {
        "id": item["id"],
        "tipo": tipo,
        "json_valido_1a": None if primeira is None else primeira["categoria"] in ("ok", "regras"),
        "regras_1a": None if primeira is None else primeira["categoria"] == "ok",
        "valida_final": r is not None,
        "recusou": bool(r and r["recusa"]),
        "origem": saida["origem"],
        "acuracia": None,
        "alucinacao": None,
        "citacao_correta": None,
    }
    if r and not r["recusa"]:
        m["citacao_verificavel"] = any(
            c["fornecido"] and c["casamento"] != "nenhum" for c in ultima.get("citacoes", [])
        )
        m["numeros_na_resposta"] = sorted(numeros(r["resposta"]))
    return m


def _metricas(
    caso: Caso | None, item: dict[str, Any], saida: dict[str, Any], chunks: dict[str, dict]
) -> dict[str, Any]:
    if caso is None:
        m = _avaliar_sem_gabarito(item, saida)
    else:
        gold = [chunks[g]["texto"] for g in caso.gold_v2 if g in chunks]
        fornecidos = [
            chunks[t["chunk_id"]]["texto"] for t in saida["trechos"] if t["chunk_id"] in chunks
        ]
        m = avaliar_linha(caso, saida, gold, fornecidos)
    if saida.get("roteamento") and item.get("requer_api") is not None:
        m["roteamento_correto"] = saida["roteamento"]["precisa_agenda"] == item["requer_api"]
        m["roteou_agenda"] = saida["roteamento"]["precisa_agenda"]
        m["roteador_origem"] = saida["roteamento"]["origem"]
    if item.get("api_esperada"):
        horas, bairros = _contexto_agenda()
        m["acerto_dinamica"] = avaliar_dinamica(item["api_esperada"], saida, horas, bairros)
    return m


def _gravar(nome: str, linhas: list[dict[str, Any]], govbr: dict[str, str]) -> None:
    """Saída completa (local, fora do git) e versionada (citações gov.br trocadas por hash)."""
    for caminho, dados in (
        (RUNS_LOCAL / f"{nome}.jsonl", linhas),
        (RUNS / f"{nome}.jsonl", [mascarar_govbr(x, govbr) for x in linhas]),
    ):
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8", newline="\n") as f:
            for x in dados:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")


def _hash_agente() -> str:
    from src.agente.prompts import hash_prompts_agente

    return hash_prompts_agente()


def rodar(cfg: dict[str, Any], args: argparse.Namespace) -> None:
    modelo = args.modelo or cfg["llm"]["modelo"]
    estruturada = not args.sem_estruturada and cfg["geracao"]["estruturada"]
    if args.conjunto == "test" and (modelo, estruturada) != (cfg["llm"]["modelo"], True):
        raise SystemExit("o test só roda com a configuração escolhida no config.yaml")
    nome = _nome_run(args.config, args.conjunto, modelo, estruturada)
    destino = RUNS / f"{nome}.jsonl"
    if args.conjunto == "test" and destino.exists():
        raise SystemExit(f"{destino.name} já existe: o test roda uma única vez")

    host = cfg["llm"]["host"]
    locais = {m["name"]: m for m in llm_ollama.modelos_locais(host)}
    esperado = cfg["llm"]["candidatos"].get(modelo)
    if modelo not in locais or (esperado and locais[modelo]["digest"] != esperado):
        raise SystemExit(f"{modelo} ausente ou com digest diferente do travado no config.yaml")
    for m in llm_ollama.modelos_carregados(host):
        if m["name"] != modelo:
            llm_ollama.descarregar(host, m["name"])

    chunks = {c["chunk_id"]: c for c in denso.trechos_indexaveis()}
    govbr = {i: c["texto"] for i, c in chunks.items() if not c.get("versionado", True)}
    llm = chamar_ollama(cfg, modelo)
    kw = {"llm": llm, "estruturada": estruturada}
    pipe = {"C0": C0, "C1": C1, "C2": _criar_c2}[args.config](cfg, **kw)
    # Aquecimento: carga do LLM na GPU e do modelo de embeddings na CPU fora da medição.
    llm([{"role": "user", "content": "Responda com um JSON vazio."}], {"type": "object"})
    if isinstance(pipe, C1):
        pipe.recuperar("aquecimento")

    itens = _itens(args.conjunto)
    linhas, metricas, latencias = [], [], []
    mon = MonitorVRAM()
    with mon:
        for item in itens:
            s = pipe.responder(item["pergunta"])
            saida = dataclasses.asdict(s)
            saida["resposta"] = s.resposta.model_dump() if s.resposta else None
            m = _metricas(item["caso"], item, saida, chunks)
            linhas.append(
                {
                    "id": item["id"],
                    "tipo": item["tipo"],
                    "pergunta": item["pergunta"],
                    "requer_api": item.get("requer_api"),
                    "api_esperada": item.get("api_esperada"),
                    "saida": saida,
                    "metricas": m,
                }
            )
            metricas.append(m)
            latencias.append(s.latencia_s)
            r = s.resposta
            extra = (
                f" rot={m.get('roteou_agenda')}/{m.get('roteador_origem')}"
                f" din={m.get('acerto_dinamica')}"
                if s.roteamento or item.get("api_esperada")
                else ""
            )
            print(
                f"  {item['id']:<8} {item['tipo']:<13} {s.origem:<14} {s.latencia_s:6.2f}s "
                f"recusa={bool(r and r.recusa)!s:<5} acur={m.get('acuracia')} "
                f"cit={m.get('citacao_correta', m.get('citacao_verificavel'))}{extra}",
                flush=True,
            )

    _gravar(nome, linhas, govbr)
    meta = {
        "run": nome,
        "config": args.config,
        "conjunto": args.conjunto,
        "modelo": modelo,
        "digest": locais[modelo]["digest"],
        "estruturada": estruturada,
        "hash_prompts": prompt.hash_prompts(),
        **({"hash_prompts_agente": _hash_agente()} if args.config == "C2" else {}),
        "teste_lock": LOCK.read_text(encoding="utf-8").split()[0],
        "retrieval": {k: cfg["retrieval"][k] for k in ("hibrido", "top_k_final", "limiar_recusa")},
        "llm": {k: cfg["llm"][k] for k in ("num_ctx", "temperature", "top_p", "seed", "think")},
        "ollama": llm_ollama.versao(host),
        "vram_pico_mib": mon.pico,
        "data_hora": dt.datetime.now().isoformat(timespec="seconds"),
        "resumo": resumir(metricas, latencias),
    }
    (RUNS / f"{nome}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(
        json.dumps({k: v for k, v in meta["resumo"].items() if k != "por_tipo"}, ensure_ascii=False)
    )


def resumo(_cfg: dict[str, Any], _args: argparse.Namespace) -> None:
    """Recalcula as métricas de todas as execuções a partir das saídas completas e tabula."""
    casos = {c.id: c for c in carregar_congelado()}
    chunks = {c["chunk_id"]: c for c in denso.trechos_indexaveis()}
    govbr = {i: c["texto"] for i, c in chunks.items() if not c.get("versionado", True)}
    extras = {x["id"]: x for x in _ler_jsonl(DINAMICAS_EXTRA)} if DINAMICAS_EXTRA.exists() else {}
    linhas = []
    for arq in sorted(RUNS_LOCAL.glob("*.jsonl")):
        arq_meta = RUNS / f"{arq.stem}.meta.json"
        if not arq_meta.exists():
            continue
        meta = json.loads(arq_meta.read_text(encoding="utf-8"))
        runs = _ler_jsonl(arq)
        for x in runs:
            caso = casos.get(x["id"]) if meta["conjunto"] in ("dev", "test") else None
            # Execuções anteriores à Fase 7 não gravavam o esperado da agenda.
            if caso is not None:
                x["requer_api"] = caso.requer_api
                x["api_esperada"] = caso.api_esperada.model_dump() if caso.api_esperada else None
            elif meta["conjunto"] == "calibracao":
                x["requer_api"] = False
            elif meta["conjunto"] == "dinamicas_extra":
                x["requer_api"] = True
                x["api_esperada"] = extras[x["id"]]["api_esperada"]
            x["metricas"] = _metricas(caso, x, x["saida"], chunks)
        _gravar(arq.stem, runs, govbr)
        meta["resumo"] = r = resumir(
            [x["metricas"] for x in runs], [x["saida"]["latencia_s"] for x in runs]
        )
        arq_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

        def fmt(chave: str, r: dict[str, Any] = r) -> str:
            t = r[chave]
            return f"{t['k']}/{t['n']}" if t["n"] else ""

        linhas.append(
            {
                "run": meta["run"],
                "config": meta["config"],
                "conjunto": meta["conjunto"],
                "modelo": meta["modelo"],
                "estruturada": meta["estruturada"],
                "json_valido_1a": fmt("json_valido_1a"),
                "regras_1a": fmt("regras_1a"),
                "acuracia": fmt("acuracia"),
                "citacao_correta": fmt("citacao_correta"),
                "suspeita_alucinacao": fmt("alucinacao"),
                "recusa_correta": fmt("recusa_correta"),
                "recusa_indevida": fmt("recusa_indevida"),
                "recusa_dinamicas": fmt("recusa_dinamicas"),
                "recusa_nega_regra": fmt("recusa_nega_regra"),
                "citacao_verificavel": fmt("citacao_verificavel"),
                "acerto_dinamicas": fmt("acerto_dinamicas"),
                "roteamento_correto": fmt("roteamento_correto"),
                "latencia_p50_s": r["latencia_p50_s"],
                "latencia_p95_s": r["latencia_p95_s"],
                "vram_pico_mib": meta["vram_pico_mib"],
            }
        )
    RESUMO.mkdir(parents=True, exist_ok=True)
    with open(RESUMO / "resumo_runs.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)
    for x in linhas:
        print(x)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="etapa", required=True)
    r = sub.add_parser("rodar")
    r.add_argument("--config", choices=["C0", "C1", "C2"], required=True)
    r.add_argument("--conjunto", choices=CONJUNTOS, required=True)
    r.add_argument("--modelo")
    r.add_argument("--sem-estruturada", action="store_true")
    sub.add_parser("resumo")
    args = ap.parse_args()
    cfg = carregar_config()
    t0 = time.perf_counter()
    {"rodar": rodar, "resumo": resumo}[args.etapa](cfg, args)
    print(f"({time.perf_counter() - t0:.0f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
