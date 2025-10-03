Project Guide: Dr.Igor-Export

Overview

- Monorepo with a Python FastAPI backend and a Next.js 14 (App Router) frontend.
- Frontend calls backend through internal Next API routes that proxy to the FastAPI service using the env var `API_BASE_URL`.
- Conversational logic is modular and agent-oriented: classification, RAG, prompting, compliance/guardrails, scoring, policy, and session state.

Repository Layout

- `src/dr_igor` — Python backend
  - `app.py` FastAPI app, CORS, routes include.
  - `config.py` Env-driven settings (Pydantic Settings). Key vars below.
  - `routers/` API endpoints
    - `chat.py` POST `/webhook/dr-igor` chat endpoint.
    - `agenda.py` POSTs for scheduling: `/webhook/agenda/consultar`, `/agendar`, `/confirmar`.
    - `notes.py` POST `/webhook/notes` append observations to a log file.
  - `models/` Pydantic models for chat and agenda payloads.
  - `services/`
    - `openai.py` Async HTTP client for OpenAI Chat and Whisper.
    - `agenda.py` Agenda integration via Google Sheets (optional) with mock fallback.
  - `store/` Ephemeral session store (in-memory).
  - `agent/` Conversation engine
    - `controller.py` Orchestrates the flow end-to-end.
    - `prompt.py` System/user prompt builders, adaptive guidance, label mapping.
    - `rag.py` Lightweight RAG over `data/base_conhecimento_rag.json`.
    - `scoring.py` Lead scoring and decision rules.
    - `policy.py` Emergency overrides for urgent situations.
    - `intent.py` Keyword heuristics for intent/sentiment/signals.
    - `agents/` helpers
      - `response_agent.py` Calls OpenAI Chat.
      - `intent_agent.py` Regex patterns from YAML to detect objections/intents.
      - `schedule_agent.py` Slot suggestions and prompt append for scheduling.
      - `compliance_agent.py` Guardrails (single question, CTA, hide convênio, split).
  - `data/`
    - `system_prompt_atendimento.md` System prompt and operating rules.
    - `prompt_agente_atendimento.md` Extended scripting (reference).
    - `objections.yaml` Regex patterns for intents/objections.
    - `base_conhecimento_rag.json` Knowledge base used by RAG.

- Frontend (Next.js)
  - `app/` App Router pages and API routes
    - `api/chat/route.ts` Proxies POST to `${API_BASE_URL}/webhook/dr-igor`.
    - `api/notes/route.ts` Proxies POST to `${API_BASE_URL}/webhook/notes`.
    - `page.tsx`, `layout.tsx`, `globals.css` UI shell.
  - `components/` UI components
    - `ChatWidget.tsx` Chat UX with buffered send and decision badges.
    - `NotesPanel.tsx` Observations UI posting to `/api/notes`.
    - `Modal.tsx` Generic modal.
  - Config files: `package.json`, `tailwind.config.ts`, `tsconfig.json`, `next.config.mjs`.

Backend: Key Concepts

- Entry: `FastAPI` app at `src/dr_igor/app.py`. Health: `GET /health`. Debug: `GET /debug`.
- Chat pipeline (simplified):
  1) Session update → heuristics (`intent_agent`, `intent.py`).
  2) Stage computation → adaptive guidance (`prompt.py`).
  3) RAG context retrieval (`rag.py`).
  4) OpenAI chat call (`services/openai.py`). Response must be JSON-parseable, containing fields: `resposta`, `tags`, `dados_coletados`.
  5) Compliance/guardrails (`compliance_agent.py`).
  6) Scoring + decision (`scoring.py`), emergency override (`policy.py`).
  7) Session persists assistant/user messages (`store/session.py`).

- Agenda integration (`services/agenda.py`):
  - Uses Google Sheets if credentials + sheet id are set; otherwise returns mock slots for 2 weeks.
  - Endpoints in `routers/agenda.py` expose consulta/agendar/confirmar.

Backend: Environment Variables

