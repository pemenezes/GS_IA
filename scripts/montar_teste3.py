"""Test T3 (Fase 8B): 24 perguntas sobre temas que nenhum conjunto anterior usou como gabarito.

  python scripts/montar_teste3.py              # candidatas e documento de revisão
  python scripts/montar_teste3.py --congelar   # depois da revisão: teste3.jsonl e teste3.lock

Escrito depois da escolha do C2+M, para medir essa escolha sem o viés de seleção do T1 e do T2:
o sistema não muda depois de rodar o T3. Mesma composição do T2; os gabaritos vêm do texto dos
trechos indicados (lidos na base), as versões de voz saem de ruido_de_voz com semente fixa e a
resposta das perguntas da agenda vem da API simulada (data de referência do config.yaml).

Grava avaliacao/teste3_candidatas.jsonl, avaliacao/revisao/revisao_teste3.md (versionado;
trechos de páginas gov.br trocados por hash) e avaliacao/runs/local/revisao_teste3_completa.md.
"""

# ruff: noqa: E501 (tabela de perguntas e gabaritos)
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from src.avaliacao.casos import (  # noqa: E402
    CANDIDATAS3,
    LOCK3,
    TESTE3,
    Caso,
    carregar,
    gravar,
)
from src.avaliacao.ruido import ruido_de_voz  # noqa: E402
from src.config import RAIZ, carregar_config  # noqa: E402
from src.paradas_api.app import criar_app  # noqa: E402
from src.rag import denso  # noqa: E402

REVISAO = RAIZ / "avaliacao" / "revisao" / "revisao_teste3.md"
REVISAO_LOCAL = RAIZ / "avaliacao" / "runs" / "local" / "revisao_teste3_completa.md"
SEMENTE_VOZ = 2027
ANTERIORES = [
    RAIZ / "avaliacao" / "teste.jsonl",
    RAIZ / "avaliacao" / "teste2.jsonl",
    RAIZ / "avaliacao" / "retrieval" / "calibracao.jsonl",
    RAIZ / "avaliacao" / "agente" / "dinamicas_extra.jsonl",
]

NAO_CONSTA = "Não consta na base: o assistente deve recusar e indicar o canal oficial."
FORA = "Fora do domínio: o assistente trata só de energia elétrica."

