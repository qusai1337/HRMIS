from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["hrm_database"]
collection = db["incident_reports"]

result = collection.update_many(
    {"incident_details.date": "string"},
    {"$set": {"incident_details.date": "2024-03-01 00:00:00"}}
)

print(f"✅ Fixed {result.modified_count} documents.")
