import io
import logging
import os

from celery import shared_task
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as Img

from src.images.models import Image

logger = logging.getLogger(__name__)


@shared_task
def generate_thumbnails_task(image_pk):
    logger.info(f"generate thumbnails for image pk={image_pk}")

    image = Image.objects.get(id=image_pk)
    filename, ext = os.path.splitext(os.path.basename(image.file.name))
    image_name = filename.split("/")[-1]

    subscription = image.owner.subscription
    thumbnail_sizes = subscription.get_thumbnail_sizes

    for size in thumbnail_sizes:
        original_image = Img.open(image.file)

        thumbnail = original_image.resize((size.width, size.height), Img.LANCZOS)

        io_handler = io.BytesIO()

        thumbnail.save(
            io_handler, format="JPEG" if ext.lower() in [".jpg", ".jpeg"] else "PNG"
        )
        thumbnail_path = f"{image_name}_{size.height}{ext.lower()}"

        thumbnail_file = SimpleUploadedFile(
            thumbnail_path,
            io_handler.getvalue(),
            content_type="image/jpeg"
            if ext.lower() in [".jpg", ".jpeg"]
            else "image/png",
        )
        image.file.save(thumbnail_path, thumbnail_file, save=False)


@shared_task
def cleanup_image_folder_task(path: str):
    logger.info(f"delete thumbnails folder {path}")

    storage = default_storage
    try:
        for file in storage.listdir(os.path.dirname(path))[1]:
            logger.info(f"deleting file from the bucket: {file}")
            storage.delete(os.path.join(os.path.dirname(path), file))
    except FileNotFoundError:
        logger.info(f"No such file or directory: {path}")
