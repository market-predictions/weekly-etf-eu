from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.send_etf_eu_report_runtime_html import validate_etf_eu_sender_preflight


def _write_pair(output_dir: Path, suffix: str) -> None:
    (output_dir / f"weekly_etf_eu_review_{suffix}.md").write_text("English companion", encoding="utf-8")
    (output_dir / f"weekly_etf_eu_review_nl_{suffix}.md").write_text("Dutch primary", encoding="utf-8")


def test_latest_canonical_eu_pair_is_selected(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    _write_pair(output_dir, "260701")
    _write_pair(output_dir, "260708")

    result = validate_etf_eu_sender_preflight(output_dir=output_dir)

    assert result["report_suffix"] == "260708"
    assert str(result["dutch_primary_report_path"]).endswith("weekly_etf_eu_review_nl_260708.md")
    assert str(result["english_companion_report_path"]).endswith("weekly_etf_eu_review_260708.md")


def test_explicit_suffix_selection_works(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    _write_pair(output_dir, "260701")
    _write_pair(output_dir, "260708")

    result = validate_etf_eu_sender_preflight(output_dir=output_dir, report_suffix="260701")

    assert result["report_suffix"] == "260701"
    assert str(result["dutch_primary_report_path"]).endswith("weekly_etf_eu_review_nl_260701.md")
    assert str(result["english_companion_report_path"]).endswith("weekly_etf_eu_review_260701.md")


def test_non_canonical_draft_artifacts_are_ignored(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    _write_pair(output_dir, "260708")
    (output_dir / "weekly_etf_eu_review_260708_draft.md").write_text("draft", encoding="utf-8")
    (output_dir / "weekly_etf_eu_review_nl_260708_mature_draft.md").write_text("draft", encoding="utf-8")

    result = validate_etf_eu_sender_preflight(output_dir=output_dir)

    assert result["non_canonical_artifacts_ignored"] is True
    assert result["non_canonical_artifacts_ignored_count"] == 2
    assert result["report_suffix"] == "260708"


def test_missing_dutch_primary_fails(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "weekly_etf_eu_review_260708.md").write_text("English only", encoding="utf-8")

    with pytest.raises(RuntimeError, match="no complete canonical Dutch/English report pair"):
        validate_etf_eu_sender_preflight(output_dir=output_dir)


def test_missing_english_companion_fails(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "weekly_etf_eu_review_nl_260708.md").write_text("Dutch only", encoding="utf-8")

    with pytest.raises(RuntimeError, match="no complete canonical Dutch/English report pair"):
        validate_etf_eu_sender_preflight(output_dir=output_dir)


def test_us_weekly_analysis_files_are_ignored(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    _write_pair(output_dir, "260708")
    (output_dir / "weekly_analysis_pro_260708.md").write_text("US report", encoding="utf-8")
    (output_dir / "weekly_analysis_pro_nl_260708.md").write_text("US report", encoding="utf-8")

    result = validate_etf_eu_sender_preflight(output_dir=output_dir)

    assert result["us_report_name_assumption_detected"] is False
    assert result["report_suffix"] == "260708"
    assert "weekly_analysis_pro_260708.md" in result["us_named_artifacts_ignored"]


def test_preflight_never_indicates_send_or_delivery_success(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    _write_pair(output_dir, "260708")

    result = validate_etf_eu_sender_preflight(output_dir=output_dir)

    assert result["send_performed"] is False
    assert result["production_delivery"] is False
    assert result["email_delivery"] is False
    assert result["delivery_receipt"] is False
    assert result["delivery_success_claimed"] is False
