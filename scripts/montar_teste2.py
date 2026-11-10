"""Test novo, T2 (Fase 8B): 24 perguntas escritas antes das melhorias e medidas uma única vez.

  python scripts/montar_teste2.py              # candidatas e documento de revisão
  python scripts/montar_teste2.py --congelar   # depois da revisão: teste2.jsonl e teste2.lock

O gabarito de cada pergunta respondível vem do texto dos trechos indicados (lidos na base) e já
inclui os trechos equivalentes: os que trazem o mesmo fato-chave entre os 15 mais próximos do
gabarito e as páginas explicativas que o repetem. As versões de voz saem de ruido_de_voz, com
semente fixa, e a resposta das perguntas da agenda vem da API simulada.

Grava avaliacao/teste2_candidatas.jsonl, avaliacao/revisao/revisao_teste2.md (versionado;
trechos de páginas gov.br trocados por hash) e avaliacao/runs/local/revisao_teste2_completa.md.
"""

# ruff: noqa: E501 (tabela de perguntas e gabaritos)
from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from src.avaliacao.casos import (  # noqa: E402
    CANDIDATAS2,
    LOCK2,
    TESTE2,
    Caso,
    carregar,
    gravar,
)
from src.avaliacao.ruido import ruido_de_voz  # noqa: E402
from src.config import RAIZ, carregar_config  # noqa: E402
from src.paradas_api.app import criar_app  # noqa: E402
from src.rag import denso  # noqa: E402

REVISAO = RAIZ / "avaliacao" / "revisao" / "revisao_teste2.md"
REVISAO_LOCAL = RAIZ / "avaliacao" / "runs" / "local" / "revisao_teste2_completa.md"
SEMENTE_VOZ = 2026

NAO_CONSTA = "Não consta na base: o assistente deve recusar e indicar o canal oficial."
FORA = "Fora do domínio: o assistente trata só de energia elétrica."

