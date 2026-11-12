"""Configurações C0 (LLM sem a base) e C1 (busca + portão + geração validada), Fase 5.

As duas expõem `responder(pergunta) -> Saida`; o agente (C2) e o serviço usam a mesma interface.
O LLM é uma função `(mensagens, schema) -> corpo do Ollama`, trocada por um simulador nos testes.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel, ValidationError

from src.rag import llm_ollama, prompt
from src.rag.schema import Resposta, classificar_saida, schema_para_llm
from src.rag.validador import Verificacao, validar

ChamarLLM = Callable[[list[dict[str, str]], dict[str, Any] | None], dict[str, Any]]

AVISO_CANAIS = "Procure a sua distribuidora de energia, a ANEEL ou o Procon."
# Texto aprovado pelo Pedro (08/11/2026).
RECUSA_PORTAO = Resposta(
    resposta="Não encontrei esse assunto nas normas que eu consulto. Para não passar informação "
    f"errada, prefiro não responder. {AVISO_CANAIS}",
    recusa=True,
    motivo_recusa="A pergunta não corresponde a nenhum trecho da base de normas.",
    fontes=[],
    confianca="alta",
)
RECUSA_CONTINGENCIA = Resposta(
    resposta=f"Não consegui montar uma resposta que eu pudesse comprovar com as normas. "
    f"{AVISO_CANAIS}",
    recusa=True,
    motivo_recusa="A resposta gerada não passou na verificação de citação, de números ou de "
    "formato.",
    fontes=[],
    confianca="baixa",
)


@dataclass
class Tentativa:
    conteudo: str
    categoria: str
    erros: list[str]
    citacoes: list[dict[str, Any]]
    numeros_sem_base: list[str]
    tokens_prompt: int
    tokens_saida: int
    duracao_s: float


@dataclass
class Saida:
    config: str
    resposta: Resposta | None  # None só no C0 quando a saída não passa no schema
    origem: Literal[
        "llm", "reparo", "portao", "contingencia", "invalida", "esclarecimento", "erro_agenda"
    ]
    latencia_s: float
    nota_portao: float | None = None
    trechos: list[dict[str, Any]] = field(default_factory=list)  # chunk_id e nota
    tentativas: list[Tentativa] = field(default_factory=list)
    # C2: decisão do roteador e consultas feitas à agenda de paradas.
    roteamento: dict[str, Any] | None = None
    consultas: list[dict[str, Any]] = field(default_factory=list)
    # Correção F (Fase 8B): resultado da autoverificação.
    verificacoes: list[dict[str, Any]] = field(default_factory=list)


class VerificacaoLLM(BaseModel):
    ok: bool
    problemas: list[str]


SCHEMA_VERIFICACAO = schema_para_llm(VerificacaoLLM)


def chamar_ollama(cfg: dict[str, Any], modelo: str | None = None) -> ChamarLLM:
    cfg_llm = cfg["llm"]
    opcoes = llm_ollama.opcoes_do_config(cfg_llm)
    nome = modelo or cfg_llm["modelo"]

    def chamar(mensagens: list[dict[str, str]], schema: dict[str, Any] | None) -> dict[str, Any]:
        return llm_ollama.chat_json(
            cfg_llm["host"],
            nome,
            mensagens,
            schema,
            opcoes,
            think=cfg_llm["think"],
            keep_alive=cfg_llm["keep_alive"],
        )

    return chamar


def _tentativa(corpo: dict[str, Any], v: Verificacao, dur: float) -> Tentativa:
    return Tentativa(
        conteudo=corpo["message"]["content"],
        categoria=v.categoria,
        erros=v.erros,
        citacoes=v.citacoes,
        numeros_sem_base=v.numeros_sem_base,
        tokens_prompt=corpo.get("prompt_eval_count", 0),
        tokens_saida=corpo.get("eval_count", 0),
        duracao_s=round(dur, 3),
    )


class _Base:
    nome = ""

    def __init__(
        self,
        cfg: dict[str, Any],
        llm: ChamarLLM | None = None,
        estruturada: bool = True,
    ) -> None:
        self.cfg = cfg
        self.data = cfg["data_referencia"]
        self.llm = llm or chamar_ollama(cfg)
        self.schema = schema_para_llm()
        self.estruturada = estruturada

    def _gerar(self, msgs: list[dict[str, str]]) -> tuple[dict[str, Any], float]:
        t0 = time.perf_counter()
        corpo = self.llm(msgs, self.schema if self.estruturada else None)
        return corpo, time.perf_counter() - t0

    def _schema_no_texto(self) -> dict[str, Any] | None:
        return None if self.estruturada else self.schema


class C0(_Base):
    """Mesmo modelo, schema e parâmetros, sem trechos, sem portão e sem reparo."""

    nome = "C0"

    def responder(self, pergunta: str, origem: str = "texto") -> Saida:
        t0 = time.perf_counter()
        msgs = prompt.mensagens_c0(pergunta, self.data, self._schema_no_texto())
        corpo, dur = self._gerar(msgs)
        resp, categoria = classificar_saida(corpo["message"]["content"])
        v = Verificacao(resp, categoria)
        return Saida(
            config=self.nome,
            resposta=resp,
            origem="llm" if resp else "invalida",
            latencia_s=round(time.perf_counter() - t0, 3),
            tentativas=[_tentativa(corpo, v, dur)],
        )


class C1(_Base):
    """Busca densa (top-3), portão pelo cosseno, geração com citação verificável e um reparo."""

    nome = "C1"

    def __init__(self, cfg: dict[str, Any], retriever: Any = None, **kwargs: Any) -> None:
        super().__init__(cfg, **kwargs)
        if retriever is None:
            from src.rag.retriever import Retriever

            retriever = Retriever(cfg)
        self.retriever = retriever
        self.tau = cfg["retrieval"]["limiar_recusa"]
        self.modo = "hibrido" if cfg["retrieval"]["hibrido"] else "denso"
        self.reranker: bool | None = None  # None: segue retrieval.reranker do config
        # Correções da Fase 8B (ligadas pelo C2): D e E no formato dos trechos, F na verificação.
        self.formato: dict[str, bool] = {}
        self.ordenar = False
        self.verificar = False
        # Correção M (opção B da Fase 8B): reformulações pelo LLM, reranker e k trechos; o
        # portão usa o maior cosseno entre a pergunta e as reformulações, com τ próprio.
        self.multiconsulta: dict[str, Any] | None = None
        self.ultimas_reformulacoes: list[str] = []

    def recuperar(self, pergunta: str) -> tuple[list[Any], float]:
        if self.multiconsulta:
            from src.rag.multiconsulta import buscar_multi, reformular

            self.ultimas_reformulacoes = reformular(pergunta, self.llm)
            return buscar_multi(
                self.retriever,
                [pergunta, *self.ultimas_reformulacoes],
                k=self.multiconsulta["k"],
                reranker=True,
                pergunta_reranker=pergunta,
            )
        cands = self.retriever.buscar(pergunta, modo=self.modo, reranker=self.reranker)
        if self.modo == "denso" and not self.reranker and cands:
            nota = cands[0].score_denso
        else:
            # O portão usa sempre o cosseno denso do melhor trecho (τ calibrado nele).
            nota = self.retriever.melhor_cosseno(pergunta)
        return cands, float(nota)

    def responder(self, pergunta: str, consulta: str | None = None, origem: str = "texto") -> Saida:
        """`consulta` substitui a pergunta só na busca e no portão (correção A do C2)."""
        t0 = time.perf_counter()
        cands, nota = self.recuperar(consulta or pergunta)
        trechos = [{"chunk_id": c.chunk_id, "nota": round(float(c.score), 4)} for c in cands]
        saida = Saida(self.nome, None, "portao", 0.0, round(nota, 4), trechos)
        if self.multiconsulta:
            saida.consultas.append({"reformulacoes": self.ultimas_reformulacoes})
        tau = self.multiconsulta["tau"] if self.multiconsulta else self.tau
        if nota < tau:
            saida.resposta = RECUSA_PORTAO
            saida.latencia_s = round(time.perf_counter() - t0, 3)
            return saida

        chunks = {c.chunk_id: c.chunk for c in cands}
        lista = [c.chunk for c in cands]
        if self.ordenar:
            lista = prompt.ordenar_por_confiabilidade(lista)
        msgs = prompt.mensagens_c1(
            pergunta, lista, self.data, self._schema_no_texto(), **self.formato
        )
        self._gerar_com_reparo(msgs, chunks, pergunta, saida, RECUSA_CONTINGENCIA)
        saida.latencia_s = round(time.perf_counter() - t0, 3)
        return saida

    def _verificar(
        self, pergunta: str, resposta: Resposta, chunks: dict[str, dict[str, Any]], saida: Saida
    ) -> list[str]:
        """Correção F: o LLM confere a resposta contra os trechos citados; devolve os problemas.

        Se a verificação falhar (rede, JSON), a resposta segue: a verificação não pode bloquear.
        """
        citados = [chunks[f.id] for f in resposta.fontes if f.id in chunks]
        msgs = prompt.mensagens_verificacao(pergunta, citados, resposta.resposta, **self.formato)
        t0 = time.perf_counter()
        registro: dict[str, Any] = {"ok": True, "problemas": [], "bruto": "", "erro": ""}
        try:
            corpo = self.llm(msgs, SCHEMA_VERIFICACAO)
            registro["bruto"] = corpo["message"]["content"]
            v = VerificacaoLLM.model_validate_json(registro["bruto"])
            registro.update(ok=v.ok, problemas=[] if v.ok else v.problemas or ["revise a resposta"])
        except (ValidationError, KeyError, ValueError) as e:
            registro["erro"] = str(e)[:300]
        except Exception as e:  # noqa: BLE001
            registro["erro"] = repr(e)[:300]
        registro["duracao_s"] = round(time.perf_counter() - t0, 3)
        saida.verificacoes.append(registro)
        return registro["problemas"]

    def _gerar_com_reparo(
        self,
        msgs: list[dict[str, str]],
        chunks: dict[str, dict[str, Any]],
        pergunta: str,
        saida: Saida,
        contingencia: Resposta,
    ) -> None:
        """Gera, valida e tenta um reparo; se falhar de novo, usa a recusa de contingência.

        Com `verificar` (correção F), a primeira resposta válida passa pela autoverificação; os
        problemas apontados viram o reparo. Há um único reparo, por validação ou por
        verificação; se ele já foi gasto, o sistema recusa.
        """
        reparo_usado = verificado = False
        while True:
            corpo, dur = self._gerar(msgs)
            conteudo = corpo["message"]["content"]
            v = validar(conteudo, chunks, pergunta, self.data)
            saida.tentativas.append(_tentativa(corpo, v, dur))
            problemas = v.erros
            if v.ok and self.verificar and not verificado and not v.resposta.recusa:
                verificado = True
                problemas = self._verificar(pergunta, v.resposta, chunks, saida)
            if not problemas:
                saida.resposta, saida.origem = v.resposta, ("reparo" if reparo_usado else "llm")
                return
            if reparo_usado:
                saida.resposta, saida.origem = contingencia, "contingencia"
                return
            reparo_usado = True
            msgs = [
                *msgs,
                {"role": "assistant", "content": conteudo},
                prompt.mensagem_reparo(problemas),
            ]
