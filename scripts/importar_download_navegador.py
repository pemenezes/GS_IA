"""Importa um arquivo obtido pelo navegador (fontes protegidas por desafio anti-robô).

Alguns servidores da ANEEL respondem 403 a clientes HTTP (desafio da Cloudflare). Nesses casos o
arquivo é obtido num navegador com `fetch` na própria página e devolvido em base64, em JSON:
{"status", "ct", "lm", "n", "b64"}. Este script decodifica, confere o tamanho, grava em base/raw/
e registra a origem em downloads.json com metodo="navegador".

Uso:  python scripts/importar_download_navegador.py D01 <resposta.json>
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingestao import download  # noqa: E402


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    doc_id, caminho = sys.argv[1], Path(sys.argv[2])
    manifesto = download.carregar_manifesto()
    doc = next(d for d in manifesto["documentos"] if d["id"] == doc_id)

    bruto = json.loads(caminho.read_text(encoding="utf-8"))
    valor = bruto
    while isinstance(valor, dict) and "b64" not in valor:
        valor = valor.get("result", valor.get("value"))
        if isinstance(valor, dict) and "value" in valor:
            valor = valor["value"]
    resposta = json.loads(valor) if isinstance(valor, str) else valor
    if resposta["status"] != 200:
        raise SystemExit(f"status HTTP {resposta['status']}: nada importado")
    dados = base64.b64decode(resposta["b64"])
    if len(dados) != resposta["n"]:
        raise SystemExit(f"tamanho divergente: {len(dados)} != {resposta['n']}")

    url_final = resposta.get("url") or doc["urls"][0]
    destino = download.dir_raw(doc)
    destino.mkdir(parents=True, exist_ok=True)
    arquivo = destino / f"{doc_id}{download.EXTENSAO[doc['formato']]}"
    arquivo.write_bytes(dados)
    cab = {"content-type": resposta.get("ct") or "", "last-modified": resposta.get("lm") or ""}
    reg = download._registro(doc, doc["urls"][0], url_final, arquivo, dados, cab)
    reg["metodo"] = "navegador"
    download._gravar_registro(destino, [reg])
    nome = arquivo.relative_to(download.RAIZ)
    print(f"{nome}: {len(dados) / 1024:.0f} KB, sha256 {reg['sha256'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
