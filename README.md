# MVP Dr. Igor - Agente Conversacional

Sistema completo de atendimento conversacional para o **Instituto Aguiar Neri** (Dr. Igor Neri), com backend FastAPI e frontend Next.js.

## 🚀 **Início Rápido**

### **Pré-requisitos**
- Python 3.8+
- Node.js 18+
- OpenAI API Key

### **1. Configuração do Ambiente**

1. **Clone o repositório:**
```bash
git clone <seu-repositorio>
cd Dr.Igor-Export
```

2. **Configure as variáveis de ambiente:**
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite .env e adicione sua OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### **2. Backend (FastAPI)**

```bash
# Instale dependências
pip install -r requirements.txt

# Execute o servidor
cd src
uvicorn dr_igor.app:app --reload --host 0.0.0.0 --port 8000
```

### **3. Frontend (Next.js)**

```bash
# Instale dependências
npm install

# Execute o desenvolvimento
npm run dev
```

### **4. Acesse a Aplicação**

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Documentação API:** http://localhost:8000/docs

## 📋 **Estrutura do Projeto**

```
Dr.Igor-Export/
├── src/dr_igor/           # Backend FastAPI
│   ├── agent/             # Sistema conversacional
│   ├── data/              # Prompts e RAG
│   ├── models/            # Modelos Pydantic
│   ├── routers/           # Endpoints API
│   └── services/          # Integrações externas
├── app/                   # Frontend Next.js
├── components/            # Componentes React
├── porting_base/          # Documentação base
└── requirements.txt       # Dependências Python
```

## ⚙️ **Configuração Avançada**

### **Variáveis de Ambiente**

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `OPENAI_API_KEY` | Chave da OpenAI API | ✅ Sim |
| `OPENAI_MODEL` | Modelo GPT (padrão: gpt-4o-mini) | ❌ Não |
| `API_BASE_URL` | URL do backend (frontend) | ✅ Sim |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Credenciais Google Sheets | ❌ Não |
| `GOOGLE_SHEET_ID` | ID da planilha de agendamentos | ❌ Não |

### **Integrações Opcionais**

- **Google Sheets:** Para agendamentos reais (se não configurado, usa dados mock)
- **Webhook:** Para notificações de dashboard

## 🤖 **Sistema Conversacional**

O agente implementa um fluxo adaptativo baseado em:

1. **Acolhimento** - Mensagem padrão de boas-vindas
2. **Descoberta Inteligente** - Detecção automática de objetivos
3. **Qualificação** - Coleta de dados essenciais
4. **Apresentação de Valor** - Proposta personalizada
5. **Agendamento** - Confirmação obrigatória de horário

### **Fluxos Especializados:**
- 🎯 **Emagrecimento** - Foco em resultados estéticos
- 💪 **Definição Corporal** - Composição corporal
- 🧬 **Reposição Hormonal** - Protocolos seguros

## 📖 **Documentação**

- **Arquitetura Técnica:** `AGENTS.MD`
- **Deploy Railway:** `DEPLOY_RAILWAY.md`
- **Documentação Base:** `porting_base/`

## 🔧 **Desenvolvimento**

### **Backend**
```bash
# Testes
python -m pytest

# Lint
ruff check src/

# Executar com debug
uvicorn dr_igor.app:app --reload --log-level debug
```

### **Frontend**
```bash
# Build de produção
npm run build

# Lint
npm run lint

# Start produção
npm start
```

## 🚀 **Deploy**

### **Railway (Recomendado)**
1. Siga o guia em `DEPLOY_RAILWAY.md`
2. Configure as variáveis de ambiente no Railway
3. Deploy automático via Git

### **Docker**
```bash
# Build da imagem
docker build -t dr-igor-mvp .

# Executar container
docker run -p 8000:8000 --env-file .env dr-igor-mvp
```

## ⚠️ **Importante**

- ✅ Configure sempre a `OPENAI_API_KEY` antes de executar
- ✅ O sistema funciona sem Google Sheets (usa mock de dados)
- ✅ Frontend e backend devem rodar em portas diferentes
- ✅ Agente só transfere para humano após confirmação de horário

## 📞 **Suporte**

Para dúvidas técnicas, consulte:
1. Documentação em `AGENTS.MD`
2. Issues do repositório
3. Logs detalhados do sistema
