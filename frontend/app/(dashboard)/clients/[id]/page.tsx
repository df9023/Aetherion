"use client"

import { use } from "react"
import { Plus, Upload } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { useClient, useClientCases } from "@/lib/hooks"
import { TopBar } from "@/components/top-bar"
import { ClientHeaderCard } from "@/components/client-header-card"
import { ClientDetailsCard } from "@/components/client-details-card"
import { LinkedCasesCard } from "@/components/linked-cases-card"
import { DocumentIngestion } from "@/components/document-ingestion"
import { CreateCaseDialog } from "@/components/create-case-dialog"

export default function ClientDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const { data: client, isLoading } = useClient(id)
  const { data: cases, isLoading: casesLoading } = useClientCases(id)

  if (isLoading) {
    return (
      <>
        <TopBar breadcrumbs={[{ label: "Clients", href: "/clients" }, { label: "Loading..." }]} />
        <main className="flex-1 bg-slate-50">
          <div className="mx-auto max-w-7xl px-6 py-8">
            <div className="space-y-6">
              <Skeleton className="h-32 rounded-xl" />
              <Skeleton className="h-60 rounded-xl" />
              <Skeleton className="h-40 rounded-xl" />
            </div>
          </div>
        </main>
      </>
    )
  }

  if (!client) {
    return (
      <>
        <TopBar breadcrumbs={[{ label: "Clients", href: "/clients" }, { label: "Not Found" }]} />
        <main className="flex-1 bg-slate-50">
          <div className="py-12 text-center text-slate-400">Client not found</div>
        </main>
      </>
    )
  }

  return (
    <>
      <TopBar breadcrumbs={[{ label: "Clients", href: "/clients" }, { label: client.name }]} />
      <main className="flex-1 bg-slate-50">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Left column */}
            <div className="space-y-6 lg:col-span-2">
              <ClientHeaderCard client={client} />
              <ClientDetailsCard client={client} />

              {/* Document Ingestion */}
              <div className="rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm">
                <div className="mb-6 flex items-center gap-2">
                  <Upload className="h-5 w-5 text-slate-600" />
                  <h3 className="text-base font-semibold text-slate-900">Document Ingestion</h3>
                </div>
                <DocumentIngestion clientId={id} client={client} />
              </div>
            </div>

            {/* Right column */}
            <div className="space-y-6">
              <LinkedCasesCard
                cases={cases ?? []}
                isLoading={casesLoading}
                createCaseButton={
                  <CreateCaseDialog
                    defaultClientId={id}
                    trigger={
                      <Button variant="outline" size="sm" className="h-8 gap-1 border-slate-200 text-slate-700">
                        <Plus className="h-3 w-3" />
                        New Case
                      </Button>
                    }
                  />
                }
              />
            </div>
          </div>
        </div>
      </main>
    </>
  )
}
