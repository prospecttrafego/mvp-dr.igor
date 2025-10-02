from __future__ import annotations

from typing import Dict
import unicodedata

INTENT_KEYWORDS: Dict[str, tuple[str, ...]] = {
    "emagrecimento": (
        "emagrecer",
        "perder peso",
        "peso",
        "gordura",
        "barriga",
    ),
    "estetica": (
        "definição",
        "definir",
        "tonificar",
        "shape",
        "estética",
    ),
    "preco": (
        "preço",
        "valor",
        "quanto custa",
        "investimento",
        "parcel",
    ),
    "medicacao": (
        "ozempic",
        "mounjaro",
        "medicação",
        "remédio",
        "saxenda",
    ),
    "reposicao": (
        "reposição",
        "testosterona",
        "trt",
        "hormônio",
    ),
    "urgencia": (
        "urgente",
        "dor",
        "socorro",
        "emergência",
        "hospital",
    ),
}

SENTIMENT_KEYWORDS = {
    "positivo": ("feliz", "animado", "esperança", "motivado", "quero", "preciso"),
    "negativo": ("triste", "frustrado", "desanimado", "cansado", "difícil", "não consigo"),
    "urgente": ("urgente", "dor", "agora", "imediato", "socorro"),
}

OBJECTION_SIGNALS = {
    "preco": ("preço", "valor", "quanto custa", "caro", "investimento"),
    "convenio": ("convênio", "convenio", "plano", "plano de saúde", "reembolso"),
    "tempo": ("sem tempo", "agenda cheia", "agora não", "correria", "apertado"),
    "distancia": ("distância", "longe", "moro em", "outra cidade", "deslocamento"),
}


def _normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def detect_intent(message: str) -> str:
    lowered = _normalize(message)
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return intent
    return "geral"


def detect_sentiment(message: str) -> str:
    lowered = _normalize(message)
    for sentiment, keywords in SENTIMENT_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return "urgente" if sentiment == "urgente" else sentiment
    return "neutro"


def detect_signals(message: str) -> Dict[str, bool]:
    lowered = _normalize(message)
    return {key: any(kw in lowered for kw in kws) for key, kws in OBJECTION_SIGNALS.items()}
