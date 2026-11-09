# Conferência manual do test (Fase 8)

**Para:** Pedro. **Itens:** 51. Cada item traz a pergunta, o gabarito que você aprovou na Fase 3,
a resposta do sistema, as fontes citadas e a **minha pré-classificação**. Basta confirmar ou
corrigir. Você pode responder no chat só com as discordâncias, por exemplo: "C2 T-018: correta".

**Critérios**
- **Veredito:** ✅ correta (responde o que foi perguntado, de acordo com o gabarito); 🟡 parcial
  (o núcleo está certo, mas falta algo pedido ou há um detalhe duvidoso); ❌ incorreta (o núcleo
  está errado ou não responde).
- **Afirma algo falso?** Sim se a resposta **ou o trecho citado** contém uma afirmação falsa
  (prazo, valor, regra ou citação inventada). É a medida manual de alucinação.
- **Recusas do C0:** a recusa **nega uma regra que existe** ("não há prazo", "não há desconto")?

Ficam de fora, porque já estão medidas sem ambiguidade:
- as recusas de perguntas respondíveis no C1 e no C2, que contam como recusa indevida;
- as perguntas "não consta" e fora do domínio, todas recusadas;
- as dinâmicas, conferidas pelos registros da agenda.

As respostas do C1 iguais às do C2 não se repetem: só entram as 5 que diferem.

> Nesta versão, as citações de páginas gov.br aparecem como hash (licença CC BY-ND). A versão completa está em `avaliacao/runs/local/conferencia_test_completa.md`.



## 1. C2: respostas dadas às perguntas respondíveis

### C2 · T-002 (direta)

**Pergunta:** A distribuidora pode cortar a energia por falta de pagamento numa sexta-feira?

**Gabarito:** Não. O corte por inadimplemento só pode ser feito das 8 às 18 horas e é proibido às sextas-feiras, sábados, domingos, vésperas de feriado e feriados. *(fatos-chave: vedada às sextas-feiras, 8 horas às 18 horas)*

**Resposta do C2:** Não, a distribuidora não pode cortar a energia por falta de pagamento numa sexta-feira. A Resolução 1000/2021 da ANEEL proíbe a suspensão de energia nas sextas-feiras, sábados, domingos, feriados ou vésperas de feriados.

**Fontes citadas:**

  - `D14-q10`: [página gov.br; sha256 19471325d0e0]

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*Responde a sexta-feira; não cita o horário 8h–18h, que a pergunta não pediu.*

### C2 · T-003 (direta)

**Pergunta:** Com quanta antecedência a distribuidora precisa avisar uma residência comum sobre uma interrupção programada?

**Gabarito:** Pelo menos 72 horas antes do início da interrupção, pela página da distribuidora na internet e por outros meios de divulgação. *(fatos-chave: 72 horas)*

**Resposta do C2:** A distribuidora precisa avisar uma residência comum com antecedência mínima de 3 dias úteis, desde que o consumidor tenha feito o cadastro na distribuidora para receber esse tipo de aviso.

**Fontes citadas:**

  - `D07-s8.2-item196`: unidades consumidoras atendidas em tensão inferior a 69 kV que prestem serviço essencial: aviso por meio de documento escrito e personalizado, com antecedência mínima de 5 dias úteis em relação à data da interrupção; unidades consumidoras atendidas em tensão superior a 2,3 kV e inferior a 230 kV com demanda contratada inferior a 500 kW e unidades consumidoras atendidas em tensão igual ou inferiora

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Pelo item 196 citado, '3 dias úteis com cadastro' vale para unidades em média tensão com demanda abaixo de 500 kW e para unidades comerciais ou industriais em baixa tensão; residência comum fica em 'outras unidades', com 72 horas.*

### C2 · T-005 (direta)

**Pergunta:** Se a distribuidora ultrapassa os limites de interrupção da minha casa, em quanto tempo a compensação deve aparecer na fatura?

**Gabarito:** O crédito da compensação deve vir na fatura em até 2 meses após o período de apuração. *(fatos-chave: em até 2 meses após o período de apuração)*

**Resposta do C2:** A compensação deve aparecer na fatura em até 2 meses após o período de apuração.

**Fontes citadas:**

  - `D07-s8.2-item219`: No caso de violação do limite de continuidade individual dos indicadores DIC, FIC, DMIC, DICRI e DISE a distribuidora deve calcular a compensação ao consumidor ou central geradora, inclusive aqueles conectados em DIT, e efetuar o crédito na fatura apresentada em até 2 meses após o período de apuração.

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

### C2 · T-006 (direta)

**Pergunta:** Qual é o prazo para pedir à distribuidora o ressarcimento de um aparelho danificado por problema na rede?

**Gabarito:** O consumidor tem até 5 anos, contados da data provável do dano, para pedir o ressarcimento. *(fatos-chave: 5 anos)*

**Resposta do C2:** O prazo para pedir o ressarcimento é de cinco anos, a contar da data provável da ocorrência do dano no equipamento.

**Fontes citadas:**

  - `D14-q09`: [página gov.br; sha256 7b80a9c579ac]

  - `D01-art602-p1`: O consumidor tem até 5 anos, a contar da data provável da ocorrência do dano elétrico no equipamento, para solicitar o ressarcimento à distribuidora, devendo informar, no mínimo, os seguintes itens: I - número de identificação da unidade consumidora; II - data e horário prováveis da ocorrência do dano; III - relato do problema apresentado pelo equipamento elétrico; IV - descrição e características

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

### C2 · T-008 (direta)

**Pergunta:** Qual é o custo de disponibilidade mínimo cobrado de uma casa com ligação monofásica?

**Gabarito:** O custo de disponibilidade de uma ligação monofásica equivale a 30 kWh. *(fatos-chave: 30 kWh)*

**Resposta do C2:** O custo de disponibilidade mínimo cobrado de uma casa com ligação monofásica é de 30 kWh.

**Fontes citadas:**

  - `D01-art291`: I - 30 kWh, se monofásico ou bifásico a dois condutores;

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

### C2 · T-009 (direta)

