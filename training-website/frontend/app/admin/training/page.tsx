"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch } from "../../../lib/api";
import type { Course, User } from "../../../lib/types";

type Session = {
  id: number;
  course_id: number;
  name: string;
  slug: string;
  description: string | null;
  trainer_user_id: number | null;
  start_at: string | null;
  end_at: string | null;
  enrollment_limit: number | null;
  status: string;
};

type Enrollment = {
  id: number;
  course_id: number;
  training_session_id: number | null;
  user_id: number;
  organization_id: number | null;
  status: "pending" | "active" | "completed" | "cancelled";
  enrolled_at: string;
  completed_at: string | null;
};

export default function AdminTraining() {
  const [user, setUser] = useState<User | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [courseId, setCourseId] = useState("");
  const [enrollUserId, setEnrollUserId] = useState("");
  const [enrollSessionId, setEnrollSessionId] = useState("");
  const [trainerUserId, setTrainerUserId] = useState("");
  const [form, setForm] = useState({
    name: "",
    slug: "",
    description: "",
    start_at: "",
    end_at: "",
    enrollment_limit: "",
  });
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");

  async function load() {
    const me = await apiFetch<User>("/api/v1/auth/me");
    if (!me.is_platform_admin) throw new Error("Platform administrator access required.");
    const [c, u, s, e] = await Promise.all([
      apiFetch<Course[]>("/admin/courses"),
      apiFetch<User[]>("/admin/users"),
      apiFetch<Session[]>("/admin/training/sessions"),
      apiFetch<Enrollment[]>("/admin/training/enrollments"),
    ]);
    setUser(me);
    setCourses(c);
    setUsers(u);
    setSessions(s);
    setEnrollments(e);
  }

  useEffect(() => {
    load().catch(e => setError(e instanceof Error ? e.message : "Unable to load training administration"));
  }, []);

  async function createSession() {
    setError("");
    setMsg("");
    try {
      const x = await apiFetch<Session>("/admin/training/courses/" + courseId + "/sessions", {
        method: "POST",
        body: JSON.stringify({
          name: form.name,
          slug: form.slug,
          description: form.description || null,
          trainer_user_id: trainerUserId ? Number(trainerUserId) : null,
          start_at: form.start_at ? new Date(form.start_at).toISOString() : null,
          end_at: form.end_at ? new Date(form.end_at).toISOString() : null,
          enrollment_limit: form.enrollment_limit ? Number(form.enrollment_limit) : null,
        }),
      });
      setSessions(v => [...v, x]);
      setMsg("Training session created.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to create session");
    }
  }

  async function updateSession(id: number, status: string) {
    try {
      const x = await apiFetch<Session>("/admin/training/sessions/" + id, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });
      setSessions(v => v.map(s => s.id === id ? x : s));
      setMsg("Session updated.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to update session");
    }
  }

  async function createEnrollment() {
    setError("");
    setMsg("");
    if (!courseId || !enrollUserId) return;
    try {
      const x = await apiFetch<Enrollment>("/admin/training/courses/" + courseId + "/enrollments", {
        method: "POST",
        body: JSON.stringify({
          user_id: Number(enrollUserId),
          training_session_id: enrollSessionId ? Number(enrollSessionId) : null,
        }),
      });
      setEnrollments(v => [x, ...v.filter(item => item.id !== x.id)]);
      setMsg("Enrollment created.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to create enrollment");
    }
  }

  async function updateEnrollment(id: number, status: Enrollment["status"]) {
    try {
      const x = await apiFetch<Enrollment>("/admin/training/enrollments/" + id, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });
      setEnrollments(v => v.map(item => item.id === id ? x : item));
      setMsg("Enrollment updated.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to update enrollment");
    }
  }

  function userName(id: number) {
    const item = users.find(x => x.id === id);
    return item ? item.full_name + " (" + item.email + ")" : "User #" + id;
  }

  function courseName(id: number) {
    return courses.find(x => x.id === id)?.title || "Course #" + id;
  }

  if (!user && !error) {
    return <main className="container"><section className="card">Loading training administration…</section></main>;
  }

  return <main className="container">
    <div className="nav" style={{ borderRadius: 14, marginBottom: 20 }}>
      <div className="brand">Training Platform · Delivery</div>
      <div className="nav-links"><Link href="/admin">Admin</Link><Link href="/admin/courses">Courses</Link></div>
    </div>

    {error && <div className="error">{error}</div>}
    {msg && <div className="success">{msg}</div>}

    <section className="card">
      <div className="eyebrow">Training delivery</div>
      <h1>Cohorts & sessions</h1>
      <div className="form-grid">
        <div className="field"><label>Course</label><select value={courseId} onChange={e => setCourseId(e.target.value)}><option value="">Select course</option>{courses.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}</select></div>
        <div className="field"><label>Name</label><input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} /></div>
        <div className="field"><label>Slug</label><input value={form.slug} onChange={e => setForm({ ...form, slug: e.target.value })} /></div>
        <div className="field"><label>Trainer</label><select value={trainerUserId} onChange={e => setTrainerUserId(e.target.value)}><option value="">Unassigned</option>{users.map(u => <option key={u.id} value={u.id}>{u.full_name} · {u.email}</option>)}</select></div>
        <div className="field"><label>Start</label><input type="datetime-local" value={form.start_at} onChange={e => setForm({ ...form, start_at: e.target.value })} /></div>
        <div className="field"><label>End</label><input type="datetime-local" value={form.end_at} onChange={e => setForm({ ...form, end_at: e.target.value })} /></div>
        <div className="field"><label>Enrollment limit</label><input type="number" min="1" value={form.enrollment_limit} onChange={e => setForm({ ...form, enrollment_limit: e.target.value })} /></div>
        <div className="field"><label>Description</label><textarea value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} /></div>
      </div>
      <button className="btn btn-primary" onClick={createSession} disabled={!courseId || !form.name || !form.slug}>Create session</button>
    </section>

    <section className="card section">
      <h2>Sessions</h2>
      <div className="list">
        {sessions.length === 0 ? <p className="muted">No training sessions yet.</p> : sessions.map(s => (
          <div className="list-item" key={s.id}>
            <div className="course-row">
              <div><strong>{s.name}</strong><div className="muted">{courseName(s.course_id)} · {s.status}{s.trainer_user_id ? " · Trainer: " + userName(s.trainer_user_id) : ""}{s.start_at ? " · " + new Date(s.start_at).toLocaleString() : ""}</div></div>
              <div className="actions">
                {s.status === "draft" && <button className="btn btn-secondary" onClick={() => updateSession(s.id, "open")}>Open enrollment</button>}
                {s.status === "open" && <button className="btn btn-secondary" onClick={() => updateSession(s.id, "closed")}>Close enrollment</button>}
                {s.status === "closed" && <button className="btn btn-secondary" onClick={() => updateSession(s.id, "open")}>Reopen</button>}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>

    <section className="card section">
      <div className="eyebrow">Enrollment administration</div>
      <h2>Enroll a learner</h2>
      <div className="form-grid">
        <div className="field"><label>Course</label><select value={courseId} onChange={e => { setCourseId(e.target.value); setEnrollSessionId(""); }}><option value="">Select course</option>{courses.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}</select></div>
        <div className="field"><label>Learner</label><select value={enrollUserId} onChange={e => setEnrollUserId(e.target.value)}><option value="">Select learner</option>{users.filter(u => !u.is_platform_admin).map(u => <option key={u.id} value={u.id}>{u.full_name} · {u.email}</option>)}</select></div>
        <div className="field"><label>Session</label><select value={enrollSessionId} onChange={e => setEnrollSessionId(e.target.value)}><option value="">No session</option>{sessions.filter(s => String(s.course_id) === courseId && s.status === "open").map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select></div>
      </div>
      <button className="btn btn-primary" onClick={createEnrollment} disabled={!courseId || !enrollUserId}>Enroll learner</button>
    </section>

    <section className="card section">
      <h2>Enrollments</h2>
      <div className="list">
        {enrollments.length === 0 ? <p className="muted">No enrollments yet.</p> : enrollments.map(e => (
          <div className="list-item" key={e.id}>
            <div className="course-row">
              <div><strong>{userName(e.user_id)}</strong><div className="muted">{courseName(e.course_id)} · Enrollment #{e.id} · {new Date(e.enrolled_at).toLocaleString()}</div></div>
              <select value={e.status} onChange={event => updateEnrollment(e.id, event.target.value as Enrollment["status"])}>
                <option value="pending">Pending</option><option value="active">Active</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>
        ))}
      </div>
    </section>
  </main>;
}
