import requests
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from . import models, serializers


class FeedViewSet(viewsets.ModelViewSet):
    queryset = models.Feed.objects.all().order_by('rss_url')
    serializer_class = serializers.FeedSerializer

    @detail_route(methods=['get'])
    def preview(self, request, pk):
        feed_page = self.get_object().get_feedpage()
        return Response({
            'title': feed_page.title,
            'description': feed_page.description,
            'link': feed_page.link,
        })
