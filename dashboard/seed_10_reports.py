from pymongo import MongoClient
from datetime import datetime, timedelta
import random

client = MongoClient("mongodb://localhost:27017/")
db = client["hrm_database"]
collection = db["incident_reports"]

countries = ["Palestine", "Syria", "Iraq", "Lebanon", "Yemen"]
cities = {
    "Palestine": "Gaza",
    "Syria": "Aleppo",
    "Iraq": "Baghdad",
    "Lebanon": "Beirut",
    "Yemen": "Sana'a"
}
violations_list = [
    "Torture",
    "Arbitrary Arrest",
    "Forced Displacement",
    "Unlawful Killing",
    "Enforced Disappearance"
]

reports = []

for i in range(10):
    country = random.choice(countries)
    city = cities[country]
    violation_count = random.randint(1, 3)
    selected_violations = random.sample(violations_list, k=violation_count)

    date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 150))
    date_str = date.strftime("%Y-%m-%d 00:00:00")

    report = {
        "incident_details": {
            "date": date_str,
            "violation_types": selected_violations,
            "location": {
                "country": country,
                "city": city,
                "coordinates": {
                    "type": "Point",
                    "coordinates": [
                        round(random.uniform(30.0, 40.0), 4),
                        round(random.uniform(30.0, 36.0), 4)
                    ]
                }
            },
            "description": f"{random.choice(selected_violations)} incident reported in {city}."
        },
        "reporter_type": random.choice(["individual", "organization"]),
        "anonymous": random.choice([True, False]),
        "evidence_ids": [],
        "status": random.choice(["new", "under_review", "resolved"]),
        "created_at": datetime.now().isoformat()
    }

    reports.append(report)

collection.insert_many(reports)
print("✅ 10 reports inserted successfully.")
