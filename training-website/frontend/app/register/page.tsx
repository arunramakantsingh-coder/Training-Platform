"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { apiFetch } from "../../lib/api";

export default function RegisterPage(){const[name,setName]=useState("");const[email,setEmail]=useState("");const[password,setPassword]=useState("");const[type,setType]=useState("individual");const[error,setError]=useState("");const[busy,setBusy]=useState(false);
async function submit(e:FormEvent){e.preventDefault();setBusy(true);setError("");try{await apiFetch("/auth/register",{method:"POST",body:JSON.stringify({email,full_name:name,password,account_type:type})});window.location.href="/dashboard";}catch(err){setError(err instanceof Error?err.message:"Registration failed");}finally{setBusy(false);}}
return <main className="container"><section className="card form"><div className="eyebrow">Account</div><h1>Create account</h1><p className="muted">Register as an individual learner or an organization account.</p>{error&&<div className="error">{error}</div>}<form onSubmit={submit}><div className="field"><label htmlFor="name">Full name</label><input id="name" required value={name} onChange={e=>setName(e.target.value)}/></div><div className="field"><label htmlFor="email">Email</label><input id="email" type="email" required value={email} onChange={e=>setEmail(e.target.value)}/></div><div className="field"><label htmlFor="password">Password</label><input id="password" type="password" minLength={8} required value={password} onChange={e=>setPassword(e.target.value)}/></div><div className="field"><label htmlFor="type">Account type</label><select id="type" value={type} onChange={e=>setType(e.target.value)}><option value="individual">Individual</option><option value="organization">Organization</option></select></div><button className="btn btn-primary" disabled={busy} type="submit">{busy?"Creating…":"Create account"}</button></form><p className="muted">Already registered? <Link href="/login">Sign in</Link></p></section></main>;
}
