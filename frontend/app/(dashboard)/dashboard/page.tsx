"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import {
  Briefcase,
  Clock,
  CheckCircle,
  CalendarDays,
  Plus,
  UserPlus,
  ArrowRight,
  CircleCheck,
  FileText,
  Sparkles,
  Calendar,
  AlertCircle,
  Bot,
  User,
} from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import {
  useCases,
  useClients,
  useRecentAudit,
  type CaseResponse,
  type AuditEntryResponse,
} from "@/lib/hooks"
import {
  statusLabels,
  statusStyles,
  caseTypeLabels,
  auditActionLabels,
} from "@/lib/labels"
import { CreateCaseDialog } from "@/components/create-case-dialog"
import { CreateClientDialog } from "@/components/create-client-dialog"
import { TopBar } from "@/components/top-bar"
import { cn } from "@/lib/utils"

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getGreeting(): string {
  const hour = new Date().getHours()
  if (hour < 12) return "God morgon"
  if (hour < 17) return "God eftermiddag"
  return "God kväll"
}

function formatSwedishDate(d: Date): string {
  const days = [
    "söndag",
    "måndag",
    "tisdag",
    "onsdag",
    "torsdag",
    "fredag",
    "lördag",
  ]
  const months = [
    "januari",
    "februari",
    "mars",
    "april",
    "maj",
    "juni",
    "juli",
    "augusti",
    "september",
    "oktober",
    "november",
    "december",
  ]
  return `${days[d.getDay()]} ${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`
}

function isThisWeek(dateStr: string): boolean {
  const d = new Date(dateStr)
  const now = new Date()
  const startOfWeek = new Date(now)
  startOfWeek.setDate(now.getDate() - now.getDay() + 1)
  startOfWeek.setHours(0, 0, 0, 0)
  const endOfWeek = new Date(startOfWeek)
  endOfWeek.setDate(startOfWeek.getDate() + 7)
  return d >= startOfWeek && d < endOfWeek
}

