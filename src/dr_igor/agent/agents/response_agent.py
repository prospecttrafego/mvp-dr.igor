from __future__ import annotations

from typing import Any, Dict, List

from ...services.openai import get_openai_client


async def generate(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    client = get_openai_client()
    return await client.chat(messages)

