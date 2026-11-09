"""Gerador determinístico das paradas programadas simuladas (Fase 6).

Calibrado com as interrupções programadas da Enel SP em 2025 (calibracao.json, dados abertos da
ANEEL): taxa por conjunto elétrico e por dia, peso do mês e do dia da semana, hora de início e
duração. Cada distrito do município de São Paulo (IBGE) faz o papel de um conjunto elétrico.

Suposições (os dados não trazem essa informação; aprovadas pelo Pedro em 09/11/2026): tipo
60% manutenção programada, 25% obra e 15% poda; 5% dos eventos cancelados.

Garantias para o gabarito (docs/dados_simulados.md): os registros-âncora sempre existem, os
bairros e datas das âncoras não têm outros eventos, e as ausências garantidas não têm nenhum.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
from unidecode import unidecode

PASTA = Path(__file__).resolve().parent
FUSO = ZoneInfo("America/Sao_Paulo")
UTC = dt.UTC
JANELA_DIAS = 30
HORA_REFERENCIA = 8  # "agora" = data de referência às 8h (horário local), para o status

TIPOS = ["manutencao_programada", "obra", "poda"]
PESOS_TIPO = [0.60, 0.25, 0.15]
TAXA_CANCELAMENTO = 0.05
MOTIVOS = {
    "manutencao_programada": [
        "Substituição de equipamentos da rede de distribuição",
        "Manutenção preventiva em transformador",
        "Troca de cabos e conexões da rede",
        "Inspeção e manutenção de chaves da rede",
    ],
    "obra": [
        "Obra de melhoria e ampliação da rede",
        "Instalação de novos postes",
        "Remanejamento da rede para obra pública",
    ],
    "poda": [
        "Poda de árvores próximas à rede",
        "Remoção de galhos em contato com a rede",
    ],
}
COLUNAS = [
    "id",
    "distrito",
    "bairro",
    "inicio_utc",
    "fim_utc",
    "tipo",
    "motivo",
    "status",
    "criado_em",
    "atualizado_em",
]

# Registros-âncora e ausências garantidas das perguntas dinâmicas (horário local).
ANCORAS = [
    {
        "id": "PAR-ANC-01",
        "bairro": "Vila Mariana",
        "data": "2026-11-11",
        "inicio": 9,
        "fim": 13,
        "tipo": "manutencao_programada",
        "motivo": "Manutenção preventiva em transformador",
    },
    {
        "id": "PAR-ANC-02",
        "bairro": "Mooca",
        "data": "2026-11-10",
        "inicio": 13,
        "fim": 17,
        "tipo": "obra",
        "motivo": "Obra de melhoria e ampliação da rede",
    },
    {
        "id": "PAR-ANC-03",
        "bairro": "Santana",
        "data": "2026-11-13",
        "inicio": 8,
        "fim": 12,
        "tipo": "poda",
        "motivo": "Poda de árvores próximas à rede",
    },
]
AUSENCIAS = [("Butantã", "2026-11-11"), ("Lapa", "2026-11-13")]
CRIACAO_ANCORAS = dt.datetime(2026, 11, 3, 12, 0, tzinfo=UTC)


def normalizar_bairro(nome: str) -> str:
    return " ".join(unidecode(nome).lower().split())


def iso(t: dt.datetime) -> str:
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def carregar_calibracao() -> dict[str, Any]:
    return json.loads((PASTA / "calibracao.json").read_text(encoding="utf-8"))


def carregar_distritos() -> list[str]:
    dados = json.loads((PASTA / "distritos_sp.json").read_text(encoding="utf-8"))
    return [d["nome"] for d in dados["distritos"]]


def dias_locais(inicio: dt.datetime, fim: dt.datetime) -> list[dt.date]:
    """Datas locais que o intervalo [inicio, fim) toca (uma parada das 23h às 3h toca duas)."""
    a = inicio.astimezone(FUSO).date()
    b = (fim.astimezone(FUSO) - dt.timedelta(microseconds=1)).date()
    return [a + dt.timedelta(days=i) for i in range((b - a).days + 1)]


def _status(inicio: dt.datetime, fim: dt.datetime, agora: dt.datetime) -> str:
    if fim <= agora:
        return "concluida"
    return "em_andamento" if inicio <= agora else "agendada"


def gerar(
    data_referencia: str,
    seed: int = 42,
    calib: dict[str, Any] | None = None,
    distritos: list[str] | None = None,
) -> list[dict[str, str]]:
    calib = calib or carregar_calibracao()
    distritos = distritos or carregar_distritos()
    ref = dt.date.fromisoformat(data_referencia)
    agora = dt.datetime.combine(ref, dt.time(HORA_REFERENCIA), FUSO)
    rng = np.random.default_rng(seed)

    p_hora = np.array(calib["peso_hora_inicio"], dtype=float)
    p_hora /= p_hora.sum()
    p_semana = np.array(calib["peso_dia_semana"], dtype=float)
    p_semana = 7 * p_semana / p_semana.sum()
    quantis = np.array(calib["duracao_quantis_h"], dtype=float)
    taxa = calib["taxa_por_conjunto_dia"]

    bloqueados = {(normalizar_bairro(a["bairro"]), a["data"]) for a in ANCORAS}
    bloqueados |= {(normalizar_bairro(b), d) for b, d in AUSENCIAS}

    eventos = []
    for k in range(-JANELA_DIAS, JANELA_DIAS + 1):
        dia = ref + dt.timedelta(days=k)
        lam = taxa * p_semana[dia.weekday()] * calib["fator_mes"][str(dia.month)]
        for distrito in distritos:
            for _ in range(rng.poisson(lam)):
                hora = int(rng.choice(24, p=p_hora))
                minuto = int(rng.choice([0, 30]))
                u = rng.uniform(0, len(quantis) - 1)
                dur_h = max(
                    0.5, round(float(np.interp(u, np.arange(len(quantis)), quantis)) * 2) / 2
                )
                tipo = TIPOS[int(rng.choice(3, p=PESOS_TIPO))]
                motivo = MOTIVOS[tipo][int(rng.integers(len(MOTIVOS[tipo])))]
                cancelado = rng.random() < TAXA_CANCELAMENTO
                aviso_dias = int(rng.integers(3, 16))
                inicio = dt.datetime.combine(dia, dt.time(hora, minuto), FUSO)
                fim = inicio + dt.timedelta(hours=dur_h)
                chave = normalizar_bairro(distrito)
                if any((chave, d.isoformat()) in bloqueados for d in dias_locais(inicio, fim)):
                    continue
                criado = min(inicio - dt.timedelta(days=aviso_dias), agora - dt.timedelta(hours=1))
                status = "cancelada" if cancelado else _status(inicio, fim, agora)
                atualizado = {
                    "concluida": fim,
                    "em_andamento": inicio,
                    "cancelada": min(criado + dt.timedelta(days=1), agora),
                }.get(status, criado)
                eventos.append(
                    {
                        "distrito": distrito,
                        "bairro": distrito,
                        "inicio_utc": iso(inicio),
                        "fim_utc": iso(fim),
                        "tipo": tipo,
                        "motivo": motivo,
                        "status": status,
                        "criado_em": iso(criado),
                        "atualizado_em": iso(atualizado),
                    }
                )
    eventos.sort(key=lambda e: (e["inicio_utc"], e["bairro"]))
    for i, e in enumerate(eventos, start=1):
        e["id"] = f"PAR-{i:05d}"

    for a in ANCORAS:
        dia = dt.date.fromisoformat(a["data"])
        inicio = dt.datetime.combine(dia, dt.time(a["inicio"]), FUSO)
        fim = dt.datetime.combine(dia, dt.time(a["fim"]), FUSO)
        eventos.append(
            {
                "id": a["id"],
                "distrito": a["bairro"],
                "bairro": a["bairro"],
                "inicio_utc": iso(inicio),
                "fim_utc": iso(fim),
                "tipo": a["tipo"],
                "motivo": a["motivo"],
                "status": "agendada",
                "criado_em": iso(CRIACAO_ANCORAS),
                "atualizado_em": iso(CRIACAO_ANCORAS),
            }
        )
    return [{c: e[c] for c in COLUNAS} for e in eventos]


def para_csv(eventos: list[dict[str, str]]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUNAS, lineterminator="\n")
    w.writeheader()
    w.writerows(eventos)
    return buf.getvalue()


def sha256_csv(eventos: list[dict[str, str]]) -> str:
    return hashlib.sha256(para_csv(eventos).encode("utf-8")).hexdigest()
