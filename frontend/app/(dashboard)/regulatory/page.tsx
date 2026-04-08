"use client"

import Link from "next/link"
import { useMemo, useState } from "react"
import {
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Play,
  Search,
  Shield,
} from "lucide-react"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { TopBar } from "@/components/top-bar"
import {
  useRegulatoryChanges,
  useScanRegulatoryChange,
  type RegulatoryChangeResponse,
} from "@/lib/hooks"
import {
  caseTypeLabels,
  agreementLabels,
  regulatorySeverityLabels,
  regulatorySeverityStyles,
} from "@/lib/labels"

const severityOptions = [
  { value: "all", label: "Alla allvarlighetsgrader" },
  { value: "critical", label: "Kritisk" },
  { value: "high", label: "Hög" },
  { value: "medium", label: "Medel" },
  { value: "low", label: "Låg" },
]

export default function RegulatoryPage() {
  const [search, setSearch] = useState("")
  const [severity, setSeverity] = useState("all")
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  const filters: Record<string, string> = {}
  if (severity !== "all") filters.severity = severity

  const { data: changes, isLoading } = useRegulatoryChanges(filters)
  const scan = useScanRegulatoryChange()

  const filtered = useMemo(() => {
    if (!changes) return []
    if (!search.trim()) return changes
    const q = search.toLowerCase()
    return changes.filter(
      (c) =>
        c.title.toLowerCase().includes(q) ||
        c.description.toLowerCase().includes(q) ||
        c.source.toLowerCase().includes(q),
    )
  }, [changes, search])

  const toggleExpanded = (id: string) => {
    const next = new Set(expanded)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setExpanded(next)
  }

  const handleScan = (id: string) => {
    scan.mutate(id, {
      onSuccess: (data) => {
        if (data.new_impacts > 0) {
          toast.success(
            `Skanning klar: ${data.new_impacts} nya påverkade ärenden hittades`,
          )
        } else if (data.total_matched_cases > 0) {
          toast.info(
            `Skanning klar: ${data.total_matched_cases} matchande ärenden (alla redan registrerade)`,
          )
        } else {
          toast.info("Skanning klar: inga aktiva ärenden matchade")
        }
      },
      onError: (err) => toast.error(err.message),
    })
  }

  return (
    <>
      <TopBar breadcrumbs={[{ label: "Regulatorisk pulse" }]} />
      <main className="flex-1 bg-slate-50">
        <div className="mx-auto max-w-5xl px-6 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="flex items-center gap-2 text-xl font-semibold text-slate-900">
              <Shield className="h-5 w-5 text-sky-500" />
              Regulatorisk pulse
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Bevaka regulatoriska ändringar och deras påverkan på aktiva
              ärenden
            </p>
          </div>

          {/* Search */}
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Sök i regulatoriska ändringar..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="border-slate-200/60 bg-white pl-10"
              />
            </div>
          </div>

          {/* Filters */}
          <div className="mb-6">
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-sky-300 focus:ring-1 focus:ring-sky-300"
            >
              {severityOptions.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>

          {/* Loading skeletons */}
          {isLoading && (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
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

          {/* Changes list */}
          {!isLoading && filtered.length > 0 && (
            <div className="space-y-3">
              {filtered.map((change) => (
                <RegulatoryChangeCard
                  key={change.id}
                  change={change}
                  isExpanded={expanded.has(change.id)}
                  onToggle={() => toggleExpanded(change.id)}
                  onScan={() => handleScan(change.id)}
                  isScanning={scan.isPending && scan.variables === change.id}
                />
              ))}
            </div>
          )}

          {/* Empty state */}
          {!isLoading && filtered.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12">
              <Shield className="mb-3 h-12 w-12 text-slate-300" />
              <p className="mb-1 text-base font-medium text-slate-600">
                Inga regulatoriska ändringar hittades
              </p>
              <p className="text-sm text-slate-400">
                Nya FI-föreskrifter och marknadshändelser syns här
              </p>
            </div>
          )}
        </div>
      </main>
    </>
  )
}

function RegulatoryChangeCard({
  change,
  isExpanded,
  onToggle,
  onScan,
  isScanning,
}: {
  change: RegulatoryChangeResponse
  isExpanded: boolean
  onToggle: () => void
  onScan: () => void
  isScanning: boolean
}) {
  const publishedDate = new Date(change.published_at).toLocaleDateString("sv-SE")
  const openCount = change.open_impact_count ?? 0
  const totalCount = change.impact_count ?? 0

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm transition-all hover:border-l-4 hover:border-l-sky-400">
      <div className="flex items-start justify-between gap-4">
        <button
          onClick={onToggle}
          className="flex min-w-0 flex-1 items-start gap-2 text-left"
        >
          {isExpanded ? (
            <ChevronDown className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
          ) : (
            <ChevronRight className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
          )}
          <div className="min-w-0 flex-1">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span
                className={cn(
                  "rounded-full px-2 py-0.5 text-xs font-medium",
                  regulatorySeverityStyles[change.severity],
                )}
              >
                {regulatorySeverityLabels[change.severity]}
              </span>
              <h3 className="text-sm font-semibold text-slate-900">
                {change.title}
              </h3>
            </div>
            <p
              className={cn(
                "text-sm leading-relaxed text-slate-600",
                !isExpanded && "line-clamp-2",
              )}
            >
              {change.description}
            </p>
          </div>
        </button>

        <div className="flex shrink-0 flex-col items-end gap-2">
          {totalCount > 0 && (
            <div className="flex items-center gap-1 text-xs">
              <span className="rounded-full bg-red-50 px-2 py-0.5 font-semibold text-red-700">
                {openCount} öppna
              </span>
              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-slate-500">
                {totalCount} totalt
              </span>
            </div>
          )}
          <button
            onClick={onScan}
            disabled={isScanning}
            className="flex items-center gap-1 rounded-lg border border-sky-200 bg-sky-50 px-2.5 py-1 text-xs font-medium text-sky-700 transition-colors hover:bg-sky-100 disabled:opacity-50"
          >
            <Play className="h-3 w-3" />
            {isScanning ? "Skannar..." : "Skanna ärenden"}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="mt-4 space-y-3 pl-6">
          {change.affected_case_types.length > 0 && (
            <div className="flex flex-wrap items-center gap-1 text-xs text-slate-500">
              <span>Ärendetyper:</span>
              {change.affected_case_types.map((t) => (
                <span
                  key={t}
                  className="rounded bg-slate-100 px-1.5 py-0.5 text-slate-600"
                >
                  {caseTypeLabels[t] ?? t}
                </span>
              ))}
            </div>
          )}
          {change.affected_agreements.length > 0 && (
            <div className="flex flex-wrap items-center gap-1 text-xs text-slate-500">
              <span>Avtal:</span>
              {change.affected_agreements.map((a) => (
                <span
                  key={a}
                  className="rounded bg-slate-100 px-1.5 py-0.5 text-slate-600"
                >
                  {agreementLabels[a] ?? a}
                </span>
              ))}
            </div>
          )}
          {change.affected_tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {change.affected_tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-500"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
          {change.knowledge_item_id && change.knowledge_item_title && (
            <p className="text-xs text-slate-500">
              Kunskapsdokument:{" "}
              <Link
                href={`/knowledge?item=${change.knowledge_item_id}`}
                className="font-medium text-sky-600 hover:underline"
              >
                {change.knowledge_item_title}
              </Link>
            </p>
          )}
          {change.source_url && (
            <a
              href={change.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs font-medium text-sky-600 hover:underline"
            >
              Öppna källa
              <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>
      )}

      <div className="mt-3 border-t border-slate-100 pt-2 text-xs text-slate-400">
        {change.source} · {publishedDate}
      </div>
    </div>
  )
}
