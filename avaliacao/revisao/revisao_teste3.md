# Revisão do test T3 (Fase 8B)

**Para:** Pedro. São 24 perguntas sobre temas que nenhum conjunto anterior usou como gabarito (T1, T2, calibração e extras da agenda). Depois da sua revisão, o T3 é congelado com hash e usado **uma vez**, para medir o C2 original e o C2+M sem o viés de seleção do T1 e do T2. O sistema não muda depois do T3.

Para cada pergunta, confira: (1) se a pergunta é clara; (2) se o **gabarito** está certo pelo texto dos trechos mostrados; (3) se os fatos-chave fazem sentido. Responda no chat só com as correções, por exemplo: "T3-04: incluir que a reclamação é por escrito".

Composição: 7 diretas, 5 coloquiais, 3 de voz (versões das coloquiais T3-08 a T3-10), 3 multi-trecho, 2 "não consta", 2 fora do domínio e 2 sobre a agenda.

> Nesta versão, os trechos de páginas gov.br aparecem como hash. A versão completa está em `avaliacao/runs/local/revisao_teste3_completa.md`.

### T3-01 (direta)

**Pergunta:** A distribuidora é obrigada a parcelar a conta de luz atrasada de um consumidor da subclasse residencial baixa renda que pedir o parcelamento?

**Gabarito:** Sim, se o débito não tiver sido parcelado antes: para a subclasse residencial baixa renda, o parcelamento é obrigatório quando o consumidor pede, com no mínimo três parcelas, na fatura de energia ou, a pedido do consumidor, por outro meio.

**Fatos-chave:** 3 parcelas

- **Trecho gold `D01-art344`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XII – DO INADIMPLEMENTO > Seção II – Do Parcelamento do Débito > Art. 344 Art. 344. A distribuidora pode parcelar ou reparcelar o débito, mediante solicitação expressa do consumidor e demais usuários. § 1º No caso de unidade consumidora classificada em uma das subclasses residencial baixa renda: I - o parcelamento do débito que não tenha sido anteriormente parcelado é obrigatório, desde que haja solicitação do consumidor e observado o mínimo de três parcelas; e II - o parcelamento deve ser realizado na fatura de energia elétrica ou, mediante solicitação do consumidor, por outro meio. § 2º O atraso no pagamento implica incidência de multa, juros de mora e atualização monetária, conforme disposto no art. 343. § 3º As parcelas podem ser incluídas nas faturas de energia elétrica subsequentes com a devida especificação. § 4º O consumidor e de

- **Equivalente `D14-q18`:** [página gov.br; sha256 357164b6c3ec]

### T3-02 (direta)

**Pergunta:** A distribuidora pode exigir caução ou outra garantia de uma casa que deixou de pagar mais de uma conta de luz no mesmo ano?

**Gabarito:** Não. A exigência de garantias (quando há mais de uma fatura não paga em 12 meses) não se aplica à classe residencial, à subclasse rural residencial nem a prestadores de serviços públicos essenciais.

**Fatos-chave:** residencial

*A negação (não se aplica à classe residencial) é conferida na revisão manual.*

- **Trecho gold `D01-art345-p1`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XII – DO INADIMPLEMENTO > Seção III – Das Garantias > Art. 345 Art. 345. A distribuidora pode exigir o oferecimento de garantias, limitadas ao valor do débito, quando houver inadimplemento de mais de uma fatura mensal durante um período de 12 meses. § 1º O disposto no caput não se aplica ao consumidor que seja prestador de serviços públicos essenciais, ou cuja unidade consumidora pertença à classe residencial ou subclasse rural residencial da classe rural. § 2º As garantias devem ser realizadas por depósito-caução em espécie, seguro ou carta-fiança, a critério do consumidor e demais usuários, e vigorar pelos 11 meses posteriores à penúltima fatura não paga. § 3º No caso de consumidor potencialmente livre, a distribuidora pode exigir, alternativamente ao oferecimento de garantias, a apresentação de contrato de compra de energia no ACL, ob

### T3-03 (direta)

**Pergunta:** Quando a inspeção constata que o medidor da distribuidora está com defeito, em quanto tempo ela tem que trocar o aparelho?

**Gabarito:** Em até 30 dias após a data em que o defeito foi constatado, informando ao consumidor, por meio auditável, as leituras do medidor retirado e do instalado.

