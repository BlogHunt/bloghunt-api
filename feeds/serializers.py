from rest_framework import serializers

from . import models


class FeedSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        fields = ['url', 'rss_url', 'title', 'description', 'link']
        model = models.Feed
        read_only_fields = ['title', 'description', 'link']
