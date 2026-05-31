from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "euronext_product_page_evidence_v1"
DEFAULT_OUTPUT_DIR = Path("output/pricing")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _euronext_rows(close_observations: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row for row in close_observations.get("rows", [])
        if isinstance(row, dict) and row.get("source_id") == "euronext_live"
    ]


def _product_page_diagnostics(row: dict[str, Any]) -> dict[str, Any]:
    lineage = row.get("source_lineage") if isinstance(row.get("source_lineage"), dict) else {}
    diagnostics = lineage.get("adapter_diagnostics") if isinstance(lineage.get("adapter_diagnostics"), dict) else {}
    return diagnostics.get("product_page_signal_diagnostics") if isinstance(diagnostics.get("product_page_signal_diagnostics"), dict) else {}


def _drupal_summary(product_page: dict[str, Any]) -> dict[str, Any]:
    return product_page.get("drupal_settings_summary") if isinstance(product_page.get("drupal_settings_summary"), dict) else {}


def _custom_summary(product_page: dict[str, Any]) -> dict[str, Any]:
    return product_page.get("custom_instrument_summary") if isinstance(product_page.get("custom_instrument_summary"), dict) else {}


def _dynamic_context_samples(product_page: dict[str, Any]) -> list[dict[str, str]]:
    samples: list[dict[str, str]] = []
    for item in product_page.get("signal_context_samples") or []:
        if not isinstance(item, dict):
            continue
        if item.get("term") == "dynamic_quotes_display":
            context = re.sub(r"\s+", " ", str(item.get("context") or "")).strip()
            samples.append({"term": "dynamic_quotes_display", "context": context[:500]})
    return samples[:3]


def _dynamic_timer_from_context(samples: list[dict[str, str]]) -> int | None:
    for sample in samples:
        context = sample.get("context") or ""
        match = re.search(r"dynamic_quotes_display.*?timer[^0-9]{1,20}([0-9]{1,5})", context)
        if match:
            return int(match.group(1))
    return None


def _dynamic_quotes_evidence(product_page: dict[str, Any]) -> dict[str, Any]:
    drupal = _drupal_summary(product_page)
    signal_key_paths = [str(path) for path in drupal.get("signal_key_paths") or []]
    signal_terms = [str(term) for term in product_page.get("signal_terms_present") or []]
    signal_counts = product_page.get("signal_term_counts") if isinstance(product_page.get("signal_term_counts"), dict) else {}
    samples = _dynamic_context_samples(product_page)
    key_paths = [path for path in signal_key_paths if "dynamic_quotes_display" in path]
    return {
        "present": bool("dynamic_quotes_display" in signal_terms or key_paths),
        "diagnostic_only": True,
        "key_paths": key_paths,
        "signal_term_count": int(signal_counts.get("dynamic_quotes_display") or 0),
        "context_samples": samples,
        "observed_config": {
            "timer": _dynamic_timer_from_context(samples),
        },
        "candidate_close_extraction": False,
        "completed_session_validation": False,
        "quote_response_fetch": False,
        "next_step": "design a controlled product-page quote response fetcher from dynamic_quotes_display only after the endpoint contract is explicit",
    }


def _custom_instrument_evidence(custom: dict[str, Any]) -> dict[str, Any]:
    instrument_fields = custom.get("instrument_fields") if isinstance(custom.get("instrument_fields"), dict) else {}
    expected_matches = custom.get("expected_matches") if isinstance(custom.get("expected_matches"), dict) else {}
    return {
        "present": custom.get("present") is True,
        "diagnostic_only": True,
        "instrument_fields": instrument_fields,
        "custom_context_fields": custom.get("custom_context_fields") if isinstance(custom.get("custom_context_fields"), dict) else {},
        "expected_registry_identity": custom.get("expected_registry_identity") if isinstance(custom.get("expected_registry_identity"), dict) else {},
        "expected_matches": expected_matches,
        "identity_match_count": custom.get("identity_match_count"),
        "identity_match_total": custom.get("identity_match_total"),
        "identity_usable_for_endpoint_design": custom.get("present") is True and expected_matches.get("isin_matches_registry_line") is True and expected_matches.get("product_data_matches_provider_symbol") is True,
        "date_restriction_is_session_hint_only": custom.get("date_restriction_is_session_hint_only") is True,
        "nb_session_is_request_window_hint_only": custom.get("nb_session_is_request_window_hint_only") is True,
    }


def _row_evidence(row: dict[str, Any]) -> dict[str, Any]:
    product_page = _product_page_diagnostics(row)
    custom = _custom_summary(product_page)
    dynamic = _dynamic_quotes_evidence(product_page)
    return {
        "registry_id": row.get("registry_id"),
        "isin": row.get("isin"),
        "exchange_ticker": row.get("exchange_ticker"),
        "provider_symbol": row.get("provider_symbol"),
        "source_id": row.get("source_id"),
        "source_url": row.get("source_url"),
        "product_page_evidence_status": "product_page_signals_observed" if custom.get("present") or dynamic.get("present") else "product_page_signals_missing",
        "custom_instrument_evidence": _custom_instrument_evidence(custom),
        "dynamic_quotes_display_evidence": dynamic,
        "decision": {
            "search_endpoint_path_disposition": "stopped_after_loopback_evidence",
            "product_page_parser_path": "continue_with_custom_instrument_and_dynamic_quotes_display",
            "promotion_blocked_until": [
                "source_lineage_validated",
                "close_value_validated",
                "close_date_validated",
                "currency_validated",
                "completed_session_validated",
                "staleness_validated",
            ],
        },
        "authority": False,
        "candidate_close_extraction": False,
        "completed_session_validation": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
    }


def build(close_observations_path: Path, output_dir: Path, run_id: str) -> Path:
    close_observations = _load_json(close_observations_path)
    rows = [_row_evidence(row) for row in _euronext_rows(close_observations)]
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_artifact": str(close_observations_path),
        "diagnostic_only": True,
        "authority": False,
        "candidate_close_extraction": False,
        "completed_session_validation": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "rows": rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"euronext_product_page_evidence_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"EURONEXT_PRODUCT_PAGE_EVIDENCE_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--close-observations", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.close_observations), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
