from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.build_etf_eu_guarded_delivery_authority import build_authority
from tools.validate_etf_eu_client_surface_safety import validate as validate_safety
from tools.validate_etf_eu_guarded_delivery_authority import validate as validate_authority

CANDIDATE = "1" * 40
BASE = "0" * 40
BASE_BRANCH = "main"


def _plain_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_package(root: Path, *, nl_text: str = "Veilige NL review", en_text: str = "Safe EN review") -> Path:
    current = root / "output" / "current"
    current.mkdir(parents=True)
    files = {
        "nl_md": ("report_nl.md", nl_text),
        "en_md": ("report_en.md", en_text),
        "nl_html": ("report_nl.html", f"<html><body>{nl_text}</body></html>"),
        "en_html": ("report_en.html", f"<html><body>{en_text}</body></html>"),
        "nl_pdf": ("report_nl.pdf", "%PDF nl"),
        "en_pdf": ("report_en.pdf", "%PDF en"),
        "review_state": ("review_state.json", "{}"),
    }
    artifacts = {}
    for key, (name, content) in files.items():
        path = current / name
        path.write_bytes(content.encode("utf-8"))
        artifacts[key] = {
            "path": str(path.relative_to(root)),
            "sha256": _plain_sha(path),
            "size_bytes": path.stat().st_size,
        }
    manifest = {
        "schema_version": "etf_eu_thin_kernel_manifest_v1",
        "run_id": "20260831_070000",
        "report_date": "2026-08-31",
        "report_suffix": "260831",
        "semantic_source": artifacts["review_state"]["path"],
        "semantic_state_frozen": True,
        "post_freeze_semantic_mutation": False,
        "artifacts": artifacts,
        "authority": {
            "portfolio_mutation": False,
            "trade_ledger_write": False,
            "real_broker_execution": False,
            "delivery_authority": False,
            "smtp_send": False,
            "funding_authority": False,
        },
    }
    path = current / "manifest.json"
    path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    return path


def _write_proxy_map(root: Path) -> Path:
    path = root / "config" / "proxy.yml"
    path.parent.mkdir(parents=True)
    path.write_text("schema_version: test\nproxy_mappings:\n  - donor_proxies: [SPY, SMH]\n", encoding="utf-8")
    return path


def _write_safety(root: Path, manifest: Path, proxy_map: Path) -> Path:
    result = validate_safety(manifest_path=manifest, proxy_map_path=proxy_map)
    path = root / "output" / "evidence" / "20260831_070000" / "client_surface_safety.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _write_review(root: Path, *, candidate: str = CANDIDATE, base_branch: str = BASE_BRANCH, base_sha: str = BASE, verdict: str = "PASS") -> Path:
    path = root / "review.json"
    path.write_text(json.dumps({
        "id": 12345,
        "state": "COMMENTED",
        "body": "\n".join([
            "ETF_EU_INDEPENDENT_ASSURANCE_V1",
            f"verdict={verdict}",
            "reviewer_role=governance_release_assurance",
            "implementation_role_separate=true",
            f"candidate_sha={candidate}",
            f"expected_base_branch={base_branch}",
            f"expected_base_sha={base_sha}",
        ]),
        "commit_id": candidate,
        "html_url": "https://github.com/market-predictions/weekly-etf-eu/pull/120#pullrequestreview-12345",
        "pull_request_url": "https://api.github.com/repos/market-predictions/weekly-etf-eu/pulls/120",
        "submitted_at": "2026-09-06T12:00:00Z",
        "user": {"login": "chatgpt-codex-connector[bot]"},
    }), encoding="utf-8")
    return path


def test_client_surface_safety_passes_clean_frozen_surfaces(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    manifest = _write_package(tmp_path)
    proxy_map = _write_proxy_map(tmp_path)
    result = validate_safety(manifest_path=Path(manifest.relative_to(tmp_path)), proxy_map_path=Path(proxy_map.relative_to(tmp_path)))
    assert result["valid"] is True
    assert result["status"] == "PASS"
    assert result["exposed_donor_proxies"] == []
    assert all(value is False for value in result["client_surface_safety"].values())


@pytest.mark.parametrize(
    ("text", "blocker"),
    [
        ("SPY remains strongest", "main_surface_us_proxy_exposure"),
        ("Best candidate: TBD", "main_surface_tbd_candidate_exposure"),
        ("Current price: nan", "nan_price_in_client_surface"),
        ("Report sent", "stale_delivery_wording_present"),
    ],
)
def test_client_surface_safety_fails_closed_on_delivery_surface_leaks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str, blocker: str
) -> None:
    monkeypatch.chdir(tmp_path)
    manifest = _write_package(tmp_path, en_text=text)
    proxy_map = _write_proxy_map(tmp_path)
    result = validate_safety(manifest_path=Path(manifest.relative_to(tmp_path)), proxy_map_path=Path(proxy_map.relative_to(tmp_path)))
    assert result["valid"] is False
    assert blocker in result["blockers"]


