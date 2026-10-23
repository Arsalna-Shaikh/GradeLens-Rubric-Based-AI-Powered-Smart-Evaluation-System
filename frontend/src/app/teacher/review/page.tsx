"use client"
import { useEffect, useState } from "react"
import { useAuth } from "@/context/AuthContext"
import { apiFetch } from "@/lib/api"

type Item={id:number;assignment_id:number;student_id:number;status:string}
type Answer={id:number;question_id:number;ai_score:number|null;ai_feedback:string|null;teacher_score:number|null;teacher_feedback:string|null;is_approved:boolean}
export default function ReviewPage(){
 const {token}=useAuth(); const [items,setItems]=useState<Item[]>([]); const [selected,setSelected]=useState<any>(null); const [msg,setMsg]=useState("")
 useEffect(()=>{if(token) apiFetch("/submissions/for-grading",{},token).then(setItems)},[token])
 async function open(id:number){setSelected(await apiFetch(`/review/submissions/${id}`,{},token))}
 async function save(a:Answer){const score=prompt("Teacher score",String(a.teacher_score ?? a.ai_score ?? "")); const feedback=prompt("Teacher feedback",a.teacher_feedback ?? a.ai_feedback ?? ""); if(score===null||feedback===null)return; const next=await apiFetch(`/review/submissions/${selected.id}/answers/${a.id}`,{method:"PATCH",body:JSON.stringify({teacher_score:Number(score),teacher_feedback:feedback})},token);setSelected(next)}
 async function release(){try{await apiFetch(`/review/submissions/${selected.id}/release`,{method:"POST"},token);setMsg("Released to student");setSelected({...selected,status:"released"})}catch(e:any){setMsg(e.message)}}
 return <main className="min-h-screen p-6"><div className="max-w-4xl mx-auto"><h1 className="text-3xl font-bold">Review & approval</h1><p className="text-gray-600 my-2">AI grades remain drafts until you edit, approve, and release them.</p>{msg&&<p className="border rounded p-3 my-3">{msg}</p>}<div className="grid md:grid-cols-2 gap-6 mt-6"><section className="space-y-2">{items.map(i=><button onClick={()=>open(i.id)} className="block w-full text-left border rounded p-3 hover:bg-gray-50" key={i.id}>Submission #{i.id} · {i.status}</button>)}</section>{selected&&<section className="space-y-3"><h2 className="font-semibold">Submission #{selected.id}</h2>{selected.answers.map((a:Answer)=><article className="border rounded p-3" key={a.id}><p>Question {a.question_id}: <b>{a.teacher_score ?? a.ai_score ?? "Needs grading"}</b></p><p className="text-sm text-gray-600">{a.teacher_feedback ?? a.ai_feedback}</p><button onClick={()=>save(a)} className="mt-2 border rounded px-3 py-1">Edit feedback/score</button></article>)}<button disabled={selected.status==="released"} onClick={release} className="bg-blue-600 disabled:bg-gray-400 text-white rounded px-4 py-2">Approve & release</button></section>}</div></div></main>
}