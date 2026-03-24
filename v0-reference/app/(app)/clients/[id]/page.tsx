'use client'

import { notFound } from 'next/navigation'
import { clients } from '@/lib/data'
import { Topbar } from '@/components/topbar'
import { ClientHeaderCard } from '@/components/client-header-card'
import { ClientDetailsCard } from '@/components/client-details-card'
import { DocumentIngestionCard } from '@/components/document-ingestion-card'
import { LinkedCasesCard } from '@/components/linked-cases-card'

interface Props {
  params: Promise<{ id: string }>
}

export default async function ClientDetailPage({ params }: Props) {
  const { id } = await params
  const client = clients.find((c) => c.id === id)

  if (!client) {
    notFound()
  }

  return (
    <>
      <Topbar breadcrumbs={[{ label: 'Clients', href: '/clients' }, { label: client.name }]} />
      <main className="flex-1 bg-slate-50">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left column */}
            <div className="lg:col-span-2 space-y-6">
              <ClientHeaderCard client={client} />
              <ClientDetailsCard client={client} />
              <DocumentIngestionCard />
            </div>

            {/* Right column */}
            <div className="space-y-6">
              <LinkedCasesCard clientName={client.name} />
            </div>
          </div>
        </div>
      </main>
    </>
  )
}
