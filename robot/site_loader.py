import os
import json
from .common import *
from urllib.parse import urlparse


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
        yield



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

