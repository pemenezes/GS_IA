# Revisão do test novo, T2 (Fase 8B)

**Para:** Pedro. São 24 perguntas novas, que não repetem nenhuma das 60 do test original, das 45 de calibração nem das 13 extras. Depois da sua revisão, o T2 é congelado com hash e só é usado **uma vez**, no fim, para medir C1, C2 original e C2 final.

Para cada pergunta, confira: (1) se a pergunta é clara; (2) se o **gabarito** está certo pelo texto dos trechos mostrados; (3) se os fatos-chave fazem sentido. Responda no chat só com as correções, por exemplo: "T2-04: incluir que a dívida continua".

Composição: 7 diretas, 5 coloquiais, 3 de voz (versões das coloquiais T2-08 a T2-10), 3 multi-trecho, 2 "não consta", 2 fora do domínio e 2 sobre a agenda.

> Nesta versão, os trechos de páginas gov.br aparecem como hash. A versão completa está em `avaliacao/runs/local/revisao_teste2_completa.md`.

### T2-01 (direta)

**Pergunta:** Em quanto tempo a distribuidora deve fazer a troca de titularidade da conta de luz de uma casa na área urbana?

**Gabarito:** Em até 3 dias úteis na área urbana (5 dias úteis na área rural).

**Fatos-chave:** 3 dias úteis

- **Trecho gold `D01-art138-p3`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO III – DOS CONTRATOS - DISPOSIÇÕES GERAIS > Seção VI – Da Alteração de Titularidade > Art. 138 § 3º Ao fornecer o protocolo, a distribuidora deve esclarecer o consumidor e demais usuários sobre as condições para alteração de titularidade do art. 346. § 4º A distribuidora deve realizar a alteração de titularidade no prazo de até 3 dias úteis na área urbana e 5 dias úteis na área rural. § 5º O indeferimento da alteração de titularidade deve ser fornecido por escrito ao consumidor e demais usuários, observado o art. 416. § 6º A alteração de titularidade implica encerramento do vínculo do titular atual nessas instalações. § 7º No caso de unidade consumidora com microgeração ou minigeração distribuída, a alteração de titularidade pode ser solicitada antes da conclusão do processo de conexão, devendo ser observadas as seguintes disposições:

- **Equivalente `D14-q04`:** [página gov.br; sha256 a394624e233f]

### T2-02 (direta)

**Pergunta:** Quantas opções de data de vencimento da fatura a distribuidora deve oferecer ao consumidor?

**Gabarito:** Pelo menos seis datas de vencimento, distribuídas uniformemente ao longo do mês.

**Fatos-chave:** 6 datas

- **Trecho gold `D01-art338`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XI – DA FATURA E DO PAGAMENTO > Seção IV – Do Vencimento > Art. 338 Art. 338. A distribuidora deve oferecer pelo menos seis datas de vencimento da fatura para escolha do consumidor e demais usuários, distribuídas uniformemente em intervalos regulares ao longo do mês. § 1º O oferecimento disposto no caput deve ser realizado na solicitação da conexão, na alteração de titularidade ou sempre que solicitado. § 2º A data de vencimento da fatura somente pode ser modificada em um intervalo maior ou igual a 12 meses, com autorização prévia do consumidor e demais usuários.

- **Equivalente `D01-anexoi-clausulaquarta-p2`:** REN 1.000/2021 > ANEXO I – CONTRATO DE ADESÃO - GRUPO B > Cláusula Quarta 4.1.5. alterar a modalidade tarifária, desde que previsto na regulação da ANEEL, no prazo de até 30 dias; 4.1.6. solicitar a inspeção do sistema de medição de faturamento, para verificação do correto funcionamento dos equipamentos; 4.1.7. responder apenas por débitos relativos à unidade consumidora de sua titularidade ou vinculados à sua pessoa, não sendo obrigado a assinar termo relacionado à débitos de terceiros; 4.1.8. não ser cobrado pelo consumo de energia elétrica reativa excedente; 4.1.9. ter a devolução em dobro dos pagamentos de valores cobrados indevidamente, acrescidos de atualização monetária e juros, salvo hipótese de erro atribuível ao CONSUMIDOR e fato de terceiro; 4.1.10. escolher a data para o vencimento da fatura, dentre as seis datas, no mínimo, disponibilizadas pela DISTRIBUIDORA, exceto na moda