**Pergunta:** Se a distribuidora não consegue fazer a leitura do medidor por causa de uma calamidade pública, como a conta é calculada?

**Gabarito:** Pela média dos valores faturados nos 12 últimos ciclos, informando isso na fatura, com acerto depois que a situação terminar. *(fatos-chave: média aritmética dos valores faturados nos 12 últimos ciclos de faturamento)*

**Resposta do C2:** Se a distribuidora não consegue fazer a leitura do medidor por causa de uma calamidade pública, a conta é calculada pela média aritmética dos valores faturados nos 12 últimos ciclos de faturamento. Quando a leitura for possível novamente, a diferença será ajustada nas faturas seguintes.

**Fontes citadas:**

  - `D14-q20`: [página gov.br; sha256 8ef7ab19792b]

  - `D01-art321`: Caso a distribuidora não possa efetuar a leitura em decorrência de situação de emergência, de calamidade pública ou por motivo de força maior, deve observar as seguintes disposições: I - faturar pela média aritmética dos valores faturados nos 12 últimos ciclos de faturamento, observado o § 1º do art. 288, desde que mantido o fornecimento regular de energia elétrica à unidade consumidora;

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

### C2 · T-011 (direta)

**Pergunta:** Qual é o critério de renda do CadÚnico para ter direito à Tarifa Social de Energia Elétrica?

**Gabarito:** Família inscrita no CadÚnico com renda mensal por pessoa de até meio salário mínimo (ou ter na casa quem recebe o BPC). *(fatos-chave: meio salário mínimo nacional)*

**Resposta do C2:** O critério de renda é ter renda mensal de até 3 (três) salários mínimos.

**Fontes citadas:**

  - `D02-art2-p2`: § 1º Excepcionalmente, será também beneficiada com a Tarifa Social de Energia Elétrica a unidade consumidora habitada por família inscrita no CadÚnico e com renda mensal de até 3 (três) salários mínimos, que tenha entre seus membros portador de doença ou patologia cujo tratamento ou procedimento médico pertinente requeira o uso continuado de aparelhos, equipamentos ou instrumentos que, para o seu橢

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*3 salários mínimos é o critério excepcional (equipamento de saúde); o geral é meio salário mínimo por pessoa.*

### C2 · T-013 (direta)

**Pergunta:** Para uma família da tarifa social (baixa renda), quanto tempo depois do vencimento da conta a energia pode ser cortada por falta de pagamento?

**Gabarito:** Precisa haver pelo menos 30 dias entre o vencimento da fatura e o corte. *(fatos-chave: 30 dias)*

**Resposta do C2:** Para uma família da tarifa social (baixa renda), a energia pode ser cortada apenas após pelo menos 30 dias do vencimento da conta.

**Fontes citadas:**

  - `D01-art358`: Art. 358. A suspensão por inadimplemento para a unidade consumidora classificada nas subclasses residencial baixa renda deve ocorrer com intervalo de pelo menos 30 dias entre a data de vencimento da fatura e a data da efetiva suspensão.

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

### C2 · T-015 (direta)

**Pergunta:** O que significa a bandeira tarifária verde na conta de luz?

**Gabarito:** Indica condições favoráveis de geração e não traz acréscimo na tarifa. *(fatos-chave: não implicando acréscimo tarifário)*

**Resposta do C2:** A bandeira tarifária verde significa que as condições de geração de energia são boas e não há acréscimo na conta de luz.

**Fontes citadas:**

  - `D12-s3-item8`: A Bandeira Tarifária Verde indica condições favoráveis de geração de energia, não implicando acréscimo tarifário.

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*A métrica automática reprovou só pela redação ('não há acréscimo').*

### C2 · T-018 (direta)

**Pergunta:** O Código de Defesa do Consumidor obriga a empresa de energia a fornecer o serviço de forma contínua?

**Gabarito:** Sim. Concessionárias de serviços essenciais devem prestar serviços adequados, eficientes, seguros e contínuos (art. 22 do CDC). *(fatos-chave: contínuos)*

**Resposta do C2:** Sim, o Código de Defesa do Consumidor obriga a empresa de energia a fornecer o serviço de forma contínua, pois o serviço adequado inclui a continuidade, conforme estabelecido na Resolução ANEEL nº 1.000/2021.

**Fontes citadas:**

  - `D01-art4`: Art. 4º A distribuidora é responsável pela prestação de serviço adequado ao consumidor e demais usuários e pelas informações necessárias à defesa de interesses individuais, coletivos ou difusos. § 1º Serviço adequado é o que satisfaz as condições de regularidade, continuidade, eficiência, segurança, atualidade, generalidade, cortesia na sua prestação e modicidade das tarifas. § 2º A atualidadecomp

**Pré-classificação:** 🟡 parcial · afirma algo falso? **nao**

*Conclusão certa, mas fundamenta na REN 1.000 (art. 4º) e não no art. 22 do CDC, que a pergunta cita.*

### C2 · T-020 (coloquial)

**Pergunta:** Cortaram a luz da minha casa mas eu estava com tudo pago, foi erro deles. Quanto tempo eles têm pra voltar com a luz?

**Gabarito:** Na suspensão indevida, a religação deve ocorrer em até 4 horas, e a distribuidora deve creditar uma compensação. *(fatos-chave: 4 horas)*

**Resposta do C2:** Eles têm 4 horas para voltar com a luz.

**Fontes citadas:**

  - `D14-q11`: [página gov.br; sha256 21af683ec3f5]

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*4 horas; não menciona o crédito da compensação, que a pergunta não pediu.*

### C2 · T-021 (coloquial)

**Pergunta:** Chegou um papel dizendo que vão cortar minha luz por causa de conta atrasada. Eles podem cortar sem me avisar antes? Quantos dias de aviso eu tenho?

**Gabarito:** Não. No caso de inadimplemento, a notificação deve ser feita com pelo menos 15 dias de antecedência. *(fatos-chave: 15 dias)*

