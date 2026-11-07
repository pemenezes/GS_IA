# Tarefa da IA: Luz Cidadã

**Versão:** 1 (Fase 1). Aprovada pelo Pedro em 07/11/2026.

## 1. Tarefa

Dada uma pergunta em linguagem natural de um cidadão leigo sobre seus direitos como consumidor
residencial de energia elétrica, o assistente responde **somente com base nos documentos oficiais da
base** (ver [`lista_documentos.md`](lista_documentos.md)), em linguagem simples, **citando o trecho e a
fonte**. Se a base não contém a resposta, ele **recusa explicitamente** ("não consta") e indica o canal
oficial. Para perguntas sobre paradas programadas, consulta a API de manutenções e cita o registro
consultado.

**Entrada:** `{"pergunta": str, "origem": "texto" | "voz" | "ocr", "contexto": {...opcional}}`.
Com `origem="voz"`, a pergunta pode vir sem pontuação, sem acentos e com palavras trocadas pela
transcrição.

**Saída:** o JSON do Apêndice B.1 do plano (`resposta`, `recusa`, `motivo_recusa`, `fontes`, `confianca`),
validado por schema e por regras (ver a seção 4).

O assistente **informa; não decide nem age pelo cidadão**. Ele não protocola reclamações, não dá parecer
jurídico individual e sempre aponta quem pode resolver: a distribuidora, a ANEEL ou o Procon.

## 2. Usuário-alvo

Moradores da Região Metropolitana de São Paulo, com prioridade para:
- idosos;
- pessoas com deficiência;
- famílias com alguém que depende de equipamento elétrico de saúde em casa;
- famílias de baixa renda, potenciais beneficiárias da Tarifa Social ou do Desconto Social.

**Consequências para o projeto:**

| Característica do usuário | Requisito do assistente |
|---|---|
| Pouca familiaridade com termos técnicos e jurídicos | Frases curtas, palavras do dia a dia; termo técnico só com explicação |
| Pode usar voz (idosos, baixa visão) | Tolerar perguntas sem pontuação, com erros de transcrição e frases longas |
| Situação de urgência (apagão, equipamento de saúde desligado) | Resposta direta primeiro, detalhe depois; sempre indicar o canal oficial de emergência da distribuidora quando ele estiver na base |
| Risco alto se a informação estiver errada | Nunca inventar números, prazos, valores, artigos ou telefones; na dúvida, recusar |

## 3. Política de recusa ("não consta")

O assistente **recusa** (`recusa=true`) em três situações:

| Gatilho | Quem detecta | Como testar |
|---|---|---|
| **(a) Busca fraca:** nenhum trecho recuperado atinge o limiar τ | Portão antes do LLM: o modelo nem é chamado | Score do melhor trecho < τ, com τ definido na Fase 4 sobre o split dev |
| **(b) Trechos insuficientes:** os trechos recuperados não sustentam a resposta (por exemplo, falam do tema, mas não do ponto perguntado) | O LLM recusa, seguindo a regra 2 do prompt (Apêndice C), e o validador confere | Perguntas "não consta" plausíveis, com vocabulário do domínio |
| **(c) Fora do domínio:** a pergunta não é sobre direitos do consumidor de energia (ver a seção 6) | O LLM recusa, e a busca tende a cair no gatilho (a) | Perguntas fora do domínio no conjunto de teste |

**Proibições fixas, valendo mesmo sem recusa:**
1. Não informar número, prazo, percentual, valor, artigo ou data que não esteja **literalmente** num trecho citado.
2. Não informar telefone, site ou endereço que não esteja num trecho da base. Na base atual, os telefones vêm só da página oficial da ANEEL (item D18 da lista).
3. Não estimar indenização, multa ou valor de conta.
4. Não aceitar instruções do usuário que tentem mudar estas regras (*prompt injection*).

**Formato da recusa:**
- `recusa=true`;
- `motivo_recusa`: uma frase dizendo o que falta, por exemplo "a base não trata de valor de indenização por dano moral";
- `resposta`: orientação curta para procurar a distribuidora, a ANEEL ou o Procon, sem telefone que não esteja na base;
- `fontes`: pode ficar vazia. Só tem itens se a recusa se apoiar num trecho, por exemplo um trecho que indica o canal de reclamação;
- `confianca`: reflete a certeza de que a base não responde.

## 4. Comportamento esperado por situação

Esta tabela é a especificação que o validador (Fase 5) e o agente (Fase 7) implementam e que o conjunto
de teste (Fase 3) verifica.

