import { notFound } from 'next/navigation'
import { cases } from '@/lib/data'
import { Topbar } from '@/components/topbar'
import { CaseHeaderCard } from '@/components/case-header-card'
import { MeetingPrepCard } from '@/components/meeting-prep-card'
import { ClientInfoCard } from '@/components/client-info-card'
import { AIRecommendationCard } from '@/components/ai-recommendation-card'
import { KnowledgeBaseCard } from '@/components/knowledge-base-card'
import { AuditTrailCard } from '@/components/audit-trail-card'

interface PageProps {
  params: Promise<{ id: string }>
}

export default async function CaseDetailPage({ params }: PageProps) {
  const { id } = await params
  const caseData = cases.find((c) => c.id === id)

  if (!caseData) notFound()

  return (
    <>
      <Topbar
        breadcrumbs={[
          { label: 'Cases', href: '/cases' },
          { label: caseData.title.length > 50 ? caseData.title.slice(0, 50) + '…' : caseData.title },
        ]}
      />
      <main className="flex flex-1 gap-5 px-6 py-6">
        {/* Left column */}
        <div className="flex min-w-0 flex-1 flex-col gap-5">
          <CaseHeaderCard caseData={caseData} />
          <MeetingPrepCard />
          <ClientInfoCard caseData={caseData} />
          <AIRecommendationCard />
        </div>

        {/* Right panel */}
        <div className="flex w-[380px] shrink-0 flex-col gap-5">
          <KnowledgeBaseCard />
          <AuditTrailCard />
        </div>
      </main>
    </>
  )
}