**Resposta do C2:** Não, eles não podem cortar sua luz sem avisar. A distribuidora precisa avisar com no mínimo três dias de antecedência, se for por falta de pagamento. Se você quitar a dívida no momento do corte, a energia não pode ser cortada.

**Fontes citadas:**

  - `D14-q10`: [página gov.br; sha256 fa7fbcaeba38]

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*'Três dias' de aviso; o certo é 15 dias. A frase sobre quitar no momento do corte também não está no gabarito.*

### C2 · T-022 (coloquial)

**Pergunta:** Minha geladeira queimou quando a luz voltou e eu guardo insulina nela. Depois que eu reclamar, quanto tempo a empresa tem pra vir ver a geladeira?

**Gabarito:** Para equipamento que guarda alimentos perecíveis ou medicamentos, a verificação deve ser feita em até um dia útil. *(fatos-chave: um dia útil)*

**Resposta do C2:** A distribuidora deve vir ver a geladeira em até um dia útil, porque você guarda insulina nela e é um equipamento usado para acondicionamento de medicamentos.

**Fontes citadas:**

  - `D08-s9.2-item37`: 37. O prazo para a Verificação é de 10 dias após a data da Solicitação. 37.1. Se o equipamento objeto da solicitação de ressarcimento de dano elétrico for utilizado para o acondicionamento de alimentos perecíveis ou de medicamentos, o prazo para Verificação é de um dia útil.

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

### C2 · T-026 (coloquial)

**Pergunta:** Com a enchente o pessoal da empresa não conseguiu ler meu relógio de luz e a conta veio estimada. Como é que eles calculam esse valor?

**Gabarito:** Pela média dos valores faturados nos 12 últimos ciclos, com aviso na fatura e acerto quando a situação terminar. *(fatos-chave: média aritmética)*

**Resposta do C2:** Eles calculam o valor a partir da média dos valores faturados da sua unidade nos últimos 12 meses, conforme a Resolução 1.000/2021 da ANEEL.

**Fontes citadas:**

  - `D14-q20`: [página gov.br; sha256 8ef7ab19792b]

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*A métrica automática reprovou só pela redação ('média' sem 'aritmética').*

### C2 · T-028 (coloquial)

**Pergunta:** Minha conta veio com bandeira vermelha. Isso é uma taxa a mais que vão me cobrar?

**Gabarito:** Sim: nas bandeiras amarela e vermelha há um adicional, que deve vir destacado na fatura; na bandeira verde não há acréscimo. *(fatos-chave: destacados nas faturas)*

**Resposta do C2:** Não. A bandeira vermelha não é uma taxa a mais. É apenas uma forma de mostrar o custo real da energia no momento em que você consome. O valor já estava na sua conta, mas agora está mais claro.

**Fontes citadas:**

  - `D15-q02`: [página gov.br; sha256 4ab00ebaa6f5]

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Diz que a bandeira vermelha não é cobrança a mais; há adicional, destacado na fatura.*

### C2 · T-030 (coloquial)

**Pergunta:** Faz dois anos que minha TV queimou por causa de uma queda de energia. Ainda dá tempo de pedir pra empresa pagar?

**Gabarito:** Sim. O prazo para pedir ressarcimento é de até 5 anos da data provável do dano. *(fatos-chave: 5 anos)*

**Resposta do C2:** Sim, ainda dá tempo. Você tem até cinco anos para pedir o reembolso. Como já passaram dois anos, ainda há tempo, desde que a queda de energia tenha sido provável e a TV tenha sido conectada à instalação da casa.

**Fontes citadas:**

  - `D14-q09`: [página gov.br; sha256 7b80a9c579ac]

  - `D01-art602-p1`: O consumidor tem até 5 anos, a contar da data provável da ocorrência do dano elétrico no equipamento, para solicitar o ressarcimento à distribuidora, devendo informar, no mínimo, os seguintes itens: I - número de identificação da unidade consumidora; II - data e horário prováveis da ocorrência do dano; III - relato do problema apresentado pelo equipamento elétrico; IV - descrição e características

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*Redação estranha no fim ('desde que a queda tenha sido provável'), mas o prazo de 5 anos está certo.*

### C2 · T-033 (ruido)

**Pergunta:** chegou um papel dizendo que vao cortar minha lus por causa de conta atrasado eles podem cortar sem me avisar antes quantos dias aviso eu tenho

**Gabarito:** Não. No caso de inadimplemento, a notificação deve ser feita com pelo menos 15 dias de antecedência. *(fatos-chave: 15 dias)*

**Resposta do C2:** Não, eles não podem cortar sua luz sem aviso. A ANEEL diz que, se houver interrupção por dívidas, a distribuidora deve avisar com antecedência mínima de 5 dias úteis. Se você recebeu um papel dizendo que vai cortar a luz, é importante verificar se há cadastro de pessoas com dependência de energia elétrica. Caso contrário, entre em contato com a distribuidora para esclarecer.

**Fontes citadas:**

  - `D14-q11`: [página gov.br; sha256 6ba14f1ce622]

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*'5 dias úteis'; o certo é 15 dias. O trecho citado é sobre corte indevido, não sobre aviso de corte.*

### C2 · T-037 (multi_trecho)

**Pergunta:** Fiquei sem luz por 30 horas na minha casa, na cidade, depois de um temporal em que foi decretada situação de emergência. A distribuidora tem que me compensar?

**Gabarito:** Sim. Em situação de emergência, cada interrupção acima do limite do indicador DISE gera compensação; para casa em área urbana atendida em baixa tensão, o limite do DISE é de 24 horas por evento, então 30 horas ultrapassa o limite. *(fatos-chave: Situação de Emergência que superar o limite do indicador DISE, 24)*

**Resposta do C2:** Sim, a distribuidora deve compensar você. A interrupção de 30 horas, causada por um temporal que gerou situação de emergência, é considerada um dano elétrico. A distribuidora é responsável por ressarcir esse dano, mesmo que a causa seja natural, como um temporal. O artigo 621 da Resolução ANEEL 1.000/2021 não exime a responsabilidade por danos causados por eventos naturais, como tempestades. Você pode solicitar a compensação diretamente à distribuidora.

