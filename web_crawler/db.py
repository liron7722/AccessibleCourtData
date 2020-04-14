from pymongo import MongoClient
from config import DB_URI
from extra import readJson, get_path


class DB:
    def __init__(self):
        self.connection = MongoClient(DB_URI)

    def get_connection(self):
        return self.connection
