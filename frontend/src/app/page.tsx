"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { apiFetch } from "@/lib/api"

export default function Home() {
  const [status, setStatus] = useState<"loading" | "ok" | "error">("loading")
  const [detail, setDetail] = useState("")

  useEffect(() => {
    apiFetch("/health")
      .then((data) => {
        setStatus(data.db === "ok" ? "ok" : "error")
        setDetail(JSON.stringify(data))
      })
      .catch((err) => {
        setStatus("error")
        setDetail(err.message)
      })
  }, [])

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-6">
      <h1 className="text-4xl font-bold mb-4">GradeLens</h1>
      <p className="text-gray-600 mb-8">Rubric-based AI-powered evaluation platform</p>

      <div className="mb-8 flex items-center gap-3">
        <span className="font-semibold">Backend status:</span>
        {status === "loading" && <span>Checking…</span>}
        {status === "ok" && <span className="text-green-600 font-semibold">Connected</span>}
        {status === "error" && <span className="text-red-600 font-semibold">Error</span>}
      </div>

      {detail && (
        <pre className="bg-gray-100 p-4 rounded text-sm mb-8 max-w-md overflow-auto">
          {detail}
        </pre>
      )}

      <div className="flex gap-4">
        <Link
          href="/register"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Register
        </Link>
        <Link
          href="/login"
          className="px-4 py-2 border border-blue-600 text-blue-600 rounded hover:bg-blue-50"
        >
          Login
        </Link>
      </div>
    </main>
  )
}
