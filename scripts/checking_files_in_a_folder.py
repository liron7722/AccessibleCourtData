from scripts.move_treated_files_to_a_new_location import *
from scripts.index_data import *

UNHANDLED_CSV_PRODUCTS_PATH = "products\/unhandled_csv_products"
RULING_INDEX = 'rulings'
RULING_ENTITIES = 'supreme_court_rulings'


def Checking_files_in_a_folder():
    directory = get_path(UNHANDLED_CSV_PRODUCTS_PATH)
    print(directory)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                ack = False
                while ack != True:
                    ack = check_index(files_to_read=file, index_of_product=RULING_INDEX, id_of_product=RULING_ENTITIES)
                move_to_a_new_location(os.path.join(directory, file))


if __name__ == '__main__':
    Checking_files_in_a_folder()
