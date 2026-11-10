"""Testes da Fase 7 sem LLM: datas, bairros, roteador, fluxo do C2 e métrica das dinâmicas."""

import datetime as dt
import json
from types import SimpleNamespace

import pytest

from src.agente import prompts
from src.agente.agente import AVISO_AGENDA, C2, RECUSA_ERRO_AGENDA, RECUSA_SEM_BAIRRO
from src.agente.normalizacao import bairro_no_texto, resolver_bairro, resolver_data
from src.agente.roteador import por_regras, rotear
from src.avaliacao.geracao import avaliar_dinamica
from src.paradas_api.fonte import ResultadoParadas
from src.paradas_api.gerador import carregar_distritos

REF = dt.date(2026, 11, 10)  # terça-feira
BAIRROS = carregar_distritos()
CFG = {
    "data_referencia": "2026-11-10",
    "retrieval": {"limiar_recusa": 0.6, "hibrido": False},
    "llm": {},
    "api_paradas": {"base_url": "http://x"},
    "agente": {"timeout_ferramenta_s": 5},
}
PARADA = {
    "id": "PAR-00436",
    "bairro": "Tatuapé",
    "inicio_local": "2026-11-12T09:00:00-03:00",
    "fim_local": "2026-11-12T15:00:00-03:00",
    "tipo": "obra",
    "status": "agendada",
    "motivo": "Instalação de novos postes",
}


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("hoje", REF),
        ("amanhã", dt.date(2026, 11, 11)),
        ("depois de amanhã", dt.date(2026, 11, 12)),
        ("nesta sexta-feira", dt.date(2026, 11, 13)),
        ("sábado que vem", dt.date(2026, 11, 14)),
        ("próxima segunda-feira", dt.date(2026, 11, 16)),
        ("terça", REF),
        ("próxima terça", dt.date(2026, 11, 17)),
        ("no dia 13 de novembro", dt.date(2026, 11, 13)),
        ("dia 5", dt.date(2026, 12, 5)),
        ("14/11", dt.date(2026, 11, 14)),
        ("Fiquei 30 horas sem luz na minha casa e quero saber", None),
    ],
)
def test_resolver_data(texto, esperado):
    assert resolver_data(texto, REF) == esperado


def test_resolver_bairro():
    assert resolver_bairro("butanta", BAIRROS).nome == "Butantã"
    assert resolver_bairro("vila prudenti", BAIRROS).nome == "Vila Prudente"
    assert resolver_bairro("no Mooca", BAIRROS).nome == "Mooca"
    jardim = resolver_bairro("Jardim", BAIRROS)
    assert jardim.situacao == "ambiguo" and len(jardim.candidatos) == 4
    assert resolver_bairro("Itaim", BAIRROS).candidatos == ["Itaim Bibi", "Itaim Paulista"]
    assert resolver_bairro("Osasco", BAIRROS).situacao == "desconhecido"
    assert resolver_bairro(None, BAIRROS).situacao == "ausente"


def test_bairro_no_texto_evita_falsos_positivos():
    assert bairro_no_texto("Vai ter manutenção amanhã na Vila Mariana?", BAIRROS) == "vila mariana"
    assert bairro_no_texto("Tem manutenção programada no Jardim amanhã?", BAIRROS) == "jardim"
    assert bairro_no_texto("se eu pagar a conta, quando religam?", BAIRROS) is None
    assert bairro_no_texto("meu pai usa equipamento de saúde, tem manutenção?", BAIRROS) is None


class _LLM:
    def __init__(self, saidas):
        self.saidas, self.chamadas = list(saidas), []

    def __call__(self, mensagens, schema):
        self.chamadas.append(mensagens)
        saida = self.saidas.pop(0)
        if isinstance(saida, Exception):
            raise saida
        return {"message": {"content": saida}, "eval_count": 1}


def _rot(agenda=True, normas=False, bairro=None, data=None):
    return json.dumps(
        {"precisa_agenda": agenda, "precisa_normas": normas, "bairro": bairro, "data": data}
    )


