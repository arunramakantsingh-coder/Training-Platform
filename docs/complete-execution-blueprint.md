# Training Platform — Complete Execution Blueprint

> Master execution plan for the reusable Training Platform serving organizations and individual subscribers.

## 1. Product Definition

The Training Platform is one reusable product. Multiple organizations (for example, training institutes or enterprise customers) and individual subscribers use the same platform.

### Customer types

- Organization/customer: an organization with multiple users/students and organization-level administration.
- Individual subscriber: a standalone account that can subscribe to courses/labs for personal use.

### Core components

1. Training Website
2. Lab Controller
3. Lab Interface

Initial lab execution platform: EVE-NG.

AInterceptor is a separate product and is not part of this repository.

## 2. Target Architecture

```
Users
  |
  v
Training Website
  |
  | lab operations
  v
Lab Controller
  |
  | generic lab operations
  v
Lab Interface
  |
  | platform-specific operations
  v
EVE-NG
```

Initial deployment may place the three application components in separate Docker containers on the same VM as EVE-NG. Application files use a dedicated path such as `/opt/training-platform/`; EVE-NG files under `/opt/unetlab/` remain outside the application boundary.

## 3. Phase 0 — Product Definition & Architecture

### Objective
Freeze the product boundaries and core operating model before feature implementation.

### Build
- Product scope and terminology
- Organization/customer model
- Individual subscriber model
- User/role concepts
- Course, lab, subscription and entitlement concepts
- Three-component boundaries
- Initial single-VM deployment model
- GitHub repository/project workflow
- Documentation structure

### Deliverables
- Product architecture
- Domain glossary
- Component responsibility definitions
- Development workflow
- Initial repository/project structure

### Exit criteria
The team can explain what each component owns and how a user reaches a lab without relying on platform-specific implementation details.

## 4. Phase 1 — Repository & Platform Foundation

### Objective
Create the technical skeleton for independent components.

### Build
- Monorepo structure
- Training Website frontend/backend placeholders
- Lab Controller placeholder
- Lab Interface placeholder
- EVE-NG adapter location
- Docker Compose foundation
- Environment configuration example
- Deployment scripts location
- Architecture/development documentation
- Git ignore and branch workflow

### Deliverables
- Buildable service structure
- Separate containers
- Repeatable deployment foundation

### Exit criteria
All three application components have independent service boundaries and can be deployed on one VM.

## 5. Phase 2 — Training Website Foundation

### Objective
Build the core application platform before courses, subscriptions and labs are added.

### Backend
- FastAPI application structure
- API versioning strategy
- Configuration management
- Database connection/session management
- SQLAlchemy models
- Alembic migrations
- Health/readiness endpoints
- Error handling foundation
- Request/response schema structure
- Logging foundation
- Test structure

### Data/domain foundation
- User
- Organization
- Individual subscriber
- Role
- Membership
- Account status
- Audit identity
- Tenant/customer ownership

### Authentication foundation
- Registration workflow
- Login workflow
- Password hashing
- Session/token strategy
- Logout
- Account activation
- Password reset architecture
- Basic authentication tests

### Authorization foundation
- Role model
- Permission model
- Resource ownership rules
- Organization membership checks
- Individual account rules

### Frontend
- Next.js application foundation
- Shared layout
- Navigation
- Authentication pages
- Login/register UI
- Basic dashboard shell
- Protected-route foundation
- API client foundation
- Error/loading states
- Responsive base design

### Administration foundation
- Basic platform-admin area
- User lookup
- Organization lookup
- Account status management foundation

### Testing
- Backend unit tests
- API tests
- Authentication tests
- Frontend smoke tests
- Database migration test

### Exit criteria
A user can create/sign into an account, an organization can exist with users, and authenticated users can reach a protected dashboard.

## 6. Phase 3 — Course & Training Management

### Objective
Turn the platform into a functioning training catalogue and learning system.

### Course catalogue
- Course creation
- Course editing
- Draft/published/retired states
- Course metadata
- Course categories
- Course visibility
- Course prerequisites

### Learning structure
- Modules
- Lessons
- Topics
- Lab references
- Course ordering
- Content metadata
- Attachments/resources

### Training delivery
- Cohorts/batches
- Start/end dates
- Trainer assignment
- Schedule
- Enrollment limits
- Enrollment status

### Enrollment
- Individual enrollment
- Organization enrollment
- Student enrollment
- Enrollment approval
- Enrollment cancellation
- Completion state

### Progress
- Lesson progress
- Module progress
- Course progress
- Completion tracking

### Administration
- Course admin
- Batch admin
- Enrollment admin
- Trainer views

### Exit criteria
A user can browse a published course, enroll, access structured learning content and have progress recorded.

## 7. Phase 4 — Subscription, Commercial & Access Management

### Objective
Create the commercial/access layer for organizations and individuals.

### Plans
- Subscription plans
- Plan features
- Plan duration
- Limits/quotas
- Active/inactive plans

### Individual subscriptions
- Subscribe
- Activation
- Renewal
- Expiry
- Cancellation
- Grace-period architecture

