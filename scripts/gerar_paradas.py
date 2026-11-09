"""Gera as paradas simuladas (Fase 6): CSV versionado, banco SQLite e figura de calibração.

  python scripts/gerar_paradas.py

Usa a semente e a data de referência do config.yaml e os parâmetros de
src/paradas_api/calibracao.json (scripts/calibrar_paradas.py).
"""

from __future__ import annotations

import datetime as dt
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from src.config import RAIZ, carregar_config  # noqa: E402
from src.paradas_api import db  # noqa: E402
from src.paradas_api.gerador import (  # noqa: E402
    FUSO,
    carregar_calibracao,
    gerar,
    para_csv,
    sha256_csv,
)

FIGURA = RAIZ / "docs" / "img" / "paradas_calibracao.png"
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def _local(iso_utc: str) -> dt.datetime:
    return (
        dt.datetime.strptime(iso_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.UTC).astimezone(FUSO)
    )


def figura(eventos: list[dict], calib: dict) -> None:
    sim = [e for e in eventos if not e["id"].startswith("PAR-ANC")]
    inicio = [_local(e["inicio_utc"]) for e in sim]
    dur = [
        (_local(e["fim_utc"]) - i).total_seconds() / 3600 for e, i in zip(sim, inicio, strict=True)
    ]
    n = len(sim)
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.6))
    sem = Counter(i.weekday() for i in inicio)
    x = np.arange(7)
    ax[0].bar(x - 0.2, calib["peso_dia_semana"], 0.4, label="Enel SP 2025 (ANEEL)", color="#2b6cb0")
    ax[0].bar(x + 0.2, [sem[d] / n for d in range(7)], 0.4, label="simulado", color="#ed8936")
    ax[0].set_xticks(x, DIAS)
    ax[0].set_title("Dia da semana")
    ax[0].legend(fontsize=8)
    hora = Counter(i.hour for i in inicio)
    h = np.arange(24)
    ax[1].bar(h - 0.2, calib["peso_hora_inicio"], 0.4, color="#2b6cb0")
    ax[1].bar(h + 0.2, [hora[k] / n for k in range(24)], 0.4, color="#ed8936")
    ax[1].set_title("Hora de início")
    q = np.array(calib["duracao_quantis_h"])
    ax[2].plot(np.sort(q), np.linspace(0.005, 0.995, len(q)), color="#2b6cb0", label="Enel SP 2025")
    ax[2].plot(np.sort(dur), np.linspace(0, 1, n), color="#ed8936", label="simulado")
    ax[2].set_xlim(0, 12)
    ax[2].set_xlabel("horas")
    ax[2].set_title("Duração (distribuição acumulada)")
    ax[2].legend(fontsize=8)
    fig.suptitle(f"Paradas programadas: dados reais x simulação ({n} eventos simulados)")
    plt.tight_layout()
    FIGURA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURA, dpi=120)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cfg = carregar_config()
    calib = carregar_calibracao()
    eventos = gerar(cfg["data_referencia"], seed=cfg["seed"], calib=calib)
    csv_destino = RAIZ / cfg["api_paradas"]["arquivo_csv"]
    csv_destino.parent.mkdir(parents=True, exist_ok=True)
    csv_destino.write_text(para_csv(eventos), encoding="utf-8", newline="")
    db.criar(RAIZ / cfg["api_paradas"]["arquivo_db"], csv_destino)
    figura(eventos, calib)
    print(f"{len(eventos)} paradas ({sum(e['id'].startswith('PAR-ANC') for e in eventos)} âncoras)")
    print("status:", dict(Counter(e["status"] for e in eventos)))
    print("tipo:", dict(Counter(e["tipo"] for e in eventos)))
    print("bairros com parada:", len({e["bairro"] for e in eventos}))
    print("sha256 do CSV:", sha256_csv(eventos))
    print(f"CSV: {csv_destino.relative_to(RAIZ)} | figura: {FIGURA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
