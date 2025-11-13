# API workflow and project structure

This document explains how the frontend, backend, and `news` app interact, plus recommended reorganization steps for deployment to Vercel and Supabase.

Overview
- Frontend: the React + Vite app under `/frontend`. It runs separately and calls the backend API using environment variable `VITE_API_URL`.
- Backend: the Django project in `/backend`. It exposes a REST API using Django REST Framework and currently hosts the `news` app.
- news: a Django app implementing the `NewsArticle` model, serializers, and views. It provides a read-only (currently) API surface for articles.

Current wiring
- The frontend's `src/lib/api.ts` reads `VITE_API_URL` (defaults to `http://localhost:8000`) and can call endpoints such as `${API_BASE}/api/news/articles/`.
- The Django project mounts the `news` app under `/api/news/` (so articles are at `/api/news/articles/`).
- The backend reads `SUPABASE_DB_URL` to connect to the Supabase (Postgres) database when deployed. Locally it falls back to SQLite.

Why there are three folders
- `frontend`: UI code and client-side data access. This is deployed as a static site (Vite build) on Vercel.
- `backend`: Django server that provides API endpoints, admin, and connects to the database.
- `news`: a Django app inside `backend` that groups news-related models, serializers, and views. It's not a separate backend; it's part of the Django backend.

Recommended structure and goals
1. Keep `frontend/` as a standalone static app that calls the backend API (hosted separately) or the same origin if you use a serverless function.
2. Keep `backend/` as a Django project. Move Django apps (`news`) inside `backend/` if you prefer a single Python package layout (current layout is fine: `news` is top-level Django app alongside `backend`—optionally move into `backend/` package).
3. Configure CORS and environment variables so Vercel-hosted frontend can call the backend.
4. Ensure the backend uses `SUPABASE_DB_URL` to connect to Supabase in production and create a `.env` or set Vercel environment variables accordingly.

Deployment notes (Vercel + Supabase)
- Frontend: deploy the `frontend` directory on Vercel. Set environment variables in Vercel:
  - VITE_API_URL -> https://<your-backend-url> (pointing to your backend deployment or serverless function)
  - VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY if you use Supabase directly from the frontend.

- Backend: deploy Django separately (e.g., Render, Fly, Railway) or convert Django API to serverless functions (more work). Configure environment variables:
  - DJANGO_SECRET_KEY
  - DJANGO_DEBUG=false
  - SUPABASE_DB_URL=postgres://user:pass@host:port/dbname
  - CORS_ALLOWED_ORIGINS (include your Vercel site URL)

API endpoints
- GET /api/news/articles/  -> list articles
- GET /api/news/articles/{id}/ -> article detail

Next steps I will perform now
- Add a `.env.example` showing relevant env vars.
- Add `README.md` summary in project root with short deployment instructions.
- Run `python manage.py check` to verify Django imports and routing are valid.

If you prefer to move the `news` app inside the `backend/` package (so files live at `backend/news/`) I can move files and update imports—tell me if you prefer that layout.


If you want, I’ll adapt the tests to be discovered by Django’s test runner (we can move test class name or run python manage.py test backend.news).

# start backend
python manage.py runserver

# from frontend/
npm install
npm run dev

start frontend

# SQL schema for NewsArticle table
CREATE TABLE public.news_newsarticle (
id BIGSERIAL PRIMARY KEY,
title VARCHAR(255) NOT NULL,
content TEXT NOT NULL,
source_link VARCHAR(500) NOT NULL,
status VARCHAR(2) NOT NULL DEFAULT 'DR',
created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
published_at TIMESTAMPTZ NULL,
author_id BIGINT NULL,  -- optional reference to auth_user.id (no FK constraint here)
relevance_score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
industry_tags JSONB NOT NULL DEFAULT '[]'::jsonb
);

ALTER TABLE public.news_newsarticle
ADD CONSTRAINT news_newsarticle_status_check
CHECK (status IN ('DR','PR','PB','ER'));

--- 
CREATE TABLE public.news_auditlog (
id BIGSERIAL PRIMARY KEY,
action VARCHAR(100) NOT NULL,
timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
actor_id BIGINT NULL,      -- optional reference to auth_user.id
article_id BIGINT NULL     -- optional reference to news_newsarticle.id
);

## insert into NewsArticle 
INSERT INTO public.news_newsarticle
(title, content, source_link, status, published_at, relevance_score, industry_tags)
VALUES
(
'OpenAI Releases GPT-5 with Multimodal Reasoning',
'OpenAI announces GPT-5, featuring advanced multimodal reasoning capabilities and improved context understanding.',
'https://example.com/openai-gpt5',
'PB',
'2025-10-28T10:30:00+00',
0.0,
'["GPT-5","Language Model","Multimodal"]'::jsonb
);

# SQL schema for news_tool table
CREATE TABLE public.news_tool (
id BIGSERIAL PRIMARY KEY,
external_id VARCHAR(64),
name VARCHAR(255) NOT NULL,
description TEXT,
url VARCHAR(1000),
logo VARCHAR(1000),
category VARCHAR(255),
subcategories JSONB NOT NULL DEFAULT '[]'::jsonb,
pricing VARCHAR(100),
price_from NUMERIC(10,2),
rating DOUBLE PRECISION,
tags JSONB NOT NULL DEFAULT '[]'::jsonb,
raw_payload JSONB,
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_news_tool_external_id ON public.news_tool(external_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_news_tool_url_lower ON public.news_tool ((lower(url)));
CREATE INDEX IF NOT EXISTS idx_news_tool_tags_gin ON public.news_tool USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_news_tool_subcategories_gin ON public.news_tool USING GIN (subcategories);

## insert into news_tool
INSERT INTO public.news_tool
(external_id, name, description, url, logo, category, subcategories, pricing, price_from, rating, tags)
VALUES
(
'3',
'Taskade',
'AI-powered productivity workspace with task management, notes, and collaboration tools.',
'https://taskade.com',
'https://via.placeholder.com/60',
'AI Productivity Tools',
'["Task Management","Collaboration"]'::jsonb,
'Freemium',
8,
4.3,
'["Productivity","Tasks","Collaboration"]'::jsonb
);