- `OPENAI_API_KEY` (required for chat/transcription)
- `OPENAI_MODEL` (default: `gpt-4o-mini`)
- `OPENAI_WHISPER_MODEL` (default: `whisper-1`)
- `GOOGLE_SERVICE_ACCOUNT_JSON` (optional JSON string)
- `GOOGLE_SHEET_ID` (optional)
- `DASHBOARD_WEBHOOK_URL` (optional)
- `RAG_TOP_K` (default: 3)
- `ALLOW_ORIGIN_REGEX` (default: `.*`), used by CORS
- `NOTES_DIR` (optional; default: `./notes` inside container)

Frontend: Environment Variables

- `API_BASE_URL` (required) — Base URL of the backend (e.g., Railway service URL of FastAPI).
- `NEXT_PUBLIC_*` — Any public flags; example `NEXT_PUBLIC_APP_NAME`.

Endpoints Overview

- Backend (FastAPI)
  - `POST /webhook/dr-igor` — Body: `LeadRequest{ session_id, mensagem, [nome, telefone, cidade, canal] }`
    - Returns: `ChatResponse{ text, parts?, score, breakdown, decisao{acao, prioridade}, dados_coletados, tags, session_id }`
  - `POST /webhook/notes` — Body: `{ texto: string, autor?: string, session_id?: string }` → `{ success, saved_to }`
  - `POST /webhook/agenda/consultar` → `{ slots: AgendaSlot[] }`
  - `POST /webhook/agenda/agendar` → `{ success, agendamento_id }`
  - `POST /webhook/agenda/confirmar` → `{ success }`
  - `GET /health` / `GET /debug`

- Frontend (Next API routes)
  - `POST /api/chat` — Proxies to backend `/webhook/dr-igor` using `API_BASE_URL`.
  - `POST /api/notes` — Proxies to backend `/webhook/notes` using `API_BASE_URL`.

Coding Conventions

- Python: Pydantic v2, FastAPI, async http via httpx. Keep modules small and pure.
- Frontend: Next.js App Router, TypeScript strict. Tailwind for styles.
- Keep guardrails in `compliance_agent.py` and decisioning in `scoring.py` — do not mix with prompting.
- RAG content lives in `data/base_conhecimento_rag.json` and is ranked heuristically in `rag.py`.

Development

- Backend
  - Install: `pip install -r requirements.txt`
  - Run: `uvicorn dr_igor.app:app --host 0.0.0.0 --port 8000 --app-dir src`
  - Env: export variables listed above (or use `.env` with Pydantic Settings).

- Frontend
  - Install: `npm install`
  - Run: `npm run dev`
  - Set `API_BASE_URL` to your running backend (e.g., `http://localhost:8000`).

Extending the System

- Add new RAG content: append to `src/dr_igor/data/base_conhecimento_rag.json` under the relevant sections.
- New guardrails: add to `agent/agents/compliance_agent.py` and wire from `controller.py`.
- Adjust scoring/thresholds: `agent/scoring.py`.
- Intent/objection patterns: `data/objections.yaml` (used by `intent_agent.py`).
- Stages and adaptive guidance: refine `_get_adaptive_guidance` and `_compute_stage`.

Operational Notes

- Sessions are in-memory and ephemeral. After a transfer or confirmed schedule, sessions are marked closed and return a fixed final message.
- CORS: configured in `app.py` to allow `ALLOW_ORIGIN_REGEX` (default allows all origins without credentials).
- Agenda (Google Sheets) is optional; without credentials, the mock slot generator returns 2 weeks of availability.

Deployment

- Backend: Dockerfile provided (`uvicorn dr_igor.app:app`, `PORT` respected). Recommended on Railway.
- Frontend: Recommended on Vercel. This repo includes `vercel.json`. Set `API_BASE_URL` to the backend public URL. The `ignoreCommand` is configured to skip builds unless frontend files change.

Troubleshooting

- 500 on `/webhook/dr-igor`: ensure `OPENAI_API_KEY` is set and model is reachable.
- CORS issues: verify `ALLOW_ORIGIN_REGEX` and that `allow_credentials` is disabled or origins are explicit.
- Empty `parts`: the compliance splitter only activates on long, single-question messages.
