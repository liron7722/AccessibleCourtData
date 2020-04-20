from pymongo import MongoClient
from ILCourtScraper.Extra.config import DB_URI


class DB:
    def __init__(self, logger=None):
        self.logger = logger
        self.connection = MongoClient(DB_URI)
        self.log('db establish connection')

    def get_connection(self):
        connection = self.connection
        return connection

    def getDB(self, dbName):
        db = self.connection.get_database(dbName)
        self.log(f'got db: {dbName}')
        return db

    def getCollection(self, db, collectionName):
        collection = db.get_collection(collectionName)
        self.log(f'got collection: {collectionName}')
        return collection

    def log(self, message):
        if self.logger is not None:
            self.logger.info(message)
