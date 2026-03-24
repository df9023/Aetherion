"use client"

import { useState } from "react"
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

interface CreateClientDialogProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

export function CreateClientDialog({ open: controlledOpen, onOpenChange: controlledOnOpenChange }: CreateClientDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const createClient = useCreateClient()

  const isControlled = controlledOpen !== undefined
  const open = isControlled ? controlledOpen : internalOpen
  const setOpen = isControlled ? controlledOnOpenChange! : setInternalOpen

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

  const dialogContent = (
    <DialogContent className="max-w-2xl">
      <DialogHeader>
        <DialogTitle>New Client</DialogTitle>
      </DialogHeader>

      <form onSubmit={handleSubmit} className="max-h-96 space-y-4 overflow-y-auto py-4">
        <div className="grid grid-cols-2 gap-x-4 gap-y-4">
          {/* Name */}
          <div className="col-span-2">
            <Label htmlFor="name" className="mb-2 block text-sm font-medium text-slate-700">
              Name *
            </Label>
            <Input
              id="name"
              required
              value={form.name}
              onChange={(e) => set("name", e.target.value)}
              placeholder="Full name"
              className="rounded-lg border-slate-200"
            />
          </div>

          {/* Date of Birth */}
          <div>
            <Label htmlFor="dob" className="mb-2 block text-sm font-medium text-slate-700">
              Date of Birth *
            </Label>
            <Input
              id="dob"
              type="date"
              required
              value={form.date_of_birth}
              onChange={(e) => set("date_of_birth", e.target.value)}
              className="rounded-lg border-slate-200"
            />
          </div>

          {/* Employer */}
          <div>
            <Label htmlFor="employer" className="mb-2 block text-sm font-medium text-slate-700">
              Employer
            </Label>
            <Input
              id="employer"
              value={form.employer_name}
              onChange={(e) => set("employer_name", e.target.value)}
              placeholder="e.g., Volvo Group AB"
              className="rounded-lg border-slate-200"
            />
          </div>

          {/* Collective Agreement */}
          <div>
            <Label htmlFor="agreement" className="mb-2 block text-sm font-medium text-slate-700">
              Collective Agreement *
            </Label>
            <Select required value={form.collective_agreement} onValueChange={(v) => set("collective_agreement", v)}>
              <SelectTrigger id="agreement">
                <SelectValue placeholder="Select agreement..." />
              </SelectTrigger>
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

          {/* Annual Income */}
          <div>
            <div className="mb-2 flex items-end justify-between">
              <Label htmlFor="annualIncome" className="text-sm font-medium text-slate-700">
                Annual Income
              </Label>
              <span className="text-xs text-slate-400">SEK</span>
            </div>
            <Input
              id="annualIncome"
              type="number"
              value={form.annual_income}
              onChange={(e) => set("annual_income", e.target.value)}
              placeholder="e.g., 684000"
              className="rounded-lg border-slate-200"
            />
          </div>

          {/* Employment Status */}
          <div>
            <Label htmlFor="employmentStatus" className="mb-2 block text-sm font-medium text-slate-700">
              Employment Status *
            </Label>
            <Select required value={form.employment_status} onValueChange={(v) => set("employment_status", v)}>
              <SelectTrigger id="employmentStatus">
                <SelectValue placeholder="Select status..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="employed">Employed</SelectItem>
                <SelectItem value="self_employed">Self-employed</SelectItem>
                <SelectItem value="retired">Retired</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Risk Profile */}
          <div>
            <Label htmlFor="riskProfile" className="mb-2 block text-sm font-medium text-slate-700">
              Risk Profile
            </Label>
            <Select value={form.risk_profile} onValueChange={(v) => set("risk_profile", v)}>
              <SelectTrigger id="riskProfile">
                <SelectValue placeholder="Select risk profile..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="moderate">Moderate</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Desired Retirement Age */}
          <div>
            <Label htmlFor="retirementAge" className="mb-2 block text-sm font-medium text-slate-700">
              Desired Retirement Age
            </Label>
            <Input
              id="retirementAge"
              type="number"
              value={form.desired_retirement_age}
              onChange={(e) => set("desired_retirement_age", e.target.value)}
              placeholder="e.g., 65"
              className="rounded-lg border-slate-200"
            />
          </div>
        </div>

        <DialogFooter className="flex justify-end gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => setOpen(false)}
            className="border-slate-200 text-slate-700"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            className="bg-sky-500 text-white hover:bg-sky-600"
            disabled={createClient.isPending || !form.name || !form.date_of_birth || !form.employment_status || !form.collective_agreement}
          >
            {createClient.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Create Client
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
        <Button className="gap-2 bg-sky-500 text-white hover:bg-sky-600">
          <Plus className="h-4 w-4" />
          New Client
        </Button>
      </DialogTrigger>
      {dialogContent}
    </Dialog>
  )
}
