"use client"

import { useState, useCallback, useRef, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import { Search, BookOpen, ChevronDown, ChevronUp, Upload, X, FileText, Loader2, Check } from "lucide-react"
import { toast } from "sonner"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { useKnowledge, useIngestKnowledge } from "@/lib/hooks"
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

const uploadCategories = categories.filter((c) => c.value !== "all")

type UploadPhase = "idle" | "extracting" | "chunking" | "embedding" | "done"

function UploadDialog({ onClose }: { onClose: () => void }) {
  const ingest = useIngestKnowledge()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [category, setCategory] = useState("product_rule")
  const [source, setSource] = useState("")
  const [tags, setTags] = useState("")
  const [phase, setPhase] = useState<UploadPhase>("idle")
  const [result, setResult] = useState<{ items_created: number } | null>(null)

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const dropped = e.dataTransfer.files[0]
    if (dropped?.name.toLowerCase().endsWith(".pdf")) {
      setFile(dropped)
    } else {
      toast.error("Only PDF files are supported")
    }
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0]
    if (selected) setFile(selected)
  }, [])

  const handleUpload = useCallback(() => {
    if (!file || !source.trim()) return

    // Simulate phase progression for UX
    setPhase("extracting")
    const t1 = setTimeout(() => setPhase("chunking"), 1200)
    const t2 = setTimeout(() => setPhase("embedding"), 2400)

    ingest.mutate(
      { file, category, source: source.trim(), tags },
      {
        onSuccess: (data) => {
          clearTimeout(t1)
          clearTimeout(t2)
          setPhase("done")
          setResult(data)
          toast.success(`${data.items_created} knowledge items created`)
        },
        onError: (err) => {
          clearTimeout(t1)
          clearTimeout(t2)
          setPhase("idle")
          toast.error(err.message)
        },
      },
    )
  }, [file, category, source, tags, ingest])

  const phaseLabel: Record<UploadPhase, string> = {
    idle: "",
    extracting: "Extracting text from PDF...",
    chunking: "Chunking document into sections...",
    embedding: "Generating embeddings...",
    done: "",
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onClose}>
      <div
        className="w-full max-w-lg rounded-xl border border-slate-200 bg-white shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <h3 className="text-sm font-semibold text-slate-800">Upload Knowledge Document</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="space-y-4 px-5 py-5">
          {phase === "done" && result ? (
            <div className="flex flex-col items-center py-6">
              <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50">
                <Check className="h-6 w-6 text-emerald-600" />
              </div>
              <p className="text-sm font-medium text-slate-700">
                {result.items_created} knowledge items created
              </p>
              <p className="mt-1 text-xs text-slate-400">
                The items are now searchable in the knowledge base.
              </p>
              <button
                onClick={onClose}
                className="mt-5 rounded-lg bg-sky-500 px-6 py-2 text-sm font-medium text-white hover:bg-sky-600"
              >
                Done
              </button>
            </div>
          ) : (
            <>
              {/* File dropzone */}
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className="flex cursor-pointer flex-col items-center rounded-lg border-2 border-dashed border-slate-200 px-4 py-8 transition-colors hover:border-sky-300 hover:bg-sky-50/30"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                {file ? (
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-sky-500" />
                    <span className="text-sm font-medium text-slate-700">{file.name}</span>
                    <span className="text-xs text-slate-400">
                      ({(file.size / 1024).toFixed(0)} KB)
                    </span>
                  </div>
                ) : (
                  <>
                    <Upload className="mb-2 h-8 w-8 text-slate-300" />
                    <p className="text-sm text-slate-500">
                      Drop a PDF here or click to browse
                    </p>
                  </>
                )}
              </div>

              {/* Category */}
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-sky-300 focus:ring-1 focus:ring-sky-300"
                >
                  {uploadCategories.map((c) => (
                    <option key={c.value} value={c.value}>
                      {c.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Source */}
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">Source</label>
                <Input
                  placeholder='e.g., "Collectum — ITP1-avtalet 2024"'
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  className="border-slate-200"
                />
              </div>

              {/* Tags */}
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">
                  Tags <span className="text-slate-400">(comma-separated, optional)</span>
                </label>
                <Input
                  placeholder="e.g., ITP1, collectum, 2024"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  className="border-slate-200"
                />
              </div>

              {/* Processing state */}
              {phase !== "idle" && (
                <div className="flex items-center gap-2 rounded-lg bg-sky-50 px-3 py-2">
                  <Loader2 className="h-4 w-4 animate-spin text-sky-500" />
                  <span className="text-xs text-sky-700">{phaseLabel[phase]}</span>
                </div>
              )}

              {/* Submit */}
              <button
                onClick={handleUpload}
                disabled={!file || !source.trim() || phase !== "idle"}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-sky-500 py-2.5 text-sm font-medium text-white transition-colors hover:bg-sky-600 disabled:opacity-50"
              >
                <Upload className="h-4 w-4" />
                Upload &amp; Process
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function KnowledgePageContent() {
  const searchParams = useSearchParams()
  const highlightId = searchParams.get("highlight")
  const { data: knowledge, isLoading } = useKnowledge()
  const [search, setSearch] = useState("")
  const [activeCategory, setActiveCategory] = useState("all")
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())
  const [showUpload, setShowUpload] = useState(false)
  const highlightedRef = useRef<HTMLDivElement>(null)
  const didScroll = useRef(false)

  // Auto-expand and scroll to highlighted item
  useEffect(() => {
    if (highlightId && knowledge && !didScroll.current) {
      setExpandedItems((prev) => new Set(prev).add(highlightId))
      // Small delay to let DOM render
      const timer = setTimeout(() => {
        const el = document.getElementById(`knowledge-${highlightId}`)
        if (el) {
          el.scrollIntoView({ behavior: "smooth", block: "center" })
          didScroll.current = true
        }
      }, 150)
      return () => clearTimeout(timer)
    }
  }, [highlightId, knowledge])

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
          <div className="mb-8 flex items-center justify-between">
            <h1 className="text-2xl font-semibold text-slate-900">
              Knowledge Base
            </h1>
            <button
              onClick={() => setShowUpload(true)}
              className="flex items-center gap-2 rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-sky-600"
            >
              <Upload className="h-4 w-4" />
              Upload Document
            </button>
          </div>

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
                    id={`knowledge-${item.id}`}
                    ref={item.id === highlightId ? highlightedRef : undefined}
                    className={`rounded-xl border p-5 shadow-sm transition-all duration-200 hover:border-l-4 hover:border-l-sky-400 ${
                      item.id === highlightId
                        ? "border-sky-400 ring-2 ring-sky-300 bg-sky-50/30"
                        : "border-slate-200/60 bg-white"
                    }`}
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

      {showUpload && <UploadDialog onClose={() => setShowUpload(false)} />}
    </>
  )
}

import { Suspense } from "react"

export default function KnowledgePage() {
  return (
    <Suspense>
      <KnowledgePageContent />
    </Suspense>
  )
}
