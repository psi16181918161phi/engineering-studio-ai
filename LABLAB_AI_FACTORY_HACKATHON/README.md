---
title: "LabLab AI Factory Hackathon — Project Reference & Participation Guide"
author: "Hadrian Hu"
date: "2026-07-06"
version: "2026.1.0.0"
keywords: ["ai-factory", "hackathon", "lablab", "llm", "multi-agent", "rapid-prototyping", "submission-guide"]
status: "Draft"
confidentiality: "DRAFT — NOT FOR DISTRIBUTION"
changelog:
  - version: "2026.1.0.0"
    date: "2026-07-06"
    author: "Hadrian Hu"
    description: "Initial document creation — LabLab AI Factory Hackathon reference and participation guide."
---

# LabLab AI Factory Hackathon — Project Reference & Participation Guide

---

## Table of Contents

- [LabLab AI Factory Hackathon — Project Reference \& Participation Guide](#lablab-ai-factory-hackathon--project-reference--participation-guide)
  - [Table of Contents](#table-of-contents)
  - [Abstract](#abstract)
  - [Keywords](#keywords)
  - [Executive Summary](#executive-summary)
  - [1. Overview of LabLab.ai](#1-overview-of-lablabai)
    - [1.1. Platform Mission](#11-platform-mission)
    - [1.2. Community Scale](#12-community-scale)
  - [2. AI Factory Hackathon Format](#2-ai-factory-hackathon-format)
    - [2.1. Event Structure](#21-event-structure)
    - [2.2. Tracks and Themes](#22-tracks-and-themes)
    - [2.3. Judging Criteria](#23-judging-criteria)
  - [3. Participation Requirements](#3-participation-requirements)
    - [3.1. Eligibility](#31-eligibility)
    - [3.2. Team Composition](#32-team-composition)
    - [3.3. Submission Requirements](#33-submission-requirements)
  - [4. Technical Stack and Tooling](#4-technical-stack-and-tooling)
    - [4.1. Supported AI Frameworks](#41-supported-ai-frameworks)
    - [4.2. Recommended Architecture Patterns](#42-recommended-architecture-patterns)
    - [4.3. Coding Standards Compliance](#43-coding-standards-compliance)
  - [5. Project Structure for This Repository](#5-project-structure-for-this-repository)
    - [5.1. Directory Layout](#51-directory-layout)
    - [5.2. Functional Programming Standards](#52-functional-programming-standards)
    - [5.3. SOLID Principles Application](#53-solid-principles-application)
  - [6. Submission Workflow](#6-submission-workflow)
    - [6.1. Pre-Submission Checklist](#61-pre-submission-checklist)
    - [6.2. Deliverables](#62-deliverables)
  - [7. Evaluation Metrics](#7-evaluation-metrics)
    - [7.1. Technical Assessment](#71-technical-assessment)
    - [7.2. Business Impact Assessment](#72-business-impact-assessment)
  - [8. Assumptions](#8-assumptions)
  - [9. Limitations](#9-limitations)
  - [Appendix A: Acronyms and Abbreviations](#appendix-a-acronyms-and-abbreviations)
  - [References](#references)
  - [Changelog](#changelog)

---

## Abstract

This document serves as the primary reference guide for participation in the
**LabLab AI Factory Hackathon**, an accelerated innovation programme hosted on
the LabLab.ai platform. LabLab.ai is a community-driven platform with over
100,000 registered builders that hosts structured hackathons enabling
participants to develop **Artificial Intelligence (AI)** prototypes using
cutting-edge **Large Language Model (LLM)** APIs and multi-agent frameworks.
The AI Factory format is characterised by condensed sprint durations (typically
48 to 72 hours), sponsor-provided technology stacks, and a structured submission
pipeline. The methodology adopted in this repository applies Functional
Programming principles per **JPL/NASA** coding standards, SOLID design
principles, and full unit-testability to all prototype code. Key outcomes
targeted include a working end-to-end AI application, a documented architecture,
and a compliant submission package. This guide provides team members and AI
agents with all information required to orient themselves, select an appropriate
technical stack, structure the codebase, and complete the submission within the
hackathon window.

---

## Keywords

ai-factory, hackathon, lablab, llm, multi-agent, rapid-prototyping,
submission-guide

---

## Executive Summary

**Objective:** Equip every team member and any AI agent operating within this
repository with a single authoritative reference for the LabLab AI Factory
Hackathon — covering platform context, event format, technical requirements,
coding standards, and the submission workflow.

**Approach:** This document aggregates publicly available information about
LabLab.ai and its AI Factory hackathon format, maps that information onto the
engineering standards mandated by this repository's `coding_stds/` suite, and
provides a structured project layout and pre-submission checklist. All code
produced under this repository must comply with Functional Programming
principles, SOLID design, and the testing standards that mandate 100% unit-test
coverage on all pure functions.

**Outcome:** A team reading this document from top to bottom will understand
(a) what the hackathon requires, (b) how this repository is organised, (c) what
coding standards apply, and (d) exactly what to deliver and when. An AI agent
reading this document will have sufficient context to generate compliant code,
documentation, and submission artefacts without additional prompting.

**Recommendations:**

1. Read this document in full before writing a single line of code.
2. Establish the technology stack selection (Section 4) within the first two
   hours of the hackathon window.
3. Commit to the directory layout in Section 5.1 immediately and do not
   restructure mid-sprint.
4. Treat the pre-submission checklist (Section 6.1) as a blocking gate — no
   submission is made until every item is ticked.
5. Ensure at least one team member is responsible for documentation parity;
   code and documentation must be updated in lockstep.

---

## 1. Overview of LabLab.ai

### 1.1. Platform Mission

**LabLab.ai** is an innovation platform founded to democratise access to
state-of-the-art AI technologies by connecting builders, developers, and
entrepreneurs with sponsor-provided API credits, mentorship, and a structured
hackathon environment. The platform's stated mission is to accelerate the
transition from AI concept to working prototype by removing the friction of
infrastructure provisioning and technology discovery.

LabLab.ai operates under a community-first model: participants are encouraged
to form teams across disciplines (engineering, design, product, domain
expertise) and to leverage the platform's integrated tutorial library alongside
the sponsor technology stacks provided for each event.

### 1.2. Community Scale

As of the most recent publicly available data, the LabLab.ai platform reports:

1. Over 100,000 registered community members across more than 180 countries.
2. More than 500 hackathon events hosted since platform launch.
3. Thousands of AI prototypes submitted and evaluated across all events.
4. Partnerships with major AI technology providers including OpenAI, Cohere,
   AI21 Labs, Stability AI, and others depending on the specific event.

---

## 2. AI Factory Hackathon Format

### 2.1. Event Structure

The **AI Factory** is LabLab.ai's flagship accelerated hackathon format. Its
defining characteristics are:

1. **Sprint Duration:** Typically 48 to 72 hours from kick-off to submission
   deadline; some extended editions run up to 7 days.
    1.1. The condensed timeline is intentional — it enforces scope discipline
         and forces teams to ship a working **Minimum Viable Product (MVP)**.
    1.2. Extended editions allow more polish but apply the same MVP-first
         philosophy.
2. **Sponsor Technology Stacks:** Each event is anchored to one or more sponsor
   AI APIs or frameworks. Participants are expected to build their submission
   *using* the sponsor technology as a core component.
    2.1. Sponsor credits (API tokens) are distributed to registered teams at
         kick-off.
    2.2. Use of the sponsor technology is typically a hard judging requirement —
         submissions not using the sponsor stack are disqualified.
3. **Mentorship Sessions:** Live office hours with sponsor engineers and
   LabLab.ai mentors are scheduled during the sprint window.
4. **Submission Portal:** All deliverables are submitted through the LabLab.ai
   platform submission interface; GitHub repository links are mandatory.

### 2.2. Tracks and Themes

AI Factory events are typically themed around a vertical or capability domain.
Common recurring themes observed across prior events include:

1. Autonomous **AI Agent** and multi-agent orchestration systems.
2. **Retrieval-Augmented Generation (RAG)** pipelines for enterprise knowledge
   management.
3. AI-powered developer tooling (code review, documentation generation,
   test generation).
4. Healthcare and life-sciences AI applications.
5. Creative and generative media (image, audio, video synthesis).
6. Sustainability and climate-tech AI applications.

The specific theme for the event this repository targets should be confirmed
against the official event page on LabLab.ai.

### 2.3. Judging Criteria

Judging across AI Factory events consistently evaluates submissions on the
following dimensions, though exact weightings vary by event:

1. **Technical Implementation** — Quality, completeness, and correctness of the
   working prototype.
    1.1. Does the application run end-to-end without manual intervention?
    1.2. Is the sponsor technology meaningfully integrated (not cosmetic)?
2. **Innovation and Creativity** — Novelty of the problem addressed or the
   approach taken.
3. **Business Viability** — Clarity of the value proposition and potential
   real-world applicability.
4. **Presentation Quality** — Clarity of the demo video and written description.
5. **Use of Sponsor Technology** — Depth and appropriateness of sponsor API/
   framework usage.

---

## 3. Participation Requirements

### 3.1. Eligibility

1. Registration must be completed on the official LabLab.ai platform prior to
   the hackathon kick-off time.
2. Participants must agree to the LabLab.ai Terms of Service and the specific
   event rules published on the event page.
3. There are no geographic restrictions; the platform is open globally.
4. Both individual and team participation are permitted, subject to team-size
   limits (see Section 3.2).

### 3.2. Team Composition

1. Teams typically consist of 1 to 5 members.
    1.1. Solo participation is permitted.
    1.2. Teams exceeding the maximum size limit are subject to disqualification.
2. Team formation tools are available on the LabLab.ai platform for participants
   seeking collaborators.
3. All team members must be registered on the platform before the submission
   is finalised.

### 3.3. Submission Requirements

1. A working prototype hosted or demonstrable via a public URL, or a locally
   runnable application with clear setup instructions.
2. A GitHub repository that is:
    2.1. Public (or shared with LabLab.ai judges as specified).
    2.2. Containing a `README.md` with setup and usage instructions.
    2.3. Containing all source code committed before the submission deadline.
3. A demo video (typically 3 to 5 minutes) demonstrating the working prototype.
4. A written project description submitted through the LabLab.ai portal covering
   the problem, solution, and technology stack used.

---

## 4. Technical Stack and Tooling

### 4.1. Supported AI Frameworks

The following frameworks and libraries are commonly available and supported
across LabLab.ai AI Factory events. Final stack selection must be aligned with
the specific sponsor technology for the event being entered.

1. **LLM API Providers**
    1.1. OpenAI API (`gpt-4o`, `gpt-4-turbo`, `text-embedding-3-large`)
    1.2. Cohere API (`command-r-plus`, `embed-v3`)
    1.3. Anthropic API (`claude-3-5-sonnet`, `claude-3-haiku`)
    1.4. AI21 Labs (`jamba-1.5`)
2. **Orchestration and Agent Frameworks**
    2.1. LangChain / LangGraph
    2.2. LlamaIndex
    2.3. CrewAI
    2.4. AutoGen (Microsoft)
3. **Vector Databases** (for RAG pipelines)
    3.1. Pinecone
    3.2. Weaviate
    3.3. Chroma
4. **Deployment Platforms**
    4.1. Streamlit (rapid UI prototyping)
    4.2. FastAPI (REST API layer)
    4.3. Gradio (ML-focused UI)
    4.4. Hugging Face Spaces (public hosting)

### 4.2. Recommended Architecture Patterns

Given the condensed sprint duration, the following architecture patterns are
recommended for AI Factory submissions:

1. **RAG Pipeline Pattern** — suitable when the domain has a document corpus.
    1.1. Ingest → Chunk → Embed → Store → Retrieve → Generate.
    1.2. Use `text-embedding-3-large` or equivalent for embedding quality.
2. **Multi-Agent Orchestration Pattern** — suitable for complex, multi-step
   workflows.
    2.1. Define agents with single responsibilities (respects SOLID **Single
         Responsibility Principle**).
    2.2. Use a supervisor/router agent to delegate to specialist agents.
3. **Tool-Augmented LLM Pattern** — suitable for agentic tasks requiring
   external data or computation.
    3.1. Define tools as pure functions with typed inputs and outputs.
    3.2. Register tools with the LLM via function-calling or tool-use APIs.

### 4.3. Coding Standards Compliance

All code in this repository is subject to the following mandatory standards,
regardless of sprint time pressure:

1. **Functional Programming** — per `architecture/10_Functional_Programming_Principles_detailed.txt`.
    1.1. Prefer pure functions: same input always produces same output, no side
         effects.
    1.2. Immutability: do not mutate state in place; return new objects.
    1.3. Bounded loops: no unbounded recursion or dynamic memory growth after
         initialisation.
2. **SOLID Principles** — per `architecture/SOLID_coding_programming_philosophy_detailed.txt`.
    2.1. Single Responsibility: each class and function has exactly one reason
         to change.
    2.2. Open/Closed: extend behaviour via composition, not modification.
    2.3. Dependency Inversion: depend on abstractions, not concrete
         implementations.
3. **Docstrings** — every function and class must document: purpose, inputs,
   outputs, and side effects (if any).
4. **Unit Testability** — all pure functions must have corresponding unit tests;
   target 100% coverage on the business logic layer.

---

## 5. Project Structure for This Repository

### 5.1. Directory Layout

```text
LABLAB_AI_FACTORY_HACKATHON/
├── README.md                  # This document
├── pyproject.toml             # Project metadata and dependency management
├── .env.example               # Environment variable template (no secrets committed)
├── src/
│   ├── __init__.py
│   ├── agents/                # Agent definitions (one file per agent role)
│   ├── tools/                 # Pure-function tool definitions
│   ├── pipelines/             # Orchestration / workflow logic
│   ├── models/                # Data models and schema definitions (Pydantic)
│   └── utils/                 # Shared utility functions
├── tests/
│   ├── unit/                  # Unit tests for all pure functions in src/
│   ├── integration/           # Integration tests for pipeline end-to-end flows
│   └── conftest.py            # Shared pytest fixtures
├── docs/
│   ├── architecture/          # Architecture decision records
│   └── assets/                # Diagrams and supporting images
├── scripts/
│   └── ingest.py              # Data ingestion / setup scripts
└── markdowns/
    ├── reports/               # Progress and outcome reports
    └── chats/                 # AI agent session summaries
```

### 5.2. Functional Programming Standards

All functions in `src/tools/` and `src/utils/` must conform to the following
template:

```python
from typing import Final
from collections.abc import Sequence


# ---------------------------------------------------------------------------
# Pure function — no side effects; deterministic output
# ---------------------------------------------------------------------------
def compute_similarity_score(
    query_embedding: Sequence[float],
    document_embedding: Sequence[float],
) -> float:
    """
    Compute the cosine similarity between two embedding vectors.

    Purpose:
        Provide a deterministic, side-effect-free similarity metric for use
        in retrieval ranking within the RAG pipeline.

    Inputs:
        query_embedding    — 1-D sequence of floats representing the query.
        document_embedding — 1-D sequence of floats representing the document.

    Outputs:
        float in the range [-1.0, 1.0]; 1.0 indicates identical direction.

    Side Effects:
        None.
    """
    if len(query_embedding) != len(document_embedding):
        raise ValueError(
            f"Embedding dimension mismatch: "
            f"{len(query_embedding)} != {len(document_embedding)}"
        )

    dot: Final[float] = sum(q * d for q, d in zip(query_embedding, document_embedding))
    norm_q: Final[float] = sum(q ** 2 for q in query_embedding) ** 0.5
    norm_d: Final[float] = sum(d ** 2 for d in document_embedding) ** 0.5

    if norm_q == 0.0 or norm_d == 0.0:
        return 0.0

    return dot / (norm_q * norm_d)
```

### 5.3. SOLID Principles Application

Agent classes must follow the Single Responsibility Principle. Each agent class
is responsible for exactly one role:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Abstract base — Dependency Inversion (depend on abstraction, not concrete)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AgentResponse:
    """
    Immutable value object representing the output of an agent invocation.

    Inputs:  N/A (dataclass)
    Outputs: N/A (dataclass)
    Side Effects: None.
    """

    content: str
    confidence: float
    source_references: tuple[str, ...]


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the AI Factory prototype.

    Purpose:
        Define the interface contract that all concrete agents must satisfy,
        enabling Liskov-substitutable agent implementations.

    Side Effects: None at the abstract level.
    """

    @abstractmethod
    def run(self, query: str) -> AgentResponse:
        """
        Execute the agent on the provided query.

        Inputs:
            query — natural-language string from upstream orchestrator.
        Outputs:
            AgentResponse — immutable response value object.
        Side Effects:
            Concrete implementations may perform I/O (network calls to LLM API).
            Document any such side effects in the concrete class docstring.
        """
        ...
```

---

## 6. Submission Workflow

### 6.1. Pre-Submission Checklist

The following checklist is a **blocking gate** — the submission must not be
made until every item is confirmed:

| Item | Automated | Owner |
| :----- | :---------: | :------ |
| All code committed and pushed to `main` | - | Lead Engineer |
| `README.md` updated with setup and usage instructions | - | Lead Engineer |
| `.env.example` present with all required variable names (no values) | - | Lead Engineer |
| Demo video recorded and uploaded (3–5 minutes) | - | Team Lead |
| Project description written and ready for portal submission | - | Team Lead |
| All unit tests passing (`pytest tests/unit/`) | Yes | CI |
| No hardcoded secrets or API keys in any committed file | Yes | CI |
| Sponsor technology is demonstrably used in the working prototype | - | All Members |
| LabLab.ai submission portal form completed | - | Team Lead |
| All team members listed on the submission | - | Team Lead |

Caption: Table 1 — Pre-Submission Blocking Checklist

### 6.2. Deliverables

1. **GitHub Repository** — public, containing complete source code and this
   `README.md`.
2. **Demo Video** — 3 to 5 minutes; must demonstrate a working end-to-end flow
   using the sponsor technology.
3. **Written Description** — submitted via the LabLab.ai portal; must address:
    3.1. Problem statement.
    3.2. Solution overview and key features.
    3.3. Technology stack and sponsor technology usage.
    3.4. Setup and run instructions (or link to `README.md`).
4. **Live Demo URL** (if applicable) — Streamlit, Gradio, or Hugging Face Spaces
   link.

---

## 7. Evaluation Metrics

### 7.1. Technical Assessment

The following quantitative metrics inform the technical quality evaluation of
the submission:

| Metric | Target | Measurement Method |
| :------- | -------: | :------------------- |
| Unit test pass rate | 100 % | `pytest --tb=short` |
| Test coverage (business logic) | ≥ 95 % | `pytest --cov=src` |
| End-to-end pipeline latency | ≤ 5,000 ms | Manual timing / profiler |
| LLM API error rate (during demo) | 0 % | Manual observation |
| Code complexity (cyclomatic) | ≤ 10 per function | `radon cc src/` |

Caption: Table 2 — Technical Quality Metrics

### 7.2. Business Impact Assessment

Business impact is assessed qualitatively by judges against:

1. **Problem Significance** — Is the problem being solved material and
   well-scoped for a hackathon prototype?
2. **Solution Differentiation** — Does the approach offer meaningful improvement
   over a naive baseline?
3. **Scalability Signal** — Does the architecture suggest it could scale beyond
   the prototype, even if not implemented at scale in the submission?
4. **User Experience** — Is the demo interface intuitive and the value
   proposition immediately legible to a non-technical judge?

---

## 8. Assumptions

1. The specific event sponsor technology and theme will be confirmed by the team
   at hackathon kick-off and backfilled into Section 4 of this document.
2. All team members have active accounts on LabLab.ai prior to the sprint start.
3. The rendering environment for this document supports standard **GitHub
   Flavored Markdown (GFM)**.
4. API credits provided by the sponsor are sufficient for development and demo
   use; budget management is the team's responsibility if overages occur.
5. Python $\geq$ 3.11 is the target runtime for all code in this repository
   unless a specific sponsor technology mandates otherwise.

---

## 9. Limitations

1. This document captures the general AI Factory format as observed across
   multiple events; specific rules for the target event may differ and must be
   verified against the official event page.
2. Sponsor API rate limits and credit caps are outside this team's control and
   may constrain demo reliability; mitigation via response caching is recommended.
3. The 48–72 hour sprint window prohibits production-grade hardening; the
   submission is explicitly a prototype and should be represented as such in the
   written description.
4. Test coverage targets in Section 7.1 apply to the business logic layer only;
   infrastructure and glue code are exempt from the coverage gate for the
   purposes of the hackathon submission.

---

## Appendix A: Acronyms and Abbreviations

| Acronym | Definition |
| :-------- | :----------- |
| AI | Artificial Intelligence |
| API | Application Programming Interface |
| GFM | GitHub Flavored Markdown |
| JPL | Jet Propulsion Laboratory |
| LLM | Large Language Model |
| MVP | Minimum Viable Product |
| NASA | National Aeronautics and Space Administration |
| RAG | Retrieval-Augmented Generation |
| SOLID | Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion |
| TOC | Table of Contents |
| YPSV | Year-Prefixed Semantic Versioning |

Caption: Table A1 — Acronyms and Abbreviations

---

## References

[1] LabLab.ai, *LabLab AI Platform — Hackathons and AI Factory Events*, LabLab.ai,
2024. [Online]. Available: <https://lablab.ai>

[2] LabLab.ai, *AI Factory — Event Format and Rules*, LabLab.ai, 2024. [Online].
Available: <https://lablab.ai/event>

[3] H. Hu, *coding\_stds/ — Most-Cited Standards Quick Index (AI-Agent Navigation Hub)*,
Internal Standards Repository, version 2026.1.0.0, 2026-07-06.

[4] H. Hu, *Markdown Standards*, Internal Standards Repository, `documentation/markdown_standards.txt`,
version 2026.1.0.0.

[5] NASA/JPL, *JPL Institutional Coding Standard for the C Programming Language*,
Jet Propulsion Laboratory, California Institute of Technology, Pasadena, CA,
USA, 2009. [Online]. Available: <https://lars-lab.jpl.nasa.gov/JPL_Coding_Standard_C.pdf>

---

## Changelog

Caption: Table C1 — Document Revision History

| Version | Date | Author | Description |
|:--------|:-----|:-------|:------------|
| 2026.1.0.0 | 2026-07-06 | Hadrian Hu | Initial document creation — LabLab AI Factory Hackathon reference and participation guide. |
