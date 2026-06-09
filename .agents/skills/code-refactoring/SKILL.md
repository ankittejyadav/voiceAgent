---
name: code-refactoring
description: >-
  Enforces systematic dead code removal, dependency cleanup, and filesystem
  hygiene during codebase refactoring tasks.
---

# Code Refactoring Rules

This skill defines mandatory procedures when refactoring code in this project.

## Dead Library Removal

1. **Verify before removing:** Search the **entire codebase** (src, scripts, tests, config files) to confirm zero imports/requires of the library before removing it.
2. **Use `npm uninstall`:** Always use `npm uninstall <package>` to remove a dependency. This removes it from both `package.json` and `node_modules/` in one step. Do **not** manually edit `package.json` for dependency removal.
3. **Delete associated code:** After uninstalling, delete any source files that solely existed to wrap or use that library (utility modules, test files for those modules).

## Dead Code Removal

4. **Confirm zero references:** Before deleting any file, function, or type, grep the full project to confirm it has no imports, references, or usages elsewhere.
5. **Remove dead types:** If a TypeScript interface or type is defined but never imported or referenced by any file, remove it.
6. **Remove dead exports:** If a function is exported but never imported anywhere outside its own file/test, remove it.

## Filesystem Hygiene

7. **Empty folder cleanup:** After deleting files, check if the parent directory is now empty. If so, remove the empty directory. Repeat upward until a non-empty parent is reached.
8. **No orphaned test files:** If a source file is deleted, its corresponding test file must also be deleted.
