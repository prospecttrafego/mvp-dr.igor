from __future__ import annotations

from typing import Optional

EMERGENCY_MESSAGE = (
    "Identifiquei sinais de urgência. O Instituto Aguiar Neri não realiza atendimentos de emergência. "
    "Por favor, procure imediatamente o pronto-socorro mais próximo ou ligue para o serviço de emergência local."
)


def emergency_override(sentiment: str, tags: dict) -> Optional[str]:
    if sentiment == "urgente" or tags.get("urgencia_expressa"):
        return EMERGENCY_MESSAGE
    return None
