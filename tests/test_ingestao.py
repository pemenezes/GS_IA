"""Testes da ingestão. Unitários usam textos fictícios; os de integridade leem a base gerada."""

import csv
import hashlib
import json

import pymupdf
import pytest
from bs4 import BeautifulSoup

from src.ingestao import base, download
from src.ingestao.chunking import Parametros, chunks_da_unidade
from src.ingestao.estrutura import Unidade, aplicar_recorte, estruturar, estruturar_articulado
from src.ingestao.extracao import (
    extrair_govbr,
    extrair_html_ato,
    extrair_pdf,
    remover_revogados,
    trechos_tachados,
)
from src.ingestao.normalizacao import e_dispositivo_vazio, normalizar, separar_notas

LEI_FICTICIA = """<html><body>
<p>Presidência da República</p>
<p>LEI Nº 99.999, DE 1º DE JANEIRO DE 2099</p>
<p>Dispõe sobre regras de teste do exemplo.</p>
<p>O PRESIDENTE DA REPÚBLICA Faço saber que o Congresso Nacional decreta:</p>
<p>TÍTULO I</p><p>DAS REGRAS DE TESTE</p>
<p>CAPÍTULO I</p><p>Disposições Gerais</p>
<p>Art. 1<sup>o</sup> O exemplo vale para testes.</p>
<p><strike>I - regra antiga de teste revogada;</strike></p>
<p>I - regra nova de teste; (Redação dada pela Lei nº 88.888, de 2098)</p>
<p>II - (revogado);</p>
<p>§ 1º O parágrafo de teste complementa o artigo.</p>
<p><span style="text-decoration: line-through">§ 2º Parágrafo antigo tachado.</span></p>
<p>Art. 2º A Lei de Exemplo passa a vigorar com as seguintes alterações:</p>
<p>“Art. 7º Texto citado de outra lei.</p>
<p>Art. 8º Outro texto citado.” (NR)</p>
<p>Art. 3º (VETADO)</p>
<p>Art. 4º Esta Lei entra em vigor na data de sua publicação.</p>
<p>Brasília, 1º de janeiro de 2099.</p>
<p>FULANO DE TAL</p>
</body></html>"""


class TokFalso:
    """Conta palavras como tokens: suficiente para testar o chunking sem baixar modelos."""

    def contar(self, texto: str) -> int:
        return len(texto.split())


# --- normalização --------------------------------------------------------------------------------


def test_normalizar_ordinais_e_espacos():
    assert normalizar("Art. 1°  da Lei n o 10.438\xa0e  §2") == "Art. 1º da Lei nº 10.438 e § 2"
    assert normalizar("Leis n os 9.991 e 10.925") == "Leis nºs 9.991 e 10.925"


def test_separar_notas_de_redacao():
    texto, notas = separar_notas(
        "I - regra nova; (Redação dada pela Lei nº 1, de 2000) (Vig ência encerrada)"
    )
    assert texto == "I - regra nova;"
    assert len(notas) == 2


@pytest.mark.parametrize(
    ("texto", "vazio"),
    [
        ("II - (revogado);", True),
        ("§ 2º", True),
        ("Art. 3º (VETADO)", True),
        ("Parágrafo único.", True),
        ("I - regra de teste;", False),
        ("Art. 4º Texto.", False),
    ],
)
def test_dispositivo_vazio(texto, vazio):
    assert e_dispositivo_vazio(texto) is vazio


# --- extração ------------------------------------------------------------------------------------


def test_remove_texto_tachado():
    soup = BeautifulSoup(LEI_FICTICIA, "lxml")
    assert remover_revogados(soup) == 2
    texto = soup.get_text()
    assert "regra antiga" not in texto and "Parágrafo antigo" not in texto
    assert "regra nova" in texto


def test_articulado_ficticio():
    est = estruturar_articulado(extrair_html_ato(LEI_FICTICIA.encode("utf-8")))
    por_id = {u.uid: u for u in est.unidades}
    assert list(por_id) == ["ementa", "art1", "art2", "art4"]
    assert por_id["ementa"].linhas == [
        "LEI Nº 99.999, DE 1º DE JANEIRO DE 2099",
        "Dispõe sobre regras de teste do exemplo.",
    ]
    art1 = por_id["art1"]
    assert art1.rotulo == "Art. 1º"
    assert art1.hierarquia == ["TÍTULO I – DAS REGRAS DE TESTE", "CAPÍTULO I – Disposições Gerais"]
    assert art1.linhas == [
        "Art. 1º O exemplo vale para testes.",
        "I - regra nova de teste;",
        "§ 1º O parágrafo de teste complementa o artigo.",
    ]
    assert art1.notas == ["(Redação dada pela Lei nº 88.888, de 2098)"]
    assert por_id["art2"].altera_outra_norma
    assert len(por_id["art2"].linhas) == 3, "artigos citados entre aspas ficam no Art. 2º"
    motivos = {m for m, _ in est.descartes}
    assert {"dispositivo revogado/vetado", "assinatura/nota de publicação"} <= motivos


