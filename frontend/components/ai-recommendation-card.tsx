"use client"

import { useState } from "react"
import Link from "next/link"
import {
  Sparkles,
  Loader2,
  RefreshCw,
  Download,
  FileText,
  AlertCircle,
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ShieldCheck,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Textarea } from "@/components/ui/textarea"
import { sourceTypeStyles } from "@/lib/labels"
import type { RecommendationResponse, EvidenceResponse, DocumentResponse } from "@/lib/hooks"

const GENERATION_STEPS = [
  "Retrieving applicable regulations",
  "Scoring suitability against client profile",
  "Drafting recommendation rationale",
]

interface AIRecommendationCardProps {
  recommendation: RecommendationResponse | undefined
  evidence: EvidenceResponse[] | undefined
  isPending: boolean
  onGenerate: () => void
  onGenerateDoc: (format: string) => void
  onDownload: () => void
  generatedDoc: DocumentResponse | null
  generateDocPending: boolean
  additionalContext: string
  onAdditionalContextChange: (value: string) => void
}

function scoreColor(score: number) {
  if (score >= 8) return "text-emerald-600"
  if (score >= 6) return "text-amber-600"
  return "text-red-600"
}

function scoreBarBg(score: number) {
  if (score >= 8) return "bg-emerald-500"
  if (score >= 6) return "bg-amber-500"
  return "bg-red-500"
}

function isUuid(str: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str)
}

const verificationConfig = {
  verified: {
    icon: CheckCircle2,
    color: "text-emerald-500",
    bg: "bg-emerald-50",
    border: "border-emerald-200",
    label: "Verified",
  },
  partially_verified: {
    icon: AlertTriangle,
    color: "text-amber-500",
    bg: "bg-amber-50",
    border: "border-amber-200",
    label: "Partially verified",
  },
  unverified: {
    icon: XCircle,
    color: "text-red-500",
    bg: "bg-red-50",
    border: "border-red-200",
    label: "Unverified",
  },
} as const

function EvidenceCard({ evidence: e }: { evidence: EvidenceResponse }) {
  const [showTooltip, setShowTooltip] = useState(false)
  const knowledgeId = e.knowledge_item_id || (isUuid(e.source_reference) ? e.source_reference : null)
  const hasKnowledgeLink = !!knowledgeId
  const isNativeCitation = !!e.cited_text
  const status = e.verification_status ?? "verified"
  const vConfig = verificationConfig[status] ?? verificationConfig.verified
  const VerifyIcon = vConfig.icon

  const card = (
    <div
      className={cn(
        "rounded-lg border p-3 transition-colors",
        vConfig.border,
        hasKnowledgeLink && "cursor-pointer hover:border-sky-300 hover:bg-sky-50/30",
      )}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <VerifyIcon className={cn("h-3.5 w-3.5", vConfig.color)} />
          <p className="text-xs font-semibold text-slate-700">{e.source_reference}</p>
          {hasKnowledgeLink && <ExternalLink className="h-3 w-3 text-sky-400" />}
        </div>
        <div className="flex items-center gap-1.5">
          <span className={cn("rounded-full px-1.5 py-0.5 text-[10px]", vConfig.bg, vConfig.color)}>
            {vConfig.label}
          </span>
          <span className={cn("rounded-full px-2 py-0.5 text-[10px]", sourceTypeStyles[e.source_type] ?? "bg-slate-100 text-slate-500")}>
            {e.source_type.replace(/_/g, " ")}
          </span>
        </div>
      </div>

      {/* Native citation: show cited_text as blockquote */}
      {isNativeCitation ? (
        <blockquote className="mt-2 border-l-2 border-emerald-300 pl-2.5 text-xs italic text-slate-600">
          {e.cited_text}
        </blockquote>
      ) : (
        <p className="mt-1 text-xs text-slate-500">{e.content_snippet}</p>
      )}

      {/* Relevance explanation for native citations */}
      {isNativeCitation && e.relevance_explanation && (
        <p className="mt-1 text-[11px] text-slate-400">{e.relevance_explanation.slice(0, 200)}</p>
      )}

      {/* Tooltip */}
      {showTooltip && hasKnowledgeLink && (
        <div className="mt-2 rounded border border-sky-200 bg-sky-50 px-2.5 py-1.5">
          <p className="text-[10px] font-medium text-sky-700">
            View in Knowledge Base
          </p>
          <p className="text-[10px] text-sky-600">
            {(e.cited_text || e.content_snippet).slice(0, 120)}...
          </p>
        </div>
      )}
    </div>
  )

  if (hasKnowledgeLink) {
    return (
      <Link href={`/knowledge?highlight=${knowledgeId}`}>
        {card}
      </Link>
    )
  }

  return card
}

