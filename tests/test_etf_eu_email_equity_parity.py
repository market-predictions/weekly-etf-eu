from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.send_etf_eu_controlled_report import _build_message, _materialize_email_equity_curve


SVG = """<svg class="equity-curve-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 390">
<rect x="0" y="0" width="920" height="390" fill="#ffffff" />
<polyline points="20,300 250,280 500,310 900,80" fill="none" stroke="#315f89" stroke-width="5" />
</svg>"""
HTML = f"""<!doctype html><html><body><section><div class="equity-curve-block">{SVG}</div></section></body></html>"""


class EmailEquityParityTests(unittest.TestCase):
    def test_materialization_replaces_inline_svg_with_single_cid_png(self) -> None:
        for language in ("nl", "en"):
            with self.subTest(language=language):
                html, png, cid = _materialize_email_equity_curve(HTML, language=language)
                self.assertIsNotNone(png)
                self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
                self.assertIsNotNone(cid)
                self.assertNotIn("equity-curve-svg", html)
                self.assertNotIn("<svg", html)
                self.assertEqual(html.count(f"cid:{cid}"), 1)
                self.assertIn("equity-curve-email-img", html)

    def test_message_has_related_png_and_pdf_for_both_languages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            md = root / "report.md"
            html = root / "report.html"
            pdf = root / "report.pdf"
            md.write_text("# Report\n", encoding="utf-8")
            html.write_text(HTML, encoding="utf-8")
            pdf.write_bytes(b"%PDF-1.4\n% test fixture\n")

            for language in ("nl", "en"):
                with self.subTest(language=language):
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
                    self.assertIsNotNone(cid_header)
                    cid = cid_header.strip("<>")
                    self.assertEqual(html_body.count(f"cid:{cid}"), 1)
                    self.assertNotIn("equity-curve-svg", html_body)
                    self.assertEqual(png_parts[0].get_content_disposition(), "inline")
                    self.assertEqual(pdf_parts[0].get_filename(), "report.pdf")

    def test_curve_marker_without_svg_fails_closed(self) -> None:
        broken = '<html><body><div class="equity-curve-block">missing curve</div></body></html>'
        with self.assertRaisesRegex(RuntimeError, "expected exactly one equity curve SVG"):
            _materialize_email_equity_curve(broken, language="nl")


if __name__ == "__main__":
    unittest.main()
