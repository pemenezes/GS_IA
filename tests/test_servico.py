"""Testes do serviço (sem LLM): mascaramento de dados pessoais, rotas e log sem a pergunta."""

import json

from fastapi.testclient import TestClient

from src.rag.pipeline import Saida
from src.rag.schema import Resposta
from src.servico import app as servico
from src.servico.pii import mascarar


def test_mascarar_dados_pessoais_e_manter_numeros_da_pergunta():
    texto, tipos = mascarar(
        "Meu CPF é 123.456.789-09, telefone (11) 91234-5678, e-mail ana@x.com.br, "
        "instalação 1234567890, CEP 01234-567. Fiquei 30 horas sem luz e a conta veio com 40 dias."
    )
    assert "123.456" not in texto and "91234" not in texto and "ana@" not in texto
    assert "1234567890" not in texto and "01234-567" not in texto
    assert "30 horas" in texto and "40 dias" in texto
    assert {"cpf", "telefone", "email", "cep"} <= set(tipos)
    assert mascarar("protocolo 202611120001234")[0] == "protocolo [NUMERO]"


class _Pipeline:
    def __init__(self):
        self.recebido = None

    def responder(self, pergunta, origem="texto"):
        self.recebido = (pergunta, origem)
        r = Resposta(
            resposta="Em até 24 horas.",
            recusa=False,
            motivo_recusa=None,
            fontes=[{"tipo": "norma", "id": "D01-x", "trecho_citado": "24 horas"}],
            confianca="alta",
        )
        return Saida("C2", r, "llm", 1.2, 0.8, [{"chunk_id": "D01-x", "nota": 0.8}])


def test_rotas_e_log_sem_texto(tmp_path, monkeypatch):
    monkeypatch.setattr(servico, "LOGS", tmp_path)
    pipe = _Pipeline()
    chunks = {
        "D01-x": {
            "fonte": "REN 1.000",
            "rotulo_doc": "REN 1.000/2021",
            "artigo": "Art. 362",
            "url": "https://exemplo",
        }
    }
    c = TestClient(servico.criar_app({"C2M": pipe, "C0": pipe}, chunks))
    assert c.get("/health").json()["carregado"] is True
    assert "C2M" in c.get("/v1/configs").json()["configs"]
    assert "Luz Cidadã" in c.get("/").text
    r = c.post(
        "/v1/perguntar",
        json={"pergunta": "Meu CPF é 123.456.789-09. Quando religam?", "origem": "voz"},
    ).json()
    assert pipe.recebido == ("Meu CPF é [CPF]. Quando religam?", "voz")
    assert r["fontes"][0]["rotulo"] == "REN 1.000/2021" and r["dados_pessoais_mascarados"] == [
        "cpf"
    ]
    log = (tmp_path / "servico.jsonl").read_text(encoding="utf-8")
    assert "religam" not in log and "123.456" not in log
    assert json.loads(log)["fontes"] == ["D01-x"]
    assert c.post("/v1/perguntar", json={"pergunta": "oi", "config": "C2M"}).status_code == 422
