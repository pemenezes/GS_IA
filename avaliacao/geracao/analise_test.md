# Falhas do C1 no test (Fase 5): pré-classificação para a conferência manual

**Status:** pré-classificação minha, feita depois da medição única no test (08/11/2026). Nada foi
ajustado por causa dela. A conferência humana do test (Fase 8) confirma ou corrige cada linha, e
os 5 erros da Fase 8 saem daqui.

Medição automática do C1 (qwen3 4B instruct) nas 26 respondíveis do test: acurácia **10/26**,
citação correta **12/20** respostas, suspeita automática de alucinação **0/20**, recusa indevida
**6/26**. As 16 perguntas sem acerto automático se dividem assim:

## 1. Resposta provavelmente certa, reprovada pela comparação literal (4)

A comparação procura o fato-chave escrito como no gabarito, que usa a redação da norma.

| Caso | Resposta (resumo) | Fato-chave procurado |
|---|---|---|
| T-002 | Não pode cortar na sexta-feira, nem sábado, domingo, véspera de feriado e feriado | "vedada às sextas-feiras" e "8 horas às 18 horas" (o horário não foi citado) |
| T-015 | Bandeira verde: condições boas de geração e nenhum acréscimo na conta | "não implicando acréscimo tarifário" |
| T-018 | Sim, o CDC exige serviço contínuo (citou a REN 1.000, não o art. 22 do CDC) | "contínuos" |
| T-026 | Média dos valores faturados nos últimos 12 meses | "média aritmética" |

## 2. Erro real que a métrica automática não detecta (5)

A regra (f) só confere se o número existe nos trechos. Nestes casos, o número existe, mas o
modelo o usou para a situação errada, ou o escreveu por extenso.

| Caso | O que o C1 disse | O certo (gabarito) | Gold no top-3? |
|---|---|---|---|
| T-011 | Renda de até 3 salários mínimos | Até meio salário mínimo por pessoa (3 salários mínimos é a regra do caso com equipamento de saúde) | não |
| T-021 | Aviso com "três dias" de antecedência | 15 dias | não |
| T-033 | Aviso com 5 dias úteis | 15 dias | não |
| T-028 | "A bandeira vermelha não é uma taxa a mais, você não paga mais" | Há adicional, destacado na fatura | sim |
| T-037 | Interrupção de 30 horas tratada como "dano elétrico" | Compensação pelo limite do indicador DISE | não |

Quatro dos cinco erros vêm de uma busca que não trouxe o trecho certo: o modelo respondeu com o
trecho mais parecido, em vez de recusar. É a categoria 6 da taxonomia (citação que não sustenta a
resposta), com a 5 (número aplicado à situação errada).

## 3. Recusa indevida (7)

| Caso | Quem recusou | Observação |
|---|---|---|
| T-024, T-036 | portão | BPC e desconto (T-036 é a versão de voz) |
| T-032, T-034 | portão | voz, com erros de grafia ("lus", "quantu") |
| T-040 | portão | multi-trecho (respirador e manutenção programada) |
| T-007 | LLM | gold no top-3 (revogação pela REN 1.137); o modelo disse que faltava informação |
| T-039 | LLM, em parte | deu o prazo do resultado (15 dias) e disse que o do pagamento não estava nos trechos |

## 4. Acerto automático a conferir (1)

| Caso | Observação |
|---|---|
| T-003 | Tem o fato-chave ("72 horas"), mas acrescenta "3 dias úteis para residências comuns, desde que o consumidor tenha feito o cadastro", que o gabarito não sustenta |

## C0 no mesmo test

O C0 acertou 0 de 26. Recusou 18 das 26 respondíveis, e 14 dessas recusas afirmam que a regra não
existe. Exemplos: T-024 ("Não há desconto oficial na conta de luz para aposentados ou
beneficiários do BPC") e T-030 ("Não há lei que obrigue a empresa de energia a pagar por danos a
aparelhos"). Quando respondeu, inventou prazos (por exemplo, "72 horas de aviso" para corte por
dívida, em T-021 e T-033, quando o certo é 15 dias).
