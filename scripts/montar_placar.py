"""Placar final (Fase 8): C0, C1, C2, C2+CDEV e C2+M no dev, test, T2 e T3, com IC de Wilson.

  python scripts/montar_placar.py

Junta as métricas automáticas das execuções (avaliacao/runs/geracao/*.meta.json) com as
conferências manuais (avaliacao/revisao/conferencia_*.yaml). Respostas que não mudaram herdam o
veredito da conferência anterior, como registrado em cada arquivo.

Coluna `condicao`:
- `dev`: conjunto usado para escolher modelos e correções;
- `limpa`: execução única, sem que o conjunto tenha sido usado para escolher aquela configuração;
- `pos_selecao`: a configuração foi escolhida olhando este conjunto (C2+M no test e no T2);
- `mista`: soma de test, T2 e T3.

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
SUFIXO = {"C0": "", "C1": "", "C2": "", "C2+CDEV": "_corrCDEV", "C2+M": "_corrM"}
EXECUCOES = [
    # (configuração, conjunto, condição)
    ("C0", "dev", "dev"),
    ("C1", "dev", "dev"),
    ("C2", "dev", "dev"),
    ("C2+CDEV", "dev", "dev"),
    ("C2+M", "dev", "dev"),
    ("C0", "test", "limpa"),
    ("C1", "test", "limpa"),
    ("C2", "test", "limpa"),
    ("C2+M", "test", "pos_selecao"),
    ("C0", "test2", "limpa"),
    ("C1", "test2", "limpa"),
    ("C2", "test2", "limpa"),
    ("C2+CDEV", "test2", "limpa"),
    ("C2+M", "test2", "pos_selecao"),
    ("C2", "test3", "limpa"),
    ("C2+M", "test3", "limpa"),
]
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
CAMPOS = [
    "config",
    "split",
    "condicao",
    "metrica",
    "fonte",
    "k",
    "n",
    "taxa",
    "ic95_inf",
    "ic95_sup",
]


def _ler(cfg: str, split: str) -> list[dict]:
    with open(RUNS / f"{cfg[:2]}_{split}_{Q}{SUFIXO[cfg]}.jsonl", encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def _meta(cfg: str, split: str) -> dict:
    return json.loads(
        (RUNS / f"{cfg[:2]}_{split}_{Q}{SUFIXO[cfg]}.meta.json").read_text(encoding="utf-8")
    )


def _yaml(nome: str, validado: bool = True) -> dict:
    dados = yaml.safe_load((REVISAO / nome).read_text(encoding="utf-8"))
    if validado and dados["status"] not in ("aprovado", "validado_pedro"):
        raise SystemExit(f"{nome}: conferência ainda não validada pelo Pedro")
    return dados


def _linha(cfg: str, split: str, cond: str, metrica: str, fonte: str, k: int, n: int) -> dict:
    lo, hi = wilson(k, n)
    return {
        "config": cfg,
        "split": split,
        "condicao": cond,
        "metrica": metrica,
        "fonte": fonte,
        "k": k,
        "n": n,
        "taxa": round(k / n, 3) if n else "",
        "ic95_inf": round(lo, 3),
        "ic95_sup": round(hi, 3),
    }


def vereditos(
    linhas: list[dict],
    itens: dict,
    herdadas: list[str] = (),
    herda_de: dict | None = None,
    recusas: dict | None = None,
    iguais_a: dict[str, dict] | None = None,
) -> dict:
    """id -> {veredito, falso} das respostas às respondíveis de uma execução.

    Recusas ficam de fora, salvo as que a conferência julgou (`recusas`, só no C0 do test).
    `iguais_a`: respostas idênticas às de outra execução herdam o veredito de `herda_de`.
    """
    v = {}
    for x in linhas:
        if x["tipo"] not in RESPONDIVEIS:
            continue
        id_, r = x["id"], x["saida"]["resposta"]
        if r is None or r["recusa"]:
            julgada = (recusas or {}).get(id_, {})
            if julgada.get("veredito"):
                v[id_] = {"veredito": julgada["veredito"], "falso": "nao", "recusa": True}
            continue
        if id_ in itens:
            v[id_] = itens[id_]
        elif id_ in herdadas or (iguais_a is not None and iguais_a[id_]["saida"]["resposta"] == r):
            v[id_] = herda_de[id_]
        else:
            raise SystemExit(f"{id_}: resposta sem veredito na conferência")
    return v


def _manuais(cfg: str, split: str, cond: str, linhas: list[dict], v: dict) -> list[dict]:
    n_resp = sum(x["tipo"] in RESPONDIVEIS for x in linhas)
    dadas = [x for x in v.values() if not x.get("recusa")]
    corretas = sum(x["veredito"] == "correta" for x in v.values())
    parciais = sum(x["veredito"] == "parcial" for x in v.values())
    return [
        _linha(cfg, split, cond, "acurácia manual (corretas)", "manual", corretas, n_resp),
        _linha(
            cfg,
            split,
            cond,
            "acurácia manual (corretas + parciais)",
            "manual",
            corretas + parciais,
            n_resp,
        ),
        _linha(
            cfg,
            split,
            cond,
            "alucinação manual (respostas dadas que afirmam algo falso)",
            "manual",
            sum(x["falso"] == "sim" for x in dadas),
            len(dadas),
        ),
    ]


def todos_vereditos() -> dict[tuple[str, str], tuple[list[dict], dict]]:
    """(configuração, conjunto) -> (linhas da execução, vereditos), para as conferências feitas."""
    test = _yaml("conferencia_test.yaml")["itens"]
    t2 = _yaml("conferencia_t2.yaml")["itens"]
    t2_pre = _yaml("conferencia_t2_pre.yaml", validado=False)["herdadas_c2_final"]
    m = _yaml("conferencia_m.yaml")
    t3 = _yaml("conferencia_t3.yaml")["itens"]
    lin = {(c, s): _ler(c, s) for c, s, _ in EXECUCOES if s != "dev"}
    c2_test = {x["id"]: x for x in lin[("C2", "test")]}
    out = {}
    for cfg in ("C0", "C1", "C2"):
        out[(cfg, "test")] = vereditos(
            lin[(cfg, "test")],
            test.get(cfg, {}),
            herda_de=test["C2"],
            recusas=test.get(f"{cfg}_recusas"),
            iguais_a=c2_test if cfg == "C1" else None,
        )
    out[("C2+M", "test")] = vereditos(
        lin[("C2+M", "test")], m["test"]["itens"], m["test"]["herdadas"], test["C2"]
    )
    out[("C2", "test2")] = vereditos(lin[("C2", "test2")], t2["C2"])
    out[("C2+CDEV", "test2")] = vereditos(
        lin[("C2+CDEV", "test2")],
        t2["C2_final"],
        t2_pre["mesma_resposta"] + t2_pre["mesmo_sentido"],
        t2["C2"],
    )
    out[("C2+M", "test2")] = vereditos(
        lin[("C2+M", "test2")], m["test2"]["itens"], m["test2"]["herdadas"], t2["C2"]
    )
    out[("C2", "test3")] = vereditos(lin[("C2", "test3")], t3["C2"])
    out[("C2+M", "test3")] = vereditos(lin[("C2+M", "test3")], t3["C2M"])
    return {k: (lin[k], v) for k, v in out.items()}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    placar = []
    for cfg, split, cond in EXECUCOES:
        meta = _meta(cfg, split)
        r = meta["resumo"]
        for chave, nome in AUTOMATICAS:
            if chave in r and r[chave]["n"]:
                placar.append(
                    _linha(cfg, split, cond, nome, "automática", r[chave]["k"], r[chave]["n"])
                )
        for nome, valor in (
            ("latência p50 (s)", r["latencia_p50_s"]),
            ("latência p95 (s)", r["latencia_p95_s"]),
            ("VRAM de pico (MiB)", meta["vram_pico_mib"]),
        ):
            placar.append(
                {
                    "config": cfg,
                    "split": split,
                    "condicao": cond,
                    "metrica": nome,
                    "fonte": "medida",
                    "taxa": valor,
                }
            )

    conds = {(c, s): cond for c, s, cond in EXECUCOES}
    manuais = todos_vereditos()
    for (cfg, split), (linhas, v) in manuais.items():
        placar += _manuais(cfg, split, conds[(cfg, split)], linhas, v)
    recusas_c0 = _yaml("conferencia_test.yaml")["itens"]["C0_recusas"]
    placar.append(
        _linha(
            "C0",
            "test",
            "limpa",
            "recusa que nega regra existente",
            "manual",
            sum(x["nega_regra"] == "sim" for x in recusas_c0.values()),
            len(recusas_c0),
        )
    )
    for cfg in ("C2", "C2+M"):
        linhas = [x for s in ("test", "test2", "test3") for x in manuais[(cfg, s)][0]]
        v = {}
        for s in ("test", "test2", "test3"):
            v |= manuais[(cfg, s)][1]
        placar += _manuais(cfg, "test+T2+T3", "mista", linhas, v)

    with open(RAIZ / "avaliacao" / "placar.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, lineterminator="\n")
        w.writeheader()
        w.writerows(placar)

    erros = _yaml("erros_test.yaml", validado=False)["falhas"]
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
        if p["fonte"] == "manual":
            print(
                f"{p['config']:<8} {p['split']:<11} {p['condicao']:<12} {p['metrica'][:42]:<42} "
                f"{p['k']}/{p['n']} = {p['taxa']} [{p['ic95_inf']}; {p['ic95_sup']}]"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
