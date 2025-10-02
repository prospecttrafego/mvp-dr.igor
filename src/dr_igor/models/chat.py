from __future__ import annotations

from typing import Optional, Dict, List

from pydantic import BaseModel, Field


class LeadRequest(BaseModel):
    session_id: str = Field(..., description="Identificador único da sessão")
    mensagem: str = Field(..., min_length=1)
    nome: Optional[str] = None
    telefone: Optional[str] = None
    cidade: Optional[str] = None
    canal: str = "chat"


class ChatTurn(BaseModel):
    role: str
    content: str


class ChatDecision(BaseModel):
    acao: str
    prioridade: str


class ChatResponse(BaseModel):
    text: str
    parts: Optional[List[str]] = None
    score: int
    breakdown: Dict[str, int]
    decisao: ChatDecision
    dados_coletados: Dict[str, Optional[str]]
    tags: Dict[str, str | bool]
    session_id: str
