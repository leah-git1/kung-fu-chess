FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org websockets redis httpx bcrypt

COPY shared/  shared/
COPY logic/   logic/
COPY server/  server/
COPY services/game-shard/main.py shard_main.py

EXPOSE 5556

CMD ["python", "shard_main.py"]