- **Equivalente `D14-q03`:** [página gov.br; sha256 5954722c9711]

### T2-03 (direta)

**Pergunta:** De quanto em quanto tempo a distribuidora deve fazer a leitura do medidor de uma casa?

**Gabarito:** A cada aproximadamente 30 dias, com intervalo mínimo de 27 e máximo de 33 dias (há exceções, como o primeiro faturamento).

**Fatos-chave:** 27, 33

- **Trecho gold `D01-art260`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO IX – DA LEITURA > Seção II – Do Período de Leitura > Art. 260 Art. 260. A leitura do sistema de medição para o grupo B deve ser realizada em intervalos de aproximadamente 30 dias, observados o mínimo de 27 e o máximo de 33 dias, de acordo com o calendário de leitura. § 1º Para o primeiro faturamento, ou no caso de remanejamento de rota ou reprogramação do calendário, as leituras podem ser realizadas em intervalos de no mínimo 15 e no máximo 47 dias. § 2º No caso de remanejamento de rota ou reprogramação do calendário, o consumidor deve ser informado, por escrito, com antecedência de pelo menos um ciclo de faturamento, admitida a inclusão de mensagem na fatura de energia elétrica.

### T2-04 (direta)

**Pergunta:** Depois de quanto tempo do vencimento de uma conta não paga a distribuidora não pode mais cortar a luz por causa dela?

**Gabarito:** Depois de 90 dias da data da fatura vencida e não paga, o corte é vedado, salvo se a distribuidora comprovar que não cortou antes por determinação judicial ou outro motivo justificável.

**Fatos-chave:** 90 dias

- **Trecho gold `D01-art357`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XIII – DA SUSPENSÃO DO FORNECIMENTO > Seção IV – Da Suspensão Precedida de Notificação > Art. 357 Art. 357. É vedada a suspensão do fornecimento após o decurso do prazo de 90 dias, contado da data da fatura vencida e não paga, sendo permitida depois desse prazo apenas se ficar comprovado que o impedimento da sua execução decorreu de determinação judicial ou outro motivo justificável. Parágrafo único. Na situação de impedimento de execução disposta no caput, a contagem do prazo deve ser suspensa pelo período do impedimento.

- **Equivalente `D01-anexoi-clausulasexta-p2`:** REN 1.000/2021 > ANEXO I – CONTRATO DE ADESÃO - GRUPO B > Cláusula Sexta 6.2.3. razões de ordem técnica. 6.3. A notificação da suspensão deve ser escrita, específica e com entrega comprovada ou, alternativamente, impressa em destaque na fatura, com antecedência mínima de: - 3 dias úteis, por razões de ordem técnica ou de segurança; ou - 15 dias, nos casos de inadimplemento. 6.4. A execução da suspensão do fornecimento somente poderá ser realizada no horário das 8h às 18h, em dias úteis, sendo vedada às sextas-feiras e nas vésperas de feriado. 6.5. A DISTRIBUIDORA não pode suspender o fornecimento após o decurso do prazo de 90 dias, contado da data da fatura vencida e não paga, exceto se comprovar que não suspendeu por determinação judicial ou outro motivo justificável.

### T2-05 (direta)

**Pergunta:** Com quantos dias de antecedência a conta de luz de uma casa deve ser entregue antes do vencimento?

**Gabarito:** Pelo menos 5 dias úteis antes do vencimento (10 dias úteis para poder público, iluminação pública e serviço público).

**Fatos-chave:** 5 dias úteis

- **Trecho gold `D01-art337`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XI – DA FATURA E DO PAGAMENTO > Seção IV – Do Vencimento > Art. 337 Art. 337. O prazo para vencimento da fatura, contado da data da apresentação, deve ser de pelo menos: I - 10 dias úteis: para unidade consumidora enquadrada nas classes poder público, iluminação pública e serviço público; e II - 5 dias úteis: nas demais situações.