export function AIRecommendationCard({
  recommendation,
  evidence,
  isPending,
  onGenerate,
  onGenerateDoc,
  onDownload,
  generatedDoc,
  generateDocPending,
  additionalContext,
  onAdditionalContextChange,
}: AIRecommendationCardProps) {
  const score = recommendation?.suitability_score ? parseFloat(recommendation.suitability_score) : null
  const scorePercent = score !== null ? score * 10 : 0

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
      <div className="flex items-center gap-2.5 border-b border-slate-100 px-5 py-4">
        <Sparkles className="h-4 w-4 text-sky-500" />
        <h2 className="text-sm font-semibold text-slate-800">AI Recommendation</h2>
        {recommendation && (
          <span className="ml-auto rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-500">
            v{recommendation.version}
          </span>
        )}
      </div>

      {/* Empty state */}
      {!recommendation && !isPending && (
        <div className="px-5 py-10">
          <div className="flex flex-col items-center justify-center">
            <Sparkles className="mb-3 h-10 w-10 text-slate-200" />
            <p className="mb-1 text-sm font-medium text-slate-600">No recommendation generated</p>
            <p className="mb-5 text-xs text-slate-400">Generate a suitability-assessed AI recommendation.</p>
          </div>
          <Textarea
            placeholder="Optional: Add context or specific questions for the AI..."
            value={additionalContext}
            onChange={(e) => onAdditionalContextChange(e.target.value)}
            className="mt-2"
            rows={3}
          />
          <button
            onClick={onGenerate}
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-sky-500 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-sky-600"
          >
            <Sparkles className="h-4 w-4" />
            Generate Recommendation
          </button>
        </div>
      )}

      {/* Generating state */}
      {isPending && (
        <div className="flex flex-col items-center justify-center py-10">
          <Loader2 className="mb-4 h-7 w-7 animate-spin text-sky-500" />
          <div className="space-y-2">
            {GENERATION_STEPS.map((s, i) => (
              <div
                key={s}
                className={cn(
                  "flex items-center gap-2 text-sm transition-colors",
                  i === 0 ? "text-slate-700" : "text-slate-300"
                )}
              >
                <span
                  className={cn(
                    "h-1.5 w-1.5 rounded-full",
                    i === 0 ? "animate-pulse bg-sky-400" : "bg-slate-200"
                  )}
                />
                {s}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generated state */}
      {recommendation && !isPending && (
        <div className="space-y-6 px-5 py-5">
          {/* Suitability score */}
          {score !== null && (
            <div>
              <div className="mb-2 flex items-center justify-between">
                <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">Suitability Score</p>
                <span className={cn("text-sm font-bold", scoreColor(score))}>{recommendation.suitability_score} / 10</span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                <div className={cn("h-full rounded-full transition-all", scoreBarBg(score))} style={{ width: `${scorePercent}%` }} />
              </div>
              <p className="mt-1 text-xs text-slate-400">
                {score >= 8 ? "High suitability — recommendation is well-aligned with client profile." : score >= 6 ? "Moderate suitability — review assumptions carefully." : "Low suitability — significant concerns identified."}
              </p>
            </div>
          )}

          {/* Summary */}
          <section>
            <p className="mb-2 text-[10px] font-medium uppercase tracking-wider text-slate-400">Recommendation Summary</p>
            <p className="text-sm leading-relaxed text-slate-600">{recommendation.summary}</p>
          </section>

          {/* Reasoning chain */}
          {recommendation.reasoning_chain?.length > 0 && (
            <section>
              <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Reasoning Chain</p>
              <div className="relative space-y-3 pl-4">
                <div className="absolute left-[7px] top-0 h-full w-px bg-slate-100" />
                {recommendation.reasoning_chain.map((step, i) => (
                  <div key={step.step} className="flex items-start gap-3">
                    <div className="relative z-10 flex h-3.5 w-3.5 shrink-0 items-center justify-center rounded-full bg-sky-100 ring-2 ring-sky-400">
                      <div className="h-1.5 w-1.5 rounded-full bg-sky-500" />
                    </div>
                    <div>
                      <p className="text-xs leading-relaxed text-slate-600">{step.description}</p>
                      {step.conclusion && (
                        <p className="mt-0.5 text-xs text-slate-400">{step.conclusion}</p>
                      )}
                      {step.evidence_ids?.length > 0 && (
                        <div className="mt-1 flex flex-wrap gap-1">
                          {step.evidence_ids.map((eid) => {
                            const linked = isUuid(eid)
                            const badge = (
                              <span
                                key={eid}
                                className={cn(
                                  "rounded-full px-2 py-0.5 text-[10px]",
                                  linked
                                    ? "bg-sky-50 text-sky-600 hover:bg-sky-100 cursor-pointer"
                                    : "bg-slate-100 text-slate-500",
                                )}
                              >
                                {eid.slice(0, 8)}...
                              </span>
                            )
                            return linked ? (
                              <Link key={eid} href={`/knowledge?highlight=${eid}`}>
                                {badge}
                              </Link>
                            ) : badge
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Assumptions */}
          {recommendation.assumptions?.length > 0 && (
            <section>
              <p className="mb-2 text-[10px] font-medium uppercase tracking-wider text-slate-400">Assumptions</p>
              <ul className="space-y-1">
                {recommendation.assumptions.map((a, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-slate-500">
                    <AlertCircle className="mt-0.5 h-3 w-3 shrink-0 text-amber-400" />
                    <div>
                      <span>{a.assumption}</span>
                      {a.impact_if_wrong && (
                        <p className="mt-0.5 text-[11px] text-amber-600">{a.impact_if_wrong}</p>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Scenarios */}
          {recommendation.scenarios && recommendation.scenarios.length > 0 && (
            <section>
              <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Projected Scenarios</p>
              <div className="grid grid-cols-2 gap-3">
                {recommendation.scenarios.map((s, i) => (
                  <div
                    key={s.name}
                    className={cn(
                      "rounded-lg border p-3",
                      i === recommendation.scenarios!.length - 1
                        ? "border-emerald-200 bg-emerald-50"
                        : "border-slate-200"
                    )}
                  >
                    <p className={cn("text-xs font-medium", i === recommendation.scenarios!.length - 1 ? "text-emerald-700" : "text-slate-600")}>
                      {s.name}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">{s.description}</p>
                    {Object.keys(s.projected_outcome).length > 0 && (
                      <div className="mt-2 space-y-1">
                        {Object.entries(s.projected_outcome).map(([k, v]) => (
                          <div key={k} className="flex items-center justify-between text-xs">
                            <span className="text-slate-400">{k.replace(/_/g, " ")}</span>
                            <span className="font-medium text-slate-700">{String(v)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Evidence cards */}
          {evidence && evidence.length > 0 && (() => {
            const verified = evidence.filter((e) => e.verification_status === "verified").length
            const partial = evidence.filter((e) => e.verification_status === "partially_verified").length
            const unverified = evidence.filter((e) => e.verification_status === "unverified").length

            return (
              <section>
                <div className="mb-3 flex items-center justify-between">
                  <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">Supporting Evidence</p>
                  <div className="flex items-center gap-2">
                    {verified > 0 && (
                      <span className="flex items-center gap-0.5 text-[10px] text-emerald-600">
                        <ShieldCheck className="h-3 w-3" />
                        {verified}
                      </span>
                    )}
                    {partial > 0 && (
                      <span className="flex items-center gap-0.5 text-[10px] text-amber-500">
                        <AlertTriangle className="h-3 w-3" />
                        {partial}
                      </span>
                    )}
                    {unverified > 0 && (
                      <span className="flex items-center gap-0.5 text-[10px] text-red-500">
                        <XCircle className="h-3 w-3" />
                        {unverified}
                      </span>
                    )}
                  </div>
                </div>
                <div className="space-y-2">
                  {evidence.map((e) => (
                    <EvidenceCard key={e.id} evidence={e} />
                  ))}
                </div>
              </section>
            )
          })()}

          {/* Action buttons */}
          <div className="flex flex-col gap-2">
            <button
              onClick={() => onGenerateDoc("docx")}
              disabled={generateDocPending}
              className="flex items-center justify-center gap-2 rounded-lg bg-sky-500 py-2.5 text-sm font-medium text-white transition-colors hover:bg-sky-600 disabled:opacity-50"
            >
              {generateDocPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <FileText className="h-4 w-4" />
              )}
              Generate Document
            </button>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={onDownload}
                disabled={!generatedDoc}
                className="flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white py-2 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50 disabled:opacity-50"
              >
                <Download className="h-3.5 w-3.5" />
                Download {generatedDoc?.file_format?.toUpperCase() ?? "DOCX"}
              </button>
              <button
                onClick={onGenerate}
                className="flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white py-2 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                New Version
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
