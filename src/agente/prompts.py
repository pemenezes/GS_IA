"""Prompts do agente (C2): roteador e resposta com registros da agenda de paradas.

Ficam fora de src/rag/prompt.py para não mudar o hash dos prompts de C0 e C1, já medidos.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from typing import Any

from unidecode import unidecode

from src.rag.prompt import _CABECALHO, _REGRAS_COMUNS, formatar_trecho

SISTEMA_ROTEADOR = """Você classifica perguntas recebidas pelo Luz Cidadã, um assistente sobre \
direitos do consumidor de energia elétrica na cidade de São Paulo. Há duas fontes:
- AGENDA: agenda de paradas programadas (manutenção, obra ou poda) da distribuidora, por bairro \
e data;
- NORMAS: leis e regras da ANEEL sobre direitos, prazos, tarifas e ressarcimentos.

Preencha:
- precisa_agenda: true só se a pessoa quer saber se há ou haverá parada, desligamento, \
manutenção ou falta de luz PROGRAMADA num lugar e numa data (ou nos próximos dias). Perguntas \
sobre direitos, prazos, regras ou faltas de luz que já aconteceram têm precisa_agenda=false, \
mesmo que citem um bairro ou uma data.
- precisa_normas: true se a pergunta pede uma regra, um direito ou um prazo (pode ser true junto \
com precisa_agenda).
- bairro: o nome do bairro como foi escrito na pergunta, ou null.
- data: a expressão de data como foi escrita ("amanhã", "dia 20", "nesta quinta"), ou null.
- pergunta_normas: se precisa_agenda e precisa_normas forem true, a parte da pergunta sobre \
regras, reescrita como uma pergunta completa e sem o bairro e a data; senão, null.

Exemplos:
Pergunta: Vai ter desligamento programado em Pinheiros depois de amanhã?
{"precisa_agenda": true, "precisa_normas": false, "bairro": "Pinheiros", "data": "depois de \
amanhã", "pergunta_normas": null}
Pergunta: Minha luz caiu ontem no Sacomã e queimou a geladeira. Tenho direito a ressarcimento?
{"precisa_agenda": false, "precisa_normas": true, "bairro": null, "data": null, \
"pergunta_normas": null}
Pergunta: Vai ter manutenção em Pirituba no sábado? Eles têm que me avisar antes?
{"precisa_agenda": true, "precisa_normas": true, "bairro": "Pirituba", "data": "sábado", \
"pergunta_normas": "A distribuidora tem que avisar antes de uma manutenção programada?"}

Responda APENAS no formato JSON do schema fornecido."""

SISTEMA_C2 = (
    _CABECALHO
    + """

REGRAS
1. Responda SOMENTE com base nos REGISTROS DA AGENDA e nos TRECHOS fornecidos. Não use \
conhecimento externo.
2. Os REGISTROS DA AGENDA já são da data ou do período que a pessoa perguntou: não refaça contas \
de data. Quando a consulta não encontrou paradas, isso É a resposta: use recusa=false, diga que \
não há parada programada registrada para aquele bairro e data e cite a consulta. Se só parte da \
pergunta tiver base, responda essa parte (recusa=false) e diga o que não encontrou. Só use \
recusa=true se nada da pergunta tiver base; nesse caso deixe fontes vazia, explique em uma frase \
o que falta, indique procurar a distribuidora, a ANEEL ou o Procon e não escreva números. Só \
informe telefone se ele estiver nos trechos.
3. Para cada informação, cite a fonte em fontes: registro da agenda com tipo "api" e o id do \
registro (por exemplo, PAR-00123 ou consulta-mooca-20261110); trecho de norma com tipo "norma" e \
o id do trecho. Copie em trecho_citado, letra por letra, a frase que sustenta a resposta (até 400 \
caracteres).
4. Informe datas, horários e status exatamente como nos registros. Se a consulta à agenda não \
encontrou paradas, diga que não há parada programada registrada para aquele bairro e período e \
cite a consulta. Nunca invente paradas, horários, bairros, prazos ou valores.
5. Se houver conflito entre trechos, mencione e prefira o mais recente ou o mais específico. Se um \
trecho tiver ALERTA, siga o alerta e prefira o ato normativo.
"""
    + _REGRAS_COMUNS
    + """

