# Light Polish and Structured Publications Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply a restrained visual polish to the existing academic homepage and render its 20 publications from one ordered YAML data file.

**Architecture:** Preserve the current Minimal Mistakes layout and content hierarchy. Store publication display data in `_data/publications.yml`, render it through `_includes/publications.html`, and keep presentation changes in focused SCSS overrides. A Python unittest validates the data-to-template contract and local asset references.

**Tech Stack:** Jekyll, Liquid, YAML, SCSS, Python 3 unittest, PyYAML

## Global Constraints

- Keep the existing page order, university branding, sidebar-and-content layout, anchors, and restrained blue identity.
- Do not add a hero, citation metric cards, gradients, a replacement navigation system, or new runtime dependencies.
- Keep all 20 publications in their current newest-first display order.
- Use one flat YAML list and preserve citation formatting as Markdown.
- Do not modify or stage unrelated working-tree files.

---

### Task 1: Publication Contract Test

**Files:**
- Create: `tests/test_publications.py`
- Test: `tests/test_publications.py`

**Interfaces:**
- Consumes: `_data/publications.yml`, `_includes/publications.html`, `_pages/about.md`, site-relative asset paths
- Produces: a repeatable structural validation command for the publication migration

- [ ] **Step 1: Write the failing test**

Create `tests/test_publications.py` with tests that load YAML via `yaml.safe_load`, require exactly 20 list items, require the six fields `badge`, `image`, `image_alt`, `citation`, `web_url`, and `pdf_url`, verify unique `(badge, citation)` pairs, verify `/images/...` and `/docs/...` targets exist, require `{% include publications.html %}` exactly once in `_pages/about.md`, reject `paper-box` in `_pages/about.md`, and require the include to iterate over `site.data.publications`, use `markdownify`, and emit `paper-box`, `paper-box-image`, `paper-box-text`, and `badge` classes.

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest tests/test_publications.py -v`

Expected: FAIL because `_data/publications.yml` and `_includes/publications.html` do not exist and the page still contains hand-written `paper-box` blocks.

- [ ] **Step 3: Commit the failing contract test**

```powershell
git add -- tests/test_publications.py
git commit -m "Add publication data contract test"
```

### Task 2: Publication Data and Renderer

**Files:**
- Create: `_data/publications.yml`
- Create: `_includes/publications.html`
- Modify: `_pages/about.md:55`
- Test: `tests/test_publications.py`

**Interfaces:**
- Consumes: the 20 existing publication blocks in `_pages/about.md`
- Produces: `site.data.publications`, rendered by `{% include publications.html %}`

- [ ] **Step 1: Build the ordered YAML data file**

Transcribe each existing block in order into this exact shape:

```yaml
- badge: "Sensors 2026"
  image: "/images/2026Sensors.jpg"
  image_alt: "Sensors article cover"
  citation: >-
    Zhao R, Cong R, Zhou R, Lin K, Yang J, Kui T, Zhang J, **Wang R\***,
    Dong R. Landmine Press Kinematics Measured with an Enhanced YOLOv8 Model
    and Mathematical Modeling[J]. *Sensors*, 2026, 26(4): 1161.
    (通讯作者；SCI期刊)
  web_url: "https://www.mdpi.com/1424-8220/26/4/1161"
  pdf_url: "/docs/2026Sensors.pdf"
```

Apply the same fields to all remaining entries, preserving their existing citation text and links. Convert repository raw PDF links to `/docs/<filename>` where the matching file exists. Correct only the known Sensors article number from `1611` to `1161`.

- [ ] **Step 2: Add the renderer include**

Create `_includes/publications.html`:

```liquid
<div class="publications" aria-label="科研成果列表">
  {% for publication in site.data.publications %}
    <article class="paper-box">
      <div class="paper-box-image">
        <div>
          <div class="badge">{{ publication.badge }}</div>
          <img src="{{ publication.image | relative_url }}" alt="{{ publication.image_alt }}" loading="lazy">
        </div>
      </div>
      <div class="paper-box-text">
        {{ publication.citation | markdownify }}
        <p class="paper-box-links">
          <a href="{{ publication.web_url }}">网页</a>
          <a href="{{ publication.pdf_url | relative_url }}">下载</a>
        </p>
      </div>
    </article>
  {% endfor %}
