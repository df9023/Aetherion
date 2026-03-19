export const mockUsers: Record<string, { id: string; name: string; role: string }> = {
  "user-1": { id: "user-1", name: "Erik Eriksson", role: "advisor" },
  "user-2": { id: "user-2", name: "Maria Lindqvist", role: "advisor" },
}

export const mockClients = [
  {
    id: "client-1",
    name: "Anna Johansson",
    date_of_birth: "1980-03-15",
    employment_status: "employed" as const,
    employer_name: "Volvo",
    collective_agreement: "ITP1",
    annual_income: "684000",
    desired_retirement_age: 65,
    risk_profile: "moderate" as const,
    organization_id: "org-1",
    created_at: "2026-03-10T08:00:00Z",
    updated_at: "2026-03-10T08:00:00Z",
    created_by: "user-1",
  },
  {
    id: "client-2",
    name: "Lars Pettersson",
    date_of_birth: "1968-07-22",
    employment_status: "employed" as const,
    employer_name: "Ericsson",
    collective_agreement: "ITP2",
    annual_income: "960000",
    desired_retirement_age: 63,
    risk_profile: "low" as const,
    organization_id: "org-1",
    created_at: "2026-03-10T08:00:00Z",
    updated_at: "2026-03-10T08:00:00Z",
    created_by: "user-2",
  },
]

export const mockCases = [
  {
    id: "case-1",
    title: "Anna Johansson — Retirement Planning",
    case_type: "retirement_planning" as const,
    status: "in_preparation" as const,
    summary: "ITP1 pension review and withdrawal strategy for client approaching retirement",
    meeting_date: "2026-04-15T10:00:00Z",
    client_id: "client-1",
    assigned_to: "user-1",
    organization_id: "org-1",
    created_at: new Date(Date.now() - 2 * 86400000).toISOString(),
    updated_at: new Date().toISOString(),
    completed_at: null,
  },
  {
    id: "case-2",
    title: "Lars Pettersson — Salary Exchange",
    case_type: "salary_exchange" as const,
    status: "draft" as const,
    summary: "Löneväxling analysis for ITP2 client at Ericsson",
    meeting_date: null,
    client_id: "client-2",
    assigned_to: "user-2",
    organization_id: "org-1",
    created_at: new Date(Date.now() - 5 * 86400000).toISOString(),
    updated_at: new Date().toISOString(),
    completed_at: null,
  },
]

export const mockRecommendation = {
  id: "rec-1",
  case_id: "case-1",
  version: 1,
  status: "draft" as const,
  recommendation_type: "withdrawal_plan" as const,
  suitability_score: "8.5",
  summary:
    "Based on Anna's ITP1 pension through Volvo, moderate risk profile, and desired retirement age of 65, we recommend a phased withdrawal strategy combining her occupational pension with the general pension. The analysis considers current fund allocation, projected returns under multiple scenarios, and tax optimization opportunities through strategic withdrawal timing.",
  reasoning_chain: [
    {
      step: 1,
      description: "Analyzed client's current ITP1 pension holdings and projected value at retirement age 65",
      conclusion: "Current trajectory yields approximately 2.1M SEK in occupational pension at retirement",
      evidence_ids: ["ev-1"],
    },
    {
      step: 2,
      description: "Evaluated risk profile alignment with current fund allocation",
      conclusion: "Moderate risk profile is well-matched with current 60/40 equity-bond allocation",
      evidence_ids: ["ev-2"],
    },
    {
      step: 3,
      description: "Modeled withdrawal scenarios considering tax brackets and general pension coordination",
      conclusion: "Phased 5-year withdrawal starting at 65 optimizes tax efficiency",
      evidence_ids: ["ev-3"],
    },
    {
      step: 4,
      description: "Assessed survivor protection needs based on family situation",
      conclusion: "Current survivor protection level is adequate, no changes recommended",
      evidence_ids: [],
    },
    {
      step: 5,
      description: "Reviewed applicable product rules and regulatory requirements for ITP1 withdrawals",
      conclusion: "All recommendations comply with ITP1 product rules and IDD requirements",
      evidence_ids: ["ev-1", "ev-4"],
    },
  ],
  assumptions: [
    {
      assumption: "Client will retire at age 65 as planned",
      basis: "Client confirmed desired retirement age during advisory meeting",
      impact_if_wrong: "Earlier retirement would reduce projected pension capital by ~8% per year brought forward",
    },
    {
      assumption: "Current employer contributions continue at present level",
      basis: "Volvo's ITP1 agreement terms and client's employment status",
      impact_if_wrong: "Job change or salary reduction would lower projected pension by 10-20%",
    },
    {
      assumption: "Average annual return of 6% on current fund allocation",
      basis: "Historical 10-year return for similar moderate-risk portfolios",
      impact_if_wrong: "A 2% lower return would reduce final capital by approximately 350K SEK",
    },
  ],
  scenarios: [
    {
      name: "Base Case",
      description: "Retirement at 65, current allocation maintained",
      projected_outcome: { "Monthly pension": "18 500 kr", "Total capital at 65": "2.1M SEK", "Tax rate": "~32%" },
    },
    {
      name: "Early Retirement (63)",
      description: "Retirement 2 years early with reduced capital",
      projected_outcome: { "Monthly pension": "15 800 kr", "Total capital at 63": "1.8M SEK", "Tax rate": "~30%" },
    },
    {
      name: "Optimized Withdrawal",
      description: "Phased 5-year withdrawal with tax optimization",
      projected_outcome: { "Monthly pension": "19 200 kr", "Effective tax rate": "~28%", "Tax savings": "~85K SEK" },
    },
  ],
  created_at: "2026-03-16T09:15:00Z",
  created_by: "user-1",
  approved_by: null,
}