def test_recorte_dispositivos_proprios():
    est = estruturar_articulado(extrair_html_ato(LEI_FICTICIA.encode("utf-8")))
    doc = {"recorte": {"tipo": "dispositivos_proprios"}}
    assert [u.uid for u in aplicar_recorte(doc, est).unidades] == ["ementa", "art1", "art4"]


def _pdf_ficticio() -> bytes:
    doc = pymupdf.open()
    paginas = [
        [
            "Cabeçalho repetido de teste",
            "Seção 1.1",
            "Assunto de Teste",
            "1. Primeiro item de teste que continua",
            "na linha seguinte.",
            "1.1. Subitem do teste.",
        ],
        ["Cabeçalho repetido de teste", "2. Segundo item de teste."],
        ["Cabeçalho repetido de teste", "3. Terceiro item de teste."],
    ]
    for linhas in paginas:
        pag = doc.new_page()
        for i, linha in enumerate(linhas):
            pag.insert_text((72, 72 + 18 * i), linha)
    return doc.tobytes()


def test_pdf_remove_cabecalho_repetido_e_agrupa_itens():
    ex = extrair_pdf(_pdf_ficticio())
    textos = [b.texto for b in ex.blocos]
    assert "Cabeçalho repetido de teste" not in textos
    assert "1. Primeiro item de teste que continua na linha seguinte." in textos
    est = estruturar({"extrator": "pdf", "recorte": {"tipo": "integral"}}, ex)
    itens = {u.uid: u for u in est.unidades}
    assert itens["s1.1-item1"].hierarquia == ["Seção 1.1 – Assunto de Teste"]
    assert itens["s1.1-item1"].linhas[-1] == "1.1. Subitem do teste."


def test_govbr_volto_le_sanfona_do_json():
    dados = {
        "content": {
            "data": {
                "title": "Página de teste",
                "modified": "2099-01-01T00:00:00+00:00",
                "blocks_layout": {"items": ["a"]},
                "blocks": {
                    "a": {
                        "@type": "accordion",
                        "data": {
                            "blocks_layout": {"items": ["p1"]},
                            "blocks": {
                                "p1": {
                                    "@type": "accordionPanel",
                                    "title": "Pergunta de teste?",
                                    "blocks_layout": {"items": ["h"]},
                                    "blocks": {
                                        "h": {"@type": "html", "html": "<p>Resposta de teste.</p>"}
                                    },
                                }
                            },
                        },
                    }
                },
            }
        }
    }
    html = f"<html><script>window.__data={json.dumps(dados)}</script></html>"
    ex = extrair_govbr(html.encode("utf-8"))
    assert [(b.tipo, b.texto) for b in ex.blocos] == [
        ("titulo", "Página de teste"),
        ("pergunta", "Pergunta de teste?"),
        ("texto", "Resposta de teste."),
    ]
    assert ex.metadados["modificado_em"].startswith("2099-01-01")


def test_resolver_link_versao_vigente():
    html = (
        '<p>Módulo 8 - Qualidade: <a href=\\"https:\\u002F\\u002Fx\\u002Fm8_v14.pdf\\">'
        'versão vigente</a> | <a href=\\"y\\">todas as versões</a></p>'
    )
    assert download.resolver_versao_vigente(html, "Módulo 8") == "https://x/m8_v14.pdf"


# --- chunking ------------------------------------------------------------------------------------


def test_chunking_respeita_limites_e_sobreposicao():
    p = Parametros(alvo=30, minimo=5, maximo=40, sobreposicao=6)
    linhas = [f"Linha {i} " + "palavra " * 8 for i in range(10)]
    u = Unidade("art9", "Art. 9º", ["TÍTULO I"], linhas)
    partes = chunks_da_unidade("Lei Teste", u, TokFalso(), p)
    assert len(partes) > 1
    assert [s for s, _, _ in partes] == [f"-p{k}" for k in range(1, len(partes) + 1)]
    for _, texto, _ in partes:
        assert texto.startswith("Lei Teste > TÍTULO I > Art. 9º\n")
        assert TokFalso().contar(texto) <= p.maximo
    corpo = "\n".join(t for _, t, _ in partes)
    assert all(linha in corpo for linha in linhas), "nenhuma linha se perde"


