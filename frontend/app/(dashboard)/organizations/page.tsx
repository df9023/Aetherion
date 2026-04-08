"use client"

import { useState } from "react"
import Link from "next/link"
import { Plus, Search, Building2, Users } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useClientOrganizations } from "@/lib/hooks"
import { TopBar } from "@/components/top-bar"
import { CreateClientOrgDialog } from "@/components/create-client-org-dialog"
import { agreementLabels, agreementStyles } from "@/lib/labels"

export default function OrganizationsPage() {
  const { data: orgs, isLoading } = useClientOrganizations()
  const [search, setSearch] = useState("")
  const [openCreateDialog, setOpenCreateDialog] = useState(false)

  const filtered = (orgs ?? []).filter(
    (o) =>
      !search ||
      o.name.toLowerCase().includes(search.toLowerCase()) ||
      (o.industry ?? "").toLowerCase().includes(search.toLowerCase())
  )

  return (
    <>
      <CreateClientOrgDialog open={openCreateDialog} onOpenChange={setOpenCreateDialog} />
      <TopBar breadcrumbs={[{ label: "Organisationer" }]} />
      <main className="flex-1 bg-slate-50">
        <div className="mx-auto max-w-7xl px-6 py-8">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <h1 className="text-xl font-semibold text-slate-900">Organisationer</h1>
            <Button
              onClick={() => setOpenCreateDialog(true)}
              className="gap-2 bg-sky-500 text-white hover:bg-sky-600"
            >
              <Plus className="h-4 w-4" />
              Ny organisation
            </Button>
          </div>

          {/* Search */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Sök organisationer..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-white border-slate-200/60 pl-10"
              />
            </div>
          </div>

          {/* Loading skeletons */}
          {isLoading && (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm">
                  <Skeleton className="h-5 w-3/4" />
                  <Skeleton className="mt-3 h-4 w-1/2" />
                  <Skeleton className="mt-2 h-3 w-1/3" />
                </div>
              ))}
            </div>
          )}

          {/* Organization cards grid */}
          {!isLoading && filtered.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filtered.map((org) => {
                const agreementStyle = agreementStyles[org.collective_agreement ?? ""] ?? "bg-slate-100 text-slate-600"

                return (
                  <Link key={org.id} href={`/organizations/${org.id}`} className="block">
                    <div className="h-full rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm transition-all duration-200 hover:border-l-4 hover:border-l-sky-400">
                      {/* Name */}
                      <div className="mb-3 flex items-center gap-3">
                        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-slate-100">
                          <Building2 className="h-5 w-5 text-slate-500" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-semibold text-slate-900">{org.name}</p>
                          {org.industry && (
                            <p className="text-sm text-slate-400">{org.industry}</p>
                          )}
                        </div>
                      </div>

                      {/* Agreement badge */}
                      {org.collective_agreement && (
                        <div className="mb-3">
                          <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${agreementStyle}`}>
                            {agreementLabels[org.collective_agreement] ?? org.collective_agreement}
                          </span>
                        </div>
                      )}

                      {/* Client count */}
                      <div className="mb-2 flex items-center gap-2">
                        <Users className="h-4 w-4 shrink-0 text-slate-400" />
                        <p className="text-sm text-slate-600">
                          {org.client_count} anställda i systemet
                        </p>
                      </div>

                      {/* Contact */}
                      {org.contact_person && (
                        <p className="text-sm text-slate-400">
                          Kontakt: {org.contact_person}
                        </p>
                      )}
                    </div>
                  </Link>
                )
              })}
            </div>
          ) : (
            !isLoading && (
              <div className="flex flex-col items-center justify-center py-12">
                <Building2 className="mb-3 h-12 w-12 text-slate-300" />
                <p className="mb-1 text-base font-medium text-slate-600">Inga organisationer ännu</p>
                <p className="mb-4 text-sm text-slate-400">
                  Skapa din första organisation för att komma igång
                </p>
                <Button
                  onClick={() => setOpenCreateDialog(true)}
                  className="gap-2 bg-sky-500 text-white hover:bg-sky-600"
                >
                  <Plus className="h-4 w-4" />
                  Ny organisation
                </Button>
              </div>
            )
          )}
        </div>
      </main>
    </>
  )
}
