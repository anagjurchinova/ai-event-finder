"""
Utilities for formatting Event entities.

Currently, it provides:
- format_event: Convert an Event object into a single string suitable for embeddings or prompts.
"""

from app.models.event import Event


def format_event(event: Event) -> str:
    """
    Convert an Event object into a string representation for use in embeddings or prompts.

    Combines key event attributes (title, description, location, category, datetime, organizer)
    into a single pipe-separated string. Fields that are missing or None are represented as empty strings.

    Args:
        event (Event): Event object from the database.

    Returns:
        str: Formatted string containing all relevant event fields.
        Example format: "Event Title | Description | Location | Category | 2025-08-26T14:00:00 | Organizer Name"
    """
    fields = [
        event.title or "",
        event.description or "",
        event.location or "",
        event.category or "",
        event.datetime.isoformat() if event.datetime else "",
        str(event.organizer) if event.organizer else "",  # You could also use organizer.name or email
    ]

    return " | ".join(fields)
