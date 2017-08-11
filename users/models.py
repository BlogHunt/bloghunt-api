import uuid

from django.db import models
from django.conf import settings

import feeds.models


class FeedRecommendation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='recommendations',
        on_delete=models.CASCADE)
    feed = models.ForeignKey(feeds.models.Feed, related_name='recommendations',
        on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'feed')
