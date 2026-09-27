import Link from "next/link";
import { iihtCourse } from "../lib/iiht";

export default function HomePage() {
  return (
    <main className="container">
      <section className="hero">
        <div className="card hero-main dark-card">
          <div className="eyebrow" style={{ color: "#9cc9f5" }}>IIHT / Techademy · Professional Training</div>
          <h1>{iihtCourse.title}</h1>
          <p className="muted">{iihtCourse.subtitle}. Structured theory, guided exercises and a dedicated student lab experience.</p>
          <div className="actions">
            <Link className="btn btn-accent" href="/courses/arista-velocloud-sd-wan">Explore course</Link>
            <Link className="btn btn-light" href="/login">Student login</Link>
          </div>
          <div className="metric-row" style={{ marginTop: 28 }}>
            <div className="metric"><span className="muted">Cohort</span><strong>{iihtCourse.participants}</strong><span className="muted">participants</span></div>
            <div className="metric"><span className="muted">Duration</span><strong>{iihtCourse.duration}</strong><span className="muted">instructor-led</span></div>
            <div className="metric"><span className="muted">Lab</span><strong>{iihtCourse.labHours}h</strong><span className="muted">hands-on</span></div>
            <div className="metric"><span className="muted">Format</span><strong>Online</strong><span className="muted">10-day delivery</span></div>
          </div>
        </div>

        <div className="card hero-side">
          <div>
            <div className="eyebrow">Training portal</div>
            <h2>One place for the cohort</h2>
            <p className="muted">Courseware, delivery schedule, student progress and lab access are presented through one learner-facing portal.</p>
          </div>
          <div>
            <div className="callout">
              <strong>Lab hosting is a separate infrastructure component.</strong>
              <div className="muted" style={{ marginTop: 5 }}>The portal is ready for a future Lab Controller connection.</div>
            </div>
            <Link className="btn btn-secondary" href="/lab" style={{ marginTop: 14 }}>View lab portal</Link>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-title"><div><div className="eyebrow">Curriculum</div><h2>11-module VeloCloud program</h2></div><Link className="btn btn-secondary" href="/courses/arista-velocloud-sd-wan">View all modules</Link></div>
        <div className="grid">
          {iihtCourse.modules.slice(0, 6).map(module => (
            <div className="card" key={module.number}>
              <div><span className="module-index">{module.number}</span><strong>{module.title}</strong></div>
              <p className="muted">{module.summary}</p>
              <div className="topic-list">{module.topics.slice(0, 2).map(topic => <span className="topic" key={topic}>{topic}</span>)}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section-title"><div><div className="eyebrow">Delivery model</div><h2>40 hours, built around hands-on practice</h2></div></div>
        <div className="metric-row">
          <div className="metric"><span className="muted">Theory</span><strong>{iihtCourse.theoryHours} hours</strong></div>
          <div className="metric"><span className="muted">Guided lab</span><strong>{iihtCourse.labHours} hours</strong></div>
          <div className="metric"><span className="muted">Daily format</span><strong>4 hours</strong></div>
          <div className="metric"><span className="muted">Capstone</span><strong>Day 10</strong></div>
        </div>
      </section>

      <footer className="footer">
        <div className="footer-row">
          <span>Lab Training Platform · IIHT VeloCloud cohort portal</span>
          <span>Lab infrastructure is provisioned separately from training delivery.</span>
        </div>
      </footer>
    </main>
  );
}
