# Conferência do test novo, T2 (Fase 8B)

**Para:** Pedro. **Itens:** 20. O T2 foi medido uma única vez, com o sistema congelado. Entram:
- **C2 original:** todas as respostas dadas às perguntas respondíveis;
- **C2 final** (qwen3 4B q4 com as correções C, D, E e V): só as respostas cujo **sentido mudou**.

Os critérios são os mesmos das conferências anteriores. Responda no chat só com as discordâncias,
por exemplo: "C2 T2-11: correta".

No C2 final, as demais respostas herdam o veredito do C2 original:
- **mesma resposta:** T2-01, T2-02, T2-23, T2-24;
- **redação diferente, mesmo sentido:** T2-04, T2-05, T2-06, T2-08, T2-09, T2-10, T2-12, T2-13, T2-16, T2-18;
- **continuam recusadas:** T2-07;
- **nova recusa (contingência):** T2-11.

> Nesta versão, as citações de páginas gov.br aparecem como hash (licença CC BY-ND). A versão completa está em `avaliacao/runs/local/conferencia_t2_completa.md`.



## 1. C2 original: respostas dadas às perguntas respondíveis

### C2 · T2-01 (direta)

**Pergunta:** Em quanto tempo a distribuidora deve fazer a troca de titularidade da conta de luz de uma casa na área urbana?

**Gabarito:** Em até 3 dias úteis na área urbana (5 dias úteis na área rural). *(fatos-chave: 3 dias úteis)*

**Resposta do C2:** A distribuidora deve fazer a troca de titularidade da conta de luz de uma casa na área urbana em até 3 dias úteis.

**Fontes citadas:**

  - `D14-q04`: [página gov.br; sha256 5be9f00aec00]

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

### C2 · T2-02 (direta)

**Pergunta:** Quantas opções de data de vencimento da fatura a distribuidora deve oferecer ao consumidor?

**Gabarito:** Pelo menos seis datas de vencimento, distribuídas uniformemente ao longo do mês. *(fatos-chave: 6 datas)*

**Resposta do C2:** A distribuidora deve oferecer pelo menos seis opções de data de vencimento da fatura.

**Fontes citadas:**

  - `D01-art338`: A distribuidora deve oferecer pelo menos seis datas de vencimento da fatura para escolha do consumidor e demais usuários, distribuídas uniformemente em intervalos regulares ao longo do mês.

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

### C2 · T2-03 (direta)

**Pergunta:** De quanto em quanto tempo a distribuidora deve fazer a leitura do medidor de uma casa?

**Gabarito:** A cada aproximadamente 30 dias, com intervalo mínimo de 27 e máximo de 33 dias (há exceções, como o primeiro faturamento). *(fatos-chave: 27, 33)*

**Resposta do C2:** Os trechos não mencionam o intervalo de tempo para a leitura do medidor de uma casa. A leitura do medidor não é regulamentada por prazo fixo nos trechos fornecidos. Procurar a distribuidora, a ANEEL ou o Procon para mais informações.

**Fontes citadas:**

  - `D01-art91`: A distribuidora deve realizar a vistoria e a instalação dos equipamentos de medição nas instalações do consumidor e demais usuários nos seguintes prazos: I - em até 5 dias úteis: para conexão em tensão menor que 2,3 kV; II - em até 10 dias úteis: para conexão em tensão maior ou igual a 2,3 kV e menor que 69 kV; e III - em até 15 dias úteis: para conexão em tensão maior ou igual a 69 kV.

  - `D01-art250-p1`: a distribuidora deve agendar com o consumidor e demais usuários na solicitação ou informar, com antecedência de pelo menos 3 dias úteis, a data fixada e o horário previsto para a realização da inspeção, de modo a possibilitar o seu acompanhamento;

  - `D01-art587`: A distribuidora deve verificar e regularizar a situação em até: I - 6 horas: na área urbana; II - 24 horas: na área rural; e III - 72 horas: se o atendimento for por meio de sistemas do tipo SIGFI ou MIGDI.

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Diz que não há prazo fixo para a leitura; o art. 260 (27 a 33 dias) não veio entre os trechos.*

