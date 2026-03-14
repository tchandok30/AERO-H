import numpy as np
import json

class HackathonAllocator:
    def __init__(self):
        self.W_DISTANCE = 0.35
        self.W_LOAD = 0.45
        self.W_EXP = 0.20
        self.W_AMB = 0.25
        self.LR = 0.01

    def calculate_score(self, hospital, patient_loc):
        dist = np.sqrt((hospital['x'] - patient_loc[0])**2 +
                       (hospital['y'] - patient_loc[1])**2)
        norm_dist = min(dist / 100, 1.0)
        load = 1 - (hospital['beds_available'] / hospital['total_beds'])
        ambulance_factor = 1 if hospital.get("ambulance_available", 0) > 0 else 0
        load_penalty = np.exp(load * 4) / 50

        score = (
            (self.W_EXP * hospital['doctor_experience'])
            + (self.W_AMB * ambulance_factor)
            - (self.W_DISTANCE * norm_dist)
            - (self.W_LOAD * load)
            - load_penalty
        )
        return score, load, norm_dist

    def update_weights(self, load, dist_norm):
        self.W_LOAD += self.LR * load
        self.W_DISTANCE += self.LR * dist_norm
        min_weight = 0.05
        total = self.W_DISTANCE + self.W_LOAD + self.W_EXP + self.W_AMB
        self.W_DISTANCE = max(min_weight, self.W_DISTANCE / total)
        self.W_LOAD = max(min_weight, self.W_LOAD / total)

    def allocate_batch(self, hospitals, patients):
        results = []
        for p in patients:
            best_hospital_idx = -1
            best_score = -float('inf')
            best_load = None
            best_dist_norm = None

            available_hospitals = [h for h in hospitals if h['beds_available'] > 0]
            if not available_hospitals:
                results.append({"error": "No beds available in region"})
                continue

            for i, h in enumerate(hospitals):
                if h['beds_available'] > 0:
                    score, load, norm_dist = self.calculate_score(h, p['loc'])
                    if score > best_score:
                        best_score = score
                        best_hospital_idx = i
                        best_load = load
                        best_dist_norm = norm_dist

            if best_hospital_idx != -1:
                target = hospitals[best_hospital_idx]
                target['beds_available'] -= 1
                
                # Assign IDs for the frontend
                # If your DB doesn't have IDs yet, it defaults to a generated string
                hospital_id = target.get("id", f"hosp_{target['name'].replace(' ', '_').lower()}")
                ambulance_id = target.get("ambulance_id", f"amb_{np.random.randint(1000, 9999)}")

                self.update_weights(best_load, best_dist_norm)

                # --- NEW JSON RETURN FORMAT ---
                results.append({
                    "hospitalId": hospital_id,
                    "ambulanceId": ambulance_id
                })

        return results

# =============================
# BACKEND SIMULATION (TEST)
# =============================
if __name__ == "__main__":
    hospitals_data = [
        {
            "id": "65fa21_city_hosp", # Mock MongoID
            "name": "City Hospital",
            "x": 1, "y": 1,
            "beds_available": 5, "total_beds": 10,
            "doctor_experience": 0.9,
            "ambulance_available": 1,
            "ambulance_id": "65fa88_amb_01"
        }
    ]

    patients_to_assign = [{"id": "P-101", "loc": [0, 0]}]

    engine = HackathonAllocator()
    assignments = engine.allocate_batch(hospitals_data, patients_to_assign)

    # Outputting raw JSON for the frontend team
    print(json.dumps(assignments[0], indent=2))