def test_roteador_contingencia_e_complemento():
    r = rotear("Vai ter manutenção amanhã no Tatuapé?", _LLM(["não é json"]), BAIRROS, REF)
    assert r.origem == "regras" and r.roteamento.precisa_agenda
    assert r.roteamento.bairro == "tatuape"
    r = rotear("Vai ter manutenção amanhã no Tatuapé?", _LLM([OSError("rede")]), BAIRROS, REF)
    assert r.origem == "regras"
    r = rotear("Vai ter manutenção amanhã no Tatuapé?", _LLM([_rot(data="amanhã")]), BAIRROS, REF)
    assert r.origem == "llm+regras" and r.roteamento.bairro == "tatuape"
    assert not por_regras("Minha luz caiu ontem. Tenho direito a desconto?", BAIRROS).precisa_agenda
    p = "Como faço pra empresa me avisar antes de desligar a energia pra manutenção?"
    r = rotear(p, _LLM([_rot(normas=True)]), BAIRROS, REF)
    assert not r.roteamento.precisa_agenda and r.origem == "llm+regras"
    r = rotear("Vai ter manutenção programada amanhã?", _LLM([_rot(data="amanhã")]), BAIRROS, REF)
    assert r.roteamento.precisa_agenda


class _Fonte:
    def __init__(self, paradas=None, erro=None):
        self.paradas, self.erro, self.consultas = paradas or {}, erro, []

    def bairros(self, q=""):
        return BAIRROS

    def buscar(self, bairro, data):
        if self.erro:
            raise self.erro
        self.consultas.append((bairro, data))
        return ResultadoParadas(True, bairro, data, self.paradas.get((bairro, data), []))


class _Retriever:
    def __init__(self, nota=0.4):
        self.nota, self.consultas = nota, []

    def melhor_cosseno(self, pergunta):
        return self.nota

    def buscar(self, pergunta, modo="denso", reranker=None):
        self.consultas.append(pergunta)
        chunk = {"chunk_id": "D01-x", "fonte": "REN", "texto": "Texto qualquer da norma."}
        return [
            SimpleNamespace(chunk=chunk, chunk_id="D01-x", score=self.nota, score_denso=self.nota)
        ]


def _c2(llm, fonte):
    return C2(CFG, fonte=fonte, retriever=_Retriever(), llm=llm)


def _resposta_api(id_, citado, texto="Sim, das 9h às 15h no dia 12/11/2026."):
    return json.dumps(
        {
            "resposta": texto,
            "recusa": False,
            "motivo_recusa": None,
            "fontes": [{"tipo": "api", "id": id_, "trecho_citado": citado}],
            "confianca": "alta",
        },
        ensure_ascii=False,
    )


def test_c2_com_parada_cita_registro_e_acrescenta_aviso():
    fonte = _Fonte({("Tatuapé", dt.date(2026, 11, 12)): [PARADA]})
    citado = prompts.registro_como_trecho(PARADA)["texto"].split("\n")[1][:120]
    llm = _LLM(
        [_rot(bairro="Tatuapé", data="depois de amanhã"), _resposta_api("PAR-00436", citado)]
    )
    s = _c2(llm, fonte).responder("Vai ter desligamento no Tatuapé depois de amanhã?")
    assert s.origem == "llm" and not s.resposta.recusa
    assert s.resposta.resposta.endswith(AVISO_AGENDA)
    assert fonte.consultas == [("Tatuapé", dt.date(2026, 11, 12))]
    esperado = {"situacao": "com_parada", "registros_esperados": ["PAR-00436"]}
    saida = {"resposta": s.resposta.model_dump()}
    assert avaliar_dinamica(esperado, saida, {"PAR-00436": (9, 15)}, BAIRROS)


