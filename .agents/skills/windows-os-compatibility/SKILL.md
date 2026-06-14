---
name: windows-compatibility
description: Documents known terminal execution failures on Windows systems (e.g. PowerShell execution policy restrictions) and provides successful Node/CMD workarounds.
---

# Windows Compatibility & Command Guidelines

This skill documents terminal execution limitations on Windows hosts and details the correct, tested workarounds.

## Diagnostics & Workarounds

### 1. PowerShell Script Execution Block (UnauthorizedAccess)
* **Problem:** Running package scripts directly using `npm run <name>` or executing global CLI scripts (like `svelte-check.ps1`) fails with a security policy error:
  `File ... cannot be loaded because running scripts is disabled on this system.`
* **Failed Command:**
  ```powershell
  npm run check:svelte
  ```
* **Successful Workaround:** Execute the package binary directly using Node:
  ```powershell
  node node_modules/svelte-check/bin/svelte-check --fail-on-warnings
  ```

### 2. Vitest Test Runner Execution
* **Problem:** Proposing standard test runners like `npm run test` fails under the execution policy.
* **Failed Command:**
  ```powershell
  npm run test
  ```
* **Successful Workaround:** Execute Vitest directly using Node:
  ```powershell
  node node_modules/vitest/vitest.mjs run
  ```

### 3. SvelteKit Syncing
* **Problem:** SvelteKit type syncing script execution.
* **Failed Command:**
  ```powershell
  npm run prepare
  ```
* **Successful Workaround:** Execute SvelteKit CLI wrapper via node:
  ```powershell
  node node_modules/@sveltejs/kit/svelte-kit sync
  ```
