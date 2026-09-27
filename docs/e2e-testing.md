# End-to-End Web Testing

The Training Platform uses Playwright for browser-level regression testing.

## Local EVE-NG VM

The E2E runner targets the same-origin Training Website through the NGINX proxy:

```text
Playwright
    |
    v
http://127.0.0.1:3000
    |
    +--> /       -> frontend
    |
    +--> /api/*  -> backend
```

Run from the repository root:

```bash
docker compose -f deployment/docker/docker-compose.e2e.yml run --rm training-platform-e2e
```

The default test credentials and course slug are development-only values. Override them with environment variables for another environment.

The E2E suite is intentionally separate from backend API tests. API tests validate service behavior; Playwright validates the actual browser journey through the frontend and same-origin routing.

A passing E2E suite does not prove Lab Controller or EVE-NG integration. Those services require separate contract and integration tests in Phases 5 and 6.
