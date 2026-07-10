- Paper
WHAT: The project's written formal artifacts — a full mathematical
model/proofs paper and a shorter public-facing whitepaper — plus their
compiled PDFs.
WHY: Keeps the LaTeX source and its build output isolated from `docs/`
(day-to-day team documentation) and `presentation/` (slide deck), so
Role 6 can iterate the formal writing on its own schedule without
touching either — see `../SCAFFOLDING.md` §2.
HOW: Edit the `.tex` source, then recompile to the matching `.pdf` (e.g.
`pdflatex engineering_studio_ai_paper.tex`, run twice so cross-references
and `lastpage` resolve). Both `.tex` files follow
`coding_stds/documentation/latex_style_guide.txt` and
`coding_stds/mathematics/mathematical_proof_structures_standards.txt`
(internal standards corpus; condensed rules for this repo live in
`../AGENTS.md`).

## Files in this folder

| File | Purpose |
|---|---|
| `engineering_studio_ai_paper.tex` | The full formal paper: the multi-agent framework's mathematical model and proofs (acyclicity, bounded rework termination, minimum agent multiplicity, trust-tier safety, plus a labeled token/cost convergence sketch — see `../docs/TEAM_QA.md` §3.6 and §9). |
| `engineering_studio_ai_paper.pdf` | Compiled output of the above. |
| `engineering_studio_ai_whitepaper_for_team_public.tex` | A shorter, public-facing whitepaper distilled from the full paper — for sharing outside the team without the complete proof detail. |
| `engineering_studio_ai_whitepaper_for_team_public.pdf` | Compiled output of the above. |

## A note on the PDFs

Both `.pdf` files are tracked via **Git LFS** (see `../.gitattributes`).
If you've cloned without LFS support, or downloaded a plain zip/tarball
of the repo, what you'll see on disk is a small ~130-byte pointer file
(`version https://git-lfs.github.com/spec/v1 ...`) instead of the real
PDF — that's expected, not a corrupted file. Run `git lfs pull` (or
`git lfs install` once, then re-clone) to fetch the actual PDF bytes.

## Rules

1. Every claim in either document must be traceable to something already
   established elsewhere in the repo (code, tests, `docs/task-specs.md`,
   `research/` findings) or explicitly labeled a sketch/assumption rather
   than a proved result — no unlabeled speculative claims, per the
   project's zero-hallucination testing standard (`../docs/TEAM_QA.md`
   §5).
2. If you change a claim in the full paper that the whitepaper also
   states (e.g. which properties are proved vs. sketched), update both
   documents in the same PR so they don't drift apart.
3. Recompile and spot-check the PDF locally before committing — a `.tex`
   edit that fails to build or silently drops a section is worse than no
   edit.
4. This folder is exclusively Role 6's — see `../SCAFFOLDING.md` §2's
   ownership-zone table.
