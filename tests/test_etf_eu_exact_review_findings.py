from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from runtime.current.reunderwriting import apply_current_reunderwriting
from tools.validate_etf_eu_guarded_delivery_git_binding import (
    _require_generated_artifact_only_delta,
    _require_semantic_manifest_stability,
)

REPORT_DATE = "2026-08-28"
BASELINE_DATE = "2026-08-21"
REPORT_RUN_ID = "20260828_070000"


def _write_history(path: Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "report_date", "run_id", "ticker", "isin", "shares", "current_weight_pct",
        "reunderwriting_complete", "current_allocation_decision", "fresh_cash_implication",
        "thesis_score", "implementation_score", "thesis_assessment", "best_alternative",
        "factor_overlap_level", "factor_overlap_flag", "hedge_validity_status", "next_review_trigger",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_accountability(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "portfolio_nav_eur", "comparator_close_eur", "comparator_index"])
        writer.writeheader()
        writer.writerow({"date": BASELINE_DATE, "portfolio_nav_eur": "100000", "comparator_close_eur": "168", "comparator_index": "100"})
        writer.writerow({"date": REPORT_DATE, "portfolio_nav_eur": "100100", "comparator_close_eur": "169", "comparator_index": "100.5"})


def _normalized(positions: list[dict]) -> dict:
    return {
        "schema_version": "fixture",
        "state_valid": True,
        "blockers": [],
        "portfolio": {"cash_eur": 10000.0, "nav_eur": 50000.0, "positions": positions},
    }


def _position(ticker: str, isin: str, pnl_pct: float) -> dict:
    return {
        "ticker": ticker,
        "exchange_ticker": ticker,
        "isin": isin,
        "identity_binding_valid": True,
        "pricing_status": "valuation_grade_exact_close",
        "price_date": REPORT_DATE,
        "verification_status": "exact_close_primary_only_verifier_unavailable",
        "unrealized_pnl_pct": pnl_pct,
    }


def _macro(path: Path) -> None:
    path.write_text(json.dumps({"donor_provenance": {"source_report_date": REPORT_DATE}, "regime_label": "fixture"}), encoding="utf-8")


def _bridge() -> dict:
    return {"assessed_lanes": [], "fundable_challengers": [], "best_fundable_challenger": None}


def test_reunderwriting_uses_accountability_baseline_and_not_same_day_memory(tmp_path: Path) -> None:
    recommendation = tmp_path / "recommendation.csv"
    accountability = tmp_path / "accountability.csv"
    macro = tmp_path / "macro.json"
    evidence = tmp_path / "evidence.json"
    _write_history(
        recommendation,
        [
            {
                "report_date": BASELINE_DATE, "run_id": "prior", "ticker": "ZZZ1", "isin": "IE0000000003",
                "shares": "10", "current_weight_pct": "20", "reunderwriting_complete": "True",
                "current_allocation_decision": "REDUCE", "fresh_cash_implication": "Reduce",
                "thesis_score": "", "implementation_score": "", "thesis_assessment": "Historical context only",
                "best_alternative": "None", "factor_overlap_level": "Low", "factor_overlap_flag": "",
                "hedge_validity_status": "Not a hedge", "next_review_trigger": "Weekly review",
            },
            {
                "report_date": REPORT_DATE, "run_id": "same-day-old-run", "ticker": "ZZZ1", "isin": "IE0000000003",
                "shares": "99", "current_weight_pct": "99", "reunderwriting_complete": "True",
                "current_allocation_decision": "CLOSE", "fresh_cash_implication": "Close",
                "thesis_score": "1", "implementation_score": "1", "thesis_assessment": "Same-day stale rerun output",
                "best_alternative": "Same-day", "factor_overlap_level": "High", "factor_overlap_flag": "yes",
                "hedge_validity_status": "Not a hedge", "next_review_trigger": "Immediate",
            },
        ],
    )
    _write_accountability(accountability)
    _macro(macro)

    result = apply_current_reunderwriting(
        _normalized([_position("ZZZ1", "IE0000000003", 1.0)]),
        recommendation_history_path=recommendation,
        accountability_history_path=accountability,
        macro_pack_path=macro,
        discovery_bridge=_bridge(),
        report_date=REPORT_DATE,
        run_id="current",
        evidence_output_path=evidence,
    )
    position = result["portfolio"]["positions"][0]
    assert position["current_allocation_decision"] == "hold"
    assert position["reunderwriting_complete"] is True
    assert position["reunderwriting_memory_report_date"] == BASELINE_DATE
    assert position["reunderwriting_memory_shares"] == 10.0
    assert position["reunderwriting_memory_action"] == "REDUCE"
    assert result["current_reunderwriting"]["accountability_baseline_date"] == BASELINE_DATE