- **Equivalente `D01-anexoi-clausulaquarta-p3`:** REN 1.000/2021 > ANEXO I – CONTRATO DE ADESÃO - GRUPO B > Cláusula Quarta 4.1.11. receber, até o mês de maio do ano corrente, declaração de quitação anual de débitos do ano anterior. 4.2. São direitos do CONSUMIDOR na modalidade tarifária convencional e branca: 4.2.1. receber a fatura com periodicidade mensal, considerando as leituras do sistema de medição ou, caso aplicável, o valor por estimativa; 4.2.1.1. A fatura deve ser entregue, conforme opção do CONSUMIDOR, em versão impressa ou eletrônica, com antecedência do vencimento de pelo menos: - 10 dias úteis, para classe poder público, Iluminação Pública e Serviço Público; - 5 dias úteis, para demais classes. 4.2.2. receber gratuitamente o código de pagamento ou outro meio que viabilize o pagamento da fatura, de forma alternativa à emissão da segunda via; e 4.2.3. ser informado, na fatura, sobre a existência de faturas não pagas; 4.3. S

- **Equivalente `D14-q03`:** [página gov.br; sha256 5954722c9711]

### T2-06 (direta)

**Pergunta:** Se a vistoria da entrada de energia de uma ligação nova for reprovada, em quanto tempo a distribuidora deve entregar o relatório com os motivos?

**Gabarito:** Em até 3 dias úteis após a conclusão da vistoria, com os motivos e as providências corretivas necessárias.

**Fatos-chave:** 3 dias úteis

- **Trecho gold `D01-art94`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO II – DA CONEXÃO > Seção XIV – Da Vistoria e Instalação da Medição > Art. 94 Art. 94. Ocorrendo reprovação das instalações de entrada de energia elétrica na vistoria, a distribuidora deve disponibilizar ao consumidor e demais usuários, em até 3 dias úteis após a conclusão do procedimento, o relatório de vistoria, com os motivos e as providências corretivas necessárias. § 1º Após resolvidas as pendências detectadas no relatório de vistoria, o consumidor e demais usuários devem formalizar nova solicitação de vistoria à distribuidora. § 2º A distribuidora pode reprovar a vistoria caso o projeto das instalações de entrada de energia não tenha sido aprovado, desde que: I - a exigência de aprovação prévia esteja estabelecida na norma técnica da distribuidora; II - o consumidor e demais usuários tenham sido informados no orçamento de conexão; e 

### T2-07 (direta)

**Pergunta:** Na hora de cobrar uma conta de luz atrasada, a empresa pode me humilhar ou me ameaçar?

**Gabarito:** Não. Pelo art. 42 do CDC, na cobrança de débitos o consumidor inadimplente não pode ser exposto a ridículo nem submetido a constrangimento ou ameaça.

**Fatos-chave:** ridicul

*Fato-chave do Pedro: 'o cliente não é ridicularizado'. A raiz 'ridicul' reconhece 'ridículo' e 'ridicularizado'; a negação é conferida na revisão manual.*

- **Trecho gold `D10-art42`:** CDC (Lei 8.078/1990) > TÍTULO I – Dos Direitos do Consumidor > CAPÍTULO V – Das Práticas Comerciais > SEÇÃO V – Da Cobrança de Dívidas > Art. 42 Art. 42. Na cobrança de débitos, o consumidor inadimplente não será exposto a ridículo, nem será submetido a qualquer tipo de constrangimento ou ameaça. Parágrafo único. O consumidor cobrado em quantia indevida tem direito à repetição do indébito, por valor igual ao dobro do que pagou em excesso, acrescido de correção monetária e juros legais, salvo hipótese de engano justificável.

### T2-08 (coloquial)

**Pergunta:** Aluguei uma casa e o morador antigo deixou conta de luz atrasada. A empresa pode me obrigar a pagar essa dívida pra passar a conta pro meu nome?

**Gabarito:** Não. A distribuidora não pode condicionar a alteração de titularidade ao pagamento de débito de titularidade de terceiros, nem exigir que você assine termo assumindo essa dívida.

**Fatos-chave:** moradores anteriores

*Fato-chave ajustado pelo Pedro ('moradores anteriores', como na página D14-q04); a conferência manual é a referência.*

- **Trecho gold `D01-art346-p1`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XII – DO INADIMPLEMENTO > Seção IV – Das Restrições pelo Inadimplemento > Art. 346 Art. 346. Quando o consumidor e demais usuários solicitarem os serviços dispostos nesta Resolução, a exemplo de conexão nova, alteração de titularidade, religação, aumento de carga e a contratação de fornecimentos especiais, a distribuidora não pode exigir ou condicionar a execução: I - ao pagamento de débito não autorizado pelo consumidor e demais usuários ou de débito de titularidade de terceiros; II - à assinatura de qualquer termo em que o consumidor e demais usuários assumam a responsabilidade por débito de titularidade de terceiros, a exemplo de termo de aceite, de assunção, de responsabilidade ou de confissão de dívida; ou III - à transferência em sistema de débitos de titularidade de terceiros para o titular ou novo titular das instalações. § 1º O 

