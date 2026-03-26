# Task: Verify Frontend UI/UX Overhaul

The frontend was just overhauled for usability — Swedish labels, larger text, bigger buttons, responsive layout, removed fake elements. Your job is to verify everything works correctly by running the app and checking each page in the browser.

## Setup

1. Make sure the backend is running: `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload`
2. Make sure the frontend is running: `cd frontend && npm run dev`
3. Open `http://localhost:3000` in the browser

## What to verify

### 1. Sidebar
- [ ] Nav items read: **Ärenden**, **Klienter**, **Kunskapsbas**
- [ ] Badge counts show next to each nav item
- [ ] User area shows name, "Rådgivare" role, and logout icon (not Settings)
- [ ] Active nav item has sky-blue highlight
- [ ] No "Workspace" label above nav items

### 2. Top bar
- [ ] Breadcrumbs show in Swedish (e.g. "Ärenden" not "Cases")
- [ ] No fake search bar or ⌘K shortcut
- [ ] No notification bell
- [ ] SPP badge shows on the right
- [ ] No avatar circle with "EE" — just the SPP badge

### 3. Cases list page (`/cases`)
- [ ] Page title: "Ärenden"
- [ ] Button: "Nytt ärende"
- [ ] Stats bar shows Swedish labels: "Aktiva ärenden", "Väntar granskning", "Klienter", "Avslutade"
- [ ] Status filter pills in Swedish: "Alla", "Utkast", "Under arbete", etc.
- [ ] Type filter pills in Swedish: "Pensionsöversyn", "Löneväxling", etc.
- [ ] Search placeholder: "Sök ärenden..."
- [ ] Case cards show actual client name in footer (not "Maria Lindqvist")
- [ ] Time ago in Swedish: "Idag", "Igår", "X dagar sedan"
- [ ] Status and type badges on each card are in Swedish

### 4. Case detail page (`/cases/[id]`)
- [ ] Breadcrumb: "Ärenden > [case title]"
- [ ] Case title is noticeably larger (`text-lg`)
- [ ] Status dropdown opens and **closes when clicking outside**
- [ ] Status options are in Swedish
- [ ] Case type badge is in Swedish

### 5. Client info card (on case detail)
- [ ] Header: "Klientinformation"
- [ ] Labels in Swedish: Namn, Ålder, Arbetsgivare, Kollektivavtal, Månadsinkomst, Riskprofil, Önskad pensionsålder, Anställningsstatus
- [ ] Risk profile shows Swedish labels (Låg/Medel/Hög)
- [ ] Age shows "X år"

### 6. Meeting prep card (on case detail)
- [ ] Header: "Mötesförberedelse"
- [ ] Empty state: "Inget mötesunderlag förberett" / "Förbered möte"
- [ ] Click "Förbered möte" — loading steps show Swedish text
- [ ] Generated brief shows Swedish section headers: Klientöversikt, Pensionssituation, Nyckelfrågor, Scenarion, Samtalspunkter, Öppna frågor, Agenda
- [ ] Severity badges show "Hög"/"Medel"/"Låg" instead of "high"/"medium"/"low"
- [ ] Regenerate button: "Generera nytt underlag"

### 7. AI recommendation card (on case detail)
- [ ] Header: "AI-rekommendation"
- [ ] Empty state: "Ingen rekommendation genererad" / "Generera rekommendation"
- [ ] Loading steps in Swedish
- [ ] Score label: "Lämplighetspoäng" with percentage (e.g. "85%")
- [ ] Suitability text in Swedish: "Hög lämplighet...", "Medel lämplighet...", "Låg lämplighet..."
- [ ] Section headers: Sammanfattning, Resonemangskedja, Antaganden, Scenarion
- [ ] Evidence section: "Underlag (X källor)" — **collapsed by default**, click to expand
- [ ] Evidence badges show Swedish: "Verifierad", "Delvis verifierad", "Ej verifierad"
- [ ] Source type labels in Swedish (Produktregel, Reglering, etc.)
- [ ] Buttons: "Generera dokumentation", "Ladda ner DOCX", "Ny version"
- [ ] All text is at least `text-xs` (12px) — no tiny unreadable text

### 8. Audit trail card (on case detail)
- [ ] Header: "Granskningslogg"
- [ ] Actions in Swedish: "Ärende skapat", "Rekommendation genererad av AI", etc.
- [ ] Dates formatted with Swedish locale (`sv-SE`)

### 9. Knowledge base card (case detail sidebar)
- [ ] Header: "Kunskapsbas"
- [ ] Search placeholder: "Sök i kunskapsbasen..."
- [ ] Empty state: "Skriv för att söka i kunskapsbasen..."

### 10. Responsive layout (case detail)
- [ ] On wide screen: two-column layout (main + sidebar)
- [ ] Resize browser to narrow width: columns stack vertically

### 11. Clients page (`/clients`)
- [ ] Title: "Klienter"
- [ ] Button: "Ny klient"
- [ ] Search: "Sök klienter..."
- [ ] Age shows "X år"
- [ ] Income shows "kr/mån"
- [ ] Risk badges: "Låg risk", "Medel risk", "Hög risk"

### 12. Client detail page (`/clients/[id]`)
- [ ] Breadcrumb: "Klienter > [client name]"
- [ ] Document section header: "Ladda upp dokument" (not "Document Ingestion")
- [ ] New case button: "Nytt ärende"

### 13. Knowledge page (`/knowledge`)
- [ ] Title: "Kunskapsbas"
- [ ] Button: "Ladda upp dokument"
- [ ] Search: "Sök i kunskapsbasen..."
- [ ] Category filters in Swedish: "Alla", "Produktregler", "Intern policy", etc.
- [ ] "Visa mer" / "Visa mindre" toggle text
- [ ] Upload dialog: Swedish labels throughout

### 14. General
- [ ] No `text-[10px]` or `text-[11px]` anywhere — smallest text is `text-xs` (12px)
- [ ] All buttons have adequate size (at least `py-2` padding)
- [ ] No English text remaining in the UI (except brand name "Aetherion" and org name "SPP")
- [ ] No console errors in browser DevTools

## If issues are found

Fix them directly. For each fix, explain what was wrong and what you changed. After fixing, re-verify the affected section.
