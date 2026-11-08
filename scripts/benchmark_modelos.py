"""Benchmark inicial dos LLMs candidatos (Fase 0).

Para cada modelo: descarrega tudo, mede a VRAM de base, faz uma chamada de aquecimento (tempo de
carga) e três casos com contexto fictício (curto, recusa e contexto longo), amostrando a VRAM da
GPU a cada 100 ms. Grava avaliacao/runs/benchmark_modelos.csv.

Os casos não repetem o texto uns dos outros: o Ollama reaproveita o cache de um prefixo de prompt
já processado, o que deixaria a latência artificialmente baixa. Só o prompt de sistema é comum a
todos, como será em produção.

Uso:  python scripts/benchmark_modelos.py [--modelos TAG ...]
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pynvml  # noqa: E402

from src.avaliacao.vram import MonitorVRAM  # noqa: E402
from src.config import RAIZ, carregar_config  # noqa: E402
from src.rag import llm_ollama  # noqa: E402
from src.rag.schema import classificar_saida, schema_para_llm  # noqa: E402

SAIDA = RAIZ / "avaliacao" / "runs" / "benchmark_modelos.csv"

SISTEMA = (
    "Responda somente com base nos TRECHOS fornecidos, em português simples. "
    "Cite o id do trecho e copie literalmente a parte usada em trecho_citado. "
    "Se os trechos não respondem, use recusa=true e fontes vazia. "
    "Responda APENAS no JSON do schema."
)

# Textos fictícios e neutros: medem desempenho sem envolver conteúdo jurídico.
CURTO = (
    "[t1] A Biblioteca Municipal de Exemplo funciona de segunda a sexta-feira, das 8h às 18h. "
    "Aos sábados, abre das 9h às 13h. Aos domingos permanece fechada."
)
CURTO_RECUSA = (
    "[t2] O Museu de Exemplo recebe visitas guiadas às terças e quintas-feiras, às 10h. "
    "Grupos com mais de dez pessoas precisam agendar com uma semana de antecedência."
)
AQUECIMENTO = "TRECHOS:\n[w1] Texto de aquecimento.\n\nPERGUNTA: Qual é o texto?"
ATIVIDADES = [
    "oficinas de pintura",
    "aulas de violão",
    "cursos de informática",
    "clube de leitura",
    "teatro infantil",
]
UNIDADES = [
    f"[u{i}] A unidade {i} do Centro Cultural de Exemplo fica na Rua Fictícia, número {100 + i}. "
    f"Ela atende das {7 + i % 4}h às {16 + i % 5}h e oferece {ATIVIDADES[i % 5]}. "
    f"A capacidade do auditório é de {40 + 5 * i} pessoas, e o agendamento é feito na recepção."
    for i in range(1, 41)
]
CASOS = {
    "curto": f"TRECHOS:\n{CURTO}\n\nPERGUNTA: A biblioteca abre no sábado à tarde?",
    "recusa": f"TRECHOS:\n{CURTO_RECUSA}\n\nPERGUNTA: Qual é o telefone do museu?",
    "longo": "TRECHOS:\n"
    + "\n".join(UNIDADES)
    + "\n\nPERGUNTA: Qual é a capacidade do auditório da unidade 27 e o que ela oferece?",
}

COLUNAS = [
    "data_hora",
    "modelo",
    "digest",
    "tamanho_disco_gb",
    "ollama",
    "gpu",
    "driver",
    "num_ctx",
    "vram_base_mib",
    "vram_pico_mib",
    "vram_modelo_mib",
    "pct_na_gpu",
    "carga_s",
    "lat_curto_s",
    "lat_recusa_s",
    "lat_longo_s",
    "tokens_prompt_longo",
    "tokens_s_geracao",
    "tokens_s_prompt",
    "json_valido",
    "regras_b1_ok",
    "recusou_quando_devia",
    "citou_fonte_certa",
    "observacoes",
]


def medir_modelo(cfg: dict, modelo: str, info: dict, mon: MonitorVRAM) -> dict:
    host = cfg["llm"]["host"]
    opcoes = llm_ollama.opcoes_do_config(cfg["llm"])
    schema = schema_para_llm()

    for m in llm_ollama.modelos_carregados(host):
        llm_ollama.descarregar(host, m["name"])
    time.sleep(3)
    base = mon.usada_mib()

    def chamar(pergunta: str) -> tuple[dict, float]:
        msgs = [{"role": "system", "content": SISTEMA}, {"role": "user", "content": pergunta}]
        t0 = time.perf_counter()
        corpo = llm_ollama.chat_json(
            host, modelo, msgs, schema, opcoes, think=cfg["llm"]["think"], keep_alive="5m"
        )
        return corpo, time.perf_counter() - t0

    linha: dict = {"modelo": modelo, "num_ctx": opcoes["num_ctx"], "vram_base_mib": base}
    with mon:
        frio, _ = chamar(AQUECIMENTO)
        linha["carga_s"] = round(frio.get("load_duration", 0) / 1e9, 2)
        resultados = {nome: chamar(p) for nome, p in CASOS.items()}
        pct = next(
            (
                100 * m.get("size_vram", 0) / max(m.get("size", 1), 1)
                for m in llm_ollama.modelos_carregados(host)
                if m["name"] == modelo
            ),
            0,
        )
    linha["vram_pico_mib"] = mon.pico
    linha["vram_modelo_mib"] = mon.pico - base
    linha["pct_na_gpu"] = round(pct)

    validos = regras_ok = 0
    respostas = {}
    eval_tok = eval_ns = 0
    for nome, (corpo, lat) in resultados.items():
        linha[f"lat_{nome}_s"] = round(lat, 2)
        eval_tok += corpo.get("eval_count", 0)
        eval_ns += corpo.get("eval_duration", 0)
        respostas[nome], categoria = classificar_saida(corpo["message"]["content"])
        validos += categoria in ("ok", "regras")
        regras_ok += categoria == "ok"
    longo = resultados["longo"][0]
    linha["tokens_prompt_longo"] = longo.get("prompt_eval_count", 0)
    linha["tokens_s_prompt"] = round(
        longo.get("prompt_eval_count", 0) / max(longo.get("prompt_eval_duration", 1) / 1e9, 1e-9), 1
    )
    linha["tokens_s_geracao"] = round(eval_tok / max(eval_ns / 1e9, 1e-9), 1)
    linha["json_valido"] = f"{validos}/{len(CASOS)}"
    linha["regras_b1_ok"] = f"{regras_ok}/{len(CASOS)}"

    r_rec = respostas.get("recusa")
    linha["recusou_quando_devia"] = bool(r_rec and r_rec.recusa)
    citou = 0
    for nome, esperado in (("curto", "t1"), ("longo", "u27")):
        r = respostas.get(nome)
        if r and not r.recusa and any(f.id.strip("[]") == esperado for f in r.fontes):
            citou += 1
    linha["citou_fonte_certa"] = f"{citou}/2"

    linha.update(info)
    linha["data_hora"] = dt.datetime.now().isoformat(timespec="seconds")
    llm_ollama.descarregar(host, modelo)
    return linha


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cfg = carregar_config()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--modelos", nargs="+", default=list(cfg["llm"]["candidatos"]))
    args = ap.parse_args()

    host = cfg["llm"]["host"]
    locais = {m["name"]: m for m in llm_ollama.modelos_locais(host)}
    mon = MonitorVRAM()
    gpu = pynvml.nvmlDeviceGetName(mon.h)
    comum = {
        "ollama": llm_ollama.versao(host),
        "gpu": gpu if isinstance(gpu, str) else gpu.decode(),
        "driver": pynvml.nvmlSystemGetDriverVersion(),
    }

    linhas = []
    for modelo in args.modelos:
        if modelo not in locais:
            print(f"[pulado] {modelo} não está baixado")
            continue
        print(f"[medindo] {modelo} ...", flush=True)
        info = {
            **comum,
            "digest": locais[modelo]["digest"][:12],
            "tamanho_disco_gb": round(locais[modelo]["size"] / 1e9, 2),
            "observacoes": "",
        }
        try:
            linha = medir_modelo(cfg, modelo, info, mon)
        except Exception as e:  # noqa: BLE001
            linha = {**info, "modelo": modelo, "observacoes": f"erro: {e}"}
        linhas.append(linha)
        print(
            "   ",
            {
                k: linha.get(k)
                for k in (
                    "carga_s",
                    "lat_curto_s",
                    "lat_longo_s",
                    "tokens_s_geracao",
                    "tokens_s_prompt",
                    "vram_pico_mib",
                    "vram_modelo_mib",
                    "pct_na_gpu",
                    "json_valido",
                    "regras_b1_ok",
                    "recusou_quando_devia",
                    "citou_fonte_certa",
                    "observacoes",
                )
            },
            flush=True,
        )

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SAIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS, extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)
    print(f"\nSalvo em {SAIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
