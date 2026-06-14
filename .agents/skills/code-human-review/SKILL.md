---
name: page-component-mapping
description: Enforces mapping all layout files, page loaders, subcomponents, and database helpers involved in a page whenever a page change or refactor is discussed, displaying their relationship and communication flow.
---

# Page Component Mapping Guidelines

This skill dictates a strict protocol for analyzing and representing the components, loaders, database files, and communication lines that comprise any given SvelteKit route page.

## Guidelines

1. **Identify Route Files:**
   - Always list the entry route files with their exact absolute Windows system paths starting with the drive volume (e.g. `C:\Users\...\src\routes\+page.svelte`).
   - For each route, include a brief explanation detailing why the page exists, what user value it serves, and what core task it performs in the application.

2. **Map Imported Components:**
   - Track every Svelte sub-component imported directly or indirectly into the page.
   - Specify the exact, absolute Windows system path of each component (e.g. `C:\Users\...\src\lib\ui\Card.svelte`).
   - For each component, include a brief explanation detailing its visual function and role on the page.

3. **Identify Backend Helpers:**
   - List all database wrapper files, LLM wrappers, external API helpers, or date utilities called by the loader or server actions, showing their exact absolute Windows system paths (e.g. `C:\Users\...\src\lib\server\context.js`).
   - For each helper, include a brief explanation of the database tables or external APIs it queries.

4. **Map Data & Communication Flow:**
   - Represent the page's communication flow using **all three** of the following formats to provide clear architectural perspectives:
     - **Option 1: Data Schema Mapping Table:** A table showing the connection between database tables/columns, fetching helpers, frontend components, and the final displayed UI elements.
     - **Option 2: Plain Text Pipeline:** A chronological step-by-step text description illustrating the lifetime of data (Fetching -> Serialization -> Binding -> Mutations).
     - **Option 3: Mermaid Sequence Diagram:** A sequence diagram (`sequenceDiagram`) representing chronological actor calls (Database -> Loader -> View -> Components). Do **not** use confusing block flowcharts (`graph TD`).

5. **Inline Text Output Only (No Artifact Docs):**
   - Do **NOT** write mapping documentation to separate artifact files or directories.
   - Always render the full component list, file paths, descriptions, tables, and flowcharts directly inside the main chat response.




