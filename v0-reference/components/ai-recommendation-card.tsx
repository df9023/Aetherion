'use client'

import { useState } from 'react'
import { Sparkles, Loader2, RefreshCw, Download, FileText, CheckCircle2, TrendingUp, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

type RecoState = 'empty' | 'generating' | 'generated'

const GENERATION_STEPS = [
  'Retrieving applicable regulations (FFFS 2007:16)',
  'Scoring suitability against client profile',
  'Drafting recommendation rationale',
]

const evidenceCards = [
  { title: 'FFFS 2007:16, §8', category: 'Regulation', snippet: 'Advisor must document the basis of each recommendation in writing prior to execution.' },
  { title: 'ITP1 Plan Document 2024', category: 'Product', snippet: 'Collectum offers 9 approved low-cost index funds with TER 0.05%–0.22%.' },
  { title: 'SPP Internal Policy', category: 'Policy', snippet: 'Fund switching requests must be submitted via KYC-verified advisor portal.' },
]

const reasoningChain = [
  { type: 'system', label: 'Client profile loaded — Moderate risk, age 45, ITP1' },
  { type: 'system', label: 'Regulation FFFS 2007:16 applied — suitability requirements verified' },
  { type: 'system', label: 'Cost analysis: current fund TER 0.8%, best-match alternative 0.18%' },
  { type: 'system', label: 'Suitability score calculated: 87/100' },
  { type: 'user', label: 'Recommendation finalized and ready for advisor review' },
]

export function AIRecommendationCard() {
  const [state, setState] = useState<RecoState>('empty')
  const [step, setStep] = useState(0)

  function handleGenerate() {
    setState('generating')
    setStep(0)
    const interval = setInterval(() => {
      setStep((s) => {
        if (s >= GENERATION_STEPS.length - 1) {
          clearInterval(interval)
          setTimeout(() => setState('generated'), 600)
          return s
        }
        return s + 1
      })
    }, 900)
  }

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
      <div className="flex items-center gap-2.5 border-b border-slate-100 px-5 py-4">
        <Sparkles className="h-4 w-4 text-sky-500" />
        <h2 className="text-sm font-semibold text-slate-800">AI Recommendation</h2>
        <span className="ml-auto rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-500">
          v2.4
        </span>
      </div>

      {state === 'empty' && (
        <div className="flex flex-col items-center justify-center py-10">
          <Sparkles className="mb-3 h-10 w-10 text-slate-200" />
          <p className="mb-1 text-sm font-medium text-slate-600">No recommendation generated</p>
          <p className="mb-5 text-xs text-slate-400">Generate a suitability-assessed AI recommendation.</p>
          <button
            onClick={handleGenerate}
            className="flex items-center gap-2 rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-sky-600"
          >
            <Sparkles className="h-4 w-4" />
            Generate Recommendation
          </button>
        </div>
      )}

      {state === 'generating' && (
        <div className="flex flex-col items-center justify-center py-10">
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
          {/* Suitability score */}
          <div>
            <div className="mb-2 flex items-center justify-between">
              <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">Suitability Score</p>
              <span className="text-sm font-bold text-emerald-600">87 / 100</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
              <div className="h-full rounded-full bg-emerald-500 transition-all" style={{ width: '87%' }} />
            </div>
            <p className="mt-1 text-xs text-slate-400">High suitability — recommendation is well-aligned with client profile and regulations.</p>
          </div>

          {/* Summary */}
          <section>
            <p className="mb-2 text-[10px] font-medium uppercase tracking-wider text-slate-400">Recommendation Summary</p>
            <p className="text-sm leading-relaxed text-slate-600">
              Switch Anna Johansson's ITP1 allocation from AMF Aktiefond (TER 0.80%) to Länsförsäkringar Global Index (TER 0.18%). This reduces annual cost drag by 0.62% on an approximate 840 000 SEK pension capital, potentially adding ~230 000 SEK to final pension value by age 65. Additionally, activate efterlevandeskydd (survivor protection) at 0.1% of insured amount to close identified coverage gap.
            </p>
          </section>

          {/* Reasoning chain */}
          <section>
            <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Reasoning Chain</p>
            <div className="relative space-y-3 pl-4">
              <div className="absolute left-[7px] top-0 h-full w-px bg-slate-100" />
              {reasoningChain.map((item, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div
                    className={cn(
                      'relative z-10 flex h-3.5 w-3.5 shrink-0 items-center justify-center rounded-full',
                      item.type === 'system'
                        ? 'bg-sky-100 ring-2 ring-sky-400'
                        : 'bg-slate-100 ring-2 ring-slate-300'
                    )}
                  >
                    <div
                      className={cn(
                        'h-1.5 w-1.5 rounded-full',
                        item.type === 'system' ? 'bg-sky-500' : 'bg-slate-400'
                      )}
                    />
                  </div>
                  <p className="text-xs leading-relaxed text-slate-600">{item.label}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Assumptions */}
          <section>
            <p className="mb-2 text-[10px] font-medium uppercase tracking-wider text-slate-400">Assumptions</p>
            <ul className="space-y-1">
              {[
                'Annual return of 6% assumed for both fund scenarios.',
                'No change in contribution rate or employment status.',
                'SEK/EUR exchange rate assumed stable for foreign equity exposure.',
              ].map((a, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-slate-500">
                  <AlertCircle className="mt-0.5 h-3 w-3 shrink-0 text-amber-400" />
                  {a}
                </li>
              ))}
            </ul>
          </section>

          {/* Scenarios grid */}
          <section>
            <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Projected Scenarios</p>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg border border-slate-200 p-3">
                <div className="mb-1 flex items-center gap-1.5">
                  <TrendingUp className="h-3.5 w-3.5 text-slate-400" />
                  <p className="text-xs font-medium text-slate-600">Status Quo</p>
                </div>
                <p className="text-base font-bold text-slate-900">~1 820 000 kr</p>
                <p className="text-[11px] text-slate-400">at age 65 · ~21 200 kr/mån</p>
              </div>
              <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
                <div className="mb-1 flex items-center gap-1.5">
                  <TrendingUp className="h-3.5 w-3.5 text-emerald-500" />
                  <p className="text-xs font-medium text-emerald-700">Recommended</p>
                </div>
                <p className="text-base font-bold text-emerald-800">~2 050 000 kr</p>
                <p className="text-[11px] text-emerald-600">at age 65 · ~23 800 kr/mån</p>
              </div>
            </div>
          </section>

          {/* Evidence cards */}
          <section>
            <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Supporting Evidence</p>
            <div className="space-y-2">
              {evidenceCards.map((e) => (
                <div key={e.title} className="rounded-lg border border-slate-200 p-3">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-semibold text-slate-700">{e.title}</p>
                    <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] text-slate-500">{e.category}</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">{e.snippet}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Action buttons */}
          <div className="flex flex-col gap-2">
            <button className="flex items-center justify-center gap-2 rounded-lg bg-sky-500 py-2.5 text-sm font-medium text-white transition-colors hover:bg-sky-600">
              <FileText className="h-4 w-4" />
              Generate Document
            </button>
            <div className="grid grid-cols-2 gap-2">
              <button className="flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white py-2 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50">
                <Download className="h-3.5 w-3.5" />
                Download DOCX
              </button>
              <button
                onClick={handleGenerate}
                className="flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white py-2 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                New Version
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
