from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_guarded_delivery_authority import validate, write_delivery_package_manifest


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _build_authority(root: Path) -> Path:
    suffix = "260807"
    out = root / "output" / "fresh_generation"
    out.mkdir(parents=True)
    names = {
        "nl_md": f"weekly_etf_eu_review_nl_{suffix}.md",
        "en_md": f"weekly_etf_eu_review_{suffix}.md",
        "nl_html": f"weekly_etf_eu_review_nl_{suffix}.html",
        "en_html": f"weekly_etf_eu_review_{suffix}.html",
        "nl_pdf": f"weekly_etf_eu_review_nl_{suffix}.pdf",
        "en_pdf": f"weekly_etf_eu_review_{suffix}.pdf",
    }
    artifacts = {}
    for key, name in names.items():
        path = out / name
        path.write_bytes((key + "\n").encode("utf-8"))
        rel = path.relative_to(root)
        artifacts[key] = {"path": str(rel), "sha256": _sha(path)}

    safety_evidence = root / "output" / "quality" / "client_surface_safety_test.json"
    safety_evidence.parent.mkdir(parents=True)
    safety_evidence.write_text('{"status":"PASS"}\n', encoding="utf-8")
    payload = {
        "schema_version": "etf_eu_guarded_delivery_authority_v1",
        "artifact_type": "etf_eu_guarded_delivery_authority",
        "product": "weekly_etf_eu",
        "status": "APPROVED_FOR_GUARDED_DELIVERY",
        "delivery_authority": True,
        "portfolio_mutation": False,
        "broker_execution": False,
        "report_date": "2026-08-07",
        "report_suffix": suffix,
        "report_run_id": "20260807_220000",
        "assured_candidate_head_sha": "1" * 40,
        "approved_report_commit_sha": "2" * 40,
        "independent_assurance": {
            "verdict": "PASS",
            "reviewer_role": "governance_release_assurance",
            "implementation_role_separate": True,
            "reviewed_head_sha": "1" * 40,
            "evidence_ref": "https://github.com/market-predictions/weekly-etf-eu/issues/999#issuecomment-1",
        },
        "principal_guarded_send_authorization": {
            "approved": True,
            "reference": "principal-command-2026-08-10",
        },
        "client_surface_safety": {
            "stale_delivery_wording_present": False,
            "main_surface_us_proxy_exposure": False,
            "main_surface_tbd_candidate_exposure": False,
            "nan_price_in_client_surface": False,
            "evidence_ref": str(safety_evidence.relative_to(root)),
        },
        "artifacts": artifacts,
    }
    path = root / "authority.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_valid_authority_binds_six_exact_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    authority = _build_authority(tmp_path)
    monkeypatch.chdir(tmp_path)
    payload = validate(Path("authority.json"))
    manifest = Path("output/delivery_package/test.json")
    write_delivery_package_manifest(payload, manifest, "20260810_160000")
    written = json.loads(manifest.read_text(encoding="utf-8"))
    assert written["source_is_independently_assured"] is True
    assert written["artifact_hashes_verified"] is True
    assert written["dutch_primary_pdf"].endswith("weekly_etf_eu_review_nl_260807.pdf")


def test_hash_drift_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    authority = _build_authority(tmp_path)
    monkeypatch.chdir(tmp_path)
    payload = json.loads(Path("authority.json").read_text(encoding="utf-8"))
    nl_md = Path(payload["artifacts"]["nl_md"]["path"])
    nl_md.write_text("changed after assurance", encoding="utf-8")
    with pytest.raises(AssertionError, match="artifact hash mismatch"):
        validate(Path("authority.json"))


def test_non_pass_or_same_role_assurance_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    authority = _build_authority(tmp_path)
    monkeypatch.chdir(tmp_path)
    payload = json.loads(Path("authority.json").read_text(encoding="utf-8"))
    payload["independent_assurance"]["verdict"] = "INDETERMINATE"
    Path("authority.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(AssertionError, match="verdict must be PASS"):
        validate(Path("authority.json"))

    payload["independent_assurance"]["verdict"] = "PASS"
    payload["independent_assurance"]["implementation_role_separate"] = False
    Path("authority.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(AssertionError, match="independence not evidenced"):
        validate(Path("authority.json"))
