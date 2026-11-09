"""Conjunto extra de perguntas dinâmicas para ajustar o agente (Fase 7; fora das 60 do teste).

  python scripts/montar_dinamicas_extra.py

Bairro, datas e situação de cada pergunta são definidos à mão abaixo (data de referência:
terça-feira, 10/11/2026). Os registros esperados são calculados a partir da agenda simulada
(dados/paradas_simuladas.csv), sem as paradas canceladas.
Grava avaliacao/agente/dinamicas_extra.jsonl.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from src.config import RAIZ, carregar_config  # noqa: E402
from src.paradas_api.app import criar_app  # noqa: E402

DESTINO = RAIZ / "avaliacao" / "agente" / "dinamicas_extra.jsonl"
SETE_DIAS = [f"2026-11-{d}" for d in range(10, 17)]

PERGUNTAS = [
    (
        "DX-01",
        "Vai ter desligamento programado no Tatuapé depois de amanhã?",
        "texto",
        "Tatuapé",
        ["2026-11-12"],
        "consulta",
        False,
    ),
    (
        "DX-02",
        "Tem manutenção de energia marcada em Perdizes no sábado?",
        "texto",
        "Perdizes",
        ["2026-11-14"],
        "consulta",
        False,
    ),
    (
        "DX-03",
        "Vai faltar luz por obra no Brás no dia 13?",
        "texto",
        "Brás",
        ["2026-11-13"],
        "consulta",
        False,
    ),
    (
        "DX-04",
        "Haverá interrupção programada em Moema no dia 14/11?",
        "texto",
        "Moema",
        ["2026-11-14"],
        "consulta",
        False,
    ),
    (
        "DX-05",
        "Tem parada programada de energia no Ipiranga amanhã?",
        "texto",
        "Ipiranga",
        ["2026-11-11"],
        "consulta",
        False,
    ),
    (
        "DX-06",
        "Vai ter manutenção programada na Penha na próxima segunda-feira?",
        "texto",
        "Penha",
        ["2026-11-16"],
        "consulta",
        False,
    ),
    (
        "DX-07",
        "Tem desligamento programado na Liberdade hoje?",
        "texto",
        "Liberdade",
        ["2026-11-10"],
        "consulta",
        False,
    ),
    (
        "DX-08",
        "Vai ter manutenção programada no Carrão?",
        "texto",
        "Carrão",
        SETE_DIAS,
        "consulta",
        False,
    ),
    (
        "DX-09",
        "tem manutensao programada amanha na vila prudenti",
        "voz",
        "Vila Prudente",
        ["2026-11-11"],
        "consulta",
        False,
    ),
    (
        "DX-10",
        "Vai ter desligamento programado no Itaim amanhã?",
        "texto",
        None,
        [],
        "bairro_ambiguo",
        False,
    ),
    (
        "DX-11",
        "Tem manutenção programada de energia em Osasco amanhã?",
        "texto",
        None,
        [],
        "bairro_desconhecido",
        False,
    ),
    (
        "DX-12",
        "Vai ter manutenção programada de energia amanhã?",
        "texto",
        None,
        [],
        "sem_bairro",
        False,
    ),
    (
        "DX-13",
        "Vai ter desligamento programado no Jabaquara nesta sexta-feira? E com quanta "
        "antecedência a distribuidora tem que avisar os moradores?",
        "texto",
        "Jabaquara",
        ["2026-11-13"],
        "consulta",
        True,
    ),
]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cfg = carregar_config()
    # No Windows o SQLite fica aberto pela API em memória; a pasta temporária pode sobrar.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        cliente = TestClient(
            criar_app(Path(tmp) / "p.sqlite", RAIZ / cfg["api_paradas"]["arquivo_csv"])
        )
        linhas = []
        for id_, pergunta, origem, bairro, datas, situacao, normas in PERGUNTAS:
            ids: list[str] = []
            for d in datas:
                r = cliente.get("/paradas", params={"bairro": bairro, "data": d}).json()
                assert r["bairro_encontrado"], bairro
                ids += [
                    p["id"]
                    for p in r["paradas"]
                    if p["status"] != "cancelada" and p["id"] not in ids
                ]
            if situacao == "consulta":
                situacao = "com_parada" if ids else "sem_parada"
            linhas.append(
                {
                    "id": id_,
                    "tipo": "dinamica",
                    "origem": origem,
                    "pergunta": pergunta,
                    "requer_api": True,
                    "precisa_normas": normas,
                    "api_esperada": {
                        "bairro": bairro,
                        "datas": datas,
                        "registros_esperados": ids,
                        "situacao": situacao,
                    },
                }
            )
            print(id_, situacao, bairro, datas[:1], ids)
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with open(DESTINO, "w", encoding="utf-8", newline="\n") as f:
        for x in linhas:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"{len(linhas)} perguntas em {DESTINO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
