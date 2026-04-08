import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiFetch, apiUpload, apiDownload } from "./api"

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
  client_organization_id: string | null
  client_organization_name: string | null
  created_at: string
  updated_at: string
  created_by: string
}

export interface CitedText {
  text: string
  source_title: string | null
  knowledge_item_id: string | null
}

export interface ReasoningStep {
  step: number
  title: string | null
  description: string
  evidence_ids: string[]
  cited_texts: CitedText[]
  conclusion: string
  advisor_annotation: string | null
  annotated_by: string | null
  annotated_at: string | null
}

export interface ReasoningMetadata {
  review_status: "pending" | "reviewed"
  reviewed_by: string | null
  reviewed_at: string | null
  review_comment: string | null
}

export interface RecommendationResponse {
  id: string
  case_id: string
  recommendation_type: string
  summary: string
  reasoning_chain: ReasoningStep[]
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
  reasoning_metadata: ReasoningMetadata | null
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
  verified: boolean
  verification_status: "verified" | "partially_verified" | "unverified"
  cited_text: string | null
  document_index: number | null
  start_char_index: number | null
  end_char_index: number | null
  knowledge_item_id: string | null
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

export interface FirmInsightResponse {
  id: string
  organization_id: string
  title: string
  content: string
  category: string
  case_types: string[]
  collective_agreements: string[]
  client_organization_id: string | null
  client_organization_name: string | null
  tags: string[]
  source_case_id: string | null
  source_case_title: string | null
  is_active: boolean
  upvotes: number
  created_by: string
  creator_name: string | null
  created_at: string
  updated_at: string
}

export interface ClientOrganizationResponse {
  id: string
  organization_id: string
  name: string
  org_number: string | null
  industry: string | null
  collective_agreement: string | null
  contact_person: string | null
  contact_email: string | null
  contact_phone: string | null
  employee_count: number | null
  notes: string | null
  client_count: number
  created_at: string
  updated_at: string
  created_by: string
}

export interface ClientOrganizationDetail extends ClientOrganizationResponse {
  clients: ClientResponse[]
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

export interface MeetingBriefResponse {
  client_overview: string
  pension_situation: {
    pillar: string
    description: string
    estimated_value: string
    notes: string
  }[]
  key_issues: {
    title: string
    description: string
    severity: "high" | "medium" | "low"
  }[]
  pre_modeled_scenarios?: {
    name: string
    description: string
    projected_outcome: Record<string, string>
  }[]
  talking_points: string[]
  open_questions: string[]
  meeting_agenda: {
    topic: string
    duration_minutes: number
    description: string
  }[]
}

export interface ExtractedField {
  field_name: string
  value: string
  confidence: number
  source_text?: string
}

export interface FundAllocation {
  fund_name: string
  allocation_percent: number
  fee_percent?: number
  confidence: number
}

export interface DocumentExtractionResponse {
  document_type: string
  extracted_fields: ExtractedField[]
  fund_allocations: FundAllocation[]
  other_observations: string
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

// Generate meeting brief (mutation)
export function useGenerateMeetingBrief(caseId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (additionalContext?: string) =>
      apiFetch<MeetingBriefResponse>(`/cases/${caseId}/generate-brief`, {
        method: "POST",
        body: JSON.stringify({ additional_context: additionalContext || null }),
      }),
    onSuccess: () => {
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

// Recent audit entries (cross-case, for dashboard)
export function useRecentAudit(limit: number = 10) {
  return useQuery({
    queryKey: ["audit", "recent", limit],
    queryFn: () => apiFetch<AuditEntryResponse[]>(`/audit/recent?limit=${limit}`),
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

// Annotate reasoning step
export function useAnnotateReasoningStep(recommendationId: string | undefined, caseId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ step, annotation }: { step: number; annotation: string }) =>
      apiFetch<RecommendationResponse>(
        `/recommendations/${recommendationId}/reasoning/${step}/annotate`,
        {
          method: "PATCH",
          body: JSON.stringify({ advisor_annotation: annotation }),
        }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cases", caseId, "recommendations"] })
      queryClient.invalidateQueries({ queryKey: ["cases", caseId, "audit"] })
    },
  })
}

// Review reasoning trail
export function useReviewReasoning(recommendationId: string | undefined, caseId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (comment?: string) =>
      apiFetch<RecommendationResponse>(
        `/recommendations/${recommendationId}/reasoning/review`,
        {
          method: "POST",
          body: JSON.stringify({ comment: comment || null }),
        }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cases", caseId, "recommendations"] })
      queryClient.invalidateQueries({ queryKey: ["cases", caseId, "audit"] })
    },
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

// Create client
export function useCreateClient() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      name: string
      date_of_birth: string
      employment_status: string
      collective_agreement: string
      employer_name?: string
      annual_income?: number
      desired_retirement_age?: number
      risk_profile?: string
    }) =>
      apiFetch<ClientResponse>("/clients", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] })
    },
  })
}

