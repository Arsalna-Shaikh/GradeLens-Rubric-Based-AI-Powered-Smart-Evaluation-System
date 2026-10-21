"use client"

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"

type User = {
  id: number
  name: string
  email: string
  role: "teacher" | "student"
  totp_enabled: boolean
}

type AuthContextType = {
  user: User | null
  token: string | null
  loading: boolean
  login: (token: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const TOKEN_KEY = "gradelens_token"

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const stored = typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null
    if (stored) {
      setToken(stored)
      fetchUser(stored)
    } else {
      setLoading(false)
    }
  }, [])

  async function fetchUser(currentToken: string) {
    try {
      const data = await apiFetch("/auth/me", {}, currentToken)
      setUser(data)
    } catch {
      localStorage.removeItem(TOKEN_KEY)
      setToken(null)
    } finally {
      setLoading(false)
    }
  }

  async function login(newToken: string) {
    localStorage.setItem(TOKEN_KEY, newToken)
    setToken(newToken)
    const data = await apiFetch("/auth/me", {}, newToken)
    setUser(data)
    if (data.role === "teacher") {
      router.push("/teacher")
    } else {
      router.push("/student")
    }
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
    router.push("/login")
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
