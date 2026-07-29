FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org websockets httpx redis

COPY shared/              shared/
COPY logic/               logic/
COPY server/session/      server/session/
COPY server/logging/      server/logging/
COPY server/__init__.py   server/__init__.py
COPY services/ws-gateway/main.py   ws_gateway.py

EXPOSE 5555

CMD ["python", "ws_gateway.py"]
