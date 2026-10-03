"""Worker profile parser."""

def parse_worker_profile(profile: dict) -> dict:
    """Parse legacy worker profile into deterministic schema."""
    writeup = profile.get("writeup", "").lower()
    
    # We build the skills ordered list starting empty (as assumed).
    skills = []
    
    if "excel" in writeup:
        skills.append("excel")
    if "crm" in writeup:
        skills.append("crm")
    if "customer" in writeup:
        skills.append("customer_support")
        
    return {
        "role": profile.get("job_title"),
        "city": profile.get("city"),
        "experience": profile.get("experience_years"),
        "skills": skills
    }