### Organization/customer contracts
- Customer account
- Contract
- Seat/user allocation
- Contract dates
- Purchased courses
- Purchased lab access

### Entitlements
- Course entitlement
- Lab entitlement
- User entitlement
- Organization entitlement
- Entitlement expiry
- Access checks

### Payments
- Payment abstraction
- Transaction record
- Payment status
- Invoice/reference support
- Refund architecture
- QR-payment integration boundary
- Gateway integration boundary

### Audit
- Subscription events
- Payment events
- Access decisions

### Exit criteria
Access to paid courses/labs is controlled by explicit subscription/contract entitlements.

## 8. Phase 5 — Lab Controller

### Objective
Build the generic service that manages the lifecycle of labs without embedding EVE-NG-specific logic.

### Domain
- Lab template
- Lab type
- Lab instance
- Lab assignment
- Lab session
- Lab state
- Lab access grant
- Usage record

### Lifecycle
- Create
- Provision
- Start
- Stop
- Reset
- Rebuild
- Delete
- Expire

### Assignment
- Assign to student
- Assign to organization
- Unassign
- Validate entitlement
- Validate availability

### Status
- Desired state
- Actual state
- Health
- Last operation
- Error state
- Capacity state

### API
- Lab catalogue
- Instance creation
- Instance retrieval
- Start/stop/reset
- Delete
- Status
- Usage

### Reliability
- Idempotent operations
- Request tracking
- Timeouts
- Retry policy
- Operation history
- Concurrency protection

### Security
- Service authentication
- Authorization
- Audit logging
- Secret handling

### Exit criteria
The controller can manage a lab instance using a platform-neutral contract and does not need to know EVE-NG implementation details.

## 9. Phase 6 — Lab Interface

### Objective
Create the platform-specific integration layer between Lab Controller and the lab execution platform.

### Generic contract
- Create lab
- Delete lab
- Start lab
- Stop lab
- Reset lab
- Get lab status
- Get topology
- Get access information
- Health check

### Adapter architecture
- Interface definition
- Adapter registry
- Platform capability discovery
- Error normalization
- Operation mapping

### EVE-NG implementation
- Connection/configuration
- Authentication
- Lab discovery
- Lab creation/mapping
- Node/topology operations
- Start/stop operations
- Reset operations
- Status retrieval
- Access information
- Failure handling

### Testing
- Mock interface tests
- Contract tests
- EVE-NG integration tests
- Failure/retry tests

### Exit criteria
Lab Controller can manage an EVE-NG lab entirely through Lab Interface, without embedding EVE-NG-specific calls in the controller.

## 10. Phase 7 — Student Lab Experience

### Objective
Expose lab capabilities cleanly in the Training Website.

### Student experience
- My courses
- My labs
- Available labs
- Assigned labs
- Lab details
- Launch lab
- Stop lab
- Reset lab
- Lab status
- Lab instructions
- Access details
- Usage history

### Course integration
- Module-to-lab mapping
- Lab prerequisites
- Lab completion state
- Lab attempt tracking

### Session/access
- Lab access window
- Session start/end
- Expiry handling
- Concurrent session rules

### Exit criteria
A student with valid entitlement can select an assigned lab, launch it, work with it and control its lifecycle from the Training Website.

## 11. Phase 8 — Multi-Tenant Platform

### Objective
Make the single platform safely support multiple organizations while retaining individual subscriptions.

### Organization management
- Organization profile
- Organization administrator
- Members
- Teams/groups
- Organization settings

### Tenant isolation
- Tenant-aware records
- Tenant-aware authorization
- Tenant-scoped administration
- Cross-tenant protection

### Organization training
- Organization course assignments
- Organization cohorts
- Organization lab allocations
- Seat management
- Usage visibility

### Individual model
- Personal account
- Personal subscriptions
- Personal entitlements
- Personal lab selection

### Reporting
- Organization usage
- Student progress
- Lab usage
- Subscription status

### Exit criteria
Two unrelated organizations can use the platform while their users, courses, entitlements, labs and administrative data remain correctly separated.

## 12. Phase 9 — Operations & Administration

### Objective
Provide operational control over the complete platform.

### Admin
- Users
- Organizations
- Courses
- Enrollments
- Subscriptions
- Labs
- Lab templates
- Access grants

### Monitoring
- Application health
- Service health
- Lab-controller health
- Lab-interface health
- Database health
- EVE-NG integration health

### Reporting
- User counts
- Course metrics
- Enrollment
- Subscription
- Lab usage
- Resource usage
- Operational events

### Audit
- Administrative actions
- Authentication events
- Authorization events
- Subscription changes
- Lab operations

### Backup/recovery
- Database backup
- Configuration backup
- Recovery procedures
- Restore validation

### Exit criteria
An administrator can operate the platform and diagnose common application/lab problems without direct database manipulation.

## 13. Phase 10 — Security, Reliability & Production Hardening

### Security
- Authentication hardening
- Authorization review
- Secure cookies/tokens
- Password policy
- Secret management
- API input validation
- CSRF strategy where applicable
- Rate limiting
- Abuse controls
- Audit coverage

