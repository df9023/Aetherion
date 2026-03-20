"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Briefcase, Users, BookOpen, Settings } from "lucide-react"
import { Separator } from "@/components/ui/separator"
import { useCases, useClients, useKnowledge } from "@/lib/hooks"

export function Sidebar() {
  const pathname = usePathname()
  const { data: cases } = useCases()
  const { data: clients } = useClients()
  const { data: knowledge } = useKnowledge()

  const activeCaseCount = cases?.filter((c) => c.status !== "archived").length
  const clientCount = clients?.length
  const knowledgeCount = knowledge?.length

  const navItems = [
    { label: "Cases", icon: Briefcase, href: "/cases", count: activeCaseCount },
    { label: "Clients", icon: Users, href: "/clients", count: clientCount },
    { label: "Knowledge Base", icon: BookOpen, href: "/knowledge", count: knowledgeCount },
  ]

  return (
    <aside className="fixed left-0 top-0 z-20 flex h-full w-64 flex-col bg-slate-950">
      <div className="px-6 py-5">
        <Link href="/cases" className="flex items-center gap-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-sky-400 to-blue-600 shadow-[inset_0_1px_1px_rgba(255,255,255,0.3)]">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 1L12.5 4.5V9.5L7 13L1.5 9.5V4.5L7 1Z" fill="white" fillOpacity="0.9" />
            </svg>
          </div>
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
              <span className="flex-1">{item.label}</span>
              {item.count !== undefined && (
                <span className="rounded-full bg-slate-700 px-1.5 py-0.5 text-[10px] font-medium text-slate-300">
                  {item.count}
                </span>
              )}
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
