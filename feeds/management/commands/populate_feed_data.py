from datetime import timedelta

from django.core.management import base
from django.utils import timezone

from ... import models


class Command(base.BaseCommand):
    help = 'Populate RSS feed information from the feeds.'

    def handle(self, *args, **kwargs):
        for feed in models.Feed.objects.exclude(last_updated__gt=timezone.now() - timedelta(days=7)):
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
                matches = models.Keyword.objects.filter(word=category.text.lower())
                for kw in matches:
                    try:
                        feed.tags.add(kw.tag)
                    except Exception:
                        pass

            feed.save(update_fields=['title', 'description', 'link', 'last_updated', 'image', 'cloud'])
