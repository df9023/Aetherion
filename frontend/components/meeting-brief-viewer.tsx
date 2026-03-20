"use client"

import {
  Clock,
  AlertTriangle,
  HelpCircle,
  MessageSquare,
  BarChart3,
} from "lucide-react"
import { Separator } from "@/components/ui/separator"
import type { MeetingBriefResponse } from "@/lib/hooks"

const pillarLabels: Record<string, string> = {
  allmän_pension: "Allmän Pension",
  tjänstepension: "Tjänstepension",
  privat_sparande: "Privat Sparande",
}

const pillarStyles: Record<string, string> = {
  allmän_pension: "border-blue-200 bg-blue-50/50",
  tjänstepension: "border-green-200 bg-green-50/50",
  privat_sparande: "border-violet-200 bg-violet-50/50",
}

const pillarAccent: Record<string, string> = {
  allmän_pension: "text-blue-700",
  tjänstepension: "text-green-700",
  privat_sparande: "text-violet-700",
}

const severityStyles: Record<string, string> = {
  high: "bg-red-50 text-red-700 border-red-200",
  medium: "bg-amber-50 text-amber-700 border-amber-200",
  low: "bg-slate-100 text-slate-600 border-slate-200",
}

const severityLabels: Record<string, string> = {
  high: "High",
  medium: "Medium",
  low: "Low",
}

export function MeetingBriefViewer({ brief }: { brief: MeetingBriefResponse }) {
  const totalMinutes = brief.meeting_agenda.reduce((sum, a) => sum + a.duration_minutes, 0)

  return (
    <div className="space-y-6">
      {/* Client Overview */}
      <div>
        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Client Overview</p>
        <p className="mt-2 text-sm leading-relaxed text-slate-600 whitespace-pre-line">{brief.client_overview}</p>
      </div>

      <Separator />

      {/* Pension Situation — Three Pillars */}
      <div>
        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Pension Situation</p>
        <div className="mt-4 grid grid-cols-1 gap-3 lg:grid-cols-3">
          {brief.pension_situation.map((p) => (
            <div
              key={p.pillar}
              className={`rounded-lg border p-4 ${pillarStyles[p.pillar] ?? "border-slate-200 bg-slate-50/50"}`}
            >
              <p className={`text-sm font-semibold ${pillarAccent[p.pillar] ?? "text-slate-900"}`}>
                {pillarLabels[p.pillar] ?? p.pillar}
              </p>
              <p className="mt-2 text-xs leading-relaxed text-slate-600">{p.description}</p>
              <div className="mt-3 flex items-center justify-between">
                <span className="text-[10px] uppercase tracking-wider text-slate-400">Estimated</span>
                <span className="text-sm font-semibold text-slate-900">{p.estimated_value}</span>
              </div>
              {p.notes && (
                <p className="mt-2 rounded bg-white/60 p-2 text-[11px] text-slate-500">{p.notes}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      <Separator />

      {/* Key Issues */}
      {brief.key_issues.length > 0 && (
        <>
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Key Issues</p>
            <div className="mt-4 space-y-3">
              {brief.key_issues.map((issue, i) => (
                <div key={i} className="rounded-lg border border-slate-100 p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-2">
                      <AlertTriangle className={`mt-0.5 h-4 w-4 shrink-0 ${
                        issue.severity === "high" ? "text-red-500" : issue.severity === "medium" ? "text-amber-500" : "text-slate-400"
                      }`} />
                      <p className="text-sm font-medium text-slate-900">{issue.title}</p>
                    </div>
                    <span className={`inline-flex rounded-full border px-2 py-0.5 text-[10px] font-medium ${severityStyles[issue.severity] ?? ""}`}>
                      {severityLabels[issue.severity] ?? issue.severity}
                    </span>
                  </div>
                  <p className="mt-2 ml-6 text-xs leading-relaxed text-slate-500">{issue.description}</p>
                </div>
              ))}
            </div>
          </div>
          <Separator />
        </>
      )}

      {/* Pre-modeled Scenarios */}
      {brief.pre_modeled_scenarios && brief.pre_modeled_scenarios.length > 0 && (
        <>
          <div>
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-slate-400" />
              <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Pre-modeled Scenarios</p>
            </div>
            <div className="mt-4 grid grid-cols-1 gap-3 lg:grid-cols-2">
              {brief.pre_modeled_scenarios.map((s) => (
                <div key={s.name} className="rounded-lg border border-slate-100 bg-slate-50/50 p-4">
                  <p className="text-sm font-semibold text-slate-900">{s.name}</p>
                  <p className="mt-1 text-xs text-slate-500">{s.description}</p>
                  <div className="mt-3 space-y-1.5">
                    {Object.entries(s.projected_outcome).map(([k, v]) => (
                      <div key={k} className="flex items-center justify-between text-xs">
                        <span className="text-slate-400">{k.replace(/_/g, " ")}</span>
                        <span className="font-medium text-slate-700">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <Separator />
        </>
      )}

      {/* Talking Points */}
      <div>
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-slate-400" />
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Talking Points</p>
        </div>
        <ol className="mt-4 space-y-2">
          {brief.talking_points.map((point, i) => (
            <li key={i} className="flex gap-3">
              <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-sky-500 text-[10px] font-bold text-white">
                {i + 1}
              </span>
              <p className="text-sm text-slate-600">{point}</p>
            </li>
          ))}
        </ol>
      </div>

      <Separator />

      {/* Open Questions */}
      {brief.open_questions.length > 0 && (
        <>
          <div>
            <div className="flex items-center gap-2">
              <HelpCircle className="h-4 w-4 text-slate-400" />
              <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Questions to Ask</p>
            </div>
            <ul className="mt-4 space-y-2">
              {brief.open_questions.map((q, i) => (
                <li key={i} className="flex gap-2 text-sm text-slate-600">
                  <span className="shrink-0 text-slate-300">?</span>
                  {q}
                </li>
              ))}
            </ul>
          </div>
          <Separator />
        </>
      )}

      {/* Meeting Agenda */}
      <div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-slate-400" />
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Meeting Agenda</p>
          </div>
          <span className="text-xs text-slate-400">{totalMinutes} min total</span>
        </div>
        <div className="mt-4 space-y-0">
          {brief.meeting_agenda.map((item, i) => (
            <div key={i} className="relative flex gap-4 pb-4 last:pb-0">
              {i < brief.meeting_agenda.length - 1 && (
                <div className="absolute left-[19px] top-8 h-[calc(100%-16px)] w-px bg-slate-200" />
              )}
              <div className="relative z-10 flex h-10 w-10 shrink-0 flex-col items-center justify-center rounded-lg bg-slate-100">
                <span className="text-xs font-bold text-slate-700">{item.duration_minutes}</span>
                <span className="text-[8px] text-slate-400">min</span>
              </div>
              <div className="min-w-0 flex-1 pt-0.5">
                <p className="text-sm font-medium text-slate-900">{item.topic}</p>
                <p className="mt-0.5 text-xs text-slate-500">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
