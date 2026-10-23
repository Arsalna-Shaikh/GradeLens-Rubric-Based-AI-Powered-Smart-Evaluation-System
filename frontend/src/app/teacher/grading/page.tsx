"use client"
import { useEffect, useState } from "react"
import { useAuth } from "@/context/AuthContext"
import { apiFetch } from "@/lib/api"

type Submission={id:number;assignment_id:number;student_id:number;status:string}
export default function GradingPage(){
 const {token}=useAuth(); const [items,setItems]=useState<Submission[]>([]); const [message,setMessage]=useState("")
 useEffect(()=>{if(token) apiFetch("/submissions/for-grading",{},token).then(setItems).catch(()=>{})},[token])
 async function grade(id:number){try{const result=await apiFetch(`/grading/submissions/${id}`,{method:"POST"},token);setMessage(`Draft generated: ${result.total_score} marks. Review is required before release.`)}catch(e:any){setMessage(e.message)}}
 return <main className="min-h-screen p-6"><div className="max-w-3xl mx-auto"><h1 className="text-3xl font-bold">AI grading drafts</h1><p className="text-gray-600 my-3">MCQs are checked against the answer key; written feedback is an AI draft only. <a className="text-blue-600 underline" href="/teacher/review">Open review queue →</a></p>{message&&<p className="border rounded p-3 mb-4">{message}</p>}<div className="space-y-3">{items.map(s=><div className="border rounded p-4 flex justify-between" key={s.id}><span>Submission #{s.id} · Assignment {s.assignment_id} · {s.status}</span><button onClick={()=>grade(s.id)} className="bg-blue-600 text-white rounded px-3 py-1">Generate draft</button></div>)}</div></div></main>
}