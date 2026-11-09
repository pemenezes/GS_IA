"""Testes da Fase 6 (sem rede): gerador, garantias do gabarito, rotas, chave e cliente."""

import datetime as dt
import hashlib

import pytest
from fastapi.testclient import TestClient

from src.avaliacao.casos import carregar_congelado
from src.config import RAIZ, carregar_config
from src.paradas_api.app import criar_app
from src.paradas_api.fonte import ClienteParadasHTTP
from src.paradas_api.gerador import (
    ANCORAS,
    AUSENCIAS,
    FUSO,
    dias_locais,
    gerar,
    para_csv,
    sha256_csv,
)

CFG = carregar_config()
ENV = "PARADAS_API_KEY_TESTE"


@pytest.fixture(scope="module")
def eventos():
    return gerar(CFG["data_referencia"], seed=CFG["seed"])


@pytest.fixture
def cliente(tmp_path, eventos):
    csv_ = tmp_path / "paradas.csv"
    csv_.write_text(para_csv(eventos), encoding="utf-8", newline="")
    return TestClient(criar_app(tmp_path / "paradas.sqlite", csv_, ENV))


def _local(iso_utc):
    t = dt.datetime.strptime(iso_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.UTC)
    return t.astimezone(FUSO)


def test_gerador_deterministico_e_csv_versionado_reprodutivel(eventos):
    assert sha256_csv(gerar(CFG["data_referencia"], seed=CFG["seed"])) == sha256_csv(eventos)
    versionado = (RAIZ / CFG["api_paradas"]["arquivo_csv"]).read_bytes()
    assert hashlib.sha256(versionado).hexdigest() == sha256_csv(eventos)
    assert sha256_csv(gerar(CFG["data_referencia"], seed=7)) != sha256_csv(eventos)


def test_ancoras_sozinhas_no_dia_e_ausencias(eventos):
    def no_dia(bairro, data):
        return [
            e["id"]
            for e in eventos
            if e["bairro"] == bairro
            and dt.date.fromisoformat(data)
            in dias_locais(_local(e["inicio_utc"]), _local(e["fim_utc"]))
        ]

    for a in ANCORAS:
        assert no_dia(a["bairro"], a["data"]) == [a["id"]]
    for bairro, data in AUSENCIAS:
        assert no_dia(bairro, data) == []


def test_api_responde_o_gabarito_das_dinamicas(cliente):
    for c in carregar_congelado():
        if c.tipo != "dinamica":
            continue
        esperado = c.api_esperada
        if esperado.situacao == "bairro_ambiguo":
            assert len(cliente.get("/bairros", params={"q": "Jardim"}).json()["bairros"]) >= 3
            continue
        r = cliente.get("/paradas", params={"bairro": esperado.bairro, "data": esperado.data})
        ids = [p["id"] for p in r.json()["paradas"] if p["status"] != "cancelada"]
        assert ids == esperado.registros_esperados, c.id


def test_bairro_sem_acento_inexistente_e_horario_local(cliente):
    r = cliente.get("/paradas", params={"bairro": "MOOCA", "data": "2026-11-10"}).json()
    assert r["bairro"] == "Mooca" and r["paradas"][0]["inicio_local"] == "2026-11-10T13:00:00-03:00"
    assert cliente.get("/paradas", params={"bairro": "butanta"}).json()["bairro"] == "Butantã"
    r = cliente.get("/paradas", params={"bairro": "Atlântida", "data": "2026-11-10"}).json()
    assert r["bairro_encontrado"] is False and r["paradas"] == []
    assert cliente.get("/paradas/PAR-ANC-03").json()["tipo"] == "poda"
    assert cliente.get("/paradas/NAO-EXISTE").status_code == 404


def test_parada_que_atravessa_a_meia_noite_aparece_nos_dois_dias(cliente, eventos):
    noite = next(
        e for e in eventos if _local(e["inicio_utc"]).date() != _local(e["fim_utc"]).date()
    )
    ini = _local(noite["inicio_utc"]).date()
    for d in (ini, ini + dt.timedelta(days=1)):
        r = cliente.get("/paradas", params={"bairro": noite["bairro"], "data": d.isoformat()})
        assert noite["id"] in [p["id"] for p in r.json()["paradas"]]


def test_escrita_exige_chave(cliente, monkeypatch):
    nova = {
        "bairro": "lapa",
        "inicio": "2026-11-20T09:00:00-03:00",
        "fim": "2026-11-20T12:00:00-03:00",
        "tipo": "obra",
        "motivo": "Obra de teste",
    }
    monkeypatch.delenv(ENV, raising=False)
    assert cliente.post("/paradas", json=nova).status_code == 503
    monkeypatch.setenv(ENV, "troque-esta-chave")
    assert (
        cliente.post("/paradas", json=nova, headers={"X-API-Key": "troque-esta-chave"}).status_code
        == 503
    )
    monkeypatch.setenv(ENV, "segredo-de-teste")
    assert cliente.post("/paradas", json=nova).status_code == 401
    assert cliente.post("/paradas", json=nova, headers={"X-API-Key": "errada"}).status_code == 401
    chave = {"X-API-Key": "segredo-de-teste"}
    r = cliente.post("/paradas", json=nova, headers=chave)
    assert r.status_code == 201 and r.json()["bairro"] == "Lapa"
    id_ = r.json()["id"]
    assert (
        cliente.get("/paradas", params={"bairro": "Lapa", "data": "2026-11-20"}).json()["paradas"][
            -1
        ]["id"]
        == id_
    )
    r = cliente.patch(f"/paradas/{id_}", json={"status": "cancelada"}, headers=chave)
    assert r.json()["status"] == "cancelada"
    ruim = {"fim": "2026-11-20T08:00:00-03:00"}
    assert cliente.patch(f"/paradas/{id_}", json=ruim, headers=chave).status_code == 422
    assert cliente.patch(f"/paradas/{id_}", json={"status": "x"}, headers=chave).status_code == 422


def test_cliente_fonte_paradas(cliente):
    fonte = ClienteParadasHTTP("http://testserver", cliente=cliente)
    r = fonte.buscar("vila mariana", dt.date(2026, 11, 11))
    assert r.bairro_encontrado and r.bairro == "Vila Mariana"
    assert [p["id"] for p in r.paradas] == ["PAR-ANC-01"]
    assert set(fonte.bairros("jardim")) == {
        "Jardim Helena",
        "Jardim Paulista",
        "Jardim São Luís",
        "Jardim Ângela",
    }
    assert cliente.get("/health").json()["registros"] == 793
