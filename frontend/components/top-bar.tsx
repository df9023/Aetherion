"use client"

import Link from "next/link"
import { Bell, ChevronRight } from "lucide-react"

interface TopBarProps {
  breadcrumbs: { label: string; href?: string }[]
}

export function TopBar({ breadcrumbs }: TopBarProps) {
  return (
    <header className="sticky top-0 z-30 flex h-12 items-center justify-between border-b border-slate-200/60 bg-white/80 px-6 backdrop-blur-sm">
      {/* Breadcrumbs */}
      <nav aria-label="Breadcrumb">
        <ol className="flex items-center gap-1 text-xs text-slate-500">
          {breadcrumbs.map((crumb, i) => (
            <li key={i} className="flex items-center gap-1">
              {i > 0 && <ChevronRight className="h-3 w-3 text-slate-300" />}
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

      {/* Center: Fake search */}
      <div className="hidden w-56 cursor-pointer items-center gap-2 rounded-lg bg-slate-100 px-3 py-1.5 sm:flex">
        <span className="flex-1 text-xs text-slate-400">Search...</span>
        <kbd className="rounded border border-slate-200 bg-white px-1 py-0.5 text-[10px] text-slate-400">
          ⌘K
        </kbd>
      </div>

      {/* Right actions */}
      <div className="flex items-center gap-3">
        <button className="relative rounded-md p-1.5 text-slate-500 transition-colors hover:bg-slate-100">
          <Bell className="h-4 w-4" />
          <span className="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-red-500" />
          <span className="sr-only">Notifications</span>
        </button>
        <div className="flex h-7 w-7 items-center justify-center rounded-full bg-sky-500/20 text-[10px] font-semibold text-sky-600">
          EE
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-500">
          SPP
        </span>
      </div>
    </header>
  )
}
