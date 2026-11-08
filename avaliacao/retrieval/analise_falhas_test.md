# Análise pós-hoc das falhas de recuperação no split test (Fase 4)

> **Natureza deste documento:** análise feita **depois** da medição única no test, para o relatório
> e para a escolha dos "5 erros" da Fase 8. Ela **não altera** o gabarito congelado
> (`avaliacao/teste.jsonl`, v2) nem o número oficial. As classificações "provavelmente relevante"
> abaixo são minhas e aguardam a validação do Pedro.

**Configuração medida:** busca densa (bge-m3), top-3, τ = 0,6038 (`avaliacao/retrieval/limiar.json`).

**Resultado oficial no test (gabarito v2):** recall@3 = 17/26 (0,654); recall@1 = 11/26 (0,423).
**Dev, para comparação:** recall@3 = 15/16 (0,938).

## As 9 perguntas sem trecho gold no top-3

| Pergunta | Tipo | O que veio no top-3 | Leitura pós-hoc |
|---|---|---|---|
| T-002 (corte na sexta-feira) | direta | `D14-q10` em 1º | **Provavelmente relevante:** a página "Corte de energia" da ANEEL diz que não pode haver corte às sextas-feiras. Faltou no gabarito v2 |
| T-021 (aviso antes do corte) | coloquial | `D14-q10` em 2º | **Provavelmente relevante:** a mesma página informa o aviso de 15 dias por falta de pagamento |
| T-024 (BPC dá desconto?) | coloquial | `D16-s00` em 1º | **Provavelmente relevante:** a página da Tarifa Social da ANEEL cita quem recebe o BPC |
| T-026 (conta estimada na enchente) | coloquial | `D14-q20` em 1º | **Parcial:** fala da média de 12 meses sem acesso ao medidor, mas não da situação de emergência do art. 321 |
| T-011 (critério de renda) | direta | gold `D17-p1-s03` em 4º | Falha de ordenação (gold em 4º) |
| T-033 (aviso antes do corte, voz) | ruído | `D14-q10` só em 4º | Falha: o ruído de voz piorou o ranking |
| T-034 (geladeira com insulina, voz) | ruído | itens do Módulo 9 sem o prazo de 1 dia útil | Falha: o ruído de voz ("geladera", "insolina") |
| T-036 (BPC, voz) | ruído | trechos sem relação | Falha: o ruído de voz ("aposentadu", "disconto", "lus") |
| T-037 (30 horas sem luz em emergência) | multi_trecho | item 105 do Módulo 4 e art. 621 | Falha: nem o item 220-A nem a Tabela 4 do Anexo 8.B entraram no top-5 |

## Leitura

- **Gabarito ainda incompleto:** o procedimento do v2 (fatos-chave literais entre os 15 vizinhos da
  resposta gabarito) não pegou páginas explicativas que dizem a mesma coisa com outras palavras,
  como "quinze dias" e "sextas-feiras" na página D14-q10. Considerando as leituras "provavelmente
  relevante", o recall@3 pós-hoc seria de 20/26 (0,77), ou 21/26 (0,81) contando a T-026.
- **Falhas reais de busca:**
  - **Ruído de voz:** 3 das 4 perguntas de voz falharam no test (1 de 2 no dev). O portão também
    recusa a maior parte delas (nota abaixo de τ). É o principal ponto fraco, e afeta o público-alvo.
  - **Pergunta de várias partes com tabela** (T-037): o trecho de tabela tem pouco texto e não se
    parece com a pergunta.
- **Diferença entre dev e test:** o dev tem só 16 perguntas respondíveis. O intervalo de confiança
  de 95% do recall@3 no dev é de [0,72; 0,99], e o do test é de [0,46; 0,81]. Os dois se sobrepõem,
  então a diferença é compatível com variação de amostra.

## Correções candidatas (para a Fase 8, medidas só no dev ou num re-teste documentado)

1. **Normalizar perguntas de voz** antes da busca: corrigir a grafia por um léxico do domínio,
   como "lus" → "luz" e "religa" → "religar".
2. **Busca híbrida com reranker** como alternativa: no dev, empatou em recall@3 com a densa, mas
   teve MRR e recall@5 maiores.
3. **Enriquecer os trechos de tabela** com o texto do item que os cita (item 214 do Módulo 8).
4. **Completar o gabarito** com as leituras acima, se o Pedro validar, e reportar a medição como
   v3, separada, em vez de substituir o v2.
