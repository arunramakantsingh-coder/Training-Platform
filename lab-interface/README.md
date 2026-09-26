# Lab Interface

The platform-specific integration layer between Lab Controller and the lab execution platform.

## Responsibilities

- Expose a stable lab-facing interface to Lab Controller
- Translate generic lab operations into platform-specific operations
- Keep platform-specific implementation isolated from the controller
- Provide the initial EVE-NG integration

## Initial adapter

- EVE-NG: `lab-interface/eveng/`
