# frontend/ — Role 5 (Frontend, Visualization & Demonstration)

WHAT: Owned exclusively by Role 5. Web UI, dashboard, log/artifact
viewer, and any live visualization surface.
WHY: Isolated from `src/engineering_studio/` (Role 3) so Role 5 can move
fast without touching backend files — see `../SCAFFOLDING.md` §2.
HOW: Framework choice (React/Vue/plain HTML+JS/etc.) is intentionally
**not** prescribed here — pick whatever you can ship fastest in the
hackathon window. The one non-negotiable is the locked color palette in
`styles/theme.css`.

## Files in this folder

| File | Purpose |
|---|---|
| `styles/theme.css` | The three **locked** brand colors as CSS custom properties — import this into whatever framework you choose. |

## Mandatory color palette

Per `../docs/TEAM_QA.md` §4 (and `coding_stds/visualization/aesthetic_standards.txt`
in the private standards repo):

- `#FFAEC9` — foreground or background (soft rose pink)
- `#000000` — background or foreground (near-black)
- `#B76E79` — accents only (rose gold)

Never use a fourth "convenience" color without checking with Role 6/Role 1
first — one consistent palette across every surface (CLI output, web
viewer, diagrams) is part of the aesthetics standard.

## Accessibility

Whatever palette combination you use, verify WCAG 2.1 AA contrast ratios
(4.5:1 for normal text, 3:1 for large text/UI components) — color must
never be the sole means of conveying information (`../docs/TEAM_QA.md` §4).

## What you consume from the backend

Read-only: `src/engineering_studio/artifacts/<discipline>/output.md`
files (written by Role 3's `SpecialistAgent`) and/or the CLI's exported
report. Do not write into `src/engineering_studio/`.
