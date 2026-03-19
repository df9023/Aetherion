"use client"

import { use, useState, useEffect, useRef, useCallback } from "react"
import {
  Calendar,
  User,
  Building2,
  Shield,
  Target,
  Clock,
  Sparkles,
  FileText,
  Download,
  RefreshCw,
  Search,
  AlertTriangle,
  BookOpen,
  Cpu,
  Loader2,
} from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import {
  useCase,
  useClient,
  useCaseRecommendations,
  useRecommendationEvidence,
  useCaseAudit,
  useGenerateRecommendation,
  useGenerateDocument,
  useKnowledgeSearch,
  downloadDocument,
} from "@/lib/hooks"
import type { DocumentResponse } from "@/lib/hooks"
import {
  caseTypeLabels,
  statusStyles,
  statusLabels,
  categoryStyles,
  categoryLabels,
  sourceTypeStyles,
  auditActionLabels,
} from "@/lib/labels"

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-SE", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

function formatCurrency(amount: string) {
  return new Intl.NumberFormat("sv-SE").format(Number(amount)) + " kr"
}

function calculateAge(dob: string) {
  const birth = new Date(dob)
  const now = new Date()
  let age = now.getFullYear() - birth.getFullYear()
  if (now.getMonth() < birth.getMonth() || (now.getMonth() === birth.getMonth() && now.getDate() < birth.getDate())) {
    age--
  }
  return age
}

function scoreColor(score: number) {
  if (score >= 8) return "text-emerald-600"
  if (score >= 6) return "text-amber-600"
  return "text-red-600"
}

function scoreBarColor(score: number) {
  if (score >= 8) return "[&>div]:bg-emerald-500"
  if (score >= 6) return "[&>div]:bg-amber-500"
  return "[&>div]:bg-red-500"
}

function useDebounced(value: string, delay: number) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return debounced
}

