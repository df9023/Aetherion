"use client"

import Link from "next/link"
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

  const riskLabels: Record<string, string> = { low: "Låg", moderate: "Medel", high: "Hög" }
  const employmentLabels: Record<string, string> = { employed: "Anställd", self_employed: "Egenföretagare", retired: "Pensionär", other: "Övrigt" }

  const employerDisplay = client.client_organization_name ?? client.employer_name ?? "—"

  const details: { label: string; value: string; badge?: boolean; badgeColor?: { bg: string; text: string }; link?: string }[] = [
    { label: "Arbetsgivare", value: employerDisplay, link: client.client_organization_id ? `/organizations/${client.client_organization_id}` : undefined },
    { label: "Kollektivavtal", value: client.collective_agreement, badge: true },
    { label: "Årsinkomst", value: client.annual_income ? formatCurrency(client.annual_income) : "—" },
    {
      label: "Månadsinkomst",
      value: client.annual_income ? formatCurrency(String(Math.round(Number(client.annual_income) / 12))) : "—",
    },
    { label: "Önskad pensionsålder", value: client.desired_retirement_age?.toString() ?? "—" },
    {
      label: "Riskprofil",
      value: client.risk_profile ? riskLabels[client.risk_profile] ?? client.risk_profile : "—",
      badge: !!client.risk_profile,
      badgeColor: riskColor,
    },
    {
      label: "Anställningsstatus",
      value: employmentLabels[client.employment_status] ?? client.employment_status,
      badge: true,
    },
  ]

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-xs font-medium uppercase tracking-wider text-slate-400">
        Detaljer
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
            ) : item.link ? (
              <Link href={item.link} className="text-sm font-medium text-sky-600 hover:text-sky-700">
                {item.value}
              </Link>
            ) : (
              <p className="text-sm font-medium text-slate-900">{item.value}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
