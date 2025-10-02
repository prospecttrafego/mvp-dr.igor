from pathlib import Path
from typing import Dict, Optional

from .rag import get_knowledge_base
from .intent import detect_intent, detect_sentiment, detect_signals

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

_SYSTEM_PROMPT_PATH = DATA_DIR / "system_prompt_atendimento.md"
_SCRIPT_PROMPT_PATH = DATA_DIR / "prompt_agente_atendimento.md"
FIELD_LABELS = {
    "nome": "nome do lead",
    "objetivo": "objetivo principal",
    "tratamentos_anteriores": "tratamentos anteriores",
    "cidade": "cidade",
    "preferencia_modalidade": "preferência (presencial ou online)",
    "telefone": "telefone",
    "tempo_problema": "tempo do problema relatado",
}

_system_prompt_cache: str | None = None
_script_prompt_cache: str | None = None


def load_system_prompt() -> str:
    global _system_prompt_cache
    if _system_prompt_cache is None:
        _system_prompt_cache = _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    return _system_prompt_cache


def load_script_prompt() -> str:
    global _script_prompt_cache
    if _script_prompt_cache is None:
        _script_prompt_cache = _SCRIPT_PROMPT_PATH.read_text(encoding="utf-8")
    return _script_prompt_cache


# Templates YAML removidos - sistema usa orientações adaptativas dinâmicas


def build_system_prompt() -> str:
    """Load only the system prompt - script prompt is for reference only."""
    return load_system_prompt()


def _get_adaptive_guidance(intent: str, collected: Dict[str, Optional[str]], stage: str | None) -> str:
    """Gera orientações adaptativas baseadas no objetivo detectado e contexto."""
    nome = collected.get("nome", "")
    objetivo = collected.get("objetivo", "")
    tratamentos = collected.get("tratamentos_anteriores", "")
    cidade = collected.get("cidade", "")

    # FLUXO ADAPTATIVO BASEADO NA DOCUMENTAÇÃO BASE

    # Se objetivo já foi mencionado/coletado, usar scripts específicos por etapa
    if objetivo:
        if "emagrecimento" in objetivo.lower() or "peso" in objetivo.lower():
            if stage == "historico_direto":
                return f"EMAGRECIMENTO - HISTÓRICO: 'Perfeito, {nome}! Emagrecimento é nossa especialidade. Se posso perguntar, já buscou algum tratamento para isso anteriormente? Como foi sua experiência?'"
            elif stage == "localizacao":
                return f"EMAGRECIMENTO - LOCALIZAÇÃO: 'Senhor(a) {nome}, para melhor atendê-lo(a) com seu objetivo de emagrecimento, poderia informar de qual cidade está falando conosco?'"
            elif stage == "modalidade":
                if "feira de santana" in cidade.lower():
                    return f"EMAGRECIMENTO - MODALIDADE PRESENCIAL: 'Excelente, {nome}! Como está em Feira de Santana, recomendo fortemente o atendimento presencial. Realizamos bioimpedância que mostra sua composição corporal exata - percentual de gordura, músculo e água. Isso é fundamental para um plano de emagrecimento eficaz.'"
                else:
                    return f"EMAGRECIMENTO - MODALIDADE ONLINE: 'Entendi, {nome}. O Dr. Igor Neri atende online com excelentes resultados em emagrecimento. Fazemos avaliação completa com cálculo detalhado de IMC e anamnese específica para seu biotipo.'"
            elif stage == "apresentacao_valor":
                return f"EMAGRECIMENTO - VALOR: 'Senhor(a) {nome}, o Dr. Igor tem mais de 10 anos de experiência e pós-graduação em Ciências da Obesidade. O investimento é R$ 700 (consulta + bioimpedância + retorno em 30 dias). Baseado em evidência científica, não dietas milagrosas.'"

        elif "definição" in objetivo.lower() or "tonificar" in objetivo.lower():
            if stage == "historico_direto":
                return f"DEFINIÇÃO - HISTÓRICO: 'Excelente escolha, {nome}! Definição corporal requer abordagem muito específica. Já buscou algum tratamento para isso anteriormente? Como foi sua experiência?'"
            elif stage == "localizacao":
                return f"DEFINIÇÃO - LOCALIZAÇÃO: 'Senhor(a) {nome}, para melhor orientá-lo(a) sobre definição corporal, poderia informar de qual cidade está falando conosco?'"
            elif stage == "apresentacao_valor":
                return f"DEFINIÇÃO - VALOR: 'Senhor(a) {nome}, definição corporal vai além da estética - é saúde. O Dr. Igor trabalha com protocolos específicos para composição corporal. Investimento: R$ 700 (consulta + bioimpedância + retorno).'"

        elif "reposição" in objetivo.lower() or "hormonal" in objetivo.lower():
            if stage == "historico_direto":
                return f"REPOSIÇÃO - HISTÓRICO: 'Entendi, {nome}. O Dr. Igor Neri realiza reposição hormonal com total segurança, baseada em exames e acompanhamento próximo. Já realizou algum exame recente (testosterona, TSH, estradiol) ou teve experiência anterior com reposição?'"
            elif stage == "apresentacao_valor":
                return f"REPOSIÇÃO - VALOR: 'Senhor(a) {nome}, reposição hormonal é área de especialização do Dr. Igor. Protocolo completo com exames, avaliação e acompanhamento. Investimento: R$ 700 (consulta + retorno).'"

    # Se ainda não coletou objetivo, verificar se foi mencionado nesta mensagem (PRIMEIRA DETECÇÃO)
    elif intent in ["emagrecimento", "estetica", "medicacao", "reposicao"]:
        if intent == "emagrecimento":
            return f"PRIMEIRA DETECÇÃO - EMAGRECIMENTO: 'Senhor(a) {nome}, entendi que busca emagrecimento. Para orientá-lo da melhor forma, já buscou algum tratamento para isso anteriormente?'"
        elif intent == "estetica":
            return f"PRIMEIRA DETECÇÃO - DEFINIÇÃO: 'Senhor(a) {nome}, entendi que busca definição corporal. Para orientá-lo da melhor forma, já buscou algum tratamento para isso anteriormente?'"
        elif intent == "reposicao":
            return f"PRIMEIRA DETECÇÃO - REPOSIÇÃO: 'Senhor(a) {nome}, entendi que busca reposição hormonal. Para orientá-lo da melhor forma, já realizou exames recentes ou teve experiência anterior com reposição?'"
        elif intent == "medicacao":
            return f"PRIMEIRA DETECÇÃO - MEDICAÇÃO: 'Senhor(a) {nome}, entendi que tem interesse em medicação para emagrecimento. O Dr. Igor prescreve quando indicado, sempre com acompanhamento. Já buscou algum tratamento anteriormente?'"

    # Orientações específicas por etapa sem objetivo definido
    if stage == "acolhimento":
        periodo = "tarde"  # Simplificado para MVP
        return f"ACOLHIMENTO: SEMPRE use a mensagem padrão exata: 'Boa {periodo}, sou Alice, assistente do Instituto Aguiar Neri. É um prazer recebê-lo(a). Como posso ajudá-lo(a) hoje?' - NÃO antecipe informações sobre a clínica."
    elif stage == "descoberta_objetivo":
        return f"DESCOBERTA: 'Senhor(a) {nome}, para que eu possa orientá-lo(a) da melhor forma, poderia me contar qual é seu principal objetivo? Emagrecimento, definição corporal, reposição hormonal?'"
    elif stage == "agendamento_preliminar":
        return f"AGENDAMENTO: Lead qualificado - ofertar 2 opções de horário específicas (formato dd/MM/yyyy às HHh) e aguardar confirmação. NÃO transferir para humano até escolha ser feita."

    return "Siga o fluxo padrão conforme a etapa atual."


