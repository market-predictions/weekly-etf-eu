from __future__ import annotations

import base64
import re
import tempfile
import unittest
from pathlib import Path

from runtime.send_etf_eu_controlled_report import EQUITY_CID, _build_message, _materialize_email_equity_curve
from runtime.standalone_html_equity_embed import (
    materialize_standalone_equity_html,
    validate_standalone_html_equity,
)


SVG = """<svg class="equity-curve-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 390">
<rect x="0" y="0" width="920" height="390" fill="#ffffff" />
<polyline points="20,300 250,280 500,310 900,80" fill="none" stroke="#315f89" stroke-width="5" />
</svg>"""
INTERMEDIATE_HTML = f"""<!doctype html><html><body><section><div class="equity-curve-block">{SVG}</div></section></body></html>"""
STATE = {
    "equity_curve": {
        "show_chart": True,
        "latest_nav_matches_state": True,
        "points": [
            {"date": "2026-05-30", "nav_eur": 100000.0},
            {"date": "2026-07-27", "nav_eur": 99756.76},
            {"date": "2026-08-10", "nav_eur": 100738.73},
            {"date": "2026-08-14", "nav_eur": 100851.09},
        ],
    }
}
DATA_URI_RE = re.compile(r"data:image/png;base64,([A-Za-z0-9+/=]+)")


class EmailEquityParityTests(unittest.TestCase):
    def _standalone_html(self, root: Path, language: str) -> tuple[str, bytes]:
        chart = root / f"curve-{language}.png"
        html = materialize_standalone_equity_html(
            INTERMEDIATE_HTML,
            STATE,
            language=language,
            chart_path=chart,
        )
        validate_standalone_html_equity(html, STATE)
        match = DATA_URI_RE.search(html)
        self.assertIsNotNone(match)
        png = base64.b64decode(match.group(1), validate=True)
        return html, png

    def test_standalone_html_uses_donor_embedded_png_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for language in ("nl", "en"):
                with self.subTest(language=language):
                    html, png = self._standalone_html(root, language)
                    self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
                    self.assertEqual(html.count("data:image/png;base64,"), 1)
                    self.assertIn("equity-curve-image", html)
                    self.assertNotIn("equity-curve-svg", html)
                    self.assertNotIn("<svg", html)

    def test_email_translation_reuses_exact_embedded_png_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for language in ("nl", "en"):
                with self.subTest(language=language):
                    standalone, approved_png = self._standalone_html(root, language)
                    email_html, mime_png, cid = _materialize_email_equity_curve(standalone, language=language)
                    self.assertEqual(mime_png, approved_png)
                    self.assertEqual(cid, EQUITY_CID)
                    self.assertEqual(email_html.count(f"cid:{EQUITY_CID}"), 1)
                    self.assertNotIn("data:image/png;base64,", email_html)
                    self.assertNotIn("equity-curve-svg", email_html)

    def test_message_has_related_png_and_pdf_for_both_languages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            md = root / "report.md"
            pdf = root / "report.pdf"
            md.write_text("# Report\n", encoding="utf-8")
            pdf.write_bytes(b"%PDF-1.4\n% test fixture\n")

            for language in ("nl", "en"):
                with self.subTest(language=language):
                    standalone, approved_png = self._standalone_html(root, language)
                    html = root / f"report-{language}.html"
                    html.write_text(standalone, encoding="utf-8")
                    msg = _build_message(
                        language=language,
                        report_date="2026-08-14",
                        sender="sender@example.invalid",
                        recipient="recipient@example.invalid",
                        markdown_path=md,
                        pdf_path=pdf,
                        html_path=html,
                        require_pdf_package=True,
                    )
                    parts = list(msg.walk())
                    html_parts = [part for part in parts if part.get_content_type() == "text/html"]
                    png_parts = [part for part in parts if part.get_content_type() == "image/png"]
                    pdf_parts = [part for part in parts if part.get_content_type() == "application/pdf"]
                    self.assertEqual(len(html_parts), 1)
                    self.assertEqual(len(png_parts), 1)
                    self.assertEqual(len(pdf_parts), 1)

                    html_body = html_parts[0].get_content()
                    cid_header = png_parts[0]["Content-ID"]
                    self.assertEqual(cid_header, f"<{EQUITY_CID}>")
                    self.assertEqual(html_body.count(f"cid:{EQUITY_CID}"), 1)
                    self.assertNotIn("data:image/png;base64,", html_body)
                    self.assertNotIn("equity-curve-svg", html_body)
                    self.assertEqual(png_parts[0].get_content_disposition(), "inline")
                    self.assertEqual(png_parts[0].get_payload(decode=True), approved_png)
                    self.assertEqual(pdf_parts[0].get_filename(), "report.pdf")

    def test_curve_marker_without_embedded_png_fails_closed(self) -> None:
        broken = '<html><body><div class="equity-curve-block"><img class="equity-curve-image" src="missing.png"></div></body></html>'
        with self.assertRaisesRegex(RuntimeError, "expected exactly one embedded equity PNG data URI"):
            _materialize_email_equity_curve(broken, language="nl")

    def test_inline_svg_is_rejected_by_controlled_transport(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "inline equity SVG reached controlled transport"):
            _materialize_email_equity_curve(INTERMEDIATE_HTML, language="nl")


if __name__ == "__main__":
    unittest.main()
