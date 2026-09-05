from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

import pytest

from runtime.current.reunderwriting import apply_current_reunderwriting
from tools.validate_etf_eu_guarded_delivery_git_binding import _require_output_only_delta

REPORT_DATE = "2026-08-28"
BASELINE_DATE = "2026-08-21"


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
        # Same-day rows are deliberately excluded by the accountability contract.
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


def test_guarded_delivery_allows_output_only_report_commit_but_rejects_unreviewed_semantic_delta(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "fixture@example.invalid")
    _git(tmp_path, "config", "user.name", "Fixture")
    runtime = tmp_path / "runtime" / "current"
    runtime.mkdir(parents=True)
    (runtime / "kernel.py").write_text("SEMANTIC = 1\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "candidate")
    candidate = _git(tmp_path, "rev-parse", "HEAD")

    output = tmp_path / "output" / "current"
    output.mkdir(parents=True)
    (output / "report.md").write_text("bound report\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "report output")
    approved = _git(tmp_path, "rev-parse", "HEAD")

    monkeypatch.chdir(tmp_path)
    assert _require_output_only_delta(candidate, approved) == ["output/current/report.md"]

    (runtime / "kernel.py").write_text("SEMANTIC = 2\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "unreviewed semantic change")
    stale_approved = _git(tmp_path, "rev-parse", "HEAD")
    with pytest.raises(AssertionError, match="unreviewed semantic changes"):
        _require_output_only_delta(candidate, stale_approved)
