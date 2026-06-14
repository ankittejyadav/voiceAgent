---
name: design
description: Guidelines for eliminating external icon dependencies and custom SVG markup in favor of stable CSS shapes, text placeholders, or the central Icon component.
---

# Design & Icon Simplification Guidelines

To prevent compilation breaks (such as missing exports in third-party icon libraries like `lucide-svelte`), this skill establishes a protocol for replacing package-dependent icons and complex inline SVGs with simple, pure CSS and HTML alternatives.

## Protocol for Icon Replacement

When refactoring pages to remove external icon dependencies:

### 1. Brand Logo Replacement (CSS/Text Placeholders)
Instead of importing brand-specific SVGs (which can change or break between library versions), replace brand logos with stylized CSS containers displaying the first letter of the vendor or a clean text tag.

**Before (Package Import / Custom SVG):**
```html
<script>
  import GithubIcon from "lucide-svelte/dist/icons/github";
</script>

<div class="logo">
  <GithubIcon size={24} />
</div>
```

**After (Simplified CSS Initials):**
```html
<div class="logo-fallback" style="background: var(--brand-color);">
  <span>G</span>
</div>
```

### 2. Standardize on Centralized Material Symbols
If a functional UI icon is strictly necessary (e.g. settings cog, checkmark, close cross), use the project's centralized [Icon.svelte](file:///C:/Users/ankit.yadav2/Documents/selfhost/src/lib/ui/Icon.svelte) component.
* Avoid importing individual icons from `lucide-svelte` or any external package.
* Use: `<Icon name="settings" size={18} />`

### 3. Verification Steps
After removing icon imports, always run:
1. Sveltekit Sync:
   `node node_modules/@sveltejs/kit/svelte-kit sync`
2. Vite Build Check:
   `node node_modules/vite/bin/vite.js build`
