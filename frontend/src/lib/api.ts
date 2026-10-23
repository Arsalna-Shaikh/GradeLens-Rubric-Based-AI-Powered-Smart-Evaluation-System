// Shared-origin proxy is the only supported browser transport in production.
const API_BASE = ""

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
  let url = buildUrl(path)
  if (token) {
    const separator = url.includes("?") ? "&" : "?"
    url = `${url}${separator}token=${encodeURIComponent(token)}`
  }
  const isForm = typeof FormData !== "undefined" && options.body instanceof FormData
  const headers: Record<string, string> = {
    ...(isForm ? {} : { "Content-Type": "application/json" }),
    ...(options.headers as Record<string, string>),
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
    // Some preview proxies strip Authorization; FastAPI also accepts this fallback.
    headers["X-Auth-Token"] = token
    headers["X-Access-Token"] = token
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
