"use client"

import Link from "next/link"
import { useMemo, useState } from "react"
import {
  ChevronDown,
  ChevronUp,
  Lightbulb,
  Plus,
  Search,
  ThumbsUp,
} from "lucide-react"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { TopBar } from "@/components/top-bar"
import { FirmInsightDialog } from "@/components/firm-insight-dialog"
import {
  useFirmInsights,
  useUpvoteFirmInsight,
  type FirmInsightResponse,
} from "@/lib/hooks"
import {
  agreementLabels,
  caseTypeLabels,
  firmInsightCategoryLabels,
  firmInsightCategoryStyles,
} from "@/lib/labels"

const categoryOptions = [
  { value: "all", label: "Alla" },
  ...Object.entries(firmInsightCategoryLabels).map(([value, label]) => ({
    value,
    label,
  })),
]

const caseTypeOptions = [
  { value: "all", label: "Alla typer" },
  ...Object.entries(caseTypeLabels).map(([value, label]) => ({ value, label })),
]

const agreementOptions = [
  { value: "all", label: "Alla avtal" },
  ...Object.entries(agreementLabels).map(([value, label]) => ({
    value,
    label,
  })),
]

export default function InsightsPage() {
  const [search, setSearch] = useState("")
  const [category, setCategory] = useState("all")
  const [caseType, setCaseType] = useState("all")
  const [agreement, setAgreement] = useState("all")
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [showCreate, setShowCreate] = useState(false)

  const filters: Record<string, string> = {}
  if (category !== "all") filters.category = category
  if (caseType !== "all") filters.case_type = caseType
  if (agreement !== "all") filters.collective_agreement = agreement

  const { data: insights, isLoading } = useFirmInsights(filters)
  const upvote = useUpvoteFirmInsight()

  const filtered = useMemo(() => {
    if (!insights) return []
    if (!search.trim()) return insights
    const q = search.toLowerCase()
    return insights.filter(
      (i) =>
        i.title.toLowerCase().includes(q) ||
        i.content.toLowerCase().includes(q) ||
        i.tags.some((t) => t.toLowerCase().includes(q)),
    )
  }, [insights, search])

  const toggleExpanded = (id: string) => {
    const next = new Set(expanded)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setExpanded(next)
  }

  const handleUpvote = (id: string) => {
    upvote.mutate(id, {
      onSuccess: () => toast.success("Tack för din röst!"),
      onError: (err) => toast.error(err.message),
    })
  }

  return (
    <>
      <TopBar breadcrumbs={[{ label: "Firmans kunskapsbank" }]} />
      <main className="flex-1 bg-slate-50">
        <div className="mx-auto max-w-5xl px-6 py-8">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="flex items-center gap-2 text-xl font-semibold text-slate-900">
                <Lightbulb className="h-5 w-5 text-amber-500" />
                Firmans kunskapsbank
              </h1>
              <p className="mt-1 text-sm text-slate-500">
                Institutionell kunskap från firmans rådgivare
              </p>
            </div>
            <button
              onClick={() => setShowCreate(true)}
              className="flex items-center gap-2 rounded-lg bg-sky-500 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-sky-600"
            >
              <Plus className="h-4 w-4" />
              Ny insikt
            </button>
          </div>

          {/* Search */}
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Sök i insikter..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="border-slate-200/60 bg-white pl-10"
              />
            </div>
          </div>

          {/* Filters */}
          <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-sky-300 focus:ring-1 focus:ring-sky-300"
            >
              {categoryOptions.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
            <select
              value={caseType}
              onChange={(e) => setCaseType(e.target.value)}
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-sky-300 focus:ring-1 focus:ring-sky-300"
            >
              {caseTypeOptions.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
            <select
              value={agreement}
              onChange={(e) => setAgreement(e.target.value)}
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-sky-300 focus:ring-1 focus:ring-sky-300"
            >
              {agreementOptions.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>

          {/* Loading skeletons */}
          {isLoading && (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div
                  key={i}
                  className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm"
                >
                  <Skeleton className="h-4 w-2/3" />
                  <Skeleton className="mt-2 h-3 w-1/4" />
                  <Skeleton className="mt-3 h-12 w-full" />
                </div>
              ))}
            </div>
          )}

          {/* Insights list */}
          {!isLoading && filtered.length > 0 && (
            <div className="space-y-3">
              {filtered.map((insight) => (
                <InsightCard
                  key={insight.id}
                  insight={insight}
                  isExpanded={expanded.has(insight.id)}
                  onToggle={() => toggleExpanded(insight.id)}
                  onUpvote={() => handleUpvote(insight.id)}
                  isUpvoting={upvote.isPending}
                />
              ))}
            </div>
          )}

          {/* Empty state */}
          {!isLoading && filtered.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12">
              <Lightbulb className="mb-3 h-12 w-12 text-slate-300" />
              <p className="mb-1 text-base font-medium text-slate-600">
                Inga insikter hittades
              </p>
              <p className="text-sm text-slate-400">
                Försök justera filter eller skapa en ny insikt
              </p>
            </div>
          )}
        </div>
      </main>

      {showCreate && (
        <FirmInsightDialog
          open={showCreate}
          onOpenChange={setShowCreate}
        />
      )}
    </>
  )
}

