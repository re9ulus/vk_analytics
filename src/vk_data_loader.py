import requests

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import config

TOKEN_FILE = 'vk.token'


class VkAPI(object):

    def __init__(self, token :str, version='5.60'):
        self._api_url = 'https://api.vk.com/method/'
        self._token = token
        self._version = version
        self._auth_params = ['{0}={1}'.format(key, val) for key, val in
            {'access_token': self._token, 'v': self._version}.items()]

    def wall_get(self, params :dict, return_text=True):
        url = self._api_url + 'wall.get?'
        params = dict(params)
        params['access_token'] = self._token
        params['v'] = self._version
        resp = None
        try:
            resp = requests.get(url, params=params)
            if return_text:
                resp = resp.text
            else:
                resp = resp.json()
        except Exception as ex:
            logger.exception('{0}\nurl: {1}\nparams: {}'.format(ex, url, params))
        return resp

    def wall_get_all(self, domain :str, count=100, offset=0, delta_offset=100, pages_to_get=10):
        params = {'domain': domain , 'count': count, 'offset': offset}
        for i in range(pages_to_get):
            logger.info('get page: {0}/{1}'.format(i+1, pages_to_get))
            yield self.wall_get(params)
            params['offset'] += delta_offset


def wall_to_file(filename, wall):
    with open(filename, 'w+', encoding='utf-8') as f:
        for data in wall:
            if data:
                try:
                    f.write(data)
                    f.write('\n')
                except Exception as ex:
                    logger.exception('{0}'.format(ex))


def main_test():
    logger.info('start')
    with open(TOKEN_FILE) as f:
        token = f.read().strip()
    vk = VkAPI(token)
    wall_to_file(config.RAW_DATA_FILENAME, vk.wall_get_all(config.DOMAIN, pages_to_get=1000))
    logger.info('done')


if __name__ == '__main__':
    main_test()
