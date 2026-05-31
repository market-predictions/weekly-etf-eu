from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from pricing.close_engine.adapters import DeutscheBoerseAdapter, EuronextAdapter
from pricing.close_engine.adapters.euronext_quote_endpoint_candidates import build_quote_endpoint_candidate_evidence_from_summary
from pricing.close_engine.contracts import SourcePolicy, TradingLine

DEFAULT_SOURCE_POLICY = Path("config/ucits_pricing_source_policy.yml")
DEFAULT_OUTPUT_DIR = Path("output/pricing")
OFFICIAL_SOURCE_IDS = {"euronext_live", "deutsche_boerse_live"}


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def make_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def adapters() -> list[Any]:
    return [EuronextAdapter(), DeutscheBoerseAdapter()]


def iter_source_requests(policy: dict[str, Any]) -> list[tuple[TradingLine, SourcePolicy]]:
    requests: list[tuple[TradingLine, SourcePolicy]] = []
    for line in policy.get("trading_line_policies") or []:
        trading_line = TradingLine(
            registry_id=str(line.get("registry_id") or ""),
            isin=str(line.get("isin") or ""),
            exchange=str(line.get("exchange") or ""),
            exchange_ticker=str(line.get("exchange_ticker") or ""),
            trading_currency=str(line.get("trading_currency") or ""),
            provider_symbol=line.get("provider_symbol"),
        )
        for raw_source in line.get("source_order") or []:
            source_id = raw_source.get("source_id")
            if source_id not in OFFICIAL_SOURCE_IDS:
                continue
            if raw_source.get("valuation_grade_eligible") is not True:
                continue
            if not raw_source.get("product_url") or not raw_source.get("expected_currency"):
                continue
            source = SourcePolicy(
                source_id=str(source_id),
                adapter_name=str(source_id),
                authority=str(raw_source.get("authority") or ""),
                valuation_grade_eligible=raw_source.get("valuation_grade_eligible") is True,
                accept_as_valuation_grade=raw_source.get("accept_as_valuation_grade") is True,
                source_url=raw_source.get("product_url"),
                mic_code=raw_source.get("mic_code"),
                expected_currency=raw_source.get("expected_currency"),
                raw=dict(raw_source),
            )
            requests.append((trading_line, source))
    return requests


def enrich_euronext_quote_candidates(row: dict[str, Any]) -> dict[str, Any]:
    if row.get("source_id") != "euronext_live":
        return row
    source_lineage = row.get("source_lineage") if isinstance(row.get("source_lineage"), dict) else {}
    diagnostics = source_lineage.get("adapter_diagnostics") if isinstance(source_lineage.get("adapter_diagnostics"), dict) else {}
    product_page = diagnostics.get("product_page_signal_diagnostics") if isinstance(diagnostics.get("product_page_signal_diagnostics"), dict) else {}
    if product_page.get("quote_endpoint_candidate_evidence"):
        return row
    custom_summary = product_page.get("custom_instrument_summary") if isinstance(product_page.get("custom_instrument_summary"), dict) else {}
    registry_identity = {
        "isin": str(row.get("isin") or ""),
        "exchange_ticker": str(row.get("exchange_ticker") or ""),
        "provider_symbol": str(row.get("provider_symbol") or ""),
        "trading_currency": str(row.get("trading_currency") or ""),
    }
    product_page["quote_endpoint_candidate_evidence"] = build_quote_endpoint_candidate_evidence_from_summary(
        custom_instrument_summary=custom_summary,
        source_url=row.get("source_url"),
        registry_identity=registry_identity,
    )
    diagnostics["product_page_signal_diagnostics"] = product_page
    source_lineage["adapter_diagnostics"] = diagnostics
    row["source_lineage"] = source_lineage
    if product_page["quote_endpoint_candidate_evidence"].get("candidate_urls"):
        row["parser_status"] = "quote_endpoint_candidate_evidence_collected"
    return row


def observe(policy_path: Path, output_dir: Path, run_id: str) -> Path:
    policy = load_yaml(policy_path)
    adapter_list = adapters()
    rows: list[dict[str, Any]] = []
    for line, source in iter_source_requests(policy):
        matched = False
        for adapter in adapter_list:
            if adapter.supports(source, line):
                rows.append(enrich_euronext_quote_candidates(adapter.observe(source, line).to_dict()))
                matched = True
                break
        if not matched:
            rows.append({
                "registry_id": line.registry_id,
                "isin": line.isin,
                "exchange": line.exchange,
                "exchange_ticker": line.exchange_ticker,
                "trading_currency": line.trading_currency,
                "provider_symbol": line.provider_symbol,
                "source_id": source.source_id,
                "adapter_name": source.adapter_name,
                "source_url": source.source_url,
                "observation_status": "no_adapter_available",
                "candidate_close": None,
                "candidate_date": None,
                "candidate_currency": None,
                "completed_session": False,
                "confidence": "none",
                "parser_status": "no_adapter",
                "blockers": ["no_adapter_available"],
                "source_lineage": {"authority": source.authority},
                "portfolio_mutation": False,
                "production_delivery": False,
                "funding_authority": False,
                "valuation_authority": False,
            })
    artifact = {
        "schema_version": "ucits_close_observations_v1",
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_policy": str(policy_path),
        "portfolio_mutation": False,
        "production_delivery": False,
        "funding_authority": False,
        "valuation_authority": False,
        "rows": rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"ucits_close_observations_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"UCITS_CLOSE_OBSERVATIONS_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-policy", default=str(DEFAULT_SOURCE_POLICY))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    observe(Path(args.source_policy), Path(args.output_dir), args.run_id or make_run_id())


if __name__ == "__main__":
    main()
