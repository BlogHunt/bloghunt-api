from django.conf import settings
from django.db.models import functions
from django.shortcuts import redirect, render
from rest_framework import viewsets, mixins, views, renderers, generics
from rest_framework.decorators import (detail_route, api_view,
    permission_classes, renderer_classes, authentication_classes)
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.models import Application

from bloghunt import filters
from users import models
from . import serializers


class UserSiteViewSet(viewsets.ModelViewSet):
    template_name = 'myfeeds.html'
    serializer_class = serializers.UserSiteSerializer
    filter_backends = (filters.IsOwnerFilterBackend,)
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.submitted_sites.order_by('-created_on')


class RecommendationViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    template_name = 'recommendations.html'
    serializer_class = serializers.RecommendationSerializer
    filter_backends = (filters.IsOwnerFilterBackend,)
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.Recommendation.objects.all()


class UserDetailView(generics.GenericAPIView):
    template_name = 'account.html'
    serializer_class = serializers.UserSerializer
    filter_backends = (filters.IsOwnerFilterBackend,)
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.PineUser.objects.all().order_by('-id')

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())[0]
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)


class GenerateAPIKeysView(generics.GenericAPIView):
    template_name = 'account.html'
    serializer_class = serializers.UserSerializer
    filter_backends = (filters.IsOwnerFilterBackend,)
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Application.objects.all().order_by('-user')

    def post(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        for app in queryset:
            app.delete()
        application = Application(user=request.user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
            name=request.user.username)
        application.save()
        return Response({}, 201)
