# Build recipe for Fly.io only — NOT a local runtime dependency (local is bare uvicorn).
# Build context is demo/ (the parent) so the image includes frontend/ + backend/.
FROM python:3.12-slim

RUN pip install --no-cache-dir uv
WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock* ./backend/
RUN cd backend && uv sync --no-dev

COPY backend/ ./backend/
COPY frontend/ ./frontend/

WORKDIR /app/backend
ENV SEED_ON_STARTUP=1
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