# id, tipo, grupo, tema, pergunta, gold, equivalentes, gabarito, fatos-chave, observações
RESPONDIVEIS = [
    (
        "T2-01",
        "direta",
        "H01",
        "titularidade",
        "Em quanto tempo a distribuidora deve fazer a troca de titularidade da conta de luz de uma "
        "casa na área urbana?",
        ["D01-art138-p3"],
        ["D14-q04"],
        "Em até 3 dias úteis na área urbana (5 dias úteis na área rural).",
        ["3 dias úteis"],
        "",
    ),
    (
        "T2-02",
        "direta",
        "H02",
        "datas_vencimento",
        "Quantas opções de data de vencimento da fatura a distribuidora deve oferecer ao consumidor?",
        ["D01-art338"],
        ["D01-anexoi-clausulaquarta-p2", "D14-q03"],
        "Pelo menos seis datas de vencimento, distribuídas uniformemente ao longo do mês.",
        ["6 datas"],
        "",
    ),
    (
        "T2-03",
        "direta",
        "H03",
        "leitura",
        "De quanto em quanto tempo a distribuidora deve fazer a leitura do medidor de uma casa?",
        ["D01-art260"],
        [],
        "A cada aproximadamente 30 dias, com intervalo mínimo de 27 e máximo de 33 dias (há "
        "exceções, como o primeiro faturamento).",
        ["27", "33"],
        "",
    ),
    (
        "T2-04",
        "direta",
        "H04",
        "corte_90_dias",
        "Depois de quanto tempo do vencimento de uma conta não paga a distribuidora não pode mais "
        "cortar a luz por causa dela?",
        ["D01-art357"],
        ["D01-anexoi-clausulasexta-p2"],
        "Depois de 90 dias da data da fatura vencida e não paga, o corte é vedado, salvo se a "
        "distribuidora comprovar que não cortou antes por determinação judicial ou outro motivo "
        "justificável.",
        ["90 dias"],
        "",
    ),
    (
        "T2-05",
        "direta",
        "H05",
        "entrega_fatura",
        "Com quantos dias de antecedência a conta de luz de uma casa deve ser entregue antes do "
        "vencimento?",
        ["D01-art337"],
        ["D01-anexoi-clausulaquarta-p3", "D14-q03"],
        "Pelo menos 5 dias úteis antes do vencimento (10 dias úteis para poder público, iluminação "
        "pública e serviço público).",
        ["5 dias úteis"],
        "",
    ),
    (
        "T2-06",
        "direta",
        "H06",
        "vistoria",
        "Se a vistoria da entrada de energia de uma ligação nova for reprovada, em quanto tempo a "
        "distribuidora deve entregar o relatório com os motivos?",
        ["D01-art94"],
        [],
        "Em até 3 dias úteis após a conclusão da vistoria, com os motivos e as providências "
        "corretivas necessárias.",
        ["3 dias úteis"],
        "",
    ),
    (
        "T2-07",
        "direta",
        "H07",
        "cdc_cobranca",
        "Na hora de cobrar uma conta de luz atrasada, a empresa pode me humilhar ou me ameaçar?",
        ["D10-art42"],
        [],
        "Não. Pelo art. 42 do CDC, na cobrança de débitos o consumidor inadimplente não pode ser "
        "exposto a ridículo nem submetido a constrangimento ou ameaça.",
        ["ridicul"],
        "Fato-chave do Pedro: 'o cliente não é ridicularizado'. A raiz 'ridicul' reconhece "
        "'ridículo' e 'ridicularizado'; a negação é conferida na revisão manual.",
    ),
    (
        "T2-08",
        "coloquial",
        "H08",
        "debito_terceiros",
        "Aluguei uma casa e o morador antigo deixou conta de luz atrasada. A empresa pode me obrigar "
        "a pagar essa dívida pra passar a conta pro meu nome?",
        ["D01-art346-p1"],
        ["D14-q04", "D01-anexoi-clausulaquarta-p2"],
        "Não. A distribuidora não pode condicionar a alteração de titularidade ao pagamento de "
        "débito de titularidade de terceiros, nem exigir que você assine termo assumindo essa "
        "dívida.",
        ["moradores anteriores"],
        "Fato-chave ajustado pelo Pedro ('moradores anteriores', como na página D14-q04); a "
        "conferência manual é a referência.",
    ),
    (
        "T2-09",
        "coloquial",
        "H09",
        "devolucao_dobro",
        "A conta de luz veio com um valor cobrado a mais e eu já paguei. Eles só me devolvem o que "
        "paguei a mais ou tem alguma coisa além disso?",
        ["D01-art323-p2"],
        ["D01-anexoi-clausulaquarta-p2", "D14-q12", "D10-art42"],
        "A quantia paga a mais deve ser devolvida em dobro, atualizada pelo IPCA e com juros de 1% "
        "ao mês; a devolução só é simples se a distribuidora comprovar que o erro foi causado pelo "
        "consumidor ou, em condições específicas, por terceiro.",
        ["em dobro"],
        "",
    ),
    (
        "T2-10",
        "coloquial",
        "H10",
        "corte_90_dias",
        "Tenho uma conta de luz de quatro meses atrás que ficou sem pagar. A empresa ainda pode "
        "cortar minha luz por causa dela?",
        ["D01-art357"],
        ["D01-anexoi-clausulasexta-p2"],
        "Em regra, não: o corte é vedado depois de 90 dias da fatura vencida e não paga, salvo se a "
        "distribuidora comprovar que não cortou antes por determinação judicial ou outro motivo "
        "justificável.",
        ["90 dias"],
        "",
    ),
    (
        "T2-11",
        "coloquial",
        "H11",
        "mudar_vencimento",
        "Minha conta vence antes do meu salário cair. Posso pedir pra mudar o dia do vencimento?",
        ["D01-art338"],
        ["D14-q03", "D01-anexoi-clausulaquarta-p2"],
        "Sim. A distribuidora deve oferecer pelo menos seis datas de vencimento para você escolher; "
        "depois da mudança, a data só pode ser alterada de novo após 12 meses.",
        ["6 datas", "12 meses"],
        "",
    ),
    (
        "T2-12",
        "coloquial",
        "H12",
        "leitura_intervalo",
        "Minha conta deste mês veio com 40 dias de consumo. A leitura do relógio não tinha que ser "
        "feita todo mês?",
        ["D01-art260", "D01-art285"],
        [],
        "Sim: a leitura deve ser feita a cada cerca de 30 dias, com no mínimo 27 e no máximo 33 dias "
        "(salvo exceções, como o primeiro faturamento ou mudança de rota). Se passar de 33 dias, a "
        "distribuidora deve proporcionalizar o consumo ao número máximo de dias permitido.",
        ["33"],
        "",
    ),
    (
        "T2-16",
        "multi_trecho",
        "H13",
        "titularidade_debito",
        "Comprei um apartamento e quero passar a conta de luz pro meu nome. Em quanto tempo a "
        "distribuidora tem que fazer a troca e ela pode exigir que eu pague as contas atrasadas do "
        "antigo dono?",
        ["D01-art138-p3", "D01-art346-p1"],
        ["D14-q04"],
        "A troca deve ser feita em até 3 dias úteis na área urbana (5 na rural), e a distribuidora "
        "não pode condicioná-la ao pagamento de débito de titularidade de terceiros.",
        ["3 dias úteis", "terceiros"],
        "",
    ),
    (
        "T2-17",
        "multi_trecho",
        "H14",
        "devolucao_correcao",
        "Descobri que a empresa me cobrou a mais na conta de luz. Quanto ela tem que me devolver, "
        "com qual correção e até quando?",
        ["D01-art323-p1", "D01-art323-p2", "D01-art323-p3"],
        ["D14-q12"],
        "Deve devolver em dobro (simples apenas se comprovar erro atribuível ao consumidor ou, em "
        "condições específicas, a terceiro), com atualização pelo IPCA e juros de mora de 1% ao mês, "
        "até o segundo ciclo de faturamento posterior à constatação.",
        ["em dobro", "IPCA", "1% ao mês"],
        "",
    ),
    (
        "T2-18",
        "multi_trecho",
        "H15",
        "creditos_gd",
        "Tenho placa solar em casa. Por quanto tempo valem os créditos de energia que sobram e o que "
        "acontece com eles quando vencem?",
        ["D09-art13-p1", "D01-art655l"],
        ["D19-s01-p2"],
        "Os créditos expiram em 60 meses após o faturamento em que foram gerados e, depois disso, "
        "são revertidos para a modicidade tarifária, sem compensação ao consumidor.",
        ["60 meses", "modicidade tarifária"],
        "",
    ),
]
# Versões de voz das coloquiais (mesmo grupo e mesmo gabarito).
VOZ = [("T2-13", "T2-08"), ("T2-14", "T2-09"), ("T2-15", "T2-10")]
NEGATIVAS = [
    (
        "T2-19",
        "nao_consta",
        "H16",
        "agencia_horario",
        "Qual é o horário de funcionamento da agência de atendimento presencial da Enel no centro "
        "de São Paulo?",
    ),
    (
        "T2-20",
        "nao_consta",
        "H17",
        "estatistica_reclamacoes",
        "Quantas reclamações contra a Enel a ANEEL recebeu em 2025?",
    ),
    ("T2-21", "fora_dominio", "H18", "documentos", "Como faço para tirar a segunda via do RG?"),
    (
        "T2-22",
        "fora_dominio",
        "H19",
        "tv_assinatura",
        "A operadora de TV por assinatura pode cobrar multa se eu cancelar antes de um ano?",
    ),
]
DINAMICAS = [
    (
        "T2-23",
        "H20",
        "Vai ter desligamento programado no Brás na quinta-feira?",
        "Brás",
        "2026-11-12",
    ),
    (
        "T2-24",
        "H21",
        "Tem manutenção programada de energia em Perdizes amanhã?",
        "Perdizes",
        "2026-11-11",
    ),
]
TIPOS_PT = {"manutencao_programada": "manutenção programada", "obra": "obra", "poda": "poda"}


