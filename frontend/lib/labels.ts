export const caseTypeLabels: Record<string, string> = {
  pension_review: "Pensionsöversyn",
  retirement_planning: "Pensionsplanering",
  salary_exchange: "Löneväxling",
  transfer_advice: "Flyttrådgivning",
  survivor_protection: "Efterlevandeskydd",
  decumulation: "Uttagsplanering",
  other: "Övrigt",
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
  draft: "Utkast",
  in_preparation: "Under arbete",
  ready_for_review: "Redo för granskning",
  in_review: "Granskas",
  approved: "Godkänd",
  completed: "Avslutad",
  archived: "Arkiverad",
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
  product_rule: "Produktregel",
  internal_policy: "Intern policy",
  regulatory_requirement: "Regulatoriskt krav",
  playbook: "Handbok",
  precedent: "Prejudikat",
  faq: "Vanliga frågor",
  process_guide: "Processguide",
}

export const sourceTypeStyles: Record<string, string> = {
  product_rule: "bg-blue-50 text-blue-700",
  internal_policy: "bg-violet-50 text-violet-700",
  regulation: "bg-amber-50 text-amber-700",
  market_data: "bg-emerald-50 text-emerald-700",
  client_data: "bg-sky-50 text-sky-700",
  precedent: "bg-slate-100 text-slate-600",
  expert_knowledge: "bg-rose-50 text-rose-700",
}

export const sourceTypeLabels: Record<string, string> = {
  product_rule: "Produktregel",
  internal_policy: "Intern policy",
  regulation: "Reglering",
  market_data: "Marknadsdata",
  client_data: "Klientdata",
  precedent: "Prejudikat",
  expert_knowledge: "Expertkunskap",
}

export const auditActionLabels: Record<string, string> = {
  case_created: "Ärende skapat",
  case_assigned: "Ärende tilldelat",
  recommendation_generated: "Rekommendation genererad av AI",
  recommendation_edited: "Rekommendation redigerad",
  recommendation_reviewed: "Rekommendation granskad",
  recommendation_approved: "Rekommendation godkänd",
  recommendation_rejected: "Rekommendation avslagen",
  document_generated: "Dokument genererat",
  compliance_check_passed: "Regelefterlevnad godkänd",
  compliance_check_failed: "Regelefterlevnad underkänd",
  case_completed: "Ärende avslutat",
  knowledge_referenced: "Kunskap refererad",
  workflow_step_completed: "Arbetsflödessteg slutfört",
  workflow_paused: "Arbetsflöde pausat",
  workflow_resumed: "Arbetsflöde återupptaget",
  meeting_brief_generated: "Mötesunderlag genererat av AI",
  document_ingested: "Dokument inhämtat av AI",
  client_data_applied: "Klientdata uppdaterad från dokument",
  knowledge_ingested: "Kunskapsdokument inhämtat",
}

export const severityLabels: Record<string, string> = {
  high: "Hög",
  medium: "Medel",
  low: "Låg",
}

export const agreementLabels: Record<string, string> = {
  ITP1: "ITP1",
  ITP2: "ITP2",
  SAF_LO: "SAF-LO",
  KAP_KL: "KAP-KL",
  AKAP_KL: "AKAP-KL",
  PA16: "PA16",
  other: "Övrigt",
  none: "Inget",
}

export const agreementStyles: Record<string, string> = {
  ITP1: "bg-blue-50 text-blue-700",
  ITP2: "bg-indigo-50 text-indigo-700",
  SAF_LO: "bg-emerald-50 text-emerald-700",
  KAP_KL: "bg-amber-50 text-amber-700",
  AKAP_KL: "bg-orange-50 text-orange-700",
  PA16: "bg-purple-50 text-purple-700",
  other: "bg-slate-100 text-slate-600",
  none: "bg-slate-50 text-slate-400",
}
