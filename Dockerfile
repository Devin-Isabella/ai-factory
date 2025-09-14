﻿FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY v1src/ /app/
RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8000
CMD ["sh","-lc","uvicorn app.main:app --host 0.0.0.0 --port \"]
