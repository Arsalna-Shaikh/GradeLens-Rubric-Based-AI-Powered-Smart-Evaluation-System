"use client"
import { useEffect, useState } from "react"
import Link from "next/link"
import { ProtectedRoute } from "@/components/ProtectedRoute"
import { RoleGuard } from "@/components/RoleGuard"
import { useAuth } from "@/context/AuthContext"
import { apiFetch } from "@/lib/api"

type ClassItem={id:number;name:string;subject:string}
type Q={type:string;text:string;marks:number;rubric:string;sample_answer:string;options:string[];correct_answer:string}
const blankQuestion=():Q=>({type:"written",text:"",marks:10,rubric:"",sample_answer:"",options:["","","",""],correct_answer:""})

function errorMessage(e:any):string{
 const detail=e?.data?.detail
 if(typeof detail==="string") return detail
 if(Array.isArray(detail)) return detail.map((d:any)=>String(d?.msg||"").replace(/^Value error, /,"")).filter(Boolean).join("; ")||"Please check the form fields"
 return e?.message||"Saving failed"
}

function toPayload(q:Q){
 const base={type:q.type,text:q.text,marks:q.marks,rubric:q.rubric||null,sample_answer:q.sample_answer||null}
 return q.type==="mcq"?{...base,options:q.options.map(o=>o.trim()),correct_answer:q.correct_answer}:base
}

function validate(questions:Q[]):string{
 for(const [i,q] of questions.entries()){
  if(q.type==="mcq"){
   if(q.options.some(o=>!o.trim())) return `Question ${i+1}: multiple choice needs four non-empty options`
   if(!q.correct_answer||!q.options.map(o=>o.trim()).includes(q.correct_answer)) return `Question ${i+1}: choose the correct answer`
  }
  if(q.type==="written"&&!q.rubric.trim()&&!q.sample_answer.trim()) return `Question ${i+1}: written questions need a rubric or sample answer`
 }
 return ""
}

export default function AssignmentsPage(){return <ProtectedRoute><RoleGuard role="teacher"><AssignmentAuthoring/></RoleGuard></ProtectedRoute>}

