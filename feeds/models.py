import re
from urllib import parse
import uuid

from defusedxml import cElementTree as etree
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


class Feed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rss_url = models.URLField(unique=True)
    title = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    def get_feedpage(self):
        response = requests.get(self.rss_url)
        response.raise_for_status()
        tree = etree.fromstring(response.text)
        channel = tree.find('channel')
        channel = channel if channel is not None else tree
        nsmatch = re.match('\{.*\}', channel.tag)
        return FeedPage(channel, url=self.rss_url, defaultns=nsmatch.group(0) if nsmatch else '')
