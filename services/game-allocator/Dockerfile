FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org fastapi uvicorn httpx redis

COPY services/game-allocator/main.py allocator_main.py

EXPOSE 8004

CMD ["uvicorn", "allocator_main:app", "--host", "0.0.0.0", "--port", "8004"]
