"""Testes da Fase 5 sem LLM: schema, validador, portão, reparo, métricas e mascaramento."""

import json
from types import SimpleNamespace

from src.avaliacao.casos import Caso
from src.avaliacao.geracao import avaliar_linha, canon, contem_fato, mascarar_govbr, nega_regra
from src.rag.pipeline import C1, RECUSA_CONTINGENCIA, RECUSA_PORTAO
from src.rag.schema import schema_para_llm
from src.rag.validador import casar_citacao, numeros, parece_ingles, validar

TEXTO = (
    "REN 1.000/2021 > Art. 362\nArt. 362. A distribuidora deve restabelecer o fornecimento "
    "nos seguintes prazos: I - 24 (vinte e quatro) horas, para religação normal de unidade "
    "consumidora localizada em área urbana;"
)
CHUNK = {"chunk_id": "D01-art362", "fonte": "REN 1.000/2021", "texto": TEXTO}
CHUNKS = {"D01-art362": CHUNK}
CFG = {
    "data_referencia": "2026-11-10",
    "retrieval": {"limiar_recusa": 0.6, "hibrido": False},
    "llm": {},
}


def _resposta(**kw):
    base = {
        "resposta": "A luz deve voltar em até 24 horas na cidade.",
        "recusa": False,
        "motivo_recusa": None,
        "fontes": [
            {
                "tipo": "norma",
                "id": "D01-art362",
                "trecho_citado": "24 (vinte e quatro) horas, para religação normal",
            }
        ],
        "confianca": "alta",
    }
    return json.dumps({**base, **kw}, ensure_ascii=False)


def test_schema_campos_obrigatorios_e_limite_de_fontes():
    s = schema_para_llm()
    assert set(s["required"]) == {"resposta", "recusa", "motivo_recusa", "fontes", "confianca"}
    assert set(s["$defs"]["Fonte"]["required"]) == {"tipo", "id", "trecho_citado"}
    assert s["properties"]["fontes"]["maxItems"] == 3


def test_casar_citacao():
    assert casar_citacao("“24 (vinte e quatro) horas”", TEXTO)[0] == "exato"
    assert casar_citacao("...restabelecer  o fornecimento nos seguintes prazos", TEXTO)[0] == (
        "exato"
    )
    assert casar_citacao("24 (vinte e quatro) horas para religacao normal", TEXTO)[0] == (
        "aproximado"
    )
    assert casar_citacao("prazo de 48 horas em área rural", TEXTO)[0] == "nenhum"


def test_numeros_ignoram_marcador_de_lista_e_milhar():
    assert numeros("1. Peça a religação.\n2) Espere 24 horas. REN 1.000") == {"24", "1000"}


def test_validar_ok_e_regras_b_c_f():
    assert validar(_resposta(), CHUNKS, "quando volta a luz?").ok
    v = validar(_resposta(fontes=[{"tipo": "norma", "id": "D99-x", "trecho_citado": "x"}]), CHUNKS)
    assert not v.ok and "não é um dos trechos" in v.erros[0]
    fonte_errada = [{"tipo": "norma", "id": "D01-art362", "trecho_citado": "em 48 horas"}]
    assert not validar(_resposta(fontes=fonte_errada), CHUNKS).ok
    v = validar(_resposta(resposta="A luz volta em 12 horas."), CHUNKS)
    assert v.numeros_sem_base == ["12"]
    assert validar(
        _resposta(resposta="Hoje, 10/11/2026, o prazo é 24 horas."), CHUNKS, "", "2026-11-10"
    ).ok


def test_validar_corrige_id_trocado_e_recusa_citacao_curta():
    outro = {"chunk_id": "D01-art31", "fonte": "REN", "texto": "Art. 31. Outro assunto qualquer."}
    trocada = [
        {"tipo": "norma", "id": "D01-art31", "trecho_citado": "24 (vinte e quatro) horas, para"}
    ]
    v = validar(_resposta(fontes=trocada), {**CHUNKS, "D01-art31": outro})
    assert v.ok and v.resposta.fontes[0].id == "D01-art362"
    assert v.citacoes[0]["id_original"] == "D01-art31"
    curta = [{"tipo": "norma", "id": "D01-art362", "trecho_citado": "24 horas"}]
    assert not validar(_resposta(fontes=curta), CHUNKS).ok


def test_validar_json_schema_e_recusa():
    assert validar("isso não é json", CHUNKS).categoria == "json"
    assert validar(_resposta(fontes=[]), CHUNKS).categoria == "regras"
    recusa = {"recusa": True, "fontes": [], "motivo_recusa": "não consta"}
    assert validar(_resposta(resposta="Procure a ANEEL.", **recusa), CHUNKS).ok
    v = validar(_resposta(resposta="Não sei, mas deve ser 48 horas.", **recusa), CHUNKS)
    assert not v.ok and "não pode trazer números" in v.erros[0]
    assert not validar(_resposta(resposta="Procure a ANEEL.", recusa=True, fontes=[]), CHUNKS).ok


class _Retriever:
    def __init__(self, nota):
        self.nota = nota

    def buscar(self, pergunta, modo="denso"):
        return [
            SimpleNamespace(
                chunk=CHUNK, chunk_id="D01-art362", score=self.nota, score_denso=self.nota
            )
        ]


