from pytumblr import TumblrRestClient
from pprint import pformat
from operator import itemgetter

from . import log

logger = log.getChild(__name__)

DEBUG = True
if DEBUG:
    log.setDebugLevel(log.DEBUG)
else:
    log.setDebugLevel(log.INFO)

def get_client(appinfo, authinfo):
    client = TumblrRestClient(
        appinfo.consumer_key, appinfo.consumer_secret,
        authinfo.token, authinfo.secret
    )
    user = client.info().get('user')
    logger.debug(
        'connect to account %s with %d followings and %d likes',
        user.get('name'), user.get('following'), user.get('likes')
    )
    return client

def make_it_do(appinfo, authinfo, method_name, data):
    client = get_client(appinfo, authinfo)
    username = client.info()['user']['name']
    completed = list()
    uncompleted = list()

    logger.debug('performing %s on data set %s', method_name, pformat(data))
    for f in data:
        logger.info('make %s to %s %s', username, method_name, f)
        ret = getattr(client, method_name)(*f)
        logger.debug('%s request returns %s', method_name, ret)
        if 'meta' in ret and int(ret['meta'].get('status', 0) / 100) != 2:
            uncompleted.append(f)
            logger.error('cannot %s the data %s', method_name, f)
            logger.error('server returns %s', ret)
        else:
            completed.append(f)
            logger.info('%d of %d %sed', len(completed), len(data), method_name)
    if uncompleted:
        logger.warn(
            'following items are not %sed by %s: %s',
            method_name, username, pformat(uncompleted)
        )
    return completed, uncompleted

def make_it_follow(appinfo, authinfo, followings):
    ans = make_it_do(
        appinfo,
        authinfo,
        'follow',
        list((f.get('uuid'),) for f in followings.get('blogs', []))
    )
    return ans

def make_it_like(appinfo, authinfo, likes):
    ans = make_it_do(
        appinfo,
        authinfo,
        'like',
        list((l.get('id'), l.get('reblog_key')) for l in likes.get('liked_posts', []))
    )
    return ans

def collect_all_pages(collector, data_getter, initial=None):
    ans = list()
    if initial:
        ans.extend(initial)
    offset = len(ans)
    while True:
        page = collector(offset=offset)
        logger.debug('new page received at offset %d: %s', offset, pformat(page))

        data = data_getter(page)
        logger.info('%d data retrieved from source', len(data))
        if not data:
            break
        ans.extend(data)
        offset = len(ans)
    return ans

def migrate(config):
    likes = None
    followings = None
    source_client = get_client(config.appinfo, config.source)

    logger.info('retrieving followings...')
    followings = source_client.following()
    logger.info(
        'found %d followings, grab the whole list...', 
        followings.get('total_blogs', -1)
    )
    followings['blogs'] = collect_all_pages(source_client.following, itemgetter('blogs'), followings['blogs'])
    logger.info(
        '%d of %d followings retrieved',
        len(followings.get('blogs', [])),
        followings.get('total_blogs', -1)
    )
    logger.debug('followings: %s', pformat(followings))

    logger.info('retrieving likes...')
    likes = source_client.likes()
    logger.info(
        'found %d likes, grab the whole list...', 
        likes.get('liked_count', -1)
    )
    likes['liked_posts'] = collect_all_pages(source_client.likes, itemgetter('liked_posts'), likes['liked_posts'])
    logger.info('%d likes retrieved', len(likes))
    logger.debug('likes: %s', pformat(likes))

    for authinfo in config.targets:
        if followings:
            completed, uncompleted = make_it_follow(config.appinfo, authinfo, followings)

        if likes:
            completed, uncompleted = make_it_like(config.appinfo, authinfo, likes)

    logger.info('all done.')



if __name__ == '__main__':
    from .config import load
    config = load('config.json')
    migrate(config)