- **Equivalente `D14-q04`:** [página gov.br; sha256 a394624e233f]

- **Equivalente `D01-anexoi-clausulaquarta-p2`:** REN 1.000/2021 > ANEXO I – CONTRATO DE ADESÃO - GRUPO B > Cláusula Quarta 4.1.5. alterar a modalidade tarifária, desde que previsto na regulação da ANEEL, no prazo de até 30 dias; 4.1.6. solicitar a inspeção do sistema de medição de faturamento, para verificação do correto funcionamento dos equipamentos; 4.1.7. responder apenas por débitos relativos à unidade consumidora de sua titularidade ou vinculados à sua pessoa, não sendo obrigado a assinar termo relacionado à débitos de terceiros; 4.1.8. não ser cobrado pelo consumo de energia elétrica reativa excedente; 4.1.9. ter a devolução em dobro dos pagamentos de valores cobrados indevidamente, acrescidos de atualização monetária e juros, salvo hipótese de erro atribuível ao CONSUMIDOR e fato de terceiro; 4.1.10. escolher a data para o vencimento da fatura, dentre as seis datas, no mínimo, disponibilizadas pela DISTRIBUIDORA, exceto na moda

### T2-09 (coloquial)

**Pergunta:** A conta de luz veio com um valor cobrado a mais e eu já paguei. Eles só me devolvem o que paguei a mais ou tem alguma coisa além disso?

**Gabarito:** A quantia paga a mais deve ser devolvida em dobro, atualizada pelo IPCA e com juros de 1% ao mês; a devolução só é simples se a distribuidora comprovar que o erro foi causado pelo consumidor ou, em condições específicas, por terceiro.

**Fatos-chave:** em dobro

- **Trecho gold `D01-art323-p2`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO X – DO FATURAMENTO > Seção XVII – Do Faturamento Incorreto > Art. 323 § 1º No caso do inciso I do caput, a distribuidora deve parcelar o pagamento em número de parcelas igual ao dobro do período em que ocorreu o erro ou a ausência de faturamento, ou, por solicitação do consumidor e demais usuários, em número menor de parcelas, incluindo as parcelas nas faturas de energia elétrica subsequentes. § 2º No caso do inciso II do caput, a distribuidora deve devolver de acordo com as seguintes disposições: I - a quantia recebida indevidamente deve ser devolvida em dobro, independentemente de dolo ou culpa da distribuidora, salvo hipótese do § 3º; II - o valor do inciso I deste parágrafo deve ser atualizado pelo Índice Nacional de Preços ao Consumidor Amplo – IPCA; e

- **Equivalente `D01-anexoi-clausulaquarta-p2`:** REN 1.000/2021 > ANEXO I – CONTRATO DE ADESÃO - GRUPO B > Cláusula Quarta 4.1.5. alterar a modalidade tarifária, desde que previsto na regulação da ANEEL, no prazo de até 30 dias; 4.1.6. solicitar a inspeção do sistema de medição de faturamento, para verificação do correto funcionamento dos equipamentos; 4.1.7. responder apenas por débitos relativos à unidade consumidora de sua titularidade ou vinculados à sua pessoa, não sendo obrigado a assinar termo relacionado à débitos de terceiros; 4.1.8. não ser cobrado pelo consumo de energia elétrica reativa excedente; 4.1.9. ter a devolução em dobro dos pagamentos de valores cobrados indevidamente, acrescidos de atualização monetária e juros, salvo hipótese de erro atribuível ao CONSUMIDOR e fato de terceiro; 4.1.10. escolher a data para o vencimento da fatura, dentre as seis datas, no mínimo, disponibilizadas pela DISTRIBUIDORA, exceto na moda

- **Equivalente `D14-q12`:** [página gov.br; sha256 8d5fd9f964a6]

- **Equivalente `D10-art42`:** CDC (Lei 8.078/1990) > TÍTULO I – Dos Direitos do Consumidor > CAPÍTULO V – Das Práticas Comerciais > SEÇÃO V – Da Cobrança de Dívidas > Art. 42 Art. 42. Na cobrança de débitos, o consumidor inadimplente não será exposto a ridículo, nem será submetido a qualquer tipo de constrangimento ou ameaça. Parágrafo único. O consumidor cobrado em quantia indevida tem direito à repetição do indébito, por valor igual ao dobro do que pagou em excesso, acrescido de correção monetária e juros legais, salvo hipótese de engano justificável.

