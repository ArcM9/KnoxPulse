
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ItemBase(BaseModel):
    title: str
    summary: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    published_at: Optional[datetime] = None
    is_official: Optional[bool] = False

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    importance: float
    fetched_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class CommentBase(BaseModel):
    item_id: int
    author: Optional[str] = None
    body: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class ListingBase(BaseModel):
    title: str
    description: str | None = None
    price: float = 0.0
    category: str | None = None
    city: str | None = None
    contact: str | None = None
    is_active: bool = True

class ListingCreate(ListingBase):
    pass

class Listing(ListingBase):
    id: int
    created_at: datetime | None = None
    class Config:
        orm_mode = True

class CommunityEventBase(BaseModel):
    title: str
    description: str | None = None
    venue: str | None = None
    city: str | None = None
    starts_at: datetime
    ends_at: datetime | None = None
    host_contact: str | None = None
    is_approved: bool = False

class CommunityEventCreate(CommunityEventBase):
    pass

class CommunityEvent(CommunityEventBase):
    id: int
    created_at: datetime | None = None
    class Config:
        orm_mode = True

class RSVPBase(BaseModel):
    event_id: int
    name: str
    email: str | None = None
    count: int = 1

class RSVPCreate(RSVPBase):
    pass

class RSVP(RSVPBase):
    id: int
    created_at: datetime | None = None
    class Config:
        orm_mode = True


class PersonBase(BaseModel):
    full_name: str
    party: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    photo_url: str | None = None
    bio: str | None = None

class PersonCreate(PersonBase):
    pass

class Person(PersonBase):
    id: int
    class Config: orm_mode = True

class OfficeBase(BaseModel):
    name: str
    jurisdiction: str
    level: str
    district: str | None = None

class OfficeCreate(OfficeBase): pass

class Office(OfficeBase):
    id: int
    class Config: orm_mode = True

class TermBase(BaseModel):
    person_id: int
    office_id: int
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_incumbent: bool = False

class TermCreate(TermBase): pass

class Term(TermBase):
    id: int
    class Config: orm_mode = True

class ActionBase(BaseModel):
    person_id: int
    title: str
    description: str | None = None
    date: datetime | None = None
    category: str | None = None
    outcome: str | None = None
    sentiment: str | None = None
    source_url: str | None = None

class ActionCreate(ActionBase): pass
class Action(ActionBase):
    id: int
    class Config: orm_mode = True

class RaceBase(BaseModel):
    name: str
    election_date: datetime | None = None
    jurisdiction: str
    level: str
    office_id: int | None = None
    is_active: bool = True

class RaceCreate(RaceBase): pass
class Race(RaceBase):
    id: int
    class Config: orm_mode = True

class CandidacyBase(BaseModel):
    person_id: int
    race_id: int
    party: str | None = None
    platform: str | None = None
    website: str | None = None
    filed_date: datetime | None = None
    status: str | None = None

class CandidacyCreate(CandidacyBase): pass
class Candidacy(CandidacyBase):
    id: int
    class Config: orm_mode = True

class PositionBase(BaseModel):
    person_id: int
    topic: str
    stance: str | None = None
    source_url: str | None = None
    date: datetime | None = None

class PositionCreate(PositionBase): pass
class Position(PositionBase):
    id: int
    class Config: orm_mode = True
