import os
import time
import uuid

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models

from src.images.custom_validators import validate_expiration_time
from src.images.services import upload_to


class Image(models.Model):
    identifier = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    owner = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    file = models.ImageField(upload_to=upload_to, null=True, blank=True, max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.owner} - {self.file}"

    @property
    def get_original_url(self):
        return self.file.url

    def get_thumbnails(self):
        subscription = self.owner.subscription
        thumbnail_heights = subscription.get_thumbnail_heights

        base_file = os.path.dirname(self.file.name)
        # Get a reference to the default storage backend for GCP
        storage = default_storage

        # List all files in the same directory as the original file
        thumbnails = storage.listdir(base_file)[1]
        thumbnails_to_return = []

        for thumbnail in thumbnails:
            name, _ = thumbnail.rsplit(".", 1)
            height = name.split("_")[-1]

            if height.isdigit() and int(height) in thumbnail_heights:
                path_to_thumbnail = os.path.join(
                    settings.MEDIA_URL + base_file, thumbnail
                )
                thumbnails_to_return.append(path_to_thumbnail)

        if subscription.original_file_access:
            thumbnails_to_return.append(self.get_original_url)

        if subscription.expiring_link_option and hasattr(self, "expiring_link"):
            thumbnails_to_return.append(self.expiring_link.link)

        return thumbnails_to_return


class ExpiringLink(models.Model):
    identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.OneToOneField(
        Image, on_delete=models.CASCADE, related_name="expiring_link", unique=True
    )
    link = models.CharField(max_length=255)
    expires_in = models.IntegerField(validators=[validate_expiration_time])

    def __str__(self):
        return f"{self.link} - {self.image}"

    def is_expired(self):
        current_time = time.time()
        return current_time > self.expires_in
