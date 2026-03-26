import { getToken, removeToken } from "./auth"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

const DEV_HEADERS: Record<string, string> = {
  "X-Dev-User-Id": process.env.NEXT_PUBLIC_DEV_USER_ID || "",
  "X-Dev-Org-Id": process.env.NEXT_PUBLIC_DEV_ORG_ID || "",
}

function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = { ...DEV_HEADERS }
  const token = getToken()
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }
  return headers
}

function handleUnauthorized(status: number): void {
  if (status === 401) {
    removeToken()
    if (typeof window !== "undefined") {
      window.location.href = "/login"
    }
  }
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
      ...options.headers,
    },
  })
  if (!res.ok) {
    handleUnauthorized(res.status)
    if (res.status === 429) {
      throw new Error("Please wait before trying again.")
    }
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `API error: ${res.status}`)
  }
  return res.json()
}

export async function apiUpload<T>(path: string, formData: FormData): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: formData,
  })
  if (!res.ok) {
    handleUnauthorized(res.status)
    if (res.status === 429) {
      throw new Error("Please wait before trying again.")
    }
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `API error: ${res.status}`)
  }
  return res.json()
}

export async function apiDownload(path: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: getAuthHeaders(),
  })
  if (!res.ok) {
    handleUnauthorized(res.status)
    if (res.status === 429) {
      throw new Error("Please wait before trying again.")
    }
    throw new Error(`Download failed: ${res.status}`)
  }
  return res.blob()
}
