# Architecture

## Component flow

```
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

## Deployment model

The first deployment target is one VM. Training Website, Lab Controller, and Lab Interface run as separate containers.

This keeps the components independently deployable without requiring multiple VMs during development.

## Boundaries

### Training Website
Owns users, organizations, individuals, courses, subscriptions, dashboards, and lab access.

### Lab Controller
Owns lab lifecycle, orchestration, assignment, and status.

### Lab Interface
Owns platform-specific communication with the lab execution environment.

### EVE-NG
Runs the actual network lab environments.

## Separate product boundary

AInterceptor is a separate product and is not part of this repository.
