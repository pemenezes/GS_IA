"""Verificação do ambiente (Fase 0).

Imprime SO, CPU, RAM, GPU/VRAM, versões e testa:
  1. Ollama: servidor no ar, modelo do config.yaml baixado, geração JSON válida < 15 s;
  2. Embeddings: bge-m3 em CPU (dimensão, normalização, latência por consulta).

Uso:  python scripts/check_env.py [--modelo TAG] [--sem-embeddings]
Sai com código 1 se alguma verificação obrigatória falhar.
"""

from __future__ import annotations

import argparse
import importlib.metadata as md
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError  # noqa: E402

from src.config import carregar_config  # noqa: E402
from src.rag import llm_ollama  # noqa: E402
from src.rag.schema import Resposta  # noqa: E402

LIMITE_JSON_S = 15.0
PACOTES = [
    "torch",
    "sentence-transformers",
    "transformers",
    "faiss-cpu",
    "rank-bm25",
    "ollama",
    "fastapi",
    "uvicorn",
    "pydantic",
    "httpx",
    "pymupdf",
    "pdfplumber",
    "beautifulsoup4",
    "pandas",
    "numpy",
    "scikit-learn",
    "rapidfuzz",
    "dateparser",
    "pytest",
    "ruff",
]

# Contexto fictício e neutro: testa formato e citação sem tocar em conteúdo jurídico.
TRECHO_TESTE = (
    "A Biblioteca Municipal de Exemplo funciona de segunda a sexta-feira, das 8h às 18h. "
    "Aos sábados, abre das 9h às 13h. Aos domingos permanece fechada."
)
MENSAGENS_TESTE = [
    {
        "role": "system",
        "content": (
            "Responda somente com base nos TRECHOS fornecidos, em português simples. "
            "Cite o id do trecho e copie literalmente a parte usada em trecho_citado. "
            "Se os trechos não respondem, use recusa=true. Responda APENAS no JSON do schema."
        ),
    },
    {
        "role": "user",
        "content": f"TRECHOS:\n[teste-1] {TRECHO_TESTE}\n\nPERGUNTA: A biblioteca abre no "
        "sábado à tarde?",
    },
]

falhas: list[str] = []


def ok(msg: str) -> None:
    print(f"  [OK]    {msg}")


def aviso(msg: str) -> None:
    print(f"  [AVISO] {msg}")


def falha(msg: str) -> None:
    print(f"  [FALHA] {msg}")
    falhas.append(msg)


def secao(titulo: str) -> None:
    print(f"\n== {titulo} ==")


def checar_sistema() -> None:
    secao("Sistema")
    ok(f"SO: {platform.platform()}")
    ok(f"CPU: {platform.processor()} ({__import__('os').cpu_count()} threads lógicas)")
    try:
        import psutil

        ok(f"RAM: {psutil.virtual_memory().total / 2**30:.1f} GB")
    except ImportError:
        aviso("psutil ausente; RAM não verificada")
    py = sys.version_info
    if (3, 11) <= (py.major, py.minor) <= (3, 12):
        ok(f"Python {platform.python_version()} ({sys.executable})")
    else:
        falha(f"Python {platform.python_version()}: o projeto exige 3.11 ou 3.12")


def checar_gpu() -> None:
    secao("GPU")
    try:
        saida = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,driver_version",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        ).stdout.strip()
        nome, total, usada, driver = [x.strip() for x in saida.splitlines()[0].split(",")]
        livre = int(total) - int(usada)
        ok(f"{nome} | driver {driver} | VRAM {total} MiB (usada {usada}, livre {livre})")
        if livre < 4000:
            aviso(f"Só {livre} MiB livres: feche apps que usam GPU antes de avaliar")
    except (FileNotFoundError, subprocess.SubprocessError) as e:
        falha(f"nvidia-smi indisponível: {e}")

    try:
        import torch

        if torch.cuda.is_available():
            cap = torch.cuda.get_device_capability(0)
            ok(
                f"torch {torch.__version__} | CUDA {torch.version.cuda} | "
                f"{torch.cuda.get_device_name(0)} (sm_{cap[0]}{cap[1]})"
            )
            x = torch.ones(1024, 1024, device="cuda", dtype=torch.float16)
            torch.cuda.synchronize()
            ok(f"kernel fp16 na GPU executou (soma={float((x @ x).float().sum()):.0f})")
        else:
            falha(f"torch {torch.__version__} sem CUDA (indexação de embeddings ficaria em CPU)")
    except ImportError:
        falha("torch não instalado")


def checar_versoes() -> None:
    secao("Versões das bibliotecas")
    for p in PACOTES:
        try:
            ok(f"{p}=={md.version(p)}")
        except md.PackageNotFoundError:
            falha(f"{p} não instalado")


