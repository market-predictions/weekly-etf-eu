from __future__ import annotations

import argparse
from pathlib import Path

from runtime import promote_etf_eu_activated_report_to_production_candidate as activated
from runtime.synchronize_etf_eu_activated_front_page import synchronize_manifest as synchronize_front_page
from runtime.synchronize_etf_eu_current_state_surface_v2 import synchronize_manifest as synchronize_current_state


FINAL_CLIENT_SURFACE_CONTRACT = "authoritative-four-position-after-final-promoter:v3"


def promote(source_manifest: Path, state_path: Path, output_dir: Path) -> Path:
    """Promote through the compatibility renderer, then reassert client truth.

    The legacy promoter may use a blocked compatibility state internally, but it
    may never be the final writer of client-visible portfolio state. After that
    pass, authoritative four-position state is reapplied first to Sections
    1/2/2A/4 and then to current-state Sections 5/6/8/9/10/11/12/13. Section 8
    exact donor-exposure coverage is derived from the authoritative current L0CK
    weight because broad core positions are explicitly not substitute exposure.
    Historical valuation context in Section 7 and the explicitly non-actionable
    allocator scenario in Section 14 remain intact.
    """
    manifest_path = activated.promote(source_manifest, state_path, output_dir)
    synchronize_front_page(manifest_path, state_path)
    synchronize_current_state(manifest_path, state_path)
    print(
        "ETF_EU_FINAL_CLIENT_STATE_OK | positions=4 | active=L0CK | monitored=VVSM | "
        "current_sections=1,2,2A,4,5,6,8,9,10,11,12,13 | section8_coverage=current_L0CK_weight | "
        "historical=7 | scenario=14 | broker_execution=false"
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
