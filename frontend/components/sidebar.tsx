"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Briefcase, Users, BookOpen, Settings } from "lucide-react"
import { Separator } from "@/components/ui/separator"

const navItems = [
  { label: "Cases", icon: Briefcase, href: "/cases" },
  { label: "Clients", icon: Users, href: "/clients" },
  { label: "Knowledge Base", icon: BookOpen, href: "/knowledge" },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 z-20 flex h-full w-64 flex-col bg-slate-950">
      <div className="px-6 py-5">
        <Link href="/cases" className="flex items-center gap-2">
          <span className="text-sky-400 text-lg">&#9670;</span>
          <span className="text-lg font-bold text-white">Aetherion</span>
        </Link>
      </div>

      <Separator className="bg-slate-800" />

      <nav className="mt-4 flex-1 space-y-1 px-3">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href)
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-r-lg px-4 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? "border-l-2 border-sky-400 bg-sky-500/10 text-sky-400"
                  : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-100"
              }`}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          )
        })}
      </nav>

      <div className="mt-auto border-t border-slate-800 px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-sky-500/20 text-xs font-medium text-sky-400">
            EE
          </div>
          <div className="flex-1 min-w-0">
            <p className="truncate text-sm font-medium text-slate-200">Erik Eriksson</p>
            <p className="text-xs text-slate-500">Advisor</p>
          </div>
          <button className="text-slate-500 hover:text-slate-300 transition-colors">
            <Settings className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}
