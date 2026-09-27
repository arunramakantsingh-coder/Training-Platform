# Lab Interface

Lab Interface is the platform-neutral lab integration boundary between Lab Controller and a lab execution platform.

Phase 6 starts with EVE-NG.

## Architecture

Training Website
→ Lab Controller
→ **Lab Interface**
→ **Lab Connector**
→ **Lab EVE API**
→ EVE-NG

### Responsibilities

**Lab Interface**
- Defines the generic lab contract.
- Contains no EVE-specific API paths, credentials, filesystem paths, or wrapper syntax.

**Lab Connector**
- Implements the Lab Interface for a platform.
- Translates generic operations into the Lab EVE API contract.
- Is replaceable for future Lab GNS3 API, Lab CML API, or other platform integrations.

**Lab EVE API**
- Runs inside the EVE-NG VM.
- Owns EVE-specific filesystem, native wrapper, permissions, and any future EVE API integration.
- Provides a stable Training Platform integration contract.
- Does not bypass EVE-NG licensing or platform restrictions.

## Current implementation

- Generic Lab Interface protocol.
- Lab Connector client for Lab EVE API.
- Lab EVE API FastAPI service.
- Safe .unl filesystem cloning foundation.
- Native lifecycle operations deliberately gated until unl_wrapper syntax is verified on the installed EVE-NG version.

## POC direction

The reusable model is:

Master lab template
→ Lab EVE API
→ per-student .unl clone
→ Lab Controller assignment
→ student access

The current development EVE VM is used for control-plane validation. Actual 25-student concurrent runtime requires a nested-virtualization-capable host, sufficient CPU/RAM, appropriate EVE licensing, and vendor image/licensing validation.
