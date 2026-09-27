"use client";

import Link from "next/link";
import { iihtCourse } from "../../lib/iiht";

export default function SchedulePage() {
  return (
    <main className="container">
      <section className="portal-banner">
        <div className="eyebrow" style={{ color: "#9cc9f5" }}>IIHT / Techademy</div>
        <h1>40-hour delivery schedule</h1>
        <p className="muted">Ten training days, four hours per day, with theory and guided hands-on lab activity.</p>
      </section>

      <section className="metric-row">
        <div className="metric"><span className="muted">Training</span><strong>40 hours</strong></div>
        <div className="metric"><span className="muted">Theory</span><strong>17 hours</strong></div>
        <div className="metric"><span className="muted">Lab</span><strong>23 hours</strong></div>
        <div className="metric"><span className="muted">Cohort</span><strong>25 learners</strong></div>
      </section>

      <section className="card section">
        <div className="table-wrap">
          <table className="schedule-table">
            <thead><tr><th>Day</th><th>Focus</th><th>Theory</th><th>Lab</th><th>Training topics</th><th>Hands-on</th></tr></thead>
            <tbody>
              {iihtCourse.days.map(day => (
                <tr key={day.day}>
                  <td><strong>Day {day.day}</strong></td>
                  <td><strong>{day.focus}</strong></td>
                  <td>{day.theory}h</td>
                  <td>{day.lab}h</td>
                  <td>{day.topics}</td>
                  <td>{day.handsOn}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card section">
        <div className="eyebrow">Delivery note</div>
        <h2>Lab activities follow the confirmed environment</h2>
        <p className="muted">The proposal allows final exercise sequencing to be adjusted to the confirmed VeloCloud software version and lab platform without changing the agreed 40-hour training scope.</p>
        <div className="actions"><Link className="btn btn-primary" href="/lab">Lab portal</Link><Link className="btn btn-secondary" href="/courses/arista-velocloud-sd-wan">Curriculum</Link></div>
      </section>
    </main>
  );
}
