from __future__ import annotations

import json
from pathlib import Path

from runtime.current.review_state import _period_position_contributions


def _state(protected_path: Path, *, current_shares: int = 110) -> dict:
    return {
        "sources": {"protected_portfolio_state": str(protected_path)},
        "portfolio": {
            "positions": [
                {
                    "ticker": "AAA",
                    "exchange_ticker": "AAA",
                    "shares": current_shares,
                    "market_value_eur": 1200.0,
                    "reunderwriting_memory_report_date": "2026-08-01",
                    "reunderwriting_memory_shares": 100,
                    "reunderwriting_memory_weight_pct": 10.0,
                }
            ]
        },
    }


def _write_flow_fixture(tmp_path: Path) -> Path:
    decision_path = tmp_path / "allocation.json"
    decision_path.write_text(
        json.dumps(
            {
                "schema_version": "etf_eu_current_allocation_decision_v1",
                "run_id": "20260805_120000",
                "report_date": "2026-08-05",
                "decisions": [
                    {
                        "action": "buy",
                        "exchange_ticker": "AAA",
                        "shares_delta": 10,
                        "trade_value_eur": 110.0,
                    }
                ],
                "authority": {
                    "explicit_current_allocation_decision": True,
                    "model_portfolio_only": True,
                    "real_broker_execution": False,
                },
            }
        ),
        encoding="utf-8",
    )
    protected_path = tmp_path / "portfolio.json"
    protected_path.write_text(
        json.dumps(
            {
                "last_model_capital_activation": {
                    "run_id": "20260805_120000",
                    "report_date": "2026-08-05",
                    "decision": str(decision_path),
                }
            }
        ),
        encoding="utf-8",
    )
    return protected_path


def test_position_contribution_reconciles_authorized_internal_trade_flow(tmp_path: Path) -> None:
    protected_path = _write_flow_fixture(tmp_path)
    contributions, unresolved = _period_position_contributions(
        _state(protected_path),
        prior_nav=10000.0,
        baseline_date="2026-08-01",
        report_date="2026-08-08",
    )
    assert unresolved == []
    assert contributions == [
        {
            "ticker": "AAA",
            "contribution_eur": 90.0,
            "flow_eur": 110.0,
            "flow_evidence_ref": str(tmp_path / "allocation.json"),
        }
    ]


def test_position_contribution_still_fails_closed_without_matching_flow_evidence(tmp_path: Path) -> None:
    protected_path = _write_flow_fixture(tmp_path)
    state = _state(protected_path, current_shares=111)
    contributions, unresolved = _period_position_contributions(
        state,
        prior_nav=10000.0,
        baseline_date="2026-08-01",
        report_date="2026-08-08",
    )
    assert contributions == []
    assert unresolved == ["position_flow_share_delta_mismatch:AAA"]
