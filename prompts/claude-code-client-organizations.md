# Task: Add Client Organizations (employer companies the advisor manages)

Read `CLAUDE.md` for project context. Read the existing models, schemas, endpoints, and frontend pages to understand the patterns.

## Concept

An advisor at SPP (the advisory firm / tenant) is responsible for **client organizations** — the companies whose employees they advise on pension matters. For example: McKinsey Stockholm, Volvo Göteborg, Scandic Hotels.

Currently, `employer_name` is a free-text string on the `Client` model. We're promoting this to a proper entity so advisors can:
- See all their client organizations at a glance
- Click into an organization and see all its employees (clients) and their cases
- Set the collective agreement at the org level (inherited by clients)
- Store HR contact info for each company

```
SPP (tenant / Organization)
  └── Advisor: Erik
        ├── McKinsey Stockholm (ClientOrganization)
        │     ├── Anna Johansson (Client)
        │     └── Lars Eriksson (Client)
        ├── Volvo Göteborg (ClientOrganization)
        │     └── Maria Lindqvist (Client)
        └── ...
```

**Important naming:** The existing `Organization` model is the advisory **firm** (tenant). The new entity is `ClientOrganization` — the **employer** company. Don't confuse them.

## 1. Backend — new model

Create `backend/app/models/client_organization.py`:

```python
class ClientOrganization(Base):
    __tablename__ = "client_organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    org_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # Swedish org number (556xxx-xxxx)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    collective_agreement: Mapped[Optional[CollectiveAgreement]] = mapped_column(ValueEnum(CollectiveAgreement), nullable=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    employee_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=..., onupdate=...)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    creator: Mapped["User"] = relationship("User")
    clients: Mapped[list["Client"]] = relationship("Client", back_populates="client_organization")
```

## 2. Backend — update Client model

Add an **optional** FK to `Client`:

```python
client_organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID(as_uuid=True), ForeignKey("client_organizations.id"), nullable=True
)

# Add relationship
client_organization: Mapped[Optional["ClientOrganization"]] = relationship("ClientOrganization", back_populates="clients")
```

Keep `employer_name` as-is for backward compatibility. The frontend can display `client_organization.name` when linked, falling back to `employer_name`.

## 3. Backend — Alembic migration

Create a new migration that:
1. Creates the `client_organizations` table
2. Adds `client_organization_id` column to `clients` table (nullable, FK)
3. Does NOT drop `employer_name`

## 4. Backend — schemas

Create `backend/app/schemas/client_organization.py`:

- `ClientOrganizationCreate` — name (required), org_number, industry, collective_agreement, contact_person, contact_email, contact_phone, employee_count, notes
- `ClientOrganizationUpdate` — all fields optional
- `ClientOrganizationResponse` — all fields + id, organization_id, created_at, updated_at, created_by, client_count (computed: len of clients)
- `ClientOrganizationDetail` — extends Response with list of `ClientResponse` (for the detail page)

Update `ClientResponse` to include `client_organization_id: Optional[UUID]` and `client_organization_name: Optional[str]` (computed from the relationship).

Register in `schemas/__init__.py`.

## 5. Backend — endpoints

Create `backend/app/api/v1/endpoints/client_organizations.py`:

- `POST /` — create client organization (org-scoped)
- `GET /` — list all client organizations for the org, include client count per org
- `GET /{id}` — get single client organization with its clients listed
- `PATCH /{id}` — update client organization
- `DELETE /{id}` — soft delete or hard delete (only if no clients linked)

Register the router in the API router as `/api/v1/client-organizations`.

## 6. Backend — update seed script

Add 3 client organizations to the seed data:

```python
CLIENT_ORG_1_ID = _uuid("client_org.mckinsey_stockholm")
CLIENT_ORG_2_ID = _uuid("client_org.volvo_goteborg")
CLIENT_ORG_3_ID = _uuid("client_org.scandic_hotels")
```

| Name | Org Number | Industry | Agreement | Employees | Contact |
|------|-----------|----------|-----------|-----------|---------|
| McKinsey & Company Stockholm | 556XXX-XXXX | Managementkonsulting | ITP1 | 450 | Lisa Bergström, lisa.bergstrom@mckinsey.com |
| Volvo Cars Göteborg | 556XXX-XXXX | Fordonsindustri | SAF_LO | 12000 | Anders Nilsson, anders.nilsson@volvocars.com |
| Scandic Hotels AB | 556XXX-XXXX | Hotell & Restaurang | other | 3200 | Maria Svensson, maria.svensson@scandichotels.com |

Link existing seed clients to these orgs:
- Anna Johansson → McKinsey Stockholm
- Lars Pettersson → Volvo Göteborg

## 7. Frontend — hooks

Add to `frontend/lib/hooks.ts`:

```typescript
export interface ClientOrganizationResponse {
  id: string
  organization_id: string
  name: string
  org_number: string | null
  industry: string | null
  collective_agreement: string | null
  contact_person: string | null
  contact_email: string | null
  contact_phone: string | null
  employee_count: number | null
  notes: string | null
  client_count: number
  created_at: string
  updated_at: string
  created_by: string
}

export function useClientOrganizations() { ... }
export function useClientOrganization(id: string) { ... }
export function useCreateClientOrganization() { ... }
export function useUpdateClientOrganization() { ... }
```

## 8. Frontend — organizations list page

Create `frontend/app/(dashboard)/organizations/page.tsx`:

- Header: "Organisationer" with "Ny organisation" button (opens create dialog)
- Grid of organization cards, each showing:
  - Organization name (large, bold)
  - Industry tag
  - Collective agreement badge
  - "X anställda i systemet" (client_count from API)
  - Contact person name
  - Click → navigates to `/organizations/[id]`
- Search bar to filter by name
- Empty state: "Inga organisationer ännu" with prompt to create one

All text in **Swedish**.

## 9. Frontend — organization detail page

Create `frontend/app/(dashboard)/organizations/[id]/page.tsx`:

- Breadcrumbs: Organisationer → McKinsey & Company Stockholm
- Two-column layout:

**Left (wider):**
- Employee/client list — table with: name, age, collective agreement, active cases count
- Each row clickable → `/clients/[id]`
- "Lägg till klient" button (opens existing create client dialog, pre-filling the client_organization_id and employer_name)

**Right (sidebar):**
- Organization info card:
  - Name, org number, industry
  - Collective agreement
  - Employee count (from org + in system)
  - Contact: person, email, phone
  - Notes
  - "Redigera" button → inline edit or dialog

All text in **Swedish**.

## 10. Frontend — sidebar update

Add "Organisationer" nav item in `frontend/components/sidebar.tsx` using the `Building2` icon from lucide-react. Place it between "Klienter" and "Kunskapsbas":

```typescript
{ href: "/organizations", icon: Building2, label: "Organisationer", badge: clientOrgs?.length },
```

## 11. Frontend — update client pages

On the clients list page and client detail page:
- Show the client organization name (linked) instead of raw `employer_name` when a `client_organization_id` exists
- Clicking the org name navigates to `/organizations/[id]`

## Important

- All UI text in Swedish
- Match existing design system exactly (card styles, spacing, colors, font sizes)
- Minimum font size `text-xs`, prefer `text-sm`
- Buttons large enough for easy clicking (same as other pages)
- Multi-tenant: always scope by organization_id
- Run `pytest backend/tests/ -v --tb=short` after backend changes to make sure nothing breaks
- Add tests in `backend/tests/test_client_organizations.py` for the new CRUD endpoints (follow same pattern as test_cases.py and test_clients.py)
