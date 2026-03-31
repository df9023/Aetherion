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
  MessageSquare,
  Check,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Textarea } from "@/components/ui/textarea"
import { sourceTypeStyles, sourceTypeLabels } from "@/lib/labels"
import type { RecommendationResponse, EvidenceResponse, DocumentResponse, ReasoningStep } from "@/lib/hooks"

const GENERATION_STEPS = [
  "Hämtar tillämpliga regelverk",
  "Bedömer lämplighet mot klientprofil",
  "Skriver rekommendationsunderlag",
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
  onAnnotateStep?: (step: number, annotation: string) => void
  onReviewReasoning?: (comment?: string) => void
  annotationPending?: boolean
  reviewPending?: boolean
}

function scoreColor(score: number) {
  if (score >= 0.8) return "text-emerald-600"
  if (score >= 0.6) return "text-amber-600"
  return "text-red-600"
}

function scoreBarBg(score: number) {
  if (score >= 0.8) return "bg-emerald-500"
  if (score >= 0.6) return "bg-amber-500"
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
    label: "Verifierad",
  },
  partially_verified: {
    icon: AlertTriangle,
    color: "text-amber-500",
    bg: "bg-amber-50",
    border: "border-amber-200",
    label: "Delvis verifierad",
  },
  unverified: {
    icon: XCircle,
    color: "text-red-500",
    bg: "bg-red-50",
    border: "border-red-200",
    label: "Ej verifierad",
  },
} as const

const complianceStatusConfig = {
  pending: {
    label: "Väntar granskning",
    bg: "bg-amber-50",
    text: "text-amber-700",
    border: "border-amber-200",
  },
  reviewed: {
    label: "Granskad",
    bg: "bg-emerald-50",
    text: "text-emerald-700",
    border: "border-emerald-200",
  },
} as const

function ComplianceBadge({ recommendation }: { recommendation: RecommendationResponse }) {
  const meta = recommendation.reasoning_metadata
  const reviewStatus = meta?.review_status ?? "pending"
  const isGenerated = !!recommendation.reasoning_chain?.length

  if (!isGenerated) return null

  if (reviewStatus === "reviewed") {
    const cfg = complianceStatusConfig.reviewed
    return (
      <span className={cn("inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium", cfg.bg, cfg.text, cfg.border)}>
        <CheckCircle2 className="h-3 w-3" />
        {cfg.label}
      </span>
    )
  }

  const cfg = complianceStatusConfig.pending
  return (
    <span className={cn("inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium", cfg.bg, cfg.text, cfg.border)}>
      <AlertTriangle className="h-3 w-3" />
      {cfg.label}
    </span>
  )
}

