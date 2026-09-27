"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "../../../../lib/api";
import type {
  Course, CourseCategory, CourseModule, Lesson, LessonLabReference,
  LessonResource, LessonTopic, User
} from "../../../../lib/types";

type CourseForm = {
  title: string;
  slug: string;
  short_description: string;
  description: string;
  category_id: string;
  visibility: string;
  level: string;
  estimated_hours: string;
};

type ModuleForm = { title: string; description: string; order_index: string };
type LessonForm = {
  title: string;
  slug: string;
  content_type: string;
  content: string;
  order_index: string;
  estimated_minutes: string;
  is_required: boolean;
};
type TopicForm = { title: string; content: string; order_index: string };
type ResourceForm = { name: string; resource_type: string; url: string; description: string };
type LabForm = { reference_key: string; display_name: string; metadata_json: string };

const emptyTopic: TopicForm = { title: "", content: "", order_index: "" };
const emptyResource: ResourceForm = { name: "", resource_type: "link", url: "", description: "" };
const emptyLab: LabForm = { reference_key: "", display_name: "", metadata_json: "" };

export default function CourseEditorPage() {
  const params = useParams<{ id: string }>();
  const courseId = Number(params.id);

  const [user, setUser] = useState<User | null>(null);
  const [course, setCourse] = useState<Course | null>(null);
  const [categories, setCategories] = useState<CourseCategory[]>([]);
  const [allCourses, setAllCourses] = useState<Course[]>([]);
  const [selectedPrerequisites, setSelectedPrerequisites] = useState<number[]>([]);
  const [modules, setModules] = useState<CourseModule[]>([]);
  const [lessons, setLessons] = useState<Record<number, Lesson[]>>({});
  const [topics, setTopics] = useState<Record<number, LessonTopic[]>>({});
  const [resources, setResources] = useState<Record<number, LessonResource[]>>({});
  const [labReferences, setLabReferences] = useState<Record<number, LessonLabReference[]>>({});

  const [courseForm, setCourseForm] = useState<CourseForm | null>(null);
  const [moduleForms, setModuleForms] = useState<Record<number, ModuleForm>>({});
  const [lessonForms, setLessonForms] = useState<Record<number, LessonForm>>({});
  const [newModule, setNewModule] = useState({ title: "", description: "" });
  const [newLesson, setNewLesson] = useState<Record<number, LessonForm>>({});
  const [newTopic, setNewTopic] = useState<Record<number, TopicForm>>({});
  const [newResource, setNewResource] = useState<Record<number, ResourceForm>>({});
  const [newLab, setNewLab] = useState<Record<number, LabForm>>({});

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  function setFailure(err: unknown) {
    setError(err instanceof Error ? err.message : "Unable to complete the operation");
  }

  async function load() {
    const me = await apiFetch<User>("/api/v1/auth/me");
    if (!me.is_platform_admin) throw new Error("Platform administrator access required.");

    const [courses, categoryList] = await Promise.all([
      apiFetch<Course[]>("/admin/courses"),
      apiFetch<CourseCategory[]>("/admin/courses/categories"),
    ]);
    const found = courses.find(item => item.id === courseId);
    if (!found) throw new Error("Course not found.");

    const [mods, prerequisiteList] = await Promise.all([
      apiFetch<CourseModule[]>("/admin/courses/" + courseId + "/modules"),
      apiFetch<Course[]>("/admin/courses/" + courseId + "/prerequisites"),
    ]);

    const lessonPairs = await Promise.all(
      mods.map(async mod => [
        mod.id,
        await apiFetch<Lesson[]>("/admin/courses/" + courseId + "/modules/" + mod.id + "/lessons"),
      ] as const),
    );

    const lessonMap = Object.fromEntries(lessonPairs);
    const lessonList = Object.values(lessonMap).flat();

    const detailPairs = await Promise.all(
      mods.flatMap(mod => (lessonMap[mod.id] || []).map(async lesson => {
        const base = "/admin/courses/" + courseId + "/modules/" + mod.id + "/lessons/" + lesson.id;
        const [topicList, resourceList, labList] = await Promise.all([
          apiFetch<LessonTopic[]>(base + "/topics"),
          apiFetch<LessonResource[]>(base + "/resources"),
          apiFetch<LessonLabReference[]>(base + "/lab-references"),
        ]);
        return [lesson.id, topicList, resourceList, labList] as const;
      })),
    );

    const topicMap: Record<number, LessonTopic[]> = {};
    const resourceMap: Record<number, LessonResource[]> = {};
    const labMap: Record<number, LessonLabReference[]> = {};
    for (const [lessonId, topicList, resourceList, labList] of detailPairs) {
      topicMap[lessonId] = topicList;
      resourceMap[lessonId] = resourceList;
      labMap[lessonId] = labList;
    }

    setUser(me);
    setCourse(found);
    setCategories(categoryList);
    setAllCourses(courses);
    setSelectedPrerequisites(prerequisiteList.map(item => item.id));
    setModules(mods);
    setLessons(lessonMap);
    setTopics(topicMap);
    setResources(resourceMap);
    setLabReferences(labMap);
    setCourseForm({
      title: found.title,
      slug: found.slug,
      short_description: found.short_description || "",
      description: found.description || "",
      category_id: found.category_id ? String(found.category_id) : "",
      visibility: found.visibility,
      level: found.level || "",
      estimated_hours: found.estimated_hours != null ? String(found.estimated_hours) : "",
    });

    const moduleState: Record<number, ModuleForm> = {};
    for (const mod of mods) {
      moduleState[mod.id] = {
        title: mod.title,
        description: mod.description || "",
        order_index: String(mod.order_index),
      };
    }
    setModuleForms(moduleState);

    const lessonState: Record<number, LessonForm> = {};
    for (const lesson of lessonList) {
      lessonState[lesson.id] = {
        title: lesson.title,
        slug: lesson.slug,
        content_type: lesson.content_type,
        content: lesson.content || "",
        order_index: String(lesson.order_index),
        estimated_minutes: lesson.estimated_minutes != null ? String(lesson.estimated_minutes) : "",
        is_required: lesson.is_required,
      };
    }
    setLessonForms(lessonState);
  }

  function modulesPath(lesson: Lesson, mods: CourseModule[]) {
    return mods.find(mod => (lessons[mod.id] || []).some(item => item.id === lesson.id))?.id
      || Object.keys(lessons).find(id => (lessons[Number(id)] || []).some(item => item.id === lesson.id))
      || "";
  }

  useEffect(() => {
    load().catch(setFailure);
    // courseId is the only route dependency; load reads the current editor state.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId]);

  async function run(action: () => Promise<void>, successMessage: string) {
    setError("");
    setMessage("");
    setBusy(true);
    try {
      await action();
      setMessage(successMessage);
    } catch (err) {
      setFailure(err);
    } finally {
      setBusy(false);
    }
  }

  async function saveCourse() {
    if (!course || !courseForm || locked(course)) return;
    await run(async () => {
      const updated = await apiFetch<Course>("/admin/courses/" + course.id, {
        method: "PATCH",
        body: JSON.stringify({
          title: courseForm.title,
          slug: courseForm.slug,
          short_description: courseForm.short_description || null,
          description: courseForm.description || null,
          category_id: courseForm.category_id ? Number(courseForm.category_id) : null,
          visibility: courseForm.visibility,
          level: courseForm.level || null,
          estimated_hours: courseForm.estimated_hours ? Number(courseForm.estimated_hours) : null,
          prerequisite_course_ids: selectedPrerequisites,
        }),
      });
      setCourse(updated);
    }, "Course metadata saved.");
  }

  async function saveModule(module: CourseModule) {
    const form = moduleForms[module.id];
    if (!form || !course || locked(course)) return;
    await run(async () => {
      const updated = await apiFetch<CourseModule>(
        "/admin/courses/" + course.id + "/modules/" + module.id,
        {
          method: "PATCH",
          body: JSON.stringify({
            title: form.title,
            description: form.description || null,
            order_index: Number(form.order_index),
          }),
        },
      );
      setModules(items => [...items.map(item => item.id === updated.id ? updated : item)].sort((a, b) => a.order_index - b.order_index));
    }, "Module saved.");
  }

  async function addModule() {
    if (!course || locked(course) || !newModule.title.trim()) return;
    await run(async () => {
      const item = await apiFetch<CourseModule>("/admin/courses/" + course.id + "/modules", {
        method: "POST",
        body: JSON.stringify({
          title: newModule.title,
          description: newModule.description || null,
          order_index: modules.length,
        }),
      });
      setModules(items => [...items, item]);
      setLessons(v => ({ ...v, [item.id]: [] }));
      setNewModule({ title: "", description: "" });
    }, "Module added.");
  }

  async function saveLesson(module: CourseModule, lesson: Lesson) {
    const form = lessonForms[lesson.id];
    if (!form || !course || locked(course)) return;
    await run(async () => {
      const updated = await apiFetch<Lesson>(
        "/admin/courses/" + course.id + "/modules/" + module.id + "/lessons/" + lesson.id,
        {
          method: "PATCH",
          body: JSON.stringify({
            title: form.title,
            slug: form.slug,
            content_type: form.content_type,
            content: form.content || null,
            order_index: Number(form.order_index),
            estimated_minutes: form.estimated_minutes ? Number(form.estimated_minutes) : null,
            is_required: form.is_required,
          }),
        },
      );
      setLessons(v => ({
        ...v,
        [module.id]: [...(v[module.id] || []).map(item => item.id === updated.id ? updated : item)]
          .sort((a, b) => a.order_index - b.order_index),
      }));
      setLessonForms(v => ({
        ...v,
        [updated.id]: {
          title: updated.title,
          slug: updated.slug,
          content_type: updated.content_type,
          content: updated.content || "",
          order_index: String(updated.order_index),
          estimated_minutes: updated.estimated_minutes != null ? String(updated.estimated_minutes) : "",
          is_required: updated.is_required,
        },
      }));
    }, "Lesson saved.");
  }

  async function addLesson(module: CourseModule) {
    const form = newLesson[module.id];
    if (!form || !course || locked(course) || !form.title.trim() || !form.slug.trim()) return;
    await run(async () => {
      const item = await apiFetch<Lesson>(
        "/admin/courses/" + course.id + "/modules/" + module.id + "/lessons",
        {
          method: "POST",
          body: JSON.stringify({
            title: form.title,
            slug: form.slug,
            content_type: form.content_type,
            content: form.content || null,
            order_index: (lessons[module.id] || []).length,
            estimated_minutes: form.estimated_minutes ? Number(form.estimated_minutes) : null,
            is_required: form.is_required,
          }),
        },
      );
      setLessons(v => ({ ...v, [module.id]: [...(v[module.id] || []), item] }));
      setLessonForms(v => ({
        ...v,
        [item.id]: {
          title: item.title, slug: item.slug, content_type: item.content_type,
          content: item.content || "", order_index: String(item.order_index),
          estimated_minutes: item.estimated_minutes != null ? String(item.estimated_minutes) : "",
          is_required: item.is_required,
        },
      }));
      setNewLesson(v => ({ ...v, [module.id]: emptyLesson() }));
      setTopics(v => ({ ...v, [item.id]: [] }));
      setResources(v => ({ ...v, [item.id]: [] }));
      setLabReferences(v => ({ ...v, [item.id]: [] }));
    }, "Lesson added.");
  }

  async function addTopic(module: CourseModule, lesson: Lesson) {
    const form = newTopic[lesson.id] || emptyTopic;
    if (!course || locked(course) || !form.title.trim()) return;
    await run(async () => {
      const item = await apiFetch<LessonTopic>(
        "/admin/courses/" + course.id + "/modules/" + module.id + "/lessons/" + lesson.id + "/topics",
        {
          method: "POST",
          body: JSON.stringify({
            title: form.title,
            content: form.content || null,
            order_index: form.order_index === "" ? (topics[lesson.id] || []).length : Number(form.order_index),
          }),
        },
      );
      setTopics(v => ({ ...v, [lesson.id]: [...(v[lesson.id] || []), item].sort((a, b) => a.order_index - b.order_index) }));
      setNewTopic(v => ({ ...v, [lesson.id]: emptyTopic }));
    }, "Topic added.");
  }

  async function addResource(module: CourseModule, lesson: Lesson) {
    const form = newResource[lesson.id] || emptyResource;
    if (!course || locked(course) || !form.name.trim() || !form.url.trim()) return;
    await run(async () => {
      const item = await apiFetch<LessonResource>(
        "/admin/courses/" + course.id + "/modules/" + module.id + "/lessons/" + lesson.id + "/resources",
        { method: "POST", body: JSON.stringify({ ...form, description: form.description || null }) },
      );
      setResources(v => ({ ...v, [lesson.id]: [...(v[lesson.id] || []), item] }));
      setNewResource(v => ({ ...v, [lesson.id]: emptyResource }));
    }, "Resource added.");
  }

  async function addLabReference(module: CourseModule, lesson: Lesson) {
    const form = newLab[lesson.id] || emptyLab;
    if (!course || locked(course) || !form.reference_key.trim()) return;
    await run(async () => {
      const item = await apiFetch<LessonLabReference>(
        "/admin/courses/" + course.id + "/modules/" + module.id + "/lessons/" + lesson.id + "/lab-references",
        { method: "POST", body: JSON.stringify({ ...form, display_name: form.display_name || null, metadata_json: form.metadata_json || null }) },
      );
      setLabReferences(v => ({ ...v, [lesson.id]: [...(v[lesson.id] || []), item] }));
      setNewLab(v => ({ ...v, [lesson.id]: emptyLab }));
    }, "Lab reference added.");
  }

  if (!user && !error) return <main className="container"><section className="card">Loading course editor…</section></main>;
  if (!course || !courseForm) {
    return <main className="container"><section className="card"><div className="error">{error || "Course not found."}</div><Link className="btn btn-secondary" href="/admin/courses">Back to courses</Link></section></main>;
  }

  const isLocked = locked(course);
  const prerequisiteOptions = allCourses.filter(item => item.id !== course.id);

  return <main className="container">
    <div className="nav" style={{ borderRadius: 14, marginBottom: 20 }}>
      <div className="brand">Training Platform · Course Editor</div>
      <div className="nav-links"><Link href="/admin/courses">Courses</Link><Link href="/admin">Admin</Link></div>
    </div>

    {error && <div className="error">{error}</div>}
    {message && <div className="success">{message}</div>}

    <section className="card">
      <div className="course-row">
        <div>
          <div className="eyebrow">Course {course.id}</div>
          <h1>{course.title}</h1>
          <p className="muted">{course.slug} · {course.visibility} · <span className={"status status-" + course.status}>{course.status}</span></p>
        </div>
        <Link className="btn btn-secondary" href="/admin/courses">Back</Link>
      </div>
      {isLocked && <div className="notice">This course is {course.status}; content editing is disabled by the backend lifecycle rules.</div>}
    </section>

    <section className="card section">
      <div className="eyebrow">1 · Course metadata</div>
      <h2>Course details</h2>
      <div className="form-grid">
        <div className="field"><label>Title</label><input disabled={isLocked} value={courseForm.title} onChange={e => setCourseForm({...courseForm, title:e.target.value})}/></div>
        <div className="field"><label>Slug</label><input disabled={isLocked} value={courseForm.slug} onChange={e => setCourseForm({...courseForm, slug:e.target.value})}/></div>
        <div className="field"><label>Short description</label><input disabled={isLocked} value={courseForm.short_description} onChange={e => setCourseForm({...courseForm, short_description:e.target.value})}/></div>
        <div className="field"><label>Category</label><select disabled={isLocked} value={courseForm.category_id} onChange={e => setCourseForm({...courseForm, category_id:e.target.value})}><option value="">No category</option>{categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></div>
        <div className="field"><label>Visibility</label><select disabled={isLocked} value={courseForm.visibility} onChange={e => setCourseForm({...courseForm, visibility:e.target.value})}><option value="public">Public</option><option value="private">Private</option><option value="organization">Organization</option></select></div>
        <div className="field"><label>Level</label><input disabled={isLocked} value={courseForm.level} onChange={e => setCourseForm({...courseForm, level:e.target.value})}/></div>
        <div className="field"><label>Estimated hours</label><input disabled={isLocked} type="number" min="0" value={courseForm.estimated_hours} onChange={e => setCourseForm({...courseForm, estimated_hours:e.target.value})}/></div>
      </div>
      <div className="field"><label>Description</label><textarea disabled={isLocked} value={courseForm.description} onChange={e => setCourseForm({...courseForm, description:e.target.value})}/></div>

      <div className="section">
        <div className="eyebrow">4 · Prerequisites</div>
        <h3>Required prior courses</h3>
        {prerequisiteOptions.length === 0 ? <p className="muted">No other courses are available.</p> :
          <div className="list">{prerequisiteOptions.map(item =>
            <label className="list-item" key={item.id} style={{display:"flex",alignItems:"center",gap:10}}>
              <input
                type="checkbox"
                disabled={isLocked}
                checked={selectedPrerequisites.includes(item.id)}
                onChange={e => setSelectedPrerequisites(v => e.target.checked ? [...v, item.id] : v.filter(id => id !== item.id))}
              />
              <span><strong>{item.title}</strong><span className="muted"> · {item.status}</span></span>
            </label>
          )}</div>}
      </div>
      {!isLocked && <button disabled={busy} className="btn btn-primary" onClick={saveCourse}>Save course metadata</button>}
    </section>

    {!isLocked && <section className="card section">
      <div className="eyebrow">2 · Learning structure</div>
      <h2>Add module</h2>
      <div className="form-grid">
        <div className="field"><label>Module title</label><input value={newModule.title} onChange={e=>setNewModule({...newModule,title:e.target.value})}/></div>
        <div className="field"><label>Description</label><input value={newModule.description} onChange={e=>setNewModule({...newModule,description:e.target.value})}/></div>
      </div>
      <button disabled={busy} className="btn btn-secondary" onClick={addModule}>Add module</button>
    </section>}

    <section className="section">
      {modules.length === 0 ? <div className="card"><p className="muted">No modules yet.</p></div> : modules.map(module => {
        const moduleForm = moduleForms[module.id] || {title:module.title,description:module.description || "",order_index:String(module.order_index)};
        const moduleLessons = lessons[module.id] || [];
        return <section className="card module-card" key={module.id}>
          <div className="eyebrow">2 · Module {module.order_index + 1}</div>
          {!isLocked ? <div className="form-grid">
            <div className="field"><label>Module title</label><input value={moduleForm.title} onChange={e=>setModuleForms(v=>({...v,[module.id]:{...moduleForm,title:e.target.value}}))}/></div>
            <div className="field"><label>Description</label><input value={moduleForm.description} onChange={e=>setModuleForms(v=>({...v,[module.id]:{...moduleForm,description:e.target.value}}))}/></div>
            <div className="field"><label>Order</label><input type="number" min="0" value={moduleForm.order_index} onChange={e=>setModuleForms(v=>({...v,[module.id]:{...moduleForm,order_index:e.target.value}}))}/></div>
          </div> : <><h2>{module.title}</h2><p className="muted">{module.description || "No description."}</p></>}
          {!isLocked && <button disabled={busy} className="btn btn-secondary" onClick={()=>saveModule(module)}>Save module</button>}

          <div className="section">
            <div className="eyebrow">3 · Lessons</div>
            {moduleLessons.map(lesson => {
              const form = lessonForms[lesson.id] || {
                title:lesson.title,slug:lesson.slug,content_type:lesson.content_type,content:lesson.content || "",
                order_index:String(lesson.order_index),estimated_minutes:lesson.estimated_minutes != null ? String(lesson.estimated_minutes) : "",
                is_required:lesson.is_required,
              };
              const topicList = topics[lesson.id] || [];
              const resourceList = resources[lesson.id] || [];
              const labList = labReferences[lesson.id] || [];
              const topicForm = newTopic[lesson.id] || emptyTopic;
              const resourceForm = newResource[lesson.id] || emptyResource;
              const labForm = newLab[lesson.id] || emptyLab;
              return <div className="list-item" key={lesson.id}>
                {!isLocked ? <div className="form-grid">
                  <div className="field"><label>Lesson title</label><input value={form.title} onChange={e=>setLessonForms(v=>({...v,[lesson.id]:{...form,title:e.target.value}}))}/></div>
                  <div className="field"><label>Slug</label><input value={form.slug} onChange={e=>setLessonForms(v=>({...v,[lesson.id]:{...form,slug:e.target.value}}))}/></div>
                  <div className="field"><label>Content type</label><select value={form.content_type} onChange={e=>setLessonForms(v=>({...v,[lesson.id]:{...form,content_type:e.target.value}}))}><option value="text">Text</option><option value="video">Video</option><option value="document">Document</option><option value="quiz">Quiz</option><option value="lab_reference">Lab reference</option></select></div>
                  <div className="field"><label>Order</label><input type="number" min="0" value={form.order_index} onChange={e=>setLessonForms(v=>({...v,[lesson.id]:{...form,order_index:e.target.value}}))}/></div>
                  <div className="field"><label>Estimated minutes</label><input type="number" min="0" value={form.estimated_minutes} onChange={e=>setLessonForms(v=>({...v,[lesson.id]:{...form,estimated_minutes:e.target.value}}))}/></div>
                  <div className="field"><label>Required</label><select value={form.is_required ? "yes" : "no"} onChange={e=>setLessonForms(v=>({...v,[lesson.id]:{...form,is_required:e.target.value==="yes"}}))}><option value="yes">Yes</option><option value="no">No</option></select></div>
                  <div className="field"><label>Lesson content</label><textarea value={form.content} onChange={e=>setLessonForms(v=>({...v,[lesson.id]:{...form,content:e.target.value}}))}/></div>
                </div> : <><strong>{lesson.order_index + 1}. {lesson.title}</strong><div className="muted">{lesson.slug} · {lesson.content_type}</div>{lesson.content && <p>{lesson.content}</p>}</>}
                {!isLocked && <button disabled={busy} className="btn btn-secondary" onClick={()=>saveLesson(module,lesson)}>Save lesson</button>}

                <div className="section">
                  <div className="eyebrow">5 · Topics</div>
                  {topicList.map(topic => <div className="muted" key={topic.id}>#{topic.order_index + 1} <strong>{topic.title}</strong>{topic.content ? " — " + topic.content : ""}</div>)}
                  {!isLocked && <div className="form-grid">
                    <div className="field"><label>Topic title</label><input value={topicForm.title} onChange={e=>setNewTopic(v=>({...v,[lesson.id]:{...topicForm,title:e.target.value}}))}/></div>
                    <div className="field"><label>Order</label><input type="number" min="0" placeholder={String(topicList.length)} value={topicForm.order_index} onChange={e=>setNewTopic(v=>({...v,[lesson.id]:{...topicForm,order_index:e.target.value}}))}/></div>
                    <div className="field"><label>Topic content</label><textarea value={topicForm.content} onChange={e=>setNewTopic(v=>({...v,[lesson.id]:{...topicForm,content:e.target.value}}))}/></div>
                  </div>}
                  {!isLocked && <button disabled={busy} className="btn btn-secondary" onClick={()=>addTopic(module,lesson)}>Add topic</button>}
                </div>

                <div className="section">
                  <div className="eyebrow">6 · Resources</div>
                  {resourceList.map(resource => <div className="muted" key={resource.id}><strong>{resource.name}</strong> · {resource.resource_type} · {resource.url}</div>)}
                  {!isLocked && <div className="form-grid">
                    <div className="field"><label>Name</label><input value={resourceForm.name} onChange={e=>setNewResource(v=>({...v,[lesson.id]:{...resourceForm,name:e.target.value}}))}/></div>
                    <div className="field"><label>Type</label><select value={resourceForm.resource_type} onChange={e=>setNewResource(v=>({...v,[lesson.id]:{...resourceForm,resource_type:e.target.value}}))}><option value="link">Link</option><option value="document">Document</option><option value="video">Video</option><option value="other">Other</option></select></div>
                    <div className="field"><label>URL</label><input value={resourceForm.url} onChange={e=>setNewResource(v=>({...v,[lesson.id]:{...resourceForm,url:e.target.value}}))}/></div>
                    <div className="field"><label>Description</label><input value={resourceForm.description} onChange={e=>setNewResource(v=>({...v,[lesson.id]:{...resourceForm,description:e.target.value}}))}/></div>
                  </div>}
                  {!isLocked && <button disabled={busy} className="btn btn-secondary" onClick={()=>addResource(module,lesson)}>Add resource</button>}
                </div>

                <div className="section">
                  <div className="eyebrow">7 · Lab references</div>
                  {labList.map(lab => <div className="muted" key={lab.id}><strong>{lab.reference_key}</strong>{lab.display_name ? " · " + lab.display_name : ""}{lab.metadata_json ? " · " + lab.metadata_json : ""}</div>)}
                  {!isLocked && <div className="form-grid">
                    <div className="field"><label>Reference key</label><input value={labForm.reference_key} onChange={e=>setNewLab(v=>({...v,[lesson.id]:{...labForm,reference_key:e.target.value}}))}/></div>
                    <div className="field"><label>Display name</label><input value={labForm.display_name} onChange={e=>setNewLab(v=>({...v,[lesson.id]:{...labForm,display_name:e.target.value}}))}/></div>
                    <div className="field"><label>Metadata JSON</label><textarea placeholder='{"topology":"example"}' value={labForm.metadata_json} onChange={e=>setNewLab(v=>({...v,[lesson.id]:{...labForm,metadata_json:e.target.value}}))}/></div>
                  </div>}
                  {!isLocked && <button disabled={busy} className="btn btn-secondary" onClick={()=>addLabReference(module,lesson)}>Add lab reference</button>}
                </div>
              </div>;
            })}

            {!isLocked && <div className="section">
              <div className="eyebrow">Add lesson</div>
              {(() => {
                const form = newLesson[module.id] || emptyLesson();
                return <div className="form-grid">
                  <div className="field"><label>Title</label><input value={form.title} onChange={e=>setNewLesson(v=>({...v,[module.id]:{...form,title:e.target.value}}))}/></div>
                  <div className="field"><label>Slug</label><input value={form.slug} onChange={e=>setNewLesson(v=>({...v,[module.id]:{...form,slug:e.target.value}}))}/></div>
                  <div className="field"><label>Content type</label><select value={form.content_type} onChange={e=>setNewLesson(v=>({...v,[module.id]:{...form,content_type:e.target.value}}))}><option value="text">Text</option><option value="video">Video</option><option value="document">Document</option><option value="quiz">Quiz</option><option value="lab_reference">Lab reference</option></select></div>
                  <div className="field"><label>Estimated minutes</label><input type="number" min="0" value={form.estimated_minutes} onChange={e=>setNewLesson(v=>({...v,[module.id]:{...form,estimated_minutes:e.target.value}}))}/></div>
                  <div className="field"><label>Lesson content</label><textarea value={form.content} onChange={e=>setNewLesson(v=>({...v,[module.id]:{...form,content:e.target.value}}))}/></div>
                  <div><button disabled={busy} className="btn btn-secondary" onClick={()=>addLesson(module)}>Add lesson</button></div>
                </div>;
              })()}
            </div>}
          </div>
        </section>;
      })}
    </section>
  </main>;
}

function locked(course: Course) {
  return course.status === "published" || course.status === "retired";
}

function emptyLesson(): LessonForm {
  return {
    title: "", slug: "", content_type: "text", content: "",
    order_index: "", estimated_minutes: "", is_required: true,
  };
}
