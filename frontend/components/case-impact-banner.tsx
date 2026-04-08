"use client"

import { useState } from "react"
import {
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Loader2,
  Shield,
  X,
} from "lucide-react"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import {
  useCaseImpacts,
  useResolveCaseImpact,
  useAcknowledgeCaseImpact,
  useMarkImpactNotApplicable,
  type CaseImpactResponse,
} from "@/lib/hooks"
import {
  caseImpactStatusLabels,
  caseImpactStatusStyles,
  regulatorySeverityLabels,
  regulatorySeverityStyles,
} from "@/lib/labels"

interface CaseImpactBannerProps {
  caseId: string
}

export function CaseImpactBanner({ caseId }: CaseImpactBannerProps) {
  const { data: impacts, isLoading } = useCaseImpacts(caseId)
  const resolve = useResolveCaseImpact()
  const acknowledge = useAcknowledgeCaseImpact()
  const notApplicable = useMarkImpactNotApplicable()
  const [expanded, setExpanded] = useState(true)

  if (isLoading || !impacts || impacts.length === 0) {
    return null
  }

  const openImpacts = impacts.filter(
    (i) => i.status === "open" || i.status === "acknowledged",
  )
  if (openImpacts.length === 0) {
    return null
  }

  // Find the highest severity
  const severityOrder: Record<string, number> = {
    critical: 4,
    high: 3,
    medium: 2,
    low: 1,
  }
  const topSeverity = openImpacts.reduce((acc, i) => {
    const sev = i.regulatory_change_severity ?? "low"
    return severityOrder[sev] > severityOrder[acc] ? sev : acc
  }, "low" as string)

  const bannerStyles: Record<string, string> = {
    critical: "border-red-300 bg-red-50",
    high: "border-orange-300 bg-orange-50",
    medium: "border-amber-300 bg-amber-50",
    low: "border-slate-300 bg-slate-50",
  }
  const iconStyles: Record<string, string> = {
    critical: "text-red-600",
    high: "text-orange-600",
    medium: "text-amber-600",
    low: "text-slate-600",
  }

  const handleResolve = (impactId: string) => {
    const note = window.prompt("Kommentar (valfritt):") ?? undefined
    resolve.mutate(
      { impactId, resolutionNote: note },
      {
        onSuccess: () => toast.success("Påverkan åtgärdad"),
        onError: (err) => toast.error(err.message),
      },
    )
  }

  const handleAcknowledge = (impactId: string) => {
    acknowledge.mutate(impactId, {
      onSuccess: () => toast.success("Påverkan bekräftad"),
      onError: (err) => toast.error(err.message),
    })
  }

  const handleNotApplicable = (impactId: string) => {
    const note = window.prompt("Motivering (valfritt):") ?? undefined
    notApplicable.mutate(
      { impactId, resolutionNote: note },
      {
        onSuccess: () => toast.success("Markerad som ej tillämplig"),
        onError: (err) => toast.error(err.message),
      },
    )
  }

  return (
    <div
      className={cn(
        "rounded-xl border-2 shadow-sm",
        bannerStyles[topSeverity],
      )}
    >
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex w-full items-center justify-between gap-3 px-5 py-3 text-left"
      >
        <div className="flex items-center gap-2">
          <AlertTriangle className={cn("h-5 w-5", iconStyles[topSeverity])} />
          <div>
            <p className="text-sm font-semibold text-slate-900">
              {openImpacts.length} regulatorisk{" "}
              {openImpacts.length === 1 ? "ändring påverkar" : "ändringar påverkar"}{" "}
              detta ärende
            </p>
            <p className="text-xs text-slate-600">
              Granska och åtgärda innan ärendet slutförs
            </p>
          </div>
        </div>
        {expanded ? (
          <ChevronUp className="h-4 w-4 text-slate-500" />
        ) : (
          <ChevronDown className="h-4 w-4 text-slate-500" />
        )}
      </button>

      {expanded && (
        <div className="space-y-2 border-t border-slate-200/50 px-5 py-3">
          {openImpacts.map((impact) => (
            <ImpactCard
              key={impact.id}
              impact={impact}
              onResolve={() => handleResolve(impact.id)}
              onAcknowledge={() => handleAcknowledge(impact.id)}
              onNotApplicable={() => handleNotApplicable(impact.id)}
              isResolving={
                resolve.isPending && resolve.variables?.impactId === impact.id
              }
              isAcknowledging={
                acknowledge.isPending && acknowledge.variables === impact.id
              }
              isMarkingNa={
                notApplicable.isPending &&
                notApplicable.variables?.impactId === impact.id
              }
            />
          ))}
        </div>
      )}
    </div>
  )
}

function ImpactCard({
  impact,
  onResolve,
  onAcknowledge,
  onNotApplicable,
  isResolving,
  isAcknowledging,
  isMarkingNa,
}: {
  impact: CaseImpactResponse
  onResolve: () => void
  onAcknowledge: () => void
  onNotApplicable: () => void
  isResolving: boolean
  isAcknowledging: boolean
  isMarkingNa: boolean
}) {
  const sev = impact.regulatory_change_severity ?? "low"
  return (
    <div className="rounded-lg border border-slate-200 bg-white/70 p-3">
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <span
          className={cn(
            "rounded-full px-2 py-0.5 text-xs font-medium",
            regulatorySeverityStyles[sev],
          )}
        >
          {regulatorySeverityLabels[sev]}
        </span>
        <span
          className={cn(
            "rounded-full px-2 py-0.5 text-xs font-medium",
            caseImpactStatusStyles[impact.status],
          )}
        >
          {caseImpactStatusLabels[impact.status]}
        </span>
        <p className="text-sm font-semibold text-slate-900">
          {impact.regulatory_change_title}
        </p>
      </div>
      <p className="mb-3 text-xs leading-relaxed text-slate-600">
        {impact.match_reason}
      </p>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={onResolve}
          disabled={isResolving}
          className="inline-flex items-center gap-1 rounded-md border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 transition-colors hover:bg-emerald-100 disabled:opacity-50"
        >
          {isResolving ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <CheckCircle2 className="h-3 w-3" />
          )}
          Åtgärdad
        </button>
        {impact.status === "open" && (
          <button
            onClick={onAcknowledge}
            disabled={isAcknowledging}
            className="inline-flex items-center gap-1 rounded-md border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700 transition-colors hover:bg-amber-100 disabled:opacity-50"
          >
            {isAcknowledging ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <Shield className="h-3 w-3" />
            )}
            Bekräfta
          </button>
        )}
        <button
          onClick={onNotApplicable}
          disabled={isMarkingNa}
          className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50 disabled:opacity-50"
        >
          {isMarkingNa ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <X className="h-3 w-3" />
          )}
          Ej tillämplig
        </button>
      </div>
    </div>
  )
}
