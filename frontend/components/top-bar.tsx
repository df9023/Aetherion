"use client"

import Link from "next/link"
import { ChevronRight } from "lucide-react"

interface TopBarProps {
  breadcrumbs: { label: string; href?: string }[]
}

export function TopBar({ breadcrumbs }: TopBarProps) {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-slate-200/60 bg-white/80 px-6 backdrop-blur-sm">
      {/* Breadcrumbs */}
      <nav aria-label="Breadcrumb">
        <ol className="flex items-center gap-1.5 text-sm text-slate-500">
          {breadcrumbs.map((crumb, i) => (
            <li key={i} className="flex items-center gap-1.5">
              {i > 0 && <ChevronRight className="h-3.5 w-3.5 text-slate-300" />}
              {crumb.href ? (
                <Link
                  href={crumb.href}
                  className="text-slate-400 transition-colors hover:text-slate-600"
                >
                  {crumb.label}
                </Link>
              ) : (
                <span
                  className={
                    i === breadcrumbs.length - 1
                      ? "font-medium text-slate-700"
                      : "text-slate-400"
                  }
                >
                  {crumb.label}
                </span>
              )}
            </li>
          ))}
        </ol>
      </nav>

      {/* Org badge */}
      <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-600">
        SPP
      </span>
    </header>
  )
}
