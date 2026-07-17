from hashlib import sha256
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
    ("Sensors 2026", "/images/2026Sensors.jpg", "Sensors article cover", "https://www.mdpi.com/1424-8220/26/4/1161", "/docs/2026Sensors.pdf"),
    ("\u300a\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280\u300b2026", "/images/2026\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.jpg", "\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280 article cover", "https://zgty.cbpt.cnki.net/portal/journal/portal/client/paper/9aa26310534f11d9ce1b7b03ef8ab6c7", "/docs/2026\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.pdf"),
    ("Sports 2025", "/images/2025Sports.jpg", "Sports article cover", "https://www.mdpi.com/2075-4663/13/12/418", "/docs/2025Sports.pdf"),
    ("\u300a\u533b\u7528\u751f\u7269\u529b\u5b66\u300b2025", "/images/2025\u533b\u7528\u751f\u7269\u529b\u5b66.png", "\u533b\u7528\u751f\u7269\u529b\u5b66 article cover", "http://www.mechanobiology.cn/yyswlx/article/abstract/202503007?st=article_issue", "/docs/2025\u533b\u7528\u751f\u7269\u529b\u5b66.pdf"),
    ("\u300a\u5929\u6d25\u4f53\u80b2\u5b66\u9662\u5b66\u62a5\u300b2025", "/images/2025\u5929\u6d25\u4f53\u80b2\u5b66\u9662\u5b66\u62a5.jpg", "\u5929\u6d25\u4f53\u80b2\u5b66\u9662\u5b66\u62a5 article cover", "https://kns.cnki.net/kcms2/article/abstract?v=y_SiIdm5mqvqk45ugVBXBLXnO2ofzeVOpFoslaGU-URdyWrw0Z6-uDG1Y1QPke6iOF1loIGdDCXbK-M0w7muh2zVesLp_8Rwv3QCWatoHkoYFEEKpAGK_MW1ZtRsgCxiNJxsWVjSJVV60ddnnAcrPmbC72VQSzWe2evtWa9Xtu0=&uniplatform=NZKPT", "/docs/2025\u5929\u6d25\u4f53\u80b2\u5b66\u9662\u5b66\u62a5.pdf"),
    ("J Strength Cond Res. 2025", "/images/2025JSCR.jpg", "Journal of Strength and Conditioning Research article cover", "https://pubmed.ncbi.nlm.nih.gov/40266644/", "/docs/2025JSCR.pdf"),
    ("Sports Med. 2025", "/images/2025SportsMedicine.png", "Sports Medicine article cover", "https://doi.org/10.1007/s40279-024-02170-6", "/docs/2025SportsMedicine.pdf"),
    ("\u300a\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280\u300b2025", "/images/2025\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.jpg", "\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280 article cover", "http://www.cisszgty.com/tykj/2025/channel/1/2025/0126/5058.html", "/docs/2025\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.pdf"),
    ("\u300a\u4f53\u80b2\u79d1\u5b66\u300b2024", "/images/2024\u4f53\u80b2\u79d1\u5b662.jpg", "\u4f53\u80b2\u79d1\u5b66 article cover", "http://tykx.xml-journal.net/article/doi/10.16469/J.css.2024KX040", "/docs/2024\u4f53\u80b2\u79d1\u5b662.pdf"),
    ("\u300a\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280\u300b2024", "/images/2024\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.jpg", "\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280 article cover", "http://www.cisszgty.com/tykj/2024/channel/4/2024/0702/4823.html", "/docs/2024\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.pdf"),
    ("\u300a\u4f53\u80b2\u79d1\u5b66\u300b2024", "/images/2024\u4f53\u80b2\u79d1\u5b66.jpg", "\u4f53\u80b2\u79d1\u5b66 article cover", "http://tykx.xml-journal.net/article/doi/10.16469/j.css.202401010", "/docs/2024\u4f53\u80b2\u79d1\u5b66.pdf"),
    ("Sports Med. 2024", "/images/2024SportsMedicine2.png", "Sports Medicine article cover", "https://link.springer.com/article/10.1007/s40279-024-02025-0", "/docs/2024SportsMedicine2.pdf"),
    ("Sports Med. 2024", "/images/2024SportsMedicine.jpg", "Sports Medicine article cover", "https://link.springer.com/article/10.1007/s40279-024-02003-6", "/docs/2024SportsMedicine.pdf"),
    ("\u300a\u4f53\u80b2\u79d1\u5b66\u300b2023", "/images/2023\u4f53\u80b2\u79d1\u5b66.jpg", "\u4f53\u80b2\u79d1\u5b66 article cover", "http://tykx.xml-journal.net/article/doi/10.16469/j.css.202301005", "/docs/2023\u4f53\u80b2\u79d1\u5b66.pdf"),
    ("\u300a\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280\u300b2022", "/images/2022\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.jpg", "\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280 article cover", "http://www.cisszgty.com/tykj/2022/channel/11/2023/0131/4307.html", "/docs/2022\u4e2d\u56fd\u4f53\u80b2\u79d1\u6280.pdf"),
    ("\u300a\u6210\u90fd\u4f53\u80b2\u5b66\u9662\u5b66\u62a5\u300b2022", "/images/2021\u6210\u4f53\u5b66\u62a5.png", "\u6210\u90fd\u4f53\u80b2\u5b66\u9662\u5b66\u62a5 article cover", "https://dx.doi.org/10.15942/j.jcsu.2022.01.021", "/docs/2022\u6210\u4f53\u5b66\u62a5.pdf"),
    ("J. Sports Eng. Technol. 2021", "/images/2021JSET.png", "Journal of Sports Engineering and Technology article cover", "https://dx.doi.org/10.1177/17543371211050312", "/docs/2021JSET.pdf"),
    ("\u300a\u4f53\u80b2\u4e0e\u79d1\u5b66\u300b2020", "/images/2020\u4f53\u80b2\u4e0e\u79d1\u5b66.png", "\u4f53\u80b2\u4e0e\u79d1\u5b66 article cover", "https://dx.doi.org/10.13598/j.issn1004-4590.2020.06.012", "/docs/2020\u4f53\u80b2\u4e0e\u79d1\u5b66.pdf"),
    ("Sports Biomech. 2020", "/images/2020SportsBiomechanics.png", "Sports Biomechanics article cover", "https://dx.doi.org/10.1080/14763141.2018.1497194", "/docs/2020SportsBiomechanics.pdf"),
    ("J. Am. Coll. Nutr. 2018", "/images/2018JACN.png", "Journal of the American Nutrition Association article cover", "https://doi.org/10.1080/07315724.2018.1475269", "/docs/2018JACN.pdf"),
]
EXPECTED_CITATION_SHA256 = [
    "f7c9c57b2b91a7e57f213b86617613dd1d01d88b6eea6a7d145f28ec6b7b5a79",
    "ff448ea205741fb2cb98e03d75d9deca67f3e3a9756b79fa9b0b6401f398652c",
    "60f47a4beab553bb4a9b70854f722aebc66c98bde153b20deb1baed3e98dec0a",
    "112b8dea45bfa15af9c52df6bb2af89ff1c01a26b2b14546bc6bff5a425fa971",
    "f1af586f6e2dd811566ff63e115db2973c88243c4ba4a779ecaf1a96cde76b12",
    "d1752fb30259030836f206e4d0302489dd7a4e6057d39befe251ca6bec290c2e",
    "a59eca632030ad289dec89dde3eb3c588fe8db10802419f711bdeb431ea37e7b",
    "61375ac452af8b06620bf495d2ca9575a7357966f70c6178b4f4f911a2eb3f18",
    "4393baf5258990c0c22efbe47cf889df904fa2dd3e53684463804bf3c6ca8960",
    "4b323d741aad01ccdcc0a4cc1eccf6e7851e05fe358b32f18c330909f8701f9a",
    "b937474abc60082d549ec1c5fe1e5b612b6e25335779cec2a75203aba3b9f341",
    "979c19842cbb800d41f84af5f631fcfc7c9fa5bf78039a414b9adb72a620f99d",
    "84dff4ea580bccdddfb19612ff5e33bc7941ed3410d8974c11ba4f5d4eeedc9d",
    "1a6d8dd816e8f38940a5dc7b418cfc423fd8908d1f1ff801d5f07163e2faa3c4",
    "d7154882474d665c6152ee3514e38882873f920ff5e9b528985eeb041d182708",
    "45442e9eb10a79eef576a3a69d0fffb2611c2149f27dd86a4856bbe3d4c6be4c",
    "b296c3a8b9331e6083370f34aa7504b4150e5f529a336bdd86906fcb4a52859c",
    "aef21d825a42512e215c4893a48e80908cf9ad3f8c15165a8abfa71789eb9bf3",
    "d58494c0a81aa928a4503e00fedd8e52ac6015a01628e080cd8ca6d2f29b9f90",
    "9d0e28fbb7c37a5c5b83ad1eec81d1a33de60d3cc51075d32c193a5253b9170b",
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
                tuple(publication.get(field) if isinstance(publication, dict) else None for field in ("badge", "image", "image_alt", "web_url", "pdf_url"))
                for publication in publications
            ],
        )
        self.assertEqual(
            EXPECTED_CITATION_SHA256,
            [
                sha256(citation.encode("utf-8")).hexdigest() if isinstance(citation, str) else None
                for citation in (
                    publication.get("citation") if isinstance(publication, dict) else None
                    for publication in publications
                )
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
        self.assertRegex(
            include,
            r'<section\s+class=["\']publications["\']\s+aria-label=["\']\{\{\s*locale\.publications_label\b[^}]*\}\}["\']>',
        )
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
