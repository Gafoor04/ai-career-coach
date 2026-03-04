def get_question_generation_prompt(
    role: str,
    level: str,
    interview_type: str,
    difficulty: str,
    count: int
) -> str:
    level_context = {
        "fresher": "0-1 years of experience, recently graduated",
        "mid": "2-4 years of experience, has worked on real projects",
        "senior": "5+ years of experience, leads teams and systems"
    }

    type_context = {
        "technical": "technical skills, coding concepts, system internals, tools and frameworks",
        "hr": "motivation, career goals, work style, team fit, salary expectations",
        "behavioral": "past experiences using STAR method (Situation, Task, Action, Result)",
        "system_design": "designing scalable systems, architecture decisions, trade-offs"
    }

    return f"""You are an expert technical interviewer at a top tech company.

Generate exactly {count} {difficulty}-difficulty interview questions for the following candidate profile:
- Role: {role}
- Experience: {level_context.get(level, level)}
- Interview Focus: {type_context.get(interview_type, interview_type)}

Requirements for the questions:
1. Each question must test REAL-WORLD understanding, not textbook definitions
2. Questions must be appropriate for {difficulty} difficulty
3. Each question should take 2-5 minutes to answer thoughtfully
4. Questions must be specific to the {role} role
5. Vary the categories/topics covered
6. No duplicate or very similar questions

You MUST respond with ONLY valid JSON. No explanation, no preamble, no markdown code blocks.

Response format:
{{
  "questions": [
    {{
      "question_text": "The full question text here",
      "category": "One of: Databases, APIs, System Design, Security, Performance, Architecture, Frontend, Backend, DevOps, Soft Skills, Leadership, Problem Solving, Algorithms, Networking, Cloud"
    }}
  ]
}}"""


def get_evaluation_prompt(
    question_text: str,
    user_answer: str,
    role: str,
    level: str,
    interview_type: str
) -> str:
    return f"""You are an expert technical interviewer evaluating a candidate's interview answer.

CANDIDATE PROFILE:
- Role: {role}
- Experience Level: {level}
- Interview Type: {interview_type}

QUESTION ASKED:
{question_text}

CANDIDATE'S ANSWER:
{user_answer}

Evaluate the answer strictly and fairly on these 5 axes, each scored 0-10:

1. TECHNICAL ACCURACY (0-10): Are the facts, concepts, and terminology correct?
2. DEPTH OF EXPLANATION (0-10): Is the answer thorough, layered, and nuanced?
3. CLARITY & COMMUNICATION (0-10): Is the answer logically structured and clearly expressed?
4. REAL-WORLD RELEVANCE (0-10): Does the answer include practical examples or industry awareness?
5. STRUCTURE (0-10): Does the answer have a clear intro → body → conclusion?

Scoring guide:
- 9-10: Exceptional, would impress at top companies
- 7-8: Good, above average candidate
- 5-6: Average, basic understanding present
- 3-4: Below average, significant gaps
- 0-2: Very poor or irrelevant answer

You MUST respond with ONLY valid JSON. No explanation, no preamble, no markdown.

Response format:
{{
  "technical_score": <float 0-10>,
  "depth_score": <float 0-10>,
  "clarity_score": <float 0-10>,
  "relevance_score": <float 0-10>,
  "structure_score": <float 0-10>,
  "strengths": "<2-3 sentences describing what was done well>",
  "weaknesses": "<2-3 sentences describing what was lacking>",
  "improvement_suggestions": "<1-2 specific, actionable suggestions to improve the answer>"
}}"""