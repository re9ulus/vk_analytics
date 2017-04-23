import json
import datetime
from typing import Iterable

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import config


class Converter:

    def __init__(self, file_from :str, file_to :str):
        self._file_from = file_from
        self._file_to = file_to
        self._date_format = '%Y-%m-%d %H:%M'
        self._required_keys = ['text', 'date', 'likes', 'comments', 'reposts']

    def convert_item(self, item: dict):
        res = None

        for key in self._required_keys:
            if key not in item:
                return None

        text = self.convert_text(item['text'])
        date = self.convert_date(item['date'])

        likes = item['likes']['count']
        comments = item['comments']['count']
        reposts = item['reposts']['count']

        if text and date:
            res = {'text': text, 'date': date, 'likes': likes, 'comments': reposts,
                'reposts': comments}  # use named tuple insted ?

        return res

    def convert_chunk(self, items: Iterable):
        logger.info('processing chunk...')
        for item in items:
            res = self.convert_item(item)
            if res:
                yield res

    def convert_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                data = self.load_record(line)
                if data and 'response' in data and 'items' in data['response']:
                    yield from self.convert_chunk(data['response']['items'])

    def load_record(self, string_record: str):
        resp = None
        try:
            resp = json.loads(string_record.strip())
        except Exception as ex:
            logger.exception('{}'.format(ex))
        return resp

    def convert_text(self, txt: str):
        txt = txt.replace('\n', ' ')
        return txt

    def convert_date(self, date_str: str):
        resp = None
        try:
            date = int(date_str)
            date = datetime.datetime.fromtimestamp(date).strftime(self._date_format)
            resp = date
        except Exception as ex:
            logger.exception('{}'.format(ex))
        return resp

    def convert_raw_file(self):
        with open(self._file_to, 'w+', encoding='utf-8') as f:
            f.write('\t'.join(self._required_keys) + '\n')
            for item in self.convert_file(self._file_from):
                if item:
                    f.write('\t'.join(str(item[key]) for key in self._required_keys) + '\n')

def convert_data(raw_filename: str, res_filename: str):
    conv = Converter(raw_filename, res_filename)
    conv.convert_raw_file()


if __name__ == '__main__':
    convert_data(config.RAW_DATA_FILENAME, config.PREPARED_DATA_FILENAME)