</div>
```

- [ ] **Step 3: Replace the hand-written blocks**

Delete all repeated publication `<div class='paper-box'>...</div>` blocks below the 科研成果 heading and insert exactly:

```liquid
{% include publications.html %}
```

Keep the following 科研项目 anchor and all later content unchanged.

- [ ] **Step 4: Run the contract test**

Run: `python -m unittest tests/test_publications.py -v`

Expected: all publication contract tests PASS.

- [ ] **Step 5: Commit the migration**

```powershell
git add -- _data/publications.yml _includes/publications.html _pages/about.md
git commit -m "Render publications from structured data"
```

### Task 3: Restrained Visual Polish

**Files:**
- Modify: `_includes/masthead.html`
- Modify: `assets/css/main.scss`
- Test: `tests/test_publications.py`

**Interfaces:**
- Consumes: existing Minimal Mistakes classes and publication renderer classes
- Produces: improved desktop/mobile presentation without changing page architecture

- [ ] **Step 1: Add minimal masthead accessibility markup**

Keep the existing greedy navigation structure. Add `aria-label="Primary navigation"` to its `<nav>`, `aria-label="Toggle navigation"` to its button, `alt="上海体育大学"` to the logo, and `target="_self"` to internal navigation links. Do not replace the navigation component.

- [ ] **Step 2: Add focused SCSS overrides**

Append one documented `Light polish` section to `assets/css/main.scss`. Use the existing blue `#00369f` as the accent and add only rules that:

- constrain readable line length and improve page section spacing;
- reduce masthead shadow, align the logo/navigation, and add subtle hover/focus states;
- refine sidebar avatar, author metadata, and link rhythm;
- give headings a restrained blue underline;
- keep publication rows unframed with consistent cover dimensions, clean borders, and aligned link spacing;
- stack publication image/text and profile/navigation content at the existing small/medium breakpoints;
- use radii no larger than `6px` and avoid gradients or decorative effects.

- [ ] **Step 3: Run structural checks**

Run:

```powershell
python -m unittest tests/test_publications.py -v
git diff --check
```

Expected: all tests PASS and `git diff --check` exits 0.

- [ ] **Step 4: Run the Jekyll build when available**

Run: `bundle exec jekyll build`

Expected: exit 0. If Ruby or Bundler is unavailable, record that limitation and rely on GitHub Pages/Actions for the integration build after push.

- [ ] **Step 5: Commit the polish**

```powershell
git add -- _includes/masthead.html assets/css/main.scss
git commit -m "Apply light homepage polish"
```

### Task 4: Final Review and Publish

**Files:**
- Review: all files changed by Tasks 1-3

**Interfaces:**
- Consumes: the completed implementation and verification output
- Produces: one reviewed branch ready to push to `origin/master`

- [ ] **Step 1: Review the complete diff**

Run `git diff 6f666a9..HEAD -- _data/publications.yml _includes/publications.html _pages/about.md _includes/masthead.html assets/css/main.scss tests/test_publications.py` and confirm there are no unrelated changes, missing publication entries, or mojibake introduced by the migration.

- [ ] **Step 2: Re-run final verification**

Run:

```powershell
python -m unittest tests/test_publications.py -v
git diff --check 6f666a9..HEAD
git status --short --branch
```

Expected: tests PASS; diff check exits 0; only known unrelated untracked files remain outside the commits.

- [ ] **Step 3: Push only after explicit publish authorization**

Run: `git push origin master`

Expected: remote `master` advances to the final implementation commit.
