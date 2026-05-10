---
name: long-script
description: Use when writing YouTube longform (8-15 min) English scripts for AI engineering / dev tool content targeting global AI engineers (Claude Code, Cursor, Aider users). Format = on-camera founder/engineer + own voice (no character, no TTS). Enforces narrative arc (open loop → stakes → problem → failed attempts → discovery → proof → demo → CTA), 3-cliff retention design (60s/3min/6min), keyword-validated titles, real terminal footage, and founder-led presenter rules.
---

# YouTube Longform Script — AI Dev Authority Content (On-Camera Presenter)

## Overview

Narrative-arc, 8-15 minute **English** script system for **on-camera founder/engineer** targeting **global AI engineers**. Drives GitHub stars / PyPI installs / subscribers through authority + proof.

**Format**: presenter on camera + own voice + real terminal B-roll. No animated character, no TTS.

Core principle: **Longform retention is a story, not an explanation.**
Shorts optimize for 3s hook + 30s completion. Longform optimizes for **3 retention cliffs** (60s / 3min / 6min) across a narrative arc.

> **Script = narrative engine that pulls the viewer past each cliff.**
> Story sequence + proof order matter more than information density for drop-off.

> **AI dev audience has an extreme fake detector.**
> Stock animation · generic B-roll · AI-generated thumbnails = exit in <2s.
> Real terminal + real benchmarks + real code = trust currency.

> **Founder-led authority: the face IS the channel.**
> Viewers subscribe to a person, not a topic. Personality + specificity + credibility = retention engine.
> You can't hide behind a character — which is a net advantage for trust.

---

## Production Format (Non-Negotiable for AI Dev ICP)

```
MAIN TRACK (A): Presenter on camera (16:9, 1080p+)
  - Face visible, eye-level framing
  - Background: uncluttered, one brand signal OK (bookshelf / monitor / logo)
  - Lighting: key light 45° front-side, no harsh shadows
  - Camera: webcam 1080p minimum; prefer mirrorless/DSLR clean HDMI
  - Eye contact: look at lens 80%+ of the time (script reading = fake detector trigger)

MAIN TRACK (B): Real screen recording (cut in during technical sections)
  - Claude Code / Cursor / VS Code live session
  - Dark theme, font 14pt+, clean tabs
  - NO AI-generated code walkthroughs (fake detector triggers)
  - Screen = ~50-60% of runtime; presenter on camera = ~35-45%

Cut rhythm:
  - Presenter (10-15s) → Screen (15-30s) → Presenter (reaction/insight, 5-10s) → repeat
  - Never more than 30 seconds on one shot type (kills engagement)

TEXT OVERLAYS: evidence layer
  - Benchmark numbers (Bold, center or upper-left on screen shots)
  - Key claims (short phrase, highlighted during presenter shots)
  - Chapter markers (subtle, upper area)
  - Lower-third nameplate: first presenter appearance only

NARRATION: your own voice, live on-camera (no TTS, no dubbing)
  - Write at 1.3× target speech rate (AI devs watch at 1.5-2×)
  - Conversational tone > formal academic
  - Global English: neutral accent acceptable, slow-down on key numbers
  - Written script as backbone, but DO NOT read word-for-word on camera
    → use script as bullet prompts + practice cold-run 2× before recording
    → reading kills eye contact + sounds robotic
  - Burned-in English subtitles recommended (accommodates non-native listeners)

AUDIO QUALITY (critical for founder-led):
  - External mic required (lavalier / shotgun / USB condenser)
  - Webcam built-in mic = immediate fake-detector trigger on audio
  - Record in quiet room, treated if possible (blankets/curtains reduce echo)
  - Post-process: noise reduction + compression + -14 LUFS normalization

EDITING: CapCut / DaVinci Resolve / Final Cut
  - Chapter markers at cliff points (60s / 3min / 6min)
  - B-roll cuts every 4-6s during screen sections
  - Presenter cuts: only for bad takes or pacing (not every 2s — jitters viewer)
  - BGM: optional, ambient/lofi very low (-22 LUFS under voice) for screen sections only
  - Presenter sections: NO BGM (let voice carry, trust signal)
```

