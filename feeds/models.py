import re
import uuid

from lxml import etree
from django.db import models
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

    class Meta:
        unique_together = (("word", "tag"),)


class Feed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rss_url = models.URLField('RSS URL', unique=True)
    title = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    last_updated = models.DateTimeField(editable=False, null=True)
    tags = models.ManyToManyField(Tag)
    image = models.URLField('Image URL', blank=True, null=True)
    cloud = models.URLField('Cloud URL', blank=True, null=True)
    cached_content = models.TextField()

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
