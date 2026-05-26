FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY packages/bulkping-common /packages/bulkping-common
RUN pip install --no-cache-dir /packages/bulkping-common

COPY services/auth/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/_base /app/services/_base
COPY services/auth /app

ENV PYTHONPATH=/app:/app/services/_base
ENV DJANGO_SETTINGS_MODULE=config.settings

RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8001
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${SERVICE_PORT:-8001} --workers 2"]