def _build_current_authority(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, **overrides) -> tuple[Path, Path]:
    monkeypatch.chdir(tmp_path)
    manifest = _write_package(tmp_path)
    proxy_map = _write_proxy_map(tmp_path)
    manifest_rel = Path(manifest.relative_to(tmp_path))
    safety = _write_safety(tmp_path, manifest_rel, Path(proxy_map.relative_to(tmp_path)))
    review = _write_review(tmp_path)
    output = Path("output/delivery_authorization/current.json")
    kwargs = {
        "thin_kernel_manifest_path": manifest_rel,
        "safety_evidence_path": Path(safety.relative_to(tmp_path)),
        "assured_candidate_head_sha": CANDIDATE,
        "expected_base_branch": BASE_BRANCH,
        "expected_base_sha": BASE,
        "approved_report_commit_sha": "2" * 40,
        "assurance_evidence_path": review,
        "principal_authorization_ref": "principal-explicit-authorization-reference",
        "confirm_principal_guarded_send_authorization": True,
        "output": output,
    }
    kwargs.update(overrides)
    build_authority(**kwargs)
    return output, review


def test_current_authority_builder_produces_validator_accepted_manifest_bound_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output, review = _build_current_authority(tmp_path, monkeypatch)
    payload = validate_authority(output, assurance_evidence_path=review)
    assert payload["status"] == "APPROVED_FOR_GUARDED_DELIVERY"
    assert payload["delivery_authority"] is True
    assert payload["independent_assurance"]["reviewed_head_sha"] == CANDIDATE
    assert payload["independent_assurance"]["expected_base_branch"] == BASE_BRANCH
    assert payload["independent_assurance"]["expected_base_sha"] == BASE
    assert payload["independent_assurance"]["evidence_binding_sha256"].startswith("sha256:")
    assert payload["principal_guarded_send_authorization"]["approved"] is True
    assert payload["client_surface_safety"]["evidence_sha256"].startswith("sha256:")


def test_current_authority_builder_refuses_missing_principal_confirmation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(RuntimeError, match="principal guarded-send authorization"):
        _build_current_authority(tmp_path, monkeypatch, confirm_principal_guarded_send_authorization=False)


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"expected_base_branch": "release"}, "base branch mismatch"),
        ({"expected_base_sha": "3" * 40}, "base sha mismatch"),
        ({"assured_candidate_head_sha": "4" * 40}, "commit/candidate mismatch|body candidate mismatch"),
    ],
)
def test_current_authority_builder_rejects_assurance_tuple_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, override: dict[str, object], message: str
) -> None:
    with pytest.raises(RuntimeError, match=message):
        _build_current_authority(tmp_path, monkeypatch, **override)


def test_current_authority_builder_rejects_non_pass_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    manifest = _write_package(tmp_path)
    proxy_map = _write_proxy_map(tmp_path)
    safety = _write_safety(tmp_path, Path(manifest.relative_to(tmp_path)), Path(proxy_map.relative_to(tmp_path)))
    review = _write_review(tmp_path, verdict="FAIL")
    with pytest.raises(RuntimeError, match="verdict must be PASS"):
        build_authority(
            thin_kernel_manifest_path=Path(manifest.relative_to(tmp_path)),
            safety_evidence_path=Path(safety.relative_to(tmp_path)),
            assured_candidate_head_sha=CANDIDATE,
            expected_base_branch=BASE_BRANCH,
            expected_base_sha=BASE,
            approved_report_commit_sha="2" * 40,
            assurance_evidence_path=review,
            principal_authorization_ref="principal-explicit-authorization-reference",
            confirm_principal_guarded_send_authorization=True,
            output=Path("output/delivery_authorization/current.json"),
        )