function ReasoningStepItem({
  step,
  onAnnotate,
  annotationPending,
}: {
  step: ReasoningStep
  onAnnotate?: (step: number, annotation: string) => void
  annotationPending?: boolean
}) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(step.advisor_annotation ?? "")

  function handleSave() {
    if (draft.trim() && onAnnotate) {
      onAnnotate(step.step, draft.trim())
      setEditing(false)
    }
  }

  return (
    <div className="flex items-start gap-3">
      <div className="relative z-10 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-sky-100 ring-2 ring-sky-400">
        <div className="h-2 w-2 rounded-full bg-sky-500" />
      </div>
      <div className="min-w-0 flex-1">
        {step.title && (
          <p className="mb-0.5 text-xs font-semibold uppercase tracking-wider text-sky-600">{step.title}</p>
        )}
        <p className="text-sm leading-relaxed text-slate-600">{step.description}</p>

        {/* Cited texts */}
        {step.cited_texts?.length > 0 && (
          <div className="mt-2 space-y-1.5">
            {step.cited_texts.map((ct, i) => (
              <blockquote key={i} className="border-l-2 border-emerald-300 pl-3">
                <p className="text-sm italic leading-relaxed text-slate-500">&ldquo;{ct.text}&rdquo;</p>
                {ct.source_title && (
                  <p className="mt-0.5 text-xs text-slate-400">&mdash; {ct.source_title}</p>
                )}
              </blockquote>
            ))}
          </div>
        )}

        {step.conclusion && (
          <p className="mt-1 text-sm text-slate-400">{step.conclusion}</p>
        )}

        {/* Advisor annotation */}
        {step.advisor_annotation && !editing && (
          <div className="mt-2 rounded-md border border-sky-100 bg-sky-50/50 px-3 py-2">
            <div className="flex items-center gap-1.5">
              <MessageSquare className="h-3.5 w-3.5 text-sky-500" />
              <span className="text-xs font-medium text-sky-600">Rådgivarens kommentar</span>
            </div>
            <p className="mt-1 text-sm text-slate-600">{step.advisor_annotation}</p>
          </div>
        )}

        {/* Annotation editor */}
        {editing ? (
          <div className="mt-2 space-y-2">
            <Textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Skriv din kommentar..."
              rows={2}
              className="text-sm"
            />
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                disabled={annotationPending || !draft.trim()}
                className="flex items-center gap-1 rounded-md bg-sky-500 px-3 py-1.5 text-xs font-medium text-white hover:bg-sky-600 disabled:opacity-50"
              >
                {annotationPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <Check className="h-3 w-3" />}
                Spara
              </button>
              <button
                onClick={() => { setEditing(false); setDraft(step.advisor_annotation ?? "") }}
                className="rounded-md border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
              >
                Avbryt
              </button>
            </div>
          </div>
        ) : onAnnotate ? (
          <button
            onClick={() => setEditing(true)}
            className="mt-1.5 flex items-center gap-1 text-xs text-slate-400 hover:text-sky-500"
          >
            <MessageSquare className="h-3 w-3" />
            {step.advisor_annotation ? "Redigera kommentar" : "Lägg till kommentar"}
          </button>
        ) : null}
      </div>
    </div>
  )
}

