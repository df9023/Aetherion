"use client"

import { use } from "react"
import Link from "next/link"
import { Building2, Shield, Target, Clock, Briefcase, Plus, Upload } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import { useClient, useClientCases } from "@/lib/hooks"
import { caseTypeLabels, statusStyles, statusLabels } from "@/lib/labels"
import { CreateCaseDialog } from "@/components/create-case-dialog"
import { DocumentIngestion } from "@/components/document-ingestion"
import { Button } from "@/components/ui/button"

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-SE", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

function formatCurrency(amount: string) {
  return new Intl.NumberFormat("sv-SE").format(Number(amount)) + " kr"
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

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return "Today"
  if (days === 1) return "Yesterday"
  return `${days} days ago`
}

export default function ClientDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const { data: client, isLoading } = useClient(id)
  const { data: cases, isLoading: casesLoading } = useClientCases(id)

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-32 rounded-xl" />
        <Skeleton className="h-60 rounded-xl" />
        <Skeleton className="h-40 rounded-xl" />
      </div>
    )
  }

  if (!client) {
    return <div className="py-12 text-center text-slate-400">Client not found</div>
  }

  return (
    <div className="space-y-6">
      {/* Client header */}
      <div className="rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 text-lg font-semibold text-slate-600">
            {client.name
              .split(" ")
              .map((n) => n[0])
              .join("")}
          </div>
          <div>
            <h1 className="text-xl font-semibold text-slate-900">{client.name}</h1>
            <div className="mt-1 flex items-center gap-3 text-sm text-slate-500">
              <span>{formatDate(client.date_of_birth)} ({calculateAge(client.date_of_birth)} years)</span>
              <span className="inline-flex rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium capitalize text-slate-600">
                {client.employment_status.replace("_", " ")}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Details */}
      <div className="rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm">
        <h2 className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Details</h2>
        <div className="mt-4 grid grid-cols-2 gap-x-8 gap-y-4">
          <div>
            <p className="text-xs text-slate-400">Employer</p>
            <p className="flex items-center gap-1.5 text-sm font-medium text-slate-900">
              <Building2 className="h-3.5 w-3.5 text-slate-400" />
              {client.employer_name || "—"}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Collective Agreement</p>
            <span className="inline-flex rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
              {client.collective_agreement}
            </span>
          </div>
          <div>
            <p className="text-xs text-slate-400">Annual Income</p>
            <p className="text-sm font-medium text-slate-900">
              {client.annual_income ? formatCurrency(client.annual_income) : "—"}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Monthly Income</p>
            <p className="text-sm font-medium text-slate-900">
              {client.annual_income
                ? formatCurrency(String(Math.round(Number(client.annual_income) / 12)))
                : "—"}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Desired Retirement Age</p>
            <p className="flex items-center gap-1.5 text-sm font-medium text-slate-900">
              <Target className="h-3.5 w-3.5 text-slate-400" />
              {client.desired_retirement_age ?? "—"}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Risk Profile</p>
            {client.risk_profile ? (
              <span
                className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  client.risk_profile === "low"
                    ? "bg-green-50 text-green-700"
                    : client.risk_profile === "moderate"
                      ? "bg-amber-50 text-amber-700"
                      : "bg-red-50 text-red-700"
                }`}
              >
                <Shield className="h-3 w-3" />
                {client.risk_profile.charAt(0).toUpperCase() + client.risk_profile.slice(1)}
              </span>
            ) : (
              <span className="text-sm text-slate-400">—</span>
            )}
          </div>
          <div>
            <p className="text-xs text-slate-400">Employment Status</p>
            <p className="text-sm font-medium capitalize text-slate-900">
              {client.employment_status.replace("_", " ")}
            </p>
          </div>
        </div>
      </div>

      {/* Document Ingestion */}
      <div className="rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-2">
          <Upload className="h-5 w-5 text-sky-500" />
          <h2 className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Document Ingestion</h2>
        </div>
        <div className="mt-4">
          <DocumentIngestion clientId={id} client={client} />
        </div>
      </div>

      {/* Linked cases */}
      <div className="rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Linked Cases</h2>
          <CreateCaseDialog
            defaultClientId={id}
            trigger={
              <Button variant="outline" size="sm" className="rounded-lg text-xs">
                <Plus className="mr-1.5 h-3.5 w-3.5" />
                New Case
              </Button>
            }
          />
        </div>
        <div className="mt-4 space-y-3">
          {casesLoading &&
            Array.from({ length: 2 }).map((_, i) => (
              <Skeleton key={i} className="h-16 rounded-lg" />
            ))}
          {!casesLoading &&
            cases.map((c) => (
              <Link key={c.id} href={`/cases/${c.id}`}>
                <div className="rounded-lg border border-slate-100 p-4 transition-all duration-200 hover:border-slate-300 hover:shadow-sm">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <Briefcase className="h-4 w-4 text-slate-400" />
                      <p className="text-sm font-medium text-slate-900">{c.title}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${statusStyles[c.status] ?? ""}`}>
                        {statusLabels[c.status] ?? c.status}
                      </span>
                      <span className="inline-flex rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                        {caseTypeLabels[c.case_type] ?? c.case_type}
                      </span>
                    </div>
                  </div>
                  <div className="mt-2 flex items-center gap-1 text-xs text-slate-400">
                    <Clock className="h-3 w-3" />
                    {timeAgo(c.updated_at)}
                  </div>
                </div>
              </Link>
            ))}
          {!casesLoading && cases.length === 0 && (
            <p className="py-6 text-center text-sm text-slate-400">No cases yet</p>
          )}
        </div>
      </div>
    </div>
  )
}
