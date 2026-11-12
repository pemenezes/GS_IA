# Conferência pós-correção do test (Fase 8): C2 com as correções A e C

**Para:** Pedro. **Itens:** 10. São as respostas do C2 com as correções A (reescrita da pergunta)
e C (busca híbrida com reranker) cujo **sentido mudou** em relação à conferência do C2 original.
Os critérios são os mesmos. Responda no chat só com as discordâncias.

As demais herdam o veredito que você já deu ao C2 original:
- **mesma resposta:** T-005, T-008, T-009;
- **redação diferente, mesmo sentido:** T-002, T-003, T-006, T-013, T-015, T-021, T-022, T-026, T-030, T-033;
- **continuam recusadas:** T-024, T-036, T-040.

O test já tinha sido visto quando as correções foram feitas; por isso esta medição é rotulada
"pós-correção" e não substitui o placar oficial.

> Nesta versão, as citações de páginas gov.br aparecem como hash (licença CC BY-ND). A versão completa está em `avaliacao/runs/local/conferencia_pos_correcao_completa.md`.



## Respostas do C2 + A + C cujo sentido mudou

### C2_AC · T-007 (direta)

**Pergunta:** A distribuidora pode negar o ressarcimento de um aparelho queimado dizendo que a cidade estava em situação de emergência decretada?

**Gabarito:** Não. Essa possibilidade existia (inciso VIII do art. 621 da REN 1.000 e alínea b do item 14 do Módulo 9 do PRODIST), mas foi revogada pela REN 1.137/2025 (arts. 19 e 20); hoje a situação de emergência não está entre os casos em que a distribuidora pode deixar de ressarcir. *(fatos-chave: Revoga-se o inciso VIII do art. 621)*

**Resposta do C2_AC:** Sim, a distribuidora pode negar o ressarcimento se a perturbação que causou o dano tiver ocorrido em função de Situação de Emergência ou de Calamidade Pública decretada por autoridade competente. Isso está previsto no item 14 do Módulo 9 do PRODIST.

**Fontes citadas:**

  - `D08-s9.1-item14`: a perturbação que tenha dado causa ao dano reclamado tiver ocorrido em função de Situação de Emergência ou de Calamidade Pública decretada por autoridade competente.

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Agora afirma que a distribuidora PODE negar, citando a alínea b do item 14 do PRODIST Módulo 9, que foi revogada pelo art. 20 da REN 1.137/2025. O trecho trazia um ALERTA dizendo isso, e o modelo o ignorou. Antes, o C2 recusava.*

### C2_AC · T-011 (direta)

**Pergunta:** Qual é o critério de renda do CadÚnico para ter direito à Tarifa Social de Energia Elétrica?

**Gabarito:** Família inscrita no CadÚnico com renda mensal por pessoa de até meio salário mínimo (ou ter na casa quem recebe o BPC). *(fatos-chave: meio salário mínimo nacional)*

**Resposta do C2_AC:** O critério de renda é até meio salário mínimo nacional per capita. Isso se aplica a famílias inscritas no CadÚnico. Também há casos com renda até três salários mínimos, se houver membro com deficiência que precise de equipamentos elétricos para tratamento.

**Fontes citadas:**

  - `D17-p2-q04`: [página gov.br; sha256 38128fb77e18]

  - `D02-art2-p1`: I - seus moradores deverão pertencer a uma família inscrita no Cadastro Único para Programas Sociais do Governo Federal - CadÚnico, com renda familiar mensal per capita menor ou igual a meio salário mínimo nacional

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*Agora dá o critério geral (meio salário mínimo por pessoa) e apresenta os 3 salários mínimos como exceção. Antes: incorreta.*

### C2_AC · T-018 (direta)

**Pergunta:** O Código de Defesa do Consumidor obriga a empresa de energia a fornecer o serviço de forma contínua?

**Gabarito:** Sim. Concessionárias de serviços essenciais devem prestar serviços adequados, eficientes, seguros e contínuos (art. 22 do CDC). *(fatos-chave: contínuos)*

**Resposta do C2_AC:** Não. O Código de Defesa do Consumidor não obriga diretamente a empresa de energia a fornecer o serviço de forma contínua. A continuidade é regulamentada pela Resolução ANEEL nº 1.000/2021, que estabelece critérios específicos para a qualidade do serviço, incluindo a continuidade, e o direito do consumidor a compensação se houver violação dos limites de continuidade.

**Fontes citadas:**

  - `D01-art433`: O consumidor e demais usuários têm o direito de receber compensação financeira em sua fatura de energia no caso da distribuidora violar os limites de continuidade individuais relativos às suas instalações.

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Agora diz que o CDC NÃO obriga a continuidade, com o art. 22 do CDC entre os trechos fornecidos. Antes: correta.*