**Fatos-chave:** 30 dias

- **Trecho gold `D01-art252`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO VIII – DA MEDIÇÃO PARA FATURAMENTO > Seção IV – Da Inspeção do Sistema de Medição > Art. 252 Art. 252. A distribuidora deve adotar as seguintes providências na realização da inspeção do sistema de medição: I - emitir o Termo de Ocorrência e Inspeção – TOI, em formulário próprio, elaborado conforme instruções da ANEEL e entregar ao consumidor e demais usuários, conforme art. 591; II - substituir os equipamentos do sistema de medição de sua responsabilidade que apresentem defeito por desempenho inadequado, em até 30 dias após a data de constatação do defeito, informando ao solicitante, por meio auditável, as informações das leituras do medidor retirado e do instalado; III - solicitar a substituição ou a correção dos equipamentos do sistema de medição de responsabilidade do consumidor e demais usuários que apresentem desempenho inadequado; 

### T3-04 (direta)

**Pergunta:** A distribuidora me notificou que vai cobrar uma diferença no faturamento e eu não concordo. Até quando posso reclamar e em quanto tempo ela tem que responder?

**Gabarito:** Você pode registrar reclamação na distribuidora em até 30 dias contados da notificação; ela deve solucionar a reclamação e comunicar a você no prazo de 15 dias.

**Fatos-chave:** 30 dias, 15 dias

- **Trecho gold `D01-art325-p2`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO X – DO FATURAMENTO > Seção XVIII – Da Compensação do Faturamento > Art. 325 § 1º A distribuidora deve notificar o consumidor por escrito, por modalidade que permita a comprovação do recebimento, contendo obrigatoriamente: III - no caso de levantamento periódico de iluminação pública, os itens do § 5º do art. 463; e III-A - no caso de recebimento irregular de benefício associado ao SCEE, descrição da irregularidade e os indícios associados, bem como dos valores a serem refaturados; e IV - direito, prazo e canais para reclamação, conforme § 2º. § 2º O consumidor pode registrar reclamação na distribuidora, em até 30 dias contados a partir da notificação, se discordar da diferença a cobrar ou a devolver informada. § 3º No caso do § 2º, a distribuidora deve solucionar a reclamação e comunicar ao consumidor no prazo de 15 dias.

### T3-05 (direta)

**Pergunta:** Posso escolher pagar a minha conta de luz pelo PIX? Depois que eu pedir, a partir de quando a mudança passa a valer?

**Gabarito:** Sim. O consumidor pode escolher o código de resposta rápida (QR) do PIX como forma de pagamento e cancelar a escolha a qualquer tempo; a mudança deve estar disponível até o primeiro ciclo completo de faturamento seguinte ao pedido.

**Fatos-chave:** ciclo completo

- **Trecho gold `D01-art339a`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XI – DA FATURA E DO PAGAMENTO > Seção V – Do Pagamento > Art. 339-A Art. 339-A O consumidor e demais usuários podem escolher o código de resposta rápida do PIX como forma de pagamento das faturas, podendo cancelar a escolha a qualquer tempo. Parágrafo Único. As mudanças na forma de pagamento devem estar disponíveis até o primeiro ciclo completo de faturamento subsequente à solicitação do consumidor e demais usuários.

- **Equivalente `D01-art327`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XI – DA FATURA E DO PAGAMENTO > Seção I – Das Disposições Gerais > Art. 327 Art. 327. A fatura de energia elétrica deve conter, de forma clara e objetiva e observadas as disposições do Módulo 11 do PRODIST, as seguintes informações: I - identificação do consumidor e demais usuários; II - identificação da unidade consumidora ou demais instalações; III - valor total devido e data de vencimento; IV - grandezas medidas e faturadas; V - tarifas aplicadas; VI - valores adicionais a serem cobrados quando da aplicação das bandeiras tarifárias, caso aplicável; VII - valores relativos aos produtos, serviços e atividades prestados; VIII - histórico de consumo, caso aplicável; IX - impostos e contribuições incidentes; e X - código para pagamento e linha numérica digitável ou, caso aplicável, mensagem indicativa de que o pagamento será realizado por 

### T3-06 (direta)

**Pergunta:** Quem tem placa solar e acumulou créditos de energia em meses diferentes: quais créditos são usados primeiro para abater o consumo?

