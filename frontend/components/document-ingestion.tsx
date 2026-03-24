"use client"

import { useState, useCallback, useRef } from "react"
import {
  Upload,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  ArrowRight,
  X,
} from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import {
  useIngestDocument,
  useApplyExtraction,
} from "@/lib/hooks"
import type {
  ClientResponse,
  DocumentExtractionResponse,
  ExtractedField,
} from "@/lib/hooks"

const fieldLabels: Record<string, string> = {
  name: "Name",
  date_of_birth: "Date of Birth",
  employer_name: "Employer",
  collective_agreement: "Collective Agreement",
  annual_income: "Annual Income",
  monthly_income: "Monthly Income",
  employment_status: "Employment Status",
  pension_provider: "Pension Provider",
  total_fees_percent: "Total Fees",
  survivor_protection: "Survivor Protection",
  pension_capital: "Pension Capital",
  desired_retirement_age: "Retirement Age",
  risk_profile: "Risk Profile",
}

const APPLICABLE_FIELDS = new Set([
  "name",
  "date_of_birth",
  "employer_name",
  "collective_agreement",
  "annual_income",
  "employment_status",
  "desired_retirement_age",
  "risk_profile",
])

function clientFieldValue(client: ClientResponse, fieldName: string): string | null {
  switch (fieldName) {
    case "name": return client.name
    case "date_of_birth": return client.date_of_birth
    case "employer_name": return client.employer_name
    case "collective_agreement": return client.collective_agreement
    case "annual_income": return client.annual_income
    case "employment_status": return client.employment_status
    case "desired_retirement_age": return client.desired_retirement_age?.toString() ?? null
    case "risk_profile": return client.risk_profile
    default: return null
  }
}

function getConfidenceIcon(confidence: number) {
  if (confidence >= 0.8) return <CheckCircle2 className="h-4 w-4 text-green-500" />
  if (confidence >= 0.5) return <AlertTriangle className="h-4 w-4 text-amber-500" />
  return <AlertCircle className="h-4 w-4 text-red-500" />
}

function getConfidenceColor(confidence: number) {
  if (confidence >= 0.8) return "text-green-600"
  if (confidence >= 0.5) return "text-amber-600"
  return "text-red-600"
}

interface Props {
  clientId: string
  client: ClientResponse
}

