from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.images.views import (
    ExpiringLinkDetailView,
    ExpiringLinkListCreateView,
    ImageViewSet,
)

router = DefaultRouter()

router.register(r"images", ImageViewSet, basename="api-images-view")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "expiring-links/",
        ExpiringLinkListCreateView.as_view(),
        name="expiring-link-create-list",
    ),
    path(
        "expiring-links/<str:signed_link>/",
        ExpiringLinkDetailView.as_view(),
        name="expiring-link-retrieve",
    ),
]