function AssignmentAuthoring(){
 const {token}=useAuth(); const [classes,setClasses]=useState<ClassItem[]>([]); const [classId,setClassId]=useState(""); const [title,setTitle]=useState(""); const [description,setDescription]=useState(""); const [deadline,setDeadline]=useState(""); const [questions,setQuestions]=useState<Q[]>([blankQuestion()]); const [message,setMessage]=useState(""); const [error,setError]=useState(""); const [saving,setSaving]=useState(false)
 useEffect(()=>{if(token) apiFetch("/classes/mine",{},token).then(setClasses).catch((e:any)=>setError(errorMessage(e)))},[token])
 const totalMarks=questions.reduce((sum,q)=>sum+(Number(q.marks)||0),0)
 function update(i:number,key:keyof Q,value:string|number){setQuestions(q=>q.map((x,n)=>n===i?{...x,[key]:value}:x))}
 function updateOption(i:number,o:number,value:string){setQuestions(q=>q.map((x,n)=>{if(n!==i)return x;const old=x.options[o];const options=x.options.map((v,k)=>k===o?value:v);return {...x,options,correct_answer:x.correct_answer===old.trim()?value.trim():x.correct_answer}}))}
 function remove(i:number){setQuestions(q=>q.length>1?q.filter((_,n)=>n!==i):q)}
 async function submit(e:React.FormEvent){
  e.preventDefault();setMessage("");setError("")
  const problem=validate(questions); if(problem){setError(problem);return}
  const body:Record<string,unknown>={title,description,questions:questions.map(toPayload)}
  if(deadline) body.deadline=new Date(deadline).toISOString()
  setSaving(true)
  try{await apiFetch(`/assignments/class/${classId}`,{method:"POST",body:JSON.stringify(body)},token);setMessage("Assignment saved");setTitle("");setDescription("");setDeadline("");setQuestions([blankQuestion()])}
  catch(e:any){setError(errorMessage(e))}
  finally{setSaving(false)}
 }
 return <main className="min-h-screen p-6"><div className="max-w-3xl mx-auto">
  <Link href="/teacher" className="inline-block mb-4 px-3 py-1 border rounded text-sm hover:bg-gray-50">← Back to dashboard</Link>
  <h1 className="text-3xl font-bold mb-2">Assignment authoring</h1>
  <p className="text-gray-600 mb-6">Configure questions, sample answers, and transparent rubric criteria.</p>
  <form onSubmit={submit} className="space-y-4">
   <select required value={classId} onChange={e=>setClassId(e.target.value)} className="border rounded p-2 w-full"><option value="">Choose a class</option>{classes.map(c=><option key={c.id} value={c.id}>{c.name} · {c.subject}</option>)}</select>
   <input required placeholder="Assignment title" value={title} onChange={e=>setTitle(e.target.value)} className="border rounded p-2 w-full"/>
   <textarea placeholder="Description" value={description} onChange={e=>setDescription(e.target.value)} className="border rounded p-2 w-full"/>
   <label className="block text-sm">Deadline (optional)<input type="datetime-local" value={deadline} onChange={e=>setDeadline(e.target.value)} className="border rounded p-2 w-full mt-1"/></label>
   <p className="text-sm text-gray-700">Total marks: <strong>{totalMarks}</strong></p>
   {questions.map((q,i)=><section key={i} className="border rounded p-4 space-y-2">
    <div className="flex justify-between items-center"><h2 className="font-semibold">Question {i+1}</h2>{questions.length>1&&<button type="button" onClick={()=>remove(i)} className="text-sm text-red-600">Remove</button>}</div>
    <select value={q.type} onChange={e=>update(i,"type",e.target.value)} className="border rounded p-2"><option value="written">Written</option><option value="short_answer">Short answer</option><option value="mcq">Multiple choice</option></select>
    <textarea required placeholder="Question text" value={q.text} onChange={e=>update(i,"text",e.target.value)} className="border rounded p-2 w-full"/>
    <label className="block text-sm">Marks <input type="number" min="0" value={q.marks} onChange={e=>update(i,"marks",Number(e.target.value))} className="border rounded p-2 w-24 ml-2"/></label>
    {q.type==="mcq"&&<div className="space-y-2">
     {q.options.map((opt,o)=><input key={o} required placeholder={`Option ${o+1}`} value={opt} onChange={e=>updateOption(i,o,e.target.value)} className="border rounded p-2 w-full"/>)}
     <select required value={q.correct_answer} onChange={e=>update(i,"correct_answer",e.target.value)} className="border rounded p-2 w-full"><option value="">Correct answer</option>{q.options.map((opt,o)=>opt.trim()?<option key={o} value={opt.trim()}>{opt.trim()}</option>:null)}</select>
    </div>}
    <textarea placeholder={q.type==="written"?"Rubric criteria (rubric or sample answer required)":"Rubric criteria"} value={q.rubric} onChange={e=>update(i,"rubric",e.target.value)} className="border rounded p-2 w-full"/>
    <textarea placeholder="Sample answer" value={q.sample_answer} onChange={e=>update(i,"sample_answer",e.target.value)} className="border rounded p-2 w-full"/>
   </section>)}
   <button type="button" onClick={()=>setQuestions([...questions,blankQuestion()])} className="border rounded px-4 py-2">+ Add question</button>
   <button disabled={saving} className="bg-blue-600 disabled:bg-gray-400 text-white rounded px-5 py-2 ml-2">{saving?"Saving…":"Save assignment"}</button>
   {error&&<p className="text-red-600">{error}</p>}
   {message&&<p className="text-green-700">{message}</p>}
  </form>
 </div></main>
}
