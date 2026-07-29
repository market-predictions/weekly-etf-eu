from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def finalize(evidence_path: Path, sources_path: Path) -> None:
    evidence = load_json(evidence_path)
    sources = yaml.safe_load(sources_path.read_text(encoding="utf-8"))
    if not isinstance(sources, dict):
        raise RuntimeError("Source registry must be a YAML object")
    config_by_symbol = {
        str(row.get("symbol")): row
        for row in sources.get("candidates") or []
        if isinstance(row, dict) and row.get("symbol")
    }

    candidates = evidence.get("candidates") if isinstance(evidence.get("candidates"), list) else []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        symbol = str(candidate.get("symbol") or "")
        config = config_by_symbol.get(symbol)
        if not isinstance(config, dict):
            raise RuntimeError(f"Missing source registry row for {symbol}")
        identity = candidate.get("identity") if isinstance(candidate.get("identity"), dict) else {}
        exchange = identity.get("official_exchange") if isinstance(identity.get("official_exchange"), dict) else {}
        issuer = identity.get("issuer_product") if isinstance(identity.get("issuer_product"), dict) else {}
        raw_path = Path(str(exchange.get("raw_path") or ""))
        text = raw_path.read_text(encoding="utf-8", errors="replace") if raw_path.is_file() else ""
        exchange_symbol = str(config.get("exchange_symbol") or symbol)
        checks = {
            "http_200": (exchange.get("source") or {}).get("http_status") == 200,
            "isin_match": str(config.get("isin") or "") in text,
            "wkn_match": str(config.get("wkn") or "") in text,
            "exchange_symbol_match": exchange_symbol in text,
            "xetra_or_mic_match": "Xetra" in text or "XETR" in text,
            "eur_match": "EUR" in text,
        }
        exchange.update({
            "exchange_symbol": exchange_symbol,
            "wkn": config.get("wkn"),
            **checks,
            "pass": all(checks.values()),
            "authority_rule": "official_deutsche_boerse_ssr_exact_isin_wkn_exchange_symbol_xetra_eur",
        })
        issuer_pass = issuer.get("pass") is True
        identity["pass"] = issuer_pass and exchange["pass"]
        identity["authority_rule"] = "official_issuer_exact_product_identity_plus_official_deutsche_boerse_exact_xetra_line"
        blockers = [item for item in (candidate.get("blockers") or []) if item != "exact_line_identity_not_pass"]
        if not identity["pass"]:
            blockers.insert(0, "exact_line_identity_not_pass")
        candidate["blockers"] = blockers
        candidate["activation_evidence_pass"] = not blockers

    summary = evidence.get("summary") if isinstance(evidence.get("summary"), dict) else {}
    summary["identity_pass_count"] = sum(
        1 for row in candidates
        if isinstance(row, dict) and isinstance(row.get("identity"), dict) and row["identity"].get("pass") is True
    )
    summary["activation_evidence_pass_count"] = sum(
        1 for row in candidates if isinstance(row, dict) and row.get("activation_evidence_pass") is True
    )
    evidence["identity_contract_finalization"] = {
        "applied": True,
        "source_registry": str(sources_path),
        "exact_exchange_symbol_distinguished_from_portfolio_label": True,
        "portfolio_mutation": False,
        "ledger_write": False,
        "funding_authority": False,
        "execution_authority": False,
    }
    evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--sources", type=Path, required=True)
    args = parser.parse_args()
    finalize(args.evidence, args.sources)
    print(args.evidence)


if __name__ == "__main__":
    main()
