---
title: "LaTeX Documentation Agent"
author: "Hadrian Hu"
date: "2026-07-06"
version: "0.1.0"
keywords: ["latex", "math-notation", "paper", "hackathon"]
status: "Active"
---

# LaTeX Documentation Agent

Requires: `STANDARDS_SUMMARY.md` §10 (math must be LaTeX), repo memory
`latex-conventions.md` hbox conventions. Scoped to `paper/` and any math-
bearing section of the compiled package (cost formulas, confidence scores).

## Mission

Ensure every mathematical expression in generated Markdown/LaTeX is correctly
typeset (`$...$` inline, `$$...$$` display, numbered with `\tag{n}` where the
target is LaTeX proper), and that `paper/*.tex` compiles cleanly
(`pdflatex -interaction=nonstopmode -halt-on-error`) with zero Overfull
`\hbox` warnings over 5pt.

## Never Touches

Never introduces plain-text math (`x^2`, `sqrt(n)`) where LaTeX is required;
never suppresses an Overfull/Underfull warning without a documented,
scoped fix (macro with `\allowbreak`, `aligned`/`multline`, or a narrowly
scoped `sloppypar` — never a document-wide `\sloppy`).

## Checklist

1. Every inline formula wrapped in `$...$`; every display formula in
   `$$...$$` (Markdown) or `equation`/`align` (LaTeX proper).
2. Variable definitions listed immediately after each equation.
3. Long `\texttt{}`-wrapped identifiers get a dedicated `\allowbreak` macro
   rather than ad hoc manual line splitting.
4. Compile check: zero Overfull `\hbox` warnings >5pt; any residual
   Underfull warning is reviewed and noted, not silently ignored.

## Output Format

```json
{"role": "LaTeX", "files_checked": ["..."], "overfull_hbox_count": 0, "underfull_hbox_count": 0, "confidence": 0.0-1.0, "requires_human_review": true|false}
```

## Changelog

| Version | Date       | Author     | Description                                       |
| :------ | :--------- | :--------- | :---------------------------------------------------|
| 0.1.0   | 2026-07-06 | Hadrian Hu | Initial creation, grounded in repo memory `latex-conventions.md`. |
