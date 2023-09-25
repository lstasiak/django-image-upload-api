import os

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.images.models import ExpiringLink, Image


class ImageSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    file = serializers.ImageField(write_only=True)
    img_urls = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Image
        fields = ["id", "owner", "title", "img_urls", "file"]

    def get_img_urls(self, obj: Image):
        thumbnails = obj.get_thumbnails()
        thumbnails_to_return = []
        for thumbnail in thumbnails:
            if thumbnail.startswith(("https", "http")):
                thumbnails_to_return.append(thumbnail)
                continue

            path = self.context["request"].build_absolute_uri(thumbnail)
            thumbnails_to_return.append(path)

        return thumbnails_to_return

    def validate_file(self, value):
        ext = os.path.splitext(value.name)[1]
        valid_extensions = [".jpg", ".png", ".jpeg"]
        if not ext.lower() in valid_extensions:
            raise ValidationError(
                "Unsupported file extension. Supported types: .jpg, .png, .jpeg"
            )
        return value

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return Image.objects.create(**validated_data)


class ExpiringLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpiringLink
        fields = ["identifier", "link", "image", "expires_in"]
        read_only_fields = ["link"]

    def __init__(self, *args, **kwargs):
        super(ExpiringLinkSerializer, self).__init__(*args, **kwargs)

        owner = self.context["request"].user
        images = Image.objects.filter(owner=owner)
        self.fields["image"].queryset = images
