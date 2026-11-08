import json
import re
from typing import Dict, Any, List, Optional
from ai.llm import call_llm


def clean_json_response(raw_text: str) -> str:
    """Extracts JSON substring from markdown code blocks or raw text."""
    # Look for ```json ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
    if match:
        return match.group(1).strip()
    # Otherwise look for outermost { ... }
    match_braces = re.search(r"(\{[\s\S]*\})", raw_text)
    if match_braces:
        return match_braces.group(1).strip()
    return raw_text.strip()


def generate_interview_plan(
    resume_data: Dict[str, Any],
    target_role: str,
    target_company: str = "",
    experience_level: str = "Fresher / College Student",
    grace_years: int = 0,
    persona: str = "Professional & Encouraging Tech Lead",
    num_questions: int = 5,
    api_key: Optional[str] = None,
    provider: str = "gemini"
) -> Dict[str, Any]:
    """
    Analyzes candidate's resume and generates a custom tailored interview plan,
    focusing on their specific projects, skills, and constructive handling of grace/gap years.
    """
    candidate_name = resume_data.get("candidate_name", "Candidate")
    skills = ", ".join(resume_data.get("skills", [])) or "General Software Development"
    projects = resume_data.get("projects_summary", "Projects detailed in resume")
    education = resume_data.get("education_summary", "Undergraduate Degree")
    detected_grace = grace_years or resume_data.get("detected_grace_years", 0)

    system_instruction = (
        f"You are {persona}, conducting a high-impact mock technical and HR interview for a student "
        f"applying for the position of '{target_role}' at '{target_company or 'a top tech company'}'. "
        "Your mission is to help this student prepare thoroughly, overcome interview nervousness, "
        "and learn how to articulate their resume projects and any career gaps/grace years with confidence. "
        "Always respond in valid, parseable JSON only."
    )

    prompt = f"""
Analyze this candidate's profile and create an interview plan of exactly {num_questions} questions.

CANDIDATE PROFILE:
- Name: {candidate_name}
- Target Role: {target_role}
- Target Company: {target_company or 'General Tech Firm'}
- Experience Level: {experience_level}
- Grace / Career Gap Years: {detected_grace} year(s)
- Extracted Skills: {skills}
- Education: {education}
- Resume Projects & Highlights:
{projects}

REQUIREMENTS:
1. Generate exactly {num_questions} tailored questions:
   - Question 1: Professional Introduction / Elevator Pitch (tailored to student background).
   - Question 2: Deep dive into one of their specific resume projects (architecture, technical decisions, challenges).
   - Question 3: Core technical skill question directly tied to their skills and target role.
   - Question 4: Behavioral question that touches upon handling challenges, self-motivation, or explaining grace/gap periods constructively.
   - Question 5: Problem-solving / situational scenario they would encounter at work.
2. For each question, provide:
   - id (1 to {num_questions})
   - type (e.g. Introduction, Project Deep Dive, Technical, Behavioral, Scenario)
   - question (conversational, direct question ready for audio/walkie-talkie speech)
   - focus (what the interviewer evaluates)
   - hint_for_candidate (practical advice on how to structure a winning answer)

FORMAT OUTPUT AS STRICT JSON WITH THIS STRUCTURE:
{{
  "candidate_profile_summary": "...",
  "detected_grace_years_analysis": "...",
  "questions": [
    {{
      "id": 1,
      "type": "...",
      "question": "...",
      "focus": "...",
      "hint_for_candidate": "..."
    }}
  ]
}}
"""

    raw_response = call_llm(
        prompt=prompt,
        system_instruction=system_instruction,
        api_key=api_key,
        provider=provider,
        temperature=0.6
    )

    try:
        cleaned = clean_json_response(raw_response)
        plan_data = json.loads(cleaned)
        if "questions" in plan_data and isinstance(plan_data["questions"], list):
            return plan_data
    except Exception as e:
        print(f"[Interviewer Warning] JSON parse failed: {e}. Raw: {raw_response[:200]}")

    # Fallback simulation if parsing failed
    from ai.llm import simulate_response
    fallback_sim = simulate_response("generate interview questions", system_instruction)
    return json.loads(clean_json_response(fallback_sim))


def generate_walkie_reaction(
    candidate_name: str,
    question: str,
    candidate_answer: str,
    persona: str = "Professional & Encouraging Tech Lead",
    question_idx: int = 1,
    total_questions: int = 5,
    api_key: Optional[str] = None,
    provider: str = "gemini"
) -> Dict[str, str]:
    """
    Generates a realistic, natural conversational reaction from the interviewer in Walkie-Talkie mode.
    Acknowledges the candidate's answer, provides immediate encouragement, and transitions to the next step.
    """
    if not candidate_answer or len(candidate_answer.strip()) < 10:
        return {
            "greeting_reaction": "I noticed that was quite brief. In a real interview, feel free to elaborate with specific examples and technical depth.",
            "follow_up_note": "Don't hesitate to share more context about your projects and thoughts.",
            "transition": "Let's proceed to the next question so you can practice expanding your answers."
        }

    system_instruction = (
        f"You are {persona} conducting a voice walkie-talkie interview. "
        "Provide a concise, authentic, professional reaction (2-3 sentences) to the student's spoken answer. "
        "Sound conversational and human. Output strict JSON only."
    )

    prompt = f"""
The candidate {candidate_name} just answered Question {question_idx} of {total_questions}.

QUESTION ASKED:
"{question}"

CANDIDATE SPOKEN ANSWER:
"{candidate_answer}"

Generate a short walkie-talkie audio reaction:
1. "greeting_reaction": Warm verbal acknowledgment (e.g. "Thank you, {candidate_name}! That's a solid point regarding...", or "Great breakdown of the technical challenge...")
2. "follow_up_note": 1 constructive observation on what was good or what to keep in mind.
3. "transition": Smooth verbal segue to the next question or interview wrap-up.

OUTPUT FORMAT:
{{
  "greeting_reaction": "...",
  "follow_up_note": "...",
  "transition": "..."
}}
"""

    raw_response = call_llm(
        prompt=prompt,
        system_instruction=system_instruction,
        api_key=api_key,
        provider=provider,
        temperature=0.7
    )

    try:
        cleaned = clean_json_response(raw_response)
        data = json.loads(cleaned)
        if "greeting_reaction" in data:
            return data
    except Exception:
        pass

    return {
        "greeting_reaction": f"Thank you, {candidate_name}. You addressed the key aspects clearly.",
        "follow_up_note": "Clear communication and structure make a great impression on hiring managers.",
        "transition": "Let's move ahead to the next question."
    }
