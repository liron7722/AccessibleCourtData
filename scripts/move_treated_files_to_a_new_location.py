import shutil
from relative_path import *

FAILURE_FOLDER = "products/unhandled_json_products"
SUCCESS_FOLDER = "products/upload_json_to_elastic"


def move_to_a_new_location(file, status):
    if(status):
        shutil.move(file, get_path(SUCCESS_FOLDER))
    else:
        shutil.move(file, get_path(FAILURE_FOLDER))

