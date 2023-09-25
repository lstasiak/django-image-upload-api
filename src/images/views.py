import mimetypes

from django.http import FileResponse
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser

from src.images.mixins import ExpiringLinkMixin
from src.images.models import ExpiringLink, Image
from src.images.serializers import ExpiringLinkSerializer, ImageSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)


class ExpiringLinkListCreateView(generics.ListCreateAPIView, ExpiringLinkMixin):
    serializer_class = ExpiringLinkSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = self.link
        return response

    def perform_create(self, serializer) -> None:
        expires_in = self.request.data.get("expires_in")
        self.link: dict = self.generate_expiring_link(
            serializer.validated_data["image"], expires_in
        )

    def get_queryset(self):
        return ExpiringLink.objects.filter(image__owner=self.request.user)


class ExpiringLinkDetailView(generics.RetrieveAPIView, ExpiringLinkMixin):
    queryset = ExpiringLink.objects.all()

    def get_object(self):
        signed_link = self.kwargs.get("signed_link")

        expiring_link_id = self.decode_signed_value(signed_link)
        expiring_link = generics.get_object_or_404(self.queryset, pk=expiring_link_id)
        if expiring_link.is_expired():
            expiring_link.delete()
            raise NotFound("Generated link has expired")

        if expiring_link.image.owner != self.request.user:
            raise PermissionDenied("User not authorized to view expiring link")

        return expiring_link.image

    def retrieve(self, request, *args, **kwargs):
        image_file = self.get_object().file
        content_type, encoding = mimetypes.guess_type(image_file.name)
        response = FileResponse(
            image_file,
            content_type=content_type,
            as_attachment=True,
            filename=image_file.name.split("/")[-1],
        )
        return response
