from urllib import parse

from django.core.management import base
from django.db.utils import IntegrityError
from lxml import etree, html
import requests
from requests.exceptions import InvalidSchema, InvalidURL

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

    def handle(self, site_url, verbosity, *args, **kwargs):
        checked_urls = set()
        index_resp = requests.get(site_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'})
        if response_is_html(index_resp):
            index_urls = [
                e.attrib['href']
                for e in
                html.fromstring(index_resp.text.encode()).findall('.//*[@href]')
                if 'href' in e.attrib
            ]
        else:
            index_urls = [
                e.text
                for e in
                etree.fromstring(index_resp.text.encode()).xpath(b'.//*[starts-with(text(), "http://")] | .//*[starts-with(text(), "https://")]')
            ]
        for article_url in set(index_urls):
            parent_url = parse.urljoin(article_url, '.')
            for url in [article_url, parent_url]:
                if '://' not in url:
                    url = parse.urljoin(site_url, url)
                if url in checked_urls:
                    continue
                checked_urls.add(url)
                try:
                    article_resp = requests.get(url)
                except InvalidSchema:
                    continue
                except InvalidURL:
                    if verbosity > 0:
                        self.stderr.write('URL appears invalid {}'.format(url))
                    continue
                except Exception:
                    if verbosity > 0:
                        self.stderr.write('Error getting {}'.format(url))
                    continue
                if response_is_html(article_resp):
                    try:
                        article_tree = html.fromstring(article_resp.text)
                    except Exception:
                        if verbosity > 0:
                            self.stderr.write('Unable to parse HTML {}'.format(url))
                        continue
                    feeds = article_tree.findall('.//head/link[@type="application/rss+xml"]')
                else:
                    try:
                        feed_tree = etree.fromstring(article_resp.text)
                    except Exception:
                        if verbosity > 0:
                            self.stderr.write('Unable to parse XML {}'.format(url))
                        continue
                    if feed_tree.tag.endswith('rss') or feed_tree.tag.endswith('rdf'):
                        feeds = [url]
                    else:
                        if verbosity > 0:
                            self.stderr.write('Non-feed xml document {}'.format(url))
                for feed in feeds:
                    href = feed.attrib['href']
                    if '://' not in href:
                        href = parse.urljoin(url, href)
                    try:
                        models.Feed.objects.create(rss_url=href)
                    except IntegrityError:
                        pass
                    if verbosity > 0:
                        self.stdout.write('{} {}'.format(feed.get('title'), href))

                if feeds:
                    break
            else:
                if verbosity > 1:
                    self.stdout.write('No feed for {}'.format(article_url))
