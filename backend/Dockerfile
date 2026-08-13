FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip==26.2.1
COPY pyproject.toml ./
RUN mkdir app && touch app/__init__.py && pip install --no-cache-dir . && rm -rf app
COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic
RUN useradd --create-home appuser
RUN mkdir -p /app/var/uploads && chown -R appuser:appuser /app/var
USER appuser
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
