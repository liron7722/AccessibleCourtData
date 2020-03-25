import json
import requests
from scripts.builder import *
from scripts.relative_path import *

HEADERS = {"'Content-Type':'application/json'"}
RULING_INDEX = 'supreme_court_rulings'


def sent_post_request(url, datafile):
    result = requests.post(url, data=json.dumps(datafile), headers=HEADERS)
    print(result)
    return result


def handler(file_to_read):
    with open(file_to_read, encoding='utf-8') as json_file:
        json_data = json.load(json_file)
        # elastic_id = json_data['Doc Details']['מספר הליך']
        elastic_id = 1
        url, data = build_post_request(json_data, RULING_INDEX, elastic_id)
        return sent_post_request(url, data)


def check_index(file_name):
    status = handler(get_path("products\/unhandled_csv_products\/") + file_name)
    return status
