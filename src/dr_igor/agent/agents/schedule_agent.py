from __future__ import annotations

from datetime import datetime
from typing import List, Dict

from ...services.agenda import list_slots


def suggest_slots(limit: int = 2) -> List[Dict[str, str]]:
    try:
        return list_slots(limit=limit)
    except Exception:
        return []


def format_br(date_iso: str, time_hhmm: str) -> str:
    dt = datetime.fromisoformat(date_iso)
    return f"{dt.strftime('%d/%m/%Y')} às {time_hhmm.replace(':00','h')}"


def build_prompt_append(slots: List[Dict[str, str]]) -> str:
    if not slots:
        return ""
    opts = [f"- {format_br(s.get('Data',''), s.get('Horario_Inicio',''))} ({s.get('Modalidade','')})" for s in slots]
    return (
        "\n\nSugestões de horários (escolha uma das opções ou diga se não pode nestas datas):\n"
        + "\n".join(opts)
        + "\n\nCaso o lead não possa nas opções acima, informe que verificará novas datas e que houve um cancelamento recente."
    )