**Gabarito:** Sempre os créditos mais antigos da unidade consumidora participante do Sistema de Compensação de Energia Elétrica (SCEE).

**Fatos-chave:** mais antigos

- **Trecho gold `D09-art13-p2`:** Lei 14.300/2022 > CAPÍTULO IV – DA COMPENSAÇÃO DE ENERGIA ELÉTRICA > Art. 13 § 2º Para abatimento do consumo, devem ser utilizados sempre os créditos mais antigos da unidade consumidora participante do SCEE. § 3º Os créditos de energia elétrica existentes no momento do encerramento da relação contratual do consumidor participante do SCEE perante a concessionária ou permissionária de distribuição de energia elétrica serão mantidos em nome do titular pelo prazo estabelecido no caput deste artigo, exceto se houver outra unidade consumidora sob mesma titularidade de pessoa física ou jurídica, inclusive matriz e filiais, consórcio, cooperativa ou condomínio voluntário ou edilício ou qualquer outra forma de associação civil instituída para esse fim, atendida pela mesma concessionária ou permissionária de distribuição de energia elétrica, e poderão ser, nesse caso, realocados para a respectiva 

- **Equivalente `D09-art13-p1`:** Lei 14.300/2022 > CAPÍTULO IV – DA COMPENSAÇÃO DE ENERGIA ELÉTRICA > Art. 13 Art. 13. Os créditos de energia elétrica expiram em 60 (sessenta) meses após a data do faturamento em que foram gerados e serão revertidos em prol da modicidade tarifária sem que o consumidor participante do SCEE faça jus a qualquer forma de compensação após esse prazo. § 1º Os créditos são determinados em termos de energia elétrica ativa, não estando sua quantidade sujeita a alterações em razão da variação nos valores das tarifas de energia elétrica. § 2º Para abatimento do consumo, devem ser utilizados sempre os créditos mais antigos da unidade consumidora participante do SCEE.

### T3-07 (direta)

**Pergunta:** Na Tarifa Social de Energia Elétrica, se a casa consumir 100 kWh no mês, sobre quanto de energia é feita a cobrança?

**Gabarito:** A gratuidade vale para o consumo de até 80 kWh por mês; com 100 kWh, é cobrada só a parcela excedente, ou seja, 20 kWh.

**Fatos-chave:** 20 kWh

*O limite de 80 kWh já aparece no T1 (T-010 e T-012); o fato novo é a cobrança só do excedente. Troca da pergunta sobre a Lei 13.460, por decisão do Pedro.*

- **Trecho gold `D17-p1-s08`:** [página gov.br; sha256 94548e9124be]

- **Equivalente `D17-p2-q02`:** [página gov.br; sha256 638d9e1839b1]

- **Equivalente `D02-art1`:** Lei 12.212/2010 > Art. 1º Art. 1º A Tarifa Social de Energia Elétrica, de que trata a Lei nº 10.438, de 26 de abril de 2002, para os consumidores enquadrados na Subclasse Residencial Baixa Renda, caracterizada por descontos incidentes sobre a tarifa aplicável à classe residencial das distribuidoras de energia elétrica, será calculada conforme indicado a seguir: I - para a parcela do consumo de energia elétrica inferior ou igual a 80 kWh/mês (oitenta quilowatts-hora por mês), o desconto será de 100% (cem por cento); e II - para a parcela do consumo de energia elétrica superior a 80 kWh/mês (oitenta quilowatts-hora por mês), o desconto será de 0% (zero por cento);

### T3-08 (coloquial)

**Pergunta:** Cortaram minha luz por falta de pagamento, mas eu tinha pagado a conta pelo PIX uma hora antes do corte. Esse corte foi certo?

**Gabarito:** Não. A suspensão é considerada indevida quando a fatura foi paga pelo código QR do PIX antes da execução da suspensão (ou até a data limite da notificação).

**Fatos-chave:** indevida

- **Trecho gold `D01-art361`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XIII – DA SUSPENSÃO DO FORNECIMENTO > Seção VI – Da Suspensão Indevida > Art. 361 Art. 361. A suspensão do fornecimento de energia elétrica é considerada indevida se: I - o pagamento da fatura tiver sido realizado até a data limite contida na notificação para suspensão do fornecimento; ou I -A - o pagamento da fatura tiver sido realizado por meio de código de resposta rápida do PIX antes da execução da suspensão do fornecimento; ou II - a suspensão for efetuada sem observar o disposto nesta Resolução.

