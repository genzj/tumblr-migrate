import json
from collections import namedtuple
from pprint import pformat

from .log import getChild

logger = getChild(__name__)

class ConfigError(Exception): pass

AppInfo = namedtuple(
    'AppInfo', (
        'consumer_key',
        'consumer_secret',
    )
)

AuthInfo = namedtuple(
    'AuthInfo', (
        'token',
        'secret'
    )
)

class Config(object):
    def __init__(self):
        self.appinfo = AppInfo('', '')
        self.source = None
        self.targets = list()

    def __repr__(self):
        return '<Config %r, %r, %r>' % (self.appinfo, self.source, self.targets)

    @staticmethod
    def from_dict(d):
        logger.debug('parsing from dict %s', pformat(d))
        ans = Config()
        ans.appinfo = AppInfo(
            d.get('consumer_key', ''),
            d.get('consumer_secret', ''),
        )
        source = d.get('source')
        if not source:
            raise ConfigError('required key "source" not set in the config')
        targets = d.get('targets')
        if not targets:
            raise ConfigError('required key "targets" not set in the config')
        ans.source = AuthInfo(
            source.get('token'),
            source.get('secret'),
        )
        for t in targets:
            ans.targets.append(AuthInfo(
                t.get('token'),
                t.get('secret'),
            ))
        return ans

def load(filename):
    try:
        with open(filename, 'rb') as f:
            o = json.load(f)
        return Config.from_dict(o)
    except Exception as ex:
        logger.error('cannot load from %s', filename)
        logger.exception(ex)

if __name__ == '__main__':
    config = load('config.json')
    logger.info('parsed from config.json:\n%s', pformat(config))
