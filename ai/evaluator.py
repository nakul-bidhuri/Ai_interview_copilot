import json
from typing import Dict, Any, List, Optional
from ai.llm import call_llm
from ai.interviewer import clean_json_response


def evaluate_interview(
    candidate_name: str,
    target_role: str,
    target_company: str,
    experience_level: str,
    grace_years: int,
    resume_summary: str,
    transcript: List[Dict[str, Any]],
    api_key: Optional[str] = None,
    provider: str = "gemini"
) -> Dict[str, Any]:
    """
    Performs comprehensive post-interview evaluation across technical depth,
    communication clarity, confidence, problem solving, and gap-year handling.
    Generates actionable feedback, model answers, and improvement guidelines.
    """
    system_instruction = (
        "You are an Elite Executive Hiring Director and Career Coach who has evaluated thousands "
        "of candidates for top global tech companies. Provide a rigorous, constructive, and highly "
        "motivating post-interview evaluation report for a student candidate. "
        "Your feedback must be practical, specific, and teach the student how to put up answers "
        "effectively, deal with tough interviewers, and tackle grace/gap years with total confidence. "
        "Always output strict valid JSON only."
    )

    # Format transcript for prompt
    transcript_text = ""
    for idx, item in enumerate(transcript, 1):
        q = item.get("question", "")
        a = item.get("answer", "(No answer provided / Skipped)")
        transcript_text += f"\n[Question {idx}]: {q}\n[Candidate Answer]: {a}\n"

    prompt = f"""
EVALUATE THIS COMPLETED MOCK INTERVIEW:

CANDIDATE: {candidate_name}
TARGET ROLE: {target_role}
TARGET COMPANY: {target_company or 'Tech Industry Standard'}
EXPERIENCE LEVEL: {experience_level}
GRACE / CAREER GAP YEARS: {grace_years} year(s)
RESUME HIGHLIGHTS:
{resume_summary}

FULL INTERVIEW TRANSCRIPT:
{transcript_text}

PROVIDE A COMPREHENSIVE EVALUATION WITH THE FOLLOWING JSON STRUCTURE:
{{
  "overall_score": 8.0,
  "readiness_verdict": "Interview Ready / Needs Targeted Polish / Foundation Stage",
  "scores": {{
    "technical_depth": 7.8,
    "communication_clarity": 8.2,
    "confidence_delivery": 7.5,
    "problem_solving": 8.0,
    "star_method_alignment": 7.0
  }},
  "top_strengths": [
    "Specific strength 1 with exact example from transcript",
    "Specific strength 2",
    "Specific strength 3"
  ],
  "critical_areas_for_improvement": [
    "Specific improvement 1 explaining why it matters to interviewers",
    "Specific improvement 2",
    "Specific improvement 3"
  ],
  "grace_years_coaching": {{
    "analysis": "How the candidate handled or should handle their {grace_years} grace/gap year(s)",
    "power_statement": "The exact script the student should say when asked about gap/grace years",
    "dos_and_donts": [
      "DO: Focus on independent projects, certifications, and consistency",
      "DON'T: Sound apologetic or defensive"
    ]
  }},
  "questions_review": [
    {{
      "question": "Question text...",
      "candidate_answer_summary": "Summary of what student said...",
      "score": 8.0,
      "feedback": "Constructive feedback on what was good and what was lacking...",
      "model_answer": "A pristine, professional 3-4 sentence model answer showing how to put up this answer to impress the interviewer"
    }}
  ],
  "interviewer_masterclass_tips": [
    "How to deal with questions when you don't know the exact answer",
    "How to structure technical explanations using top-down hierarchy",
    "How to manage pacing, tone, and active listening"
  ],
  "actionable_next_steps": [
    "Immediate step 1 to take within 24 hours",
    "Immediate step 2",
    "Immediate step 3"
  ]
}}
"""

    raw_response = call_llm(
        prompt=prompt,
        system_instruction=system_instruction,
        api_key=api_key,
        provider=provider,
        temperature=0.5
    )

    try:
        cleaned = clean_json_response(raw_response)
        eval_data = json.loads(cleaned)
        if "overall_score" in eval_data and "scores" in eval_data:
            return eval_data
    except Exception as e:
        print(f"[Evaluator Warning] JSON parse failed: {e}. Raw: {raw_response[:200]}")

    # Fallback simulation
    from ai.llm import simulate_response
    fallback_sim = simulate_response("evaluate score report", system_instruction)
    return json.loads(clean_json_response(fallback_sim))
