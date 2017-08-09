from rest_framework import serializers

import feeds.models, feeds.serializers
from . import models


class UserFeedSerializer(serializers.HyperlinkedModelSerializer):
    tags = feeds.serializers.SimpleTagSerializer(many=True)

    class Meta:
        fields = ['url', 'rss_url', 'title', 'description', 'link', 'tags', 'cloud', 'image', 'time_since_update']
        model = feeds.models.Feed
        read_only_fields = ['__all__']
