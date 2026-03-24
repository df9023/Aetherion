"use client"

import type { ClientResponse } from "@/lib/hooks"

const riskColors: Record<string, { bg: string; text: string }> = {
  low: { bg: "bg-green-50", text: "text-green-700" },
  moderate: { bg: "bg-amber-50", text: "text-amber-700" },
  high: { bg: "bg-red-50", text: "text-red-700" },
}

interface ClientDetailsCardProps {
  client: ClientResponse
}

function formatCurrency(amount: string) {
  return new Intl.NumberFormat("sv-SE").format(Number(amount)) + " kr"
}

export function ClientDetailsCard({ client }: ClientDetailsCardProps) {
  const riskColor = riskColors[client.risk_profile ?? ""]

  const details: { label: string; value: string; badge?: boolean; badgeColor?: { bg: string; text: string } }[] = [
    { label: "Employer", value: client.employer_name ?? "—" },
    { label: "Collective Agreement", value: client.collective_agreement, badge: true },
    { label: "Annual Income", value: client.annual_income ? formatCurrency(client.annual_income) : "—" },
    {
      label: "Monthly Income",
      value: client.annual_income ? formatCurrency(String(Math.round(Number(client.annual_income) / 12))) : "—",
    },
    { label: "Desired Retirement Age", value: client.desired_retirement_age?.toString() ?? "—" },
    {
      label: "Risk Profile",
      value: client.risk_profile ? client.risk_profile.charAt(0).toUpperCase() + client.risk_profile.slice(1) : "—",
      badge: !!client.risk_profile,
      badgeColor: riskColor,
    },
    {
      label: "Employment Status",
      value: client.employment_status.charAt(0).toUpperCase() + client.employment_status.slice(1).replace("_", " "),
      badge: true,
    },
  ]

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-xs font-medium uppercase tracking-wider text-slate-400">
        Details
      </h3>

      <div className="grid grid-cols-2 gap-4">
        {details.map((item, idx) => (
          <div key={idx}>
            <p className="mb-1 text-xs font-medium uppercase tracking-wider text-slate-400">
              {item.label}
            </p>
            {item.badge ? (
              <div
                className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  item.badgeColor
                    ? `${item.badgeColor.bg} ${item.badgeColor.text}`
                    : "bg-blue-50 text-blue-700"
                }`}
              >
                {item.value}
              </div>
            ) : (
              <p className="text-sm font-medium text-slate-900">{item.value}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
