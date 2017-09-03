import uuid

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from . import parsers, utils, pages


class Error(models.Model):
    HTTPError = 'HTTPError'
    MissingOrInvalidSchemaError = 'MissingOrInvalidSchemaError'
    ConnectionError = 'ConnectionError'
    NotAFeedError = 'NotAFeedError'
    NotAnRSSFeedError = 'NotAnRSSFeedError'
    SiteHasNoFeedsError = 'SiteHasNoFeedsError'

    identifiers = (
        (HTTPError, 'HTTP Error'),
        (MissingOrInvalidSchemaError, 'Missing or Invalid Schema Error'),
        (ConnectionError, 'Connection Error'),
        (NotAFeedError, 'Not A Feed Error'),
        (NotAnRSSFeedError, 'Not An RSS Feed Error'),
        (SiteHasNoFeedsError, 'Site Has No Feeds Error'),
    )

    message = models.TextField(max_length=250, blank=True, null=True)
    identifier = models.CharField(max_length=50, choices=identifiers)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        sitename = getattr(self, 'site', 'No site')
        return '<Error %s: %s>' % (self.identifier, sitename)


class Tag(models.Model):
    slug = models.SlugField(primary_key=True)
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name


class Keyword(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word = models.CharField(max_length=250, blank=True, null=True, unique=False)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return "%s -> %s" % (self.word, self.tag.name)

    class Meta:
        unique_together = (("word", "tag"),)


class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tags = models.ManyToManyField(Tag, related_name='sites')
    link = models.URLField(blank=True, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submitted_sites',
                              on_delete=models.CASCADE, blank=True, null=True)
    error = models.OneToOneField(Error, related_name='site', on_delete=models.CASCADE,
                                 blank=True, null=True)
    default_feed = models.OneToOneField('Feed', related_name='host_site',
                                        on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def time_since_update(self):
        if self.last_updated is None:
            return None
        now = timezone.now()
        delta = now - self.last_updated

        if delta.days == 1:
            return 'yesterday'
        elif delta.days > 1:
            return '%s %s ago' % (delta.days, 'days')
        else:
            return '%s %s ago' % (delta.hours, 'hours')

    @property
    def total_recommendations(self):
        return self.recommendations.count()

    @property
    def title(self):
        return getattr(self.default_feed, 'title', 'Untitled site')

    @property
    def description(self):
        return getattr(self.default_feed, 'description', None)

    @property
    def image(self):
        return getattr(self.default_feed, 'image', None)

    @staticmethod
    def get_site(url, owner=None, verbose=False):
        """ Given a URL attempt to create a site object from it by checking
        if the URL links to either a site or it's Feed.

        :returns: A Site object with associated feeds.
        """
        site = Site(owner=owner)
        if verbose:
            print('Trying as feed...')
        try:
            response_content = utils.encoded_text_from_url(url)
            feed = Feed.get_feed(url, response_content)
            if verbose:
                print('Feed parsed...')
            site.link = feed.link
            site.save()
            site.feeds.add(feed, bulk=False)
        except parsers.NotAnRSSFeedError:
            if verbose:
                print('Trying as site...')
            site_page = pages.get_sitepage(url, response_content)
            site.link = url
            site.save()
            for url in site_page.possible_feeds:
                if verbose:
                    print('Feed detected...\n%s' % url)
                try:
                    feed = Feed.get_feed(url, utils.encoded_text_from_url(url))
                    if verbose:
                        print('Feed parsed...')
                    site.feeds.add(feed, bulk=False)
                except parsers.NotAnRSSFeedError:
                    pass
        if site.feeds.count() == 0:
            raise parsers.SiteHasNoFeedsError('Site has no valid feeds.')
        site.default_feed = site.feeds.all()[0]
        return site


class Feed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feed_url = models.URLField('Feed URL', unique=True)
    title = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    last_updated = models.DateTimeField(editable=False, null=True)
    image = models.URLField('Image URL', blank=True, null=True)
    cloud = models.URLField('Cloud URL', blank=True, null=True)
    cached_content = models.TextField()
    site = models.ForeignKey(Site, related_name='feeds', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('site', 'feed_url')

    def __str__(self):
        return self.feed_url

    def update_using_feedpage(self, feedpage):
        self.title = feedpage.title
        self.description = feedpage.description
        self.link = feedpage.link
        self.image = feedpage.image
        self.cloud = feedpage.cloud
        self.last_updated = timezone.now()
        return self

    @staticmethod
    def get_feed(url, content):
        try:
            feed = Feed.objects.get(feed_url=url)
        except ObjectDoesNotExist:
            feed = Feed(cached_content=content, feed_url=url)
        feed.update_using_feedpage(pages.get_feedpage(url, content, overtime=True))
        return feed
