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
CONTACT_KEYS = ("googlescholar", "email", "researchgate", "uri")
BILINGUAL_IMPLEMENTATION_FILES = (
    "_pages/about.md", "_pages/about-en.md", "_includes/masthead.html",
    "_includes/author-profile.html", "_includes/publications.html",
    "_includes/seo.html", "_layouts/default.html",
)
FORBIDDEN_CLIENT_SIDE_LANGUAGE_TOKENS = (
    r"<script\b", r"navigator\.language", r"window\.location",
    r"location\.replace", r"localStorage", r"sessionStorage", r"document\.cookie",
)
FORBIDDEN_LANGUAGE_LOGIC_TOKENS = FORBIDDEN_CLIENT_SIDE_LANGUAGE_TOKENS[1:]
BANNED_MULTILINGUAL_TOKENS = (
    r"jekyll[-_]polyglot", r"jekyll[-_]multiple[-_]languages[-_]plugin",
    r"jekyll[-_]localization", r"jekyll[-_]i18n", r"\bmultilingual\b",
)
PAGE_FACT_MARKERS = {
    "zh-CN": {
        "-grjj": ["上海体育大学竞技运动学院", "中国体育科学学会体能训练分会", "中国田径协会青少年委员会", "上海市体育科学学会体能训练分会", "上海市青少年体育协会体适能分会", "国家体育总局教练员学院", "国家应急管理部重点实验室"],
        "-zxxx": [r"2026\.04", "https://www.mdpi.com/journal/jfmk/special_issues/WY0Z1REVS9", r"2024\.04", "http://www.mechanobiology.cn/yyswlx/news/view/20240428141350001", r"2023\.11", "https://journals.sagepub.com/editorial-board/PIP"],
        "-jybj": [r"2013\.08\s*-\s*2017\.05", "中佛罗里达大学", "运动生理学博士", "Jay Hoffman", "David Fukuda", r"2010\.09\s*-\s*2013\.06", "北京体育大学", "运动人体科学硕士", "胡扬", "邱俊强", r"2006\.09\s*-\s*2010\.06", "运动人体科学学士", "李燕春"],
        "-kyxm": ["科技部国家重点研发计划", r"362\s*万元", "上海市科委地方院校能力建设项目", r"50\s*万元", "上海市科委青年科技英才扬帆计划", r"20\s*万元", "易力加运动科技有限公司", r"200\s*万元", "华为终端有限公司", r"141\s*万元"],
        "-ryjl": [r"2019\.01", "上海市教育委员会", "上海市海外高层次人才", r"2017\.06", "美国体能协会NSCA", "Minority Scholarship", r"2016\.06", "Challenge Scholarship", r"2014\.06", r"2014\.05", "国家留学基金委员会", "国家公派留学奖学金", r"2012\.11", "国家教育部", "硕士研究生国家奖学金", r"2011\.11", "亚太体育科学大会", "Young Graduate Scholars Award"],
        "-yjtd": [r"2025级", "张玮", r"2024级", "谭卓然", r"2023级", "路恒", r"2022级", "唐文静", "萧正邦", r"2021级", "邱翰"],
    },
    "en": {
        "-grjj": ["Shanghai University of Sport", "Chinese Sports Science Society", "Chinese Athletics Association", "Shanghai Sports Science Society", "Shanghai Youth Sports Association", "General Administration of Sport", "Ministry of Emergency Management"],
        "-zxxx": [r"2026\.04", "https://www.mdpi.com/journal/jfmk/special_issues/WY0Z1REVS9", r"2024\.04", "http://www.mechanobiology.cn/yyswlx/news/view/20240428141350001", r"2023\.11", "https://journals.sagepub.com/editorial-board/PIP"],
        "-jybj": [r"2013\.08\s*-\s*2017\.05", "University of Central Florida", "Exercise Physiology", "Jay Hoffman", "David Fukuda", r"2010\.09\s*-\s*2013\.06", "Beijing Sport University", "Sports Science", "Yang Hu", "Junqiang Qiu", r"2006\.09\s*-\s*2010\.06", "Bachelor", "Yanchun Li"],
        "-kyxm": ["Ministry of Science and Technology", "National Key R&D Program", r"3\.62\s*million", "Shanghai Municipal Science and Technology Commission", r"0\.5\s*million", "Youth Science and Technology Talent", r"0\.2\s*million", "Yilijia Sports Technology", r"2\s*million", "Huawei Terminal", r"1\.41\s*million"],
        "-ryjl": [r"2019\.01", "Shanghai Municipal Education Commission", "Overseas High-Level Talent", r"2017\.06", "National Strength and Conditioning Association", "Minority Scholarship", r"2016\.06", "Challenge Scholarship", r"2014\.06", r"2014\.05", "China Scholarship Council", r"2012\.11", "Ministry of Education", "National Scholarship", r"2011\.11", "Asia-Pacific Conference of Sports Science", "Young Graduate Scholars Award"],
        "-yjtd": [r"2025", "Zhang Wei", r"2024", "Tan Zhuoran", r"2023", "Lu Heng", r"2022", "Tang Wenjing", "Xiao Zhengbang", r"2021", "Qiu Han"],
    },
}


