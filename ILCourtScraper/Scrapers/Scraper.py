# -*- coding: utf-8 -*-
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
        logPath = getPath(N=0) + f'logs{sep}{site}{sep}' if site is not None else getPath(N=0) + f'logs{sep}'
        self.logger = Logger(f'{site}_Scraper.log', logPath).getLogger()
        self.db = DB(logger=self.logger).getDB(site)
        self.num_of_crawlers = cpu_count() if num_of_crawlers == 0 else num_of_crawlers  # 0 = max, else num
        self.product_path = getPath(N=0) + f'products{sep}json_products{sep}'  # product path
        createDir(self.product_path)

    # Functions
    def getNumOfCrawlers(self):
        return self.num_of_crawlers

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

    def uploadData(self, name, data):
        collection = self.db.get_collection('files')
        collection.insert_one({"name": name, "data": data})

    def get_link(self):
        return NotImplementedError

    def start_crawler(self, index):
        return NotImplementedError