def test_continuacao_repete_dispositivo_pai():
    p = Parametros(alvo=25, minimo=1, maximo=60, sobreposicao=8)
    linhas = ["Art. 5º O caput de teste.", "§ 1º O parágrafo que introduz os incisos de teste:"]
    linhas += [
        f"{r} - inciso de teste numero {i} com texto;"
        for i, r in enumerate(["I", "II", "III", "IV", "V", "VI"], start=1)
    ]
    partes = chunks_da_unidade("Lei", Unidade("art5", "Art. 5º", [], linhas), TokFalso(), p)
    assert len(partes) > 1
    for _, texto, _ in partes[1:]:
        corpo = texto.split("\n")[1:]
        if not corpo[0].startswith(("Art.", "§")):
            raise AssertionError(f"continuação sem contexto: {corpo[0]}")
        assert corpo[0].startswith("§ 1º O parágrafo")


def test_tabela_repete_cabecalho_so_quando_existe():
    p = Parametros(alvo=20, minimo=1, maximo=40, sobreposicao=0)
    com = Unidade("t", "Tabela", [], [], tabela=[["Tipo", "Prazo"]] + [["1", "5 dias"]] * 12)
    for _, texto, tabela in chunks_da_unidade("Doc", com, TokFalso(), p):
        assert tabela and texto.split("\n")[1] == "Tipo | Prazo"
    sem = Unidade(
        "t", "Tabela", [], [], tabela=[[f"Cooperativa {i}, telefone 0800 {i}"] for i in range(12)]
    )
    textos = [t for _, t, _ in chunks_da_unidade("Doc", sem, TokFalso(), p)]
    assert sum(t.count("Cooperativa 0,") for t in textos) == 1


# --- integridade da base gerada ------------------------------------------------------------------

sem_base = pytest.mark.skipif(not base.CHUNKS.exists(), reason="base ainda não gerada")


@pytest.fixture(scope="module")
def chunks_versionados():
    return base.carregar_chunks(incluir_locais=False)


@sem_base
def test_trechos_validos(chunks_versionados):
    obrigatorios = [
        "chunk_id",
        "doc_id",
        "fonte",
        "url",
        "artigo",
        "data_consulta",
        "vigencia",
        "licenca",
        "sha256_doc",
        "n_tokens",
        "texto",
    ]
    ids = [c["chunk_id"] for c in chunks_versionados]
    assert len(ids) == len(set(ids))
    for c in chunks_versionados:
        assert all(c.get(k) not in (None, "") for k in obrigatorios), c["chunk_id"]
        assert c["texto"].strip()
        assert c["n_tokens"] <= 400


@sem_base
def test_trava_de_licenca(chunks_versionados):
    manifesto = download.carregar_manifesto()
    proibidos = {d["id"] for d in manifesto["documentos"] if not d["versionar_texto"]}
    assert not [c for c in chunks_versionados if c["doc_id"] in proibidos or not c["versionado"]]


@sem_base
def test_fontes_csv_confere_com_originais_e_trechos(chunks_versionados):
    with open(base.FONTES, encoding="utf-8") as f:
        fontes = {linha["id"]: linha for linha in csv.DictReader(f)}
    manifesto = download.carregar_manifesto()
    assert set(fontes) == {d["id"] for d in manifesto["documentos"]}
    contagem = {}
    for c in chunks_versionados:
        contagem[c["doc_id"]] = contagem.get(c["doc_id"], 0) + 1
    for doc in manifesto["documentos"]:
        if not doc["versionar_texto"]:
            continue
        linha = fontes[doc["id"]]
        assert int(linha["n_trechos"]) == contagem[doc["id"]]
        for arq, reg in base.arquivos_do_documento(doc):
            assert hashlib.sha256(arq.read_bytes()).hexdigest() == reg["sha256"]
            assert reg["sha256"] in linha["sha256"]


@sem_base
def test_texto_tachado_dos_originais_nao_entra_na_base(chunks_versionados):
    manifesto = download.carregar_manifesto()
    por_doc: dict[str, str] = {}
    for c in chunks_versionados:
        por_doc[c["doc_id"]] = por_doc.get(c["doc_id"], "") + "\n" + c["texto"]
    verificados = 0
    for doc in manifesto["documentos"]:
        if doc["formato"] != "HTML" or not doc["versionar_texto"]:
            continue
        for arq, _ in base.arquivos_do_documento(doc):
            for trecho in trechos_tachados(arq.read_bytes()):
                assert trecho not in por_doc.get(doc["id"], ""), (doc["id"], trecho[:80])
                verificados += 1
    assert verificados > 50
