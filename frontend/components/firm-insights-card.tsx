"use client"

import Link from "next/link"
import { useState } from "react"
import { Lightbulb, ThumbsUp, Plus, ChevronDown, ChevronRight, Loader2 } from "lucide-react"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import {
  firmInsightCategoryLabels,
  firmInsightCategoryStyles,
} from "@/lib/labels"
import {
  useRelevantInsights,
  useUpvoteFirmInsight,
  type FirmInsightResponse,
} from "@/lib/hooks"
import { FirmInsightDialog } from "@/components/firm-insight-dialog"

interface FirmInsightsCardProps {
  caseId: string
  caseType?: string
  clientCollectiveAgreement?: string | null
  clientOrganizationId?: string | null
}

export function FirmInsightsCard({
  caseId,
  caseType,
  clientCollectiveAgreement,
  clientOrganizationId,
}: FirmInsightsCardProps) {
  const { data: insights, isLoading } = useRelevantInsights(caseId)
  const upvote = useUpvoteFirmInsight()
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [showCreate, setShowCreate] = useState(false)

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

  const count = insights?.length ?? 0

  return (
    <>
      <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <div className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-amber-500" />
            <h3 className="text-sm font-semibold text-slate-700">Firmans insikter</h3>
            {count > 0 && (
              <span className="rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700">
                {count}
              </span>
            )}
          </div>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50"
          >
            <Plus className="h-3 w-3" />
            Lägg till insikt
          </button>
        </div>

        <div className="divide-y divide-slate-100">
          {isLoading && (
            <div className="px-5 py-6 text-center text-sm text-slate-400">
              Laddar insikter...
            </div>
          )}

          {!isLoading && count === 0 && (
            <div className="px-5 py-8 text-center text-sm text-slate-400">
              Inga insikter matchar detta ärende ännu
            </div>
          )}

          {!isLoading &&
            insights?.map((insight) => (
              <InsightRow
                key={insight.id}
                insight={insight}
                isExpanded={expanded.has(insight.id)}
                onToggle={() => toggleExpanded(insight.id)}
                onUpvote={() => handleUpvote(insight.id)}
                isUpvoting={upvote.isPending}
              />
            ))}
        </div>
      </div>

      {showCreate && (
        <FirmInsightDialog
          open={showCreate}
          onOpenChange={setShowCreate}
          defaultValues={{
            source_case_id: caseId,
            case_types: caseType ? [caseType] : [],
            collective_agreements: clientCollectiveAgreement
              ? [clientCollectiveAgreement]
              : [],
            client_organization_id: clientOrganizationId ?? null,
          }}
        />
      )}
    </>
  )
}

function InsightRow({
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
    <div className="px-5 py-4">
      <div className="flex items-start justify-between gap-3">
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
            <div className="mb-1.5 flex flex-wrap items-center gap-2">
              <span
                className={cn(
                  "shrink-0 rounded-full px-2 py-0.5 text-xs font-medium",
                  firmInsightCategoryStyles[insight.category] ??
                    "bg-slate-100 text-slate-700",
                )}
              >
                {firmInsightCategoryLabels[insight.category] ?? insight.category}
              </span>
              <p className="text-sm font-semibold text-slate-800">{insight.title}</p>
            </div>
            <p
              className={cn(
                "text-sm leading-relaxed text-slate-600",
                !isExpanded && "line-clamp-2",
              )}
            >
              {insight.content}
            </p>
          </div>
        </button>
      </div>

      {isExpanded && (
        <div className="mt-3 space-y-2 pl-6">
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
          {insight.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
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
        </div>
      )}

      <div className="mt-3 flex items-center justify-between pl-6">
        <div className="text-xs text-slate-400">
          {insight.creator_name ?? "Okänd"} · {createdDate}
        </div>
        <button
          onClick={onUpvote}
          disabled={isUpvoting}
          className="flex items-center gap-1 rounded-lg border border-slate-200 px-2 py-1 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50 disabled:opacity-50"
        >
          {isUpvoting ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <ThumbsUp className="h-3 w-3" />
          )}
          {insight.upvotes}
        </button>
      </div>
    </div>
  )
}
