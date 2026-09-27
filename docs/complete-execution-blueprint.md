# Training Platform — Complete Execution Blueprint

## Product Boundary

The Training Platform is a reusable product for organizations and individual subscribers. It is composed of four logical services/boundaries:

1. Training Website — account, organization, course, enrollment, subscription, administration, learner experience.
2. Lab Controller — generic lab lifecycle and orchestration.
3. Lab Interface — platform-neutral contract between Lab Controller and a lab integration.
4. Lab Connector — platform-specific integration client implementing Lab Interface.

**Lab EVE API** is a dedicated EVE-specific integration service. It runs with the EVE-NG environment and is not the generic Lab Interface. Future platform services may include Lab GNS3 API, Lab CML API, or equivalent control services.

EVE-NG is the current lab execution platform. AIF/AInterceptor is a separate product and is consumed, when enabled, as an external AI intelligence service through a standardized AI service boundary.

## External Integration Boundaries

### Lab Execution Boundary

Training Platform → Lab Controller → Lab Interface → Lab Connector → Lab EVE API → EVE-NG

- Lab Controller owns generic lab lifecycle, assignment, authorization, usage, and orchestration.
- Lab Interface defines the generic lab contract.
- Lab Connector implements the contract for a selected platform.
- Lab EVE API owns EVE-specific API paths, authentication, lab-file conventions, native wrapper use, local filesystem operations, permissions, topology operations, node operations, and platform behavior.
- EVE-NG owns the actual virtual lab execution.
- EVE-NG licensing and technical restrictions remain applicable.

### AI Intelligence Boundary

Training Platform → AI Service Interface → AIF/AInterceptor → AIP/provider(s) → AI model/service

AIF/AInterceptor is a separate product and is not part of the Training Platform repository or service boundary.

## Cross-Phase Architecture Rules

### Service and Platform Separation

Training Website, Lab Controller, Lab Interface, and Lab Connector remain logically separated application boundaries. Lab EVE API is the EVE-specific control service. EVE-NG is the execution platform.

The generic Lab Interface must never contain EVE-specific API paths, credentials, filesystem paths, or wrapper commands.

The Lab Connector must communicate with the EVE environment through the Lab EVE API contract rather than embedding EVE implementation details.

AIF/AInterceptor remains external and must not introduce AIF-specific dependencies into the lab services.

### Deployment and URL Configuration

The application must never depend on a fixed VM, LAN, NAT, Tailscale, cloud, or public IP address. All environment-specific endpoints are deployment configuration.

## Phase Roadmap

### Phase 0 — Product Definition & Architecture
Define product scope, service boundaries, lifecycle concepts, data ownership, security boundaries, deployment model, and end-to-end learner journeys.

### Phase 1 — Repository & Platform Foundation
Create the repository structure, service boundaries, Docker development layout, deployment conventions, documentation, and development workflow.

### Phase 2 — Training Website Foundation
Implement application backend, PostgreSQL persistence, migrations, users, organizations, membership roles, authentication, authorization, frontend foundation, learner dashboard, basic platform administration, and automated API tests.

### Phase 3 — Course & Training Management
Build course catalogue, course structure, modules, lessons, delivery metadata, training sessions, enrollments, learner progress, and administration.

### Phase 4 — Subscription, Commercial & Access
Implement plans, individual subscriptions, organization contracts/seats, entitlements, payment abstraction, QR/payment gateway boundary, invoices and commercial audit.

### Phase 5 — Lab Controller
Implement platform-neutral lab objects, lab templates, provisioning, allocation, start/stop/reset/delete, status, assignment, usage, reliability, and authorization.

### Phase 6 — Lab Interface, Lab Connector & Lab EVE API
Define and preserve the generic Lab Interface contract. Implement the EVE Lab Connector and the Lab EVE API service. Move all EVE-specific control behind the Lab EVE API. Implement reusable lab template/clone provisioning and lifecycle integration. Validate the native EVE mechanisms against the installed EVE-NG version before enabling destructive/runtime operations.

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

Learner → Training Website → authentication/authorization → course/subscription entitlement → Lab Controller → Lab Interface → Lab Connector → Lab EVE API → EVE-NG → assigned lab → usage/status → dashboard.

Future platform example:

Lab Interface → Lab Connector → Lab GNS3 API → GNS3

Optional AI-assisted flows use a separate boundary:

Learner/Trainer/Admin → Training Platform AI Service Interface → AIF/AInterceptor → AIP/provider → AI service/model.

## Development Rule

Each phase is implemented on a Git branch, committed to GitHub, pulled to the EVE-NG VM, tested locally, and only then considered complete. The repository is the source of truth for application code; /opt/unetlab remains the EVE-NG platform area and should not be repurposed for application source.
