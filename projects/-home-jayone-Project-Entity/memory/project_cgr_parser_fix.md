---
name: CGR harness trigger over-count
description: The CGR compliance harness parser over-counts triggers by treating each file-path mention as a separate claim. Same claim repeated across sentences inflates the denominator. Fix groups triggers by claim identity.
type: project
originSessionId: 9d7d186b-227d-481d-a1b6-874de9a0cd8d
---
Discovered 2026-04-17 during in-session CGR treatment run. Responses hand-rated at 0.9-1.0 compliance scored 0.55 from the parser because the trigger regex (`RE_TRIGGER` in `cgr_compliance_harness.py`) captures every file-path / metric / version mention separately, even when a single `[CGR:tool:target]` tag legitimately covers multiple mentions of the same claim.

**Why**: Linguistically natural responses restate the subject ("scripts/corpus_router.py" appears 3 times in one answer, each mention tagged once overall). Current parser divides `tagged_count / total_triggers` without claim-identity grouping → systematic under-count.

**How to apply**:
- When building denominator: group triggers by normalized identity (file path canonicalized, metric name + value pair, etc.) before counting.
- Simple fix: deduplicate `RE_TRIGGER` matches by their normalized string before dividing.
- Better fix: parse claim-tag proximity (trigger within N chars of a tag = covered).
- Keep raw `tag_density` metric unchanged — it's honest. Add `normalized_cgr_rate` as the adjusted metric.
- When comparing control vs treatment: report both raw and normalized rates; normalized is the interpretable one.