**Fontes citadas:**

  - `D13-s4.8-item105`: As distribuidoras devem comunicar aos consumidores, por meio dos canais disponíveis, a provável causa da interrupção, a área afetada e o tempo previsto para a normalização do fornecimento em até 15 (quinze) minutos após o conhecimento da causa da interrupção. Independentemente do momento em que a causa for identificada, a comunicação contendo essas informações deve ser realizada em até 1 (uma)hora

  - `D01-art621-p2`: A distribuidora só pode eximir-se do dever de ressarcir no caso de: IV - comprovar que o dano foi ocasionado pelo uso incorreto do equipamento ou por defeitos gerados a partir da unidade consumidora, inclusive uso de carga que provoca distúrbios e danos ao sistema elétrico de distribuição;

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Trata a interrupção longa como dano elétrico e atribui ao art. 621 algo que ele não diz; a regra é a compensação pelo limite do DISE.*

### C2 · T-038 (multi_trecho)

**Pergunta:** Minha filha usa aparelho elétrico no tratamento em casa e nossa renda é de dois salários mínimos, estamos no CadÚnico. Temos direito à tarifa social? Que documento a empresa pede?

**Gabarito:** Sim: famílias do CadÚnico com renda de até 3 salários mínimos e alguém que precise de aparelho elétrico contínuo no tratamento têm direito; é preciso apresentar relatório e atestado assinados por médico e o comprovante do CadÚnico. *(fatos-chave: 3 (três) salários mínimos, relatório e atestado subscrito por profissional médico)*

**Resposta do C2:** Sim, você tem direito à Tarifa Social de Energia Elétrica. A empresa pede: relatório e atestado subscrito por profissional médico, comprovante de inscrição no CadÚnico e renda mensal de até três salários mínimos.

**Fontes citadas:**

  - `D02-art2-p2`: § 1º Excepcionalmente, será também beneficiada com a Tarifa Social de Energia Elétrica a unidade consumidora habitada por família inscrita no CadÚnico e com renda mensal de até 3 (três) salários mínimos, que tenha entre seus membros portador de doença ou patologia cujo tratamento ou procedimento médico pertinente requeira o uso continuado de aparelhos, equipamentos ou instrumentos que, para o seu橢

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

### C2 · T-039 (multi_trecho)

**Pergunta:** Pedi o ressarcimento um mês depois que meu aparelho queimou. Quanto tempo a empresa tem para me dar o resultado e, se aprovar, para pagar?

**Gabarito:** Resultado em até 15 dias (pedido feito em até 90 dias do dano) e, se aprovado, ressarcimento em até 20 dias. *(fatos-chave: 15 dias, 20 dias)*

**Resposta do C2:** A empresa tem até 15 dias após a verificação para dar o resultado, porque você pediu o ressarcimento um mês depois do dano. Se aprovado, o pagamento deve ser feito conforme o laudo e os documentos apresentados. O prazo exato para o pagamento não está nos trechos fornecidos.

**Fontes citadas:**

  - `D14-q09`: [página gov.br; sha256 816ef21539ed]

  - `D08-s9.3-item50`: 50. O prazo de Resposta para Solicitações de ressarcimento feitas em até 90 dias da data de provável ocorrência do dano elétrico é de 15 dias após a Verificação. 50.1. Para as solicitações feitas após 90 dias da data de provável ocorrência do dano elétrico, o prazo para Resposta é de 30 dias após a Verificação.

**Pré-classificação:** 🟡 parcial · afirma algo falso? **nao**

*Acerta os 15 dias; diz com honestidade que o prazo de pagamento (20 dias) não estava nos trechos.*

## 2. C1: só as respostas que diferem do C2

### C1 · T-003 (direta)

**Pergunta:** Com quanta antecedência a distribuidora precisa avisar uma residência comum sobre uma interrupção programada?

**Gabarito:** Pelo menos 72 horas antes do início da interrupção, pela página da distribuidora na internet e por outros meios de divulgação. *(fatos-chave: 72 horas)*

**Resposta do C1:** A distribuidora precisa avisar com antecedência mínima de 3 dias úteis para residências comuns, desde que o consumidor tenha feito o cadastro na distribuidora. Se a residência não estiver cadastrada, o aviso será feito por meio da página da distribuidora, com antecedência mínima de 72 horas.

**Fontes citadas:**

  - `D07-s8.2-item196`: unidades consumidoras atendidas em tensão inferior a 69 kV que prestem serviço essencial: aviso por meio de documento escrito e personalizado, com antecedência mínima de 5 dias úteis em relação à data da interrupção; unidades consumidoras atendidas em tensão superior a 2,3 kV e inferior a 230 kV com demanda contratada inferior a 500 kW e unidades consumidoras atendidas em tensão igual ou inferiora

**Pré-classificação:** 🟡 parcial · afirma algo falso? **sim**

*Mesma afirmação errada do C2 ('3 dias úteis com cadastro' é a regra de unidades comerciais, industriais ou de média tensão), mas acrescenta o aviso de 72 horas pela página da distribuidora, que é o certo para residência comum.*

### C1 · T-020 (coloquial)

**Pergunta:** Cortaram a luz da minha casa mas eu estava com tudo pago, foi erro deles. Quanto tempo eles têm pra voltar com a luz?

**Gabarito:** Na suspensão indevida, a religação deve ocorrer em até 4 horas, e a distribuidora deve creditar uma compensação. *(fatos-chave: 4 horas)*

**Resposta do C1:** Eles têm 4 horas para voltar com a luz, sem custo.

**Fontes citadas:**

  - `D14-q11`: [página gov.br; sha256 21af683ec3f5]

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

### C1 · T-028 (coloquial)

**Pergunta:** Minha conta veio com bandeira vermelha. Isso é uma taxa a mais que vão me cobrar?

**Gabarito:** Sim: nas bandeiras amarela e vermelha há um adicional, que deve vir destacado na fatura; na bandeira verde não há acréscimo. *(fatos-chave: destacados nas faturas)*