export const mockEvidence = [
  {
    id: "ev-1",
    recommendation_id: "rec-1",
    source_type: "product_rule" as const,
    source_reference: "ITP1 Product Rules 2024",
    content_snippet:
      "ITP1 pension benefits are calculated based on final salary and years of service. Withdrawal can commence from age 55 with actuarial reduction.",
    relevance_explanation: "Defines withdrawal rules applicable to client",
    confidence: "0.95",
    created_at: "2026-03-16T09:15:00Z",
  },
  {
    id: "ev-2",
    recommendation_id: "rec-1",
    source_type: "internal_policy" as const,
    source_reference: "Risk Profile Assessment Playbook",
    content_snippet:
      "Moderate risk profile clients should maintain 50-70% equity allocation with gradual de-risking starting 5 years before planned retirement.",
    relevance_explanation: "Guides fund allocation recommendation",
    confidence: "0.88",
    created_at: "2026-03-16T09:15:00Z",
  },
  {
    id: "ev-3",
    recommendation_id: "rec-1",
    source_type: "regulation" as const,
    source_reference: "IDD Regulatory Requirements",
    content_snippet:
      "Advisors must demonstrate that recommended products and withdrawal strategies are suitable given the client's financial situation, knowledge, and objectives.",
    relevance_explanation: "Compliance framework for suitability assessment",
    confidence: "0.92",
    created_at: "2026-03-16T09:15:00Z",
  },
  {
    id: "ev-4",
    recommendation_id: "rec-1",
    source_type: "regulation" as const,
    source_reference: "Pension Withdrawal Rules — Skatteverket",
    content_snippet:
      "Occupational pension withdrawals are taxed as employment income. Phased withdrawals over minimum 5 years can optimize tax bracket utilization.",
    relevance_explanation: "Tax optimization basis for withdrawal timing",
    confidence: "0.90",
    created_at: "2026-03-16T09:15:00Z",
  },
]

