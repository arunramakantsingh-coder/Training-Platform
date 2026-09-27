"use client";

import Link from "next/link";
import { useState } from "react";

const labCards = [
  ["🖥️", "Student Environment", "Your dedicated lab environment will appear here once the Lab Controller is connected."],
  ["▶️", "Start Lab", "Start, stop and reset actions will be connected to the selected lab platform in the hosting phase."],
  ["↻", "Reset / Re-provision", "Recover the student environment between exercises without rebuilding the course."],
  ["🌐", "Appliance Web UI", "Future device access can open the actual vendor appliance interface from the lab environment."]
];

export default function LabPage() {
  const [message, setMessage] = useState("");

  return (
    <main className="container">
      <section className="portal-banner">
        <div className="eyebrow" style={{ color: "#9cc9f5" }}>Hands-on environment</div>
        <h1>Student Lab Portal</h1>
        <p className="muted">The portal UI is ready now. Real lab provisioning will be connected later through the Lab Controller and platform adapter.</p>
        <div className="lab-state" style={{ marginTop: 16 }}><span className="lab-dot"></span>Lab platform connection pending</div>
      </section>

      <section className="metric-row">
        <div className="metric"><span className="muted">Cohort capacity</span><strong>25</strong><span className="muted">concurrent students</span></div>
        <div className="metric"><span className="muted">Access model</span><strong>Isolated</strong><span className="muted">per student</span></div>
        <div className="metric"><span className="muted">Operations</span><strong>Reset</strong><span className="muted">re-provision ready</span></div>
        <div className="metric"><span className="muted">Platform</span><strong>Pending</strong><span className="muted">hosting integration</span></div>
      </section>

      <section className="grid section">
        {labCards.map(([icon, title, detail]) => (
          <div className="lab-card disabled" key={title}>
            <div className="icon">{icon}</div>
            <h3>{title}</h3>
            <p className="muted">{detail}</p>
            <button className="btn btn-secondary" disabled onClick={() => setMessage(title + " will be enabled when lab hosting is connected.")}>Unavailable in demo</button>
          </div>
        ))}
      </section>

      {message && <div className="notice section">{message}</div>}

      <section className="card section">
        <div className="eyebrow">Hosting boundary</div>
        <h2>Training portal first, infrastructure later</h2>
        <p className="muted">This portal does not pretend that the EVE-NG environment is live. Once the hosting platform is finalized, the website can connect to the Lab Controller, which will expose the generic Lab Interface and selected platform adapter.</p>
        <div className="actions">
          <Link className="btn btn-primary" href="/courses/arista-velocloud-sd-wan">Back to course</Link>
          <Link className="btn btn-secondary" href="/schedule">View schedule</Link>
        </div>
      </section>
    </main>
  );
}
