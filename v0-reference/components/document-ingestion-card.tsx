'use client'

import { useState } from 'react'
import {
  Upload,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Loader2,
  ArrowRight,
} from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ExtractedField {
  label: string
  value: string
  confidence: number
  current?: string
  checked: boolean
}

export function DocumentIngestionCard() {
  const [state, setState] = useState<'upload' | 'extracting' | 'review'>(
    'review'
  )
  const [fields, setFields] = useState<ExtractedField[]>([
    {
      label: 'Employer',
      value: 'Volvo Group AB',
      confidence: 98,
      current: 'Volvo Group AB',
      checked: true,
    },
    {
      label: 'Collective Agreement',
      value: 'ITP1',
      confidence: 95,
      current: 'ITP1',
      checked: true,
    },
    {
      label: 'Pension Provider',
      value: 'Collectum',
      confidence: 88,
      current: undefined,
      checked: true,
    },
    {
      label: 'Annual Income',
      value: '720 000 kr',
      confidence: 72,
      current: '684 000 kr',
      checked: true,
    },
    {
      label: 'Survivor Protection',
      value: 'Yes, 5 years',
      confidence: 65,
      current: undefined,
      checked: true,
    },
    {
      label: 'Risk Profile',
      value: 'Moderate',
      confidence: 42,
      current: 'Moderate',
      checked: false,
    },
  ])

  const handleCheck = (index: number) => {
    setFields((prev) =>
      prev.map((f, i) => (i === index ? { ...f, checked: !f.checked } : f))
    )
  }

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 80) {
      return <CheckCircle2 className="h-4 w-4 text-green-500" />
    } else if (confidence >= 50) {
      return <AlertTriangle className="h-4 w-4 text-amber-500" />
    }
    return <AlertCircle className="h-4 w-4 text-red-500" />
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600'
    if (confidence >= 50) return 'text-amber-600'
    return 'text-red-600'
  }

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm p-6">
      <div className="flex items-center gap-2 mb-6">
        <Upload className="h-5 w-5 text-slate-600" />
        <h3 className="text-base font-semibold text-slate-900">
          Document Ingestion
        </h3>
      </div>

      {state === 'upload' && (
        <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center">
          <Upload className="h-10 w-10 text-slate-300 mx-auto mb-3" />
          <p className="text-sm font-medium text-slate-700 mb-1">
            Upload pension document
          </p>
          <p className="text-xs text-slate-400 mb-3">
            Drop a PDF here or click to browse
          </p>
          <p className="text-xs text-slate-400">
            Supported formats: PDF. Max size 10 MB.
          </p>
        </div>
      )}

      {state === 'extracting' && (
        <div className="space-y-4">
          {[
            { step: 1, label: 'Extracting text from document...' },
            { step: 2, label: 'Analyzing pension data...' },
            { step: 3, label: 'Building structured output...' },
          ].map((item, idx) => (
            <div key={idx} className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-0.5">
                {idx < 1 ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                ) : idx === 1 ? (
                  <Loader2 className="h-5 w-5 text-sky-500 animate-spin" />
                ) : (
                  <div className="h-5 w-5 rounded-full bg-slate-200" />
                )}
              </div>
              <div className={idx === 1 ? 'animate-pulse' : ''}>
                <p
                  className={
                    idx < 1
                      ? 'text-sm text-slate-600'
                      : 'text-sm text-slate-900 font-medium'
                  }
                >
                  {item.label}
                </p>
              </div>
            </div>
          ))}
          <p className="text-xs text-slate-400 mt-4">
            This may take 15-30 seconds
          </p>
        </div>
      )}

      {state === 'review' && (
        <div>
          <h4 className="text-base font-semibold text-slate-900 mb-4">
            Review Extracted Data
          </h4>

          <div className="space-y-3 mb-6 max-h-96 overflow-y-auto">
            {fields.map((field, idx) => (
              <div key={idx} className="grid grid-cols-2 gap-4 p-3 bg-slate-50 rounded-lg items-center">
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={field.checked}
                    onChange={() => handleCheck(idx)}
                    className="mt-0.5 rounded border-slate-300"
                  />
                  <div className="min-w-0">
                    <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">
                      {field.label}
                    </p>
                    <p className="text-sm font-medium text-slate-900">
                      {field.value}
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1">
                    {getConfidenceIcon(field.confidence)}
                    <span className={`text-xs font-medium ${getConfidenceColor(field.confidence)}`}>
                      {field.confidence}%
                    </span>
                  </div>

                  {field.current && field.current !== field.value ? (
                    <div className="flex items-center gap-1 text-slate-400 text-xs">
                      <span className="truncate">{field.current}</span>
                      <ArrowRight className="h-3 w-3 flex-shrink-0" />
                      <span className="truncate">{field.value}</span>
                    </div>
                  ) : (
                    <span className="text-xs text-slate-400">—</span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Fund allocations table */}
          <div className="mb-6 p-3 bg-slate-50 rounded-lg">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400 mb-3">
              Fund Allocations
            </p>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-slate-600">
                  <th className="text-left py-2 px-2 font-medium">Fund Name</th>
                  <th className="text-right py-2 px-2 font-medium">Allocation</th>
                  <th className="text-right py-2 px-2 font-medium">Fee</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { name: 'Handelsbanken Norden', alloc: '45%', fee: '0.32%' },
                  { name: 'SEB Sverige', alloc: '35%', fee: '0.28%' },
                  { name: 'AMF Räntefond', alloc: '20%', fee: '0.12%' },
                ].map((row, idx) => (
                  <tr key={idx} className="border-b border-slate-200">
                    <td className="py-2 px-2 text-slate-900">{row.name}</td>
                    <td className="py-2 px-2 text-right text-slate-600">{row.alloc}</td>
                    <td className="py-2 px-2 text-right text-slate-600">{row.fee}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex gap-2">
            <Button className="flex-1 bg-sky-500 hover:bg-sky-600 text-white">
              Apply Selected Fields
            </Button>
            <Button variant="outline" className="px-4">
              Cancel
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
