"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../../../lib/api";
import type { Course, CourseCategory, User } from "../../../lib/types";

const initialForm = { title: "", slug: "", short_description: "", description: "", category_id: "", visibility: "public", level: "", estimated_hours: "" };

export default function AdminCoursesPage() {
  const [user, setUser] = useState<User | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [categories, setCategories] = useState<CourseCategory[]>([]);
  const [form, setForm] = useState(initialForm);
  const [categoryForm, setCategoryForm] = useState({ name: "", slug: "", description: "" });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    const me = await apiFetch<User>("/api/v1/auth/me");
    if (!me.is_platform_admin) throw new Error("Platform administrator access required.");
    const result = await Promise.all([apiFetch<Course[]>("/admin/courses"), apiFetch<CourseCategory[]>("/admin/courses/categories")]);
    setUser(me); setCourses(result[0]); setCategories(result[1]);
  }

  useEffect(() => { load().catch(err => setError(err instanceof Error ? err.message : "Unable to load courses")); }, []);

  async function createCourse(event: FormEvent) {
    event.preventDefault(); setError(""); setMessage("");
    try {
      const course = await apiFetch<Course>("/admin/courses", { method: "POST", body: JSON.stringify({
        ...form, category_id: form.category_id ? Number(form.category_id) : null,
        estimated_hours: form.estimated_hours ? Number(form.estimated_hours) : null,
        prerequisite_course_ids: []
      })});
      setCourses(items => [course, ...items]); setForm(initialForm); setMessage("Course created as Draft.");
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to create course"); }
  }

  async function createCategory(event: FormEvent) {
    event.preventDefault(); setError(""); setMessage("");
    try {
      const category = await apiFetch<CourseCategory>("/admin/courses/categories", { method: "POST", body: JSON.stringify(categoryForm) });
      setCategories(items => [...items, category].sort((a, b) => a.name.localeCompare(b.name)));
      setCategoryForm({ name: "", slug: "", description: "" }); setMessage("Category created.");
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to create category"); }
  }

  async function transition(course: Course, action: "submit-review" | "publish" | "retire") {
    setError(""); setMessage("");
    try {
      const updated = await apiFetch<Course>("/admin/courses/" + course.id + "/" + action, { method: "POST" });
      setCourses(items => items.map(item => item.id === updated.id ? updated : item));
      setMessage("Course moved to " + updated.status + ".");
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to change course status"); }
  }

  if (!user && !error) return <main className="container"><section className="card">Loading course administration…</section></main>;

  return <main className="container">
    <div className="nav" style={{ borderRadius: 14, marginBottom: 20 }}><div className="brand">Training Platform · Course Admin</div><div className="nav-links"><Link href="/admin">Admin</Link><Link href="/dashboard">Dashboard</Link></div></div>
    {error && <div className="error">{error}</div>}{message && <div className="success">{message}</div>}
    <section className="card">
      <div className="eyebrow">Course catalogue</div><h1>Manage courses</h1>
      <p className="muted">Create and manage the catalogue before training delivery, enrollment and labs are added.</p>
      <div className="list">{courses.length === 0 ? <p className="muted">No courses yet.</p> : courses.map(course =>
        <div className="list-item" key={course.id}><div className="course-row">
          <div><strong>{course.title}</strong><div className="muted">{course.slug} · {course.visibility} · {course.level || "Level not set"}</div></div>
          <div className="course-actions"><span className={"status status-" + course.status}>{course.status}</span>
            <Link className="btn btn-secondary" href={"/admin/courses/" + course.id}>Edit</Link>
            {course.status === "draft" && <button className="btn btn-secondary" onClick={() => transition(course, "submit-review")}>Submit review</button>}
            {course.status === "review" && <button className="btn btn-primary" onClick={() => transition(course, "publish")}>Publish</button>}
            {course.status === "published" && <button className="btn btn-secondary" onClick={() => transition(course, "retire")}>Retire</button>}
          </div>
        </div></div>
      )}</div>
    </section>
    <div className="admin-two-col section">
      <section className="card"><div className="eyebrow">New course</div><h2>Create course</h2>
        <form onSubmit={createCourse}>
          <div className="field"><label>Title</label><input required value={form.title} onChange={e => setForm({...form,title:e.target.value})}/></div>
          <div className="field"><label>Slug</label><input required value={form.slug} onChange={e => setForm({...form,slug:e.target.value})}/></div>
          <div className="field"><label>Short description</label><input value={form.short_description} onChange={e => setForm({...form,short_description:e.target.value})}/></div>
          <div className="field"><label>Description</label><textarea value={form.description} onChange={e => setForm({...form,description:e.target.value})}/></div>
          <div className="form-grid">
            <div className="field"><label>Category</label><select value={form.category_id} onChange={e => setForm({...form,category_id:e.target.value})}><option value="">No category</option>{categories.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select></div>
            <div className="field"><label>Visibility</label><select value={form.visibility} onChange={e => setForm({...form,visibility:e.target.value})}><option value="public">Public</option><option value="private">Private</option><option value="organization">Organization</option></select></div>
            <div className="field"><label>Level</label><input value={form.level} onChange={e => setForm({...form,level:e.target.value})}/></div>
            <div className="field"><label>Estimated hours</label><input type="number" min="0" value={form.estimated_hours} onChange={e => setForm({...form,estimated_hours:e.target.value})}/></div>
          </div>
          <button className="btn btn-primary" type="submit">Create draft</button>
        </form>
      </section>
      <section className="card"><div className="eyebrow">Catalogue taxonomy</div><h2>Categories</h2>
        <div className="list">{categories.map(c=><div className="list-item" key={c.id}><strong>{c.name}</strong><div className="muted">{c.slug}</div></div>)}{categories.length===0&&<p className="muted">No categories yet.</p>}</div>
        <form onSubmit={createCategory} className="section">
          <div className="field"><label>Name</label><input required value={categoryForm.name} onChange={e=>setCategoryForm({...categoryForm,name:e.target.value})}/></div>
          <div className="field"><label>Slug</label><input required value={categoryForm.slug} onChange={e=>setCategoryForm({...categoryForm,slug:e.target.value})}/></div>
          <div className="field"><label>Description</label><input value={categoryForm.description} onChange={e=>setCategoryForm({...categoryForm,description:e.target.value})}/></div>
          <button className="btn btn-secondary" type="submit">Add category</button>
        </form>
      </section>
    </div>
  </main>;
}