def read_utf8(path):
    return path.read_text(encoding="utf-8")


def strip_comments(text):
    text = re.sub(r"{%\s*comment\s*%}[\s\S]*?{%\s*endcomment\s*%}", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\{#[\s\S]*?#\}", "", text)
    return re.sub(r"<!--[\s\S]*?-->", "", text)


def active_source(path):
    return strip_comments(read_utf8(path))


def loaded_script_sources():
    root = ROOT / "_includes" / "scripts.html"
    paths = {root}
    queue = [root]
    while queue:
        path = queue.pop()
        source = active_source(path)
        for include_name in re.findall(r"{%\s*include\s+([^\s%]+)", source):
            include_path = ROOT / "_includes" / include_name
            if include_path.is_file() and include_path not in paths:
                paths.add(include_path)
                queue.append(include_path)
        for source_url in re.findall(r"<script\b[^>]*\bsrc\s*=\s*['\"]([^'\"]+)", source, re.IGNORECASE):
            if re.match(r"(?:[a-z]+:)?//", source_url, re.IGNORECASE):
                continue
            local_path = ROOT / source_url.lstrip("/")
            if local_path.is_file() and local_path not in paths:
                paths.add(local_path)
                queue.append(local_path)
    main_source = ROOT / "assets" / "js" / "_main.js"
    if main_source.is_file():
        paths.add(main_source)
    return sorted(paths)


def load_front_matter(path):
    text = read_utf8(path)
    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", text, re.DOTALL)
    if match is None:
        raise AssertionError(f"{path} must have a YAML front matter block")
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as error:
        raise AssertionError(f"{path} front matter is invalid YAML: {error}") from error


def anchors_in(text):
    return re.findall(r"<span\s+class=['\"]anchor['\"]\s+id=['\"]([^'\"]+)", text)


def liquid_value(name):
    return rf"{{{{\s*{re.escape(name)}\b[^}}]*}}}}"


def locale_contract(text):
    page_lang = r"{%\s*assign\s+page_lang\s*=\s*page\.lang\s*\|\s*default\s*:\s*['\"]zh-CN['\"]\s*%}"
    locale = r"{%\s*assign\s+locale\s*=\s*site\.data\.locales\[\s*page_lang\s*\]\s*\|\s*default\s*:\s*site\.data\.locales\[\s*['\"]zh-CN['\"]\s*\]\s*%}"
    return page_lang, locale


class BilingualContractTest(unittest.TestCase):
    def assert_yaml_document(self, path, expected_type):
        self.assertTrue(path.is_file(), f"{path.relative_to(ROOT)} must exist")
        if not path.is_file():
            return None
        try:
            document = yaml.safe_load(read_utf8(path))
        except yaml.YAMLError as error:
            self.fail(f"{path.name} has invalid YAML: {error}")
            return None
        self.assertIsInstance(document, expected_type, f"{path.name} must contain YAML {expected_type.__name__}")
        return document if isinstance(document, expected_type) else None

    def assert_page_metadata(self, path, expected, language):
        self.assertTrue(path.is_file(), f"{path.relative_to(ROOT)} must exist")
        if not path.is_file():
            return None
        try:
            front_matter = load_front_matter(path)
        except AssertionError as error:
            self.fail(str(error))
            return None
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
            self.assertRegex(value, r"[\u3400-\u9fff]" if language == "zh-CN" else r"[A-Za-z]")
            if language == "en":
                self.assertNotRegex(value, r"[\u3400-\u9fff]")
        return front_matter

    def assert_section_markers(self, page, language):
        sections = {}
        matches = list(re.finditer(r"<span\s+class=['\"]anchor['\"]\s+id=['\"]([^'\"]+)", page))
        for index, match in enumerate(matches):
            anchor = match.group(1)
            end = matches[index + 1].start() if index + 1 < len(matches) else len(page)
            sections[anchor] = page[match.start():end]
        for anchor, markers in PAGE_FACT_MARKERS[language].items():
            self.assertIn(anchor, sections, f"{language} page is missing section {anchor}")
            for marker in markers:
                self.assertRegex(sections.get(anchor, ""), marker, f"{language} section {anchor} is missing {marker}")
        return sections

    def test_pages_have_bilingual_routes_and_metadata(self):
        self.assert_page_metadata(ROOT / "_pages" / "about.md", {"permalink": "/", "lang": "zh-CN", "alternate_url": "/en/"}, "zh-CN")
        self.assert_page_metadata(ROOT / "_pages" / "about-en.md", {"permalink": "/en/", "lang": "en", "alternate_url": "/"}, "en")

    def test_pages_have_matching_sections_facts_and_one_publication_include(self):
        paths = [ROOT / "_pages" / name for name in ("about.md", "about-en.md")]
        for path in paths:
            self.assertTrue(path.is_file(), f"{path.relative_to(ROOT)} must exist")
        if not all(path.is_file() for path in paths):
            return
        pages = [active_source(path) for path in paths]
        for page, language in zip(pages, ("zh-CN", "en")):
            self.assertEqual(EXPECTED_ANCHORS, [anchor for anchor in anchors_in(page) if anchor in EXPECTED_ANCHORS])
            self.assertEqual(1, page.count("{% include publications.html %}"))
            sections = self.assert_section_markers(page, language)
            for anchor in EXPECTED_ANCHORS:
                self.assertRegex(sections[anchor], r"</span>\s*\n\s*#\s+[^\n]+", f"section {anchor} needs a heading")

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
                self.assertIsInstance(item, dict, f"{path.name} entries must be mappings")
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
            config = self.assert_yaml_document(ROOT / "_config.yml", dict)
            shared_author = config.get("author", {}) if isinstance(config, dict) else {}
            shared_values = {str(shared_author[key]) for key in CONTACT_KEYS if isinstance(shared_author, dict) and shared_author.get(key)}
            for key, value in locales[language].items():
                self.assertIsInstance(key, str, f"{language} locale keys must be strings")
                self.assertIsInstance(value, str, f"{language}.{key} must be a scalar string")
                if not isinstance(key, str) or not isinstance(value, str):
                    continue
                self.assertTrue(value.strip(), f"{language}.{key} must be non-empty")
                self.assertLessEqual(len(value), 160, f"{language}.{key} is too long for display text")
                self.assertNotRegex(value, r"https?://|mailto:", f"{language}.{key} must not contain a URL")
                self.assertNotRegex(value, r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", f"{language}.{key} must not contain an email")
                self.assertNotIn(key.lower(), {"email", "googlescholar", "researchgate", "uri", "avatar", "github", "twitter", "facebook"}, f"{language}.{key} duplicates shared author data")
                self.assertNotIn(value, shared_values, f"{language}.{key} duplicates shared contact data")

    def test_shared_contact_urls_and_no_multilingual_plugins(self):
        config = self.assert_yaml_document(ROOT / "_config.yml", dict)
        if config is None:
            return
        author = config.get("author")
        self.assertIsInstance(author, dict, "_config.yml author must be a mapping")
        if isinstance(author, dict):
            for key in CONTACT_KEYS:
                self.assertIn(key, author, f"site.author must retain {key}")
            self.assertEqual("https://scholar.google.com/citations?user=2zkUJHAAAAAJ&hl", author.get("googlescholar"))
            self.assertEqual("wangran@sus.edu.cn", author.get("email"))
            self.assertEqual("https://www.researchgate.net/profile/Ran-Wang-61", author.get("researchgate"))
        config_active = strip_comments(read_utf8(ROOT / "_config.yml"))
        gemfile_active = strip_comments(read_utf8(ROOT / "Gemfile"))
        for token in BANNED_MULTILINGUAL_TOKENS:
            self.assertNotRegex(config_active, token)
            self.assertNotRegex(gemfile_active, token)

    def test_bilingual_implementation_has_no_client_side_language_detection_or_redirects(self):
        for relative_path in BILINGUAL_IMPLEMENTATION_FILES:
            path = ROOT / relative_path
            if not path.is_file():
                continue
            text = active_source(path)
            for token in FORBIDDEN_CLIENT_SIDE_LANGUAGE_TOKENS:
                self.assertNotRegex(text, token, f"{relative_path} must not use {token}")
        script_paths = loaded_script_sources()
        self.assertIn(ROOT / "_includes" / "scripts.html", script_paths)
        self.assertIn(ROOT / "assets" / "js" / "_main.js", script_paths)
        for path in script_paths:
            self.assertTrue(path.is_file(), f"loaded script source must exist: {path.relative_to(ROOT)}")
            text = active_source(path)
            for token in FORBIDDEN_LANGUAGE_LOGIC_TOKENS:
                self.assertNotRegex(text, token, f"{path.relative_to(ROOT)} must not use {token}")

    def test_includes_derive_locale_from_page_language(self):
        for relative_path in ("_includes/masthead.html", "_includes/author-profile.html", "_includes/publications.html"):
            text = active_source(ROOT / relative_path)
            page_lang, locale = locale_contract(text)
            self.assertRegex(text, page_lang, f"{relative_path} must derive page_lang")
            self.assertRegex(text, locale, f"{relative_path} must derive locale from page_lang")

    def test_masthead_has_localized_navigation_branch_and_real_language_link(self):
        masthead = active_source(ROOT / "_includes" / "masthead.html")
        page_lang, locale = locale_contract(masthead)
        self.assertRegex(masthead, page_lang)
        self.assertRegex(masthead, locale)
        self.assertRegex(masthead, r"{%\s*if\s+page_lang\s*==\s*['\"]en['\"]\s*%}[\s\S]*?site\.data\[['\"]navigation-en['\"]\]\.main")
        self.assertRegex(masthead, r"{%\s*else\s*%}[\s\S]*?site\.data\.navigation\.main")
        switch_match = re.search(r"<a\b[^>]*class\s*=\s*['\"][^'\"]*\blanguage-switch\b[^'\"]*['\"][^>]*>[\s\S]*?</a>", masthead)
        self.assertIsNotNone(switch_match, "masthead must emit a language-switch anchor")
        if switch_match is None:
            return
        switch = switch_match.group(0)
        self.assertRegex(switch, r"href\s*=\s*['\"][^'\"]*\{\{\s*page\.alternate_url\b[^}]*\}\}")
        self.assertRegex(switch, r"hreflang\s*=\s*['\"][^'\"]+['\"]")
        self.assertRegex(switch, r"aria-label\s*=\s*['\"]\{\{\s*locale\.switch_label\b[^}]*\}\}")

    def test_profile_interpolates_localized_fields_and_keeps_shared_author_contacts(self):
        profile = active_source(ROOT / "_includes" / "author-profile.html")
        page_lang, locale = locale_contract(profile)
        self.assertRegex(profile, page_lang)
        self.assertRegex(profile, locale)
        for key in ("profile_name", "profile_bio", "location"):
            self.assertRegex(profile, liquid_value(f"locale.{key}"))
        self.assertRegex(profile, r"{%\s*assign\s+author\s*=\s*site\.author\s*%}")
        self.assertRegex(profile, r"author\.avatar")
        self.assertRegex(profile, r"author\.(?:email|uri|github|researchgate|googlescholar)")

    def test_publications_localizes_attributes_and_links_inside_real_loop(self):
        publications = active_source(ROOT / "_includes" / "publications.html")
        page_lang, locale = locale_contract(publications)
        self.assertRegex(publications, page_lang)
        self.assertRegex(publications, locale)
        loop_match = re.search(r"{%\s*for\s+publication\s+in\s+site\.data\.publications\s*%}(?P<body>[\s\S]*?){%\s*endfor\s*%}", publications)
        self.assertIsNotNone(loop_match, "publications include must loop over site.data.publications")
        self.assertRegex(publications, r"<section\b[^>]*aria-label\s*=\s*['\"]\{\{\s*locale\.publications_label\b[^}]*\}\}")
        if loop_match is None:
            return
        loop_body = loop_match.group("body")
        self.assertRegex(loop_body, liquid_value("locale.article_label"))
        self.assertRegex(loop_body, liquid_value("locale.download_label"))

    def test_default_layout_uses_dynamic_page_language_with_chinese_fallback(self):
        layout = active_source(ROOT / "_layouts" / "default.html")
        html_match = re.search(r"<html\b(?P<attrs>[^>]*)>", layout)
        self.assertIsNotNone(html_match)
        if html_match is None:
            return
        attrs = html_match.group("attrs")
        inline = re.search(r"lang\s*=\s*['\"]\{\{\s*page\.lang\s*\|\s*default\s*:\s*['\"]zh-CN['\"]\s*\}\}", attrs)
        assigned = re.search(r"{%\s*assign\s+(\w+)\s*=\s*page\.lang\s*\|\s*default\s*:\s*['\"]zh-CN['\"]\s*%}", layout)
        self.assertTrue(inline or (assigned and re.search(rf"lang\s*=\s*['\"]\{{\{{\s*{assigned.group(1)}\s*\}}\}}", attrs)), "html lang must use page.lang or a page-derived fallback variable")

    def test_seo_include_emits_real_language_alternate_pairings(self):
        seo = active_source(ROOT / "_includes" / "seo.html")
        links = []
        for tag in re.findall(r"<link\b[^>]*>", seo):
            rel = re.search(r"\brel\s*=\s*['\"]([^'\"]+)['\"]", tag)
            lang = re.search(r"\bhreflang\s*=\s*['\"]([^'\"]+)['\"]", tag)
            href = re.search(r"\bhref\s*=\s*(['\"])(.*?)\1", tag)
            if rel and rel.group(1) == "alternate" and lang and href:
                links.append((lang.group(1), href.group(2), tag))
        for language in ("zh-CN", "en", "x-default"):
            matches = [href for lang, href, _ in links if lang == language]
            self.assertEqual(1, len(matches), f"SEO must emit one alternate for {language}")
            if not matches:
                continue
            href = matches[0]
            if language == "en":
                self.assertRegex(href, r"\{\{\s*['\"]?/en/['\"]?\s*\|\s*prepend\s*:\s*seo_url")
            else:
                self.assertRegex(href, r"\{\{\s*['\"]?/['\"]?\s*\|\s*prepend\s*:\s*seo_url")
                self.assertNotIn("/en/", href, f"{language} alternate must use the exact root route")


if __name__ == "__main__":
    unittest.main()