// Create case
export function useCreateCase() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      title: string
      case_type: string
      client_id: string
      assigned_to: string
      summary?: string
      meeting_date?: string
    }) =>
      apiFetch<CaseResponse>("/cases", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cases"] })
    },
  })
}

// Update case
export function useUpdateCase(caseId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      title?: string
      case_type?: string
      status?: string
      summary?: string
      assigned_to?: string
    }) =>
      apiFetch<CaseResponse>(`/cases/${caseId}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cases"] })
      queryClient.invalidateQueries({ queryKey: ["cases", caseId] })
    },
  })
}

// Client cases (filtered client-side)
export function useClientCases(clientId: string) {
  const { data: cases } = useCases()
  const clientCases = cases?.filter((c) => c.client_id === clientId) ?? []
  return { data: clientCases, isLoading: !cases }
}

// Document ingestion
export function useIngestDocument(clientId: string) {
  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData()
      formData.append("file", file)
      return apiUpload<DocumentExtractionResponse>(
        `/clients/${clientId}/ingest-document`,
        formData,
      )
    },
  })
}

// Knowledge ingestion
export interface KnowledgeIngestResponse {
  items_created: number
  chunks: { id: string; title: string; content_preview: string }[]
}

export function useIngestKnowledge() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { file: File; category: string; source: string; tags: string }) => {
      const formData = new FormData()
      formData.append("file", data.file)
      formData.append("category", data.category)
      formData.append("source", data.source)
      formData.append("tags", data.tags)
      return apiUpload<KnowledgeIngestResponse>("/knowledge/ingest-document", formData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge"] })
    },
  })
}

// Apply extraction
export function useApplyExtraction(clientId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Record<string, string | number>) =>
      apiFetch<ClientResponse>(`/clients/${clientId}/apply-extraction`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients", clientId] })
      queryClient.invalidateQueries({ queryKey: ["clients"] })
    },
  })
}

// Client Organizations
export function useClientOrganizations() {
  return useQuery({
    queryKey: ["client-organizations"],
    queryFn: () => apiFetch<ClientOrganizationResponse[]>("/client-organizations"),
  })
}

export function useClientOrganization(id: string) {
  return useQuery({
    queryKey: ["client-organizations", id],
    queryFn: () => apiFetch<ClientOrganizationDetail>(`/client-organizations/${id}`),
    enabled: !!id,
  })
}

export function useCreateClientOrganization() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      name: string
      org_number?: string
      industry?: string
      collective_agreement?: string
      contact_person?: string
      contact_email?: string
      contact_phone?: string
      employee_count?: number
      notes?: string
    }) =>
      apiFetch<ClientOrganizationResponse>("/client-organizations", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["client-organizations"] })
    },
  })
}

export function useUpdateClientOrganization(id: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      name?: string
      org_number?: string
      industry?: string
      collective_agreement?: string
      contact_person?: string
      contact_email?: string
      contact_phone?: string
      employee_count?: number
      notes?: string
    }) =>
      apiFetch<ClientOrganizationResponse>(`/client-organizations/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["client-organizations"] })
      queryClient.invalidateQueries({ queryKey: ["client-organizations", id] })
    },
  })
}

