from __future__ import annotations

import asyncio
from typing import Any, Dict

import httpx

from ..config import get_settings

HEADERS_TEMPLATE = {"Content-Type": "application/json"}
CHAT_URL = "https://api.openai.com/v1/chat/completions"
WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"


class OpenAIClient:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = httpx.AsyncClient(timeout=30.0)

    async def chat(self, messages: list[dict[str, Any]], response_format: str = "json_object", temperature: float = 0.3) -> Dict[str, Any]:
        if not self._settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY não configurada no servidor")
        payload = {
            "model": self._settings.openai_model,
            "messages": messages,
            "response_format": {"type": response_format},
            "temperature": temperature,
        }
        headers = {
            **HEADERS_TEMPLATE,
            "Authorization": f"Bearer {self._settings.openai_api_key}",
        }
        resp = await self._client.post(CHAT_URL, json=payload, headers=headers)
        resp.raise_for_status()
        body = resp.json()
        content = body["choices"][0]["message"]["content"]
        return body | {"parsed_content": content}

    async def transcribe(self, audio_bytes: bytes, file_name: str = "audio.ogg") -> Dict[str, Any]:
        if not self._settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY não configurada no servidor")
        headers = {"Authorization": f"Bearer {self._settings.openai_api_key}"}
        files = {
            "file": (file_name, audio_bytes, "application/octet-stream"),
            "model": (None, self._settings.openai_whisper_model),
            "response_format": (None, "json"),
        }
        resp = await self._client.post(WHISPER_URL, files=files, headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def aclose(self) -> None:
        await self._client.aclose()

_openai_client: OpenAIClient | None = None


def get_openai_client() -> OpenAIClient:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client

async def shutdown_openai_client() -> None:
    global _openai_client
    if _openai_client:
        await _openai_client.aclose()
        _openai_client = None
