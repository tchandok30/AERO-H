def assign_doctor(doctors, specialization, severity):
    """
    Python version of the Doctor Allocator.
    Filters doctors by specialization and availability, then selects 
    the best match based on patient severity.
    """
    
    # Step 1: Filter doctors by specialization and availability
    # Using list comprehension for efficiency
    filtered = [
        d for d in doctors 
        if d.get("specialization") == specialization and d.get("available") == True
    ]

    # If no doctors match the criteria, return None or a fallback
    if not filtered:
        return None

    # Step 2: Allocation logic based on severity
    if severity >= 8:
        # Try to find a Senior doctor first
        senior_doc = next((d for d in filtered if d.get("experienceLevel") == "Senior"), None)
        return senior_doc if senior_doc else filtered[0]

    # Step 3: Default/Lower severity logic
    # Try to find a Junior doctor first to save Senior resources for critical cases
    junior_doc = next((d for d in filtered if d.get("experienceLevel") == "Junior"), None)
    return junior_doc if junior_doc else filtered[0]

# =============================
# EXAMPLE TEST
# =============================
if __name__ == "__main__":
    doctors_db = [
        {"name": "Dr. Mehta", "specialization": "Cardiology", "experienceLevel": "Senior", "available": True},
        {"name": "Dr. Sharma", "specialization": "Cardiology", "experienceLevel": "Junior", "available": True},
        {"name": "Dr. Ray", "specialization": "Neurology", "experienceLevel": "Senior", "available": False},
    ]

    # Scenario: Critical Heart Issue (Severity 9)
    assigned = assign_doctor(doctors_db, "Cardiology", 9)
    print(f"Assigned for Critical Case: {assigned['name'] if assigned else 'No doctor available'}")

    # Scenario: Mild Issue (Severity 4)
    assigned_mild = assign_doctor(doctors_db, "Cardiology", 4)
    print(f"Assigned for Mild Case: {assigned_mild['name'] if assigned_mild else 'No doctor available'}")