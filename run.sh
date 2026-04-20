#!/usr/bin/env bash
set -euo pipefail

FRONTEND_PORT="${FRONTEND_PORT:-3080}"

echo "========================================="
echo "  Legal Document Analyzer - Setup & Run"
echo "========================================="
echo ""

# 1. Create .env from example if it doesn't exist
if [ ! -f .env ]; then
  echo "→ Creating .env from .env.example..."
  cp .env.example .env
  echo "  ⚠️  Edit .env and set your OPENAI_API_KEY before AI features will work."
  echo ""
else
  echo "→ .env already exists, skipping."
fi

# 2. Build all Docker images
echo "→ Building Docker images (this may take a few minutes on first run)..."
docker compose build

# 3. Stop any existing containers cleanly
docker compose down 2>/dev/null || true

# 4. Start infrastructure services first
echo "→ Starting PostgreSQL and Redis..."
docker compose up -d postgres redis

# 5. Wait for postgres to be healthy
echo "→ Waiting for PostgreSQL to be ready..."
until docker compose exec -T postgres pg_isready -U legaluser -q 2>/dev/null; do
  sleep 2
done
echo "  PostgreSQL is ready."

# 6. Wait for Redis to be healthy
echo "→ Waiting for Redis to be ready..."
until docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; do
  sleep 2
done
echo "  Redis is ready."

# 7. Generate initial migration if none exist
MIGRATION_COUNT=$(find backend/alembic/versions -name '*.py' 2>/dev/null | wc -l | tr -d ' ')
if [ "$MIGRATION_COUNT" -eq 0 ]; then
  echo "→ Generating initial database migration..."
  docker compose run --rm \
    -v "$(pwd)/backend/alembic/versions:/app/alembic/versions" \
    backend alembic revision --autogenerate -m "initial_schema"

  # Fix pgvector import in generated migration
  for f in backend/alembic/versions/*.py; do
    if grep -q "pgvector.sqlalchemy" "$f" && ! grep -q "import pgvector" "$f"; then
      sed -i.bak 's/^import sqlalchemy as sa$/import sqlalchemy as sa\nimport pgvector.sqlalchemy/' "$f"
      rm -f "${f}.bak"
      echo "  Fixed pgvector import in migration."
    fi
  done
fi

# 8. Run database migrations
echo "→ Running database migrations..."
docker compose run --rm \
  -v "$(pwd)/backend/alembic/versions:/app/alembic/versions" \
  backend alembic upgrade head

# 9. Seed demo data
echo "→ Seeding demo data..."
docker compose run --rm backend python -m scripts.seed

# 10. Start all remaining services
echo "→ Starting all services..."
docker compose up -d

# Check if frontend started
if docker compose ps frontend 2>/dev/null | grep -q "running"; then
  FRONTEND_MSG="  Frontend:  http://localhost:${FRONTEND_PORT}"
else
  FRONTEND_MSG="  Frontend:  ⚠️  Failed to start (port conflict). Run the frontend locally:"
  FRONTEND_MSG="${FRONTEND_MSG}\n             cd frontend && npm install && npm run dev"
fi

echo ""
echo "========================================="
echo "  ✅ Backend services are running!"
echo "========================================="
echo ""
echo -e "$FRONTEND_MSG"
echo "  API Docs:  http://localhost:8000/docs"
echo "  Health:    http://localhost:8000/api/v1/health"
echo ""
echo "  Demo login:"
echo "    Email:    demo@example.com"
echo "    Password: Demo1234"
echo ""
echo "  Useful commands:"
echo "    docker compose logs -f    # View logs"
echo "    docker compose down       # Stop everything"
echo "    make test                 # Run tests"
echo ""