---

## STEP 0 — Script Engine (Before writing, ALWAYS)

### 0-1. Authority Angle — What authority are you claiming?

Longform = authority play. Pick ONE authority angle per video.

| Angle | Pattern | Example (CTX topic) |
|-------|---------|---------------------|
| **Benchmark proof** | "I tested X vs Y, here's what happened" | "I tested BM25 vs my retrieval on Flask/FastAPI/Requests" |
| **Contrarian evidence** | "Everyone uses X. I tried X+Y. Y won." | "Everyone uses embedding search. BM25 + import graph beats it by 16%." |
| **Research journey** | "I iterated from 0.169 to 0.746. Here's each step." | "How I 4.4×'d code retrieval recall" |
| **Working system reveal** | "I built X. It's running in production. Here's how." | "The Claude Code hook that gives me cross-session memory" |
| **Failure autopsy** | "My first attempt failed. Here's why the second worked." | "Why my first BM25 tokenizer killed the whole system" |
| **Architecture breakdown** | "[System X] under the hood — what no one explains" | "The 4 triggers that make Claude Code find the right file" |
| **Paper implementation** | "I implemented [paper]. Here's what they got wrong." | "LocAgent claimed 92.7% — I got 50%. Here's why." |

### 0-2. Villain Structure — What is the specific enemy?

Longform needs a sustained villain (not just the 60s shorts version).

```
Villain candidates for AI dev content:
- 기존 방법의 한계 (embedding search limits on code)
- 모든 사람이 믿는 가정 ("embeddings > keyword search for semantic tasks")
- 대기업 제품의 숨은 약점 (Cursor/Copilot cross-session memory 부재)
- 논문이 실제로 측정하지 않은 것 (paper benchmark ≠ real codebases)
- 시청자가 지금 겪는 구체적 고통 (agentic grep taking 20 rounds)

Hero = 나의 시스템 / 발견 / 증명된 접근

요구조건:
- Villain은 "구체적으로 명명 가능해야" 함 (generic "복잡함" 금지)
- Hero는 "검증 가능한 증거로 뒷받침" 되어야 함
```

### 0-3. Retention Arc — 3-Cliff Design

Unlike Shorts (5 zones × 12s), longform has 3 critical retention cliffs.

| Cliff | Timing | Risk | Design principle |
|-------|--------|------|------------------|
| **C1: 60-second cliff** | 0:45-1:00 | "Is this going to be worth 10 min?" | Show payoff proof BEFORE explaining (open loop) |
| **C2: 3-min cliff** | 2:45-3:15 | "Am I still engaged?" | Hit the strongest benchmark number or reveal at this point |
| **C3: 6-min cliff** | 5:30-6:30 | "Am I going to finish?" | Live demo / working example / "here's the code" moment |

**Research basis** [REASONED: public retention curve patterns for AI-dev YouTube, April 2026]: retention drops ~15-20% at each cliff if no structural lock-in. Structural lock-in = new information/proof/demo that resets engagement.

### 0-4. Open Loop Stack (Longform Version)

```
Open at 0:00-0:10: Show END state BEFORE explaining anything.
  "This is Claude Code. Without my system. Watch. Now with it. See the difference?"
  → Viewer question #1: "How does that work?"

Cliff 1 (60s): Partially answer #1, open question #2
  "The trick is not what most people think."
  → Viewer question #2: "What's the actual trick?"

Cliff 2 (3min): Answer #2 with proof, open question #3
  "This is why it beats BM25 on Flask by +0.198."
  → Viewer question #3: "Can I actually use this?"

Cliff 3 (6min): Live demo answers #3, open question #4
  "pip install ctx-retriever — 30 seconds to set up."
  → Viewer question #4: "What's next? What about [edge case]?"

End: CTA addresses #4 + invites to subscribe for part 2
  "Next video: the 4 triggers under the hood — subscribe."
```

---

## Script Architecture — 10-minute reference structure

