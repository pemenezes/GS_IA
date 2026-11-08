"""Testes da Fase 3: schema dos casos, ruído de voz, divisão dev/test e verificador."""

import json
import sys
from collections import Counter
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.avaliacao.casos import CANDIDATAS, COMPOSICAO, Caso, carregar
from src.avaliacao.ruido import ruido_de_voz
from src.avaliacao.split import dividir
from src.ingestao import base

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

RESPONDIVEL = {
    "id": "X-1",
    "tipo": "direta",
    "grupo": "G",
    "tema": "t",
    "pergunta": "p?",
    "deve_recusar": False,
    "chunk_ids_gold": ["D01-art362"],
    "resposta_gabarito": "r",
    "fatos_chave": ["24 horas"],
}


@pytest.mark.parametrize(
    "mudanca",
    [
        {"fatos_chave": []},
        {"chunk_ids_gold": []},
        {"deve_recusar": True},
        {"tipo": "multi_trecho"},
        {"tipo": "ruido"},
        {"armadilha_temporal": True},
        {"tipo": "nao_consta", "deve_recusar": True},
        {"tipo": "dinamica"},
    ],
)
def test_schema_rejeita_casos_incoerentes(mudanca):
    with pytest.raises(ValidationError):
        Caso.model_validate({**RESPONDIVEL, **mudanca})


def test_ruido_de_voz_e_deterministico_e_sem_pontuacao():
    a = ruido_de_voz("Paguei a conta, e agora? A luz está cortada!", 31)
    assert a == ruido_de_voz("Paguei a conta, e agora? A luz está cortada!", 31)
    assert a == a.lower() and not any(ch in a for ch in ",.?!áãé")
    assert "lus" in a.split()


def _casos_ficticios():
    casos = []
    for tipo, n in COMPOSICAO.items():
        for i in range(n):
            casos.append(
                Caso.model_validate(
                    {
                        **RESPONDIVEL,
                        "id": f"{tipo}-{i}",
                        "tipo": tipo,
                        "grupo": f"{tipo}-{i // 2}" if i < 4 else f"{tipo}-{i}",
                        "origem": "voz" if tipo == "ruido" else "texto",
                        "deve_recusar": tipo in ("nao_consta", "fora_dominio"),
                        "requer_api": tipo == "dinamica",
                        "chunk_ids_gold": []
                        if tipo in ("nao_consta", "fora_dominio")
                        else ["a", "b"]
                        if tipo == "multi_trecho"
                        else ["a"],
                        "fatos_chave": [] if tipo in ("nao_consta", "fora_dominio") else ["f"],
                        "api_esperada": {
                            "bairro": "B",
                            "data": "2026-11-11",
                            "situacao": "sem_parada",
                        }
                        if tipo == "dinamica"
                        else None,
                    }
                )
            )
    return casos


def test_split_respeita_grupos_e_proporcao():
    casos = dividir(_casos_ficticios(), 0.4, 42)
    assert Counter(c.split for c in casos) == {"dev": 24, "test": 36}
    por_grupo = {}
    for c in casos:
        por_grupo.setdefault(c.grupo, set()).add(c.split)
    assert all(len(s) == 1 for s in por_grupo.values())
    assert dividir(_casos_ficticios(), 0.4, 42) == casos


sem_base = pytest.mark.skipif(
    not base.CHUNKS.exists() or not CANDIDATAS.exists(),
    reason="base ou candidatas ainda não geradas",
)


@sem_base
def test_candidatas_passam_no_verificador():
    import validar_teste

    assert validar_teste.validar(CANDIDATAS) == []


@sem_base
def test_verificador_pega_erros_injetados(tmp_path):
    import validar_teste

    casos = [c.model_dump() for c in carregar(CANDIDATAS)]
    alvo = next(c for c in casos if c["id"] == "T-001")
    alvo["fatos_chave"] = ["36 horas"]
    trap = next(c for c in casos if c["id"] == "T-010")
    trap["fatos_proibidos"] = ["80 kWh/mês"]
    nc = next(c for c in casos if c["tipo"] == "nao_consta")
    nc["pergunta"] = "religação normal área urbana 24 horas"
    casos[0]["split"], casos[18]["split"] = "dev", "test"
    caminho = tmp_path / "ruim.jsonl"
    caminho.write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in casos), encoding="utf-8"
    )
    erros = " ".join(validar_teste.validar(caminho))
    assert "[4] T-001" in erros
    assert "[5] T-010" in erros
    assert f"[6] {nc['id']}" in erros
    assert "[7] grupo G01" in erros
