try:
	from flask_pymongo import PyMongo
	# Initialize the PyMongo instance
	mongo = PyMongo()
except Exception:
	# Fallback: try using pymongo directly (for environments without flask-pymongo)
	try:
		import pymongo

		class SimpleMongo:
			def __init__(self):
				self.client = None
				self.db = None

			def init_app(self, app):
				mongo_uri = app.config.get('MONGO_URI', 'mongodb+srv://darpanmeher1346_db_user:E8kreTF6Z8G5mFbn@cluster0.mhkyevr.mongodb.net/?retryWrites=true&w=majority')
				self.client = pymongo.MongoClient(mongo_uri)
				self.db = self.client.get_default_database()

		mongo = SimpleMongo()
	except Exception:
		# Last-resort dummy that raises helpful error at init time
		class DummyMongo:
			def init_app(self, app):
				raise RuntimeError('Missing pymongo or flask_pymongo. Please install dependencies or run inside the project venv.')

		mongo = DummyMongo()