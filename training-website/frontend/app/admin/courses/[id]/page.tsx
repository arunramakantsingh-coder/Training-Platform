"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "../../../../lib/api";
import type { Course, CourseModule, Lesson, User } from "../../../../lib/types";

type Draft = { title: string; slug: string; content_type: string; content: string; estimated_minutes: string };

export default function CourseEditorPage() {
  const params = useParams<{ id: string }>();
  const courseId = Number(params.id);
  const [user, setUser] = useState<User | null>(null), [course, setCourse] = useState<Course | null>(null);
  const [modules, setModules] = useState<CourseModule[]>([]), [lessons, setLessons] = useState<Record<number, Lesson[]>>({});
  const [moduleTitle, setModuleTitle] = useState(""), [moduleDescription, setModuleDescription] = useState("");
  const [drafts, setDrafts] = useState<Record<number, Draft>>({});
  const [error, setError] = useState(""), [message, setMessage] = useState("");

  async function load() {
    const me = await apiFetch<User>("/api/v1/auth/me");
    if (!me.is_platform_admin) throw new Error("Platform administrator access required.");
    const courses = await apiFetch<Course[]>("/admin/courses");
    const found = courses.find(item => item.id === courseId);
    if (!found) throw new Error("Course not found.");
    const mods = await apiFetch<CourseModule[]>("/admin/courses/" + courseId + "/modules");
    const pairs = await Promise.all(mods.map(async mod => [mod.id, await apiFetch<Lesson[]>("/admin/courses/" + courseId + "/modules/" + mod.id + "/lessons")] as const));
    setUser(me); setCourse(found); setModules(mods); setLessons(Object.fromEntries(pairs));
  }

  useEffect(() => { load().catch(err => setError(err instanceof Error ? err.message : "Unable to load course")); }, [courseId]);

  async function addModule() {
    if (!moduleTitle.trim() || !course || course.status === "published" || course.status === "retired") return;
    setError(""); setMessage("");
    try {
      const item = await apiFetch<CourseModule>("/admin/courses/" + courseId + "/modules", { method:"POST", body:JSON.stringify({title:moduleTitle,description:moduleDescription||null,order_index:modules.length}) });
      setModules(items=>[...items,item]); setLessons(v=>({...v,[item.id]:[]})); setModuleTitle(""); setModuleDescription(""); setMessage("Module added.");
    } catch(err) { setError(err instanceof Error ? err.message : "Unable to add module"); }
  }

  async function addLesson(module: CourseModule) {
    const draft = drafts[module.id]; if (!draft || !draft.title.trim() || !draft.slug.trim() || !course || course.status==="published" || course.status==="retired") return;
    setError(""); setMessage("");
    try {
      const item = await apiFetch<Lesson>("/admin/courses/" + courseId + "/modules/" + module.id + "/lessons", {method:"POST",body:JSON.stringify({
        title:draft.title,slug:draft.slug,content_type:draft.content_type,content:null,
        order_index:(lessons[module.id]||[]).length,estimated_minutes:draft.estimated_minutes ? Number(draft.estimated_minutes) : null,is_required:true
      })});
      setLessons(v=>({...v,[module.id]:[...(v[module.id]||[]),item]}));
      setDrafts(v=>({...v,[module.id]:{title:"",slug:"",content_type:"text",content:"",estimated_minutes:""}})); setMessage("Lesson added.");
    } catch(err) { setError(err instanceof Error ? err.message : "Unable to add lesson"); }
  }

  if(!user && !error) return <main className="container"><section className="card">Loading course editor…</section></main>;
  if(!course) return <main className="container"><section className="card"><div className="error">{error || "Course not found."}</div><Link className="btn btn-secondary" href="/admin/courses">Back to courses</Link></section></main>;
  const locked = course.status==="published" || course.status==="retired";

  return <main className="container">
    <div className="nav" style={{borderRadius:14,marginBottom:20}}><div className="brand">Training Platform · Course Editor</div><div className="nav-links"><Link href="/admin/courses">Courses</Link><Link href="/admin">Admin</Link></div></div>
    {error&&<div className="error">{error}</div>}{message&&<div className="success">{message}</div>}
    <section className="card"><div className="eyebrow">Course {course.id}</div><h1>{course.title}</h1><p className="muted">{course.slug} · {course.visibility} · <span className={"status status-"+course.status}>{course.status}</span></p>
      {locked&&<div className="notice">This course is {course.status}; content editing is disabled by the backend lifecycle rules.</div>}
    </section>
    {!locked&&<section className="card section"><div className="eyebrow">Learning structure</div><h2>Add module</h2>
      <div className="form-grid"><div className="field"><label>Module title</label><input value={moduleTitle} onChange={e=>setModuleTitle(e.target.value)}/></div><div className="field"><label>Description</label><input value={moduleDescription} onChange={e=>setModuleDescription(e.target.value)}/></div></div>
      <button className="btn btn-primary" onClick={addModule}>Add module</button>
    </section>}
    <section className="section">{modules.length===0?<div className="card"><p className="muted">No modules yet.</p></div>:modules.map(module=>{
      const draft=drafts[module.id]||{title:"",slug:"",content_type:"text",content:"",estimated_minutes:""};
      return <section className="card module-card" key={module.id}><div className="course-row"><div><div className="eyebrow">Module {module.order_index+1}</div><h2>{module.title}</h2><p className="muted">{module.description||"No description."}</p></div><span className="muted">{(lessons[module.id]||[]).length} lessons</span></div>
        <div className="list section">{(lessons[module.id]||[]).map(lesson=><div className="list-item" key={lesson.id}><strong>{lesson.order_index+1}. {lesson.title}</strong><div className="muted">{lesson.slug} · {lesson.content_type}{lesson.estimated_minutes!=null ? " · "+lesson.estimated_minutes+" min" : ""}</div>{lesson.content&&<p>{lesson.content}</p>}</div>)}</div>
        {!locked&&<div className="section"><div className="eyebrow">Add lesson</div><div className="form-grid">
          <div className="field"><label>Title</label><input value={draft.title} onChange={e=>setDrafts(v=>({...v,[module.id]:{...draft,title:e.target.value}}))}/></div>
          <div className="field"><label>Slug</label><input value={draft.slug} onChange={e=>setDrafts(v=>({...v,[module.id]:{...draft,slug:e.target.value}}))}/></div>
          <div className="field"><label>Content type</label><select value={draft.content_type} onChange={e=>setDrafts(v=>({...v,[module.id]:{...draft,content_type:e.target.value}}))}><option value="text">Text</option><option value="video">Video</option><option value="document">Document</option><option value="quiz">Quiz</option><option value="lab_reference">Lab reference</option></select></div>
          <div className="field"><label>Estimated minutes</label><input type="number" min="0" value={draft.estimated_minutes} onChange={e=>setDrafts(v=>({...v,[module.id]:{...draft,estimated_minutes:e.target.value}}))}/></div><div className="field"><label>Lesson content</label><textarea value={draft.content} onChange={e=>setDrafts(v=>({...v,[module.id]:{...draft,content:e.target.value}}))}/></div>
        </div><button className="btn btn-secondary" onClick={()=>addLesson(module)}>Add lesson</button></div>}
      </section>;
    })}</section>
  </main>;
}
