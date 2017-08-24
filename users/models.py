import uuid

from django.db import models
from django.conf import settings

import feeds.models


class Recommendation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='recommendations',
        on_delete=models.CASCADE)
    site = models.ForeignKey(feeds.models.Site, related_name='recommendations',
        on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'site')