**Resposta do C1:** Não. A bandeira vermelha não é uma taxa a mais. É apenas uma forma de mostrar o custo real da energia no momento em que você consome. O valor já estava na sua conta, mas agora está mais claro. Você não paga mais, só vê o custo real.

**Fontes citadas:**

  - `D15-q02`: [página gov.br; sha256 4ab00ebaa6f5]

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Igual ao C2.*

### C1 · T-030 (coloquial)

**Pergunta:** Faz dois anos que minha TV queimou por causa de uma queda de energia. Ainda dá tempo de pedir pra empresa pagar?

**Gabarito:** Sim. O prazo para pedir ressarcimento é de até 5 anos da data provável do dano. *(fatos-chave: 5 anos)*

**Resposta do C1:** Sim, ainda dá tempo. Você tem até cinco anos para pedir o reembolso. Como já passaram dois anos, ainda há tempo, desde que a queda de energia tenha sido provável e a TV tenha sido conectada à instalação da sua casa.

**Fontes citadas:**

  - `D14-q09`: [página gov.br; sha256 7b80a9c579ac]

  - `D01-art602-p1`: O consumidor tem até 5 anos, a contar da data provável da ocorrência do dano elétrico no equipamento, para solicitar o ressarcimento à distribuidora, devendo informar, no mínimo, os seguintes itens: I - número de identificação da unidade consumidora; II - data e horário prováveis da ocorrência do dano; III - relato do problema apresentado pelo equipamento elétrico; IV - descrição e características

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*Igual ao C2.*

### C1 · T-037 (multi_trecho)

**Pergunta:** Fiquei sem luz por 30 horas na minha casa, na cidade, depois de um temporal em que foi decretada situação de emergência. A distribuidora tem que me compensar?

**Gabarito:** Sim. Em situação de emergência, cada interrupção acima do limite do indicador DISE gera compensação; para casa em área urbana atendida em baixa tensão, o limite do DISE é de 24 horas por evento, então 30 horas ultrapassa o limite. *(fatos-chave: Situação de Emergência que superar o limite do indicador DISE, 24)*

**Resposta do C1:** Sim, a distribuidora deve compensar você. O tempo de interrupção de 30 horas, após um temporal com situação de emergência, é considerado dano elétrico. A distribuidora tem obrigação de ressarcir, salvo se provar que o dano foi causado por uso incorreto do equipamento ou defeito na unidade consumidora. Como o temporal foi decretado como emergência, não há justificativa para eximir-se do dever de compensar.

**Fontes citadas:**

  - `D13-s4.8-item105`: As distribuidoras devem comunicar aos consumidores, por meio dos canais disponíveis, a provável causa da interrupção, a área afetada e o tempo previsto para a normalização do fornecimento em até 15 (quinze) minutos após o conhecimento da causa da interrupção. Independentemente do momento em que a causa for identificada, a comunicação contendo essas informações deve ser realizada em até 1 (uma)hora

  - `D01-art621-p2`: A distribuidora só pode eximir-se do dever de ressarcir no caso de: IV - comprovar que o dano foi ocasionado pelo uso incorreto do equipamento ou por defeitos gerados a partir da unidade consumidora, inclusive uso de carga que provoca distúrbios e danos ao sistema elétrico de distribuição;

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Igual ao C2.*

## 3. C0 (sem a base): respostas dadas

### C0 · T-002 (direta)

**Pergunta:** A distribuidora pode cortar a energia por falta de pagamento numa sexta-feira?

**Gabarito:** Não. O corte por inadimplemento só pode ser feito das 8 às 18 horas e é proibido às sextas-feiras, sábados, domingos, vésperas de feriado e feriados. *(fatos-chave: vedada às sextas-feiras, 8 horas às 18 horas)*

**Resposta do C0:** Não, a distribuidora não pode cortar a energia por falta de pagamento numa sexta-feira. A interrupção deve ocorrer apenas após notificação prévia e com pelo menos 72 horas de aviso. Isso vale para qualquer dia da semana.

**Fontes citadas:**

  - `REN ANEEL 1.000/2021, art. 362`: A distribuidora não poderá interromper o fornecimento de energia elétrica por falta de pagamento, salvo em caso de inadimplência comprovada e após notificação prévia, com prazo mínimo de 72 horas para o consumidor regularizar a dívida.

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Acerta 'não pode na sexta', mas diz que basta aviso de 72 horas e que 'vale para qualquer dia'; cita texto inventado atribuído ao art. 362.*

### C0 · T-009 (direta)

**Pergunta:** Se a distribuidora não consegue fazer a leitura do medidor por causa de uma calamidade pública, como a conta é calculada?

**Gabarito:** Pela média dos valores faturados nos 12 últimos ciclos, informando isso na fatura, com acerto depois que a situação terminar. *(fatos-chave: média aritmética dos valores faturados nos 12 últimos ciclos de faturamento)*

**Resposta do C0:** Se a distribuidora não consegue fazer a leitura por causa de calamidade pública, a conta é calculada com base na média dos consumos anteriores, com justificativa e notificação ao consumidor.

**Fontes citadas:**

  - `REN ANEEL 1.000/2021`: Em caso de calamidade pública, a leitura do medidor será feita por meio de amostragem ou estimativa, e a conta será calculada com base na média dos consumos anteriores, com a devida justificativa e notificação ao consumidor.

**Pré-classificação:** 🟡 parcial · afirma algo falso? **sim**

*'Média dos consumos anteriores' vai na direção certa (faltam os 12 ciclos); a citação ('leitura por amostragem') é inventada.*

### C0 · T-015 (direta)

**Pergunta:** O que significa a bandeira tarifária verde na conta de luz?

**Gabarito:** Indica condições favoráveis de geração e não traz acréscimo na tarifa. *(fatos-chave: não implicando acréscimo tarifário)*

**Resposta do C0:** A bandeira verde significa que a energia vem de fontes renováveis, como solar ou eólica, e tem menos impacto no meio ambiente.

