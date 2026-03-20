"use client"

import React from "react"
import { usePathname } from "next/navigation"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { useCase, useClient } from "@/lib/hooks"

export function TopBar() {
  const pathname = usePathname()
  const segments = pathname.split("/").filter(Boolean)

  const caseId = segments[0] === "cases" && segments[1] ? segments[1] : ""
  const clientId = segments[0] === "clients" && segments[1] ? segments[1] : ""

  const { data: caseData } = useCase(caseId)
  const { data: clientData } = useClient(clientId)

  const crumbs: { label: string; href?: string }[] = []

  if (segments[0] === "cases") {
    crumbs.push({ label: "Cases", href: segments.length > 1 ? "/cases" : undefined })
    if (segments[1]) {
      crumbs.push({ label: caseData?.title ?? "Loading..." })
    }
  } else if (segments[0] === "clients") {
    crumbs.push({ label: "Clients", href: segments.length > 1 ? "/clients" : undefined })
    if (segments[1]) {
      crumbs.push({ label: clientData?.name ?? "Loading..." })
    }
  } else if (segments[0] === "knowledge") {
    crumbs.push({ label: "Knowledge Base" })
  }

  return (
    <header className="sticky top-0 z-10 flex h-14 items-center justify-between border-b border-slate-200/60 bg-white/80 px-6 backdrop-blur-sm">
      <Breadcrumb>
        <BreadcrumbList>
          {crumbs.map((crumb, i) => (
            <React.Fragment key={i}>
              {i > 0 && <BreadcrumbSeparator />}
              <BreadcrumbItem>
                {crumb.href ? (
                  <BreadcrumbLink href={crumb.href}>{crumb.label}</BreadcrumbLink>
                ) : (
                  <BreadcrumbPage>{crumb.label}</BreadcrumbPage>
                )}
              </BreadcrumbItem>
            </React.Fragment>
          ))}
        </BreadcrumbList>
      </Breadcrumb>

      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500">
        SPP
      </span>
    </header>
  )
}
