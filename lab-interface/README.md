# Lab Interface

Lab Interface is the platform-specific adapter boundary between the platform-neutral Lab Controller and a lab execution platform.

Phase 6 starts with EVE-NG.

## Architecture

Training Website
→ Lab Controller
→ Lab Interface
→ EVE-NG

Lab Controller must not contain EVE-NG API paths, authentication details, lab-file conventions, or other EVE-NG-specific behavior.

## Current implementation

- Generic adapter contract.
- EVE-NG API client with session authentication.
- EVE-NG adapter for lab create, read/status, start, stop, reset/wipe, release, and delete operations.
- Configuration through environment variables.
- Unit tests using a fake EVE-NG transport.

## EVE-NG API

The adapter follows the documented EVE-NG API model: authenticated API requests use an EVE session cookie and return JSend-style responses. EVE-NG documents login at `/api/auth/login`, lab management under `/api/labs/... `, and node start/stop/wipe operations under the lab node endpoints.

Provisioning of a reusable topology/template is intentionally separated from this initial adapter foundation. The next increment will define the template/clone mechanism without leaking that concern into Lab Controller.