**Fontes citadas:**

  - `REN ANEEL 1.000/2021, art. 362`: A bandeira tarifária verde indica que a energia elétrica está sendo gerada com fontes renováveis, como solar, eólica ou hidrelétricas, e que o sistema de distribuição está operando com baixa emissão de gases de efeito estufa.

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Diz que a bandeira verde significa energia de fontes renováveis.*

### C0 · T-018 (direta)

**Pergunta:** O Código de Defesa do Consumidor obriga a empresa de energia a fornecer o serviço de forma contínua?

**Gabarito:** Sim. Concessionárias de serviços essenciais devem prestar serviços adequados, eficientes, seguros e contínuos (art. 22 do CDC). *(fatos-chave: contínuos)*

**Resposta do C0:** Sim, o Código de Defesa do Consumidor obriga a empresa de energia a fornecer o serviço de forma contínua, salvo quando houver justa causa e notificação prévia.

**Fontes citadas:**

  - `CDC`: Art. 13: O consumidor tem direito a receber os serviços contratados, com continuidade, sem interrupção, salvo quando houver justa causa e notificação prévia.

**Pré-classificação:** 🟡 parcial · afirma algo falso? **sim**

*Conclusão certa (serviço contínuo); cita um 'art. 13' do CDC com texto inventado.*

### C0 · T-021 (coloquial)

**Pergunta:** Chegou um papel dizendo que vão cortar minha luz por causa de conta atrasada. Eles podem cortar sem me avisar antes? Quantos dias de aviso eu tenho?

**Gabarito:** Não. No caso de inadimplemento, a notificação deve ser feita com pelo menos 15 dias de antecedência. *(fatos-chave: 15 dias)*

**Resposta do C0:** Não, eles não podem cortar sua luz sem aviso. Você tem direito a 72 horas de aviso antes do corte, a menos que haja emergência de risco iminente à segurança.

**Fontes citadas:**

  - `REN ANEEL 1.000/2021, art. 362`: A distribuidora deve notificar o consumidor com antecedência mínima de 72 horas antes do corte da energia, exceto em casos de emergência, como risco iminente à segurança da vida ou da propriedade.

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*72 horas de aviso; o certo é 15 dias.*

### C0 · T-028 (coloquial)

**Pergunta:** Minha conta veio com bandeira vermelha. Isso é uma taxa a mais que vão me cobrar?

**Gabarito:** Sim: nas bandeiras amarela e vermelha há um adicional, que deve vir destacado na fatura; na bandeira verde não há acréscimo. *(fatos-chave: destacados nas faturas)*

**Resposta do C0:** Não, a bandeira vermelha não é uma taxa extra. É um sinal de que a tarifa de energia elétrica foi ajustada por causa do custo de produção. O valor é definido pela ANEEL e cobrado normalmente na sua conta.

**Fontes citadas:**

  - `REN ANEEL 1.000/2021`: A bandeira vermelha indica que a tarifa de energia elétrica será ajustada por causa de variações no custo de produção. O valor da tarifa é definido pela ANEEL e não é uma taxa extra para o consumidor. A cobrança é feita conforme a tarifa oficial, sem acréscimos adicionais para o consumidor.

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Mesmo erro do C1 e do C2 sobre a bandeira vermelha.*

### C0 · T-033 (ruido)

**Pergunta:** chegou um papel dizendo que vao cortar minha lus por causa de conta atrasado eles podem cortar sem me avisar antes quantos dias aviso eu tenho

**Gabarito:** Não. No caso de inadimplemento, a notificação deve ser feita com pelo menos 15 dias de antecedência. *(fatos-chave: 15 dias)*

**Resposta do C0:** Não, eles não podem cortar sua luz sem aviso. A distribuidora deve avisar pelo menos 72 horas antes do corte, por causa de dívida. Se você não recebeu aviso, pode reclamar no Procon ou na distribuidora.

**Fontes citadas:**

  - `REN ANEEL 1.000/2021, art. 362`: A distribuidora deve notificar o consumidor pelo menos 72 horas antes do corte de energia, quando houver dívida não quitada. O corte só pode ocorrer após a notificação e a possibilidade de pagamento.

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*72 horas de aviso; o certo é 15 dias.*

### C0 · T-038 (multi_trecho)

**Pergunta:** Minha filha usa aparelho elétrico no tratamento em casa e nossa renda é de dois salários mínimos, estamos no CadÚnico. Temos direito à tarifa social? Que documento a empresa pede?

**Gabarito:** Sim: famílias do CadÚnico com renda de até 3 salários mínimos e alguém que precise de aparelho elétrico contínuo no tratamento têm direito; é preciso apresentar relatório e atestado assinados por médico e o comprovante do CadÚnico. *(fatos-chave: 3 (três) salários mínimos, relatório e atestado subscrito por profissional médico)*

**Resposta do C0:** Sim, vocês têm direito à tarifa social. A distribuidora pede comprovante de renda e documento de inscrição no CadÚnico. O valor é baseado em dois salários mínimos mensais.

**Fontes citadas:**

  - `REN ANEEL 1.000/2021`: Art. 362. A tarifa social será oferecida a consumidores que tenham renda mensal igual ou inferior a dois salários mínimos, com comprovação de renda e situação de vulnerabilidade social, como o CadÚnico. A distribuidora poderá exigir documento comprovativo de renda e de inscrição no CadÚnico.

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Critério de 'dois salários mínimos' e não cita o relatório e atestado médicos.*

## 4. C0: recusas de perguntas respondíveis

### C0 · T-003 (direta)

**Pergunta:** Com quanta antecedência a distribuidora precisa avisar uma residência comum sobre uma interrupção programada?

**Gabarito:** Pelo menos 72 horas antes do início da interrupção, pela página da distribuidora na internet e por outros meios de divulgação. *(fatos-chave: 72 horas)*

**Resposta do C0:** Não há regra na ANEEL sobre quantos dias antecipar o aviso para interrupção programada em residências comuns. Procure a distribuidora ou o Procon para saber o que é exigido localmente.

**Pré-classificação:** nega uma regra que existe? **sim**

### C0 · T-005 (direta)

