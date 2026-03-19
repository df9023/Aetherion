import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiFetch, apiDownload } from "./api"

// Types matching backend schemas
export interface CaseResponse {
  id: string
  title: string
  case_type: string
  status: string
  summary: string | null
  meeting_date: string | null
  client_id: string
  assigned_to: string
  organization_id: string
  created_at: string
  updated_at: string
  completed_at: string | null
}

export interface ClientResponse {
  id: string
  name: string
  date_of_birth: string
  employment_status: string
  collective_agreement: string
  external_id: string | null
  employer_name: string | null
  annual_income: string | null
  desired_retirement_age: number | null
  risk_profile: string | null
  organization_id: string
  created_at: string
  updated_at: string
  created_by: string
}

export interface RecommendationResponse {
  id: string
  case_id: string
  recommendation_type: string
  summary: string
  reasoning_chain: {
    step: number
    description: string
    evidence_ids: string[]
    conclusion: string
  }[]
  assumptions: {
    assumption: string
    basis: string
    impact_if_wrong: string
  }[]
  scenarios: {
    name: string
    description: string
    projected_outcome: Record<string, string>
  }[] | null
  suitability_score: string | null
  version: number
  status: string
  created_at: string
  created_by: string
  approved_by: string | null
}

export interface EvidenceResponse {
  id: string
  recommendation_id: string
  source_type: string
  source_reference: string
  content_snippet: string
  relevance_explanation: string
  confidence: string
  created_at: string
}

export interface KnowledgeItemResponse {
  id: string
  title: string
  content: string
  category: string
  source: string
  tags: string[]
  effective_date: string | null
  expiry_date: string | null
  organization_id: string
  is_active: boolean
  created_at: string
  updated_at: string
  created_by: string
  approved_by: string | null
}

export interface AuditEntryResponse {
  id: string
  case_id: string
  action: string
  actor_id: string
  actor_type: string
  details: Record<string, unknown>
  ip_address: string | null
  timestamp: string
}

export interface DocumentResponse {
  id: string
  document_type: string
  title: string
  file_format: string
  case_id: string
  recommendation_id: string | null
  file_path: string
  generated_at: string
  generated_by: string
  version: number
}

// Cases
export function useCases() {
  return useQuery({
    queryKey: ["cases"],
    queryFn: () => apiFetch<CaseResponse[]>("/cases"),
  })
}

export function useCase(id: string) {
  return useQuery({
    queryKey: ["cases", id],
    queryFn: () => apiFetch<CaseResponse>(`/cases/${id}`),
    enabled: !!id,
  })
}

// Clients
export function useClients() {
  return useQuery({
    queryKey: ["clients"],
    queryFn: () => apiFetch<ClientResponse[]>("/clients"),
  })
}

export function useClient(id: string) {
  return useQuery({
    queryKey: ["clients", id],
    queryFn: () => apiFetch<ClientResponse>(`/clients/${id}`),
    enabled: !!id,
  })
}

// Recommendations for a case
export function useCaseRecommendations(caseId: string) {
  return useQuery({
    queryKey: ["cases", caseId, "recommendations"],
    queryFn: () => apiFetch<RecommendationResponse[]>(`/cases/${caseId}/recommendations`),
    enabled: !!caseId,
  })
}

// Evidence for a recommendation
export function useRecommendationEvidence(recId: string | undefined) {
  return useQuery({
    queryKey: ["recommendations", recId, "evidence"],
    queryFn: () => apiFetch<EvidenceResponse[]>(`/recommendations/${recId}/evidence`),
    enabled: !!recId,
  })
}

// Generate recommendation (mutation)
export function useGenerateRecommendation(caseId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (additionalContext?: string) =>
      apiFetch<RecommendationResponse>(`/cases/${caseId}/generate-recommendation`, {
        method: "POST",
        body: JSON.stringify({ additional_context: additionalContext || null }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cases", caseId, "recommendations"] })
      queryClient.invalidateQueries({ queryKey: ["cases", caseId, "audit"] })
    },
  })
}

// Audit trail
export function useCaseAudit(caseId: string) {
  return useQuery({
    queryKey: ["cases", caseId, "audit"],
    queryFn: () => apiFetch<AuditEntryResponse[]>(`/cases/${caseId}/audit`),
    enabled: !!caseId,
  })
}

// Knowledge search
export function useKnowledgeSearch(query: string) {
  return useQuery({
    queryKey: ["knowledge", "search", query],
    queryFn: () =>
      apiFetch<KnowledgeItemResponse[]>("/knowledge/search", {
        method: "POST",
        body: JSON.stringify({ query, limit: 10 }),
      }),
    enabled: query.length >= 2,
  })
}

// Knowledge list
export function useKnowledge() {
  return useQuery({
    queryKey: ["knowledge"],
    queryFn: () => apiFetch<KnowledgeItemResponse[]>("/knowledge"),
  })
}

// Generate document (mutation)
export function useGenerateDocument(recommendationId: string | undefined) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (fileFormat: string = "docx") =>
      apiFetch<DocumentResponse>(`/recommendations/${recommendationId}/generate-document`, {
        method: "POST",
        body: JSON.stringify({ file_format: fileFormat }),
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["cases", data.case_id, "audit"] })
    },
  })
}

// Download document
export async function downloadDocument(documentId: string, filename: string) {
  const blob = await apiDownload(`/documents/${documentId}/download`)
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
