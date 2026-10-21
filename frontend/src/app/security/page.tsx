"use client"

import { useState } from "react"
import { useAuth } from "@/context/AuthContext"
import { apiFetch } from "@/lib/api"
import { ProtectedRoute } from "@/components/ProtectedRoute"

export default function SecurityPage() {
  return (
    <ProtectedRoute>
      <Security />
    </ProtectedRoute>
  )
}

function Security() {
  const { token, user } = useAuth()
  const [qrCode, setQrCode] = useState<string | null>(null)
  const [secret, setSecret] = useState<string | null>(null)
  const [code, setCode] = useState("")
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function setup() {
    setError("")
    setMessage("")
    setLoading(true)

    try {
      const data = await apiFetch(
        "/auth/2fa/setup",
        { method: "POST" },
        token
      )
      setQrCode(data.qr_code)
      setSecret(data.secret)
    } catch (err: any) {
      setError(err.data?.detail || "Failed to start 2FA setup")
    } finally {
      setLoading(false)
    }
  }

  async function verify(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setMessage("")
    setLoading(true)

    try {
      const data = await apiFetch(
        "/auth/2fa/verify",
        { method: "POST", body: JSON.stringify({ code }) },
        token
      )
      setMessage(data.message)
      setCode("")
    } catch (err: any) {
      setError(err.data?.detail || "Invalid code")
    } finally {
      setLoading(false)
    }
  }

  if (user?.totp_enabled) {
    return (
      <main className="min-h-screen p-6">
        <div className="max-w-xl mx-auto bg-white p-8 rounded shadow">
          <h1 className="text-2xl font-bold mb-4">Security</h1>
          <p className="text-green-600">Two-factor authentication is enabled.</p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen p-6">
      <div className="max-w-xl mx-auto bg-white p-8 rounded shadow">
        <h1 className="text-2xl font-bold mb-4">Enable two-factor authentication</h1>

        {message && (
          <div className="mb-4 p-3 bg-green-50 text-green-700 rounded text-sm">{message}</div>
        )}
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded text-sm">{error}</div>
        )}

        {!qrCode ? (
          <button
            onClick={setup}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Generating…" : "Set up 2FA"}
          </button>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Scan the QR code with your authenticator app, then enter the 6-digit code.
            </p>
            <img src={qrCode} alt="2FA QR code" className="border rounded" />
            {secret && (
              <p className="text-xs text-gray-500 break-all">Manual entry: {secret}</p>
            )}

            <form onSubmit={verify} className="space-y-3">
              <input
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                placeholder="000000"
                required
                className="w-full border rounded px-3 py-2"
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? "Verifying…" : "Verify and enable"}
              </button>
            </form>
          </div>
        )}
      </div>
    </main>
  )
}
