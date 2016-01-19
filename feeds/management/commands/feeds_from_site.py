from urllib import parse

from django.core.management import base
from django.db.utils import IntegrityError
from lxml import etree, html
import requests
from requests.exceptions import InvalidSchema

from ... import models


def response_is_html(response):
    if 'html' in response.headers.get('Content-Type', ''):
        return True
    if response.text.strip().startswith('<!'):
        return True
    return False


class Command(base.BaseCommand):
    help = 'Add RSS feeds for urls from a page.'

    def add_arguments(self, parser):
        parser.add_argument('site_url')

    def handle(self, site_url, *args, **kwargs):
        index_resp = requests.get(site_url)
        if response_is_html(index_resp):
            index_urls = [
                e.attrib['href']
                for e in
                html.fromstring(index_resp.text).findall('.//*[@href]')
                if 'href' in e.attrib
            ]
        else:
            index_urls = [
                e.text
                for e in
                etree.fromstring(index_resp.text).xpath('.//*[starts-with(text(), "http://")] | .//*[starts-with(text(), "https://")]')
            ]
        for article_url in set(index_urls):
            parent_url = parse.urljoin(article_url, '.')
            for url in [article_url, parent_url]:
                if '://' not in url:
                    url = parse.urljoin(site_url, url)
                try:
                    article_resp = requests.get(url)
                except InvalidSchema:
                    continue
                if response_is_html(article_resp):
                    try:
                        article_tree = html.fromstring(article_resp.text)
                    except Exception:
                        self.stderr.write('Unable to parse HTML {}'.format(url))
                        continue
                    feeds = article_tree.findall('.//head/link[@type="application/rss+xml"]')
                else:
                    try:
                        feed_tree = etree.fromstring(article_resp.text)
                    except Exception:
                        self.stderr.write('Unable to parse XML {}'.format(url))
                        continue
                    if feed_tree.tag.endswith('rss'):
                        feeds = [url]
                    else:
                        self.stderr.write('Non-feed xml document {}'.format(url))
                for feed in feeds:
                    href = feed.attrib['href']
                    if '://' not in href:
                        href = parse.urljoin(url, href)
                    try:
                        models.Feed.objects.create(rss_url=href)
                    except IntegrityError:
                        pass
                    print(feed.get('title'), href)

                if feeds:
                    break
            else:
                self.stdout.write('No feed for {}'.format(article_url))
