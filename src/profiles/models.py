import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class ThumbnailSize(models.Model):
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField()

    class Meta:
        unique_together = ["height", "width"]

    def __str__(self):
        return f"{self.width}x{self.height}"

    def save(self, *args, **kwargs):
        if self.width == 0:
            self.width = round(self.height * 16 / 9)

        super(ThumbnailSize, self).save(*args, **kwargs)


class Subscription(models.Model):
    identifier = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=240)
    original_file_access = models.BooleanField(default=False)
    expiring_link_option = models.BooleanField(default=False)
    thumbnail_sizes = models.ManyToManyField(ThumbnailSize, blank=True)

    def __str__(self):
        return self.name

    @property
    def get_thumbnail_sizes(self):
        return self.thumbnail_sizes.all()

    @property
    def get_thumbnail_heights(self):
        thumbnails = self.get_thumbnail_sizes
        return [thumbnail.height for thumbnail in thumbnails]


class Profile(AbstractUser):
    identifier = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, null=True, related_name="profiles"
    )

    def __str__(self):
        return (
            f"{self.username} ({self.subscription if self.subscription else 'Basic'})"
        )

    def save(self, *args, **kwargs):
        if self.subscription is None:
            self.subscription = Subscription.objects.get(name="Basic")
        super(Profile, self).save(*args, **kwargs)
