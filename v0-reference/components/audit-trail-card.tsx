import { Cpu, User } from 'lucide-react'
import { cn } from '@/lib/utils'

const auditEvents = [
  { type: 'system', action: 'Case created automatically from CRM sync', time: '3 days ago' },
  { type: 'user', action: 'Advisor Erik Eriksson opened the case', time: '2 days ago' },
  { type: 'system', action: 'Client profile data refreshed from Collectum API', time: '2 days ago' },
  { type: 'system', action: 'AI Meeting Brief generated (v1)', time: 'Yesterday' },
  { type: 'user', action: 'Status changed: Draft → In Preparation', time: 'Yesterday' },
  { type: 'system', action: 'AI Recommendation generated (v2.4)', time: '4 hours ago' },
  { type: 'user', action: 'Advisor added a comment: "Confirmed meeting for Thursday"', time: '2 hours ago' },
]

export function AuditTrailCard() {
  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4">
        <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">Audit Trail</p>
      </div>
      <div className="px-5 py-4">
        <div className="relative space-y-0">
          <div className="absolute left-[15px] top-2 h-[calc(100%-16px)] w-px bg-slate-100" />
          {auditEvents.map((event, i) => (
            <div key={i} className="relative flex items-start gap-3 pb-4 last:pb-0">
              <div
                className={cn(
                  'relative z-10 mt-0.5 flex h-[18px] w-[18px] shrink-0 items-center justify-center rounded-full',
                  event.type === 'system'
                    ? 'bg-sky-500/10 ring-1 ring-sky-400'
                    : 'bg-slate-100 ring-1 ring-slate-300'
                )}
              >
                {event.type === 'system' ? (
                  <Cpu className="h-2.5 w-2.5 text-sky-500" />
                ) : (
                  <User className="h-2.5 w-2.5 text-slate-400" />
                )}
              </div>
              <div className="flex-1">
                <p className="text-xs leading-relaxed text-slate-600">{event.action}</p>
                <p className="mt-0.5 text-[10px] text-slate-400">{event.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
