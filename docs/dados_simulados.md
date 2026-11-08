# Dados simulados: API de paradas programadas

> **Situação:** rascunho da Fase 3, só com a especificação dos registros-âncora. A justificativa da
> simulação, o gerador e as limitações entram na Fase 6.

## Por que há registros-âncora

As 6 perguntas dinâmicas do conjunto de teste (`avaliacao/teste.jsonl`, tipo `dinamica`) dependem
do que a API de paradas devolve. Para o gabarito não depender de sorteio, o gerador da Fase 6
**sempre** cria os registros abaixo, com id fixo, além dos cerca de 300 eventos aleatórios gerados
com semente 42. Ele também **garante a ausência** de eventos nas combinações de bairro e data
listadas.

Data de referência dos testes: **terça-feira, 10/11/2026** (`data_referencia` no `config.yaml`).
Os horários são locais (America/Sao_Paulo); no banco eles ficam em UTC.

## Registros-âncora (sempre presentes)

| id | Distrito | Bairro | Data | Início | Fim | Tipo | Status | Pergunta |
|---|---|---|---|---|---|---|---|---|
| PAR-ANC-01 | Vila Mariana | Vila Mariana | 2026-11-11 | 09:00 | 13:00 | manutencao_programada | agendada | T-055 |
| PAR-ANC-02 | Mooca | Mooca | 2026-11-10 | 13:00 | 17:00 | obra | agendada | T-056 |
| PAR-ANC-03 | Santana | Santana | 2026-11-13 | 08:00 | 12:00 | poda | agendada | T-057 |

## Ausências garantidas

O gerador não cria nenhum evento, em nenhum status, para:

| Bairro | Data | Pergunta |
|---|---|---|
| Butantã | 2026-11-11 | T-058 |
| Lapa | 2026-11-13 | T-059 |

## Ambiguidade garantida

Existem pelo menos três bairros que começam com "Jardim" (por exemplo Jardim Paulista, Jardim
Ângela e Jardim São Luís). Assim, "no Jardim", sem complemento, é ambíguo, e o agente deve pedir o
nome completo (T-060).