### C2 · T2-04 (direta)

**Pergunta:** Depois de quanto tempo do vencimento de uma conta não paga a distribuidora não pode mais cortar a luz por causa dela?

**Gabarito:** Depois de 90 dias da data da fatura vencida e não paga, o corte é vedado, salvo se a distribuidora comprovar que não cortou antes por determinação judicial ou outro motivo justificável. *(fatos-chave: 90 dias)*

**Resposta do C2:** A distribuidora não pode cortar a luz após 30 dias do vencimento da fatura para consumidores de renda baixa. Isso vale apenas para unidades residenciais de baixa renda. Para outros casos, o prazo é de 15 dias, conforme a Resolução 1.000/2021.

**Fontes citadas:**

  - `D01-art582`: Para unidade consumidora classificada nas subclasses residencial baixa renda, a distribuidora deve observar o intervalo de pelo menos 30 dias entre a data de vencimento da fatura e a data de suspensão do fornecimento.

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Responde com os 30 dias da baixa renda (art. 358) e um prazo de 15 dias; não fala da vedação após 90 dias (art. 357, que não veio).*

### C2 · T2-05 (direta)

**Pergunta:** Com quantos dias de antecedência a conta de luz de uma casa deve ser entregue antes do vencimento?

**Gabarito:** Pelo menos 5 dias úteis antes do vencimento (10 dias úteis para poder público, iluminação pública e serviço público). *(fatos-chave: 5 dias úteis)*

**Resposta do C2:** A conta de luz deve ser entregue pelo menos 5 dias úteis antes do vencimento, para casas que não estão em classes como poder público, iluminação pública ou serviço público. Para essas classes, o prazo é de 10 dias úteis.

**Fontes citadas:**

  - `D01-art337`: Art. 337. O prazo para vencimento da fatura, contado da data da apresentação, deve ser de pelo menos: I - 10 dias úteis: para unidade consumidora enquadrada nas classes poder público, iluminação pública e serviço público; e II - 5 dias úteis: nas demais situações.

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

### C2 · T2-06 (direta)

**Pergunta:** Se a vistoria da entrada de energia de uma ligação nova for reprovada, em quanto tempo a distribuidora deve entregar o relatório com os motivos?

**Gabarito:** Em até 3 dias úteis após a conclusão da vistoria, com os motivos e as providências corretivas necessárias. *(fatos-chave: 3 dias úteis)*

**Resposta do C2:** Em até 3 dias úteis após a conclusão do procedimento, a distribuidora deve entregar o relatório com os motivos.

**Fontes citadas:**

  - `D01-art94`: Ocorrendo reprovação das instalações de entrada de energia elétrica na vistoria, a distribuidora deve disponibilizar ao consumidor e demais usuários, em até 3 dias úteis após a conclusão do procedimento, o relatório de vistoria, com os motivos e as providências corretivas necessárias.

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

### C2 · T2-08 (coloquial)

**Pergunta:** Aluguei uma casa e o morador antigo deixou conta de luz atrasada. A empresa pode me obrigar a pagar essa dívida pra passar a conta pro meu nome?

**Gabarito:** Não. A distribuidora não pode condicionar a alteração de titularidade ao pagamento de débito de titularidade de terceiros, nem exigir que você assine termo assumindo essa dívida. *(fatos-chave: moradores anteriores)*

**Resposta do C2:** Não, a empresa não pode obrigar você a pagar a dívida do morador antigo. A ANEEL proíbe que a distribuidora cobre o novo morador por dívidas anteriores.

**Fontes citadas:**

  - `D14-q05`: [página gov.br; sha256 5d050f1448b5]

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*Cita a página D14-q05 (não estava entre os equivalentes), que diz o mesmo.*

### C2 · T2-09 (coloquial)

**Pergunta:** A conta de luz veio com um valor cobrado a mais e eu já paguei. Eles só me devolvem o que paguei a mais ou tem alguma coisa além disso?

