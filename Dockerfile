FROM python:3.10-bullseye

WORKDIR /app
COPY . /app

ENV PIP_NO_CACHE_DIR=off
ENV PIP_CACHE_DIR=/root/.pip-cache
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install torch==2.2.2
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
