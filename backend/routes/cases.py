from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel
from bson import ObjectId
from database import cases_collection, db
from datetime import datetime
import os

router = APIRouter()

# Collection لتخزين سجل التعديلات
status_history_collection = db.case_status_history

# Model لتعديل الحالة فقط
class UpdateCaseStatus(BaseModel):
    status: str

# ✅ إنشاء قضية (بملف مرفق اختياري)
@router.post("/cases")
async def create_case(
    title: str = Form(...),
    description: str = Form(...),
    violation_types: str = Form(...),
    status: str = Form("new"),
    priority: str = Form("medium"),
    country: str = Form(...),
    region: str = Form(...),
    date_occurred: str = Form(...),
    date_reported: str = Form(...),
    file: UploadFile = File(None)
):
    evidence = []

    # معالجة الملف فقط إذا كان فعلياً مرفوع ومش فاضي
    if file and file.filename != "":
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_location = f"{upload_dir}/{file.filename}"

        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)

        evidence.append({
            "type": "file",
            "url": file_location,
            "description": "Uploaded evidence"
        })

    new_case = {
        "title": title,
        "description": description,
        "violation_types": violation_types.split(","),
        "status": status,
        "priority": priority,
        "location": {
            "country": country,
            "region": region
        },
        "date_occurred": date_occurred,
        "date_reported": date_reported,
        "evidence": evidence,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = cases_collection.insert_one(new_case)
    return {"id": str(result.inserted_id), "message": "Case created (with or without file)"}

@router.get("/cases")
def get_cases(
    violation_type: str = Query(None),
    country: str = Query(None),
    from_date: str = Query(None),
    to_date: str = Query(None)
):
    query = {}

    if violation_type:
        query["violation_types"] = violation_type

    if country:
        query["location.country"] = country

    if from_date and to_date:
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            query["date_occurred"] = {"$gte": from_dt, "$lte": to_dt}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    cases = []
    for case in cases_collection.find(query):
        cases.append({
            "id": str(case["_id"]),
            "title": case["title"],
            "description": case["description"],
            "status": case.get("status", ""),
            "priority": case.get("priority", ""),
            "violation_types": case.get("violation_types", []),
            "location": case.get("location", {}),
        })

    return cases

@router.get("/cases/{case_id}")
def get_case(case_id: str):
    case = cases_collection.find_one({"_id": ObjectId(case_id)})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return {
        "id": str(case["_id"]),
        "title": case["title"],
        "description": case["description"],
        "status": case.get("status", ""),
        "priority": case.get("priority", ""),
        "violation_types": case.get("violation_types", []),
        "location": case.get("location", {}),
        "evidence": case.get("evidence", [])
    }

@router.patch("/cases/{case_id}")
def update_case_status(case_id: str, update: UpdateCaseStatus):
    result = cases_collection.update_one(
        {"_id": ObjectId(case_id)},
        {"$set": {"status": update.status, "updated_at": datetime.utcnow()}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Case not found")

    status_history_collection.insert_one({
        "case_id": ObjectId(case_id),
        "new_status": update.status,
        "timestamp": datetime.utcnow()
    })

    return {"message": "Case status updated", "new_status": update.status}

@router.delete("/cases/{case_id}")
def delete_case(case_id: str):
    result = cases_collection.delete_one({"_id": ObjectId(case_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"message": "Case deleted successfully"}