### T2-10 (coloquial)

**Pergunta:** Tenho uma conta de luz de quatro meses atrás que ficou sem pagar. A empresa ainda pode cortar minha luz por causa dela?

**Gabarito:** Em regra, não: o corte é vedado depois de 90 dias da fatura vencida e não paga, salvo se a distribuidora comprovar que não cortou antes por determinação judicial ou outro motivo justificável.

**Fatos-chave:** 90 dias

- **Trecho gold `D01-art357`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XIII – DA SUSPENSÃO DO FORNECIMENTO > Seção IV – Da Suspensão Precedida de Notificação > Art. 357 Art. 357. É vedada a suspensão do fornecimento após o decurso do prazo de 90 dias, contado da data da fatura vencida e não paga, sendo permitida depois desse prazo apenas se ficar comprovado que o impedimento da sua execução decorreu de determinação judicial ou outro motivo justificável. Parágrafo único. Na situação de impedimento de execução disposta no caput, a contagem do prazo deve ser suspensa pelo período do impedimento.

- **Equivalente `D01-anexoi-clausulasexta-p2`:** REN 1.000/2021 > ANEXO I – CONTRATO DE ADESÃO - GRUPO B > Cláusula Sexta 6.2.3. razões de ordem técnica. 6.3. A notificação da suspensão deve ser escrita, específica e com entrega comprovada ou, alternativamente, impressa em destaque na fatura, com antecedência mínima de: - 3 dias úteis, por razões de ordem técnica ou de segurança; ou - 15 dias, nos casos de inadimplemento. 6.4. A execução da suspensão do fornecimento somente poderá ser realizada no horário das 8h às 18h, em dias úteis, sendo vedada às sextas-feiras e nas vésperas de feriado. 6.5. A DISTRIBUIDORA não pode suspender o fornecimento após o decurso do prazo de 90 dias, contado da data da fatura vencida e não paga, exceto se comprovar que não suspendeu por determinação judicial ou outro motivo justificável.

### T2-11 (coloquial)

**Pergunta:** Minha conta vence antes do meu salário cair. Posso pedir pra mudar o dia do vencimento?

**Gabarito:** Sim. A distribuidora deve oferecer pelo menos seis datas de vencimento para você escolher; depois da mudança, a data só pode ser alterada de novo após 12 meses.

**Fatos-chave:** 6 datas, 12 meses

- **Trecho gold `D01-art338`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XI – DA FATURA E DO PAGAMENTO > Seção IV – Do Vencimento > Art. 338 Art. 338. A distribuidora deve oferecer pelo menos seis datas de vencimento da fatura para escolha do consumidor e demais usuários, distribuídas uniformemente em intervalos regulares ao longo do mês. § 1º O oferecimento disposto no caput deve ser realizado na solicitação da conexão, na alteração de titularidade ou sempre que solicitado. § 2º A data de vencimento da fatura somente pode ser modificada em um intervalo maior ou igual a 12 meses, com autorização prévia do consumidor e demais usuários.

- **Equivalente `D14-q03`:** [página gov.br; sha256 5954722c9711]

- **Equivalente `D01-anexoi-clausulaquarta-p2`:** REN 1.000/2021 > ANEXO I – CONTRATO DE ADESÃO - GRUPO B > Cláusula Quarta 4.1.5. alterar a modalidade tarifária, desde que previsto na regulação da ANEEL, no prazo de até 30 dias; 4.1.6. solicitar a inspeção do sistema de medição de faturamento, para verificação do correto funcionamento dos equipamentos; 4.1.7. responder apenas por débitos relativos à unidade consumidora de sua titularidade ou vinculados à sua pessoa, não sendo obrigado a assinar termo relacionado à débitos de terceiros; 4.1.8. não ser cobrado pelo consumo de energia elétrica reativa excedente; 4.1.9. ter a devolução em dobro dos pagamentos de valores cobrados indevidamente, acrescidos de atualização monetária e juros, salvo hipótese de erro atribuível ao CONSUMIDOR e fato de terceiro; 4.1.10. escolher a data para o vencimento da fatura, dentre as seis datas, no mínimo, disponibilizadas pela DISTRIBUIDORA, exceto na moda

