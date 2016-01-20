import os
import unittest
from unittest import mock

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
