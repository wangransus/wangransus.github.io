from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ANCHORS = ["-grjj", "-zxxx", "-jybj", "-kycg", "-kyxm", "-ryjl", "-yjtd"]
REQUIRED_LOCALE_KEYS = {
    "profile_name", "profile_bio", "location", "language_name",
    "switch_label", "publications_label", "article_label",
    "download_label", "navigation_label", "contact_label",
}
SECTION_MARKERS = [
    "2006", "2010", "2013", "2017", "2026.04", "2024.04", "2023.11",
    "https://www.ucf.edu/", "https://www.bsu.edu.cn/", "https://jjyd.sus.edu.cn/",
]
FUNDING_VALUE_MARKERS = [r"(?:362\s*万元|3\.62\s*million)", r"(?:50\s*万元|0\.5\s*million)"]
FUNDING_VALUE_MARKERS += [r"(?:20\s*万元|0\.2\s*million)", r"(?:200\s*万元|2\s*million)", r"(?:141\s*万元|1\.41\s*million)"]
BILINGUAL_IMPLEMENTATION_FILES = (
    "_pages/about.md", "_pages/about-en.md", "_includes/masthead.html",
    "_includes/author-profile.html", "_includes/publications.html",
    "_includes/seo.html", "_layouts/default.html",
)
FORBIDDEN_CLIENT_SIDE_LANGUAGE_TOKENS = (
    r"<script\b", r"navigator\.language", r"window\.location",
    r"location\.replace", r"localStorage", r"sessionStorage", r"document\.cookie",
)


def read_utf8(path):
    return path.read_text(encoding="utf-8")


def load_front_matter(path):
    text = read_utf8(path)
    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", text, re.DOTALL)
    if match is None:
        raise AssertionError(f"{path} must begin with YAML front matter")
    return yaml.safe_load(match.group(1)) or {}


def anchors_in(text):
    return re.findall(r"<span\s+class=['\"]anchor['\"]\s+id=['\"]([^'\"]+)", text)


def liquid_value(text, name):
    return rf"{{{{\s*{re.escape(name)}\b[^}}]*}}}}"


