"""Worker Gemini analysis."""
import json
import re

from src.api.worker_engine.gemini_client import generate_text, mask_secrets, GeminiNotConfigured

SYSTEM_PROMPT = """You are an AI labor market expert analyzing a worker's vulnerability to automation. 
You will receive the worker's current job title, city, years of experience, and known skills.

You must estimate the risk of AI automation taking over this job (0 to 100).
- If the risk is very high (e.g., > 70), suggest pivot roles.
- If the risk is moderate, suggest additional skills.
- If the risk is low, reassure the worker.

Use this exact reasoning formula and explain each term in your explanation:
Risk = Base Risk + (Regional Adjustment x 0.1) - (Experience Reduction) + (Entry Penalty)

Rules for the formula:
- Base Risk: derive from the role's automation vulnerability.
- Regional Adjustment: your estimation.
- Experience Reduction: at most 25.
- Entry Penalty: exactly 15 if the years of experience is under 1 year, otherwise 0.

Pivot logic rules:
- If the job title represents a BPO profile, strictly steer the worker toward 'AI Content Moderation' roles.
- For other high-risk roles, steer them toward 'Data Analytics'.

You must reply ONLY with valid JSON matching this exact structure (no markdown formatting, no prose):
{
  "risk_score": <number 0-100>,
  "risk_level": "<high|moderate|low>",
  "pivot_roles": ["<role1>", "<role2>"],
  "new_skills": ["<skill1>", "<skill2>"],
  "explanation": "<your detailed reasoning string explaining the formula terms>"
}
"""

def analyze_worker(job_title: str, city: str, experience: float, skills: list[str]) -> dict:
    """Analyze worker vulnerability via Gemini."""
    skills_str = ", ".join(skills) if skills else "None provided"
    
    prompt = SYSTEM_PROMPT + f"\n\nUser Inputs:\nCurrent Job Title: {job_title}\nCity: {city}\nYears of Experience: {experience}\nKnown Skills: {skills_str}"
    
    try:
        raw_text = generate_text(prompt, "GEMINI_API_KEY_WORKERANALYSIS")
        
        # Greedy regex to extract JSON
        match = re.search(r'\{[\s\S]*\}', raw_text)
        if match:
            try:
                data = json.loads(match.group(0))
                return {
                    "risk_score": data.get("risk_score"),
                    "risk_level": data.get("risk_level", "unknown"),
                    "pivot_roles": data.get("pivot_roles", []),
                    "new_skills": data.get("new_skills", []),
                    "explanation": data.get("explanation", ""),
                    "raw_response": raw_text
                }
            except json.JSONDecodeError:
                pass
                
        # Parse failed or no JSON found
        return {
            "risk_score": None,
            "risk_level": "unknown",
            "pivot_roles": [],
            "new_skills": [],
            "explanation": raw_text,
            "raw_response": raw_text
        }
        
    except GeminiNotConfigured:
        return {
            "risk_score": None,
            "risk_level": "unknown",
            "pivot_roles": [],
            "new_skills": [],
            "explanation": "Gemini worker analysis is not configured. Set GEMINI_API_KEY_WORKERANALYSIS.",
            "raw_response": ""
        }
    except Exception as e:
        return {
            "risk_score": None,
            "risk_level": "unknown",
            "pivot_roles": [],
            "new_skills": [],
            "explanation": "Gemini request failed: " + mask_secrets(str(e)),
            "raw_response": ""
        }
