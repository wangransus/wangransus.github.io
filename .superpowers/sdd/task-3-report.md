# Task 3 Report: Chinese and English Page Sources

## Changes

- Updated `_pages/about.md` with the Chinese route language, reciprocal URL, and localized SEO front matter while preserving redirects and body content.
- Added `_pages/about-en.md` at `/en/` with the same author profile behavior, Scholar badge setup, section order, anchors, links, education logos, and single shared publications include.
- Translated the profile, news, education, projects, honors, and research-team prose into professional English without duplicating or translating publication citations.

## Parity Review

- Anchor order matches exactly: `-grjj`, `-zxxx`, `-jybj`, `-kycg`, `-kyxm`, `-ryjl`, `-yjtd`.
- All 13 external URLs match between the Chinese and English pages.
- Education image paths match, and the Scholar badge uses the same Liquid data setup with a localized label.
- Both pages include `{% include publications.html %}` exactly once.
- The English page preserves all dates, institutions, appointments, five project amounts and investigator roles, seven honors, and doctoral-student cohorts and names from 2021 through 2025.

## Test Evidence

Baseline command:

```powershell
python -m unittest tests/test_bilingual.py tests/test_publications.py -v
```

Baseline result: 17 tests run, with four expected failures for the missing Task 3 pages/metadata and the pending Task 4 document-language/hreflang metadata.

Post-implementation result: 17 tests run; all Task 3 page, parity, publication, locale, navigation, and include contracts pass. The only remaining failures are the two Task 4 contracts:

- `test_default_layout_uses_dynamic_page_language_with_chinese_fallback`
- `test_seo_include_emits_real_language_alternate_pairings`

Focused Task 3 verification ran the two page contracts and all five publication contracts: 7 tests passed with no failures.

## Review Amendment

The English page terminology was refined after review:

- Replaced the project and sponsor wording with `Shanghai Sailing Program`, `Eliga Sports Technology Co., Ltd.`, `Huawei Device Co., Ltd.`, and the reviewed winter speed-events title.
- Corrected degree names and concentrations, including singular `Sport Science` and `Sports Training Monitoring`.
- Updated the specially appointed roles, doctoral/master's supervision sentence, JFMK article, and professional master's program wording.
- Rechecked surrounding Markdown and punctuation without changing facts, anchors, dates, amounts, URLs, names, or section order.

Review verification retained one known contract mismatch in addition to the two pending Task 4 failures. The current test still requires the superseded `Sports Science` wording and also contains the old project sponsor markers; tests were not edited because they are outside Task 3 review scope. The focused run completed 7 tests with 6 passing and the stale fact-marker test failing. The full relevant run completed 17 tests with 14 passing and three failures: the stale fact-marker test plus the two pending Task 4 document-language and hreflang tests.
