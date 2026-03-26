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
        <h3 className="text-sm font-semibold text-slate-700">Kunskapsbas</h3>
        <div className="mt-3 flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
          <Search className="h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Sök i kunskapsbasen..."
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            className="flex-1 bg-transparent text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none"
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
                  className="flex w-full items-start justify-between gap-3 px-5 py-4 text-left hover:bg-slate-50"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={cn(
                          "shrink-0 rounded-full px-2 py-0.5 text-xs font-medium",
                          categoryStyles[item.category] ?? "bg-slate-100 text-slate-600"
                        )}
                      >
                        {categoryLabels[item.category] ?? item.category}
                      </span>
                      <p className="text-sm font-medium text-slate-700">{item.title}</p>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {item.tags.map((tag) => (
                        <span key={tag} className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-500">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  {isOpen ? (
                    <ChevronDown className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
                  ) : (
                    <ChevronRight className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
                  )}
                </button>
                {isOpen && (
                  <div className="border-t border-slate-100 bg-slate-50 px-5 py-4">
                    <p className="text-sm leading-relaxed text-slate-600">{item.content}</p>
                  </div>
                )}
              </div>
            )
          })
        ) : query.length >= minQueryLength ? (
          <p className="px-5 py-6 text-center text-sm text-slate-400">Inga resultat hittades.</p>
        ) : (
          <p className="px-5 py-6 text-center text-sm text-slate-400">Skriv för att söka i kunskapsbasen...</p>
        )}
      </div>
    </div>
  )
}
