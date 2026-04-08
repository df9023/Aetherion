"use client"

import { use, useState } from "react"
import Link from "next/link"
import { Building2, Mail, Phone, User, Users, FileText, Pencil, Loader2 } from "lucide-react"
import { toast } from "sonner"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
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
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  useClientOrganization,
  useUpdateClientOrganization,
  useCases,
  type ClientResponse,
} from "@/lib/hooks"
import { TopBar } from "@/components/top-bar"
import { agreementLabels, agreementStyles } from "@/lib/labels"

function calculateAge(dob: string) {
  const birth = new Date(dob)
  const now = new Date()
  let age = now.getFullYear() - birth.getFullYear()
  if (now.getMonth() < birth.getMonth() || (now.getMonth() === birth.getMonth() && now.getDate() < birth.getDate())) {
    age--
  }
  return age
}

function ClientRow({ client, caseCount }: { client: ClientResponse; caseCount: number }) {
  return (
    <Link
      href={`/clients/${client.id}`}
      className="flex items-center gap-4 rounded-lg px-4 py-3 transition-colors hover:bg-slate-50"
    >
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-100">
        <span className="text-sm font-medium text-slate-600">
          {client.name.split(" ").map((n) => n[0]).join("")}
        </span>
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-slate-900">{client.name}</p>
        <p className="text-sm text-slate-400">{calculateAge(client.date_of_birth)} år</p>
      </div>
      <div className="text-right">
        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${agreementStyles[client.collective_agreement] ?? "bg-slate-100 text-slate-600"}`}>
          {agreementLabels[client.collective_agreement] ?? client.collective_agreement}
        </span>
      </div>
      <div className="w-24 text-right">
        <p className="text-sm text-slate-500">{caseCount} ärenden</p>
      </div>
    </Link>
  )
}

function EditOrgDialog({
  open,
  onOpenChange,
  org,
  orgId,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
  org: {
    name: string
    org_number: string | null
    industry: string | null
    collective_agreement: string | null
    contact_person: string | null
    contact_email: string | null
    contact_phone: string | null
    employee_count: number | null
    notes: string | null
  }
  orgId: string
}) {
  const [form, setForm] = useState({
    name: org.name,
    org_number: org.org_number ?? "",
    industry: org.industry ?? "",
    collective_agreement: org.collective_agreement ?? "",
    contact_person: org.contact_person ?? "",
    contact_email: org.contact_email ?? "",
    contact_phone: org.contact_phone ?? "",
    employee_count: org.employee_count?.toString() ?? "",
    notes: org.notes ?? "",
  })
  const updateOrg = useUpdateClientOrganization(orgId)

  function set(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    updateOrg.mutate(
      {
        name: form.name || undefined,
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
          toast.success("Organisation uppdaterad")
          onOpenChange(false)
        },
      }
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Redigera organisation</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="max-h-96 space-y-4 overflow-y-auto py-4">
          <div className="grid grid-cols-2 gap-x-4 gap-y-4">
            <div className="col-span-2">
              <Label className="mb-2 block text-sm font-medium text-slate-700">Namn</Label>
              <Input value={form.name} onChange={(e) => set("name", e.target.value)} className="rounded-lg border-slate-200" />
            </div>
            <div>
              <Label className="mb-2 block text-sm font-medium text-slate-700">Organisationsnummer</Label>
              <Input value={form.org_number} onChange={(e) => set("org_number", e.target.value)} className="rounded-lg border-slate-200" />
            </div>
            <div>
              <Label className="mb-2 block text-sm font-medium text-slate-700">Bransch</Label>
              <Input value={form.industry} onChange={(e) => set("industry", e.target.value)} className="rounded-lg border-slate-200" />
            </div>
            <div>
              <Label className="mb-2 block text-sm font-medium text-slate-700">Kollektivavtal</Label>
              <Select value={form.collective_agreement} onValueChange={(v) => set("collective_agreement", v)}>
                <SelectTrigger><SelectValue placeholder="Välj avtal..." /></SelectTrigger>
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
            <div>
              <Label className="mb-2 block text-sm font-medium text-slate-700">Antal anställda</Label>
              <Input type="number" value={form.employee_count} onChange={(e) => set("employee_count", e.target.value)} className="rounded-lg border-slate-200" />
            </div>
            <div>
              <Label className="mb-2 block text-sm font-medium text-slate-700">Kontaktperson</Label>
              <Input value={form.contact_person} onChange={(e) => set("contact_person", e.target.value)} className="rounded-lg border-slate-200" />
            </div>
            <div>
              <Label className="mb-2 block text-sm font-medium text-slate-700">E-post</Label>
              <Input type="email" value={form.contact_email} onChange={(e) => set("contact_email", e.target.value)} className="rounded-lg border-slate-200" />
            </div>
            <div>
              <Label className="mb-2 block text-sm font-medium text-slate-700">Telefon</Label>
              <Input value={form.contact_phone} onChange={(e) => set("contact_phone", e.target.value)} className="rounded-lg border-slate-200" />
            </div>
            <div className="col-span-2">
              <Label className="mb-2 block text-sm font-medium text-slate-700">Anteckningar</Label>
              <Textarea value={form.notes} onChange={(e) => set("notes", e.target.value)} className="rounded-lg border-slate-200" rows={3} />
            </div>
          </div>
          <DialogFooter className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} className="border-slate-200 text-slate-700">Avbryt</Button>
            <Button type="submit" className="bg-sky-500 text-white hover:bg-sky-600" disabled={updateOrg.isPending}>
              {updateOrg.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Spara
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default function OrganizationDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const { data: org, isLoading } = useClientOrganization(id)
  const { data: allCases } = useCases()
  const [editOpen, setEditOpen] = useState(false)

  // Count cases per client
  const caseCounts = new Map<string, number>()
  if (allCases) {
    for (const c of allCases) {
      caseCounts.set(c.client_id, (caseCounts.get(c.client_id) ?? 0) + 1)
    }
  }

  if (isLoading) {
    return (
      <>
        <TopBar breadcrumbs={[{ label: "Organisationer", href: "/organizations" }, { label: "Laddar..." }]} />
        <main className="flex-1 bg-slate-50">
          <div className="mx-auto max-w-7xl px-6 py-8">
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
              <div className="space-y-6 lg:col-span-2">
                <Skeleton className="h-60 rounded-xl" />
              </div>
              <div>
                <Skeleton className="h-80 rounded-xl" />
              </div>
            </div>
          </div>
        </main>
      </>
    )
  }

  if (!org) {
    return (
      <>
        <TopBar breadcrumbs={[{ label: "Organisationer", href: "/organizations" }, { label: "Hittades inte" }]} />
        <main className="flex-1 bg-slate-50">
          <div className="py-12 text-center text-sm text-slate-400">Organisation hittades inte</div>
        </main>
      </>
    )
  }

  const agreementStyle = agreementStyles[org.collective_agreement ?? ""] ?? "bg-slate-100 text-slate-600"

  return (
    <>
      {editOpen && (
        <EditOrgDialog open={editOpen} onOpenChange={setEditOpen} org={org} orgId={id} />
      )}
      <TopBar breadcrumbs={[{ label: "Organisationer", href: "/organizations" }, { label: org.name }]} />
      <main className="flex-1 bg-slate-50">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Left column — employee list */}
            <div className="space-y-6 lg:col-span-2">
              <div className="rounded-xl border border-slate-200/60 bg-white shadow-sm">
                <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
                  <div className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-slate-600" />
                    <h2 className="text-base font-semibold text-slate-900">
                      Anställda i systemet ({org.clients.length})
                    </h2>
                  </div>
                </div>

                {org.clients.length > 0 ? (
                  <div className="divide-y divide-slate-100">
                    {org.clients.map((client) => (
                      <ClientRow
                        key={client.id}
                        client={client}
                        caseCount={caseCounts.get(client.id) ?? 0}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-10">
                    <Users className="mb-2 h-10 w-10 text-slate-300" />
                    <p className="text-sm text-slate-400">Inga klienter kopplade ännu</p>
                  </div>
                )}
              </div>
            </div>

            {/* Right column — org info card */}
            <div className="space-y-6">
              <div className="rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm">
                <div className="mb-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Building2 className="h-5 w-5 text-slate-600" />
                    <h2 className="text-base font-semibold text-slate-900">Organisation</h2>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setEditOpen(true)}
                    className="gap-1 border-slate-200 text-slate-700"
                  >
                    <Pencil className="h-3.5 w-3.5" />
                    Redigera
                  </Button>
                </div>

                <div className="space-y-4">
                  {/* Name */}
                  <div>
                    <p className="text-sm font-medium text-slate-900">{org.name}</p>
                    {org.org_number && (
                      <p className="text-sm text-slate-400">{org.org_number}</p>
                    )}
                  </div>

                  {/* Industry */}
                  {org.industry && (
                    <div>
                      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Bransch</p>
                      <p className="text-sm text-slate-700">{org.industry}</p>
                    </div>
                  )}

                  {/* Agreement */}
                  {org.collective_agreement && (
                    <div>
                      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Kollektivavtal</p>
                      <span className={`mt-1 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${agreementStyle}`}>
                        {agreementLabels[org.collective_agreement] ?? org.collective_agreement}
                      </span>
                    </div>
                  )}

                  {/* Employee counts */}
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Anställda</p>
                    <p className="text-sm text-slate-700">
                      {org.employee_count ? `${org.employee_count.toLocaleString("sv-SE")} totalt` : "—"}
                      {" / "}
                      {org.clients.length} i systemet
                    </p>
                  </div>

                  {/* Contact info */}
                  {(org.contact_person || org.contact_email || org.contact_phone) && (
                    <div>
                      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">Kontakt</p>
                      {org.contact_person && (
                        <div className="flex items-center gap-2 text-sm text-slate-700">
                          <User className="h-4 w-4 shrink-0 text-slate-400" />
                          {org.contact_person}
                        </div>
                      )}
                      {org.contact_email && (
                        <div className="mt-1 flex items-center gap-2 text-sm text-slate-700">
                          <Mail className="h-4 w-4 shrink-0 text-slate-400" />
                          <a href={`mailto:${org.contact_email}`} className="hover:text-sky-600">{org.contact_email}</a>
                        </div>
                      )}
                      {org.contact_phone && (
                        <div className="mt-1 flex items-center gap-2 text-sm text-slate-700">
                          <Phone className="h-4 w-4 shrink-0 text-slate-400" />
                          {org.contact_phone}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Notes */}
                  {org.notes && (
                    <div>
                      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Anteckningar</p>
                      <div className="mt-1 flex items-start gap-2">
                        <FileText className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
                        <p className="text-sm text-slate-700 whitespace-pre-wrap">{org.notes}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}
