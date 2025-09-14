FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# (Optional) system deps if you need them later
# RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy the v1 backend
COPY v1src/ /app/

# Install deps
RUN pip install --no-cache-dir -r requirements.txt

# Render provides $PORT; default 8000 for local runs
ENV PORT=8000

# Start FastAPI (no env-var indirection)
CMD ["sh","-lc","uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
