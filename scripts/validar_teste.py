"""Verificação automática do conjunto de teste (Fase 3).

  1. schema e ids únicos;
  2. composição exata por tipo;
  3. trechos gold existem na base; trecho gov.br só junto de um ato oficial (salvo se o fato só
     existir na página);
  4. cada fato-chave é cópia literal de um trecho gold; no multi-trecho, 2+ trechos contribuem;
  5. fatos proibidos não estão nos trechos gold e estão em texto oficial revogado (tachado nos
     originais ou trecho com alerta de revogação);
  6. "não consta": nenhum trecho contém todos os termos da pergunta (heurística BM25 + revisão);
  7. nenhum grupo dividido entre dev e test (quando o split existe);
  + registros-âncora das dinâmicas documentados em docs/dados_simulados.md.

Uso:  python scripts/validar_teste.py [arquivo.jsonl]   (padrão: teste_candidatas.jsonl)
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.avaliacao.casos import CANDIDATAS, COMPOSICAO, carregar  # noqa: E402
from src.config import RAIZ  # noqa: E402
from src.ingestao import base, download  # noqa: E402
from src.ingestao.extracao import trechos_tachados  # noqa: E402
from src.ingestao.normalizacao import normalizar  # noqa: E402
from src.rag.lexico import tokenizar  # noqa: E402

DADOS_SIMULADOS = RAIZ / "docs" / "dados_simulados.md"


def _textos_revogados() -> list[str]:
    textos = []
    for doc in download.carregar_manifesto()["documentos"]:
        if doc["formato"] == "HTML" and doc["versionar_texto"]:
            for arq, _ in base.arquivos_do_documento(doc):
                textos += trechos_tachados(arq.read_bytes(), minimo=10)
    return textos


def validar(caminho: Path) -> list[str]:
    erros: list[str] = []
    casos = carregar(caminho)
    chunks = {c["chunk_id"]: c for c in base.carregar_chunks()}

    ids = Counter(c.id for c in casos)
    erros += [f"[1] id repetido: {i}" for i, n in ids.items() if n > 1]
    comp = Counter(c.tipo for c in casos)
    if dict(comp) != COMPOSICAO:
        erros.append(f"[2] composição {dict(comp)} != {COMPOSICAO}")

    revogados = None
    alertas = " ".join(c["texto"] for c in chunks.values() if c.get("alerta"))
    for c in casos:
        faltando = [g for g in c.gold_v2 if g not in chunks]
        if faltando:
            erros.append(f"[3] {c.id}: trechos gold inexistentes {faltando}")
            continue
        golds = [chunks[g] for g in c.chunk_ids_gold]
        if golds and all(not g["versionado"] for g in golds):
            erros.append(f"[3] {c.id}: só há gold de página gov.br (exige um ato oficial junto)")
        textos = [normalizar(g["texto"]) for g in golds]
        for f in c.fatos_chave:
            if not any(normalizar(f) in t for t in textos):
                erros.append(f"[4] {c.id}: fato-chave não literal nos gold: {f!r}")
        if c.tipo == "multi_trecho":
            contribuem = sum(any(normalizar(f) in t for f in c.fatos_chave) for t in textos)
            if contribuem < 2:
                erros.append(f"[4] {c.id}: multi-trecho com só {contribuem} trecho contribuindo")
        for f in c.fatos_proibidos:
            if any(normalizar(f) in t for t in textos):
                erros.append(f"[5] {c.id}: fato proibido aparece no gold: {f!r}")
            if revogados is None:
                revogados = " ".join(_textos_revogados())
            if normalizar(f) not in revogados and normalizar(f) not in alertas:
                erros.append(f"[5] {c.id}: fato proibido não está em texto revogado: {f!r}")
        if c.tipo == "nao_consta":
            termos = set(tokenizar(c.pergunta))
            for ch in chunks.values():
                if termos and termos <= set(tokenizar(ch["texto"])):
                    erros.append(f"[6] {c.id}: {ch['chunk_id']} contém todos os termos {termos}")
                    break

    splits: dict[str, set[str]] = defaultdict(set)
    for c in casos:
        splits[c.grupo].add(c.split)
    erros += [f"[7] grupo {g} dividido: {s}" for g, s in splits.items() if {"dev", "test"} <= s]

    doc_simulados = DADOS_SIMULADOS.read_text(encoding="utf-8") if DADOS_SIMULADOS.exists() else ""
    for c in casos:
        for reg in c.api_esperada.registros_esperados if c.api_esperada else []:
            if reg not in doc_simulados:
                erros.append(f"[+] {c.id}: registro-âncora {reg} não documentado")
    return erros


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else CANDIDATAS
    erros = validar(caminho)
    casos = carregar(caminho)
    print(f"{caminho.name}: {len(casos)} casos | por tipo {dict(Counter(c.tipo for c in casos))}")
    print(f"split: {dict(Counter(c.split for c in casos))}")
    if erros:
        print(f"{len(erros)} problema(s):")
        for e in erros:
            print("  -", e)
        return 1
    print("Todas as verificações passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
