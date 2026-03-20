# Claude Code Prompt: Meeting Brief Generation

You are working on **Aetherion**, an AI-native decision workspace for Swedish pension advisory. The core product loop (generate recommendation → compliance docs → download) already works end-to-end. Your job is to build the **Meeting Brief Generation** feature.

An advisor clicks "Prepare Meeting" on a case and within seconds gets a structured meeting preparation document covering the client's full pension situation, key issues, pre-modeled scenarios, talking points, and a suggested agenda.

## Codebase orientation

Before writing any code, read these files to understand the existing patterns:

### Backend patterns (follow these exactly)
- `backend/app/services/reasoner.py` — Has `RECOMMENDATION_TOOL` and `CLIENT_EXPLANATION_TOOL` as Claude tool_use definitions, plus `generate_recommendation()` and `generate_client_explanation()` methods. Your meeting brief tool and method must follow this same pattern.
- `backend/app/prompts/system.j2` — Swedish-language system prompt for all Claude calls. Already covers pension domain knowledge.
- `backend/app/prompts/recommendation.j2` — Example of a Jinja2 prompt template. Your meeting brief template goes in the same directory.
- `backend/app/api/v1/endpoints/cases.py` — Has `generate_recommendation` endpoint that loads case + client, retrieves knowledge via MemoryService RAG, calls ReasonerService. Your endpoint follows this same flow.
- `backend/app/services/memory.py` — `MemoryService` with `get_relevant_knowledge()` for RAG retrieval.

### Frontend patterns (follow these exactly)
- `frontend/app/(dashboard)/cases/[id]/page.tsx` — The case detail page where you'll add the "Prepare Meeting" section.
- `frontend/lib/hooks.ts` — All API hooks use `useQuery`/`useMutation` from React Query with `apiFetch` from `lib/api.ts`.
- `frontend/lib/labels.ts` — Label/style maps.
- Design system: dark sidebar, white cards (`rounded-xl border border-slate-200/60 bg-white p-6 shadow-sm`), sky-500 primary buttons, Inter font, Lucide icons.

## What to build

### Backend

1. **Claude tool definition** (`MEETING_BRIEF_TOOL`) in `reasoner.py`
   - Structured output with these sections: client overview, pension situation (across all three Swedish pension pillars: allmän, tjänste, privat), key issues with severity levels, pre-modeled scenarios with trade-offs, talking points, open questions for the client, and a suggested meeting agenda with time estimates.
   - Follow the exact `input_schema` pattern of the existing tools.

2. **Jinja2 prompt template** (`backend/app/prompts/meeting_brief.j2`)
   - Swedish language, instructs Claude to analyze the client's pension situation step by step.
   - Receives: case_type, context (client + case data), knowledge_items, optional additional_context.
   - Tells Claude to consider: active fund choices, fee levels, survivor/disability protection gaps, salary exchange opportunities, risk alignment, and projected outcomes.

3. **ReasonerService method** (`generate_meeting_brief`)
   - Same pattern as `generate_recommendation()`: render template, call Claude with tool_use, extract tool input.

4. **API endpoint** (`POST /api/v1/cases/{case_id}/generate-brief`)
   - Same flow as `generate_recommendation`: load case (org-scoped), load client, build context dict, retrieve knowledge via MemoryService RAG, call ReasonerService, create audit entry, return the structured brief as JSON.
   - Request body: `{ additional_context?: string }`
   - Returns: the raw tool output (the structured brief dict).

### Frontend

5. **React Query hook** (`useGenerateMeetingBrief`) in `hooks.ts`
   - Mutation that POSTs to `/cases/{caseId}/generate-brief`.
   - TypeScript interface for the response matching the tool schema.

6. **Meeting Brief Viewer component** (`components/meeting-brief-viewer.tsx`)
   - Renders all sections of the brief with appropriate styling.
   - Pension situation: show the three pillars with colored left borders (blue for allmän, green for tjänste, violet for privat).
   - Key issues: severity indicators (red/amber/slate badges and left borders).
   - Scenarios: card grid with projected outcomes and trade-offs (match existing scenario cards in the recommendation viewer).
   - Talking points: numbered list.
   - Open questions: list with distinct styling.
   - Agenda: timeline with duration and notes, total time shown.

7. **Integration into case detail page** (`cases/[id]/page.tsx`)
   - Add a "Prepare Meeting" card between the Case Header and Client Information sections.
   - Three states: empty (with CTA button), generating (animated progress), brief exists (renders MeetingBriefViewer).
   - "Regenerate Brief" button after brief is shown.
   - Toast on success/error.

8. **Audit label** — Add appropriate label in `labels.ts` for the brief generation audit event.

## Constraints

- Use `claude-sonnet-4-20250514` (same model as existing calls).
- All prompt templates in Swedish. Tool schema descriptions can be English.
- Endpoint returns 503 if `ANTHROPIC_API_KEY` not configured.
- No new database models or migrations — the brief is returned directly (not persisted).
- Don't modify existing components beyond adding the new section to the case detail page.
- Run `npx tsc --noEmit` from `frontend/` to verify no TypeScript errors.
