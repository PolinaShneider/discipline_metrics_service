FROM python:3.10-bullseye

WORKDIR /app
COPY . /app

ENV PIP_NO_CACHE_DIR=off
ENV PIP_CACHE_DIR=/root/.pip-cache
ENV PYTHONPATH=/app

# Установка системных пакетов и ngrok
RUN apt-get update && apt-get install -y git curl unzip && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip

# Установка torch без CUDA
RUN pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu

# Основные зависимости
RUN pip install -r requirements.txt && rm -rf ~/.cache/pip

# Установка ngrok (для локальной разработки)
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list \
    && apt-get update && apt-get install -y ngrok

# entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
