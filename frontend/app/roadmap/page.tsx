'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/InterviewContext'
import { roadmapAPI } from '@/lib/api'
import { ExperienceLevel } from '@/types'

export default function RoadmapPage() {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [pastRoadmaps, setPastRoadmaps] = useState<any[]>([])

  const [form, setForm] = useState({
    target_role: '',
    experience_level: 'fresher' as ExperienceLevel,
    current_skills: '' // comma separated input
  })

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace('/auth/login')
  }, [isAuthenticated, isLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      roadmapAPI.getAll().then(setPastRoadmaps).catch(console.error)
    }
  }, [isAuthenticated])

  const handleGenerate = async () => {
    if (!form.target_role.trim()) { setError('Please enter a target role'); return }
    setError('')
    setGenerating(true)
    try {
      const skills = form.current_skills
        .split(',')
        .map(s => s.trim())
        .filter(Boolean)

      const res = await roadmapAPI.generate({
        target_role: form.target_role,
        experience_level: form.experience_level,
        current_skills: skills
      })
      router.push(`/roadmap/${res.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate roadmap')
    } finally {
      setGenerating(false)
    }
  }

  const Option = ({ value, current, onClick }: any) => (
    <button
      type="button"
      onClick={() => onClick(value)}
      className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all capitalize
        ${current === value
          ? 'border-primary bg-primary/10 text-primary'
          : 'border-border bg-background text-muted-foreground hover:border-primary/50 hover:text-foreground'
        }`}
    >
      {value}
    </button>
  )

  if (isLoading || !isAuthenticated) return null

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border bg-card px-6 py-4">
        <div className="mx-auto flex max-w-3xl items-center justify-between">
          <button onClick={() => router.push('/dashboard')} className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            ← Dashboard
          </button>
          <h1 className="text-base font-semibold text-foreground">Career Roadmap</h1>
          <div className="w-20" />
        </div>
      </nav>

      <div className="mx-auto max-w-3xl px-6 py-10 flex flex-col gap-8">

        {/* Generator card */}
        <div className="rounded-2xl border border-border bg-card p-8">
          <h2 className="text-xl font-bold text-foreground mb-1">Generate Your Roadmap</h2>
          <p className="text-sm text-muted-foreground mb-6">
            Get a personalized learning path powered by AI
          </p>

          <div className="flex flex-col gap-5">
            {/* Target role */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-foreground">Target Role</label>
              <input
                type="text"
                placeholder="e.g. Full Stack Developer, Data Scientist..."
                value={form.target_role}
                onChange={e => setForm({ ...form, target_role: e.target.value })}
                className="rounded-lg border border-input bg-background px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>

            {/* Experience level */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-foreground">Experience Level</label>
              <div className="flex gap-2">
                {(['fresher', 'mid', 'senior'] as ExperienceLevel[]).map(l => (
                  <Option key={l} value={l} current={form.experience_level}
                    onClick={(v: ExperienceLevel) => setForm({ ...form, experience_level: v })} />
                ))}
              </div>
            </div>

            {/* Current skills */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-foreground">
                Current Skills
                <span className="ml-2 text-xs text-muted-foreground">(comma separated)</span>
              </label>
              <input
                type="text"
                placeholder="e.g. Python, SQL, HTML, CSS..."
                value={form.current_skills}
                onChange={e => setForm({ ...form, current_skills: e.target.value })}
                className="rounded-lg border border-input bg-background px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>

            {error && (
              <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <button
              onClick={handleGenerate}
              disabled={generating}
              className="rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground hover:opacity-90 disabled:opacity-50 transition-opacity flex items-center justify-center gap-2"
            >
              {generating ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Generating Roadmap...
                </>
              ) : (
                '✨ Generate Roadmap'
              )}
            </button>
          </div>
        </div>

        {/* Past roadmaps */}
        {pastRoadmaps.length > 0 && (
          <div className="rounded-2xl border border-border bg-card p-6">
            <h3 className="font-semibold text-foreground mb-4">Past Roadmaps</h3>
            <div className="flex flex-col gap-3">
              {pastRoadmaps.map((r: any) => (
                <button
                  key={r.id}
                  onClick={() => router.push(`/roadmap/${r.id}`)}
                  className="flex items-center justify-between rounded-xl border border-border bg-background p-4 hover:border-primary/50 transition-colors text-left"
                >
                  <div>
                    <p className="font-medium text-foreground capitalize">{r.target_role}</p>
                    <p className="text-xs text-muted-foreground capitalize">{r.experience_level}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(r.created_at).toLocaleDateString()}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}