Responda APENAS no formato JSON do schema fornecido."""
)

TIPOS = {
    "manutencao_programada": "manutenção programada",
    "obra": "obra na rede",
    "poda": "poda de árvores",
}
STATUS = {
    "agendada": "agendada",
    "em_andamento": "em andamento",
    "concluida": "concluída",
    "cancelada": "cancelada",
}


def _hora(t: dt.datetime) -> str:
    curta = f"{t.hour}h" + (f"{t.minute:02d}" if t.minute else "")
    return f"{t:%H:%M} ({curta})"


def registro_como_trecho(p: dict[str, Any]) -> dict[str, Any]:
    """Registro da API no formato de trecho citável (horários nas duas grafias, 09:00 e 9h)."""
    ini = dt.datetime.fromisoformat(p["inicio_local"])
    fim = dt.datetime.fromisoformat(p["fim_local"])
    ate = _hora(fim) + ("" if fim.date() == ini.date() else f" do dia {fim:%d/%m/%Y}")
    texto = (
        f"Agenda de paradas programadas > {p['bairro']} > {ini:%d/%m/%Y}\n"
        f"Parada programada em {p['bairro']}, no dia {ini:%d/%m/%Y}, das {_hora(ini)} às {ate}. "
        f"Tipo: {TIPOS[p['tipo']]}. Status: {STATUS[p['status']]}. Motivo: {p['motivo']}."
    )
    return {
        "chunk_id": p["id"],
        "fonte": "Agenda de paradas programadas",
        "texto": texto,
        "tipo_citacao": "api",
    }


def consulta_vazia_como_trecho(bairro: str, inicio: dt.date, fim: dt.date) -> dict[str, Any]:
    slug = "".join(c for c in unidecode(bairro).lower() if c.isalnum()) or "bairro"
    if inicio == fim:
        periodo, id_ = f"em {inicio:%d/%m/%Y}", f"consulta-{slug}-{inicio:%Y%m%d}"
    else:
        periodo = f"entre {inicio:%d/%m/%Y} e {fim:%d/%m/%Y}"
        id_ = f"consulta-{slug}-{inicio:%Y%m%d}-{fim:%Y%m%d}"
    texto = (
        f"Agenda de paradas programadas > {bairro} > consulta\n"
        f"A consulta à agenda de paradas programadas não encontrou nenhuma parada para {bairro} "
        f"{periodo}."
    )
    return {
        "chunk_id": id_,
        "fonte": "Agenda de paradas programadas",
        "texto": texto,
        "tipo_citacao": "api",
    }


# Correção A (Fase 8): a parte sobre regras vem sempre reescrita em português padrão, para a busca
# e o portão não sofrerem com erros de grafia da voz e com a linguagem coloquial.
SISTEMA_ROTEADOR_REESCRITA = SISTEMA_ROTEADOR.replace(
    "- pergunta_normas: se precisa_agenda e precisa_normas forem true, a parte da pergunta "
    "sobre regras, reescrita como uma pergunta completa e sem o bairro e a data; senão, null.",
    "- pergunta_normas: se precisa_normas for true, a parte da pergunta sobre regras, reescrita "
    "como uma pergunta completa em português padrão: corrija erros de grafia e de digitação, "
    "troque gírias por palavras comuns, mantenha todos os detalhes do caso (quem, o quê, "
    "quanto tempo) e tire o bairro e a data; senão, null.",
).replace(
    '"pergunta_normas": null}\nPergunta: Vai ter manutenção',
    '"pergunta_normas": "Tenho direito a ressarcimento da geladeira que queimou depois de uma '
    'queda de energia?"}\nPergunta: Vai ter manutenção',
)
assert "corrija erros de grafia" in SISTEMA_ROTEADOR_REESCRITA
assert "Tenho direito a ressarcimento da geladeira" in SISTEMA_ROTEADOR_REESCRITA


def mensagens_roteador(pergunta: str, reescrever: bool = False) -> list[dict[str, str]]:
    sistema = SISTEMA_ROTEADOR_REESCRITA if reescrever else SISTEMA_ROTEADOR
    return [
        {"role": "system", "content": sistema},
        {"role": "user", "content": f"Pergunta: {pergunta}"},
    ]


def mensagens_c2(
    pergunta: str,
    registros: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
    data: str,
    descricao_consulta: str,
) -> list[dict[str, str]]:
    partes = [
        f"REGISTROS DA AGENDA ({descricao_consulta}):\n"
        + "\n\n".join(f"[{r['chunk_id']}]\n{r['texto']}" for r in registros)
    ]
    if chunks:
        partes.append("TRECHOS:\n" + "\n\n".join(formatar_trecho(c) for c in chunks))
    partes.append(f"PERGUNTA DO USUÁRIO:\n{pergunta}")
    return [
        {"role": "system", "content": SISTEMA_C2.format(data=data)},
        {"role": "user", "content": "\n\n".join(partes)},
    ]


def hash_prompts_agente() -> str:
    texto = SISTEMA_ROTEADOR + SISTEMA_C2 + json.dumps([TIPOS, STATUS], ensure_ascii=False)
    return hashlib.sha256(texto.encode()).hexdigest()[:12]


def hash_prompt_reescrita() -> str:
    return hashlib.sha256(SISTEMA_ROTEADOR_REESCRITA.encode()).hexdigest()[:12]
