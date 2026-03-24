"use client"

import type { ClientResponse } from "@/lib/hooks"

const riskColors: Record<string, { bg: string; text: string }> = {
  low: { bg: "bg-green-50", text: "text-green-700" },
  moderate: { bg: "bg-amber-50", text: "text-amber-700" },
  high: { bg: "bg-red-50", text: "text-red-700" },
}

interface ClientHeaderCardProps {
  client: ClientResponse
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

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-SE", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

export function ClientHeaderCard({ client }: ClientHeaderCardProps) {
  const initials = client.name
    .split(" ")
    .map((n) => n[0])
    .join("")
  const riskColor = riskColors[client.risk_profile ?? ""] ?? { bg: "bg-slate-100", text: "text-slate-600" }

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm">
      <div className="flex items-start gap-4">
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-slate-100">
          <span className="text-lg font-semibold text-slate-600">{initials}</span>
        </div>

        <div className="flex-1">
          <h1 className="mb-1 text-xl font-semibold text-slate-900">{client.name}</h1>
          <p className="mb-3 text-sm text-slate-500">
            Born {formatDate(client.date_of_birth)} · {calculateAge(client.date_of_birth)} years
          </p>

          <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${riskColor.bg} ${riskColor.text}`}>
            {client.employment_status.charAt(0).toUpperCase() + client.employment_status.slice(1).replace("_", " ")}
          </div>
        </div>
      </div>
    </div>
  )
}
