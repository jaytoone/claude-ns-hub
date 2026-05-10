# Clone SVTool — Scope & Feature Spec

_Written: 2026-05-11 | Status: Draft_

## What is Clone?

Clone is an SVTool (Solo Venture Tool) for the insurance domain. It automates the research, comparison, and optimization workflows that a solo operator would otherwise do manually — acting as a "clone" of an expert insurance analyst.

Core premise: Korean individual insurance products are complex, poorly standardized, and difficult to compare. Clone makes sense of this chaos for a 1-person operation.

## Primary Use Cases

### 1. Insurance Product Research (M1 — 보험 조사)
- Ingest product PDFs / web pages from major Korean insurers
- Normalize coverage terms, exclusions, premium structures
- Surface key differentiators across products in a comparison table

### 2. Coverage Gap Analysis
- Map a user's current coverage → identify gaps vs. life-stage needs
- Score adequacy (health / life / car / liability)
- Recommend add-on products that fill gaps without duplication

### 3. Premium Optimization
- Given target coverage, find the lowest-premium combination
- Model premium escalation over time (age-linked products)
- Flag products with high lapse rates or hidden penalty clauses

### 4. Renewal & Event Triggers
- Track renewal dates, grace periods, benefit trigger conditions
- Auto-remind when life events (marriage, child, home) open better product windows

## Out of Scope (v1)
- Direct policy purchase / API integration with insurers
- Claims processing
- Non-Korean products

## FreeOS Integration Touchpoints (→ M3)
- Clone feeds coverage data into FreeOS's financial freedom model
- FreeOS asks: "What coverage is required to sustain my target monthly outflow under adverse health events?"
- Clone answers with a minimum viable coverage bundle + cost

## Tech Stack (proposed)
- Python scraper / PDF parser for product ingestion
- SQLite or flat-file store for normalized product DB
- LLM layer (Claude) for gap analysis and recommendations
- CLI or simple web UI (Dash / Streamlit) for operator use

## North Star Metric
**Coverage Adequacy Score** (0–100) for a given user profile, computed from gap analysis output. Target: user reaches 80+ with minimum monthly premium spend.

## Milestones Sequence
| ID | Task | Status |
|----|------|--------|
| M1 | Insurance market research — benchmark products | queued |
| M2 | This spec document | → completing |
| M3 | FreeOS integration plan | queued |
| M4 | MVP: product ingestion + gap analysis CLI | (future) |
| M5 | UI for comparison table | (future) |
