import argparse
import csv
import json
import os
import requests
from builder import *

HEADERS = {"'Content-Type':'application/json'"}

A_RULINGS_TITLE = ['החלטה', 'בשם המשיבים', 'בשם העותרים', 'המשיבים', 'העותרים', 'שופטים', 'מספר תיק', 'בית משפט']
B_RULINGS_TITLE = ['פסק דין', 'בשם המשיבים', 'בשם העותרים', 'המשיבים', 'העותרים', 'שופטים', 'מספר תיק', 'בית משפט']
C_RULINGS_TITLE = ['צו', 'בשם המשיבים', 'בשם העותרים', 'המשיבים', 'העותרים', 'שופטים', 'מספר תיק', 'בית משפט']
TITLE_OF_RULINGS = 'בית משפט העליון'
RULING_INDEX = 'rulings'
RULING_ENTITIES = 'supreme_court_rulings'
TOOL_ID = 'מספר תיק'


def sent_post_request(url, datafile):
    print(requests.post(url, data=json.dumps(datafile), headers=HEADERS))


def read_file_titles(file_to_read):
    with open(file_to_read, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        titles = reader.fieldnames
        csv_file.close()
    return titles


def handler(file_to_read, titles, entities, index_type):
    first_line = True
    with open(file_to_read, 'r') as csv_file:
        reader = csv.DictReader(csv_file, titles)
        for row in reader:
            if first_line:
                first_line = False
            else:
                url, data = build_post_request(entities, row, index_type)
                sent_post_request(url, data)
        csv_file.close()


def check_index(files_to_read, index_of_product):
    for file_name in files_to_read:
        if os.path.isfile(file_name):
            titles = read_file_titles(file_name)
            if index_of_product == RULING_INDEX and TITLE_OF_RULINGS in titles:
                handler(file_name, A_RULINGS_TITLE, TOOL_ID, RULING_ENTITIES)
                return True
            else:
                print("File '{file_name}' is incompatible with indexed".format(file_name=os.path.basename(file_name)))
                return False
        else:
            print("The file '{file_name}' does not exist !".format(file_name=os.path.basename(file_name)))
            return False


def main():
    parser = argparse.ArgumentParser(description="index data to elastic")
    parser.add_argument('--file', metavar='files', required=True, nargs='+', help="documents file")
    parser.add_argument('--index', type=str, required=True, help="type of index: 'supreme_court_rulings' ")
    args = parser.parse_args()
    check_index(files_to_read=args.file, index_of_product=args.index)
