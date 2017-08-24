""" Background tasks for parsing and importing sites/feeds.

author: Brian Schrader
"""

from celery import shared_task
import requests
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from . import models, parsers


@shared_task
def import_site_and_notify_user(url, user_id, debug=False):
    """ Given a url and it's owner, attempt to pull down the feed/site
    and parse it. Once done, email the owner of the result.
    """
    workflow = (import_site_from_url.s(url, user_id, debug) | notify_user.s(url, user_id, debug))
    workflow.delay()


@shared_task
def import_site_from_url(url, user_id, debug=False):
    """ Given an url to import attempt to import the site.

    :returns: The site instance that was imported (along with possible errors)
    or None if such a site already exists.
    """
    user = get_user_model().objects.get(id=user_id)
    try:
        site = models.Site.get_site(url, owner=user, verbose=debug)
    except (requests.exceptions.HTTPError):
        error = models.Error(identifier=models.Error.HTTPError,
                             message='Feed at URL not found.')
        error.save()
        site = models.Site(link=url, owner=user, error=error)
    except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema):
        error = models.Error(identifier=models.Error.MissingOrInvalidSchemaError,
                             message='Invalid url.')
        error.save()
        site = models.Site(link=url, owner=user, error=error)
    except (requests.exceptions.ConnectionError):
        error = models.Error(identifier=models.Error.ConnectionError,
                             message='Could not fetch feed from site.')
        error.save()
        site = models.Site(link=url, owner=user, error=error)
    except (parsers.SiteHasNoFeedsError):
        error = models.Error(identifier=models.Error.SiteHasNoFeedsError,
                             message='No feeds found for this site.')
        error.save()
        site = models.Site(link=url, owner=user, error=error)

    site.save()
    try:
        site.save()
    except IntegrityError:
        site.delete()
        return None
    return site.id.hex


@shared_task
def notify_user(site, url, user_id, debug=False):
    """ Notify the user via email as to whether or not their import succeeded. """
    success = site is not None
    # TODO
    return success
