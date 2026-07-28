FROM python:3.11-slim

WORKDIR /app

# Install only server-side deps (no opencv/numpy needed in the container)
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org websockets bcrypt

COPY shared/ shared/
COPY logic/  logic/
COPY server/ server/

# users.db lives inside server/db/ — mount a volume there to persist it
VOLUME ["/app/server/db"]

EXPOSE 5555

CMD ["python", "-m", "server.main"]
