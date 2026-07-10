import requests
from flask import current_app

def generate_ai_feedback(resume_text):
  prompt = f"""
  You are an ATS resume reviewer.

  Analyze this resume carefully.

  Only mention weaknesses or missing skills if they are genuinely absent.

  Do NOT suggest technologies already mentioned in the resume.

  Keep feedback concise and professional.

  Respond ONLY in this format:

  ## Strengths
  - bullet points

  ## Weaknesses
  - bullet points

  ## Missing Skills
  - bullet points

  ## ATS Tips
  - bullet points

  ## Improvements
  - bullet points

  Resume:
  {resume_text[:700]}
  """
  try:
    response = requests.post( current_app.config["OLLAMA_API_URL"] + "/api/generate", json={"model": current_app.config["OLLAMA_MODEL"], "prompt": prompt, "stream": False, "options": {"temperature": 0.3}}, timeout=300)
    print("Status Code:", response.status_code)
    print("Response:", response.text)

    response.raise_for_status()

    data = response.json()

    return data.get("response", "No response returned.")
  
  except Exception as e:
        print("OLLAMA ERROR:", e)
        raise
