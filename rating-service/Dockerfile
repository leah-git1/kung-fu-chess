FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org fastapi uvicorn

COPY shared/   shared/
COPY server/db/ server/db/
COPY server/__init__.py server/__init__.py
COPY rating-service/main.py rating_main.py

VOLUME ["/app/server/db"]

EXPOSE 8002

CMD ["uvicorn", "rating_main:app", "--host", "0.0.0.0", "--port", "8002"]
