
# CivicPulse — Local Civic Intelligence (Starter Kit)

This is a minimal, working starter that:
- Ingests (mocked) sources, normalizes them, ranks by importance, and exposes an API.
- Displays a simple web UI.
- Supports comments (no auth yet).

## Run
1) API
```bash
cd civicpulse
docker compose up --build
# or run locally with uvicorn
```

2) Frontend
Open `frontend/index.html` in your browser (or serve via any static server).

## Next steps (recommended roadmap)
- Replace mocked scrapers with real ones in `backend/app/scrapers`:
  - agendas/legislation pages (requests + BeautifulSoup)
  - RSS feeds (feedparser)
  - PDFs (pdfminer.six) when agendas are PDFs
- Add background scheduler (APScheduler) to run scrapers hourly/daily.
- Add Postgres + pgvector for semantic search.
- Add auth (Clerk/Auth0) and moderation for comments.
- Build production web app (Next.js or Remix).
- Build mobile app with Expo (React Native), consuming the same API.
- Add webhooks for Slack/Discord/Twilio SMS alerts for high-importance items.


## Knoxville defaults
`backend/app/scraper_sources.yaml` is pre-filled with Knoxville, TN sources (City Council, County Commission, Ordinances, KUB, Schools, VisitKnoxville). Replace/expand as needed, then implement real scrapers.

## New APIs
- **Marketplace**
  - `POST /listings` — create a listing
  - `GET /listings?city=Knoxville,%20TN&category=for_sale&active=true`
- **Community Events**
  - `POST /community-events` — submit an event (moderated)
  - `POST /community-events/{id}/approve` — approve an event
  - `GET /community-events?city=Knoxville,%20TN&upcoming_only=true` — public feed
  - `POST /rsvps` — RSVP to an approved event
  - `GET /community-events/{id}/rsvps` — list RSVPs (for admins/hosts)

### Moderation Notes
- Add auth (JWT via Auth0/Clerk) and an admin role before going public.
- Auto-spam checks: Akismet, link throttling, flood control, banned words.
- Phone/email validation on listings & events; captcha on submissions.


## Government Directory & Elections (API)
Create data:
```http
POST /offices
{ "name": "Mayor of Knoxville", "jurisdiction": "City of Knoxville", "level": "city" }

POST /persons
{ "full_name": "Jane Doe", "party": "Nonpartisan", "website": "https://example.com" }

POST /terms
{ "person_id": 1, "office_id": 1, "is_incumbent": true }
```

List current officeholders:
`GET /incumbents?jurisdiction=City%20of%20Knoxville`

Track records (“what they have done”):
```http
POST /actions
{ "person_id": 1, "title": "Voted YES on Ordinance 123", "category": "vote", "date": "2025-08-01T00:00:00Z", "outcome": "passed", "source_url": "https://city.url/..." }
GET /actions?person_id=1
```

Capture positions/platforms with sources:
```http
POST /positions
{ "person_id": 1, "topic": "zoning", "stance": "Supports ADUs citywide", "source_url": "https://interview.url/..." }
GET /positions?person_id=1&topic=zoning
```

Elections:
```http
POST /races
{ "name": "Knoxville City Council D4 (2026)", "jurisdiction": "City of Knoxville", "level": "city", "election_date": "2026-08-01T00:00:00Z" }

POST /candidacies
{ "person_id": 2, "race_id": 1, "party": "Nonpartisan", "platform": "Traffic calming, small biz support", "status": "filed" }

GET /candidates?race_id=1
```
**Note:** Fill with verified data and cite sources on actions/positions. Add admin moderation and provenance before launch.


## RSS Feeds for Squarespace (No-Code Embeds)
The API provides:
- `/rss/incumbents.xml?jurisdiction=City%20of%20Knoxville` — current officeholders
- `/rss/races.xml?jurisdiction=City%20of%20Knoxville&level=city` — active races
- `/rss/candidates.xml?race_id=1` — candidates for a race (omit `race_id` for all)
- `/rss/person.xml?person_id=1` — positions + record for a person

### Squarespace Setup
1) Add a **Summary** block → choose **RSS** as the source.
2) Paste the feed URL (e.g., `https://api.knoxpulse.com/rss/incumbents.xml`).
3) Choose a layout (list, grid) and show fields you want (title/description/date).
4) Done — it updates automatically as your API data changes.