def build_user_prompt(
    message: str,
    session_id: str,
    nome: str | None = None,
    telefone: str | None = None,
    cidade: str | None = None,
    signals_override: dict | None = None,
    collected: Dict[str, Optional[str]] | None = None,
    pending_field: str | None = None,
    stage: str | None = None,
) -> tuple[str, str, str, str]:
    intent = detect_intent(message)
    sentiment = detect_sentiment(message)
    signals = signals_override if signals_override is not None else detect_signals(message)
    kb = get_knowledge_base()
    entries = kb.search_entries(message, intent_hint=intent, top_k=6)
    knowledge_text = kb.format_as_bullets(entries) if entries else "- [faq] Sem contexto relevante"

    collected = collected or {}
    collected_lines = [
        f"- {FIELD_LABELS.get(key, key)}: {value}"
        for key, value in collected.items()
        if value
    ]
    collected_block = "\n".join(collected_lines) if collected_lines else "- nenhum dado confirmado"

    if pending_field:
        pending_block = f"- {FIELD_LABELS.get(pending_field, pending_field)}"
    else:
        pending_block = "- nenhum campo prioritário definido"

    # Obter orientação adaptativa baseada no objetivo
    adaptive_guidance = _get_adaptive_guidance(intent, collected, stage)

    user_prompt = f"""
Lead ID: {session_id}
Nome: {nome or 'não informado'}
Telefone: {telefone or 'não informado'}
Cidade: {cidade or 'não informada'}
Intenção detectada: {intent}
Sentimento detectado: {sentiment}
Etapa atual (fluxo): {stage or 'desconhecida'}
Mensagem atual: "{message}"

ORIENTAÇÃO ADAPTATIVA (siga esta instrução específica):
{adaptive_guidance}

Contexto RAG (resumo):
{knowledge_text}

Sinais detectados (heurísticos):
{signals}

Dados já confirmados nesta sessão:
{collected_block}

Campo prioritário (pergunte somente isso agora):
{pending_block}

Regras adicionais:
- Faça no máximo uma pergunta por resposta.
- Se a pergunta prioritária ainda não foi respondida, repergunte somente ela.
- Não antecipe a próxima etapa enquanto a atual estiver sem resposta clara.
- Não ofereça datas/horários até a etapa "agendamento_preliminar".
- Quando perguntarem sobre preço, responda objetivamente, e em seguida retorne ao próximo passo pendente do fluxo (não finalize).
- PRIORIZE a orientação adaptativa acima de tudo.
""".strip()
    return user_prompt, knowledge_text, intent, sentiment
