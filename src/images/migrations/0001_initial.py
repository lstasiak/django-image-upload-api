import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import src.images.custom_validators
import src.images.services


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Image",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "identifier",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                (
                    "file",
                    models.ImageField(
                        blank=True,
                        max_length=255,
                        null=True,
                        upload_to=src.images.services.upload_to,
                    ),
                ),
                ("uploaded_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExpiringLink",
            fields=[
                (
                    "identifier",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("link", models.CharField(max_length=255)),
                (
                    "expires_in",
                    models.IntegerField(
                        validators=[
                            src.images.custom_validators.validate_expiration_time
                        ]
                    ),
                ),
                (
                    "image",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expiring_link",
                        to="images.image",
                    ),
                ),
            ],
        ),
    ]