// Firm Insights
export function useFirmInsights(filters?: Record<string, string>) {
  const params = new URLSearchParams()
  if (filters) {
    for (const [key, value] of Object.entries(filters)) {
      if (value) params.set(key, value)
    }
  }
  const qs = params.toString()
  return useQuery({
    queryKey: ["firm-insights", filters ?? {}],
    queryFn: () =>
      apiFetch<FirmInsightResponse[]>(
        qs ? `/firm-insights?${qs}` : "/firm-insights",
      ),
  })
}

export function useFirmInsight(id: string | undefined) {
  return useQuery({
    queryKey: ["firm-insights", id],
    queryFn: () => apiFetch<FirmInsightResponse>(`/firm-insights/${id}`),
    enabled: !!id,
  })
}

export function useRelevantInsights(caseId: string) {
  return useQuery({
    queryKey: ["firm-insights", "relevant", caseId],
    queryFn: () =>
      apiFetch<FirmInsightResponse[]>(
        `/firm-insights/relevant?case_id=${caseId}`,
      ),
    enabled: !!caseId,
  })
}

export interface FirmInsightCreateInput {
  title: string
  content: string
  category: string
  case_types?: string[]
  collective_agreements?: string[]
  client_organization_id?: string | null
  tags?: string[]
  source_case_id?: string | null
}

export function useCreateFirmInsight() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: FirmInsightCreateInput) =>
      apiFetch<FirmInsightResponse>("/firm-insights", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["firm-insights"] })
      if (data.source_case_id) {
        queryClient.invalidateQueries({
          queryKey: ["firm-insights", "relevant", data.source_case_id],
        })
        queryClient.invalidateQueries({
          queryKey: ["cases", data.source_case_id, "audit"],
        })
      }
    },
  })
}

export function useUpvoteFirmInsight() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (insightId: string) =>
      apiFetch<FirmInsightResponse>(`/firm-insights/${insightId}/upvote`, {
        method: "POST",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["firm-insights"] })
    },
  })
}

export function useDeleteFirmInsight() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (insightId: string) =>
      apiFetch<void>(`/firm-insights/${insightId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["firm-insights"] })
    },
  })
}

// Regulatory Pulse
export type RegulatoryChangeSeverity = "critical" | "high" | "medium" | "low"
export type CaseImpactStatus =
  | "open"
  | "acknowledged"
  | "resolved"
  | "not_applicable"

export interface RegulatoryChangeResponse {
  id: string
  organization_id: string
  created_by: string | null
  creator_name: string | null
  title: string
  description: string
  source: string
  source_url: string | null
  severity: RegulatoryChangeSeverity
  affected_case_types: string[]
  affected_agreements: string[]
  affected_tags: string[]
  knowledge_item_id: string | null
  knowledge_item_title: string | null
  is_active: boolean
  published_at: string
  created_at: string
  updated_at: string
  impact_count: number | null
  open_impact_count: number | null
}

export interface CaseImpactResponse {
  id: string
  organization_id: string
  regulatory_change_id: string
  regulatory_change_title: string | null
  regulatory_change_severity: RegulatoryChangeSeverity | null
  case_id: string
  case_title: string | null
  case_status: string | null
  match_reason: string
  affected_sections: string[]
  status: CaseImpactStatus
  resolved_by: string | null
  resolver_name: string | null
  resolved_at: string | null
  resolution_note: string | null
  created_at: string
  updated_at: string
}

export interface ScanResult {
  regulatory_change_id: string
  new_impacts: number
  skipped_existing: number
  total_matched_cases: number
  impacts: CaseImpactResponse[]
}

export interface ComplianceHealthResponse {
  total_active_cases: number
  cases_with_open_impacts: number
  total_open_impacts: number
  impacts_by_severity: Record<string, number>
  recent_changes: RegulatoryChangeResponse[]
}

export interface RegulatoryChangeCreateInput {
  title: string
  description: string
  source: string
  source_url?: string | null
  severity: RegulatoryChangeSeverity
  affected_case_types?: string[]
  affected_agreements?: string[]
  affected_tags?: string[]
  knowledge_item_id?: string | null
  published_at?: string | null
}

export function useRegulatoryChanges(filters?: Record<string, string>) {
  const params = new URLSearchParams()
  if (filters) {
    for (const [key, value] of Object.entries(filters)) {
      if (value) params.set(key, value)
    }
  }
  const qs = params.toString()
  return useQuery({
    queryKey: ["regulatory-changes", filters ?? {}],
    queryFn: () =>
      apiFetch<RegulatoryChangeResponse[]>(
        qs ? `/regulatory-changes?${qs}` : "/regulatory-changes",
      ),
  })
}

export function useRegulatoryChange(id: string | undefined) {
  return useQuery({
    queryKey: ["regulatory-changes", id],
    queryFn: () =>
      apiFetch<RegulatoryChangeResponse>(`/regulatory-changes/${id}`),
    enabled: !!id,
  })
}

export function useCreateRegulatoryChange() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: RegulatoryChangeCreateInput) =>
      apiFetch<RegulatoryChangeResponse>("/regulatory-changes", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["regulatory-changes"] })
      queryClient.invalidateQueries({ queryKey: ["compliance-health"] })
    },
  })
}

export function useScanRegulatoryChange() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (changeId: string) =>
      apiFetch<ScanResult>(`/regulatory-changes/${changeId}/scan`, {
        method: "POST",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["regulatory-changes"] })
      queryClient.invalidateQueries({ queryKey: ["case-impacts"] })
      queryClient.invalidateQueries({ queryKey: ["compliance-health"] })
    },
  })
}

export function useDeleteRegulatoryChange() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (changeId: string) =>
      apiFetch<void>(`/regulatory-changes/${changeId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["regulatory-changes"] })
      queryClient.invalidateQueries({ queryKey: ["compliance-health"] })
    },
  })
}

