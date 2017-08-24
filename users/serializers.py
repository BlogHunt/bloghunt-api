from rest_framework import serializers
from rest_framework.fields import empty

import feeds.models, feeds.serializers
from . import models


class SimpleErrorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ['message']
        model = feeds.models.Error
        read_only_fields = ('message',)


class SimpleTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ('slug', 'name', 'url')
        model = feeds.models.Tag
        read_only_fields = ('slug', 'name', 'url')


class UserSiteSerializer(serializers.HyperlinkedModelSerializer):
    all_tags = serializers.SerializerMethodField()
    tags = SimpleTagSerializer(many=True)
    feeds = feeds.serializers.SimpleFeedSerializer(many=True, read_only=True)
    error = SimpleErrorSerializer(read_only=True)

    class Meta:
        fields = (
            'id', 'url', 'feeds', 'title', 'description', 'link', 'tags',
            'image', 'time_since_update', 'error', 'all_tags', 'created_on'
        )
        model = feeds.models.Site
        read_only_fields = (
            'id', 'url', 'feeds', 'title', 'description', 'link',
            'image', 'time_since_update', 'error', 'all_tags', 'created_on'
        )

    def get_all_tags(self, site):
        tags = feeds.models.Tag.objects.all()
        serializer = SimpleTagSerializer(tags, many=True, context=self.context)
        return serializer.data

    def update(self, site, validated_data):
        tag_slugs = self.initial_data.getlist('tags', None)
        tags = validated_data.pop('tags')
        if tag_slugs is not None:
            # Be forgiving of select posted nested results.
            tags = [{'slug': slug} for slug in tag_slugs if isinstance(slug, str)]

        if tags is not None:
            site.tags = [
                feeds.models.Tag.objects.get(slug=tag['slug'])
                for tag in tags
            ][:2]
        return super().update(site, validated_data)


class RecommendationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ['site']
        model = models.Recommendation

    def create(self, validated_data, *args, **kwargs):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data, *args, **kwargs)
