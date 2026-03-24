"use client"

import { cn } from "@/lib/utils"
import { Skeleton } from "@/components/ui/skeleton"
import type { ClientResponse } from "@/lib/hooks"

const riskColors: Record<string, string> = {
  low: "bg-green-50 text-green-700",
  moderate: "bg-amber-50 text-amber-700",
  high: "bg-red-50 text-red-700",
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
          <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">Client Information</p>
        </div>
        <div className="grid grid-cols-2 gap-x-6 gap-y-3 px-5 py-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i}>
              <Skeleton className="h-3 w-16" />
              <Skeleton className="mt-1 h-4 w-24" />
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
          <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">Client Information</p>
        </div>
        <p className="px-5 py-4 text-sm text-slate-400">Client not found</p>
      </div>
    )
  }

  const fields: { label: string; value: React.ReactNode }[] = [
    { label: "Name", value: client.name },
    { label: "Age", value: `${calculateAge(client.date_of_birth)} years` },
    { label: "Employer", value: client.employer_name ?? "—" },
    {
      label: "Collective Agreement",
      value: (
        <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
          {client.collective_agreement}
        </span>
      ),
    },
    {
      label: "Monthly Income",
      value: client.annual_income
        ? formatCurrency(String(Math.round(Number(client.annual_income) / 12)))
        : "—",
    },
    {
      label: "Risk Profile",
      value: client.risk_profile ? (
        <span
          className={cn(
            "rounded-full px-2 py-0.5 text-xs font-medium",
            riskColors[client.risk_profile] ?? "bg-slate-100 text-slate-600"
          )}
        >
          {client.risk_profile.charAt(0).toUpperCase() + client.risk_profile.slice(1)}
        </span>
      ) : (
        "—"
      ),
    },
    { label: "Retirement Age", value: client.desired_retirement_age ?? "—" },
    {
      label: "Employment Status",
      value: client.employment_status.charAt(0).toUpperCase() + client.employment_status.slice(1).replace("_", " "),
    },
  ]

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4">
        <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
          Client Information
        </p>
      </div>
      <div className="grid grid-cols-2 gap-x-6 gap-y-3 px-5 py-4">
        {fields.map(({ label, value }) => (
          <div key={label}>
            <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
              {label}
            </p>
            <div className="mt-0.5 text-sm font-medium text-slate-800">{value}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