**Gabarito:** A quantia paga a mais deve ser devolvida em dobro, atualizada pelo IPCA e com juros de 1% ao mês; a devolução só é simples se a distribuidora comprovar que o erro foi causado pelo consumidor ou, em condições específicas, por terceiro. *(fatos-chave: em dobro)*

**Resposta do C2:** Eles devolvem o valor pago a mais em dobro, se a cobrança foi indevida. Se a distribuidora provar que foi culpa do consumidor ou de terceiros, só devolve o valor pago a mais.

**Fontes citadas:**

  - `D14-q12`: [página gov.br; sha256 ea7bc2fa102b]

  - `D01-art103`: Art. 103. Caso cobre pela conexão sem observar o disposto nesta Resolução, a distribuidora deve devolver em dobro o valor pago em excesso pelo consumidor e demais usuários, acrescido de correção monetária e juros e calculado conforme § 2º do art. 323.

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*Responde o que foi perguntado (em dobro); não cita o IPCA e os juros.*

### C2 · T2-10 (coloquial)

**Pergunta:** Tenho uma conta de luz de quatro meses atrás que ficou sem pagar. A empresa ainda pode cortar minha luz por causa dela?

**Gabarito:** Em regra, não: o corte é vedado depois de 90 dias da fatura vencida e não paga, salvo se a distribuidora comprovar que não cortou antes por determinação judicial ou outro motivo justificável. *(fatos-chave: 90 dias)*

**Resposta do C2:** Sim, a empresa ainda pode cortar sua luz por causa da conta de quatro meses atrás, desde que a suspensão seja feita com aviso prévio de pelo menos três dias (ou quinze dias, no caso de falta de pagamento), conforme a Resolução 1000/2021 da ANEEL. Se você apresentar comprovante de quitação no momento da suspensão, a energia não pode ser cortada.

**Fontes citadas:**

  - `D14-q10`: [página gov.br; sha256 5bc1eb2acc95]

  - `D14-q15`: [página gov.br; sha256 25bd18c64b36]

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Diz que a empresa AINDA PODE cortar pela conta de 4 meses; depois de 90 dias o corte é vedado.*

### C2 · T2-11 (coloquial)

**Pergunta:** Minha conta vence antes do meu salário cair. Posso pedir pra mudar o dia do vencimento?

**Gabarito:** Sim. A distribuidora deve oferecer pelo menos seis datas de vencimento para você escolher; depois da mudança, a data só pode ser alterada de novo após 12 meses. *(fatos-chave: 6 datas, 12 meses)*

**Resposta do C2:** Sim, você pode pedir para mudar o dia do vencimento da conta. A distribuidora deve oferecer pelo menos seis datas de vencimento distribuídas uniformemente ao longo do mês. Mas a mudança só pode ser feita após 12 meses, com autorização prévia do consumidor.

**Fontes citadas:**

  - `D01-art338`: A distribuidora deve oferecer pelo menos seis datas de vencimento da fatura para escolha do consumidor e demais usuários, distribuídas uniformemente em intervalos regulares ao longo do mês. § 1º O oferecimento disposto no caput deve ser realizado na solicitação da conexão, na alteração de titularidade ou sempre que solicitado. § 2º A data de vencimento da fatura somente pode ser modificada em um间隔

**Pré-classificação:** 🟡 parcial · afirma algo falso? **nao**

*Acerta as seis datas, mas diz 'a mudança só pode ser feita após 12 meses', quando a regra é que a data só pode ser alterada de novo depois de 12 meses.*

### C2 · T2-12 (coloquial)

**Pergunta:** Minha conta deste mês veio com 40 dias de consumo. A leitura do relógio não tinha que ser feita todo mês?

**Gabarito:** Sim: a leitura deve ser feita a cada cerca de 30 dias, com no mínimo 27 e no máximo 33 dias (salvo exceções, como o primeiro faturamento ou mudança de rota). Se passar de 33 dias, a distribuidora deve proporcionalizar o consumo ao número máximo de dias permitido. *(fatos-chave: 33)*

**Resposta do C2:** Não, a leitura não precisa ser feita todo mês. Para o grupo B, o intervalo é de 27 a 33 dias. Em casos especiais, como primeiro faturamento, pode ser de 15 a 47 dias. Seu caso com 40 dias está dentro do permitido.