### T3-09 (coloquial)

**Pergunta:** O leiturista colocou na conta que houve impedimento de acesso, mas meu relógio de luz fica no muro, virado pra calçada. Isso conta como impedimento?

**Gabarito:** Não. O impedimento de acesso exige, ao mesmo tempo, medidor dentro do imóvel sem livre acesso ao leiturista e leitura não feita por responsabilidade do consumidor; a leitura frustrada em medidor no limite da via pública não caracteriza impedimento de acesso.

**Fatos-chave:** via pública

- **Trecho gold `D01-art277`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO IX – DA LEITURA > Seção V – Do Impedimento de Acesso para Leitura > Art. 277 Art. 277. O impedimento de acesso para fins de leitura é caracterizado pela ocorrência, de forma conjunta, dos seguintes requisitos: I - o medidor se encontra em ambiente interno ao imóvel da unidade consumidora, sem livre acesso ao leiturista; e II - a leitura local não é realizada por responsabilidade do consumidor. Parágrafo Único. A leitura frustrada em medidores localizados no limite da via pública não se caracteriza como impedimento de acesso para fins de leitura.

### T3-10 (coloquial)

**Pergunta:** Recebo o benefício do Luz do Povo e vou me mudar de casa no mês que vem. Perco o benefício?

**Gabarito:** Não automaticamente. É preciso manter o CadÚnico atualizado e informar à distribuidora os dados da nova unidade consumidora, para que ela verifique a elegibilidade e vincule o benefício ao novo endereço.

**Fatos-chave:** CadÚnico

- **Trecho gold `D17-p2-q08`:** [página gov.br; sha256 dae4b10cb514]

### T3-11 (coloquial)

**Pergunta:** Estou inscrito no CadÚnico, mas a conta de luz da casa onde moro está no nome do proprietário. Como faço pra receber o benefício do Luz do Povo?

**Gabarito:** É preciso entrar em contato com a distribuidora e apresentar a documentação exigida para vincular o seu cadastro à unidade consumidora; os procedimentos podem variar conforme a distribuidora.

**Fatos-chave:** document

*A raiz 'document' reconhece 'documentação' e 'documentos'.*

- **Trecho gold `D17-p2-q07`:** [página gov.br; sha256 90496f6eb91c]

### T3-12 (coloquial)

**Pergunta:** Parcelei uma dívida da conta de luz e agora entrou um dinheiro. Se eu quitar as parcelas antes, pago menos juros?

**Gabarito:** Sim. O consumidor tem direito ao pagamento antecipado do parcelamento, total ou parcial, com redução proporcional dos juros e demais acréscimos.

**Fatos-chave:** proporcional

- **Trecho gold `D01-art344`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XII – DO INADIMPLEMENTO > Seção II – Do Parcelamento do Débito > Art. 344 Art. 344. A distribuidora pode parcelar ou reparcelar o débito, mediante solicitação expressa do consumidor e demais usuários. § 1º No caso de unidade consumidora classificada em uma das subclasses residencial baixa renda: I - o parcelamento do débito que não tenha sido anteriormente parcelado é obrigatório, desde que haja solicitação do consumidor e observado o mínimo de três parcelas; e II - o parcelamento deve ser realizado na fatura de energia elétrica ou, mediante solicitação do consumidor, por outro meio. § 2º O atraso no pagamento implica incidência de multa, juros de mora e atualização monetária, conforme disposto no art. 343. § 3º As parcelas podem ser incluídas nas faturas de energia elétrica subsequentes com a devida especificação. § 4º O consumidor e de

### T3-13 (ruido, voz)

**Pergunta:** cortaram minha lus por falta pagamento mas eu tinha pagado a conta pelo pix uma hora antes do corte esse corte foi certo

**Gabarito:** Não. A suspensão é considerada indevida quando a fatura foi paga pelo código QR do PIX antes da execução da suspensão (ou até a data limite da notificação).

**Fatos-chave:** indevida

*Versão com ruído de voz de T3-08.*

### T3-14 (ruido, voz)

**Pergunta:** o leiturista colocou na conta que houve impedimento acesso mas meu relogio de lus fica no muro virado pra calcada isso conta como impedimento

