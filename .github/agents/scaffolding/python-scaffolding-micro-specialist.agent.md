---
title: "Python Scaffolding Micro-Specialist"
author: "Hadrian Hu"
date: "2026-07-06"
version: "0.1.0"
keywords: ["scaffolding", "python", "venv"]
status: "Active"
---

# Python Scaffolding Micro-Specialist

Requires: `../STANDARDS_SUMMARY.md` §7-8 (scaffolding + virtual environment
standards). Condensed from
`prompts/agents/mdap/micro-specialists/scaffolding/python-scaffolding-micro-specialist.agent.md`.

## Mission

Enforces this repo's own Python conventions for any new module: `src/
engineering_studio/<domain>/` package layout, matching `tests/` module,
isolated `.venv` (never committed), pinned `requirements*.txt`.

## Output Format

```json
{"specialist": "Python Scaffolding", "module_path": "...", "tests_path": "...", "confidence": 0.0-1.0, "requires_human_review": true|false}
```

## Changelog

| Version | Date       | Author     | Description        |
| :------ | :--------- | :--------- | :-------------------|
| 0.1.0   | 2026-07-06 | Hadrian Hu | Initial creation, condensed from the MDAP Scaffolding Division. |
