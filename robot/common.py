from collections import namedtuple

Feed = namedtuple('Feed', ['favicon', 'title', 'url', 'site_url', 'last_update_time'])
FeedItem = namedtuple('FeedItem', ['title', 'link', 'published_time'])


class RobotError(RuntimeError):
    pass


class InvalidRssError(RobotError):
    pass


class InvalidConfigError(RobotError):
    pass
