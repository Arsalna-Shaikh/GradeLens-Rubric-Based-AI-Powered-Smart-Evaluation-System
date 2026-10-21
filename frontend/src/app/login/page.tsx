"use client"

import { useState } from "react"
import Link from "next/link"
import { useAuth } from "@/context/AuthContext"
import { apiFetch } from "@/lib/api"

export default function Login() {
  const { login } = useAuth()
  const [form, setForm] = useState({ email: "", password: "" })
  const [tempToken, setTempToken] = useState<string | null>(null)
  const [code, setCode] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const data = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify(form),
      })

      if (data.requires_2fa) {
        setTempToken(data.temp_token)
      } else {
        await login(data.access_token)
      }
    } catch (err: any) {
      setError(err.data?.detail || "Login failed")
    } finally {
      setLoading(false)
    }
  }

  async function handle2fa(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const data = await apiFetch("/auth/2fa/login", {
        method: "POST",
        body: JSON.stringify({ temp_token: tempToken, code }),
      })
      await login(data.access_token)
    } catch (err: any) {
      setError(err.data?.detail || "Invalid 2FA code")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md bg-white p-8 rounded shadow">
        <h1 className="text-2xl font-bold mb-6">
          {tempToken ? "Two-factor authentication" : "Sign in"}
        </h1>

        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded text-sm">{error}</div>
        )}

        {!tempToken ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <input
                type="email"
                required
                className="w-full border rounded px-3 py-2"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <input
                type="password"
                required
                className="w-full border rounded px-3 py-2"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>
        ) : (
          <form onSubmit={handle2fa} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">TOTP code</label>
              <input
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                required
                placeholder="000000"
                className="w-full border rounded px-3 py-2"
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "Verifying…" : "Verify"}
            </button>

            <button
              type="button"
              onClick={() => {
                setTempToken(null)
                setCode("")
              }}
              className="w-full py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              Back to login
            </button>
          </form>
        )}

        <p className="mt-4 text-sm text-center">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-blue-600 hover:underline">
            Register
          </Link>
        </p>
      </div>
    </main>
  )
}
