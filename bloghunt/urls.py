"""bloghunt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView
from rest_framework import routers

import feeds.views, users.views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'feeds', feeds.views.FeedViewSet)
router.register(r'tags', feeds.views.TagViewSet)
# router.register(r'keywords', feeds.views.KeywordViewSet)

user_router = routers.DefaultRouter(trailing_slash=False)
user_router.register(r'feeds', users.views.UserFeedViewSet, base_name='feeds')

urlpatterns = [
    url(r'^$', feeds.views.HomeViewSet.as_view({ 'get': 'list'})),
    url(r'^feeds/new$', feeds.views.NewFeedView.as_view(),
        name='new-feed'),
    url(r'^about$', feeds.views.about_view),
    url(r'^documentation$', feeds.views.documentation_view),
    url(r'^users/', include(user_router.urls)),
    url(r'^', include(router.urls)),

    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
