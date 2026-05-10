# Clone ↔ FreeOS Integration Plan

**Date:** 2026-05-11  
**Milestone:** M3 — FreeOS integration plan

---

## Current State

| Project | Category | Status | North Star | Notes |
|---------|----------|--------|------------|-------|
| Clone   | SVTool   | paused | undefined  | Insurance market research in progress (M1); tool scope TBD (M2) |
| FreeOS  | VERTICAL | paused | undefined  | No milestones yet; connected to Clone |

Both projects are pre-spec. This plan maps the **logical touchpoints** and lists the open questions that must be resolved before any technical integration is designed.

---

## Touchpoint Map

### 1. User / Target Segment Overlap
- **Clone** → SVTool targeting likely insurance agents, adjusters, or self-employed freelancers needing policy management  
- **FreeOS** → vertical OS implies a curated platform for a specific user type  
- **Touchpoint**: If FreeOS's target user matches Clone's target user, Clone could be a **bundled app or first-class tool** inside FreeOS rather than a standalone product

### 2. Data Layer
- Clone will generate structured insurance/policy data (research, comparisons, scenarios)  
- FreeOS as a vertical OS could own the **user profile, identity, and data store**  
- **Touchpoint**: FreeOS provides the data persistence + auth layer; Clone reads/writes user insurance records through FreeOS APIs

### 3. Distribution Channel
- FreeOS as a platform = built-in distribution for Clone  
- **Touchpoint**: Clone ships as a pre-installed or default app on FreeOS → Clone gains users via FreeOS adoption, no separate GTM needed

### 4. Business Model Alignment
- If Clone monetizes via subscription or per-analysis fee, FreeOS could offer it as a **premium tier add-on**  
- **Touchpoint**: FreeOS billing layer handles Clone's payments (bundle pricing, single billing relationship with user)

### 5. Shared Infrastructure
- Auth, notifications, local storage, background sync  
- **Touchpoint**: FreeOS provides OS-level services (keychain, sync, push); Clone consumes them rather than building its own

---

## Open Questions (must resolve before technical design)

1. **What is FreeOS's core vertical?** (insurance? freelance? SMB?) — determines whether user overlap is real
2. **Is FreeOS a web OS, desktop OS, or mobile OS?** — determines what runtime Clone runs on
3. **Is Clone a standalone web app or a FreeOS-native module?** — defines the integration surface
4. **Who owns identity/auth?** — FreeOS-managed or Clone-managed?
5. **What is the release order?** — Clone first with later FreeOS migration, or FreeOS ships first with Clone bundled?

---

## Recommended Next Steps

| Priority | Action | Owner |
|----------|--------|-------|
| P0 | Complete Clone M1 (insurance research) + M2 (SVTool scope) — these define what Clone actually does | Clone/M1, M2 |
| P0 | Define FreeOS north star and first milestone — no integration design is possible until FreeOS scope is known | FreeOS |
| P1 | Answer the 5 open questions above (brief doc or conversation) | User |
| P1 | Once both scopes are defined: revisit this plan and map API surface | Claude |

---

## Integration Risk

> **Integration before spec = wasted work.**  
> Both projects are paused and unspecified. The safest path is to complete Clone M1+M2 and define FreeOS's first milestone first, then reconvene on this plan with real specs.

---

_Written by Claude for Clone M3_
