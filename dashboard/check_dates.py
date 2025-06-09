from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["hrm_database"]
collection = db["incident_reports"]

cursor = collection.find({}, {"incident_details.date": 1})

print("📋 Existing `incident_details.date` values:")
for doc in cursor:
    date = doc.get("incident_details", {}).get("date", "⛔️ Not Found")
    print(f"• {date}")
