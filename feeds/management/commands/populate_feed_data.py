from datetime import timedelta

from django.core.management import base
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from ... import models
from ... import pages

class Command(base.BaseCommand):
    help = 'Populate RSS feed information from the feeds.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all', action='store_true', dest='all_feeds', default=False,
            help='Process all feed objects.',
        )

    def handle(self, all_feeds, verbosity, *args, **kwargs):
        feeds = self.get_feeds_to_update(all_feeds)
        for i, feed in enumerate(feeds):
            if verbosity > 0:
                self.stdout.write('Updating [%s/%s]: %s' % (i+1, len(feeds), feed.feed_url))
            try:
                feedpage = pages.get_feedpage(feed.feed_url)
            except Exception as e:
                if verbosity > 1:
                    self.stderr.write('Unable to parse {}\n\t{}'.format(feed.feed_url, e))
                feed.last_updated = timezone.now()
                feed.save(update_fields=['last_updated'])
                continue

            feed.update_using_feedpage(feedpage)

            try:
                feed.save()
            except Exception:
                if verbosity > 0:
                    self.stderr.write('Error saving {} ({})'.format(feed.feed_url, feed.pk))

    @staticmethod
    def get_feeds_to_update(all_feeds):
        if all_feeds:
            return models.Feed.objects.all()
        return models.Feed.objects.exclude(last_updated__gt=timezone.now() - timedelta(hours=6))
