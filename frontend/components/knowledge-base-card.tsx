"use client"

import { Search, ChevronDown, ChevronRight } from "lucide-react"
import { useState } from "react"
import { cn } from "@/lib/utils"
import { categoryStyles, categoryLabels } from "@/lib/labels"
import type { KnowledgeItemResponse } from "@/lib/hooks"

interface KnowledgeBaseCardProps {
  query: string
  onQueryChange: (value: string) => void
  results: KnowledgeItemResponse[] | undefined
  minQueryLength?: number
}

export function KnowledgeBaseCard({ query, onQueryChange, results, minQueryLength = 2 }: KnowledgeBaseCardProps) {
  const [expanded, setExpanded] = useState<string | null>(null)

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
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            className="flex-1 bg-transparent text-xs text-slate-700 placeholder:text-slate-400 focus:outline-none"
          />
        </div>
      </div>
      <div className="divide-y divide-slate-100">
        {results && results.length > 0 ? (
          results.map((item) => {
            const isOpen = expanded === item.id
            return (
              <div key={item.id}>
                <button
                  onClick={() => setExpanded(isOpen ? null : item.id)}
                  className="flex w-full items-start justify-between gap-3 px-5 py-3.5 text-left hover:bg-slate-50"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={cn(
                          "shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium",
                          categoryStyles[item.category] ?? "bg-slate-100 text-slate-600"
                        )}
                      >
                        {categoryLabels[item.category] ?? item.category}
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
        ) : query.length >= minQueryLength ? (
          <p className="px-5 py-6 text-center text-xs text-slate-400">No results found.</p>
        ) : (
          <p className="px-5 py-6 text-center text-xs text-slate-400">Type to search knowledge base...</p>
        )}
      </div>
    </div>
  )
}
