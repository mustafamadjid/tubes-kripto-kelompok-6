# Civic Trust UI Refresh Design

## Context

The project is a FastAPI and Jinja2 e-voting prototype for a cryptography course. It demonstrates RSA-OAEP encryption, SHA-256 hashing, RSA-PSS signatures, recapitulation, audit logging, and crypto benchmarking.

The current interface works, but it mixes a generic landing-page shell with decorative voting artwork and placeholder navigation labels. That makes the app feel less like a secure voting portal and less clear for voters, admins, and demo reviewers.

## Goal

Refresh the web UI into a Civic Trust Dashboard: calm, official, accessible, and data-oriented. The redesign should improve perceived trust, task clarity, mobile behavior, and admin readability while preserving the existing backend routes and Jinja template structure.

## Non-Goals

- No backend route changes.
- No database schema changes.
- No new JavaScript framework.
- No real-time results or live polling.
- No new authentication behavior.
- No production-grade election claims beyond the existing academic prototype framing.

## Design Direction

Use a light dashboard system anchored in civic blue, slate neutrals, white surfaces, and amber action highlights. The app should look like a secure operational portal rather than a marketing page.

Recommended visual tokens:

- Primary: `#1E40AF`
- Secondary: `#3B82F6`
- Accent action: `#D97706`
- Background: `#F8FAFC`
- Text: `#0F172A`
- Muted text: `#64748B`
- Card: `#FFFFFF`
- Border: `#DBEAFE`
- Success: `#16A34A`
- Warning: `#D97706`
- Error: `#DC2626`

Typography should stay system-font based for reliability and speed. Use tighter dashboard hierarchy: medium-sized page headings, compact body copy, readable labels, and tabular text where hashes, IDs, and benchmark values appear.

## App Shell

Replace generic brand and navigation labels with app-specific language:

- Brand: `SecureVote RSA`
- Voter path: `Voter Login`, `Ballot`
- Admin path: `Admin`, `Dashboard`, `Results`, `Audit`, `Benchmarks`

The header should be compact, sticky or visually persistent enough to orient users, and responsive on mobile. Active page states should be visible through color, underline, or filled navigation treatment.

The layout should use a constrained content width, pale page background, white panels, and consistent spacing. Avoid decorative blobs, oversized hero text, and unrelated illustration-heavy composition.

## Voter Experience

The voter login page should become a focused portal entry screen:

- Left side or primary area: login form with clear `NIM` and password fields.
- Supporting area: short assurance panel explaining the demo pipeline: encrypted, hashed, signed, audited.
- Admin login should remain discoverable but secondary.
- Error messages should be visually distinct and near the form.

The ballot page should prioritize decision clarity:

- Show voter name and one-time voting status clearly.
- Candidate cards should be large, scannable, and fully clickable.
- Selected candidate state must be obvious.
- Include a short finality notice before submit.
- Submit button should be prominent and use the amber action color.
- Already-voted state should use a calm confirmation panel instead of a plain message.

The success page should reassure the user:

- Confirm the vote was recorded.
- Display the vote ID in a readable code block.
- Summarize the cryptographic processing in concise language.
- Provide a clear return action.

## Admin Experience

The admin dashboard should feel like an operations dashboard:

- KPI cards for voters, candidates, vote records, and audit logs.
- A primary action for running recapitulation.
- Secondary actions for results, audit logs, and benchmarks.
- Short helper text that tells the admin what each action does.

The results page should make validity easy to scan:

- KPI cards for total, valid, and invalid votes.
- Candidate result table in a responsive table wrapper.
- Invalid vote details with status/reason chips where possible.
- Empty state that clearly tells the admin to run recapitulation first.

The audit logs and benchmark pages should use readable, responsive tables:

- Wrap tables in horizontal scroll containers on small screens.
- Use compact row height and clear header contrast.
- Apply monospace styling for IDs, hashes, or technical samples.
- Use hover states for rows to aid scanning.

## Components

Core reusable CSS classes should cover:

- Page shell and content container.
- Header, brand, navigation, active links.
- Buttons with primary, secondary, ghost, and danger variants.
- Panels and cards.
- KPI stat cards.
- Forms, labels, inputs, help text, and errors.
- Candidate card radio selections.
- Alerts and status chips.
- Table wrappers and dense tables.
- Code blocks for vote IDs and technical values.

Do not introduce nested cards. Cards are for repeated items, panels, stat summaries, and table sections only.

## Accessibility

The refresh must improve keyboard and low-vision usability:

- Every interactive element has a visible focus state.
- Text contrast targets WCAG AA.
- Inputs keep real labels, not placeholder-only labels.
- Buttons and links have minimum practical touch targets.
- Tables do not overflow the viewport without a scroll wrapper.
- Selected radio-card state is not communicated by color alone.
- Motion, if added, is subtle and respects reduced-motion preferences.

## Responsive Behavior

Verify layouts at these widths:

- 375px mobile
- 768px tablet
- 1024px laptop
- 1440px desktop

On mobile, navigation may wrap or become a compact horizontal scroller. Forms and candidate cards become single-column. Admin KPI cards collapse from four columns to two or one depending on available width. Tables scroll horizontally inside their section instead of breaking the page.

## Implementation Scope

Expected files:

- `app/templates/base.html`
- `app/templates/login.html`
- `app/templates/admin_login.html`
- `app/templates/vote.html`
- `app/templates/vote_success.html`
- `app/templates/admin_dashboard.html`
- `app/templates/recap_result.html`
- `app/templates/audit_logs.html`
- `app/templates/benchmark.html`
- `app/static/styles.css`

Implementation should stay template-first and CSS-first. No JavaScript is required unless needed for minor progressive enhancement.

## Verification

Run automated tests to confirm backend behavior is unchanged:

```bash
pytest
```

If the app can be started locally, visually verify:

- Voter login
- Admin login
- Ballot selection
- Already-voted state
- Vote success
- Admin dashboard
- Results empty and populated states when available
- Audit logs
- Benchmarks

At minimum, inspect the rendered templates or run the app in a browser to confirm no text overlap, broken table behavior, or inaccessible focus styles.

## Acceptance Criteria

- The app no longer presents generic navigation labels or placeholder branding.
- Voter and admin flows have distinct but coherent visual hierarchy.
- Candidate selection state is obvious with mouse and keyboard.
- Admin KPI, result, audit, and benchmark data is easier to scan.
- Tables behave on mobile without breaking the viewport.
- Focus states and form labels are visible and consistent.
- The implementation does not change backend behavior or tests.
