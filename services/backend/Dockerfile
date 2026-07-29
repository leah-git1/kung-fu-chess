FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    fastapi uvicorn bcrypt redis

COPY shared/                        shared/
COPY server/db/                     server/db/
COPY server/__init__.py             server/__init__.py
COPY services/backend/              services/backend/

VOLUME ["/app/server/db"]
