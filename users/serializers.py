from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import empty

import feeds.models, feeds.serializers
from . import models


class SimpleErrorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ['message']
        model = feeds.models.Error
        read_only_fields = ('message',)


class SimpleUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ['email', 'username', 'is_authenticated']
        model = get_user_model()
        read_only_fields = ('email', 'username')


class SimpleTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ('slug', 'name', 'url')
        model = feeds.models.Tag
        read_only_fields = ('slug', 'name', 'url')


class SimpleFeedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = feeds.models.Feed
        fields = ('feed_url', 'cloud')


class UserSiteSerializer(serializers.HyperlinkedModelSerializer):
    all_tags = serializers.SerializerMethodField()
    tags = SimpleTagSerializer(many=True)
    feeds = SimpleFeedSerializer(many=True, read_only=True)
    default_feed = SimpleFeedSerializer()
    error = SimpleErrorSerializer(read_only=True)

    class Meta:
        fields = (
            'id', 'url', 'feeds', 'title', 'description', 'link', 'tags', 'default_feed',
            'image', 'time_since_update', 'error', 'all_tags', 'created_on', 'types', 'type'
        )
        model = feeds.models.Site
        read_only_fields = (
            'id', 'url', 'feeds', 'title', 'description', 'link', 'types',
            'image', 'time_since_update', 'error', 'all_tags', 'created_on'
        )

    def get_all_tags(self, site):
        tags = feeds.models.Tag.objects.all()
        serializer = SimpleTagSerializer(tags, many=True, context=self.context)
        return serializer.data

    def update(self, site, validated_data):
        # Update default feeds.
        default_feed = self.initial_data.getlist('default_feed', None)
        if default_feed:
            site.default_feed = feeds.models.Feed.objects.get(feed_url=default_feed[0])

        # Update Tags
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

        # Now update as normal.
        return super(UserSiteSerializer, self).update(site, validated_data)


class RecommendationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ['site']
        model = models.Recommendation

    def create(self, validated_data, *args, **kwargs):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data, *args, **kwargs)


class UserDetailSerializer(serializers.HyperlinkedModelSerializer):
    user = SimpleUserSerializer()
    class Meta:
        fields = ('user', 'gravatar_url')
        model = models.UserDetails


class PremiumUserDetailSerializer(serializers.HyperlinkedModelSerializer):
    user = SimpleUserSerializer()
    class Meta:
        fields = ('user', 'api_client_id', 'api_client_secret', 'has_application', 'renewal_date')
        model = models.PremiumUserDetails


class UserSerializer(serializers.ModelSerializer):
    details = UserDetailSerializer()
    premium_details = PremiumUserDetailSerializer()

    class Meta:
        fields = ['email', 'username', 'is_authenticated', 'premium_details',
            'details', 'is_premium', 'total_recommendations', 'total_sites_submitted']
        model = models.PineUser
        read_only_fields = ('email', 'username')


