from scripts.move_treated_files_to_a_new_location import *
from scripts.index_data import *

UNHANDLED_CSV_PRODUCTS_PATH = "products\/unhandled_csv_products"


def Checking_files_in_a_folder():
    directory = get_path(UNHANDLED_CSV_PRODUCTS_PATH)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                ack = False
                while ack is not True:
                    ack = check_index(file_name=file)
                move_to_a_new_location(os.path.join(directory, file))


if __name__ == '__main__':
    Checking_files_in_a_folder()
