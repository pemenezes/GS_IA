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

Os modelos do Ollama ocupam cerca de 28 GB. Para guardá-los fora do disco C, defina a variável
de ambiente do usuário `OLLAMA_MODELS` (nesta máquina, `D:\GS_IA\models\ollama`; a pasta
`models/` é ignorada pelo git) e reinicie o Ollama.

Os modelos do Ollama ocupam cerca de 28 GB. Para guardá-los fora do disco C, defina a variável
de ambiente do usuário `OLLAMA_MODELS` (nesta máquina, `D:\GS_IA\models\ollama`; a pasta
`models/` é ignorada pelo git) e reinicie o Ollama.

`requirements.txt` traz as dependências diretas com versão travada; `requirements-lock.txt`
traz o freeze completo do ambiente de referência (`pip install -r requirements-lock.txt` para
reproduzir exatamente; regenere com `scripts\gerar_lock.py`).

As versões dos modelos também ficam travadas no `config.yaml`: o digest de cada LLM do Ollama
(o `check_env.py` avisa se a tag foi atualizada) e a revisão do bge-m3 no Hugging Face.

## Verificar o ambiente

```powershell
.\.venv\Scripts\python.exe scripts\check_env.py          # GPU, versões, Ollama (JSON < 15 s), bge-m3
.\.venv\Scripts\python.exe scripts\benchmark_modelos.py  # tokens/s e VRAM de pico por candidato
.\.venv\Scripts\python.exe -m pytest                     # testes sem LLM
.\.venv\Scripts\python.exe -m ruff check .
```

O benchmark grava `avaliacao/runs/benchmark_modelos.csv`. Feche programas que usam a GPU
(navegadores com aceleração de hardware, jogos) antes de medir.

## Base de conhecimento

```powershell
.\.venv\Scripts\python.exe scripts\construir_base.py          # baixa o que faltar e gera os trechos
.\.venv\Scripts\python.exe scripts\construir_base.py --etapa base   # só regera os trechos
.\.venv\Scripts\python.exe scripts\qc_amostra.py              # amostra de controle de qualidade
```

- A entrada é `base/manifesto.yaml`, com os 19 documentos aprovados (`docs/lista_documentos.md`).
- Os originais dos **atos oficiais** já estão versionados em `base/raw/`, com sha256 e data de acesso em `base/raw/downloads.json`. Os trechos deles estão em `base/chunks.jsonl`.
- As **páginas explicativas do gov.br** estão sob licença CC BY-ND 3.0, então o texto delas não vai para o git. O script baixa as páginas para `base/local/` e gera `base/local/chunks_govbr.jsonl` na sua máquina. Elas podem ter mudado desde 07/11/2026; o hash original está em `base/fontes.csv`.
- Os servidores da ANEEL (`www2.aneel.gov.br`, `git.aneel.gov.br`) bloqueiam clientes HTTP com um desafio da Cloudflare (erro 403). Os arquivos versionados foram obtidos por navegador e importados com `scripts/importar_download_navegador.py`, que mantém os bytes originais e o hash.

## API de paradas programadas (simulada)

```powershell
.\.venv\Scripts\python.exe scripts\calibrar_paradas.py   # opcional: refaz a calibração (baixa 272 MB da ANEEL)
.\.venv\Scripts\python.exe scripts\gerar_paradas.py      # gera dados/paradas_simuladas.csv e o SQLite
.\.venv\Scripts\python.exe -m uvicorn src.paradas_api.app:app --port 8001
```

- Leitura: `GET /paradas?bairro=Mooca&data=2026-11-10`, `GET /bairros?q=jardim`, `GET /health`. A documentação interativa fica em `http://localhost:8001/docs`.
- Escrita (`POST /paradas`, `PATCH /paradas/{id}`) exige o header `X-API-Key` igual a `PARADAS_API_KEY` do `.env`. Sem chave configurada, ou com o valor de exemplo, a escrita fica desligada.
- Os dados são **simulados**, calibrados com interrupções programadas reais da Enel SP. Os detalhes estão em [`docs/dados_simulados.md`](docs/dados_simulados.md).

## Interface de teste do assistente

Com o Ollama rodando e os índices gerados:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.servico.app:app --port 8000
```

Abra `http://localhost:8000`. Os modelos carregam em segundo plano (cerca de 30 s; o selo "assistente pronto" indica o fim). A página permite escolher a configuração (C0, C1, C2 ou C2M, a recomendada), a origem (texto ou voz) e comparar a resposta lado a lado com o C0. A API correspondente é `POST /v1/perguntar` com `{"pergunta": ..., "config": "C2M", "origem": "texto"}`.

- CPF, CNPJ, telefone, e-mail, CEP e números longos são mascarados antes de chegar ao modelo.
- O log (`logs/servico.jsonl`) guarda um hash da pergunta, a configuração, a latência, se houve recusa, os ids das fontes e os tipos de dado mascarados, sem o texto da pergunta nem da resposta.
- A agenda de paradas usada pelo C2 é a mesma API simulada, executada no mesmo processo (não é preciso subir a porta 8001).

Para executar os notebooks, ative o venv antes (`.\.venv\Scripts\Activate.ps1`), para que o kernel use as bibliotecas do projeto:

```powershell
jupyter nbconvert --to notebook --execute --inplace notebooks\01_base_conhecimento.ipynb
```

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