### T2-12 (coloquial)

**Pergunta:** Minha conta deste mês veio com 40 dias de consumo. A leitura do relógio não tinha que ser feita todo mês?

**Gabarito:** Sim: a leitura deve ser feita a cada cerca de 30 dias, com no mínimo 27 e no máximo 33 dias (salvo exceções, como o primeiro faturamento ou mudança de rota). Se passar de 33 dias, a distribuidora deve proporcionalizar o consumo ao número máximo de dias permitido.

**Fatos-chave:** 33

- **Trecho gold `D01-art260`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO IX – DA LEITURA > Seção II – Do Período de Leitura > Art. 260 Art. 260. A leitura do sistema de medição para o grupo B deve ser realizada em intervalos de aproximadamente 30 dias, observados o mínimo de 27 e o máximo de 33 dias, de acordo com o calendário de leitura. § 1º Para o primeiro faturamento, ou no caso de remanejamento de rota ou reprogramação do calendário, as leituras podem ser realizadas em intervalos de no mínimo 15 e no máximo 47 dias. § 2º No caso de remanejamento de rota ou reprogramação do calendário, o consumidor deve ser informado, por escrito, com antecedência de pelo menos um ciclo de faturamento, admitida a inclusão de mensagem na fatura de energia elétrica.

- **Trecho gold `D01-art285`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO X – DO FATURAMENTO > Seção I – Das Disposições Gerais > Art. 285 Art. 285. Caso a leitura do Grupo B seja efetuada sem observar os intervalos de tempo estabelecidos no art. 260, ressalvadas as exceções dispostas nesta Resolução, a distribuidora deve faturar de acordo com as seguintes disposições: I - não atingido o limite mínimo de 27 dias: faturar o consumo medido, vedada a aplicação do custo de disponibilidade; e II - ultrapassado o limite máximo de 33 dias: proporcionalizar o consumo registrado pelo número máximo de dias permitido, ajustando a leitura atual ao consumo resultante.

### T2-13 (ruido, voz)

**Pergunta:** aluguei uma casa o morador antigo deixou conta de lus atrasado a impresa pode me obrigar a pagar essa divida pra passar a conta pro meu nome

**Gabarito:** Não. A distribuidora não pode condicionar a alteração de titularidade ao pagamento de débito de titularidade de terceiros, nem exigir que você assine termo assumindo essa dívida.

**Fatos-chave:** moradores anteriores

*Versão com ruído de voz de T2-08.*

### T2-14 (ruido, voz)

**Pergunta:** conta de lus veio com um valor cobrado a mais e eu ja paguei eles so me devolvem o que paguei a mais ou tem alguma coisa alem disso

**Gabarito:** A quantia paga a mais deve ser devolvida em dobro, atualizada pelo IPCA e com juros de 1% ao mês; a devolução só é simples se a distribuidora comprovar que o erro foi causado pelo consumidor ou, em condições específicas, por terceiro.

**Fatos-chave:** em dobro

*Versão com ruído de voz de T2-09.*

### T2-15 (ruido, voz)

**Pergunta:** tenho uma conta de lus de quatro meses atras ficou sem pagar a impresa ainda pode cortar minha lus por causa dela

**Gabarito:** Em regra, não: o corte é vedado depois de 90 dias da fatura vencida e não paga, salvo se a distribuidora comprovar que não cortou antes por determinação judicial ou outro motivo justificável.

**Fatos-chave:** 90 dias

*Versão com ruído de voz de T2-10.*

### T2-16 (multi_trecho)

**Pergunta:** Comprei um apartamento e quero passar a conta de luz pro meu nome. Em quanto tempo a distribuidora tem que fazer a troca e ela pode exigir que eu pague as contas atrasadas do antigo dono?

**Gabarito:** A troca deve ser feita em até 3 dias úteis na área urbana (5 na rural), e a distribuidora não pode condicioná-la ao pagamento de débito de titularidade de terceiros.

**Fatos-chave:** 3 dias úteis, terceiros

