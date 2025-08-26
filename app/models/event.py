from datetime import datetime, UTC

from pgvector.sqlalchemy import Vector
from sqlalchemy import Index

from app.configuration.config import Config
from app.constants import (
    TITLE_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    LOCATION_MAX_LENGTH,
    CATEGORY_MAX_LENGTH,
)
from app.extensions import db

# Association table for many-to-many User <-> Event relationship
guest_list = db.Table(
    'guest_list',
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
)


class Event(db.Model):
    """
    Represents an event in the database.

    Attributes:
        id (int): Primary key.
        title (str): Unique title of the event (max length = TITLE_MAX_LENGTH).
        datetime (datetime): Start date/time of the event (UTC).
        description (str | None): Optional event description (max length = DESCRIPTION_MAX_LENGTH).
        version (int): Optimistic lock version counter for concurrency control.
        embedding (Vector | None): Unified vector for semantic search (dim = UNIFIED_VECTOR_DIM).
        organizer_id (int): Foreign key to the User organizing this event.
        organizer (User): Relationship to the event organizer (one-to-many).
        location (str | None): Event location (max length = LOCATION_MAX_LENGTH).
        category (str | None): Event category (max length = CATEGORY_MAX_LENGTH).
        guests (list[User]): Users attending this event (many-to-many).
    """
    __tablename__ = 'events'

    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(TITLE_MAX_LENGTH), nullable=False, unique=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    description = db.Column(db.String(DESCRIPTION_MAX_LENGTH), nullable=True)
    version = db.Column(db.Integer, nullable=False, default=1)

    # Unified 1024-d vector embedding for semantic search
    embedding = db.Column(Vector(Config.UNIFIED_VECTOR_DIM), nullable=True)

    # --- Relationships ---

    # ONE-TO-MANY: Organizer of the event
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    organizer = db.relationship('User', back_populates='organized_events', lazy='joined')

    # MANY-TO-MANY: Guests attending this event
    guests = db.relationship('User', secondary=guest_list, back_populates='events_attending', lazy='dynamic')

    # Optional metadata
    location = db.Column(db.String(LOCATION_MAX_LENGTH), nullable=True)
    category = db.Column(db.String(CATEGORY_MAX_LENGTH), nullable=True)

    __mapper_args__ = {
        "version_id_col": version
    }

    __table_args__ = (
        Index(
            'idx_events_embedding_cosine',
            'embedding',  # <— string, not Event.embedding
            postgresql_using='ivfflat',
            postgresql_with={'lists': '100'},
            postgresql_ops={'embedding': 'vector_cosine_ops'},
        ),
    )

    def __repr__(self):
        """
                Returns a readable string representation of the event.

                Returns:
                    str: Example '<Event 1 – Party @ 2025-08-26T19:00:00 organized by User 3>'
                """
        return f"<Event {self.id} – {self.title} @ {self.datetime.isoformat()}>"
