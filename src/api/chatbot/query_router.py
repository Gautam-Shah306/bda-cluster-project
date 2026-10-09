"""Chatbot query router."""
import json
from src.api.worker_engine.gemini_client import generate_text, mask_secrets, GeminiNotConfigured
from src.api.chatbot import sql_engine

RISK_KEYWORDS = [
    "risk score", "my risk", "risk level", "risk analysis", "risk assessment", 
    "ai risk", "automation risk", "vulnerability", "vulnerable", "at risk", 
    "job security", "will ai take", "replace my job", "replaced by ai", 
    "how risky", "explain my risk", "why is my risk", "jokhim", "mera risk", 
    "mera score", "risk kitna", "khatra"
]

IMPROVEMENT_KEYWORDS = [
    "improve", "reduce risk", "lower my risk", "career path", "career", "future", 
    "reskill", "upskill", "learning path", "learning", "course", "recommend", 
    "suggest", "timeline", "roadmap", "what should i learn", "what to learn", 
    "new skill", "skills to learn", "pivot", "switch", "transition", "next step", 
    "guidance", "advice", "path", "kya seekhu", "kya sikhu", "kaise improve", 
    "sudhar", "aage badhna"
]

LANGUAGE_RULE = "Reply entirely in the same language as the user's question (English or Hindi), never mixing them."

def classify_intent(question: str) -> str:
    """Classify the user intent based on keywords."""
    question_lower = question.lower()
    
    for kw in IMPROVEMENT_KEYWORDS:
        if kw in question_lower:
            return "improvement_guidance"
            
    for kw in RISK_KEYWORDS:
        if kw in question_lower:
            return "risk_explanation"
            
    return "data_query"

def ask_gemini(prompt: str) -> str:
    """Wrapper to call Gemini and handle errors."""
    try:
        text = generate_text(prompt, None)
        if not text:
            return "No response text returned by Gemini."
        return text
    except GeminiNotConfigured:
        return "Gemini is not configured. Set GEMINI_API_KEY and try again."
    except Exception as exc:
        return "Gemini request failed: " + mask_secrets(str(exc))

def _handle_risk_intent(question: str, user_data: dict, worker_profile: dict) -> str:
    gemini_analysis = user_data.get("gemini_analysis")
    job_role = user_data.get("job_role")
    
    if not gemini_analysis or gemini_analysis.get("risk_score") is None:
        return "Please fill in the Worker Analysis page and click 'Analyze Risk & Opportunities' first."
        
    prompt = f"""You are a career guidance assistant. Answer using ONLY the analysis below. Never say you don't know.

Job Role: {job_role}
Risk Score: {gemini_analysis.get('risk_score', 'N/A')}/100
Risk Level: {gemini_analysis.get('risk_level', 'unknown')}
Explanation: {gemini_analysis.get('explanation', '')}
Pivot Roles: {gemini_analysis.get('pivot_roles', [])}
New Skills: {gemini_analysis.get('new_skills', [])}

Question: {question}

{LANGUAGE_RULE}"""

    return ask_gemini(prompt)

def _handle_improvement_intent(question: str, user_data: dict, worker_profile: dict) -> str:
    gemini_analysis = user_data.get("gemini_analysis") or {}
    reskilling_result = user_data.get("reskilling_result")
    
    if not gemini_analysis and not reskilling_result:
        return "Please submit the Worker Analysis profile and then click 'Generate Reskilling Path' first."
        
    prompt_parts = ["You are a career guidance assistant."]
    prompt_parts.append(f"User Job Role: {user_data.get('job_role', 'N/A')}")
    prompt_parts.append(f"User Skills: {user_data.get('skills', [])}")
    
    if gemini_analysis:
        prompt_parts.append("Risk Context:")
        prompt_parts.append(json.dumps({
            "risk_score": gemini_analysis.get("risk_score"),
            "risk_level": gemini_analysis.get("risk_level"),
            "explanation": gemini_analysis.get("explanation"),
            "pivot_roles": gemini_analysis.get("pivot_roles"),
            "new_skills": gemini_analysis.get("new_skills")
        }, ensure_ascii=False))
        
    if isinstance(reskilling_result, dict) and reskilling_result.get("recommendation_type"):
        prompt_parts.append("Reskilling Context:")
        prompt_parts.append(json.dumps({
            "recommendation_type": reskilling_result.get("recommendation_type"),
            "summary": reskilling_result.get("summary"),
            "recommended_skills": reskilling_result.get("recommended_skills"),
            "recommended_courses": reskilling_result.get("recommended_courses", [])[:8],
            "recommended_jobs": reskilling_result.get("recommended_jobs", [])[:8],
            "learning_path": reskilling_result.get("learning_path")
        }, ensure_ascii=False))
        
    prompt_parts.append(f"Question: {question}")
    prompt_parts.append(LANGUAGE_RULE)
    
    return ask_gemini("\n\n".join(prompt_parts))

def _handle_data_query(question: str, worker_profile: dict) -> str:
    sql_prompt = f"""Convert the question into ONE read-only Spark SQL query.
Reply with ONLY the SQL, no markdown, no explanation.
Add LIMIT 100 unless the question asks for a count or an aggregate.
Compare strings case-insensitively with lower().

Tables available:
{sql_engine.schema_text()}

Note: A job's city is the trimmed text before the first comma in joblocation_address (e.g., trim(split(joblocation_address, ',')[0])); for any questions related to cities, you must filter or group using this expression rather than the full joblocation_address.

Question: {question}"""

    try:
        sql_text = generate_text(sql_prompt, None)
    except GeminiNotConfigured:
        return "Gemini is not configured. Set GEMINI_API_KEY and try again."
    except Exception as exc:
        return "Gemini request failed: " + mask_secrets(str(exc))
        
    sql = sql_engine.clean_sql(sql_text)
    if not sql_engine.validate_sql(sql):
        return "Query blocked due to safety restrictions."
        
    try:
        rows, total, more = sql_engine.run_query(sql)
    except PermissionError:
        return "Query blocked due to safety restrictions."
    except Exception as exc:
        return "Error processing query: " + mask_secrets(str(exc))[:500]
        
    if not rows:
        results_text = "No records found matching the criteria."
    else:
        raw_str = str(rows)[:3000]
        if more:
            results_text = f"Found more than 1000 results (showing top 20):\n{raw_str}"
        elif total > 20:
            results_text = f"Found {total} results (showing top 20):\n{raw_str}"
        else:
            results_text = raw_str

    answer_parts = ["Write a concise summary. Mention only existing data."]
    
    if isinstance(worker_profile, dict) and worker_profile:
        prof_str = json.dumps(worker_profile, ensure_ascii=False)[:2000]
        answer_parts.append(f"Worker Profile:\n{prof_str}")
        
    answer_parts.append(f"Question: {question}")
    answer_parts.append(f"Results:\n{results_text}")
    answer_parts.append(LANGUAGE_RULE)
    
    return ask_gemini("\n\n".join(answer_parts))

def handle_query(query: dict, user_data: dict | None) -> str:
    question = query.get("question", "")
    worker_profile = query.get("worker_profile") or {}
    
    user_data = user_data or {}
    
    intent = classify_intent(question)
    
    if intent == "risk_explanation":
        return _handle_risk_intent(question, user_data, worker_profile)
    elif intent == "improvement_guidance":
        return _handle_improvement_intent(question, user_data, worker_profile)
    else:
        return _handle_data_query(question, worker_profile)
