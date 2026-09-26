"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";
import type { Organization, User } from "../../lib/types";

export default function DashboardPage(){const[user,setUser]=useState<User|null>(null);const[orgs,setOrgs]=useState<Organization[]>([]);const[name,setName]=useState("");const[error,setError]=useState("");
useEffect(()=>{Promise.all([apiFetch<User>("/api/v1/auth/me"),apiFetch<Organization[]>("/api/v1/organizations")]).then(([me,o])=>{setUser(me);setOrgs(o);}).catch(()=>{window.location.href="/login";});},[]);
async function createOrg(){if(!name.trim())return;setError("");try{const org=await apiFetch<Organization>("/api/v1/organizations",{method:"POST",body:JSON.stringify({name})});setOrgs(items=>[...items,org]);setName("");}catch(err){setError(err instanceof Error?err.message:"Unable to create organization");}}
async function logout(){await apiFetch<void>("/api/v1/auth/logout",{method:"POST"});window.location.href="/";}
if(!user)return <main className="container"><section className="card">Loading dashboard…</section></main>;
return <main className="container"><div className="nav" style={{borderRadius:14,marginBottom:20}}><div className="brand">Training Platform</div><div className="nav-links"><Link href="/dashboard">Dashboard</Link>{user.is_platform_admin&&<Link href="/admin">Admin</Link>}<button className="btn btn-secondary" onClick={logout}>Sign out</button></div></div><section className="card"><div className="eyebrow">Learner dashboard</div><h1>Welcome, {user.full_name}</h1><p className="muted">{user.email} · {user.account_type}</p></section><section className="grid section"><div className="card"><div className="eyebrow">Organizations</div><div className="stat">{orgs.length}</div></div><div className="card"><div className="eyebrow">Courses</div><div className="stat">0</div><div className="muted">Phase 3</div></div><div className="card"><div className="eyebrow">Labs</div><div className="stat">0</div><div className="muted">Later phase</div></div></section><section className="card section"><h2>Organizations</h2>{orgs.length===0?<p className="muted">No organization membership yet.</p>:<div className="list">{orgs.map(o=><div className="list-item" key={o.id}><strong>{o.name}</strong><div className="muted">{o.slug}</div></div>)}</div>}<div className="actions"><input className="org-input" placeholder="New organization name" value={name} onChange={e=>setName(e.target.value)}/><button className="btn btn-primary" onClick={createOrg}>Create organization</button></div>{error&&<div className="error">{error}</div>}</section></main>;
}
