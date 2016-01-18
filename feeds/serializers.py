from rest_framework import serializers

from . import models


class FeedSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Feed
