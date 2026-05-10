---
name: expert-questions
description: "Expert Perspective Question Templates — Review tasks from Architect/QA/Security/Performance expert viewpoints. Triggered when pattern-search returns no results, when approaching new problems, or when domain expert perspectives are needed. On Phase 1 detection of a new problem with no patterns, call Skill(\"expert-questions\")."
trigger: manual
tags:
  - expert
  - architect
  - adr
  - qa
  - security
  - owasp
  - pattern-none
---

# Expert Perspective Question Templates

Structure questions from each expert perspective when approaching new problems.
For TDD questions, refer to `Skill("tdd-guide")`.

---

## Architect (Software Architecture)

**Basis**: ADR (Architecture Decision Records, Michael Nygard), Clean Architecture (Robert Martin)

### Key Questions
- **Change driver**: What is the context and forces behind this decision?
- **Alternatives**: What other options were considered? Why were they rejected?
- **Consequences**: What are the positive/negative consequences of this decision?
- **Boundaries**: What is the scope of this component's responsibility? (Single Responsibility)

### Record in ADR Format
```markdown
## Decision: [title]
**Status**: Proposed | Accepted | Deprecated
**Context**: [Why was this decision needed]
**Decision**: [What was chosen]
**Rationale**: [Why this choice]
**Consequences**: [Positive consequences] / [Negative consequences]
```

### Trade-off Matrix
| Criterion | Option A | Option B |
|-----------|----------|----------|
| Performance | HIGH | MEDIUM |
| Maintainability | LOW | HIGH |
| Complexity | LOW | HIGH |

---

## QA (Quality Assurance)

**Basis**: Agile Testing Quadrants (Lisa Crispin & Janet Gregory), ISTQB

### Testing Quadrants

| | Team Support | Product Critique |
|--|-------------|-----------------|
| **Technology-facing** | Q1: Unit/Component Tests (TDD) | Q4: Performance/Load/Security Tests |
| **Business-facing** | Q2: Acceptance Tests/Story Tests | Q3: Exploratory/Usability Tests |

### Key Questions
- **Q1 (Unit)**: What are the boundary values, null/undefined, empty array cases per function?
- **Q2 (Acceptance)**: Are there tests that directly verify the business rules?
- **Q3 (Exploratory)**: What scenarios can't be discovered through actual user flows?
- **Q4 (Non-functional)**: Can it handle response time P95 and 100 concurrent users?

### Risk-Based Testing
- **HIGH**: Potential financial/data loss → Cover all quadrants
- **MEDIUM**: Functional errors → Q1+Q2
- **LOW**: Simple UI → Q1 only

---

## Security

**Basis**: OWASP Top 10 (2021), OWASP Testing Guide v4.2

### OWASP Top 10 Checklist (2021)
- [ ] **A01 Broken Access Control**: Can resources be accessed without authentication?
- [ ] **A02 Cryptographic Failures**: Is sensitive data transmitted/stored in plaintext?
- [ ] **A03 Injection**: Is there input validation for SQL/NoSQL/LDAP/OS injection?
- [ ] **A04 Insecure Design**: Is threat modeling reflected in the design?
- [ ] **A05 Security Misconfiguration**: Default credentials, unnecessary ports/services exposed?
- [ ] **A06 Vulnerable Components**: Are libraries with known CVEs being used?
- [ ] **A07 Authentication/Session Management**: JWT expiration, session fixation attack defense?
- [ ] **A08 Software Integrity**: Is code loaded from untrusted sources?
- [ ] **A09 Logging/Monitoring Failures**: Are attack attempts being logged?
- [ ] **A10 SSRF**: Can the server make arbitrary URL requests?

### Code Review Points
```typescript
// ❌ SQL Injection vulnerable
const query = `SELECT * FROM users WHERE id = ${userId}`

// ✅ Parameterized Query
const query = `SELECT * FROM users WHERE id = $1`
db.query(query, [userId])
```

---

## Performance Engineering

**Basis**: Google Web Vitals, Google SRE Book (Beyer et al.)

### Measurement Metrics
- **LCP** (Largest Contentful Paint): < 2.5s (Good), 2.5-4s (Needs Work), > 4s (Poor)
- **CLS** (Cumulative Layout Shift): < 0.1 (Good)
- **INP** (Interaction to Next Paint, 2024 standard): < 200ms
- **TTFB** (Time to First Byte): < 800ms

### SRE Four Golden Signals
- **Latency**: Measure normal request vs error response latency separately
- **Traffic**: RPS (Requests Per Second)
- **Errors**: 4xx/5xx error rate
- **Saturation**: CPU/memory/disk saturation level

### Performance Budget Example
| Resource | Limit |
|----------|-------|
| Initial JS bundle | < 200KB (gzip) |
| Image optimization | WebP/AVIF preferred |
| API response P95 | < 200ms |
| DB query | < 50ms (no N+1) |
