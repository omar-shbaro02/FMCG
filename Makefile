.PHONY: install dev test lint format typecheck check api frontend worker migrate

install:
	python3 -m pip install -e './backend[dev]'
	cd frontend && npm install

dev:
	docker compose up --build

api:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

worker:
	cd backend && celery -A app.workers.celery_app worker --loglevel=info

migrate:
	cd backend && alembic upgrade head

test:
	cd backend && pytest
	cd frontend && npm test -- --run

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

format:
	cd backend && ruff format .
	cd frontend && npm run format

typecheck:
	cd backend && mypy app
	cd frontend && npm run typecheck

check: lint typecheck test
