from move_treated_files_to_a_new_location import *
from index_data import *

HANDLED_JSON_PRODUCTS_PATH = "products/handled_json_products"


def Checking_files_in_a_folder():
    directory = get_path(HANDLED_JSON_PRODUCTS_PATH)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                ack = False
                retry = 0;
                while ack is not True and retry <= 2: 
                    ack = check_index(file_path=HANDLED_JSON_PRODUCTS_PATH, file_name=file)
                    retry += 1    
                move_to_a_new_location(os.path.join(directory, file), ack)


if __name__ == '__main__':
    Checking_files_in_a_folder()
