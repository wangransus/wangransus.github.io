# 王然 | 上海体育大学个人主页

This repository powers the academic homepage for Prof. Ran Wang at Shanghai University of Sport:

https://wangransus.github.io/

The site is built with Jekyll and GitHub Pages. It presents a concise academic profile, research interests, publications, funded projects, awards, and team information.

## What Is Included

- One-page academic profile in `_pages/about.md`
- Site metadata and author links in `_config.yml`
- Navigation in `_data/navigation.yml`
- Publication images in `images/`
- Downloadable papers and supporting documents in `docs/`
- Google Scholar citation crawler in `google_scholar_crawler/`
- GitHub Actions workflows for site build checks and citation data refreshes

## Local Development

Install Ruby and Bundler, then run:

```bash
bundle install
bundle exec jekyll serve
```

Open `http://127.0.0.1:4000`.

On Windows, `run_server.sh` is mainly useful from Git Bash or WSL.

## Updating Content

- Edit profile text, news, publications, projects, awards, and team information in `_pages/about.md`.
- Add optimized cover images to `images/`.
- Add downloadable PDFs to `docs/`.
- Update navigation labels or anchors in `_data/navigation.yml`.
- Update title, description, profile links, and verification IDs in `_config.yml`.

## Citation Data

The workflow `.github/workflows/google_scholar_crawler.yaml` reads `GOOGLE_SCHOLAR_ID` from repository Actions secrets and publishes citation JSON to the `google-scholar-stats` branch.

The homepage badge reads:

```text
https://raw.githubusercontent.com/wangransus/wangransus.github.io/google-scholar-stats/gs_data_shieldsio.json
```

## Maintenance Notes

- Run `bundle exec jekyll build` before publishing larger changes.
- Keep images web-sized where possible; large originals and full PDFs make the repository slower to clone.
- Prefer small, descriptive commits for content updates.
