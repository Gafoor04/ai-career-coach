// ─── AUTH TYPES ───────────────────────────────────────────────────────────────

export interface User {
  id: string
  email: string
  name: string
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  name: string
  password: string
}

export interface AuthToken {
  access_token: string
  token_type: string
}

// ─── INTERVIEW SETUP TYPES ────────────────────────────────────────────────────

export type ExperienceLevel = 'fresher' | 'mid' | 'senior'
export type InterviewType = 'technical' | 'hr' | 'behavioral' | 'system_design'
export type Difficulty = 'easy' | 'medium' | 'hard'
export type SessionStatus = 'in_progress' | 'completed'
export type Rating = 'excellent' | 'good' | 'needs_improvement' | 'poor'

export interface InterviewStartRequest {
  role: string
  level: ExperienceLevel
  interview_type: InterviewType
  difficulty: Difficulty
  question_count: number
  timer_enabled: boolean
  time_per_question?: number
}

// ─── QUESTION TYPES ───────────────────────────────────────────────────────────

export interface Question {
  id: string
  question_index: number
  question_text: string
  category: string | null
}

export interface InterviewStartResponse {
  session_id: string
  first_question: Question
  total_questions: number
  message: string
}

// ─── EVALUATION TYPES ─────────────────────────────────────────────────────────

export interface EvaluationResult {
  technical_score: number
  depth_score: number
  clarity_score: number
  relevance_score: number
  structure_score: number
  overall_score: number
  strengths: string
  weaknesses: string
  improvement_suggestions: string
}

export interface AnswerSubmitRequest {
  session_id: string
  question_id: string
  answer: string
}

export interface AnswerSubmitResponse {
  evaluation: EvaluationResult
  next_question: Question | null
  is_last_question: boolean
  questions_answered: number
  total_questions: number
}

// ─── SESSION SUMMARY TYPES ────────────────────────────────────────────────────

export interface AxisAverages {
  technical: number
  depth: number
  clarity: number
  relevance: number
  structure: number
}

export interface QuestionSummary {
  id: string
  question_index: number
  question_text: string
  category: string | null
  user_answer: string | null
  technical_score: number | null
  depth_score: number | null
  clarity_score: number | null
  relevance_score: number | null
  structure_score: number | null
  overall_score: number | null
  strengths: string | null
  weaknesses: string | null
  improvement_suggestions: string | null
}

export interface SessionSummary {
  session_id: string
  role: string
  level: string
  interview_type: string
  difficulty: string
  total_score: number
  rating: Rating
  rating_label: string
  axis_averages: AxisAverages
  questions: QuestionSummary[]
  weak_areas: string[]
  created_at: string
  completed_at: string | null
}

// ─── SESSION LIST TYPES ───────────────────────────────────────────────────────

export interface SessionListItem {
  id: string
  role: string
  level: string
  interview_type: string
  difficulty: string
  question_count: number
  total_score: number | null
  status: SessionStatus
  rating: Rating | null
  created_at: string
}

export interface SessionHistoryResponse {
  sessions: SessionListItem[]
  total: number
  page: number
  limit: number
  total_pages: number
}

// ─── SESSION DETAIL TYPES ─────────────────────────────────────────────────────

export interface SessionDetail {
  id: string
  role: string
  level: string
  interview_type: string
  difficulty: string
  question_count: number
  total_score: number | null
  status: SessionStatus
  timer_enabled: boolean
  time_per_question: number | null
  questions: QuestionSummary[]
  created_at: string
  completed_at: string | null
}