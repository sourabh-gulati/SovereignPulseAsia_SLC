# Fixed Income Analytics - Agent Guide

## Project overview

This repository is a fixed-income analytics application with:

- `frontend/`: Vue 3, TypeScript, and Vite.
- `backend/`: FastAPI, SQLAlchemy, Alembic, and PostgreSQL/Supabase.
- `backend/app/services/treasury.py`: historical Treasury data parsing and import support.

The frontend communicates only with the FastAPI API. Never connect browser code directly to the database or expose database credentials in client-side configuration.

## Local development

Use Docker Compose for the full stack:

```powershell
Copy-Item .env.example .env
# Add a valid DATABASE_URL to .env.
docker compose up --build
```

- UI: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

For focused work, run commands from the relevant directory:

```powershell
cd backend
pytest -q

cd ../frontend
npm run build
npm test
```

## Implementation conventions

- Keep API routes thin; put Treasury data parsing and import support in `backend/app/services/`.
- Define and update request/response models in `backend/app/schemas.py` when the API contract changes.
- Add database schema changes as Alembic migrations in `backend/migrations/versions/`; do not modify a deployed schema manually.
- Preserve missing Treasury tenors as missing values. Do not replace unavailable rates with zero or fabricate observations.
- Treat yields as percentages unless a function or schema explicitly documents another unit.
- Home-page requests must only read stored observations; do not add on-demand Treasury downloads or real-time refresh behavior.
- Use TypeScript types from `frontend/src/services/api.ts` for API payloads. Update them with any backend contract change.
- Keep the Vue view focused on rendering the daily-yields table and its loading or error state.

## Validation expectations

- Backend changes: run `pytest -q` from `backend/`.
- Frontend changes: run `npm run build` from `frontend/`; run `npm test` when tests are present or affected.
- Migration/model/API changes: exercise the affected endpoint and verify a fresh database can apply migrations.
- UI changes: verify loading, empty, and API-error states as well as successful table display.

## Security and configuration

- Do not commit `.env`, connection strings, API keys, or Supabase credentials.
- Update `.env.example` only with safe placeholders and document new required variables in `README.md`.
- Keep CORS origins explicit outside local development.
- Do not log credentials or complete database URLs.

## Scope discipline

- Prefer small, targeted changes that retain the existing Vue/FastAPI architecture.
- Do not upgrade dependencies, reformat unrelated files, or alter generated artifacts unless the task requires it.
- Update `README.md` when setup instructions, API endpoints, or user-visible behavior changes.
