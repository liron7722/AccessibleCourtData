import sys
sys.path.insert(1, './..')

import os
import shutil
import ntpath
from scripts.relative_path import *

FAILURE_FOLDER = "products/unhandled_json_products"
SUCCESS_FOLDER = "products/upload_json_to_elastic"


class Moving:
    _success = None
    _failure = None

    def __init__(self):
        self._success_path = get_path(SUCCESS_FOLDER)
        self._failure_path = get_path(FAILURE_FOLDER)

    def move_to_a_new_location(self, file, status):
        if (status):
            self.success(file)
        else:
            self.failure(file)

    def success(self, file):
        shutil.move(file, os.path.join(self._success_path, ntpath.basename(file)))

    def failure(self, file):
        shutil.move(file, os.path.join(self._failure_path, ntpath.basename(file)))
