'use client'

import { Client, getInitials, getRiskColor } from '@/lib/data'

interface Props {
  client: Client
}

export function ClientHeaderCard({ client }: Props) {
  const riskColor = getRiskColor(client.risk)
  const riskLabels = { low: 'Low', moderate: 'Moderate', high: 'High' }

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm p-6">
      <div className="flex items-start gap-4">
        <div className="h-14 w-14 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">
          <span className="text-lg font-semibold text-slate-600">
            {getInitials(client.name)}
          </span>
        </div>

        <div className="flex-1">
          <h1 className="text-xl font-semibold text-slate-900 mb-1">
            {client.name}
          </h1>
          <p className="text-sm text-slate-500 mb-3">
            Born {client.dob} · {client.age} years
          </p>

          <div
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${riskColor.bg} ${riskColor.text}`}
          >
            {client.status.charAt(0).toUpperCase() + client.status.slice(1)}
          </div>
        </div>
      </div>
    </div>
  )
}
