"use client"
import { useEffect, useState } from "react"
import { apiFetch } from "@/lib/api"

type Question = { id: number; type: string; text: string; marks: number; options?: string[] | null }
type Assignment = { id: number; class_id: number; title: string; description?: string | null; total_marks: number; deadline?: string | null; questions: Question[] }
type SubmissionLite = { id: number; assignment_id: number; status: string }
type EnrolledClass = { id: number; class_id: number; class_name: string; subject: string }

const MAX_BYTES = 10 * 1024 * 1024

function isPastDeadline(deadline?: string | null) {
  return !!deadline && new Date(deadline).getTime() < Date.now()
}

function SubmitForm({ assignment, token, onDone }: { assignment: Assignment; token: string | null; onDone: () => void }) {
  const [text, setText] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    if (!text.trim() && !file) return setError("Type an answer or attach a PDF.")
    if (file && file.size > MAX_BYTES) return setError("PDF must be 10 MB or smaller.")
    if (file && !file.name.toLowerCase().endsWith(".pdf")) return setError("Only .pdf files are accepted.")
    const form = new FormData()
    if (text.trim()) form.append("content_text", text)
    if (file) form.append("file", file)
    setBusy(true)
    try {
      await apiFetch(`/submissions/assignments/${assignment.id}`, { method: "POST", body: form }, token)
      setText(""); setFile(null); onDone()
    } catch (err: any) {
      const detail = err.data?.detail
      setError(typeof detail === "string" ? detail : err.message || "Submission failed")
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit} className="mt-3 grid gap-2">
      <textarea value={text} onChange={e => setText(e.target.value)} rows={4} placeholder="Type your answer (answer each question in order)" className="border rounded px-3 py-2" />
      <input type="file" accept="application/pdf,.pdf" onChange={e => setFile(e.target.files?.[0] || null)} />
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <button disabled={busy} className="bg-blue-600 text-white rounded px-4 py-2 w-fit disabled:opacity-50">{busy ? "Submitting..." : "Submit"}</button>
    </form>
  )
}

function AssignmentCard({ a, submission, token, onDone }: { a: Assignment; submission?: SubmissionLite; token: string | null; onDone: () => void }) {
  const [open, setOpen] = useState(false)
  const past = isPastDeadline(a.deadline)
  return (
    <div className="border rounded p-3">
      <div className="flex justify-between gap-2 flex-wrap">
        <b>{a.title}</b>
        <span className="text-sm text-gray-600">{a.total_marks} marks · Deadline: {a.deadline ? new Date(a.deadline).toLocaleString() : "none"}</span>
      </div>
      {a.description && <p className="text-sm text-gray-700 mt-1">{a.description}</p>}
      <ol className="list-decimal ml-5 mt-2 text-sm">
        {a.questions.map(q => (
          <li key={q.id}>{q.text} <span className="text-gray-500">({q.marks} marks)</span>
            {q.options && q.options.length > 0 && <ul className="list-[lower-alpha] ml-5">{q.options.map((o, i) => <li key={i}>{o}</li>)}</ul>}
          </li>
        ))}
      </ol>
      <div className="mt-2 text-sm">
        {submission ? <span className="text-green-700">Submitted — status: {submission.status}</span>
          : past ? <span className="text-red-600">Deadline passed — not submitted</span>
          : <span className="text-amber-700">Not submitted</span>}
      </div>
      {!submission && !past && (open
        ? <SubmitForm assignment={a} token={token} onDone={() => { setOpen(false); onDone() }} />
        : <button onClick={() => setOpen(true)} className="mt-2 border rounded px-3 py-1">Submit work</button>)}
    </div>
  )
}

export function StudentAssignments({ classes, submissions, token, onSubmitted }: { classes: EnrolledClass[]; submissions: SubmissionLite[]; token: string | null; onSubmitted: () => void }) {
  const [byClass, setByClass] = useState<Record<number, Assignment[]>>({})
  const [errors, setErrors] = useState<Record<number, string>>({})

  useEffect(() => {
    if (!token) return
    classes.forEach(async c => {
      try {
        const rows = await apiFetch(`/assignments/class/${c.class_id}`, {}, token)
        setByClass(prev => ({ ...prev, [c.class_id]: rows || [] }))
      } catch (err: any) {
        setErrors(prev => ({ ...prev, [c.class_id]: err.message || "Could not load assignments" }))
      }
    })
  }, [classes, token])

  if (classes.length === 0) return <p className="text-gray-500">Enroll in a class with a join code to see its assignments.</p>

  return (
    <div className="grid gap-4">
      {classes.map(c => (
        <div key={c.id} className="border rounded p-4 bg-white">
          <div className="mb-2"><b>{c.class_name}</b><span className="ml-3 text-gray-600">{c.subject}</span></div>
          {errors[c.class_id] && <p className="text-red-600 text-sm">{errors[c.class_id]}</p>}
          {!byClass[c.class_id] ? <p className="text-sm text-gray-500">Loading assignments...</p>
            : byClass[c.class_id].length === 0 ? <p className="text-sm text-gray-500">No assignments yet.</p>
            : <div className="grid gap-2">{byClass[c.class_id].map(a => (
                <AssignmentCard key={a.id} a={a} token={token} onDone={onSubmitted} submission={submissions.find(s => s.assignment_id === a.id)} />
              ))}</div>}
        </div>
      ))}
    </div>
  )
}
