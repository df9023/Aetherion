"use client"

import { ClipboardList, Loader2, RefreshCw } from "lucide-react"
import { cn } from "@/lib/utils"
import { MeetingBriefViewer } from "@/components/meeting-brief-viewer"
import type { MeetingBriefResponse } from "@/lib/hooks"

const GENERATION_STEPS = [
  "Analyserar pensionssituation",
  "Identifierar nyckelfrågor",
  "Bygger mötesagenda",
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
        <ClipboardList className="h-5 w-5 text-slate-500" />
        <h2 className="text-base font-semibold text-slate-800">Mötesförberedelse</h2>
      </div>

      {/* Empty state */}
      {!brief && !isPending && (
        <div className="flex flex-col items-center justify-center py-12">
          <ClipboardList className="mb-3 h-12 w-12 text-slate-200" />
          <p className="mb-1 text-base font-medium text-slate-600">Inget mötesunderlag förberett</p>
          <p className="mb-5 text-sm text-slate-400">Generera ett AI-drivet mötesunderlag för detta ärende.</p>
          <button
            onClick={onGenerate}
            className="rounded-lg bg-sky-500 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-sky-600"
          >
            Förbered möte
          </button>
        </div>
      )}

      {/* Generating state */}
      {isPending && (
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="mb-4 h-8 w-8 animate-spin text-sky-500" />
          <div className="space-y-3">
            {GENERATION_STEPS.map((s, i) => (
              <div
                key={s}
                className={cn(
                  "flex items-center gap-2.5 text-sm transition-colors",
                  i === 0 ? "text-slate-700" : "text-slate-300"
                )}
              >
                <span
                  className={cn(
                    "h-2 w-2 rounded-full",
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
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white py-2.5 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50"
          >
            <RefreshCw className="h-4 w-4" />
            Generera nytt underlag
          </button>
        </div>
      )}
    </div>
  )
}