**Fontes citadas:**

  - `D01-art260`: A leitura do sistema de medição para o grupo B deve ser realizada em intervalos de aproximadamente 30 dias, observados o mínimo de 27 e o máximo de 33 dias, de acordo com o calendário de leitura. § 1º Para o primeiro faturamento, ou no caso de remanejamento de rota ou reprogramação do calendário, as leituras podem ser realizadas em intervalos de no mínimo 15 e no máximo 47 dias.

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Diz que 40 dias está dentro do permitido; o intervalo normal é de 27 a 33 dias, e 15 a 47 só vale para exceções como o primeiro faturamento.*

### C2 · T2-13 (ruido)

**Pergunta:** aluguei uma casa o morador antigo deixou conta de lus atrasado a impresa pode me obrigar a pagar essa divida pra passar a conta pro meu nome

**Gabarito:** Não. A distribuidora não pode condicionar a alteração de titularidade ao pagamento de débito de titularidade de terceiros, nem exigir que você assine termo assumindo essa dívida. *(fatos-chave: moradores anteriores)*

**Resposta do C2:** Não, a distribuidora não pode obrigar você a pagar a dívida do antigo morador. A ANEEL diz que não pode cobrar o novo morador como condição para mudar a conta de luz.

**Fontes citadas:**

  - `D14-q05`: [página gov.br; sha256 a55e2f3b83d3]

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*Versão de voz da T2-08.*

### C2 · T2-14 (ruido)

**Pergunta:** conta de lus veio com um valor cobrado a mais e eu ja paguei eles so me devolvem o que paguei a mais ou tem alguma coisa alem disso

**Gabarito:** A quantia paga a mais deve ser devolvida em dobro, atualizada pelo IPCA e com juros de 1% ao mês; a devolução só é simples se a distribuidora comprovar que o erro foi causado pelo consumidor ou, em condições específicas, por terceiro. *(fatos-chave: em dobro)*

**Resposta do C2:** Se a cobrança a mais foi indevida, a distribuidora deve devolver o valor pago a mais em dobro. Isso está previsto na Resolução 1000/2021 da ANEEL. Se a distribuidora comprovar que foi culpa do consumidor ou de terceiros, só devolve o valor pago a mais.

**Fontes citadas:**

  - `D14-q12`: [página gov.br; sha256 ea7bc2fa102b]

  - `D14-q13`: [página gov.br; sha256 578e026d8945]

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*Versão de voz da T2-09.*

### C2 · T2-16 (multi_trecho)

**Pergunta:** Comprei um apartamento e quero passar a conta de luz pro meu nome. Em quanto tempo a distribuidora tem que fazer a troca e ela pode exigir que eu pague as contas atrasadas do antigo dono?

**Gabarito:** A troca deve ser feita em até 3 dias úteis na área urbana (5 na rural), e a distribuidora não pode condicioná-la ao pagamento de débito de titularidade de terceiros. *(fatos-chave: 3 dias úteis, terceiros)*

**Resposta do C2:** A distribuidora deve fazer a troca do nome em até 3 dias úteis, na área urbana. Ela não pode exigir que você pague as contas atrasadas do antigo dono.

**Fontes citadas:**

  - `D14-q04`: [página gov.br; sha256 d899404d596b]

  - `D14-q05`: [página gov.br; sha256 9ccf13584e07]

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

### C2 · T2-17 (multi_trecho)

**Pergunta:** Descobri que a empresa me cobrou a mais na conta de luz. Quanto ela tem que me devolver, com qual correção e até quando?

**Gabarito:** Deve devolver em dobro (simples apenas se comprovar erro atribuível ao consumidor ou, em condições específicas, a terceiro), com atualização pelo IPCA e juros de mora de 1% ao mês, até o segundo ciclo de faturamento posterior à constatação. *(fatos-chave: em dobro, IPCA, 1% ao mês)*

