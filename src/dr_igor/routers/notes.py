from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..config import get_settings


class ObservacaoPayload(BaseModel):
    session_id: Optional[str] = Field(default=None)
    autor: Optional[str] = Field(default=None)
    texto: str = Field(..., min_length=3, description="Observação ou ajuste identificado")


router = APIRouter()


def _get_notes_path() -> Path:
    settings = get_settings()
    base = Path(settings.notes_dir) if settings.notes_dir else Path("notes")
    base.mkdir(parents=True, exist_ok=True)
    return base / "observacoes.log"


@router.post("/webhook/notes", response_model=dict)
async def save_observacao(payload: ObservacaoPayload) -> dict:
    try:
        notes_path = _get_notes_path()
        timestamp = datetime.utcnow().isoformat()
        line = f"[{timestamp}] session={payload.session_id or '-'} autor={payload.autor or '-'}\n{payload.texto}\n---\n"
        with notes_path.open("a", encoding="utf-8") as fh:
            fh.write(line)
        return {"success": True, "saved_to": str(notes_path)}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

