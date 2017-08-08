from rest_framework import serializers

from . import models


class TagSerializer(serializers.HyperlinkedModelSerializer):
    feeds = serializers.SerializerMethodField()

    class Meta:
        fields = ['url', 'name', 'slug', 'feeds']
        model = models.Tag
        read_only_fields = ['feeds']

    def get_feeds(self, tag):
        queryset = models.Feed.objects.filter(tags=tag)[:4]
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

    class Meta:
        fields = ['url', 'rss_url', 'title', 'description', 'link', 'tags', 'cloud', 'image', 'time_since_update']
        model = models.Feed
        read_only_fields = ['title', 'description', 'link', 'time_since_update']


class SimpleFeedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ['url', 'rss_url', 'title', 'link', 'image']
        model = models.Feed


