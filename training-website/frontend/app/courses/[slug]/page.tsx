"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { apiFetch } from "../../../lib/api";
import { iihtCourse } from "../../../lib/iiht";

type Lesson = { id: number; title: string; slug: string; content_type: string; content: string | null; order_index: number; estimated_minutes: number | null; is_required: boolean };
type Module = { id: number; title: string; description: string | null; order_index: number; lessons: Lesson[] };
type CourseInfo = { id: number; title: string; slug: string; short_description: string | null; description: string | null; level: string | null; estimated_hours: number | null };
type PublicData = { course: CourseInfo; modules: Module[] };
type LearnerData = PublicData & { enrollment: { id: number; status: string } | null; progress_percent: number };

function portalCourse(): LearnerData {
  return {
    course: {
      id: 0,
      title: iihtCourse.title,
      slug: "arista-velocloud-sd-wan",
      short_description: iihtCourse.subtitle,
      description: "The approved IIHT / Techademy course combines VeloCloud architecture, administration, deployment, routing, policy, security, monitoring, troubleshooting, lifecycle management and migration knowledge transfer.",
      level: iihtCourse.level,
      estimated_hours: 40
    },
    modules: iihtCourse.modules.map((m, index) => ({
      id: m.number,
      title: m.title,
      description: m.summary,
      order_index: index,
      lessons: m.topics.map((topic, topicIndex) => ({
        id: m.number * 100 + topicIndex,
        title: topic,
        slug: topic.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
        content_type: "lab_reference",
        content: null,
        order_index: topicIndex,
        estimated_minutes: null,
        is_required: true
      }))
    })),
    enrollment: null,
    progress_percent: 0
  };
}

export default function CourseDetail() {
  const p = useParams<{ slug: string }>();
  const [data, setData] = useState<LearnerData | null>(null);
  const [apiAvailable, setApiAvailable] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const publicData = await apiFetch<PublicData>("/training/catalogue/" + p.slug);
        setData({ ...publicData, enrollment: null, progress_percent: 0 });
        try {
          setData(await apiFetch<LearnerData>("/training/courses/" + p.slug));
        } catch {}
      } catch {
        setApiAvailable(false);
        setData(portalCourse());
      }
    }
    load();
  }, [p.slug]);

  if (!data) return <main className="container"><section className="card">Loading course…</section></main>;

  return (
    <main className="container">
      <section className="portal-banner">
        <div className="eyebrow" style={{ color: "#9cc9f5" }}>IIHT / Techademy · {data.course.level || "Professional"}</div>
        <h1>{data.course.title}</h1>
        <p className="muted">{data.course.short_description}</p>
        <div className="actions">
          <Link className="btn btn-accent" href="/schedule">View 10-day schedule</Link>
          <Link className="btn btn-light" href="/lab">Open lab portal</Link>
        </div>
      </section>

      {!apiAvailable && <div className="notice">This page is using the portal curriculum definition. Live enrollment and progress will connect when the training API is available.</div>}

      <section className="metric-row section">
        <div className="metric"><span className="muted">Duration</span><strong>40 hours</strong></div>
        <div className="metric"><span className="muted">Theory</span><strong>17 hours</strong></div>
        <div className="metric"><span className="muted">Hands-on</span><strong>23 hours</strong></div>
        <div className="metric"><span className="muted">Cohort</span><strong>25 learners</strong></div>
      </section>

      <section className="section">
        <div className="section-title"><div><div className="eyebrow">Curriculum</div><h2>11 modules</h2></div></div>
        {data.modules.map((m, index) => (
          <article className="card module-card" key={m.id}>
            <div><span className="module-index">{index + 1}</span><strong>{m.title}</strong></div>
            <p className="muted">{m.description}</p>
            <div className="topic-list">{m.lessons.map(l => <span className="topic" key={l.id}>{l.title}</span>)}</div>
          </article>
        ))}
      </section>

      <section className="card section">
        <div className="eyebrow">Assessment & lab</div>
        <h2>Capstone-led completion</h2>
        <p className="muted">The final delivery day includes an end-to-end VeloCloud implementation and assessment. Hands-on activities are aligned to the confirmed lab environment and can be reset or re-provisioned as required.</p>
        <div className="actions">
          <Link className="btn btn-primary" href="/lab">Lab access</Link>
          <Link className="btn btn-secondary" href="/schedule">Daily schedule</Link>
        </div>
      </section>
    </main>
  );
}
