# Knowledge Documents

Drop PDF or TXT files here to include them in the knowledge base.

Each file needs a companion `.meta.json` file with the same base name:

    itp1-avtalet.pdf
    itp1-avtalet.meta.json

Meta format:
```json
{
  "title": "ITP1-avtalet — Premiebestämd tjänstepension",
  "category": "product_rule",
  "source": "Collectum — ITP1-avtalet 2024",
  "tags": ["ITP1", "premiebestämd", "collectum"]
}
```

Valid categories: product_rule, internal_policy, regulatory_requirement, playbook, precedent, faq, process_guide

Files are ingested automatically when running: `python -m scripts.seed`
