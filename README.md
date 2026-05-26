# BulkPing

Multi-tenant WhatsApp BSP wrapping [Evolution API v2.3.7](https://github.com/EvolutionAPI/evolution-api). Built per **BulkPing Technical PRD v1.2**.

## Architecture (microservices)

| Service | Port | Responsibility |
|---------|------|----------------|
| **gateway** (nginx) | 8000 | API routing |
| **auth-service** | 8001 | Users, JWT, disclaimer |
| **instance-service** | 8002 | WA instances, daily caps, warm-up |
| **contacts-service** | 8003 | Contacts, groups, CSV import |
| **campaigns-service** | 8004 | Campaigns, message logs, stats |
| **chatbot-service** | 8005 | Keyword rules, match logging |
| **webhook-service** | 8006 | Evolution webhook ingestion |
| **celery-worker** | — | Throttled sends, scheduled jobs |
| **celery-beat** | — | Midnight IST resets, health checks |
| **streamlit-ui** | 8501 | Testing-phase dashboard |
| **evolution-api** | 8080 | WhatsApp bridge (Docker) |

Each service owns a **PostgreSQL schema** (`auth`, `instance`, `contacts`, `campaigns`, `chatbot`). Cross-service calls use internal HTTP + `X-Internal-Token`.

Shared library: `packages/bulkping-common` (JWT, Evolution client, HTTP helpers).

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

- API gateway: http://localhost:8000  
- Streamlit UI: http://localhost:8501  
- Health: http://localhost:8000/health  

### First-time migrations

After containers are up:

```bash
docker compose run --rm auth-service python manage.py makemigrations
docker compose run --rm auth-service python manage.py migrate
# Repeat for: instance-service, contacts-service, campaigns-service, chatbot-service
```

Or use `scripts/makemigrations.sh` on Linux/macOS.

## API (via gateway)

All routes prefixed `/api/` except webhooks. JWT required except auth.

- `POST /api/auth/signup/` — `{ email, password, disclaimer_accepted: true }`
- `POST /api/auth/login/`
- `POST /api/auth/token/refresh/`
- `POST /api/instance/create/` — returns QR base64
- `GET /api/instance/status/`
- `DELETE /api/instance/disconnect/`
- `POST /api/contacts/import/` — multipart CSV
- `POST /api/contacts/`, `DELETE /api/contacts/{id}/`
- `GET|POST /api/groups/`, group members endpoints
- `GET|POST /api/campaigns/`, stats, CSV export
- `GET|POST|PATCH|DELETE /api/chatbot/rules/`
- `POST /webhooks/evolution/` — `X-Webhook-Secret` header

## Anti-ban (PRD §4)

- Random **3–8s** Celery countdown between broadcast messages
- **Daily cap** with warm-up: 50 → 100 → 200 (days 1–7, 8–14, 15+)
- Celery Beat: midnight IST reset, 5-min connection health check
- Broadcast hours **warning** (08:00–21:00 IST) on campaign create

## Data policy

Delivery **metadata only** — no message content stored (MessageLog, ChatbotMatchLog).

## Disclaimer

Users must accept the Meta ToS / Baileys disclaimer at signup (`disclaimer_accepted`). All protected endpoints return **403** until accepted.

## Production notes

- Do not expose Postgres, Redis, or Evolution API publicly (nginx only on 80/443).
- Set strong `SECRET_KEY`, `INTERNAL_SERVICE_TOKEN`, `WEBHOOK_SECRET`.
- Beta: Evolution `STORE_TYPE=redis` for session persistence.

## Project layout

```
├── apps/streamlit-ui/     # Testing UI
├── gateway/               # nginx config
├── infra/postgres/        # Schema init
├── packages/bulkping-common/
└── services/
    ├── auth/
    ├── instance/
    ├── contacts/
    ├── campaigns/
    ├── chatbot/
    ├── webhook/
    └── worker/
```
