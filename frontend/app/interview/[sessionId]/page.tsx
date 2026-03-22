'use client'
import { useEffect, useState, useCallback } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useAuth } from '@/context/InterviewContext'
import { interviewAPI } from '@/lib/api'
import { Question, EvaluationResult } from '@/types'

export default function ActiveInterviewPage() {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const { sessionId } = useParams<{ sessionId: string }>()

  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null)
  const [answer, setAnswer] = useState('')
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null)
  const [questionsAnswered, setQuestionsAnswered] = useState(0)
  const [totalQuestions, setTotalQuestions] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [loadingSession, setLoadingSession] = useState(true)

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace('/auth/login')
  }, [isAuthenticated, isLoading, router])

  useEffect(() => {
    if (isAuthenticated && sessionId) {
      interviewAPI.resumeSession(sessionId)
        .then(res => {
          setCurrentQuestion(res.current_question)
          setQuestionsAnswered(res.questions_answered)
          setTotalQuestions(res.total_questions)
        })
        .catch(() => {
          // Session might be new, get from history
          interviewAPI.getSession(sessionId)
            .then(s => {
              const unanswered = s.questions.find(q => q.user_answer === null)
              if (unanswered) {
                setCurrentQuestion({
                  id: unanswered.id,
                  question_index: unanswered.question_index,
                  question_text: unanswered.question_text,
                  category: unanswered.category,
                })
              }
              setTotalQuestions(s.question_count)
              setQuestionsAnswered(s.questions.filter(q => q.user_answer !== null).length)
            })
        })
        .finally(() => setLoadingSession(false))
    }
  }, [isAuthenticated, sessionId])

  const handleSubmit = async () => {
    if (!currentQuestion || !answer.trim()) return
    setError('')
    setSubmitting(true)
    try {
      const res = await interviewAPI.submitAnswer({
        session_id: sessionId,
        question_id: currentQuestion.id,
        answer: answer.trim(),
      })

      setEvaluation(res.evaluation)
      setQuestionsAnswered(res.questions_answered)
      setTotalQuestions(res.total_questions)

      if (res.is_last_question) {
        setTimeout(() => router.push(`/interview/${sessionId}/summary`), 3000)
      } else if (res.next_question) {
        setCurrentQuestion(res.next_question)
        setAnswer('')
        setEvaluation(null)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit answer')
    } finally {
      setSubmitting(false)
    }
  }

  const handleAbandon = async () => {
    if (!confirm('Are you sure you want to abandon this interview?')) return
    try {
      await interviewAPI.abandonSession(sessionId)
      router.push('/dashboard')
    } catch {
      router.push('/dashboard')
    }
  }

  if (isLoading || loadingSession) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  const scoreColor = (score: number) =>
    score >= 7 ? 'text-green-400' : score >= 5 ? 'text-yellow-400' : 'text-red-400'

  return (
    <div className="min-h-screen bg-background">
      {/* Top bar */}
      <nav className="border-b border-border bg-card px-6 py-4">
        <div className="mx-auto flex max-w-3xl items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-foreground">
              Question {questionsAnswered + (evaluation ? 0 : 1)} of {totalQuestions}
            </span>
            <div className="h-2 w-32 overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-primary transition-all"
                style={{ width: `${(questionsAnswered / totalQuestions) * 100}%` }}
              />
            </div>
          </div>
          <button
            onClick={handleAbandon}
            className="text-xs text-muted-foreground hover:text-destructive transition-colors"
          >
            Abandon
          </button>
        </div>
      </nav>

      <div className="mx-auto max-w-3xl px-6 py-10 flex flex-col gap-6">
        {/* Question card */}
        {currentQuestion && (
          <div className="rounded-2xl border border-border bg-card p-6">
            {currentQuestion.category && (
              <span className="mb-3 inline-block rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                {currentQuestion.category}
                {(currentQuestion as any).is_followup && (
                  <span className="ml-2 text-yellow-400">↪ Follow-up</span>
                )}
              </span>
            )}
            <p className="text-base font-medium leading-relaxed text-foreground">
              {currentQuestion.question_text}
            </p>
          </div>
        )}

        {/* Answer area — hide after evaluation */}
        {!evaluation && (
          <div className="flex flex-col gap-3">
            <textarea
              value={answer}
              onChange={e => setAnswer(e.target.value)}
              placeholder="Type your answer here..."
              rows={8}
              className="rounded-xl border border-input bg-card px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 resize-none"
            />
            {error && (
              <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                {error}
              </div>
            )}
            <button
              onClick={handleSubmit}
              disabled={submitting || !answer.trim()}
              className="self-end rounded-xl bg-primary px-8 py-3 text-sm font-semibold text-primary-foreground hover:opacity-90 disabled:opacity-50 transition-opacity"
            >
              {submitting ? 'Evaluating...' : 'Submit Answer →'}
            </button>
          </div>
        )}

        {/* Evaluation result */}
        {evaluation && (
          <div className="rounded-2xl border border-border bg-card p-6 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-foreground">Evaluation</h3>
              <span className={`text-2xl font-bold ${scoreColor(evaluation.overall_score)}`}>
                {evaluation.overall_score.toFixed(1)}/10
              </span>
            </div>

            {/* Score bars */}
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'Technical', score: evaluation.technical_score },
                { label: 'Depth', score: evaluation.depth_score },
                { label: 'Clarity', score: evaluation.clarity_score },
                { label: 'Relevance', score: evaluation.relevance_score },
                { label: 'Structure', score: evaluation.structure_score },
              ].map(({ label, score }) => (
                <div key={label} className="flex flex-col gap-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">{label}</span>
                    <span className={scoreColor(score)}>{score.toFixed(1)}</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full rounded-full bg-primary transition-all"
                      style={{ width: `${(score / 10) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="flex flex-col gap-3 border-t border-border pt-4">
              <div>
                <p className="text-xs font-medium text-green-400 mb-1">✓ Strengths</p>
                <p className="text-sm text-muted-foreground">{evaluation.strengths}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-red-400 mb-1">✗ Weaknesses</p>
                <p className="text-sm text-muted-foreground">{evaluation.weaknesses}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-yellow-400 mb-1">→ Suggestions</p>
                <p className="text-sm text-muted-foreground">{evaluation.improvement_suggestions}</p>
              </div>
            </div>

            <button
              onClick={() => {
                setEvaluation(null)
                setAnswer('')
              }}
              className="self-end rounded-xl bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground hover:opacity-90 transition-opacity"
            >
              Next Question →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}