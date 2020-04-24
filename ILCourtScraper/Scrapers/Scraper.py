# -*- coding: utf-8 -*-
import sys
sys.path.insert(1, '../..')
from psutil import cpu_count
from concurrent.futures import ThreadPoolExecutor
from ILCourtScraper.Extra.db import DB
from ILCourtScraper.Extra.time import currTime
from ILCourtScraper.Extra.logger import Logger
from ILCourtScraper.Extra.path import getPath, sep, createDir


class Scraper:
    num_of_crawlers = None  # number of threads as well
    product_path = None  # product path as string
    logger = None

    def __init__(self, num_of_crawlers=0, site=None):
        self.logger = Logger(f'{site}_Scraper.log', getPath(N=2) + f'logs{sep}').getLogger()
        self.db = DB(logger=self.logger).getDB(site)
        self.num_of_crawlers = cpu_count() if num_of_crawlers == 0 else num_of_crawlers  # 0 = max, else num
        self.product_path = getPath(N=2) + f'products{sep}json_products{sep}'  # product path
        createDir(self.product_path)

    # Functions
    # output - return case file name by date and page index as string
    @staticmethod
    def randomName(index=0):
        return f'{currTime()}_{index}.json'  # date_time_index.json

    def getSettings(self, key):
        collection = self.db.get_collection('settings')
        query = collection.find({})
        for item in query:
            if key in item:
                return item[key]
        return None

    def get_link(self):
        return NotImplementedError

    def start_crawler(self, index):
        return NotImplementedError

    # do - take thread from pool and give them assignment
    def start(self):
        with ThreadPoolExecutor() as executor:
            indexes = [index for index in range(1, self.num_of_crawlers + 1)]
            executor.map(self.start_crawler, indexes)
