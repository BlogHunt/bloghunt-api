from django.db.models import functions
from rest_framework import viewsets, permissions
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from . import models, serializers


class Position(functions.Func):
    function = 'POSITION'
    arg_joiner = ' in '
    arity = 2

    def __init__(self, left, right, **extra):
        super().__init__(left, right, **extra)

    def as_sqlite(self, compiler, connection):
        preserve_arg_joiner = self.arg_joiner
        self.arg_joiner = ','
        sql, params = super().as_sql(compiler, connection, function='INSTR')
        self.arg_joiner = preserve_arg_joiner
        return sql, params


class FeedViewSet(viewsets.ModelViewSet):
    queryset = (
        models.Feed.objects
        # filter out feeds without data
        .filter(last_updated__isnull=False, title__isnull=False)
        # order by the rss_url without the schema
        .order_by(functions.Substr('rss_url', Position('rss_url', functions.Value('://')) + 3))
        .prefetch_related('tags')
    )
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
    permission_classes = (permissions.IsAdminUser,)
