from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional


class AgendaConsultaRequest(BaseModel):
    modalidade: Optional[str] = Field(default=None, description="Presencial ou Online")
    urgencia: Optional[bool] = False


class AgendaSlot(BaseModel):
    Data: str
    Horario_Inicio: str
    Modalidade: str
    Status: str


class AgendaConsultarResponse(BaseModel):
    slots: List[AgendaSlot]


class AgendarRequest(BaseModel):
    id: str = Field(..., description="ID único do lead")
    nome: str
    telefone: str
    email: Optional[str] = None
    data: str
    horario: str
    modalidade: str
    objetivo: Optional[str] = None


class AgendarResponse(BaseModel):
    success: bool
    agendamento_id: str


class ConfirmarRequest(BaseModel):
    agendamento_id: str


class ConfirmarResponse(BaseModel):
    success: bool
