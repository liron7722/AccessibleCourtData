import csv
import json
import os
import requests
from scripts.builder import *

HEADERS = {"'Content-Type':'application/json'"}

A_RULINGS_TITLE = ['החלטה', 'בשם המשיבים', 'בשם העותרים', 'המשיבים', 'העותרים', 'שופטים', 'מספר תיק', 'בית משפט']
TITLE_OF_RULINGS = 'בית משפט העליון'
RULING_INDEX = 'rulings'
RULING_ENTITIES = 'supreme_court_rulings'


def sent_post_request(url, datafile):
    print(requests.post(url, data=json.dumps(datafile), headers=HEADERS))


def read_file_titles(file_to_read):
    with open(file_to_read, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        titles = reader.fieldnames
        csv_file.close()
    return titles


def handler(file_to_read, titles, index_type, doc_type):
    first_line = True
    with open(file_to_read, 'r') as csv_file:
        reader = csv.DictReader(csv_file, titles)
        for row in reader:
            if first_line:
                first_line = False
            else:
                url, data = build_post_request(row, index_type, doc_type)
                sent_post_request(url, data)
        csv_file.close()


def check_index(files_to_read, index_of_product, id_of_product):
    for file_name in files_to_read:
        if os.path.isfile(file_name):
            # titles = read_file_titles(file_name)
            if index_of_product == RULING_INDEX and id_of_product == RULING_ENTITIES:
                handler(file_name, A_RULINGS_TITLE, RULING_ENTITIES, RULING_INDEX)
                return True
            else:
                print("File '{file_name}' is incompatible with indexed".format(file_name=os.path.basename(file_name)))
                return False
        else:
            print("The file '{file_name}' does not exist !".format(file_name=os.path.basename(file_name)))
            return False

