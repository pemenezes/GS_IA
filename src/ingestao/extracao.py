"""Extração de texto dos originais (HTML do Planalto e da ANEEL, PDF, páginas gov.br).

A saída é uma lista de blocos em ordem de leitura, já sem texto revogado (tachado). Nenhum texto é
reescrito: só limpeza de marcação, espaços e numeração ordinal.
"""

from __future__ import annotations

import collections
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf
from bs4 import BeautifulSoup, Tag

from src.ingestao.normalizacao import normalizar, separar_notas


@dataclass
class Bloco:
    texto: str
    tipo: str = "texto"  # texto | titulo | pergunta | tabela
    pagina: int | None = None
    linhas_tabela: list[list[str]] = field(default_factory=list)


@dataclass
class Extracao:
    blocos: list[Bloco]
    descartes: list[tuple[str, str]] = field(default_factory=list)
    metadados: dict[str, str] = field(default_factory=dict)


def _decodificar(dados: bytes) -> str:
    cabeca = dados[:4000].decode("ascii", "ignore").lower()
    m = re.search(r"charset=[\"']?([\w-]+)", cabeca)
    if m:
        try:
            return dados.decode(m.group(1))
        except (LookupError, UnicodeDecodeError):
            pass
    try:
        return dados.decode("utf-8")
    except UnicodeDecodeError:
        return dados.decode("cp1252")


def remover_revogados(soup: BeautifulSoup) -> int:
    """Remove o texto tachado (redação revogada) e devolve quantos elementos saíram."""
    alvos = list(soup.find_all(["strike", "s", "del"]))
    alvos += [
        el
        for el in soup.find_all(style=True)
        if "line-through" in el["style"].replace(" ", "").lower()
    ]
    removidos = 0
    for el in alvos:
        if not el.decomposed:
            el.decompose()
            removidos += 1
    return removidos


def trechos_tachados(dados: bytes, minimo: int = 60) -> list[str]:
    """Trechos tachados de um HTML que não reaparecem no texto vigente (para conferência)."""
    soup = BeautifulSoup(_decodificar(dados), "lxml")
    _ordinais_em_sobrescrito(soup)
    tachados = list(soup.find_all(["strike", "s", "del"])) + [
        el
        for el in soup.find_all(style=True)
        if "line-through" in el["style"].replace(" ", "").lower()
    ]
    textos = {separar_notas(_texto(el))[0] for el in tachados}
    remover_revogados(soup)
    vigente = normalizar(soup.get_text(" "))
    return sorted(t for t in textos if len(t) >= minimo and t not in vigente)


def _ordinais_em_sobrescrito(soup: BeautifulSoup) -> None:
    for el in soup.find_all(["sup", "u"]):
        conteudo = el.get_text(strip=True)
        if conteudo in ("o", "º", "°"):
            el.replace_with("º")
        elif conteudo in ("a", "ª"):
            el.replace_with("ª")


def _texto(el: Tag) -> str:
    return normalizar(el.get_text(" "))


def _linhas_tabela(tabela: Tag) -> list[list[str]]:
    linhas = []
    for tr in tabela.find_all("tr"):
        celulas = [separar_notas(_texto(c))[0] for c in tr.find_all(["td", "th"])]
        if any(celulas):
            linhas.append(celulas)
    return linhas


def extrair_html_ato(dados: bytes) -> Extracao:
    """HTML de atos oficiais (Planalto e ANEEL cedoc): um bloco por parágrafo ou tabela."""
    soup = BeautifulSoup(_decodificar(dados), "lxml")
    n_revogados = remover_revogados(soup)
    _ordinais_em_sobrescrito(soup)
    blocos: list[Bloco] = []
    for el in soup.find_all(["p", "h1", "h2", "h3", "h4", "table"]):
        if el.find_parent("table"):
            continue
        if el.name == "table":
            linhas = _linhas_tabela(el)
            if linhas:
                texto = "\n".join(" | ".join(c) for c in linhas)
                blocos.append(Bloco(texto, "tabela", linhas_tabela=linhas))
            continue
        if el.find(["p", "table"]):
            continue
        texto = _texto(el)
        if not texto or (blocos and blocos[-1].texto == texto):
            continue
        tipo = "titulo" if el.name in ("h1", "h2", "h3", "h4") else "texto"
        blocos.append(Bloco(texto, tipo))
    return Extracao(blocos, metadados={"elementos_revogados_removidos": str(n_revogados)})


# --- PDF -----------------------------------------------------------------------------------------

