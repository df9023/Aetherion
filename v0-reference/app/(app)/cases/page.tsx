'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Briefcase, Clock, Users, CheckCircle, Plus, Inbox } from 'lucide-react'
import { cases, statusConfig, getInitials, type CaseStatus, type CaseType } from '@/lib/data'
import { cn } from '@/lib/utils'
import { Topbar } from '@/components/topbar'
import { CreateCaseDialog } from '@/components/create-case-dialog'

const STATUS_FILTERS: { value: CaseStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'draft', label: 'Draft' },
  { value: 'in_preparation', label: 'In Preparation' },
  { value: 'ready_for_review', label: 'Ready for Review' },
  { value: 'in_review', label: 'In Review' },
  { value: 'approved', label: 'Approved' },
  { value: 'completed', label: 'Completed' },
]

const TYPE_FILTERS: { value: CaseType | 'all'; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'Retirement Planning', label: 'Retirement Planning' },
  { value: 'Salary Exchange', label: 'Salary Exchange' },
  { value: 'Pension Review', label: 'Pension Review' },
]

const stats = [
  { icon: Briefcase, number: 4, label: 'Active Cases', bg: 'bg-sky-50 border-sky-100', iconColor: 'text-sky-500' },
  { icon: Clock, number: 1, label: 'Pending Review', bg: 'bg-amber-50 border-amber-100', iconColor: 'text-amber-500' },
  { icon: Users, number: 2, label: 'Clients', bg: 'bg-emerald-50 border-emerald-100', iconColor: 'text-emerald-500' },
  { icon: CheckCircle, number: 0, label: 'Completed', bg: 'bg-slate-50 border-slate-100', iconColor: 'text-slate-400' },
]

export default function CasesDashboard() {
  const [statusFilter, setStatusFilter] = useState<CaseStatus | 'all'>('all')
  const [typeFilter, setTypeFilter] = useState<CaseType | 'all'>('all')
  const [search, setSearch] = useState('')
  const [openCreateDialog, setOpenCreateDialog] = useState(false)

  const filtered = cases.filter((c) => {
    if (statusFilter !== 'all' && c.status !== statusFilter) return false
    if (typeFilter !== 'all' && c.type !== typeFilter) return false
    if (search && !c.title.toLowerCase().includes(search.toLowerCase()) && !c.summary.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <>
      <CreateCaseDialog open={openCreateDialog} onOpenChange={setOpenCreateDialog} />
      <Topbar breadcrumbs={[{ label: 'Cases' }]} />
      <main className="flex-1 px-6 py-6">
        {/* Stats bar */}
        <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
          {stats.map(({ icon: Icon, number, label, bg, iconColor }) => (
            <div
              key={label}
              className={cn('flex items-center gap-4 rounded-xl border p-4 shadow-sm', bg)}
            >
              <div className={cn('rounded-lg p-2', bg)}>
                <Icon className={cn('h-5 w-5', iconColor)} />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{number}</p>
                <p className="text-xs text-slate-500">{label}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Header */}
        <div className="mb-5 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-slate-900">Cases</h1>
          <button onClick={() => setOpenCreateDialog(true)} className="flex items-center gap-2 rounded-lg bg-sky-500 px-3 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-sky-600">
            <Plus className="h-4 w-4" />
            New Case
          </button>
        </div>

        {/* Filters */}
        <div className="mb-4 space-y-2">
          <div className="flex flex-wrap items-center gap-1">
            {STATUS_FILTERS.map((f) => (
              <button
                key={f.value}
                onClick={() => setStatusFilter(f.value as CaseStatus | 'all')}
                className={cn(
                  'rounded-full px-3 py-1 text-xs font-medium transition-colors',
                  statusFilter === f.value
                    ? 'bg-sky-500 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                )}
              >
                {f.label}
              </button>
            ))}
            <span className="mx-1 text-slate-300">|</span>
            {TYPE_FILTERS.map((f) => (
              <button
                key={f.value}
                onClick={() => setTypeFilter(f.value as CaseType | 'all')}
                className={cn(
                  'rounded-full px-3 py-1 text-xs font-medium transition-colors',
                  typeFilter === f.value
                    ? 'bg-sky-500 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                )}
              >
                {f.label}
              </button>
            ))}
          </div>
          <input
            type="text"
            placeholder="Search cases..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/30 sm:w-80"
          />
        </div>

        {/* Case list */}
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-xl border border-slate-200/60 bg-white py-16 shadow-sm">
            <Inbox className="mb-3 h-12 w-12 text-slate-300" />
            <p className="mb-1 text-sm font-medium text-slate-600">No cases found</p>
            <p className="mb-4 text-xs text-slate-400">Try adjusting your filters or create a new case.</p>
            <button onClick={() => setOpenCreateDialog(true)} className="flex items-center gap-2 rounded-lg bg-sky-500 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-sky-600">
              <Plus className="h-4 w-4" />
              New Case
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            {filtered.map((c) => {
              const cfg = statusConfig[c.status]
              const initials = getInitials(
                c.title.split('—')[1]?.trim() ?? c.title
              )
              return (
                <Link
                  key={c.id}
                  href={`/cases/${c.id}`}
                  className="group block overflow-hidden rounded-xl border border-l-4 border-transparent border-slate-200/60 bg-white shadow-sm transition-all duration-200 hover:border-l-sky-400 hover:shadow-md"
                >
                  {/* Progress bar */}
                  <div className="h-[3px] w-full bg-slate-100">
                    <div
                      className={cn('h-full transition-all', cfg.progressColor)}
                      style={{ width: `${cfg.progress}%` }}
                    />
                  </div>
                  <div className="flex items-start gap-4 px-4 py-3.5">
                    {/* Avatar */}
                    <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-600">
                      {initials}
                    </div>
                    {/* Content */}
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-start justify-between gap-2">
                        <p className="text-sm font-medium text-slate-900 group-hover:text-sky-600">
                          {c.title}
                        </p>
                        <div className="flex shrink-0 items-center gap-2">
                          <span
                            className={cn(
                              'rounded-full px-2.5 py-0.5 text-xs font-medium',
                              cfg.color
                            )}
                          >
                            {cfg.label}
                          </span>
                          <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                            {c.type}
                          </span>
                        </div>
                      </div>
                      <p className="mt-0.5 line-clamp-1 text-xs text-slate-500">
                        {c.summary}
                      </p>
                    </div>
                  </div>
                  {/* Footer */}
                  <div className="flex items-center gap-1.5 border-t border-slate-100 px-4 py-2">
                    <Clock className="h-3 w-3 text-slate-300" />
                    <span className="text-xs text-slate-400">
                      {c.advisor} · {c.updated}
                    </span>
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </main>
    </>
  )
}
