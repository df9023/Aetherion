"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { Briefcase, Clock, Users, CheckCircle, Plus, Inbox } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import { useCases, useClients } from "@/lib/hooks"
import { caseTypeLabels, statusStyles, statusLabels } from "@/lib/labels"
import { CreateCaseDialog } from "@/components/create-case-dialog"
import { TopBar } from "@/components/top-bar"
import { cn } from "@/lib/utils"

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return "Idag"
  if (days === 1) return "Igår"
  return `${days} dagar sedan`
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

const STATUS_FILTERS = [
  { value: "all", label: "Alla" },
  { value: "draft", label: "Utkast" },
  { value: "in_preparation", label: "Under arbete" },
  { value: "ready_for_review", label: "Redo för granskning" },
  { value: "in_review", label: "Granskas" },
  { value: "approved", label: "Godkänd" },
  { value: "completed", label: "Avslutad" },
]

const TYPE_FILTERS = [
  { value: "all", label: "Alla" },
  ...Object.entries(caseTypeLabels).map(([value, label]) => ({ value, label })),
]

export default function CasesPage() {
  const { data: cases, isLoading } = useCases()
  const { data: clients } = useClients()
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [typeFilter, setTypeFilter] = useState("all")
  const [openCreateDialog, setOpenCreateDialog] = useState(false)

  const clientMap = useMemo(() => {
    const map = new Map<string, string>()
    for (const c of clients ?? []) {
      map.set(c.id, c.name)
    }
    return map
  }, [clients])

  const allCases = cases ?? []
  const activeCases = allCases.filter((c) => c.status !== "archived")
  const pendingReview = allCases.filter((c) => c.status === "ready_for_review" || c.status === "in_review")
  const uniqueClients = new Set(allCases.map((c) => c.client_id)).size
  const completedCases = allCases.filter((c) => c.status === "completed")

  const stats = [
    { icon: Briefcase, number: activeCases.length, label: "Aktiva ärenden", bg: "bg-sky-50 border-sky-100", iconColor: "text-sky-500" },
    { icon: Clock, number: pendingReview.length, label: "Väntar granskning", bg: "bg-amber-50 border-amber-100", iconColor: "text-amber-500" },
    { icon: Users, number: uniqueClients, label: "Klienter", bg: "bg-emerald-50 border-emerald-100", iconColor: "text-emerald-500" },
    { icon: CheckCircle, number: completedCases.length, label: "Avslutade", bg: "bg-slate-50 border-slate-100", iconColor: "text-slate-400" },
  ]

  const filtered = allCases.filter((c) => {
    if (search && !c.title.toLowerCase().includes(search.toLowerCase()) && !(c.summary ?? "").toLowerCase().includes(search.toLowerCase())) return false
    if (statusFilter !== "all" && c.status !== statusFilter) return false
    if (typeFilter !== "all" && c.case_type !== typeFilter) return false
    return true
  })

  return (
    <>
      <CreateCaseDialog open={openCreateDialog} onOpenChange={setOpenCreateDialog} />
      <TopBar breadcrumbs={[{ label: "Ärenden" }]} />
      <main className="flex-1 px-6 py-6">
        {/* Stats bar */}
        {!isLoading && (
          <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
            {stats.map(({ icon: Icon, number, label, bg, iconColor }) => (
              <div key={label} className={cn("flex items-center gap-4 rounded-xl border p-4 shadow-sm", bg)}>
                <div className={cn("rounded-lg p-2", bg)}>
                  <Icon className={cn("h-5 w-5", iconColor)} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900">{number}</p>
                  <p className="text-sm text-slate-500">{label}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Header */}
        <div className="mb-5 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-slate-900">Ärenden</h1>
          <button
            onClick={() => setOpenCreateDialog(true)}
            className="flex items-center gap-2 rounded-lg bg-sky-500 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-sky-600"
          >
            <Plus className="h-4 w-4" />
            Nytt ärende
          </button>
        </div>

        {/* Filters */}
        <div className="mb-4 space-y-3">
          <div className="flex flex-wrap items-center gap-1.5">
            {STATUS_FILTERS.map((f) => (
              <button
                key={f.value}
                onClick={() => setStatusFilter(f.value)}
                className={cn(
                  "rounded-full px-3 py-1.5 text-sm font-medium transition-colors",
                  statusFilter === f.value
                    ? "bg-sky-500 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                )}
              >
                {f.label}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {TYPE_FILTERS.map((f) => (
              <button
                key={f.value}
                onClick={() => setTypeFilter(f.value)}
                className={cn(
                  "rounded-full px-3 py-1.5 text-sm font-medium transition-colors",
                  typeFilter === f.value
                    ? "bg-sky-500 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                )}
              >
                {f.label}
              </button>
            ))}
          </div>
          <input
            type="text"
            placeholder="Sök ärenden..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/30 sm:w-80"
          />
        </div>

        {/* Loading skeletons */}
        {isLoading && (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="mt-2 h-3 w-1/2" />
                <Skeleton className="mt-3 h-3 w-1/4" />
              </div>
            ))}
          </div>
        )}

        {/* Case list */}
        {!isLoading && filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-xl border border-slate-200/60 bg-white py-16 shadow-sm">
            <Inbox className="mb-3 h-12 w-12 text-slate-300" />
            <p className="mb-1 text-base font-medium text-slate-600">Inga ärenden hittades</p>
            <p className="mb-4 text-sm text-slate-400">Försök justera dina filter eller skapa ett nytt ärende.</p>
            <button
              onClick={() => setOpenCreateDialog(true)}
              className="flex items-center gap-2 rounded-lg bg-sky-500 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-sky-600"
            >
              <Plus className="h-4 w-4" />
              Nytt ärende
            </button>
          </div>
        ) : (
          !isLoading && (
            <div className="space-y-2">
              {filtered.map((c) => {
                const progress = STATUS_PROGRESS[c.status]
                const clientName = clientMap.get(c.client_id)
                const initials = clientName
                  ? clientName.split(" ").map((n) => n[0]).join("")
                  : "?"

                return (
                  <Link
                    key={c.id}
                    href={`/cases/${c.id}`}
                    className="group block overflow-hidden rounded-xl border border-l-4 border-transparent border-slate-200/60 bg-white shadow-sm transition-all duration-200 hover:border-l-sky-400 hover:shadow-md"
                  >
                    {progress && (
                      <div className="h-[3px] w-full bg-slate-100">
                        <div className={cn("h-full transition-all", progress.color)} style={{ width: progress.width }} />
                      </div>
                    )}
                    <div className="flex items-start gap-4 px-5 py-4">
                      <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-slate-100 text-sm font-semibold text-slate-600">
                        {initials}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-start justify-between gap-2">
                          <p className="text-sm font-semibold text-slate-900 group-hover:text-sky-600">
                            {c.title}
                          </p>
                          <div className="flex shrink-0 items-center gap-2">
                            <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-medium", statusStyles[c.status] ?? "")}>
                              {statusLabels[c.status] ?? c.status}
                            </span>
                            <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                              {caseTypeLabels[c.case_type] ?? c.case_type}
                            </span>
                          </div>
                        </div>
                        <p className="mt-1 line-clamp-1 text-sm text-slate-500">
                          {c.summary}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 border-t border-slate-100 px-5 py-2.5">
                      <Clock className="h-3.5 w-3.5 text-slate-300" />
                      <span className="text-xs text-slate-400">
                        {clientName ?? "—"} · {timeAgo(c.updated_at)}
                      </span>
                    </div>
                  </Link>
                )
              })}
            </div>
          )
        )}
      </main>
    </>
  )
}
