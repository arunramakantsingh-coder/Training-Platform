import Link from "next/link";

export default function HomePage() {
  return <main className="container"><div className="hero"><section className="card"><div className="eyebrow">Training Platform</div><h1>Training delivery with hands-on labs.</h1><p className="muted">A reusable platform for organizations and individual learners, designed to connect training content with controlled lab access.</p><div className="actions"><Link className="btn btn-primary" href="/register">Create account</Link><Link className="btn btn-secondary" href="/login">Sign in</Link></div></section><section className="card"><h2>Phase 2 foundation</h2><p className="muted">Accounts, authentication, organizations, roles, PostgreSQL persistence, and the learner dashboard are part of the current application foundation.</p></section></div></main>;
}
