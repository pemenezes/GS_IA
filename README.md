# Luz Cidadã (provisório): assistente de direitos do consumidor de energia

Projeto da disciplina *Generative AI for Engineering* (FIAP, Global Solution 2026.2, CitizenTech).
Um LLM local responde perguntas de cidadãos sobre direitos do consumidor de energia elétrica
**somente com base em documentos oficiais**, citando a fonte, e recusa quando a base não tem a
resposta. O plano completo está em [`PLANO_IMPLEMENTACAO_GENAI.md`](PLANO_IMPLEMENTACAO_GENAI.md).

> README em construção: a versão final (Fase 10) terá instruções completas de reprodução.

## Integrantes

| Nome | RM |
|---|---|
| Anny Carolina | RM98295 |
| Henrique Lima | RM551528 |
| Pedro Menezes | RM97432 |

## Pré-requisitos

- Windows 10/11, Python 3.11 ou 3.12
- GPU NVIDIA com pelo menos 6 GB de VRAM (testado numa RTX 2060 6 GB, driver 621.01)
- [Ollama](https://ollama.com) para Windows (testado na 0.40.15)

## Instalação

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env   # e preencha os valores

ollama pull qwen3:4b-instruct-2507-q4_K_M
ollama pull qwen3.5:4b-q4_K_M
ollama pull gemma3:4b-it-q4_K_M
ollama pull llama3.2:3b-instruct-q4_K_M
```

`requirements.txt` traz as dependências diretas com versão travada; `requirements-lock.txt`
traz o freeze completo do ambiente de referência.

## Verificar o ambiente

```powershell
.\.venv\Scripts\python.exe scripts\check_env.py          # GPU, versões, Ollama (JSON < 15 s), bge-m3
.\.venv\Scripts\python.exe scripts\benchmark_modelos.py  # tokens/s e VRAM de pico por candidato
.\.venv\Scripts\python.exe -m pytest                     # testes sem LLM
.\.venv\Scripts\python.exe -m ruff check .
```

O benchmark grava `avaliacao/runs/benchmark_modelos.csv`. Feche programas que usam a GPU
(navegadores com aceleração de hardware, jogos) antes de medir.

## Estrutura

```
base/        documentos oficiais, trechos (chunks) e índices
avaliacao/   conjunto de teste, saídas brutas, placar e análise de erros
notebooks/   notebooks com saídas salvas
src/         código (ingestão, RAG, agente, serviço, API de paradas, avaliação)
scripts/     utilitários (check_env, benchmark, runners)
tests/       pytest
docs/        tarefa da IA, dados simulados, LGPD, relatório
```

## Aviso

Orientação informativa; não substitui o atendimento da distribuidora, da ANEEL ou de um advogado.
