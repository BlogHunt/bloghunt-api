from django.db.models import functions, Count
from django.shortcuts import redirect
from django.core import validators
from django.core.exceptions import ValidationError
from rest_framework import viewsets, mixins, views, renderers
from rest_framework.decorators import (detail_route, api_view,
                                       permission_classes, renderer_classes)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from bloghunt.response import error_response
from . import models, serializers, tasks


class SiteViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    template_name = 'feeds.html'

    base_queryset = (
        models.Site.objects
        .filter(error=None)
        .annotate(recommendations_count=Count('recommendations'))
        .order_by('-recommendations_count')
        .prefetch_related('tags')
        .prefetch_related('feeds')
    )

    serializer_class = serializers.SiteSerializer
    filter_fields = (
        'tags',
    )
    search_fields = (
        'feeds__title',
        'feeds__description',
    )

    def get_queryset(self):
        type = self.request.GET.get('type', '')
        if not type:
            return self.base_queryset
        else:
            return self.base_queryset.filter(type=type)


    def list(self, request, *args, **kwargs):
        q = request.GET.get('search', '').strip()
        if q:
            return super().list(self, request, *args, **kwargs)
        else:
            return Response({
                'error': 'Missing or invalid search query parameter.'
            }, status=400)

    @detail_route(methods=['get'])
    def preview(self, request, pk):
        feed_page = self.get_object()._default_feed.get_feedpage()
        return Response({
            'title': feed_page.title,
            'description': feed_page.description,
            'link': feed_page.link,
            'image': feed_page.image,
            'cloud': feed_page.cloud,
        })


class NewFeedView(views.APIView):
    template_name = 'submit.html'
    permission_classes = (IsAuthenticated,)
    throttle_rates = {
        'user-write': '5/day'
    }

    def get(self, request, *args, **kwargs):
        return Response()

    def post(self, request, *args, **kwargs):
        url = request.POST['link'].strip()
        try:
            validators.URLValidator(schemes=['http', 'https'])(url)
        except ValidationError:
            return error_response('Please enter a valid url.', link=url)
        if not url:
            return error_response('Please enter a url.', link=url)
        if models.Site.objects.filter(link=url).exists():
            return error_response('Site already exists.', link=url)
        if models.Feed.objects.filter(feed_url=url).exists():
            return error_response('Site with feed already exists.', link=url)
        tasks.import_site_and_notify_user.delay(url, request.user.id)
        return Response({'success': True})


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
    serializer_class = serializers.TagSummarySerializer


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

@api_view()
@renderer_classes((renderers.TemplateHTMLRenderer,))
@permission_classes((AllowAny,))
def api_documentation_view(request):
    return Response({}, template_name='api_documentation.html')
