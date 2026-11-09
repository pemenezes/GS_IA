"""Calibração do gerador de paradas simuladas (Fase 6) com dados abertos da ANEEL e do IBGE.

  python scripts/calibrar_paradas.py

1. Baixa o conjunto "Interrupções de Energia Elétrica nas Redes de Distribuição" de 2025
   (Parquet, licença ODbL) para base/local/aneel/ (fora do git), se ainda não existir.
2. Filtra a Enel SP (SigAgente "ELETROPAULO") e as interrupções programadas. Cada par
   (ordem de interrupção, conjunto elétrico) conta como uma parada sentida naquele conjunto.
3. Grava só agregados em src/paradas_api/calibracao.json (versionado).
4. Baixa os 96 distritos do município de São Paulo (API de localidades do IBGE) para
   src/paradas_api/distritos_sp.json.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402

from src.config import RAIZ  # noqa: E402

URL_ANEEL = (
    "https://dadosabertos.aneel.gov.br/dataset/ccb25653-f07b-4f28-84c2-62a89d1f5a56/resource/"
    "691de320-cb3d-471b-b9ec-8c1b86af8c83/download/interrupcoes-energia-eletrica-2025.parquet"
)
PAGINA_ANEEL = "https://dadosabertos.aneel.gov.br/dataset/interrupcoes-de-energia-eletrica-nas-redes-de-distribuicao"
URL_IBGE = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3550308/distritos"
PARQUET = RAIZ / "base" / "local" / "aneel" / "interrupcoes-energia-eletrica-2025.parquet"
DESTINO = RAIZ / "src" / "paradas_api"
AGENTE = "ELETROPAULO"  # sigla da Enel Distribuição São Paulo nos dados da ANEEL
DURACAO_MAX_H = 24
COLUNAS = [
    "SigAgente",
    "DscTipoInterrupcao",
    "NumOrdemInterrupcao",
    "DscConjuntoUnidadeConsumidora",
    "DatInicioInterrupcao",
    "DatFimInterrupcao",
]


def _baixar(url: str, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_suffix(".parcial")
    with (
        httpx.stream("GET", url, timeout=600, follow_redirects=True) as r,
        open(parcial, "wb") as f,
    ):
        r.raise_for_status()
        for bloco in r.iter_bytes(1 << 20):
            f.write(bloco)
    parcial.replace(destino)


def _sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def calibrar() -> dict:
    if not PARQUET.exists():
        print(f"baixando {PARQUET.name} ...", flush=True)
        _baixar(URL_ANEEL, PARQUET)
    df = pq.read_table(PARQUET, columns=COLUNAS).to_pandas()
    df = df[df["SigAgente"].str.strip() == AGENTE]
    n_conjuntos = df["DscConjuntoUnidadeConsumidora"].nunique()
    prog = df[df["DscTipoInterrupcao"].str.strip() == "Programada"]
    pares = prog.drop_duplicates(["NumOrdemInterrupcao", "DscConjuntoUnidadeConsumidora"]).copy()
    pares["dur_h"] = (
        pares["DatFimInterrupcao"] - pares["DatInicioInterrupcao"]
    ).dt.total_seconds() / 3600
    validos = pares[(pares["dur_h"] > 0) & (pares["dur_h"] <= DURACAO_MAX_H)]
    inicio = validos["DatInicioInterrupcao"]

    dias_no_ano = 365
    por_mes = inicio.dt.month.value_counts().sort_index()
    dias_mes = pd.Series({m: pd.Period(f"2025-{m:02d}").days_in_month for m in range(1, 13)})
    taxa_mes = por_mes / dias_mes
    semana = inicio.dt.day_of_week.value_counts(normalize=True).reindex(range(7), fill_value=0)
    hora = inicio.dt.hour.value_counts(normalize=True).reindex(range(24), fill_value=0)
    return {
        "fonte": "ANEEL, Interrupções de Energia Elétrica nas Redes de Distribuição (2025)",
        "pagina": PAGINA_ANEEL,
        "url": URL_ANEEL,
        "licenca": "Open Data Commons Open Database License (ODbL) 1.0",
        "atribuicao": "Contém dados da ANEEL (dadosabertos.aneel.gov.br), sob a licença ODbL.",
        "arquivo": PARQUET.name,
        "sha256": _sha256(PARQUET),
        "data_calibracao": dt.date.today().isoformat(),
        "filtro": {"SigAgente": AGENTE, "DscTipoInterrupcao": "Programada"},
        "n_registros_programados": int(len(prog)),
        "n_ordens": int(prog["NumOrdemInterrupcao"].nunique()),
        "n_pares_ordem_conjunto": int(len(pares)),
        "n_pares_descartados_duracao": int(len(pares) - len(validos)),
        "n_conjuntos_enel": int(n_conjuntos),
        "taxa_por_conjunto_dia": round(len(validos) / n_conjuntos / dias_no_ano, 5),
        # Taxa diária de cada mês dividida pela média: multiplica a taxa básica.
        "fator_mes": {int(m): round(float(v), 4) for m, v in (taxa_mes / taxa_mes.mean()).items()},
        # Participação de cada dia da semana (0 = segunda-feira).
        "peso_dia_semana": [round(float(v), 4) for v in semana],
        "peso_hora_inicio": [round(float(v), 4) for v in hora],
        # Quantis 0,5%, 1,5%, ..., 99,5% da duração em horas (amostragem por interpolação).
        "duracao_quantis_h": [
            round(float(q), 3) for q in np.quantile(validos["dur_h"], np.arange(0.005, 1, 0.01))
        ],
        "duracao_resumo_h": {
            k: round(float(v), 2)
            for k, v in validos["dur_h"].quantile([0.1, 0.25, 0.5, 0.75, 0.9]).items()
        },
    }


def distritos() -> dict:
    dados = httpx.get(URL_IBGE, timeout=30).raise_for_status().json()
    return {
        "fonte": "IBGE, API de localidades: distritos do município de São Paulo (3550308)",
        "url": URL_IBGE,
        "data_consulta": dt.date.today().isoformat(),
        "distritos": sorted(
            ({"id": d["id"], "nome": d["nome"]} for d in dados), key=lambda d: d["nome"]
        ),
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cal = calibrar()
    (DESTINO / "calibracao.json").write_text(
        json.dumps(cal, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    dis = distritos()
    (DESTINO / "distritos_sp.json").write_text(
        json.dumps(dis, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in cal.items() if "quantis" not in k}, ensure_ascii=False))
    print(f"distritos: {len(dis['distritos'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