function isThisMonth(dateStr: string | null): boolean {
  if (!dateStr) return false
  const d = new Date(dateStr)
  const now = new Date()
  return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return "Just nu"
  if (minutes < 60) return `${minutes} min sedan`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} tim sedan`
  const days = Math.floor(hours / 24)
  if (days === 1) return "Igår"
  return `${days} dagar sedan`
}

function formatSwedishShortDate(dateStr: string): string {
  const d = new Date(dateStr)
  const months = [
    "jan",
    "feb",
    "mar",
    "apr",
    "maj",
    "jun",
    "jul",
    "aug",
    "sep",
    "okt",
    "nov",
    "dec",
  ]
  return `${d.getDate()} ${months[d.getMonth()]}`
}

function isWithinDays(dateStr: string, days: number): boolean {
  const d = new Date(dateStr)
  const now = new Date()
  const future = new Date(now)
  future.setDate(now.getDate() + days)
  return d >= now && d <= future
}

// ---------------------------------------------------------------------------
// Metric card
// ---------------------------------------------------------------------------

function MetricCard({
  icon: Icon,
  value,
  label,
  accent,
  iconColor,
}: {
  icon: React.ElementType
  value: number
  label: string
  accent: string
  iconColor: string
}) {
  return (
    <div
      className={cn(
        "flex items-center gap-4 rounded-xl border p-4 shadow-sm",
        accent
      )}
    >
      <div className={cn("rounded-lg p-2", accent)}>
        <Icon className={cn("h-5 w-5", iconColor)} />
      </div>
      <div>
        <p className="text-2xl font-bold text-slate-900">{value}</p>
        <p className="text-sm text-slate-500">{label}</p>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export default function DashboardPage() {
  const { data: cases, isLoading: casesLoading } = useCases()
  const { data: clients } = useClients()
  const { data: recentAudit, isLoading: auditLoading } = useRecentAudit(10)

  const [openCreateCase, setOpenCreateCase] = useState(false)
  const [openCreateClient, setOpenCreateClient] = useState(false)

  const clientMap = useMemo(() => {
    const map = new Map<string, string>()
    for (const c of clients ?? []) {
      map.set(c.id, c.name)
    }
    return map
  }, [clients])

  const allCases = cases ?? []

  // Metrics
  const activeCases = allCases.filter(
    (c) => c.status !== "archived" && c.status !== "completed"
  )
  const awaitingReview = allCases.filter(
    (c) => c.status === "ready_for_review" || c.status === "in_review"
  )
  const meetingsThisWeek = allCases.filter(
    (c) => c.meeting_date && isThisWeek(c.meeting_date)
  )
  const completedThisMonth = allCases.filter(
    (c) => c.status === "completed" && isThisMonth(c.completed_at)
  )

  // Cases needing attention — ordered by urgency
  const needsAttention = useMemo(() => {
    const review = allCases.filter((c) => c.status === "ready_for_review")
    const drafts = allCases.filter((c) => c.status === "draft")
    const upcomingNoRec = allCases.filter(
      (c) =>
        c.meeting_date &&
        isWithinDays(c.meeting_date, 3) &&
        c.status !== "completed" &&
        c.status !== "archived" &&
        c.status !== "approved"
    )
    // Deduplicate (a case might be both draft and have an upcoming meeting)
    const seen = new Set<string>()
    const result: CaseResponse[] = []
    for (const list of [review, upcomingNoRec, drafts]) {
      for (const c of list) {
        if (!seen.has(c.id)) {
          seen.add(c.id)
          result.push(c)
        }
      }
    }
    return result.slice(0, 5)
  }, [allCases])

  // Upcoming meetings
  const upcomingMeetings = useMemo(() => {
    const now = new Date()
    return allCases
      .filter((c) => c.meeting_date && new Date(c.meeting_date) >= now)
      .sort(
        (a, b) =>
          new Date(a.meeting_date!).getTime() -
          new Date(b.meeting_date!).getTime()
      )
      .slice(0, 5)
  }, [allCases])

  // Monthly stats from audit
  const monthlyStats = useMemo(() => {
    const entries = recentAudit ?? []
    // We only have last 10 entries — count what we can.
    // For a real implementation we'd want a dedicated stats endpoint.
    const now = new Date()
    const thisMonth = entries.filter((e) => {
      const d = new Date(e.timestamp)
      return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
    })
    return {
      recommendations: thisMonth.filter(
        (e) => e.action === "recommendation_generated"
      ).length,
      documents: thisMonth.filter((e) => e.action === "document_generated")
        .length,
      completed: completedThisMonth.length,
    }
  }, [recentAudit, completedThisMonth])

  const isLoading = casesLoading

  return (
    <>
      <CreateCaseDialog
        open={openCreateCase}
        onOpenChange={setOpenCreateCase}
      />
      <CreateClientDialog
        open={openCreateClient}
        onOpenChange={setOpenCreateClient}
      />
      <TopBar breadcrumbs={[{ label: "Översikt" }]} />

      <main className="flex-1 px-6 py-6">
        {/* --- Greeting header --- */}
        <div className="mb-6 flex items-start justify-between">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">
              {getGreeting()}, Erik
            </h1>
            <p className="mt-0.5 text-sm text-slate-500">
              {formatSwedishDate(new Date())}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setOpenCreateCase(true)}
              className="flex items-center gap-2 rounded-lg bg-sky-500 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-sky-600"
            >
              <Plus className="h-4 w-4" />
              Nytt ärende
            </button>
            <button
              onClick={() => setOpenCreateClient(true)}
              className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition-colors hover:bg-slate-50"
            >
              <UserPlus className="h-4 w-4" />
              Ny klient
            </button>
          </div>
        </div>

        {/* --- Metric cards --- */}
        {isLoading ? (
          <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="flex items-center gap-4 rounded-xl border border-slate-100 bg-white p-4 shadow-sm"
              >
                <Skeleton className="h-9 w-9 rounded-lg" />
                <div>
                  <Skeleton className="h-7 w-12" />
                  <Skeleton className="mt-1 h-4 w-24" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
            <MetricCard
              icon={Briefcase}
              value={activeCases.length}
              label="Aktiva ärenden"
              accent="bg-sky-50 border-sky-100"
              iconColor="text-sky-500"
            />
            <MetricCard
              icon={Clock}
              value={awaitingReview.length}
              label="Väntar granskning"
              accent="bg-amber-50 border-amber-100"
              iconColor="text-amber-500"
            />
            <MetricCard
              icon={CalendarDays}
              value={meetingsThisWeek.length}
              label="Möten denna vecka"
              accent="bg-violet-50 border-violet-100"
              iconColor="text-violet-500"
            />
            <MetricCard
              icon={CheckCircle}
              value={completedThisMonth.length}
              label="Avslutade denna månad"
              accent="bg-emerald-50 border-emerald-100"
              iconColor="text-emerald-500"
            />
          </div>
        )}

        {/* --- Two-column layout --- */}
        <div className="grid gap-6 lg:grid-cols-5">
          {/* Left column (3/5) */}
          <div className="space-y-6 lg:col-span-3">
            {/* Cases needing attention */}
            <section className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
              <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
                <h2 className="text-sm font-semibold text-slate-900">
                  Kräver åtgärd
                </h2>
                <Link
                  href="/cases"
                  className="flex items-center gap-1 text-sm text-sky-500 hover:text-sky-600"
                >
                  Visa alla ärenden
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>

              {isLoading ? (
                <div className="divide-y divide-slate-100">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="flex items-center gap-4 px-5 py-4">
                      <Skeleton className="h-9 w-9 rounded-full" />
                      <div className="flex-1">
                        <Skeleton className="h-4 w-3/4" />
                        <Skeleton className="mt-1.5 h-3 w-1/2" />
                      </div>
                      <Skeleton className="h-5 w-20 rounded-full" />
                    </div>
                  ))}
                </div>
              ) : needsAttention.length === 0 ? (
                <div className="flex flex-col items-center py-10">
                  <CircleCheck className="mb-2 h-10 w-10 text-emerald-300" />
                  <p className="text-sm font-medium text-slate-600">
                    Alla ärenden är uppdaterade
                  </p>
                  <p className="mt-0.5 text-sm text-slate-400">
                    Inga ärenden kräver din uppmärksamhet just nu.
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {needsAttention.map((c) => {
                    const clientName = clientMap.get(c.client_id)
                    return (
                      <Link
                        key={c.id}
                        href={`/cases/${c.id}`}
                        className="group flex items-center gap-4 px-5 py-3.5 transition-colors hover:bg-slate-50"
                      >
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-600">
                          {clientName
                            ? clientName
                                .split(" ")
                                .map((n) => n[0])
                                .join("")
                            : "?"}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-medium text-slate-900 group-hover:text-sky-600">
                            {c.title}
                          </p>
                          <p className="text-sm text-slate-400">
                            {clientName ?? "Okänd klient"} &middot;{" "}
                            {timeAgo(c.updated_at)}
                          </p>
                        </div>
                        <span
                          className={cn(
                            "shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium",
                            statusStyles[c.status] ?? ""
                          )}
                        >
                          {statusLabels[c.status] ?? c.status}
                        </span>
                      </Link>
                    )
                  })}
                </div>
              )}
            </section>

            {/* Recent activity */}
            <section className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
              <div className="border-b border-slate-100 px-5 py-4">
                <h2 className="text-sm font-semibold text-slate-900">
                  Senaste aktivitet
                </h2>
              </div>

              {auditLoading ? (
                <div className="divide-y divide-slate-100">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} className="flex items-center gap-3 px-5 py-3.5">
                      <Skeleton className="h-7 w-7 rounded-full" />
                      <div className="flex-1">
                        <Skeleton className="h-4 w-4/5" />
                        <Skeleton className="mt-1 h-3 w-1/3" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : !recentAudit || recentAudit.length === 0 ? (
                <div className="flex flex-col items-center py-10">
                  <Clock className="mb-2 h-10 w-10 text-slate-300" />
                  <p className="text-sm text-slate-400">
                    Ingen aktivitet ännu.
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {recentAudit.slice(0, 8).map((entry) => {
                    const caseData = allCases.find(
                      (c) => c.id === entry.case_id
                    )
                    const isAI = entry.actor_type === "system"

                    return (
                      <Link
                        key={entry.id}
                        href={`/cases/${entry.case_id}`}
                        className="group flex items-center gap-3 px-5 py-3 transition-colors hover:bg-slate-50"
                      >
                        <div
                          className={cn(
                            "flex h-7 w-7 shrink-0 items-center justify-center rounded-full",
                            isAI
                              ? "bg-violet-100 text-violet-500"
                              : "bg-sky-100 text-sky-500"
                          )}
                        >
                          {isAI ? (
                            <Bot className="h-3.5 w-3.5" />
                          ) : (
                            <User className="h-3.5 w-3.5" />
                          )}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm text-slate-700">
                            <span className="font-medium">
                              {auditActionLabels[entry.action] ??
                                entry.action}
                            </span>
                            {caseData && (
                              <span className="text-slate-400">
                                {" "}
                                &middot; {caseData.title}
                              </span>
                            )}
                          </p>
                        </div>
                        <span className="shrink-0 text-xs text-slate-400">
                          {timeAgo(entry.timestamp)}
                        </span>
                      </Link>
                    )
                  })}
                </div>
              )}
            </section>
          </div>

          {/* Right column (2/5) */}
          <div className="space-y-6 lg:col-span-2">
            {/* Upcoming meetings */}
            <section className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
              <div className="border-b border-slate-100 px-5 py-4">
                <h2 className="text-sm font-semibold text-slate-900">
                  Kommande möten
                </h2>
              </div>

              {isLoading ? (
                <div className="divide-y divide-slate-100">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="flex items-center gap-3 px-5 py-3.5">
                      <Skeleton className="h-9 w-12 rounded-lg" />
                      <div className="flex-1">
                        <Skeleton className="h-4 w-3/4" />
                        <Skeleton className="mt-1 h-3 w-1/2" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : upcomingMeetings.length === 0 ? (
                <div className="flex flex-col items-center py-10">
                  <Calendar className="mb-2 h-10 w-10 text-slate-300" />
                  <p className="text-sm text-slate-400">
                    Inga planerade möten
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {upcomingMeetings.map((c) => {
                    const clientName = clientMap.get(c.client_id)
                    const hasBrief =
                      c.status === "in_preparation" ||
                      c.status === "ready_for_review" ||
                      c.status === "in_review" ||
                      c.status === "approved" ||
                      c.status === "completed"

                    return (
                      <Link
                        key={c.id}
                        href={`/cases/${c.id}`}
                        className="group flex items-center gap-3 px-5 py-3.5 transition-colors hover:bg-slate-50"
                      >
                        <div className="flex h-10 w-12 shrink-0 flex-col items-center justify-center rounded-lg bg-slate-100 text-center">
                          <span className="text-sm font-bold text-slate-700">
                            {new Date(c.meeting_date!).getDate()}
                          </span>
                          <span className="text-xs text-slate-400">
                            {formatSwedishShortDate(c.meeting_date!).split(" ")[1]}
                          </span>
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-medium text-slate-900 group-hover:text-sky-600">
                            {clientName ?? "Okänd klient"}
                          </p>
                          <p className="truncate text-sm text-slate-400">
                            {c.title}
                          </p>
                        </div>
                        {hasBrief ? (
                          <span className="flex shrink-0 items-center gap-1 text-xs font-medium text-emerald-600">
                            <CircleCheck className="h-3.5 w-3.5" />
                            Förberett
                          </span>
                        ) : (
                          <span className="flex shrink-0 items-center gap-1 text-xs font-medium text-amber-600">
                            <AlertCircle className="h-3.5 w-3.5" />
                            Ej förberett
                          </span>
                        )}
                      </Link>
                    )
                  })}
                </div>
              )}
            </section>

            {/* Monthly stats */}
            <section className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
              <div className="border-b border-slate-100 px-5 py-4">
                <h2 className="text-sm font-semibold text-slate-900">
                  Din månad
                </h2>
              </div>

              {auditLoading ? (
                <div className="space-y-3 px-5 py-4">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="flex items-center justify-between">
                      <Skeleton className="h-4 w-40" />
                      <Skeleton className="h-5 w-6" />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  <div className="flex items-center justify-between px-5 py-3.5">
                    <div className="flex items-center gap-3">
                      <Sparkles className="h-4 w-4 text-violet-400" />
                      <span className="text-sm text-slate-600">
                        Rekommendationer genererade
                      </span>
                    </div>
                    <span className="text-sm font-semibold text-slate-900">
                      {monthlyStats.recommendations}
                    </span>
                  </div>
                  <div className="flex items-center justify-between px-5 py-3.5">
                    <div className="flex items-center gap-3">
                      <FileText className="h-4 w-4 text-sky-400" />
                      <span className="text-sm text-slate-600">
                        Dokument skapade
                      </span>
                    </div>
                    <span className="text-sm font-semibold text-slate-900">
                      {monthlyStats.documents}
                    </span>
                  </div>
                  <div className="flex items-center justify-between px-5 py-3.5">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="h-4 w-4 text-emerald-400" />
                      <span className="text-sm text-slate-600">
                        Ärenden avslutade
                      </span>
                    </div>
                    <span className="text-sm font-semibold text-slate-900">
                      {monthlyStats.completed}
                    </span>
                  </div>
                </div>
              )}
            </section>
          </div>
        </div>
      </main>
    </>
  )
}
