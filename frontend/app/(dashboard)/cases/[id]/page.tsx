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
  const updateCase = useUpdateCase(id)

  const [meetingBrief, setMeetingBrief] = useState<MeetingBriefResponse | null>(null)
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
          />
        </div>

        {/* Right panel */}
        <div className="flex w-full shrink-0 flex-col gap-5 lg:w-[380px]">
          <KnowledgeBaseCard query={knowledgeQuery} onQueryChange={setKnowledgeQuery} results={knowledgeResults} />
          <AuditTrailCard entries={audit} />
        </div>
      </main>
    </>
  )
}
