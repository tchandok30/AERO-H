import os
import google.generativeai as genai

# Configure your API Key
genai.configure(api_key="YOUR_GEMINI_API_KEY")

def get_first_aid_advice(symptoms):
    """
    Python version of the First Aid AI module.
    Takes symptoms (list or string) and returns clear, actionable bullet points.
    """
    
    # Initialize the model
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Ensure symptoms is a readable string
    symptoms_str = ", ".join(symptoms) if isinstance(symptoms, list) else symptoms

    prompt = f"""
    You are an emergency medical assistant.
    Provide immediate, short, and life-saving first aid advice based on the symptoms provided.
    
    Symptoms:
    {symptoms_str}

    Return the response as clear, concise bullet points only. 
    Keep it strictly medical and urgent.
    """

    try:
        # Generate content
        response = model.generate_content(prompt)
        advice = response.text.strip()
        
        # Fallback if AI returns empty or nonsense
        if not advice:
            return "• Stay calm.\n• Call emergency services immediately.\n• Monitor the patient's breathing."
            
        return advice
        
    except Exception as e:
        # Fallback in case of API issues
        return (
            "• Alert emergency responders immediately.\n"
            "• Ensure the patient is in a safe environment.\n"
            "• Do not give the patient anything to eat or drink until help arrives."
        )

# =============================
# QUICK TEST
# =============================
if __name__ == "__main__":
    test_symptoms = ["chest pain", "shortness of breath", "fainting"]
    print("--- FIRST AID ADVICE ---")
    print(get_first_aid_advice(test_symptoms))