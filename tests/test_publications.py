from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
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
HIGHLIGHTED_WANG_MARKDOWN = re.compile(
    r"(?:`[^`]*(?:Wang|\u738b\u7136)[^`]*`|\*\*[^*]*(?:Wang|\u738b\u7136)[^*]*\*\*)"
)


class PublicationsContractTest(unittest.TestCase):
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
        for field in ("badge", "image", "image_alt", "web_url", "pdf_url"):
            self.assertRegex(loop_body, rf"{{{{\s*publication\.{field}\s*}}}}")
        self.assertRegex(
            loop_body,
            r"{{\s*publication\.citation\s*\|\s*markdownify\s*}}",
        )
        for css_class in ("paper-box", "paper-box-image", "paper-box-text", "badge"):
            self.assertIn(css_class, loop_body)


if __name__ == "__main__":
    unittest.main()