def checar_ollama(cfg: dict, modelo: str) -> None:
    secao("Ollama")
    host = cfg["llm"]["host"]
    try:
        ok(f"servidor {host} no ar, versão {llm_ollama.versao(host)}")
    except Exception as e:  # noqa: BLE001
        falha(f"servidor Ollama inacessível em {host}: {e}")
        return

    locais = {m["name"]: m for m in llm_ollama.modelos_locais(host)}
    for cand in cfg["llm"].get("candidatos", []):
        status = "baixado" if cand in locais else "NÃO baixado"
        print(f"          candidato {cand}: {status}")
    if modelo not in locais:
        falha(f"modelo {modelo} não está baixado (ollama pull {modelo})")
        return

    opcoes = llm_ollama.opcoes_do_config(cfg["llm"])
    t0 = time.perf_counter()
    try:
        corpo = llm_ollama.chat_json(
            host,
            modelo,
            MENSAGENS_TESTE,
            Resposta.model_json_schema(),
            opcoes,
            think=cfg["llm"]["think"],
            keep_alive=cfg["llm"]["keep_alive"],
        )
    except Exception as e:  # noqa: BLE001
        falha(f"geração falhou: {e}")
        return
    dt = time.perf_counter() - t0

    conteudo = corpo["message"]["content"]
    try:
        resp = Resposta.model_validate_json(conteudo)
        ok("JSON válido segundo o schema Resposta")
    except ValidationError as e:
        falha(f"JSON inválido: {e.errors()[:2]}\n          saída: {conteudo[:300]}")
        return
    print("          " + json.dumps(resp.model_dump(), ensure_ascii=False)[:400])

    tps = corpo.get("eval_count", 0) / max(corpo.get("eval_duration", 1) / 1e9, 1e-9)
    carga = corpo.get("load_duration", 0) / 1e9
    msg = f"tempo total {dt:.1f} s (carga {carga:.1f} s), geração {tps:.1f} tokens/s"
    (ok if dt < LIMITE_JSON_S else falha)(f"{msg} [limite {LIMITE_JSON_S:.0f} s]")
    if not resp.recusa and any(f.id == "teste-1" for f in resp.fontes):
        ok("citou a fonte do trecho de teste")
    else:
        aviso("não citou a fonte esperada (informativo; avaliado nas fases 5+)")

    for m in llm_ollama.modelos_carregados(host):
        if m["name"] == modelo:
            pct = 100 * m.get("size_vram", 0) / max(m.get("size", 1), 1)
            ok(f"carregado: {m['size'] / 2**30:.2f} GB, {pct:.0f}% na GPU")
            if pct < 100:
                aviso("parte do modelo está na CPU (offload): latência maior")


def checar_embeddings(cfg: dict) -> None:
    secao("Embeddings")
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        falha(f"sentence-transformers indisponível: {e}")
        return
    nome = cfg["embeddings"]["modelo"]
    disp = cfg["embeddings"]["dispositivo_consulta"]
    t0 = time.perf_counter()
    modelo = SentenceTransformer(nome, device=disp)
    modelo.max_seq_length = cfg["embeddings"]["max_length"]
    ok(f"{nome} carregado em {disp} ({time.perf_counter() - t0:.1f} s)")

    frases = [
        "Fiquei sem luz em casa. Em quanto tempo a energia deve voltar?",
        "Prazo para restabelecimento do fornecimento de energia elétrica.",
        "Receita de bolo de cenoura com cobertura de chocolate.",
    ]
    modelo.encode(frases[:1], normalize_embeddings=True)
    t0 = time.perf_counter()
    vetores = modelo.encode(frases, normalize_embeddings=cfg["embeddings"]["normalizar"])
    ms = (time.perf_counter() - t0) * 1000 / len(frases)
    dim = vetores.shape[1]
    (ok if dim == 1024 else falha)(f"dimensão {dim} (esperado 1024)")
    normas = np.linalg.norm(vetores, axis=1)
    (ok if np.allclose(normas, 1, atol=1e-3) else falha)(f"normas {normas.round(3).tolist()}")
    ok(f"latência média {ms:.0f} ms por consulta (CPU)")
    sim = vetores @ vetores.T
    if sim[0, 1] > sim[0, 2]:
        ok(
            f"sanidade semântica: sim(pergunta, prazo)={sim[0, 1]:.2f} > "
            f"sim(pergunta, receita)={sim[0, 2]:.2f}"
        )
    else:
        falha("sanidade semântica falhou: frase sem relação ficou mais próxima")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--modelo", help="tag do Ollama (padrão: llm.modelo do config.yaml)")
    ap.add_argument("--sem-embeddings", action="store_true", help="pula o teste do bge-m3")
    args = ap.parse_args()

    cfg = carregar_config()
    modelo = args.modelo or cfg["llm"]["modelo"]

    checar_sistema()
    checar_gpu()
    checar_versoes()
    checar_ollama(cfg, modelo)
    if not args.sem_embeddings:
        checar_embeddings(cfg)

    secao("Resultado")
    if falhas:
        print(f"  {len(falhas)} falha(s):")
        for f in falhas:
            print(f"   - {f.splitlines()[0]}")
        return 1
    print("  Ambiente OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