**Gabarito:** Não. O impedimento de acesso exige, ao mesmo tempo, medidor dentro do imóvel sem livre acesso ao leiturista e leitura não feita por responsabilidade do consumidor; a leitura frustrada em medidor no limite da via pública não caracteriza impedimento de acesso.

**Fatos-chave:** via pública

*Versão com ruído de voz de T3-09.*

### T3-15 (ruido, voz)

**Pergunta:** recebo o benefisio do lus do povo e vou me mudar de casa no mes vem perco o benefisio

**Gabarito:** Não automaticamente. É preciso manter o CadÚnico atualizado e informar à distribuidora os dados da nova unidade consumidora, para que ela verifique a elegibilidade e vincule o benefício ao novo endereço.

**Fatos-chave:** CadÚnico

*Versão com ruído de voz de T3-10.*

### T3-16 (multi_trecho)

**Pergunta:** Sou baixa renda e pedi pra parcelar uma conta de luz atrasada. A distribuidora pode negar? E se eu atrasar uma parcela, o que pode ser cobrado?

**Gabarito:** Não pode negar se o débito não tiver sido parcelado antes: para baixa renda, o parcelamento é obrigatório a pedido do consumidor, com no mínimo três parcelas. O atraso no pagamento implica multa de até 2%, atualização monetária pelo IPCA e juros de mora de 1% ao mês.

**Fatos-chave:** 3 parcelas, 2%, 1% ao mês

- **Trecho gold `D01-art344`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XII – DO INADIMPLEMENTO > Seção II – Do Parcelamento do Débito > Art. 344 Art. 344. A distribuidora pode parcelar ou reparcelar o débito, mediante solicitação expressa do consumidor e demais usuários. § 1º No caso de unidade consumidora classificada em uma das subclasses residencial baixa renda: I - o parcelamento do débito que não tenha sido anteriormente parcelado é obrigatório, desde que haja solicitação do consumidor e observado o mínimo de três parcelas; e II - o parcelamento deve ser realizado na fatura de energia elétrica ou, mediante solicitação do consumidor, por outro meio. § 2º O atraso no pagamento implica incidência de multa, juros de mora e atualização monetária, conforme disposto no art. 343. § 3º As parcelas podem ser incluídas nas faturas de energia elétrica subsequentes com a devida especificação. § 4º O consumidor e de

- **Trecho gold `D01-art343`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XII – DO INADIMPLEMENTO > Seção I – Dos Acréscimos Moratórios > Art. 343 Art. 343. No caso de atraso no pagamento da fatura, a distribuidora pode cobrar multa, atualização monetária pelo Índice Nacional de Preços ao Consumidor Amplo – IPCA e juros de mora de 1% ao mês calculados pro rata die. § 1º A cobrança de multa pode ser realizada no percentual de até 2%. § 2º A multa e os juros de mora incidem sobre o valor total da fatura, com exceção das seguintes parcelas: I - a contribuição para o custeio, a expansão e a melhoria do serviço de iluminação pública e de sistemas de monitoramento para segurança e preservação de logradouros públicos e a taxa ou tarifa dos serviços de limpeza urbana e de manejo de resíduos sólidos, as quais se sujeitam às multas, atualizações e juros de mora estabelecidos na legislação específica; II - os valores rel

- **Equivalente `D14-q18`:** [página gov.br; sha256 357164b6c3ec]

### T3-17 (multi_trecho)

**Pergunta:** Em que situações o corte de luz por falta de pagamento é considerado indevido e, nesse caso, em quanto tempo a distribuidora tem que religar?

**Gabarito:** É indevido se a fatura foi paga até a data limite da notificação, se foi paga pelo PIX antes da execução do corte ou se a suspensão não seguiu a REN 1.000. A religação deve ocorrer em até 4 horas, contadas da constatação ou da comunicação do consumidor, em qualquer dia e horário, e a distribuidora deve creditar a compensação.

**Fatos-chave:** 4 horas, PIX

- **Trecho gold `D01-art361`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XIII – DA SUSPENSÃO DO FORNECIMENTO > Seção VI – Da Suspensão Indevida > Art. 361 Art. 361. A suspensão do fornecimento de energia elétrica é considerada indevida se: I - o pagamento da fatura tiver sido realizado até a data limite contida na notificação para suspensão do fornecimento; ou I -A - o pagamento da fatura tiver sido realizado por meio de código de resposta rápida do PIX antes da execução da suspensão do fornecimento; ou II - a suspensão for efetuada sem observar o disposto nesta Resolução.