### Reliability
- Health/readiness
- Graceful shutdown
- Retry policy
- Transaction integrity
- Data consistency
- Idempotency
- Concurrency controls

### Platform
- Container hardening
- Least-privilege execution
- Network segmentation
- Secure configuration
- TLS/reverse proxy readiness

### Exit criteria
The platform has documented security controls, operational recovery procedures and production-oriented defaults.

## 14. Phase 11 — Testing & Automation

### Testing layers
- Unit
- API
- Database
- Integration
- Contract
- End-to-end
- UI smoke
- Lab integration
- Failure/recovery

### Automation
- Test execution
- Formatting/linting
- Type checking
- Dependency checks
- Build validation
- Container build validation

### CI/CD
- Pull request checks
- Main-branch checks
- Build artifacts
- Release tagging
- Deployment validation

### Exit criteria
Core functionality is protected by repeatable automated tests and every release candidate passes CI validation.

## 15. Phase 12 — Production & Commercial Readiness

### Customer onboarding
- Organization onboarding
- Individual onboarding
- Administrator onboarding
- Student invitation
- Subscription activation

### Product catalogue
- Course catalogue
- Lab catalogue
- Packages/plans
- Availability rules

### Commercial operations
- Subscription lifecycle
- Contract lifecycle
- Billing records
- Payment provider integration
- Invoicing support
- Usage/quota enforcement

### Operational readiness
- Release process
- Versioning
- Support runbooks
- Customer documentation
- Admin documentation
- Disaster recovery procedures
- Upgrade procedures

### Exit criteria
The platform can be deployed, onboarded, operated, supported and commercially used with documented processes.

## 16. End-to-End User Journeys

### Individual
Register → verify account → choose course/plan → subscribe → receive entitlement → enroll → access course → select eligible lab → launch lab → complete work → track progress.

### Organization
Organization created → administrator invited → contract/subscription activated → seats/users provisioned → courses assigned → students enrolled → labs allocated → students access labs → administrator monitors usage/progress.

### Student
Login → dashboard → course → module → lab → launch → work → reset/stop → progress recorded.

### Administrator
Login → organizations/users/courses/subscriptions/labs → configure → monitor → audit → report.

## 17. Lab Lifecycle

```
TEMPLATE
  ↓
REQUESTED
  ↓
PROVISIONING
  ↓
READY
  ↓
RUNNING
  ↓
STOPPED
  ↓
RESETTING → READY
  ↓
EXPIRED
  ↓
DELETING
  ↓
DELETED
```

The exact state machine will be finalized during Phase 5.

## 18. Course Lifecycle

```
DRAFT → REVIEW → PUBLISHED → RETIRED
```

## 19. Subscription Lifecycle

```
PENDING → ACTIVE → EXPIRING → EXPIRED
             ↓
          CANCELLED
```

The exact business rules will be finalized during Phase 4.

## 20. Component Responsibilities

### Training Website
Owns user-facing workflows, courses, subscriptions, enrollment, progress and lab access.

### Lab Controller
Owns lab lifecycle and orchestration.

### Lab Interface
Owns platform-specific lab integration.

### EVE-NG
Executes the network lab environments.

## 21. Repository Structure

```
Training-Platform/
├── training-website/
│   ├── frontend/
│   └── backend/
├── lab-controller/
├── lab-interface/
│   └── eveng/
├── deployment/
│   ├── docker/
│   └── scripts/
└── docs/
```

## 22. Deployment Model

Initial:

```
One VM
├── Training Website containers
├── Lab Controller container
├── Lab Interface container
├── PostgreSQL
└── EVE-NG
```

Application code and persistent application configuration use a dedicated application boundary such as `/opt/training-platform/`. EVE-NG system files remain under `/opt/unetlab/`.

Later, individual services may move to separate hosts without changing their logical responsibilities.

## 23. Development Workflow

GitHub is the source of truth.

1. Create/select issue.
2. Move work to planned/in progress.
3. Implement in feature branch.
4. Commit to GitHub.
5. Open/review pull request.
6. Merge to main after review.
7. Pull selected main revision into the EVE-NG VM.
8. Deploy.
9. Test.
10. Log defects/follow-up work in GitHub.

## 24. Phase Exit Rule

A phase is not considered complete merely because code exists. It is complete when its documented deliverables are implemented, tested, integrated with the preceding phase, and validated in the target development environment.

## 25. Deferred/Future Enhancements

These are intentionally not required for the initial implementation but should remain compatible with the architecture:

- Additional lab execution platforms through new Lab Interface adapters
- Advanced scheduling and reservations
- Resource quotas
- Usage-based billing
- Automated lab expiry
- Content authoring improvements
- Certificates/badges
- Advanced analytics
- Customer self-service administration
- High-availability deployment
- Horizontal scaling
- External object storage
- Notifications and messaging

## 26. Current Status

Phase 0: Defined
Phase 1: Repository foundation implemented in PR #2
Phase 2: Training Website foundation in progress in PR #4

The detailed task breakdown for each phase will be tracked through GitHub Issues and the Training Platform Development GitHub Project.
