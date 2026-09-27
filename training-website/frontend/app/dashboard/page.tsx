"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";
import type { Organization, User } from "../../lib/types";
import { iihtCourse } from "../../lib/iiht";

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([apiFetch<User>("/api/v1/auth/me"), apiFetch<Organization[]>("/organizations")])
      .then(([me, organizations]) => { setUser(me); setOrgs(organizations); })
      .catch(() => { window.location.href = "/login"; });
  }, []);

  async function createOrg() {
    if (!name.trim()) return;
    setError("");
    try {
      const org = await apiFetch<Organization>("/organizations", { method: "POST", body: JSON.stringify({ name }) });
      setOrgs(items => [...items, org]);
      setName("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create organization");
    }
  }

  async function logout() {
    await apiFetch<void>("/api/v1/auth/logout", { method: "POST" });
    window.location.href = "/";
  }

  if (!user) return <main className="container"><section className="card">Loading student portal…</section></main>;

  return (
    <main className="container">
      <section className="portal-banner">
        <div className="eyebrow" style={{ color: "#9cc9f5" }}>Student dashboard · IIHT / Techademy</div>
        <h1>Welcome, {user.full_name}</h1>
        <p className="muted">{user.email} · {user.account_type}</p>
        <div className="actions">
          <Link className="btn btn-accent" href="/lab">Open Lab Portal</Link>
          <Link className="btn btn-light" href="/schedule">Training Schedule</Link>
          <button className="btn btn-secondary" onClick={logout}>Sign out</button>
        </div>
      </section>

      <section className="metric-row section">
        <div className="metric"><span className="muted">Current course</span><strong>VeloCloud</strong><span className="muted">40-hour program</span></div>
        <div className="metric"><span className="muted">Progress</span><strong>0%</strong><span className="muted">ready for enrollment sync</span></div>
        <div className="metric"><span className="muted">Lab</span><strong>Pending</strong><span className="muted">hosting connection</span></div>
        <div className="metric"><span className="muted">Cohort</span><strong>25</strong><span className="muted">participant capacity</span></div>
      </section>

      <section className="card section">
        <div className="section-title">
          <div><div className="eyebrow">My training</div><h2>{iihtCourse.title}</h2></div>
          <Link className="btn btn-primary" href="/courses/arista-velocloud-sd-wan">Open course</Link>
        </div>
        <p className="muted">{iihtCourse.subtitle}. {iihtCourse.theoryHours} hours theory + {iihtCourse.labHours} hours guided hands-on activity.</p>
        <div className="progress"><span style={{ width: "0%" }} /></div>
        <div className="topic-list">{iihtCourse.modules.slice(0, 5).map(m => <span className="topic" key={m.number}>Module {m.number}</span>)}</div>
      </section>

      <section className="grid section">
        <div className="card"><div className="eyebrow">Next session</div><h3>Day 1 · VeloCloud Architecture & Fundamentals</h3><p className="muted">Lab orientation, environment access and basic connectivity validation.</p><Link className="btn btn-secondary" href="/schedule">View schedule</Link></div>
        <div className="card"><div className="eyebrow">Lab access</div><h3>Student environment</h3><p className="muted">Your future dedicated environment will be controlled through the Lab Controller.</p><Link className="btn btn-secondary" href="/lab">Lab portal</Link></div>
        <div className="card"><div className="eyebrow">Resources</div><h3>Course materials</h3><p className="muted">Courseware, exercises and supporting material can be connected to the learner account.</p><Link className="btn btn-secondary" href="/courses/arista-velocloud-sd-wan">Course content</Link></div>
      </section>

      <section className="card section">
        <div className="eyebrow">Organizations</div>
        <h2>Account organizations</h2>
        {orgs.length === 0 ? <p className="muted">No organization membership yet.</p> : <div className="list">{orgs.map(o => <div className="list-item" key={o.id}><strong>{o.name}</strong><div className="muted">{o.slug}</div></div>)}</div>}
        <div className="actions"><input className="org-input" placeholder="New organization name" value={name} onChange={e => setName(e.target.value)} /><button className="btn btn-primary" onClick={createOrg}>Create organization</button></div>
        {error && <div className="error">{error}</div>}
      </section>
    </main>
  );
}
