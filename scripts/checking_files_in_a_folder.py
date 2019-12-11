import os
from move_treated_files_to_a_new_location import *
from index_data import *

UNHANDLED_CSV_PRODUCTS_PATH = "C:/Users/Administrator/Documents/AccessibleCourtData/products/unhandled_csv_products"


def Checking_files_in_a_folder():
    directory = os.path.join(UNHANDLED_CSV_PRODUCTS_PATH)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                ack = False
                while ack != True:
                    ack = check_index(files_to_read=file, index_of_product=RULING_INDEX)
                move_to_a_new_location(UNHANDLED_CSV_PRODUCTS_PATH + file)


if __name__ == '__main__':
    Checking_files_in_a_folder()