- **Trecho gold `D01-art362`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO XIII – DA SUSPENSÃO DO FORNECIMENTO > Seção VII – Da Religação das Instalações > Art. 362 Art. 362. A distribuidora deve restabelecer o fornecimento de energia elétrica nos seguintes prazos, contados de forma contínua e sem interrupção: I - 4 horas: para religação em caso de suspensão indevida do fornecimento; II - 4 horas: para religação de urgência de instalações localizadas em área urbana; III - 8 horas: para religação de urgência de instalações localizadas em área rural; IV - 24 horas: para religação normal de instalações localizadas em área urbana; e V - 48 horas: para religação normal de instalações localizadas em área rural. § 1º Em caso de suspensão indevida: I - a contagem do prazo de religação inicia a partir da constatação da situação ou comunicação do consumidor e demais usuários, independentemente do dia e horário; e II - a 

### T3-18 (multi_trecho)

**Pergunta:** A distribuidora vai trocar o medidor da minha casa porque ele está com defeito. Quanto tempo ela tem pra fazer a troca e eu tenho que pagar pelo medidor novo?

**Gabarito:** A troca deve ser feita em até 30 dias após constatado o defeito, e o medidor é fornecido e instalado pela distribuidora sem custo (o equipamento é gratuito); a substituição deve ser comunicada ao consumidor por correspondência específica com o motivo.

**Fatos-chave:** 30 dias, gratuit

*A raiz 'gratuit' reconhece 'gratuito' e 'gratuitamente'; 'sem custo' é conferido na revisão manual.*

- **Trecho gold `D01-art252`:** REN 1.000/2021 > TÍTULO I – PARTE GERAL > CAPÍTULO VIII – DA MEDIÇÃO PARA FATURAMENTO > Seção IV – Da Inspeção do Sistema de Medição > Art. 252 Art. 252. A distribuidora deve adotar as seguintes providências na realização da inspeção do sistema de medição: I - emitir o Termo de Ocorrência e Inspeção – TOI, em formulário próprio, elaborado conforme instruções da ANEEL e entregar ao consumidor e demais usuários, conforme art. 591; II - substituir os equipamentos do sistema de medição de sua responsabilidade que apresentem defeito por desempenho inadequado, em até 30 dias após a data de constatação do defeito, informando ao solicitante, por meio auditável, as informações das leituras do medidor retirado e do instalado; III - solicitar a substituição ou a correção dos equipamentos do sistema de medição de responsabilidade do consumidor e demais usuários que apresentem desempenho inadequado; 

- **Trecho gold `D14-q16`:** [página gov.br; sha256 a70b8dcbd01a]

### T3-19 (nao_consta)

**Pergunta:** Qual foi o lucro da Enel Distribuição São Paulo em 2025?

**Gabarito:** Não consta na base: o assistente deve recusar e indicar o canal oficial.

### T3-20 (nao_consta)

**Pergunta:** Quanto custa, em média, instalar um sistema de energia solar de 5 kW numa casa em São Paulo?

**Gabarito:** Não consta na base: o assistente deve recusar e indicar o canal oficial.

### T3-21 (fora_dominio)

**Pergunta:** Como faço para dar entrada no seguro-desemprego?

**Gabarito:** Fora do domínio: o assistente trata só de energia elétrica.

### T3-22 (fora_dominio)

**Pergunta:** O condomínio pode me multar por barulho depois das 22h?

**Gabarito:** Fora do domínio: o assistente trata só de energia elétrica.

### T3-23 (dinamica)

**Pergunta:** Vai ter desligamento programado de energia no Mandaqui na segunda-feira, dia 16?

**Gabarito:** Sim: há parada programada em Mandaqui em 16/11/2026: manutenção programada das 10:00 às 13:00 (registro PAR-00482).

**Agenda:** {'bairro': 'Mandaqui', 'data': '2026-11-16', 'registros_esperados': ['PAR-00482'], 'situacao': 'com_parada'}

### T3-24 (dinamica)

**Pergunta:** Tem manutenção programada de luz em Pinheiros na sexta-feira?

**Gabarito:** Não há parada programada registrada para Pinheiros em 13/11/2026.

**Agenda:** {'bairro': 'Pinheiros', 'data': '2026-11-13', 'registros_esperados': [], 'situacao': 'sem_parada'}