def test_c2_sem_parada_cita_consulta_e_sem_data_consulta_7_dias():
    fonte = _Fonte()
    vazia = prompts.consulta_vazia_como_trecho("Lapa", REF, REF + dt.timedelta(days=6))
    citado = vazia["texto"].split("\n")[1]
    llm = _LLM(
        [
            _rot(bairro="Lapa"),
            _resposta_api(vazia["chunk_id"], citado, "Não há parada programada na Lapa."),
        ]
    )
    s = _c2(llm, fonte).responder("Vai ter manutenção na Lapa?")
    assert len(fonte.consultas) == 7 and not s.resposta.recusa
    esperado = {"situacao": "sem_parada", "registros_esperados": []}
    assert avaliar_dinamica(esperado, {"resposta": s.resposta.model_dump()}, {}, BAIRROS)


def test_c2_esclarecimentos_sem_chamar_o_llm_de_novo():
    llm = _LLM([_rot(bairro="Jardim", data="amanhã")])
    s = _c2(llm, _Fonte()).responder("Tem manutenção programada no Jardim amanhã?")
    assert s.origem == "esclarecimento" and s.resposta.recusa and len(llm.chamadas) == 1
    assert avaliar_dinamica(
        {"situacao": "bairro_ambiguo"}, {"resposta": s.resposta.model_dump()}, {}, BAIRROS
    )
    s = _c2(_LLM([_rot(data="amanhã")]), _Fonte()).responder("Vai ter manutenção amanhã?")
    assert s.resposta == RECUSA_SEM_BAIRRO
    s = _c2(_LLM([_rot(bairro="Osasco")]), _Fonte()).responder("Manutenção em Osasco amanhã?")
    assert "Não encontrei o bairro" in s.resposta.resposta


def test_c2_erro_da_agenda_e_limite_de_chamadas():
    s = _c2(_LLM([_rot(bairro="Lapa", data="hoje")]), _Fonte(erro=TimeoutError())).responder("x")
    assert s.resposta == RECUSA_ERRO_AGENDA and s.origem == "erro_agenda"
    llm = _LLM([_rot(bairro="Lapa", data="hoje"), "{}", "{}"])
    s = _c2(llm, _Fonte()).responder("Tem manutenção na Lapa hoje?")
    assert s.origem == "contingencia" and len(llm.chamadas) == 3


def test_c2_pergunta_mista_busca_normas_pela_parte_reescrita():
    rot = json.loads(_rot(normas=True, bairro="Lapa", data="hoje"))
    rot["pergunta_normas"] = "A distribuidora tem que avisar antes?"
    ret = _Retriever(nota=0.9)
    llm = _LLM([json.dumps(rot), "{}", "{}"])
    s = C2(CFG, fonte=_Fonte(), retriever=ret, llm=llm).responder(
        "Manutenção na Lapa hoje? E o aviso?"
    )
    assert ret.consultas == ["A distribuidora tem que avisar antes?"]
    assert [t["chunk_id"] for t in s.trechos] == ["consulta-lapa-20261110", "D01-x"]


def test_correcoes_a_e_c():
    rot = json.loads(_rot(agenda=False, normas=True))
    rot["pergunta_normas"] = "Quanto tempo a distribuidora tem para religar a luz?"
    ret = _Retriever(nota=0.4)
    c2 = C2(CFG, fonte=_Fonte(), retriever=ret, llm=_LLM([json.dumps(rot)]), correcoes={"A"})
    c2.responder("quantu tempo eles tem pra voutar com a lus")
    assert ret.consultas == ["Quanto tempo a distribuidora tem para religar a luz?"]
    sem_a = _Retriever(nota=0.4)
    C2(CFG, fonte=_Fonte(), retriever=sem_a, llm=_LLM([json.dumps(rot)])).responder("x?")
    assert sem_a.consultas == ["x?"]
    c = C2(CFG, fonte=_Fonte(), retriever=ret, llm=_LLM([]), correcoes={"C"})
    assert (c.modo, c.reranker) == ("hibrido", True)
    with pytest.raises(ValueError):
        C2(CFG, fonte=_Fonte(), retriever=ret, llm=_LLM([]), correcoes={"Z"})


