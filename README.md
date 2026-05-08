# The Over-Engineered Guestbook

A modern, containerized **guestbook** application built on Docker, Flask, PostgreSQL, Redis, and Nginx.
This project was built as a practical exercise in Docker orchestration and multi-service architectures. It intentionally over-engineers a simple message board to demonstrate production-grade infrastructure patterns.

```bash
# Copy and fill in your environment variables, then start everything
cp .env.example .env
docker compose up -d
```

---

## Access

| Service | URL | Notes |
|---|---|---|
| Web app | http://localhost | Main guestbook UI |
| REST API | http://localhost/api/messages | JSON endpoint |
| Health check | http://localhost/health | Orchestration readiness |
| Adminer | http://localhost:8080 | Dev only — localhost only |

Credentials are defined in your `.env` file.

---

## Features

- **Visit counter** tracked in Redis
- **Message storage** in PostgreSQL via parameterized queries
- **REST API** — `GET /api/messages`, `POST /api/messages`
- **Health endpoint** at `/health` for container orchestration
- **Data persistence** via named Docker volumes
- **Reverse proxy** via Nginx — single external entry point

---

## Architecture

```
Internet
   │
   ▼
[Nginx :80]            ← only exposed port
   │
   ▼
[Flask API :8000]      ← internal, unreachable from outside
   │
   ├──▶ [PostgreSQL :5432]   ← data network only
   └──▶ [Redis :6379]        ← data network only
```

**Networks:**
- `front_end`: external → Nginx
- `back_end`: Nginx ↔ Flask
- `data`: Flask / Adminer ↔ PostgreSQL / Redis

Services start in dependency order via Docker Compose health checks: PostgreSQL and Redis must pass their health checks before Flask starts, and Flask must be healthy before Nginx accepts traffic.

---

## Security

- No credentials in the repository — secrets via `.env` only
- Redis and PostgreSQL are network-isolated, not exposed to the host
- Nginx is the only externally reachable service
- Adminer bound to `127.0.0.1` — no remote access
- Non-root user (`app_user`) runs the Flask process inside the container
- Parameterized SQL queries throughout

---

## File structure

```
.
├── app.py                  # Flask API
├── Dockerfile              # Flask container build
├── docker-compose.yaml     # Full-stack orchestration
├── nginx.conf              # Reverse proxy config
├── init.sql                # PostgreSQL schema and seed data
├── requirements.txt        # Pinned production dependencies
├── requirements-dev.txt    # Dev/test dependencies
├── templates/              # Jinja2 HTML templates
├── tests/                  # Pytest test suite
├── .env.example            # Environment variable template
└── README.md
```

---

## Running tests

```bash
pip install -r requirements-dev.txt
pytest tests/
```

---

## Useful commands

```bash
# View logs
docker compose logs -f

# Stop all services
docker compose down

# Stop and remove volumes (clears database)
docker compose down -v

# Connect to PostgreSQL
docker exec -it $(docker compose ps -q db) psql -U $POSTGRES_USER -d $POSTGRES_DB
```
