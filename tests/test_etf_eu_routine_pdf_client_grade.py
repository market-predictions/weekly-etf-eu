from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from runtime.render_etf_eu_client_report import render_report
from tools.validate_etf_eu_routine_pdf_client_grade import validate_pdf


ROOT = Path(__file__).resolve().parents[1]


def _fixture_markdown(language: str) -> str:
    if language == "nl":
        titles = [
            "1. Besluit in één oogopslag",
            "2. Portefeuille en kapitaal",
            "3. Actuele UCITS-prijssnapshot",
            "4. Dekking en besliskwaliteit",
            "5. Lane-oordeel",
            "6. Risico- en kwaliteitsgrenzen",
            "7. Volgende routineactie",
            "8. Authority flags",
        ]
        title = "# Weekly ETF EU Review | Nederlands | 2026-07-12"
        intro = "Geen funding vóór volledige verificatie; de portefeuille blijft cash."
    else:
        titles = [
            "1. Decision at a glance",
            "2. Portfolio and capital",
            "3. Current UCITS pricing snapshot",
            "4. Coverage and decision quality",
            "5. Lane assessment",
            "6. Risk and quality boundaries",
            "7. Next routine action",
            "8. Authority flags",
        ]
        title = "# Weekly ETF EU Review | English Companion | 2026-07-12"
        intro = "No funding before full verification; the portfolio remains in cash."

    lines = [title, "", f"> **Review.** {intro}", ""]
    for idx, section in enumerate(titles, start=1):
        lines += [f"## {section}", ""]
        if idx == 2:
            lines += [
                "| Component | Value |",
                "|---|---:|",
                "| Cash | EUR 100,000 |",
                "| Portfolio and capital | EUR 100,000 |",
                "",
            ]
        elif idx == 3:
            lines += ["| Trading line | ISIN | Market | Close | Currency | Status |", "|---|---|---|---:|---|---|"]
            for number in range(10):
                lines.append(
                    f"| ETF{number} · Xetra | IE00B5BMR0{number:02d} | 2026-07-10 | {100 + number}.00 | EUR | candidate_requires_verification |"
                )
            lines.append("")
        elif idx == 8:
            lines += [
                "```text",
                "ready_for_controlled_delivery=false",
                "send_executed=false",
                "transport_attempted=false",
                "receipt_confirmed=false",
                "valuation_grade=false",
                "funding_authority=false",
                "portfolio_mutation=false",
                "production_delivery_authority=false",
                "```",
            ]
        else:
            lines += [f"- {intro}" for _ in range(7)]
            lines.append("")
    return "\n".join(lines)


def test_routine_builder_does_not_use_plain_text_pdf() -> None:
    source = (ROOT / "tools/build_etf_eu_routine_report_package.py").read_text(encoding="utf-8")
    assert "_simple_pdf" not in source
    assert "latin-1" not in source.lower()
    assert "render_etf_eu_client_report" in source


def test_renderer_uses_semantic_html_and_weasyprint() -> None:
    source = (ROOT / "runtime/render_etf_eu_client_report.py").read_text(encoding="utf-8")
    assert 'mistune.create_markdown(plugins=["table"]' in source
    assert "HTML(string=html" in source
    assert "table-row" not in source


@pytest.mark.skipif(not all(shutil.which(name) for name in ("pdfinfo", "pdftotext", "pdftoppm")), reason="Poppler unavailable")
@pytest.mark.parametrize("language", ["nl", "en"])
def test_multi_page_client_report_passes(tmp_path: Path, language: str) -> None:
    markdown = tmp_path / f"{language}.md"
    html = tmp_path / f"{language}.html"
    pdf = tmp_path / f"{language}.pdf"
    markdown.write_text(_fixture_markdown(language), encoding="utf-8")
    title = (
        "Weekly ETF EU Review | Nederlands | 2026-07-12"
        if language == "nl"
        else "Weekly ETF EU Review | English Companion | 2026-07-12"
    )
    render_report(markdown_path=markdown, html_output=html, pdf_output=pdf, language=language, title=title)
    result = validate_pdf(
        pdf=pdf,
        html=html,
        markdown=markdown,
        language=language,
        repair_run_id="fixture",
        source_run_id="fixture",
    )
    assert result["machine_validation_passed"] is True
    assert result["page_count"] >= 2
    assert result["table_rendering_passed"] is True
    assert result["markdown_leakage_detected"] is False
    assert result["duplicate_title_detected"] is False


