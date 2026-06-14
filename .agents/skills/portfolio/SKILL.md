---
name: portfolio-documentation
description: >-
  Guides the creation of highly technical, clear, and comprehensive portfolio.md
  files for project repositories, featuring automated tech stack auditing,
  architectural trade-off tables, and core code snippet extraction.
---

# Portfolio Documentation Authoring Rules

This skill defines the rules and templates for generating a standard, technical `portfolio.md` file at the root of a project repository. This file serves as the source of truth for the developer's automated resume and portfolio website.

---

## 1. Codebase Scan & Audit (Pre-Writing Phase)

Before writing or editing the `portfolio.md` file, you must perform a comprehensive scan of the repository to identify the complete tech stack. Do not rely on manual memory.

### Step 1: Scan Dependency Files
* **JavaScript/TypeScript:** Parse `package.json` dependencies and devDependencies to identify frameworks (e.g. SvelteKit, React), data libraries (e.g. Supabase client, Prisma, Mongoose), and build tools (e.g. Vite, TailwindCSS).
* **Python:** Parse `requirements.txt`, `Pipfile`, or `pyproject.toml` (e.g. Flask, Django, Pandas).
* **Java:** Parse `pom.xml` or `build.gradle` (e.g. Spring Boot, JPA, Hibernate).
* **Other Languages:** Audit Go modules (`go.mod`), Rust configs (`Cargo.toml`), etc.

### Step 2: Scan Infrastructure & Tooling
* Look for configuration files that indicate infrastructure:
  * Presence of `Dockerfile` or `docker-compose.yml` $\rightarrow$ **Docker** / **Docker Compose**
  * Presence of `.github/workflows/` $\rightarrow$ **GitHub Actions**
  * Presence of `vercel.json` or `.vercel/` $\rightarrow$ **Vercel**
  * Presence of `supabase/` folder $\rightarrow$ **Supabase CLI** / **Supabase**

### Step 3: Scan Code Files & Imports
* Identify languages by file extensions (`.svelte`, `.ts`, `.js`, `.py`, `.java`, `.go`, `.rs`, `.sql`).
* Search codebase imports to identify integrations and external APIs (e.g. `google-calendar`, `gemini-api`, `spotify-api`).

### Step 4: Scan Decision Logs (ADRs)
* Parse all Architectural Decision Record (ADR) files located under `docs/decisions/` (format: `YYYY-MM-DD-*.md`).
* Extract key design context, considered options, trade-offs, and chosen rationales. Incorporate these decisions directly into the corresponding sections (`## Key Achievements`, `### Architectural Trade-offs`, and `## Technical Challenges & Deep Dives`) of `portfolio.md`.

---

## 2. Document Template Structure

Generate the `portfolio.md` file matching the following structure. Do not include frontmatter blocks (YAML/JSON). The file should be written in clean, standard markdown.

```markdown
# [Project Name]

[A 2-3 sentence high-level tagline explaining what the system is, who it is for, and its primary value proposition. This serves as the tagline.]

## Tech Stack
* **Languages:** [Comma-separated list, e.g. Python, TypeScript, SQL]
* **Frameworks & Libraries:** [Comma-separated list, e.g. SvelteKit, Flask, Spring Boot]
* **Tools & Databases:** [Comma-separated list of databases, tools, APIs, and infra, e.g. PostgreSQL, Docker, Google Calendar API]

## Key Achievements (Resume Bullets)
* [Action Verb] [Feature/System] [Technical Detail/Implementation] resulting in [Quantifiable Impact or Result].
* [Action Verb] [Complexity/Integration] [Implementation details] to solve [Problem/Challenge].
* [Action Verb] [Infrastructure/Architecture] [Optimizations] to achieve [Performance/Security improvement].

## Core Architecture & Data Flow
[A concise explanation of how components interact and how data flows through the system. Utilize a Mermaid diagram where helpful.]

### Architectural Trade-offs
[Present a table showing why specific technologies or patterns were selected over standard alternatives.]
| Decision | Selected Option | Considered Alternatives | Engineering Rationale |
|---|---|---|---|
| [Category, e.g. State] | [Selected, e.g. Svelte Runes] | [e.g. Redux / RxJS] | [Concrete rationale, e.g. Compile-time reactivity eliminates virtual-dom overhead; keeps bundle size minimal] |

## Technical Challenges & Deep Dives

### 1. [Challenge Name, e.g. Multi-Model Fallback Cascades]
* **Problem:** [Describe why this was difficult and the potential failure modes (e.g. API rate limits, model availability)]
* **Solution:** [Explain the technical solution, including data structures, retry strategies, and design patterns used]
* **Key Takeaway:** [Describe what you learned and the stability/performance result]


## System Performance & Key Metrics
[Provide a list of any performance guarantees, latency metrics, bundle sizes, or reliability standards achieved by the system, if applicable.]
* **Execution/Latency:** [e.g. Hydration completed in < 150ms; first contentful paint (FCP) of < 0.3s]
* **Resource Footprint:** [e.g. Production build bundle size < 45KB gzip]
* **Uptime/Stability:** [e.g. Robust error recovery allowing 100% operation retention during primary API timeouts]
```

---

## 3. Tone, Formatting & Resume Standards

* **Resume Style:** The bullet points under `## Key Achievements` must begin with strong, professional active verbs (e.g. *Engineered*, *Optimized*, *Architected*, *Implemented*, *Formulated*, *Redesigned*).
* **Technical Depth:** Be extremely precise. Use specific engineering terms (e.g. *PostGIS EWKB coordinate decoding*, *cascade fallback retry states*, *Row-Level Security allowlisting*) rather than generic phrases.
* **No Fluff:** Remove all filler text, welcoming phrases, or subjective statements.

## 4. Execution & File Generation
* Always execute the `write_to_file` tool to create or overwrite the `portfolio.md` file at the root of the repository (`C:\Users\ankit.yadav2\Documents\selfhost\portfolio.md`). Set `Overwrite` to true.
* In the chat response, output a clear summary of the file generation and list the generated content inside a code block for the user's review.

