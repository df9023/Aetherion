"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Loader2, Plus } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
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
}

export function CreateCaseDialog({ defaultClientId, trigger }: CreateCaseDialogProps) {
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const { data: clients } = useClients()
  const createCase = useCreateCase()

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
          toast.success("Case created")
          resetForm()
          setOpen(false)
          router.push(`/cases/${data.id}`)
        },
      }
    )
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger ?? (
          <Button className="bg-sky-500 hover:bg-sky-600 text-white rounded-lg">
            <Plus className="mr-2 h-4 w-4" />
            New Case
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>New Case</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <Label>Client *</Label>
            <Select required value={clientId} onValueChange={setClientId}>
              <SelectTrigger><SelectValue placeholder="Select client..." /></SelectTrigger>
              <SelectContent>
                {(clients ?? []).map((c) => (
                  <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Case Type *</Label>
            <Select required value={caseType} onValueChange={setCaseType}>
              <SelectTrigger><SelectValue placeholder="Select type..." /></SelectTrigger>
              <SelectContent>
                {Object.entries(caseTypeLabels).map(([val, label]) => (
                  <SelectItem key={val} value={val}>{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="case-title">Title *</Label>
            <Input id="case-title" required value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div>
            <Label htmlFor="case-summary">Summary</Label>
            <Textarea id="case-summary" rows={3} value={summary} onChange={(e) => setSummary(e.target.value)} />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="outline" className="rounded-lg" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button
              type="submit"
              className="bg-sky-500 hover:bg-sky-600 text-white rounded-lg"
              disabled={createCase.isPending || !title || !caseType || !clientId}
            >
              {createCase.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Case
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
