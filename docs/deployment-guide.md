# Local deployment guide

## Prerequisites

- Docker Engine with Compose v2, or Python 3.12+ and Node.js 22+
- Git

## Docker Compose

Copy `.env.example` to `.env`, replace `SECRET_KEY`, then run `make dev`.
The frontend is served at `http://localhost:3000`; the API and OpenAPI document
are at `http://localhost:8000` and `/docs`. PostgreSQL and Redis stay inside the
Compose network. Do not use the development credentials in production.

## Native development

Run `make install`, then run `make api`, `make worker`, and `make frontend` in
separate terminals. Native PostgreSQL/Redis connection URLs must be supplied in
`.env`. Task 3 will add database migrations.