# id, tipo, grupo, tema, pergunta, gold, equivalentes, gabarito, fatos-chave, observações
RESPONDIVEIS = [
    (
        "T3-01",
        "direta",
        "H01",
        "parcelamento_baixa_renda",
        "A distribuidora é obrigada a parcelar a conta de luz atrasada de um consumidor da "
        "subclasse residencial baixa renda que pedir o parcelamento?",
        ["D01-art344"],
        ["D14-q18"],
        "Sim, se o débito não tiver sido parcelado antes: para a subclasse residencial baixa renda, "
        "o parcelamento é obrigatório quando o consumidor pede, com no mínimo três parcelas, na "
        "fatura de energia ou, a pedido do consumidor, por outro meio.",
        ["3 parcelas"],
        "",
    ),
    (
        "T3-02",
        "direta",
        "H02",
        "garantia_residencial",
        "A distribuidora pode exigir caução ou outra garantia de uma casa que deixou de pagar mais "
        "de uma conta de luz no mesmo ano?",
        ["D01-art345-p1"],
        [],
        "Não. A exigência de garantias (quando há mais de uma fatura não paga em 12 meses) não se "
        "aplica à classe residencial, à subclasse rural residencial nem a prestadores de serviços "
        "públicos essenciais.",
        ["residencial"],
        "A negação (não se aplica à classe residencial) é conferida na revisão manual.",
    ),
    (
        "T3-03",
        "direta",
        "H03",
        "medidor_defeito",
        "Quando a inspeção constata que o medidor da distribuidora está com defeito, em quanto "
        "tempo ela tem que trocar o aparelho?",
        ["D01-art252"],
        [],
        "Em até 30 dias após a data em que o defeito foi constatado, informando ao consumidor, por "
        "meio auditável, as leituras do medidor retirado e do instalado.",
        ["30 dias"],
        "",
    ),
    (
        "T3-04",
        "direta",
        "H04",
        "reclamacao_diferenca",
        "A distribuidora me notificou que vai cobrar uma diferença no faturamento e eu não "
        "concordo. Até quando posso reclamar e em quanto tempo ela tem que responder?",
        ["D01-art325-p2"],
        [],
        "Você pode registrar reclamação na distribuidora em até 30 dias contados da notificação; "
        "ela deve solucionar a reclamação e comunicar a você no prazo de 15 dias.",
        ["30 dias", "15 dias"],
        "",
    ),
    (
        "T3-05",
        "direta",
        "H05",
        "pagamento_pix",
        "Posso escolher pagar a minha conta de luz pelo PIX? Depois que eu pedir, a partir de "
        "quando a mudança passa a valer?",
        ["D01-art339a"],
        ["D01-art327"],
        "Sim. O consumidor pode escolher o código de resposta rápida (QR) do PIX como forma de "
        "pagamento e cancelar a escolha a qualquer tempo; a mudança deve estar disponível até o "
        "primeiro ciclo completo de faturamento seguinte ao pedido.",
        ["ciclo completo"],
        "",
    ),
    (
        "T3-06",
        "direta",
        "H06",
        "creditos_antigos",
        "Quem tem placa solar e acumulou créditos de energia em meses diferentes: quais créditos "
        "são usados primeiro para abater o consumo?",
        ["D09-art13-p2"],
        ["D09-art13-p1"],
        "Sempre os créditos mais antigos da unidade consumidora participante do Sistema de "
        "Compensação de Energia Elétrica (SCEE).",
        ["mais antigos"],
        "",
    ),
    (
        "T3-07",
        "direta",
        "H07",
        "tarifa_social_excedente",
        "Na Tarifa Social de Energia Elétrica, se a casa consumir 100 kWh no mês, sobre quanto de "
        "energia é feita a cobrança?",
        ["D17-p1-s08"],
        ["D17-p2-q02", "D02-art1"],
        "A gratuidade vale para o consumo de até 80 kWh por mês; com 100 kWh, é cobrada só a "
        "parcela excedente, ou seja, 20 kWh.",
        ["20 kWh"],
        "O limite de 80 kWh já aparece no T1 (T-010 e T-012); o fato novo é a cobrança só do "
        "excedente. Troca da pergunta sobre a Lei 13.460, por decisão do Pedro.",
    ),
    (
        "T3-08",
        "coloquial",
        "H08",
        "suspensao_indevida_pix",
        "Cortaram minha luz por falta de pagamento, mas eu tinha pagado a conta pelo PIX uma hora "
        "antes do corte. Esse corte foi certo?",
        ["D01-art361"],
        [],
        "Não. A suspensão é considerada indevida quando a fatura foi paga pelo código QR do PIX "
        "antes da execução da suspensão (ou até a data limite da notificação).",
        ["indevida"],
        "",
    ),
    (
        "T3-09",
        "coloquial",
        "H09",
        "impedimento_acesso",
        "O leiturista colocou na conta que houve impedimento de acesso, mas meu relógio de luz fica "
        "no muro, virado pra calçada. Isso conta como impedimento?",
        ["D01-art277"],
        [],
        "Não. O impedimento de acesso exige, ao mesmo tempo, medidor dentro do imóvel sem livre "
        "acesso ao leiturista e leitura não feita por responsabilidade do consumidor; a leitura "
        "frustrada em medidor no limite da via pública não caracteriza impedimento de acesso.",
        ["via pública"],
        "",
    ),
    (
        "T3-10",
        "coloquial",
        "H10",
        "luz_do_povo_mudanca",
        "Recebo o benefício do Luz do Povo e vou me mudar de casa no mês que vem. Perco o "
        "benefício?",
        ["D17-p2-q08"],
        [],
        "Não automaticamente. É preciso manter o CadÚnico atualizado e informar à distribuidora os "
        "dados da nova unidade consumidora, para que ela verifique a elegibilidade e vincule o "
        "benefício ao novo endereço.",
        ["CadÚnico"],
        "",
    ),
    (
        "T3-11",
        "coloquial",
        "H11",
        "luz_do_povo_titularidade",
        "Estou inscrito no CadÚnico, mas a conta de luz da casa onde moro está no nome do "
        "proprietário. Como faço pra receber o benefício do Luz do Povo?",
        ["D17-p2-q07"],
        [],
        "É preciso entrar em contato com a distribuidora e apresentar a documentação exigida para "
        "vincular o seu cadastro à unidade consumidora; os procedimentos podem variar conforme a "
        "distribuidora.",
        ["document"],
        "A raiz 'document' reconhece 'documentação' e 'documentos'.",
    ),
    (
        "T3-12",
        "coloquial",
        "H12",
        "parcelamento_antecipado",
        "Parcelei uma dívida da conta de luz e agora entrou um dinheiro. Se eu quitar as parcelas "
        "antes, pago menos juros?",
        ["D01-art344"],
        [],
        "Sim. O consumidor tem direito ao pagamento antecipado do parcelamento, total ou parcial, "
        "com redução proporcional dos juros e demais acréscimos.",
        ["proporcional"],
        "",
    ),
    (
        "T3-16",
        "multi_trecho",
        "H13",
        "parcelamento_atraso",
        "Sou baixa renda e pedi pra parcelar uma conta de luz atrasada. A distribuidora pode negar? "
        "E se eu atrasar uma parcela, o que pode ser cobrado?",
        ["D01-art344", "D01-art343"],
        ["D14-q18"],
        "Não pode negar se o débito não tiver sido parcelado antes: para baixa renda, o parcelamento "
        "é obrigatório a pedido do consumidor, com no mínimo três parcelas. O atraso no pagamento "
        "implica multa de até 2%, atualização monetária pelo IPCA e juros de mora de 1% ao mês.",
        ["3 parcelas", "2%", "1% ao mês"],
        "",
    ),
    (
        "T3-17",
        "multi_trecho",
        "H14",
        "suspensao_indevida_religacao",
        "Em que situações o corte de luz por falta de pagamento é considerado indevido e, nesse "
        "caso, em quanto tempo a distribuidora tem que religar?",
        ["D01-art361", "D01-art362"],
        [],
        "É indevido se a fatura foi paga até a data limite da notificação, se foi paga pelo PIX "
        "antes da execução do corte ou se a suspensão não seguiu a REN 1.000. A religação deve "
        "ocorrer em até 4 horas, contadas da constatação ou da comunicação do consumidor, em "
        "qualquer dia e horário, e a distribuidora deve creditar a compensação.",
        ["4 horas", "PIX"],
        "",
    ),
    (
        "T3-18",
        "multi_trecho",
        "H15",
        "medidor_troca",
        "A distribuidora vai trocar o medidor da minha casa porque ele está com defeito. Quanto "
        "tempo ela tem pra fazer a troca e eu tenho que pagar pelo medidor novo?",
        ["D01-art252", "D14-q16"],
        [],
        "A troca deve ser feita em até 30 dias após constatado o defeito, e o medidor é fornecido e "
        "instalado pela distribuidora sem custo (o equipamento é gratuito); a substituição deve ser "
        "comunicada ao consumidor por correspondência específica com o motivo.",
        ["30 dias", "gratuit"],
        "A raiz 'gratuit' reconhece 'gratuito' e 'gratuitamente'; 'sem custo' é conferido na "
        "revisão manual.",
    ),
]
# Versões de voz das coloquiais (mesmo grupo e mesmo gabarito).
VOZ = [("T3-13", "T3-08"), ("T3-14", "T3-09"), ("T3-15", "T3-10")]
NEGATIVAS = [
    (
        "T3-19",
        "nao_consta",
        "H16",
        "lucro_distribuidora",
        "Qual foi o lucro da Enel Distribuição São Paulo em 2025?",
    ),
    (
        "T3-20",
        "nao_consta",
        "H17",
        "preco_solar",
        "Quanto custa, em média, instalar um sistema de energia solar de 5 kW numa casa em São "
        "Paulo?",
    ),
    (
        "T3-21",
        "fora_dominio",
        "H18",
        "seguro_desemprego",
        "Como faço para dar entrada no seguro-desemprego?",
    ),
    (
        "T3-22",
        "fora_dominio",
        "H19",
        "condominio",
        "O condomínio pode me multar por barulho depois das 22h?",
    ),
]
DINAMICAS = [
    (
        "T3-23",
        "H20",
        "Vai ter desligamento programado de energia no Mandaqui na segunda-feira, dia 16?",
        "Mandaqui",
        "2026-11-16",
    ),
    (
        "T3-24",
        "H21",
        "Tem manutenção programada de luz em Pinheiros na sexta-feira?",
        "Pinheiros",
        "2026-11-13",
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


def _sem_sobreposicao(casos: list[Caso]) -> None:
    """Falha se um gold original ou uma pergunta já apareceu num conjunto anterior."""
    golds, perguntas = set(), set()
    for arq in ANTERIORES:
        with open(arq, encoding="utf-8") as f:
            for linha in f:
                x = json.loads(linha)
                golds.update(x.get("chunk_ids_gold") or [])
                perguntas.add(x.get("pergunta", "").strip().lower())
    repetidos = sorted({g for c in casos for g in c.chunk_ids_gold if g in golds})
    if repetidos:
        print("aviso: trechos gold já usados antes (só como apoio de multi-trecho):", repetidos)
    iguais = [c.id for c in casos if c.pergunta.strip().lower() in perguntas]
    if iguais:
        raise SystemExit(f"perguntas repetidas de conjuntos anteriores: {iguais}")


def _revisao(casos: list[Caso], chunks: dict, govbr: set[str], mascarar: bool) -> str:
    linhas = [
        "# Revisão do test T3 (Fase 8B)",
        "",
        "**Para:** Pedro. São 24 perguntas sobre temas que nenhum conjunto anterior usou como "
        "gabarito (T1, T2, calibração e extras da agenda). Depois da sua revisão, o T3 é "
        "congelado com hash e usado **uma vez**, para medir o C2 original e o C2+M sem o viés "
        "de seleção do T1 e do T2. O sistema não muda depois do T3.",
        "",
        "Para cada pergunta, confira: (1) se a pergunta é clara; (2) se o **gabarito** está "
        "certo pelo texto dos trechos mostrados; (3) se os fatos-chave fazem sentido. Responda "
        'no chat só com as correções, por exemplo: "T3-04: incluir que a reclamação é por escrito".',
        "",
        "Composição: 7 diretas, 5 coloquiais, 3 de voz (versões das coloquiais T3-08 a T3-10), "
        '3 multi-trecho, 2 "não consta", 2 fora do domínio e 2 sobre a agenda.',
    ]
    if mascarar:
        linhas += [
            "",
            "> Nesta versão, os trechos de páginas gov.br aparecem como hash. A versão "
            "completa está em `avaliacao/runs/local/revisao_teste3_completa.md`.",
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
    """Grava avaliacao/teste3.jsonl (split test3) e o hash, depois da revisão do Pedro."""
    if TESTE3.exists():
        print(f"{TESTE3.relative_to(RAIZ)} já existe: o T3 está congelado. Nada feito.")
        return 1
    casos = [c.model_copy(update={"split": "test3"}) for c in carregar(CANDIDATAS3)]
    gravar(casos, TESTE3)
    sha = hashlib.sha256(TESTE3.read_bytes()).hexdigest()
    LOCK3.write_text(f"{sha}  teste3.jsonl\n", encoding="utf-8", newline="\n")
    print(f"{TESTE3.relative_to(RAIZ)}: {len(casos)} perguntas; sha256 {sha[:12]}")
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
    _sem_sobreposicao(casos)
    govbr = {i for i, c in chunks.items() if not c.get("versionado", True)}
    gravar(casos, CANDIDATAS3)
    for destino, mascarar in ((REVISAO, True), (REVISAO_LOCAL, False)):
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(_revisao(casos, chunks, govbr, mascarar), encoding="utf-8", newline="\n")
    print(len(casos), "perguntas:", dict(Counter(c.tipo for c in casos)))
    for c in casos:
        if c.origem == "voz" or c.tipo == "dinamica":
            print(" ", c.id, "|", c.pergunta, "|", c.resposta_gabarito[:120])
    return 0


if __name__ == "__main__":
    sys.exit(main())