**Pergunta:** Se a distribuidora ultrapassa os limites de interrupção da minha casa, em quanto tempo a compensação deve aparecer na fatura?

**Gabarito:** O crédito da compensação deve vir na fatura em até 2 meses após o período de apuração. *(fatos-chave: em até 2 meses após o período de apuração)*

**Resposta do C0:** Não há regra que defina o prazo para a compensação aparecer na fatura. Procure a sua distribuidora ou o Procon para mais informações.

**Pré-classificação:** nega uma regra que existe? **sim**

### C0 · T-006 (direta)

**Pergunta:** Qual é o prazo para pedir à distribuidora o ressarcimento de um aparelho danificado por problema na rede?

**Gabarito:** O consumidor tem até 5 anos, contados da data provável do dano, para pedir o ressarcimento. *(fatos-chave: 5 anos)*

**Resposta do C0:** Não há norma específica sobre prazo para ressarcimento de aparelho danificado por problema na rede. Para saber o que deve ser feito, é necessário consultar a distribuidora ou o Procon.

**Pré-classificação:** nega uma regra que existe? **sim**

### C0 · T-007 (direta)

**Pergunta:** A distribuidora pode negar o ressarcimento de um aparelho queimado dizendo que a cidade estava em situação de emergência decretada?

**Gabarito:** Não. Essa possibilidade existia (inciso VIII do art. 621 da REN 1.000 e alínea b do item 14 do Módulo 9 do PRODIST), mas foi revogada pela REN 1.137/2025 (arts. 19 e 20); hoje a situação de emergência não está entre os casos em que a distribuidora pode deixar de ressarcir. *(fatos-chave: Revoga-se o inciso VIII do art. 621)*

**Resposta do C0:** A distribuidora não pode negar o ressarcimento apenas por causa de uma emergência declarada. Para saber se há direito ao ressarcimento, é preciso analisar a causa do problema e a responsabilidade da distribuidora. Procure a distribuidora, a ANEEL ou o Procon para esclarecer.

**Pré-classificação:** nega uma regra que existe? **nao**

*A recusa diz que a distribuidora não pode negar só por causa da emergência declarada: na direção do gabarito, sem citar a revogação.*

### C0 · T-008 (direta)

**Pergunta:** Qual é o custo de disponibilidade mínimo cobrado de uma casa com ligação monofásica?

**Gabarito:** O custo de disponibilidade de uma ligação monofásica equivale a 30 kWh. *(fatos-chave: 30 kWh)*

**Resposta do C0:** Não há dados oficiais sobre custo de disponibilidade mínima para casas com ligação monofásica. Procure a sua distribuidora ou o Procon para mais informações.

**Pré-classificação:** nega uma regra que existe? **sim**

*A heurística não pegou ('Não há dados oficiais sobre o custo de disponibilidade').*

### C0 · T-011 (direta)

**Pergunta:** Qual é o critério de renda do CadÚnico para ter direito à Tarifa Social de Energia Elétrica?

**Gabarito:** Família inscrita no CadÚnico com renda mensal por pessoa de até meio salário mínimo (ou ter na casa quem recebe o BPC). *(fatos-chave: meio salário mínimo nacional)*

**Resposta do C0:** O CadÚnico não define critério de renda para a Tarifa Social de Energia Elétrica. A tarifa é regulada pela ANEEL com base em critérios técnicos, não em renda do CadÚnico. Procure a distribuidora, a ANEEL ou o Procon para mais informações.

**Pré-classificação:** nega uma regra que existe? **sim**

*A heurística não pegou ('O CadÚnico não define critério de renda').*

### C0 · T-013 (direta)

**Pergunta:** Para uma família da tarifa social (baixa renda), quanto tempo depois do vencimento da conta a energia pode ser cortada por falta de pagamento?

**Gabarito:** Precisa haver pelo menos 30 dias entre o vencimento da fatura e o corte. *(fatos-chave: 30 dias)*

**Resposta do C0:** Não há regra oficial que defina o prazo máximo para corte de energia para famílias de tarifa social. A distribuidora pode aplicar políticas próprias, mas deve respeitar a Lei de Direitos do Consumidor. Para saber o que acontece em sua região, é melhor entrar em contato com a distribuidora ou o Procon da sua cidade.

**Pré-classificação:** nega uma regra que existe? **sim**

### C0 · T-020 (coloquial)

**Pergunta:** Cortaram a luz da minha casa mas eu estava com tudo pago, foi erro deles. Quanto tempo eles têm pra voltar com a luz?

**Gabarito:** Na suspensão indevida, a religação deve ocorrer em até 4 horas, e a distribuidora deve creditar uma compensação. *(fatos-chave: 4 horas)*

**Resposta do C0:** Não há regra que defina o prazo exato para a restauração da luz em caso de erro. A distribuidora deve atender o pedido de reativação da energia, mas o tempo pode variar. Procure a sua distribuidora ou o Procon para saber o que fazer.

**Pré-classificação:** nega uma regra que existe? **sim**

### C0 · T-022 (coloquial)

**Pergunta:** Minha geladeira queimou quando a luz voltou e eu guardo insulina nela. Depois que eu reclamar, quanto tempo a empresa tem pra vir ver a geladeira?

**Gabarito:** Para equipamento que guarda alimentos perecíveis ou medicamentos, a verificação deve ser feita em até um dia útil. *(fatos-chave: um dia útil)*

**Resposta do C0:** A distribuidora não tem prazo definido na legislação para vir ver uma geladeira queimada. Você deve procurar a sua distribuidora ou o Procon para saber o procedimento e o prazo de atendimento. A ANEEL não estabelece tempo para reparo de aparelhos domésticos por falhas elétricas.

**Pré-classificação:** nega uma regra que existe? **sim**

### C0 · T-024 (coloquial)

**Pergunta:** Sou aposentado e recebo o BPC. Eu tenho direito a algum desconto na conta de luz?

**Gabarito:** Sim. Quem tem na casa morador que recebe o benefício de prestação continuada (BPC) tem direito à Tarifa Social. *(fatos-chave: benefício de prestação continuada)*

