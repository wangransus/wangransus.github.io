from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "_config.yml"
DATA_PATH = ROOT / "_data" / "publications.yml"
INCLUDE_PATH = ROOT / "_includes" / "publications.html"
ABOUT_PATH = ROOT / "_pages" / "about.md"
REQUIRED_FIELDS = {
    "badge",
    "image",
    "image_alt",
    "citation",
    "web_url",
    "pdf_url",
}
EXPECTED_IMAGE_PATHS = [
    "/images/2026Sensors.jpg",
    "/images/2026\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.jpg",
    "/images/2025Sports.jpg",
    "/images/2025\u533b\u7528\u751f\u7269\u529b\u5b66.png",
    "/images/2025\u5929\u6d25\u4f53\u80b2\u5b66\u9662\u5b66\u62a5.jpg",
    "/images/2025JSCR.jpg",
    "/images/2025SportsMedicine.png",
    "/images/2025\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.jpg",
    "/images/2024\u4f53\u80b2\u79d1\u5b662.jpg",
    "/images/2024\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.jpg",
    "/images/2024\u4f53\u80b2\u79d1\u5b66.jpg",
    "/images/2024SportsMedicine2.png",
    "/images/2024SportsMedicine.jpg",
    "/images/2023\u4f53\u80b2\u79d1\u5b66.jpg",
    "/images/2022\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.jpg",
    "/images/2021\u6210\u4f53\u5b66\u62a5.png",
    "/images/2021JSET.png",
    "/images/2020\u4f53\u80b2\u4e0e\u79d1\u5b66.png",
    "/images/2020SportsBiomechanics.png",
    "/images/2018JACN.png",
]
EXPECTED_PUBLICATION_PROJECTION = [
    ("Sensors 2026", "/images/2026Sensors.jpg", "https://www.mdpi.com/1424-8220/26/4/1161", "/docs/2026Sensors.pdf"),
    ("\u300a\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280\u300b2026", "/images/2026\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.jpg", "https://zgty.cbpt.cnki.net/portal/journal/portal/client/paper/9aa26310534f11d9ce1b7b03ef8ab6c7", "/docs/2026\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.pdf"),
    ("Sports 2025", "/images/2025Sports.jpg", "https://www.mdpi.com/2075-4663/13/12/418", "/docs/2025Sports.pdf"),
    ("\u300a\u533b\u7528\u751f\u7269\u529b\u5b66\u300b2025", "/images/2025\u533b\u7528\u751f\u7269\u529b\u5b66.png", "http://www.mechanobiology.cn/yyswlx/article/abstract/202503007?st=article_issue", "/docs/2025\u533b\u7528\u751f\u7269\u529b\u5b66.pdf"),
    ("\u300a\u5929\u6d25\u4f53\u80b2\u5b66\u9662\u5b66\u62a5\u300b2025", "/images/2025\u5929\u6d25\u4f53\u80b2\u5b66\u9662\u5b66\u62a5.jpg", "https://kns.cnki.net/kcms2/article/abstract?v=y_SiIdm5mqvqk45ugVBXBLXnO2ofzeVOpFoslaGU-URdyWrw0Z6-uDG1Y1QPke6iOF1loIGdDCXbK-M0w7muh2zVesLp_8Rwv3QCWatoHkoYFEEKpAGK_MW1ZtRsgCxiNJxsWVjSJVV60ddnnAcrPmbC72VQSzWe2evtWa9Xtu0=&uniplatform=NZKPT", "/docs/2025\u5929\u6d25\u4f53\u80b2\u5b66\u9662\u5b66\u62a5.pdf"),
    ("J Strength Cond Res. 2025", "/images/2025JSCR.jpg", "https://pubmed.ncbi.nlm.nih.gov/40266644/", "/docs/2025JSCR.pdf"),
    ("Sports Med. 2025", "/images/2025SportsMedicine.png", "https://doi.org/10.1007/s40279-024-02170-6", "/docs/2025SportsMedicine.pdf"),
    ("\u300a\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280\u300b2025", "/images/2025\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.jpg", "http://www.cisszgty.com/tykj/2025/channel/1/2025/0126/5058.html", "/docs/2025\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.pdf"),
    ("\u300a\u4f53\u80b2\u79d1\u5b66\u300b2024", "/images/2024\u4f53\u80b2\u79d1\u5b662.jpg", "http://tykx.xml-journal.net/article/doi/10.16469/J.css.2024KX040", "/docs/2024\u4f53\u80b2\u79d1\u5b662.pdf"),
    ("\u300a\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280\u300b2024", "/images/2024\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.jpg", "http://www.cisszgty.com/tykj/2024/channel/4/2024/0702/4823.html", "/docs/2024\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.pdf"),
    ("\u300a\u4f53\u80b2\u79d1\u5b66\u300b2024", "/images/2024\u4f53\u80b2\u79d1\u5b66.jpg", "http://tykx.xml-journal.net/article/doi/10.16469/j.css.202401010", "/docs/2024\u4f53\u80b2\u79d1\u5b66.pdf"),
    ("Sports Med. 2024", "/images/2024SportsMedicine2.png", "https://link.springer.com/article/10.1007/s40279-024-02025-0", "/docs/2024SportsMedicine2.pdf"),
    ("Sports Med. 2024", "/images/2024SportsMedicine.jpg", "https://link.springer.com/article/10.1007/s40279-024-02003-6", "/docs/2024SportsMedicine.pdf"),
    ("\u300a\u4f53\u80b2\u79d1\u5b66\u300b2023", "/images/2023\u4f53\u80b2\u79d1\u5b66.jpg", "http://tykx.xml-journal.net/article/doi/10.16469/j.css.202301005", "/docs/2023\u4f53\u80b2\u79d1\u5b66.pdf"),
    ("\u300a\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280\u300b2022", "/images/2022\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.jpg", "http://www.cisszgty.com/tykj/2022/channel/11/2023/0131/4307.html", "/docs/2022\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.pdf"),
    ("\u300a\u6210\u90fd\u4f53\u80b2\u5b66\u9662\u5b66\u62a5\u300b2022", "/images/2021\u6210\u4f53\u5b66\u62a5.png", "https://dx.doi.org/10.15942/j.jcsu.2022.01.021", "/docs/2022\u6210\u4f53\u5b66\u62a5.pdf"),
    ("J. Sports Eng. Technol. 2021", "/images/2021JSET.png", "https://dx.doi.org/10.1177/17543371211050312", "/docs/2021JSET.pdf"),
    ("\u300a\u4f53\u80b2\u4e0e\u79d1\u5b66\u300b2020", "/images/2020\u4f53\u80b2\u4e0e\u79d1\u5b66.png", "https://dx.doi.org/10.13598/j.issn1004-4590.2020.06.012", "/docs/2020\u4f53\u80b2\u4e0e\u79d1\u5b66.pdf"),
    ("Sports Biomech. 2020", "/images/2020SportsBiomechanics.png", "https://dx.doi.org/10.1080/14763141.2018.1497194", "/docs/2020SportsBiomechanics.pdf"),
    ("J. Am. Coll. Nutr. 2018", "/images/2018JACN.png", "https://doi.org/10.1080/07315724.2018.1475269", "/docs/2018JACN.pdf"),
]
HIGHLIGHTED_WANG_MARKDOWN = re.compile(
    r"(?:`[^`]*(?:Wang|\u738b\u7136)[^`]*`|\*\*[^*]*(?:Wang|\u738b\u7136)[^*]*\*\*)"
)