**Resposta do C2:** A distribuidora deve devolver em dobro o valor pago a mais, acrescido de correção monetária e juros, conforme o § 2º do art. 323. O prazo para a devolução não é especificado nos trechos fornecidos. Se a cobrança foi por erro da distribuidora, a devolução é em dobro. Se for por erro do consumidor, o valor é devolvido apenas uma vez.

**Fontes citadas:**

  - `D01-art103`: Caso cobre pela conexão sem observar o disposto nesta Resolução, a distribuidora deve devolver em dobro o valor pago em excesso pelo consumidor e demais usuários, acrescido de correção monetária e juros e calculado conforme § 2º do art. 323.

  - `D01-art627a-p8`: Em caso de cobrança incorreta por motivo atribuível à distribuidora ou ao titular do serviço, aplica-se a devolução prevista no art. 323, devendo serem estabelecidas em contrato eventuais formas de ressarcimento entre os contratantes.

  - `D14-q12`: [página gov.br; sha256 ea7bc2fa102b]

**Pré-classificação:** 🟡 parcial · afirma algo falso? **nao**

*Acerta o dobro com correção e juros; diz que o prazo para devolver não está nos trechos (é até o 2º ciclo, art. 323, que não veio inteiro) e cita o art. 103 (conexão).*

### C2 · T2-18 (multi_trecho)

**Pergunta:** Tenho placa solar em casa. Por quanto tempo valem os créditos de energia que sobram e o que acontece com eles quando vencem?

**Gabarito:** Os créditos expiram em 60 meses após o faturamento em que foram gerados e, depois disso, são revertidos para a modicidade tarifária, sem compensação ao consumidor. *(fatos-chave: 60 meses, modicidade tarifária)*

**Resposta do C2:** Os créditos de energia da sua placa solar valem por 60 meses a partir da data do faturamento. Após esse prazo, eles são revertidos para a modicidade tarifária e você não tem direito a compensação. A quantidade de energia não muda mesmo que as tarifas mudem.

**Fontes citadas:**

  - `D09-art13-p1`: Os créditos de energia elétrica expiram em 60 (sessenta) meses após a data do faturamento em que foram gerados e serão revertidos em prol da modicidade tarifária sem que o consumidor participante do SCEE faça jus a qualquer forma de compensação após esse prazo.

  - `D01-art655l`: Os créditos de energia expiram em 60 meses após a data do faturamento em que foram gerados. § 1º Ao final do prazo de validade estabelecido no caput, os créditos de energia devem ser revertidos para a modicidade tarifária, sem que o consumidor tenha direito a qualquer forma de compensação.

  - `D09-art13-p1`: Os créditos são determinados em termos de energia elétrica ativa, não estando sua quantidade sujeita a alterações em razão da variação nos valores das tarifas de energia elétrica.

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

## 2. C2 final: respostas cujo sentido mudou

### C2_final · T2-03 (direta)

**Pergunta:** De quanto em quanto tempo a distribuidora deve fazer a leitura do medidor de uma casa?

**Gabarito:** A cada aproximadamente 30 dias, com intervalo mínimo de 27 e máximo de 33 dias (há exceções, como o primeiro faturamento). *(fatos-chave: 27, 33)*

**Resposta do C2_final:** A distribuidora não define um intervalo fixo para leitura do medidor. O que é garantido é que o consumidor pode acompanhar a leitura a qualquer tempo, e, se houver problema, o reparo é feito em até 15 dias.

**Fontes citadas:**

  - `D01-art243`: Quando instalar medição externa, a distribuidora deve assegurar meio que permita ao consumidor acompanhar a leitura do medidor a qualquer tempo. § 1º Quando houver deficiência que impossibilite o acompanhamento da leitura internamente na unidade consumidora, a distribuidora deve providenciar o reparo em até 15 dias após ter conhecimento do fato.

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Outro erro: diz que não há intervalo fixo e fala de reparo em 15 dias.*

### C2_final · T2-14 (ruido)

**Pergunta:** conta de lus veio com um valor cobrado a mais e eu ja paguei eles so me devolvem o que paguei a mais ou tem alguma coisa alem disso

