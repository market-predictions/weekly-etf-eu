from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from runtime.polish_etf_eu_reports import polish_english

DEFAULT_SOURCE_REPORT = Path("output/weekly_etf_eu_review_260618_draft.md")
DEFAULT_PRICING = Path("output/pricing/etf_eu_ucits_closing_price_smoke_20260618_000000.json")
DEFAULT_PORTING = Path("output/porting/etf_eu_wp14g_donor_comparison_20260618_000000.json")
DEFAULT_BILINGUAL = Path("output/bilingual/etf_eu_bilingual_surface_readiness_20260618_000000.json")
DEFAULT_DRY_RUN = Path("output/delivery/etf_eu_delivery_pdf_dry_run_20260618_000000.json")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")
    return payload


def _header() -> str:
    return """# ETF EU Review — Mature Bilingual Draft

## ETF EU mature draft status

```text
review_only=true
production_delivery=false
recipient_activation=false
send_attempted=false
portfolio_mutation=false
funding_authority=false
valuation_grade=false
```

This mature English draft is derived from EU source artifacts only. It is not a delivery artifact and does not create funding, valuation-grade, portfolio or recipient authority.
"""


def render_mature_english(
    *,
    source_report_path: Path = DEFAULT_SOURCE_REPORT,
    pricing_artifact_path: Path = DEFAULT_PRICING,
    porting_artifact_path: Path = DEFAULT_PORTING,
    bilingual_readiness_path: Path = DEFAULT_BILINGUAL,
    delivery_dry_run_path: Path = DEFAULT_DRY_RUN,
) -> str:
    source = source_report_path.read_text(encoding="utf-8")
    body = polish_english(source, runtime_state={})
    if body.startswith("# ETF EU Review"):
        body = "\n".join(body.splitlines()[1:]).lstrip()
    pricing = _load_json(pricing_artifact_path)
    summary = pricing.get("summary", {}) if isinstance(pricing.get("summary"), dict) else {}
    provenance = f"""
## Source artifact provenance

| Artifact | Path |
| --- | --- |
| Source draft report | `{source_report_path}` |
| UCITS pricing evidence | `{pricing_artifact_path}` |
| Donor-port comparison | `{porting_artifact_path}` |
| Bilingual readiness gate | `{bilingual_readiness_path}` |
| Delivery/PDF dry-run manifest | `{delivery_dry_run_path}` |

Pricing evidence summary: prices_found={summary.get('prices_found')}, pricing_symbols_attempted={summary.get('pricing_symbols_attempted')}, source_errors={summary.get('source_errors')}.
"""
    next_step = """
## Mature bilingual rendering next development step

```text
WP14J — ETF EU HTML/PDF render dry run from mature bilingual reports, no recipients
```

Delivery remains blocked. This package produces mature bilingual report surfaces only.
"""
    return _header().rstrip() + "\n\n" + provenance.strip() + "\n\n" + body.strip() + "\n\n" + next_step.strip() + "\n"


def write_mature_english(output_path: Path, **kwargs: Any) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_mature_english(**kwargs), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--source-report", default=str(DEFAULT_SOURCE_REPORT))
    parser.add_argument("--pricing-artifact", default=str(DEFAULT_PRICING))
    parser.add_argument("--porting-artifact", default=str(DEFAULT_PORTING))
    parser.add_argument("--bilingual-readiness", default=str(DEFAULT_BILINGUAL))
    parser.add_argument("--delivery-dry-run", default=str(DEFAULT_DRY_RUN))
    args = parser.parse_args()
    output = write_mature_english(
        Path(args.output),
        source_report_path=Path(args.source_report),
        pricing_artifact_path=Path(args.pricing_artifact),
        porting_artifact_path=Path(args.porting_artifact),
        bilingual_readiness_path=Path(args.bilingual_readiness),
        delivery_dry_run_path=Path(args.delivery_dry_run),
    )
    print(f"ETF_EU_MATURE_ENGLISH_REPORT_RENDERED | output={output}")


if __name__ == "__main__":
    main()
