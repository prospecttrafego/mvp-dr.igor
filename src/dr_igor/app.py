from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import chat, agenda, notes
from .services.openai import shutdown_openai_client

settings = get_settings()

app = FastAPI(title="Dr Igor Conversational Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"]
    ,
    allow_headers=["*"],
)

app.include_router(chat.router, tags=["chat"])
app.include_router(agenda.router, tags=["agenda"])
app.include_router(notes.router, tags=["notes"])

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

@app.get("/debug")
async def debug_info() -> dict:
    """Endpoint para debug - verificar configurações (remover em produção)"""
    import os
    from datetime import datetime
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "environment": {
            "openai_key_configured": bool(os.getenv("OPENAI_API_KEY")),
            "openai_key_prefix": os.getenv("OPENAI_API_KEY", "")[:8] + "..." if os.getenv("OPENAI_API_KEY") else None,
            "openai_model": os.getenv("OPENAI_MODEL", "not-set"),
            "cors_regex": os.getenv("ALLOW_ORIGIN_REGEX", "not-set"),
            "port": os.getenv("PORT", "8000"),
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
        },
        "app_info": {
            "name": "dr-igor-backend",
            "version": "1.0.0",
            "endpoints": ["/health", "/debug", "/webhook/dr-igor", "/webhook/notes"],
            "cors_enabled": True
        }
    }

@app.on_event("shutdown")
async def shutdown_event() -> None:
    await shutdown_openai_client()
