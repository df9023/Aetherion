"use client"

import { ClipboardList, Loader2, RefreshCw } from "lucide-react"
import { cn } from "@/lib/utils"
import { MeetingBriefViewer } from "@/components/meeting-brief-viewer"
import type { MeetingBriefResponse } from "@/lib/hooks"

const GENERATION_STEPS = [
  "Analyzing pension situation",
  "Identifying key issues",
  "Building meeting agenda",
]

interface MeetingPrepCardProps {
  brief: MeetingBriefResponse | null
  isPending: boolean
  onGenerate: () => void
}

export function MeetingPrepCard({ brief, isPending, onGenerate }: MeetingPrepCardProps) {
  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
      <div className="flex items-center gap-2.5 border-b border-slate-100 px-5 py-4">
        <ClipboardList className="h-4 w-4 text-slate-500" />
        <h2 className="text-sm font-semibold text-slate-800">Meeting Preparation</h2>
      </div>

      {/* Empty state */}
      {!brief && !isPending && (
        <div className="flex flex-col items-center justify-center py-12">
          <ClipboardList className="mb-3 h-10 w-10 text-slate-200" />
          <p className="mb-1 text-sm font-medium text-slate-600">No brief prepared yet</p>
          <p className="mb-5 text-xs text-slate-400">Generate an AI-powered meeting brief for this case.</p>
          <button
            onClick={onGenerate}
            className="w-40 rounded-lg bg-sky-500 py-2 text-sm font-medium text-white transition-colors hover:bg-sky-600"
          >
            Prepare Meeting
          </button>
        </div>
      )}

      {/* Generating state */}
      {isPending && (
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="mb-4 h-7 w-7 animate-spin text-sky-500" />
          <div className="space-y-2">
            {GENERATION_STEPS.map((s, i) => (
              <div
                key={s}
                className={cn(
                  "flex items-center gap-2 text-sm transition-colors",
                  i === 0 ? "text-slate-700" : "text-slate-300"
                )}
              >
                <span
                  className={cn(
                    "h-1.5 w-1.5 rounded-full",
                    i === 0 ? "animate-pulse bg-sky-400" : "bg-slate-200"
                  )}
                />
                {s}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generated state */}
      {brief && !isPending && (
        <div className="space-y-6 px-5 py-5">
          <MeetingBriefViewer brief={brief} />

          <button
            onClick={onGenerate}
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white py-2 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Regenerate Brief
          </button>
        </div>
      )}
    </div>
  )
}
