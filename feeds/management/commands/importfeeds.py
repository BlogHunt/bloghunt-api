from datetime import timedelta

from django.core.management import base
from django.core import validators
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ... import models
from feeds import tasks
import users.models

class Command(base.BaseCommand):
    help = 'Given a set of seed URLs, attempt to import the feeds..'

    def add_arguments(self, parser):
        parser.add_argument(
            'input', help='File containing newline seperated list of feeds.',
        )
        parser.add_argument(
            'username', help='The username to attribute the feeds to.',
        )
        parser.add_argument(
            '--delay', action='store_true', default=False,
            help='Process asyncronously',
        )

    def handle(self, input, username, delay, verbosity, *args, **kwargs):
        user = users.models.User.objects.get(username=username)
        for url in self.get_urls(input):
            try:
                validators.URLValidator(schemes=['http', 'https', 'feed'])(url)
            except ValidationError:
                if verbosity:
                    print('Please enter a valid url.\n%s' % url)
                continue
            if not url:
                if verbosity:
                    print('Please enter a url.\n%s' % url)
                continue
            if models.Site.objects.filter(link=url).exists():
                if verbosity:
                    print('Site already exists.\n%s' % url)
                continue
            if models.Feed.objects.filter(feed_url=url).exists():
                if verbosity:
                    print('Site with feed already exists.\n%s' % url)
                continue

            if verbosity:
                print('Importing %s' % url)
            if delay:
                tasks.import_site_from_url.delay(url, user.id, debug=verbosity)
            else:
                tasks.import_site_from_url(url, user.id, debug=verbosity)

    def get_urls(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                yield line.strip()
