from django.core.exceptions import ValidationError

from src.settings import MAX_EXPIRY_LINK_TIME, MIN_EXPIRY_LINK_TIME


def validate_expiration_time(value):
    if not (300 <= value <= 30000):
        raise ValidationError(
            f"Expiration time must be between {MIN_EXPIRY_LINK_TIME} and {MAX_EXPIRY_LINK_TIME} seconds."
        )
