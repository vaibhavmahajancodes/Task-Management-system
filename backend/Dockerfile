FROM python:3.12-slim

WORKDIR /app

# System deps needed for psycopg2 and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc libffi-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

# Run DB migrations then start the API server
CMD alembic upgrade head && \
    python app/seed.py && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
