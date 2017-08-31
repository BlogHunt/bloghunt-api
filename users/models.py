import uuid, hashlib
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from oauth2_provider.models import Application

import feeds.models


class Recommendation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='recommendations',
        on_delete=models.CASCADE)
    site = models.ForeignKey(feeds.models.Site, related_name='recommendations',
        on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'site')


class UserDetails(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='details')

    GRAVATAR_URL_FORMAT = 'https://www.gravatar.com/avatar/{hash}?d=mm'

    @property
    def gravatar_url(self):
        hash = hashlib.md5(self.user.email.encode())
        return self.GRAVATAR_URL_FORMAT.format(hash=hash.hexdigest())

    @property
    def total_recommendations(self):
        self.user.recommendations.count()

    @property
    def total_sites_submitted(self):
        return self.user.submitted_sites.count()


class PremiumUserDetails(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='premium_details')
    date_joined = models.DateTimeField(default=timezone.now)
    last_charge = models.DateTimeField(default=None, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=100)

    @property
    def renewal_date(self):
        if self.last_charge is None:
            return None
        return self.last_charge + relativedelta(years=1)

    @property
    def api_client_id(self):
        return self._shared_application.client_id

    @property
    def api_client_secret(self):
        return self._shared_application.client_secret

    @property
    def has_application(self):
        return self._shared_application is not None

    @property
    def _shared_application(self):
        try:
            return Application.objects.get(user=self.user)
        except ObjectDoesNotExist:
            return None


class PineUser(User):
    class Meta:
        proxy = True

    @property
    def is_premium(self):
        return self.premium_details is not None

    @staticmethod
    def get_users_to_renew(self):
        year_ago = timezone.now() - timedelta(years=1)
        return PineUser.objects.filter(premium_details__last_charge__lte=year_ago)
