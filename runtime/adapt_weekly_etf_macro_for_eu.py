from __future__ import annotations

import argparse
import copy
import hashlib
import json
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_date(value: Any) -> date | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None


def _load_url(url: str) -> tuple[dict[str, Any], str]:
    request = urllib.request.Request(url, headers={"User-Agent": "weekly-etf-eu-macro-adapter/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def adapt(donor: dict[str, Any], *, report_date: str, run_id: str, source_url: str, source_sha256: str) -> dict[str, Any]:
    target_date = _parse_date(report_date)
    donor_date = _parse_date(donor.get("report_date") or donor.get("generated_at_utc"))
    if target_date is None or donor_date is None:
        raise RuntimeError("Could not resolve report date or donor macro date")
    age_days = (target_date - donor_date).days
    if age_days < 0 or age_days > 3:
        raise RuntimeError(f"Donor macro pack is not current enough for EU shadow run: age_days={age_days}")

    payload = copy.deepcopy(donor)
    payload["schema_version"] = "etf_eu_macro_policy_pack_v1"
    payload["artifact_type"] = "etf_eu_macro_policy_pack"
    payload["generated_at_utc"] = _utc_now()
    payload["report_date"] = report_date
    payload["run_id"] = run_id
    payload["source_of_truth_repo"] = "market-predictions/weekly-etf-eu"
    payload["reference_architecture_repo"] = "market-predictions/weekly-etf"
    payload["upstream_pattern_adapted"] = "weekly-etf current macro-policy pack adapted as descriptive EU/UCITS context"
    payload["donor_provenance"] = {
        "source_repo": "market-predictions/weekly-etf",
        "source_url": source_url,
        "source_sha256": source_sha256,
        "source_report_date": donor.get("report_date"),
        "source_generated_at_utc": donor.get("generated_at_utc"),
        "age_days_at_eu_report_date": age_days,
    }
    payload["authority"] = {
        "authority_class": "eu_descriptive_macro_context",
        "client_facing_authority": False,
        "client_surface_allowed": True,
        "decision_authority": "descriptive_only",
        "shadow_only": True,
        "input_state_contract": "Current weekly-etf macro pack is donor context; EU portfolio, UCITS registry and EU pricing remain authoritative.",
        "output_contract": "Only client-safe descriptive regime, central-bank and policy context may enter the EU report.",
        "operational_runbook": "Refresh from the current donor pack, record provenance, adapt implications to EU/UCITS, and never create funding or trade authority.",
    }

    banks = payload.get("central_banks") if isinstance(payload.get("central_banks"), dict) else {}
    fed = banks.get("fed") if isinstance(banks.get("fed"), dict) else {}
    ecb = banks.get("ecb") if isinstance(banks.get("ecb"), dict) else {}
    fed["etf_implication"] = "Maintain quality and cash discipline; any allocation still requires a verified UCITS instrument, current pricing and a separate capital decision."
    ecb["etf_implication"] = "European equity or bond exposure remains conditional on UCITS identity, trading-line verification, current pricing and relative-strength confirmation."
    banks["fed"] = fed
    banks["ecb"] = ecb
    payload["central_banks"] = banks

    payload["portfolio_implications"] = [
        "Retain cash until the selected UCITS trading line, broker availability and current pricing are jointly verified.",
        "Broad U.S. core equity through verified UCITS lines remains the most mature implementation lane; thematic exposure still requires concentration discipline.",
        "Macro context is descriptive and cannot by itself authorize funding, valuation or portfolio mutation.",
    ]
    payload["eu_adaptation"] = {
        "isin_first": True,
        "us_etfs_research_only": True,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "client_surface_scope": "descriptive_regime_central_bank_policy_context_only",
    }
    payload["source_files"] = {
        "donor_macro_policy_pack": source_url,
        "eu_portfolio_state": "output/etf_eu_portfolio_state.json",
        "eu_ucits_registry": "config/ucits_symbol_registry.yml",
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Adapt the current Weekly ETF donor macro pack for EU/UCITS shadow reporting.")
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--latest-output")
    args = parser.parse_args()

    donor, source_sha256 = _load_url(args.source_url)
    payload = adapt(
        donor,
        report_date=args.report_date,
        run_id=args.run_id,
        source_url=args.source_url,
        source_sha256=source_sha256,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    output.write_text(rendered, encoding="utf-8")
    if args.latest_output:
        latest = Path(args.latest_output)
        latest.parent.mkdir(parents=True, exist_ok=True)
        latest.write_text(rendered, encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "source_sha256": source_sha256,
        "source_report_date": donor.get("report_date"),
        "eu_report_date": args.report_date,
        "authority": "descriptive_only",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
