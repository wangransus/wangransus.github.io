# Bilingual Chinese-English Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish manually authored Chinese and English versions of the academic homepage at `/` and `/en/`, with shared publications, localized navigation/profile labels, reciprocal language switching, and bilingual SEO metadata.

**Architecture:** Keep `_pages/about.md` as the Chinese source and add `_pages/about-en.md` as an independently authored English source. Short reusable strings live in `_data/locales.yml`; navigation remains explicit in `_data/navigation.yml` and `_data/navigation-en.yml`; existing includes select data through `page.lang`. Publications remain one shared ordered dataset.

**Tech Stack:** Jekyll, Liquid, YAML, Markdown, SCSS, Python 3 unittest, PyYAML

## Global Constraints

- Chinese remains at `/`; English is published at `/en/`.
- Do not use JavaScript language detection, automatic redirects, browser-language persistence, or a multilingual plugin.
- Keep the current Minimal Mistakes layout, light-polish styling, university identity, section order, and publication order.
- Publication citations remain in their official published language and are not translated.
- Long-form Chinese and English page copy stays in Markdown pages, not locale YAML.
- Shared contact URLs remain in `_config.yml`; locale data contains display strings only.
- Both pages use equivalent anchors, facts, dates, institutions, names, grants, monetary values, and external links.
- Unrelated working-tree files must not be modified or staged.

---

### Task 1: Bilingual Contract Tests

**Files:**
- Create: `tests/test_bilingual.py`
- Test: `tests/test_bilingual.py`

**Interfaces:**
- Consumes: bilingual pages, navigation data, locale data, masthead/profile/publication/SEO includes, default layout
- Produces: a repeatable structural contract for routes, language parity, localization, and metadata

- [ ] **Step 1: Write the failing bilingual contract**

Create `tests/test_bilingual.py` using `unittest`, `pathlib`, `re`, and `yaml.safe_load`. Define `ROOT`, a UTF-8 file reader, and a front-matter loader. Add tests that require:

```python
EXPECTED_ANCHORS = ["-grjj", "-zxxx", "-jybj", "-kycg", "-kyxm", "-ryjl", "-yjtd"]
REQUIRED_LOCALE_KEYS = {
    "profile_name", "profile_bio", "location", "language_name",
    "switch_label", "publications_label", "article_label",
    "download_label", "navigation_label", "contact_label",
}
```

The tests must assert:

- `_pages/about.md` has `permalink: /`, `lang: zh-CN`, `alternate_url: /en/`, a non-empty Chinese `title`, `description`, and `excerpt`;
- `_pages/about-en.md` has `permalink: /en/`, `lang: en`, `alternate_url: /`, and non-empty English `title`, `description`, and `excerpt`;
- both pages contain `EXPECTED_ANCHORS` in the same order and include `{% include publications.html %}` exactly once;
- `_data/navigation.yml` and `_data/navigation-en.yml` each expose `main`, have equal lengths, and target equivalent anchors under `/` and `/en/`;
- `_data/locales.yml` contains exactly `zh-CN` and `en`, with every `REQUIRED_LOCALE_KEYS` value present and non-empty;
- `_includes/masthead.html` reads `page.lang`, selects `navigation-en` for English, keeps `navigation` for Chinese, uses `page.alternate_url`, and emits a language-switch class without JavaScript;
- `_includes/author-profile.html` reads localized profile fields while continuing to use `site.author` for avatar and contact URLs;
- `_includes/publications.html` reads localized list, article, and download labels and still loops over `site.data.publications`;
- `_layouts/default.html` sets `<html lang>` from `page.lang` with a `zh-CN` fallback;
- `_includes/seo.html` emits `hreflang="zh-CN"`, `hreflang="en"`, and `hreflang="x-default"` using language-specific URLs.

- [ ] **Step 2: Run the contract to verify RED**

Run:

```powershell
python -m unittest tests/test_bilingual.py -v
```

Expected: FAIL because the English page, English navigation, locale data, bilingual front matter, localized includes, document language, and alternate metadata do not yet exist.

- [ ] **Step 3: Commit the failing contract**

```powershell
git add -- tests/test_bilingual.py
git commit -m "Add bilingual site contract tests"
```

### Task 2: Locale Data, Navigation, and Shared Includes

**Files:**
- Create: `_data/locales.yml`
- Create: `_data/navigation-en.yml`
- Modify: `_data/navigation.yml`
- Modify: `_includes/masthead.html`
- Modify: `_includes/author-profile.html`
- Modify: `_includes/publications.html`
- Modify: `assets/css/main.scss`
- Test: `tests/test_bilingual.py`
- Test: `tests/test_publications.py`

**Interfaces:**
- Consumes: `page.lang`, `page.alternate_url`, `site.author`, and shared publication data
- Produces: `locale`, `navigation`, localized profile values, bilingual publication labels, and the visible language control

- [ ] **Step 1: Create the locale data**

Create `_data/locales.yml` with exactly this structure:

