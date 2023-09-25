from django.contrib import admin

from src.images.models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass
