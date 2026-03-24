"use client"

import { useState } from "react"
import Link from "next/link"
import { Plus, Search, Building2, Shield, Users } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useClients } from "@/lib/hooks"
import { CreateClientDialog } from "@/components/create-client-dialog"
import { TopBar } from "@/components/top-bar"

function calculateAge(dob: string) {
  const birth = new Date(dob)
  const now = new Date()
  let age = now.getFullYear() - birth.getFullYear()
  if (now.getMonth() < birth.getMonth() || (now.getMonth() === birth.getMonth() && now.getDate() < birth.getDate())) {
    age--
  }
  return age
}

function formatCurrency(amount: string) {
  return new Intl.NumberFormat("sv-SE").format(Math.round(Number(amount) / 12)) + " kr/mo"
}

const riskColors: Record<string, { bg: string; text: string }> = {
  low: { bg: "bg-green-50", text: "text-green-700" },
  moderate: { bg: "bg-amber-50", text: "text-amber-700" },
  high: { bg: "bg-red-50", text: "text-red-700" },
}

const riskLabels: Record<string, string> = {
  low: "Low",
  moderate: "Moderate",
  high: "High",
}

export default function ClientsPage() {
  const { data: clients, isLoading } = useClients()
  const [search, setSearch] = useState("")
  const [openCreateDialog, setOpenCreateDialog] = useState(false)

  const filtered = (clients ?? []).filter(
    (c) =>
      !search ||
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      (c.employer_name ?? "").toLowerCase().includes(search.toLowerCase())
  )

  return (
    <>
      <CreateClientDialog open={openCreateDialog} onOpenChange={setOpenCreateDialog} />
      <TopBar breadcrumbs={[{ label: "Clients" }]} />
      <main className="flex-1 bg-slate-50">
        <div className="mx-auto max-w-7xl px-6 py-8">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <h1 className="text-2xl font-semibold text-slate-900">Clients</h1>
            <Button
              onClick={() => setOpenCreateDialog(true)}
              className="gap-2 bg-sky-500 text-white hover:bg-sky-600"
            >
              <Plus className="h-4 w-4" />
              New Client
            </Button>
          </div>

          {/* Search */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search clients..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-white border-slate-200/60 pl-10"
                data-search-input
              />
            </div>
          </div>

          {/* Loading skeletons */}
          {isLoading && (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <Skeleton className="mt-3 h-4 w-3/4" />
                  <Skeleton className="mt-2 h-3 w-1/2" />
                </div>
              ))}
            </div>
          )}

          {/* Client cards grid */}
          {!isLoading && filtered.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filtered.map((client) => {
                const riskColor = riskColors[client.risk_profile ?? ""]
                const initials = client.name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")

                return (
                  <Link key={client.id} href={`/clients/${client.id}`} className="block">
                    <div className="h-full rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm transition-all duration-200 hover:border-l-4 hover:border-l-sky-400">
                      {/* Initials avatar */}
                      <div className="mb-3 flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100">
                          <span className="text-sm font-medium text-slate-600">{initials}</span>
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-semibold text-slate-900">{client.name}</p>
                          <p className="text-xs text-slate-400">{calculateAge(client.date_of_birth)} years</p>
                        </div>
                      </div>

                      {/* Employer */}
                      <div className="mb-3 flex items-center gap-2">
                        <Building2 className="h-4 w-4 shrink-0 text-slate-400" />
                        <p className="truncate text-sm text-slate-600">{client.employer_name ?? "—"}</p>
                      </div>

                      {/* Income */}
                      <div className="mb-3">
                        <p className="text-sm text-slate-600">
                          {client.annual_income ? formatCurrency(client.annual_income) : "—"}
                        </p>
                      </div>

                      {/* Risk profile badge */}
                      {client.risk_profile && riskColor ? (
                        <div className="flex items-center gap-2">
                          <Shield className="h-4 w-4 shrink-0 text-slate-400" />
                          <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${riskColor.bg} ${riskColor.text}`}>
                            {riskLabels[client.risk_profile] ?? client.risk_profile}
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <Shield className="h-4 w-4 shrink-0 text-slate-400" />
                          <span className="text-xs text-slate-400">—</span>
                        </div>
                      )}
                    </div>
                  </Link>
                )
              })}
            </div>
          ) : (
            !isLoading && (
              <div className="flex flex-col items-center justify-center py-12">
                <Users className="mb-3 h-12 w-12 text-slate-300" />
                <p className="mb-1 font-medium text-slate-600">No clients found</p>
                <p className="mb-4 text-sm text-slate-400">
                  Create your first client to get started
                </p>
                <Button
                  onClick={() => setOpenCreateDialog(true)}
                  className="gap-2 bg-sky-500 text-white hover:bg-sky-600"
                >
                  <Plus className="h-4 w-4" />
                  New Client
                </Button>
              </div>
            )
          )}
        </div>
      </main>
    </>
  )
}