export function useCaseImpacts(caseId: string | undefined) {
  return useQuery({
    queryKey: ["case-impacts", caseId],
    queryFn: () =>
      apiFetch<CaseImpactResponse[]>(`/cases/${caseId}/impacts`),
    enabled: !!caseId,
  })
}

export function useResolveCaseImpact() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      impactId,
      resolutionNote,
    }: {
      impactId: string
      resolutionNote?: string
    }) =>
      apiFetch<CaseImpactResponse>(
        `/regulatory-changes/case-impacts/${impactId}/resolve`,
        {
          method: "PATCH",
          body: JSON.stringify({ resolution_note: resolutionNote ?? null }),
        },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["regulatory-changes"] })
      queryClient.invalidateQueries({ queryKey: ["case-impacts"] })
      queryClient.invalidateQueries({ queryKey: ["compliance-health"] })
    },
  })
}

export function useAcknowledgeCaseImpact() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (impactId: string) =>
      apiFetch<CaseImpactResponse>(
        `/regulatory-changes/case-impacts/${impactId}/acknowledge`,
        { method: "PATCH" },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["regulatory-changes"] })
      queryClient.invalidateQueries({ queryKey: ["case-impacts"] })
      queryClient.invalidateQueries({ queryKey: ["compliance-health"] })
    },
  })
}

export function useMarkImpactNotApplicable() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      impactId,
      resolutionNote,
    }: {
      impactId: string
      resolutionNote?: string
    }) =>
      apiFetch<CaseImpactResponse>(
        `/regulatory-changes/case-impacts/${impactId}/not-applicable`,
        {
          method: "PATCH",
          body: JSON.stringify({ resolution_note: resolutionNote ?? null }),
        },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["regulatory-changes"] })
      queryClient.invalidateQueries({ queryKey: ["case-impacts"] })
      queryClient.invalidateQueries({ queryKey: ["compliance-health"] })
    },
  })
}

export function useComplianceHealth() {
  return useQuery({
    queryKey: ["compliance-health"],
    queryFn: () =>
      apiFetch<ComplianceHealthResponse>("/dashboard/compliance-health"),
  })
}