| Section | Time | Goal | Key rule |
|---------|------|------|----------|
| **OPEN LOOP** | 0:00-0:10 | Show end state | Proof before explanation. No intro. |
| **STAKES** | 0:10-0:45 | Why this matters to *you* | Identity activation ("1M+ Claude Code users hit this") |
| **PROBLEM** | 0:45-2:00 | Specific pain, live | Real Claude Code session wasting time, viewer recognizes self |
| **FAILED ATTEMPTS** | 2:00-3:00 | What didn't work | Credibility via showing losses, not just wins |
| **DISCOVERY** | 3:00-6:00 | How you solved it | ONE query walked through end-to-end |
| **PROOF** | 6:00-8:00 | Evidence stack | Benchmarks, specific numbers, external validation |
| **LIVE DEMO** | 8:00-9:00 | Install & run in real time | Converts viewers → users |
| **CTA + LOOP** | 9:00-10:00 | GitHub/PyPI/subscribe + tease next | Compound the series |

**Scaling to 8-min or 15-min**: compress/expand DISCOVERY + PROOF sections. Keep OPEN LOOP / STAKES / CTA timing fixed.

---

## Hook Design (0:00-0:10) — Different from Shorts

Shorts hook = 1.5s visual shock.
Longform hook = 10s open loop that promises a specific payoff.

### Formula: `[End state demonstrated] + [Specific promised outcome]`

```
Weak (academic): "Today I'm going to show you my retrieval system."
Weak (tutorial): "In this video we'll install and configure CTX."

Strong (open loop):
  "This is Claude Code — asked to continue from yesterday. Nothing.
   Same prompt, with one hook installed. [live demo of CTX injection]
   How? Let me show you."

Strong (benchmark reveal):
  "BM25 on Flask: 0.347. My system: 0.545. Same codebase, same queries.
   Here's what I did — and why it works on FastAPI and Requests too."
```

### Hook rules for AI dev longform

- [ ] Show working output IN THE FIRST 10 SECONDS (real terminal, real code)
- [ ] State ONE specific promised outcome (not vague "you'll learn about X")
- [ ] Avoid: "Hey guys welcome", logo intro, "today we're going to...", any self-intro
- [ ] ✅ OK to skip intro entirely and open cold on the demo

---

## Stakes Section (0:10-0:45) — Identity Activation

```
Goal: viewer thinks "I'm one of those people, this is about me."

Pattern: [Platform anchor] + [Specific number/stat] + [Shared pain named]

O: "Claude Code now has over 1 million daily users.
    Every one of them hits this wall by end of session two.
    If you've ever typed 'continue from yesterday' and watched Claude
    re-ask for context — this is why."

X (generic): "AI coding assistants are great but they have limitations"
X (research-style): "Previous work has explored context injection for LLMs..."
```

**Anti-pattern**: treating the intro as academic context. For 1.5× watchers, every second without personal relevance = exit.

---

## Problem Section (0:45-2:00) — Live Pain Recognition

```
Goal: viewer sees their own problem on screen.

Structure:
  - Real screen recording of the pain (no reenactment)
  - Specific failure mode demonstrated
  - Time counter visible (emphasizes waste)

O: [screen recording] "Here's Claude Code opening a fresh session.
    [counter starts] I type: 'continue from yesterday's auth refactor.'
    It says: 'Could you remind me what we were working on?'
    [counter: 00:00:47] 47 seconds wasted.
    I close it. Open again. Same thing.
    [cut to benchmark] This happens 31 times per day on average."

X: explaining the problem abstractly with stock animation
```

---

## Failed Attempts Section (2:00-3:00) — Credibility

**Counter-intuitive principle**: showing losses builds more trust than showing wins alone.

```
Goal: establish that you actually tried the obvious things.

Pattern: "I tried X. Here's what happened. Then I tried Y. Same problem.
         Then I noticed something."

Structure:
  - Attempt 1 (obvious solution) → show data/result → why it failed
  - Attempt 2 (next obvious solution) → same → why it failed
  - Attempt 3 (the insight) → introduce the actual solution

O: "First I tried embeddings — thought semantic similarity would solve it.
    [benchmark: 0.740 on CodeSearchNet]
    But on my actual codebase? 0.152. Worse than grep.
    Then I tried BM25 vanilla. Better — 0.337. Still not great.
    Then I noticed: the queries that failed all had one thing in common..."

X: "I built the perfect solution from scratch" (no failure = no credibility)
```

