import os
import json
import re
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

# Automatically load .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


def get_configured_api_key(provider: str = "gemini") -> Optional[str]:
    """Retrieves API key for the requested provider from environment or .env."""
    if provider.lower() == "gemini":
        return os.getenv("GEMINI_API_KEY")
    elif provider.lower() in ("openai", "groq"):
        return os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
    return None


def call_llm(
    prompt: str,
    system_instruction: str = "You are an expert AI Technical and HR Interviewer.",
    api_key: Optional[str] = None,
    provider: str = "gemini",
    model_name: Optional[str] = None,
    temperature: float = 0.7
) -> str:
    """
    Unified LLM call supporting Google Gemini and OpenAI-compatible endpoints,
    with an intelligent fallback simulator when no API key is provided or models are busy.
    """
    active_key = api_key or get_configured_api_key(provider)

    # 1. Google Gemini Provider
    if provider.lower() == "gemini" and active_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=active_key)
            
            # List of models to try in order of availability and speed
            candidate_models = [model_name] if model_name else [
                "gemini-3.1-flash-lite",
                "gemini-3.8-flash",
                "gemini-flash-latest"
            ]

            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
            )

            last_error = None
            for model in candidate_models:
                if not model:
                    continue
                try:
                    response = client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=config
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as model_err:
                    last_error = model_err
                    continue

            if last_error:
                print(f"[LLM Warning] Gemini models failed: {last_error}. Falling back to simulation.")
        except Exception as e:
            print(f"[LLM Warning] Gemini initialization failed: {e}. Falling back to simulation.")

    # 2. OpenAI / Groq Provider
    elif provider.lower() in ("openai", "groq") and active_key:
        try:
            from openai import OpenAI
            base_url = "https://api.groq.com/openai/v1" if provider.lower() == "groq" else None
            client = OpenAI(api_key=active_key, base_url=base_url)
            model = model_name or ("llama-3.3-70b-versatile" if provider.lower() == "groq" else "gpt-4o-mini")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM Warning] OpenAI/Groq call failed: {e}. Falling back to simulation.")

    # 3. Intelligent Simulation Fallback (Offline / Free Mode)
    return simulate_response(prompt, system_instruction)


