'use client'

import { useState } from 'react'
import {
  ClipboardList,
  Loader2,
  RefreshCw,
  HelpCircle,
  AlertTriangle,
  TrendingUp,
} from 'lucide-react'
import { cn } from '@/lib/utils'

type BriefState = 'empty' | 'generating' | 'generated'

const GENERATION_STEPS = [
  'Analyzing pension situation',
  'Identifying key issues',
  'Building meeting agenda',
]

const pillars = [
  {
    name: 'Allmän pension (AGS)',
    border: 'border-l-blue-500',
    bg: 'bg-blue-50',
    value: '~7 300 kr/mån',
    detail: 'Inkomstpension + premiepension via AP-fonderna. Prognos baserad på nuvarande intjänande.',
  },
  {
    name: 'Tjänstepension (ITP1)',
    border: 'border-l-emerald-500',
    bg: 'bg-emerald-50',
    value: '~12 100 kr/mån',
    detail: 'Via Volvo / Collectum. Premiebestämd plan, 4.5% under taket och 30% över. Nuvarande fond: AMF Aktiefond.',
  },
  {
    name: 'Privat pension',
    border: 'border-l-violet-500',
    bg: 'bg-violet-50',
    value: '~1 800 kr/mån',
    detail: 'Kapitalförsäkring hos Avanza. Oregelbundna insättningar. Ej skattemässigt avdragsgill.',
  },
]

const keyIssues = [
  { severity: 'high', label: 'Suboptimal fund selection — 0.8% TER vs 0.2% equivalent', border: 'border-l-red-400', badge: 'bg-red-50 text-red-700' },
  { severity: 'medium', label: 'Missing survivor protection (efterlevandeskydd) on ITP1', border: 'border-l-amber-400', badge: 'bg-amber-50 text-amber-700' },
  { severity: 'low', label: 'Private pension is small; redirecting contributions may be more efficient', border: 'border-l-slate-300', badge: 'bg-slate-100 text-slate-600' },
]

const scenarios = [
  {
    title: 'Keep Current Allocation',
    outcome: '~21 200 kr/mån at 65',
    detail: 'Baseline. AMF Aktiefond continues at current trajectory.',
  },
  {
    title: 'Switch to Low-Cost Index Fund',
    outcome: '~23 800 kr/mån at 65',
    detail: '+12% projected improvement by eliminating 0.6% annual cost drag.',
  },
]

const talkingPoints = [
  'Recap current pension overview and total projected outcome at age 65.',
  'Explain fee drag: how 0.6% cost difference compounds to ~230k SEK by retirement.',
  'Walk through three fund alternatives in Collectum and their risk profiles.',
  'Address the nachlevandeskydd gap — cost is modest relative to coverage benefit.',
  'Discuss whether to consolidate private pension into occupational pension.',
]

const openQuestions = [
  'Has Anna's employment situation at Volvo changed since last review?',
  'Does she have other savings/assets outside the pension system?',
  'What is her actual risk tolerance — has it shifted post-COVID?',
  'Is Lars Pettersson (spouse) covered by a group agreement?',
]

const agenda = [
  { topic: 'Welcome & recap', duration: '5 min', notes: 'Quick recap of previous meeting objectives.' },
  { topic: 'Pension overview walkthrough', duration: '10 min', notes: 'Present the three-pillar summary and projected outcomes.' },
  { topic: 'Key issues deep-dive', duration: '15 min', notes: 'Fund fees, survivor protection gap. Use visuals.' },
  { topic: 'Scenario comparison', duration: '10 min', notes: 'Side-by-side fund comparison; projected outcomes.' },
  { topic: 'Q&A and next steps', duration: '10 min', notes: 'Agree on fund switch and schedule follow-up for WAFÖ.' },
]

