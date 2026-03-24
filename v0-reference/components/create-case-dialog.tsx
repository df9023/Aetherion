'use client'

import { useState, useEffect } from 'react'
import { clients, type CaseType } from '@/lib/data'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'

interface CreateCaseDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const CASE_TYPES: CaseType[] = [
  'Retirement Planning',
  'Salary Exchange',
  'Pension Review',
  'Transfer Advice',
  'Survivor Protection',
]

export function CreateCaseDialog({ open, onOpenChange }: CreateCaseDialogProps) {
  const [selectedClient, setSelectedClient] = useState<string>('c1')
  const [caseType, setCaseType] = useState<CaseType>('Retirement Planning')
  const [title, setTitle] = useState('')
  const [summary, setSummary] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Pre-fill title based on type + client
  useEffect(() => {
    if (selectedClient && caseType) {
      const client = clients.find((c) => c.id === selectedClient)
      if (client) {
        setTitle(`${caseType} — ${client.name}`)
      }
    }
  }, [selectedClient, caseType])

  const handleSubmit = () => {
    const newErrors: Record<string, string> = {}
    if (!selectedClient) newErrors.client = 'Required'
    if (!caseType) newErrors.caseType = 'Required'

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    // Handle form submission
    console.log({
      client: selectedClient,
      caseType,
      title,
      summary,
    })

    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>New Case</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Client Select */}
          <div>
            <Label htmlFor="client" className="text-sm font-medium text-slate-700 mb-2 block">
              Client
            </Label>
            <Select value={selectedClient} onValueChange={setSelectedClient}>
              <SelectTrigger
                id="client"
                className={`${errors.client ? 'border-red-500' : ''}`}
              >
                <SelectValue placeholder="Select a client..." />
              </SelectTrigger>
              <SelectContent>
                {clients.map((client) => (
                  <SelectItem key={client.id} value={client.id}>
                    <div className="flex flex-col">
                      <span>{client.name}</span>
                      <span className="text-xs text-slate-400">{client.employer}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.client && (
              <p className="text-xs text-red-600 mt-1">{errors.client}</p>
            )}
          </div>

          {/* Case Type Select */}
          <div>
            <Label htmlFor="caseType" className="text-sm font-medium text-slate-700 mb-2 block">
              Case Type
            </Label>
            <Select value={caseType} onValueChange={(value) => setCaseType(value as CaseType)}>
              <SelectTrigger
                id="caseType"
                className={`${errors.caseType ? 'border-red-500' : ''}`}
              >
                <SelectValue placeholder="Select type..." />
              </SelectTrigger>
              <SelectContent>
                {CASE_TYPES.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.caseType && (
              <p className="text-xs text-red-600 mt-1">{errors.caseType}</p>
            )}
          </div>

          {/* Title Input */}
          <div>
            <Label htmlFor="title" className="text-sm font-medium text-slate-700 mb-2 block">
              Title
            </Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Case title"
              className="rounded-lg border-slate-200"
            />
          </div>

          {/* Summary Textarea */}
          <div>
            <Label htmlFor="summary" className="text-sm font-medium text-slate-700 mb-2 block">
              Summary
            </Label>
            <Textarea
              id="summary"
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              placeholder="Brief description of the case..."
              rows={3}
              className="rounded-lg border-slate-200"
            />
          </div>
        </div>

        <DialogFooter className="flex justify-end gap-2">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="border-slate-200 text-slate-700"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            className="bg-sky-500 hover:bg-sky-600 text-white"
          >
            Create Case
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