class PublicationsContractTest(unittest.TestCase):
    def test_config_does_not_exclude_publication_pdfs(self):
        with CONFIG_PATH.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        self.assertNotIn("docs", config.get("exclude", []))

    def test_publication_data_has_the_required_schema_and_assets(self):
        self.assertTrue(DATA_PATH.is_file(), "_data/publications.yml must exist")
        if not DATA_PATH.is_file():
            return

        with DATA_PATH.open(encoding="utf-8") as data_file:
            publications = yaml.safe_load(data_file)

        self.assertIsInstance(publications, list)
        self.assertEqual(20, len(publications))
        self.assertEqual(
            EXPECTED_IMAGE_PATHS,
            [publication.get("image") if isinstance(publication, dict) else None for publication in publications],
        )
        self.assertEqual(
            EXPECTED_PUBLICATION_PROJECTION,
            [
                tuple(publication.get(field) if isinstance(publication, dict) else None for field in ("badge", "image", "web_url", "pdf_url"))
                for publication in publications
            ],
        )

        sensors_citation = publications[0].get("citation") if isinstance(publications[0], dict) else ""
        self.assertIn("26(4): 1161.", sensors_citation)
        self.assertNotIn("1611", sensors_citation)

        pairs = set()
        for publication in publications:
            self.assertIsInstance(publication, dict)
            if not isinstance(publication, dict):
                continue
            self.assertEqual(REQUIRED_FIELDS, set(publication))
            if set(publication) != REQUIRED_FIELDS:
                continue

            citation = publication["citation"]
            self.assertIsInstance(citation, str)
            if not isinstance(citation, str):
                continue
            self.assertTrue(citation.strip())
            self.assertRegex(citation, HIGHLIGHTED_WANG_MARKDOWN)

            pair = (publication["badge"], citation)
            self.assertNotIn(pair, pairs)
            pairs.add(pair)

            for field, prefix in (("image", "/images/"), ("pdf_url", "/docs/")):
                asset_path = publication[field]
                self.assertTrue(asset_path.startswith(prefix))
                self.assertTrue((ROOT / asset_path.lstrip("/")).is_file())

    def test_about_page_includes_publications_once(self):
        about = ABOUT_PATH.read_text(encoding="utf-8")

        self.assertEqual(1, about.count("{% include publications.html %}"))

    def test_about_page_has_no_hand_written_publication_boxes(self):
        about = ABOUT_PATH.read_text(encoding="utf-8")

        self.assertNotIn("paper-box", about)

    def test_publications_include_renders_the_data_contract(self):
        self.assertTrue(INCLUDE_PATH.is_file(), "_includes/publications.html must exist")
        if not INCLUDE_PATH.is_file():
            return

        include = INCLUDE_PATH.read_text(encoding="utf-8")
        loop_match = re.search(
            r"{%\s*for\s+publication\s+in\s+site\.data\.publications\s*%}"
            r"(?P<body>.*?)"
            r"{%\s*endfor\s*%}",
            include,
            re.DOTALL,
        )
        self.assertIsNotNone(loop_match)
        if loop_match is None:
            return

        loop_body = loop_match.group("body")
        self.assertRegex(include, r'<section\s+class=["\']publications["\']\s+aria-label=["\']\u79d1\u7814\u6210\u679c\u5217\u8868["\']>')
        self.assertTrue(include.rstrip().endswith("</section>"))
        for field, filters in (
            ("badge", r"\|\s*escape"),
            ("image", r"\|\s*relative_url\s*\|\s*escape"),
            ("image_alt", r"\|\s*escape"),
            ("web_url", r"\|\s*escape"),
            ("pdf_url", r"\|\s*relative_url\s*\|\s*escape"),
        ):
            self.assertRegex(loop_body, rf"{{{{\s*publication\.{field}\s*{filters}\s*}}}}")
        self.assertRegex(
            loop_body,
            r"{{\s*publication\.citation\s*\|\s*markdownify\s*}}",
        )
        class_attributes = re.findall(r"class\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", loop_body)
        class_tokens = {
            token
            for attribute in class_attributes
            for value in attribute
            for token in value.split()
        }
        for css_class in ("paper-box", "paper-box-image", "paper-box-text", "badge"):
            self.assertIn(css_class, class_tokens)


if __name__ == "__main__":
    unittest.main()