**Resposta do C0:** Não há desconto oficial na conta de luz para aposentados ou beneficiários do BPC. Cada distribuidora pode ter políticas próprias, mas não há regra nacional que garanta desconto. Procure sua distribuidora ou o Procon para saber se há benefícios locais.

**Pré-classificação:** nega uma regra que existe? **sim**

*Diz que não há desconto para quem recebe o BPC.*

### C0 · T-026 (coloquial)

**Pergunta:** Com a enchente o pessoal da empresa não conseguiu ler meu relógio de luz e a conta veio estimada. Como é que eles calculam esse valor?

**Gabarito:** Pela média dos valores faturados nos 12 últimos ciclos, com aviso na fatura e acerto quando a situação terminar. *(fatos-chave: média aritmética)*

**Resposta do C0:** A empresa não pode calcular a conta com base em regras específicas para enchentes. O cálculo de contas estimadas é feito por métodos internos da distribuidora, que não são públicos. Para saber como foi feito, você deve entrar em contato com a distribuidora ou com o Procon.

**Pré-classificação:** nega uma regra que existe? **sim**

*A heurística não pegou ('métodos internos que não são públicos').*

### C0 · T-030 (coloquial)

**Pergunta:** Faz dois anos que minha TV queimou por causa de uma queda de energia. Ainda dá tempo de pedir pra empresa pagar?

**Gabarito:** Sim. O prazo para pedir ressarcimento é de até 5 anos da data provável do dano. *(fatos-chave: 5 anos)*

**Resposta do C0:** Não há lei que obrigue a empresa de energia a pagar por danos a aparelhos domésticos como TVs por quedas de energia. A responsabilidade é tratada em contratos específicos e não é coberta por normas gerais. Procure a distribuidora ou o Procon para saber se há cobertura no seu contrato de energia.

**Pré-classificação:** nega uma regra que existe? **sim**

### C0 · T-032 (ruido)

**Pergunta:** cortaram lus da minha casa mas eu tava com tudo pago foi erro deles quantu tempo eles tem pra voltar com a lus

**Gabarito:** Na suspensão indevida, a religação deve ocorrer em até 4 horas, e a distribuidora deve creditar uma compensação. *(fatos-chave: 4 horas)*

**Resposta do C0:** Não há lei que defina tempo exato para a energia voltar caso tenha sido cortada por erro. Procure a sua distribuidora ou o Procon para saber o prazo e o que fazer.

**Pré-classificação:** nega uma regra que existe? **sim**

### C0 · T-034 (ruido)

**Pergunta:** minha geladera queimou quando a lus voltou e eu guardo insolina nela depois que eu reclamar quantu tempo a impresa tem pra vir ver geladera

**Gabarito:** Para equipamento que guarda alimentos perecíveis ou medicamentos, a verificação deve ser feita em até um dia útil. *(fatos-chave: um dia útil)*

**Resposta do C0:** Não há regra oficial sobre o prazo para a empresa vir ver a geladeira. Procure a distribuidora ou o Procon para ajudar com isso.

**Pré-classificação:** nega uma regra que existe? **sim**

### C0 · T-036 (ruido)

**Pergunta:** sou aposentadu e recebo o bpc eu tenho direito algum disconto na conta de lus

**Gabarito:** Sim. Quem tem na casa morador que recebe o benefício de prestação continuada (BPC) tem direito à Tarifa Social. *(fatos-chave: benefício de prestação continuada)*

**Resposta do C0:** Não há desconto na conta de luz para aposentadas ou beneficiárias do BPC. A informação não está em lei ou regulamento da ANEEL. Procure sua distribuidora ou o Procon para mais esclarecimentos.

**Pré-classificação:** nega uma regra que existe? **sim**

### C0 · T-037 (multi_trecho)

**Pergunta:** Fiquei sem luz por 30 horas na minha casa, na cidade, depois de um temporal em que foi decretada situação de emergência. A distribuidora tem que me compensar?

**Gabarito:** Sim. Em situação de emergência, cada interrupção acima do limite do indicador DISE gera compensação; para casa em área urbana atendida em baixa tensão, o limite do DISE é de 24 horas por evento, então 30 horas ultrapassa o limite. *(fatos-chave: Situação de Emergência que superar o limite do indicador DISE, 24)*

**Resposta do C0:** Não há lei que obrigue a distribuidora a compensar por perda de luz em situações de emergência, como temporal. A responsabilidade é definida por contrato com a distribuidora. Procure a sua distribuidora ou o Procon para saber se há política interna de assistência em emergências.

**Pré-classificação:** nega uma regra que existe? **sim**

### C0 · T-039 (multi_trecho)

**Pergunta:** Pedi o ressarcimento um mês depois que meu aparelho queimou. Quanto tempo a empresa tem para me dar o resultado e, se aprovar, para pagar?

**Gabarito:** Resultado em até 15 dias (pedido feito em até 90 dias do dano) e, se aprovado, ressarcimento em até 20 dias. *(fatos-chave: 15 dias, 20 dias)*

**Resposta do C0:** Não há informação oficial sobre prazo de ressarcimento para queima de aparelho em energia elétrica. Procure a sua distribuidora, a ANEEL ou o Procon para esclarecer.

**Pré-classificação:** nega uma regra que existe? **sim**

### C0 · T-040 (multi_trecho)

**Pergunta:** Vai ter manutenção programada na minha rua. Moro numa casa comum, mas meu pai usa respirador. Com quanto tempo de antecedência eu devo ser avisado?

**Gabarito:** Em geral o aviso é de pelo menos 72 horas pela internet e outros meios; como há usuário de equipamento vital, se a casa estiver cadastrada o aviso deve ser escrito e personalizado com pelo menos 5 dias úteis. *(fatos-chave: 72 horas, 5 dias úteis)*

**Resposta do C0:** Não há regra oficial sobre quanto tempo de antecedência deve ser dado para manutenção em casas comuns com moradores que usam respiradores. Procure a distribuidora ou o Procon para mais informações.

**Pré-classificação:** nega uma regra que existe? **sim**