def test_correcao_d_marca_incisos_revogados_e_padrao_nao_muda():
    from src.rag.prompt import formatar_trecho, marcar_revogados, ordenar_por_confiabilidade

    texto = "Art. 9. Pode:\nVII - um;\nIX - dois;\nXII - tres."
    assert marcar_revogados(texto).split("\n")[2:4] == ["VIII - (revogado)", "IX - dois;"]
    assert "XI - (revogado)" in marcar_revogados(texto)
    chunk = {
        "chunk_id": "x",
        "fonte": "REN",
        "texto": texto,
        "notas_redacao": ["(Revogado pela REN ANEEL 1.137, DE 21.10.2025)"],
    }
    assert "VIII - (revogado)" not in formatar_trecho(chunk)
    assert "VIII - (revogado)" in formatar_trecho(chunk, notas=True)
    sem_nota = {**chunk, "notas_redacao": []}
    assert "(revogado)" not in formatar_trecho(sem_nota, notas=True)
    com_alerta = {**chunk, "chunk_id": "y", "alerta": "página antiga"}
    assert [c["chunk_id"] for c in ordenar_por_confiabilidade([com_alerta, chunk])] == ["x", "y"]


def _rnorma(texto="A luz volta em 24 horas."):
    return json.dumps(
        {
            "resposta": texto,
            "recusa": False,
            "motivo_recusa": None,
            "fontes": [
                {"tipo": "norma", "id": "D01-x", "trecho_citado": "Texto qualquer da norma."}
            ],
            "confianca": "alta",
        }
    )


def test_correcao_f_autoverificacao():
    ret = _Retriever(nota=0.9)
    ret_chunk = "Texto qualquer da norma. Prazo de 24 horas."
    ret.buscar = lambda p, modo="denso", reranker=None: [
        SimpleNamespace(
            chunk={"chunk_id": "D01-x", "fonte": "REN", "texto": ret_chunk},
            chunk_id="D01-x",
            score=0.9,
            score_denso=0.9,
        )
    ]
    rot = _rot(agenda=False, normas=True)
    ruim = json.dumps({"ok": False, "problemas": ["o prazo vale para outra situação"]})
    bom = json.dumps({"ok": True, "problemas": []})
    llm = _LLM([rot, _rnorma(), ruim, _rnorma()])
    s = C2(CFG, fonte=_Fonte(), retriever=ret, llm=llm, correcoes={"F"}).responder("prazo?")
    assert s.origem == "reparo" and len(llm.chamadas) == 4
    assert "outra situação" in llm.chamadas[3][-1]["content"]
    llm = _LLM([rot, _rnorma(), bom])
    s = C2(CFG, fonte=_Fonte(), retriever=ret, llm=llm, correcoes={"F"}).responder("prazo?")
    assert s.origem == "llm" and s.verificacoes[0]["ok"]
    llm = _LLM([rot, "{}", _rnorma(), ruim])
    s = C2(CFG, fonte=_Fonte(), retriever=ret, llm=llm, correcoes={"F"}).responder("prazo?")
    assert s.origem == "contingencia" and len(llm.chamadas) == 4
    llm = _LLM([rot, _rnorma(), "não é json"])
    s = C2(CFG, fonte=_Fonte(), retriever=ret, llm=llm, correcoes={"F"}).responder("prazo?")
    assert s.origem == "llm" and s.verificacoes[0]["erro"]


def test_correcao_v_reescreve_so_voz():
    rot = json.loads(_rot(agenda=False, normas=True))
    rot["pergunta_normas"] = "Pergunta reescrita?"
    for origem, esperado in (("voz", "Pergunta reescrita?"), ("texto", "orig")):
        ret = _Retriever(nota=0.4)
        c2 = C2(CFG, fonte=_Fonte(), retriever=ret, llm=_LLM([json.dumps(rot)]), correcoes={"V"})
        c2.responder("orig", origem=origem)
        assert ret.consultas == [esperado]


def test_c2_pergunta_de_normas_segue_o_caminho_do_c1():
    llm = _LLM([_rot(agenda=False, normas=True)])
    s = _c2(llm, _Fonte()).responder("Qual o prazo para religar a luz?")
    assert s.origem == "portao" and s.config == "C2" and len(llm.chamadas) == 1
    assert s.roteamento["precisa_agenda"] is False
