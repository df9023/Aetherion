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
import { useCreateClientOrganization } from "@/lib/hooks"

const EMPTY_FORM = {
  name: "",
  org_number: "",
  industry: "",
  collective_agreement: "",
  contact_person: "",
  contact_email: "",
  contact_phone: "",
  employee_count: "",
  notes: "",
}

interface CreateClientOrgDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function CreateClientOrgDialog({ open, onOpenChange }: CreateClientOrgDialogProps) {
  const [form, setForm] = useState(EMPTY_FORM)
  const createOrg = useCreateClientOrganization()

  function set(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    createOrg.mutate(
      {
        name: form.name,
        org_number: form.org_number || undefined,
        industry: form.industry || undefined,
        collective_agreement: form.collective_agreement || undefined,
        contact_person: form.contact_person || undefined,
        contact_email: form.contact_email || undefined,
        contact_phone: form.contact_phone || undefined,
        employee_count: form.employee_count ? Number(form.employee_count) : undefined,
        notes: form.notes || undefined,
      },
      {
        onSuccess: () => {
          toast.success("Organisation skapad")
          setForm(EMPTY_FORM)
          onOpenChange(false)
        },
      }
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Ny organisation</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="max-h-96 space-y-4 overflow-y-auto py-4">
          <div className="grid grid-cols-2 gap-x-4 gap-y-4">
            {/* Name */}
            <div className="col-span-2">
              <Label htmlFor="co-name" className="mb-2 block text-sm font-medium text-slate-700">
                Organisationsnamn *
              </Label>
              <Input
                id="co-name"
                required
                value={form.name}
                onChange={(e) => set("name", e.target.value)}
                placeholder="t.ex. McKinsey & Company Stockholm"
                className="rounded-lg border-slate-200"
              />
            </div>

            {/* Org Number */}
            <div>
              <Label htmlFor="co-orgnum" className="mb-2 block text-sm font-medium text-slate-700">
                Organisationsnummer
              </Label>
              <Input
                id="co-orgnum"
                value={form.org_number}
                onChange={(e) => set("org_number", e.target.value)}
                placeholder="556XXX-XXXX"
                className="rounded-lg border-slate-200"
              />
            </div>

            {/* Industry */}
            <div>
              <Label htmlFor="co-industry" className="mb-2 block text-sm font-medium text-slate-700">
                Bransch
              </Label>
              <Input
                id="co-industry"
                value={form.industry}
                onChange={(e) => set("industry", e.target.value)}
                placeholder="t.ex. Konsulting"
                className="rounded-lg border-slate-200"
              />
            </div>

            {/* Collective Agreement */}
            <div>
              <Label htmlFor="co-agreement" className="mb-2 block text-sm font-medium text-slate-700">
                Kollektivavtal
              </Label>
              <Select value={form.collective_agreement} onValueChange={(v) => set("collective_agreement", v)}>
                <SelectTrigger id="co-agreement">
                  <SelectValue placeholder="Välj avtal..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ITP1">ITP1</SelectItem>
                  <SelectItem value="ITP2">ITP2</SelectItem>
                  <SelectItem value="SAF_LO">SAF-LO</SelectItem>
                  <SelectItem value="KAP_KL">KAP-KL</SelectItem>
                  <SelectItem value="AKAP_KL">AKAP-KL</SelectItem>
                  <SelectItem value="PA16">PA16</SelectItem>
                  <SelectItem value="other">Övrigt</SelectItem>
                  <SelectItem value="none">Inget</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Employee Count */}
            <div>
              <Label htmlFor="co-employees" className="mb-2 block text-sm font-medium text-slate-700">
                Antal anställda
              </Label>
              <Input
                id="co-employees"
                type="number"
                value={form.employee_count}
                onChange={(e) => set("employee_count", e.target.value)}
                placeholder="t.ex. 450"
                className="rounded-lg border-slate-200"
              />
            </div>

            {/* Contact Person */}
            <div>
              <Label htmlFor="co-contact" className="mb-2 block text-sm font-medium text-slate-700">
                Kontaktperson
              </Label>
              <Input
                id="co-contact"
                value={form.contact_person}
                onChange={(e) => set("contact_person", e.target.value)}
                placeholder="Namn"
                className="rounded-lg border-slate-200"
              />
            </div>

            {/* Contact Email */}
            <div>
              <Label htmlFor="co-email" className="mb-2 block text-sm font-medium text-slate-700">
                Kontakt e-post
              </Label>
              <Input
                id="co-email"
                type="email"
                value={form.contact_email}
                onChange={(e) => set("contact_email", e.target.value)}
                placeholder="namn@foretag.se"
                className="rounded-lg border-slate-200"
              />
            </div>

            {/* Contact Phone */}
            <div>
              <Label htmlFor="co-phone" className="mb-2 block text-sm font-medium text-slate-700">
                Kontakt telefon
              </Label>
              <Input
                id="co-phone"
                value={form.contact_phone}
                onChange={(e) => set("contact_phone", e.target.value)}
                placeholder="+46 70 XXX XX XX"
                className="rounded-lg border-slate-200"
              />
            </div>

            {/* Notes */}
            <div className="col-span-2">
              <Label htmlFor="co-notes" className="mb-2 block text-sm font-medium text-slate-700">
                Anteckningar
              </Label>
              <Textarea
                id="co-notes"
                value={form.notes}
                onChange={(e) => set("notes", e.target.value)}
                placeholder="Valfria anteckningar om organisationen..."
                className="rounded-lg border-slate-200"
                rows={3}
              />
            </div>
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
              disabled={createOrg.isPending || !form.name}
            >
              {createOrg.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Skapa organisation
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
