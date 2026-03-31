# Drident — Next Capabilities

*Product specification for three new core capabilities. Written as a PM brief — what they do, what changes for the user, why they matter.*

---

## 1. Regulatory Pulse

**One line:** Drident watches the regulatory landscape so the firm doesn't have to — and tells advisors exactly which of their cases are affected when something changes.

### The problem today

Regulatory change in Swedish pension is constant but unpredictable. FI publishes new guidance. Collective agreements get renegotiated (ITP is currently under active revision). Tax rules shift with every budget. Product terms change when providers update their offerings.

Today, staying current is a manual, human process. A senior advisor reads FI circulars, interprets them, and maybe sends an email to the team. There's no structured way to know whether a new rule invalidates a recommendation you gave three weeks ago. Firms discover compliance gaps reactively — during audits, during complaints, or when a junior advisor happens to ask the right question.

This is the quiet risk in every advisory firm: not that advisors are incompetent, but that the ground shifted and nobody noticed.

### What Regulatory Pulse does

Regulatory Pulse maintains a living model of the rules that govern every active case. It doesn't just store documents — it understands the dependency structure between regulations, products, collective agreements, and client situations.

When something changes in the regulatory environment, Pulse traces the impact through the firm's active caseload and surfaces exactly what's affected and why.

**Day-to-day experience for the advisor:**

The advisor opens Drident on a Monday morning. There's a notification: *"FI published FFFS 2026:4 on Friday — updated suitability documentation requirements for salary exchange recommendations. 6 of your active cases include salary exchange. 2 of those cases have recommendations in review status that reference the old requirements. Here's what changed and what needs updating in each case."*

Each affected case links directly to a diff — here's the old rule, here's the new rule, here's the specific section of the recommendation that needs attention.

The advisor doesn't need to read the circular. They don't need to figure out which cases might be affected. They don't even need to understand the new rule from scratch — Pulse explains the change in context of each specific case.

**Day-to-day experience for the compliance officer:**

The compliance officer sees a firm-wide view: which regulatory changes have occurred, which cases across all advisors are affected, which have been resolved and which are still open. They can generate a report showing the firm's response time to regulatory changes — useful for FI inspections and internal governance.

**What this looks like in the product:**

- A "Regulatory Feed" in the dashboard that shows recent changes with impact assessments
- Per-case impact flags that appear when a regulatory change touches an active case
- A "Compliance Health" view showing how many cases are current vs. how many have unresolved regulatory impacts
- Automated alerts (email or in-app) when high-severity changes affect cases in review or recently completed

**What this does NOT do:**

Pulse does not automatically update recommendations. The advisor always reviews and decides. The system tells you what changed and where — the human decides what to do about it. This preserves the human-in-the-loop requirement and keeps Drident firmly in "decision support" territory under the EU AI Act.

### Why this matters for the firm

- **Risk reduction.** The biggest compliance risk in advisory isn't doing something wrong — it's not noticing that the rules changed. Pulse eliminates this category of risk.
- **Advisor productivity.** Instead of every advisor independently tracking regulatory changes (or more realistically, not tracking them), the system does it once for the whole firm.
- **Audit readiness.** If FI asks "how did your firm respond to FFFS 2026:4?", the compliance officer can show exactly when the change was detected, which cases were affected, and the resolution timeline.
- **Client trust.** Advisors can proactively reach out to clients when something changes that affects them — "Hi Anna, new guidance came out that affects your salary exchange setup. Let's schedule a review." That's the kind of proactive service that builds loyalty.

### What makes this hard to copy

Any firm can set up Google Alerts for FI publications. What they can't easily replicate is the connection between regulatory changes and live case data. Pulse's value comes from knowing that *this specific rule* affects *these specific cases* because of *these specific facts in each case*. That requires the case data, the regulatory model, and the reasoning to connect them — which is exactly what Drident has.

---

## 2. Reasoning Trail

