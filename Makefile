.PHONY: up down build logs test migrate makemigration seed lint format shell-db

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

test:
	docker compose run --rm backend pytest tests/ -v

migrate:
	docker compose run --rm backend alembic upgrade head

makemigration:
	docker compose run --rm backend alembic revision --autogenerate -m "$(name)"

seed:
	docker compose run --rm backend python -m scripts.seed

lint:
	docker compose run --rm backend ruff check src/

format:
	docker compose run --rm backend black src/

shell-db:
	docker compose exec postgres psql -U legaluser -d legalanalyzer
