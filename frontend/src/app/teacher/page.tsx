"use client"
import { useEffect, useState } from "react"
import Link from "next/link"
import { ProtectedRoute } from "@/components/ProtectedRoute"
import { RoleGuard } from "@/components/RoleGuard"
import { useAuth } from "@/context/AuthContext"
import { apiFetch } from "@/lib/api"

type ClassItem = { id:number; name:string; subject:string; join_code:string; enrolled_count:number }
export default function TeacherDashboardPage(){return <ProtectedRoute><RoleGuard role="teacher"><TeacherDashboard/></RoleGuard></ProtectedRoute>}
function TeacherDashboard(){
 const {user,token,logout}=useAuth(); const [items,setItems]=useState<ClassItem[]>([]); const [name,setName]=useState(""); const [subject,setSubject]=useState(""); const [error,setError]=useState("")
 async function load(){try{setItems(await apiFetch("/classes/mine",{},token))}catch(e:any){setError(e.message)}}
 useEffect(()=>{if(token) load()},[token])
 async function create(e:React.FormEvent){e.preventDefault();setError("");try{await apiFetch("/classes",{method:"POST",body:JSON.stringify({name,subject})},token);setName("");setSubject("");load()}catch(e:any){setError(e.message)}}
 return <main className="min-h-screen p-6"><div className="max-w-4xl mx-auto"><div className="flex justify-between mb-6"><h1 className="text-3xl font-bold">Teacher Dashboard</h1><button onClick={logout} className="px-4 py-2 border rounded">Logout</button></div><p className="mb-3">Welcome, {user?.name}</p><nav className="flex flex-wrap gap-2 mb-6"><Link href="/teacher/assignments" className="px-3 py-1 border rounded text-sm hover:bg-gray-50">Create assignment</Link><Link href="/teacher/review" className="px-3 py-1 border rounded text-sm hover:bg-gray-50">Review</Link><Link href="/teacher/grading" className="px-3 py-1 border rounded text-sm hover:bg-gray-50">Grading</Link><Link href="/teacher/analytics" className="px-3 py-1 border rounded text-sm hover:bg-gray-50">Analytics</Link></nav><form onSubmit={create} className="flex gap-2 mb-6"><input required placeholder="Class name" value={name} onChange={e=>setName(e.target.value)} className="border rounded px-3 py-2"/><input required placeholder="Subject" value={subject} onChange={e=>setSubject(e.target.value)} className="border rounded px-3 py-2"/><button className="bg-blue-600 text-white rounded px-4">Create class</button></form>{error&&<p className="text-red-600">{error}</p>}<div className="grid gap-3">{items.map(item=><div className="border rounded p-4" key={item.id}><b>{item.name}</b><span className="ml-3 text-gray-600">{item.subject}</span><p className="text-sm mt-2">Join code: <strong>{item.join_code}</strong> · {item.enrolled_count} students</p></div>)}</div></div></main>
}