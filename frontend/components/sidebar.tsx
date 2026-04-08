"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, Briefcase, Users, Building2, BookOpen, Lightbulb, Shield, LogOut } from "lucide-react"
import { cn } from "@/lib/utils"
import {
  useCases,
  useClients,
  useClientOrganizations,
  useKnowledge,
  useFirmInsights,
  useRegulatoryChanges,
} from "@/lib/hooks"

export function Sidebar() {
  const pathname = usePathname()
  const { data: cases } = useCases()
  const { data: clients } = useClients()
  const { data: clientOrgs } = useClientOrganizations()
  const { data: knowledge } = useKnowledge()
  const { data: insights } = useFirmInsights()
  const { data: regChanges } = useRegulatoryChanges({ is_active: "true" })

  const navItems = [
    { href: "/dashboard", icon: LayoutDashboard, label: "Översikt" },
    { href: "/cases", icon: Briefcase, label: "Ärenden", badge: cases?.filter((c) => c.status !== "archived").length },
    { href: "/clients", icon: Users, label: "Klienter", badge: clients?.length },
    { href: "/organizations", icon: Building2, label: "Organisationer", badge: clientOrgs?.length },
    { href: "/knowledge", icon: BookOpen, label: "Kunskapsbas", badge: knowledge?.length },
    { href: "/insights", icon: Lightbulb, label: "Insikter", badge: insights?.length },
    { href: "/regulatory", icon: Shield, label: "Regulatorisk pulse", badge: regChanges?.length },
  ]

  return (
    <aside className="fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-slate-950">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-sky-400 to-blue-600 shadow-md">
          <span className="text-sm font-bold text-white">A</span>
        </div>
        <span className="text-lg font-bold text-white">Aetherion</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 border-t border-slate-800 px-3 pt-5">
        <ul className="space-y-1">
          {navItems.map(({ href, icon: Icon, label, badge }) => {
            const isActive = pathname.startsWith(href)
            return (
              <li key={href}>
                <Link
                  href={href}
                  className={cn(
                    "group flex items-center justify-between rounded-lg px-3 py-2.5 text-sm transition-all duration-150",
                    isActive
                      ? "border-l-2 border-sky-400 bg-sky-500/10 pl-[10px] text-sky-400"
                      : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="h-5 w-5 shrink-0" />
                    <span className="font-medium">{label}</span>
                  </div>
                  {badge !== undefined && (
                    <span className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-400">
                      {badge}
                    </span>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* User area */}
      <div className="border-t border-slate-800 px-3 py-4">
        <div className="flex items-center gap-3 px-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-sky-500/20 text-sm font-semibold text-sky-400">
            EE
          </div>
          <div className="flex flex-1 flex-col">
            <span className="text-sm font-medium text-slate-300">Erik Eriksson</span>
            <span className="text-xs text-slate-500">Rådgivare</span>
          </div>
          <button
            className="rounded-md p-2 text-slate-500 transition-colors hover:bg-slate-800 hover:text-slate-300"
            title="Logga ut"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}
