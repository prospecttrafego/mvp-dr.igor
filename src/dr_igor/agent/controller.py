from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple
import re

from .agents.intent_agent import get_intent_agent
from .agents.schedule_agent import suggest_slots, build_prompt_append
from .agents.response_agent import generate as generate_response
from .agents.compliance_agent import (
    ensure_cta,
    enforce_single_question,
    hide_convenio_if_not_asked,
    split_parts,
)
from .prompt import build_system_prompt, build_user_prompt
from .intent import detect_intent
from .scoring import compute_score, decide_action
from ..models.chat import LeadRequest, ChatDecision
from ..store.session import session_store


FIELD_PRIORITY = [
    "nome",
    "objetivo",
    "tratamentos_anteriores",
    "cidade",
    # "preferencia_modalidade" não é mais perguntado proativamente
    "telefone",
]

TRACKED_FIELDS = {
    "nome",
    "telefone",
    "cidade",
    "objetivo",
    "tempo_problema",
    "tratamentos_anteriores",
    "preferencia_modalidade",
}

OUTPUT_FIELDS = [
    "nome",
    "telefone",
    "cidade",
    "objetivo",
    "tempo_problema",
    "tratamentos_anteriores",
    "preferencia_modalidade",  # apenas preenchido se usuário disser explicitamente
]


def _normalize_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None


def _first_missing_field(collected: Dict[str, Optional[str]]) -> Optional[str]:
    for field in FIELD_PRIORITY:
        value = collected.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            return field
    return None


