'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/InterviewContext'
import { interviewAPI } from '@/lib/api'
import { ExperienceLevel, InterviewType, Difficulty } from '@/types'

export default function InterviewSetupPage() {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    role: '',
    level: 'fresher' as ExperienceLevel,
    interview_type: 'technical' as InterviewType,
    difficulty: 'medium' as Difficulty,
    question_count: 5,
    timer_enabled: false,
    time_per_question: 120,
  })

  if (isLoading) return null
  if (!isAuthenticated) { router.replace('/auth/login'); return null }

  const handleStart = async () => {
    if (!form.role.trim()) { setError('Please enter a job role'); return }
    setError('')
    setLoading(true)
    try {
      const res = await interviewAPI.start({
        ...form,
        time_per_question: form.timer_enabled ? form.time_per_question : undefined,
      })
      router.push(`/interview/${res.session_id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start interview')
    } finally {
      setLoading(false)
    }
  }

  const Option = ({ value, label, current, onClick }: any) => (
    <button
      type="button"
      onClick={() => onClick(value)}
      className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all capitalize
        ${current === value
          ? 'border-primary bg-primary/10 text-primary'
          : 'border-border bg-background text-muted-foreground hover:border-primary/50 hover:text-foreground'
        }`}
    >
      {label || value}
    </button>
  )

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border bg-card px-6 py-4">
        <div className="mx-auto flex max-w-2xl items-center justify-between">
          <button onClick={() => router.push('/dashboard')} className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            ← Dashboard
          </button>
          <h1 className="text-base font-semibold text-foreground">New Interview</h1>
          <div className="w-20" />
        </div>
      </nav>

      <div className="mx-auto max-w-2xl px-6 py-10">
        <div className="rounded-2xl border border-border bg-card p-8">
          <h2 className="mb-6 text-xl font-bold text-foreground">Configure Your Interview</h2>

          <div className="flex flex-col gap-6">
            {/* Role */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-foreground">Job Role</label>
              <input
                type="text"
                placeholder="e.g. Backend Developer, Data Scientist..."
                value={form.role}
                onChange={e => setForm({ ...form, role: e.target.value })}
                className="rounded-lg border border-input bg-background px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>

            {/* Level */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-foreground">Experience Level</label>
              <div className="flex gap-2">
                {(['fresher', 'mid', 'senior'] as ExperienceLevel[]).map(l => (
                  <Option key={l} value={l} current={form.level} onClick={(v: ExperienceLevel) => setForm({ ...form, level: v })} />
                ))}
              </div>
            </div>

            {/* Type */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-foreground">Interview Type</label>
              <div className="flex flex-wrap gap-2">
                {([
                  { value: 'technical', label: 'Technical' },
                  { value: 'hr', label: 'HR' },
                  { value: 'behavioral', label: 'Behavioral' },
                  { value: 'system_design', label: 'System Design' },
                ] as { value: InterviewType; label: string }[]).map(t => (
                  <Option key={t.value} value={t.value} label={t.label} current={form.interview_type} onClick={(v: InterviewType) => setForm({ ...form, interview_type: v })} />
                ))}
              </div>
            </div>

            {/* Difficulty */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-foreground">Difficulty</label>
              <div className="flex gap-2">
                {(['easy', 'medium', 'hard'] as Difficulty[]).map(d => (
                  <Option key={d} value={d} current={form.difficulty} onClick={(v: Difficulty) => setForm({ ...form, difficulty: v })} />
                ))}
              </div>
            </div>

            {/* Question Count */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-foreground">
                Number of Questions: <span className="text-primary">{form.question_count}</span>
              </label>
              <input
                type="range"
                min={1}
                max={15}
                value={form.question_count}
                onChange={e => setForm({ ...form, question_count: Number(e.target.value) })}
                className="accent-primary"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>1</span><span>15</span>
              </div>
            </div>

            {/* Timer */}
            <div className="flex items-center justify-between rounded-lg border border-border bg-background p-4">
              <div>
                <p className="text-sm font-medium text-foreground">Enable Timer</p>
                <p className="text-xs text-muted-foreground">Set time limit per question</p>
              </div>
              <button
                type="button"
                onClick={() => setForm({ ...form, timer_enabled: !form.timer_enabled })}
                className={`relative h-6 w-11 rounded-full transition-colors ${form.timer_enabled ? 'bg-primary' : 'bg-muted'}`}
              >
                <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${form.timer_enabled ? 'left-5.5 translate-x-0.5' : 'left-0.5'}`} />
              </button>
            </div>

            {form.timer_enabled && (
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground">
                  Time per question: <span className="text-primary">{form.time_per_question}s</span>
                </label>
                <input
                  type="range"
                  min={30}
                  max={300}
                  step={30}
                  value={form.time_per_question}
                  onChange={e => setForm({ ...form, time_per_question: Number(e.target.value) })}
                  className="accent-primary"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>30s</span><span>5min</span>
                </div>
              </div>
            )}

            {error && (
              <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <button
              onClick={handleStart}
              disabled={loading}
              className="rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground hover:opacity-90 disabled:opacity-50 transition-opacity"
            >
              {loading ? 'Starting...' : 'Start Interview →'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}