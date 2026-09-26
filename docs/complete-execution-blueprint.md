# Training Platform — Complete Execution Blueprint

## Product Boundary

The Training Platform is a reusable product for organizations and individual subscribers. It is composed of three logical services:

1. Training Website — account, organization, course, enrollment, subscription, administration, learner experience.
2. Lab Controller — generic lab lifecycle and orchestration.
3. Lab Interface — platform-specific adapter boundary between Lab Controller and a lab execution platform.

EVE-NG is the current execution platform. AInterceptor is a separate product and is outside this repository.

## Phase Roadmap

### Phase 0 — Product Definition & Architecture
Define product scope, service boundaries, lifecycle concepts, data ownership, security boundaries, deployment model, and end-to-end learner journeys.

### Phase 1 — Repository & Platform Foundation
Create the repository structure, service boundaries, Docker development layout, deployment conventions, documentation, and development workflow.

### Phase 2 — Training Website Foundation
Implement application backend, PostgreSQL persistence, migrations, users, organizations, membership roles, authentication, authorization, frontend foundation, learner dashboard, basic platform administration, and automated API tests.

Exit criteria: a user can register, log in, maintain a session, create an organization, view memberships, and platform-admin access is enforced by the API.

### Phase 3 — Course & Training Management
Build course catalogue, course structure, modules, lessons, delivery metadata, training sessions, enrollments, learner progress, and administration.

### Phase 4 — Subscription, Commercial & Access
Implement plans, individual subscriptions, organization contracts/seats, entitlements, payment abstraction, QR/payment gateway boundary, invoices and commercial audit.

### Phase 5 — Lab Controller
Implement platform-neutral lab objects, lab templates, provisioning, allocation, start/stop/reset/delete, status, assignment, usage, reliability, and authorization.

### Phase 6 — Lab Interface
Define the generic adapter interface and implement the initial EVE-NG adapter. Keep Lab Controller independent of EVE-NG-specific details.

### Phase 7 — Student Lab Experience
Connect entitled learners to assigned labs, provide launch/access/reset/status experience, display usage and lifecycle information, and support safe recovery paths.

### Phase 8 — Multi-Tenant Platform
Harden organization isolation, tenant-aware access control, organization administration, tenant configuration, reporting boundaries, and reusable client onboarding.

### Phase 9 — Operations & Administration
Operational dashboards, user/org management, course operations, lab operations, support tooling, audit visibility, capacity and usage reports.

### Phase 10 — Security, Reliability & Production Hardening
Secrets, secure cookies, CSRF strategy, rate limiting, audit logging, validation, backup/restore, error handling, observability, resource limits, and production configuration.

### Phase 11 — Testing, CI/CD & Automation
Unit/integration tests, frontend tests, service contract tests, Docker validation, CI pipelines, deployment automation, smoke tests, and regression coverage.

### Phase 12 — Production & Commercial Readiness
Production deployment, onboarding workflow, documentation, pricing/entitlement operations, tenant support, SLA/monitoring model, and release management.

## End-to-End Target Flow

Learner → Training Website → authentication/authorization → course/subscription entitlement → Lab Controller → Lab Interface → EVE-NG → assigned lab → usage/status → dashboard.

## Development Rule

Each phase is implemented on a Git branch, committed to GitHub, pulled to the EVE-NG VM, tested locally, and only then considered complete. The repository is the source of truth for application code; `/opt/unetlab` remains the EVE-NG platform area and should not be repurposed for application source.
