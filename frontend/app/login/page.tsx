"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { isAuthenticated } from "@/lib/auth"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export default function LoginPage() {
  const router = useRouter()

  useEffect(() => {
    if (isAuthenticated()) {
      router.replace("/cases")
    }
  }, [router])

  function handleLogin() {
    window.location.href = `${API_BASE}/auth/login`
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950">
      <div className="w-full max-w-sm space-y-8 px-4">
        {/* Logo */}
        <div className="flex flex-col items-center gap-3">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-400 to-blue-600 shadow-lg">
            <span className="text-2xl font-bold text-white">A</span>
          </div>
          <div className="text-center">
            <h1 className="text-2xl font-bold text-white">Aetherion</h1>
            <p className="mt-1 text-sm text-slate-400">
              AI-native decision workspace
            </p>
          </div>
        </div>

        {/* Login card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="mb-1 text-center text-lg font-semibold text-slate-200">
            Sign in to your account
          </h2>
          <p className="mb-6 text-center text-sm text-slate-500">
            Use your organization&apos;s single sign-on
          </p>
          <Button
            onClick={handleLogin}
            size="lg"
            className="w-full bg-sky-600 text-white hover:bg-sky-500"
          >
            Sign in with SSO
          </Button>
        </div>

        <p className="text-center text-xs text-slate-600">
          Contact your administrator if you need access.
        </p>
      </div>
    </div>
  )
}