_INICIO_PARAGRAFO_PDF = re.compile(
    r"^(?:"
    r"\d+(?:-[A-Z])?(?:\.\d+)*\.\s"  # item numerado: 13. / 13.1. / 220-A.
    r"|[A-Z]\.\s"  # alínea do PRORET: A.
    r"|Se[çc][ãa]o\s+\d+\.\d+\b"  # Seção 8.2
    r"|ANEXO\s+\d+\.[A-Z]\b"  # ANEXO 8.B
    r"|Art\.\s*\d+"
    r"|§\s*\d+"
    r"|Par[áa]grafo\s+[úu]nico"
    r"|[IVXLC]+\s*[-–]\s"
    r"|[a-z]\)\s"
    r"|“"
    r")"
)
_FIM_FRASE = (".", ":", ";", "?", "!", "”", '"')


def _linhas_repetidas(paginas: list[list[str]]) -> set[str]:
    contagem = collections.Counter(linha for pag in paginas for linha in set(pag))
    limite = max(3, int(len(paginas) * 0.4))
    return {linha for linha, n in contagem.items() if n >= limite}


def _e_subtitulo(
    linha: str, anterior: str | None, proxima: str | None, anterior_titulo: bool = False
) -> bool:
    if len(linha) > 90 or linha.endswith(_FIM_FRASE) or linha.endswith(","):
        return False
    if not linha[0].isupper() or _INICIO_PARAGRAFO_PDF.match(linha):
        return False
    if re.search(r"[=×∑+<>≤≥%/]", linha) or not re.search(r"[a-zà-ú]{3,}", linha):
        return False
    anterior_fechou = (
        anterior is None
        or anterior_titulo
        or anterior.endswith(_FIM_FRASE)
        or anterior.endswith(":")
    )
    proxima_abre = (
        proxima is None or bool(_INICIO_PARAGRAFO_PDF.match(proxima)) or (proxima[:1].isupper())
    )
    return anterior_fechou and proxima_abre


def _celula_pdf(texto: str | None) -> str:
    texto = re.sub(r"(\w)\n(\w)\b", r"\1\2", texto or "")
    return normalizar(texto.replace("\n", " "))


def _tabelas_da_pagina(dados: bytes, numero: int) -> list[Bloco]:
    """Tabelas de uma página (pdfplumber), com a legenda "Tabela N – ..." logo acima de cada uma."""
    import io

    import pdfplumber

    blocos: list[Bloco] = []
    with pdfplumber.open(io.BytesIO(dados)) as pdf:
        pag = pdf.pages[numero - 1]
        for t in pag.find_tables():
            linhas = [[_celula_pdf(c) for c in linha] for linha in t.extract()]
            linhas = [linha for linha in linhas if any(linha)]
            acima = pag.crop((0, max(0, t.bbox[1] - 45), pag.width, t.bbox[1])).extract_text()
            m = re.search(r"Tabela \d+ – .*", (acima or "").replace("\n", " "), re.S)
            legenda = normalizar(m.group(0)) if m else ""
            blocos.append(Bloco(legenda, "tabela", numero, linhas_tabela=linhas))
    return blocos


