from __future__ import annotations

from pathlib import Path


WORKFLOW_DIR = Path(".github/workflows")
ARCHIVE_DIR = Path("archive/workflows")
ARCHIVE_POLICY = Path("archive/README.md")
CANDIDATE = WORKFLOW_DIR / "run-weekly-etf-eu-routine.yml"
TRANSPORT = WORKFLOW_DIR / "send-weekly-etf-eu-controlled-transport.yml"

RETIRED_ACTIVE_PATHS = {
    "activate-etf-eu-stage1-20260804.yml",
    "run-etf-eu-capital-activation.yml",
    "run-weekly-etf-eu-20260804-fresh-send.yml",
    "run-weekly-etf-eu-routine-preview-recovery.yml",
    "run-weekly-etf-eu-routine-preview.yml",
    "send-etf-eu-shadow-cid-delivery.yml",
    "send-weekly-etf-eu-corrected-report.yml",
    "send-weekly-etf-eu-current-package.yml",
    "send-weekly-etf-eu-report.yml",
    "send-weekly-report-split-test.yml",
    "send-weekly-report-split-test_OLD.yml",
    "send-weekly-report.yml",
    "repair-weekly-etf-eu-client-surface.yml",
    "repair-weekly-etf-eu-routine-pdf.yml",
    "render-weekly-etf-eu-client-grade-v2-evidence.yml",
    "preview-weekly-etf-eu-20260803-expanded-v4.yml",
    "preview-weekly-etf-eu-converged-routine.yml",
    "export-etf-eu-preview-artifact-20260717.yml",
    "refresh-etf-state-from-report.yml",
    "validate-etf-eu-allocator-report-shadow.yml",
    # Retired after PR #91 post-merge exact-main validation exposed US donor execution leakage.
    "persist-etf-pricing-audit.yml",
    "validate-etf-runtime.yml",
    "validate-etf-lane-breadth.yml",
}

FORENSIC_ARCHIVE_PATHS = {
    "persist-etf-pricing-audit.yml",
    "validate-etf-runtime.yml",
    "validate-etf-lane-breadth.yml",
}

PROHIBITED_US_DONOR_EXECUTION_TOKENS = (
    "pricing.run_pricing_pass",
    "output/etf_portfolio_state.json",
    "weekly_analysis_pro_",
    "send_report.py",
    "import send_report",
    "etf.txt",
    "etf-pro.txt",
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _active_workflows() -> list[Path]:
    return sorted(set(WORKFLOW_DIR.glob("*.yml")) | set(WORKFLOW_DIR.glob("*.yaml")))


def validate() -> None:
    _require(CANDIDATE.exists(), "canonical candidate workflow missing")
    _require(TRANSPORT.exists(), "canonical controlled transport workflow missing")
    _require(ARCHIVE_POLICY.exists(), "forensic archive policy missing")

    active_paths = _active_workflows()
    active_names = {path.name for path in active_paths}
    leaked = sorted(RETIRED_ACTIVE_PATHS & active_names)
    _require(not leaked, f"retired workflows remain executable: {leaked}")

    # Architecture V2 deliberately removes the former `.yml.disabled` pseudo-workflow
    # graveyard. Git history is the default provenance source. Only the three workflows
    # needed to explain the 2026-08-10 donor-runtime incident remain as explicit,
    # non-executable forensic artifacts outside `.github/workflows/`.
    missing_forensic = sorted(
        name for name in FORENSIC_ARCHIVE_PATHS
        if not (ARCHIVE_DIR / name).exists()
    )
    _require(not missing_forensic, f"forensic workflow archive evidence missing: {missing_forensic}")

    stale_disabled = sorted(path.name for path in WORKFLOW_DIR.glob("*.disabled"))
    _require(not stale_disabled, f"retired .disabled workflow graveyard remains: {stale_disabled}")

    donor_runtime_leaks: list[str] = []
    for path in active_paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        folded = text.casefold()
        for token in PROHIBITED_US_DONOR_EXECUTION_TOKENS:
            if token.casefold() in folded:
                donor_runtime_leaks.append(f"{path.name}:{token}")
    _require(
        not donor_runtime_leaks,
        "US Weekly ETF donor execution token(s) remain in active ETF EU workflows: "
        + ", ".join(donor_runtime_leaks),
    )

    candidate = CANDIDATE.read_text(encoding="utf-8")
    for forbidden in (
        "git push origin HEAD:main",
        "build_etf_eu_release_assurance.py",
        "validate_etf_eu_release_assurance.py",
        "runtime.send_etf_eu_controlled_report",
        "runtime.send_etf_eu_rel",
        "--mode send",
        "MRKT_RPRTS_SMTP_PASS",
    ):
        _require(forbidden not in candidate, f"candidate workflow contains forbidden authority token: {forbidden}")
    for required in (
        "ETF_EU_CANDIDATE_BUILD_REFUSES_MAIN",
        "ETF_EU_CANDIDATE_ONLY=PASS",
        "ETF_EU_INDEPENDENT_ASSURANCE_REQUIRED=true",
        "ETF_EU_DELIVERY_AUTHORITY=false",
        'git push origin "HEAD:${ETF_EU_CANDIDATE_BRANCH}"',
    ):
        _require(required in candidate, f"candidate workflow missing boundary: {required}")

    transport = TRANSPORT.read_text(encoding="utf-8")
    for required in (
        "ETF_EU_CONTROLLED_TRANSPORT_REQUIRES_MAIN",
        "delivery_authority_path",
        "validate_etf_eu_guarded_delivery_authority.py",
        "ETF_EU_APPROVED_REPORT_COMMIT",
        "git merge-base --is-ancestor",
        "confirm_guarded_send_second",
        "runtime.send_etf_eu_controlled_report",
        "--nl-md",
        "--en-md",
    ):
        _require(required in transport, f"controlled transport missing authority boundary: {required}")
    for forbidden in (
        "runtime.render_etf_eu_delivery_package",
        "build_etf_eu_release_assurance.py",
    ):
        _require(forbidden not in transport, f"controlled transport may not create its own release authority: {forbidden}")

    active_send_invocations: list[str] = []
    for path in active_paths:
        text = path.read_text(encoding="utf-8")
        if "runtime.send_etf_eu_controlled_report" in text or "runtime.send_etf_eu_rel" in text or "--mode send" in text:
            active_send_invocations.append(path.name)
    _require(
        active_send_invocations == [TRANSPORT.name],
        f"unexpected executable delivery path(s): {active_send_invocations}",
    )

    print(
        "ETF_EU_WORKFLOW_AUTHORITY=PASS"
        f" | active_workflows={len(active_names)}"
        f" | retired_removed={len(RETIRED_ACTIVE_PATHS)}"
        f" | forensic_archived={len(FORENSIC_ARCHIVE_PATHS)}"
        " | disabled_graveyard=0 | candidate_route=1 | delivery_route=1 | us_donor_execution_routes=0"
    )


def main() -> None:
    validate()


if __name__ == "__main__":
    main()
