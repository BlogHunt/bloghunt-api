from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from . import models
import users.models


class TagSerializer(serializers.HyperlinkedModelSerializer):
    PAGE_SIZE = 10
    sites = serializers.SerializerMethodField()

    class Meta:
        fields = ['url', 'name', 'sites']
        model = models.Tag
        read_only_fields = ['sites']

    def get_sites(self, tag):
        queryset = models.Site.objects.filter(tags=tag).order_by('-recommendations')[:self.PAGE_SIZE]
        serializer = SiteSerializer(queryset, many=True, context=self.context)
        return serializer.data


class TagSummarySerializer(TagSerializer):
    PAGE_SIZE = 4


class SimpleTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ['url', 'name']
        model = models.Tag


class KeywordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ['word', 'tag']
        model = models.Keyword
        read_only_fields = []


class SimpleSiteRecommendationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = users.models.Recommendation
        fields = ('url', )
        extra_kwargs = {
            'url': {'view_name': 'users:recommendation-detail'},
        }


class SimpleFeedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Feed
        fields = ('feed_url', 'cloud', 'type')

    def to_representation(self, feed):
        if feed.type == models.Feed.JSONFeed:
            cloud = self.fields.pop('cloud', None)

        data = super(SimpleFeedSerializer, self).to_representation(feed)

        if feed.type == models.Feed.JSONFeed:
            self.fields['cloud'] = cloud
        return data


class SiteSerializer(serializers.HyperlinkedModelSerializer):
    tags = SimpleTagSerializer(many=True)
    feeds = SimpleFeedSerializer(many=True)
    recommendation = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'url', 'title', 'description', 'link', 'tags', 'feeds', 'type',
            'image', 'time_since_update', 'total_recommendations', 'recommendation',
        )
        model = models.Site
        read_only_fields = ('__all__',)

    def get_recommendation(self, site):
        user = self.context['request'].user
        try:
            obj = users.models.Recommendation.objects.get(user=user, site=site)
        except (ObjectDoesNotExist, TypeError):
            return None
        return SimpleSiteRecommendationSerializer(obj, context={
            'request': self.context['request']
        }).data


# API Serializers


class SimpleTagAPISerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ['url', 'name']
        model = models.Tag
        extra_kwargs = {
            'url': {'view_name': 'api:tag-detail'},
        }


class TagAPISerializer(SimpleTagSerializer):
    PAGE_SIZE = 10
    sites = serializers.SerializerMethodField()

    class Meta:
        fields = ['url', 'name', 'sites']
        model = models.Tag
        read_only_fields = ['sites']
        extra_kwargs = {
            'url': {'view_name': 'api:site-detail'},
        }

    def get_sites(self, tag):
        queryset = models.Site.objects.filter(tags=tag).order_by('-recommendations')[:self.PAGE_SIZE]
        serializer = SiteAPISerializer(queryset, many=True, context=self.context)
        return serializer.data


class SiteAPISerializer(serializers.HyperlinkedModelSerializer):
    tags = SimpleTagAPISerializer(many=True)
    feeds = SimpleFeedSerializer(many=True)

    class Meta:
        model = models.Site
        fields = (
            'url', 'title', 'description', 'link', 'type', 'image',
            'feeds', 'tags', 'total_recommendations',
        )
        read_only_fields = ('__all__',)
        extra_kwargs = {
            'url': {'view_name': 'api:site-detail'},
        }