class BilingualContractTest(unittest.TestCase):
    def assert_yaml_document(self, path, expected_type):
        self.assertTrue(path.is_file(), f"{path.relative_to(ROOT)} must exist")
        if not path.is_file():
            return None
        document = yaml.safe_load(read_utf8(path))
        self.assertIsInstance(document, expected_type, f"{path.name} must contain YAML {expected_type.__name__}")
        if not isinstance(document, expected_type):
            return None
        return document

    def assert_page_metadata(self, path, expected, language):
        self.assertTrue(path.is_file(), f"{path.relative_to(ROOT)} must exist")
        if not path.is_file():
            return None
        front_matter = load_front_matter(path)
        self.assertIsInstance(front_matter, dict, f"{path.name} front matter must be a mapping")
        if not isinstance(front_matter, dict):
            return None
        for key, value in expected.items():
            self.assertEqual(value, front_matter.get(key), f"{path.name} {key}")
        for key in ("title", "description", "excerpt"):
            value = front_matter.get(key)
            self.assertIsInstance(value, str, f"{path.name} {key} must be text")
            if not isinstance(value, str):
                continue
            self.assertTrue(value.strip(), f"{path.name} {key} must be non-empty")
            if language == "zh-CN":
                self.assertRegex(value, r"[\u3400-\u9fff]", f"{path.name} {key} must contain CJK text")
            else:
                self.assertRegex(value, r"[A-Za-z]", f"{path.name} {key} must contain Latin text")
                self.assertNotRegex(value, r"[\u3400-\u9fff]", f"{path.name} {key} must not contain CJK text")
        return front_matter

    def test_pages_have_bilingual_routes_and_metadata(self):
        self.assert_page_metadata(ROOT / "_pages" / "about.md", {"permalink": "/", "lang": "zh-CN", "alternate_url": "/en/"}, "zh-CN")
        self.assert_page_metadata(ROOT / "_pages" / "about-en.md", {"permalink": "/en/", "lang": "en", "alternate_url": "/"}, "en")

    def test_pages_have_matching_sections_facts_and_one_publication_include(self):
        page_paths = [ROOT / "_pages" / name for name in ("about.md", "about-en.md")]
        for path in page_paths:
            self.assertTrue(path.is_file(), f"{path.relative_to(ROOT)} must exist")
        if not all(path.is_file() for path in page_paths):
            return
        pages = [read_utf8(path) for path in page_paths]
        anchor_sequences = []
        heading_sequences = []
        for page in pages:
            anchor_sequences.append([anchor for anchor in anchors_in(page) if anchor in EXPECTED_ANCHORS])
            self.assertEqual(1, page.count("{% include publications.html %}"))
            headings = []
            for anchor in EXPECTED_ANCHORS:
                heading_match = re.search(rf"id=['\"]{re.escape(anchor)}['\"]\s*></span>\s*\n\s*#\s+([^\n]+)", page)
                self.assertIsNotNone(heading_match, f"section {anchor} must have a following heading")
                if heading_match is not None:
                    headings.append(heading_match.group(1).strip())
            heading_sequences.append(headings)
            for marker in SECTION_MARKERS:
                self.assertIn(marker, page, f"page must preserve factual marker {marker}")
            for marker in FUNDING_VALUE_MARKERS:
                self.assertRegex(page, marker, f"page must preserve funding value {marker}")
        self.assertEqual([EXPECTED_ANCHORS, EXPECTED_ANCHORS], anchor_sequences)
        self.assertEqual(len(heading_sequences[0]), len(heading_sequences[1]))

    def test_navigation_datasets_match_page_anchors_and_routes(self):
        paths = [ROOT / "_data" / name for name in ("navigation.yml", "navigation-en.yml")]
        navigation = [self.assert_yaml_document(path, dict) for path in paths]
        if any(data is None for data in navigation):
            return
        mains = []
        for data, path in zip(navigation, paths):
            self.assertIn("main", data, f"{path.name} must expose main")
            self.assertIsInstance(data.get("main"), list, f"{path.name}.main must be a list")
            if not isinstance(data.get("main"), list):
                return
            for item in data["main"]:
                self.assertIsInstance(item, dict, f"{path.name} navigation entries must be mappings")
                if not isinstance(item, dict):
                    continue
                self.assertIsInstance(item.get("title"), str, f"{path.name} titles must be strings")
                self.assertIsInstance(item.get("url"), str, f"{path.name} URLs must be strings")
            mains.append(data["main"])
        if any(not isinstance(item, dict) or not isinstance(item.get("url"), str) for main in mains for item in main):
            return
        self.assertEqual(len(mains[0]), len(mains[1]))
        anchor_sequences = []
        for main in mains:
            anchors = []
            for item in main:
                match = re.search(r"#([^\s]+)$", item["url"])
                self.assertIsNotNone(match, f"navigation URL must target an anchor: {item['url']}")
                if match is not None:
                    anchors.append(match.group(1))
            anchor_sequences.append(anchors)
        self.assertEqual(EXPECTED_ANCHORS, anchor_sequences[0])
        self.assertEqual(EXPECTED_ANCHORS, anchor_sequences[1])
        self.assertTrue(all(item["url"].startswith("/") and not item["url"].startswith("/en/") for item in mains[0]))
        self.assertTrue(all(item["url"].startswith("/en/") for item in mains[1]))

    def test_locale_data_has_required_locales_and_non_empty_display_strings(self):
        locales = self.assert_yaml_document(ROOT / "_data" / "locales.yml", dict)
        if locales is None:
            return
        self.assertEqual({"zh-CN", "en"}, set(locales))
        for language in ("zh-CN", "en"):
            self.assertIsInstance(locales.get(language), dict, f"{language} locale must be a mapping")
            if not isinstance(locales.get(language), dict):
                continue
            self.assertTrue(REQUIRED_LOCALE_KEYS.issubset(locales[language]), f"{language} locale is missing required keys")
            for key in REQUIRED_LOCALE_KEYS:
                value = locales[language].get(key)
                self.assertIsInstance(value, str, f"{language}.{key} must be a string")
                if isinstance(value, str):
                    self.assertTrue(value.strip(), f"{language}.{key} must be non-empty")

    def test_bilingual_implementation_has_no_client_side_language_detection_or_redirects(self):
        for relative_path in BILINGUAL_IMPLEMENTATION_FILES:
            path = ROOT / relative_path
            if not path.is_file():
                continue
            text = read_utf8(path)
            for token in FORBIDDEN_CLIENT_SIDE_LANGUAGE_TOKENS:
                self.assertNotRegex(text, token, f"{relative_path} must not use {token}")

    def test_masthead_has_localized_navigation_branch_and_real_language_link(self):
        masthead = read_utf8(ROOT / "_includes" / "masthead.html")
        self.assertRegex(masthead, r"{%\s*assign\s+page_lang\s*=\s*page\.lang\s*\|\s*default\s*:\s*['\"]zh-CN['\"]\s*%}")
        self.assertRegex(masthead, r"{%\s*if\s+page_lang\s*==\s*['\"]en['\"]\s*%}[\s\S]*?site\.data\[['\"]navigation-en['\"]\]\.main")
        self.assertRegex(masthead, r"{%\s*else\s*%}[\s\S]*?site\.data\.navigation\.main")
        switch_match = re.search(r"<a\b(?P<attrs>[^>]*)class\s*=\s*['\"][^'\"]*\blanguage-switch\b[^'\"]*['\"][^>]*>(?P<body>[\s\S]*?)</a>", masthead)
        self.assertIsNotNone(switch_match, "masthead must emit a language-switch anchor")
        if switch_match is None:
            return
        switch = switch_match.group(0)
        self.assertRegex(switch, r"href\s*=\s*['\"][^'\"]*\{\{\s*page\.alternate_url\b[^}]*\}\}")
        self.assertRegex(switch, r"hreflang\s*=\s*['\"][^'\"]+['\"]")
        self.assertRegex(switch, r"aria-label\s*=\s*['\"]\{\{\s*locale\.switch_label\b[^}]*\}\}")

    def test_profile_interpolates_localized_fields_and_keeps_shared_author_contacts(self):
        profile = read_utf8(ROOT / "_includes" / "author-profile.html")
        self.assertRegex(profile, r"{%\s*assign\s+locale\s*=\s*site\.data\.locales\[")
        for key in ("profile_name", "profile_bio", "location"):
            self.assertRegex(profile, liquid_value(f"locale.{key}"))
        self.assertRegex(profile, r"{%\s*assign\s+author\s*=\s*site\.author\s*%}")
        self.assertRegex(profile, r"author\.avatar")
        self.assertRegex(profile, r"author\.(?:email|uri|github|researchgate)")

    def test_publications_localizes_attributes_and_links_inside_real_loop(self):
        publications = read_utf8(ROOT / "_includes" / "publications.html")
        loop_match = re.search(r"{%\s*for\s+publication\s+in\s+site\.data\.publications\s*%}(?P<body>[\s\S]*?){%\s*endfor\s*%}", publications)
        self.assertIsNotNone(loop_match, "publications include must loop over site.data.publications")
        self.assertRegex(publications, r"<section\b[^>]*aria-label\s*=\s*['\"]\{\{\s*locale\.publications_label\b[^}]*\}\}")
        if loop_match is None:
            return
        loop_body = loop_match.group("body")
        self.assertRegex(loop_body, liquid_value("locale.article_label"))
        self.assertRegex(loop_body, liquid_value("locale.download_label"))

    def test_default_layout_uses_dynamic_page_language_with_chinese_fallback(self):
        layout = read_utf8(ROOT / "_layouts" / "default.html")
        html_match = re.search(r"<html\b(?P<attrs>[^>]*)>", layout)
        self.assertIsNotNone(html_match)
        if html_match is None:
            return
        self.assertRegex(html_match.group("attrs"), r"lang\s*=\s*['\"]\{\{\s*page\.lang\s*\|\s*default\s*:\s*['\"]zh-CN['\"]\s*\}\}")

    def test_seo_include_emits_real_language_alternate_pairings(self):
        seo = read_utf8(ROOT / "_includes" / "seo.html")
        for language, route in (("zh-CN", r"/"), ("en", r"/en/"), ("x-default", r"/")):
            pattern = rf"<link\b(?=[^>]*\brel\s*=\s*['\"]alternate['\"])(?=[^>]*\bhreflang\s*=\s*['\"]{re.escape(language)}['\"])(?=[^>]*\bhref\s*=\s*[^>]*{re.escape(route)})[^>]*>"
            self.assertRegex(seo, pattern, f"SEO must pair {language} with {route}")


if __name__ == "__main__":
    unittest.main()
