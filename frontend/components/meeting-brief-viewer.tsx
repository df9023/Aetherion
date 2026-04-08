"use client"

import { HelpCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import { severityLabels } from "@/lib/labels"
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
  allmän_pension: "Allmän pension",
  tjänstepension: "Tjänstepension",
  privat_sparande: "Privat sparande",
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
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Klientöversikt</h3>
        <p className="text-sm leading-relaxed text-slate-600 whitespace-pre-line">{brief.client_overview}</p>
      </section>

      {/* Pension Situation */}
      <section>
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Pensionssituation</h3>
        <div className="space-y-2">
          {brief.pension_situation.map((p) => (
            <div
              key={p.pillar}
              className={cn(
                "rounded-lg border-l-4 p-4",
                pillarBorders[p.pillar] ?? "border-l-slate-300",
                pillarBg[p.pillar] ?? "bg-slate-50"
              )}
            >
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-slate-700">
                  {pillarLabels[p.pillar] ?? p.pillar}
                </p>
                <span className="text-sm font-bold text-slate-800">{p.estimated_value}</span>
              </div>
              <p className="mt-1 text-sm leading-relaxed text-slate-500">{p.description}</p>
              {p.notes && (
                <p className="mt-1 text-xs text-slate-400">{p.notes}</p>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Key Issues */}
      {brief.key_issues.length > 0 && (
        <section>
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Nyckelfrågor</h3>
          <div className="space-y-2">
            {brief.key_issues.map((issue, i) => {
              const cfg = severityConfig[issue.severity] ?? severityConfig.low
              return (
                <div
                  key={i}
                  className={cn("flex items-start gap-3 rounded-lg border-l-4 bg-slate-50 p-4", cfg.border)}
                >
                  <span className={cn("mt-0.5 shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase", cfg.badge)}>
                    {severityLabels[issue.severity] ?? issue.severity}
                  </span>
                  <div>
                    <p className="text-sm font-medium text-slate-700">{issue.title}</p>
                    <p className="mt-0.5 text-sm leading-relaxed text-slate-500">{issue.description}</p>
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
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Scenarion</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            {brief.pre_modeled_scenarios.map((s) => (
              <div key={s.name} className="rounded-lg border border-slate-200 p-4">
                <p className="text-sm font-semibold text-slate-700">{s.name}</p>
                <p className="mt-1 text-sm text-slate-500">{s.description}</p>
                {Object.keys(s.projected_outcome).length > 0 && (
                  <div className="mt-2.5 space-y-1">
                    {Object.entries(s.projected_outcome).map(([k, v]) => (
                      <div key={k} className="flex items-center justify-between text-sm">
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
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Samtalspunkter</h3>
        <ol className="space-y-2">
          {brief.talking_points.map((t, i) => (
            <li key={i} className="flex items-start gap-3 text-sm text-slate-600">
              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-sky-100 text-xs font-bold text-sky-600">
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
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Öppna frågor</h3>
          <ul className="space-y-2">
            {brief.open_questions.map((q, i) => (
              <li key={i} className="flex items-start gap-2.5 text-sm text-slate-600">
                <HelpCircle className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
                {q}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Agenda */}
      <section>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Agenda</h3>
          <span className="text-sm font-medium text-slate-500">Totalt: {totalMinutes} min</span>
        </div>
        <div className="space-y-1">
          {brief.meeting_agenda.map((item, i) => (
            <div key={i} className="flex items-start gap-3 rounded-lg p-2.5 hover:bg-slate-50">
              <div className="flex flex-col items-center gap-1">
                <div className="h-2.5 w-2.5 rounded-full bg-sky-400" />
                {i < brief.meeting_agenda.length - 1 && <div className="h-7 w-px bg-slate-200" />}
              </div>
              <div className="flex-1 pb-1">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-slate-700">{item.topic}</p>
                  <span className="text-xs font-medium text-slate-400">{item.duration_minutes} min</span>
                </div>
                <p className="mt-0.5 text-xs text-slate-400">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
