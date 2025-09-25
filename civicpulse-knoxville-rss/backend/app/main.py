
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import yaml

from .db import Base, engine, get_db
from . import models, schemas
from .ranking import score_item
from .scrapers.generic import scrape_from_config

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CivicPulse API", version="0.1.0")

# CORS for local dev and simple frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/items", response_model=schemas.Item)
def create_item(payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    itm = models.Item(
        title=payload.title,
        summary=payload.summary,
        url=payload.url,
        source=payload.source,
        category=payload.category,
        city=payload.city,
        published_at=payload.published_at,
        is_official=payload.is_official,
        importance=0.0,
    )
    itm.importance = score_item({
        "title": itm.title,
        "summary": itm.summary,
        "source": itm.source,
        "category": itm.category,
        "published_at": itm.published_at,
        "is_official": itm.is_official
    })
    db.add(itm)
    db.commit()
    db.refresh(itm)
    return itm

@app.get("/items", response_model=List[schemas.Item])
def list_items(limit: int = 50, db: Session = Depends(get_db), city: str | None = None, category: str | None = None):
    q = db.query(models.Item)
    if city:
        q = q.filter(models.Item.city == city)
    if category:
        q = q.filter(models.Item.category == category)
    q = q.order_by(models.Item.importance.desc(), models.Item.published_at.desc().nullslast())
    return q.limit(limit).all()

@app.post("/ingest/from-config")
def ingest_from_config(db: Session = Depends(get_db)):
    """Mock ingest that reads scraper_sources.yaml and creates placeholder items."""
    with open("app/scraper_sources.yaml","r") as f:
        sources = yaml.safe_load(f) or []
    created = 0
    for src in sources:
        for item in scrape_from_config(src):
            payload = schemas.ItemCreate(**item)
            create_item(payload, db)
            created += 1
    return {"created": created}

@app.post("/comments", response_model=schemas.Comment)
def add_comment(payload: schemas.CommentCreate, db: Session = Depends(get_db)):
    # Minimal validation
    item = db.query(models.Item).filter(models.Item.id == payload.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    c = models.Comment(item_id=payload.item_id, author=payload.author, body=payload.body)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@app.get("/comments/{item_id}", response_model=List[schemas.Comment])
def get_comments(item_id: int, db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.item_id == item_id).order_by(models.Comment.created_at.desc()).all()


# ==================== Marketplace ====================
@app.post("/listings", response_model=schemas.Listing)
def create_listing(payload: schemas.ListingCreate, db: Session = Depends(get_db)):
    l = models.Listing(**payload.dict())
    db.add(l)
    db.commit()
    db.refresh(l)
    return l

@app.get("/listings", response_model=List[schemas.Listing])
def list_listings(db: Session = Depends(get_db), city: str | None = "Knoxville, TN", category: str | None = None, active: bool = True, limit: int = 100):
    q = db.query(models.Listing).filter(models.Listing.is_active == active)
    if city:
        q = q.filter(models.Listing.city == city)
    if category:
        q = q.filter(models.Listing.category == category)
    return q.order_by(models.Listing.created_at.desc()).limit(limit).all()

# ==================== Community Events ====================
@app.post("/community-events", response_model=schemas.CommunityEvent)
def create_event(payload: schemas.CommunityEventCreate, db: Session = Depends(get_db)):
    ev = models.CommunityEvent(**payload.dict())
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev

@app.post("/community-events/{event_id}/approve")
def approve_event(event_id: int, db: Session = Depends(get_db)):
    ev = db.query(models.CommunityEvent).filter(models.CommunityEvent.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    ev.is_approved = True
    db.commit()
    return {"ok": True}

@app.get("/community-events", response_model=List[schemas.CommunityEvent])
def list_events(db: Session = Depends(get_db), city: str | None = "Knoxville, TN", upcoming_only: bool = True, limit: int = 100):
    q = db.query(models.CommunityEvent).filter(models.CommunityEvent.is_approved == True)
    if city:
        q = q.filter(models.CommunityEvent.city == city)
    if upcoming_only:
        q = q.filter(models.CommunityEvent.starts_at >= datetime.utcnow())
    return q.order_by(models.CommunityEvent.starts_at.asc()).limit(limit).all()

# ==================== RSVPs ====================
@app.post("/rsvps", response_model=schemas.RSVP)
def create_rsvp(payload: schemas.RSVPCreate, db: Session = Depends(get_db)):
    ev = db.query(models.CommunityEvent).filter(models.CommunityEvent.id == payload.event_id).first()
    if not ev or not ev.is_approved:
        raise HTTPException(status_code=400, detail="Event not found or not approved")
    r = models.RSVP(**payload.dict())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@app.get("/community-events/{event_id}/rsvps", response_model=List[schemas.RSVP])
def list_rsvps(event_id: int, db: Session = Depends(get_db)):
    return db.query(models.RSVP).filter(models.RSVP.event_id == event_id).order_by(models.RSVP.created_at.desc()).all()


# ==================== Government Directory & Elections ====================
@app.post("/persons", response_model=schemas.Person)
def create_person(payload: schemas.PersonCreate, db: Session = Depends(get_db)):
    p = models.Person(**payload.dict())
    db.add(p); db.commit(); db.refresh(p); return p

@app.get("/persons", response_model=List[schemas.Person])
def list_persons(db: Session = Depends(get_db), party: str | None = None, q: str | None = None, limit: int = 200):
    qry = db.query(models.Person)
    if party: qry = qry.filter(models.Person.party == party)
    if q: qry = qry.filter(models.Person.full_name.ilike(f"%{q}%"))
    return qry.order_by(models.Person.full_name.asc()).limit(limit).all()

@app.post("/offices", response_model=schemas.Office)
def create_office(payload: schemas.OfficeCreate, db: Session = Depends(get_db)):
    o = models.Office(**payload.dict())
    db.add(o); db.commit(); db.refresh(o); return o

@app.get("/offices", response_model=List[schemas.Office])
def list_offices(db: Session = Depends(get_db), jurisdiction: str | None = "City of Knoxville", level: str | None = None, limit: int = 200):
    qry = db.query(models.Office)
    if jurisdiction: qry = qry.filter(models.Office.jurisdiction == jurisdiction)
    if level: qry = qry.filter(models.Office.level == level)
    return qry.order_by(models.Office.name.asc()).limit(limit).all()

@app.post("/terms", response_model=schemas.Term)
def create_term(payload: schemas.TermCreate, db: Session = Depends(get_db)):
    t = models.Term(**payload.dict())
    db.add(t); db.commit(); db.refresh(t); return t

@app.get("/incumbents")
def list_incumbents(db: Session = Depends(get_db), jurisdiction: str | None = "City of Knoxville"):
    # returns office + person
    from sqlalchemy import and_
    terms = db.query(models.Term).filter(models.Term.is_incumbent == True).all()
    result = []
    for t in terms:
        office = db.query(models.Office).filter(models.Office.id == t.office_id).first()
        if jurisdiction and office and office.jurisdiction != jurisdiction:
            continue
        person = db.query(models.Person).filter(models.Person.id == t.person_id).first()
        result.append({
            "office": {"id": office.id, "name": office.name, "jurisdiction": office.jurisdiction, "level": office.level, "district": office.district},
            "person": {"id": person.id, "full_name": person.full_name, "party": person.party, "website": person.website, "email": person.email, "phone": person.phone, "photo_url": person.photo_url}
        })
    return result

@app.post("/actions", response_model=schemas.Action)
def create_action(payload: schemas.ActionCreate, db: Session = Depends(get_db)):
    a = models.Action(**payload.dict())
    db.add(a); db.commit(); db.refresh(a); return a

@app.get("/actions", response_model=List[schemas.Action])
def list_actions(db: Session = Depends(get_db), person_id: int | None = None, category: str | None = None, limit: int = 200):
    q = db.query(models.Action)
    if person_id: q = q.filter(models.Action.person_id == person_id)
    if category: q = q.filter(models.Action.category == category)
    return q.order_by(models.Action.date.desc().nullslast()).limit(limit).all()

@app.post("/races", response_model=schemas.Race)
def create_race(payload: schemas.RaceCreate, db: Session = Depends(get_db)):
    r = models.Race(**payload.dict())
    db.add(r); db.commit(); db.refresh(r); return r

@app.get("/races", response_model=List[schemas.Race])
def list_races(db: Session = Depends(get_db), active: bool | None = True, jurisdiction: str | None = None, level: str | None = None, limit: int = 200):
    q = db.query(models.Race)
    if active is not None: q = q.filter(models.Race.is_active == active)
    if jurisdiction: q = q.filter(models.Race.jurisdiction == jurisdiction)
    if level: q = q.filter(models.Race.level == level)
    return q.order_by(models.Race.election_date.asc().nullslast()).limit(limit).all()

@app.post("/candidacies", response_model=schemas.Candidacy)
def create_candidacy(payload: schemas.CandidacyCreate, db: Session = Depends(get_db)):
    c = models.Candidacy(**payload.dict())
    db.add(c); db.commit(); db.refresh(c); return c

@app.get("/candidates")
def list_candidates(db: Session = Depends(get_db), race_id: int | None = None):
    q = db.query(models.Candidacy)
    if race_id: q = q.filter(models.Candidacy.race_id == race_id)
    out = []
    for c in q.all():
        p = db.query(models.Person).filter(models.Person.id == c.person_id).first()
        out.append({
            "person": {"id": p.id, "full_name": p.full_name, "party": p.party, "website": p.website, "photo_url": p.photo_url},
            "candidacy": {"id": c.id, "race_id": c.race_id, "party": c.party, "status": c.status, "platform": c.platform, "website": c.website, "filed_date": c.filed_date}
        })
    return out

@app.post("/positions", response_model=schemas.Position)
def create_position(payload: schemas.PositionCreate, db: Session = Depends(get_db)):
    p = models.Position(**payload.dict())
    db.add(p); db.commit(); db.refresh(p); return p

@app.get("/positions", response_model=List[schemas.Position])
def list_positions(db: Session = Depends(get_db), person_id: int | None = None, topic: str | None = None, limit: int = 200):
    q = db.query(models.Position)
    if person_id: q = q.filter(models.Position.person_id == person_id)
    if topic: q = q.filter(models.Position.topic == topic)
    return q.order_by(models.Position.date.desc().nullslast()).limit(limit).all()


from fastapi.responses import Response
from urllib.parse import quote
from datetime import datetime

def _rss_header(title: str, link: str = "", desc: str = ""):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{title}</title>
    <link>{link}</link>
    <description>{desc}</description>
    <lastBuildDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>
"""

def _rss_item(title: str, link: str, description: str = "", pubDate: str | None = None, guid: str | None = None):
    pub = pubDate or datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
    g = guid or link or title
    # naive minimal escaping
    def esc(s): 
        return (s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    return f"""    <item>
      <title>{esc(title)}</title>
      <link>{esc(link)}</link>
      <guid>{esc(g)}</guid>
      <pubDate>{pub}</pubDate>
      <description>{esc(description)}</description>
    </item>
"""

def _rss_footer():
    return "  </channel>\n</rss>\n"

@app.get("/rss/incumbents.xml")
def rss_incumbents(jurisdiction: str = "City of Knoxville", db: Session = Depends(get_db)):
    terms = db.query(models.Term).filter(models.Term.is_incumbent == True).all()
    items = []
    for t in terms:
        office = db.query(models.Office).filter(models.Office.id == t.office_id).first()
        if jurisdiction and office and office.jurisdiction != jurisdiction:
            continue
        person = db.query(models.Person).filter(models.Person.id == t.person_id).first()
        title = f"{person.full_name} — {office.name}"
        link = person.website or ""
        desc = f"Party: {person.party or 'Nonpartisan'} | Office: {office.jurisdiction} ({office.level})"
        items.append(_rss_item(title, link, desc))
    xml = _rss_header(f"Incumbents — {jurisdiction}") + "".join(items) + _rss_footer()
    return Response(content=xml, media_type="application/rss+xml")

@app.get("/rss/races.xml")
def rss_races(jurisdiction: str = "City of Knoxville", level: str | None = "city", db: Session = Depends(get_db)):
    q = db.query(models.Race)
    if jurisdiction: q = q.filter(models.Race.jurisdiction == jurisdiction)
    if level: q = q.filter(models.Race.level == level)
    races = q.filter(models.Race.is_active == True).all()
    items = []
    for r in races:
        title = r.name
        # Deep-link idea: candidates feed for this race
        link = f"/candidates?race_id={r.id}"
        desc = f"Election date: {r.election_date}"
        items.append(_rss_item(title, link, desc, guid=f"race-{r.id}"))
    xml = _rss_header(f"Active Races — {jurisdiction}") + "".join(items) + _rss_footer()
    return Response(content=xml, media_type="application/rss+xml")

@app.get("/rss/candidates.xml")
def rss_candidates(race_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Candidacy)
    if race_id: q = q.filter(models.Candidacy.race_id == race_id)
    items = []
    for c in q.all():
        p = db.query(models.Person).filter(models.Person.id == c.person_id).first()
        title = f"{p.full_name} ({c.party or p.party or 'Nonpartisan'})"
        link = p.website or ""
        desc = f"Status: {c.status or '—'} | Race #{c.race_id} | Platform: {(c.platform or '')[:240]}"
        items.append(_rss_item(title, link, desc, guid=f"cand-{c.id}"))
    header_title = f"Candidates" + (f" — Race #{race_id}" if race_id else "")
    xml = _rss_header(header_title) + "".join(items) + _rss_footer()
    return Response(content=xml, media_type="application/rss+xml")

@app.get("/rss/person.xml")
def rss_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not person:
        return Response(status_code=404, content="Not found")
    # positions
    positions = db.query(models.Position).filter(models.Position.person_id == person_id).all()
    actions = db.query(models.Action).filter(models.Action.person_id == person_id).all()
    items = []
    for pos in positions:
        title = f"Position: {pos.topic}"
        link = pos.source_url or (person.website or "")
        desc = (pos.stance or "")
        items.append(_rss_item(title, link, desc, guid=f"pos-{pos.id}"))
    for act in actions:
        title = f"Record: {act.title}"
        link = act.source_url or (person.website or "")
        desc = f"{act.category or ''} | {act.outcome or ''} | {(act.description or '')[:240]}"
        pub = act.date.strftime('%a, %d %b %Y %H:%M:%S +0000') if act.date else None
        items.append(_rss_item(title, link, desc, pubDate=pub, guid=f"act-{act.id}"))
    xml = _rss_header(f"{person.full_name} — Positions & Record", person.website or "") + "".join(items) + _rss_footer()
    return Response(content=xml, media_type="application/rss+xml")
