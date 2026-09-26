# Training Platform

A multi-tenant training platform for organizations and individual subscribers, with course delivery and hands-on lab access.

## Components

- training-website — learner, course, subscription, administration, and lab access experience.
- lab-controller — lab lifecycle and student lab orchestration.
- lab-interface — platform-specific interface between Lab Controller and the lab system.

## Development Layout

```
Training-Platform/
├── training-website/
├── lab-controller/
├── lab-interface/
├── deployment/
└── docs/
```

The three components remain logically independent and can run as separate containers while initially sharing the same EVE-NG VM.

## Development Workflow

1. Plan work in the GitHub Project and Issues.
2. Implement changes in this repository.
3. Commit changes to GitHub.
4. Pull the required revision into the EVE-NG VM.
5. Test there.
6. Record fixes and follow-up work in GitHub.

## Scope Boundary

EVE-NG is the lab execution platform for the current development environment. AInterceptor is a separate product and is not part of this repository.
