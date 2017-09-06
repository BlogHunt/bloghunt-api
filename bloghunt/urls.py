"""bloghunt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
"""
from django.conf import settings
from django.views.generic.base import RedirectView
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework import routers

import feeds.views
import users.views

# Needed imports
from feeds import tasks
from users import signals


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'sites', feeds.views.SiteViewSet)
router.register(r'tags', feeds.views.TagViewSet)
# router.register(r'keywords', feeds.views.KeywordViewSet)

user_router = routers.DefaultRouter(trailing_slash=False)
user_router.register(r'sites', users.views.UserSiteViewSet, base_name='sites')
user_router.register(r'recommendations', users.views.RecommendationViewSet)

urlpatterns = [
    url(r'^$', feeds.views.HomeViewSet.as_view({'get': 'list'})),
    url(r'^sites/new$', feeds.views.NewFeedView.as_view(),
        name='new-site'),
    url(r'^about$', feeds.views.about_view),
    url(r'^accounts/profile/$', RedirectView.as_view(url='/accounts/profile')),
    url(r'^accounts/profile$', users.views.UserDetailView.as_view()),
    url(r'^accounts/generate_api_keys$', users.views.GenerateAPIKeysView.as_view()),
    url(r'^documentation$', feeds.views.documentation_view),
    url(r'^api_documentation$', feeds.views.api_documentation_view),
    url(r'^users/', include(user_router.urls)),
    url(r'^', include(router.urls)),

    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
#     url(r"^payments/", include("pinax.stripe.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
