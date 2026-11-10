"""C2: C1 com um agente que também consulta a agenda de paradas programadas (Fase 7).

Fluxo, com no máximo 3 chamadas ao LLM (roteador, resposta e um reparo):
1. o roteador decide se a pergunta precisa da agenda e/ou das normas e extrai bairro e data;
2. sem agenda, a pergunta segue exatamente o caminho do C1;
3. com agenda, o bairro e a data são resolvidos; bairro ambíguo, desconhecido ou ausente vira
   pedido de esclarecimento, sem LLM; a agenda é consultada (timeout da ferramenta);
4. o LLM responde citando os registros (tipo "api") e, se pedidos e acima de τ, os trechos das
   normas; o validador é o mesmo do C1. O aviso para confirmar com a distribuidora é
   acrescentado pelo código, não pelo LLM.
"""

from __future__ import annotations

import datetime as dt
import time
from typing import Any

from src.agente import prompts
from src.agente.normalizacao import bairro_no_texto, resolver_bairro, resolver_data
from src.agente.roteador import rotear
from src.paradas_api.fonte import ClienteParadasHTTP, FonteParadas
from src.paradas_api.gerador import carregar_distritos
from src.rag.pipeline import C1, Saida
from src.rag.schema import Resposta

DIAS_SEM_DATA = 7
# Textos aprovados pelo Pedro (09/11/2026).
AVISO_AGENDA = (
    "Confirme na página de manutenção programada da sua distribuidora, com o número da sua "
    "instalação."
)


def _recusa(resposta: str, motivo: str) -> Resposta:
    return Resposta(
        resposta=resposta, recusa=True, motivo_recusa=motivo, fontes=[], confianca="alta"
    )


SEMANA = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
]


def _dia(d: dt.date) -> str:
    return f"{SEMANA[d.weekday()]}, {d:%d/%m/%Y}"


def _lista(nomes: list[str], maximo: int = 6) -> str:
    mostrados = nomes[:maximo]
    texto = (
        ", ".join(mostrados[:-1]) + f" e {mostrados[-1]}" if len(mostrados) > 1 else mostrados[0]
    )
    return texto + (", entre outros" if len(nomes) > maximo else "")


RECUSA_SEM_BAIRRO = _recusa(
    "Para consultar a agenda de manutenções programadas, preciso saber o seu bairro. Qual é?",
    "Bairro não informado.",
)
RECUSA_ERRO_AGENDA = _recusa(
    f"Não consegui consultar a agenda de manutenções programadas agora. {AVISO_AGENDA}",
    "A consulta à agenda de paradas falhou ou demorou demais.",
)
RECUSA_CONTINGENCIA_AGENDA = _recusa(
    f"Não consegui montar uma resposta que eu pudesse comprovar com a agenda. {AVISO_AGENDA}",
    "A resposta gerada não passou na verificação de citação, de números ou de formato.",
)


CORRECOES = {
    "A": "reescrever a pergunta em português padrão antes da busca e do portão",
    "C": "busca híbrida (BM25 + densa, RRF) com reranker bge-reranker-v2-m3",
}