def _dinamicas(cfg: dict) -> list[Caso]:
    casos = []
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        cliente = TestClient(
            criar_app(Path(tmp) / "p.sqlite", RAIZ / cfg["api_paradas"]["arquivo_csv"])
        )
        for id_, grupo, pergunta, bairro, data in DINAMICAS:
            r = cliente.get("/paradas", params={"bairro": bairro, "data": data}).json()
            ps = [p for p in r["paradas"] if p["status"] != "cancelada"]
            dia = f"{data[8:10]}/{data[5:7]}/{data[:4]}"
            if ps:
                partes = [
                    f"{TIPOS_PT[p['tipo']]} das {p['inicio_local'][11:16]} às "
                    f"{p['fim_local'][11:16]} (registro {p['id']})"
                    for p in ps
                ]
                gab = f"Sim: há parada programada em {bairro} em {dia}: " + "; ".join(partes) + "."
            else:
                gab = f"Não há parada programada registrada para {bairro} em {dia}."
            casos.append(
                Caso(
                    id=id_,
                    split="pendente",
                    tipo="dinamica",
                    grupo=grupo,
                    tema="paradas",
                    pergunta=pergunta,
                    deve_recusar=False,
                    requer_api=True,
                    resposta_gabarito=gab,
                    api_esperada={
                        "bairro": bairro,
                        "data": data,
                        "registros_esperados": [p["id"] for p in ps],
                        "situacao": "com_parada" if ps else "sem_parada",
                    },
                )
            )
    return casos