def test_historical_scores_cannot_change_current_loss_review_decision(tmp_path: Path) -> None:
    recommendation = tmp_path / "recommendation.csv"
    accountability = tmp_path / "accountability.csv"
    macro = tmp_path / "macro.json"
    evidence = tmp_path / "evidence.json"
    _write_history(
        recommendation,
        [
            {
                "report_date": BASELINE_DATE, "run_id": "prior", "ticker": "LOW", "isin": "IE0000000004",
                "shares": "10", "current_weight_pct": "20", "reunderwriting_complete": "True",
                "current_allocation_decision": "HOLD", "fresh_cash_implication": "Hold",
                "thesis_score": "1", "implementation_score": "1", "thesis_assessment": "Low historical score",
                "best_alternative": "None", "factor_overlap_level": "Low", "factor_overlap_flag": "",
                "hedge_validity_status": "Not a hedge", "next_review_trigger": "Weekly review",
            },
            {
                "report_date": BASELINE_DATE, "run_id": "prior", "ticker": "HIGH", "isin": "IE0000000005",
                "shares": "10", "current_weight_pct": "20", "reunderwriting_complete": "True",
                "current_allocation_decision": "HOLD", "fresh_cash_implication": "Hold",
                "thesis_score": "5", "implementation_score": "5", "thesis_assessment": "High historical score",
                "best_alternative": "None", "factor_overlap_level": "Low", "factor_overlap_flag": "",
                "hedge_validity_status": "Not a hedge", "next_review_trigger": "Weekly review",
            },
        ],
    )
    _write_accountability(accountability)
    _macro(macro)

    result = apply_current_reunderwriting(
        _normalized([
            _position("LOW", "IE0000000004", -11.0),
            _position("HIGH", "IE0000000005", -11.0),
        ]),
        recommendation_history_path=recommendation,
        accountability_history_path=accountability,
        macro_pack_path=macro,
        discovery_bridge=_bridge(),
        report_date=REPORT_DATE,
        run_id="current",
        evidence_output_path=evidence,
    )
    by_ticker = {row["ticker"]: row for row in result["portfolio"]["positions"]}
    for ticker in ("LOW", "HIGH"):
        assert by_ticker[ticker]["current_allocation_decision"] == "review"
        assert by_ticker[ticker]["reunderwriting_blockers"] == ["current_loss_review_trigger"]
    assert result["state_valid"] is False


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_manifest(root: Path) -> None:
    current = root / "output" / "current"
    artifacts = {
        "review_state": {"path": "output/current/review_state.json", "sha256": _sha(current / "review_state.json"), "size_bytes": (current / "review_state.json").stat().st_size},
        "nl_md": {"path": "output/current/report_nl.md", "sha256": _sha(current / "report_nl.md"), "size_bytes": (current / "report_nl.md").stat().st_size},
        "en_md": {"path": "output/current/report_en.md", "sha256": _sha(current / "report_en.md"), "size_bytes": (current / "report_en.md").stat().st_size},
        "nl_html": {"path": "output/current/report_nl.html", "sha256": _sha(current / "report_nl.html"), "size_bytes": (current / "report_nl.html").stat().st_size},
        "en_html": {"path": "output/current/report_en.html", "sha256": _sha(current / "report_en.html"), "size_bytes": (current / "report_en.html").stat().st_size},
        "nl_pdf": {"path": "output/current/report_nl.pdf", "sha256": _sha(current / "report_nl.pdf"), "size_bytes": (current / "report_nl.pdf").stat().st_size},
        "en_pdf": {"path": "output/current/report_en.pdf", "sha256": _sha(current / "report_en.pdf"), "size_bytes": (current / "report_en.pdf").stat().st_size},
    }
    manifest = {
        "schema_version": "etf_eu_thin_kernel_manifest_v1",
        "run_id": REPORT_RUN_ID,
        "report_date": REPORT_DATE,
        "report_suffix": "260828",
        "semantic_source": "output/current/review_state.json",
        "semantic_state_frozen": True,
        "post_freeze_semantic_mutation": False,
        "current_kernel": "runtime/current",
        "candidate_builder": "tools/build_etf_eu_thin_kernel_package.py",
        "production_renderer": "runtime/current/render.py",
        "artifacts": artifacts,
        "evidence": {
            "pricing": "output/pricing/current.json",
            "accountability_history": "output/etf_eu_accountability_history.csv",
            "recommendation_history": "output/etf_eu_recommendation_scorecard.csv",
        },
        "authority": {
            "portfolio_mutation": False,
            "trade_ledger_write": False,
            "real_broker_execution": False,
            "delivery_authority": False,
            "smtp_send": False,
            "funding_authority": False,
        },
    }
    (current / "manifest.json").write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")


