import pytest
import time
from robot.feed_loader import *


class MockConnection:
    def __init__(self, filename):
        self.file = filename

    async def request(self, *args):
        filename = self.file
        class MockResponse:
            @property
            def raw(self):
                with open(filename, 'rb') as f:
                    return f.read()
        return MockResponse()


class TestRSSLoader:
    @pytest.mark.asyncio
    async def test_description_and_iteration(self):
        connection = MockConnection('fixture/rss_feed.xml')
        loader = RSSLoader(connection, 'http://sample.com/sub/rss/feed.xml')
        feed_info = await loader.description()
        assert feed_info.title == 'Sample Feed'
        assert feed_info.site_url == 'http://sample.com'
        assert feed_info.url == 'http://sample.com/sub/rss/feed.xml'
        update_time = time.strptime('Sat, 07 Sep 2002 0:00:01 GMT', '%a, %d %b %Y %H:%M:%S %Z')
        assert feed_info.last_update_time == update_time

        async for article in loader:
            assert article.title == 'First item title'
            assert article.link == 'http://example.org/item/1'
            update_time = time.strptime('Thu, 05 Sep 2002 16:00:01 GMT', '%a, %d %b %Y %H:%M:%S %Z')
            assert article.published_time == update_time

    @pytest.mark.asyncio
    async def test_with_invalid_rss(self):
        with pytest.raises(InvalidRssError):
            connection = MockConnection('fixture/proxies.json')
            loader = RSSLoader(connection, 'http://sample.com/sub/rss/feed.xml')
            await loader.description()

        with pytest.raises(InvalidRssError):
            connection = MockConnection('fixture/data.xml')
            loader = RSSLoader(connection, 'http://sample.com/sub/rss/feed.xml')
            await loader.description()

