from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Dict

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "objections.yaml"


def _normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


class IntentAgent:
    def __init__(self) -> None:
        self.patterns: Dict[str, list[re.Pattern[str]]] = {}

        if not YAML_AVAILABLE:
            # Fallback sem yaml - use padrões básicos hardcoded
            basic_patterns = {
                "preco": ["preço", "valor", "quanto custa", "caro"],
                "convenio": ["convênio", "convenio", "plano", "reembolso"],
                "medicacao": ["ozempic", "mounjaro", "medicação"],
                "agendamento": ["agendar", "marcar", "horário"]
            }
            for key, patterns in basic_patterns.items():
                self.patterns[key] = [re.compile(_normalize(pat)) for pat in patterns]
            return

        try:
            with DATA_PATH.open("r", encoding="utf-8") as fh:
                payload = yaml.safe_load(fh)
        except FileNotFoundError:
            # Arquivo não encontrado - use padrões vazios
            return

        for key, items in payload.items():
            self.patterns[key] = [re.compile(_normalize(pat)) for pat in items]

    def classify(self, message: str) -> Dict[str, bool]:
        msg = _normalize(message)
        return {key: any(p.search(msg) for p in pats) for key, pats in self.patterns.items()}


_agent: IntentAgent | None = None


def get_intent_agent() -> IntentAgent:
    global _agent
    if _agent is None:
        _agent = IntentAgent()
    return _agent

