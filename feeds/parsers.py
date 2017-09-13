"""

author: Brian Schrader
"""

import re, json

from bs4 import BeautifulSoup, Doctype
from lxml import etree


class NotASiteError(Exception):
    pass

class NotAFeedError(Exception):
    pass


class NotAnRSSFeedError(NotAFeedError):
    pass


class NotAJSONFeedError(NotAFeedError):
    pass


class SiteHasNoFeedsError(Exception):
    pass


def get_site_soup(content):
    soup = BeautifulSoup(content, 'html.parser')
    if not _is_probably_a_site_page(soup):
        raise NotASiteError('This content doesn\'t seem to be an HTML page.')
    return soup


def get_rss_feed_parts(content, overtime=False):
    """ Given the byte content of what is supposed to be an RSS feed,
    return the channel element tree and the default namespace.

    :throws:
    """
    tree = etree.fromstring(content, parser=etree.XMLParser(recover=overtime))
    if tree is None:
        raise NotAnRSSFeedError('Tree cannot be parsed.')
    if not _is_probably_an_rss_feed(tree):
        raise NotAnRSSFeedError('This content doesn\'t seem to be an RSS feed.')
    channel = tree.find('{*}channel')
    channel = channel if channel is not None else tree
    nsmatch = re.match('\{.*\}', channel.tag)
    defaultns = nsmatch.group(0) if nsmatch else ''
    return (channel, defaultns)


def get_json_feed(content):
    """ Given the byte content of what is supposed to be a JSON feed,
    return the feed as a page.

    Note: Only UTF-8 encoded feeds are supported.
    """
    feed = json.loads(content.decode('utf-8'))
    if not _is_json_feed(feed):
        raise NotAJSONFeedError('JSON is not a valid feed.')
    return feed


# Private


def _is_probably_a_site_page(soup):
    """ Checks a few heuristics to see if a given soup is probably an HTML
    site rather than a feed.

    Heuristics
    ----------
    - Does it have a doctype element?
    - Does it have an html element?
    """
    for item in soup.contents:
        if isinstance(item, Doctype):
            return True

    html = soup.find_all('html')
    if len(html) > 0:
        return True

    # TODO: Add more checks.

    return False


def _is_probably_an_rss_feed(tree):
    """ Checks a few heuristics to see if a given feed is probably RSS.

    Heuristics
    ----------
    - Does it have any items or entries?
    - Does it have a channel?
    """
    items = tree.find('{*}item')
    if items is not None:
        return True

    channel = tree.find('{*}channel')
    if channel is not None:
        return True

    # Atom Support
    entries = tree.find('{*}entry')
    if entries is not None:
        return True

    # TODO: Add more checks.

    return False


def _is_json_feed(feed):
    """ Checks a few heuristics to see if a given JSON object
    is a valid JSON feed.

    Heuristics
    ----------
    - If the feed has a version.
    """
    if feed.get('version'):
        return True
    return False
