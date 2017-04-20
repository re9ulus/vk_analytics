import requests


TOKEN_FILE = 'vk.token'


class VkAPI(object):

    def __init__(self, key, version='5.60'):
        self._api_url = 'https://api.vk.com/method/'
        self._key = key
        self._version = version

    def wall_get(self, params):
        url = self._api_url + 'wall.get?'
        param_string = ['{0}={1}'.format(key, val) for key, val in params.items()]
        param_string += ['{0}={1}'.format(key, val) for key, val in
            {'access_token': self._key, 'v': self._version}.items()]
        url += '&'.join(param_string)
        try:
            resp = requests.get(url).text  # json()
        except:
            pass

        return resp


def test_get(token):
    vk = VkAPI(token)
    params = {'domain': 'sevastopolsearch', 'count': 100, 'offset': 0}

    delta_offset = 100

    with open('test_res.txt', 'w+', encoding='utf-8') as f:
        for i in range(10):
            try:
                print('request {0} offset {1}'.format(params['domain'], params['offset']))
                resp = vk.wall_get(params)
                print('response length: {}'.format(len(resp)))
                f.write(resp)
            except Exception as ex:
                print('exception: {}'.format(ex))
            params['offset'] += delta_offset



if __name__ == '__main__':

    with open(TOKEN_FILE) as f:
        token = f.read().strip()

    test_get(token)
    print('done')
