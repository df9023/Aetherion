'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Plus, Search, Building2, Shield, Users } from 'lucide-react'
import { clients, getInitials, getRiskColor } from '@/lib/data'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Topbar } from '@/components/topbar'
import { CreateClientDialog } from '@/components/create-client-dialog'

export default function ClientsPage() {
  const [search, setSearch] = useState('')
  const [openCreateDialog, setOpenCreateDialog] = useState(false)

  const filtered = clients.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.employer.toLowerCase().includes(search.toLowerCase())
  )

  const riskLabels = { low: 'Low', moderate: 'Moderate', high: 'High' }

  return (
    <>
      <CreateClientDialog open={openCreateDialog} onOpenChange={setOpenCreateDialog} />
      <Topbar breadcrumbs={[{ label: 'Clients' }]} />
      <main className="flex-1 bg-slate-50">
        <div className="mx-auto max-w-7xl px-6 py-8">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <h1 className="text-2xl font-semibold text-slate-900">Clients</h1>
            <Button onClick={() => setOpenCreateDialog(true)} className="gap-2 bg-sky-500 hover:bg-sky-600 text-white">
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
                className="pl-10 bg-white border-slate-200/60"
              />
            </div>
          </div>

          {/* Client cards grid */}
          {filtered.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filtered.map((client) => {
                const riskColor = getRiskColor(client.risk)
                return (
                  <Link
                    key={client.id}
                    href={`/clients/${client.id}`}
                    className="block"
                  >
                    <div
                      className="rounded-xl border border-slate-200/60 bg-white shadow-sm p-5 
                      hover:border-l-4 hover:border-l-sky-400 transition-all duration-200 h-full"
                    >
                      {/* Initials avatar */}
                      <div className="mb-3 flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-slate-100 flex items-center justify-center">
                          <span className="text-sm font-medium text-slate-600">
                            {getInitials(client.name)}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-slate-900 truncate">
                            {client.name}
                          </p>
                          <p className="text-xs text-slate-400">
                            {client.age} years
                          </p>
                        </div>
                      </div>

                      {/* Employer */}
                      <div className="mb-3 flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-slate-400 flex-shrink-0" />
                        <p className="text-sm text-slate-600 truncate">
                          {client.employer}
                        </p>
                      </div>

                      {/* Income */}
                      <div className="mb-3">
                        <p className="text-sm text-slate-600">
                          {client.monthlyIncome.toLocaleString()} kr/month
                        </p>
                      </div>

                      {/* Risk profile badge */}
                      <div className="flex items-center gap-2">
                        <Shield className="h-4 w-4 text-slate-400 flex-shrink-0" />
                        <div
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${riskColor.bg} ${riskColor.text}`}
                        >
                          {riskLabels[client.risk]}
                        </div>
                      </div>
                    </div>
                  </Link>
                )
              })}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12">
              <Users className="h-12 w-12 text-slate-300 mb-3" />
              <p className="text-slate-600 font-medium mb-1">No clients found</p>
              <p className="text-slate-400 text-sm mb-4">
                Create your first client to get started
              </p>
              <Button onClick={() => setOpenCreateDialog(true)} className="gap-2 bg-sky-500 hover:bg-sky-600 text-white">
                <Plus className="h-4 w-4" />
                New Client
              </Button>
            </div>
          )}
        </div>
      </main>
    </>
  )
}