### C2_AC · T-020 (coloquial)

**Pergunta:** Cortaram a luz da minha casa mas eu estava com tudo pago, foi erro deles. Quanto tempo eles têm pra voltar com a luz?

**Gabarito:** Na suspensão indevida, a religação deve ocorrer em até 4 horas, e a distribuidora deve creditar uma compensação. *(fatos-chave: 4 horas)*

**Resposta do C2_AC:** Eles têm até 1 hora para comunicar a você a causa e o tempo previsto para a luz voltar. Se a interrupção for emergencial, a distribuidora deve voltar com a luz o mais rápido possível, mas não há um prazo fixo para a restauração. Para saber o prazo exato, entre em contato com a distribuidora.

**Fontes citadas:**

  - `D13-s4.8-item105`: As distribuidoras devem comunicar aos consumidores, por meio dos canais disponíveis, a provável causa da interrupção, a área afetada e o tempo previsto para a normalização do fornecimento em até 15 (quinze) minutos após o conhecimento da causa da interrupção. Independentemente do momento em que a causa for identificada, a comunicação contendo essas informações deve ser realizada em até  1 (uma) 20

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*A reescrita trocou 'cortaram por erro' por 'interrupção programada', e a resposta diz que não há prazo fixo. Na suspensão indevida, são 4 horas. Antes: correta.*

### C2_AC · T-028 (coloquial)

**Pergunta:** Minha conta veio com bandeira vermelha. Isso é uma taxa a mais que vão me cobrar?

**Gabarito:** Sim: nas bandeiras amarela e vermelha há um adicional, que deve vir destacado na fatura; na bandeira verde não há acréscimo. *(fatos-chave: destacados nas faturas)*

**Resposta do C2_AC:** Não. A bandeira vermelha não é uma taxa a mais que você paga de forma separada. Ela indica que os custos de geração da energia estão mais altos, e por isso há uma cobrança adicional proporcional ao seu consumo. Mas isso já está incluído na sua conta de energia elétrica.

**Fontes citadas:**

  - `D15-q03`: [página gov.br; sha256 da33deef91c2]

  - `D15-q05`: [página gov.br; sha256 8519a121aa1e]

**Pré-classificação:** 🟡 parcial · afirma algo falso? **sim**

*Começa com 'Não, não é uma taxa a mais', mas agora reconhece uma cobrança adicional proporcional ao consumo; não diz que vem destacada na fatura. Antes: incorreta.*

### C2_AC · T-032 (ruido)

**Pergunta:** cortaram lus da minha casa mas eu tava com tudo pago foi erro deles quantu tempo eles tem pra voltar com a lus

**Gabarito:** Na suspensão indevida, a religação deve ocorrer em até 4 horas, e a distribuidora deve creditar uma compensação. *(fatos-chave: 4 horas)*

**Resposta do C2_AC:** Se você tinha tudo pago e a energia foi cortada por erro, a distribuidora deve voltar com a energia em até 4 horas. Isso está previsto na Resolução 1.000/2021.

**Fontes citadas:**

  - `D01-art362`: Art. 362. A distribuidora deve restabelecer o fornecimento de energia elétrica nos seguintes prazos, contados de forma contínua e sem interrupção: I - 4 horas: para religação em caso de suspensão indevida do fornecimento;

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*Pergunta de voz que o portão barrava; agora responde 4 horas na suspensão indevida, citando o art. 362.*

### C2_AC · T-034 (ruido)

**Pergunta:** minha geladera queimou quando a lus voltou e eu guardo insolina nela depois que eu reclamar quantu tempo a impresa tem pra vir ver geladera

**Gabarito:** Para equipamento que guarda alimentos perecíveis ou medicamentos, a verificação deve ser feita em até um dia útil. *(fatos-chave: um dia útil)*

**Resposta do C2_AC:** A distribuidora deve vir ver sua geladera em até 5 dias úteis, se não for necessária visita técnica. Se for necessária, o prazo é de até 10 dias úteis. Se a reclamação for sobre o medidor ou equipamentos, pode haver prazo de até 6 horas (área urbana).

**Fontes citadas:**

  - `D01-art408`: A distribuidora deve solucionar as reclamações do consumidor e demais usuários nos seguintes prazos, contados a partir da data do protocolo: I - até 5 dias úteis: caso não seja necessária a realização de visita técnica à unidade consumidora ou demais instalações; ou II - até 10 dias úteis: nas demais situações.

  - `D01-anexoi-clausulaoitava-p3`: A DISTRIBUIDORA deve solucionar as reclamações do CONSUMIDOR em até 5 dias úteis do protocolo, ressalvados os prazos de solução especiais estabelecidos na regulação da ANEEL.

