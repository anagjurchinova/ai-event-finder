"""
Schemas for the User entity using Marshmallow.

- CreateUserSchema: validates and deserializes incoming user creation payloads.
- UpdateUserSchema: validates and deserializes user update payloads (all fields optional).
- UserSchema: serializes User model instances for API responses, excluding sensitive fields like passwords.

Includes pre-load processing to trim strings and normalize emails.
"""

from marshmallow import Schema, fields, validate, EXCLUDE, pre_load

from app.util.user_util import (
    PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH, NAME_MAX_LENGTH, SURNAME_MAX_LENGTH, EMAIL_MAX_LENGTH)


class CreateUserSchema(Schema):
    """
    Schema for incoming user creation payloads.

    - Validates and deserializes client-provided data.
    - Preprocesses string fields: trims whitespace and lowercases email.
    - Enforces string length, email format, and password complexity requirements.
    """

    class Meta:
        # Drop any unknown fields instead of raising errors
        unknown = EXCLUDE

    @pre_load
    def strip_strings(self, data, **kwargs):
        """
        Trim leading/trailing whitespace on 'name' and 'surname'.
        """
        for key in ("name", "surname"):
            val = data.get(key)
            if isinstance(val, str):
                data[key] = val.strip()
        return data

    @pre_load
    def normalize_email(self, data, **kwargs):
        """
        Trim leading/trailing whitespace and lowercase 'email'.
        """
        email = data.get("email")
        if isinstance(email, str):
            data["email"] = email.strip().lower()
        return data

    """
    Name field:
      - Required
      - Must be between 1 and 50 characters after trimming
    """
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=NAME_MAX_LENGTH),
        error_messages={
            "required": "Name is required.",
            "invalid": f"Name must be a string between 1 and {NAME_MAX_LENGTH} characters."
        }
    )

    """
    Surname field:
      - Required
      - Must be between 1 and 50 characters after trimming
    """
    surname = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=SURNAME_MAX_LENGTH),
        error_messages={
            "required": "Surname is required.",
            "invalid": f"Surname must be a string between 1 and {SURNAME_MAX_LENGTH} characters."
        }
    )

    """
    Email field:
      - Required
      - Validates correct email format
    """
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Must be a valid email address."
        },
        validate=validate.Length(min=1, max=EMAIL_MAX_LENGTH)
    )

    """
    Password field:
      - Required
      - Load-only: never serialized back to client
      - Must be 8–80 characters
      - Must contain at least one uppercase letter and one number
    """
    password = fields.Str(
        required=True,
        load_only=True,
        validate=[
            validate.Length(
                min=PASSWORD_MIN_LENGTH,
                max=PASSWORD_MAX_LENGTH,
                error="Password must be at least 8 characters long."
            ),
            validate.Regexp(
                r'^(?=.*[A-Z])(?=.*\d).+$',
                error="Password must contain at least one uppercase letter and one number."
            )
        ],
        error_messages={
            "required": "Password is required."
        }
    )


class UpdateUserSchema(Schema):
    """
    Schema for incoming user update payloads.

    - Similar to CreateUserSchema, but all fields are optional.
    - Preprocesses string fields: trims whitespace.
    - Validates field lengths and password complexity if provided.
    """

    class Meta:
        # Drop any unknown fields instead of raising errors
        unknown = EXCLUDE

    @pre_load
    def strip_strings(self, data, **kwargs):
        """
        Trim leading/trailing whitespace on 'name' and 'surname'.
        """
        for key in ("name", "surname"):
            val = data.get(key)
            if isinstance(val, str):
                data[key] = val.strip()
        return data

    """
    Name field:
      - Required
      - Must be between 1 and 50 characters after trimming
    """
    name = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=NAME_MAX_LENGTH),
        error_messages={
            "required": "Name is required.",
            "invalid": f"Name must be a string between 1 and {NAME_MAX_LENGTH} characters."
        }
    )

    """
    Surname field:
      - Required
      - Must be between 1 and 50 characters after trimming
    """
    surname = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=SURNAME_MAX_LENGTH),
        error_messages={
            "required": "Surname is required.",
            "invalid": f"Surname must be a string between 1 and {SURNAME_MAX_LENGTH} characters."
        }
    )

    """
    Password field:
      - Required
      - Load-only: never serialized back to client
      - Must be 8–80 characters
      - Must contain at least one uppercase letter and one number
    """
    password = fields.Str(
        required=False,
        load_only=True,
        validate=[
            validate.Length(
                min=PASSWORD_MIN_LENGTH,
                max=PASSWORD_MAX_LENGTH,
                error="Password must be at least 8 characters long."
            ),
            validate.Regexp(
                r'^(?=.*[A-Z])(?=.*\d).+$',
                error="Password must contain at least one uppercase letter and one number."
            )
        ],
        error_messages={
            "required": "Password is required."
        }
    )


class UserSchema(Schema):
    """
    Schema for outgoing user data.

    - Serializes internal User model instances to safe JSON.
    - Excludes sensitive fields like passwords.
    - Preserves field declaration order in output.
    """

    class Meta:
        # Exclude any unexpected attributes when dumping
        unknown = EXCLUDE
        # Preserve field declaration order in output
        ordered = True

    name = fields.Str(
        dump_only=True,
        metadata={"description": "User's first name"}
    )
    surname = fields.Str(
        dump_only=True,
        metadata={"description": "User's surname"}
    )
    email = fields.Email(
        dump_only=True,
        metadata={"description": "User's email address"}
    )