export function DocumentIngestion({ clientId, client }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const ingest = useIngestDocument(clientId)
  const apply = useApplyExtraction(clientId)

  const [extraction, setExtraction] = useState<DocumentExtractionResponse | null>(null)
  const [selectedFields, setSelectedFields] = useState<Set<string>>(new Set())
  const [dragOver, setDragOver] = useState(false)

  const handleFile = useCallback(
    (file: File) => {
      if (!file.name.toLowerCase().endsWith(".pdf")) {
        toast.error("Only PDF files are supported")
        return
      }
      ingest.mutate(file, {
        onSuccess: (data) => {
          setExtraction(data)
          const preselected = new Set<string>()
          for (const f of data.extracted_fields) {
            if (APPLICABLE_FIELDS.has(f.field_name) && f.confidence >= 0.5) {
              preselected.add(f.field_name)
            }
          }
          setSelectedFields(preselected)
        },
        onError: (err) => toast.error(err.message),
      })
    },
    [ingest]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragOver(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile]
  )

  const handleApply = useCallback(() => {
    if (!extraction) return
    const data: Record<string, string | number> = {}
    for (const field of extraction.extracted_fields) {
      if (!selectedFields.has(field.field_name)) continue
      if (!APPLICABLE_FIELDS.has(field.field_name)) continue

      if (field.field_name === "desired_retirement_age") {
        data[field.field_name] = parseInt(field.value, 10)
      } else if (field.field_name === "annual_income") {
        data[field.field_name] = field.value.replace(/[^\d.]/g, "")
      } else {
        data[field.field_name] = field.value
      }
    }

    if (Object.keys(data).length === 0) {
      toast.error("No applicable fields selected")
      return
    }

    apply.mutate(data, {
      onSuccess: () => {
        toast.success("Client profile updated")
        setExtraction(null)
        setSelectedFields(new Set())
      },
      onError: (err) => toast.error(err.message),
    })
  }, [extraction, selectedFields, apply])

  const handleReset = useCallback(() => {
    setExtraction(null)
    setSelectedFields(new Set())
  }, [])

  const toggleField = (fieldName: string) => {
    setSelectedFields((prev) => {
      const next = new Set(prev)
      if (next.has(fieldName)) {
        next.delete(fieldName)
      } else {
        next.add(fieldName)
      }
      return next
    })
  }

  // State 1: Upload
  if (!extraction && !ingest.isPending) {
    return (
      <div>
        <div
          className={`flex cursor-pointer flex-col items-center rounded-xl border-2 border-dashed p-8 text-center transition-colors ${
            dragOver
              ? "border-sky-400 bg-sky-50/50"
              : "border-slate-300 hover:border-slate-400"
          }`}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
        >
          <Upload className="mb-3 h-10 w-10 text-slate-300" />
          <p className="mb-1 text-sm font-medium text-slate-700">Upload pension document</p>
          <p className="mb-3 text-xs text-slate-400">Drop a PDF here or click to browse</p>
          <p className="text-xs text-slate-400">Supported formats: PDF. Max size 10 MB.</p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) handleFile(file)
            e.target.value = ""
          }}
        />
      </div>
    )
  }

  // State 2: Extracting
  if (ingest.isPending) {
    return (
      <div className="space-y-4">
        {[
          { step: 1, label: "Extracting text from document..." },
          { step: 2, label: "Analyzing pension data..." },
          { step: 3, label: "Building structured output..." },
        ].map((item, idx) => (
          <div key={idx} className="flex items-start gap-3">
            <div className="mt-0.5 shrink-0">
              {idx < 1 ? (
                <CheckCircle2 className="h-5 w-5 text-green-500" />
              ) : idx === 1 ? (
                <Loader2 className="h-5 w-5 animate-spin text-sky-500" />
              ) : (
                <div className="h-5 w-5 rounded-full bg-slate-200" />
              )}
            </div>
            <div className={idx === 1 ? "animate-pulse" : ""}>
              <p className={idx < 1 ? "text-sm text-slate-600" : "text-sm font-medium text-slate-900"}>
                {item.label}
              </p>
            </div>
          </div>
        ))}
        <p className="mt-4 text-xs text-slate-400">This may take 15-30 seconds</p>
      </div>
    )
  }

  // State 3: Review
  if (!extraction) return null

  return (
    <div>
      <h4 className="mb-4 text-base font-semibold text-slate-900">Review Extracted Data</h4>

      <div className="mb-6 max-h-96 space-y-3 overflow-y-auto">
        {extraction.extracted_fields.map((field, idx) => {
          const isApplicable = APPLICABLE_FIELDS.has(field.field_name)
          const currentValue = clientFieldValue(client, field.field_name)
          const isDifferent = currentValue !== null && currentValue !== field.value && currentValue !== ""

          return (
            <div key={idx} className="grid grid-cols-2 items-center gap-4 rounded-lg bg-slate-50 p-3">
              <div className="flex items-start gap-3">
                {isApplicable ? (
                  <input
                    type="checkbox"
                    checked={selectedFields.has(field.field_name)}
                    onChange={() => toggleField(field.field_name)}
                    className="mt-0.5 rounded border-slate-300"
                  />
                ) : (
                  <div className="h-4 w-4" />
                )}
                <div className="min-w-0">
                  <p className="mb-1 text-xs uppercase tracking-wider text-slate-400">
                    {fieldLabels[field.field_name] ?? field.field_name}
                  </p>
                  <p className="text-sm font-medium text-slate-900">{field.value}</p>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                  {getConfidenceIcon(field.confidence)}
                  <span className={`text-xs font-medium ${getConfidenceColor(field.confidence)}`}>
                    {Math.round(field.confidence * 100)}%
                  </span>
                </div>

                {isDifferent ? (
                  <div className="flex items-center gap-1 text-xs text-slate-400">
                    <span className="truncate">{currentValue}</span>
                    <ArrowRight className="h-3 w-3 shrink-0" />
                    <span className="truncate">{field.value}</span>
                  </div>
                ) : (
                  <span className="text-xs text-slate-400">—</span>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Fund allocations table */}
      {extraction.fund_allocations.length > 0 && (
        <div className="mb-6 rounded-lg bg-slate-50 p-3">
          <p className="mb-3 text-xs font-medium uppercase tracking-wider text-slate-400">
            Fund Allocations
          </p>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-slate-600">
                <th className="px-2 py-2 text-left font-medium">Fund Name</th>
                <th className="px-2 py-2 text-right font-medium">Allocation</th>
                <th className="px-2 py-2 text-right font-medium">Fee</th>
              </tr>
            </thead>
            <tbody>
              {extraction.fund_allocations.map((fund, idx) => (
                <tr key={idx} className="border-b border-slate-200">
                  <td className="px-2 py-2 text-slate-900">{fund.fund_name}</td>
                  <td className="px-2 py-2 text-right text-slate-600">{fund.allocation_percent}%</td>
                  <td className="px-2 py-2 text-right text-slate-600">
                    {fund.fee_percent !== undefined ? `${fund.fee_percent}%` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex gap-2">
        <Button
          onClick={handleApply}
          disabled={apply.isPending || selectedFields.size === 0}
          className="flex-1 bg-sky-500 text-white hover:bg-sky-600"
        >
          {apply.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Apply Selected Fields
        </Button>
        <Button variant="outline" className="px-4" onClick={handleReset}>
          Cancel
        </Button>
      </div>
    </div>
  )
}
