FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org fastapi uvicorn httpx redis

COPY api-gateway/main.py api_gateway.py

EXPOSE 8080

CMD ["uvicorn", "api_gateway:app", "--host", "0.0.0.0", "--port", "8080"]
