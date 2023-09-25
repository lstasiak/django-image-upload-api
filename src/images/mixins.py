import time
import uuid

from django.core import signing
from django.urls import reverse
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from src.images.models import ExpiringLink, Image
from src.settings import (
    DEFAULT_EXPIRY_LINK_TIME,
    MAX_EXPIRY_LINK_TIME,
    MIN_EXPIRY_LINK_TIME,
)


class ExpiringLinkMixin:
    def generate_expiring_link(
        self, image: Image, expires_in: str = DEFAULT_EXPIRY_LINK_TIME
    ) -> dict:
        subscription = image.owner.subscription
        if not subscription.expiring_link_option:
            raise PermissionDenied(
                "Subscription plan does not have expiring link option enabled."
            )

        if not expires_in.isdigit() or not (
            MIN_EXPIRY_LINK_TIME <= (expires := int(expires_in)) <= MAX_EXPIRY_LINK_TIME
        ):
            raise ValidationError("Invalid value for expires_in")

        identifier = uuid.uuid4()
        signed_link = signing.dumps(str(identifier))

        # Build the full URL for the expiring link
        full_url = self.request.build_absolute_uri(
            reverse("expiring-link-retrieve", kwargs={"signed_link": signed_link})
        )

        current_timestamp = int(time.time())
        expiry_time = current_timestamp + expires

        # create expiring link
        ExpiringLink.objects.create(
            identifier=identifier, link=full_url, image=image, expires_in=expiry_time
        )

        return {"link": full_url}

    @staticmethod
    def decode_signed_value(value: str):
        try:
            return signing.loads(value)
        except signing.BadSignature:
            raise NotFound("Invalid signed link")
