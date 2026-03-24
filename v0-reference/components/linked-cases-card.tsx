'use client'

import Link from 'next/link'
import { Briefcase, Plus } from 'lucide-react'
import { cases, getInitials } from '@/lib/data'
import { Button } from '@/components/ui/button'

interface Props {
  clientName: string
}

export function LinkedCasesCard({ clientName }: Props) {
  const linkedCases = cases.filter((c) => c.summary.includes(clientName))
  const statusConfig = {
    draft: 'bg-slate-100 text-slate-600',
    in_preparation: 'bg-blue-50 text-blue-700',
    ready_for_review: 'bg-amber-50 text-amber-700',
    in_review: 'bg-purple-50 text-purple-700',
    approved: 'bg-emerald-50 text-emerald-700',
    completed: 'bg-green-50 text-green-700',
  }

  const statusLabels = {
    draft: 'Draft',
    in_preparation: 'In Preparation',
    ready_for_review: 'Ready for Review',
    in_review: 'In Review',
    approved: 'Approved',
    completed: 'Completed',
  }

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-medium uppercase tracking-wider text-slate-400">
          Linked Cases
        </h3>
        <Button
          variant="outline"
          size="sm"
          className="h-8 gap-1 border-slate-200 text-slate-700"
        >
          <Plus className="h-3 w-3" />
          New Case
        </Button>
      </div>

      {linkedCases.length > 0 ? (
        <div className="space-y-2">
          {linkedCases.map((caseItem) => (
            <Link
              key={caseItem.id}
              href={`/cases/${caseItem.id}`}
              className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors group"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 truncate group-hover:text-sky-600">
                  {caseItem.title}
                </p>
                <p className="text-xs text-slate-400 mt-0.5">{caseItem.updated}</p>
              </div>
              <div className="flex items-center gap-2 ml-2 flex-shrink-0">
                <div
                  className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${
                    statusConfig[caseItem.status as keyof typeof statusConfig]
                  }`}
                >
                  {statusLabels[caseItem.status as keyof typeof statusLabels]}
                </div>
                <div className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600">
                  {caseItem.type}
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-6">
          <Briefcase className="h-8 w-8 text-slate-300 mx-auto mb-2" />
          <p className="text-sm text-slate-400">No cases yet</p>
        </div>
      )}
    </div>
  )
}
