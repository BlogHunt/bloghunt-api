from rest_framework import serializers

from . import models


class FeedSerializer(serializers.HyperlinkedModelSerializer):
    tags = serializers.HyperlinkedRelatedField('tag-detail',
        queryset=models.Tag.objects.all(), many=True)

    class Meta:
        fields = ['url', 'rss_url', 'title', 'description', 'link', 'tags',
            'cloud', 'image']
        model = models.Feed
        read_only_fields = ['title', 'description', 'link']


class TagSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        fields = ['name', 'slug', 'url']
        model = models.Tag
        read_only_fields = []


class KeywordSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        fields = ['word', 'tag']
        model = models.Keyword
        read_only_fields = []
