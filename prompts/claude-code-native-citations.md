# Claude Code Prompt — Switch to Native Citations (Two-Pass Architecture)

## Goal

Refactor the recommendation generation to use Claude's native Citations API for evidence and reasoning, while keeping `tool_use` for the structured recommendation fields. This gives us guaranteed-accurate citations instead of the current fuzzy-match validator.

Read the official docs first: https://platform.claude.com/docs/en/build-with-claude/citations

## Context

Currently, `generate_recommendation()` in `backend/app/services/reasoner.py` makes a single `tool_use` call that returns everything — summary, reasoning chain, scenarios, suitability score, AND evidence citations — as one structured JSON blob. After that, `CitationValidator` does a fuzzy longest-common-substring match to check whether Claude's `content_snippet` actually appears in the source document. This is unreliable.

Claude's native Citations API guarantees that `cited_text` is extracted verbatim from the source document. But it's incompatible with structured outputs / `tool_use`. So we need two passes.

## What to build

### Pass 1 — Structured recommendation (keep tool_use, same as today)

- Keep using `tool_use` with `RECOMMENDATION_TOOL` for the structured fields: `summary`, `assumptions`, `scenarios`, `suitability_score`, `cost_disclosure`, `conflict_disclosure`.
- **Remove** `evidences` and `reasoning_chain` from the `RECOMMENDATION_TOOL` schema — these move to Pass 2.
- Update `recommendation.j2` to remove citation instructions (no longer needed here). This pass only handles analysis and structured output.

### Pass 2 — Evidence and reasoning with native citations

- Make a second Claude API call using the Citations API.
- Send each retrieved knowledge item as a `document` content block with `citations: {"enabled": true}`. Use `"type": "text"` source with `media_type: "text/plain"`. Put the knowledge item's content as `data`, its title as `title`, and metadata (category, source, tags, ID) as `context`.
- The user message should contain the recommendation summary from Pass 1, plus the client/case context, and ask Claude to:
  1. Write a step-by-step reasoning chain explaining how the recommendation was reached, citing the provided documents.
  2. List all evidence sources with exact quotes from the documents.
- Parse the response: Claude will return multiple text blocks, some with `citations` arrays. Each citation has `cited_text`, `document_index`, and either `start_char_index`/`end_char_index` (plain text) or `start_page_number`/`end_page_number` (PDF).
- Map `document_index` back to the knowledge item ID (based on the order you sent them).
- Create a Jinja2 template for the Pass 2 prompt (e.g., `evidence_analysis.j2`).

### Update the Recommendation model and storage

- Evidence entries should now store the native citation data: `cited_text` (the verbatim quote), `document_index`, `start_char_index`, `end_char_index`, and the resolved `knowledge_item_id`.
- Every evidence entry created from a native citation is `verified=True` by definition — the API guarantees it.
- The reasoning chain should reference citations by their knowledge item IDs (resolved from `document_index`).
- Create a new Alembic migration for any schema changes.

### Simplify or remove CitationValidator

- The fuzzy-match logic in `citation_validator.py` is no longer needed for Pass 2 evidence.
- Keep any logic that cleans orphaned `evidence_ids` from the reasoning chain (IDs referencing knowledge items that don't exist).
- If there's nothing left worth keeping, delete the file and remove imports.

### Update the recommendation endpoint and related endpoints

- `generate_recommendation()` and `refine_recommendation()` in `reasoner.py` should both use the two-pass flow.
- The audit entry should record that native citations were used (e.g., `"citation_method": "native"`).
- The meeting brief and document extraction flows do NOT need this change — leave them as `tool_use` only.

### Frontend evidence display

- Evidence cards already show verification status (green/amber/red). Native citations should all show as verified (green).
- If a citation includes `start_char_index`/`end_char_index`, display the `cited_text` as a blockquote. This is the exact verbatim text — no fuzzy matching.
- Update the `EvidenceResponse` interface in the frontend hooks if the API response shape changes.

## What NOT to do

- Don't change the meeting brief or document extraction flows.
- Don't remove the dev auth bypass.
- Don't change the database models beyond what's needed for citation fields.
- Don't break the existing frontend data layer (React Query hooks, API client).

## Verification

- Run `pytest` — all existing tests should pass (or be updated if they mock the old single-pass flow).
- Run `next build` — no frontend type errors.
- Generate a test recommendation and confirm evidence items have `verified=True` and contain `cited_text` from native citations.
