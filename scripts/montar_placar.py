"""Placar oficial (Fase 8): C0, C1 e C2 no test (oficial) e no dev, com IC de Wilson de 95%.

  python scripts/montar_placar.py

Junta as métricas automáticas das execuções (avaliacao/runs/geracao/*.meta.json) com a
conferência manual do test (avaliacao/revisao/conferencia_test.yaml). No C1, as respostas
iguais às do C2 herdam o veredito do C2; só as que diferem foram conferidas.

Grava avaliacao/placar.csv e avaliacao/matriz_erros.csv.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

from src.avaliacao.recuperacao import RESPONDIVEIS, wilson  # noqa: E402
from src.config import RAIZ  # noqa: E402

RUNS = RAIZ / "avaliacao" / "runs" / "geracao"
REVISAO = RAIZ / "avaliacao" / "revisao"
Q = "qwen3_4b-instruct-2507-q4_K_M"
CONFIGS = ("C0", "C1", "C2")
AUTOMATICAS = [
    ("json_valido_1a", "JSON válido na 1ª tentativa"),
    ("acuracia", "acurácia automática (fatos-chave)"),
    ("citacao_correta", "citação correta (gold v2 e verificável)"),
    ("alucinacao", "suspeita automática de alucinação"),
    ("recusa_correta", "recusa correta (não consta e fora do domínio)"),
    ("recusa_indevida", "recusa indevida (respondíveis)"),
    ("recusa_nega_regra", "recusa que nega regra (heurística)"),
    ("acerto_dinamicas", "acerto nas dinâmicas (agenda)"),
    ("roteamento_correto", "roteamento correto"),
]
NOMES_CATEGORIA = {
    1: "1. recuperação",
    2: "2. fragmentação",
    3: "3. recusa indevida",
    4: "4. aceite indevido (não consta)",
    5: "5. número alterado",
    6: "6. citação não sustenta",
    7: "7. roteador/ferramenta",
    8: "8. regra obsoleta",
}


def _ler(nome: str) -> list[dict]:
    with open(RUNS / f"{nome}.jsonl", encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def _linha(cfg: str, split: str, metrica: str, fonte: str, k: int, n: int) -> dict:
    lo, hi = wilson(k, n)
    return {
        "config": cfg,
        "split": split,
        "metrica": metrica,
        "fonte": fonte,
        "k": k,
        "n": n,
        "taxa": round(k / n, 3) if n else "",
        "ic95_inf": round(lo, 3),
        "ic95_sup": round(hi, 3),
    }


def vereditos(conf: dict, cfg: str, linhas: list[dict], linhas_c2: dict[str, dict]) -> dict:
    """id -> {veredito, falso} das respostas dadas às respondíveis, para uma configuração."""
    resp = {x["id"]: x for x in linhas if x["tipo"] in RESPONDIVEIS}
    v = {}
    for id_, x in resp.items():
        r = x["saida"]["resposta"]
        if r is None or r["recusa"]:
            recusa = conf.get(f"{cfg}_recusas", {}).get(id_, {})
            if recusa.get("veredito"):
                v[id_] = {"veredito": recusa["veredito"], "falso": "nao", "recusa": True}
            continue
        if id_ in conf.get(cfg, {}):
            v[id_] = conf[cfg][id_]
        elif cfg == "C1" and linhas_c2[id_]["saida"]["resposta"] == r:
            v[id_] = conf["C2"][id_]
        else:
            raise SystemExit(f"{cfg} {id_}: resposta sem veredito na conferência")
    return v


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    conf = yaml.safe_load((REVISAO / "conferencia_test.yaml").read_text(encoding="utf-8"))
    if conf["status"] != "aprovado":
        raise SystemExit("a conferência manual ainda não foi aprovada")
    conf = conf["itens"]
    erros = yaml.safe_load((REVISAO / "erros_test.yaml").read_text(encoding="utf-8"))["falhas"]
    placar = []
    for split in ("test", "dev"):
        for cfg in CONFIGS:
            meta = json.loads((RUNS / f"{cfg}_{split}_{Q}.meta.json").read_text(encoding="utf-8"))
            r = meta["resumo"]
            for chave, nome in AUTOMATICAS:
                if r[chave]["n"]:
                    placar.append(
                        _linha(cfg, split, nome, "automática", r[chave]["k"], r[chave]["n"])
                    )
            for nome, chave in (
                ("latência p50 (s)", "latencia_p50_s"),
                ("latência p95 (s)", "latencia_p95_s"),
            ):
                placar.append(
                    {
                        "config": cfg,
                        "split": split,
                        "metrica": nome,
                        "fonte": "medida",
                        "taxa": r[chave],
                    }
                )
            placar.append(
                {
                    "config": cfg,
                    "split": split,
                    "metrica": "VRAM de pico (MiB)",
                    "fonte": "medida",
                    "taxa": meta["vram_pico_mib"],
                }
            )

    linhas_c2 = {x["id"]: x for x in _ler(f"C2_test_{Q}")}
    for cfg in CONFIGS:
        linhas = _ler(f"{cfg}_test_{Q}")
        v = vereditos(conf, cfg, linhas, linhas_c2)
        n_resp = sum(x["tipo"] in RESPONDIVEIS for x in linhas)
        dadas = [x for x in v.values() if not x.get("recusa")]
        corretas = sum(x["veredito"] == "correta" for x in v.values())
        parciais = sum(x["veredito"] == "parcial" for x in v.values())
        placar += [
            _linha(cfg, "test", "acurácia manual (corretas)", "manual", corretas, n_resp),
            _linha(
                cfg,
                "test",
                "acurácia manual (corretas + parciais)",
                "manual",
                corretas + parciais,
                n_resp,
            ),
            _linha(
                cfg,
                "test",
                "alucinação manual (respostas dadas que afirmam algo falso)",
                "manual",
                sum(x["falso"] == "sim" for x in dadas),
                len(dadas),
            ),
        ]
        if cfg == "C0":
            recusas = conf["C0_recusas"]
            placar.append(
                _linha(
                    cfg,
                    "test",
                    "recusa que nega regra existente",
                    "manual",
                    sum(x["nega_regra"] == "sim" for x in recusas.values()),
                    len(recusas),
                )
            )

    with open(RAIZ / "avaliacao" / "placar.csv", "w", encoding="utf-8", newline="") as f:
        campos = ["config", "split", "metrica", "fonte", "k", "n", "taxa", "ic95_inf", "ic95_sup"]
        w = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
        w.writeheader()
        w.writerows(placar)

    matriz = []
    for cfg in ("C1", "C2"):
        cont = {nome: 0 for nome in NOMES_CATEGORIA.values()}
        for e in erros.values():
            cont[NOMES_CATEGORIA[e["categoria"]]] += 1
        dinamicas = 3 if cfg == "C1" else 0  # o C1 não tem acesso à agenda
        cont[NOMES_CATEGORIA[7]] += dinamicas
        matriz.append({"config": cfg, **cont, "total": sum(cont.values())})
    with open(RAIZ / "avaliacao" / "matriz_erros.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(matriz[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(matriz)

    for p in placar:
        if p["split"] == "test" and p["fonte"] != "medida":
            print(
                f"{p['config']} {p['metrica']:<60} {p['k']}/{p['n']} = {p['taxa']} "
                f"[{p['ic95_inf']}; {p['ic95_sup']}]"
            )
    for m in matriz:
        print(m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
