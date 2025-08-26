"""
constants.py

Central location for project-wide constants.
Avoids duplication and ensures consistency across the application.
"""

# ----------------------
# Authentication & Defaults
# ----------------------
DEFAULT_PASSWORD: str = "ChangeMe123!"  # Default password for seeded users

# ----------------------
# Event entity limits
# ----------------------
TITLE_MAX_LENGTH: int       = 100
DESCRIPTION_MAX_LENGTH: int = 1000
LOCATION_MAX_LENGTH: int    = 100
CATEGORY_MAX_LENGTH: int    = 100
