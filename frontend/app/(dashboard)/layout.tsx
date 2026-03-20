"use client"

import { useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { TopBar } from "@/components/top-bar"
import { Providers } from "@/components/providers"
import { Toaster } from "@/components/ui/sonner"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Skip if user is typing in an input/textarea
      const tag = (e.target as HTMLElement).tagName
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return

      if (e.key === "/") {
        e.preventDefault()
        const searchInput = document.querySelector<HTMLInputElement>("[data-search-input]")
        searchInput?.focus()
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  return (
    <Providers>
      <div className="min-h-screen bg-slate-50">
        <Sidebar />
        <div className="ml-64 min-h-screen">
          <TopBar />
          <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
        </div>
      </div>
      <Toaster />
    </Providers>
  )
}
