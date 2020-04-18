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
INDEXES_FILE_LOCATION = "products/indexes.txt"
NUMBER_OF_REPETITIONS_IN_CASE_OF_FAILURE = 5
THE_AMOUNT_OF_DELIVERABLES_TO_SEND_EACH_TIME = 100
DELAY_TIME_BETWEEN_ONE_REQUEST_AND_ANOTHER = 2  # In seconds
GET_REQUEST = "GET"
POST_REQUEST = "POST"


class Elastic:
    _logger = None
    _moving = None
    _schema = None
    _counter = None
    _elk_id = None
    _elasticsearch_indexes_list = None

    def __init__(self, json_schema=True, the_amount_of_delivery=THE_AMOUNT_OF_DELIVERABLES_TO_SEND_EACH_TIME):
        self._log_name = 'Elastic.log'  # name log file
        self._log_path = self.fixPath() + f'{os.sep}logs{os.sep}'
        self._logger = self.startLogger()
        self._moving = Moving()
        self._schema = json_schema
        self._counter = the_amount_of_delivery
        self._elasticsearch_indexes_list = list()

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

    def index_with_schema(self, list_of_products):
        for (idx, product) in enumerate(list_of_products, 1):
            if idx == 1:
                self._logger.info("Testing in front of Elastic server")
                if not is_connected():  # check if elastic is up
                    self._logger.info("Elastic server is not available, please try later")
                    return
                else:
                    self._logger.info("Elastic server is available")

            if idx % self._counter == 0:
                self._logger.info("Writing the results of Elastic posting in the index file")
                self.write_indexes_to_file()
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
                while ack is not True and retry <= NUMBER_OF_REPETITIONS_IN_CASE_OF_FAILURE:
                    self._logger.info("Attempt to index Elastic # {} of file by name {}".format(retry, file_name))
                    ack, self._elk_id = self.handler(file_to_read=product)
                    retry += 1
                if ack is True:
                    self._elasticsearch_indexes_list.append("{id}::{file_name}".format(id=self._elk_id, file_name=file_name))
                self._logger.info("The file named {} finished the process and moved to its new location".format(file_name))
                self._moving.move_to_a_new_location(product, ack)
            else:
                self._logger.info("File is not approved")
                self._logger.info("UnHandles file # {} by name {}".format(idx, file_name))
                self._logger.info("The file is moved to an unsuccessful file folder")
                self._moving.move_to_a_new_location(product, False)

        if not self._elasticsearch_indexes_list:
            self._logger.info("Writing the results of Elastic posting in the index file")
            self.write_indexes_to_file()

    def index_without_schema(self, list_of_products):
        for (idx, product) in enumerate(list_of_products, 1):
            if idx == 1:
                self._logger.info("Testing in front of Elastic server")
                if not is_connected():  # check if elastic is up
                    self._logger.info("Elastic server is not available, please try later")
                    return
                else:
                    self._logger.info("Elastic server is available")

            if idx % self._counter == 0:
                self._logger.info("Writing the results of Elastic posting in the index file")
                self.write_indexes_to_file()
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
                ack, self._elk_id = self.handler(file_to_read=product)
                retry += 1
            if ack is True:
                self._elasticsearch_indexes_list.append("{id}::{file_name}".format(id=self._elk_id, file_name=file_name))
            self._logger.info("The file named {} finished the process and moved to its new location".format(file_name))
            self._moving.move_to_a_new_location(product, ack)

        if not self._elasticsearch_indexes_list:
            self._logger.info("Writing the results of Elastic posting in the index file")
            self.write_indexes_to_file()


    def write_indexes_to_file(self):
        path = get_path(folder=INDEXES_FILE_LOCATION)
        list_of_indexes = self._elasticsearch_indexes_list

        # first append all indexes to file
        with open(path, "a") as file:
            for line in list_of_indexes:
                file.write(line + '\n')
            file.close()

        # second get all lines from file
        with open(path, 'r') as file:
            lines = file.readlines()
            file.close()

        # remove spaces
        lines = [line.replace(' ', '') for line in lines]
        lines.sort()

        # finally, write lines in the file
        with open(path, 'w') as file:
            file.writelines(lines)
            file.close()
        self._elasticsearch_indexes_list = list()

    def sent_post_request(self, url, datafile):
        return requests.post(url, data=json.dumps(datafile), auth=('elastic', 'changeme'), headers=HEADERS)

    def check_status_code(self, status, type_of_request):
        self._logger.info("{type_of_request}: The Elastic file revenue status code is {status} ".format(type_of_request=type_of_request, status=status.status_code))
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

    def handler(self, file_to_read):
        with open(file_to_read, encoding='utf-8') as json_file:
            try:
                json_data = json.load(json_file)  # Load json file
                self._logger.info("The file was successfully loaded")
                id_from_json = json_data['Doc Details']['מספר הליך']  # Take procedure number from json file
                self._logger.info("The procedure number is taken from the file for further treatment")

                elasticsearch_id = build_elasticsearch_id(json_id=id_from_json)  # Build id to get and post request
                self._logger.info("ID successfully built")
                get_url = build_get_request(index=RULING_INDEX, id=elasticsearch_id)  # Build get request url
                self._logger.info("Successfully built get request URL")
                self.sleep_now()
                get_result = self.send_get_request(url=get_url)  # Send get request
                self._logger.info("GET request sent")
                data_from_elastic = get_result.json()  # Convert result from get request to json format

                if self.check_status_code(get_result, GET_REQUEST) is False and data_from_elastic['found'] is False:
                    # Build post request url and data
                    post_url, post_data = build_post_request(json_file=json_data, index=RULING_INDEX, id=elasticsearch_id)
                    self._logger.info("Successfully built post request URL and data")
                    self.sleep_now()
                    post_status = self.sent_post_request(post_url, post_data)  # Do post request and get post status
                    self._logger.info("POST request sent")
                    return self.check_status_code(post_status, POST_REQUEST), elasticsearch_id  # Check type of status code and return

                while self.check_status_code(get_result, GET_REQUEST) and data_from_elastic['found'] is True:
                    the_result_of_the_comparison = self.comparison_data(data_to_post=json_data, data_from_elastic=data_from_elastic)
                    self._logger.info("The result of comparison is: {result} ".format(result=the_result_of_the_comparison))
                    if the_result_of_the_comparison:
                        post_url, post_data = build_post_request(json_file=json_data, index=RULING_INDEX, id=elasticsearch_id)
                        self.sleep_now()
                        post_status = self.sent_post_request(post_url, post_data)  # Do post request and get post status
                        self._logger.info("POST request sent")
                        return self.check_status_code(post_status, POST_REQUEST), elasticsearch_id  # Check type of status code and return
                    else:
                        elasticsearch_id = rebuilding_id(elasticsearch_id)
                        self._logger.info("ID successfully rebuild")
                        get_url = build_get_request(index=RULING_INDEX, id=elasticsearch_id)
                        self._logger.info("Successfully built get request URL")
                        self.sleep_now()
                        get_result = self.send_get_request(get_url)
                        self._logger.info("GET request sent")
                        data_from_elastic = get_result.json()

                if self.check_status_code(get_result, GET_REQUEST) is False and data_from_elastic['found'] is False:
                    post_url, post_data = build_post_request(json_file=json_data, index=RULING_INDEX, id=elasticsearch_id)
                    self._logger.info("Successfully built post request URL and data")
                    self.sleep_now()
                    post_status = self.sent_post_request(post_url, post_data)  # Do post request and get post status
                    self._logger.info("POST request sent")
                    return self.check_status_code(post_status, POST_REQUEST), elasticsearch_id  # Check type of status code and return
                return False, None
            except:
                self._logger.info("There was an error event")
                return False, None

    def sleep_now(self):
        self._logger.info("The system is delayed for {0} seconds".format(DELAY_TIME_BETWEEN_ONE_REQUEST_AND_ANOTHER))
        sleep(DELAY_TIME_BETWEEN_ONE_REQUEST_AND_ANOTHER)
        self._logger.info("The delay is over")

    def call_sleep(self, days=0, hours=0, minutes=1, seconds=0):
        massage = f"Going to sleep for {days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
        self._logger.info(massage)
        sleep((days * 24 * 60 * 60) + (hours * 60 * 60) + (minutes * 60) + seconds)


if __name__ == '__main__':
    while True:
        Elastic().start_index()  # start index product to elastic DB
        Elastic().call_sleep(minutes=10)  # after finished with all the files wait a bit - hours * minutes * seconds
