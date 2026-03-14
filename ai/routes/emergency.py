import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows any frontend to connect
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- IMPORT CORRECTIONS ---
# Adding current directory to path to ensure 'services' folder is visible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.triageAI import analyze_emergency
from services.firstAidAI import get_first_aid_advice
from services.qlearning import HackathonAllocator  # Import the Class
from services.doctorAllocator import assign_doctor

# Initialize the RL Engine once at startup
# This allows the weights (W_LOAD, W_DIST) to adapt over time
engine = HackathonAllocator()

class EmergencyReport(BaseModel):
    message: str
    location: List[float]  # [x, y]

# =============================
# PERSISTENT DATA (DATABASE MOCK)
# =============================
hospitals_db = [
    {
        "name": "City Hospital", 
        "x": 10, "y": 10, 
        "beds_available": 5, "total_beds": 10, 
        "doctor_experience": 0.9,
        "specializations": ["cardiology"],
        "ambulance_available": 2
    },
    {
        "name": "Metro Hospital", 
        "x": 2, "y": 2, 
        "beds_available": 1, "total_beds": 10, 
        "doctor_experience": 0.7,
        "specializations": ["cardiology"],
        "ambulance_available": 1
    }
]

doctors_db = [
    {"name": "Dr Mehta", "specialization": "cardiology", "experienceLevel": "Senior", "available": True},
    {"name": "Dr Sharma", "specialization": "cardiology", "experienceLevel": "Junior", "available": True}
]

# =============================
# THE EMERGENCY ROUTE
# =============================

@app.post("/report")
async def report_emergency(report: EmergencyReport):
    # Step 1: AI Triage
    triage = await analyze_emergency(report.message)
    if "error" in triage:
        raise HTTPException(status_code=500, detail="AI Triage Service Offline")

    # Step 2: Hospital Allocation (The Corrected Logic)
    # The engine expects a list of patients for batch processing
    patient_data = [{"id": "current_patient", "loc": report.location}]
    
    # Run the RL-based allocation
    assignment_results = engine.allocate_batch(hospitals_db, patient_data)
    best_assignment = assignment_results[0]

    if "❌" in best_assignment["assigned_to"]:
        raise HTTPException(status_code=503, detail="System Overloaded: No Beds Available")

    # Find the assigned hospital object in our DB to get coordinates/status
    hospital_obj = next(h for h in hospitals_db if h["name"] == best_assignment["assigned_to"])

    # Step 3: Doctor Allocation
    # Use specialization from AI and severity to find the right level
    doctor = assign_doctor(
        doctors_db, 
        triage.get("required_specialization", "general").lower(), # Case-insensitive
        triage.get("severity_score", 5)
    )

    # Step 4: First Aid Advice
    first_aid = await get_first_aid_advice(triage.get("symptoms", []))

    # Step 5: Mark Doctor as busy (State Persistence)
    if doctor and isinstance(doctor, dict):
        doctor["available"] = False
        # Get doctor ID (fallback to name-based ID if missing)
        doc_id = doctor.get("id", f"doc_{doctor['name'].replace(' ', '_').lower()}")
    else:
        doc_id = "staff_assigned"

    # FINAL RESPONSE (Updated to match frontend ID requirements)
    return {
        "hospitalId": best_assignment.get("hospitalId"),
        "doctorId": doc_id,
        "ambulanceId": best_assignment.get("ambulanceId")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)