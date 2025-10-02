# Deploy no Railway (Passo a Passo Simples)

Este guia explica como publicar o BACK-END (FastAPI) no Railway e conectar o FRONT (Vercel).

Requisitos:
- Conta no Railway (https://railway.app) e no GitHub
- Repositório no GitHub com este projeto

## 1) Criar o serviço no Railway

1. Acesse o painel do Railway e clique em "New Project".
2. Escolha "Deploy from GitHub repo" e conecte sua conta do GitHub.
3. Selecione o repositório deste projeto (Dr.Igor-Export).
4. O Railway vai iniciar o build automaticamente.

## 2) Configurar variáveis de ambiente

No projeto do Railway, vá em "Variables" e adicione:

- `OPENAI_API_KEY` → sua chave da OpenAI (obrigatória)
- `OPENAI_MODEL` → `gpt-4.1` (opcional; já é o padrão)
- `ALLOW_ORIGIN_REGEX` → por enquanto `.*` (depois troque para o domínio do Vercel)
- `NOTES_DIR` → `/app/notes` (opcional; para persistir observações em um volume)

## 3) Comando de start

1. Vá em "Settings" → "Deployments" → encontre a seção de "Start Command".
2. Defina:

```
uvicorn dr_igor.app:app --host 0.0.0.0 --port ${PORT} --app-dir src
```

3. Confirme as alterações. O Railway usará a porta fornecida automaticamente na variável `PORT`.

## 4) (Opcional) Persistir observações em arquivo

Se quiser guardar as observações (enviadas pelo front) mesmo após reiniciar o serviço, crie um volume e monte em `/app/notes`:

1. No projeto do Railway, vá em "Storage" → "Add Volume".
2. Dê um nome (ex.: `notes-vol`) e confirme.
3. Em "Variables", deixe `NOTES_DIR` como `/app/notes`.
4. Em "Settings" do serviço, monte o volume no caminho `/app/notes`.

Pronto. O backend vai gravar em `/app/notes/observacoes.log`.

## 5) Expor a URL pública do backend

1. Após o deploy, abra o serviço → verá uma URL pública (ex.: `https://dr-igor-production.up.railway.app`).
2. Teste saúde da API:
   - Abra no navegador: `https://SEU_DOMINIO/health` → deve aparecer `{"status":"ok"}`.

## 6) Conectar o Front (Vercel) ao Backend (Railway)

1. No Vercel, crie um projeto conectando o mesmo repositório (ou somente a pasta do front).
2. Em "Settings" → "Environment Variables", adicione:
   - `API_BASE_URL` = `https://SEU_DOMINIO_RAILWAY` (ex.: `https://dr-igor-production.up.railway.app`)
3. Faça o deploy no Vercel.

Após o deploy, o front chamará o backend via rotas proxy:
- `/api/chat` → encaminha para `${API_BASE_URL}/webhook/dr-igor`
- `/api/notes` → encaminha para `${API_BASE_URL}/webhook/notes`

## 7) Ajustar CORS (recomendado para produção)

No Railway, em `ALLOW_ORIGIN_REGEX`, defina para o domínio do Vercel, por exemplo:

```
^https://seu-app.vercel.app$
```

Assim, somente seu front poderá acessar o backend do navegador.

## 8) Testes rápidos

Backend (Railway):
- `GET /health` → status ok
- `POST /webhook/dr-igor` com JSON `{ "session_id":"t1", "mensagem":"Quero emagrecer" }` → retorna resposta da IA
- `POST /webhook/agenda/consultar` → retorna 2 semanas de slots
- `POST /webhook/notes` com `{ "texto": "Exemplo de observação" }` → grava no arquivo

Frontend (Vercel):
- Abra a URL do Vercel
- Clique em "Abrir Chat" e envie mensagens
- Clique em "Abrir Observações/Ajustes" e salve uma observação

## 9) Dúvidas comuns

- Erro 500 ao chamar a IA → verifique `OPENAI_API_KEY` no Railway.
- Front não fala com o back → verifique `API_BASE_URL` no Vercel.
- CORS bloqueando → ajuste `ALLOW_ORIGIN_REGEX` no Railway para o domínio do Vercel.
- Notas não aparecem no arquivo → crie o volume e defina `NOTES_DIR=/app/notes`.