"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";
import { iihtCourse } from "../../lib/iiht";

type Course = { id: number; title: string; slug: string; short_description: string | null; level: string | null; estimated_hours: number | null };

export default function Courses() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<Course[]>("/training/courses")
      .then(setCourses)
      .catch(() => {
        setCourses([{
          id: 0,
          title: iihtCourse.title,
          slug: "arista-velocloud-sd-wan",
          short_description: "40-hour instructor-led Arista VeloCloud SD-WAN program with 23 hours of structured hands-on lab activity.",
          level: iihtCourse.level,
          estimated_hours: 40
        }]);
      });
  }, []);

  return (
    <main className="container">
      <section className="portal-banner">
        <div className="eyebrow" style={{ color: "#9cc9f5" }}>IIHT / Techademy</div>
        <h1>Training catalogue</h1>
        <p className="muted">The current cohort portal contains the approved Arista VeloCloud SD-WAN training program.</p>
      </section>

      <section className="card">
        <div className="section-title">
          <div><div className="eyebrow">Available program</div><h2>Course catalogue</h2></div>
          <Link className="btn btn-secondary" href="/schedule">Delivery schedule</Link>
        </div>
        {error && <div className="notice">Showing the portal course catalogue while the training API is unavailable.</div>}
        <div className="list">
          {courses.map(c => (
            <div className="list-item" key={c.id || c.slug}>
              <div className="course-row">
                <div>
                  <h2>{c.title}</h2>
                  <p className="muted">{c.short_description || "Hands-on professional training."}</p>
                  <div className="muted">{c.level || "Professional"} · {c.estimated_hours ?? 40} hours · 25-participant cohort</div>
                </div>
                <Link className="btn btn-primary" href={"/courses/" + c.slug}>View course</Link>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
