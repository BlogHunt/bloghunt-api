import itertools
import re
from urllib import parse
import uuid

from lxml import etree
from django.db import models
import requests


class FeedPage(object):

    def __init__(self, tree, url='', defaultns=''):
        self.tree = tree
        self.defaultns = defaultns
        self.url = url

    @property
    def title(self):
        title_elem = self.tree.find('{}title'.format(self.defaultns))
        return title_elem.text if title_elem is not None else None

    @property
    def description(self):
        description_elem = self.tree.find('{}description'.format(self.defaultns))
        return description_elem.text if description_elem is not None else None

    @property
    def link(self):
        link_elems = self.tree.findall('{}link'.format(self.defaultns))
        for link_elem in link_elems:
            if link_elem.attrib.get('rel') == 'self':
                continue
            link = link_elem.text or link_elem.attrib.get('href')
            if self.url and link:
                link = parse.urljoin(self.url, link)
            return link

    @property
    def categories(self):
        return {
            c.text for c in itertools.chain(*(
                i.findall('{}category'.format(self.defaultns))
                for i in self.tree.findall('{}item'.format(self.defaultns)) + [self.tree]
            )) if c is not None and c.text
        }

    @property
    def image(self):
        image_elems = self.tree.findall('{}image/url'.format(self.defaultns))
        for image_elem in image_elems:
            if image_elem.attrib.get('rel') == 'self':
                continue
            image = image_elem.text or image_elem.attrib.get('href')
            return image

    @property
    def cloud(self):
        cloud_elems = self.tree.findall('{}cloud'.format(self.defaultns))
        for cloud_elem in cloud_elems:
            if cloud_elem.attrib.get('rel') == 'self':
                continue
            cloud = cloud_elem.text or cloud_elem.attrib.get('href')
            return cloud


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

    def get_feedpage(self):
        response = requests.get(self.rss_url)
        response.raise_for_status()
        tree = etree.fromstring(response.text.encode())
        channel = tree.find('{*}channel')
        channel = channel if channel is not None else tree
        nsmatch = re.match('\{.*\}', channel.tag)
        defaultns = nsmatch.group(0) if nsmatch else ''
        return FeedPage(channel, url=self.rss_url, defaultns=defaultns)

    def __str__(self):
        return self.rss_url