export function MeetingPrepCard() {
  const [state, setState] = useState<BriefState>('empty')
  const [step, setStep] = useState(0)

  function handleGenerate() {
    setState('generating')
    setStep(0)
    const interval = setInterval(() => {
      setStep((s) => {
        if (s >= GENERATION_STEPS.length - 1) {
          clearInterval(interval)
          setTimeout(() => setState('generated'), 500)
          return s
        }
        return s + 1
      })
    }, 900)
  }

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
      <div className="flex items-center gap-2.5 border-b border-slate-100 px-5 py-4">
        <ClipboardList className="h-4 w-4 text-slate-500" />
        <h2 className="text-sm font-semibold text-slate-800">Meeting Preparation</h2>
      </div>

      {state === 'empty' && (
        <div className="flex flex-col items-center justify-center py-12">
          <ClipboardList className="mb-3 h-10 w-10 text-slate-200" />
          <p className="mb-1 text-sm font-medium text-slate-600">No brief prepared yet</p>
          <p className="mb-5 text-xs text-slate-400">Generate an AI-powered meeting brief for this case.</p>
          <button
            onClick={handleGenerate}
            className="w-40 rounded-lg bg-sky-500 py-2 text-sm font-medium text-white transition-colors hover:bg-sky-600"
          >
            Prepare Meeting
          </button>
        </div>
      )}

      {state === 'generating' && (
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="mb-4 h-7 w-7 animate-spin text-sky-500" />
          <div className="space-y-2">
            {GENERATION_STEPS.map((s, i) => (
              <div
                key={s}
                className={cn(
                  'flex items-center gap-2 text-sm transition-colors',
                  i <= step ? 'text-slate-700' : 'text-slate-300'
                )}
              >
                <span
                  className={cn(
                    'h-1.5 w-1.5 rounded-full',
                    i < step ? 'bg-sky-500' : i === step ? 'animate-pulse bg-sky-400' : 'bg-slate-200'
                  )}
                />
                {s}
              </div>
            ))}
          </div>
        </div>
      )}

      {state === 'generated' && (
        <div className="space-y-6 px-5 py-5">
          {/* Client Overview */}
          <section>
            <p className="mb-2 text-[10px] font-medium uppercase tracking-wider text-slate-400">Client Overview</p>
            <p className="text-sm leading-relaxed text-slate-600">
              Anna Johansson, 45 år, senior engineer at Volvo Cars. Enrolled in ITP1 collective agreement via Collectum. Annual income ~720 000 SEK. Risk profile: Moderate. Target retirement age: 65. Has been a client since 2021.
            </p>
          </section>

          {/* Pension Situation */}
          <section>
            <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Pension Situation</p>
            <div className="space-y-2">
              {pillars.map((p) => (
                <div
                  key={p.name}
                  className={cn('rounded-lg border-l-4 p-3', p.border, p.bg)}
                >
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-semibold text-slate-700">{p.name}</p>
                    <span className="text-xs font-bold text-slate-800">{p.value}</span>
                  </div>
                  <p className="mt-1 text-xs leading-relaxed text-slate-500">{p.detail}</p>
                </div>
              ))}
              <div className="rounded-lg border-l-4 border-l-sky-400 bg-sky-50 p-3">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-semibold text-slate-700">Total projected at 65</p>
                  <span className="text-sm font-bold text-sky-700">~21 200 kr/mån</span>
                </div>
                <p className="mt-0.5 text-xs text-slate-500">Before income tax. Scenario: current allocation maintained.</p>
              </div>
            </div>
          </section>

          {/* Key Issues */}
          <section>
            <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Key Issues</p>
            <div className="space-y-2">
              {keyIssues.map((issue) => (
                <div
                  key={issue.label}
                  className={cn('flex items-start gap-3 rounded-lg border-l-4 bg-slate-50 p-3', issue.border)}
                >
                  <span className={cn('mt-0.5 shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase', issue.badge)}>
                    {issue.severity}
                  </span>
                  <p className="text-xs leading-relaxed text-slate-600">{issue.label}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Scenarios */}
          <section>
            <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Scenarios</p>
            <div className="grid grid-cols-2 gap-3">
              {scenarios.map((s) => (
                <div key={s.title} className="rounded-lg border border-slate-200 p-3">
                  <p className="text-xs font-semibold text-slate-700">{s.title}</p>
                  <p className="mt-1 text-sm font-bold text-slate-900">{s.outcome}</p>
                  <p className="mt-1 text-xs text-slate-500">{s.detail}</p>
                </div>
              ))}
            </div>
            <div className="mt-3 flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 p-3">
              <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-500" />
              <p className="text-xs text-amber-700">
                Trade-off: switching funds incurs a short-term performance gap during transition. Estimated 2–4 week rebalancing window.
              </p>
            </div>
          </section>

          {/* Talking Points */}
          <section>
            <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Talking Points</p>
            <ol className="space-y-1.5">
              {talkingPoints.map((t, i) => (
                <li key={i} className="flex items-start gap-2.5 text-xs text-slate-600">
                  <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-sky-100 text-[10px] font-bold text-sky-600">
                    {i + 1}
                  </span>
                  {t}
                </li>
              ))}
            </ol>
          </section>

          {/* Open Questions */}
          <section>
            <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Open Questions</p>
            <ul className="space-y-1.5">
              {openQuestions.map((q, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-slate-600">
                  <HelpCircle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400" />
                  {q}
                </li>
              ))}
            </ul>
          </section>

          {/* Agenda */}
          <section>
            <div className="mb-3 flex items-center justify-between">
              <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">Agenda</p>
              <span className="text-xs font-medium text-slate-500">Total: 50 min</span>
            </div>
            <div className="space-y-1">
              {agenda.map((item, i) => (
                <div key={i} className="flex items-start gap-3 rounded-lg p-2 hover:bg-slate-50">
                  <div className="flex flex-col items-center gap-1">
                    <div className="h-2 w-2 rounded-full bg-sky-400" />
                    {i < agenda.length - 1 && <div className="h-6 w-px bg-slate-200" />}
                  </div>
                  <div className="flex-1 pb-1">
                    <div className="flex items-center justify-between">
                      <p className="text-xs font-medium text-slate-700">{item.topic}</p>
                      <span className="text-[10px] font-medium text-slate-400">{item.duration}</span>
                    </div>
                    <p className="mt-0.5 text-[11px] text-slate-400">{item.notes}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <button
            onClick={handleGenerate}
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white py-2 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Regenerate Brief
          </button>
        </div>
      )}
    </div>
  )
}
