# AI-Powered Legal Document Analyzer

A full-stack web application that analyzes legal documents using RAG + GPT-4o. Upload contracts, NDAs, and employment agreements to extract clauses, flag risks, generate plain-English summaries, and compare documents.

## Architecture

```
React (Vite) → FastAPI → Celery Worker → PostgreSQL + Redis
                  ↓                           ↓
              OpenAI API              FAISS + PGVector
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Tailwind CSS, Zustand |
| Backend | FastAPI, SQLAlchemy 2.x, Pydantic |
| AI/ML | GPT-4o, text-embedding-3-small, LangChain, FAISS |
| Database | PostgreSQL 16 + PGVector |
| Cache/Broker | Redis 7 |
| Task Queue | Celery |
| Containerization | Docker Compose |

## Prerequisites

- Docker and Docker Compose
- OpenAI API key

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd legal-doc-analyzer
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env and set your OPENAI_API_KEY
   ```

3. Start the stack:
   ```bash
   make up
   ```

4. Run database migrations:
   ```bash
   make migrate
   ```

5. Seed demo data:
   ```bash
   make seed
   ```

6. Open the app:
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - Login: `demo@example.com` / `Demo1234`

## Project Structure

```
├── backend/          # FastAPI + Celery
│   ├── src/
│   │   ├── api/      # REST endpoints
│   │   ├── core/     # Business logic (parser, chunker, embedder)
│   │   ├── models/   # SQLAlchemy models
│   │   ├── rag/      # LLM chains, prompts, vector store
│   │   ├── schemas/  # Pydantic schemas
│   │   └── tasks/    # Celery tasks
│   └── tests/
├── frontend/         # React + Vite
│   └── src/
│       ├── api/      # API client
│       ├── components/
│       ├── pages/
│       └── store/    # Zustand stores
├── docker/
└── docker-compose.yml
```

## Make Commands

| Command | Description |
|---|---|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make build` | Build Docker images |
| `make logs` | View logs |
| `make test` | Run backend tests |
| `make migrate` | Run database migrations |
| `make seed` | Seed demo data |
| `make lint` | Lint backend code |
| `make format` | Format backend code |

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` — Register
- `POST /api/v1/auth/login` — Login
- `POST /api/v1/auth/refresh` — Refresh token
- `POST /api/v1/auth/logout` — Logout
- `GET /api/v1/auth/me` — Current user

### Documents
- `POST /api/v1/documents/upload` — Upload document
- `GET /api/v1/documents` — List documents
- `GET /api/v1/documents/{id}` — Get document
- `DELETE /api/v1/documents/{id}` — Delete document

### Analysis
- `GET /api/v1/analyses/{document_id}` — Full analysis
- `GET /api/v1/analyses/{document_id}/clauses` — Clauses
- `GET /api/v1/analyses/{document_id}/summary` — Summary
- `POST /api/v1/analyses/{document_id}/compare` — Compare

### Queries (RAG)
- `POST /api/v1/queries/{document_id}` — Ask question
- `GET /api/v1/queries/{document_id}/history` — Query history

### System
- `GET /api/v1/health` — Health check
- `GET /api/v1/jobs/{id}` — Job status

## Design Decisions

- **Chunking Strategy**: Section-aware chunking with 800-token chunks and 150-token overlap preserves clause boundaries
- **RAG Approach**: FAISS per-document index for fast retrieval + PGVector for cross-document queries
- **Risk Scoring**: Weighted average of clause-level risks (critical=100, high=75, medium=40, low=10, info=0)
- **Dual Storage**: FAISS for speed, PGVector for persistence and cross-document search

## Known Limitations

- OCR not supported for scanned PDFs (text-based PDFs only)
- DOCX page count is estimated (always returns 1)
- Requires OpenAI API key (no offline mode)
- Single-user optimized (no team/org features)

## License

MIT