**Gabarito:** A quantia paga a mais deve ser devolvida em dobro, atualizada pelo IPCA e com juros de 1% ao mês; a devolução só é simples se a distribuidora comprovar que o erro foi causado pelo consumidor ou, em condições específicas, por terceiro. *(fatos-chave: em dobro)*

**Resposta do C2_final:** Eles devem devolver o valor que você pagou a mais, mas em dobro. Isso inclui a correção pelo IPCA. Se a distribuidora provar que o erro foi por sua responsabilidade, só devolve o valor pago a mais, sem dobrar.

**Fontes citadas:**

  - `D14-q12`: [página gov.br; sha256 ea7bc2fa102b]

  - `D01-art323-p2`: No caso do inciso II do caput, a distribuidora deve devolver de acordo com as seguintes disposições: I - a quantia recebida indevidamente deve ser devolvida em dobro, independentemente de dolo ou culpa da distribuidora, salvo hipótese do § 3º; II - o valor do inciso I deste parágrafo deve ser atualizado pelo Índice Nacional de Preços ao Consumidor Amplo – IPCA;

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*Agora também cita a correção pelo IPCA.*

### C2_final · T2-15 (ruido)

**Pergunta:** tenho uma conta de lus de quatro meses atras ficou sem pagar a impresa ainda pode cortar minha lus por causa dela

**Gabarito:** Em regra, não: o corte é vedado depois de 90 dias da fatura vencida e não paga, salvo se a distribuidora comprovar que não cortou antes por determinação judicial ou outro motivo justificável. *(fatos-chave: 90 dias)*

**Resposta do C2_final:** Sim, a distribuidora pode cortar sua energia por falta de pagamento, desde que tenha notificado você com pelo menos três dias de antecedência, por escrito ou na fatura. Se você não pagou a conta de quatro meses, isso pode justificar o corte. Mas, se você apresentar comprovante de quitação no momento da suspensão, a energia não pode ser cortada.

**Fontes citadas:**

  - `D01-art636`: A distribuidora pode suspender o fornecimento de energia elétrica por falta de pagamento caso o consumidor e demais usuários, após ter recebido a notificação de suspensão, não paguem os valores da prestação do serviço de energia elétrica, observado o direito de cancelamento das cobranças do art. 635.

  - `D14-q10`: [página gov.br; sha256 fa7fbcaeba38]

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Pergunta de voz que o portão barrava no C2 original; agora responde que a empresa PODE cortar pela conta de 4 meses.*

### C2_final · T2-17 (multi_trecho)

**Pergunta:** Descobri que a empresa me cobrou a mais na conta de luz. Quanto ela tem que me devolver, com qual correção e até quando?

**Gabarito:** Deve devolver em dobro (simples apenas se comprovar erro atribuível ao consumidor ou, em condições específicas, a terceiro), com atualização pelo IPCA e juros de mora de 1% ao mês, até o segundo ciclo de faturamento posterior à constatação. *(fatos-chave: em dobro, IPCA, 1% ao mês)*

**Resposta do C2_final:** A distribuidora deve devolver o valor pago a mais em dobro, se a cobrança ocorreu por motivo atribuível ao consumidor ou a terceiros. A devolução deve ser feita no ciclo de faturamento posterior à constatação, com prazo máximo de 36 ciclos. Se a distribuidora comprovar que foi responsabilidade exclusiva do consumidor, a devolução será apenas o valor pago a mais.

**Fontes citadas:**

  - `D01-art324`: Art. 324. A distribuidora deve observar os seguintes procedimentos no caso de, por motivo atribuível ao consumidor e demais usuários, faturar valores incorretos ou faturar sem utilizar a leitura do sistema de medição: I - faturamento a maior: devolver ao consumidor e demais usuários as quantias recebidas indevidamente, no ciclo de faturamento posterior à constatação, correspondentes ao período fат

  - `D14-q20`: [página gov.br; sha256 bba1e6401d96]

  - `D14-q12`: [página gov.br; sha256 23487574d03e]

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Inverte a regra: diz que a devolução é em dobro quando a culpa é do consumidor ou de terceiros, e cita um prazo de 36 ciclos de outro artigo.*
