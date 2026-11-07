"""Schema de saída do assistente (Apêndice B.1 do plano)."""

from __future__ import annotations

import copy
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError, model_validator


class Fonte(BaseModel):
    tipo: Literal["norma", "api"]
    id: str = Field(description="chunk_id da base ou id do registro da API")
    trecho_citado: str = Field(max_length=400, description="cópia literal do trecho usado")


class Resposta(BaseModel):
    resposta: str = Field(description="linguagem simples, frases curtas")
    recusa: bool
    motivo_recusa: str | None = None
    fontes: list[Fonte] = []
    confianca: Literal["alta", "media", "baixa"]

    @model_validator(mode="after")
    def _resposta_sem_recusa_tem_fonte(self) -> Resposta:
        if not self.recusa and not self.fontes:
            raise ValueError("recusa=false exige pelo menos uma fonte")
        return self


def schema_para_llm(modelo: type[BaseModel] = Resposta) -> dict[str, Any]:
    """JSON Schema para o `format` do Ollama, com todos os campos obrigatórios.

    A geração restrita do Ollama só garante os campos listados em `required`; campos com valor
    padrão (como `fontes`) ficariam de fora e o modelo poderia omiti-los.
    """
    schema = copy.deepcopy(modelo.model_json_schema())
    for obj in (schema, *schema.get("$defs", {}).values()):
        if "properties" in obj:
            obj["required"] = list(obj["properties"])
    return schema


def classificar_saida(conteudo: str) -> tuple[Resposta | None, str]:
    """Valida a saída do LLM e devolve (resposta, categoria).

    Categorias: "ok"; "regras" (estrutura certa, mas viola as regras do B.1);
    "schema" (JSON fora do schema); "json" (não é JSON).
    """
    try:
        return Resposta.model_validate_json(conteudo), "ok"
    except ValidationError as e:
        erros = e.errors()
        if any(err["type"] == "json_invalid" for err in erros):
            return None, "json"
        if all(err["type"] == "value_error" and not err["loc"] for err in erros):
            return None, "regras"
        return None, "schema"
