# Decisões da revisão do gabarito (Fase 3)

**Revisor:** Pedro Menezes (RM97432). **Data:** 08/11/2026.

| Casos | Decisão |
|---|---|
| T-001 a T-006, T-008 a T-060 | ✅ Aprovados como estão |
| T-007 | ✏️ Ajustado (ver abaixo) |

## T-007: ressarcimento em situação de emergência

**Dúvida levantada pelo Pedro:** uma fonte não oficial na internet (Editora Brasil Energia) afirma
que a distribuidora pode negar o ressarcimento se comprovar que o dano decorreu de interrupção
associada a situação de emergência ou calamidade pública decretada.

**Verificação no texto oficial da base:**
- Essa redação é a do inciso VIII do art. 621 da REN 1.000/2021. No texto compilado da ANEEL, o
  inciso aparece **tachado**, com a nota "(Revogado pela REN ANEEL 1.137, DE 21.10.2025)".
- O art. 19 da REN 1.137/2025 (`D06-art19`) revoga esse inciso, e o art. 20 (`D06-art20`) revoga
  a alínea b do item 14 do PRODIST Módulo 9, que tinha a mesma hipótese.
- A lista vigente do art. 621 (`D01-art621-p3`) passa do inciso VII para o IX.

**Ajuste aprovado:**
- **Gabarito:** `D06-art19`, `D06-art20` e `D01-art621-p3`.
- **Resposta:** "Não, foi revogado pela REN 1.137/2025".
- **Fatos proibidos:** as duas redações revogadas, a do inciso VIII e a da alínea b.

A fonte da internet estava desatualizada, que é exatamente o comportamento que a armadilha temporal
mede.

## Outras decisões da mesma revisão

- **Paradas programadas (Fase 6):** a API continua simulada, por ser a única forma de manter o
  gabarito congelado e reprodutível. Ela será **calibrada com os dados abertos da ANEEL**
  ("Interrupções de Energia Elétrica nas Redes de Distribuição", licença ODbL), usando as
  interrupções programadas da Enel SP, e ficará atrás de uma interface que permita trocá-la por
  dados reais. O assistente indica a página oficial de manutenção programada da distribuidora
  como canal para o cidadão confirmar com o número da instalação.
- **Congelamento:** autorizado depois do ajuste da T-007.
