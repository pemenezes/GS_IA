"""Métricas automáticas da geração (Fase 5; seção 7.2 do plano).

A acurácia automática compara a resposta com os fatos-chave e os fatos proibidos do gabarito,
depois de normalizar a forma de escrever números ("15 (quinze) minutos", "quinze minutos" e
"15 minutos" ficam iguais). É um indicador: a conferência humana do test é feita na Fase 8.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from unidecode import unidecode

from src.avaliacao.casos import Caso
from src.avaliacao.recuperacao import NEGATIVOS, RESPONDIVEIS, wilson
from src.rag.validador import normalizar_texto, numeros

_UNIDADES = {
    "zero": 0,
    "um": 1,
    "uma": 1,
    "dois": 2,
    "duas": 2,
    "tres": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
    "dez": 10,
    "onze": 11,
    "doze": 12,
    "treze": 13,
    "catorze": 14,
    "quatorze": 14,
    "quinze": 15,
    "dezesseis": 16,
    "dezessete": 17,
    "dezoito": 18,
    "dezenove": 19,
    "vinte": 20,
    "trinta": 30,
    "quarenta": 40,
    "cinquenta": 50,
    "sessenta": 60,
    "setenta": 70,
    "oitenta": 80,
    "noventa": 90,
    "cem": 100,
    "cento": 100,
    "duzentos": 200,
    "trezentos": 300,
    "quatrocentos": 400,
    "quinhentos": 500,
}
_PALAVRA = "|".join(sorted(_UNIDADES, key=len, reverse=True))
_POR_EXTENSO = re.compile(rf"\b(?:{_PALAVRA})(?:\s+e\s+(?:{_PALAVRA}))*\b")


def _extenso_para_digitos(m: re.Match[str]) -> str:
    return str(sum(_UNIDADES[p] for p in m.group(0).split() if p != "e"))


def canon(texto: str) -> str:
    t = unidecode(texto).lower()
    t = re.sub(r"quilowatts?[-\s]*horas?", "kwh", t)
    t = re.sub(r"quilowatts?", "kw", t)
    t = re.sub(r"(\d)\s*\(\s*[a-z\s-]+\)", r"\1", t)  # "15 (quinze)" -> "15"
    t = _POR_EXTENSO.sub(_extenso_para_digitos, t)
    t = re.sub(r"(\d)[oa]\b", r"\1", t)  # ordinais: "1º de janeiro" -> "1 de janeiro"
    t = re.sub(r"(\d)\s*h\b", r"\1 horas", t)
    t = re.sub(r"(\d)\s*por\s*cento\b", r"\1%", t)
    t = t.replace("/mes", " por mes").replace("/ mes", " por mes")
    t = re.sub(r"(\d)([a-z])", r"\1 \2", t)
    t = re.sub(r"(\d)\.(\d{3})\b", r"\1\2", t)  # milhar
    return re.sub(r"\s+", " ", t).strip()


def contem_fato(resposta: str, fato: str) -> bool:
    alvo = re.escape(canon(fato))
    return re.search(rf"(?<![\d,]){alvo}(?![\d])", canon(resposta)) is not None


_NEGA_REGRA = re.compile(
    r"\bnao (ha|existe|existem|tem|possui|define|definem|especifica)\b.{0,60}?"
    r"\b(norma|regra|prazo|lei|obrigacao|obrigatori|informacao oficial|valor|potencia|direito|"
    r"desconto|oficial|definid|legal)"
)


def nega_regra(texto: str) -> bool:
    """Heurística: a resposta afirma que não existe regra, prazo ou direito sobre o assunto."""
    return _NEGA_REGRA.search(unidecode(texto).lower()) is not None


def avaliar_linha(
    caso: Caso, saida: dict[str, Any], textos_gold: list[str], textos_fornecidos: list[str] = ()
) -> dict[str, Any]:
    """Métricas de uma pergunta a partir da saída gravada pelo runner.

    `textos_fornecidos` são os trechos que o C1 entregou ao modelo: um número que está neles não
    é inventado, mesmo que não esteja no gold.
    """
    r = saida["resposta"]
    primeira = saida["tentativas"][0] if saida["tentativas"] else None
    m: dict[str, Any] = {
        "id": caso.id,
        "tipo": caso.tipo,
        "json_valido_1a": None if primeira is None else primeira["categoria"] in ("ok", "regras"),
        "regras_1a": None if primeira is None else primeira["categoria"] == "ok",
        "valida_final": r is not None,
        "recusou": bool(r and r["recusa"]),
        "origem": saida["origem"],
    }
    if r is None or r["recusa"]:
        m.update(acuracia=False if caso.tipo in RESPONDIVEIS else None, alucinacao=None)
        m["citacao_correta"] = None
        if r is not None and caso.tipo in RESPONDIVEIS:
            m["recusa_nega_regra"] = nega_regra(r["resposta"])
        return m
    texto = r["resposta"]
    if caso.tipo in RESPONDIVEIS:
        tem = all(contem_fato(texto, f) for f in caso.fatos_chave)
        proibido = [f for f in caso.fatos_proibidos if contem_fato(texto, f)]
        m["acuracia"] = tem and not proibido
        m["fatos_ausentes"] = [f for f in caso.fatos_chave if not contem_fato(texto, f)]
        m["fatos_proibidos_presentes"] = proibido
        base = " ".join([caso.pergunta, caso.resposta_gabarito, *textos_gold, *textos_fornecidos])
        inventados = sorted(numeros(texto) - numeros(base))
        m["numeros_fora_do_gabarito"] = inventados
        m["alucinacao"] = bool(proibido or inventados)
        ultima = saida["tentativas"][-1] if saida["tentativas"] else {}
        cit = {c["id"]: c for c in ultima.get("citacoes", [])}
        ids = [f["id"].strip().strip("[]") for f in r["fontes"]]
        m["citacao_correta"] = any(
            i in caso.gold_v2 and cit.get(i, {}).get("casamento", "nenhum") != "nenhum" for i in ids
        )
    else:
        m["acuracia"] = None
        m["citacao_correta"] = None
        # Responder uma "não consta" é afirmar algo que a base não sustenta.
        m["alucinacao"] = True if caso.tipo == "nao_consta" else None
    return m


JANELA_LITERAL = 60  # caracteres seguidos de uma página gov.br que bastam para mascarar o campo


def _tem_trecho_literal(texto: str, corpos: list[str]) -> bool:
    t = normalizar_texto(texto)
    return any(
        corpo[i : i + JANELA_LITERAL] in t
        for corpo in corpos
        for i in range(0, max(1, len(corpo) - JANELA_LITERAL + 1), 10)
    )


def mascarar_govbr(linha: dict[str, Any], govbr: dict[str, str]) -> dict[str, Any]:
    """Troca texto literal de páginas gov.br (CC BY-ND 3.0) por hash e tamanho.

    `govbr` mapeia chunk_id -> texto. Mascara a citação de uma fonte gov.br e qualquer campo
    (resposta, motivo, citação com outro id) que copie 60 caracteres seguidos dessas páginas.
    """
    linha = json.loads(json.dumps(linha))
    usados = [i for i in (t["chunk_id"] for t in linha["saida"]["trechos"]) if i in govbr]
    if not usados:
        return linha
    corpos = [normalizar_texto(govbr[i]) for i in usados]

    def omitir(texto: str) -> str:
        h = hashlib.sha256(texto.encode()).hexdigest()[:12]
        return f"[omitido: página gov.br (CC BY-ND 3.0); sha256 {h}; {len(texto)} caracteres]"

    def mascarar_resposta(r: dict[str, Any] | None) -> None:
        if not isinstance(r, dict):
            return
        for campo in ("resposta", "motivo_recusa"):
            if isinstance(r.get(campo), str) and _tem_trecho_literal(r[campo], corpos):
                r[campo] = omitir(r[campo])
        for f in r.get("fontes", []) or []:
            if not isinstance(f, dict):
                continue
            citado = str(f.get("trecho_citado", ""))
            if str(f.get("id", "")).strip("[] ") in govbr or _tem_trecho_literal(citado, corpos):
                f["trecho_citado"] = omitir(citado)

    mascarar_resposta(linha["saida"]["resposta"])
    for t in linha["saida"]["tentativas"]:
        try:
            bruto = json.loads(t["conteudo"])
        except json.JSONDecodeError:
            t["conteudo"] = omitir(t["conteudo"])
            continue
        mascarar_resposta(bruto)
        t["conteudo"] = json.dumps(bruto, ensure_ascii=False)
    return linha


def _taxa(sel: list[bool]) -> dict[str, Any]:
    n, k = len(sel), sum(sel)
    lo, hi = wilson(k, n)
    return {"k": k, "n": n, "taxa": round(k / n, 3) if n else None, "ic95": [lo, hi]}


def resumir(metricas: list[dict[str, Any]], latencias: list[float]) -> dict[str, Any]:
    def sel(chave: str, tipos: tuple[str, ...] | None = None) -> list[bool]:
        return [
            bool(m[chave])
            for m in metricas
            if m.get(chave) is not None and (tipos is None or m["tipo"] in tipos)
        ]

    lat = sorted(latencias)

    def pct(p: float) -> float | None:
        return round(lat[min(len(lat) - 1, int(round(p * (len(lat) - 1))))], 2) if lat else None

    return {
        "n": len(metricas),
        "json_valido_1a": _taxa(sel("json_valido_1a")),
        "regras_1a": _taxa(sel("regras_1a")),
        "valida_final": _taxa(sel("valida_final")),
        "acuracia": _taxa(sel("acuracia")),
        "citacao_correta": _taxa(sel("citacao_correta")),
        "alucinacao": _taxa(sel("alucinacao")),
        "recusa_correta": _taxa([m["recusou"] for m in metricas if m["tipo"] in NEGATIVOS]),
        "recusa_indevida": _taxa(
            [m["recusou"] for m in metricas if m["tipo"] in (*RESPONDIVEIS, "respondivel")]
        ),
        "citacao_verificavel": _taxa(sel("citacao_verificavel")),
        "recusa_nega_regra": _taxa(sel("recusa_nega_regra")),
        "recusa_dinamicas": _taxa([m["recusou"] for m in metricas if m["tipo"] == "dinamica"]),
        "latencia_p50_s": pct(0.5),
        "latencia_p95_s": pct(0.95),
        "por_tipo": {
            t: {
                "n": sum(m["tipo"] == t for m in metricas),
                "recusou": sum(m["recusou"] for m in metricas if m["tipo"] == t),
                "acuracia": sum(bool(m.get("acuracia")) for m in metricas if m["tipo"] == t),
                "citacao_correta": sum(
                    bool(m.get("citacao_correta")) for m in metricas if m["tipo"] == t
                ),
                "alucinacao": sum(bool(m.get("alucinacao")) for m in metricas if m["tipo"] == t),
            }
            for t in dict.fromkeys(m["tipo"] for m in metricas)
        },
    }
