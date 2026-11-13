import re

import httpx
import pytest
from pydantic import ValidationError

from src.config import RAIZ, carregar_config, url_ollama
from src.rag import llm_ollama
from src.rag.schema import Resposta, classificar_saida, schema_para_llm

FONTE_OK = '[{"tipo": "norma", "id": "c1", "trecho_citado": "texto"}]'


def test_config_tem_chaves_essenciais():
    cfg = carregar_config()
    assert cfg["seed"] == 42
    assert cfg["data_referencia"] == "2026-11-10"
    assert cfg["llm"]["temperature"] == 0.0
    assert cfg["llm"]["think"] is False
    assert cfg["llm"]["modelo"] in cfg["llm"]["candidatos"]


def test_config_trava_versoes_dos_modelos():
    cfg = carregar_config()
    for tag, digest in cfg["llm"]["candidatos"].items():
        assert re.fullmatch(r"[0-9a-f]{64}", str(digest)), tag
    assert re.fullmatch(r"[0-9a-f]{40}", cfg["embeddings"]["revisao"])


def test_lock_aponta_indice_do_torch_cuda():
    linhas = (RAIZ / "requirements-lock.txt").read_text(encoding="utf-8").splitlines()
    torch = next(linha for linha in linhas if linha.startswith("torch=="))
    if "+cu" in torch:
        assert any(
            linha.startswith("--extra-index-url https://download.pytorch.org/whl/cu")
            for linha in linhas
        )


def test_ollama_host_sobrescrito_por_env(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "127.0.0.1:9999")
    assert carregar_config()["llm"]["host"] == "http://127.0.0.1:9999"


@pytest.mark.parametrize(
    ("valor", "url"),
    [
        ("0.0.0.0", "http://127.0.0.1:11434"),
        ("0.0.0.0:11434", "http://127.0.0.1:11434"),
        (":11434", "http://127.0.0.1:11434"),
        ("localhost", "http://localhost:11434"),
        ("http://host.docker.internal:11434", "http://host.docker.internal:11434"),
        ("https://ollama.exemplo:8443/", "https://ollama.exemplo:8443"),
        ("[::]:11434", "http://127.0.0.1:11434"),
    ],
)
def test_url_ollama_normaliza_valores_do_servidor(valor, url):
    assert url_ollama(valor) == url


def test_schema_aceita_resposta_valida():
    r = Resposta.model_validate_json(
        '{"resposta": "Sim.", "recusa": false, "confianca": "alta", "fontes": ' + FONTE_OK + "}"
    )
    assert r.fontes[0].id == "c1"
    assert r.motivo_recusa is None


@pytest.mark.parametrize(
    "json_invalido",
    [
        '{"resposta": "x", "recusa": false, "confianca": "altíssima"}',
        '{"resposta": "x", "confianca": "alta"}',
        '{"resposta": "x", "recusa": false, "confianca": "alta",'
        ' "fontes": [{"tipo": "site", "id": "c1", "trecho_citado": "t"}]}',
        '{"resposta": "x", "recusa": false, "confianca": "alta",'
        ' "fontes": [{"tipo": "norma", "id": "c1", "trecho_citado": "' + "a" * 401 + '"}]}',
    ],
)
def test_schema_rejeita_resposta_invalida(json_invalido):
    with pytest.raises(ValidationError):
        Resposta.model_validate_json(json_invalido)


def test_regra_b1_resposta_sem_recusa_exige_fonte():
    with pytest.raises(ValidationError, match="pelo menos uma fonte"):
        Resposta.model_validate_json('{"resposta": "nao", "recusa": false, "confianca": "alta"}')
    recusa = Resposta.model_validate_json(
        '{"resposta": "Não consta.", "recusa": true, "motivo_recusa": "fora da base",'
        ' "confianca": "baixa"}'
    )
    assert recusa.fontes == []


def test_schema_para_llm_exige_todos_os_campos():
    schema = schema_para_llm()
    assert set(schema["required"]) == set(schema["properties"])
    fonte = schema["$defs"]["Fonte"]
    assert set(fonte["required"]) == set(fonte["properties"])
    assert "fontes" not in Resposta.model_json_schema()["required"]


@pytest.mark.parametrize(
    ("conteudo", "categoria"),
    [
        (
            '{"resposta": "Sim.", "recusa": false, "confianca": "alta", "fontes": '
            + FONTE_OK
            + "}",
            "ok",
        ),
        ('{"resposta": "Sim.", "recusa": false, "confianca": "alta", "fontes": []}', "regras"),
        ('{"resposta": "Sim.", "recusa": false, "confianca": "talvez", "fontes": []}', "schema"),
        ('{"resposta": "Sim.", "recusa": ', "json"),
    ],
)
def test_classificar_saida(conteudo, categoria):
    resposta, obtida = classificar_saida(conteudo)
    assert obtida == categoria
    assert (resposta is not None) == (categoria == "ok")


def test_chat_json_envia_schema_e_opcoes(monkeypatch):
    enviados = []

    def falso_post(url, json, timeout):
        enviados.append(json)
        return httpx.Response(
            200, json={"message": {"content": "{}"}}, request=httpx.Request("POST", url)
        )

    monkeypatch.setattr(httpx, "post", falso_post)
    cfg = carregar_config()
    opcoes = llm_ollama.opcoes_do_config(cfg["llm"])
    llm_ollama.chat_json("http://h", "m", [], Resposta.model_json_schema(), opcoes)
    payload = enviados[0]
    assert payload["format"]["title"] == "Resposta"
    assert payload["options"]["temperature"] == 0.0
    assert payload["options"]["seed"] == 42
    assert payload["think"] is False
    assert payload["stream"] is False


def test_chat_json_repete_sem_think_se_modelo_nao_suporta(monkeypatch):
    enviados = []

    def falso_post(url, json, timeout):
        enviados.append(dict(json))
        req = httpx.Request("POST", url)
        if "think" in json:
            return httpx.Response(
                400, text='{"error":"model does not support thinking"}', request=req
            )
        return httpx.Response(200, json={"message": {"content": "{}"}}, request=req)

    monkeypatch.setattr(httpx, "post", falso_post)
    llm_ollama.chat_json("http://h", "m", [], {}, {})
    assert len(enviados) == 2
    assert "think" not in enviados[1]
