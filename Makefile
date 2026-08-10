.PHONY: install dev build lint typecheck test compose-up compose-down

install:
	npm ci
	npm --prefix frontend ci
	python3 -m pip install -e './backend[dev]'

dev:
	npm run dev

build:
	npm run build

lint:
	npm run lint
	cd backend && ruff check app tests

typecheck:
	npm run typecheck
	cd backend && mypy app

test:
	npm test
	cd backend && pytest

compose-up:
	docker compose up --build

compose-down:
	docker compose down
