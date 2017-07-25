import os
import re
import json
import time
from lxml import etree
from .common import *
from urllib.parse import urlparse


def _select_all(root, selector):
    return root.xpath(selector)


def _select_one(root, selector):
    rs = _select_all(root, selector)
    if len(rs) != 1:
        raise InvalidPatternError("the matched tag should be exactly one")
    return rs[0]


def _capture(text, cfg):
    text = str(text)
    match = re.search(cfg, text)
    if len(match.groups()) != 1:
        raise InvalidPatternError("the capture should only have one group")
    return match[1]


def _to_datetime(string, pattern):
    try:
        return time.strptime(string, pattern)
    except ValueError:
        raise InvalidPatternError("the datetime format is not valid")


class SiteLoader:
    def __init__(self, conn, url, patterns):
        self.conn = conn
        self.url = url
        self.patterns = patterns

    async def description(self):
        # TODO favicon
        site_url = "://".join([self.url.scheme, self.url.netloc])
        return Feed('', self.patterns['title'], self.url.geturl(), site_url, None)

    async def __aiter__(self):
        await self._load_content()
        articles = self._get_list()
        for article in articles:
            yield article

    async def _load_content(self):
        resp = await self.conn.request(self.url.geturl())
        if not resp.content:
            raise InvalidWebSiteError('this url contains no valid html')
        self.html = etree.fromstring(resp.content, parser=etree.HTMLParser(recover=True))

    def _get_list(self):
        item_list = []
        item_sel = self.patterns['item']['sel']

        for item_elem in _select_all(self.html, item_sel):
            item_list.append(self._get_item(item_elem))
        return item_list

    def _get_item(self, item_elem):
        title = self._get_field(item_elem, 'title')
        link = self._get_field(item_elem, 'link')
        update_time = self._get_field(item_elem, 'update_time')

        return FeedItem(title, link, update_time)

    def _get_field(self, root, field_name):
        cfg = self.patterns['item'][field_name]
        sel = cfg['sel']

        result = _select_one(root, sel)

        if 'capture' in cfg:
            result = _capture(result, cfg['capture'])
        if 'date-format' in cfg:
            result = _to_datetime(result, cfg['date-format'])
        return result


class SiteLoaderManager:
    def __init__(self, cfg):
        self.cfg = cfg
        self.patterns = {}
        self._sanity_check()

    def refresh(self):
        base_dir = self.cfg['base_dir']
        for root, dirs, files in os.walk(base_dir):
            for config_file in files:
                self._refresh_file(os.path.join(root, config_file))

    def get_loader(self, conn, url):
        parsed_url = urlparse(url)
        key = parsed_url.netloc
        if key in self.patterns:
            return SiteLoader(conn, parsed_url, self.patterns[key]['feed'])
        else:
            return None

    def _sanity_check(self):
        if 'base_dir' not in self.cfg:
            raise InvalidConfigError("SiteLoaderManager should see the base_dir config")

    def _refresh_file(self, config_file):
        # TODO add json schema sanity check here
        with open(config_file, 'r', encoding='utf-8') as file:
            site_desc_list = json.load(file, encoding='utf-8')
            for site_desc in site_desc_list:
                self._update_site_patterns(site_desc)

    def _update_site_patterns(self, desc):
        key = desc['url']
        if 'feed' in desc:
            self.patterns[key] = desc