export const mockKnowledge = [
  {
    id: "k-1",
    title: "ITP1 Product Rules & Fund Selection",
    category: "product_rule" as const,
    source: "Collectum Product Guide 2024",
    tags: ["ITP1", "funds", "withdrawal", "collectum"],
    content:
      "ITP1 is a defined-contribution occupational pension plan managed through Collectum. The employee selects fund allocation from approved providers. Key withdrawal rules: benefits can be drawn from age 55 with actuarial reduction, standard retirement age is 65. Fund selection options include traditional insurance and unit-linked (fondförsäkring). Transfer rights exist between approved providers with restrictions on traditional insurance policies.",
    effective_date: "2024-01-01",
    is_active: true,
  },
  {
    id: "k-2",
    title: "ITP2 Traditional & ITPK Rules",
    category: "product_rule" as const,
    source: "Alecta/Collectum Handbook",
    tags: ["ITP2", "traditional", "ITPK", "defined-benefit"],
    content:
      "ITP2 consists of a defined-benefit base pension (managed by Alecta) and a supplementary ITPK component (employee-directed). The DB base provides approximately 10% of salary between 7.5-20 income base amounts and 65% between 20-30 IBB. ITPK premiums are 2% of pensionable salary.",
    effective_date: "2024-01-01",
    is_active: true,
  },
  {
    id: "k-3",
    title: "Löneväxling Internal Policy",
    category: "internal_policy" as const,
    source: "SPP Advisory Handbook",
    tags: ["salary exchange", "löneväxling", "policy"],
    content:
      'Salary exchange (löneväxling) allows employees to convert gross salary into additional pension contributions. Our advisory guidelines: minimum income threshold of 40,000 kr/month before recommending löneväxling, always assess impact on sjukpenning/föräldrapenning.',
    effective_date: "2023-06-15",
    is_active: true,
  },
  {
    id: "k-4",
    title: "IDD Regulatory Requirements",
    category: "regulatory_requirement" as const,
    source: "Finansinspektionen FFFS 2018:10",
    tags: ["IDD", "compliance", "suitability"],
    content:
      "The Insurance Distribution Directive (IDD) requires advisors to: conduct a demands-and-needs analysis, assess suitability based on client's knowledge, financial situation, and objectives, disclose all costs and fees in standardized format, identify and manage conflicts of interest.",
    effective_date: "2018-10-01",
    is_active: true,
  },
  {
    id: "k-5",
    title: "Risk Profile Assessment Playbook",
    category: "playbook" as const,
    source: "SPP Internal",
    tags: ["risk", "assessment", "methodology"],
    content:
      "Risk profiling methodology: Use structured questionnaire covering investment horizon, loss tolerance, income stability, and experience. Map to three-tier scale (Low/Moderate/High). Review risk profile annually and at major life events.",
    effective_date: "2023-01-01",
    is_active: true,
  },
  {
    id: "k-6",
    title: "Pension Withdrawal Rules & Tax Optimization",
    category: "regulatory_requirement" as const,
    source: "Skatteverket Guidelines",
    tags: ["withdrawal", "tax", "optimization"],
    content:
      "Occupational pension can generally be withdrawn from age 55. General pension available from age 63. Withdrawals taxed as employment income. Key optimization: phased withdrawals over 5+ years can reduce marginal tax rate.",
    effective_date: "2024-01-01",
    is_active: true,
  },
]

export const mockAudit = [
  {
    id: "a-1",
    case_id: "case-1",
    action: "case_created",
    actor_id: "user-1",
    actor_type: "user" as const,
    details: { case_type: "retirement_planning" },
    timestamp: "2026-03-16T09:00:00Z",
  },
  {
    id: "a-2",
    case_id: "case-1",
    action: "recommendation_generated",
    actor_id: "system",
    actor_type: "system" as const,
    details: { version: 1, recommendation_type: "withdrawal_plan" },
    timestamp: "2026-03-16T09:15:00Z",
  },
]

// Helper maps
export const caseTypeLabels: Record<string, string> = {
  pension_review: "Pension Review",
  retirement_planning: "Retirement Planning",
  salary_exchange: "Salary Exchange",
  transfer_advice: "Transfer Advice",
  survivor_protection: "Survivor Protection",
  decumulation: "Decumulation",
  other: "Other",
}

export const statusStyles: Record<string, string> = {
  draft: "bg-slate-100 text-slate-600",
  in_preparation: "bg-blue-50 text-blue-700 border border-blue-200",
  ready_for_review: "bg-amber-50 text-amber-700 border border-amber-200",
  in_review: "bg-purple-50 text-purple-700 border border-purple-200",
  approved: "bg-emerald-50 text-emerald-700 border border-emerald-200",
  completed: "bg-green-50 text-green-800 border border-green-200",
  archived: "bg-slate-50 text-slate-400",
}

export const statusLabels: Record<string, string> = {
  draft: "Draft",
  in_preparation: "In Preparation",
  ready_for_review: "Ready for Review",
  in_review: "In Review",
  approved: "Approved",
  completed: "Completed",
  archived: "Archived",
}

export const categoryStyles: Record<string, string> = {
  product_rule: "bg-blue-50 text-blue-700",
  internal_policy: "bg-violet-50 text-violet-700",
  regulatory_requirement: "bg-amber-50 text-amber-700",
  playbook: "bg-emerald-50 text-emerald-700",
  precedent: "bg-slate-100 text-slate-600",
  faq: "bg-sky-50 text-sky-700",
  process_guide: "bg-rose-50 text-rose-700",
}

export const categoryLabels: Record<string, string> = {
  product_rule: "Product Rule",
  internal_policy: "Internal Policy",
  regulatory_requirement: "Regulatory",
  playbook: "Playbook",
  precedent: "Precedent",
  faq: "FAQ",
  process_guide: "Process Guide",
}

export const sourceTypeStyles: Record<string, string> = {
  product_rule: "bg-blue-50 text-blue-700",
  internal_policy: "bg-violet-50 text-violet-700",
  regulation: "bg-amber-50 text-amber-700",
}
