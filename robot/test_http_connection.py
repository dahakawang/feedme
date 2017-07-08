from robot.http_connection import HttpConnection
import pytest
import json
import logging


logging.getLogger().setLevel(logging.DEBUG)

class TestHttpConnection:
    @classmethod
    def setup_class(cls):
        with open("proxies.json", "r") as f:
            cls.proxy_cfg = json.load(f)
        cls.conn = HttpConnection(cls.proxy_cfg)

    @classmethod
    def teardown_class(cls):
        cls.conn.close()

    @pytest.mark.asyncio
    async def test_request(self):
        resp = await self.conn.request("http://www.google.com")
        print(resp)
