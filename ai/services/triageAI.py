import os
import json
import google.generativeai as genai

# Configure your API Key
# In a hackathon, you can use: os.getenv("GEMINI_API_KEY") 
genai.configure(api_key="YOUR_GEMINI_API_KEY")

def analyze_emergency(message):
    """
    Python version of the Triage AI module.
    Analyzes patient messages and returns structured JSON.
    """
    
    # Initialize the model
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    You are an emergency medical triage assistant.
    Extract structured information from the patient message.
    
    Return JSON ONLY with these fields:
    - severity_score (1-10)
    - priority (low, medium, high, critical)
    - symptoms (array)
    - required_specialization
    - possible_condition

    Message:
    "{message}"
    """

    try:
        # Generate content
        response = model.generate_content(prompt)
        text = response.text
        
        # CLEANUP: Remove markdown formatting if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        # Parse and return
        return json.loads(text)
        
    except Exception as e:
        # Fallback in case of AI failure or parsing error
        return {
            "error": "AI parsing failed",
            "details": str(e),
            "severity_score": 5,  # Default to medium if error
            "priority": "medium",
            "symptoms": [],
            "required_specialization": "general",
            "possible_condition": "unknown"
        }

# =============================
# QUICK TEST
# =============================
if __name__ == "__main__":
    test_message = "My chest feels very tight and I am struggling to breathe."
    result = analyze_emergency(test_message)
    print(json.dumps(result, indent=4))