- **Trecho gold `D01-art138-p3`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO III – DOS CONTRATOS - DISPOSIÇÕES GERAIS > Seção VI – Da Alteração de Titularidade > Art. 138 § 3º Ao fornecer o protocolo, a distribuidora deve esclarecer o consumidor e demais usuários sobre as condições para alteração de titularidade do art. 346. § 4º A distribuidora deve realizar a alteração de titularidade no prazo de até 3 dias úteis na área urbana e 5 dias úteis na área rural. § 5º O indeferimento da alteração de titularidade deve ser fornecido por escrito ao consumidor e demais usuários, observado o art. 416. § 6º A alteração de titularidade implica encerramento do vínculo do titular atual nessas instalações. § 7º No caso de unidade consumidora com microgeração ou minigeração distribuída, a alteração de titularidade pode ser solicitada antes da conclusão do processo de conexão, devendo ser observadas as seguintes disposições:

- **Trecho gold `D01-art346-p1`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XII – DO INADIMPLEMENTO > Seção IV – Das Restrições pelo Inadimplemento > Art. 346 Art. 346. Quando o consumidor e demais usuários solicitarem os serviços dispostos nesta Resolução, a exemplo de conexão nova, alteração de titularidade, religação, aumento de carga e a contratação de fornecimentos especiais, a distribuidora não pode exigir ou condicionar a execução: I - ao pagamento de débito não autorizado pelo consumidor e demais usuários ou de débito de titularidade de terceiros; II - à assinatura de qualquer termo em que o consumidor e demais usuários assumam a responsabilidade por débito de titularidade de terceiros, a exemplo de termo de aceite, de assunção, de responsabilidade ou de confissão de dívida; ou III - à transferência em sistema de débitos de titularidade de terceiros para o titular ou novo titular das instalações. § 1º O 

- **Equivalente `D14-q04`:** [página gov.br; sha256 a394624e233f]

### T2-17 (multi_trecho)

**Pergunta:** Descobri que a empresa me cobrou a mais na conta de luz. Quanto ela tem que me devolver, com qual correção e até quando?

**Gabarito:** Deve devolver em dobro (simples apenas se comprovar erro atribuível ao consumidor ou, em condições específicas, a terceiro), com atualização pelo IPCA e juros de mora de 1% ao mês, até o segundo ciclo de faturamento posterior à constatação.

**Fatos-chave:** em dobro, IPCA, 1% ao mês

- **Trecho gold `D01-art323-p1`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO X – DO FATURAMENTO > Seção XVII – Do Faturamento Incorreto > Art. 323 Art. 323. A distribuidora, no caso de faturar valores incorretos, não apresentar fatura ou faturar sem utilizar a leitura do sistema de medição nos casos em que não haja previsão nesta Resolução, sem prejuízo das penalidades cabíveis, deve observar os seguintes procedimentos: I - faturamento a menor ou ausência de faturamento: cobrar do consumidor e demais usuários as quantias não recebidas, limitando-se aos últimos 3 ciclos de faturamento imediatamente anteriores ao ciclo vigente; e II - faturamento a maior: devolver ao consumidor e demais usuários, até o segundo ciclo de faturamento posterior à constatação, as quantias recebidas indevidamente nos últimos 60 ciclos de faturamento imediatamente anteriores à constatação. (Suspensos os efeitos referentes ao prazo de 60 (

- **Trecho gold `D01-art323-p2`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO X – DO FATURAMENTO > Seção XVII – Do Faturamento Incorreto > Art. 323 § 1º No caso do inciso I do caput, a distribuidora deve parcelar o pagamento em número de parcelas igual ao dobro do período em que ocorreu o erro ou a ausência de faturamento, ou, por solicitação do consumidor e demais usuários, em número menor de parcelas, incluindo as parcelas nas faturas de energia elétrica subsequentes. § 2º No caso do inciso II do caput, a distribuidora deve devolver de acordo com as seguintes disposições: I - a quantia recebida indevidamente deve ser devolvida em dobro, independentemente de dolo ou culpa da distribuidora, salvo hipótese do § 3º; II - o valor do inciso I deste parágrafo deve ser atualizado pelo Índice Nacional de Preços ao Consumidor Amplo – IPCA; e

- **Trecho gold `D01-art323-p3`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO X – DO FATURAMENTO > Seção XVII – Do Faturamento Incorreto > Art. 323 § 2º No caso do inciso II do caput, a distribuidora deve devolver de acordo com as seguintes disposições: III - devem ser calculados e acrescidos os juros de mora à razão de 1% ao mês pro rata die sobre o valor atualizado obtido do inciso II deste parágrafo. § 3º A devolução prevista no inciso I do § 2º deve ser simples caso a distribuidora comprove que o faturamento a maior foi causado por motivo atribuível: I - exclusivamente ao consumidor ou demais usuários, em que deve ser observado o art. 324; ou II - a terceiro, desde que satisfeitas as seguintes condições: a) a distribuidora demonstre que adotou as medidas cabíveis para mitigar a possibilidade de faturamento a maior; b) o terceiro não preste ou tenha prestado serviços à distribuidora ou ao grupo empresarial de q

