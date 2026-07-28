FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org fastapi uvicorn redis

COPY matchmaker-service/main.py matchmaker_main.py

EXPOSE 8003

CMD ["uvicorn", "matchmaker_main:app", "--host", "0.0.0.0", "--port", "8003"]
