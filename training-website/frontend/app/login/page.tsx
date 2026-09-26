"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { apiFetch } from "../../lib/api";

export default function LoginPage() {
  const [email,setEmail]=useState(""); const [password,setPassword]=useState(""); const [error,setError]=useState(""); const [busy,setBusy]=useState(false);
  async function submit(e:FormEvent){e.preventDefault();setBusy(true);setError("");try{await apiFetch("/api/v1/auth/login",{method:"POST",body:JSON.stringify({email,password})});window.location.href="/dashboard";}catch(err){setError(err instanceof Error?err.message:"Login failed");}finally{setBusy(false);}}
  return <main className="container"><section className="card form"><div className="eyebrow">Account</div><h1>Sign in</h1><p className="muted">Use your Training Platform account.</p>{error&&<div className="error">{error}</div>}<form onSubmit={submit}><div className="field"><label htmlFor="email">Email</label><input id="email" type="email" required value={email} onChange={e=>setEmail(e.target.value)}/></div><div className="field"><label htmlFor="password">Password</label><input id="password" type="password" required value={password} onChange={e=>setPassword(e.target.value)}/></div><button className="btn btn-primary" disabled={busy} type="submit">{busy?"Signing in…":"Sign in"}</button></form><p className="muted">New learner? <Link href="/register">Create an account</Link></p></section></main>;
}
