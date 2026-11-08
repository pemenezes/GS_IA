"""Estrutura hierárquica: transforma blocos extraídos em unidades citáveis.

Unidade = artigo (atos articulados), item numerado (PRODIST/PRORET), pergunta (FAQ) ou seção de
página. O chunking (chunking.py) divide só as unidades que passam do limite de tokens.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from unidecode import unidecode

from src.ingestao.extracao import Bloco, Extracao
from src.ingestao.normalizacao import e_dispositivo_vazio, separar_notas


@dataclass
class Unidade:
    uid: str
    rotulo: str
    hierarquia: list[str]
    linhas: list[str] = field(default_factory=list)
    notas: list[str] = field(default_factory=list)
    tabela: list[list[str]] | None = None
    pagina: int | None = None
    altera_outra_norma: bool = False
    secao: str | None = None


@dataclass
class Estrutura:
    unidades: list[Unidade]
    descartes: list[tuple[str, str]] = field(default_factory=list)


_NIVEL = {
    "PARTE": 1,
    "TÍTULO": 1,
    "TITULO": 1,
    "CAPÍTULO": 2,
    "CAPITULO": 2,
    "SEÇÃO": 3,
    "SECAO": 3,
    "SUBSEÇÃO": 4,
    "SUBSECAO": 4,
}
_CABECALHO_RE = re.compile(
    r"^(PARTE|T[ÍI]TULO|CAP[ÍI]TULO|Se[çc][ãa]o|SE[ÇC][ÃA]O|Subse[çc][ãa]o|SUBSE[ÇC][ÃA]O)\s+"
    r"([IVXLCDM]+|[ÚU]NIC[AO]|\d+)\b\s*[-–.]?\s*(.*)$"
)
_ANEXO_RE = re.compile(r"^ANEXO\b\s*([IVXLCDM]+|\d+|[ÚU]NICO)?\b\s*[-–]?\s*(.*)$")
_ART_RE = re.compile(r"^Art\.?\s*(\d+(?:\.\d+)?)\s*º?\s*(?:-\s*([A-Z]{1,2}))?(?![\w])")
_CLAUSULA_RE = re.compile(r"^CL[ÁA]USULA\s+[\wÀ-ú]+")
_TITULO_ATO_RE = re.compile(r"^(LEI|DECRETO|PORTARIA|RESOLU[ÇC][ÃA]O|MEDIDA PROVIS[ÓO]RIA)\b")
_EMENTA_RE = re.compile(
    r"^(Disp[õo]e|Institui|Altera|Estabelece|Regula|Aprova|Regulamenta|Define|Cria)\b"
)
_NOTA_TOPO_RE = re.compile(r"^(Despacho\s+[\d.]+/\d{4}|Vide:)")
_ALTERA_RE = re.compile(
    r"(passa(?:m)?\s+a\s+vigorar|fica(?:m)?\s+acrescid|passa(?:m)?\s+a\s+ser\s+acrescid)"
    r"|^Art\.\s*\S+\s+(Alterar|Incluir|Acrescentar|Revogar)\b",
    re.IGNORECASE,
)
_ASSINATURA_RE = re.compile(r"^[A-ZÀ-Ú][A-ZÀ-Ú .'-]{5,60}$")
_FIM_ARTICULADO_RE = re.compile(r"^(Bras[íi]lia,|Este texto não substitui)")
_ROTULO_DISP_RE = re.compile(
    r"^(Art\.|§|Par[áa]grafo\s+[úu]nico|[IVXLCDM]+(?:-[A-Z]+)?\s*[-–]|[a-z]\))"
)


def _slug(texto: str) -> str:
    return re.sub(r"[^0-9a-z.]+", "", unidecode(texto.replace("º", "")).lower()).strip(".")


def _e_nome_de_cabecalho(bloco: Bloco) -> bool:
    t = bloco.texto
    return (
        len(t) <= 160
        and not _ROTULO_DISP_RE.match(t)
        and not _CABECALHO_RE.match(t)
        and not _ANEXO_RE.match(t)
        and bloco.tipo != "tabela"
    )


def _ementa(pre: list[Bloco]) -> tuple[Unidade | None, list[Unidade], list[tuple[str, str]]]:
    """Separa título e ementa do preâmbulo; o resto vira descarte."""
    titulo = ementa = None
    notas_topo: list[str] = []
    descartes = []
    for b in pre:
        celulas = [c.strip() for c in b.texto.split(" | ")] if b.tipo == "tabela" else [b.texto]
        usado = False
        for c in celulas:
            limpo, _ = separar_notas(c)
            if not titulo and _TITULO_ATO_RE.match(limpo):
                titulo = re.split(
                    r"\s+(?:OS|O)\s+(?:MINISTROS|MINISTRO|PRESIDENTE|DIRETOR)", limpo
                )[0]
                usado = True
            elif not ementa and _EMENTA_RE.match(limpo):
                ementa, usado = limpo, True
            elif _NOTA_TOPO_RE.match(limpo):
                notas_topo.append(limpo)
                usado = True
        if not usado:
            descartes.append(("preâmbulo/cabeçalho", b.texto))
    unidades = []
    if notas_topo:
        unidades.append(Unidade("notas", "Notas do texto compilado", [], notas_topo))
    if titulo or ementa:
        linhas = [x for x in (titulo, ementa) if x]
        return Unidade("ementa", "Ementa", [], linhas), unidades, descartes
    return None, unidades, descartes


def estruturar_articulado(ex: Extracao) -> Estrutura:
    blocos = ex.blocos
    inicio = next(
        (
            i
            for i, b in enumerate(blocos)
            if _ART_RE.match(b.texto) or (_CABECALHO_RE.match(b.texto) and b.tipo != "tabela")
        ),
        len(blocos),
    )
    ementa, unidades, descartes = _ementa(blocos[:inicio])
    if ementa:
        unidades.insert(0, ementa)

    pilha: list[tuple[int, str]] = []
    atual: Unidade | None = None
    estado = "corpo"
    em_citacao = False
    usados: dict[str, int] = {}
    anexo: str | None = None
    i = inicio

    def nova(uid: str, rotulo: str) -> Unidade:
        n = usados.get(uid, 0)
        usados[uid] = n + 1
        u = Unidade(uid if n == 0 else f"{uid}-{n + 1}", rotulo, [h for _, h in pilha])
        unidades.append(u)
        return u

    while i < len(blocos):
        b = blocos[i]
        texto = b.texto
        i += 1
        if estado == "fim":
            descartes.append(("índice/sumário", texto))
            continue
        if texto.upper() in ("ÍNDICE", "INDICE", "SUMÁRIO"):
            estado = "fim"
            descartes.append(("índice/sumário", texto))
            continue
        m_anexo = _ANEXO_RE.match(texto) if not em_citacao and b.tipo != "tabela" else None
        if m_anexo and (b.tipo == "titulo" or texto.isupper()):
            estado = "anexo"
            anexo = m_anexo.group(1) or "único"
            pilha = [(0, texto)]
            atual = None
            continue
        if estado == "pos":
            descartes.append(("assinatura/nota de publicação", texto))
            continue
        if (
            not em_citacao
            and atual
            and (
                _FIM_ARTICULADO_RE.match(texto)
                or (
                    estado == "corpo"
                    and _ASSINATURA_RE.match(texto)
                    and not _CABECALHO_RE.match(texto)
                )
            )
        ):
            estado = "pos"
            descartes.append(("assinatura/nota de publicação", texto))
            continue

        if b.tipo == "tabela":
            if atual is None or estado == "anexo":
                atual = nova(f"anexo{_slug(anexo or '')}-tabela" if anexo else "tabela", "Tabela")
            if estado == "anexo":
                atual.tabela = b.linhas_tabela
                atual = None
            else:
                atual.linhas.extend(" | ".join(c) for c in b.linhas_tabela)
            continue

        limpo, notas = separar_notas(texto)
        if not em_citacao:
            m_cab = _CABECALHO_RE.match(limpo)
            if m_cab and estado == "corpo":
                tipo = m_cab.group(1).upper()
                nivel = _NIVEL.get(tipo, 3)
                nome = m_cab.group(3)
                if not nome and i < len(blocos) and _e_nome_de_cabecalho(blocos[i]):
                    nome = separar_notas(blocos[i].texto)[0]
                    i += 1
                rotulo = f"{m_cab.group(1)} {m_cab.group(2)}" + (f" – {nome}" if nome else "")
                pilha = [(n, h) for n, h in pilha if n < nivel] + [(nivel, rotulo)]
                atual = None
                continue
            m_art = _ART_RE.match(limpo)
            if m_art:
                if e_dispositivo_vazio(limpo):
                    descartes.append(("dispositivo revogado/vetado", texto))
                    atual = None
                    continue
                base_num = m_art.group(1)
                ordinal = "º" if base_num.isdigit() and int(base_num) < 10 else ""
                num = base_num + (f"-{m_art.group(2)}" if m_art.group(2) else "")
                prefixo = f"anexo{_slug(anexo)}-" if estado == "anexo" and anexo else ""
                rotulo = f"Art. {base_num}{ordinal}" + (
                    f"-{m_art.group(2)}" if m_art.group(2) else ""
                )
                atual = nova(f"{prefixo}art{_slug(num)}", rotulo)
                atual.altera_outra_norma = bool(_ALTERA_RE.search(limpo))
            elif estado == "anexo" and _CLAUSULA_RE.match(limpo):
                atual = nova(
                    f"anexo{_slug(anexo or '')}-{_slug(limpo.split(':')[0])}",
                    limpo.split(":")[0].title(),
                )
            elif e_dispositivo_vazio(limpo):
                descartes.append(("dispositivo revogado/vetado", texto))
                continue
        if atual is None:
            uid = f"anexo{_slug(anexo)}-texto" if estado == "anexo" and anexo else "texto"
            atual = nova(uid, "Texto")
        if limpo:
            atual.linhas.append(limpo)
        atual.notas.extend(notas)
        if b.pagina and atual.pagina is None:
            atual.pagina = b.pagina
        abre = limpo.count("“") + limpo.count("\u201f")
        fecha = limpo.count("”")
        if limpo.startswith(("“", '"')) and fecha < abre:
            em_citacao = True
        elif em_citacao and fecha:
            em_citacao = False
    return Estrutura([u for u in unidades if u.linhas or u.tabela], descartes)


_SECAO_PDF_RE = re.compile(r"^Se[çc][ãa]o\s+(\d+\.\d+)$")
_SECAO_PRORET_RE = re.compile(r"^(\d+)\.\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ ,\-–/]{3,})$")
_ITEM_RE = re.compile(r"^(\d+(?:-[A-Z])?)((?:\.\d+)*)\.\s")
_ANEXO_PDF_RE = re.compile(r"^ANEXO\s+(\d+\.[A-Z])\b")


def estruturar_itens(ex: Extracao) -> Estrutura:
    """PDFs do PRODIST/PRORET: seções e itens numerados."""
    unidades: list[Unidade] = []
    descartes: list[tuple[str, str]] = []
    secao: str | None = None
    hier: list[str] = []
    atual: Unidade | None = None
    usados: dict[str, int] = {}
    blocos = ex.blocos
    cabecalho = []
    i = 0
    while i < len(blocos) and not (
        _SECAO_PDF_RE.match(blocos[i].texto) or _SECAO_PRORET_RE.match(blocos[i].texto)
    ):
        cabecalho.append(blocos[i].texto)
        i += 1
    if cabecalho:
        unidades.append(Unidade("ementa", "Identificação", [], cabecalho[:3], pagina=1))
        descartes += [("cabeçalho do documento", t) for t in cabecalho[3:]]

    def nova(uid: str, rotulo: str, pagina: int | None) -> Unidade:
        n = usados.get(uid, 0)
        usados[uid] = n + 1
        u = Unidade(
            uid if n == 0 else f"{uid}-{n + 1}", rotulo, list(hier), pagina=pagina, secao=secao
        )
        unidades.append(u)
        return u

    while i < len(blocos):
        b = blocos[i]
        t = b.texto
        i += 1
        m_sec = _SECAO_PDF_RE.match(t)
        m_proret = _SECAO_PRORET_RE.match(t)
        m_anexo = _ANEXO_PDF_RE.match(t)
        if m_sec:
            secao = m_sec.group(1)
            nome = blocos[i].texto if i < len(blocos) and blocos[i].tipo == "titulo" else ""
            i += 1 if nome else 0
            hier = [f"Seção {secao}" + (f" – {nome}" if nome else "")]
            atual = None
            continue
        if m_proret:
            secao = m_proret.group(1)
            hier = [f"{secao}. {m_proret.group(2).title()}"]
            atual = None
            continue
        if m_anexo:
            secao = f"anexo-{m_anexo.group(1)}"
            hier = [f"Anexo {m_anexo.group(1)}"]
            atual = None
            continue
        if b.tipo == "tabela":
            m_num = re.match(r"Tabela (\d+)", t)
            uid = f"tabela{m_num.group(1)}" if m_num else "tabela"
            prefixo = _slug(secao) if secao and secao.startswith("anexo") else f"s{secao}"
            u = nova(f"{prefixo}-{uid}" if secao else uid, t or "Tabela", b.pagina)
            u.tabela = b.linhas_tabela
            atual = None
            continue
        if b.tipo == "titulo":
            hier = hier[:1] + [t]
            atual = None
            continue
        m_item = _ITEM_RE.match(t)
        if m_item and not m_item.group(2):
            num = m_item.group(1)
            atual = nova(
                f"s{secao}-item{_slug(num)}" if secao else f"item{_slug(num)}",
                f"Item {num}",
                b.pagina,
            )
        elif atual is None:
            atual = nova(f"s{secao}-texto" if secao else "texto", "Texto", b.pagina)
        atual.linhas.append(t)
    return Estrutura([u for u in unidades if u.linhas or u.tabela], descartes)


def estruturar_govbr(ex: Extracao, pagina: int | None = None) -> Estrutura:
    unidades: list[Unidade] = []
    prefixo = f"p{pagina}-" if pagina else ""
    raiz = [ex.blocos[0].texto] if ex.blocos and ex.blocos[0].tipo == "titulo" else []
    atual: Unidade | None = None
    n_perg = n_sec = 0
    for b in ex.blocos[1 if raiz else 0 :]:
        if b.tipo == "pergunta":
            n_perg += 1
            atual = Unidade(
                f"{prefixo}q{n_perg:02d}", f"Pergunta: {b.texto}", list(raiz), [b.texto]
            )
            unidades.append(atual)
            continue
        if b.tipo == "titulo" and not (atual and atual.uid.startswith(f"{prefixo}q")):
            n_sec += 1
            atual = Unidade(f"{prefixo}s{n_sec:02d}", b.texto, list(raiz), [b.texto])
            unidades.append(atual)
            continue
        if atual is None:
            atual = Unidade(f"{prefixo}s00", "Introdução", list(raiz))
            unidades.append(atual)
        if b.tipo == "tabela":
            if atual.linhas and atual.tabela is None and len(atual.linhas) > 1:
                atual = Unidade(f"{atual.uid}-tabela", f"{atual.rotulo} (tabela)", list(raiz))
                unidades.append(atual)
            atual.tabela = b.linhas_tabela
            continue
        atual.linhas.append(b.texto)
    return Estrutura([u for u in unidades if u.linhas or u.tabela], [])


def aplicar_recorte(doc: dict[str, Any], est: Estrutura) -> Estrutura:
    recorte = doc.get("recorte") or {"tipo": "integral"}
    tipo = recorte["tipo"]
    anexos_fora = tuple(f"anexo{_slug(a)}-" for a in recorte.get("excluir_anexos") or [])
    if tipo == "integral" and not anexos_fora:
        return est
    manter: list[Unidade] = []
    descartes = list(est.descartes)
    for u in est.unidades:
        if anexos_fora and u.uid.startswith(anexos_fora):
            descartes.append(
                ("anexo excluído do recorte", f"{u.rotulo}: {' '.join(u.linhas)[:80]}")
            )
            continue
        if tipo == "integral" or u.uid in ("ementa", "notas"):
            ok = True
        elif tipo == "titulo":
            alvo = recorte["titulo"]
            ok = bool(u.hierarquia) and bool(
                re.match(rf"^T[ÍI]TULO\s+{alvo}\b(?![IVXLC])", u.hierarquia[0])
            )
        elif tipo == "dispositivos_proprios":
            # Texto fora de artigo, num ato que altera outros, é conteúdo inserido em outra norma.
            ok = u.uid.startswith("art") and not u.altera_outra_norma
        elif tipo == "secoes":
            ok = u.secao in (recorte.get("secoes") or [])
        else:
            raise ValueError(f"recorte desconhecido: {tipo}")
        if ok:
            manter.append(u)
        else:
            descartes.append(
                (f"fora do recorte ({tipo})", f"{u.rotulo}: {' '.join(u.linhas)[:80]}")
            )
    return Estrutura(manter, descartes)


def estruturar(doc: dict[str, Any], ex: Extracao, pagina: int | None = None) -> Estrutura:
    if doc["extrator"] == "govbr":
        est = estruturar_govbr(ex, pagina)
    elif doc["extrator"] == "pdf" and sum(bool(_ART_RE.match(b.texto)) for b in ex.blocos) < 2:
        est = estruturar_itens(ex)
    else:
        est = estruturar_articulado(ex)
    est.descartes = ex.descartes + est.descartes
    return aplicar_recorte(doc, est)
