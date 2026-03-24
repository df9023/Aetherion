'use client'

import { useState } from 'react'
import { ChevronDown, Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { type Case, type CaseStatus, statusConfig } from '@/lib/data'

const STATUS_ORDER: CaseStatus[] = [
  'draft',
  'in_preparation',
  'ready_for_review',
  'in_review',
  'approved',
  'completed',
]

interface CaseHeaderCardProps {
  caseData: Case
}

export function CaseHeaderCard({ caseData }: CaseHeaderCardProps) {
  const [open, setOpen] = useState(false)
  const [status, setStatus] = useState<CaseStatus>(caseData.status)
  const cfg = statusConfig[status]

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h1 className="text-base font-semibold text-slate-900">{caseData.title}</h1>
          <p className="mt-1 text-sm text-slate-500">{caseData.summary}</p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {/* Status dropdown */}
          <div className="relative">
            <button
              onClick={() => setOpen(!open)}
              className={cn(
                'flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium transition-opacity hover:opacity-80',
                cfg.color
              )}
            >
              {cfg.label}
              <ChevronDown className="h-3 w-3" />
            </button>
            {open && (
              <div className="absolute right-0 top-7 z-10 w-48 rounded-lg border border-slate-200 bg-white py-1 shadow-lg">
                {STATUS_ORDER.map((s) => {
                  const c = statusConfig[s]
                  return (
                    <button
                      key={s}
                      onClick={() => { setStatus(s); setOpen(false) }}
                      className="flex w-full items-center justify-between px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-50"
                    >
                      <span className={cn('rounded-full px-2 py-0.5 font-medium', c.color)}>{c.label}</span>
                      {status === s && <Check className="h-3 w-3 text-sky-500" />}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
          <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
            {caseData.type}
          </span>
        </div>
      </div>
    </div>
  )
}
