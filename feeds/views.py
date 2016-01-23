from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from . import models, serializers


class FeedViewSet(viewsets.ModelViewSet):
    queryset = models.Feed.objects.filter(last_updated__isnull=False)
    serializer_class = serializers.FeedSerializer
    filter_fields = (
        'tags',
    )
    search_fields = (
        'title',
        'description',
        'rss_url',
    )

    @detail_route(methods=['get'])
    def preview(self, request, pk):
        feed_page = self.get_object().get_feedpage()
        return Response({
            'title': feed_page.title,
            'description': feed_page.description,
            'link': feed_page.link,
            'image': feed_page.image,
            'cloud': feed_page.cloud,
        })


class TagViewSet(viewsets.ModelViewSet):
    queryset = models.Tag.objects.order_by('slug')
    serializer_class = serializers.TagSerializer


class KeywordViewSet(viewsets.ModelViewSet):
    queryset = models.Keyword.objects.order_by('tag')
    serializer_class = serializers.KeywordSerializer
