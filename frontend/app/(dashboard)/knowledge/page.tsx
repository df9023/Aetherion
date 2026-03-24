"use client"

import { useState } from "react"
import { Search, BookOpen, ChevronDown, ChevronUp } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { useKnowledge } from "@/lib/hooks"
import type { KnowledgeItemResponse } from "@/lib/hooks"
import { categoryStyles, categoryLabels } from "@/lib/labels"
import { TopBar } from "@/components/top-bar"

const categories = [
  { value: "all", label: "All" },
  { value: "product_rule", label: "Product Rules" },
  { value: "internal_policy", label: "Internal Policy" },
  { value: "regulatory_requirement", label: "Regulatory" },
  { value: "playbook", label: "Playbook" },
  { value: "precedent", label: "Precedent" },
  { value: "faq", label: "FAQ" },
  { value: "process_guide", label: "Process Guide" },
]

export default function KnowledgePage() {
  const { data: knowledge, isLoading } = useKnowledge()
  const [search, setSearch] = useState("")
  const [activeCategory, setActiveCategory] = useState("all")
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())

  const filtered = (knowledge ?? []).filter((item) => {
    const matchSearch =
      !search ||
      item.title.toLowerCase().includes(search.toLowerCase()) ||
      item.content.toLowerCase().includes(search.toLowerCase()) ||
      item.tags.some((tag) => tag.toLowerCase().includes(search.toLowerCase()))

    const matchCategory = activeCategory === "all" || item.category === activeCategory

    return matchSearch && matchCategory
  })

  const toggleExpanded = (id: string) => {
    const newSet = new Set(expandedItems)
    if (newSet.has(id)) {
      newSet.delete(id)
    } else {
      newSet.add(id)
    }
    setExpandedItems(newSet)
  }

  return (
    <>
      <TopBar breadcrumbs={[{ label: "Knowledge Base" }]} />
      <main className="flex-1 bg-slate-50">
        <div className="mx-auto max-w-4xl px-6 py-8">
          {/* Header */}
          <h1 className="mb-8 text-2xl font-semibold text-slate-900">
            Knowledge Base
          </h1>

          {/* Search */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search knowledge..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-white border-slate-200/60 pl-10"
                data-search-input
              />
            </div>
          </div>

          {/* Category filter pills */}
          <div className="mb-8 flex flex-wrap gap-2">
            {categories.map((cat) => (
              <button
                key={cat.value}
                onClick={() => setActiveCategory(cat.value)}
                className={`rounded-full px-3 py-1 text-xs font-medium transition-all ${
                  activeCategory === cat.value
                    ? "bg-sky-500 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Loading skeletons */}
          {isLoading && (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm">
                  <Skeleton className="h-4 w-2/3" />
                  <Skeleton className="mt-2 h-3 w-1/4" />
                  <Skeleton className="mt-3 h-12 w-full" />
                </div>
              ))}
            </div>
          )}

          {/* Knowledge items */}
          {!isLoading && filtered.length > 0 ? (
            <div className="space-y-3">
              {filtered.map((item) => {
                const isExpanded = expandedItems.has(item.id)

                return (
                  <div
                    key={item.id}
                    className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm transition-all duration-200 hover:border-l-4 hover:border-l-sky-400"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0 flex-1">
                        <h3 className="mb-2 text-sm font-semibold text-slate-900">
                          {item.title}
                        </h3>

                        <div className="mb-3 flex flex-wrap items-center gap-2">
                          <div
                            className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${
                              categoryStyles[item.category] ?? "bg-slate-100 text-slate-600"
                            }`}
                          >
                            {categoryLabels[item.category] ?? item.category}
                          </div>
                          <p className="text-xs text-slate-400">
                            {item.source}
                          </p>
                        </div>

                        <div className="mb-3 flex flex-wrap gap-1">
                          {item.tags.map((tag, tagIdx) => (
                            <span
                              key={tagIdx}
                              className="inline-flex rounded px-1.5 py-0.5 text-[10px] bg-slate-100 text-slate-500"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>

                        <p className={`text-sm text-slate-600 ${!isExpanded ? "line-clamp-3" : ""}`}>
                          {item.content}
                        </p>

                        <button
                          onClick={() => toggleExpanded(item.id)}
                          className="mt-2 text-xs font-medium text-sky-600 hover:text-sky-700"
                        >
                          {isExpanded ? "Show less" : "Show more"}
                        </button>
                      </div>

                      <button
                        onClick={() => toggleExpanded(item.id)}
                        className="shrink-0 text-slate-400 hover:text-slate-600"
                      >
                        {isExpanded ? (
                          <ChevronUp className="h-5 w-5" />
                        ) : (
                          <ChevronDown className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            !isLoading && (
              <div className="flex flex-col items-center justify-center py-12">
                <BookOpen className="mb-3 h-12 w-12 text-slate-300" />
                <p className="mb-1 font-medium text-slate-600">
                  No knowledge items found
                </p>
                <p className="text-sm text-slate-400">
                  Try adjusting your search or category filter
                </p>
              </div>
            )
          )}
        </div>
      </main>
    </>
  )
}
