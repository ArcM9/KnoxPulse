
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.sql import func
from .db import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    summary = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    source = Column(String, index=True, nullable=True)
    category = Column(String, index=True, nullable=True)  # e.g., 'legislation','event','public_notice','news'
    city = Column(String, index=True, nullable=True)
    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    importance = Column(Float, default=0.0)  # computed score
    is_official = Column(Boolean, default=False)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, index=True, nullable=False)
    author = Column(String, nullable=True)  # replace with user id/auth later
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, default=0.0)
    category = Column(String, index=True)  # e.g., 'for_sale','services','housing','gigs'
    city = Column(String, index=True)
    contact = Column(String, nullable=True)  # email/phone (later: user_id)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class CommunityEvent(Base):
    __tablename__ = "community_events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    venue = Column(String, nullable=True)
    city = Column(String, index=True)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=True)
    host_contact = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_approved = Column(Boolean, default=False)  # moderation

class RSVP(Base):
    __tablename__ = "rsvps"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    count = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=False)
    party = Column(String, index=True)  # e.g., 'Democratic','Republican','Independent','Nonpartisan'
    website = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)

class Office(Base):
    __tablename__ = "offices"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # e.g., 'Mayor of Knoxville'
    jurisdiction = Column(String, index=True)  # e.g., 'City of Knoxville', 'Knox County', 'Tennessee'
    level = Column(String, index=True)  # 'city','county','state','federal'
    district = Column(String, nullable=True)  # e.g., 'District 4'

class Term(Base):
    __tablename__ = "terms"
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, index=True, nullable=False)
    office_id = Column(Integer, index=True, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_incumbent = Column(Boolean, default=False)

class Action(Base):
    __tablename__ = "actions"
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, index=True, nullable=False)
    title = Column(String, nullable=False)  # 'Voted YES on Ordinance XYZ'
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=True)
    category = Column(String, index=True)  # 'vote','sponsorship','ethics','initiative','press'
    outcome = Column(String, nullable=True)  # 'passed','failed','pending'
    sentiment = Column(String, nullable=True)  # 'good','bad','neutral' (user-tagged, not authoritative)
    source_url = Column(String, nullable=True)

class Race(Base):
    __tablename__ = "races"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 'Knoxville City Council District 4 (2025)'
    election_date = Column(DateTime, nullable=True)
    jurisdiction = Column(String, index=True)
    level = Column(String, index=True)  # 'city','county','state','federal'
    office_id = Column(Integer, index=True, nullable=True)
    is_active = Column(Boolean, default=True)

class Candidacy(Base):
    __tablename__ = "candidacies"
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, index=True, nullable=False)
    race_id = Column(Integer, index=True, nullable=False)
    party = Column(String, index=True)
    platform = Column(Text, nullable=True)  # what they are running on
    website = Column(String, nullable=True)
    filed_date = Column(DateTime, nullable=True)
    status = Column(String, index=True)  # 'filed','qualified','withdrawn','incumbent','won','lost'

class Position(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, index=True, nullable=False)
    topic = Column(String, index=True)  # 'taxes','zoning','transit','schools'
    stance = Column(Text, nullable=True)
    source_url = Column(String, nullable=True)
    date = Column(DateTime, nullable=True)
