"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Sidebar } from "@/components/sidebar"
import { Providers } from "@/components/providers"
import { Toaster } from "@/components/ui/sonner"
import { isAuthenticated } from "@/lib/auth"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [checked, setChecked] = useState(false)

  useEffect(() => {
    // In dev mode, skip auth check if dev headers are configured
    const devUserId = process.env.NEXT_PUBLIC_DEV_USER_ID
    if (devUserId) {
      setChecked(true)
      return
    }
    if (!isAuthenticated()) {
      router.replace("/login")
      return
    }
    setChecked(true)
  }, [router])

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
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

  if (!checked) {
    return null
  }

  return (
    <Providers>
      <div className="min-h-screen bg-slate-50">
        <Sidebar />
        <div className="ml-64 flex min-h-screen flex-col">
          {children}
        </div>
      </div>
      <Toaster />
    </Providers>
  )
}
