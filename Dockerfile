FROM python:3.12-slim

WORKDIR /app

COPY requirements-backend.txt .
RUN pip install --no-cache-dir --default-timeout=300 --retries=10 -r requirements-backend.txt

COPY app.py .
COPY preprocessing.py .
COPY air_plane.pkl .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]