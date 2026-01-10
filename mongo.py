class MockCursor:
    """Mocks the MongoDB Cursor object to support chaining .sort()"""
    def __init__(self, data):
        self.data = data

    def sort(self, key, direction=-1):
        # Sort the data list in-place based on the key
        reverse = (direction == -1)
        self.data.sort(key=lambda x: x.get(key), reverse=reverse)
        return self.data

    def __iter__(self):
        return iter(self.data)

class MockCollection:
    """Mocks a MongoDB Collection (e.g., pickup_requests)"""
    def __init__(self):
        self.data = []

    def find(self, query=None):
        if query is None:
            query = {}
        
        # Simple mock filter: currently only supports filtering by user_id
        filtered_data = self.data
        if 'user_id' in query:
            filtered_data = [item for item in self.data if item.get('user_id') == query['user_id']]
        
        return MockCursor(filtered_data)

    def insert_one(self, document):
        self.data.append(document)
        return True

class MockPyMongo:
    """Mocks the main PyMongo object"""
    def __init__(self):
        self.db = type('MockDB', (), {'pickup_requests': MockCollection()})()

    def init_app(self, app):
        print("⚠️ RUNNING IN MOCK MODE: Data is stored in memory.")

# Initialize the Mock instance
mongo = MockPyMongo()