```yaml
zh-CN:
  profile_name: "王然 博士"
  profile_bio: "上海体育大学"
  location: "中国·上海"
  language_name: "中文"
  switch_label: "切换语言"
  publications_label: "科研成果列表"
  article_label: "网页"
  download_label: "下载"
  navigation_label: "主导航"
  contact_label: "联系方式"
en:
  profile_name: "Ran Wang, PhD"
  profile_bio: "Shanghai University of Sport"
  location: "Shanghai, China"
  language_name: "EN"
  switch_label: "Switch language"
  publications_label: "Publication list"
  article_label: "Article"
  download_label: "Download"
  navigation_label: "Primary navigation"
  contact_label: "Contact information"
```

- [ ] **Step 2: Create matching navigation datasets**

Keep Chinese navigation under `main` and ensure it contains these anchors in order: `-grjj`, `-zxxx`, `-jybj`, `-kycg`, `-kyxm`, `-ryjl`, `-yjtd`. Add the missing Chinese 科研项目 item if necessary.

Create `_data/navigation-en.yml`:

```yaml
main:
  - title: "Profile"
    url: "/en/#-grjj"
  - title: "News"
    url: "/en/#-zxxx"
  - title: "Education"
    url: "/en/#-jybj"
  - title: "Publications"
    url: "/en/#-kycg"
  - title: "Projects"
    url: "/en/#-kyxm"
  - title: "Honors"
    url: "/en/#-ryjl"
  - title: "Team"
    url: "/en/#-yjtd"
```

- [ ] **Step 3: Localize masthead selection and language switching**

At the top of `_includes/masthead.html`, assign a language fallback, locale, and navigation:

```liquid
{% assign page_lang = page.lang | default: "zh-CN" %}
{% assign locale = site.data.locales[page_lang] | default: site.data.locales["zh-CN"] %}
{% if page_lang == "en" %}
  {% assign navigation = site.data["navigation-en"].main %}
{% else %}
  {% assign navigation = site.data.navigation.main %}
{% endif %}
```

Use `navigation` in the existing greedy-nav loop. Add an internal link with class `language-switch`, `href="{{ page.alternate_url | default: '/en/' | relative_url }}"`, `hreflang` equal to the alternate language, an accessible label from `locale.switch_label`, and visible text `EN` on Chinese pages or `中文` on English pages. Preserve the existing logo and greedy-nav button.

- [ ] **Step 4: Localize the author profile**

In `_includes/author-profile.html`, assign `page_lang` and `locale` as above. Keep `author = site.author` for shared avatar and URLs. Replace displayed `author.name`, `author.bio`, `author.location`, and the description line with localized equivalents. Add `aria-label="{{ locale.contact_label | escape }}"` to the contact list. Do not duplicate or relocate contact URLs.

- [ ] **Step 5: Localize publication UI labels**

In `_includes/publications.html`, assign locale from `page.lang`, change the section `aria-label` to `locale.publications_label`, and replace hard-coded link text with `locale.article_label` and `locale.download_label`. Keep the publication loop, citation `markdownify`, escaping, and URLs unchanged.

- [ ] **Step 6: Style the language switch**

Append focused `.language-switch` rules to the existing `Light polish` SCSS section. Use the current `#00369f` accent, compact padding, a border radius no greater than 6px, visible focus, and mobile wrapping compatible with greedy-nav. Do not introduce cards, gradients, flags, or layout restructuring.

- [ ] **Step 7: Run focused tests**

Run:

```powershell
python -m unittest tests/test_bilingual.py tests/test_publications.py -v
```

Expected: publication tests PASS; bilingual tests still fail only for missing page front matter, English content, document language, and SEO alternates.

- [ ] **Step 8: Commit shared localization infrastructure**

```powershell
git add -- _data/locales.yml _data/navigation.yml _data/navigation-en.yml _includes/masthead.html _includes/author-profile.html _includes/publications.html assets/css/main.scss
git commit -m "Add shared bilingual navigation and labels"
```

### Task 3: Chinese and English Page Sources

**Files:**
- Modify: `_pages/about.md`
- Create: `_pages/about-en.md`
- Test: `tests/test_bilingual.py`
- Test: `tests/test_publications.py`

**Interfaces:**
- Consumes: shared navigation, locale data, and publication include
- Produces: stable `/` and `/en/` page sources with equivalent anchors and facts

- [ ] **Step 1: Add localized Chinese front matter**

Update `_pages/about.md` front matter to include:

```yaml
permalink: /
lang: zh-CN
alternate_url: /en/
title: "王然 | 上海体育大学"
description: "竞技运动科学、体能训练与运动表现评估"
excerpt: "上海体育大学王然博士的学术主页"
author_profile: true
```

Preserve its redirects, Liquid citation setup, anchors, body content, external links, and publication include.

- [ ] **Step 2: Create the English page**

Create `_pages/about-en.md` with this front matter:

```yaml
permalink: /en/
lang: en
alternate_url: /
title: "Ran Wang | Shanghai University of Sport"
description: "Sport science, strength and conditioning, and performance assessment"
excerpt: "Academic profile of Ran Wang at Shanghai University of Sport"
author_profile: true
```

