"use client"

import { cn } from "@/lib/utils"
import { Skeleton } from "@/components/ui/skeleton"
import type { ClientResponse } from "@/lib/hooks"

const riskColors: Record<string, string> = {
  low: "bg-green-50 text-green-700",
  moderate: "bg-amber-50 text-amber-700",
  high: "bg-red-50 text-red-700",
}

const riskLabels: Record<string, string> = {
  low: "Låg",
  moderate: "Medel",
  high: "Hög",
}

const employmentLabels: Record<string, string> = {
  employed: "Anställd",
  self_employed: "Egenföretagare",
  retired: "Pensionär",
  other: "Övrigt",
}

interface ClientInfoCardProps {
  client: ClientResponse | undefined
  isLoading: boolean
}

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
  return new Intl.NumberFormat("sv-SE").format(Number(amount)) + " kr"
}

export function ClientInfoCard({ client, isLoading }: ClientInfoCardProps) {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
        <div className="border-b border-slate-100 px-5 py-4">
          <h3 className="text-sm font-semibold text-slate-700">Klientinformation</h3>
        </div>
        <div className="grid grid-cols-2 gap-x-6 gap-y-4 px-5 py-5">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i}>
              <Skeleton className="h-3 w-16" />
              <Skeleton className="mt-1.5 h-5 w-24" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!client) {
    return (
      <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
        <div className="border-b border-slate-100 px-5 py-4">
          <h3 className="text-sm font-semibold text-slate-700">Klientinformation</h3>
        </div>
        <p className="px-5 py-5 text-sm text-slate-400">Klient hittades inte</p>
      </div>
    )
  }

  const fields: { label: string; value: React.ReactNode }[] = [
    { label: "Namn", value: client.name },
    { label: "Ålder", value: `${calculateAge(client.date_of_birth)} år` },
    { label: "Arbetsgivare", value: client.employer_name ?? "—" },
    {
      label: "Kollektivavtal",
      value: (
        <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-sm font-medium text-blue-700">
          {client.collective_agreement}
        </span>
      ),
    },
    {
      label: "Månadsinkomst",
      value: client.annual_income
        ? formatCurrency(String(Math.round(Number(client.annual_income) / 12)))
        : "—",
    },
    {
      label: "Riskprofil",
      value: client.risk_profile ? (
        <span
          className={cn(
            "rounded-full px-2.5 py-0.5 text-sm font-medium",
            riskColors[client.risk_profile] ?? "bg-slate-100 text-slate-600"
          )}
        >
          {riskLabels[client.risk_profile] ?? client.risk_profile}
        </span>
      ) : (
        "—"
      ),
    },
    { label: "Önskad pensionsålder", value: client.desired_retirement_age ? `${client.desired_retirement_age} år` : "—" },
    {
      label: "Anställningsstatus",
      value: employmentLabels[client.employment_status] ?? client.employment_status,
    },
  ]

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4">
        <h3 className="text-sm font-semibold text-slate-700">Klientinformation</h3>
      </div>
      <div className="grid grid-cols-2 gap-x-6 gap-y-4 px-5 py-5">
        {fields.map(({ label, value }) => (
          <div key={label}>
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">
              {label}
            </p>
            <div className="mt-1 text-sm font-medium text-slate-800">{value}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