function InsightCard({
  insight,
  isExpanded,
  onToggle,
  onUpvote,
  isUpvoting,
}: {
  insight: FirmInsightResponse
  isExpanded: boolean
  onToggle: () => void
  onUpvote: () => void
  isUpvoting: boolean
}) {
  const createdDate = new Date(insight.created_at).toLocaleDateString("sv-SE")

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm transition-all hover:border-l-4 hover:border-l-amber-400">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <span
              className={cn(
                "rounded-full px-2 py-0.5 text-xs font-medium",
                firmInsightCategoryStyles[insight.category] ??
                  "bg-slate-100 text-slate-700",
              )}
            >
              {firmInsightCategoryLabels[insight.category] ?? insight.category}
            </span>
            <h3 className="text-sm font-semibold text-slate-900">
              {insight.title}
            </h3>
          </div>

          <p
            className={cn(
              "text-sm leading-relaxed text-slate-600",
              !isExpanded && "line-clamp-3",
            )}
          >
            {insight.content}
          </p>

          {isExpanded && (
            <div className="mt-3 space-y-2">
              {insight.client_organization_name && (
                <p className="text-xs text-slate-500">
                  Klientorg:{" "}
                  <span className="font-medium text-slate-700">
                    {insight.client_organization_name}
                  </span>
                </p>
              )}
              {insight.source_case_id && insight.source_case_title && (
                <p className="text-xs text-slate-500">
                  Från ärende:{" "}
                  <Link
                    href={`/cases/${insight.source_case_id}`}
                    className="font-medium text-sky-600 hover:underline"
                  >
                    {insight.source_case_title}
                  </Link>
                </p>
              )}
              {insight.case_types.length > 0 && (
                <div className="flex flex-wrap items-center gap-1 text-xs text-slate-500">
                  <span>Ärendetyper:</span>
                  {insight.case_types.map((t) => (
                    <span
                      key={t}
                      className="rounded bg-slate-100 px-1.5 py-0.5 text-slate-600"
                    >
                      {caseTypeLabels[t] ?? t}
                    </span>
                  ))}
                </div>
              )}
              {insight.collective_agreements.length > 0 && (
                <div className="flex flex-wrap items-center gap-1 text-xs text-slate-500">
                  <span>Avtal:</span>
                  {insight.collective_agreements.map((a) => (
                    <span
                      key={a}
                      className="rounded bg-slate-100 px-1.5 py-0.5 text-slate-600"
                    >
                      {agreementLabels[a] ?? a}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {insight.tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {insight.tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-500"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}

          <button
            onClick={onToggle}
            className="mt-2 text-sm font-medium text-sky-600 hover:text-sky-700"
          >
            {isExpanded ? "Visa mindre" : "Visa mer"}
          </button>
        </div>

        <div className="flex shrink-0 flex-col items-end gap-2">
          <button
            onClick={onToggle}
            className="text-slate-400 hover:text-slate-600"
          >
            {isExpanded ? (
              <ChevronUp className="h-5 w-5" />
            ) : (
              <ChevronDown className="h-5 w-5" />
            )}
          </button>
          <button
            onClick={onUpvote}
            disabled={isUpvoting}
            className="flex items-center gap-1 rounded-lg border border-slate-200 px-2 py-1 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50 disabled:opacity-50"
          >
            <ThumbsUp className="h-3 w-3" />
            {insight.upvotes}
          </button>
        </div>
      </div>

      <div className="mt-3 border-t border-slate-100 pt-2 text-xs text-slate-400">
        {insight.creator_name ?? "Okänd"} · {createdDate}
      </div>
    </div>
  )
}
