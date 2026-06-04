from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from runtime.etf_eu_pricing_surface import pricing_surface_section, production_report_maturity_section
from runtime.render_etf_eu_report import (
    DEFAULT_PROXY_MAP,
    DEFAULT_REGISTRY,
    DEFAULT_STATE,
    _read_json,
    _suffix,
    render_en,
    render_nl,
)


def _read_pricing_payload(path: Path | None) -> dict:
    if path is None or not path.exists():
        return {"rows": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _insert_before_delivery_status(report: str, section: str, *, language: str) -> str:
    marker = "## 8. Leveringsstatus" if language == "nl" else "## 8. Delivery status"
    if marker not in report:
        return report.rstrip() + "\n\n" + section + "\n"
    return report.replace(marker, section + "\n\n" + marker, 1)


def _production_maturity_and_surface(payload: dict, *, language: str) -> str:
    return production_report_maturity_section(language=language) + "\n\n" + pricing_surface_section(payload, language=language)


def render_nl_with_pricing_surface(
    state: dict,
    report_date: str,
    proxy_map: Path,
    registry: Path,
    pricing_preflight: Path | None,
    output_dir: Path,
    valuation_artifact: Path | None,
) -> str:
    base = render_nl(state, report_date, proxy_map, registry, pricing_preflight, output_dir)
    payload = _read_pricing_payload(valuation_artifact)
    surface = _production_maturity_and_surface(payload, language="nl")
    return _insert_before_delivery_status(base, surface, language="nl")


def render_en_with_pricing_surface(
    state: dict,
    report_date: str,
    proxy_map: Path,
    registry: Path,
    pricing_preflight: Path | None,
    output_dir: Path,
    valuation_artifact: Path | None,
) -> str:
    base = render_en(state, report_date, proxy_map, registry, pricing_preflight, output_dir)
    payload = _read_pricing_payload(valuation_artifact)
    surface = _production_maturity_and_surface(payload, language="en")
    return _insert_before_delivery_status(base, surface, language="en")


def write_reports_with_pricing_surface(
    output_dir: Path,
    state_path: Path,
    proxy_map: Path,
    registry: Path,
    pricing_preflight: Path | None,
    valuation_artifact: Path | None,
    report_date: str,
) -> tuple[Path, Path]:
    state = _read_json(state_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = _suffix(report_date)
    en_path = output_dir / f"weekly_etf_eu_review_{suffix}.md"
    nl_path = output_dir / f"weekly_etf_eu_review_nl_{suffix}.md"
    en_path.write_text(
        render_en_with_pricing_surface(state, report_date, proxy_map, registry, pricing_preflight, output_dir, valuation_artifact),
        encoding="utf-8",
    )
    nl_path.write_text(
        render_nl_with_pricing_surface(state, report_date, proxy_map, registry, pricing_preflight, output_dir, valuation_artifact),
        encoding="utf-8",
    )
    return en_path, nl_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--state", default=str(DEFAULT_STATE))
    parser.add_argument("--proxy-map", default=str(DEFAULT_PROXY_MAP))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--pricing-preflight", default=None)
    parser.add_argument("--valuation-artifact", default=None)
    parser.add_argument("--report-date", default=date.today().isoformat())
    args = parser.parse_args()
    en_path, nl_path = write_reports_with_pricing_surface(
        Path(args.output_dir),
        Path(args.state),
        Path(args.proxy_map),
        Path(args.registry),
        Path(args.pricing_preflight) if args.pricing_preflight else None,
        Path(args.valuation_artifact) if args.valuation_artifact else None,
        args.report_date,
    )
    print(f"ETF_EU_REPORT_PRICING_SURFACE_RENDER_OK | en={en_path} | nl={nl_path} | dutch_first_maturity=true | delivery=false")


if __name__ == "__main__":
    main()
