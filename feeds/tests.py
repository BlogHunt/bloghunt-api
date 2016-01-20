import os
import unittest
from unittest import mock

from django.contrib import auth
from django.core.urlresolvers import reverse
from rest_framework import status, test as resttest
import requests

from . import models

MODULE_PATH = os.path.dirname(__file__)
FEED_FIXTURE_PATH = os.path.abspath(os.path.join(MODULE_PATH, 'fixtures', 'feeds'))


class TestFeedPage(unittest.TestCase):

    def check_feed(self, filename, data):
        mock_response = requests.Response()
        mock_response.status_code = 200
        with open(os.sep.join((FEED_FIXTURE_PATH, filename))) as feed_xml_file:
            mock_response._content = feed_xml_file.read().encode()
        with mock.patch('requests.get', return_value=mock_response):
            feedpage = models.Feed().get_feedpage()
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
        })

    def test_atom(self):
        self.check_feed('atom.xml', {
            'title': 'Example Feed',
            'description': None,
            'link': 'http://example.org/',
        })


class TestApiCreateFeed(resttest.APITestCase):

    def setUp(self):
        self.user = auth.get_user_model().objects.create_user(
            'tester', password='password', is_superuser=True)

    def test_create_new_feed(self):
        mock_feed_url = 'http://example.com/feed.xml'
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('feed-list'), {'rss_url': mock_feed_url}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(list(models.Feed.objects.values_list('rss_url', flat=True)), [mock_feed_url])
