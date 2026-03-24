"use client"

import Link from "next/link"
import { Briefcase, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { statusStyles, statusLabels, caseTypeLabels } from "@/lib/labels"
import type { CaseResponse } from "@/lib/hooks"

interface LinkedCasesCardProps {
  cases: CaseResponse[]
  isLoading: boolean
  createCaseButton: React.ReactNode
}

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return "Today"
  if (days === 1) return "Yesterday"
  return `${days} days ago`
}

export function LinkedCasesCard({ cases, isLoading, createCaseButton }: LinkedCasesCardProps) {
  return (
    <div className="rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-xs font-medium uppercase tracking-wider text-slate-400">
          Linked Cases
        </h3>
        {createCaseButton}
      </div>

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-16 rounded-lg" />
          ))}
        </div>
      )}

      {!isLoading && cases.length > 0 && (
        <div className="space-y-2">
          {cases.map((caseItem) => (
            <Link
              key={caseItem.id}
              href={`/cases/${caseItem.id}`}
              className="group flex items-center justify-between rounded-lg p-3 transition-colors hover:bg-slate-50"
            >
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-slate-900 group-hover:text-sky-600">
                  {caseItem.title}
                </p>
                <p className="mt-0.5 text-xs text-slate-400">{timeAgo(caseItem.updated_at)}</p>
              </div>
              <div className="ml-2 flex shrink-0 items-center gap-2">
                <div className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${statusStyles[caseItem.status] ?? ""}`}>
                  {statusLabels[caseItem.status] ?? caseItem.status}
                </div>
                <div className="inline-flex rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                  {caseTypeLabels[caseItem.case_type] ?? caseItem.case_type}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {!isLoading && cases.length === 0 && (
        <div className="py-6 text-center">
          <Briefcase className="mx-auto mb-2 h-8 w-8 text-slate-300" />
          <p className="text-sm text-slate-400">No cases yet</p>
        </div>
      )}
    </div>
  )
}
