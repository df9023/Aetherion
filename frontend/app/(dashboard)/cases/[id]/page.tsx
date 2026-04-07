"use client"

import { use, useState, useEffect, useCallback } from "react"
import { toast } from "sonner"
import { Skeleton } from "@/components/ui/skeleton"
import {
  useCase,
  useClient,
  useCaseRecommendations,
  useRecommendationEvidence,
  useCaseAudit,
  useGenerateRecommendation,
  useGenerateMeetingBrief,
  useGenerateDocument,
  useKnowledgeSearch,
  useUpdateCase,
  useAnnotateReasoningStep,
  useReviewReasoning,
  downloadDocument,
} from "@/lib/hooks"
import type { DocumentResponse, MeetingBriefResponse } from "@/lib/hooks"
import { TopBar } from "@/components/top-bar"
import { CaseHeaderCard } from "@/components/case-header-card"
import { MeetingPrepCard } from "@/components/meeting-prep-card"
import { ClientInfoCard } from "@/components/client-info-card"
import { AIRecommendationCard } from "@/components/ai-recommendation-card"
import { KnowledgeBaseCard } from "@/components/knowledge-base-card"
import { AuditTrailCard } from "@/components/audit-trail-card"
import { FirmInsightsCard } from "@/components/firm-insights-card"
import { FirmInsightDialog } from "@/components/firm-insight-dialog"
import { Lightbulb } from "lucide-react"

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
  const generateBrief = useGenerateMeetingBrief(id)
  const generateDoc = useGenerateDocument(recommendation?.id)
  const annotateStep = useAnnotateReasoningStep(recommendation?.id, id)
  const reviewReasoning = useReviewReasoning(recommendation?.id, id)
  const updateCase = useUpdateCase(id)

  const [meetingBrief, setMeetingBrief] = useState<MeetingBriefResponse | null>(null)
  const [additionalContext, setAdditionalContext] = useState("")
  const [knowledgeQuery, setKnowledgeQuery] = useState("")
  const debouncedQuery = useDebounced(knowledgeQuery, 300)
  const { data: knowledgeResults } = useKnowledgeSearch(debouncedQuery)

  const [generatedDoc, setGeneratedDoc] = useState<DocumentResponse | null>(null)
  const [showInsightDialog, setShowInsightDialog] = useState(false)

  const handleGenerate = useCallback(() => {
    generateRec.mutate(additionalContext || undefined, {
      onError: (err) => toast.error(err.message),
    })
  }, [generateRec, additionalContext])

  const handleGenerateBrief = useCallback(() => {
    generateBrief.mutate(undefined, {
      onSuccess: (data) => {
        setMeetingBrief(data)
        toast.success("Mötesunderlag genererat")
      },
      onError: (err) => toast.error(err.message),
    })
  }, [generateBrief])

  const handleGenerateDoc = useCallback(
    (format: string) => {
      generateDoc.mutate(format, {
        onSuccess: (doc) => {
          setGeneratedDoc(doc)
          toast.success("Dokument genererat")
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

  const handleAnnotateStep = useCallback(
    (step: number, annotation: string) => {
      annotateStep.mutate(
        { step, annotation },
        {
          onSuccess: () => toast.success("Kommentar sparad"),
          onError: (err) => toast.error(err.message),
        }
      )
    },
    [annotateStep]
  )

  const handleReviewReasoning = useCallback(
    (comment?: string) => {
      reviewReasoning.mutate(comment, {
        onSuccess: () => toast.success("Resonemangskedja markerad som granskad"),
        onError: (err) => toast.error(err.message),
      })
    },
    [reviewReasoning]
  )

  const handleStatusChange = useCallback(
    (status: string) => {
      updateCase.mutate(
        { status },
        { onSuccess: () => toast.success("Status uppdaterad") }
      )
    },
    [updateCase]
  )

  if (caseLoading) {
    return (
      <>
        <TopBar breadcrumbs={[{ label: "Ärenden", href: "/cases" }, { label: "Laddar..." }]} />
        <main className="flex flex-1 flex-col gap-5 px-6 py-6 lg:flex-row">
          <div className="flex min-w-0 flex-1 flex-col gap-5">
            <Skeleton className="h-24 rounded-xl" />
            <Skeleton className="h-60 rounded-xl" />
            <Skeleton className="h-40 rounded-xl" />
            <Skeleton className="h-96 rounded-xl" />
          </div>
          <div className="flex w-full shrink-0 flex-col gap-5 lg:w-[380px]">
            <Skeleton className="h-80 rounded-xl" />
            <Skeleton className="h-40 rounded-xl" />
          </div>
        </main>
      </>
    )
  }

  if (!caseData) {
    return (
      <>
        <TopBar breadcrumbs={[{ label: "Ärenden", href: "/cases" }, { label: "Hittades inte" }]} />
        <main className="flex-1">
          <div className="py-12 text-center text-sm text-slate-400">Ärendet hittades inte</div>
        </main>
      </>
    )
  }

  const audit = auditEntries ?? []

  return (
    <>
      <TopBar
        breadcrumbs={[
          { label: "Ärenden", href: "/cases" },
          { label: caseData.title.length > 50 ? caseData.title.slice(0, 50) + "…" : caseData.title },
        ]}
      />
      <main className="flex flex-1 flex-col gap-5 px-6 py-6 lg:flex-row">
        {/* Left column */}
        <div className="flex min-w-0 flex-1 flex-col gap-5">
          {caseData.status === "completed" && (
            <div className="flex items-center justify-between gap-3 rounded-xl border border-amber-200 bg-amber-50 px-5 py-3">
              <div className="flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-amber-600" />
                <p className="text-sm text-amber-900">
                  Har du lärdomar från detta ärende?
                </p>
              </div>
              <button
                onClick={() => setShowInsightDialog(true)}
                className="rounded-lg border border-amber-300 bg-white px-3 py-1.5 text-xs font-medium text-amber-800 hover:bg-amber-100"
              >
                Lägg till insikt
              </button>
            </div>
          )}
          <CaseHeaderCard caseData={caseData} onStatusChange={handleStatusChange} />
          <MeetingPrepCard brief={meetingBrief} isPending={generateBrief.isPending} onGenerate={handleGenerateBrief} />
          <ClientInfoCard client={client} isLoading={clientLoading} />
          <AIRecommendationCard
            recommendation={recommendation}
            evidence={evidence}
            isPending={generateRec.isPending}
            onGenerate={handleGenerate}
            onGenerateDoc={handleGenerateDoc}
            onDownload={handleDownload}
            generatedDoc={generatedDoc}
            generateDocPending={generateDoc.isPending}
            additionalContext={additionalContext}
            onAdditionalContextChange={setAdditionalContext}
            onAnnotateStep={handleAnnotateStep}
            onReviewReasoning={handleReviewReasoning}
            annotationPending={annotateStep.isPending}
            reviewPending={reviewReasoning.isPending}
          />
        </div>

        {/* Right panel */}
        <div className="flex w-full shrink-0 flex-col gap-5 lg:w-[380px]">
          <KnowledgeBaseCard query={knowledgeQuery} onQueryChange={setKnowledgeQuery} results={knowledgeResults} />
          <FirmInsightsCard
            caseId={id}
            caseType={caseData.case_type}
            clientCollectiveAgreement={client?.collective_agreement}
            clientOrganizationId={client?.client_organization_id ?? null}
          />
          <AuditTrailCard entries={audit} />
        </div>
      </main>

      {showInsightDialog && (
        <FirmInsightDialog
          open={showInsightDialog}
          onOpenChange={setShowInsightDialog}
          defaultValues={{
            source_case_id: id,
            case_types: caseData.case_type ? [caseData.case_type] : [],
            collective_agreements: client?.collective_agreement
              ? [client.collective_agreement]
              : [],
            client_organization_id: client?.client_organization_id ?? null,
            category: "lesson_learned",
          }}
        />
      )}
    </>
  )
}
