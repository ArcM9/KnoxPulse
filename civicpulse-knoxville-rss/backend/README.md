
# CivicPulse Backend (MVP)

## Quick start (Docker)
```bash
docker compose up --build
# in another terminal
curl -X POST http://localhost:8000/ingest/from-config
curl http://localhost:8000/items
```

## Local (without Docker)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --reload
```

### API
- `POST /ingest/from-config` — reads `app/scraper_sources.yaml` and inserts placeholder items.
- `GET /items?city=&category=&limit=` — ranked feed by importance.
- `POST /items` — add an item manually (used by real scrapers later).
- `POST /comments` — add a comment to an item.
- `GET /comments/{item_id}` — list comments for an item.

### Next steps
- Implement real scrapers in `app/scrapers` using requests/BeautifulSoup or playwright.
- Add auth (JWT) and rate limiting.
- Switch SQLite to Postgres for production.
- Add background jobs (Celery/APScheduler) to run scrapers on intervals.