class _LLM:
    def __init__(self, saidas):
        self.saidas, self.chamadas = list(saidas), []

    def __call__(self, mensagens, schema):
        self.chamadas.append(mensagens)
        return {"message": {"content": self.saidas.pop(0)}, "eval_count": 1}


def test_portao_recusa_sem_chamar_llm():
    llm = _LLM([])
    s = C1(CFG, retriever=_Retriever(0.5), llm=llm).responder("qual a capital da França?")
    assert s.origem == "portao" and s.resposta == RECUSA_PORTAO and not llm.chamadas


def test_reparo_e_contingencia():
    llm = _LLM([_resposta(resposta="Volta em 12 horas."), _resposta()])
    s = C1(CFG, retriever=_Retriever(0.8), llm=llm).responder("quando volta a luz?")
    assert s.origem == "reparo" and len(s.tentativas) == 2
    assert "12" in llm.chamadas[1][-1]["content"]
    llm = _LLM(["{}", "não é json"])
    s = C1(CFG, retriever=_Retriever(0.8), llm=llm).responder("quando volta a luz?")
    assert s.origem == "contingencia" and s.resposta == RECUSA_CONTINGENCIA


def test_canon_e_fatos():
    assert canon("15 (quinze) minutos") == canon("quinze minutos") == "15 minutos"
    assert contem_fato("O limite é de 80 kWh por mês.", "80 kWh/mês")
    assert contem_fato("Vale desde o primeiro... 1º de janeiro de 2026", "1º de janeiro de 2026")
    assert contem_fato("em até vinte e quatro horas", "24 horas")
    assert contem_fato("em 24h", "24 horas")
    assert contem_fato("potência até 75 quilowatts (KW)", "75 kW")
    assert contem_fato("até 80 quilowatts-hora por mês", "80 kWh/mês")
    assert not contem_fato("desconto de 165%", "65%")
    assert not contem_fato("de 1 a 5 dias úteis", "15 dias úteis")


def test_avaliar_linha_acuracia_citacao_e_alucinacao():
    caso = Caso(
        id="T-X",
        tipo="direta",
        grupo="g",
        tema="t",
        pergunta="Em quanto tempo religam?",
        deve_recusar=False,
        chunk_ids_gold=["D01-art362"],
        resposta_gabarito="Em 24 horas.",
        fatos_chave=["24 horas"],
        fatos_proibidos=["48 horas"],
    )
    saida = {
        "resposta": json.loads(_resposta()),
        "origem": "llm",
        "tentativas": [
            {
                "categoria": "ok",
                "citacoes": [
                    {"id": "D01-art362", "fornecido": True, "casamento": "exato", "nota": 100}
                ],
            }
        ],
    }
    m = avaliar_linha(caso, saida, [TEXTO])
    assert m["acuracia"] and m["citacao_correta"] and not m["alucinacao"]
    saida["resposta"]["resposta"] = "Em 48 horas."
    m = avaliar_linha(caso, saida, [TEXTO])
    assert not m["acuracia"] and m["alucinacao"]


def test_regra_g_idioma():
    assert parece_ingles("People have the right to the social tariff if they are registered.")
    assert not parece_ingles("A distribuidora deve religar a luz em até 24 horas.")
    v = validar(_resposta(resposta="The power must be back within 24 hours in the city."), CHUNKS)
    assert not v.ok and "português" in v.erros[0]


def test_nega_regra():
    assert nega_regra("Não há informação oficial sobre o prazo de religação.")
    assert nega_regra("A distribuidora não tem obrigação legal de avisar.")
    assert not nega_regra("Não encontrei esse assunto nas normas que eu consulto.")


def test_numero_do_trecho_fornecido_nao_e_alucinacao():
    caso = Caso(
        id="T-Y",
        tipo="direta",
        grupo="g",
        tema="t",
        pergunta="Quando avisam?",
        deve_recusar=False,
        chunk_ids_gold=["D01-art362"],
        resposta_gabarito="Em 24 horas.",
        fatos_chave=["24 horas"],
    )
    saida = {
        "resposta": json.loads(_resposta(resposta="Em 24 horas; aviso com 72 horas.")),
        "origem": "llm",
        "tentativas": [{"categoria": "ok", "citacoes": []}],
    }
    assert avaliar_linha(caso, saida, [TEXTO])["alucinacao"]
    assert not avaliar_linha(caso, saida, [TEXTO], ["prazo de 72 horas"])["alucinacao"]


def test_mascarar_govbr():
    linha = {
        "saida": {
            "trechos": [{"chunk_id": "D14-q1"}],
            "resposta": {"fontes": [{"id": "D14-q1", "trecho_citado": "texto da página"}]},
            "tentativas": [
                {
                    "conteudo": json.dumps(
                        {"fontes": [{"id": "D14-q1", "trecho_citado": "texto da página"}]}
                    )
                }
            ],
        }
    }
    pagina = "Página explicativa com um texto longo o bastante para passar da janela literal. " * 2
    m = mascarar_govbr(linha, {"D14-q1": pagina})
    assert "texto da página" not in json.dumps(m, ensure_ascii=False)
    assert linha["saida"]["resposta"]["fontes"][0]["trecho_citado"] == "texto da página"
    assert mascarar_govbr(linha, {"D15-q2": pagina}) == linha
    linha["saida"]["resposta"]["resposta"] = "Veja: " + pagina
    assert "[omitido" in mascarar_govbr(linha, {"D14-q1": pagina})["saida"]["resposta"]["resposta"]
