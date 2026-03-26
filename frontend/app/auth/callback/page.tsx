"use client"

import { Suspense, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { setToken } from "@/lib/auth"

function CallbackHandler() {
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    const token = searchParams.get("token")
    if (token) {
      setToken(token)
      router.replace("/cases")
    } else {
      router.replace("/login")
    }
  }, [router, searchParams])

  return <p className="text-sm text-slate-400">Signing you in...</p>
}

export default function AuthCallbackPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950">
      <Suspense fallback={<p className="text-sm text-slate-400">Loading...</p>}>
        <CallbackHandler />
      </Suspense>
    </div>
  )
}