export default function CaseDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const { data: caseData, isLoading: caseLoading } = useCase(id)
  const { data: client, isLoading: clientLoading } = useClient(caseData?.client_id ?? "")
  const { data: recommendations } = useCaseRecommendations(id)
  const recommendation = recommendations?.[0]
  const { data: evidence } = useRecommendationEvidence(recommendation?.id)
  const { data: auditEntries } = useCaseAudit(id)
  const generateRec = useGenerateRecommendation(id)
  const generateDoc = useGenerateDocument(recommendation?.id)

  const [additionalContext, setAdditionalContext] = useState("")
  const [knowledgeQuery, setKnowledgeQuery] = useState("")
  const debouncedQuery = useDebounced(knowledgeQuery, 300)
  const { data: knowledgeResults } = useKnowledgeSearch(debouncedQuery)

  const [generatedDoc, setGeneratedDoc] = useState<DocumentResponse | null>(null)

  const handleGenerate = useCallback(() => {
    generateRec.mutate(additionalContext || undefined, {
      onError: (err) => toast.error(err.message),
    })
  }, [generateRec, additionalContext])

  const handleGenerateDoc = useCallback(
    (format: string) => {
      generateDoc.mutate(format, {
        onSuccess: (doc) => {
          setGeneratedDoc(doc)
          toast.success("Document generated")
        },
        onError: (err) => toast.error(err.message),
      })
    },
    [generateDoc]
  )

  const handleDownload = useCallback(() => {
    if (generatedDoc) {
      downloadDocument(generatedDoc.id, `${generatedDoc.title}.${generatedDoc.file_format}`)
    }
  }, [generatedDoc])

  if (caseLoading) {
    return (
      <div className="grid grid-cols-[1fr_400px] gap-6">
        <div className="space-y-6">
          <Skeleton className="h-40 rounded-xl" />
          <Skeleton className="h-60 rounded-xl" />
          <Skeleton className="h-96 rounded-xl" />
        </div>
        <div className="space-y-6">
          <Skeleton className="h-80 rounded-xl" />
          <Skeleton className="h-40 rounded-xl" />
        </div>
      </div>
    )
  }

  if (!caseData) {
    return <div className="py-12 text-center text-slate-400">Case not found</div>
  }

  const score = recommendation?.suitability_score ? parseFloat(recommendation.suitability_score) : null
  const audit = auditEntries ?? []

  return (
    <div className="grid grid-cols-[1fr_400px] gap-6">
      {/* Left column */}
      <div className="space-y-6">
        {/* Case header */}
        <div className="rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-xl font-semibold text-slate-900">{caseData.title}</h1>
              <p className="mt-1 text-sm text-slate-500">{caseData.summary}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${statusStyles[caseData.status] ?? ""}`}>
                {statusLabels[caseData.status] ?? caseData.status}
              </span>
              <span className="inline-flex rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                {caseTypeLabels[caseData.case_type] ?? caseData.case_type}
              </span>
            </div>
          </div>
          <div className="mt-4 flex items-center gap-6 text-sm text-slate-500">
            {caseData.meeting_date && (
              <span className="flex items-center gap-1.5">
                <Calendar className="h-4 w-4 text-slate-400" />
                Meeting: {formatDate(caseData.meeting_date)}
              </span>
            )}
          </div>
        </div>

        {/* Client info */}
        <div className="rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm">
          <h2 className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Client Information</h2>
          {clientLoading ? (
            <div className="mt-4 space-y-3">
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-4 w-1/3" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          ) : client ? (
            <div className="mt-4 grid grid-cols-2 gap-x-8 gap-y-4">
              <div>
                <p className="text-xs text-slate-400">Name</p>
                <p className="text-sm font-medium text-slate-900">{client.name}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Age</p>
                <p className="text-sm font-medium text-slate-900">{calculateAge(client.date_of_birth)} years</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Employer</p>
                <p className="flex items-center gap-1.5 text-sm font-medium text-slate-900">
                  <Building2 className="h-3.5 w-3.5 text-slate-400" />
                  {client.employer_name}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Collective Agreement</p>
                <span className="inline-flex rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                  {client.collective_agreement}
                </span>
              </div>
              <div>
                <p className="text-xs text-slate-400">Monthly Income</p>
                <p className="text-sm font-medium text-slate-900">
                  {client.annual_income
                    ? formatCurrency(String(Math.round(Number(client.annual_income) / 12)))
                    : "—"}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Risk Profile</p>
                {client.risk_profile ? (
                  <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                    client.risk_profile === "low"
                      ? "bg-green-50 text-green-700"
                      : client.risk_profile === "moderate"
                        ? "bg-amber-50 text-amber-700"
                        : "bg-red-50 text-red-700"
                  }`}>
                    <Shield className="h-3 w-3" />
                    {client.risk_profile.charAt(0).toUpperCase() + client.risk_profile.slice(1)}
                  </span>
                ) : (
                  <span className="text-sm text-slate-400">—</span>
                )}
              </div>
              <div>
                <p className="text-xs text-slate-400">Desired Retirement Age</p>
                <p className="flex items-center gap-1.5 text-sm font-medium text-slate-900">
                  <Target className="h-3.5 w-3.5 text-slate-400" />
                  {client.desired_retirement_age ?? "—"}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Employment Status</p>
                <p className="text-sm font-medium capitalize text-slate-900">{client.employment_status}</p>
              </div>
            </div>
          ) : (
            <p className="mt-4 text-sm text-slate-400">Client not found</p>
          )}
        </div>

        {/* AI Recommendation */}
        <div className="rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-sky-500" />
            <h2 className="text-lg font-semibold text-slate-900">AI Recommendation</h2>
            {recommendation && (
              <Badge variant="secondary" className="ml-2 text-xs">v{recommendation.version}</Badge>
            )}
          </div>

          {/* State 1: No recommendation */}
          {!recommendation && !generateRec.isPending && (
            <div className="mt-6">
              <div className="flex flex-col items-center py-8 text-center">
                <Sparkles className="h-10 w-10 text-slate-300" />
                <p className="mt-3 text-sm font-medium text-slate-600">Generate an AI recommendation for this case</p>
                <p className="mt-1 text-xs text-slate-400">The AI will analyze the client data, retrieve relevant knowledge, and produce a structured recommendation.</p>
              </div>
              <Textarea
                placeholder="Optional: Add context or specific questions for the AI..."
                value={additionalContext}
                onChange={(e) => setAdditionalContext(e.target.value)}
                className="mt-4"
                rows={3}
              />
              <Button
                onClick={handleGenerate}
                className="mt-4 h-12 w-full bg-sky-500 hover:bg-sky-600 text-white rounded-lg"
              >
                <Sparkles className="mr-2 h-4 w-4" />
                Generate Recommendation
              </Button>
            </div>
          )}

          {/* State 2: Generating */}
          {generateRec.isPending && (
            <div className="mt-6 space-y-4 py-8">
              {["Retrieving knowledge", "Analyzing case", "Building recommendation"].map((step, i) => (
                <div key={step} className="flex items-center gap-3">
                  <div className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${
                    i === 0 ? "bg-sky-500 text-white" : "bg-slate-200 text-slate-500"
                  }`}>
                    {i === 0 ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : i + 1}
                  </div>
                  <span className={`text-sm ${i === 0 ? "font-medium text-slate-900" : "text-slate-400"}`}>
                    {step}...
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* State 3: Recommendation exists */}
          {recommendation && !generateRec.isPending && (
            <>
              {/* Suitability score */}
              {score !== null && (
                <div className="mt-6 flex items-center gap-6">
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Suitability Score</p>
                    <p className={`mt-1 text-4xl font-bold ${scoreColor(score)}`}>{recommendation.suitability_score}</p>
                    <p className="text-xs text-slate-400">out of 10</p>
                  </div>
                  <div className="flex-1">
                    <Progress value={score * 10} className={`h-3 ${scoreBarColor(score)}`} />
                  </div>
                </div>
              )}

              {/* Summary */}
              <div className="mt-6">
                <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Summary</p>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{recommendation.summary}</p>
              </div>

              <Separator className="my-6" />

              {/* Reasoning chain */}
              {recommendation.reasoning_chain?.length > 0 && (
                <div>
                  <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Reasoning Chain</p>
                  <div className="mt-4 space-y-0">
                    {recommendation.reasoning_chain.map((step, i) => (
                      <div key={step.step} className="relative flex gap-4 pb-6 last:pb-0">
                        {i < recommendation.reasoning_chain.length - 1 && (
                          <div className="absolute left-[15px] top-8 h-[calc(100%-16px)] w-px bg-slate-200" />
                        )}
                        <div className="relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-sky-500 text-xs font-bold text-white">
                          {step.step}
                        </div>
                        <div className="min-w-0 flex-1 pt-0.5">
                          <p className="text-sm font-medium text-slate-900">{step.description}</p>
                          <p className="mt-1 text-sm text-slate-500">{step.conclusion}</p>
                          {step.evidence_ids?.length > 0 && evidence && (
                            <div className="mt-2 flex flex-wrap gap-1.5">
                              {step.evidence_ids.map((eid) => {
                                const ev = evidence.find((e) => e.id === eid)
                                return ev ? (
                                  <span key={eid} className="inline-flex rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-500">
                                    {ev.source_reference}
                                  </span>
                                ) : null
                              })}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  <Separator className="my-6" />
                </div>
              )}

              {/* Assumptions */}
              {recommendation.assumptions?.length > 0 && (
                <div>
                  <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Assumptions</p>
                  <div className="mt-4 space-y-3">
                    {recommendation.assumptions.map((a, i) => (
                      <div key={i} className="rounded-lg border border-slate-100 bg-slate-50/50 p-4">
                        <p className="text-sm font-medium text-slate-900">{a.assumption}</p>
                        <p className="mt-1 text-xs text-slate-500">Basis: {a.basis}</p>
                        <div className="mt-2 flex items-start gap-1.5 rounded-md bg-amber-50 p-2">
                          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-500" />
                          <p className="text-xs text-amber-700">{a.impact_if_wrong}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                  <Separator className="my-6" />
                </div>
              )}

              {/* Scenarios */}
              {recommendation.scenarios && recommendation.scenarios.length > 0 && (
                <div>
                  <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Scenarios</p>
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    {recommendation.scenarios.map((s) => (
                      <div key={s.name} className="rounded-lg border border-slate-100 bg-slate-50/50 p-4">
                        <p className="text-sm font-semibold text-slate-900">{s.name}</p>
                        <p className="mt-1 text-xs text-slate-500">{s.description}</p>
                        <div className="mt-3 space-y-1.5">
                          {Object.entries(s.projected_outcome).map(([k, v]) => (
                            <div key={k} className="flex items-center justify-between text-xs">
                              <span className="text-slate-400">{k}</span>
                              <span className="font-medium text-slate-700">{String(v)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                  <Separator className="my-6" />
                </div>
              )}

              {/* Evidence */}
              {evidence && evidence.length > 0 && (
                <div>
                  <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Evidence</p>
                  <div className="mt-4 space-y-3">
                    {evidence.map((ev) => (
                      <div key={ev.id} className="rounded-lg border border-slate-100 p-4">
                        <div className="flex items-center gap-2">
                          <span className={`inline-flex rounded-full px-2.5 py-0.5 text-[10px] font-medium ${sourceTypeStyles[ev.source_type] ?? "bg-slate-100 text-slate-600"}`}>
                            {ev.source_type.replace(/_/g, " ")}
                          </span>
                          <span className="text-sm font-medium text-slate-900">{ev.source_reference}</span>
                        </div>
                        <p className="mt-2 text-xs leading-relaxed text-slate-500">{ev.content_snippet}</p>
                        <div className="mt-2 flex items-center justify-between">
                          <p className="text-[10px] text-slate-400">{ev.relevance_explanation}</p>
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] text-slate-400">{Math.round(parseFloat(ev.confidence) * 100)}%</span>
                            <div className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-100">
                              <div
                                className="h-full rounded-full bg-sky-500"
                                style={{ width: `${parseFloat(ev.confidence) * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <Separator className="my-6" />
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center gap-3">
                <Button
                  onClick={() => handleGenerateDoc("docx")}
                  disabled={generateDoc.isPending}
                  className="bg-sky-500 hover:bg-sky-600 text-white rounded-lg"
                >
                  {generateDoc.isPending ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <FileText className="mr-2 h-4 w-4" />
                  )}
                  Generate Document
                </Button>
                {generatedDoc && (
                  <Button variant="outline" className="rounded-lg" onClick={handleDownload}>
                    <Download className="mr-2 h-4 w-4" />
                    Download {generatedDoc.file_format.toUpperCase()}
                  </Button>
                )}
                <Button
                  variant="outline"
                  className="rounded-lg"
                  onClick={handleGenerate}
                  disabled={generateRec.isPending}
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Generate New Version
                </Button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Right column */}
      <div className="space-y-6">
        {/* Knowledge search */}
        <div className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm">
          <h2 className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Knowledge Base</h2>
          <div className="relative mt-3">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <Input
              placeholder="Search knowledge..."
              className="pl-9 text-sm"
              value={knowledgeQuery}
              onChange={(e) => setKnowledgeQuery(e.target.value)}
            />
          </div>
          <div className="mt-4 space-y-3">
            {knowledgeResults && knowledgeResults.length > 0
              ? knowledgeResults.map((k) => (
                  <details key={k.id} className="group">
                    <summary className="cursor-pointer list-none rounded-lg p-3 transition-colors hover:bg-slate-50">
                      <div className="flex items-start justify-between">
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium text-slate-900">{k.title}</p>
                          <span className={`mt-1 inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium ${categoryStyles[k.category] ?? "bg-slate-100 text-slate-600"}`}>
                            {categoryLabels[k.category] ?? k.category}
                          </span>
                        </div>
                        <BookOpen className="mt-1 h-3.5 w-3.5 shrink-0 text-slate-300" />
                      </div>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {k.tags.map((t) => (
                          <span key={t} className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500">
                            {t}
                          </span>
                        ))}
                      </div>
                    </summary>
                    <div className="px-3 pb-3">
                      <p className="text-xs leading-relaxed text-slate-500">{k.content}</p>
                    </div>
                  </details>
                ))
              : debouncedQuery.length >= 2 ? (
                  <p className="py-4 text-center text-xs text-slate-400">No results</p>
                ) : (
                  <p className="py-4 text-center text-xs text-slate-400">Type to search knowledge base...</p>
                )}
          </div>
        </div>

        {/* Audit trail */}
        <div className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm">
          <h2 className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Audit Trail</h2>
          <div className="mt-4 space-y-0">
            {audit.map((a, i) => (
              <div key={a.id} className="relative flex gap-3 pb-6 last:pb-0">
                {i < audit.length - 1 && (
                  <div className="absolute left-[7px] top-5 h-[calc(100%-8px)] w-px bg-slate-200" />
                )}
                <div className={`relative z-10 mt-1 h-4 w-4 shrink-0 rounded-full ${
                  a.actor_type === "system" ? "bg-sky-500" : "bg-slate-300"
                }`}>
                  {a.actor_type === "system" ? (
                    <Cpu className="h-2.5 w-2.5 absolute top-[3px] left-[3px] text-white" />
                  ) : (
                    <User className="h-2.5 w-2.5 absolute top-[3px] left-[3px] text-white" />
                  )}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-900">
                    {auditActionLabels[a.action] ?? a.action}
                  </p>
                  <p className="flex items-center gap-1 text-xs text-slate-400">
                    <Clock className="h-3 w-3" />
                    {formatDate(a.timestamp)}
                  </p>
                </div>
              </div>
            ))}
            {audit.length === 0 && (
              <p className="py-4 text-center text-xs text-slate-400">No audit entries</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
