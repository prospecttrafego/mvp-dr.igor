from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from zoneinfo import ZoneInfo

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

from ..config import get_settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def _get_client():
    if not GSPREAD_AVAILABLE:
        return None

    settings = get_settings()
    if not settings.google_service_account_json:
        return None
    info = json.loads(settings.google_service_account_json)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)


def _mock_slots_two_weeks() -> List[Dict[str, str]]:
    """Gera disponibilidade para as próximas 2 semanas no fuso de São Paulo.

    Datas a partir de "hoje" no TZ America/Sao_Paulo; considerando 4 horários/dia
    (09:00, 11:00, 14:00, 16:00) alternando modalidades Presencial/Online.
    """
    tz = ZoneInfo("America/Sao_Paulo")
    today_sp = datetime.now(tz).date()
    days = 14
    hours = ["09:00", "11:00", "14:00", "16:00"]
    slots: List[Dict[str, str]] = []
    for d in range(days):
        date_str = (today_sp + timedelta(days=d)).isoformat()
        for idx, h in enumerate(hours):
            modality = "Presencial" if idx % 2 == 0 else "Online"
            slots.append(
                {
                    "Data": date_str,
                    "Horario_Inicio": h,
                    "Modalidade": modality,
                    "Status": "Disponível",
                }
            )
    return slots


def list_slots(limit: int = 56) -> List[Dict[str, str]]:
    client = _get_client()
    settings = get_settings()
    if client and settings.google_sheet_id:
        sheet = client.open_by_key(settings.google_sheet_id)
        ws = sheet.worksheet("disponibilidade")
        records = ws.get_all_records()
        slots = [r for r in records if str(r.get("Status", "Disponível")).lower() == "disponível"]
        return slots[:limit]
    # fallback mock: duas semanas completas no fuso de São Paulo
    slots = _mock_slots_two_weeks()
    return slots[:limit]


def append_agendamento(row: List[str]) -> None:
    client = _get_client()
    settings = get_settings()
    if client and settings.google_sheet_id:
        sheet = client.open_by_key(settings.google_sheet_id)
        ws = sheet.worksheet("agendamentos")
        ws.append_row(row, value_input_option="USER_ENTERED")


def confirm_agendamento(agendamento_id: str) -> None:
    client = _get_client()
    settings = get_settings()
    if client and settings.google_sheet_id:
        sheet = client.open_by_key(settings.google_sheet_id)
        ws = sheet.worksheet("agendamentos")
        values = ws.get_all_records()
        for idx, row in enumerate(values, start=2):
            if str(row.get("ID")) == agendamento_id:
                ws.update_cell(idx, 12, "CONFIRMADO")
                ws.update_cell(idx, 13, True)
                return
