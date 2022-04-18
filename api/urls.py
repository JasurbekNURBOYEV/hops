# built-in

# local
from rest_framework import authentication

# django-specific
from django.urls import path, include

# third party
from rest_framework.routers import DefaultRouter
from drf_yasg2.views import get_schema_view
from drf_yasg2 import openapi

from greed_island.views import TagsViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="Hops API",
        default_version='v1',
    ),
    public=False,
    authentication_classes=(authentication.BasicAuthentication,)
)

router = DefaultRouter()
router.register(prefix="tags", viewset=TagsViewSet)


urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
]
