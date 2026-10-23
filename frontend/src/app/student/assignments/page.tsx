"use client"
import { useEffect, useState } from "react"
import Link from "next/link"
import { ProtectedRoute } from "@/components/ProtectedRoute"
import { RoleGuard } from "@/components/RoleGuard"
import { AssignmentSubmitForm } from "@/components/AssignmentSubmitForm"
import { useAuth } from "@/context/AuthContext"
import { apiFetch } from "@/lib/api"

type Enrollment = { id: number; class_id: number; class_name: string; subject: string }
type Question = { id: number; text: string; marks: number; options?: string[] | null }
type Assignment = { id: number; class_id: number; title: string; description: string | null; total_marks: number; deadline: string | null; questions?: Question[] }
type Submission = { id: number; assignment_id: number; status: string }
type Group = { classId: number; className: string; assignments: Assignment[]; error?: string }

export default function StudentAssignmentsPage() {
  return <ProtectedRoute><RoleGuard role="student"><StudentAssignmentsList /></RoleGuard></ProtectedRoute>
}

function formatDeadline(value: string | null) {
  if (!value) return "No deadline"
  const d = new Date(value)
  return isNaN(d.getTime()) ? value : d.toLocaleString()
}

function StudentAssignmentsList() {
  const { token } = useAuth()
  const [groups, setGroups] = useState<Group[]>([])
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [selected, setSelected] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  async function loadSubmissions() {
    setSubmissions(await apiFetch("/submissions/mine", {}, token))
  }

  async function load() {
    setLoading(true); setError("")
    try {
      const enrollments: Enrollment[] = await apiFetch("/classes/enrolled", {}, token)
      const loaded = await Promise.all(enrollments.map(async (en): Promise<Group> => {
        try {
          const assignments: Assignment[] = await apiFetch(`/assignments/class/${en.class_id}`, {}, token)
          return { classId: en.class_id, className: en.class_name, assignments }
        } catch (e: any) {
          return { classId: en.class_id, className: en.class_name, assignments: [], error: e.message }
        }
      }))
      setGroups(loaded)
      await loadSubmissions()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { if (token) load() }, [token])

  const submissionFor = (id: number) => submissions.find(s => s.assignment_id === id)

  async function handleSubmitted(message: string) {
    setSelected(null); setSuccess(message)
    try { await loadSubmissions() } catch (e: any) { setError(e.message) }
  }

  return (
    <main className="min-h-screen p-6"><div className="max-w-4xl mx-auto">
      <Link href="/student" className="inline-block mb-4 px-3 py-1 border rounded text-sm hover:bg-gray-50">← Back to dashboard</Link>
      <h1 className="text-3xl font-bold mb-6">My assignments</h1>
      {error && <p className="text-red-600 mb-4">{error}</p>}
      {success && <p className="text-green-700 mb-4">{success}</p>}
      {loading ? <p className="text-gray-500">Loading…</p> : groups.length === 0 ? (
        <p className="text-gray-500">You are not enrolled in any classes yet. Enroll with a join code on your dashboard.</p>
      ) : groups.map(g => (
        <section key={g.classId} className="mb-8">
          <h2 className="text-xl font-semibold mb-3">{g.className}</h2>
          {g.error && <p className="text-red-600 text-sm">{g.error}</p>}
          {g.assignments.length === 0 && !g.error && <p className="text-gray-500 text-sm">No assignments yet.</p>}
          <div className="grid gap-3">
            {g.assignments.map(a => {
              const sub = submissionFor(a.id)
              return (
                <article key={a.id} className="border rounded p-4 bg-white">
                  <div className="flex justify-between items-start gap-4">
                    <div>
                      <h3 className="font-semibold">{a.title}</h3>
                      {a.description && <p className="text-sm text-gray-700 mt-1">{a.description}</p>}
                      <p className="text-sm text-gray-600 mt-2">Total marks: {a.total_marks} · Deadline: {formatDeadline(a.deadline)}</p>
                      <p className={`text-sm mt-1 ${sub ? "text-green-700" : "text-gray-500"}`}>{sub ? `Submitted (${sub.status})` : "Not submitted"}</p>
                    </div>
                    {!sub && <button onClick={() => { setSelected(a.id); setSuccess("") }} className="bg-blue-600 text-white rounded px-4 py-2 shrink-0">Submit work</button>}
                  </div>
                  {a.questions && a.questions.length > 0 && (
                    <ol className="list-decimal ml-5 mt-3 text-sm">
                      {a.questions.map(q => (
                        <li key={q.id}>{q.text} <span className="text-gray-500">({q.marks} marks)</span>
                          {q.options && q.options.length > 0 && <ul className="list-[lower-alpha] ml-5">{q.options.map((o, i) => <li key={i}>{o}</li>)}</ul>}
                        </li>
                      ))}
                    </ol>
                  )}
                  {selected === a.id && !sub && (
                    <AssignmentSubmitForm assignmentId={a.id} title={a.title} token={token} onCancel={() => setSelected(null)} onSubmitted={handleSubmitted} />
                  )}
                </article>
              )
            })}
          </div>
        </section>
      ))}
    </div></main>
  )
}
