"use client"
import { useState } from "react"
import { apiFetch } from "@/lib/api"

const MAX_BYTES = 10 * 1024 * 1024

type Props = {
  assignmentId: number
  title: string
  token: string | null
  onCancel: () => void
  onSubmitted: (message: string) => void
}

export function AssignmentSubmitForm({ assignmentId, title, token, onCancel, onSubmitted }: Props) {
  const [text, setText] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)

  function chooseFile(f: File | null) {
    setError("")
    if (f && !f.name.toLowerCase().endsWith(".pdf")) { setError("Only .pdf files are accepted"); setFile(null); return }
    if (f && f.size > MAX_BYTES) { setError("PDF must be 10 MB or smaller"); setFile(null); return }
    setFile(f)
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    if (!text.trim() && !file) { setError("Type your answer or attach a PDF"); return }
    const form = new FormData()
    if (text.trim()) form.append("content_text", text)
    if (file) form.append("file", file)
    setBusy(true)
    try {
      // apiFetch skips Content-Type for FormData so the browser sets the multipart boundary.
      await apiFetch(`/submissions/assignments/${assignmentId}`, { method: "POST", body: form }, token)
      onSubmitted(`Submitted "${title}" successfully`)
    } catch (err: any) {
      const detail = err?.data?.detail
      setError(typeof detail === "string" ? detail : err?.message || "Submission failed")
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit} className="border rounded p-4 mt-3 space-y-3 bg-gray-50">
      <h3 className="font-semibold">Submit: {title}</h3>
      <textarea placeholder="Type your answer" value={text} onChange={e => setText(e.target.value)} rows={6} className="border rounded p-2 w-full" />
      <label className="block text-sm">Or attach a PDF (max 10 MB)
        <input type="file" accept=".pdf,application/pdf" onChange={e => chooseFile(e.target.files?.[0] ?? null)} className="block mt-1" />
      </label>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <div className="flex gap-2">
        <button disabled={busy} className="bg-blue-600 disabled:bg-gray-400 text-white rounded px-4 py-2">{busy ? "Submitting…" : "Submit"}</button>
        <button type="button" onClick={onCancel} className="border rounded px-4 py-2">Cancel</button>
      </div>
    </form>
  )
}
