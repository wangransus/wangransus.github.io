from pathlib import Path
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


class PublicationsContractTest(unittest.TestCase):
    def test_publication_data_has_the_required_schema_and_assets(self):
        self.assertTrue(DATA_PATH.is_file(), "_data/publications.yml must exist")
        if not DATA_PATH.is_file():
            return

        with DATA_PATH.open(encoding="utf-8") as data_file:
            publications = yaml.safe_load(data_file)

        self.assertIsInstance(publications, list)
        self.assertEqual(20, len(publications))

        pairs = set()
        for publication in publications:
            self.assertIsInstance(publication, dict)
            self.assertEqual(REQUIRED_FIELDS, set(publication))

            pair = (publication["badge"], publication["citation"])
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
        self.assertIn("site.data.publications", include)
        self.assertIn("markdownify", include)
        for css_class in ("paper-box", "paper-box-image", "paper-box-text", "badge"):
            self.assertIn(css_class, include)


if __name__ == "__main__":
    unittest.main()
