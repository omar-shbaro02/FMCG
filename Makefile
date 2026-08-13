.PHONY: install dev build lint typecheck test check compose-up compose-down

install:
	npm ci
	npm --prefix frontend ci
	python3 -m venv --clear .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -e './backend[dev]'

dev:
	npm --prefix frontend run dev

build:
	npm --prefix frontend run build

lint:
	npm --prefix frontend run lint
	cd backend && ../.venv/bin/ruff check app tests

typecheck:
	npm --prefix frontend run typecheck
	cd backend && ../.venv/bin/mypy app

test:
	npm --prefix frontend test
	cd backend && ../.venv/bin/alembic upgrade head
	cd backend && ../.venv/bin/pytest

check: lint typecheck test build

compose-up:
	docker compose up --build

compose-down:
	docker compose down
