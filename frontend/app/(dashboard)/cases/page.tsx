"use client"

import { useState } from "react"
import Link from "next/link"
import { Search, Clock } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useCases } from "@/lib/hooks"
import { caseTypeLabels, statusStyles, statusLabels } from "@/lib/labels"
import { CreateCaseDialog } from "@/components/create-case-dialog"

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return "Today"
  if (days === 1) return "Yesterday"
  return `${days} days ago`
}

export default function CasesPage() {
  const { data: cases, isLoading } = useCases()
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [typeFilter, setTypeFilter] = useState<string>("all")

  const filtered = (cases ?? []).filter((c) => {
    if (search && !c.title.toLowerCase().includes(search.toLowerCase())) return false
    if (statusFilter !== "all" && c.status !== statusFilter) return false
    if (typeFilter !== "all" && c.case_type !== typeFilter) return false
    return true
  })

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Cases</h1>
        <CreateCaseDialog />
      </div>

      <div className="mt-6 flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <Input
            placeholder="Search cases..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-44">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            {Object.entries(statusLabels).map(([val, label]) => (
              <SelectItem key={val} value={val}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Case Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {Object.entries(caseTypeLabels).map(([val, label]) => (
              <SelectItem key={val} value={val}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="mt-6 space-y-3">
        {isLoading &&
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="mt-2 h-3 w-1/2" />
              <Skeleton className="mt-3 h-3 w-1/4" />
            </div>
          ))}

        {!isLoading &&
          filtered.map((c) => (
            <Link key={c.id} href={`/cases/${c.id}`}>
              <div className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm transition-all duration-200 hover:border-slate-300 hover:shadow-md">
                <div className="flex items-start justify-between">
                  <div className="min-w-0 flex-1">
                    <h3 className="text-sm font-semibold text-slate-900">{c.title}</h3>
                    <p className="mt-1 text-sm text-slate-500 line-clamp-1">{c.summary}</p>
                  </div>
                  <div className="ml-4 flex items-center gap-2">
                    <span
                      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${statusStyles[c.status] ?? ""}`}
                    >
                      {statusLabels[c.status] ?? c.status}
                    </span>
                    <span className="inline-flex rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                      {caseTypeLabels[c.case_type] ?? c.case_type}
                    </span>
                  </div>
                </div>
                <div className="mt-3 flex items-center gap-4 text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" />
                    {timeAgo(c.updated_at)}
                  </span>
                </div>
              </div>
            </Link>
          ))}

        {!isLoading && filtered.length === 0 && (
          <div className="py-12 text-center text-sm text-slate-400">No cases found</div>
        )}
      </div>
    </div>
  )
}
