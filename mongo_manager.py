import os
from typing import List, Dict
from pymongo import MongoClient
from loguru import logger


try:
    MONGODB_URI = os.environ['MONGODB_URI']
except KeyError as ke:
    logger.error(f'Missing environment variable: {ke}')


class MongoManager:
    def __init__(self):
        self._client = MongoClient(MONGODB_URI)
        self._db = self._client['imusic']
        self._collection = self._db['vinyl']

    def insert_vinyl_info(self, vinyl_info: List[Dict]):
        self._collection.insert_many(vinyl_info)


mongo = MongoManager()
