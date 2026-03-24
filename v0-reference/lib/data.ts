export type CaseStatus =
  | 'draft'
  | 'in_preparation'
  | 'ready_for_review'
  | 'in_review'
  | 'approved'
  | 'completed'

export type CaseType =
  | 'Retirement Planning'
  | 'Salary Exchange'
  | 'Pension Review'
  | 'Survivor Protection'

export interface Case {
  id: string
  title: string
  type: CaseType
  status: CaseStatus
  summary: string
  advisor: string
  updated: string
}

export const cases: Case[] = [
  {
    id: 'cs1',
    title: 'Pensionsöversikt och placeringsrådgivning — Anna Johansson',
    type: 'Retirement Planning',
    status: 'in_preparation',
    summary: 'Anna, 45 år, ITP1 via Volvo. Vill se över sin tjänstepension.',
    advisor: 'Maria Lindqvist',
    updated: 'Yesterday',
  },
  {
    id: 'cs2',
    title: 'Löneväxlingsanalys — Lars Pettersson',
    type: 'Salary Exchange',
    status: 'in_preparation',
    summary: 'Lars, 58 år, ITP2 via Ericsson. Hög lön, vill utreda löneväxling.',
    advisor: 'Maria Lindqvist',
    updated: '2 days ago',
  },
  {
    id: 'cs3',
    title: 'Fondval och avgiftsöversyn — Anna Johansson',
    type: 'Pension Review',
    status: 'ready_for_review',
    summary: 'Uppföljning av Annas fondval hos Collectum.',
    advisor: 'Erik Eriksson',
    updated: 'Today',
  },
  {
    id: 'cs4',
    title: 'Familjeskydd — Lars Pettersson',
    type: 'Survivor Protection',
    status: 'draft',
    summary: 'Översyn av Lars familjeskydd.',
    advisor: 'Erik Eriksson',
    updated: '3 days ago',
  },
]

export const statusConfig: Record<
  CaseStatus,
  { label: string; color: string; progress: number; progressColor: string }
