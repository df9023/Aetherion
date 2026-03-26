# Seed Knowledge Base from Document Folder

## Context

We have a working ingestion pipeline (chunker + embeddings + storage). We want the seed script to automatically ingest PDF documents from a local folder so the knowledge base is persistent and reproducible across re-seeds.

Read `backend/scripts/seed.py` for the current seed logic. Read `backend/app/services/chunker.py` for ChunkerService. Read `backend/app/services/memory.py` for MemoryService.

## 1. Create the knowledge documents folder

Create `backend/data/knowledge/` with a `README.md` explaining:

```markdown
# Knowledge Documents

Drop PDF files here to include them in the knowledge base.

Each PDF needs a companion `.meta.json` file with the same base name:

    itp1-avtalet.pdf
    itp1-avtalet.meta.json

Meta format:
{
  "title": "ITP1-avtalet — Premiebestämd tjänstepension",
  "category": "product_rule",
  "source": "Collectum — ITP1-avtalet 2024",
  "tags": ["ITP1", "premiebestämd", "collectum"]
}

Valid categories: product_rule, internal_policy, regulatory_requirement, playbook, precedent, faq, process_guide

Files are ingested automatically when running: python scripts/seed.py
```

Add `backend/data/knowledge/*.pdf` to `.gitignore` — PDFs are real documents that shouldn't be in the repo. Keep `.meta.json` files and `README.md` tracked.

## 2. Update the seed script

Add a function to `backend/scripts/seed.py`:

```python
async def seed_knowledge_documents(db: AsyncSession, embed_fn, org_id, user_id) -> int:
    """Ingest PDFs from backend/data/knowledge/ into knowledge items."""
```

This function should:

1. Scan `backend/data/knowledge/` for `.meta.json` files
2. For each meta file, find the matching `.pdf` file (same base name)
3. Skip if no matching PDF found (just warn)
4. Extract text using pdfplumber
5. Chunk using `ChunkerService`
6. For each chunk:
   - Generate a **deterministic ID**: `uuid5(NAMESPACE_DNS, f"aetherion.seed.doc.{filename}.chunk.{index}")`
   - Create a `KnowledgeItem` with:
     - `title`: `"{meta.title} — {section_heading or 'Del ' + str(index+1)}"`
     - `content`: chunk text
     - `category`, `source`, `tags` from the meta file
     - `embedding`: from embed_fn
     - `source_location`: character offsets from chunker
     - `organization_id`: org_id
     - `created_by`: user_id
7. Return count of items created

**Idempotency**: Before inserting chunks from a file, delete any existing knowledge items whose IDs match the deterministic IDs for that file. This way re-seeding replaces document-based items cleanly.

Call this in `seed()` after the existing hardcoded knowledge items, inside the same DB session:

```python
print("Seeding knowledge from documents...")
doc_count = await seed_knowledge_documents(db, embed, ORG_ID, USER_ADMIN_ID)
```

Update the print summary:
```
Knowledge:     6 base items + {doc_count} document chunks
```

## 3. Also support .txt files

Some documents might be plain text instead of PDF. If the matching file is `.txt` instead of `.pdf`, read it directly instead of using pdfplumber. Check for both extensions.

## Verification

1. Place any PDF + meta.json pair in `backend/data/knowledge/`
2. Run `python scripts/seed.py`
3. Verify the knowledge items appear in the frontend knowledge base page
4. Search for a term from the document — verify it returns results
5. Re-run `python scripts/seed.py` — verify no duplicates (idempotent)
