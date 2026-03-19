# Aetherion

**The AI operating system for retirement and pension decisions.**

Aetherion helps pension providers, retirement advisors, and life insurers turn complex retirement cases into explainable recommendations, compliant documentation, and executable workflows.

---

## What it does

An advisor opens the Workbench, selects a client case, clicks **Generate Recommendation**, and within seconds gets a structured, evidence-backed pension recommendation with:

- Step-by-step reasoning chain with cited evidence
- Suitability score against client risk profile
- Scenario comparisons with projected outcomes
- Cost and conflict-of-interest disclosures (IDD-compliant)
- Downloadable recommendation pack (Word/PDF) in Swedish

All outputs are auditable, versioned, and compliance-ready.

---

## Architecture

Five modules, one monolith:

| Module | What it does |
|--------|-------------|
| **Workbench** | Advisor-facing case workspace (Next.js) |
| **Reasoner** | LLM reasoning engine — Claude tool_use for structured output |
| **Control** | Compliance checks, audit trail, approval workflow |
| **Memory** | RAG over institutional knowledge — pgvector + OpenAI embeddings |
| **Flow** | Workflow orchestration across case lifecycle |

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11+ / FastAPI (async) |
| Database | PostgreSQL + pgvector |
| LLM | Anthropic Claude (tool_use) |
| Embeddings | OpenAI text-embedding-3-small |
| Frontend | Next.js / React / TypeScript / shadcn/ui / Tailwind |
| Auth | WorkOS |
| Doc generation | python-docx, WeasyPrint, Jinja2 |
| Infra | Docker, Azure (EU-region) |

---

## Getting Started

See **[SETUP.md](SETUP.md)** for full setup instructions. Quick start:

```bash
# 1. Environment
cp .env.example .env
cp backend/.env.example backend/.env
# Fill in API keys (see SETUP.md for details)

# 2. Infrastructure
docker compose up -d

# 3. Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# 4. Seed dev data
python -m scripts.seed

# 5. Run
uvicorn app.main:app --reload
```

API: http://localhost:8000 | Docs: http://localhost:8000/docs

---

## API Highlights

| Endpoint | What it does |
|----------|-------------|
| `POST /api/v1/cases/{id}/generate-recommendation` | AI-generates a full structured recommendation |
| `POST /api/v1/recommendations/{id}/generate-document` | Generates a compliance-ready recommendation pack (DOCX/PDF) |
| `GET /api/v1/documents/{id}/download` | Downloads the generated document |
| `POST /api/v1/knowledge/search` | Semantic search over institutional knowledge |
| `GET /api/v1/cases/{id}/audit` | Full audit trail for a case |

---

## Project Structure

```
Aetherion/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # Route handlers
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Reasoner, Control, Memory, Flow, Document
│   │   ├── prompts/            # Jinja2 LLM + document templates
│   │   └── utils/              # Encryption, helpers
│   ├── alembic/                # Database migrations
│   └── scripts/                # Seed data, pipeline tests
├── frontend/                   # Next.js app (Workbench UI)
├── docs/                       # Architecture, domain model, compliance spec
└── docker-compose.yml          # PostgreSQL (pgvector) + Redis
```

---

## Starting Market

Swedish occupational pension advisory workflows. The product encodes Swedish pension domain knowledge (ITP1/ITP2, collective agreements, löneväxling, IDD compliance) while the architecture is designed to expand via jurisdiction packs.

---

## Status

Backend complete. Frontend in progress. See **[TODO.md](TODO.md)** for current roadmap.

---

## License

Proprietary. All rights reserved.
