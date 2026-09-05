from __future__ import annotations

from pathlib import Path

import pytest

from runtime.write_etf_eu_delivery_evidence import (
    _controlled_languages,
    _validate_transport_result_binding,
)


def _transport_result(*, nl_md: Path, en_md: Path) -> dict[str, object]:
    return {
        "schema_version": "etf_eu_controlled_transport_result_v1",
        "artifact_type": "etf_eu_controlled_transport_result",
        "run_id": "20260831_210000",
        "report_date": "2026-08-28",
        "report_suffix": "260828",
        "languages": [
            {
                "language": "nl",
                "report_path": str(nl_md),
                "recipient_redacted": True,
                "recipient_hash": "abc123",
            },
            {
                "language": "en",
                "report_path": str(en_md),
                "recipient_redacted": True,
                "recipient_hash": "def456",
            },
        ],
    }


def test_controlled_pre_evidence_uses_exact_assured_paths(tmp_path: Path) -> None:
    nl_md = tmp_path / "current" / "report_nl.md"
    en_md = tmp_path / "current" / "report_en.md"
    package_manifest = tmp_path / "delivery_package" / "manifest.json"

    languages = _controlled_languages(
        nl_md=nl_md,
        en_md=en_md,
        delivery_package_manifest=package_manifest,
        mode="controlled_pre",
    )
    rows = {str(row["language"]): row for row in languages}

    assert rows["nl"]["report_path"] == str(nl_md)
    assert rows["en"]["report_path"] == str(en_md)
    assert rows["nl"]["source_manifest_path"] == str(package_manifest)
    assert rows["en"]["source_manifest_path"] == str(package_manifest)
    assert rows["nl"]["source_manifest_type"] == "etf_eu_delivery_package_manifest_v1"
    assert rows["en"]["source_manifest_type"] == "etf_eu_delivery_package_manifest_v1"


def test_transport_result_must_match_exact_assured_report_paths(tmp_path: Path) -> None:
    nl_md = tmp_path / "current" / "report_nl.md"
    en_md = tmp_path / "current" / "report_en.md"
    result = _transport_result(nl_md=nl_md, en_md=en_md)

    hashes = _validate_transport_result_binding(
        result,
        run_id="20260831_210000",
        report_date="2026-08-28",
        report_suffix="260828",
        nl_md=nl_md,
        en_md=en_md,
    )
    assert hashes == {"nl": "abc123", "en": "def456"}

    result["languages"][0]["report_path"] = str(tmp_path / "stale" / "report_nl.md")  # type: ignore[index]
    with pytest.raises(RuntimeError, match="does not match assured path"):
        _validate_transport_result_binding(
            result,
            run_id="20260831_210000",
            report_date="2026-08-28",
            report_suffix="260828",
            nl_md=nl_md,
            en_md=en_md,
        )
