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

    def handle(self, all_feeds, *args, **kwargs):
        for feed in self.get_feeds_to_update(all_feeds):
            try:
                feedpage = feed.get_feedpage()
            except Exception as e:
                self.stderr.write('Unable to parse {}.\n\t{}'.format(feed.rss_url, e))
                continue
            feed.title = feedpage.title
            feed.description = feedpage.description
            feed.link = feedpage.link
            feed.image = feedpage.image
            feed.cloud = feedpage.cloud
            feed.last_updated = timezone.now()

            for category in feedpage.categories:
                matches = models.Keyword.objects.filter(word__iexact=category)
                for kw in matches:
                    try:
                        feed.tags.add(kw.tag)
                    except ObjectDoesNotExist as e:
                        pass
            feed.save(update_fields=['title', 'description', 'link', 'last_updated', 'image', 'cloud'])

    @staticmethod
    def get_feeds_to_update(all_feeds):
        if all_feeds:
            return models.Feed.objects.all()
        return models.Feed.objects.exclude(last_updated__gt=timezone.now() - timedelta(days=7))
