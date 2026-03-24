"use client"

import { AlertTriangle, HelpCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import type { MeetingBriefResponse } from "@/lib/hooks"

const pillarBorders: Record<string, string> = {
  allmän_pension: "border-l-blue-500",
  tjänstepension: "border-l-emerald-500",
  privat_sparande: "border-l-violet-500",
}

const pillarBg: Record<string, string> = {
  allmän_pension: "bg-blue-50",
  tjänstepension: "bg-emerald-50",
  privat_sparande: "bg-violet-50",
}

const pillarLabels: Record<string, string> = {
  allmän_pension: "Allmän Pension",
  tjänstepension: "Tjänstepension",
  privat_sparande: "Privat Sparande",
}

const severityConfig: Record<string, { border: string; badge: string }> = {
  high: { border: "border-l-red-400", badge: "bg-red-50 text-red-700" },
  medium: { border: "border-l-amber-400", badge: "bg-amber-50 text-amber-700" },
  low: { border: "border-l-slate-300", badge: "bg-slate-100 text-slate-600" },
}

export function MeetingBriefViewer({ brief }: { brief: MeetingBriefResponse }) {
  const totalMinutes = brief.meeting_agenda.reduce((sum, a) => sum + a.duration_minutes, 0)

  return (
    <div className="space-y-6">
      {/* Client Overview */}
      <section>
        <p className="mb-2 text-[10px] font-medium uppercase tracking-wider text-slate-400">Client Overview</p>
        <p className="text-sm leading-relaxed text-slate-600 whitespace-pre-line">{brief.client_overview}</p>
      </section>

      {/* Pension Situation */}
      <section>
        <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Pension Situation</p>
        <div className="space-y-2">
          {brief.pension_situation.map((p) => (
            <div
              key={p.pillar}
              className={cn(
                "rounded-lg border-l-4 p-3",
                pillarBorders[p.pillar] ?? "border-l-slate-300",
                pillarBg[p.pillar] ?? "bg-slate-50"
              )}
            >
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold text-slate-700">
                  {pillarLabels[p.pillar] ?? p.pillar}
                </p>
                <span className="text-xs font-bold text-slate-800">{p.estimated_value}</span>
              </div>
              <p className="mt-1 text-xs leading-relaxed text-slate-500">{p.description}</p>
              {p.notes && (
                <p className="mt-1 text-[11px] text-slate-400">{p.notes}</p>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Key Issues */}
      {brief.key_issues.length > 0 && (
        <section>
          <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Key Issues</p>
          <div className="space-y-2">
            {brief.key_issues.map((issue, i) => {
              const cfg = severityConfig[issue.severity] ?? severityConfig.low
              return (
                <div
                  key={i}
                  className={cn("flex items-start gap-3 rounded-lg border-l-4 bg-slate-50 p-3", cfg.border)}
                >
                  <span className={cn("mt-0.5 shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase", cfg.badge)}>
                    {issue.severity}
                  </span>
                  <div>
                    <p className="text-xs font-medium text-slate-700">{issue.title}</p>
                    <p className="mt-0.5 text-xs leading-relaxed text-slate-500">{issue.description}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </section>
      )}

      {/* Scenarios */}
      {brief.pre_modeled_scenarios && brief.pre_modeled_scenarios.length > 0 && (
        <section>
          <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Scenarios</p>
          <div className="grid grid-cols-2 gap-3">
            {brief.pre_modeled_scenarios.map((s) => (
              <div key={s.name} className="rounded-lg border border-slate-200 p-3">
                <p className="text-xs font-semibold text-slate-700">{s.name}</p>
                <p className="mt-1 text-xs text-slate-500">{s.description}</p>
                {Object.keys(s.projected_outcome).length > 0 && (
                  <div className="mt-2 space-y-1">
                    {Object.entries(s.projected_outcome).map(([k, v]) => (
                      <div key={k} className="flex items-center justify-between text-xs">
                        <span className="text-slate-400">{k.replace(/_/g, " ")}</span>
                        <span className="font-medium text-slate-700">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Talking Points */}
      <section>
        <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Talking Points</p>
        <ol className="space-y-1.5">
          {brief.talking_points.map((t, i) => (
            <li key={i} className="flex items-start gap-2.5 text-xs text-slate-600">
              <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-sky-100 text-[10px] font-bold text-sky-600">
                {i + 1}
              </span>
              {t}
            </li>
          ))}
        </ol>
      </section>

      {/* Open Questions */}
      {brief.open_questions.length > 0 && (
        <section>
          <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-slate-400">Open Questions</p>
          <ul className="space-y-1.5">
            {brief.open_questions.map((q, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-slate-600">
                <HelpCircle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400" />
                {q}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Agenda */}
      <section>
        <div className="mb-3 flex items-center justify-between">
          <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">Agenda</p>
          <span className="text-xs font-medium text-slate-500">Total: {totalMinutes} min</span>
        </div>
        <div className="space-y-1">
          {brief.meeting_agenda.map((item, i) => (
            <div key={i} className="flex items-start gap-3 rounded-lg p-2 hover:bg-slate-50">
              <div className="flex flex-col items-center gap-1">
                <div className="h-2 w-2 rounded-full bg-sky-400" />
                {i < brief.meeting_agenda.length - 1 && <div className="h-6 w-px bg-slate-200" />}
              </div>
              <div className="flex-1 pb-1">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-medium text-slate-700">{item.topic}</p>
                  <span className="text-[10px] font-medium text-slate-400">{item.duration_minutes} min</span>
                </div>
                <p className="mt-0.5 text-[11px] text-slate-400">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