def test_readiness_requires_machine_and_visual_gates() -> None:
    source = (ROOT / "tools/prepare_etf_eu_routine_package_readiness.py").read_text(encoding="utf-8")
    assert "--pdf-client-grade-gate" in source
    assert "--pdf-visual-review" in source
    assert "visual_review_passed" in source
    assert "pdf_client_grade_passed" in source


def test_normal_workflow_blocks_delivery_before_visual_approval() -> None:
    workflow = (ROOT / ".github/workflows/run-weekly-etf-eu-routine.yml").read_text(encoding="utf-8")
    gate_index = workflow.index("Require explicit rendered-page visual review")
    send_index = workflow.index("Execute guarded current-run delivery")
    assert gate_index < send_index
    assert "etf_eu_routine_pdf_client_grade_" in workflow
    assert "pdftoppm" in (ROOT / "tools/render_etf_eu_pdf_review_pages.py").read_text(encoding="utf-8")


def test_repair_workflow_has_no_transport_or_mail_secrets() -> None:
    workflow = (ROOT / ".github/workflows/repair-weekly-etf-eu-routine-pdf.yml").read_text(encoding="utf-8")
    forbidden = [
        "MRKT_RPRTS_SMTP_HOST",
        "MRKT_RPRTS_SMTP_PASS",
        "MRKT_RPRTS_MAIL_TO",
        "send_confirmation",
        "send_etf_eu_current_package_delivery",
        "check_etf_eu_delivery_receipt",
    ]
    for token in forbidden:
        assert token not in workflow


def test_visual_review_template_remains_pending_until_inspected() -> None:
    workflow = (ROOT / ".github/workflows/repair-weekly-etf-eu-routine-pdf.yml").read_text(encoding="utf-8")
    assert '"visual_review_passed": False' in workflow
    assert "manual visual inspection required before corrected resend" in workflow


@pytest.mark.skipif(not all(shutil.which(name) for name in ("pdfinfo", "pdftotext", "pdftoppm")), reason="Poppler unavailable")
def test_single_page_truncated_output_fails(tmp_path: Path) -> None:
    markdown = tmp_path / "truncated.md"
    html = tmp_path / "truncated.html"
    pdf = tmp_path / "truncated.pdf"
    markdown.write_text(
        "# Weekly ETF EU Review | English Companion | 2026-07-12\n\n"
        "## 1. Decision at a glance\n\nOnly the first section is present.\n",
        encoding="utf-8",
    )
    render_report(
        markdown_path=markdown,
        html_output=html,
        pdf_output=pdf,
        language="en",
        title="Weekly ETF EU Review | English Companion | 2026-07-12",
    )
    result = validate_pdf(
        pdf=pdf,
        html=html,
        markdown=markdown,
        language="en",
        repair_run_id="truncated",
        source_run_id="truncated",
    )
    assert result["machine_validation_passed"] is False
    assert result["page_count"] == 1
    assert result["required_sections_present"] is False


@pytest.mark.skipif(not all(shutil.which(name) for name in ("pdfinfo", "pdftotext", "pdftoppm")), reason="Poppler unavailable")
def test_duplicate_visible_title_fails(tmp_path: Path) -> None:
    markdown = tmp_path / "duplicate.md"
    html = tmp_path / "duplicate.html"
    pdf = tmp_path / "duplicate.pdf"
    source = _fixture_markdown("en")
    source = source.replace(
        "# Weekly ETF EU Review | English Companion | 2026-07-12",
        "# Weekly ETF EU Review | English Companion | 2026-07-12\n\n"
        "Weekly ETF EU Review | English Companion | 2026-07-12",
        1,
    )
    markdown.write_text(source, encoding="utf-8")
    render_report(
        markdown_path=markdown,
        html_output=html,
        pdf_output=pdf,
        language="en",
        title="Weekly ETF EU Review | English Companion | 2026-07-12",
    )
    result = validate_pdf(
        pdf=pdf,
        html=html,
        markdown=markdown,
        language="en",
        repair_run_id="duplicate",
        source_run_id="duplicate",
    )
    assert result["machine_validation_passed"] is False
    assert result["duplicate_title_detected"] is True