- **Equivalente `D14-q12`:** [página gov.br; sha256 8d5fd9f964a6]

### T2-18 (multi_trecho)

**Pergunta:** Tenho placa solar em casa. Por quanto tempo valem os créditos de energia que sobram e o que acontece com eles quando vencem?

**Gabarito:** Os créditos expiram em 60 meses após o faturamento em que foram gerados e, depois disso, são revertidos para a modicidade tarifária, sem compensação ao consumidor.

**Fatos-chave:** 60 meses, modicidade tarifária

- **Trecho gold `D09-art13-p1`:** Lei 14.300/2022 > CAPÍTULO IV – DA COMPENSAÇÃO DE ENERGIA ELÉTRICA > Art. 13 Art. 13. Os créditos de energia elétrica expiram em 60 (sessenta) meses após a data do faturamento em que foram gerados e serão revertidos em prol da modicidade tarifária sem que o consumidor participante do SCEE faça jus a qualquer forma de compensação após esse prazo. § 1º Os créditos são determinados em termos de energia elétrica ativa, não estando sua quantidade sujeita a alterações em razão da variação nos valores das tarifas de energia elétrica. § 2º Para abatimento do consumo, devem ser utilizados sempre os créditos mais antigos da unidade consumidora participante do SCEE.

- **Trecho gold `D01-art655l`:** REN 1.000/2021 > TÍTULO II – PARTE ESPECIAL > CAPÍTULO XI – DA MICROGERAÇÃO E MINIGERAÇÃO DISTRIBUÍDA E DO SISTEMA DE COMPENSAÇÃO DE ENERGIA ELÉTRICA (SCEE) > Seção III – Do Faturamento de unidades consumidoras do SCEE > Art. 655-L Art. 655-L. Os créditos de energia expiram em 60 meses após a data do faturamento em que foram gerados. § 1º Ao final do prazo de validade estabelecido no caput, os créditos de energia devem ser revertidos para a modicidade tarifária, sem que o consumidor tenha direito a qualquer forma de compensação. § 2º Os créditos de energia são estabelecidos em termos de energia elétrica ativa, e a sua quantidade não se altera devido a variações nas tarifas de energia elétrica.

- **Equivalente `D19-s01-p2`:** [página gov.br; sha256 32498b8b1b11]

### T2-19 (nao_consta)

**Pergunta:** Qual é o horário de funcionamento da agência de atendimento presencial da Enel no centro de São Paulo?

**Gabarito:** Não consta na base: o assistente deve recusar e indicar o canal oficial.

### T2-20 (nao_consta)

**Pergunta:** Quantas reclamações contra a Enel a ANEEL recebeu em 2025?

**Gabarito:** Não consta na base: o assistente deve recusar e indicar o canal oficial.

### T2-21 (fora_dominio)

**Pergunta:** Como faço para tirar a segunda via do RG?

**Gabarito:** Fora do domínio: o assistente trata só de energia elétrica.

### T2-22 (fora_dominio)

**Pergunta:** A operadora de TV por assinatura pode cobrar multa se eu cancelar antes de um ano?

**Gabarito:** Fora do domínio: o assistente trata só de energia elétrica.

### T2-23 (dinamica)

**Pergunta:** Vai ter desligamento programado no Brás na quinta-feira?

**Gabarito:** Sim: há parada programada em Brás em 12/11/2026: manutenção programada das 08:00 às 10:00 (registro PAR-00434).

**Agenda:** {'bairro': 'Brás', 'data': '2026-11-12', 'registros_esperados': ['PAR-00434'], 'situacao': 'com_parada'}

### T2-24 (dinamica)

**Pergunta:** Tem manutenção programada de energia em Perdizes amanhã?

**Gabarito:** Não há parada programada registrada para Perdizes em 11/11/2026.

**Agenda:** {'bairro': 'Perdizes', 'data': '2026-11-11', 'registros_esperados': [], 'situacao': 'sem_parada'}