---

## Discovery Section (3:00-6:00) — Walk Through ONE Example

**Counter-intuitive**: depth of ONE example beats breadth of five.

```
Goal: viewer walks through the mechanism with you, not watches it.

Structure:
  - Pick ONE specific query/case
  - Walk through what happens step by step
  - Show the code, the data, the output at each step
  - Narrate the "why" at each decision point

O: "Let's take one query: 'what uses AuthService?'
    BM25 returns: files containing 'AuthService' as text — 8 files.
    But only 2 actually use it. The rest just mention it in comments.
    My system: detects EXPLICIT_SYMBOL trigger. Looks up symbol index.
    Finds 2 files. Now does BFS on import graph — one hop out.
    Finds 5 more files that import AuthService transitively.
    Total: 7 files, 100% relevant.
    R@5 on this class of query: 1.000."

X: "The system uses 4 triggers, a symbol index, an import graph,
    a tokenizer, a ranker..." (list ≠ understanding)
```

---

## Proof Section (6:00-8:00) — Evidence Stack

```
Goal: numbers + external validation + reproducibility.

Evidence hierarchy (strongest → weakest):
1. External codebase benchmarks (Flask/FastAPI/Requests) — held-out validation
2. Specific numerical deltas (+0.198, not "significantly better")
3. Comparison to well-known baselines (BM25, not proprietary methods)
4. Statistical confidence (95% CI if you have it)
5. Paper reference (if implementing a published method)
6. Your own benchmark (weakest — can always be accused of overfitting)

Presentation rules:
- Show the actual data visualization on screen (chart, table)
- Say the numbers out loud ("Flask: point five four five. BM25: point three four seven.")
- Name the conditions explicitly ("same 35 queries, held-out codebase")
- Acknowledge limits ("text-to-code semantic search is NOT where this wins")
```

