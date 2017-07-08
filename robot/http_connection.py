import aiohttp
from collections import namedtuple
from aiosocks.connector import ProxyConnector, ProxyClientRequest
from aiohttp import ClientSession, ClientError
import aiosocks
import logging

HTTPResponse = namedtuple('HTTPResponse', ['version', 'status', 'reason', 'url', 'cookies', 'charset', 'headers', 'text', 'proxy_used'])


async def _response_to_tuple(response, proxy_used):
    return HTTPResponse(response.version, response.status, response.reason, response.url, response.cookies,
                        response.charset, response.headers, await response.text(), proxy_used)


class HttpConnection:
    def __init__(self, cfg):
        self.logger = logging.getLogger(__name__)
        self.cfg = cfg
        self.session = self.proxy_session = None

        self.proxy_url, self.proxy_auth, self.proxy_only = self._get_auth()

    def _create_sessions(self):
        con = ProxyConnector(remote_resolve=True)
        session_cfg = dict(raise_for_status=True, connector=con, request_class=ProxyClientRequest)
        session_cfg.update(self.cfg.get('timeouts', {}))

        self.session = ClientSession(**session_cfg)  # error if return code >= 400

    def _get_proxy_url(self):
        if "url" not in self.cfg["proxy"]:
            raise RuntimeError("proxy have no url configured")
        url = self.cfg["proxy"]["url"]
        if not isinstance(url, str):
            raise RuntimeError("proxy url should be string")
        return url

    def _get_proxy_auth(self, url):
        schema = url.split("://")[0]
        if "auth" not in self.cfg["proxy"]:
            return None
        auth = {"login": "", "password": ""}
        auth.update(self.cfg["proxy"]["auth"])

        if schema == "socks5":
            return aiosocks.Socks5Auth(**auth)
        elif schema == "socks4":
            return aiosocks.Socks4Auth(**auth)
        elif schema == "http":
            return aiohttp.BasicAuth(**auth)
        else:
            raise RuntimeError("in valid schema for url %s" % (url))

    def _get_auth(self):
        if "proxy" not in self.cfg:
            return None, None, None

        url = self._get_proxy_url()
        auth = self._get_proxy_auth(url)
        proxy_only = self.cfg["proxy"].get("proxy_only", False)
        return url, auth, proxy_only

    async def request(self, url):
        if not self.session and not self.proxy_session:
            self._create_sessions()

        if not self.proxy_only:
            try:
                async with self.session.get(url) as response:
                    return await _response_to_tuple(response, False)
            except ClientError as e:
                self.logger.debug("failed to download %s, with error %s", url, e)
                if not self.proxy_url:
                    raise e

        if self.proxy_url:
            async with self.session.get(url, proxy=self.proxy_url, proxy_auth=self.proxy_auth) as response:
                return await _response_to_tuple(response, True)

    def close(self):
        if self.session:
            self.session.close()
        if self.proxy_session:
            self.proxy_session.close()

