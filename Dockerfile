FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# copy code into image
COPY v1src/ /app/

# install dependencies (uses v1src/requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Render provides PORT; default to 8000 locally
ENV PORT=8000

# start server; entrypoint must be app.main:app
CMD ["sh","-lc","uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
