import os
from dotenv import load_dotenv

from pymongo import AsyncMongoClient

load_dotenv()

class MongoDBConnector:
    def __init__(self):
        self.client: AsyncMongoClient = AsyncMongoClient(os.getenv("MONGO_URI"))