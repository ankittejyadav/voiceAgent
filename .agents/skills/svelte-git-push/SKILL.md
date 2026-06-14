---
name: svelte-check-pre-push
description: Protocol for running svelte-check validation and pushing code safely to GitHub on Windows machines.
---

# Svelte-Check & Git Push Protocol

This skill details how to perform pre-push code verification using `svelte-check` on Windows (bypassing execution policy restrictions) and commit/push changes safely to GitHub.

## Verification & Deployment Workflow

### 1. Run Pre-Push Checks
Before staging any changes, run the Svelte diagnostic compiler checks directly using Node to check for type, syntax, or import errors:
```powershell
node node_modules/svelte-check/bin/svelte-check --fail-on-warnings
```

If any compilation errors or unused CSS selectors are found, fix them before proceeding.

### 2. Compile Production Build
Verify that the code compiles into a production bundle successfully:
```powershell
node node_modules/vite/bin/vite.js build
```

### 3. Commit and Push to GitHub
Once both the check and the production build pass, commit the files and push to GitHub:
```powershell
git add .
git commit -m "your commit message"
git push
```
