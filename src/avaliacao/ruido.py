"""Versões "transcritas por voz" das perguntas, de forma determinística.

Imita a saída típica de reconhecimento de fala: sem pontuação nem acentos, tudo minúsculo,
contrações da fala ("pra", "tá") e trocas de grafia por som parecido. Uma palavra curta de ligação
pode sumir, escolhida com semente fixa.
"""

from __future__ import annotations

import random
import re

from unidecode import unidecode

TROCAS = {
    "para": "pra",
    "estava": "tava",
    "esta": "ta",
    "estou": "to",
    "voce": "ce",
    "religar": "religa",
    "religacao": "religasao",
    "manutencao": "manutensao",
    "energia": "enegia",
    "geladeira": "geladera",
    "luz": "lus",
    "desconto": "disconto",
    "empresa": "impresa",
    "concentrador": "concentrado",
    "oxigenio": "oxigenu",
    "atrasada": "atrasado",
    "quanto": "quantu",
    "insulina": "insolina",
    "aposentado": "aposentadu",
    "beneficio": "benefisio",
}
LIGACAO = {"a", "o", "de", "da", "do", "que", "e"}


def ruido_de_voz(texto: str, semente: int) -> str:
    rng = random.Random(semente)
    palavras = re.findall(r"[a-z0-9]+", unidecode(texto.lower()))
    palavras = [TROCAS.get(p, p) for p in palavras]
    candidatas = [i for i, p in enumerate(palavras) if p in LIGACAO]
    if candidatas:
        del palavras[rng.choice(candidatas)]
    return " ".join(palavras)
