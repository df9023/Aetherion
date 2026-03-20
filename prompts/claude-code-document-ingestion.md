# Claude Code Prompt: Document Ingestion (Upload & Extract)

You are working on **Aetherion**, an AI-native decision workspace for Swedish pension advisory. Your job is to build the **Document Ingestion** feature. An advisor uploads a PDF (pensionsbesked, lönespecifikation, insurance policy) on a client's profile page, and the system extracts structured pension data from it using Claude, then lets the advisor review and apply the extracted data to the client profile.

This saves 20-30 minutes of manual data entry per case.

## Codebase orientation

Read these files to understand existing patterns:

### Backend
- `backend/app/services/reasoner.py` — Has Claude tool_use definitions (RECOMMENDATION_TOOL, MEETING_BRIEF_TOOL, etc.) and methods that call Claude with structured output. Follow the same tool_use pattern for document extraction.
- `backend/app/api/v1/endpoints/clients.py` — Has `PATCH /{client_id}` for updating client fields. The extraction endpoint lives here too.
- `backend/app/schemas/client.py` — `ClientUpdate` schema (all fields optional). The extracted data will be applied via this schema.
- `backend/app/models/client.py` — Client model with fields: name, date_of_birth, employment_status, employer_name, collective_agreement, annual_income, desired_retirement_age, risk_profile.
- `backend/app/models/base.py` — All enums (EmploymentStatus, CollectiveAgreement, RiskProfile, etc.).
- `backend/app/prompts/system.j2` — Swedish-language system prompt with full pension domain knowledge.

### Frontend
- `frontend/app/(dashboard)/clients/[id]/page.tsx` — Client detail page where the upload UI goes.
- `frontend/lib/hooks.ts` — React Query hooks pattern. Has `useClient`, `useCreateClient`, etc.
- `frontend/lib/api.ts` — `apiFetch` helper with dev auth headers.
- Design: white cards with `rounded-xl border border-slate-200/60`, sky-500 buttons, Lucide icons.

## What to build

### Backend

1. **Claude tool definition** for document extraction
   - Define a tool schema that extracts pension-relevant fields from uploaded documents.
   - Fields to extract: client name, date of birth, employer, collective agreement type, annual/monthly income, pension provider, fund allocations (fund name + percentage + fee), total fees, survivor protection status, any pension holdings/capital amounts, and a free-text "other observations" field for anything else notable.
   - Each extracted field should include a `confidence` score (0-1) so the advisor knows what to double-check.

2. **Jinja2 prompt template** (`backend/app/prompts/document_extraction.j2`)
   - Swedish language. Instructs Claude to carefully extract pension data from the provided document text.
   - Should handle different document types: pensionsbesked (pension statements from Collectum, Alecta, SPP, etc.), lönespecifikationer (pay slips), insurance policy documents.
   - Tells Claude to flag uncertain extractions and note what type of document it appears to be.

3. **ReasonerService method** (`extract_document_data`)
   - Receives document content (text extracted from PDF) and optionally the raw PDF bytes for Claude vision.
   - Calls Claude with the extraction tool.
   - Returns the structured extraction result.

4. **API endpoint** (`POST /api/v1/clients/{client_id}/ingest-document`)
   - Accepts a file upload (multipart/form-data with a PDF file).
   - Extracts text from the PDF (use `PyPDF2` or `pdfplumber` — add to requirements.txt).
   - Calls ReasonerService to extract structured data.
   - Returns the extracted data for advisor review (does NOT auto-update the client — the advisor confirms first).
   - Org-scoped: verify client belongs to the user's organization.
   - Returns 503 if ANTHROPIC_API_KEY not set.

5. **API endpoint** (`POST /api/v1/clients/{client_id}/apply-extraction`)
   - Receives the confirmed extracted fields (subset chosen by advisor).
   - Updates the client via the existing update logic.
   - Creates an audit entry.
   - This is a simple thin endpoint — it just calls the existing PATCH logic with the confirmed data.

### Frontend

6. **Upload and extraction hook** in `hooks.ts`
   - `useIngestDocument(clientId)` — mutation that uploads a file, returns extracted data.
   - `useApplyExtraction(clientId)` — mutation that sends confirmed fields, returns updated client.
   - Note: the upload needs `multipart/form-data`, not JSON. Use `FormData` and don't set Content-Type header (browser sets it with boundary).

7. **Document ingestion component** (`components/document-ingestion.tsx`)
   - UI flow with 3 states:

   **State 1 — Upload**: A dropzone/file picker card on the client detail page. Accepts PDF files. Shows a dashed border upload area with an `Upload` icon and "Upload pension document" text. Drag-and-drop or click to select.

   **State 2 — Extracting**: Loading state with progress indicators while Claude processes the document.

   **State 3 — Review**: Shows all extracted fields in a two-column layout. Each field shows:
   - Field name (e.g., "Collective Agreement")
   - Extracted value
   - Confidence indicator (green checkmark for >0.8, amber warning for 0.5-0.8, red flag for <0.5)
   - Checkbox to include/exclude this field from the update
   - If the field differs from the current client value, highlight it (show current → extracted)

   At the bottom: "Apply Selected Fields" button (sky-500) and "Cancel" button.
   On success: toast, refetch client data, reset to upload state.

8. **Integration into client detail page**
   - Add the document ingestion component as a new card section between the "Details" card and the "Linked Cases" card.
   - Section header: "Document Ingestion" with an `Upload` icon.

## Constraints

- Use `claude-sonnet-4-20250514` for extraction (same model as all other Claude calls).
- PDF text extraction should use a lightweight library (PyPDF2 or pdfplumber). Add it to `backend/requirements.txt`.
- The upload endpoint uses `File` from FastAPI for file handling, not JSON body.
- Don't persist the uploaded PDF — just extract data from it and discard. No new database models needed.
- The extraction result is ephemeral — returned to the frontend for review, not stored in DB.
- The actual client update uses the existing `PATCH /clients/{id}` logic or a thin wrapper.
- Run `npx tsc --noEmit` from `frontend/` to verify no TypeScript errors.
