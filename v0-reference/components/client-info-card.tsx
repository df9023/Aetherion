'use client'

import { type Case } from '@/lib/data'
import { cn } from '@/lib/utils'

const riskColors: Record<string, string> = {
  Conservative: 'bg-blue-50 text-blue-700',
  Moderate: 'bg-amber-50 text-amber-700',
  Aggressive: 'bg-red-50 text-red-700',
}

interface ClientInfoCardProps {
  caseData: Case
}

const clientDetails = {
  cs1: {
    name: 'Anna Johansson',
    age: '45',
    employer: 'Volvo Cars AB',
    collectiveAgreement: 'ITP1',
    monthlyIncome: '60 000 kr',
    riskProfile: 'Moderate',
    retirementAge: '65',
    employmentStatus: 'Full-time',
  },
  cs2: {
    name: 'Lars Pettersson',
    age: '58',
    employer: 'Ericsson AB',
    collectiveAgreement: 'ITP2',
    monthlyIncome: '98 000 kr',
    riskProfile: 'Conservative',
    retirementAge: '63',
    employmentStatus: 'Full-time',
  },
  cs3: {
    name: 'Anna Johansson',
    age: '45',
    employer: 'Volvo Cars AB',
    collectiveAgreement: 'ITP1',
    monthlyIncome: '60 000 kr',
    riskProfile: 'Moderate',
    retirementAge: '65',
    employmentStatus: 'Full-time',
  },
  cs4: {
    name: 'Lars Pettersson',
    age: '58',
    employer: 'Ericsson AB',
    collectiveAgreement: 'ITP2',
    monthlyIncome: '98 000 kr',
    riskProfile: 'Conservative',
    retirementAge: '63',
    employmentStatus: 'Full-time',
  },
} as Record<string, typeof clientDetails.cs1>

export function ClientInfoCard({ caseData }: ClientInfoCardProps) {
  const info = clientDetails[caseData.id] ?? clientDetails.cs1

  const fields = [
    { label: 'Name', value: info.name },
    { label: 'Age', value: info.age },
    { label: 'Employer', value: info.employer },
    {
      label: 'Collective Agreement',
      value: (
        <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
          {info.collectiveAgreement}
        </span>
      ),
    },
    { label: 'Monthly Income', value: info.monthlyIncome },
    {
      label: 'Risk Profile',
      value: (
        <span
          className={cn(
            'rounded-full px-2 py-0.5 text-xs font-medium',
            riskColors[info.riskProfile] ?? 'bg-slate-100 text-slate-600'
          )}
        >
          {info.riskProfile}
        </span>
      ),
    },
    { label: 'Retirement Age', value: info.retirementAge },
    { label: 'Employment Status', value: info.employmentStatus },
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
