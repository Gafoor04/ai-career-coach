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
def get_followup_prompt(
    original_question: str,
    user_answer: str,
    weaknesses: str,
    role: str,
    level: str
) -> str:
    return f"""You are an expert interviewer conducting a real interview.

The candidate gave a weak answer to a question. Generate ONE targeted follow-up question to help them demonstrate better understanding.

ORIGINAL QUESTION:
{original_question}

CANDIDATE'S ANSWER:
{user_answer}

WEAKNESSES IDENTIFIED:
{weaknesses}

CANDIDATE PROFILE:
- Role: {role}
- Level: {level}

Rules:
1. The follow-up must directly address the weakness
2. It should give the candidate a chance to recover
3. Keep it concise and specific
4. Do NOT repeat the original question

Respond with ONLY valid JSON:
{{
  "question_text": "Your follow-up question here",
  "category": "Same category as original"
}}"""
def get_roadmap_prompt(
    target_role: str,
    current_skills: list,
    experience_level: str
) -> str:
    skills_str = ", ".join(current_skills) if current_skills else "None specified"

    return f"""You are an expert career advisor and technical mentor.

Generate a detailed, personalized career roadmap for the following profile:
- Target Role: {target_role}
- Experience Level: {experience_level}
- Current Skills: {skills_str}

Return a comprehensive roadmap with the following structure:

{{
  "target_role": "{target_role}",
  "summary": "2-3 sentence overview of the path to becoming a {target_role}",
  "estimated_timeline": "e.g. 3-6 months",
  "skill_gaps": [
    {{
      "skill": "Skill name",
      "priority": "high|medium|low",
      "reason": "Why this skill is needed"
    }}
  ],
  "phases": [
    {{
      "phase_number": 1,
      "title": "Phase title",
      "duration": "e.g. 2 weeks",
      "goals": ["goal 1", "goal 2"],
      "skills_to_learn": ["skill 1", "skill 2"],
      "resources": [
        {{
          "type": "course|book|documentation|practice",
          "title": "Resource title",
          "url": "",
          "is_free": true
        }}
      ],
      "projects": [
        {{
          "title": "Project title",
          "description": "What to build and why",
          "tech_stack": ["tech1", "tech2"]
        }}
      ]
    }}
  ],
  "certifications": [
    {{
      "name": "Certification name",
      "provider": "Provider",
      "priority": "high|medium|low",
      "is_free": false
    }}
  ],
  "industry_insights": {{
    "demand_level": "high|medium|low",
    "avg_salary_range": "e.g. $80k-$120k",
    "top_companies_hiring": ["Company1", "Company2", "Company3"],
    "key_technologies": ["tech1", "tech2", "tech3"]
  }}
}}

You MUST respond with ONLY valid JSON. No explanation, no preamble, no markdown."""