function EvidenceCard({ evidence: e }: { evidence: EvidenceResponse }) {
  const [expanded, setExpanded] = useState(false)
  const knowledgeId = e.knowledge_item_id || (isUuid(e.source_reference) ? e.source_reference : null)
  const hasKnowledgeLink = !!knowledgeId
  const isNativeCitation = !!e.cited_text
  const status = e.verification_status ?? "verified"
  const vConfig = verificationConfig[status] ?? verificationConfig.verified
  const VerifyIcon = vConfig.icon

  const card = (
    <div
      className={cn(
        "rounded-lg border p-4 transition-colors",
        vConfig.border,
        hasKnowledgeLink && "cursor-pointer hover:border-sky-300 hover:bg-sky-50/30",
      )}
      onClick={() => !hasKnowledgeLink && setExpanded(!expanded)}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <VerifyIcon className={cn("h-4 w-4 shrink-0", vConfig.color)} />
          <p className="text-sm font-semibold text-slate-700">{e.source_reference}</p>
          {hasKnowledgeLink && <ExternalLink className="h-3.5 w-3.5 text-sky-400" />}
        </div>
        <div className="flex items-center gap-2">
          <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", vConfig.bg, vConfig.color)}>
            {vConfig.label}
          </span>
          <span className={cn("rounded-full px-2 py-0.5 text-xs", sourceTypeStyles[e.source_type] ?? "bg-slate-100 text-slate-500")}>
            {sourceTypeLabels[e.source_type] ?? e.source_type.replace(/_/g, " ")}
          </span>
        </div>
      </div>

      {isNativeCitation ? (
        <blockquote className="mt-3 border-l-2 border-emerald-300 pl-3 text-sm italic leading-relaxed text-slate-600">
          {e.cited_text}
        </blockquote>
      ) : (
        <p className="mt-2 text-sm leading-relaxed text-slate-500">{e.content_snippet}</p>
      )}

      {isNativeCitation && e.relevance_explanation && (
        <p className="mt-2 text-xs text-slate-400">{e.relevance_explanation.slice(0, 250)}</p>
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
  onAnnotateStep,
  onReviewReasoning,
  annotationPending,
  reviewPending,
}: AIRecommendationCardProps) {
  const score = recommendation?.suitability_score ? parseFloat(recommendation.suitability_score) : null
  const scorePercent = score !== null ? score * 100 : 0
  const [showEvidence, setShowEvidence] = useState(false)
  const reviewStatus = recommendation?.reasoning_metadata?.review_status ?? "pending"
  const isReviewed = reviewStatus === "reviewed"

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
      <div className="flex items-center gap-2.5 border-b border-slate-100 px-5 py-4">
        <Sparkles className="h-5 w-5 text-sky-500" />
        <h2 className="text-base font-semibold text-slate-800">AI-rekommendation</h2>
        {recommendation && (
          <div className="ml-auto flex items-center gap-2">
            <ComplianceBadge recommendation={recommendation} />
            <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-500">
              v{recommendation.version}
            </span>
          </div>
        )}
      </div>

      {/* Empty state */}
      {!recommendation && !isPending && (
        <div className="px-5 py-10">
          <div className="flex flex-col items-center justify-center">
            <Sparkles className="mb-3 h-12 w-12 text-slate-200" />
            <p className="mb-1 text-base font-medium text-slate-600">Ingen rekommendation genererad</p>
            <p className="mb-5 text-sm text-slate-400">Generera en lämplighetsbedömd AI-rekommendation för detta ärende.</p>
          </div>
          <Textarea
            placeholder="Valfritt: Lägg till kontext eller specifika frågor till AI:n..."
            value={additionalContext}
            onChange={(e) => onAdditionalContextChange(e.target.value)}
            className="mt-2 text-sm"
            rows={3}
          />
          <button
            onClick={onGenerate}
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-sky-500 px-4 py-3 text-base font-medium text-white transition-colors hover:bg-sky-600"
          >
            <Sparkles className="h-5 w-5" />
            Generera rekommendation
          </button>
        </div>
      )}

      {/* Generating state */}
      {isPending && (
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="mb-4 h-8 w-8 animate-spin text-sky-500" />
          <div className="space-y-3">
            {GENERATION_STEPS.map((s, i) => (
              <div
                key={s}
                className={cn(
                  "flex items-center gap-2.5 text-sm transition-colors",
                  i === 0 ? "text-slate-700" : "text-slate-300"
                )}
              >
                <span
                  className={cn(
                    "h-2 w-2 rounded-full",
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
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Lämplighetspoäng</p>
                <span className={cn("text-lg font-bold", scoreColor(score))}>{Math.round(score * 100)}%</span>
              </div>
              <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                <div className={cn("h-full rounded-full transition-all", scoreBarBg(score))} style={{ width: `${scorePercent}%` }} />
              </div>
              <p className="mt-1.5 text-sm text-slate-400">
                {score >= 0.8
                  ? "Hög lämplighet — rekommendationen är väl anpassad till klientens profil."
                  : score >= 0.6
                  ? "Medel lämplighet — granska antaganden noggrant."
                  : "Låg lämplighet — väsentliga frågetecken identifierade."}
              </p>
            </div>
          )}

          {/* Summary */}
          <section>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Sammanfattning</h3>
            <p className="text-sm leading-relaxed text-slate-600">{recommendation.summary}</p>
          </section>

          {/* Reasoning chain */}
          {recommendation.reasoning_chain?.length > 0 && (
            <section>
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Resonemangskedja</h3>
                {onReviewReasoning && !isReviewed && (
                  <button
                    onClick={() => onReviewReasoning()}
                    disabled={reviewPending}
                    className="flex items-center gap-1 rounded-md border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 hover:bg-emerald-100 disabled:opacity-50"
                  >
                    {reviewPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <ShieldCheck className="h-3 w-3" />}
                    Markera som granskad
                  </button>
                )}
                {isReviewed && (
                  <span className="flex items-center gap-1 text-xs text-emerald-600">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    Granskad
                  </span>
                )}
              </div>
              <div className="relative space-y-4 pl-5">
                <div className="absolute left-[9px] top-0 h-full w-px bg-slate-100" />
                {recommendation.reasoning_chain.map((step) => (
                  <ReasoningStepItem
                    key={step.step}
                    step={step}
                    onAnnotate={onAnnotateStep}
                    annotationPending={annotationPending}
                  />
                ))}
              </div>
            </section>
          )}

          {/* Assumptions */}
          {recommendation.assumptions?.length > 0 && (
            <section>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Antaganden</h3>
              <ul className="space-y-2">
                {recommendation.assumptions.map((a, i) => (
                  <li key={i} className="flex items-start gap-2.5 text-sm text-slate-500">
                    <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
                    <div>
                      <span>{a.assumption}</span>
                      {a.impact_if_wrong && (
                        <p className="mt-0.5 text-xs text-amber-600">{a.impact_if_wrong}</p>
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
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Scenarion</h3>
              <div className="grid gap-3 sm:grid-cols-2">
                {recommendation.scenarios.map((s, i) => (
                  <div
                    key={s.name}
                    className={cn(
                      "rounded-lg border p-4",
                      i === recommendation.scenarios!.length - 1
                        ? "border-emerald-200 bg-emerald-50"
                        : "border-slate-200"
                    )}
                  >
                    <p className={cn("text-sm font-semibold", i === recommendation.scenarios!.length - 1 ? "text-emerald-700" : "text-slate-700")}>
                      {s.name}
                    </p>
                    <p className="mt-1 text-sm text-slate-500">{s.description}</p>
                    {Object.keys(s.projected_outcome).length > 0 && (
                      <div className="mt-2.5 space-y-1">
                        {Object.entries(s.projected_outcome).map(([k, v]) => (
                          <div key={k} className="flex items-center justify-between text-sm">
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

          {/* Evidence - collapsible */}
          {evidence && evidence.length > 0 && (() => {
            const verified = evidence.filter((e) => e.verification_status === "verified").length
            const partial = evidence.filter((e) => e.verification_status === "partially_verified").length
            const unverified = evidence.filter((e) => e.verification_status === "unverified").length

            return (
              <section>
                <button
                  onClick={() => setShowEvidence(!showEvidence)}
                  className="mb-3 flex w-full items-center justify-between"
                >
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Underlag ({evidence.length} källor)
                  </h3>
                  <div className="flex items-center gap-3">
                    {verified > 0 && (
                      <span className="flex items-center gap-1 text-xs text-emerald-600">
                        <ShieldCheck className="h-3.5 w-3.5" />
                        {verified}
                      </span>
                    )}
                    {partial > 0 && (
                      <span className="flex items-center gap-1 text-xs text-amber-500">
                        <AlertTriangle className="h-3.5 w-3.5" />
                        {partial}
                      </span>
                    )}
                    {unverified > 0 && (
                      <span className="flex items-center gap-1 text-xs text-red-500">
                        <XCircle className="h-3.5 w-3.5" />
                        {unverified}
                      </span>
                    )}
                    <span className="text-xs text-slate-400">{showEvidence ? "Dölj" : "Visa"}</span>
                  </div>
                </button>
                {showEvidence && (
                  <div className="space-y-2">
                    {evidence.map((e) => (
                      <EvidenceCard key={e.id} evidence={e} />
                    ))}
                  </div>
                )}
              </section>
            )
          })()}

          {/* Action buttons */}
          <div className="flex flex-col gap-2 pt-2">
            <button
              onClick={() => onGenerateDoc("docx")}
              disabled={generateDocPending}
              className="flex items-center justify-center gap-2 rounded-lg bg-sky-500 py-3 text-sm font-medium text-white transition-colors hover:bg-sky-600 disabled:opacity-50"
            >
              {generateDocPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <FileText className="h-4 w-4" />
              )}
              Generera dokumentation
            </button>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={onDownload}
                disabled={!generatedDoc}
                className="flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white py-2.5 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50 disabled:opacity-50"
              >
                <Download className="h-4 w-4" />
                Ladda ner {generatedDoc?.file_format?.toUpperCase() ?? "DOCX"}
              </button>
              <button
                onClick={onGenerate}
                className="flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white py-2.5 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50"
              >
                <RefreshCw className="h-4 w-4" />
                Ny version
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
