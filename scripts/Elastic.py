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
from json_validator import *
from internet import *

HEADERS = {"Content-Type": "application/json"}
RULING_INDEX = 'supreme_court_rulings_test'
HANDLED_JSON_PRODUCTS_PATH = "products/handled_json_products_test"
THE_AMOUNT_OF_DELIVERABLES_TO_SEND_EACH_TIME = 100

elasticsearch_index_list = list()


class Elastic:
    _logger = None
    _moving = None
    _schema = None
    _counter = None

    def __init__(self, json_schema=True, the_amount_of_delivery=THE_AMOUNT_OF_DELIVERABLES_TO_SEND_EACH_TIME):
        self._log_name = 'Elastic.log'  # name log file
        self._log_path = self.fixPath() + f'{os.sep}logs{os.sep}'
        self._logger = self.startLogger()
        self._moving = Moving()
        self._schema = json_schema
        self._counter = the_amount_of_delivery

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

        file_handler = logging.handlers.RotatingFileHandler(self._log_path + self._log_name, maxBytes=10485760,
                                                            backupCount=10)
        file_handler.setFormatter(formatter)

        newLogger.addHandler(file_handler)
        newLogger.addHandler(stream_handler)

        newLogger.info('Initialize')
        return newLogger

    def start_index(self):
        self._logger.info("Start posting information into Elastic")
        directory = get_path(folder=HANDLED_JSON_PRODUCTS_PATH)
        list_of_products = self.get_files_from_folder(folderName=directory)
        self._logger.info("Get all file from handled_json_products_path folder")
        if self._schema:
            self.index_with_schema(list_of_products)
        else:
            self.index_without_schema(list_of_products)
        self._logger.info("The elastic posting process is over at this point")

        with open('listfile.txt', 'w') as filehandle:
            for listitem in elasticsearch_index_list:
                filehandle.write('%s\n' % listitem)

    def index_with_schema(self, list_of_products):
        for (idx, product) in enumerate(list_of_products, 1):
            if idx % self._counter == 0:
                self._logger.info("Testing in front of Elastic server")
                if not is_connected():  # check if elastic is up
                    self._logger.info("Elastic server is not available, please try later")
                    return
                else:
                    self._logger.info("Elastic server is available")

            file_name = os.path.basename(product)
            self._logger.info("Begins file verification")
            if validate_v1(dataFile=product):
                self._logger.info("File approved")
                self._logger.info("Handles file # {} by name {}".format(idx, file_name))
                ack = False
                retry = 1
                while ack is not True and retry <= 3:
                    self._logger.info("Attempt to index Elastic # {} of file by name {}".format(retry, file_name))
                    ack = self.handler(file_to_read=product, file_name=file_name)
                    retry += 1
                self._logger.info(
                    "The file named {} finished the process and moved to its new location".format(file_name))
                self._moving.move_to_a_new_location(product, ack)
            else:
                self._logger.info("File is not approved")
                self._logger.info("UnHandles file # {} by name {}".format(idx, file_name))
                self._logger.info("The file is moved to an unsuccessful file folder")
                self._moving.move_to_a_new_location(product, False)

    def index_without_schema(self, list_of_products):
        for (idx, product) in enumerate(list_of_products, 1):
            if idx % self._counter == 0:
                self._logger.info("Testing in front of Elastic server")
                if not is_connected():  # check if elastic is up
                    self._logger.info("Elastic server is not available, please try later")
                    return
                else:
                    self._logger.info("Elastic server is available")

            file_name = os.path.basename(product)
            self._logger.info("Handles file # {} by name {}".format(idx, file_name))
            ack = False
            retry = 1
            while ack is not True and retry <= 3:
                self._logger.info("Attempt to index Elastic # {} of file by name {}".format(retry, file_name))
                ack = self.handler(file_to_read=product, file_name=file_name)
                retry += 1
            self._logger.info("The file named {} finished the process and moved to its new location".format(file_name))
            self._moving.move_to_a_new_location(product, ack)

    def sent_post_request(self, url, datafile):
        return requests.post(url, data=json.dumps(datafile), auth=('elastic', 'changeme'), headers=HEADERS)

    def check_status_code(self, status):
        self._logger.info("The Elastic file revenue status code is {} ".format(status.status_code))
        if 200 <= status.status_code <= 299:
            return True
        return False

    def get_files_from_folder(self, folderName, fileType='json'):
        return [f for f in glob.glob(folderName + os.sep + "*." + fileType)]

    def send_get_request(self, url):
        return requests.get(url, auth=('elastic', 'changeme'))

    def comparison_data(self, data_to_post, data_from_elastic):
        result = data_to_post['Doc Details']['מספר הליך'] in data_from_elastic['_source']['Doc Details']['מספר הליך'] or \
                 data_from_elastic['_source']['Doc Details']['מספר הליך'] in data_to_post['Doc Details']['מספר הליך'] or \
                 data_from_elastic['_source']['Doc Details']['מספר הליך'] == "null" and \
                 data_to_post['Doc Details']['לפני'] in data_from_elastic['_source']['Doc Details']['לפני'] or \
                 data_from_elastic['_source']['Doc Details']['לפני'] in data_to_post['Doc Details']['לפני'] or \
                 data_from_elastic['_source']['Doc Details']['לפני'] == "null" and \
                 data_to_post['Doc Details']['העותר'] in data_from_elastic['_source']['Doc Details']['העותר'] or \
                 data_from_elastic['_source']['Doc Details']['העותר'] in data_to_post['Doc Details']['העותר'] or \
                 data_from_elastic['Doc Details']['העותר'] == "null" and \
                 data_to_post['Doc Details']['המשיב'] in data_from_elastic['_source']['Doc Details']['המשיב'] or \
                 data_from_elastic['_source']['Doc Details']['המשיב'] in data_to_post['Doc Details']['המשיב'] or \
                 data_from_elastic['Doc Details']['המשיב'] == "null" and \
                 data_to_post['Doc Details']['סוג מסמך'] in data_from_elastic['_source']['Doc Details']['סוג מסמך'] or \
                 data_from_elastic['_source']['Doc Details']['סוג מסמך'] in data_to_post['Doc Details']['סוג מסמך'] or \
                 data_from_elastic['Doc Details']['סוג מסמך'] == "null" and \
                 data_to_post['Doc Details']['סיכום'] in data_from_elastic['_source']['Doc Details']['סיכום'] or \
                 data_from_elastic['_source']['Doc Details']['סיכום'] in data_to_post['Doc Details']['סיכום'] or \
                 data_from_elastic['Doc Details']['סיכום'] == "null"
        return result

    def handler(self, file_to_read, file_name):
        with open(file_to_read, encoding='utf-8') as json_file:
            json_data = json.load(json_file)  # Load json file
            id_from_json = json_data['Doc Details']['מספר הליך']  # Take procedure number from json file

            elasticsearch_id = build_elasticsearch_id(json_id=id_from_json)  # Build id to get and post request
            get_url = build_get_request(index=RULING_INDEX, id=elasticsearch_id)  # Build get request url
            get_result = self.send_get_request(url=get_url)  # Send get request
            data_from_elastic = get_result.json()  # Convert result from get request to json format

            if self.check_status_code(get_result) is False and data_from_elastic['found'] is False:
                # Build post request url and data
                post_url, post_data = build_post_request(json_file=json_data, index=RULING_INDEX, id=elasticsearch_id)
                post_status = self.sent_post_request(post_url, post_data)  # Do post request and get post status
                elasticsearch_index_list.append(elasticsearch_id)
                return self.check_status_code(post_status)  # Check type of status code and return

            while self.check_status_code(get_result) and data_from_elastic['found'] is True:
                the_result_of_the_comparison = self.comparison_data(data_to_post=json_data, data_from_elastic=data_from_elastic)
                if the_result_of_the_comparison:
                    post_status = self.sent_post_request(post_url, post_data)
                    elasticsearch_index_list.append(elasticsearch_id)
                    return self.check_status_code(post_status)
                else:
                    elasticsearch_id = rebuilding_id(elasticsearch_id)
                    get_url = build_get_request(index=RULING_INDEX, id=elasticsearch_id)
                    get_result = self.send_get_request(get_url)
                    data_from_elastic = get_result.json()

            if self.check_status_code(get_result) is False and data_from_elastic['found'] is False:
                post_url, post_data = build_post_request(json_file=json_data, index=RULING_INDEX, id=elasticsearch_id)
                post_status = self.sent_post_request(post_url, post_data)
                elasticsearch_index_list.append(elasticsearch_id)
                return self.check_status_code(post_status)

            elasticsearch_index_list.append(elasticsearch_id)
            return False

    def call_sleep(self, days=0, hours=0, minutes=1, seconds=0):
        massage = f"Going to sleep for {days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
        self._logger.info(massage)
        sleep((days * 24 * 60 * 60) + (hours * 60 * 60) + (minutes * 60) + seconds)


if __name__ == '__main__':
    while True:
        Elastic().start_index()  # start index product to elastic DB
        Elastic().call_sleep(minutes=10)  # after finished with all the files wait a bit - hours * minutes * seconds
