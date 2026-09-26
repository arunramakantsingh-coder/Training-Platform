# Phase 2 Implementation

## Delivered

- FastAPI application with versioned `/api/v1` routing.
- PostgreSQL/SQLAlchemy persistence foundation.
- Alembic initial migration for users, organizations and memberships.
- Individual and organization account types.
- Password hashing using `pwdlib` Argon2.
- JWT session token stored in an HttpOnly, SameSite=Lax cookie.
- Registration, login, logout and current-user endpoints.
- Organization creation and membership listing.
- Organization admin / student / trainer role representation.
- Platform-admin authorization and read-only admin endpoints.
- Bootstrap script for creating/promoting a platform administrator.
- Next.js pages for home, registration, login, dashboard and platform admin.
- Phase-isolated Docker Compose startup for the services implemented in Phase 2.
- SQLite-backed API tests covering health, authentication, duplicate registration, bad login, organization creation and authorization.

## Local Validation on EVE-NG VM

Phase 2 must be independently buildable and runnable. Lab Controller and Lab Interface are future phases and are not required for this phase.

From the repository root:

```bash
docker compose -f deployment/docker/docker-compose.yml config
docker compose -f deployment/docker/docker-compose.yml build
docker compose -f deployment/docker/docker-compose.yml up -d
docker compose -f deployment/docker/docker-compose.yml ps
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
```

Create a test platform admin after the database is ready:

```bash
docker compose -f deployment/docker/docker-compose.yml exec training-website \
  python scripts/create_platform_admin.py \
  --email admin@example.com \
  --name "Platform Admin" \
  --password "ChangeThisPassword123!"
```

Frontend: `http://<EVE-NG-VM-IP>:3000` when the port is reachable.
API: `http://<EVE-NG-VM-IP>:8000`.

For remote browser access, set `NEXT_PUBLIC_API_BASE_URL` to the reachable VM API URL and `CORS_ORIGINS` to the frontend origin.

## Phase 2 Security Boundary

This is a development foundation, not the final production security posture. Phase 10 will add production secret enforcement, CSRF controls beyond SameSite protection, rate limits, audit logging, stronger session policy, and operational hardening.

## Next Phase

Phase 3 starts only after the local Phase 2 test flow passes on the EVE-NG VM.
