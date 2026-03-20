"use client"

import { useState } from "react"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useCreateClient } from "@/lib/hooks"

const EMPTY_FORM = {
  name: "",
  date_of_birth: "",
  employment_status: "",
  employer_name: "",
  collective_agreement: "",
  annual_income: "",
  desired_retirement_age: "",
  risk_profile: "",
}

export function CreateClientDialog() {
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const createClient = useCreateClient()

  function set(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    createClient.mutate(
      {
        name: form.name,
        date_of_birth: form.date_of_birth,
        employment_status: form.employment_status,
        collective_agreement: form.collective_agreement,
        employer_name: form.employer_name || undefined,
        annual_income: form.annual_income ? Number(form.annual_income) : undefined,
        desired_retirement_age: form.desired_retirement_age ? Number(form.desired_retirement_age) : undefined,
        risk_profile: form.risk_profile || undefined,
      },
      {
        onSuccess: () => {
          toast.success("Client created")
          setForm(EMPTY_FORM)
          setOpen(false)
        },
      }
    )
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-sky-500 hover:bg-sky-600 text-white rounded-lg">
          <Plus className="mr-2 h-4 w-4" />
          New Client
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>New Client</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="mt-4 grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <Label htmlFor="name">Name *</Label>
            <Input id="name" required value={form.name} onChange={(e) => set("name", e.target.value)} />
          </div>
          <div>
            <Label htmlFor="dob">Date of Birth *</Label>
            <Input id="dob" type="date" required value={form.date_of_birth} onChange={(e) => set("date_of_birth", e.target.value)} />
          </div>
          <div>
            <Label>Employment Status *</Label>
            <Select required value={form.employment_status} onValueChange={(v) => set("employment_status", v)}>
              <SelectTrigger><SelectValue placeholder="Select..." /></SelectTrigger>
              <SelectContent>
                <SelectItem value="employed">Employed</SelectItem>
                <SelectItem value="self_employed">Self-employed</SelectItem>
                <SelectItem value="retired">Retired</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="employer">Employer Name</Label>
            <Input id="employer" value={form.employer_name} onChange={(e) => set("employer_name", e.target.value)} />
          </div>
          <div>
            <Label>Collective Agreement *</Label>
            <Select required value={form.collective_agreement} onValueChange={(v) => set("collective_agreement", v)}>
              <SelectTrigger><SelectValue placeholder="Select..." /></SelectTrigger>
              <SelectContent>
                <SelectItem value="ITP1">ITP1</SelectItem>
                <SelectItem value="ITP2">ITP2</SelectItem>
                <SelectItem value="SAF_LO">SAF-LO</SelectItem>
                <SelectItem value="KAP_KL">KAP-KL</SelectItem>
                <SelectItem value="AKAP_KL">AKAP-KL</SelectItem>
                <SelectItem value="PA16">PA16</SelectItem>
                <SelectItem value="other">Other</SelectItem>
                <SelectItem value="none">None</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="income">Annual Income (SEK)</Label>
            <Input id="income" type="number" value={form.annual_income} onChange={(e) => set("annual_income", e.target.value)} />
          </div>
          <div>
            <Label htmlFor="retage">Desired Retirement Age</Label>
            <Input id="retage" type="number" value={form.desired_retirement_age} onChange={(e) => set("desired_retirement_age", e.target.value)} />
          </div>
          <div>
            <Label>Risk Profile</Label>
            <Select value={form.risk_profile} onValueChange={(v) => set("risk_profile", v)}>
              <SelectTrigger><SelectValue placeholder="Select..." /></SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="moderate">Moderate</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="col-span-2 flex justify-end gap-3 pt-2">
            <Button type="button" variant="outline" className="rounded-lg" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button
              type="submit"
              className="bg-sky-500 hover:bg-sky-600 text-white rounded-lg"
              disabled={createClient.isPending || !form.name || !form.date_of_birth || !form.employment_status || !form.collective_agreement}
            >
              {createClient.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Client
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
