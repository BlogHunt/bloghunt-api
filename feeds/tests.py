from datetime import timedelta
import os
import unittest
from unittest import mock

from django import test as djangotest
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.utils import timezone
from rest_framework import status, test as resttest
import requests

from . import models
from .management.commands import populate_feed_data

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
            'categories': {'1765', 'conferences'},
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
        data = {'rss_url': mock_feed_url, 'tags': []}
        response = self.client.post(reverse('feed-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(list(models.Feed.objects.values_list('rss_url', flat=True)), [mock_feed_url])


class TestPopulateFeedData(djangotest.TestCase):

    def setUp(self):
        self.new_feed, self.update_feed, self.recent_feed = models.Feed.objects.bulk_create([
            models.Feed(rss_url='http://example.com/1', last_updated=None),
            models.Feed(rss_url='http://example.com/2', last_updated=timezone.now() - timedelta(weeks=10)),
            models.Feed(rss_url='http://example.com/3', last_updated=timezone.now()),
        ])

    def test_filter_to_update(self):
        feeds_to_update = populate_feed_data.Command.get_feeds_to_update(all_feeds=False)
        self.assertEqual(set([self.new_feed, self.update_feed]), set(feeds_to_update))
