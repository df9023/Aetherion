"use client"

import { Cpu, User } from "lucide-react"
import { cn } from "@/lib/utils"
import { auditActionLabels } from "@/lib/labels"
import type { AuditEntryResponse } from "@/lib/hooks"

interface AuditTrailCardProps {
  entries: AuditEntryResponse[]
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("sv-SE", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

export function AuditTrailCard({ entries }: AuditTrailCardProps) {
  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4">
        <h3 className="text-sm font-semibold text-slate-700">Granskningslogg</h3>
      </div>
      <div className="px-5 py-4">
        {entries.length === 0 ? (
          <p className="py-4 text-center text-sm text-slate-400">Inga loggposter</p>
        ) : (
          <div className="relative space-y-0">
            <div className="absolute left-[15px] top-2 h-[calc(100%-16px)] w-px bg-slate-100" />
            {entries.map((event) => (
              <div key={event.id} className="relative flex items-start gap-3 pb-4 last:pb-0">
                <div
                  className={cn(
                    "relative z-10 mt-0.5 flex h-[22px] w-[22px] shrink-0 items-center justify-center rounded-full",
                    event.actor_type === "system"
                      ? "bg-sky-500/10 ring-1 ring-sky-400"
                      : "bg-slate-100 ring-1 ring-slate-300"
                  )}
                >
                  {event.actor_type === "system" ? (
                    <Cpu className="h-3 w-3 text-sky-500" />
                  ) : (
                    <User className="h-3 w-3 text-slate-400" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-sm leading-relaxed text-slate-600">
                    {auditActionLabels[event.action] ?? event.action}
                  </p>
                  <p className="mt-0.5 text-xs text-slate-400">{formatDate(event.timestamp)}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
