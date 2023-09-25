from django.apps import AppConfig


class ImagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.images"

    def ready(self):
        import src.images.signals  # noqa: F401
