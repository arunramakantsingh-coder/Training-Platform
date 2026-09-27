# Training Platform — Complete Execution Blueprint

## Product Boundary

The Training Platform is a reusable product for organizations and individual subscribers. It is composed of three logical services:

1. Training Website — account, organization, course, enrollment, subscription, administration, learner experience.
2. Lab Controller — generic lab lifecycle and orchestration.
3. Lab Interface — platform-specific adapter boundary between Lab Controller and a lab execution platform.

EVE-NG is the current lab execution platform. AIF/AInterceptor is a separate product and is consumed, when enabled, as an external AI intelligence service through a standardized AI service boundary.

## External Integration Boundaries

The Training Platform has two distinct external/platform boundaries:

### Lab Execution Boundary

Training Platform → Lab Controller → Lab Interface → EVE-NG

- Lab Controller owns generic lab lifecycle, assignment, authorization, usage, and orchestration.
- Lab Interface owns platform-specific behavior.
- EVE-NG owns the actual virtual lab execution.
- EVE-NG-specific API paths, authentication, lab files, topology operations, node operations, and platform behavior must not leak into Lab Controller.

### AI Intelligence Boundary

Training Platform → AI Service Interface → AIF/AInterceptor → AIP/provider(s) → AI model/service

AIF/AInterceptor is a separate product and is not part of the Training Platform repository or service boundary. The Training Platform may use it as an external AI intelligence provider/router.

The Training Platform must depend on a stable AI-service contract rather than on AInterceptor-specific implementation details. The external AI service boundary should remain capable of supporting multiple provider and protocol paths, including API/HTTP and MCP where appropriate, without coupling the Training Platform to one AIP.

This boundary is intentionally separate from the Lab Controller and Lab Interface. AI intelligence may support learner, trainer, administration, lab assistance, or future agent workflows, but AI routing/provider implementation belongs to AIF/AInterceptor.

## Cross-Phase Architecture Rules

### Deployment and URL Configuration

The application must never depend on a fixed VM, LAN, NAT, Tailscale, cloud, or public IP address.

All environment-specific endpoints must be deployment configuration, not application-source constants. The same build should be deployable to a local VM, another VM with a different IP, a private network, a cloud host, or the public Internet without changing application source.

For development, a deployment may provide an explicit API endpoint through an environment variable such as `NEXT_PUBLIC_API_BASE_URL`.

For Internet/public hosting, the preferred target architecture is same-origin access behind DNS and HTTPS:

```text
Browser
  |
  | https://training.example.com
  |
  +-- /       -> Training Website frontend
  |
  +-- /api/* -> Training Website backend
```

In that model, the browser does not need to know the backend server IP. DNS, reverse proxy/load balancer, and deployment configuration provide the routing.

The frontend API client should therefore support an empty API base URL and use relative `/api/...` paths for same-origin deployments. Public DNS names and TLS certificates belong to deployment/operations configuration, not hard-coded source.

Never commit a changing infrastructure IP as the permanent production value of `NEXT_PUBLIC_API_BASE_URL`. Any current VM-specific value is development-only and must remain overrideable.

### Service and Platform Separation

Training Website, Lab Controller, and Lab Interface remain logically separated services. EVE-NG is the lab execution platform, not a product service. Platform-specific behavior belongs behind Lab Interface.

AIF/AInterceptor is an external AI product, not a Training Platform service. Integration must occur through the AI service boundary and must not introduce AIF/AInterceptor-specific dependencies into Lab Controller or Lab Interface.

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

Optional AI-assisted flows use a separate boundary:

Learner/Trainer/Admin → Training Platform AI Service Interface → AIF/AInterceptor → AIP/provider → AI service/model.

## Development Rule

Each phase is implemented on a Git branch, committed to GitHub, pulled to the EVE-NG VM, tested locally, and only then considered complete. The repository is the source of truth for application code; `/opt/unetlab` remains the EVE-NG platform area and should not be repurposed for application source.
