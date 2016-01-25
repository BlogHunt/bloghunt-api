from urllib import parse

from django.core.management import base
from django.db.utils import IntegrityError
from lxml import etree, html
import requests
from requests.exceptions import InvalidSchema, InvalidURL

from ... import models


COMMON_FEED_NAMES = [
    'rss.xml',
    'feed.xml',
    'atom.xml',
    'index.xml',
    'feed.rss',
    'index.rss',
    'rss2.0.xml',
    'articles.rss',

    # least prefered
    'feed',
    'rss',
]


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
        index_resp = requests.get(site_url, headers={'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
        )})
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
                etree.fromstring(index_resp.text.encode()).xpath(b'.//*[starts-with(text(), "http://")] | ' +
                                                                 b'.//*[starts-with(text(), "https://")]')
            ]
        for article_url in set(index_urls):
            if '://' not in article_url:
                article_url = parse.urljoin(site_url, article_url)
            if article_url in checked_urls:
                continue
            checked_urls.add(article_url)
            if (
                'https://news.ycombinator.com' in article_url or
                'https://www.google.com' in article_url or
                'https://hn.algolia.com' in article_url or
                '://' not in article_url
            ):
                continue
            feeds = self.feeds_for_url(article_url, verbosity=verbosity)
            if not feeds and verbosity > 1:
                self.stderr.write('No feed for {}'.format(article_url))
            for feed_url in feeds:
                try:
                    models.Feed.objects.create(rss_url=feed_url)
                except IntegrityError:
                    pass

    def feeds_for_url(self, article_url, verbosity=1):
        feed_urls = []
        if '://' not in article_url:
            raise Exception('Expecting fully qualified URL')
        parent_url = parse.urljoin(article_url, '.')
        if parent_url == article_url:
            parent_url = parse.urljoin(article_url, '..')
        for url in [article_url, parent_url] if article_url != parent_url else [article_url]:
            try:
                article_resp = requests.get(url)
            except (InvalidSchema, InvalidURL):
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
                feeds = article_tree.xpath(b'.//head/link[@type="application/rss+xml"] | ' +
                                           b'.//head/link[@type="application/atom+xml"]')
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
                feed_urls.append(href)
                if verbosity > 0:
                    self.stdout.write('{} {}'.format(feed.get('title'), href))

            if feeds:
                return feeds
        else:
            possible_feed_root = parent_url
            while True:
                for feed_name in COMMON_FEED_NAMES:
                    try:
                        resp = requests.get(
                            parse.urljoin(possible_feed_root, feed_name), allow_redirects=False)
                    except Exception:
                        continue
                    try:
                        root_tag = etree.fromstring(
                            resp.text.encode(), parser=etree.XMLParser(recover=True)).tag
                    except Exception:
                        continue
                    if resp.status_code < 300 and root_tag.endswith('rss') or root_tag.endswith('rdf'):
                        return [resp.url]
                parent = parse.urljoin(possible_feed_root, '..')
                if parent == possible_feed_root:
                    break
                possible_feed_root = parent
        return []
