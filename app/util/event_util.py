"""
Utility constants and helper functions for Event entities.

Provides:
- Maximum allowed lengths for event fields.
- Simple helper functions to generate "not found" messages for events by id, title, category, or location.
"""
TITLE_MAX_LENGTH = 50
DESCRIPTION_MAX_LENGTH = 500
LOCATION_MAX_LENGTH = 50
CATEGORY_MAX_LENGTH = 50


# ------------------------
# Helper functions
# ------------------------

def return_not_found_by_id_message(event_id) -> str:
    return f"Event not found with id {event_id}"


def return_not_found_by_title_message(title) -> str:
    return f"Event not found with title {title}"


def return_not_found_by_category_message(category) -> str:
    return f"Event not found with category {category}"


def return_not_found_by_location_message(location) -> str:
    return f"Event not found with location {location}"
