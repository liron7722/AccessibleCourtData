import shutil

DESTINATION_FOLDER = "C:/Users/Administrator/Documents/AccessibleCourtData/products/handled_csv_products"


def move_to_a_new_location(path):
    shutil.move(path, DESTINATION_FOLDER)
