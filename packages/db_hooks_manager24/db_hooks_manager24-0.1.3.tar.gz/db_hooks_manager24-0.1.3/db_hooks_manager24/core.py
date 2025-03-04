import importlib


class DatabaseManager:
    def __init__(self, db_type="mongodb", connection_string=None):
        self.db_type = db_type
        self.connection_string = connection_string
        self.db_client = None

        if db_type == "mongodb":
            if importlib.util.find_spec("pymongo") is None:
                raise ImportError(
                    "pymongo is required for MongoDB support. Install with 'pip install db_manager[mongodb]'")
            from pymongo import MongoClient
            self.db_client = MongoClient(connection_string)

    def get_client(self):
        if not self.db_client:
            raise ValueError("Database client is not initialized")
        return self.db_client
