from __future__ import annotations

import uuid
from fastapi import APIRouter

from ..models.agenda import (
    AgendaConsultaRequest,
    AgendaConsultarResponse,
    AgendaSlot,
    AgendarRequest,
    AgendarResponse,
    ConfirmarRequest,
    ConfirmarResponse,
)
from ..services.agenda import list_slots, append_agendamento, confirm_agendamento

router = APIRouter()

@router.post("/webhook/agenda/consultar", response_model=AgendaConsultarResponse)
async def consultar_agenda(req: AgendaConsultaRequest) -> AgendaConsultarResponse:
    # Retorna, por padrão, duas semanas de disponibilidade (4 horários/dia)
    slots_raw = list_slots(limit=56)
    slots = [AgendaSlot(**slot) for slot in slots_raw]
    return AgendaConsultarResponse(slots=slots)

@router.post("/webhook/agenda/agendar", response_model=AgendarResponse)
async def agendar(req: AgendarRequest) -> AgendarResponse:
    agendamento_id = req.id or str(uuid.uuid4())
    append_agendamento([
        agendamento_id,
        req.nome,
        req.telefone,
        req.email or "",
        req.data,
        req.horario,
        req.modalidade,
        req.objetivo or "",
    ])
    return AgendarResponse(success=True, agendamento_id=agendamento_id)

@router.post("/webhook/agenda/confirmar", response_model=ConfirmarResponse)
async def confirmar(req: ConfirmarRequest) -> ConfirmarResponse:
    confirm_agendamento(req.agendamento_id)
    return ConfirmarResponse(success=True)
