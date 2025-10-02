from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models.chat import LeadRequest, ChatResponse
from ..agent.controller import run as run_controller

router = APIRouter()


@router.post("/webhook/dr-igor", response_model=ChatResponse)
async def chat_endpoint(payload: LeadRequest) -> ChatResponse:
    try:
        text, meta = await run_controller(payload)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(
        text=text,
        parts=meta.get("parts"),
        score=meta.get("score", 0),
        breakdown=meta.get("breakdown", {}),
        decisao=meta.get("decisao"),
        dados_coletados=meta.get("dados", {}),
        tags=meta.get("tags", {}),
        session_id=payload.session_id,
    )
