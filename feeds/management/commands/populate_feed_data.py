from django.core.management import base

from ... import models


class Command(base.BaseCommand):
    help = 'Populate RSS feed information from the feeds.'

    def handle(self, *args, **kwargs):
        for feed in models.Feed.objects.all():
            try:
                feedpage = feed.get_feedpage()
            except Exception:
                self.stderr.write('Unable to parse {}'.format(feed.rss_url))
                continue
            feed.title = feedpage.title
            feed.description = feedpage.description
            feed.link = feedpage.link
            feed.save(update_fields=['title', 'description', 'link'])