Use the same Google Scholar badge Liquid setup as the Chinese page. Create sections with the same anchors and order:

- `# Profile`: Professor of Physical Education and Training; doctoral and master's supervisor; program director for Strength and Conditioning; research in performance testing and assessment, training-load planning and monitoring, and coaching strategies; list the same seven professional appointments in accurate English.
- `# News`: retain the three dated JFMK and editorial-board announcements and URLs.
- `# Education`: translate the three UCF and Beijing Sport University degrees, dates, fields, directions, supervisors, logos, and URLs without changing facts.
- `# Publications`: include `{% include publications.html %}` exactly once with no duplicated publication data.
- `# Research Projects`: translate all five project names while retaining funding agencies, values of RMB 3.62 million, 0.5 million, 0.2 million, 2 million, and 1.41 million, and the role Principal Investigator.
- `# Honors and Awards`: translate all seven entries while preserving dates, awarding organizations, and official English award names where already English.
- `# Research Team`: translate recruitment directions and the doctoral-student cohorts from 2021 through 2025, preserving every personal name in standard romanization or established English spelling.

Do not translate publication citations, institution names that have official English forms incorrectly, personal identities, dates, URLs, or monetary values.

- [ ] **Step 3: Run page parity tests**

Run:

```powershell
python -m unittest tests/test_bilingual.py tests/test_publications.py -v
```

Expected: route, front matter, anchor parity, publication parity, locale, and navigation tests PASS; document-language and SEO tests remain failing until Task 4.

- [ ] **Step 4: Commit page sources**

```powershell
git add -- _pages/about.md _pages/about-en.md
git commit -m "Add English academic homepage"
```

### Task 4: Document Language and Alternate Metadata

**Files:**
- Modify: `_layouts/default.html`
- Modify: `_includes/seo.html`
- Test: `tests/test_bilingual.py`

**Interfaces:**
- Consumes: `page.lang`, `page.url`, and `page.alternate_url`
- Produces: correct document language, canonical URL behavior, and reciprocal alternate-language metadata

- [ ] **Step 1: Set document language from front matter**

Change the opening element in `_layouts/default.html` to:

```liquid
<html lang="{{ page.lang | default: 'zh-CN' }}" class="no-js">
```

- [ ] **Step 2: Emit reciprocal hreflang links**

In `_includes/seo.html`, after the canonical link, assign `seo_url` as the existing include already does and emit fixed route alternates when `page.lang` is `zh-CN` or `en`:

```liquid
{% if page.lang == "zh-CN" or page.lang == "en" %}
  <link rel="alternate" hreflang="zh-CN" href="{{ '/' | prepend: seo_url }}">
  <link rel="alternate" hreflang="en" href="{{ '/en/' | prepend: seo_url }}">
  <link rel="alternate" hreflang="x-default" href="{{ '/' | prepend: seo_url }}">
{% endif %}
```

Preserve the existing language-specific canonical URL generated from `page.url`.

- [ ] **Step 3: Run all contracts**

Run:

```powershell
python -m unittest tests/test_bilingual.py tests/test_publications.py -v
git diff --check
```

Expected: every bilingual and publication test passes; diff check exits 0.

- [ ] **Step 4: Attempt the Jekyll build**

Run:

```powershell
bundle exec jekyll build
```

Expected: exit 0 and generated `_site/index.html` plus `_site/en/index.html`. If Ruby/Bundler is unavailable, report the limitation and use GitHub Pages as the integration build after publishing.

- [ ] **Step 5: Commit metadata support**

```powershell
git add -- _layouts/default.html _includes/seo.html
git commit -m "Add bilingual document metadata"
```

### Task 5: Final Review and Publishing Readiness

**Files:**
- Review: all files changed in Tasks 1-4

**Interfaces:**
- Consumes: completed bilingual implementation and test evidence
- Produces: a reviewed branch ready for explicit merge or PR authorization

- [ ] **Step 1: Review the complete feature diff**

Compare the feature branch against its base and confirm only the planned bilingual files and tests changed. Verify Chinese text remains valid UTF-8, English content contains no mojibake or untranslated interface labels, both navigation files have seven links, and publication data is unchanged.

- [ ] **Step 2: Run final verification**

Run:

```powershell
python -m unittest tests/test_bilingual.py tests/test_publications.py -v
git diff --check
git status --short --branch
```

Expected: all tests PASS, diff check exits 0, and the branch is clean except for known unrelated files outside an isolated worktree.

- [ ] **Step 3: Review generated output when available**

If `_site` was generated, verify both files exist and contain their expected language and alternate metadata:

```powershell
Test-Path _site/index.html
Test-Path _site/en/index.html
Select-String -Path _site/index.html -Pattern 'lang="zh-CN"','hreflang="en"'
Select-String -Path _site/en/index.html -Pattern 'lang="en"','hreflang="zh-CN"'
```

- [ ] **Step 4: Publish only after explicit authorization**

Do not push, merge, or create a pull request until the user chooses the branch-completion workflow.