**Pré-classificação:** ❌ incorreta · afirma algo falso? **sim**

*Pergunta de voz que o portão barrava; agora responde com os prazos de solução de reclamação (5 e 10 dias úteis) em vez da verificação em 1 dia útil para geladeira com medicamento. A reescrita tirou a insulina da pergunta.*

### C2_AC · T-037 (multi_trecho)

**Pergunta:** Fiquei sem luz por 30 horas na minha casa, na cidade, depois de um temporal em que foi decretada situação de emergência. A distribuidora tem que me compensar?

**Gabarito:** Sim. Em situação de emergência, cada interrupção acima do limite do indicador DISE gera compensação; para casa em área urbana atendida em baixa tensão, o limite do DISE é de 24 horas por evento, então 30 horas ultrapassa o limite. *(fatos-chave: Situação de Emergência que superar o limite do indicador DISE, 24)*

**Resposta do C2_AC:** Sim, a distribuidora deve compensar você. O temporal gerou situação de emergência, e a interrupção de 30 horas supera o limite do indicador DISE. O artigo 220-A do PRODIST exige compensação para interrupções em situações de emergência que ultrapassam os limites de continuidade.

**Fontes citadas:**

  - `D07-s8.2-item220a`: A distribuidora deve efetuar uma compensação ao consumidor ou central geradora de média ou baixa tensão para cada interrupção ocorrida em Situação de Emergência que superar o limite do indicador DISE.

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*Agora aplica a compensação por violação do limite do DISE em situação de emergência (item 220-A). Não diz o limite de 24 horas, mas a conclusão está certa. Antes: incorreta.*

### C2_AC · T-038 (multi_trecho)

**Pergunta:** Minha filha usa aparelho elétrico no tratamento em casa e nossa renda é de dois salários mínimos, estamos no CadÚnico. Temos direito à tarifa social? Que documento a empresa pede?

**Gabarito:** Sim: famílias do CadÚnico com renda de até 3 salários mínimos e alguém que precise de aparelho elétrico contínuo no tratamento têm direito; é preciso apresentar relatório e atestado assinados por médico e o comprovante do CadÚnico. *(fatos-chave: 3 (três) salários mínimos, relatório e atestado subscrito por profissional médico)*

**Resposta do C2_AC:** Sim, você tem direito à tarifa social. A empresa pede um relatório e atestado subscrito por profissional médico comprovando a necessidade do uso de equipamento elétrico para tratamento médico. O documento deve ser apresentado junto com o comprovante de inscrição no CadÚnico.

**Fontes citadas:**

  - `D17-p2-q04`: [página gov.br; sha256 a42388a6fd46]

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*Diz que tem direito e lista o relatório e o atestado médicos e o comprovante do CadÚnico; não repete o limite de 3 salários mínimos, mas responde ao caso de 2 salários mínimos.*

### C2_AC · T-039 (multi_trecho)

**Pergunta:** Pedi o ressarcimento um mês depois que meu aparelho queimou. Quanto tempo a empresa tem para me dar o resultado e, se aprovar, para pagar?

**Gabarito:** Resultado em até 15 dias (pedido feito em até 90 dias do dano) e, se aprovado, ressarcimento em até 20 dias. *(fatos-chave: 15 dias, 20 dias)*

**Resposta do C2_AC:** A empresa tem até 15 dias para te dar o resultado, porque você pediu o ressarcimento um mês depois que o aparelho queimou, o que está dentro dos 90 dias da ocorrência. Se aprovado, ela deve pagar em até 20 dias a partir do vencimento do prazo do art. 617 ou da disponibilização do resultado, o que ocorrer primeiro.

**Fontes citadas:**

  - `D01-art617`: Art. 617. A distribuidora deve disponibilizar ao consumidor o resultado da análise da solicitação de ressarcimento nos seguintes prazos, contados da data da verificação no local ou, caso esta não tenha sido realizada, da data da solicitação de ressarcimento: I - 15 dias: para solicitação de ressarcimento feita em até 90 dias da data provável da ocorrência do dano elétrico; ou II - 30 dias: para só

  - `D01-art618-p1`: Art. 618. No caso de deferimento da solicitação de ressarcimento, a distribuidora deve: I - escolher a forma de ressarcimento dentre as seguintes alternativas: a) conserto do equipamento danificado; b) substituição do equipamento danificado; c) pagamento em moeda corrente em valor equivalente a um equipamento novo; ou d) pagamento em moeda corrente em valor equivalente ao conserto; II - ressarcir 

**Pré-classificação:** ✅ correta · afirma algo falso? **nao**

*Agora dá os dois prazos: 15 dias para o resultado e 20 dias para o pagamento. Antes: parcial.*
