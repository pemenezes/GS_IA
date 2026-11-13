# Luz Cidadã: assistente de direitos do consumidor de energia

[![CI](https://github.com/pemenezes/GS_IA/actions/workflows/ci.yml/badge.svg)](https://github.com/pemenezes/GS_IA/actions/workflows/ci.yml)

Projeto da disciplina *Generative AI for Engineering* (FIAP, Global Solution 2026.2, CitizenTech).
Um LLM local (qwen3 4B, via Ollama) responde perguntas de cidadãos da Região Metropolitana de São
Paulo sobre direitos do consumidor de energia elétrica **somente com base em documentos oficiais**
(REN ANEEL 1.000/2021, PRODIST, CDC, leis da Tarifa Social e da geração distribuída, páginas da
ANEEL e do MME). Toda resposta cita o trecho usado; quando a base não tem a resposta, o assistente
recusa e indica o canal oficial. Um agente também consulta uma agenda (simulada) de paradas
programadas por bairro.

O plano completo está em [`PLANO_IMPLEMENTACAO_GENAI.md`](PLANO_IMPLEMENTACAO_GENAI.md) e o
relatório em [`docs/RELATORIO.md`](docs/RELATORIO.md).

## Integrantes

| Nome | RM |
|---|---|
| Anny Carolina | RM98295 |
| Henrique Lima | RM551528 |
| Pedro Menezes | RM97432 |

## Resultados

Acurácia na conferência manual, resposta a resposta, com IC de Wilson de 95%
(`avaliacao/placar.csv`; análise nos notebooks 05 a 07):

| Configuração | test (26) | T2 (18) | T3 (18, medida limpa) |
|---|---|---|---|
| C0: LLM sozinho | 0/26 | — | — |
| C1: RAG com portão de recusa | 13/26 | — | — |
| C2: C1 + agente da agenda | 13/26 | 10/18 | 9/18 (50%, IC 29% a 71%) |
| **C2+M: C2 com multiconsulta (sistema oficial)** | 19/26 \* | 12/18 \* | **14/18 (78%, IC 55% a 91%)** |

\* Pós-seleção: a multiconsulta foi escolhida olhando a busca no test e no T2. O T3 foi escrito
depois dessa escolha, sobre temas novos, e medido uma única vez.

- Recusa correta das perguntas sem resposta na base: 100% em todos os conjuntos.
- Perguntas da agenda: todas certas no C2 e no C2+M.
- Respostas do C2+M que afirmam algo falso: 13 de 59 (22%) somando os três conjuntos; é o
  principal ponto fraco (detalhes no notebook 06).
- Latência p95 do C2+M: cerca de 19 s numa RTX 2060 de 6 GB.

## Pré-requisitos

- Windows 10/11 e Python 3.12 (3.11 também serve)
- GPU NVIDIA com pelo menos 6 GB de VRAM (testado numa RTX 2060 6 GB, driver 621.01)
- [Ollama](https://ollama.com) para Windows (testado nas versões 0.40.15 e 0.40.16)
- Cerca de 20 GB livres: 3 GB do LLM, 5 GB dos modelos do Hugging Face e as dependências Python
- Opcional: Docker Desktop, para rodar o serviço em container

## Instalação

```powershell
git clone https://github.com/pemenezes/GS_IA.git
cd GS_IA
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env      # e preencha PARADAS_API_KEY se for usar a escrita da API de paradas

ollama pull qwen3:4b-instruct-2507-q4_K_M
```

- `requirements.txt` traz as dependências diretas com versão travada; `requirements-lock.txt`
  traz o freeze completo do ambiente de referência (`pip install -r requirements-lock.txt` para
  reproduzir exatamente; regenere com `scripts\gerar_lock.py`).
- As versões dos modelos ficam travadas no `config.yaml`: o digest de cada LLM do Ollama (o
  `check_env.py` avisa se a tag mudou) e a revisão de cada modelo no Hugging Face.
- Os outros LLMs comparados na avaliação estão em `llm.candidatos` do `config.yaml`; só são
  necessários para refazer essas comparações.
- Para guardar os modelos do Ollama fora do disco C, defina a variável de ambiente do usuário
  `OLLAMA_MODELS` (por exemplo, `D:\GS_IA\models\ollama`; a pasta `models/` é ignorada pelo git)
  e reinicie o Ollama.
- `OLLAMA_HOST` no `.env` muda o endereço do Ollama (padrão `http://localhost:11434`).

## Verificar o ambiente

```powershell
.\.venv\Scripts\python.exe scripts\check_env.py   # GPU, versões, Ollama (JSON em menos de 15 s), bge-m3
.\.venv\Scripts\python.exe -m pytest -q           # testes sem LLM e sem GPU (os mesmos do CI)
.\.venv\Scripts\python.exe -m ruff check src tests scripts
```

Feche programas que usam a GPU (navegadores com aceleração de hardware, jogos) antes de avaliar.
`scripts\benchmark_modelos.py` mede tokens/s e VRAM de cada LLM candidato.

## Base de conhecimento e índices

```powershell
.\.venv\Scripts\python.exe scripts\construir_base.py      # baixa as páginas gov.br e gera os trechos
.\.venv\Scripts\python.exe scripts\construir_indices.py   # índice denso (bge-m3 + FAISS) em base/indices/
```

- A entrada é `base/manifesto.yaml`, com os 19 documentos aprovados (`docs/lista_documentos.md`).
- Os originais dos **atos oficiais** estão versionados em `base/raw/`, com sha256 e data de acesso
  em `base/raw/downloads.json`; os trechos deles estão em `base/chunks.jsonl`.
- As **páginas explicativas do gov.br** estão sob licença CC BY-ND 3.0, então o texto delas não vai
  para o git. O `construir_base.py` baixa as páginas para `base/local/` e gera
  `base/local/chunks_govbr.jsonl` na sua máquina. Elas podem ter mudado desde 07/11/2026; o hash
  original de cada uma está em `base/fontes.csv`, para comparação.
- Os servidores da ANEEL (`www2.aneel.gov.br`, `git.aneel.gov.br`) bloqueiam clientes HTTP com um
  desafio da Cloudflare (erro 403). Os arquivos versionados foram obtidos por navegador e
  importados com `scripts\importar_download_navegador.py`, que mantém os bytes e o hash.
- `scripts\qc_amostra.py` sorteia 20 trechos para controle de qualidade.

## Avaliação

```powershell
# Busca: recall@k, ablação e limiar do portão de recusa (Fase 4)
.\.venv\Scripts\python.exe scripts\avaliar_recuperacao.py
# Geração: C0, C1 ou C2 (com --correcoes M para o sistema oficial) sobre um conjunto
.\.venv\Scripts\python.exe scripts\avaliar_geracao.py rodar --config C2 --conjunto dev
.\.venv\Scripts\python.exe scripts\avaliar_geracao.py rodar --config C2 --conjunto dev --correcoes M --num-ctx 6144
.\.venv\Scripts\python.exe scripts\avaliar_geracao.py resumo
# Placar com as conferências manuais
.\.venv\Scripts\python.exe scripts\montar_placar.py
```

- Conjuntos: `dev` (24 perguntas), `test` (36, placar oficial), `test2` e `test3` (24 cada),
  `calibracao` (45, comportamento de recusa), `injecao` (5 tentativas de prompt injection) e
  `dinamicas_extra` (13, agenda). Os de teste estão congelados com hash (`avaliacao/*.lock`).
- `test`, `test2` e `test3` rodam **uma única vez** por configuração: o script recusa repetir se a
  saída já existe em `avaliacao/runs/geracao/`. Para refazer do zero, apague as saídas, ciente de
  que o resultado deixa de ser uma medição única.
- O Ollama não é determinístico bit a bit entre execuções, mesmo com temperatura 0 e semente 42:
  algumas respostas mudam de redação.
- As saídas versionadas em `avaliacao/runs/geracao/` trazem as citações de páginas gov.br trocadas
  por hash; as completas ficam em `avaliacao/runs/local/` (fora do git).
- As conferências manuais estão em `avaliacao/revisao/` e as decisões, em
  `avaliacao/revisao/decisoes.md`.

Para executar os notebooks, ative o venv antes (`.\.venv\Scripts\Activate.ps1`), para que o kernel
use as bibliotecas do projeto:

```powershell
jupyter nbconvert --to notebook --execute --inplace notebooks\05_placar_e_analise.ipynb
```

## Serviço e interface de teste

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.servico.app:app --port 8000
```

Abra `http://localhost:8000`. Os modelos carregam em segundo plano (cerca de 30 s; o selo
"assistente pronto" indica o fim). A página permite escolher a configuração (C0, C1, C2 ou C2M, a
recomendada), a origem (texto ou voz) e comparar a resposta lado a lado com o C0.

| Rota | O que faz |
|---|---|
| `POST /v1/perguntar` | `{"pergunta": "...", "config": "C2M", "origem": "texto"}`; devolve resposta, fontes e trechos |
| `GET /v1/configs` | configurações disponíveis |
| `GET /health` | status e se os modelos já carregaram |
| `GET /metrics` | contagens e latência desde a partida, sem texto de pergunta |
| `GET /docs` | documentação interativa |

- CPF, CNPJ, telefone, e-mail, CEP e números longos são mascarados antes de chegar ao modelo.
- O log (`logs/servico.jsonl`) guarda um hash da pergunta, a configuração, a latência, se houve
  recusa, os ids das fontes e os tipos de dado mascarados, sem o texto da pergunta nem da resposta.
- A agenda de paradas usada pelo C2 roda no mesmo processo (não é preciso subir a porta 8001).

### Em container (Docker)

Com o Ollama rodando no Windows, a base e os índices gerados e os modelos do Hugging Face já
baixados (basta ter rodado o `check_env.py` e o serviço uma vez):

```powershell
docker compose up --build      # e abra http://localhost:8000
```

A imagem (cerca de 13 GB, por causa do PyTorch com CUDA) tem só o código e as dependências. A
pasta `base/` e o cache do Hugging Face entram como volumes, então nenhuma página gov.br vai para
a imagem; o container fala com o Ollama do host por `host.docker.internal`. Com GPU (Docker Desktop
com WSL 2), o reranker roda nela; sem GPU, roda na CPU. No Docker Desktop, a opção *Resources >
Advanced > Disk image location* permite guardar as imagens fora do disco C.

## API de paradas programadas (simulada)

```powershell
.\.venv\Scripts\python.exe scripts\calibrar_paradas.py   # opcional: refaz a calibração (baixa 272 MB da ANEEL)
.\.venv\Scripts\python.exe scripts\gerar_paradas.py      # gera dados/paradas_simuladas.csv e o SQLite
.\.venv\Scripts\python.exe -m uvicorn src.paradas_api.app:app --port 8001
```

- Leitura: `GET /paradas?bairro=Mooca&data=2026-11-10`, `GET /bairros?q=jardim`, `GET /health`.
  A documentação interativa fica em `http://localhost:8001/docs`.
- Escrita (`POST /paradas`, `PATCH /paradas/{id}`) exige o header `X-API-Key` igual a
  `PARADAS_API_KEY` do `.env`. Sem chave configurada, ou com o valor de exemplo, a escrita fica
  desligada.
- Os dados são **simulados**, calibrados com interrupções programadas reais da Enel SP (dados
  abertos da ANEEL) e com os 96 distritos do município (IBGE). Detalhes em
  [`docs/dados_simulados.md`](docs/dados_simulados.md).

## Estrutura

```
base/        manifesto, documentos oficiais, trechos (chunks) e índices (gerados)
avaliacao/   conjuntos de teste congelados, saídas, conferências, placar e decisões
notebooks/   01 base, 02 busca, 03 geração, 04 agente, 05 placar, 06 cinco erros, 07 melhorias
src/         ingestão, RAG (busca, prompt, validador), agente, API de paradas, serviço, avaliação
scripts/     construção da base, índices, avaliação, placar e utilitários
tests/       pytest (rodam no CI sem GPU e sem Ollama)
docs/        tarefa da IA, ficha técnica, lista de documentos, dados simulados, LGPD, relatório
```

## Limitações

- Cerca de 1 em cada 5 respostas do sistema oficial ainda afirma algo falso, em geral um prazo de
  outra situação, uma regra geral sem a exceção ou uma regra revogada. A citação permite conferir.
- A base é um recorte de 19 documentos, consultados em 07/11/2026; normas mudam.
- A agenda de paradas é simulada: o assistente indica a página oficial da distribuidora para
  confirmar.
- Os conjuntos de teste são pequenos (18 a 26 perguntas respondíveis), por isso os intervalos de
  confiança são largos.

## Privacidade e uso responsável

O serviço não precisa de dados pessoais: mascara o que identificar e não guarda o texto das
perguntas. As regras completas estão em
[`docs/lgpd_e_ia_responsavel.md`](docs/lgpd_e_ia_responsavel.md).

**Aviso:** orientação informativa; não substitui o atendimento da distribuidora, da ANEEL ou de um
advogado.