def simulate_response(prompt: str, system_instruction: str) -> str:
    """
    Realistic simulation engine when no API key is configured or services are offline.
    Generates structured, dynamic interview plans and detailed feedback.
    """
    prompt_lower = prompt.lower()

    # Case A: Generating Interview Questions from Resume
    if "generate" in prompt_lower and "questions" in prompt_lower:
        return json.dumps({
            "candidate_profile_summary": "Promising software engineering candidate with strong foundation in core programming, hands-on projects, and enthusiasm for scalable technology.",
            "detected_grace_years_analysis": "The candidate has a potential career transition / grace gap period. This will be explored constructively to highlight self-learning, freelancing, and personal discipline.",
            "questions": [
                {
                    "id": 1,
                    "type": "Introduction & Background",
                    "question": "Welcome! To start off, walk me through your background, your main areas of interest, and what motivated you to pursue this specific role.",
                    "focus": "Communication, clarity, professional self-introduction, and narrative.",
                    "hint_for_candidate": "Keep it under 90 seconds. Cover your education, top 1-2 skills, and what makes you passionate about this domain."
                },
                {
                    "id": 2,
                    "type": "Project Deep Dive",
                    "question": "In your resume, you highlighted your major project. Could you explain the high-level architecture, the key technical challenges you faced while building it, and how you solved them?",
                    "focus": "Technical ownership, problem-solving under constraints, design decisions.",
                    "hint_for_candidate": "Explain the 'Why' behind tech stack choices, a specific bottleneck you debugged, and measurable outcomes."
                },
                {
                    "id": 3,
                    "type": "Core Technical Competency",
                    "question": "Let's dive into core technical principles. When designing an application or handling data requests, how do you handle error states, edge cases, and ensure scalability under load?",
                    "focus": "System robustness, defensive programming, and understanding of scalability.",
                    "hint_for_candidate": "Mention try-catch patterns, input validation, logging, caching, and rate limiting."
                },
                {
                    "id": 4,
                    "type": "Behavioral & Grace/Gap Explanation",
                    "question": "Tell me about a time when you experienced a setback, a delay, or took time to upskill independently. How did you structure your time and stay accountable?",
                    "focus": "Resilience, self-motivation, turning grace/gap periods into productive learning stories.",
                    "hint_for_candidate": "Use the STAR method (Situation, Task, Action, Result). Emphasize discipline and self-directed projects."
                },
                {
                    "id": 5,
                    "type": "Scenario / Problem Solving",
                    "question": "Imagine you are assigned a critical production bug right before a deadline, and the requirements are ambiguous. What exact steps would you take to resolve it?",
                    "focus": "Prioritization, communication with stakeholders, triage, and calm under pressure.",
                    "hint_for_candidate": "Focus on reproducing the issue, communicating with the team, proposing a phased fix, and writing post-mortem tests."
                }
            ]
        })

    # Case B: Walkie-Talkie Conversational Reaction
    elif "react" in prompt_lower or "walkie" in prompt_lower or "acknowledge" in prompt_lower:
        return json.dumps({
            "greeting_reaction": "Thank you for that thoughtful answer! I like how you explained your thought process.",
            "follow_up_note": "You demonstrated clear awareness of the core concepts.",
            "transition": "Let's move directly to our next question."
        })

    # Case C: Comprehensive Interview Evaluation
    elif "evaluate" in prompt_lower or "score" in prompt_lower or "report" in prompt_lower:
        return json.dumps({
            "overall_score": 8.2,
            "readiness_verdict": "Interview Ready - High Potential",
            "scores": {
                "technical_depth": 8.0,
                "communication_clarity": 8.5,
                "confidence_delivery": 8.0,
                "problem_solving": 8.2,
                "star_method_alignment": 8.0
            },
            "top_strengths": [
                "Clear, structured communication and enthusiastic delivery during the project walkthrough.",
                "Good grasp of end-to-end software development lifecycle and foundational principles.",
                "Honest and positive attitude when discussing challenges and learning experiences."
            ],
            "critical_areas_for_improvement": [
                "Quantify your project results: Instead of saying 'it improved performance', specify 'reduced query response time by ~30%'.",
                "Deepen technical terminology: Clearly distinguish between client-side vs server-side responsibilities.",
                "Structure behavioral stories strictly using the STAR format (Situation -> Task -> Action -> Result)."
            ],
            "grace_years_coaching": {
                "advice": "Frame any gap or grace period as an intentional season of aggressive upskilling and practical portfolio building.",
                "power_statement": "During this period, I dedicated 25+ hours a week to mastering modern full-stack architectures, building real-world projects from scratch, and refining my engineering fundamentals."
            },
            "questions_review": [
                {
                    "question": "Candidate Background & Introduction",
                    "score": 8.5,
                    "feedback": "Smooth introduction with clear articulation of personal interests and relevant skills.",
                    "model_answer": "Hello! I am a software engineer focused on building robust, scalable applications. Over the past few years, I've built projects across modern full-stack technologies, with special interest in efficient APIs and clean UX. I'm excited about this opportunity because your team works on high-impact systems where I can contribute and grow rapidly."
                },
                {
                    "question": "Project Architecture & Deep Dive",
                    "score": 8.0,
                    "feedback": "Covered the components well. Can be enhanced by diving deeper into database optimization and failure recovery.",
                    "model_answer": "In this project, I architected a decoupled system using a RESTful API backend and a responsive frontend. One major challenge was high latency on search queries. I resolved this by adding indexing in the database and implementing in-memory caching, reducing latency by 45%."
                },
                {
                    "question": "Technical Principles & Scalability",
                    "score": 8.0,
                    "feedback": "Good fundamental understanding. Remember to mention automated testing and error logging frameworks.",
                    "model_answer": "I approach scalability on three levels: modular code architecture, defensive input validation with clear HTTP status codes, and infrastructure practices such as connection pooling and caching."
                },
                {
                    "question": "Behavioral & Overcoming Setbacks",
                    "score": 8.2,
                    "feedback": "Great honesty and positive framing of self-learning.",
                    "model_answer": "When facing an unexpected roadblock or timeline delay, I immediately broke the deliverable into daily verifiable milestones. I established a focused study and building routine, which helped me complete the project ahead of schedule."
                },
                {
                    "question": "Ambiguous Production Bug Scenario",
                    "score": 8.3,
                    "feedback": "Logical sequence of troubleshooting. Showed teamwork and calm under pressure.",
                    "model_answer": "First, I reproduce the bug in an isolated staging environment and check application logs. Next, I communicate with the team lead to assess severity and customer impact. I deliver a hotfix or rollback to stabilize production, followed by unit tests to prevent regression."
                }
            ],
            "final_preparation_checklist": [
                "Practice the 60-second elevator pitch out loud 3 times before the interview.",
                "Prepare 2 specific metrics for each resume project (e.g. users, requests/sec, lines of code, efficiency gain).",
                "Have 2 thoughtful questions ready to ask the interviewer at the end of the conversation."
            ]
        })

    # Default fallback
    return "Thank you for sharing your thoughts. That demonstrates a solid technical thought process."
