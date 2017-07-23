import feedparser
import time
from lxml import etree
from urllib.parse import urlparse
from .common import *


def _extract_publish_time(entry):
    return entry.published_parsed if 'published_parsed' in entry else None


class RSSLoader:
    def __init__(self, conn, url):
        self.conn = conn
        self.url = urlparse(url)
        self.content = None
        self.feed = None

    async def _ensure_data(self):
        if self.feed:
            return

        self.content = await self._request()
        self.feed = feedparser.parse(self.content)
        self._sanity_check()

    async def _request(self):
        content = (await self.conn.request(self.url.geturl())).raw
        parser = etree.XMLParser(ns_clean=True, recover=True)
        parsed_tree = etree.fromstring(content, parser=parser)

        if parsed_tree is None:
            raise InvalidRss("invalid xml format")
        return etree.tostring(parsed_tree)

    async def description(self):
        await self._ensure_data()

        # TODO get favicon
        title = self.feed.feed.title
        url = self.url.geturl()
        site_url = "://".join([self.url.scheme, self.url.netloc])
        return Feed('', title, url, site_url, _extract_publish_time(self.feed.feed))

    async def __aiter__(self):
        await self._ensure_data()

        for entry in self.feed.entries:
            yield FeedItem(entry.title, entry.link, _extract_publish_time(entry))

    def _sanity_check(self):
        feed = self.feed
        if not (feed and 'title' in feed.feed and feed.entries):
            raise InvalidRss("The documents lacks necessary tags, it may be an invalid RSS")