def extrair_pdf(dados: bytes, paginas_tabela: list[int] | None = None) -> Extracao:
    """PDF: junta as linhas em parágrafos pelos marcadores de item e reconhece subtítulos.

    Páginas em `paginas_tabela` são lidas como tabelas (pdfplumber), não como texto corrido.
    """
    doc = pymupdf.open(stream=dados, filetype="pdf")
    paginas_tabela = paginas_tabela or []
    paginas = [
        [normalizar(linha) for linha in p.get_text().splitlines() if normalizar(linha)] for p in doc
    ]
    tabelas_por_pagina = {n: _tabelas_da_pagina(dados, n) for n in paginas_tabela}
    for n in paginas_tabela:
        paginas[n - 1] = [
            linha for linha in paginas[n - 1] if re.match(r"ANEXO\s+\d+\.[A-Z]\b", linha)
        ]
    repetidas = _linhas_repetidas(paginas)
    descartes: list[tuple[str, str]] = [("cabeçalho/rodapé repetido", r) for r in repetidas]
    linhas = [
        (n, linha)
        for n, pag in enumerate(paginas, start=1)
        for linha in pag
        if linha not in repetidas and not re.fullmatch(r"\d{1,3}", linha)
    ]
    blocos: list[Bloco] = []
    atual: list[str] = []
    pagina_atual = 1

    def fechar() -> None:
        if atual:
            texto = " ".join(atual)
            texto = re.sub(r"(\w)- (\w)", r"\1-\2", texto)
            blocos.append(Bloco(normalizar(texto), "texto", pagina_atual))
            atual.clear()

    anterior_titulo = False
    pendentes = dict(tabelas_por_pagina)

    def inserir_tabelas_ate(pagina: int) -> None:
        for n in sorted(p for p in pendentes if p <= pagina):
            fechar()
            for t in pendentes.pop(n):
                anterior_tab = blocos[-1] if blocos and blocos[-1].tipo == "tabela" else None
                continua = (
                    anterior_tab is not None
                    and not t.texto
                    and len(t.linhas_tabela[0]) == len(anterior_tab.linhas_tabela[0])
                )
                if continua:
                    anterior_tab.linhas_tabela.extend(t.linhas_tabela)
                else:
                    blocos.append(t)

    for i, (pag, linha) in enumerate(linhas):
        if pendentes and min(pendentes) < pag:
            inserir_tabelas_ate(pag - 1)
        anterior = linhas[i - 1][1] if i else None
        proxima = linhas[i + 1][1] if i + 1 < len(linhas) else None
        if re.fullmatch(r"Se[çc][ãa]o\s+\d+\.\d+", linha) or _e_subtitulo(
            linha, anterior, proxima, anterior_titulo
        ):
            fechar()
            blocos.append(Bloco(linha, "titulo", pag))
            anterior_titulo = True
            continue
        anterior_titulo = False
        if _INICIO_PARAGRAFO_PDF.match(linha) or not atual:
            fechar()
            pagina_atual = pag
        atual.append(linha)
        if pendentes and pag in pendentes and (i + 1 == len(linhas) or linhas[i + 1][0] > pag):
            inserir_tabelas_ate(pag)
    fechar()
    inserir_tabelas_ate(len(paginas))
    return Extracao(blocos, descartes, {"paginas": str(len(paginas))})


# --- Páginas gov.br ------------------------------------------------------------------------------

_RUIDO_GOVBR = re.compile(
    r"^(?:Publicado em|Modificado (?:em|há)|Compartilhe|Imprimir|Vídeo educativo|Podcast|"
    r"Copiar para área de transferência|Link para Copiar)",
    re.IGNORECASE,
)


def _carregar_volto(html: str) -> dict | None:
    marca = "window.__data="
    if marca not in html:
        return None
    resto = html[html.index(marca) + len(marca) :]
    resto = re.sub(r"(?<=[:\[,])undefined(?=[,\]}])", "null", resto)
    try:
        return json.JSONDecoder().raw_decode(resto)[0]
    except json.JSONDecodeError:
        return None


def _texto_slate(nos: list) -> str:
    partes = []
    for no in nos or []:
        if "text" in no:
            partes.append(no["text"])
        else:
            partes.append(_texto_slate(no.get("children", [])))
    return "".join(partes)


def _blocos_slate(valor: list) -> list[Bloco]:
    blocos = []
    for no in valor or []:
        tipo = no.get("type", "p")
        if tipo in ("ul", "ol"):
            blocos += [Bloco(normalizar(_texto_slate([li])), "texto") for li in no["children"]]
        else:
            rotulo = "titulo" if tipo in ("h1", "h2", "h3", "h4") else "texto"
            blocos.append(Bloco(normalizar(_texto_slate([no])), rotulo))
    return [b for b in blocos if b.texto]


def _blocos_html_fragmento(html: str) -> list[Bloco]:
    soup = BeautifulSoup(html, "lxml")
    blocos = []
    for el in soup.find_all(["h2", "h3", "h4", "p", "li", "table"]):
        if el.name == "table":
            linhas = _linhas_tabela(el)
            if linhas:
                blocos.append(
                    Bloco("\n".join(" | ".join(c) for c in linhas), "tabela", linhas_tabela=linhas)
                )
            continue
        if el.find_parent("table") or (el.name in ("p", "li") and el.find(["p", "li"])):
            continue
        texto = _texto(el)
        if texto:
            blocos.append(Bloco(texto, "titulo" if el.name.startswith("h") else "texto"))
    return blocos


