# Phase 2 — Training Website Foundation Validation Report

## Status

Phase 2 implementation is complete and the core learner account flow has been validated on the EVE-NG VM.

Validation date: 2026-09-27 (IST)
Environment: EVE-NG VM
Project path: /opt/training-platform
Git branch: phase-2/training-website-foundation
Validated commit: 7ff63ff

## Completed

### Repository and development environment
- Training Platform monorepo established.
- Phase 2 branch synchronized on the EVE-NG VM.
- VS Code Remote SSH access to the EVE-NG VM established.
- VM repository is clean and tracks the GitHub Phase 2 branch.

### Training Website backend
- FastAPI application and /api/v1 routing.
- Registration, login, logout and current-user session APIs.
- HttpOnly SameSite authentication cookie with JWT.
- Argon2 password hashing.
- PostgreSQL persistence with SQLAlchemy.
- Alembic migration and migration-before-start behavior.
- User, organization and membership models.
- Organization creation and membership lookup.
- Role representation and platform-admin authorization.
- Health and readiness endpoints.
- Backend container healthcheck.

### Training Website frontend
- Next.js application foundation.
- Home page.
- Registration page.
- Login page.
- Learner dashboard.
- Admin console foundation.
- Relative same-origin API calls using /api/v1/....

### Deployment and routing
- Docker Compose deployment.
- NGINX reverse proxy added.
- Public application endpoint: http://eve-ng:3000.
- NGINX routes /api/* to FastAPI backend.
- NGINX routes /* to Next.js frontend.
- Frontend container moved to host port 3001.
- Backend remains on port 8000.
- PostgreSQL remains internal to the Compose network.
- Removed dependency on a fixed VM IP in frontend API configuration.

## VM validation performed

### Repository
- Git branch: phase-2/training-website-foundation.
- Working tree: clean.
- VM synchronized from 4f6193d to 7ff63ff.

### Compose configuration
- docker compose config completed successfully.

### Runtime
- PostgreSQL: healthy.
- Training Website backend: healthy after startup.
- Training Website frontend: running on host port 3001.
- NGINX proxy: running on host port 3000.

### Routing test
- GET /api/v1/auth/register through NGINX returned HTTP 405 with Allow: POST.
- Direct backend GET /api/v1/auth/register returned HTTP 405 with Allow: POST.
- This confirms the registration route exists and NGINX forwards /api/* to the backend.

### Browser smoke test
Validated through http://eve-ng:3000:
1. Training Platform home page loaded.
2. Registration completed.
3. Login completed.
4. Dashboard loaded successfully.

VS Code Remote SSH may also expose the application as http://127.0.0.1:3000 through automatic port forwarding. This is a VS Code tunnel endpoint and is not an application configuration value.

## Important development improvement

A production-style frontend image currently requires a Next.js build before frontend source changes appear in the image. A development-specific Compose configuration should therefore be introduced before substantial Phase 3 UI development.

Target development workflow:
VS Code Remote SSH → source on VM → Docker development containers → hot reload

Production-style Docker builds remain for milestone validation and release testing.

## Remaining Phase 2 validation

The core learner flow is validated. Before formally closing/merging Phase 2, separately validate:
- Platform-admin bootstrap.
- Platform-admin login and admin console access.
- Authorization denial for non-admin users accessing admin APIs.

## Phase 3 — Next Stage

Phase 3 is Course & Training Management.

Planned scope:
1. Course model and database schema.
2. Course creation/update/archive lifecycle.
3. Course catalog.
4. Training/cohort/batch model.
5. Trainer assignment.
6. Course enrollment foundation.
7. Learner course progress foundation.
8. Admin/trainer course management UI and APIs.
9. API authorization rules for course/training operations.
10. Tests and VM validation.

Phase 3 should build on the Phase 2 identity, organization and authorization foundation without introducing lab-controller or lab-interface functionality prematurely.
