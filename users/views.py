from django.conf import settings
from django.db.models import functions
from django.shortcuts import redirect
from rest_framework import viewsets, mixins, views, renderers
from rest_framework.decorators import (detail_route, api_view,
    permission_classes, renderer_classes, authentication_classes)
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from bloghunt import filters
from users import models
from . import serializers


class UserFeedViewSet(viewsets.ModelViewSet):
    template_name = 'myfeeds.html'
    serializer_class = serializers.UserFeedSerializer
    filter_backends = (filters.IsOwnerFilterBackend,)
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.submitted_feeds


class FeedRecommendationViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    template_name = 'recommendations.html'
    serializer_class = serializers.FeedRecommendationSerializer
    filter_backends = (filters.IsOwnerFilterBackend,)
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.FeedRecommendation.objects.all()
