# API workflow and architecture map

## Index

- [Overview](#overview)
- [End-to-end flow](#end-to-end-flow)
- [API surface](#api-surface)
- [Data source rules](#data-source-rules)
- [Environment variables](#environment-variables)
- [Deployment notes](#deployment-notes)
- [Local development](#local-development)

## Overview

GrowKnow is split into three runtime parts:

- `frontend/` — React + Vite user interface.
- `backend/` — Django REST API and admin.
- `n8n/` — automation workflows that collect, filter, and push content into the backend.

The current architecture is intentionally decoupled:

- The frontend renders the UI and fetches data over HTTP.
- Django is the primary API source for articles and tools.
- n8n acts as the ingestion layer and writes new content into Django.

## End-to-end flow

### 1) Frontend requests data

- `frontend/src/lib/api.ts` reads `VITE_API_URL` and defaults to `http://localhost:8000` when not provided.
- `frontend/src/lib/toolsApi.ts` uses the same base URL for tool data.
- The frontend first tries Supabase when both `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` are present.
- If Supabase is not configured, unavailable, or fails, the frontend falls back to the Django API.

### 2) Django serves the API

- The Django project mounts the `news` app under `/api/news/`.
- Read endpoints are handled by Django REST Framework view classes in `backend/news/views.py`.
- A top-level health endpoint is exposed at `/health/`.

### 3) n8n ingests external content

The automation workflow in `n8n/workflow.json` runs on a schedule and follows this path:

1. Fetch RSS from the external AI news feed.
2. Convert XML to JSON.
3. Split items into individual articles.
4. Use Ollama to classify whether each item is AI/ML-related.
5. Keep only the positive matches.
6. Format the payload for Django.
7. POST the result to the backend article endpoint.

For a dedicated breakdown of the automation, see `docs/n8n_workflow.md`.

## API surface

### News articles

- `GET /api/news/articles/` — list articles
- `GET /api/news/articles/{id}/` — article detail

### Tools

- `GET /api/news/tools/` — list tools
- `GET /api/news/tools/{id}/` — tool detail

### Health

- `GET /health/` — basic app and database connectivity check

## Data source rules

Current read order in the frontend:

1. Supabase, when configured and reachable.
2. Django API at `VITE_API_URL`.

This keeps Supabase optional while preserving Django as the supported API path.

## Environment variables

### Frontend

- `VITE_API_URL` — base URL for the backend API.
- `VITE_SUPABASE_URL` — optional Supabase project URL.
- `VITE_SUPABASE_ANON_KEY` — optional Supabase anonymous key.

### Backend

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `SUPABASE_DB_URL` — production Postgres connection string when using Supabase.
- `CORS_ALLOWED_ORIGINS` — include the deployed frontend origin.

## Deployment notes

### Frontend deployment

- Deploy `frontend/` as a static site.
- Point `VITE_API_URL` to the deployed Django backend.
- Add Supabase variables only if you want the frontend to use Supabase directly as an optional read source.

### Backend deployment

- Deploy Django separately from the frontend.
- Configure CORS so the frontend domain can access the API.
- Use `SUPABASE_DB_URL` in production and SQLite locally.

### Automation deployment

- Run n8n with the provided Docker Compose setup.
- Ensure n8n can reach Ollama and Django from inside the container.
- The workflow uses `host.docker.internal` for both Ollama and the backend API.

## Local development

From the project root:

```bash
python manage.py runserver
```

From `frontend/`:

```bash
npm install
npm run dev
```
