from pymongo import MongoClient

DB_URI = "mongodb+srv://ACD:FX6xH18gcFXX0W5U@accessiblecourtdata-vu2ls.mongodb.net/test?retryWrites=true&w=majority"


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
