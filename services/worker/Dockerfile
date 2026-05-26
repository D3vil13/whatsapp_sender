FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc && rm -rf /var/lib/apt/lists/*
COPY packages/bulkping-common /packages/bulkping-common
RUN pip install --no-cache-dir /packages/bulkping-common
COPY services/worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/worker /app
ENV PYTHONPATH=/app
CMD ["celery", "-A", "worker.celery_app", "worker", "-l", "info", "-Q", "default,broadcast,chatbot,scheduled"]
