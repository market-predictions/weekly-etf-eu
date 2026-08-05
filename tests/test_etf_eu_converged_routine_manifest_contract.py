from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_etf_eu_converged_routine_manifest import validate


FALSE_AUTHORITY = {
    "portfolio_mutation": False,
    "ledger_write": False,
    "funding_authority": False,
    "activation_authority": False,
    "execution_authority": False,
    "production_delivery_authority": False,
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def position(ticker: str, isin: str) -> dict:
    return {"ticker": ticker, "isin": isin, "shares": 1}


class RoutineManifestContractTests(unittest.TestCase):
    def _fixture(self, root: Path, *, activated: bool) -> tuple[dict, dict, Path]:
        positions = [
            position("VWCE", "IE00BK5BQT80"),
            position("EUNA", "IE00BDBRDM35"),
            position("SXR8", "IE00B5BMR087"),
        ]
        stage = {
            "value": "blocked",
            "activated_tickers": [],
            "remaining_monitored_tickers": ["VVSM", "L0CK"],
            "executable_trade_intents": [],
        }
        if activated:
            positions.append(position("L0CK", "IE00BG0J4C88"))
            stage = {
                "value": "partially_activated",
                "activated_tickers": ["L0CK"],
                "remaining_monitored_tickers": ["VVSM"],
                "executable_trade_intents": [],
            }

        state = {
            "schema_version": "etf_eu_production_convergence_state_v1",
            "run_id": "20260805_test",
            "report_date": "2026-08-05",
            "official_portfolio": {
                "positions": positions,
                "position_count": len(positions),
                "nav_eur": 100000.0,
                "cash_eur": 2500.0,
                "invested_market_value_eur": 97500.0,
            },
            "promoted_exposures": [{}] * 6,
            "strategy": {
                "mapped_promoted_exposure_count": 6,
                "unmapped_promoted_exposure_count": 0,
            },
            "stage_1_review_candidates": [{}, {}],
            "stage_1_decision": stage,
            "authority": dict(FALSE_AUTHORITY),
        }
        state_path = root / "state.json"
        state_path.write_text(json.dumps(state), encoding="utf-8")

        package_files: dict[str, dict] = {}
        for role, suffix in (
            ("nl_html", ".html"),
            ("nl_pdf", ".pdf"),
            ("en_html", "_en.html"),
            ("en_pdf", "_en.pdf"),
        ):
            path = root / f"{role}{suffix}"
            path.write_bytes((b"%PDF-1.7\n" if role.endswith("pdf") else b"<!doctype html>") + b"x" * 2048)
            package_files[role] = {
                "path": str(path),
                "sha256": sha(path),
                "size_bytes": path.stat().st_size,
            }

        artifacts: dict[str, dict] = {}
        for role in ("pricing_artifact", "macro_policy_pack", "client_report_manifest"):
            path = root / f"{role}.json"
            path.write_text(json.dumps({"role": role}), encoding="utf-8")
            artifacts[role] = {"path": str(path), "sha256": sha(path)}
        artifacts["production_convergence_state"] = {
            "path": str(state_path),
            "sha256": sha(state_path),
        }

        manifest = {
            "schema_version": "etf_eu_routine_run_manifest_v3_converged",
            "report_engine": "production_convergence_v1",
            "report_section_count": 19,
            "languages": ["nl", "en"],
            "expected_attachment_count": 4,
            "run_id": state["run_id"],
            "report_date": state["report_date"],
            "report_suffix": "260805",
            "source_commit_sha": "a" * 40,
            "donor_commit_sha": "b" * 40,
            "files": package_files,
            "state_artifacts": artifacts,
            "portfolio_snapshot": {
                "position_count": len(positions),
                "positions": positions,
                "nav_eur": 100000.0,
                "cash_eur": 2500.0,
                "invested_market_value_eur": 97500.0,
                "pricing_close_dates": ["2026-08-05"],
                "official_portfolio_state_sha256": "c" * 64,
                "official_trade_ledger_sha256": "d" * 64,
            },
            "strategy_snapshot": {
                "current_promoted_exposure_count": 6,
                "mapped_promoted_exposure_count": 6,
                "unmapped_promoted_exposure_count": 0,
                "stage_1_review_candidate_count": 2,
                "stage_1_decision": stage["value"],
                "activated_tickers": stage["activated_tickers"],
                "remaining_monitored_tickers": stage["remaining_monitored_tickers"],
                "stage_1_activation_recorded": activated,
                "current_activation_authority": False,
                "executable_trade_intents": [],
            },
            "package_status": "generated_pending_machine_and_visual_review",
            "ready_for_controlled_delivery": False,
            "delivery_authority": False,
            "smtp_transport_success": False,
            "independent_receipt_confirmed": False,
            **FALSE_AUTHORITY,
        }
        return manifest, state, state_path

    def test_blocked_three_position_manifest_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest, state, state_path = self._fixture(Path(tmp), activated=False)
            self.assertEqual(validate(manifest, state, state_path), [])

    def test_partially_activated_four_position_manifest_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest, state, state_path = self._fixture(Path(tmp), activated=True)
            self.assertEqual(validate(manifest, state, state_path), [])

    def test_planted_position_roster_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest, state, state_path = self._fixture(Path(tmp), activated=True)
            manifest["portfolio_snapshot"]["positions"] = manifest["portfolio_snapshot"]["positions"][:-1]
            blockers = validate(manifest, state, state_path)
            self.assertIn("portfolio position identity roster differs from convergence state", blockers)

    def test_planted_stage_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest, state, state_path = self._fixture(Path(tmp), activated=True)
            manifest["strategy_snapshot"]["stage_1_decision"] = "blocked"
            blockers = validate(manifest, state, state_path)
            self.assertIn("Stage-1 decision differs from convergence state", blockers)

    def test_planted_current_activation_authority_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest, state, state_path = self._fixture(Path(tmp), activated=True)
            manifest["strategy_snapshot"]["current_activation_authority"] = True
            blockers = validate(manifest, state, state_path)
            self.assertIn("current Stage-1 activation authority must be false", blockers)

    def test_planted_delivery_authority_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest, state, state_path = self._fixture(Path(tmp), activated=True)
            manifest["production_delivery_authority"] = True
            blockers = validate(manifest, state, state_path)
            self.assertIn("manifest current authority production_delivery_authority must be false", blockers)


if __name__ == "__main__":
    unittest.main()
