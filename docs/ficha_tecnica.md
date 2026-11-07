# Ficha Técnica: Luz Cidadã

**Versão:** 1 (Fase 1). Aprovada pelo Pedro em 07/11/2026. Componente desta disciplina:
*Inteligência* (Generative AI for Engineering).

**Equipe:** Anny Carolina (RM98295), Henrique Lima (RM551528), Pedro Menezes (RM97432).

## 1. Ficha

| Campo | Conteúdo |
|---|---|
| Nome do produto | **Luz Cidadã** |
| Cidadão e território | Moradores da Região Metropolitana de São Paulo, com prioridade para idosos, pessoas com deficiência, famílias com alguém que depende de equipamento elétrico de saúde em casa e famílias de baixa renda. A RMSP é atendida por mais de uma distribuidora, como Enel SP, EDP SP e cooperativas; o mapeamento por município está em [`lista_documentos.md`](lista_documentos.md), seção 4 |
| Problema (uma frase) | Na hora do apagão ou da conta absurda, o cidadão não sabe o que a distribuidora é obrigada a fazer, em quanto tempo e como reclamar. |
| Proposta de valor | Respostas confiáveis, em linguagem simples e com a fonte oficial, sobre direitos e prazos, mais o aviso de manutenções programadas no bairro. Quando a base não sabe, o assistente diz isso e aponta o canal oficial, em vez de inventar |
| Arquitetura: componentes | Ingestão de normas → índice híbrido (denso + BM25) → agente (roteador + ferramentas) → LLM local → validador (schema, citação, recusa) → API `/v1/perguntar`; API de paradas programadas (simulada). Diagrama na seção 3.1 do plano |
| Fontes de dados | Atos oficiais (ANEEL, Presidência, MME/MS) e páginas explicativas oficiais (ANEEL, MME), listados em [`lista_documentos.md`](lista_documentos.md); dados de paradas **simulados**, com geração documentada em `docs/dados_simulados.md` (Fase 6) |
| Modelos de IA | LLM local de 3 a 4B quantizado (Q4_K_M) servido pelo Ollama; candidatos medidos na Fase 0, escolha final na Fase 5. Embeddings bge-m3 e BM25 |
| URL do MVP e repositório | MVP: a definir no projeto integrado. Repositório: https://github.com/pemenezes/GS_IA |
| Indicadores de impacto | Ver a seção 4 |
| ODS conectados | 3, 10, 11 e 9; o 7 entra como complementar, pendente de validação com o professor (seção 3) |

## 2. As seis perguntas da proposta

**1. Quem é o cidadão beneficiado?**
O morador da RMSP que depende da energia para viver com segurança e tem dificuldade de entender a
regulação. Os grupos prioritários são: idosos; pessoas com deficiência; famílias com equipamentos
elétricos de saúde em casa, como concentradores de oxigênio e aparelhos de suporte à vida; e famílias de
baixa renda, que podem ter direito a descontos na conta e muitas vezes não sabem.

**2. Qual problema?**
As regras existem e são públicas, mas estão espalhadas em normas longas e técnicas: a REN 1.000 da ANEEL
sozinha tem centenas de artigos. Na hora do problema (apagão, aparelho queimado, conta alta, corte), o
cidadão não sabe o que a distribuidora deve fazer, em quanto tempo e a quem recorrer. Ferramentas
genéricas de IA podem piorar a situação: respondem com segurança, mas podem inventar prazos ou usar
regras antigas.

**3. Como a solução funciona?**
1. O cidadão pergunta por texto ou, no futuro, por voz.
2. O assistente busca os trechos relevantes nas normas oficiais.
3. Um LLM rodando localmente escreve uma resposta curta, citando literalmente o trecho e a fonte.
4. Um validador confere o formato e se a citação existe. Se a base não sustenta a resposta, o assistente recusa e indica o canal oficial.
5. Para perguntas sobre manutenção programada, um agente consulta a API de paradas e cita o registro.

