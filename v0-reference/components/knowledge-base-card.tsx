'use client'

import { useState } from 'react'
import { Search, ChevronDown, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

const kbItems = [
  {
    title: 'ITP1 Plan Document 2024 — Collectum',
    category: 'Product',
    tags: ['ITP1', 'collectum', 'occupational'],
    content:
      'Collectum administers ITP1 on behalf of participating employers. Employees can choose from approved fund providers and must review their fund selection annually. The plan is premium-defined at 4.5% of salary up to 7.5 IBB and 30% above.',
  },
  {
    title: 'FFFS 2007:16 — Suitability Assessment Requirements',
    category: 'Regulation',
    tags: ['suitability', 'FFFS', 'Finansinspektionen'],
    content:
      'Advisors are required to assess customer suitability before providing investment advice. This includes documenting financial situation, investment knowledge, objectives and risk tolerance. All assessments must be kept for at least 5 years.',
  },
  {
    title: 'Löneväxling — SPP Internal Policy 2024',
    category: 'Policy',
    tags: ['salary exchange', 'SPP', 'tax'],
    content:
      'Salary exchange (löneväxling) allows employees to reduce their gross salary in exchange for higher employer pension contributions. Tax benefits apply up to 35% of income base amount. Employer social security savings can partially offset the cost.',
  },
  {
    title: 'Efterlevandeskydd — Guide for Advisors',
    category: 'Guide',
    tags: ['survivor protection', 'family', 'ITP'],
    content:
      'Survivor protection ensures dependents receive benefits upon the policyholder\'s death. Available as both term coverage and capital protection. Advisors should document whether clients have assessed this need.',
  },
]

const categoryColors: Record<string, string> = {
  Product: 'bg-blue-50 text-blue-700',
  Regulation: 'bg-red-50 text-red-700',
  Policy: 'bg-emerald-50 text-emerald-700',
  Guide: 'bg-violet-50 text-violet-700',
}

export function KnowledgeBaseCard() {
  const [search, setSearch] = useState('')
  const [expanded, setExpanded] = useState<string | null>(null)

  const filtered = kbItems.filter((item) => {
    if (!search) return true
    const q = search.toLowerCase()
    return (
      item.title.toLowerCase().includes(q) ||
      item.category.toLowerCase().includes(q) ||
      item.tags.some((t) => t.toLowerCase().includes(q))
    )
  })

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4">
        <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
          Knowledge Base
        </p>
        <div className="mt-3 flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
          <Search className="h-3.5 w-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search knowledge base..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-transparent text-xs text-slate-700 placeholder:text-slate-400 focus:outline-none"
          />
        </div>
      </div>
      <div className="divide-y divide-slate-100">
        {filtered.length === 0 ? (
          <p className="px-5 py-6 text-center text-xs text-slate-400">No results found.</p>
        ) : (
          filtered.map((item) => {
            const isOpen = expanded === item.title
            return (
              <div key={item.title}>
                <button
                  onClick={() => setExpanded(isOpen ? null : item.title)}
                  className="flex w-full items-start justify-between gap-3 px-5 py-3.5 text-left hover:bg-slate-50"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={cn(
                          'shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium',
                          categoryColors[item.category] ?? 'bg-slate-100 text-slate-600'
                        )}
                      >
                        {item.category}
                      </span>
                      <p className="text-xs font-medium text-slate-700">{item.title}</p>
                    </div>
                    <div className="mt-1.5 flex flex-wrap gap-1">
                      {item.tags.map((tag) => (
                        <span key={tag} className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  {isOpen ? (
                    <ChevronDown className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400" />
                  ) : (
                    <ChevronRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400" />
                  )}
                </button>
                {isOpen && (
                  <div className="border-t border-slate-100 bg-slate-50 px-5 py-3">
                    <p className="text-xs leading-relaxed text-slate-600">{item.content}</p>
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
