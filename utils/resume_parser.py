import re
from typing import Dict, Any, List
from io import BytesIO
from datetime import datetime
import PyPDF2


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts raw text from a PDF file in bytes using PyPDF2."""
    try:
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"


def parse_resume(raw_text: str) -> Dict[str, Any]:
    """
    Parses resume text and extracts candidate name, skills, projects,
    education, and estimated gap/grace years.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    
    # 1. Candidate Name (usually in the first 3 lines)
    candidate_name = "Candidate"
    for line in lines[:5]:
        # Skip lines that look like emails, URLs, or phone numbers
        if "@" in line or "http" in line or re.search(r"\d{5,}", line):
            continue
        cleaned = re.sub(r"[^a-zA-Z\s]", "", line).strip()
        words = cleaned.split()
        if 1 <= len(words) <= 4 and all(w.istitle() or w.isupper() for w in words):
            candidate_name = cleaned
            break

    # 2. Extract Email & Phone
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_text)
    email = email_match.group(0) if email_match else "Not specified"

    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", raw_text)
    phone = phone_match.group(0) if phone_match else "Not specified"

    # 3. Known Skills Vocabulary Matching
    common_skills = [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "PHP",
        "React", "Vue", "Angular", "Next.js", "Node.js", "Express", "Django", "Flask",
        "FastAPI", "Spring Boot", "HTML", "CSS", "Tailwind", "Bootstrap",
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Firebase",
        "Git", "GitHub", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux",
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy",
        "Scikit-learn", "Data Science", "Computer Vision", "NLP", "LLM", "REST API",
        "GraphQL", "Microservices", "CI/CD", "Agile", "Scrum"
    ]
    detected_skills = []
    text_lower = raw_text.lower()
    for skill in common_skills:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            detected_skills.append(skill)

    # 4. Extract Project Mentions
    projects = []
    project_headers = ["projects", "personal projects", "academic projects", "key projects"]
    in_project_section = False
    current_proj = []

    for line in lines:
        lower_line = line.lower()
        if any(h in lower_line for h in project_headers) and len(line) < 40:
            in_project_section = True
            continue
        if in_project_section:
            # If hit another major section, stop
            if any(sec in lower_line for sec in ["education", "experience", "certifications", "skills", "achievements"]) and len(line) < 35:
                in_project_section = False
                break
            if line.startswith(("-", "•", "*", "–")) or len(line) > 10:
                current_proj.append(line)

    if current_proj:
        # Group or summarize
        projects_summary = "\n".join(current_proj[:12])
    else:
        # Fallback: scan for lines mentioning "project" or tech keywords
        candidates = [l for l in lines if any(w in l.lower() for w in ["developed", "built", "implemented", "created", "designed"])][:5]
        projects_summary = "\n".join(candidates) if candidates else "Projects extracted from full resume text."

    # 5. Extract Education & Detect Grace/Gap Years
    years = [int(y) for y in re.findall(r"\b(20[0-2][0-9]|19[8-9][0-9])\b", raw_text)]
    current_year = datetime.now().year
    
    graduation_year = None
    education_lines = []
    in_edu_section = False
    for line in lines:
        lower_line = line.lower()
        if "education" in lower_line or "academics" in lower_line:
            in_edu_section = True
            continue
        if in_edu_section:
            if any(sec in lower_line for sec in ["experience", "projects", "skills", "certifications"]) and len(line) < 35:
                in_edu_section = False
                break
            education_lines.append(line)

    # Calculate estimated gap / grace years
    # If student graduated before current year and has no recent experience, calculate gap
    grace_years = 0
    if years:
        # Recent years in the 2018-current range
        relevant_years = [y for y in years if 2015 <= y <= current_year]
        if relevant_years:
            latest_year = max(relevant_years)
            if current_year > latest_year:
                grace_years = max(0, current_year - latest_year)

    return {
        "candidate_name": candidate_name,
        "email": email,
        "phone": phone,
        "skills": detected_skills,
        "projects_summary": projects_summary,
        "education_summary": "\n".join(education_lines[:5]) if education_lines else "Education details from resume.",
        "detected_grace_years": grace_years,
        "raw_text": raw_text[:4000] # Cap for prompt safety
    }
