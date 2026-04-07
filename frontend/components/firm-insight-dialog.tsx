"use client"

import { useState } from "react"
import { Loader2 } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  useClientOrganizations,
  useCreateFirmInsight,
  type FirmInsightCreateInput,
} from "@/lib/hooks"
import {
  caseTypeLabels,
  agreementLabels,
  firmInsightCategoryLabels,
} from "@/lib/labels"

interface FirmInsightDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  defaultValues?: Partial<FirmInsightCreateInput>
  onCreated?: () => void
}

export function FirmInsightDialog({
  open,
  onOpenChange,
  defaultValues,
  onCreated,
}: FirmInsightDialogProps) {
  const createInsight = useCreateFirmInsight()
  const { data: clientOrgs } = useClientOrganizations()

  const [title, setTitle] = useState("")
  const [content, setContent] = useState("")
  const [category, setCategory] = useState<string>(
    defaultValues?.category ?? "general",
  )
  const [caseTypes, setCaseTypes] = useState<string[]>(
    defaultValues?.case_types ?? [],
  )
  const [agreements, setAgreements] = useState<string[]>(
    defaultValues?.collective_agreements ?? [],
  )
  const [clientOrganizationId, setClientOrganizationId] = useState<string>(
    defaultValues?.client_organization_id ?? "",
  )
  const [tagsInput, setTagsInput] = useState("")

  function resetForm() {
    setTitle("")
    setContent("")
    setCategory(defaultValues?.category ?? "general")
    setCaseTypes(defaultValues?.case_types ?? [])
    setAgreements(defaultValues?.collective_agreements ?? [])
    setClientOrganizationId(defaultValues?.client_organization_id ?? "")
    setTagsInput("")
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const tags = tagsInput
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean)

    const payload: FirmInsightCreateInput = {
      title,
      content,
      category,
      case_types: caseTypes,
      collective_agreements: agreements,
      client_organization_id: clientOrganizationId || null,
      tags,
      source_case_id: defaultValues?.source_case_id ?? null,
    }

    createInsight.mutate(payload, {
      onSuccess: () => {
        toast.success("Insikt skapad")
        resetForm()
        onOpenChange(false)
        onCreated?.()
      },
      onError: (err) => toast.error(err.message),
    })
  }

  const toggleCaseType = (value: string) => {
    setCaseTypes((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value],
    )
  }

  const toggleAgreement = (value: string) => {
    setAgreements((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value],
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Ny firmainsikt</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          <div>
            <Label htmlFor="insight-title" className="mb-2 block text-sm font-medium text-slate-700">
              Titel
            </Label>
            <Input
              id="insight-title"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Kort, tydlig rubrik"
              className="rounded-lg border-slate-200"
              maxLength={255}
            />
          </div>

          <div>
            <Label htmlFor="insight-content" className="mb-2 block text-sm font-medium text-slate-700">
              Innehåll
            </Label>
            <Textarea
              id="insight-content"
              required
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Beskriv insikten – vad är det, när gäller det, varför är det viktigt?"
              rows={5}
              className="rounded-lg border-slate-200"
            />
          </div>

          <div>
            <Label htmlFor="insight-category" className="mb-2 block text-sm font-medium text-slate-700">
              Kategori
            </Label>
            <Select value={category} onValueChange={setCategory}>
              <SelectTrigger id="insight-category">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(firmInsightCategoryLabels).map(([val, label]) => (
                  <SelectItem key={val} value={val}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label className="mb-2 block text-sm font-medium text-slate-700">
              Gäller ärendetyp (valfritt)
            </Label>
            <div className="flex flex-wrap gap-1.5">
              {Object.entries(caseTypeLabels).map(([val, label]) => (
                <button
                  type="button"
                  key={val}
                  onClick={() => toggleCaseType(val)}
                  className={`rounded-full px-2.5 py-1 text-xs font-medium transition-colors ${
                    caseTypes.includes(val)
                      ? "bg-sky-500 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <Label className="mb-2 block text-sm font-medium text-slate-700">
              Gäller avtal (valfritt)
            </Label>
            <div className="flex flex-wrap gap-1.5">
              {Object.entries(agreementLabels).map(([val, label]) => (
                <button
                  type="button"
                  key={val}
                  onClick={() => toggleAgreement(val)}
                  className={`rounded-full px-2.5 py-1 text-xs font-medium transition-colors ${
                    agreements.includes(val)
                      ? "bg-sky-500 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <Label htmlFor="insight-client-org" className="mb-2 block text-sm font-medium text-slate-700">
              Klientorganisation (valfritt)
            </Label>
            <Select
              value={clientOrganizationId || "none"}
              onValueChange={(v) => setClientOrganizationId(v === "none" ? "" : v)}
            >
              <SelectTrigger id="insight-client-org">
                <SelectValue placeholder="Ingen specifik" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Ingen specifik</SelectItem>
                {(clientOrgs ?? []).map((co) => (
                  <SelectItem key={co.id} value={co.id}>
                    {co.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="insight-tags" className="mb-2 block text-sm font-medium text-slate-700">
              Taggar <span className="text-slate-400">(kommaseparerade)</span>
            </Label>
            <Input
              id="insight-tags"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              placeholder="t.ex. löneväxling, itp1, tak"
              className="rounded-lg border-slate-200"
            />
          </div>

          <DialogFooter className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="border-slate-200 text-slate-700"
            >
              Avbryt
            </Button>
            <Button
              type="submit"
              className="bg-sky-500 text-white hover:bg-sky-600"
              disabled={createInsight.isPending || !title || !content}
            >
              {createInsight.isPending && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Spara insikt
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
