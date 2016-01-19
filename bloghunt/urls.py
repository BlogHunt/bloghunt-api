"""bloghunt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

import feeds.views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'feeds', feeds.views.FeedViewSet)
router.register(r'tags', feeds.views.TagViewSet)
router.register(r'keywords', feeds.views.KeywordViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^', include(router.urls)),
]
