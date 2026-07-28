FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org fastapi uvicorn redis

COPY rooms-api/main.py rooms_api.py

EXPOSE 8001

CMD ["uvicorn", "rooms_api:app", "--host", "0.0.0.0", "--port", "8001"]
