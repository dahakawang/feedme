import pytest
from robot.site_loader import *
from asynctest.mock import MagicMock, Mock


class TestSiteLoaderManager():
    @pytest.fixture
    def manager(self):
        return SiteLoaderManager({'base_dir': 'fixture/patterns'})

    @pytest.mark.asyncio
    async def test_refresh(self, manager):
        manager.refresh()
        loader = manager.get_loader(None, 'http://www.cnbeta.com')
        assert isinstance(loader, SiteLoader)

        loader = manager.get_loader(None, 'https://www.cnbeta.com')
        assert isinstance(loader, SiteLoader)

        loader = manager.get_loader(None, 'http://www.youtube.com')
        assert loader is None

        loader = manager.get_loader(None, 'http://www.matrix67.com')
        assert loader is None

    @pytest.mark.asyncio
    async def test_get_description(self, manager):
        manager.refresh()
        loader = manager.get_loader(None, 'http://www.cnbeta.com')
        desc = await loader.description()
        assert desc.title == 'cnBeta.COM_中文业界资讯站'
        assert desc.url == 'http://www.cnbeta.com'
        assert desc.site_url == 'http://www.cnbeta.com'
        assert desc.last_update_time is None

    @pytest.mark.asyncio
    async def test_get_list(self, manager):
        manager.refresh()

        from robot.http_connection import HttpConnection
        with HttpConnection({}) as conn:
            loader = manager.get_loader(conn, 'http://www.cnbeta.com')
            async for item in loader:
                print(item)