def montar(cfg: dict) -> list[Caso]:
    casos = {}
    for id_, tipo, grupo, tema, perg, gold, eq, gab, fatos, obs in RESPONDIVEIS:
        casos[id_] = Caso(
            id=id_,
            split="pendente",
            tipo=tipo,
            grupo=grupo,
            tema=tema,
            pergunta=perg,
            deve_recusar=False,
            chunk_ids_gold=gold,
            gold_equivalentes=eq,
            resposta_gabarito=gab,
            fatos_chave=fatos,
            observacoes=obs,
        )
    for i, (id_, origem) in enumerate(VOZ):
        base = casos[origem]
        casos[id_] = base.model_copy(
            update={
                "id": id_,
                "tipo": "ruido",
                "origem": "voz",
                "pergunta": ruido_de_voz(base.pergunta, SEMENTE_VOZ + i),
                "observacoes": f"Versão com ruído de voz de {origem}.",
            }
        )
    for id_, tipo, grupo, tema, perg in NEGATIVAS:
        casos[id_] = Caso(
            id=id_,
            split="pendente",
            tipo=tipo,
            grupo=grupo,
            tema=tema,
            pergunta=perg,
            deve_recusar=True,
            resposta_gabarito=NAO_CONSTA if tipo == "nao_consta" else FORA,
        )
    for c in _dinamicas(cfg):
        casos[c.id] = c
    ordem = sorted(casos, key=lambda i: int(i.split("-")[1]))
    return [Caso.model_validate(casos[i].model_dump()) for i in ordem]