def _percorrer_volto(no: dict) -> list[Bloco]:
    """Percorre os blocos do Volto na ordem de `blocks_layout`."""
    blocos: list[Bloco] = []
    filhos = no.get("blocks") or {}
    for bid in (no.get("blocks_layout") or {}).get("items", []):
        b = filhos.get(bid) or {}
        tipo = b.get("@type")
        if tipo == "accordionPanel":
            blocos.append(Bloco(normalizar(b.get("title") or ""), "pergunta"))
            blocos += _percorrer_volto(b)
        elif tipo == "html":
            blocos += _blocos_html_fragmento(b.get("html") or "")
        elif tipo == "slate":
            blocos += _blocos_slate(b.get("value"))
        elif tipo == "slateTable":
            linhas = [
                [normalizar(_texto_slate(c.get("value"))) for c in linha.get("cells", [])]
                for linha in (b.get("table") or {}).get("rows", [])
            ]
            linhas = [linha for linha in linhas if any(linha)]
            if linhas:
                blocos.append(
                    Bloco("\n".join(" | ".join(c) for c in linhas), "tabela", linhas_tabela=linhas)
                )
        elif tipo == "SectionTitleBlock" and isinstance(b.get("title"), str):
            blocos.append(Bloco(normalizar(b["title"]), "titulo"))
        elif isinstance(b.get("data"), dict) and "blocks" in b["data"]:
            blocos += _percorrer_volto(b["data"])
        elif "blocks" in b and "blocks_layout" in b:
            blocos += _percorrer_volto(b)
    return [b for b in blocos if b.texto]


def extrair_govbr(dados: bytes) -> Extracao:
    """Páginas do gov.br: Volto (ANEEL, conteúdo lido do JSON embutido) ou Plone (MME)."""
    html = _decodificar(dados)
    volto = _carregar_volto(html)
    if volto and isinstance((volto.get("content") or {}).get("data"), dict):
        conteudo = volto["content"]["data"]
        blocos = [Bloco(normalizar(conteudo.get("title") or ""), "titulo")]
        if conteudo.get("description"):
            blocos.append(Bloco(normalizar(conteudo["description"]), "texto"))
        blocos += _percorrer_volto(conteudo)
        metadados = {
            k: conteudo[c]
            for k, c in (("publicado_em", "created"), ("modificado_em", "modified"))
            if conteudo.get(c)
        }
        return Extracao([b for b in blocos if b.texto], [], metadados)

    soup = BeautifulSoup(html, "lxml")
    texto_pagina = soup.get_text(" ", strip=True)
    metadados = {}
    for chave, padrao in (
        ("publicado_em", r"Publicado em ([\d/]+ [\d:]+)"),
        ("modificado_em", r"Modificado (em [\d/]+ [\d:]+|há [^\s]+ \w+)"),
    ):
        m = re.search(padrao, texto_pagina)
        if m:
            metadados[chave] = m.group(1)
    area = (
        soup.find(class_="content-area")
        or soup.find(id="content-core")
        or soup.find(id="main-content")
        or soup.body
    )
    blocos: list[Bloco] = []
    descartes: list[tuple[str, str]] = []
    for el in area.find_all(["h1", "h2", "h3", "h4", "p", "li", "summary", "div", "table"]):
        e_pergunta = el.name == "summary" or "accordion-title" in (el.get("class") or [])
        if el.name == "div" and not e_pergunta:
            continue
        if el.name == "table":
            linhas = _linhas_tabela(el)
            if linhas:
                blocos.append(
                    Bloco("\n".join(" | ".join(c) for c in linhas), "tabela", linhas_tabela=linhas)
                )
            continue
        if el.find_parent("table") or (el.name in ("p", "li") and el.find(["p", "li"])):
            continue
        texto = _texto(el)
        if not texto or (blocos and blocos[-1].texto == texto):
            continue
        if _RUIDO_GOVBR.match(texto):
            descartes.append(("ruído de página", texto))
            continue
        tipo = "pergunta" if e_pergunta else ("titulo" if el.name.startswith("h") else "texto")
        blocos.append(Bloco(texto, tipo))
    return Extracao(blocos, descartes, metadados)


EXTRATORES = {
    "planalto": extrair_html_ato,
    "aneel": extrair_html_ato,
    "pdf": extrair_pdf,
    "govbr": extrair_govbr,
}


def extrair_arquivo(doc: dict, dados: bytes) -> Extracao:
    """Extrai um original aplicando as opções do manifesto (ex.: páginas lidas como tabela)."""
    if doc["extrator"] == "pdf":
        return extrair_pdf(dados, doc.get("tabelas_pdf"))
    return EXTRATORES[doc["extrator"]](dados)


def extrair(extrator: str, arquivos: list[Path]) -> Extracao:
    partes = [EXTRATORES[extrator](arq.read_bytes()) for arq in arquivos]
    total = Extracao(
        [b for p in partes for b in p.blocos], [d for p in partes for d in p.descartes]
    )
    for p in partes:
        for k, v in p.metadados.items():
            total.metadados.setdefault(k, v)
    return total