**One line:** The AI's step-by-step reasoning becomes the compliance documentation — not a summary after the fact, but the actual auditable process record.

### The problem today

IDD requires advisory firms to demonstrate that a proper suitability assessment was conducted. Not just "we recommended product X" — but that the advisor gathered the client's needs, analyzed their situation, compared alternatives, assessed suitability, and arrived at a justified recommendation through a structured process.

In practice, this process happens in the advisor's head (or in a conversation with a colleague), and then gets documented after the fact. The documentation describes a process that already happened — it's a narrative, not a record.

This creates two problems. First, the documentation often doesn't fully reflect the actual reasoning — things get simplified, edge cases get glossed over, the messy reality of "I also considered X but rejected it because Y" doesn't make it into the clean document. Second, the documentation is labor-intensive to produce — advisors spend significant time writing up justifications for decisions they already made.

### What Reasoning Trail does

When Drident generates a recommendation, the AI doesn't just produce an output — it produces a visible, step-by-step reasoning chain that walks through the entire suitability assessment process. This chain is captured, structured, and stored as the compliance record for that case.

**What the advisor sees:**

When the advisor hits "Generate Recommendation," instead of (or before) getting a finished document, they see the reasoning unfold:

> **Step 1 — Client situation analysis**
> Anna Johansson, born 1985, employed at McKinsey Stockholm. Current income: 78,000 SEK/month, exceeding 7.5 IBB (currently 57,187 SEK/month). Collective agreement: ITP1. This means her pension contributions above the income ceiling are limited to the ITP1 rate of 30%, creating a potential coverage gap.
>
> **Step 2 — Needs identification**
> Based on the intake data, Anna has expressed concern about retirement income adequacy. Her income above the ceiling is significant (20,813 SEK/month). Under ITP1, the employer contributes 30% above the ceiling, but her total projected pension replacement rate at age 65 is approximately 52% of current income — below her stated target of 70%.
>
> **Step 3 — Option evaluation**
> Three options assessed:
> (a) Salary exchange above the income ceiling — additional employer pension contributions in exchange for gross salary reduction. Tax-efficient for Anna's income level. *However:* reduces sick pay and parental benefit base. Must verify employer willingness.
> (b) Private pension savings (IPS) — no longer tax-deductible since 2016. Limited benefit.
> (c) ISK-based long-term savings — tax-efficient, liquid, no lock-in. Doesn't provide the same employer contribution benefit as salary exchange.
>
> **Step 4 — Suitability assessment**
> Salary exchange is assessed as suitable based on: income significantly above ceiling (low risk of falling below), stable employment, moderate risk profile (compatible with available fund selection), no planned major life changes. Risk factors noted: salary exchange reduces SGI, which could impact parental leave compensation. Anna has no children and has stated no near-term plans — flagged for re-review if circumstances change.
>
> **Step 5 — Product matching**
> [Continues through provider selection, cost comparison, etc.]

Each step cites the specific regulations, data points, and policies it relies on. The calculations referenced (income ceiling, contribution rates, replacement ratios) are computed by the deterministic engine — the reasoning chain explains them, it doesn't invent them.

**What happens with the reasoning chain:**

- The chain is **stored as a first-class object** attached to the case — not buried in a log file, but accessible alongside the recommendation document
- The advisor can **annotate the chain** — "I discussed this with Anna and she confirmed no plans for children in the next 3 years" — adding human context to the AI reasoning
- The chain feeds directly into the **recommendation document** — the IDD-compliant output references the exact reasoning steps, so the document and the process are consistent by construction
- The compliance officer can **review the chain** alongside the final recommendation to verify the process was sound

**What the advisor's workflow becomes:**

Instead of: generate recommendation → read it → separately write up the justification → hope they match

Now: review the reasoning chain → annotate where needed → approve → the document is generated from the chain

The advisor's job shifts from "write the compliance documentation" to "verify and enrich the reasoning." That's faster *and* produces better documentation.

