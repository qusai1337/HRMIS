from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017"
client = MongoClient(MONGO_URL)

db = client.hrm_database  # اسم قاعدة البيانات
cases_collection = db.cases  # جدول القضايا
