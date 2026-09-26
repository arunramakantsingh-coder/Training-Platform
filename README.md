# Training Platform

A reusable training and hands-on lab platform for organizations and individual subscribers.

## Core Components

- **Training Website** — learner, organization, course, subscription, administration, and lab-access experience.
- **Lab Controller** — lab lifecycle, provisioning, assignment, status, and orchestration.
- **Lab Interface** — stable interface between Lab Controller and the underlying lab platform, with the initial EVE-NG implementation.

## Architecture

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

The three components are independent services and may initially run as separate Docker containers on the same VM.

## Customer Model

One platform can serve multiple organizations and individual subscribers.

Organizations can have multiple users/students. Individuals can subscribe and select courses/labs available to them.

## Repository Layout

```
Training-Platform/
├── training-website/
│   ├── frontend/
│   └── backend/
├── lab-controller/
├── lab-interface/
│   └── eveng/
├── deployment/
└── docs/
```

## Development and Deployment

GitHub is the source of truth for application code. Development work is completed in feature branches and reviewed through pull requests.

The initial test environment is a single EVE-NG VM. The application components are deployed separately from EVE-NG's own files.

Application files should use a dedicated path such as:

```
/opt/training-platform/
```

Do not place application code under:

```
/opt/unetlab/
```

## Scope Boundary

AInterceptor is a separate product and is not part of this repository.
