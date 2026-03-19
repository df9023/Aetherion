const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

const DEV_HEADERS: Record<string, string> = {
  "X-Dev-User-Id": process.env.NEXT_PUBLIC_DEV_USER_ID || "",
  "X-Dev-Org-Id": process.env.NEXT_PUBLIC_DEV_ORG_ID || "",
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...DEV_HEADERS,
      ...options.headers,
    },
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `API error: ${res.status}`)
  }
  return res.json()
}

export async function apiDownload(path: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: DEV_HEADERS,
  })
  if (!res.ok) {
    throw new Error(`Download failed: ${res.status}`)
  }
  return res.blob()
}