class C2(C1):
    """C1 com agente. `correcoes` ativa as correções da Fase 8 (ver CORRECOES)."""

    nome = "C2"

    def __init__(
        self,
        cfg: dict[str, Any],
        fonte: FonteParadas | None = None,
        correcoes: frozenset[str] = frozenset(),
        **kwargs: Any,
    ):
        super().__init__(cfg, **kwargs)
        if desconhecidas := set(correcoes) - set(CORRECOES):
            raise ValueError(f"correções desconhecidas: {desconhecidas}")
        self.correcoes = frozenset(correcoes)
        if "C" in self.correcoes:
            self.modo, self.reranker = "hibrido", True
        self.referencia = dt.date.fromisoformat(cfg["data_referencia"])
        self.fonte = fonte or ClienteParadasHTTP(
            cfg["api_paradas"]["base_url"], timeout=cfg["agente"]["timeout_ferramenta_s"]
        )
        try:
            self.bairros = self.fonte.bairros("")
        except Exception:  # noqa: BLE001 (API fora do ar: usa a lista local do IBGE)
            self.bairros = carregar_distritos()

    def responder(self, pergunta: str) -> Saida:
        t0 = time.perf_counter()
        r = rotear(pergunta, self.llm, self.bairros, self.referencia, "A" in self.correcoes)
        rot = {**r.roteamento.model_dump(), "origem": r.origem, "bruto": r.bruto, "erro": r.erro}
        if not r.roteamento.precisa_agenda:
            consulta = r.roteamento.pergunta_normas if "A" in self.correcoes else None
            saida = super().responder(pergunta, consulta=consulta)
            saida.config, saida.roteamento = self.nome, rot
            saida.latencia_s = round(time.perf_counter() - t0, 3)
            return saida
        saida = Saida(self.nome, None, "esclarecimento", 0.0, roteamento=rot)
        self._agenda(pergunta, r.roteamento, saida)
        saida.latencia_s = round(time.perf_counter() - t0, 3)
        return saida

    def _agenda(self, pergunta: str, rot: Any, saida: Saida) -> None:
        bairro = resolver_bairro(
            rot.bairro or bairro_no_texto(pergunta, self.bairros), self.bairros
        )
        saida.roteamento["bairro_resolvido"] = {
            "situacao": bairro.situacao,
            "nome": bairro.nome,
            "candidatos": bairro.candidatos,
        }
        if bairro.situacao == "ausente":
            saida.resposta = RECUSA_SEM_BAIRRO
            return
        if bairro.situacao == "ambiguo":
            saida.resposta = _recusa(
                f"Encontrei mais de um bairro com esse nome: {_lista(bairro.candidatos)}. "
                "Qual deles é o seu?",
                "Bairro ambíguo.",
            )
            return
        if bairro.situacao == "desconhecido":
            saida.resposta = _recusa(
                f'Não encontrei o bairro "{bairro.consultado}" na agenda de manutenções, que por '
                f"enquanto cobre só os distritos da cidade de São Paulo. {AVISO_AGENDA}",
                "Bairro fora da agenda.",
            )
            return

        data = resolver_data(rot.data, self.referencia) if rot.data else None
        data = data or resolver_data(pergunta, self.referencia)
        dias = (
            [data]
            if data
            else [self.referencia + dt.timedelta(days=i) for i in range(DIAS_SEM_DATA)]
        )
        saida.roteamento["datas_consultadas"] = [d.isoformat() for d in dias]
        paradas: dict[str, dict[str, Any]] = {}
        try:
            for d in dias:
                res = self.fonte.buscar(bairro.nome, d)
                saida.consultas.append(
                    {
                        "bairro": bairro.nome,
                        "data": d.isoformat(),
                        "ids": [p["id"] for p in res.paradas],
                    }
                )
                for p in res.paradas:
                    paradas.setdefault(p["id"], p)
        except Exception as e:  # noqa: BLE001 (erro ou timeout da ferramenta vira recusa)
            saida.resposta, saida.origem = RECUSA_ERRO_AGENDA, "erro_agenda"
            saida.roteamento["erro_agenda"] = repr(e)[:300]
            return

        registros = [prompts.registro_como_trecho(p) for p in paradas.values()]
        if not registros:
            registros = [prompts.consulta_vazia_como_trecho(bairro.nome, dias[0], dias[-1])]
        normas: list[dict[str, Any]] = []
        if rot.precisa_normas:
            cands, nota = self.recuperar(rot.pergunta_normas or pergunta)
            saida.nota_portao = round(nota, 4)
            if nota >= self.tau:
                normas = [c.chunk for c in cands]
                saida.trechos = [
                    {"chunk_id": c.chunk_id, "nota": round(float(c.score), 4)} for c in cands
                ]
        saida.trechos = [
            {"chunk_id": r["chunk_id"], "nota": None} for r in registros
        ] + saida.trechos
        if len(dias) == 1:
            periodo = f"data pedida: {_dia(dias[0])}"
        else:
            periodo = f"período pedido: de {_dia(dias[0])} a {_dia(dias[-1])}"
        descricao = f"bairro {bairro.nome}; {periodo}; hoje é {_dia(self.referencia)}"
        msgs = prompts.mensagens_c2(pergunta, registros, normas, self.data, descricao)
        chunks = {c["chunk_id"]: c for c in registros + normas}
        self._gerar_com_reparo(msgs, chunks, pergunta, saida, RECUSA_CONTINGENCIA_AGENDA)
        if saida.resposta is not None and not saida.resposta.recusa:
            saida.resposta = saida.resposta.model_copy(
                update={"resposta": f"{saida.resposta.resposta.rstrip()} {AVISO_AGENDA}"}
            )
