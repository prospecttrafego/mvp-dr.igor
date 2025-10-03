from __future__ import annotations

from typing import Dict, Tuple

ScoreBreakdown = Dict[str, int]
Decision = Dict[str, str | int]

QUALIFICATION_THRESHOLD = 8
HUMAN_HANDOFF_THRESHOLD = 8
PRE_APPOINTMENT_THRESHOLD = 6
CONTINUE_THRESHOLD = 4


def compute_score(tags: Dict[str, str | bool], dados_coletados: Dict[str, str | None]) -> Tuple[int, ScoreBreakdown]:
    breakdown: ScoreBreakdown = {
        "objetivo": 0,
        "capacidade": 0,
        "urgencia": 0,
        "fit": 0,
    }

    if tags.get("objetivo_claro"):
        breakdown["objetivo"] = 3
    if tags.get("capacidade_financeira") == "positiva":
        breakdown["capacidade"] = 3
    if tags.get("urgencia_expressa"):
        breakdown["urgencia"] = 2
    fit = 0
    if tags.get("busca_medicacao") or tags.get("reposicao_hormonal"):
        fit += 1
    if dados_coletados.get("cidade"):
        fit += 1
    breakdown["fit"] = min(fit, 2)

    total = sum(breakdown.values())
    return total, breakdown


def decide_action(score: int, tags: Dict[str, str | bool]) -> Decision:
    # Regra específica: reposição hormonal com capacidade financeira positiva → transferir para humano
    if tags.get("reposicao_hormonal") and tags.get("capacidade_financeira") == "positiva":
        return {"acao": "transferir_humano", "prioridade": "alta"}
    if score >= HUMAN_HANDOFF_THRESHOLD:
        return {"acao": "transferir_humano", "prioridade": "alta"}
    if score >= PRE_APPOINTMENT_THRESHOLD:
        return {"acao": "agendar_preliminar", "prioridade": "media"}
    if score >= CONTINUE_THRESHOLD:
        return {"acao": "continuar_conversa", "prioridade": "normal"}
    return {"acao": "follow_up", "prioridade": "baixa"}
