from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.render_etf_eu_shadow_pdf import build_shadow_pdf_manifest
from tools.validate_etf_eu_shadow_pdf import validate


def _write_report_pair(tmp_path: Path, suffix: str = "260605") -> tuple[Path, Path, Path]:
    output = tmp_path / "output"
    output.mkdir()
    dutch = output / f"weekly_etf_eu_review_nl_{suffix}.md"
    english = output / f"weekly_etf_eu_review_{suffix}.md"
    dutch.write_text("# Weekly ETF EU Review | Nederlands\n\nGeen productielevering.\n", encoding="utf-8")
    english.write_text("# Weekly ETF EU Review | English Companion\n\nNo production delivery.\n", encoding="utf-8")
    return output, dutch, english


def test_shadow_pdf_renderer_writes_pdf_pair_and_manifest(tmp_path: Path) -> None:
    output, dutch, english = _write_report_pair(tmp_path)
    pdf_dir = output / "pdf"

    manifest = build_shadow_pdf_manifest(
        run_id="test_run",
        report_date="2026-06-05",
        dutch_report_path=dutch,
        english_report_path=english,
        output_dir=pdf_dir,
    )

    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "etf_eu_shadow_pdf_manifest_v1"
    assert payload["pdf_generation"] == "shadow_only"
    assert payload["production_delivery"] is False
    assert payload["email_delivery"] is False
    assert payload["delivery_receipt"] is False
    assert payload["workflow_integrated"] is False
    assert Path(payload["dutch_pdf_path"]).name == "weekly_etf_eu_review_nl_260605.pdf"
    assert Path(payload["english_pdf_path"]).name == "weekly_etf_eu_review_260605.pdf"
    assert Path(payload["dutch_pdf_path"]).read_bytes().startswith(b"%PDF-")
    assert Path(payload["english_pdf_path"]).read_bytes().startswith(b"%PDF-")


def test_shadow_pdf_validator_accepts_safe_manifest(tmp_path: Path) -> None:
    output, dutch, english = _write_report_pair(tmp_path)
    pdf_dir = output / "pdf"
    manifest = build_shadow_pdf_manifest(
        run_id="test_run",
        report_date="2026-06-05",
        dutch_report_path=dutch,
        english_report_path=english,
        output_dir=pdf_dir,
    )

    validate(manifest, output_dir=pdf_dir)


def test_shadow_pdf_validator_rejects_delivery_claim(tmp_path: Path) -> None:
    output, dutch, english = _write_report_pair(tmp_path)
    pdf_dir = output / "pdf"
    manifest = build_shadow_pdf_manifest(
        run_id="test_run",
        report_date="2026-06-05",
        dutch_report_path=dutch,
        english_report_path=english,
        output_dir=pdf_dir,
    )
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["production_delivery"] = True
    manifest.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    with pytest.raises(RuntimeError, match="production_delivery_must_be_false"):
        validate(manifest, output_dir=pdf_dir)
