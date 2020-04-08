import json
import requests
from builder import *
from relative_path import *

HEADERS = {"Content-Type":"application/json"}
RULING_INDEX = 'supreme_court_rulings'


def sent_post_request(url, datafile):
    return requests.post(url, data=json.dumps(datafile), auth=('elastic','changeme'), headers=HEADERS)


def check_post_status(status):
    print(status)
    if(200 == status.status_code or 201 == status.status_code):
        return True
    return False


def handler(file_to_read, file_name):
    with open(file_to_read, encoding='utf-8') as json_file:
        json_data = json.load(json_file)
        id_from_json = json_data['Doc Details']['מספר הליך']
        elastic_id = build_id_to_elastic(id_from_json, file_name[-13:-5])
        url, data = build_post_request(json_data, RULING_INDEX, elastic_id)
        post_status = sent_post_request(url, data)
        return check_post_status(post_status)


def check_index(file_path, file_name):
    file_path = get_path(file_path) + '/' + file_name
    status = handler(file_path, file_name)
    return status
