from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import DefaultDict, Dict, List, Optional

@dataclass
class Message:
    role: str
    content: str

@dataclass
class Session:
    messages: List[Message] = field(default_factory=list)
    closed: bool = False
    final_message: Optional[str] = None
    pending_field: Optional[str] = None
    collected_data: Dict[str, Optional[str]] = field(default_factory=dict)
    stage: Optional[str] = None
    pending_schedule_confirmation: bool = False
    offered_slots: Optional[List[Dict[str, str]]] = field(default_factory=list)

class SessionStore:
    def __init__(self) -> None:
        self._sessions: DefaultDict[str, Session] = defaultdict(Session)

    def add(self, session_id: str, role: str, content: str) -> None:
        self._sessions[session_id].messages.append(Message(role=role, content=content))

    def get(self, session_id: str) -> Session:
        return self._sessions[session_id]

    def reset(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def mark_closed(self, session_id: str, final_message: Optional[str] = None) -> None:
        sess = self._sessions[session_id]
        sess.closed = True
        if final_message:
            sess.final_message = final_message

    def export(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            key: [msg.__dict__ for msg in session.messages]
            for key, session in self._sessions.items()
        }

session_store = SessionStore()
