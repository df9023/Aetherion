"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Loader2, Plus } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
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
import { useClients, useCreateCase } from "@/lib/hooks"
import { caseTypeLabels } from "@/lib/labels"

interface CreateCaseDialogProps {
  defaultClientId?: string
  trigger?: React.ReactNode
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

export function CreateCaseDialog({ defaultClientId, trigger, open: controlledOpen, onOpenChange: controlledOnOpenChange }: CreateCaseDialogProps) {
  const router = useRouter()
  const [internalOpen, setInternalOpen] = useState(false)
  const { data: clients } = useClients()
  const createCase = useCreateCase()

  const isControlled = controlledOpen !== undefined
  const open = isControlled ? controlledOpen : internalOpen
  const setOpen = isControlled ? controlledOnOpenChange! : setInternalOpen

  const [title, setTitle] = useState("")
  const [caseType, setCaseType] = useState("")
  const [clientId, setClientId] = useState(defaultClientId ?? "")
  const [summary, setSummary] = useState("")

  function resetForm() {
    setTitle("")
    setCaseType("")
    setClientId(defaultClientId ?? "")
    setSummary("")
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    createCase.mutate(
      {
        title,
        case_type: caseType,
        client_id: clientId,
        assigned_to: process.env.NEXT_PUBLIC_DEV_USER_ID || "",
        summary: summary || undefined,
      },
      {
        onSuccess: (data) => {
          toast.success("Ärende skapat")
          resetForm()
          setOpen(false)
          router.push(`/cases/${data.id}`)
        },
      }
    )
  }

  const dialogContent = (
    <DialogContent className="max-w-lg">
      <DialogHeader>
        <DialogTitle>Nytt ärende</DialogTitle>
      </DialogHeader>

      <form onSubmit={handleSubmit} className="space-y-4 py-4">
        {/* Client Select */}
        <div>
          <Label htmlFor="client" className="mb-2 block text-sm font-medium text-slate-700">
            Klient
          </Label>
          <Select required value={clientId} onValueChange={setClientId}>
            <SelectTrigger id="client">
              <SelectValue placeholder="Välj klient..." />
            </SelectTrigger>
            <SelectContent>
              {(clients ?? []).map((c) => (
                <SelectItem key={c.id} value={c.id}>
                  <div className="flex flex-col">
                    <span>{c.name}</span>
                    <span className="text-xs text-slate-400">{c.employer_name}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Case Type Select */}
        <div>
          <Label htmlFor="caseType" className="mb-2 block text-sm font-medium text-slate-700">
            Ärendetyp
          </Label>
          <Select required value={caseType} onValueChange={setCaseType}>
            <SelectTrigger id="caseType">
              <SelectValue placeholder="Välj typ..." />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(caseTypeLabels).map(([val, label]) => (
                <SelectItem key={val} value={val}>{label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Title Input */}
        <div>
          <Label htmlFor="title" className="mb-2 block text-sm font-medium text-slate-700">
            Titel
          </Label>
          <Input
            id="title"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Ärendetitel"
            className="rounded-lg border-slate-200"
          />
        </div>

        {/* Summary Textarea */}
        <div>
          <Label htmlFor="summary" className="mb-2 block text-sm font-medium text-slate-700">
            Sammanfattning
          </Label>
          <Textarea
            id="summary"
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="Kort beskrivning av ärendet..."
            rows={3}
            className="rounded-lg border-slate-200"
          />
        </div>

        <DialogFooter className="flex justify-end gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => setOpen(false)}
            className="border-slate-200 text-slate-700"
          >
            Avbryt
          </Button>
          <Button
            type="submit"
            className="bg-sky-500 text-white hover:bg-sky-600"
            disabled={createCase.isPending || !title || !caseType || !clientId}
          >
            {createCase.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Skapa ärende
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  )

  if (isControlled) {
    return (
      <Dialog open={open} onOpenChange={setOpen}>
        {dialogContent}
      </Dialog>
    )
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger ?? (
          <Button className="gap-2 bg-sky-500 text-white hover:bg-sky-600">
            <Plus className="h-4 w-4" />
            Nytt ärende
          </Button>
        )}
      </DialogTrigger>
      {dialogContent}
    </Dialog>
  )
}
