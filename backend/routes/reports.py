from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from database import db
from pydantic import BaseModel

router = APIRouter()
reports_collection = db.incident_reports

class StatusUpdate(BaseModel):
    status: str


# ✅ POST - Create Report
@router.post("/reports/")
async def create_report(
    reporter_type: str = Form(...),
    anonymous: bool = Form(...),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    preferred_contact: Optional[str] = Form(None),
    date: str = Form(...),
    country: str = Form(...),
    city: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    description: str = Form(...),
    violation_types: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    location = {
        "country": country,
        "city": city,
        "coordinates": {
            "type": "Point",
            "coordinates": [longitude, latitude]
        }
    }

    evidence = []
    if file:
        evidence.append({
            "type": file.content_type,
            "url": f"/evidence/{file.filename}",
            "description": "Uploaded evidence"
        })

    report_doc = {
        "reporter_type": reporter_type,
        "anonymous": anonymous,
        "contact_info": {
            "email": email if not anonymous else None,
            "phone": phone if not anonymous else None,
            "preferred_contact": preferred_contact if not anonymous else None
        },
        "incident_details": {
            "date": datetime.strptime(date, "%Y-%m-%d"),
            "location": location,
            "description": description,
            "violation_types": violation_types.split(",")
        },
        "evidence": evidence,
        "status": "new",
        "created_at": datetime.utcnow()
    }

    result = reports_collection.insert_one(report_doc)
    return {"id": str(result.inserted_id), "message": "Report submitted"}


# GET - List reports with filters
@router.get("/reports/")
async def list_reports(
    status: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None)
):
    query = {}

    if status:
        query["status"] = status
    if country:
        query["incident_details.location.country"] = country
    if city:
        query["incident_details.location.city"] = city
    if from_date and to_date:
        try:
            query["incident_details.date"] = {
                "$gte": datetime.strptime(from_date, "%Y-%m-%d"),
                "$lte": datetime.strptime(to_date, "%Y-%m-%d")
            }
        except:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    try:
        reports = list(reports_collection.find(query))
        cleaned = []
        for report in reports:
            cleaned.append({
                "id": str(report["_id"]),
                "reporter_type": report.get("reporter_type"),
                "anonymous": report.get("anonymous"),
                "status": report.get("status"),
                "city": report.get("incident_details", {}).get("location", {}).get("city"),
                "country": report.get("incident_details", {}).get("location", {}).get("country"),
                "description": report.get("incident_details", {}).get("description"),
                "violation_types": report.get("incident_details", {}).get("violation_types", []),
                "created_at": str(report.get("created_at"))
            })
        return cleaned
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/reports/{report_id}")
async def update_report_status(report_id: str, update: StatusUpdate):
    result = reports_collection.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": {"status": update.status}}
    )
    if result.modified_count == 1:
        return {"message": "Report status updated"}
    raise HTTPException(status_code=404, detail="Report not found")
