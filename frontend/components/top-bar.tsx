"use client"

import { usePathname } from "next/navigation"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { mockCases } from "@/lib/mock-data"

function useBreadcrumbs() {
  const pathname = usePathname()
  const segments = pathname.split("/").filter(Boolean)

  const crumbs: { label: string; href?: string }[] = []

  if (segments[0] === "cases") {
    crumbs.push({ label: "Cases", href: segments.length > 1 ? "/cases" : undefined })
    if (segments[1]) {
      const c = mockCases.find((c) => c.id === segments[1])
      crumbs.push({ label: c?.title ?? segments[1] })
    }
  } else if (segments[0] === "clients") {
    crumbs.push({ label: "Clients" })
  } else if (segments[0] === "knowledge") {
    crumbs.push({ label: "Knowledge Base" })
  }

  return crumbs
}

export function TopBar() {
  const crumbs = useBreadcrumbs()

  return (
    <header className="sticky top-0 z-10 flex h-14 items-center justify-between border-b border-slate-200/60 bg-white/80 px-6 backdrop-blur-sm">
      <Breadcrumb>
        <BreadcrumbList>
          {crumbs.map((crumb, i) => (
            <BreadcrumbItem key={i}>
              {i > 0 && <BreadcrumbSeparator />}
              {crumb.href ? (
                <BreadcrumbLink href={crumb.href}>{crumb.label}</BreadcrumbLink>
              ) : (
                <BreadcrumbPage>{crumb.label}</BreadcrumbPage>
              )}
            </BreadcrumbItem>
          ))}
        </BreadcrumbList>
      </Breadcrumb>

      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500">
        SPP
      </span>
    </header>
  )
}
