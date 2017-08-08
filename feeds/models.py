import re, uuid

from lxml import etree
from django.db import models
from django.utils import timezone
from django.conf import settings
import requests

from . import pages


class Tag(models.Model):
    slug = models.SlugField(primary_key=True)
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name


class Keyword(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word = models.CharField(max_length=250, blank=True, null=True, unique=False)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return "%s -> %s" % (self.word, self.tag.name)

    class Meta:
        unique_together = (("word", "tag"),)


class Feed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rss_url = models.URLField('RSS URL', unique=True)
    title = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    last_updated = models.DateTimeField(editable=False, null=True)
    tags = models.ManyToManyField(Tag, related_name='feeds')
    image = models.URLField('Image URL', blank=True, null=True)
    cloud = models.URLField('Cloud URL', blank=True, null=True)
    cached_content = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submitted_feeds',
        on_delete=models.CASCADE, blank=True, null=True)

    def get_feedpage(self, use_cached=False):
        if not use_cached:
            response = requests.get(self.rss_url, headers={'Accept': (
                'application/rss+xml, application/rdf+xml, application/atom+xml, application/xml, text/xml'
            )})
            response.raise_for_status()
            self.cached_content = response.text.encode()

        tree = etree.fromstring(self.cached_content, parser=etree.XMLParser(recover=True))
        channel = tree.find('{*}channel')
        channel = channel if channel is not None else tree
        nsmatch = re.match('\{.*\}', channel.tag)
        defaultns = nsmatch.group(0) if nsmatch else ''
        return pages.FeedPage(channel, url=self.rss_url, defaultns=defaultns)

    def __str__(self):
        return self.rss_url

    @property
    def time_since_update(self):
        if self.last_updated is None:
            return None
        now = timezone.now()
        delta = now - self.last_updated

        if delta.days == 1:
            return 'yesterday'
        elif delta.days > 1:
            return '%s %s ago' % (delta.days, 'days')
        else:
            return '%s %s ago' % (delta.hours, 'hours')


