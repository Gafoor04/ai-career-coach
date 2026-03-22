'use client'
import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useAuth } from '@/context/InterviewContext'
import { roadmapAPI } from '@/lib/api'

const priorityColors: Record<string, string> = {
  high: 'text-red-400 bg-red-400/10 border-red-400/20',
  medium: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
  low: 'text-green-400 bg-green-400/10 border-green-400/20',
}

const demandColors: Record<string, string> = {
  high: 'text-green-400',
  medium: 'text-yellow-400',
  low: 'text-red-400',
}

export default function RoadmapDetailPage() {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const { roadmapId } = useParams<{ roadmapId: string }>()
  const [roadmap, setRoadmap] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [activePhase, setActivePhase] = useState(0)

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace('/auth/login')
  }, [isAuthenticated, isLoading, router])

  useEffect(() => {
    if (isAuthenticated && roadmapId) {
      roadmapAPI.getOne(roadmapId)
        .then(res => setRoadmap(res.roadmap_data))
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [isAuthenticated, roadmapId])

  if (isLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-sm text-muted-foreground">Loading your roadmap...</p>
        </div>
      </div>
    )
  }

  if (!roadmap) return null

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border bg-card px-6 py-4">
        <div className="mx-auto flex max-w-4xl items-center justify-between">
          <button onClick={() => router.push('/roadmap')} className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            ← Back
          </button>
          <h1 className="text-base font-semibold text-foreground capitalize">{roadmap.target_role} Roadmap</h1>
          <span className="text-xs text-muted-foreground">{roadmap.estimated_timeline}</span>
        </div>
      </nav>

      <div className="mx-auto max-w-4xl px-6 py-10 flex flex-col gap-6">

        {/* Summary */}
        <div className="rounded-2xl border border-border bg-card p-6">
          <p className="text-muted-foreground leading-relaxed">{roadmap.summary}</p>
          <div className="mt-4 flex flex-wrap gap-3">
            <span className="rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs text-primary">
              ⏱ {roadmap.estimated_timeline}
            </span>
            {roadmap.industry_insights && (
              <span className={`rounded-full border px-3 py-1 text-xs ${demandColors[roadmap.industry_insights.demand_level]} border-current/20 bg-current/5`}>
                📈 {roadmap.industry_insights.demand_level} demand
              </span>
            )}
          </div>
        </div>

        {/* Industry insights */}
        {roadmap.industry_insights && (
          <div className="rounded-2xl border border-border bg-card p-6">
            <h3 className="font-semibold text-foreground mb-4">Industry Insights</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-muted-foreground mb-2">Avg Salary</p>
                <p className="text-sm font-medium text-foreground">{roadmap.industry_insights.avg_salary_range}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-2">Demand</p>
                <p className={`text-sm font-medium capitalize ${demandColors[roadmap.industry_insights.demand_level]}`}>
                  {roadmap.industry_insights.demand_level}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-2">Top Companies</p>
                <div className="flex flex-wrap gap-1">
                  {roadmap.industry_insights.top_companies_hiring?.map((c: string) => (
                    <span key={c} className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">{c}</span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-2">Key Technologies</p>
                <div className="flex flex-wrap gap-1">
                  {roadmap.industry_insights.key_technologies?.map((t: string) => (
                    <span key={t} className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">{t}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Skill gaps */}
        {roadmap.skill_gaps?.length > 0 && (
          <div className="rounded-2xl border border-border bg-card p-6">
            <h3 className="font-semibold text-foreground mb-4">Skill Gaps to Address</h3>
            <div className="flex flex-col gap-3">
              {roadmap.skill_gaps.map((gap: any, i: number) => (
                <div key={i} className="flex items-start justify-between gap-3 rounded-xl border border-border bg-background p-3">
                  <div>
                    <p className="text-sm font-medium text-foreground">{gap.skill}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{gap.reason}</p>
                  </div>
                  <span className={`shrink-0 rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize ${priorityColors[gap.priority]}`}>
                    {gap.priority}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Phases */}
        {roadmap.phases?.length > 0 && (
          <div className="rounded-2xl border border-border bg-card p-6">
            <h3 className="font-semibold text-foreground mb-4">Learning Phases</h3>

            {/* Phase tabs */}
            <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
              {roadmap.phases.map((phase: any, i: number) => (
                <button
                  key={i}
                  onClick={() => setActivePhase(i)}
                  className={`shrink-0 rounded-lg border px-4 py-2 text-sm font-medium transition-all
                    ${activePhase === i
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border bg-background text-muted-foreground hover:border-primary/50'
                    }`}
                >
                  Phase {phase.phase_number}
                </button>
              ))}
            </div>

            {/* Active phase content */}
            {roadmap.phases[activePhase] && (() => {
              const phase = roadmap.phases[activePhase]
              return (
                <div className="flex flex-col gap-5">
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold text-foreground">{phase.title}</h4>
                    <span className="text-xs text-muted-foreground">⏱ {phase.duration}</span>
                  </div>

                  {/* Goals */}
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">Goals</p>
                    <ul className="flex flex-col gap-1.5">
                      {phase.goals?.map((g: string, i: number) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-foreground">
                          <span className="text-primary mt-0.5">✓</span>{g}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Skills */}
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">Skills to Learn</p>
                    <div className="flex flex-wrap gap-2">
                      {phase.skills_to_learn?.map((s: string, i: number) => (
                        <span key={i} className="rounded-full bg-primary/10 border border-primary/20 px-3 py-1 text-xs text-primary">{s}</span>
                      ))}
                    </div>
                  </div>

                  {/* Resources */}
                  {phase.resources?.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">Resources</p>
                      <div className="flex flex-col gap-2">
                        {phase.resources.map((r: any, i: number) => (
                          <div key={i} className="flex items-center justify-between rounded-lg border border-border bg-background px-4 py-2.5">
                            <div className="flex items-center gap-2">
                              <span className="text-xs capitalize text-muted-foreground border border-border rounded px-2 py-0.5">{r.type}</span>
                              <span className="text-sm text-foreground">{r.title}</span>
                            </div>
                            <span className={`text-xs font-medium ${r.is_free ? 'text-green-400' : 'text-yellow-400'}`}>
                              {r.is_free ? 'Free' : 'Paid'}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Projects */}
                  {phase.projects?.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">Projects to Build</p>
                      <div className="flex flex-col gap-3">
                        {phase.projects.map((p: any, i: number) => (
                          <div key={i} className="rounded-xl border border-border bg-background p-4">
                            <p className="text-sm font-medium text-foreground">{p.title}</p>
                            <p className="text-xs text-muted-foreground mt-1">{p.description}</p>
                            <div className="flex flex-wrap gap-1 mt-2">
                              {p.tech_stack?.map((t: string, j: number) => (
                                <span key={j} className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">{t}</span>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )
            })()}
          </div>
        )}

        {/* Certifications */}
        {roadmap.certifications?.length > 0 && (
          <div className="rounded-2xl border border-border bg-card p-6">
            <h3 className="font-semibold text-foreground mb-4">Recommended Certifications</h3>
            <div className="flex flex-col gap-3">
              {roadmap.certifications.map((cert: any, i: number) => (
                <div key={i} className="flex items-center justify-between rounded-xl border border-border bg-background p-4">
                  <div>
                    <p className="text-sm font-medium text-foreground">{cert.name}</p>
                    <p className="text-xs text-muted-foreground">{cert.provider}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize ${priorityColors[cert.priority]}`}>
                      {cert.priority}
                    </span>
                    <span className={`text-xs font-medium ${cert.is_free ? 'text-green-400' : 'text-yellow-400'}`}>
                      {cert.is_free ? 'Free' : 'Paid'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  )
}