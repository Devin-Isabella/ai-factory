# Base
FROM python:3.11-slim

# Keep Python clean & unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app app

# Render sets PORT at runtime. We also set a default for local use.
ENV PORT=8000
EXPOSE 8000

# Use /bin/sh -lc so ${PORT} expands; default to 8000 locally
CMD ["/bin/sh","-lc","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
