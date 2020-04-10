import os
import json
import glob
import requests
import logging
import logging.handlers
from time import sleep
from pathlib import Path
from builder import *
from Moving import Moving
from relative_path import *

HEADERS = {"Content-Type": "application/json"}
RULING_INDEX = 'supreme_court_rulings'
HANDLED_JSON_PRODUCTS_PATH = "products/handled_json_products"


class Elastic:
    _logger = None
    _moving = None
    _schema = None

    def __init__(self, json_schema=False):
        self._log_name = 'Elastic.log'  # name log file
        self._log_path = self.fixPath() + f'{os.sep}logs{os.sep}'
        self._logger = self.startLogger()
        self._moving = Moving()
        self._schema = json_schema

    # Functions
    @staticmethod
    def fixPath(path=None, N=1):
        path = Path().parent.absolute() if path is None else path
        splitPath = str(path).split(os.sep)
        return f"{os.sep}".join(splitPath[:-N])

    def startLogger(self, logger=None):
        newLogger = logging.getLogger(__name__) if logger is None else logger
        newLogger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s: %(message)s', datefmt='%d-%m-%Y %H-%M-%S')

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        file_handler = logging.handlers.RotatingFileHandler(self._log_path + self._log_name, maxBytes=52428800,
                                                            backupCount=10)
        file_handler.setFormatter(formatter)

        newLogger.addHandler(file_handler)
        newLogger.addHandler(stream_handler)

        newLogger.info('Initialize')
        return newLogger

    def start_index(self):
        directory = get_path(folder=HANDLED_JSON_PRODUCTS_PATH)
        list_of_products = self.getFilesFromFolder(folderName=directory)
        self._logger.info("Get all file from handled_json_products_path folder")
        for (idx, product) in enumerate(list_of_products, 1):
            file_name = os.path.basename(product)
            self._logger.info("Handles file # {} by name {}".format(idx, file_name))
            ack = False
            retry = 0
            while ack is not True and retry <= 2:
                self._logger.info("Attempt to index Elastic # {} of file by name {}".format(retry, file_name))
                ack = self.handler(file_to_read=product, file_name=file_name)
                retry += 1
            self._logger.info("The file named {} finished the process and moved to its new location".format(file_name))
            self._moving.move_to_a_new_location(product, ack)

    def sent_post_request(self, url, datafile):
        return requests.post(url, data=json.dumps(datafile), auth=('elastic', 'changeme'), headers=HEADERS)

    def check_post_status(self, status):
        self._logger.info("The Elastic file revenue status code is {} ".format(status.status_code))
        if 200 == status.status_code or 201 == status.status_code:
            return True
        return False

    def getFilesFromFolder(self, folderName, fileType='json'):
        return [f for f in glob.glob(folderName + os.sep + "*." + fileType)]

    def handler(self, file_to_read, file_name):
        with open(file_to_read, encoding='utf-8') as json_file:
            json_data = json.load(json_file)
            id_from_json = json_data['Doc Details']['מספר הליך']
            elastic_id = build_elastic_id(json_id=id_from_json, unique_name=file_name[-13:-5])
            url, data = build_post_request(json_file=json_data, index=RULING_INDEX, id=elastic_id)
            post_status = self.sent_post_request(url, data)
            return self.check_post_status(post_status)

    def call_sleep(self, logFunc=None, days=0, hours=0, minutes=1, seconds=0):
        massage = f"Going to sleep for {days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
        if logFunc is not None:
            logFunc(massage)
        sleep((days * 24 * 60 * 60) + (hours * 60 * 60) + (minutes * 60) + seconds)


if __name__ == '__main__':
    while True:
        Elastic().start_index()  # start index product to elastic DB
        Elastic().call_sleep(minutes=10)  # after finished with all the files wait a bit - hours * minutes * seconds