### Why this matters for the firm

- **Documentation quality goes up.** The reasoning trail is more thorough than what an advisor would write manually — it considers every step, every alternative, every risk factor. Compliance officers get richer, more structured records.
- **Advisor time goes down.** The most tedious part of the job — writing up the justification — is replaced by reviewing and annotating a pre-built chain. Most of the advisor's expertise goes into the 20% that needs human judgment, not the 80% that's structured process.
- **Audit defensibility.** If a recommendation is ever challenged, the firm can show the exact reasoning chain — what was considered, what was rejected and why, what data informed each step. This is qualitatively different from a post-hoc narrative.
- **Training tool.** Junior advisors can study the reasoning chains of complex cases to understand how senior-level analysis works. The chain makes expert reasoning visible and learnable.

### The subtle advantage

The more thorough the reasoning, the better the compliance documentation. This means the "cost" of AI inference (longer reasoning = more tokens = more compute) directly maps to "value" for the firm (better audit trail). Most AI products try to minimize inference cost. Reasoning Trail turns it into the product.

---

## 3. Firm Memory

**One line:** Drident learns how *this specific firm* advises — accumulating institutional judgment from every case into a knowledge layer that makes every future recommendation smarter.

### The problem today

Every advisory firm has institutional knowledge that exists only in the heads of senior people. It's the kind of judgment that takes years to develop:

- "For manufacturing clients with high overtime, always double-check that the salary exchange doesn't dip them below the ceiling in low-production months."
- "We've had problems with Provider X's fund selection for clients over 55 — the age-based funds shift too aggressively."
- "When a client at a Big Four firm asks about salary exchange, remember that the employer typically only approves it above the ceiling — check with HR first."

This knowledge is incredibly valuable. It's what distinguishes a good advisory firm from a generic one. But it doesn't scale — it lives in individual heads, it gets lost when people leave, it's shared inconsistently through hallway conversations and lunch-and-learns.

Junior advisors take years to absorb it. When a senior advisor retires, some of it leaves with them.

### What Firm Memory does

Firm Memory is a knowledge layer that sits alongside Drident's regulatory knowledge base. While the regulatory KB contains universal knowledge (pension rules, IDD requirements, FI guidance), Firm Memory contains *this firm's* specific patterns, preferences, and accumulated judgment.

It builds over time from two sources:

**1. Pattern extraction from case history**

As the firm completes cases through Drident, the system identifies recurring patterns in how advisors handle specific situations. Not individual client data — but the generalizable judgment calls.

Example: Over 15 cases involving ITP1 clients above the income ceiling, the firm's advisors consistently flag the SGI impact for clients under 40 as a significant risk factor but treat it as minor for clients over 50. Firm Memory captures this as a pattern: *"This firm considers SGI impact from salary exchange to be age-dependent — higher concern for younger clients due to longer exposure to reduced parental/sick benefit base."*

These patterns are surfaced to the advisor as contextual suggestions when working on similar cases. Not as rules — as "here's how your firm has typically handled this."

**2. Explicit advisor input**

Advisors can directly teach the system. After completing a case, they can flag insights:

- "Important: McKinsey HR requires a minimum 3-month notice period before starting salary exchange. Build this into timeline recommendations for McKinsey employees."
- "Lesson learned: for clients in this income bracket, always present the ISK alternative alongside salary exchange — even when salary exchange is clearly better. It builds client trust when they see you considered alternatives."

These inputs are tagged, stored, and surfaced in future relevant cases. When the next advisor opens a McKinsey employee case, they see the notice period note — without having to discover it themselves.

**What the advisor experiences:**

When working on a case, the advisor sees a "Firm Insights" panel alongside the AI recommendation. It might show:

