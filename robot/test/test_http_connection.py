from robot.http_connection import HttpConnection
import pytest
from asynctest.mock import MagicMock, Mock
from aiohttp.client import ClientSession
from unittest.mock import sentinel, call, DEFAULT
from aiosocks.connector import ProxyClientRequest
from aiohttp import ClientError


class MockResponse:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def text(self):
        return ''

    async def read(self):
        return ''

    def __getattr__(self, item):
        return 'mock'


def failed_at_step(step, exception_cls):
    current = 1

    def failed(*args, **kwargs):
        nonlocal current
        current += 1
        if current - 1 == step:
            raise exception_cls()
        return DEFAULT

    return failed


class TestHttpConnection:
    @pytest.fixture
    def no_config(self):
        return {}

    @pytest.fixture
    def timeout_config(self):
        return {
            'timeouts': {
                'conn_timeout': 123,
                'read_timeout': 456
            }
        }

    @pytest.fixture(params=['http://localhost:8080', 'socks4://localhost:8080', 'socks5://localhost:8080'])
    def proxy_only_config(self, request):
        return {
            'proxy': {
                'url': request.param,
                'proxy_only': True
            }
        }

    @pytest.fixture(params=['http://localhost:8080', 'socks4://localhost:8080', 'socks5://localhost:8080'])
    def proxy_config(self, request):
        return {
            'proxy': {
                'url': request.param,
                'proxy_only': False
            }
        }

    @pytest.fixture(params=['http://localhost:8080', 'socks4://localhost:8080', 'socks5://localhost:8080'])
    def proxy_with_auth(self, request):
        return {
            'proxy': {
                'url': request.param,
                'auth': {
                    'login': 'myname',
                    'password': 'pw'
                } if not request.param.startswith("socks4://") else {
                    'login': 'myname'
                },
                'proxy_only': True
            }
        }

    @pytest.fixture
    def invalid_config(self):
        return [
            {
                'proxy': {
                    'url': 'https://localhost:8000'
                }
            },
            {
                'proxy': {
                    'url': 'thunder://localhost:8000'
                }
            },
            {
                'proxy': {
                    'url': None
                }
            },
            {
                'proxy': {
                    'url': 'socks4://localhost:8000',
                    'auth': {
                        'password': 'pw'
                    }
                }
            },
            {
                'proxy': {
                    'proxy_only': True
                }
            }
        ]

    @staticmethod
    def _setup(mocker):
        session = MagicMock(ClientSession)
        session.get.return_value = MockResponse()
        session_cls = mocker.patch('robot.http_connection.ClientSession', new=Mock(return_value=session))
        mocker.patch('robot.http_connection.ProxyConnector', new=Mock(return_value=sentinel.connector))
        return session_cls, session

    @pytest.mark.asyncio
    async def test_request_with_no_config_when_got_response_will_return_response(self, mocker, no_config):
        session_cls, session = self._setup(mocker)

        with HttpConnection(no_config) as conn:
            resp = await conn.request("http://www.baidu.com")
            assert resp.proxy_used is False
        session_cls.assert_called_once_with(connector=sentinel.connector, request_class=ProxyClientRequest,
                                            raise_for_status=True)
        session.get.assert_called_once_with("http://www.baidu.com")

    @pytest.mark.asyncio
    async def test_request_with_no_config_when_got_response_fail_will_throw(self, mocker, no_config):
        session_cls, session = self._setup(mocker)
        session.get = Mock(side_effect=ClientError)

        with HttpConnection(no_config) as conn:
            with pytest.raises(ClientError):
                await conn.request("http://www.baidu.com")

    @pytest.mark.asyncio
    async def test_request_with_timeout_config_will_configure_aiohttp_timeouts(self, mocker, timeout_config):
        session_cls, session = self._setup(mocker)

        with HttpConnection(timeout_config) as conn:
            await conn.request("http://www.baidu.com")
        session_cls.assert_called_once_with(connector=sentinel.connector, request_class=ProxyClientRequest,
                                            raise_for_status=True, conn_timeout=123, read_timeout=456)

    @pytest.mark.asyncio
    async def test_request_with_proxy_only_config_will_only_try_with_proxy(self, mocker, proxy_only_config):
        session_cls, session = self._setup(mocker)

        with HttpConnection(proxy_only_config) as conn:
            resp = await conn.request("http://www.baidu.com")
            assert resp.proxy_used is True
        session.get.assert_called_once_with("http://www.baidu.com", proxy=proxy_only_config['proxy']['url'],
                                            proxy_auth=None)

        session.get = Mock(side_effect=ClientError)
        with HttpConnection(proxy_only_config) as conn:
            with pytest.raises(ClientError):
                await conn.request("http://www.baidu.com")

    @pytest.mark.asyncio
    async def test_request_with_proxy_config_will_try_both(self, mocker, proxy_config):
        session_cls, session = self._setup(mocker)

        # no errors happened
        with HttpConnection(proxy_config) as conn:
            resp = await conn.request("http://www.baidu.com")
            assert resp.proxy_used is False
        session.get.assert_called_once_with("http://www.baidu.com")
        session.get.reset_mock()

        with HttpConnection(proxy_config) as conn:
            resp = await conn.request("http://www.baidu.com", True)
            assert resp.proxy_used is True
        session.get.assert_called_once_with("http://www.baidu.com", proxy=proxy_config['proxy']['url'],
                                            proxy_auth=None)
        session.get.reset_mock()

        # errors always happen
        session.get = Mock(side_effect=ClientError)
        with HttpConnection(proxy_config) as conn:
            with pytest.raises(ClientError):
                await conn.request("http://www.baidu.com")
        assert session.get.call_count == 2
        session.get.assert_has_calls([call("http://www.baidu.com"),
                                      call("http://www.baidu.com", proxy=proxy_config['proxy']['url'], proxy_auth=None)],
                                     any_order=False)
        session.get.reset_mock()

        with HttpConnection(proxy_config) as conn:
            with pytest.raises(ClientError):
                await conn.request("http://www.baidu.com", True)
        assert session.get.call_count == 2
        session.get.assert_has_calls([call("http://www.baidu.com", proxy=proxy_config['proxy']['url'], proxy_auth=None),
                                      call("http://www.baidu.com")], any_order=False)
        session.get.reset_mock()

        # errors happened first time
        session.get = Mock(side_effect=failed_at_step(1, ClientError), return_value=MockResponse())
        with HttpConnection(proxy_config) as conn:
            await conn.request("http://www.baidu.com")
        assert session.get.call_count == 2
        session.get.assert_has_calls([call("http://www.baidu.com"),
                                      call("http://www.baidu.com", proxy=proxy_config['proxy']['url'], proxy_auth=None)],
                                     any_order=False)
        session.get.reset_mock()

        # error will happen at the 2nd time
        session.get = Mock(side_effect=failed_at_step(2, ClientError), return_value=MockResponse())
        with HttpConnection(proxy_config) as conn:
            await conn.request("http://www.baidu.com")
        assert session.get.call_count == 1
        session.get.assert_called_once_with("http://www.baidu.com")
        session.get.reset_mock()

    @pytest.mark.asyncio
    async def test_request_with_proxy_auth_will_set_auth(self, mocker, proxy_with_auth):
        session_cls, session = self._setup(mocker)

        with HttpConnection(proxy_with_auth) as conn:
            await conn.request("http://www.baidu.com")
        session.get.assert_called_once()
        auth = session.get.call_args[1]['proxy_auth']
        assert auth.login == 'myname' or auth.login.decode('utf-8') == 'myname'
        if not proxy_with_auth['proxy']['url'].startswith('socks4://'):
            assert auth.password == 'pw' or auth.password.decode('utf-8') == 'pw'

    @pytest.mark.asyncio
    async def test_request_with_invalid_config_will_throw(self, mocker, invalid_config):
        self._setup(mocker)

        for config in invalid_config:
            with pytest.raises(Exception):
                with HttpConnection(config):
                    pass
