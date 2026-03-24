'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Briefcase, Users, BookOpen, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/cases', icon: Briefcase, label: 'Cases', badge: '4' },
  { href: '/clients', icon: Users, label: 'Clients', badge: '2' },
  { href: '/knowledge', icon: BookOpen, label: 'Knowledge Base', badge: '6' },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-slate-950">
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-sky-400 to-blue-600 shadow-md">
          <span className="text-xs font-bold text-white">A</span>
        </div>
        <span className="text-lg font-bold text-white">Aetherion</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 border-t border-slate-800 px-3 pt-4">
        <p className="mb-2 px-3 text-[10px] font-medium uppercase tracking-wider text-slate-500">
          Workspace
        </p>
        <ul className="space-y-0.5">
          {navItems.map(({ href, icon: Icon, label, badge }) => {
            const isActive = pathname.startsWith(href)
            return (
              <li key={href}>
                <Link
                  href={href}
                  className={cn(
                    'group flex items-center justify-between rounded-lg px-3 py-2 text-sm transition-all duration-150',
                    isActive
                      ? 'border-l-2 border-sky-400 bg-sky-500/10 pl-[10px] text-sky-400'
                      : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="h-4 w-4 shrink-0" />
                    <span className="font-medium">{label}</span>
                  </div>
                  {badge && (
                    <span className="rounded-full bg-slate-800 px-1.5 py-0.5 text-[10px] text-slate-400">
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
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-sky-500/20 text-xs font-semibold text-sky-400">
              EE
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-medium text-slate-300">Erik Eriksson</span>
              <span className="text-xs text-slate-500">Advisor</span>
            </div>
          </div>
          <button className="rounded-md p-1 text-slate-500 transition-colors hover:bg-slate-800 hover:text-slate-300">
            <Settings className="h-4 w-4" />
            <span className="sr-only">Settings</span>
          </button>
        </div>
      </div>
    </aside>
  )
}
