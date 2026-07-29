"""
Generates a personalized warning message for each flagged student,
using either Gemini or Groq (set in config.AI_PROVIDER).
"""

import config


def generate_warning(student):
    """
    student is one dict from analyzer.analyze() — contains student_name,
    reasons (list of strings), and whichever grade/attendance fields apply.
    Returns a short personalized warning message as a string.
    """
    prompt = _build_prompt(student)

    if config.AI_PROVIDER == "gemini":
        return _call_gemini(prompt)
    elif config.AI_PROVIDER == "groq":
        return _call_groq(prompt)
    else:
        raise ValueError(f"Unknown AI_PROVIDER in config.py: {config.AI_PROVIDER}")


def _build_prompt(student):
    reasons_text = "; ".join(student["reasons"])
    performer_note = (
        "This student has historically been a strong performer this semester, "
        "so this recent change is a notable shift worth flagging clearly."
        if student.get("is_high_performer")
        else "This student's recent performance has dropped and needs attention."
    )

    return f"""You are writing a short, supportive advisory notice for a college student.

Student name: {student['student_name']}
Observed changes this week: {reasons_text}
Context: {performer_note}

Write a brief (3-5 sentence) message that:
- Is addressed directly to the student, in a caring but professional tone
- Clearly states what changed (grades and/or attendance) without being alarming
- Encourages them to reach out to their advisor or instructor
- Does not sound robotic or like a form letter

Return only the message text, nothing else."""


def _call_gemini(prompt):
    from google import genai
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
    )
    return response.text.strip()


def _call_groq(prompt):
    from groq import Groq
    client = Groq(api_key=config.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()
