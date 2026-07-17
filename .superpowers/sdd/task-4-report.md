# Task 4 Report: Document Language and Alternate Metadata

## Summary

- `_layouts/default.html` now derives the document language from `page.lang` and falls back to `zh-CN`.
- `_includes/seo.html` maps `page.url` and `page.alternate_url` to Chinese and English paths according to `page.lang`.
- The SEO include emits one absolute `zh-CN` alternate and one absolute `en` alternate for bilingual pages, while retaining the approved `x-default` root alternate.
- Existing canonical, Open Graph, Twitter, verification, and include behavior remains in place.
- No JavaScript locale detection, redirect, persistence, plugin, or unrelated file change was added.

## Test Evidence

Baseline command:

```powershell
python -B -m unittest tests/test_bilingual.py tests/test_publications.py -v
```

Baseline result: 17 tests ran; 15 passed and the two expected Task 4 contracts failed for the static `lang="en"` value and missing hreflang links.

Post-implementation result: 17 tests ran and all 17 passed.

Whitespace verification:

```powershell
git diff --check
```

Result: exit 0 with no output.

## Build Attempt

```powershell
bundle exec jekyll build
```

The local integration build could not run because PowerShell could not find the `bundle` command. Per the implementation plan, GitHub Pages remains the integration build environment.

## Files

- `_layouts/default.html`
- `_includes/seo.html`
- `.superpowers/sdd/task-4-report.md`

Commit subject: `Add bilingual document and SEO metadata`