def _init_semantic_candidate(root: Path) -> str:
    _git(root, "init")
    _git(root, "config", "user.email", "fixture@example.invalid")
    _git(root, "config", "user.name", "Fixture")
    (root / "runtime" / "current").mkdir(parents=True)
    (root / "runtime" / "current" / "kernel.py").write_text("SEMANTIC = 1\n", encoding="utf-8")
    current = root / "output" / "current"
    current.mkdir(parents=True)
    (current / "review_state.json").write_text('{"frozen":true}\n', encoding="utf-8")
    for name, content in {
        "report_nl.md": "nl\n", "report_en.md": "en\n",
        "report_nl.html": "<html>nl</html>\n", "report_en.html": "<html>en</html>\n",
        "report_nl.pdf": "%PDF nl\n", "report_en.pdf": "%PDF en\n",
    }.items():
        (current / name).write_text(content, encoding="utf-8")
    (root / "output" / "etf_eu_portfolio_state.json").write_text('{"cash_eur":1000}\n', encoding="utf-8")
    (root / "output" / "etf_eu_recommendation_scorecard.csv").write_text("report_date,ticker\n", encoding="utf-8")
    (root / "output" / "etf_eu_accountability_history.csv").write_text("date,portfolio_nav_eur\n", encoding="utf-8")
    (root / "output" / "pricing").mkdir(parents=True)
    (root / "output" / "pricing" / "current.json").write_text('{"price":1}\n', encoding="utf-8")
    _write_manifest(root)
    _git(root, "add", ".")
    _git(root, "commit", "-m", "assured semantic candidate")
    return _git(root, "rev-parse", "HEAD")


def test_guarded_delivery_allows_only_pure_projection_delta(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    candidate = _init_semantic_candidate(tmp_path)
    current = tmp_path / "output" / "current"
    (current / "report_nl.md").write_text("regenerated nl\n", encoding="utf-8")
    _write_manifest(tmp_path)
    safety = tmp_path / "output" / "evidence" / REPORT_RUN_ID / "client_surface_safety.json"
    safety.parent.mkdir(parents=True)
    safety.write_text('{"status":"PASS"}\n', encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "pure projection refresh")
    approved = _git(tmp_path, "rev-parse", "HEAD")
    monkeypatch.chdir(tmp_path)
    _require_semantic_manifest_stability(candidate, approved)
    changed = _require_generated_artifact_only_delta(candidate, approved, report_run_id=REPORT_RUN_ID)
    assert "output/current/report_nl.md" in changed
    assert "output/current/manifest.json" in changed
    assert f"output/evidence/{REPORT_RUN_ID}/client_surface_safety.json" in changed


@pytest.mark.parametrize(
    "path",
    [
        "output/etf_eu_portfolio_state.json",
        "output/etf_eu_recommendation_scorecard.csv",
        "output/etf_eu_accountability_history.csv",
        "output/pricing/current.json",
        "output/current/review_state.json",
    ],
)
def test_guarded_delivery_rejects_semantic_output_mutation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, path: str) -> None:
    candidate = _init_semantic_candidate(tmp_path)
    target = tmp_path / path
    target.write_text(target.read_text(encoding="utf-8") + "mutated\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "unreviewed semantic output mutation")
    approved = _git(tmp_path, "rev-parse", "HEAD")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(AssertionError, match="unreviewed semantic changes"):
        _require_generated_artifact_only_delta(candidate, approved, report_run_id=REPORT_RUN_ID)


def test_guarded_delivery_rejects_semantic_manifest_change_even_on_allowlisted_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    candidate = _init_semantic_candidate(tmp_path)
    manifest_path = tmp_path / "output" / "current" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["evidence"]["pricing"] = "output/pricing/other.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "semantic manifest drift")
    approved = _git(tmp_path, "rev-parse", "HEAD")
    monkeypatch.chdir(tmp_path)
    assert _require_generated_artifact_only_delta(candidate, approved, report_run_id=REPORT_RUN_ID) == ["output/current/manifest.json"]
    with pytest.raises(AssertionError, match="manifest semantic fields changed"):
        _require_semantic_manifest_stability(candidate, approved)
