FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org fastapi uvicorn bcrypt
COPY shared/   shared/
COPY server/db/ server/db/
COPY server/__init__.py server/__init__.py
COPY auth-service/main.py auth_main.py

VOLUME ["/app/server/db"]

EXPOSE 8000

CMD ["uvicorn", "auth_main:app", "--host", "0.0.0.0", "--port", "8000"]
