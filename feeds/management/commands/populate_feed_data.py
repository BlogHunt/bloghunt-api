from datetime import timedelta

from django.core.management import base
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from ... import models


class Command(base.BaseCommand):
    help = 'Populate RSS feed information from the feeds.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all', action='store_true', dest='all_feeds', default=False,
            help='Process all feed objects.',
        )

    def handle(self, all_feeds, verbosity, *args, **kwargs):
        for feed in self.get_feeds_to_update(all_feeds):
            try:
                feedpage = feed.get_feedpage()
            except Exception as e:
                if verbosity > 1:
                    self.stderr.write('Unable to parse {}\n\t{}'.format(feed.rss_url, e))
                feed.last_updated = timezone.now()
                feed.save(update_fields=['last_updated'])
                continue

            feed.update_using_feedpage(feedpage)

            try:
                feed.save()
            except Exception:
                if verbosity > 0:
                    self.stderr.write('Error saving {} ({})'.format(feed.rss_url, feed.pk))

    @staticmethod
    def get_feeds_to_update(all_feeds):
        if all_feeds:
            return models.Feed.objects.all()
        return models.Feed.objects.exclude(last_updated__gt=timezone.now() - timedelta(days=7))
