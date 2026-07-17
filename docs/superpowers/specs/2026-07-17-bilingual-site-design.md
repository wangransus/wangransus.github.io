# Bilingual Chinese-English Site Design

## Goal

Add manually authored Chinese and English versions of the academic homepage with stable URLs, a visible language switch, shared publication data, and no client-side translation or automatic redirect.

## Routes and Language Behavior

The Chinese homepage remains the default route at `/`. The English homepage is published at `/en/`. Both pages are independently renderable and have stable, indexable URLs.

Each page front matter will declare:

```yaml
lang: zh-CN
alternate_url: /en/
```

or:

```yaml
lang: en
alternate_url: /
```

The site will not inspect browser language, redirect visitors automatically, or store language preference in JavaScript. Visitors choose a language through a compact `中文 | EN` control in the masthead. The active language is visually identified and exposed with appropriate accessibility semantics.

## Page Content

`_pages/about.md` remains the manually authored Chinese page. `_pages/about-en.md` becomes the manually authored English equivalent with permalink `/en/`.

The English page will translate:

- profile introduction and research interests;
- news and editorial roles;
- education history;
- section headings;
- research projects;
- honors and awards;
- research-team and recruitment information;
- interface labels and accessibility text.

Both pages preserve the same section order and equivalent anchor IDs so navigation behavior remains predictable. Dates, institutions, names, grants, monetary values, external URLs, and factual details must remain equivalent across languages.

## Publications

`_data/publications.yml` remains the single source of publication data and the display order remains identical on both pages. Publication citations stay in their official published language. Chinese-language citations are not given unofficial English title translations.

`_includes/publications.html` continues to render the shared dataset. It selects localized interface labels from page language:

- Chinese: `网页`, `下载`, and Chinese accessibility labels.
- English: `Article`, `Download`, and English accessibility labels.

Publication badges, citations, images, article URLs, and PDF URLs remain identical across both routes.

## Localized Site Data

Navigation uses two explicit files:

- `_data/navigation.yml` for Chinese;
- `_data/navigation-en.yml` for English.

Both files contain the same number of links in the same order and target equivalent anchors under their respective route prefixes.

A small `_data/locales.yml` file holds short reusable interface/profile strings only. It will contain entries for `zh-CN` and `en`, including:

- profile name;
- profile bio;
- location;
- language-switch labels;
- publication list, article, and download labels;
- navigation and contact accessibility labels.

Long-form page copy does not move into YAML.

## Masthead and Sidebar

The existing greedy navigation component and current visual structure remain. `_includes/masthead.html` chooses Chinese or English navigation according to `page.lang`, prefixes links correctly for `/` or `/en/`, and renders the reciprocal language switch.

The author profile include reads localized name, bio, location, and short labels from `_data/locales.yml`, while shared values such as avatar, email, ORCID, Google Scholar, and ResearchGate remain in `_config.yml`. This avoids duplicating contact URLs and prevents one language from drifting from the other.

The language control must fit the existing navigation on desktop and within the current mobile navigation behavior. It will use text labels rather than flag icons.

## Metadata and SEO

The root document language will come from `page.lang`, with `zh-CN` as the fallback. Each page will emit reciprocal alternate-language links:

```html
<link rel="alternate" hreflang="zh-CN" href="https://wangransus.github.io/">
<link rel="alternate" hreflang="en" href="https://wangransus.github.io/en/">
<link rel="alternate" hreflang="x-default" href="https://wangransus.github.io/">
```

Each page will have localized SEO title, description, and excerpt values. Canonical URLs remain language-specific. The English page will not reuse a Chinese title or description.

## Styling

The language switch will reuse the existing light-polish design language: restrained blue accent, no gradients, no cards, no large new component, and radii no greater than 6px. It must remain legible at desktop and mobile breakpoints without displacing essential navigation.

No other visual redesign is included in this feature.

## Validation

Automated tests will verify:

- both `/` and `/en/` source pages exist with the correct `lang`, permalink, and reciprocal `alternate_url`;
- Chinese and English navigation files have matching lengths, order, and equivalent anchors;
- every locale required by an include exists for both languages;
- the masthead chooses navigation and renders reciprocal language links without JavaScript;
- the author profile resolves localized display values while preserving shared contact URLs;
- both pages include the same publication renderer exactly once;
- the renderer uses shared publication data and language-specific interface labels;
- publication order and field fidelity remain protected by the existing publication contract;
- document language and reciprocal `hreflang` metadata are present;
- referenced images and PDFs remain valid;
- all changed YAML parses as UTF-8 and `git diff --check` passes.

A Jekyll build will be run if Ruby and Bundler are available. If they remain unavailable locally, GitHub Pages will be treated as the integration build and that limitation will be reported before publishing.

## Delivery Boundaries

This feature includes only bilingual routing, translated English page content, localized short UI/profile strings, navigation selection, language switching, metadata, and tests. It does not include automatic translation, browser-language redirect, a translation management service, translated publication titles, or a new theme.

Unrelated working-tree files will not be modified or staged.
