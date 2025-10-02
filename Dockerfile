FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependências do sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas arquivos de dependências primeiro (para melhor cache)
COPY requirements.txt ./

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar apenas o código fonte necessário (backend)
COPY src/ ./src/

EXPOSE 8000

# Comando otimizado para executar a aplicação
CMD ["sh","-c","uvicorn dr_igor.app:app --host 0.0.0.0 --port ${PORT:-8000} --app-dir src"]

