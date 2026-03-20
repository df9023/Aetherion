"use client"

import { useState, useCallback, useRef } from "react"
import {
  Upload,
  Loader2,
  Check,
  AlertTriangle,
  Flag,
  FileText,
  X,
} from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import {
  useIngestDocument,
  useApplyExtraction,
} from "@/lib/hooks"
import type {
  ClientResponse,
  DocumentExtractionResponse,
  ExtractedField,
} from "@/lib/hooks"

/** Maps extraction field names to display labels */
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

/** Fields that can be applied to the client profile */
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

/** Maps extraction field names to ClientResponse keys */
function clientFieldValue(
  client: ClientResponse,
  fieldName: string,
): string | null {
  switch (fieldName) {
    case "name":
      return client.name
    case "date_of_birth":
      return client.date_of_birth
    case "employer_name":
      return client.employer_name
    case "collective_agreement":
      return client.collective_agreement
    case "annual_income":
      return client.annual_income
    case "employment_status":
      return client.employment_status
    case "desired_retirement_age":
      return client.desired_retirement_age?.toString() ?? null
    case "risk_profile":
      return client.risk_profile
    default:
      return null
  }
}

function ConfidenceIcon({ confidence }: { confidence: number }) {
  if (confidence >= 0.8) {
    return <Check className="h-4 w-4 text-emerald-500" />
  }
  if (confidence >= 0.5) {
    return <AlertTriangle className="h-4 w-4 text-amber-500" />
  }
  return <Flag className="h-4 w-4 text-red-500" />
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
          // Pre-select applicable high-confidence fields
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
    [ingest],
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragOver(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile],
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
        // Strip non-numeric characters except decimal point
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
          className={`flex cursor-pointer flex-col items-center rounded-lg border-2 border-dashed p-8 transition-colors ${
            dragOver
              ? "border-sky-400 bg-sky-50/50"
              : "border-slate-200 hover:border-slate-300"
          }`}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault()
            setDragOver(true)
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
        >
          <Upload className="h-8 w-8 text-slate-300" />
          <p className="mt-3 text-sm font-medium text-slate-600">
            Upload pension document
          </p>
          <p className="mt-1 text-xs text-slate-400">
            PDF — pensionsbesked, lönespecifikation, insurance policy
          </p>
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
      <div className="space-y-4 py-8">
        {["Reading document", "Extracting pension data", "Structuring results"].map(
          (step, i) => (
            <div key={step} className="flex items-center gap-3">
              <div
                className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${
                  i === 0
                    ? "bg-sky-500 text-white"
                    : "bg-slate-200 text-slate-500"
                }`}
              >
                {i === 0 ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  i + 1
                )}
              </div>
              <span
                className={`text-sm ${
                  i === 0
                    ? "font-medium text-slate-900"
                    : "text-slate-400"
                }`}
              >
                {step}...
              </span>
            </div>
          ),
        )}
      </div>
    )
  }

  // State 3: Review
  if (!extraction) return null

  return (
    <div>
      {/* Document type header */}
      <div className="flex items-center gap-2 rounded-lg bg-slate-50 p-3">
        <FileText className="h-4 w-4 text-slate-400" />
        <span className="text-sm font-medium text-slate-700">
          {extraction.document_type}
        </span>
      </div>

      {/* Extracted fields */}
      <div className="mt-4 space-y-2">
        {extraction.extracted_fields.map((field) => {
          const isApplicable = APPLICABLE_FIELDS.has(field.field_name)
          const currentValue = clientFieldValue(client, field.field_name)
          const isDifferent =
            currentValue !== null &&
            currentValue !== field.value &&
            currentValue !== ""

          return (
            <FieldRow
              key={field.field_name}
              field={field}
              isApplicable={isApplicable}
              isSelected={selectedFields.has(field.field_name)}
              currentValue={isDifferent ? currentValue : null}
              onToggle={() => toggleField(field.field_name)}
            />
          )
        })}
      </div>

      {/* Fund allocations */}
      {extraction.fund_allocations.length > 0 && (
        <>
          <Separator className="my-4" />
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Fund Allocations
          </p>
          <div className="mt-3 space-y-2">
            {extraction.fund_allocations.map((fund, i) => (
              <div
                key={i}
                className="flex items-center justify-between rounded-lg border border-slate-100 p-3"
              >
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-slate-900">
                    {fund.fund_name}
                  </p>
                  {fund.fee_percent !== undefined && (
                    <p className="text-xs text-slate-400">
                      Fee: {fund.fee_percent}%
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-semibold text-slate-700">
                    {fund.allocation_percent}%
                  </span>
                  <ConfidenceIcon confidence={fund.confidence} />
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Other observations */}
      {extraction.other_observations && (
        <>
          <Separator className="my-4" />
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Other Observations
          </p>
          <p className="mt-2 text-xs leading-relaxed text-slate-500">
            {extraction.other_observations}
          </p>
        </>
      )}

      {/* Actions */}
      <div className="mt-6 flex items-center gap-3">
        <Button
          onClick={handleApply}
          disabled={apply.isPending || selectedFields.size === 0}
          className="bg-sky-500 text-white hover:bg-sky-600 rounded-lg"
        >
          {apply.isPending ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Check className="mr-2 h-4 w-4" />
          )}
          Apply Selected Fields
        </Button>
        <Button variant="outline" className="rounded-lg" onClick={handleReset}>
          <X className="mr-2 h-4 w-4" />
          Cancel
        </Button>
      </div>
    </div>
  )
}

function FieldRow({
  field,
  isApplicable,
  isSelected,
  currentValue,
  onToggle,
}: {
  field: ExtractedField
  isApplicable: boolean
  isSelected: boolean
  currentValue: string | null
  onToggle: () => void
}) {
  return (
    <div
      className={`flex items-center gap-3 rounded-lg border p-3 transition-colors ${
        isSelected
          ? "border-sky-200 bg-sky-50/30"
          : "border-slate-100"
      }`}
    >
      {/* Checkbox */}
      {isApplicable ? (
        <button
          onClick={onToggle}
          className={`flex h-5 w-5 shrink-0 items-center justify-center rounded border transition-colors ${
            isSelected
              ? "border-sky-500 bg-sky-500 text-white"
              : "border-slate-300 bg-white"
          }`}
        >
          {isSelected && <Check className="h-3 w-3" />}
        </button>
      ) : (
        <div className="h-5 w-5 shrink-0" />
      )}

      {/* Field info */}
      <div className="min-w-0 flex-1">
        <p className="text-xs text-slate-400">
          {fieldLabels[field.field_name] ?? field.field_name}
        </p>
        <p className="text-sm font-medium text-slate-900">{field.value}</p>
        {currentValue && (
          <p className="mt-0.5 text-[11px] text-amber-600">
            Current: {currentValue} → {field.value}
          </p>
        )}
      </div>

      {/* Confidence */}
      <div className="flex shrink-0 items-center gap-1.5">
        <ConfidenceIcon confidence={field.confidence} />
        <span className="text-xs text-slate-400">
          {Math.round(field.confidence * 100)}%
        </span>
      </div>
    </div>
  )
}
