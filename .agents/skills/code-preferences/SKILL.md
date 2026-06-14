---
name: minimalist-data-development
description: Enforces the elimination of mock data, requires safe empty/fallback states to prevent crashes, permits hardcoding only when strictly necessary, and enforces a minimalist visual/UX style.
---

# Minimalist & Real-Data Development Guidelines

This skill enforces strict rules around mock data removal, safety boundaries, hardcoding restrictions, and minimalist design.

## Rules & Principles

1. **No Mock Data:**
   - Do not use mock data files, objects, or static mock values for application state.
   - All components and pages must load data directly from the server or database.

2. **Safe Fallbacks (No-Crash Policy):**
   - When real data is absent, the application must not crash or display raw error codes.
   - Render clean, functional empty states or "unconfigured" indicators (e.g., "Connect Google Calendar to see your schedule" or "Log your first meal to track macros").
   - Handle database nulls and API request failures gracefully.

3. **No Hardcoding unless Absolutely Necessary:**
   - Values like timezones, API endpoints, location coordinates, usernames, and goals must be dynamic and loaded from database rows or secure environment configurations.
   - Hardcoding is only permitted for configuration defaults (like `DEFAULT_TIMEZONE = 'America/New_York'`) when database-level values are missing.

4. **Minimalist Aesthetics:**
   - Design layouts to be highly functional, clean, and uncluttered.
   - Avoid excessive visual decorations, mesh backgrounds, or complex gradients unless requested.
   - Prioritize high-quality typography, clean borders, structured white space, and clear contrast.
   - Rely strictly on CSS variables defined in the central theme rather than ad-hoc inline styles.
