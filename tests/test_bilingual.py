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


class BilingualContractTest(unittest.TestCase):
    def test_pages_have_bilingual_routes_and_metadata(self):
        pages = {
            "zh-CN": ROOT / "_pages" / "about.md",
            "en": ROOT / "_pages" / "about-en.md",
        }
        expected = {
            "zh-CN": {"permalink": "/", "lang": "zh-CN", "alternate_url": "/en/"},
            "en": {"permalink": "/en/", "lang": "en", "alternate_url": "/"},
        }

        for language, path in pages.items():
            self.assertTrue(path.is_file(), f"{path.relative_to(ROOT)} must exist")
            if not path.is_file():
                continue
            front_matter = load_front_matter(path)
            for key, value in expected[language].items():
                self.assertEqual(value, front_matter.get(key), f"{path.name} {key}")
            for key in ("title", "description", "excerpt"):
                value = front_matter.get(key)
                self.assertIsInstance(value, str, f"{path.name} {key} must be text")
                self.assertTrue(value.strip(), f"{path.name} {key} must be non-empty")
            if language == "zh-CN":
                self.assertRegex(front_matter["title"], r"[\u3400-\u9fff]")
            else:
                self.assertRegex(front_matter["title"], r"[A-Za-z]")

    def test_pages_have_matching_anchors_and_one_publication_include(self):
        page_paths = [ROOT / "_pages" / name for name in ("about.md", "about-en.md")]
        for path in page_paths:
            self.assertTrue(path.is_file(), f"{path.relative_to(ROOT)} must exist")
        if not all(path.is_file() for path in page_paths):
            return
        pages = [read_utf8(path) for path in page_paths]
        for page in pages:
            self.assertEqual(EXPECTED_ANCHORS, [anchor for anchor in anchors_in(page) if anchor in EXPECTED_ANCHORS])
            self.assertEqual(1, page.count("{% include publications.html %}"))

    def test_navigation_datasets_match_page_anchors_and_routes(self):
        navigation_paths = [ROOT / "_data" / name for name in ("navigation.yml", "navigation-en.yml")]
        for path in navigation_paths:
            self.assertTrue(path.is_file(), f"{path.relative_to(ROOT)} must exist")
        if not all(path.is_file() for path in navigation_paths):
            return
        navigation = [yaml.safe_load(read_utf8(path)) for path in navigation_paths]
        for data, path in zip(navigation, navigation_paths):
            self.assertIsInstance(data, dict, f"{path.name} must be a mapping")
            self.assertIn("main", data, f"{path.name} must expose main")

        chinese, english = navigation
        chinese_main = chinese.get("main", [])
        english_main = english.get("main", [])
        self.assertEqual(len(chinese_main), len(english_main))
        chinese_anchors = [re.search(r"#([^\s]+)$", item.get("url", "")).group(1) for item in chinese_main]
        english_anchors = [re.search(r"#([^\s]+)$", item.get("url", "")).group(1) for item in english_main]
        self.assertEqual(EXPECTED_ANCHORS, chinese_anchors)
        self.assertEqual(EXPECTED_ANCHORS, english_anchors)
        self.assertTrue(all(item["url"].startswith("/") and not item["url"].startswith("/en/") for item in chinese_main))
        self.assertTrue(all(item["url"].startswith("/en/") for item in english_main))

    def test_locale_data_has_exact_locales_and_required_values(self):
        locale_path = ROOT / "_data" / "locales.yml"
        self.assertTrue(locale_path.is_file(), "_data/locales.yml must exist")
        if not locale_path.is_file():
            return
        locales = yaml.safe_load(read_utf8(locale_path))
        self.assertEqual({"zh-CN", "en"}, set(locales))
        for language in ("zh-CN", "en"):
            self.assertEqual(REQUIRED_LOCALE_KEYS, set(locales[language]))
            for key, value in locales[language].items():
                self.assertIsInstance(value, str)
                self.assertTrue(value.strip(), f"{language}.{key} must be non-empty")

    def test_masthead_selects_localized_navigation_and_switches_without_javascript(self):
        masthead = read_utf8(ROOT / "_includes" / "masthead.html")
        self.assertRegex(masthead, r"page\.lang")
        self.assertRegex(masthead, r"navigation-en")
        self.assertRegex(masthead, r"site\.data\.navigation(?:\.main|\b)")
        self.assertRegex(masthead, r"page\.alternate_url")
        self.assertIn("language-switch", masthead)
        self.assertNotRegex(masthead, r"(?i)javascript")

    def test_profile_uses_localized_fields_and_shared_author_contacts(self):
        profile = read_utf8(ROOT / "_includes" / "author-profile.html")
        self.assertRegex(profile, r"site\.data\.locales")
        for key in ("profile_name", "profile_bio", "location"):
            self.assertIn(key, profile)
        self.assertRegex(profile, r"site\.author")
        self.assertRegex(profile, r"author\.avatar")
        self.assertRegex(profile, r"author\.(?:email|uri|github|researchgate)")

    def test_publications_uses_localized_labels_and_shared_data(self):
        publications = read_utf8(ROOT / "_includes" / "publications.html")
        for key in ("publications_label", "article_label", "download_label"):
            self.assertIn(key, publications)
        self.assertRegex(publications, r"for\s+publication\s+in\s+site\.data\.publications")

    def test_default_layout_uses_page_language_with_chinese_fallback(self):
        layout = read_utf8(ROOT / "_layouts" / "default.html")
        self.assertRegex(layout, r"<html\s+lang=\"\{\{\s*page\.lang\s*\|\s*default:\s*['\"]zh-CN['\"]\s*\}\}")

    def test_seo_include_emits_language_alternates(self):
        seo = read_utf8(ROOT / "_includes" / "seo.html")
        for language in ("zh-CN", "en", "x-default"):
            self.assertIn(f'hreflang="{language}"', seo)
        self.assertRegex(seo, r"hreflang=\"zh-CN\"[\s\S]*?['\"]\/['\"]")
        self.assertRegex(seo, r"hreflang=\"en\"[\s\S]*?['\"]\/en\/['\"]")
        self.assertRegex(seo, r"hreflang=\"x-default\"[\s\S]*?['\"]\/['\"]")


if __name__ == "__main__":
    unittest.main()
