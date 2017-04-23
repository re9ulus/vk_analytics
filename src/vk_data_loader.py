import json
import time
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

    def wall_get(self, params :dict, return_text=False):
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
    empty_counter = 0
    max_empty = 3
    sleep_time = 0.3
    with open(filename, 'w+', encoding='utf-8') as f:
        for data in wall:
            if data:
                if 'error' in data:
                    logger.info('error response: {}'.format(data['error']))
                    time.sleep(0.5)
                    continue
                if 'items' in data.get('response', {}) and not data['response']['items']:
                    empty_counter += 1
                    logger.info('Empty response {0}/{1}'.format(empty_counter, max_empty))
                    if empty_counter >= max_empty:
                        logger.info('All data received.')
                        break
                    continue
                empty_counter = 0
                try:
                    f.write(json.dumps(data, ensure_ascii=False))
                    f.write('\n')
                except Exception as ex:
                    logger.exception('{0}'.format(ex))
                time.sleep(sleep_time)


def main_test():
    logger.info('Start')
    with open(TOKEN_FILE) as f:
        token = f.read().strip()
    vk = VkAPI(token)
    wall_to_file(config.RAW_DATA_FILENAME, vk.wall_get_all(config.DOMAIN, pages_to_get=1000))
    logger.info('Done')


if __name__ == '__main__':
    main_test()
