from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

DB_URI = "mongodb+srv://ACD:FX6xH18gcFXX0W5U@accessiblecourtdata-vu2ls.mongodb.net/test?retryWrites=true&w=majority"


class DB:
    def __init__(self, logger=None):
        self.logger = logger
        self.client = MongoClient(DB_URI)
        self.get_connection()

    def get_connection(self):
        try:
            connection = self.client
            self.log('db establish connection')
        except ServerSelectionTimeoutError as _:
            message = 'db connection Timeout - check for if this machine ip is on whitelist'
            if self.logger is not None:
                self.logger.exception(message)
            else:
                print(message)
            connection = None
        return connection

    def getDB(self, dbName):
        db = self.client.get_database(dbName)
        self.log(f'got db: {dbName}')
        return db

    def getCollection(self, db, collectionName):
        collection = db.get_collection(collectionName)
        self.log(f'got collection: {collectionName}')
        return collection

    def log(self, message):
        if self.logger is not None:
            self.logger.info(message)
