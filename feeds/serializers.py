from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from . import models
import users.models


class TagSerializer(serializers.HyperlinkedModelSerializer):
    feeds = serializers.SerializerMethodField()

    class Meta:
        fields = ['url', 'name', 'slug', 'feeds']
        model = models.Tag
        read_only_fields = ['feeds']

    def get_feeds(self, tag):
        queryset = models.Feed.objects.filter(tags=tag).order_by('-recommendations')[:4]
        serializer = SimpleFeedSerializer(queryset, many=True, context=self.context)
        return serializer.data


class SimpleTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ['url', 'name']
        model = models.Tag


class KeywordSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        fields = ['word', 'tag']
        model = models.Keyword
        read_only_fields = []


class FeedSerializer(serializers.HyperlinkedModelSerializer):
    tags = SimpleTagSerializer(many=True)
    recommendation = serializers.SerializerMethodField()

    class Meta:
        fields = [
            'url', 'rss_url', 'title', 'description', 'link', 'tags', 'cloud',
            'image', 'time_since_update', 'total_recommendations', 'recommendation'
        ]
        model = models.Feed
        read_only_fields = [
            'url', 'rss_url', 'title', 'description', 'link', 'cloud',
            'image', 'time_since_update', 'total_recommendations', 'recommendation'
        ]
        extra_kwargs = {
            'tags': {
                'template': 'fields/multi-select-input.html'
            }
        }

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        feed = models.Feed.objects.create(**validated_data)
        feed.tags = [Tag.objects.get(name=name) for name in tags]
        feed.save()
        return feed

    def get_recommendation(self, feed):
        user = self.context['request'].user
        try:
            return users.models.FeedRecommendation.objects.get(user=user, feed=feed)
        except (ObjectDoesNotExist, TypeError):
            return None


class SimpleFeedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = [
            'url', 'rss_url', 'title', 'link', 'image',
            'total_recommendations', 'description', 'time_since_update'
        ]
        model = models.Feed


class NewFeedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ['rss_url',]
        model = models.Feed
        extra_kwargs = {
            'rss_url': {
                'style': {
                    'placeholder': 'http://mysite.com(/feed.xml)',
                    'autofocus': True,
                    'hide_label': True,
                }
            }
        }
