#!/bin/bash

if [ "$USE_NGROK" = "true" ]; then
  echo "🔗 Запуск с ngrok"
  ngrok config add-authtoken "$NGROK_AUTHTOKEN"
  uvicorn main:app --host 0.0.0.0 --port 8000 &
  sleep 2
  ngrok http 8000 --log stdout
else
  echo "🚀 Запуск без ngrok"
  uvicorn main:app --host 0.0.0.0 --port 8000
fi
