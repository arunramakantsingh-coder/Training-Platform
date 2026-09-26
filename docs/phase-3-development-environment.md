# Phase 3 — Development Environment

## Purpose

Phase 3 introduces a development-specific Docker Compose configuration so source changes on the EVE-NG VM are reflected without rebuilding the production-style images for every change.

## Development flow

VS Code Remote SSH
→ /opt/training-platform
→ Docker development Compose
→ backend reload + frontend reload
→ NGINX same-origin routing
→ PostgreSQL

## Start

From the repository root:

```bash
docker compose -f deployment/docker/docker-compose.dev.yml config
docker compose -f deployment/docker/docker-compose.dev.yml build
docker compose -f deployment/docker/docker-compose.dev.yml up -d
docker compose -f deployment/docker/docker-compose.dev.yml ps
```

Application endpoint remains:

```text
http://eve-ng:3000
```

Backend direct health endpoint:

```text
http://eve-ng:8000/health
```

## Hot reload

### Backend

The backend source directory is mounted into `/app`. Uvicorn runs with `--reload`, so Python source changes trigger an application reload.

### Frontend

The frontend source directory is mounted into `/app`. Next.js runs in development mode. `node_modules` and `.next` use named Docker volumes so generated dependencies/build state are not written into the Git working tree.

## Production-style Compose

The existing `deployment/docker/docker-compose.yml` remains the milestone/release validation configuration. It continues to build immutable-style backend/frontend images and does not use development source mounts.

## Architecture rules

- Do not hard-code VM, LAN, Tailscale, cloud, or public IP addresses into application source.
- Keep NGINX same-origin routing: `/api/*` to backend and `/*` to frontend.
- Keep Training Website, Lab Controller, and Lab Interface as separate logical services.
- Do not introduce Lab Controller or Lab Interface implementation into Phase 3.
- The EVE-NG VM project repository remains `/opt/training-platform`; `/opt/unetlab` remains the EVE-NG platform area.
