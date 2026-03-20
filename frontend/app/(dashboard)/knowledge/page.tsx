"use client"

import { useState } from "react"
import { Search, BookOpen } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useKnowledge } from "@/lib/hooks"
import type { KnowledgeItemResponse } from "@/lib/hooks"
import { categoryStyles, categoryLabels } from "@/lib/labels"

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

function KnowledgeItem({ item }: { item: KnowledgeItemResponse }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="rounded-xl border border-l-4 border-slate-200/60 border-l-transparent bg-white p-5 shadow-sm transition-all duration-200 hover:border-l-sky-400 hover:border-slate-300 hover:shadow-md">
      <div className="flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-semibold text-slate-900">{item.title}</h3>
          <div className="mt-2 flex items-center gap-2">
            <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${categoryStyles[item.category] ?? "bg-slate-100 text-slate-600"}`}>
              {categoryLabels[item.category] ?? item.category}
            </span>
            <span className="text-xs text-slate-400">{item.source}</span>
          </div>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-1">
        {item.tags.map((t) => (
          <span key={t} className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500">
            {t}
          </span>
        ))}
      </div>

      <p className={`mt-3 text-sm leading-relaxed text-slate-600 ${expanded ? "" : "line-clamp-3"}`}>
        {item.content}
      </p>

      <button
        onClick={() => setExpanded(!expanded)}
        className="mt-2 text-xs font-medium text-sky-500 hover:text-sky-600"
      >
        {expanded ? "Show less" : "Show more"}
      </button>
    </div>
  )
}

export default function KnowledgePage() {
  const { data: knowledge, isLoading } = useKnowledge()
  const [search, setSearch] = useState("")
  const [tab, setTab] = useState("all")

  const filtered = (knowledge ?? []).filter((k) => {
    if (tab !== "all" && k.category !== tab) return false
    if (search && !k.title.toLowerCase().includes(search.toLowerCase()) && !k.content.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <div className="animate-[fadeIn_0.3s_ease-out]">
      <h1 className="text-2xl font-semibold text-slate-900">Knowledge Base</h1>

      <div className="relative mt-6 max-w-xl">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <Input
          placeholder="Search knowledge base..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
          data-search-input
        />
      </div>

      <Tabs value={tab} onValueChange={setTab} className="mt-6">
        <TabsList className="bg-slate-100">
          {categories.map((c) => (
            <TabsTrigger key={c.value} value={c.value} className="text-xs">
              {c.label}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value={tab} className="mt-6">
          <div className="space-y-4">
            {isLoading &&
              Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm">
                  <Skeleton className="h-4 w-2/3" />
                  <Skeleton className="mt-2 h-3 w-1/4" />
                  <Skeleton className="mt-3 h-12 w-full" />
                </div>
              ))}
            {!isLoading && filtered.map((k) => (
              <KnowledgeItem key={k.id} item={k} />
            ))}
            {!isLoading && filtered.length === 0 && (
              <div className="flex flex-col items-center py-16">
                <BookOpen className="h-12 w-12 text-slate-300" />
                <p className="mt-4 text-sm font-medium text-slate-600">No knowledge items found</p>
                <p className="mt-1 text-xs text-slate-400">Try adjusting your search or category filter</p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