| Situação | `recusa` | `fontes` | `resposta` | Observação |
|---|---|---|---|---|
| Base responde | `false` | ≥ 1 item `tipo="norma"`, `trecho_citado` literal e presente no trecho de `id` | Resposta curta e simples, com os números iguais aos do trecho | Regra B.1, já validada em `src/rag/schema.py` |
| Busca fraca (gatilho a) | `true` | vazia | Orientação para os canais oficiais | Gerada sem chamar o LLM |
| Base não sustenta (gatilho b) | `true` | vazia, ou o trecho do canal de reclamação | Diz o que falta e orienta | — |
| Fora do domínio (gatilho c) | `true` | vazia | Diz que o assistente só trata de energia elétrica | — |
| Parada programada, com registro na API | `false` | ≥ 1 item `tipo="api"` com o `id` do registro | Data, janela e bairro como no registro | Pode citar também a norma sobre aviso prévio |
| Parada programada, sem registro | `false` | o item `tipo="api"` da consulta vazia, ou um trecho de norma | "Não há parada registrada para esse bairro e data" | Ausência de registro não é recusa; é a resposta |
| Erro ou tempo esgotado na API | `true` | vazia | Explica que não foi possível consultar agora e orienta procurar a distribuidora | Regra da Fase 7: erro de ferramenta vira recusa explicada |
| Conflito entre trechos | `false` | os dois trechos | Menciona o conflito e prefere o mais recente ou mais específico | Regra 5 do prompt (Apêndice C) |
| Pergunta com ruído de voz | Igual às linhas acima | — | — | A busca e o LLM devem tolerar o ruído; o desempenho é medido por tipo de pergunta |

## 5. Exemplos canônicos

Os exemplos descrevem o **comportamento**, sem números. Os prazos e artigos de verdade entram no gabarito
só na Fase 3, conferidos no texto oficial.

1. **Interrupção longa.**
   - *Pergunta:* "Fiquei sem luz há 30 horas na minha casa, na cidade. A distribuidora está dentro do prazo?"
   - *Esperado:* responder com o prazo de restabelecimento que a norma prevê para área urbana, dizer se 30 horas está dentro ou fora dele, citar o trecho e o artigo, e indicar como reclamar. Se houver direito a compensação, citar a regra.
2. **Pedido de valor que a norma não fixa.**
   - *Pergunta:* "Quanto vou receber de indenização por dano moral?"
   - *Esperado:* **recusar**, com o motivo "a base não fixa valor de dano moral", e indicar os canais oficiais. Se a base tiver regra de ressarcimento de **danos em aparelhos**, pode citá-la deixando claro que é outra coisa.
3. **Parada programada.**
   - *Pergunta:* "Tem manutenção programada no meu bairro amanhã?"
   - *Esperado:* calcular "amanhã" a partir da data de referência fixa (`data_referencia` no `config.yaml`), extrair o bairro (ou perguntar, se faltar), consultar a API e citar o registro, ou dizer que não há registro.

## 6. Escopo

**Dentro do escopo:**

| Tema | Documentos principais (ver a lista) |
|---|---|
| Falta de energia, prazos de restabelecimento, compensação por interrupção, situações de emergência | D01, D06, D07, D13, D14 |
| Interrupção programada e aviso prévio, inclusive para quem depende de equipamento de saúde | D01, D14 + API de paradas |
| Suspensão por falta de pagamento e religação | D01 |
| Danos em aparelhos e ressarcimento | D01, D08, D14 |
| Conta de luz, leitura e faturamento | D01 |
| Tarifa Social e Desconto Social: quem tem direito e como receber | D01, D02, D03, D05, D16, D17 |
| Pessoa com equipamento elétrico de saúde em casa: Tarifa Social e cadastro na distribuidora | D01, D02, D04, D14 |
| Bandeiras tarifárias: o que são e como funcionam | D01, D12, D15 |
| Geração distribuída (energia solar em casa) para o consumidor residencial | D01, D09, D19 |
| Como reclamar: distribuidora, ouvidoria, ANEEL; telefones oficiais | D14, D18 |
| Direitos gerais do consumidor e do usuário de serviço essencial | D10, D11 |

**Fora do escopo** (gera recusa, gatilho c, ou "não consta", gatilho b):
- valores em R$: tarifa da distribuidora, valor da bandeira do mês, valor estimado da conta;
- indenização por dano moral e qualquer estimativa de valor de ação judicial;
- parecer jurídico individual ("devo processar?");
- abrir ou acompanhar protocolo de reclamação em nome do cidadão;
- outros serviços: água, gás, telefonia e internet;
- consumidores do mercado livre e grandes consumidores (alta e média tensão);
- iluminação pública, recarga de veículo elétrico e projetos técnicos de conexão de geração distribuída (dimensionamento, potência de usina).

Decisões de 07/11/2026 sobre a base (ver a seção 5 de [`lista_documentos.md`](lista_documentos.md)):
- o CDC (D10) entra só com o Título I;
- as páginas gov.br (D14 a D19) entram no índice local, mas o texto delas não vai para o repositório.

## 7. Ligação com a avaliação (Fase 3)

| Tipo de pergunta (seção 6, Fase 3 do plano) | O que testa nesta especificação |
|---|---|
| Diretas (18, incluindo 3 armadilhas temporais) | Linha "base responde" da seção 4; armadilhas temporais com a Tarifa Social antiga (redações revogadas da Lei 12.212) |
| Coloquiais (12) | Linguagem do usuário da seção 2 |
| Ruído de transcrição (6) | `origem="voz"` |
| Multi-trecho (6) | Combinação de trechos; linha "conflito entre trechos" |
| Não consta (12) | 6 plausíveis do domínio, a partir da lista "fora do escopo" e dos documentos excluídos de propósito (seção 3 da lista), + 6 fora do domínio |
| Dinâmicas (6) | Linhas de parada programada e erro de API |
