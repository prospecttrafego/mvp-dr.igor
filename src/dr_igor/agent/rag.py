from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Tuple

from ..config import get_settings

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "base_conhecimento_rag.json"


def _normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text


class KnowledgeBase:
    def __init__(self) -> None:
        with _DATA_PATH.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        self._payload = payload

    @property
    def payload(self) -> Dict[str, Any]:
        return self._payload

    def _iter_items(self) -> List[Tuple[str, Dict[str, Any]]]:
        items: List[Tuple[str, Dict[str, Any]]] = []
        for key, entries in self._payload.items():
            if isinstance(entries, list):
                for it in entries:
                    items.append((key, it))
        return items

    def search_entries(self, query: str, top_k: int | None = None, intent_hint: str | None = None) -> List[Dict[str, Any]]:
        """Busca melhorada por similaridade simples com pesos heurísticos.

        - Normaliza acentos e caixa
        - Pondera por correspondência de palavras-chave
        - Aumenta peso se categoria/coisas combinam com a intenção detectada
        """
        nq = _normalize(query)
        top_k = top_k or max(6, get_settings().rag_top_k)

        intent_weights: Dict[str, float] = {
            "emagrecimento": 0.5,
            "estetica": 0.4,
            "medicacao": 0.6,
            "reposicao": 0.7,
        }
        iw = intent_weights.get((intent_hint or "").split("_")[0], 0.0)

        def item_text(cat: str, it: Dict[str, Any]) -> str:
            # Concatenar campos comuns
            parts: List[str] = []
            for k in ("titulo", "descricao", "depoimento", "resposta", "nome", "indicacao"):
                v = it.get(k)
                if isinstance(v, str):
                    parts.append(v)
            # tags e estratégias
            tags = it.get("tags") or []
            if isinstance(tags, list):
                parts.extend([str(t) for t in tags])
            for k in ("estrategias", "fases"):
                v = it.get(k)
                if isinstance(v, list):
                    parts.extend([json.dumps(x, ensure_ascii=False) for x in v])
            return _normalize(" \n ".join(parts + [cat]))

        def score(cat: str, it: Dict[str, Any]) -> float:
            txt = item_text(cat, it)
            s = 0.0
            # sobreposição de tokens simples
            for kw in ("emagrec", "definicao", "reposicao", "hormonal", "ozempic", "mounjaro", "online", "preco", "valor", "bioimpedancia"):
                if kw in nq and kw in txt:
                    s += 0.6
            # presença direta do termo
            if nq and nq in txt:
                s += 1.0
            # boost por intenção
            if intent_hint:
                if intent_hint.startswith("medicacao") and ("ozempic" in txt or "glp-1" in txt):
                    s += iw
                if intent_hint.startswith("reposicao") and ("reposicao" in txt or "trt" in txt or "hormonal" in txt):
                    s += iw
                if intent_hint.startswith("emagrec") and ("emagrec" in txt or "perda" in txt):
                    s += iw
                if intent_hint.startswith("estetica") and ("definicao" in txt or "recomposicao" in txt):
                    s += iw
            # fallback por relevância nativa
            s += float(it.get("relevancia_score", 0.0)) * 0.3
            return s

        items = self._iter_items()
        ranked = sorted(
            (
                {
                    "categoria": cat,
                    "item": it,
                    "_score": score(cat, it),
                }
                for cat, it in items
            ),
            key=lambda x: x["_score"],
            reverse=True,
        )
        top = [x for x in ranked if x["_score"] > 0][:top_k]
        return top

    def format_as_bullets(self, ranked_items: List[Dict[str, Any]]) -> str:
        lines: List[str] = []
        for r in ranked_items:
            cat = r.get("categoria")
            it = r.get("item", {})
            titulo = it.get("titulo") or it.get("nome") or it.get("id") or "Conteúdo"
            resumo = it.get("descricao") or it.get("resposta") or ""
            resumo = resumo.strip().replace("\n", " ")
            if len(resumo) > 240:
                resumo = resumo[:237] + "..."
            lines.append(f"- [{cat}] {titulo}: {resumo}")
        return "\n".join(lines[: max(3, get_settings().rag_top_k)])

    # Compatibilidade: mantém método antigo (não usado no prompt)
    def search(self, query: str, top_k: int | None = None) -> Dict[str, List[Dict[str, Any]]]:
        nq = _normalize(query)
        top_k = top_k or get_settings().rag_top_k

        def relevance(item: Dict[str, Any]) -> float:
            score = 0.0
            text = _normalize(json.dumps(item, ensure_ascii=False))
            if nq in text:
                score += 1.0
            keywords = ["emagrec", "definicao", "reposicao", "online", "ozempic", "urgente", "preco", "valor"]
            score += sum(0.2 for kw in keywords if kw in nq and kw in text)
            return score

        result: Dict[str, List[Dict[str, Any]]] = {}
        for key, entries in self._payload.items():
            if not isinstance(entries, list):
                continue
            ranked = sorted(entries, key=relevance, reverse=True)
            result[key] = ranked[:top_k]
        return result


_knowledge_base: KnowledgeBase | None = None


def get_knowledge_base() -> KnowledgeBase:
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base
