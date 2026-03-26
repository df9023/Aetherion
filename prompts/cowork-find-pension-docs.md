# Find Swedish Pension Knowledge Base Documents

## What I need

I'm building Aetherion, an AI-powered decision workspace for Swedish pension advisors. I need to populate a knowledge base with real, publicly available Swedish pension documents that advisors reference daily.

Help me find and list downloadable PDFs (or web pages I can save as PDF) for each category below. For each document, give me:
- **Title** (Swedish)
- **URL** to download or view
- **Category** (one of: product_rule, internal_policy, regulatory_requirement, playbook, process_guide)
- **Source** (organization that published it)
- **Tags** (3-5 relevant keywords)
- **Why it matters** (one sentence on why an advisor needs this)

## Documents I need

### Regulatory (Finansinspektionen / EU)
1. **FFFS 2018:10** — FI's implementation of IDD (Insurance Distribution Directive). The core regulation governing pension advisory in Sweden. Suitability assessment, needs analysis, documentation requirements.
2. **FFFS 2007:16** — FI's regulation on investment advice. Still referenced alongside IDD.
3. **IDD directive summary** — the EU directive itself, in Swedish or English.
4. Any FI guidance or FAQ documents about advisory documentation requirements.

### Collective agreements (Collectum / Fora)
5. **ITP1 plan rules** — the full ITP1 agreement (premiums, fund selection, Collectum's role, fees, survivor protection).
6. **ITP2 plan rules** — the full ITP2 agreement (defined benefit formula, Alecta, ITPK, family pension).
7. **SAF-LO** collective pension agreement — for blue-collar workers.
8. **KAP-KL / AKAP-KL** — municipal/public sector pension agreements.

### Product documentation
9. **Collectum fund lineup** — the current list of available funds with fees.
10. **Alecta product documentation** — ITP2 defined benefit details.
11. **AMF product documentation** — default fund options, fees.
12. **SPP product sheets** — any publicly available pension product info.

### Pension system overview
13. **Pensionsmyndigheten** — official guide to the Swedish pension system (tre pelare / three pillars).
14. **Orange envelope (orange kuvertet)** explanation — how to read the annual pension statement.
15. **Skatteverket** — pension taxation rules, salary exchange tax implications.

### Advisory methodology
16. Any publicly available risk profiling methodology (Swedish financial advisory context).
17. Salary exchange (löneväxling) calculation guides or examples.
18. Survivor protection (efterlevandeskydd) comparison guides.

## Format

For each document you find, format it like this so I can create the meta.json files:

```json
{
  "filename": "suggested-filename.pdf",
  "title": "Document Title in Swedish",
  "category": "regulatory_requirement",
  "source": "Finansinspektionen — FFFS 2018:10",
  "tags": ["IDD", "compliance", "behovsanalys"],
  "url": "https://...",
  "notes": "Any notes about downloading or format"
}
```

## Important
- Only publicly available documents (no paywalled content)
- Swedish language preferred, English acceptable for EU-level documents
- If a document isn't available as PDF but exists as a web page, note that I can save it as PDF
- If you're not sure a URL is still valid, say so — I'll verify manually
- Prioritize: the top 10 most important documents an ITP1/ITP2 pension advisor would reference weekly
