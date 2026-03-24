'use client'

import { useState } from 'react'
import { Search, BookOpen, ChevronDown, ChevronUp } from 'lucide-react'
import { knowledge, getCategoryLabel, getCategoryColor, type KnowledgeCategory } from '@/lib/data'
import { Input } from '@/components/ui/input'
import { Topbar } from '@/components/topbar'

const categories: { value: KnowledgeCategory | 'all'; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'product_rule', label: 'Product Rules' },
  { value: 'internal_policy', label: 'Internal Policy' },
  { value: 'regulatory', label: 'Regulatory' },
  { value: 'playbook', label: 'Playbook' },
  { value: 'precedent', label: 'Precedent' },
  { value: 'faq', label: 'FAQ' },
  { value: 'process_guide', label: 'Process Guide' },
]

export default function KnowledgePage() {
  const [search, setSearch] = useState('')
  const [activeCategory, setActiveCategory] = useState<
    KnowledgeCategory | 'all'
  >('all')
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set())

  const filtered = knowledge.filter((item) => {
    const matchSearch =
      item.title.toLowerCase().includes(search.toLowerCase()) ||
      item.content.toLowerCase().includes(search.toLowerCase()) ||
      item.tags.some((tag) =>
        tag.toLowerCase().includes(search.toLowerCase())
      )

    const matchCategory =
      activeCategory === 'all' || item.category === activeCategory

    return matchSearch && matchCategory
  })

  const toggleExpanded = (idx: number) => {
    const newSet = new Set(expandedItems)
    if (newSet.has(idx)) {
      newSet.delete(idx)
    } else {
      newSet.add(idx)
    }
    setExpandedItems(newSet)
  }

  return (
    <>
      <Topbar breadcrumbs={[{ label: 'Knowledge Base' }]} />
      <main className="flex-1 bg-slate-50">
        <div className="mx-auto max-w-4xl px-6 py-8">
          {/* Header */}
          <h1 className="text-2xl font-semibold text-slate-900 mb-8">
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
                className="pl-10 bg-white border-slate-200/60"
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
                    ? 'bg-sky-500 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Knowledge items */}
          {filtered.length > 0 ? (
            <div className="space-y-3">
              {filtered.map((item, idx) => {
                const isExpanded = expandedItems.has(idx)
                const color = getCategoryColor(item.category)

                return (
                  <div
                    key={idx}
                    className="rounded-xl border border-slate-200/60 bg-white shadow-sm p-5 
                    hover:border-l-4 hover:border-l-sky-400 transition-all duration-200"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-semibold text-slate-900 mb-2">
                          {item.title}
                        </h3>

                        <div className="flex items-center gap-2 mb-3 flex-wrap">
                          <div
                            className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${color.bg} ${color.text}`}
                          >
                            {getCategoryLabel(item.category)}
                          </div>
                          <p className="text-xs text-slate-400">
                            {item.source}
                          </p>
                        </div>

                        <div className="flex flex-wrap gap-1 mb-3">
                          {item.tags.map((tag, tagIdx) => (
                            <span
                              key={tagIdx}
                              className="inline-flex px-1.5 py-0.5 rounded text-[10px] bg-slate-100 text-slate-500"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>

                        <p
                          className={`text-sm text-slate-600 ${
                            !isExpanded ? 'line-clamp-3' : ''
                          }`}
                        >
                          {item.content}
                        </p>

                        <button
                          onClick={() => toggleExpanded(idx)}
                          className="mt-2 text-xs font-medium text-sky-600 hover:text-sky-700"
                        >
                          {isExpanded ? 'Show less' : 'Show more'}
                        </button>
                      </div>

                      <button
                        onClick={() => toggleExpanded(idx)}
                        className="flex-shrink-0 text-slate-400 hover:text-slate-600"
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
            <div className="flex flex-col items-center justify-center py-12">
              <BookOpen className="h-12 w-12 text-slate-300 mb-3" />
              <p className="text-slate-600 font-medium mb-1">
                No knowledge items found
              </p>
              <p className="text-slate-400 text-sm">
                Try adjusting your search or category filter
              </p>
            </div>
          )}
        </div>
      </main>
    </>
  )
}