> = {
  draft: {
    label: 'Draft',
    color: 'bg-slate-100 text-slate-600',
    progress: 15,
    progressColor: 'bg-slate-400',
  },
  in_preparation: {
    label: 'In Preparation',
    color: 'bg-blue-50 text-blue-700',
    progress: 30,
    progressColor: 'bg-blue-500',
  },
  ready_for_review: {
    label: 'Ready for Review',
    color: 'bg-amber-50 text-amber-700',
    progress: 50,
    progressColor: 'bg-amber-500',
  },
  in_review: {
    label: 'In Review',
    color: 'bg-purple-50 text-purple-700',
    progress: 70,
    progressColor: 'bg-purple-500',
  },
  approved: {
    label: 'Approved',
    color: 'bg-emerald-50 text-emerald-700',
    progress: 85,
    progressColor: 'bg-emerald-500',
  },
  completed: {
    label: 'Completed',
    color: 'bg-green-50 text-green-700',
    progress: 100,
    progressColor: 'bg-green-500',
  },
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

export type RiskProfile = 'low' | 'moderate' | 'high'
export type EmploymentStatus = 'employed' | 'unemployed' | 'retired'
export type KnowledgeCategory =
  | 'product_rule'
  | 'internal_policy'
  | 'regulatory'
  | 'playbook'
  | 'precedent'
  | 'faq'
  | 'process_guide'

export interface Client {
  id: string
  name: string
  dob: string
  age: number
  employer: string
  agreement: string
  annualIncome: number
  monthlyIncome: number
  retirementAge: number
  risk: RiskProfile
  status: EmploymentStatus
}

export interface KnowledgeItem {
  title: string
  category: KnowledgeCategory
  source: string
  tags: string[]
  content: string
}

export const clients: Client[] = [
  {
    id: 'c1',
    name: 'Anna Johansson',
    dob: '1981-03-15',
    age: 45,
    employer: 'Volvo Group AB',
    agreement: 'ITP1',
    annualIncome: 684000,
    monthlyIncome: 57000,
    retirementAge: 65,
    risk: 'moderate',
    status: 'employed',
  },
  {
    id: 'c2',
    name: 'Lars Pettersson',
    dob: '1968-08-22',
    age: 58,
    employer: 'Ericsson AB',
    agreement: 'ITP2',
    annualIncome: 960000,
    monthlyIncome: 80000,
    retirementAge: 63,
    risk: 'low',
    status: 'employed',
  },
  {
    id: 'c3',
    name: 'Karin Svensson',
    dob: '1975-11-08',
    age: 49,
    employer: 'Swedbank AB',
    agreement: 'ITP1',
    annualIncome: 820000,
    monthlyIncome: 68333,
    retirementAge: 66,
    risk: 'moderate',
    status: 'employed',
  },
  {
    id: 'c4',
    name: 'Johan Berg',
    dob: '1962-06-20',
    age: 63,
    employer: 'Skanska AB',
    agreement: 'ITP2',
    annualIncome: 1200000,
    monthlyIncome: 100000,
    retirementAge: 63,
    risk: 'low',
    status: 'employed',
  },
  {
    id: 'c5',
    name: 'Maria Lundgren',
    dob: '1990-01-12',
    age: 34,
    employer: 'H&M Hennes & Mauritz AB',
    agreement: 'ITP1',
    annualIncome: 520000,
    monthlyIncome: 43333,
    retirementAge: 67,
    risk: 'high',
    status: 'employed',
  },
]

export const knowledge: KnowledgeItem[] = [
  {
    title: 'ITP1 — Premiebestämd tjänstepension',
    category: 'product_rule',
    source: 'Collectum — ITP1-avtalet 2024',
    tags: ['ITP1', 'premiebestämd', 'collectum'],
    content:
      'ITP1 gäller för anställda födda 1979 eller senare. Premien baseras på lönen och betalas av arbetsgivaren. Den anställde väljer själv hur premierna placeras bland de valbara fonderna hos Collectum.',
  },
  {
    title: 'ITP2 — Förmånsbestämd tjänstepension',
    category: 'product_rule',
    source: 'Collectum — ITP2-avtalet 2024',
    tags: ['ITP2', 'förmånsbestämd', 'alecta'],
    content:
      'ITP2 gäller för anställda födda 1978 eller tidigare. Pensionen baseras på slutlönen och intjänandetiden. Grundtryggheten hanteras av Alecta.',
  },
  {
    title: 'Löneväxling — regler och förutsättningar',
    category: 'internal_policy',
    source: 'SPP — Intern policy 2024',
    tags: ['löneväxling', 'salary_exchange'],
    content:
      'Löneväxling innebär att den anställde avstår en del av sin bruttolön mot en extra pensionsavsättning. Villkor: lön efter växling får inte understiga gränsen för sjukpenninggrundande inkomst.',
  },
  {
    title: 'IDD — Krav på behovsanalys',
    category: 'regulatory',
    source: 'Finansinspektionen — FFFS 2018:10',
    tags: ['IDD', 'compliance', 'FI'],
    content:
      'Enligt IDD ska en behovsanalys genomföras innan rådgivning lämnas. Analysen ska dokumenteras och innehålla kundens ekonomiska situation, mål, riskvilja och kunskapsnivå.',
  },
  {
    title: 'Riskprofiler — bedömning och rekommendation',
    category: 'playbook',
    source: 'SPP — Riskprofilsguide v3',
    tags: ['riskprofil', 'rådgivning'],
    content:
      'Riskprofilen bestäms genom en kombination av kundens tidshorisont, ekonomiska situation och subjektiva riskvilja. Tre nivåer: låg, moderat, hög.',
  },
  {
    title: 'Pensionsålder och uttag — regler 2024',
    category: 'regulatory',
    source: 'Pensionsmyndigheten / SKV',
    tags: ['pensionsålder', 'uttag'],
    content:
      'Tidigaste uttag av allmän pension: 63 år (höjs till 64 år 2026). Tjänstepension kan vanligtvis tas ut från 55 år. Privat pension från 55 år.',
  },
  {
    title: 'Fonder hos Collectum — valbara alternativ',
    category: 'process_guide',
    source: 'Collectum — Fondutbud 2024',
    tags: ['collectum', 'fonder', 'val'],
    content:
      'Collectum erbjuder över 100 valbara fonder. De populäraste är Handelsbanken Norden, SEB Sverige och AMF Räntefond. Avgifterna varierar mellan 0,1% och 0,5%.',
  },
  {
    title: 'Precedent: Löneväxling för tjänstemän',
    category: 'precedent',
    source: 'Intern fallsamling — 2024',
    tags: ['löneväxling', 'precedent', 'tjänstemän'],
    content:
      'Två tidigare klienter i liknande situationer (höga inkomster, ITP1) genomförde löneväxling med goda resultat för pensionssparandet.',
  },
]

export function getCategoryLabel(category: KnowledgeCategory): string {
  const labels: Record<KnowledgeCategory, string> = {
    product_rule: 'Product Rule',
    internal_policy: 'Internal Policy',
    regulatory: 'Regulatory',
    playbook: 'Playbook',
    precedent: 'Precedent',
    faq: 'FAQ',
    process_guide: 'Process Guide',
  }
  return labels[category]
}

export function getCategoryColor(
  category: KnowledgeCategory
): { bg: string; text: string } {
  const colors: Record<KnowledgeCategory, { bg: string; text: string }> = {
    product_rule: { bg: 'bg-blue-50', text: 'text-blue-700' },
    internal_policy: { bg: 'bg-violet-50', text: 'text-violet-700' },
    regulatory: { bg: 'bg-amber-50', text: 'text-amber-700' },
    playbook: { bg: 'bg-emerald-50', text: 'text-emerald-700' },
    precedent: { bg: 'bg-cyan-50', text: 'text-cyan-700' },
    faq: { bg: 'bg-pink-50', text: 'text-pink-700' },
    process_guide: { bg: 'bg-indigo-50', text: 'text-indigo-700' },
  }
  return colors[category]
}

export function getRiskColor(
  risk: RiskProfile
): { bg: string; text: string } {
  const colors: Record<RiskProfile, { bg: string; text: string }> = {
    low: { bg: 'bg-emerald-50', text: 'text-emerald-700' },
    moderate: { bg: 'bg-amber-50', text: 'text-amber-700' },
    high: { bg: 'bg-red-50', text: 'text-red-700' },
  }
  return colors[risk]
}

export function getClientCases(clientId: string): typeof cases {
  // Return cases linked to this client based on name
  return cases.filter((c) => {
    const clientName = clients.find((cl) => cl.id === clientId)?.name
    return c.summary.includes(clientName || '')
  })
}