def _revisao(casos: list[Caso], chunks: dict, govbr: set[str], mascarar: bool) -> str:
    linhas = [
        "# Revisão do test novo, T2 (Fase 8B)",
        "",
        "**Para:** Pedro. São 24 perguntas novas, que não repetem nenhuma das 60 do test "
        "original, das 45 de calibração nem das 13 extras. Depois da sua revisão, o T2 é "
        "congelado com hash e só é usado **uma vez**, no fim, para medir C1, C2 original e C2 "
        "final.",
        "",
        "Para cada pergunta, confira: (1) se a pergunta é clara; (2) se o **gabarito** está "
        "certo pelo texto dos trechos mostrados; (3) se os fatos-chave fazem sentido. Responda "
        'no chat só com as correções, por exemplo: "T2-04: incluir que a dívida continua".',
        "",
        "Composição: 7 diretas, 5 coloquiais, 3 de voz (versões das coloquiais T2-08 a T2-10), "
        '3 multi-trecho, 2 "não consta", 2 fora do domínio e 2 sobre a agenda.',
    ]
    if mascarar:
        linhas += [
            "",
            "> Nesta versão, os trechos de páginas gov.br aparecem como hash. A versão "
            "completa está em `avaliacao/runs/local/revisao_teste2_completa.md`.",
        ]
    for c in casos:
        linhas += [
            "",
            f"### {c.id} ({c.tipo}{', voz' if c.origem == 'voz' else ''})",
            "",
            f"**Pergunta:** {c.pergunta}",
            "",
            f"**Gabarito:** {c.resposta_gabarito}",
        ]
        if c.fatos_chave:
            linhas += ["", f"**Fatos-chave:** {', '.join(c.fatos_chave)}"]
        if c.api_esperada:
            linhas += ["", f"**Agenda:** {c.api_esperada.model_dump()}"]
        if c.observacoes:
            linhas += ["", f"*{c.observacoes}*"]
        if c.origem == "voz":
            continue
        for rotulo, ids in (
            ("Trecho gold", c.chunk_ids_gold),
            ("Equivalente", c.gold_equivalentes),
        ):
            for i in ids:
                texto = chunks[i]["texto"]
                if mascarar and i in govbr:
                    texto = (
                        f"[página gov.br; sha256 {hashlib.sha256(texto.encode()).hexdigest()[:12]}]"
                    )
                linhas += ["", f"- **{rotulo} `{i}`:** " + texto.replace("\n", " ")[:900]]
    return "\n".join(linhas) + "\n"


def congelar() -> int:
    """Grava avaliacao/teste2.jsonl (split test2) e o hash, depois da revisão do Pedro."""
    if TESTE2.exists():
        print(f"{TESTE2.relative_to(RAIZ)} já existe: o T2 está congelado. Nada feito.")
        return 1
    casos = [c.model_copy(update={"split": "test2"}) for c in carregar(CANDIDATAS2)]
    gravar(casos, TESTE2)
    sha = hashlib.sha256(TESTE2.read_bytes()).hexdigest()
    LOCK2.write_text(f"{sha}  teste2.jsonl\n", encoding="utf-8", newline="\n")
    print(f"{TESTE2.relative_to(RAIZ)}: {len(casos)} perguntas; sha256 {sha[:12]}")
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--congelar" in sys.argv:
        return congelar()
    cfg = carregar_config()
    casos = montar(cfg)
    chunks = {c["chunk_id"]: c for c in denso.trechos_indexaveis()}
    faltam = [g for c in casos for g in c.gold_v2 if g not in chunks]
    if faltam:
        raise SystemExit(f"trechos inexistentes na base: {faltam}")
    govbr = {i for i, c in chunks.items() if not c.get("versionado", True)}
    gravar(casos, CANDIDATAS2)
    for destino, mascarar in ((REVISAO, True), (REVISAO_LOCAL, False)):
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(_revisao(casos, chunks, govbr, mascarar), encoding="utf-8", newline="\n")
    from collections import Counter

    print(len(casos), "perguntas:", dict(Counter(c.tipo for c in casos)))
    for c in casos:
        if c.origem == "voz" or c.tipo == "dinamica":
            print(" ", c.id, "|", c.pergunta, "|", c.resposta_gabarito[:120])
    return 0


if __name__ == "__main__":
    sys.exit(main())
