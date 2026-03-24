'use client'

import { useState } from 'react'
import { type EmploymentStatus, type RiskProfile } from '@/lib/data'
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
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'

interface CreateClientDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const AGREEMENTS = ['ITP1', 'ITP2', 'SAF-LO', 'KAP-KL', 'PA 16', 'Other']
const EMPLOYMENT_STATUSES: EmploymentStatus[] = ['employed', 'unemployed', 'retired']
const RISK_PROFILES: RiskProfile[] = ['low', 'moderate', 'high']

export function CreateClientDialog({ open, onOpenChange }: CreateClientDialogProps) {
  const [formData, setFormData] = useState({
    firstName: 'Anna',
    lastName: 'Johansson',
    dob: '',
    employer: 'Volvo Group AB',
    agreement: '',
    annualIncome: '',
    employmentStatus: 'employed' as EmploymentStatus,
    riskProfile: '' as RiskProfile | '',
    retirementAge: '',
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleSelectChange = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleSubmit = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.firstName.trim()) newErrors.firstName = 'Required'
    if (!formData.lastName.trim()) newErrors.lastName = 'Required'
    if (!formData.dob) newErrors.dob = 'Required'

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    // Handle form submission
    console.log(formData)

    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>New Client</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4 max-h-96 overflow-y-auto">
          {/* Row 1: First Name, Last Name */}
          <div className="grid grid-cols-2 gap-x-4 gap-y-4">
            <div>
              <Label htmlFor="firstName" className="text-sm font-medium text-slate-700 mb-2 block">
                First Name
              </Label>
              <Input
                id="firstName"
                value={formData.firstName}
                onChange={(e) => handleInputChange('firstName', e.target.value)}
                placeholder="Anna"
                className={`rounded-lg border-slate-200 ${errors.firstName ? 'border-red-500' : ''}`}
              />
              {errors.firstName && (
                <p className="text-xs text-red-600 mt-1">{errors.firstName}</p>
              )}
            </div>

            <div>
              <Label htmlFor="lastName" className="text-sm font-medium text-slate-700 mb-2 block">
                Last Name
              </Label>
              <Input
                id="lastName"
                value={formData.lastName}
                onChange={(e) => handleInputChange('lastName', e.target.value)}
                placeholder="Johansson"
                className={`rounded-lg border-slate-200 ${errors.lastName ? 'border-red-500' : ''}`}
              />
              {errors.lastName && (
                <p className="text-xs text-red-600 mt-1">{errors.lastName}</p>
              )}
            </div>

            {/* Row 2: Date of Birth, Employer */}
            <div>
              <Label htmlFor="dob" className="text-sm font-medium text-slate-700 mb-2 block">
                Date of Birth
              </Label>
              <Input
                id="dob"
                type="date"
                value={formData.dob}
                onChange={(e) => handleInputChange('dob', e.target.value)}
                className={`rounded-lg border-slate-200 ${errors.dob ? 'border-red-500' : ''}`}
              />
              {errors.dob && (
                <p className="text-xs text-red-600 mt-1">{errors.dob}</p>
              )}
            </div>

            <div>
              <Label htmlFor="employer" className="text-sm font-medium text-slate-700 mb-2 block">
                Employer
              </Label>
              <Input
                id="employer"
                value={formData.employer}
                onChange={(e) => handleInputChange('employer', e.target.value)}
                placeholder="e.g., Volvo Group AB"
                className="rounded-lg border-slate-200"
              />
            </div>

            {/* Row 3: Collective Agreement, Annual Income */}
            <div>
              <Label htmlFor="agreement" className="text-sm font-medium text-slate-700 mb-2 block">
                Collective Agreement
              </Label>
              <Select value={formData.agreement} onValueChange={(value) => handleSelectChange('agreement', value)}>
                <SelectTrigger id="agreement">
                  <SelectValue placeholder="Select agreement..." />
                </SelectTrigger>
                <SelectContent>
                  {AGREEMENTS.map((agr) => (
                    <SelectItem key={agr} value={agr}>
                      {agr}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <div className="flex items-end justify-between mb-2">
                <Label htmlFor="annualIncome" className="text-sm font-medium text-slate-700">
                  Annual Income
                </Label>
                <span className="text-xs text-slate-400">SEK</span>
              </div>
              <Input
                id="annualIncome"
                type="number"
                value={formData.annualIncome}
                onChange={(e) => handleInputChange('annualIncome', e.target.value)}
                placeholder="e.g., 684000"
                className="rounded-lg border-slate-200"
              />
            </div>

            {/* Row 4: Employment Status, Risk Profile */}
            <div>
              <Label htmlFor="employmentStatus" className="text-sm font-medium text-slate-700 mb-2 block">
                Employment Status
              </Label>
              <Select value={formData.employmentStatus} onValueChange={(value) => handleSelectChange('employmentStatus', value)}>
                <SelectTrigger id="employmentStatus">
                  <SelectValue placeholder="Select status..." />
                </SelectTrigger>
                <SelectContent>
                  {EMPLOYMENT_STATUSES.map((status) => (
                    <SelectItem key={status} value={status}>
                      {status.charAt(0).toUpperCase() + status.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="riskProfile" className="text-sm font-medium text-slate-700 mb-2 block">
                Risk Profile
              </Label>
              <Select value={formData.riskProfile} onValueChange={(value) => handleSelectChange('riskProfile', value as RiskProfile)}>
                <SelectTrigger id="riskProfile">
                  <SelectValue placeholder="Select risk profile..." />
                </SelectTrigger>
                <SelectContent>
                  {RISK_PROFILES.map((risk) => (
                    <SelectItem key={risk} value={risk}>
                      {risk.charAt(0).toUpperCase() + risk.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Row 5: Desired Retirement Age */}
            <div className="col-span-1">
              <Label htmlFor="retirementAge" className="text-sm font-medium text-slate-700 mb-2 block">
                Desired Retirement Age
              </Label>
              <Input
                id="retirementAge"
                type="number"
                value={formData.retirementAge}
                onChange={(e) => handleInputChange('retirementAge', e.target.value)}
                placeholder="e.g., 65"
                className="rounded-lg border-slate-200"
              />
            </div>
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
            Create Client
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
