# ---- Build stage (optional, we keep it simple) ----
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system deps (if you need psycopg etc., uncomment below)
# RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# copy code
COPY v1src/ /app/

# install deps
RUN pip install --no-cache-dir -r requirements.txt

# Render provides \; default to 8000 locally
ENV PORT=8000

# healthcheck (optional—your /health already exists)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python - << 'PY'
import json,sys,urllib.request,os
try:
    url=f"http://127.0.0.1:{os.getenv('PORT','8000')}/health"
    with urllib.request.urlopen(url,timeout=4) as r:
        sys.exit(0 if r.status==200 else 1)
except Exception:
    sys.exit(1)
PY

# Run uvicorn on 0.0.0.0 and \
CMD ["sh","-lc","uvicorn app.main:app --host 0.0.0.0 --port \"]
