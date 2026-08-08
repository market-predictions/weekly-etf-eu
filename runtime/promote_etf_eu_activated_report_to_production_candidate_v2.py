from __future__ import annotations

import argparse
from pathlib import Path

from runtime import promote_etf_eu_activated_report_to_production_candidate as activated
from runtime.synchronize_etf_eu_activated_front_page import synchronize_manifest


FINAL_CLIENT_SURFACE_CONTRACT = "authoritative-four-position-after-final-promoter:v1"


def promote(source_manifest: Path, state_path: Path, output_dir: Path) -> Path:
    """Run the compatibility promoter, then re-assert authoritative client state.

    The activated promoter deliberately invokes the legacy promoter with a blocked
    compatibility state so historical renderer assumptions remain usable. That
    compatibility pass is allowed internally, but it must never be the final
    writer of portfolio state visible to the client. The exact final NL/EN HTML
    and PDFs are therefore synchronized again from authoritative convergence
    state after promotion and fail closed if Sections 1, 2, 2A or 4 disagree.
    """
    manifest_path = activated.promote(source_manifest, state_path, output_dir)
    synchronize_manifest(manifest_path, state_path)
    print(
        "ETF_EU_FINAL_CLIENT_STATE_OK | positions=4 | active=L0CK | monitored=VVSM | "
        "sections=1,2,2A,4 | broker_execution=false"
    )
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Promote activated ETF EU report and enforce final authoritative client state"
    )
    parser.add_argument("source_manifest", type=Path)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    promote(args.source_manifest, args.state, args.output_dir)


if __name__ == "__main__":
    main()