**AI dev audience specifically wants**:
- Exact numbers, not "significant improvement"
- Named baselines (they can mentally verify)
- Reproducible setup (they might actually try it)
- Honest limits (refusing to claim what you didn't measure)

---

## Live Demo Section (8:00-9:00) — Conversion Moment

```
Goal: viewer sees they can actually use this in 60 seconds.

Structure:
  - Real terminal
  - Copy-paste commands visible on screen
  - Real-time (no cuts during install unless truly slow)
  - End with a working output that mirrors the opening

O: [live terminal]
    "pip install ctx-retriever" [shows 4s install]
    "Add this to ~/.claude/settings.json:" [shows JSON]
    "Restart Claude Code."
    [new terminal] "continue from yesterday"
    [CTX injection visible, Claude responds with specific context]
    "That's it."

X: slide deck showing install steps
X: "You can find instructions in the description"
```

**Conversion anchor**: this section drives PyPI installs + GitHub stars. Optimize for "they can try it RIGHT NOW while watching."

---

## CTA + Loop (9:00-10:00) — Compound Series

```
Two-part CTA:
1. Primary action (GitHub star OR PyPI install OR subscribe)
2. Next-video tease (specific, not generic)

O: "If this saves you even one 'continue from yesterday' reset —
    star on GitHub. Link in description.
    Next video: the 4 triggers under the hood — how the system
    decides which retrieval to run. Subscribe so you don't miss it."

X: "Like and subscribe if you enjoyed the video"
X: "Thanks for watching" (empty closer)
```

### CTA priority by channel stage

| Subs | Primary CTA | Notes |
|------|-------------|-------|
| <100 | Subscribe | Need base before conversion CTAs work |
| 100-1K | Subscribe + GitHub star | Build authority + early adopter signal |
| 1K-10K | GitHub star + PyPI install | Conversion to real users |
| 10K+ | Product/SaaS link | Monetization layer |

---

## Title Formula — Keyword-Validated

Based on YouTube autosuggest validation (April 2026), for AI dev / Claude Code content:

### GREEN keywords (use in title)

```
"Claude Code" — platform anchor, strongest CTR
"Claude Code memory" — all variants trending (memory tool/bank/mcp/infinite)
"Claude Code hooks" — tutorial/setup variants validated
"Context engineering" — architecture/framework framing
"MCP" / "MCP server" — trending but narrower
"Vibe coding" — broader AI-dev reach
"Anthropic Claude Code" — authority signal
```

### RED keywords (DO NOT use as title anchor)

```
"BM25 vs embedding" — dead (only 4 generic results)
"Code retrieval RAG" — noise (ragnarok/rage suggestions)
"Semantic search code" — near-zero volume
"Agentic grep" — single result
```

### Title formula

```
[Trending anchor] — [Specific outcome with number] + [Optional contrast]

Examples:
✅ "Claude Code memory — the hook that beats embedding search (1.9× better, 5% tokens)"
✅ "Context engineering for Claude Code — 4 triggers I built from scratch"
✅ "Claude Code hooks tutorial — full setup for cross-session memory"
✅ "I tried 7 retrieval methods on real codebases — here's what beat BM25"

❌ "My retrieval system explained" (no anchor, no outcome)
❌ "The best way to improve Claude Code" (no specific claim)
❌ "BM25 vs embedding vs CTX" (dead keyword)
```

Character limit: 50-60 characters visible on mobile YouTube before truncation. Put keyword + outcome in the first 50 chars.

---

## Thumbnail Rules (Longform-specific)

Different from Shorts thumbnails. Longform thumbnails drive CTR from browse surface.

```
Structure:
- YOUR FACE in upper-right 30% (founder-led = face is brand)
- Large text (≥ 50% of frame): specific number/contrast
- Contrasting color: red/yellow on dark bg OR white on vivid
- Expression: focused/curious (NOT open-mouth shock — AI devs read that as clickbait)

For AI dev audience specifically:
✅ Benchmark comparison ("BM25: 0.347 vs MY SYSTEM: 0.545") + your face
✅ Code snippet + bold claim ("ONE HOOK. INFINITE MEMORY.") + your face
✅ Before/after screenshot + your face reaction
❌ Generic "shocked face + red arrow" YouTube clickbait style
❌ AI-generated face/character thumbnails (fake detector triggers)
❌ Vague "THIS CHANGES EVERYTHING" type text
❌ Hiding your face behind a logo — defeats founder-led authority
```

A/B test at least 2 thumbnails via YouTube Studio experiments after 500 views.

---

## Script Writing Rules

### Narration style for AI devs

```
Conversational (O): "So I tried embeddings first. Didn't work. Here's why."
Academic (X):       "We initially investigated dense retrieval methodologies."

Direct (O):   "The number is 0.545."
Hedged (X):   "We observed what appears to be approximately 0.54."

Show-then-tell (O): [screen shows output] "See that? That's the injection."
Tell-then-show (X): [narration 20s] ... [finally shows screen]

Specific (O): "47 seconds wasted, 31 times a day, 0.545 R@5."
Generic (X):  "A lot of time wasted, frequently, significant improvement."
```

### Pacing rules

- Sentences: mix short (5-8 words) + medium (15-20 words). Avoid long 25+ word sentences.
- Pauses: 0.3-0.5s pause after numbers and key claims (real voice advantage — emphasize with breath)
- Reading speed: write for 1.3× speech rate (AI devs listen fast)
- No filler: "um", "like", "sort of", "kind of" — cut all in post if any slip through
- Real voice pro tip: prosody + breath are your retention weapon. Use them.
  → drop pitch on key numbers (not rising)
  → pause BEFORE reveal, not after ("BM25 got... [pause] ...0.347.")

### Global English delivery

- Target: neutral/international accent acceptable — AI dev audience is non-native in ~60% of cases
- DO NOT try to fake American/British accent — sounds uncanny, triggers fake detector
- Slow-down on key technical numbers and named systems (Flask, BM25, Claude Code)
- Technical terms: keep native English pronunciation (don't over-translate)
- Burned-in English subtitles: MANDATORY (helps non-native listeners + accessibility + silent-watch)
- Bilingual option: if filming in Korean for Korean-speaking subset, still subtitle in English. But default = film in English.

---

## B-roll Sourcing Strategy (Anti-fake)

```
TIER 1 (Authority): Real terminal, real code, real benchmarks
- Your actual Claude Code session (best)
- Real PyPI install / GitHub output
- Real benchmark CSV or plot

TIER 2 (Acceptable): Minimal designed overlays
- Simple diagrams (arrows, boxes, labels)
- Text-only slides with one claim per slide
- Clean code editor views

TIER 3 (Risky — use sparingly): Stock / designed animation
- OK for 2-3 second transitions
- NEVER as primary content footage
- NEVER AI-generated code walkthroughs

TIER 4 (Kill): Stock footage of generic devs at laptops
- Triggers fake detector in <2s
- Do not use under any circumstances
```

---

## Pre-Publication Checklist

### Script (before recording)

- [ ] STEP 0 complete: angle + villain + cliff design + open loop stack
- [ ] Title has GREEN keyword + specific number + clear outcome
- [ ] Open loop shows end state in first 10 seconds
- [ ] 3 retention cliffs addressed (60s / 3min / 6min)
- [ ] Failed attempts section included (credibility)
- [ ] Discovery section walks through ONE example end-to-end
- [ ] Proof section has ≥3 numerical claims with baselines
- [ ] Live demo section shows install + run in <90 seconds
- [ ] CTA specifies next video topic

### Production (before uploading)

- [ ] Real screen recording used for ≥70% of runtime
- [ ] No stock footage of generic developers
- [ ] Chapter markers set at cliff points + section boundaries
- [ ] Thumbnail has specific number/contrast, not generic clickbait
- [ ] Description has GREEN keyword in first line
- [ ] End card links to GitHub/PyPI (not just subscribe button)

### SEO (at upload)

- [ ] Title: 50-60 chars, GREEN keyword first
- [ ] Description first line: primary keyword + specific claim
- [ ] Tags: 5-10 relevant (include all GREEN terms that apply)
- [ ] Category: Science & Technology
- [ ] Language: matches audio
- [ ] Pinned comment: GitHub link + next video tease

---

## Script Template

```markdown
## Longform #[number] — "[Title with GREEN keyword + specific outcome]"

**Authority angle**: [Benchmark proof / Contrarian evidence / Research journey / ...]
**Villain**: [specific named enemy]
**Hero**: [your specific solution/system]
**Target duration**: [10 min default]
**Primary CTA**: [GitHub star / PyPI install / Subscribe]

---

### [0:00-0:10] OPEN LOOP
VISUAL: [Real screen recording — end state demo]
NARRATION: "[10-second open loop — end state + specific promise]"
→ Viewer question: "How does that work?"

---

### [0:10-0:45] STAKES
VISUAL: [identity-activating shot — "1M+ Claude Code users"]
NARRATION: "[Why this matters to the viewer specifically]"
→ Viewer feeling: "This is about me."

---

### [0:45-2:00] PROBLEM
VISUAL: [Real Claude Code session wasting time — timer visible]
NARRATION: "[Live pain demonstration + frequency/waste stat]"
→ Viewer feeling: "Yes, this happens to me too."
CLIFF 1 (60s): ✅ question partially answered, new question opens

---

### [2:00-3:00] FAILED ATTEMPTS
VISUAL: [Benchmark data from each failed attempt]
NARRATION: "[Attempt 1 → failure. Attempt 2 → failure. Then insight.]"
→ Viewer feeling: "OK, this person actually tried things."

---

### [3:00-6:00] DISCOVERY
VISUAL: [ONE example query walked through end-to-end]
NARRATION: "[Step-by-step mechanism with visible evidence]"
→ Viewer feeling: "Oh, I see how this works now."
CLIFF 2 (3min): ✅ strongest benchmark/reveal landed

---

### [6:00-8:00] PROOF
VISUAL: [External benchmarks + comparison chart]
NARRATION: "[Specific numbers + named baselines + honest limits]"
→ Viewer feeling: "These are real results, not cherry-picked."

---

### [8:00-9:00] LIVE DEMO
VISUAL: [Real terminal — install + run in real time]
NARRATION: "[Copy-paste-run — 60 second path to working system]"
→ Viewer feeling: "I can do this right now."
CLIFF 3 (6min): ✅ live demo addresses "can I use this"

---

### [9:00-10:00] CTA + LOOP
VISUAL: [GitHub star prompt + next video tease]
NARRATION: "[Primary CTA + specific next video preview]"
→ Viewer action: GitHub star / PyPI install / subscribe

---

Title candidates (algorithm-optimized, 3):
1. [GREEN keyword — specific outcome — number/contrast]
2. [alternate phrasing]
3. [alternate phrasing]

Thumbnail concept:
- [Specific number + contrast + face/character upper-right]
- Alternative A/B: [alternate concept]

Description first line:
[Primary GREEN keyword + specific outcome statement]

Pinned comment:
[GitHub/PyPI link + next video tease]
```

---

## Series Design for Longform

```
Videos 1-3:    Authority establishment (Type = Benchmark proof / Working system reveal)
Videos 4-6:    Architecture depth (Type = Architecture breakdown / Research journey)
Videos 7+:     Community & monetization (tutorial series, live coding, Q&A)
```

**Conversion gates** (gate before progressing):
```
Videos 1-3 → 4: AVG view duration ≥ 45% AND subscribers from these videos ≥ 100
Videos 4-6 → 7: PyPI installs from CTA ≥ 500 (tracked via source tags in install instructions)
```

**Failure mode to watch**: tutorial-fatigue. If videos 4-6 drop below 30% retention, pivot back to "reveal" angle instead of "teach" angle.

---

## Anti-patterns (Immediate Rejection)

- ❌ Intro longer than 10s ("welcome back to the channel...")
- ❌ "Today we're going to talk about..."
- ❌ Self-introduction in first 30s ("I'm [name], a [role]...")
- ❌ Slide deck for more than 20% of runtime
- ❌ AI-generated B-roll of "developers working at laptops"
- ❌ Vague claims without numbers ("significantly better", "much faster")
- ❌ Tutorial format without a narrative arc (= bounces AI dev audience)
- ❌ CTA without specific next-video tease ("thanks for watching" = empty close)
- ❌ Academic citation format in narration ("Smith et al. demonstrated...")
- ❌ Hiding failures / only showing wins (= fake detector triggers)
- ❌ Title without GREEN keyword (= CTR tanks)
- ❌ Reading benchmark numbers without showing the chart on screen
- ❌ Claiming what you didn't actually measure

---

## Shorts vs Longform Key Differences

| Dimension | Shorts (60s) | Longform (8-15min) |
|-----------|--------------|---------------------|
| Hook timing | 1.5s visual shock | 10s open loop demo |
| Retention target | 30s completion (algo signal) | 3 cliffs (60s/3min/6min) |
| Primary goal | Subscribe acquisition | GitHub/PyPI conversion |
| Presenter | 메바 character (proxy) | Founder on camera (face = brand) |
| Voice | Fish Audio TTS | Your own voice, live recorded |
| Language | Korean | Global English (+ burned-in subtitles) |
| B-roll | HTML designed OK | Real screen recording required (Tier 1) |
| Narration | TTS optimized (15-char sentences) | Conversational, mix lengths, natural prosody |
| BGM | Optional (Shorts often none) | Screen sections only, never over presenter voice |
| Audio | TTS + post-mix | External mic required (lavalier/condenser) |
| Proof density | 1-2 numbers | 5+ numbers with named baselines |
| CTA | Follow / next short | GitHub + PyPI + subscribe + next |
| Title keyword | Single trending phrase | GREEN keyword + specific outcome |
| Thumbnail | Big face + bold text | Your real face + benchmark number + comparison |
| Series cadence | 2-3/week | 1-2/month |
| Production time | 2-4h per video | 8-16h per video (on-camera recording + edit) |

---

## Reference: When to use /shorts-script vs /long-script

| Content type | Duration | Skill |
|--------------|----------|-------|
| Hook-bait, single claim | <60s | `shorts-script` |
| Tutorial with proof + install | 8-15min | `long-script` |
| Series overview / multiple concepts | 10-15min | `long-script` |
| Single benchmark reveal | <60s Short + 10min longform pair | both |
| Paper implementation walkthrough | 12-15min | `long-script` |
| Quick announcement | <60s | `shorts-script` |
