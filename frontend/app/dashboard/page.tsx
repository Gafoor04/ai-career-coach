'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/context/InterviewContext'
import { interviewAPI } from '@/lib/api'
import { SessionListItem, SessionHistoryResponse } from '@/types'

const ratingColors: Record<string, string> = {
  excellent: 'text-green-400 bg-green-400/10 border-green-400/20',
  good: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
  needs_improvement: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
  poor: 'text-red-400 bg-red-400/10 border-red-400/20',
}

export default function DashboardPage() {
  const { user, logout, isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const [history, setHistory] = useState<SessionHistoryResponse | null>(null)
  const [loadingData, setLoadingData] = useState(true)

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace('/auth/login')
  }, [isAuthenticated, isLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      interviewAPI.getHistory(1, 5)
        .then(setHistory)
        .catch(console.error)
        .finally(() => setLoadingData(false))
    }
  }, [isAuthenticated])

  if (isLoading || !isAuthenticated) return null

  return (
    <div className="min-h-screen bg-background">
      {/* Navbar */}
      <nav className="border-b border-border bg-card px-6 py-4">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <h1 className="text-lg font-bold text-foreground">AI Career Coach</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              Hey, <span className="font-medium text-foreground">{user?.name}</span>
            </span>
            <button
              onClick={logout}
              className="rounded-lg border border-border px-3 py-1.5 text-sm text-muted-foreground hover:border-primary hover:text-primary transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="mx-auto max-w-5xl px-6 py-10">
        {/* Welcome + Start */}
        <div className="mb-10 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-foreground">Dashboard</h2>
            <p className="mt-1 text-muted-foreground">Track your interview progress</p>
          </div>
          <div className="flex gap-3">
  <Link
    href="/roadmap"
    className="rounded-xl border border-border px-5 py-3 text-sm font-semibold text-foreground hover:border-primary hover:text-primary transition-colors"
  >
    🗺 Roadmap
  </Link>
  <Link
    href="/interview"
    className="rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground hover:opacity-90 transition-opacity"
  >
    + New Interview
  </Link>
</div>
        </div>

        {/* Recent Sessions */}
        <div className="rounded-2xl border border-border bg-card p-6">
          <h3 className="mb-4 text-base font-semibold text-foreground">Recent Sessions</h3>

          {loadingData ? (
            <div className="flex items-center justify-center py-12">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          ) : history?.sessions.length === 0 ? (
            <div className="py-12 text-center">
              <p className="text-muted-foreground">No interviews yet.</p>
              <Link href="/interview" className="mt-3 inline-block text-sm font-medium text-primary hover:underline">
                Start your first interview →
              </Link>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {history?.sessions.map((session) => (
                <Link
                  key={session.id}
                  href={`/interview/${session.id}/summary`}
                  className="flex items-center justify-between rounded-xl border border-border bg-background p-4 hover:border-primary/50 transition-colors"
                >
                  <div className="flex flex-col gap-1">
                    <span className="font-medium text-foreground capitalize">{session.role}</span>
                    <span className="text-xs text-muted-foreground capitalize">
                      {session.interview_type} · {session.level} · {session.difficulty}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    {session.rating && (
                      <span className={`rounded-full border px-3 py-1 text-xs font-medium capitalize ${ratingColors[session.rating]}`}>
                        {session.rating.replace('_', ' ')}
                      </span>
                    )}
                    {session.total_score !== null && (
                      <span className="text-sm font-semibold text-foreground">
                        {session.total_score.toFixed(1)}/10
                      </span>
                    )}
                    <span className="text-xs text-muted-foreground">
                      {new Date(session.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}

          {history && history.total > 5 && (
            <Link
              href="/interview/history"
              className="mt-4 block text-center text-sm text-primary hover:underline"
            >
              View all {history.total} sessions →
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}
<div className="flex gap-3">
  <Link
    href="/roadmap"
    className="rounded-xl border border-border px-5 py-3 text-sm font-semibold text-foreground hover:border-primary hover:text-primary transition-colors"
  >
    🗺 Roadmap
  </Link>
  <Link
    href="/interview"
    className="rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground hover:opacity-90 transition-opacity"
  >
    + New Interview
  </Link>
</div>