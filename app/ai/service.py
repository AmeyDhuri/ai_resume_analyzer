import requests


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
  response = requests.post("http://127.0.0.1:11434/api/generate", json={"model": "qwen2.5:0.5b", "prompt": prompt, "stream": False, "options": {"temperature": 0.3}}, timeout=300)
 
  data = response.json()

  return data["response"]

