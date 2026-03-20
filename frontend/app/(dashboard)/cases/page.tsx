"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { Search, Clock, Briefcase, AlertCircle, Users, CheckCircle, FolderOpen, User } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { useCases, useClients } from "@/lib/hooks"
import { caseTypeLabels, statusStyles, statusLabels } from "@/lib/labels"
import { CreateCaseDialog } from "@/components/create-case-dialog"

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return "Today"
  if (days === 1) return "Yesterday"
  return `${days} days ago`
}

const STATUS_PROGRESS: Record<string, { width: string; color: string }> = {
  draft: { width: "15%", color: "bg-slate-300" },
  in_preparation: { width: "30%", color: "bg-blue-400" },
  ready_for_review: { width: "50%", color: "bg-amber-400" },
  in_review: { width: "70%", color: "bg-purple-400" },
  approved: { width: "85%", color: "bg-emerald-400" },
  completed: { width: "100%", color: "bg-green-500" },
  archived: { width: "100%", color: "bg-slate-300" },
}

export default function CasesPage() {
  const { data: cases, isLoading } = useCases()
  const { data: clients } = useClients()
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [typeFilter, setTypeFilter] = useState<string>("all")

  // Build client lookup by ID
  const clientMap = useMemo(() => {
    const map = new Map<string, string>()
    for (const c of clients ?? []) {
      map.set(c.id, c.name)
    }
    return map
  }, [clients])

  // Stats
  const allCases = cases ?? []
  const activeCases = allCases.filter((c) => c.status !== "archived")
  const pendingReview = allCases.filter((c) => c.status === "ready_for_review" || c.status === "in_review")
  const completedThisMonth = allCases.filter((c) => {
    if (c.status !== "completed") return false
    const d = new Date(c.updated_at)
    const now = new Date()
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
  })

  const filtered = allCases.filter((c) => {
    if (search && !c.title.toLowerCase().includes(search.toLowerCase())) return false
    if (statusFilter !== "all" && c.status !== statusFilter) return false
    if (typeFilter !== "all" && c.case_type !== typeFilter) return false
    return true
  })

  return (
    <div className="animate-[fadeIn_0.3s_ease-out]">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Cases</h1>
        <CreateCaseDialog />
      </div>

      {/* Stats bar */}
      {!isLoading && (
        <div className="mt-6 grid grid-cols-4 gap-4">
          <StatCard icon={Briefcase} label="Active Cases" value={activeCases.length} tint="bg-sky-50" iconColor="text-sky-500" />
          <StatCard icon={AlertCircle} label="Pending Review" value={pendingReview.length} tint="bg-amber-50" iconColor="text-amber-500" />
          <StatCard icon={Users} label="Total Clients" value={clients?.length ?? 0} tint="bg-emerald-50" iconColor="text-emerald-500" />
          <StatCard icon={CheckCircle} label="Completed This Month" value={completedThisMonth.length} tint="bg-slate-50" iconColor="text-slate-500" />
        </div>
      )}

      {/* Search + filter pills */}
      <div className="mt-6 space-y-3">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <Input
            placeholder="Search cases..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
            data-search-input
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {/* Status pills */}
          <FilterPill active={statusFilter === "all"} onClick={() => setStatusFilter("all")}>All Statuses</FilterPill>
          {Object.entries(statusLabels).map(([val, label]) => (
            <FilterPill key={val} active={statusFilter === val} onClick={() => setStatusFilter(val)}>
              {label}
            </FilterPill>
          ))}

          <div className="mx-1 h-5 w-px bg-slate-200" />

          {/* Type pills */}
          <FilterPill active={typeFilter === "all"} onClick={() => setTypeFilter("all")}>All Types</FilterPill>
          {Object.entries(caseTypeLabels).map(([val, label]) => (
            <FilterPill key={val} active={typeFilter === val} onClick={() => setTypeFilter(val)}>
              {label}
            </FilterPill>
          ))}
        </div>
      </div>

      {/* Case list */}
      <div className="mt-6 space-y-3">
        {isLoading &&
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="mt-2 h-3 w-1/2" />
              <Skeleton className="mt-3 h-3 w-1/4" />
            </div>
          ))}

        {!isLoading &&
          filtered.map((c) => {
            const progress = STATUS_PROGRESS[c.status]
            const clientName = clientMap.get(c.client_id)
            const initials = clientName
              ? clientName.split(" ").map((n) => n[0]).join("")
              : "?"

            return (
              <Link key={c.id} href={`/cases/${c.id}`}>
                <div className="overflow-hidden rounded-xl border border-l-4 border-slate-200/60 border-l-transparent bg-white shadow-sm transition-all duration-200 hover:border-l-sky-400 hover:border-slate-300 hover:shadow-md">
                  {/* Progress bar */}
                  {progress && (
                    <div className="h-1 w-full bg-slate-100">
                      <div className={`h-full ${progress.color} transition-all duration-500`} style={{ width: progress.width }} />
                    </div>
                  )}

                  <div className="p-5">
                    <div className="flex items-start gap-3">
                      {/* Client avatar */}
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-medium text-slate-600">
                        {initials}
                      </div>

                      <div className="min-w-0 flex-1">
                        <div className="flex items-start justify-between">
                          <div className="min-w-0 flex-1">
                            <h3 className="text-sm font-semibold text-slate-900">{c.title}</h3>
                            <p className="mt-1 text-sm text-slate-500 line-clamp-1">{c.summary}</p>
                          </div>
                          <div className="ml-4 flex items-center gap-2">
                            <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${statusStyles[c.status] ?? ""}`}>
                              {statusLabels[c.status] ?? c.status}
                            </span>
                            <span className="inline-flex rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                              {caseTypeLabels[c.case_type] ?? c.case_type}
                            </span>
                          </div>
                        </div>
                        <div className="mt-3 flex items-center gap-4 text-xs text-slate-400">
                          <span className="flex items-center gap-1">
                            <User className="h-3 w-3" />
                            Maria Lindqvist
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-3.5 w-3.5" />
                            {timeAgo(c.updated_at)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            )
          })}

        {!isLoading && filtered.length === 0 && (
          <div className="flex flex-col items-center py-16">
            <FolderOpen className="h-12 w-12 text-slate-300" />
            <p className="mt-4 text-sm font-medium text-slate-600">No cases found</p>
            <p className="mt-1 text-xs text-slate-400">Try adjusting your filters or create a new case</p>
            <div className="mt-4">
              <CreateCaseDialog />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({
  icon: Icon,
  label,
  value,
  tint,
  iconColor,
}: {
  icon: React.ComponentType<{ className?: string }>
  label: string
  value: number
  tint: string
  iconColor: string
}) {
  return (
    <div className={`flex items-center gap-3 rounded-xl ${tint} p-4`}>
      <Icon className={`h-5 w-5 ${iconColor}`} />
      <div>
        <p className="text-2xl font-bold text-slate-900">{value}</p>
        <p className="text-xs text-slate-500">{label}</p>
      </div>
    </div>
  )
}

function FilterPill({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      onClick={onClick}
      className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium transition-colors ${
        active
          ? "bg-sky-500 text-white"
          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
      }`}
    >
      {children}
    </button>
  )
}
