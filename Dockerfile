FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app app

# Render sets PORT; default 8000 for local
ENV PORT=8000
EXPOSE 8000

# Use shell-form so ${PORT} expands at runtime
CMD ["/bin/sh","-lc","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
