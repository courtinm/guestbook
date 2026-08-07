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

## CI/CD pipeline

Every push to `main` runs a two-stage GitHub Actions pipeline — no manual build or deploy step:

1. **CI** (`.github/workflows/ci.yaml`) builds the Flask image, tags it with the version in `VERSION.txt` and with `latest`, then pushes both tags to Docker Hub.
2. **CD** (`.github/workflows/cd.yaml`) runs automatically once CI succeeds (or on demand via `workflow_dispatch`). It SSHes into the GCP VM, pulls the latest source and image, and restarts the stack with `docker compose up -d`.

```
main push
   │
   ▼
CI   build → tag (VERSION.txt + latest) → push to Docker Hub
   │
   ▼  (on success, or manual dispatch)
CD   ssh → git pull → docker compose pull → docker compose up -d
```

---

## Design decisions

Short answers to "why", for anyone asking in review:

- **Three Docker networks instead of one.** `front_end`, `back_end`, and `data` isolate blast radius — Postgres and Redis are reachable only from Flask/Adminer, never from Nginx or the host. A single default bridge network would work identically in the happy path, but wouldn't stop a compromised Nginx container from talking to the database directly.
- **Healthchecks + `depends_on: condition: service_healthy` instead of `restart: always` alone.** `restart: always` only recovers a container after it's already crashed; it does nothing to stop Flask from starting before Postgres can accept connections. Ordering by healthcheck avoids that startup race.
- **Redis has no persistent volume.** The visit counter is disposable cache, not source of truth — Postgres is. Losing it on a container recreate is an acceptable trade-off for not managing another volume; if the counter needed to survive restarts, it would live in Postgres instead.
- **Versioning via `VERSION.txt` rather than a commit SHA.** A human-readable version (`1.0.1`) is easier to reason about and maps directly to the Docker Hub tag — at the cost of remembering to bump it before a release. Known limitation: the VM's `docker-compose.yaml` pulls `latest`, not a pinned version, so rollback today means re-tagging on Docker Hub rather than editing one line in Compose — the next thing worth fixing.
- **Adminer bound to `127.0.0.1` only.** It's a debugging convenience, not a feature meant to be internet-facing — loopback-only binding keeps it unreachable even if port 8080 were opened on the firewall by mistake.

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
├── .github/workflows/      # CI (build+push) and CD (deploy) pipelines
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
