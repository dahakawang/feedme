import pytest
from .http_connection import HttpConnection
from .rss_loader import *


class TestRSSLoader:
    @pytest.mark.asyncio
    async def test_description(self):

        with HttpConnection({}) as connection:
            loader = RSSLoader(connection, "http://www.matrix67.com/blog/feed")
            print(await loader.description())
            async for blog in loader:
                print(blog)
