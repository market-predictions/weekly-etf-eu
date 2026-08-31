from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_delivery_package_manifest import validate as validate_package
from tools.validate_etf_eu_guarded_delivery_authority import validate, write_delivery_package_manifest


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _plain_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build_authority(root: Path) -> Path:
    suffix = "260807"
    current = root / "output" / "current"
    current.mkdir(parents=True)
    names = {
        "nl_md": "report_nl.md",
        "en_md": "report_en.md",
        "nl_html": "report_nl.html",
        "en_html": "report_en.html",
        "nl_pdf": "report_nl.pdf",
        "en_pdf": "report_en.pdf",
        "review_state": "review_state.json",
    }
    manifest_artifacts = {}
    for key, name in names.items():
        path = current / name
        path.write_bytes((key + "\n").encode("utf-8"))
        rel = path.relative_to(root)
        manifest_artifacts[key] = {
            "path": str(rel),
            "sha256": _plain_sha(path),
            "size_bytes": path.stat().st_size,
        }

    thin_manifest = {
        "schema_version": "etf_eu_thin_kernel_manifest_v1",
        "run_id": "20260807_220000",
        "report_date": "2026-08-07",
        "report_suffix": suffix,
        "semantic_source": manifest_artifacts["review_state"]["path"],
        "semantic_state_frozen": True,
        "post_freeze_semantic_mutation": False,
        "current_kernel": "runtime/current",
        "candidate_builder": "tools/build_etf_eu_thin_kernel_package.py",
        "production_renderer": "runtime/current/render.py",
        "artifacts": manifest_artifacts,
        "authority": {
            "portfolio_mutation": False,
            "trade_ledger_write": False,
            "real_broker_execution": False,
            "delivery_authority": False,
            "smtp_send": False,
            "funding_authority": False,
        },
    }
    thin_manifest_path = current / "manifest.json"
    thin_manifest_path.write_text(json.dumps(thin_manifest, sort_keys=True), encoding="utf-8")

    safety_evidence = root / "output" / "quality" / "client_surface_safety_test.json"
    safety_evidence.parent.mkdir(parents=True)
    safety_evidence.write_text(json.dumps({
        "schema_version": "etf_eu_client_surface_safety_v1",
        "status": "PASS",
        "valid": True,
        "thin_kernel_manifest": {
            "path": str(thin_manifest_path.relative_to(root)),
            "sha256": _sha(thin_manifest_path),
        },
        "artifacts": {},
        "client_surface_safety": {
            "stale_delivery_wording_present": False,
            "main_surface_us_proxy_exposure": False,
            "main_surface_tbd_candidate_exposure": False,
            "nan_price_in_client_surface": False,
        },
        "exposed_donor_proxies": [],
        "blockers": [],
    }, sort_keys=True) + "\n", encoding="utf-8")
    artifacts = {
        key: {
            "path": manifest_artifacts[key]["path"],
            "sha256": _sha(root / manifest_artifacts[key]["path"]),
        }
        for key in ("nl_md", "en_md", "nl_html", "en_html", "nl_pdf", "en_pdf")
    }
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
        "thin_kernel_manifest": {
            "path": str(thin_manifest_path.relative_to(root)),
            "sha256": _sha(thin_manifest_path),
        },
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
            "evidence_sha256": _sha(safety_evidence),
        },
        "artifacts": artifacts,
    }
    path = root / "authority.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_valid_authority_binds_canonical_thin_kernel_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _build_authority(tmp_path)
    monkeypatch.chdir(tmp_path)
    payload = validate(Path("authority.json"))
    manifest = Path("output/delivery_package/test.json")
    write_delivery_package_manifest(payload, manifest, "20260810_160000")
    written = json.loads(manifest.read_text(encoding="utf-8"))
    assert written["source_is_independently_assured"] is True
    assert written["artifact_hashes_verified"] is True
    assert written["dutch_primary_pdf"] == "output/current/report_nl.pdf"
    assert written["source_thin_kernel_manifest_path"] == "output/current/manifest.json"
    assert written["client_surface_safety_evidence_path"] == "output/quality/client_surface_safety_test.json"
    assert written["report_run_id"] == "20260807_220000"
    assert validate_package(manifest)["status"] == "valid"


def test_package_rejects_source_manifest_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _build_authority(tmp_path)
    monkeypatch.chdir(tmp_path)
    payload = validate(Path("authority.json"))
    package = Path("output/delivery_package/test.json")
    write_delivery_package_manifest(payload, package, "20260810_160000")
    source = Path("output/current/manifest.json")
    source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="source thin-kernel manifest hash mismatch"):
        validate_package(package)


def test_package_rejects_safety_evidence_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _build_authority(tmp_path)
    monkeypatch.chdir(tmp_path)
    payload = validate(Path("authority.json"))
    package = Path("output/delivery_package/test.json")
    write_delivery_package_manifest(payload, package, "20260810_160000")
    safety = Path("output/quality/client_surface_safety_test.json")
    safety.write_text(safety.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="client-surface safety evidence hash mismatch"):
        validate_package(package)


def test_hash_drift_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _build_authority(tmp_path)
    monkeypatch.chdir(tmp_path)
    payload = json.loads(Path("authority.json").read_text(encoding="utf-8"))
    Path(payload["artifacts"]["nl_md"]["path"]).write_text("changed after assurance", encoding="utf-8")
    with pytest.raises(AssertionError, match="artifact hash mismatch"):
        validate(Path("authority.json"))


def test_manifest_freeze_drift_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _build_authority(tmp_path)
    monkeypatch.chdir(tmp_path)
    payload = json.loads(Path("authority.json").read_text(encoding="utf-8"))
    manifest_path = Path(payload["thin_kernel_manifest"]["path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["semantic_state_frozen"] = False
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    payload["thin_kernel_manifest"]["sha256"] = _sha(manifest_path)
    Path("authority.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(AssertionError, match="semantic state is not frozen"):
        validate(Path("authority.json"))


def test_artifact_binding_drift_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _build_authority(tmp_path)
    monkeypatch.chdir(tmp_path)
    payload = json.loads(Path("authority.json").read_text(encoding="utf-8"))
    payload["artifacts"]["nl_md"]["path"] = "output/current/report_en.md"
    payload["artifacts"]["nl_md"]["sha256"] = payload["artifacts"]["en_md"]["sha256"]
    Path("authority.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(AssertionError, match="path differs from thin kernel manifest"):
        validate(Path("authority.json"))


def test_candidate_authority_escalation_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _build_authority(tmp_path)
    monkeypatch.chdir(tmp_path)
    payload = json.loads(Path("authority.json").read_text(encoding="utf-8"))
    manifest_path = Path(payload["thin_kernel_manifest"]["path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["authority"]["delivery_authority"] = True
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    payload["thin_kernel_manifest"]["sha256"] = _sha(manifest_path)
    Path("authority.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(AssertionError, match="candidate authority escalated: delivery_authority"):
        validate(Path("authority.json"))


def test_non_pass_or_same_role_assurance_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _build_authority(tmp_path)
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
