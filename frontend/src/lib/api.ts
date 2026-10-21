const API_BASE =
  typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL
    ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")
    : ""

function buildUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`
  if (API_BASE) {
    return `${API_BASE}${normalized}`
  }
  // Shared-origin proxy: Next.js rewrites /api/* to the FastAPI backend.
  return `/api${normalized}`
}

export async function apiFetch(
  path: string,
  options: RequestInit = {},
  token?: string | null
) {
  const url = buildUrl(path)
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
    // Some preview proxies strip Authorization; FastAPI also accepts this fallback.
    headers["X-Auth-Token"] = token
  }

  const response = await fetch(url, { ...options, headers })
  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const error = new Error(
      data?.detail || `Request failed with status ${response.status}`
    )
    ;(error as any).status = response.status
    ;(error as any).data = data
    throw error
  }

  return data
}
