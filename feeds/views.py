from django.db.models import functions
from django.shortcuts import redirect
from rest_framework import viewsets, mixins, views, renderers
from rest_framework.decorators import (detail_route, api_view,
    permission_classes, renderer_classes, authentication_classes)
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from bloghunt import filters
from . import models, serializers, forms


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


class FeedViewSet(viewsets.ReadOnlyModelViewSet):
    template_name = 'feeds.html'

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

    def list(self, request, *args, **kwargs):
        if request.GET.get('search', False):
            return super().list(self, request, *args, **kwargs)
        else:
            return Response({
                'error': 'Missing or invalid search query parameter.'
            }, status=400)

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



class NewFeedView(views.APIView):
    template_name = 'submit.html'

    def get(self, request, *args, **kwargs):
        return Response({})


class ConfirmFeedView(views.APIView):
    template_name = 'confirm.html'
    throttle_scope = 'upload'

    def post(self, request, *args, **kwargs):
        new_feed_form = forms.NewFeedForm(request.POST)
        if not new_feed_form.is_valid():
            return redirect('new-feed', error='Invalid url')

        # TODO Validate feed and allow tags to be added.

        return Response({})


class DoneFeedView(views.APIView):
    template_name = 'done.html'
    throttle_scope = 'upload'

    def post(self, request, *args, **kwargs):

        # TODO Add feed to db.

        return Response({})


class TagViewSet(viewsets.ModelViewSet):
    template_name = 'tags.html'
    queryset = models.Tag.objects.order_by('slug')
    serializer_class = serializers.TagSerializer


class KeywordViewSet(viewsets.ModelViewSet):
    queryset = models.Keyword.objects.order_by('tag')
    serializer_class = serializers.KeywordSerializer


class HomeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    template_name = 'home.html'
    queryset = models.Tag.objects.order_by('slug')
    serializer_class = serializers.TagSerializer


@api_view()
@renderer_classes((renderers.TemplateHTMLRenderer,))
@permission_classes((AllowAny,))
def about_view(request):
    return Response({}, template_name='about.html')


@api_view()
@renderer_classes((renderers.TemplateHTMLRenderer,))
@permission_classes((AllowAny,))
def documentation_view(request):
    return Response({}, template_name='documentation.html')
