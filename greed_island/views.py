from django.db.models import Count, Exists, Subquery, F, OuterRef
from drf_yasg2.openapi import Parameter
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework import viewsets, status, filters
from rest_framework.response import Response

from greed_island.models import Tag
from core.models import User
from greed_island.serializers import TagSerializer, TagRequestSerializer


class TagsViewSet(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin, viewsets.mixins.CreateModelMixin):
    queryset = Tag.all()
    serializer_class = TagSerializer

    search_fields = [
        'name',
    ]
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        self.user = None  # noqa
        self.subscribed_tags = []  # noqa

        queryset = super(TagsViewSet, self).get_queryset()
        user_uuid = self.request.query_params.get("user")

        if not user_uuid:
            return []

        user = User.get(uuid=user_uuid)
        if not user:
            return []

        self.user = user  # noqa
        self.subscribed_tags = [t.pk for t in user.tags.all()]  # noqa
        queryset = queryset.annotate(
            subscribers_count=Count("subscribers"),
        ).order_by("-subscribers_count")

        return queryset

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'user': self.user,
            'subscribed_tags': self.subscribed_tags
        }

    @swagger_auto_schema(
        manual_parameters=[
            Parameter(
                name="user",
                type=openapi.FORMAT_UUID,
                in_=openapi.IN_QUERY,
                description="UUID of user",
                required=True
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=TagRequestSerializer,
        responses={status.HTTP_201_CREATED: "-nothing-"}
    )
    def create(self, request, *args, **kwargs):
        serializer = TagRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response()
