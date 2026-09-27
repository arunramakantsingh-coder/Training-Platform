# Phase 6 — Lab Interface

## Objective

Provide a platform-specific adapter boundary between the platform-neutral Lab Controller and EVE-NG.

## Boundary

```text
Training Website
      |
      v
Lab Controller
      |
      v
Lab Interface
      |
      v
EVE-NG
```

## Rules

- Lab Controller remains platform-neutral.
- EVE-NG-specific API paths and authentication stay inside Lab Interface.
- EVE-NG configuration is environment-specific.
- The adapter must be replaceable by another platform adapter later.
- AIF/AInterceptor remains a separate external AI product. If the Training Platform uses AI, it does so through the AI service boundary defined in the master blueprint.

## Phase 6 increments

1. Generic Lab Interface contract and EVE-NG API client.
2. EVE-NG lab template/clone strategy.
3. Integration with Lab Controller.
4. Real VM lifecycle validation.
5. Contract/error/reliability tests.

## Current increment

The adapter foundation is implemented with a configurable EVE-NG API client and a generic lifecycle contract. The current provisioning operation creates a uniquely named EVE-NG lab as a foundation; topology/template cloning is deliberately the next increment because the public EVE-NG API documentation does not expose a documented clone endpoint. EVE-NG documents lab creation, lab retrieval, node start/stop/wipe, and deletion through its API.

This keeps the first implementation honest and avoids inventing an undocumented API contract.
