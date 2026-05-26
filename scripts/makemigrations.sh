#!/bin/sh
set -e
for svc in auth instance contacts campaigns chatbot webhook; do
  echo "=== migrations: $svc ==="
  docker compose run --rm --no-deps "${svc}-service" python manage.py makemigrations --noinput
  docker compose run --rm --no-deps "${svc}-service" python manage.py migrate --noinput
done
