# Light Polish and Structured Publications Design

## Goal

Improve the academic homepage without changing its familiar structure or identity, and move publication content from repeated HTML blocks into maintainable structured data.

## Visual Direction

The site will retain its current page order, university branding, left author profile, section anchors, written content, and restrained blue identity. The update will refine typography, spacing, navigation alignment, sidebar presentation, publication rows, and responsive behavior.

The update will not add a hero section, citation metric cards, gradients, a new color theme, or a replacement navigation architecture. Desktop will continue to use the existing sidebar-and-content composition. Mobile will stack content cleanly and keep navigation usable without hiding essential profile information.

## Publication Data Model

All 20 publication entries currently embedded in `_pages/about.md` will move to one ordered list in `_data/publications.yml`. The list order is the display order, newest first. Each item will use this schema:

```yaml
- badge: "Sensors 2026"
  image: "/images/2026Sensors.jpg"
  image_alt: "Sensors article cover"
  citation: >-
    Zhao R, Cong R, Zhou R, Lin K, Yang J, Kui T, Zhang J, **Wang R\***,
    Dong R. Landmine Press Kinematics Measured with an Enhanced YOLOv8
    Model and Mathematical Modeling[J]. *Sensors*, 2026, 26(4): 1161.
    (通讯作者；SCI期刊)
  web_url: "https://www.mdpi.com/1424-8220/26/4/1161"
  pdf_url: "/docs/2026Sensors.pdf"
```

Required fields are `badge`, `image`, `image_alt`, `citation`, `web_url`, and `pdf_url`. Citation remains Markdown so emphasis and the highlighted author name can be preserved without splitting bibliographic content into many fields. URLs for repository-hosted images and PDFs will be site-relative. External article links remain absolute.

## Rendering

`_includes/publications.html` will iterate over `site.data.publications` and produce semantic publication entries using the existing `paper-box`, `paper-box-image`, `badge`, and `paper-box-text` classes. Citation Markdown will be rendered with Liquid's `markdownify` filter. Links will be output consistently as `网页` and `下载`.

The repeated publication HTML in `_pages/about.md` will be replaced by one include call directly below the existing 科研成果 heading. No other page content will move into data files.

## Content Fidelity

Migration will preserve the current display order, citation wording, badges, images, webpage links, and PDF links. Only unambiguous defects discovered during migration will be corrected. The known Sensors 2026 article number will change from `1611` to `1161`, matching its article URL.

## Styling Scope

The CSS changes will be appended as focused overrides that work with the existing Minimal Mistakes theme. They will:

- improve base readability and vertical rhythm;
- make the masthead spacing and navigation states more orderly;
- refine the author sidebar without replacing it;
- make publication images consistently sized while preserving their full subject;
- improve citation and link spacing;
- stack sidebar, navigation, and publication rows cleanly on small screens;
- retain compact radii, restrained borders, and minimal shadow.

The masthead markup may receive small accessibility and class-name additions, but its current logo and navigation data source will remain. The page layout and content hierarchy will not be restructured.

## Validation

Automated structural checks will verify:

- `_data/publications.yml` parses and contains exactly 20 entries;
- every entry contains all required fields;
- every site-relative image and PDF path exists;
- `_pages/about.md` contains one publication include and no hand-written `paper-box` blocks;
- the include contains the expected loop and semantic classes;
- YAML and Liquid-facing files remain valid UTF-8;
- the repository passes `git diff --check`.

A Jekyll build will be run when Ruby and Bundler are available. If unavailable locally, the existing GitHub Pages build remains the final integration check, and that limitation will be reported explicitly before publishing.

## Delivery

Implementation will be one focused change set covering publication migration, the renderer include, light CSS polish, minimal masthead accessibility adjustments, and validation. Unrelated working-tree files will not be staged or modified.
