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

import feeds.views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'feeds', feeds.views.FeedViewSet)
router.register(r'tags', feeds.views.TagViewSet)
router.register(r'keywords', feeds.views.KeywordViewSet)

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/feeds')),
    url(r'^', include(router.urls)),

    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