> **Relevant to this case:**
>
> *From case history (12 similar cases):* For ITP1 clients with income above 1.5x the ceiling, this firm typically recommends salary exchange with a 60/40 split between traditional and fund insurance. The reasoning is usually related to the client's proximity to retirement and the firm's risk philosophy.
>
> *Advisor note (Johan, 2025-11):* "Skandia has updated their salary exchange process — new employer agreement template required as of January 2026. Check with the employer's HR before generating documents."
>
> *Pattern detected:* Clients in the consulting sector referred by McKinsey HR tend to have high financial literacy. Past cases show shorter explanation sections in recommendations and more detail on fund selection rationale.

The advisor can accept, dismiss, or modify these insights. Dismissals feed back into the system — if multiple advisors dismiss a pattern, it loses confidence and eventually fades.

**What this looks like for firm leadership:**

- A "Firm Knowledge" section where partners and senior advisors can review, curate, and approve the patterns the system has identified
- The ability to promote certain patterns to firm-wide policies ("we always do X in situation Y") or flag them as optional preferences
- Visibility into what institutional knowledge exists and where gaps might be — "we have strong patterns for ITP1 salary exchange but almost no accumulated judgment on KAP-KL cases"

### Why this matters for the firm

- **Junior advisors get productive faster.** Instead of spending 2-3 years absorbing institutional knowledge through osmosis, they have it available from day one. They still need judgment and experience — but they start from a much higher baseline.
- **Consistency across the firm.** When five advisors handle the same type of case, the recommendations should reflect the firm's philosophy — not five different personal styles. Firm Memory creates convergence without rigid rules.
- **Knowledge retention.** When a senior advisor leaves, their accumulated judgment doesn't walk out the door. The most valuable patterns from their cases are already captured in the system.
- **Competitive differentiation.** Over time, a firm's Memory becomes a genuine asset — years of refined judgment encoded into the advisory process. This is proprietary to each firm and makes Drident increasingly valuable the longer they use it.

### The lock-in dynamic (honest version)

Let's be transparent: Firm Memory creates switching costs. A firm that has spent two years building up its knowledge layer would lose that accumulated judgment if they moved to a different tool. This is good for Drident's business, but it's only ethical if the value is real. The switching cost should come from "this is genuinely useful and I'd miss it" — not from data hostage-taking.

To that end: firms should be able to export their Firm Memory at any time in a structured format. The lock-in should come from the system's ability to use that knowledge, not from trapping the knowledge itself.

### How it builds over time

This is not a launch-day feature in its full form. The rollout is staged:

**Phase 1 — Advisor notes.** Simple: advisors can attach notes and insights to case types, clients, and products. These are stored, tagged, and surfaced in relevant future cases. No ML needed — just structured institutional memory.

**Phase 2 — Pattern detection.** The system begins identifying recurring patterns across completed cases. These are surfaced as suggestions that advisors validate or dismiss. Confidence builds with volume.

**Phase 3 — Recommendation integration.** Validated firm patterns are integrated into the recommendation engine itself. The AI doesn't just use regulatory knowledge — it reasons with the firm's accumulated judgment as additional context. The output reflects "how pension regulations work" *and* "how this firm thinks about it."

---

## How the three capabilities connect

These aren't three separate features — they form a reinforcing system:

**Regulatory Pulse** ensures the firm's knowledge base is always current. When a rule changes, it doesn't just flag cases — it also checks whether any Firm Memory patterns were based on the old rule and flags those for review.

**Reasoning Trail** produces the structured reasoning chains that Firm Memory learns from. Without visible reasoning, there's nothing to extract patterns from. The trail is both the compliance artifact *and* the training data for the firm's knowledge layer.

**Firm Memory** makes Reasoning Trail's output better over time. As the firm accumulates judgment, the reasoning chains become more nuanced — they don't just follow the regulations, they reflect the firm's specific expertise and client approach.

Together, they turn Drident from a tool that generates documents into a system that **accumulates and applies institutional intelligence** — getting better at advising the longer a firm uses it.

---

*The advisor is still the expert. Drident just makes sure their expertise is captured, their knowledge is current, and their reasoning is visible.*
