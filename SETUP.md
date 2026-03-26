# Aetherion — How to Run

> Living document. Update this as the stack evolves.

---

## Prerequisites

| Tool | Version | Why |
|------|---------|-----|
| **Python** | 3.11+ | Backend runtime |
| **Docker + Docker Compose** | Latest | PostgreSQL (pgvector) + Redis |
| **Node.js** | 20+ (via nvm) | Frontend |
| **Git** | Any | Version control |

### Installing prerequisites (Ubuntu / WSL)

```bash
# Python
sudo apt update
sudo apt install python3 python3-venv python3-pip

# Node.js (via nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 20

# Docker — if not installed, follow:
# https://docs.docker.com/engine/install/ubuntu/
# Make sure Docker Desktop (Windows) has WSL integration enabled
```

---

## 1. Clone the repo

```bash
git clone <repo-url> ~/projects/Aetherion
cd ~/projects/Aetherion
```

---

## 2. Set up environment variables

```bash
# Root env (used by docker-compose)
cp .env.example .env

# Backend env (used by the FastAPI app)
cp backend/.env.example backend/.env
```

Open both `.env` files and fill in your keys:

| Variable | Where to get it |
|----------|----------------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/) (for embeddings) |
| `WORKOS_API_KEY` / `WORKOS_CLIENT_ID` | [dashboard.workos.com](https://dashboard.workos.com/) — skip until auth is wired up |
| `ENCRYPTION_KEY` | Generate locally (see below) |
| `JWT_SECRET_KEY` | Generate locally (see below) |

### Generate secrets

```bash
# Fernet encryption key (for PII encryption at rest)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# JWT secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Paste the outputs into `backend/.env`.

---

## 3. Start infrastructure

```bash
docker compose up -d
```

This starts:
- **PostgreSQL 16** with pgvector extension (`localhost:5432`)
- **Redis 7** (`localhost:6379`)

Verify they're running:

```bash
docker compose ps
```

---

## 4. Set up the backend

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head
```

---

## 5. Start the dev server

```bash
# Make sure you're in backend/ with the venv activated
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

The API is now running at **http://localhost:8000**.

- API docs (Swagger): **http://localhost:8000/docs**
- Health check: **http://localhost:8000/api/v1/health**

---

## 6. Seed the database

```bash
# In backend/ with venv activated
python scripts/seed.py
```

This populates the dev database with SPP as the example organization, two users (advisor + admin), sample clients, cases, knowledge items, and audit entries.

---

## 7. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:3000**.

The frontend needs environment variables for the dev auth bypass. These should already exist in `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_DEV_USER_ID=<user-id-from-seed>
NEXT_PUBLIC_DEV_ORG_ID=<org-id-from-seed>
```

If the file doesn't exist, run the seed script first — it prints the IDs you need.

---

## Common Commands

```bash
# --- Infrastructure ---
docker compose up db -d       # Start PostgreSQL (pgvector)
docker compose down           # Stop everything
docker compose logs -f db     # Watch database logs

# --- Backend ---
cd backend
source .venv/bin/activate     # Activate virtualenv (every new terminal)
uvicorn app.main:app --reload # Start dev server
python scripts/seed.py        # Seed/reset dev data

# --- Frontend ---
cd frontend
npm run dev                   # Start Next.js dev server
npm run build                 # Production build (check for errors)

# --- Database ---
alembic upgrade head          # Run all migrations
alembic downgrade -1          # Rollback last migration
alembic revision --autogenerate -m "description"  # Create new migration

# --- Testing ---
pytest                        # Run all tests
pytest -v                     # Verbose output
pytest --cov=app              # With coverage report
```

---

## Project Structure

```
Aetherion/
├── .env.example                  # Root env template (docker-compose vars)
├── docker-compose.yml            # PostgreSQL (pgvector) + Redis
├── CLAUDE.md                     # AI assistant project context
├── Aetherion.md                  # Product vision and strategy
├── SETUP.md                      # This file
│
├── docs/
│   ├── ARCHITECTURE_DECISIONS.md # ADRs for all major decisions
│   ├── DOMAIN_MODEL.md           # All data entities and relationships
│   ├── RAG_PIPELINE.md           # Memory module pipeline spec
│   └── COMPLIANCE_SPEC.md        # Recommendation pack + audit trail spec
│
├── backend/
│   ├── .env.example              # Backend env template
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini               # Migration config
│   ├── alembic/
│   │   └── versions/             # Migration files
│   ├── scripts/
│   │   ├── seed.py               # Dev data seeder
│   │   └── test_pipeline.py      # End-to-end integration test
│   └── app/
│       ├── main.py               # FastAPI entry point
│       ├── config.py             # Pydantic settings
│       ├── database.py           # Async SQLAlchemy engine + session
│       ├── api/
│       │   ├── deps.py           # Auth + DB dependencies (dev bypass)
│       │   └── v1/endpoints/     # Route handlers
│       ├── models/               # SQLAlchemy models
│       ├── schemas/              # Pydantic request/response schemas
│       ├── services/
│       │   ├── reasoner.py       # LLM reasoning + meeting briefs + doc extraction
│       │   ├── control.py        # Compliance checks + document generation
│       │   ├── memory.py         # RAG / semantic search
│       │   └── flow.py           # Workflow orchestration
│       ├── prompts/              # Jinja2 LLM prompt templates
│       └── utils/
│           └── encryption.py     # PII encryption (Fernet)
│
├── frontend/                     # Next.js 14 app
│   ├── app/(dashboard)/          # Dashboard pages (cases, clients, knowledge)
│   ├── components/               # UI components + feature components
│   └── lib/
│       ├── api.ts                # API client with dev auth
│       ├── hooks.ts              # React Query hooks for all endpoints
│       └── labels.ts             # UI labels, status colors, category styles
│
└── v0-reference/                 # v0.dev visual prototype (reference only, delete after redesign)
```

---

## Troubleshooting

### `alembic upgrade head` fails with connection refused

Make sure PostgreSQL is running:

```bash
docker compose up -d db
docker compose ps    # Should show db as "healthy"
```

### `ENCRYPTION_KEY is not set` error at startup

Generate and add a Fernet key to `backend/.env`:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Port 5432 already in use

Another PostgreSQL instance may be running locally. Either stop it or change the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "5433:5432"  # Use 5433 on host
```

Then update `DATABASE_URL` in `backend/.env` to use port `5433`.

### WeasyPrint errors on Linux

WeasyPrint needs system libraries for PDF generation:

```bash
sudo apt install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

---

## What to Build Next

See `TODO.md` for the full task list. Current priorities:

1. Visual redesign (apply v0 reference to existing frontend)
2. Compliance documentation polish
3. Knowledge Q&A (conversational)
4. Auth & security (WorkOS, rate limiting)
