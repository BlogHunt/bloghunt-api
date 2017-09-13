from urllib import parse
import itertools, json

from . import parsers, utils


def get_sitepage(url, cached_content=None):
    """ Ask for new sitepage content from url and return a site page """
    if not cached_content:
        cached_content = utils.encoded_text_from_url(url)
    soup = parsers.get_site_soup(cached_content)
    return SitePage(soup, url=url)


def get_feedpage(url, cached_content=None, overtime=False):
    """ Ask for new feedpage content from feed_url and return a feed page.
    This function will attempt to parse JSON Feeds and XML Feeds before failing.

    TODO: Add more intelligence to check the URL before trying to parse.
    """
    if not cached_content:
        cached_content = utils.encoded_text_from_url(url)
    try:
        feed = parsers.get_json_feed(cached_content)
        return JSONFeedPage(feed, url=url)
    except (parsers.NotAJSONFeedError, json.decoder.JSONDecodeError) as e:
        pass
    channel, defaultns = parsers.get_rss_feed_parts(cached_content, overtime=overtime)
    return RssFeedPage(channel, url=url, defaultns=defaultns)


class RssFeedPage(object):

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


class JSONFeedPage(object):
    def __init__(self, feed, url=''):
        self.feed = feed
        self.url = url

    @property
    def title(self):
        return self.feed.get('title', None)

    @property
    def description(self):
        return self.feed.get('description', None)

    @property
    def link(self):
        return self.feed.get('home_page_url', None)

    @property
    def image(self):
        author = self.feed.get('author', None)
        if author:
            image = author.get('avatar', None)
        else:
            image = self.feed.get('icon', None)
            if not image:
                image = self.feed.get('favicon', None)
        return image


class SitePage(object):

    def __init__(self, soup, url=''):
        self.soup = soup
        self.url = url

    @property
    def possible_feeds(self):
        for feed_elem in self.soup.find_all(rel='alternate'):
            # Check for relative links.
            if feed_elem['href'][:3] == 'http':
                yield feed_elem['href']
            else:
                yield parse.urljoin(self.url, feed_elem['href'])
