from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_related_models_for_new_user(sender, instance, created, **kwargs):
    """ Whenever a user is created, also create any related models. """
    if created:
        details = models.UserDetails(user=instance)
        details.save()
