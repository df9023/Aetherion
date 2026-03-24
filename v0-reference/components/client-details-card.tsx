'use client'

import { Client, getRiskColor } from '@/lib/data'

interface Props {
  client: Client
}

export function ClientDetailsCard({ client }: Props) {
  const riskColor = getRiskColor(client.risk)
  const riskLabels = { low: 'Low', moderate: 'Moderate', high: 'High' }
  const statusLabels = {
    employed: 'Employed',
    unemployed: 'Unemployed',
    retired: 'Retired',
  }

  const details = [
    { label: 'Employer', value: client.employer },
    {
      label: 'Collective Agreement',
      value: client.agreement,
      badge: true,
    },
    { label: 'Annual Income', value: `${client.annualIncome.toLocaleString()} kr` },
    { label: 'Monthly Income', value: `${client.monthlyIncome.toLocaleString()} kr` },
    { label: 'Desired Retirement Age', value: client.retirementAge.toString() },
    {
      label: 'Risk Profile',
      value: riskLabels[client.risk],
      badge: true,
      badgeColor: riskColor,
    },
    {
      label: 'Employment Status',
      value: statusLabels[client.status],
      badge: true,
    },
  ]

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm p-6">
      <h3 className="text-xs font-medium uppercase tracking-wider text-slate-400 mb-4">
        Details
      </h3>

      <div className="grid grid-cols-2 gap-4">
        {details.map((item, idx) => (
          <div key={idx}>
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400 mb-1">
              {item.label}
            </p>
            {item.badge ? (
              <div
                className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  item.badgeColor
                    ? `${item.badgeColor.bg} ${item.badgeColor.text}`
                    : 'bg-blue-50 text-blue-700'
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
