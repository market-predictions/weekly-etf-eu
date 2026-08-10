from __future__ import annotations

from pathlib import Path


WORKFLOW_DIR = Path(".github/workflows")
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
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> None:
    _require(CANDIDATE.exists(), "canonical candidate workflow missing")
    _require(TRANSPORT.exists(), "canonical controlled transport workflow missing")

    active_names = {path.name for path in WORKFLOW_DIR.glob("*.yml")}
    leaked = sorted(RETIRED_ACTIVE_PATHS & active_names)
    _require(not leaked, f"retired workflows remain executable: {leaked}")

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
    for path in WORKFLOW_DIR.glob("*.yml"):
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
        f" | retired_disabled={len(RETIRED_ACTIVE_PATHS)}"
        " | candidate_route=1 | delivery_route=1"
    )


def main() -> None:
    validate()


if __name__ == "__main__":
    main()
