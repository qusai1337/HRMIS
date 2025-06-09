from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId
from database import db
from datetime import datetime

router = APIRouter()


class RiskAssessment(BaseModel):
    level: str  # e.g., "low", "medium", "high"
    threats: List[str]
    protection_needed: bool

class SupportService(BaseModel):
    type: str
    provider: str
    status: str

class VictimBase(BaseModel):
    type: str  # "victim" or "witness"
    anonymous: bool
    gender: Optional[str]
    age: Optional[int]
    ethnicity: Optional[str]
    occupation: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    secure_messaging: Optional[str]
    risk_assessment: RiskAssessment
    support_services: List[SupportService] = []
    cases_involved: List[str]  # list of case ObjectId strings

class RiskUpdate(BaseModel):
    level: str  # new risk level


@router.post("/victims/")
async def add_victim(victim: VictimBase):
    data = {
        "type": victim.type,
        "anonymous": victim.anonymous,
        "demographics": {
            "gender": victim.gender,
            "age": victim.age,
            "ethnicity": victim.ethnicity,
            "occupation": victim.occupation
        },
        "contact_info": {
            "email": victim.email,
            "phone": victim.phone,
            "secure_messaging": victim.secure_messaging
        },
        "risk_assessment": victim.risk_assessment.dict(),
        "support_services": [s.dict() for s in victim.support_services],
        "cases_involved": [ObjectId(cid) for cid in victim.cases_involved],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = db.victims.insert_one(data)
    return {"id": str(result.inserted_id), "message": "Victim added successfully"}


@router.get("/victims/{victim_id}")
async def get_victim(victim_id: str):
    try:
        victim = db.victims.find_one({"_id": ObjectId(victim_id)})
        if not victim:
            raise HTTPException(status_code=404, detail="Victim not found")
        victim["_id"] = str(victim["_id"])
        victim["cases_involved"] = [str(cid) for cid in victim["cases_involved"]]
        return victim
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


@router.patch("/victims/{victim_id}")
async def update_risk_level(victim_id: str, data: RiskUpdate):
    result = db.victims.update_one(
        {"_id": ObjectId(victim_id)},
        {"$set": {"risk_assessment.level": data.level, "updated_at": datetime.utcnow()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Victim not found or no changes made")
    return {"message": "Risk level updated"}


@router.get("/victims/case/{case_id}")
async def list_victims_by_case(case_id: str):
    try:
        victims = db.victims.find({"cases_involved": ObjectId(case_id)})
        return [{
            "_id": str(v["_id"]),
            "type": v["type"],
            "risk": v["risk_assessment"]["level"]
        } for v in victims]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
