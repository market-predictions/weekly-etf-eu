from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import tools.validate_etf_eu_independent_assurance as assurance_module
from tools.validate_etf_eu_guarded_delivery_git_binding import _require_exact_delivery_head
from tools.validate_etf_eu_independent_assurance import (
    EXPECTED_PULL_API_URL,
    resolve_review,
    validate_review,
)
from tools.validate_etf_eu_pure_projections import (
    expected_projection_bytes,
    validate_projection_bytes,
)

CANDIDATE = "1" * 40
BASE = "0" * 40


def _review(*, pull_url: str = EXPECTED_PULL_API_URL) -> dict:
    return {
        "id": 12345,
        "state": "COMMENTED",
        "body": "\n".join(
            [
                "ETF_EU_INDEPENDENT_ASSURANCE_V1",
                "verdict=PASS",
                "reviewer_role=governance_release_assurance",
                "implementation_role_separate=true",
                f"candidate_sha={CANDIDATE}",
                "expected_base_branch=main",
                f"expected_base_sha={BASE}",
            ]
        ),
        "commit_id": CANDIDATE,
        "html_url": "https://github.com/market-predictions/weekly-etf-eu/pull/120#pullrequestreview-12345",
        "pull_request_url": pull_url,
        "submitted_at": "2026-09-06T12:00:00Z",
        "user": {"login": "chatgpt-codex-connector[bot]"},
    }


def _pull(
    *,
    number: int = 120,
    repo: str = "market-predictions/weekly-etf-eu",
    head_sha: str = CANDIDATE,
    base_branch: str = "main",
    base_sha: str = BASE,
) -> dict:
    return {
        "number": number,
        "url": EXPECTED_PULL_API_URL,
        "head": {"sha": head_sha, "repo": {"full_name": repo}},
        "base": {"ref": base_branch, "sha": base_sha, "repo": {"full_name": repo}},
    }


@pytest.mark.parametrize(
    "pull_url",
    [
        "https://api.github.com/repos/other/repo/pulls/120",
        "https://api.github.com/repos/market-predictions/weekly-etf-eu/pulls/121",
    ],
)
def test_independent_assurance_rejects_wrong_repository_or_pr(pull_url: str) -> None:
    with pytest.raises(AssertionError, match="not bound to market-predictions/weekly-etf-eu PR #120"):
        validate_review(
            _review(pull_url=pull_url),
            candidate_sha=CANDIDATE,
            expected_base_branch="main",
            expected_base_sha=BASE,
        )


@pytest.mark.parametrize(
    "parent_pull",
    [
        _pull(number=121),
        _pull(repo="market-predictions/other"),
        _pull(head_sha="2" * 40),
        _pull(base_branch="release"),
        _pull(base_sha="3" * 40),
    ],
)
def test_resolve_review_rejects_live_parent_pr_identity_drift(
    monkeypatch: pytest.MonkeyPatch, parent_pull: dict
) -> None:
    review = _review()
    review_url = EXPECTED_PULL_API_URL + "/reviews/12345"

    def fake_fetch(url: str) -> dict:
        if url == review_url:
            return review
        if url == EXPECTED_PULL_API_URL:
            return parent_pull
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(assurance_module, "_fetch_github_json", fake_fetch)
    with pytest.raises(AssertionError, match="parent PR"):
        resolve_review(
            evidence_api_url=review_url,
            candidate_sha=CANDIDATE,
            expected_base_branch="main",
            expected_base_sha=BASE,
        )


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def test_delivery_rejects_runtime_change_after_approved_commit(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "fixture@example.invalid")
    _git(tmp_path, "config", "user.name", "Fixture")
    runtime = tmp_path / "runtime" / "current"
    runtime.mkdir(parents=True)
    (runtime / "kernel.py").write_text("SEMANTIC = 1\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "approved report commit")
    approved = _git(tmp_path, "rev-parse", "HEAD")

    (runtime / "kernel.py").write_text("SEMANTIC = 2\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "later unreviewed runtime change")
    current = _git(tmp_path, "rev-parse", "HEAD")

    with pytest.raises(AssertionError, match="HEAD differs from approved report commit"):
        _require_exact_delivery_head(approved, current)


def _review_state() -> dict:
    return {
        "schema_version": "fixture",
        "semantic_state_frozen": True,
        "semantic_mutation_allowed_downstream": False,
        "state_valid": True,
        "blockers": [],
        "report_date": "2026-08-28",
        "portfolio": {
            "nav_eur": 100000.0,
            "invested_market_value_eur": 90000.0,
            "cash_eur": 10000.0,
        },
        "accountability": {
            "cash_weight_pct": 10.0,
            "portfolio_period_return_pct": 1.0,
            "comparator_period_return_pct": 0.5,
            "active_return_pp": 0.5,
            "portfolio_drawdown_pct": -1.0,
            "comparator_drawdown_pct": -1.2,
            "top_contributor": {"ticker": "AAA", "contribution_eur": 100.0},
            "top_detractor": {"ticker": "BBB", "contribution_eur": -50.0},
            "cash_rationale": "Retain cash pending stronger evidence",
            "comparator_id": "vwce",
            "comparator_ticker": "VWCE",
            "comparator_isin": "IE00BK5BQT80",
        },
        "weekly_decision": {
            "action": "HOLD",
            "best_new_or_replace_candidate": None,
            "biggest_current_risk": {"ticker": "AAA", "summary": "Concentration risk"},
        },
        "funded_position_decisions": [
            {
                "ticker": "AAA",
                "action": "HOLD",
                "weight_pct": 90.0,
                "value_eur": 90000.0,
                "fresh_cash_view": "No additional capital",
                "contribution_eur": 100.0,
                "confidence": "medium",
                "rationale": "Current rationale from frozen review state",
                "best_alternative": "None established",
                "invalidation_or_next_trigger": "Next weekly review",
            }
        ],
        "epistemics": {"unresolved": []},
        "sources": {"pricing_artifact": "output/pricing/current.json"},
    }


def test_pure_projection_validator_rejects_semantic_report_edits() -> None:
    review_state_bytes = json.dumps(_review_state(), sort_keys=True).encode("utf-8")
    approved = expected_projection_bytes(review_state_bytes)
    validate_projection_bytes(review_state_bytes, approved)

    tampered_md = dict(approved)
    tampered_md["nl_md"] = tampered_md["nl_md"].replace(b"HOLD", b"SELL", 1)
    with pytest.raises(AssertionError, match="not a pure projection"):
        validate_projection_bytes(review_state_bytes, tampered_md)

    tampered_html = dict(approved)
    tampered_html["en_html"] = tampered_html["en_html"].replace(
        b"Current rationale from frozen review state", b"Different rationale", 1
    )
    with pytest.raises(AssertionError, match="not a pure projection"):
        validate_projection_bytes(review_state_bytes, tampered_html)

    tampered_pdf = dict(approved)
    tampered_pdf["nl_pdf"] = tampered_pdf["nl_pdf"] + b"tampered"
    with pytest.raises(AssertionError, match="not a pure projection"):
        validate_projection_bytes(review_state_bytes, tampered_pdf)
