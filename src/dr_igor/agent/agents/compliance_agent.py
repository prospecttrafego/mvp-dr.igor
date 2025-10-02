from __future__ import annotations

from typing import Tuple


def enforce_single_question(text: str) -> str:
    """Trim response to keep only the first question when multiple appear."""
    if text.count("?") <= 1:
        return text
    idx = text.find("?")
    return text[: idx + 1].strip()


def ensure_cta(text: str, asked_price: bool, allow_cta: bool) -> str:
    if not asked_price or not allow_cta:
        return text
    lower = text.lower()
    if any(w in lower for w in ["agendar", "marcar", "horário", "horario", "data", "escolha uma das opções"]):
        return text
    return text.rstrip() + "\n\nGostaria de verificar uma data para sua consulta?"


def hide_convenio_if_not_asked(text: str, asked_convenio: bool) -> str:
    if asked_convenio:
        return text
    lower = text.lower()
    if "convênio" not in lower and "convenio" not in lower and "plano" not in lower and "reembolso" not in lower:
        return text
    # Remover frases com esses termos de forma simples
    sentences = [s.strip() for s in text.split('.')]
    filtered = [s for s in sentences if s and not any(k in s.lower() for k in ["convênio", "convenio", "plano", "reembolso"])]
    cleaned = '. '.join(filtered)
    return cleaned if cleaned else text


def split_parts(text: str) -> Tuple[str, list[str] | None]:
    """Split only very long responses into two readable chunks."""
    if len(text) < 500 or text.count("?") >= 2:
        return text, None

    # Prefer splitting around sentence boundaries between 220 and 400 chars.
    window_start, window_end = 220, 400
    period_idx = text.rfind(". ", window_start, window_end)
    comma_idx = text.rfind(", ", window_start, window_end)
    idx = max(period_idx, comma_idx)

    if idx == -1:
        return text, None

    a = text[: idx + 1].strip()
    b = text[idx + 1 :].strip()
    if not a or not b:
        return text, None
    return text, [a, b]
