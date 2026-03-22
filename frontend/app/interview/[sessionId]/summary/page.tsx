'use client'
import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/context/InterviewContext'
import { interviewAPI } from '@/lib/api'
import { SessionSummary } from '@/types'

const ratingConfig = {
  excellent: { label: 'Excellent', color: 'text-green-400', bg: 'bg-green-400/10 border-green-400/20' },
  good: { label: 'Good', color: 'text-blue-400', bg: 'bg-blue-400/10 border-blue-400/20' },
  needs_improvement: { label: 'Needs Improvement', color: 'text-yellow-400', bg: 'bg-yellow-400/10 border-yellow-400/20' },
  poor: { label: 'Poor', color: 'text-red-400', bg: 'bg-red-400/10 border-red-400/20' },
}

export default function SummaryPage() {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const { sessionId } = useParams<{ sessionId: string }>()
  const [summary, setSummary] = useState<SessionSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace('/auth/login')
  }, [isAuthenticated, isLoading, router])

  useEffect(() => {
    if (isAuthenticated && sessionId) {
      interviewAPI.getSummary(sessionId)
        .then(setSummary)
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [isAuthenticated, sessionId])

  if (isLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!summary) return null

  const rating = ratingConfig[summary.rating] || ratingConfig.poor
  const scoreColor = (s: number) => s >= 7 ? 'text-green-400' : s >= 5 ? 'text-yellow-400' : 'text-red-400'

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border bg-card px-6 py-4">
        <div className="mx-auto flex max-w-3xl items-center justify-between">
          <Link href="/dashboard" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            ← Dashboard
          </Link>
          <h1 className="text-base font-semibold text-foreground">Interview Summary</h1>
          <Link href="/interview" className="text-sm font-medium text-primary hover:underline">
            New Interview
          </Link>
        </div>
      </nav>

      <div className="mx-auto max-w-3xl px-6 py-10 flex flex-col gap-6">
        {/* Score card */}
        <div className="rounded-2xl border border-border bg-card p-8 text-center">
          <p className="text-sm text-muted-foreground capitalize mb-1">
            {summary.role} · {summary.level} · {summary.interview_type} · {summary.difficulty}
          </p>
          <div className={`text-6xl font-bold mt-4 ${scoreColor(summary.total_score)}`}>
            {summary.total_score.toFixed(1)}
          </div>
          <p className="text-muted-foreground text-sm mt-1">out of 10</p>
          <span className={`mt-4 inline-block rounded-full border px-4 py-1.5 text-sm font-medium ${rating.color} ${rating.bg}`}>
            {summary.rating_label}
          </span>
        </div>

        {/* Axis averages */}
        <div className="rounded-2xl border border-border bg-card p-6">
          <h3 className="mb-4 font-semibold text-foreground">Score Breakdown</h3>
          <div className="flex flex-col gap-3">
            {Object.entries(summary.axis_averages).map(([key, val]) => (
              <div key={key} className="flex items-center gap-3">
                <span className="w-24 text-sm capitalize text-muted-foreground">{key}</span>
                <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                  <div
                    className="h-full rounded-full bg-primary"
                    style={{ width: `${(val / 10) * 100}%` }}
                  />
                </div>
                <span className={`w-8 text-right text-sm font-medium ${scoreColor(val)}`}>
                  {val.toFixed(1)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Weak areas */}
        {summary.weak_areas.length > 0 && (
          <div className="rounded-2xl border border-destructive/20 bg-destructive/5 p-6">
            <h3 className="mb-3 font-semibold text-foreground">Areas to Improve</h3>
            <div className="flex flex-wrap gap-2">
              {summary.weak_areas.map(area => (
                <span key={area} className="rounded-full border border-destructive/30 bg-destructive/10 px-3 py-1 text-xs text-destructive">
                  {area}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Questions breakdown */}
        <div className="rounded-2xl border border-border bg-card p-6">
          <h3 className="mb-4 font-semibold text-foreground">Question Breakdown</h3>
          <div className="flex flex-col gap-4">
            {summary.questions.map((q, i) => (
              <div key={q.id} className="rounded-xl border border-border bg-background p-4 flex flex-col gap-2">
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm font-medium text-foreground">
                    <span className="text-muted-foreground mr-2">Q{i + 1}.</span>
                    {q.question_text}
                  </p>
                  {q.overall_score !== null && (
                    <span className={`shrink-0 text-sm font-bold ${scoreColor(q.overall_score)}`}>
                      {q.overall_score.toFixed(1)}
                    </span>
                  )}
                </div>
                {q.strengths && (
                  <p className="text-xs text-muted-foreground">
                    <span className="text-green-400">✓ </span>{q.strengths}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}