async def run(payload: LeadRequest) -> Tuple[str, Dict[str, Any]]:
    # Encerrada?
    sess = session_store.get(payload.session_id)
    if getattr(sess, "closed", False):
        final_text = sess.final_message or "Aguarde mais um instante que logo a Milena entrará em contato com você."
        decisao = ChatDecision(acao="transferir_humano", prioridade="alta")
        return final_text, {
            "parts": None,
            "score": 10,
            "breakdown": {"objetivo": 0, "capacidade": 0, "urgencia": 0, "fit": 0},
            "decisao": decisao,
            "dados": {},
            "tags": {"escalacao_humana": True},
        }

    # Registrar user
    session_store.add(payload.session_id, "user", payload.mensagem)

    collected = sess.collected_data

    for field, value in (
        ("nome", payload.nome),
        ("telefone", payload.telefone),
        ("cidade", payload.cidade),
    ):
        normalized = _normalize_value(value)
        if normalized:
            collected[field] = normalized

    # Heurísticas leves para extrair dados quando o usuário responde fora de ordem
    msg = (payload.mensagem or "").strip()

    def _extract_name(text: str) -> Optional[str]:
        t = text.strip()
        patterns = [
            r"\bmeu nome e\s+([\w\sÁÂÃÉÍÓÔÕÚÇáâãéíóôõúç.'-]{2,})",
            r"\bme chamo\s+([\w\sÁÂÃÉÍÓÔÕÚÇáâãéíóôõúç.'-]{2,})",
            r"^sou\s+([\w\sÁÂÃÉÍÓÔÕÚÇáâãéíóôõúç.'-]{2,})",
        ]
        for p in patterns:
            m = re.search(p, t, flags=re.IGNORECASE)
            if m:
                return m.group(1).strip(" .!")
        # Se for apenas 2-4 palavras com iniciais possivelmente maiúsculas, tratar como nome
        tokens = t.split()
        if 1 < len(tokens) <= 4 and all(len(tok) >= 2 for tok in tokens):
            # Evitar frases comuns como "quero agendar"
            blacklist = {"quero", "agendar", "consulta", "preco", "preço", "valor"}
            if not any(tok.lower() in blacklist for tok in tokens):
                return t.strip(" .!")
        return None

    def _extract_city(text: str) -> Optional[str]:
        m = re.search(r"\bsou de\s+([\w\sÁÂÃÉÍÓÔÕÚÇáâãéíóôõúç.'-]{2,})", text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip(" .!")
        return None

    def _extract_preference(text: str) -> Optional[str]:
        if re.search(r"\bonline\b", text, flags=re.IGNORECASE):
            return "online"
        if re.search(r"\bpresencial\b", text, flags=re.IGNORECASE):
            return "presencial"
        if re.search(r"prefir[oa].*online", text, flags=re.IGNORECASE):
            return "online"
        if re.search(r"prefir[oa].*presencial", text, flags=re.IGNORECASE):
            return "presencial"
        return None

    if not collected.get("nome"):
        nm = _extract_name(msg)
        if nm:
            collected["nome"] = nm
    if not collected.get("cidade"):
        ct = _extract_city(msg)
        if ct:
            collected["cidade"] = ct
    if not collected.get("preferencia_modalidade"):
        pref = _extract_preference(msg)
        if pref:
            collected["preferencia_modalidade"] = pref

    if sess.pending_field and collected.get(sess.pending_field):
        sess.pending_field = None

    if sess.pending_field is None:
        sess.pending_field = _first_missing_field(collected)

    # Classificar sinais por regras
    classifier = get_intent_agent()
    rule_signals = classifier.classify(payload.mensagem)

    # Heurística simples de intenção explícita de agendar
    def _has_schedule_intent(msg: str) -> bool:
        lower = msg.lower()
        keys = ["agendar", "marcar", "agendamento", "marcação", "horário", "horario", "data"]
        return any(k in lower for k in keys)

    # Detectar se usuário escolheu um horário específico
    def _has_schedule_confirmation(msg: str, offered_slots: List[Dict[str, str]]) -> bool:
        if not offered_slots:
            return False
        lower = msg.lower()
        # Procurar por números de data, referências a opções ou confirmações explícitas
        confirmation_keywords = ["primeira", "segunda", "opção 1", "opção 2", "escolho", "quero", "ok", "sim", "confirmo"]
        date_patterns = [r"\d{1,2}/\d{1,2}", r"\d{1,2}h", r"às \d"]

        # Verificar confirmações explícitas
        if any(k in lower for k in confirmation_keywords):
            return True

        # Verificar se menciona elementos dos horários oferecidos
        import re
        for pattern in date_patterns:
            if re.search(pattern, lower):
                return True

        return False

    # Computar etapa do fluxo baseado na documentação base
    def _compute_stage(col: Dict[str, Optional[str]], msg: str) -> str:
        # Se já estamos aguardando confirmação de horário, verificar se confirmou
        if sess.pending_schedule_confirmation:
            if _has_schedule_confirmation(msg, sess.offered_slots or []):
                return "confirmado_horario"
            else:
                return "aguardando_confirmacao_horario"

        # FLUXO ADAPTATIVO baseado na documentação:

        # 1. Se não tem nome, está no acolhimento inicial
        if not col.get("nome"):
            return "acolhimento"

        # 2. DESCOBERTA INTELIGENTE: verificar se objetivo foi mencionado
        intent = detect_intent(msg)
        objetivo_mencionado_agora = intent in ["emagrecimento", "estetica", "medicacao", "reposicao"]
        objetivo_ja_coletado = bool(col.get("objetivo"))

        # Se objetivo foi mencionado agora OU já estava coletado, ir direto para histórico
        if objetivo_mencionado_agora or objetivo_ja_coletado:
            if not col.get("tratamentos_anteriores"):
                return "historico_direto"  # Pula pergunta de objetivo, vai direto pro histórico
        else:
            # Se não mencionou objetivo, perguntar explicitamente
            if not objetivo_ja_coletado:
                return "descoberta_objetivo"

        # 3. Continuar fluxo normal após histórico
        if not col.get("cidade"):
            return "localizacao"

        # 4. Apresentação de valor e agendamento
        # Se o usuário disser que deseja agendar, mas ainda não temos objetivo, pergunte objetivo primeiro.
        if _has_schedule_intent(msg):
            if not col.get("objetivo"):
                return "descoberta_objetivo"
            return "agendamento_preliminar"
        return "apresentacao_valor"

    pre_stage = _compute_stage(collected, payload.mensagem)
    sess.stage = pre_stage

    # Montar prompt do usuário + RAG
    # Contagem de re-perguntas para variar a formulação
    if sess.pending_field:
        sess.reask_counts[sess.pending_field] = sess.reask_counts.get(sess.pending_field, 0)
    prev_pending = sess.pending_field

    user_prompt, _, intent, sentiment = build_user_prompt(
        payload.mensagem,
        session_id=payload.session_id,
        nome=collected.get("nome") or payload.nome,
        telefone=collected.get("telefone") or payload.telefone,
        cidade=collected.get("cidade") or payload.cidade,
        signals_override=rule_signals,
        collected=collected,
        pending_field=sess.pending_field,
        stage=pre_stage,
        reask_count=sess.reask_counts.get(sess.pending_field or "", 0),
    )

    # Agenda: Só anexar 2 slots quando a etapa for de agendamento
    if pre_stage == "agendamento_preliminar":
        slots = suggest_slots(limit=2)
        user_prompt += build_prompt_append(slots)
        # Salvar slots oferecidos na sessão e marcar como aguardando confirmação
        sess.offered_slots = slots
        sess.pending_schedule_confirmation = True

    # Histórico
    system = build_system_prompt()
    history = session_store.get(payload.session_id).messages[:-1]
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": system},
        *({"role": m.role, "content": m.content} for m in history),
        {"role": "user", "content": user_prompt},
    ]

    raw = await generate_response(messages)
    parsed_content = raw.get("parsed_content")
    parsed = json.loads(parsed_content)

    tags = parsed.get("tags", {})
    dados_extraidos = parsed.get("dados_coletados", {})

    for key in TRACKED_FIELDS:
        value = dados_extraidos.get(key)
        if isinstance(value, str):
            normalized = _normalize_value(value)
        else:
            normalized = value
        if normalized:
            sess.collected_data[key] = normalized

    if sess.pending_field and sess.collected_data.get(sess.pending_field):
        sess.pending_field = None

    if sess.pending_field is None:
        sess.pending_field = _first_missing_field(sess.collected_data)

    # Atualizar contagem de re-perguntas
    if sess.pending_field:
        if prev_pending == sess.pending_field:
            sess.reask_counts[sess.pending_field] = sess.reask_counts.get(sess.pending_field, 0) + 1
        else:
            sess.reask_counts[sess.pending_field] = 0

    # Recomputar etapa após extrair novos dados
    post_stage = _compute_stage(sess.collected_data, payload.mensagem)
    sess.stage = post_stage

    dados = {field: sess.collected_data.get(field) for field in OUTPUT_FIELDS}
    # Mesclar sinais de regras nas tags para rastreio
    tags |= {f"sinal_{k}": v for k, v in rule_signals.items()}

    score, breakdown = compute_score(tags, dados)
    decisao_dict = decide_action(score, tags)

    # Sem override de emergência: negócio não contempla esse fluxo
    resposta_texto = parsed.get("resposta") or "Não foi possível gerar uma resposta."

    # Guardrails
    lower_user = payload.mensagem.lower()
    asked_price = any(k in lower_user for k in ["preço", "preco", "valor", "quanto custa", "custa", "investimento"]) or rule_signals.get("preco", False)
    asked_convenio = any(k in lower_user for k in ["convênio", "convenio", "plano", "reembolso"]) or rule_signals.get("convenio", False)

    # Guardrails (sempre aplicados, sem caminho de override)
    resposta_texto = enforce_single_question(resposta_texto)
    # CTA de preço somente quando qualificado e apresentando valor (não quando aguardando confirmação)
    allow_cta = (score >= 6 and post_stage in ["apresentacao_valor"] and not sess.pending_schedule_confirmation)
    resposta_texto = ensure_cta(resposta_texto, asked_price, allow_cta)
    resposta_texto = hide_convenio_if_not_asked(resposta_texto, asked_convenio)

    # Split parts
    resposta_texto, parts = split_parts(resposta_texto)

    # Salvar histórico
    if parts:
        for p in parts:
            session_store.add(payload.session_id, "assistant", p)
    else:
        session_store.add(payload.session_id, "assistant", resposta_texto)

    decisao = ChatDecision(**decisao_dict)

    # REGRA CRÍTICA: Só transferir para humano se horário foi confirmado
    if decisao.acao == "transferir_humano":
        if post_stage == "confirmado_horario":
            # Horário confirmado, pode transferir
            final_msg = "Agradeço! Em instantes nossa equipe (Milena) entrará em contato para confirmar os detalhes."
            session_store.mark_closed(payload.session_id, final_message=final_msg)
        else:
            # Ainda não confirmou horário, manter conversa
            decisao = ChatDecision(acao="continuar_conversa", prioridade="normal")

    # Se confirmou horário mas sistema não detectou transferência, forçar
    elif post_stage == "confirmado_horario":
        decisao = ChatDecision(acao="transferir_humano", prioridade="alta")
        final_msg = "Agradeço! Em instantes nossa equipe (Milena) entrará em contato para confirmar os detalhes."
        session_store.mark_closed(payload.session_id, final_message=final_msg)

    return resposta_texto, {
        "parts": parts,
        "score": score,
        "breakdown": breakdown,
        "decisao": decisao,
        "dados": dados,
        "tags": tags,
    }
