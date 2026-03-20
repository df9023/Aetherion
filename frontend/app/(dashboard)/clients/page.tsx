"use client"

import { useState } from "react"
import Link from "next/link"
import { Search, Building2, Shield } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { useClients } from "@/lib/hooks"
import { CreateClientDialog } from "@/components/create-client-dialog"

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

export default function ClientsPage() {
  const { data: clients, isLoading } = useClients()
  const [search, setSearch] = useState("")

  const filtered = (clients ?? []).filter(
    (c) => !search || c.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Clients</h1>
        <CreateClientDialog />
      </div>

      <div className="relative mt-6 max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <Input
          placeholder="Search clients..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {isLoading &&
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm">
              <Skeleton className="h-10 w-10 rounded-full" />
              <Skeleton className="mt-3 h-4 w-3/4" />
              <Skeleton className="mt-2 h-3 w-1/2" />
            </div>
          ))}
        {!isLoading &&
          filtered.map((c) => (
            <Link key={c.id} href={`/clients/${c.id}`}>
              <div className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm transition-all duration-200 hover:border-slate-300 hover:shadow-md">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-sm font-medium text-slate-600">
                    {c.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{c.name}</p>
                    <p className="text-xs text-slate-400">{calculateAge(c.date_of_birth)} years old</p>
                  </div>
                </div>

                <div className="mt-4 space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-1.5 text-slate-500">
                      <Building2 className="h-3.5 w-3.5 text-slate-400" />
                      {c.employer_name}
                    </span>
                    <span className="inline-flex rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                      {c.collective_agreement}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500">{c.annual_income ? formatCurrency(c.annual_income) : "—"}</span>
                    {c.risk_profile ? (
                      <span
                        className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          c.risk_profile === "low"
                            ? "bg-green-50 text-green-700"
                            : c.risk_profile === "moderate"
                              ? "bg-amber-50 text-amber-700"
                              : "bg-red-50 text-red-700"
                        }`}
                      >
                        <Shield className="h-3 w-3" />
                        {c.risk_profile.charAt(0).toUpperCase() + c.risk_profile.slice(1)}
                      </span>
                    ) : (
                      <span className="text-xs text-slate-400">—</span>
                    )}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        {!isLoading && filtered.length === 0 && (
          <div className="col-span-full py-12 text-center text-sm text-slate-400">No clients found</div>
        )}
      </div>
    </div>
  )
}
