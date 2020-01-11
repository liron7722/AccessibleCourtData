import shutil
from scripts.relative_path import *

DESTINATION_FOLDER = "products\handled_csv_products"


def move_to_a_new_location(file):
    shutil.move(file, get_path(DESTINATION_FOLDER))

