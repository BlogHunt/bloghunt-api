from datetime import timedelta
import os
import unittest
from unittest import mock

from django import test as djangotest
# from django.contrib import auth
# from django.core.urlresolvers import reverse
from django.utils import timezone
# from rest_framework import status, test as resttest
import requests
import lxml

from . import models, pages, parsers
from .management.commands import populate_feed_data

MODULE_PATH = os.path.dirname(__file__)
FEED_FIXTURE_PATH = os.path.abspath(os.path.join(MODULE_PATH, 'fixtures', 'feeds'))
SITE_FIXTURE_PATH = os.path.abspath(os.path.join(MODULE_PATH, 'fixtures', 'sites'))


class TestSitePage(djangotest.TestCase):
    def check_site(self, filename, data):
        mock_response = requests.Response()
        mock_response.status_code = 200
        with open(os.sep.join((SITE_FIXTURE_PATH, filename))) as site_html_file:
            mock_response._content = site_html_file.read().encode()
        with mock.patch('requests.get', return_value=mock_response):
            sitepage = pages.get_sitepage(filename)
        found_feeds = [url for url in sitepage.possible_feeds]
        for url in found_feeds:
            self.assertIn(url, data['possible_feeds'])
        self.assertEqual(len(data['possible_feeds']), len(found_feeds))

    def test_scripting_com(self):
        self.check_site('scripting.com.html', {
            'possible_feeds': [
                'http://scripting.com/rss.xml',
            ],
        })

    def test_brianschrader_com(self):
        self.check_site('brianschrader.com.html', {
            'possible_feeds': [
                '/rss.xml',
                '/feed.json',
            ],
        })

    def test_marco_org(self):
        self.check_site('marco.org.html', {
            'possible_feeds': [
                'http://marco.org/rss',
            ],
        })


class TestFeedPage(unittest.TestCase):

    def check_feed(self, filename, data):
        mock_response = requests.Response()
        mock_response.status_code = 200
        with open(os.sep.join((FEED_FIXTURE_PATH, filename))) as feed_xml_file:
            mock_response._content = feed_xml_file.read().encode()
        with mock.patch('requests.get', return_value=mock_response):
            feedpage = pages.get_feedpage(filename)
        self.assertEqual(
            {tag: getattr(feedpage, tag) for tag in data.keys()},
            data,
        )

    def test_rss091(self):
        self.check_feed('rss091.xml', {
            'title': 'Scripting News',
            'description': 'News and commentary from the cross-platform scripting community.',
            'link': 'http://www.scripting.com/',
        })

    def test_rss10(self):
        self.check_feed('rss10.xml', {
            'title': 'Meerkat',
            'description': 'Meerkat: An Open Wire Service',
            'link': 'http://meerkat.oreillynet.com',
        })

    def test_rss20(self):
        self.check_feed('rss20.xml', {
            'title': 'Scripting News',
            'description': 'A weblog about scripting and stuff like that.',
            'link': 'http://www.scripting.com/',
            'categories': {'1765', 'conferences'},
        })

    def test_atom(self):
        self.check_feed('atom.xml', {
            'title': 'Example Feed',
            'description': None,
            'link': 'http://example.org/',
        })

    def test_atom(self):
        self.check_feed('feed.json', {
            'title': 'JSON Feed',
            'description': 'JSON Feed is a pragmatic syndication format for blogs, microblogs, and other time-based content.',
            'link': 'https://jsonfeed.org/',
        })


# class TestApiCreateFeed(resttest.APITestCase):
#
#     def setUp(self):
#         self.user = auth.get_user_model().objects.create_user(
#             'tester', password='password', is_superuser=True)
#
#     def test_create_new_feed(self):
#         mock_feed_url = 'http://example.com/feed.xml'
#         self.client.force_authenticate(self.user)
#         data = {'feed_url': mock_feed_url, 'tags': []}
#         response = self.client.post(reverse('site-list'), data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
#         self.assertEqual(list(models.Feed.objects.values_list('feed_url', flat=True)), [mock_feed_url])


class TestPopulateFeedData(djangotest.TestCase):

    def setUp(self):
        self.site = models.Site(link='http://example.com/')
        self.new_feed, self.update_feed, self.recent_feed = models.Feed.objects.bulk_create([
            models.Feed(feed_url='http://example.com/1',
                        last_updated=None, site=self.site),
            models.Feed(feed_url='http://example.com/2',
                        last_updated=timezone.now() - timedelta(weeks=10), site=self.site),
            models.Feed(feed_url='http://example.com/3',
                        last_updated=timezone.now(), site=self.site),
        ])

    def test_filter_to_update(self):
        feeds_to_update = populate_feed_data.Command.get_feeds_to_update(all_feeds=False)
        self.assertEqual(set([self.new_feed, self.update_feed]), set(feeds_to_update))