**4. Quais tecnologias?**
- **IA local:** Python, Ollama (LLM de 3 a 4B quantizado), sentence-transformers (bge-m3), FAISS e BM25.
- **Serviço:** FastAPI e Pydantic (schema e validação), SQLite (API simulada).
- **Qualidade:** pytest e ruff.
- **Por que local:** os dados ficam na máquina, e a solução roda num computador com GPU de 6 GB, sem depender de API paga.

**5. Quem participa do ecossistema?**
- **Fontes oficiais e canais de reclamação:** ANEEL, que regula e é a principal fonte, e as distribuidoras da RMSP.
- **Defesa do consumidor:** Procon e a plataforma consumidor.gov.br.
- **Alcance e validação:** a rede de assistência social (CRAS e Cadastro Único) e associações de pacientes, que poderiam divulgar a ferramenta e validar a linguagem.
- **Distribuidoras, no futuro:** poderiam fornecer dados reais de paradas programadas no lugar dos simulados.

**6. Como o impacto é medido e ampliado?**
- **Hoje, na avaliação da disciplina:** taxa de respostas corretas com fonte, taxa de recusa correta e taxa de alucinação, comparando o LLM sem contexto, o RAG e o agente (seção 4).
- **No produto:** usuários atendidos, perguntas recusadas por tema (que mostram o que falta na base) e encaminhamentos aos canais oficiais.
- **Para ampliar:** trocar os dados simulados pelos dados abertos das distribuidoras, adicionar voz e OCR da conta de luz (já previstos nos campos `origem` e `contexto` da API) e estender a base a outras regiões.

## 3. ODS e contribuição

| ODS | Contribuição concreta | Como medimos |
|---|---|---|
| **3**: Saúde e bem-estar | Famílias com equipamento elétrico de saúde passam a saber dos seus direitos específicos e a receber aviso de parada programada no bairro. Os direitos citados nas fontes são o aviso individual de interrupção programada para quem depende de equipamento indispensável à vida (D14) e a Tarifa Social nesse caso (D02, D04) | Acerto nas perguntas sobre equipamentos de saúde e nas perguntas dinâmicas (API) |
| **10**: Redução das desigualdades | Linguagem simples e tolerância a perguntas por voz reduzem a barreira para idosos, pessoas com deficiência e pessoas com pouca escolaridade. Informação sobre Tarifa Social e Desconto Social chega a quem tem direito | Desempenho por tipo de pergunta: coloquiais e com ruído de voz versus diretas (seção 7.2 do plano) |
| **11**: Cidades e comunidades sustentáveis | Em apagões urbanos e eventos climáticos severos na RMSP, o cidadão sabe o que exigir e como reclamar | Acerto nas perguntas sobre interrupção e emergência |
| **9**: Indústria, inovação e infraestrutura | IA confiável e de baixo custo, rodando localmente, aplicada à transparência de um serviço de infraestrutura essencial | Placar C0 × C1 × C2; latência e VRAM medidas (Fase 0 e Fase 8) |
| **7**: Energia limpa e acessível *(complementar)* | É o ODS mais direto para o tema (acesso a energia a preço justo), mas **não está na lista sugerida pelo professor**. Fica pendente de validação (dúvida 3 da seção 12 do plano) | — |

## 4. Indicadores de impacto

Cada indicador está ligado a uma métrica que a avaliação realmente calcula (seção 7.2 do plano), para o
relatório não prometer o que não mede.

| Indicador | Métrica da avaliação | Meta (plano, seção 7.2) |
|---|---|---|
| Respostas corretas e com fonte | Acurácia da resposta + citação correta | Citação correta ≥ 0,85 |
| Não enganar o cidadão | Taxa de alucinação; recusa correta | Recusa correta ≥ 0,90 |
| Não negar ajuda à toa | Recusa indevida | ≤ 0,10 |
| Atender quem fala por voz ou de forma coloquial | Acurácia por tipo de pergunta | Reportar sem meta fixa |
| Aviso de parada programada | Acerto nas perguntas dinâmicas | Reportar sem meta fixa |
| Responder a tempo | Latência p95 | ≤ 15 s |
| Futuro (produto) | Usuários atendidos, encaminhamentos aos canais oficiais | Fora do escopo desta disciplina |
